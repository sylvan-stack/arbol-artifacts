---
role: derived
sources:
  - arbol:research/hermes-agent-upstream-2026-10-27.md
  - arbol:driver-contract/00-overview-and-boundary.md
---
# Hermes Agent Driver investigation

Research bindings: `repo=arbol`, `topic=new Driver supporting Hermes Agent`,
`depth=standard`. Investigated 27 October 2026. This prepares specifications;
it does not accept a design or implement a Driver.

## What the spec writer needs first

Hermes Agent means the Nous Research agent application, rather than a Hermes
model served through an existing Driver. It offers enough agent functionality
to justify investigation, but **a transport compatible with Arbol's execution
and state ownership rules has not yet been established**.

Three findings determine the next work:

1. **ACP is a viewer of a shared execution gateway.** The production constructor
   selects `GatewayACPAgent`; its connection can start a profile gateway. Owning
   the ACP subprocess therefore does not mean owning the inference or its tools.
2. **The standalone TUI stdio server needs exclusive ownership of the home.**
   Its own entry point says current product surfaces use the profile gateway
   instead. Running one standalone server per Arbol run against the normal home
   conflicts with concurrent runs and an existing Hermes gateway.
3. **History and memory need explicit integration work.** Standalone
   `session.create(messages=...)` retains text roles only. A richer canonical
   import exists and deserves a probe. `--ignore-rules` is too broad for memory
   suppression because it also removes project context; `skip_memory=True`
   alone can still load built-in memory when that toolset is enabled.

Start with an ownership and configuration compatibility experiment. Do not
write an accepted implementation plan around `hermes acp` merely because it
speaks JSON-RPC. A private core wrapper is an investigation candidate, not a
proven escape from Hermes' canonical writer model.

<!-- sources:
arbol:research/hermes-agent-upstream-2026-10-27.md#H01 Integration surfaces
arbol:research/hermes-agent-upstream-2026-10-27.md#H02 ACP dispatch to a gateway
arbol:research/hermes-agent-upstream-2026-10-27.md#H04 Automatic gateway startup
arbol:research/hermes-agent-upstream-2026-10-27.md#H05 Standalone home ownership
arbol:research/hermes-agent-upstream-2026-10-27.md#H08 Seed history coercion
arbol:research/hermes-agent-upstream-2026-10-27.md#H16 Memory initialization
-->

## Evidence baseline and limits

The [upstream snapshot](hermes-agent-upstream-2026-10-27.md) pins 31 evidence
sections to main commit `b63fbbac4d27d1e4b8585ff7065e6dceb6207394`. GitHub's
latest release at capture was **v0.22.5**, published 23 October 2026, commit
`bf0203a794a07aac3ff764972ab9087baa4e4f4e`. The snapshot separately copies
the release's ACP dispatch and standalone-home ownership code: those two
constraints also exist in the release. Other main findings must be rechecked
against the version selected for implementation.

Mycel search ran with `--repo arbol --no-fresh` for initial orientation. It
returned the migration plan and conformance harness; freshness and dependency
verification were incomplete. Findings below were checked against files.
No previous Hermes research was found by a Markdown search of the active
artifact corpora. This is a scoped search result, not proof of universal absence.

Use Mycel's configured `readonly` source checkouts as the implementation
baseline. The top-level `arbol` checkout differs from that baseline, including
its conformance fixture's Driver list. Revisions read:

| Repository | Configured source revision |
|---|---|
| `arbol` | `b7bcf1f8c678560a6e4a31158b646fae7f581e86` |
| `arbol-trunk` | `d067d7dd7fe72bd1f47c636df51bee53bd7aeb44` |
| `arbol-pi-driver` | `9d40e549c4450c835815da1ddfe32d623bfeda62` |
| `arbol-claude-driver` | `fc66624fca03b7f1d7cb395b0f1d445c2fc3030a` |
| `arbol-codex-driver` | `7db318307aa04f172b1d4daecf3262215ef759eb` |

No `hermes` executable resolved on PATH in the session or a clean owner login
shell. Hermes was not installed, imported or started. There were no account,
inference, cancellation or runtime compatibility probes. Runtime behavior and
release qualification remain unverified. Existing unrelated edits in Arbol's
corpus were preserved. Production source and its Git state were not changed.

<!-- sources:
arbol:research/hermes-agent-upstream-2026-10-27.md#Release comparison
arbol:conformance/harness.py#ScenarioHome.part
-->

## The Arbol boundary to preserve

The accepted Driver Contract governs this work; the glossary's Driver entry
still describes the older subscription-agnostic design. DRV-0 explicitly
records that vocabulary drift. Use the contract's responsibilities.

| Contract area | Consequence for Hermes |
|---|---|
| DRV-0: boundary and packaging | A command-line program, one invocation per operation, installed native tool, reported compatibility, allowlisted child environment, normal native home, numbered Builds. No Driver daemon. |
| DRV-1: Subscriptions | A specific vendor family and account binding, sign-in/status/check/models/usage, native credential ownership, no public credential export or silent account substitution. Hermes is the transport; it is not automatically the billing family. |
| DRV-2: inference | Full caller history on each run, correct resume or rebuild, exact request selection, ordered complete blocks, usage totals, one terminal event and bounded cancellation. |
| DRV-3: tools | Normal native setup, instructions, hooks, plugins, skills and MCP; unrestricted permissions; memory off for the run; all tools or none; shell normalization, child attribution and user questions. |
| DRV-4: failures | Closed typed errors, structured evidence first, no Driver retry, rate-limit and credential rejection handled at the first observable refusal. |
| DRV-5: proof | Shared stand-in scenarios, isolated no-inference probes, explicit live checks and packaged release gates. |
| DRV-6: state | Nonsecret Subscription and run records, locks and recovery, and a continuity map containing identifiers/digests rather than another stored transcript. |

Pi is the closest current implementation example because it bridges a
multi-provider agent. Its recent specs add Kimi Code and ChatGPT beyond the
initial z.ai/DeepSeek scope; the shared contract's older family summary is not
an exhaustive current list. Its architecture is useful precedent, but its Pi
bootstrap, native history and resource adapters cannot simply be renamed.

<!-- sources:
arbol:driver-contract/README.md
arbol:driver-contract/00-overview-and-boundary.md
arbol:driver-contract/01-subscriptions.md
arbol:driver-contract/02-inference.md
arbol:driver-contract/03-tools-and-permissions.md
arbol:driver-contract/04-errors-and-limits.md
arbol:driver-contract/05-conformance.md
arbol:driver-contract/06-state-and-simultaneous-calls.md
arbol-pi-driver:specs/overview.md
-->

## Integration surfaces and ownership

| Candidate | Established in source | Implication for the specification |
|---|---|---|
| `hermes acp` | Standard ACP messages, model/session controls and cancellation; production construction delegates execution to the profile gateway. | Good protocol reach; owning the stdio client is insufficient for process ownership. Session-scoped controls and settlement would need proof or a contract amendment. |
| Standalone `tui_gateway.entry` | Rich JSON-RPC; creates an in-process agent, but takes the home's exclusive ownership reservation. | Useful for isolated probes. Cannot assume one process per run sharing the normal home or coexistence with ordinary Hermes. |
| Canonical gateway WebSocket | Native client ensures/attaches a profile gateway; canonical create supports provider/model, reasoning, yolo and toolsets. Canonical session mutation offers import. | Most faithful to current Hermes architecture, but execution is shared. Generic and canonical methods with the same name have different schemas. |
| HTTP API | `/v1/runs` has status/events/approval/steer/stop; separate capabilities endpoint. | A service integration candidate. OpenAI compatibility alone does not establish Driver history, account or resource semantics. |
| Private child importing installed `AIAgent` | Constructor exposes callbacks, provider settings, system-prompt append, toolsets, memory and background-review switches; conversation call accepts native history. | Potential control over one execution process. Public stability, complete native startup, canonical persistence and normal-home concurrency all remain to be established. Do not bypass ownership guards or open the canonical DB directly. |

The mismatch is between Arbol's owned execution and Hermes' shared execution,
not between JSON and another wire format. Stopping the user's entire Hermes
gateway cannot be the cleanup mechanism for one Arbol run. A separate Hermes
home per production run would also violate the current normal-home rule and
would lose the owner's ordinary setup unless an explicit design changed it.

A vendor-owned gateway is not itself a Driver daemon. Its existence alone
does not prove nonconformance: the investigation must establish whether scoped
native controls can meet the invocation, cancellation, isolation and cleanup
requirements. An owner decision is needed only if the resulting design changes
those guarantees, rather than merely choosing a different wire protocol.

Current source's canonical-store documentation identifies the gateway as the
only canonical session writer, including managed workers. An integration must
respect that ownership. A private wrapper needs a supported execution/store
boundary, not a direct SQLite workaround.

<!-- sources:
arbol:research/hermes-agent-upstream-2026-10-27.md#H02 ACP dispatch to a gateway
arbol:research/hermes-agent-upstream-2026-10-27.md#H03 ACP viewer lifetime
arbol:research/hermes-agent-upstream-2026-10-27.md#H04 Automatic gateway startup
arbol:research/hermes-agent-upstream-2026-10-27.md#H05 Standalone home ownership
arbol:research/hermes-agent-upstream-2026-10-27.md#H06 Canonical store ownership
arbol:research/hermes-agent-upstream-2026-10-27.md#H13 Agent construction controls
arbol:research/hermes-agent-upstream-2026-10-27.md#H14 Core conversation input
arbol:research/hermes-agent-upstream-2026-10-27.md#H29 HTTP run API
arbol:research/hermes-agent-upstream-2026-10-27.md#H30 Canonical create controls
arbol:driver-contract/00-overview-and-boundary.md
-->

## History and native state

Arbol's caller history is authoritative. Resume must verify that the native
conversation covers exactly that history; failures invalidate the map. Native
compaction and removed conversations cannot make the next run depend on data
available only in Hermes. This includes histories created by other Drivers.

Standalone `SessionCreateParams` exposes `messages`, but the seed coercer
accepts only `user`, `assistant` and `system` with string content. It builds
fresh rows containing role/content and optional hidden display metadata.
Consequently that path does not import tool result roles, assistant tool-call
structure or native image content. Ordinary foreign-session import also
normalizes user/assistant text; it is not evidence of lossless Arbol import.

There is a more promising path: canonical `session.mutate` with operation
`import` authorizes `session:create` and validates a session payload. The
portability layer retains tool-call identifiers/names, accepts structured
message content and validates native import rows. This is **source evidence
of a candidate**, not proof that an imported tool/image history resumes with
the semantics Arbol requires. Probe pairing, full tool calls, media lifetime,
provider-specific history acceptance, import limits and native compaction.

The spec should define fresh/resumed/rebuilt outcomes, digest scope, concurrent
resume reservations, allowed native writes, failure invalidation and the
contract's visible text fallback. Prefer the gateway's supported mutation
boundary to writing rows or copying a live database. If a different supported
native history API is selected, prove that API instead.

<!-- sources:
arbol:driver-contract/02-inference.md#The conversation
arbol:driver-contract/06-state-and-simultaneous-calls.md
arbol:research/hermes-agent-upstream-2026-10-27.md#H07 Session create overrides
arbol:research/hermes-agent-upstream-2026-10-27.md#H08 Seed history coercion
arbol:research/hermes-agent-upstream-2026-10-27.md#H09 Seed message wire
arbol:research/hermes-agent-upstream-2026-10-27.md#H10 Foreign import scope
arbol:research/hermes-agent-upstream-2026-10-27.md#H11 Rich import authority
arbol:research/hermes-agent-upstream-2026-10-27.md#H12 Rich import fields
arbol-pi-driver:src/arbol_pi_driver/continuity.py
-->

## Memory, instructions and native features

Hermes' persistent memory is a material product difference. Built-in memory
and user-profile flags default to enabled; an external memory provider can
also participate. Background memory/skill review can start after the reply is
delivered, and optional preparation of compaction can run at turn end.

The current TUI factory passes the same `ignore_rules` value to
`skip_context_files` and `skip_memory`. That switch cannot satisfy Arbol's
requirement to preserve instructions while turning off native memory. Direct
`AIAgent` construction separates those arguments and exposes
`skip_background_review`, but memory initialization explicitly allows the
built-in store when the memory toolset is requested even with `skip_memory`.
The precise run-scoped mechanism must cover reads, writes, external providers,
review and descendants while preserving ordinary skills, hooks and MCP.

Do not mutate `config.yaml`, `.env`, memory files or saved tool preferences as
an invocation setup step. A per-run supported configuration context may be
needed; its availability is unproven. Also qualify `tools=none` separately:
the existence of toolset parameters does not prove that every built-in,
plugin and MCP tool can be removed without residual work.

An owner decision is needed if the intended Hermes support specifically
includes its persistent learning. The proposed baseline remains DRV-3's
memory-off rule until the owner changes that contract explicitly.

<!-- sources:
arbol:driver-contract/00-overview-and-boundary.md#The vendor tool's home
arbol:driver-contract/03-tools-and-permissions.md#The vendor tool's full power
arbol:research/hermes-agent-upstream-2026-10-27.md#H13 Agent construction controls
arbol:research/hermes-agent-upstream-2026-10-27.md#H15 Native setup and coupled memory switch
arbol:research/hermes-agent-upstream-2026-10-27.md#H16 Memory initialization
arbol:research/hermes-agent-upstream-2026-10-27.md#H17 Memory defaults
arbol:research/hermes-agent-upstream-2026-10-27.md#H18 Work after delivery
-->

## Accounts, models, usage and failures

Hermes' provider resolver supports several credential paths, a credential
pool, OAuth and explicit endpoint/key resolution, with fallback behavior.
It can also select a Codex app-server runtime whose own login supplies the
account. A model/provider label therefore does not by itself prove the
credential or billing endpoint used. The TUI factory passes a credential pool
and configured fallback model into the agent. Default agent configuration
includes API retries and post-exhaustion recovery cycles.

The Hermes spec must pin a vendor family, account identity, effective endpoint,
API mode and allowed renewal behavior. Normal configuration discovery cannot
silently rotate into another paid account or model. Native refresh of the
same bound account is a separate concern from substitution. Prove the first
observable authentication/rate-limit error path rather than waiting for native
recovery to finish or assuming all retry controls are exposed publicly.

Standalone session creation supports model, provider, reasoning effort and
service tier, but canonical creation uses a different schema. Validate exact
effective settings before sending a prompt. `model.options` is the documented
Hermes-aware catalog surface; the minimal OpenAI `/v1/models` endpoint is not
a complete provider-aware picker. Each supported family still needs a
non-inference account check, catalog provenance, and an honest allowance
capability statement.

The generic usage wire has default-zero fields as well as optional cost and
cache fields. Arbol must omit unavailable quantities rather than manufacture
zeros. Establish actual producer semantics, cumulative versus turn totals,
resume baselines, subagent/auxiliary/compression costs and reported versus
estimated cost. Token consumption and account allowance are different reports.
No account family's check or allowance endpoint has been qualified here.

<!-- sources:
arbol:driver-contract/01-subscriptions.md
arbol:driver-contract/02-inference.md#Usage
arbol:driver-contract/04-errors-and-limits.md
arbol:research/hermes-agent-upstream-2026-10-27.md#H07 Session create overrides
arbol:research/hermes-agent-upstream-2026-10-27.md#H15 Native setup and coupled memory switch
arbol:research/hermes-agent-upstream-2026-10-27.md#H21 Provider resolution ladder
arbol:research/hermes-agent-upstream-2026-10-27.md#H22 Retry and recovery defaults
arbol:research/hermes-agent-upstream-2026-10-27.md#H28 Usage fields
arbol:research/hermes-agent-upstream-2026-10-27.md#H30 Canonical create controls
arbol:research/hermes-agent-upstream-2026-10-27.md#H31 Provider-aware model catalogs
-->

## Events, questions and completion

Hermes has structured message deltas/completion and tool start/completion
events. Those are useful inputs to an Arbol mapper, rather than a matching
public event schema. Tool results retain vendor meaning; terminal calls need
the shared `shell` command/cwd/output/exitCode form. Reconstruct authoritative
complete answer blocks in order, classify failures from native fields and
close every announced tool/question before one `finished` event.

Subagent progress has attribution fields, but their wire definition says the
identity fields are optional. Qualification must establish enough identity
for parent attribution in the selected version and exclude child prose from
the root answer. A final parent reply is not proof that its children ended.

For the standalone protocol, questions and approvals are server-to-client
JSON-RPC requests with corresponding responses and withdrawal events.
Capability negotiation advertises support. Hermes' clarification timeout can
be configured to unlimited, but the current helper otherwise has a 300-second
fallback. Arbol specifies no Driver-imposed question timeout; establish a
per-run compatible setting. Approvals and questions are distinct: approve
tool permissions according to DRV-3, while actual user questions map to
`ask_opened` and the control-input answer protocol. Native secret/vault/desktop
bridge requests require a declared mapping or refusal, not indefinite waits.

Most significantly, Hermes background processes can start in their own OS
sessions, and `persist_on_release` exempts them from ordinary lifecycle
cleanup. `AIAgent.close()` attempts resource and child cleanup, but this source
does not establish an Arbol completion barrier. A Driver process-group kill
alone cannot reach independently sessioned commands. Track resources through
native ownership and verify scoped cleanup, including persisted work,
subagents, browser/MCP resources and remote terminal backends where present.
Do not close unrelated native sessions to achieve it.

<!-- sources:
arbol:driver-contract/02-inference.md
arbol:driver-contract/03-tools-and-permissions.md
arbol:research/hermes-agent-upstream-2026-10-27.md#H19 Process sessions and persistence
arbol:research/hermes-agent-upstream-2026-10-27.md#H20 Agent close
arbol:research/hermes-agent-upstream-2026-10-27.md#H23 Message events
arbol:research/hermes-agent-upstream-2026-10-27.md#H24 Tool events
arbol:research/hermes-agent-upstream-2026-10-27.md#H25 Questions and capability negotiation
arbol:research/hermes-agent-upstream-2026-10-27.md#H26 Clarification deadline
arbol:research/hermes-agent-upstream-2026-10-27.md#H27 Child attribution
arbol-pi-driver:src/arbol_pi_driver/run.py
-->

## Integration work outside the new Driver

The current Trivial Trunk resolves a Driver name to `arbol-<driver>-driver`
and queries `info`, `subscriptions families` and `subscriptions list` before
inference. Its capability check currently accepts contracts 1 and 2. This
suggests a new Driver can use existing process orchestration if it conforms;
it does not prove every backend or route-picker path supports Hermes.

The shared conformance harness installs settings files for the explicit list
`claude`, `codex`, `pi`. A new Driver needs fixture support and appropriate
stand-in behavior, not just its own unit tests. Pi's build definition shows
the required packaged unit/contract/live checks and versioned contract/state
metadata. Keep the new Driver independent of Pi code and the caller.

Likely follow-on changes: a Driver code repository and corpus, build definition
and launcher, explicit family/default settings, shared conformance fixtures,
contract family/home documentation, and route discovery/catalog coverage.
Choose names, requirement prefix and concrete defaults in the spec phase.
Adding this route is distinct from migrating or retiring existing routes;
no such migration is proposed by this research.

<!-- sources:
arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/driver.py#capabilities
arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/driver.py#launcher_name
arbol:conformance/harness.py#ScenarioHome.part
arbol:conformance/harness.py#ScenarioHome.settings
arbol:conformance/README.md
arbol-pi-driver:arbol-build.json
-->

## Suggested specification outline

Mirror DRV-0–DRV-6, following the shared specification authoring conventions:

| Chapter | What this investigation says it must settle |
|---|---|
| 0 Overview/boundary | Transport and execution ownership, supported installed version/capability profile, native home, native startup fidelity and packaging. |
| 1 Subscriptions | Initial families, credential owner/binding, renewal, sign-in/check/model/allowance behavior and unsupported operations. |
| 2 Inference/history | Request settings, system prompt, native import/resume, images, continuity map and usage. |
| 3 Events/tools | Stream mapping, shell form, subagent identities, permissions, user/secret requests, native memory and tools-none. |
| 4 Errors/limits | Typed mappings, first observable refusal, native retries/fallback, partial output and time limits. |
| 5 Conformance | Requirement-to-check matrix, installed-tool probes, explicit live gates and packaged proof. |
| 6 Ownership/state | Run leases, native DB boundary, resource inventory, detached/background work, concurrent runs and verified settlement. |

Every chapter needs Purpose, Scope, Behaviour, Requirements, Interface, Known
problems and Decisions. Retain the distinction between an accepted spec and
an implementation whose checks pass. Record technical uncertainties as probe
tasks, and reserve owner questions for actual product choices.

<!-- sources:
arbol:driver-contract/README.md
arbol-pi-driver:specs/ownership-and-state.md
arbol-pi-driver:specs/readiness-review.md
-->

## Proposed probes before accepting the design

These are proposed experiments, not checks already performed. Start with
isolated state and synthetic providers. Keep raw results outside Git.

| Order | Experiment | Evidence needed to advance |
|---|---|---|
| 1 | Installed executable/runtime and public capability discovery | Exact version, package/interpreter paths, supported startup API, and whether ordinary invocation can change/install native state. |
| 2 | Execution/store ownership | One run can be stopped or lose its caller without harming a second run or ordinary Hermes; no unowned work survives. Establish either a supported owned worker boundary or the exact contract change required. |
| 3 | Native setup and run-scoped policy | Sentinel instructions, hooks, skills, plugin, MCP and system-prompt append remain active; memory reads/writes/review are off; config/auth bytes stay unchanged except specified same-account native refresh. |
| 4 | Credential/route fidelity | Conflicting configured defaults, pools and fallbacks cannot change the selected account, endpoint, model, effort or tier. Wrong credentials and rate limits surface promptly with structured evidence. |
| 5 | Rich native history | Fresh/resume/rebuild, edited/branched input, tool/error pairing, image history, native compaction and missing conversation; canonical import tested before considering text fallback. |
| 6 | Completion and cleanup | Foreground, background and persisted terminal work, descendants, nested agents, MCP/browser resources, cancellation, EOF, output failure and abrupt parent death. Measure native cleanup rather than infer it from reply completion. |
| 7 | Public event/control contract | Stable call attribution, text-before-tool ordering, complete blocks, partial failure, questions/withdrawals, no-control input, large results and tools-none. |
| 8 | Account and packaged qualification | Non-inference checks first; then minimal explicit live inference per initial family, shared conformance, relocated packaged executable and cross-Driver history checks. |

The first two experiments should decide whether proceeding within the current
contract is practical. Do not spend live inference quota to discover a
process/state ownership incompatibility that source and synthetic probes can
settle first.

<!-- sources:
arbol:driver-contract/05-conformance.md
arbol-pi-driver:specs/conformance.md
arbol-pi-driver:specs/ownership-and-state.md
arbol:research/hermes-agent-upstream-2026-10-27.md
-->

## Open questions

Product choices for the owner when drafting specs:

1. **Which vendor families should the first Hermes release support?** Proposed:
   choose explicit families/accounts after inspecting the intended installation;
   do not promise every Hermes provider. Existing Claude, Codex and Pi support
   does not determine the Hermes scope.
2. **Should Hermes persistent memory and learning be part of Arbol runs?**
   Proposed: retain DRV-3's memory-off rule and preserve normal skills. Keeping
   Hermes memory would require a deliberate contract decision defining its
   interaction with Arbol's authoritative history and cross-Driver continuity.
3. **May execution live in Hermes' shared gateway?** Proposed: preserve the
   current owned-run contract. If a supported owned worker cannot be qualified,
   present the shared-gateway design and precise changed guarantees for an
   owner decision before accepting specifications.

Technical questions to resolve through evidence:

- Which public, maintained Hermes entry point can provide run-scoped settings,
  canonical persistence and owned execution concurrently in the normal home?
  The sources examined expose pieces, not a qualified combined path.
- Can canonical rich import preserve the exact Arbol tool/image transcript and
  still resume normally after compaction? The text seed and foreign import
  paths are insufficient evidence; the mutation candidate has not been run.
- Can every memory path be disabled per run without disabling project context,
  configured skills or unrelated features? Does that propagate to child agents?
- What does scoped quiescence mean for Hermes' persisted processes, background
  review, prepared compaction, plugin/MCP/browser work and remote backends?
- Which account checks, catalogs, allowance endpoints, renewal mechanisms,
  error fields and usage producers are reliable for the chosen families?
- Which hooks/agent-record integration and backend route-picker changes are
  needed? This pass established the Trunk launcher boundary, not complete UI
  coverage or Hermes hook lifecycle parity.
- Is the currently installed target intended to be v0.22.5, newer main, or a
  future release offering a suitable execution API? No installation was found
  on PATH, and source findings do not choose a supported-version policy.

Search/index freshness for the initial retrieval was not established. New
artifact ingestion and retrieval must be reported separately from source
verification; none of them qualifies Hermes runtime behavior.

<!-- sources:
arbol:driver-contract/00-overview-and-boundary.md
arbol:driver-contract/03-tools-and-permissions.md
arbol:research/hermes-agent-upstream-2026-10-27.md
-->

## Selected Arbol code evidence

These excerpts use the configured source revisions in the baseline table.
The paths are relative to their named code repository.

### Caller capability checks and launcher convention

`arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/driver.py`, lines 107–117:

```python
async def capabilities(launcher: str, driver: str, subscription: str | None, cwd: str, home: Path,
                       stopped: Callable[[], bool]) -> None:
    migration_ready(home, driver, subscription)
    info = await capability_query(launcher, ["info"], cwd, stopped)
    if (not isinstance(info, dict) or info.get("driver") != driver
            or type(info.get("contract")) is not int or info["contract"] not in (1, 2)):
        raise CapabilityError("The launcher does not offer the selected Driver and a supported contract (1 or 2).")
    families = await capability_query(launcher, ["subscriptions", "families"], cwd, stopped)
    records = await capability_query(launcher, ["subscriptions", "list"], cwd, stopped)
    if (not isinstance(families, list) or not families or not isinstance(records, list) or not records
            or any(not isinstance(item, dict) or not isinstance(item.get("id"), str) for item in families)
```

`arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/driver.py`, lines 130–138:

```python
def launcher_name(driver: str) -> str:
    return f"arbol-{driver}-driver"


def find_launcher(driver: str, search_path: str | None = None) -> str | None:
    """The launcher of the Driver in the first folder of the search path that holds it, or None."""
    if not driver or "/" in driver or "\0" in driver:
        return None
    name = launcher_name(driver)
```

`arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/driver.py`, lines 205–209:

```python
    @classmethod
    async def start(cls, launcher: str, request_file: Path, working_folder: str) -> DriverRun:
        process = await asyncio.create_subprocess_exec(
            launcher, "run", "--control", "--request", str(request_file), cwd=working_folder,
            stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=None)
```

<!-- sources:
arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/driver.py
-->

### Shared fixture Driver list

`arbol:conformance/harness.py`, lines 265–270:

```python
    async def part(self, part: str, missing: bool = False) -> None:
        write_file(join(self.tool, "scenario"), f"{self.id} {part}\n", 0o600)
        settings = text_of(stringify({"toolPath": join(self.tool, "nonexistent") if missing else self.tool_path}))
        # Both contract filenames are installed before discovering the Driver with info.
        for driver in ("claude", "codex", "pi"):
            write_file(join(self.home, ".arbol", f"arbol-{driver}-driver.json"), settings, 0o600)
```

`arbol:conformance/harness.py`, lines 287–290:

```python
    async def settings(self, value: dict[str, Any]) -> None:
        text = text_of(stringify({"toolPath": self.tool_path, **value}))
        for driver in ("claude", "codex", "pi"):
            write_file(join(self.home, ".arbol", f"arbol-{driver}-driver.json"), text, 0o600)
```

<!-- sources:
arbol:conformance/harness.py
-->

### Pi verifies cleanup before history publication

`arbol-pi-driver:src/arbol_pi_driver/run.py`, lines 431–445:

```python
                verified = self.cleanup_verified()
                self.usage_snapshot()
                if self.signal_stop and self.outcome == "completed":
                    self.outcome = "cancelled"
                if self.outcome == "completed":
                    if not verified:
                        raise Failure("tool_failed", "Cleanup could not verify that every owned process ended.")
                    if self.mapper and (self.mapper.asks or any(
                        call.started and not call.ended for call in self.mapper.calls.values()
                    )):
                        raise Failure("tool_failed", "Native settlement left unclosed public activity.")
                    assert self.history and self.profile
                    self.history.commit(self.profile, self.emitter.texts)
                elif self.history:
                    self.history.invalidate()
```

<!-- sources:
arbol-pi-driver:src/arbol_pi_driver/run.py
-->

### Pi publishes continuity only after verified completion

`arbol-pi-driver:src/arbol_pi_driver/continuity.py`, lines 149–159:

```python
    def commit(self, profile: Profile, texts: list[str]) -> None:
        if self.map is None or self.request.cwd is None:
            return
        if self.ledger.phase != "terminal" or not self.ledger.sealed or not self.ledger.closed:
            raise Failure("internal", "Continuity cannot be written before verified completion.")
        assert self.metadata is not None
        path = self.safe_path(self.metadata["sessionPath"])
        # Inspection after native shutdown sees every native append, including hooks.
        raw = capture([str(profile.node), "--experimental-import-meta-resolve", str(HELPERS / "history-inspect.mjs"),
                       str(profile.package / "dist/index.js"), str(path), str(self.request.cwd)],
                      env=native_environment(profile))
```

<!-- sources:
arbol-pi-driver:src/arbol_pi_driver/continuity.py
-->
