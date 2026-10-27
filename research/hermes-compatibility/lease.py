"""Private EOF lease helper for a shared-gateway run; no native behavior is patched."""
import argparse
import asyncio
import json
from pathlib import Path
import runpy
import subprocess
import sys
import time


def controller(args):
    child_args = [str(Path(__file__)), "--mode", "watchdog", "--source", args.source,
                  "--probe", args.probe, "--request", args.request, "--output", args.output]
    code = ("import sys,runpy;sys.path.insert(0," + repr(args.source) + ");import hermes_bootstrap;"
            "sys.argv=" + repr(child_args) + ";runpy.run_path(" + repr(str(Path(__file__))) + ",run_name='__main__')")
    child = subprocess.Popen([sys.executable, "-I", "-B", "-c", code], stdin=subprocess.PIPE,
                             start_new_session=True)
    Path(args.output + ".controller-ready").write_text(json.dumps({"watchdog_pid": child.pid}))
    # Only this process holds the pipe's write end. SIGKILL closes it in the kernel.
    while child.poll() is None:
        time.sleep(.1)
    return child.returncode


async def cancel(args, library, request):
    from websockets.asyncio.client import connect
    home = Path(request["home"])
    descriptor = library["control"](home, "identify")
    grant = library["control"](home, "session-ticket", {
        "profile_id": str(home), "instance_id": descriptor["instance_id"], "purpose": "interactive"})
    url = descriptor["api_origin"].replace("http:", "ws:") + "/api/ws"
    async with connect(url, subprotocols=["hermes-gateway-v1", "hermes-gateway-ticket." + grant["ticket"]]) as ws:
        client = library["Client"](ws, Path(args.output).parent, "lease-watchdog")
        boundary = library["Gateway"].__new__(library["Gateway"])
        try:
            await client.rpc("session.resume", session_id=request["session_id"])
            return await boundary.stop(client, request["session_id"], request["admission"])
        finally:
            await client.close()


def main(args):
    if args.mode == "controller":
        return controller(args)
    library = runpy.run_path(args.probe)
    request = json.loads(Path(args.request).read_text())
    Path(args.output + ".watchdog-ready").write_text("ready\n")
    sys.stdin.buffer.read()
    start = time.monotonic()
    try:
        result = {"status": "finished", "stop": asyncio.run(cancel(args, library, request))}
    except Exception as exc:
        result = {"status": "error", "error": str(exc)}
    result["eof_to_end_seconds"] = time.monotonic() - start
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n")
    return 0 if result["status"] == "finished" else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ("mode", "source", "probe", "request", "output"):
        parser.add_argument("--" + name, required=True)
    sys.exit(main(parser.parse_args()))
