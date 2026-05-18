"""
duplicate_finder.py — Detect and optionally delete duplicate files using MD5 hashing.

Uses multi-threading for faster directory scans.
"""

import hashlib
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from collections import defaultdict

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TaskID
from rich import box
from modules.logger import log_action, log_error, log_section

console = Console()

# ─── Hashing ───────────────────────────────────────────────────────────────

def _hash_file(path: Path, chunk_size: int = 65536) -> str | None:
    """Return MD5 hex-digest of a file, or None on error."""
    hasher = hashlib.md5()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(chunk_size):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (PermissionError, OSError) as exc:
        log_error(f"Cannot hash '{path}': {exc}")
        return None


def _fmt_bytes(b: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if b < 1024:
            return f"{b:.2f} {unit}"
        b /= 1024
    return f"{b:.2f} TB"


# ─── Scanner ───────────────────────────────────────────────────────────────

def find_duplicates(directory: str, workers: int = 8) -> dict[str, list[Path]]:
    """
    Scan *directory* recursively and return a dict of
    {md5_hash: [list_of_duplicate_paths]} for hashes with 2+ files.

    Uses a thread pool for fast parallel hashing.

    BUG FIX (Bug 5): Zero-byte files are skipped before hashing.
    All empty files share the same MD5 (d41d8cd98f00b204e9800998ecf8427e),
    so without this guard every .gitkeep / empty placeholder would be
    flagged as a duplicate and offered for deletion.
    """
    root = Path(directory).expanduser().resolve()
    if not root.is_dir():
        console.print(f"[red]✗ Directory not found: {root}[/red]")
        return {}

    log_section("Duplicate File Detector")
    log_action(f"Scanning for duplicates in: {root}")

    # Collect all non-empty files
    all_files: list[Path] = [
        f for f in root.rglob("*")
        if f.is_file() and f.stat().st_size > 0   # skip empty files (Bug 5 fix)
    ]
    console.print(f"[cyan]Found {len(all_files)} non-empty file(s) to scan…[/cyan]")

    hash_map: dict[str, list[Path]] = defaultdict(list)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[cyan]{task.completed}/{task.total}[/cyan]"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("[cyan]Hashing files…", total=len(all_files))

        with ThreadPoolExecutor(max_workers=workers) as executor:
            future_to_path = {executor.submit(_hash_file, f): f for f in all_files}
            for future in as_completed(future_to_path):
                file_path = future_to_path[future]
                digest = future.result()
                if digest:
                    hash_map[digest].append(file_path)
                progress.advance(task)

    # Keep only groups with more than one file
    duplicates = {h: paths for h, paths in hash_map.items() if len(paths) > 1}
    log_action(f"Found {len(duplicates)} duplicate group(s).")
    return duplicates


# ─── Display ───────────────────────────────────────────────────────────────

def display_duplicates(duplicates: dict[str, list[Path]]) -> None:
    """Pretty-print duplicate groups."""
    if not duplicates:
        console.print(Panel(
            "[bold green]✓ No duplicate files found![/bold green]",
            border_style="green",
        ))
        return

    total_wasted = 0
    total_dupes = 0

    table = Table(
        title=f"🔁 Duplicate Files ({len(duplicates)} group(s))",
        box=box.ROUNDED,
        border_style="yellow",
        show_lines=True,
        expand=True,
    )
    table.add_column("#", style="dim", justify="right", min_width=3)
    table.add_column("Group / File", style="white")
    table.add_column("Size", style="cyan", justify="right")

    for idx, (digest, paths) in enumerate(duplicates.items(), start=1):
        file_size = paths[0].stat().st_size if paths[0].exists() else 0
        wasted = file_size * (len(paths) - 1)
        total_wasted += wasted
        total_dupes += len(paths) - 1

        table.add_row(
            str(idx),
            f"[bold yellow]Group {idx}[/bold yellow]  "
            f"[dim](hash: {digest[:12]}…, {len(paths)} copies)[/dim]",
            f"[bold]{_fmt_bytes(file_size)} each[/bold]",
        )
        for p in paths:
            table.add_row("", f"  [dim]{p}[/dim]", "")

    table.add_row(
        "", f"[bold red]TOTAL duplicates: {total_dupes}[/bold red]",
        f"[bold red]{_fmt_bytes(total_wasted)} wasted[/bold red]"
    )
    console.print(table)


# ─── Safe deletion ─────────────────────────────────────────────────────────

def delete_duplicates(duplicates: dict[str, list[Path]]) -> int:
    """
    Keep the first (alphabetically earliest) copy of each duplicate group
    and delete the rest after user confirmation.

    Returns the number of files deleted.
    """
    if not duplicates:
        return 0

    files_to_delete: list[Path] = []
    for paths in duplicates.values():
        sorted_paths = sorted(paths)
        files_to_delete.extend(sorted_paths[1:])   # keep [0], delete rest

    console.print(f"\n[yellow]Will DELETE {len(files_to_delete)} file(s) (keeping 1 copy of each group).[/yellow]")
    confirmed = Confirm.ask(
        "[bold red]Confirm deletion?[/bold red] [dim](Cannot be undone)[/dim]",
        default=False,
    )
    if not confirmed:
        console.print("[yellow]Deletion cancelled.[/yellow]")
        return 0

    deleted = 0
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[cyan]{task.completed}/{task.total}[/cyan]"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("[red]Deleting duplicates…", total=len(files_to_delete))
        for f in files_to_delete:
            try:
                f.unlink()
                deleted += 1
                log_action(f"Deleted duplicate: {f}")
            except Exception as exc:
                log_error(f"Could not delete '{f}': {exc}")
            finally:
                progress.advance(task)

    return deleted


# ─── Interactive Menu ──────────────────────────────────────────────────────

def duplicate_finder_menu() -> None:
    """Interactive CLI for duplicate file detection."""
    console.print(Panel("[bold yellow]🔁 Duplicate File Detector[/bold yellow]", border_style="yellow"))

    directory = Prompt.ask(
        "[bold green]Enter directory to scan[/bold green]",
        default=str(Path.home()),
    )

    duplicates = find_duplicates(directory)
    display_duplicates(duplicates)

    if duplicates:
        console.print()
        console.print("[1] Delete duplicates (keep 1 copy each)")
        console.print("[0] Back without deleting")
        choice = Prompt.ask("[bold green]Select option[/bold green]", default="0")
        if choice == "1":
            deleted = delete_duplicates(duplicates)
            if deleted:
                console.print(Panel(
                    f"[bold green]✓ Deleted {deleted} duplicate file(s).[/bold green]",
                    border_style="green",
                ))
