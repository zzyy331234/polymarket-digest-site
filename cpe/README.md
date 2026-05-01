# Capability Procurement Engine (CPE)

一个面向 Agent 的 **外部能力采购决策内核**。

CPE 不负责替代支付协议，也不负责替代模型路由器；它解决的是更上层的一个问题：

> 在任务执行过程中，Agent 什么时候值得花钱买更强的信息和能力？

换句话说，CPE 让 Agent 不只是“会调用工具”，而是会像一个 **有预算、有风控、会按 ROI 做决策的分析员** 一样行动。

---

## 1. CPE 是什么

CPE 的定位是：

## **Agent 的外部能力采购决策大脑**

它主要负责：

- 该不该买
- 买哪个
- 为什么买
- 自动还是人工审批
- 买完后效果如何
- 这些经验如何反过来影响下一轮采购

它不直接解决：

- x402 本身的支付协议
- wallet / settlement
- 单纯的 API registry
- 单纯的 budget guardrail

更准确地说：

- **x402** 解决 *怎么付钱*
- **budget / CFO layer** 解决 *能不能付*
- **CPE** 解决 *该不该付、买什么、为什么买*

---

## 2. 当前原型能力

这个目录下的原型已经具备：

### 决策层
- 任务价值 / 紧急度 / 风险 / ROI / 预算约束评估
- 候选 capability 排序
- auto / manual path 区分

### 治理层
- 最小状态机
- 审批队列
- manual capability 审批 gate

### 反馈层
- ledger 记录
- outcome 回写
- capability 历史表现更新
- 同一次多轮运行内读取最新能力画像
- score change explanation

### 演示层
- 单轮 demo
- 多轮 demo
- manual approval demo

也就是说，这已经不是概念草图，而是一个 **可运行的 alpha 内核**。

---

## 3. 目录结构

```text
cpe/
  README.md

  # 文档
  concept_note.md
  data_schema.md
  execution_flow.md

  # 核心代码
  schemas.py
  procurement_engine.py
  ledger.py
  state_machine.py
  capability_store.py
  approval_queue.py
  update_capability_stats.py

  # demos
  ledger_demo.py
  state_machine_demo.py
  approval_queue_demo.py
  run_cpe_demo.py
  run_cpe_multiround_demo.py
  run_cpe_manual_demo.py
  reset_runtime_catalog.py

  # 基线数据
  samples/
    procurement_capabilities.sample.json
    procurement_policy.sample.json
    procurement_task.sample.json
    procurement_state.sample.json

  # 运行态数据
  runtime/
    procurement_capabilities.runtime.json
    approval_queue.json

  # 账本
  ledger/
    decision_records.jsonl
    outcome_records.jsonl
```

---

## 4. 文档说明

### `concept_note.md`
讲清楚：
- CPE 的定位
- 和 x402 / CFO / marketplace / model router 的边界
- 核心架构
- 演进路线

### `data_schema.md`
定义：
- Task
- State
- Capability
- Policy
- DecisionRecord
- OutcomeRecord
- Ledger Event

### `execution_flow.md`
定义：
- 顶层执行链
- 分阶段采购
- auto / manual 审批
- 回退 / 降级逻辑
- 最小状态机

---

## 5. 核心代码说明

### `schemas.py`
统一定义核心数据结构：
- `Task`
- `State`
- `Capability`
- `Policy`
- `DecisionRecord`
- `OutcomeRecord`

### `procurement_engine.py`
核心采购决策引擎。

当前支持：
- hard constraints
- score calculation
- capability ranking
- auto/manual 决策
- 历史表现参与打分

### `ledger.py`
最小 JSONL ledger 层。

负责：
- decision record 写入
- outcome record 写入
- ledger summary

### `state_machine.py`
最小采购状态机。

支持：
- created
- assessing
- discovering
- deciding
- awaiting_approval
- executing
- evaluating_outcome
- fallback
- completed
- aborted

### `capability_store.py`
capability catalog 的读取、落盘、反馈更新。

### `approval_queue.py`
最小审批队列抽象。

支持：
- 添加审批请求
- 列出全部请求
- 按状态过滤
- 更新审批状态

### `update_capability_stats.py`
根据 outcome 更新 capability 的历史表现：
- `historical_success_rate`
- `historical_confidence_delta_avg`
- `historical_roi_avg`

---

## 6. Demo 说明

### 6.1 单轮 demo
```bash
python3 run_cpe_demo.py
```

作用：
- 跑一轮完整流程
- 生成 decision / outcome / ledger

---

### 6.2 多轮采购 demo
```bash
python3 run_cpe_multiround_demo.py
```

作用：
- 跑多轮采购
- 避免重复使用同一 capability
- 回写 capability 历史表现
- 同次运行内重新读取 runtime catalog
- 输出 capability before / after 与 score explanation

---

### 6.3 manual 审批主流程 demo
```bash
python3 run_cpe_manual_demo.py
```

作用：
- 强制触发 manual capability
- 创建审批请求
- 写入审批队列
- 审批通过后执行
- 输出完整 manual path 状态流

---

### 6.4 ledger demo
```bash
python3 ledger_demo.py
```

### 6.5 state machine demo
```bash
python3 state_machine_demo.py
```

### 6.6 approval queue demo
```bash
python3 approval_queue_demo.py
```

### 6.7 重置 runtime catalog
```bash
python3 reset_runtime_catalog.py
```

---

## 7. sample / runtime 分离

### 基线样例
位于：
- `samples/procurement_capabilities.sample.json`

作用：
- 保持干净的初始能力目录
- 作为 runtime catalog 的重建来源

### 运行态目录
位于：
- `runtime/procurement_capabilities.runtime.json`

作用：
- 被 demo 真正读写
- 随 outcome 更新而演化

这样可以做到：
- sample 保持基线
- runtime 作为实验现场

---

## 8. 当前原型最有价值的点

我认为这套原型目前最有价值的不是“会打分”，而是它已经具备：

### 1. 分阶段采购
不是一上来重投入，而是逐轮升级能力。

### 2. 可解释决策
每次为什么买、为什么不买，都有结构化输出。

### 3. 反馈闭环
采购结果会回写到 capability 历史表现里。

### 4. 运行态学习
后续轮次会带着更新后的能力画像继续决策。

### 5. 治理路径
manual capability 已经能走：

```text
awaiting_approval → approval_queue → approved → executing
```

---

## 9. 当前限制

当前仍然是 alpha 原型，尚未完成：

- 真正接入 x402 / wallet / marketplace
- 真正接入外部真实 paid capability
- 审批拒绝分支的完整处理
- 多 capability 组合采购
- 更成熟的学习型 ROI 模型
- 正式模块化重构（engines / stores / demos / docs）

所以现在适合：
- 架构验证
- 概念澄清
- 原型演示
- 后续接真实业务前的设计沉淀

---

## 10. 建议的下一步

现在最值得继续推进的方向：

1. **审批拒绝 / pending 分支真正影响执行**
2. **把 auto / manual 路径统一成场景工厂**
3. **把 capability 历史反馈真正接入下一轮排序差异分析**
4. **接一个更贴近真实世界的 paid capability**
5. **再决定是否对接具体业务系统**

---

## 11. 一句话总结

> Capability Procurement Engine 不是让 Agent 只是“能花钱”，而是让它知道：什么时候该花、为什么该花、该花在哪一项能力上最值。 
