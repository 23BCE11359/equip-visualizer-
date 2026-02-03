"""Simple CI script to upload sample CSV to running backend using the demo token.

Usage: python scripts/ci_e2e_upload.py

It expects a file 'demo_output.txt' at repo root containing the output from the
`python manage.py create_demo_user` command (created by the CI job).
"""
import re
import sys
import os
import requests

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO_OUT = os.path.join(REPO_ROOT, 'demo_output.txt')
CSV_PATH = os.path.join(REPO_ROOT, 'frontend-desktop', 'test_data', 'sample_upload.csv')
API_BASE = 'http://127.0.0.1:8000/api'

if not os.path.exists(DEMO_OUT):
    print('demo_output.txt not found; ensure create_demo_user was run')
    sys.exit(2)

with open(DEMO_OUT, 'r') as fh:
    out = fh.read()

m = re.search(r'Token:\s*([a-f0-9]+)', out)
if not m:
    print('Could not find token in demo_output.txt')
    print(out)
    sys.exit(2)

token = m.group(1)
print('Using token:', token)

url = API_BASE + '/upload/'
headers = {'Authorization': f'Token {token}'}
with open(CSV_PATH, 'rb') as fh:
    files = {'file': ('sample_upload.csv', fh, 'text/csv')}
    r = requests.post(url, files=files, headers=headers, timeout=30)
    print('Status:', r.status_code)
    try:
        print('Resp JSON:', r.json())
    except Exception:
        print('Resp text:', r.text)
    if r.status_code != 200:
        sys.exit(1)
    created = r.json().get('created', 0)
    if created <= 0:
        print('No rows created; failing')
        sys.exit(1)
    print('Created rows:', created)
    sys.exit(0)
