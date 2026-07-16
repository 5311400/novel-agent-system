# 多 Agent 小说写作系统（Novel Agent System）

基于 7 家 AI（DeepSeek、智谱清言、Kimi、豆包、通义千问、ChatGPT）× 2 轮深度咨询构建的最优架构方案。

## 架构概览

```
Skill 定流程 + Agent 干专活 + Artifact 管流转 + Data 保一致
        ↓            ↓              ↓              ↓
   技能模块化      角色分工       流水线管理      长期记忆
```

## 项目结构

```
novel-agent-system/
├── AGENTS.md               # 项目级全局规则
├── .gitignore              # Git 忽略规则
├── skills/                 # Skill 层——跨平台通用
│   ├── shared/             # 全局通用 Skill
│   │   ├── 01_novel-standards.md       # 网文连载通用规范
│   │   ├── 02_data-access-rules.md     # 档案读取/写入标准
│   │   └── 03_handoff-protocol.md      # Agent 交接协议
│   └── agents/             # 各岗位私有 Skill
│       ├── coordinator.md              # 总控调度
│       ├── world-building.md           # 世界观设定维护
│       ├── character-keeper.md         # 人物连贯性追踪
│       ├── chapter-drafting.md         # 章节起草
│       ├── style-guide.md              # 文风一致性指南
│       ├── polish-review.md            # 润色与质检
│       └── token-efficient-delegation.md # Token高效委派协议
├── agents/                 # Agent 配置层
│   ├── codex/              # Codex 端 .toml 配置
│   │   ├── chief-editor.toml
│   │   ├── world-builder.toml
│   │   ├── character-keeper.toml
│   │   ├── chapter-writer.toml
│   │   └── polish-editor.toml
│   └── workbuddy/          # Work Buddy 端配置
├── artifacts/              # Artifact 层——中间产物
├── data/                   # Data 层——长期记忆
│   ├── INDEX.md            # 全局版本号 GV 管理
│   ├── .lock-policy.md     # 写入锁规则
│   ├── project-board.md    # 项目进度看板
│   ├── timeline.md         # 时间线
│   ├── plot-log.md         # 剧情摘要
│   ├── changelog.md        # 变更日志
│   ├── world/              # 世界观设定
│   ├── characters/         # 人物档案
│   └── chapters/           # 已发布章节
├── runtime/                # 运行时文件(.gitignore)
│   ├── .signals/           # Work Buddy 信号文件
│   ├── .locks/             # 文件锁
│   ├── .violations.log     # 权限违规记录
│   └── .tmp/               # 临时写入缓冲
└── tests/                  # 自动化测试
    ├── skill-triggers/
    └── consistency-checks/
```

## 快速开始

### 第一步：配置 Agent
在 Codex 中加载 agents/codex/ 下的 .toml 文件，或根据 Work Buddy 对应的配置。

### 第二步：撰写你的小说
1. 填充 data/world/ 下的世界观设定
2. 填充 data/characters/ 下的人物档案
3. 通过总控 Agent 开始章节创作

### 第三步：工作流（每章重复）
总控→并行收集设定/人物→起草→质检→冲突仲裁→原子写入→归档

## 核心设计要点
1. **原子锁+版本向量**：LOCK 原子独占创建 + 僵尸锁清理；全局GV+分资源版本向量
2. **读取侧防过期**：子Agent快照绑定GV，过期产出直接驳回
3. **写入事务原子化**：先缓存再全量落地，changelog绑定GV+hash
4. **读写分级锁**：共享读/排他写分级
5. **Token控制**：三明治压缩法(300 Token) + 分级模型
6. **冲突仲裁**：硬规则→版本向量→变更提案→节奏校验→人机回环
7. **Work Buddy 适配**：文件驱动+轻量信号模式

## 咨询过程文件
- 汇总_小说agent架构_第1轮.md — 6家AI首轮建议
- 汇总_小说agent架构_第2轮反馈.md — 5家AI第二轮评审
- 小说agent写作系统_综合架构方案.md — 完整架构方案书
