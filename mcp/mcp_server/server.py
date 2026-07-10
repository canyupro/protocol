from __future__ import annotations

import json
from datetime import datetime, timezone

from mcp.server.fastmcp import FastMCP

from .checker import (
    PROJECT_ROOT,
    check_freeze_violation,
    check_snapshot_completeness,
    get_changed_files,
    parse_coverage,
    validate_evidence,
)
from .models import (
    CheckTimeboxResult,
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
    RiskLevel,
    SnapshotCheckResult,
    StartTimeboxRequest,
    StartTimeboxResult,
    ValidateCoverageResult,
    VerifyFreezeResult,
)
from .store import (
    get_active_timebox,
    get_pause,
    init_db,
    log_call,
    log_coverage,
    log_freeze_check,
    log_pause,
    log_resume,
    log_snapshot_check,
    log_step,
    log_timebox_check,
    log_timebox_start,
)

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


# ── Phase 4: Tool Expansion (时间盒 / 覆盖率 / 冻结检测 / 快照校验) ──


@mcp.tool()
def start_timebox(
    step_id: str,
    max_minutes: int,
    risk_level: str,
) -> dict[str, object]:
    """
    启动一个时间盒计时器。同一 step_id 重复调用 -> 报错。

    Args:
        step_id: 步骤标识，如 "R6-chain1-task-001"
        max_minutes: 超时阈值（分钟）
        risk_level: 风险等级，可选: normal / high

    Returns:
        dict: {timer_id, step_id, max_minutes, risk_level, started_at, started, message}
    """
    # 校验 step_id 非空
    if not step_id.strip():
        return StartTimeboxResult(
            timer_id=-1,
            step_id=step_id,
            max_minutes=max_minutes,
            risk_level=RiskLevel.NORMAL,
            started_at="",
            started=False,
            message="step_id 不能为空",
        ).model_dump()

    # 校验 max_minutes > 0
    if max_minutes <= 0:
        return StartTimeboxResult(
            timer_id=-1,
            step_id=step_id,
            max_minutes=max_minutes,
            risk_level=RiskLevel.NORMAL,
            started_at="",
            started=False,
            message="max_minutes 必须 > 0",
        ).model_dump()

    # 校验 risk_level
    try:
        rl = RiskLevel(risk_level)
    except ValueError:
        valid = [r.value for r in RiskLevel]
        return StartTimeboxResult(
            timer_id=-1,
            step_id=step_id,
            max_minutes=max_minutes,
            risk_level=RiskLevel.NORMAL,
            started_at="",
            started=False,
            message=f"risk_level 无效: {risk_level}，可选: {valid}",
        ).model_dump()

    # 校验 step_id 不存在活跃时间盒
    existing = get_active_timebox(step_id)
    if existing is not None:
        return StartTimeboxResult(
            timer_id=-1,
            step_id=step_id,
            max_minutes=max_minutes,
            risk_level=rl,
            started_at="",
            started=False,
            message=f"step_id '{step_id}' 已存在活跃时间盒（timer_id={existing['id']}），请先 check_timebox 或等待过期后再重新启动",
        ).model_dump()

    # 记录
    now_iso = datetime.now(timezone.utc).isoformat()
    timer_id = log_timebox_start(step_id, max_minutes, rl.value)

    return StartTimeboxResult(
        timer_id=timer_id,
        step_id=step_id,
        max_minutes=max_minutes,
        risk_level=rl,
        started_at=now_iso,
        started=True,
        message=f"时间盒已启动（timer_id={timer_id}，{max_minutes} 分钟，risk={rl.value}）",
    ).model_dump()


@mcp.tool()
def check_timebox(
    step_id: str,
) -> dict[str, object]:
    """
    检查时间盒是否超时。计算 elapsed = now - started_at。

    Args:
        step_id: 要检查的步骤标识

    Returns:
        dict: {timer_id, step_id, max_minutes, elapsed_minutes, exceeded, risk_level, message}
    """
    # 校验 step_id 非空
    if not step_id.strip():
        return CheckTimeboxResult(
            timer_id=-1,
            step_id=step_id,
            max_minutes=0,
            elapsed_minutes=0.0,
            exceeded=False,
            risk_level=RiskLevel.NORMAL,
            message="step_id 不能为空",
        ).model_dump()

    # 查询活跃时间盒
    record = get_active_timebox(step_id)
    if record is None:
        return CheckTimeboxResult(
            timer_id=-1,
            step_id=step_id,
            max_minutes=0,
            elapsed_minutes=0.0,
            exceeded=False,
            risk_level=RiskLevel.NORMAL,
            message=f"step_id '{step_id}' 不存在活跃时间盒",
        ).model_dump()

    # 计算 elapsed
    started_at_dt = datetime.fromisoformat(record["started_at"])
    now_dt = datetime.now(timezone.utc)
    elapsed_seconds = (now_dt - started_at_dt).total_seconds()
    elapsed_minutes = round(elapsed_seconds / 60.0, 2)
    exceeded = elapsed_minutes > record["max_minutes"]
    rl = RiskLevel(record["risk_level"])

    # 记录检查
    log_timebox_check(record["id"], elapsed_minutes, int(exceeded))

    if exceeded:
        msg = f"时间盒超时！已过 {elapsed_minutes} 分钟（上限 {record['max_minutes']} 分钟，risk={rl.value}）"
    else:
        msg = f"时间盒未超时（已过 {elapsed_minutes} / {record['max_minutes']} 分钟，risk={rl.value}）"

    return CheckTimeboxResult(
        timer_id=record["id"],
        step_id=step_id,
        max_minutes=record["max_minutes"],
        elapsed_minutes=elapsed_minutes,
        exceeded=exceeded,
        risk_level=rl,
        message=msg,
    ).model_dump()


@mcp.tool()
def validate_coverage(
    cov_output: str,
    threshold: float = 70.0,
) -> dict[str, object]:
    """
    解析 pytest 覆盖率输出，校验 TOTAL 行覆盖率 >= threshold。

    Args:
        cov_output: pytest --cov-report=term 的完整输出
        threshold: 覆盖率阈值（默认 70.0）

    Returns:
        dict: {accepted, coverage_percent, threshold, total_line, message}
    """
    # 校验 cov_output 非空
    if not cov_output.strip():
        return ValidateCoverageResult(
            accepted=False,
            coverage_percent=0.0,
            threshold=threshold,
            total_line="",
            message="cov_output 不能为空",
        ).model_dump()

    # 解析覆盖率
    parsed = parse_coverage(cov_output)
    if parsed is None:
        return ValidateCoverageResult(
            accepted=False,
            coverage_percent=0.0,
            threshold=threshold,
            total_line="",
            message="无法从 cov_output 中提取 TOTAL 行的覆盖率百分比",
        ).model_dump()

    coverage_percent, total_line = parsed
    accepted = coverage_percent >= threshold

    # 记录
    log_coverage(coverage_percent, threshold, accepted)

    if accepted:
        msg = f"覆盖率 {coverage_percent}% >= 阈值 {threshold}%，验收通过"
    else:
        msg = f"覆盖率 {coverage_percent}% < 阈值 {threshold}%，验收不通过"

    return ValidateCoverageResult(
        accepted=accepted,
        coverage_percent=coverage_percent,
        threshold=threshold,
        total_line=total_line,
        message=msg,
    ).model_dump()


@mcp.tool()
def verify_freeze(
    frozen_files: list[str],
) -> dict[str, object]:
    """
    校验当前 git 改动是否触及硬冻结文件。

    Args:
        frozen_files: 硬冻结文件路径列表（相对 PROJECT_ROOT 的路径）

    Returns:
        dict: {accepted, frozen_count, changed_count, violated_files, message}
    """
    # 校验 frozen_files 非空
    if not frozen_files:
        return VerifyFreezeResult(
            accepted=True,
            frozen_count=0,
            changed_count=0,
            violated_files=[],
            message="frozen_files 为空，无需检查冻结文件",
        ).model_dump()

    # 获取当前改动文件
    changed_files = get_changed_files()

    # 检查违规
    violated_files = check_freeze_violation(frozen_files, changed_files)
    accepted = len(violated_files) == 0

    # 记录
    log_freeze_check(len(frozen_files), len(changed_files), violated_files, accepted)

    if accepted:
        msg = f"冻结检查通过：{len(frozen_files)} 个冻结文件均未被修改"
    else:
        msg = f"冻结检查不通过：以下 {len(violated_files)} 个冻结文件被修改: {violated_files}"

    return VerifyFreezeResult(
        accepted=accepted,
        frozen_count=len(frozen_files),
        changed_count=len(changed_files),
        violated_files=violated_files,
        message=msg,
    ).model_dump()


@mcp.tool()
def snapshot_check(
    snapshot_path: str,
) -> dict[str, object]:
    """
    校验继承快照是否包含所有必填字段。

    必填字段（支持中英文双语搜索）：
    - workflow_state
    - 当前角色 / Current role
    - 任务阶段 / Task stage
    - 已冻结决策 / Frozen Decision
    - 待定项 / Pending
    - 下一步 / Next Step

    Args:
        snapshot_path: 继承快照文件路径（相对 PROJECT_ROOT）

    Returns:
        dict: {accepted, snapshot_path, total_fields, found_fields, missing_fields, message}
    """
    # 校验 snapshot_path 非空
    if not snapshot_path.strip():
        return SnapshotCheckResult(
            accepted=False,
            snapshot_path=snapshot_path,
            total_fields=0,
            found_fields=0,
            missing_fields=[],
            message="snapshot_path 不能为空",
        ).model_dump()

    # 解析路径
    full_path = PROJECT_ROOT / snapshot_path
    if not full_path.exists():
        return SnapshotCheckResult(
            accepted=False,
            snapshot_path=snapshot_path,
            total_fields=0,
            found_fields=0,
            missing_fields=[],
            message=f"快照文件不存在: {full_path}",
        ).model_dump()

    # 校验完整性
    found_fields, missing_fields = check_snapshot_completeness(full_path)
    total_fields = len(found_fields) + len(missing_fields)
    accepted = len(missing_fields) == 0

    # 记录
    log_snapshot_check(snapshot_path, total_fields, len(found_fields), missing_fields, accepted)

    if accepted:
        msg = f"快照完整性检查通过：{total_fields} 个必填字段全部存在"
    else:
        msg = f"快照完整性检查不通过：缺少 {len(missing_fields)} 个必填字段: {missing_fields}"

    return SnapshotCheckResult(
        accepted=accepted,
        snapshot_path=snapshot_path,
        total_fields=total_fields,
        found_fields=len(found_fields),
        missing_fields=missing_fields,
        message=msg,
    ).model_dump()


if __name__ == "__main__":
    init_db()
    mcp.run(transport="stdio")
