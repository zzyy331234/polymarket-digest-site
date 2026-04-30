# Polymarket Intelligence Brief - 2026-04-30

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
- [do_not_touch] Putin out as President of Russia by December 31, 2026? | NO | conf=0.62 | catalyst=mean_reversion

## 观察名单
- Putin out as President of Russia by December 31, 2026? | cluster=other | regime=mean_revert | why=Relevant within active cluster=other and current regime=mean_revert.

## 今日避坑
- Will Uruguay win the 2026 FIFA World Cup? | cluster=world_cup | regime=carry_no | blocking=high_noise
- Will Colombia win the 2026 FIFA World Cup? | cluster=world_cup | regime=carry_no | blocking=high_noise
- Will Kim Kardashian win the 2028 Democratic presidential nomination? | cluster=us_election | regime=carry_no | blocking=high_noise
- Will Switzerland win the 2026 FIFA World Cup? | cluster=world_cup | regime=carry_no | blocking=high_noise
- Will Mexico win the 2026 FIFA World Cup? | cluster=world_cup | regime=carry_no | blocking=high_noise

## 后验复盘快照
- outcomes: {'pending': 17, 'flat': 116, 'hit': 23, 'miss': 44}
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