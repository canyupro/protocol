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


def enable_guard(root: Path, mode: str = "standard") -> str:
    """创建 pending guard，返回 created / exists / blocked。

    mode:
      - standard: 默认 guard.json（status=pending），由 has_matching_approval 决定拦截
      - read-only: 公司项目/纯只读场景，guard.json intent=observe-only，
                   守卫层拒绝所有业务路径，但项目区文档可写
    """
    guard = root / ".agents/protocol/guard.json"
    if guard.exists():
        return "exists"
    approvals = root / "doc/protocol/approvals"
    if approvals.exists() and any(approvals.iterdir()):
        return "blocked"
    payload = {"version": 1, "status": "pending"}
    if mode == "read-only":
        payload["intent"] = "observe-only"
    dest = root / ".agents/protocol/guard.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    import json as _json
    dest.write_text(_json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
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
              "timeoutMs": 5000,
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


def read_only_mode_enabled(args: argparse.Namespace) -> bool:
    """检测 --read-only 是否开启。"""
    return bool(getattr(args, "read_only", False))


def main() -> int:
    parser = argparse.ArgumentParser(description="创建 Protocol 项目区骨架")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="项目根或其子目录")
    # ── 守卫三档策略：guard-mode × hook-mode × --read-only ──
    # 默认：guard=auto（已有 approvals 则不创建）+ hook=on
    # 修正版：默认双开——guard 必须搭配 hook 才有意义（appcode-fend 翻车教训）
    parser.add_argument(
        "--guard", "--enable-guard",
        dest="guard_mode",
        choices=["on", "off", "auto"],
        default="auto",
        help="guard.json 创建策略：on=无条件创建 / off=不创建 / auto=已有 approvals 时拒绝（默认）",
    )
    parser.add_argument(
        "--hook", "--project-hook",
        dest="hook_mode",
        choices=["on", "off"],
        default="on",
        help=".zcode/config.json 创建策略，默认 on",
    )
    parser.add_argument(
        "--guard-only",
        action="store_const",
        dest="hook_mode",
        const="off",
        help="只创建 guard.json，不写 .zcode/config.json",
    )
    parser.add_argument(
        "--hook-only",
        action="store_const",
        dest="guard_mode",
        const="off",
        help="只写 .zcode/config.json，不创建 guard.json（不推荐：hook 会持续 fail-closed）",
    )
    parser.add_argument(
        "--read-only",
        action="store_true",
        help="公司项目/纯只读场景：跳过 hook 安装，生成 intent=observe-only 的 guard.json（业务路径一律 deny）",
    )
    args = parser.parse_args()
    root = find_root(args.root)

    # read-only 与 hook-only 互斥：read-only 明确跳过 hook
    if args.read_only and args.hook_mode == "on" and args.guard_mode != "off":
        # 那就照常生成 hook，让用户在客户端决定是否信任（observe-only 即使 hook 被信任也只放行项目区文档）
        pass

    created = initialize(root)

    # read-only 模式：创建 observe-only guard，跳过 hook
    if args.read_only:
        if args.guard_mode == "off":
            print("--read-only 与 --guard=off 互斥；忽略 --guard=off，强制启用 observe-only guard。", file=sys.stderr)
        guard_result = enable_guard(root, mode="read-only")
        if guard_result == "blocked":
            print("拒绝启用 guard：审批目录在守卫启用前已存在内容，请由人类检查后重新初始化。", file=sys.stderr)
            return 2
        if guard_result == "created":
            created.append(Path(".agents/protocol/guard.json"))
        print("[read-only] 已生成 observe-only guard；不安装 hook（公司项目/纯只读场景）。", file=sys.stderr)
        # 跳过 hook 创建
    else:
        # 标准模式：按 guard-mode + hook-mode 创建
        if args.guard_mode != "off":
            guard_result = enable_guard(root, mode="standard")
            if guard_result == "blocked":
                print("拒绝启用 guard：审批目录在守卫启用前已存在内容，请由人类检查后重新初始化。", file=sys.stderr)
                return 2
            if guard_result == "created":
                created.append(Path(".agents/protocol/guard.json"))
        if args.hook_mode == "on":
            if args.guard_mode == "off":
                # hook-only 警告：hook 会持续 fail-closed
                print(
                    "WARNING: --hook-only 让 hook 持续 fail-closed（找不到 guard.json）；"
                    "仅用于调试。请补一个 --guard=on。",
                    file=sys.stderr,
                )
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
