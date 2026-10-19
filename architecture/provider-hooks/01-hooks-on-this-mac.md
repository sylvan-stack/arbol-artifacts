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

As read on 19 October 2026:

| Hook | Owner | Tool and events | Kind | State |
|---|---|---|---|---|
| `~/.config/iterm2/cc-status` | iTerm2's integration, not Arbol | Claude Code: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `Notification`, `Stop`, `StopFailure`, `SubagentStop`, `SessionEnd`. No time limit set | Watching: shows a session's state on its iTerm2 tab | Installed |
| `~/.local/bin/arbol-agents hook claude-code` and `… hook codex` | Arbol, the [agent records](../../agent-records/README.md) ([AGR-1](../../agent-records/01-the-hooks.md)) | Claude Code: 17 events. Codex: all 12. Time limit 5 seconds, 3 for Codex's `SessionEnd` | Watching: keeps one record per session | Accepted; built and installed by the Beats SYL-201 and SYL-202 |
| `~/.local/bin/agent-watch-hook` | The check from outside of the guide [Working in Sagas](../../../mycel/operations/sagas.md) | Claude Code and Codex: `PreToolUse` | Steering: blocks a tool call once (a steer) or until released (a stop) | Planned in the Beat SYL-221 |
| Codex's `notify` | Computer Use | Codex, once per finished turn | Not a hook ([PHK-0](00-hooks-of-claude-code-and-codex.md#codexs-notify)) | Installed |

`~/.codex/hooks.json` does not exist yet: no hook runs in Codex today. No repository under `~/repos/sylvan-stack` or `~/Artifacts` has a settings file of its own with hooks.

### Watching and steering hooks

A *watching* hook learns what a session does and never changes it: it exits with 0, prints nothing and blocks nothing. A *steering* hook may block a tool call with exit status 2 and a message for the agent. Every hook of Arbol's is a watching hook, except the check from outside's, the only steering hook. Keeping them apart means that a fault in the agent records can never stop a session, and that the one hook that can is small and can be reviewed alone.

### Sessions that run no hooks of the Leather Bag's

| Session | Why no hooks | Where it is said |
|---|---|---|
| A Driver's run | It runs in the Subscription's own home, to which no settings, hooks or plug-ins of the Leather Bag's are copied. Codex's `hooks` feature is on there, as shipped, but the home has no `hooks.json` | [CLD-3](../../../arbol-claude-driver/specs/03-tools-and-permissions.md), [CDX-3](../../../arbol-codex-driver/specs/03-tools-and-permissions.md); the conformance scenario checks that the owner's `hooks` never reach the home |
| The check from outside's Claude Code reviewer | `claude -p --safe-mode` | [The check from outside](../../../mycel/operations/agent-watch.md) |
| The check from outside's Codex reviewer | Not yet: `codex exec --ephemeral …` runs in `~/.codex` and will run every hook installed there ([PHK-D2](#decisions)) | — |

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

### The rules for running a hook

| Rule | Watching hook | Steering hook |
|---|---|---|
| Exit status | Always 0 | 2 only to block a `PreToolUse` it means to block; otherwise 0 |
| Output | Nothing, on standard output or standard error | Only the message to the agent, on standard error, with a blocked call |
| Foreground | Yes, never a background hook | Yes |
| Time limit in the tool's settings | 5 seconds; 3 for Codex's `SessionEnd` | The same |
| Own speed | At most 50 milliseconds in the median on this Mac when it has work to do | At most 50 milliseconds in the median when there is nothing to steer, which is almost always the case |
| On any fault of its own | Exits with 0 | Not decided ([PHK-D5](#decisions)) |
| The conversation | Keeps no part of it | Keeps no part of it |
| Elsewhere | Starts no process that outlives it, uses no network, writes only its own files | The same |

Several hooks on one event add their times. With all of them installed, Claude Code's `PreToolUse` starts three: `cc-status`, `arbol-agents hook` and `agent-watch-hook`.

### Hooks of different owners side by side

A steering hook's block is seen by the watching hooks only as a `PreToolUse` whose call never comes back ([PHK-D1](00-hooks-of-claude-code-and-codex.md#decisions)). The agent records then keep that call open until the end of the turn, which the next `Stop` corrects. Neither hook reads the other's files.

## Requirements

| ID | Every hook of Arbol's and its installer must… | Origin | Verified by |
|---|---|---|---|
| PHK-1.1 | be installed only into `~/.claude/settings.json`, `~/.codex/hooks.json` and `hooks.state` of `~/.codex/config.toml`, as a group of its own per event, leaving every other entry and setting as it is | New | unit |
| PHK-1.2 | run a command at a fixed path under `~/.local/bin`, without shell syntax, that never changes across Builds | New | unit |
| PHK-1.3 | write each file whole, keep a copy before its own first change and never overwrite it, refuse a file it cannot read, and add nothing twice | New | unit |
| PHK-1.4 | record Codex's trust only through `codex app-server`'s `hooks/list` and `config/batchWrite` | New | probe |
| PHK-1.5 | on `uninstall`, remove exactly its own entries and their trust entries; on `status`, say for each tool whether each entry is in place and trusted, and the tool's version | New | unit; probe |
| PHK-1.6 | as a watching hook, always exit with 0, print nothing and never run in the background | New | unit |
| PHK-1.7 | as a steering hook, block only a `PreToolUse` and print only the message to the agent | New | unit; live |
| PHK-1.8 | take at most 50 milliseconds in the median on this Mac, keep no part of the conversation, start no lasting process and use no network | New | unit; live |
| PHK-1.9 | not be run by a session that Arbol or its checks start for their own work, such as a Driver's run or a reviewer of the check from outside | New | contract; unit |

## Known problems in version 1

Version 1 used no hooks of either tool.

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| PHK-D2 | The check from outside's Codex reviewer runs `codex exec` in `~/.codex`. Once hooks are installed there, each review would create an agent record of its own and could be blocked by the check's own steering hook. Is it run without hooks? | Yes: its command line gets `--disable hooks`, beside `--disable apps` and the others it has. Its Claude Code counterpart already runs with `--safe-mode`. A test of the check asserts both | Open |
| PHK-D3 | Do the agent records and the check from outside share one installer? | No. Each installer writes only its own entries under the rules above, as the Beats SYL-202 and SYL-221 already plan. One installer would tie the agent records' Builds to the check's | Open |
| PHK-D4 | `cc-status` runs on ten Claude Code events with no time limit of its own, so the tool's default applies. Is a limit added to its entries? | No. It is not Arbol's hook, and the installers never change an entry they did not write | Open |
| PHK-D5 | What does the steering hook do when it fails on its own, for example when its steering file cannot be read? | It lets the call through and exits with 0. A broken hook that blocked would stop every session on the Mac, the session that could repair it included; a missed steer is caught by the next check five minutes later | Open |
