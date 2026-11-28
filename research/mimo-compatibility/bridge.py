"""Research bridge to Arbol Pi's pinned, gated macOS ownership machinery.

Not a Driver. The native executable, permission scan and command text remain
unchanged. A same-basename SHELL shim forwards execution after native checks.
Only this controller holds guard leases; commands never inherit those leases.
Runtime records contain identities, call lineage and outcomes, never environments.
"""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path
import select
import signal
import socket
import stat
import subprocess
import sys
import threading
import time
import uuid

PI_SOURCE = Path('/Users/msix/repos/sylvan-stack/readonly/arbol-pi-driver/src')
sys.path.insert(0, str(PI_SOURCE))
from arbol_pi_driver.guard_client import GuardClient
from arbol_pi_driver.process import current_owner, Owner
from arbol_pi_driver.process_table import group_members
from arbol_pi_driver.state import write_json
from arbol_pi_driver.watcher import WatcherClient

MAX_FRAME = 1024 * 1024


def frame(sock, value):
    data = (json.dumps(value, separators=(',', ':')) + '\n').encode()
    if len(data) > MAX_FRAME:
        raise ValueError('oversized bridge frame')
    sock.sendall(data)


def read_frame(sock):
    result = bytearray()
    while not result.endswith(b'\n'):
        part = sock.recv(1)
        if not part:
            raise EOFError('bridge lease ended')
        result.extend(part)
        if len(result) > MAX_FRAME:
            raise ValueError('oversized bridge frame')
    return json.loads(result)


class Host:
    def __init__(self, root):
        self.root = root
        self.lock = threading.RLock()
        self.closing = threading.Event()
        self.admission = True
        self.threads = []
        self.guards = {}
        self.resources = {}
        self.sequence = 0
        self.owner = current_owner()
        self.nonce = uuid.uuid4().hex
        self.socket_path = '/tmp/mimo-bridge-' + uuid.uuid4().hex + '.sock'
        self.server = socket.socket(socket.AF_UNIX)
        self.server.bind(self.socket_path)
        os.chmod(self.socket_path, 0o600)
        self.server.listen(16)
        self.server.settimeout(.1)
        self.persist('bootstrap')
        self.watcher = WatcherClient(root / 'ledger.json', self.nonce, self.owner)
        self.watcher.admit()
        write_json(root / 'endpoint.json', {'socket': self.socket_path, 'nonce': self.nonce,
                                          'owner': self.owner.json(), 'watcher': self.watcher.owner.json()})

    def persist(self, phase='running', *, closed=False):
        self.sequence += 1
        write_json(self.root / 'ledger.json', {'nonce': self.nonce, 'owner': self.owner.json(),
            'resources': self.resources, 'phase': phase, 'closed': closed,
            'admission': self.admission, 'seq': self.sequence})

    def record(self, kind, **body):
        # Publication is serialized and durable before the corresponding admit.
        self.sequence += 1
        data = {'seq': self.sequence, 'kind': kind, 'at': time.time(), **body}
        with (self.root / 'bridge-events.jsonl').open('a') as stream:
            stream.write(json.dumps(data) + '\n');stream.flush();os.fsync(stream.fileno())

    def publish(self, key, kind, body, call, state='prepared'):
        with self.lock:
            self.resources[key] = {'kind': kind, **body, 'state': state, 'call': call}
            self.persist()
            self.record('published', key=key, resource=self.resources[key])

    def revoke(self, guard, key):
        # Move intentional shutdown out of the watcher's live-helper predicate
        # before EOF lets the guard release its anchor.
        with self.lock:
            for resource_key, resource in self.resources.items():
                if resource_key == key or resource_key.startswith(key + ':'):
                    resource['state'] = 'revoked'
            self.persist('closing' if self.closing.is_set() else 'running')
            self.record('lease_revoked', key=key)
            guard.revoke()

    def admit(self, guard, key, op, connection):
        pause = self.root / ('pause-' + (op if isinstance(op, str) else op['op']))
        if pause.exists():
            write_json(self.root / 'paused.json', {'op': op, 'key': key})
            deadline = time.monotonic() + 10
            while pause.exists() and not self.closing.is_set() and time.monotonic() < deadline:
                if connection and select.select([connection], [], [], .05)[0]:
                    if not connection.recv(1, socket.MSG_PEEK):
                        return False
                else:
                    time.sleep(.025)
        with self.lock:
            if not self.admission or self.closing.is_set():
                self.record('admission_rejected', key=key, op=op if isinstance(op, str) else op['op'])
                return False
            operation = op if isinstance(op, str) else op['op']
            resource_key = key + (':group_anchor' if operation == 'admit_anchor' else ':shell' if operation == 'admit_shell' else '')
            self.resources[resource_key]['state'] = 'admitted'
            self.persist()
            guard.send(op if isinstance(op, dict) else {'op': op})
            self.record('admitted', key=key, op=op if isinstance(op, str) else op['op'])
            return True

    def run_guard(self, request, connection=None):
        key = uuid.uuid4().hex
        guard = None
        pipe_read = pipe_write = None
        call = request['call']
        category = request['kind']
        exit_code = 125
        closed = False
        try:
            with self.lock:
                if not self.admission or self.closing.is_set():
                    raise RuntimeError('bridge admission closed')
                if category in ('mcp', 'lsp'):
                    pipe_read, pipe_write = os.pipe()
                    os.set_blocking(pipe_write, False)
                guard = GuardClient(cwd=Path(request['cwd']),
                                    stdin=pipe_read if pipe_read is not None else subprocess.DEVNULL)
                if pipe_read is not None:
                    os.close(pipe_read);pipe_read = None
                self.guards[key] = guard
                self.publish(key, 'shell_guard', {'owner': guard.owner.json(), 'pgid': guard.owner.pid,
                                                'category': category}, call)
            environment = request['env']
            if category != 'native':
                environment['SHELL'] = request.get('real_shell', environment.get('SHELL', '/bin/zsh'))
                # Native bootstrap needs the bridge; user code never inherits it.
                environment = {k: v for k, v in environment.items() if not k.startswith('ARBOL_MIMO_BRIDGE_')}
            configuration = {'op': 'start', 'argv': request['argv'], 'cwd': request['cwd'],
                             'env': environment, 'scale': 1}
            if not self.admit(guard, key, configuration, connection):
                self.revoke(guard, key)
            pending = bytearray()
            incoming = bytearray()
            disconnected = False
            while True:
                if self.closing.is_set() and not guard.control.closed:
                    self.revoke(guard, key)
                if connection and not disconnected and select.select([connection], [], [], 0)[0]:
                    chunk = connection.recv(65536)
                    if not chunk:
                        disconnected = True;self.revoke(guard, key)
                    else:
                        incoming.extend(chunk)
                        if len(incoming) > MAX_FRAME:
                            raise ValueError('oversized client input')
                        while b'\n' in incoming:
                            line, _, rest = incoming.partition(b'\n');incoming[:] = rest
                            value = json.loads(line)
                            if value['op'] == 'stdin' and pipe_write is not None:
                                pending.extend(base64.b64decode(value['data'], validate=True))
                                if len(pending) > MAX_FRAME:
                                    raise ValueError('MCP stdin backpressure exceeded')
                            elif value['op'] == 'stdin_eof' and pipe_write is not None and not pending:
                                os.close(pipe_write);pipe_write = None
                            else:
                                raise ValueError('invalid bridge input')
                if pending and pipe_write is not None:
                    try:
                        count = os.write(pipe_write, pending);del pending[:count]
                    except BlockingIOError:
                        pass
                for kind, payload in guard.read(.025):
                    if kind in ('stdout', 'stderr'):
                        if connection and not disconnected:
                            frame(connection, {'kind': kind, 'data': base64.b64encode(payload).decode()})
                        elif category == 'native':
                            os.write(1 if kind == 'stdout' else 2, payload)
                        continue
                    event, body = payload['type'], payload['body']
                    with self.lock:
                        self.record('guard_' + event, key=key, body=body)
                    if event == 'prepare':
                        part = key + ':' + body['kind']
                        self.publish(part, body['kind'], {'owner': body['owner'], 'pgid': body['pgid']}, call)
                        if not self.admit(guard, key, 'admit_' + ('anchor' if body['kind'] == 'group_anchor' else 'shell'), connection):
                            self.revoke(guard, key)
                    elif event == 'drained':
                        exit_code = body.get('exitCode')
                        exit_code = exit_code if isinstance(exit_code, int) else 125
                        with self.lock:
                            for resource_key, resource in self.resources.items():
                                if resource_key == key or resource_key.startswith(key + ':'):
                                    resource['state'] = 'drained'
                            self.persist('closing' if self.closing.is_set() else 'running')
                        guard.send({'op': 'finish'})
                    elif event == 'closed':
                        closed = True
                if guard.process.poll() is not None and not guard.streams:
                    break
            guard.process.wait(timeout=2)
            with self.lock:
                gone = not group_members(guard.owner.pid)
                for resource_key, resource in self.resources.items():
                    if resource_key == key or resource_key.startswith(key + ':'):
                        resource.update(state='closed' if gone and closed else 'unresolved', closed=gone and closed)
                self.persist('closing' if self.closing.is_set() else 'running')
                self.record('released', key=key, empty=gone, closed=closed, exit=exit_code)
            if not gone or not closed:
                raise RuntimeError('guard ended without an empty acknowledged group')
            if connection and not disconnected:
                frame(connection, {'kind': 'exit', 'code': exit_code, 'key': key, 'empty': True})
        except Exception as error:
            with self.lock:
                self.record('fault', key=key, error=type(error).__name__, message=str(error))
            if connection:
                try:frame(connection, {'kind': 'fault', 'message': str(error)})
                except OSError:pass
            # A helper failure closes the whole run, never yields a successful final.
            self.closing.set()
        finally:
            if guard:
                guard.close()
            for fd in (pipe_read, pipe_write):
                if fd is not None:os.close(fd)
            if connection:connection.close()

    def connection(self, sock):
        sock.settimeout(3)
        try:
            request = read_frame(sock)
            if request.get('nonce') != self.nonce:
                raise ValueError('bridge nonce mismatch')
            op = request.get('op')
            if op in ('seal', 'freeze', 'close', 'status'):
                with self.lock:
                    work = [k for k, x in self.resources.items() if x.get('category') in ('bash', 'formatter') and x['state'] != 'closed']
                    if op == 'seal' and (request.get('watermark') != self.sequence or work):
                        frame(sock, {'sealed': False, 'seq': self.sequence,
                                     'reason': 'work_pending' if work else 'stale_watermark'})
                        sock.close();return
                    if op != 'status':
                        self.admission = False
                        if op == 'close':self.closing.set()
                        self.persist('closing' if op == 'close' else 'sealed')
                        self.record(op)
                    frame(sock, {'seq': self.sequence, 'admission': self.admission,
                                 'resources': self.resources, 'work': work, 'sealed': op == 'seal'})
                sock.close()
            elif op == 'run':
                self.run_guard(request, sock)
            else:
                raise ValueError('invalid bridge operation')
        except Exception as error:
            try:frame(sock, {'kind': 'fault', 'message': str(error)})
            except OSError:pass
            sock.close()

    def run(self, native):
        threading.Thread(target=self.accept, daemon=True).start()
        thread = threading.Thread(target=self.run_guard, args=({'argv': native, 'cwd': os.getcwd(),
            'env': dict(os.environ), 'kind': 'native', 'call': {'resource': 'native-server'},
            'real_shell': os.environ['ARBOL_MIMO_BRIDGE_REAL_SHELL']},))
        self.threads.append(thread);thread.start()
        while not self.closing.is_set() and thread.is_alive():
            if select.select([sys.stdin], [], [], .1)[0] and not os.read(0, 1):
                self.closing.set()
            if self.watcher.process.poll() is not None:
                self.closing.set()
        with self.lock:
            self.admission = False
            self.persist('closing');self.record('close_admission')
        self.closing.set()
        deadline = time.monotonic() + 18
        for item in list(self.threads):
            item.join(max(0, deadline - time.monotonic()))
        with self.lock:
            groups = sorted({x['pgid'] for x in self.resources.values()})
            empty = {str(group): [p.owner.json() for p in group_members(group)] for group in groups}
            clean = not any(empty.values()) and not any(t.is_alive() for t in self.threads)
            fault = any(json.loads(line)['kind'] == 'fault' for line in
                        (self.root / 'bridge-events.jsonl').read_text().splitlines())
            self.persist('terminal', closed=True)
        if self.watcher.process.poll() is None:
            try:
                self.watcher.finish() if clean else self.watcher.revoke()
            except BrokenPipeError:pass
        self.watcher.process.wait(timeout=18)
        observations = json.loads((self.root / 'observations.json').read_text())
        # The watcher may have been doing escalation while the controller joined
        # its handlers. Final evidence must be collected after its terminal ack.
        empty = {str(group): [p.owner.json() for p in group_members(group)] for group in groups}
        clean = not any(empty.values()) and not any(t.is_alive() for t in self.threads)
        bad_outcome = any(e['kind'] in ('guard_closed', 'guard_drained') and
                          e.get('body', {}).get('reason') not in (None, 'lease_closed', 'cancelled')
                          for e in (json.loads(line) for line in
                                    (self.root / 'bridge-events.jsonl').read_text().splitlines()))
        write_json(self.root / 'terminal.json', {'clean': clean and observations['clean'],
            'successful': clean and observations['clean'] and not fault and not bad_outcome and observations['reason'] is None,
            'groups': empty, 'seq': self.sequence, 'watcher': observations})
        self.server.close()
        Path(self.socket_path).unlink(missing_ok=True)

    def accept(self):
        while not self.closing.is_set():
            try:sock, _ = self.server.accept()
            except socket.timeout:continue
            thread = threading.Thread(target=self.connection, args=(sock,))
            self.threads.append(thread);thread.start()


def endpoint():
    return json.loads(Path(os.environ['ARBOL_MIMO_BRIDGE_ENDPOINT']).read_text())


def client(argv, kind='bash', resource=None):
    value = endpoint()
    sock = socket.socket(socket.AF_UNIX);sock.connect(value['socket'])
    environment = dict(os.environ)
    real_shell = environment['ARBOL_MIMO_BRIDGE_REAL_SHELL']
    request = {'op': 'run', 'nonce': value['nonce'], 'argv': argv, 'cwd': os.getcwd(),
               'env': environment, 'real_shell': real_shell, 'kind': kind,
               'call': {'resource': resource} if resource else json.loads(environment.get('ARBOL_MIMO_BRIDGE_CALL', '{}'))}
    frame(sock, request)
    if kind in ('mcp', 'lsp'):
        def stdin():
            try:
                while data := os.read(0, 65536):
                    frame(sock, {'op': 'stdin', 'data': base64.b64encode(data).decode()})
                frame(sock, {'op': 'stdin_eof'})
            except OSError:pass
        threading.Thread(target=stdin, daemon=True).start()
    try:
        while True:
            message = read_frame(sock)
            if message['kind'] in ('stdout', 'stderr'):
                os.write(1 if message['kind'] == 'stdout' else 2, base64.b64decode(message['data']))
            elif message['kind'] == 'exit':
                code = message['code'];return code if code >= 0 else 128 - code
            else:
                return 125
    except (EOFError, OSError):
        return 125
    finally:sock.close()


def admin(path, op, **options):
    value = json.loads(Path(path).read_text())
    with socket.socket(socket.AF_UNIX) as sock:
        sock.connect(value['socket']);frame(sock, {'op': op, 'nonce': value['nonce'], **options})
        return read_frame(sock)


def recover(root):
    """Remove the stale endpoint only after exact owner death and clean audit."""
    value = json.loads((root / 'endpoint.json').read_text())
    if Owner.read(value['owner']).alive():
        raise RuntimeError('refusing recovery of a live controller')
    deadline = time.monotonic() + 16
    while time.monotonic() < deadline:
        observations = json.loads((root / 'observations.json').read_text())
        if observations.get('terminal') and not Owner.read(value['watcher']).alive():break
        time.sleep(.05)
    ledger = json.loads((root / 'ledger.json').read_text())
    groups = {x['pgid'] for x in ledger['resources'].values()}
    clean = observations.get('clean') and not any(group_members(g) for g in groups)
    if not clean or Owner.read(value['watcher']).alive():
        raise RuntimeError('cleanup remains unresolved; preserving endpoint evidence')
    path = Path(value['socket'])
    if path.exists():
        info = path.lstat()
        if not stat.S_ISSOCK(info.st_mode) or info.st_uid != os.getuid() or not str(path).startswith('/tmp/mimo-bridge-'):
            raise RuntimeError('endpoint identity mismatch')
        path.unlink()
    result = {'clean': True, 'ownerDead': True, 'watcherDead': True,
              'groups': {str(g): [] for g in sorted(groups)}, 'endpointRemoved': not path.exists()}
    write_json(root / 'recovery.json', result)
    return result


if __name__ == '__main__':
    if sys.argv[1] == 'host':
        host = Host(Path(sys.argv[2]))
        signal.signal(signal.SIGTERM, lambda *_: host.closing.set())
        signal.signal(signal.SIGINT, lambda *_: host.closing.set())
        host.run(sys.argv[3:])
    elif sys.argv[1] == 'mcp':
        raise SystemExit(client(sys.argv[2:], 'mcp'))
    elif sys.argv[1] == 'resource':
        raise SystemExit(client(sys.argv[4:], sys.argv[2], sys.argv[3]))
    elif sys.argv[1] == 'shell':
        raise SystemExit(client([os.environ['ARBOL_MIMO_BRIDGE_REAL_SHELL'], *sys.argv[2:]]))
