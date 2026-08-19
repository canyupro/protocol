from __future__ import annotations

import importlib.util
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


class InitProjectAreaTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / ".git").mkdir()

    def tearDown(self) -> None:
        self.tempdir.cleanup()

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

    def test_project_hook_created_only_with_guard(self) -> None:
        init_project_area.initialize(self.root)
        self.assertFalse((self.root / ".zcode/config.json").exists())
        self.assertTrue(init_project_area.write_project_hook(self.root))
        config = (self.root / ".zcode/config.json").read_text(encoding="utf-8")
        self.assertIn("PreToolUse", config)
        self.assertIn("protocol_guard.py", config)
        # 幂等：已存在不覆盖
        self.assertFalse(init_project_area.write_project_hook(self.root))


if __name__ == "__main__":
    unittest.main()
