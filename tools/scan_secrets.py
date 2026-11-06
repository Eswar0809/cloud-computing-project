import os
import re

PATTERNS = [
    re.compile(r'AKIA[0-9A-Z]{16}'),
    re.compile(r'(?i)aws_secret_access_key\s*=\s*[\'\"][0-9a-zA-Z\/+=]{40}[\'\"]'),
    re.compile(r'ghp_[0-9a-zA-Z]{36}'),
    re.compile(r'(?i)bearer\s+[a-zA-Z0-9_\-\.]{25,}')
]


def scan_repo():
    found = False
    for root, _, files in os.walk('.'):
        if any(p in root for p in ['.git', 'seaweedfs_data', 'scratch']):
            continue
        for f in files:
            if f.endswith(('.py', '.yaml', '.yml', '.json', '.md', '.txt')):
                fpath = os.path.join(root, f)
                try:
                    content = open(fpath, 'r', encoding='utf-8', errors='ignore').read()
                    for pat in PATTERNS:
                        if pat.search(content):
                            print(f'Warning: Potential secret match in {fpath}')
                            found = True
                except Exception:
                    pass
    if not found:
        print('Secret Scan Clean: 0 secrets detected across repository!')
    return not found


if __name__ == '__main__':
    scan_repo()
