---
role: authored
spec: IMP-0
status: accepted
---
# Session Import · 00 The import

## Purpose

The owner has worked for months in Claude Code, Codex, Kimi Code, Pi and Mimo, before Arbol is ready for daily use. Those tools keep every conversation in their own formats in their own homes. This specification makes them Arbol chats. They become readable in Elma beside new chats and are kept in Arbol's database as training material, while each native session is kept whole in a raw archive. The evidence for every format and constraint is in [Importing native harness sessions](../research/native-session-import.md). The owner accepted this specification on 18 November 2026.

## Scope

Covered:
- the command that imports, and which sessions it imports;
- how a native session becomes a chat, its Exchanges and their rows;
- images, large results and sub-agents;
- the provenance of an imported chat, and the raw archive;
- importing the same session again;
- imported chats being read-only and archived, with the changes this needs in the backend, the Bridge and Elma;
- the schema change;
- admission, maintenance and failures.

How each tool's records are read, deduplicated and split into turns is in [IMP-1](01-reading-each-tool.md).

Not covered:
- **Extracting training data from the database or archive.** A later specification covers it, including any redaction of secrets.
- **Exporting Arbol chats to a native format.** Each Driver's rebuilt-history rule already covers that ([DRV-2](../driver-contract/02-inference.md)).
- **Continuing an imported chat** ([IMP-D4](#decisions)).

It follows the conventions of the [Driver Contract](../driver-contract/README.md#conventions) with the additional checks of the [Architecture](../architecture/README.md#conventions). Version 1 had no import, so every requirement's Origin is New, followed by the decision or finding it rests on.

## Behaviour

### The command

`arbol import` is a subcommand of Arbol's command line ([ARC-0](../architecture/00-components-and-boundaries.md)). It runs without a running backend.

```sh
arbol import <tool> [--session <native id>]... [--dry-run] [--include arbol_driver|probe]...
```

- `<tool>` is one of `claude-code`, `codex`, `kimi-code`, `pi` and `mimo`.
- Without `--session`, it considers every session in the tool's home.
- `--dry-run` reads and maps everything. It writes nothing to the installed database, the raw archive or the tool's home. A private SQLite copy may exist in the importer's work folder for the reading pass, and is removed afterwards. The command predicts the same session outcomes and row counts as a real import from the same inputs. Its archive bytes written are zero, and it does not allocate IDs for new chats ([IMP-D34, IMP-D35](#decisions)).
- `--include` adds a kind of session the default leaves out ([Which sessions](#which-sessions)).

The command prints one JSON report on standard output. The exit status is 0 when no session failed and 1 otherwise.

**The tool's home is only read.** An importer never writes to a tool's home: it reads files and opens databases there read-only. It reads Mimo's SQLite database and Codex's state catalogue from private copies taken under the rules for [Mimo](01-reading-each-tool.md#mimo) and [Codex](01-reading-each-tool.md#codex).

**Outcomes.** Every session considered gets one outcome:

| Outcome | When |
|---|---|
| `imported` | A new chat was written |
| `extended` | New turns were added to an imported chat |
| `rearchived` | Its files changed, but no turn was added. Only a new manifest was recorded |
| `unchanged` | Nothing changed since its last import |
| `deferred` | Every turn not yet imported is still live ([Importing a session again](#importing-a-session-again)). It is tried at the next run |
| `empty` | It has no turn. No chat is written |
| `excluded` | Its kind is not imported |
| `failed` | It could not be mapped or written. The cause is reported |

Example report (fictional values):

```json
{"tool":"codex","sessions":[
 {"native":"019a…c3","kind":"owner","outcome":"imported","chat":"5f0e…a1","exchanges":12,"messages":31,"toolCalls":88,"subagentFallbacks":0},
 {"native":"019a…d0","kind":"agent_launched","outcome":"deferred"},
 {"native":"019a…e7","kind":"arbol_driver","outcome":"excluded"},
 {"native":"019a…f2","kind":"owner","outcome":"failed","error":{"code":"unknown_format","message":"Line 4812 has a conversation record of an unknown shape."}}],
 "archiveBytesWritten":48210331}
```

**Error messages never quote a session's content.** A message names a line number, a record type or a file path within the tool's home, and nothing else.

### Which sessions

IMP-1 gives every top-level native session exactly one **kind**, by the rules for its tool:

| Kind | What it is | Default |
|---|---|---|
| `owner` | A session the owner ran in the tool | imported |
| `agent_launched` | A session another agent started in that tool, such as a Codex run that Claude Code launched, an agent-created thread or a Claude `sdk-cli` session in a scratch folder | imported |
| `scheduled` | A session started on a schedule, such as Codex automation heartbeats | imported |
| `arbol_driver` | A session an Arbol Driver created. Its content is already an Arbol chat, or was one before the clean start | excluded |
| `probe` | A probe, conformance or hook-test run, which holds no real work | excluded |

A sub-agent's session belongs to its parent session and has no kind of its own.

`--include` imports an excluded kind. This default is the proposal of [IMP-D6](#decisions), which the owner has not yet confirmed. The kind is recorded with every imported chat, so a training extraction can filter by it.

### From a session to a chat

One top-level session becomes one chat. Each of its turns, as IMP-1 forms them, becomes one Exchange.

**The chat.**
- **`chats.title`** is the session's native title by IMP-1's rule. Unicode whitespace is trimmed and the title is cut to 240 characters. An empty title stores NULL, as `chat.rename` does.
- **`chats.created_at`** is the time of the session's first record.
- **`chat_marks`** gets `archived_at` and `updated_at` set to the import time, and `ongoing` false ([IMP-D4](#decisions)).

**Each Exchange.**
| Column | Value |
|---|---|
| `number` | From 1, in the order of the turns |
| `accepted_at` | The turn's start |
| `ended_at` | The turn's end, else the time of its last record |
| `state` | IMP-1's state: `completed`, `failed`, `cancelled` or `interrupted` |
| `error` | Set exactly when the state is `failed`, as `{"code": "imported_failure", "message": <the tool's error text, cut to 2,000 characters, or "The tool recorded the turn as failed without a message.">, "native": <the tool's error kind, when it has one>}` |
| `trunk`, `build` | `imported` and `0` ([IMP-D7](#decisions)) |
| `route` | `{"driver", "model", "effort"}`, with each field present only when the turn records it. `driver` is the Arbol Driver code name for the tool: `claude`, `codex`, `pi` or `mimo`, and `kimi-code` for Kimi Code, which has no Driver |
| `small_call_route` | NULL |
| `working_folder` | The turn's working folder, else the session's, else the owner's home folder |

**The run.** Each Exchange has exactly one `runs` row:
- `run_id` is `<exchange>.import` and the kind is `agent`.
- `outcome` is the Exchange's state, `error` the Exchange's error, and `ended_at` the Exchange's `ended_at`.
- `usage` holds the turn's summed usage in DRV-2's `RunUsage` form: `model`, `inputTokens` (cached and cache-write input included), `cachedInputTokens`, `outputTokens` and, where the tool records them, `reasoningTokens` and `cacheWriteTokens`. RCT-3 lets a field the form does not name arrive inside `usage`.
- `costUsd` is set only when the tool records a billed cost.
- `started` is NULL, because no Driver started the run.

**Positions.** Messages and tool calls share one dense position counter per Exchange, as in a live chat ([RCT-3](../../arbol-root/contract/03-the-chat-tables.md#how-lines-become-rows)):
1. Position 0 is the prompt.
2. Each assistant text block and each tool call then takes the next position, in native order.
3. A tool call's children are placed directly after it, depth-first, before the next item of their parent. Children are a sub-agent's calls, or the work a Codex `exec` call ran. Sibling children follow their native order, and calls running in parallel follow the time of their first record.

**Messages.**
- Position 0 holds the turn's prompt, the text the owner typed. A turn the tool started itself holds its trigger text ([IMP-1](01-reading-each-tool.md#what-every-reader-gives-imp-0)). Images are left out ([Images and large results](#images-and-large-results)).
- Each later message is one assistant text block of the turn's main agent.

**Tool calls.**
- **`call_id`** is unique within the Exchange. A main-agent call keeps its native ID. A nested call's ID is prefixed with the native identity of the agent that made it: `<agent>/<native id>`.
- **`name`** is Arbol's name where a Driver already maps that tool. For example, a shell call becomes `shell` with `{"command", "cwd"?}`, as DRV-3.19 does. Every other tool keeps its native name.
- **`input`** is the native input as JSON. Where the native input is a string, it becomes `{"input": <string>}`.
- **`result`** is `{"output": <text>}` plus the structured fields the native result carries, such as an exit code.
- **`ok`** is false when the tool marked the call as an error. `error` then holds the native error text, cut to 2,000 characters.
- **A call with no result** in the session is written with `ok` false, `interrupted` true and `error` "The session ended before the tool call finished."

**What the tables leave out.** These live only in the raw archive, as the tables leave them out for live chats too (RCT-3):
- thinking;
- text the harness injected, such as reminders, AGENTS.md and environment context;
- system prompts and tool lists;
- compaction summaries;
- a sub-agent's own text;
- file snapshots, and permission and mode changes.

**Text values.** Each value is stored exactly, except that U+0000 and a lone surrogate half become U+FFFD in text and inside JSON, as RCT-3 does.

### Input added during a turn

The tools let the owner send another message while the agent is still answering: Claude queued commands, Kimi steers, a second typed Codex message within one turn. In the tool, that is one turn holding two messages from the owner. An Arbol Exchange holds exactly one message from the owner, at position 0 (RCT-3). So the import cuts such a turn in two at the moment the second message arrived ([IMP-D8](#decisions)). Example:

```text
In the tool, one turn:                         In Arbol, two Exchanges:
  you:   "Fix the failing test"                  Exchange 5  you: "Fix the failing test"
  agent: runs the tests, reads a file                        agent's work up to your second message
  you:   "Use the new fixture instead"   ──►                 state completed
  agent: edits the fixture, runs tests           Exchange 6  you: "Use the new fixture instead"
  agent: "Done, all green"                                   agent's work from then on, ending "Done, all green"
```

The specification calls each piece of such a turn a **segment**. A turn without added input is one segment. Each segment becomes one Exchange:
- The first segment's `turnKey` is the turn's key. The n-th added message starts a segment with the key `<turn key>#<n>`, counting from 1.
- Every segment except the last has state `completed`, and its `ended_at` is the time of the message that ends it. The last segment takes the turn's state, end and error.
- Work is assigned by where it started. A tool call belongs to the segment in which it started, a model response's usage to the segment in which the response started, and a text block to the segment in which it was written. For a Codex response without a saved start time, use the usage record's time ([IMP-D22](#decisions)).

### Images and large results

Images stay out of the tables and in the archive, where the tool stored them: inline in a session file, or as a file of their own (Claude `tool-results/`, Kimi `blobs/` and `media/`).
- A prompt's images are left out of its message text.
- A tool result's image parts become `"images": [{"mediaType", "size"}]` in `result`. Each entry records that an image existed and its size in bytes; the image is read from the archive.

A tool result is cut to 200 KiB, whatever its shape, with `truncated` true, as DRV-2.22 cuts a live result. A message's text is never cut. The archive preserves the available native result bytes in full. When a Claude Code spill is missing, the saved preview is already truncated and remains in its raw transcript ([IMP-D36](#decisions)).

### Sub-agents

A sub-agent's work is nested in the parent Exchange, as a live chat keeps it ([IMP-D3](#decisions)).
- **Tool calls.** Every tool call the sub-agent made becomes a `tool_calls` row of that Exchange:
  - `run_id` is `<exchange>.import`;
  - `parent_call_id` is the `call_id` of the call that started the sub-agent;
  - positions follow [Positions](#from-a-session-to-a-chat).
- **Nesting.** A sub-agent's own sub-agents are nested under the calls that started them, at any depth.
- **Usage.** The sub-agent's usage is added to the Exchange's run.
- **Text.** The sub-agent's text and thinking stay in the archive.

**When the starting call cannot be found.** IMP-1 may be unable to find the call that started a sub-agent. The importer then adds a `tool_calls` row to the Exchange in which the sub-agent's first record falls, at the end of that Exchange:
- `name` is `subagent`, `call_id` is `subagent/<native agent id>`, and `run_id` is `<exchange>.import`;
- `input` is `{"agent": <native agent id>}` and `result` is `{"output": ""}`;
- `ok` is false only when the sub-agent's last turn failed.

That row becomes the parent of the sub-agent's calls, and the report counts each such fallback. Reused Codex sub-agents' work stays with its recorded root turn. In that turn, use the same fallback if the original launching call belongs to an earlier turn ([IMP-D23](#decisions)).

Nested calls are hidden in Elma's chat view, as a live sub-agent's are. Elma reads only calls without `parent_call_id`.

### Provenance

Migration revision 3 adds two tables and one trigger. The later additive import fingerprint migration adds `chat_imports.files_fingerprint` and keeps `compatibility_version` at 1 ([ARC-4](../architecture/04-single-database.md#build-selection-and-release-compatibility)). A Build that only reads the original import fields still requires revision 3. The importer requires the revision containing the fingerprint ([Builds that change](#builds-that-change)).

```sql
CREATE TABLE chat_imports (
  chat_id         uuid        PRIMARY KEY REFERENCES chats (id) ON DELETE RESTRICT,
  tool            text        NOT NULL CHECK (tool IN ('claude-code','codex','kimi-code','pi','mimo')),
  native_id       text        NOT NULL CHECK (octet_length(native_id) BETWEEN 1 AND 256),
  kind            text        NOT NULL CHECK (kind IN ('owner','agent_launched','scheduled','arbol_driver','probe')),
  tool_version    text,
  origin          jsonb       NOT NULL CHECK (jsonb_typeof(origin) = 'object'),
  manifest        text        NOT NULL CHECK (manifest ~ '^[0-9a-f]{64}$'),
  first_imported  timestamptz NOT NULL,
  last_imported   timestamptz NOT NULL,
  UNIQUE (tool, native_id)
);
CREATE TABLE exchange_imports (
  exchange_id  uuid  PRIMARY KEY REFERENCES exchanges (id) ON DELETE RESTRICT,
  chat_id      uuid  NOT NULL REFERENCES chat_imports (chat_id) ON DELETE RESTRICT,
  turn_key     text  NOT NULL CHECK (octet_length(turn_key) BETWEEN 1 AND 512),
  trigger      text  NOT NULL CHECK (trigger IN ('typed','steered','task','scheduled','system')),
  UNIQUE (chat_id, turn_key)
);
```

- `origin` keeps the native facts IMP-1 names for the tool, such as the originator, entrypoint, source or workspace, for a later filter.
- `trigger` says what started the Exchange: typed by the owner, steered in during a turn, a task notification, a schedule, or the tool itself.
- `turn_key` is the Exchange's native identity from IMP-1 and [Input added during a turn](#input-added-during-a-turn).
- `manifest` names the session's current archive manifest.
- `files_fingerprint` is the SHA-256 of the compact JSON array of `[relative path, lowercase content SHA-256]` pairs, sorted by path. Use UTF-8 JSON with non-ASCII characters escaped. Compute the content digest from the exact bytes the manifest describes before archive compression. The fingerprint excludes modification and import times. A move changes the manifest path and fingerprint while preserving the chat's identity ([IMP-D35](#decisions)).

The additive migration preserves earlier provenance rows with an absent fingerprint. The database requires a 64-character lowercase hexadecimal fingerprint on new or updated provenance rows. A real import can fill an absent fingerprint from the saved manifest after verifying its digest and session identity on Mercury. It records this repair in the session transaction. When the session is otherwise unchanged, the repair keeps the manifest and import timestamps. A dry run reports a row failure for a legacy session whose outcome requires an absent fingerprint, with a fixed message to run a real import with Mercury mounted. The first importer release creates new provenance with a fingerprint.

**Writers.** The importer is the only writer of both tables. It is also a named exception to the single writers of the chat tables (ARC-D10, RCT-3), next to the chat title:
- it writes `chats`, `exchanges`, `messages`, `tool_calls` and `runs` only for the chats it creates;
- it writes `chat_marks` only once, when it creates the chat.

### The raw archive

The archive keeps every file of a native session, so that nothing the tables leave out is lost ([IMP-D1](#decisions)). Nothing of the import lives under `~/Library/Application Support`. The owner wants to find these files and check them without digging there ([IMP-D9](#decisions)). The import uses two places:

```text
/Volumes/Mercury/Arbol/imports/        the raw archive, on the external drive Mercury
  objects/ab/cdef…                     one native file's bytes, zstd-compressed, named by the sha256 of the uncompressed bytes
  manifests/12/34ab….json              one manifest, named by the sha256 of its own bytes
~/.arbol/imports/                      the importer's own working files, beside Arbol's settings (ARC-5)
  import.lock                          held while an import runs
  tmp/                                 private Mimo database and Codex catalogue copies during a run, removed afterwards
```

Folders are created with mode 0700 and files with 0600. Mercury is FileVault-encrypted APFS with ownership disabled, so those modes protect nothing on Mercury itself. The drive's encryption protects the archive at rest.

**When Mercury is not mounted.** A real import refuses with `archive_unavailable` before it reads a session, because no session may be committed before its objects are on the drive. A dry run runs without Mercury and compares current files with the saved PostgreSQL fingerprint. The chat tables never depend on the archive: imported chats open in Elma whether Mercury is mounted or not.

A manifest is a JSON object:
- `{"tool", "nativeId", "takenAt", "toolVersion", "files": [...]}`;
- each entry of `files` is `{"path", "sha256", "size", "mtime"}`, where `path` is relative to the tool's home;
- for exported database rows, `path` names the database and the session, such as `state_5.sqlite#<thread id>.json`.

IMP-1 lists, for each tool, which files belong to a session and which are never archived. Credentials, sign-in tokens, device identifiers, tool configuration and derived caches are never archived, and neither is any file outside the tool's home.

**Objects and manifests are never changed or deleted.** The same bytes in two sessions, or in two imports of one session, are stored once. Objects, manifests and their folders are written and synced to disk before the database transaction that names the manifest commits. A crash can therefore leave unnamed objects behind, but never a manifest that points at a missing object.

### Importing a session again

Running the import again is safe. A session already in `chat_imports`:
- with eligible turns whose turn keys are not yet imported is `extended`. Those turns become Exchanges numbered after the last one;
- with only a live withheld turn left to import is `deferred`;
- with no turn left to import and matching fingerprints is `unchanged`;
- with no turn left to import and differing fingerprints is `rearchived`.

An `extended` or `rearchived` session records a new manifest and updates `manifest`, `files_fingerprint` and `last_imported` together in its transaction. When an import publishes a manifest, the written fingerprint comes from that same manifest's file inventory.

**Earlier turns are fixed.** An imported turn is never rewritten. A turn whose native records changed after its import keeps its imported rows. Its new bytes are kept only in the new manifest. A file the tool moved, such as a Codex rollout moved to `archived_sessions/`, is matched to its session by IMP-1's identity rule, not by its path.

**Live sessions.** A session is **live** when one of its files changed in the last 10 minutes, or when IMP-1 names a lock for the tool and the lock is held.
- A live session's last turn is not imported, even when it looks finished. It is tried at the next run.
- In a session that is not live, an unfinished turn is imported with state `interrupted`.

### Imported chats are read-only and archived

An imported chat is archived when it is created and never takes a new message ([IMP-D4](#decisions)).

**The backend refuses first.** On `chat.send` and every other path that would start an Exchange, the backend refuses a chat that has a `chat_imports` row with the code `imported_chat` before starting anything. It never creates a Draft for such a chat.

**The database refuses as a safety net.** A trigger refuses an `INSERT` into `exchanges` for a chat in `chat_imports` with SQLSTATE `P0001` and the message `imported_chat`. The importer sets `SET LOCAL arbol.importing = 'on'` in its own transactions, and the trigger lets those through. A Trunk Build that does not yet know the code reports this refusal as its database failure, `database_unavailable` (RCT-2). That can happen only when the backend's check was bypassed.

**What the Bridge and Elma show.**
- The Bridge gives each chat of the chat list and each chat snapshot an `imported` field: `{"tool", "kind"}` for an imported chat, and absent otherwise.
- Elma's Archived chats list uses an opt-in archived-only `chats.page` request. The existing Latest chats page and subscription still start with active chats. An archived page uses the same ordering, cursor and limit as the active page. Its summaries carry `archived: true` and carry the import metadata when applicable ([IMP-D33](#decisions), [BKD-1](../backend/01-the-bridge.md#interface)).
- Elma shows an imported chat like any archived chat, names the tool it came from, and shows no composer for it.
- The owner can unarchive an imported chat, but it stays read-only.

This amends the backend's table description that "nothing archives or deletes a chat by itself" ([BKD-0](../backend/00-the-arbol-backend.md)): the import archives the chats it creates.

### Builds that change

| Build | Change | Schema declaration |
|---|---|---|
| `arbol` | The `arbol import` command, fingerprint migration, backend refusal and import provenance reads | `minRevision` is the fingerprint migration revision |
| Elma's renderer, with the shared design system | Show the tool of an imported chat and hide its composer | Follows `arbol` through the Bridge |
| Trivial Trunk | No change is required. A later Build may report the trigger's refusal as `imported_chat` | unchanged |

Each Build declares the minimum revision it actually needs ([IMP-D14, IMP-D35](#decisions)). The first importer Build requires the fingerprint migration. Builds that already read import provenance keep their earlier declaration and still read the original fields after the additive migration.

BLD-0 reserves the Trunk code name `imported`, and no Trunk Build may take it. A reader that meets `trunk = 'imported'` treats the Exchange as imported: it accepts the Trunk `imported` with Build `0`, never resolves it to a Trunk Build, and takes the import's facts from `chat_imports` ([IMP-D15](#decisions)). Build `0` otherwise means a program outside a Build ([BLD-0](../builds/00-builds-and-versions.md)).

### Admission, maintenance and failures

- **Schema check.** Before reading any session, the importer checks the installed schema pair. It refuses with `incompatible_schema` unless the compatibility version is 1 and the revision includes the import fingerprint migration. That check takes no writer permit.
- **Writer admission.** The importer passes installation writer admission ([ARC-4](../architecture/04-single-database.md#maintenance-and-writer-admission)) once per session, holding the permit only for that session's transaction. When admission is draining or exclusive, it finishes the session in hand, takes no further permit, and ends with `maintenance`. The sessions it did not reach are listed with no outcome.
- **Dry runs.** A dry run takes no writer permit, but reads the database to tell new sessions from imported ones. It refuses with `maintenance` while admission is exclusive.
- **One import at a time.** A second import refuses with `busy`.
- **One transaction per session.** Each session is imported in one transaction. A session that fails to map, or whose rows the database refuses, is rolled back alone and reported as `failed` with the cause, and the import goes on. An interrupted import leaves every committed session complete and every other session absent, and running it again finishes the work.

## Requirements

| ID | Arbol must | Origin | Verified by |
|---|---|---|---|
| IMP-0.1 | Offer `arbol import <tool>` for `claude-code`, `codex`, `kimi-code`, `pi` and `mimo`, with `--session`, `--dry-run` and `--include`, printing one JSON report with one outcome per session and exiting 1 when any session failed | New; IMP-D5 | unit; probe |
| IMP-0.2 | Never write to a tool's home; read Mimo's database and Codex's state catalogue and write-ahead logs from private copies | New; research, IMP-D34 | probe |
| IMP-0.3 | Give every top-level session one kind by IMP-1's rules; import `owner`, `agent_launched` and `scheduled` and exclude `arbol_driver` and `probe` unless `--include` names them | New; IMP-D6 | unit; probe |
| IMP-0.4 | Write one chat per top-level session and one Exchange, with exactly one run, per turn or segment, with the values of [From a session to a chat](#from-a-session-to-a-chat), including a failure error exactly for failed Exchanges and runs | New; IMP-D1, RCT-3 | unit; journey |
| IMP-0.5 | Set the title from IMP-1's rule, trimmed, cut to 240 characters, and NULL when empty | New; BKD-0 `chat.rename` | unit |
| IMP-0.6 | Number messages and tool calls with one dense counter per Exchange, placing children depth-first directly after their parent call | New; RCT-3 | unit |
| IMP-0.7 | Keep thinking, injected text, system prompts, tool lists, compaction summaries, a sub-agent's text and file snapshots out of the tables and in the raw archive | New; IMP-D1 | unit |
| IMP-0.8 | Store a turn's trigger text at position 0 when the tool started the turn, split a turn into segments at input added during it with the keys, states and assignments of [Input added during a turn](#input-added-during-a-turn), and record each Exchange's trigger | New; IMP-D8 | unit |
| IMP-0.9 | Nest a sub-agent's calls in the parent Exchange under the call that started it, at any depth, with Exchange-unique call IDs; otherwise under a `subagent` row; add its usage to the run | New; IMP-D3 | unit; probe |
| IMP-0.10 | Leave images out of messages, describe image parts in results by media type and size, and cut a result to 200 KiB whatever its shape, flagging it | New; DRV-2.22 | unit |
| IMP-0.11 | Add `chat_imports`, `exchange_imports` and the insert trigger as migration revision 3, additive under compatibility version 1, applied by the fenced migration procedure | New; IMP-D7, ARC-4.2 | Migration on a populated disposable database |
| IMP-0.12 | Record each imported chat's tool, native ID, kind, tool version, origin facts and current manifest, and each Exchange's turn key and trigger | New; IMP-D6 | unit |
| IMP-0.13 | Archive every file of an imported session as content-addressed zstd objects and a manifest in `/Volumes/Mercury/Arbol/imports/`, keep the importer's working files in `~/.arbol/imports/`, use nothing under `~/Library/Application Support`, and refuse a real import with `archive_unavailable` when Mercury is not mounted; never archive credentials, tokens, device identifiers, configuration, derived caches or files outside the tool's home; never change or delete an object or manifest; make objects, manifests and folders durable before the transaction naming the manifest | New; IMP-D1, IMP-D9 | unit; drill |
| IMP-0.14 | Import a session again without duplicating rows: report `unchanged`, `extended` or `rearchived`; add only turns with new keys; never rewrite an imported turn; match moved files by session identity | New; research | unit; drill |
| IMP-0.15 | Withhold a live session's last turn, and import an unfinished turn of a session that is not live as `interrupted` | New; research | unit |
| IMP-0.16 | Refuse every new Exchange for an imported chat in the backend with `imported_chat`, and in the database through the insert trigger; create no Draft for it | New; IMP-D4 | contract; journey |
| IMP-0.17 | Archive an imported chat on import; give the Bridge's chat list and snapshot the `imported` field; provide an archived-only chat page for Elma; Elma names the tool and shows no composer | New; IMP-D4, IMP-D33 | journey |
| IMP-0.18 | Reserve the Trunk code name `imported` in BLD-0, and in every reader accept `trunk = 'imported'` with Build `0` as an import, never resolve it to a Trunk Build, and take its facts from `chat_imports` | New; IMP-D7, IMP-D15 | unit |
| IMP-0.19 | Check the installed schema pair and refuse with `incompatible_schema`; take one writer permit per session; stop at draining or exclusive admission with `maintenance`; refuse a dry run under exclusive admission; allow one import at a time; import each session in its own transaction | New; ARC-4.4 | drill |
| IMP-0.20 | Replace U+0000 and lone surrogate halves with U+FFFD in stored text and JSON, leaving the archive byte-exact | New; RCT-3 | unit |
| IMP-0.21 | Never quote session content in an error message or report | New; research | unit |
| IMP-0.22 | Store the file fingerprint with the current archived manifest and use it to compare files on a repeat dry run without Mercury. Keep the prior import schema compatible and use the fenced migration procedure. | New; IMP-D35, IMP-0.14 | unit; drill |

## Interface

- **The command:** `arbol import <tool> [--session <id>]... [--dry-run] [--include arbol_driver|probe]...`.
- **Its report:** `{"tool", "sessions": [{"native", "kind", "outcome", "chat"?, "exchanges"?, "messages"?, "toolCalls"?, "subagentFallbacks"?, "filesNotArchived"?, "error"?}], "archiveBytesWritten"}`. `filesNotArchived` counts the files a session names outside the tool's home, which are never archived.
- **Errors**, as `{"code", "message"}`:
  - `maintenance`, `busy`, `incompatible_schema`, `archive_unavailable` and `database_unavailable` end the command.
  - `unreadable_session`, `unknown_format` and `rows_refused` belong to one session ([IMP-D13](#decisions)):
    - `unreadable_session` when a file of the session cannot be read or decoded: an I/O error, a corrupt compressed stream, a complete line that is not JSON, or a file that disappears while it is read. An initially absent Claude Code spill with a saved preview follows [IMP-D36](#decisions);
    - `unknown_format` when a record parses but a conversation record has an unknown shape (IMP-D10);
    - `rows_refused` when the database refuses the session's rows or a legacy dry run needs a fingerprint that has not been recorded.
  - A session that fails before its native ID is known is reported with the name of its file as `native` and no `kind`.
  - A session that fails after its native ID is known is reported with the kind its tool's table in IMP-1 gives for the records read before the failure ([IMP-D16](#decisions)).
- **Database:** the tables and trigger of [Provenance](#provenance), and the error object of a failed imported Exchange.
- **Bridge:** the `imported` field of a chat, the archived-only page through `chats.page {archived: true}`, and the send refusal `imported_chat`.
- **Archive:** the layout, places and manifest of [The raw archive](#the-raw-archive).

## Known problems

- **Kimi Code has no Arbol Driver**, so `route.driver` is `kimi-code`. A reader that resolves the route's Driver must accept an unknown Driver on an imported Exchange.
- **The archive is on a removable drive.** Mercury is USB-attached, and an import cannot run while it is unplugged. File modes are not enforced there because ownership is disabled; FileVault protects the archive at rest.
- **The archive is not part of the database snapshots ARC-4 takes before a migration.** Restoring an older database leaves archive objects that no row names. They are harmless, but the space is not recovered.
- **Some Codex threads are hidden by the Driver's home.** The Codex Driver specification says it uses the tool's default home, but the installed Driver keeps its threads in a private home ([research](../research/native-session-import.md#codex)). Those threads are not seen by an import of `~/.codex`.
- **A Codex `exec` call's work is nested under it**, so Elma hides those child calls as it hides a sub-agent's. They remain in the database for training.

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| IMP-D1 | How complete must an imported chat be? | Fill the chat tables, and keep every native session whole in a raw archive linked to its chat | Decided 17 November 2026 by the owner: the proposed default |
| IMP-D2 | Where do imported chats go? | The installed single database, marked with their tool | Decided 17 November 2026 by the owner: the proposed default |
| IMP-D3 | How do sub-agent traces appear? | Nested in the parent Exchange through `parent_call_id`, with the full trace in the archive | Decided 17 November 2026 by the owner: the proposed default |
| IMP-D4 | Can an imported chat be continued? | No: read-only, and archived on import | Decided 17 November 2026 by the owner: the proposed default |
| IMP-D5 | Which tools are supported, and is Mimo built while it has no owner sessions? | Claude Code, Codex, Kimi Code, Pi and Mimo, with Mimo built from its defined format and qualified on probe data | Decided 17 November 2026 by the owner: the proposed default |
| IMP-D6 | Which sessions not made by the owner are imported? | Import `agent_launched` and `scheduled` sessions with their kind recorded. Exclude `arbol_driver` and `probe` unless asked | Owner gave no preference on 17 November 2026; accepted with the specification on 18 November 2026: the proposed default |
| IMP-D7 | How is an imported Exchange marked, given that `trunk` and `build` are required? | Additive tables `chat_imports` and `exchange_imports`, plus the reserved Trunk code name `imported` with Build `0` | Decided 18 November 2026 by the owner: the proposed default |
| IMP-D8 | A message the owner sent while the agent was still answering leaves two owner messages in one native turn, but an Exchange holds only one. How is it imported? | Cut the turn in two where the second message arrived. The work before it becomes one Exchange, marked `completed`, and the second message starts the next Exchange | Decided 18 November 2026 by the owner: the proposed default. On 17 November 2026 the owner had asked what a segment is; the section explains it with an example |
| IMP-D9 | Where is the archive kept? | Content-addressed zstd objects and manifests, never deleted | Decided 17 November 2026 by the owner: nothing under `~/Library/Application Support`. The archive goes on the external drive Mercury at `/Volumes/Mercury/Arbol/imports/`, and the importer's own working files go in `~/Arbol/imports/`. Changed later that day by the owner for the whole of Arbol: no `~/Arbol/` folder; the working files go in `~/.arbol/imports/` ([ARC-D83](../architecture/05-where-arbol-keeps-its-files.md#decisions)) |
| IMP-D13 | Which error does a session get when its files are broken, and how is a session reported that fails before its ID is known? Found while planning SIM-4 | `unreadable_session` when a file cannot be read or decoded; `unknown_format` only when a record parses but has an unknown shape; such a session is reported by its file name, with no kind | Decided 18 November 2026 by the owner: the proposed default |
| IMP-D14 | BLD-0's Single-database amendment says database-dependent components declare `minRevision: 3`. Does every Build move to revision 3? Found while planning SIM-1 | No. Each Build declares the revision it needs; only the `arbol` Build with the import declares 3 | Decided 18 November 2026 by the owner: the proposed default |
| IMP-D15 | What does "treat the Exchange as imported" ask of a reader? Found while planning SIM-2 | Accept Trunk `imported` with Build `0`, never resolve it to a Trunk Build, and take the import's facts from `chat_imports` | Decided 18 November 2026 by the owner: the proposed default |
| IMP-D16 | What kind is reported for a session that fails after its native ID is known, when its tool's kind rule depends on records after the failure? Found while planning SIM-24 | The kind its tool's table gives for the records read before the failure, so every session with a known ID is reported with a kind | Decided 19 November 2026 by the owner: the proposed default |
| IMP-D17 | How does the Claude Code reader represent a readable session with no complete record? Found while planning SIM-5 | Report it as `empty`. Use the earliest modification time of its top-level session files as the reader form's internal creation time. An empty session creates no chat. | Decided 19 November 2026 by the owner |
| IMP-D18 | How does the Claude Code reader classify sessions when the supplied Driver chat-map directory or an entry is unreadable or cannot be decoded? Found while planning SIM-5 | Continue with the readable map entries and evidence in the session files. An unavailable portion of the shared map contributes no classification evidence and produces no session failure. | Decided 19 November 2026 by the owner |
| IMP-D19 | How does Codex import when shared metadata is unavailable? Found while planning SIM-6 | Continue with readable state catalogue rows, title index entries, Driver map entries and rollout evidence. Missing, busy, unreadable or unrecognised shared metadata supplies no evidence for the affected portion and causes no session failure. | Decided 19 November 2026 by the owner |
| IMP-D20 | What kind does Codex give a thread with zero validated turn starts when no earlier kind rule matches? Found while planning SIM-6 | Give it `owner`. The `scheduled` rule requires at least one validated root turn start. Use the same condition when classifying the prefix of a failed session. | Decided 19 November 2026 by the owner |
| IMP-D21 | Which of several Codex rollout files with the same native ID supplies the conversation? Found while planning SIM-6 | Prefer the path in the state catalogue, matching with and without `.zst`. When there is no matching copy, prefer the most recently modified one. Project one copy and keep the verified same-ID rollout files in the archive. | Decided 19 November 2026 by the owner |
| IMP-D22 | Which time assigns Codex response usage to a segment when the response start is absent? Found while planning SIM-6 | Use the saved usage record's time for segment assignment when no response start time was saved. | Decided 19 November 2026 by the owner |
| IMP-D23 | Where does a reused Codex sub-agent's work go if a later root turn owns it? Found while planning SIM-6 | Assign it to the later native root turn. In that turn use the existing sub-agent fallback if the launching call belongs to an earlier turn. | Decided 19 November 2026 by the owner |
| IMP-D24 | What if a Kimi Code fork's source cannot be read? | Report `unreadable_session` for the fork alone. Its copied records cannot be distinguished from its new records without a readable source. | Decided 19 November 2026 by the owner |
| IMP-D25 | How is a readable Kimi Code wire with no complete record imported? | Report it as `empty`. Use the session's recorded `state.json.createdAt` as its internal creation time when available, otherwise the main wire's modification time. | Decided 19 November 2026 by the owner |
| IMP-D26 | Which of several loop requests supplies a Kimi Code turn's model and effort? | Use the model and effort together from the last retained `llm.request` of kind `loop` in the turn. | Decided 19 November 2026 by the owner |
| IMP-D27 | What if a Kimi Code image reference has no local evidence of media type and size? | Leave the reference in the raw archive. Emit an image descriptor only when native metadata or an eligible in-home file provides both values. Make no network request. | Decided 19 November 2026 by the owner |
| IMP-D28 | Which Kimi Code prompts count as Forester hook probes? | Use exact prompts from documented Forester hook-installation probes in the one-turn, no-tool-call rule. An unmatched prompt is `owner`. | Decided 19 November 2026 by the owner |
| IMP-D29 | Does the Pi reader read a spilled tool result outside the Pi home? | Keep the saved inline result and its truncation flag and count the named file in `filesNotArchived`. Read spills only from eligible paths resolved inside the supplied Pi home. | Decided 19 November 2026 by the owner |
| IMP-D30 | Do synthetic-only Mimo user messages form turns? | Keep the synthetic prompt in the archive. Attach its subsequent main-lane responses to the preceding real main turn, or keep the continuation archive-only if no real turn precedes it. A real non-text prompt still starts a turn. | Decided 19 November 2026 by the owner |
| IMP-D31 | Which turn owns a Mimo actor's work? | Use the turn of its proven launching call. Without a link, use the existing fallback in the main turn containing the actor's first record. Keep unassignable actor work in the raw archive. | Decided 19 November 2026 by the owner |
| IMP-D32 | Which Mimo response supplies the turn model? | Use the first main-lane assistant's native `providerID/modelID` pair, leaving the model absent if there is no assistant or the pair is unavailable. | Decided 19 November 2026 by the owner |
| IMP-D33 | How does Elma list imported chats while they are archived? | Offer an archived-only mode on `chats.page` through `archived: true` and use it for Elma's Archived chats list. Use the existing sort, cursor and limit. Summaries in this mode carry `archived: true`, with import metadata when present. Omitted or false keeps the existing page. The Latest chats subscription keeps its current scope. | Decided 19 November 2026 by the owner |
| IMP-D34 | May the Codex reader use private scratch to read the live state catalogue? | Take a verified private DB and WAL copy in the importer's work folder, including during dry runs. Open it read-only and remove it and any private sidecars after reading. Original files remain untouched. If a consistent copy cannot be verified, use IMP-D19. | Decided 19 November 2026 by the owner |
| IMP-D35 | How can a repeat dry run report the exact file-change outcome with Mercury unmounted? | Store the fingerprint of the current manifest's relative file paths and content digests in PostgreSQL. Use the same comparison in real and dry runs, and update the fingerprint and manifest together. Add it through an additive migration. | Approved 21 November 2026 by the owner |
| IMP-D36 | What happens when Claude Code saved a tool-result preview and the eligible full output file is missing? | Read the full result when available. If the file is absent when first checked and its transcript contains a saved preview, keep that preview as a truncated tool result and continue importing the Chat Session. Archive the transcript and the available files. A missing file without a saved preview, an unreadable or nonregular file, or an input that changes after it is observed still causes an individual session failure. | Approved 21 November 2026 by the owner |
