"""Real Hermes gateway and tools, controlled by an offline model peer.

No behavior of Hermes is patched. The scripted peer replaces only inference.
Results describe compatibility, not the language model's ability to use tools.
"""
import argparse
import asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import base64
import hashlib
import json
import os
from pathlib import Path
import shlex
import signal
import socket
import struct
import subprocess
import sys
import threading
import time
import traceback
import uuid
import zlib

import psutil
from websockets.asyncio.client import connect


def fixture_png():
    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload))
    rows = (b"\x00" + b"\x80\x20\x40\xff" * 16) * 16
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 16, 16, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b""))


PNG = fixture_png()
IMAGE = "data:image/png;base64," + base64.b64encode(PNG).decode()
MEMORY = "ARBOL_MEMORY_READ_SENTINEL_8b36"
USER_MEMORY = "ARBOL_USER_MEMORY_SENTINEL_837a"
INSTRUCTION = "ARBOL_PROJECT_INSTRUCTION_SENTINEL_a691"
SKILL = "ARBOL_SKILL_SENTINEL_6eca"


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def control(home, verb, params=None):
    pointer = home / "gateway.sock.path"
    endpoint = pointer.read_text().strip() if pointer.exists() else str(home / "gateway.sock")
    with socket.socket(socket.AF_UNIX) as peer:
        peer.settimeout(2)
        peer.connect(endpoint)
        peer.sendall(json.dumps({"protocol": 1, "id": 1, "verb": verb, "params": params or {}}).encode() + b"\n")
        with peer.makefile("rb") as stream:
            response = json.loads(stream.readline())
    if not response.get("ok"):
        raise RuntimeError(response)
    return response["result"]


def user_text(messages):
    for item in reversed(messages):
        if item.get("role") == "user":
            value = item.get("content", "")
            return value if isinstance(value, str) else json.dumps(value)
    return ""


def call(name, arguments, ident):
    return {"id": ident, "type": "function", "function": {"name": name, "arguments": json.dumps(arguments)}}


class ModelPeer(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        body = json.dumps({"data": [{"id": "gpt-4o", "object": "model"}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        with self.server.lock:
            self.server.requests.append(body)
            with (self.server.output / "model-requests.jsonl").open("a") as stream:
                stream.write(json.dumps({"path": self.path, "body": body}) + "\n")
        messages = body.get("messages", [])
        prompt = user_text(messages)
        last_user = max((i for i, m in enumerate(messages) if m.get("role") == "user"), default=-1)
        used_tool = any(m.get("role") == "tool" for m in messages[last_user + 1:])
        message = {"role": "assistant", "content": "PROBE_ACK " + prompt[-120:]}
        mode = next((s for s in self.server.scripts if s in prompt), None)
        if "CHILD_PROBE_TASK" in prompt and not used_tool:
            message = {"role": "assistant", "content": None, "tool_calls": [
                call("terminal", {"command": self.server.child_command}, "probe-child-terminal")]}
        elif mode and not used_tool:
            definition = self.server.scripts[mode]
            message = {"role": "assistant", "content": None, "tool_calls": [
                call(definition[0], definition[1], "probe-" + mode.lower())]}
        finish = "tool_calls" if message.get("tool_calls") else "stop"
        envelope = {"id": "probe-" + uuid.uuid4().hex, "object": "chat.completion", "created": 1,
                    "model": body.get("model", "gpt-4o"), "choices": [
                        {"index": 0, "message": message, "finish_reason": finish}],
                    "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}}
        if body.get("stream"):
            delta = json.loads(json.dumps(message))
            for i, tool in enumerate(delta.get("tool_calls", [])):
                tool["index"] = i
            chunks = [{"id": envelope["id"], "object": "chat.completion.chunk", "created": 1,
                       "model": envelope["model"], "choices": [{"index": 0, "delta": delta, "finish_reason": None}]},
                      {"id": envelope["id"], "object": "chat.completion.chunk", "created": 1,
                       "model": envelope["model"], "choices": [{"index": 0, "delta": {}, "finish_reason": finish}],
                       "usage": envelope["usage"]}]
            payload = ("".join("data: " + json.dumps(chunk) + "\n\n" for chunk in chunks)
                       + "data: [DONE]\n\n").encode()
            content_type = "text/event-stream"
        else:
            payload, content_type = json.dumps(envelope).encode(), "application/json"
        try:
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass


class Client:
    def __init__(self, ws, output, label):
        self.ws, self.output, self.label = ws, output, label
        self.serial = 0
        self.pending = {}
        self.events = []
        self.reader = asyncio.create_task(self.read())

    async def read(self):
        try:
            async for raw in self.ws:
                frame = json.loads(raw)
                with (self.output / (self.label + "-wire.jsonl")).open("a") as log:
                    log.write(json.dumps(frame) + "\n")
                if frame.get("id") in self.pending and ("result" in frame or "error" in frame):
                    future = self.pending.pop(frame["id"])
                    if not future.done():
                        future.set_result(frame)
                elif "method" in frame:
                    self.events.append(frame)
        finally:
            for future in self.pending.values():
                if not future.done():
                    future.set_exception(ConnectionError("Hermes transport closed"))

    async def raw(self, method, **params):
        self.serial += 1
        rid = self.serial
        future = asyncio.get_running_loop().create_future()
        self.pending[rid] = future
        await self.ws.send(json.dumps({"jsonrpc": "2.0", "id": rid, "method": method, "params": params}))
        return await asyncio.wait_for(future, 30)

    async def rpc(self, method, **params):
        frame = await self.raw(method, **params)
        if "error" in frame:
            raise RuntimeError({"method": method, **frame["error"]})
        return frame["result"]

    async def close(self):
        await self.ws.close()
        await self.reader


class Gateway:
    def __init__(self, args, label, *, memory=False, tools=None):
        from hermes_cli.config_defaults import DEFAULT_CONFIG
        self.args = args
        self.output = Path(args.output) / label
        self.output.mkdir(parents=True)
        self.home = self.output / "profile"
        self.workspace = self.output / "workspace"
        self.home.mkdir(mode=0o700)
        self.workspace.mkdir()
        self.peer = ThreadingHTTPServer(("127.0.0.1", 0), ModelPeer)
        self.peer.requests, self.peer.scripts = [], {}
        self.peer.lock, self.peer.output = threading.Lock(), self.output
        self.peer.child_command = ""
        self.thread = threading.Thread(target=self.peer.serve_forever, daemon=True)
        self.thread.start()
        self.model_url = f"http://127.0.0.1:{self.peer.server_port}/v1"
        self.config = {
            "_config_version": DEFAULT_CONFIG["_config_version"],
            "gateway": {"multiplex_profiles": False},
            "model": {"provider": "custom", "default": "gpt-4o", "base_url": self.model_url,
                      "supports_vision": True},
            "auxiliary": {"title_generation": {"enabled": False}, "background_review": {"enabled": False}},
            "memory": {"memory_enabled": memory, "user_profile_enabled": memory},
            "plugins": {"enabled": []},
            "terminal": {"backend": "local", "cwd": str(self.workspace)},
            "platform_toolsets": {"cli": tools if tools is not None else ["terminal", "file", "skills", "memory", "delegation"]},
        }
        if memory:
            peer_script = self.output / "mcp-peer.py"
            peer_script.write_text('''import json,os,pathlib,sys
pathlib.Path(__file__).with_suffix('.pid').write_text(str(os.getpid()))
for line in sys.stdin:
    request=json.loads(line)
    ident=request.get('id')
    if ident is None: continue
    method=request.get('method')
    if method=='initialize': result={'protocolVersion':request['params']['protocolVersion'],'capabilities':{'tools':{}},'serverInfo':{'name':'arbol-probe','version':'1'}}
    elif method=='tools/list': result={'tools':[{'name':'sentinel','description':'ARBOL_MCP_SENTINEL','inputSchema':{'type':'object','properties':{}}}]}
    elif method=='tools/call': result={'content':[{'type':'text','text':'ARBOL_MCP_SENTINEL'}]}
    else: result={}
    print(json.dumps({'jsonrpc':'2.0','id':ident,'result':result}),flush=True)
''')
            self.config["mcp_servers"] = {"arbol-probe": {"command": sys.executable,
                "args": ["-I", "-B", str(peer_script)], "enabled": True}}
        (self.home / "config.yaml").write_text(json.dumps(self.config))
        self.config_digest = hashlib.sha256((self.home / "config.yaml").read_bytes()).hexdigest()
        self.env = {k: os.environ[k] for k in ("HOME", "USER", "LOGNAME", "PATH", "LANG", "TZ", "TERM") if k in os.environ}
        self.env.update(HERMES_HOME=str(self.home), PYTHONUNBUFFERED="1", PYTHONDONTWRITEBYTECODE="1",
                        OPENAI_API_KEY="arbol-loopback-not-a-real-key", OPENAI_BASE_URL=self.model_url)
        self.process = None
        self.clients = []
        self.owned_pids = {}

    async def __aenter__(self):
        self.log = (self.output / "gateway.log").open("w")
        self.process = subprocess.Popen([self.args.hermes, "--run-module", "gateway.run"],
            cwd=self.workspace, env=self.env, stdin=subprocess.DEVNULL, stdout=self.log,
            stderr=subprocess.STDOUT, start_new_session=True)
        deadline = time.monotonic() + 60
        self.descriptor = {}
        while self.process.poll() is None and time.monotonic() < deadline:
            try:
                self.descriptor = await asyncio.to_thread(control, self.home, "identify")
                if self.descriptor.get("state") == "ready":
                    write_json(self.output / "descriptor.json", self.descriptor)
                    return self
            except (OSError, ValueError, RuntimeError):
                pass
            await asyncio.sleep(.1)
        await self.__aexit__(None, None, None)
        raise RuntimeError("Gateway failed to become ready: " + (self.output / "gateway.log").read_text()[-5000:])

    async def client(self, label):
        grant = await asyncio.to_thread(control, self.home, "session-ticket", {
            "profile_id": str(self.home), "instance_id": self.descriptor["instance_id"], "purpose": "interactive"})
        url = self.descriptor["api_origin"].replace("http:", "ws:") + "/api/ws"
        ws = await connect(url, subprotocols=["hermes-gateway-v1", "hermes-gateway-ticket." + grant["ticket"]],
                           max_size=16 * 1024 * 1024)
        client = Client(ws, self.output, label)
        self.clients.append(client)
        return client

    async def create(self, client, **kwargs):
        return await client.rpc("session.create", request_id=uuid.uuid4().hex, source="tool",
            cwd=str(self.workspace), model="gpt-4o", provider="custom", yolo=True, **kwargs)

    async def submit(self, client, sid, text, *, finite=False):
        return await client.rpc("prompt.submit", session_id=sid, input_id=uuid.uuid4().hex,
                                text=text, finite=finite)

    async def receipt(self, client, sid, admission, timeout=40):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            row = await client.rpc("prompt.receipt", session_id=sid, admission_id=admission["admission_id"])
            if row.get("status") == "terminal":
                return row
            await asyncio.sleep(.05)
        raise TimeoutError({"sid": sid, "last_receipt": row})

    async def resources(self, client, sid):
        processes = await client.rpc("process.list", session_id=sid)
        children = await client.rpc("subagent.list", session_id=sid)
        session = await client.rpc("session.resume", session_id=sid)
        live_processes = [p for p in processes["processes"] if p.get("status") == "running"]
        live_children = [c for c in children.get("subagents", [])
                         if c.get("status") in ("running", "pending", "queued", "starting")]
        return {"processes": processes, "children": children, "running": session["running"],
                "pending": session["pending"], "live_processes": live_processes,
                "live_children": live_children,
                "quiescent": not (session["running"] or session["pending"] or live_processes or live_children)}

    async def stop(self, client, sid, admission):
        start = time.monotonic()
        row = await client.rpc("prompt.receipt", session_id=sid, admission_id=admission["admission_id"])
        cancelled = {"already_terminal": True}
        if row["status"] == "queued":
            cancelled = await client.raw("prompt.cancel", session_id=sid, admission_id=admission["admission_id"])
            if "error" in cancelled:
                row = await client.rpc("prompt.receipt", session_id=sid, admission_id=admission["admission_id"])
                if row["status"] == "queued":
                    raise RuntimeError(cancelled)
        if row["status"] == "started":
            cancelled = await client.rpc("session.interrupt", session_id=sid,
                                         execution_generation=row["execution_generation"])
        processes = await client.rpc("process.stop", session_id=sid)
        terminal = await self.receipt(client, sid, admission, timeout=15)
        deadline = start + 15
        while time.monotonic() < deadline:
            resources = await self.resources(client, sid)
            if resources["quiescent"]:
                break
            await asyncio.sleep(.05)
        return {"seconds": time.monotonic() - start, "cancel": cancelled,
                "process_stop": processes, "receipt": terminal, "resources": resources}

    def alive(self, pid):
        try:
            process = psutil.Process(pid)
            expected = self.owned_pids.get(pid)
            return (process.status() != psutil.STATUS_ZOMBIE and process.is_running()
                    and (expected is None or process.create_time() == expected))
        except psutil.NoSuchProcess:
            return False

    def track(self, pid):
        self.owned_pids[pid] = psutil.Process(pid).create_time()

    async def pid(self, path):
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if path.exists():
                pid = int(path.read_text())
                self.track(pid)
                return pid
            await asyncio.sleep(.05)
        raise TimeoutError("Native terminal did not write " + str(path))

    async def __aexit__(self, *exc):
        gateway_forced = False
        for client in self.clients:
            if not client.reader.done():
                await client.close()
        if self.process is not None and self.process.poll() is None:
            self.process.send_signal(signal.SIGINT)
            try:
                await asyncio.to_thread(self.process.wait, 15)
            except subprocess.TimeoutExpired:
                gateway_forced = True
                os.killpg(self.process.pid, signal.SIGKILL)
                await asyncio.to_thread(self.process.wait, 5)
        # Fixture backstop: recorded PIDs originate only in our generated terminal commands.
        fixture_kills = []
        for pid in self.owned_pids:
            if self.alive(pid):
                try:
                    fixture_kills.append(pid)
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
        self.peer.shutdown()
        self.peer.server_close()
        self.thread.join(5)
        if hasattr(self, "log"):
            self.log.close()
        write_json(self.output / "cleanup.json", {
            "gateway_exited": self.process is None or self.process.poll() is not None,
            "gateway_forced_kill": gateway_forced, "fixture_kill_backstop": fixture_kills,
            "owned_pids_alive": [pid for pid in self.owned_pids if self.alive(pid)],
            "config_unchanged": hashlib.sha256((self.home / "config.yaml").read_bytes()).hexdigest() == self.config_digest})


async def smoke(args):
    async with Gateway(args, "smoke", tools=[]) as gateway:
        client = await gateway.client("client")
        session = await gateway.create(client)
        sid = session["session_id"]
        admitted = await gateway.submit(client, sid, "ARBOL_SMOKE")
        receipt = await gateway.receipt(client, sid, admitted)
        snapshot = await client.rpc("session.resume", session_id=sid)
        result = {"receipt": receipt, "reply_saved": "PROBE_ACK ARBOL_SMOKE" in json.dumps(snapshot),
                  "native_model_requests": len(gateway.peer.requests)}
        write_json(gateway.output / "result.json", result)
        assert result["reply_saved"] and receipt.get("outcome") == "completed", result
        return result


def sleeper(path, seconds=300, *, ignore_signals=False):
    code = "import os,time,pathlib,signal;"
    if ignore_signals:
        code += "signal.signal(signal.SIGTERM,signal.SIG_IGN);signal.signal(signal.SIGINT,signal.SIG_IGN);"
    code += "pathlib.Path(" + repr(str(path)) + ").write_text(str(os.getpid()));time.sleep(" + str(seconds) + ")"
    return shlex.quote(sys.executable) + " -I -u -c " + shlex.quote(code)


async def ownership(args):
    async with Gateway(args, "ownership") as gateway:
        a, b = await gateway.client("a"), await gateway.client("b")
        sid_a = (await gateway.create(a))["session_id"]
        sid_b = (await gateway.create(b))["session_id"]
        pidfile_a, pidfile_b = gateway.output / "a.pid", gateway.output / "b.pid"
        gateway.peer.scripts["FOREGROUND_A"] = ("terminal", {"command": sleeper(pidfile_a), "timeout": 180})
        gateway.peer.scripts["BACKGROUND_B"] = ("terminal", {"command": sleeper(pidfile_b, ignore_signals=True), "background": True,
                                                                      "persist_on_release": True})
        run_a = await gateway.submit(a, sid_a, "FOREGROUND_A")
        pid_a = await gateway.pid(pidfile_a)
        run_b = await gateway.submit(b, sid_b, "BACKGROUND_B")
        pid_b = await gateway.pid(pidfile_b)
        native_b = await gateway.receipt(b, sid_b, run_b)
        resources_b = await gateway.resources(b, sid_b)
        stop_a = await gateway.stop(a, sid_a, run_a)
        a_dead, b_alive = not gateway.alive(pid_a), gateway.alive(pid_b)
        b_inventory = await b.rpc("process.list", session_id=sid_b)
        foreign_attempt = None
        if b_inventory["processes"]:
            foreign_attempt = await a.raw("process.kill", session_id=sid_a,
                                           process_id=b_inventory["processes"][0]["session_id"])
        stop_b = await gateway.stop(b, sid_b, run_b)
        child_sid = (await gateway.create(a))["session_id"]
        child_pidfile = gateway.output / "child.pid"
        gateway.peer.child_command = sleeper(child_pidfile)
        gateway.peer.scripts["DELEGATE_PARENT"] = ("delegate_task", {"tasks": [{"goal": "CHILD_PROBE_TASK"}]})
        child_admission = await gateway.submit(a, child_sid, "DELEGATE_PARENT")
        child_pid = await gateway.pid(child_pidfile)
        child_before = await gateway.resources(a, child_sid)
        child_stop = await gateway.stop(a, child_sid, child_admission)
        lease_sid = (await gateway.create(a))["session_id"]
        lease_pidfile = gateway.output / "lease-worker.pid"
        gateway.peer.scripts["LEASE_WORKER"] = ("terminal", {"command": sleeper(lease_pidfile), "timeout": 180})
        lease_admission = await gateway.submit(a, lease_sid, "LEASE_WORKER")
        lease_pid = await gateway.pid(lease_pidfile)
        lease_request = gateway.output / "lease-request.json"
        lease_result = gateway.output / "lease-result.json"
        write_json(lease_request, {"home": str(gateway.home), "session_id": lease_sid, "admission": lease_admission})
        helper = Path(__file__).with_name("lease-source.py")
        with (gateway.output / "lease.log").open("w") as log:
            controller = subprocess.Popen([sys.executable, "-I", "-B", str(helper), "--mode", "controller",
                "--source", args.source, "--probe", str(Path(__file__)), "--request", str(lease_request),
                "--output", str(lease_result)], env=gateway.env, cwd=gateway.workspace,
                stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
            gateway.track(controller.pid)
            ready = Path(str(lease_result) + ".watchdog-ready")
            deadline = time.monotonic() + 30
            while not ready.exists() and time.monotonic() < deadline:
                await asyncio.sleep(.05)
            if not ready.exists():
                raise RuntimeError("Lease helper failed to start")
            watchdog = json.loads(Path(str(lease_result) + ".controller-ready").read_text())["watchdog_pid"]
            gateway.track(watchdog)
            kill_at = time.monotonic()
            controller.kill()
            await asyncio.to_thread(controller.wait, 5)
            deadline = kill_at + 15
            while not lease_result.exists() and time.monotonic() < deadline:
                await asyncio.sleep(.05)
            lease_observation = json.loads(lease_result.read_text()) if lease_result.exists() else {"status": "timeout"}
            lease_observation.update({"controller_sigkill_to_end_seconds": time.monotonic() - kill_at,
                                      "native_worker_dead": not gateway.alive(lease_pid)})
        result = {
            "scoped_cancel": {"a_dead": a_dead, "b_alive_after_a_cancel": b_alive,
                              "stop": stop_a, "foreign_process_refusal": foreign_attempt},
            "background_completion": {"native_receipt": native_b,
                "worker_ignores_sigint_and_sigterm": True,
                "alive_at_native_completion": bool(resources_b["live_processes"]),
                "adapter_withholds_finished": not resources_b["quiescent"],
                "inventory": resources_b, "stop": stop_b, "b_dead": not gateway.alive(pid_b)},
            "subagent_cancel": {"before": child_before, "stop": child_stop,
                                "native_child_dead": not gateway.alive(child_pid)},
            "caller_death": lease_observation,
        }
        result["verdict"] = "pass-in-tested-scope" if (
            a_dead and b_alive and stop_a["seconds"] < 15 and stop_a["resources"]["quiescent"]
            and not gateway.alive(pid_b) and stop_b["resources"]["quiescent"]
            and not resources_b["quiescent"] and not gateway.alive(child_pid)
            and child_stop["resources"]["quiescent"] and lease_observation["status"] == "finished"
            and lease_observation["native_worker_dead"]
            and lease_observation["controller_sigkill_to_end_seconds"] < 15) else "fail"
        write_json(gateway.output / "result.json", result)
        return result


def arbol_history(image=IMAGE):
    return [
        {"type": "message", "role": "user", "text": "HISTORY_USER_SENTINEL", "images": [image]},
        {"type": "tool_call", "name": "shell", "input": {"command": "printf history", "cwd": "/fixture"},
         "result": {"output": "HISTORY_TOOL_RESULT_SENTINEL", "exitCode": 0}},
        {"type": "tool_call", "name": "shell", "input": {"command": "exit 7", "cwd": "/fixture"},
         "result": {"output": "HISTORY_FAILURE_SENTINEL", "exitCode": 7}},
        {"type": "message", "role": "assistant", "text": "HISTORY_ASSISTANT_SENTINEL"},
    ]


def native_history(history):
    result = []
    for i, item in enumerate(history):
        if item["type"] == "message":
            content = item["text"]
            if item.get("images"):
                content = [{"type": "text", "text": content}] + [
                    {"type": "image_url", "image_url": {"url": image}} for image in item["images"]]
            result.append({"role": item["role"], "content": content})
        else:
            ident = "arbol-history-" + str(i)
            tool = "terminal" if item["name"] == "shell" else item["name"]
            arguments = dict(item["input"])
            if item["name"] == "shell" and "cwd" in arguments:
                arguments["workdir"] = arguments.pop("cwd")
            output = item["result"]["output"]
            if item["result"].get("exitCode", 0):
                output += "\nexit code: " + str(item["result"]["exitCode"])
            result += [{"role": "assistant", "content": None, "tool_calls": [call(tool, arguments, ident)]},
                       {"role": "tool", "content": output, "tool_call_id": ident, "tool_name": tool}]
    return result


async def history(args):
    async with Gateway(args, "history", tools=[]) as gateway:
        client = await gateway.client("client")
        history = arbol_history()
        expected = native_history(history)
        imported = "20261027_220000_" + uuid.uuid4().hex[:12]
        receipt = await client.rpc("session.mutate", session_id=imported, request_id=uuid.uuid4().hex,
            expected_revision=0, operation="import", payload={"sessions": [{
                "id": imported, "source": "tool", "cwd": str(gateway.workspace),
                "model": "gpt-4o", "messages": expected}]})
        snapshot = await client.rpc("session.resume", session_id=imported)
        admitted = await gateway.submit(client, imported, "HISTORY_VERIFY")
        finished = await gateway.receipt(client, imported, admitted)
        request = next(body for body in reversed(gateway.peer.requests) if "HISTORY_VERIFY" in user_text(body.get("messages", [])))
        model_messages = request["messages"]
        encoded = json.dumps(model_messages)
        calls = [call_ for m in model_messages for call_ in m.get("tool_calls", [])]
        tools = [m for m in model_messages if m.get("role") == "tool"]
        checks = {"image_bytes_preserved": IMAGE in encoded, "caller_text_preserved": "HISTORY_USER_SENTINEL" in encoded,
                  "tool_call_ids_preserved": {c["id"] for c in calls} == {"arbol-history-1", "arbol-history-2"},
                  "shell_arguments_preserved": {c["id"]: json.loads(c["function"]["arguments"]) for c in calls} == {
                      "arbol-history-1": {"command": "printf history", "workdir": "/fixture"},
                      "arbol-history-2": {"command": "exit 7", "workdir": "/fixture"}},
                  "tool_results_paired": {m["tool_call_id"] for m in tools} == {"arbol-history-1", "arbol-history-2"},
                  "failed_shell_exit_preserved": any("HISTORY_FAILURE_SENTINEL\nexit code: 7" == m["content"] for m in tools),
                  "previous_reply_preserved": "HISTORY_ASSISTANT_SENTINEL" in encoded,
                  "new_reply_completed": finished.get("outcome") == "completed"}
        await client.close()
        resumed = await gateway.client("resumed")
        after = await resumed.rpc("session.resume", session_id=imported)
        follow = await gateway.submit(resumed, imported, "HISTORY_FOLLOWUP")
        follow_result = await gateway.receipt(resumed, imported, follow)
        follow_request = next(body for body in reversed(gateway.peer.requests) if "HISTORY_FOLLOWUP" in user_text(body.get("messages", [])))
        checks["resume_retains_tool_and_image_history"] = IMAGE in json.dumps(follow_request) and "HISTORY_TOOL_RESULT_SENTINEL" in json.dumps(follow_request)
        checks["followup_completed"] = follow_result.get("outcome") == "completed"
        edited = arbol_history()
        edited[0]["text"] = "HISTORY_EDITED_USER_SENTINEL"
        edited[1]["result"]["output"] = "HISTORY_EDITED_TOOL_SENTINEL"
        rebuilt_ids = []
        for label, caller_history in (("edited", edited), ("missing", history)):
            if label == "missing":
                current = await resumed.rpc("session.resume", session_id=imported)
                await resumed.rpc("session.mutate", session_id=imported, request_id=uuid.uuid4().hex,
                    expected_revision=current["revision"], expected_generation=current["execution_generation"],
                    operation="delete", payload={})
            rebuilt = "20261027_220001_" + uuid.uuid4().hex[:12]
            await resumed.rpc("session.mutate", session_id=rebuilt, request_id=uuid.uuid4().hex,
                expected_revision=0, operation="import", payload={"sessions": [{
                    "id": rebuilt, "source": "tool", "cwd": str(gateway.workspace),
                    "model": "gpt-4o", "messages": native_history(caller_history)}]})
            await resumed.rpc("session.resume", session_id=rebuilt)
            admitted = await gateway.submit(resumed, rebuilt, "HISTORY_REBUILD_" + label)
            completed = await gateway.receipt(resumed, rebuilt, admitted)
            request = next(body for body in reversed(gateway.peer.requests)
                           if "HISTORY_REBUILD_" + label in user_text(body.get("messages", [])))
            rebuilt_text = json.dumps(request)
            marker = "HISTORY_EDITED_TOOL_SENTINEL" if label == "edited" else "HISTORY_TOOL_RESULT_SENTINEL"
            checks[label + "_history_rebuilt"] = (
                marker in rebuilt_text and IMAGE in rebuilt_text and completed.get("outcome") == "completed")
            if label == "edited":
                checks["edited_history_replaces_old_text"] = "HISTORY_USER_SENTINEL" not in rebuilt_text
            rebuilt_ids.append(rebuilt)
        result = {"verdict": "pass-in-tested-scope" if all(checks.values()) else "fail", "checks": checks,
                  "import_receipt": receipt, "initial_snapshot": snapshot, "resume_snapshot": after,
                  "model_messages": model_messages,
                  "rebuilt_session_ids": rebuilt_ids,
                  "caller_history_digest": hashlib.sha256(json.dumps(history, sort_keys=True).encode()).hexdigest()}
        write_json(gateway.output / "result.json", result)
        return result


async def memory(args):
    async with Gateway(args, "memory", memory=True) as gateway:
        (gateway.workspace / "AGENTS.md").write_text(INSTRUCTION + "\n")
        memories = gateway.home / "memories"
        memories.mkdir(exist_ok=True)
        (memories / "MEMORY.md").write_text(MEMORY + "\n")
        (memories / "USER.md").write_text(USER_MEMORY + "\n")
        skills = gateway.home / "skills/arbol-probe"
        skills.mkdir(parents=True)
        (skills / "SKILL.md").write_text("---\nname: arbol-probe\ndescription: " + SKILL + "\n---\n" + SKILL + "\n")
        original_files = {str(p.relative_to(gateway.home)): p.read_bytes() for p in memories.glob("*.md")}
        client = await gateway.client("client")
        observations = {}
        session_ids = {}
        for name, options in (("normal", {}), ("ignore_rules", {"ignore_rules": True})):
            sid = (await gateway.create(client, skills=["arbol-probe"], **options))["session_id"]
            session_ids[name] = sid
            admission = await gateway.submit(client, sid, "MEMORY_READ_" + name)
            done = await gateway.receipt(client, sid, admission)
            request = next(body for body in reversed(gateway.peer.requests) if "MEMORY_READ_" + name in user_text(body.get("messages", [])))
            text = json.dumps(request)
            observations[name] = {"receipt": done, "memory_visible": MEMORY in text,
                "user_memory_visible": USER_MEMORY in text, "instructions_visible": INSTRUCTION in text,
                "skill_visible": SKILL in text,
                "mcp_tool_available": any("arbol" in t.get("function", {}).get("name", "")
                                           for t in request.get("tools", [])),
                "memory_tool_available": any(t.get("function", {}).get("name") == "memory" for t in request.get("tools", []))}
            snapshot = await client.rpc("session.resume", session_id=sid)
            observations[name]["mcp_connected"] = any(
                server.get("name") == "arbol-probe" and server.get("connected")
                for server in snapshot.get("info", {}).get("mcp_servers", []))
        refused = {}
        for option in ("skip_memory", "memory_enabled"):
            refused[option] = await client.raw("session.create", request_id=uuid.uuid4().hex,
                source="tool", cwd=str(gateway.workspace), **{option: False if option == "memory_enabled" else True})
        current_files = {str(p.relative_to(gateway.home)): p.read_bytes() for p in memories.glob("*.md")}
        gateway.peer.scripts["MEMORY_WRITE_REQUEST"] = ("memory", {
            "action": "add", "target": "memory", "content": "ARBOL_MEMORY_WRITE_SENTINEL_8ac2"})
        write_admission = await gateway.submit(client, session_ids["ignore_rules"], "MEMORY_WRITE_REQUEST")
        write_receipt = await gateway.receipt(client, session_ids["ignore_rules"], write_admission)
        native_write = any("ARBOL_MEMORY_WRITE_SENTINEL_8ac2" in p.read_text() for p in memories.glob("*.md"))
        gateway.peer.scripts["MCP_CALL_REQUEST"] = ("tool_call", {"calls": [
            {"name": "mcp__arbol_probe__sentinel", "arguments": {}}]})
        mcp_admission = await gateway.submit(client, session_ids["ignore_rules"], "MCP_CALL_REQUEST")
        mcp_receipt = await gateway.receipt(client, session_ids["ignore_rules"], mcp_admission)
        mcp_request = next(body for body in reversed(gateway.peer.requests)
                           if "MCP_CALL_REQUEST" in user_text(body.get("messages", [])))
        mcp_results = [m for m in mcp_request.get("messages", []) if m.get("role") == "tool"]
        mcp_invoked = any("ARBOL_MCP_SENTINEL" in json.dumps(m.get("content")) for m in mcp_results)
        mcp_pid = gateway.output / "mcp-peer.pid"
        if mcp_pid.exists():
            gateway.track(int(mcp_pid.read_text()))
        result = {"verdict": "no-independent-public-memory-control-demonstrated", "observations": observations,
                  "per_session_option_refusals": refused, "read_only_turns_preserved_files": current_files == original_files,
                  "memory_write_with_ignore_rules": native_write, "memory_write_receipt": write_receipt,
                  "mcp_invocation_preserved": mcp_invoked, "mcp_receipt": mcp_receipt,
                  "config_unchanged": hashlib.sha256((gateway.home / "config.yaml").read_bytes()).hexdigest() == gateway.config_digest}
        assert all(observations["normal"][key] for key in (
            "memory_visible", "user_memory_visible", "instructions_visible", "skill_visible")), observations
        assert observations["normal"]["mcp_connected"] and mcp_invoked, result
        write_json(gateway.output / "result.json", result)
        return result


async def main(args):
    output = Path(args.output)
    provenance = {"source": args.source, "revision": subprocess.check_output(
        ["git", "-C", args.source, "rev-parse", "HEAD"], text=True).strip(),
        "python": sys.version, "executable": sys.executable, "platform": sys.platform,
        "hermes": args.hermes, "inference": "loopback scripted peer only",
        "prototype_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    write_json(output / "provenance.json", provenance)
    cases = {"smoke": smoke, "ownership": ownership, "history": history, "memory": memory}
    results = {}
    for name in (list(cases) if args.case == "all" else [args.case]):
        print("Starting " + name, flush=True)
        try:
            results[name] = {"status": "finished", "observations": await cases[name](args)}
            print("Finished " + name, flush=True)
        except Exception as error:
            results[name] = {"status": "error", "error": str(error), "traceback": traceback.format_exc()}
            print("Failed " + name + ": " + str(error)[:600], flush=True)
        write_json(output / "results.json", results)
    return 1 if any(result["status"] == "error" for result in results.values()) else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("source", "hermes", "output", "case"):
        parser.add_argument("--" + name, required=True)
    sys.exit(asyncio.run(main(parser.parse_args())))
