from __future__ import annotations

import os
import sqlite3

import pytest

from mcp_server.server import validate_coverage
from mcp_server.store import DB_PATH, init_db

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


# ── AC-1: TOTAL 行 85% >= 70 → accepted=True ────────────

def test_valid_coverage_pass():
    """AC-1: TOTAL 行覆盖率 85% >= 阈值 70% → accepted=True"""
    cov_output = """\
Name                     Stmts   Miss  Cover
-----------------------------------------------
mcp_server/checker.py       50     10    80%
mcp_server/models.py        30      2    93%
mcp_server/server.py        80     15    81%
mcp_server/store.py         60      8    87%
-----------------------------------------------
TOTAL                      220     35    85%
"""
    result = validate_coverage(cov_output)
    assert result["accepted"] is True
    assert result["coverage_percent"] == 85.0
    assert result["threshold"] == 70.0
    assert "TOTAL" in result["total_line"]
    assert "通过" in result["message"] or ">=" in result["message"]


# ── AC-2: TOTAL 行 50% < 70 → accepted=False ────────────

def test_valid_coverage_below_threshold():
    """AC-2: TOTAL 行覆盖率 50% < 阈值 70% → accepted=False"""
    cov_output = """\
Name                     Stmts   Miss  Cover
-----------------------------------------------
module_a.py                100     50    50%
-----------------------------------------------
TOTAL                      100     50    50%
"""
    result = validate_coverage(cov_output)
    assert result["accepted"] is False
    assert result["coverage_percent"] == 50.0
    assert "不通过" in result["message"] or "<" in result["message"]


# ── AC-3: 刚好等于阈值 → accepted=True ──────────────────

def test_coverage_exactly_at_threshold():
    """AC-3: TOTAL 行覆盖率 70% == 阈值 70% → accepted=True"""
    cov_output = """\
TOTAL                      100     30    70%
"""
    result = validate_coverage(cov_output, threshold=70.0)
    assert result["accepted"] is True
    assert result["coverage_percent"] == 70.0


# ── AC-4: 输出无 TOTAL 行 → accepted=False ─────────────

def test_coverage_no_total_line():
    """AC-4: cov_output 中无 TOTAL 行 → accepted=False"""
    cov_output = """\
Name                     Stmts   Miss  Cover
-----------------------------------------------
module_a.py                100     10    90%
"""
    result = validate_coverage(cov_output)
    assert result["accepted"] is False
    assert result["total_line"] == ""
    assert "TOTAL" in result["message"] or "无法" in result["message"]


# ── AC-5: 空输出 → accepted=False ──────────────────────

def test_coverage_empty_output():
    """AC-5: cov_output 为空 → accepted=False"""
    result = validate_coverage("   ")
    assert result["accepted"] is False
    assert "不能为空" in result["message"]


# ── AC-6: 自定义阈值 90%，实际 85 → accepted=False ─────

def test_coverage_custom_threshold():
    """AC-6: threshold=90, 实际 85% → accepted=False"""
    cov_output = """\
TOTAL                      100     15    85%
"""
    result = validate_coverage(cov_output, threshold=90.0)
    assert result["accepted"] is False
    assert result["coverage_percent"] == 85.0
    assert result["threshold"] == 90.0


# ── AC-7: 调用后 SQLite 有记录 ──────────────────────────

def test_coverage_logged_to_sqlite():
    """AC-7: validate_coverage 调用后 SQLite coverage_log 有记录"""
    cov_output = "TOTAL                      100      8    92%"
    result = validate_coverage(cov_output)
    assert result["accepted"] is True

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM coverage_log ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    assert row is not None
    assert row["coverage_percent"] == 92.0
    assert row["threshold"] == 70.0
    assert row["accepted"] == 1


# ── AC-8: 不同 pytest-cov 输出格式（空格对齐差异）─────

def test_coverage_various_formats():
    """AC-8: 多种 pytest-cov TOTAL 行格式都能正确解析"""
    # 格式 1: 紧凑对齐
    result1 = validate_coverage("TOTAL                           120      8    93%")
    assert result1["coverage_percent"] == 93.0

    # 格式 2: 宽对齐
    result2 = validate_coverage("TOTAL                                 999       88      91.2%")
    assert result2["coverage_percent"] == 91.2

    # 格式 3: 浮点覆盖率
    result3 = validate_coverage("TOTAL                       50     10    80.5%")
    assert result3["coverage_percent"] == 80.5

    # 格式 4: 极简对齐
    result4 = validate_coverage("TOTAL 10 5 50%")
    assert result4["coverage_percent"] == 50.0
