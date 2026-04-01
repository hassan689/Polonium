# Polonium Desktop (Tauri)

This directory contains the Tauri desktop shell for Polonium.

## Prerequisites

- Rust toolchain
- Node.js
- Tauri system dependencies for your OS

## Run (development)

```bash
cd desktop
npm install
npm run tauri:dev
```

The desktop shell points to the frontend dev server at `http://localhost:3000`.

## Architecture (Layered + Client/Server)

- Frontend Layer: Next.js app loaded in Tauri WebView
- Bridge Layer: Tauri Rust backend with IPC commands
- Service Layer: Rust modules for file operations and local AI analysis
- External API Layer: optional remote Polonium backend client

## Rust Module Layout

```text
src-tauri/src/
├── main.rs
├── commands/
├── file_system/
├── local_ai/
└── api_client/
```

