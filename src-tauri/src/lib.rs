mod services;
mod utils;

use services::formatter::{FormatType, FormatterService};
use services::ocr::{OCRMode, OCRService};
use services::storage::{HistoryItem, StorageService};
use services::text_parser::{ParseResult, TextParser};
use tauri::AppHandle;

// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[tauri::command]
fn parse_text(text: String) -> ParseResult {
    TextParser::parse(&text)
}

#[tauri::command]
async fn ocr_extract_models(
    image_path: String,
    mode: String,
    ai_key: Option<String>,
    ai_url: Option<String>,
    ai_model: Option<String>,
) -> Result<Vec<String>, String> {
    let ocr_mode = match mode.as_str() {
        "ai" => OCRMode::AI,
        _ => OCRMode::System,
    };
    let service = OCRService::new(ocr_mode);
    let ai_config = if let (Some(k), Some(u), Some(m)) = (ai_key, ai_url, ai_model) {
        Some((k, u, m))
    } else {
        None
    };
    service.extract_models(&image_path, ai_config).await
}

#[tauri::command]
fn load_history(app: AppHandle) -> Result<Vec<HistoryItem>, String> {
    StorageService::load_history(&app)
}

#[tauri::command]
fn add_history_item(app: AppHandle, item: HistoryItem) -> Result<(), String> {
    StorageService::add_history_item(&app, item)
}

#[tauri::command]
fn format_output(
    vendor: String,
    base_url: Option<String>,
    api_key: Option<String>,
    models: Vec<String>,
    format_type: String,
    custom_template: Option<String>,
) -> Result<String, String> {
    let f_type = match format_type.to_lowercase().as_str() {
        "json" => FormatType::Json,
        "yaml" | "yml" => FormatType::Yaml,
        "toml" => FormatType::Toml,
        "custom" => {
            if let Some(t) = custom_template {
                FormatType::Custom(t)
            } else {
                FormatType::Env
            }
        }
        _ => FormatType::Env,
    };
    FormatterService::format(&vendor, base_url, api_key, models, f_type)
}

#[tauri::command]
fn load_templates(app: AppHandle) -> Result<Vec<services::storage::CustomTemplate>, String> {
    StorageService::load_templates(&app)
}

#[tauri::command]
fn save_templates(
    app: AppHandle,
    templates: Vec<services::storage::CustomTemplate>,
) -> Result<(), String> {
    StorageService::save_templates(&app, templates)
}

#[tauri::command]
fn save_history(app: AppHandle, items: Vec<services::storage::HistoryItem>) -> Result<(), String> {
    StorageService::save_history(&app, items)
}

#[tauri::command]
fn clear_history(app: AppHandle) -> Result<(), String> {
    StorageService::save_history(&app, Vec::new())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_fs::init())
        .invoke_handler(tauri::generate_handler![
            greet,
            parse_text,
            ocr_extract_models,
            load_history,
            add_history_item,
            save_history,
            clear_history,
            format_output,
            load_templates,
            save_templates
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
