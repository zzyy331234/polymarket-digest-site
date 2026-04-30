# MRAS-Lite v5 Best Combo Validation

生成时间：2026-04-30T19:13:32

## 固化参数

- params: `{"pct_low": 0.12, "rsi_low": 38, "chg24h_min": 0.05, "noise_max": 1.8, "min_strength": 3, "pct_high": 0.88, "rsi_high": 62}`
- raw_signals: **56**
- dedup_signals: **10**

## Fixed Params DEDUP Performance

- 4h: count=10, hit_rate=0.4, avg_roi=0.0012, median_roi=0.0, max_consecutive_losses=5
- 8h: count=10, hit_rate=0.8, avg_roi=0.052699, median_roi=0.021194, max_consecutive_losses=2
- 12h: count=10, hit_rate=0.5, avg_roi=0.016968, median_roi=0.006211, max_consecutive_losses=4
- 24h: count=10, hit_rate=0.5, avg_roi=0.038061, median_roi=0.004311, max_consecutive_losses=4

## 样本审计（DEDUP）

- dem_nomination: count=3, 24h_avg_roi=-0.0121, 24h_hit_rate=0.6667
- nhl: count=3, 24h_avg_roi=0.086979, 24h_hit_rate=0.6667
- other: count=2, 24h_avg_roi=-0.025459, 24h_hit_rate=0.0
- us_election: count=1, 24h_avg_roi=0.206897, 24h_hit_rate=1.0
- world_cup: count=1, 24h_avg_roi=0.0, 24h_hit_rate=0.0

### Top 24h Cases

- Will Tucker Carlson win the 2028 US Presidential Election? | 2026-04-15T19:15:00 | 24h=0.206897 | 12h=0.068966 | 8h=0.068966
- Will the Tampa Bay Lightning win the 2026 NHL Stanley Cup? | 2026-04-15T19:45:00 | 24h=0.145669 | 12h=0.141732 | 8h=0.102362
- Will the Vegas Golden Knights win the 2026 NHL Stanley Cup? | 2026-04-15T18:30:00 | 24h=0.132812 | 12h=0.09375 | 8h=0.007813
- Will Alexandria Ocasio-Cortez win the 2028 Democratic presidential nomination? | 2026-04-15T19:15:00 | 24h=0.024845 | 12h=0.012422 | 8h=0.024845
- Will Jon Ossoff win the 2028 Democratic presidential nomination? | 2026-04-15T19:45:00 | 24h=0.008621 | 12h=0.025862 | 8h=0.008621

### Bottom 24h Cases

- Will Ro Khanna win the 2028 Democratic presidential nomination? | 2026-04-15T18:30:00 | 24h=-0.069767 | 12h=-0.046512 | 8h=-0.046512
- Will Cooper Flagg win the 2025–26 NBA Rookie of the Year award? | 2026-04-15T18:30:00 | 24h=-0.048368 | 12h=-0.088271 | 8h=0.158404
- Will the Pittsburgh Penguins win the 2026 NHL Stanley Cup? | 2026-04-15T20:30:00 | 24h=-0.017544 | 12h=0.0 | 8h=0.017544
- Will Kon Knueppel win the 2025–26 NBA Rookie of the Year award? | 2026-04-15T18:30:00 | 24h=-0.002551 | 12h=-0.038265 | 8h=0.184949
- Will USA win the 2026 FIFA World Cup? | 2026-04-15T18:30:00 | 24h=0.0 | 12h=0.0 | 8h=0.0

## Walk-forward

- fold 1: train_best={"pct_low": 0.1, "rsi_low": 30, "chg24h_min": 0.03, "noise_max": 1.8, "min_strength": 3, "pct_high": 0.9, "rsi_high": 70} | selected_test_24h=0.014231 (7) | fixed_test_24h=0.023754 (7)
- fold 2: train_best={"pct_low": 0.08, "rsi_low": 30, "chg24h_min": 0.05, "noise_max": 1.8, "min_strength": 3, "pct_high": 0.92, "rsi_high": 70} | selected_test_24h=0.0609 (4) | fixed_test_24h=0.030552 (8)
- fold 3: train_best={"pct_low": 0.12, "rsi_low": 38, "chg24h_min": 0.05, "noise_max": 1.8, "min_strength": 3, "pct_high": 0.88, "rsi_high": 62} | selected_test_24h=0.02755 (7) | fixed_test_24h=0.02755 (7)

### Walk-forward Aggregate Test

- aggregate_selected_test:
  - 4h: count=18, hit_rate=0.4444, avg_roi=-6.8e-05
  - 8h: count=18, hit_rate=0.8889, avg_roi=0.061811
  - 12h: count=18, hit_rate=0.5556, avg_roi=-0.015409
  - 24h: count=18, hit_rate=0.5556, avg_roi=0.029781
- aggregate_fixed_test:
  - 4h: count=22, hit_rate=0.4545, avg_roi=0.001114
  - 8h: count=22, hit_rate=0.8182, avg_roi=0.059161
  - 12h: count=22, hit_rate=0.5455, avg_roi=-0.014946
  - 24h: count=22, hit_rate=0.5455, avg_roi=0.027434
