# 编码规约（Coding Standards）

> 协议插件内携带的「普适编码规约根目录」，不随 `/protocol:init` 复制到项目。
> 项目方按需复制/引用其中的规范，结合本项目 `understanding/` 下的实际用法记录。

## 文件索引

| 文件 | 内容 | 引用方式 |
|---|---|---|
| [naming.md](naming.md) | 目录 / 模块 / 类型 / 接口 / 函数 / 测试的命名约定 | `understanding/&lt;项目&gt;.md` 用 `naming_ref:` 字段引用 |
| [color-tokens.md](color-tokens.md) | 颜色调色板、语义 token、主题约定 | `understanding/&lt;项目&gt;.md` 用 `color_ref:` 字段引用 |

## 原则

1. **本目录是规范定义**（普适、跨项目可复用），`understanding/` 是项目如何实践的事实记录。两者通过 `ref:` 字段引用，**不复制内容**。
2. **字段框架定下来，具体值由项目填入**——避免插件替你预设色值、命名风格这种主观选择。
3. **修改本目录需走 PR + 独立验证方审查**，因为改动会影响所有引用此规范的项目。

## 引入流程（项目方）

1. `/protocol:init` 完成后，复制本目录到项目 `doc/protocol/coding-standards/`
2. 在 `understanding/&lt;项目名&gt;.md` 加 `color_ref:` / `naming_ref:` 字段指向上述文件
3. 项目方填入本项目实际使用的色值、命名风格
4. 与 `understanding/` 下项目专用文件（如 `understanding/naming.md`）保持双向引用，避免内容漂移
