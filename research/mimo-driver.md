---
role: derived
sources:
  - arbol:research/mimo-upstream-2026-10-27.md
  - arbol:driver-contract/00-overview-and-boundary.md
---
# Mimo Driver investigation

Research bindings: `repo=arbol`, `topic=new Driver for the installed Mimo CLI`,
`depth=standard`. Updated 27 October 2026 after compatibility and ownership-bridge experiments.
This is research, not accepted specifications or release qualification.

## Current decision

28 October 2026: the [Mimo Driver specifications](../mimo-driver/specs/README.md)
were drafted from these findings and accepted after delegated review on
28 October 2026. They name production qualification gates separately from this
research; no Driver implementation or working Build is claimed. The original findings and negative controls remain.

**The pre-specification ownership blocker is closed for the tested macOS profile.**
Proceed to drafting around an authenticated private HTTP server plus a resource
bridge that admits and owns command groups. Plain server ownership remains
incompatible: native Bash and the Effect process spawner create detached groups.
The prototype supplies the missing boundary without patching the native binary
or replacing its permission scan.

The [bridge prototype](mimo-compatibility/bridge.py) and
[adversarial native cases](mimo-compatibility/bridge_cases.py) passed 57 checks
across 13 native instances. The final independent inventory found no live
members in any of 43 registered groups. Tests cover background work after shell
exit, cancellation, timeouts, controller/guard/anchor death, pre-admission death,
admission and seal races, actor commands, MCP, formatters and LSP support.
Both Bash and zsh were exercised. An unrelated process survived cleanup.

This closes a feasibility question, not release qualification. The first Driver
must qualify an exact native binary and executable resource/dependency inventory,
refuse an unqualified profile as a whole, and preserve normal owner discovery.
Do not silently remove executable resources. The accepted deliberate-detachment
exception DRV-D33 is unchanged; ordinary `&` and reparented descendants that stay
in their command group are owned. No quiet interval or native final answer is a
completion barrier.

The [reproducible probe suite](mimo-compatibility/README.md),
[bridge report](../generated/mimo-bridge-2026-10-27/report.md) and earlier
[native compatibility report](../generated/mimo-compatibility-2026-10-27/report.md)
retain the selected outcomes, original counterexamples and harness corrections.
Runtime/account material stays in ignored local output. The subsequent accepted
specification set is linked above; no Driver repository or installed owner
plugin has been created.

<!-- sources:
arbol:research/mimo-upstream-2026-10-27.md#M02 Serve lifecycle
arbol:research/mimo-upstream-2026-10-27.md#M18 Bash cancellation
arbol:research/mimo-upstream-2026-10-27.md#M31 Native detached shell groups
arbol:research/mimo-compatibility/lease.py
arbol:research/mimo-compatibility/controller.py
arbol:research/mimo-compatibility/run.py
arbol:driver-contract/03-tools-and-permissions.md
arbol-pi-driver:specs/ownership-and-state.md
arbol:research/mimo-compatibility/bridge.py
arbol:research/mimo-compatibility/bridge_cases.py
arbol:research/mimo-upstream-2026-10-27.md#M48 Effect process spawner defaults to detached groups
arbol:driver-contract/02-inference.md
-->

## Disposition of the original open questions

The questions below now have an integration choice or a named incompatibility.
The private report carries the actual observations. A demonstrated native
limitation is not a reason to claim that a compatibility gate passed.

| Question | Disposition for the first Driver |
|---|---|
| Transport and ownership | Use private HTTP plus the demonstrated gated resource bridge. A same-basename shell shim preserves native Bash's original-command permission checks; public command configuration wraps MCP/formatter/LSP resources. Guards retain groups after shell exit; an independent watcher handles controller/helper death. Plain server-only ownership remains a negative control. |
| Memory | The native write switch is insufficient. Use the observed pinned public-hook profile: disable native memory writes and auto dream/distill; remove only the native memory prompt/reminder; cancel the memory search tool before execution. Retain the native base, owner instructions/plugins, skills, ordinary reads and MCP. Use fresh native conversations for a changed profile. |
| System prompt | Append exact caller context through the public system-transform hook; preserve native instructions. Native prefix snapshots freeze that result, so a changed context/profile requires rebuilding under a fresh native identity. Never silently resume with old context. |
| No tools | Combine native deny-all permissions with a public before-tool cancellation hook. Native MCP search/use schemas may remain exposed; deliberately test the actual execution paths, including search, dispatch and actors. Cancelled native outcomes need normalization by the Driver. |
| History and images | Rebuild with typed completed native message/part import. Allocate fresh session, message and part identities; preserve success/failure tool results and image parts. Do not import a pending execution queue. Resume only against the Driver's matching history/profile map. |
| Events | Ordinary SSE is best effort and ordinary `/sync/history` is not an always-on journal. A private sequenced event hook is a candidate; native durable replay is separately available when the workspace feature is enabled. Neither is an ownership barrier. Qualify one delivery mechanism rather than assuming SSE is lossless. |
| Account check and allowance | Bind the existing Xiaomi login. Use authenticated non-inference `GET /models` for credential validation and catalog reading. Report allowance as `unsupported` for the current supported surface; official docs direct users to the platform page and do not document a remaining-allowance API. Do not substitute local stats or infer entitlement from a catalog. |
| Account/provider scope | Proceed with the existing native Xiaomi login only. Driver identity `mimo` and native provider/family `xiaomi` stay distinct. Do not expand to other providers or additional accounts without their own binding and isolation work. |
| Release profile | Baseline is the installed 0.1.16 binary plus a checked protocol/resource fingerprint. Qualify other binaries and executable resource profiles explicitly; version ordering alone is insufficient. |

These are research dispositions, not accepted product requirements. Scope is
conservatively tied to the owner's installed and logged-in tool. No feasibility
question remains open before drafting. Production protocol, packaging, resource
qualification and shared conformance checks belong in the specifications and
implementation plan; the prototype does not claim those are complete.

<!-- sources:
arbol:research/mimo-upstream-2026-10-27.md#M09 Memory write switch
arbol:research/mimo-upstream-2026-10-27.md#M10 Memory prompt construction
arbol:research/mimo-upstream-2026-10-27.md#M14 Prompt input and persistence
arbol:research/mimo-upstream-2026-10-27.md#M16 Native history import
arbol:research/mimo-upstream-2026-10-27.md#M19 Event delivery
arbol:research/mimo-upstream-2026-10-27.md#M31 Native detached shell groups
arbol:research/mimo-upstream-2026-10-27.md#M32 Conditional durable event storage
arbol:research/mimo-upstream-2026-10-27.md#M33 Native frozen prompt prefix
arbol:research/mimo-upstream-2026-10-27.md#M34 Memory and all-tool cancellation hooks
arbol:research/mimo-upstream-2026-10-27.md#M35 Public event subscription
arbol:research/mimo-upstream-2026-10-27.md#M36 Durable event catch-up
arbol:research/mimo-upstream-2026-10-27.md#M43 Official non-inference model catalog
arbol:research/mimo-upstream-2026-10-27.md#M44 Official allowance and billing distinction
arbol:research/mimo-compatibility/profile.mjs
arbol:research/mimo-compatibility/run.py
-->

## Native interfaces and data flow

| Surface | Consequence |
|---|---|
| `mimo run --format json --thinking` | A presentation stream: whole text/reasoning blocks, step usage and finished tool parts. It omits tool starts, filters other native sessions, and denies questions for newly created sessions. Useful for simple probes, insufficient as the primary Driver transport. |
| `mimo acp` | Owns an HTTP shim and exposes stdio JSON-RPC, images and native conversation operations. It shares the engine's memory and process behavior; it is not a separate ownership solution. Its README retains stale OpenCode limitations and names. |
| `mimo serve` | Broad session, prompt, raw-event, question, permission and abort APIs. Use one authenticated loopback server per invocation, itself behind an owned guard, together with per-command/resource guards. It also advertises a native model-server address. |
| `mimo import` / `mimo export` | Native typed message/part boundary. Import validates global identities and writes transactionally. Completed history is distinct from optional restored queue/execution state. |

Candidate flow: validate caller data and bound account; reserve run/conversation;
start and register all private native resources; verify effective profile and
exact model/variant; establish event delivery before prompting; translate events
and questions; stop admission and settle all owned work; stop/reap support and
native processes; emit one final event after cleanup. The resource steps now
have a working research prototype. The complete Driver and public final-event
implementation have not been built or run through shared conformance.

<!-- sources:
arbol:research/mimo-upstream-2026-10-27.md#M02 Serve lifecycle
arbol:research/mimo-upstream-2026-10-27.md#M03 Run session policy
arbol:research/mimo-upstream-2026-10-27.md#M04 Run event projection
arbol:research/mimo-upstream-2026-10-27.md#M05 Run reasoning projection
arbol:research/mimo-upstream-2026-10-27.md#M06 ACP construction
arbol:research/mimo-upstream-2026-10-27.md#M07 ACP capabilities
arbol:research/mimo-upstream-2026-10-27.md#M16 Native history import
arbol:driver-contract/02-inference.md
-->

## Command-group ownership bridge

The prototype reuses the Pi Driver's guard, exec gate, in-group anchor, Darwin
identity inspection and independent watcher at revision
`9d40e549c4450c835815da1ddfe32d623bfeda62`. Each run retains dependency file
hashes. This is a research dependency on that checkout; a shipped Mimo Driver
must package a pinned implementation rather than depend on another checkout.

The temporary `SHELL` executable has the original shell's basename. Mimo still
parses the original Bash command, applies native permissions, resolves cwd,
applies native `shell.env` additions and starts the shim. The public hook adds
session/call correlation and a test environment sentinel. The shim transfers
argv, cwd and the effective child environment over a private Unix socket; the
guard executes the original shell once, with its arguments and restored `SHELL`.
No command text is rewritten for native permission evaluation. A denied native
`touch *` rule and an allowed `printf` were tested separately from deny-all tool
configuration. Output, quoted metacharacters and exit code 7 survived unchanged.
No environment or resolved credential enters the ownership ledger.

The controller durably publishes exact PID/kernel-start identities and PGIDs
for the guard, anchor and gated exec child before each admission. A command
receives no execution authority before its gate opens. The guard retains its
group after the immediate shell exits and waits for remaining members and
output pipes. A double fork with reparenting did not escape that ownership.
An EOF lease ends the group when the native shim goes away. Controller death
closes all guard leases; the independent watcher cleans verified groups even
when a guard or anchor was killed. Signals require a live exact identity,
not merely an old numeric PID/PGID. TERM-ignoring fixtures required escalation.

MCP and LSP are registered support: idle support does not count as unfinished
agent work, but must end before final cleanup acknowledgement. Formatters are
work. Native formatter launch uses the detached-by-default Effect spawner, so
Bash interception alone would have missed it. The public formatter command
override was exercised by a native `write`; its background child held the tool
until it ended. A public LSP command override preserved initialize/didOpen and
diagnostics. MCP discovery and tool dispatch remained native. Support fixtures
deliberately ignore stdin EOF and SIGTERM.

Admission and sealing share a lock. `freeze` closes admission for stop/race
experiments. A completion `seal` requires an exact current ledger watermark and
no live or preparing command/formatter work. Pending admission and stale
watermarks were rejected. Sealing an empty work epoch left idle support owned
until shutdown. A shell paused after publication did not run when admission
closed or the controller died before acknowledgement. A post-freeze launch
faulted the run instead of acquiring another group.

After shutdown, the controller waits for the independent watcher's terminal
acknowledgement and then collects a fresh group inventory. Helper loss cannot
produce a successful ownership acknowledgement even when cleanup succeeds.
Recovery removes the stale private socket only after exact controller/watcher
death and a clean inventory. Actor commands carry their native session/call IDs;
the child actor's message identifies the originating actor. A root answer with
a live child remains a candidate; session abort cleans the child's group.

The research acknowledgement is not Arbol's public `finished` event. The real
Driver must combine this resource barrier with native actor/follow-up settlement,
dialog closure, event drain and history/usage persistence. Inventory admission,
all native launch paths, configuration translation, resource failure readiness,
sequence bounds and packaging need production implementation and qualification.
The tested disposable profile does not certify arbitrary owner plugins or
auto-discovered executables. These are explicit implementation obligations,
not a remaining uncertainty about whether native command ownership is possible.

<!-- sources:
arbol:research/mimo-compatibility/bridge.py
arbol:research/mimo-compatibility/bridge_cases.py
arbol:research/mimo-compatibility/profile.mjs
arbol:research/mimo-compatibility/support_fixture.py
arbol:research/mimo-upstream-2026-10-27.md#M45 Native shell environment selection
arbol:research/mimo-upstream-2026-10-27.md#M46 Native command-scoped shell environment hook
arbol:research/mimo-upstream-2026-10-27.md#M47 Native original-command permission scan
arbol:research/mimo-upstream-2026-10-27.md#M48 Effect process spawner defaults to detached groups
arbol:research/mimo-upstream-2026-10-27.md#M49 Public formatter command override
arbol:research/mimo-upstream-2026-10-27.md#M50 Public language-server command override
arbol-pi-driver:src/arbol_pi_driver/guard.py
arbol-pi-driver:src/arbol_pi_driver/guard_client.py
arbol-pi-driver:src/arbol_pi_driver/process_table.py
arbol-pi-driver:src/arbol_pi_driver/watcher.py
arbol-pi-driver:src/arbol_pi_driver/worker_entry.py
arbol-pi-driver:specs/ownership-and-state.md
arbol:driver-contract/02-inference.md
arbol:driver-contract/03-tools-and-permissions.md
-->

## Prompt, memory and history boundaries

The temporary integration plugin uses public hooks, not patched native source.
System transformations must mutate the supplied system array in place: replacing
its property is not equivalent where the caller retains the original array.
Memory suppression targets the native `# Memory system` block, its generated
path reminder and the memory-search tool. Native `memory.disable_write` also
keeps existing memory searchable; the negative probe therefore needs a positive
memory retrieval control. Keep checkpoint/compaction/history concepts distinct
from cross-conversation memory.

This is a native-memory feature control, not filesystem isolation. With full
tools, ordinary shell/read access can still read explicitly requested files,
including a file in a memory directory. Do not claim a sandbox or protection
against arbitrary executable owner plugins. The observed fixture profile must
be fingerprinted; unknown executable resources need qualification, not silent
removal. A native conversation made under an older prompt/tool/memory profile
must not be resumed merely because its session ID exists.

Mimo pins native system/tool prefixes. Fresh history reconstruction with a new
identity is the compatible route when the caller context, bound account,
working folder, history or integration profile differs. Message/part identifiers
are globally unique in the native database: changing only a session ID is not a
valid branch import. Preserve user/assistant roles, tool call/result identity,
shell result/error information and ordered prior/current image parts. A native
session file/database is history, not an authority to adopt live work.

<!-- sources:
arbol:research/mimo-upstream-2026-10-27.md#M09 Memory write switch
arbol:research/mimo-upstream-2026-10-27.md#M10 Memory prompt construction
arbol:research/mimo-upstream-2026-10-27.md#M16 Native history import
arbol:research/mimo-upstream-2026-10-27.md#M33 Native frozen prompt prefix
arbol:research/mimo-upstream-2026-10-27.md#M39 Prefix snapshot persistence
arbol:research/mimo-upstream-2026-10-27.md#M42 Memory search independent of write control
arbol:research/mimo-compatibility/profile.mjs
arbol:research/mimo-compatibility/run.py
arbol:driver-contract/06-state-and-simultaneous-calls.md
-->

## Events, actors, questions and failures

SSE uses a bounded drop-oldest queue. Durable event storage is conditional on
`MIMOCODE_EXPERIMENTAL_WORKSPACES` or replay; the history endpoint's presence
alone is not proof that it contains events. Public event hooks and the native
journal deserve separate delivery designs. A production hook needs checked
source sequence, explicit fault behavior, bounded buffering, startup readiness,
replay/deduplication and a completion drain; the probe's synchronous local log
is not that production protocol.

Native actors have an actor identity within a session. Fetch all slices using
`agent_id=*`, inspect the actor inventory's execution state, and correlate child
identity with the spawning tool's metadata. A root answer is not evidence that
children settled. Preserve child attribution and keep child text out of the root
answer. Actor status, command groups, native/support processes and pending
follow-ups all belong in the eventual completion predicate.

HTTP questions expose a native request ID, tool call correlation and ordered
answer arrays. The Driver must generate/validate common question IDs, correlate
answers, deduplicate deliveries, treat decline as cancellation and withdraw asks
before finalization. Permission requests are a different channel and follow
DRV-3's immediate-decision rule.

Use structured errors and retry records rather than HTTP success alone. Native
prompting can return an empty HTTP success response while publishing a model
error asynchronously. Rate-limit retry state must be latched before sending
abort, or its later aborted result would hide the original failure. Native
variant lookup can yield no variant for an unknown name: validate model and
variant against the exact catalog before prompting. Native `low` and other
variant names are model-specific, not a universal effort scale.

<!-- sources:
arbol:research/mimo-upstream-2026-10-27.md#M19 Event delivery
arbol:research/mimo-upstream-2026-10-27.md#M20 Retry defaults
arbol:research/mimo-upstream-2026-10-27.md#M23 Question bridge
arbol:research/mimo-upstream-2026-10-27.md#M25 Native event identities
arbol:research/mimo-upstream-2026-10-27.md#M32 Conditional durable event storage
arbol:research/mimo-upstream-2026-10-27.md#M35 Public event subscription
arbol:research/mimo-upstream-2026-10-27.md#M37 Actor history slices
arbol:research/mimo-upstream-2026-10-27.md#M38 Actor inventory
arbol:research/mimo-upstream-2026-10-27.md#M41 Variant provider options
arbol:research/mimo-compatibility/run.py
arbol:driver-contract/03-tools-and-permissions.md
arbol:driver-contract/04-errors-and-limits.md
-->

## Accounts and configuration

Keep the native Xiaomi credential in Mimo's store. Its browser authorization is
OAuth-labelled but returns an API key and metadata, not an established OAuth
refresh-token record. A Driver attachment should pin native account, endpoint
and credential revision without copying a credential into Arbol state or the
Keychain. Reattachment is explicit after a native account change; no fallback
to another provider, endpoint or payment mode.

The official models endpoint is the non-inference validation/catalog surface.
Use the exact native endpoint and explicit host/redirect rules, never send the
credential to a guessed host. Public model availability is not a per-model
entitlement promise. Token Plan and pay-as-you-go credentials/endpoints are
separate. For the supported documented surface, remaining allowance is
`unsupported`; token totals are consumption, not account allowance.

Production uses Mimo's normal XDG-based native directories and normal resource
discovery. `MIMOCODE_HOME` relocates all native directories and is for disposable
tests, not a replacement for the owner's home. Apply temporary configuration
with `MIMOCODE_CONFIG_CONTENT`; remove inherited auth/provider/home overrides
and keep the real HOME. Do not use `--pure` or disable instructions/plugins to
make a memory test pass. An isolated fixture home does not certify the owner's
entire real executable resource profile.

<!-- sources:
arbol:research/mimo-upstream-2026-10-27.md#M11 Native directories
arbol:research/mimo-upstream-2026-10-27.md#M12 Native credential store
arbol:research/mimo-upstream-2026-10-27.md#M13 Xiaomi browser authorization
arbol:research/mimo-upstream-2026-10-27.md#M21 Runtime configuration
arbol:research/mimo-upstream-2026-10-27.md#M24 Provider catalog
arbol:research/mimo-upstream-2026-10-27.md#M43 Official non-inference model catalog
arbol:research/mimo-upstream-2026-10-27.md#M44 Official allowance and billing distinction
arbol:driver-contract/01-subscriptions.md
-->

## Arbol integration and evidence baseline

Target accepted Driver Contract 2, DRV-0 through DRV-6. A future
`arbol-mimo-driver` follows the typed Python CLI, packaged interpreter,
numbered Builds, installed native tool, common state and event rules. It does
not own the caller's transcript, select failover routes or become a resident
service. The Trivial Trunk derives `arbol-<driver>-driver` from its route and
checks identity, contract, families and Subscription records; Radar discovers
Driver launchers. These are extension points, not full UI/distribution proof.

Source is pinned to MiMo-Code tag v0.1.16, commit
`b8dbe084ed8e77be2f75a85a9c880031aed699c9`; version agreement is not binary build
provenance. Private runs retain binary/script hashes and their exact evidence.
The configured `readonly/` Arbol source clones differ from the similarly named
top-level checkouts; use configured roots for continuing source research.
Revisions inspected in the initial investigation were:

| Repository | Configured revision |
|---|---|
| `arbol` | `b7bcf1f8c678560a6e4a31158b646fae7f581e86` |
| `arbol-trunk` | `d067d7dd7fe72bd1f47c636df51bee53bd7aeb44` |
| `arbol-codex-driver` | `7db318307aa04f172b1d4daecf3262215ef759eb` |
| `arbol-claude-driver` | `fc66624fca03b7f1d7cb395b0f1d445c2fc3030a` |
| `arbol-pi-driver` | `9d40e549c4450c835815da1ddfe32d623bfeda62` |

Mycel search supplied orientation with `--repo arbol --no-fresh`; freshness and
dependency verification were incomplete. Source files and section targets were
checked directly. Ingest, Source Ref index resolution and retrieval of this
new research remain unverified. The shared conformance suite was not run
against a nonexistent Mimo Driver. The experiments qualify specific native
mechanisms and counterexamples; they are not BLD release gates or the complete
DRV scenario suite.

<!-- sources:
arbol:driver-contract/00-overview-and-boundary.md
arbol:driver-contract/05-conformance.md
arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/driver.py#capabilities
arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/driver.py#launcher_name
arbol:src/arbol_radar/drivers.py#drivers_of
arbol:research/mimo-compatibility/README.md
-->
