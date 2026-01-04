use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct VendorConfig {
    pub name: String,
    pub keywords: Vec<String>,
    pub capabilities: Vec<String>,
    pub env_prefix: String,
}

pub fn get_vendors() -> Vec<VendorConfig> {
    vec![
        VendorConfig {
            name: "openai".to_string(),
            keywords: vec!["openai.com".to_string(), "openai".to_string()],
            capabilities: vec![
                "vision".to_string(),
                "function_calling".to_string(),
                "stream".to_string(),
            ],
            env_prefix: "OPENAI".to_string(),
        },
        VendorConfig {
            name: "anthropic".to_string(),
            keywords: vec!["anthropic.com".to_string(), "claude".to_string()],
            capabilities: vec![
                "vision".to_string(),
                "thinking".to_string(),
                "stream".to_string(),
            ],
            env_prefix: "ANTHROPIC".to_string(),
        },
        VendorConfig {
            name: "google".to_string(),
            keywords: vec![
                "generativeai".to_string(),
                "gemini".to_string(),
                "googleapis".to_string(),
                "google".to_string(),
            ],
            capabilities: vec!["vision".to_string(), "multimodal".to_string()],
            env_prefix: "GOOGLE".to_string(),
        },
        VendorConfig {
            name: "deepseek".to_string(),
            keywords: vec!["deepseek".to_string()],
            capabilities: vec!["vision".to_string(), "reasoning".to_string()],
            env_prefix: "DEEPSEEK".to_string(),
        },
        VendorConfig {
            name: "zhipu".to_string(),
            keywords: vec!["zhipuai".to_string(), "chatglm".to_string()],
            capabilities: vec!["vision".to_string()],
            env_prefix: "ZHIPU".to_string(),
        },
        VendorConfig {
            name: "moonshot".to_string(),
            keywords: vec!["moonshot".to_string(), "kimi".to_string()],
            capabilities: vec!["long_context".to_string()],
            env_prefix: "MOONSHOT".to_string(),
        },
    ]
}

pub fn detect_vendor(url: &str) -> String {
    let url_lower = url.to_lowercase();
    for vendor in get_vendors() {
        for keyword in vendor.keywords {
            if url_lower.contains(&keyword) {
                return vendor.name;
            }
        }
    }
    "custom".to_string()
}
