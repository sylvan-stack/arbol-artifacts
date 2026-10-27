---
role: authored
---
# Hermes compatibility prototype

Executable research for the [Hermes Driver investigation](../hermes-agent-driver.md).
The prototype checks the unmodified installed Hermes release against Arbol's
run ownership, native tool/image history and per-run memory requirements.
It is not an installed Driver or an accepted specification.

Use disposable Hermes profiles and a loopback model peer with synthetic
responses. No real provider credential or remote inference is required. Keep
runtime outputs under the corpus's ignored `generated/` directory, outside
this tracked folder. Record exact runtime/source provenance in those outputs.
Preserve the installed Hermes checkout and the owner's native configuration.
Any experiment using an internal API must identify that boundary separately
from shipped public-protocol behavior.

The runner must report a separate verdict for each contract area, retain
counterexamples and clean up only its own processes and profiles. A missing
capability is a failed compatibility check or an explicit unresolved question;
it must not be hidden by replacing native behavior with a mock.

## Run the prototype

Run [run.py](run.py) with `--case ownership`, `--case history`, `--case memory`
or `--case all`, and `--output <new-output-directory>`. The default installation
is `~/.local/bin/hermes` with source under `~/.hermes/hermes-agent`; override
these with `--hermes` and `--source` when needed. Use a fresh output directory.

The launcher resolves Hermes' published `--print-runtime-command` boundary,
loads its native bootstrap and executes a frozen copy of [probe.py](probe.py).
Each gateway starts through the installed launcher's `--run-module gateway.run`
entry. Hermes may prepare its dependency environment for each disposable data
root. That is native installation work in the test root, separate from remote
model inference. The loopback server supplies scripted Chat Completions; the
gateway, agent loop, tools, persistence, MCP and process controls remain native.

The runner copies its own code and records hashes, native revision, Python,
wire frames, model inputs, per-case observations and cleanup. Exit 0 means the
experiment completed; read each compatibility `verdict` and its checks before
claiming a contract pass. A demonstrated missing capability is a valid research
result, rather than a runner crash. `results.json` records unexpected errors.

## What is exercised

| Case | Contract focus | Native mechanisms |
|---|---|---|
| Ownership | DRV-0.10; DRV-2.16, 2.19, 2.21, 2.26; DRV-3.32 | Two concurrent sessions; generation-fenced interrupt; session-scoped process/child inventory and stop; persisted background process; delegated child; a private EOF lease after killing its controller. |
| History | DRV-2.11, 2.12, 2.23, 2.35, 2.36 | Import a normalized caller transcript with shell calls/results and PNG; inspect actual model payloads; resume; import an edited branch; delete the old conversation and rebuild from caller data. |
| Memory | DRV-0.4; DRV-3.25, 3.31 | Positive sentinels for memory, user memory, project instructions and a skill; normal and `ignore_rules` sessions; rejected separate memory flags; real memory write; configured MCP discovery and invocation. |

[lease.py](lease.py) demonstrates a Driver-side lifetime mechanism for a shared
vendor service. Its controller alone holds a pipe's write end. On controller
death, the helper observes EOF and uses the session/admission identity to stop
only that run. This helper is prototype code, not a feature claimed of the
unmodified ACP client. Native transport disconnect by itself is not used as
the cancellation guarantee. The result records controller-kill-to-cleanup time.

The completion check joins the native admission result with `process.list`,
`subagent.list`, pending admissions and execution state. A terminal parent
reply alone is insufficient. The process fixture records OS identities and
checks that native cancellation actually ended its workers. The fixture's
emergency cleanup is recorded separately; it cannot turn a failed native
cleanup into a passing observation.

## Limits of these probes

These are deterministic macOS compatibility experiments against the exact
installed source, not full DRV-5 conformance or provider qualification. The
profiles explicitly disable automatic background review and title generation,
select a loopback custom model, and declare that model's vision capability.
Memory tests enable built-in memory. Production home contents are not copied.
Tools are selected in the fixture profile; the prototype does not establish
fidelity for every possible native setup. Native config files use the release's
current schema, and configuration bytes are compared after each experiment.

Only PNG is exercised. No remote provider, real allowance, full compaction,
external memory provider, browser/remote terminal, arbitrary plugin or shell
hook qualification is claimed. A completion inventory must be qualified for
every supported native resource profile before a production Driver promises
the whole contract. The ownership verdict covers scoped cleanup and the total
15-second budget on the exercised paths. It does not establish Arbol's exact
two-second escalation phase: native process termination has two grace windows,
and a blocked native call still needs its own bounded integration. The prototype
deliberately writes no specification.

Local run records and the compatibility report are under the ignored
`generated/hermes-compatibility-2026-10-27/` folder of the Arbol corpus. They are
not published with this source. The investigation links the local report so
the owner can inspect the actual verdicts and limitations.

<!-- sources:
arbol:driver-contract/00-overview-and-boundary.md
arbol:driver-contract/02-inference.md
arbol:driver-contract/03-tools-and-permissions.md
arbol:research/hermes-agent-upstream-2026-10-27.md
-->
