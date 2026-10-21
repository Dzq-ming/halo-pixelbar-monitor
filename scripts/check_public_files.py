"""Check the tracked release allowlist and common accidental private data."""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent
ROOT_FILES = {'.gitignore','.gitattributes','LICENSE','README.md','SECURITY.md',
              'THIRD_PARTY.md','CONTRIBUTING.md','CHANGELOG.md','pyproject.toml',
              'requirements.txt','config.example.json','Setup.ps1',
              'Start-Monitor.ps1','Start-Monitor.cmd','Stop-Monitor.cmd'}
PREFIXES = ('halo_pixelbar_monitor/','tests/','docs/','.github/','scripts/')
BLOCKED = ('.exe','.dll','.pyd','.zip','.bin','.log','.tmp','.lock','.pyc')
PATTERNS = {
    'personal Windows path': re.compile(r'[A-Za-z]:[\\/](?:Users|code)[\\/]', re.I),
    'credential-like value': re.compile(r'(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----)'),
    'raw USB instance path': re.compile(r'(?:USB|HID)\\VID_[0-9A-F]{4}&PID_[0-9A-F]{4}[^\r\n]*\\[0-9A-F&]{6,}', re.I),
    'runtime telemetry': re.compile(r'"(?:sensor_pid|display_pid|serial_number|download_bps|upload_bps)"\s*:'),
}


def main():
    names = subprocess.check_output(['git','ls-files','--cached','-z'],cwd=ROOT).decode('utf8').split('\0')
    failures=[]
    for name in filter(None,names):
        if name not in ROOT_FILES and not name.startswith(PREFIXES):
            failures.append((name,'file outside release allowlist'))
        if name.endswith(BLOCKED) or '/__pycache__/' in name or name.startswith(('runtime/','lib/','.venv/','vendor/')):
            failures.append((name,'runtime/binary/dependency file'))
        try:
            # Inspect the staged blob, not an unstaged sanitized working copy.
            content=subprocess.check_output(['git','show',f':{name}'],cwd=ROOT).decode('utf-8-sig')
        except UnicodeError:
            failures.append((name,'unexpected binary content'))
            continue
        for label, pattern in PATTERNS.items():
            if pattern.search(content):
                failures.append((name,label))
    for name,label in failures:
        print(f'{name}: {label}')  # Never echo the matched private value.
    if failures:
        return 1
    print(f'Public-file check passed ({sum(bool(n) for n in names)} tracked files).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
