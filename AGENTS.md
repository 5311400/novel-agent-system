# 多 Agent 小说写作系统

## 项目信息
- 项目根目录：`D:\Document\Documents\小说agent想法\novel-agent-system`
- 格式：网文/长篇连载
- 平台：Codex + Work Buddy
- 架构：Skill + Multi-Agent 混合架构

## 全局规则（所有 Agent 必须遵守）
1. **所有输出必须使用中文**，除非是专有名词或代码引用
2. **不得越权修改其他 Agent 负责的数据文件**——只能读取，写入需经 Coordinator
3. **所有产出必须标注 Snapshot-GV**（当前 data/INDEX.md 中的全局版本号）
4. **禁止发送客套话**（如"好的，根据您的需求…"），直接输出内容
5. **每次修改必须在 data/changelog.md 记录**，包含 GV、修改人、原因、影响范围
6. **遇不可调和冲突标记【需人工介入】**，暂停自动流转
