---
role: authored
spec: DRV-5
status: accepted
---
# Driver Contract · 05 Conformance

How a Driver proves that it meets this contract. One suite of scenarios runs against every Driver, with a scripted stand-in for its vendor tool, and needs no network, no account and no quota. Beside it are probes of the installed vendor tool, which cost nothing, and live checks, which spend quota and run only when asked for. This specification lists the scenarios and the rules for the other two. It matters because version 1's tests ran against a stand-in written for an older tool version and kept passing while the installed tool had moved on, and because probing a real tool on a real machine can damage the owner's own setup, as happened on 5 October 2026.

## Scope

Covered: the stand-ins, the scenarios of the shared suite and the requirements each covers, the rules for probes and live checks.

Not covered: unit tests of a Driver's own code, which each Driver chooses; testing the caller.

## Behaviour

### Three kinds of check

| Kind | Runs against | Costs | When |
|---|---|---|---|
| Contract suite | The Driver, with a stand-in for the vendor tool | Nothing | On every change, without network |
| Probe | The installed vendor tool, sending no prompt | Nothing | When the installed tool changes, and before a specification is accepted |
| Live check | The installed tool with a real account | Quota | One real message when a Build is made (BLD-0). Every other one only when someone asks for it |

The contract suite starts each Driver's program as a caller would, through its command line, and reads what it writes. It shares no code with a Driver and does not depend on the language a Driver is written in.

### Stand-ins

Each Driver ships an executable that takes the vendor tool's place: it reads what the Driver writes, answers from a script, and records what it received, including the names of the environment variables it was started with and the paths it was asked to use. A script is a sequence of the tool's own records or messages, taken from a probe record and naming the tool version it was observed on. When a probe of a new tool version shows a changed shape, the scripts change with it.

Observed in version 1: the Claude route's tests ran against a scripted stand-in written for tool version 2.1.81. By version 2.1.289 the tool reported a failed login as a result of subtype `success`, and the tests could not notice.

<!-- sources:
arbol:tests/unit/test_claude_native_turn.py
arbol:tests/integration/conftest.py
-->

### The scenarios

Every scenario runs against each Driver. A Driver that does not offer something a scenario needs, such as questions from the agent on the Codex Driver, passes by refusing it in the specified way.

| ID | Scenario | Covers |
|---|---|---|
| C1 | The Subscriptions a Driver has from the start are listed, one per family. Create, list, relabel and remove a further Subscription of each family; `list` contacts no vendor | DRV-1.1, 1.13, 1.14, 1.15 |
| C2 | Sign in through each step kind the family uses; a second sign-in replaces the first, which ends with `in_use`; one left alone ends after five minutes | DRV-1.5, 1.6, 6.9 |
| C3 | A key with a non-ASCII character, stored in the Subscription's Keychain item, is refused with up to three characters named, and is removed from the item | DRV-1.4, 1.26 |
| C4 | The vendor rejects the credential during a check and during a run: the Subscription becomes `needs_attention` with a remedy, and the run fails with `credential_rejected` | DRV-1.7, 4.7 |
| C5 | Sign-out and removal with a run in progress are refused, and succeed when forced, after the run is cancelled | DRV-1.12 |
| C6 | The `sign-in` command is killed while an attempt is pending: the Subscription is `signed_out` | DRV-1.24, 1.25, 0.8 |
| C7 | No secret appears in any event, error, state file, log line or argument recorded by the stand-in, and the state directory holds no copy of a login the stand-in keeps in its home | DRV-0.3, 1.3, 1.8 |
| C8 | The stand-in records the names of its environment: no inherited `CLAUDE_*`, `CLAUDECODE`, `ANTHROPIC_*`, `OPENAI_*` or `CODEX_*` variable is among them, although the test sets several | DRV-0.5 |
| C9 | The test's home holds sentinel files where the owner's own setup of the tool would be: none is changed, and nothing is read but the skills and the list of MCP servers, in the places the Driver's specification names | DRV-0.4 |
| C10 | A plain completed run: event order, gapless sequence numbers, one `finished`. A run that names no Subscription, model or effort takes them from the settings file, and without one from the Driver's and the tool's defaults; `started` names what is used; a settings file that cannot be read refuses the run | DRV-2.1, 2.3, 2.4, 0.2, 0.16 |
| C11 | Text, a tool call, more text: the first `text` precedes the `tool_started`; every call is finished before `finished`. A command in a terminal is shown as `shell` with `command` and `output`, and a `shell` call of a history reaches the stand-in in the tool's own form | DRV-2.5, 2.6, 3.19 |
| C12 | The tool reports a failure under a subtype or status that looks like success: the run is `failed` | DRV-2.7 |
| C13 | Usage events are totals; a field the tool does not report is absent | DRV-2.15 |
| C14 | Continuity for one chat session: fresh; resumed on the next run with the same messages; rebuilt after an edited earlier message, after a replaced reply, on another Subscription, when the working folder has changed, when the system prompt has changed on a Driver whose tool keeps a conversation's first prompt (DRV-6), when the saved conversation is gone, while another run uses it, and when no chat session is named, each with its reason. On a Driver whose tool takes a new prompt, a changed system prompt continues the conversation and reaches the stand-in. A rebuilt conversation reaches the stand-in with the earlier tool calls and their results. The map holds no message. A run that fails removes the entry it was continuing | DRV-2.11, 2.12, 2.13, 2.34, 2.35, 6.11, 6.12, 6.14, 6.15 |
| C15 | Stop during a streamed answer, with a question open, with a tool call running and while a sub-agent works: the order of events, the reasons, the limits of 2 and 15 seconds. After the final event the stand-in's record shows nothing more from the sub-agent | DRV-2.16, 2.17 |
| C16 | Stop of a finished run and of an unknown run succeeds | DRV-2.18 |
| C17 | The stand-in starts a process that is left in the background of the command that started it; after the final event it is gone. It is also gone after the suite, in the caller's place, closes the run's output, ends its control input or sends its process a termination signal | DRV-2.19, 2.26, 0.10 |
| C18 | Two runs at once on one Subscription; one fails, the other is unaffected; a slow reader of one does not delay the other | DRV-2.21 |
| C19 | A run with tools off: one text, no folder left behind. On a Driver whose tool cannot be started without its tools, the stand-in is started locked down, and a tool call it reports nonetheless is passed on without failing the run | DRV-2.20 |
| C20 | A tool result over 200 KiB, as text and as structure, is cut and flagged | DRV-2.22 |
| C25 | The stand-in sends a request for permission although nothing should ask for one: it is approved, one that makes no sense is declined, a `notice` is emitted, and only that run is affected | DRV-3.22, 0.7 |
| C26 | Each row of the Driver's error mapping, fed as the tool's own records | DRV-4.1, 4.4 |
| C27 | A rate limit with and without a time from the vendor: the wait is present only in the first case; nothing is retried | DRV-4.5, 4.6 |
| C28 | The tool retries a rejected credential: the run ends at the first retry | DRV-4.8 |
| C29 | The idle limit fires on a silent tool, and does not fire while a tool call runs or a question is open; the start limit fires on a tool that never starts | DRV-4.9, 4.10, 4.11 |
| C30 | Limit information during a run becomes the Subscription's last usage report when the run ends | DRV-4.13 |
| C31 | The tool is missing, and reports a version below the oldest supported | DRV-0.6, 4.14 |
| C32 | The command line: every command and option this contract names is accepted; `info` names the versions and the tool; an unknown command or option is refused with `invalid_input`; the sign-in of a key family names a Keychain item, goes on once the suite has stored a key there, and takes none as an argument, on standard input or from a file; with a command named as the source of the key, the key is what that command prints; exit statuses 0, 1 and 2 match what happened; `info` and `started` name the build number of the Build, and `info` the package version | DRV-0.1, 0.11 to 0.15, 1.23, 1.26 |
| C33 | A run without a control input completes, and a question the stand-in raises in it is declined with a message. From a second invocation, `runs list` shows a run in progress and `runs stop` ends it as `cancelled`. A malformed line on a control input is answered with `control_refused` and the run goes on | DRV-2.25, 2.27, 2.28, 3.30, 6.7, 6.8 |
| C35 | A run with tools: the stand-in is started in the mode that asks for no permission, with no list of tools and with nothing switched off but its own memory. A call the stand-in refuses by itself ends as a failed `tool_finished`, and the run goes on. What a sub-agent did carries the call that started it, and its text is not in the answer. Where the stand-in reports the agent's part as ended while a sub-agent or a command left in the background still works, the run goes on and ends after the last part; the idle limit does not end it meanwhile | DRV-3.20, 3.21, 3.23, 3.24, 3.25, 3.32, 4.10 |
| C36 | A question from the agent is carried, answered and declined; a second answer, an answer after withdrawal and a malformed answer; two questions answered in reverse order. The Codex Driver emits none | DRV-3.26 to 3.29 |
| C37 | A skill and an MCP server set up under the test's home, in the places the Driver's specification names for the owner's own setup, reach the stand-in in a run with tools, and nothing there is changed | DRV-3.31, 0.4 |
| C38 | A Driver is killed outright in the middle of a run: the next call ends the stand-in that outlived it and removes the run's record, its folder and the map entry it was continuing. Two calls change one Subscription at the same moment and both changes are kept. A change to one Subscription goes through while another Subscription is signing in. A state directory with a higher format number is refused with `state_newer`. An empty state directory works | DRV-0.9, 1.10, 6.1, 6.3, 6.5, 6.10 |
| C39 | Two Subscriptions of one family: each starts the stand-in in a home of its own; signing one out leaves the other signed in; a conversation saved under one is not continued under the other | DRV-1.2 |
| C40 | Refusals before the tool is started. A run and a request for the model catalog on a Subscription that is not signed in; a run that names a folder that does not exist, a run identifier in use, or a model or effort the catalog does not have: each is refused in one result or one `finished` event, and the stand-in's record shows that no run was started. `check` works on a Subscription that needs attention, and `usage` on a signed-out one answers `needs_sign_in` | DRV-1.11, 2.2 |
| C41 | Usage and the model catalog. The stand-in is asked for usage only when the `usage` command runs. Each of the four outcomes is reported; a value the stand-in leaves out is absent; the last report with the outcome `ok` comes back with the Subscription's record. The catalog names its source, and is the built-in list when the stand-in cannot answer. Account details come from the stand-in and are gone after sign-out | DRV-1.16, 1.17, 1.18, 1.19, 1.22 |
| C42 | A run fails after it has produced text and started a tool call: the events already written stand, `finished` reports the usage so far, says that output was produced and names the unfinished call, and the stand-in is not started again | DRV-2.8, 2.9, 2.10 |
| C43 | The state directory cannot be written when a run starts: the run ends with one `finished` event, `failed` with `internal` | DRV-4.15 |

C21 to C24 covered tool sets, levels of asking and permission questions. They were withdrawn on 6 October 2026 with DRV-D12. C34 was withdrawn earlier. Their numbers are not used again.

### How the suite drives a Driver

The suite is one program for all Drivers. It lives in the `arbol` repository, in the folder `conformance`, and is started as `arbol-conformance --driver <command>`, with `--only <scenario ids>` to run a part of it. The command is whatever starts the Driver: a launcher, or the program of one Build.

For every scenario the suite sets the Driver up from nothing:

| What | How |
|---|---|
| A home of its own | A new temporary folder is the home directory of the Driver's process. The settings file, the state directory in its default place and the owner's own setup of the tool are therefore all the test's own, and the real ones are out of reach |
| The stand-in instead of the tool | The settings file names `toolPath`: a small launcher the suite writes into `<home>/tool/`. It starts the Driver's stand-in and tells it that folder |
| What the stand-in plays | The suite writes the scenario's identifier, and the part of it where a scenario has several, into `<home>/tool/scenario`. Each Driver's stand-in holds its own script for every scenario |
| What the stand-in saw | The stand-in appends one line per start to `<home>/tool/received.jsonl`: its arguments, the names of its environment variables, its working folder, and the outcome of checks only it can make, such as whether an earlier `shell` call arrived in the tool's own form |
| Keys | A key comes from a command in the test's home (the `secret` setting of DRV-0). One scenario, C3, uses the Keychain: the suite stores a made-up key under the service name of the test's own state directory, which is never the owner's (DRV-1) |
| Vendor addresses | Where a Driver asks a vendor directly, as for z.ai's quota, the Subscription's address setting points at a listener the suite runs on this machine. No scenario leaves the machine |
| Time | The suite starts the Driver with `ARBOL_TEST_TIME_SCALE=<n>` in its environment. A Driver divides every fixed wait of this contract by that number: the five minutes of a sign-in, the 2 and 15 seconds of a stop, the 10 seconds of a lock. Limits a request names are not scaled |

Every `received.jsonl` record has `scenario` and `part` strings, `arguments` and `environment` arrays of strings (environment variable names only), a `workingDirectory` string and a `checks` object. A version-probe script also records its `toolVersion` string, or `null` for a missing tool; the suite compares the version reported by `info` with that script value without reading the vendor protocol. These common record fields are the same for both stand-ins.

The suite judges a scenario by what the Driver writes on its standard output, by its exit status, by the files in the state directory where a scenario names them, and by `received.jsonl`.

### The checks a Build carries

Every Build of a Driver has four commands for checking it. They are part of the Driver's program, under `dev`, so that a Build can be checked as it stands.

| Command | What it does | Costs |
|---|---|---|
| `dev stand-in <folder> -- <arguments>` | Runs the stand-in for the vendor tool. Only the suite's launcher calls it | Nothing |
| `dev probe` | Runs the probes of this specification against the installed tool and writes their record | Nothing |
| `dev live-check` | Runs the live checks. Only when someone asks for it | Quota |
| `dev build-check` | Sends the one real message of a build (BLD-0): a run without tools on the Driver's test Subscription, with the message "Answer with the single word: ready". It passes when the run completes and the answer holds that word | A little quota |

The test Subscription of a family is the Subscription named `test-<family>`, such as `test-anthropic` or `test-chatgpt`. The owner creates it and signs it in once. `dev build-check` uses the test Subscription of the Driver's default family. It does not start, and fails, when that Subscription is missing or not signed in, or when its last usage report shows a window used up.

### Probes

A probe starts the installed tool, sends no prompt, and records shapes, never values: key names, record types, enumerated values, error texts. It runs in homes created for it, never in the owner's own `~/.claude` or `~/.codex`, and with a clean environment. Where a probe needs a signed-in account, it uses a Subscription home that exists for testing, signed in once by the owner. The record of a probe names the tool version and the date and is kept in the Driver's `research/` folder.

Observed on 5 October 2026, the reasons for these rules: probes run with the environment of a Claude desktop session gave false results, and one `claude` subcommand run that way replaced the owner's stored login for the default folder. Probes that reused existing homes recreated a retired profile folder and left session files and model-written memory files in it.

### Live checks

A live check sends real prompts, as small as possible. Before it starts it reads the account's usage, and it does not start when a window is used up: on 5 October 2026 the Codex account's weekly window was at 100 percent, and the probes' turns were charged to the account's credits. A live check reports the turns it spent and the change in the account's usage.

One live check is part of every build: one real message, as small as possible, through the installed tool on the Driver's test Subscription (BLD-0). It follows the same rules, so a build made while the account's window is used up does not become a working Build.

## Requirements

| ID | A Driver must… | Origin | Verified by |
|---|---|---|---|
| DRV-5.1 | ship a stand-in for its vendor tool and pass the scenarios above with it, without network, account or quota | New | Claude: `C1`, `C2`, `C3`, `C4`, `C5`, `C6`, `C7`, `C8`, `C9`, `C10`, `C11`, `C12`, `C13`, `C14`, `C15`, `C16`, `C17`, `C18`, `C19`, `C20`, `C25`, `C26`, `C27`, `C28`, `C29`, `C30`, `C31`, `C32`, `C33`, `C35`, `C36`, `C37`, `C38`, `C39`, `C40`, `C41`, `C42`, `C43` (all 38 scenarios); Codex: `C1`, `C2`, `C6`, `C39`, `C41`, plus subscription scopes of `C4`, `C5`, `C7`, `C8`, `C40`; `C10`, `C11`, `C12`, `C13`, `C18`, `C19`, `C20`, `C42`, `C43`, no-control/stdin scope of `C33` and fresh-run scope of `C40`; continuity, stopping, advanced tools and error scopes pending |
| DRV-5.2 | derive every stand-in script from a probe record and name the tool version it shows | New | Claude: `base.stand-in`, `probe.subscriptions`, `live.subscriptions`, `test/run-protocol-2026-10-06.json` (Claude 2.1.289 raw run envelopes, explicitly synthetic test variants), `probe.run-settings`, `probe.continuity` (Claude 2.1.289 refusal envelope and native session acceptance); `probe.errors` and `test/errors-protocol-2026-10-07.json` (recorded Claude 2.1.289 error, retry and limit envelopes; explicitly synthetic variants); Codex: `base.stand-in`, `base.stand-in-handshake`, `probe.base-info` (codex-cli 0.159.2 version and recorded initialize response, explicitly synthetic old-version and home/platform variants; run scripts derived from `research/probe-scripts-2026-10-06/live/codex-all.json`, with marked synthetic text/count/failure/truncation variants; `probe.run-protocol` checks installed stable fields) |
| DRV-5.3 | provide its probes as a command that sends no prompt, uses only homes created for it and a clean environment, and writes a record of shapes without values | New | Claude: `dev.probe`, `dev.records`, `C32`, real `dev probe` on Claude 2.1.289 (research/dev-probe-2026-10-07.json, zero inference requests); Codex pending |
| DRV-5.4 | provide its live checks as a separate command that runs only when asked for, refuses to start when the account's usage is exhausted, and reports what it spent | New | Claude: `dev.gates`, `dev.live-check`, `dev.failed-cost`, `C32` (opt-in orchestration, usage preflight and spending reports); historical `live.run`, `live.tools`, `live.continuity`, `live.stopping`, `live.errors-usage` retain the real behavior checks. A new six-turn vendor run was not requested; Codex pending |
| DRV-5.5 | have a scenario for every requirement of DRV-0 to DRV-4 and of DRV-6 whose check names `contract` | New | `runner.shared-scenarios`, `runner.selection` (C31 and C32 info registered); remaining coverage pending |
| DRV-5.6 | provide the one real message of a build (BLD-0) as a check of its own: one prompt, as small as possible, through the installed tool on its test Subscription, under the rules of DRV-5.4 | New | Claude: `dev.build-check`, `C32`, real `dev build-check` on test-anthropic (research/dev-build-check-2026-10-07.json, one Haiku message); `build.clean-working`, `build.checks` (numbered Build 1, research/first-working-build-2026-10-07.json, one real Haiku message); Codex pending |
| DRV-5.7 | divide every fixed wait of this contract by the number in `ARBOL_TEST_TIME_SCALE`, when its environment holds one | New | Claude: `state.time-scale`, `state.lock` (base waits); other waits and contract pending; Codex: `state.time-scale`, `state.lock` (base waits; later lifecycle waits pending) |
| DRV-5.8 | carry the commands `dev stand-in`, `dev probe`, `dev live-check` and `dev build-check` in every Build, as stated above | New | Claude: `dev.gates`, `dev.probe`, `dev.build-check`, `dev.live-check`, `C32`, `build.checks` (all 38 scenarios and 81 unit tests from numbered Build 1); Codex pending |
| DRV-5.9 | hold, in its stand-in, a script for every scenario, play the one named in the file `scenario` of its folder, and append what it saw to `received.jsonl` there | New | Claude: `C2`, `C4`, `C5`, `C6`, `C7`, `C8`, `C9`, `C10`, `C11`, `C12`, `C13`, `C14`, `C15`, `C16`, `C17`, `C18`, `C19`, `C20`, `C25`, `C26`, `C27`, `C28`, `C29`, `C30`, `C31`, `C32`, `C33`, `C35`, `C36`, `C37`, `C38`, `C39`, `C40`, `C41`, `C42`, `C43`; all scenario scripts present; Codex: `base.stand-in`, `base.stand-in-handshake`, `C31`, `C32` , `C1`, `C2`, `C6`, `C39`, `C41`, subscription scopes of `C4`, `C5`, `C7`, `C8`, `C40` (base, subscription and fresh-run scripts); `C10`, `C11`, `C12`, `C13`, `C18`, `C19`, `C20`, `C42`, `C43`, fresh-run scopes of `C33` and `C40`; later scenario scripts pending |
| DRV-5.10 | use the Subscription `test-<family>` of its default family for `dev build-check`, and fail without starting when it is missing, not signed in or shows a window used up | New | Claude: `dev.gates`, `C32`, `dev.build-check`, real `dev build-check` on test-anthropic; Codex pending |

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| DRV-D18 | Which accounts do probes and live checks use? | A test Subscription per family, in a home of its own under the Driver's state directory, signed in once by the owner. Never the owner's default folders | Decided 6 October 2026 by the owner: the proposed default (SYL-49) |
| DRV-D19 | Are the stand-ins shared between the Drivers? | No. Each speaks one tool's protocol; they share only the scenario descriptions | Decided 6 October 2026 by the owner: the proposed default (SYL-50) |
| DRV-D35 | How does the first stand-in read a scenario with several parts? | The `scenario` file is a scenario identifier and an optional part separated by whitespace, such as `C31 old`. C31 has `supported`, `old` and `missing` parts; the default is `supported`. C32 uses the part `info`, playing the supported version record. For C31 `missing`, the suite names a nonexistent executable in `toolPath`; no stand-in starts. The stand-in records arguments, environment variable names and working directory, never environment values. Later tasks add their own protocol scripts | Decided 6 October 2026 during SYL-75, a technical choice |
| DRV-D32 | How does one suite drive two Drivers whose stand-ins speak different protocols? | Through a home of the test's own, `toolPath`, a scenario identifier the stand-in reads from a file, and a record the stand-in writes. The suite knows scenarios and events; each stand-in knows its tool. Time is shortened by one environment variable | Decided 6 October 2026, a technical choice made in drafting on the owner's go-ahead |
| DRV-D36 | How are shared scenarios written and how is a Driver command selected? | A TypeScript registry in `arbol/conformance` gives each scenario its identifier, scope, covered requirements and function. Functions use only the command line, contract JSON and stand-in records; they import no Driver code. The suite writes both contract settings filenames before any Driver starts, so it discovers the Driver through isolated `info`, without probing a real tool. `--driver` is a program and optional fixed arguments, split as quoted command words without shell expansion; relative program and argument paths are relative to the caller. `--only` accepts comma-separated or quoted whitespace-separated identifiers; an unknown or unimplemented identifier is an input error, never a pass. Every scenario gets a new home, `ARBOL_TEST_TIME_SCALE=100` by default (authentication scenarios use 10 for subprocess startup and replacement, then 100 for expiry), a minimal environment, and bounded subprocesses whose process groups are ended before the home is removed. Exit status is 0 for all selected checks passing, 1 for any failure and 2 for invalid suite input | Decided 6 October 2026 during SYL-77, a technical choice |
