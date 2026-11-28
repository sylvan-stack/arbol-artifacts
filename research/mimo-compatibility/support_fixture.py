"""Native formatter and LSP fixtures; intentionally stubborn support lifetime."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

kind, directory = sys.argv[1:3]
root = Path(directory)
signal.signal(signal.SIGTERM, signal.SIG_IGN)
(root / (kind + '.pid')).write_text(str(os.getpid()))
if kind == 'formatter':
    target = Path(sys.argv[3])
    target.write_text(target.read_text() + '\nMIMO_FORMATTED_SENTINEL\n')
    subprocess.Popen([sys.executable, __file__, 'format_background', directory],
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
elif kind == 'format_background':
    while not (root / 'formatter.release').exists():time.sleep(.02)
elif kind == 'lsp':
    def send(value):
        body = json.dumps({'jsonrpc': '2.0', **value}).encode()
        sys.stdout.buffer.write(('Content-Length: ' + str(len(body)) + '\r\n\r\n').encode() + body)
        sys.stdout.buffer.flush()
    while True:
        headers = {}
        while line := sys.stdin.buffer.readline():
            if line in (b'\r\n', b'\n'):break
            key, value = line.decode().split(':', 1);headers[key.lower()] = value.strip()
        if not headers:
            time.sleep(60);break
        request = json.loads(sys.stdin.buffer.read(int(headers['content-length'])))
        method = request.get('method')
        with (root / 'lsp.requests').open('a') as stream:stream.write(str(method) + '\n')
        if 'id' in request:
            send({'id': request['id'], 'result': {'capabilities': {'textDocumentSync': 1}} if method == 'initialize' else None})
        if method in ('textDocument/didOpen', 'textDocument/didChange'):
            send({'method': 'textDocument/publishDiagnostics', 'params': {
                'uri': request['params']['textDocument']['uri'], 'diagnostics': []}})
