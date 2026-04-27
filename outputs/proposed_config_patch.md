# Proposed Config Patch

- 生成时间: 2026-04-27T17:01:29
- requires_manual_review: True
- change_count: 2

## Proposed Changes
- discipline_v2.buckets.high_confidence_min: 0.7 -> 0.72 | win_rate=0.00%, flat_rate=100.00%, pnl=0.0000
- discipline_v2.execution.overrides.observe_only_regimes: add carry_no | flat_rate=100.00%, pnl=0.0000, closed=7

## Proposed Config Excerpt
{
  "discipline_v2": {
    "version": "v2",
    "buckets": {
      "high_confidence_min": 0.72,
      "main_pool_min": 0.58,
      "research_min": 0.5
    },
    "execution": {
      "trade_buckets": [
        "high_confidence",
        "main_pool"
      ],
      "observe_only_buckets": [
        "research"
      ],
      "blocked_buckets": [
        "below_floor"
      ],
      "overrides": {
        "blocked_clusters": [
          "world_cup"
        ],
        "observe_only_clusters": [
          "us_election"
        ],
        "blocked_regimes": [
          "carry_no"
        ],
        "observe_only_regimes": [
          "carry_no"
        ]
      }
    },
    "release_gates": {
      "paper_to_micro_live": {
        "min_closed_trades": 30,
        "min_win_rate": 0.55,
        "min_avg_win_loss_ratio_like": 1.3,
        "max_consecutive_losses": 3,
        "max_flat_rate": 0.5
      }
    }
  }
}
