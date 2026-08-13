# AGENTS.md — protocol 项目级规则

## 项目简介

并行开发规程（Parallel Development Protocol）v3.0 —— 一套对话驱动的多 AI 协作开发方法论，规定从空白目录到项目发版的完整过程。

本仓库 = 规程文档（中英双语）+ 配套 MCP server（规程 L2 工具层）。

## 技术栈

| 部分 | 技术 |
|------|------|
| 规程文档 | Markdown，`zh/`（中文）+ `en/`（英文）双语，9 份文件 |
| MCP server | Python ≥3.10，`mcp>=2,<3`，`pydantic>=2,<3`，SQLite 持久化 |
| 测试 | pytest，位于 `mcp/tests/` |
| 依赖锁定 | `mcp/pyproject.toml` |

> 注意：mcp SDK 2.x 已移除 `fastmcp` 模块，统一用 `mcp.server.mcpserver.MCPServer`。

## 代码风格

- 注释用中文。
- 小步提交：一个提交 = 一个可独立回滚、独立理解、独立 review 的逻辑变更。
- Conventional Commits 规范。
- 提交粒度：`fix`（代码/功能）与 `docs`（文档）分开提交；`fix` 在前、`docs` 在后（docs 对齐 fix 后的代码真相）。

## 测试要求

- 核心逻辑必须补测试：`checker` 校验规则、`store` 持久化、`server` tool 行为。
- 改动后跑 `cd mcp && python -B -m pytest tests/ -q`，全绿才算完成。

## 文档要求

- 项目级文档放 `doc/`。
- 非临时文档（设计、决策、规范、笔记）归档到 `/Users/Repository/memory/protocol/doc/`；临时草稿留在项目内，不归档。

## 协作约定

- 讨论方向文档只存大方向与议题状态，不存细节（见 `/Users/canyu/AI work/protocol-讨论方向.md`）。
- 讨论产生实质结论时，及时写入持久记忆：全局反馈写入 `~/.agents/memory/`，项目事实写入 ZCode 项目记忆目录。
