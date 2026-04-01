#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod api_client;
mod commands;
mod file_system;
mod local_ai;

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            commands::open_repository,
            commands::get_file_content,
            commands::analyze_locally
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

