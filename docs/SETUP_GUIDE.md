# Setup & Installation Guide

This guide walks you through setting up, configuring, and executing the **Automated Business Performance Dashboard** on Windows (or macOS / Linux).

---

## 1. Prerequisites

- **Python 3.10+** (Python 3.11 recommended)
- **Git**
- **Power BI Desktop** (free download from Microsoft Store or official site)

---

## 2. Installation & Environment Setup

### Step 1: Open Terminal / PowerShell
Navigate to your preferred directory and clone the repository:

```bash
git clone https://github.com/SamruddhiHole/Automated-Business-Performance-Dashboard.git
cd Automated-Business-Performance-Dashboard
```

### Step 2: Create a Virtual Environment (Recommended)
```powershell
# Create virtual environment
python -m venv venv

# Activate on Windows PowerShell:
.\venv\Scripts\Activate.ps1

# (If script execution is disabled in PowerShell, run: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)
```

### Step 3: Install Required Dependencies
```powershell
pip install -r requirements.txt
```

---

## 3. Running the Automated Pipeline

### Single Command Run (Default)
Places all raw files inside `data/raw/` (e.g. `Online Retail.xlsx`) and executes:

```powershell
python python/automated_pipeline.py
```

### Available Command-Line Arguments:
| Argument | Description | Example |
|---|---|---|
| `--input <path>` | Process a specific file | `python python/automated_pipeline.py --input "data/raw/Online Retail.xlsx"` |
| `--all` | Process every dataset found in `data/raw/` | `python python/automated_pipeline.py --all` |
| `--force` | Force re-run even if already processed | `python python/automated_pipeline.py --force` |
| `--dry-run` | Run cleaning & validation without DB changes | `python python/automated_pipeline.py --dry-run` |

---

## 4. Running Automated Tests

Run the full pytest test suite (19 tests covering cleaning, validation, database transactions, idempotency, and reporting):

```powershell
pytest tests/ -v
```

All tests execute with isolated synthetic in-memory fixtures without modifying production databases.

---

## 5. Scheduling Daily Automation on Windows

### Option A: PowerShell Helper (Recommended)
Run the pre-configured scheduling script (schedules daily execution at 02:00 AM):

```powershell
.\scripts\schedule_task.ps1 -Time "02:00"
```

To test the scheduled task immediately:
```powershell
.\scripts\schedule_task.ps1 -RunNow
```

To remove the scheduled task:
```powershell
.\scripts\schedule_task.ps1 -Remove
```

### Option B: Windows Task Scheduler GUI
1. Press `Win + R`, type `taskschd.msc`, and press Enter.
2. Click **Create Basic Task...** in the right pane.
3. Set Name to `AutomatedRetailPipeline` and Trigger to **Daily**.
4. Set Action to **Start a program**.
5. Program/script: browse to your `python.exe` (or `scripts\run_pipeline_scheduled.bat`).
6. Arguments: `python/automated_pipeline.py`
7. Start in: `C:\path\to\Automated-Business-Performance-Dashboard`
8. Finish.
