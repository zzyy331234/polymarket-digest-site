# MRAS-Lite v5 Best Combo Validation

生成时间：2026-04-17T20:18:31

## 固化参数

- params: `{"pct_low": 0.12, "rsi_low": 38, "chg24h_min": 0.05, "noise_max": 1.8, "min_strength": 3, "pct_high": 0.88, "rsi_high": 62}`
- raw_signals: **38**
- dedup_signals: **8**

## Fixed Params DEDUP Performance

- 4h: count=8, hit_rate=0.5, avg_roi=0.013378, median_roi=0.004311, max_consecutive_losses=3
- 8h: count=8, hit_rate=0.75, avg_roi=0.022955, median_roi=0.013083, max_consecutive_losses=2
- 12h: count=8, hit_rate=0.625, avg_roi=0.037027, median_roi=0.019142, max_consecutive_losses=2
- 24h: count=8, hit_rate=0.625, avg_roi=0.053942, median_roi=0.016733, max_consecutive_losses=2

## 样本审计（DEDUP）

- dem_nomination: count=3, 24h_avg_roi=-0.0121, 24h_hit_rate=0.6667
- nhl: count=3, 24h_avg_roi=0.086979, 24h_hit_rate=0.6667
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
- Will the Pittsburgh Penguins win the 2026 NHL Stanley Cup? | 2026-04-15T20:30:00 | 24h=-0.017544 | 12h=0.0 | 8h=0.017544
- Will USA win the 2026 FIFA World Cup? | 2026-04-15T18:30:00 | 24h=0.0 | 12h=0.0 | 8h=0.0
- Will Jon Ossoff win the 2028 Democratic presidential nomination? | 2026-04-15T19:45:00 | 24h=0.008621 | 12h=0.025862 | 8h=0.008621
- Will Alexandria Ocasio-Cortez win the 2028 Democratic presidential nomination? | 2026-04-15T19:15:00 | 24h=0.024845 | 12h=0.012422 | 8h=0.024845

## Walk-forward

- fold 1: train_best={"pct_low": 0.08, "rsi_low": 30, "chg24h_min": 0.03, "noise_max": 1.8, "min_strength": 2, "pct_high": 0.92, "rsi_high": 70} | selected_test_24h=0.031239 (6) | fixed_test_24h=0.050821 (5)
- fold 2: train_best={"pct_low": 0.1, "rsi_low": 30, "chg24h_min": 0.05, "noise_max": 1.8, "min_strength": 3, "pct_high": 0.9, "rsi_high": 70} | selected_test_24h=0.112871 (3) | fixed_test_24h=0.066646 (6)
- fold 3: train_best={"pct_low": 0.12, "rsi_low": 38, "chg24h_min": 0.05, "noise_max": 1.8, "min_strength": 3, "pct_high": 0.88, "rsi_high": 62} | selected_test_24h=0.067692 (5) | fixed_test_24h=0.067692 (5)

### Walk-forward Aggregate Test

- aggregate_selected_test:
  - 4h: count=14, hit_rate=0.5, avg_roi=0.008471
  - 8h: count=14, hit_rate=0.7857, avg_roi=0.028353
  - 12h: count=14, hit_rate=0.7143, avg_roi=0.030402
  - 24h: count=14, hit_rate=0.7143, avg_roi=0.061751
- aggregate_fixed_test:
  - 4h: count=16, hit_rate=0.5, avg_roi=0.008201
  - 8h: count=16, hit_rate=0.75, avg_roi=0.028052
  - 12h: count=16, hit_rate=0.75, avg_roi=0.03549
  - 24h: count=16, hit_rate=0.75, avg_roi=0.062028
