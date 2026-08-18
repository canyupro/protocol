---
name: legacy-intervention
description: Apply the Protocol legacy-intervention workflow after the base survey confirms a task-driven unfamiliar project intervention.
---

# 存量介入模式

存量介入必须任务驱动。仅使用项目不构成介入。

执行前达到最低理解标准并文档化：

1. `doc/protocol/understanding/architecture.drawio`：整体架构图。
2. `doc/protocol/understanding/data-flow.drawio`：任务相关数据流。
3. `doc/protocol/understanding/naming.md`：命名规范、局部约定和历史例外。

README 和文件名只是线索。用入口、配置、依赖、测试和关键实现交叉验证。图中区分 `[已验证]`、`[假设]`、`[待确认]`；任务范围、系统复杂度和权限决定图谱与文档的拆分粒度。

涉及人类不可兜底的责任边界时，暂停并按任务文档升级确认。代码写入只有在人类批准或有效书面豁免后才可进行。
