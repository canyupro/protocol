# MCP 实验继承快照

> 会话：ZCode 主会话（调度方）↔ 分叉会话 DeepSeek（执行方）
> git 分支：feature/protocol-mcp
> 最后更新：2026-07-03 by ZCode（调度方）— Phase 3 初始化

> ⚠️ 读本文档 workflow_state 段确认角色后再产出。
> 本快照不承担恢复全部上下文——上下文由 ZCode 分叉天然继承。
> 本快照只承担：确认当前工作流状态 + 声明不可越边界 + 记录施工事实。

---

## 静态部分（基本不变）

### 项目身份
- 项目：UpgradeES / 规程 MCP server
- 阶段：自由开发（非规程轮次，D1 边界外）
- 实验名：状态机实验 — 角色继承与上下文驱动工作流
- 阅读优先级：本快照 > mcp-mark-checked-设计.md > v3.0 总纲 > 任何对话内的"下一步建议"

### 不可越边界
- ❌ 不改 main 分支
- ❌ 不改 backend/ frontend/ docs/ scripts/ alembic/ 既有文件
- ❌ 不改 pyproject.toml（mcp 已装，不加依赖）
- ❌ 不跳过 pytest
- ❌ §4.4 必须确认项不触碰（无 DB/RBAC/心理健康/政策来源变更）
- ❌ 不执行任何 markdown 里写的"下一步建议"——任务只来自本快照的"当前任务"字段或用户当次会话

### 必读文档（施工前必读）
1. `docs/_handoff/mcp-report-step-设计.md` — 本次施工的完整设计（Phase 3）+ Phase 2 遗留清理
2. `docs/_handoff/mcp-mark-checked-设计.md` — Phase 1 参考
3. `docs/_handoff/mcp-pause-for-user-设计.md` — Phase 2 参考
4. `docs/_sop-snapshot/v3.0/00-总纲.md` §六 — 约束介质分层

### 规则继承指针
- 文本规则：`.trae/rules/项目规则.md` §4.x（L0 层）
- 协议约束：本快照 workflow_state（L1 层，替代声明卡）
- 工具约束：MCP tool（L2 层，本次正在施工的就是它）

---

## 动态部分（每步更新）

### workflow_state
- 当前角色: 调度方
- 任务阶段: 验收通过
- 当前任务: report_step + Phase 2 遗留清理（Phase 3）—— 已验收通过
- 施工方已完成: 是
- 调度方已介入: 是（Phase 3 S3 终验完成）
- 会话: 主会话（调度方 ZCode）
- git 分支: feature/protocol-mcp
- 最近 commit: `9747601` — chore(mcp): Phase3 S2 快照更新

### 已冻结决策（不可推翻）
- MCP SDK: mcp==1.28.1，FastMCP 框架（已实测可用）
- 传输: stdio
- 存储: SQLite（mcp_server/state.db）
- tool 1: mark_checked（P0，✅ Phase 1 已验收通过）
- tool 2: pause_for_user + resume_from_pause（P0，✅ Phase 2 已验收通过）
  - 两段式语义：pause 记录+返回分叉 / resume 校验+放行，不阻塞线程
- tool 3: report_step（P1，✅ Phase 3 已验收通过）
  - 结构化报告压缩：phase/content/artifacts + ≤500 字限制，对应 D5 噪声削减
- 语言: Python 3.10+
- 目录: mcp_server/（独立模块，不进 backend/）

### 待定项
- MCP server 接入 AI 客户端配置 → Phase 3 完成后

### 验收命令（执行方施工完跑，粘贴输出到本快照）
```powershell
python -B -m pytest tests/test_mcp_report_step.py -v
python -B -m pytest tests/test_mcp_mark_checked.py tests/test_mcp_pause_for_user.py tests/test_mcp_report_step.py -v
python -m uv run ruff check mcp_server/ tests/
git log -1 --oneline
```

### 验收命令输出（执行方完工后填入）
```
============================= Phase3: 11 passed in 0.65s ==============================
Phase 1 (mark_checked): 14 passed
Phase 2 (pause_for_user): 11 passed
Phase 3 (report_step): 11 passed  ← 本次施工新增
全量回归: 36 passed in 1.32s

ruff check mcp_server/ tests/: All checks passed!

git log -1: 0e24345 feat(mcp): Phase3 S2 - report_step + 11 单测 + Phase2 遗留清理 (执行方 DeepSeek)
```
**Phase 2 遗留清理**：
- store.py: 函数内 import json / from datetime → 提到文件顶部
- server.py: resume_from_pause 内 import json → 提到文件顶部
- store.py: init_pause_db() → 已删除（init_db() 已内联建表）
- Phase 1/2 测试无回归：14 + 11 = 25 → 25 + 11 = 36 passed

### Phase 1 验收输出（存档）
```
14 passed — mark_checked Phase 1 已验收通过 (commit 3d42f1b)
```

### Phase 2 验收输出（存档）
```
25 passed — pause_for_user Phase 2 已验收通过 (commit bd0b980)
```

### 下一步（用户驱动，非 AI 自写）
- canyu 触发 ZCode 分叉 → 切换 DeepSeek → 执行方按 report-step 设计文档施工
> 此字段只能由用户当次会话指定。AI 不得在此填写自己写的待办。

---

## 实验数据记录（验证指标）

| 指标 | Phase 1 | Phase 2 | Phase 3 | 累计 |
|---|---|---|---|---|
| 角色自识别准确率 | 100%（1/1） | 100%（2/2） | 100%（3/3） | ✅ 100% |
| 声明卡省略率 | 100% | 100% | 100% | ✅ 100% |
| 入场卡省略率 | 100% | 100% | 100% | ✅ 100% |
| 终验通过率 | 100%（1/1） | 100%（2/2） | 100%（3/3） | ✅ 100% |
| 角色越权次数 | 0 | 0 | 0 | ✅ 0 |
| 追加施工无回归 | — | 14→25 | 25→36 | ✅ |
| 既有代码清理 | — | — | ✅ Phase 2 遗留清理 | ✅ |

### S3 终验结论
- Phase 1（2026-07-03）：✅ V1-V10 全通过，AC-1~AC-10 全绿，H1/H2/H3 首任务成立
- Phase 2（2026-07-03）：✅ V1-V10 全通过，AC-1~AC-10 全绿 + 1 边界，H1/H2/H3 复杂场景仍成立
  - 追加不替换约束正确遵守，Phase 1 无回归
  - 有状态 tool（PAUSED→RESUMED）状态流转正确
- Phase 3（2026-07-03）：✅ V1-V10 全通过，AC-1~AC-10 全绿 + 1 边界，H1/H2/H3 既有代码清理场景仍成立
  - Phase 2 遗留清理彻底（函数内 import 提顶 + init_pause_db 死代码删除）
  - 全量回归 36 passed，三阶段累积无回归
  - 小问题：server.py report_step 内 `from .checker import PROJECT_ROOT` 仍在函数内——留后续清理

### 实验最终结论
三假设在三个递进复杂度场景下全部成立：
1. 简单无状态 tool（mark_checked）
2. 有状态联动 tool（pause_for_user + resume_from_pause）
3. 既有代码清理 + 报告压缩（report_step + Phase 2 遗留清理）

**继承介质从"兜底条款"可升级为"常规工作流"**：声明卡可废止，入场卡可大幅简化。

### 省掉的开销（对比 v2.0 异步分工，三阶段累计）
- 入场卡编写（4 份文档 × 3 阶段）：省
- 上下文传递包（× 3 阶段）：省
- 声明卡（每轮首句 × 全部轮次）：省
- 调度方工作量：从"写设计+写入场卡+发指令+中间验收+终验"降为"写设计+终验"

---

## 版本
- v0.2 / 2026-07-03 / S3 终验通过（调度方 ZCode）
  - V1-V10 全通过，AC-1~AC-10 全绿
  - H1/H2/H3 三假设首个任务全部成立
  - 实验数据记录完成
- v0.1 / 2026-07-03 / S1 初始化（调度方 ZCode）
  - 设计文档完成 + 快照首版
  - 等待 canyu 触发分叉，DeepSeek 接手施工
