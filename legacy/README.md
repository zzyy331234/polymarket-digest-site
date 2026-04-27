# Polymarket Legacy

这些文件来自旧的 Polymarket 运行链路，已于 2026-04-19 进入**安全退役**状态。

## 已退役内容

- `polymarket_forecast.py`
- `run_forecast.sh`
- `run_forecast_v2.sh`
- `run_trading_cycle.sh`

## 为什么没有直接删除

因为这些文件曾经是主链入口，先迁入 `legacy/` 比直接删除更安全，便于：

- 回溯旧逻辑
- 对照历史输出
- 临时排查兼容问题
- 确认新 paper 闭环稳定后再做最终清理

## 当前主链

现在应使用的新链路：

- `run_paper_cycle.sh`
- `paper_trader.py`
- `paper_report.py`
- `daily_report.py`
- `status_overview.py`
- `apply_config_patch.py`

## 退役动作

2026-04-19 已完成：

1. 备份原 `crontab`
2. 移除老定时入口：
   - `run_forecast.sh`
   - `run_trading_cycle.sh`
3. 保留：
   - `refresh_scanner.sh`
   - `launchd` 的 `com.polymarket.paper-cycle`
4. 手动验证新链路仍可正常运行

## 说明

如果后续连续观察无问题，可考虑最终删除本目录中的旧文件。
