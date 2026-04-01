import typer

from polonium_cli.client import APIError, PoloniumClient

app = typer.Typer(help="File commands")


@app.command("explain")
def explain(repo_id: int, path: str, api_url: str = "http://localhost:8000/api/v1") -> None:
    """Explain a specific file in a repository."""
    client = PoloniumClient(base_url=api_url)
    try:
        data = client.explain_file(repo_id, path)
        typer.echo(f"Purpose: {data.get('purpose', '')}\n")
        typer.echo(data.get("explanation", ""))
    except APIError as exc:
        typer.echo(f"Error: {exc}")
        raise typer.Exit(code=1)

