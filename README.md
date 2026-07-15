# Employee Attendance Recording System
Capstone Project 2 (IT-CPSTONE40/IT-CPSTONE42) — Python + SQLite

## What's inside
- `db.py` — creates `Attendance.db` (SQLite) with the `Departments`,
  `Employees`, and `Attendance` tables from the spec sheet's data
  dictionary, plus optional sample data matching the sheet.
- `main.py` — the console MENU / index page. Run this file.

## Requirements
- Python 3.8+ (sqlite3 is built into Python, no extra installs needed)

## How to run in VS Code
1. Open this folder (`attendance_system`) in VS Code: `File > Open Folder...`
2. Open a terminal in VS Code: `Terminal > New Terminal`
3. Run:
   ```
   python main.py
   ```
   (use `python3 main.py` on macOS/Linux if `python` isn't mapped)
4. A file called `Attendance.db` will be created automatically in the same
   folder on first run — that's your SQLite database. You can inspect it
   with the "SQLite Viewer" extension in VS Code, or with the `sqlite3`
   CLI / DB Browser for SQLite.

## Modules (matches the spec sheet)
1. **Departments Management** — Add / Edit / Delete / list departments
2. **Employees Management** — Add / Edit / Delete / list employees
   (each tied to a department via `depCode`)
3. **Attendance Recording** — Time In, Time Out, and Cancel a record
4. **Attendance Monitoring**
   - By Employee: enter an Employee # to see all records, total hours
     worked, rate/hour, and computed salary
   - By Date Range: enter a From/To date to see all records in that
     range and the total hours

## Notes / things you may want to customize for submission
- `seed_sample_data()` in `main.py`'s `__main__` block pre-loads the exact
  sample rows shown on your spec sheet (departments 10–16, employees
  234–240) so the menus aren't empty on first run. Comment out that line
  if you want to start from a blank database, or delete `Attendance.db`
  and re-run to reset.
- Dates/times are entered as plain text in `YYYY-MM-DD` and
  `YYYY-MM-DD HH:MM` (24-hour) format — this keeps the code
  dependency-free. If you want native date pickers, this would need to
  become a GUI app (e.g. with `tkinter`), which is a natural next step if
  your requirements call for a graphical interface.
- "Cancelled" attendance records are excluded from the hour/salary totals
  in both monitoring modules.
- Deleting a Department that still has Employees, or an Employee that
  still has Attendance records, is blocked to protect referential
  integrity (mirrors the FK relationships in the data dictionary).
