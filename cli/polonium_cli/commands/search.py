import typer

app = typer.Typer(help="Search commands")


@app.command("code")
def search_code(query: str) -> None:
    """Placeholder for future semantic/code search command."""
    typer.echo(f"Search is not implemented yet. Query received: {query}")

