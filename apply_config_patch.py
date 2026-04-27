#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

CONFIG_FILE = Path('/Users/mac/.openclaw/workspace/polymarket/trading_config.json')
PATCH_FILE = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/proposed_config_patch.json')
BACKUP_DIR = Path('/Users/mac/.openclaw/workspace/polymarket/backups')
APPLY_LOG = Path('/Users/mac/.openclaw/workspace/polymarket/outputs/applied_config_patches.jsonl')


def load_json(path: Path, default=None):
    if default is None:
        default = {}
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def ensure_parent(root: Dict, parts: List[str]) -> Dict:
    cur = root
    for part in parts:
        if part not in cur or not isinstance(cur[part], dict):
            cur[part] = {}
        cur = cur[part]
    return cur


def get_value(root: Dict, path: str):
    cur = root
    for part in path.split('.'):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def set_value(root: Dict, path: str, value: Any) -> None:
    parts = path.split('.')
    parent = ensure_parent(root, parts[:-1])
    parent[parts[-1]] = value


def add_unique(root: Dict, path: str, value: Any) -> bool:
    current = get_value(root, path)
    if current is None:
        set_value(root, path, [value])
        return True
    if not isinstance(current, list):
        raise TypeError(f'{path} is not a list')
    if value in current:
        return False
    current.append(value)
    return True


def apply_change(config: Dict, change: Dict) -> Dict:
    path = change['path']
    action = change['action']
    result = {
        'path': path,
        'action': action,
        'status': 'noop',
    }

    if action == 'add':
        changed = add_unique(config, path, change['value'])
        result['status'] = 'applied' if changed else 'noop'
        result['value'] = change['value']
    elif action == 'replace':
        before = get_value(config, path)
        after = change['to']
        if before == after:
            result['status'] = 'noop'
        else:
            set_value(config, path, after)
            result['status'] = 'applied'
        result['from'] = before
        result['to'] = after
    else:
        raise ValueError(f'Unsupported action: {action}')

    if 'reason' in change:
        result['reason'] = change['reason']
    return result


def backup_config(config: Dict) -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    backup = BACKUP_DIR / f'trading_config.{stamp}.json'
    write_json(backup, config)
    return backup


def append_apply_log(entry: Dict) -> None:
    APPLY_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(APPLY_LOG, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def main() -> None:
    parser = argparse.ArgumentParser(description='Apply proposed Polymarket config patch')
    parser.add_argument('--apply', action='store_true', help='Actually write changes to trading_config.json')
    parser.add_argument('--patch', default=str(PATCH_FILE), help='Path to proposed patch JSON')
    parser.add_argument('--config', default=str(CONFIG_FILE), help='Path to trading config JSON')
    args = parser.parse_args()

    patch_path = Path(args.patch)
    config_path = Path(args.config)

    patch = load_json(patch_path, None)
    if not patch:
        raise SystemExit(f'Patch file missing or empty: {patch_path}')

    config = load_json(config_path, None)
    if config is None:
        raise SystemExit(f'Config file missing: {config_path}')

    proposed = deepcopy(config)
    results = []
    for change in patch.get('changes', []):
        results.append(apply_change(proposed, change))

    applied_count = sum(1 for r in results if r['status'] == 'applied')
    noop_count = sum(1 for r in results if r['status'] == 'noop')

    if not args.apply:
        print(f'dry_run=true patch={patch_path} config={config_path} applied={applied_count} noop={noop_count}')
        for row in results:
            print(json.dumps(row, ensure_ascii=False))
        return

    backup = backup_config(config)
    write_json(config_path, proposed)
    log_entry = {
        'applied_at': datetime.now().isoformat(timespec='seconds'),
        'patch_file': str(patch_path),
        'config_file': str(config_path),
        'backup_file': str(backup),
        'results': results,
    }
    append_apply_log(log_entry)
    print(f'dry_run=false patch={patch_path} config={config_path} backup={backup} applied={applied_count} noop={noop_count}')


if __name__ == '__main__':
    main()
