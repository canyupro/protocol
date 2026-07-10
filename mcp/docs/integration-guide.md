# protocol-mcp 接入说明

> 配套：v3.0 总纲 §六 L2 工具层 / MCP 服务器设计建议
> 日期：2026-07-03
> 状态：已接入 ZCode，待重启验证

---

## 一、已接入配置

ZCode MCP 配置文件：`~/.zcode/cli/config.json`

已添加 `protocol-mcp` 条目：

```json
{
  "protocol-mcp": {
    "command": "C:\\Users\\canyu\\AppData\\Local\\Programs\\Python\\Python312\\python.exe",
    "args": ["-B", "-m", "mcp_server.server"],
    "cwd": "O:\\warehuose\\UpgradeES"
  }
}
```

### 烟测结果

```
initialize 握手成功
serverInfo: {"name":"protocol-mcp","version":"1.28.1"}
capabilities: tools available
```

---

## 二、可用 tool

| tool | 功能 | 对应规程条款 |
|---|---|---|
| `mark_checked(item_id, evidence_url, evidence_type)` | 标记 AC 完成，必须附带证据，无证据 reject | C2 V7/V9 自动化 |
| `pause_for_user(forks, context)` | 策略分叉暂停，返回分叉选项给用户 | §4.12 分叉暂停 tool 化 |
| `resume_from_pause(pause_id, choice)` | 用户选择后恢复执行 | §4.12 配套 |
| `report_step(phase, content, artifacts)` | 报告规程步骤完成，≤500 字，压缩噪声 | §8 模板 + D5 |

---

## 三、生效方式

**需要重启 ZCode** 让 MCP 配置生效。重启后，AI 协调方在对话中可以直接调用这 4 个 tool。

### 验证生效

重启后在对话中输入：
> 列出你可用的 MCP tool

应看到 `mark_checked` / `pause_for_user` / `resume_from_pause` / `report_step` 四个 tool。

---

## 四、使用场景

### 场景 1：标记 AC 完成（替代人工抽检）

```
AI: AC-F20-1 已通过，证据是 tests/test_k12_facts.py::TestHistoryRecallIntent
→ AI 应调用 mark_checked("AC-F20-1", "tests/test_k12_facts.py::TestHistoryRecallIntent", "pytest")
→ tool 校验测试函数存在 → accepted=True
```

若 AI 标了不存在的证据 → accepted=False → 规程层要求 AI 重新提供证据。

### 场景 2：策略分叉暂停（替代自觉暂停）

```
AI 遇到分叉：继续修 / 降级 / 延期
→ AI 应调用 pause_for_user([{"option":"继续修","risk":"MEDIUM"},{"option":"降级","risk":"LOW"}], "测试失败原因不明")
→ tool 返回 paused=True + forks
→ AI 停止产出，等用户选择
→ 用户选"继续修" → AI 调用 resume_from_pause(pause_id, "继续修")
→ tool 返回 resumed=True → AI 继续
```

### 场景 3：报告步骤（替代冗长决策记录）

```
AI 完成实现步骤
→ AI 调用 report_step("implement", "实现 mark_checked tool", ["mcp_server/server.py"])
→ tool 校验 content≤500字 + artifacts 路径存在 → accepted=True, step_seq=N
→ 压缩为结构化记录，削减 D5 噪声
```

---

## 五、已知限制

| 限制 | 说明 | 后续 |
|---|---|---|
| tool 不强制阻塞 | pause_for_user 返回 paused=True 后，AI 是否真的停止产出靠客户端/规程层保证 | 需客户端配合 |
| 无强制调用机制 | AI 可以不调用 tool 直接标完成 | 需客户端层强制（ZCode 目前不支持） |
| stdio 单进程 | 多个对话共享同一 server 进程，SQLite 并发写入可能冲突 | 低风险，MVP 可接受 |
| cwd 硬编码 | 配置里 cwd 写死项目路径 | 换项目需改配置 |

---

## 六、版本

- v0.1 / 2026-07-03 / 接入说明首发
  - 已写入 ~/.zcode/cli/config.json
  - 烟测通过
  - 待重启 ZCode 验证
