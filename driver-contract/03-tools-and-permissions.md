---
role: authored
spec: DRV-3
status: accepted
---
# Driver Contract · 03 Tools and permissions

The agent's tools belong to the vendor tool: it reads and changes files, runs commands, uses the web and starts sub-agents by itself. A Driver decides nothing about them and holds nothing back. It runs the agent as *trusted* and with the vendor tool's full power: every tool is available, nothing of the vendor tool is switched off but its own memory, the owner's own skills and MCP servers are there, and no call waits for anyone's permission. The owner decided this on 6 October 2026; restrictions may follow later and are no part of the first release. This specification states what a run with tools is given, what a run without tools is, how a command in a terminal is shown, what a caller sees of sub-agents, and how a question from the agent reaches the person. It matters because nothing stands between the agent and the Leather Bag's machine any more: what an agent does is settled by the folder it is started in and the instructions it is given, not by a question at the moment it acts.

## Scope

Covered: the two kinds of run, the vendor tool's full power, running the agent as trusted, calls the vendor tool refuses by itself, the common form of a command in a terminal, sub-agents, questions from the agent to the person.

Not covered: the tool events of a run and the size limit of results (DRV-2); how each vendor tool is started (CLD-3, CDX-3); levels of asking and permission questions, which the first release does not have (Decisions).

## Behaviour

### Two kinds of run

A request says one of two things about tools.

| `tools` | The agent has |
|---|---|
| `all` | Every tool the vendor tool offers with the owner's own setup. The Driver names no tool to the vendor tool, neither to allow it nor to forbid it |
| `none` | No tools: one prompt in, one text out (DRV-2, A run without tools) |

Nothing in between exists. A request cannot take a single tool away or add one.

### The vendor tool's full power

A Driver switches one part of its vendor tool off: the tool's own memory, the notes a tool writes for itself and reads again in later conversations. Everything else is as the tool ships it. In a run with tools the agent has the tool's tools for files, the terminal and the web, its sub-agents, the services connected to the signed-in account, and whatever the working folder sets up for the tool, such as its instruction file. What all of that is, is the vendor tool's own matter and changes with its version, the account and the model.

The agent also has everything the owner set up for that vendor tool, because the tool runs in its default home, `~/.claude` or `~/.codex` (DRV-0.4, [DRV-D42](00-overview-and-boundary.md#decisions)): its settings, hooks, plug-ins, skills, MCP servers with their sign-ins, and the owner's own instruction files. The Driver changes nothing there.

Two things differ from the same tool started by hand, and neither is a part switched off:

- The tool's own memory is off for the run, through an option of that run, not through the owner's settings.
- The request's system prompt is added to the tool's own (DRV-2).

A setting that concerns the tool's housekeeping and not the agent, such as its check for updates, is the Driver's to make. Its specification lists each one.

Observed in version 1: the Claude route disallowed five tools by name, among them web access and sub-agents, switched the tool's own memory off and read no settings of the working folder. The Codex route switched 27 optional features off and left shell and file tools on.

Observed with the installed tools on 6 October 2026: `claude` read the instruction file `CLAUDE.md` of the working folder, and `AGENTS.md` where that was the only one. `codex` read `AGENTS.md` and did not read `CLAUDE.md`. Both tools listed the owner's skills in a new home, and both started an MCP server that was handed to them at the start of a run.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:drivers/claude/arbol_driver_claude/turn.py#TurnRunner._build_argv_native`
- `arbol_deprecated_v1:drivers/codex/arbol_driver_codex/session.py#control_argv`
- `arbol_deprecated_v1:product-spec/06-tools-and-permissions.md#Two ways a tool runs`

### Nothing asks for permission

A Driver starts the vendor tool in the mode in which it carries out every call without a question, with the access to files, programs and the network that the Leather Bag's own account has. A request has no level to choose. Arbol 2 has no Full Permissions setting: every run is what that setting used to switch on.

A run therefore never waits for a permission. Should the vendor tool send a request for one all the same, the Driver answers it at once, so that it is never left open, and emits a `notice`. It approves the request where the tool's protocol has an answer that approves, and declines it otherwise, with a message that tells the agent so.

The vendor tool can still refuse a call by itself, for instance a command its terminal tool will not run. Such a call ends with `tool_finished` as a failure carrying the tool's reason, and the run goes on.

Observed in version 1: on the Claude route the tool asked and Root answered, by rule or by the Leather Bag; a route setting called Full Permissions made Root approve automatically, question by question. The Codex route never asked: the tool ran with full access, its approval requests were declined, and Full Permissions had no effect.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/06-tools-and-permissions.md#Full Permissions`
- `arbol_deprecated_v1:product-spec/06-tools-and-permissions.md#Defaults and remaining decisions`
- `arbol_deprecated_v1:drivers/codex/arbol_driver_codex/session.py#tool_policy`

### Commands in a terminal

Both vendor tools let the agent run commands in a terminal, each under its own name and in its own shape. A Driver hides that difference. Wherever this contract shows a tool call (in the events of a run and in the history a request carries), a command in a terminal is the tool `shell`, with the same fields from every Driver:

| Field | Meaning |
|---|---|
| Input `command` | The command as a person would type it, without the launcher a tool may wrap around it |
| Input `cwd` | The folder it runs in, where the tool states one |
| Result `output` | What the command printed |
| Result `exitCode` | Present where the tool reports one |

When a Driver builds a conversation from a history (DRV-2), it writes each `shell` call back in its own tool's form. An agent therefore never meets the other tool's name for a command.

Every other tool keeps the name and the shape its vendor tool gives it.

An agent can leave a command running in the background and end what it has to say for now. The run then lasts until that command has ended, as it does for a sub-agent, and whatever the vendor tool reports until then is part of the run: the command's result, and the agent's further words where the tool tells the agent that the command has finished. A command that never ends by itself, such as a development server, therefore keeps its run going until the run is stopped, and the stop ends the command (DRV-D34).

Observed with the installed tools on 6 October 2026, one real run each, with a command of 12 and of 40 seconds left in the background: `claude`, with its input kept open, told the agent when the command had finished, and the agent said so in a second part; with its input closed after the first part it ended the command. `codex` completed the turn while the command still ran, sent the command's result when it had finished, and did not tell the agent.

Observed with the installed tools: `claude` calls the tool `Bash` and gives it a command and a short description; the result is text with an error flag and no exit code. `codex` reports a command execution with the command inside a shell launcher (`/bin/zsh -lc 'echo hi'`), the plain command beside it, the folder, the collected output and an exit code.

### Sub-agents

Both vendor tools let an agent hand a part of its task to a sub-agent that it starts itself. A Driver does not switch this off and adds nothing to it: the sub-agents run inside the vendor tool, with the same access as the agent.

Starting a sub-agent is a tool call like any other. What the sub-agent then does is reported in the same run, and each such event names the call that started the sub-agent, so that a caller can show it under that call or leave it out. The answer of a run is the agent's own text: a sub-agent's text is never mixed into it.

A sub-agent can go on working after the agent has said something for the time being, and the agent then goes on when the sub-agent reports back. A run lasts until the agent and every sub-agent it started have ended. Something the agent says while a sub-agent still works is not the end of the run. A stop ends the sub-agents with the agent (DRV-2).

Observed with the installed tools on 6 October 2026, one real run each: both agents started a sub-agent when asked to, the sub-agent ran a command, and the agent reported its result. On `claude` the sub-agent worked in the background: the tool reported the agent's part as ended, then the sub-agent's work, then a second part of the agent with the result. On `codex` the agent waited inside one turn, and the sub-agent's work arrived under a thread of its own. A sub-agent on `claude` had no tool for asking the person, so a question came from the agent itself or not at all.

Observed in version 1: sub-agents were switched off on both routes.

### Questions from the agent to the person

An agent can ask the Leather Bag something while it works: one or more questions, each with a few options to choose from. This is the one occasion on which a run waits for its caller.

The Driver emits `ask_opened`. The question names the tool call it belongs to, which the Driver has already announced with `tool_started`, and carries the questions with their options. The caller answers with an `answer` line on the run's control input (DRV-2): the chosen options per question, or a decline. A decline ends the run as `cancelled`. `ask_closed` follows either way.

A question stays open until it is answered, the vendor tool withdraws it, or the run ends. The Driver sets no time limit on it. Several questions can be open at once and are answered in any order. A second answer to the same question changes nothing. The Driver checks an answer before passing it on, so a malformed answer is refused to the caller and never reaches the tool.

A run started without a control input has nobody to answer. Where the vendor tool allows it, the Driver then gives the agent no means to ask. A question that arises nonetheless is declined by the Driver with a message saying that nobody is there to answer, and the run goes on.

A Driver whose vendor tool cannot carry such questions never emits them, and says so in its specification.

Observed in version 1: questions from the agent arrived through the same bridge as permission questions on the Claude route, were answered in the chat window only, and cancelling one stopped the response. The Codex route had none.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/06-tools-and-permissions.md#Questions from the agent`

## SYL-92 verification, 7 October 2026

SYL-92 passed the complete 38-scenario shared registry for both Python Drivers. Codex also passed 128 unit methods, Ruff and strict mypy from source; its standalone CPython 3.14.8 development candidate passed the same units and all 38 scenarios, and its relocated copy passed metadata and unit checks under a minimal environment. A fresh packaged `dev probe` passed against codex-cli 0.159.2 with zero inference requests. The packaged build gate sent exactly one no-tools ready message through `test-chatgpt`; it completed and reported tokens and usage before/after. The extended five-turn `dev live-check` orchestration and refusal gates passed offline, but the extended vendor run was not requested. Contract and state format remain 1. The first numbered Codex Build is the separate SYL-94 task.

Current records and source/package provenance: `~/Artifacts/arbol-codex-driver/research/conformance-2026-10-07/verification.json`, `coverage-audit.json`, `packaged-probe.json` and `packaged-build-check.txt` in that folder. Dated migration and TypeScript evidence below remains historical; unobserved real vendor failures remain unobserved. The coverage audit retains every former Verified by cell before this update.

## Requirements

| ID | A Driver must… | Origin | Verified by |
|---|---|---|---|
| DRV-3.19 | show every command the agent runs in a terminal as the tool `shell`, with the input and result above, in events, and write a `shell` call of a history back in its own tool's form or, where that form is not known, in a form its tool was seen to accept | New | Claude Python: `C11`, `C35`, `test_runtime.ProtocolTests`; Codex Python: `C11`, `C35`, `Foundation.test_history_native_pairing_shell_fields_and_private_ordered_images`, `Mapper.test_shell_unwrap_preserves_quoting`, `MapperTools.test_generic_tool_failures_preserve_reasons_and_success_false_is_failed` |
| DRV-3.20 | give a run with tools every tool the vendor tool offers with the owner's own setup, and name no tool to it, neither to allow nor to forbid | Changed | contract |
| DRV-3.21 | start the vendor tool so that it carries out every tool call without asking, with the access of the owner's account | Changed | Claude Python: `C35`, `test_runtime.ProtocolTests`; Codex Python: `C35`, `Continuity.test_resume_overrides_and_delayed_restored_usage_do_not_count_previous_thread` |
| DRV-3.22 | ask its caller for no permission; answer at once a request for permission that the vendor tool sends nonetheless, approving it where the tool's protocol has an answer that approves and declining it otherwise, and emit a `notice` | Changed | Claude Python: `C25`, `test_runtime.ProtocolTests`; Codex Python: `C25`, `MapperTools.test_child_request_notice_without_turn_replays_after_spawn_discovery` |
| DRV-3.23 | end a call the vendor tool refused by itself with `tool_finished` as a failure carrying the tool's reason, and let the run go on | Kept | Claude Python: `C35`, `test_runtime.ProtocolTests`; Codex Python: `C35`, `MapperTools.test_generic_tool_failures_preserve_reasons_and_success_false_is_failed` |
| DRV-3.24 | name, on every event that reports what a sub-agent did, the call that started the sub-agent, and keep a sub-agent's text out of the run's answer | New | Claude Python: `C35`, `test_runtime.ProtocolTests`; Codex Python: `C35`, `Lifecycle.test_active_nested_and_late_discovered_children_are_interrupted_and_attributed`, `MapperTools.test_child_post_turn_output_notices_and_retry_keep_parent_attribution`, `MapperTools.test_child_request_notice_without_turn_replays_after_spawn_discovery` |
| DRV-3.32 | keep a run going, with its events, until the agent, every sub-agent it started and every command it left running in the background have ended, and treat nothing the agent says while one of them still works as the end of the run | New | Claude Python: `C29`, `C35`, `test_runtime.ProtocolTests`; Codex Python: `C29`, `C35`, `Lifecycle.test_active_nested_and_late_discovered_children_are_interrupted_and_attributed`, `ToolRuns.test_late_noncommand_child_tool_closes_after_completed_turns_and_background_work` |
| DRV-3.25 | switch off no part of its vendor tool except the tool's own memory: its tools, its sub-agents, the services connected to the account and what the working folder sets up for the tool stay as the tool ships them | Changed | Claude Python: `C35`, `test_runtime.ProtocolTests`; Codex Python: `C35`, `AppServerTests.test_private_home_configuration_clean_environment_and_owner_cleanup`, `AppServerTests.test_startup_wrong_home_config_and_cancellation_gives_eof_before_force` |
| DRV-3.26 | carry a question from the agent to the person to its caller as `ask_opened`, after the `tool_started` of the call it belongs to and naming that call | Kept | Claude Python: `C36`, `test_runtime.ProtocolTests`; Codex not applicable (CDX-3.13): `C25`, `C33`, `C36` (unsupported vendor question rejected, no ask events, unmatched control answer refused) |
| DRV-3.27 | keep a question open, without a time limit of its own, until it is answered, withdrawn or the run ends, and allow several open questions and answers in any order | Kept | Claude Python: `C29`, `C36`, `test_runtime.ProtocolTests`; Codex not applicable (CDX-3.13): `C25`, `C33`, `C36` (unsupported vendor question rejected, no ask events, unmatched control answer refused) |
| DRV-3.28 | check an answer before it reaches the vendor tool and deliver it exactly once; treat a second answer as success without effect; refuse a malformed answer with `invalid_input` and an answer to a question that was withdrawn or never opened with `not_found`, each in a `control_refused` event | Kept | Claude Python: `C36`, `test_runtime.ProtocolTests`; Codex not applicable (CDX-3.13): `C25`, `C33`, `C36` (unsupported vendor question rejected, no ask events, unmatched control answer refused) |
| DRV-3.29 | end the run as `cancelled` when the caller declines a question | Kept | Claude Python: `C36`, `test_runtime.ProtocolTests`; Codex not applicable (CDX-3.13): `C25`, `C33`, `C36` (unsupported vendor question rejected, no ask events, unmatched control answer refused) |
| DRV-3.30 | in a run without a control input, give the agent no means to ask where the vendor tool allows that, and decline a question that arises nonetheless with a message saying that nobody is there to answer | New | Claude Python: `C33`, `test_runtime.ProtocolTests`; Codex not applicable (CDX-3.13): `C25`, `C33`, `C36` (unsupported vendor question rejected, no ask events, unmatched control answer refused) |
| DRV-3.31 | give a run with tools everything the owner set up for the vendor tool, settings, hooks, plug-ins, skills, MCP servers and instruction files, by starting the tool in its default home, and change nothing there | New | contract |

DRV-3.1 to DRV-3.18 described tool sets, levels of asking and permission questions. They were withdrawn on 6 October 2026 with DRV-D12, and their numbers are not used again.

## Interface

```ts
type Tools = "all" | "none";                                     // RunRequest.tools (DRV-2)

interface ShellInput  { command: string; cwd?: string }          // input of the tool "shell"
interface ShellResult { output: string; exitCode?: number }     // its result

interface Ask {                                                  // a question from the agent to the person
  callId: string;                                                // the tool call of an earlier tool_started
  questions: Array<{ id: string; header?: string; question: string; multiple: boolean;
                     options: Array<{ label: string; description?: string }> }>;
}

type Answer =
  | { type: "answers"; answers: Record<string, string[]> }      // question id to chosen labels
  | { type: "decline" };                                         // ends the run
```

| Line | Input | Result |
|---|---|---|
| An `answer` line on a run's control input | `{ type: "answer", askId, answer }` | Nothing when accepted, and the question's `ask_closed` follows. A `control_refused` event otherwise |

An event that reports what a sub-agent did carries `parentCallId`: the `callId` of the tool call that started the sub-agent (DRV-2).

Errors: `not_found` (a question that was withdrawn or never opened), `invalid_input` (an answer the question does not accept; a value of `tools` other than the two above).

## Known problems in version 1

Not to be reproduced.

- **A setting that did nothing.** On the Codex route Full Permissions suggested a gate where there was none. Arbol 2 has no such setting.
- **One unanswered question held back the answers to the others.**
- **One malformed question disabled every later turn.**
- **A question the tool raised and the Driver did not know was never answered**, and the turn waited forever.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/06-tools-and-permissions.md#Known problems and lessons`
- `arbol_deprecated_v1:drivers/claude/arbol_driver_claude/turn.py#TurnRunner._run_native`

## Python migration verification, 7 October 2026

SYL-95 verification is recorded in the requirement-level `~/Artifacts/arbol/driver-contract/python-migration-coverage-2026-10-07.json` and the Driver records `research/python-migration-2026-10-07/verification.json`. Python check names identify the copied standard-library unittest suites and the unchanged shared scenarios. Prior Driver unit/probe/live names refer to historical TypeScript evidence; unchanged shared build-tool and runner names remain active. Claude passes the complete 38-scenario suite; Codex passes its five original scoped groups (29 scenario invocations, with the same exclusions), and remains a development candidate. No historical live result is treated as fresh Python evidence, and previously unobserved vendor failures stay unobserved.

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| DRV-D12 | How is version 1's Full Permissions realised? | By the caller: the run stays at a level that asks and a rule of the caller answers. Every decision then leaves the same record whoever made it | Decided 6 October 2026 by the owner, against the proposed default: a Driver runs every agent as trusted, with unrestricted access and every tool of the vendor tool, and nothing asks for permission. Arbol 2 has no Full Permissions setting. Restrictions may be added later and are not a priority (SYL-43, SYL-44, SYL-59, SYL-60, SYL-67) |
| DRV-D13 | Which level does a Codex run get by default? | The caller's choice | Decided 6 October 2026 by the owner: there are no levels. Both Drivers run unrestricted (DRV-D12) |
| DRV-D14 | May an agent start sub-agents in the first release? | No. Their events have not been probed | Decided 6 October 2026 by the owner, against the proposed default: agents are not kept from starting sub-agents. The vendor tools do this by themselves, and a Driver only reports it (SYL-45) |
| DRV-D25 | Can the agent ask the person a question while it works? | Not in the first release | Decided 6 October 2026 by the owner, against the proposed default: yes. It is the ordinary behaviour of the agent's question tool. The Claude Driver carries such questions. `codex` offers them only in an experimental mode, so the Codex Driver carries none until that changes (SYL-70) |
| DRV-D26 | Does a Driver switch any part of its vendor tool off? | Yes, what brings something into a run that is neither in the request nor in the saved conversation: the tool's own memory, the services connected to the account, optional parts such as plug-ins | Decided 6 October 2026 by the owner, against the proposed default: no. `claude` and `codex` keep their full power, and nothing is switched off (SYL-71). One exception, named by the owner the same day: the tool's own memory is off |
| DRV-D27 | Which skills and MCP servers does a run have, beyond those of the working folder and of the account? | None: a Subscription's home starts empty | Widened on 19 October 2026 by DRV-D42: a run has the owner's whole setup of the tool, because the tool runs in its default home. Decided 6 October 2026 by the owner, against the proposed default: the owner's own, by the Driver in use. The Claude Driver gives a run the skills and MCP servers the owner set up for `claude`, the Codex Driver those set up for `codex`. A Driver reads them and never changes them |
| DRV-D34 | The agent leaves a command running in the background and ends what it has to say. Does the run wait for the command? | Yes, as for a sub-agent. The command finishes, its result is reported, and on `claude` the agent is told and goes on. The cost: a command that never ends, such as a development server, keeps the run going until it is stopped, and the stop ends the command. The other choice ends the command the moment the agent has spoken | Decided 6 October 2026 by Claude, on the owner's standing direction that the vendor tools keep their full power (DRV-D26), and confirmed by the owner the same day: a run may wait for a command however long it takes. What Arbol does about a run that waits for long is settled in Arbol, not in a Driver |
