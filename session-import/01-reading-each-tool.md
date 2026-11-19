---
role: authored
spec: IMP-1
status: accepted
---
# Session Import · 01 Reading each tool

## Purpose

[IMP-0](00-the-import.md) turns a session into a chat once the session is known as a list of turns. This specification says how each tool's saved records become that list. It covers:
- where a tool keeps its sessions, and which files belong to one;
- how to tell what kind of session it is;
- which records to drop as duplicates;
- where one turn ends;
- where the prompt, text, tool calls, usage, model and working folder come from.

The measurements behind it are in [Importing native harness sessions](../research/native-session-import.md).

## Scope

The five formats as they are on the owner's Mac on 17 November 2026:

| Tool | Version |
|---|---|
| Claude Code | 2.1.280–2.1.325 |
| Codex CLI and Desktop | 0.155.0-alpha.16 to 0.167.1 |
| Kimi Code Desktop | 1.1.3–1.3.5, wire `protocol_version` 1.5 |
| Pi | 1.1.0, session format 3 |
| Mimo | `0.1.16-arbol4` |

A tool may change its format without notice. Each reader follows [IMP-D10](#decisions) for what it does not recognise.

Not covered: the rows themselves, the archive and re-import, all of which are in IMP-0.

## Behaviour

### What every reader gives IMP-0

A reader yields one **session**, a list of **turns** and the session's archive files.

**The session.** `nativeId`, `kind`, `title`, `createdAt`, `toolVersion` and `origin` (the facts named for the tool below), and `live` as IMP-0 defines it.

**Each turn**, in native order:
- `turnKey` and `trigger`;
- `prompt`: the text the owner typed, or for a turn the tool started, the trigger text;
- `startedAt` and `endedAt`;
- `state` (`completed`, `failed`, `cancelled` or `interrupted`) and, for `failed`, the tool's error text and kind;
- `workingFolder`, `model` and `effort`;
- `usage`: one entry per model response of the main agent, each with the response's `startedAt`, so that IMP-0 can assign it to a segment ([IMP-D12](#decisions)). Codex uses the usage record's time if the response start was not saved ([IMP-D22](00-the-import.md#decisions));
- `items`, an ordered list of:
  - text blocks of the main agent, each with the time it was written;
  - tool calls: `callId`, `agent`, `name`, `input`, `result`, `ok`, `error`, `parentCallId` and `startedAt`;
- `subagents`: one record per sub-agent that worked in the turn, with its native agent ID, the `callId` of the call that started it or none when that call cannot be found, the time of its first record, whether its last turn failed, and its usage. A turn's `usage` leaves out its sub-agents'; IMP-0 adds theirs to the run ([IMP-D12](#decisions));
- `steers`: the inputs the owner added during the turn, each with its time. IMP-0 splits the turn at them.

**The archive files** of a session are each a file in the tool's home with its path relative to the home, or rows of a database exported as JSON. Exported rows take the database file's modification time as their `mtime` ([IMP-D12](#decisions)).

**Common rules for every reader.**
- A line-oriented file is split only at `\n`. A last line without `\n` is ignored, because the tool is still writing it.
- Duplicate records are dropped by the tool's rule below before turns are formed.
- **Usage** gives `inputTokens` as input + cache read + cache write, with `cachedInputTokens` (cache read) and `cacheWriteTokens` beside it, and `outputTokens`, as IMP-0 stores them.
- A turn can end in a way that the tool's state rule below does not name. It is then `failed`, and its error kind is the tool's word for that ending.
- A session that fails after its native ID is known keeps the kind its tool's table gives for the records read before the failure ([IMP-D16](00-the-import.md#decisions)).

### Claude Code

**Where.**
- One top-level session is `~/.claude/projects/<folder>/<session>.jsonl`. Its identity is the file name's session ID.
- Its folder `<session>/` holds:
  - `subagents/` (with `workflows/`);
  - `tool-results/`;
  - `custom-title.json`.

The archive takes the `.jsonl` file and that whole folder, plus the `~/.claude/file-history/` entries its `file-history-*` records name. Nothing else under `~/.claude` is archived: not settings, credentials, `memory/` or other projects.

A readable session with no complete record still yields a session with no turns, so the importer reports `empty`. Its internal creation time is the earliest modification time of its top-level session files. A file with no complete record contributes no line to time ordering or deduplication. [IMP-D17](00-the-import.md#decisions)

**Kind.**
| Kind | Rule |
|---|---|
| `arbol_driver` | The session is named in a Claude Driver chat map under the Driver's state, `~/.arbol/drivers/claude/subscriptions/*/chats/` ([ARC-5](../architecture/05-where-arbol-keeps-its-files.md); `~/Library/Application Support/Arbol/drivers/claude/…` before the installed move), or holds a line with `version: "synthetic-arbol"` |
| `probe` | Its folder is a `-private-tmp-*` folder, its `entrypoint` is `sdk-cli`, it has no `bridge-session` line, and its first prompt matches a recorded probe of the Arbol, Forester or conformance suites |
| `agent_launched` | Any other `sdk-cli` session |
| `owner` | Everything else: `claude-desktop` and `cli` |

If the supplied Driver chat-map directory or an entry cannot be read or decoded, continue with the readable entries and the session records. Unavailable map data contributes no evidence and produces no session failure. [IMP-D18](00-the-import.md#decisions)

`origin` keeps `entrypoint`, `permissionMode`, the folder name and the first `turnOrigin`.

**Duplicates.**
- A line's `uuid` is its identity. The session files of a project folder are read in the order of their first record's time. A line whose `uuid` already appeared in an earlier file is dropped, because continuing a session in a new file copies its earlier lines.
- An API response spans several assistant lines with the same `message.id`, and its usage is counted once.

**Turns.**
- **Start.** A turn starts at a user line that meets all of these:
  - it carries no tool result;
  - it is neither `isMeta` nor `isCompactSummary`;
  - it is not an interruption marker (text beginning `[Request interrupted by user`);
  - it is not only command-wrapper text (`<command-name>`, `<command-message>`, `<local-command-stdout>`).

  Lines that fail these tests stay in the archive. An interruption marker makes the turn before it `cancelled`.
- **Prompt.** The line's string content or its `text` blocks. `image` blocks are left out as IMP-0 says.
- **Trigger.**
  - `typed` for `turnOrigin` `human`, or where `turnOrigin` is absent;
  - `task` for `task_notification`;
  - `system` for `sdk`, `peer` and `host_synthetic`.
- **Steers.** A `queued_command` attachment within the turn is a steer.
- **End and key.** A turn ends before the next start. `turnKey` is the start line's `uuid`.
- **State.**
  - `cancelled` when an interruption marker follows it;
  - `failed` when its last assistant line has `isApiErrorMessage`, with the line's `error` as the kind and its text as the message;
  - `completed` when its last assistant line has `stop_reason: end_turn`;
  - `interrupted` otherwise.

**Items.**
- Assistant `text` blocks are text blocks.
- A `tool_use` block is joined with the `tool_result` that names its ID. The result's content is read as text. A result that points to a `tool-results/` file takes that file's text, and image parts are described as IMP-0 says.
- `is_error` sets `ok` false and `error` to the result text.

**Sub-agents.**
- A sub-agent file's `.meta.json` `toolUseId` names the parent's `Agent` or `Task` call. Its lines are read as items with `agent` set to the file's agent ID.
- Workflow agents under `subagents/workflows/` are nested the same way under the call that launched the workflow.

**Usage and model.** Usage is the sum over distinct `message.id`s of `message.usage`: `input_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens` and `output_tokens`. `model` is the first assistant line's `message.model`, and `effort` its `effort`.

**Working folder, version and title.**
- The working folder is the start line's `cwd`, and `toolVersion` the start line's `version`.
- The title is the last `custom-title` line, else `custom-title.json`, else the last `ai-title`.

**Live.** By modification time only (IMP-0).

### Codex

**Where.**
- One top-level session is one rollout whose `session_meta` names no parent thread: `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl[.zst]` or a rollout in `~/.codex/archived_sessions/`. Its identity is `session_meta.id`, so a rollout moved between the two folders is the same session.
- A `.zst` file is decompressed as a stream.
- A verified private copy of `~/.codex/state_5.sqlite` and any write-ahead log, opened read-only, gives the title (`threads.title`, else the name in `session_index.jsonl`) and archival. A thread's `rollout_path` is matched with and without `.zst`.
- An unavailable part of the shared state catalogue, session title index or Driver chat map supplies no evidence. Continue with the parts that can be read and the evidence in the rollouts. Unavailable shared metadata causes no session failure. Take a consistent copy of the catalogue and its write-ahead log in the supplied private work folder, including for a dry run. Do not open the originals with SQLite. If bounded attempts cannot verify a consistent copy, apply IMP-D19. Remove the copy and any private sidecars after reading ([IMP-D19 and IMP-D34](00-the-import.md#decisions)).
- When rollout files have the same validated native ID, use the catalogue's matching path for conversation projection. When no copy matches it, use the most recently modified copy. The raw archive keeps the verified copies. [IMP-D21](00-the-import.md#decisions)

The archive takes the rollout files of the session and of all its sub-agent threads, plus the session's rows of `threads` and `thread_spawn_edges` exported as JSON. Nothing else in `~/.codex` is archived, including `auth.json`, `config.toml`, `thread_history_1.sqlite` (derived from the rollouts) and the logs.

**Kind.**
| Kind | Rule |
|---|---|
| `arbol_driver` | `originator` is `arbol-codex-driver`, or the thread is named in a Codex Driver chat map |
| `probe` | `originator` is `hook-probe`, or the agent role begins `probe_` |
| `agent_launched` | `originator` is `codex_exec`, or the `source` is `agent_created_thread` |
| `scheduled` | At least one root turn start was validated and every validated root turn's trigger is `automation_heartbeat_scheduled` ([IMP-D20](00-the-import.md#decisions)) |
| `owner` | Everything else: Codex Desktop, `codex_work_desktop` and `codex-tui` |

`origin` keeps `originator`, `source`, `thread_source` and the session's working folder.

**Duplicates.**
- **Assistant text** comes from `response_item/message` with role `assistant` only. `item_completed:AgentMessage` repeats it.
- **Prompts.** A user `response_item/message` whose `content_item_kinds` is `["user.text"]` is a typed prompt. Every other user-role message is harness context and stays in the archive ([IMP-D11](#decisions)).
- **Reasoning** is not read. It is encrypted, and both of its copies stay in the archive.
- **Usage** comes from `token_usage_record` only. `token_count` repeats it.
- **Compaction.** `compacted` lines and their `replacement_history` are skipped.
- **Forks.** In a forked sub-agent thread, every line whose `ordinal` is below `subagent_history_start_ordinal` copies the parent's history and is skipped.

**Turns.**
- **Bounds and key.** A turn starts at `event_msg/task_started` and ends at its `task_complete` or `turn_aborted`, or else at the next `task_started`. Its records carry its `turn_id`, which is the `turnKey`.
- **Prompt and steers.** The first `user.text` message of the turn is its prompt, and each later `user.text` message within the turn is a steer. A turn with no `user.text` message takes its first harness user message as its prompt, or else its trigger name.
- **Trigger.**
  - `typed` for `composer` and `edit_user_message`;
  - `scheduled` for `automation_heartbeat_scheduled`;
  - `system` for the rest.
- **State.**
  - `completed` on `task_complete` without an error;
  - `failed` when `task_complete` carries an error, with its kind;
  - `cancelled` on `turn_aborted` with reason `interrupted`;
  - `failed` on any other abort reason, with that reason as the kind;
  - `interrupted` when the turn has no end.

**Items.**
- Assistant messages (`commentary` and `final_answer` alike) are text blocks.
- A `function_call` (name `namespace::name`) or `custom_tool_call` is joined with the `…_output` that has the same `call_id`.
  - A call whose linked command item has an exit code is `ok` exactly when that code is 0.
  - Any other call is `ok` unless its output is an error object.
- **Work inside `exec`.** The command executions, MCP calls and file changes that an `exec` call ran are `item_completed` items with no call link. Each becomes a call with `parentCallId` set to the `exec` call whose time span contains it. When two `exec` calls overlap, the item stays in the archive.

**Sub-agents.**
- A thread whose `session_meta.source.subagent.thread_spawn.parent_thread_id` names a thread of this session is a sub-agent. Its items have `agent` set to its thread ID.
- They are nested under the call that spawned the thread, found through `thread_spawn_edges` and the spawning call's output. Otherwise IMP-0's fallback applies.
- Deeper sub-agents are nested the same way.
- When the native root turn ID places a reused sub-agent's later work in a different turn, assign its work and usage there. Use IMP-0's fallback in that turn if the spawning call belongs to an earlier turn. [IMP-D23](00-the-import.md#decisions)

**Usage, model and folder.** Usage is the sum of `token_usage_record.usage` with the turn's `turn_id`: `input`, `cached_input`, `cache_write_input`, `output` and `reasoning_output`. Use the response start when present, else the usage record's time for segment assignment ([IMP-D22](00-the-import.md#decisions)). `model`, `effort` and the working folder come from the turn's last `turn_context`, and `toolVersion` from `session_meta.cli_version`.

**Live.** By modification time only. A turn with no end in a session that is not live is `interrupted`.

### Kimi Code

**Where.**
- One session is a folder `~/.kimi-code/sessions/<workspace>/session_<uuid>/`, and its identity is that UUID.
- Its conversation is `agents/main/wire.jsonl`, and each sub-agent has `agents/<agent>/wire.jsonl`.
- `state.json` gives the title, the working folder, archival and `forkedFrom`.

The archive takes, from the session folder:
- `state.json`;
- `agents/*/wire.jsonl`, `blobs/`, `tool-results/`, `file-history/`, `tasks/`, `plans/`;
- `media/` and `media-originals/`.

It also takes the files under `~/.kimi-code/files/` that the session's `kimi-file://` references name. Never archived:
- the session's `logs/` and its `.wal`, `.index` and `.postings` files;
- `credentials/`, `oauth/`, `server.token`, `device_id` and `config.toml*`;
- `server/events/`, a UI journal that repeats tool output;
- `search-index/`, `cache/` and `image-upload-cache/`;
- uploads that no session references.

**Kind.**
| Kind | Rule |
|---|---|
| `probe` | A one-turn session with no tool calls whose prompt exactly matches a documented Forester hook-installation probe ([IMP-D28](00-the-import.md#decisions)) |
| `owner` | Everything else, the `*-test` workspaces included |

Kimi Code has no Arbol Driver, so no session is `arbol_driver`. `origin` keeps the workspace folder name and the first prompt's `origin.kind`.

**Records read.**
- Only these are read: `turn.*`, `prompt.*`, `context.append_message`, `context.append_loop_event`, `context.apply_compaction`, `context.undo`, `context.clear`, `llm.request`, `subagent.*`, and `metadata`. The legacy `agent.*` stream of versions before 1.3.5 repeats the conversation and is not read.
- **Forks.** A forked session (`forkedFrom`) drops every record whose `uuid` also appears in the session it was forked from, because a fork copies its source's records. If that source is missing or unreadable, report just the fork as `unreadable_session` ([IMP-D24](00-the-import.md#decisions)).
- **Empty session.** If the main wire is readable but has no complete record, the session has no turns and the importer reports it as `empty`. Use `state.json.createdAt` when available, otherwise the main wire's modification time, as the internal creation time ([IMP-D25](00-the-import.md#decisions)).
- **Undo and clear.** `context.undo` with count N removes the previous N messages from the turn being read. `context.clear` ends the readable history before it. Both are honoured even though no session uses them today.

**Turns.**
- **Bounds and key.** A turn runs from `turn.prompt` to its `turn.ended`. Its key is the `turnId`, read as text, because the prompt writes it as a number and the loop events as text.
- **Prompt and trigger.** The prompt is `turn.prompt.input`'s text parts. The trigger is `typed` for `origin.kind` `user`, `task` for `task`, and `system` for `skill_activation` and `system_trigger`.
- **Steers.** Each `turn.steer` within the turn is a steer.
- **State.** `turn.ended.reason` `completed`, `failed` and `cancelled` map to the same states; with no end, the state is `interrupted`.

**Items.**
- A `content.part` of kind `text` is a text block. Kind `think` stays in the archive.
- A `tool.call` (`toolCallId`, `name`, `args`) is joined with the `tool.result` whose `parentUuid` is the call's `uuid`.
  - `isError` sets `ok` false and `error`.
  - Output spilled to `tool-results/` is read from there.
  - `blobref:`, `data:`, `kimi-file://` and `ms://` images are described as IMP-0 says when native metadata or an eligible in-home file gives their media type and size. Otherwise the reference stays in the archive. The reader does not fetch remote images ([IMP-D27](00-the-import.md#decisions)).
- Injected `context.append_message` records whose `origin.kind` is not `user` stay in the archive.

**Sub-agents.** `subagent.spawned.parentToolCallId` names the call. The sub-agent's wire is read the same way, with `agent` set to its agent ID, and its calls are nested under that call.

**Usage, model and folder.** Usage is the sum of the turn's `step.end.usage`, with input `inputOther + inputCacheRead + inputCacheCreation`. `model` and `effort` come together from the last retained `llm.request` of kind `loop` in the turn ([IMP-D26](00-the-import.md#decisions)). The working folder is `state.json.cwd`, and `toolVersion` the version `metadata` records.

**Live.** The session's lock in `~/.kimi-code/locks/sessions/` is held, or a wire changed in the last 10 minutes.

### Pi

**Where.**
- One session is `~/.pi/agent/sessions/<folder>/<time>_<id>.jsonl`, and its identity is the header's `id`.
- The archive takes that file, plus any file that a result's `details.fullOutputPath` names, but only when that file is inside `~/.pi/agent`. Read a spilled result only from an eligible file whose resolved path stays inside the supplied Pi home. For an outside-home path, use the saved inline result and its truncation flag and count the file in `filesNotArchived` ([IMP-D29](00-the-import.md#decisions)).
- Never archived: `auth.json`, `models*.json`, `settings.json`, `install/` and `bin/`.

**Kind.**
| Kind | Rule |
|---|---|
| `arbol_driver` | The first entry after the header is `custom` with `customType: "arbol-history-import"` |
| `owner` | Everything else |

`origin` keeps the header's `cwd`.

**Active path.**
- Entries form a tree by `parentId`. Only the path from the last leaf back to the root is read, and other branches stay in the archive.
- A `compaction` entry does not shorten what is read: the raw entries before it are still read.
- A `context_edit` stays in the archive.

**Turns.**
- **Bounds and key.** A turn starts at a `message` entry with role `user` and ends before the next one. `turnKey` is that entry's `id`, and the trigger is `typed`.
- **State.** Taken from the last assistant message's `stopReason`:
  - `stop` gives `completed`;
  - `error` gives `failed`, with `errorMessage`;
  - `aborted` gives `cancelled`;
  - `toolUse` gives `interrupted`;
  - any other reason, such as `length`, gives `failed` with that reason as the kind.

**Items.** Assistant `text` parts are text blocks. A `toolCall` is joined with the `toolResult` message whose `toolCallId` matches. `isError` sets `ok` false and `error`, and `details.truncation` sets `truncated`.

**Usage and model.** Usage is the sum of the assistant messages' `usage`: `input`, `cacheRead`, `cacheWrite`, `output` and `reasoning`. Pi's `cost` is a catalogue estimate and is not imported (PI-2). `model` is the turn's first assistant message's `provider/model`, and `effort` its `thinkingLevel`.

**Folder and title.** The working folder is the header's `cwd`. The title is the last `session_info` entry's name, else none.

**Live.** By modification time only.

### Mimo

**Where.**
- `~/.local/share/mimocode/mimocode.db`, together with its `-wal` and `-shm` files, is copied into `~/.arbol/imports/tmp/` and opened read-only there. The copy is removed when the run ends.
- One session is one `session` row whose `parent_id` is null, together with its `message` and `part` rows. Its identity is the session `id`.

The archive takes the session's rows exported as JSON, and its `storage/session_diff/<id>.json`. Never archived: `auth.json`, `mcp-auth.json`, `mimo-key-name`, `installation_id` and `log/`, whose logs hold full prompts outside any session.

**Kind.**
| Kind | Rule |
|---|---|
| `arbol_driver` | Any one of: a title of the form `Arbol run <32 hex>`, `Arbol completed history`, `arbol-source-<hex>:…` or `Cancelled <id>`; a session ID of the form `ses_<26 lowercase hex>`; a part whose metadata holds `arbolCompletedHistory` |
| `probe` | `directory` is under a Claude scratchpad, or an actor is named `probe-*` |
| `owner` | Everything else |

`origin` keeps `directory`, `title_source` and `slug`.

**Turns.**
- **Bounds and key.** A turn is one real user message of the main lane, the main agent's `agent_id`, together with the main-lane assistant messages whose `parentID` names it. `turnKey` is the user message's `id`, and the trigger is `typed`. A main-lane user message with recorded synthetic input and no real user input contributes no prompt or turn. Attach responses to it to the preceding real main turn. If none precedes it, its responses stay in the archive. A real prompt that contains only non-text input still starts a turn ([IMP-D30](00-the-import.md#decisions)).
- **Prompt.** The user message's text parts that are not `synthetic`.
- **State.**
  - `failed` when the last assistant message has an `error`, with its kind;
  - `completed` when its `finish` is `stop`;
  - `interrupted` otherwise.

**Items.**
- `text` parts that are not synthetic are text blocks. `reasoning` and step parts stay in the archive.
- A `tool` part gives one call: `callID`, `tool` and `state.input`.
  - `state.status` `completed` sets `ok` with `output`.
  - `error` sets `ok` false with `error`.
  - `pending` and `running` give an interrupted call.

**Sub-agents.** An actor lane's messages belong to the `actor` tool call whose `state.metadata.actorId` is that lane's `agent_id`. Its calls are nested under that call in the launch turn, with `agent` set to the actor ID. If there is no proven launch link, use IMP-0's fallback in the main turn containing the actor's first record. Keep the actor's work in the archive if no turn owns it. Each assistant message's tokens are counted once, in the lane that holds it ([IMP-D31](00-the-import.md#decisions)).

**Usage, model and folder.** Usage is the sum of the assistant messages' `tokens`: `input`, `cache.read`, `cache.write`, `output` and `reasoning`. `model` is the first main-lane assistant message's `providerID/modelID`, when that pair is available ([IMP-D32](00-the-import.md#decisions)). The working folder is `session.directory`, the title `session.title`, and `toolVersion` `session.version`.

**Live.** `time_updated` within the last 10 minutes.

## Requirements

| ID | Arbol must | Origin | Verified by |
|---|---|---|---|
| IMP-1.1 | Give IMP-0 a session, its turns, their sub-agents and its archive files in the form of [What every reader gives IMP-0](#what-every-reader-gives-imp-0), and treat an unrecognised format by IMP-D10 | New; IMP-D10, IMP-D12 | unit |
| IMP-1.2 | Split line files only at `\n` and ignore a last line without one | New; research | unit |
| IMP-1.3 | Classify every session by its tool's kind table, and keep the origin facts it names | New; IMP-D6 | unit; probe |
| IMP-1.4 | Drop each tool's duplicates: Claude by line `uuid` across files read in time order and by `message.id`; Codex by its single sources, skipped compaction and fork prefix; Kimi by ignoring `agent.*` and by fork `uuid`s | New; research | unit; probe |
| IMP-1.5 | Form turns, turn keys, prompts, steers, triggers and states by each tool's rule, ending an unended Codex turn at the next start, and mapping an unnamed ending to `failed` with its kind | New; research | unit; probe |
| IMP-1.6 | Join each tool call with its result by the tool's identifier, read spilled outputs by each tool's rules, and nest sub-agent calls and Codex `exec` work under their parent call | New; IMP-D3 | unit; probe |
| IMP-1.7 | Sum usage by each tool's rule, counting no repeated record twice, and never import Pi's estimated cost | New; research, PI-2 | unit |
| IMP-1.8 | Archive exactly each tool's listed session files, and never its credentials, tokens, device identifiers, configuration, derived caches, logs, unreferenced uploads or files outside its home | New; IMP-D1 | unit; probe |
| IMP-1.9 | Open private copies of Codex's `state_5.sqlite` and Mimo's database read-only, and never open a file for writing in a tool's home | New; IMP-0.2, IMP-D34 | probe |
| IMP-1.10 | Read only Pi's active path, and honour Kimi's `context.undo` and `context.clear` | New; research | unit |
| IMP-1.11 | Identify a session by its native identity, not its path, and report liveness by each tool's rule | New; IMP-0.14, IMP-0.15 | unit |
| IMP-1.12 | Take each title by its tool's rule | New; IMP-0.5 | unit |

## Interface

The reader's output form is in [What every reader gives IMP-0](#what-every-reader-gives-imp-0). It is internal to `arbol import`, and no other program reads it.

## Known problems

- **Claude probe sessions are recognised partly by their first prompt.** That relies on the probe prompts the suites record. A new suite needs its prompts added, or its sessions are imported as `agent_launched`.
- **Codex `exec` work is placed by time.** Its items are nested under the `exec` call whose time span contains them. When two `exec` calls overlap, they stay in the archive.
- **The Codex Driver's real home differs from its specification** ([IMP-0 Known problems](00-the-import.md#known-problems)).
- **Mimo has no owner session today**, so its reader can be qualified only on probe data ([IMP-D5](00-the-import.md#decisions)).

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| IMP-D10 | What does a reader do with a record type or format version it does not know? | Ignore an unknown record type that is not a conversation record (a turn bound, message, loop event, response item or part). Refuse the session with `unknown_format` when a conversation record has an unknown shape | Decided 18 November 2026 by the owner: the proposed default |
| IMP-D11 | Are Codex's harness user messages (AGENTS.md, environment, heartbeat text) ever shown in the chat? | No. Only `user.text` messages are prompts, except as the prompt of a turn that has none; the others stay in the archive | Decided 18 November 2026 by the owner: the proposed default |
| IMP-D12 | What must the reader form hold for segments, the sub-agent fallback and exported rows? Found while planning SIM-4 | Usage per model response with its start, a time on each text block, one record per sub-agent with its usage kept apart from the turn's, and the database file's modification time for exported rows | Decided 18 November 2026 by the owner: the proposed default |
