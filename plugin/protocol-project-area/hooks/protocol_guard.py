#!/usr/bin/env python3
"""Protocol 项目区代码写入守卫。

仅用于 ZCode PreToolUse 的 Edit/Write 路径。未初始化项目放行；已初始化项目
必须存在与目标相匹配的人类批准或未过期的人类豁免才能修改非项目区文件。

已知边界：该脚本无法可靠拦截 Bash 间接写入或零工具纯文本路径。
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

GUARD_RELATIVE_PATH = Path(".agents/protocol/guard.json")
PROJECT_DOCS_PREFIX = Path("doc/protocol")
AGENT_PROTOCOL_PREFIX = Path(".agents/protocol")
PROTECTED_RELATIVE_PATHS = {
    Path(".agents/protocol/guard.json"),
}
PROTECTED_PREFIXES = (Path("doc/protocol/approvals"),)
ALLOWED_AGENT_FILES = {
    Path(".agents/protocol/task.md"),
    Path(".agents/protocol/map.md"),
}


@dataclass(frozen=True)
class Decision:
    allowed: bool
    reason: str


def _value_at(data: dict[str, Any], *keys: str) -> Any:
    value: Any = data
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def extract_target_path(payload: dict[str, Any]) -> Path | None:
    """从常见 ZCode hook 载荷字段提取 Edit/Write 目标路径。"""
    tool_input = payload.get("toolInput")
    sources = [tool_input, payload]
    for source in sources:
        if not isinstance(source, dict):
            continue
        for key in ("file_path", "filePath", "path", "target_path", "targetPath"):
            value = source.get(key)
            if isinstance(value, str) and value.strip():
                return Path(value).expanduser()
    return None


def extract_cwd(payload: dict[str, Any]) -> Path:
    """优先使用 hook 载荷的 cwd，其次使用插件工作区环境变量。"""
    candidates = (
        _value_at(payload, "path", "cwd"),
        payload.get("cwd"),
        os.environ.get("ZCODE_PROJECT_DIR"),
        os.environ.get("CLAUDE_PROJECT_DIR"),
        os.getcwd(),
    )
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return Path(candidate).expanduser()
    return Path.cwd()


def _absolute_target(target: Path, cwd: Path) -> Path:
    return target if target.is_absolute() else cwd / target


def find_project_root(target: Path | None, cwd: Path) -> Path | None:
    """自目标文件或 cwd 向上寻找已初始化项目的 guard 文件。"""
    start = (target.parent if target is not None else cwd).resolve(strict=False)
    for candidate in (start, *start.parents):
        if (candidate / GUARD_RELATIVE_PATH).is_file():
            return candidate
    return None


def relative_to_root(target: Path, root: Path) -> Path | None:
    try:
        return target.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError:
        return None


def is_project_area_document(relative: Path) -> bool:
    if relative == PROJECT_DOCS_PREFIX or PROJECT_DOCS_PREFIX in relative.parents:
        return True
    if relative in ALLOWED_AGENT_FILES:
        return True
    verification = AGENT_PROTOCOL_PREFIX / "verification"
    return relative == verification or verification in relative.parents


def is_protected(relative: Path) -> bool:
    if relative in PROTECTED_RELATIVE_PATHS:
        return True
    return any(relative == prefix or prefix in relative.parents for prefix in PROTECTED_PREFIXES)


def load_guard(root: Path) -> dict[str, Any] | None:
    guard_path = root / GUARD_RELATIVE_PATH
    try:
        data = json.loads(guard_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict) or data.get("version") != 1:
        return None
    return data


def _field_value(text: str, label: str) -> str | None:
    for line in text.splitlines():
        stripped = line.strip()
        for prefix in (f"- {label}", label):
            if stripped.startswith(prefix):
                value = stripped[len(prefix):].lstrip("：:").strip()
                return value or None
    return None


def _list_after_label(text: str, label: str) -> list[str]:
    """读取标签下紧邻的缩进 Markdown 路径列表。

    范围列表必须使用模板中的缩进子项（`  - path`）。空行、下一个字段、
    标题或非列表内容都结束解析，避免把后续说明误当作可写范围。
    """
    lines = text.splitlines()
    values: list[str] = []
    found = False
    for line in lines:
        stripped = line.strip()
        if not found:
            if stripped in {f"- {label}", label}:
                found = True
            continue
        if not stripped:
            break
        if not line[:1].isspace():
            break
        child = line.lstrip()
        if not child.startswith("- "):
            break
        value = child[2:].strip().strip("`")
        if not value or "：" in value or ":" in value:
            break
        values.append(value)
    return values


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _normalize_scope_for_display(scope: str) -> str:
    """归一化 scope 仅用于比较展示：不改变空语义。

    原 lstrip("./") 会字符集剥离：'../src' → 'src'（不是 '../../../src'）。
    这会让用户写 '../src' 静默匹配项目根内 src，语义被悄悄改变。
    这里仅 strip + rstrip，不做 lstrip；对含 .. 段的 scope 视为非法（返回 ''）。
    """
    candidate = scope.strip().rstrip("/")
    if ".." in Path(candidate).parts:
        return ""
    return candidate


def _scope_matches(relative: Path, scopes: list[str]) -> bool:
    normalized = relative.as_posix()
    for scope in scopes:
        candidate = _normalize_scope_for_display(scope)
        if not candidate:
            continue
        if candidate in {"*", "."}:
            return True
        if normalized == candidate or normalized.startswith(f"{candidate}/"):
            return True
    return False


def _project_level_from_guard(root: Path) -> str:
    """从 questionnaire 第 5 节识别项目等级（个人/实验/生产级/未指定）。

    用于 PR 3 修正：expiry 分级。返回小写字符串；不在 4 个枚举内返回 "unknown"。
    """
    q = root / "doc" / "protocol" / "00-基础调查问卷.md"
    try:
        text = q.read_text(encoding="utf-8")
    except OSError:
        return "unknown"
    if "已上线生产级项目" in text:
        return "production"
    if "团队内部可控系统" in text:
        return "team"
    if "个人 / 实验项目" in text:
        return "personal"
    return "unknown"


def has_matching_approval(root: Path, relative: Path, now: datetime | None = None) -> bool:
    """检查是否有人类签发的理解批准，且目标路径落在批准范围内。

    PR 3 修正：expiry 分级。
      - production / team: 必填批准到期 ISO8601，默认 90 天
      - personal: 允许不填批准到期（即默认无过期约束）
      - unknown: 默认 production 行为（保守）
    """
    path = root / "doc/protocol/approvals/understanding-approved.md"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    approver = _field_value(text, "批准人")
    signed_at = _parse_datetime(_field_value(text, "批准时间（ISO8601）"))
    scopes = _list_after_label(text, "批准范围：")
    if not approver or not signed_at:
        return False

    level = _project_level_from_guard(root)
    expiry_raw = _field_value(text, "批准到期（ISO8601）")
    expiry_at = _parse_datetime(expiry_raw)

    if level == "personal":
        # 单人项目：批准人就是用户自己，不需要 expiry 硬约束
        pass
    else:
        # 生产 / 团队 / 未知：默认 90 天过期
        if expiry_at is None:
            expiry_at = signed_at + timedelta(days=90)
        # 接受 evaluate(now=...) 注入以保证测试可重现
        current = now or datetime.now(timezone.utc)
        if expiry_at <= current.astimezone(timezone.utc):
            return False

    return _scope_matches(relative, scopes)


def has_matching_exemption(root: Path, relative: Path, now: datetime) -> bool:
    path = root / "doc/protocol/approvals/write-exemption.md"
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return False
    issuer = _field_value(text, "豁免人")
    expires_at = _parse_datetime(_field_value(text, "到期时间（ISO8601）"))
    scopes = _list_after_label(text, "允许路径（相对项目根；一行一个文件或目录前缀）：")
    if not issuer or not expires_at or expires_at <= now:
        return False
    return _scope_matches(relative, scopes)


def evaluate(payload: dict[str, Any], now: datetime | None = None) -> Decision:
    """根据 hook 载荷评估一次 Edit/Write 是否可执行。"""
    cwd = extract_cwd(payload)
    target = extract_target_path(payload)
    absolute_target = _absolute_target(target, cwd) if target is not None else None
    root = find_project_root(absolute_target, cwd)
    if root is None:
        return Decision(True, "未初始化 Protocol 项目区，放行")

    relative = relative_to_root(absolute_target, root) if absolute_target is not None else None
    if relative is None:
        return Decision(False, "无法确认目标文件是否在已初始化项目内，拒绝写入")
    if is_protected(relative):
        return Decision(False, "guard 与人类批准/豁免文件受保护，主施工 agent 不得修改")
    if is_project_area_document(relative):
        return Decision(True, "项目区理解与流程文档允许写入")

    guard = load_guard(root)
    if guard is None:
        return Decision(False, "guard 状态损坏或不可读；对代码路径 fail-closed")
    if guard.get("status") != "pending":
        return Decision(False, "guard 状态无效；对代码路径 fail-closed")

    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if has_matching_approval(root, relative, now):
        return Decision(True, "存在匹配范围的人类理解批准")
    if has_matching_exemption(root, relative, current):
        return Decision(True, "存在匹配范围且未过期的人类书面豁免")
    return Decision(
        False,
        "最低理解标准尚未获得人类批准，也没有匹配的有效书面豁免；请补齐理解文档并由人类签发批准，或签发范围和期限明确的豁免",
    )


def main() -> int:
    payload_text = sys.stdin.read()

    # 空 stdin：客户端可能因异常管道发送空数据。
    # 无法判断 target / cwd → 没有证据说这次调用应该被拦 → return 0 放行，
    # 但 stderr 必须留下可观测的告警，让运维能发现 hook 异常。
    if not payload_text.strip():
        sys.stderr.write(
            "Protocol guard: stdin empty; unable to evaluate (allowing; "
            "this typically indicates a ZCode hook delivery bug — check client logs)\n"
        )
        return 0

    try:
        payload = json.loads(payload_text)
    except json.JSONDecodeError as exc:
        sys.stderr.write(
            f"Protocol guard: stdin is not valid JSON ({exc.msg} "
            f"@ line {exc.lineno} col {exc.colno}); allowing; "
            f"this typically indicates a ZCode hook delivery bug — check client logs)\n"
        )
        return 0

    if not isinstance(payload, dict):
        sys.stderr.write(
            "Protocol guard: payload must be a JSON object; allowing; "
            "check ZCode hook delivery version)\n"
        )
        return 0

    try:
        decision = evaluate(payload)
    except Exception as exc:  # noqa: BLE001
        sys.stderr.write(
            f"Protocol guard: internal error {type(exc).__name__}: {exc}; "
            f"allowing; this is a bug in the guard script — please report)\n"
        )
        return 0

    if decision.allowed:
        return 0
    sys.stderr.write(f"Protocol guard: {decision.reason}\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
