"""
backup_system.py — Backup, restore, and schedule compressed ZIP backups.

Features:
  - Timestamped ZIP backups
  - Restore from any previous backup
  - Backup history log (JSON)
  - Optional scheduled backups via 'schedule' library
"""

import json
import os
import shutil
import threading
import time
import zipfile
from datetime import datetime
from pathlib import Path

import schedule
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich import box
from modules.logger import log_action, log_error, log_section
from modules.settings import load_settings

console = Console()

# ─── Paths ─────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKUP_DIR   = PROJECT_ROOT / "backups"
HISTORY_FILE = BACKUP_DIR / "backup_history.json"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)


def _fmt_bytes(b: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.2f} {unit}"
        b /= 1024
    return f"{b:.2f} TB"


# ─── History helpers ────────────────────────────────────────────────────────

def _load_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_history(history: list[dict]) -> None:
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
    except Exception as exc:
        log_error(f"Could not save backup history: {exc}")


def _add_history_entry(source: str, zip_path: Path, size: int) -> None:
    history = _load_history()
    history.append({
        "timestamp": datetime.now().isoformat(),
        "source": source,
        "backup_file": str(zip_path),
        "size_bytes": size,
    })
    _save_history(history)


# ─── Core backup ────────────────────────────────────────────────────────────

def create_backup(source_dir: str, dest_dir: str | None = None) -> Path | None:
    """
    Compress source_dir into a timestamped ZIP archive.

    Args:
        source_dir : Directory to back up.
        dest_dir   : Where to place the ZIP (default: project backups/).

    Returns:
        Path to the created ZIP file, or None on failure.
    """
    log_section("Backup System")
    source = Path(source_dir).expanduser().resolve()
    if not source.is_dir():
        console.print(f"[red]✗ Source directory not found: {source}[/red]")
        log_error(f"Backup failed — source not found: {source}")
        return None

    dest = Path(dest_dir).expanduser().resolve() if dest_dir else BACKUP_DIR
    dest.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name  = f"{source.name}_{timestamp}.zip"
    zip_path  = dest / zip_name

    # Collect all files
    all_files = [f for f in source.rglob("*") if f.is_file()]
    console.print(f"[cyan]Backing up {len(all_files)} file(s) from [bold]{source}[/bold]…[/cyan]")

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[cyan]{task.completed}/{task.total}[/cyan]"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task("[green]Compressing…", total=len(all_files))
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for file in all_files:
                    arcname = file.relative_to(source.parent)
                    zf.write(file, arcname)
                    progress.advance(task)

        size = zip_path.stat().st_size
        _add_history_entry(str(source), zip_path, size)
        log_action(f"Backup created: {zip_path} ({_fmt_bytes(size)})")
        return zip_path

    except Exception as exc:
        log_error(f"Backup failed: {exc}")
        console.print(f"[red]✗ Backup failed: {exc}[/red]")
        return None


# ─── Restore ────────────────────────────────────────────────────────────────

def restore_backup(zip_path: str, restore_to: str) -> bool:
    """
    Extract a backup ZIP to restore_to directory.

    Returns True on success.
    """
    zip_file = Path(zip_path).expanduser().resolve()
    dest     = Path(restore_to).expanduser().resolve()

    if not zip_file.is_file():
        console.print(f"[red]✗ Backup file not found: {zip_file}[/red]")
        return False

    dest.mkdir(parents=True, exist_ok=True)
    log_section("Backup Restore")

    try:
        with zipfile.ZipFile(zip_file, "r") as zf:
            members = zf.namelist()
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[cyan]{task.completed}/{task.total}[/cyan]"),
                console=console,
                transient=True,
            ) as progress:
                task = progress.add_task("[blue]Extracting…", total=len(members))
                for member in members:
                    zf.extract(member, dest)
                    progress.advance(task)

        log_action(f"Restored '{zip_file}' → '{dest}'")
        return True
    except Exception as exc:
        log_error(f"Restore failed: {exc}")
        console.print(f"[red]✗ Restore failed: {exc}[/red]")
        return False


# ─── History display ────────────────────────────────────────────────────────

def show_backup_history() -> None:
    """Display all past backups in a Rich table."""
    history = _load_history()
    if not history:
        console.print(Panel("[yellow]No backup history found.[/yellow]", border_style="yellow"))
        return

    table = Table(
        title="🗂  Backup History",
        box=box.ROUNDED,
        border_style="bright_cyan",
        show_lines=True,
    )
    table.add_column("#",            style="dim",          justify="right", min_width=3)
    table.add_column("Timestamp",    style="bold white",   min_width=20)
    table.add_column("Source",       style="cyan")
    table.add_column("Backup File",  style="dim")
    table.add_column("Size",         style="green",        justify="right")

    for idx, entry in enumerate(history, 1):
        table.add_row(
            str(idx),
            entry.get("timestamp", "?"),
            entry.get("source", "?"),
            Path(entry.get("backup_file", "?")).name,
            _fmt_bytes(entry.get("size_bytes", 0)),
        )
    console.print(table)


# ─── Scheduler ─────────────────────────────────────────────────────────────

_scheduler_thread: threading.Thread | None = None
_scheduler_running = False


def _run_scheduler() -> None:
    """Background thread target for the schedule loop."""
    global _scheduler_running
    _scheduler_running = True
    while _scheduler_running:
        schedule.run_pending()
        time.sleep(60)


def start_scheduled_backup(source_dir: str, time_str: str = "02:00") -> None:
    """
    Schedule a daily backup of source_dir at time_str (HH:MM, 24h).
    Runs in a daemon background thread.

    BUG FIX: Clears all existing schedule jobs before adding the new one
    to prevent stacked duplicate jobs when called multiple times.
    Also guards against spawning multiple scheduler threads.
    """
    global _scheduler_thread, _scheduler_running

    def _job():
        console.print(f"\n[bold green]⏰ Scheduled backup starting…[/bold green]")
        zip_path = create_backup(source_dir)
        if zip_path:
            console.print(f"[green]✓ Scheduled backup saved to {zip_path}[/green]")

    # ── Clear old jobs to avoid stacking on re-schedule ──────────────────
    schedule.clear()
    schedule.every().day.at(time_str).do(_job)

    # ── Only start a new thread if none is already running ───────────────
    if _scheduler_thread is None or not _scheduler_thread.is_alive():
        _scheduler_running = True
        _scheduler_thread = threading.Thread(target=_run_scheduler, daemon=True)
        _scheduler_thread.start()
    # (if thread is already alive it will pick up the newly added job)

    log_action(f"Scheduled daily backup at {time_str} for '{source_dir}'")
    console.print(
        f"[green]✓ Scheduled backup set for [bold]{time_str}[/bold] daily.[/green]\n"
        "[dim](Scheduler runs in background while app is open.)[/dim]"
    )


# ─── Interactive Menu ──────────────────────────────────────────────────────

def backup_menu() -> None:
    """
    Interactive CLI for the Backup System.

    BUG FIX: Removed the inner `while True` loop.
    Navigation is now handled uniformly by main.py's loop,
    preventing the double "Press ENTER" prompt after pressing [0] Back.
    Sub-options are still fully accessible in a single visit.
    """
    settings = load_settings()

    console.print(Panel("[bold green]🗄  Backup System[/bold green]", border_style="green"))
    console.print("[1] Create a new backup")
    console.print("[2] Restore a backup")
    console.print("[3] View backup history")
    console.print("[4] Schedule daily backup")
    console.print("[0] Back")
    console.print()

    choice = Prompt.ask("[bold green]Select option[/bold green]", default="0")

    if choice == "1":
        src = Prompt.ask(
            "[bold green]Directory to backup[/bold green]",
            default=settings.get("default_backup_dir", str(Path.home())),
        )
        use_custom = Confirm.ask("Use custom destination for the ZIP?", default=False)
        dst = None
        if use_custom:
            dst = Prompt.ask("[bold green]Destination directory[/bold green]")
        zip_path = create_backup(src, dst)
        if zip_path:
            console.print(Panel(
                f"[bold green]✓ Backup created![/bold green]\n  → [white]{zip_path}[/white]\n"
                f"  Size: [cyan]{_fmt_bytes(zip_path.stat().st_size)}[/cyan]",
                border_style="green",
            ))

    elif choice == "2":
        show_backup_history()
        zip_p = Prompt.ask("[bold green]Enter full path of backup ZIP to restore[/bold green]")
        dest  = Prompt.ask("[bold green]Restore to directory[/bold green]", default=str(Path.home() / "restored"))
        success = restore_backup(zip_p, dest)
        if success:
            console.print(Panel(
                f"[bold green]✓ Backup restored to:[/bold green] [white]{dest}[/white]",
                border_style="green",
            ))

    elif choice == "3":
        show_backup_history()

    elif choice == "4":
        src = Prompt.ask(
            "[bold green]Directory to backup[/bold green]",
            default=settings.get("default_backup_dir", str(Path.home())),
        )
        t = Prompt.ask(
            "[bold green]Time for daily backup (HH:MM, 24h)[/bold green]",
            default=settings.get("backup_schedule_time", "02:00"),
        )
        start_scheduled_backup(src, t)

    elif choice == "0":
        return
    else:
        console.print("[red]Invalid option.[/red]")
