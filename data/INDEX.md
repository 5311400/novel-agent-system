# INDEX.md —— 全局版本号管理

## 当前全局版本
- GV: 1
- WV: 0
- CV: 0
- CH-V: 0

## 更新说明
每次批量写入成功，GV+1。
三类独立资源版本（WV/CV/CH-V）分别在对应档案写入时递增。

## 版本说明
- WV (世界观版本)：data/world/ 下的文件写入时递增
- CV (人物档案版本)：data/characters/ 下的文件写入时递增
- CH-V (章节分卷版本)：data/chapters/ 下的文件写入时递增
