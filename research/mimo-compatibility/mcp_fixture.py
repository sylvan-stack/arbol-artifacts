"""Minimal real MCP stdio peer with observable fixture-only side effects."""
import json
import os
import signal
from pathlib import Path
import sys
import time

root = Path(sys.argv[1])
if '--ignore-term' in sys.argv:
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
(root / 'mcp.pid').write_text(str(os.getpid()))
for line in sys.stdin:
    try:
        request = json.loads(line)
        method = request.get('method')
        if method == 'initialize':
            result = {'protocolVersion': '2024-11-05', 'capabilities': {'tools': {}},
                      'serverInfo': {'name': 'arbol-compatibility-fixture', 'version': '1'}}
        elif method == 'tools/list':
            result = {'tools': [{'name': 'echo', 'description': 'Return the fixture sentinel.',
                                'inputSchema': {'type': 'object', 'properties': {'text': {'type': 'string'}}}}]}
        elif method == 'tools/call':
            with (root / 'mcp.calls').open('a') as file:
                file.write(json.dumps(request['params']) + '\n')
            result = {'content': [{'type': 'text', 'text': 'MIMO_MCP_SENTINEL ' +
                                  str(request.get('params', {}).get('arguments', {}).get('text', ''))}]}
        elif method == 'ping':
            result = {}
        else:
            result = {}
        if 'id' in request:
            print(json.dumps({'jsonrpc': '2.0', 'id': request['id'], 'result': result}), flush=True)
    except (ValueError, KeyError):
        pass
if '--ignore-eof' in sys.argv:
    time.sleep(60)
