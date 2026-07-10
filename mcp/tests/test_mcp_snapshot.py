from __future__ import annotations

import os
import sqlite3

import pytest

from mcp_server.checker import PROJECT_ROOT
from mcp_server.server import snapshot_check
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

def _create_snapshot_file(name: str, content: str) -> str:
    """在 PROJECT_ROOT 下创建临时快照文件。返回相对路径名。"""
    file_path = PROJECT_ROOT / name
    file_path.write_text(content, encoding="utf-8")
    return name


def _remove_snapshot_file(name: str) -> None:
    """删除临时快照文件。"""
    file_path = PROJECT_ROOT / name
    file_path.unlink(missing_ok=True)


# ── AC-1: 所有必填字段都存在 → accepted=True ────────────

def test_complete_snapshot():
    """AC-1: 快照包含所有 6 个必填字段 → accepted=True"""
    content = """\
## workflow_state
- 当前角色: 执行方
- 任务阶段: 施工中
## 已冻结决策清单
- backend/core/ 不可修改
## 待定项
- 无
## 下一步
- 继续编码
"""
    name = _create_snapshot_file("test_complete_snap.md", content)
    try:
        result = snapshot_check(name)
        assert result["accepted"] is True
        assert result["total_fields"] == 6
        assert result["found_fields"] == 6
        assert result["missing_fields"] == []
        assert "通过" in result["message"]
    finally:
        _remove_snapshot_file(name)


# ── AC-2: 缺 workflow_state → accepted=False ────────────

def test_missing_workflow_state():
    """AC-2: 快照缺少 workflow_state → accepted=False"""
    content = """\
- 当前角色: 执行方
- 任务阶段: 施工中
## 已冻结决策清单
## 待定项
## 下一步
"""
    name = _create_snapshot_file("test_miss_ws.md", content)
    try:
        result = snapshot_check(name)
        assert result["accepted"] is False
        assert "workflow_state" in result["missing_fields"]
    finally:
        _remove_snapshot_file(name)


# ── AC-3: 缺当前角色 → accepted=False ──────────────────

def test_missing_role():
    """AC-3: 快照缺少「当前角色」→ accepted=False"""
    content = """\
## workflow_state
- 任务阶段: 施工中
## 已冻结决策清单
## 待定项
## 下一步
"""
    name = _create_snapshot_file("test_miss_role.md", content)
    try:
        result = snapshot_check(name)
        assert result["accepted"] is False
        assert "当前角色" in result["missing_fields"]
    finally:
        _remove_snapshot_file(name)


# ── AC-4: 缺多个字段 → missing_fields 含全部缺失 ───────

def test_missing_multiple():
    """AC-4: 快照缺少多个字段 → missing_fields 含全部"""
    content = """\
## workflow_state
- 当前角色: 执行方
"""
    name = _create_snapshot_file("test_miss_multi.md", content)
    try:
        result = snapshot_check(name)
        assert result["accepted"] is False
        missing = result["missing_fields"]
        # 缺少: 任务阶段, 已冻结决策, 待定项, 下一步
        assert "任务阶段" in missing
        assert "已冻结决策" in missing
        assert "待定项" in missing
        assert "下一步" in missing
        assert len(missing) == 4
    finally:
        _remove_snapshot_file(name)


# ── AC-5: 文件不存在 → accepted=False ──────────────────

def test_file_not_found():
    """AC-5: snapshot_path 指向不存在的文件 → accepted=False"""
    result = snapshot_check("nonexistent_snapshot_xyz.md")
    assert result["accepted"] is False
    assert "不存在" in result["message"]


# ── AC-6: snapshot_path 为空 → accepted=False ──────────

def test_empty_path():
    """AC-6: snapshot_path 为空字符串 → accepted=False"""
    result = snapshot_check("   ")
    assert result["accepted"] is False
    assert "不能为空" in result["message"]


# ── AC-7: 英文双语字段也能识别 ──────────────────────────

def test_bilingual_fields():
    """AC-7: 英文必填字段名也能被识别"""
    content = """\
## workflow_state
- Current role: Executor
- Task stage: In Progress
## Frozen Decision
- backend/core/ is frozen
## Pending
- None
## Next Step
- Continue coding
"""
    name = _create_snapshot_file("test_bilingual.md", content)
    try:
        result = snapshot_check(name)
        assert result["accepted"] is True
        assert result["found_fields"] == 6
        assert result["missing_fields"] == []
    finally:
        _remove_snapshot_file(name)


# ── AC-8: 调用后 SQLite 有记录 ──────────────────────────

def test_logged_to_sqlite():
    """AC-8: snapshot_check 调用后 SQLite snapshot_check_log 有记录"""
    content = """\
## workflow_state
- 当前角色: 执行方
- 任务阶段: 测试中
## 已冻结决策清单
## 待定项
## 下一步
"""
    name = _create_snapshot_file("test_sql_snap.md", content)
    try:
        result = snapshot_check(name)
        assert result["accepted"] is True

        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM snapshot_check_log ORDER BY id DESC LIMIT 1"
        ).fetchone()
        conn.close()
        assert row is not None
        assert row["snapshot_path"] == name
        assert row["total_fields"] == 6
        assert row["found_fields"] == 6
        assert row["accepted"] == 1
    finally:
        _remove_snapshot_file(name)
