---
name: independent-verification
description: Produce a read-only independent verification package for Protocol understanding evidence and task boundaries.
---

# 独立验证任务包

独立验证方只“看 + 判 + 说”，不设计、不施工、不补写理解答案、不批准、不修改 guard。

验证任务包必须直接列出仓库路径、问卷、任务、三项理解文档、证据来源、当前项目规则和测试入口。检查：

1. 整体架构图、数据流动、命名规范是否齐全且可复核。
2. 是否将假设误写为事实。
3. 任务、权限、人类可兜底边界和升级路径是否明确。
4. 是否允许进入代码执行。

规则来源、输入材料、判断权限和输出通道不得由被检察施工方控制。优先由用户配置的 `testcoder` 在独立上下文执行；没有时将任务包直接交给用户在独立会话执行。
