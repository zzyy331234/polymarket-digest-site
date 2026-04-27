# Polymarket 策略整理与审计（2026-04-15）

## 一、当前目录与职责

### 1. 主策略与运行脚本
- `polymarket/polymarket_forecast.py`
  - 主扫描器
  - 当前核心策略：MRAS（Regime Detection → Direction → Confidence/Position）
- `polymarket/run_forecast.sh`
  - 每 30 分钟执行 forecast scan
- `polymarket/refresh_scanner.sh`
  - 只刷新 dashboard cache，不刷新 A 股
- `polymarket/run_smartmoney.sh`
  - 每 30 分钟执行聪明钱扫描
- `polymarket/smart_money_monitor.py`
  - 聪明钱逻辑

### 2. 数据采集层
- `polymarket/collector/collector.py`
  - 采集 Polymarket 市场与价格数据
- `polymarket/collector/polymarket_data.db`
  - SQLite 主数据库
- `polymarket/collector/view.py`
  - 数据查看工具

### 3. 展示层 / 看板
- `dashboard/data/fetcher.py`
  - 从 SQLite 读取 Polymarket 数据，并生成 scanner_signals
- `dashboard/app.py`
  - Streamlit 看板（http://localhost:8502）

### 4. 其他资料
- `polymarket/mcp_server/`
  - 一整套额外 Polymarket MCP/server 项目
  - 更多像资料库 / 外部项目，不是当前主线策略核心

---

## 二、当前 MRAS 策略概要

### 策略目标
从所有流动性足够的市场里，识别四类状态：
- `trend`
- `mean_revert`
- `contrarian`
- `no_trade`

### 当前框架
1. **Regime Detection**：先判断市场状态
2. **Direction**：再决定做 YES 还是 NO
3. **Confidence / Position**：最后给出置信度与仓位

### 当前主要参数
- 基础过滤：`liquidity >= 20000`
- 普通信号门槛：`confidence >= 0.45`
- contrarian 门槛：`confidence >= 0.55`
- 仓位：
  - `large >= 0.80`
  - `medium >= 0.65`
  - `small < 0.65`

---

## 三、我看到的核心问题（按优先级排序）

## P0：数据定义错误，1D 和 1W 其实是同一件事

### 现状
`fetch_real_markets()` / `fetch_polymarket_scanner()` 都是这样算的：
- `one_day_change = (latest - first_price) / first_price`
- `one_week_change = (latest - first_price) / first_price`

也就是说：
- 现在的 **1D 变化率** 不是最近 1 天
- 现在的 **1W 变化率** 也不是最近 1 周
- 两者本质上都是“数据库最早点到当前”的总变化率

### 后果
- trend 的“1W + 1D 同向确认”是伪确认
- 你以为有两个独立维度，其实只有一个维度重复用了两次
- regime 判定会严重偏向 trend

### 建议
必须改成真正的窗口计算：
- `1h`
- `4h`
- `24h`
- `7d`

至少要把：
- `oneDayPriceChange` 改成最近 **24h**
- `oneWeekPriceChange` 改成最近 **7d**

如果当前数据库长度不够：
- 不要伪造 1W
- 应返回 `None` / `0` 并降低置信度，而不是复用 first_price

---

## P0：Trend 条件表面上是“交叉验证”，实际上高度相关

### 现状
trend_hits 来源：
- `abs(one_week) >= 0.05`
- `one_week > 0 and one_day > 0`
- `one_week < 0 and one_day < 0`
- `liquidity >= 50000`

### 后果
因为 `one_day` 和 `one_week` 目前是同源数据：
- 只要有一个价格趋势，几乎自动同时命中两个趋势条件
- 再加一个流动性，就很容易达到 `trend_hits >= 2`

所以现在 scanner 里：
- `trend` 占绝大多数（当前 98 个信号里 90 个是 trend）
- 策略几乎退化成“有点涨跌幅 + 流动性够 = trend”

### 建议
把 trend 的确认拆开成真正独立的维度，例如：
- 24h 变化率
- 7d 变化率
- 近 N 小时连续斜率 / 连续上涨条数
- 订单簿方向 / 成交量放大
- 波动率过滤

---

## P0：高赔率/低赔率市场被 trend 误触发

### 现状
像 YES 价格极低（0.1% ~ 3%）的市场，只要短期有一点波动，也可能被判成 trend。

当前信号里有大量这种市场：
- Qatar / Egypt / Cape Verde / Curaçao 等世界杯极低概率市场
- 这些市场很多只是长期极低赔率 + 短期价格抖动

### 后果
- 会出现“YES 价格 0.015 涨了 10%，就给出高置信度 YES/NO trend 信号”
- 这种信号统计上容易很多，但交易价值未必高
- 特别容易把 **赔率微小跳动** 错当成趋势

### 建议
增加价格区间过滤：
- `yes_price <= 0.03` 或 `yes_price >= 0.97` 的市场
  - 默认不允许进入 trend
  - 只能走 mean_revert / special bucket

也可以单独做：
- `ultra-low-probability regime`
- `binary floor/ceiling regime`

---

## P0：event_time 惩罚基本没有生效

### 现状
`calculate_signal()` 里有：
- 距事件 <= 6h / 24h / 48h 的 `event_penalty`

但 `fetch_real_markets()` 读取 SQLite 时并没有把 event_time 带进 market dict。

### 后果
- 大部分市场 `hours_to_event = None`
- 事件临近惩罚逻辑几乎没用
- 临近结算的市场没有被有效降权

### 建议
采集层/表结构里补上：
- event_time / close_time / resolution_time

然后在 scanner 中：
- 剩余时间太短时降权
- 或直接禁止新开仓

---

## P1：liquidity_bonus 有逻辑 bug

### 现状
`polymarket_forecast.py` 里：
```python
if liquidity >= 50000:
    liquidity_bonus = 0.08
elif liquidity >= 100000:
    liquidity_bonus = 0.12
```

### 问题
这个顺序是错的：
- 当 `liquidity >= 100000` 时，前面的 `>= 50000` 已经先命中了
- 所以 `0.12` 永远进不去

`dashboard/data/fetcher.py` 里也有同样问题：
```python
liq_bonus = 0.08 if liquidity >= 50000 else (0.12 if liquidity >= 100000 else 0.0)
```
同样会导致 `>=100000` 只能拿到 `0.08`

### 建议
改成：
```python
if liquidity >= 100000:
    liquidity_bonus = 0.12
elif liquidity >= 50000:
    liquidity_bonus = 0.08
```

---

## P1：RSI 目前恒等于 50，相关逻辑形同虚设

### 现状
从 DB 读取时：
- `rsi = 50.0`

### 后果
以下逻辑都失真：
- RSI extreme 加分失效
- mean_revert 的 RSI 条件失效
- contrarian 的 RSI 条件失效

### 建议
短期有两种方案：
1. **直接移除 RSI 相关条件**（最干净）
2. 用 price_history 实时计算一个简化 RSI（推荐）

如果继续保留固定 50：
- 就不要在策略里假装用了 RSI

---

## P1：price_percentile 计算过于简化，短历史时噪音很大

### 现状
当前 percentile 用：
- `(latest - min_yes) / (max_yes - min_yes)`

### 问题
- 历史短时，min/max 很容易被偶然点决定
- 容易出现百分位过度极端
- 不是严格意义上的 percentile，只是 min-max 归一化

### 建议
改成真正分位数：
- 用过去 N 个点排序后的百分位
- 或至少用 rolling window（如最近 3d / 7d）

---

## P1：dashboard 与主策略逻辑重复，存在漂移风险

### 现状
- `polymarket_forecast.py` 有一套 MRAS 逻辑
- `dashboard/data/fetcher.py` 里 `_compute_scanner_signals()` 又复制了一套几乎同样的逻辑

### 后果
- 以后改一个忘了改另一个，结果会不一致
- 看板和命令行 scanner 可能出现不同信号

### 建议
抽成一个独立模块，例如：
- `polymarket/mras_strategy.py`

然后：
- CLI 调它
- Dashboard 也调它
- 只保留一份策略代码

---

## P2：confidence 分布过于集中，区分度不够

### 现状
当前缓存里：
- 大量信号 `confidence = 1.00`
- 其次大批 `0.93`
- 再少量 `0.78`

### 后果
- 置信度失去排序意义
- `large` 仓位过多（当前 98 个信号里 91 个是 large）
- 实战中很难区分真正强信号 vs 普通信号

### 建议
压缩 confidence：
- base_confidence 不要直接线性顶满
- bonus 上限降低
- 给 event/volatility/noise 引入扣分

例如：
- 最终分数限制在 0.35 ~ 0.90 更合理
- 大于 0.80 的信号应该是少数，不应占绝大多数

---

## P2：mean_revert 与 contrarian 仍然偏弱

### 现状
现在 fresh data 下：
- trend = 90
- mean_revert = 7
- contrarian = 1

### 说明
这不一定完全错，但比例明显失衡。
原因主要有：
- 数据特征还偏单薄
- RSI 无效
- 1D/1W 定义错误
- 极端价格市场先被 trend 吃掉

### 建议
优先修正数据窗口和极端价格过滤，再重新看 regime 分布。

---

## 四、建议的调整顺序（最务实版本）

### 第一阶段（必须先做）
1. 修正 `one_day_change` / `one_week_change` 真正按 24h / 7d 计算
2. 修正 `liquidity_bonus` 顺序 bug
3. 给 ultra-low / ultra-high price 市场增加 trend 过滤
4. 让 event_time 真正接入策略

### 第二阶段（强烈建议）
5. 把 RSI 改成真实计算，或者临时删掉 RSI 条件
6. 把 percentile 改成 rolling percentile
7. 把策略逻辑抽成单独模块，避免 dashboard / scanner 漂移

### 第三阶段（做强策略）
8. 增加波动率过滤 / 噪音过滤
9. 把 confidence 重新标定，减少 1.00 泛滥
10. 针对低赔率市场单独做 regime

---

## 五、结论

当前这套 MRAS 已经比旧版更像“策略”了，但**最大的瓶颈已经不在阈值，而在数据定义本身**。

最关键的不是继续微调 0.45 / 0.55 这种门槛，而是先解决：
- 1D / 1W 伪窗口
- 极端赔率市场误判
- event_time 没接上
- RSI 是假值
- scanner / dashboard 双份逻辑漂移

如果先把这些问题修掉，再回头调 regime 阈值，策略会稳定很多。
