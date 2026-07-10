from __future__ import annotations

import os

import pytest

from mcp_server.server import report_step
from mcp_server.store import DB_PATH, get_step, get_step_count, init_db

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


# ── AC-1: 合法报告 → accepted=True, step_seq>0 ──────────

def test_valid_report():
    """AC-1: 合法报告 → accepted=True, step_seq>0"""
    result = report_step(
        phase="implement",
        content="实现 report_step tool",
        artifacts=["mcp_server/server.py"],
    )
    assert result["accepted"] is True
    assert result["step_seq"] > 0
    assert "步骤" in result["message"]


# ── AC-2: step_seq 递增 ──────────────────────────────────

def test_step_seq_auto_increments():
    """AC-2: 连续报告 → step_seq 递增"""
    r1 = report_step(phase="read", content="读文档", artifacts=["mcp_server/server.py"])
    r2 = report_step(phase="plan", content="写方案", artifacts=["mcp_server/server.py"])
    r3 = report_step(phase="implement", content="写代码", artifacts=["mcp_server/server.py"])
    assert r1["step_seq"] < r2["step_seq"] < r3["step_seq"]


# ── AC-3: phase 不在枚举 → accepted=False ───────────────

def test_invalid_phase_rejected():
    """AC-3: phase 不在枚举 → accepted=False"""
    result = report_step(
        phase="invalid_phase",
        content="test",
        artifacts=["mcp_server/server.py"],
    )
    assert result["accepted"] is False
    assert result["step_seq"] == -1
    assert "无效" in result["message"]


# ── AC-4: content 为空 → accepted=False ─────────────────

def test_empty_content_rejected():
    """AC-4: content 为空 → accepted=False"""
    result = report_step(
        phase="test",
        content="   ",
        artifacts=["mcp_server/server.py"],
    )
    assert result["accepted"] is False
    assert "content" in result["message"].lower()


# ── AC-5: content >500 字 → accepted=False ──────────────

def test_content_over_500_chars_rejected():
    """AC-5: content >500 字 → accepted=False"""
    result = report_step(
        phase="implement",
        content="x" * 501,
        artifacts=["mcp_server/server.py"],
    )
    assert result["accepted"] is False
    assert "500" in result["message"]


# ── AC-6: artifacts 为空 → accepted=False ───────────────

def test_empty_artifacts_rejected():
    """AC-6: artifacts 为空 → accepted=False"""
    result = report_step(
        phase="wrap_up",
        content="完成收尾",
        artifacts=[],
    )
    assert result["accepted"] is False
    assert "不能为空" in result["message"]


# ── AC-7: artifact 路径不存在 → accepted=False ──────────

def test_nonexistent_artifact_rejected():
    """AC-7: artifact 路径不存在 → accepted=False"""
    result = report_step(
        phase="test",
        content="测试不存在路径",
        artifacts=["nonexistent/file.py"],
    )
    assert result["accepted"] is False
    assert "路径不存在" in result["message"]


# ── AC-8: 调用后 SQLite 有记录 ──────────────────────────

def test_step_logged_to_sqlite():
    """AC-8: 调用后 SQLite 有记录"""
    result = report_step(
        phase="read",
        content="读取设计文档",
        artifacts=["mcp_server/server.py"],
    )
    step_seq = result["step_seq"]
    record = get_step(step_seq)
    assert record is not None
    assert record["phase"] == "read"
    assert record["content"] == "读取设计文档"


# ── AC-9 (加分): get_step_count ─────────────────────────

def test_get_step_count_accurate():
    """AC-9: get_step_count 返回正确数量"""
    for i in range(3):
        report_step(
            phase="test",
            content=f"测试步骤{i}",
            artifacts=["mcp_server/server.py"],
        )
    assert get_step_count() == 3


# ── AC-10 (加分): 5 种 phase 都 accepted ────────────────

def test_all_five_phases_accepted():
    """AC-10: 5 种 phase 都 accepted=True"""
    for ph in ["read", "plan", "implement", "test", "wrap_up"]:
        result = report_step(
            phase=ph,
            content=f"phase={ph} 测试",
            artifacts=["mcp_server/server.py"],
        )
        assert result["accepted"] is True, f"phase={ph} 应为 accepted=True，实际: {result['message']}"


# ── 边界: content 刚好 500 字 → accepted ────────────────

def test_content_exactly_500_chars_accepted():
    """content 刚好 500 字 → accepted=True"""
    result = report_step(
        phase="implement",
        content="a" * 500,
        artifacts=["mcp_server/server.py"],
    )
    assert result["accepted"] is True
