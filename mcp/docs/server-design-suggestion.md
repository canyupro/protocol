# 规程 MCP 服务器 — 必要性分析与设计建议

> 配套：并行开发规程 v3.0 总纲 §六（约束介质分层）/ C5 规程迭代提取 B2
> 日期：2026-07-03
> 状态：设计建议，待 canyu 决策是否实施

---

## 一、要不要做 MCP 服务器？—— 结论：值得做，但分阶段

### 1.1 支持做的证据

| 证据 | 来源 | 说明 |
|---|---|---|
| 文本规则对弱模型软约束失效 | `protocol-evolution.md` §1.3 | 22 轮 DeepSeek 实测，10 类规则违反。规则文本再完美，弱模型一样崩。 |
| 模式声明卡（F 试点）不稳 | canyu 反馈 + C5 A3 | 自我声明不可验证，caveman 不好用。F 层已证明「协议层软约束」也不够。 |
| 制衡机制全失效 | 重大错误反思 根因 3 | §4.12 分叉暂停从未触发、§4.18 自己设计自己执行。自己解释、自己执行的规则等于没有。 |
| [x] 必带证据未强制 | 全景复盘 P3-2 | 弱模型把「implementation done」即标 [x]。当前靠人工抽检。 |
| tool call 是硬约束 | `protocol-evolution.md` §三 C 层 | 模型再弱也得调用 tool 才能产出。这是与模型强度无关的约束。 |

### 1.2 反对/谨慎的理由

| 理由 | 应对 |
|---|---|
| 工程量大，本项目是技术演示，不是生产 | 分阶段：先做最小集（3 个 tool），验证有效再扩。MCP server 可以是单文件 Python。 |
| MCP 生态在变，可能很快过时 | 锁定 MCP 协议版本；tool 设计与协议解耦（tool 逻辑可复用到其他载体）。 |
| 当前模型（强模型）不需要硬约束 | MCP 的价值恰恰在「模型切换时」——UpgradeES 切 DeepSeek 后崩，正是缺硬约束。MCP 让规程与模型强度解耦。 |
| 可能过度工程化 | 用 D2 判据检验：每个 tool 必须对应一条「文本层反复失效」的规则，否则不做。 |

### 1.3 结论

**值得做，但作为 v3.0 的 L2 层（工具层）分阶段实施。** 核心论断：UpgradeES 已经证明「读规则」路径到天花板了，再优化规则文本无收益；约束必须迁到 tool 层才能与模型强度解耦。

但**不急于一次性做全**。先做最小集验证，确认有效再扩。

---

## 二、最小可行集（MVP）：3 个 tool

从 `protocol-evolution.md` §三 的 5 个候选里，按「文本层失效频率 × 后果严重度」排序，选前 3 个：

| 优先级 | tool | 对应规则 | 为什么选它 |
|---|---|---|---|
| P0 | `mark_checked(item, evidence_url)` | [x] 必带证据 | 失效频率最高（弱模型每轮都违规）；后果是验收失真；实现最简单（校验 evidence 非空 + URL 可达） |
| P0 | `pause_for_user(forks[])` | §4.12 分叉暂停 | 后果最严重（默认决策导致方向偏差，D2 自我合法化）；文本层从未触发过；实现中等 |
| P1 | `report_step(phase, content)` | §8 报告模板 / 决策记录 | 失效频率高（弱模型不按模板）；后果是决策成本转嫁（D5）；实现简单 |

**先不做**的 2 个：
- `start_timebox(minutes)`：时间盒用人工/计时器即可，tool 化收益低。
- `set_mode(mode, template)`：声明卡已否决，模式约束改用「产出契约」更直接。

---

## 三、MCP 服务器设计

### 3.1 定位

```
规程 MCP 服务器（protocol-mcp）
  ├─ 不是规程本体（规程在文档里）
  ├─ 不是 AI（不做判断，只做校验与拦截）
  └─ 是「约束执行器」：把文本规则里「反复失效 + 后果严重」的少数条款，物化为不可绕过的 tool 调用
```

**设计原则**：
1. **最小化**：只承接文本层反复失效的规则，不把所有规则都 tool 化（否则又回到 800 行规则稀释问题）。
2. **可校验**：每个 tool 的参数必须是机器可校验的（URL 可达、字段非空、枚举合法）。
3. **不判断**：tool 不做业务判断，只做「证据是否齐全」「是否在分叉点」的机械校验。判断仍由人。
4. **与模型无关**：tool 是 MCP 协议，任何支持 tool calling 的模型都能用。

### 3.2 tool 规格定义

#### tool 1: `mark_checked`

```python
@mcp.tool()
def mark_checked(
    item_id: str,           # AC 编号 / 任务编号，如 "AC-F20-1"
    evidence_url: str,      # 证据路径，如 "tests/test_k12_facts.py::TestHistoryRecallIntent"
    evidence_type: str,     # "pytest" | "ruff" | "git_log" | "screenshot" | "review"
) -> dict:
    """
    标记一个 AC / 任务为完成。必须附带证据。
    无证据或证据不可达 → reject，不允许标完成。
    """
```

**校验逻辑**：
- `evidence_url` 非空 + 符合格式
- `evidence_type=pytest` 时，校验对应测试函数存在（grep）
- `evidence_type=git_log` 时，校验 commit hash 真实（`git rev-parse --verify`）
- 返回 `{"accepted": bool, "reason": str}`

**对应 C2 V7/V9**：把验收 checklist 的两条人工项自动化。

#### tool 2: `pause_for_user`

```python
@mcp.tool()
def pause_for_user(
    forks: list[dict],      # 分叉选项 [{"option": "继续修", "risk": "MEDIUM"}, ...]
    context: str,           # 为什么需要暂停
) -> dict:
    """
    在策略分叉点强制暂停，把决策权交还用户。
    AI 不能自行选择分叉，必须调用本 tool 后等待用户拍板。
    """
```

**校验逻辑**：
- `forks` 至少 2 项（否则不是分叉）
- 调用后进入「等待用户」状态，AI 不能继续产出
- 用户回复后，记录选择并放行

**对应 §4.12**：把「自己触发」改成「tool 强制触发」。

#### tool 3: `report_step`

```python
@mcp.tool()
def report_step(
    phase: str,             # "阅读" | "方案" | "实现" | "测试" | "收尾"
    content: str,           # 本步骤实际产出摘要（≤ 500 字）
    artifacts: list[str],   # 产出文件路径
) -> dict:
    """
    报告一个规程步骤的完成。不调用本 tool 不允许进入下一步 / 不允许 commit。
    把「自我证明在按规程做事」的噪声压缩为结构化记录。
    """
```

**校验逻辑**：
- `phase` 在枚举内
- `content` 非空 + ≤ 500 字（防止 D5 决策成本转嫁）
- `artifacts` 路径存在
- 返回步骤序号 + 时间戳

**对应 §8 模板 + D5**：把冗长报告压缩为结构化记录，削减噪声。

### 3.3 技术栈建议

| 项 | 选择 | 理由 |
|---|---|---|
| 语言 | Python 3.10+ | 与项目一致 |
| MCP SDK | 官方 `mcp` Python SDK | 锁版本 |
| 传输 | stdio（本地）| 演示项目不需要远程 server |
| 存储 | SQLite（可选）| 记录 tool 调用历史，用于复盘 |
| 部署 | 单文件 + `pyproject.toml` | 最小化 |

### 3.4 集成方式

```
用户 ↔ AI 客户端（Trae/Claude Code）↔ MCP server（protocol-mcp）↔ 校验逻辑
                                          ↕
                                     规程文档（只读引用）
```

AI 客户端配置 MCP server 后，规程里写「完成 AC 必须调 `mark_checked`」「分叉必须调 `pause_for_user`」。模型若不调用，产出不被接受。

---

## 四、分阶段实施计划

| 阶段 | 内容 | 工时估算 | 验证标准 |
|---|---|---|---|
| Phase 1 | `mark_checked` 单 tool + 接入一个 AI 客户端 | 4-6h | 弱模型标 AC 时必须附带证据，否则 reject |
| Phase 2 | 加 `pause_for_user` + `report_step` | 4-6h | 弱模型在分叉点被迫暂停，报告噪声下降 |
| Phase 3 | 接入 v3.0 规程文档，跑一个完整 Round 验证 | 2-4h | 一轮开发全程 tool 化，对比无 tool 时的违规率 |

**总工时**：10-16h（可分 3 个里程碑）。

**Phase 1 成功判据**：弱模型（DeepSeek 级）标 AC 时，证据缺失率从当前的高发降到 < 10%。

**失败判据**（何时放弃 MCP 路线）：
- Phase 1 后弱模型绕过 tool（不调用直接标完成）且无法拦截 → 说明当前客户端不支持强制 tool → 放弃，回退到人工验收。
- tool 调用开销 > 收益（每轮多花 30%+ 时间在 tool 交互）→ 缩减 tool 数量。

---

## 五、风险

| 风险 | 概率 | 应对 |
|---|---|---|
| AI 客户端不支持「强制 tool」（模型可绕过） | 中 | Phase 1 先验证；不支持则 MCP 路线作废 |
| tool 设计过度，变成新的规程噪声（D5） | 中 | 每个 tool 必须对应一条文本层反复失效的规则；否则不做 |
| MCP 协议变动 | 低 | 锁版本；tool 逻辑与协议解耦 |
| 工程量超预算 | 中 | 严格分阶段，Phase 1 不达标不进 Phase 2 |

---

## 六、决策点（待 canyu 拍板）

1. **是否启动 MCP 路线？** 是 → 进 Phase 1；否 → v3.0 L2 层留空，靠 L1（产出契约）+ 人工验收。
2. **若启动，先做哪个 tool？** 建议从 `mark_checked` 开始（最简单、收益最直接）。
3. **MVP 范围？** 建议 3 个 tool（§二）。若想更保守，只做 `mark_checked` 1 个先验证。
4. **谁实现？** DS 执行方 / 调度方亲自 / 另起任务。

---

## 七、版本

- v0.1 / 2026-07-03 / MCP 必要性分析与设计建议首发
  - 结论：值得做，分 3 阶段
  - MVP 3 个 tool：mark_checked / pause_for_user / report_step
  - 待 canyu 决策是否启动
