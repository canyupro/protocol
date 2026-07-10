# 01 — 串行对话：Round 0 至 Round 2b

> 项目前半段的逐轮操作指南。每轮按"输入 / 产出物 / 关键步骤 / 触发器 / 决策点 / 反向流程 / 红黄绿"7 字段展开。
> 每轮首句须输出模式声明卡（§4.4），每轮结束须更新继承快照（§4.12）。

---

## 通用约定（每轮生效）

- 本轮开始前，协调方给出议题清单（5-8 个），你勾选哪些本轮讨论、哪些下轮再议
- 只有你勾选的议题在本轮结束时被冻结/标记
- 每轮结束产出决策记录 + 更新 PPM + 更新继承快照
- 你确认后才进入下一轮
- **§4.4 模式声明卡**：每轮 AI 首句输出 `[模式] caveman={ON|OFF} | §8={ON|OFF} | timebox={N}min | 风险={LOW|MEDIUM|HIGH}`。所有平台保留，与继承介质正交互补
- **§4.12 继承快照**：每轮结束更新 `workflow_state`（当前角色/任务阶段/最近 commit/已冻结决策/待定项/下一步）。模板见 04-附录 H

---

## Round 0: 项目播种

**输入**：空白工作目录。

**产出物**：顶层目录结构 + git init + .env.example + 环境预演 + 项目播种记录。

**§4.1 环境纪律 Runbook 预检**：

项目启动前必须过环境 Runbook（详见 05-G 速查）。核心三件套（Windows + async DB 项目）：
1. Docker Desktop 已启动（`docker version` 确认 Server 段可连）
2. Python 缓存纪律：`python -B` 禁止 .pyc + 改 .py 后清 `__pycache__`
3. Windows 异步驱动：用 `run_backend.py`（设 SelectorEventLoopPolicy），不用 `uvicorn` 直接启动

非 Windows 项目按实际环境调整，但"启动即固化"原则不变——不靠现场调试。

**议题清单**：

- 顶层目录讨论（backend/ frontend/ docs/ scripts/ tests/ .gitignore README.md，约 8 个目录）
- 技术栈初始化（Python 版本 / Node 版本 / 虚拟环境 / 最小依赖）
- 版本控制（git init + .gitignore 规则）
- 环境预演（跑通 health check）
- 触发轨道评估（是否为 Demo Mode）

**关键步骤**：

1. 确认顶层目录名和结构
2. git init，写 .gitignore
3. 初始化 Python 虚拟环境，安装最小依赖（FastAPI / pytest / ruff）
4. 初始化前端脚手架（按实际选型）
5. 创建 .env.example 和 .env（空）
6. 跑通一条 health check，证明环境可用

Stage 0 只讨论顶层目录，`docs/` 的 7 层细分留到 Round 2b。

**冻结判定**：

- 顶层目录结构：硬冻结
- .env.example 格式：软冻结
- 技术栈版本范围：软冻结

**决策点**：canyu 确认顶层目录结构 + 判断是否为 Demo Mode。

**反向流程**：目录结构不合理，回 Round 0 重做。

**红黄绿**：

- 绿：顶层目录结构确认 + git init 完成 + 环境预演全绿
- 黄：环境预演通过但有 warning
- 红：环境预演失败

---

## Round 1a: 拿需求

**输入**：客户需求 / 会议纪要 / 邮件。

**产出物**：

- `docs/02-product/PRD.md`（骨架：业务背景 + 目标用户 + 核心场景 + 非功能需求 + 验收标准粗）
- `docs/02-product/用户故事.md`（每条含 AC，格式：As a / I want to / So that）
- 原始材料归档到 `docs/02-product/raw/`

**§4.10 换位思考原则**：

需求阶段对以下对象强制触发换位思考：
- 未成年人
- 弱势用户群体
- 业务流程中处于被服务而非服务方
- 在业务流程中产生非显式数据（情绪 / 心理状态 / 隐私行为）

协调方必做：
1. 主动提出"换位场景"议题，加入议题清单
2. 至少识别 1-2 个"业务侧未提但用户侧必有"诉求
3. 即使 MVP 不实现，也在 PRD/DB 阶段预埋字段或接口
4. 显式询问 canyu 是否纳入 MVP / V2 / V3

**议题清单**：

- 业务背景与目标用户
- 核心场景排列（3-5 个）
- 非功能性需求（性能 / 安全 / 合规）
- 用户故事逐条讨论（每条你确认才定）
- 每条用户故事的验收标准（AC）是否可验证
- **换位场景**（§4.10 强制）：哪些用户群体需要换位思考？有什么业务侧未提的诉求？

**关键步骤**：

1. 收集所有原始需求（邮件 / 会议纪要 / 聊天记录），归档到 raw/
2. 整理结构化 PRD：业务背景、目标用户、核心场景、非功能需求、验收标准（粗）
3. 拆为用户故事，每故事必带 AC：
   ```
   As a [角色]
   I want to [动作]
   So that [价值]
   Acceptance Criteria:
   - Given [前置]
   - When [动作]
   - Then [结果]
   ```
4. 换位思考：对每个 user-facing 角色检查非业务诉求，预埋字段/接口

**冻结判定**：

- 用户故事内容：软冻结（Round 1b 可能调整归属）
- 业务背景：软冻结

**决策点**：无（纯产出，分类留到 Round 1b）。

**反向流程**：需求矛盾，找业务方确认，回头修改用户故事。

**红黄绿**：

- 绿：PRD + 用户故事齐全，验收标准明确可验证
- 黄：PRD 有但用户故事不全
- 红：需求模糊，验收标准缺失

---

## Round 1b: 需求分类

**输入**：Round 1a 产出的 PRD + 用户故事。

**产出物**：

- `docs/02-product/MVP 范围定义.md`（必须 / 可选 / 不做）
- 链路映射表（每个故事归属 1 条链路）
- `docs/03-agent/验收标准.md`（6 核心文档之一，接口级粒度）

**AI Agent 链路识别**：

需求分类时，如果项目含 AI Agent 能力，必须将以下链路单独标注（不走 CRUD 链路模板）：

| Agent 链路类型 | 特征 | 与 CRUD 链路的区别 |
|---|---|---|
| RAG 检索链路 | 用户查询 → 向量检索 → LLM 生成 | 需向量库 collection 规划 + Embedding 选型 + 降级策略 |
| Agent 对话链路 | 多工具上下文 + LLM 决策 + SSE 流式 | 需记忆架构 + Prompt 版本化 + 危机短路 + 降级 |
| 推荐链路 | 结构化推理 + LLM 生成 | 需 fallback 规则推荐 |
| 情感/心理监听链路 | 关键词触发 + LLM 评级 | 需安全边界 + 评级取严 + 学生端零暴露 |

标注后，这些链路在 Round 2a/2b/3/4a/4b 需走 Agent 专项工程节点（详见后续 Round）。

**议题清单**：

- 业务对象提炼（哪些业务对象，每条链路对应 1 个）
- 链路映射（每个故事归谁）
- **AI Agent 链路识别**（哪些链路是 Agent 类型，需走专项工程节点）
- MVP 范围定义（必须 / 可选 / 不做）
- 检查触发器：链路超过 6 条？链路不足 3 个 story？重叠？
- 验收标准是否达到接口级（路径 / 方法 / 入参 / 出参 / 错误码）

**关键步骤**：

1. 按业务对象分类：列出所有业务对象（customer / student / enterprise 等），每个故事归 1 个对象，每个对象 = 1 条链路
2. **标注 Agent 链路**：识别 RAG / Agent 对话 / 推荐 / 情感监听等非 CRUD 链路
3. 标 MVP 范围：必须 / 可选 / 不做
4. 写链路映射表，格式：
   ```
   链路 1: 客户管理 (customer) [CRUD]
     故事 1.1: 注册 / 故事 1.2: 登录 / 故事 1.3: 资料修改
   链路 5: K12 Agent 对话 (k12_agent) [Agent]
     故事 5.1: 学生对话 / 故事 5.2: 对话持久化
   ```
5. 写验收标准，每个 story 对应"如何验证完成"，含正常路径和异常路径

**验收标准模板**（可直接复制使用）：

```markdown
# 验收标准

## 链路 1: [链路名]
### 故事 1.1 [故事名]
- 验收: [HTTP 方法] [路径] 返回 [状态码]，[验证条件]
- 异常: [异常条件] → [预期状态码]，[另一种异常] → [预期状态码]
- 测试覆盖: 单测 / 集成 / E2E
```

**触发器**：

| 编号 | 条件 | 判定 |
|------|------|------|
| T2.1 | 链路数超过 6 条 | 警告，太多，考虑合并 |
| T2.2 | 某条链路不足 3 个 story | 警告，太小，考虑合并到其他链路 |
| T2.3 | 验收标准缺失或太抽象（只写"完成"不写"如何验证"） | 标红 |
| T2.4 | 链路互相重叠（同一故事归到 2 条链路） | 标红 |
| T2.5 | Agent 链路未标注类型（RAG/Agent/推荐/情感） | 标红 |

**冻结判定**：

- 链路数：硬冻结（新增链路需审计）
- MVP 范围定义：硬冻结
- 验收标准：软冻结（后续可加深粒度，不可删减）

**决策点**：canyu 拍"链路分类 + MVP 范围对不对"。

**反向流程**：链路重叠，回 Round 1a 重新分类；MVP 模糊，canyu 拍板。

**红黄绿**：

- 绿：链路数合理（2-6 条），MVP 清晰，验收标准可验证，Agent 链路已标注
- 黄：链路数过多或过少，验收标准模糊
- 红：MVP 模糊，链路互相重叠，验收标准缺失，Agent 链路未标注

---

## Round 2a: 实现拆分 + 技术栈

**输入**：链路映射表 + 验收标准 + Agent 链路标注。

**产出物**：

- `docs/03-agent/任务拆分规范.md`（6 核心文档之二）
- `docs/03-agent/链路N-todo.md`（每条链路 1 份，标器官 + 测试点 + 跨链路依赖）
- `docs/04-technical/技术选型.md`（含备选 + 风险 + 版本锁定）

**§4.17 Prompt 版本化规则**：

如果项目含 AI Agent 链路，技术选型必须确认以下 AI Agent 技术栈：

| 项 | 要求 |
|---|---|
| LLM 框架 | 版本锁定（如 LangChain 1.0），确认 create_agent / astream_events API 可用 |
| LLM Provider | 版本锁定 + 可切换（如 DeepSeek / Ollama / OpenAI） |
| Embedding | 版本锁定 + 维度确认（如 bge-m3 1024 维） |
| 向量库 | 版本锁定 + collection 规划（如 Milvus 2.6） |
| Prompt 版本化 | 所有 prompt 写在 `ai/chains/*` 文件内 git 跟踪，PROMPT_VERSION 必填 |
| SSE | 确认 astream_events / EventSourceResponse 兼容性 |

**议题清单**：

- 技术选型（后端 / 前端 / 数据库 / AI / 缓存 / 部署）
- **AI Agent 技术栈确认**（§4.17：LLM 框架 / Provider / Embedding / 向量库 / Prompt 版本化 / SSE）
- 版本锁定（写 requirements.txt / package.json，禁止 "latest"）
- 任务拆分规范确立（粒度标准：不超过 1 文件 / 不超过 200 行 / 不超过 30 分钟）
- 每条链路拆器官（API / Service / Model / Schema / 测试 / E2E）
- 跨链路依赖标注
- 检查触发器：器官数不少于 8？测试点齐全？依赖标注？

**关键技术选型要求**：

每个选型必须填 3 项：为什么选（1-2 句话）、备选（选错了换什么）、风险（已知坑 / 版本兼容 / 升级成本）。版本写进 requirements.txt / package.json，禁止 "latest"。

**任务拆分规范模板**：

```markdown
# 任务拆分规范

## 任务粒度判断标准
- 一个任务不超过 1 个文件改动（大文件除外）
- 一个任务不超过 200 行代码
- 一个任务不超过 30 分钟完成
- 一个任务 = 一个可 commit 的单元

## 任务模板
- 任务 ID: chainN-task-001
- 输入（依赖）: 阶段骨架
- 输出（文件 + 内容）: 对应的代码文件路径
- 测试点: 单测 / 集成 / E2E
- 完成定义: pytest 通过 + 接口设计更新

## 禁止事项
- 不要跨多个链路
- 不要修改无关代码
- 不要"顺便"优化
- 不要 mock 关键路径
```

**链路 todo 格式**（每条链路必须包含）：

```markdown
# 链路 N todo — [链路名] [CRUD / Agent]

## 器官清单
| 器官 | 类型 | 文件路径 | 测试点 | 依赖 |
|------|------|---------|--------|------|
| 注册 API | API POST | api/v1/customer.py | 单测 + 集成 | — |
| 注册 Service | Service | services/customer_svc.py | 单测 | — |
| ... | ... | ... | ... | ... |

## 跨链路依赖
- 链路 3 调链路 1: POST /api/v1/customers → 透传 JWT token
```

Agent 链路的 todo 额外标注 Agent 专项器官（记忆层 / RAG 工具 / Prompt / 降级 / 危机短路）。

**触发器**：

| 编号 | 条件 | 判定 |
|------|------|------|
| T3.1 | 每条链路器官数不少于 8 个 | 细分合理则通过 |
| T3.2 | 任何器官没标测试点 | 标红 |
| T3.3 | 任务拆分规范没有"任务粒度判断标准" | 标红 |
| T3.4 | 跨链路依赖未标出 | 标红 |
| T3.5 | 链路 todo 缺失或器官过少（不足 5 个） | 标红 |
| T3.6 | Agent 链路 todo 未标注 Agent 专项器官 | 标红 |
| T4.1 | 用"最新版"而不锁版本 | 标红 |
| T4.2 | 无"备选"或"风险" | 标黄 |
| T4.3 | 版本号缺失 | 标红 |
| T4.4 | 不同选型之间版本不兼容 | 标红 |
| T4.5 | Agent 链路但未确认 LLM 框架 / Embedding / 向量库版本 | 标红 |

**冻结判定**：

- 技术栈 + 版本：硬冻结
- 任务拆分规范：软冻结（可补充不可删除标准）
- 链路 todo 器官：软冻结（写代码时发现可追加）

**决策点**：canyu 拍"技术选型对不对"。

**反向流程**：选型后跑不起来，排查版本，不轻易换技术栈。

**红黄绿**：

- 绿：每条链路器官齐全 + 测试点齐全 + 依赖清晰 + 任务拆分规范有粒度标准 + Agent 技术栈已确认
- 黄：器官齐但测试点不全
- 红：链路漏器官 / 依赖混乱 / 任务拆分规范缺失 / Agent 技术栈未确认

---

## Round 2b: 目录结构

**输入**：技术选型 + 链路 todo + 业务对象清单 + Agent 链路标注。

**产出物**：

- `docs/04-technical/系统架构设计.md`
- 完整目录树（含 `docs/04-technical/_chains/` 链路隔离区 + 前端单源 View 目录 + Agent 工具层目录）
- **契约冻结文档**（§4.13）
- Premium 升级评估（本轮结束时协调方主动提问）

**§4.13 契约冻结**：

目录结构确定后、Round 3 规范制定前，必须冻结前后端契约：

| 契约项 | 内容 | 冻结级别 |
|---|---|---|
| 接口 schema | 每条链路每接口含路径/方法/入参/出参/错误码 | 硬冻结 |
| 枚举值 | 所有枚举（角色/状态/类型等）的完整取值 | 硬冻结 |
| SSE 事件协议 | 事件名（conversation_created / token / meta / done / error）+ 字段 | 硬冻结 |
| 前后端字段映射 | 前端需要的字段 vs 后端返回的字段，无遗漏 | 硬冻结 |

契约文档先于代码，不是崩溃后补。启动门第 8 项检查"契约已冻结"。

**前端目录规划**：

如果项目含前端，目录结构必须遵循单源 View 模板（详见 08 号文件 §三）：

```
frontend/app/
  _shared/
    views/           # 业务组件真源（StudentView / ParentView / ...）
    role-context.tsx # 角色态共享
  student/page.tsx   # 薄壳：return <StudentView />
  parent/page.tsx    # 薄壳
  dev/page.tsx       # 测试期聚合入口（DEV ONLY，生产期下线）
```

**Agent 工具层目录**：

如果项目含 AI Agent 链路，后端目录必须包含 Agent 工具层：

```
backend/app/ai/
  agents/            # Agent 编排（supervisor / context / response_format）
  agents/tools/      # Agent 工具（每个 @tool 一个文件）
  agents/guards/     # 安全守卫（关键词兜底 / 危机短路）
  chains/            # LLM 链路（每个 chain 一个文件，Prompt 版本化）
  llm_factory.py     # LLM 工厂
  embeddings.py      # Embedding
  vectorstore.py     # 向量库
  reranker.py        # 重排序（可选）
```

**议题清单**：

- 系统架构设计（模块间关系 / 数据流向 / 部署方式）
- 后端目录树（按业务对象分文件，禁止 chainN_*.py）
- **Agent 工具层目录**（ai/agents/ / ai/chains/ / ai/guards/）
- **前端目录规划**（_shared/views 单源 View + dev 聚合入口）
- **契约冻结**（§4.13：接口 schema / 枚举 / SSE 事件 / 前后端字段映射）
- `_chains/` 隔离区结构（每链路 1 子目录）
- 升级评估：是否滑向 Premium？（协调方主动提问）
- 检查触发器：按技术层分？7 层缺失？_chains 缺链路？契约未冻结？

**关键目录约束**：

```
docs/ 内严格使用 7 层结构: 01-business/ 02-product/ 03-agent/
  04-technical/ 05-ai-coding/ 06-project/ 07-testing/

docs/04-technical/_chains/  每链路 1 子目录，链路 Agent 工作区
backend/app/
  core/        公共模块，协调方写，链路 Agent 禁改
  api/v1/      按业务对象分: customer.py / student.py / ai_chat.py / mental.py
  models/      按链路: customer.py / student.py / ...
  schemas/     按链路
  services/    按链路
  ai/          Agent 工具层（agents/ chains/ guards/ llm_factory.py ...）
  tests/       按链路: test_chain1_customer.py / test_chain2_student.py / ...
```

**严禁**：后端 api/v1/ 下出现 chain_routes.py 或 chainN_*.py 这种按链路号命名的文件。

**_chains/ 设计原则**：

- 只切 04-technical 一层（只有技术层链路 Agent 真的会写）
- 后端代码目录不冗余，用 git 分支隔离 + 按业务对象分文件
- 阶段整合时协调方把链路草稿合并到主目录，`_chains/` 保留作链路归档
- 下划线前缀 = 内部目录，工具/AI 跳过扫描

**触发器**：

| 编号 | 条件 | 判定 |
|------|------|------|
| T5.1 | backend/app/ 下出现 controllers/ views/ models/ 按技术层分 | 改 |
| T5.2 | docs/ 下没有 7 层目录结构 | 改 |
| T5.3 | docs/04-technical/_chains/ 没建或缺某个链路子目录 | 阻塞 |
| T5.4 | _chains/ 链路 Agent 在并行前被告知"先写这里" | 必跑 |
| T5.5 | 后端 api/v1/ 出现 chain_routes.py 或 chainN_*.py | 标红 |
| T5.6 | 含 Agent 链路但未建 ai/agents/ 目录 | 标红 |
| T5.7 | 含前端但未建 _shared/views/ 单源 View 目录 | 标红 |
| T5.8 | 契约冻结文档缺失（接口 schema / 枚举 / SSE 事件 / 字段映射） | 阻塞 |

**冻结判定**：

- 目录结构：硬冻结（改了就是 4 倍返工）
- 系统架构设计：硬冻结
- 契约冻结文档：硬冻结

**决策点**：无（基于技术选型自然推导），但如果升级 Premium 则 canyu 拍。

**反向流程**：目录结构不合理，重新设计，不要在错的结构上写代码。契约变更需回 Round 2b 重新冻结。

**红黄绿**：

- 绿：业务对象清晰分层 + docs 7 层结构齐 + _chains/ 链路数等于 todo 数 + Agent 目录齐 + 前端单源 View 齐 + 契约冻结完成
- 黄：部分按业务对象，部分按技术层；契约部分冻结
- 红：完全按技术层分 / docs 目录乱 / _chains/ 缺失 / 契约未冻结

---

> Round 0-2b 完。进入 Round 3 前确保所有触发器已检查通过、契约已冻结、继承快照已更新。继续阅读 02-串行对话-Round3至Round5与启动门。
