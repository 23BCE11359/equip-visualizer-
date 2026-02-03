import urllib.request

urls = [
    'http://127.0.0.1:8000/',
    'http://127.0.0.1:8000/status/',
    'http://127.0.0.1:8000/api/'
]

for u in urls:
    try:
        r = urllib.request.urlopen(u, timeout=10)
        body = r.read(400).decode('utf-8', 'ignore')
        print('---', u, 'Status', r.getcode())
        print(body)
    except Exception as e:
        print('---', u, 'ERROR', repr(e))
