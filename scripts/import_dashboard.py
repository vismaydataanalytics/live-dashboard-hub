"""Prepare only the reviewed HTML output for the public dashboard URL."""
import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AI_START = '/* ============================================================================\n   VISMAY AI'
AI_END = '/* ---------- Channel switch ---------- */'
AI_INIT = "try{ _aiChatInit(); }catch(e){ console.warn('AI chat init failed', e); }"

def prepare(source, root=ROOT):
    source = Path(source).resolve(strict=True)
    raw = source.read_bytes()
    content = raw.decode('utf-8-sig').replace('\r\n', '\n')
    if content.count(AI_START) != 1 or content.count(AI_INIT) != 1:
        raise ValueError('The dashboard AI section changed. Review the new HTML before publishing.')
    start = content.index(AI_START)
    end = content.index(AI_END, start)
    content = content[:start] + '/* AI chat removed from public output. */\n\n' + content[end:]
    content = content.replace(AI_INIT, '')
    # Scan outside inline image encodings to avoid random base64 false positives.
    inspect = re.sub(r'data:image/[^;,]+;base64,[A-Za-z0-9+/=\s]+', '[embedded image]', content)
    for pattern in (r'AI_BACKEND_URL', r'AI_PROXY_KEY', r'\b_ai[A-Z]\w*\s*\(',
                    r'\bfetch\s*\(', r'XMLHttpRequest', r'WebSocket', r'sendBeacon',
                    r'gh[pousr]_[A-Za-z0-9]{20,}', r'AKIA[A-Z0-9]{16}',
                    r'-----BEGIN [A-Z ]*PRIVATE KEY-----', r'sk-(?:proj-|ant-)?[A-Za-z0-9_-]{24,}'):
        if re.search(pattern, inspect):
            raise ValueError('Unexpected AI/network/credential marker remains. Review before publishing.')
    stamp = datetime.fromtimestamp(source.stat().st_mtime, timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    if content.lower().count('</body>') != 1:
        raise ValueError('Expected one complete HTML document')
    footer = '<aside aria-label="Publication details" style="padding:14px 24px;background:#f3ede4;color:#3d3033;font:13px system-ui,sans-serif;text-align:center"><a href="../../">Dashboard hub</a> &middot; Public version: AI disabled.<br>Source HTML generated: ' + stamp + ' &middot; Published build: {{BUILD_TIME}}<br>Version {{COMMIT}}</aside>'
    content = content.replace('</body>', footer + '\n</body>')
    output = root / 'site/dashboards/sample/index.html'
    output.parent.mkdir(parents=True, exist_ok=True)
    encoded = content.encode('utf-8')
    if len(encoded) >= 25 * 1024 * 1024:
        raise ValueError('Prepared HTML exceeds the GitHub browser upload limit; use Git to publish.')
    registry_path = root / 'dashboards.json'
    registry = json.loads(registry_path.read_text(encoding='utf-8'))
    entries = [item for item in registry if item['id'] == 'sample']
    if len(entries) != 1:
        raise ValueError('The permanent dashboard ID sample must exist exactly once')
    entries[0].update(title='Design Performance', description='VISMAY designer sell-through dashboard. Public version with AI disabled.', source_updated_at=stamp)
    output.with_suffix('.html.tmp').write_bytes(encoded)
    output.with_suffix('.html.tmp').replace(output)
    registry_path.with_suffix('.json.tmp').write_text(json.dumps(registry, indent=2) + '\n', encoding='utf-8')
    registry_path.with_suffix('.json.tmp').replace(registry_path)
    print('Prepared Design Performance at the existing /dashboards/sample/ URL.')
    print('AI module removed; filters and charts retained. Original source unchanged.')
    print('Source SHA256: ' + hashlib.sha256(raw).hexdigest())
    print('Prepared HTML: ' + str(output))
    return output

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    args = parser.parse_args()
    prepare(args.source)
