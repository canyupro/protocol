from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "init_project_area.py"
SPEC = importlib.util.spec_from_file_location("init_project_area", SCRIPT_PATH)
assert SPEC and SPEC.loader
init_project_area = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = init_project_area
SPEC.loader.exec_module(init_project_area)

GUARD_SCRIPT = Path(__file__).resolve().parents[1] / "hooks" / "protocol_guard.py"


class InitProjectAreaTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / ".git").mkdir()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    # ── helper ──
    def _run_main(self, *extra_args: str) -> int:
        """通过 subprocess 调 main()，隔离 argv 与 stdout 噪音。"""
        import subprocess
        proc = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(self.root), *extra_args],
            capture_output=True, text=True, timeout=10,
        )
        # 缓存最近一次结果供调试
        self._last_main_stdout = proc.stdout
        self._last_main_stderr = proc.stderr
        return proc.returncode

    def test_initialize_creates_skeleton_without_guard_or_approvals(self) -> None:
        created = init_project_area.initialize(self.root)
        self.assertIn(Path("doc/protocol/00-基础调查问卷.md"), created)
        self.assertTrue((self.root / "doc/protocol/understanding/architecture.drawio").exists())
        self.assertTrue((self.root / ".agents/protocol/task.md").exists())
        self.assertFalse((self.root / ".agents/protocol/guard.json").exists())
        self.assertFalse((self.root / "doc/protocol/approvals").exists())

    def test_initialize_is_idempotent_and_preserves_existing_files(self) -> None:
        questionnaire = self.root / "doc/protocol/00-基础调查问卷.md"
        questionnaire.parent.mkdir(parents=True)
        questionnaire.write_text("已有问卷\n", encoding="utf-8")
        created = init_project_area.initialize(self.root)
        self.assertNotIn(Path("doc/protocol/00-基础调查问卷.md"), created)
        self.assertEqual(questionnaire.read_text(encoding="utf-8"), "已有问卷\n")
        self.assertEqual(init_project_area.initialize(self.root), [])

    def test_find_root_walks_up_to_git(self) -> None:
        nested = self.root / "a/b/c"
        nested.mkdir(parents=True)
        self.assertEqual(init_project_area.find_root(nested), self.root.resolve())

    def test_guard_enable_rejects_preexisting_approvals(self) -> None:
        init_project_area.initialize(self.root)
        approvals = self.root / "doc/protocol/approvals"
        approvals.mkdir(parents=True)
        (approvals / "understanding-approved.md").write_text("伪造批准\n", encoding="utf-8")
        self.assertEqual(init_project_area.enable_guard(self.root), "blocked")
        self.assertFalse((self.root / ".agents/protocol/guard.json").exists())

    def test_guard_enable_is_idempotent_after_creation(self) -> None:
        init_project_area.initialize(self.root)
        self.assertEqual(init_project_area.enable_guard(self.root), "created")
        self.assertEqual(init_project_area.enable_guard(self.root), "exists")

    def test_project_hook_idempotent(self) -> None:
        """write_project_hook 独立调用幂等（hook-only 流程依赖它）。"""
        init_project_area.initialize(self.root)
        self.assertFalse((self.root / ".zcode/config.json").exists())
        self.assertTrue(init_project_area.write_project_hook(self.root))
        config = (self.root / ".zcode/config.json").read_text(encoding="utf-8")
        self.assertIn("PreToolUse", config)
        self.assertIn("protocol_guard.py", config)
        self.assertIn("\"timeoutMs\": 5000", config)
        self.assertFalse(init_project_area.write_project_hook(self.root))

    # ── PR 2: flag 合并 + --read-only ──

    def test_default_args_create_both_guard_and_hook(self) -> None:
        """不传任何 flag：默认双开 guard.json + .zcode/config.json。"""
        init_project_area.initialize(self.root)
        rc = self._run_main()
        self.assertEqual(rc, 0)
        self.assertTrue((self.root / ".agents/protocol/guard.json").exists())
        self.assertTrue((self.root / ".zcode/config.json").exists())
        payload = json.loads((self.root / ".agents/protocol/guard.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "pending")
        self.assertNotIn("intent", payload)

    def test_explicit_guard_on_and_hook_on_same_as_default(self) -> None:
        """--guard on --hook on 与默认行为一致。"""
        init_project_area.initialize(self.root)
        rc = self._run_main("--guard", "on", "--hook", "on")
        self.assertEqual(rc, 0)
        self.assertTrue((self.root / ".agents/protocol/guard.json").exists())
        self.assertTrue((self.root / ".zcode/config.json").exists())

    def test_guard_only_skips_hook(self) -> None:
        """--guard-only：只创建 guard.json，不写 .zcode/config.json。"""
        init_project_area.initialize(self.root)
        rc = self._run_main("--guard-only")
        self.assertEqual(rc, 0)
        self.assertTrue((self.root / ".agents/protocol/guard.json").exists())
        self.assertFalse((self.root / ".zcode/config.json").exists())

    def test_hook_only_writes_config_without_guard(self) -> None:
        """--hook-only：只写 .zcode/config.json，不创建 guard.json。
        hook 会持续 fail-closed，应有 stderr 警告。"""
        init_project_area.initialize(self.root)
        rc = self._run_main("--hook-only")
        self.assertEqual(rc, 0)
        self.assertFalse((self.root / ".agents/protocol/guard.json").exists())
        self.assertTrue((self.root / ".zcode/config.json").exists())

    def test_hook_only_warns_to_stderr(self) -> None:
        init_project_area.initialize(self.root)
        import subprocess
        proc = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(self.root), "--hook-only"],
            capture_output=True, text=True, timeout=10,
        )
        self.assertIn("fail-closed", proc.stderr)
        self.assertIn("--guard=on", proc.stderr)

    def test_guard_off_no_guard_no_hook(self) -> None:
        """--guard off：不创建 guard.json；同时 hook-on 也写，但 hook 永远跑空（罕见，但可选）。"""
        init_project_area.initialize(self.root)
        rc = self._run_main("--guard", "off")
        self.assertEqual(rc, 0)
        self.assertFalse((self.root / ".agents/protocol/guard.json").exists())
        # 默认 hook=on，仍写 .zcode/config.json
        self.assertTrue((self.root / ".zcode/config.json").exists())

    def test_read_only_creates_observe_only_guard_without_hook(self) -> None:
        """--read-only：公司项目场景，只生成 intent=observe-only 的 guard.json，不写 .zcode/config.json。"""
        init_project_area.initialize(self.root)
        rc = self._run_main("--read-only")
        self.assertEqual(rc, 0)
        self.assertTrue((self.root / ".agents/protocol/guard.json").exists())
        self.assertFalse((self.root / ".zcode/config.json").exists())
        payload = json.loads((self.root / ".agents/protocol/guard.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "pending")
        self.assertEqual(payload["intent"], "observe-only")

    def test_read_only_with_guard_off_overrides_to_observe_only(self) -> None:
        """--read-only 与 --guard off 同时出现：忽略 --guard off，强制 enable observe-only guard。"""
        init_project_area.initialize(self.root)
        rc = self._run_main("--read-only", "--guard", "off")
        self.assertEqual(rc, 0)
        self.assertTrue((self.root / ".agents/protocol/guard.json").exists())
        payload = json.loads((self.root / ".agents/protocol/guard.json").read_text(encoding="utf-8"))
        self.assertEqual(payload["intent"], "observe-only")

    def test_read_only_warns_to_stderr(self) -> None:
        """--read-only 输出 stderr 说明。"""
        init_project_area.initialize(self.root)
        import subprocess
        proc = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--root", str(self.root), "--read-only"],
            capture_output=True, text=True, timeout=10,
        )
        self.assertIn("observe-only", proc.stderr)


if __name__ == "__main__":
    unittest.main()
