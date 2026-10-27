---
role: authored
spec: BKD-0
status: accepted
---
# Arbol backend · 00 The Arbol backend

The *Arbol backend* is the one process of a [Root](../GLOSSARY.md#arbol-root)'s `arbol` [Build](../GLOSSARY.md#build) that serves the [Leather Bag](../GLOSSARY.md#leather-bag)'s windows in that Root. It reads the chats from the Root's database, keeps the [Drafts](../GLOSSARY.md#draft), sends a message by having `arbol-root` start an [Arbol Trunk](../GLOSSARY.md#arbol-trunk) for a new [Chat Exchange](../GLOSSARY.md#chat-exchange) (*Exchange* for short: the message and the agent's answer to it), follows the answer as it arrives in the Exchange's folder, passes on a stop and the Leather Bag's answers to the agent's questions, looks every 30 seconds for an Exchange that is stuck, notices a database that cannot be reached, lists the Leather Bag's Subscriptions through the [Drivers](../GLOSSARY.md#driver), and reports how much space the chats take. For example, when the Leather Bag sends "What does build.sh do?" in First Sapling, the backend writes a request file, runs `arbol-root --root sapling start --exchange 2d4f6a8c-… --request …/2d4f6a8c-….json`, reads the acceptance line, and from then on reads `exchanges/2d4f6a8c-…/events.jsonl` line by line and passes each line to every window that shows the chat. This specification states the process and its socket, the database and the backend's own tables, Drafts, sending and sending again, an Exchange in progress, stopping and answering the agent's questions, settling, stuck Exchanges, restarts and discovery across Roots, a database that cannot be reached, accounts, health and storage, and tests. It matters because in version 1 every window talked to a resident service that also ran the chats, so one failed turn could hold up every chat, a chat whose end could not be recorded showed "running" for ever, and the database filled its disk twice without anyone seeing it coming.

It follows the conventions of the [Driver Contract](../driver-contract/README.md#conventions) and the additions in this chapter's [README](README.md#conventions). It makes exact what [ARC-0](../architecture/00-components-and-boundaries.md#arbol-the-swift-app-and-the-backend) to [ARC-3](../architecture/03-stuck-trunks.md) say of the backend, and is one party of the [Root Contract](../../arbol-root/contract/README.md), version 1: it reads the Exchange folder of [RCT-1](../../arbol-root/contract/01-the-exchange-folder.md) and the chat tables of [RCT-3](../../arbol-root/contract/03-the-chat-tables.md), and writes answers into `control`. The forms are technical choices made on 18 October 2026; the questions only the owner can settle are rows of the Decisions table with a proposed answer.

## Scope

Covered: the process, its socket and its lifetime, other programs it starts, the database and the backend's own tables, Drafts, sending a message and sending it again, an Exchange in progress, stopping and answering the agent's questions, settling, stuck Exchanges, restarts and discovery across Roots, a database that cannot be reached, accounts, the working folder of a chat, health and storage, the program and its Build, tests.

Not covered: what crosses the Bridge, in [BKD-1](01-the-bridge.md); what the window shows, in [BKD-2](02-elma-chat.md); Brain Recipes and the small-call route (SYL-191); the command line `arbol` apart from its command `backend` (SYL-193); the tray menu and how the Swift App starts and ends a backend (SYL-192); listeners such as Telegram ([ARC-D52](../architecture/01-roots.md#decisions)); a message that steers a running agent ([ARC-D54](../architecture/02-chat-exchange-across-components.md#decisions)); the Root-owned stale/reimport SQL and global command implementation (RTM-1; SYL-195). The additive backend binding of that path is described below and implemented in the Backend Arc.

## Behaviour

### The process

The backend is the command `backend` of the program `arbol`, the same program the command line uses ([ARC-0](../architecture/00-components-and-boundaries.md#the-command-line)). The Arbol Swift App starts it through the launcher, naming the Root:

```sh
arbol --root sapling backend
# {"ready":true,"root":"sapling","build":"6","socket":"/Users/sam/Library/Application Support/Arbol/roots/sapling/backend.sock","pid":51207}
```

| | |
|---|---|
| Its Root | The one the `root` of its own Build record names, as with `arbol-root` ([RTM-0](../../arbol-root/specs/00-the-commands.md#the-root-of-a-command)); `--root` only outside a Build, as in development, with the build number `0` (BLD-0). The Root's folder is `~/Library/Application Support/Arbol/roots/<root>/` |
| One for each Root | It takes an exclusive lock on the file `backend.lock` in the Root's folder before anything else. A second backend of the same Root refuses with `already_running`, whose message names the first one's process, and the Swift App connects to the socket of the first |
| Its socket | `backend.sock` in the Root's folder ([ARC-1](../architecture/01-roots.md#a-root-on-disk)), a Unix socket of the mode 0600, which only the owner can open. Once it holds the lock it removes a socket file left by a backend that died, then listens. A path longer than the 103 bytes a macOS socket address can hold is refused with `invalid_input`; for a home folder such as `/Users/sam` it leaves room for a Root identifier of up to 39 letters |
| Ready | Once it listens, it prints one line, the *ready line*, and from then on writes nothing more on standard output. Standard error is for a person only |
| A refusal | One line `{"error":{"code","message"}}` and the exit status 1: `invalid_input`, `unknown_root` for a Root whose folder holds no readable `root.json`, `already_running` |
| Its end | On SIGTERM or SIGINT, and when its standard input is a pipe that reaches its end, which happens when the Swift App that started it ends, it closes every connection, removes its socket, releases the lock and ends with the status 0 within 2 seconds. It stops no Exchange (ARC-2) |
| What it hands on | The lock file and the socket are opened so that no program the backend starts inherits them (close-on-exec), and the socket is made with the file mode mask 077, so that a detached Trunk never holds a later backend out |

The Swift App starts the current Root's backend when Arbol starts, and starts it again whenever it ends while Arbol runs. It starts another Root's backend when that Root's first window opens, and ends it when the last one closes (ARC-0). How it does so is the Swift App's specification (SYL-192).

A backend starts for a Root in every state, `preparing`, `working` or `failed`, because a Root that is being prepared is tried with its chats, and a failed one is still opened when it is named ([ARC-1](../architecture/01-roots.md#the-states-of-a-root-and-the-current-root)). It serves an older Root for as long as its folder, its database and its Builds exist.

What it does at its start, in this order: the lock, the socket and the ready line; the removal of request files older than one hour that a start left in `requests/` ([below](#sending-a-message)); the connection to the database, which may fail without stopping anything else ([below](#when-the-database-cannot-be-reached)); `arbol-root settle` ([below](#settling)); the first look at the Exchanges ([below](#stuck-exchanges)); and the discovery across Roots ([below](#restarts-and-discovery-across-roots)). Windows can connect from the ready line on.

<!-- sources:
arbol:src/arbol_backend/model.py#identity
arbol:src/arbol_backend/lifetime.py#Lifetime
arbol:src/arbol_backend/server.py#Backend.run
arbol:src/arbol_backend/cli.py#main
arbol:tests/test_backend.py#Process
-->

### The current Root and listeners

The backend never stores which Root is current. When it needs to know, at its start and when a window asks, it runs `arbol-roots list` and takes the record marked `current` ([ARC-1](../architecture/01-roots.md#the-states-of-a-root-and-the-current-root)). Listeners run only in the current Root's backend; this specification has none, because Telegram, the only listener so far, is postponed (ARC-D52). While a window is connected it observes its own Root's `root.json` and the current catalogue on the bounded cycle in BKD-D29, and tells every window within 5 seconds when the Root's state, display name or current flag changed (the topic `root`, BKD-1), so that a header never shows a state the Root has left.

<!-- sources:
arbol:src/arbol_backend/process.py#Programs.current_root
arbol:src/arbol_backend/roots.py#Roots.refresh
arbol:src/arbol_backend/roots.py#Roots.get
arbol:tests/backend/test_bridge.py#RootWire
arbol:src/arbol_backend/server.py#Backend.monitor
arbol:tests/test_backend.py#AsyncFoundation.test_current_root_is_read_each_time_and_metadata_refreshes
-->

### Other programs it starts

| Program | For | Through |
|---|---|---|
| `arbol-root` | Starting, listing, stopping and settling Exchanges ([RTM-0](../../arbol-root/specs/00-the-commands.md)) | Its launcher, always with `--root <root>` |
| `arbol-roots` | The list of Roots ([ARC-1](../architecture/01-roots.md#the-tray-menu-and-arbol-roots)) | Its program on the search path |
| `arbol-claude-driver`, `arbol-codex-driver` | Account commands only ([below](#accounts)) | Their launchers |
| `/usr/bin/security` | Reading the database password, as a Trunk reads it ([below](#the-database)) | Itself |

The *launchers* are the small programs in `~/.local/bin` that pick the Build to run and start it (BLD-0). The folder of the launchers, `~/.local/bin` unless `--bin-dir` names another, is first on the search path of every program the backend starts, so that a Trunk that `arbol-root` starts for the backend finds the same Drivers as one started from a shell (RCT-0). Each program is started in a process group of its own, as the system call `setsid` does, so that a start, a stop or a settle that is under way goes on when the backend ends. The backend waits for none without a time limit:

| Command | Waited for at most | Because |
|---|---|---|
| `arbol-root start` | 25 seconds | The 20 seconds of RTM-0, and 5 for the launcher |
| `arbol-root stop` | 90 seconds | Up to 15 seconds until the folder is in place, 20 waiting for the end, 10 ending by force, then settling (RTM-0, RCT-2) |
| `arbol-root settle` | 120 seconds | Each Exchange is settled in turn, and the database may take 10 seconds to answer for the first (RCT-2) |
| `arbol-root list`, `arbol-roots list`, and every account command | 10 seconds | They read files, or ask the vendor once |

A program that has not answered in its time is reported as `no_answer`. A `list`, an `arbol-roots list` or an account command then gets SIGKILL to its process group. A start, a stop or a settle is left to run, because it may be doing its work, and the backend keeps track of its process: while one runs it starts no second settle of the same Root, no second stop of the same Exchange and no new look ([below](#stuck-exchanges)).

<!-- sources:
arbol:src/arbol_backend/process.py#Programs.call
arbol:src/arbol_backend/process.py#Programs.close
arbol:tests/test_backend.py#AsyncFoundation.test_listing_group_killed_and_mutation_tracked
arbol:tests/test_backend.py#AsyncFoundation.test_launcher_path_groups_and_no_inference
-->

### Copies whose original went on

For a Root with lineage and an installed supported layout, run its global `arbol-roots migrate <root> --check` at backend start and when its chat list opens (ARC-D50). Coalesce an already running check for that Root; no timer/poll or parallel duplicate is added. Serve local chat data meanwhile and publish changed summaries after success. Failure preserves saved marks and opens a `migration_unavailable` attention item with the source’s bounded message, cleared by a later successful check; never claim the originals are up to date after failure. Missing stale/provenance columns are `layout_incomplete`, not a guessed fresh state. The backend reads only its own metadata and Root catalogue; it never opens the older database.

`chat.reimport` validates the target copy UUID and calls `arbol-roots migrate <root> --chat <chat>`, at most 90 seconds. It changes no chat table itself, starts no second import of that copy while one is unresolved, and returns the result chat/action through BKD-1.13. Publish normal list/chat invalidations/snapshots after success, and preserve unrelated Drafts. A process still working after no_answer is tracked, not killed to guess rollback. Reimport is never automatically repeated after ambiguous/disconnected/no_answer: it may have made another copy; refresh the list and report that uncertainty. The copy’s current agent is never stopped or transferred.

<!-- sources:
arbol:src/arbol_backend/migration.py#Migration
arbol:src/arbol_backend/migration.py#message
arbol:src/arbol_backend/process.py#Programs.call
arbol:tests/backend/test_chat_migration.py#Delegation
arbol:src/arbol_roots/sql.py#migrate
-->

### The database

The backend connects to the Root's database as a Trunk does ([RCT-0](../../arbol-root/contract/00-overview.md#how-a-trunk-finds-its-roots-folder-and-database)): the address in `~/.arbol/database.json`; the password of the Keychain item with the service `com.sylvan-stack.arbol.database` and, as its account, the role the address names, read with `security find-generic-password -s com.sylvan-stack.arbol.database -a <role> -w` within 2 seconds, where the exit status 44 means that there is no such item and the backend connects without a password; and the database that `root.json` names (ARC-1). It talks to it with psycopg 3 at a version pinned in the Build, with its own plain SQL, and every call has a time limit of 5 seconds, to connect and for each statement (RCT-3). It never opens the database of another Root (ARC-1).

| Tables | The backend |
|---|---|
| The chat tables `chats`, `exchanges`, `messages`, `tool_calls`, `runs` (RCT-3) | Reads them directly with SQL, and writes only `chats.title`, when the Leather Bag gives a chat a title or takes it away |
| Its own tables, `drafts`, `chat_settings`, `chat_marks` and `exchange_notes` ([Interface](#interface)) | Reads and writes their rows; nobody else does |
| `migrated_chats` of a Root that grew from another (RTM-1) | Reads optional provenance/stale fields for its own Root only; the Root script alone compares/imports and writes them |

It reads a chat, a page of the list of chats and every snapshot of BKD-1 in one transaction that is `REPEATABLE READ` and `READ ONLY`, so that what it reads is one moment and a Trunk's end committed meanwhile cannot tear it; every other use of a connection commits each statement at once, so that no connection stays idle inside a transaction. It reads a chat as RCT-3 says, without knowing which Trunk wrote it: every Exchange of the chat that was not replaced, in the order of their numbers, and within each its messages and the tool calls the agent made itself in the order of their positions ([RCT-3](../../arbol-root/contract/03-the-chat-tables.md#how-a-chat-is-read)). For an Exchange that is still open it reads the answer from the folder ([below](#an-exchange-in-progress)). With a chat it reads the number of its Exchanges that were not replaced and the sum of the tokens of its runs, which the window shows as "Turn n of N" and in the cockpit.

A title is 1 to 240 characters, counted as PostgreSQL's `char_length` counts them, as the chat tables check. The backend writes the Leather Bag's text with its white space at both ends removed, and NULL when nothing is left, and never a placeholder ([RCT-3](../../arbol-root/contract/03-the-chat-tables.md#the-tables)). For example, renaming a chat to "  Build script  " stores `Build script`.

**Its own tables.** The backend never changes the shape of the database: it creates, changes and removes no table, column, index or check. Its four tables are written into the Root's own layout, `roots/<root>/layout.sql` in the `arbol-root` repository, which the Root's `arbol-root` Builds carry as `layout/root-tables.sql` and `arbol-roots` runs ([RTM-1](../../arbol-root/specs/01-builds-layouts-and-migration.md#the-roots-own-layout)). A later Build of the Root may only add to that file what the Root's older Builds can ignore (RTM-1.5), and the settings file `arbol.json` changes the same way ([below](#settings)). When a Root's database lacks them, the backend still serves its chats, without Drafts, settings, marks and notes, and every window shows the attention item `layout_incomplete` ([BKD-1](01-the-bridge.md#attention)).

A Root that grows from another gets the rows of these tables from its migration script, which copies them as they are, after the chat tables, as the [Interface](#interface) shows. A Root whose layout lacks them gets them with `arbol-roots layout <root>` before another Root grows from it (RTM-1).

<!-- sources:
arbol:src/arbol_backend/database.py#credentials
arbol:src/arbol_backend/database.py#password
arbol:src/arbol_backend/database.py#Database
arbol:src/arbol_backend/database.py#Session.execute
arbol:tests/test_backend.py#SQL
-->

<!-- sources:
arbol:src/arbol_backend/chat_data.py#Reader
arbol:src/arbol_backend/chat_data.py#preview
arbol:src/arbol_backend/chat_data.py#metadata
arbol:src/arbol_backend/metadata.py#inspect
arbol:src/arbol_backend/metadata.py#Layout
arbol:tests/backend/test_chat_reader.py#Chats
arbol:tests/backend/test_chat_wire.py#Windows.test_backend_needs_no_schema_or_history_write_permission
-->

### Chat read and update choices (BKD-D30)

SYL-249 settles the following details before implementation. Reads of a chat, its older Exchanges or a page use one `REPEATABLE READ READ ONLY` transaction, including layout/provenance inspection and all dependent rows. Visible Exchanges exclude `replaced_by`; the visible count excludes them, while token totals include every saved agent/small run of the chat, including replaced runs whose tokens were spent. An open Exchange contributes only its position-zero user message from SQL; sub-agent tool calls (`parent_call_id` not null) are omitted. The newest 12 visible Exchanges are returned in ascending number order, with `more` for older visible ones; `beforeNumber` is exclusive, positive, and limits are integers, never booleans. A missing chat has null title, zero count/usage, no Exchanges and defaults for absent local rows; it is not created by a read or a setting call.

List activity is the latest accepted/end time of the last visible Exchange, or the chat creation time when it has none. The ordering key is that time truncated to milliseconds plus the chat UUID, both descending, and `before` uses that same key exclusively. All wire times are UTC ISO strings with exactly milliseconds and `Z`, so a microsecond lost in display cannot skip a pagination boundary. The default page is100, at most200; older Exchange pages default12, at most50. Tool input/result values over8KiB of canonical UTF-8 JSON become a string preview of that representation whose own JSON encoding fits8KiB, without breaking UTF-8; `cut:true` marks either cut. `toolCall.get` returns their full original values (the normal16MiB Bridge ceiling still applies). Other tool flags, questions/answers and saved run metadata are preserved. No credential/configuration object is projected as metadata; route fields are the known Route fields, with unknown request fields ignored rather than saved as credentials. User transcript/tool content is not logged or treated as an account configuration channel.

Each view coalesces only its in-flight read, per chat or list, and commits its captured state, publication version and snapshot cutoff together without an await. A mutation invalidates an earlier in-flight view generation before refreshing it, so that an older database snapshot cannot overwrite a completed local change. Different chats, Root metadata, windows and ordinary calls do not share a database connection or a lock across I/O. Observers read subscribed views on a250ms cycle; on a responsive database changed summaries are published within one second, with a bounded observation attempt rather than allowing one slow query to serialize other views. Changes to title/settings/marks/Draft use their named events; material saved-history or provenance changes may replace the chat with a fresh snapshot. This is an additive use of the existing snapshot event. The live lines/saved-event lifecycle remains SYL-251. The list observer compares all lightweight summaries so that an older paged chat's rename/archive is not missed; the initial snapshot still holds only100. Archived summaries appear only in changed events with `archived:true`. Changes are published only from committed reads, never before a write commits.

`chat.rename` trims Unicode whitespace; null or whitespace-only text stores NULL, otherwise it requires1–240 valid Unicode characters. Settings and marks require an existing chat and at least one known change; omitted fields preserve current values by a single autocommit upsert, including under concurrent independent changes. A supplied route names driver/subscription/model, with optional effort, and only known fields are stored; every supplied UUID and syntactic identifier is checked first. Available Driver launchers and their previously obtained local `subscriptions list` catalogues supply identifier membership before any request can start a program or touch a parameter-derived file. The backend loads those public catalogues independently at startup; account refresh/UI belongs to SYL-253. A catalogue failure refuses a route change safely, never guesses that a Subscription exists. A working folder must be an existing absolute directory. Archiving records its time once, repeated archive is harmless, and unarchive clears that time; a partial mark never overwrites the other mark. No mutation here marks ongoing on acceptance; SYL-250 does.

Required current columns are checked with the backend tables and sequence; an id-only stand-in table is not a complete supported layout. This is not a demand for future optional columns. When a required backend table/column/sequence is missing, reads omit all four tables' local data, the attention snapshot/changes carry `layout_incomplete`, and calls which need those tables fail with that code. The backend never runs DDL. For a Root with `grewFrom`, required local `migrated_chats` columns (including stale) are also checked before exposing provenance; an unsupported shape is layout_incomplete, not fabricated fresh metadata. `root.get.layoutComplete` includes this additional required lineage layout, while database errors remain errors. ChatSummary and ChatInfo may carry the same optional `{fromRoot,fromChat,stale}`; the backend never connects to that source Root. Stored marks stay last-known when a comparison fails.

For lineage with a supported layout, startup and each list opening start `arbol-roots migrate <ownRoot> --check` independently of serving local data. Concurrent requests join its existing attempt; there is no comparison timer. Both comparison and explicit reimport have a90-second deadline and remain tracked rather than killed on timeout, cancellation or shutdown because the command may be changing provenance/history. Reimport calls only `arbol-roots migrate <ownRoot> --chat <validatedTargetCopy>`; one unresolved attempt per copy is allowed, no automatic retry, and a late/ambiguous result remains uncertain. A successful validated command result maps `resultChat` to `chat`, its input copy to `previousChat`, and carries action/fromRoot/fromChat; it invalidates local subscribed views only after the command succeeds. Forwarded codes/source are preserved with a bounded plain message; credential-shaped diagnostics use a fixed safe fallback and no raw output is logged. Comparison failure opens migration_unavailable, a later success closes it, and failed or missing layout never clears stale marks by guesswork.

`paste.save` requires at least10,000 valid Unicode characters. It creates an exclusive UUID-named UTF-8 file under the own Root's private0700 `pastes` directory with0600 permissions, uses directory descriptors and no-follow opens to refuse symlink/path substitution, writes exact bytes and removes only its own incomplete file on failure. Existing files are never overwritten or pruned.

<!-- sources:
arbol:src/arbol_backend/views.py#View
arbol:src/arbol_backend/chats.py#Chats
arbol:src/arbol_backend/chats.py#page_params
arbol:src/arbol_backend/validation.py#Catalogues
arbol:tests/backend/test_chat_foundation.py#Views
arbol:tests/backend/test_chat_wire.py#Windows.test_late_older_write_reply_cannot_publish_stale_settings
-->

### Settings

The backend's settings are the file `~/.arbol/roots/<root>/arbol.json`, which the owner can edit and the backend reads at its start ([ARC-1](../architecture/01-roots.md#settings)). In this specification it holds the defaults of Elma Chat: the route a new chat starts with, for all repositories and for single ones, until the Leather Bag picks another, and the small-call route a Trunk is handed for small calls such as a title ([BKD-D3](#decisions)):

```json
{ "route": { "driver": "claude", "subscription": "anthropic", "model": "sonnet", "effort": "high" },
  "repositories": { "shop": { "route": { "driver": "codex", "subscription": "chatgpt" } } },
  "smallCallRoute": { "driver": "claude", "subscription": "anthropic", "model": "haiku" } }
```

A missing file, or one without a field, is no error. A new chat's route is then the first that exists of its repository's route, the file's route and the first signed-in Subscription of the first Driver; a route that names no model or effort takes the catalog's defaults ([BKD-2](02-elma-chat.md#the-route)). No small-call route is handed without one. Elma Chat uses no Brain Recipe: a route is always the Leather Bag's choice or a default ([BKD-D3](#decisions)).

<!-- sources:
arbol:src/arbol_backend/model.py#settings
arbol:src/arbol_backend/model.py#Settings
arbol:tests/test_backend.py#Process.test_optional_settings_and_routes
-->

### Drafts

A Draft is what the Leather Bag has typed in a composer and not sent ([ARC-0](../architecture/00-components-and-boundaries.md#who-writes-what)). As in version 1, each chat has one Draft of its reply, and each repository one Draft of a new chat ([BKD-2](02-elma-chat.md#the-composer)). A Draft holds the text; the route and the folder are the chat's settings ([below](#the-chats-settings-and-marks)). The backend keeps Drafts in its table `drafts` ([BKD-D5](#decisions)).

| | |
|---|---|
| Saving | The window sends the Draft as the Leather Bag types, with the revision it last saw. The backend replaces the row whole and gives it a new `revision`, taken from one counter for all Drafts, so that a revision is never given twice, also after a Draft was removed. A Draft whose text is empty is removed |
| Two windows | A save over a revision that is no longer the Draft's is refused with `draft_conflict` and the Draft as it is, so no window overwrites text it has not seen. Every window of the chat is told of each new revision (BKD-1) |
| Sending | `chat.send` names the revision it was sent from. The backend marks that Draft with the Exchange's identifier, `sent_as`, and keeps beside it what was sent, `sent_request`: the chat, the route and the working folder, before it starts anything; a save clears the mark, because the Draft then holds new text |
| Accepted | The backend removes the Draft that is still marked with that Exchange, and tells every window. A Draft typed further meanwhile carries no mark, and stays. Whenever the backend reads a Draft whose mark names an Exchange the chat tables hold, it removes the Draft too, so a removal that a backend which ended never made is made later |
| Ongoing | Once a message is accepted, the backend marks its chat ongoing in `chat_marks`, as version 1 did ([below](#the-chats-settings-and-marks)) |
| Refused | The backend clears the mark, and the Draft stays as it was ([ARC-2](../architecture/02-chat-exchange-across-components.md#the-steps)) |
| Too large | A Draft or a message of more than 1 MiB is refused with `invalid_input` |

For example, the Leather Bag sends "Add a --clean option" from revision 41 in one window and types "and a --verbose one" in another before the reply: the backend marks revision 41 as sent with the new Exchange, the second window's save makes revision 42 and clears the mark, and the acceptance then removes nothing, so the new text stays.

<!-- sources:
arbol:src/arbol_backend/drafts.py#Drafts
arbol:src/arbol_backend/drafts.py#Drafts.save
arbol:src/arbol_backend/drafts.py#Drafts.mark
arbol:src/arbol_backend/drafts.py#Drafts.finish
arbol:src/arbol_backend/drafts.py#Drafts.reconcile
arbol:src/arbol_backend/drafts.py#Drafts.recover_captured
arbol:src/arbol_backend/drafts.py#Conflict
arbol:src/arbol_backend/drafts.py#scope
arbol:src/arbol_backend/drafts.py#save_params
arbol:src/arbol_backend/drafts.py#content
arbol:src/arbol_backend/drafts.py#folder
arbol:tests/backend/test_drafts.py#Drafts
-->

### Draft and dispatch choices (BKD-D31)

SYL-250 settles these details before implementation. A Draft scope contains exactly one canonical chat UUID or one absolute, normalized repository-folder path; folder keys remain readable when the folder disappears. A chat Draft requires an existing chat; no backend operation creates chat history. Text is preserved exactly, is valid Unicode without NUL, and is at most1MiB of UTF-8; empty means exactly the empty string. A message must also contain non-whitespace text. Revisions/base revisions are exact positive integers within PostgreSQL bigint, never booleans/fractions; null base means absence. Conditional SQL insert/update/delete arbitrates competing windows; failed CAS returns draft_conflict with the current Draft or explicit null. Revisions use nextval(drafts_revision), may have gaps, and never reuse a removed revision. Every successful text save clears both send fields. No DDL is issued.

A send validates its entire public payload before changing a Draft or file. A named Draft belongs to that chat or the new-chat repository folder; a fresh dispatch must match its revision and exact message text and cannot steal another pending Exchange's mark. Conditional marking changes no text revision. Repeating an already tracked dispatch joins it before marking again; a previously accepted own-chat identifier may be replayed after its Draft was removed or edited. Conflicting normalized payloads for one identifier are invalid_input. Acceptance and refusal cleanup are conditional on the exact marked revision/Exchange/request; a later text save or different mark survives. Acceptance sets ongoing while preserving archived state. If local cleanup fails after a valid acceptance, return that acceptance and recover the marked Draft on a later read. Read reconciliation first observes an accepted Exchange in a read-only repeatable snapshot, then conditionally removes only that exact marked Draft outside it, confirming the saved request's chat matches the Exchange; it also restores ongoing. The final chat/Draft/list snapshot is a fresh READ ONLY REPEATABLE READ transaction. No cleanup is written inside a snapshot and no unvalidated identifier can erase another chat's text.

The requests directory is owner-only0700, opened through the own Root with no-follow descriptors; files are owner-only0600. A complete bounded UTF-8 JSON request is written to an exclusive private temporary file and linked atomically as <exchange>.json without overwriting an existing path. An existing regular owner-only single-link file may be adopted only when its bounded bytes equal the same normalized request; symlinks, special files, foreign/insecure/mismatched files are refused. Cleanup compares the inode it owns and never removes a replacement. While its manager is unresolved, the request stays readable; after that manager returns it is removed, and any retry writes it anew. Shutdown never unlinks a request still needed by a mutating child. Startup removes only matching private regular request/temporary files older than one hour, not arbitrary directory contents; inaccessible/insecure storage yields a safe request error without stopping readiness.

Each normalized Exchange dispatch is one backend-owned shielded task, independent of a window's connection. Equivalent callers receive its one outcome; closing one window never cancels the dispatch. Production attempts wait at most25 seconds, retry no sooner than15 seconds after the preceding attempt returned, stop waiting at120 seconds from the first attempt, and never launch while that Exchange's manager remains tracked. The total bound also bounds a last attempt's wait; an unresolved start is retained, never killed, and its Draft mark/request remain recoverable. no_answer, in_progress, missing/malformed/oversized replies and launch failure are uncertain; they do not clear a mark. A new explicit call may resume after the bounded run, retaining the same identifier/payload and any unresolved manager. Timing injection is test-only, not settings or public wire input. No automatic retry continues after the total bound.

Only a validated accepted:true/boolean duplicate/canonical matching Exchange and chat/positive number result is projected as Accepted; other fields are ignored. Structured exit1 refusals are accepted only in the stated error shape, with bounded plain messages and safe source projection; credential-shaped diagnostics or the already held database password become a fixed message. Root manager/launcher codes (unknown_root, unknown_trunk, no_fit, contract_mismatch, trunk_unavailable) are attributed to root-manager; untagged contract refusals to trunk, because the current manager forwards a Trunk's line unchanged. An explicitly valid source is preserved. no_answer/in_progress remain uncertainty regardless of their source. Unknown well-formed refusal codes are passed through, not guessed to be acceptance. For sendAgain, read only the old Exchange's own chat/folder, validate the chosen route/new distinct UUID, omit message and pass --replaces; the Trunk alone checks last/ended/replaced eligibility. Exchange following/stop/control, real vendor journeys and Swift/UI work remain their later Beats.

### The chat's settings and marks

Observed in version 1: a model or an effort picked was saved for the chat at once and counted from its next message on, also while its agent worked, and a route picked counted from the next message. Changed: a route picked for a chat that exists is saved at once too; in an empty chat the choice stays in the window and goes with the first message ([BKD-2](02-elma-chat.md#the-route)). The backend keeps, in its own tables:

| Table | For each chat |
|---|---|
| `chat_settings` | The route picked for its next message and its working folder, once either differs from its last Exchange's. A new chat's first message names both itself (`chat.send`) |
| `chat_marks` | Whether the Leather Bag marked it ongoing, and when it was archived. An archived chat leaves the latest chats; nothing archives or deletes a chat by itself |

**A long paste.** Text of 10,000 characters or more pasted into a composer is saved by the backend as a file `pastes/<uuid>.txt` of the mode 0600 in the Root's folder, which the folder `pastes/` of the mode 0700 holds, and the window puts the file's path in the message in its place (`paste.save`, BKD-1), as version 1 did. The files stay with the Root, because the chat names them.

<!-- sources:
arbol:src/arbol_backend/chats.py#Chats.rename
arbol:src/arbol_backend/chats.py#Chats.settings
arbol:src/arbol_backend/chats.py#Chats.mark
arbol:src/arbol_backend/chats.py#Chats.paste
arbol:src/arbol_backend/chats.py#rename_params
arbol:src/arbol_backend/chats.py#mark_params
arbol:src/arbol_backend/chats.py#paste_params
arbol:src/arbol_backend/validation.py#save_paste
arbol:tests/backend/test_chat_foundation.py#Inputs
arbol:tests/backend/test_chat_wire.py#Windows
-->

### Sending a message

1. The window calls `chat.send` with the chat, the message, the route, the working folder, the Draft's revision and an Exchange identifier it chose ([BKD-1](01-the-bridge.md#sending-and-repeating)).
2. The backend checks what it can before it touches a file or starts a program, and refuses with `invalid_input`: a chat or an Exchange identifier that is not a UUID written in lower case with hyphens (RCT-0); a route that does not name a Driver whose launcher is in the folder of the launchers, a Subscription and a model, because Arbol always hands those three (ARC-0); a working folder that is not an absolute path to a folder that exists (RCT-0); an empty message, and one of more than 1 MiB. It marks the Draft as sent ([above](#drafts)).
3. It writes the *request file* of [RCT-0](../../arbol-root/contract/00-overview.md#what-is-handed-to-a-trunk) into the folder `requests/` of the Root's folder, of the mode 0700, as `<exchange>.json` of the mode 0600: the chat, the message, the route, the working folder, and the `smallCallRoute` of `arbol.json` when it names one ([above](#settings)). The Trivial Trunk makes no small call with it (TRV-0).
4. It runs `arbol-root --root <root> start --exchange <exchange> --request <file>`. Without a code name the Root manager starts the Trivial Trunk ([RTM-0](../../arbol-root/specs/00-the-commands.md#starting-a-trunk)).
5. It returns what the one line says, and removes the request file when the Root manager has not.

```json
{
  "chat": "c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b",
  "message": "Add a --clean option to it.",
  "route": { "driver": "claude", "subscription": "anthropic", "model": "sonnet", "effort": "high" },
  "workingFolder": "/Users/sam/repos/shop"
}
```

| The line says | The backend |
|---|---|
| `"accepted": true`, `"duplicate"` either way | The message is accepted ([ARC-2](../architecture/02-chat-exchange-across-components.md#the-steps), RCT-2). It removes the Draft as above, and every window of the chat starts to follow the Exchange |
| A refusal of the Trunk or the Root manager, such as `chat_busy` or `database_unavailable` | Passes it on with its code and its message. The Draft stays, and nothing was started (RCT-2) |
| Nothing within its 25 seconds, `no_answer`, or `in_progress` | None of these is a refusal: the message may still be accepted. The backend runs the same start again, with the same identifier and a request file written anew, 15 seconds after the previous attempt returned, the longest an acceptance takes (RCT-2), and never while an attempt still runs. A Trunk that accepted it replies `"duplicate": true` and starts nothing (RCT-D17). After 120 seconds without an acceptance or a refusal it replies `no_answer`, and the Draft keeps its mark ([BKD-D9](#decisions)) |

Because the window chose the Exchange's identifier, it sends the same `chat.send` again after `no_answer`, and after a backend that ended before it replied has come back, and gets the same Exchange, not a second one (RCT-D17). A second `chat.send` or `exchange.sendAgain` for an Exchange the backend is starting joins the first and gets its reply; a stop of that Exchange waits until the start has returned. A window that finds a Draft still marked as sent, of a chat or of a repository's new chat, sends that `chat.send` again with the marked identifier and the request kept beside it, so a send that a closed window left half done is finished.

A chat takes one Exchange at a time (ARC-D54): a message to a chat whose Exchange is still open is refused by the Trunk with `chat_busy`, which names the open Exchange. The window asks "Stop current response?" while it knows the chat busy, and puts a message refused with `chat_busy` back in the composer ([BKD-2](02-elma-chat.md#sending-and-stopping)). The backend checks nothing of this itself, because only the database can tell two messages at the same moment apart (RCT-3).

<!-- sources:
arbol:src/arbol_backend/dispatch.py#Dispatch
arbol:src/arbol_backend/dispatch.py#Dispatch.send
arbol:src/arbol_backend/dispatch.py#Dispatch.run
arbol:src/arbol_backend/dispatch.py#Dispatch.result
arbol:src/arbol_backend/dispatch.py#Dispatch.send_params
arbol:src/arbol_backend/dispatch.py#Dispatch.close
arbol:src/arbol_backend/requests.py#Requests
arbol:src/arbol_backend/requests.py#Requests.write
arbol:src/arbol_backend/requests.py#Requests.clean
arbol:src/arbol_backend/requests.py#Request.remove
arbol:tests/backend/test_dispatch.py#Sending
arbol:tests/backend/test_request_files.py#Files
-->

### Sending a message again

The Leather Bag can send the message of a chat's last Exchange again once that Exchange has ended, for example after a failure or a rate limit: the previous answer and its tool calls are discarded, and everything runs again from the same message ([RCT-2](../../arbol-root/contract/02-starting-stopping-and-settling.md#sending-a-message-again), RCT-D15, RCT-D16).

The window calls `exchange.sendAgain` with the Exchange, a new Exchange identifier and the route; the backend writes a request file with the chat, the route and the working folder of the replaced Exchange and no message, and runs `arbol-root --root <root> start --exchange <new> --request <file> --replaces <old>`. The route is the one the Leather Bag picks, by default the one the replaced Exchange ran with. The Trunk refuses with `cannot_replace` an Exchange that is not the last of its chat, has not ended or was replaced already (RCT-2), and the backend passes that on.

<!-- sources:
arbol:src/arbol_backend/dispatch.py#Dispatch.again_params
arbol:tests/backend/test_dispatch.py#Sending.test_send_again_uses_old_chat_folder_no_message_and_passes_cannot_replace
-->

<!-- sources:
arbol:src/arbol_backend/event_file.py#Scanner
arbol:src/arbol_backend/event_file.py#Envelope
arbol:src/arbol_backend/event_file.py#completed
arbol:src/arbol_backend/event_file.py#superseded
arbol:src/arbol_backend/exchange_files.py#Folders
arbol:src/arbol_backend/exchange_files.py#Record.status
arbol:src/arbol_backend/exchange_files.py#processes
arbol:src/arbol_backend/exchange_files.py#living
arbol:src/arbol_backend/live.py#Live
arbol:src/arbol_backend/live.py#Live.step
arbol:src/arbol_backend/live.py#Live.stream
arbol:src/arbol_backend/live.py#Lines
arbol:src/arbol_backend/controls.py#Controls
arbol:src/arbol_backend/controls.py#Controls.run
arbol:src/arbol_backend/answers.py#Answers
arbol:src/arbol_backend/answers.py#answer_params
arbol:src/arbol_backend/answers.py#current
arbol:src/arbol_backend/answers.py#validate
arbol:src/arbol_backend/settling.py#Settling
arbol:src/arbol_backend/settling.py#listing
arbol:tests/backend/live_support.py#Trunk
arbol:tests/backend/test_event_file.py#Files
arbol:tests/backend/test_exchange_files.py#Files
arbol:tests/backend/test_live.py#Windows
arbol:tests/backend/test_controls.py#Stopping
arbol:tests/backend/test_answers.py#Answering
arbol:tests/backend/test_settling.py#Settles
-->

### Live Exchange and control choices (BKD-D32)

SYL-251 settles these details before implementation. Folder readers open only their own Root's exchanges directory, real canonical UUID directories, and the published record/events/control files through no-follow descriptors. Directories/files must be private owner-owned directories/regular files, not symlinks, devices, FIFOs or extra hard links. Missing/dot folders are skipped; unreadable records never become guessed dead or saved Exchanges. Records are bounded to1MiB and must have matching Root/Exchange, canonical chat, contract1, valid immutable process/trunk/build identity, absolute timestamps and a nonnegative heartbeat. Unknown fields are ignored and unknown waiting/end-state strings are preserved. Only published fields are projected, with the existing safe diagnostic boundary. The process reader runs only /bin/ps, with PATH=/usr/bin:/bin, LANG=C, LC_ALL=C and TZ=UTC, at most5 seconds; missing PID means gone, another failure means unknown/unreadable. Its UTC start must match within two seconds inclusive. Folder names/process observations use one shared750ms cycle per Root while chat windows follow it; a100ms follower cycle leaves room for healthy I/O within the one-second appearance and250ms file-delivery bounds. Line batches remain at least50ms apart. No backend process check signals a Trunk.

Each active chat subscription has its own file offsets and replay generation. Its snapshot is queued before any file event. Every replacement snapshot resets replay, including one published by an ordinary SQL view refresh: a window that forgets its old lines must receive them again. A generation check before each enqueue prevents an older replay from crossing a newer snapshot. Subscription replacement, disconnect and slow_reader release only that reader's state/descriptors. File lines are never cached as conversation history. Bounded read buffers and metadata such as offsets, completed-block identities and sequence numbers are allowed; all other windows/calls remain independent.

At replay start capture a file-size boundary and find its complete-line prefix. First scan that prefix for completed text/thinking blocks and finished tools; then read it again and emit its lines in order, omitting only deltas superseded within that prefix. Block identity is runId plus parentCallId plus text/thinking kind; tool identity also includes callId. Because the Driver format has no block id, a whole block supersedes preceding deltas of that kind in that run/parent stream. Deltas after the last whole block remain. A concurrently appended suffix is read normally after the captured prefix, without compacting already delivered deltas. Preserve each n and every field of a recognized envelope/event; skip unknown/malformed complete lines and unfinished final lines, never reflect them in diagnostics. An unknown line may leave a gap in the numbers delivered; the Bridge seq remains gapless. Known events with additive fields remain intact. Duplicate/backward n values are ignored rather than replayed as new content.

Read in bounded chunks with cooperative yields. A line whose complete Bridge wrapper cannot fit16MiB including LF becomes {n,tooLarge:true,bytes}, with bytes counting its original UTF-8 file line including LF. This also covers an otherwise16MiB line whose wrapper would cross the limit. Oversized lines are scanned for bounded envelope metadata without allocating their payload, and do not assume JSON property order. Complete batches are split under the same ceiling; file polls run at250ms or faster and queued batches at least50ms apart. A changed/truncated/replaced events file restarts from its first line with its identity checked, so duplicate n values are harmless to a window. No mmap access can fault on a concurrently truncated producer file.

Read the chat's own database row before treating an Exchange as live. While it is open, only its position-zero message comes from SQL. A valid folder can announce accepting/running/ending/unsaved/gone; unaccepted is hidden, and an uncertain process is not fabricated as gone. A committed ended row must not regress to a live status after an ended snapshot. When a previously followed folder disappears, capture committed saved rows again and send saved only for an ended row; an open/missing row is not guessed complete. Normal immutable chat snapshots still carry counts/usage/local metadata. A folder that appeared outside chat.send is observed within a second under healthy local I/O, whichever caller started it.

A stop is one backend-owned shielded task per Exchange, and publishes stopping to known chat windows until a record/database end confirms the outcome. It waits up to120 seconds for this backend's already shared dispatch and any retained active start manager, then runs only arbol-root --root ownRoot stop <exchange>, at most90 seconds. Both waits are bounded; neither cancels or kills a mutation. In the unusual case of a long acceptance, the window's120-second deadline can expire while the backend's stop continues; repeating joins that same task. A start wait that expires returns no_answer without inventing a stopped state, and a later explicit stop may resume. Concurrent callers never launch two stop managers, also after a caller timeout. A valid ended value (completed,failed,cancelled,interrupted,saved,none) is projected unchanged only from a matching own-Root/Exchange reply. Structured refusals keep their safe code/message with root-manager source. Unknown/ended Exchanges are delegated idempotently; a command result is not a fabricated database end.

For an answer, scan the complete live file prefix for the most recent still-open matching askId, its run/parent identity and question form. Withdrawn/never-opened is not_found; absent live and matching .new folder is ended. Ambiguous simultaneously open uses of the same askId are refused. Validate exact known question ids, unique chosen labels, single/multiple cardinality and membership in the listed options. A question with no options has an empty selection; all-empty questions therefore support Continue. There is no free text (BKD-2). Decline is valid for a current question. Normalize only known answer fields. A known answer line for that question is already delivered and can succeed without another write; a later Driver refusal/end remains authoritative. No persisted in-memory copy of event lines is needed to find a form.

Append the bounded UTF-8 JSON control line including LF with exactly one os.write on an existing private regular control opened append-only/nonblocking/no-follow, never O_CREAT. Recheck directory/file identity and current end before writing. When only the matching .<UUID>.new directory exists, wait at most15 seconds for publication; neither directory means ended. A short/failed write is a safe uncertain error and is never automatically repeated by the backend. Writing is not an answer-accepted event: the window learns that only from answer/ask_closed/control_refused lines.

Settling is an own-Root coalesced work queue. Startup and a validated listing with unaccepted/unsaved/interrupted request it; a reason arriving while one runs schedules one further pass after it. Probe the own database before launching, and launch none while it is unavailable. Each actual settle waits at most120 seconds and is retained, never killed, after no_answer. A pending reason cannot launch another while that manager runs; without a new reason no automatic retry is invented. Validate structured results/refusals, then invalidate relevant committed chat views; saved is still driven by actual rows/folder state. SYL-252 extends this queue with the database-return, stuck and per-Root recovery choices below. Real Root/Trunk/vendor/window journeys and Swift/renderer work remain their named later Beats. Timing injection exists only in private checks, never as wire/settings input.

### An Exchange in progress

While an Exchange's folder exists, its answer is read from the folder, which holds all of it so far ([RCT-1](../../arbol-root/contract/01-the-exchange-folder.md#the-answer-as-it-arrives-eventsjsonl)):

1. The backend reads the Exchange's row first. While it is `open`, it takes from the tables only the Leather Bag's message at position 0, and the answer only from the folder `exchanges/<exchange>/`, which holds all of it so far (RCT-3).
2. It reads `events.jsonl` from its first line and then each line as it is appended, at least every 250 milliseconds while a window follows the Exchange, and passes what it has read to each such window at most every 50 milliseconds, as one batch. It reads only whole lines: a last line without a newline is left for the next read. It ignores a line, a field and an event type it does not know (RCT-1).
3. It reads `record.json` with the same reads, for the Exchange's *signs of life*, a counter the Trunk raises at least every 10 seconds while it works and what it waits for (RCT-1), and for its end. It counts the Exchange's process as alive only when a process with the recorded number runs and was started at the recorded time, give or take two seconds, so that a new program that got the same number is not taken for it (RCT-1). It reads the start time with `/bin/ps` in a clean environment and the C locale, as the Root manager does (RTM-0).
4. When the folder is gone, the end is in the database, because a Trunk saves the end before it removes its folder (RCT-2). The backend reads the row and the Exchange's rows again, and tells every window that follows the chat that the Exchange is saved.

A folder whose name starts with a dot is skipped (RCT-1). A window opened late, opened again or opened twice gets the lines of `events.jsonl` from the first one on, so it shows the whole answer so far ([ARC-2](../architecture/02-chat-exchange-across-components.md#the-arriving-answer-is-a-file)). When it catches up this way, the backend leaves out the pieces of a block whose whole block is in the file, the `text_delta` and `thinking_delta` lines before its `text` or `thinking` line, and the `tool_output_delta` lines of a tool call whose `tool_finished` is in the file, keeping the `n` of every line it sends, because the window would only replace them. The backend keeps no copy of the lines: the file is the copy, so a backend that has just started serves a late window exactly as one that has run for hours.

While any window follows the chats of the Root, the backend reads the names in `exchanges/` and each record there once a second, and checks each record's process once a second, whatever number of windows follow it. So a window learns within a second that an Exchange appeared, whoever started it, the command line included, that it waits for an answer, or that it went.

What the window is told of the Exchange's state comes from the record and the listing of `arbol-root` ([RTM-0](../../arbol-root/specs/00-the-commands.md#the-listing)), with one state of the backend's own, `stopping`:

| State | When |
|---|---|
| `accepting`, `running`, `ending` | As the listing says. `running` comes with what the Exchange waits for and since when ([ARC-3](../architecture/03-stuck-trunks.md#long-waits-on-purpose)) |
| `stopping` | The backend's own: it was asked to stop the Exchange, which has not ended yet |
| `unsaved` | As the listing says: the record has an end, its process is gone, and the database does not have the end yet ([below](#when-the-database-cannot-be-reached)) |
| `gone` | The listing's `interrupted`: its process is gone without an end, and settling has not saved it yet ([below](#settling)). The window shows it as interrupted, but treats the Exchange as ended only once it is saved |
| `unaccepted` | As the listing says: its process is gone before the database had it. No window shows it; settling removes its folder |
| `completed`, `failed`, `cancelled`, `interrupted` | The final state, from the database |

### Stopping, and answering the agent's questions

**Stopping.** The window calls `exchange.stop`. The backend marks the Exchange `stopping` for every window from that moment until it has ended, and runs `arbol-root --root <root> stop <exchange>` ([RTM-0](../../arbol-root/specs/00-the-commands.md#stopping)). When the command returns, the backend replies with the `ended` that `arbol-root stop` printed, unchanged: `cancelled` when the Trunk confirmed the stop, `interrupted` when the Root manager had to end it by force, or what it ended with otherwise ([ARC-3](../architecture/03-stuck-trunks.md#a-stop-that-is-not-obeyed)). The final state the database holds reaches the windows as the Exchange is saved. "Stopped" is shown only once the end says `cancelled` (RCT-2). A stop of an Exchange that has ended already, or that is unknown, succeeds and changes nothing (ARC-3). Two windows that stop the same Exchange start one `arbol-root stop`: the second waits for the first.

**Answering.** When the agent asks the Leather Bag a question (DRV-3), the window shows it from the `ask_opened` line and calls `exchange.answer` with the question's `askId` and the answer. The backend checks the Exchange's identifier as above and the answer against the question's form (DRV-3), and refuses a malformed one with `invalid_input`. Then it appends one line to the Exchange's `control` file, the Driver's own control line ([RCT-1](../../arbol-root/contract/01-the-exchange-folder.md#stop-and-answers-control)):

```json
{"type":"answer","askId":"ask_1","answer":{"type":"answers","answers":{"branch":["main"]}}}
```

| Rule | Detail |
|---|---|
| One write | It opens the file for appending, never creating it, and writes the whole line of at most 64 KiB, ending with a newline, with one write call |
| Not yet in place | When there is no `<exchange>/control` but the folder `.<exchange>.new` exists, it waits until the folder is renamed into place, at most 15 seconds |
| Gone | When neither is there, the Exchange has ended, and the call is refused with `ended` |
| What the Trunk did with it | The answer is in `events.jsonl` once the Trunk has handed it to the run, as an `answer` line; a `control_refused` event says the Driver did not take it (DRV-2). The window shows what the file says, not what was sent |

A decline is an answer too, `{"type":"decline"}`, and ends the run as cancelled (DRV-3).

### Settling

An Exchange whose process is gone is shown as interrupted, and is *settled*: a Trunk Build saves what its folder holds ([ARC-2](../architecture/02-chat-exchange-across-components.md#an-exchange-whose-process-is-gone), RCT-2). The backend runs `arbol-root --root <root> settle` ([RTM-0](../../arbol-root/specs/00-the-commands.md#settling)):

- when it starts;
- when it sees the database return ([below](#when-the-database-cannot-be-reached));
- after a listing that shows an Exchange in the state `unaccepted`, `unsaved` or `interrupted`, its own or, in a listing across Roots ([below](#restarts-and-discovery-across-roots)), another Root's: then it runs `arbol-root --root <that Root> settle`.

One settle runs at a time for each Root; a reason that arises while one runs runs the next one after it. None runs while the database is unreachable, because settling needs it; its return is a reason of its own. Once settling has saved an Exchange, the backend reads its rows again and tells every window that follows the chat.

### Recovery and discovery choices (BKD-D33)

SYL-252 settles these details before implementation. Health observes only the backend's own database. A connection deadline/failure, a failed bounded SELECT1 probe, a lost connection or a configuration/Keychain failure marks it unreachable and opens database_unreachable with a fixed plain cause. Safe endpoint fields may name the host/port; no password, raw exception, connection string or arbitrary diagnostic crosses the Bridge. Keychain exit44 means an empty password, not a Keychain failure; its other failures or two-second deadline are database-unavailable. The standalone low-level Keychain helper can retain its timeout code; the database boundary classifies that cause. A normal statement timeout is still timeout and marks no outage. Other SQL errors do not by themselves prove a lost connection; a fresh bounded probe decides health.

A backend-owned health task probes at startup and every5 seconds, with the whole connection/SELECT1 probe bounded to5 seconds. Only one probe runs; delays are scheduled from the attempt's start. A successful whole connection/SELECT1 probe ends the outage; an already in-flight ordinary SQL operation that succeeds can do so too. A handshake alone while SELECT1 still fails is not a false recovery. Probe renewal/credential-lock waiting is inside the same5-second bound, and queued ordinary credential callers recheck the outage gate after acquiring the lock. On return, discovery is rechecked independently so previously gated eligible foreign Roots get a fresh listing reason; other Roots never delay this Root's snapshot refresh. Each active return refresh retries a transient read refusal or a superseded generation after a5-second wait while its outage epoch is still current; the next outage or shutdown cancels that obligation. A recovered connection therefore cannot strand an unchanged subscription without its return snapshot. A transition generation rejects obsolete recovery publications. Ordinary SQL operations fail promptly while marked away; only the health probe bypasses that gate, and retries re-resolve this Root's configuration/credentials so a corrected setting can recover. Established unrelated statements remain independent and a single statement timeout changes no health state. Attention snapshots remain available while SQL is away, including when the layout cannot be inspected. No new table is created.

Existing active chat subscriptions retain their already captured immutable SQL snapshot and known row identities. SQL view refreshes, row-identity confirmation and saved-row reads run in separate shared read-only tasks; the file-poll path never awaits a database operation, even before a slow connection is classified as away. Unknown row identities wait for confirmation and cannot masquerade as an ended older Exchange or supply live answer lines. While away, file followers use those identities and private files, continue complete-line replay/status/unsaved transitions and retain no event-line cache. No saved event is guessed without committed SQL rows. Newly discovered folders can announce accepting metadata but their answers wait until their rows are confirmed; a new chat subscription still requires a fresh SQL read and is refused database_unavailable. Poll refresh failures during an outage keep existing subscriptions alive; a slow refresh alone preserves its captured view and cannot fabricate an outage. Draft writes fail safely while away; the window owns its unsaved typed text as BKD-2 says. On return, invalidate captured views, request settling, flush durable notes and refresh every still-active subscription with a new snapshot, checking the transition generation before enqueue. A new outage leaves the existing display/stream intact.

The own-Root outside look runs at startup and every30 awake seconds independently of windows. The clock is time.clock_gettime(CLOCK_UPTIME_RAW) on macOS, monotonic on a platform without it, and a constructor-injected callable only in private checks. Each successful listing records an alive accepting/running/ending Exchange's immutable process identity, heartbeat and first observation time. Any heartbeat or identity change starts a new interval, regardless of waitingFor. A failed/unreadable look discards the affected observation, so unobserved time never proves90 unchanged seconds. At90 or more awake seconds with the same identity/heartbeat, request the own Root's stop --force. A pending normal stop or retained stop manager is joined/serialized first; never start two stop managers for the same Root/Exchange. A force reason is retained until it can run serially. Immediately before launching force, obtain a successful listing begun after those waits and recheck the same process identity/heartbeat and90-second interval. If the heartbeat advanced, the process/end changed or the look failed, cancel that force reason without inventing an ended reply. A normal stop that was still pending and then confirms an end resolves that queued force reason; its interrupted result is not mislabeled as caused by the stuck force. A user stop joining a cancelled force continues as an ordinary stop. Only a matching own-Root/Exchange interrupted reply creates ended_stuck; completed/failed/cancelled/saved/none never does. The backend signals no Trunk itself and never kills an unresolved mutation.

A successful force's note is first published atomically as a private own-Root notes/<UUID>.json file, then inserted into the existing exchange_notes table within a5-second whole-operation bound. This write-ahead use of the specified fallback file closes the crash gap before SQL. Its JSON is bounded to4KiB of UTF-8 including LF, enough for these fixed metadata fields: root, exchange, chat, kind=ended_stuck and an absolute at timestamp; no transcript. Use owner-owned private no-follow regular files/directories, exclusive temporary publication and inode-checked removal; never replace a different existing note silently. Publication uses an exclusive temporary name and atomic no-replace hardlink, then removes its temporary link and syncs the directory. If a crash leaves exactly one private canonical-note temporary link to the same inode, validate the complete matching note and both names before removing only that temporary link; any unknown extra hardlink is refused. This keeps a published note recoverable at every crash boundary. Startup/recovery enumerates only canonical matching files, skips malformed/unsafe entries without deleting them and retries SQL idempotently. Keep the file through a SQL failure/timeout or a still-open/missing Exchange, then remove only our unchanged file once the interrupted row and matching durable note are confirmed. An actual different saved end cannot acquire a stuck note. A settle completion requests another note flush, because the row may still be open when recovery first requests settling. Pending file metadata and confirmed notes can supply the chat note event; database snapshots remain the authority for saved state.

Discovery runs at startup and on roots.list. It shares one in-flight listing per Root with the own-Root look and eligible-settle observer. Catalogue entries come only from arbol-roots list. Each Root is listed through its own named arbol-root launcher with an explicit validated Root; the backend reads no foreign Root file or database. At most8 independent listing calls run together; the discovery operation has a25-second total bound inside the window's30 seconds. Every catalogue Root retains its own result or safe per-Root error, including a bounded no-answer for unfinished looks, so one failure hides no other result. Project only published listing metadata, retaining unknown nonempty state/waiting strings and safe end diagnostics; no chat content or arbitrary producer fields are returned. A malformed identity makes only that Root's listing fail. Valid entries remain available beside a safe per-Root error when its unreadable array is nonempty. The combined reply reserves the complete Bridge framing bound; an entry whose listing would exceed the remaining16MiB budget keeps its Root record and a safe no-answer error rather than failing every Root. Shared listing capacity is global to the backend, including the own-Root watcher, and a timed-out Discovery caller does not cancel a listing another observer shares. A bare Exchange UUID never implicitly selects a Root.

Root command process identities include their explicit Root as well as kind and Exchange key; own-Root existing keys remain compatible and foreign keys carry an unambiguous Root prefix. Programs permits an explicit different Root only for list/stop/settle and never accepts a --root argument smuggled through args. Other commands remain own-Root. exchange.stop gains an optional root parameter: omission means this backend's Root; a different Root must be present in a fresh valid catalogue and is sent to that Root's manager. Concurrent stops/retained children coalesce by Root and Exchange, even if two Roots contain the same UUID. Foreign stops publish no own-chat status and read no foreign history. exchange.answer/send remain own-Root. A deleted or unknown explicit Root is a safe refusal, never a fallback to current Root.

Settling queues are per explicit Root. Valid unaccepted/unsaved/interrupted discovery entries request that listed Root's queue; startup and database return request the own queue. Each queue has one mutation and at most one pending further pass, respects the120-second actual command bound, and waits for a retained manager's real exit. No queue launches while the backend's own database is unreachable; the foreign manager/Trunk remains responsible for its own database outcome, which this backend cannot inspect. There is no timer retry absent a new reason. Stuck detection remains own-Root only; discovery does not authorize automatic force in another Root. All recovery/force/settle tasks are owned by the backend, safe on caller cancellation and bounded shutdown. Real retained-Root/vendor/Swift/renderer journeys remain SYL-257.

<!-- sources:
arbol:src/arbol_backend/health.py#Health
arbol:src/arbol_backend/health.py#Health.probe
arbol:src/arbol_backend/database.py#Unavailable
arbol:src/arbol_backend/database.py#Session.execute
arbol:src/arbol_backend/database.py#Database.session
arbol:src/arbol_backend/chats.py#Chats.observe
arbol:src/arbol_backend/live.py#Live.observe_rows
arbol:src/arbol_backend/live.py#Live.observe_saved
arbol:src/arbol_backend/live.py#Live.step
arbol:src/arbol_backend/live.py#Live.note
arbol:src/arbol_backend/note_files.py#NoteFiles
arbol:src/arbol_backend/notes.py#Notes
arbol:src/arbol_backend/listings.py#Listings
arbol:src/arbol_backend/discovery.py#Discovery
arbol:src/arbol_backend/process.py#Programs.command_key
arbol:src/arbol_backend/process.py#Programs.call
arbol:src/arbol_backend/controls.py#Controls.run_force
arbol:src/arbol_backend/controls.py#Controls.force
arbol:src/arbol_backend/controls.py#ForceCancelled
arbol:src/arbol_backend/stuck.py#Stuck
arbol:src/arbol_backend/stuck.py#awake
arbol:src/arbol_backend/recovery.py#Recovery
arbol:src/arbol_backend/settling.py#Settling
arbol:src/arbol_backend/server.py#Backend.__init__
arbol:src/arbol_backend/server.py#Backend.run
arbol:tests/backend/test_health.py#Availability
arbol:tests/backend/test_offline_live.py#Offline
arbol:tests/backend/test_note_files.py#Files
arbol:tests/backend/test_notes.py#Recovery
arbol:tests/backend/test_discovery.py#AcrossRoots
arbol:tests/backend/test_stuck.py#Watching
arbol:tests/backend/test_return.py#Returned
arbol:tests/backend/recovery_support.py#offline
arbol:tests/backend/recovery_support.py#online
arbol:tests/backend/discovery_support.py#install
-->

### Stuck Exchanges

An Exchange is *stuck* when its process is alive and does nothing ([ARC-3](../architecture/03-stuck-trunks.md)). The backend looks from outside, as the second line of defence of ARC-3:

1. Every 30 seconds it runs `arbol-root --root <root> list`. For each Exchange whose process lives, in the state `accepting`, `running` or `ending`, it keeps the heartbeat and the time of the first look that found that value. The *heartbeat* is the counter of its signs of life (RCT-1).
2. An Exchange is stuck when a later look finds the same heartbeat at least 90 seconds after that time. For example, looks at 0, 30, 60 and 90 seconds that all find the heartbeat 41 make the Exchange stuck at the fourth; a look at 60 seconds that finds 42 starts the count again.
3. It ends a stuck Exchange without asking ([ARC-D57](../architecture/03-stuck-trunks.md#decisions)) with `arbol-root --root <root> stop --force <exchange>`. The Root manager ends the Trunk's processes and has the Exchange settled as interrupted, with what had arrived (RTM-0). When the stop replies `interrupted`, the backend writes a note into its table `exchange_notes` that the Exchange was ended because it was stuck; when the Trunk had written its end just before, that end stands (RCT-2), and no note is written. When the note cannot be written within 5 seconds, the backend keeps it as a file `notes/<exchange>.json` of the mode 0600 in the Root's folder, and writes it into the table, and removes the file, once the database is back, also after a restart.
4. The window shows the note under the Exchange: "Ended because it was stuck" ([BKD-2](02-elma-chat.md#the-status-of-an-exchange)). The chat takes a new message afterwards (ARC-3).

The 30 and the 90 seconds are counted with the clock that macOS calls `CLOCK_UPTIME_RAW`, which stands still while the Mac sleeps, so that waking the Mac makes no Exchange look stuck ([ARC-3](../architecture/03-stuck-trunks.md#two-lines-of-defence)). A heartbeat that goes on is never stuck, whatever the Exchange waits for: an answer of the Leather Bag or a command the agent runs is never ended for taking long, and the window shows what it waits for and for how long (ARC-D61).

The same listing gives every window the states and the signs of life of its Exchanges, and is the listing after which settling runs. The backend of a Root looks only at its own Root, and only while it runs: a Root whose backend has ended has only the Trunk's watch on itself (ARC-3).

### Restarts and discovery across Roots

The backend keeps nothing that a restart would lose, except one mark in memory: which Exchanges it is stopping. A note it could not yet write is a file (above). When it ends, no Exchange stops: the Exchanges run detached (RCT-2), and a start, a stop or a settle it began goes on in its own process group. At its next start it settles, lists and reads everything again, so what was produced meanwhile is shown ([ARC-2](../architecture/02-chat-exchange-across-components.md#when-arbol-quits)). A newer Build of the same Root, or a newer Build of `arbol-root`, finds the same Exchanges, because they are known only from their records; no Exchange changes its Root or its Trunk Build ([ARC-1](../architecture/01-roots.md#what-a-root-is)).

**Discovery across Roots.** Every backend finds the running work of every Root, also of a Root that is not current and has no window open, at its start and when a window asks ([ARC-1](../architecture/01-roots.md#discovery-across-roots)):

1. It runs `arbol-roots list` for the records of the retained Roots.
2. For each, it runs `arbol-root --root <identifier> list`: the launcher picks that Root's newest working Build of `arbol-root` (BLD-0). It never applies its own Root's manager to another Root.
3. It puts the listings together, because each entry names its Root ([RTM-0](../../arbol-root/specs/00-the-commands.md#the-listing)), and keeps beside each Root what failed: a refusal, no answer, or a listing it could not read. A Root that fails hides no other Root.

The result gives each Root with its state, whether it is current, and its Exchanges in progress with their chat, Trunk, Build, state and signs of life. It holds no chat content: what a chat says is read only by the backend of the chat's own Root, from its own database (ARC-1). A command for an Exchange, such as a stop or a settle, goes to the manager of the Root its listing names, such as `arbol-root --root <that Root> stop <exchange>`.

### When the database cannot be reached

The database is *unreachable* when a new connection, or `SELECT 1` on it, does not succeed within 5 seconds, or the Keychain fails otherwise than with the exit status 44 or does not answer within its 2 seconds. A statement that passes its 5 seconds on a server that answers fails only its own call, with `timeout`, and the database is not marked. A database that does not answer is not a normal state ([ARC-D53](../architecture/02-chat-exchange-across-components.md#decisions)):

| | |
|---|---|
| Noticing | The first call that finds it so marks the database unreachable, with the cause in plain words, such as "The database server does not answer at 127.0.0.1:5433" or "The Keychain did not answer for the database's password". From then on the backend tries to connect every 5 seconds |
| Attention | For as long as it lasts, every window of the Root shows it with the cause, as an *attention* item ([BKD-1](01-the-bridge.md#attention)) |
| Sending | A message is refused by the Trunk with `database_unavailable`, and its Draft stays in the composer (RCT-2); saving a Draft fails with `database_unavailable`, and the window keeps it and sends it again later ([BKD-2](02-elma-chat.md#the-composer)) |
| Reading | A chat the window already shows stays shown. A chat that is opened is refused with `database_unavailable`. Exchanges in progress go on being followed from their folders, which need no database |
| Not yet saved | An Exchange whose record has an end and whose process is gone ended while the database was away. The backend shows its answer from the folder, marked `unsaved`, until settling has saved it ([ARC-D53](../architecture/02-chat-exchange-across-components.md#decisions)) |
| Back | At the first connection that succeeds, the backend clears the attention item, runs `arbol-root settle`, writes the notes it kept as files, and sends a new snapshot on every subscription (BKD-1) |

### Accounts

The backend calls the Drivers' account commands directly; Root and Trunk have no part in it ([ARC-0](../architecture/00-components-and-boundaries.md#accounts), [DRV-1](../driver-contract/01-subscriptions.md)). The Drivers are those whose launcher `arbol-<driver>-driver` is in the folder of the launchers: `claude`, `codex` and the accepted `pi` Driver; the `driver` of a route names one of them (TRV-0).

| The window asks for | The backend runs |
|---|---|
| Every Subscription of every Driver, with its state and its last usage, for the route rows | `arbol-<driver>-driver subscriptions list` for each Driver |
| One Subscription checked, its usage, its models | `subscriptions check <id>`, `subscriptions usage <id>`, `subscriptions models <id>` |

These are the only commands of a Driver the backend runs: it never starts a run, and it never signs in or out (ARC-0). Until Seqoya Lab has a page for it, the Leather Bag signs in with the Driver's own command at the terminal, such as `arbol-claude-driver subscriptions sign-in zai`, which shows its steps itself and reads a key from the Keychain item it names ([BKD-D17](02-elma-chat.md#decisions), [BKD-D10](#decisions)). No secret passes through the backend or the Bridge.

### The working folder of a chat

Version 1 gave a chat the repository's own checkout, so two chats on one repository changed the same files. Now `~/repos/sylvan-stack/<repository>/` is the owner's own folder, the ten named work areas such as **Badger Workspace** at `~/repos/sylvan-stack/badger/` each hold a clone of every repository and are taken by a hold, and `~/repos/sylvan-stack/readonly/` holds the last merged `main` of every repository and is never edited (the guide Working in Sagas). The animal paths are aliases to the existing color folders; running agents and existing holds keep their paths (the owner's decision of 26 October 2026). As the owner decided ([BKD-D4](#decisions)):

| | |
|---|---|
| A new chat | Works in the repository's folder in `readonly/`, such as `~/repos/sylvan-stack/readonly/arbol-trunk`, or in `readonly/` itself for the stack as a whole. Arbol takes no work area for it. A folder picked with "Other…" is used as it is |
| An agent that has to change files | Books a work area with the booking tool, when it needs one, and works there; the hold names the chat (AGR-D11), so that the agent finds its folder again at the chat's next message. The tool is not part of Arbol: it belongs with the holds and the named work areas of the guide Working in Sagas, and is built in a task of its own |
| The chat's folder | Stays as it is for every message, also after the agent booked a work area, because a Driver continues its saved conversation only in the same folder (TRV-0). The agent learns its Root and chat from `ARBOL_ROOT` and `ARBOL_CHAT` (AGR-D11, SYL-207) |

For example, a chat started with ⌘2 on `arbol-trunk` reads `~/repos/sylvan-stack/readonly/arbol-trunk`. Asked to fix a test, its agent books **Fox Workspace** at `~/repos/sylvan-stack/fox/` for the chat, works in `fox/arbol-trunk` on a branch of its own, and a second chat on `arbol-trunk` that only answers questions books nothing. More chats than named work areas can be open at once, because only the chats that change files take one.

### Health and storage

The chats of every Root are in one PostgreSQL server on this Mac, in its data folder `~/Library/Application Support/Arbol/database/data` ([ARC-D64](../architecture/00-components-and-boundaries.md#decisions)). The backend reports its health and how much space it takes, and warns before space runs out ([ARC-0](../architecture/00-components-and-boundaries.md#the-database-server)). It measures at its start, every 5 minutes, counted with `CLOCK_UPTIME_RAW`, and when a window asks:

| Measure | How |
|---|---|
| The server | Whether a connection and `SELECT 1` succeed within 5 seconds, and if not, why |
| The size of each Root's database | `pg_database_size` of the database each retained Root's `root.json` names, asked on the backend's own connection. This reads the server's catalogue and opens no other Root's database (ARC-1) |
| The data folder | Its size on disk, which holds every database and the server's own files |
| The free space | The free space of the disk that holds the data folder |

| Free space on that disk | The backend |
|---|---|
| Less than 10 GiB | Shows an attention item in every window: the free space, the data folder's size and the largest database, for example "8.6 GiB left on the disk of the database. First Sapling's chats take 3.2 GiB" |
| Less than 2 GiB | The same, marked urgent |

The figures are proposed in [BKD-D11](#decisions), with their basis.

For example, the reply of a measurement:

```json
{
  "measuredAt": "2026-10-18T09:00:00.000Z",
  "server": { "ok": true },
  "roots": [ { "root": "sapling", "name": "First Sapling", "database": "arbol_sapling", "bytes": 3435973837 } ],
  "dataFolderBytes": 3758096384,
  "freeBytes": 9234179072,
  "warning": "low"
}
```

### Its program and its Build

The backend is typed Python in the repository `arbol`, beside `arbol-builds` and `arbol-roots`, with a packaged interpreter, as every component is (ARC-0, BLD-0). It is built with `arbol-builds build arbol --root <root>` into a Build of `arbol` made for that Root (BLD-0, RTM-D9). The Build also carries the renderer bundle of Elma Chat, built from the same repository ([BKD-2](02-elma-chat.md#its-renderer-bundle)):

```text
~/Library/Application Support/Arbol/builds/arbol/6/
  build.json               "root": "sapling"
  bin/arbol                the program: backend, and the command line of SYL-193
  ui/elma/index.html       the renderer bundle of Elma Chat, which the Swift App loads into a window
```

It serves its Bridge with one task for each window and for each call, so no call to the database or to another program holds up another (ARC-2). Each window's connection and each call can fail on its own without ending the backend.

<!-- sources:
arbol:arbol-build.json
arbol:scripts/package_backend.py#package
arbol:scripts/backend_package.py#verify
arbol:scripts/check_backend.py#main
arbol:bin/arbol
arbol:bin/arbol_entry.py
-->

### Process foundation choices

SYL-246 settles these technical details before implementation (BKD-D27). The backend is an asyncio process. Each socket connection owns a task; the Bridge will supply its wire handling in SYL-248. This foundation keeps accepted connections alive and monitors Root metadata while they exist, without inventing a second wire protocol. Startup prints ready before launching background database/current-Root/settle work. Stuck/discovery/attention and Bridge publication stay in their named later Beats.

Development requires `--root <identifier>`; a packaged program reads its adjacent Build record, validates component/entry/version/number/Root and accepts only an agreeing explicit Root. The Root record must be a readable regular object for the same identifier and a supported state (preparing/working/failed). A duplicate lock reports the recorded owner's PID. Lock and socket are private, non-inheritable, and held for the process lifetime. Only a stale socket is unlinked under the lock; a regular file or symlink at that path is refused. Cleanup removes only the socket this process bound. SIGTERM/SIGINT/pipe EOF close clients and cancel local tasks within two seconds, never sending a signal to an Exchange or an unresolved start/stop/settle child.

Child calls go through the named launchers in the bin folder, with that folder first in PATH, stdin closed, close_fds and a fresh session/process group. Child output goes to a private anonymous temporary regular file, read with pread without moving the writer’s file position. Each call stays independent and captures at most 1 MiB in memory. The anonymous file remains writable through the child’s own descriptor after the backend ends, so shutdown cannot deliver SIGPIPE to an unresolved mutation; it disappears when the last descriptor closes. The backend does not claim to bound a faulty long-running child’s total output on disk. Exact production deadlines remain the command table's 25/90/120/10 seconds. A timeout of a listing/account call kills its entire group; a timed-out start/stop/settle remains tracked and cannot be duplicated for its identity until the observed process exits. Output is never allowed to keep the backend alive after its own shutdown; closing its local descriptor leaves the child’s independent descriptor valid and is no claim that the child failed or rolled back. Tests may inject shorter deadlines only through Python helpers, never user-facing options. Drivers include Pi's accepted account launcher as well as Claude/Codex; no inference command is offered by this helper.

Use pinned `psycopg[binary]==3.3.6` with its self-contained libpq, on the existing pinned Python. Each database operation gets its own async autocommit connection; a snapshot owns one explicit REPEATABLE READ READ ONLY transaction. Connect and each SQL statement have a five-second async deadline plus PostgreSQL statement_timeout=5000, with timeout distinct from database_unavailable. Close the connection on cancellation/error and never expose connection strings, passwords or server error text in public exceptions. Explicit private --database bypasses owner config and Keychain. Otherwise validate the database address object, replace only its database with the Root's own database, and read only the named role's database Keychain item with /usr/bin/security (two seconds; exit 44 means no password). At process entry remove inherited PG* environment settings so libpq cannot select another service, address, password or options. Supply an explicit password and a newly made private empty temporary passfile (removed at shutdown), never the owner’s default passfile. Child launchers likewise receive no inherited PG* settings; their own Root/Driver configuration decides their database. No schema change is performed by the backend.

Settings are read once from the selected settings folder. Missing arbol.json/fields yield empty defaults; present route objects keep optional driver/subscription/model/effort strings, including per-repository and small-call routes. Malformed present JSON or a malformed known field is invalid_input; unknown future fields are ignored. No Brain Recipe or vendor catalogue call is invented here. The test harness always supplies root/bin/settings/database paths, runs a socket-only temporary PostgreSQL cluster, and copies the merged readonly Root Contract layout as its immutable input. A package carries that exact test input, its own pinned interpreter and pinned binary dependencies; no code from another component is imported.

### Tests

A test runs the Builds of the Root it tests on a folder and a database of its own, named with options ([ARC-1](../architecture/01-roots.md#a-place-for-tests)):

| Option of `arbol backend` | In place of | What it names |
|---|---|---|
| `--root-dir <folder>` | `~/Library/Application Support/Arbol/roots/<root>/` | The Root's folder, with its `root.json`, `exchanges/` and the socket |
| `--bin-dir <folder>` | `~/.local/bin` | The folder of the launchers, where a test puts stand-ins of `arbol-root`, `arbol-roots` and the Drivers |
| `--settings-dir <folder>` | `~/.arbol/roots/<root>/` | The folder of `arbol.json` |
| `--database <address>` | The address of `~/.arbol/database.json` and the database of `root.json` | A database on a server of the test's own, such as `postgresql://bkd@%2Ftmp%2Fbkd-1a2b/arbol_test` |

`--root-dir` is refused without `--bin-dir` and `--database`, so that a test that names another Root folder cannot start a real Trunk or reach the chats of a Root in use, as RTM-0 refuses it for the Root manager.

<!-- sources:
arbol:tests/backend/support.py#Frame
arbol:tests/backend/support.py#Cluster
arbol:tests/test_backend.py#SQL.test_connect_deadline_and_shutdown_during_handshake
-->

### Backend tables in layouts and migration

SYL-247 settles the concrete additions before code (RTM-D31, BKD-D28). Both roots/sapling/layout.sql and roots/jensen/layout.sql append the exact commented drafts_revision sequence and four tables of BKD-0; no earlier statement or comment changes. Layout validation admits repeatable CREATE SEQUENCE IF NOT EXISTS and COMMENT ON SEQUENCE alongside the existing table/index/column forms, and verifies sequence comments as well. Older schemas/rows and every existing sequence definition are preserved; this new counter is bigint, ascending by one, no cycle, cache one. Compatibility and repeated-layout checks use real retained earlier same-Root Builds privately before installation.

Whole migration copies all four backend tables byte-for-byte in the same READ ONLY REPEATABLE READ snapshot as chat history, including chat/repository Drafts and pending send fields. It also exports drafts_revision's last_value/is_called and definition as a fixed binary file. Sequences are not MVCC snapshots: the read may include consumption newer than the row snapshot, so a safe counter can skip values. It never calls nextval or changes the source. Source and target must have the complete backend layout; missing or incompatible tables/counter fail with status 3 rather than guessing empty data.

The target validates that one source counter row has the expected bigint/unit-increment/cache-one/no-cycle definition. It takes the sequence's transactional ALTER lock (ALTER SEQUENCE drafts_revision CACHE 1), then reads the target's latest state and calculates the next value as the maximum of one, every copied revision plus one, and the source/target last_value plus one only when is_called. Refuse exhaustion before allocating or writing an out-of-range value. ALTER SEQUENCE ... RESTART WITH applies that next value in the target's one transaction, so late failure rolls back rows and the restart together. Do not use setval: its effects survive rollback and max(revision) alone could reuse a revision consumed by a deleted Draft. Concurrent nextval calls are blocked until commit/rollback, with the normal bounded lock timeout. The source read and the target copy never alter another Root's counter. PostgreSQL's documented transactional RESTART and ALTER locking are qualified by rollback/concurrent-allocator tests.

In-use comparison remains stale-only: every backend row and counter is unchanged. One-chat reimport copies exchange_notes with the imported history and remaps its Exchange IDs together; replacing an uncontinued copy removes only notes on that replaced history, while a continued copy and all its notes survive beside the new copy. Drafts, chat_settings and chat_marks are local input/preferences in a Root. Reimport never overwrites or copies those rows: an existing copy keeps them byte-for-byte, a newly imported copy starts without them, and repository Drafts plus the revision counter never change. This keeps the UI's saved current Draft meaningful and never schedules the other Root's pending send. Before replacing history, lock the existing target chat Draft and refuse an unresolved sent_as with busy (55P03); the owner can settle/save that Draft first. Source notes require the complete source backend layout, and every failure/collision remains one-transaction rollback. Whole migration, not one-chat reimport, carries all backend rows as the accepted first migration requires. Backend/UI code that consumes these choices stays in SYL-249/250/256/257.

The [PostgreSQL sequence functions](https://www.postgresql.org/docs/17/functions-sequence.html) and [ALTER SEQUENCE](https://www.postgresql.org/docs/17/sql-altersequence.html) define the counter behavior. Tests use only check-owned clusters, layouts and fictional data. Actual installed work makes new merged-source manager Builds for Sapling and Jensen and applies additive layouts only, proving all older data/current selection unchanged; no whole production migration or vendor call is needed.

<!-- sources:
arbol-root:roots/sapling/layout.sql
arbol-root:roots/jensen/layout.sql
arbol-root:roots/jensen/migrate.sql
arbol-root:scripts/backend_tables.py#rows
arbol-root:scripts/backend_tables.py#seed
arbol-root:scripts/backend_tables.py#next_draft
arbol-root:scripts/check_layout.py#run_layout
arbol-root:scripts/check_migration.py#run_migration
arbol-root:scripts/chat_migration_check.py#backend_modes
arbol-root:scripts/migration_protocol.py#mode_protocol
arbol-root:scripts/sql_statements.py#layout_statements
arbol-root:tests/test_backend_tables.py#BackendTables
arbol-root:tests/test_backend_tables.py#OperationalBoundary
arbol-root:tests/test_layout_check.py#LayoutCheck.test_a_sequence_requires_its_comment_and_a_repeatable_create
arbol-root:roots/sapling/drills/backend_layout_drills.py#state
arbol-root:roots/sapling/drills/backend_layout_drills.py#preserved
arbol-root:roots/sapling/drills/backend_layout_drills.py#run
arbol-root:roots/sapling/drills/drill-backend-layouts.py
-->

## Requirements

The process:

| ID | The Arbol backend must… | Origin | Verified by |
|---|---|---|---|
| BKD-0.1 | be the command `backend` of a Root's `arbol` Build, work on the Root its Build record names, refuse a Root whose folder holds no readable `root.json` and a socket path longer than 103 bytes, run once for each Root by an exclusive lock on `backend.lock`, remove a socket file a dead backend left, listen on `backend.sock` of the mode 0600 in the Root's folder, hand neither the lock nor the socket to a program it starts, print one ready line once it listens, and on SIGTERM, on SIGINT and when its standard input is a pipe that reaches its end, close its connections, remove its socket and end within 2 seconds | Changed | unit `backend.process-lock`, `backend.shutdown`, `backend.identity-isolation`, `backend.socket-path`, `backend.descriptor-ownership`, `backend.build-identity`; private Build `backend.name-only-build` |
| BKD-0.2 | start for a Root in any state that is named, a failed one included, and serve its windows for as long as its folder, its database and its Builds exist | New | unit `backend.identity-isolation` starts preparing/working/failed; private Root-scoped Build `backend.name-only-build`; UI journey remains SYL-257 |
| BKD-0.3 | take the current Root from `arbol-roots list` whenever it needs it, store it nowhere, run no listener unless its Root is current, and tell every window within 5 seconds when its own Root's state or display name changed | New | unit `backend.root-observation`, `bridge.root-observation`, `bridge.root-catalogue`, `bridge.root-get`; no listener is implemented |
| BKD-0.4 | start `arbol-root`, `arbol-roots` and the Drivers only through their launchers, with the folder of the launchers first on the search path, each in a process group of its own; wait for none longer than its time limit, end a listing or an account command at its limit, and start no second settle of a Root, no second stop of an Exchange and no new look while one runs | New | unit `backend.launcher-boundaries`, `backend.child-deadlines` (exact production limit table plus private shorter injected waits) |
| BKD-0.30 | read the defaults of `~/.arbol/roots/<root>/arbol.json` at its start, the default route, each repository's default route and the small-call route, a missing file or a missing field being no error, and use no Brain Recipe | Changed | unit `backend.settings` |

The database:

| ID | The Arbol backend must… | Origin | Verified by |
|---|---|---|---|
| BKD-0.5 | read the chat tables directly with SQL of its own, as RCT-3 puts a chat together, leaving out every Exchange that was replaced, read a chat, a page of chats and a snapshot each in one `REPEATABLE READ READ ONLY` transaction and commit every other statement at once, and open no database but its Root's | Changed | unit `chats.contract-assembly`, `chats.consistent-snapshot`, `chats.exchange-pages`, `chats.page-cursor`, `chats.own-root-provenance`, `chats.read-only-contract` |
| BKD-0.6 | create, change and remove no table, column, index or check, use for its own rows only the tables of the Root's own layout that `arbol-roots` runs, and serve a Root whose database lacks them without Drafts and notes, with the attention item `layout_incomplete` | New | layout/migration: SYL-247 checks and installed `sapling.backend-layouts`; backend: unit `chats.no-ddl`, `chats.layout-inspection`, `chats.layout-degraded`, `chats.layout-wire`, `chats.provenance-layout`; Draft mutation unit `sending.no-ddl-history-writes`, `drafts.validation`; database recovery remains SYL-252 |
| BKD-0.7 | have its own tables changed within a Root only by additions to the Root's own layout that the Root's older Builds can ignore (RTM-1.5), and its settings file only by fields older Builds can ignore | New | layout/migration part: `root.backend-layouts`, `root.backend-whole`, `root.backend-counter-rollback`, `root.backend-counter-lock`, `root.backend-empty-counter`, `root.backend-chat-state`; installed additive check `sapling.backend-layouts` (SYL-247). Backend missing-layout serving/read/write behavior is checked by `chats.layout-wire`, `sending.no-ddl-history-writes`; database recovery remains SYL-252 |
| BKD-0.8 | write in the chat tables only `chats.title`, when the Leather Bag gives a chat a title or takes it away: the text without spaces at its ends, NULL when nothing is left, and never a placeholder | Changed | unit `chats.title-windows`, `chats.read-only-contract`, `chats.input-types` |
| BKD-0.9 | read the database password as a Trunk does, with the exit status 44 meaning no password, give every call to the database a time limit of 5 seconds, fail a statement that passes it with `timeout`, and serve each window and each call in a task of its own, so that no call holds up another | Changed | unit `backend.keychain`, `backend.database-identity`, `backend.connect-timeout`, `backend.database-deadlines`, `backend.database-away-start`, `bridge.calls`, `chats.observer-isolation`, `chats.migration-check-coalescing` |

Drafts and sending:

| ID | The Arbol backend must… | Origin | Verified by |
|---|---|---|---|
| BKD-0.10 | keep in its table `drafts` one Draft of the reply for each chat and one Draft of a new chat for each repository folder, holding the text; replace it whole only over the revision the window last saw, with a revision from one counter, and refuse any other save with `draft_conflict`; mark it with the Exchange it is sent as and clear the mark on a save or a refusal; remove it once that Exchange is accepted, or later when it reads a mark the chat tables hold; and refuse a Draft or a message of more than 1 MiB | Changed | unit `drafts.scope-counter`, `drafts.cas-races`, `drafts.conflict-null`, `drafts.validation`, `drafts.utf8-boundary`, `drafts.subscriptions`, `drafts.sent-mark`, `drafts.accepted-recovery`, `drafts.newer-text`, `drafts.cleanup-cas`, `drafts.capture-acceptance-race`, `sending.repository-draft`, `sending.refusal`, `sending.database-cleanup-recovery` |
| BKD-0.11 | send a message by writing a request file with the chat, the message, the route, the working folder and the small-call route of `arbol.json` when it names one, into `requests/` of the Root's folder, and running `arbol-root --root <root> start --exchange <id> --request <file>` with the Exchange identifier the window chose; refuse with `invalid_input`, before it touches a file or starts a program, an identifier that is not a lower-case UUID, a route without a Driver found among the launchers, a Subscription and a model, a working folder that is not an absolute path to a folder that exists, and an empty message | Changed | unit `sending.validate-before-effects`, `sending.ownership`, `sending.mark-before-start`, `sending.accepted`, `sending.private-request`, `sending.request-path-safety`, `sending.request-inode`, `sending.request-write-failure`, `sending.request-startup-cleanup` |
| BKD-0.12 | count a message as accepted only on its acceptance line, pass every refusal on with its code and message and keep the Draft, take nothing, `no_answer` and `in_progress` as no refusal and run the same start again with a request file written anew 15 seconds after the previous attempt returned, never two at once, until 120 seconds after the first, and join a second call for an Exchange it is starting to the first | Changed | unit `sending.acceptance-shape`, `sending.error-shape`, `sending.result-validation`, `sending.refusal`, `sending.safe-errors`, `sending.repeat`, `sending.shared-dispatch`, `sending.retry-schedule`, `sending.no-concurrent-start`, `sending.total-bound`, `sending.uncertain-mark`, `sending.disconnect`, `sending.detached-shutdown`; actual production25/15sec private-process check `sending.production-25-15`. Root/Trunk/vendor/UI journey remains SYL-257 |
| BKD-0.13 | send a message again only with `--replaces`, for the Exchange the window names, with the replaced Exchange's working folder and the route the Leather Bag picks, and pass a refusal `cannot_replace` on | Changed | unit `sending.send-again`, `sending.cannot-replace`; Root/Trunk replacement eligibility already belongs to RCT-2; real backend journey remains SYL-257 |
| BKD-0.14 | keep a failed, stuck or cancelled Exchange to its own chat: serve every other chat meanwhile, and take a new message for the chat as soon as its Exchange has ended | Changed | unit `sending.chat-isolation`, `sending.after-ended-exchange`; live folder following is qualified by BKD-0.15 below; automatic stuck/recovery and actual window presentation remain SYL-252/SYL-257 |
| BKD-0.31 | keep for each chat, in its tables `chat_settings` and `chat_marks`, the route and the working folder picked for its next message, whether it is ongoing and when it was archived, saving a choice at once, also while its agent works, and mark a chat ongoing whenever a message of it is accepted | Changed | choice/marks part: unit `chats.atomic-settings`, `chats.atomic-marks`, `chats.mutation-publication-order`, `chats.title-windows`, `chats.archive-list`, `chats.identifier-catalogues`, `chats.additive-driver-catalogue`; ongoing-on-acceptance unit `sending.accepted`, `sending.repository-draft`, `drafts.accepted-recovery` |
| BKD-0.32 | save a pasted text of 10,000 characters or more as a file of the mode 0600 in the folder `pastes/` of the Root's folder, and give the window its path | Kept | unit `chats.paste-private`, `chats.paste-paths`, `chats.paste-wire` |
| BKD-0.33 | compare migrated copies through the owning Root’s supported global command at startup/list opening, serve local data and expose truthful provenance/stale/failure state, and delegate one-chat reimport without direct cross-Root SQL or an automatic ambiguous retry | New | backend unit `chats.migration-check-coalescing`, `chats.migration-unavailable`, `chats.own-root-provenance`, `chats.provenance-layout`, `chats.reimport-results`, `chats.reimport-local-input`, `chats.reimport-coalescing`, `chats.reimport-validation`, `chats.reimport-uncertain`, `chats.migration-errors`; core SQL/CLI SYL-195/SYL-247; UI drill remains SYL-257 |

An Exchange in progress:

| ID | The Arbol backend must… | Origin | Verified by |
|---|---|---|---|
| BKD-0.15 | read an Exchange's row first and, while it is open, only its message from the tables and its answer from its folder, as RCT-1.9 and RCT-1.10 say: `events.jsonl` from its first line and each new whole line at least every 250 milliseconds while a window follows it, passed on at most every 50 milliseconds, leaving out when it catches up the pieces of a block or a tool call that is whole in the file, and the row again once the folder is gone; and while a window follows the Root's chats, read the names and records in `exchanges/` and check their processes once a second | Changed | unit `live.row-first`, `live.old-ended-folder`, `live.windows`, `live.replay`, `live.compaction`, `live.cutoff`, `live.partial-line`, `live.forward-compatibility`, `live.malformed-lines`, `live.oversized-line`, `live.bounded-file-memory`, `live.streaming-metadata`, `live.oversized-wire`, `live.batch-boundary`, `live.poll-latency`, `live.snapshot-generation`, `live.truncated-file`, `live.outside-folder`, `live.shared-process-observation`, `live.saved`, `live.private-files`, `live.records`, `live.record-validation`, `live.record-privacy`, `live.process-identity`, `live.process-environment`, `live.process-failure`, `live.slow-window-isolation` (SYL-251); real/UI journey SYL-257 |
| BKD-0.16 | on a stop, mark the Exchange `stopping` from the request until it has ended, run `arbol-root --root <root> stop <exchange>` once however many windows ask, waiting for a start of it under way to return, and reply with the `ended` it printed | Changed | unit `stop.shared`, `stop.confirmed-end`, `stop.no-fabricated-save`, `stop.wait-start`, `stop.production-limits`, `stop.start-wait-timeout`, `stop.shielded`, `stop.retained-manager`, `stop.repeat`, `stop.forwarding`, `stop.safe-errors`, `stop.result-identity`, `stop.shutdown` (SYL-251); actual Root/Trunk/window journey SYL-257 |
| BKD-0.17 | write the Leather Bag's answer to the agent's question only after checking it against the question's form, as one whole line of at most 64 KiB with one write on `control` opened for appending, never create the file, wait up to 15 seconds while only `.<exchange>.new` exists, and refuse with `ended` when neither is there | Changed | unit `answers.form`, `answers.one-write`, `answers.no-free-text`, `answers.invalid-form`, `answers.current-ask`, `answers.observed-delivery`, `answers.nested-asks`, `answers.publication`, `answers.ended`, `answers.byte-limit`, `answers.short-write`, `answers.syntax-before-effects`, `answers.file-identity`, `answers.no-create` (SYL-251); actual Root/Trunk/window journey SYL-257 |
| BKD-0.18 | run `arbol-root --root <root> settle` when it starts, when it sees the database return and after a listing that shows an Exchange `unaccepted`, `unsaved` or `interrupted`, its own Root's or another's, one at a time for each Root and none while the database is unreachable, and show such an Exchange as `gone` until it is settled | Changed | own-Root unit `settle.startup`, `settle.coalescing`, `settle.production-limit`, `settle.database-gate`, `settle.no-timer-retry`, `settle.retained-manager`, `settle.no-overlap`, `settle.listing-reasons`, `settle.own-root`, `settle.shared-listing`, `settle.dead-observation`, `settle.gone-until-saved`, `settle.failure`, `settle.shutdown` (SYL-251); database-return/cross-Root recovery remains SYL-252, actual journey SYL-257 |

Stuck Exchanges:

| ID | The Arbol backend must… | Origin | Verified by |
|---|---|---|---|
| BKD-0.19 | list its Root's Exchanges every 30 seconds while it runs, keep for each Exchange whose process lives, in the state `accepting`, `running` or `ending`, its heartbeat and the time of the first look that found it, call it stuck when a look finds the same heartbeat at least 90 seconds later, count both with `CLOCK_UPTIME_RAW`, and never end an Exchange whose heartbeat goes on, whatever it waits for | New | unit `stuck.awake-30-90`, `stuck.heartbeat-progress`, `stuck.waiting-is-not-stuck`, `stuck.reset`, `stuck.identity`, `stuck.failed-look`, `stuck.unreadable`, `stuck.sleep-excluded`, `stuck.scheduler`, `stuck.native-clock`, `stuck.candidate-states`, `stuck.own-root-only` (SYL-252; private PostgreSQL, contract files and manager stand-ins). Actual Root/Trunk/vendor/Swift/renderer and Mac-sleep journeys remain SYL-257. |
| BKD-0.20 | end a stuck Exchange without asking with `arbol-root --root <root> stop --force <exchange>`, and when that replies `interrupted`, record in `exchange_notes` that it was ended because it was stuck, keeping the note as a file in the Root's folder until the database takes it | Changed | unit `stuck.force-route`, `stuck.decision-time`, `stuck.note`, `stuck.revalidate-after-stop`, `stuck.healthy-queue-cancel`, `stuck.manual-stop-cause`, `stuck.no-false-note`, `stuck.user-stop-after-force-cancel`, `stuck.refusal-is-not-internal-cancel`, `stuck.true-force-end`, `stuck.cancelled-caller`, `stuck.retained-force`, `stuck.force-serial`, `stuck.shutdown`; `notes.private-file`, `notes.atomic-publication`, `notes.first-timestamp`, `notes.crash-publication`, `notes.verified-temp-recovery`, `notes.short-write`, `notes.no-overwrite`, `notes.file-boundaries`, `notes.invalid-file`, `notes.conditional-removal`, `notes.directory-identity`, `notes.unknown-hardlink`, `notes.directory-no-follow`, `notes.sql-commit`, `notes.note-event`, `notes.idempotent`, `notes.database-away`, `notes.restart-recovery`, `notes.pending-row`, `notes.uncertain-sql`, `notes.retry-after-commit`, `notes.true-end`, `notes.chat-identity`, `notes.sql-file-race`, `notes.sql-deadline` (SYL-252; private PostgreSQL, contract files and manager stand-ins). Actual Root/Trunk/vendor/Swift/renderer and Mac-sleep journeys remain SYL-257. |

Restarts and discovery:

| ID | The Arbol backend must… | Origin | Verified by |
|---|---|---|---|
| BKD-0.21 | stop no Exchange when it ends, keep nothing a restart would lose except the mark of a stop under way, and at every start settle, list and read again | Kept | unit `stuck.shutdown`, `recovery.backend-restart`, `recovery.pending-note-snapshot`, `discovery.shared`, `stop.shutdown`, `settle.startup` (SYL-252; private PostgreSQL, contract files and manager stand-ins). Actual Root/Trunk/vendor/Swift/renderer and Mac-sleep journeys remain SYL-257. |
| BKD-0.22 | find the Exchanges of every retained Root at its start and when a window asks, through `arbol-roots list` and each Root's own `arbol-root --root <identifier> list`, report a Root whose listing fails for that Root alone, read no other Root's database or Exchange files, and send a command for an Exchange to the manager of the Root its listing names | New | unit `discovery.shared`, `discovery.metadata-only`, `discovery.root-manager-route`, `discovery.root-error-isolation`, `discovery.partial`, `discovery.safe-refusal`, `discovery.stop-root-identity`, `discovery.same-uuid`, `discovery.foreign-no-chat-read`, `discovery.deleted-root`, `discovery.validate-root-before-effects`, `discovery.stop-result-root`, `discovery.settle-root`, `discovery.settle-coalescing`, `discovery.settle-database-gate`, `discovery.retained-root-mutation`, `discovery.independent-roots`, `discovery.caller-shield`, `discovery.shared-look`, `discovery.total-bound`, `discovery.capacity`, `discovery.reply-bound`, `discovery.oversized-root-isolation` (SYL-252; private PostgreSQL, contract files and manager stand-ins). Actual Root/Trunk/vendor/Swift/renderer and Mac-sleep journeys remain SYL-257. |

A database that cannot be reached:

| ID | The Arbol backend must… | Origin | Verified by |
|---|---|---|---|
| BKD-0.23 | mark the database unreachable when a new connection or `SELECT 1` does not succeed within 5 seconds or the Keychain fails, with the cause, try to connect every 5 seconds, show an attention item in every window of the Root for as long as it lasts, and on its return clear it, settle and send a new snapshot on every subscription | New | unit `recovery.database-loss`, `recovery.attention`, `recovery.return`, `recovery.statement-timeout`, `recovery.sql-error-is-not-loss`, `recovery.connection-deadline`, `recovery.probe-bound`, `recovery.keychain-classification`, `recovery.safe-cause`, `recovery.credentials-refresh`, `recovery.retry-cadence`, `recovery.whole-probe-confirmation`, `recovery.renew-lock-bound`, `recovery.credential-lock-race`; `recovery.all-topic-snapshots`, `recovery.repeated-return`, `recovery.draft-preserved`, `recovery.draft-snapshot-race`, `recovery.saved-snapshot-race`, `recovery.epoch-race`, `recovery.live-stream-survives-return`, `recovery.independent-discovery`, `recovery.settled-note-retry`, `recovery.backend-restart`, `recovery.pending-note-snapshot`, `recovery.transient-snapshot-retry` (SYL-252; private PostgreSQL, contract files and manager stand-ins). Actual Root/Trunk/vendor/Swift/renderer and Mac-sleep journeys remain SYL-257. |
| BKD-0.24 | follow the Exchanges in progress from their folders while the database is away, keep the Draft of every message refused meanwhile, and show the answer of an Exchange whose record has an end and whose process is gone from its folder, marked `unsaved`, until it is settled | New | unit `recovery.offline-lines`, `recovery.open-chat-retained`, `recovery.unsaved`, `recovery.new-chat-refused`, `recovery.slow-sql-file-isolation`, `recovery.slow-refresh-preserves-subscription`, `recovery.offline-partial`, `recovery.offline-replay-generation`, `recovery.row-proof-before-stream`, `recovery.draft-refusal`; `notes.no-history-writes`, `recovery.settled-note-retry` (SYL-252; private PostgreSQL, contract files and manager stand-ins). Actual Root/Trunk/vendor/Swift/renderer and Mac-sleep journeys remain SYL-257. |

Accounts and the working folder:

| ID | The Arbol backend must… | Origin | Verified by |
|---|---|---|---|
| BKD-0.25 | run of a Driver only its account commands `subscriptions list`, `check`, `usage` and `models`, through its launcher, and never sign in, sign out or pass a secret | Changed | unit |
| BKD-0.26 | give a chat the folder its repository slot names in `~/repos/sylvan-stack/readonly/`, or the folder picked with "Other…", keep it for every message of the chat, and take no work area itself | Changed | unit, journey |

Health and tests:

| ID | The Arbol backend must… | Origin | Verified by |
|---|---|---|---|
| BKD-0.27 | measure at its start, every 5 minutes and when a window asks, whether the database server answers, the size of each retained Root's database, the size of the data folder and the free space of its disk | Changed | unit, journey |
| BKD-0.28 | show an attention item in every window when that free space is below 10 GiB, marked urgent below 2 GiB, naming the free space, the data folder's size and the largest database | New | unit, drill |
| BKD-0.29 | take its Root's folder, the folder of the launchers, its settings folder and its database from `--root-dir`, `--bin-dir`, `--settings-dir` and `--database` when they are given, and refuse `--root-dir` without `--bin-dir` and `--database` | New | unit `backend.identity-isolation`, `backend.database-identity`; packaged `backend.name-only-build` |

BKD-0.19's clock is checked inside the backend's own process, because no drill makes the Mac sleep, as RTM-0.12's is.

## Interface

```ts
// arbol [--root <root>] [-v <build>] backend [--root-dir <folder> --bin-dir <folder> --database <address>] [--settings-dir <folder>]
interface ReadyLine {                  // one line on standard output once it listens
  ready: true;
  root: string;                        // "sapling"
  build: string;                       // the build number of the arbol Build, "6"; "0" outside a Build (BLD-0)
  socket: string;                      // the absolute path of backend.sock
  pid: number;
}
// a refusal: { "error": { "code": "invalid_input" | "unknown_root" | "already_running", "message": string } }, exit status 1

interface BackendSettings {            // ~/.arbol/roots/<root>/arbol.json; every field may be missing
  route?: Partial<Route>;              // the route a new chat starts with (ARC-0 Route); model and effort may be left to the catalog
  repositories?: Record<string, { route?: Partial<Route> }>;   // by the repository's name, as its folder is named: its own default route
  smallCallRoute?: Route;              // handed to every Trunk for small calls such as a title
}

interface Measurement {                // the health of the database server (BKD-0.27)
  measuredAt: string;
  server: { ok: boolean; problem?: string };
  roots: Array<{ root: string; name: string; database: string; bytes?: number; problem?: string }>;
  dataFolderBytes?: number;
  freeBytes?: number;
  warning?: "low" | "urgent";          // below 10 GiB, below 2 GiB
}
```

Every time has the form that JavaScript's `toISOString` writes, as in BLD-0.

The backend's own tables, added to the Root's own layout `roots/<root>/layout.sql` of the `arbol-root` repository for every Root, First Sapling's included, under the rules of RTM-1:

```sql
-- The Arbol backend's own tables (BKD-0). Written by the Arbol backend alone.

CREATE SEQUENCE IF NOT EXISTS drafts_revision;
COMMENT ON SEQUENCE drafts_revision IS 'The one counter of the revisions of every Draft, so that no revision is given twice, also after a Draft was removed.';

CREATE TABLE IF NOT EXISTS drafts (
  id              uuid        PRIMARY KEY,
  chat_id         uuid        UNIQUE REFERENCES chats (id) ON DELETE RESTRICT,
  folder          text        UNIQUE CHECK (folder IS NULL OR folder LIKE '/%'),
  text            text        NOT NULL,
  revision        bigint      NOT NULL CHECK (revision >= 1),
  sent_as         uuid,
  sent_request    jsonb       CHECK (sent_request IS NULL OR jsonb_typeof(sent_request) = 'object'),
  updated_at      timestamptz NOT NULL,
  CHECK ((chat_id IS NULL) <> (folder IS NULL)),
  CHECK ((sent_as IS NULL) = (sent_request IS NULL))
);
COMMENT ON TABLE drafts IS 'What the Leather Bag typed in a composer and has not sent: one Draft of the reply for each chat, and one Draft of a new chat for each repository folder. Written by the Arbol backend alone (BKD-0).';
COMMENT ON COLUMN drafts.id IS 'The Draft''s own identifier, a UUID the backend gives it.';
COMMENT ON COLUMN drafts.chat_id IS 'For the Draft of a reply: its chat, for example c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b; NULL for the Draft of a new chat.';
COMMENT ON COLUMN drafts.folder IS 'For the Draft of a new chat: the absolute folder of its repository, for example /Users/sam/repos/shop; NULL for the Draft of a reply.';
COMMENT ON COLUMN drafts.text IS 'The text as the Leather Bag typed it, exactly.';
COMMENT ON COLUMN drafts.revision IS 'A new value of drafts_revision each time the Draft is saved. A save names the revision it was made over and is refused when that is no longer the Draft''s.';
COMMENT ON COLUMN drafts.sent_as IS 'The Exchange this Draft was sent as and not yet accepted or refused, for example 9b3a2c1e-5c6d-4f70-9a1b-2c3d4e5f6a7b; NULL when it is not being sent. Cleared by a save, which brings new text. The Draft is removed once that Exchange is in the chat tables.';
COMMENT ON COLUMN drafts.sent_request IS 'With sent_as: what the Draft was sent with, so that a send left half done can be made again with the same Exchange, for example {"chat": "c3d4e5f6-…", "route": {"driver": "claude", "subscription": "anthropic", "model": "sonnet"}, "workingFolder": "/Users/sam/repos/sylvan-stack/readonly/shop"}.';
COMMENT ON COLUMN drafts.updated_at IS 'When the Draft was last saved.';

CREATE TABLE IF NOT EXISTS chat_settings (
  chat_id         uuid        PRIMARY KEY REFERENCES chats (id) ON DELETE RESTRICT,
  route           jsonb       CHECK (route IS NULL OR jsonb_typeof(route) = 'object'),
  working_folder  text        CHECK (working_folder IS NULL OR working_folder LIKE '/%'),
  updated_at      timestamptz NOT NULL
);
COMMENT ON TABLE chat_settings IS 'What the Leather Bag picked for a chat''s next message, where it differs from the chat''s last Exchange. Written by the Arbol backend alone (BKD-0).';
COMMENT ON COLUMN chat_settings.chat_id IS 'The chat.';
COMMENT ON COLUMN chat_settings.route IS 'The route picked for the next message, in the form of ARC-0, for example {"driver": "claude", "subscription": "anthropic", "model": "sonnet", "effort": "high"}; NULL: the route of the last Exchange.';
COMMENT ON COLUMN chat_settings.working_folder IS 'The absolute folder picked for the next message, for example /Users/sam/repos/shop; NULL: the folder of the last Exchange.';
COMMENT ON COLUMN chat_settings.updated_at IS 'When a choice was last saved.';

CREATE TABLE IF NOT EXISTS chat_marks (
  chat_id      uuid        PRIMARY KEY REFERENCES chats (id) ON DELETE RESTRICT,
  ongoing      boolean     NOT NULL DEFAULT false,
  archived_at  timestamptz,
  updated_at   timestamptz NOT NULL
);
COMMENT ON TABLE chat_marks IS 'The marks the Leather Bag gives a chat in Elma Chat. Written by the Arbol backend alone (BKD-0).';
COMMENT ON COLUMN chat_marks.chat_id IS 'The chat.';
COMMENT ON COLUMN chat_marks.ongoing IS 'true while the Leather Bag marks the chat as one still being worked on (Elma Chat, Ongoing).';
COMMENT ON COLUMN chat_marks.archived_at IS 'When the Leather Bag archived the chat; NULL while it is not archived. An archived chat leaves the latest chats.';
COMMENT ON COLUMN chat_marks.updated_at IS 'When a mark was last changed.';

CREATE TABLE IF NOT EXISTS exchange_notes (
  exchange_id  uuid        NOT NULL REFERENCES exchanges (id) ON DELETE RESTRICT,
  kind         text        NOT NULL CHECK (kind IN ('ended_stuck')),
  at           timestamptz NOT NULL,
  PRIMARY KEY (exchange_id, kind)
);
COMMENT ON TABLE exchange_notes IS 'What Arbol says about an Exchange that the chat tables do not hold. Written by the Arbol backend alone (BKD-0).';
COMMENT ON COLUMN exchange_notes.exchange_id IS 'The Exchange the note is about.';
COMMENT ON COLUMN exchange_notes.kind IS 'ended_stuck: the backend ended the Exchange by force because its heartbeat stood still (ARC-3).';
COMMENT ON COLUMN exchange_notes.at IS 'When the backend decided it.';
```

`kind` is a check that a later Build may not widen inside a Root (RTM-1). A new kind of note therefore needs a table of its own or a new Root; the first thin path, the first version that goes once through every part ([ARC-1](../architecture/01-roots.md#what-is-built-first)), needs only `ended_stuck` ([BKD-D6](#decisions)).

The lines a Root's migration script, `roots/<root>/migrate.sql`, adds for these tables: in its first step, after the chat tables,

```sql
\copy (SELECT * FROM drafts) TO 'drafts.copy' WITH (FORMAT binary)
\copy (SELECT * FROM chat_settings) TO 'chat_settings.copy' WITH (FORMAT binary)
\copy (SELECT * FROM chat_marks) TO 'chat_marks.copy' WITH (FORMAT binary)
\copy (SELECT * FROM exchange_notes) TO 'exchange_notes.copy' WITH (FORMAT binary)
\copy (SELECT d.last_value,d.is_called,(s.seqtypid='bigint'::regtype AND s.seqincrement=1 AND s.seqmin=1 AND s.seqmax=9223372036854775807 AND s.seqcache=1 AND NOT s.seqcycle) AS valid_definition FROM drafts_revision d JOIN pg_sequence s ON s.seqrelid='drafts_revision'::regclass) TO 'drafts_revision.copy' WITH (FORMAT binary)
```

and in its second step, validate the counter before importing rows, copy the four tables after `\copy runs FROM …`, and restart the sequence last before COMMIT, as the full RTM-1 script shows:

```sql
SET LOCAL lock_timeout='2s';
DO $$
BEGIN
  IF to_regclass('drafts') IS NULL OR to_regclass('chat_settings') IS NULL
     OR to_regclass('chat_marks') IS NULL OR to_regclass('exchange_notes') IS NULL
     OR to_regclass('drafts_revision') IS NULL THEN
    RAISE EXCEPTION 'The target backend layout is incomplete';
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_sequence WHERE seqrelid='drafts_revision'::regclass
      AND seqtypid='bigint'::regtype AND seqincrement=1 AND seqmin=1
      AND seqmax=9223372036854775807 AND seqcache=1 AND NOT seqcycle) THEN
    RAISE EXCEPTION 'The target Draft revision counter is incompatible';
  END IF;
END $$;
CREATE TEMP TABLE incoming_drafts_revision (
  last_value bigint NOT NULL, is_called boolean NOT NULL, valid_definition boolean NOT NULL
) ON COMMIT DROP;
\copy incoming_drafts_revision FROM 'drafts_revision.copy' WITH (FORMAT binary)
DO $$
BEGIN
  IF (SELECT count(*) FROM incoming_drafts_revision)<>1
     OR EXISTS (SELECT 1 FROM incoming_drafts_revision WHERE last_value<1 OR NOT valid_definition) THEN
    RAISE EXCEPTION 'The source Draft revision counter is incompatible';
  END IF;
END $$;
\copy drafts FROM 'drafts.copy' WITH (FORMAT binary)
\copy chat_settings FROM 'chat_settings.copy' WITH (FORMAT binary)
\copy chat_marks FROM 'chat_marks.copy' WITH (FORMAT binary)
\copy exchange_notes FROM 'exchange_notes.copy' WITH (FORMAT binary)

-- A transactionally locked restart neither reuses a consumed/deleted revision nor survives rollback.
DO $$
DECLARE following numeric;
BEGIN
  ALTER SEQUENCE drafts_revision CACHE 1;
  SELECT greatest(1::numeric,
    (SELECT last_value::numeric+is_called::integer FROM incoming_drafts_revision),
    (SELECT last_value::numeric+is_called::integer FROM drafts_revision),
    (SELECT coalesce(max(revision)::numeric,0)+1 FROM drafts)) INTO following;
  IF following>9223372036854775807 THEN
    RAISE EXCEPTION 'The Draft revision counter is exhausted';
  END IF;
  EXECUTE format('ALTER SEQUENCE drafts_revision RESTART WITH %s',following);
END $$;
```

A Draft of a chat whose Exchange is open at the snapshot comes over too, so the Leather Bag finds the text in the newer Root.

The calls, subscriptions and events the backend answers are in [BKD-1](01-the-bridge.md#interface).

## Known problems in version 1

Not to be reproduced.

- **A resident service that also ran the chats.** The windows talked to version 1's resident service, then called Arbol Root, which orchestrated every turn, so a restart of it touched every chat, and one failed turn could hold up all of them.
- **"Running" for ever.** When the end of a turn could not be recorded, the chat stayed running, and cancel doubled as repair.
- **Storage on the path of every chat.** A slow write on the loop that served every chat stalled all of them, for up to nine seconds.
- **A database nobody could see.** It ran in a container whose disk the application could not see, and filled that disk twice.
- **Replay held in memory.** The text not yet sealed lived only in a process's memory, so a window opened late, or after a restart, missed it.
- **A Draft with several owners.** Windows overwrote each other's Drafts, a late "clear" could delete newer text, and a save that failed was never shown.
- **A placeholder stored as the title.** A window stored `Elma · <repository>` as the title, so no title was ever made for chats started there.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#2. One turn's failure could block everything else`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#3. Durable bookkeeping on the streaming path`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#7. Blocking storage calls on the loop that serves every chat`
- `arbol_deprecated_v1:product-spec/03-turn-execution.md#Stored versus live-only, and how a window reconciles them`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#9. A draft had more than one owner`
- `arbol_deprecated_v1:product-spec/02-chat-sessions.md#Known problems and lessons`

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| BKD-D1 | Where does the specification of Arbol itself live? | A chapter of its own, `~/Artifacts/arbol/backend/`, numbered `BKD`, with three specifications: the backend, the Bridge, and Elma Chat's first version. What that first version does is [BKD-D22](02-elma-chat.md#decisions). The alternative: a chapter for each part, or the window inside the Swift App's specification (SYL-192) | Decided 18 October 2026, a technical choice: the proposed default, as the Beat SYL-190 proposed it |
| BKD-D2 | How does the backend start, and how many run? | The command `arbol --root <root> backend`, the same program as the command line (ARC-0), started by the Swift App; one for each Root, by an exclusive lock on a file in the Root's folder; a ready line once its socket listens. A second start finds the first and refuses with `already_running`, and the Swift App connects to the first. The alternative: the Swift App keeps the count itself, which two Swift Apps, or a backend started by hand for development, would break | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D3 | Brain Recipes are not specified yet (SYL-191). Which route does a message of Elma Chat go with? | The one the Leather Bag picks in the composer: a Driver with one of its Subscriptions, a model and an effort, from the Drivers' own lists. A chat keeps the route of its last message, and a new chat starts with the route of the Root's last message, or with the `route` of `arbol.json` when the Root has none yet. No small-call route is handed, because the Trivial Trunk makes no small call (TRV-0). When Brain Recipes come, the picker offers them beside the routes. The alternative: one fixed route in `arbol.json` and no picker | Decided 19 October 2026 by the owner: "We don't use Brain Recipes when user should specify explicitly or there are default values. Elma Chat should work as previously and it never used Brain Recipes but defaults and user selections." The route of Elma Chat is the Leather Bag's choice or a default, never a Brain Recipe; the defaults are those of version 1's Elma Chat, kept in `arbol.json` (BKD-2), with a default small-call route for the Trunks that make small calls |
| BKD-D4 | In which folder does the agent of an Elma chat work, now that agents work at once in named work areas? | Proposed (B): every chat on a repository of the stack gets a work area of its own when its first message is sent, with a hold that names the chat, on a branch of its own, given back when the chat is archived. The alternative (A): a chat works in the folder its slot names, as in version 1, and only an agent that takes a Beat moves to a work area | Decided 19 October 2026 by the owner, against both: "We definitely will have more than 5 chat sessions open and not every chat session need its own prepared folder. So I still recommend open it in readonly initially and provide tool to book prepared folder only when needed." A chat works in the repository's folder in `readonly/`; an agent that has to change files books a work area with a tool of the guide Working in Sagas, built in a task of its own, and the hold names the chat (AGR-D11) |
| BKD-D5 | Where are Drafts kept, and how? | In the Root's database, as ARC-0 says, in the backend's own table `drafts`: as version 1 had them, one Draft of the reply for each chat and one Draft of a new chat for each repository folder, holding the text. A save names the revision it was made over and is refused when another window saved meanwhile, so that no window overwrites text it has not seen; revisions come from one counter, so none is given twice. A Draft being sent is marked with its Exchange, and is removed only once that Exchange is in the chat tables, so that a message accepted while the Leather Bag typed on in another window removes no newer text, and a removal a backend could not make is made later. The alternative: the last save wins, as in version 1, where a late clear deleted newer text | Decided 19 October 2026, a technical choice following BKD-D22 |
| BKD-D6 | Where does Arbol say in a chat that it ended an Exchange because it was stuck (ARC-3)? | A note in a table of the backend's own, `exchange_notes`, which the window shows under the Exchange. The chat tables belong to the Trunks, and Arbol writes only a chat's title there (ARC-0). The alternative: the window infers it from an interrupted Exchange, which cannot tell a stuck one from one whose process was killed | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D7 | Who chooses the identifier of a new Exchange? | The window, a UUID it makes before it calls `chat.send`. When the backend ends before it could answer, the window sends the same call again, and the Trunk answers with the Exchange it accepted (RCT-D17), so one message never runs twice. The alternative: the backend chooses it, and a window whose backend ended cannot tell whether its message was accepted | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D8 | How does the backend follow `events.jsonl`? | It reads the new bytes of the file at least every 250 milliseconds while a window follows the Exchange, whole lines only, from the first line for each window that starts to follow it, and keeps no copy of the lines: the file is the copy. The alternative: the system's notice of a changed file (kqueue), which saves reads but needs a reading by time anyway for a file replaced while it is watched | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D9 | What does the backend do when `arbol-root start` gives no clear reply? | Nothing within its 25 seconds, `no_answer` and `in_progress` are not refusals: the message may still be accepted. The backend runs the same start again, with the same identifier and a request file written anew, 15 seconds after the previous attempt returned, the longest an acceptance takes (RCT-2), never while one still runs, until 120 seconds after the first; then it replies `no_answer`, and the window sends the same call again. A Trunk that accepted the message replies as a repeat and starts nothing (RCT-D17), so the message never runs twice. The alternative: one attempt, after which the Leather Bag cannot tell whether the message runs | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D10 | A sign-in step `store_secret` asks for a key. Does the window take it? | No. Every secret is entered on the Secrets page of Seqoya Lab, and until that page exists by hand with the system's `security` command (ARC-D62). The window names the Keychain item the step names and waits | Decided 19 October 2026 by the owner: the Leather Bag signs in with the Driver's own command at the terminal until Seqoya Lab has a page for it (BKD-D17), and that command takes a key as the Driver says (DRV-1). No secret crosses the Bridge or passes through the backend |
| BKD-D11 | When does Arbol warn that space runs out? | When the disk of the database's data folder has less than 10 GiB free, and urgently below 2 GiB, measured every 5 minutes. In version 1 one table grew by about 50 GB a day through a defect; 10 GiB leaves hours to act in such a case and is far above what a day of ordinary chats takes, and 2 GiB is about the room PostgreSQL needs to keep running and vacuum. The alternative: a share of the disk, such as 10 %, which on a large disk warns far too early | Decided 18 October 2026, a technical choice: the proposed default, the values to start with |
| BKD-D12 | How is a measurement of each Root's database size made without opening another Root's database? | `pg_database_size` of each database named in a retained Root's `root.json`, asked on the backend's own connection, which reads the server's catalogue and opens nothing else (ARC-1). The alternative: each Root's backend measures its own, which leaves out every Root whose backend is not running | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D24 | Where are a chat's settings and marks kept? | In two tables of the backend's own, `chat_settings` for the route and the folder picked for the next message, and `chat_marks` for ongoing and archived, because the chat tables belong to the Trunks and hold only what an Exchange ran with (ARC-0, RCT-3). Version 1 saved a choice to the chat at once and let it count from the next message on, also while the agent worked; Arbol 2 keeps that. The alternative: the window keeps the choice until the next message, which loses it when the window closes | Decided 19 October 2026, a technical choice following BKD-D22 |
| BKD-D25 | What becomes of a long paste? | As in version 1: text of 10,000 characters or more is saved as a file and the message names its path, so that a message stays readable and the agent reads the text from the file. The file is kept in the Root's folder, `pastes/`, of the mode 0600, and stays as long as the Root, because the chat names it. The alternative: the text in the message, which a Driver sends whole with every later message of the chat | Decided 19 October 2026, a technical choice following BKD-D22 |
| BKD-D26 | How does the deferred stale-copy feature cross the backend/Bridge/UI after Root commands exist? | Own-Root optional provenance/stale metadata on summaries, startup/list-open comparison coalesced per Root, a bounded chat.reimport call that returns the actual result chat/action, migration_unavailable attention on failed comparison, and no automatic repeat after ambiguous reimport. UI opens that returned chat after saving its current Draft. SQL/CLI remains SYL-195; backend/renderer/journey implementation is SYL-249/SYL-256/SYL-257 | Chosen 27 October 2026 during SYL-195 before core code, retaining ARC-D50’s owner-approved default |
| BKD-D27 | How are the backend process, child and database helpers made concrete for SYL-246? | asyncio tasks and private lifetime lock/socket; ready before independent startup work; launcher-only nonblocking bounded children with exact production deadlines and tracked unresolved mutations; pinned psycopg binary 3.3.6, one autocommit connection per operation and explicit read-only repeatable snapshots; isolated private server/fixtures and packaged interpreter/dependencies. See Process foundation choices for refusal/cleanup and settings details | Chosen 27 October 2026 before implementation; technical choices, no Bridge/UI or later attention behavior claimed |
| BKD-D28 | How are backend rows/counters preserved by Root layout/whole migration and one-chat reimport? | Exact additive schema in both Roots, full row/counter copy with locked transactional RESTART rather than setval; comparison changes only stale marks; reimport copies/remaps history notes, preserves local Draft/settings/marks and never transfers pending dispatch, with busy for replacement of an unresolved send | Chosen 27 October 2026 before SYL-247 code; detailed shared behavior above, future Backend/UI consumers remain named Beats |
| BKD-D30 | How are chat reads, changes, observations, degradation and migration calls made precise? | The Chat read and update choices above: consistent views and ordering, exact cuts, atomic local updates, private pastes and delegated bounded provenance/reimport | Decided27 October2026 before SYL-249 code, a technical choice; UI/live Exchange behavior remains in its named Beats |
| BKD-D31 | How are Draft CAS, send ownership/recovery, request files and bounded shared dispatch made precise? | The Draft and dispatch choices above: exact scope/text/revision validation, conditional marks/cleanup, private atomic request lifetime, shielded per-Exchange dispatch and strict result/refusal projection | Chosen27 October2026 before SYL-250 implementation; technical choices, no live/Swift/UI behavior claimed |
| BKD-D32 | How are live replay, record/process/status observation, stop, answers and settling made precise? | The Live Exchange and control choices above: per-subscription snapshot generations, bounded two-pass replay and oversized metadata, own private files, truthful saved transitions, shared bounded stops and current-form one-write answers, and coalesced gated settling | Chosen27 October2026 before SYL-251 code; technical choices; full recovery/cross-Root work252 and real/UI journeys257 remain explicit |
| BKD-D33 | How are database loss, durable stuck notes and explicit cross-Root discovery made precise? | The Recovery and discovery choices above: classified health/5sec probes, retained opened chats, awake30/90 looks, serialized force and write-ahead notes, per-Root command/listing/settle ownership and generation-checked recovery | Chosen27 October2026 before SYL-252 code; technical choices; actual Root/vendor/Swift/window journeys remain257 |
