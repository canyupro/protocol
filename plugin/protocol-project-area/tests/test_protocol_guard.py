from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

GUARD_PATH = Path(__file__).resolve().parents[1] / "hooks" / "protocol_guard.py"
SPEC = importlib.util.spec_from_file_location("protocol_guard", GUARD_PATH)
assert SPEC and SPEC.loader
protocol_guard = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = protocol_guard
SPEC.loader.exec_module(protocol_guard)


class ProtocolGuardTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.source = self.root / "src" / "main.py"
        self.source.parent.mkdir(parents=True)
        self.source.write_text("print('before')\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def payload(self, path: Path) -> dict[str, object]:
        return {
            "path": {"cwd": str(self.root)},
            "toolInput": {"file_path": str(path)},
        }

    def initialize(self, content: str = '{"version": 1, "status": "pending"}') -> None:
        guard = self.root / ".agents/protocol/guard.json"
        guard.parent.mkdir(parents=True)
        guard.write_text(content, encoding="utf-8")

    def approval(self, scope: str = "src") -> None:
        path = self.root / "doc/protocol/approvals/understanding-approved.md"
        path.parent.mkdir(parents=True)
        path.write_text(
            "# 人类批准：最低理解标准\n\n"
            "- 批准人：负责人\n"
            "- 批准时间（ISO8601）：2026-08-14T00:00:00+00:00\n"
            "- 批准范围：\n"
            f"  - {scope}\n",
            encoding="utf-8",
        )

    def exemption(self, scope: str, expires_at: datetime) -> None:
        path = self.root / "doc/protocol/approvals/write-exemption.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "# 人类豁免：临时代码写入\n\n"
            "- 豁免人：负责人\n"
            f"- 到期时间（ISO8601）：{expires_at.isoformat()}\n"
            "- 允许路径（相对项目根；一行一个文件或目录前缀）：\n"
            f"  - {scope}\n",
            encoding="utf-8",
        )

    def test_uninitialized_project_allows_write(self) -> None:
        decision = protocol_guard.evaluate(self.payload(self.source))
        self.assertTrue(decision.allowed)

    def test_pending_guard_blocks_source_write(self) -> None:
        self.initialize()
        decision = protocol_guard.evaluate(self.payload(self.source))
        self.assertFalse(decision.allowed)
        self.assertIn("最低理解标准", decision.reason)

    # ── PR 2: observe-only 模式（read-only 项目）──

    def test_observe_only_blocks_source_write(self) -> None:
        """observe-only：业务路径一律 deny，不需要人类批准。"""
        self.initialize(content='{"version":1,"status":"pending","intent":"observe-only"}')
        decision = protocol_guard.evaluate(self.payload(self.source))
        self.assertFalse(decision.allowed)
        self.assertIn("observe-only", decision.reason)
        self.assertIn("不允许任何业务代码写入", decision.reason)

    def test_observe_only_allows_project_document(self) -> None:
        """observe-only：项目区文档（如理解文档、问卷）仍可写。"""
        self.initialize(content='{"version":1,"status":"pending","intent":"observe-only"}')
        document = self.root / "doc/protocol/understanding/naming.md"
        decision = protocol_guard.evaluate(self.payload(document))
        self.assertTrue(decision.allowed)
        self.assertIn("observe-only", decision.reason)

    def test_observe_only_blocks_verification_directory(self) -> None:
        """observe-only：verification/ 仍受 PROTECTED 规则约束（独立验证方才能写）。"""
        self.initialize(content='{"version":1,"status":"pending","intent":"observe-only"}')
        target = self.root / ".agents/protocol/verification/understanding-review.md"
        decision = protocol_guard.evaluate(self.payload(target))
        self.assertFalse(decision.allowed)
        self.assertIn("受保护", decision.reason)

    def test_pending_guard_allows_project_document(self) -> None:
        self.initialize()
        document = self.root / "doc/protocol/understanding/naming.md"
        decision = protocol_guard.evaluate(self.payload(document))
        self.assertTrue(decision.allowed)

    def test_guard_and_approval_files_are_protected(self) -> None:
        self.initialize()
        for path in (
            self.root / ".agents/protocol/guard.json",
            self.root / "doc/protocol/approvals/understanding-approved.md",
        ):
            decision = protocol_guard.evaluate(self.payload(path))
            self.assertFalse(decision.allowed)
            self.assertIn("受保护", decision.reason)

    def test_matching_approval_allows_source_write(self) -> None:
        self.initialize()
        self.approval("src")
        decision = protocol_guard.evaluate(self.payload(self.source))
        self.assertTrue(decision.allowed)

    def test_approval_does_not_allow_outside_scope(self) -> None:
        self.initialize()
        self.approval("src")
        other = self.root / "other.py"
        decision = protocol_guard.evaluate(self.payload(other))
        self.assertFalse(decision.allowed)

    def test_approval_scope_stops_before_following_fields(self) -> None:
        self.initialize()
        path = self.root / "doc/protocol/approvals/understanding-approved.md"
        path.parent.mkdir(parents=True)
        path.write_text(
            "# 人类批准：最低理解标准\n\n"
            "- 批准人：负责人\n"
            "- 批准时间（ISO8601）：2026-08-14T00:00:00+00:00\n"
            "- 批准范围：\n"
            "  - src\n"
            "- 说明：不允许其他路径\n",
            encoding="utf-8",
        )
        decision = protocol_guard.evaluate(self.payload(self.root / "outside.py"))
        self.assertFalse(decision.allowed)

    def test_approval_scope_accepts_trailing_slash(self) -> None:
        self.initialize()
        self.approval("src/")
        decision = protocol_guard.evaluate(self.payload(self.source))
        self.assertTrue(decision.allowed)

    def test_approval_scope_requires_indented_child_items(self) -> None:
        self.initialize()
        path = self.root / "doc/protocol/approvals/understanding-approved.md"
        path.parent.mkdir(parents=True)
        path.write_text(
            "# 人类批准：最低理解标准\n\n"
            "- 批准人：负责人\n"
            "- 批准时间（ISO8601）：2026-08-14T00:00:00+00:00\n"
            "- 批准范围：\n"
            "- src\n",
            encoding="utf-8",
        )
        decision = protocol_guard.evaluate(self.payload(self.source))
        self.assertFalse(decision.allowed)

    def test_valid_exemption_allows_matching_path(self) -> None:
        self.initialize()
        now = datetime(2026, 8, 14, tzinfo=timezone.utc)
        self.exemption("src/main.py", now + timedelta(days=1))
        decision = protocol_guard.evaluate(self.payload(self.source), now=now)
        self.assertTrue(decision.allowed)

    def test_expired_exemption_blocks_write(self) -> None:
        self.initialize()
        now = datetime(2026, 8, 14, tzinfo=timezone.utc)
        self.exemption("src", now - timedelta(seconds=1))
        decision = protocol_guard.evaluate(self.payload(self.source), now=now)
        self.assertFalse(decision.allowed)

    def test_invalid_guard_fails_closed(self) -> None:
        self.initialize("not json")
        decision = protocol_guard.evaluate(self.payload(self.source))
        self.assertFalse(decision.allowed)
        self.assertIn("fail-closed", decision.reason)

    # ── PR 1: main() fail-OPEN 改为 return 0 + stderr 告警 ──

    def test_main_empty_stdin_returns_zero_with_stderr(self) -> None:
        """空 stdin：无法判断 target/cwd → 放行 + stderr 告警（修正后 fail-OPEN 策略）。

        归因：解析失败 = 不知道这次操作是否针对 protocol 项目 → 不应误伤所有无关 Edit/Write。
        """
        import subprocess
        proc = subprocess.run(
            [sys.executable, str(GUARD_PATH)],
            input="", capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("stdin empty", proc.stderr)

    def test_main_bad_json_returns_zero_with_stderr(self) -> None:
        """损坏 JSON：放行 + stderr 告警。"""
        import subprocess
        proc = subprocess.run(
            [sys.executable, str(GUARD_PATH)],
            input="{not json", capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("not valid JSON", proc.stderr)

    def test_main_payload_not_dict_returns_zero_with_stderr(self) -> None:
        """payload 不是 dict（如数组）：放行 + stderr 告警。"""
        import subprocess
        proc = subprocess.run(
            [sys.executable, str(GUARD_PATH)],
            input="[1,2,3]", capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("must be a JSON object", proc.stderr)

    # ── PR 3: expiry 分级 + 范围约束修正 ──

    def test_approval_personal_project_no_expiry_required(self) -> None:
        """个人/实验项目：批准人不填 expiry，批准仍生效（不再误伤单人项目）。"""
        self.initialize()
        self._write_questionnaire_with_level("个人 / 实验项目")
        path = self.root / "doc/protocol/approvals/understanding-approved.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "# 人类批准：最低理解标准\n\n"
            "- 批准人：canyu\n"
            "- 批准时间（ISO8601）：2026-08-14T00:00:00+00:00\n"
            # 故意不填批准到期
            "- 批准范围：\n"
            "  - src\n",
            encoding="utf-8",
        )
        decision = protocol_guard.evaluate(self.payload(self.source))
        self.assertTrue(decision.allowed)

    def test_approval_production_project_expires_after_90_days(self) -> None:
        """生产级项目：批准到期默认 90 天，过期后拒绝。"""
        self.initialize()
        self._write_questionnaire_with_level("已上线生产级项目")
        path = self.root / "doc/protocol/approvals/understanding-approved.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "# 人类批准：最低理解标准\n\n"
            "- 批准人：负责人\n"
            "- 批准时间（ISO8601）：2026-08-14T00:00:00+00:00\n"
            # 故意不填批准到期 → 默认 90 天
            "- 批准范围：\n"
            "  - src\n",
            encoding="utf-8",
        )
        # 89 天后仍有效
        almost_expired = datetime(2026, 11, 10, tzinfo=timezone.utc)
        decision = protocol_guard.evaluate(self.payload(self.source), now=almost_expired)
        self.assertTrue(decision.allowed)
        # 91 天后过期
        expired = datetime(2026, 11, 12, tzinfo=timezone.utc)
        decision = protocol_guard.evaluate(self.payload(self.source), now=expired)
        self.assertFalse(decision.allowed)

    def test_approval_team_project_expires_after_90_days(self) -> None:
        """团队内部可控项目：与生产级一致，90 天默认过期。"""
        self.initialize()
        self._write_questionnaire_with_level("团队内部可控系统")
        path = self.root / "doc/protocol/approvals/understanding-approved.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "# 人类批准：最低理解标准\n\n"
            "- 批准人：负责人\n"
            "- 批准时间（ISO8601）：2026-08-14T00:00:00+00:00\n"
            "- 批准范围：\n"
            "  - src\n",
            encoding="utf-8",
        )
        expired = datetime(2026, 11, 12, tzinfo=timezone.utc)
        decision = protocol_guard.evaluate(self.payload(self.source), now=expired)
        self.assertFalse(decision.allowed)

    def test_scope_normalization_rejects_parent_traversal(self) -> None:
        """`../src` 在新版归一化下被识别为非法 scope（防语义误解，非防逃逸）。

        注意：原 lstrip('./') 会字符集剥离导致 '../src' → 'src' 静默匹配项目根内 src。
        新版用 Path.parts 检测 .. 段，返回空，scope 不匹配 → 拒绝。
        """
        self.initialize()
        path = self.root / "doc/protocol/approvals/understanding-approved.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "# 人类批准：最低理解标准\n\n"
            "- 批准人：负责人\n"
            "- 批准时间（ISO8601）：2026-08-14T00:00:00+00:00\n"
            "- 批准范围：\n"
            "  - ../src\n",
            encoding="utf-8",
        )
        # ../src 不应静默匹配项目根内的 src/，应被拒
        decision = protocol_guard.evaluate(self.payload(self.source))
        self.assertFalse(decision.allowed)

    # ── 辅助方法 ──

    def _write_questionnaire_with_level(self, level_marker: str) -> None:
        """在 00-基础调查问卷.md 第 5 节写入指定等级标记。"""
        q = self.root / "doc/protocol/00-基础调查问卷.md"
        if not q.exists():
            q.parent.mkdir(parents=True, exist_ok=True)
            q.write_text("", encoding="utf-8")
        text = q.read_text(encoding="utf-8")
        # 注入最小可触发识别结构（用层级 marker，模拟问卷勾选）
        if level_marker not in text:
            # 直接追加到问卷末尾
            with q.open("a", encoding="utf-8") as f:
                f.write(f"\n- {level_marker}\n")


if __name__ == "__main__":
    unittest.main()
