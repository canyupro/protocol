from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timedelta, timezone

import pytest

from mcp_server.server import check_timebox, start_timebox
from mcp_server.store import DB_PATH, get_active_timebox, init_db

# ── 环境准备 ──────────────────────────────────────────────


@pytest.fixture(autouse=True)
def clean_state_db():
    """每个测试前清空 SQLite 状态文件。"""
    if DB_PATH.exists():
        os.remove(DB_PATH)
    init_db()
    yield
    if DB_PATH.exists():
        os.remove(DB_PATH)


# ── AC-1: 正常启动 → started=True, timer_id>0 ────────────

def test_start_timebox_normal():
    """AC-1: 正常启动时间盒 → started=True, timer_id>0"""
    result = start_timebox(
        step_id="task-001",
        max_minutes=30,
        risk_level="normal",
    )
    assert result["started"] is True
    assert result["timer_id"] > 0
    assert result["step_id"] == "task-001"
    assert result["max_minutes"] == 30
    assert result["risk_level"] == "normal"
    assert "时间盒已启动" in result["message"]


# ── AC-2: high risk 启动 ─────────────────────────────────

def test_start_timebox_high_risk():
    """AC-2: high risk 时间盒启动成功"""
    result = start_timebox(
        step_id="critical-task",
        max_minutes=10,
        risk_level="high",
    )
    assert result["started"] is True
    assert result["timer_id"] > 0
    assert result["risk_level"] == "high"


# ── AC-3: 同一 step_id 重复启动 → started=False ─────────

def test_start_timebox_duplicate_step_id():
    """AC-3: 同一 step_id 重复启动 → started=False"""
    r1 = start_timebox(step_id="dup-task", max_minutes=15, risk_level="normal")
    assert r1["started"] is True

    r2 = start_timebox(step_id="dup-task", max_minutes=30, risk_level="high")
    assert r2["started"] is False
    assert r2["timer_id"] == -1
    assert "已存在活跃时间盒" in r2["message"]


# ── AC-4: step_id 为空 → started=False ──────────────────

def test_start_timebox_empty_step_id():
    """AC-4: step_id 为空字符串 → started=False"""
    result = start_timebox(
        step_id="   ",
        max_minutes=10,
        risk_level="normal",
    )
    assert result["started"] is False
    assert result["timer_id"] == -1
    assert "step_id" in result["message"]


# ── AC-5: risk_level 不在枚举 → started=False ───────────

def test_start_timebox_invalid_risk():
    """AC-5: risk_level 无效 → started=False"""
    result = start_timebox(
        step_id="bad-risk-task",
        max_minutes=20,
        risk_level="critical",
    )
    assert result["started"] is False
    assert result["timer_id"] == -1
    assert "risk_level" in result["message"].lower()
    assert "无效" in result["message"]


# ── AC-6: max_minutes=0 → started=False ─────────────────

def test_start_timebox_zero_minutes():
    """AC-6: max_minutes=0 → started=False"""
    result = start_timebox(
        step_id="zero-min-task",
        max_minutes=0,
        risk_level="normal",
    )
    assert result["started"] is False
    assert result["timer_id"] == -1


# ── AC-7: 启动后立即检查 → exceeded=False ───────────────

def test_check_timebox_not_exceeded():
    """AC-7: 启动后立即检查 → exceeded=False"""
    r = start_timebox(step_id="check-me", max_minutes=60, risk_level="normal")
    assert r["started"] is True

    cr = check_timebox(step_id="check-me")
    assert cr["exceeded"] is False
    assert cr["timer_id"] == r["timer_id"]
    assert cr["elapsed_minutes"] >= 0
    assert "未超时" in cr["message"]


# ── AC-8: 模拟超时 → exceeded=True ──────────────────────

def test_check_timebox_exceeded():
    """AC-8: 手动修改 started_at 为过去时间 → exceeded=True"""
    r = start_timebox(step_id="will-timeout", max_minutes=1, risk_level="high")
    assert r["started"] is True

    # 直接操作 SQLite，把 started_at 改为 10 分钟前
    conn = sqlite3.connect(str(DB_PATH))
    past_time = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
    conn.execute(
        "UPDATE timebox_log SET started_at=? WHERE id=?",
        (past_time, r["timer_id"]),
    )
    conn.commit()
    conn.close()

    cr = check_timebox(step_id="will-timeout")
    assert cr["exceeded"] is True
    assert cr["elapsed_minutes"] > 1
    assert "超时" in cr["message"]


# ── AC-9: step_id 不存在 → 返回错误 ─────────────────────

def test_check_timebox_not_found():
    """AC-9: step_id 不存在活跃时间盒 → timer_id=-1"""
    cr = check_timebox(step_id="no-such-task")
    assert cr["timer_id"] == -1
    assert "没有活跃的时间盒" in cr["message"] or "不存在活跃时间盒" in cr["message"]


# ── AC-10: 检查后 SQLite 有记录 ─────────────────────────

def test_check_timebox_logs_to_sqlite():
    """AC-10: check_timebox 调用后 SQLite timebox_log 更新"""
    r = start_timebox(step_id="sql-log-task", max_minutes=45, risk_level="normal")
    assert r["started"] is True

    check_timebox(step_id="sql-log-task")

    # 验证数据库：status 变为 CHECKED，checked_at 非空
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT * FROM timebox_log WHERE step_id=? AND status='CHECKED'",
        ("sql-log-task",),
    ).fetchone()
    conn.close()
    assert row is not None
    assert row["checked_at"] is not None
    assert row["elapsed_minutes"] is not None
