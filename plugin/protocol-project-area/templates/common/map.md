# 项目区文件映射

> 本文件只连接 Protocol 项目区关键资产，不生成全仓 INDEX。

## 流程元数据

> 由 agent 在 `/protocol:begin` 时自动写入，禁止手填覆盖。

- 最近一次 begin：YYYY-MM-DDTHH:MM:SSZ
- 最近一次发起方：human / agent-auto / scheduled
- 最近一次会话 ID：
- 上一次 begin：YYYY-MM-DDTHH:MM:SSZ

## 项目规则与入口

| 类别 | 路径 | 状态/说明 |
|---|---|---|
| 项目根规则 | `AGENTS.md` | |
| 局部规则 | | |
| README | `README.md` | |
| 构建入口 | | |
| 测试入口 | | |

## Protocol 项目区

| 资产 | 路径 | 状态 |
|---|---|---|
| 基础调查问卷 | `doc/protocol/00-基础调查问卷.md` | 待确认 |
| 当前任务与权限 | `.agents/protocol/task.md` | 待补充 |
| 整体架构图 | `doc/protocol/understanding/architecture.drawio` | 待验证 |
| 数据流动 | `doc/protocol/understanding/data-flow.drawio` | 待验证 |
| 命名规范 | `doc/protocol/understanding/naming.md` | 待验证 |
| 影响面 | `doc/protocol/impact/` | 待补充 |
| 独立验证报告 | `.agents/protocol/verification/understanding-review.md` | 待审查 |
| 人类批准/豁免 | `doc/protocol/approvals/` | 未签发 |
| 守卫状态 | `.agents/protocol/guard.json` | pending |
