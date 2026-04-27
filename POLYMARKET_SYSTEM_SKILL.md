# Polymarket System Skill

## 目标
把当前 Polymarket 系统作为“自动 paper trading / 未来极小资金 live trial”的运营底座，形成稳定闭环：

collector -> MRAS v2 -> portfolio caps -> alert pipeline -> paper trader -> review pipeline -> readiness report

## 当前主文件

### 数据层
- `collector/collector.py`
- `collector/polymarket_data.db`
- `core/data_adapter.py`

### 策略层
- `core/mras_v2.py`
- `core/scoring.py`

### 组合与运营层
- `core/portfolio_manager.py`
- `core/ops_rules.py`
- `alert_pipeline.py`
- `review_pipeline.py`
- `readiness_report.py`

### 交易层
- `paper_trader.py`
- `risk_manager.py`
- `trading_config.json`
- `portfolio_state.json`
- `trade_log.jsonl`

### 运行入口
- `run_paper_cycle.sh`
- `status_overview.py`
- `daily_report.py`
- `refresh_scanner.sh`

### 看板
- `dashboard/pages/polymarket.py`
- `dashboard/pages/polymarket_ops.py`

## 关键设计

### 1. 风险语义拆分
不要再把所有风险标签都塞进同一个 `risk_flags` 逻辑里。

- `advisory_flags`: 提示类，如 `event_soon`
- `blocking_flags`: 真正阻断 alert / paper trader 的风险，如 `event_near`, `high_noise`, `trend_noisy`

页面、alert pipeline、paper trader 都应优先使用 `blocking_flags` 判定是否阻断。

### 2. v2 单一入口
Dashboard cache 里的 Polymarket 主入口已经统一到 v2：
- `scanner_signals_v2` 是主 key

不要再把旧 v1 scanner 当成运营主链，也不要继续维护兼容 alias。

### 3. review pipeline 语义
复盘系统已支持：
- `post_move_6h / 24h / 48h`
- `window_6h_ready / 24h_ready / 48h_ready`
- `mfe_6h / 24h / 48h`
- `mae_6h / 24h / 48h`
- `outcome`

只有窗口成熟 (`window_*_ready = true`) 时，才应用于较正式的 hit/miss 判断。

### 4. paper trader 控制层
`trading_config.json` 控制：
- `mode`
- `daily_budget_usd`
- `auto_trade_enabled`
- `live_trade_enabled`
- `emergency_stop`
- `max_daily_loss_like`
- `paper_review_only`
- `consecutive_fail_halt`

当前默认应保持：
- `mode = paper_trade`
- `live_trade_enabled = false`

### 5. readiness report
`readiness_report.py` 用于决定是否接近 live trial。
当前 status 若不是 `ready_for_tiny_live_trial`，就继续 paper-only。

## 日常运行

### 手动完整跑一轮
```bash
bash /Users/mac/.openclaw/workspace/polymarket/run_paper_cycle.sh
python3 /Users/mac/.openclaw/workspace/polymarket/status_overview.py
```

### 刷新看板 v2 cache
```bash
bash /Users/mac/.openclaw/workspace/polymarket/refresh_scanner.sh
```

## 当前原则
1. 先积累 paper 数据，不急着 live。
2. readiness / discipline gate 未达标前，不上真资金。
3. 优先做“更稳的运营闭环”，不是追求更多花哨信号。
4. 系统目标是：自动分析 + 自动 paper 交易 + 自动复盘 + 自动日报 + proposal / apply workflow。
