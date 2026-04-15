use std::fs;
use std::path::Path;

pub fn validate_repository_path(path: &str) -> Result<(), String> {
    let repo_path = Path::new(path);
    if !repo_path.exists() {
        return Err("Repository path does not exist".to_string());
    }
    if !repo_path.is_dir() {
        return Err("Repository path must be a directory".to_string());
    }
    let git_dir = repo_path.join(".git");
    if !git_dir.exists() {
        return Err("Path is not a git repository (missing .git directory)".to_string());
    }
    Ok(())
}

pub fn read_file_content(path: &str) -> Result<String, String> {
    let file_path = Path::new(path);
    if !file_path.exists() {
        return Err("File does not exist".to_string());
    }
    if !file_path.is_file() {
        return Err("Path must point to a file".to_string());
    }
    fs::read_to_string(file_path).map_err(|err| format!("Failed to read file: {err}"))
}

