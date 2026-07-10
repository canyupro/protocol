from __future__ import annotations

import os

import pytest

from mcp_server.server import pause_for_user, resume_from_pause
from mcp_server.store import DB_PATH, get_pause, init_db

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


# ── AC-1: 2 个合法分叉 → paused=True ──────────────────────

def test_valid_pause_with_two_forks():
    """AC-1: 2 个合法分叉 → paused=True"""
    result = pause_for_user(
        forks=[
            {"option": "继续修复", "risk": "MEDIUM"},
            {"option": "降级处理", "risk": "LOW"},
        ],
        context="测试分叉1: 两项可选",
    )
    assert result["paused"] is True
    assert result["pause_id"] > 0
    assert "已暂停" in result["message"]


# ── AC-2: 3 个分叉 → paused=True ─────────────────────────

def test_pause_with_three_forks():
    """AC-2: 3 个分叉 → paused=True"""
    result = pause_for_user(
        forks=[
            {"option": "方案A: 继续修复", "risk": "HIGH"},
            {"option": "方案B: 降级处理", "risk": "MEDIUM"},
            {"option": "方案C: 延期到V2", "risk": "LOW"},
        ],
        context="测试分叉2: 三项可选",
    )
    assert result["paused"] is True
    assert len(result["forks"]) == 3


# ── AC-3: 只有 1 个分叉 → paused=False ────────────────────

def test_pause_rejects_single_fork():
    """AC-3: 只有 1 个分叉 → paused=False"""
    result = pause_for_user(
        forks=[
            {"option": "只有一个选项", "risk": "LOW"},
        ],
        context="测试分叉3: 只有一项",
    )
    assert result["paused"] is False
    assert result["pause_id"] == -1
    assert "至少需要 2 项" in result["message"]


# ── AC-4: forks 为空 → paused=False ──────────────────────

def test_pause_rejects_empty_forks():
    """AC-4: forks 为空 → paused=False"""
    result = pause_for_user(
        forks=[],
        context="测试分叉4: 空列表",
    )
    assert result["paused"] is False
    assert "不能为空" in result["message"]


# ── AC-5: risk 非法 → paused=False ───────────────────────

def test_pause_rejects_invalid_risk():
    """AC-5: risk 不是 LOW/MEDIUM/HIGH → paused=False"""
    result = pause_for_user(
        forks=[
            {"option": "合法选项", "risk": "LOW"},
            {"option": "非法risk", "risk": "CRITICAL"},
        ],
        context="测试分叉5: 非法risk",
    )
    assert result["paused"] is False
    assert "LOW/MEDIUM/HIGH" in result["message"]


# ── AC-6: 合法 choice 恢复 → resumed=True ─────────────────

def test_valid_resume():
    """AC-6: 合法 choice 恢复 → resumed=True"""
    # 先 pause
    p = pause_for_user(
        forks=[
            {"option": "选A", "risk": "LOW"},
            {"option": "选B", "risk": "MEDIUM"},
        ],
        context="测试恢复1",
    )
    assert p["paused"] is True
    pause_id = p["pause_id"]

    # 再 resume
    r = resume_from_pause(pause_id=pause_id, choice="选B")
    assert r["resumed"] is True
    assert r["choice"] == "选B"
    assert "已恢复" in r["message"]

    # 验证 SQLite 状态已更新
    record = get_pause(pause_id)
    assert record["status"] == "RESUMED"
    assert record["choice"] == "选B"


# ── AC-7: choice 不在 forks 内 → resumed=False ────────────

def test_resume_rejects_invalid_choice():
    """AC-7: choice 不在 forks 内 → resumed=False"""
    p = pause_for_user(
        forks=[
            {"option": "选A", "risk": "LOW"},
            {"option": "选B", "risk": "MEDIUM"},
        ],
        context="测试恢复2",
    )
    r = resume_from_pause(pause_id=p["pause_id"], choice="选C")
    assert r["resumed"] is False
    assert "不在分叉选项内" in r["message"]


# ── AC-8: pause_id 不存在 → resumed=False ────────────────

def test_resume_rejects_nonexistent_pause_id():
    """AC-8: pause_id 不存在 → resumed=False"""
    r = resume_from_pause(pause_id=99999, choice="随便")
    assert r["resumed"] is False
    assert "不存在" in r["message"]


# ── AC-9 (加分): 同一 pause_id 不可重复恢复 ───────────────

def test_resume_rejects_double_resume():
    """AC-9(加分): 同一 pause_id 恢复两次 → 第二次 resumed=False"""
    p = pause_for_user(
        forks=[
            {"option": "选A", "risk": "LOW"},
            {"option": "选B", "risk": "MEDIUM"},
        ],
        context="测试重复恢复",
    )

    # 第一次恢复
    r1 = resume_from_pause(pause_id=p["pause_id"], choice="选A")
    assert r1["resumed"] is True

    # 第二次恢复
    r2 = resume_from_pause(pause_id=p["pause_id"], choice="选B")
    assert r2["resumed"] is False
    assert "非 PAUSED" in r2["message"]


# ── AC-10 (加分): pause_for_user 返回 pause_id 且 > 0 ────

def test_pause_returns_pause_id():
    """AC-10(加分): pause_for_user 返回 pause_id 且 > 0"""
    p1 = pause_for_user(
        forks=[
            {"option": "选A", "risk": "LOW"},
            {"option": "选B", "risk": "MEDIUM"},
        ],
        context="测试pause_id 1",
    )
    p2 = pause_for_user(
        forks=[
            {"option": "选X", "risk": "HIGH"},
            {"option": "选Y", "risk": "MEDIUM"},
        ],
        context="测试pause_id 2",
    )
    assert p1["pause_id"] > 0
    assert p2["pause_id"] > 0
    assert p1["pause_id"] != p2["pause_id"]  # 每次不同


# ── 边界: context 为空 → paused=False ────────────────────

def test_pause_rejects_empty_context():
    """context 为空 → paused=False"""
    result = pause_for_user(
        forks=[
            {"option": "选A", "risk": "LOW"},
            {"option": "选B", "risk": "MEDIUM"},
        ],
        context="   ",
    )
    assert result["paused"] is False
    assert "context" in result["message"].lower()
