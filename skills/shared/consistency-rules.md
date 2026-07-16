# Skill：全局一致性校验规则（Consistency Rules）
> 全局共享 Skill，所有 Agent 在读取/写入档案时强制加载。
> 定义跨档案引用的语法规范、校验规则和孤儿检测逻辑。

## 适用范围
所有 Agent（WorldBuilder / CharacterKeeper / ChapterWriter / PolishEditor）在操作 data/ 目录下的 `.md` 档案时，必须遵守本规则。

## 引用语法
引用格式：`[[类型:ID]]`

### 支持的类型
| 类型 | 前缀 | 示例 | 指向文件 |
|------|------|------|---------|
| 地理 | `geo` | `[[geo:云岚山脉]]` | data/world/geography.md |
| 势力 | `faction` | `[[faction:青云宗]]` | data/world/factions.md |
| 人物 | `character` | `[[character:C001]]` | data/characters/ |
| 功法 | `technique` | `[[technique:青云剑诀]]` | data/world/power-system.md |
| 物品 | `item` | `[[item:青云剑]]` | data/world/geography.md 或 characters/ |
| 事件 | `event` | `[[event:青云之变]]` | data/timeline.md |

## 校验规则

### 1. 外键必须存在
- 引用的档案ID必须在对应文件中存在
- 不存在 → 抛出严重级错误，阻断写入

### 2. 禁止循环引用
- A引用B，则B不得直接或间接引用A
- 检测到循环引用 → 抛出严重级错误，返回循环链路

### 3. 孤儿检测
- 每10章扫描一次，标记未被任何档案引用的条目为 `orphan`
- orphan 条目不删除，仅标记备查

### 4. 版本锁定
- 引用时自动记录被引用档案的版本号
- 被引用档案版本变更 → 触发关联校验
- 版本不匹配 → 标记为过期引用，要求刷新

### 5. 引用断裂恢复
- 发现断裂引用时，自动定位断裂源（哪个文件/哪个字段引用了不存在的ID）
- 返回断裂清单给 Coordinator，由人工决定修复方案

## 加载方式
所有 Agent Skill 文件头部统一加载：
```markdown
> 本 Agent 遵守全局一致性校验规则：@import skills/shared/consistency-rules.md
```
具体实现中，由 Agent 加载时自动读取本文件并注入上下文。

## 与 WorldBuilder 的协作
- **WorldBuilder 写入时**：主动调用本规则做写入前校验（第一层防守）
- **其他 Agent 读取时**：被动调用本规则做读取后校验（第二层防守）
- 详见 WorldBuilder Skill 中的「写入时主动校验」章节
