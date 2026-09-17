import sqlite3
from datetime import datetime

DB_NAME = "feedback.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review TEXT NOT NULL,
            label TEXT NOT NULL,
            score INTEGER NOT NULL,
            theme TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            review TEXT NOT NULL,
            error TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_results(results: list[dict]):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT INTO feedback (review, label, score, theme) VALUES (?, ?, ?, ?)",
        [(r["review"], r["label"], r["score"], r["theme"]) for r in results],
    )
    conn.commit()
    conn.close()


def load_history() -> list[dict]:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, review, label, score, theme FROM feedback ORDER BY id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def log_error(review: str, error: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO audit_log (review, error, timestamp) VALUES (?, ?, ?)",
        (review, error, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def load_audit_log() -> list[dict]:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, review, error, timestamp FROM audit_log ORDER BY id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows
