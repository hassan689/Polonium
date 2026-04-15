"""Parse one user line and route to shell or API handlers."""
from __future__ import annotations

import shlex
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from polonium_cli.client import APIError, PoloniumClient
from polonium_cli.ui_layer.constants import help_markup
from polonium_cli.ui_layer import handlers, shell

Emit = Callable[[Any], None]


@dataclass
class DispatchContext:
    cwd: Path
    theme: str
    api_url: str

    def make_client(self) -> PoloniumClient:
        return PoloniumClient(base_url=self.api_url)


def dispatch_line(raw: str, ctx: DispatchContext, emit: Emit) -> Path:
    """Run one command. Returns updated working directory."""
    try:
        parts = shlex.split(raw)
    except ValueError as exc:
        emit(f"[bold {ctx.theme}]Parse error:[/bold {ctx.theme}] {exc}")
        return ctx.cwd

    if not parts:
        return ctx.cwd
    if parts[0] == "help":
        emit(help_markup())
        return ctx.cwd
    if parts[0] == "pwd":
        emit(f"[{ctx.theme}]{ctx.cwd}[/{ctx.theme}]")
        return ctx.cwd
    if parts[0] == "cd":
        return shell.cd(ctx.cwd, parts, theme=ctx.theme, emit=lambda s: emit(s))
    if parts[0] in {"ls", "dir"}:
        shell.ls_dir(ctx.cwd, theme=ctx.theme, emit=lambda s: emit(s))
        return ctx.cwd
    if parts[0] == "tree":
        shell.run_win(ctx.cwd, ["tree"], theme=ctx.theme, emit=lambda s: emit(s))
        return ctx.cwd
    if parts[0] == "win":
        shell.run_win(ctx.cwd, parts[1:], theme=ctx.theme, emit=lambda s: emit(s))
        return ctx.cwd

    client = ctx.make_client()
    t = ctx.theme
    e: Emit = emit
    try:
        if parts[:2] == ["repo", "list"]:
            handlers.repo_list(client, theme=t, emit=e)
        elif parts[:2] == ["repo", "connect"] and len(parts) >= 3:
            handlers.repo_connect(client, " ".join(parts[2:]), theme=t, emit=e)
        elif parts[:2] == ["repo", "overview"] and len(parts) >= 3:
            handlers.repo_overview(client, int(parts[2]), theme=t, emit=e)
        elif parts[:2] == ["file", "explain"] and len(parts) >= 4:
            handlers.file_explain(client, int(parts[2]), parts[3], theme=t, emit=e)
        elif parts[:2] == ["chat", "send"] and len(parts) >= 4:
            handlers.chat_send(client, int(parts[2]), " ".join(parts[3:]), theme=t, emit=e)
        elif parts[:2] == ["chat", "history"] and len(parts) >= 3:
            handlers.chat_history(client, int(parts[2]), theme=t, emit=e)
        elif parts[:2] == ["search", "code"] and len(parts) >= 3:
            handlers.search_code(" ".join(parts[2:]), theme=t, emit=e)
        else:
            emit(f"[bold {t}]Unknown command.[/bold {t}] Type [bold]help[/bold].")
    except ValueError as exc:
        emit(f"[bold {t}]{exc}[/bold {t}]")
    except APIError as exc:
        emit(f"[bold {t}]API error:[/bold {t}] {exc}")
    except Exception as exc:  # noqa: BLE001
        emit(f"[bold {t}]Unexpected error:[/bold {t}] {exc}")

    return ctx.cwd
