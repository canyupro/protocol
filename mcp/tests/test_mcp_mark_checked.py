from __future__ import annotations

import os

import pytest

from mcp_server.checker import validate_evidence
from mcp_server.models import EvidenceType, MarkCheckedRequest
from mcp_server.server import mark_checked
from mcp_server.store import DB_PATH, get_history, init_db

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


# ── 占位测试类（供 PYTEST 类目标校验测试引用）─────────────

class TestPlaceholder:
    """Placeholder test class for mark_checked PYTEST class-target validation."""
    pass


# ── AC-1: PYTEST 类目标存在 ────────────────────────────────

def test_valid_pytest_class_target():
    """AC-1: PYTEST 证据，类目标存在 → accepted=True"""
    req = MarkCheckedRequest(
        item_id="AC-1",
        evidence_url="tests/test_mcp_mark_checked.py::TestPlaceholder",
        evidence_type=EvidenceType.PYTEST,
    )
    accepted, reason = validate_evidence(req)
    assert accepted is True, f"预期 accepted=True，实际 reason={reason}"
    assert "PYTEST 证据有效" in reason


# ── AC-2: PYTEST 函数目标存在 ────────────────────────────────

def test_valid_pytest_func_target():
    """AC-2: PYTEST 证据，函数目标存在 → accepted=True"""
    req = MarkCheckedRequest(
        item_id="AC-2",
        evidence_url="tests/test_mcp_timebox.py::test_start_timebox_normal",
        evidence_type=EvidenceType.PYTEST,
    )
    accepted, reason = validate_evidence(req)
    assert accepted is True, f"预期 accepted=True，实际 reason={reason}"
    assert "PYTEST 证据有效" in reason


# ── AC-3: PYTEST 文件不存在 ──────────────────────────────────

def test_invalid_pytest_file_not_exist():
    """AC-3: PYTEST 证据，文件不存在 → accepted=False"""
    req = MarkCheckedRequest(
        item_id="AC-3",
        evidence_url="tests/nonexistent_file.py::TestFake",
        evidence_type=EvidenceType.PYTEST,
    )
    accepted, reason = validate_evidence(req)
    assert accepted is False
    assert "不存在" in reason


# ── AC-4: PYTEST 目标找不到 ──────────────────────────────────

def test_invalid_pytest_target_not_found():
    """AC-4: PYTEST 证据，目标在文件中找不到 → accepted=False"""
    req = MarkCheckedRequest(
        item_id="AC-4",
        evidence_url="tests/test_mcp_timebox.py::TestNonexistentClass",
        evidence_type=EvidenceType.PYTEST,
    )
    accepted, reason = validate_evidence(req)
    assert accepted is False
    assert "未找到测试目标" in reason


# ── AC-5: GIT_LOG 真实 commit ──────────────────────────────

def test_valid_git_commit_short():
    """AC-5: GIT_LOG 证据，真实 short hash → accepted=True"""
    req = MarkCheckedRequest(
        item_id="AC-5",
        evidence_url="0f292df",
        evidence_type=EvidenceType.GIT_LOG,
    )
    accepted, reason = validate_evidence(req)
    assert accepted is True, f"预期 accepted=True，实际 reason={reason}"
    assert "GIT_LOG 证据有效" in reason


# ── AC-6: GIT_LOG 假 commit ────────────────────────────────

def test_invalid_git_commit():
    """AC-6: GIT_LOG 证据，假 hash → accepted=False"""
    req = MarkCheckedRequest(
        item_id="AC-6",
        evidence_url="deadbeefdeadbeef",
        evidence_type=EvidenceType.GIT_LOG,
    )
    accepted, reason = validate_evidence(req)
    assert accepted is False
    assert "无效" in reason


# ── AC-7: REVIEW 类型 ─────────────────────────────────────

def test_review_type_always_accepted():
    """AC-7: REVIEW 类型不做机器校验 → accepted=True"""
    req = MarkCheckedRequest(
        item_id="AC-7",
        evidence_url="人工确认: canyu 已 review",
        evidence_type=EvidenceType.REVIEW,
    )
    accepted, reason = validate_evidence(req)
    assert accepted is True


# ── AC-8: 空 item_id 拒绝 ───────────────────────────────────

def test_empty_item_id_rejected():
    """AC-8: item_id 为空 → accepted=False"""
    req = MarkCheckedRequest(
        item_id="   ",
        evidence_url="some_evidence",
        evidence_type=EvidenceType.REVIEW,
    )
    accepted, reason = validate_evidence(req)
    assert accepted is False
    assert "item_id" in reason


# ── AC-9 (加分): tool 返回 dict ─────────────────────────────

def test_mark_checked_tool_returns_dict():
    """AC-9: tool 调用返回 dict 且含 accepted 字段"""
    result = mark_checked(
        item_id="AC-9",
        evidence_url="人工确认通过",
        evidence_type="review",
    )
    assert isinstance(result, dict)
    assert "accepted" in result
    assert result["accepted"] is True


# ── AC-10 (加分): SQLite 记录 ──────────────────────────────

def test_mark_checked_logs_to_sqlite(clean_state_db):
    """AC-10: 调用后 SQLite 有记录"""
    result = mark_checked(
        item_id="AC-10",
        evidence_url="tests/test_mcp_mark_checked.py::TestPlaceholder",
        evidence_type="pytest",
    )
    assert result["accepted"] is True

    history = get_history("AC-10")
    assert len(history) == 1
    assert history[0]["item_id"] == "AC-10"
    assert history[0]["accepted"] == 1


# ── 边界: 空 evidence_url ──────────────────────────────────

def test_empty_evidence_url_rejected():
    """空 evidence_url → accepted=False"""
    req = MarkCheckedRequest(
        item_id="EDGE-1",
        evidence_url="  ",
        evidence_type=EvidenceType.PYTEST,
    )
    accepted, reason = validate_evidence(req)
    assert accepted is False
    assert "evidence_url" in reason


# ── 边界: PYTEST 格式错误 ──────────────────────────────────

def test_pytest_malformed_url():
    """PYTEST 格式不含 :: → accepted=False"""
    req = MarkCheckedRequest(
        item_id="EDGE-2",
        evidence_url="tests/test_k12_facts.py",
        evidence_type=EvidenceType.PYTEST,
    )
    accepted, reason = validate_evidence(req)
    assert accepted is False
    assert "格式应为" in reason


# ── 边界: RUFF 类型 ───────────────────────────────────────

def test_ruff_valid_file():
    """RUFF 证据，文件存在 → accepted=True"""
    req = MarkCheckedRequest(
        item_id="EDGE-3",
        evidence_url="mcp_server/checker.py",
        evidence_type=EvidenceType.RUFF,
    )
    accepted, reason = validate_evidence(req)
    assert accepted is True


def test_ruff_invalid_file():
    """RUFF 证据，文件不存在 → accepted=False"""
    req = MarkCheckedRequest(
        item_id="EDGE-4",
        evidence_url="nonexistent/ruff_target.py",
        evidence_type=EvidenceType.RUFF,
    )
    accepted, reason = validate_evidence(req)
    assert accepted is False
    assert "不存在" in reason
