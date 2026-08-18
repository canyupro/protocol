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


if __name__ == "__main__":
    unittest.main()
