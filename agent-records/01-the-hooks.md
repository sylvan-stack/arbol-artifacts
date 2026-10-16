---
role: authored
spec: AGR-1
status: review
---
# Agent records · 01 The hooks of Claude Code and Codex

A *hook* is a command that Claude Code or Codex runs by itself at fixed moments of a session, such as before every tool call, and to which it hands a short JSON description of that moment on its standard input. This specification states which hooks of the two tools keep an [agent record](00-the-agent-record.md) up to date and what each one writes, how the hooks are installed once next to the hooks the Leather Bag already has, what they never do, and what they cannot see. It matters because the hooks are the only way to follow a session that Arbol did not start without changing the tool: Claude Code and Codex keep their full power, and the hooks only watch.

It follows the conventions of the [Driver Contract](../driver-contract/README.md#conventions) and of this chapter's [README](README.md#conventions). What it says about the two tools was seen in live checks on 16 October 2026 with Claude Code 2.1.294 in a terminal, Codex CLI 0.162.1 (`codex exec` and the terminal UI) and the Codex app's own `codex` 0.160.0 run as `codex app-server`, each in a test home ([Live checks](#live-checks-of-16-october-2026)). What was not tried is said where it is used.

## Scope

Covered: the one command every hook runs, which event writes what, sub-agents, questions to the Leather Bag, what the hooks never do, how fast they are, installing and removing them, Codex's trust in hooks, what the hooks cannot see, the live checks and how they are repeated for a new version of a tool.

Not covered: the record, its folder, its owner and how it is read ([AGR-0](00-the-agent-record.md)); the Exchanges of Arbol's Trunks, which keep their own record ([RCT-1](../../arbol-root/contract/01-the-exchange-folder.md)); a Driver's runs, in whose Subscription homes no hook is installed.

## Behaviour

### One command for every hook

Every hook runs the same command, with the tool's name as its only argument:

```text
/Users/sam/.local/bin/arbol-agents hook claude-code
/Users/sam/.local/bin/arbol-agents hook codex
```

The tool names the event in its input (`hook_event_name`), so one command serves every event. The command is a single program with two arguments, without any shell syntax, so that the tool starts it directly and the hook's parent process is the tool's own process (seen in the live checks). Should a shell stand between them anyway, the hook takes the shell's parent.

### Which hook writes what

Each row says what the event does to the record. *Open calls* are the tool calls that have begun and not yet returned; *asks* marks an open call that waits for the Leather Bag's answer (below). After every event, `waitingFor` is worked out anew: `answer` while an open call asks, otherwise `tool` while a call is open, otherwise `message` after the end of a turn, otherwise `driver` ([AGR-0](00-the-agent-record.md#what-an-agent-waits-for)).

| Event | Claude Code sends it | Codex sends it | What it does to the record |
|---|---|---|---|
| `SessionStart` | When `claude` starts, before the first message; on `--resume` and `/clear` | At the first message of a thread, not when the thread is opened; when a thread is continued | The record is created, or its `end` is removed. Owner, `entrypoint`, `workingFolder`, `transcript` and `model` are set, and `background` removed. The open calls are emptied and the turn counts as ended: `message` |
| `SessionStart` after a compaction (`source` is `compact`) | When it has compacted the conversation, also in the middle of a turn | The same | Only `lastEvent`: a compaction neither starts nor ends anything |
| `UserPromptSubmit` | At each message of the Leather Bag, and at the notice that a command left in the background has ended | At each message | A turn begins: `driver`, unless calls are still open. The open calls are kept, because such a notice can come while another call runs |
| `PreToolUse` | Before each tool call | Before each tool call: a command, `apply_patch`, an MCP tool, starting or waiting for a sub-agent | The call is added to the open calls, and `toolName` set. A tool that exists to ask the Leather Bag (below) is marked as asking |
| `PermissionRequest` | When it asks permission for a call; also for `AskUserQuestion` | When it asks approval for a call | The open call of the same tool opened last is marked as asking |
| `Notification` with `permission_prompt` or `elicitation_dialog`, and `Elicitation` | Yes | — | The open call opened last is marked as asking. With no call open, only `lastEvent` |
| `ElicitationResult` | Yes | — | The open call opened last is no longer marked as asking |
| `PostToolUse`, `PostToolUseFailure`, `PermissionDenied` | After each tool call | `PostToolUse` | The call is taken off the open calls |
| `Stop`, `StopFailure` | At the end of each turn, with `background_tasks`, the commands left running in the background | `Stop` | The turn has ended: the open calls are emptied, `message`. Claude Code: `background` becomes the number of those commands still running |
| `Interrupt` | — | When the Leather Bag interrupts a turn | The turn has ended: the open calls are emptied, `message` |
| `Notification` with `idle_prompt` | 60 seconds after a turn ended without a new message | — | The turn has ended: the open calls are emptied, `message` |
| `SubagentStart`, `SubagentStop`, `PreCompact`, `PostCompact`, any other `Notification` | Yes | Yes | Only `lastEvent`: a sign of life |
| `SessionEnd` | On `/exit`, `/clear`, signing out, at the end of `claude -p`. Whether the desktop app sends it when it closes a session was not tried | At the end of `codex exec`, on quitting the terminal UI, on archiving or deleting a thread (seen in the live checks); by Codex's documentation also when it unloads a thread that was idle for 30 minutes and open in no window, which the Codex app does not do while it runs (below) | `end`, with the reason the tool gives. Ignored when it comes from another process while the record's owner is alive ([AGR-0](00-the-agent-record.md#the-owner)) |

Every event also sets `lastEvent`. `workingFolder` and `transcript` are taken only from events of the session itself, not of a sub-agent; `transcript` only from `SessionStart` and `UserPromptSubmit`.

### Sub-agents

An event that comes from a sub-agent carries the session's `session_id` and an `agent_id` of its own. Codex gives such events the sub-agent's own transcript (seen in the live checks). An event with an `agent_id` changes only the open calls and `lastEvent`: a tool call of a sub-agent is an open call of the session, so while a sub-agent runs a command, the session waits for a command; but a sub-agent's end of turn, its start and its transcript change nothing else.

### Questions to the Leather Bag

Some tools exist to ask the Leather Bag something. While their call is open, the record says `answer`, not `tool`. A permission request marks its own call in the same way.

| Tool | The tool that asks | Seen in the live checks |
|---|---|---|
| Claude Code | `AskUserQuestion`, which asks one or more questions with choices; `ExitPlanMode`, which asks to approve a plan | `AskUserQuestion`: `PreToolUse`, then `PermissionRequest`, then after 6 seconds `Notification` `permission_prompt`; `PostToolUse` once answered. `ExitPlanMode` was not tried |
| Codex | `request_user_input` | Not tried: whether Codex sends `PreToolUse` for it is to be checked before it is relied on |

A permission request names the tool but not the call. The hook therefore marks the open call of that tool that was opened last; with two calls of one tool open at once, it may mark the other one, which changes nothing that a reader sees.

### What the hooks never do

| Rule | Why |
|---|---|
| They never block, approve, deny or change anything. The hook always exits with 0 | Exit status 2 blocks a tool call in both tools |
| They print nothing, on standard output or standard error | Both tools add what a `SessionStart` or `UserPromptSubmit` hook prints to what the model reads |
| They run in the foreground, not as background hooks ([AGR-D4](00-the-agent-record.md#decisions)) | Codex runs background hooks side by side and drops those still running at the end of the session |
| They give up after 1 second without the folder's lock, and the tools' settings give each hook a time limit of 5 seconds, 3 for Codex's `SessionEnd`, the most Codex allows there | A hook must never hold a session up |
| They keep no part of the conversation ([AGR-0.7](00-the-agent-record.md#requirements)) | The input holds the prompt, the tool's input and output and the last message |
| They start no process that outlives them, use no network and touch no file but the agent records | — |

### How fast a hook is

A tool waits for its hooks, so a hook adds its time to each event. In the live checks Python took about 30 milliseconds to start, a hook's own work of reading its input, asking `ps` and writing a small file about 10 more, and asking `lsof` about 120 more. The hook therefore asks `ps` only when the process identifier differs from the record's owner, which happens at a session's start, and never asks `lsof`: that is the reader's work ([AGR-0](00-the-agent-record.md#what-a-reader-can-tell)). It must take at most 50 milliseconds in the median on this Mac, and at most 100 when it asks `ps`.

The Leather Bag already runs iTerm2's `cc-status` on ten Claude Code events, so each of those events starts two hooks.

### Installing the hooks

`arbol-agents install` adds the hooks once, for all sessions of each tool on the Mac:

| Tool | Where | What is added | What else |
|---|---|---|---|
| Claude Code | `~/.claude/settings.json`, which the terminal `claude` and the Claude desktop app both read: the app starts each session with `--setting-sources=user,project,local` (seen in the app's own process, version 2.1.299) | For each event of the table above, one more entry in the event's list under `hooks`. The entries already there, such as `cc-status`, stay as they are | Nothing |
| Codex | `~/.codex/hooks.json`, which `codex` in a terminal and the Codex app both read | The same, with Codex's event names | Codex runs a hook only once it is trusted ([AGR-D12](#decisions)). The installer records the trust through Codex itself: it starts `codex app-server`, asks `hooks/list` for each new hook's key and `currentHash`, and writes them under `hooks.state` in `~/.codex/config.toml` with Codex's own `config/batchWrite`, which leaves the rest of the file as it is (tried in a throwaway home: the hooks then count as trusted for both Codex versions, which compute the same hash) |

For example, Claude Code's `PreToolUse` list with the entry that was there before and the one added, and the file `~/.codex/hooks.json` with one of its events:

```json
"PreToolUse": [
  { "hooks": [ { "type": "command", "command": "/Users/sam/.config/iterm2/cc-status" } ] },
  { "hooks": [ { "type": "command", "command": "/Users/sam/.local/bin/arbol-agents hook claude-code", "timeout": 5 } ] }
]
```

```json
{
  "hooks": {
    "SessionEnd": [
      { "hooks": [ { "type": "command", "command": "/Users/sam/.local/bin/arbol-agents hook codex", "timeout": 3 } ] }
    ]
  }
}
```

| Rule | Detail |
|---|---|
| Whole files | Each settings file is written whole, through a temporary file and a rename. A file that cannot be read as JSON is left alone, and the command fails naming it |
| A copy first | Before the first change ever made to a file, a copy of it is kept beside it as `<name>.before-arbol-agents`. A later `install` or `uninstall` never overwrites that copy |
| Once | Running `install` again adds nothing that is there already. It recognises its own entries by their command |
| The command never changes | Codex trusts a hook only for its exact definition: a hook whose command changes is skipped until it is trusted again. The path `~/.local/bin/arbol-agents` therefore stays the same across installs ([AGR-D8](00-the-agent-record.md#decisions)) |
| Only the Leather Bag's own settings | Never a project's settings (`.claude/settings.json`, `.codex/hooks.json` of a repository), never a Subscription home of a Driver, never Codex's `notify`, which Computer Use already uses |
| When it takes effect | Claude Code reads its hooks when a session starts; a session that was running already keeps its old hooks. The Codex app reads them when its `codex app-server` starts, so the Leather Bag quits and reopens the Codex app once, which loads its threads anew; `install` says so when it ends |
| Removing | `arbol-agents uninstall` removes exactly the entries whose command is `arbol-agents hook`, and their trust entries, and nothing else |

`arbol-agents status` says, for each tool, whether every entry is in place, whether Codex counts each as trusted (`hooks/list`), and the tool's version.

### What the hooks cannot see

| Case | What the record says | How long |
|---|---|---|
| The Leather Bag interrupts Claude Code with Esc | Claude Code sends no hook at all: no `Stop`, no `PostToolUse`, and no `idle_prompt` in the next 75 seconds (live check). Only its transcript records "[Request interrupted by user]". The record keeps `tool` or `driver` | Until the end of the next turn, or of the session. A record left at `driver` shows as silent after 15 minutes ([AGR-D13](#decisions)) |
| The Leather Bag grants a permission | Neither tool sends a hook when the answer is given, only when the call ends. The record keeps `answer` while the approved command runs | Until the call ends. Rare here: the Leather Bag runs both tools with full permissions, but `AskUserQuestion` asks permission even then |
| A command left running in the background after the turn | `message`, because the agent waits for the Leather Bag. Claude Code's `background` says how many such commands run; Codex says nothing | Until the next turn |
| A Codex thread before its first message | No record: Codex sends `SessionStart` only with the first message. Nothing happens in such a thread | — |
| A Codex app thread the Leather Bag is not looking at | The Codex app keeps its threads loaded while it runs: on 16 October 2026 its `codex app-server` had 46 threads open, the oldest from 12 October. Such a thread waits for a `message` | Until it is archived or deleted, or the app quits |
| Codex's `request_user_input`, Claude Code's `ExitPlanMode`, the Claude desktop app ending a session | Not tried. If no hook comes, the record keeps `tool`, or misses its `end`; then the reader sees the owner gone once the process ends | Checked before they are relied on |
| A session killed outright, or a Mac that restarts | No `SessionEnd` | The reader sees the agent gone ([AGR-0](00-the-agent-record.md#what-a-reader-can-tell)) |
| A `SessionEnd` hook that takes longer than Codex allows | No `end` | The reader sees the agent gone once no process holds its transcript |

### Live checks of 16 October 2026

Each tool ran in a test home, with hooks that recorded what they were given and their parent process, and sent short messages on the test accounts. Claude Code ran in its test Subscription's home with the hooks given through `--settings`; Codex in its test Subscription's home with the hooks given through `-c` with `--dangerously-bypass-hook-trust`, and, for `codex app-server`, through a `hooks.json` and trust entries added to that home for the check and removed afterwards. Neither tool's settings in `~/.claude` or `~/.codex` were changed.

| Tool and form | Events seen | Seen besides |
|---|---|---|
| Claude Code 2.1.294, `claude -p` | `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, `SessionEnd` | The hook's parent process is the `claude` process, whose number is in `CLAUDE_PID`; `CLAUDE_CODE_SESSION_ID` is set. The transcript is not held open |
| Claude Code 2.1.294, terminal | The above, `PermissionRequest`, `Notification` (`permission_prompt`, `idle_prompt` 60 seconds after `Stop`), `SubagentStop`; `SessionEnd` with `prompt_input_exit` on `/exit` | `SessionStart` comes at start, before any message. A command the agent puts in the background ends its call at once; its end comes back as a new `UserPromptSubmit`, and `Stop` lists it in `background_tasks`. Esc during a command: no hook |
| Claude Code 2.1.299 in the Claude desktop app | None: no hook was added there | Seen in this app's own processes: one `claude` process for each open session, alive for hours while the session waits; started with `--setting-sources=user,project,local`; `CLAUDE_CODE_ENTRYPOINT` is `claude-desktop` |
| Codex CLI 0.162.1, `codex exec` | `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, `SessionEnd`; with a sub-agent also `SubagentStart` and `SubagentStop`, under the parent's `session_id` | The hook's parent process is the `codex` process, which holds the transcript open until it ends. `CODEX_THREAD_ID` is set in the agent's commands, not in the hooks' environment |
| Codex CLI 0.162.1, terminal UI | `SessionStart` at the first message, then as above; `SessionEnd` on `/quit` | The `codex` process holds the transcript open while it runs, between turns too |
| Codex 0.160.0 of the Codex app, as `codex app-server` | `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `Stop`, `Interrupt`; `SessionEnd` when the thread was archived, not when the client stopped following it | Hooks given on the command line are never trusted, and `--dangerously-bypass-hook-trust` is ignored: only trust entries in the home's `config.toml` count. The hook's parent is the `codex app-server` process, which holds the transcript open while the thread is loaded. `CODEX_THREAD_ID` is set in the agent's commands |

A new version of either tool may send other events, or none. `arbol-agents status` names the version, and the live checks above are repeated, scripted, for each new version before it is relied on: the requirements below that are verified by *live*.

## Requirements

| ID | The hooks and `arbol-agents install` must… | Origin | Verified by |
|---|---|---|---|
| AGR-1.1 | change the record as the table "Which hook writes what" says, for each event of each tool | New | unit; live |
| AGR-1.2 | let an event that carries an `agent_id` change only the open calls and `lastEvent` | New | unit; live |
| AGR-1.3 | mark as asking a call of `AskUserQuestion` or `ExitPlanMode` (Claude Code) or `request_user_input` (Codex), and the open call that a permission request concerns | New | unit; live |
| AGR-1.4 | take `transcript` only from `SessionStart` and `UserPromptSubmit` of the session itself, and the owner from `CLAUDE_PID` (Claude Code) or the parent process, past a shell (Codex) | New | unit; live |
| AGR-1.5 | always exit with 0, print nothing, and keep no part of the conversation | New | unit |
| AGR-1.6 | take at most 50 milliseconds in the median on this Mac, at most 100 when it asks `ps`, and never ask `lsof` | New | live |
| AGR-1.7 | install for every event of the table one entry that runs `~/.local/bin/arbol-agents hook <tool>` in the foreground, with a time limit of 5 seconds (3 for Codex's `SessionEnd`), in `~/.claude/settings.json` and `~/.codex/hooks.json` only, leaving every other entry and setting as it is | New | unit |
| AGR-1.8 | write each settings file whole, keep a copy of it before the first change ever made and never overwrite that copy, refuse a file it cannot read, and add nothing twice | New | unit |
| AGR-1.9 | record Codex's trust in the new hooks through Codex's own `hooks/list` and `config/batchWrite`, as [AGR-D12](#decisions) decides, and say at the end that the Codex app is to be reopened | New | probe |
| AGR-1.10 | on `uninstall`, remove exactly its own entries and their trust entries | New | unit |
| AGR-1.11 | on `status`, say for each tool whether every entry is in place, whether Codex trusts it, and the tool's version | New | unit; probe |

## Interface

What the hooks read from their input, as the two tools send it (seen in the live checks):

```ts
interface HookInput {                         // JSON on standard input, one object
  hook_event_name: string;                    // "SessionStart", "PreToolUse", …
  session_id: string;                         // Claude Code: the session; Codex: the thread, also for a sub-agent
  transcript_path?: string | null;            // the tool's own record file of the session; for a Codex sub-agent its own
  cwd: string;
  model?: string;                             // Codex only
  source?: string;                            // SessionStart: "startup", "resume", "clear", "compact", "fork"
  reason?: string;                            // SessionEnd
  tool_name?: string;                         // PreToolUse, PermissionRequest, PostToolUse: "Bash", "AskUserQuestion", …
  tool_use_id?: string;                       // PreToolUse, PostToolUse: identifies the call
  notification_type?: string;                 // Claude Code Notification: "permission_prompt", "idle_prompt", "elicitation_dialog", …
  background_tasks?: { id: string; status: string }[];   // Claude Code Stop
  agent_id?: string;                          // events of a sub-agent
  // prompt, tool_input, tool_response, last_assistant_message: present, and never kept
}
```

From the environment, Claude Code's hooks read `CLAUDE_PID` and `CLAUDE_CODE_ENTRYPOINT`. Codex gives its hooks no variable of its own but `CODEX_HOME`.

```text
arbol-agents hook claude-code | codex      reads one event, rewrites one record, prints nothing, exits 0
arbol-agents install                       adds the hooks; prints what it added for each tool, and that the Codex app is to be reopened
arbol-agents uninstall                     removes them
arbol-agents status [--json]               for each tool: installed, trusted (Codex), version
```

## Known problems in version 1

Version 1 used no hooks of either tool. It saw only the turns it ran itself.

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| AGR-D12 | Codex runs a new hook only after the Leather Bag has reviewed and trusted it, for example with `/hooks` in `codex`. Does `arbol-agents install` record that trust itself? | Yes. Installing is the Leather Bag's own act, and the command shows what it adds. It records the trust through Codex's own calls, so Codex computes and stores it. The alternative: `install` adds the hooks, and the Leather Bag trusts them once in `codex` with `/hooks`; until then Codex skips them and `status` says so | Open |
| AGR-D13 | Claude Code sends no hook when the Leather Bag interrupts it. Is anything done about it? | No. The record is corrected by the end of the next turn or of the session, and only the Radar shows it wrong meanwhile. Reading the transcript's last line would tie Arbol to a format Claude Code changes without notice (AGR-D9) | Technical choice, 16 October 2026 |
| AGR-D14 | Which events are installed? | Every event that changes the record or shows life, as the table says: 17 of Claude Code's and all 12 of Codex's. Events that say nothing about waiting, such as a changed setting or a created task, are left out | Technical choice, 16 October 2026 |
