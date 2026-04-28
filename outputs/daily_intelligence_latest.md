# Polymarket Intelligence Brief - 2026-04-28

## 今日结论
- 阶段: paper_trade
- 核心判断: 继续 paper-only，优先做情报筛选和噪音剔除。
- paper gate eligible=False
- win_rate=0.0667
- flat_rate=0.6
- realized_pnl_like=-0.14775

## 今日优先候选
### 1. Will Cooper Flagg win the 2025–26 NBA Rookie of the Year award? [research] 
- 方向: YES | conf=0.69 | evidence=0.53
- regime/cluster: trend / other
- thesis: [trend] YES on 'Will Cooper Flagg win the 2025–26 NBA Rookie of the Year award?' because 4h move visible.
- why_now: Short-term dislocation detected (1h=0.000, 4h=0.237, 24h=0.251).
- do_not_trade_if: Liquidity/exit quality deteriorates materially before action.

## 可直接关注的 Ready Alerts
- [research] Will Cooper Flagg win the 2025–26 NBA Rookie of the Year award? | YES | conf=0.69 | catalyst=price_dislocation
- [watch] Will Alexandria Ocasio-Cortez win the 2028 US Presidential Election? | YES | conf=0.68 | catalyst=price_dislocation
- [watch] Will Kamala Harris win the 2028 US Presidential Election? | YES | conf=0.69 | catalyst=price_dislocation
- [do_not_touch] Will the Dallas Stars win the 2026 NHL Stanley Cup? | YES | conf=0.63 | catalyst=price_dislocation
- [do_not_touch] Will Jesus Christ return before GTA VI? | NO | conf=0.62 | catalyst=theme_cluster
- [do_not_touch] Russia-Ukraine Ceasefire before GTA VI? | NO | conf=0.62 | catalyst=theme_cluster

## 观察名单
- Will Kamala Harris win the 2028 US Presidential Election? | cluster=us_election | regime=trend | why=Short-term dislocation detected (1h=0.000, 4h=0.089, 24h=0.126).
- Will Alexandria Ocasio-Cortez win the 2028 US Presidential Election? | cluster=us_election | regime=trend | why=Short-term dislocation detected (1h=0.015, 4h=0.172, 24h=0.088).
- Will Jon Ossoff win the 2028 Democratic presidential nomination? | cluster=us_election | regime=trend | why=Short-term dislocation detected (1h=0.000, 4h=0.064, 24h=0.084).
- Will Gavin Newsom win the 2028 Democratic presidential nomination? | cluster=us_election | regime=mean_revert | why=Short-term dislocation detected (1h=0.004, 4h=0.019, 24h=0.051).
- Will the Dallas Stars win the 2026 NHL Stanley Cup? | cluster=other | regime=trend | why=Short-term dislocation detected (1h=0.045, 4h=0.106, 24h=0.307).

## 今日避坑
- Will George Clooney win the 2028 Democratic presidential nomination? | cluster=us_election | regime=carry_no | blocking=low_tradability
- Will Andrew Yang win the 2028 Democratic presidential nomination? | cluster=us_election | regime=carry_no | blocking=low_tradability
- Will the Colorado Avalanche win the 2026 NHL Stanley Cup? | cluster=other | regime=mean_revert | blocking=high_noise
- Xi Jinping out before 2027? | cluster=other | regime=mean_revert | blocking=high_noise
- Will bitcoin hit $1m before GTA VI? | cluster=gta_vi | regime=mean_revert | blocking=high_noise

## 后验复盘快照
- outcomes: {'flat': 175, 'miss': 7, 'pending': 7, 'hit': 11}
- paper_summary: {'realized_trade_count': 15, 'win_rate': 0.0667, 'flat_rate': 0.6, 'total_realized_pnl_like': -0.14775}

## Regime Snapshot
- trend: closed=2 win_rate=0.0 flat_rate=0.0 pnl=-0.01275
- carry_no: closed=7 win_rate=0.0 flat_rate=1.0 pnl=0.0
- mean_revert: closed=6 win_rate=0.1667 flat_rate=0.3333 pnl=-0.135

## Cluster Snapshot
- other: closed=4 win_rate=0.0 flat_rate=0.0 pnl=-0.14475
- world_cup: closed=4 win_rate=0.0 flat_rate=1.0 pnl=0.0
- us_election: closed=5 win_rate=0.2 flat_rate=0.6 pnl=-0.003
- gta_vi: closed=2 win_rate=0.0 flat_rate=1.0 pnl=0.0

## 建议动作
- 继续保持 paper-only，不推进 micro live。
- 优先减少 flat-heavy cluster/regime 的注意力占用。
- 只把 candidate/research 级别信号用于主观察池。