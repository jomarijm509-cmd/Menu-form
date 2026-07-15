
from datetime import datetime
import sqlite3
import sys

from db import init_db, seed_sample_data, get_connection

DATE_FMT = "%Y-%m-%d"
DATETIME_FMT = "%Y-%m-%d %H:%M"



def pause():
    input("\nPress Enter to continue...")


def clear_header(title):
    print("\n" + "=" * 70)
    print(title.center(70))
    print("=" * 70)


def read_int(prompt):
    while True:
        raw = input(prompt).strip()
        if raw.isdigit():
            return int(raw)
        print("  Please enter a valid whole number.")


def read_float(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            return float(raw)
        except ValueError:
            print("  Please enter a valid number.")


def read_nonempty(prompt):
    while True:
        raw = input(prompt).strip()
        if raw:
            return raw
        print("  This field cannot be blank.")


def read_date(prompt, fmt=DATE_FMT, example="2024-04-15"):
    while True:
        raw = input(f"{prompt} (format YYYY-MM-DD, e.g. {example}): ").strip()
        try:
            datetime.strptime(raw, fmt)
            return raw
        except ValueError:
            print("  Invalid date format, try again.")


def read_datetime(prompt):
    while True:
        raw = input(f"{prompt} (format YYYY-MM-DD HH:MM, 24hr): ").strip()
        try:
            datetime.strptime(raw, DATETIME_FMT)
            return raw
        except ValueError:
            print("  Invalid date/time format, try again.")


def print_table(headers, rows):
    if not rows:
        print("\n  (no records found)\n")
        return
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    line = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print("\n  " + line)
    print("  " + "-" * len(line))
    for row in rows:
        print("  " + " | ".join(str(c).ljust(widths[i]) for i, c in enumerate(row)))
    print()



def list_departments():
    conn = get_connection()
    rows = conn.execute(
        "SELECT depCode, depName, depHead, depTelNo FROM Departments ORDER BY depCode;"
    ).fetchall()
    conn.close()
    print_table(["Code", "Name", "Head", "Tel. No."], [tuple(r) for r in rows])


def add_department():
    clear_header("Add a Department")
    depCode = read_int("Department Code: ")
    depName = read_nonempty("Department Name: ")
    depHead = read_nonempty("Department Head: ")
    depTelNo = read_nonempty("Telephone No.: ")

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO Departments (depCode, depName, depHead, depTelNo) VALUES (?,?,?,?);",
            (depCode, depName, depHead, depTelNo),
        )
        conn.commit()
        print("\n  Department added successfully.")
    except sqlite3.IntegrityError:
        print(f"\n  ERROR: Department code {depCode} already exists.")
    finally:
        conn.close()


def edit_department():
    clear_header("Edit a Department")
    depCode = read_int("Enter Department Code to edit: ")
    conn = get_connection()
    row = conn.execute("SELECT * FROM Departments WHERE depCode=?;", (depCode,)).fetchone()
    if not row:
        print("\n  Department not found.")
        conn.close()
        return

    print(f"  Leave a field blank to keep its current value.")
    depName = input(f"Department Name [{row['depName']}]: ").strip() or row["depName"]
    depHead = input(f"Department Head [{row['depHead']}]: ").strip() or row["depHead"]
    depTelNo = input(f"Telephone No. [{row['depTelNo']}]: ").strip() or row["depTelNo"]

    conn.execute(
        "UPDATE Departments SET depName=?, depHead=?, depTelNo=? WHERE depCode=?;",
        (depName, depHead, depTelNo, depCode),
    )
    conn.commit()
    conn.close()
    print("\n  Department updated successfully.")


def delete_department():
    clear_header("Delete a Department")
    depCode = read_int("Enter Department Code to delete: ")
    conn = get_connection()
    in_use = conn.execute(
        "SELECT COUNT(*) FROM Employees WHERE depCode=?;", (depCode,)
    ).fetchone()[0]
    if in_use > 0:
        print(f"\n  Cannot delete: {in_use} employee(s) still belong to this department.")
        conn.close()
        return
    cur = conn.execute("DELETE FROM Departments WHERE depCode=?;", (depCode,))
    conn.commit()
    conn.close()
    print("\n  Department deleted." if cur.rowcount else "\n  Department not found.")


def departments_menu():
    while True:
        clear_header("Departments Management")
        list_departments()
        print("  [A] Add a Department   [E] Edit   [D] Delete   [B] Back to Menu")
        choice = input("  Choose: ").strip().lower()
        if choice == "a":
            add_department()
        elif choice == "e":
            edit_department()
        elif choice == "d":
            delete_department()
        elif choice == "b":
            return
        else:
            print("  Invalid choice.")
        pause()



def list_employees():
    conn = get_connection()
    rows = conn.execute(
        """SELECT empID, depCode, empLName, empFName, empRPH
           FROM Employees ORDER BY empID;"""
    ).fetchall()
    conn.close()
    print_table(
        ["ID", "Dept.", "Lastname", "Firstname", "Rate/Hour"],
        [(r["empID"], r["depCode"], r["empLName"], r["empFName"], f"{r['empRPH']:.2f}") for r in rows],
    )


def department_exists(depCode):
    conn = get_connection()
    ok = conn.execute("SELECT 1 FROM Departments WHERE depCode=?;", (depCode,)).fetchone()
    conn.close()
    return ok is not None


def add_employee():
    clear_header("Add an Employee")
    empID = read_int("Employee ID: ")
    depCode = read_int("Department Code: ")
    if not department_exists(depCode):
        print(f"\n  ERROR: Department code {depCode} does not exist. Add it first.")
        return
    empFName = read_nonempty("First Name: ")
    empLName = read_nonempty("Last Name: ")
    empRPH = read_float("Rate Per Hour: ")

    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO Employees (empID, depCode, empFName, empLName, empRPH) VALUES (?,?,?,?,?);",
            (empID, depCode, empFName, empLName, empRPH),
        )
        conn.commit()
        print("\n  Employee added successfully.")
    except sqlite3.IntegrityError:
        print(f"\n  ERROR: Employee ID {empID} already exists.")
    finally:
        conn.close()


def edit_employee():
    clear_header("Edit an Employee")
    empID = read_int("Enter Employee ID to edit: ")
    conn = get_connection()
    row = conn.execute("SELECT * FROM Employees WHERE empID=?;", (empID,)).fetchone()
    if not row:
        print("\n  Employee not found.")
        conn.close()
        return

    print("  Leave a field blank to keep its current value.")
    depCode_raw = input(f"Department Code [{row['depCode']}]: ").strip()
    depCode = int(depCode_raw) if depCode_raw else row["depCode"]
    if not department_exists(depCode):
        print(f"\n  ERROR: Department code {depCode} does not exist.")
        conn.close()
        return
    empFName = input(f"First Name [{row['empFName']}]: ").strip() or row["empFName"]
    empLName = input(f"Last Name [{row['empLName']}]: ").strip() or row["empLName"]
    rph_raw = input(f"Rate Per Hour [{row['empRPH']:.2f}]: ").strip()
    empRPH = float(rph_raw) if rph_raw else row["empRPH"]

    conn.execute(
        "UPDATE Employees SET depCode=?, empFName=?, empLName=?, empRPH=? WHERE empID=?;",
        (depCode, empFName, empLName, empRPH, empID),
    )
    conn.commit()
    conn.close()
    print("\n  Employee updated successfully.")


def delete_employee():
    clear_header("Delete an Employee")
    empID = read_int("Enter Employee ID to delete: ")
    conn = get_connection()
    in_use = conn.execute(
        "SELECT COUNT(*) FROM Attendance WHERE empID=?;", (empID,)
    ).fetchone()[0]
    if in_use > 0:
        print(f"\n  Cannot delete: {in_use} attendance record(s) exist for this employee.")
        conn.close()
        return
    cur = conn.execute("DELETE FROM Employees WHERE empID=?;", (empID,))
    conn.commit()
    conn.close()
    print("\n  Employee deleted." if cur.rowcount else "\n  Employee not found.")


def employees_menu():
    while True:
        clear_header("Employees Management")
        list_employees()
        print("  [A] Add an Employee   [E] Edit   [D] Delete   [B] Back to Menu")
        choice = input("  Choose: ").strip().lower()
        if choice == "a":
            add_employee()
        elif choice == "e":
            edit_employee()
        elif choice == "d":
            delete_employee()
        elif choice == "b":
            return
        else:
            print("  Invalid choice.")
        pause()



def employee_exists(empID):
    conn = get_connection()
    ok = conn.execute("SELECT 1 FROM Employees WHERE empID=?;", (empID,)).fetchone()
    conn.close()
    return ok is not None


def list_attendance():
    conn = get_connection()
    rows = conn.execute(
        """SELECT attRN, empID, attDate, attTimeIn, attTimeOut, attStat
           FROM Attendance ORDER BY attRN;"""
    ).fetchall()
    conn.close()
    print_table(
        ["Record#", "Emp.ID", "Date", "Time In", "Time Out", "Status"],
        [(r["attRN"], r["empID"], r["attDate"], r["attTimeIn"], r["attTimeOut"] or "-", r["attStat"]) for r in rows],
    )


def record_time_in():
    clear_header("Record Attendance - Time In")
    empID = read_int("Employee ID: ")
    if not employee_exists(empID):
        print(f"\n  ERROR: Employee {empID} does not exist.")
        return
    attDate = read_date("Attendance Date")
    attTimeIn = read_datetime("Time In")

    conn = get_connection()
    conn.execute(
        "INSERT INTO Attendance (empID, attDate, attTimeIn, attTimeOut, attStat) VALUES (?,?,?,?,?);",
        (empID, attDate, attTimeIn, None, "Not Cancelled"),
    )
    conn.commit()
    conn.close()
    print("\n  Time In recorded successfully.")


def record_time_out():
    clear_header("Record Attendance - Time Out")
    attRN = read_int("Record # to time out: ")
    attTimeOut = read_datetime("Time Out")

    conn = get_connection()
    cur = conn.execute(
        "UPDATE Attendance SET attTimeOut=? WHERE attRN=? AND attStat='Not Cancelled';",
        (attTimeOut, attRN),
    )
    conn.commit()
    conn.close()
    if cur.rowcount:
        print("\n  Time Out recorded successfully.")
    else:
        print("\n  Record not found or already cancelled.")


def cancel_attendance():
    clear_header("Cancel an Attendance Record")
    attRN = read_int("Record # to cancel: ")
    conn = get_connection()
    cur = conn.execute(
        "UPDATE Attendance SET attStat='Cancelled' WHERE attRN=?;", (attRN,)
    )
    conn.commit()
    conn.close()
    print("\n  Record cancelled." if cur.rowcount else "\n  Record not found.")


def attendance_recording_menu():
    while True:
        clear_header("Attendance Recording")
        list_attendance()
        print("  [I] Time In   [O] Time Out   [C] Cancel   [B] Back to Menu")
        choice = input("  Choose: ").strip().lower()
        if choice == "i":
            record_time_in()
        elif choice == "o":
            record_time_out()
        elif choice == "c":
            cancel_attendance()
        elif choice == "b":
            return
        else:
            print("  Invalid choice.")
        pause()



def compute_hours(time_in, time_out):
    """Return hours worked (float) between two 'YYYY-MM-DD HH:MM' strings."""
    if not time_in or not time_out:
        return 0.0
    t_in = datetime.strptime(time_in, DATETIME_FMT)
    t_out = datetime.strptime(time_out, DATETIME_FMT)
    delta = (t_out - t_in).total_seconds() / 3600.0
    return max(delta, 0.0)


def monitor_by_employee():
    clear_header("Attendance Monitoring (By Employee)")
    empID = read_int("Input Employee #: ")

    conn = get_connection()
    emp = conn.execute(
        """SELECT e.*, d.depName FROM Employees e
           JOIN Departments d ON e.depCode = d.depCode
           WHERE empID=?;""",
        (empID,),
    ).fetchone()
    if not emp:
        print("\n  Employee not found.")
        conn.close()
        return

    rows = conn.execute(
        """SELECT attRN, empID, attDate, attTimeIn, attTimeOut, attStat
           FROM Attendance WHERE empID=? AND attStat='Not Cancelled'
           ORDER BY attRN;""",
        (empID,),
    ).fetchall()
    conn.close()

    print(f"\n  Name: {emp['empLName']}, {emp['empFName']}      Department: {emp['depName']}")
    print_table(
        ["Record#", "Emp.ID", "Date/Time In", "Date/Time Out", "Total (hrs)"],
        [
            (r["attRN"], r["empID"], r["attTimeIn"], r["attTimeOut"] or "-",
             f"{compute_hours(r['attTimeIn'], r['attTimeOut']):.2f}")
            for r in rows
        ],
    )

    total_hours = sum(compute_hours(r["attTimeIn"], r["attTimeOut"]) for r in rows)
    salary = total_hours * emp["empRPH"]
    print(f"  Rate Per Hour: {emp['empRPH']:.2f}")
    print(f"  Total Hours Worked: {total_hours:.2f}")
    print(f"  Salary: {salary:,.2f}")
    print(f"  Date Generated: {datetime.now().strftime(DATE_FMT)}")


def monitor_by_date_range():
    clear_header("Attendance Monitoring (Date Range)")
    date_from = read_date("Date From")
    date_to = read_date("Date To")

    conn = get_connection()
    rows = conn.execute(
        """SELECT attRN, empID, attTimeIn, attTimeOut
           FROM Attendance
           WHERE attStat='Not Cancelled' AND attDate BETWEEN ? AND ?
           ORDER BY attRN;""",
        (date_from, date_to),
    ).fetchall()
    conn.close()

    print_table(
        ["Record#", "Emp.ID", "Date/Time In", "Date/Time Out", "Total (hrs)"],
        [
            (r["attRN"], r["empID"], r["attTimeIn"], r["attTimeOut"] or "-",
             f"{compute_hours(r['attTimeIn'], r['attTimeOut']):.2f}")
            for r in rows
        ],
    )
    total_hours = sum(compute_hours(r["attTimeIn"], r["attTimeOut"]) for r in rows)
    print(f"  Date Generated: {datetime.now().strftime(DATE_FMT)}")
    print(f"  Total: {total_hours:.2f}")


def attendance_monitoring_menu():
    while True:
        clear_header("Attendance Monitoring")
        print("  [E] By Employee   [D] By Date Range   [B] Back to Menu")
        choice = input("  Choose: ").strip().lower()
        if choice == "e":
            monitor_by_employee()
        elif choice == "d":
            monitor_by_date_range()
        elif choice == "b":
            return
        else:
            print("  Invalid choice.")
        pause()



def main_menu():
    while True:
        clear_header("Employee Attendance Recording System")
        print("  Choose your Transaction:\n")
        print("  1. Departments Management")
        print("  2. Employees Management")
        print("  3. Attendance Recording")
        print("  4. Attendance Monitoring")
        print("  0. Exit")
        choice = input("\n  Choose: ").strip()

        if choice == "1":
            departments_menu()
        elif choice == "2":
            employees_menu()
        elif choice == "3":
            attendance_recording_menu()
        elif choice == "4":
            attendance_monitoring_menu()
        elif choice == "0":
            print("\n  Goodbye!")
            sys.exit(0)
        else:
            print("  Invalid choice.")
            pause()


if __name__ == "__main__":
    init_db()
    seed_sample_data()   # comment this line out if you don't want sample data
    main_menu()
