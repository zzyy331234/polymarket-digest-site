#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, List, Optional

from .scoring import build_signal, clamp


DEFAULT_LOW_TRADABILITY = {
    "shared": {
        "require_volatility": True,
        "min_hours_to_event": 24 * 7,
        "max_abs_chg_1h": 0.003,
        "max_abs_chg_4h": 0.005,
        "max_abs_chg_24h": 0.015,
        "max_volatility": 0.0015,
        "edge_price_low": 0.10,
        "edge_price_high": 0.90,
    },
    "regimes": {
        "carry_no": {"enabled": True, "allow_mid_price": True},
        "mean_revert": {"enabled": True, "allow_mid_price": False},
        "trend": {"enabled": True, "allow_mid_price": False},
        "contrarian": {"enabled": True, "allow_mid_price": False},
    },
}


class MRASv2:
    def __init__(self, config: Optional[Dict] = None):
        config = config or {}
        self.low_tradability_config = config.get("low_tradability") or {}

    def _low_tradability_rule(self, regime: str) -> Dict:
        shared = dict(DEFAULT_LOW_TRADABILITY.get("shared", {}))
        shared.update((self.low_tradability_config.get("shared") or {}))
        regime_rule = dict((DEFAULT_LOW_TRADABILITY.get("regimes") or {}).get(regime, {}))
        regime_rule.update(((self.low_tradability_config.get("regimes") or {}).get(regime) or {}))
        shared.update(regime_rule)
        return shared
    def _is_deep_tail_world_cup(self, feature: Dict) -> bool:
        question = (feature.get("question") or "").lower()
        yes_price = float(feature.get("yes_price") or 0.0)
        hours_to_event = feature.get("hours_to_event")
        chg_4h = float(feature.get("chg_4h") or 0.0)
        chg_24h = float(feature.get("chg_24h") or 0.0)
        if "world cup" not in question:
            return False
        if yes_price > 0.005:
            return False
        if hours_to_event is not None and hours_to_event < 24 * 30:
            return False
        return abs(chg_4h) < 0.01 and abs(chg_24h) < 0.02

    def _is_stale_carry_no(self, feature: Dict) -> bool:
        yes_price = float(feature.get("yes_price") or 0.0)
        chg_4h = float(feature.get("chg_4h") or 0.0)
        chg_24h = float(feature.get("chg_24h") or 0.0)
        volatility = float(feature.get("volatility") or 0.0)
        pct_rank_7d = feature.get("pct_rank_7d")
        pct_rank_30d = feature.get("pct_rank_30d")
        hours_to_event = feature.get("hours_to_event")

        if yes_price > 0.012:
            return False
        if hours_to_event is not None and hours_to_event < 24 * 14:
            return False
        if abs(chg_4h) >= 0.005 or abs(chg_24h) >= 0.01:
            return False
        if volatility >= 0.002:
            return False
        if pct_rank_7d is not None and pct_rank_7d < 0.98:
            return False
        if pct_rank_30d is not None and pct_rank_30d < 0.98:
            return False
        return True

    def _is_low_tradability(self, feature: Dict, regime: str) -> bool:
        rule = self._low_tradability_rule(regime)
        if not rule.get("enabled", True):
            return False

        yes_price = float(feature.get("yes_price") or 0.0)
        chg_1h = float(feature.get("chg_1h") or 0.0)
        chg_4h = float(feature.get("chg_4h") or 0.0)
        chg_24h = float(feature.get("chg_24h") or 0.0)
        volatility_raw = feature.get("volatility")
        pct_rank_7d = feature.get("pct_rank_7d")
        pct_rank_30d = feature.get("pct_rank_30d")
        hours_to_event = feature.get("hours_to_event")

        require_volatility = bool(rule.get("require_volatility", True))
        if require_volatility and volatility_raw is None:
            return False
        volatility = float(volatility_raw) if volatility_raw is not None else None

        min_hours_to_event = rule.get("min_hours_to_event")
        if hours_to_event is not None and min_hours_to_event is not None and hours_to_event < float(min_hours_to_event):
            return False
        if abs(chg_1h) >= float(rule.get("max_abs_chg_1h", 0.003)):
            return False
        if abs(chg_4h) >= float(rule.get("max_abs_chg_4h", 0.005)):
            return False
        if abs(chg_24h) >= float(rule.get("max_abs_chg_24h", 0.015)):
            return False
        max_volatility = rule.get("max_volatility")
        if volatility is not None and max_volatility is not None and volatility >= float(max_volatility):
            return False

        edge_price_low = rule.get("edge_price_low")
        edge_price_high = rule.get("edge_price_high")
        edge_price = False
        if edge_price_low is not None and yes_price <= float(edge_price_low):
            edge_price = True
        if edge_price_high is not None and yes_price >= float(edge_price_high):
            edge_price = True
        if edge_price:
            return True
        if rule.get("allow_mid_price", False):
            edge_pct = False
            if pct_rank_7d is not None and (pct_rank_7d <= 0.08 or pct_rank_7d >= 0.92):
                edge_pct = True
            if pct_rank_30d is not None and (pct_rank_30d <= 0.08 or pct_rank_30d >= 0.92):
                edge_pct = True
            return edge_pct
        return False

    def evaluate(self, feature: Dict) -> Optional[Dict]:
        yes_price = feature.get("yes_price") or 0.0
        liquidity = feature.get("liquidity") or 0.0
        chg_4h = feature.get("chg_4h")
        chg_24h = feature.get("chg_24h")
        chg_7d = feature.get("chg_7d")
        rsi = feature.get("rsi_14")
        pct_rank = feature.get("pct_rank_7d")
        slope_4h = feature.get("trend_slope_4h")
        slope_24h = feature.get("trend_slope_24h")
        noise = feature.get("noise_score")
        hours_to_event = feature.get("hours_to_event")

        advisory_flags: List[str] = []
        blocking_flags: List[str] = []
        if liquidity < 20000:
            return None
        if hours_to_event is not None:
            if hours_to_event <= 6:
                return None
            if hours_to_event <= 24:
                advisory_flags.append("event_near")
                blocking_flags.append("event_near")
            elif hours_to_event <= 48:
                advisory_flags.append("event_soon")
        if noise is not None and noise > 2.5:
            advisory_flags.append("high_noise")
            blocking_flags.append("high_noise")

        # 1) carry_no: low YES price markets should not leak into trend
        if yes_price <= 0.03:
            local_advisory = list(advisory_flags)
            local_blocking = list(blocking_flags)
            reasons = ["ultra low YES price", "better classified as carry_no than trend"]
            if self._is_low_tradability(feature, "carry_no"):
                local_advisory.append("low_tradability")
                local_blocking.append("low_tradability")
                reasons.append("low tradability profile")
            if self._is_stale_carry_no(feature):
                local_advisory.append("stale_carry_no")
                local_blocking.append("stale_carry_no")
                reasons.append("stale low-vol carry_no")
            if self._is_deep_tail_world_cup(feature):
                local_advisory.append("deep_tail_world_cup")
                local_blocking.append("deep_tail_world_cup")
                reasons.append("deep-tail World Cup outright")
            setup = 0.85 if liquidity >= 50000 else 0.65
            edge = 0.55 if (chg_24h is None or abs(chg_24h) < 0.03) else 0.35
            execution = 0.75
            if "event_near" in local_advisory:
                execution -= 0.25
            elif "event_soon" in local_advisory:
                execution -= 0.12
            return build_signal(
                feature,
                regime="carry_no",
                direction="NO",
                setup_score=setup,
                edge_score=edge,
                execution_score=execution,
                reasons=reasons,
                risk_flags=local_advisory + local_blocking,
                advisory_flags=local_advisory,
                blocking_flags=local_blocking,
            )

        # 2) trend
        trend_hits = 0
        reasons: List[str] = []
        local_advisory = list(advisory_flags)
        local_blocking = list(blocking_flags)
        if chg_4h is not None and abs(chg_4h) >= 0.02:
            trend_hits += 1
            reasons.append("4h move visible")
        if chg_24h is not None and abs(chg_24h) >= 0.05:
            trend_hits += 1
            reasons.append("24h move strong")
        if chg_7d is not None and abs(chg_7d) >= 0.08:
            trend_hits += 1
            reasons.append("7d move strong")
        if chg_24h is not None and chg_7d is not None and chg_24h * chg_7d > 0:
            trend_hits += 1
            reasons.append("24h and 7d aligned")
        elif chg_4h is not None and chg_24h is not None and chg_4h * chg_24h > 0:
            trend_hits += 1
            reasons.append("4h and 24h aligned")
        if slope_4h is not None and slope_24h is not None and slope_4h * slope_24h > 0:
            trend_hits += 1
            reasons.append("4h and 24h slope aligned")
        if liquidity >= 50000:
            trend_hits += 1
            reasons.append("liquidity good")

        trend_trigger = False
        if chg_7d is not None:
            trend_trigger = trend_hits >= 5
        else:
            trend_trigger = trend_hits >= 5 and chg_4h is not None and chg_24h is not None

        if trend_trigger and chg_24h is not None:
            direction = "YES" if chg_24h > 0 else "NO"
            if direction == "NO" and yes_price <= 0.05:
                trend_trigger = False
            else:
                if self._is_low_tradability(feature, "trend"):
                    local_advisory.append("low_tradability")
                    local_blocking.append("low_tradability")
                    reasons.append("low tradability profile")
                setup = clamp(0.55 + (0.15 if liquidity >= 100000 else 0.0))
                edge = clamp(0.42 + min(abs(chg_24h) * 2.3, 0.23))
                execution = 0.75
                if chg_7d is None:
                    execution -= 0.08
                    reasons.append("7d window missing, using 4h/24h fallback")
                if "event_near" in local_advisory:
                    execution -= 0.22
                elif "event_soon" in local_advisory:
                    execution -= 0.10
                if noise is not None and noise > 1.8:
                    execution -= 0.15
                    local_advisory.append("trend_noisy")
                    local_blocking.append("trend_noisy")
                return build_signal(
                    feature,
                    "trend",
                    direction,
                    setup,
                    edge,
                    execution,
                    reasons,
                    local_advisory + local_blocking,
                    advisory_flags=local_advisory,
                    blocking_flags=local_blocking,
                )

        # 3) mean_revert
        mr_reasons: List[str] = []
        if pct_rank is not None and ((pct_rank <= 0.10) or (pct_rank >= 0.90)):
            edge = 0.45
            if rsi is not None and (rsi <= 35 or rsi >= 65):
                edge += 0.15
                mr_reasons.append("RSI extreme")
            if chg_24h is not None and abs(chg_24h) >= 0.03:
                edge += 0.10
                mr_reasons.append("24h move extended")
            direction = None
            if pct_rank <= 0.10:
                direction = "YES"
                mr_reasons.insert(0, "lower percentile bounce setup")
            elif pct_rank >= 0.90:
                direction = "NO"
                mr_reasons.insert(0, "upper percentile fade setup")
            if direction:
                local_advisory = list(advisory_flags)
                local_blocking = list(blocking_flags)
                if self._is_low_tradability(feature, "mean_revert"):
                    local_advisory.append("low_tradability")
                    local_blocking.append("low_tradability")
                    mr_reasons.append("low tradability profile")
                return build_signal(
                    feature,
                    "mean_revert",
                    direction,
                    setup_score=0.62,
                    edge_score=clamp(edge),
                    execution_score=0.68 if "event_near" not in local_advisory else 0.42,
                    reasons=mr_reasons,
                    risk_flags=local_advisory + local_blocking,
                    advisory_flags=local_advisory,
                    blocking_flags=local_blocking,
                )

        # 4) contrarian
        con_reasons: List[str] = []
        if yes_price >= 0.65 and chg_24h is not None and chg_24h < -0.03:
            edge = 0.55
            if chg_7d is not None and chg_7d < 0:
                edge += 0.10
                con_reasons.append("7d weakening too")
            if rsi is not None and rsi < 55:
                edge += 0.05
                con_reasons.append("RSI not overheated")
            local_advisory = list(advisory_flags)
            local_blocking = list(blocking_flags)
            if self._is_low_tradability(feature, "contrarian"):
                local_advisory.append("low_tradability")
                local_blocking.append("low_tradability")
                con_reasons.append("low tradability profile")
            return build_signal(
                feature,
                "contrarian",
                "NO",
                setup_score=0.66,
                edge_score=clamp(edge),
                execution_score=0.62 if "event_near" not in local_advisory else 0.40,
                reasons=["crowded YES fading"] + con_reasons,
                risk_flags=local_advisory + local_blocking,
                advisory_flags=local_advisory,
                blocking_flags=local_blocking,
            )

        return None


def scan_features(features: List[Dict], config: Optional[Dict] = None) -> List[Dict]:
    engine = MRASv2(config=config)
    out: List[Dict] = []
    for feature in features:
        sig = engine.evaluate(feature)
        if sig and sig.get("position") != "skip":
            out.append(sig)
    out.sort(key=lambda x: (x.get("confidence", 0.0), x.get("quality", 0.0)), reverse=True)
    return out
