# 多 Agent 小说写作系统 —— 综合架构方案

> 基于 DeepSeek、智谱清言、Kimi、豆包、通义千问、ChatGPT 共 7 家 AI × 2 轮深度咨询整理

---

## 一、架构选型结论

**Skill + Multi-Agent 混合架构 —— 7 家 AI 零分歧**

| 方案 | 劣势 | 适用场景 |
|------|------|---------|
| ❌ 纯 Skill（单 Agent） | 上下文爆炸，写到第 50 章就崩；串行无法并行；职责混杂 | 短篇 / 万字内一次性文稿 |
| ❌ 纯 Multi-Agent（无 Skill） | 每次 handoff 重复传递规则；输出标准不统一；漏检严重 | 临时碎片化写作 |
| ✅ **Skill + Multi-Agent 混合** | 每个 Agent 用专属 Skill 固化知识库；职责隔离、流水线流转；双平台通用 | **百万字长篇连载（你的场景）** |

**核心公式：Skill 定流程 + Agent 干专活 + 文件系统保记忆 + Artifact 管流转 = 不崩坏的连载系统**

---

## 二、Agent 角色划分

### 推荐架构（1 总控 + 4-5 个核心子 Agent）

| Agent 角色 | 职责 | 专属 Skill | 核心产出 |
|-----------|------|-----------|---------|
| **总控 Agent（主编）** | 任务分解、进度追踪、冲突仲裁 | planning.md, quality-gate.md | 任务清单、最终交付 |
| **世界观设定师（WorldBuilder）** | 维护地理、势力、能力体系、时间线、硬规则 | world-building.md | 设定档案、变更日志 |
| **人物连贯性管家（CharacterKeeper）** | 追踪角色档案、关系网、成长轨迹；OOC 校验 | character-tracker.md | 人设一致性报告 |
| **章节撰稿人（ChapterWriter）** | 根据大纲和设定起草章节正文 | chapter-drafting.md | draft_chapter_X.md |
| **文风润色&校验官（Editor/QualityJudge）** | 润色文笔、消除 AI 腔、一致性检查 | style-guide.md, polish-review.md | 质检报告、终稿 |

### 可选扩展 Agent
- **选题 Agent**（ChatGPT 建议）：市场分析、爆点设计
- **剧情分镜策划 PlotPlanner**（豆包建议）：卷大纲、章小节拆分
- **冲突复审 Checker**：跨卷设定/人设全局扫描
- **回溯修正 Retroactive Agent**（智谱清言建议）：修改早期设定后修正后续章节

---

## 三、Skill 编写策略

### 分层设计（Kimi + 豆包共识）

```
skills/
├── shared/            # 全局共享 Skill（所有 Agent 加载）
│   ├── 01_novel-standards.md     # 网文连载通用规范
│   ├── 02_data-access-rules.md    # 档案读取/写入标准
│   └── 03_handoff-protocol.md     # Agent 交接协议
└── agents/            # 各岗位私有 Skill（仅对应 Agent 加载）
    ├── world-building.md
    ├── character-keeper.md
    ├── chapter-drafting.md
    ├── style-guide.md
    └── polish-review.md
```

### Skill 模板结构（通义千问 + 豆包推荐）
每份 Skill 统一为 4 段式：
1. **岗位定位**：权限边界、禁止越权的明确声明
2. **领域知识库**：固化业务规则
3. **强制校验规则**：不可省略的检查步骤
4. **标准输出模板**：统一的结构化输出

### Description 写法（Kimi 优化）
- 格式：`"When [触发场景] needs [能力] returns [输出格式]"`
- "handles" → "needs"（更接近用户表达习惯）
- **触发词密度量化标准**：准确率 > 90%，误触发 < 5%，漏触发 < 5%
- 提供 `test-skill-trigger.py` 自动化测试脚本

---

## 四、项目目录结构

```
project/
├── skills/                # Skill 层——跨平台通用
│   ├── shared/            # 全局通用 Skill
│   └── agents/            # 各岗位私有 Skill
├── agents/                # Agent 配置层——平台单独定义
│   ├── codex/             # Codex 端 .toml 配置
│   └── workbuddy/         # Work Buddy 端配置
├── artifacts/             # Artifact 层——中间产物（ChatGPT 提出）
│   ├── chapter-001.draft.md      # 草稿
│   ├── chapter-001.review.json   # 质检报告
│   └── chapter-001.final.md      # 终稿
├── data/                  # Data 层——长期记忆（受版本控制）
│   ├── INDEX.md           # 全局版本号 GV 管理（豆包提出）
│   ├── world/             # 世界观设定
│   ├── characters/        # 人物档案
│   ├── chapters/          # 已发布章节
│   ├── timeline.md        # 时间线
│   ├── plot-log.md        # 每章 100 字剧情梗概
│   ├── project-board.md   # 项目进度看板
│   ├── .write.lock        # 原子排他写锁（含 expire_ts）
│   └── .read.shared       # 共享读标记
├── runtime/               # 运行时文件（进 .gitignore，Kimi 提出）
│   ├── .signals/          # Work Buddy 信号文件
│   ├── .locks/            # 文件锁
│   ├── .violations.log    # 权限违规记录
│   └── .tmp/              # 临时写入缓冲
└── tests/                 # 自动化测试（Kimi 提出）
    ├── skill-triggers/
    └── consistency-checks/
```

---

## 五、工作流编排 —— 写一章的完整流程

```
用户：写第 N 章
↓
总控 Agent
├── 读取 project-board.md → 确认前置依赖无阻塞
├── 检查 INDEX.md → 获取当前全局版本 GV
├── 并行派发（只读，创建共享读标记）：
│   ├── WorldBuilder → "提供第 N 章涉及的设定"
│   └── CharacterKeeper → "提供出场角色的当前状态"
├── 收集结果 → 校验快照版本（过期则驳回重跑）
├── 生成 chapter-brief-N.md
├── 派发 ChapterWriter → "按 brief 起草第 N 章"
├── 收集 draft-N.md
├── 派发 polish-editor → "质检第 N 章"
├── 收集质检报告
├── 冲突仲裁（四层）：
│   ① Skill 硬规则校验 → 拦截 OOC / 设定冲突
│   ② 版本向量仲裁（WV/CV/CH-V）→ 自动合并可合并变更
│   ③ 变更提案审批（Change Proposal）
│   ④ 人机回环 → 不可调和暂停等待
├── 原子批量写入（创建排他写锁）：
│   ├── 更新 data/ 档案
│   ├── 追加 changelog（绑定 GV+hash）
│   ├── 递增 INDEX.md GV
│   └── 释放写锁
└── 返回最终正文
```

---

## 六、Token 成本控制（DeepSeek 核心贡献）

### "Token 高效子 Agent 委派" Skill 框架

### 1. 委派决策树
| 条件 | 操作 |
|------|------|
| 涉及 >3 个独立实体的信息检索 | **必须委派** |
| 单一句子润色、已知上下文微小修改 | **禁止委派**，总控自己处理 |
| 信息收集类（查询世界观+查询角色） | **可以并行** |
| 生成类（写作、质检） | **强制串行** |

### 2. "三明治压缩法" —— 总 Prompt 控制在 300 Token
```
【必须上下文】(50词内) 当前章节梗概 + 前一章结尾
【唯一任务】(30词内) 具体要产出的东西，量化
【硬性约束】(50词内) 遵守世界观第X条 + 角色当前状态
```

### 3. 子Agent 输出 "极简归档" 格式
```
[核心产出]：正文/列表
[变更摘要]：仅列出改了哪些设定文件
[待办提醒]：下一章必须解决的伏笔，不超过 2 条
```

### 4. 上下文续写策略（替代全文传递）
只传递 3 个片段：① 上一章结尾 200 字、② 当前章节 3 个关键节拍、③ 正在对话的 2 个角色的最新性格标签

### 5. 额外控制措施
- **分级模型策略**：信息查询用轻量模型，写作和质检用最强模型
- **硬缓存**：高频查询（主角姓名等）禁止调子 Agent，总控从 rules.json 检索
- **动态降级**：遇到复杂章节时临时提高 max_threads
- **最大深度**：Codex 设 max_depth=1，max_threads=4

---

## 七、冲突仲裁与数据一致性

### 四层仲裁机制

| 层级 | 机制 | 说明 |
|------|------|------|
| 第 1 层 | **Skill 硬规则校验** | rules.md 不可违背，违规强制阻断 |
| 第 2 层 | **版本向量仲裁** | WV/CV/CH-V 分资源版本号，高覆盖低，无冲突直接合并 |
| 第 3 层 | **变更提案（Change Proposal）** | 改设定需说明理由，全局影响扫描 |
| 第 4 层 | **人机回环** | 不可调和冲突标记"需人工介入" |

### 原子锁与版本控制（豆包核心贡献）

- **LOCK 原子化**：OS 原生独占创建文件，消除竞态条件
- **僵尸锁清理**：锁文件含 expire_ts（120s 超时），总控常驻巡检
- **全局版本号 GV**：data/INDEX.md 维护，每次批量写入 GV+1
- **快照绑定**：子Agent 产出必须标注 Snapshot-GV，过期驳回重跑
- **写入事务原子化**：先缓存再全量落地，"要么全改要么不改"
- **读写分级锁**：共享读标记 (.read.shared) 支持并行只读
- **changelog 完整性**：绑定 GV+batch_id+hash

### 节奏控制（智谱清言补充）
- **宏观节奏校验**：Coordinator 扫描 plot-log.md，强制战斗/舒缓场景交替
- **"蝴蝶效应"处理**：Retroactive Agent 应对早期设定修改，锁定影响域→生成补丁→一致性重置

---

## 八、Work Buddy 适配方案

### 与 Codex 的差异
| 维度 | Codex | Work Buddy |
|------|-------|-----------|
| Agent 调度 | 原生 sub-agent/handoff | 无原生机制，多会话模拟 |
| Handoff | spawn_agent + wait | 文件信号 + 轮询 |
| Skill 加载 | skills/ 目录软链接 | 知识库共享或手动粘贴 |
| 会话隔离 | 子 Agent 独立上下文 | 独立角色会话 |

### 适配策略：文件驱动 + 轻量信号（Kimi 建议）
- 总控只负责读 `data/.signals/` 信号文件、做决策、写新信号
- 子 Agent 会话轮询信号文件，读取共享 data/ 目录
- 每次新任务强制刷新 data/INDEX.md 版本，清除本地缓存
- 标准化交接报文强制携带：Snapshot-GV / WV / CV / CH-V

---

## 九、避坑指南（各家汇总）

| # | 坑 | 解法 | 来源 |
|---|-----|------|------|
| 1 | **Token 成本失控** | 三明治压缩法 + 分级模型 + 增量摘要 | DeepSeek / Kimi |
| 2 | **设定/人设遗忘（50章后崩）** | 文件系统即记忆 + 分片读取 + 结构化增量摘要 | 智谱清言 / 豆包 |
| 3 | **Skill 触发不稳定** | description 触发词前置 + 量化测试脚本 | Kimi |
| 4 | **各说各话 / 并行冲突** | 文件锁 + 读写分离 + 快照版本校验 | 豆包 |
| 5 | **AI 腔反复出现** | style-guide 列出替代词 + 正例库 | Kimi / ChatGPT |
| 6 | **写作Agent越权改设定** | Skill 第一条写死权限边界 + 总控拦截 | 豆包 / 通义千问 |
| 7 | **核心决策不要多 Agent 投票** | 总控独断，不搞 Agent 投票 | 通义千问 |
| 8 | **写作Agent不要做规划** | 总控下发任务书，写作只执行 | ChatGPT |
| 9 | **审核不要最后才用** | 每章完成后立即审核，不积压 | ChatGPT |
| 10 | **没有版本控制** | data/ 目录进 git，runtime/ 进 .gitignore | Kimi |
| 11 | **跨平台目录不统一** | skills/shared/ + agents/codex/ + agents/workbuddy/ | Kimi |
| 12 | **蝴蝶效应——改前文崩后文** | Retroactive Agent 锁定影响域 → 批量修正 | 智谱清言 |

---

## 十、MVP 实施路线图

| 阶段 | 内容 | 目标 |
|------|------|------|
| **Week 1** | 编写 3 个核心 Skill（world-building / character-tracker / chapter-drafting）+ 搭建 `skills/` 和 `data/` 目录 | 技能库就绪 |
| **Week 2** | 在 Codex 配置 2 个 Agent（总控 + ChapterWriter），跑通"写一章"的串行流程 | 最小闭环 |
| **Week 3** | 加入润色/校验 Agent（polish-review + style-guide），建立"起草→质检→修改"循环 | 质量保障 |
| **Week 4** | 加入并行（WorldBuilder + CharacterKeeper 同时查询），实现 project-board 状态机；加 LOCK 机制和 GV 版本控制 | 效率提升 |
| **Month 2** | 适配 Work Buddy，验证 Skill 跨平台兼容性；加入 Retractive Agent / 蝴蝶效应处理 | 双平台跑通 |
| **长期** | 加入选题Agent、剧情策划Agent；优化 Token 控制；加入自动化测试套件 | 生产级系统 |

---

## 附：各 AI 核心贡献速查

| AI | 一句话特点 | 第1轮核心贡献 | 第2轮核心贡献 |
|----|-----------|-------------|-------------|
| **DeepSeek** | Token 成本控制专家 | 共享知识库 + Token 高效委派概念 | 三明治压缩法完整框架 + 硬缓存 |
| **智谱清言** | 最担心长线维护 | Stateful Pipeline + 读写分离 | Change Proposal + Retractive Agent |
| **Kimi** | 最务实的架构师 | 5 个完整 Skill 模板 + TOML 配置 | runtime/ + tests/ 目录 + 文件信号模式 |
| **豆包** | 最硬核的技术评审 | 分层 Skill + 流程锁 | 6个技术漏洞 + 6个补丁（原子锁/GV/版本向量） |
| **通义千问** | 最清醒的避坑者 | 渐进式披露 + "万能指令包"警告 | — |
| **ChatGPT** | 最像产品经理 | 三级审核 + 小说目录结构 | Artifact 层 + 5层架构 + 开源项目评价 |
