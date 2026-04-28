# Paper Trade Summary

- 生成时间: 2026-04-28T17:01:34
- 纪律版本: v2
- 执行桶: trade=['high_confidence', 'main_pool'] observe_only=['research'] blocked=['below_floor']
- open / close / skip / halt: 15 / 15 / 545 / 196
- 当前持仓: 0 open / 15 closed
- 实现交易数: 15
- 胜率: 6.67%
- flat rate: 60.00%
- 平均单笔 realized_pnl_like: -0.0098
- 平均盈利 / 平均亏损: 0.0015 / -0.0299
- 平均盈亏比 like: 0.0503
- total realized_pnl_like: -0.1477
- profit_factor_like: 0.0101
- 当前 halt: True (daily_loss_halt)

## Discipline v2 Gate (Paper → Micro Live)
- eligible: False
- closed_trades: 15 / >= 30
- win_rate: 6.67% / >= 55%
- avg_win_loss_ratio_like: 0.0503 / >= 1.3
- recent_consecutive_losses: 0 / <= 3
- flat_rate: 60.00% / <= 50%

## Execution Scope Split
- 当前 open positions by policy: {}
- 当前 closed positions by policy: {'observe_only': 2, 'trade': 6, 'blocked': 7}
- 历史 open events by policy: {'observe_only': 2, 'trade': 6, 'blocked': 7}
- 历史 skip events by policy: {'blocked': 164, 'trade': 207, 'observe_only': 174}

## Auto Downgrade Suggestions
- [high] bucket/high_confidence -> tighten_gate | win_rate=0.00%, flat_rate=100.00%, pnl=0.0000
- [high] cluster/world_cup -> block | flat_rate=100.00%, pnl=0.0000, closed=4
- [high] overall/paper_to_micro_live -> stay_paper | eligible=False, closed=15, win_rate=6.67%, flat_rate=60.00%
- [high] regime/carry_no -> observe_only | flat_rate=100.00%, pnl=0.0000, closed=7
- [low] bucket/main_pool -> keep | closed=8, win_rate=12.50%, flat_rate=25.00%, pnl=-0.1477
- [low] cluster/gta_vi -> monitor | 样本不足: closed=2 < 3
- [low] cluster/other -> keep | closed=4, win_rate=0.00%, flat_rate=0.00%, pnl=-0.1447
- [low] cluster/us_election -> keep | closed=5, win_rate=20.00%, flat_rate=60.00%, pnl=-0.0030
- [low] regime/mean_revert -> keep | closed=6, win_rate=16.67%, flat_rate=33.33%, pnl=-0.1350
- [low] regime/trend -> monitor | 样本不足: closed=2 < 3

## Close Reasons
- thesis_invalidated: 2
- time_stop_24h: 6
- deep_tail_world_cup_exit: 2
- stale_carry_no_exit: 2
- low_tradability_exit: 1
- stop_loss: 2

## Skip Reasons
- risk flags present: 9
- confidence too low: 4
- total exposure limit reached: 140
- cluster exposure limit for world_cup: 1
- max positions reached: 38
- cluster exposure limit for us_election: 2
- daily trade limit reached: 64
- daily budget reached: 8
- cluster exposure limit for other: 101
- bucket=main_pool policy=observe_only: 174
- cooldown after consecutive losses: 4

## By Regime
- trend: closed=2 wins=0 win_rate=0.00% pnl=-0.0127
- carry_no: closed=7 wins=0 win_rate=0.00% pnl=0.0000
- mean_revert: closed=6 wins=1 win_rate=16.67% pnl=-0.1350

## By Cluster
- other: closed=4 wins=0 flat=0 win_rate=0.00% flat_rate=0.00% pnl=-0.1447
- world_cup: closed=4 wins=0 flat=4 win_rate=0.00% flat_rate=100.00% pnl=0.0000
- us_election: closed=5 wins=1 flat=3 win_rate=20.00% flat_rate=60.00% pnl=-0.0030
- gta_vi: closed=2 wins=0 flat=2 win_rate=0.00% flat_rate=100.00% pnl=0.0000

## By Bucket
- main_pool: closed=8 wins=1 flat=2 win_rate=12.50% flat_rate=25.00% pnl=-0.1477
- high_confidence: closed=7 wins=0 flat=7 win_rate=0.00% flat_rate=100.00% pnl=0.0000

## By Execution Policy
- trade: closed=6 wins=0 flat=2 win_rate=0.00% flat_rate=33.33% pnl=-0.1447
- blocked: closed=7 wins=0 flat=7 win_rate=0.00% flat_rate=100.00% pnl=0.0000
- observe_only: closed=2 wins=1 flat=0 win_rate=50.00% flat_rate=0.00% pnl=-0.0030
