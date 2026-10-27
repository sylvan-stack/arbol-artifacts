#!/usr/bin/env python3
"""Enter the installed Hermes runtime, then run isolated compatibility probes."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hermes", default=str(Path.home() / ".local/bin/hermes"))
    parser.add_argument("--source", default=str(Path.home() / ".hermes/hermes-agent"))
    parser.add_argument("--output", required=True)
    parser.add_argument("--case", choices=("smoke", "ownership", "history", "memory", "all"), default="all")
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    bootstrap_home = output / "bootstrap-profile"
    bootstrap_home.mkdir(exist_ok=True)
    env = {k: os.environ[k] for k in ("HOME", "USER", "LOGNAME", "PATH", "LANG", "TZ", "TERM") if k in os.environ}
    env.update(HERMES_HOME=str(bootstrap_home), PYTHONDONTWRITEBYTECODE="1", PYTHONUNBUFFERED="1")
    discovered = subprocess.run([args.hermes, "--print-runtime-command"], env=env,
                                capture_output=True, text=True, timeout=60, check=True)
    command = json.loads(discovered.stdout)
    (output / "runtime-command.json").write_text(json.dumps(command, indent=2) + "\n")
    script = output / "probe-source.py"
    script.write_bytes(Path(__file__).with_name("probe.py").read_bytes())
    (output / "lease-source.py").write_bytes(Path(__file__).with_name("lease.py").read_bytes())
    (output / "launcher-source.py").write_bytes(Path(__file__).read_bytes())
    code = ("import sys,runpy; sys.path.insert(0," + repr(str(Path(args.source).resolve())) + "); "
            "import hermes_bootstrap; sys.argv=" + repr([str(script), "--output", str(output),
            "--source", args.source, "--hermes", args.hermes, "--case", args.case]) + "; "
            "runpy.run_path(" + repr(str(script)) + ",run_name='__main__')")
    return subprocess.call([command[0], "-I", "-B", "-c", code], env=env)


if __name__ == "__main__":
    sys.exit(main())
