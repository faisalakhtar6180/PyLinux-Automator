"""
disk_monitor.py — Disk Usage Monitor with visual bars and alerts.
"""

import psutil
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich import box
from modules.logger import log_action, log_error, log_section
from modules.settings import load_settings

console = Console()


def _fmt_bytes(b: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024:
            return f"{b:.2f} {unit}"
        b /= 1024
    return f"{b:.2f} PB"


def _bar(percent: float, width: int = 25) -> str:
    filled = int(width * percent / 100)
    bar = "█" * filled + "░" * (width - filled)
    if percent >= 90:
        color = "bold red"
    elif percent >= 75:
        color = "yellow"
    else:
        color = "green"
    return f"[{color}]{bar}[/{color}]  [bold]{percent:.1f}%[/bold]"


def check_disk_usage(warn_threshold: int = 85) -> list[dict]:
    """
    Return disk usage info for all partitions.
    Emits a warning for partitions above warn_threshold%.
    """
    log_section("Disk Usage Monitor")
    results = []

    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            info = {
                "mount": part.mountpoint,
                "device": part.device,
                "fstype": part.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent,
                "warning": usage.percent >= warn_threshold,
            }
            results.append(info)
            log_action(
                f"Disk {part.mountpoint}: {usage.percent:.1f}% used "
                f"({_fmt_bytes(usage.used)} / {_fmt_bytes(usage.total)})"
            )
            if info["warning"]:
                log_error(
                    f"⚠ Disk usage alert: {part.mountpoint} at {usage.percent:.1f}% "
                    f"(threshold {warn_threshold}%)"
                )
        except PermissionError:
            continue
        except Exception as exc:
            log_error(f"Error reading partition {part.mountpoint}: {exc}")

    return results


def display_disk_monitor(warn_threshold: int = 85) -> None:
    """Render disk usage dashboard."""
    disks = check_disk_usage(warn_threshold)

    if not disks:
        console.print("[red]Could not retrieve disk information.[/red]")
        return

    table = Table(
        title=f"💾 Disk Usage Monitor  (⚠ threshold: {warn_threshold}%)",
        box=box.ROUNDED,
        border_style="bright_cyan",
        show_lines=True,
        expand=True,
    )
    table.add_column("Mount Point", style="bold white", min_width=12)
    table.add_column("Device", style="dim")
    table.add_column("FS", style="dim", justify="center")
    table.add_column("Total", style="cyan", justify="right")
    table.add_column("Used", style="yellow", justify="right")
    table.add_column("Free", style="green", justify="right")
    table.add_column("Usage", min_width=32)

    any_warning = False
    for d in disks:
        warn_mark = " [bold red]⚠[/bold red]" if d["warning"] else ""
        table.add_row(
            d["mount"] + warn_mark,
            d["device"],
            d["fstype"],
            _fmt_bytes(d["total"]),
            _fmt_bytes(d["used"]),
            _fmt_bytes(d["free"]),
            _bar(d["percent"]),
        )
        if d["warning"]:
            any_warning = True

    console.print(table)

    if any_warning:
        console.print(Panel(
            f"[bold red]⚠  WARNING:[/bold red] One or more partitions exceed [bold]{warn_threshold}%[/bold] usage!\n"
            "Consider cleaning up files or expanding storage.",
            border_style="red",
        ))
    else:
        console.print(Panel(
            "[bold green]✓ All partitions are within safe usage limits.[/bold green]",
            border_style="green",
        ))


def disk_monitor_menu() -> None:
    """Interactive menu for disk monitor."""
    settings = load_settings()
    threshold = settings.get("disk_warn_threshold", 85)

    console.print(Panel("[bold cyan]💾 Disk Usage Monitor[/bold cyan]", border_style="cyan"))
    console.print(f"[dim]Current warning threshold: {threshold}%[/dim]\n")

    console.print("[1] View disk usage (current threshold)")
    console.print("[2] View disk usage (custom threshold)")
    console.print("[0] Back")
    console.print()

    choice = Prompt.ask("[bold green]Select option[/bold green]", default="1")

    if choice == "1":
        display_disk_monitor(threshold)
    elif choice == "2":
        custom = IntPrompt.ask("Enter warning threshold %", default=threshold)
        display_disk_monitor(custom)
    elif choice == "0":
        return
    else:
        console.print("[red]Invalid option.[/red]")
