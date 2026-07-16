# Skill：Agent 交接协议

## 交接报文格式
所有 Agent 间的消息传递必须使用以下标准化格式：

```
[任务ID]: {UUID}
[来源Agent]: {角色名}
[目标Agent]: {角色名}
[Snapshot-GV]: {数字}
[WV]: {世界观版本}
[CV]: {人物档案版本}
[CH-V]: {章节分卷版本}
[核心产出]: {正文/列表}
[变更摘要]: {改了哪些文件}
[待办提醒]: {下次需处理的伏笔/问题}
```

## 规则
1. 禁止传递整本前 N 章全文——使用结构化摘要
2. Coordinator 分发任务时同步下发最新资源版本
3. 子 Agent 接收任务时强制刷新 data/INDEX.md 版本，清除本地缓存
4. Work Buddy 使用文件驱动 + 轻量信号模式（详见下文）

## Work Buddy 适配：文件驱动 + 轻量信号模式

### 差异对照
| 维度 | Codex | Work Buddy |
|------|-------|-----------|
| Agent 调度 | 原生 sub-agent/handoff | 无原生机制，多会话模拟 |
| Handoff | spawn_agent + wait | 文件信号 + 轮询 |
| Skill 加载 | skills/ 目录软链接 | 知识库共享或手动复制 |
| 会话隔离 | 子 Agent 独立上下文 | 独立角色会话 |

### 信号协议
```
发送方：
  写信号文件到 data/.signals/，文件名为 {任务ID}.signal
  文件内容包含完整交接报文

接收方：
  轮询 data/.signals/ 目录（每 5s）
  匹配到自己的 {任务ID}.signal → 读取 → 处理 → 删除信号

总控：
  只读 data/.signals/ → 做决策 → 写新信号
```

### Work Buddy 版本绑定
- 交接报文强制携带：Snapshot-GV / WV / CV / CH-V
- 每次新任务开始前，强制刷新 data/INDEX.md 版本
- 子 Agent 缓存过期自动失效

### 标准化交接报文（Codex + Work Buddy 通用）
```
[任务ID]: {UUID}
[来源Agent]: {角色名}
[目标Agent]: {角色名}
[Snapshot-GV]: {数字}
[WV]: {世界观版本}
[CV]: {人物档案版本}
[CH-V]: {章节分卷版本}
[核心产出]: {正文/列表}
[变更摘要]: {改了哪些文件}
[待办提醒]: {下次需处理的伏笔/问题}
```
