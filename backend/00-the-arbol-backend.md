---
role: authored
spec: BKD-0
status: draft
---
# Arbol backend · 00 The Arbol backend

The *Arbol backend* is the one process of a Root's `arbol` [Build](../GLOSSARY.md#build) that serves the Leather Bag's windows in that Root. It reads the chats from the Root's database, keeps the [Drafts](../GLOSSARY.md#draft), sends a message by having `arbol-root` start a Trunk, follows the answer as it arrives in the Exchange's folder, passes stops and answers on, looks every 30 seconds for an Exchange that is stuck, notices a database that cannot be reached, signs the Leather Bag in through the Drivers, and reports how much space the chats take. For example, when the Leather Bag sends "What does build.sh do?" in First Sapling, the backend writes a request file, runs `arbol-root --root sapling start --exchange 2d4f6a8c-… --request …/2d4f6a8c-….json`, reads the acceptance line, and from then on reads `exchanges/2d4f6a8c-…/events.jsonl` line by line and passes each line to every window that shows the chat. This specification states the process and its socket, the database and the backend's own tables, Drafts, sending and sending again, an Exchange in progress, stop and answers, settling, stuck Exchanges, restarts and discovery across Roots, a database that cannot be reached, accounts, health and storage, and tests. It matters because in version 1 every window talked to a resident service that also ran the chats, so one failed turn could hold up every chat, a chat whose end could not be recorded showed "running" for ever, and the database filled its disk twice without anyone seeing it coming.

It follows the conventions of the [Driver Contract](../driver-contract/README.md#conventions) and the additions in this chapter's [README](README.md#conventions). It makes exact what [ARC-0](../architecture/00-components-and-boundaries.md#arbol-the-swift-app-and-the-backend) to [ARC-3](../architecture/03-stuck-trunks.md) say of the backend, and is one party of the [Root Contract](../../arbol-root/contract/README.md), version 1: it reads the Exchange folder of [RCT-1](../../arbol-root/contract/01-the-exchange-folder.md) and the chat tables of [RCT-3](../../arbol-root/contract/03-the-chat-tables.md), and writes answers into `control`. The forms are technical choices made on 18 October 2026; the questions only the owner can settle are rows of the Decisions table with a proposed answer.

## Scope

Covered: the process, its socket and its lifetime, other programs it starts, the database and the backend's own tables, Drafts, sending a message and sending it again, an Exchange in progress, stop and answers, settling, stuck Exchanges, restarts and discovery across Roots, a database that cannot be reached, accounts, health and storage, the program and its Build, tests.

Not covered: what crosses the Bridge, in [BKD-1](01-the-bridge.md); what the window shows, in [BKD-2](02-elma-chat.md); Brain Recipes and the small-call route (SYL-191); the command line `arbol` apart from its command `backend` (SYL-193); the tray menu and how the Swift App starts and ends a backend (SYL-192); listeners such as Telegram ([ARC-D52](../architecture/01-roots.md#decisions)); a message that steers a running agent ([ARC-D54](../architecture/02-chat-exchange-across-components.md#decisions)); marking a migrated chat stale and bringing it over again (ARC-1.19, ARC-1.20; SYL-195).

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
| Its socket | `backend.sock` in the Root's folder ([ARC-1](../architecture/01-roots.md#a-root-on-disk)), a Unix socket of the mode 0600, which only the owner can open. Once it holds the lock it removes a socket file left by a backend that died, then listens. A path longer than the 103 bytes a macOS socket address can hold is refused with `invalid_input` |
| Ready | Once it listens, it prints one line, the *ready line*, and from then on writes nothing more on standard output. Standard error is for a person only |
| A refusal | One line `{"error":{"code","message"}}` and the exit status 1: `invalid_input`, `unknown_root` for a Root whose folder holds no readable `root.json`, `already_running` |
| Its end | On SIGTERM or SIGINT, and when the process that started it ends, it closes every connection, removes its socket, releases the lock and ends with the status 0 within 2 seconds. It stops no Exchange (ARC-2) |

The Swift App starts the current Root's backend when Arbol starts and again when it ends, and the backend of another Root when one of that Root's windows opens; it ends that one when the last of its windows closes (ARC-0). How it does so is the Swift App's specification (SYL-192).

A backend starts for a Root in every state, `preparing`, `working` or `failed`, because a Root that is being prepared is tried with its chats, and a failed one is still opened when it is named ([ARC-1](../architecture/01-roots.md#the-states-of-a-root-and-the-current-root)). It serves an older Root for as long as its folder, its database and its Builds exist.

What it does at its start, in this order: the lock, the socket and the ready line; the connection to the database, which may fail without stopping anything else ([below](#when-the-database-cannot-be-reached)); `arbol-root settle` ([below](#settling)); the first look at the Exchanges ([below](#stuck-exchanges)); and the discovery across Roots ([below](#restarts-and-discovery-across-roots)). Windows can connect from the ready line on.

### The current Root and listeners

The backend never stores which Root is current. When it needs to know, at its start and when a window asks, it runs `arbol-roots list` and takes the record marked `current` ([ARC-1](../architecture/01-roots.md#the-states-of-a-root-and-the-current-root)). Listeners run only in the current Root's backend; this specification has none, because Telegram, the only listener so far, is postponed (ARC-D52).

### Other programs it starts

| Program | For | Through |
|---|---|---|
| `arbol-root` | Starting, listing, stopping and settling Exchanges ([RTM-0](../../arbol-root/specs/00-the-commands.md)) | Its launcher, always with `--root <root>` |
| `arbol-roots` | The list of Roots ([ARC-1](../architecture/01-roots.md#the-tray-menu-and-arbol-roots)) | Its program on the search path |
| `arbol-claude-driver`, `arbol-codex-driver` | Account commands only ([below](#accounts)) | Their launchers |
| `/usr/bin/security` | Storing a secret that a sign-in asks for ([below](#accounts)), and reading the database password, as a Trunk reads it ([RCT-0](../../arbol-root/contract/00-overview.md#how-a-trunk-finds-its-roots-folder-and-database)) | Itself |

The folder of the launchers, `~/.local/bin` unless `--bin-dir` names another, is first on the search path of every program it starts, so that a Trunk that `arbol-root` starts for the backend finds the same Drivers as one started from a shell (RCT-0). Each program is started in a process group of its own, as the system call `setsid` does, so that a start, a stop or a settle that is under way goes on when the backend ends. The backend waits for none without a time limit: 25 seconds for `arbol-root start` (the 20 of RTM-0, and 5 for the launcher), 45 seconds for `arbol-root stop`, which may wait 20 seconds, end by force for 10 and then settle, 60 seconds for `arbol-root settle`, and 10 seconds for `arbol-root list`, `arbol-roots list` and every account command except `sign-in`, which lasts as long as its attempt (DRV-1). A program that has not answered in its time is reported as `no_answer` and left alone.

### The database

The backend connects to the Root's database as a Trunk does: the address in `~/.arbol/database.json`, the password in the Keychain item `com.sylvan-stack.arbol.database`, and the database that `root.json` names (RCT-0, ARC-1). It talks to it with psycopg 3 at a version pinned in the Build, with its own plain SQL, and every call has a time limit of 5 seconds, to connect and for each statement (RCT-3). It never opens the database of another Root (ARC-1).

| Tables | The backend |
|---|---|
| The chat tables `chats`, `exchanges`, `messages`, `tool_calls`, `runs` (RCT-3) | Reads them directly with SQL, and writes only `chats.title`, when the Leather Bag gives a chat a title or takes it away |
| Its own tables, `drafts` and `exchange_notes` ([Interface](#interface)) | Reads and writes their rows; nobody else does |
| `migrated_chats` of a Root that grew from another (RTM-1) | Reads nothing of it in this specification; marking a stale copy is SYL-195 |

It reads a chat as RCT-3 says, without knowing which Trunk wrote it: every Exchange of the chat that was not replaced, in the order of their numbers, and within each its messages and the tool calls the agent made itself in the order of their positions ([RCT-3](../../arbol-root/contract/03-the-chat-tables.md#how-a-chat-is-read)). For an Exchange that is still open it reads the answer from the folder ([below](#an-exchange-in-progress)).

A title is 1 to 240 characters, as the chat tables check. The backend writes the Leather Bag's text with its spaces at both ends removed, and NULL when nothing is left, and never a placeholder ([RCT-3](../../arbol-root/contract/03-the-chat-tables.md#the-tables)). For example, renaming a chat to "  Build script  " stores `Build script`.

**Its own tables.** The backend creates, changes and removes no table, column, index or check. Its own two tables are in the Root's own layout, `roots/<root>/layout.sql` in the `arbol-root` repository, which the Root's `arbol-root` Builds carry as `layout/root-tables.sql` and `arbol-roots` runs ([RTM-1](../../arbol-root/specs/01-builds-layouts-and-migration.md#the-roots-own-layout)). Within a Root they change only by additions the Root's older Builds can ignore, as RTM-1 says, and so does the settings file `arbol.json` ([below](#settings)). A Root whose database lacks them is served without Drafts and without notes, and every window says that the Root's layout is incomplete; nothing else stops.

A Root that grew from another gets the rows of both tables from its migration script, copied as they are, as it copies the chat tables (RTM-1).

### Settings

The backend's settings are the file `~/.arbol/roots/<root>/arbol.json`, which the owner can edit and the backend reads at its start ([ARC-1](../architecture/01-roots.md#settings)). In this specification it holds one setting, the route a new chat starts with until the Leather Bag picks another ([BKD-D3](#decisions)):

```json
{ "route": { "driver": "claude", "subscription": "anthropic", "model": "sonnet", "effort": "high" } }
```

A missing file, or one without `route`, is no error: a new chat then starts with the route of the Root's last message, and the first message of a Root with no route at all has to have one picked. Brain Recipes, which SYL-191 specifies, will be kept in the same file.

### Drafts

A Draft is what the Leather Bag has typed in a chat's composer and not sent ([ARC-0](../architecture/00-components-and-boundaries.md#who-writes-what)). The backend keeps one Draft for each chat, in its table `drafts`, with the text, the working folder and the route the composer shows ([BKD-D5](#decisions)).

| | |
|---|---|
| A new chat | Its Draft is kept under the identifier the chat will have, a UUID the window chooses when it opens a new composer; the chat itself exists only once a Trunk accepts its first message (RCT-0) |
| Saving | The window sends the Draft as the Leather Bag types ([BKD-2](02-elma-chat.md#the-composer)); the backend replaces the row whole and gives it a new `revision`, a number that only grows. A Draft whose text is empty and whose chat does not exist is removed |
| Two windows | The last Draft sent wins. Every other window of the chat is told of the new revision (BKD-1) |
| Sent | Once a Trunk accepts the message, the backend removes the Draft when its revision is still the one the window sent with the message; a Draft typed further meanwhile stays |
| Refused | The Draft stays as it was ([ARC-2](../architecture/02-chat-exchange-across-components.md#the-steps)) |

### Sending a message

1. The window calls `chat.send` with the chat, the message, the route, the working folder, the Draft's revision and an Exchange identifier it chose ([BKD-1](01-the-bridge.md#sending-and-repeating)).
2. The backend checks what it can before anything starts and refuses with `invalid_input`: a route that does not name a Driver, a Subscription and a model, because Arbol always hands those three (ARC-0); a working folder that is not an absolute path to a folder that exists (RCT-0); an empty message.
3. It writes the *request file* of [RCT-0](../../arbol-root/contract/00-overview.md#what-is-handed-to-a-trunk) into the folder `requests/` of the Root's folder, of the mode 0700, as `<exchange>.json` of the mode 0600: the chat, the message, the route, the working folder, and no small-call route, because no Brain Recipe exists yet to resolve one (ARC-0, SYL-191).
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
| Nothing, `no_answer`, or the backend lost the line because it ended | Starts the same Exchange again with the same identifier and the same request file, 15 seconds after the first start, and again every 15 seconds, for at most 60 seconds. A Trunk that accepted it answers `"duplicate": true` and starts nothing; one still accepting answers `in_progress` (RCT-2). After 60 seconds without an answer the backend passes `no_answer` on, and the Draft stays |

Because the window chose the Exchange's identifier, it sends the same `chat.send` again after a backend that ended came back, and gets the same Exchange, not a second one (RCT-D17).

A chat takes one Exchange at a time (ARC-D54): a message to a chat whose Exchange is still open is refused by the Trunk with `chat_busy`, which names the open Exchange, and the window offers to stop it and send then ([BKD-2](02-elma-chat.md#sending-and-stopping)). The backend checks nothing of this itself, because only the database can tell two messages at the same moment apart (RCT-3).

### Sending a message again

The Leather Bag can send the message of a chat's last Exchange again once that Exchange has ended, for example after a failure or a rate limit: the previous answer and its tool calls are discarded, and everything runs again from the same message ([RCT-2](../../arbol-root/contract/02-starting-stopping-and-settling.md#sending-a-message-again), RCT-D15, RCT-D16).

The window calls `exchange.sendAgain` with the Exchange, a new Exchange identifier and the route; the backend writes a request file with the chat, the route and the working folder of the replaced Exchange and no message, and runs `arbol-root --root <root> start --exchange <new> --request <file> --replaces <old>`. The route is the one the Leather Bag picks, by default the one the replaced Exchange ran with. The Trunk refuses with `cannot_replace` an Exchange that is not the last of its chat, has not ended or was replaced already (RCT-2), and the backend passes that on.

### An Exchange in progress

While an Exchange's folder exists, its answer is read from the folder, which holds all of it so far ([RCT-1](../../arbol-root/contract/01-the-exchange-folder.md#the-answer-as-it-arrives-eventsjsonl)):

1. The backend reads the Exchange's row first. While it is `open`, it reads the folder `exchanges/<exchange>/`.
2. It reads `events.jsonl` from its first line and then each line as it is appended, at least every 250 milliseconds while a window follows the Exchange. It reads only whole lines: a last line without a newline is left for the next read. It ignores a line, a field and an event type it does not know (RCT-1).
3. It reads `record.json` with the same reads, for the Exchange's signs of life and its end, and takes the record's process as living only when a process with its `pid` exists and was started at its `startedAt`, give or take two seconds, reading the start time with `/bin/ps` in a clean environment and the C locale, as the Root manager does (RCT-1, RTM-0).
4. When the folder is gone, the end is in the database, because a Trunk saves the end before it removes its folder (RCT-2). The backend reads the row and the Exchange's rows again, and tells every window that follows the chat that the Exchange is saved.

A folder whose name starts with a dot is skipped (RCT-1). A window opened late, opened again or opened twice gets the lines of `events.jsonl` from the first one on, so it shows the whole answer so far ([ARC-2](../architecture/02-chat-exchange-across-components.md#the-arriving-answer-is-a-file)). The backend keeps no copy of the lines: the file is the copy, so a backend that has just started serves a late window exactly as one that has run for hours.

What the window is told of the Exchange's state comes from the record and the listing of `arbol-root` ([RTM-0](../../arbol-root/specs/00-the-commands.md#the-listing)), with two states of the backend's own:

| State | When |
|---|---|
| `accepting`, `running`, `ending` | As the listing says. `running` comes with what the Exchange waits for and since when ([ARC-3](../architecture/03-stuck-trunks.md#long-waits-on-purpose)) |
| `stopping` | The backend was asked to stop it, and it has not ended yet |
| `unsaved` | The record has an end, its process is gone, and the database does not have the end yet ([below](#when-the-database-cannot-be-reached)) |
| `interrupted` | Its process is gone without an end: shown as interrupted until settling has saved it ([below](#settling)) |
| `completed`, `failed`, `cancelled`, `interrupted` | The final state, from the database |

### Stop and answers

**Stop.** The window calls `exchange.stop`. The backend marks the Exchange `stopping` for every window from that moment until it has ended, and runs `arbol-root --root <root> stop <exchange>` ([RTM-0](../../arbol-root/specs/00-the-commands.md#stopping)). When the command returns, it reads the Exchange's row and reports its true final state: `cancelled` when the Trunk confirmed the stop, `interrupted` when the Root manager had to end it by force, or what it ended with otherwise ([ARC-3](../architecture/03-stuck-trunks.md#a-stop-that-is-not-obeyed)). "Stopped" is shown only once the end says `cancelled` (RCT-2). A stop of an Exchange that has ended already, or that is unknown, succeeds and changes nothing (ARC-3). Two windows that stop the same Exchange start one `arbol-root stop`: the second waits for the first.

**Answers.** When the agent asks the Leather Bag a question (DRV-3), the window shows it from the `ask_opened` line and calls `exchange.answer` with the question's `askId` and the answer. The backend checks the answer against the question's form (DRV-3) and refuses a malformed one with `invalid_input`. Then it appends one line to the Exchange's `control` file, the Driver's own control line ([RCT-1](../../arbol-root/contract/01-the-exchange-folder.md#stop-and-answers-control)):

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
- after a listing that shows an Exchange in the state `unaccepted`, `unsaved` or `interrupted`.

One settle runs at a time; a reason that arises while one runs runs the next one after it. Once settling has saved an Exchange, the backend reads its rows again and tells every window that follows the chat.

### Stuck Exchanges

An Exchange is *stuck* when its process is alive and does nothing ([ARC-3](../architecture/03-stuck-trunks.md)). The backend looks from outside, as the second line of defence of ARC-3:

1. Every 30 seconds it runs `arbol-root --root <root> list` and keeps, for each Exchange in the state `running` whose process lives, its heartbeat and the time of the look.
2. An Exchange is stuck when its heartbeat is the same as at a look at least 90 seconds earlier. For example, looks at 0, 30, 60 and 90 seconds that all find the heartbeat 41 make the Exchange stuck at the fourth.
3. It ends a stuck Exchange without asking ([ARC-D57](../architecture/03-stuck-trunks.md#decisions)): it writes a note into its table `exchange_notes`, that the Exchange was ended because it was stuck, and runs `arbol-root --root <root> stop --force <exchange>`. The Root manager ends the Trunk's processes and has the Exchange settled as interrupted, with what had arrived (RTM-0). When the note cannot be written within 5 seconds, it stops the Exchange anyway and writes the note once the database is back, keeping it in memory meanwhile.
4. The window shows the note under the Exchange: "Ended because it was stuck" ([BKD-2](02-elma-chat.md#coming-back)). The chat takes a new message afterwards (ARC-3).

The 30 and the 90 seconds are counted with the clock that macOS calls `CLOCK_UPTIME_RAW`, which stands still while the Mac sleeps, so that waking the Mac makes no Exchange look stuck ([ARC-3](../architecture/03-stuck-trunks.md#two-lines-of-defence)). A heartbeat that goes on is never stuck, whatever the Exchange waits for: an answer of the Leather Bag or a command the agent runs is never ended for taking long, and the window shows what it waits for and for how long (ARC-D61).

The same listing gives every window the states and the signs of life of its Exchanges, and is the listing after which settling runs. The backend of a Root looks only at its own Root, and only while it runs: a Root whose backend has ended has only the Trunk's watch on itself (ARC-3).

### Restarts and discovery across Roots

The backend keeps nothing that a restart would lose, except two marks in memory: which Exchanges it is stopping, and a note it could not yet write. When it ends, no Exchange stops: the Exchanges run detached (RCT-2), and a start, a stop or a settle it began goes on in its own process group. At its next start it settles, lists and reads everything again, so what was produced meanwhile is shown ([ARC-2](../architecture/02-chat-exchange-across-components.md#when-arbol-quits)). A newer Build of the same Root, or a newer Build of `arbol-root`, finds the same Exchanges, because they are known only from their records; no Exchange changes its Root or its Trunk Build ([ARC-1](../architecture/01-roots.md#what-a-root-is)).

**Discovery across Roots.** The current Root's backend finds the running work of every Root, also of a Root that is not current and has no window open, at its start and when a window asks ([ARC-1](../architecture/01-roots.md#discovery-across-roots)):

1. It runs `arbol-roots list` for the records of the retained Roots.
2. For each, it runs `arbol-root --root <identifier> list`: the launcher picks that Root's newest working Build of `arbol-root` (BLD-0). It never applies its own Root's manager to another Root.
3. It puts the listings together, because each entry names its Root ([RTM-0](../../arbol-root/specs/00-the-commands.md#the-listing)), and keeps beside each Root what failed: a refusal, no answer, or a listing it could not read. A Root that fails hides no other Root.

The result gives each Root with its state, whether it is current, and its Exchanges in progress with their chat, Trunk, Build, state and signs of life. It holds no chat content: what a chat says is read only by the backend of the chat's own Root, from its own database (ARC-1). A command for an Exchange, such as a stop, goes to the manager of the Root its listing names, `arbol-root --root <that Root> stop <exchange>`.

### When the database cannot be reached

The database is *unreachable* when a call to it fails to connect or does not answer within its 5 seconds, or the Keychain does not give the password. A database that does not answer is not a normal state ([ARC-D53](../architecture/02-chat-exchange-across-components.md#decisions)):

| | |
|---|---|
| Noticing | The first call that fails marks the database unreachable, with the cause in plain words, such as "The database server does not answer at 127.0.0.1:5433" or "The Keychain gave no password for the database". From then on the backend tries to connect every 5 seconds |
| Attention | For as long as it lasts, every window of the Root shows it with the cause, as an *attention* item ([BKD-1](01-the-bridge.md#attention)) |
| Sending | A message is refused by the Trunk with `database_unavailable`, and its Draft stays in the composer (RCT-2); saving a Draft fails with `database_unavailable`, and the window keeps it and sends it again later ([BKD-2](02-elma-chat.md#the-composer)) |
| Reading | A chat the window already shows stays shown. A chat that is opened is refused with `database_unavailable`. Exchanges in progress go on being followed from their folders, which need no database |
| Not yet saved | An Exchange whose record has an end and whose process is gone ended while the database was away. The backend shows its answer from the folder, marked `unsaved`, until settling has saved it ([ARC-D53](../architecture/02-chat-exchange-across-components.md#decisions)) |
| Back | At the first call that succeeds, the backend clears the attention item, runs `arbol-root settle`, writes a note it kept in memory, and tells every window to read again |

### Accounts

The Leather Bag signs in from an Arbol window, and the backend calls the Drivers' account commands directly; Root and Trunk have no part in it ([ARC-0](../architecture/00-components-and-boundaries.md#accounts), [DRV-1](../driver-contract/01-subscriptions.md)). The Drivers are those whose launcher `arbol-<driver>-driver` is in the folder of the launchers, `claude` and `codex` today, and the `driver` of a route names one of them (TRV-0).

| The window asks for | The backend runs |
|---|---|
| Every Subscription of every Driver, with its state and its last usage | `arbol-<driver>-driver subscriptions list` for each Driver |
| One Subscription checked, its usage, its models | `subscriptions check <id>`, `subscriptions usage <id>`, `subscriptions models <id>` |
| Signing in | `subscriptions sign-in <id>`, for the whole attempt |
| Signing out | `subscriptions sign-out <id>` |

These are the only commands of a Driver the backend runs: it never starts a run (ARC-0).

**Signing in** is an exchange in steps (DRV-1). The backend starts `sign-in`, passes each step it prints to the window as it comes, and the window shows it ([BKD-2](02-elma-chat.md#accounts)):

| Step | What happens |
|---|---|
| `open_url` | The window shows the address and its code, and asks the Swift App to open the address in a window that refuses every host not in the step's host list ([BKD-1](01-the-bridge.md#what-the-swift-app-answers-itself)). The Driver notices completion itself |
| `enter_code` | The window collects the code; the backend writes it as one line `{"input": "…"}` on the command's standard input |
| `store_secret` | The window collects the secret in a concealed field and sends it once. The backend stores it in the Keychain item the step names with `/usr/bin/security`, handing it on the command's standard input, never as an argument, so it appears in no list of processes, and keeps, logs and returns nothing of it. The Driver reads the item and goes on by itself |
| `done`, `failed` | The window shows the Subscription signed in, or the error |

One attempt per Subscription runs at a time, as the Driver allows (DRV-1). The backend ends the command when the window cancels, when the window that started it closes, and when the step's `expiresAt` has passed; ending the command cancels the attempt. A Keychain item that `/usr/bin/security` writes can be read by `/usr/bin/security` without a question to the Leather Bag, which is how a Driver reads it (ARC-0, "Secrets").

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

### Tests

A test runs the Builds of the Root it tests on a folder and a database of its own, named with options ([ARC-1](../architecture/01-roots.md#a-place-for-tests)):

| Option of `arbol backend` | In place of | What it names |
|---|---|---|
| `--root-dir <folder>` | `~/Library/Application Support/Arbol/roots/<root>/` | The Root's folder, with its `root.json`, `exchanges/` and the socket |
| `--bin-dir <folder>` | `~/.local/bin` | The folder of the launchers, where a test puts stand-ins of `arbol-root`, `arbol-roots` and the Drivers |
| `--settings-dir <folder>` | `~/.arbol/roots/<root>/` | The folder of `arbol.json` |
| `--database <address>` | The address of `~/.arbol/database.json` and the database of `root.json` | A database on a server of the test's own, such as `postgresql://bkd@%2Ftmp%2Fbkd-1a2b/arbol_test` |

`--root-dir` is refused without `--bin-dir` and `--database`, so that a test that names another Root folder cannot start a real Trunk or reach the chats of a Root in use, as RTM-0 refuses it for the Root manager.

## Requirements

The process:

| ID | The Arbol backend must… | Origin | Verified by |
|---|---|---|---|
| BKD-0.1 | be the command `backend` of a Root's `arbol` Build, work on the Root its Build record names, run once for each Root by an exclusive lock on `backend.lock`, listen on `backend.sock` of the mode 0600 in the Root's folder, print one ready line once it listens, and on SIGTERM, on SIGINT and when its starter ends, close its connections, remove its socket and end within 2 seconds | Changed | unit |
| BKD-0.2 | start for a Root in any state that is named, and serve its windows for as long as its folder, its database and its Builds exist | New | journey |
| BKD-0.3 | take the current Root from `arbol-roots list` whenever it needs it, store it nowhere, and run no listener unless its Root is current | New | unit |
| BKD-0.4 | start `arbol-root`, `arbol-roots` and the Drivers only through their launchers, with the folder of the launchers first on the search path, each in a process group of its own, and wait for none longer than its time limit | New | unit |

The database:

| ID | The Arbol backend must… | Origin | Verified by |
|---|---|---|---|
| BKD-0.5 | read the chat tables directly with SQL of its own, as RCT-3 puts a chat together, leaving out every Exchange that was replaced, and open no database but its Root's | Changed | unit |
| BKD-0.6 | create, change and remove no table, column, index or check, and use for its own rows only the tables of the Root's own layout that `arbol-roots` runs | New | unit |
| BKD-0.7 | change its own tables and its settings file within a Root only by additions that the Root's older Builds can ignore | New | unit |
| BKD-0.8 | write in the chat tables only `chats.title`, when the Leather Bag gives a chat a title or takes it away: the text without spaces at its ends, NULL when nothing is left, and never a placeholder | Changed | unit |
| BKD-0.9 | give every call to the database a time limit of 5 seconds, and serve each window and each call in a task of its own, so that no call holds up another | Changed | unit |

Drafts and sending:

| ID | The Arbol backend must… | Origin | Verified by |
|---|---|---|---|
| BKD-0.10 | keep one Draft for each chat in its table `drafts`, a new chat's under the identifier the chat will have, replace it whole with a revision that only grows, and remove it once its message is accepted and only when its revision is still the one sent | Changed | unit |
| BKD-0.11 | send a message by writing a request file with the chat, the message, the route and the working folder, and no small-call route, into `requests/` of the Root's folder, and running `arbol-root --root <root> start --exchange <id> --request <file>` with the Exchange identifier the window chose; refuse with `invalid_input` before starting anything a route without a Driver, a Subscription and a model, a working folder that is not an absolute path to a folder that exists, and an empty message | Changed | unit |
| BKD-0.12 | count a message as accepted only on its acceptance line, pass every refusal on with its code and message and keep the Draft, and on no answer start the same Exchange again with the same identifier every 15 seconds for at most 60 seconds | Changed | unit, drill |
| BKD-0.13 | send a message again only with `--replaces`, for the Exchange the window names, with the replaced Exchange's working folder and the route the Leather Bag picks, and pass a refusal `cannot_replace` on | New | unit |
| BKD-0.14 | keep a failed, stuck or cancelled Exchange to its own chat: serve every other chat meanwhile, and take a new message for the chat as soon as its Exchange has ended | Changed | drill |

An Exchange in progress:

| ID | The Arbol backend must… | Origin | Verified by |
|---|---|---|---|
| BKD-0.15 | read an Exchange's row first and, while it is open, its folder: `events.jsonl` from its first line and each whole line as it is appended, at least every 250 milliseconds while a window follows it, skipping a folder whose name starts with a dot and a last line without a newline, ignoring every field, line and event type it does not know, taking a record's process as living only when its `pid` exists and was started at its `startedAt`, give or take two seconds, and reading the row again once the folder is gone | Changed | unit |
| BKD-0.16 | on a stop, mark the Exchange `stopping` from the request until it has ended, run `arbol-root --root <root> stop <exchange>`, and then report the final state the database holds | Changed | unit, drill |
| BKD-0.17 | write an answer to the agent's question only after checking it against the question's form, as one whole line of at most 64 KiB with one write on `control` opened for appending, never create the file, wait up to 15 seconds while only `.<exchange>.new` exists, and refuse with `ended` when neither is there | New | unit |
| BKD-0.18 | run `arbol-root --root <root> settle` when it starts, when it sees the database return and after a listing that shows an Exchange whose process is gone, one at a time, and show such an Exchange as interrupted until it is settled | Changed | unit, drill |

Stuck Exchanges:

| ID | The Arbol backend must… | Origin | Verified by |
|---|---|---|---|
| BKD-0.19 | list its Root's Exchanges every 30 seconds while it runs, call an Exchange stuck when its process lives and its heartbeat did not move between two looks at least 90 seconds apart, count both with `CLOCK_UPTIME_RAW`, and never end an Exchange whose heartbeat goes on, whatever it waits for | New | unit, drill |
| BKD-0.20 | end a stuck Exchange without asking with `arbol-root --root <root> stop --force <exchange>`, and record in `exchange_notes` that it was ended because it was stuck, writing the note later when the database is away | Changed | drill |

Restarts and discovery:

| ID | The Arbol backend must… | Origin | Verified by |
|---|---|---|---|
| BKD-0.21 | stop no Exchange when it ends, keep nothing a restart would lose except the marks of a stop under way and of a note not yet written, and at every start settle, list and read again | Kept | drill |
| BKD-0.22 | in the current Root, find the Exchanges of every retained Root at its start and when a window asks, through `arbol-roots list` and each Root's own `arbol-root --root <identifier> list`, report a Root whose listing fails for that Root alone, read no other Root's database or Exchange files, and send a command for an Exchange to the manager of the Root its listing names | New | unit, drill |

A database that cannot be reached:

| ID | The Arbol backend must… | Origin | Verified by |
|---|---|---|---|
| BKD-0.23 | mark the database unreachable at the first call that fails, with the cause, try to connect every 5 seconds, show an attention item in every window of the Root for as long as it lasts, and on its return clear it, settle and have every window read again | New | drill |
| BKD-0.24 | follow the Exchanges in progress from their folders while the database is away, and show the answer of an Exchange whose record has an end and whose process is gone from its folder, marked `unsaved`, until it is settled | New | drill |

Accounts:

| ID | The Arbol backend must… | Origin | Verified by |
|---|---|---|---|
| BKD-0.25 | run of a Driver only its account commands `subscriptions list`, `check`, `usage`, `models`, `sign-in` and `sign-out`, through its launcher | Changed | unit |
| BKD-0.26 | pass each step of `sign-in` to the window as it comes, write the code of an `enter_code` step on the command's standard input, store the secret of a `store_secret` step in the Keychain item the step names through the standard input of `/usr/bin/security`, never keeping, logging or returning it, and end the command when the window cancels or closes or the step has expired | Changed | unit, journey |

Health and tests:

| ID | The Arbol backend must… | Origin | Verified by |
|---|---|---|---|
| BKD-0.27 | measure at its start, every 5 minutes and when a window asks, whether the database server answers, the size of each retained Root's database, the size of the data folder and the free space of its disk | New | unit, journey |
| BKD-0.28 | show an attention item in every window when that free space is below 10 GiB, marked urgent below 2 GiB, naming the free space, the data folder's size and the largest database | New | unit, drill |
| BKD-0.29 | take its Root's folder, the folder of the launchers, its settings folder and its database from `--root-dir`, `--bin-dir`, `--settings-dir` and `--database` when they are given, and refuse `--root-dir` without `--bin-dir` and `--database` | New | unit |

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
  route?: Route;                       // the route a new chat starts with (ARC-0 Route)
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

CREATE TABLE IF NOT EXISTS drafts (
  chat_id         uuid        PRIMARY KEY,
  text            text        NOT NULL,
  working_folder  text        CHECK (working_folder IS NULL OR working_folder LIKE '/%'),
  route           jsonb       CHECK (route IS NULL OR jsonb_typeof(route) = 'object'),
  revision        bigint      NOT NULL CHECK (revision >= 1),
  updated_at      timestamptz NOT NULL
);
COMMENT ON TABLE drafts IS 'One Draft for each chat: what the Leather Bag typed in its composer and has not sent. Written by the Arbol backend alone (BKD-0).';
COMMENT ON COLUMN drafts.chat_id IS 'The chat the Draft belongs to, for example c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b. For a new chat, the identifier the chat will have once a Trunk accepts its first message, so there is no reference to chats.';
COMMENT ON COLUMN drafts.text IS 'The text as the Leather Bag typed it, exactly.';
COMMENT ON COLUMN drafts.working_folder IS 'The absolute folder the composer shows for the next message, for example /Users/sam/repos/shop; NULL when none is chosen.';
COMMENT ON COLUMN drafts.route IS 'The route the composer shows for the next message, in the form of ARC-0, for example {"driver": "claude", "subscription": "anthropic", "model": "sonnet", "effort": "high"}; NULL when none is chosen.';
COMMENT ON COLUMN drafts.revision IS 'Raised by 1 each time the Draft is saved, starting at 1. A message sent with revision 7 removes the Draft only while it still has revision 7.';
COMMENT ON COLUMN drafts.updated_at IS 'When the Draft was last saved.';

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

`kind` is a check that a later Build may not widen inside a Root (RTM-1). A new kind of note therefore needs a table of its own or a new Root; the first thin path needs only `ended_stuck` ([BKD-D6](#decisions)).

The calls, subscriptions and events the backend answers are in [BKD-1](01-the-bridge.md#interface).

## Known problems in version 1

Not to be reproduced.

- **A resident service that also ran the chats.** The windows talked to Arbol Root, which orchestrated every turn, so a restart of it touched every chat, and one failed turn could hold up all of them.
- **"Running" for ever.** When the end of a turn could not be recorded, the chat stayed running, and cancel doubled as repair.
- **Storage on the path of every chat.** A slow write on the loop that served every chat stalled all of them, for up to nine seconds.
- **A database nobody could see.** It ran in a container whose disk the application could not see, and filled that disk twice.
- **Replay held in memory.** The text not yet sealed lived only in a process's memory, so a window opened late, or after a restart, missed it.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#2. One turn's failure could block everything else`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#3. Durable bookkeeping on the streaming path`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#7. Blocking storage calls on the loop that serves every chat`
- `arbol_deprecated_v1:product-spec/03-turn-execution.md#Stored versus live-only, and how a window reconciles them`

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| BKD-D1 | Where does the specification of Arbol itself live, and which window comes first? | A chapter of its own, `~/Artifacts/arbol/backend/`, numbered `BKD`, with three specifications: the backend, the Bridge, and the first window. The first window is a first version of Elma Chat, the conversation UI: one window that lists the chats of its Root and shows one of them, with sending, stopping, answering, sending again and renaming. Branches, search, tags and the other UIs come later. The alternative: a chapter for each part, or the window inside the Swift App's specification (SYL-192) | Open: a question for the owner |
| BKD-D2 | How does the backend start, and how many run? | The command `arbol --root <root> backend`, the same program as the command line (ARC-0), started by the Swift App; one for each Root, by an exclusive lock on a file in the Root's folder; a ready line once its socket listens. A second start finds the first and refuses with `already_running`, and the Swift App connects to the first. The alternative: the Swift App keeps the count itself, which two Swift Apps, or a backend started by hand for development, would break | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D3 | Brain Recipes are not specified yet (SYL-191). Which route does a message go with until they are? | The one the Leather Bag picks in the composer: a Driver with one of its Subscriptions, a model and an effort, from the Drivers' own lists. A chat keeps the route of its last message, and a new chat starts with the route of the Root's last message, or with the `route` of `arbol.json` when the Root has none yet. No small-call route is handed, because the Trivial Trunk makes no small call (TRV-0) and nothing yet resolves one. When Brain Recipes come, the picker offers them beside the routes. The alternative: one fixed route in `arbol.json` and no picker, so changing the model means editing a file | Open: a question for the owner |
| BKD-D4 | In which folder does the agent work? | Each chat has the folder of its last message. A new chat starts in the folder of the Root's last message, and the composer lets the Leather Bag choose another with the Mac's own folder dialog, which the Swift App opens ([BKD-1](01-the-bridge.md#what-the-swift-app-answers-itself)). Changing the folder of a chat that has messages is allowed and is shown, because the agent then starts its own conversation anew (TRV-0). The alternative: one folder for the whole Root in `arbol.json` | Open: a question for the owner |
| BKD-D5 | Where are Drafts kept, and how? | In the Root's database, as ARC-0 says: one row for each chat in the backend's own table `drafts`, with the text, the folder and the route the composer shows, replaced whole each time it is saved and given a revision, so that a message accepted while the Leather Bag typed on in another window removes only the Draft it was sent from. A new chat's Draft is kept under the identifier the chat will get. The alternative: every revision kept, as the glossary allows; no use of the earlier revisions is specified yet | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D6 | Where does Arbol say in a chat that it ended an Exchange because it was stuck (ARC-3)? | A note in a table of the backend's own, `exchange_notes`, which the window shows under the Exchange. The chat tables belong to the Trunks, and Arbol writes only a chat's title there (ARC-0). The alternative: the window infers it from an interrupted Exchange, which cannot tell a stuck one from one whose process was killed | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D7 | Who chooses the identifier of a new Exchange? | The window, a UUID it makes before it calls `chat.send`. When the backend ends before it could answer, the window sends the same call again, and the Trunk answers with the Exchange it accepted (RCT-D17), so one message never runs twice. The alternative: the backend chooses it, and a window whose backend ended cannot tell whether its message was accepted | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D8 | How does the backend follow `events.jsonl`? | It reads the new bytes of the file at least every 250 milliseconds while a window follows the Exchange, whole lines only, from the first line for each window that starts to follow it, and keeps no copy of the lines: the file is the copy. The alternative: the system's notice of a changed file (kqueue), which saves reads but needs a reading by time anyway for a file replaced while it is watched | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D9 | What does the backend do when `arbol-root start` gives no answer? | It starts the same Exchange again with the same identifier every 15 seconds, the longest an acceptance takes (RCT-2), for at most 60 seconds, then passes `no_answer` on and keeps the Draft. A Trunk that accepted it answers as a repeat and starts nothing (RCT-D17) | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D10 | Does the backend store a secret that a sign-in asks for, and how? | Yes: the window collects it in a concealed field and sends it once; the backend writes it to the Keychain item the step names with `/usr/bin/security`, on its standard input, so it is in no argument and no log, and keeps nothing. An item written by `/usr/bin/security` is read by `/usr/bin/security` without a question, as the Driver reads it. The alternative: the window asks the Swift App to store it natively, which needs a native call before SYL-192 | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D11 | When does Arbol warn that space runs out? | When the disk of the database's data folder has less than 10 GiB free, and urgently below 2 GiB, measured every 5 minutes. In version 1 one table grew by about 50 GB a day through a defect; 10 GiB leaves hours to act in such a case and is far above what a day of ordinary chats takes, and 2 GiB is about the room PostgreSQL needs to keep running and vacuum. The alternative: a share of the disk, such as 10 %, which on a large disk warns far too early | Decided 18 October 2026, a technical choice: the proposed default, the values to start with |
| BKD-D12 | How is a measurement of each Root's database size made without opening another Root's database? | `pg_database_size` of each database named in a retained Root's `root.json`, asked on the backend's own connection, which reads the server's catalogue and opens nothing else (ARC-1). The alternative: each Root's backend measures its own, which leaves out every Root whose backend is not running | Decided 18 October 2026, a technical choice: the proposed default |
