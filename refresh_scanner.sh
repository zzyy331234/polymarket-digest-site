#!/bin/bash
# 单独刷新 Polymarket v2 信号，不动 A股数据
python3 - <<'PY'
import sys
sys.path.insert(0, '/Users/mac/.openclaw/workspace/dashboard')
from data.fetcher import _load_cache, _save_cache, load_polymarket_v2_signals
from datetime import datetime, timezone

cache = _load_cache()
poly_scanner_v2 = load_polymarket_v2_signals()
cache.setdefault('polymarket', {})
cache['polymarket'].pop('scanner_signals', None)
cache['polymarket']['scanner_signals_v2'] = poly_scanner_v2
cache['updated'] = datetime.now(timezone.utc).isoformat()
_save_cache(cache)

yes_c = sum(1 for s in poly_scanner_v2 if s.get('direction') == 'YES')
no_c = sum(1 for s in poly_scanner_v2 if s.get('direction') == 'NO')
trend_c = sum(1 for s in poly_scanner_v2 if s.get('regime') == 'trend')
mr_c = sum(1 for s in poly_scanner_v2 if s.get('regime') == 'mean_revert')
con_c = sum(1 for s in poly_scanner_v2 if s.get('regime') == 'contrarian')
carry_c = sum(1 for s in poly_scanner_v2 if s.get('regime') == 'carry_no')
print(f"[{datetime.now().strftime('%H:%M:%S')}] Polymarket v2 scanner: {len(poly_scanner_v2)} signals | YES={yes_c} NO={no_c} | trend={trend_c} mr={mr_c} con={con_c} carry={carry_c}")
PY
