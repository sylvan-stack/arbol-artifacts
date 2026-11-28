---
role: authored
---
# Mimo compatibility probes

Executable research for [the Mimo Driver investigation](../mimo-driver.md).
Run the installed, unmodified CLI with disposable homes, normal native discovery
of fixture instructions/plugins/skills/MCP, and a scripted loopback model peer.
The model peer is synthetic; agent loops, tools, history, questions, event
storage and process controls remain native. No real-provider inference or
credential copying is needed. The account investigation is read-only and uses
separate private evidence.

Run `python3 run.py --case <case> --output <new-absolute-directory>`.
Native cases are `core`, `history`, `ownership`, `errors`, `events`, `actors`,
`leases`, and `all` (the original native cases). Bridge cases are listed below.
Pass a path that does not yet exist under
`~/Builds/sylvan-stack/arbol/<run-id>/` for a retained run, or a new child of a
directory from `mktemp -d` for a disposable run. Keep reports and selected
result summaries in the corpus.
The runner retains raw peer requests, events, native state, process identities,
per-case checks and source/runtime provenance. It cleans only its own fixture
processes. A harness error is distinct from a failed compatibility check.
Exit 0 means the selected experiment ran without a harness error, not that every
compatibility assertion passed. Read each named result and retain negative
native controls. Run separate cases for bounded progress; `all` is a convenience
for an independently monitored run.

`core` uses positive and negative controls for native memory, retained owner
resources, appended system context, tool execution and questions. `history`
imports completed success/failure tool parts and images, then resumes, forks,
edits and rebuilds with fresh identities. `events` applies SSE backpressure,
observes a public event hook, and separately enables the native workspace
journal. `actors` checks child identity, cancellation and restart behavior.
`ownership` and `leases` retain the background-process counterexample and test
a real SIGKILL of a disposable controller. The original EOF helper owns only its
private server group; its negative result is retained as a control.

The command-group prototype adds `bridge.py`, `bridge_cases.py` and
`support_fixture.py`. It imports the guard/anchor/exec/watcher/process-identity
implementation from the configured read-only Pi Driver source checkout at
revision `9d40e549c4450c835815da1ddfe32d623bfeda62`. Each run records dependency
hashes in `guard-provenance.json`. Python 3.14 and the macOS libproc ABI are the
tested runtime. This cross-checkout dependency is research scaffolding, not a
packaging proposal. The installed Mimo binary is unchanged.

| Case | Qualification target |
|---|---|
| `bridge_background` | Ordinary background, double fork/reparenting, immediate shell exit, retained late output, publish before admit |
| `bridge_cancel` | Native abort and timeout, TERM-ignoring foreground/background, acknowledged empty groups |
| `bridge_death` | Real controller SIGKILL, independent cleanup of native/command/MCP groups, unrelated process survives, socket recovery |
| `bridge_faults` | Guard/anchor SIGKILL, complete cleanup and mandatory failure acknowledgement |
| `bridge_races` | Published-but-gated shell, admission close, controller death before ack, rejection of busy seals and late launch |
| `bridge_support` | Original command/cwd/environment/output/exit, deny-all tool control, native MCP discovery and dispatch, stubborn support cleanup |
| `bridge_actors` | Native child call lineage, root answer while child works, abort of actor background group |
| `bridge_resources` | Native formatter background child, real LSP framing/discovery, stale and empty-work seals, support cleanup |
| `bridge_shells` | Bash and zsh selection, background work and restored original `SHELL` |
| `bridge_permissions` | Native command-pattern deny/allow before shim execution, without rewriting native tool arguments |

The shell shim preserves the real shell's basename so native parsing and
permission checks see the original command. The public `shell.env` hook adds
call correlation. Configured MCP/formatter/LSP commands use the same ownership
bridge through native public configuration. A private controller owns leases;
neither commands nor descendants inherit the controller's guard-control FDs.
Prepared identities and admission commits are durable before the exec gate opens.
Guard/anchor/watchers retain group identity and apply bounded escalation.

`freeze` closes admission for stop; `seal` accepts only the current empty-work
watermark. Idle MCP/LSP support stays owned through shutdown. The terminal
ownership audit is produced after watcher acknowledgement and a fresh kernel
inventory. It is not the future Driver's public final event. The Driver still
has to combine it with actor/follow-up settlement, event/dialog drain and durable
history/usage handling. Whole-profile qualification must cover automatic helper
and formatter discovery, executable plugins and their dependencies; unknown
resources must refuse the invocation rather than disappear from native discovery.
The accepted DRV-D33 deliberate process-group/session escape exception is retained.

The [selected bridge report](../../generated/mimo-bridge-2026-10-27/report.md)
records 57 passing checks, 13 native instances and 43 empty group inventories.
It closes the pre-specification ownership feasibility blocker for the tested
macOS profile. Runtime histories, model wire bodies and all process identities
remain in private run storage outside the corpus. No real-provider inference is used.

The optional temporary plugin uses Mimo's public plugin hooks. It is a candidate
integration mechanism, not an installed plugin or accepted Driver design.
Memory suppression must preserve native instructions and ordinary resources;
tool cancellation must be tested with deliberately requested calls. A passing
fixture profile does not qualify arbitrary executable plugins or native versions.

Keep raw runtime output and account material outside the corpus. Keep counterexamples,
do not convert a negative result into an unsupported claim that a contract
passed, and update the investigation before drafting specifications.

Source and runtime filenames are included in each private run's provenance and
script copy. The native baseline is the installed 0.1.16 binary and the pinned
source revision in the investigation. A fixture home is a test profile; these
experiments do not certify every executable resource in the owner's real home.

<!-- sources:
arbol:research/mimo-compatibility/run.py
arbol:research/mimo-compatibility/profile.mjs
arbol:research/mimo-compatibility/mcp_fixture.py
arbol:research/mimo-compatibility/controller.py
arbol:research/mimo-compatibility/lease.py
arbol:research/mimo-compatibility/bridge.py
arbol:research/mimo-compatibility/bridge_cases.py
arbol:research/mimo-compatibility/support_fixture.py
arbol-pi-driver:src/arbol_pi_driver/guard.py
arbol-pi-driver:src/arbol_pi_driver/guard_client.py
arbol-pi-driver:src/arbol_pi_driver/process_table.py
arbol-pi-driver:src/arbol_pi_driver/watcher.py
arbol-pi-driver:specs/ownership-and-state.md
arbol:driver-contract/02-inference.md
-->
