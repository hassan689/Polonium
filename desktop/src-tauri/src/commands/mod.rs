use serde::Serialize;

use crate::file_system::{read_file_content, validate_repository_path};
use crate::local_ai::{LocalAIEngine, LocalAnalysisResult, MockLocalProvider};

#[derive(Serialize)]
pub struct RepositoryOpenResponse {
    pub path: String,
    pub status: String,
}

#[tauri::command]
pub fn open_repository(path: String) -> Result<RepositoryOpenResponse, String> {
    validate_repository_path(&path)?;
    Ok(RepositoryOpenResponse {
        path,
        status: "opened".to_string(),
    })
}

#[tauri::command]
pub fn get_file_content(path: String) -> Result<String, String> {
    read_file_content(&path)
}

#[tauri::command]
pub fn analyze_locally(content: String) -> Result<LocalAnalysisResult, String> {
    let provider = MockLocalProvider::new();
    provider.analyze(&content)
}

