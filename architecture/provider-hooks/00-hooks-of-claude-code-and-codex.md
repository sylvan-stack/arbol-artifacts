---
role: authored
spec: PHK-0
status: draft
---
# Provider hooks · 00 The hooks of Claude Code and Codex

What Claude Code and Codex do with a hook: where it is set, at which moments each tool runs it, what it is given, what its exit status and its output do, how long the tool waits, Codex's trust in it, and what no hook can see. It matters because every hook Arbol installs rests on these facts, and both tools change them without notice: a fact written once here is checked once for each new version of a tool, not once for each hook.

It follows the conventions of this chapter's [README](README.md#conventions). It says what the tools do, not what a hook of Arbol's does with it; that is in [AGR-1](../../agent-records/01-the-hooks.md) for the agent records and in [PHK-1](01-hooks-on-this-mac.md) for the rules every such hook follows.

## Scope

Covered: where each tool reads its hooks, the events and when each tool sends them, a hook's input, the effect of its exit status and output, time limits and background hooks, Codex's trust, when a change takes effect, Codex's `notify`, what no hook sees, the live checks and how they are repeated.

Not covered: which hooks are on this Mac and the rules for installing one ([PHK-1](01-hooks-on-this-mac.md)); what the agent records' hook writes ([AGR-1](../../agent-records/01-the-hooks.md)); the hooks of other tools, such as git's.

## Behaviour

### Where each tool reads its hooks

| | Claude Code | Codex |
|---|---|---|
| The Leather Bag's own file | `~/.claude/settings.json`, key `hooks` | `~/.codex/hooks.json`, key `hooks` |
| Who reads it | The terminal `claude`; `claude-zai`, which is `claude` with the same home and one more settings file (`--settings ~/.claude/settings-zai.json`, which has no hooks); the Claude desktop app, which starts each session with `--setting-sources=user,project,local` (seen in the app's own process, version 2.1.299) | `codex` in a terminal and the Codex app's own `codex app-server` |
| A repository's file | `.claude/settings.json` and `.claude/settings.local.json` of the working folder | `.codex/hooks.json` of the working folder |
| On the command line | `--settings <file>` | `-c` overrides; the Codex app ignores hooks given this way ([Codex's trust](#codexs-trust)) |
| Switched off | `--safe-mode` leaves out hooks, CLAUDE.md and MCP servers | `--disable hooks`: `hooks` is a stable feature, on as shipped (`codex features list`, 19 October 2026) |

Both files have the same shape: for each event a list of groups, each with an optional `matcher` on the tool name and a list of commands:

```json
{
  "hooks": {
    "PreToolUse": [
      { "hooks": [ { "type": "command", "command": "/Users/sam/.config/iterm2/cc-status" } ] },
      { "hooks": [ { "type": "command", "command": "/Users/sam/.local/bin/arbol-agents hook claude-code", "timeout": 5 } ] }
    ]
  }
}
```

A command that is a single program with its arguments, without any shell syntax, is started directly: the hook's parent process is the tool's own process (seen in the live checks).

### The events, and when each tool sends them

| Event | Claude Code sends it | Codex sends it |
|---|---|---|
| `SessionStart` | When `claude` starts, before the first message; on `--resume` and `/clear`; after a compaction, with `source` `compact`, also in the middle of a turn | At the first message of a thread, not when the thread is opened; when a thread is continued; after a compaction, with `source` `compact` |
| `UserPromptSubmit` | At each message of the Leather Bag, and at the notice that a command left in the background has ended | At each message |
| `PreToolUse` | Before each tool call | Before each tool call: a command, `apply_patch`, an MCP tool, starting or waiting for a sub-agent |
| `PermissionRequest` | When it asks permission for a call; also for `AskUserQuestion`, even with full permissions | When it asks approval for a call |
| `Notification` | With a `notification_type`: `permission_prompt` (6 seconds after a `PermissionRequest` left unanswered), `idle_prompt` (60 seconds after a turn ended without a new message), `elicitation_dialog`, and others | Yes |
| `Elicitation`, `ElicitationResult` | When an MCP server asks the Leather Bag something, and when it is answered | — |
| `PostToolUse` | After each tool call that succeeded | After each tool call |
| `PostToolUseFailure`, `PermissionDenied` | After a call that failed, or was denied | — |
| `Stop` | At the end of each turn, with `background_tasks`, the commands left running in the background | At the end of each turn |
| `StopFailure` | At the end of a turn that failed | — |
| `Interrupt` | — | When the Leather Bag interrupts a turn |
| `SubagentStart`, `SubagentStop` | When a sub-agent starts and ends | The same, under the parent's `session_id` |
| `PreCompact`, `PostCompact` | Around a compaction | The same |
| `SessionEnd` | On `/exit`, `/clear`, signing out, at the end of `claude -p`. Whether the desktop app sends it when it closes a session was not tried | At the end of `codex exec`, on quitting the terminal UI, on archiving or deleting a thread (seen in the live checks); by Codex's documentation also when it unloads a thread that was idle for 30 minutes and open in no window, which the Codex app does not do while it runs |

An event that comes from a sub-agent carries the session's `session_id` and an `agent_id` of its own. Codex gives such events the sub-agent's own transcript.

Claude Code sends further events that say nothing about what a session waits for, such as a changed setting or a created task. They are left out here, as AGR-D14 leaves them out of the agent records.

### What a hook is given

One JSON object on standard input ([Interface](#interface)). It holds the prompt, the tool's input and output and the last message of the agent: a hook that keeps any of it keeps part of the conversation.

From the environment, a Claude Code hook can read `CLAUDE_PID`, the `claude` process, `CLAUDE_CODE_SESSION_ID` and `CLAUDE_CODE_ENTRYPOINT` (`cli`, `claude-desktop`, …). A Codex hook gets no variable of its own but `CODEX_HOME`; `CODEX_THREAD_ID` is set in the agent's commands, not in the hooks.

### What a hook's answer does

| The hook… | Claude Code | Codex |
|---|---|---|
| exits with 0 | Nothing happens | Nothing happens |
| exits with 2 in `PreToolUse` | The call is blocked; what the hook wrote on standard error is given to the model | The same |
| prints on standard output in `SessionStart` or `UserPromptSubmit` | Added to what the model reads | The same |
| exits with another status | Not tried | Not tried |
| answers with a JSON decision on standard output | Not tried | Not tried |

Which event follows a call that a hook blocked, if any, was not tried ([PHK-D1](#decisions)).

### How long a tool waits

| Rule | Claude Code | Codex |
|---|---|---|
| The tool waits for its hooks before it goes on | Yes | Yes, for hooks in the foreground |
| Time limit of a hook | `timeout` in seconds, per command | `timeout` in seconds, per command; at most 3 seconds for `SessionEnd` |
| Background hooks | Not tried | Run side by side; those still running at the end of the session are dropped |
| Several hooks on one event | All are run; whether one after another or side by side was not tried | The same |

In the live checks, Python took about 30 milliseconds to start, reading the input, asking `ps` and writing a small file about 10 more, and asking `lsof` about 120 more. A hook adds its own time to every event it is set on.

### Codex's trust

Codex runs a hook from `hooks.json` only once it is trusted, and only for its exact definition: a hook whose command changes is skipped until it is trusted again. Trust is kept under `hooks.state` in `~/.codex/config.toml`, as each hook's key and `currentHash`.

| How trust is given | Works |
|---|---|
| The Leather Bag reviews the hook with `/hooks` in `codex` | Yes |
| A program starts `codex app-server`, asks `hooks/list` for each hook's key and `currentHash`, and writes them with `config/batchWrite`, which leaves the rest of the file as it is | Yes, tried in a throwaway home; Codex 0.160.0 and 0.162.1 compute the same hash |
| `--dangerously-bypass-hook-trust` | Only for `codex exec` and the terminal UI, and only for that invocation. `codex app-server`, and so the Codex app, ignores it |

Claude Code has no such trust: a hook in its settings runs.

### When a change takes effect

| Tool | A change to the hooks counts… |
|---|---|
| Claude Code | From the next session. A running session keeps the hooks it started with |
| Codex in a terminal | From the next `codex` |
| The Codex app | When its `codex app-server` starts again: the Leather Bag quits and reopens the app, which loads its threads anew |

### Codex's `notify`

`notify` in `~/.codex/config.toml` is not a hook. It names one program that Codex starts once per finished turn, by Codex's documentation with a JSON description of the turn as its last argument; it cannot block anything. There is room for only one, and on this Mac it is Computer Use's `SkyComputerUseClient … turn-ended`.

### What no hook sees

| Case | What the tools send |
|---|---|
| The Leather Bag interrupts Claude Code with Esc | Nothing at all: no `Stop`, no `PostToolUse`, and no `idle_prompt` in the next 75 seconds (live check). Only the transcript records "[Request interrupted by user]" |
| The Leather Bag answers a permission request | Neither tool sends a hook when the answer is given, only when the call ends |
| A command left running in the background after the turn | Claude Code lists it in `Stop`'s `background_tasks` and sends `UserPromptSubmit` when it ends. Codex says nothing |
| A Codex thread before its first message | Nothing: `SessionStart` comes with the first message |
| A Codex app thread the Leather Bag is not looking at | Nothing. The app keeps its threads loaded while it runs: on 16 October 2026 its `codex app-server` had 46 threads open, the oldest from 12 October |
| A session killed outright, or a Mac that restarts | No `SessionEnd` |
| A `SessionEnd` hook slower than Codex allows | It is cut off |
| Codex's `request_user_input`, Claude Code's `ExitPlanMode`, the Claude desktop app closing a session | Not tried |

### Live checks of 16 October 2026

Each tool ran in a test home, with hooks that recorded what they were given and their parent process, and sent short messages on the test accounts. Claude Code ran in its test Subscription's home with the hooks given through `--settings`; Codex in its test Subscription's home with the hooks given through `-c` with `--dangerously-bypass-hook-trust`, and, for `codex app-server`, through a `hooks.json` and trust entries added to that home for the check and removed afterwards. Neither tool's settings in `~/.claude` or `~/.codex` were changed.

| Tool and form | Events seen | Seen besides |
|---|---|---|
| Claude Code 2.1.294, `claude -p` | `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, `SessionEnd` | The hook's parent process is the `claude` process, whose number is in `CLAUDE_PID`; `CLAUDE_CODE_SESSION_ID` is set. The transcript is not held open |
| Claude Code 2.1.294, terminal | The above, `PermissionRequest`, `Notification` (`permission_prompt`, `idle_prompt` 60 seconds after `Stop`), `SubagentStop`; `SessionEnd` with `prompt_input_exit` on `/exit` | `SessionStart` comes at start, before any message. A command the agent puts in the background ends its call at once; its end comes back as a new `UserPromptSubmit`, and `Stop` lists it in `background_tasks`. Esc during a command: no hook. `AskUserQuestion`: `PreToolUse`, then `PermissionRequest`, then after 6 seconds `Notification` `permission_prompt`; `PostToolUse` once answered |
| Claude Code 2.1.299 in the Claude desktop app | None: no hook was added there | One `claude` process for each open session, alive for hours while the session waits; started with `--setting-sources=user,project,local`; `CLAUDE_CODE_ENTRYPOINT` is `claude-desktop` |
| Codex CLI 0.162.1, `codex exec` | `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`, `SessionEnd`; with a sub-agent also `SubagentStart` and `SubagentStop`, under the parent's `session_id` | The hook's parent process is the `codex` process, which holds the transcript open until it ends |
| Codex CLI 0.162.1, terminal UI | `SessionStart` at the first message, then as above; `SessionEnd` on `/quit` | The `codex` process holds the transcript open while it runs, between turns too |
| Codex 0.160.0 of the Codex app, as `codex app-server` | `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `Stop`, `Interrupt`; `SessionEnd` when the thread was archived, not when the client stopped following it | Hooks given on the command line are never trusted, and `--dangerously-bypass-hook-trust` is ignored: only trust entries in the home's `config.toml` count. The hook's parent is the `codex app-server` process, which holds the transcript open while the thread is loaded |

A new version of either tool may send other events, or none. The checks above are repeated, scripted, for each new version before a hook relies on it (PHK-0.1). The agent records' Beat SYL-204 writes that script.

## Requirements

| ID | Arbol must… | Origin | Verified by |
|---|---|---|---|
| PHK-0.1 | repeat the live checks of this specification, scripted, for each new version of Claude Code or Codex before a hook of Arbol's relies on it, and record the version, the date and every difference from this specification | New | live |

## Interface

What the two tools send on a hook's standard input (seen in the live checks):

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
  prompt?: string;                            // UserPromptSubmit
  tool_input?: unknown;                       // PreToolUse, PostToolUse
  tool_response?: unknown;                    // PostToolUse
  last_assistant_message?: string;            // Stop
}
```

## Known problems in version 1

Version 1 used no hooks of either tool. It saw only the turns it ran itself.

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| PHK-D1 | When a `PreToolUse` hook blocks a call with exit status 2, does either tool send `PostToolUse`, `PostToolUseFailure` or nothing for that call? A watching hook that saw the `PreToolUse` keeps the call open until it learns | Settled by the live check of SYL-221, which blocks calls in both tools; written here with the result | Open |
