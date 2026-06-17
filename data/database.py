import sqlite3
import os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), "tracker.db")

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE TABLE IF NOT EXISTS food_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_date TEXT NOT NULL,
                meal_type TEXT NOT NULL,
                cut TEXT NOT NULL,
                form TEXT NOT NULL,
                weight_g INTEGER NOT NULL,
                calories REAL NOT NULL,
                protein REAL NOT NULL,
                fat REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS weight_log (
                log_date TEXT PRIMARY KEY,
                weight_kg REAL NOT NULL
            );
        """)

def save_setting(key: str, value: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )

def get_setting(key: str, default: str = "") -> str:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT value FROM settings WHERE key=?", (key,)
        ).fetchone()
    return row[0] if row else default

def add_food_log(log_date: str, meal_type: str, cut: str, form: str,
                 weight_g: int, calories: float, protein: float, fat: float):
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO food_log
               (log_date, meal_type, cut, form, weight_g, calories, protein, fat)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (log_date, meal_type, cut, form, weight_g, calories, protein, fat)
        )

def get_food_logs(log_date: str) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM food_log WHERE log_date=? ORDER BY id",
            (log_date,)
        ).fetchall()
    return rows

def delete_food_log(log_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM food_log WHERE id=?", (log_id,))

def get_daily_totals(log_date: str) -> dict:
    with get_conn() as conn:
        row = conn.execute(
            """SELECT COALESCE(SUM(calories),0),
                      COALESCE(SUM(protein),0),
                      COALESCE(SUM(fat),0),
                      COALESCE(SUM(weight_g),0)
               FROM food_log WHERE log_date=?""",
            (log_date,)
        ).fetchone()
    return {"칼로리": row[0], "단백질": row[1], "지방": row[2], "소고기_g": row[3]}

def save_weight(log_date: str, weight_kg: float):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO weight_log (log_date, weight_kg) VALUES (?, ?)",
            (log_date, weight_kg)
        )

def get_weight_history(days: int = 30) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT log_date, weight_kg FROM weight_log ORDER BY log_date DESC LIMIT ?",
            (days,)
        ).fetchall()
    return list(reversed(rows))

def get_weekly_summary(start_date: str, end_date: str) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT log_date,
                      SUM(calories), SUM(protein), SUM(fat), SUM(weight_g)
               FROM food_log
               WHERE log_date BETWEEN ? AND ?
               GROUP BY log_date ORDER BY log_date""",
            (start_date, end_date)
        ).fetchall()
    return rows
