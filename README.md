# PyLinux Automator 🐧

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python" />
  <img src="https://img.shields.io/badge/Platform-Linux-green?style=for-the-badge&logo=linux" />
  <img src="https://img.shields.io/badge/CLI-Rich-purple?style=for-the-badge" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" />
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge" />
</p>

> **A complete Linux automation toolkit** — organize files, backup data, monitor disk usage, clean your system, detect duplicates, and view a live system dashboard — all from a beautiful, beginner-friendly terminal interface.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [Screenshots](#-screenshots)
- [Skills Demonstrated](#-skills-demonstrated)
- [Future Improvements](#-future-improvements)
- [GitHub Upload Guide](#-upload-to-github)
- [License](#-license)

---

## 🔍 Overview

**PyLinux Automator** is a modular, resume-worthy Python project designed for B.Tech IT students targeting internships in **Python Development**, **DevOps**, **Linux System Administration**, and **Cybersecurity**.

It demonstrates real-world skills:
- **Object-Oriented Programming** and modular architecture
- **CLI development** with the Rich library
- **File system automation** using `pathlib`, `shutil`, `os`
- **System monitoring** using `psutil`
- **Concurrent programming** with `ThreadPoolExecutor`
- **Scheduling** with the `schedule` library
- **Data persistence** with JSON config and backup history logs

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

---

## 📸 Screenshots

> _Screenshots section — add your own terminal captures here._

| Feature | Screenshot |
|---------|-----------|
| Main Menu | _(add screenshot)_ |
| File Organizer | _(add screenshot)_ |
| System Dashboard | _(add screenshot)_ |
| Disk Monitor | _(add screenshot)_ |
| Duplicate Finder | _(add screenshot)_ |

**Tip — capture screenshots:**
```bash
# Record a terminal session as a gif:
sudo apt install asciinema
asciinema rec demo.cast
# Replay:
asciinema play demo.cast
```

---

## 🧠 Skills Demonstrated

| Category | Skills |
|----------|--------|
| **Python** | OOP, modules, generators, decorators, type hints, context managers |
| **CLI** | Rich library, progress bars, panels, tables, interactive prompts |
| **Linux** | File system operations, process management, system calls |
| **DevOps** | Backup automation, scheduling, disk monitoring, logging |
| **Security** | Safe file deletion, permission handling, input validation |
| **Concurrency** | `ThreadPoolExecutor` for fast parallel file hashing |
| **Data** | JSON config management, structured logging, history tracking |

---

## 🔮 Future Improvements

- [ ] **SQLite database** for richer backup and action history queries
- [ ] **Email/Telegram alerts** when disk usage exceeds threshold
- [ ] **Export reports** to CSV / PDF
- [ ] **SSH remote backup** support
- [ ] **Systemd service** integration for background scheduling
- [ ] **TUI mode** (Textual library) for full keyboard-driven UI
- [ ] **Plugin system** for community-contributed automation modules
- [ ] **Docker container** for portable deployment
- [ ] **Unit tests** with `pytest`
- [ ] **GitHub Actions CI** pipeline

---

## 📤 Upload to GitHub

### Step-by-step for a professional portfolio repo

```bash
# 1. Create a new repo on github.com (name: PyLinux-Automator)

# 2. Inside the project directory:
git init
git add .
git commit -m "feat: initial release — PyLinux Automator v1.0.0"

# 3. Add remote and push
git remote add origin https://github.com/<your-username>/PyLinux-Automator.git
git branch -M main
git push -u origin main
```

### Recommended repo settings
- ✅ Add a **description**: "A modular Linux automation toolkit built with Python & Rich"
- ✅ Add **topics/tags**: `python`, `linux`, `cli`, `automation`, `devops`, `rich`, `psutil`, `kali-linux`
- ✅ Enable **Issues** and **Discussions**
- ✅ Add a `LICENSE` file (MIT)
- ✅ Pin this repo on your GitHub profile

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Made with ❤️ using Python 🐍 | Built for Linux 🐧 | Designed for learners 🎓
</p>
