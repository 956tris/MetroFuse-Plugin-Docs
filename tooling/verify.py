"""Validate tracked guide links, JSON/JavaScript examples and API snapshot hashes."""
from pathlib import Path
import hashlib
import json
import re
import subprocess

root = Path(__file__).resolve().parents[1]
files = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split(chr(0))
errors = []
guides = 0
for name in filter(None, files):
    path = root / name
    if path.suffix != '.md':
        continue
    text = path.read_text(encoding='utf-8')
    guides += 1
    if any(ord(c) < 32 and c not in [chr(9), chr(10), chr(13)] for c in text):
        errors.append(name + ': invalid control character')
    for target in re.findall(r'\]\(([^\s)]+)\)', text):
        if '://' in target or target.startswith('#'):
            continue
        target = target.split('#', 1)[0]
        destination = (path.parent / target).resolve()
        relative = destination.relative_to(root).as_posix()
        if not destination.exists() or (destination.is_file() and relative not in files):
            errors.append(name + ': broken or untracked link ' + target)
    for kind, code in re.findall(r'```(json|javascript)\n(.*?)```', text, re.S):
        if kind == 'json':
            try:
                json.loads(code)
            except ValueError:
                errors.append(name + ': invalid JSON example')
        else:
            result = subprocess.run(['node', '--input-type=module', '--check'], input=code, text=True, capture_output=True)
            if result.returncode:
                errors.append(name + ': JavaScript syntax error')
snapshot = json.loads((root / 'reference/snapshot.json').read_text(encoding='utf-8'))
for entry in snapshot['files']:
    data = (root / entry['path']).read_bytes().replace(bytes([13, 10]), bytes([10]))
    if hashlib.sha256(data).hexdigest() != entry['sha256']:
        errors.append(entry['path'] + ': source snapshot mismatch')
if errors:
    raise SystemExit(chr(10).join(errors))
print('Verified', guides, 'tracked guides, code examples, links and API snapshot hashes.')
