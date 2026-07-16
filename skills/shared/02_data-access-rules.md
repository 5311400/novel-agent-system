# Skill：项目全局档案读取规则

## 目录映射
| 路径 | 内容 | 读写权限 |
|------|------|---------|
| data/world/ | 世界观设定 | Coordinator 写，只读 Agent 读 |
| data/characters/ | 人物档案 | Coordinator 写，只读 Agent 读 |
| data/chapters/ | 已发布章节终稿 | Coordinator 写，只读 Agent 读 |
| data/timeline.md | 时间线 | Coordinator 写，只读 Agent 读 |
| data/plot-log.md | 每章剧情摘要 | Coordinator 写，只读 Agent 读 |
| data/INDEX.md | 全局版本号 GV | Coordinator 维护 |
| artifacts/ | 中间产物 | 对应 Agent 读写 |
| runtime/ | 运行时临时文件 | 对应 Agent 读写 |

## 读写规则
1. 所有 Agent 启动任务时**必须**先读取 `data/INDEX.md` 获取当前 GV
2. 读取的档案快照 GV 必须在产出中标注
3. 写入仅由 Coordinator 在执行排他锁时进行
4. 变更日志必须记录到 `data/changelog.md`，绑定 GV + batch_id + hash
5. 读取侧防过期——子Agent快照绑定GV，过期产出直接驳回重跑
6. 写入事务原子化——先缓存至 runtime/.tmp/，全量校验后再一次性落地

## 原子锁协议

### 排他写锁（data/.write.lock）
- OS 原生独占创建文件操作，消除竞态条件
- 锁文件内容：owner_id / task_batch_id / acquire_ts / expire_ts / global_version
- 释放：写入事务全部完成后删除 .write.lock
- 超时回收：超过 expire_ts（默认 120s）视为僵尸锁，自动清理
- 续约：写入流程内部每 30s 刷新 expire_ts

### 共享读标记（data/.read.shared）
- 子 Agent 只读时创建/计数共享读标记，无需等待排他写锁
- Coordinator 申请排他锁时先等待所有共享读标记销毁
- 写入完成释放排他锁后，恢复只读并行

### 写入事务原子化
```
1. 等待所有共享读标记销毁
2. 获取排他写锁（原子独占创建 .write.lock）
3. 所有修改先写入 runtime/.tmp/（不覆盖原文件）
4. 全量校验一致性
5. 校验通过 → 一次性落地到 data/
6. 追加 changelog（绑定 GV + batch_id + hash）
7. 递增 INDEX.md GV
8. 释放写锁
```

### 违规处理
所有锁操作异常记录到 runtime/.violations.log
