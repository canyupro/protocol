from __future__ import annotations

import re
import subprocess
from pathlib import Path

from .models import EvidenceType, MarkCheckedRequest

# 项目根目录（mcp_server/ 的父目录）
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def validate_evidence(req: MarkCheckedRequest) -> tuple[bool, str]:
    """
    校验证据是否有效。返回 (accepted, reason)。

    校验规则按 evidence_type 分发：
    - PYTEST: 校验 evidence_url 里的 test 函数/类在文件中存在（grep）
    - RUFF: 校验 evidence_url 指向的文件存在
    - GIT_LOG: 校验 commit hash 真实（git rev-parse --verify）
    - SCREENSHOT: 校验文件存在于 docs/ 下
    - REVIEW: 不做机器校验，accepted=True（人工 review 无法机器验证）
    """
    if not req.item_id.strip():
        return False, "item_id 不能为空"

    if not req.evidence_url.strip():
        return False, "evidence_url 不能为空"

    if req.evidence_type == EvidenceType.PYTEST:
        return _validate_pytest(req.evidence_url)
    if req.evidence_type == EvidenceType.RUFF:
        return _validate_ruff(req.evidence_url)
    if req.evidence_type == EvidenceType.GIT_LOG:
        return _validate_git_log(req.evidence_url)
    if req.evidence_type == EvidenceType.SCREENSHOT:
        return _validate_screenshot(req.evidence_url)
    if req.evidence_type == EvidenceType.REVIEW:
        return True, "人工 review 类型，不做机器校验"

    return False, f"未知 evidence_type: {req.evidence_type}"


def _validate_pytest(evidence_url: str) -> tuple[bool, str]:
    """
    校验格式：path/to/test_xxx.py::TestClassName 或 path/to/test_xxx.py::test_func_name
    校验逻辑：文件存在 + 测试目标（类名或函数名）在文件中 grep 到。
    """
    match = re.match(r"^(.+\.py)::(.+)$", evidence_url)
    if not match:
        return False, f"PYTEST 证据格式应为 path/file.py::TestName，实际: {evidence_url}"

    file_rel, target = match.group(1), match.group(2)
    file_path = PROJECT_ROOT / file_rel

    if not file_path.exists():
        return False, f"测试文件不存在: {file_path}"

    content = file_path.read_text(encoding="utf-8")
    if target.startswith("Test"):
        pattern = rf"class\s+{re.escape(target)}\b"
    else:
        pattern = rf"def\s+{re.escape(target)}\b"

    if re.search(pattern, content):
        return True, f"PYTEST 证据有效: {file_rel}::{target}"
    return False, f"在 {file_rel} 中未找到测试目标: {target}"


def _validate_ruff(evidence_url: str) -> tuple[bool, str]:
    """校验 evidence_url 指向的文件存在。"""
    file_path = PROJECT_ROOT / evidence_url
    if file_path.exists():
        return True, f"RUFF 证据有效: {evidence_url}"
    return False, f"文件不存在: {file_path}"


def _validate_git_log(evidence_url: str) -> tuple[bool, str]:
    """校验 commit hash 真实。evidence_url 是 commit hash（7 或 40 位）。"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--verify", evidence_url],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return True, f"GIT_LOG 证据有效: {evidence_url}"
        return False, f"commit hash 无效: {evidence_url}"
    except subprocess.TimeoutExpired:
        return False, "git rev-parse 超时"
    except FileNotFoundError:
        return False, "git 命令不可用"


def _validate_screenshot(evidence_url: str) -> tuple[bool, str]:
    """校验截图文件存在于 docs/ 下。"""
    file_path = PROJECT_ROOT / evidence_url
    if file_path.exists() and "docs" in str(file_path):
        return True, f"SCREENSHOT 证据有效: {evidence_url}"
    return False, f"截图文件不存在或不在 docs/ 下: {file_path}"
