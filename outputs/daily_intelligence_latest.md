# Polymarket Intelligence Brief - 2026-04-27

## 今日结论
- 阶段: paper_trade
- 核心判断: 继续 paper-only，优先做情报筛选和噪音剔除。
- paper gate eligible=False
- win_rate=0.0667
- flat_rate=0.6
- realized_pnl_like=-0.14775

## 今日优先候选
### 1. Will the Anaheim Ducks win the 2026 NHL Stanley Cup? [research] 
- 方向: YES | conf=0.69 | evidence=0.53
- regime/cluster: trend / other
- thesis: [trend] YES on 'Will the Anaheim Ducks win the 2026 NHL Stanley Cup?' because 4h move visible.
- why_now: Short-term dislocation detected (1h=0.000, 4h=0.080, 24h=0.500).
- do_not_trade_if: Liquidity/exit quality deteriorates materially before action.

### 2. New Rihanna Album before GTA VI? [research] 
- 方向: YES | conf=0.66 | evidence=0.48
- regime/cluster: mean_revert / gta_vi
- thesis: [mean_revert] YES on 'New Rihanna Album before GTA VI?' because lower percentile bounce setup.
- why_now: Relevant within active cluster=gta_vi and current regime=mean_revert.
- do_not_trade_if: GTA VI themed cluster remains flat-heavy and should stay observational unless new catalyst appears.; Liquidity/exit quality deteriorates materially before action.

### 3. New Playboi Carti Album before GTA VI? [research] 
- 方向: NO | conf=0.66 | evidence=0.48
- regime/cluster: mean_revert / gta_vi
- thesis: [mean_revert] NO on 'New Playboi Carti Album before GTA VI?' because upper percentile fade setup.
- why_now: Relevant within active cluster=gta_vi and current regime=mean_revert.
- do_not_trade_if: GTA VI themed cluster remains flat-heavy and should stay observational unless new catalyst appears.; Liquidity/exit quality deteriorates materially before action.

## 可直接关注的 Ready Alerts
- [research] Will the Anaheim Ducks win the 2026 NHL Stanley Cup? | YES | conf=0.69 | catalyst=price_dislocation
- [research] New Rihanna Album before GTA VI? | YES | conf=0.66 | catalyst=theme_cluster
- [research] New Playboi Carti Album before GTA VI? | NO | conf=0.66 | catalyst=theme_cluster
- [watch] Will Josh Shapiro win the 2028 Democratic presidential nomination? | NO | conf=0.66 | catalyst=price_dislocation
- [watch] Will JD Vance win the 2028 US Presidential Election? | NO | conf=0.62 | catalyst=mean_reversion
- [do_not_touch] Will the Dallas Stars win the 2026 NHL Stanley Cup? | NO | conf=0.63 | catalyst=price_dislocation

## 观察名单
- Will Josh Shapiro win the 2028 Democratic presidential nomination? | cluster=us_election | regime=mean_revert | why=Short-term dislocation detected (1h=0.000, 4h=0.000, 24h=0.055).
- Will the Dallas Stars win the 2026 NHL Stanley Cup? | cluster=other | regime=trend | why=Short-term dislocation detected (1h=0.073, 4h=0.157, 24h=-0.195).
- Will Jesus Christ return before GTA VI? | cluster=gta_vi | regime=mean_revert | why=Relevant within active cluster=gta_vi and current regime=mean_revert.
- Will JD Vance win the 2028 US Presidential Election? | cluster=us_election | regime=mean_revert | why=Relevant within active cluster=us_election and current regime=mean_revert.
- Will the Oklahoma City Thunder win the 2026 NBA Finals? | cluster=other | regime=mean_revert | why=Relevant within active cluster=other and current regime=mean_revert.

## 今日避坑
- Will George Clooney win the 2028 Democratic presidential nomination? | cluster=us_election | regime=carry_no | blocking=low_tradability
- Will Andrew Yang win the 2028 Democratic presidential nomination? | cluster=us_election | regime=carry_no | blocking=low_tradability
- Will Alexandria Ocasio-Cortez win the 2028 US Presidential Election? | cluster=us_election | regime=mean_revert | blocking=high_noise
- Will the Colorado Avalanche win the 2026 NHL Stanley Cup? | cluster=other | regime=mean_revert | blocking=high_noise
- Will the Buffalo Sabres win the 2026 NHL Stanley Cup? | cluster=other | regime=mean_revert | blocking=high_noise

## 后验复盘快照
- outcomes: {'flat': 175, 'miss': 9, 'hit': 9, 'pending': 7}
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