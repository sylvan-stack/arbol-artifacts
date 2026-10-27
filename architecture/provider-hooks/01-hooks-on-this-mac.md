---
role: authored
spec: PHK-1
status: draft
---
# Provider hooks · 01 The hooks on this Mac, and the rules for installing one

Which hooks of Claude Code and Codex are on this Mac or planned, who owns each, and the rules every hook that Arbol or its checks install must follow so that several of them can share the Leather Bag's settings files. It matters because three installers will write into the same two files, one of whose hooks blocks tool calls while the others only watch, and the tools give a hook enough power to stop every session on the Mac or to slip text into what the model reads.

It follows the conventions of this chapter's [README](README.md#conventions). What the tools do with a hook is in [PHK-0](00-hooks-of-claude-code-and-codex.md).

## Scope

Covered: the hooks on this Mac and those planned, watching and steering hooks, sessions that run no hooks of the Leather Bag's, the rules for installing, removing and checking a hook, how hooks of different owners live side by side.

Not covered: what each tool does with a hook ([PHK-0](00-hooks-of-claude-code-and-codex.md)); what the agent records' hook writes ([AGR-1](../../agent-records/01-the-hooks.md)); when the check from outside steers or stops (the Beat SYL-221 and the guide [The check from outside](../../../mycel/operations/agent-watch.md)); git's hooks, such as `commit-guard`.

## Behaviour

### The hooks on this Mac

As qualified on 27 October 2026 after SYL-221 installation:

| Hook | Owner | Tool and events | Kind | State |
|---|---|---|---|---|
| `~/.local/bin/arbol-agents hook claude-code` and `… hook codex` | Arbol, the [agent records](../../agent-records/README.md) ([AGR-1](../../agent-records/01-the-hooks.md)) | Claude Code: 17 events. Codex: all 12. Time limit 5 seconds, 3 for Codex's `SessionEnd` | Watching: keeps one record per session | Accepted; implementation and installation remain SYL-201 and SYL-202 |
| `~/.local/bin/agent-watch-hook` | The check from outside of the guide [Working in Sagas](../../../mycel/operations/sagas.md) | Claude Code and Codex: `PreToolUse` | Steering: blocks a tool call once (a steer) or until released (a stop) | Installed, activated and trusted by SYL-221; live private checks pass in Claude Code 2.1.304 and Codex CLI 0.162.1 |
| Codex's `notify` | Computer Use | Codex, once per finished turn | Not a hook ([PHK-0](00-hooks-of-claude-code-and-codex.md#codexs-notify)) | Installed |

Other programs may add hooks of their own to the same files. Arbol neither uses nor changes them, and depends on none. `~/.codex/hooks.json` now holds the check’s PreToolUse group, with trust obtained from Codex itself. New Claude sessions load their group; the Codex desktop app must be reopened to load newly installed hooks. SYL-221 installs no repository-local hook settings.

### Watching and steering hooks

A *watching* hook learns what a session does and never changes it: it exits with 0, prints nothing and blocks nothing. A *steering* hook may block a tool call with exit status 2 and a message for the agent. Every hook of Arbol's is a watching hook, except the check from outside's, the only steering hook. Keeping them apart means that a fault in the agent records can never stop a session, and that the one hook that can is small and can be reviewed alone.

### A Driver's run

A Driver starts `claude` and `codex` in their default homes, `~/.claude` and `~/.codex` ([DRV-D42](../../driver-contract/00-overview-and-boundary.md#the-vendor-tools-home), decided 19 October 2026). A run of an Arbol chat therefore runs every hook on this Mac, as any session does. Each hook of Arbol's says what it does in such a run, which it can tell by `ARBOL_ROOT` in its environment once the Driver's caller sets it (SYL-207): the agent records write no record for it, because its Exchange keeps its own ([AGR-D17](../../agent-records/01-the-hooks.md#decisions)), and the check from outside never steers a chat.

### Sessions that run no hooks of the Leather Bag's

| Session | Why no hooks | Where it is said |
|---|---|---|
| A probe or live check of a Driver | It runs in a home created for it ([DRV-D44](../../driver-contract/05-conformance.md#decisions)) | [DRV-5](../../driver-contract/05-conformance.md) |
| The check from outside's Claude Code reviewer | `claude -p --safe-mode` | [The check from outside](../../../mycel/operations/agent-watch.md) |
| The check from outside's Codex reviewer | `codex exec --ephemeral … --disable hooks`, to keep it outside its own steering hook ([PHK-D2](#decisions)); implementation/qualification in SYL-221 | — |

### The rules for installing a hook

Every installer of a hook of Arbol's (today `arbol-agents install` and the check from outside's) follows the same rules, so that each keeps the others' entries:

| Rule | Detail |
|---|---|
| Only the Leather Bag's own files | `~/.claude/settings.json`, `~/.codex/hooks.json`, and `hooks.state` in `~/.codex/config.toml`. Never a repository's settings, never a Subscription home, never `--settings` files such as `settings-zai.json`, never Codex's `notify` |
| One entry per event, its own group | Each hook is added as a group of its own in the event's list. Entries already there, whoever wrote them, stay as they are and in their order |
| Known by its command | An installer recognises its own entries only by their command. Running it again adds nothing that is there already |
| The command never changes | A fixed path under `~/.local/bin`, one program with its arguments, no shell syntax. Codex trusts only the exact definition ([PHK-0](00-hooks-of-claude-code-and-codex.md#codexs-trust)), so a new Build changes what the path points at, never the path |
| Whole files | Each file is written whole, through a temporary file and a rename. A file that cannot be read is left alone and the installer fails naming it |
| A copy first | Before an installer first changes a file, it keeps a copy beside it as `<name>.before-<installer>`, such as `settings.json.before-arbol-agents`, and never overwrites it |
| Codex's trust through Codex | Trust is recorded through `codex app-server`'s `hooks/list` and `config/batchWrite`, never by computing a hash or editing `config.toml` by hand |
| Said when it takes effect | The installer ends by saying that running Claude Code sessions keep their old hooks and that the Codex app is to be reopened |
| Removing | `uninstall` removes exactly the entries with its own command and their trust entries |
| Status | `status` says for each tool whether every entry is in place, whether Codex trusts each one, and the tool's version |

<!-- sources:
sagas:@code/tools/agent-watch/hook_install.py#install
sagas:@code/tools/agent-watch/hook_install.py#uninstall
sagas:@code/tools/agent-watch/hook_install.py#status
sagas:@code/tools/agent-watch/hook_codex.py#Codex
sagas:@code/tools/agent-watch/test_hook_install.py#Installation
sagas:@code/tools/agent-watch/test_hook_codex.py#Protocol
-->

### The rules for running a hook

| Rule | Watching hook | Steering hook |
|---|---|---|
| Exit status | Always 0 | 2 only to block a `PreToolUse` it means to block; otherwise 0 |
| Output | Nothing, on standard output or standard error | Only the message to the agent, on standard error, with a blocked call |
| Foreground | Yes, never a background hook | Yes |
| Time limit in the tool's settings | 5 seconds; 3 for Codex's `SessionEnd` | The same |
| Own speed | At most 50 milliseconds in the median on this Mac when it has work to do | At most 50 milliseconds in the median when there is nothing to steer, which is almost always the case |
| On any fault of its own | Exits with 0 | Exits with 0 silently ([PHK-D4](#decisions)) |
| The conversation | Keeps no part of it | Keeps no part of it |
| Elsewhere | Starts no process that outlives it, uses no network, writes only its own files | The same |

Several hooks on one event add their times. With both of Arbol's installed, each tool's `PreToolUse` starts `arbol-agents hook` and `agent-watch-hook`, besides any hook of another program.

<!-- sources:
sagas:@code/tools/agent-watch/agent_hook.py#main
sagas:@code/tools/agent-watch/agent_hook.py#launcher
sagas:@code/tools/agent-watch/agent_control.py#fresh_owner
sagas:@code/tools/agent-watch/test_agent_hook.py#Hook
sagas:@code/tools/agent-watch/agent_actions.py#observe
sagas:@code/tools/agent-watch/test_agent_actions.py#Actions
sagas:@code/tools/agent-watch/hook_live.py#live
sagas:@code/tools/agent-watch/hook_live_controller.py#main
-->

### Hooks of different owners side by side

A steering hook's block is seen by the watching hooks only as a `PreToolUse` whose call never comes back ([PHK-D1](00-hooks-of-claude-code-and-codex.md#decisions)). The agent records then keep that call open until the end of the turn, which the next `Stop` corrects. Neither hook reads the other's files.

## Requirements

| ID | Every hook of Arbol's and its installer must… | Origin | Verified by |
|---|---|---|---|
| PHK-1.1 | be installed only into `~/.claude/settings.json`, `~/.codex/hooks.json` and `hooks.state` of `~/.codex/config.toml`, as a group of its own per event, leaving every other entry and setting as it is | New | agent-watch part: private `Installation`, actual private lifecycle and normal installed proof in SYL-221 preserve unrelated JSON/TOML and the independent watcher LaunchAgent. Agent-record hook remains SYL-202 |
| PHK-1.2 | run a command at a fixed path under `~/.local/bin`, without shell syntax, that never changes across Builds | New | agent-watch part: `Hook.test_wrapper_has_an_empty_fast_path_arbol_chat_bypass_and_silent_missing_runtime`, `Installation`; fixed foreground launcher source is agent_hook.launcher. Agent-record hook remains SYL-202 |
| PHK-1.3 | write each file whole, keep a copy before its own first change and never overwrite it, refuse a file it cannot read, and add nothing twice | New | agent-watch part: `Installation` covers first backups/absence, idempotence, malformed/duplicate JSON, symlinks, disabled providers, changed launchers and preserved foreign trust indices; actual private lifecycle (SYL-221) |
| PHK-1.4 | record Codex's trust only through `codex app-server`'s `hooks/list` and `config/batchWrite` | New | agent-watch part: `Protocol`, actual private install/reinstall/uninstall and normal installed trust/status prove the exact provider-supplied hook key/hash; no provider hash is computed (SYL-221) |
| PHK-1.5 | on `uninstall`, remove exactly its own entries and their trust entries; on `status`, say for each tool whether each entry is in place and trusted, and the tool's version | New | agent-watch part: `Installation`/`Protocol`, actual private exact uninstall and normal installed status with tool versions, trust and enabled state (SYL-221). Agent-record hook remains SYL-202 |
| PHK-1.6 | as a watching hook, always exit with 0, print nothing and never run in the background | New | unit |
| PHK-1.7 | as a steering hook, block only a `PreToolUse` and print only the message to the agent | New | agent-watch part: `Hook`, `Policy`, `Actions`; actual private Claude Code 2.1.304 and Codex CLI 0.162.1 live checks (SYL-221) prove one-use steer, persistent stop, successful retry, allowed wrap-up/release and no forbidden file. Agent-record watching hooks remain SYL-202 |
| PHK-1.8 | take at most 50 milliseconds in the median on this Mac, keep no part of the conversation, start no lasting process and use no network | New | agent-watch part: `Hook.test_twenty_no_action_calls_stay_below_the_fifty_millisecond_median`, silent missing-script/runtime regression, fail-open/action-owner tests; explicit twenty-run speed check passes. The policy hook uses no network or lasting process; provider live qualification is separate |
| PHK-1.9 | not be run by a reviewer of the check from outside, and say what it does in a Driver's run, which runs every hook of the owner's (DRV-D42) | New | agent-watch reviewer exclusion: ReviewerTests.test_codex_reviews_a_claude_code_agent_and_claude_code_a_codex_agent requires --disable hooks for Codex, and Claude keeps --safe-mode. Normal Driver-run hooks follow DRV-D42; the agent-record hook remains SYL-202 |

## Known problems in version 1

Version 1 used no hooks of either tool.

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| PHK-D2 | The check from outside's Codex reviewer runs `codex exec` in `~/.codex`. Once hooks are installed there, each review would create an agent record of its own and could be blocked by the check's own steering hook. Is it run without hooks? | Yes: its command line gets `--disable hooks`, beside `--disable apps` and the others it has. Its Claude Code counterpart already runs with `--safe-mode`. A test of the check asserts both | Decided 26 October 2026 for SYL-221: disable hooks explicitly in Codex reviewers before installing the steering hook; the independent reviewer must not observe or block itself |
| PHK-D3 | Do the agent records and the check from outside share one installer? | No. Each installer writes only its own entries under the rules above, as the Beats SYL-202 and SYL-221 already plan. One installer would tie the agent records' Builds to the check's | Decided 26 October 2026 for SYL-221: separate installers with exact command ownership, as both accepted Beats already require |
| PHK-D4 | What does the steering hook do when it fails on its own, for example when its steering file cannot be read? | It lets the call through and exits with 0. A broken hook that blocked would stop every session on the Mac, the session that could repair it included; a missed steer is caught by the next check five minutes later | Decided 26 October 2026 for SYL-221: fail open silently on every hook fault; only an intended block exits 2 |
| PHK-D5 | Does a Driver's run get the owner's hooks, as it gets the owner's skills and MCP servers (DRV-D27)? | Yes. The Driver copies the `hooks` of `~/.claude/settings.json` into the Subscription home's `settings.json`, and `~/.codex/hooks.json` into its home with Codex's trust recorded there, before each run. A hook installed once then reaches every session on the Mac, Arbol's chats included, and Arbol builds on the tools' hooks instead of leaving them out. Each hook of Arbol's must then tell a Driver's run apart where it matters: the agent records already keep an Exchange's own record (AGR-D7), and the check from outside never steers a chat | Settled 19 October 2026 by the owner's wider decision DRV-D42: a Driver runs the tools in their default homes, so a run has the owner's hooks without any copy |
| PHK-D6 | How does the steering hook preserve a repair path and avoid treating old dry-run verdicts as live orders? | Fixed provider-qualified command, explicitly disabled until qualified installation; exact-run action files, actual delivery records, fresh owner-message cursors, lift watermarks and a conservative wrap-up allowlist. The owning guide states the protocol and provider coverage limits | Decided 26 October 2026 before implementation in SYL-221; no historical review is replayed and no process is killed |
