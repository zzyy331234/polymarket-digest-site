#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIGEST_JSON = ROOT / 'outputs' / 'short_intelligence_digest_latest.json'
OUT_HTML = ROOT / 'outputs' / 'short_intelligence_digest_latest.html'
ARCHIVE_HOME_HTML = ROOT / 'reports' / 'short_digest_html' / 'archive.html'
ARCHIVE_JSON = ROOT / 'reports' / 'short_digest_archive' / 'index.json'
REPORTS_DIR = ROOT / 'reports' / 'short_digest'
ARCHIVE_HTML_DIR = ROOT / 'reports' / 'short_digest_html'
PUBLISH_DIR = ROOT / 'dist' / 'digest_site'
PUBLISH_ARCHIVE_DIR = PUBLISH_DIR / 'archive'
PUBLISH_LATEST_DIR = PUBLISH_DIR / 'latest'
PUBLISH_INDEX_HTML = PUBLISH_DIR / 'index.html'
PUBLISH_MANIFEST = PUBLISH_DIR / 'manifest.json'


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def esc(text):
    return str(text or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def render_links(item):
    link = item.get('bilingual_link') or {}
    url = link.get('url')
    reason = esc(link.get('reason_cn') or '暂无来源摘要')
    if not url:
        return f'<div class="muted">暂无可用链接</div><div class="source-reason">为什么还值得看：{reason}</div>'
    return (
        f'<div class="links">'
        f'<div><strong>中文导读：</strong><a href="{esc(url)}" target="_blank">{esc(link.get("label_cn"))}</a></div>'
        f'<div><strong>English source:</strong> <a href="{esc(url)}" target="_blank">{esc(link.get("label_en"))}</a></div>'
        f'</div>'
        f'<div class="source-reason"><strong>为什么值得点开：</strong>{reason}</div>'
    )


def render_item(item, mode='main'):
    extra = ''
    if mode == 'avoid':
        if item.get('blocking_flags_cn'):
            extra = '避开原因：' + '；'.join(item.get('blocking_flags_cn', [])[:3])
        elif item.get('risk_flags_cn'):
            extra = '风险提示：' + '；'.join(item.get('risk_flags_cn', [])[:3])
        elif item.get('advisory_flags_cn'):
            extra = '观察提示：' + '；'.join(item.get('advisory_flags_cn', [])[:3])
    elif mode == 'watch':
        extra = '观察原因：' + esc(item.get('why_now_cn'))
    else:
        extra = '观点：' + esc(item.get('thesis_cn')) + '<br>现在看它的原因：' + esc(item.get('why_now_cn'))

    return f'''
    <div class="card">
      <div class="title">{esc(item.get('display_title_cn'))}</div>
      <div class="meta">{esc(item.get('readiness_label_cn'))} | {esc(item.get('cluster_label_cn'))} / {esc(item.get('regime_label_cn'))} | 方向={esc(item.get('direction'))} | conf={float(item.get('confidence', 0) or 0):.2f}</div>
      <div class="body">{extra}</div>
      {render_links(item)}
      <div class="raw">原题：{esc(item.get('raw_question'))}</div>
    </div>
    '''


def archive_html_name(date_str):
    return f'{date_str}.html'


def archive_href_for_page(date, is_latest_page, publish_mode=False):
    file_name = archive_html_name(date)
    if publish_mode:
        return f'../archive/{file_name}' if is_latest_page else file_name
    return f'../reports/short_digest_html/{file_name}' if is_latest_page else file_name


def render_archive_nav(archive, current_date, is_latest_page, publish_mode=False):
    if not archive:
        return '<div class="muted">暂无历史样刊</div>'
    links = []
    for item in archive:
        date = item.get('date')
        href = archive_href_for_page(date, is_latest_page, publish_mode=publish_mode)
        cls = 'archive-chip active' if date == current_date else 'archive-chip'
        links.append(f'<a class="{cls}" href="{esc(href)}">{esc(date)}</a>')
    return ''.join(links)


def render_archive_list(archive, current_date, is_latest_page, publish_mode=False):
    if not archive:
        return '<li>暂无归档</li>'
    rows = []
    for item in archive:
        date = item.get('date')
        active = ' <span class="badge">当前</span>' if date == current_date else ''
        page_link = archive_href_for_page(date, is_latest_page, publish_mode=publish_mode)
        rows.append(
            f'<li><strong>{esc(date)}</strong>{active}｜{esc(item.get("title"))}'
            f'<br><span class="muted">{esc(item.get("one_liner"))}</span>'
            f'<br><a class="inline-link" href="{esc(page_link)}">打开这期 HTML 样刊</a>'
            f'<br><span class="muted">{esc(item.get("markdown_path"))}</span></li>'
        )
    return ''.join(rows)


def render_top_actions(is_latest_page, latest_href, publish_mode=False):
    actions = []
    if is_latest_page:
        actions.append('<a class="action-link" href="#archive">查看历史归档</a>')
        if publish_mode:
            actions.append('<a class="action-link" href="../archive/archive.html">归档首页</a>')
            actions.append('<a class="action-link" href="../index.html">发布版入口</a>')
        else:
            actions.append('<a class="action-link" href="../reports/short_digest_html/archive.html">归档首页</a>')
            actions.append('<a class="action-link" href="../dist/digest_site/index.html">发布版入口</a>')
    else:
        actions.append(f'<a class="action-link" href="{esc(latest_href)}">返回 latest 展示页</a>')
        actions.append('<a class="action-link" href="archive.html">归档首页</a>')
        if publish_mode:
            actions.append('<a class="action-link" href="../index.html">发布版入口</a>')
    return ''.join(actions)


def render_html(digest, archive, current_date, latest_href, is_latest_page, publish_mode=False):
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(digest.get('title', 'Polymarket 情报样刊'))}</title>
  <style>
    body {{ font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:#0b1020; color:#e8ecf3; margin:0; padding:32px; }}
    .wrap {{ max-width: 1120px; margin: 0 auto; }}
    .hero {{ padding:24px 28px; background:#121933; border:1px solid #253056; border-radius:18px; margin-bottom:20px; }}
    .hero h1 {{ margin:0 0 8px 0; font-size:32px; }}
    .hero p {{ margin:6px 0; color:#b7c2df; line-height:1.6; }}
    .top-actions {{ margin-top:14px; display:flex; flex-wrap:wrap; gap:10px; }}
    .action-link {{ display:inline-block; padding:8px 12px; border-radius:999px; background:#1a2448; border:1px solid #32406d; color:#d8e2ff; text-decoration:none; font-size:13px; }}
    .archive-nav {{ display:flex; flex-wrap:wrap; gap:10px; margin:18px 0 6px 0; }}
    .archive-chip {{ display:inline-block; padding:8px 12px; border-radius:999px; border:1px solid #32406d; background:#111936; color:#c8d6ff; text-decoration:none; font-size:13px; }}
    .archive-chip.active {{ background:#28407b; border-color:#5f8cff; color:#fff; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:16px; margin-bottom:24px; }}
    .section {{ margin-bottom:28px; }}
    .section h2 {{ margin:0 0 14px 0; font-size:22px; }}
    .card {{ background:#121933; border:1px solid #253056; border-radius:16px; padding:16px; margin-bottom:12px; }}
    .title {{ font-size:18px; font-weight:700; margin-bottom:8px; }}
    .meta {{ color:#98a7d1; font-size:13px; margin-bottom:10px; }}
    .body {{ color:#e8ecf3; line-height:1.6; margin-bottom:10px; }}
    .links {{ color:#c7d3f1; line-height:1.6; margin-bottom:10px; }}
    .links a, .inline-link {{ color:#7bc4ff; text-decoration:none; }}
    .source-reason {{ color:#d8e2ff; line-height:1.6; margin:0 0 10px 0; background:#172246; border-radius:12px; padding:10px 12px; }}
    .raw {{ color:#7f8db5; font-size:12px; }}
    .pill {{ display:inline-block; padding:8px 12px; border-radius:999px; background:#1a2448; color:#d8e2ff; margin:4px 8px 0 0; font-size:13px; }}
    .muted {{ color:#7f8db5; }}
    .badge {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#28407b; color:#fff; font-size:12px; }}
    ul.clean {{ list-style:none; padding:0; margin:0; }}
    ul.clean li {{ margin-bottom:10px; padding:12px 14px; background:#121933; border:1px solid #253056; border-radius:12px; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <h1>{esc(digest.get('title'))}</h1>
      <p><strong>{esc(digest.get('issue_date'))}</strong></p>
      <p>{esc(digest.get('one_liner'))}</p>
      <p>{esc(digest.get('mainline'))}</p>
      <div class="top-actions">
        {render_top_actions(is_latest_page, latest_href, publish_mode=publish_mode)}
      </div>
      <div class="archive-nav">{render_archive_nav(archive, current_date, is_latest_page, publish_mode=publish_mode)}</div>
      <p class="muted">每个日期都会对应一页独立 HTML 样刊，方便直接展示、分享和归档。</p>
    </div>

    <div class="section">
      <h2>主观察池</h2>
      {''.join(render_item(item, 'main') for item in (digest.get('top_candidates') or [])) or '<div class="muted">暂无主观察候选</div>'}
    </div>

    <div class="grid">
      <div class="section">
        <h2>谨慎观察</h2>
        {''.join(render_item(item, 'watch') for item in (digest.get('watch_items') or [])) or '<div class="muted">暂无观察项</div>'}
      </div>
      <div class="section">
        <h2>今天不碰</h2>
        {''.join(render_item(item, 'avoid') for item in (digest.get('avoid_items') or [])) or '<div class="muted">暂无避坑项</div>'}
      </div>
    </div>

    <div class="section">
      <h2>周度偏好</h2>
      <div>
        {''.join(f'<span class="pill">倾向保留：{esc(row.get("name_cn"))} | score={esc(row.get("score"))}</span>' for row in (digest.get('best_regimes') or []))}
        {''.join(f'<span class="pill">继续降权：{esc(row.get("name_cn"))} | flat={esc(row.get("flat"))}</span>' for row in (digest.get('worst_clusters') or []))}
      </div>
    </div>

    <div class="section">
      <h2>编辑注</h2>
      <ul class="clean">
        {''.join(f'<li>{esc(note)}</li>' for note in (digest.get('editor_notes') or []))}
      </ul>
    </div>

    <div class="section" id="archive">
      <h2>样刊归档</h2>
      <ul class="clean">
        {render_archive_list(archive, current_date, is_latest_page, publish_mode=publish_mode)}
      </ul>
    </div>
  </div>
</body>
</html>
'''


def render_archive_home(archive):
    latest_entry = archive[0] if archive else {}
    latest_href = '../../outputs/short_intelligence_digest_latest.html'
    publish_href = '../../dist/digest_site/index.html'
    cards = []
    for item in archive:
        date = item.get('date', '')
        title = item.get('title', 'Polymarket 情报样刊')
        one_liner = item.get('one_liner', '')
        file_name = archive_html_name(date)
        is_latest = item == latest_entry
        badge = '<span class="badge">最新</span>' if is_latest else ''
        cards.append(
            f'<a class="archive-card" href="{esc(file_name)}">'
            f'<div class="archive-card-date">{esc(date)} {badge}</div>'
            f'<div class="archive-card-title">{esc(title)}</div>'
            f'<div class="archive-card-body">{esc(one_liner)}</div>'
            f'</a>'
        )

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Polymarket 情报样刊归档</title>
  <style>
    body {{ font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:#0b1020; color:#e8ecf3; margin:0; padding:32px; }}
    .wrap {{ max-width: 1120px; margin: 0 auto; }}
    .hero {{ padding:24px 28px; background:#121933; border:1px solid #253056; border-radius:18px; margin-bottom:24px; }}
    .hero h1 {{ margin:0 0 10px 0; font-size:32px; }}
    .hero p {{ margin:6px 0; color:#b7c2df; line-height:1.6; }}
    .actions {{ margin-top:14px; display:flex; flex-wrap:wrap; gap:10px; }}
    .action-link {{ display:inline-block; padding:8px 12px; border-radius:999px; background:#1a2448; border:1px solid #32406d; color:#d8e2ff; text-decoration:none; font-size:13px; }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:16px; }}
    .archive-card {{ display:block; text-decoration:none; background:#121933; border:1px solid #253056; border-radius:16px; padding:18px; color:#e8ecf3; }}
    .archive-card-date {{ color:#9fb4eb; font-size:14px; margin-bottom:8px; }}
    .archive-card-title {{ font-size:20px; font-weight:700; margin-bottom:10px; }}
    .archive-card-body {{ color:#c7d3f1; line-height:1.7; }}
    .badge {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#28407b; color:#fff; font-size:12px; vertical-align:middle; }}
    .muted {{ color:#7f8db5; }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <h1>Polymarket 情报样刊归档</h1>
      <p>这里集中展示每一期样刊的 HTML 归档页，适合直接浏览、回看、分享。</p>
      <p class="muted">最新页保留为单独入口，归档页负责沉淀历史内容。</p>
      <div class="actions">
        <a class="action-link" href="{esc(latest_href)}">打开 latest 展示页</a>
        <a class="action-link" href="{esc(publish_href)}">打开发布版入口</a>
      </div>
    </div>
    <div class="grid">
      {''.join(cards) or '<div class="muted">暂无归档样刊</div>'}
    </div>
  </div>
</body>
</html>
'''


def render_publish_index(archive, latest_digest):
    latest_issue = latest_digest.get('issue_date', '')
    latest_title = latest_digest.get('title', 'Polymarket 情报样刊')
    latest_one_liner = latest_digest.get('one_liner', '')
    mainline = latest_digest.get('mainline', '')
    editor_notes = latest_digest.get('editor_notes') or []
    top_candidates = latest_digest.get('top_candidates') or []
    watch_items = latest_digest.get('watch_items') or []
    avoid_items = latest_digest.get('avoid_items') or []
    count = len(archive)
    latest_page = 'latest/short_intelligence_digest_latest.html'
    archive_page = 'archive/archive.html'
    latest_archive = archive[0] if archive else {}
    archive_cards = []
    for item in archive[:6]:
        date = item.get('date', '')
        title = item.get('title', 'Polymarket 情报样刊')
        one_liner = item.get('one_liner', '')
        href = f'archive/{archive_html_name(date)}'
        badge = '<span class="mini-badge">最新</span>' if item == latest_archive else ''
        archive_cards.append(
            f'<a class="archive-item" href="{esc(href)}">'
            f'<div class="archive-item-date">{esc(date)} {badge}</div>'
            f'<div class="archive-item-title">{esc(title)}</div>'
            f'<div class="archive-item-body">{esc(one_liner)}</div>'
            f'</a>'
        )

    spotlight = ''
    if top_candidates:
        first = top_candidates[0]
        spotlight = f'''
        <div class="spotlight-card">
          <div class="eyebrow">本期主线机会</div>
          <h2>{esc(first.get('display_title_cn'))}</h2>
          <p>{esc(first.get('thesis_cn'))}</p>
          <div class="spotlight-meta">{esc(first.get('readiness_label_cn'))} · {esc(first.get('cluster_label_cn'))} / {esc(first.get('regime_label_cn'))} · conf={float(first.get('confidence', 0) or 0):.2f}</div>
        </div>
        '''
    else:
        spotlight = '''
        <div class="spotlight-card">
          <div class="eyebrow">本期主线机会</div>
          <h2>暂无高优先级机会</h2>
          <p>当前更适合保持观察，等待更清晰的赔率错位和情绪回摆。</p>
          <div class="spotlight-meta">无主观察候选</div>
        </div>
        '''

    notes_html = ''.join(f'<li>{esc(note)}</li>' for note in editor_notes[:4]) or '<li>暂无编辑注</li>'

    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Polymarket 情报样刊发布版</title>
  <style>
    :root {{
      --bg:#08101f;
      --panel:#121933;
      --panel-2:#101935;
      --border:#253056;
      --border-strong:#30437b;
      --text:#eef2ff;
      --muted:#97a8d3;
      --muted-2:#7f8db5;
      --accent:#7bc4ff;
      --accent-2:#9ad7ff;
      --good:#89f0b5;
    }}
    * {{ box-sizing:border-box; }}
    body {{ font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; background:radial-gradient(circle at top,#12214a 0%,#08101f 42%,#060c17 100%); color:var(--text); margin:0; padding:32px; }}
    .wrap {{ max-width:1180px; margin:0 auto; }}
    .hero {{ background:linear-gradient(135deg,rgba(16,25,53,.96),rgba(21,39,85,.92)); border:1px solid var(--border-strong); border-radius:28px; padding:34px; margin-bottom:24px; box-shadow:0 18px 60px rgba(0,0,0,.28); }}
    .eyebrow {{ color:var(--accent-2); font-size:12px; letter-spacing:.14em; text-transform:uppercase; margin-bottom:12px; }}
    h1 {{ margin:0 0 14px 0; font-size:40px; line-height:1.1; }}
    p {{ color:#c6d3f4; line-height:1.75; margin:0 0 10px 0; }}
    .hero-grid {{ display:grid; grid-template-columns:1.35fr .95fr; gap:18px; align-items:stretch; margin-top:24px; }}
    .hero-copy {{ padding-right:8px; }}
    .hero-copy .subhead {{ font-size:18px; color:#e6eeff; margin-bottom:14px; }}
    .actions {{ display:flex; flex-wrap:wrap; gap:12px; margin-top:20px; }}
    .btn {{ display:inline-block; padding:11px 16px; border-radius:999px; text-decoration:none; background:var(--accent); color:#061120; font-weight:700; }}
    .btn.secondary {{ background:#172447; color:#dce7ff; border:1px solid #344979; }}
    .btn.ghost {{ background:transparent; color:#dce7ff; border:1px dashed #41619e; }}
    .spotlight-card {{ background:linear-gradient(180deg,rgba(18,25,51,.96),rgba(13,20,42,.98)); border:1px solid #34508d; border-radius:22px; padding:22px; }}
    .spotlight-card h2 {{ margin:0 0 10px 0; font-size:28px; line-height:1.2; }}
    .spotlight-card p {{ color:#deebff; }}
    .spotlight-meta {{ color:#9fb4eb; font-size:13px; margin-top:14px; }}
    .stats {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; margin-bottom:24px; }}
    .stat {{ background:rgba(18,25,51,.92); border:1px solid var(--border); border-radius:18px; padding:18px; }}
    .label {{ color:var(--muted); font-size:13px; margin-bottom:8px; }}
    .value {{ font-size:26px; font-weight:700; }}
    .section-grid {{ display:grid; grid-template-columns:1.2fr .8fr; gap:18px; margin-bottom:24px; }}
    .section {{ background:rgba(18,25,51,.94); border:1px solid var(--border); border-radius:22px; padding:22px; }}
    .section-title {{ margin:0 0 14px 0; font-size:22px; }}
    .summary-box {{ background:#0f1731; border:1px solid #233663; border-radius:16px; padding:16px; color:#dfe9ff; }}
    .summary-box strong {{ color:#fff; }}
    ul.clean {{ list-style:none; padding:0; margin:0; }}
    ul.clean li {{ margin-bottom:10px; padding:12px 14px; background:#0f1731; border:1px solid #22345f; border-radius:14px; color:#d7e2ff; }}
    .archive-list {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:14px; }}
    .archive-item {{ display:block; text-decoration:none; background:#0f1731; border:1px solid #243760; border-radius:16px; padding:16px; color:var(--text); }}
    .archive-item-date {{ color:#9fb4eb; font-size:13px; margin-bottom:8px; }}
    .archive-item-title {{ font-size:18px; font-weight:700; margin-bottom:8px; }}
    .archive-item-body {{ color:#c7d3f1; line-height:1.7; font-size:14px; }}
    .mini-badge {{ display:inline-block; padding:2px 8px; border-radius:999px; background:#28407b; color:#fff; font-size:11px; vertical-align:middle; }}
    .muted {{ color:var(--muted-2); }}
    @media (max-width: 900px) {{
      .hero-grid, .section-grid {{ grid-template-columns:1fr; }}
      .stats {{ grid-template-columns:repeat(2,minmax(0,1fr)); }}
      body {{ padding:18px; }}
      .hero {{ padding:24px; }}
      h1 {{ font-size:32px; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <div class="eyebrow">Polymarket intelligence digest</div>
      <div class="hero-grid">
        <div class="hero-copy">
          <h1>{esc(latest_title)}</h1>
          <p class="subhead">给中文用户直接看的样刊入口，不是工程输出，不是原始日志，而是已经整理过的可展示情报页。</p>
          <p><strong>本期日期：</strong>{esc(latest_issue or '-')}</p>
          <p><strong>一句话判断：</strong>{esc(latest_one_liner)}</p>
          <p><strong>当前主线：</strong>{esc(mainline or '暂无主线说明')}</p>
          <div class="actions">
            <a class="btn" href="{latest_page}">打开最新样刊</a>
            <a class="btn secondary" href="{archive_page}">查看历史归档</a>
            <a class="btn ghost" href="manifest.json">查看站点清单</a>
          </div>
        </div>
        {spotlight}
      </div>
    </div>

    <div class="stats">
      <div class="stat">
        <div class="label">已归档期数</div>
        <div class="value">{count}</div>
      </div>
      <div class="stat">
        <div class="label">主观察候选</div>
        <div class="value">{len(top_candidates)}</div>
      </div>
      <div class="stat">
        <div class="label">谨慎观察</div>
        <div class="value">{len(watch_items)}</div>
      </div>
      <div class="stat">
        <div class="label">今天不碰</div>
        <div class="value">{len(avoid_items)}</div>
      </div>
    </div>

    <div class="section-grid">
      <div class="section">
        <h2 class="section-title">这套站点现在能直接干什么</h2>
        <div class="summary-box">
          <p><strong>1.</strong> latest/ 保留最新样刊，适合每天直接打开。</p>
          <p><strong>2.</strong> archive/ 保留每一期独立 HTML，适合沉淀案例和回看。</p>
          <p><strong>3.</strong> 每条卡片都附带中英文来源和“为什么值得点开”，更像编辑稿，不像数据管道输出。</p>
        </div>
      </div>
      <div class="section">
        <h2 class="section-title">编辑注摘录</h2>
        <ul class="clean">
          {notes_html}
        </ul>
      </div>
    </div>

    <div class="section">
      <h2 class="section-title">近期样刊</h2>
      <div class="archive-list">
        {''.join(archive_cards) or '<div class="muted">暂无归档内容</div>'}
      </div>
      <p class="muted" style="margin-top:14px;">目录说明：latest/ 存放最新页，archive/ 存放归档首页与每期历史 HTML。</p>
    </div>
  </div>
</body>
</html>
'''


def publish_site(archive, latest_digest):
    if PUBLISH_DIR.exists():
        shutil.rmtree(PUBLISH_DIR)
    PUBLISH_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)
    PUBLISH_LATEST_DIR.mkdir(parents=True, exist_ok=True)

    publish_latest_html = render_html(
        digest=latest_digest,
        archive=archive,
        current_date=latest_digest.get('issue_date') or (archive[0].get('date') if archive else ''),
        latest_href='short_intelligence_digest_latest.html',
        is_latest_page=True,
        publish_mode=True,
    )
    (PUBLISH_LATEST_DIR / 'short_intelligence_digest_latest.html').write_text(publish_latest_html, encoding='utf-8')

    publish_archive_home = render_archive_home(archive).replace('../../outputs/short_intelligence_digest_latest.html', '../latest/short_intelligence_digest_latest.html').replace('../../dist/digest_site/index.html', '../index.html')
    (PUBLISH_ARCHIVE_DIR / 'archive.html').write_text(publish_archive_home, encoding='utf-8')

    for item in archive:
        date = item.get('date')
        digest_path = REPORTS_DIR / f'{date}.json'
        if not digest_path.exists():
            continue
        digest = load_json(digest_path, latest_digest)
        publish_archive_html = render_html(
            digest=digest,
            archive=archive,
            current_date=date,
            latest_href='../latest/short_intelligence_digest_latest.html',
            is_latest_page=False,
            publish_mode=True,
        )
        (PUBLISH_ARCHIVE_DIR / archive_html_name(date)).write_text(publish_archive_html, encoding='utf-8')

    manifest = {
        'generated_from': str(ROOT),
        'latest_issue': latest_digest.get('issue_date'),
        'archive_count': len(archive),
        'latest_entry': archive[0] if archive else {},
        'files': {
            'index': 'index.html',
            'latest': 'latest/short_intelligence_digest_latest.html',
            'archive_home': 'archive/archive.html',
            'archive_pages': [f'archive/{archive_html_name(item.get("date"))}' for item in archive],
        },
    }
    PUBLISH_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    PUBLISH_INDEX_HTML.write_text(render_publish_index(archive, latest_digest), encoding='utf-8')


def write_archive_pages(archive, latest_digest):
    ARCHIVE_HTML_DIR.mkdir(parents=True, exist_ok=True)
    for item in archive:
        date = item.get('date')
        digest_path = REPORTS_DIR / f'{date}.json'
        if not digest_path.exists():
            continue
        digest = load_json(digest_path, latest_digest)
        out_path = ARCHIVE_HTML_DIR / archive_html_name(date)
        html = render_html(
            digest=digest,
            archive=archive,
            current_date=date,
            latest_href='../../outputs/short_intelligence_digest_latest.html',
            is_latest_page=False,
        )
        out_path.write_text(html, encoding='utf-8')

    ARCHIVE_HOME_HTML.write_text(render_archive_home(archive), encoding='utf-8')


def main():
    archive = load_json(ARCHIVE_JSON, [])[:32]
    latest_digest = load_json(DIGEST_JSON, {})
    latest_date = latest_digest.get('issue_date') or (archive[0].get('date') if archive else '')

    latest_html = render_html(
        digest=latest_digest,
        archive=archive,
        current_date=latest_date,
        latest_href='short_intelligence_digest_latest.html',
        is_latest_page=True,
    )
    OUT_HTML.write_text(latest_html, encoding='utf-8')
    write_archive_pages(archive, latest_digest)
    publish_site(archive, latest_digest)
    print(f'wrote {OUT_HTML}')
    print(f'wrote archive html pages under {ARCHIVE_HTML_DIR}')
    print(f'wrote {ARCHIVE_HOME_HTML}')
    print(f'published static site under {PUBLISH_DIR}')


if __name__ == '__main__':
    main()
