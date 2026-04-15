import typer
from rich.table import Table

import polonium_cli.actions as actions
from polonium_cli.client import APIError, PoloniumClient
from polonium_cli.ui import THEME_COLOR, console, print_error

app = typer.Typer(help="Chat commands", rich_markup_mode="rich")


@app.command("send")
def send(repo_id: int, message: str, api_url: str = "http://localhost:8000/api/v1") -> None:
    """Send a chat message to repository assistant."""
    client = PoloniumClient(base_url=api_url)
    try:
        response = actions.chat_send(client, repo_id, message)
        console.print(response.get("content", ""))
    except APIError as exc:
        print_error(str(exc))
        raise typer.Exit(code=1)


@app.command("history")
def history(repo_id: int, api_url: str = "http://localhost:8000/api/v1") -> None:
    """Show chat history for a repository."""
    client = PoloniumClient(base_url=api_url)
    try:
        messages = actions.chat_history_messages(client, repo_id)
        table = Table(title=f"Chat History (repo {repo_id})")
        table.add_column("Role", style=THEME_COLOR)
        table.add_column("Message", style="white")
        for msg in messages:
            table.add_row(msg.get("role", "unknown"), msg.get("content", ""))
        console.print(table)
    except ValueError as exc:
        print_error(str(exc))
        raise typer.Exit(code=1)
    except APIError as exc:
        print_error(str(exc))
        raise typer.Exit(code=1)
