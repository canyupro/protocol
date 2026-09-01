# 颜色设计语言（Color Tokens）

> 编码规约根目录：`doc/protocol/coding-standards/`
> 本文件定义项目应使用的颜色 token 字段框架。具体色值由项目方按 UI 框架（Tailwind / Ant Design / 自研）填入。
>
> **引用关系**：本文档是规范定义；项目实际使用 + 异常记在 `understanding/&lt;项目名&gt;.md`，**通过字段引用**指向本文档对应小节（不要复制粘贴）。

---

## 0. 一段话人话摘要

> 项目整体：颜色以 `category-role-variant` 三段式命名（例：`text-primary-default` / `bg-primary-hover`），按「类别（语义层）→ 角色（业务）→ 变体（状态）」分层。
> 例外：[由项目填入。例如「Ant Design 沿用 `-1` / `-3` / `-6` 后缀；Tailwind 用 `slate-500` 等色阶命名」]。

---

## 1. 调色板（Palette）

> 调色板是「颜色原料」，通过 token 引用，**不直接用于组件**。按角色列出 + 各自色阶范围。

| 调色板 | 角色 | 适用场景 | 色阶范围（如未填请留 `[待填]`） |
|---|---|---|---|
| `[品牌主色名，如 primary / brand]` | 主行动色 | 主要 CTA 按钮、关键链接、品牌强调 | `[50, 100, 200, 400, 500, 600, 700, 800, 900]` |
| `[次要色名，如 accent]` | 辅助强调 | 次要行动、链接 hover、辅助 highlight | `[同上]` |
| `[success / warning / danger / info]` | 语义状态 | 成功/警告/错误/提示 | `[同上]` |
| `[neutral / gray / slate]` | 中性灰阶 | 文本、背景、边框、disabled | `[50, ..., 900]` |

---

## 2. 语义令牌（Semantic Tokens）

> 组件**必须引用语义 token，不直接引用调色板**。语义层把调色板映射到使用场景。

### 2.1 文本（Text）

| Token 名 | 用途 | 引用调色板（由项目填具体值） |
|---|---|---|
| `text-primary` | 主要正文 | `[如 primary-700]` |
| `text-secondary` | 次要文本 | `[如 neutral-600]` |
| `text-muted` | 辅助/禁用 | `[如 neutral-400]` |
| `text-on-primary` | 主色背景上的文字 | `[如 white / neutral-50]` |
| `text-link` | 链接 | `[如 primary-600]` |
| `text-danger` | 错误文字 | `[如 danger-600]` |

### 2.2 背景（Background）

| Token 名 | 用途 | 引用调色板 |
|---|---|---|
| `bg-page` | 页面底色 | `[如 neutral-50]` |
| `bg-card` | 卡片底色 | `[如 white]` |
| `bg-elevated` | 浮层/Menu/Drawer | `[如 white]` |
| `bg-overlay` | 模态遮罩 | `[如 neutral-900 + 50% alpha]` |
| `bg-hover` | 交互 hover | `[如 neutral-100]` |
| `bg-active` | 交互按下 | `[如 neutral-200]` |
| `bg-disabled` | 禁用态 | `[如 neutral-100]` |

### 2.3 边框（Border）

| Token 名 | 用途 | 引用调色板 |
|---|---|---|
| `border-default` | 默认边框 | `[如 neutral-200]` |
| `border-muted` | 次要边框 | `[如 neutral-100]` |
| `border-strong` | 强调边框 | `[如 neutral-300]` |
| `border-danger` | 错误边框 | `[如 danger-300]` |
| `border-focus` | 聚焦环 | `[如 primary-500]` |

### 2.4 状态变体（State Variants）

| 变体后缀 | 适用 |
|---|---|
| `-default` | 默认/静止态 |
| `-hover` | 鼠标悬停 |
| `-active` / `-pressed` | 按下/激活 |
| `-focus` | 聚焦可见（键盘 a11y） |
| `-disabled` | 禁用 |
| `-muted` | 低对比度（如辅助信息） |

---

## 3. 主题（Themes）

| 主题 | 状态 | 说明 |
|---|---|---|
| `light` | 默认 | 主应用主题 |
| `dark` | 待定 | 如项目支持，[由项目填入切换策略] |
| `high-contrast` | 可选 | a11y 增强，如需支持请补字段 |

**主题切换约定**：组件代码**只引用语义 token**（如 `text-primary`），不直接引用调色板（不允许 `colors.primary[700]`）。切换主题时改 token→palette 映射，组件零改动。

---

## 4. 命名约定

### 4.1 Token 命名格式

推荐 `category-role-variant` 三段式：

```
{category}-{role}-{variant}
├── text    primary default    （text-primary-default）
├── bg      primary hover      （bg-primary-hover）
├── border  danger             （border-danger）
└── icon    secondary muted    （icon-secondary-muted）
```

### 4.2 项目实际命名兼容

| 项目 UI 框架 | 实际 token 前缀 | 与本规范映射 |
|---|---|---|
| Tailwind | `text-primary-500` / `bg-primary-100` 等 | 用 50-900 色阶替代 role-variant |
| Ant Design | `colorPrimary` / `colorBgContainer` | 单驼峰 + 无连字符 |
| 自研 | `[由项目填入]` | 建议遵循 `category-role-variant` 三段式 |

如果项目用其他框架，**在 `understanding/&lt;项目名&gt;.md` 的 color_ref 段引用本文档**并标注实际命名映射：

```markdown
## 颜色引用
color_ref: doc/protocol/coding-standards/color-tokens.md
framework: Tailwind 3.4
mapping:
  text-primary-default: text-gray-900
  bg-primary-hover: bg-primary-50
```

---

## 5. 本项目如何记录

`understanding/&lt;项目名&gt;.md` 增加以下字段（**不是**复制本文档内容）：

```markdown
## 颜色引用

- color_ref: doc/protocol/coding-standards/color-tokens.md
- framework: [Tailwind / Ant Design / 自研]
- palette: [如 primary / brand / slate]
- state_style: [项目实际状态变体命名，如 hover:light-50 / focused:primary-200]
- theme: [light / dark / both]
- 项目特例：[如有不在规范定义内的颜色用法，描述原因与影响范围]
- 证据：[如 styles/theme.css 第 N 行、tailwind.config.js L20-30]
```

---

## 6. 历史例外与待确认项

- 项目特例（不在规范内的颜色用法）：
  - [待补充]
- 验证方式（项目方可改动）：

> 协议区 task.md 与 `00-基础调查问卷.md` 的 `[待确认]` 项应与本节双向引用，避免悬挂。
