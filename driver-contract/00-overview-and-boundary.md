---
role: authored
spec: DRV-0
status: accepted
---
# Driver Contract · 00 Overview and boundary

A [Driver](../GLOSSARY.md#driver) is the only part of Arbol 2 that knows a vendor's command-line tool. This specification fixes what a Driver owns, what it leaves to its caller, and how it is packaged. It matters because version 1 split the same work across three processes, and most defects listed in the Product Specification for accounts and routes sit on those seams.

## Next-release Pi routing amendment — in review

The owner selected Pi on 20 October 2026 and renamed the work **Pi Integration Specs Saga**. The first `arbol-pi-driver` must support z.ai Coding Plan and DeepSeek using the API keys already managed by OpenCode. Claude's target is the Anthropic subscription family only. OpenCode is the credential owner, not the new execution engine.

The [Pi specification set](../../sagas/pi-integration-specs/overview.md) and [coordinated A1/A2 amendments](../../sagas/pi-integration-specs/cutover.md) define the exact target: contract 2 for the breaking Claude-family removal; native-managed key attachment and authenticated non-inference checks; no key migration or deletion; private in-memory Pi key override; normal Pi home/discovery; and explicit refusal of stale Claude z.ai/default/gateway settings before inference. No automatic fallback to Anthropic or the retired route is permitted.

**Version boundary:** the accepted text and dated verification below describe the pre-cutover contract-1 Builds. For target contract 2, A1/A2 explicitly supersede the z.ai-on-Claude family, key injection, sign-in, catalog, usage and run branches. Native-login and Keychain modes retain their existing semantics except the retired family. The target amendment remains in review alongside PI-0–PI-6; it does not claim that existing code or installed settings have changed. Final acceptance waits for P5 normal-resource compatibility qualification and SYL-267 review. Implementation then coordinates caller/default/model migration, Pi history rebuilding, Anthropic regression and crash-safe cutover/recovery.

## Scope

Covered: the responsibility boundary, the Subscription families each Driver serves, packaging and hosting, the rules of the command line, the settings file, the rules that hold for every operation.

Not covered: Subscription operations ([DRV-1](01-subscriptions.md)); inference, tools, errors and conformance (DRV-2 to DRV-5); which Subscription or model a [Chat Session](../GLOSSARY.md#chat-session) uses, which is the caller's decision and is specified with the caller.

## What moves into the Driver

Observed in version 1: a Driver only ran turns. It received a ready credential with every turn and knew nothing about accounts. Sign-in, credential storage, refresh, usage and model lists lived in Arbol Root; the usage reading for one vendor lived in the Swift application.

| Responsibility | Version 1 owner | Arbol 2 owner |
|---|---|---|
| Starting the vendor tool, translating its stream, cancel | Driver | Driver |
| Recognising a rate limit or an authentication failure in vendor output | Driver, then re-recognised by Root from error text | Driver, reported as a typed error |
| Sign-in, sign-out | Root, plus an application window | Driver. The caller only shows what the Driver asks it to show |
| Credential storage and refresh | Root | Driver for a key or a token; the vendor tool for the owner's own sign-in in its default home ([The vendor tool's home](#the-vendor-tools-home)) |
| Account status, plan, usage | Root and the Swift application | Driver |
| Model list | Root | Driver |
| Isolation of one account from another | Root (environment per turn) and conventions about profile folders | Driver |
| Choosing the Subscription, model and effort for a turn | Root | Caller, unchanged |
| Repository rules, defaults, failover between routes | Root | Caller, unchanged |
| Chat sessions and their history | Root | Caller, unchanged: Arbol and its Trunks. A Driver keeps no conversation and is sent the messages with every run. It keeps only a map from the caller's chat session to the vendor tool's saved conversation (DRV-2) |
| Deciding a tool permission request | Root with the Effector | Nobody. The agent runs as trusted and nothing asks (DRV-3) |

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/05-intelligence-providers.md#Concept model`
- `arbol_deprecated_v1:daemons/core/arbol_core/subscriptions.py`
- `arbol_deprecated_v1:daemons/core/arbol_core/rpc/subscription.py`
- `arbol_deprecated_v1:daemons/core/arbol_core/orchestration/agent_attempt_execution.py#AgentAttemptExecutionService.compose_turn_options`
- `arbol_deprecated_v1:daemons/shared/arbol_shared/claude_cli.py`

## Drivers and Subscription families

A [Provider](../GLOSSARY.md#provider) value has two meanings that must stay apart: the *transport* (whose tool carries the bytes) and the *vendor family* (who is paid, whose models and usage apply). One Driver exists per transport. A Subscription belongs to a vendor family.

| Driver | Transport | Vendor families it serves | How the family signs in |
|---|---|---|---|
| Claude Driver | The `claude` command-line tool | `anthropic` | The vendor tool's own login |
| | | `zai` | A static key for z.ai's Anthropic-compatible gateway |
| Codex Driver | The `codex` command-line tool, through its app-server | `chatgpt` | The vendor tool's own login |

Not served in the first version: the direct ChatGPT backend route (`universe`, retired in version 1), a Cursor route (historical), key-billed API accounts of either vendor.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/05-intelligence-providers.md#Concept model`
- `arbol_deprecated_v1:daemons/core/arbol_core/subscriptions.py#DEFAULT_SUBSCRIPTIONS`

## Packaging and hosting

Proposed.

- **Form.** Each Driver is one command-line program, `arbol-claude-driver` or `arbol-codex-driver`, and nothing else. Its command line is its only interface: a caller written in any language starts the program, gives it what the operation needs as options and on standard input, and reads the result from standard output. There is no library to load, so Arbol contains no Driver code. Decided on 6 October 2026 ([DRV-D2](#decisions)).
- **Versions.** A Driver is built into numbered Builds that are kept side by side ([BLD-0](../builds/00-builds-and-versions.md)). The name on the search path is a launcher: without a build number it starts the newest working Build, and `-v a3` as the first argument starts Build `a3`.
- **Language.** Typed Python on CPython 3.14, with an exact patch and standalone distribution pinned in each Driver repository. Strict mypy, Ruff and standard-library `unittest` checks run during development; normal invocation uses only the standard library and the packaged interpreter. The owner superseded the original TypeScript decision on 7 October 2026 ([DRV-D1](#decisions), SYL-95). The shared build tool, launchers and conformance suite in the `arbol` repository are typed Python too (BLD-D15, SYL-166). The language is the Driver's own matter: nothing outside a Driver loads its code.
- **No resident service.** A Driver is not a daemon and has no socket, launch agent or build generation. Every invocation is one process that does one thing and ends. An inference run is one invocation: it lasts as long as the run and has the vendor tool as its child process.
- **State.** A Driver keeps its files under one state directory, named by its caller or taken from the default ([DRV-D3](#decisions)). By default it lies inside Arbol's own application folder; a Driver adds no folder of its own to the owner's home. It holds what the Driver knows about its Subscriptions, the map from chat sessions to the tool's saved conversations (DRV-2), and the records of runs in progress. The files and their formats are in DRV-6. It holds no conversation of the Driver's own, and no settings: those are in `~/.arbol` (below). Secrets are never in that directory tree. The vendor tool runs in its own default home, not in the state directory (below).
- **Vendor tool.** The Driver uses the tool installed on the machine. It does not bundle or update it.

### The vendor tool's home

Decided by the owner on 19 October 2026 ([DRV-D42](#decisions)). A Driver starts `claude` and `codex` with their default homes, `~/.claude` and `~/.codex`, as the Leather Bag starts them by hand. Arbol builds on the two tools and replaces none of their features, so a run has everything the owner set up for the tool: its settings, hooks, plug-ins, skills, MCP servers and instruction files ([DRV-3](03-tools-and-permissions.md#the-vendor-tools-full-power)). A run also shows up where the tool keeps its own history, such as `~/.claude/projects`, `~/.codex/sessions` and the Codex app's list of threads, and the tool's hooks see it as they see any other session ([PHK-1](../architecture/provider-hooks/01-hooks-on-this-mac.md)).

For example, a run of `arbol-claude-driver run --subscription anthropic …` starts `claude` without `CLAUDE_CONFIG_DIR`. It reads `~/.claude/settings.json`, runs the hooks set there, has the owner's plug-ins and `CLAUDE.md`, and is signed in with the owner's own sign-in of `claude`.

| Subscription | Its credential | How a run gets it |
|---|---|---|
| `anthropic`, which the Claude Driver has from the start | The owner's own sign-in of `claude`, which `claude` keeps and renews itself | Nothing is added: `claude` uses it |
| A further Subscription of the Anthropic family | A long-lived token made by `claude setup-token` at the Subscription's sign-in, kept in the Subscription's Keychain item like a key (DRV-1) | `CLAUDE_CODE_OAUTH_TOKEN` in the environment of that run's `claude` only (not tried yet) |
| `zai`, and any further one of its family | Its key, in the Subscription's Keychain item or from the owner's command | `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` in the environment of that run's `claude` only, as the alias `claude-zai` does |
| `chatgpt`, which the Codex Driver has from the start | The owner's own sign-in of `codex` in `~/.codex/auth.json`, which `codex` keeps and renews itself | Nothing is added: `codex` uses it |
| A further Subscription of the ChatGPT family | None: not offered. `codex` has no tested way to run as another account than the one signed in to `~/.codex`, and changing `auth.json` would change the account of every other `codex` on the Mac | `subscriptions create` refuses it with `invalid_input` |

| Rule | Detail |
|---|---|
| No home of the Driver's | The Driver sets neither `CLAUDE_CONFIG_DIR` nor `CODEX_HOME`, and removes either when it is inherited (DRV-0.5) |
| The Driver writes nothing there | What the tool writes in its home is the tool's own, as when it is started by hand. The one exception is what a Driver's specification names, such as the new session file the Claude Driver writes to continue a conversation ([CLD-D21](../../arbol-claude-driver/specs/02-inference.md#decisions)). A setting the Driver needs for a run, such as the tool's memory switched off (DRV-3) or its check for updates, is given on that run's command line or in its environment, never written to the owner's files |
| Runs side by side | Any number of runs, and the Leather Bag's own sessions, share the home as sessions started by hand do |
| The owner's own sign-in | Signing `anthropic` or `chatgpt` in is signing the tool in on this Mac. The Driver never signs it out and never removes it ([DRV-D43](01-subscriptions.md#decisions)) |
| Probes and live checks | A test Subscription, named `test-<family>` (DRV-5), keeps a home of its own in the test state directory; probes and live checks use it or homes created for them and never the default homes ([DRV-5](05-conformance.md), [DRV-D44](05-conformance.md#decisions)) |

Observed until 19 October 2026: each Subscription had a home of its own in the state directory, the Claude Driver kept each sign-in in a Keychain item named after that home, and of the owner's own setup a run had only the skills and the MCP servers (DRV-D27). A Driver run therefore had no hooks, no plug-ins, no settings and no instruction file of the owner's.

## The command line

Proposed. The rules below hold for every command. The commands themselves are listed with their subject: Subscriptions in [DRV-1](01-subscriptions.md), runs in DRV-2, tools in DRV-3.

```sh
arbol-claude-driver run --subscription zai --model glm-5.3-flash --effort high "say hi"
arbol-claude-driver subscriptions list
arbol-codex-driver info
arbol-codex-driver -v a3 info
```

| Rule | Detail |
|---|---|
| One invocation, one operation | The program starts, does what the command says and ends. Nothing is kept between invocations except in the state directory, the Keychain and the vendor tool's home |
| Build | `-v <build number>` as the first argument runs that Build of the Driver. Without it the default Build runs: the newest working one (BLD-0) |
| Input | Short values are options, written `--name value` or `--name=value`. Anything long is read from a file the caller names, never from an argument: an argument has a size limit and is visible to other processes |
| Secrets | A Driver is never given a secret, neither as an argument nor on standard input nor in a file. It reads a secret from the place its settings file names for it: the Keychain, where the caller or the owner has stored it, unless the owner names a command that prints it (DRV-1) |
| Output | The result is JSON on standard output: one document for a command with one result, one object per line for a command that reports as it goes (a run, a sign-in). A caller ignores fields and events it does not know |
| Errors | A command that is refused or fails writes `{ "error": … }` with the error object of DRV-4 as its result. A run reports its error in its final event |
| Exit status | 0: done as asked. 1: refused or failed. 2: stopped by the caller |
| Standard error | Diagnostics for a person. A caller never needs it to understand a result, and no secret is written there |
| State directory | `--state-dir <path>` on any command; otherwise the default |
| `info` | Prints the Driver's name, its package version and the build number of the Build that runs, the version of this contract it implements, its state directory, and the vendor tool it found: path, version, and whether that version is supported |

Three numbers are kept apart. The *build number* says which Build runs, such as `a3`; a new one appears with every build. The *package version*, such as 1.0.0, is the number in the Driver's package file, which the owner changes by hand (BLD-0). The *version of this contract* says which commands, events and codes a Driver offers; it changes rarely.

The version of this contract is a whole number, and the first one is 1. It rises when a command, an option, an event or an error code is removed or changes its meaning. Additions do not raise it. A caller checks it once with `info` and can then rely on everything this contract states.

```ts
interface DriverInfo {
  driver: string;                    // "claude" or "codex"
  version: string;                   // the package version, e.g. "1.0.0"
  build: string;                     // the build number of the Build that runs, e.g. "a3" (BLD-0)
  contract: number;                  // the version of this contract
  stateDirectory: string;
  settingsFile: string;                // the Driver's file in ~/.arbol, whether or not it exists
  tool: { name: string; path?: string; version?: string; supported: boolean; oldestSupported: string };
}
```

## The settings file

Proposed. Every Arbol component keeps its settings in the folder `~/.arbol`, one plain file per component, named after it. A Driver's file is `~/.arbol/arbol-claude-driver.json` or `~/.arbol/arbol-codex-driver.json`. It says which Subscription a run uses when it names none, which model and effort a Subscription uses when a run names none, the settings its vendor family defines for a Subscription (DRV-1), and where a Subscription's key comes from when that is not the Keychain. The file belongs to the Driver, and it is only a file: Arbol, or a person with any editor, reads and changes it directly. There is no command for it.

```json
{
  "defaultSubscription": "anthropic",
  "subscriptions": {
    "anthropic": { "defaultModel": "opus", "defaultEffort": "high" },
    "zai": {
      "defaultModel": "glm-5.3-flash",
      "settings": { "baseUrl": "https://api.z.ai/api/anthropic" }
    }
  }
}
```

```sh
arbol-claude-driver run "hello"     # the anthropic Subscription, its default model and effort, a new conversation
```

| Rule | Detail |
|---|---|
| When it is read | At the start of every invocation, so a change holds from the next run on |
| What is missing | Without the file, or without an entry: the Driver's own default Subscription (DRV-1), and for model and effort the vendor tool's own default |
| What is named wins | The file only fills in what a run leaves out. A model or Subscription that a run names and that cannot be used fails the run; nothing is put in its place |
| A default that does not fit | A `defaultEffort` that the model of a run does not take is left out, and the run says so in a `notice`. An effort the run itself names and the model does not take fails the run |
| What was used | The `started` event of a run names the Subscription, the model and the effort it runs with |
| A faulty file | A file that cannot be read as below refuses the run with `invalid_input`, naming the file and the fault. A key the Driver does not know is a fault too, and the message names it. For a command with one JSON result, notices are an optional `notices` array on that result; each has `code` and `message`. Settings must be a JSON object, and every known field must have the type in `DriverSettings`. A faulty field is named without printing its value |
| Who writes it | The Driver never does, except in an import the owner starts (CLD-1.17) |

```ts
interface DriverSettings {                 // ~/.arbol/<component>.json
  toolPath?: string;                       // the vendor tool's program; without it, the one found on the search path
  defaultSubscription?: string;            // a Subscription's identifier
  subscriptions?: Record<string, {
    defaultModel?: string;
    defaultEffort?: string;
    settings?: Record<string, unknown>;    // what the Subscription's family defines (DRV-1); never a secret
    secret?: SecretSource;                 // where the Subscription's key comes from; without it, the Keychain
  }>;
}

type SecretSource =
  | { from: "keychain" }                       // the Subscription's Keychain item (DRV-1), read with the system's `security` command
  | { from: "command"; command: string[] };    // a program and its arguments; what it prints is the key
```

## SYL-92 verification, 7 October 2026

SYL-92 passed the complete 38-scenario shared registry for both Python Drivers. Codex also passed 128 unit methods, Ruff and strict mypy from source; its standalone CPython 3.14.8 development candidate passed the same units and all 38 scenarios, and its relocated copy passed metadata and unit checks under a minimal environment. A fresh packaged `dev probe` passed against codex-cli 0.159.2 with zero inference requests. The packaged build gate sent exactly one no-tools ready message through `test-chatgpt`; it completed and reported tokens and usage before/after. The extended five-turn `dev live-check` orchestration and refusal gates passed offline, but the extended vendor run was not requested. Contract and state format remain 1. The first numbered Codex Build is the separate SYL-94 task.

Current records and source/package provenance: `~/Artifacts/arbol-codex-driver/research/conformance-2026-10-07/verification.json`, `coverage-audit.json`, `packaged-probe.json` and `packaged-build-check.txt` in that folder. Dated migration and TypeScript evidence below remains historical; unobserved real vendor failures remain unobserved. The coverage audit retains every former Verified by cell before this update.

## Requirements

| ID | A Driver must… | Origin | Verified by |
|---|---|---|---|
| DRV-0.1 | offer the commands of DRV-1 to DRV-4 with the same names, options, inputs, outputs and error codes as every other Driver. Family-specific data travels in fields this contract marks as family-specific | New | Claude Python: `C32`, `test_runtime.CompatibilityTests`, `test_runtime.TransportTests`; Codex Python: `C32`, `Foundation.test_arguments_settings_environment_and_error_sanitization` |
| DRV-0.2 | run with the Subscription, model and effort a request names, and with the defaults of its settings file for what the request leaves out. It never puts another model or another account in place of one that was named and cannot be used | Changed | Claude Python: `C10`, `test_runtime.CompatibilityTests`, `test_runtime.TransportTests`; Codex Python: `C10`, `Requests.test_request_defaults_and_ignored_settings_effort_provenance` |
| DRV-0.3 | keep a credential value only in the macOS Keychain or wherever the owner's own command keeps it (DRV-0.14), in the vendor tool's own credential store in its default home, and in the environment of the one child process that needs it. Never in a state file, log, event, error, command-line argument or address | Kept | contract |
| DRV-0.4 | start the vendor tool with its default home (`~/.claude`, `~/.codex`), set no variable that names another home, and write nothing there itself, except what a Driver's specification names, such as a new session file to continue a conversation: a setting the Driver needs for a run is given on that run's command line or in its environment. Only probes and live checks use homes created for them (DRV-5) | Changed | contract; probe |
| DRV-0.5 | build the environment of every child process from a short allow-list, then apply exactly one account. Inherited variables that select an account or configure the vendor tool never reach the child | Changed | Claude Python: `C8`, `test_runtime.CompatibilityTests`, `test_runtime.TransportTests`; Codex Python: `C8`, `AppServerTests.test_private_home_configuration_clean_environment_and_owner_cleanup`, `Foundation.test_arguments_settings_environment_and_error_sanitization` |
| DRV-0.6 | report the vendor tool it found: path, version and whether that version is supported. With a missing or unsupported tool every operation that needs it fails with a typed error naming the tool and the version | New | Claude Python: `C31`, `test_runtime.CompatibilityTests`, `test_runtime.TransportTests`; Codex Python: `C31`, `AppServerTests.test_handshake_version_and_effective_configuration_are_enforced`, `DevChecks.test_probe_missing_and_old_tools_preserve_public_version_refusal_details` |
| DRV-0.7 | report every failure as one error object with a code from the closed list of DRV-4, a message a Leather Bag can act on, and whether a retry can succeed. A caller never has to match error text | Changed | Claude Python: `C25`, `test_runtime.CompatibilityTests`, `test_runtime.TransportTests`; Codex Python: `C25`, `RunErrors.test_every_structured_class_and_exact_retry_policy` |
| DRV-0.8 | keep nothing between invocations except in its state directory, the Keychain and what the vendor tool keeps in its own home; every invocation starts from those alone | Changed | contract |
| DRV-0.9 | serialise changes to one Subscription, across processes, and never let operations on one Subscription wait for another | Kept | Claude Python: `C38`, `test_runtime.CompatibilityTests`, `test_runtime.TransportTests`; Codex Python: `C38`, `ConformanceState.test_another_subscription_changes_while_first_lock_is_held` |
| DRV-0.10 | leave no child process behind when a run ends, is cancelled or its caller goes away | Kept | Claude Python: `C17`, `test_runtime.CompatibilityTests`, `test_runtime.TransportTests`; Codex Python: `C17`, `AppServerTests.test_cancelled_request_leaves_transport_available_and_preabort_sends_nothing`, `AppServerTests.test_cleanup_survives_capture_failure_and_ends_ignoring_descendant`, `AppServerTests.test_startup_wrong_home_config_and_cancellation_gives_eof_before_force`, `Lifecycle.test_control_signals_eof_and_peer_stop_interrupt_once_then_cleanup` |
| DRV-0.11 | be one command-line program whose command line is its only interface: no library, no socket, and every invocation ends by itself when its operation is done | Changed | Claude Python: `C32`, `test_runtime.CompatibilityTests`, `test_runtime.TransportTests`; Codex Python: `C32` |
| DRV-0.12 | follow the command-line rules above for input, output, errors and exit status | New | Claude Python: `C32`, `test_runtime.CompatibilityTests`, `test_runtime.TransportTests`; Codex Python: `C32`, `OutputTests.test_serialized_output_gapless_events_lone_surrogates_and_cancelled_blocked_flush` |
| DRV-0.14 | take no secret as an argument, on standard input or in a file, and read every secret it needs from the place its settings file names: by default the Keychain, read with the system's `security` command, or else a command of the owner's that prints the secret. The one exception is an import the owner starts, which may read a key from the file it imports | Changed | Claude Python: `C32`, `test_runtime.CompatibilityTests`, `test_runtime.TransportTests`; Codex Python: `C32` |
| DRV-0.15 | be built into numbered Builds as BLD-0 says, report the build number of the Build that runs in `info` and at the start of every run, and keep the format number of BLD-0.13 in its state directory | New | Claude Python: `C32`, `test_runtime.CompatibilityTests`, `test_runtime.TransportTests`; Codex Python: `C32`, `Foundation.test_build_identity_ignores_cwd_and_rejects_invalid_metadata`, `PackagingTests.test_build_record_requires_matching_number_entry_and_version`; Codex SYL-94 Build 1: `build.clean-working`, `build.contract (C32 and numbered started events)`, `build.test-state-cleanup` |
| DRV-0.16 | read its settings file at the start of every invocation, never write it except in an import the owner starts, and refuse to run with `invalid_input` when the file cannot be read, naming the file and the fault | New | Claude Python: `C10`, `test_runtime.CompatibilityTests`, `test_runtime.TransportTests`; Codex Python: `C10`, `Foundation.test_arguments_settings_environment_and_error_sanitization`, `FamilySettings.test_an_unknown_family_setting_refuses_and_is_named`. An unknown key, from 14 October 2026: Claude `CompatibilityTests.test_settings_unknown_values_withheld_and_environment_allowlist`, Codex the two named above |
| DRV-0.13 | report with `info` its package version and build number, the version of this contract it implements and the vendor tool it found, and never remove or change a command, option, event or error code within one contract version | New | Claude Python: `C32`, `test_runtime.CompatibilityTests`, `test_runtime.TransportTests`; Codex Python: `C32`, `Foundation.test_build_identity_ignores_cwd_and_rejects_invalid_metadata`; Codex SYL-94 Build 1: `build.launcher-default`, `build.launcher-named`, `build.contract (C32)` |

## Known problems in version 1

- **Three owners for one account.** A turn's credential was loaded and refreshed in Root, used in the Driver and metered in the Swift application. Root recognised an expired credential by matching the Driver's error text.
- **Ambient state decided outcomes.** A logged-out account still ran, on whatever login the vendor tool had in its profile folder. The Codex route always ran as whoever was logged in to the vendor tool.
- **A deny-list for the environment.** The Claude route removed `ANTHROPIC_*` and five named variables before a launch and let everything else through. Observed on 5 October 2026: a shell started from a Claude desktop session carries more than twenty other `CLAUDE_*` variables, among them session and entry-point identifiers, which that list would have passed on. The same day, a `claude` subcommand started from such a shell replaced the stored Anthropic login of the default config folder: the tool behaved as if a host managed its credentials.
- **Resident Driver processes.** Each Driver was a versioned service with its own socket and launch job. Old and new builds ran side by side during an upgrade, and a partially rolled-back upgrade left turns blocked until manual recovery.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/05-intelligence-providers.md#Can two accounts of one vendor run at the same time, isolated?`
- `arbol_deprecated_v1:product-spec/05-intelligence-providers.md#Known problems and lessons`
- `arbol_deprecated_v1:daemons/shared/arbol_shared/claude_cli.py#environment`
- `arbol_deprecated_v1:daemons/core/arbol_core/orchestration/agent_attempt_execution.py#AgentAttemptExecutionService._refresh_bound_subscription_token`

## Vocabulary changes this contract requires

The Glossary entries below describe version 1. They need new wording once this specification is accepted; they are not edited yet.

| Entry | Change |
|---|---|
| [Driver](../GLOSSARY.md#driver) | No longer "subscription-agnostic": a Driver owns the Subscriptions of its vendor families |
| [Driver Instance](../GLOSSARY.md#driver-instance) | History. Arbol 2 has no versioned Driver process |
| [Subscription](../GLOSSARY.md#subscription) | Created and removed through its Driver; several per vendor family; the credential is no longer "passed to the Driver per Turn" |
| [Intelligence Provider](../GLOSSARY.md#intelligence-provider-ip) | Still the caller's configured route. It names a Driver and a Subscription; Root no longer hands a token to the Driver |

## SYL-94 numbered Build verification, 7 October 2026

Codex Build `1`, package version `1.0.0`, is the first working numbered Python
Build and the production default. It was built from a clean checkout of
`19fb51de21b074f62984fe28ad2450c3b1b09268`, using the repository's
`arbol-build.json` with locked uv setup, Ruff, strict mypy and standalone
packaging. The Build's own CPython 3.14.8 ran all 128 packaged unit tests; its
direct executable passed all 38 shared conformance scenarios, including
numbered `info` and `started` identity. The final `dev.build-check` passed with
exactly one no-tools ready request on `test-chatgpt`, using `gpt-5.6-luna` with
low effort. Its report retains actual tokens, tool/source/runtime provenance
and usage before and after. Contract and state format remain `1`.

Default and explicitly named launcher invocations both report Build `1` and
package version `1.0.0`. The direct executable also runs from an unrelated
folder with only HOME, PATH and LANG, without a source checkout or external
Python/uv/Node on PATH. Package and registry source records agree, and the
pinned standalone interpreter and packaged file digests passed verification.
The test state has no active run or temporary residue after the live gate.

An intentionally failing first check reserved Build `2`, retained its failed
record and log, and spent no inference quota. Build `1` stayed the default;
explicit selection of Build `2` was refused and listed only Build `1` as
available. The production build tool and launchers required no changes.
Extended vendor live checks were not run; previously unobserved real vendor
failures remain unobserved. Earlier candidate and migration records stay
historical.

Acceptance names and raw records:
`~/Artifacts/arbol-codex-driver/research/first-working-build-2026-10-07/verification.json`,
`coverage-audit.json`, `working-build.log`, `failed-build.log` and
`dev-build-check.json`. The numbered folder and launcher remain installed at
`~/Library/Application Support/Arbol/builds/arbol-codex-driver/1/` and
`~/.local/bin/arbol-codex-driver`.

## Python migration verification, 7 October 2026

SYL-95 verification is recorded in the requirement-level `~/Artifacts/arbol/driver-contract/python-migration-coverage-2026-10-07.json` and the Driver records `research/python-migration-2026-10-07/verification.json`. Python check names identify the copied standard-library unittest suites and the unchanged shared scenarios. Prior Driver unit/probe/live names refer to historical TypeScript evidence; unchanged shared build-tool and runner names remain active. Claude passes the complete 38-scenario suite; Codex passes its five original scoped groups (29 scenario invocations, with the same exclusions), and remains a development candidate. No historical live result is treated as fresh Python evidence, and previously unobserved vendor failures stay unobserved.

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| DRV-D1 | Implementation language | Original decision: TypeScript on Node.js 24, recorded on 5 October 2026. Migration: typed Python on CPython 3.14 with exact patch/distribution pins, strict mypy, Ruff and standard-library `unittest`; standalone interpreter delivery preserves the executable interface. Direct installed-vendor transports remain independent and standard-library-only. | Superseded 7 October 2026 by the owner's Python maintenance choice (SYL-95). Shared build, launcher and conformance infrastructure became typed Python too, by the owner's decision of 14 October 2026. Contract and state format stay at 1 only after bidirectional compatibility checks pass. CLD-D1 and CDX-D1 authentication decisions are unchanged |
| DRV-D2 | In what form does a Driver exist, and where does it run? | Each Driver is one command-line program and nothing else. Arbol holds none of its code and starts it once per operation. A run is one process and lasts only as long as the process that started it stays, so the product guarantee that work in progress survives closed windows and a restart of the coordinator is met by starting runs from an execution process separate from both. The contract has no command for finding and rejoining a run after that process itself restarts | Decided 6 October 2026 by the owner. It replaces the decision of the day before for a library (SYL-8) |
| DRV-D3 | Location of the state directory | Named by the caller with `--state-dir`. Default: `~/Library/Application Support/Arbol/drivers/<driver>/`, inside Arbol's own application folder | Decided 6 October 2026 by the owner: the proposed default, inside Arbol's application folder (SYL-32) |
| DRV-D4 | Keychain access from the Driver | A native binding to the Security framework. Version 1 found the `security` command unusable for writing: the value is visible in the process list, or the write silently stores nothing for long values. To check with it: whether macOS asks the owner for permission when a Driver reads an item that another program stored (DRV-0.14) | Decided 6 October 2026 by the owner, against the proposed default: no native binding. A Driver reads a key with the system's `security` command, which is safe for reading; version 1's trouble with it was about writing. The settings file can name a command that prints the key instead, so that another store, such as Proton Pass, can take the Keychain's place without a change to the Driver (SYL-37). To check when it is built: whether macOS asks the owner once when a Driver first reads an item that another program stored |
| DRV-D42 | Which home does the vendor tool run in? | Until 19 October 2026: a home of its own for each Subscription, in the state directory, with the owner's skills and MCP servers brought in (DRV-0.4 then, DRV-D27) | Decided 19 October 2026 by the owner: the default homes, `~/.claude` and `~/.codex`, so that a run has every feature and everything the owner set up for the tool, hooks included. Each tool runs on the owner's own sign-in; `zai` by its key, as before; a further Anthropic account by a token in `CLAUDE_CODE_OAUTH_TOKEN`; no second ChatGPT account for now ([The vendor tool's home](#the-vendor-tools-home)) |
| DRV-D5 | Oldest supported vendor tool versions | The versions the specifications were probed against: `claude` 2.1.289, `codex` 0.159.2 | Decided 6 October 2026 by the owner: the proposed default. What matters is that a Driver keeps working with the newest version of its tool; nothing is done for older ones (SYL-38) |
| DRV-D20 | May commands an agent started outlive the run? | No, on either Driver: DRV-0.10 and DRV-2.19 hold without exception. Version 1 ended them on the Claude route and left them running on purpose on the Codex route. A real test on 6 October 2026 found one kind of program that no Driver can find again; the owner accepted that limit the same day (DRV-D33 in DRV-2) | Decided 5 October 2026 by the owner: the proposed default (SYL-11) |
| DRV-D34 | How are settings faults and notices reported by a command with one result? | Validate known fields by the interface types, without printing their values. A key the Driver does not know refuses the file with `invalid_input` and is named. Other notices go in an optional `notices` array of objects with `code` and `message` on the result. Family settings are validated by the family when used | Decided 6 October 2026 during SYL-75, a technical choice. Until 14 October 2026 a key the Driver did not know was ignored and named in a notice; that day the owner decided that it refuses the file, in a Driver as in the classifier (CLS-D5 in CLS-0) |
| DRV-D24 | Where are settings kept? | Every Arbol component keeps its settings in the folder `~/.arbol`, one plain file per component, which Arbol or any editor reads and changes. A Driver's file holds the default Subscription, the default model and effort of each Subscription, and each Subscription's own settings. Each Driver has one Subscription per family from the start, and the Claude Driver's default is `anthropic` | Decided 6 October 2026 by the owner |

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:daemons/shared/arbol_shared/macos_keychain.py`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#6. Many resident services with strict, version-coupled contracts`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#Product guarantees the rewrite must keep`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#Decisions for the successor's design`
