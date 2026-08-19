#!/usr/bin/env python3
"""创建 Protocol 项目区骨架。

该脚本只复制不存在的项目区模板，绝不修改已有 AGENTS.md、README、业务代码、
批准、豁免或 guard 状态。guard 只能在问卷确认和 AGENTS 指针确认之后显式启用。
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = PLUGIN_ROOT / "templates" / "common"

COPY_MAP = {
    "00-基础调查问卷.md": Path("doc/protocol/00-基础调查问卷.md"),
    "README.md": Path("doc/protocol/README.md"),
    "task.md": Path(".agents/protocol/task.md"),
    "map.md": Path(".agents/protocol/map.md"),
    "understanding-review.md": Path(".agents/protocol/verification/understanding-review.md"),
    "architecture.drawio": Path("doc/protocol/understanding/architecture.drawio"),
    "data-flow.drawio": Path("doc/protocol/understanding/data-flow.drawio"),
    "naming.md": Path("doc/protocol/understanding/naming.md"),
}


def find_root(start: Path) -> Path:
    for candidate in (start.resolve(), *start.resolve().parents):
        if (candidate / ".git").exists():
            return candidate
    return start.resolve()


def copy_if_missing(source: Path, destination: Path) -> bool:
    if destination.exists():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    return True


def initialize(root: Path) -> list[Path]:
    created: list[Path] = []
    for template_name, relative_path in COPY_MAP.items():
        destination = root / relative_path
        if copy_if_missing(TEMPLATES / template_name, destination):
            created.append(relative_path)

    for relative_path in (
        Path("doc/protocol/impact/.gitkeep"),
        Path("doc/protocol/tasks/.gitkeep"),
        Path("doc/protocol/reviews/.gitkeep"),
    ):
        destination = root / relative_path
        if not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text("", encoding="utf-8")
            created.append(relative_path)

    return created


def enable_guard(root: Path) -> str:
    """创建 pending guard，返回 created / exists / blocked。"""
    guard = root / ".agents/protocol/guard.json"
    if guard.exists():
        return "exists"
    approvals = root / "doc/protocol/approvals"
    if approvals.exists() and any(approvals.iterdir()):
        return "blocked"
    copy_if_missing(TEMPLATES / "guard.json", guard)
    return "created"


PROJECT_HOOK_TEMPLATE = """{{
  "hooks": {{
    "enabled": true,
    "events": {{
      "PreToolUse": [
        {{
          "matcher": "Edit|Write",
          "hooks": [
            {{
              "type": "process",
              "command": "python3",
              "args": ["{guard_script}"],
              "timeoutMs": 1000,
              "statusMessage": "Checking Protocol project-area write guard"
            }}
          ]
        }}
      ]
    }}
  }}
}}
"""


def write_project_hook(root: Path, guard_script: Path | None = None) -> bool:
    """生成项目区 `.zcode/config.json`（PreToolUse → 守卫脚本）。

    守卫脚本默认取插件内 hooks/protocol_guard.py 的绝对路径；也可传入项目内副本。
    仅由人类在客户端完成「工作区 Hook 信任」后才生效，脚本不绕过。
    """
    if guard_script is None:
        guard_script = PLUGIN_ROOT / "hooks" / "protocol_guard.py"
    destination = root / ".zcode" / "config.json"
    if destination.exists():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(PROJECT_HOOK_TEMPLATE.format(guard_script=guard_script), encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="创建 Protocol 项目区骨架")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="项目根或其子目录")
    parser.add_argument(
        "--enable-guard",
        action="store_true",
        help="仅在用户确认问卷和 AGENTS 短指针后创建 pending guard",
    )
    parser.add_argument(
        "--project-hook",
        action="store_true",
        help="启用 guard 时同时生成项目区 .zcode/config.json（PreToolUse → 守卫脚本）",
    )
    args = parser.parse_args()
    root = find_root(args.root)
    created = initialize(root)
    if args.enable_guard:
        guard_result = enable_guard(root)
        if guard_result == "blocked":
            print("拒绝启用 guard：审批目录在守卫启用前已存在内容，请由人类检查后重新初始化。", file=sys.stderr)
            return 2
        if guard_result == "created":
            created.append(Path(".agents/protocol/guard.json"))
        if args.project_hook:
            if write_project_hook(root):
                created.append(Path(".zcode/config.json"))
            else:
                print("已存在 .zcode/config.json，未覆盖；请人工检查其 hook 是否指向 Protocol 守卫。", file=sys.stderr)
    print(f"项目根: {root}")
    if created:
        print("已创建:")
        for path in created:
            print(f"- {path.as_posix()}")
    else:
        print("项目区骨架已存在，未覆盖任何文件")
    print("下一步：读取问卷并征得用户确认后，再人工确认 AGENTS.md 短指针。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
