# Polymarket 日报 - 2026-04-30

## 今日结论
- 当前阶段：paper_trade / discipline v2
- Paper → Micro Live 放行：未达标，继续 paper
- 最新 paper：realized_trade_count=15 / win_rate=6.67% / flat_rate=60.00% / total_realized_pnl_like=-0.1477
- 最新 proposal：change_count=1 / requires_manual_review=True

## 当前配置与执行口径
- bucket_thresholds: {'high_confidence_min': 0.7, 'main_pool_min': 0.58, 'research_min': 0.5}
- trade_buckets: ['high_confidence', 'main_pool']
- observe_only_buckets: ['research']
- blocked_buckets: ['below_floor']
- overrides: {'blocked_clusters': ['world_cup'], 'observe_only_clusters': ['us_election'], 'blocked_regimes': ['carry_no'], 'observe_only_regimes': []}

## 最新周期
- ran_at: 2026-04-30T14:32:31
- ready_count: 6 / ready_buckets: {'main_pool': 4, 'high_confidence': 2}
- opened: 0 / opened_buckets: {}
- closed: 0 / skipped: 0 / skipped_buckets: {}
- skip_reasons: {}

## Paper 表现
- open_positions: 0 / closed_positions: 15
- open_policy_counts: {}
- closed_policy_counts: {'observe_only': 2, 'trade': 6, 'blocked': 7}

## Gate 检查（Paper → Micro Live）
- eligible: False
- actuals: {'closed_trades': 15, 'win_rate': 0.0667, 'avg_win_loss_ratio_like': 0.0503, 'recent_consecutive_losses': 0, 'flat_rate': 0.6}
- thresholds: {'min_closed_trades': 30, 'min_win_rate': 0.55, 'min_avg_win_loss_ratio_like': 1.3, 'max_consecutive_losses': 3, 'max_flat_rate': 0.5}

## Proposal
- generated_at: 2026-04-30T14:32:31
- change_count: 1
- requires_manual_review: True
- discipline_v2.buckets.high_confidence_min: 0.7 -> 0.72 | win_rate=0.00%, flat_rate=100.00%, pnl=0.0000

## Top Recommendations
- [high] bucket/high_confidence -> tighten_gate | win_rate=0.00%, flat_rate=100.00%, pnl=0.0000
- [high] cluster/world_cup -> block | flat_rate=100.00%, pnl=0.0000, closed=4
- [high] overall/paper_to_micro_live -> stay_paper | eligible=False, closed=15, win_rate=6.67%, flat_rate=60.00%
- [high] regime/carry_no -> observe_only | flat_rate=100.00%, pnl=0.0000, closed=7
- [low] bucket/main_pool -> keep | closed=8, win_rate=12.50%, flat_rate=25.00%, pnl=-0.1477

## 建议动作
- 继续保持 paper，不进入 micro live。
- 审核 proposed_config_patch，确认是否应用。
- 继续关注 high_confidence 桶是否还需要进一步收紧。
- 持续观察被 block / observe_only 的 cluster 与 regime 是否仍然合理。
