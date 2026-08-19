# Protocol 插件与项目区设计

> 状态：第一版实现与本地小型项目验证中。
> 本文定义当前产品设计；存量介入方法论见 [存量介入方法论草案](存量介入方法论草案.md)，项目区资产职责见 [项目区文件映射规范](项目区文件映射规范.md)。

## 1. 定位

Protocol Project Area Plugin 是全局安装的 ZCode 插件，为任意项目提供统一入口：先建立项目区和基础调查问卷，再按“新启动”或“存量介入”模式推进。

插件不是项目模板生成器，也不在安装时静默修改工作区。用户进入项目后，必须显式执行 `/protocol:init` 才能初始化。

## 2. 分层

```text
全局插件
  commands / skills / hooks / templates
    ↓ 显式 /protocol:init
项目区
  项目规则短指针 + 机器状态/映射 + 人类可读工作文档
```

| 层 | 职责 | 不做什么 |
|---|---|---|
| 全局插件 | 分发通用命令、工作流、守卫与模板 | 不安装即改项目，不保存项目业务事实 |
| 项目根 `AGENTS.md` | 只放 Protocol 项目区短指针和常设边界 | 不复制规程全文、全局规则或任务细节 |
| `.agents/protocol/` | 存机器状态、当前任务和关键连接映射 | 不存大段人类架构文档 |
| `doc/protocol/` | 存问卷、理解图、命名规范、影响面、回顾和人类批准 | 不作为全仓 INDEX |
| 项目区 `.zcode/config.json` | 项目级 hook（仅在该项目生效，需用户工作区信任） | 不绕过信任门槛 |

> 项目区 hook 说明（2026-08-19 实测）：当前 ZCode 已支持项目区 `.zcode/config.json` 的 hooks，但默认 `pending`，必须在客户端完成「工作区 Hook 信任」后才执行。这正好符合「制衡外移 + 人类兜底」——信任是不可脚本绕过的平台安全动作。

## 3. 命令生命周期

```text
/protocol:init
  → 发现项目根、读取现有规则与 README
  → 创建无 guard、无 approvals 的项目区骨架
  → 预填基础调查问卷
  → 经用户确认后追加 AGENTS 短指针

/protocol:begin
  → 对话确认新启动或存量介入
  → 补齐当前任务、权限、交付物和升级路径
  → 最后显式建立 pending guard

/protocol:status
  → 报告问卷、理解门槛、批准/豁免与当前可写资格

/protocol:check
  → 生成独立验证任务包
```

初始化前不得编辑业务代码。已有 `AGENTS.md` 必须先读取、展示拟议差异并获得用户确认，禁止覆盖。

## 4. 基础调查问卷

`doc/protocol/00-基础调查问卷.md` 是任何模式的第一轮前提。它记录：项目识别、模式、当前任务、交付物、授权与权限、项目等级、人类兜底、现有证据、验收、风险和待确认项。

插件可根据 README、已有规则和可读配置预填事实；无法交叉验证的内容必须标记为 `[假设]` 或 `[待确认]`。初始化骨架不创建 `approvals/`，防止主施工 agent 在守卫启用前伪造解锁文件。

## 5. 守卫

### 5.1 生效范围（两路可选）

守卫可走两条路径，二者可择一或并用：

| 路径 | 配置位置 | 生效条件 | 优点 |
|---|---|---|---|
| **项目区 hook（推荐）** | 项目自己的 `<repo>/.zcode/config.json` | 用户在工作区完成 Hook 信任后 | 天然只对该项目生效，未配置项目完全无 hook；无需全局脚本探测项目根 |
| **全局插件 hook** | 插件 `hooks/hooks.json` | 插件启用后全局运行，脚本发现 `.agents/protocol/guard.json` 才拦截 | 跨项目统一分发 |

`/protocol:init` 可生成项目区 `.zcode/config.json`（含 guard hook），但**不能绕过信任**：用户需在客户端确认后才生效。信任按工作区身份 + hook 指纹记录，脚本内容变化后可能需重新信任。

hook 仅匹配 `Edit|Write`，不拦截 Bash 间接写入，也不拦截纯文本输出。这是已知硬约束天花板，仍需项目规则、独立验证、人类兜底与冷启动回顾补足。

### 5.2 代码写入规则

| 目标 | 规则 |
|---|---|
| `doc/protocol/**`、任务/映射/验证报告 | 放行，允许补理解与流程文档 |
| `.agents/protocol/guard.json` | 拒绝，主施工 agent 不得改 guard |
| `doc/protocol/approvals/**` | 拒绝，主施工 agent 不得伪造批准或豁免 |
| 其他项目文件 | 未有匹配的人类批准或有效豁免时拒绝；满足其一时放行 |
| guard 损坏或状态无效 | 对其他项目文件 fail-closed |

### 5.3 解锁路径

代码写入只允许两种人类解锁路径：

1. 人类签发 `approvals/understanding-approved.md`，确认整体架构图、数据流动和命名规范满足当前任务；批准范围必须明确。
2. 人类签发 `approvals/write-exemption.md`，明确豁免范围、负责人、原因、到期时间和可兜底边界。

两类文件仅应由人类在 ZCode 工具路径之外签发。主施工 agent 不得创建、修改或伪造。

## 6. 独立验证方

`/protocol:check` 生成只读独立验证任务包。独立验证方只“看 + 判 + 说”，不设计、不施工、不批准、不修改 guard。

检察者的规则来源、输入材料、判断权限和输出通道，不能由被检察者控制。用户可配置 `testcoder` 作为独立验证方；插件不自动创建或配置子 agent。

## 7. 本地安装与客户端验证

第一版提供 `plugin/marketplace.json` 作为本地 marketplace，不手改 ZCode 安装记录或缓存。使用者在客户端按以下步骤加载：

1. `Settings → Plugin Management → Discover → + → Local directory`。
2. 选择仓库内的 `plugin/` 目录。
3. 在 Discover 中安装并启用 `protocol-project-area`。
4. 新开会话，确认 `/protocol:init`、`/protocol:begin`、`/protocol:status`、`/protocol:check` 已出现，再在小型临时项目验证 hook。

客户端加载是第一版剩余的真实平台验证，不能以脚本单测替代。

## 8. 第一版非目标

- Marketplace 发布或自动安装（第一版仅提供可由客户端添加的本地 marketplace）。
- 安装插件后自动初始化任意项目。
- 自动批准、自动豁免或自动修改人类责任边界。
- MCP 专用工具扩展。
- Bash 或纯文本路径的完全拦截。
