# MRAS-Lite v4 Mean Revert 参数扫描

生成时间：2026-04-17T20:07:38

## 配置

- db_path: `/Users/mac/.openclaw/workspace/polymarket/collector/polymarket_data.db`
- min_liquidity: `20000`
- min_samples_per_bar: `10`
- min_quality_ratio: `0.7`
- recent_pct_bars: `96`
- cooldown_hours: `12.0`
- max_markets: `0`
- grid_size: `216`
- strategy_focus: `mean_revert_parameter_scan`

## 数据质量

- markets_scanned: **195**
- markets_with_bars: **195**
- candidate_markets: **185**
- segments_total: **2608**
- segments_ge_24h: **185**
- bars_total: **53944**
- candidates_total: **1850**

## Best Combo

- params: `{"pct_low": 0.12, "rsi_low": 38, "chg24h_min": 0.05, "noise_max": 1.8, "min_strength": 3, "pct_high": 0.88, "rsi_high": 62}`
- score: **0.086442**
- raw_signals: **38**
- dedup_signals: **8**

### Best Combo DEDUP Performance

- 4h: count=8, hit_rate=0.5, avg_roi=0.013378, median_roi=0.004311, max_consecutive_losses=3
- 8h: count=8, hit_rate=0.75, avg_roi=0.022955, median_roi=0.013083, max_consecutive_losses=2
- 12h: count=8, hit_rate=0.625, avg_roi=0.037027, median_roi=0.019142, max_consecutive_losses=2
- 24h: count=8, hit_rate=0.625, avg_roi=0.053942, median_roi=0.016733, max_consecutive_losses=2

## Top 10 Combos

1. score=0.086442 | params={"pct_low": 0.12, "rsi_low": 38, "chg24h_min": 0.05, "noise_max": 1.8, "min_strength": 3, "pct_high": 0.88, "rsi_high": 62} | dedup=8 | 8h=0.022955 | 12h=0.037027 | 24h=0.053942
2. score=0.074632 | params={"pct_low": 0.12, "rsi_low": 30, "chg24h_min": 0.03, "noise_max": 1.8, "min_strength": 3, "pct_high": 0.88, "rsi_high": 70} | dedup=8 | 8h=0.025211 | 12h=0.033795 | 24h=0.044531
3. score=0.074402 | params={"pct_low": 0.12, "rsi_low": 38, "chg24h_min": 0.05, "noise_max": 2.2, "min_strength": 3, "pct_high": 0.88, "rsi_high": 62} | dedup=9 | 8h=0.018839 | 12h=0.029783 | 24h=0.046383
4. score=0.07425 | params={"pct_low": 0.1, "rsi_low": 30, "chg24h_min": 0.05, "noise_max": 1.8, "min_strength": 3, "pct_high": 0.9, "rsi_high": 70} | dedup=5 | 8h=0.011022 | 12h=0.025725 | 24h=0.058957
5. score=0.07425 | params={"pct_low": 0.1, "rsi_low": 30, "chg24h_min": 0.05, "noise_max": 2.2, "min_strength": 3, "pct_high": 0.9, "rsi_high": 70} | dedup=5 | 8h=0.011022 | 12h=0.025725 | 24h=0.058957
6. score=0.07425 | params={"pct_low": 0.12, "rsi_low": 30, "chg24h_min": 0.05, "noise_max": 1.8, "min_strength": 3, "pct_high": 0.88, "rsi_high": 70} | dedup=5 | 8h=0.011022 | 12h=0.025725 | 24h=0.058957
7. score=0.07425 | params={"pct_low": 0.12, "rsi_low": 30, "chg24h_min": 0.05, "noise_max": 2.2, "min_strength": 3, "pct_high": 0.88, "rsi_high": 70} | dedup=5 | 8h=0.011022 | 12h=0.025725 | 24h=0.058957
8. score=0.073934 | params={"pct_low": 0.12, "rsi_low": 33, "chg24h_min": 0.03, "noise_max": 1.8, "min_strength": 3, "pct_high": 0.88, "rsi_high": 67} | dedup=9 | 8h=0.024342 | 12h=0.033905 | 24h=0.041515
9. score=0.069367 | params={"pct_low": 0.08, "rsi_low": 33, "chg24h_min": 0.05, "noise_max": 1.8, "min_strength": 3, "pct_high": 0.92, "rsi_high": 67} | dedup=6 | 8h=0.015008 | 12h=0.027235 | 24h=0.049106
10. score=0.069367 | params={"pct_low": 0.08, "rsi_low": 33, "chg24h_min": 0.05, "noise_max": 2.2, "min_strength": 3, "pct_high": 0.92, "rsi_high": 67} | dedup=6 | 8h=0.015008 | 12h=0.027235 | 24h=0.049106
