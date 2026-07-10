# 02 — 串行对话：Round 3 至 Round 5 与启动门

> 规范制定 → 数据库设计 + 记忆架构 → 框架构造 + SSE 双轨 + 危机短路 → 冻结审计 → 多 Agent 启动门。
> 6 核心文档的完整模板全部在本文件中内联，可直接复制使用。
> 每轮首句须输出模式声明卡（§4.4），每轮结束须更新继承快照（§4.12）。

---

## Round 3: 规范制定

这是本规程最关键的一轮——决定了"AI 能不能稳定执行任务"。

**输入**：目录结构 + 链路 todo + 验收标准 + 技术栈 + 契约冻结文档。

**产出物**（6 核心文档全在这里）：

- `docs/03-agent/AGENTS.md`（核心文档之一）
- `docs/03-agent/Agent 职责划分.md`（核心文档之二）
- `docs/03-agent/Prompt 设计规范.md`（核心文档之三）
- `docs/03-agent/AI Agent Prompt 规范.md`（核心文档之四，§4.17，含 Agent 链路时必产）
- `docs/05-ai-coding/开发规则.md`（5 条不可删规则 + 每条配执行检查项）
- `docs/05-ai-coding/代码规范.md`（命名 / 注释 / 错误处理 / 日志 / 测试）
- `docs/05-ai-coding/CLAUDE.md` + `docs/05-ai-coding/CODEX.md`
- `docs/03-agent/AI Agent 安全边界规范.md`（§4.14，含 Agent 链路时必产）
- `docs/05-ai-coding/前端规范.md`（§4.5，含前端时必产）

**议题清单**：

- AGENTS.md: 团队结构 / 职责 / 协作流程 / 评估标准
- Agent 职责划分: 协调方 / 编码 Agent / 审计 Agent 做/不做
- Prompt 设计规范: 任务模板 / 上下文格式 / 输出格式 / 禁止
- **AI Agent Prompt 规范**（§4.17）: 版本化 / 结构化输出 / 安全约束 / fallback / 反禁止清单
- **AI Agent 安全边界规范**（§4.14）: 敏感字段分层 / 学生端零暴露 / RAG 知识边界 / 评级取严
- **前端规范**（§4.5）: 完成定义 / 视角收束 / 单源 View（详见 08 号文件）
- 开发规则 5 条（不可删）+ 每条配执行检查项
- 代码规范讨论（命名 / 注释 / 错误处理 / 日志 / 测试）
- **声明卡协议**（§4.4）: 每轮首句双向校准
- 检查触发器

---

### AGENTS.md 模板（可直接复制）

```markdown
# AGENTS.md

## 1. 团队结构
- AI 协调员: 派活 / 验收 / 整合，不写业务代码
- 编码 Agent A（链路 1）: [链路名，如 customer]
- 编码 Agent B（链路 2）: [链路名，如 student]
- 编码 Agent C（链路 3）: [链路名，如 ai_chat] [Agent]
- 编码 Agent D（链路 4）: [链路名，如 mental_health] [Agent]

## 2. 职责划分
- 协调方: 不写业务代码，改公共文件
- 编码 Agent: 写 + 自测 + 写链路文档
- 审计: 协调方兼任

## 3. 协作流程
- 阶段 1-7: 协调方独立
- 阶段 8: 协调方立骨架
- 阶段 9: 各 Agent 并行（自己分支）
- 阶段 10: 协调方隔离区合并
- 阶段 11: 协调方发版

## 4. 评估标准（5 维度）
- 代码规范（ruff）
- 动态测试（pytest 真跑）
- 契约一致性（API vs 设计文档）
- 文档完整性（7 层齐）
- 实战复盘（踩坑清单）

## 5. 失败处理
- 单 Agent 失败 → 隔离调试，不破坏骨架
- 整合冲突 → 隔离区解决，不动主分支
- 整体失败 → 回退 + 重新整合
```

---

### Agent 职责划分.md 模板（可直接复制）

```markdown
# Agent 职责划分

## 协调方（AI 协调员）
### 做
- 派活（分配链路任务）
- 验收（5 维度审计）
- 整合（隔离区合并）
- 改公共文件（core/ router.py）
- 写 7 层 docs 公共层
- 写会议纪要

### 不做
- 写业务代码
- 改链路 Agent 白名单外的文件
- 擅自发版（必须 canyu 拍）

## 编码 Agent（每个链路 1 个）
### 做
- 写业务代码（models / schemas / services / api）
- 写测试
- 写链路内文档（_chains/chainN-xxx/）
- 自测 + 跑 pytest
- 必带测试输出在 commit message

### 不做
- 改 core/ router.py 等公共文件
- 改其他链路的文件
- 直接改主目录文档（必须走 _chains/）
- mock 关键路径（LangChain / SSE / 跨链路 HTTP）
- commit message 不带测试输出

## 审计 Agent（协调方兼任）
### 做
- 5 维度审计
- 红黄绿评估
- 实战复盘

## 测试 Agent（协调方兼任）
### 做
- E2E 测试
- 覆盖率检查
- 性能测试（可选）
```

---

### Prompt 设计规范.md 模板（可直接复制）

```markdown
# Prompt 设计规范

## 任务模板
[背景]
[目标]
[输入 / 输出]
[约束]
[完成定义]

## 上下文格式
- 引用文档: 路径必填
- 引用代码: file:line 必填
- 不允许"猜"

## 输出格式
- 改动列表（文件 + 行数）
- 测试结果（pytest 输出）
- 已知问题
- 建议改进

## 禁止
- 不要"顺便"改无关代码
- 不要"我觉得" — 引文档
- 不要"应该可以" — 给证据
```

---

### AI Agent Prompt 规范.md 模板（§4.17，含 Agent 链路时必产）

```markdown
# AI Agent Prompt 规范

## 版本化
- 所有 prompt 写在 ai/chains/* 文件内，git 跟踪
- PROMPT_VERSION 必填（如 k12-supervisor-v1）
- 禁止散落在 service 层

## 结构化输出
- PydanticOutputParser 强制结构化输出
- 失败 fallback + 日志
- structured_response 是最终真相（评级/alert_reason 不走 token）

## 安全约束
- 不贴标签（§4.5 换位思考红线）
- 不暴露 confidence / direction 等内部字段给学生
- alert_reason 必填可解释
- 回复 ≤ 250 字

## Fallback
- LLM 失败 → fallback 文案（温和提示，不抛 500）
- RAG 检索失败 → "未找到相关内容"，不阻塞主流程
- 所有工具兼具 fallback

## 反禁止清单
- 不拼接无关历史
- 不向学生暴露结构化字段
- 不让 Supervisor 下调关键词命中的评级

## Few-shot
- 关键场景配 Few-shot 示例
```

---

### AI Agent 安全边界规范.md 模板（§4.14，含 Agent 链路时必产）

```markdown
# AI Agent 安全边界规范

## 敏感字段分层过滤
| 字段 | 老师端 | 学生端 |
|---|---|---|
| 心理评级（level） | ✅ 可见 | ❌ 零暴露 |
| 告警原因（alert_reason） | ✅ 可见 | ❌ 零暴露 |
| 关键词命中信息 | ✅ 可见 | ❌ 零暴露 |

## 学生端零暴露
- 学生端 SSE token 不含评级 / alert_reason / 关键词命中信息
- 学生端 UI 只展示支持性文案
- 任何形式向学生侧暴露评级信息 = 红线

## RAG 知识边界
- RAG 仅索引机构知识（Policy），不索引学生数据
- 学生历史单独 collection + user_id 强隔离
- A 学生不能召回 B 学生数据

## 心理评级取严
- 关键词兜底优先于 LLM 判断
- red 强制 escalate_to_teacher=True
- LLM 不能下调关键词命中的 red
- merge_with_supervisor_level 永远取更严重评级

## 事实画像撤回
- agent_known_facts 含 retracted_at 字段
- 撤回不删除，标记失效
- 撤回后该事实不再作为决策依据
```

---

### 开发规则.md（5 条不可删，每条配执行检查项）

```markdown
# 开发规则

## 规则 1: 每次只完成一个任务
单 commit 粒度，不跨任务。
执行检查项: commit message 中"任务 ID"必填。

## 规则 2: 禁止修改无关代码
只改任务指定的文件。
执行检查项: git diff 中出现的文件全部在白名单内。

## 规则 3: 新增接口必补接口文档
文档放 _chains/chainN-xxx/接口设计.md。
执行检查项: 接口设计.md 中的接口数 = 实际路由数。

## 规则 4: 数据库变更必须提供 migration
Alembic up + down 必写。
执行检查项: alembic/versions/ 中有对应 migration 文件。

## 规则 5: 输出测试方案
单测 / 集成 / E2E 分层。
执行检查项: commit message 附 pytest 输出。
```

---

### 代码规范.md 基本要求

```markdown
# 代码规范

## 命名
- 变量/函数: snake_case
- 类: PascalCase
- 表名: 复数（customers / students）
- 模型名: 单数（Customer / Student）
- 文件: snake_case

## 注释
- 公开接口必注
- 复杂逻辑必注
- 不注释"显而易见的"

## 错误处理
- API 层统一异常处理
- Service 层抛业务异常
- 不打敏感信息到日志

## 测试（动态测试规范节必含）
- 覆盖率不低于 70%
- 关键路径禁用 mock（LangChain / SSE / 跨链路 HTTP）
- commit message 必带 pytest 输出
```

---

### 触发器

| 编号 | 条件 | 判定 |
|------|------|------|
| T6.1 | 每条 AI 协作规则没有对应执行检查项 | 标红 |
| T6.2 | AGENTS.md 缺 4 大要素（团队结构 / 职责 / 流程 / 评估） | 标红 |
| T6.3 | 代码规范.md 缺"动态测试规范"小节 | 标红 |
| T6.4 | 开发规则.md 5 条标准规则被改或被删 | 标红 |
| T6.5 | Agent 职责划分.md 没写"做/不做" | 标红 |
| T6.6 | Prompt 设计规范.md 缺"任务模板" | 标红 |
| T6.7 | 含 Agent 链路但缺 AI Agent Prompt 规范.md | 标红 |
| T6.8 | 含 Agent 链路但缺 AI Agent 安全边界规范.md | 标红 |
| T6.9 | 含前端但缺前端规范.md | 标红 |

**冻结判定**：

- 6 核心文档：硬冻结（多 Agent 协作的依据）
- 开发规则 5 条：硬冻结（不可删）
- 代码规范：软冻结（可补充不可减少）

**决策点**：canyu 拍"规范对不对"。

**反向流程**：规范执行不下去，不重新设计，用例外记录留 Round 8 复盘。

**红黄绿**：

- 绿：6 核心文档全齐 + 编码 + AI 规则齐全 + 每条规则可验证 + Agent 安全边界 + 前端规范
- 黄：有规则但验证机制不全
- 红：规则口头化，无法验证

---

## Round 4a: 数据库设计

**输入**：设计规范 + 链路 todo + 验收标准。

**产出物**：`docs/04-technical/数据库设计.md` + `建表语句.sql` + `alembic/versions/`。

**§4.18 记忆架构设计**（含 Agent 链路时必做）：

如果项目含 AI Agent 链路，数据库设计必须包含记忆架构设计：

| 层 | 存储介质 | schema 要点 |
|---|---|---|
| L1 短期 | DB（conversation_messages） | role / content / created_at，最近 N 条 |
| L2 中期 | DB（conversation.summary 字段） | 会话级摘要 |
| L3 结构化事实画像 | DB（JSONB agent_known_facts） | 权重 / 趋势 / retracted_at / 扣分推算 |
| L4 跨会话 | 向量库（独立 collection） | user_id 强隔离 / top_k / 降级友好 |

设计要点：
- **user_id 隔离**：A 学生不能召回 B 学生数据（向量库 expr 过滤 + 结果二次校验）
- **仅入 role=user 消息**：assistant 回复不入向量库（避免 AI 自己说的话被当成"学生历史"召回）
- **retracted_at 撤回**：撤回不删除，标记失效
- **超长消息截断**：留余量（如 schema 上限 1000，截断 1500）

**议题清单**：

- 列出所有表（每条链路 1 套 + 公共表）
- 字段命名校准（snake_case / 复数表名 / 单数模型名）
- 软删字段（is_deleted）+ 时间戳（created_at / updated_at）
- 外键 + 索引
- Alembic migration 脚本（up + down）
- **记忆架构设计**（§4.18：4 层记忆 schema / 向量库 collection 规划 / user_id 隔离）

**关键步骤**：

1. 列出所有表，每条链路 1 套表，加公共表（用户/角色/权限）
2. 字段命名：snake_case、复数表名、单数模型名
3. 每表必加：is_deleted BOOLEAN DEFAULT FALSE、created_at TIMESTAMP、updated_at TIMESTAMP
4. 外键必加，索引覆盖 where / order by / join 字段
5. Alembic 迁移：每次变更 1 个 migration，写 up + down，在 test DB 跑
6. **记忆架构**（含 Agent 链路时）：设计 4 层记忆表结构 + 向量库 collection + user_id 隔离

**触发器**：

| 编号 | 条件 | 判定 |
|------|------|------|
| T7.1 | 表名/字段名跟代码不一致 | 标红 |
| T7.2 | 无 is_deleted 字段 | 标红 |
| T7.3 | 无 created_at / updated_at | 标红 |
| T7.4 | 无 Alembic migration | 标红 |
| T7.5 | 外键缺失 / 索引缺失 | 标黄 |
| T7.6 | 含 Agent 链路但无记忆架构设计 | 标红 |
| T7.7 | 记忆架构无 user_id 隔离方案 | 标红 |

**冻结判定**：

- 表结构：软冻结（写代码时可能微调字段，不经回滚）
- 命名规范（表/字段）：硬冻结
- 记忆架构 schema：硬冻结

**决策点**：无（基于规范推导）。

**反向流程**：表结构跟规范不一致，重新对齐。

**红黄绿**：

- 绿：命名一致 + 软删/时间戳齐全 + Alembic 齐全 + 记忆架构设计完成
- 黄：命名一致但字段不全
- 红：命名不一致 / 无 Alembic / 无记忆架构

---

## Round 4b: 整体框架构造

**输入**：数据库设计 + 设计规范 + 记忆架构设计。

**产出物**：

- `backend/app/` 公共模块（config / main / core / router 留白）
- 业务路由空壳（customer.py / student.py / ai_chat.py / mental.py）
- **Agent 框架**（含 Agent 链路时：ai/agents/ + ai/chains/ + ai/guards/）
- **SSE 协议骨架**（§4.20，含 Agent 链路时）
- **危机短路模块**（§4.16，含 Agent 链路时）
- `scripts/env_check.py`（环境预演）
- `tests/test_health.py`（smoke 测试）
- `docs/04-technical/模块划分.md`

**§4.20 真流式 SSE 双轨设计**（含 Agent 链路时必做）：

| 要点 | 内容 |
|---|---|
| 主轨 | `astream_events("v2")` 监听 `on_chat_model_stream` |
| 副轨 | 伪流式 `pseudo_stream_chunks` 按 12 字切分回退 |
| 触发条件 | `streamed_visible_chars == 0`（互斥，不重复下发） |
| 可见过滤 | `is_visible_token` 过滤 JSON 控制符 / 字段头 / 空白，结构化 schema 不漏到用户侧 |
| 真相源 | structured_response 是最终真相（评级 / alert_reason 不走 token） |
| TTFT | ≤ 2s，可加占位 token 降级 |

SSE 事件协议（在 Round 2b 契约冻结时已定，此处实现骨架）：
- `conversation_created`：会话创建
- `token`：流式 token
- `meta`：元信息（如 mental_health_update）
- `done`：完成（含 plan_update_hint / history_rag_hits / tools_used）
- `error`：错误（含 code + fallback token）

**§4.16 危机响应短路**（含 Agent 链路时必做）：

AI Agent 链路在 LLM 调用之前必须有危机关键词短路：
- 关键词匹配（如 HIGH_RISK_KEYWORDS）→ 返回安全模板（如 12355 心理援助热线），**不走 LLM**
- 危机短路在所有工具 / LLM 之前执行
- 危机短路测试是严格类（100% 通过才发版，详见 03 号文件 §4.19）

**议题清单**：

- config.py — extra="ignore" 必加
- main.py + core/（database / security / middleware / response / exceptions）
- router.py（只公共，业务留白）
- 业务路由空壳（每链路 1 个空文件）
- **Agent 框架构造**（含 Agent 链路时：agents/supervisor + context + response_format + guards/keyword_alert + tools/）
- **SSE 协议骨架 + 真流式双轨**（§4.20）
- **危机短路模块**（§4.16）
- 环境预演脚本（跑通全绿，含 Docker / 向量库）
- smoke 测试（health check 通过）
- 检查触发器

**config.py 关键约束**（pydantic v2 实战教训）：

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    # ... 其它字段

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"  # 必加——不加则 pydantic 默认 forbid，所有 pytest 跑不起来
    )

settings = Settings()
```

必须使用 `model_config = SettingsConfigDict(...)` 而非老版 `class Config`。

**环境预演 checklist**：

- config.py 含 model_config + extra="ignore"
- requirements.txt 锁版本，禁止 "latest"
- Dockerfile 锁基础镜像版本
- 数据库可达、向量库可达（如有）、LLM Provider 可达（如有）
- .env.example 完整
- 跑通 scripts/env_check.py 全绿
- 跑通 pytest tests/test_health.py 全过

**router.py 留白规则**：

```python
from fastapi import APIRouter
# 业务路由留白，并行阶段由链路 Agent 在分支上添加
router = APIRouter()
```

router.py 是公共文件，只协调方改，链路 Agent 禁改。

**触发器**：

| 编号 | 条件 | 判定 |
|------|------|------|
| T8.1 | 环境预演失败 | 阻塞 |
| T8.2 | smoke 测试失败 | 阻塞 |
| T8.3 | 配置没加 extra="ignore" | 阻塞 |
| T8.4 | router.py 包含业务路由 | 标红 |
| T8.5 | _chains/ 还没建 | 阻塞 |
| T8.6 | 含 Agent 链路但未构造 Agent 框架 | 标红 |
| T8.7 | 含 Agent 链路但未实现 SSE 协议骨架 | 标红 |
| T8.8 | 含 Agent 链路但未实现危机短路 | 标红（阻塞发版） |
| T8.9 | 含 Agent 链路但向量库不可达且无降级 | 标黄 |

**冻结判定**：

- 公共模块代码（config / core / main）：硬冻结（链路 Agent 禁改）
- router.py 留白规则：硬冻结
- SSE 事件协议：硬冻结（Round 2b 契约冻结时已定）
- Agent 框架接口：硬冻结

**决策点**：canyu 拍"骨架对不对"。

**反向流程**：骨架跑不起来，排查 config / 依赖 / 版本，不重写架构。

**红黄绿**：

- 绿：环境预演过 + smoke 测试过 + 路由框架空着 + Agent 框架齐 + SSE 骨架齐 + 危机短路齐
- 黄：环境预演过但有 warning
- 红：环境预演失败 / Agent 框架缺失 / 危机短路缺失

---

## Round 5: 冻结审计

**输入**：所有前轮的硬冻/软冻/草稿项 + PPM + 契约冻结文档。

**产出物**：冻结审计报告 + 完整性扫描报告 + 所有软冻→硬冻升级确认。

**审计内容**：

A. **跨轮依赖一致性检查**：所有硬冻结项梳理成一张冻结清单，检查跨轮依赖是否一致。

B. **软冻→硬冻升级**：关键软冻项在这里决定是否升级为硬冻结。默认策略：模糊时偏软，但协调方认为风险高则升级。

C. **PPM 完整性扫描**：
- 7 层文档中标记为"本轮需要"的目录，不能有空文件
- 6 核心文档缺一阻塞
- 每条链路接口设计含路径/方法/入参/出参/错误码
- 每条链路 todo 每器官含测试点标注
- PPM 中所有进行中项必须全部转为完成
- 任何文档出现待补充标记且涉及本轮必产内容，阻塞

D. **Agent 契约冻结**（含 Agent 链路时）：
- SSE 事件协议冻结（事件名 / 字段 / 顺序）
- Prompt 版本冻结（PROMPT_VERSION 已定）
- 记忆 schema 冻结（4 层记忆表结构 / 向量库 collection）
- 安全边界冻结（敏感字段分层 / 评级取严规则）

E. **前端完成定义冻结**（含前端时）：
- 角色矩阵冻结（哪些角色 / 各角色页面入口）
- 单源 View 目录结构冻结
- 视角收束计划冻结（哪些功能归哪个角色 / 收束时间点）

**决策点**：canyu 确认"可以开门了"。

---

## 多 Agent 启动门（8 项硬条件，全部满足才通过）

```
条件 1: 架构冻结
  目录结构已定 + 技术栈已锁版本 + 公共模块已写

条件 2: 契约冻结
  每条链路的接口设计.md 已写（路径/方法/入参/出参/错误码）
  SSE 事件协议已冻结（含 Agent 链路时）
  枚举值 / 前后端字段映射已冻结

条件 3: 环境预演通过
  scripts/env_check.py 全绿
  Docker / 向量库可达（含 Agent 链路时）

条件 4: smoke 测试通过
  pytest tests/test_health.py 全过

条件 5: 6 核心文档齐全
  AGENTS.md / Agent 职责划分 / Prompt 设计规范
  / AI Agent Prompt 规范（含 Agent 时）/ 任务拆分规范 / 验收标准

条件 6: 每条链路 todo.md 已拆分
  含器官 + 测试点标注 + 跨链路依赖标注
  Agent 链路 todo 含 Agent 专项器官标注

条件 7: 白名单明确
  每个 Agent 能改/不能改哪些文件

条件 8: 契约已冻结
  接口 schema / 枚举 / SSE 事件 / 前后端字段映射
  契约文档先于代码，不是崩溃后补
```

全部通过则开门，任意未通过则阻塞，退回到对应轮次补齐。

---

> Round 3-5 完。启动门通过后，进入 03-并行开发与收尾-Round6至Round8。
> 每轮结束须更新继承快照（§4.12）。
