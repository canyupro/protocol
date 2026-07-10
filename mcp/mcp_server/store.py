from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .models import MarkCheckedRequest, MarkCheckedResult, PauseRequest, ReportStepRequest

DB_PATH = Path(__file__).resolve().parent / "state.db"


def init_db() -> None:
    """初始化所有 SQLite 表。幂等。"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mark_checked_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id TEXT NOT NULL,
            evidence_url TEXT NOT NULL,
            evidence_type TEXT NOT NULL,
            accepted INTEGER NOT NULL,
            reason TEXT NOT NULL,
            checked_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pause_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            context TEXT NOT NULL,
            forks_json TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'PAUSED',
            choice TEXT,
            paused_at TEXT NOT NULL,
            resumed_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS step_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phase TEXT NOT NULL,
            content TEXT NOT NULL,
            artifacts_json TEXT NOT NULL,
            reported_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def log_call(req: MarkCheckedRequest, result: MarkCheckedResult) -> None:
    """记录一次 mark_checked 调用。"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "INSERT INTO mark_checked_log (item_id, evidence_url, evidence_type, accepted, reason, checked_at) VALUES (?, ?, ?, ?, ?, ?)",
        (req.item_id, req.evidence_url, req.evidence_type.value, int(result.accepted), result.reason, result.checked_at),
    )
    conn.commit()
    conn.close()


def get_history(item_id: str | None = None) -> list[dict[str, object]]:
    """查询调用历史。item_id 为 None 时返回全部。"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    if item_id:
        rows = conn.execute(
            "SELECT * FROM mark_checked_log WHERE item_id = ? ORDER BY id DESC", (item_id,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM mark_checked_log ORDER BY id DESC LIMIT 100").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Phase 2: pause_for_user / resume_from_pause ──────────────

def log_pause(req: PauseRequest) -> int:
    """记录一次暂停请求，返回 pause_id。"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.execute(
        "INSERT INTO pause_log (context, forks_json, status, paused_at) VALUES (?, ?, 'PAUSED', ?)",
        (req.context, json.dumps([f.model_dump() for f in req.forks], ensure_ascii=False),
         datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    pause_id = cursor.lastrowid
    conn.close()
    return pause_id


def log_resume(pause_id: int, choice: str) -> bool:
    """记录用户的选择，更新状态为 RESUMED。返回是否成功。"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.execute(
        "UPDATE pause_log SET status='RESUMED', choice=?, resumed_at=? WHERE id=? AND status='PAUSED'",
        (choice, datetime.now(timezone.utc).isoformat(), pause_id),
    )
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def get_pause(pause_id: int) -> dict[str, object] | None:
    """查询单条暂停记录。"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM pause_log WHERE id=?", (pause_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


# ── Phase 3: report_step ──────────────────────────────────────

def log_step(req: ReportStepRequest) -> int:
    """记录一次步骤报告，返回 step_seq。"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.execute(
        "INSERT INTO step_log (phase, content, artifacts_json, reported_at) VALUES (?, ?, ?, ?)",
        (req.phase.value, req.content,
         json.dumps(req.artifacts, ensure_ascii=False),
         datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    step_seq = cursor.lastrowid
    conn.close()
    return step_seq


def get_step(step_seq: int) -> dict[str, object] | None:
    """查询单条步骤记录。"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM step_log WHERE id=?", (step_seq,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_step_count() -> int:
    """查询步骤总数。"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.execute("SELECT COUNT(*) FROM step_log")
    count = cursor.fetchone()[0]
    conn.close()
    return count
