# Work Buddy 适配配置

## 架构差异
Work Buddy 没有 Codex 的原生 sub-agent/handoff 机制，使用**文件驱动 + 轻量信号模式**。

## 工作模式
```
总控（一个会话）：
  └── 轮询 data/.signals/ 信号文件
  └── 做决策
  └── 写新信号文件

子 Agent（独立会话）：
  └── 轮询 data/.signals/ 信号文件
  └── 匹配到自己的任务
  └── 读取共享 data/ 目录
  └── 执行任务
  └── 写产出到 artifacts/
  └── 删除信号文件
```

## 配置步骤
1. 将 skills/shared/ 内容导入各 Agent 的知识库或作为系统提示词
2. 每个 Agent 独立的 Skill 按角色导入
3. 确保各 Agent 能访问 data/ 目录（网络共享或同步机制）
4. 总控 Agent 启动轮询循环，子 Agent 启动等待循环

## 信号文件格式
信号文件放在 data/.signals/，使用标准化交接报文格式（参见 skills/shared/03_handoff-protocol.md）。
