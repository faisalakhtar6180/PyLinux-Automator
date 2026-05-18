"""
system_info.py — System Information Dashboard.

Displays CPU, RAM, Disk, Uptime, User, OS, and Network info
using psutil and Rich.
"""

import os
import platform
import socket
import time
from datetime import timedelta
from pathlib import Path

import psutil
from rich.console import Console
from rich.table import Table
from rich.columns import Columns
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich import box
from modules.logger import log_action, log_section

console = Console()


def _fmt_bytes(b: float) -> str:
    """Convert bytes to human-readable string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if b < 1024:
            return f"{b:.1f} {unit}"
        b /= 1024
    return f"{b:.1f} PB"


def _usage_bar(percent: float, width: int = 20) -> str:
    """Create a simple ASCII progress bar."""
    filled = int(width * percent / 100)
    bar = "█" * filled + "░" * (width - filled)
    color = "red" if percent >= 85 else "yellow" if percent >= 60 else "green"
    return f"[{color}]{bar}[/{color}] [bold]{percent:.1f}%[/bold]"


def get_cpu_info() -> dict:
    cpu_freq = psutil.cpu_freq()
    return {
        "Physical Cores": psutil.cpu_count(logical=False),
        "Logical Cores": psutil.cpu_count(logical=True),
        "CPU Usage": psutil.cpu_percent(interval=1),
        "Frequency (MHz)": f"{cpu_freq.current:.0f}" if cpu_freq else "N/A",
        "Max Frequency": f"{cpu_freq.max:.0f}" if cpu_freq else "N/A",
    }


def get_ram_info() -> dict:
    vm = psutil.virtual_memory()
    sw = psutil.swap_memory()
    return {
        "Total RAM": _fmt_bytes(vm.total),
        "Used RAM": _fmt_bytes(vm.used),
        "Available RAM": _fmt_bytes(vm.available),
        "RAM Usage %": vm.percent,
        "Swap Total": _fmt_bytes(sw.total),
        "Swap Used": _fmt_bytes(sw.used),
        "Swap Usage %": sw.percent,
    }


def get_disk_info() -> list[dict]:
    """Return info for all mounted disk partitions."""
    partitions = []
    for part in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(part.mountpoint)
            partitions.append({
                "Mount": part.mountpoint,
                "Device": part.device,
                "FS": part.fstype,
                "Total": _fmt_bytes(usage.total),
                "Used": _fmt_bytes(usage.used),
                "Free": _fmt_bytes(usage.free),
                "Usage %": usage.percent,
            })
        except PermissionError:
            continue
    return partitions


def get_system_info() -> dict:
    """Gather general system info."""
    boot_time = psutil.boot_time()
    uptime_secs = time.time() - boot_time
    uptime_str = str(timedelta(seconds=int(uptime_secs)))

    hostname = socket.gethostname()
    try:
        ip = socket.gethostbyname(hostname)
    except Exception:
        ip = "N/A"

    # Try to read distro info
    distro = "Unknown"
    try:
        import distro as _d
        distro = _d.name(pretty=True)
    except ImportError:
        if Path("/etc/os-release").exists():
            for line in Path("/etc/os-release").read_text().splitlines():
                if line.startswith("PRETTY_NAME="):
                    distro = line.split("=", 1)[1].strip().strip('"')
                    break

    return {
        "OS": platform.system(),
        "Distribution": distro,
        "Kernel": platform.release(),
        "Architecture": platform.machine(),
        "Hostname": hostname,
        "IP Address": ip,
        "Current User": os.getenv("USER", os.getenv("USERNAME", "unknown")),
        "Python Version": platform.python_version(),
        "Uptime": uptime_str,
    }


def display_system_dashboard() -> None:
    """Render the full System Information Dashboard."""
    log_section("System Information Dashboard")
    log_action("System info dashboard opened.")

    console.print(Panel(
        "[bold cyan]🖥  System Information Dashboard[/bold cyan]",
        border_style="bright_cyan",
        padding=(0, 2),
    ))

    # ── General Info ──────────────────────────────────────────────────────
    sys_info = get_system_info()
    sys_table = Table(title="🌐 System Overview", box=box.ROUNDED, border_style="blue", show_lines=True)
    sys_table.add_column("Property", style="bold yellow", min_width=20)
    sys_table.add_column("Value", style="white")
    for k, v in sys_info.items():
        sys_table.add_row(k, str(v))
    console.print(sys_table)

    # ── CPU ──────────────────────────────────────────────────────────────
    cpu = get_cpu_info()
    cpu_table = Table(title="⚡ CPU", box=box.ROUNDED, border_style="yellow", show_lines=True)
    cpu_table.add_column("Property", style="bold yellow", min_width=20)
    cpu_table.add_column("Value / Usage", style="white")
    for k, v in cpu.items():
        if k == "CPU Usage":
            cpu_table.add_row(k, _usage_bar(v))
        else:
            cpu_table.add_row(k, str(v))
    console.print(cpu_table)

    # ── RAM ──────────────────────────────────────────────────────────────
    ram = get_ram_info()
    ram_table = Table(title="🧠 RAM & Swap", box=box.ROUNDED, border_style="magenta", show_lines=True)
    ram_table.add_column("Property", style="bold yellow", min_width=20)
    ram_table.add_column("Value / Usage", style="white")
    for k, v in ram.items():
        if "%" in k:
            ram_table.add_row(k, _usage_bar(v))
        else:
            ram_table.add_row(k, str(v))
    console.print(ram_table)

    # ── Disk ─────────────────────────────────────────────────────────────
    disk_table = Table(title="💾 Disk Partitions", box=box.ROUNDED, border_style="green", show_lines=True)
    disk_table.add_column("Mount", style="bold white")
    disk_table.add_column("FS", style="dim")
    disk_table.add_column("Total", style="cyan")
    disk_table.add_column("Used", style="yellow")
    disk_table.add_column("Free", style="green")
    disk_table.add_column("Usage", style="white", min_width=28)
    for d in get_disk_info():
        disk_table.add_row(
            d["Mount"], d["FS"], d["Total"], d["Used"], d["Free"],
            _usage_bar(d["Usage %"])
        )
    console.print(disk_table)

    # ── Running Processes (top 5 by CPU) ──────────────────────────────────
    proc_table = Table(title="🔧 Top 5 Processes (CPU)", box=box.ROUNDED, border_style="red", show_lines=True)
    proc_table.add_column("PID", style="dim", justify="right")
    proc_table.add_column("Name", style="bold white")
    proc_table.add_column("CPU %", style="yellow", justify="right")
    proc_table.add_column("RAM %", style="magenta", justify="right")
    procs = []
    for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            procs.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    procs.sort(key=lambda x: x.get("cpu_percent", 0) or 0, reverse=True)
    for p in procs[:5]:
        proc_table.add_row(
            str(p.get("pid", "?")),
            p.get("name", "?"),
            f"{p.get('cpu_percent', 0):.1f}",
            f"{p.get('memory_percent', 0):.1f}",
        )
    console.print(proc_table)
    console.print()
