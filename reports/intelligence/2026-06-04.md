# Polymarket Intelligence Brief - 2026-06-04

## 今日结论
- 阶段: paper_trade
- 核心判断: 继续 paper-only，优先做情报筛选和噪音剔除。
- paper gate eligible=False
- win_rate=0.0667
- flat_rate=0.6
- realized_pnl_like=-0.14775

## 今日优先候选
### 1. Will the Carolina Hurricanes win the 2026 NHL Stanley Cup? [research] 
- 方向: YES | conf=0.66 | evidence=0.48
- regime/cluster: mean_revert / other
- thesis: [mean_revert] YES on 'Will the Carolina Hurricanes win the 2026 NHL Stanley Cup?' because lower percentile bounce setup.
- why_now: Short-term dislocation detected (1h=0.000, 4h=0.000, 24h=-0.308).
- do_not_trade_if: Liquidity/exit quality deteriorates materially before action.

## 可直接关注的 Ready Alerts
- [research] Will the Carolina Hurricanes win the 2026 NHL Stanley Cup? | YES | conf=0.66 | catalyst=price_dislocation
- [do_not_touch] Will Eric Trump win the 2028 US Presidential Election? | NO | conf=0.71 | catalyst=structural
- [do_not_touch] Will Cooper Flagg win the 2025–26 NBA Rookie of the Year award? | YES | conf=0.69 | catalyst=price_dislocation
- [do_not_touch] Will Ron DeSantis win the 2028 US Presidential Election? | YES | conf=0.69 | catalyst=price_dislocation

## 观察名单
- Will the Vegas Golden Knights win the 2026 NHL Stanley Cup? | cluster=other | regime=mean_revert | why=Short-term dislocation detected (1h=0.001, 4h=0.001, 24h=0.411).

## 今日避坑
- Will Eric Trump win the 2028 US Presidential Election? | cluster=us_election | regime=carry_no | blocking=
- Will Oprah Winfrey win the 2028 Democratic presidential nomination? | cluster=us_election | regime=carry_no | blocking=
- Will Cooper Flagg win the 2025–26 NBA Rookie of the Year award? | cluster=other | regime=trend | blocking=
- Will Ron DeSantis win the 2028 US Presidential Election? | cluster=us_election | regime=trend | blocking=
- Will Iraq win the 2026 FIFA World Cup? | cluster=world_cup | regime=carry_no | blocking=deep_tail_world_cup

## 后验复盘快照
- outcomes: {'flat': 146, 'miss': 8, 'hit': 6, 'pending': 40}
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