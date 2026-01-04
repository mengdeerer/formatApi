use crate::services::text_parser::TextParser;
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub enum OCRMode {
    System,
    AI,
}

pub struct OCRService {
    mode: OCRMode,
}

impl OCRService {
    pub fn new(mode: OCRMode) -> Self {
        Self { mode }
    }

    pub async fn extract_models(
        &self,
        image_path: &str,
        ai_config: Option<(String, String, String)>,
    ) -> Result<Vec<String>, String> {
        match self.mode {
            OCRMode::System => self.extract_with_system(image_path),
            OCRMode::AI => {
                if let Some((api_key, base_url, model)) = ai_config {
                    self.extract_with_ai(image_path, &api_key, &base_url, &model)
                        .await
                } else {
                    Err("AI OCR configuration missing".to_string())
                }
            }
        }
    }

    fn extract_with_system(&self, image_path: &str) -> Result<Vec<String>, String> {
        #[cfg(target_os = "macos")]
        {
            use objc2::rc::Retained;
            use objc2::AnyThread;
            use objc2_foundation::{NSArray, NSDictionary, NSURL};
            use objc2_vision::{
                VNImageBasedRequest, VNImageRequestHandler, VNRecognizeTextRequest,
                VNRecognizedTextObservation, VNRequest, VNRequestTextRecognitionLevel,
            };

            let path_str = image_path.to_string();
            let url = NSURL::fileURLWithPath(&objc2_foundation::NSString::from_str(&path_str));

            unsafe {
                let options = NSDictionary::new();
                let handler = VNImageRequestHandler::initWithURL_options(
                    <VNImageRequestHandler as AnyThread>::alloc(),
                    &url,
                    &options,
                );

                let request =
                    VNRecognizeTextRequest::init(<VNRecognizeTextRequest as AnyThread>::alloc());
                request.setRecognitionLevel(VNRequestTextRecognitionLevel::Accurate);

                // Hierarchy: VNRecognizeTextRequest -> VNImageBasedRequest -> VNRequest
                let request_base: Retained<VNImageBasedRequest> =
                    Retained::into_super(request.clone());
                let request_vn: Retained<VNRequest> = Retained::into_super(request_base);

                let requests = NSArray::from_retained_slice(&[request_vn]);
                let success: bool = handler.performRequests_error(&requests).is_ok();

                if !success {
                    return Err("Vision request failed".to_string());
                }

                let results: Retained<NSArray<VNRecognizedTextObservation>> =
                    request.results().unwrap_or_else(|| NSArray::new());
                let mut texts = Vec::new();

                for i in 0..results.count() {
                    let observation = results.objectAtIndex(i);
                    let candidates = observation.topCandidates(1);
                    if candidates.count() > 0 {
                        let text = candidates.objectAtIndex(0).string();
                        texts.push(text.to_string());
                    }
                }

                let combined_text = texts.join("\n");
                Ok(TextParser::parse_model_names(&combined_text))
            }
        }
        #[cfg(not(target_os = "macos"))]
        {
            let _ = image_path;
            Err("System OCR is only supported on macOS".to_string())
        }
    }

    async fn extract_with_ai(
        &self,
        image_path: &str,
        api_key: &str,
        base_url: &str,
        model: &str,
    ) -> Result<Vec<String>, String> {
        let image_data = std::fs::read(image_path).map_err(|e| e.to_string())?;
        use base64::engine::general_purpose::STANDARD;
        use base64::Engine;
        let base64_image = STANDARD.encode(image_data);

        let url = format!("{}/chat/completions", base_url.trim_end_matches('/'));
        let client = reqwest::Client::new();

        let prompt = "请从这张图片中提取所有AI模型名称。要求：1. 只返回模型名称，每行一个；2. 不要添加序号、说明文字或其他内容。";

        let payload = serde_json::json!({
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": format!("data:image/jpeg;base64,{}", base64_image)}
                        }
                    ]
                }
            ],
            "max_tokens": 2000
        });

        let response = client
            .post(url)
            .header("Authorization", format!("Bearer {}", api_key))
            .json(&payload)
            .send()
            .await
            .map_err(|e| e.to_string())?;

        let result: serde_json::Value = response.json().await.map_err(|e| e.to_string())?;
        let content = result["choices"][0]["message"]["content"]
            .as_str()
            .ok_or("Failed to parse AI response")?;

        Ok(TextParser::parse_model_names(content))
    }
}
