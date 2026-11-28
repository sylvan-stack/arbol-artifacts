"""Disposable owner process, killed by the probe to test kernel pipe EOF."""
import json
from pathlib import Path
import select
import subprocess
import sys

child = subprocess.Popen(sys.argv[2:], stdin=subprocess.PIPE, start_new_session=True)
Path(sys.argv[1]).write_text(json.dumps({'guardian': child.pid}))
while child.poll() is None:
    readable, _, _ = select.select([sys.stdin.fileno()], [], [], .1)
    if readable and not sys.stdin.buffer.read1(4096):
        child.stdin.close()
        break
child.wait()
