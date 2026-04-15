use serde::Serialize;
#[derive(Serialize)]
pub struct LocalAnalysisResult {
    pub summary: String,
    pub model_provider: String,
    pub offline_mode: bool,
}
pub trait LocalAIEngine {
    fn analyze(&self, content: &str) -> Result<LocalAnalysisResult, String>;
}
pub struct MockLocalProvider;
impl MockLocalProvider {
    pub fn new() -> Self {
        Self
    }
}
impl LocalAIEngine for MockLocalProvider {
    fn analyze(&self, content: &str) -> Result<LocalAnalysisResult, String> {
        if content.trim().is_empty() {
            return Err("Content cannot be empty for local analysis".to_string());
        }
        let preview: String = content.chars().take(160).collect();
        Ok(LocalAnalysisResult {
            summary: format!("Local analysis preview: {preview}"),
            model_provider: "mock_local_provider".to_string(),
            offline_mode: true,
        })
    }
}

