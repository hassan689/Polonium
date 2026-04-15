"""Textual application: layout, bindings, and wiring to dispatch."""
from __future__ import annotations

from pathlib import Path

from rich.panel import Panel
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.widgets import Footer, Header, Input, RichLog

from polonium_cli.ui_layer.constants import (
    ASCII_LOGO,
    DEFAULT_API_URL,
    THEME_COLOR,
    TIPS_MARKUP,
    TUI_CSS,
)
from polonium_cli.ui_layer.dispatch import DispatchContext, dispatch_line


class PoloniumTUI(App[None]):
    TITLE = "Polonium CLI"
    SUB_TITLE = "Terminal mode"
    CSS = TUI_CSS

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "quit", "Close"),
        Binding("ctrl+l", "clear_output", "Clear", priority=True),
        Binding("ctrl+p", "command_palette", "Palette", priority=True),
        ("?", "show_help", "Help"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="terminal"):
            yield RichLog(id="output", markup=True, wrap=True)
            yield Input(placeholder="polonium > Type command and press Enter...", id="command_input")
        yield Footer()

    def on_mount(self) -> None:
        self._cwd = Path.cwd()
        self.query_one("#command_input", Input).focus()
        out = self.query_one("#output", RichLog)
        out.write(Panel(f"[{THEME_COLOR}]{ASCII_LOGO.strip(chr(10))}[/{THEME_COLOR}]", border_style=THEME_COLOR))
        out.write(Panel(TIPS_MARKUP, title="Tips", border_style=THEME_COLOR))
        self._emit(f"[bold {THEME_COLOR}]Polonium terminal ready.[/bold {THEME_COLOR}] Use [bold]help[/bold].")

    def action_clear_output(self) -> None:
        self.query_one("#output", RichLog).clear()
        self._emit("[dim]Cleared.[/dim]")

    def action_show_help(self) -> None:
        from polonium_cli.ui_layer.constants import help_markup

        self._emit(help_markup())

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "command_input":
            return
        raw = event.input.value.strip()
        if not raw:
            return
        self._emit(f"[bold {THEME_COLOR}]>[/bold {THEME_COLOR}] {raw}")
        event.input.value = ""
        ctx = DispatchContext(cwd=self._cwd, theme=THEME_COLOR, api_url=DEFAULT_API_URL)
        self._cwd = dispatch_line(raw, ctx, self._emit)

    def _emit(self, item: object) -> None:
        self.query_one("#output", RichLog).write(item)


def run_tui() -> None:
    PoloniumTUI().run()
