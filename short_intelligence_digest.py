#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent
DAILY_JSON = ROOT / 'outputs' / 'daily_intelligence_latest.json'
WEEKLY_JSON = ROOT / 'outputs' / 'weekly_intelligence_summary.json'
OUT_MD = ROOT / 'outputs' / 'short_intelligence_digest_latest.md'
OUT_JSON = ROOT / 'outputs' / 'short_intelligence_digest_latest.json'
REPORTS_DIR = ROOT / 'reports' / 'short_digest'
ARCHIVE_DIR = ROOT / 'reports' / 'short_digest_archive'
ARCHIVE_INDEX_MD = ARCHIVE_DIR / 'index.md'
ARCHIVE_INDEX_JSON = ARCHIVE_DIR / 'index.json'

TEAM_CN = {
    'Utah Mammoth': '犹他猛犸',
    'Vegas Golden Knights': '维加斯金骑士',
}

PERSON_CN = {
    'Xi Jinping': '习近平',
    'Pete Buttigieg': '皮特·布蒂吉格',
    'George Clooney': '乔治·克鲁尼',
    'Andrew Yang': '杨安泽',
    'Donald Trump': '唐纳德·特朗普',
    'Alexandria Ocasio-Cortez': '亚历山大·奥卡西奥-科尔特斯',
    'Putin': '普京',
    'Jesus Christ': '耶稣基督',
}

CLUSTER_CN = {
    'us_election': '美国大选',
    'world_cup': '世界杯主题',
    'gta_vi': 'GTA VI 主题',
    'other': '其他事件',
}

REGIME_CN = {
    'trend': '趋势延续',
    'mean_revert': '均值回归',
    'carry_no': '低效拖时间盘',
    'contrarian': '逆向博弈',
}

READINESS_CN = {
    'candidate': '主观察',
    'research': '研究观察',
    'watch': '谨慎观察',
    'do_not_touch': '不碰',
}

FLAG_CN = {
    'low_tradability': '流动性差，退出困难',
    'high_noise': '噪音过高，方向不稳定',
    'stale_signal': '信号陈旧，缺乏新催化',
    'wide_spread': '价差偏大，执行质量差',
    'cooldown_active': '冷却期内，暂不适合重复动作',
}


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def pick_top(items: List[Dict[str, Any]], limit: int) -> List[Dict[str, Any]]:
    return sorted(
        items or [],
        key=lambda x: (
            {'candidate': 0, 'research': 1, 'watch': 2, 'do_not_touch': 3}.get(x.get('execution_readiness'), 9),
            -float(x.get('evidence_score', 0) or 0),
            -float(x.get('confidence', 0) or 0),
        ),
    )[:limit]


def slugify(text: str) -> str:
    text = (text or '').lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-') or 'market'


def first_match(mapping: Dict[str, str], text: str) -> str:
    for key, value in mapping.items():
        if key in text:
            return value
    return ''


def cluster_label(name: str) -> str:
    return CLUSTER_CN.get(name or '', name or '未分类')


def regime_label(name: str) -> str:
    return REGIME_CN.get(name or '', name or '未分类')


def readiness_label(name: str) -> str:
    return READINESS_CN.get(name or '', name or '未分类')


def flag_label(name: str) -> str:
    return FLAG_CN.get(name or '', name or '未知风险')


def flags_to_cn(flags: List[str]) -> List[str]:
    return [flag_label(flag) for flag in (flags or [])]


def market_url(sig: Dict[str, Any]) -> str:
    if sig.get('market_url'):
        return sig.get('market_url')
    slug = sig.get('slug')
    if slug:
        return f'https://polymarket.com/question/{slug}'
    return ''


def source_reason(sig: Dict[str, Any]) -> str:
    reasons = sig.get('reasons', []) or []
    cluster = sig.get('cluster') or ''
    confidence = float(sig.get('confidence', 0) or 0)
    evidence = float(sig.get('evidence_score', 0) or 0)

    if '4h move visible' in reasons or '24h move strong' in reasons:
        return '因为这题已经出现了可见的短线异动，点开原盘能直接核对价格是否还在延续。'
    if 'upper percentile fade setup' in reasons:
        return '因为它更像高位回落型 setup，点开原盘主要是确认价格是否还停留在偏贵区间。'
    if 'RSI extreme' in reasons:
        return '因为短线指标已经偏极端，点开原盘可以先看有没有继续被情绪推着走。'
    if cluster == 'gta_vi':
        return '因为它属于主题噪音盘，点开更多是为了确认热度，而不是为了执行。'
    if evidence >= 0.75 or confidence >= 0.70:
        return '因为它属于当前少数还留在版面里的高证据线索，值得直接去原盘核对成交和价格位置。'
    return '因为它还在观察名单里，点开原盘可以快速判断这条线索是不是还活着。'


def bilingual_link_payload(sig: Dict[str, Any]) -> Dict[str, str]:
    url = market_url(sig)
    title_cn = sig.get('display_title_cn') or sig.get('question') or ''
    title_en = sig.get('raw_question') or sig.get('question') or ''
    reason_cn = source_reason(sig)
    if not url:
        return {
            'title_cn': title_cn,
            'title_en': title_en,
            'url': '',
            'label_cn': '暂无可用链接',
            'label_en': 'No source link available',
            'reason_cn': reason_cn,
        }
    return {
        'title_cn': title_cn,
        'title_en': title_en,
        'url': url,
        'label_cn': f'中文导读：{title_cn}',
        'label_en': f'English source: {title_en}',
        'reason_cn': reason_cn,
    }


def to_display_title(question: str, cluster: str = '', regime: str = '') -> Dict[str, str]:
    q = question or ''
    cluster = cluster or ''
    regime = regime or ''

    if 'GTA VI' in q:
        if 'before GTA VI' in q:
            subject = q.replace(' before GTA VI?', '').replace('Will ', '')
            subject_cn = first_match(PERSON_CN, subject) or subject
            return {
                'display_title_cn': f'主题盘：{subject_cn}会先于 GTA VI 发生吗？',
                'display_slug': f'gta-vi-theme-{slugify(subject)}',
                'raw_question': q,
            }
        return {
            'display_title_cn': '主题盘：GTA VI 相关事件',
            'display_slug': 'gta-vi-theme',
            'raw_question': q,
        }

    if 'World Cup' in q or cluster == 'world_cup':
        return {
            'display_title_cn': '世界杯主题盘',
            'display_slug': 'world-cup-theme',
            'raw_question': q,
        }

    if 'out before' in q:
        person = q.split(' out before')[0].replace('Will ', '').strip()
        person_cn = first_match(PERSON_CN, person) or person
        year = q.split('before ')[-1].replace('?', '')
        return {
            'display_title_cn': f'人事盘：{person_cn}会在{year}前下台吗？',
            'display_slug': f'leadership-exit-{slugify(person)}',
            'raw_question': q,
        }

    if 'win the 2026 NHL Stanley Cup' in q:
        team = q.replace('Will the ', '').replace(' win the 2026 NHL Stanley Cup?', '')
        team_cn = first_match(TEAM_CN, team) or team
        return {
            'display_title_cn': f'体育盘：{team_cn}能否赢得 2026 年 NHL 斯坦利杯？',
            'display_slug': f'nhl-stanley-cup-{slugify(team)}',
            'raw_question': q,
        }

    if 'Democratic presidential nomination' in q:
        person = q.replace('Will ', '').replace(' win the 2028 Democratic presidential nomination?', '')
        person_cn = first_match(PERSON_CN, person) or person
        return {
            'display_title_cn': f'选举盘：{person_cn}能否赢得 2028 民主党总统提名？',
            'display_slug': f'dem-primary-{slugify(person)}',
            'raw_question': q,
        }

    if 'US Presidential Election' in q:
        person = q.replace('Will ', '').replace(' win the 2028 US Presidential Election?', '')
        person_cn = first_match(PERSON_CN, person) or person
        return {
            'display_title_cn': f'选举盘：{person_cn}能否赢得 2028 美国总统大选？',
            'display_slug': f'us-election-{slugify(person)}',
            'raw_question': q,
        }

    if 'President of Russia' in q:
        return {
            'display_title_cn': '人事盘：普京会在 2026 年底前失去总统职位吗？',
            'display_slug': 'putin-exit-2026',
            'raw_question': q,
        }

    return {
        'display_title_cn': f'观察盘：{q}',
        'display_slug': slugify(q),
        'raw_question': q,
    }


def rewrite_thesis(sig: Dict[str, Any]) -> str:
    direction = sig.get('direction') or '-'
    regime = regime_label(sig.get('regime'))
    reasons = sig.get('reasons', []) or []
    cluster = cluster_label(sig.get('cluster'))
    if '4h move visible' in reasons or '24h move strong' in reasons:
        return f'市场短线异动已经放大，当前更像{regime}下的延续机会，方向偏向 {direction}。'
    if 'upper percentile fade setup' in reasons:
        return f'价格已处在阶段性高位，更像{regime}框架下的回落博弈，方向偏向 {direction}。'
    if 'RSI extreme' in reasons:
        return f'短线指标已偏极端，继续追价性价比一般，更适合按{regime}思路处理。'
    return f'这是一笔来自“{cluster}”的{regime}型线索，目前方向偏向 {direction}。'


def rewrite_why_now(sig: Dict[str, Any]) -> str:
    chg_1h = float(sig.get('chg_1h', 0) or 0)
    chg_4h = float(sig.get('chg_4h', 0) or 0)
    chg_24h = float(sig.get('chg_24h', 0) or 0)
    cluster = cluster_label(sig.get('cluster'))
    regime = regime_label(sig.get('regime'))
    max_abs = max(abs(chg_1h), abs(chg_4h), abs(chg_24h))
    if max_abs >= 0.10:
        return '过去 24 小时内价格错位已经足够明显，属于可以单独拎出来观察的强波动线索。'
    if max_abs >= 0.05:
        return '短周期价格已经出现可见偏移，这类信号更适合放进今日观察池，而不是直接忽略。'
    if sig.get('cluster') == 'gta_vi':
        return '它仍属于 GTA VI 主题盘，只能做跟踪，不适合给主栏位置。'
    return f'它属于“{cluster}”里的{regime}型线索，虽然爆发力一般，但还值得继续盯一眼。'


def enrich_display(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for item in items or []:
        enriched = dict(item)
        enriched.update(to_display_title(item.get('question', ''), item.get('cluster', ''), item.get('regime', '')))
        enriched['cluster_label_cn'] = cluster_label(item.get('cluster'))
        enriched['regime_label_cn'] = regime_label(item.get('regime'))
        enriched['readiness_label_cn'] = readiness_label(item.get('execution_readiness'))
        enriched['blocking_flags_cn'] = flags_to_cn(item.get('blocking_flags', []))
        enriched['risk_flags_cn'] = flags_to_cn(item.get('risk_flags', []))
        enriched['advisory_flags_cn'] = flags_to_cn(item.get('advisory_flags', []))
        enriched['thesis_cn'] = rewrite_thesis(enriched)
        enriched['why_now_cn'] = rewrite_why_now(enriched)
        enriched['bilingual_link'] = bilingual_link_payload(enriched)
        out.append(enriched)
    return out


def build_mainline(daily: Dict[str, Any], weekly: Dict[str, Any]) -> str:
    top = (daily.get('active_candidates') or [])[:1]
    worst_clusters = (weekly.get('ranked_clusters') or {}).get('worst', [])[:2]
    if top:
        title = to_display_title(top[0].get('question', ''), top[0].get('cluster', ''), top[0].get('regime', '')).get('display_title_cn')
    else:
        title = '暂无足够强的主观察标的'
    if worst_clusters:
        weak = '、'.join(cluster_label(row.get('name', '-')) for row in worst_clusters)
        return f'今天的主线不是扩张出手，而是收缩注意力：主看“{title}”，继续回避 {weak} 这类 flat-heavy 噪音盘。'
    return f'今天的主线不是扩张出手，而是收缩注意力：主看“{title}”，继续坚持 paper-only。'


def build_editor_note(daily: Dict[str, Any], weekly: Dict[str, Any]) -> List[str]:
    notes = []
    paper = daily.get('paper_summary', {}) or {}
    notes.append(f"当前 paper 胜率 {paper.get('win_rate')}，flat_rate {paper.get('flat_rate')}，说明系统仍处在去噪优先阶段。")
    worst_regimes = (weekly.get('ranked_regimes') or {}).get('worst', [])[:1]
    if worst_regimes:
        notes.append(f"{regime_label(worst_regimes[0].get('name'))} 仍是最弱 regime，不值得给额外注意力。")
    notes.append('样刊主栏宁可少，也不要把低质量主题盘硬塞进去。')
    notes.append('对中文读者，所有有效链接都应同时提供中文导读标题和英文原题，降低理解门槛。')
    return notes


def build_digest() -> Dict[str, Any]:
    daily = load_json(DAILY_JSON, {})
    weekly = load_json(WEEKLY_JSON, {})
    active = enrich_display(pick_top(daily.get('active_candidates', []), 3))
    watch = enrich_display(pick_top(daily.get('watchlist', []), 2))
    avoid = enrich_display(pick_top(daily.get('do_not_touch', []), 3))
    best_regimes = [dict(row, name_cn=regime_label(row.get('name'))) for row in ((weekly.get('ranked_regimes') or {}).get('best', [])[:2])]
    worst_clusters = [dict(row, name_cn=cluster_label(row.get('name'))) for row in ((weekly.get('ranked_clusters') or {}).get('worst', [])[:2])]
    return {
        'generated_at': datetime.now().isoformat(timespec='seconds'),
        'title': 'Polymarket 情报样刊',
        'issue_date': datetime.now().strftime('%Y-%m-%d'),
        'one_liner': '继续 paper-only，把版面留给少量高证据候选，把 flat-heavy 主题盘挡在主栏之外。',
        'mainline': build_mainline(daily, weekly),
        'top_candidates': active,
        'watch_items': watch,
        'avoid_items': avoid,
        'best_regimes': best_regimes,
        'worst_clusters': worst_clusters,
        'paper_gate_eligible': daily.get('paper_gate_eligible'),
        'paper_summary': daily.get('paper_summary', {}),
        'editor_notes': build_editor_note(daily, weekly),
    }


def render_links(sig: Dict[str, Any]) -> List[str]:
    link = sig.get('bilingual_link', {}) or {}
    if not link.get('url'):
        return [
            '  链接: 暂无可用链接',
            f"  值得点开的原因: {link.get('reason_cn', '暂无来源摘要')}",
        ]
    return [
        f"  链接（中文导读）: {link.get('label_cn')}",
        f"  Link (English source): {link.get('label_en')}",
        f"  URL: {link.get('url')}",
        f"  值得点开的原因: {link.get('reason_cn')}",
    ]


def render_candidate(sig: Dict[str, Any]) -> List[str]:
    lines = []
    lines.append(f"- {sig.get('display_title_cn')}")
    lines.append(f"  标签: {sig.get('readiness_label_cn')} | 方向={sig.get('direction')} | conf={float(sig.get('confidence', 0) or 0):.2f} | evidence={float(sig.get('evidence_score', 0) or 0):.2f}")
    lines.append(f"  类型: {sig.get('cluster_label_cn')} / {sig.get('regime_label_cn')}")
    lines.append(f"  观点: {sig.get('thesis_cn')}")
    lines.append(f"  现在看它的原因: {sig.get('why_now_cn')}")
    lines.extend(render_links(sig))
    lines.append(f"  原始题目: {sig.get('raw_question')}")
    return lines


def render_md(digest: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# {digest['title']} | {digest['issue_date']}")
    lines.append('')
    lines.append('一句话判断')
    lines.append(digest['one_liner'])
    lines.append('')
    lines.append('## 今日主线')
    lines.append(digest['mainline'])
    lines.append('')
    lines.append('## 主观察池')
    if not digest['top_candidates']:
        lines.append('- 今天没有值得放进主栏的候选。')
    else:
        for sig in digest['top_candidates']:
            lines.extend(render_candidate(sig))
    lines.append('')
    lines.append('## 谨慎观察')
    if not digest['watch_items']:
        lines.append('- 暂无需要单列跟踪的观察项。')
    else:
        for sig in digest['watch_items']:
            lines.append(f"- {sig.get('display_title_cn')} | {sig.get('cluster_label_cn')} / {sig.get('regime_label_cn')}")
            lines.append(f"  观察原因: {sig.get('why_now_cn')}")
            lines.extend(render_links(sig))
            lines.append(f"  原始题目: {sig.get('raw_question')}")
    lines.append('')
    lines.append('## 今天不碰')
    if not digest['avoid_items']:
        lines.append('- 暂无新增避坑项。')
    else:
        for sig in digest['avoid_items']:
            lines.append(f"- {sig.get('display_title_cn')} | {sig.get('cluster_label_cn')} | {sig.get('regime_label_cn')}")
            if sig.get('blocking_flags_cn'):
                lines.append(f"  避开原因: {'；'.join(sig.get('blocking_flags_cn', [])[:3])}")
            elif sig.get('risk_flags_cn'):
                lines.append(f"  风险提示: {'；'.join(sig.get('risk_flags_cn', [])[:3])}")
            elif sig.get('advisory_flags_cn'):
                lines.append(f"  观察提示: {'；'.join(sig.get('advisory_flags_cn', [])[:3])}")
            lines.extend(render_links(sig))
            lines.append(f"  原始题目: {sig.get('raw_question')}")
    lines.append('')
    lines.append('## 周度偏好')
    if digest['best_regimes']:
        for row in digest['best_regimes']:
            lines.append(f"- 倾向保留: {row.get('name_cn')} | score={row.get('score')} | total={row.get('total')}")
    if digest['worst_clusters']:
        for row in digest['worst_clusters']:
            lines.append(f"- 应继续降权: {row.get('name_cn')} | score={row.get('score')} | flat={row.get('flat')}")
    lines.append('')
    lines.append('## 编辑注')
    for note in digest['editor_notes']:
        lines.append(f"- {note}")
    lines.append('')
    lines.append('## 底稿')
    lines.append(f"- Paper gate eligible: {digest.get('paper_gate_eligible')}")
    lines.append(f"- Paper summary: {digest.get('paper_summary')}")
    return '\n'.join(lines) + '\n'


def build_archive_index() -> None:
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    entries = []
    for path in sorted(REPORTS_DIR.glob('*.json')):
        if path.name == 'index.json':
            continue
        payload = load_json(path, {})
        date = payload.get('issue_date') or payload.get('generated_at', '')[:10]
        title = payload.get('title', 'Polymarket 情报样刊')
        one_liner = payload.get('one_liner', '')
        md_rel = str((REPORTS_DIR / f'{date}.md').relative_to(ROOT)) if (REPORTS_DIR / f'{date}.md').exists() else ''
        json_rel = str(path.relative_to(ROOT))
        entries.append({
            'date': date,
            'title': title,
            'one_liner': one_liner,
            'markdown_path': md_rel,
            'json_path': json_rel,
        })

    entries = sorted(entries, key=lambda x: x.get('date', ''), reverse=True)
    ARCHIVE_INDEX_JSON.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding='utf-8')

    lines = ['# Polymarket 情报样刊归档', '']
    if not entries:
        lines.append('- 暂无归档记录')
    else:
        for item in entries:
            lines.append(f"- {item['date']} | {item['title']}")
            lines.append(f"  摘要: {item['one_liner']}")
            lines.append(f"  Markdown: {item['markdown_path']}")
            lines.append(f"  JSON: {item['json_path']}")
            lines.append('')
    ARCHIVE_INDEX_MD.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')


def main() -> None:
    digest = build_digest()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    markdown = render_md(digest)
    OUT_JSON.write_text(json.dumps(digest, ensure_ascii=False, indent=2), encoding='utf-8')
    OUT_MD.write_text(markdown, encoding='utf-8')
    date_str = digest['generated_at'][:10]
    (REPORTS_DIR / f'{date_str}.json').write_text(json.dumps(digest, ensure_ascii=False, indent=2), encoding='utf-8')
    (REPORTS_DIR / f'{date_str}.md').write_text(markdown, encoding='utf-8')
    build_archive_index()
    print(f'wrote {OUT_MD} and {OUT_JSON}')
    print(f'archive {ARCHIVE_INDEX_MD} and {ARCHIVE_INDEX_JSON}')


if __name__ == '__main__':
    main()
