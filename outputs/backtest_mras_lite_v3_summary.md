# MRAS-Lite 回测结果 v3

生成时间：2026-04-17T19:57:15

## 配置

- 数据库：`/Users/mac/.openclaw/workspace/polymarket/collector/polymarket_data.db`
- 最低流动性：`20000`
- 15m bar 最低样本数：`10`
- recent percentile 窗口：`96` bars
- 最近 24h 高质量 bar 比例门槛：`0.7`
- cooldown：`12.0` 小时
- carry_no_enabled：`False`
- strategy_focus：`mean_revert_first`

## 数据质量

- markets_scanned: **195**
- markets_with_bars: **195**
- markets_with_signals: **28**
- segments_total: **2608**
- segments_ge_24h: **185**
- bars_total: **53758**

## RAW 信号概览

- 总信号数：**137**
- Regime 分布：`{"mean_revert": 35, "trend": 102}`
- 仓位分布：`{"medium": 88, "small": 49}`
- 方向分布：`{"NO": 48, "YES": 89}`

## RAW 总体表现

### RAW 4h

- count: **137**
- hit_rate: **0.2482**
- avg_edge: **-0.00038**
- median_edge: **0.0**
- avg_roi: **-0.009927**
- median_roi: **0.0**
- max_consecutive_losses: **12**

### RAW 8h

- count: **137**
- hit_rate: **0.3869**
- avg_edge: **0.000164**
- median_edge: **0.0**
- avg_roi: **-0.010893**
- median_roi: **0.0**
- max_consecutive_losses: **7**

### RAW 12h

- count: **137**
- hit_rate: **0.3869**
- avg_edge: **-6.2e-05**
- median_edge: **0.0**
- avg_roi: **-0.028318**
- median_roi: **0.0**
- max_consecutive_losses: **7**

### RAW 24h

- count: **137**
- hit_rate: **0.365**
- avg_edge: **-0.000398**
- median_edge: **0.0**
- avg_roi: **-0.039959**
- median_roi: **0.0**
- max_consecutive_losses: **8**

## RAW 分 Regime 表现

### RAW 4h

- **mean_revert**: count=35, hit_rate=0.4, avg_roi=0.005292, max_consecutive_losses=5
- **trend**: count=102, hit_rate=0.1961, avg_roi=-0.015149, max_consecutive_losses=27

### RAW 8h

- **mean_revert**: count=35, hit_rate=0.7429, avg_roi=0.025868, max_consecutive_losses=3
- **trend**: count=102, hit_rate=0.2647, avg_roi=-0.023507, max_consecutive_losses=8

### RAW 12h

- **mean_revert**: count=35, hit_rate=0.6571, avg_roi=0.029818, max_consecutive_losses=2
- **trend**: count=102, hit_rate=0.2941, avg_roi=-0.048266, max_consecutive_losses=7

### RAW 24h

- **mean_revert**: count=35, hit_rate=0.6, avg_roi=0.058085, max_consecutive_losses=2
- **trend**: count=102, hit_rate=0.2843, avg_roi=-0.073601, max_consecutive_losses=6

## DEDUP 信号概览

- 总信号数：**34**
- Regime 分布：`{"mean_revert": 8, "trend": 26}`
- 仓位分布：`{"medium": 20, "small": 14}`
- 方向分布：`{"NO": 14, "YES": 20}`

## DEDUP 总体表现

### DEDUP 4h

- count: **34**
- hit_rate: **0.2941**
- avg_edge: **-0.000632**
- median_edge: **0.0**
- avg_roi: **-0.003195**
- median_roi: **0.0**
- max_consecutive_losses: **6**

### DEDUP 8h

- count: **34**
- hit_rate: **0.3235**
- avg_edge: **-0.000574**
- median_edge: **-0.0005**
- avg_roi: **-0.016755**
- median_roi: **-0.000519**
- max_consecutive_losses: **7**

### DEDUP 12h

- count: **34**
- hit_rate: **0.2647**
- avg_edge: **-0.000765**
- median_edge: **-0.0005**
- avg_roi: **-0.031904**
- median_roi: **-0.000764**
- max_consecutive_losses: **7**

### DEDUP 24h

- count: **34**
- hit_rate: **0.3235**
- avg_edge: **-0.00075**
- median_edge: **-0.0005**
- avg_roi: **-0.025713**
- median_roi: **-0.000774**
- max_consecutive_losses: **5**

## DEDUP 分 Regime 表现

### DEDUP 4h

- **mean_revert**: count=8, hit_rate=0.5, avg_roi=0.013975, max_consecutive_losses=4
- **trend**: count=26, hit_rate=0.2308, avg_roi=-0.008478, max_consecutive_losses=10

### DEDUP 8h

- **mean_revert**: count=8, hit_rate=0.75, avg_roi=0.012829, max_consecutive_losses=1
- **trend**: count=26, hit_rate=0.1923, avg_roi=-0.025858, max_consecutive_losses=10

### DEDUP 12h

- **mean_revert**: count=8, hit_rate=0.5, avg_roi=0.016905, max_consecutive_losses=1
- **trend**: count=26, hit_rate=0.1923, avg_roi=-0.046922, max_consecutive_losses=10

### DEDUP 24h

- **mean_revert**: count=8, hit_rate=0.5, avg_roi=0.026735, max_consecutive_losses=1
- **trend**: count=26, hit_rate=0.2692, avg_roi=-0.041852, max_consecutive_losses=7

# RAW_SLICES

## RAW_SLICES all 信号概览

- 总信号数：**137**
- Regime 分布：`{"mean_revert": 35, "trend": 102}`
- 仓位分布：`{"medium": 88, "small": 49}`
- 方向分布：`{"NO": 48, "YES": 89}`

## RAW_SLICES all 总体表现

### RAW_SLICES all 4h

- count: **137**
- hit_rate: **0.2482**
- avg_edge: **-0.00038**
- median_edge: **0.0**
- avg_roi: **-0.009927**
- median_roi: **0.0**
- max_consecutive_losses: **12**

### RAW_SLICES all 8h

- count: **137**
- hit_rate: **0.3869**
- avg_edge: **0.000164**
- median_edge: **0.0**
- avg_roi: **-0.010893**
- median_roi: **0.0**
- max_consecutive_losses: **7**

### RAW_SLICES all 12h

- count: **137**
- hit_rate: **0.3869**
- avg_edge: **-6.2e-05**
- median_edge: **0.0**
- avg_roi: **-0.028318**
- median_roi: **0.0**
- max_consecutive_losses: **7**

### RAW_SLICES all 24h

- count: **137**
- hit_rate: **0.365**
- avg_edge: **-0.000398**
- median_edge: **0.0**
- avg_roi: **-0.039959**
- median_roi: **0.0**
- max_consecutive_losses: **8**

## RAW_SLICES all 分 Regime 表现

### RAW_SLICES all 4h

- **mean_revert**: count=35, hit_rate=0.4, avg_roi=0.005292, max_consecutive_losses=5
- **trend**: count=102, hit_rate=0.1961, avg_roi=-0.015149, max_consecutive_losses=27

### RAW_SLICES all 8h

- **mean_revert**: count=35, hit_rate=0.7429, avg_roi=0.025868, max_consecutive_losses=3
- **trend**: count=102, hit_rate=0.2647, avg_roi=-0.023507, max_consecutive_losses=8

### RAW_SLICES all 12h

- **mean_revert**: count=35, hit_rate=0.6571, avg_roi=0.029818, max_consecutive_losses=2
- **trend**: count=102, hit_rate=0.2941, avg_roi=-0.048266, max_consecutive_losses=7

### RAW_SLICES all 24h

- **mean_revert**: count=35, hit_rate=0.6, avg_roi=0.058085, max_consecutive_losses=2
- **trend**: count=102, hit_rate=0.2843, avg_roi=-0.073601, max_consecutive_losses=6

## RAW_SLICES no_carry 信号概览

- 总信号数：**137**
- Regime 分布：`{"mean_revert": 35, "trend": 102}`
- 仓位分布：`{"medium": 88, "small": 49}`
- 方向分布：`{"NO": 48, "YES": 89}`

## RAW_SLICES no_carry 总体表现

### RAW_SLICES no_carry 4h

- count: **137**
- hit_rate: **0.2482**
- avg_edge: **-0.00038**
- median_edge: **0.0**
- avg_roi: **-0.009927**
- median_roi: **0.0**
- max_consecutive_losses: **12**

### RAW_SLICES no_carry 8h

- count: **137**
- hit_rate: **0.3869**
- avg_edge: **0.000164**
- median_edge: **0.0**
- avg_roi: **-0.010893**
- median_roi: **0.0**
- max_consecutive_losses: **7**

### RAW_SLICES no_carry 12h

- count: **137**
- hit_rate: **0.3869**
- avg_edge: **-6.2e-05**
- median_edge: **0.0**
- avg_roi: **-0.028318**
- median_roi: **0.0**
- max_consecutive_losses: **7**

### RAW_SLICES no_carry 24h

- count: **137**
- hit_rate: **0.365**
- avg_edge: **-0.000398**
- median_edge: **0.0**
- avg_roi: **-0.039959**
- median_roi: **0.0**
- max_consecutive_losses: **8**

## RAW_SLICES no_carry 分 Regime 表现

### RAW_SLICES no_carry 4h

- **mean_revert**: count=35, hit_rate=0.4, avg_roi=0.005292, max_consecutive_losses=5
- **trend**: count=102, hit_rate=0.1961, avg_roi=-0.015149, max_consecutive_losses=27

### RAW_SLICES no_carry 8h

- **mean_revert**: count=35, hit_rate=0.7429, avg_roi=0.025868, max_consecutive_losses=3
- **trend**: count=102, hit_rate=0.2647, avg_roi=-0.023507, max_consecutive_losses=8

### RAW_SLICES no_carry 12h

- **mean_revert**: count=35, hit_rate=0.6571, avg_roi=0.029818, max_consecutive_losses=2
- **trend**: count=102, hit_rate=0.2941, avg_roi=-0.048266, max_consecutive_losses=7

### RAW_SLICES no_carry 24h

- **mean_revert**: count=35, hit_rate=0.6, avg_roi=0.058085, max_consecutive_losses=2
- **trend**: count=102, hit_rate=0.2843, avg_roi=-0.073601, max_consecutive_losses=6

## RAW_SLICES mean_revert_only 信号概览

- 总信号数：**35**
- Regime 分布：`{"mean_revert": 35}`
- 仓位分布：`{"medium": 19, "small": 16}`
- 方向分布：`{"YES": 35}`

## RAW_SLICES mean_revert_only 总体表现

### RAW_SLICES mean_revert_only 4h

- count: **35**
- hit_rate: **0.4**
- avg_edge: **0.000114**
- median_edge: **0.0**
- avg_roi: **0.005292**
- median_roi: **0.0**
- max_consecutive_losses: **5**

### RAW_SLICES mean_revert_only 8h

- count: **35**
- hit_rate: **0.7429**
- avg_edge: **0.001043**
- median_edge: **0.001**
- avg_roi: **0.025868**
- median_roi: **0.024845**
- max_consecutive_losses: **3**

### RAW_SLICES mean_revert_only 12h

- count: **35**
- hit_rate: **0.6571**
- avg_edge: **0.001371**
- median_edge: **0.001**
- avg_roi: **0.029818**
- median_roi: **0.034783**
- max_consecutive_losses: **2**

### RAW_SLICES mean_revert_only 24h

- count: **35**
- hit_rate: **0.6**
- avg_edge: **0.002257**
- median_edge: **0.002**
- avg_roi: **0.058085**
- median_roi: **0.024845**
- max_consecutive_losses: **2**

## RAW_SLICES mean_revert_only 分 Regime 表现

### RAW_SLICES mean_revert_only 4h

- **mean_revert**: count=35, hit_rate=0.4, avg_roi=0.005292, max_consecutive_losses=5

### RAW_SLICES mean_revert_only 8h

- **mean_revert**: count=35, hit_rate=0.7429, avg_roi=0.025868, max_consecutive_losses=3

### RAW_SLICES mean_revert_only 12h

- **mean_revert**: count=35, hit_rate=0.6571, avg_roi=0.029818, max_consecutive_losses=2

### RAW_SLICES mean_revert_only 24h

- **mean_revert**: count=35, hit_rate=0.6, avg_roi=0.058085, max_consecutive_losses=2

## RAW_SLICES trend_only 信号概览

- 总信号数：**102**
- Regime 分布：`{"trend": 102}`
- 仓位分布：`{"medium": 69, "small": 33}`
- 方向分布：`{"NO": 48, "YES": 54}`

## RAW_SLICES trend_only 总体表现

### RAW_SLICES trend_only 4h

- count: **102**
- hit_rate: **0.1961**
- avg_edge: **-0.000549**
- median_edge: **0.0**
- avg_roi: **-0.015149**
- median_roi: **0.0**
- max_consecutive_losses: **27**

### RAW_SLICES trend_only 8h

- count: **102**
- hit_rate: **0.2647**
- avg_edge: **-0.000137**
- median_edge: **-0.0005**
- avg_roi: **-0.023507**
- median_roi: **-0.000504**
- max_consecutive_losses: **8**

### RAW_SLICES trend_only 12h

- count: **102**
- hit_rate: **0.2941**
- avg_edge: **-0.000554**
- median_edge: **-0.00025**
- avg_roi: **-0.048266**
- median_roi: **-0.000253**
- max_consecutive_losses: **7**

### RAW_SLICES trend_only 24h

- count: **102**
- hit_rate: **0.2843**
- avg_edge: **-0.001309**
- median_edge: **-0.001**
- avg_roi: **-0.073601**
- median_roi: **-0.001017**
- max_consecutive_losses: **6**

## RAW_SLICES trend_only 分 Regime 表现

### RAW_SLICES trend_only 4h

- **trend**: count=102, hit_rate=0.1961, avg_roi=-0.015149, max_consecutive_losses=27

### RAW_SLICES trend_only 8h

- **trend**: count=102, hit_rate=0.2647, avg_roi=-0.023507, max_consecutive_losses=8

### RAW_SLICES trend_only 12h

- **trend**: count=102, hit_rate=0.2941, avg_roi=-0.048266, max_consecutive_losses=7

### RAW_SLICES trend_only 24h

- **trend**: count=102, hit_rate=0.2843, avg_roi=-0.073601, max_consecutive_losses=6

## RAW_SLICES contrarian_only 信号概览

- 总信号数：**0**
- Regime 分布：`{}`
- 仓位分布：`{}`
- 方向分布：`{}`

## RAW_SLICES contrarian_only 总体表现

### RAW_SLICES contrarian_only 4h

- count: **0**
- hit_rate: **None**
- avg_edge: **None**
- median_edge: **None**
- avg_roi: **None**
- median_roi: **None**
- max_consecutive_losses: **None**

### RAW_SLICES contrarian_only 8h

- count: **0**
- hit_rate: **None**
- avg_edge: **None**
- median_edge: **None**
- avg_roi: **None**
- median_roi: **None**
- max_consecutive_losses: **None**

### RAW_SLICES contrarian_only 12h

- count: **0**
- hit_rate: **None**
- avg_edge: **None**
- median_edge: **None**
- avg_roi: **None**
- median_roi: **None**
- max_consecutive_losses: **None**

### RAW_SLICES contrarian_only 24h

- count: **0**
- hit_rate: **None**
- avg_edge: **None**
- median_edge: **None**
- avg_roi: **None**
- median_roi: **None**
- max_consecutive_losses: **None**

## RAW_SLICES contrarian_only 分 Regime 表现

### RAW_SLICES contrarian_only 4h


### RAW_SLICES contrarian_only 8h


### RAW_SLICES contrarian_only 12h


### RAW_SLICES contrarian_only 24h


# DEDUP_SLICES

## DEDUP_SLICES all 信号概览

- 总信号数：**34**
- Regime 分布：`{"mean_revert": 8, "trend": 26}`
- 仓位分布：`{"medium": 20, "small": 14}`
- 方向分布：`{"NO": 14, "YES": 20}`

## DEDUP_SLICES all 总体表现

### DEDUP_SLICES all 4h

- count: **34**
- hit_rate: **0.2941**
- avg_edge: **-0.000632**
- median_edge: **0.0**
- avg_roi: **-0.003195**
- median_roi: **0.0**
- max_consecutive_losses: **6**

### DEDUP_SLICES all 8h

- count: **34**
- hit_rate: **0.3235**
- avg_edge: **-0.000574**
- median_edge: **-0.0005**
- avg_roi: **-0.016755**
- median_roi: **-0.000519**
- max_consecutive_losses: **7**

### DEDUP_SLICES all 12h

- count: **34**
- hit_rate: **0.2647**
- avg_edge: **-0.000765**
- median_edge: **-0.0005**
- avg_roi: **-0.031904**
- median_roi: **-0.000764**
- max_consecutive_losses: **7**

### DEDUP_SLICES all 24h

- count: **34**
- hit_rate: **0.3235**
- avg_edge: **-0.00075**
- median_edge: **-0.0005**
- avg_roi: **-0.025713**
- median_roi: **-0.000774**
- max_consecutive_losses: **5**

## DEDUP_SLICES all 分 Regime 表现

### DEDUP_SLICES all 4h

- **mean_revert**: count=8, hit_rate=0.5, avg_roi=0.013975, max_consecutive_losses=4
- **trend**: count=26, hit_rate=0.2308, avg_roi=-0.008478, max_consecutive_losses=10

### DEDUP_SLICES all 8h

- **mean_revert**: count=8, hit_rate=0.75, avg_roi=0.012829, max_consecutive_losses=1
- **trend**: count=26, hit_rate=0.1923, avg_roi=-0.025858, max_consecutive_losses=10

### DEDUP_SLICES all 12h

- **mean_revert**: count=8, hit_rate=0.5, avg_roi=0.016905, max_consecutive_losses=1
- **trend**: count=26, hit_rate=0.1923, avg_roi=-0.046922, max_consecutive_losses=10

### DEDUP_SLICES all 24h

- **mean_revert**: count=8, hit_rate=0.5, avg_roi=0.026735, max_consecutive_losses=1
- **trend**: count=26, hit_rate=0.2692, avg_roi=-0.041852, max_consecutive_losses=7

## DEDUP_SLICES no_carry 信号概览

- 总信号数：**34**
- Regime 分布：`{"mean_revert": 8, "trend": 26}`
- 仓位分布：`{"medium": 20, "small": 14}`
- 方向分布：`{"NO": 14, "YES": 20}`

## DEDUP_SLICES no_carry 总体表现

### DEDUP_SLICES no_carry 4h

- count: **34**
- hit_rate: **0.2941**
- avg_edge: **-0.000632**
- median_edge: **0.0**
- avg_roi: **-0.003195**
- median_roi: **0.0**
- max_consecutive_losses: **6**

### DEDUP_SLICES no_carry 8h

- count: **34**
- hit_rate: **0.3235**
- avg_edge: **-0.000574**
- median_edge: **-0.0005**
- avg_roi: **-0.016755**
- median_roi: **-0.000519**
- max_consecutive_losses: **7**

### DEDUP_SLICES no_carry 12h

- count: **34**
- hit_rate: **0.2647**
- avg_edge: **-0.000765**
- median_edge: **-0.0005**
- avg_roi: **-0.031904**
- median_roi: **-0.000764**
- max_consecutive_losses: **7**

### DEDUP_SLICES no_carry 24h

- count: **34**
- hit_rate: **0.3235**
- avg_edge: **-0.00075**
- median_edge: **-0.0005**
- avg_roi: **-0.025713**
- median_roi: **-0.000774**
- max_consecutive_losses: **5**

## DEDUP_SLICES no_carry 分 Regime 表现

### DEDUP_SLICES no_carry 4h

- **mean_revert**: count=8, hit_rate=0.5, avg_roi=0.013975, max_consecutive_losses=4
- **trend**: count=26, hit_rate=0.2308, avg_roi=-0.008478, max_consecutive_losses=10

### DEDUP_SLICES no_carry 8h

- **mean_revert**: count=8, hit_rate=0.75, avg_roi=0.012829, max_consecutive_losses=1
- **trend**: count=26, hit_rate=0.1923, avg_roi=-0.025858, max_consecutive_losses=10

### DEDUP_SLICES no_carry 12h

- **mean_revert**: count=8, hit_rate=0.5, avg_roi=0.016905, max_consecutive_losses=1
- **trend**: count=26, hit_rate=0.1923, avg_roi=-0.046922, max_consecutive_losses=10

### DEDUP_SLICES no_carry 24h

- **mean_revert**: count=8, hit_rate=0.5, avg_roi=0.026735, max_consecutive_losses=1
- **trend**: count=26, hit_rate=0.2692, avg_roi=-0.041852, max_consecutive_losses=7

## DEDUP_SLICES mean_revert_only 信号概览

- 总信号数：**8**
- Regime 分布：`{"mean_revert": 8}`
- 仓位分布：`{"medium": 3, "small": 5}`
- 方向分布：`{"YES": 8}`

## DEDUP_SLICES mean_revert_only 总体表现

### DEDUP_SLICES mean_revert_only 4h

- count: **8**
- hit_rate: **0.5**
- avg_edge: **0.0005**
- median_edge: **0.0005**
- avg_roi: **0.013975**
- median_roi: **0.006211**
- max_consecutive_losses: **4**

### DEDUP_SLICES mean_revert_only 8h

- count: **8**
- hit_rate: **0.75**
- avg_edge: **0.0005**
- median_edge: **0.00075**
- avg_roi: **0.012829**
- median_roi: **0.017468**
- max_consecutive_losses: **1**

### DEDUP_SLICES mean_revert_only 12h

- count: **8**
- hit_rate: **0.5**
- avg_edge: **0.000875**
- median_edge: **0.0005**
- avg_roi: **0.016905**
- median_roi: **0.006211**
- max_consecutive_losses: **1**

### DEDUP_SLICES mean_revert_only 24h

- count: **8**
- hit_rate: **0.5**
- avg_edge: **0.001125**
- median_edge: **0.00025**
- avg_roi: **0.026735**
- median_roi: **0.001653**
- max_consecutive_losses: **1**

## DEDUP_SLICES mean_revert_only 分 Regime 表现

### DEDUP_SLICES mean_revert_only 4h

- **mean_revert**: count=8, hit_rate=0.5, avg_roi=0.013975, max_consecutive_losses=4

### DEDUP_SLICES mean_revert_only 8h

- **mean_revert**: count=8, hit_rate=0.75, avg_roi=0.012829, max_consecutive_losses=1

### DEDUP_SLICES mean_revert_only 12h

- **mean_revert**: count=8, hit_rate=0.5, avg_roi=0.016905, max_consecutive_losses=1

### DEDUP_SLICES mean_revert_only 24h

- **mean_revert**: count=8, hit_rate=0.5, avg_roi=0.026735, max_consecutive_losses=1

## DEDUP_SLICES trend_only 信号概览

- 总信号数：**26**
- Regime 分布：`{"trend": 26}`
- 仓位分布：`{"medium": 17, "small": 9}`
- 方向分布：`{"NO": 14, "YES": 12}`

## DEDUP_SLICES trend_only 总体表现

### DEDUP_SLICES trend_only 4h

- count: **26**
- hit_rate: **0.2308**
- avg_edge: **-0.000981**
- median_edge: **0.0**
- avg_roi: **-0.008478**
- median_roi: **0.0**
- max_consecutive_losses: **10**

### DEDUP_SLICES trend_only 8h

- count: **26**
- hit_rate: **0.1923**
- avg_edge: **-0.000904**
- median_edge: **-0.00075**
- avg_roi: **-0.025858**
- median_roi: **-0.001026**
- max_consecutive_losses: **10**

### DEDUP_SLICES trend_only 12h

- count: **26**
- hit_rate: **0.1923**
- avg_edge: **-0.001269**
- median_edge: **-0.001**
- avg_roi: **-0.046922**
- median_roi: **-0.001548**
- max_consecutive_losses: **10**

### DEDUP_SLICES trend_only 24h

- count: **26**
- hit_rate: **0.2692**
- avg_edge: **-0.001327**
- median_edge: **-0.00075**
- avg_roi: **-0.041852**
- median_roi: **-0.000774**
- max_consecutive_losses: **7**

## DEDUP_SLICES trend_only 分 Regime 表现

### DEDUP_SLICES trend_only 4h

- **trend**: count=26, hit_rate=0.2308, avg_roi=-0.008478, max_consecutive_losses=10

### DEDUP_SLICES trend_only 8h

- **trend**: count=26, hit_rate=0.1923, avg_roi=-0.025858, max_consecutive_losses=10

### DEDUP_SLICES trend_only 12h

- **trend**: count=26, hit_rate=0.1923, avg_roi=-0.046922, max_consecutive_losses=10

### DEDUP_SLICES trend_only 24h

- **trend**: count=26, hit_rate=0.2692, avg_roi=-0.041852, max_consecutive_losses=7

## DEDUP_SLICES contrarian_only 信号概览

- 总信号数：**0**
- Regime 分布：`{}`
- 仓位分布：`{}`
- 方向分布：`{}`

## DEDUP_SLICES contrarian_only 总体表现

### DEDUP_SLICES contrarian_only 4h

- count: **0**
- hit_rate: **None**
- avg_edge: **None**
- median_edge: **None**
- avg_roi: **None**
- median_roi: **None**
- max_consecutive_losses: **None**

### DEDUP_SLICES contrarian_only 8h

- count: **0**
- hit_rate: **None**
- avg_edge: **None**
- median_edge: **None**
- avg_roi: **None**
- median_roi: **None**
- max_consecutive_losses: **None**

### DEDUP_SLICES contrarian_only 12h

- count: **0**
- hit_rate: **None**
- avg_edge: **None**
- median_edge: **None**
- avg_roi: **None**
- median_roi: **None**
- max_consecutive_losses: **None**

### DEDUP_SLICES contrarian_only 24h

- count: **0**
- hit_rate: **None**
- avg_edge: **None**
- median_edge: **None**
- avg_roi: **None**
- median_roi: **None**
- max_consecutive_losses: **None**

## DEDUP_SLICES contrarian_only 分 Regime 表现

### DEDUP_SLICES contrarian_only 4h


### DEDUP_SLICES contrarian_only 8h


### DEDUP_SLICES contrarian_only 12h


### DEDUP_SLICES contrarian_only 24h


## Top Examples

- [trend] NO conf=0.688 best_roi=0.002538 | Will the Los Angeles Lakers win the 2026 NBA Finals? | 2026-04-15T19:15:00
- [trend] NO conf=0.688 best_roi=-0.002023 | Will the Los Angeles Kings win the 2026 NHL Stanley Cup? | 2026-04-15T20:15:00
- [trend] YES conf=0.688 best_roi=-0.157895 | Will the Minnesota Timberwolves win the 2026 NBA Finals? | 2026-04-15T18:30:00
- [trend] YES conf=0.688 best_roi=-0.25641 | Will the Philadelphia Flyers win the 2026 NHL Stanley Cup? | 2026-04-15T18:30:00
- [trend] YES conf=0.688 best_roi=-0.352941 | Will the Atlanta Hawks win the 2026 NBA Finals? | 2026-04-15T18:30:00
- [trend] YES conf=0.6649 best_roi=-0.1 | Will the Boston Bruins win the 2026 NHL Stanley Cup? | 2026-04-15T19:00:00
- [trend] YES conf=0.664 best_roi=0.333333 | Will the Charlotte Hornets win the 2026 NBA Finals? | 2026-04-15T18:30:00
- [trend] NO conf=0.664 best_roi=0.002044 | Will Ro Khanna win the 2028 Democratic presidential nomination? | 2026-04-15T19:15:00
- [trend] NO conf=0.664 best_roi=0.001505 | Will the Orlando Magic win the 2026 NBA Finals? | 2026-04-15T20:45:00
- [trend] NO conf=0.664 best_roi=-0.000507 | Will Ron DeSantis win the 2028 US Presidential Election? | 2026-04-15T20:15:00
