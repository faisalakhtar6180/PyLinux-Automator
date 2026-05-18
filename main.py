#!/usr/bin/env python3
"""
main.py — PyLinux Automator Entry Point
========================================
A modular Linux automation toolkit with a beautiful, beginner-friendly CLI.

Run:
    python3 main.py

Author : PyLinux Automator
License: MIT
"""

import os
import sys
import time

# ── Ensure project root is on sys.path ─────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.prompt import Prompt
from rich.live import Live
from rich import box

# ── Internal modules ────────────────────────────────────────────────────────
from modules.file_organizer   import file_organizer_menu
from modules.backup_system    import backup_menu
from modules.disk_monitor     import disk_monitor_menu
from modules.system_cleaner   import system_cleaner_menu
from modules.duplicate_finder import duplicate_finder_menu
from modules.system_info      import display_system_dashboard
from modules.settings         import settings_menu, load_settings
from modules.logger           import log_action, log_section

console = Console()

# ───────────────────────────────────────────────────────────────────────────
# ASCII Banner
# ───────────────────────────────────────────────────────────────────────────
BANNER = r"""
██████╗ ██╗   ██╗██╗     ██╗███╗   ██╗██╗   ██╗██╗  ██╗
██╔══██╗╚██╗ ██╔╝██║     ██║████╗  ██║██║   ██║╚██╗██╔╝
██████╔╝ ╚████╔╝ ██║     ██║██╔██╗ ██║██║   ██║ ╚███╔╝
██╔═══╝   ╚██╔╝  ██║     ██║██║╚██╗██║██║   ██║ ██╔██╗
██║        ██║   ███████╗██║██║ ╚████║╚██████╔╝██╔╝ ██╗
╚═╝        ╚═╝   ╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝



       █████╗ ██╗   ██╗████████╗ ██████╗ ███╗   ███╗ █████╗ ████████╗ ██████╗ ██████╗ 
      ██╔══██╗██║   ██║╚══██╔══╝██╔═══██╗████╗ ████║██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗
      ███████║██║   ██║   ██║   ██║   ██║██╔████╔██║███████║   ██║   ██║   ██║██████╔╝
      ██╔══██║██║   ██║   ██║   ██║   ██║██║╚██╔╝██║██╔══██║   ██║   ██║   ██║██╔══██╗
      ██║  ██║╚██████╔╝   ██║   ╚██████╔╝██║ ╚═╝ ██║██║  ██║   ██║   ╚██████╔╝██║  ██║
      ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
"""

TAGLINE = "🐧  Linux Automation Toolkit  |  v1.0.0  |  Built with Python"

# ───────────────────────────────────────────────────────────────────────────
# Menu Items
# ───────────────────────────────────────────────────────────────────────────
MENU_ITEMS = [
    ("1", "📁", "Organize Files",        "Auto-sort files into categorized folders"),
    ("2", "🗄", "Backup Files",          "Create & restore compressed backups"),
    ("3", "💾", "Monitor Disk Usage",    "View disk space with visual bars"),
    ("4", "🧹", "Clean System",          "Remove temp files & empty folders"),
    ("5", "🔁", "Find Duplicate Files",  "Detect & remove duplicate files (MD5)"),
    ("6", "🖥", "System Information",   "Full system dashboard (CPU / RAM / Net)"),
    ("7", "⚙", "Settings",             "Configure paths, thresholds & schedule"),
    ("8", "🚪", "Exit",                  "Quit PyLinux Automator"),
]


# ───────────────────────────────────────────────────────────────────────────
# UI Helpers
# ───────────────────────────────────────────────────────────────────────────

def _clear() -> None:
    os.system("clear")


def _print_banner() -> None:
    """Print the ASCII banner with colours."""
    console.print(Text(BANNER, style="bold bright_cyan"), justify="center")
    console.print(Align.center(Text(TAGLINE, style="bold bright_white on #1a1a2e")))
    console.print()


def _print_menu() -> None:
    """Render the interactive main menu."""
    table = Table(
        box=box.ROUNDED,
        border_style="bright_cyan",
        show_header=True,
        header_style="bold bright_cyan",
        expand=False,
        min_width=60,
    )
    table.add_column("  #", justify="center", style="bold bright_yellow", width=4)
    table.add_column("Feature",             style="bold white",      min_width=22)
    table.add_column("Description",         style="dim white",       min_width=40)

    for key, icon, name, desc in MENU_ITEMS:
        if key == "8":
            table.add_row(f"[bold red]{key}[/bold red]", f"[bold red]{icon}  {name}[/bold red]", f"[dim]{desc}[/dim]")
        else:
            table.add_row(key, f"{icon}  {name}", desc)

    console.print(Align.center(table))
    console.print()


def _splash_loading() -> None:
    """Show a quick animated loading splash on first run."""
    steps = [
        ("Initialising modules",     0.15),
        ("Loading configuration",    0.12),
        ("Checking system state",    0.12),
        ("Starting Rich interface",  0.10),
    ]
    with console.status("[bold cyan]Booting PyLinux Automator…[/bold cyan]", spinner="dots12"):
        for label, delay in steps:
            console.log(f"[green]✓[/green]  {label}")
            time.sleep(delay)


def _separator(char: str = "─", width: int = 72, color: str = "bright_cyan") -> None:
    console.print(f"[{color}]{char * width}[/{color}]", justify="center")


# ───────────────────────────────────────────────────────────────────────────
# Dispatch
# ───────────────────────────────────────────────────────────────────────────

DISPATCH = {
    "1": file_organizer_menu,
    "2": backup_menu,
    "3": disk_monitor_menu,
    "4": system_cleaner_menu,
    "5": duplicate_finder_menu,
    "6": display_system_dashboard,
    "7": settings_menu,
}


def _run_feature(choice: str) -> None:
    """Clear screen, run the chosen feature, then pause before returning."""
    _clear()
    _separator()
    fn = DISPATCH.get(choice)
    if fn:
        log_action(f"User selected menu option {choice} — {MENU_ITEMS[int(choice)-1][2]}")
        fn()
    _separator()
    console.print()
    Prompt.ask("[dim]Press ENTER to return to the main menu[/dim]", default="")


# ───────────────────────────────────────────────────────────────────────────
# Scheduled backup auto-start
# ───────────────────────────────────────────────────────────────────────────

def _maybe_start_scheduler() -> None:
    """If auto_schedule_backup is enabled in settings, start it silently."""
    try:
        settings = load_settings()
        if settings.get("auto_schedule_backup", False):
            from modules.backup_system import start_scheduled_backup
            src = settings.get("default_backup_dir", str(os.path.expanduser("~")))
            t   = settings.get("backup_schedule_time", "02:00")
            start_scheduled_backup(src, t)
            log_action(f"Auto-scheduler started for '{src}' at {t}")
    except Exception as exc:
        pass   # Silent — don't block startup


# ───────────────────────────────────────────────────────────────────────────
# Main Loop
# ───────────────────────────────────────────────────────────────────────────

def main() -> None:
    """Application entry point."""
    _clear()
    _splash_loading()
    _maybe_start_scheduler()
    log_section("PyLinux Automator Started")

    while True:
        _clear()
        _print_banner()
        _print_menu()

        choice = Prompt.ask(
            "[bold bright_green]  Enter your choice[/bold bright_green]",
            choices=[str(i) for i in range(1, 9)],
            show_choices=False,
        )

        if choice == "8":
            _clear()
            console.print(Panel(
                Align.center(Text(
                    "\n  Thank you for using PyLinux Automator! 🐧\n"
                    "  Built with ❤  in Python  |  Stay curious, keep hacking!\n",
                    style="bold bright_cyan",
                )),
                border_style="bright_cyan",
                padding=(1, 4),
            ))
            log_action("PyLinux Automator exited by user.")
            sys.exit(0)

        _run_feature(choice)


if __name__ == "__main__":
    main()
