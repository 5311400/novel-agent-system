# 关系网（relationships.md）
> 角色间关系图谱，支持版本向量追踪。

## 关系格式
```yaml
relation_id:
role_a:
role_b:
relation_type: 爱慕/师徒/仇敌/盟友/家族
strength: 亲密/中立/敌对
origin_chapter: 首次建立关系的章节
change_log: 关系变更历史（绑定 CV 版本号）
```
