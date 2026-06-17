import sqlite3
import os
from datetime import date, timedelta

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

            CREATE TABLE IF NOT EXISTS challenge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                goal_protein INTEGER NOT NULL,
                is_active INTEGER DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS challenge_daily (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                challenge_id INTEGER NOT NULL,
                log_date TEXT NOT NULL,
                achieved INTEGER DEFAULT 0,
                UNIQUE(challenge_id, log_date)
            );

            CREATE TABLE IF NOT EXISTS shopping_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cut TEXT NOT NULL,
                form TEXT NOT NULL,
                quantity_g INTEGER NOT NULL,
                purchase_date TEXT NOT NULL,
                notes TEXT
            );
        """)

# ── settings ─────────────────────────────────────────────
def save_setting(key, value):
    with get_conn() as conn:
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))

def get_setting(key, default=""):
    with get_conn() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return row[0] if row else default

# ── food_log ─────────────────────────────────────────────
def add_food_log(log_date, meal_type, cut, form, weight_g, calories, protein, fat):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO food_log (log_date,meal_type,cut,form,weight_g,calories,protein,fat) VALUES (?,?,?,?,?,?,?,?)",
            (log_date, meal_type, cut, form, weight_g, calories, protein, fat)
        )

def get_food_logs(log_date):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM food_log WHERE log_date=? ORDER BY id", (log_date,)
        ).fetchall()

def delete_food_log(log_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM food_log WHERE id=?", (log_id,))

def get_daily_totals(log_date):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(calories),0), COALESCE(SUM(protein),0), COALESCE(SUM(fat),0), COALESCE(SUM(weight_g),0) FROM food_log WHERE log_date=?",
            (log_date,)
        ).fetchone()
    return {"칼로리": row[0], "단백질": row[1], "지방": row[2], "소고기_g": row[3]}

def get_monthly_logs(year, month):
    prefix = f"{year:04d}-{month:02d}"
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT log_date, SUM(calories), SUM(protein), SUM(fat), SUM(weight_g) FROM food_log WHERE log_date LIKE ? GROUP BY log_date",
            (f"{prefix}%",)
        ).fetchall()
    return rows

def get_weekly_summary(start_date, end_date):
    with get_conn() as conn:
        return conn.execute(
            "SELECT log_date, SUM(calories), SUM(protein), SUM(fat), SUM(weight_g) FROM food_log WHERE log_date BETWEEN ? AND ? GROUP BY log_date ORDER BY log_date",
            (start_date, end_date)
        ).fetchall()

def get_consumption_by_cut(weeks=4):
    start = (date.today() - timedelta(weeks=weeks)).isoformat()
    with get_conn() as conn:
        return conn.execute(
            "SELECT cut, form, SUM(weight_g) as total FROM food_log WHERE log_date >= ? GROUP BY cut, form ORDER BY total DESC",
            (start,)
        ).fetchall()

# ── weight_log ───────────────────────────────────────────
def save_weight(log_date, weight_kg):
    with get_conn() as conn:
        conn.execute("INSERT OR REPLACE INTO weight_log (log_date, weight_kg) VALUES (?, ?)", (log_date, weight_kg))

def get_weight_history(days=30):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT log_date, weight_kg FROM weight_log ORDER BY log_date DESC LIMIT ?", (days,)
        ).fetchall()
    return list(reversed(rows))

# ── challenge ────────────────────────────────────────────
def create_challenge(start_date, end_date, goal_protein):
    with get_conn() as conn:
        conn.execute("UPDATE challenge SET is_active=0")
        conn.execute(
            "INSERT INTO challenge (start_date, end_date, goal_protein, is_active) VALUES (?, ?, ?, 1)",
            (start_date, end_date, goal_protein)
        )

def get_active_challenge():
    with get_conn() as conn:
        return conn.execute(
            "SELECT id, start_date, end_date, goal_protein FROM challenge WHERE is_active=1 ORDER BY id DESC LIMIT 1"
        ).fetchone()

def get_challenge_days(challenge_id, start_date, end_date):
    with get_conn() as conn:
        return conn.execute(
            "SELECT log_date, achieved FROM challenge_daily WHERE challenge_id=? AND log_date BETWEEN ? AND ? ORDER BY log_date",
            (challenge_id, start_date, end_date)
        ).fetchall()

def sync_challenge_daily(challenge_id, goal_protein):
    ch = get_active_challenge()
    if not ch:
        return
    today = date.today().isoformat()
    start = ch[1]
    # 챌린지 시작일부터 오늘까지 달성 여부 동기화
    cur = date.fromisoformat(start)
    end = min(date.today(), date.fromisoformat(ch[2]))
    with get_conn() as conn:
        while cur <= end:
            d = cur.isoformat()
            row = conn.execute(
                "SELECT COALESCE(SUM(protein),0) FROM food_log WHERE log_date=?", (d,)
            ).fetchone()
            achieved = 1 if row[0] >= goal_protein else 0
            conn.execute(
                "INSERT OR REPLACE INTO challenge_daily (challenge_id, log_date, achieved) VALUES (?, ?, ?)",
                (challenge_id, d, achieved)
            )
            cur += timedelta(days=1)

# ── shopping ─────────────────────────────────────────────
def add_shopping_record(cut, form, quantity_g, purchase_date, notes=""):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO shopping_history (cut, form, quantity_g, purchase_date, notes) VALUES (?, ?, ?, ?, ?)",
            (cut, form, quantity_g, purchase_date, notes)
        )

def get_shopping_history(limit=20):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM shopping_history ORDER BY purchase_date DESC LIMIT ?", (limit,)
        ).fetchall()
