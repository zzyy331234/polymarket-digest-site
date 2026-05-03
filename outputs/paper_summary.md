# Paper Trade Summary

- 生成时间: 2026-05-03T13:36:14
- 纪律版本: vNext-mr-core
- 执行桶: trade=['main_pool'] observe_only=['high_confidence', 'research'] blocked=['below_floor']
- open / close / skip / halt: 15 / 15 / 545 / 311
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

## vNext Strategy Snapshot
- trade_regimes: ['mean_revert']
- observe_only_regimes: ['trend']
- blocked_regimes: ['carry_no', 'contrarian']
- blocked_clusters: ['world_cup', 'gta_vi', 'us_election']
- allowed_clusters: ['other']
- whitelist_keywords: ['nhl', 'stanley cup']
- observe_keywords: ['rookie of the year', 'nba rookie']
- blocklist_keywords: ['world cup', 'fifa', 'democratic presidential nomination', '2028 us presidential election', 'released before june 2026', 'gta vi']
- whitelist_hit_count: 132
- observe_hit_count: 3
- blocklist_hit_count: 328
- vnext_skip_count: 0

## Discipline v2 Gate (Paper → Micro Live)
- eligible: False
- closed_trades: 15 / >= 40
- win_rate: 6.67% / >= 58%
- avg_win_loss_ratio_like: 0.0503 / >= 1.5
- recent_consecutive_losses: 0 / <= 3
- flat_rate: 60.00% / <= 45%

## Execution Scope Split
- 当前 open positions by policy: {}
- 当前 closed positions by policy: {'blocked': 12, 'trade': 1, 'observe_only': 2}
- 历史 open events by policy: {'blocked': 12, 'trade': 1, 'observe_only': 2}
- 历史 skip events by policy: {'observe_only': 338, 'trade': 207}

## Auto Downgrade Suggestions
- [high] bucket/main_pool -> tighten_gate | win_rate=0.00%, flat_rate=70.00%, pnl=-0.0143
- [high] cluster/world_cup -> block | flat_rate=100.00%, pnl=0.0000, closed=4
- [high] overall/paper_to_micro_live -> stay_paper | eligible=False, closed=15, win_rate=6.67%, flat_rate=60.00%
- [high] regime/carry_no -> observe_only | flat_rate=100.00%, pnl=0.0000, closed=7
- [low] bucket/research -> keep | closed=5, win_rate=20.00%, flat_rate=40.00%, pnl=-0.1335
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

## vNext Skip Reasons
- 暂无 vNext 专属拦截

## v6 Whitelist / Blocklist Monitor
- whitelist_hit_count: 132
- observe_hit_count: 3
- blocklist_hit_count: 328
- whitelist_examples: ['Will the Ottawa Senators win the 2026 NHL Stanley Cup?', 'Will the Minnesota Wild win the 2026 NHL Stanley Cup?', 'Will the Carolina Hurricanes win the 2026 NHL Stanley Cup?', 'Will the Dallas Stars win the 2026 NHL Stanley Cup?', 'Will the Dallas Stars win the 2026 NHL Stanley Cup?']
- observe_examples: ['Will Cooper Flagg win the 2025–26 NBA Rookie of the Year award?', 'Will Cooper Flagg win the 2025–26 NBA Rookie of the Year award?', 'Will Cooper Flagg win the 2025–26 NBA Rookie of the Year award?']
- blocklist_examples: ['Will Alexandria Ocasio-Cortez win the 2028 US Presidential Election?', 'Will Panama win the 2026 FIFA World Cup?', 'Will Iraq win the 2026 FIFA World Cup?', 'Will Bernie Sanders win the 2028 Democratic presidential nomination?', 'Will Zohran Mamdani win the 2028 Democratic presidential nomination?']

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
- main_pool: closed=10 wins=0 flat=7 win_rate=0.00% flat_rate=70.00% pnl=-0.0143
- research: closed=5 wins=1 flat=2 win_rate=20.00% flat_rate=40.00% pnl=-0.1335

## By Execution Policy
- blocked: closed=12 wins=1 flat=9 win_rate=8.33% flat_rate=75.00% pnl=-0.0112
- trade: closed=1 wins=0 flat=0 win_rate=0.00% flat_rate=0.00% pnl=-0.0015
- observe_only: closed=2 wins=0 flat=0 win_rate=0.00% flat_rate=0.00% pnl=-0.1350
