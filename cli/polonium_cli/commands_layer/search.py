import typer

import polonium_cli.actions as actions
from polonium_cli.ui import print_info_panel

app = typer.Typer(help="Search commands", rich_markup_mode="rich")


@app.command("code")
def search_code(query: str) -> None:
    """Placeholder for future semantic/code search command."""
    print_info_panel("Search", actions.search_code_placeholder(query))
