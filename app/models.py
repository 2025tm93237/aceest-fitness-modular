import sqlite3

from werkzeug.security import generate_password_hash

SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT UNIQUE NOT NULL,
    age INTEGER,
    gender TEXT,
    height_cm REAL,
    weight_kg REAL,
    target TEXT,
    membership_state TEXT DEFAULT 'active',
    joined_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS training_plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_name TEXT NOT NULL,
    plan_type TEXT NOT NULL,
    blueprint_text TEXT NOT NULL,
    generated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT UNIQUE NOT NULL,
    muscle_group TEXT,
    equipment TEXT
);
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_name TEXT NOT NULL,
    movement_title TEXT NOT NULL,
    session_date TEXT NOT NULL,
    minutes INTEGER DEFAULT 30,
    kcal_burned INTEGER DEFAULT 0,
    remarks TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS measurements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_name TEXT NOT NULL,
    logged_at TEXT NOT NULL,
    weight_kg REAL,
    body_fat_pct REAL,
    chest_cm REAL,
    waist_cm REAL,
    hip_cm REAL,
    remarks TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS targets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_name TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_value REAL,
    due_date TEXT,
    state TEXT DEFAULT 'active'
);
CREATE TABLE IF NOT EXISTS progress_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    member_name TEXT NOT NULL,
    logged_at TEXT NOT NULL,
    weight_kg REAL,
    remark TEXT DEFAULT ''
);
"""


def init_db(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    seed = [
        ("admin", generate_password_hash("admin123"), "admin"),
        ("trainer", generate_password_hash("trainer123"), "trainer"),
    ]
    for username, password_hash, role in seed:
        conn.execute(
            "INSERT OR IGNORE INTO accounts (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role),
        )
    conn.commit()
    conn.close()
