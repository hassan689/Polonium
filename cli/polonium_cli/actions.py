"""Shared API/business logic used by Typer commands and the TUI."""
from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

from polonium_cli.client import PoloniumClient


def parse_github_repo_url(url: str) -> tuple[str, str]:
    """Return (owner, repo_name) from a GitHub https URL."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    parts = path.split("/")
    if len(parts) < 2:
        raise ValueError("Expected GitHub URL like https://github.com/<owner>/<repo>")
    return parts[0], parts[1].replace(".git", "")


def repo_connect(client: PoloniumClient, url: str) -> dict[str, Any]:
    owner, name = parse_github_repo_url(url)
    return client.connect_repo(owner, name)


def repo_list_rows(client: PoloniumClient) -> list[dict[str, Any]]:
    response = client.list_repos()
    repos = response["data"] if "data" in response and isinstance(response["data"], list) else response
    if not isinstance(repos, list):
        raise ValueError("Unexpected response format from backend.")
    return repos


def repo_overview(client: PoloniumClient, repo_id: int) -> dict[str, Any]:
    return client.repo_overview(repo_id)


def file_explain(client: PoloniumClient, repo_id: int, path: str) -> dict[str, Any]:
    return client.explain_file(repo_id, path)


def chat_send(client: PoloniumClient, repo_id: int, message: str) -> dict[str, Any]:
    return client.send_chat(repo_id, message)


def chat_history_messages(client: PoloniumClient, repo_id: int) -> list[dict[str, Any]]:
    response = client.chat_history(repo_id)
    messages = response["data"] if "data" in response and isinstance(response["data"], list) else response
    if not isinstance(messages, list):
        raise ValueError("Unexpected response format from backend.")
    return messages


def search_code_placeholder(query: str) -> str:
    return f"Search is not implemented yet.\nQuery: {query}"
