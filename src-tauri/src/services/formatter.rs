use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Serialize, Deserialize)]
pub enum FormatType {
    Env,
    Json,
    Yaml,
    Toml,
    Custom(String), // The template string
}

pub struct FormatterService;

impl FormatterService {
    pub fn format(
        vendor: &str,
        base_url: Option<String>,
        api_key: Option<String>,
        models: Vec<String>,
        format_type: FormatType,
    ) -> Result<String, String> {
        let mut data = HashMap::new();
        data.insert("vendor", vendor.to_string());
        if let Some(url) = base_url.clone() {
            data.insert("base_url", url);
        }
        if let Some(key) = api_key.clone() {
            data.insert("api_key", key);
        }

        match format_type {
            FormatType::Env => Self::to_env(vendor, data, models),
            FormatType::Json => Self::to_json(data, models),
            FormatType::Yaml => Self::to_yaml(data, models),
            FormatType::Toml => Self::to_toml(data, models),
            FormatType::Custom(template) => Self::to_custom(template, base_url, api_key, models),
        }
    }

    fn to_custom(
        template: String,
        base_url: Option<String>,
        api_key: Option<String>,
        models: Vec<String>,
    ) -> Result<String, String> {
        let mut result = template;
        result = result.replace("{{base_url}}", &base_url.unwrap_or_default());
        result = result.replace("{{api_key}}", &api_key.unwrap_or_default());
        result = result.replace("{{models}}", &format!("{:?}", models));
        result = result.replace("{{models_comma}}", &models.join(", "));
        Ok(result)
    }

    fn to_env(
        vendor: &str,
        data: HashMap<&str, String>,
        models: Vec<String>,
    ) -> Result<String, String> {
        let prefix = match vendor {
            "openai" => "OPENAI",
            "anthropic" => "ANTHROPIC",
            "google" => "GOOGLE",
            "deepseek" => "DEEPSEEK",
            "zhipu" => "ZHIPU",
            "moonshot" => "MOONSHOT",
            _ => "CUSTOM",
        };

        let mut lines = Vec::new();
        if let Some(key) = data.get("api_key") {
            lines.push(format!("{}_API_KEY={}", prefix, key));
        }
        if let Some(url) = data.get("base_url") {
            lines.push(format!("{}_BASE_URL={}", prefix, url));
        }
        if !models.is_empty() {
            lines.push(format!("MODELS={:?}", models));
        }

        Ok(lines.join("\n"))
    }

    fn to_json(data: HashMap<&str, String>, models: Vec<String>) -> Result<String, String> {
        let mut full_data = serde_json::to_value(data).map_err(|e| e.to_string())?;
        if let Some(obj) = full_data.as_object_mut() {
            obj.insert("models".to_string(), serde_json::to_value(models).unwrap());
        }
        serde_json::to_string_pretty(&full_data).map_err(|e| e.to_string())
    }

    fn to_yaml(data: HashMap<&str, String>, models: Vec<String>) -> Result<String, String> {
        let mut full_data: serde_json::Value = serde_json::to_value(data).unwrap();
        if let Some(obj) = full_data.as_object_mut() {
            obj.insert("models".to_string(), serde_json::to_value(models).unwrap());
        }
        serde_yaml::to_string(&full_data).map_err(|e| e.to_string())
    }

    fn to_toml(data: HashMap<&str, String>, models: Vec<String>) -> Result<String, String> {
        let mut full_data: serde_json::Value = serde_json::to_value(data).unwrap();
        if let Some(obj) = full_data.as_object_mut() {
            obj.insert("models".to_string(), serde_json::to_value(models).unwrap());
        }
        toml::to_string(&full_data).map_err(|e| e.to_string())
    }
}
