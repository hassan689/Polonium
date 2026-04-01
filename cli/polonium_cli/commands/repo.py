from urllib.parse import urlparse

import typer

from polonium_cli.client import APIError, PoloniumClient

app = typer.Typer(help="Repository commands")


def _parse_repo_url(url: str) -> tuple[str, str]:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    parts = path.split("/")
    if len(parts) < 2:
        raise typer.BadParameter("Expected GitHub URL like https://github.com/<owner>/<repo>")
    return parts[0], parts[1].replace(".git", "")


@app.command("connect")
def connect(url: str, api_url: str = "http://localhost:8000/api/v1") -> None:
    """Connect a repository via URL."""
    owner, name = _parse_repo_url(url)
    client = PoloniumClient(base_url=api_url)
    try:
        repo = client.connect_repo(owner, name)
        typer.echo(f"Connected: {repo.get('github_full_name')} (id={repo.get('id')})")
    except APIError as exc:
        typer.echo(f"Error: {exc}")
        raise typer.Exit(code=1)


@app.command("list")
def list_repositories(api_url: str = "http://localhost:8000/api/v1") -> None:
    """List connected repositories."""
    client = PoloniumClient(base_url=api_url)
    try:
        response = client.list_repos()
        repos = response["data"] if "data" in response and isinstance(response["data"], list) else response
        if not isinstance(repos, list):
            typer.echo("Unexpected response format from backend.")
            raise typer.Exit(code=1)
        for repo in repos:
            typer.echo(f"{repo['id']}: {repo['github_full_name']} [{repo['status']}]")
    except APIError as exc:
        typer.echo(f"Error: {exc}")
        raise typer.Exit(code=1)


@app.command("overview")
def overview(repo_id: int, api_url: str = "http://localhost:8000/api/v1") -> None:
    """Show AI-generated repository overview."""
    client = PoloniumClient(base_url=api_url)
    try:
        data = client.repo_overview(repo_id)
        typer.echo(f"Overview:\n{data.get('overview', '')}\n")
        typer.echo(f"Architecture:\n{data.get('architecture', '')}\n")
        typer.echo("Tech Stack:")
        for tech in data.get("tech_stack", []) or []:
            typer.echo(f"- {tech}")
        typer.echo("Key Files:")
        for path in data.get("key_files", []) or []:
            typer.echo(f"- {path}")
    except APIError as exc:
        typer.echo(f"Error: {exc}")
        raise typer.Exit(code=1)

