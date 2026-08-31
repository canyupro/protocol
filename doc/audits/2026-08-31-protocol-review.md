# 协议项目区审查报告（一轮）

> 审查日期：2026-08-31
> 审查范围：`/Library/Project/appcode`（后端 Java）和 `/Library/Project/appcode-fend`（前端 uni-app）两个工作区的全部会话（13 个 interactive 会话）
> 审查方法：4 个并行 sub agent，分别审查**流程执行 / 人读文档 / 守卫机制 / 图产物** 4 个维度，每个 agent 独立只读分析
> 本文件：完整记录各维度发现与证据路径，供二轮深挖与规程修正使用

## 一、背景事实（影响所有维度判定）

| 事实 | 证据 | 影响 |
|---|---|---|
| 两个项目区骨架均已创建（问卷/task.md/map.md/guard.json） | appcode 2026-08-19、appcode-fend 2026-08-27 | 初始化阶段基本完成 |
| ZCode 项目 Hook **从未被信任**：8 月 25–31 日 `pending_trust` 警告共 **962 条** + 0 条 `trusted` 事件 | `~/.zcode/cli/log/zcode-2026-08-{25..31}.jsonl` | **guard.py 形同虚设**，所有拦截都是纸面的 |
| appcode-fend **没有 `.zcode/config.json`**；appcode 有但由 agent 手工补写 | `ls /Library/Project/appcode-fend/.zcode` 仅 `plans/` `commands/` | init 脚本未生成项目级 hook 配置 |
| archify 生成的 `xiaocheng-architecture.html`（715KB）躺在 `/Library/Project/appcode/doc/protocol/temp/`，未被 README 引用 | temp 目录文件 | 高质量人读产物被埋没 |

## 二、各维度发现（按严重程度排序）

### 维度 1：流程执行

| # | 严重度 | 发现 | 证据 |
|---|---|---|---|
| 1.1 | 高 | `init_project_area.py` 不生成 `.zcode/config.json`；appcode 之所以有，是 agent 手工补写的 | `sess_a83805c7/call_2ha9kn9*.json` 的 before/after diff |
| 1.2 | 中 | appcode-fend 问卷第 2 节勾选的是 `[x] 存量介入 [假设]`，第 5 节负责人三项空白；task.md 用 "canyu" 兜底，与问卷存在事实漂移 | `appcode-fend/doc/protocol/00-基础调查问卷.md:19,48-51` |
| 1.3 | 低 | `appcode-fend/AGENTS.md` 直接被 agent 改写覆盖，无 diff artifact；plugin SKILL 写需用户确认 append，未强制 | `appcode-fend/AGENTS.md` |
| 2.1 | 高 | appcode `[待确认]` 2 项悬挂 **12 天**；appcode-fend 第 5 节空白 4 天；task.md 把待确认项当事实写 | appcode task.md:23 vs 问卷:35,39 |
| 2.2 | 高 | appcode-fend 任务"在店顾客列表"整体撤回，`understanding-approved.md` 范围 `*` 仍生效，无任务-批准联动 | task.md:6、approvals/understanding-approved.md |
| 2.3 | 低 | `/protocol:begin` 不记录触发时间（begin_at）和主/被动（initiated_by），无法审计流程来源 | map.md:22 仅写日期 |
| 2.4 | 低 | task.md "事实状态"段被当作 changelog 用，appcode 已 53 行/2KB | appcode `.agents/protocol/task.md:38` |
| 3.1 | 高 | appcode 独立验证报告"允许进入代码执行"，但 approvals 目录**从未创建** 12 天 | `verification/understanding-review.md` vs `ls approvals/` 不存在 |
| 3.2 | 高 | appcode-fend 验证报告与批准文件**在同一 parent session**（sess_d79ccb0e）内产出，违反独立上下文 | artifacts/sess_d79ccb0e/ 下两份文件 |
| 3.3 | 中 | 批准模板无"偏差修订证据 / 修订后核验者"字段，无法溯源 | `templates/common/understanding-approved.md` |
| 3.4 | 中 | 后续业务改动（tester 写测试/vision 渲染异常调查）不再走 `/protocol:check` | sess_711d0cc1, sess_45e93181 |
| 4.1 | 中 | `[待确认]` 项无超时升级、无清单可视化 | appcode 4 项悬挂 12 天 |
| 4.2 | 高 | appcode-fend 任务撤回后，批准/plan 文件未同步撤销 | `.zcode/plans/plan-sess_d79ccb0e*.md` |
| 4.3 | 中 | `verification/understanding-review.md` 曾被人工编辑；`ALLOWED_AGENT_FILES` 未保护 verification 目录 | `protocol_guard.py:26-29` |
| 5.1 | 最高 | guard 962 条 pending_trust + 0 条 trusted，所有拦截从未实际触发 | ZCode 日志 |
| 5.2 | 中 | plan mode 与 protocol guard 边界混淆，3 条 `tool.permission.denied` 是 plan mode 不是 protocol | `zcode-2026-08-28.jsonl` |
| 5.3 | 中 | 子 agent mode 不一致（plan/yolo 切换），协议区未强制 mode | sess_d79ccb0e trace |
| 5.4 | 低 | sess_ea028a43 cwd 是 `appcode-shop-pad`（第三个项目），命名混淆 | 会话标题 |
| 5.5 | 低 | 部分会话（sess_879d8a0f、sess_7937be79）agents/ 下无 transcript | `~/.zcode/cli/agents/` |
| 5.6 | 低 | subagent 可自由 spawn 任意 profile | sess_711d0cc1 |
| 5.7 | 中 | hook 脚本在项目外路径 `/Users/Repository/protocol/`，外部路径变更会丢 guard | `.zcode/config.json:12` |

### 维度 2：人读文档

| # | 严重度 | 发现 | 证据 |
|---|---|---|---|
| 1 | 高 | appcode README 第 7-13 行 "本轮已产出" 横幅 + 第 51-63 行 "当前理解进度" 占人读入口前 1/3，违反渐进认知 | `appcode/doc/protocol/README.md` |
| 2 | 高 | appcode-fend README 仅 13 行空壳目录，无人话入口 | `appcode-fend/doc/protocol/README.md` |
| 3 | 中 | 问卷 "交付物" 字段空模板留空白，无占位 | `00-基础调查问卷.md:26`（appcode-fend） |
| 4 | 中 | drawio 信息密度极端化：appcode 太疏（5 节点无标记）、appcode-fend 太密（14 节点 + 内联标记） | 两份 architecture.drawio |
| 5 | 高 | archify HTML 在 `temp/` 未被 README/map.md 引用 | `appcode/doc/protocol/temp/xiaocheng-architecture.html` |
| 6 | 中 | appcode-fend 把 `[已验证]/[假设]/[异常]` 塞进 mxCell value 字符串，AI 不能结构化抽取 | `appcode-fend/.../architecture.drawio` L1-L3 |
| 7 | 中 | 两个项目区 drawio 标准不一致（appcode 无标记、appcode-fend 有） | 两份 drawio |
| 8 | 中 | `naming.md` 4 列表格机读友好但人读干涩（验证等级差异占认知重心） | 两份 naming.md |
| 9 | 低 | `visualization/lifecycle-onepager.html` 在 README 只是表格里一行 | `appcode/.../README.md:113` |
| 10 | 中 | appcode README 25 条下钻表同级平铺，缺"先看哪 3 条"分组 | `appcode/.../README.md:96-125` |
| 11 | 中 | "双读者原则"在 README 未被命名 | `appcode/.../README.md:86-95` |
| 12 | 低 | archify 的 "按角色切片" 视图未被利用 | archify JSON `views` 字段 |

### 维度 3：守卫机制

| # | 严重度 | 发现 | 证据 |
|---|---|---|---|
| 1.1 | 最高 | 962 条 `pending_trust` + 0 条 `trusted`，guard 从未被实际触发 | `~/.zcode/cli/log/*.jsonl` |
| 1.2 | 高 | `init_project_area.py` 的 `--enable-guard` 和 `--project-hook` 是两个独立 flag，用户可能只开一个 | `init_project_area.py:121-129` |
| 1.3 | 中 | 守卫只覆盖创建之后的写入，存量自检缺失 | `init_project_area.py` |
| 1.4 | 低 | 多项目共用 ZCode 工作区时，`find_project_root` 可能误用 | `protocol_guard.py:81-86` |
| 1.5 | 高 | 业务修改可借 Bash 旁路（hook 自承无法拦截） | `protocol_guard.py` 注释行 7 |
| 2.1 | 高 | appcode `approvals/` 始终未创建，guard 永久 deny 状态但用户无感知 | `ls appcode/doc/protocol/approvals/` |
| 2.2 | 中 | appcode-fend 批准范围 `*` + 无到期 = "一次签字长期整库可写" | `approvals/understanding-approved.md:14-15` |
| 2.3 | 高 | 批准 "说明" 字段无证据链接约束（canyu "口头授予"无原始记录） | `approvals/understanding-approved.md:16-17` |
| 2.4 | 中 | 批准后无消费监控（实际未触发），无过期机制 | `verification/understanding-review.md` |
| 3.1 | 中 | 批准模板 4 项证据平铺，无"必须通过独立验证"字段 | `templates/common/understanding-approved.md` |
| 3.2 | 中 | `write-exemption.md` 行 11 字面 `[待填写]` 占位未替换会 fail-closed 假象 | `templates/common/write-exemption.md` |
| 3.3 | 高 | 验证报告说"不允许"，同会话签发"允许"，违反独立原则 | `appcode-fend/verification/understanding-review.md` |
| 4.1 | 中 | appcode 待确认项 12 天无超时升级 | `appcode/doc/protocol/00-基础调查问卷.md:35,39` |
| 4.2 | 高 | appcode-fend 负责人空白但仍允许签发批准 | `approvals/understanding-approved.md:6` |
| 4.3 | 中 | `[待确认]`/`[假设]` 残留项插件从不主动扫描 | task.md / map.md |
| 4.4 | 中 | init 流程"状态文件创了就以为完了"，无任务状态机 | map.md 第 51-52 行 pending 共存 8 天 |
| 5.1 | 高 | appcode 是公司项目（用户无业务代码修改权限），init 仍创建 guard.json | appcode task.md:16 + 问卷第 4 节 |
| 5.2 | 中 | 插件无 "项目模式=纯只读 → 跳过 guard" 分流 | `init_project_area.py` |
| 5.3 | 低 | hook 跨项目可能误继承 | `protocol_guard.py:81-86` |
| 5.4 | 中 | `verification/` 被 `is_project_area_document` 判定，等价于施工方可以改验证报告 | `protocol_guard.py:96-102` |
| 6.1 | 正面 | `load_guard` 对损坏/解析失败返回 None → fail-closed，单元测试已覆盖 | `protocol_guard.py:111-119, 230-231` |
| 6.2 | **脚本 bug** | `json.load(sys.stdin)` 解析失败 `return 0` = fail-OPEN 漏洞 | `protocol_guard.py:247-250` |
| 6.3 | 中 | `extract_cwd` fallback 链：payload → env → os.getcwd()，子 agent cwd 不一定是项目根 | `protocol_guard.py:64-73` |
| 6.4 | 中 | `timeoutMs: 1000` 过短，脚本超时 ZCode 默认视为通过（fail-open） | `.zcode/config.json:13` |
| 6.5 | 中 | fail-closed 在生产中从未被真实验证（自伤测试缺失） | 全日志搜索 |

### 维度 4：图产物

| # | 严重度 | 发现 | 证据 |
|---|---|---|---|
| 1 | 高 | appcode drawio 无 `[已验证]/[假设]/[待确认]` 三标记，违反草案 3.4 | `architecture.drawio` 第 9-145 行 |
| 2 | 高 | appcode-fend drawio 把三标记塞进 mxCell value 字符串，AI 不能结构化抽取 | `architecture.drawio` L1-L3 |
| 3 | 高 | 独立验证报告 24 条核验全部走 grep/find/md5，未走 XML 结构抽取 | `verification/understanding-review.md:35-88` |
| 4 | 中 | 两个项目区 drawio 标准不一致 | 两份 drawio |
| 5 | 中 | archify 调试至少 1-2 轮（raboot-core 位置反复改） | sess_3b538ed3 artifacts |
| 6 | 中 | `judge` 子 agent 失败（vision 模型无图像输入），需 vision agent 复核 | sess_3b538ed3 output |
| 7 | 高 | 项目区 0 份结构事实 JSON；唯一结构 JSON 是 guard.json | `understanding/`、`doc/protocol/` 下无 JSON |
| 8 | 高 | archify HTML 在 `temp/`，未被 promote 进 `understanding/` | `appcode/doc/protocol/temp/xiaocheng-architecture.html` |
| 9 | 中 | 草案 3.4 把架构图定位成"中段视图"但实际承担了人读起点 | 草案文本 |

## 三、跨维度最高优先级汇总

1. **【最高】Protocol guard 从未被实际触发**：962 pending_trust + 0 trusted → 所有拦截纸面
2. **【高】独立验证与批准未真正分离**：appcode-fend 同一会话闭环
3. **【高】批准文件路径应外置**：让 agent 物理写不到
4. **【中】`[待确认]` 项无闭环机制**：4-12 天悬挂无超时
5. **【中】任务撤销与批准撤销未联动**：范围 `*` 长期生效
6. **【中】init 流程场景未分流**：公司项目/纯只读项目也创建 guard
7. **【高】fail-OPEN 漏洞**：`protocol_guard.py:247-250` payload 解析失败返回 0
8. **【中】hook 脚本在项目外路径**：项目不自包含

## 四、关键证据路径速查

| 类别 | 路径 |
|---|---|
| appcode 项目区 | `/Library/Project/appcode/.agents/protocol/`、`/Library/Project/appcode/doc/protocol/` |
| appcode-fend 项目区 | `/Library/Project/appcode-fend/.agents/protocol/`、`/Library/Project/appcode-fend/doc/protocol/` |
| appcode-fend 批准 | `/Library/Project/appcode-fend/doc/protocol/approvals/understanding-approved.md` |
| 协议插件源码 | `/Users/Repository/protocol/plugin/protocol-project-area/` |
| hook 脚本 | `/Users/Repository/protocol/plugin/protocol-project-area/hooks/protocol_guard.py` |
| 项目 hook 配置（appcode） | `/Library/Project/appcode/.zcode/config.json`、`/Library/Project/appcode/.codex/hooks.json` |
| 独立验证 skill | `/Users/canyu/.zcode/cli/plugins/cache/protocol-local/protocol-project-area/0.1.0/skills/independent-verification/SKILL.md` |
| ZCode 日志 | `/Users/canyu/.zcode/cli/log/zcode-2026-08-{25..31}.jsonl` |
| archify 生成物 | `/Library/Project/appcode/doc/protocol/temp/xiaocheng-architecture.{html,json}` |
