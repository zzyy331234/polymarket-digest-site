# Capability Procurement Engine - Execution Flow Draft

## 1. 目标

这份文档描述 **Capability Procurement Engine (CPE)** 在真实系统中从“任务进入”到“采购完成并反馈”的执行流程草案。

它主要回答：

1. 一个任务进入后，CPE 应该怎么接管？
2. 采购决策应该发生在哪些阶段？
3. 什么情况下自动采购，什么情况下人工审批？
4. 采购失败后怎么降级？
5. 采购结果如何回写到账本和反馈系统？

这份文档偏流程，不替代数据 schema，也不替代具体代码实现。

---

## 2. 顶层流程图

先给出一条最简执行链：

```text
Task Created
   ↓
Initial Assessment
   ↓
Need External Capability?
   ├─ No  → Continue Local Workflow
   └─ Yes → Candidate Discovery
                 ↓
           Policy Pre-Check
                 ↓
           Capability Scoring
                 ↓
           Select Best Candidate
                 ↓
      Auto Buy or Manual Review?
          ├─ Auto   → Execute Procurement
          └─ Manual → Approval Queue
                           ↓
                     Approved / Rejected
                           ↓
                  Execute or Fallback
                           ↓
                   Outcome Evaluation
                           ↓
                     Ledger + Feedback
                           ↓
                    Continue Task Flow
```

一句话：

> CPE 不是一次性的判断器，而是插在任务流程中的“阶段性采购决策器”。

---

## 3. 流程分层

建议把执行流程拆成 6 个阶段：

1. Task Intake
2. Initial Assessment
3. Candidate Discovery
4. Procurement Decision
5. Execution & Approval
6. Outcome & Feedback

---

## 4. Stage 1: Task Intake

### 4.1 输入

任务从上游系统进入，例如：

- 一个研究任务
- 一次交易前验证任务
- 一次报告生成任务
- 一次多 Agent 工作流的子任务

### 4.2 动作

系统在这里做 3 件事：

1. 生成 `Task`
2. 初始化 `State`
3. 绑定默认 `Policy`

### 4.3 输出

```text
Task + State + Policy Context
```

### 4.4 关键点

这一步不做采购，只做初始化。

目的是让任何任务进入 CPE 时，都带着：

- 任务价值
- 风险等级
- 时效性
- 初始预算
- 当前阶段

如果上游没给完整数据，也要在这里补默认值。

---

## 5. Stage 2: Initial Assessment

### 5.1 目的

先判断：

> 这个任务在当前阶段，是否真的需要外部能力？

### 5.2 判断信号

常见触发条件：

- 当前置信度低于阈值
- 证据数不足
- 上游工作流显式标记“需要验证”
- 当前任务风险较高
- 当前任务价值较高且信息不足

### 5.3 输出

两种结果：

#### A. 不需要外部能力
```text
need_external_support = false
→ 继续本地流程
```

#### B. 需要外部能力
```text
need_external_support = true
→ 进入 Candidate Discovery
```

### 5.4 关键点

这里不要直接“发现低置信度就买”。

它只是触发采购评估入口，不是直接采购。

---

## 6. Stage 3: Candidate Discovery

### 6.1 目的

在能力目录中找到当前任务“可能能买”的候选项。

### 6.2 输入

- `task_type`
- 当前 `stage`
- 风险等级
- 预算范围
- 上游指定约束（如果有）

### 6.3 动作

从 `Capability Catalog` 里筛选：

1. 支持当前任务类型的能力
2. 没被策略封禁的能力
3. 价格不明显超预算的能力
4. 当前阶段允许使用的能力

### 6.4 输出

```text
Candidate Capability List
```

### 6.5 推荐筛选逻辑

先粗筛，再精排：

#### 粗筛
- task compatibility
- provider allow/block rules
- currency/network compatibility
- cost sanity check

#### 精排留给下一阶段
- ROI
- confidence uplift expectation
- latency tradeoff
- quality tradeoff

### 6.6 关键点

Candidate Discovery 不是打分器，它更像检索器。

它要尽量保证：
- 召回够全
- 过滤掉明显不合法的项

---

## 7. Stage 4: Procurement Decision

这是核心阶段。

### 7.1 目的

在候选能力集合中决定：

1. 买不买
2. 买哪个
3. 自动还是人工审批
4. 如果不买，为什么不买

### 7.2 执行顺序

建议采用：

```text
Hard Constraints → Score Candidates → Rank → Select
```

### 7.3 Hard Constraints

在打分前先过硬约束：

- `remaining_budget > 0`
- `spent < budget_cap`
- `confidence < target_confidence`
- `unit_cost <= remaining_budget`
- `expected_roi >= min_expected_roi`
- provider 不在 blocklist
- currency/network 合规

如果硬约束不满足，直接 skip。

### 7.4 Candidate Scoring

对每个候选项计算采购分：

```text
score = value_score × confidence_gap × urgency_weight × risk_weight × quality_weight
        ÷ (cost_weight + latency_penalty)
```

未来可以升级成：

- 加历史 uplift
- 加 provider trust
- 加 stage fit
- 加 opportunity cost

### 7.5 Rank & Select

输出结果建议包括：

- `selected`
- `buy_candidates`
- `all_decisions`

也就是：

- 最终选谁
- 还有哪些可买
- 所有被拒绝对象为什么被拒绝

### 7.6 不采购也是决策

一个成熟系统必须把以下情况视为正确输出：

- `confidence_enough`
- `roi_too_low`
- `over_remaining_budget`
- `unsupported_task_type`
- `score_too_low`

不买，不等于系统没工作。

---

## 8. Stage 5: Execution & Approval

### 8.1 目的

把“采购决策”转成真实动作。

### 8.2 auto / manual 分流

#### Auto Buy
满足以下条件可自动采购：

- 成本低于 `auto_buy_threshold`
- 风险不过高
- provider 合规
- 不需要额外审批

#### Manual Review
进入人工审批的典型情况：

- 单次成本超过阈值
- 高风险任务要双验证
- provider 新且未验证
- 采购动作将触发真实链上支付
- 用户要求保守模式

### 8.3 审批队列

建议抽象一个通用审批队列对象，而不是把“人工审批”写死成某个平台消息。

审批队列字段至少应包含：

- task_id
- capability_id
- expected_cost
- expected_benefit
- reason
- deadline
- status

### 8.4 执行动作

执行器层要做的是：

1. 发起采购请求
2. 如果是 x402/付费 API，处理支付与请求
3. 获取结果或失败原因
4. 更新 `State`
5. 写入 `DecisionRecord`
6. 写入 `OutcomeRecord`

### 8.5 关键点

决策引擎和执行引擎一定要分开。

因为：

- 决策可以模拟
- 执行可能失败
- 执行需要处理支付、超时、重试、回滚

---

## 9. Stage 6: Outcome & Feedback

### 9.1 目的

判断：

> 这笔采购到底有没有带来正向效果？

### 9.2 回写内容

采购执行后，至少回写：

- 实际成本
- 实际延迟
- 置信度变化
- 证据数变化
- 是否提升了任务质量
- 是否触发了后续阶段

### 9.3 输出对象

- `OutcomeRecord`
- `Ledger Event`
- 更新后的 `State`

### 9.4 为什么重要

如果没有 Outcome 层：

- 系统永远只知道“买了什么”
- 不知道“买得值不值”

有了 Outcome 层之后，后面才能：

- 调整 `quality_score`
- 调整 `trust_score`
- 更新 `historical_roi`
- 做学习型决策模型

---

## 10. 分阶段采购机制

CPE 不建议默认“一步到顶”。

更好的方式是：

## 10.1 三阶段采购树

### Phase A：低成本初筛
目标：快速判断是否值得深入

常见能力：
- 低价搜索
- 低价分类
- 廉价模型摘要

### Phase B：中成本验证
目标：降低误判，确认事实

常见能力：
- 优质新闻验证源
- 第二信源交叉验证
- 更可靠的数据 API

### Phase C：高成本复核
目标：只在高价值/高风险时触发

常见能力：
- 强推理模型
- 专项专家 Agent
- 高精度数据服务

### 10.2 为什么分阶段重要

这样做的好处：

- 避免一上来就重投入
- 更符合真实预算管理逻辑
- 便于把采购变成层级递进

---

## 11. 失败、回退与降级

这是实战里很重要的一层。

### 11.1 常见失败类型

- 支付失败
- provider 超时
- provider 返回空结果
- provider 返回低质量结果
- 超预算
- 审批被拒

### 11.2 回退策略

建议支持 4 种回退动作：

#### A. Retry Same Capability
适合：网络抖动、短时超时

#### B. Fallback to Cheaper Capability
适合：预算收紧、审批被拒

#### C. Escalate to Manual Review
适合：自动路径不可靠、任务价值高

#### D. Abort External Procurement
适合：高成本低收益、无合适候选项

### 11.3 降级原则

优先顺序建议：

```text
同能力重试 → 更便宜替代 → 人工审批 → 放弃采购
```

### 11.4 状态更新

一旦失败，`State` 里建议记录：

- `blocked_reasons`
- `last_failure_type`
- `fallback_attempts`

---

## 12. 与未来 x402 / marketplace 的接口预留

当前虽然不接具体支付，但执行流里要提前留接口。

### 12.1 建议抽象接口

#### `CapabilityResolver`
负责：
- 根据 capability_id 找到 endpoint / provider config

#### `ProcurementExecutor`
负责：
- 发请求
- 处理 x402 / API key / marketplace purchase
- 返回响应和成本

#### `LedgerWriter`
负责：
- 决策日志
- 执行日志
- outcome 日志

#### `FeedbackUpdater`
负责：
- 更新能力表现统计
- 更新任务状态

### 12.2 为什么现在就要留

因为如果前期不抽象，后面一接真实支付就会把整个决策层污染掉。

---

## 13. 推荐的最小执行状态机

V0 建议先做一个很小的状态机：

```text
created
  → assessing
  → discovering
  → deciding
  → awaiting_approval | executing
  → evaluating_outcome
  → completed | fallback | aborted
```

### 13.1 状态说明

- `created`：任务已创建
- `assessing`：正在判断是否需要外部能力
- `discovering`：正在找候选能力
- `deciding`：正在做采购排序
- `awaiting_approval`：待人工审批
- `executing`：正在执行采购
- `evaluating_outcome`：正在评估结果
- `completed`：成功完成
- `fallback`：走回退逻辑
- `aborted`：终止采购

这个状态机够简单，但已经能支撑真实系统演化。

---

## 14. 一条完整示例流程

下面给一个完整例子。

### 场景
某任务需要验证预测市场异动是否由真实新闻驱动。

### 流程

1. 上游 scanner 创建 `Task`
2. 初始化 `State`
3. CPE 检查当前 `confidence=0.42 < 0.60`
4. 进入 Candidate Discovery
5. 找到三个候选能力：
   - cheap_news_search
   - premium_news_verify
   - deep_reasoning_model
6. Policy Pre-Check 通过前两个，第三个标记 manual
7. Decision Engine 打分并排序
8. 系统选中 `cheap_news_search`
9. 因成本低于 auto 阈值，自动执行
10. 执行后返回结果，置信度上升到 `0.56`
11. 仍低于目标置信度，触发下一阶段采购评估
12. 第二轮选中 `premium_news_verify`
13. 执行后置信度上升到 `0.67`
14. 达到目标，停止采购
15. 记录两条 `DecisionRecord` 与两条 `OutcomeRecord`
16. 任务继续进入后续分析流程

### 关键观察

这说明采购并不是“选一个就结束”，而是：

> 分阶段、逐步升级、在达到目标后自动停止。

---

## 15. 最值得先做的工程落点

如果下一步从文档切到工程，我建议按这个顺序：

1. 让 `State` 支持阶段推进
2. 给引擎加上 `current_stage`
3. 给每次决策写入 `DecisionRecord`
4. 给每次执行写入 `OutcomeRecord`
5. 实现一个最小状态机
6. 再接人工审批队列

也就是说：

**先把流程闭环跑起来，再接真实支付和外部市场。**

---

## 16. 一句话总结

> CPE 的执行流本质上是一套“分阶段采购状态机”：先判断是否需要买，再发现候选、做风控、做排序、执行采购、记录结果，并在达到目标或预算边界时自动停止。
