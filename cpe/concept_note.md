# Capability Procurement Engine - V0 Concept Note

## 1. 定位

**Capability Procurement Engine（CPE）** 是一个给 Agent 用的“外部能力采购决策层”。

它不负责替代支付协议，也不负责替代模型路由器；它负责在任务执行过程中回答下面几个核心问题：

1. 当前任务是否值得为额外信息或能力付费？
2. 如果值得，应该采购哪一种外部能力？
3. 应该自动采购，还是升级为人工审批？
4. 在预算、风险、时效和置信度约束下，最优采购顺序是什么？

一句话总结：

> CPE 让 Agent 不只是“会调用工具”，而是“会像一个有预算、有风控的分析员一样，决定什么时候该花钱买更强的信息和能力”。

---

## 2. 解决的问题

当前大多数 Agent 系统已经具备：

- 工具调用能力
- API 集成能力
- 工作流编排能力
- 多模型切换能力
- 甚至是 x402 / wallet / 自动支付能力

但仍缺少一层真正的“采购决策逻辑”：

- 什么时候应该继续用免费信息？
- 什么时候值得为更高质量的数据付费？
- 什么时候该升级到更强推理模型？
- 什么时候需要购买第二验证源降低误判？
- 在预算有限时，哪一笔采购最值得做？

没有这一层，Agent 只有两种状态：

1. **不会花钱**：能力上限受限，结论可能浅
2. **乱花钱**：调用越来越多，成本失控

CPE 的目标，就是在“不会花”和“乱花”之间，建立一套可解释、可约束、可迭代的采购大脑。

---

## 3. 与现有方向的边界

### 3.1 CPE 不是什么

CPE **不是**：

- x402 支付协议
- wallet / facilitator / settlement 层
- MCP 工具网关
- 单纯的 LLM router
- 单纯的预算拦截器
- 传统企业采购系统

### 3.2 CPE 与相邻系统的关系

#### x402 / agentic payment protocol
负责：**怎么付钱**

CPE 负责：**该不该付、买什么、为什么买**

#### CFO / budget guardrail layer
负责：**预算约束、异常检测、拦截超额支付**

CPE 负责：**在可支付集合中做采购决策排序**

#### Marketplace / service registry
负责：**有哪些服务可买**

CPE 负责：**哪些服务在当前任务下最值得买**

#### Model router
负责：**已有模型池中的路由**

CPE 负责：**是否要付费升级能力池本身**

所以，CPE 的定位更准确地说是：

> Agent 的外部能力采购决策层（Procurement Brain）

---

## 4. 核心使用场景

### 场景 A：事件验证

任务：某预测市场或交易系统发现异动，需要确认是否存在真实外部事件。

Agent 的决策链：

1. 先使用免费或低价来源初筛
2. 若证据不足，评估是否采购高质量新闻验证源
3. 若风险较高，再评估是否采购第二验证源
4. 若结论仍不稳定，再升级更强推理模型

核心点：采购是分阶段进行的，而不是一上来把所有贵工具全调一遍。

### 场景 B：高价值任务复核

任务：某交易/运营/研究决策潜在收益高，但当前置信度不足。

Agent 的决策链：

1. 估算当前任务价值
2. 判断采购高质量外部能力的成本是否合理
3. 若 ROI 足够高，则执行采购
4. 采购后提升置信度，再决定是否继续推进

### 场景 C：预算受限的智能工作流

任务：在固定预算内完成多步工作流。

Agent 的决策链：

1. 给每个子任务估值
2. 只在关键节点采购外部能力
3. 非关键节点坚持使用低成本路径
4. 在剩余预算基础上动态降级或升级

---

## 5. 核心架构

CPE V0 建议拆成 4 层：

### Layer 1: Capability Catalog
外部能力目录层

负责维护可采购对象的元数据：

- capability_id
- category
- provider
- unit_cost
- latency
- quality_score
- reliability_score
- supported_tasks
- approval requirement
- historical uplift（后续版本）

作用：

> 告诉 Agent 市场上“有什么可买”。

---

### Layer 2: Procurement Policy
采购策略层

负责定义风控和预算规则：

- 单任务预算上限
- 单次自动采购上限
- 最低 ROI 要求
- 高风险任务是否需要双验证
- 人工审批阈值
- 黑白名单供应商
- 时间窗口预算规则（后续版本）

作用：

> 告诉 Agent “在什么条件下允许买”。

---

### Layer 3: Decision Engine
决策引擎层

负责综合：

- 任务价值
- 当前置信度
- 风险等级
- 时效性
- 能力质量
- 成本
- 剩余预算

输出：

- buy / skip
- 采购对象排序
- 自动 / 人工审批模式
- 理由
- 预计 ROI

作用：

> 告诉 Agent “当前最值得买什么”。

---

### Layer 4: Execution + Ledger
执行与账本层

负责：

- 调起实际采购（支付/API调用）
- 记录每笔采购明细
- 记录采购后的效果
- 为后续统计学习提供反馈数据

作用：

> 把采购变成真实动作，并沉淀为经验。

---

## 6. V0 决策模型

V0 不追求复杂学习，优先使用：

- 规则
- 打分
- 可解释逻辑

### 6.1 输入

#### Task
- task_id
- task_type
- topic
- expected_value
- urgency
- risk_level
- budget_cap
- target_confidence

#### State
- confidence
- evidence_count
- spent
- remaining_budget
- need_external_support

#### Capability
- capability_id
- category
- provider
- unit_cost
- latency_sec
- quality_score
- reliability_score
- supported_tasks

#### Policy
- auto_buy_threshold
- max_budget_ratio
- min_expected_roi
- confidence_upgrade_trigger
- high_risk_requires_double_verify
- min_procurement_score

---

### 6.2 决策原则

先过硬约束：

1. 没预算不买
2. 当前置信度足够高不买
3. 超出预算比例不买
4. ROI 过低不买
5. 当前任务类型不适配不买

再做价值排序：

```text
procurement_score
= value_score × confidence_gap × urgency_weight × risk_weight × quality_weight
  ÷ (cost_weight + latency_penalty)
```

这是一个 V0 启发式分数，不代表最终形式，但适合快速落地。

---

### 6.3 决策输出

每次决策标准化输出：

```json
{
  "task_id": "pm_breakout_001",
  "decision": "buy",
  "capability_id": "premium_news_verify",
  "cost": 0.03,
  "score": 0.1851,
  "expected_roi": 216.67,
  "reason": "buy_auto",
  "approval_mode": "auto"
}
```

如果不采购：

```json
{
  "task_id": "pm_breakout_001",
  "decision": "skip",
  "reason": "confidence_enough"
}
```

---

## 7. 当前原型实现状态

已完成一个可运行的 Python V0：

- `procurement_engine.py`
- `procurement_capabilities.sample.json`
- `procurement_policy.sample.json`
- `procurement_task.sample.json`
- `procurement_state.sample.json`

当前能力：

- 加载任务、状态、能力目录、策略配置
- 对候选能力做逐项评估
- 给出可解释的 buy/skip 决策
- 返回排序后的候选列表
- 区分 auto / manual 采购

当前还未接入：

- 真实支付执行
- 真实 API 采购
- 历史效果反馈
- 学习型参数优化

---

## 8. 与现有开源生态的差异

通过 GitHub 初步观察，目前较接近的开源方向有：

### 8.1 x402-cfo
偏：预算控制 / 花费风控 / 审计

差异：
- 它偏“支付控制平面”
- CPE 偏“采购决策大脑”

### 8.2 autonomous-agent-payments
偏：Agent 支付与市场雇佣流程

差异：
- 它偏“怎么付、怎么雇”
- CPE 偏“该不该买、买哪个”

### 8.3 hardened x402 middleware
偏：支付安全与合规中间件

差异：
- 它偏“支付前拦截和审计”
- CPE 偏“支付前价值判断与采购排序”

### 8.4 MultiAgent Procurement AI
偏：企业供应链采购自动化

差异：
- 它偏“供应商/商品采购”
- CPE 偏“信息能力/API/模型采购”

总结：

> 开源生态已经开始覆盖“支付执行、预算风控、安全中间件、Agent 市场”这些层，但“Agent 外部能力采购决策层”仍然相对空白。

---

## 9. 为什么这个方向值得继续

### 原因 1：支付基础设施正在成熟
x402、wallet、agent marketplace 这类基础设施出现后，Agent 已经具备“能付钱”的能力。

下一步自然问题就是：

> 什么时候值得付？

### 原因 2：Agent 的成本约束会越来越重要
未来 Agent 不再只是“会不会做”，而是“值不值得花这笔钱去做”。

### 原因 3：高价值任务需要动态升级能力
很多任务不是固定工具链能解决的，必须按需采购：

- 更强模型
- 更可信数据
- 第二验证源
- 专项 API

CPE 正是这层动态能力升级的决策器。

---

## 10. 未来演进路线

### V0：规则 + 打分
- 快速落地
- 强可解释
- 便于观察数据

### V1：规则 + 经验统计
- 记录不同能力对不同任务的平均增益
- 将 quality_score 从静态值变为经验值

### V2：学习型 ROI 预测
- 预测“某能力在某类任务上的预期增益”
- 做更细粒度的成本收益优化

### V3：多阶段采购工作流
- 低价筛选
- 中价验证
- 高价复核
- 形成完整采购树

### V4：与支付执行层联动
- 接入 x402 / wallet / facilitator
- 采购决策变成真实交易

---

## 11. 最小产品定义（MVP）

一个最小可用 CPE 至少需要：

1. **能力目录**
2. **采购策略**
3. **任务状态输入**
4. **决策引擎**
5. **标准化输出**
6. **账本记录接口（哪怕先是本地 JSONL）**

MVP 不要求一开始就接支付，但必须先把“该不该买”的逻辑跑通。

---

## 12. 推荐命名

可选名称：

- Capability Procurement Engine
- Agent Procurement Engine
- External Capability Router
- Autonomous Capability Buyer
- Agent Spend & Procurement Brain

当前推荐主名：

## **Capability Procurement Engine (CPE)**

原因：
- 最准确
- 不会被误解成单纯支付工具
- 能覆盖模型、数据、API、验证源等多类能力

---

## 13. 下一步建议

短期建议：

1. 保持与具体业务系统解耦
2. 继续完善数据结构和账本接口
3. 增加“采购后置信度变化”的反馈记录
4. 抽象出标准事件日志
5. 为未来接 x402 / marketplace 留出执行接口

最值得先补的是：

### A. 账本 schema
记录：
- 采购前状态
- 采购动作
- 采购成本
- 采购后结果
- 采购是否真正带来提升

### B. 能力目录 schema
把：
- provider trust
- approval mode
- cost class
- response quality history
- task affinity

系统化下来。

### C. 反馈闭环
让系统不只是做决策，还能逐步学会：

- 哪些采购经常值得
- 哪些采购常常浪费
- 哪些任务最该用高质量能力

---

## 14. 一句话总结

> Capability Procurement Engine 是 Agent 时代“支付能力”之上的下一层：不是让 Agent 只是能花钱，而是让它知道什么时候该花、为什么花、花在哪最值。
