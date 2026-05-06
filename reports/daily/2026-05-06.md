# Polymarket 日报 - 2026-05-06

## 今日结论
- 当前阶段：paper_trade / discipline vNext-mr-core
- Paper → Micro Live 放行：未达标，继续 paper
- 最新 paper：realized_trade_count=15 / win_rate=6.67% / flat_rate=60.00% / total_realized_pnl_like=-0.1477
- 最新 proposal：change_count=0 / requires_manual_review=True

## 当前配置与执行口径
- bucket_thresholds: {'high_confidence_min': 0.74, 'main_pool_min': 0.64, 'research_min': 0.56}
- trade_buckets: ['main_pool']
- observe_only_buckets: ['high_confidence', 'research']
- blocked_buckets: ['below_floor']
- overrides: {'blocked_clusters': ['world_cup', 'gta_vi'], 'observe_only_clusters': ['us_election'], 'blocked_regimes': ['carry_no', 'trend', 'contrarian'], 'observe_only_regimes': []}

## 最新周期
- ran_at: 2026-05-06T17:02:40
- ready_count: 4 / ready_buckets: {'main_pool': 4}
- opened: 0 / opened_buckets: {}
- closed: 0 / skipped: 0 / skipped_buckets: {}
- skip_reasons: {}

## Paper 表现
- open_positions: 0 / closed_positions: 15
- open_policy_counts: {}
- closed_policy_counts: {'blocked': 12, 'trade': 1, 'observe_only': 2}

## Gate 检查（Paper → Micro Live）
- eligible: False
- actuals: {'closed_trades': 15, 'win_rate': 0.0667, 'avg_win_loss_ratio_like': 0.0503, 'recent_consecutive_losses': 0, 'flat_rate': 0.6}
- thresholds: {'min_closed_trades': 40, 'min_win_rate': 0.58, 'min_avg_win_loss_ratio_like': 1.5, 'max_consecutive_losses': 3, 'max_flat_rate': 0.45}

## Proposal
- generated_at: 2026-05-06T17:02:40
- change_count: 0
- requires_manual_review: True
- 今日无新的 proposal 变更

## Top Recommendations
- [high] bucket/main_pool -> tighten_gate | win_rate=0.00%, flat_rate=70.00%, pnl=-0.0143
- [high] cluster/world_cup -> block | flat_rate=100.00%, pnl=0.0000, closed=4
- [high] overall/paper_to_micro_live -> stay_paper | eligible=False, closed=15, win_rate=6.67%, flat_rate=60.00%
- [high] regime/carry_no -> observe_only | flat_rate=100.00%, pnl=0.0000, closed=7
- [low] bucket/research -> keep | closed=5, win_rate=20.00%, flat_rate=40.00%, pnl=-0.1335

## 建议动作
- 继续保持 paper，不进入 micro live。
- 继续关注 high_confidence 桶是否还需要进一步收紧。
- 持续观察被 block / observe_only 的 cluster 与 regime 是否仍然合理。
