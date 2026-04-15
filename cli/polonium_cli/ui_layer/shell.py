"""Local shell-style commands (cd, ls, win) for the TUI."""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Callable

Emit = Callable[[str], None]


def cd(cwd: Path, parts: list[str], *, theme: str, emit: Emit) -> Path:
    """Change directory; exit `emit` messages. Returns new cwd."""
    if len(parts) == 1:
        emit(f"[{theme}]{cwd}[/{theme}]")
        return cwd
    target = " ".join(parts[1:]).strip()
    if target in {"~"}:
        next_dir = Path.home()
    else:
        raw_path = Path(target)
        next_dir = (cwd / raw_path).resolve() if not raw_path.is_absolute() else raw_path.resolve()
    if not next_dir.exists() or not next_dir.is_dir():
        emit(f"[bold {theme}]Directory not found:[/bold {theme}] {target}")
        return cwd
    emit(f"[bold {theme}]cwd:[/bold {theme}] {next_dir}")
    return next_dir


def ls_dir(cwd: Path, *, theme: str, emit: Emit) -> None:
    try:
        entries = sorted(cwd.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except OSError as exc:
        emit(f"[bold {theme}]Cannot list directory:[/bold {theme}] {exc}")
        return
    if not entries:
        emit(f"[{theme}]<empty>[/{theme}]")
        return
    for entry in entries:
        prefix = "[D]" if entry.is_dir() else "[F]"
        emit(f"[{theme}]{prefix}[/{theme}] {entry.name}")


def run_win(cwd: Path, command_parts: list[str], *, theme: str, emit: Emit) -> None:
    if not command_parts:
        emit(f"[bold {theme}]Usage:[/bold {theme}] win <windows command>")
        return
    command = " ".join(command_parts)
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        shell=True,
        capture_output=True,
        text=True,
    )
    if completed.stdout.strip():
        emit(completed.stdout.rstrip("\n"))
    if completed.stderr.strip():
        emit(f"[bold {theme}]stderr:[/bold {theme}] {completed.stderr.rstrip()}")
    if completed.returncode != 0:
        emit(f"[bold {theme}]exit code:[/bold {theme}] {completed.returncode}")
