from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class EvidenceType(str, Enum):
    """证据类型，决定校验方式。"""
    PYTEST = "pytest"
    RUFF = "ruff"
    GIT_LOG = "git_log"
    SCREENSHOT = "screenshot"
    REVIEW = "review"


class MarkCheckedRequest(BaseModel):
    """mark_checked tool 的入参。"""
    item_id: str = Field(..., description="AC 编号或任务编号，如 AC-F20-1")
    evidence_url: str = Field(..., description="证据路径，如 tests/test_k12_facts.py::TestHistoryRecallIntent")
    evidence_type: EvidenceType = Field(..., description="证据类型")


class MarkCheckedResult(BaseModel):
    """mark_checked tool 的返回。"""
    item_id: str
    accepted: bool
    reason: str
    checked_at: str  # ISO8601 时间戳
    evidence_type: EvidenceType
    evidence_url: str


# ── Phase 2: pause_for_user / resume_from_pause ──────────────

class ForkOption(BaseModel):
    """分叉选项。"""
    option: str = Field(..., description="选项描述，如 '继续修复'")
    risk: str = Field(..., description="风险等级: LOW / MEDIUM / HIGH")


class PauseRequest(BaseModel):
    """pause_for_user tool 的入参。"""
    forks: list[ForkOption] = Field(..., description="分叉选项列表，至少 2 项")
    context: str = Field(..., description="为什么需要暂停")


class PauseResult(BaseModel):
    """pause_for_user tool 的返回。"""
    paused: bool
    forks: list[ForkOption]
    context: str
    message: str
    pause_id: int  # SQLite 记录 ID，供 resume 引用


class ResumeRequest(BaseModel):
    """resume_from_pause tool 的入参。"""
    pause_id: int = Field(..., description="pause_for_user 返回的 pause_id")
    choice: str = Field(..., description="用户选择的 option 文本")


class ResumeResult(BaseModel):
    """resume_from_pause tool 的返回。"""
    resumed: bool
    pause_id: int
    choice: str
    message: str


# ── Phase 3: report_step ──────────────────────────────────────

class ReportPhase(str, Enum):
    """报告阶段枚举。"""
    READ = "read"
    PLAN = "plan"
    IMPLEMENT = "implement"
    TEST = "test"
    WRAP_UP = "wrap_up"


class ReportStepRequest(BaseModel):
    """report_step tool 的入参。"""
    phase: ReportPhase = Field(..., description="阶段: read/plan/implement/test/wrap_up")
    content: str = Field(..., description="本步骤实际产出摘要，≤500 字")
    artifacts: list[str] = Field(..., description="产出文件路径列表")


class ReportStepResult(BaseModel):
    """report_step tool 的返回。"""
    step_seq: int           # 自增步骤序号
    phase: ReportPhase
    content: str
    artifacts: list[str]
    reported_at: str        # ISO8601 时间戳
    accepted: bool
    message: str


# ── Phase 4: Tool Expansion (时间盒 / 覆盖率 / 冻结检测 / 快照校验) ──


class RiskLevel(str, Enum):
    """时间盒风险等级。normal=5轮红灯，high=2轮红灯。"""
    NORMAL = "normal"
    HIGH = "high"


class StartTimeboxRequest(BaseModel):
    """start_timebox tool 的入参。"""
    step_id: str = Field(..., description="步骤标识，如 R6-chain1-task-001")
    max_minutes: int = Field(..., description="超时阈值（分钟）")
    risk_level: RiskLevel = Field(..., description="风险等级")


class StartTimeboxResult(BaseModel):
    """start_timebox tool 的返回。"""
    timer_id: int
    step_id: str
    max_minutes: int
    risk_level: RiskLevel
    started_at: str         # ISO8601 时间戳
    started: bool
    message: str


class CheckTimeboxResult(BaseModel):
    """check_timebox tool 的返回。"""
    timer_id: int
    step_id: str
    max_minutes: int
    elapsed_minutes: float
    exceeded: bool
    risk_level: RiskLevel
    message: str


class ValidateCoverageResult(BaseModel):
    """validate_coverage tool 的返回。"""
    accepted: bool
    coverage_percent: float
    threshold: float
    total_line: str
    message: str


class VerifyFreezeResult(BaseModel):
    """verify_freeze tool 的返回。"""
    accepted: bool
    frozen_count: int
    changed_count: int
    violated_files: list[str]
    message: str


class SnapshotCheckResult(BaseModel):
    """snapshot_check tool 的返回。"""
    accepted: bool
    snapshot_path: str
    total_fields: int
    found_fields: int
    missing_fields: list[str]
    message: str
