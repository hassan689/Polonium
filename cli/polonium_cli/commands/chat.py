import typer

from polonium_cli.client import APIError, PoloniumClient

app = typer.Typer(help="Chat commands")


@app.command("send")
def send(repo_id: int, message: str, api_url: str = "http://localhost:8000/api/v1") -> None:
    """Send a chat message to repository assistant."""
    client = PoloniumClient(base_url=api_url)
    try:
        response = client.send_chat(repo_id, message)
        typer.echo(response.get("content", ""))
    except APIError as exc:
        typer.echo(f"Error: {exc}")
        raise typer.Exit(code=1)


@app.command("history")
def history(repo_id: int, api_url: str = "http://localhost:8000/api/v1") -> None:
    """Show chat history for a repository."""
    client = PoloniumClient(base_url=api_url)
    try:
        response = client.chat_history(repo_id)
        messages = response["data"] if "data" in response and isinstance(response["data"], list) else response
        if not isinstance(messages, list):
            typer.echo("Unexpected response format from backend.")
            raise typer.Exit(code=1)
        for msg in messages:
            typer.echo(f"[{msg.get('role', 'unknown')}] {msg.get('content', '')}")
    except APIError as exc:
        typer.echo(f"Error: {exc}")
        raise typer.Exit(code=1)

