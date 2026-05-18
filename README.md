# PyLinux Automator 🐧

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Platform-Linux-green?style=for-the-badge&logo=linux" />
  <img src="https://img.shields.io/badge/CLI-Rich-purple?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge" />
</p>

> **A complete Linux automation toolkit** — organize files, backup data, monitor disk usage, clean your system, detect duplicates, and view a live system dashboard — all from a  beginner-friendly terminal interface.

---
## ✨ Features

| # | Feature | Description |
|---|---------|-------------|
| 1 | 📁 **File Organizer** | Auto-sort files into Documents, Images, Videos, Music, Archives, Code, Others |
| 2 | 🗄 **Backup System** | Compressed ZIP backups with timestamps, restore, history log, and scheduler |
| 3 | 💾 **Disk Monitor** | Visual disk usage bars with configurable warning thresholds |
| 4 | 🧹 **System Cleaner** | Safe preview + delete of temp files and empty directories |
| 5 | 🔁 **Duplicate Finder** | MD5-hash-based duplicate detection with multi-threaded scanning |
| 6 | 🖥 **System Dashboard** | Live CPU, RAM, disk, uptime, network, top processes panel |
| 7 | ⚙ **Settings** | JSON config: paths, thresholds, schedule time, cleanup extensions |
| 8 | 📝 **Logging** | Separate action and error logs with timestamps in `logs/` |

---

## 📁 Project Structure

```
PyLinux Automator/
├── main.py                    # Entry point — ASCII banner, menu loop
├── requirements.txt           # Python dependencies
├── README.md                  # You are here
│
├── modules/                   # Feature modules
│   ├── __init__.py
│   ├── file_organizer.py      # File categorization & moving
│   ├── backup_system.py       # ZIP backup, restore, scheduler
│   ├── disk_monitor.py        # Disk usage bars & alerts
│   ├── system_cleaner.py      # Temp file & empty dir cleanup
│   ├── duplicate_finder.py    # MD5 duplicate detection
│   ├── system_info.py         # psutil system dashboard
│   ├── settings.py            # Config load/save/display
│   └── logger.py              # Centralized action & error logging
│
├── config/
│   └── settings.json          # User preferences & defaults
│
├── logs/                      # Auto-generated log files
│   ├── actions.log
│   └── errors.log
│
└── backups/                   # ZIP backup archives
    └── backup_history.json    # Backup history (auto-generated)
```

---

## 🛠 Tech Stack

| Tool / Library | Purpose |
|----------------|---------|
| `Python 3.10+` | Core language |
| `rich` | Beautiful terminal UI (tables, progress bars, panels) |
| `psutil` | System metrics (CPU, RAM, disk, processes) |
| `schedule` | Cron-like task scheduling in Python |
| `pathlib` | Modern file path handling |
| `shutil` | File copying, moving, zipping |
| `zipfile` | ZIP archive creation and extraction |
| `hashlib` | MD5 hashing for duplicate detection |
| `concurrent.futures` | Multi-threaded file scanning |
| `logging` | Built-in structured logging |
| `json` | Settings and history persistence |

---

## ⚡ Installation

### Prerequisites

- **Linux** (Kali, Ubuntu, Debian, Fedora, Arch — any modern distro)
- **Python 3.10+**

```bash
python3 --version    # Must be 3.10 or higher
```

### Step 1 — Clone the Repository

```bash
git clone https://github.com/<your-username>/PyLinux-Automator.git
cd "PyLinux Automator"
```

### Step 2 — Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Run the Application

```bash
python3 main.py
```

---

## 🚀 Usage

After launching, you'll see the ASCII banner and the main menu:

```
┌──────────────────────────────────────────────────────────────┐
│   #   │ Feature                │ Description                 │
├───────┼────────────────────────┼─────────────────────────────┤
│   1   │ 📁 Organize Files      │ Auto-sort files…            │
│   2   │ 🗄 Backup Files        │ Compressed ZIP backups…     │
│   3   │ 💾 Monitor Disk Usage  │ Visual disk bars…           │
│   4   │ 🧹 Clean System        │ Remove temp files…          │
│   5   │ 🔁 Find Duplicates     │ MD5 duplicate detection…    │
│   6   │ 🖥 System Information  │ Full system dashboard…      │
│   7   │ ⚙ Settings            │ Configure paths…            │
│   8   │ 🚪 Exit                │ Quit PyLinux Automator      │
└───────┴────────────────────────┴─────────────────────────────┘

  Enter your choice:
```

### Quick Examples

**Organize your Downloads folder:**
```
Choice: 1
Source directory: ~/Downloads
Proceed? yes
```

**Create a backup:**
```
Choice: 2 → 1
Directory to backup: ~/Documents
```

**Check disk usage:**
```
Choice: 3 → 1
# Shows visual bars for all mounted partitions
```

**Find & delete duplicates in a folder:**
```
Choice: 5
Directory: ~/Pictures
# Scans with multi-threading, shows duplicate groups
```


<p align="center">
  Made with ❤️ using Python 🐍 | Built for Linux 🐧 
</p>
