"""Native Mimo compatibility experiments; outputs are private, untracked data."""
from __future__ import annotations

import argparse
import base64
import concurrent.futures
import copy
import hashlib
import http.server
import json
import os
from pathlib import Path
import queue
import re
import shlex
import shutil
import signal
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import uuid

HERE = Path(__file__).resolve().parent
BINARY = Path.home() / '.mimocode/bin/mimo'
PNG = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jED8AAAAASUVORK5CYII='
MODEL = {'providerID': 'arbol-probe', 'modelID': 'probe'}
POOL = concurrent.futures.ThreadPoolExecutor(12)


def write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False))


def wait_for(fn, seconds=12):
    deadline = time.monotonic() + seconds
    last = None
    while time.monotonic() < deadline:
        last = fn()
        if last:
            return last
        time.sleep(.05)
    raise TimeoutError(f'condition not satisfied in {seconds}s; last={last!r}')


def identity(pid):
    result = subprocess.run(['ps', '-p', str(pid), '-o', 'pid=,ppid=,pgid=,lstart=,stat='],
                            capture_output=True, text=True).stdout.strip()
    return result or None


def alive(pid):
    info = identity(pid) if pid else None
    return bool(info and not info.split()[-1].startswith('Z'))


def stop(p):
    if p.poll() is None:
        os.killpg(p.pid, signal.SIGTERM)
        try:
            p.wait(4)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL)
            p.wait(4)


class Peer:
    def __init__(self, output):
        self.output = output
        self.plans = {}
        self.records = []
        self.lock = threading.Lock()
        peer = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                text = json.dumps([m for m in body.get('messages', []) if m.get('role') == 'user'])
                keys = re.findall(r'CASE:([a-zA-Z0-9_-]+)', text)
                key = keys[-1] if keys else 'unrouted'
                with peer.lock:
                    plan = peer.plans.setdefault(key, {'steps': [], 'count': 0})
                    index = plan['count']
                    plan['count'] += 1
                    item = plan['steps'][index] if index < len(plan['steps']) else {'text': 'MIMO_FINAL_' + key}
                    record = {'path': self.path, 'key': key, 'index': index, 'body': body, 'at': time.time()}
                    peer.records.append(record)
                    write(peer.output / f'peer-{len(peer.records):04d}.json', record)
                if callable(item):
                    item = item(body)
                if 'status' in item:
                    self.send_response(item['status'])
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': {'message': 'Synthetic compatibility refusal',
                                                          'type': 'rate_limit_error' if item['status'] == 429 else 'authentication_error'}}).encode())
                    return
                self.send_response(200)
                self.send_header('Content-Type', 'text/event-stream')
                self.end_headers()
                try:
                    self.event({'role': 'assistant'})
                    if item.get('hold'):
                        item['hold'].wait(25)
                    calls = item.get('calls', [])
                    if calls:
                        self.event({'tool_calls': [{'index': i, 'id': 'call_' + uuid.uuid4().hex[:16],
                                    'type': 'function', 'function': {'name': tool, 'arguments': json.dumps(args)}}
                                   for i, (tool, args) in enumerate(calls)]})
                    else:
                        for part in item.get('chunks', [item.get('text', 'MIMO_SYNTHETIC_OK')]):
                            self.event({'content': part})
                    self.event({}, 'tool_calls' if calls else 'stop')
                    self.wfile.write(b'data: [DONE]\n\n')
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    pass

            def event(self, delta, finish=None):
                data = {'id': 'chatcmpl_probe', 'object': 'chat.completion.chunk',
                        'created': int(time.time()), 'model': 'probe',
                        'choices': [{'index': 0, 'delta': delta, 'finish_reason': finish}]}
                if finish:
                    data['usage'] = {'prompt_tokens': 12, 'completion_tokens': 7, 'total_tokens': 19}
                self.wfile.write(('data: ' + json.dumps(data) + '\n\n').encode())
                self.wfile.flush()

        self.server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        self.server.daemon_threads = True
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def plan(self, key, steps):
        self.plans[key] = {'steps': steps, 'count': 0}
        return 'CASE:' + key

    def records_for(self, key):
        return [r for r in self.records if r['key'] == key]


class Native:
    def __init__(self, output, peer, *, profile=True, shared=None, capacity=None, journal=False, leased=False, bridge=False,
                 real_shell='/bin/bash', resource_fixture=False, permission=None):
        self.output = output
        output.mkdir()
        self.peer = peer
        self.leased = leased
        self.bridge = bridge
        self.home = shared.home if shared else output / 'home'
        self.work = shared.work if shared else output / 'work'
        self.home.mkdir(exist_ok=True)
        self.work.mkdir(exist_ok=True)
        self.native_data = self.home / '.local/share/mimocode'
        self.mode = output / 'mode.json'
        write(self.mode, {})
        self.events = []
        self.responses = []
        self.pid_records = []
        self.sse = None
        self.config = {
            'autoupdate': False, 'share': 'disabled', 'snapshot': False,
            'memory': {'disable_write': True, 'cc_index': False},
            'dream': {'auto': False}, 'distill': {'auto': False},
            'enabled_providers': ['arbol-probe'],
            'model': 'arbol-probe/probe', 'small_model': 'arbol-probe/probe',
            'permission': {'*': 'allow'},
            'provider': {'arbol-probe': {'name': 'Synthetic local peer',
                'npm': '@ai-sdk/openai-compatible',
                'options': {'baseURL': f'http://127.0.0.1:{peer.server.server_port}/v1', 'apiKey': 'synthetic-fixture'},
                'models': {'probe': {'name': 'Probe', 'attachment': True, 'tool_call': True,
                    'modalities': {'input': ['text', 'image'], 'output': ['text']},
                    'limit': {'context': 64000, 'output': 2048},
                    'variants': {'low': {'reasoningEffort': 'low'}}}}}}
        }
        self.extra = {
            'HOME': str(self.home), 'MIMOCODE_CONFIG_CONTENT': json.dumps(self.config),
            'MIMOCODE_DISABLE_AUTOUPDATE': '1', 'MIMOCODE_ENABLE_ANALYSIS': 'false',
            'MIMOCODE_DISABLE_LSP_DOWNLOAD': '1', 'MIMOCODE_SERVER_PASSWORD': 'local-synthetic-password',
            'MIMOCODE_ENABLE_QUESTION_TOOL': '1',
            'ARBOL_MIMO_PROBE_MODE': str(self.mode),
            'ARBOL_MIMO_PROBE_HOOK_LOG': str(output / 'hooks.jsonl'),
            'CI': '1',
        }
        if permission is not None:self.config['permission'] = permission
        if bridge:
            self.bridge_root = output / 'bridge';self.bridge_root.mkdir(mode=0o700)
            shell_dir = self.bridge_root / 'shell';shell_dir.mkdir()
            # Same basename retains native shell classification and permissions.
            shim = shell_dir / Path(real_shell).name
            shim.write_text('#!' + sys.executable + ' -B\nimport sys,os\nsys.path.insert(0,' + repr(str(HERE)) + ')\nfrom bridge import client\nraise SystemExit(client([os.environ["ARBOL_MIMO_BRIDGE_REAL_SHELL"], *sys.argv[1:]]))\n')
            shim.chmod(0o700)
            self.extra.update(SHELL=str(shim), ARBOL_MIMO_BRIDGE_REAL_SHELL=real_shell,
                              ARBOL_MIMO_BRIDGE_ENDPOINT=str(self.bridge_root / 'endpoint.json'))
            if resource_fixture:
                for kind, extension in [('formatter', '.mimofmt'), ('lsp', '.mimolsp')]:
                    self.config[kind] = {'fixture': {'extensions': [extension], 'command': [
                        sys.executable, '-B', str(HERE / 'bridge.py'), 'resource', kind, kind + ':fixture',
                        sys.executable, '-B', str(HERE / 'support_fixture.py'), kind, str(output),
                        *(['$FILE'] if kind == 'formatter' else [])]}}
        if capacity:
            self.extra['MIMOCODE_EVENT_QUEUE_CAPACITY'] = str(capacity)
        if journal:
            self.extra['MIMOCODE_EXPERIMENTAL_WORKSPACES'] = '1'
        if not shared:
            self.fixtures(profile)
        elif profile:
            self.config['plugin'] = [str(HERE / 'profile.mjs')]
        self.extra['MIMOCODE_CONFIG_CONTENT'] = json.dumps(self.config)
        self.process = self.launch(['serve', '--port', '0'], 'server')
        lines = queue.Queue()
        def read():
            with (output / 'server.stdout').open('w') as file:
                for line in self.process.stdout:
                    file.write(line);file.flush();lines.put(line)
        threading.Thread(target=read, daemon=True).start()
        deadline = time.monotonic() + 20
        self.base = None
        while time.monotonic() < deadline:
            try:
                line = lines.get(timeout=.25)
            except queue.Empty:
                if self.process.poll() is not None:
                    break
                continue
            match = re.search(r'listening on (http://\S+)', line)
            if match:
                self.base = match.group(1)
                break
        if not self.base:
            stop(self.process)
            raise RuntimeError('native server did not start: ' + str(output / 'server.stderr'))
        self.pid_records.append(identity(self.process.pid))
        self.api('/config')

    def fixtures(self, profile):
        config_dir = self.home / '.config/mimocode'
        config_dir.mkdir(parents=True)
        owner_plugin = config_dir / 'owner.mjs'
        owner_plugin.write_text("export default async function OwnerFixture() { return { 'experimental.chat.system.transform': async (_,o) => {o.system.push('MIMO_OWNER_PLUGIN_SENTINEL');} }; }\n")
        mcp = {'fixture': {'type': 'local', 'command': [sys.executable, str(HERE / 'mcp_fixture.py'), str(self.output)]}}
        if self.bridge:
            mcp['fixture']['command'] = [sys.executable, '-B', str(HERE / 'bridge.py'), 'mcp', *mcp['fixture']['command'], '--ignore-eof', '--ignore-term']
            mcp['fixture']['environment'] = {'ARBOL_MIMO_BRIDGE_CALL': json.dumps({'resource': 'mcp:fixture'})}
        write(config_dir / 'mimocode.json', {'plugin': [str(owner_plugin)], 'mcp': mcp})
        if profile:
            self.config['plugin'] = [str(HERE / 'profile.mjs')]
        (config_dir / 'AGENTS.md').write_text('MIMO_GLOBAL_INSTRUCTION_SENTINEL\n')
        (self.work / 'AGENTS.md').write_text('MIMO_PROJECT_INSTRUCTION_SENTINEL\n')
        skill = self.work / '.agents/skills/native-fixture'
        skill.mkdir(parents=True)
        (skill / 'SKILL.md').write_text('---\nname: native-fixture\ndescription: Mimo compatibility fixture skill\n---\nMIMO_SKILL_SENTINEL\n')
        (self.work / 'ordinary.txt').write_text('MIMO_ORDINARY_FILE_SENTINEL\n')
        memory = self.native_data / 'memory/global'
        memory.mkdir(parents=True)
        (memory / 'MEMORY.md').write_text('# Native memory\n\nZEBRAMIMO_MEMORY_SENTINEL is a retained fact.\n')

    def launch(self, args, name):
        clean = {'HOME': str(Path.home()), 'USER': os.environ['USER'],
                 'LOGNAME': os.environ.get('LOGNAME', os.environ['USER']), 'TERM': 'xterm-256color'}
        native = [str(BINARY), *args]
        if self.bridge and name == 'server':
            native = [sys.executable, '-B', str(HERE / 'bridge.py'), 'host', str(self.bridge_root), *native]
        elif self.leased and name == 'server':
            native = [sys.executable, str(HERE / 'lease.py'), str(self.output / 'lease-native.json'), *native]
            native = [sys.executable, str(HERE / 'controller.py'), str(self.output / 'lease-controller.json'), *native]
        command = shlex.join(['env', *[f'{k}={v}' for k, v in self.extra.items()], *native])
        err = (self.output / (name + '.stderr')).open('w')
        return subprocess.Popen(['/bin/zsh', '-l', '-i', '-c', 'exec ' + command],
                                cwd=self.work, env=clean, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=err, text=True, start_new_session=True)

    def command(self, args, name):
        p = self.launch(args, name)
        try:
            out, _ = p.communicate(timeout=25)
            (self.output / (name + '.stdout')).write_text(out)
            return p.returncode, out
        finally:
            stop(p)

    def api(self, path, body=None, *, timeout=25, method=None):
        req = urllib.request.Request(self.base + path,
            data=None if body is None else json.dumps(body).encode(), method=method,
            headers={'Authorization': 'Basic ' + base64.b64encode(b'mimocode:local-synthetic-password').decode(),
                     'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                raw = response.read()
                result = json.loads(raw) if raw.strip() else None
                self.responses.append({'path': path, 'status': response.status, 'data': result})
                return result
        except urllib.error.HTTPError as error:
            raw = error.read().decode()
            self.responses.append({'path': path, 'status': error.code, 'error': raw})
            raise RuntimeError(f'{path}: HTTP {error.code}: {raw[:500]}') from None

    def subscribe(self, consume=True):
        req = urllib.request.Request(self.base + '/event', headers={
            'Authorization': 'Basic ' + base64.b64encode(b'mimocode:local-synthetic-password').decode()})
        self.sse = urllib.request.urlopen(req, timeout=30)
        def read():
            try:
                for raw in self.sse:
                    if raw.startswith(b'data:'):
                        self.events.append(json.loads(raw[5:]))
            except (OSError, ValueError):
                pass
        if consume:
            threading.Thread(target=read, daemon=True).start()

    def session(self, title='Compatibility fixture'):
        return self.api('/session', {'title': title})

    def prompt(self, key, steps=(), *, session=None, **options):
        sid = session or self.session()['id']
        marker = self.peer.plan(key, list(steps))
        body = {'model': MODEL, 'parts': [{'type': 'text', 'text': marker}], **options}
        return self.api('/session/' + sid + '/message', body)

    def async_prompt(self, *args, **kwargs):
        return POOL.submit(self.prompt, *args, **kwargs)

    def set_mode(self, **mode):
        write(self.mode, mode)

    def close(self):
        if self.bridge:
            if self.process.poll() is None:
                self.process.stdin.close()
                self.process.wait(20)
            if not (self.bridge_root / 'terminal.json').exists():
                from bridge import recover
                recover(self.bridge_root)
        else:
            stop(self.process)
        if self.sse:
            try:
                self.sse.close()
            except OSError:
                pass
        write(self.output / 'events.json', self.events)
        write(self.output / 'responses.json', self.responses)
        write(self.output / 'identities.json', self.pid_records)
        # Only fixture process identities learned from our private files are eligible.
        for file in [self.output / 'mcp.pid', *self.work.glob('*.pid')]:
            try:
                pid = int(file.read_text())
                before = identity(pid)
                argv = subprocess.run(['ps', '-p', str(pid), '-o', 'args='], capture_output=True, text=True).stdout
                owned = str(self.work) in argv or ('mcp_fixture.py' in argv and str(self.output) in argv)
                if before and owned:
                    self.pid_records.append({'cleanup': str(file), 'identity': before})
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(.05)
            except (OSError, ValueError):
                pass


class Checks:
    def __init__(self):
        self.items = []

    def add(self, name, passed, detail=None):
        self.items.append({'name': name, 'passed': bool(passed), 'detail': detail})
        print(json.dumps(self.items[-1]), flush=True)


def system_text(record):
    return '\n'.join(str(m.get('content', '')) for m in record['body']['messages'] if m['role'] == 'system')


def tool_parts(message):
    return [p for p in (message or {}).get('parts', []) if p['type'] == 'tool']


def all_tool_parts(native, message):
    sid = message.get('info', {}).get('sessionID')
    if not sid:
        return tool_parts(message)
    return [p for m in native.api('/session/' + sid + '/message') for p in m['parts'] if p['type'] == 'tool']


def core(root, peer, checks):
    n = Native(root / 'native', peer)
    try:
        preserved = [n.home / '.config/mimocode/AGENTS.md', n.home / '.config/mimocode/mimocode.json',
                     n.home / '.config/mimocode/owner.mjs', n.work / 'AGENTS.md',
                     n.work / '.agents/skills/native-fixture/SKILL.md', n.native_data / 'memory/global/MEMORY.md']
        original = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in preserved}
        n.subscribe()
        msg = n.prompt('baseline')
        baseline = peer.records_for('baseline')[-1]
        payload = json.dumps(baseline['body'])
        checks.add('normal_project_instructions', 'MIMO_PROJECT_INSTRUCTION_SENTINEL' in payload)
        checks.add('normal_global_instructions', 'MIMO_GLOBAL_INSTRUCTION_SENTINEL' in payload)
        checks.add('normal_owner_plugin', 'MIMO_OWNER_PLUGIN_SENTINEL' in payload)
        checks.add('native_memory_instructions_present_under_disable_write', '# Memory system' in payload)
        checks.add('native_real_tool_list', len(baseline['body'].get('tools', [])) > 5)
        n.prompt('memory_positive', [{'calls': [('memory', {'query': 'ZEBRAMIMO_MEMORY_SENTINEL'})]}])
        positive = json.dumps(peer.records_for('memory_positive')[-1]['body'])
        checks.add('memory_positive_control_retrieves_existing_fact', 'ZEBRAMIMO_MEMORY_SENTINEL' in positive and 'is a retained fact' in positive)
        n.set_mode(memoryOff=True, context='MIMO_ARBOL_CONTEXT_A')
        sid = n.session()['id']
        n.prompt('profile_a', session=sid)
        a = peer.records_for('profile_a')[-1]
        n.set_mode(memoryOff=True, context='MIMO_ARBOL_CONTEXT_B')
        n.prompt('profile_b', session=sid)
        b = peer.records_for('profile_b')[-1]
        checks.add('system_context_exact_once', system_text(a).count('MIMO_ARBOL_CONTEXT_A') == 1)
        checks.add('changed_context_same_native_session', system_text(b).count('MIMO_ARBOL_CONTEXT_B') == 1 and 'MIMO_ARBOL_CONTEXT_A' not in system_text(b))
        n.prompt('profile_b_fresh')
        fresh = peer.records_for('profile_b_fresh')[-1]
        checks.add('changed_context_rebuild_uses_new_system', system_text(fresh).count('MIMO_ARBOL_CONTEXT_B') == 1 and 'MIMO_ARBOL_CONTEXT_A' not in system_text(fresh))
        checks.add('memory_prompt_removed_preserving_native_base', '# Memory system' not in system_text(b) and 'MiMoCode' in system_text(b))
        checks.add('memory_path_reminder_removed', 'Memory paths for this conversation' not in json.dumps(b['body']))
        checks.add('profile_preserves_instruction_and_owner_plugin', all(x in json.dumps(b['body']) for x in ['MIMO_PROJECT_INSTRUCTION_SENTINEL', 'MIMO_OWNER_PLUGIN_SENTINEL']))
        negative = n.prompt('memory_negative', [{'calls': [('memory', {'query': 'ZEBRAMIMO_MEMORY_SENTINEL'})]}])
        checks.add('memory_search_cancelled', any(p['state'].get('metadata', {}).get('cancelled') for p in all_tool_parts(n, negative)))
        checks.add('memory_fact_not_recalled', 'is a retained fact' not in json.dumps(peer.records_for('memory_negative')[-1]['body']))
        def resources(body):
            names = [t['function']['name'] for t in body.get('tools', [])]
            mcp = next((s for s in names if s.endswith('fixture_echo')), None)
            calls = [('skill', {'name': 'native-fixture'}), ('read', {'file_path': str(n.work / 'ordinary.txt')})]
            calls.append((mcp, {'text': 'resource-positive'}) if mcp else ('mcp_tool_use', {'name': 'fixture_echo', 'arguments': {'text': 'resource-positive'}}))
            return {'calls': calls}
        n.prompt('resources', [resources])
        data = json.dumps(peer.records_for('resources')[-1]['body'])
        checks.add('memory_off_preserves_skill', 'MIMO_SKILL_SENTINEL' in data)
        checks.add('memory_off_preserves_ordinary_read', 'MIMO_ORDINARY_FILE_SENTINEL' in data)
        checks.add('memory_off_preserves_mcp_call', 'MIMO_MCP_SENTINEL' in data)
        memory_target = n.native_data / 'memory/global/notes.md'
        n.prompt('memory_write', [{'calls': [('write', {'file_path': str(memory_target), 'content': 'MIMO_SHOULD_NOT_WRITE_MEMORY'})]}])
        checks.add('native_memory_write_guard', not memory_target.exists())
        n.set_mode(memoryOff=True, context='MIMO_ARBOL_CONTEXT_B', noTools=True)
        search = n.prompt('no_tools_search', [{'calls': [('mcp_tool_search', {'query': 'fixture echo'})]}], tools={'*': False})
        search_parts = all_tool_parts(n, search)
        checks.add('no_tools_mcp_search_cancelled_before_execution', any(p['tool'] == 'mcp_tool_search' and p['state'].get('metadata', {}).get('cancelled') for p in search_parts), search_parts)
        marker = n.work / 'forbidden.txt'
        no_tools = n.prompt('no_tools', [{'calls': [
            ('bash', {'command': 'touch ' + shlex.quote(str(marker)), 'description': 'Fixture side effect'}),
            ('write', {'file_path': str(marker), 'content': 'forbidden'}),
            ('read', {'file_path': str(n.work / 'ordinary.txt')}),
            ('mcp_tool_use', {'name': 'fixture_echo', 'arguments': {'text': 'forbidden'}}),
            ('actor', {'operation': {'action': 'spawn', 'description': 'Fixture child', 'prompt': 'CASE:forbiddenchild', 'subagent_type': 'general'}})
        ]}], tools={'*': False})
        checks.add('no_tools_no_file_side_effect', not marker.exists())
        checks.add('no_tools_no_file_read', 'MIMO_ORDINARY_FILE_SENTINEL' not in json.dumps(peer.records_for('no_tools')[-1]['body']))
        checks.add('no_tools_no_mcp_execution', not (n.output / 'mcp.calls').exists() or 'forbidden' not in (n.output / 'mcp.calls').read_text())
        checks.add('no_tools_no_child_request', not peer.records_for('forbiddenchild'))
        checks.add('no_tools_native_outcomes', True, [{'name': p['tool'], 'state': p['state']} for p in all_tool_parts(n, no_tools)])
        n.set_mode(memoryOff=True)
        question = {'questions': [{'question': 'Choose a fixture color', 'header': 'Fixture',
                                  'options': [{'label': 'Blue', 'description': 'Synthetic blue'}, {'label': 'Red', 'description': 'Synthetic red'}]}]}
        sid = n.session()['id']
        pending = n.async_prompt('question', [{'calls': [('question', question)]}], session=sid)
        q = wait_for(lambda: next((q for q in n.api('/question') if q['sessionID'] == sid), None))
        checks.add('question_correlates_native_tool', bool(q.get('tool', {}).get('callID')))
        n.api('/question/' + q['id'] + '/reply', {'answers': [['Blue']]})
        pending.result(15)
        checks.add('question_answer_reaches_model', 'Blue' in json.dumps(peer.records_for('question')[-1]['body']))
        checks.add('question_closed_after_answer', not any(q['sessionID'] == sid for q in n.api('/question')))
        sid = n.session()['id']
        pending = n.async_prompt('question_abort', [{'calls': [('question', question)]}], session=sid)
        wait_for(lambda: any(q['sessionID'] == sid for q in n.api('/question')))
        n.api('/session/' + sid + '/abort', {})
        pending.result(15)
        checks.add('question_cancel_withdraws_pending', not any(q['sessionID'] == sid for q in n.api('/question')))
        # Deliberately collect durable records after the run: this models a lost live stream.
        sync = n.api('/sync/history', {})
        write(root / 'sync-history.json', sync)
        groups = {}
        for event in sync:
            groups.setdefault(event['aggregate_id'], []).append(event['seq'])
        checks.add('durable_sync_sequences_contiguous', bool(groups) and all(v == list(range(v[0], v[-1] + 1)) for v in groups.values()))
        states = [e for e in sync if 'part' in e.get('type', '')]
        checks.add('durable_sync_has_tool_transitions', any('running' in json.dumps(e) for e in states) and any('completed' in json.dumps(e) for e in states))
        checks.add('live_events_include_tool_starts', any(e.get('type') == 'message.part.updated' and e.get('properties', {}).get('part', {}).get('state', {}).get('status') == 'running' for e in n.events))
        checks.add('owner_settings_instructions_plugin_skill_memory_files_unchanged', all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == digest for p, digest in original.items()))
    finally:
        n.close()


def native_id(prefix, index):
    return prefix + '_' + f'{int(time.time()*1000)-10000+index:014x}' + uuid.uuid4().hex[:12]


def history(root, peer, checks):
    n = Native(root / 'native', peer)
    try:
        n.set_mode(memoryOff=True, context='MIMO_HISTORY_CONTEXT')
        template = n.session()
        info = {**template, 'id': native_id('ses', 0), 'slug': 'arbol-completed-history', 'title': 'Imported completed history'}
        sid = info['id'];uid = native_id('msg', 0);aid = native_id('msg', 1)
        now = int(time.time()*1000) - 8000
        user = {'id': uid, 'sessionID': sid, 'role': 'user', 'time': {'created': now}, 'agent': 'build', 'model': MODEL}
        assistant = {'id': aid, 'sessionID': sid, 'role': 'assistant', 'time': {'created': now+1, 'completed': now+3},
                     'parentID': uid, 'modelID': 'probe', 'providerID': 'arbol-probe', 'mode': 'build', 'agent': 'build',
                     'path': {'cwd': str(n.work), 'root': str(n.work)}, 'cost': 0,
                     'tokens': {'input': 4, 'output': 3, 'reasoning': 0, 'cache': {'read': 0, 'write': 0}}, 'finish': 'stop'}
        def part(mid, **content):
            return {'id': native_id('prt', len(content)), 'sessionID': sid, 'messageID': mid, **content}
        fixture = {'info': info, 'messages': [
            {'info': user, 'parts': [part(uid, type='text', text='MIMO_HISTORY_USER'),
                                   part(uid, type='file', mime='image/png', filename='prior.png', url='data:image/png;base64,'+PNG)]},
            {'info': assistant, 'parts': [part(aid, type='tool', callID='call_history_shell', tool='bash',
                state={'status': 'completed', 'input': {'command': 'printf MIMO_HISTORY_SHELL', 'description': 'Prior completed command'},
                       'output': 'MIMO_HISTORY_SHELL_RESULT', 'title': 'Prior shell', 'metadata': {'exit': 0},
                       'time': {'start': now+1, 'end': now+2}}),
                part(aid, type='tool', callID='call_history_failed', tool='bash', state={'status': 'error',
                    'input': {'command': 'false', 'description': 'Prior failed command'},
                    'error': 'MIMO_HISTORY_FAILURE_RESULT', 'time': {'start': now+2, 'end': now+3}}),
                part(aid, type='text', text='MIMO_HISTORY_ASSISTANT')]}]}
        file = root / 'import.json';write(file, fixture)
        count = len(peer.records)
        code, stdout = n.command(['import', str(file)], 'history-import')
        checks.add('native_import_completed_history', code == 0, stdout[-500:])
        checks.add('native_import_does_not_infer', len(peer.records) == count)
        if code != 0:
            return
        restored = n.api('/session/' + sid + '/message')
        checks.add('history_native_parts_retained', any(p['type'] == 'tool' and p.get('callID') == 'call_history_shell' for m in restored for p in m['parts']))
        n.prompt('history_resume', session=sid, parts=[{'type': 'text', 'text': peer.plan('history_resume', [])},
                            {'type': 'file', 'mime': 'image/png', 'filename': 'current.png', 'url': 'data:image/png;base64,'+PNG}])
        body = peer.records_for('history_resume')[-1]['body']
        payload = json.dumps(body)
        checks.add('history_text_roles_reach_model', all(x in payload for x in ['MIMO_HISTORY_USER', 'MIMO_HISTORY_ASSISTANT']))
        checks.add('history_native_tool_call_reaches_model', 'call_history_shell' in payload and 'MIMO_HISTORY_SHELL_RESULT' in payload)
        checks.add('history_failed_tool_reaches_model', 'call_history_failed' in payload and 'MIMO_HISTORY_FAILURE_RESULT' in payload)
        images = sum(1 for m in body['messages'] for p in (m.get('content') if isinstance(m.get('content'), list) else []) if p.get('type') == 'image_url')
        checks.add('history_prior_and_current_images_reach_model', images == 2, images)
        n.prompt('history_followup', session=sid)
        checks.add('history_followup_retains_prior_turn', 'MIMO_FINAL_history_resume' in json.dumps(peer.records_for('history_followup')[-1]['body']))
        forked = n.api('/session/' + sid + '/fork', {})
        n.prompt('history_fork', session=forked['id'])
        checks.add('native_fork_preserves_history', 'MIMO_HISTORY_USER' in json.dumps(peer.records_for('history_fork')[-1]['body']))
        # Rebuild an edited branch with fresh native identities and no pending queue.
        edited = copy.deepcopy(fixture)
        new_sid = native_id('ses', 20);edited['info']['id'] = new_sid
        ids = {m['info']['id']: native_id('msg', 30+i) for i, m in enumerate(edited['messages'])}
        for m in edited['messages']:
            m['info']['sessionID'] = new_sid
            m['info']['id'] = ids[m['info']['id']]
            if 'parentID' in m['info']:m['info']['parentID'] = ids[m['info']['parentID']]
            for p in m['parts']:
                p['sessionID'] = new_sid
                p['messageID'] = m['info']['id']
                p['id'] = native_id('prt', 30)
                if p['type'] == 'text' and p['text'] == 'MIMO_HISTORY_USER':p['text'] = 'MIMO_HISTORY_EDITED'
        file = root / 'edited.json';write(file, edited)
        code, out = n.command(['import', str(file)], 'history-edited')
        checks.add('edited_history_import', code == 0, out[-200:])
        if code == 0:
            n.prompt('history_edited', session=new_sid)
            payload = json.dumps(peer.records_for('history_edited')[-1]['body'])
            checks.add('edited_history_replaces_prior_text', 'MIMO_HISTORY_EDITED' in payload and 'MIMO_HISTORY_USER' not in payload)
        # Native deletion does not prevent reconstructing from the caller's saved input.
            n.api('/session/' + new_sid, method='DELETE')
            code, out = n.command(['import', str(file)], 'history-rebuilt')
            checks.add('missing_conversation_rebuilt_from_caller_history', code == 0, out[-200:])
    finally:
        n.close()


def ownership(root, peer, checks):
    n = Native(root / 'native', peer, profile=False)
    other = None
    try:
        n.subscribe()
        other = Native(root / 'concurrent', peer, profile=False, shared=n)
        hold = threading.Event()
        sid = n.session()['id']
        pending = n.async_prompt('concurrent_hold', [{'hold': hold, 'text': 'FIRST_COMPLETED'}], session=sid)
        wait_for(lambda: peer.records_for('concurrent_hold'))
        other.prompt('concurrent_other')
        checks.add('same_home_concurrent_distinct_sessions', bool(peer.records_for('concurrent_other')) and not pending.done())
        hold.set();pending.result(15)
        foreground = n.work / 'foreground.pid'
        script = n.work / 'foreground.py'
        script.write_text('import os,time\nfrom pathlib import Path\nPath('+repr(str(foreground))+').write_text(str(os.getpid()))\ntime.sleep(40)\n')
        sid = n.session()['id']
        pending = n.async_prompt('foreground', [{'calls': [('bash', {'command': shlex.join([sys.executable, str(script)]), 'description': 'Owned fixture foreground'})]}], session=sid)
        pid = int(wait_for(lambda: foreground.read_text() if foreground.exists() else None))
        n.pid_records.append({'foreground': identity(pid)})
        n.api('/session/' + sid + '/abort', {})
        pending.result(15)
        time.sleep(.3)
        checks.add('native_abort_foreground_process_gone', not alive(pid), identity(pid))
        other.prompt('other_after_abort')
        checks.add('cancellation_does_not_stop_other_native_session', bool(peer.records_for('other_after_abort')))
        background = n.work / 'background.pid'
        script = n.work / 'background.py'
        script.write_text('import os,time\nfrom pathlib import Path\nPath('+repr(str(background))+').write_text(str(os.getpid()))\ntime.sleep(40)\n')
        sid = n.session()['id']
        command = shlex.join([sys.executable, str(script)]) + ' </dev/null >/dev/null 2>&1 &'
        n.prompt('background', [{'calls': [('bash', {'command': command, 'description': 'Background fixture ownership'})]}], session=sid)
        pid = int(wait_for(lambda: background.read_text() if background.exists() else None))
        n.pid_records.append({'background': identity(pid)})
        status = n.api('/session/status')
        checks.add('native_idle_means_all_background_work_ended', not alive(pid), {'status': status.get(sid), 'background': identity(pid)})
        n.process.stdin.close()
        time.sleep(.4)
        checks.add('native_server_stops_on_controller_eof', n.process.poll() is not None)
        stop(n.process)
        time.sleep(.3)
        checks.add('native_shutdown_cleans_background_descendant', not alive(pid), identity(pid))
        other.prompt('other_survives_shutdown')
        checks.add('private_server_shutdown_preserves_other_server', bool(peer.records_for('other_survives_shutdown')))
    finally:
        if other:other.close()
        n.close()


def errors(root, peer, checks):
    n = Native(root / 'native', peer)
    try:
        n.subscribe()
        n.set_mode(memoryOff=True)
        for status in (401, 403, 429):
            key = 'error_' + str(status)
            sid = n.session()['id']
            pending = n.async_prompt(key, [{'status': status}] * 10, session=sid)
            wait_for(lambda: peer.records_for(key))
            # Allow structured native status to become observable, then explicitly stop.
            time.sleep(.35)
            status_record = n.api('/session/status').get(sid)
            n.api('/session/' + sid + '/abort', {})
            try:result = pending.result(15)
            except Exception as error:result = {'harness_error': str(error)}
            if status == 429 and status_record and status_record.get('next'):
                # Observe beyond the advertised retry deadline while the server stays alive.
                time.sleep(min(4, max(0, status_record['next'] / 1000 - time.time() + .2)))
                checks.add('abort_prevents_advertised_rate_limit_retry', len(peer.records_for(key)) == 1)
            observed = result.get('info', {}).get('error', {}).get('data', {}).get('statusCode') == status if status != 429 else (status_record or {}).get('type') == 'retry'
            checks.add('structured_error_' + str(status), observed and len(peer.records_for(key)) == 1, {'status': status_record, 'reply': result, 'requests': len(peer.records_for(key))})
        before = len(peer.records)
        try:
            result = n.api('/session/' + n.session()['id'] + '/message', {'model': {'providerID': 'missing-provider', 'modelID': 'missing'}, 'parts': [{'type': 'text', 'text': 'CASE:missing_model'}]})
            native_errors = wait_for(lambda: [e for e in n.events if e['type'] == 'session.error' and 'Model not found' in json.dumps(e)], seconds=3)
            checks.add('invalid_model_refused_before_inference', len(peer.records) == before and bool(native_errors), {'reply': result, 'native_errors': native_errors})
        except Exception as error:
            checks.add('invalid_model_refused_before_inference', len(peer.records) == before, str(error))
        n.prompt('variant', variant='low')
        checks.add('selected_variant_reaches_provider', peer.records_for('variant')[-1]['body'].get('reasoning_effort') == 'low', peer.records_for('variant')[-1]['body'].get('reasoning_effort'))
        n.prompt('unknown_variant', variant='not-a-real-variant')
        checks.add('native_rejects_unknown_variant', not peer.records_for('unknown_variant'))
    finally:
        n.close()


def events(root, peer, checks):
    n = Native(root / 'default', peer, capacity=2)
    try:
        n.set_mode(memoryOff=True)
        n.subscribe(consume=False)
        n.prompt('event_pressure', [{'chunks': ['MIMO_EVENT_PRESSURE_' + str(i) + '_' + ('x' * 4096) for i in range(400)]}])
        journal = n.api('/sync/history', {})
        checks.add('default_sync_journal_available', bool(journal), {'events': len(journal)})
        if n.sse:
            n.sse.close();n.sse = None
        n.prompt('event_tools', [{'calls': [('bash', {'command': 'printf MIMO_EVENT_TOOL', 'description': 'Event continuity fixture'})]}])
        rows = [json.loads(line) for line in (n.output / 'hooks.jsonl').read_text().splitlines()]
        records = [x['data'] for x in rows if x['kind'] == 'native_event']
        seq = [x['seq'] for x in records]
        checks.add('public_event_hook_contiguous', bool(seq) and seq == list(range(1, len(seq) + 1)))
        transitions = [x['event'].get('properties', {}).get('part', {}) for x in records if x['event'].get('type') == 'message.part.updated']
        checks.add('public_event_hook_carries_start_and_finish', any(p.get('state', {}).get('status') == 'running' for p in transitions) and any(p.get('state', {}).get('status') == 'completed' for p in transitions))
        checks.add('public_event_hook_carries_complete_text', any('MIMO_EVENT_PRESSURE_399_' in p.get('text', '') for p in transitions))
    finally:
        n.close()
    n = Native(root / 'journal', peer, journal=True)
    try:
        n.set_mode(memoryOff=True)
        n.prompt('journal_tools', [{'calls': [('bash', {'command': 'printf MIMO_JOURNAL_TOOL', 'description': 'Durable event fixture'})]}])
        rows = n.api('/sync/history', {})
        write(root / 'journal-history.json', rows)
        checks.add('experimental_workspace_flag_enables_journal', bool(rows), len(rows))
        parts = [x for x in rows if 'part' in x['type']]
        checks.add('journal_recovers_start_and_finish', any('running' in json.dumps(p) for p in parts) and any('completed' in json.dumps(p) for p in parts))
        cursors = {}
        for x in rows:cursors[x['aggregate_id']] = max(cursors.get(x['aggregate_id'], 0), x['seq'])
        checks.add('journal_cursor_deduplicates_replay', n.api('/sync/history', cursors) == [])
    finally:
        n.close()


def actors(root, peer, checks):
    n = Native(root / 'native', peer)
    try:
        n.subscribe();n.set_mode(memoryOff=True)
        hold = threading.Event();peer.plan('actor_child', [{'hold': hold, 'text': 'MIMO_CHILD_FINAL'}])
        sid = n.session()['id']
        root_reply = n.async_prompt('actor_root', [{'calls': [('actor', {'operation': {'action': 'spawn', 'description': 'Owned fixture actor',
                            'prompt': 'CASE:actor_child', 'subagent_type': 'general'}})]}], session=sid)
        wait_for(lambda: peer.records_for('actor_child'))
        wait_for(lambda: len(peer.records_for('actor_root')) >= 2)
        main_messages = wait_for(lambda: (messages if any(p.get('text') == 'MIMO_FINAL_actor_root' for m in messages for p in m['parts']) else None)
                                  if (messages := n.api('/session/' + sid + '/message')) else None)
        actor_list = n.api('/session/' + sid + '/actors')
        checks.add('root_answer_can_precede_child_settlement', bool(main_messages) and any(x.get('actorID') != 'main' and x.get('status') in ('running', 'pending') for x in actor_list), actor_list)
        n.api('/session/' + sid + '/abort', {})
        time.sleep(.3)
        after = n.api('/session/' + sid + '/actors')
        checks.add('session_abort_stops_actor_execution', all(x.get('status') not in ('running', 'pending') for x in after), after)
        root_reply.result(15)
        all_messages = n.api('/session/' + sid + '/message?agent_id=*')
        checks.add('actor_messages_have_distinct_actor_identity', any(m['info'].get('agentID') not in (None, 'main') for m in all_messages))
        parts = [p for m in all_messages for p in m['parts'] if p['type'] == 'tool' and p['tool'] == 'actor']
        checks.add('spawning_call_retains_child_identity', bool(parts), [{'callID': p.get('callID'), 'metadata': p.get('state', {}).get('metadata')} for p in parts])
        hold.set()
        n.close()
        n = Native(root / 'reopened', peer, shared=n)
        before = len(peer.records_for('actor_child'))
        n.api('/session/' + sid + '/message?agent_id=*')
        time.sleep(.3)
        checks.add('read_after_restart_does_not_restart_actor', len(peer.records_for('actor_child')) == before)
        crash_hold = threading.Event();peer.plan('actor_crash_child', [{'hold': crash_hold, 'text': 'CRASH_CHILD_FINAL'}])
        sid = n.session()['id']
        crash_reply = n.async_prompt('actor_crash_root', [{'calls': [('actor', {'operation': {'action': 'spawn',
            'description': 'Crash fixture actor', 'prompt': 'CASE:actor_crash_child', 'subagent_type': 'general'}})]}], session=sid)
        wait_for(lambda: peer.records_for('actor_crash_child'))
        before = len(peer.records_for('actor_crash_child'))
        os.kill(n.process.pid, signal.SIGKILL);n.process.wait(4)
        crash_hold.set()
        try:crash_reply.result(5)
        except Exception:pass
        n.close()
        n = Native(root / 'after-crash', peer, shared=n)
        n.api('/session/' + sid + '/message?agent_id=*')
        n.prompt('fresh_after_crash')
        checks.add('startup_and_unrelated_prompt_do_not_restart_crashed_actor', len(peer.records_for('actor_crash_child')) == before)
    finally:
        n.close()


def leases(root, peer, checks):
    n = Native(root / 'native', peer, leased=True)
    try:
        n.set_mode(memoryOff=True)
        file = n.work / 'lease_background.pid'
        script = n.work / 'lease_background.py'
        script.write_text('import os,time\nfrom pathlib import Path\nPath('+repr(str(file))+').write_text(str(os.getpid()))\ntime.sleep(40)\n')
        command = shlex.join([sys.executable, str(script)]) + ' </dev/null >/dev/null 2>&1 &'
        n.prompt('lease_background', [{'calls': [('bash', {'command': command, 'description': 'Lease scope fixture'})]}])
        pid = int(wait_for(lambda: file.read_text() if file.exists() else None))
        native_pid = json.loads((n.output / 'lease-native.json').read_text())['pid']
        checks.add('lease_counterexample_background_outside_server_group', os.getpgid(pid) != os.getpgid(native_pid), {'background': identity(pid), 'native': identity(native_pid)})
        os.kill(n.process.pid, signal.SIGKILL)
        n.process.wait(6)
        wait_for(lambda: not alive(native_pid), seconds=6)
        checks.add('owner_sigkill_eof_guard_stops_private_server', not alive(native_pid))
        checks.add('server_only_eof_guard_cleans_native_background_work', not alive(pid), identity(pid))
    finally:
        n.close()


def main():
    from bridge_cases import bridge_background, bridge_cancel, bridge_death, bridge_faults, bridge_races, bridge_support, bridge_actors, bridge_resources, bridge_shells, bridge_permissions
    bridge_functions = (bridge_background, bridge_cancel, bridge_death, bridge_faults, bridge_races, bridge_support, bridge_actors, bridge_resources, bridge_shells, bridge_permissions)
    globals().update({f.__name__: f for f in bridge_functions})
    parser = argparse.ArgumentParser()
    parser.add_argument('--case', choices=['core', 'history', 'ownership', 'errors', 'events', 'actors', 'leases', *[f.__name__ for f in bridge_functions], 'all'], default='all')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(mode=0o700, parents=True, exist_ok=False)
    scripts = args.output / 'scripts';scripts.mkdir()
    for file in HERE.glob('*'):
        if file.is_file():shutil.copy2(file, scripts / file.name)
    write(args.output / 'provenance.json', {'binary': str(BINARY), 'sha256': hashlib.sha256(BINARY.read_bytes()).hexdigest(),
                                         'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                                         'source_revision': 'b8dbe084ed8e77be2f75a85a9c880031aed699c9', 'real_provider_inference': 0})
    from bridge import PI_SOURCE
    write(args.output / 'guard-provenance.json', {'source': str(PI_SOURCE),
        'revision': subprocess.run(['git', '-C', str(PI_SOURCE), 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip(),
        'files': {str(p.relative_to(PI_SOURCE)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (PI_SOURCE / 'arbol_pi_driver').glob('*.py')}})
    checks = Checks();peer = Peer(args.output)
    cases = ['core', 'history', 'ownership', 'errors', 'events', 'actors', 'leases'] if args.case == 'all' else [args.case]
    errors_seen = []
    try:
        for name in cases:
            directory = args.output / name;directory.mkdir()
            try:
                globals()[name](directory, peer, checks)
            except Exception as error:
                import traceback
                record = {'case': name, 'error': str(error), 'traceback': traceback.format_exc()}
                errors_seen.append(record);print(json.dumps(record), flush=True)
    finally:
        peer.server.shutdown()
        write(args.output / 'results.json', {'case': args.case, 'checks': checks.items, 'harness_errors': errors_seen,
                                            'peer_requests': len(peer.records), 'real_provider_inference': 0})
    raise SystemExit(1 if errors_seen else 0)


if __name__ == '__main__':
    main()
