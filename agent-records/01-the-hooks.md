---
role: authored
spec: AGR-1
status: accepted
---
# Agent records · 01 The hooks of Claude Code and Codex

A *hook* is a command that Claude Code or Codex runs by itself at fixed moments of a session, such as before every tool call, and to which it hands a short JSON description of that moment on its standard input. This specification states which hooks of the two tools keep an [agent record](00-the-agent-record.md) up to date and what each one writes, how the hooks are installed once next to the hooks the Leather Bag already has, what they never do, and what they cannot see. It matters because the hooks are the only way to follow a session that Arbol did not start without changing the tool: Claude Code and Codex keep their full power, and the hooks only watch.

It follows the conventions of the [Driver Contract](../driver-contract/README.md#conventions) and of this chapter's [README](README.md#conventions). What Claude Code and Codex do with a hook, and the live checks of 16 October 2026 that saw it, are in [PHK-0](../architecture/provider-hooks/00-hooks-of-claude-code-and-codex.md); the rules every hook of Arbol's follows, and the other hooks on this Mac, are in [PHK-1](../architecture/provider-hooks/01-hooks-on-this-mac.md). Both were taken out of this specification on 19 October 2026 without a change of meaning. The owner answered its question on 16 October 2026, and the specification was accepted the same day.

## Scope

Covered: the one command every hook runs, which event writes what, sub-agents, questions to the Leather Bag, what the hooks never do, how fast they are, installing and removing them, what the record says where the hooks cannot see.

Not covered: the record, its folder, its owner and how it is read ([AGR-0](00-the-agent-record.md)); the Exchanges of Arbol's Trunks, which keep their own record ([RCT-1](../../arbol-root/contract/01-the-exchange-folder.md)); a Driver's runs, which run these hooks since DRV-D42 and for which the hook writes no record ([AGR-D17](#decisions)); when each tool sends each event, what it hands a hook, Codex's trust and the live checks ([PHK-0](../architecture/provider-hooks/00-hooks-of-claude-code-and-codex.md)); the rules shared with every other hook of Arbol's ([PHK-1](../architecture/provider-hooks/01-hooks-on-this-mac.md)).

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

When each tool sends each event is in [PHK-0](../architecture/provider-hooks/00-hooks-of-claude-code-and-codex.md#the-events-and-when-each-tool-sends-them).

| Event | Sent by | What it does to the record |
|---|---|---|
| `SessionStart` | Both | The record is created, or its `end` is removed. Owner, `entrypoint`, `workingFolder`, `transcript` and `model` are set, and `background` removed. The open calls are emptied and the turn counts as ended: `message` |
| `SessionStart` after a compaction (`source` is `compact`) | Both | Only `lastEvent`: a compaction neither starts nor ends anything |
| `UserPromptSubmit` | Both | A turn begins: `driver`, unless calls are still open. The open calls are kept, because Claude Code's notice that a background command ended can come while another call runs |
| `PreToolUse` | Both | The call is added to the open calls, and `toolName` set. A tool that exists to ask the Leather Bag (below) is marked as asking |
| `PermissionRequest` | Both | The open call of the same tool opened last is marked as asking |
| `Notification` with `permission_prompt` or `elicitation_dialog`, and `Elicitation` | Claude Code | The open call opened last is marked as asking. With no call open, only `lastEvent` |
| `ElicitationResult` | Claude Code | The open call opened last is no longer marked as asking |
| `PostToolUse`, `PostToolUseFailure`, `PermissionDenied` | Both send `PostToolUse`; the other two only Claude Code | The call is taken off the open calls |
| `Stop`, `StopFailure` | Both send `Stop`; `StopFailure` only Claude Code | The turn has ended: the open calls are emptied, `message`. Claude Code: `background` becomes the number of `background_tasks` still running |
| `Interrupt` | Codex | The turn has ended: the open calls are emptied, `message` |
| `Notification` with `idle_prompt` | Claude Code | The turn has ended: the open calls are emptied, `message` |
| `SubagentStart`, `SubagentStop`, `PreCompact`, `PostCompact` | Both | Only `lastEvent`: a sign of life |
| Any other `Notification` | Claude Code | Only `lastEvent`: a sign of life |
| `SessionEnd` | Both | `end`, with the reason the tool gives. Ignored when it comes from another process while the record's owner is alive ([AGR-0](00-the-agent-record.md#the-owner)) |

Every event also sets `lastEvent`. `workingFolder` and `transcript` are taken only from events of the session itself, not of a sub-agent; `transcript` only from `SessionStart` and `UserPromptSubmit`.

### Sub-agents

An event that comes from a sub-agent carries the session's `session_id` and an `agent_id` of its own ([PHK-0](../architecture/provider-hooks/00-hooks-of-claude-code-and-codex.md#the-events-and-when-each-tool-sends-them)). An event with an `agent_id` changes only the open calls and `lastEvent`: a tool call of a sub-agent is an open call of the session, so while a sub-agent runs a command, the session waits for a command; but a sub-agent's end of turn, its start and its transcript change nothing else.

### Questions to the Leather Bag

Some tools exist to ask the Leather Bag something. While their call is open, the record says `answer`, not `tool`. A permission request marks its own call in the same way.

| Tool | The tool that asks | Seen in the live checks |
|---|---|---|
| Claude Code | `AskUserQuestion`, which asks one or more questions with choices; `ExitPlanMode`, which asks to approve a plan | `AskUserQuestion`: yes ([PHK-0](../architecture/provider-hooks/00-hooks-of-claude-code-and-codex.md#live-checks-of-16-october-2026)). `ExitPlanMode` was not tried |
| Codex | `request_user_input` | Not tried: whether Codex sends `PreToolUse` for it is to be checked before it is relied on |

A permission request names the tool but not the call. The hook therefore marks the open call of that tool that was opened last; with two calls of one tool open at once, it may mark the other one, which changes nothing that a reader sees.

### What the hooks never do

They are watching hooks and follow [PHK-1](../architecture/provider-hooks/01-hooks-on-this-mac.md#the-rules-for-running-a-hook)'s rules for one: they never block, approve, deny or change anything and always exit with 0; they print nothing; they run in the foreground ([AGR-D4](00-the-agent-record.md#decisions)); the tools' settings give each a time limit of 5 seconds, 3 for Codex's `SessionEnd`; they keep no part of the conversation ([AGR-0.7](00-the-agent-record.md#requirements)); they start no process that outlives them, use no network and touch no file but the agent records. Besides, a hook gives up after 1 second without the folder's lock.

### How fast a hook is

A tool waits for its hooks, so a hook adds its time to each event ([PHK-0](../architecture/provider-hooks/00-hooks-of-claude-code-and-codex.md#how-long-a-tool-waits)). Asking `ps` costs a hook little and asking `lsof` much, so the hook asks `ps` only when the process identifier differs from the record's owner, which happens at a session's start, and never asks `lsof`: that is the reader's work ([AGR-0](00-the-agent-record.md#what-a-reader-can-tell)). It must take at most 50 milliseconds in the median on this Mac, and at most 100 when it asks `ps`.

### Installing the hooks

`arbol-agents install` adds the hooks once, for all sessions of each tool on the Mac:

| Tool | Where | What is added | What else |
|---|---|---|---|
| Claude Code | `~/.claude/settings.json`, which the terminal `claude` and the Claude desktop app both read: the app starts each session with `--setting-sources=user,project,local` (seen in the app's own process, version 2.1.299) | For each event of the table above, one more entry in the event's list under `hooks`. The entries already there, whoever wrote them, stay as they are | Nothing |
| Codex | `~/.codex/hooks.json`, which `codex` in a terminal and the Codex app both read | The same, with Codex's event names | Codex runs a hook only once it is trusted ([AGR-D12](#decisions)). The installer records the trust through Codex itself, as [PHK-0](../architecture/provider-hooks/00-hooks-of-claude-code-and-codex.md#codexs-trust) describes |

For example, Claude Code's `PreToolUse` list with the entry that was there before and the one added, and the file `~/.codex/hooks.json` with one of its events:

```json
"PreToolUse": [
  { "hooks": [ { "type": "command", "command": "<a hook of another program>" } ] },
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

The installer follows [PHK-1](../architecture/provider-hooks/01-hooks-on-this-mac.md#the-rules-for-installing-a-hook)'s rules for installing a hook. Its own names under them: the copy of a file is `<name>.before-arbol-agents`, the command is always `~/.local/bin/arbol-agents` ([AGR-D8](00-the-agent-record.md#decisions)), and `arbol-agents uninstall` removes exactly the entries whose command is `arbol-agents hook`, and their trust entries. When it ends, `install` says that running Claude Code sessions keep their old hooks and that the Codex app is to be quit and reopened once ([PHK-0](../architecture/provider-hooks/00-hooks-of-claude-code-and-codex.md#when-a-change-takes-effect)).

`arbol-agents status` says, for each tool, whether every entry is in place, whether Codex counts each as trusted (`hooks/list`), and the tool's version.

### What the hooks cannot see

What the tools do not send is in [PHK-0](../architecture/provider-hooks/00-hooks-of-claude-code-and-codex.md#what-no-hook-sees). What the record says meanwhile:

| Case | What the record says | How long |
|---|---|---|
| The Leather Bag interrupts Claude Code with Esc | It keeps `tool` or `driver` | Until the end of the next turn, or of the session. A record left at `driver` shows as silent after 15 minutes ([AGR-D13](#decisions)) |
| The Leather Bag grants a permission | It keeps `answer` while the approved command runs | Until the call ends. Rare here: the Leather Bag runs both tools with full permissions, but `AskUserQuestion` asks permission even then |
| A command left running in the background after the turn | `message`, because the agent waits for the Leather Bag. Claude Code's `background` says how many such commands run; Codex says nothing | Until the next turn |
| A Codex thread before its first message | No record. Nothing happens in such a thread | — |
| A Codex app thread the Leather Bag is not looking at | `message` | Until it is archived or deleted, or the app quits |
| Codex's `request_user_input`, Claude Code's `ExitPlanMode`, the Claude desktop app ending a session | If no hook comes, the record keeps `tool`, or misses its `end`; then the reader sees the owner gone once the process ends | Checked before they are relied on |
| A session killed outright, or a Mac that restarts | No `end` | The reader sees the agent gone ([AGR-0](00-the-agent-record.md#what-a-reader-can-tell)) |
| A `SessionEnd` hook that takes longer than Codex allows | No `end` | The reader sees the agent gone once no process holds its transcript |

### Live checks

The live checks of 16 October 2026, with Claude Code 2.1.294 and 2.1.299 and Codex 0.162.1 and 0.160.0, are in [PHK-0](../architecture/provider-hooks/00-hooks-of-claude-code-and-codex.md#live-checks-of-16-october-2026). `arbol-agents status` names each tool's version, and the checks are repeated, scripted, for each new version before it is relied on ([PHK-0.1](../architecture/provider-hooks/00-hooks-of-claude-code-and-codex.md#requirements)): the requirements below that are verified by *live*.

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

The hooks read these fields of the input that [PHK-0](../architecture/provider-hooks/00-hooks-of-claude-code-and-codex.md#interface) describes: `hook_event_name`, `session_id`, `transcript_path`, `cwd`, `model`, `source`, `reason`, `tool_name`, `tool_use_id`, `notification_type`, `background_tasks` and `agent_id`. The prompt, the tool's input and output and the last message are present, and never kept. From the environment, Claude Code's hooks read `CLAUDE_PID` and `CLAUDE_CODE_ENTRYPOINT`; Codex gives its hooks no variable of its own but `CODEX_HOME`.

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
| AGR-D12 | Codex runs a new hook only after the Leather Bag has reviewed and trusted it, for example with `/hooks` in `codex`. Does `arbol-agents install` record that trust itself? | Yes. Installing is the Leather Bag's own act, and the command shows what it adds. It records the trust through Codex's own calls, so Codex computes and stores it. The alternative: `install` adds the hooks, and the Leather Bag trusts them once in `codex` with `/hooks`; until then Codex skips them and `status` says so | Decided 16 October 2026 by the owner: the proposed default |
| AGR-D13 | Claude Code sends no hook when the Leather Bag interrupts it. Is anything done about it? | No. The record is corrected by the end of the next turn or of the session, and only the Radar shows it wrong meanwhile. Reading the transcript's last line would tie Arbol to a format Claude Code changes without notice (AGR-D9) | Technical choice, 16 October 2026 |
| AGR-D14 | Which events are installed? | Every event that changes the record or shows life, as the table says: 17 of Claude Code's and all 12 of Codex's. Events that say nothing about waiting, such as a changed setting or a created task, are left out | Technical choice, 16 October 2026 |
| AGR-D17 | Since 19 October 2026 a Driver runs `claude` and `codex` in their default homes (DRV-D42), so a run of an Arbol chat runs these hooks too. Does it get an agent record? | No. The hook writes nothing when `ARBOL_ROOT` is in its environment, because the run's Exchange already keeps its own record (AGR-D7). Until the Driver's caller sets `ARBOL_ROOT` (SYL-207), such a run gets an ordinary record, which shows the chat twice | Open: technical consequence of DRV-D42, proposed 19 October 2026 |
