from __future__ import annotations

import json
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

from .checker import PROJECT_ROOT, validate_evidence
from .models import (
    EvidenceType,
    ForkOption,
    MarkCheckedRequest,
    MarkCheckedResult,
    PauseRequest,
    PauseResult,
    ReportPhase,
    ReportStepRequest,
    ReportStepResult,
    ResumeResult,
)
from .store import get_pause, init_db, log_call, log_pause, log_resume, log_step

# 初始化 MCP server
mcp = FastMCP("protocol-mcp")


@mcp.tool()
def mark_checked(
    item_id: str,
    evidence_url: str,
    evidence_type: str,
) -> dict[str, object]:
    """
    标记一个 AC / 任务为完成。必须附带证据。
    无证据或证据不可达 → reject，不允许标完成。

    Args:
        item_id: AC 编号或任务编号，如 "AC-F20-1"
        evidence_url: 证据路径，如 "tests/test_k12_facts.py::TestHistoryRecallIntent"
        evidence_type: 证据类型，可选值: pytest / ruff / git_log / screenshot / review

    Returns:
        dict: {item_id, accepted, reason, checked_at, evidence_type, evidence_url}
    """
    # 构造请求
    try:
        req = MarkCheckedRequest(
            item_id=item_id,
            evidence_url=evidence_url,
            evidence_type=EvidenceType(evidence_type),
        )
    except ValueError:
        valid = [e.value for e in EvidenceType]
        return MarkCheckedResult(
            item_id=item_id,
            accepted=False,
            reason=f"evidence_type 无效: {evidence_type}，可选: {valid}",
            checked_at=datetime.now(timezone.utc).isoformat(),
            evidence_type=EvidenceType.REVIEW,
            evidence_url=evidence_url,
        ).model_dump()

    # 校验
    accepted, reason = validate_evidence(req)

    # 记录
    result = MarkCheckedResult(
        item_id=item_id,
        accepted=accepted,
        reason=reason,
        checked_at=datetime.now(timezone.utc).isoformat(),
        evidence_type=req.evidence_type,
        evidence_url=evidence_url,
    )
    log_call(req, result)

    return result.model_dump()


# ── Phase 2: pause_for_user / resume_from_pause ──────────────

@mcp.tool()
def pause_for_user(
    forks: list[dict[str, str]],
    context: str,
) -> dict[str, object]:
    """
    在策略分叉点强制暂停，把决策权交还用户。
    AI 不能自行选择分叉，必须调用本 tool 后等待用户拍板。

    调用后 AI 应停止产出，把 forks 展示给用户。
    用户做出选择后，调用 resume_from_pause(pause_id, choice) 恢复。

    Args:
        forks: 分叉选项列表，每项含 option(描述) 和 risk(LOW/MEDIUM/HIGH)，至少 2 项
        context: 为什么需要暂停

    Returns:
        dict: {paused, forks, context, message, pause_id}
    """
    # 校验 forks
    if not forks or len(forks) < 2:
        return PauseResult(
            paused=False,
            forks=[],
            context=context,
            message="分叉选项至少需要 2 项，否则不是分叉" if forks else "forks 不能为空",
            pause_id=-1,
        ).model_dump()

    # 校验 context 非空
    if not context.strip():
        return PauseResult(
            paused=False,
            forks=[],
            context=context,
            message="context 不能为空",
            pause_id=-1,
        ).model_dump()

    # 构造 ForkOption 列表
    try:
        fork_options = [ForkOption(**f) for f in forks]
    except Exception as e:
        return PauseResult(
            paused=False,
            forks=[],
            context=context,
            message=f"分叉选项格式错误: {e}",
            pause_id=-1,
        ).model_dump()

    # 校验 risk 值
    valid_risks = {"LOW", "MEDIUM", "HIGH"}
    for fo in fork_options:
        if fo.risk not in valid_risks:
            return PauseResult(
                paused=False,
                forks=fork_options,
                context=context,
                message=f"risk 必须是 LOW/MEDIUM/HIGH，实际: {fo.risk}",
                pause_id=-1,
            ).model_dump()

    req = PauseRequest(forks=fork_options, context=context)

    # 记录
    pause_id = log_pause(req)

    return PauseResult(
        paused=True,
        forks=fork_options,
        context=context,
        message="已暂停。请用户在分叉选项中选择，然后调用 resume_from_pause",
        pause_id=pause_id,
    ).model_dump()


@mcp.tool()
def resume_from_pause(
    pause_id: int,
    choice: str,
) -> dict[str, object]:
    """
    用户做出分叉选择后恢复执行。

    Args:
        pause_id: pause_for_user 返回的 pause_id
        choice: 用户选择的 option 文本

    Returns:
        dict: {resumed, pause_id, choice, message}
    """
    # 校验 pause_id 存在且处于 PAUSED 状态
    record = get_pause(pause_id)
    if record is None:
        return ResumeResult(
            resumed=False,
            pause_id=pause_id,
            choice=choice,
            message=f"pause_id={pause_id} 不存在",
        ).model_dump()

    if record["status"] != "PAUSED":
        return ResumeResult(
            resumed=False,
            pause_id=pause_id,
            choice=choice,
            message=f"pause_id={pause_id} 状态为 {record['status']}，非 PAUSED，不可重复恢复",
        ).model_dump()

    # 校验 choice 在原 forks 内
    forks_data = json.loads(record["forks_json"])
    valid_options = [f["option"] for f in forks_data]
    if choice not in valid_options:
        return ResumeResult(
            resumed=False,
            pause_id=pause_id,
            choice=choice,
            message=f"choice '{choice}' 不在分叉选项内: {valid_options}",
        ).model_dump()

    # 记录恢复
    success = log_resume(pause_id, choice)

    return ResumeResult(
        resumed=success,
        pause_id=pause_id,
        choice=choice,
        message="已恢复执行" if success else "恢复失败",
    ).model_dump()


# ── Phase 3: report_step ──────────────────────────────────────

@mcp.tool()
def report_step(
    phase: str,
    content: str,
    artifacts: list[str],
) -> dict[str, object]:
    """
    报告一个规程步骤的完成。不调用本 tool 不允许进入下一步 / 不允许 commit。
    把「自我证明在按规程做事」的噪声压缩为结构化记录。

    Args:
        phase: 阶段，可选值: read / plan / implement / test / wrap_up
        content: 本步骤实际产出摘要，≤500 字
        artifacts: 产出文件路径列表

    Returns:
        dict: {step_seq, phase, content, artifacts, reported_at, accepted, message}
    """
    # 校验 phase
    try:
        report_phase = ReportPhase(phase)
    except ValueError:
        valid = [p.value for p in ReportPhase]
        return ReportStepResult(
            step_seq=-1,
            phase=ReportPhase.READ,
            content=content,
            artifacts=artifacts,
            reported_at=datetime.now(timezone.utc).isoformat(),
            accepted=False,
            message=f"phase 无效: {phase}，可选: {valid}",
        ).model_dump()

    # 校验 content 非空
    if not content.strip():
        return ReportStepResult(
            step_seq=-1,
            phase=report_phase,
            content=content,
            artifacts=artifacts,
            reported_at=datetime.now(timezone.utc).isoformat(),
            accepted=False,
            message="content 不能为空",
        ).model_dump()

    # 校验 content ≤ 500 字
    if len(content) > 500:
        return ReportStepResult(
            step_seq=-1,
            phase=report_phase,
            content=content,
            artifacts=artifacts,
            reported_at=datetime.now(timezone.utc).isoformat(),
            accepted=False,
            message=f"content 超过 500 字（实际 {len(content)} 字），请压缩",
        ).model_dump()

    # 校验 artifacts 非空
    if not artifacts:
        return ReportStepResult(
            step_seq=-1,
            phase=report_phase,
            content=content,
            artifacts=artifacts,
            reported_at=datetime.now(timezone.utc).isoformat(),
            accepted=False,
            message="artifacts 不能为空，至少 1 个产出文件",
        ).model_dump()

    # 校验 artifacts 路径存在
    missing = []
    for art in artifacts:
        if not (PROJECT_ROOT / art).exists():
            missing.append(art)
    if missing:
        return ReportStepResult(
            step_seq=-1,
            phase=report_phase,
            content=content,
            artifacts=artifacts,
            reported_at=datetime.now(timezone.utc).isoformat(),
            accepted=False,
            message=f"artifacts 路径不存在: {missing}",
        ).model_dump()

    req = ReportStepRequest(phase=report_phase, content=content, artifacts=artifacts)

    # 记录
    step_seq = log_step(req)

    return ReportStepResult(
        step_seq=step_seq,
        phase=report_phase,
        content=content,
        artifacts=artifacts,
        reported_at=datetime.now(timezone.utc).isoformat(),
        accepted=True,
        message=f"步骤 {step_seq} 已记录（phase={report_phase.value}）",
    ).model_dump()


if __name__ == "__main__":
    init_db()
    mcp.run(transport="stdio")
