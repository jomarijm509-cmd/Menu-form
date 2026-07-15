
import sqlite3
import os

DB_NAME = "Attendance.db"
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), DB_NAME)


def get_connection():
    """Return a connection with foreign keys enforced and Row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables if they do not already exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Departments (
            depCode   INTEGER PRIMARY KEY,
            depName   TEXT NOT NULL,
            depHead   TEXT,
            depTelNo  TEXT
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Employees (
            empID     INTEGER PRIMARY KEY,
            depCode   INTEGER NOT NULL,
            empFName  TEXT NOT NULL,
            empLName  TEXT NOT NULL,
            empRPH    REAL NOT NULL,
            FOREIGN KEY (depCode) REFERENCES Departments(depCode)
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS Attendance (
            attRN      INTEGER PRIMARY KEY AUTOINCREMENT,
            empID      INTEGER NOT NULL,
            attDate    TEXT NOT NULL,
            attTimeIn  TEXT NOT NULL,
            attTimeOut TEXT,
            attStat    TEXT NOT NULL DEFAULT 'Not Cancelled',
            FOREIGN KEY (empID) REFERENCES Employees(empID)
        );
    """)

    conn.commit()
    conn.close()


def seed_sample_data():
    """Optional: populate the tables with the sample data shown on the
    spec sheet, only if the tables are currently empty. Handy for demoing
    the system without typing everything in by hand."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM Departments;")
    if cur.fetchone()[0] == 0:
        departments = [
            (10, "Accounting", "Julius Caesar", "2557777"),
            (11, "Warehouse", "Gretchen", "2551111"),
            (12, "HR", "Gretchen", "2552222"),
            (13, "IT", "Gilbert", "2553333"),
            (14, "Production", "Troy", "2554444"),
            (15, "QA", "Evangeline", "2550000"),
            (16, "Marketing", "Jessica", "2558888"),
        ]
        cur.executemany(
            "INSERT INTO Departments (depCode, depName, depHead, depTelNo) VALUES (?,?,?,?);",
            departments,
        )

    cur.execute("SELECT COUNT(*) FROM Employees;")
    if cur.fetchone()[0] == 0:
        employees = [
            (234, 10, "Neil", "Basabe", 500.00),
            (235, 10, "Heubert", "Ferolino", 300.00),
            (236, 11, "Denis", "Durano", 200.00),
            (237, 13, "Jennifer", "Amores", 500.00),
            (238, 15, "Catherine", "Carumba", 350.00),
            (239, 15, "Leah", "Ybanez", 345.00),
            (240, 14, "Leo", "Bermudez", 290.00),
        ]
        cur.executemany(
            "INSERT INTO Employees (empID, depCode, empFName, empLName, empRPH) VALUES (?,?,?,?,?);",
            employees,
        )

    conn.commit()
    conn.close()
