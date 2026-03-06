import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

DB_PATH = Path(__file__).parent / "db.sqlite"


def conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          role TEXT NOT NULL,
          username TEXT NOT NULL UNIQUE,
          password TEXT NOT NULL,
          full_name TEXT NOT NULL DEFAULT ''
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS attendance_sessions (
          id TEXT PRIMARY KEY,
          class_name TEXT NOT NULL,
          start_iso TEXT NOT NULL,
          end_iso TEXT NOT NULL,
          created_iso TEXT NOT NULL,
          token TEXT NOT NULL,
          center_lat REAL NOT NULL,
          center_lng REAL NOT NULL,
          radius_m REAL NOT NULL
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS attendance_marks (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          session_id TEXT NOT NULL,
          student_username TEXT NOT NULL,
          student_name TEXT NOT NULL,
          status TEXT NOT NULL,
          reason TEXT,
          marked_iso TEXT NOT NULL
        )
        """)

        c.execute("""
        CREATE TABLE IF NOT EXISTS safety_reports (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          student_username TEXT NOT NULL,
          title TEXT NOT NULL,
          details TEXT NOT NULL,
          lat REAL,
          lng REAL,
          created_iso TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'NEW'
        )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS od_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_username TEXT NOT NULL,
            student_name TEXT NOT NULL,
            college_name TEXT NOT NULL,
            event_type TEXT NOT NULL,
            event_name TEXT NOT NULL,
            event_date TEXT NOT NULL,
            parent_letter_path TEXT NOT NULL,
            clg_od_letter_path TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'PENDING',
            created_iso TEXT NOT NULL,
            reviewed_iso TEXT
            )
        """)

        seed_user(c, role="admin", username="admin", password="12345", full_name="Admin User")
        seed_user(c, role="student", username="student1", password="12345", full_name="Swathi Krishna")


def seed_user(c, role: str, username: str, password: str, full_name: str):
    row = c.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
    if row is None:
        c.execute(
            "INSERT INTO users(role, username, password, full_name) VALUES(?,?,?,?)",
            (role, username, password, full_name),
        )


def get_user(username: str) -> Optional[Dict[str, Any]]:
    with conn() as c:
        r = c.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        return dict(r) if r else None


def create_session(payload: Dict[str, Any]):
    with conn() as c:
        c.execute("""
          INSERT INTO attendance_sessions
          (id, class_name, start_iso, end_iso, created_iso, token, center_lat, center_lng, radius_m)
          VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            payload["id"], payload["class_name"], payload["start_iso"], payload["end_iso"],
            payload["created_iso"], payload["token"], payload["center_lat"], payload["center_lng"],
            payload["radius_m"],
        ))


def list_sessions() -> List[Dict[str, Any]]:
    with conn() as c:
        rows = c.execute("SELECT * FROM attendance_sessions ORDER BY created_iso DESC").fetchall()
        return [dict(r) for r in rows]


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    with conn() as c:
        r = c.execute("SELECT * FROM attendance_sessions WHERE id=?", (session_id,)).fetchone()
        return dict(r) if r else None


def mark_attendance(session_id: str, student_username: str, student_name: str, status: str, reason: str):
    with conn() as c:
        c.execute("""
          INSERT INTO attendance_marks(session_id, student_username, student_name, status, reason, marked_iso)
          VALUES (?,?,?,?,?,?)
        """, (
            session_id, student_username, student_name, status, reason, datetime.utcnow().isoformat()
        ))


def list_marks_for_student(student_username: str) -> List[Dict[str, Any]]:
    with conn() as c:
        rows = c.execute("""
          SELECT m.*, s.class_name
          FROM attendance_marks m
          JOIN attendance_sessions s ON s.id = m.session_id
          WHERE m.student_username=?
          ORDER BY m.marked_iso DESC
        """, (student_username,)).fetchall()
        return [dict(r) for r in rows]


def list_marks_for_session(session_id: str) -> List[Dict[str, Any]]:
    with conn() as c:
        rows = c.execute("""
          SELECT student_name, student_username, status, reason, marked_iso
          FROM attendance_marks
          WHERE session_id=?
          ORDER BY marked_iso DESC
        """, (session_id,)).fetchall()
        return [dict(r) for r in rows]


def create_report(payload: Dict[str, Any]):
    with conn() as c:
        c.execute("""
          INSERT INTO safety_reports(student_username, title, details, lat, lng, created_iso, status)
          VALUES(?,?,?,?,?,?,?)
        """, (
            payload["student_username"], payload["title"], payload["details"],
            payload.get("lat"), payload.get("lng"), payload["created_iso"], payload["status"]
        ))


def list_reports() -> List[Dict[str, Any]]:
    with conn() as c:
        rows = c.execute("SELECT * FROM safety_reports ORDER BY created_iso DESC").fetchall()
        return [dict(r) for r in rows]


# ---------------- OD ----------------

def create_od_request(payload: Dict[str, Any]):
    with conn() as c:
        c.execute("""
                INSERT INTO od_requests(
                 student_username,
                 student_name,
                 college_name,
                 event_type,
                 event_name,
                 event_date,
                 parent_letter_path,
                 clg_od_letter_path,
                 status,
                 created_iso,
                 reviewed_iso
                )
                VALUES(?,?,?,?,?,?,?,?,?,?,?)
                """,(
                 payload["student_username"],
                 payload["student_name"],
                 payload["college_name"],
                 payload["event_type"],
                 payload["event_name"],
                 payload["event_date"],
                                payload["parent_letter_path"],
                 payload["clg_od_letter_path"],
                 payload["status"],
                 payload["created_iso"],
                 payload.get("reviewed_iso")
        ))


def list_od_requests_for_student(student_username: str) -> List[Dict[str, Any]]:
    with conn() as c:
        rows = c.execute("""
          SELECT *
          FROM od_requests
          WHERE student_username=?
          ORDER BY created_iso DESC
        """, (student_username,)).fetchall()
        return [dict(r) for r in rows]


def list_od_requests() -> List[Dict[str, Any]]:
    with conn() as c:
        rows = c.execute("""
          SELECT *
          FROM od_requests
          ORDER BY created_iso DESC
        """).fetchall()
        return [dict(r) for r in rows]


def update_od_status(od_id: int, status: str):
    with conn() as c:
        c.execute("""
          UPDATE od_requests
          SET status=?, reviewed_iso=?
          WHERE id=?
        """, (status, datetime.utcnow().isoformat(), od_id))


def get_approved_od_for_student_on_date(student_username: str, event_date: str) -> Optional[Dict[str, Any]]:
    with conn() as c:
        row = c.execute("""
          SELECT *
          FROM od_requests
          WHERE student_username=?
            AND event_date=?
            AND status='APPROVED'
          ORDER BY created_iso DESC
          LIMIT 1
        """, (student_username, event_date)).fetchone()
        return dict(row) if row else None

def manual_mark_attendance(session_id: str, student_username: str, student_name: str, status: str, reason: str):
    with conn() as c:
        existing = c.execute("""
            SELECT id
            FROM attendance_marks
            WHERE session_id=? AND student_username=?
            ORDER BY id DESC
            LIMIT 1
        """, (session_id, student_username)).fetchone()

        now_iso = datetime.utcnow().isoformat()

        if existing:
            c.execute("""
                UPDATE attendance_marks
                SET student_name=?, status=?, reason=?, marked_iso=?
                WHERE id=?
            """, (
                student_name,
                status,
                reason,
                now_iso,
                existing["id"]
            ))
        else:
            c.execute("""
                INSERT INTO attendance_marks(session_id, student_username, student_name, status, reason, marked_iso)
                VALUES (?,?,?,?,?,?)
            """, (
                session_id,
                student_username,
                student_name,
                status,
                reason,
                now_iso
            ))