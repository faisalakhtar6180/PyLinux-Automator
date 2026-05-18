"""
file_organizer.py — Organize files into categorized folders.

Categories:
  Documents, Images, Videos, Music, Archives, Code, Others
"""

import shutil
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from modules.logger import log_action, log_error, log_section

console = Console()

# ─── Extension → Folder mapping ────────────────────────────────────────────
CATEGORY_MAP: dict[str, list[str]] = {
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".odt", ".rtf", ".xlsx",
                  ".xls", ".pptx", ".ppt", ".csv", ".md", ".tex"],
    "Images":    [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp",
                  ".ico", ".tiff", ".heic", ".raw"],
    "Videos":    [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm",
                  ".mpeg", ".3gp"],
    "Music":     [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
    "Archives":  [".zip", ".tar", ".gz", ".bz2", ".xz", ".rar", ".7z", ".iso"],
    "Code":      [".py", ".js", ".ts", ".html", ".css", ".java", ".c", ".cpp",
                  ".h", ".sh", ".bash", ".json", ".yaml", ".yml", ".xml",
                  ".sql", ".php", ".go", ".rs", ".rb", ".kt"],
    "Others":    [],  # Catch-all
}

# Reverse lookup: extension → category
_EXT_TO_CAT: dict[str, str] = {}
for _cat, _exts in CATEGORY_MAP.items():
    for _ext in _exts:
        _EXT_TO_CAT[_ext.lower()] = _cat


def _categorize(file: Path) -> str:
    """Return the category folder name for a given file."""
    return _EXT_TO_CAT.get(file.suffix.lower(), "Others")


def _safe_destination(dest_dir: Path, filename: str) -> Path:
    """Return a non-colliding destination path (appends _1, _2 … if needed)."""
    dest = dest_dir / filename
    if not dest.exists():
        return dest
    stem, suffix = Path(filename).stem, Path(filename).suffix
    counter = 1
    while True:
        dest = dest_dir / f"{stem}_{counter}{suffix}"
        if not dest.exists():
            return dest
        counter += 1


def organize_files(source_dir: str, target_dir: str | None = None) -> dict:
    """
    Move files from source_dir into categorized sub-folders.

    Args:
        source_dir: Directory to scan for files.
        target_dir: Where to create category folders (defaults to source_dir).

    Returns:
        Summary dict {category: count}.
    """
    source = Path(source_dir).expanduser().resolve()
    target = Path(target_dir).expanduser().resolve() if target_dir else source

    if not source.is_dir():
        console.print(f"[red]✗ Source directory not found: {source}[/red]")
        log_error(f"Organize failed — source not found: {source}")
        return {}

    files = [f for f in source.iterdir() if f.is_file()]
    if not files:
        console.print("[yellow]⚠  No files found in source directory.[/yellow]")
        return {}

    log_section("File Organizer")
    log_action(f"Organizing {len(files)} files from '{source}' → '{target}'")

    summary: dict[str, int] = {cat: 0 for cat in CATEGORY_MAP}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[bold cyan]{task.completed}/{task.total}[/bold cyan]"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("[cyan]Organizing files…", total=len(files))

        for file in files:
            try:
                category = _categorize(file)
                cat_dir = target / category
                cat_dir.mkdir(parents=True, exist_ok=True)
                dest_path = _safe_destination(cat_dir, file.name)
                shutil.move(str(file), str(dest_path))
                summary[category] += 1
                log_action(f"Moved '{file.name}' → {category}/")
            except Exception as exc:
                log_error(f"Could not move '{file.name}': {exc}")
                console.print(f"[red]  ✗ Failed: {file.name} — {exc}[/red]")
            finally:
                progress.advance(task)

    return {k: v for k, v in summary.items() if v > 0}


def _display_summary(summary: dict, source: str) -> None:
    """Print a pretty summary table after organizing."""
    table = Table(title="📁 Organization Summary", border_style="bright_green", show_lines=True)
    table.add_column("Category", style="bold yellow", min_width=15)
    table.add_column("Files Moved", style="bold white", justify="right")

    total = 0
    for cat, count in summary.items():
        table.add_row(cat, str(count))
        total += count

    table.add_row("[bold cyan]TOTAL[/bold cyan]", f"[bold cyan]{total}[/bold cyan]")
    console.print(table)
    console.print(f"[green]✓ Done! Files organized from:[/green] [white]{source}[/white]")


def file_organizer_menu() -> None:
    """Interactive CLI for the File Organizer feature."""
    console.print(Panel("[bold cyan]📁 File Organizer[/bold cyan]", border_style="cyan"))

    source = Prompt.ask(
        "[bold green]Enter source directory to organize[/bold green]",
        default=str(Path.home() / "Downloads"),
    )
    use_custom_target = Confirm.ask("Use a different target directory for organized folders?", default=False)
    target = None
    if use_custom_target:
        target = Prompt.ask("[bold green]Enter target directory[/bold green]")

    # Preview
    source_path = Path(source).expanduser().resolve()
    if source_path.is_dir():
        all_files = [f for f in source_path.iterdir() if f.is_file()]
        console.print(f"\n[cyan]Found {len(all_files)} file(s) in[/cyan] [white]{source_path}[/white]")
        if not all_files:
            console.print("[yellow]No files to organize.[/yellow]")
            return

        # Show preview table
        preview = Table(title="Preview (first 10 files)", border_style="dim", show_lines=False)
        preview.add_column("File", style="dim white")
        preview.add_column("→ Category", style="cyan")
        for f in all_files[:10]:
            preview.add_row(f.name, _categorize(f))
        if len(all_files) > 10:
            preview.add_row(f"… and {len(all_files) - 10} more", "")
        console.print(preview)

    confirmed = Confirm.ask("\n[bold yellow]Proceed with organizing?[/bold yellow]", default=True)
    if not confirmed:
        console.print("[yellow]Cancelled.[/yellow]")
        return

    summary = organize_files(source, target)
    if summary:
        console.print()
        _display_summary(summary, source)
