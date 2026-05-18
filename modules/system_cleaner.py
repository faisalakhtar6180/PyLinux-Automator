"""
system_cleaner.py — Safe system cleanup tool.

Removes:
  - Temporary files (configurable extensions)
  - Empty folders
  - Common cache directories (optional)

Always previews before deleting.
"""

import os
import shutil
from pathlib import Path
from typing import Generator

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich import box
from modules.logger import log_action, log_error, log_section
from modules.settings import load_settings

console = Console()

# Default temp-file extensions
DEFAULT_JUNK_EXTENSIONS: list[str] = [
    ".tmp", ".bak", ".swp", ".swo", ".log~", ".DS_Store", ".Thumbs.db",
    ".pyc", ".pyo", ".pyd",
]

# Common cache directories relative to home
CACHE_DIRS: list[str] = [
    "~/.cache/thumbnails",
    "~/.local/share/Trash",
    "/tmp",
]


def _fmt_bytes(b: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.2f} {unit}"
        b /= 1024
    return f"{b:.2f} TB"


def _scan_junk_files(directory: Path, extensions: list[str]) -> Generator[Path, None, None]:
    """Yield files matching junk extensions recursively."""
    for file in directory.rglob("*"):
        if file.is_file() and file.suffix.lower() in extensions:
            yield file


def _scan_empty_dirs(directory: Path) -> Generator[Path, None, None]:
    """Yield empty directories (deepest first)."""
    for dirpath in sorted(directory.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if dirpath.is_dir():
            try:
                if not any(dirpath.iterdir()):
                    yield dirpath
            except PermissionError:
                continue


def preview_cleanup(directory: str, extensions: list[str]) -> tuple[list[Path], list[Path]]:
    """
    Scan and return (junk_files, empty_dirs) without deleting anything.
    """
    root = Path(directory).expanduser().resolve()
    if not root.is_dir():
        console.print(f"[red]✗ Directory not found: {root}[/red]")
        return [], []

    junk_files = list(_scan_junk_files(root, extensions))
    empty_dirs = list(_scan_empty_dirs(root))
    return junk_files, empty_dirs


def _display_preview(junk_files: list[Path], empty_dirs: list[Path]) -> None:
    """Pretty-print preview table."""
    if not junk_files and not empty_dirs:
        console.print(Panel("[green]✓ No junk found. Your system is clean![/green]", border_style="green"))
        return

    if junk_files:
        table = Table(title="🗑  Junk Files Found", box=box.SIMPLE, border_style="yellow", show_lines=False)
        table.add_column("File", style="dim white")
        table.add_column("Size", style="cyan", justify="right")
        total_size = 0
        for f in junk_files[:30]:
            size = f.stat().st_size
            total_size += size
            table.add_row(str(f), _fmt_bytes(size))
        if len(junk_files) > 30:
            table.add_row(f"… and {len(junk_files) - 30} more files", "")
        table.add_row(f"[bold]TOTAL ({len(junk_files)} files)[/bold]", f"[bold cyan]{_fmt_bytes(total_size)}[/bold]")
        console.print(table)

    if empty_dirs:
        console.print(f"\n[yellow]Found {len(empty_dirs)} empty director(ies).[/yellow]")


def run_cleanup(directory: str, extensions: list[str], delete_empty: bool = True) -> dict:
    """
    Delete junk files (by extension) and (optionally) empty directories.

    Returns summary dict.
    """
    log_section("System Cleaner")
    junk_files, empty_dirs = preview_cleanup(directory, extensions)

    _display_preview(junk_files, empty_dirs)

    if not junk_files and not empty_dirs:
        return {"files_deleted": 0, "dirs_deleted": 0, "bytes_freed": 0}

    confirmed = Confirm.ask(
        "\n[bold yellow]Proceed with cleanup?[/bold yellow] [dim](This cannot be undone)[/dim]",
        default=False,
    )
    if not confirmed:
        console.print("[yellow]Cleanup cancelled.[/yellow]")
        return {"files_deleted": 0, "dirs_deleted": 0, "bytes_freed": 0}

    files_deleted = 0
    dirs_deleted = 0
    bytes_freed = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[cyan]{task.completed}/{task.total}[/cyan]"),
        console=console,
        transient=True,
    ) as progress:
        # Delete junk files
        task = progress.add_task("[red]Deleting junk files…", total=len(junk_files))
        for f in junk_files:
            try:
                size = f.stat().st_size
                f.unlink()
                bytes_freed += size
                files_deleted += 1
                log_action(f"Deleted file: {f}")
            except Exception as exc:
                log_error(f"Failed to delete '{f}': {exc}")
            finally:
                progress.advance(task)

        # Delete empty directories
        if delete_empty:
            task2 = progress.add_task("[red]Removing empty directories…", total=len(empty_dirs))
            for d in empty_dirs:
                try:
                    d.rmdir()
                    dirs_deleted += 1
                    log_action(f"Removed empty dir: {d}")
                except Exception as exc:
                    log_error(f"Failed to remove dir '{d}': {exc}")
                finally:
                    progress.advance(task2)

    return {"files_deleted": files_deleted, "dirs_deleted": dirs_deleted, "bytes_freed": bytes_freed}


def run_tmp_cleanup() -> dict:
    """
    BUG FIX (Bug 3): Dedicated /tmp cleaner that removes ALL files and
    sub-directories in /tmp — not just those matching junk extensions.

    Using only extension-based filtering on /tmp left most temp files
    (which have no extension) untouched. This function bypasses the
    extension filter and is the correct behaviour users expect from a
    /tmp cleaner.

    Locked / permission-denied files are silently skipped.
    Returns summary dict.
    """
    tmp = Path("/tmp")
    log_section("System Cleaner — /tmp")

    entries = list(tmp.iterdir())
    if not entries:
        console.print(Panel("[green]✓ /tmp is already empty.[/green]", border_style="green"))
        return {"files_deleted": 0, "dirs_deleted": 0, "bytes_freed": 0}

    # Preview
    console.print(f"[cyan]Found {len(entries)} item(s) in /tmp[/cyan]")
    confirmed = Confirm.ask(
        "[bold red]Delete ALL contents of /tmp?[/bold red] [dim](Cannot be undone)[/dim]",
        default=False,
    )
    if not confirmed:
        console.print("[yellow]Cancelled.[/yellow]")
        return {"files_deleted": 0, "dirs_deleted": 0, "bytes_freed": 0}

    files_deleted = dirs_deleted = 0
    bytes_freed = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[cyan]{task.completed}/{task.total}[/cyan]"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("[red]Cleaning /tmp…", total=len(entries))
        for entry in entries:
            try:
                if entry.is_file() or entry.is_symlink():
                    size = entry.stat().st_size if entry.is_file() else 0
                    entry.unlink()
                    bytes_freed += size
                    files_deleted += 1
                    log_action(f"Deleted from /tmp: {entry}")
                elif entry.is_dir():
                    dir_size = sum(
                        f.stat().st_size for f in entry.rglob("*") if f.is_file()
                    )
                    shutil.rmtree(entry, ignore_errors=True)
                    bytes_freed += dir_size
                    dirs_deleted += 1
                    log_action(f"Removed dir from /tmp: {entry}")
            except PermissionError:
                log_error(f"Permission denied (skipped): {entry}")
            except Exception as exc:
                log_error(f"Error removing '{entry}': {exc}")
            finally:
                progress.advance(task)

    return {"files_deleted": files_deleted, "dirs_deleted": dirs_deleted, "bytes_freed": bytes_freed}


def system_cleaner_menu() -> None:
    """Interactive CLI for system cleaner."""
    settings = load_settings()
    ext_list = settings.get("cleanup_extensions", DEFAULT_JUNK_EXTENSIONS)

    console.print(Panel("[bold red]🧹 System Cleaner[/bold red]", border_style="red"))
    console.print("[1] Preview cleanup (safe — no deletion)")
    console.print("[2] Run cleanup (with confirmation)")
    console.print("[3] Clean system /tmp directory (ALL contents)")
    console.print("[0] Back")
    console.print()

    choice = Prompt.ask("[bold green]Select option[/bold green]", default="1")

    if choice == "0":
        return

    if choice in ("1", "2"):
        directory = Prompt.ask(
            "[bold green]Enter directory to clean[/bold green]",
            default=str(Path.home()),
        )
        del_empty = Confirm.ask("Also remove empty folders?", default=True)
    elif choice == "3":
        # BUG FIX: call the dedicated /tmp cleaner, not the extension-filtered one
        result = run_tmp_cleanup()
        console.print(Panel(
            f"[bold green]✓ /tmp Cleaned![/bold green]\n"
            f"  Files deleted : [cyan]{result['files_deleted']}[/cyan]\n"
            f"  Dirs removed  : [cyan]{result['dirs_deleted']}[/cyan]\n"
            f"  Space freed   : [cyan]{_fmt_bytes(result['bytes_freed'])}[/cyan]",
            border_style="green",
        ))
        log_action(
            f"/tmp cleanup: {result['files_deleted']} files, "
            f"{result['dirs_deleted']} dirs, {_fmt_bytes(result['bytes_freed'])} freed."
        )
        return
    else:
        console.print("[red]Invalid option.[/red]")
        return

    if choice == "1":
        junk, empty = preview_cleanup(directory, ext_list)
        _display_preview(junk, empty)
    else:
        result = run_cleanup(directory, ext_list, del_empty)
        console.print(Panel(
            f"[bold green]✓ Cleanup Complete![/bold green]\n"
            f"  Files deleted : [cyan]{result['files_deleted']}[/cyan]\n"
            f"  Dirs removed  : [cyan]{result['dirs_deleted']}[/cyan]\n"
            f"  Space freed   : [cyan]{_fmt_bytes(result['bytes_freed'])}[/cyan]",
            border_style="green",
        ))
        log_action(
            f"Cleanup done: {result['files_deleted']} files, "
            f"{result['dirs_deleted']} dirs, {_fmt_bytes(result['bytes_freed'])} freed."
        )
