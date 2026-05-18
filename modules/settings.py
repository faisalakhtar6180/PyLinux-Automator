"""
settings.py — Load, save, and display user settings.
Config stored as JSON in config/settings.json.
"""

import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from modules.logger import log_action, log_error

console = Console()

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "settings.json"

# ─── Defaults ──────────────────────────────────────────────────────────────
DEFAULTS: dict = {
    "default_organize_dir": "~/Downloads",
    "default_backup_dir": "~/",
    "backup_storage_dir": "backups",
    "disk_warn_threshold": 85,
    "log_level": "INFO",
    "theme": "dark",
    "auto_schedule_backup": False,
    "backup_schedule_time": "02:00",
    "cleanup_extensions": [".tmp", ".log", ".bak", ".swp", ".DS_Store"],
    "reports_dir": "reports",
}


def load_settings() -> dict:
    """Load settings from JSON file, creating it with defaults if missing."""
    if not CONFIG_PATH.exists():
        save_settings(DEFAULTS)
        return DEFAULTS.copy()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Merge with defaults to add any new keys
        merged = DEFAULTS.copy()
        merged.update(data)
        return merged
    except Exception as e:
        log_error(f"Failed to load settings: {e}")
        return DEFAULTS.copy()


def save_settings(settings: dict) -> None:
    """Persist settings dictionary to JSON file."""
    try:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
        log_action("Settings saved.")
    except Exception as e:
        log_error(f"Failed to save settings: {e}")
        console.print(f"[red]Error saving settings: {e}[/red]")


def display_settings(settings: dict) -> None:
    """Pretty-print settings as a Rich table."""
    table = Table(title="⚙  Current Settings", border_style="bright_cyan", show_lines=True)
    table.add_column("Key", style="bold yellow", min_width=25)
    table.add_column("Value", style="white")
    for key, value in settings.items():
        table.add_row(str(key), str(value))
    console.print(table)


def settings_menu() -> None:
    """
    Interactive settings editor.

    BUG FIX: Removed the inner `while True` loop.
    Navigation is handled uniformly by main.py's loop,
    preventing the double "Press ENTER" prompt after pressing [0] Back.
    """
    settings = load_settings()

    console.print(Panel("[bold cyan]⚙  Settings[/bold cyan]", border_style="cyan"))
    display_settings(settings)
    console.print()
    console.print("[1] Change default organize directory")
    console.print("[2] Change default backup directory")
    console.print("[3] Change disk warning threshold (%)")
    console.print("[4] Toggle auto schedule backup")
    console.print("[5] Change backup schedule time (HH:MM)")
    console.print("[6] Reset to defaults")
    console.print("[0] Back to main menu")
    console.print()

    choice = Prompt.ask("[bold green]Select option[/bold green]", default="0")

    if choice == "1":
        new_val = Prompt.ask("Enter new organize directory", default=settings["default_organize_dir"])
        settings["default_organize_dir"] = new_val
        save_settings(settings)
        console.print("[green]✓ Updated![/green]")

    elif choice == "2":
        new_val = Prompt.ask("Enter new backup source directory", default=settings["default_backup_dir"])
        settings["default_backup_dir"] = new_val
        save_settings(settings)
        console.print("[green]✓ Updated![/green]")

    elif choice == "3":
        val = IntPrompt.ask("Enter disk warning threshold (1-99)", default=settings["disk_warn_threshold"])
        settings["disk_warn_threshold"] = max(1, min(99, val))
        save_settings(settings)
        console.print("[green]✓ Updated![/green]")

    elif choice == "4":
        settings["auto_schedule_backup"] = not settings["auto_schedule_backup"]
        save_settings(settings)
        state = "enabled" if settings["auto_schedule_backup"] else "disabled"
        console.print(f"[green]✓ Auto backup {state}![/green]")

    elif choice == "5":
        t = Prompt.ask("Enter time (HH:MM, 24h format)", default=settings["backup_schedule_time"])
        settings["backup_schedule_time"] = t
        save_settings(settings)
        console.print("[green]✓ Updated![/green]")

    elif choice == "6":
        settings = DEFAULTS.copy()
        save_settings(settings)
        console.print("[green]✓ Settings reset to defaults![/green]")

    elif choice == "0":
        return
    else:
        console.print("[red]Invalid option.[/red]")

