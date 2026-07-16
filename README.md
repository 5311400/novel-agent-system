# Novel Agent System — 多 Agent 小说写作系统

Skill 定流程 + Agent 干专活 + Artifact 管流转 + Data 保一致

一款基于 **Skill + Multi-Agent 混合架构**的网文长篇连载写作系统。  
通过 6 个 AI Agent 协作完成世界构建、人物追踪、章节起草、文风检测、深度质检的全流程自动化。

---

## 架构概览

```
│ Coordinator(总控) │ ← 调度中心
──────────────────────────
│ WorldBuilder  │ CharacterKeeper │ ChapterWriter │  ← 生成层
│ StyleGuard    │ PolishEditor    │               │  ← 质检层
──────────────────────────
│       data/ 目录（文件系统即记忆）            │  ← 持久层
```

## Agent 角色

| Agent | 职责 |
|-------|------|
| **Coordinator** | 状态机调度、任务分解、冲突仲裁、原子锁管理 |
| **WorldBuilder** | 地理/势力/力量体系/规则档案维护，主动校验跨档案引用 |
| **CharacterKeeper** | 角色档案维护、OOC 校验、跨章节连续性检查 |
| **ChapterWriter** | 按节拍表起草正文，遵守首尾锚点，不新增设定 |
| **StyleGuard** | AI腔检测（24种模式）、7:2:1文风配比、句长/对话密度检查 |
| **PolishEditor** | 战力/OOC/设定/逻辑三级错误分级、深度质检报告 |

## 工作流（写一章）

```
ChapterWriter 完稿
    ↓
StyleGuard 文风报检
    ↓
Coordinator 决策
    ↓
PolishEditor 深度质检（三级分级）
    ↓
Coordinator 仲裁 → 归档
```

## 特色

- **原子锁 + 版本向量**：LOCK 独占创建，快照绑定 GV，过期驳回重跑
- **四层冲突仲裁**：硬规则 → 版本向量 → 变更提案 → 人机回环
- **Token 控制**：三明治压缩法 ≤300 Token，分级模型策略
- **自我进化**：每 10 章一轮错误分析 → 补丁报告 → 人工确认 → 落地
- **跨平台兼容**：Codex 原生 sub-agent + Work Buddy 文件信号模式

## 项目结构

```
novel-agent-system/
├── skills/            # Skill 层 — 跨平台通用
│   ├── shared/        # 全局共享（一致性规则、数据访问、交接协议）
│   └── agents/        # 各岗位私有 Skill
├── agents/            # Agent 配置层
│   ├── codex/         # Codex 端 .toml 配置
│   └── workbuddy/     # Work Buddy 配置样板
├── data/              # 长期记忆（版本控制）
│   ├── world/         # 世界观档案 + .example 示例
│   ├── characters/    # 人物档案
│   └── chapters/      # 已发布章节
├── docs/              # 架构设计文档
├── tests/             # 测试策略
└── artifacts/         # 中间产物（draft→review→final）
```

## 开始使用

### 第一步：选择你的平台

- **Codex**：加载 `agents/codex/chief-editor.toml` 作为主 Agent
- **Work Buddy**：复制 `agents/workbuddy/config.sample.toml` 为 `config.toml`
- **通用 AI（ChatGPT/DeepSeek 等）**：把 `docs/投喂包_系统概要.md` 作为开场提示词

### 第二步：初始化

```
/init
```

### 第三步：写第一章

```
/write-chapter 1
```

---

> 系统基于 7 家 AI（DeepSeek、智谱清言、Kimi、豆包、通义千问、ChatGPT）× 3 轮深度咨询构建。  
> 设计文档见 `docs/` 目录。
