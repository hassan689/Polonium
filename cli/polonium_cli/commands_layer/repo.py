import typer
from rich.table import Table

import polonium_cli.actions as actions
from polonium_cli.client import APIError, PoloniumClient
from polonium_cli.ui import THEME_COLOR, console, print_error, print_info_panel, print_success

app = typer.Typer(help="Repository commands", rich_markup_mode="rich")


@app.command("connect")
def connect(url: str, api_url: str = "http://localhost:8000/api/v1") -> None:
    """Connect a repository via URL."""
    client = PoloniumClient(base_url=api_url)
    try:
        repo = actions.repo_connect(client, url)
        print_success(f"Connected: {repo.get('github_full_name')} (id={repo.get('id')})")
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    except APIError as exc:
        print_error(str(exc))
        raise typer.Exit(code=1)


@app.command("list")
def list_repositories(api_url: str = "http://localhost:8000/api/v1") -> None:
    """List connected repositories."""
    client = PoloniumClient(base_url=api_url)
    try:
        repos = actions.repo_list_rows(client)
        table = Table(title="Connected Repositories")
        table.add_column("ID", style=THEME_COLOR, justify="right")
        table.add_column("Repository", style="white")
        table.add_column("Status", style=THEME_COLOR)
        for repo in repos:
            table.add_row(str(repo["id"]), repo["github_full_name"], repo["status"])
        console.print(table)
    except ValueError as exc:
        print_error(str(exc))
        raise typer.Exit(code=1)
    except APIError as exc:
        print_error(str(exc))
        raise typer.Exit(code=1)


@app.command("overview")
def overview(repo_id: int, api_url: str = "http://localhost:8000/api/v1") -> None:
    """Show AI-generated repository overview."""
    client = PoloniumClient(base_url=api_url)
    try:
        data = actions.repo_overview(client, repo_id)
        print_info_panel("Overview", data.get("overview", ""))
        print_info_panel("Architecture", data.get("architecture", ""))
        tech_stack = "\n".join(f"- {tech}" for tech in (data.get("tech_stack", []) or [])) or "-"
        key_files = "\n".join(f"- {path}" for path in (data.get("key_files", []) or [])) or "-"
        print_info_panel("Tech Stack", tech_stack)
        print_info_panel("Key Files", key_files)
    except APIError as exc:
        print_error(str(exc))
        raise typer.Exit(code=1)
