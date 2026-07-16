# Artifacts — 中间产物目录

Artifact 层管理写作流程中的中间产物，类比代码开发中的「提交→Review→Merge」管道。

## 文件生命周期
```
draft_chapter_N.md   ← ChapterWriter 产出
        ↓
review_chapter_N.md  ← PolishEditor 质检报告
        ↓
final_chapter_N.md   ← Coordinator 仲裁通过后的终稿
        ↓
移动至 data/chapters/   ← 归档为已发布章节
```

## 文件命名规则
- 草稿：`draft_chapter_{N}.md`
- 质检报告：`review_chapter_{N}.md`
- 终稿：`final_chapter_{N}.md`
- 章节概要：`brief_chapter_{N}.md`

## 注意事项
- Artifacts 是中间状态，不进入长期记忆
- 终稿经仲裁通过后，由 Coordinator 移至 data/chapters/
- Artifacts 可随时清理，不影响世界观/人物档案
