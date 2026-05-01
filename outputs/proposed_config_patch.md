# Proposed Config Patch

- 生成时间: 2026-05-01T20:32:31
- requires_manual_review: True
- change_count: 0

## Proposed Changes
- 当前没有新的配置补丁建议

## Proposed Config Excerpt
{
  "discipline_v2": {
    "version": "vNext-mr-core",
    "buckets": {
      "high_confidence_min": 0.74,
      "main_pool_min": 0.64,
      "research_min": 0.56
    },
    "execution": {
      "trade_buckets": [
        "main_pool"
      ],
      "observe_only_buckets": [
        "high_confidence",
        "research"
      ],
      "blocked_buckets": [
        "below_floor"
      ],
      "overrides": {
        "blocked_clusters": [
          "gta_vi",
          "world_cup"
        ],
        "observe_only_clusters": [
          "us_election"
        ],
        "blocked_regimes": [
          "carry_no",
          "contrarian",
          "trend"
        ],
        "observe_only_regimes": []
      }
    },
    "release_gates": {
      "paper_to_micro_live": {
        "min_closed_trades": 40,
        "min_win_rate": 0.58,
        "min_avg_win_loss_ratio_like": 1.5,
        "max_consecutive_losses": 3,
        "max_flat_rate": 0.45
      }
    }
  }
}
