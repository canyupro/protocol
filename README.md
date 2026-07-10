# Parallel Development Protocol — 并行开发规程

> A conversation-driven multi-AI collaborative development methodology. From an empty directory to project release.
> 对话驱动的多 AI 协作开发方法论。从空白目录到项目发版。

---

## Directory Structure · 目录结构

```
protocol/
├── README.md              # This file · 本文件
├── zh/                    # 中文版 (Chinese)
│   ├── 00-总纲.md
│   ├── 01-串行对话-Round0至Round2b.md
│   ├── 02-串行对话-Round3至Round5与启动门.md
│   ├── 03-并行开发与收尾-Round6至Round8.md
│   ├── 04-附录-触发器与模板全集.md
│   ├── 05-操作速查卡.md
│   ├── 06-约束介质与MCP.md
│   ├── 07-继承介质与介入机制.md
│   └── 08-前端与异步分工.md
├── en/                    # English 英文版
│   ├── 00-Overview.md
│   ├── 01-Serial-Conversation-Round0-to-Round2b.md
│   ├── 02-Serial-Conversation-Round3-to-Round5-and-Launch-Gate.md
│   ├── 03-Parallel-Development-and-WrapUp-Round6-to-Round8.md
│   ├── 04-Appendix-Triggers-and-Templates.md
│   ├── 05-Quick-Reference-Card.md
│   ├── 06-Constraint-Media-and-MCP.md
│   ├── 07-Inheritance-Media-and-Intervention.md
│   └── 08-Frontend-and-Async-Division.md
└── .gitignore
```

---

## Version · 版本

| Version | Date | Description |
|---|---|---|
| v3.0 | 2026-07-03 | Formal release · 正式版 — self-contained complete protocol · 自包含完整规程 |

---

## What's Inside · 内容概述

**9 files, 21 clauses, 65+ triggers.** Three-domain coverage:

- **Complete Development Process**: Rounds 0–8 Serial → Parallel → Wrap-Up, including frontend and AI Agent engineering nodes
- **Full Business Development Paradigms**: CRUD + Frontend + AI Agent (RAG / Memory / SSE / Degradation / Prompt versioning / Crisis short-circuit) + Async division
- **Special Mechanisms**: Constraint media stratification (L0/L1/L2) + Inheritance media (Fork / Sub-agent / Snapshot) + Intervention (four escalation tiers) + MCP tools + Declaration Card + Acceptance Lock + Environment Runbook

**9 份文件、21 条条款、65+ 触发器。** 三件事全覆盖：

- **完整开发流程**：Round 0-8 串行→并行→收尾，含前端和 AI Agent 工程节点
- **全业务开发范式**：CRUD + 前端 + AI Agent + 异步分工
- **特殊机制**：约束介质分层 + 继承介质 + 介入机制 + MCP + 声明卡 + 验收锁 + Runbook

---

## File Map · 文件导航

| # | EN | ZH | Content | When to Read |
|---|---|---|---|---|
| 00 | [Overview](en/00-Overview.md) | [总纲](zh/00-总纲.md) | Philosophy, process overview, tracks, freeze rules, clause index | First |
| 01 | [Rounds 0–2b](en/01-Serial-Conversation-Round0-to-Round2b.md) | [Round 0–2b](zh/01-串行对话-Round0至Round2b.md) | Seeding → Requirements → Tech stack → Directory + Contract freeze | Project startup |
| 02 | [Rounds 3–5 & Gate](en/02-Serial-Conversation-Round3-to-Round5-and-Launch-Gate.md) | [Round 3–5 与启动门](zh/02-串行对话-Round3至Round5与启动门.md) | Standards → DB+Memory → Framework+SSE+Crisis → Freeze audit + Gate | After R2b |
| 03 | [Rounds 6–8](en/03-Parallel-Development-and-WrapUp-Round6-to-Round8.md) | [Round 6–8](zh/03-并行开发与收尾-Round6至Round8.md) | Parallel coding → Integration → Release | After gate |
| 04 | [Appendix](en/04-Appendix-Triggers-and-Templates.md) | [附录](zh/04-附录-触发器与模板全集.md) | All triggers, decision record, PPM, snapshot, intervention templates | Quick lookup |
| 05 | [Quick Ref](en/05-Quick-Reference-Card.md) | [速查卡](zh/05-操作速查卡.md) | Per-round actions, Runbook, acceptance lock, MCP, intervention | Keep open |
| 06 | [Constraint & MCP](en/06-Constraint-Media-and-MCP.md) | [约束介质与MCP](zh/06-约束介质与MCP.md) | L0/L1/L2 layers, MCP specs, Declaration Card, Acceptance Lock | Rules deep-dive |
| 07 | [Inheritance & Intervention](en/07-Inheritance-Media-and-Intervention.md) | [继承介质与介入](zh/07-继承介质与介入机制.md) | Fork/Sub-agent/Snapshot, escalation, state machine, platform matrix | Collaboration deep-dive |
| 08 | [Frontend & Async](en/08-Frontend-and-Async-Division.md) | [前端与异步分工](zh/08-前端与异步分工.md) | Completion def, perspective convergence, single-source View, executor-first | Frontend/division |

---

## Reading Order · 阅读顺序

1. **00-Overview** — understand the philosophy and landscape
2. **06-Constraint-Media-and-MCP** — how rules take effect (referenced by 01/02/03)
3. **07-Inheritance-Media-and-Intervention** — cross-session collaboration (referenced by 01/02/03)
4. **08-Frontend-and-Async-Division** — frontend & division protocol (referenced by 01/02/03)
5. **01 → 02 → 03** — execute the full workflow
6. **04-Appendix** — template library for execution
7. **05-Quick-Reference-Card** — keep open alongside during execution

---

## Key Features · 核心特性

- **Three-Tier Freeze**: Hard-Freeze / Soft-Freeze / Draft — progressive certainty
- **Three Tracks**: Demo Mode / Standard / Premium — fit project scale
- **Launch Gate**: 8 hard conditions before parallelization
- **5-Dimension Audit**: Code standards + Dynamic testing + Contract consistency + Docs + Postmortem
- **21 Embedded Clauses**: §4.1–§4.21 woven into Round workflow
- **Platform Branching**: v3.0-ZCode (fork + sub-agent) / v3.0-Generic (snapshot mailbox)

---

## Related Repositories · 相关仓库

- [UpgradeES](https://github.com/canyupro/UpgradeES) — Reference implementation (K12 education platform)
- [protocol-mcp](https://github.com/canyupro/protocol) — This repository
