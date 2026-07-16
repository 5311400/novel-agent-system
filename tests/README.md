# 测试策略

## 分层方案

```
tests/
├── skill-triggers/         # Python 自动化测试
│   ├── test_trigger_routing.py    # Agent 路由正确性
│   ├── test_ai_tone_window.py     # AI腔滑动窗口阈值
│   ├── test_state_machine.py      # 三重锁状态流转
│   └── fixtures/                  # 测试用例数据
├── consistency-checks/     # Python + Markdown 混合
│   ├── test_cross_ref.py          # 跨档案引用检测
│   ├── test_cross_ref_cases/      # 故意断裂/正常引用测试数据
│   └── manual_qa_checklist.md     # 人工验收清单
└── acceptance/             # Markdown 行为验收
    ├── q1-error-grading.md        # 错误分级验收
    ├── q3-style-guide.md          # 文风配比验收
    └── q5-state-machine.md        # 状态流转验收
```

## Python 自动化（CI 执行）
- 每次 git push 前自动运行
- 测试 Skill 路由、AI腔阈值、状态机切换、跨档案引用
- 使用 pytest 框架

## Markdown 验收（人工执行）
- 每 10 章一轮或版本升级后全量重跑
- 验收清单格式：Given → When → Then
- 抓 Python 测不到的"感觉问题"（文风是否真的爽、节奏是否舒适）

## 运行方式
```bash
# 运行全部自动化测试
cd tests
pytest -v

# 运行特定测试
pytest skill-triggers/test_ai_tone_window.py -v

# 人工验收
# 打开 tests/acceptance/ 下对应的 .md 文件逐条确认
```
