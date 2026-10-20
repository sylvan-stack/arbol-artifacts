---
role: authored
---
# Arbol Driver migration to Python implementation plan

Replace the TypeScript implementations of `arbol-claude-driver` and `arbol-codex-driver` with typed Python in their existing repositories. Python is the owner's preferred language for long-term maintenance. The migration preserves the accepted Driver architecture and public behavior, with contract version 1 and state format 1 where compatibility checks prove that they remain valid.

The scope is the code already implemented. Claude has a complete implementation and a historical working Build. Codex has implemented its base, Subscriptions, fresh runs, continuity, and stopping/recovery; its remaining feature and delivery issues continue after the port. The implementation work is tracked in [SYL-95](https://linear.app/amorphius/issue/SYL-95/migrate-the-implemented-claude-and-codex-drivers-from-typescript-to), under [SYL-74](https://linear.app/amorphius/issue/SYL-74/build-the-two-drivers).

## Language and tooling

Use CPython 3.14, pinning an exact supported patch and distribution during setup. Add `pyproject.toml`, `.python-version`, and `uv.lock` in each Driver repository. Require strict mypy checks, Ruff, and standard-library `unittest` suites, including asynchronous lifecycle tests. Keep these development tools out of normal Driver invocation. Validate input and vendor JSON at runtime; annotations alone do not validate decoded records.

Port the current direct vendor transports: Claude's installed CLI with bidirectional stream JSON, and Codex's installed app-server with JSON-RPC over standard streams. Use `asyncio`, typed request/event/error models, and standard-library process and filesystem facilities. Runtime dependencies should remain standard-library-only unless a concrete requirement warrants an explicitly recorded exception. SDK adoption is a separate change; it is unnecessary for the language port.

Keep the Drivers independent. Share conventions and packaging recipes, while retaining separate vendor transport code, stand-ins, and runtime packages. The shared `arbol-builds`, launchers, and conformance suite remain in TypeScript/Node. They already start arbitrary executable entries, so the Python port does not require rewriting that infrastructure or Arbol's callers.

## Compatibility requirements

Preserve command names, options, input sources, JSON fields and events, ordering, exit statuses, error codes, settings paths, default state paths, Keychain identities, Subscription homes, and account selection. Preserve ARBOL_TEST_TIME_SCALE for fixed contract waits in the stand-in/conformance environment; caller-specified idle and total limits remain unscaled. Preserve recognized-but-unimplemented Codex operations and their current refusal behavior until their existing issues implement them.

Treat the accepted specifications as the target behavior. Use the TypeScript code, fixtures, and recorded checks as a reference; do not reproduce a known defect merely to match it. Any intentional externally visible change must first update the relevant specification and compatibility decision.

Cross-language compatibility must include:

- **History and paths.** Exact compact JSON bytes used for SHA-256 history fingerprints; Unicode, quotes, controls, lone/split surrogates, streamed snapshots, merged assistant blocks, image bytes, chat identifiers, and Claude project-folder encoding. Python's default JSON formatting and Unicode escaping must not silently change existing fingerprints. Compare committed golden vectors, including TypeScript-created histories resumed by Python and Python-created histories resumed by the retained baseline TypeScript executable, including the Claude Build where available.
- **State and credentials.** Existing format-1 records; private permissions; fsync and atomic replacement; lock creation and stale-owner reaping; PID plus process-start identity; conditional map invalidation; concurrent account and usage updates. Keep Keychain service/account names, including the custom-state suffix based on the real state path.
- **Process lifecycle.** Clean child environment allow-lists; private vendor homes; independent reads of stdout, stderr, and control input; serialized output with flow control; per-vendor interruption behavior; verified descendant groups; stop deadlines; cleanup after a killed Driver; and exactly one final event after cleanup when output remains writable; cleanup and exit remain bounded when output is broken or accepts no data.
- **Mixed implementations.** Exercise old and new executables concurrently against isolated shared test state: locking, peer stopping, duplicate run IDs, cleanup election, and protection of newer session/account records. Rollback needs write compatibility as well as readable JSON.

## Phase 1 Record the baseline and update the specifications

Capture the actual current commit and worktree state of both repositories when implementation starts. Preserve current fixture files and evidence, including unsuccessful attempts. The planning baseline on 7 October 2026 is Claude `5ea45f2` and Codex `37daaf8`; refresh this if either repository advances. Claude's historical Build record names an earlier source revision, so it cannot stand in for fresh Python verification.

Record the owner's dated supersession of DRV-D1, preserving the original decision and rationale as history. Update both Driver overview language statements and Claude's development/check/packaging decisions, including CLD-D13, CLD-D15, and CLD-D16, with Python equivalents. CLD-D1 and CDX-D1 concern authentication and remain intact. Audit active task instructions for TypeScript-only commands and republish changed specification originals to Linear before implementation diverges from them.

Create a coverage matrix mapping each implemented requirement to its Python check and separating Codex's outstanding requirements. Produce deterministic cross-language fixtures from the baseline. Normalize only noncontractual identifiers and timestamps; preserve event order, outcomes, errors, and state changes.

**Exit criterion:** the language amendment is published, the baseline and compatibility vectors are recorded, and every implemented behavior has an assigned migration check.

## Phase 2 Establish the Python foundation

Create each executable entry and internal package layout. Port argument handling, settings/default selection, typed errors, `info`, package/Build identity, tool discovery/version checks, environment construction, storage primitives, locks, and recovery ownership. Use monotonic clocks for deadlines and persisted wall-clock values where the accepted state format requires them.

Port Subscription creation, listing, relabeling, removal, sign-in/sign-out, status, usage, models, cached reports, and private-home configuration. Claude additionally needs the z.ai gateway, Keychain/command secret sources, and explicit import behavior. Keep credential values out of events, state records, arguments, and diagnostics. For Claude, preserve the real macOS HOME used by login/Keychain access while CLAUDE_CONFIG_DIR and operation working directories select the private Subscription storage; do not substitute the private directory for HOME.

**Exit criterion:** foundation and Subscription tests pass for Python, existing state and credentials remain accessible, and concurrent operations preserve account independence and newer records.

## Phase 3 Port the complete Claude Driver

Port request validation, model/effort selection, images, whole blocks and deltas, thinking, token usage, text output, and the bidirectional control protocol. Preserve native continuation/reconstruction and fallback reasons; tools and shell normalization; owner skills/MCP loading; questions and withdrawals; parent attribution; sub-agents and background completion.

Port stopping, signal/EOF/broken-pipe handling, process-group ledgers and orphan recovery. Ensure coroutine cancellation cannot abandon required cleanup. Preserve field-based vendor error classification, retry notices, credential rejection handling, start/idle/total time limits, and usage-report merging.

Port all implemented development commands and the vendor stand-in, retaining the recorded protocol fixtures. Adapt implementation-specific tests to Python without targeting a literal test-count match.

**Exit criterion:** meaningful unit coverage, cross-language compatibility tests, and all 38 existing Claude conformance scenarios pass against the Python executable, with no contract checks weakened to accommodate the port.

## Phase 4 Port the implemented Codex Driver

Port the initialization handshake, bounded JSONL framing and fragmented UTF-8 handling, request IDs and response correlation, notifications arriving before responses, server-initiated requests, request timeouts, account/login/catalog/usage operations, and fresh inference runs.

Port ordered answer/reasoning events, image files, native thread resume/history injection and fallback, exact continuity fingerprints, conditional session-map settlement, run registration, stopping, active-child interruption, descendant cleanup, and orphan recovery. Include late child starts, blocked output, and the current per-vendor interruption and cleanup bounds.

Retarget current Codex fixture tests and scoped conformance wrappers to Python. Record the exact scenario/part set currently implemented; carry existing applicable checks forward without enlarging exclusion lists.

**Exit criterion:** Python matches the implemented Codex coverage and compatibility requirements. Outstanding features remain explicit in SYL-90, SYL-91, SYL-92, and SYL-94.

## Phase 5 Package and verify the Python executables

Package a standalone CPython distribution inside each delivery artifact, with the Driver modules, fixtures, and packaged check modules. Build the executable entry so it directly execs that artifact's interpreter and preserves arguments, streams, signals, process identity, and working directory. Record the exact interpreter version, architecture, and distribution digest. Verify the artifact at its final location; ordinary virtual environments must not be copied as if relocatable.

Normal invocation must require no source checkout, development environment, uv invocation, download, or dependency installation. Use uv during provisioning/build preparation only. Retain minimal `package.json` version metadata because the existing build tool reads it; check that it agrees with Python package metadata. Port the Driver build/package/check scripts to Python while leaving the shared build tool and launcher unchanged.

Rehearse compatibility, launcher behavior, failing checks, and withdrawal rollback in an isolated test registry before production cutover. For Claude, produce a new numbered Build through the existing registry after these gates pass. Its packaged unit tests, full conformance check, and required one-message vendor Build check must all pass. Test the deliberately failing Build path and verify that it preserves the prior working default.

For Codex, verify a packaged development candidate against its implemented coverage. This task does not create a fully working Codex numbered Build before its outstanding features and checks exist. SYL-92 gathers complete development checks; SYL-94 creates the first working Python Build after those pass.

**Exit criterion:** Claude has fresh passing packaged Build evidence; Codex has a reproducible runnable Python candidate with its exact implemented coverage recorded; neither artifact depends on the Driver's TypeScript implementation.

## Phase 6 Switch delivery and retire the active TypeScript implementations

Complete compatibility/probe gates and the isolated rollback rehearsal before the final Claude Build checks can mark it working: the registry then makes it the default automatically. After it becomes working, verify the real default and explicitly selected older Build, their `info` identity, and leave the production Python Build working. A withdrawn Build cannot be reactivated by the current tool. Withdrawal affects future launches; active invocations must finish or follow the accepted stopping/recovery rules. Preserve retained Builds and historical evidence.

Replace the active Driver source, entry, stand-in, unit tests, and packaging scripts with Python after their checks pass. Keep the old implementation available through history and retained Builds. Node remains needed for the shared launcher/build/conformance machinery.

Update repository READMEs, development commands, the requirement verification matrix, and changed specification copies. Continue the remaining Codex issues in Python in their existing order.

**Exit criterion:** both existing implementations are migrated and verified at their respective coverage levels; the active Driver code is Python; delivery and rollback are documented; remaining Codex feature work is ready to resume.

## Validation and completion

The migration task is complete when all of the following are recorded with current source provenance:

1. Strict static checks and lint pass; meaningful unit, fixture, and malformed-input tests preserve prior behavior.
2. Claude passes all 38 existing conformance scenarios. Codex passes its unchanged implemented scenario/part set. The shared runner starts the packaged Python entries.
3. Cross-language fingerprints, Keychain identities, saved-session continuation, and format-1 state compatibility pass in both directions.
4. Lifecycle checks cover normal completion, stop controls, signals, EOF, broken/slow output, malformed vendor records, timeouts, killed owners, late child starts, and concurrent recovery. No stale PID is signalled and finalization obeys the accepted bounds.
5. Fresh no-prompt probes record the installed supported vendor versions, private homes, and configuration preservation. The required tiny Claude Build check uses the designated test Subscription and the packaged executable; previous TypeScript live evidence does not validate Python.
6. Claude's numbered Build/launcher/failure/rollback checks pass. Codex's candidate remains explicitly partial until SYL-90 through SYL-94 complete.
7. Requirement tables, delivery instructions, and Linear copies agree with the Python implementation, without presenting unsupported or historically unobserved vendor failures as verified.

Follow the [existing working instructions](https://linear.app/amorphius/document/driver-implementation-how-to-work-on-a-task-and-the-order-of-tasks-2e262fb1d277) for test accounts, clean environments, quota, small commits, and publication. Additional live checks run only within the existing authorization rules; the unit and conformance suites remain offline and credential-free, while the separately named Build live check uses the designated test Subscription.

## Existing task order

Insert the migration issue under [SYL-74](https://linear.app/amorphius/issue/SYL-74/build-the-two-drivers), before the remaining Codex tasks. The migration issue blocks SYL-90 and SYL-91; their existing dependencies then lead to SYL-92 and SYL-94. Do not reopen completed implementation issues or duplicate the unfinished features inside the port.

Mycel, Arbol UI/caller rewrites, a shared Driver runtime library, vendor SDK adoption, and new account/tool features are outside this migration.

## References

- [Driver Contract overview and boundary](https://linear.app/amorphius/document/driver-contract-00-overview-and-boundary-1033d737cd03)
- [State and simultaneous calls](https://linear.app/amorphius/document/driver-contract-06-state-and-simultaneous-calls-0862c11a65fa)
- [Conformance](https://linear.app/amorphius/document/driver-contract-05-conformance-34932d51618d)
- [Builds and versions](https://linear.app/amorphius/document/builds-00-builds-and-versions-08bf00dd79a4)
- [uv managed Python distributions](https://docs.astral.sh/uv/concepts/python-versions/#cpython-distributions)
- [Python virtual environment portability](https://docs.python.org/3/library/venv.html)
