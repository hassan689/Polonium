"""TUI theme, layout CSS, and static copy."""

THEME_COLOR = "#07F5E9"
DEFAULT_API_URL = "http://localhost:8000/api/v1"

ASCII_LOGO = """
██████╗  ██████╗ ██╗      ██████╗ ███╗   ██╗██╗██╗   ██╗███╗   ███╗
██╔══██╗██╔═══██╗██║     ██╔═══██╗████╗  ██║██║██║   ██║████╗ ████║
██████╔╝██║   ██║██║     ██║   ██║██╔██╗ ██║██║██║   ██║██╔████╔██║
██╔═══╝ ██║   ██║██║     ██║   ██║██║╚██╗██║██║██║   ██║██║╚██╔╝██║
██║     ╚██████╔╝███████╗╚██████╔╝██║ ╚████║██║╚██████╔╝██║ ╚═╝ ██║
╚═╝      ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝ ╚═════╝ ╚═╝     ╚═╝
"""

TUI_CSS = f"""
Screen {{ layout: vertical; background: #06171c; color: #eafcfa; }}
Header {{ background: #06171c; color: {THEME_COLOR}; }}
Footer {{ background: #06171c; color: {THEME_COLOR}; }}
#terminal {{ height: 1fr; border: round {THEME_COLOR}; padding: 0 1; }}
#command_input {{
    border: round {THEME_COLOR};
    margin-top: 1;
    color: {THEME_COLOR};
    background: #0a1f25;
}}
"""

TIPS_MARKUP = (
    "Tips\n"
    "- Start with: repo list\n"
    "- Ctrl+L clear output | Ctrl+P command palette | q quit\n"
    "- If Ctrl+P does nothing, the host (e.g. Cursor) may capture it; try Windows Terminal\n"
    "- Get help any time: help"
)


def help_markup() -> str:
    c = THEME_COLOR
    return (
        f"[bold {c}]Commands[/bold {c}]\n"
        f"[{c}]repo list\n"
        "repo connect <github_url>\n"
        "repo overview <repo_id>\n"
        "file explain <repo_id> <path>\n"
        "chat send <repo_id> <message>\n"
        "chat history <repo_id>\n"
        "search code <query>\n"
        "pwd\ncd <path>\nls | dir\ntree\n"
        f"win <windows command>[/{c}]"
    )
