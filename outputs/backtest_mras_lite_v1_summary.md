# MRAS-Lite 回测结果 v1

生成时间：2026-04-17T19:41:51

## 配置

- 数据库：`/Users/mac/.openclaw/workspace/polymarket/collector/polymarket_data.db`
- 最低流动性：`20000`
- 15m bar 最低样本数：`10`
- recent percentile 窗口：`96` bars
- 最近 24h 高质量 bar 比例门槛：`0.7`

## 数据质量

- markets_scanned: **196**
- markets_with_bars: **196**
- markets_with_signals: **169**
- segments_total: **2622**
- segments_ge_24h: **186**
- bars_total: **53860**

## 信号概览

- 总信号数：**1595**
- Regime 分布：`{"carry_no": 1360, "mean_revert": 173, "trend": 62}`
- 仓位分布：`{"medium": 985, "small": 610}`
- 方向分布：`{"NO": 1570, "YES": 25}`

## 总体表现

### 4h

- count: **1595**
- hit_rate: **0.1266**
- avg_edge: **8.9e-05**
- median_edge: **0.0**
- avg_roi: **0.000137**
- median_roi: **0.0**
- max_consecutive_losses: **45**

### 12h

- count: **1595**
- hit_rate: **0.1824**
- avg_edge: **0.000348**
- median_edge: **0.0**
- avg_roi: **0.000606**
- median_roi: **0.0**
- max_consecutive_losses: **45**

### 24h

- count: **1585**
- hit_rate: **0.1912**
- avg_edge: **0.0004**
- median_edge: **0.0**
- avg_roi: **0.000392**
- median_roi: **0.0**
- max_consecutive_losses: **29**

## 分 Regime 表现

### 4h

- **carry_no**: count=1360, hit_rate=0.111, avg_roi=1.5e-05, max_consecutive_losses=44
- **mean_revert**: count=173, hit_rate=0.1676, avg_roi=0.001271, max_consecutive_losses=14
- **trend**: count=62, hit_rate=0.3548, avg_roi=-0.000344, max_consecutive_losses=4

### 12h

- **carry_no**: count=1360, hit_rate=0.1721, avg_roi=0.000121, max_consecutive_losses=41
- **mean_revert**: count=173, hit_rate=0.1908, avg_roi=0.000275, max_consecutive_losses=9
- **trend**: count=62, hit_rate=0.3871, avg_roi=0.012177, max_consecutive_losses=5

### 24h

- **carry_no**: count=1350, hit_rate=0.1711, avg_roi=0.000169, max_consecutive_losses=30
- **mean_revert**: count=173, hit_rate=0.3295, avg_roi=0.002205, max_consecutive_losses=7
- **trend**: count=62, hit_rate=0.2419, avg_roi=0.00018, max_consecutive_losses=6

## Top Examples

- [carry_no] NO conf=0.71 24h_roi=0.003014 | Will the Orlando Magic win the 2026 NBA Finals? | 2026-04-15T19:15:00
- [carry_no] NO conf=0.71 24h_roi=0.003014 | Will the Orlando Magic win the 2026 NBA Finals? | 2026-04-15T19:45:00
- [carry_no] NO conf=0.71 24h_roi=0.002548 | Will the Boston Bruins win the 2026 NHL Stanley Cup? | 2026-04-15T18:30:00
- [carry_no] NO conf=0.71 24h_roi=0.002036 | Will the Los Angeles Lakers win the 2026 NBA Finals? | 2026-04-15T20:00:00
- [carry_no] NO conf=0.71 24h_roi=0.001529 | Will the Boston Bruins win the 2026 NHL Stanley Cup? | 2026-04-15T20:00:00
- [carry_no] NO conf=0.71 24h_roi=0.00103 | Will the Pittsburgh Penguins win the 2026 NHL Stanley Cup? | 2026-04-15T19:45:00
- [carry_no] NO conf=0.71 24h_roi=0.00103 | Will the Pittsburgh Penguins win the 2026 NHL Stanley Cup? | 2026-04-15T20:00:00
- [carry_no] NO conf=0.71 24h_roi=0.00103 | Will the Pittsburgh Penguins win the 2026 NHL Stanley Cup? | 2026-04-15T20:15:00
- [carry_no] NO conf=0.71 24h_roi=0.00103 | Will the Utah Mammoth win the 2026 NHL Stanley Cup? | 2026-04-15T19:15:00
- [carry_no] NO conf=0.71 24h_roi=0.001023 | Will Jon Stewart win the 2028 Democratic presidential nomination? | 2026-04-15T18:30:00
