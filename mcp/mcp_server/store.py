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
    # Phase 4: Tool Expansion tables
    conn.execute("""
        CREATE TABLE IF NOT EXISTS timebox_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            step_id TEXT NOT NULL,
            max_minutes INTEGER NOT NULL,
            risk_level TEXT NOT NULL,
            started_at TEXT NOT NULL,
            checked_at TEXT,
            elapsed_minutes REAL,
            exceeded INTEGER,
            status TEXT NOT NULL DEFAULT 'ACTIVE'
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS coverage_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coverage_percent REAL,
            threshold REAL,
            accepted INTEGER NOT NULL,
            checked_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS freeze_check_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            frozen_count INTEGER,
            changed_count INTEGER,
            violated_files_json TEXT,
            accepted INTEGER NOT NULL,
            checked_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS snapshot_check_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_path TEXT NOT NULL,
            total_fields INTEGER,
            found_fields INTEGER,
            missing_fields_json TEXT,
            accepted INTEGER NOT NULL,
            checked_at TEXT NOT NULL
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


# ── Phase 4: Tool Expansion (时间盒 / 覆盖率 / 冻结检测 / 快照校验) ──


def log_timebox_start(step_id: str, max_minutes: int, risk_level: str) -> int:
    """记录一次时间盒启动，返回 timer_id。"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.execute(
        "INSERT INTO timebox_log (step_id, max_minutes, risk_level, started_at, status) VALUES (?, ?, ?, ?, 'ACTIVE')",
        (step_id, max_minutes, risk_level, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    timer_id = cursor.lastrowid
    conn.close()
    return timer_id


def get_active_timebox(step_id: str) -> dict[str, object] | None:
    """查询指定 step_id 的活跃时间盒。返回 None 如果不存在或已结束。"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM timebox_log WHERE step_id=? AND status='ACTIVE' ORDER BY id DESC LIMIT 1",
        (step_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def log_timebox_check(timer_id: int, elapsed_minutes: float, exceeded: int) -> None:
    """记录一次时间盒检查结果。"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "UPDATE timebox_log SET checked_at=?, elapsed_minutes=?, exceeded=?, status='CHECKED' WHERE id=?",
        (datetime.now(timezone.utc).isoformat(), elapsed_minutes, exceeded, timer_id),
    )
    conn.commit()
    conn.close()


def log_coverage(coverage_percent: float, threshold: float, accepted: bool) -> None:
    """记录一次覆盖率检查。"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "INSERT INTO coverage_log (coverage_percent, threshold, accepted, checked_at) VALUES (?, ?, ?, ?)",
        (coverage_percent, threshold, int(accepted), datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def log_freeze_check(frozen_count: int, changed_count: int, violated_files: list[str], accepted: bool) -> None:
    """记录一次冻结文件检查。"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "INSERT INTO freeze_check_log (frozen_count, changed_count, violated_files_json, accepted, checked_at) VALUES (?, ?, ?, ?, ?)",
        (frozen_count, changed_count, json.dumps(violated_files, ensure_ascii=False), int(accepted), datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def log_snapshot_check(snapshot_path: str, total_fields: int, found_fields: int, missing_fields: list[str], accepted: bool) -> None:
    """记录一次快照完整性检查。"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        "INSERT INTO snapshot_check_log (snapshot_path, total_fields, found_fields, missing_fields_json, accepted, checked_at) VALUES (?, ?, ?, ?, ?, ?)",
        (snapshot_path, total_fields, found_fields, json.dumps(missing_fields, ensure_ascii=False), int(accepted), datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()
