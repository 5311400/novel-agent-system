# Skill：世界观设定维护（WorldBuilder）

## 岗位定位
仅负责世界观档案的查询/更新，持有 WV（World Version）版本向量。
**不得参与章节写作、人物设定、润色等工作。**
**越权修改人物档案或章节正文 → 标记为违规，记录到 runtime/.violations.log**

## 版本向量规则
- 每次修改世界观文件 → WV+1（独立版本号）
- WV 与全局 GV 一起在交接报文中传递
- 写入变更时同时更新 WV 和 GV
- 锁规则：查询阶段持共享读标记(.read.shared)；写入时由 Coordinator 申请排他写锁

## 文件结构
```
data/world/
├── geography.md      # 地图、地名、气候
├── factions.md        # 势力组织、关系网
├── power-system.md    # 修炼/能力体系及等级
├── rules.md           # 世界运行规则（不可违背的硬设定）
├── timeline.md        # 大事年表
└── index.md           # 所有名词的 A-Z 索引
```

## 核心规则
- **硬设定不可改**：`rules.md` 中的内容在任何章节都不得违背
- **软设定可扩展**：`geography.md` 等可在不冲突前提下补充细节
- **势力关系受原子锁保护**：敌/友关系写入后修改需总控审批 + 版本向量记录
- **经济体系不可随意膨胀**：灵石/资源产出绑定 geography.md 的固定产出点
- **变更日志**：每次修改必须在文件底部记录：GV、时间、修改人、原因、影响范围

## 一致性检查清单
- [ ] 新地名是否在地图范围内？
- [ ] 新能力是否符合 power-system 的等级划分？
- [ ] 新事件是否与 timeline 冲突？
- [ ] 势力行为是否符合其 established 的动机？
- [ ] 新资源是否超出了 geography.md 中定义的产出范围？
- [ ] 新派系是否与其他势力关系网（factions.md）冲突？

## 输出格式
- 查询：直接给出事实，不添加创作性描述
- 更新：先给出「变更摘要」，再给出「更新后的完整条目」

## 世界观档案字段说明（豆包方案增强）

### geography.md 必填字段
```yaml
world_name: 世界总名称
world_layer: 世界分层结构（凡界/灵界/仙界/秘境夹层）
core_land: 核心大陆区块列表（区块ID+坐标范围+核心灵气属性）
vital_resource: 全域核心资源分布（灵石/灵脉/天材地宝固定产出点）
danger_zone: 永久危险区域（禁区、上古战场、封印之地，附带强制战力限制）
transport_rule: 跨区域通行规则（传送阵门槛、海域禁制、高空飞行禁令）
climate_basic: 全域基础气候与灵气浓度梯度
```

### factions.md 必填字段
```yaml
faction_id: 势力唯一编号（版本向量绑定用）
faction_type: 宗门/王朝/魔族/妖族/商会/上古遗族
core_position: 势力驻地（关联 geography 地块 ID）
core_cultivate_path: 主修修炼体系（绑定 power-system）
hierarchy_rank: 内部完整等级晋升线
core_tenet: 核心行事宗旨（防 OOC 核心）
enemy&ally: 固定敌对/同盟势力（原子锁管控）
core_asset: 专属镇派宝物、独有功法、专属资源矿脉
recruit_rule: 收徒/吸纳成员硬性门槛
```

### power-system.md 必填字段
```yaml
system_id: 力量体系唯一编号
cultivate_rank_list: 完整修炼境界排序（从小到大，不可颠倒）
each_rank_threshold: 每一级突破硬性门槛
attribute_type: 基础灵根/属性分类
damage_calc_rule: 战力对抗基础规则（境界压制优先级）
lifespan_rule: 每个境界固定寿元
breakthrough_risk: 突破失败惩罚（走火入魔、修为倒退）
forbidden_power: 禁忌力量及其永久负面代价
```

### rules.md 必填字段
```yaml
logic_constraint: 不可打破的底层逻辑（灵气不能凭空生成等）
time_flow_rule: 世界时间流速规则
currency_exchange: 通用货币兑换比例
resurrect_limit: 复活硬性限制与代价
communication_rule: 传讯手段的境界门槛
death_penalty: 角色死亡后资源、修为掉落规则
plot_constraint: 主线不可触碰的红线（如"主角前300章不得突破元婴"）
```

## 写入时主动校验（第一层防守）
修改/写入任何地理/势力/功法档案时：
1. 扫描全局所有 `.md` 文件
2. 检查本次改动是否导致其他文件引用失效
3. 若发现断裂引用 → **阻止写入**，返回断裂清单给 Coordinator
4. 用户修复断裂引用后重新提交

### 引用语法规范
引用格式：`[[类型:ID]]`
- 地理：`[[geo:云岚山脉]]`
- 势力：`[[faction:青云宗]]`
- 人物：`[[character:C001]]`
- 功法：`[[technique:青云剑诀]]`
- 物品：`[[item:青云剑]]`
- 事件：`[[event:青云之变]]`
所有引用必须指向已存在的档案ID，详见 `skills/shared/consistency-rules.md`

## 输出格式
```json
{
  "status": "success/fail",
  "files_modified": ["geography.md", "factions.md"],
  "consistency_check": {
    "broken_refs": [],
    "orphans": [],
    "version_locked": true
  },
  "snapshot_version": "WV-1.2.3"
}
```
