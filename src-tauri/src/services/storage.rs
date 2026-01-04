use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;
use tauri::{path::BaseDirectory, AppHandle, Manager};

#[derive(Debug, Serialize, Deserialize, Clone)]
#[serde(rename_all = "snake_case")]
pub struct HistoryItem {
    pub timestamp: u64,
    pub vendor: String,
    pub base_url: Option<String>,
    pub api_key: Option<String>,
    pub models: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CustomTemplate {
    pub name: String,
    pub content: String, // e.g., "export API_KEY={{api_key}}\nexport BASE_URL={{base_url}}"
}

pub struct StorageService;

impl StorageService {
    fn get_app_data_path(app: &AppHandle, filename: &str) -> Result<PathBuf, String> {
        let path = app
            .path()
            .resolve(filename, BaseDirectory::AppData)
            .map_err(|e| e.to_string())?;

        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent).map_err(|e| e.to_string())?;
        }

        Ok(path)
    }

    // --- History ---
    pub fn load_history(app: &AppHandle) -> Result<Vec<HistoryItem>, String> {
        let path = Self::get_app_data_path(app, "history.json")?;
        if !path.exists() {
            return Ok(Vec::new());
        }
        let content = fs::read_to_string(path).map_err(|e| e.to_string())?;
        let items: Vec<HistoryItem> = serde_json::from_str(&content).map_err(|e| e.to_string())?;
        Ok(items)
    }

    pub fn save_history(app: &AppHandle, items: Vec<HistoryItem>) -> Result<(), String> {
        let path = Self::get_app_data_path(app, "history.json")?;
        let content = serde_json::to_string_pretty(&items).map_err(|e| e.to_string())?;
        fs::write(path, content).map_err(|e| e.to_string())?;
        Ok(())
    }

    pub fn add_history_item(app: &AppHandle, item: HistoryItem) -> Result<(), String> {
        let mut items = Self::load_history(app)?;
        items.insert(0, item);
        if items.len() > 50 {
            items.truncate(50);
        }
        Self::save_history(app, items)
    }

    // --- Templates ---
    pub fn load_templates(app: &AppHandle) -> Result<Vec<CustomTemplate>, String> {
        let path = Self::get_app_data_path(app, "templates.json")?;
        if !path.exists() {
            return Ok(Vec::new());
        }
        let content = fs::read_to_string(path).map_err(|e| e.to_string())?;
        let items: Vec<CustomTemplate> =
            serde_json::from_str(&content).map_err(|e| e.to_string())?;
        Ok(items)
    }

    pub fn save_templates(app: &AppHandle, templates: Vec<CustomTemplate>) -> Result<(), String> {
        let path = Self::get_app_data_path(app, "templates.json")?;
        let content = serde_json::to_string_pretty(&templates).map_err(|e| e.to_string())?;
        fs::write(path, content).map_err(|e| e.to_string())?;
        Ok(())
    }
}
