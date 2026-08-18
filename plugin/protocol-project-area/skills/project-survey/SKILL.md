---
name: project-survey
description: Confirm a Protocol base survey, choose new-project or legacy-intervention mode, and create the first task state.
---

# 基础调查问卷确认

读取 `doc/protocol/00-基础调查问卷.md`、`.agents/protocol/task.md` 和 `.agents/protocol/map.md`，通过对话补齐未确认项。

## 必须确认

- 模式：新启动 / 存量介入。
- 当前任务、交付物、明确不做什么。
- 读、写、执行、测试、环境、数据、发布权限。
- 项目等级、人类负责人、可询问维护者与升级条件。
- 验收证据、人类可兜底边界、风险和待确认项。

确认后只更新任务和映射文档；不得自行创建批准或豁免。用户确认问卷和根 `AGENTS.md` 短指针后，才可通过初始化脚本 `--enable-guard` 建立 pending guard。存量介入进入执行前必须产出整体架构图、数据流动和命名规范，并由独立验证方审查。
