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

### 2. Will the Buffalo Sabres win the 2026 NHL Stanley Cup? [research] 
- 方向: NO | conf=0.66 | evidence=0.48
- regime/cluster: mean_revert / other
- thesis: [mean_revert] NO on 'Will the Buffalo Sabres win the 2026 NHL Stanley Cup?' because upper percentile fade setup.
- why_now: Short-term dislocation detected (1h=0.007, 4h=0.013, 24h=0.222).
- do_not_trade_if: Liquidity/exit quality deteriorates materially before action.

## 可直接关注的 Ready Alerts
- [research] Will the Anaheim Ducks win the 2026 NHL Stanley Cup? | YES | conf=0.69 | catalyst=price_dislocation
- [research] Will the Buffalo Sabres win the 2026 NHL Stanley Cup? | NO | conf=0.66 | catalyst=price_dislocation
- [watch] Will Kamala Harris win the 2028 US Presidential Election? | YES | conf=0.63 | catalyst=trend_follow
- [watch] Will Pete Buttigieg win the 2028 Democratic presidential nomination? | YES | conf=0.65 | catalyst=price_dislocation
- [do_not_touch] Will Jesus Christ return before GTA VI? | NO | conf=0.62 | catalyst=theme_cluster
- [do_not_touch] Will China invades Taiwan before GTA VI? | NO | conf=0.62 | catalyst=theme_cluster

## 观察名单
- Will Pete Buttigieg win the 2028 Democratic presidential nomination? | cluster=us_election | regime=trend | why=Short-term dislocation detected (1h=0.000, 4h=0.024, 24h=0.061).
- Will Josh Shapiro win the 2028 Democratic presidential nomination? | cluster=us_election | regime=mean_revert | why=Short-term dislocation detected (1h=0.000, 4h=0.000, 24h=0.055).
- Will Kamala Harris win the 2028 US Presidential Election? | cluster=us_election | regime=trend | why=Relevant within active cluster=us_election and current regime=trend.
- Will the Dallas Stars win the 2026 NHL Stanley Cup? | cluster=other | regime=trend | why=Short-term dislocation detected (1h=0.000, 4h=0.157, 24h=-0.195).
- Will Jesus Christ return before GTA VI? | cluster=gta_vi | regime=mean_revert | why=Relevant within active cluster=gta_vi and current regime=mean_revert.

## 今日避坑
- Will George Clooney win the 2028 Democratic presidential nomination? | cluster=us_election | regime=carry_no | blocking=low_tradability
- Will Andrew Yang win the 2028 Democratic presidential nomination? | cluster=us_election | regime=carry_no | blocking=low_tradability
- Will Alexandria Ocasio-Cortez win the 2028 US Presidential Election? | cluster=us_election | regime=mean_revert | blocking=high_noise
- Will the Colorado Avalanche win the 2026 NHL Stanley Cup? | cluster=other | regime=mean_revert | blocking=high_noise
- Will Panama win the 2026 FIFA World Cup? | cluster=world_cup | regime=carry_no | blocking=low_tradability, deep_tail_world_cup

## 后验复盘快照
- outcomes: {'flat': 179, 'pending': 7, 'miss': 6, 'hit': 8}
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