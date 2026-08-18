---
name: project-area-init
description: Initialize the Protocol project area in an existing or new workspace. Use for /protocol:init.
---

# Protocol 项目区初始化

仅在用户显式执行 `/protocol:init` 后初始化。插件安装本身绝不改项目。

## 初始化顺序

1. 从当前目录向上发现 `.git`；找到的目录是项目根。找不到时说明 cwd 作为候选根并请用户确认。
2. 读取用户全局 `AGENTS.md`、项目根和当前子目录链上的已有 `AGENTS.md`、根 README、可读的构建和测试配置。只提取项目差异事实，不复制全局规则，不读取敏感配置。
3. 先创建 `doc/protocol/00-基础调查问卷.md`、`doc/protocol/README.md`、`.agents/protocol/task.md`、`.agents/protocol/map.md`、理解文档骨架和验证报告骨架。初始化阶段不得创建 `doc/protocol/approvals/`；批准和豁免模板只保留在全局插件包中。使用插件 `templates/common/` 的模板作为唯一来源。
4. 根据已读事实预填问卷，所有推断标为 `[假设]`，不把目录名或 README 单独当作事实。
5. 若已有根 `AGENTS.md`，展示拟追加的 Protocol 项目区短指针和差异，必须等用户明确确认后才追加。若不存在，则创建最小根 `AGENTS.md`。
6. `/protocol:init` 到此只创建骨架，不创建 guard。用户确认问卷并确认根 `AGENTS.md` 短指针后，使用插件脚本的 `--enable-guard` 显式创建 `.agents/protocol/guard.json`，内容必须是插件模板提供的固定 pending 状态。创建后，代码写入守卫开始生效。

## 不可违反边界

- 不覆盖现有 `AGENTS.md`、README、项目文档或配置。
- 不自行填写 `doc/protocol/approvals/`；批准和豁免仅由人类在 ZCode 工具路径之外签发。
- 不在问卷未经用户确认前判定项目模式。
- 初始化阶段只写项目区资产，不编辑业务代码。
