import typer

import polonium_cli.actions as actions
from polonium_cli.client import APIError, PoloniumClient
from polonium_cli.ui import print_error, print_info_panel

app = typer.Typer(help="File commands", rich_markup_mode="rich")


@app.command("explain")
def explain(repo_id: int, path: str, api_url: str = "http://localhost:8000/api/v1") -> None:
    """Explain a specific file in a repository."""
    client = PoloniumClient(base_url=api_url)
    try:
        data = actions.file_explain(client, repo_id, path)
        print_info_panel("Purpose", data.get("purpose", ""))
        print_info_panel("Explanation", data.get("explanation", ""))
    except APIError as exc:
        print_error(str(exc))
        raise typer.Exit(code=1)
