"""Probe an EOF lease around one private native process group.

This deliberately does not claim ownership of groups created by Mimo's tools.
It tests whether a server-only lifetime helper is sufficient.
"""
import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
import time

record = Path(sys.argv[1])
command = sys.argv[2:]
child = subprocess.Popen(command, stdin=subprocess.DEVNULL, start_new_session=True)
record.write_text(json.dumps({'pid': child.pid, 'group': child.pid}))
closing = False

def close(*_):
    global closing
    closing = True

signal.signal(signal.SIGTERM, close)
signal.signal(signal.SIGINT, close)
try:
    while child.poll() is None and not closing:
        readable, _, _ = select.select([sys.stdin.fileno()], [], [], .1)
        if readable and not os.read(sys.stdin.fileno(), 4096):
            closing = True
    if child.poll() is None:
        os.killpg(child.pid, signal.SIGTERM)
        try:
            child.wait(2)
        except subprocess.TimeoutExpired:
            os.killpg(child.pid, signal.SIGKILL)
            child.wait(2)
finally:
    if child.poll() is None:
        os.killpg(child.pid, signal.SIGKILL)
        child.wait()
