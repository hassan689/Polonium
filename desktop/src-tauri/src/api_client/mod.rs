#[derive(Clone)]
pub struct RemoteApiClient {
    pub base_url: String,
    pub auth_token: Option<String>,
}

impl RemoteApiClient {
    pub fn new(base_url: String, auth_token: Option<String>) -> Self {
        Self { base_url, auth_token }
    }

    pub fn is_configured(&self) -> bool {
        !self.base_url.trim().is_empty()
    }
}

