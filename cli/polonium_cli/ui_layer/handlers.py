"""Polonium API commands: call shared actions and emit Rich output."""
from __future__ import annotations

from typing import Any, Callable

from rich.panel import Panel
from rich.table import Table

import polonium_cli.actions as actions
from polonium_cli.client import PoloniumClient

Emit = Callable[[Any], None]


def repo_connect(client: PoloniumClient, url: str, *, theme: str, emit: Emit) -> None:
    try:
        repo = actions.repo_connect(client, url)
    except ValueError as exc:
        emit(f"[bold {theme}]{exc}[/bold {theme}]")
        return
    emit(f"[bold {theme}]Connected:[/bold {theme}] {repo.get('github_full_name')} (id={repo.get('id')})")


def repo_list(client: PoloniumClient, *, theme: str, emit: Emit) -> None:
    try:
        repos = actions.repo_list_rows(client)
    except ValueError as exc:
        emit(f"[bold {theme}]{exc}[/bold {theme}]")
        return
    table = Table(title="Connected Repositories")
    table.add_column("ID", justify="right", style=theme)
    table.add_column("Repository")
    table.add_column("Status", style=theme)
    for repo in repos:
        table.add_row(str(repo.get("id", "")), str(repo.get("github_full_name", "")), str(repo.get("status", "")))
    emit(table)


def repo_overview(client: PoloniumClient, repo_id: int, *, theme: str, emit: Emit) -> None:
    data = actions.repo_overview(client, repo_id)
    emit(Panel(data.get("overview", ""), title="Overview", border_style=theme))
    emit(Panel(data.get("architecture", ""), title="Architecture", border_style=theme))
    tech_stack = "\n".join(f"- {tech}" for tech in (data.get("tech_stack", []) or [])) or "-"
    key_files = "\n".join(f"- {path}" for path in (data.get("key_files", []) or [])) or "-"
    emit(Panel(tech_stack, title="Tech Stack", border_style=theme))
    emit(Panel(key_files, title="Key Files", border_style=theme))


def file_explain(client: PoloniumClient, repo_id: int, path: str, *, theme: str, emit: Emit) -> None:
    data = actions.file_explain(client, repo_id, path)
    emit(Panel(data.get("purpose", ""), title="Purpose", border_style=theme))
    emit(Panel(data.get("explanation", ""), title="Explanation", border_style=theme))


def chat_send(client: PoloniumClient, repo_id: int, message: str, *, theme: str, emit: Emit) -> None:
    response = actions.chat_send(client, repo_id, message)
    emit(Panel(response.get("content", ""), title="Assistant", border_style=theme))


def chat_history(client: PoloniumClient, repo_id: int, *, theme: str, emit: Emit) -> None:
    try:
        messages = actions.chat_history_messages(client, repo_id)
    except ValueError as exc:
        emit(f"[bold {theme}]{exc}[/bold {theme}]")
        return
    table = Table(title=f"Chat History (repo {repo_id})")
    table.add_column("Role", style=theme)
    table.add_column("Message")
    for msg in messages:
        table.add_row(str(msg.get("role", "unknown")), str(msg.get("content", "")))
    emit(table)


def search_code(query: str, *, theme: str, emit: Emit) -> None:
    body = actions.search_code_placeholder(query)
    emit(Panel(body, title="Search", border_style=theme))
