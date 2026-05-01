#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Any, Dict, List


def infer_catalyst_type(sig: Dict[str, Any]) -> str:
    cluster = str(sig.get('cluster') or '')
    regime = str(sig.get('regime') or '')
    changes = [abs(float(sig.get(k, 0) or 0)) for k in ('chg_1h', 'chg_4h', 'chg_24h')]
    max_change = max(changes) if changes else 0.0
    reasons = ' '.join(sig.get('reasons', []) or []).lower()
    flags = ' '.join((sig.get('risk_flags', []) or []) + (sig.get('advisory_flags', []) or [])).lower()

    if 'world_cup' in cluster or 'gta' in cluster:
        return 'theme_cluster'
    if 'stale' in reasons or 'stale' in flags:
        return 'stale_carry'
    if max_change >= 0.05:
        return 'price_dislocation'
    if regime == 'trend':
        return 'trend_follow'
    if regime == 'mean_revert':
        return 'mean_reversion'
    return 'structural'


def infer_execution_readiness(sig: Dict[str, Any], config: Dict[str, Any] = None) -> str:
    config = config or {}
    blocked_clusters = set((((config.get('discipline_v2') or {}).get('execution') or {}).get('overrides') or {}).get('blocked_clusters', []) or [])
    blocked_regimes = set((((config.get('discipline_v2') or {}).get('execution') or {}).get('overrides') or {}).get('blocked_regimes', []) or [])
    observe_only_clusters = set((((config.get('discipline_v2') or {}).get('execution') or {}).get('overrides') or {}).get('observe_only_clusters', []) or [])
    observe_only_regimes = set((((config.get('discipline_v2') or {}).get('execution') or {}).get('overrides') or {}).get('observe_only_regimes', []) or [])
    strategy_vnext = config.get('strategy_vnext') or {}
    trade_regimes = set(((strategy_vnext.get('signal_rules') or {}).get('trade_regimes') or []) or [])
    vnext_observe_regimes = set(((strategy_vnext.get('signal_rules') or {}).get('observe_only_regimes') or []) or [])
    vnext_blocked_clusters = set(((strategy_vnext.get('tradability_gate') or {}).get('blocked_clusters') or []) or [])

    cluster = sig.get('cluster')
    regime = sig.get('regime')
    confidence = float(sig.get('confidence', 0) or 0)
    blocking = sig.get('blocking_flags', []) or []
    advisory = sig.get('advisory_flags', []) or []

    if blocking or cluster in blocked_clusters or cluster in vnext_blocked_clusters or regime in blocked_regimes:
        return 'do_not_touch'
    if cluster in observe_only_clusters or regime in observe_only_regimes or regime in vnext_observe_regimes:
        return 'watch'
    if trade_regimes and regime not in trade_regimes:
        return 'watch'
    if confidence >= 0.72 and len(advisory) == 0:
        return 'candidate'
    if confidence >= 0.64 and len(advisory) <= 1:
        return 'research'
    if confidence >= 0.58 and len(advisory) == 0 and regime not in ('carry_no', 'contrarian'):
        return 'watch'
    return 'do_not_touch'


def infer_evidence_score(sig: Dict[str, Any]) -> float:
    confidence = float(sig.get('confidence', 0) or 0)
    quality = float(sig.get('quality', 0) or 0)
    risk_penalty = float(sig.get('risk_score', 0) or 0) * 0.35
    advisory_penalty = 0.05 * len(sig.get('advisory_flags', []) or [])
    blocking_penalty = 0.1 * len(sig.get('blocking_flags', []) or [])
    score = confidence * 0.55 + quality * 0.35 - risk_penalty - advisory_penalty - blocking_penalty
    return round(max(0.0, min(1.0, score)), 4)


def build_thesis_summary(sig: Dict[str, Any]) -> str:
    regime = sig.get('regime', '-')
    direction = sig.get('direction', '-')
    question = sig.get('question', '')
    reasons = sig.get('reasons', []) or []
    lead_reason = reasons[0] if reasons else 'signal ranked by model'
    return f"[{regime}] {direction} on '{question}' because {lead_reason}."


def build_why_now(sig: Dict[str, Any]) -> str:
    chg_1h = float(sig.get('chg_1h', 0) or 0)
    chg_4h = float(sig.get('chg_4h', 0) or 0)
    chg_24h = float(sig.get('chg_24h', 0) or 0)
    if max(abs(chg_1h), abs(chg_4h), abs(chg_24h)) >= 0.05:
        return f"Short-term dislocation detected (1h={chg_1h:.3f}, 4h={chg_4h:.3f}, 24h={chg_24h:.3f})."
    if sig.get('cluster'):
        return f"Relevant within active cluster={sig.get('cluster')} and current regime={sig.get('regime')}."
    return f"Signal cleared current ranking thresholds with confidence={float(sig.get('confidence', 0) or 0):.2f}."


def build_do_not_trade_if(sig: Dict[str, Any]) -> List[str]:
    rules: List[str] = []
    if sig.get('blocking_flags'):
        rules.append('Any blocking flag remains active.')
    if sig.get('advisory_flags'):
        rules.append('Advisory flags worsen or increase before entry.')
    if sig.get('cluster') == 'world_cup':
        rules.append('World Cup cluster remains blocked / low-tradability heavy.')
    if sig.get('cluster') == 'gta_vi':
        rules.append('GTA VI themed cluster remains flat-heavy and should stay observational unless new catalyst appears.')
    if sig.get('regime') == 'carry_no':
        rules.append('Carry_no remains stale or still observe-only / blocked.')
    if 'high_noise' in (sig.get('blocking_flags', []) or []):
        rules.append('High-noise flag remains active.')
    rules.append('Liquidity/exit quality deteriorates materially before action.')
    return rules


def enrich_signal(sig: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
    enriched = dict(sig)
    enriched['catalyst_type'] = infer_catalyst_type(sig)
    enriched['execution_readiness'] = infer_execution_readiness(sig, config=config)
    enriched['evidence_score'] = infer_evidence_score(sig)
    enriched['thesis_summary'] = build_thesis_summary(sig)
    enriched['why_now'] = build_why_now(sig)
    enriched['do_not_trade_if'] = build_do_not_trade_if(sig)
    return enriched
