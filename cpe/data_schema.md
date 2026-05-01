# Capability Procurement Engine - Data Schema Draft

## 1. 目标

这份文档定义 **Capability Procurement Engine (CPE)** 的基础数据结构草案，目标是把前一版概念说明进一步落成“可实现规范”。

设计原则：

1. **先够用**：优先支持 V0 / V1 落地
2. **强可解释**：每次采购决策都能回溯原因
3. **易扩展**：未来可以接真实支付、学习模型、市场注册表
4. **和具体业务解耦**：先做通用 schema，再接具体系统

---

## 2. 核心对象总览

CPE 建议先定义 6 类对象：

1. `Task`：任务对象
2. `State`：当前决策状态对象
3. `Capability`：可采购能力对象
4. `Policy`：采购策略对象
5. `DecisionRecord`：一次采购决策记录
6. `OutcomeRecord`：采购后效果反馈记录

这 6 类对象已经够支撑一个最小采购闭环。

---

## 3. Task Schema

`Task` 用来描述“当前要解决的任务是什么，它值多少钱，风险多大”。

### 3.1 字段定义

```json
{
  "task_id": "pm_breakout_001",
  "task_type": "market_verification",
  "topic": "Polymarket 异动验证",
  "description": "检测到某类市场联动异动，需要验证是否存在真实事件驱动",
  "expected_value": 6.5,
  "urgency": 0.9,
  "risk_level": "medium",
  "budget_cap": 0.1,
  "target_confidence": 0.6,
  "created_at": "2026-05-01T15:00:00+08:00",
  "context": {
    "market_slug": "example-market",
    "signal_strength": 0.58,
    "source": "scanner_v2"
  }
}
```

### 3.2 字段说明

| 字段 | 类型 | 说明 |
|---|---|---|
| `task_id` | string | 任务唯一 ID |
| `task_type` | string | 任务类型，如 `market_verification` / `report_synthesis` |
| `topic` | string | 任务标题 |
| `description` | string | 更详细的任务说明 |
| `expected_value` | number | 任务预估价值，可用统一内部价值单位 |
| `urgency` | number | 0~1，越高越紧急 |
| `risk_level` | enum | `low` / `medium` / `high` |
| `budget_cap` | number | 本任务最大可花预算 |
| `target_confidence` | number | 希望达到的最小置信度 |
| `created_at` | string | ISO 时间 |
| `context` | object | 业务上下文，留给上层系统补充 |

### 3.3 设计备注

- `expected_value` 不一定是美元，可以是统一内部评分，但需要跨任务可比较
- `context` 必须保持松耦合，避免 schema 被某个具体系统绑死

---

## 4. State Schema

`State` 表示 Agent 在某个任务中的当前状态。

### 4.1 字段定义

```json
{
  "task_id": "pm_breakout_001",
  "confidence": 0.42,
  "evidence_count": 1,
  "spent": 0.0,
  "remaining_budget": 0.1,
  "need_external_support": true,
  "current_stage": "initial_screening",
  "selected_capabilities": [],
  "blocked_reasons": []
}
```

### 4.2 字段说明

| 字段 | 类型 | 说明 |
|---|---|---|
| `task_id` | string | 对应任务 ID |
| `confidence` | number | 当前置信度 0~1 |
| `evidence_count` | int | 当前已有证据数 |
| `spent` | number | 当前已花费预算 |
| `remaining_budget` | number | 剩余预算 |
| `need_external_support` | bool | 是否还需要外部能力 |
| `current_stage` | string | 当前任务阶段 |
| `selected_capabilities` | array | 已采购或已使用能力列表 |
| `blocked_reasons` | array | 被策略阻断的原因 |

### 4.3 推荐阶段值

建议先统一几个阶段：

- `initial_screening`
- `verification`
- `deep_reasoning`
- `final_review`
- `done`

---

## 5. Capability Schema

`Capability` 描述一个可采购的外部能力，可以是模型、API、数据源、第二验证源等。

### 5.1 字段定义

```json
{
  "capability_id": "premium_news_verify",
  "name": "Premium News Verification",
  "category": "verification",
  "provider": "provider_b",
  "provider_type": "api",
  "unit_cost": 0.03,
  "currency": "USD",
  "latency_sec": 4,
  "quality_score": 0.82,
  "reliability_score": 0.88,
  "trust_score": 0.9,
  "supported_tasks": ["market_verification", "event_research"],
  "approval_mode": "auto",
  "cost_class": "low",
  "tags": ["news", "verification", "high_precision"],
  "metadata": {
    "endpoint": "https://example.com/api/verify",
    "network": "base",
    "payment_method": "x402"
  }
}
```

### 5.2 字段说明

| 字段 | 类型 | 说明 |
|---|---|---|
| `capability_id` | string | 能力唯一 ID |
| `name` | string | 展示名称 |
| `category` | string | 能力分类 |
| `provider` | string | 提供商名称 |
| `provider_type` | string | `api` / `model` / `dataset` / `agent_service` |
| `unit_cost` | number | 单次使用成本 |
| `currency` | string | 币种 |
| `latency_sec` | number | 平均延迟 |
| `quality_score` | number | 静态质量评分 |
| `reliability_score` | number | 稳定性评分 |
| `trust_score` | number | 信任评分 |
| `supported_tasks` | array | 支持的任务类型 |
| `approval_mode` | enum | `auto` / `manual` / `blocked` |
| `cost_class` | enum | `low` / `medium` / `high` |
| `tags` | array | 检索标签 |
| `metadata` | object | 供应商额外信息 |

### 5.3 设计备注

后续 V1/V2 可以增加：

- `historical_uplift_confidence`
- `historical_success_rate`
- `historical_roi`
- `availability_score`
- `compliance_flags`

也就是把能力对象从“静态卡片”变成“带历史表现的供应商画像”。

---

## 6. Policy Schema

`Policy` 用来定义采购规则与风控边界。

### 6.1 字段定义

```json
{
  "policy_id": "default_v0",
  "auto_buy_threshold": 0.05,
  "max_budget_ratio": 0.15,
  "min_expected_roi": 2.0,
  "confidence_upgrade_trigger": 0.6,
  "high_risk_requires_double_verify": true,
  "min_procurement_score": 0.15,
  "blocked_providers": [],
  "allowed_currencies": ["USD", "USDC"],
  "allowed_networks": ["base"],
  "manual_review_threshold": 0.05,
  "notes": "default starting policy"
}
```

### 6.2 字段说明

| 字段 | 类型 | 说明 |
|---|---|---|
| `policy_id` | string | 策略 ID |
| `auto_buy_threshold` | number | 单次低于该金额可自动采购 |
| `max_budget_ratio` | number | 单次采购成本占任务价值的最大比例 |
| `min_expected_roi` | number | 最低 ROI 要求 |
| `confidence_upgrade_trigger` | number | 低于此置信度可触发升级 |
| `high_risk_requires_double_verify` | bool | 高风险任务是否强制双验证 |
| `min_procurement_score` | number | 最低采购分数 |
| `blocked_providers` | array | 禁用供应商 |
| `allowed_currencies` | array | 允许币种 |
| `allowed_networks` | array | 允许网络 |
| `manual_review_threshold` | number | 超过该金额需要人工审批 |
| `notes` | string | 备注 |

### 6.3 设计备注

后续可增加多层策略继承：

- 全局策略
- 任务类型策略
- Agent 级策略
- 用户级策略

---

## 7. DecisionRecord Schema

`DecisionRecord` 是采购引擎每次输出的核心日志。

### 7.1 字段定义

```json
{
  "decision_id": "dec_20260501_001",
  "task_id": "pm_breakout_001",
  "capability_id": "premium_news_verify",
  "provider": "provider_b",
  "decision": "buy",
  "approval_mode": "auto",
  "score": 0.1851,
  "expected_roi": 216.67,
  "unit_cost": 0.03,
  "reason": "buy_auto",
  "inputs": {
    "value_score": 0.65,
    "confidence_gap": 0.18,
    "urgency_weight": 0.95,
    "risk_weight": 1.0,
    "quality_weight": 0.7216,
    "cost_weight": 0.3,
    "latency_penalty": 0.1333
  },
  "created_at": "2026-05-01T15:10:00+08:00"
}
```

### 7.2 字段说明

| 字段 | 类型 | 说明 |
|---|---|---|
| `decision_id` | string | 决策记录 ID |
| `task_id` | string | 关联任务 |
| `capability_id` | string | 关联能力 |
| `provider` | string | 提供商 |
| `decision` | enum | `buy` / `skip` / `review` |
| `approval_mode` | enum | `auto` / `manual` |
| `score` | number | 采购打分 |
| `expected_roi` | number | 预估 ROI |
| `unit_cost` | number | 成本 |
| `reason` | string | 原因 |
| `inputs` | object | 用于可解释分析的中间量 |
| `created_at` | string | ISO 时间 |

### 7.3 推荐 reason 值

- `buy_auto`
- `buy_manual`
- `buy_auto_double_verify`
- `confidence_enough`
- `no_budget`
- `over_remaining_budget`
- `roi_too_low`
- `unsupported_task_type`
- `score_too_low`
- `provider_blocked`

---

## 8. OutcomeRecord Schema

`OutcomeRecord` 用来记录采购之后，这笔采购到底有没有带来价值。

这是未来学习闭环最关键的对象。

### 8.1 字段定义

```json
{
  "outcome_id": "out_20260501_001",
  "decision_id": "dec_20260501_001",
  "task_id": "pm_breakout_001",
  "capability_id": "premium_news_verify",
  "executed": true,
  "actual_cost": 0.03,
  "latency_sec": 3.8,
  "confidence_before": 0.42,
  "confidence_after": 0.64,
  "confidence_delta": 0.22,
  "evidence_count_before": 1,
  "evidence_count_after": 3,
  "task_result": "improved",
  "notes": "confirmed event from premium source",
  "created_at": "2026-05-01T15:12:00+08:00"
}
```

### 8.2 字段说明

| 字段 | 类型 | 说明 |
|---|---|---|
| `outcome_id` | string | 结果记录 ID |
| `decision_id` | string | 关联决策记录 |
| `task_id` | string | 关联任务 |
| `capability_id` | string | 关联能力 |
| `executed` | bool | 是否真的执行了采购 |
| `actual_cost` | number | 实际成本 |
| `latency_sec` | number | 实际延迟 |
| `confidence_before` | number | 采购前置信度 |
| `confidence_after` | number | 采购后置信度 |
| `confidence_delta` | number | 置信度提升 |
| `evidence_count_before` | int | 前证据数 |
| `evidence_count_after` | int | 后证据数 |
| `task_result` | string | `improved` / `neutral` / `worse` |
| `notes` | string | 补充说明 |
| `created_at` | string | ISO 时间 |

### 8.3 为什么这个对象很重要

没有 `OutcomeRecord`，系统永远只能靠拍脑袋调参数。

有了它，后面就能统计：

- 哪些能力最常提升置信度
- 哪类任务上哪种能力最值钱
- 哪些采购经常花钱但没帮助
- 哪些高价能力真的值得保留

---

## 9. Ledger Event Schema（推荐）

如果要做统一账本，建议把 `DecisionRecord` 和 `OutcomeRecord` 包装成标准事件。

### 9.1 示例

```json
{
  "event_id": "evt_20260501_001",
  "event_type": "procurement_decision",
  "task_id": "pm_breakout_001",
  "entity_id": "dec_20260501_001",
  "payload": {
    "decision": "buy",
    "capability_id": "premium_news_verify",
    "score": 0.1851
  },
  "created_at": "2026-05-01T15:10:00+08:00"
}
```

### 9.2 推荐事件类型

- `task_created`
- `procurement_decision`
- `procurement_executed`
- `procurement_blocked`
- `procurement_outcome`
- `task_completed`

这样以后日志、回放、审计都更统一。

---

## 10. 文件组织建议

V0 建议先用最简单的文件布局：

```text
cpe/
  capabilities.json
  policy.json
  tasks/
    pm_breakout_001.task.json
  states/
    pm_breakout_001.state.json
  ledger/
    decision_records.jsonl
    outcome_records.jsonl
```

如果后续走数据库，可映射到：

- `tasks`
- `states`
- `capabilities`
- `policies`
- `decisions`
- `outcomes`
- `events`

---

## 11. V1 / V2 可扩展字段

后续建议扩展这些字段：

### Capability 扩展
- `historical_success_rate`
- `historical_confidence_delta_avg`
- `historical_roi_avg`
- `availability_score`
- `compliance_flags`

### Policy 扩展
- `hourly_budget_cap`
- `daily_budget_cap`
- `provider_allowlist`
- `task_type_overrides`
- `agent_role_overrides`

### Outcome 扩展
- `final_task_success`
- `realized_value`
- `user_feedback`
- `error_type`
- `retried`

---

## 12. 最小落地建议

如果现在就要把 schema 落成工程，最优先的顺序是：

1. `Task`
2. `State`
3. `Capability`
4. `Policy`
5. `DecisionRecord`
6. `OutcomeRecord`

原因很简单：

- 前四个支撑决策
- 后两个支撑复盘和学习

这 6 个对象先跑通，整个 CPE 就已经不是纸面构想，而是一个可以开始积累数据的系统了。

---

## 13. 一句话总结

> CPE 的数据模型核心不是“记录花了多少钱”，而是“记录在什么任务、什么状态下，为什么买了这个能力，以及买完后到底有没有变得更好”。
