---
description: 基于已确认问卷开始新启动或存量介入流程
argument-hint: "[补充任务说明]"
skills: project-survey
---

使用 `project-survey` skill 读取并确认基础调查问卷，然后开始对应模式的第一轮。

**自动写入流程元数据**：确认问卷后，agent 必须用 `date +%Y-%m-%dT%H:%M:%S%z` 拿当前时间写入：
- `.agents/protocol/task.md` 的 `## 任务生命周期` 段：`开始时间`（ISO8601）+ `发起方`（`human` / `agent-auto` / `scheduled`）+ `当前会话 ID`（agent 父会话 ID）
- `.agents/protocol/map.md` 的 `## 流程元数据` 段：`最近一次 begin` + `最近一次发起方` + `最近一次会话 ID` + `上一次 begin`

若已有 `开始时间` / `最近一次 begin`，**不得覆盖**，仅追加新会话 ID 与时间。

$ARGUMENTS
