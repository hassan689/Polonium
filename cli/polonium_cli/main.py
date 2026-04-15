import typer
from polonium_cli.commands_layer.chat import app as chat_app
from polonium_cli.commands_layer.file import app as file_app
from polonium_cli.commands_layer.repo import app as repo_app
from polonium_cli.commands_layer.search import app as search_app
# You can change the cmd but keep it simple and easy to understand
#TODO : add remaining features to the cmd 
#TODO : add feature like show dev tree 
app = typer.Typer(
    help="[bold #07F5E9]Polonium CLI [^_^][/bold #07F5E9]",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
app.add_typer(repo_app, name="repo")
app.add_typer(file_app, name="file")
app.add_typer(chat_app, name="chat")
app.add_typer(search_app, name="search")


@app.command("ui")
def ui() -> None:
    from polonium_cli.ui_layer.app import run_tui
    run_tui()
def run() -> None:
    app()
if __name__ == "__main__":
    run()

