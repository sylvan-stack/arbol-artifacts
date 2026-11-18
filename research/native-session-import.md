---
role: authored
---
# Importing native harness sessions into Arbol

Feature research for importing the saved chat sessions of Claude Code, Codex, Kimi Code, Pi and Mimo into Arbol. Feature Course stages 2 and 3 ([Feature Course](../../mycel/operations/feature-course.md)), 17 November 2026. Repository `arbol` at `9496503`, with the Driver repositories and the native homes on the owner's Mac. Depth: standard. Counts were measured read-only on 17 November 2026. Several sessions were still being written while they were counted, so a few counts vary slightly. This document records structure only. It quotes no conversation content, credential or account identifier.

## The owner's idea and decisions so far

The owner does not use Arbol for daily work yet, while it is in active development. The sessions they had with the vendor tools are worth keeping as training material, and the owner wants them in Arbol. On 17 November 2026 the owner chose three things:

| Question | Owner's choice |
|---|---|
| How complete must an imported chat be? | Fill the normal chat tables, so the chats open in Elma. Also keep each native session as a compressed raw archive linked to its chat, so nothing is lost |
| Where do the imported chats go? | Into the installed single Arbol database ([ARC-4](../architecture/04-single-database.md)), marked with their source tool |
| How is the work run? | As a new Saga: specification, then Arcs and Beats |
| How do sub-agent traces appear? | Nested in the parent Exchange as tool calls through `parent_call_id`, like a live Arbol chat's sub-agent work. The full trace stays in the raw archive |
| Can an imported chat be continued? | No. Imported chats are read-only and archived on import, so Elma's list stays clean and no Driver rebuilds another tool's history |
| Is Mimo built now? | Yes. Write it from the format the tool defines and qualify it on probe data, so it is ready when the owner uses Mimo |
| Which sessions not made by the owner are imported? | No preference given. Proposed default for Spec Writing: import every session, including the Kimi `*-test` workspaces, Codex heartbeats and agent-launched runs, and record each one's native origin so a training extraction can filter it. Exclude only sessions an Arbol Driver created, which duplicate Arbol's own chats, and probe or conformance runs, which hold no real work |

Nothing exists today that imports native sessions. ARC-4's clean start chose to have no history importer ([Arbol with one database](arbol-single-database.md#database-migration-and-recovery)). Each Driver's inference specification maps formats in the other direction: from Arbol's history into a rebuilt native session. Each also maps the tool's live output into Driver events. Those mappings are the nearest existing evidence for the field correspondences below.

## What the target tables require

The chat tables were designed for live Exchanges written by a Trunk. Several constraints matter for imported content:

| Constraint | Evidence | Consequence for import |
|---|---|---|
| `exchanges.trunk` matches `^[a-z][a-z0-9]{0,31}$` and `build` is a hex Build number, both `NOT NULL` | `arbol:database/001-baseline.sql` lines 17–18 | An imported Exchange has no Trunk or Build. The specification must choose a marker value or a provenance column (see open questions) |
| `exchanges.route` is a non-null JSON object, `working_folder` an absolute path | lines 19, 21 | Every tool records a working folder. The route can be built from the native provider and model |
| `state` is one of five values, and `ended_at` is null exactly when the Exchange is open | lines 15, 26 | Imported turns map to completed, failed, cancelled or interrupted, never open |
| `messages` position 0 is the user's message and every other position is the assistant's | line 38 | Every imported Exchange needs a user prompt at position 0. Turns that a tool started itself (heartbeats, task notifications, sub-agent triggers) need a rule |
| `messages` and `tool_calls` share one position sequence per Exchange; `tool_calls.position >= 1` | lines 34, 43 and [RCT-3](../../arbol-root/contract/03-the-chat-tables.md#how-lines-become-rows) | Assistant text blocks and tool calls interleave in native order |
| `tool_calls.parent_call_id` exists for a sub-agent's calls | line 46 | Sub-agent traces can be nested under the calling tool call without a schema change |
| `runs` has one row per Driver run, `usage` a JSON object | lines 59–69 | Native usage is per model response, so the importer sums it per turn |
| PostgreSQL rejects U+0000 and lone surrogates; RCT-3 replaces them with U+FFFD | [RCT-3](../../arbol-root/contract/03-the-chat-tables.md#how-lines-become-rows) | Seven Claude Code files contain `\u0000`. The raw archive keeps the original bytes |
| Schema changes go only through the migration ledger, under a fenced maintenance window | `arbol:database/migrations.toml`; `arbol:database/README.md` "Database recovery before reopening" | Any new provenance column is revision 3, applied with the full drain/fence procedure |
| Every writer passes installation writer admission | `arbol:src/arbol_installation/admission.py` lines 146–165 | The importer is a writer. It refuses during maintenance like any other |

<!-- sources:
arbol:database/001-baseline.sql
arbol:database/migrations.toml
arbol:src/arbol_installation/admission.py#Admission.permit
arbol-root:contract/03-the-chat-tables.md#How lines become rows
-->

## Claude Code

**Store.** `~/.claude/projects/<folder>/<session>.jsonl`: 262 top-level sessions (636 MB). The per-session folder `<session>/` holds:
- `subagents/agent-<id>.jsonl` (159 files) with `.meta.json` and `.prefix.json`;
- workflow agents under `subagents/workflows/wf_<id>/` (206 files) with `journal.jsonl`;
- large tool outputs and screenshots in `tool-results/` (394 files), which the lines refer to;
- `custom-title.json`.

File backups live in `~/.claude/file-history/`. Versions seen: 2.1.280 to 2.1.325.

**Threading.**
- Every assistant line carries exactly one content block. One API response spans several lines with the same `message.id`, up to 38 of them.
- `parentUuid` forms a tree. Its 1,125 fork points are all parallel tool calls, not edits.
- A compaction writes a `compact_boundary` line with `parentUuid: null` and `logicalParentUuid`. The earlier lines stay in the file.
- Sub-agents live in their own files, with `isSidechain: true` on every line. The link runs from the parent's `Agent` tool-use ID, through `meta.json.toolUseId`, to `toolUseResult.agentId` (148 of 148 checked).

**Exchange boundary.**
- A turn starts at a user line with no tool result, no `isMeta` and no `isCompactSummary`. `turnOrigin` tells a human prompt (862) apart from sdk (491), task notification (311), peer (63) and host-synthetic (32) prompts.
- Prompts typed while a turn runs arrive as `queued_command` attachments.
- The tool-result lines of a turn keep its `promptId`.

**Usage.** Usage is on every assistant line and is identical for all lines of one `message.id`, so the importer counts it once per message. The saved values are real, unlike the stream's placeholders.

**Duplication.** When a session continues in a new file, the earlier lines are copied with the same `uuid`. 1,824 uuids occur in two files. The importer deduplicates by `uuid`.

**Sessions Arbol started.**
- No file contains `synthetic-arbol` lines. The Driver's map under `~/Library/Application Support/Arbol/drivers/claude/subscriptions/anthropic/chats/` names 9 sessions; 8 are in `~/.claude/projects`.
- 114 `sdk-cli` sessions sit in `-private-tmp-*` folders: probe, scratchpad and conformance runs.
- The desktop app writes `bridge-session` lines; `sdk-cli` sessions never have them.

**Edge cases.**
- Empty files and sessions without an assistant line.
- 43 API-error assistant lines.
- 341 base64 images (24 MB), almost all inside tool results.
- 79 files with more than one `cwd`; `relocated` lines record each change.

<!-- sources:
arbol-claude-driver:src/arbol_claude_driver/history.py
arbol-claude-driver:specs/02-inference.md#Building a session from a history
arbol-claude-driver:specs/02-inference.md#From records to events
-->

## Codex

**Store.**
- 980 rollouts in `~/.codex/sessions/YYYY/MM/DD/`, about 15 GB decompressed. 547 are `.jsonl.zst` and 423 plain `.jsonl`.
- 10 more rollouts in `archived_sessions/`.
- `state_5.sqlite` table `threads` (976 rows) holds titles, the originator, the source and archival. Its `rollout_path` always ends in `.jsonl`, even where only the `.zst` file exists.
- `thread_spawn_edges` records sub-agent parentage.
- `thread_history_1.sqlite` (3.1 GB) is a derived projection of the rollouts, and `session_index.jsonl` holds thread names.

Every line is `{timestamp, ordinal, type, payload}`, and line 1 is `session_meta`. `session_meta.cli_version` shows 14 versions, from 0.155.0-alpha.16 to 0.167.1.

**Exchange boundary.** One turn runs from `event_msg/task_started` to `task_complete` or `turn_aborted`, keyed by `turn_id`, which every response item carries. 421 started turns have no end, and 511 turns are automation heartbeats.

**Duplication.** The importer must pick one source for each fact:
- **Assistant text:** both `response_item/message` and `item_completed:AgentMessage`.
- **Reasoning:** both `response_item/reasoning` and `item_completed:Reasoning`.
- **Usage:** both `token_usage_record` and `token_count`.
- **User prompts:** only user messages whose `content_item_kinds` is `["user.text"]` are typed prompts. The other user-role messages are harness context (AGENTS.md, environment, heartbeats).
- **Compaction:** `compacted` lines carry a `replacement_history` that re-lists earlier history. Do not import it.

**Sub-agents.**
- 595 rollouts are sub-agent threads (`source.subagent.thread_spawn`), nested up to depth 3.
- 357 of them are forks. Every line before `subagent_history_start_ordinal` copies the parent's history and must be skipped.
- Sub-agent messaging dominates the tool calls: `collaboration::send_message` (30,194) and `wait_agent`.

**Tool calls.**
- Most calls are code-mode `exec` custom tool calls (111,317). The 136k command executions, 20k MCP calls and 8.7k file changes they run appear as `item_completed` items with no call link. They can only become child tool calls of the enclosing `exec`, or stay in the archive.

**Reasoning.** All of it is encrypted (`encrypted_content`); only about 17k summaries are readable.

**Images.** Inline `data:` URLs, up to 3.7 MB each. The largest line is 20.2 MB.

**Sessions not made by the owner.**
- `~/.codex` holds no rollout with originator `arbol-codex-driver`. Arbol's 33 Codex rollouts live in Arbol's private homes under `~/Library/Application Support/Arbol/drivers/…/home/sessions`.
- `codex_exec` (88) are mostly runs launched by Claude Code in `/private/tmp`.
- There are also `agent_created_thread` (57) threads and two probe threads, with agent roles `probe_plain` and `probe_clean`. Probes in Arbol's homes use originator `hook-probe`.
- Originators: Codex Desktop 866, codex_exec 88, codex_work_desktop 22, codex-tui 4.

**Finding: the specification and the installation disagree.** [Codex Driver 02](../../arbol-codex-driver/specs/02-inference.md#one-process-per-run) and DRV-0.4 say the Driver runs the tool with its default home. The installed Driver's threads and chat map are in a private home. Bring this to the Codex Driver specification separately, because it decides whether Arbol's own Codex chats appear in an import of `~/.codex`.

<!-- sources:
arbol-codex-driver:src/arbol_codex_driver/history.py
arbol-codex-driver:specs/02-inference.md#Threads and continuity
arbol-codex-driver:specs/02-inference.md#Building a thread from a history
arbol:driver-contract/00-overview-and-boundary.md
-->

## Kimi Code

**Store.** Kimi Code Desktop 1.3.5, with upgrades from 1.1.3 since 26 October. Each wire starts with a `metadata` record of `protocol_version` 1.5.
- 38 sessions under `~/.kimi-code/sessions/<workspace>/session_<uuid>/`.
- The workspace folder is `wd_<slug>_<sha256(root)[:12]>`, or `wm_<uuid>` for a workspace managed through the API.

The canonical record is `agents/<agent>/wire.jsonl`, an append-only journal per agent (1.44 GB in total). Beside it:
- `blobs/<sha256>` holds image bytes, referenced as `blobref:`.
- `tool-results/` holds outputs over 50k characters.
- `file-history/` holds file snapshots for undo.
- There are also background `tasks/` and `plans/`.

The session also has `media/`, `media-originals/` and `state.json`, which gives the title, cwd, archival and `forkedFrom`. The `.wal`, `.index` and `.postings` files belong to rebuildable search and query caches.

**What is conversation.** The conversation records are `context.append_message` (prompts and injections) and `context.append_loop_event`. Loop events are `step.begin`, `content.part` (text or think), `tool.call`, `tool.result` and `step.end`. Kimi Code's bundled source describes them this way to its own model.
- Of 2,147 user-role messages, only 305 have `origin.kind = user`. The rest are injections, mainly todo reminders.
- Thinking is stored in plain text.
- Versions before 1.3.5 also wrote a legacy `agent.*` stream until 12 November, which holds 1.30 GB of inline base64 images. Read only `context.*` and `turn.*` records.

**Exchange boundary.**
- One `turn.prompt` through the matching `turn.ended`. `turnId` is an integer in prompts and a string in loop events.
- `turn.steer` adds input in the middle of a turn.
- Sub-agents have their own `agents/agent-0/wire.jsonl`, linked by `subagent.spawned.parentToolCallId`.
- `context.apply_compaction` marks a boundary, and the earlier records stay. `context.undo` and `context.clear` are defined but unused here, and the importer must still honour them.

**Usage and model.** Usage is per model call, in `step.end.usage`. The model comes from `llm.request`; do not take it from the legacy stream.

**Space.**
| Item | Size | Treatment |
|---|---|---|
| `files/` | 1.76 GB | Mostly one unreferenced video; archive only the referenced items |
| `server/events/` | 1.38 GB | A UI journal that duplicates tool output; skip |
| `blobs` | 0.97 GB | Archive |
| `media` | 0.69 GB | Archive |

Never archive `credentials/`, `oauth/`, `server.token`, `device_id` or `config.toml*`.

**Sessions not made by the owner.**
- 5 identical one-turn probe sessions and one session that looks like hook testing.
- The two `*-test` workspaces on `/Volumes/Mercury` look like substantive multi-day work despite their names.

**Edge cases.**
- U+2028 occurs inside lines, so split only on `\n`.
- `ms://` media references point to remote Moonshot videos with no local file.
- 182 file-history keys have no snapshot file.
- A session lock marks a live session.

<!-- sources:
arbol:src/arbol_agents/kimi_config.py
-->

## Pi

**Store.** `~/.pi/agent/sessions/--<cwd>--/<timestamp>_<id>.jsonl`: 6 sessions, 2.2 MB, session format version 3 (Pi 1.1.0). The rest of `~/.pi/agent` is installed releases.

**Format.**
- Line 1 is the session header. Every other entry has `{type, id, parentId, timestamp}`, forming a tree; the active path runs from the leaf back to the root.
- The source declares compaction, branch summaries and context edits. Only one `context_edit` occurs.
- Assistant messages carry `provider`, `model`, `thinkingLevel` and usage. Pi's `cost` is a catalogue estimate, not a billed amount (PI-2 "Usage and outcomes").

**Sessions Arbol started.** The Pi Driver marks them with a first entry of `customType: "arbol-history-import"`, a UUIDv4 identifier and `import_` call identifiers. None of the 6 sessions has these markers.

<!-- sources:
arbol-pi-driver:src/arbol_pi_driver/native/history.mjs
arbol-pi-driver:specs/inference-and-history.md#Native history construction
-->

## Mimo

**Store.** `~/.local/share/mimocode/mimocode.db` (SQLite in WAL mode; build `0.1.16-arbol4`), in an opencode-like `session`/`message`/`part` layout. Part types include text, reasoning, step-start and step-finish, and tool. A sub-agent is an actor inside the same session, linked by `state.metadata.actorId`.

**Sessions.** There are two, and both are probe runs. Arbol's own imports, titled "Arbol completed history" with slug `arbol-completed-history`, were deleted afterwards. **There is no session of the owner's to import today.** A Mimo importer can only be written from the format the tool defines and qualified on probe data.

<!-- sources:
arbol-mimo-driver:specs/02-inference.md
arbol-mimo-driver:specs/00-overview-and-boundary.md
arbol:research/mimo-upstream-2026-10-27.md#M16 Native history import
-->

## Shared design findings

- **The same pipeline fits every tool.**
  1. Read a session and drop the tool's duplicate records.
  2. Select one active path through the session.
  3. Split it into turns.
  4. Map each turn to one Exchange: the prompt at position 0, then assistant text blocks and tool calls in native order, with a sub-agent's calls nested through `parent_call_id`.
  5. Sum usage per turn into one `runs` row.

  Everything else goes only to the raw archive: thinking, injections, system prompts, compaction summaries, file history and permission changes.
- **Each tool needs a per-tool adapter to Arbol's normal tool names.** Each Driver already maps its tool's shell call to Arbol's `shell` (DRV-3.19); the importer can reuse those mappings.
- **Turns without a typed prompt are common.** Examples are Claude task notifications, Codex heartbeats and Kimi system triggers. Position 0 must hold something, so either the trigger text is stored as the user message or such turns are folded into the previous Exchange.
- **The raw archive must be the session's whole folder, not only its main file.** Claude's `tool-results/` and sub-agent files, and Kimi's blobs and media, hold content the main file only refers to. For Codex it is the rollout plus the session's rows from `state_5.sqlite`. For Mimo it is the session's database rows exported as JSON.
- **Size.** Raw input is roughly 1 GB for Claude, 15 GB decompressed for Codex, 4 GB of useful Kimi data, and a few MB for Pi and Mimo. Images dominate the Claude and Kimi data and compress poorly. That argues for a content-addressed archive of files referenced from the database, rather than byte columns. On 17 November 2026 the owner placed it on the external drive Mercury, outside `~/Library/Application Support` ([IMP-D9](../session-import/00-the-import.md#decisions)).
- **Many sessions are still being written.** The importer must tolerate a partial last line, and a second import must add a live session's new turns without duplicating rows. Native IDs give a stable key: the session ID with `uuid`, `turn_id` or `turnId`.
- **Sessions not made by the owner occur in every store.** Each tool marks them differently, as listed above: originator, entrypoint, `/private/tmp` folders, Driver map entries, synthetic markers and probe shapes. Recognising them is per tool, and which of them to import is the owner's choice.
- **The content is sensitive.** Tool outputs may contain secrets the agent read. The importer copies content verbatim into the local database and archive, as Arbol does for live chats. Any redaction belongs to a later export for training.

## Questions for Spec Writing

Questions 3, 4 and 7 were answered on 17 November 2026 (see the table at the top). Question 1 has a proposed default there. The rest remain for Spec Writing.

1. **Which sessions to import.** Proposed default above. Confirm it when the specification is reviewed.
2. **How an imported Exchange is marked.** A new provenance column (tool, native session ID, tool version, archive reference) added by migration revision 3, with `trunk`/`build` set to a reserved marker? Or relax those checks for imported rows?
3. **Sub-agents.** Nest them as tool calls through `parent_call_id`, as live Arbol chats already do? Or import them as their own chats linked to the parent?
4. **Continuing an imported chat.** Can an imported chat take a new message in Arbol? If so, a Driver rebuilds its history, possibly from another tool's tool names. Or should imported chats be read-only, or archived on import so Elma's list stays clean?
5. **Re-import.** Add only the new turns of a session imported before, or keep the first import fixed?
6. **The archive.** Where and in what format: a content-addressed store in the installation's private directory, per-session zstd, with exclusions such as Kimi's unreferenced uploads and UI journal?
7. **Mimo.** Build its importer now from the format alone, or wait until real sessions exist?
8. **Thinking in the tables.** The owner chose raw archive plus tables, which keeps thinking out of the tables. Confirm that training extraction will read thinking from the archive, given that Codex reasoning is encrypted anyway.
