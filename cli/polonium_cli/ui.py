from __future__ import annotations

from rich.console import Console
from rich.panel import Panel

console = Console()
THEME_COLOR = "#07F5E9"


def print_error(message: str) -> None:
    console.print(f"[bold {THEME_COLOR}]Error:[/bold {THEME_COLOR}] {message}")


def print_success(message: str) -> None:
    console.print(f"[bold {THEME_COLOR}]{message}[/bold {THEME_COLOR}]")


def print_info_panel(title: str, body: str) -> None:
    console.print(Panel(body, title=title, border_style=THEME_COLOR))
