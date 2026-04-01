import typer

from polonium_cli.commands.chat import app as chat_app
from polonium_cli.commands.file import app as file_app
from polonium_cli.commands.repo import app as repo_app
from polonium_cli.commands.search import app as search_app

app = typer.Typer(help="Polonium command line interface")
app.add_typer(repo_app, name="repo")
app.add_typer(file_app, name="file")
app.add_typer(chat_app, name="chat")
app.add_typer(search_app, name="search")


def run() -> None:
    app()


if __name__ == "__main__":
    run()

