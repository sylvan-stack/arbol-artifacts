---
role: authored
spec: AGR-0
status: accepted
---
# Agent records · 00 The agent record

An *agent record* is a small JSON file that one agent session keeps up to date while it lives, such as `~/Library/Application Support/Arbol/agents/codex-01a1438b-1b0b-78c2-ae38-236d45157af0.json` for one Codex thread. It says who the agent is, which process runs it, what the agent waits for now and since when, and when the session ended. This specification states what counts as one agent session, where the records are kept, the fields of a record and how it is written so that a reader never sees half of it, how the process that owns a record is named, how a reader tells a working, waiting, silent, gone and ended agent apart, and how an Exchange of an Arbol Trunk takes part without a file of its own. It matters because until now only Arbol's own programs kept such a record (a Driver's run, [DRV-6](../driver-contract/06-state-and-simultaneous-calls.md); a Trunk's Exchange, [RCT-1](../../arbol-root/contract/01-the-exchange-folder.md)), so an agent that the Leather Bag ran in Claude Code or Codex was invisible to Arbol.

It follows the conventions of the [Driver Contract](../driver-contract/README.md#conventions) and of this chapter's [README](README.md#conventions). The hooks that write the records are in [AGR-1](01-the-hooks.md). The owner answered its question on 16 October 2026, and the specification was accepted the same day.

In this chapter the *owner* of a record is always a process, as in DRV-6. The person who works with the agent is the Leather Bag.

## Scope

Covered: what one agent session is, where the records are, the record and its fields, writing a record, the owner, what an agent waits for, signs of life, what a reader can tell, an Exchange of an Arbol Trunk, the program `arbol-agents` and its listing, removing old records, what changes elsewhere once this is accepted.

Not covered: which hook writes what, installing the hooks ([AGR-1](01-the-hooks.md)); the Radar itself; the check of holds, which belongs to the guide [Working in Sagas](../../mycel/operations/sagas.md) and reads these records as data; stopping or steering another tool's session; agents on other machines or in the cloud.

## Behaviour

### One agent session

An agent session is what the Leather Bag talks to as one conversation, in whatever tool:

| Tool | One agent session is | Its identifier | Example |
|---|---|---|---|
| Claude Code, in a terminal, in the Claude desktop app or as `claude -p` | One session | The session id, which Claude Code gives its hooks as `session_id` and the agent's commands as `CLAUDE_CODE_SESSION_ID` | `ace0b692-38cf-4eca-ac4c-1d8e53451149` |
| Codex, in a terminal, as `codex exec`, or in the Codex app | One thread | The thread id, which Codex gives its hooks as `session_id` and the agent's commands as `CODEX_THREAD_ID` | `01a1438b-1b0b-78c2-ae38-236d45157af0` |
| Arbol | One chat of a Root, seen through its Exchange in progress | The Root and the chat | `sapling/c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b` |

A sub-agent belongs to the session that started it: its hooks carry its parent's `session_id`, with an `agent_id` of its own (seen in the live checks for Codex). A session that is continued later, such as with `claude --resume` or by opening a Codex thread again, keeps its identifier and its record. A session that the Leather Bag clears with `/clear` is a new session: the old record ends, a new one begins.

A run of a Driver is not an agent session of its own. It runs in the Driver's Subscription home, where the hooks are not installed ([CLD-3](../../arbol-claude-driver/specs/03-tools-and-permissions.md): nothing of the Leather Bag's own setup reaches a run), and the Exchange that started it stands for it.

### Where the records are

```text
~/Library/Application Support/Arbol/agents/
  claude-code-ace0b692-38cf-4eca-ac4c-1d8e53451149.json     one Claude Code session
  codex-01a1438b-1b0b-78c2-ae38-236d45157af0.json           one Codex thread
  .lock                                                     taken by a hook while it rewrites a record
  .codex-01a1438b-1b0b-78c2-ae38-236d45157af0.json.4711.tmp a record being written: every reader skips a name that starts with a dot
```

The file is named `<tool>-<session>.json`. A session identifier holds only letters, digits and `-`; a hook that is given any other identifier writes nothing. The folder has the mode 0700 and its files 0600. It lies outside every Root, like `arbol-roots` ([ARC-1](../architecture/01-roots.md)): there is one for the Mac, because the agents on it are not part of any Root.

The records are the interface. A reader needs no Arbol program to read them: the rules of this specification are all it needs. Something that refers to an agent, such as a hold of a Beat, names it by `tool` and `session`, and the reader finds its record by that name. Arbol reads the records with `arbol-agents list` (below); the check of holds in Working in Sagas reads them itself, because a Mycel guide may read Arbol's data but never run Arbol's programs.

### The record

```json
{
  "agentRecord": 1,
  "tool": "codex",
  "session": "01a1438b-1b0b-78c2-ae38-236d45157af0",
  "entrypoint": "app-server",
  "owner": { "pid": 15922, "startedAt": "2026-10-16T07:09:12.000Z" },
  "workingFolder": "/Users/sam/repos/shop",
  "transcript": "/Users/sam/.codex/sessions/2026/10/16/rollout-2026-10-16T09-09-12-01a1438b-1b0b-78c2-ae38-236d45157af0.jsonl",
  "model": "gpt-6.1-sol",
  "startedAt": "2026-10-16T07:09:13.927Z",
  "waitingFor": "answer",
  "since": "2026-10-16T07:09:17.284Z",
  "toolName": "Bash",
  "lastEvent": { "name": "PermissionRequest", "at": "2026-10-16T07:09:17.284Z" },
  "calls": [ { "id": "exec-f9c1e3b4-56e1-427e-b1a2-2bd1a1120ae0", "name": "Bash", "asks": true } ]
}
```

| Field | What it is | Example |
|---|---|---|
| `agentRecord` | The format number, `1` for this specification. A reader that finds a higher number lists the record as unreadable | `1` |
| `tool` | `claude-code` or `codex` | `"codex"` |
| `session` | The session's identifier (above) | |
| `entrypoint` | Where the session runs, as the tool tells it: for Claude Code the value of `CLAUDE_CODE_ENTRYPOINT`, such as `cli` in a terminal or `claude-desktop` in the app; for Codex `app-server` when its owner is a `codex app-server` process, as in the Codex app, and `cli` otherwise. Absent when unknown | `"app-server"` |
| `owner` | The process that runs the session (below) | |
| `workingFolder` | The session's working folder, as the latest event of the session itself gave it | `"/Users/sam/repos/shop"` |
| `transcript` | The tool's own record file of the session, which Claude Code and Codex name `transcript_path`. Absent when no event has given it yet | |
| `model` | The model, when the tool names it. Codex names it in every event; Claude Code's hooks do not | `"gpt-6.1-sol"` |
| `startedAt` | When the first event of the session was seen | |
| `waitingFor` and `since` | What the agent waits for now, and since when (below) | `"answer"` |
| `toolName` | The name of the tool call opened last, while `waitingFor` is `tool` or `answer`. Only the name, never its input | `"Bash"` |
| `background` | Claude Code only: how many commands the agent left running in the background when its last turn ended | `1` |
| `lastEvent` | The name of the latest hook event and when it came | |
| `end` | Absent while the session lives. When it ends: `{ "at", "reason" }`, the reason as the tool gave it, such as `prompt_input_exit` when the Leather Bag typed `/exit` in Claude Code, or `other` | |
| `calls` | The hooks' own bookkeeping: the tool calls that are open, each with its identifier, its name and whether it asks the Leather Bag something. Readers ignore it | |

Every time has the form that JavaScript's `toISOString` writes, in UTC, as in BLD-0. A reader ignores a field it does not know, and shows a `waitingFor` it does not know as it is given.

The record holds no part of the conversation: no message, no prompt, no tool input or output, no answer ([AGR-D6](#decisions)). The hooks receive all of these and keep none of them.

### Writing a record

| Rule | Detail |
|---|---|
| One writer at a time | A hook takes the folder's lock before it reads a record, and gives it up after the rename. The lock is the system's lock (`flock`) on the file `.lock`, which is never removed. The system lets go of it when the hook ends in any way, so no lock outlives its writer ([AGR-D15](#decisions)). A hook holds it for a few milliseconds; one that has not got it after 1 second writes nothing |
| Replaced whole | The hook writes `.<file>.<pid>.tmp` in the same folder and renames it over the record, so a reader sees the old record or the new one, never a part ([DRV-6](../driver-contract/06-state-and-simultaneous-calls.md#writing-a-file)) |
| A missing or unreadable record | Is written anew from the event at hand. A hook installed in the middle of a session therefore starts its record with the next event |
| After the end | An ended record changes again only through a start event, or through an event from another process (below). Then its `end` is removed |

### The owner

The owner of a record is the process that runs the session, named as DRV-6 names the owner of a run: its process identifier and the time it was started, as `/bin/ps -o lstart= -p <pid>` prints it in a clean environment and the C locale ([DRV-D36](../driver-contract/06-state-and-simultaneous-calls.md#decisions)). A process is alive when a process with that number exists and was started at that time, give or take two seconds.

| Tool | Its owner | Found by the hook as | The agent counts as alive while |
|---|---|---|---|
| Claude Code | The session's own `claude` process. It runs one session at a time; the desktop app runs one for each open session | `CLAUDE_PID`, which is also the hook's parent process (seen in the live checks) | the owner is alive, and no newer record names the same owner: a process that has gone on to another session has left the old one |
| Codex | The `codex` process that has the thread loaded: `codex` or `codex exec` in a terminal, or the one `codex app-server` that runs every thread of the Codex app | the hook's parent process (seen in the live checks for all three) | some `codex` process has the thread's transcript open. Codex keeps that file open exactly while the thread is loaded, also when another process loaded it again, such as the Codex app after a restart. A record without `transcript`: while its owner is alive |

Which process becomes the owner:

| The event comes from | The record's owner |
|---|---|
| any process, and starts the session (`SessionStart`, but not after a compaction) | becomes that process |
| another process, while the record's owner is no longer alive or the record has ended | becomes that process, and `end` is removed. For example, a Codex thread opened again after the Codex app was restarted |
| another process, while the record's owner is alive | stays. The event still changes the record, except `SessionEnd`, which is ignored: the session goes on in its owner. This happens when one session runs in two processes at once, such as a thread open in the Codex app and in `codex resume` |

<!-- sources:
arbol:driver-contract/06-state-and-simultaneous-calls.md#Knowing that a process is alive
-->

### What an agent waits for

`waitingFor` uses the words of [ARC-3](../architecture/03-stuck-trunks.md#the-signs-of-life-of-a-trunk) and [RCT-1](../../arbol-root/contract/01-the-exchange-folder.md#signs-of-life), and one more for the time between two turns ([AGR-D3](#decisions)):

| `waitingFor` | The agent… | Example |
|---|---|---|
| `answer` | asked the Leather Bag a question, or asks permission for a tool call, and waits for the answer | "Which branch should I push to?" |
| `tool` | waits for a tool call to return, such as a command it runs | `make` for 2 h 10 min |
| `driver` | works: the model reads, thinks or writes, and no tool call or question is open | the agent writes its answer |
| `message` | has ended its turn and waits for the Leather Bag's next message | the answer is complete |

When several are true, the first in the order of this table is given. `driver` is ARC-3's word for an Exchange whose Driver run goes on; no Driver runs in a Claude Code or Codex session of the Leather Bag's own, but what it says is the same: the model is at work. `since` changes only when `waitingFor` changes: while one command runs for two hours, `since` stays at its start, and each new tool call after a pause in `driver` starts a new `since`. Which event of which tool leads to which value is in [AGR-1](01-the-hooks.md#which-hook-writes-what).

### Signs of life

A Trunk raises a heartbeat at least every 10 seconds (ARC-3). Claude Code and Codex have none: their hooks run only when something happens. A record's sign of life is therefore the later of two times: its `lastEvent.at`, and the time the tool last changed the session's transcript, which both tools write while they work ([AGR-D5](#decisions)). A record without `transcript` has only `lastEvent.at`.

An agent is *silent* when it waits for `driver` and has given no sign of life for 15 minutes: the idle limit of a Driver run ([DRV-4](../driver-contract/04-errors-and-limits.md#time-limits-of-a-run)). Waiting for an answer, a message or a tool call is never silent, however long it lasts ([ARC-3](../architecture/03-stuck-trunks.md#slow-is-not-stuck)). A silent agent is only shown, never stopped and never released: it may go on and change files.

<!-- sources:
arbol:architecture/03-stuck-trunks.md#Slow is not stuck
arbol:driver-contract/04-errors-and-limits.md#Time limits of a run
-->

### What a reader can tell

A reader tells six states apart from the record, its owner and its signs of life, in the order of this table:

| The record | The agent counts as alive (above) | State | Shown, for example, as |
|---|---|---|---|
| has `end` | — | `ended` | "ended at 16:40" |
| has no `end` | no | `gone`: it was killed, the Mac restarted, or the app quit without ending it | "gone since 16:40" |
| `waitingFor` is `answer` or `message` | yes | `waiting-for-leather-bag` | "waiting for your answer since 14:02", "waiting for your message since 14:02" |
| `waitingFor` is `tool` | yes | `waiting-for-command` | "running Bash for 2 h 10 min" |
| `waitingFor` is `driver`, a sign of life within 15 minutes | yes | `working` | "working" |
| `waitingFor` is `driver`, no sign of life for 15 minutes | yes | `silent` | "silent for 40 min" |

A record that cannot be read, or whose `agentRecord` is higher than the reader knows, is listed as unreadable and stops nothing. Checking a Codex record needs the files that `codex` processes have open: a reader asks `lsof` once for all of them, not once for each record, because the one `codex app-server` of the Codex app can hold dozens of threads (46 on 16 October 2026).

What this means for holds is the guide's to say. Once this specification is accepted, the guide releases a hold whose agent is `gone` or `ended`, keeps every other hold, and shows a `silent` one ([below](#what-changes-elsewhere)). Two cases follow from it: a Claude Code session that the Leather Bag ends with `/exit` and continues later with `--resume`, and a thread of the Codex app while the app is closed, lose their holds if a check runs in between ([AGR-D16](#decisions)).

### An Exchange of an Arbol Trunk

An Exchange keeps its own record already: `record.json` in its folder holds its process, `signsOfLife` with `heartbeat`, `waitingFor` and `since`, and, once it has ended, `end` ([RCT-1](../../arbol-root/contract/01-the-exchange-folder.md#the-record)). It takes part as it is: no agent record file is written for it, and the Root Contract is not changed ([AGR-D7](#decisions)).

`arbol-agents list` adds the Exchanges in progress of every Root the way ARC-1 says Arbol finds them: `arbol-roots list` for the Roots, and for each the listing of an `arbol-root` Build made for that Root ([RTM-0](../../arbol-root/specs/00-the-commands.md#the-listing)). Each listed Exchange becomes one agent of the tool `arbol`, with the session `<root>/<chat>` and the Exchange's process as its owner:

| RTM-0's `state` | `signsOfLife.waitingFor` | State in the agent view |
|---|---|---|
| `accepting`, `ending` | — | `working` |
| `running` | `answer` | `waiting-for-leather-bag` |
| `running` | `tool` | `waiting-for-command` |
| `running` | `driver`, `small-call`, `database`, or one the reader does not know | `working` |
| `unaccepted`, `unsaved`, `interrupted` | — | `ended`: the Exchange's process is gone, and Arbol settles it (ARC-2); its chat waits for the Leather Bag's next message |

The agent view never calls an Exchange silent. Whether an Exchange is stuck is decided by the Trunk itself and by the Arbol backend, which compares heartbeats between two looks and ends a stuck Exchange (ARC-3). A Root whose listing fails is named in `unreadable`.

A reader outside Arbol, such as the check of holds, reads the Exchange folders `~/Library/Application Support/Arbol/roots/<root>/exchanges/<exchange>/` directly, as RCT-1 says a folder tells a reader, with the same mapping. It lists as unreadable a record whose `rootContract` it does not know.

An Arbol chat has no process between two messages, and Arbol has no closing of a chat yet. A hold for an agent working in an Arbol chat therefore names the chat, stays while the chat waits for its next message, and is released only by hand until Arbol can close a chat ([AGR-D11](#decisions)). The agent learns its Root and chat from `ARBOL_ROOT` and `ARBOL_CHAT`, which the Trunk hands to the vendor tool. Until that is built, a Beat is worked in Claude Code or Codex directly, not in an Arbol chat.

<!-- sources:
arbol-root:contract/01-the-exchange-folder.md#The record
arbol-root:contract/01-the-exchange-folder.md#What a folder tells a reader
arbol-root:specs/00-the-commands.md#The listing
-->

### The program `arbol-agents`

`arbol-agents` is a small program in the `arbol` repository, beside `arbol-builds` and `arbol-roots`. Like `arbol-builds` it is typed Python that uses only the standard library, it is installed by that repository's install script, it lies outside every Root, and it is not itself a Build: there is one of it, replaced when it is installed again (BLD-0). It is reached through a path that never changes, `~/.local/bin/arbol-agents`, because the hooks name that path in the tools' settings ([AGR-D8](#decisions)). Its commands:

| Command | What it does |
|---|---|
| `arbol-agents hook claude-code` and `arbol-agents hook codex` | The hook: reads one event from its input and rewrites the session's record ([AGR-1](01-the-hooks.md)) |
| `arbol-agents list [--json]` | Lists every agent on the Mac: the records, and the Exchanges in progress of every Root, each with its state. It removes old records (below) |
| `arbol-agents install` and `arbol-agents uninstall` | Adds the hooks to the settings of Claude Code and Codex, or removes exactly what it added ([AGR-1](01-the-hooks.md#installing-the-hooks)) |
| `arbol-agents status` | Says for each tool whether the hooks are installed, whether Codex will run them (Codex runs a new hook only once it is trusted, AGR-1), and the tool's version |

For example, `arbol-agents list` prints:

```text
TOOL         SESSION                                       STATE                          SINCE  FOLDER
claude-code  ace0b692-38cf-4eca-ac4c-1d8e53451149          waiting for your message       14:02  ~/repos/shop
codex        01a1438b-1b0b-78c2-ae38-236d45157af0          running Bash                   13:51  ~/repos/shop
arbol        sapling/c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b  working                        14:10
```

### Removing old records

`arbol-agents list` removes every record that has ended, or whose agent no longer counts as alive, and whose `lastEvent.at` is more than 7 days old, and every leftover `.tmp` file older than one minute. It never removes the lock file. Nothing else removes records ([AGR-D10](#decisions)).

### What changes elsewhere

Once this specification is accepted, three documents follow it. Their changes are made in later Beats that hold them:

| Document | Change |
|---|---|
| The guide [Working in Sagas](../../mycel/operations/sagas.md) | A hold names its agent by `tool` and `session` instead of a process and a thread file; its check reads the record and releases a hold whose agent is `gone` or `ended`. *Silent* becomes this specification's: only an agent that works and gives no sign of life, not one that waits for the next message. Its "Not tried yet" is answered: `CODEX_THREAD_ID` is set in the threads of the Codex app and of the codex CLI, and the codex CLI keeps the thread's file open while it runs |
| [ARC-1](../architecture/01-roots.md) | `arbol-agents` and the folder of agent records join what lies outside every Root |
| DRV-2, RCT-2 and TRV-0 | As AGR-D11 decides: the Trunk hands `ARBOL_ROOT` and `ARBOL_CHAT` to the vendor tool's environment |

## Requirements

The hooks (`arbol-agents hook`):

| ID | A hook must… | Origin | Verified by |
|---|---|---|---|
| AGR-0.1 | keep one record for each agent session in `~/Library/Application Support/Arbol/agents/<tool>-<session>.json`, with the fields above, the folder 0700 and the files 0600, and write nothing for an identifier that holds anything but letters, digits and `-` | New | unit |
| AGR-0.2 | take the folder's lock (`flock` on `.lock`) before reading a record, write nothing when it has not got the lock within 1 second, and replace the record whole by renaming a temporary file over it | New | unit |
| AGR-0.3 | write a missing or unreadable record anew from the event at hand, and change an ended record only for a start event or an event from another process | New | unit |
| AGR-0.4 | name the owner by process identifier and start time, read with `/bin/ps` in a clean environment and the C locale: for Claude Code the process in `CLAUDE_PID`, for Codex the hook's parent process; and read the start time only when the process identifier differs from the record's owner | New | unit; live |
| AGR-0.5 | change the owner as the table "Which process becomes the owner" says, and ignore `SessionEnd` from a process other than a live owner | New | unit |
| AGR-0.6 | set `waitingFor` to the first that holds of `answer`, `tool`, `driver` and `message`, and change `since` only when `waitingFor` changes | New | unit |
| AGR-0.7 | keep no message, prompt, tool input, tool output or answer in the record | New | unit |

A reader (`arbol-agents list`, and any other program that reads the records):

| ID | A reader must… | Origin | Verified by |
|---|---|---|---|
| AGR-0.8 | tell `ended`, `gone`, `waiting-for-leather-bag`, `waiting-for-command`, `working` and `silent` apart as the table above says, in its order | New | unit |
| AGR-0.9 | count a Claude Code agent as alive while its owner is alive and no newer record names the same owner, and a Codex agent while some `codex` process has its transcript open, or, without a transcript, while its owner is alive | New | unit; drill |
| AGR-0.10 | take as a record's sign of life the later of `lastEvent.at` and the change time of its transcript, and call an agent silent only when it waits for `driver` and has given none for 15 minutes | New | unit |
| AGR-0.11 | never stop, release or change anything because an agent is silent | New | unit |
| AGR-0.12 | list a record it cannot read, or whose format number is higher than it knows, as unreadable, and go on with the others | New | unit |
| AGR-0.13 | skip every name in the folder that starts with a dot | New | unit |
| AGR-0.14 | map an Exchange to the agent view as the table above says, never call an Exchange silent, and list a record whose `rootContract` it does not know as unreadable | New | unit |

`arbol-agents list`:

| ID | `arbol-agents list` must… | Origin | Verified by |
|---|---|---|---|
| AGR-0.15 | add the Exchanges in progress of every Root, found through `arbol-roots list` and each Root's `arbol-root list`, without writing any file for them, and name a Root whose listing fails in `unreadable` | New | unit |
| AGR-0.16 | ask `lsof` once for all Codex records, not once for each record | New | unit |
| AGR-0.17 | remove records that ended, or whose agent no longer counts as alive, when their last event is more than 7 days old, and temporary files older than one minute, and never the lock file | New | unit |

## Interface

```ts
// ~/Library/Application Support/Arbol/agents/<tool>-<session>.json
interface AgentRecord {
  agentRecord: 1;                              // the format number
  tool: "claude-code" | "codex";
  session: string;                             // Claude Code: the session id; Codex: the thread id
  entrypoint?: string;                         // "cli", "claude-desktop", "app-server", …
  owner: { pid: number; startedAt: string };   // the process that runs the session (DRV-6)
  workingFolder: string;
  transcript?: string;                         // the tool's own record file of the session
  model?: string;                              // when the tool names it
  startedAt: string;                           // the first event seen
  waitingFor: "answer" | "tool" | "driver" | "message";
  since: string;
  toolName?: string;                           // the call opened last, while waitingFor is "tool" or "answer"
  background?: number;                         // Claude Code: commands left running in the background at the end of the last turn
  lastEvent: { name: string; at: string };     // the hook event's name as the tool gives it
  end?: { at: string; reason: string };
  calls: { id: string; name: string; asks: boolean }[];   // the hooks' bookkeeping: open tool calls
}

// arbol-agents list --json
interface AgentListing {
  agents: ListedAgent[];
  unreadable: string[];                        // record files, Exchange folders or Roots that could not be read
}

interface ListedAgent {
  tool: "claude-code" | "codex" | "arbol";
  session: string;                             // for "arbol": "<root>/<chat>"
  exchange?: string;                           // for "arbol": the Exchange in progress
  state: "working" | "waiting-for-leather-bag" | "waiting-for-command" | "silent" | "gone" | "ended";
  waitingFor?: string;                         // as in the record, or the Exchange's signsOfLife.waitingFor
  since?: string;
  owner?: { pid: number; startedAt: string; alive: boolean };
  entrypoint?: string;
  workingFolder?: string;
  model?: string;
  toolName?: string;
  background?: number;
  lastSignOfLife?: string;                     // absent for an Exchange
  end?: { at: string; reason: string };
}
```

## Known problems in version 1

Version 1 knew only the turns it ran itself. An agent that the Leather Bag ran in Claude Code or Codex outside Arbol was invisible to it, and nothing told whether such a session was still alive or what it waited for.

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| AGR-D1 | How are the records kept? | One JSON file for each session in one folder, written whole, as a Driver keeps its runs and a Trunk its Exchange. Any program can read them, nothing has to run for them, and one broken file harms nothing else. The alternatives: one shared log, or a database, which would need a lock across all sessions or a server | Technical choice, 16 October 2026 |
| AGR-D2 | Who owns a record? | The process that runs the session, as the hook's parent process gives it, by process identifier and start time (DRV-6); for Codex also the open transcript, because one `codex app-server` runs every thread of the Codex app | Technical choice, 16 October 2026 |
| AGR-D3 | Which words say what an agent waits for? | ARC-3's `answer`, `tool` and `driver`, and `message` for the time between two turns, which an Exchange does not have because it ends with its answer | Technical choice, 16 October 2026 |
| AGR-D4 | Are the hooks run in the background, so that they cannot slow a tool down? | No. Codex runs background hooks side by side and drops those still running when the session ends, so events could arrive out of order and the end could be lost. The hook is made fast instead (AGR-1) | Technical choice, 16 October 2026 |
| AGR-D5 | What is a sign of life, and when is an agent silent? | The latest hook event, or a change of the tool's transcript, whichever is later. Silent after 15 minutes without either while the agent works, the idle limit of a Driver run. The Mac's sleep counts, because silent is only shown | Technical choice, 16 October 2026 |
| AGR-D6 | What of the conversation does a record keep? | Nothing: names, identifiers, times, the working folder and the model only. The folder is readable by its user only, but a record is read by more programs than a transcript is | Technical choice, 16 October 2026 |
| AGR-D7 | How does an Exchange take part? | As it is: its `record.json` already has its process, what it waits for and since when, and its end. No file is written for it and the Root Contract is not changed | Technical choice, 16 October 2026 |
| AGR-D8 | Which program writes and reads the records? | `arbol-agents`, in the `arbol` repository beside `arbol-roots`, outside every Root, installed like `arbol-builds` and reached through `~/.local/bin/arbol-agents`. The hooks name that path in the tools' settings, so it must not change with an install, and Codex trusts a hook only as long as its command stays the same (AGR-1) | Technical choice, 16 October 2026 |
| AGR-D9 | Does a reader look into a tool's transcript to learn more, such as that the Leather Bag interrupted Claude Code? | No. It reads only the transcript's change time. The contents are the tool's own format and change without notice | Technical choice, 16 October 2026 |
| AGR-D10 | When are records removed? | By `arbol-agents list`, 7 days after the last event of a record that ended or whose agent no longer counts as alive. A hold or the Radar can still say what happened to an agent a few days later | Technical choice, 16 October 2026 |
| AGR-D11 | An agent working in an Arbol chat: what does its hold name, and when is it released? | The chat, not the Exchange. An Exchange ends with every answer, so a hold that named it would be released after each message. A hold that names the chat stays while the chat waits for the next message, and is released only by hand until Arbol can close a chat. For the agent to name its chat, the Trunk would hand `ARBOL_ROOT` and `ARBOL_CHAT` to the vendor tool's environment, which needs a field in the Driver's run request (DRV-2) and a line in RCT-2 and TRV-0: a later Beat | Decided 16 October 2026 by the owner: the proposed default |
| AGR-D15 | How do two hooks keep from writing one record at once? | The system's file lock (`flock`) on one lock file for the whole folder, held for a few milliseconds and never removed. DRV-6 uses lock files created exclusively instead, because Node.js had no file locks (DRV-D29); the hooks are Python, which has them, and the system releases such a lock when its process dies, so a killed hook never blocks the next one | Technical choice, 16 October 2026 |
| AGR-D16 | Does a session that ended count as the same agent when it is continued later? | It is the same record, taken back at the next start, but in between it had ended, and the guide releases its hold at that moment. A Beat held in a Claude Code session that the Leather Bag ends with `/exit` and later resumes, or in a Codex app thread while the app is closed, is released by a check that runs in between, and is taken again after the session resumes. The alternative, keeping a hold through an end, would leave Beats held by sessions that are never continued | Technical choice, 16 October 2026 |
