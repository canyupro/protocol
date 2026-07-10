from __future__ import annotations

import os
import sqlite3

import pytest

from mcp_server.checker import PROJECT_ROOT
from mcp_server.server import verify_freeze
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


# ── 辅助函数 ──────────────────────────────────────────────

def _dirty_file(file_rel: str):
    """临时修改一个 tracked 文件，让 git diff --name-only HEAD 检测到它。
    返回 (original_content, file_path) 用于 restore。"""
    file_path = PROJECT_ROOT / file_rel
    original = file_path.read_bytes()
    # 追加一个换行（不会影响 Python 语法）
    file_path.write_bytes(original + b"\n")
    return original, file_path


def _restore_file(file_path, original_content):
    """恢复文件原始内容。"""
    file_path.write_bytes(original_content)


# ── AC-1: frozen_files 与 changed_files 无交集 → accepted=True ──

def test_no_violation():
    """AC-1: frozen_files 与当前改动无交集 → accepted=True"""
    result = verify_freeze(
        frozen_files=["docs/nonexistent-file.md", "backend/nonexistent/config.py"]
    )
    assert result["accepted"] is True
    assert result["violated_files"] == []
    assert "冻结检查通过" in result["message"]


# ── AC-2: frozen_file 出现在 changed_files → accepted=False ──

def test_violation_detected():
    """AC-2: frozen_file 在当前 git 改动中 → accepted=False"""
    target = "mcp_server/__init__.py"
    original, fp = _dirty_file(target)
    try:
        result = verify_freeze(frozen_files=[target])
        assert result["accepted"] is False
        assert target in result["violated_files"]
        assert "不通过" in result["message"]
    finally:
        _restore_file(fp, original)


# ── AC-3: frozen_files=[] → accepted=True ───────────────

def test_empty_frozen_files():
    """AC-3: frozen_files 为空列表 → accepted=True"""
    result = verify_freeze(frozen_files=[])
    assert result["accepted"] is True
    assert result["frozen_count"] == 0


# ── AC-4: frozen_files 非空但无匹配改动 → accepted=True ─

def test_no_changes_match():
    """AC-4: frozen_files 非空但 git 改动中无匹配 → accepted=True"""
    result = verify_freeze(
        frozen_files=["tests/not_changed_test.py", "docs/readme.md"]
    )
    assert result["accepted"] is True
    assert result["violated_files"] == []


# ── AC-5: 多个冻结文件被改 → violated_files 含全部 ─────

def test_multiple_violations():
    """AC-5: 多个冻结文件在改动中 → violated_files 含全部"""
    target1 = "mcp_server/__init__.py"
    target2 = "tests/test_mcp_coverage.py"

    original1, fp1 = _dirty_file(target1)
    try:
        # 第二个文件可能不存在，创建后再恢复
        fp2 = PROJECT_ROOT / target2
        original2 = fp2.read_bytes() if fp2.exists() else b""
        fp2.write_bytes(original2 + b"\n")
        try:
            result = verify_freeze(frozen_files=[target1, target2])
            assert result["accepted"] is False
            assert target1 in result["violated_files"]
            assert target2 in result["violated_files"]
            assert len(result["violated_files"]) == 2
        finally:
            fp2.write_bytes(original2)
    finally:
        _restore_file(fp1, original1)


# ── AC-6: 调用后 SQLite 有记录 ──────────────────────────

def test_logged_to_sqlite():
    """AC-6: verify_freeze 调用后 SQLite freeze_check_log 有记录"""
    target = "mcp_server/__init__.py"
    original, fp = _dirty_file(target)
    try:
        result = verify_freeze(frozen_files=[target])
        assert result["accepted"] is False

        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM freeze_check_log ORDER BY id DESC LIMIT 1"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row["frozen_count"] == 1
        assert row["accepted"] == 0
    finally:
        _restore_file(fp, original)


# ── AC-7: 部分冻结文件被改 → violated_files 只含被改的 ──

def test_partial_overlap():
    """AC-7: frozen_files 中部分命中 → violated_files 只含命中的"""
    target = "mcp_server/__init__.py"
    original, fp = _dirty_file(target)
    try:
        result = verify_freeze(
            frozen_files=[
                target,                              # 被改了
                "nonexistent/deep/path/file.py",      # 没被改
            ]
        )
        assert result["accepted"] is False
        assert target in result["violated_files"]
        assert "nonexistent/deep/path/file.py" not in result["violated_files"]
        assert len(result["violated_files"]) == 1
    finally:
        _restore_file(fp, original)


# ── AC-8: 路径格式测试 ──────────────────────────────────

def test_file_path_matching():
    """AC-8: 相对路径匹配验证"""
    target = "mcp_server/__init__.py"
    original, fp = _dirty_file(target)
    try:
        result = verify_freeze(frozen_files=[target])
        assert result["accepted"] is False
        assert target in result["violated_files"]
    finally:
        _restore_file(fp, original)
