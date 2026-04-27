# MRAS-Lite 回测结果 v2

生成时间：2026-04-17T19:49:20

## 配置

- 数据库：`/Users/mac/.openclaw/workspace/polymarket/collector/polymarket_data.db`
- 最低流动性：`20000`
- 15m bar 最低样本数：`10`
- recent percentile 窗口：`96` bars
- 最近 24h 高质量 bar 比例门槛：`0.7`
- cooldown：`12.0` 小时
- carry_no 过滤：`{"max_yes_price": 0.02, "min_liquidity": 100000, "max_abs_chg_24h": 0.02, "min_hours_to_event": 72, "max_noise": 2.2}`

## 数据质量

- markets_scanned: **196**
- markets_with_bars: **196**
- markets_with_signals: **125**
- segments_total: **2622**
- segments_ge_24h: **186**
- bars_total: **54047**

## RAW 信号概览

- 总信号数：**1085**
- Regime 分布：`{"carry_no": 802, "mean_revert": 195, "trend": 88}`
- 仓位分布：`{"medium": 871, "small": 214}`
- 方向分布：`{"NO": 1057, "YES": 28}`

## RAW 总体表现

### RAW 4h

- count: **1085**
- hit_rate: **0.0793**
- avg_edge: **9.6e-05**
- median_edge: **0.0**
- avg_roi: **-7.2e-05**
- median_roi: **0.0**
- max_consecutive_losses: **70**

### RAW 12h

- count: **1085**
- hit_rate: **0.1088**
- avg_edge: **0.000364**
- median_edge: **0.0**
- avg_roi: **0.000487**
- median_roi: **0.0**
- max_consecutive_losses: **39**

### RAW 24h

- count: **1085**
- hit_rate: **0.1382**
- avg_edge: **0.000343**
- median_edge: **0.0**
- avg_roi: **-0.000537**
- median_roi: **0.0**
- max_consecutive_losses: **25**

## RAW 分 Regime 表现

### RAW 4h

- **carry_no**: count=802, hit_rate=0.0337, avg_roi=-1.1e-05, max_consecutive_losses=65
- **mean_revert**: count=195, hit_rate=0.1641, avg_roi=0.001143, max_consecutive_losses=15
- **trend**: count=88, hit_rate=0.3068, avg_roi=-0.003315, max_consecutive_losses=7

### RAW 12h

- **carry_no**: count=802, hit_rate=0.0449, avg_roi=-2e-05, max_consecutive_losses=35
- **mean_revert**: count=195, hit_rate=0.2154, avg_roi=0.000291, max_consecutive_losses=9
- **trend**: count=88, hit_rate=0.4545, avg_roi=0.005532, max_consecutive_losses=7

### RAW 24h

- **carry_no**: count=802, hit_rate=0.0586, avg_roi=-7.4e-05, max_consecutive_losses=25
- **mean_revert**: count=195, hit_rate=0.3538, avg_roi=0.00204, max_consecutive_losses=6
- **trend**: count=88, hit_rate=0.3864, avg_roi=-0.01047, max_consecutive_losses=4

## DEDUP 信号概览

- 总信号数：**130**
- Regime 分布：`{"carry_no": 85, "mean_revert": 29, "trend": 16}`
- 仓位分布：`{"medium": 99, "small": 31}`
- 方向分布：`{"NO": 122, "YES": 8}`

## DEDUP 总体表现

### DEDUP 4h

- count: **130**
- hit_rate: **0.1231**
- avg_edge: **0.000177**
- median_edge: **0.0**
- avg_roi: **-0.000533**
- median_roi: **0.0**
- max_consecutive_losses: **64**

### DEDUP 12h

- count: **130**
- hit_rate: **0.1615**
- avg_edge: **0.000281**
- median_edge: **0.0**
- avg_roi: **-0.000385**
- median_roi: **0.0**
- max_consecutive_losses: **35**

### DEDUP 24h

- count: **130**
- hit_rate: **0.1923**
- avg_edge: **0.000792**
- median_edge: **0.0**
- avg_roi: **-0.001144**
- median_roi: **0.0**
- max_consecutive_losses: **25**

## DEDUP 分 Regime 表现

### DEDUP 4h

- **carry_no**: count=85, hit_rate=0.0235, avg_roi=-6.6e-05, max_consecutive_losses=64
- **mean_revert**: count=29, hit_rate=0.3448, avg_roi=0.002817, max_consecutive_losses=12
- **trend**: count=16, hit_rate=0.25, avg_roi=-0.009088, max_consecutive_losses=7

### DEDUP 12h

- **carry_no**: count=85, hit_rate=0.0706, avg_roi=6e-06, max_consecutive_losses=35
- **mean_revert**: count=29, hit_rate=0.3448, avg_roi=0.001777, max_consecutive_losses=12
- **trend**: count=16, hit_rate=0.3125, avg_roi=-0.006384, max_consecutive_losses=6

### DEDUP 24h

- **carry_no**: count=85, hit_rate=0.0706, avg_roi=-9.4e-05, max_consecutive_losses=25
- **mean_revert**: count=29, hit_rate=0.4483, avg_roi=0.005698, max_consecutive_losses=8
- **trend**: count=16, hit_rate=0.375, avg_roi=-0.019118, max_consecutive_losses=4

## Top Examples

- [carry_no] NO conf=0.752 24h_roi=0.001012 | Will Glenn Youngkin win the 2028 US Presidential Election? | 2026-04-15T18:30:00
- [carry_no] NO conf=0.752 24h_roi=0.001011 | Will Mark Cuban win the 2028 Democratic presidential nomination? | 2026-04-15T18:30:00
- [carry_no] NO conf=0.752 24h_roi=0.001005 | Will South Korea win the 2026 FIFA World Cup? | 2026-04-15T18:30:00
- [carry_no] NO conf=0.752 24h_roi=0.000506 | Will Thomas Massie win the 2028 US Presidential Election? | 2026-04-15T18:30:00
- [carry_no] NO conf=0.752 24h_roi=0.000506 | Will Wes Moore win the 2028 Democratic presidential nomination? | 2026-04-15T18:30:00
- [carry_no] NO conf=0.752 24h_roi=0.0 | Will Iraq win the 2026 FIFA World Cup? | 2026-04-15T18:30:00
- [carry_no] NO conf=0.752 24h_roi=0.0 | Will Haiti win the 2026 FIFA World Cup? | 2026-04-15T18:30:00
- [carry_no] NO conf=0.752 24h_roi=0.0 | Will Qatar win the 2026 FIFA World Cup? | 2026-04-15T18:30:00
- [carry_no] NO conf=0.752 24h_roi=0.0 | Will Panama win the 2026 FIFA World Cup? | 2026-04-15T18:30:00
- [carry_no] NO conf=0.752 24h_roi=0.0 | Will Bosnia-Herzegovina win the 2026 FIFA World Cup? | 2026-04-15T18:30:00
