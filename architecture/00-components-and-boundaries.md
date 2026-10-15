---
role: authored
spec: ARC-0
status: accepted
---
# Architecture · 00 Components and boundaries

Arbol 2 is a few programs with one job each: the Arbol Swift App, `arbol`, `arbol-root`, `arbol-trunk`, the [Drivers](../GLOSSARY.md#driver) and `arbol-classifier`. This specification states what each of them owns and must never do, which processes exist and for how long, and how one reaches another. It matters because version 1 ran eleven resident services that spoke closed, version-coupled protocols and needed each other to be up: one failed turn could block every chat, and an upgrade could take more than an hour. Here every component is a command-line program, only Arbol itself stays running, and no [Chat Exchange](../GLOSSARY.md#chat-exchange) in progress depends on it.

It follows the conventions of the [Driver Contract](../driver-contract/README.md#conventions) and the additions in this chapter's [README](README.md#conventions).

## Scope

Covered: the components and what each owns, the direction of dependence, the processes and their lifetimes, the two parts of Arbol, the command line, small model calls, accounts, secrets, Brain Recipes and the resolved route, what Arbol Root does, what any Trunk must offer, who writes which data, the database server, the languages, what fails together.

Not covered: the creation, isolation and migration of named Roots ([ARC-1](01-roots.md)); the path of one Chat Exchange through the components ([ARC-2](02-chat-exchange-across-components.md)); the inside of a Trunk, which each Trunk's own specification states; a Trunk's command line and files, which are in the [Root Contract](../../arbol-root/contract/README.md) ([RCT-0](../../arbol-root/contract/00-overview.md) to [RCT-2](../../arbol-root/contract/02-starting-stopping-and-settling.md)); the Drivers ([DRV-0](../driver-contract/00-overview-and-boundary.md)); Builds ([BLD-0](../builds/00-builds-and-versions.md)); what each UI shows; what Telegram does; a message sent while its chat is busy.

## Behaviour

### The components

| Component | Owns | Never |
|---|---|---|
| The [Arbol Swift App](../GLOSSARY.md#arbol-swift-app), built from `arbol-app` | The tray menu, the hotkeys and the native surfaces; the web views that show the UIs | Opens the database. Interprets what a UI and its backend say to each other |
| `arbol` | Every [Surface](../GLOSSARY.md#surface): the renderer bundles of the [UIs](../GLOSSARY.md#ui), the [CLI](../GLOSSARY.md#cli), Telegram. The Arbol backend. [Brain Recipes](../GLOSSARY.md#brain-recipe). The tools `arbol-builds` and `arbol-roots` | Runs an agent itself. Writes a table that a Trunk writes, except a chat's title |
| `arbol-root` | Managing every compatible Trunk of a named Root: choosing compatible Builds, listing and controlling Exchanges, and arranging interrupted settlement. Starting a Trunk for a new Chat Exchange with the Build it picks. The layout of the Root's own tables and the `layout.sql` of its Root Contract version for the chat tables ([RCT-3](../../arbol-root/contract/03-the-chat-tables.md)), and the script that brings chats over from the Root before it ([ARC-D48](#decisions)) | Stays running. Reads chat content. Opens the database. Is needed by an Exchange that was accepted |
| A Trunk (`arbol-trunk/<code name>`, such as `arbol-trunk/trivial`; all in the repository `arbol-trunk`, with one launcher, `arbol-trunk`, for every Trunk) | One Chat Exchange from accepted input to its final state; the rows of the chat tables | Knows a Brain Recipe. Manages an account. Creates or changes a table. Needs Arbol, the Root manager or the database in order to finish |
| A Driver | The vendor tool and its [Subscriptions](../GLOSSARY.md#subscription) (DRV-0) | Keeps a conversation |
| `arbol-classifier` | Classifications through Jev: the key, the pinned model version and the limits of size and time | Interprets a question. Keeps anything between two calls. Starts another component |

Arbol holds the UIs and brings the components together. A named Root is the persistent environment in which compatible Trunks are managed; its `arbol-root` Build provides the management commands. Neither the manager nor a Trunk knows a UI's renderer or presentation. Arbol as the Leather Bag sees it is the Arbol Swift App together with the Arbol backend; the two are built from two repositories, `arbol-app` and `arbol` ([ARC-D21](#decisions)).

The owner's scope decision 8 of 5 October 2026 said that the Root/Trunk split and runtime generations are not carried over. The owner restored the split on 9 October (ARC-D1) and on 12 October gave Root the persistent compatibility environment previously called Ring ([ARC-D47](01-roots.md#decisions)). Root managers and Trunks are command-line programs: a manager invocation ends, and one detached Trunk process owns one Exchange. A compatible release is another Build of the same component; an incompatible environment is another named Root kept alongside the earlier one.

Observed in version 1: Arbol Root was at once the control plane, the gateway of every UI and, in the code, the place where chats were orchestrated. A Trunk Runtime was a resident service that hosted many Exchanges, with an old and a new generation side by side during an upgrade. A Driver was a resident service too.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#6. Many resident services with strict, version-coupled contracts`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#Scope decisions already made by the owner`
- `arbol_deprecated_v1:grafts/arbol-trunks/component-model.md#Target process topology`

### Direction of dependence

```text
Arbol Swift App  →  arbol  →  arbol-root  →  arbol-trunk  →  a Driver  →  the vendor tool
                      └──────────── account commands ───────────┘
                                             arbol-trunk  →  arbol-classifier  →  Jev
```

| Rule | Detail |
|---|---|
| A component starts only what lies to its right | Arbol also starts a Driver directly, and only for account commands. A Trunk starts a Driver and `arbol-classifier` |
| No component holds another's code | A caller starts the other program and reads what it prints or what it leaves in files, as a Driver's caller does (DRV-D2) |
| Nothing reaches leftward | No component starts or calls a component to its left. Until 13 October 2026 a Trunk reached `arbol` for its small model calls, through commands that its settings named ([ARC-D56](#decisions)) |
| Builds are chosen by what they are compatible with | Each caller picks the newest working Build that implements the contract version it speaks ([ARC-1](01-roots.md#builds-and-roots)) |

### The processes

| Process | Started by | Lives |
|---|---|---|
| Arbol Swift App | The [Leather Bag](../GLOSSARY.md#leather-bag) | As long as Arbol runs. One |
| Arbol backend | The Arbol Swift App | The current Root's: as long as Arbol runs. Another Root's: while one of its UIs is open. One per Root in use |
| `arbol-root` | The Arbol backend or the command line | One command, then it ends |
| A Trunk process | `arbol-root`, detached; or a person, in the foreground ([RCT-2](../../arbol-root/contract/02-starting-stopping-and-settling.md)) | One Chat Exchange. It outlives whoever started it, and Arbol |
| A Driver run | The Trunk | One run. It does not outlive its caller (DRV-2) |
| A classification | The Trunk | One call of `arbol-classifier` |
| PostgreSQL | The system | Always |

Resident by design are Arbol, with its two parts, and the database server.

### Arbol: the Swift App and the backend

Arbol is two parts.

The **Arbol Swift App** is the native part. It is a component of its own, `arbol-app`, built from the repository of that name into numbered Builds that belong to no Root ([ARC-D21](#decisions)). It holds the tray menu, the global hotkeys and the native surfaces, shows each UI's renderer bundle in a web view and exposes the [Bridge](../GLOSSARY.md#bridge) to it. It passes every `call` and `subscribe` of the Bridge on to the Arbol backend, over a socket file in the Root's folder that only the owner can open. It does not interpret what it passes on, so a Root can change what its UIs and its backend say to each other without a new Swift App. A UI's renderer bundle is no longer baked into its `.app`: the Swift App loads it from the `arbol` Build of the Root chosen in the tray menu.

A breaking change can still reach the Swift App: the way it starts a backend and loads renderer bundles can change, and so can what its native surfaces show. Each Root's record therefore names the oldest Build of `arbol-app` that the Root works with, written when the Root is made ([ARC-D46](#decisions)). The Swift App reads that from each Root and offers in the tray menu the Roots it is new enough for; for any other Root it says which Build is needed. A new Root may need a new Build of the Swift App. A newer Build keeps working with every Root that still exists, because one tray menu serves all of them.

The **Arbol backend** is a Python process from a Root's `arbol` Build. It:

- answers the Bridge;
- reads the Root's database;
- follows the arriving answers of the Exchanges in progress (ARC-2);
- resolves Brain Recipes;
- calls `arbol-root` and, for accounts, the Drivers;
- holds every *listener*: anything that waits for input while no UI is open, such as Telegram.

The Swift App starts the current Root's backend when Arbol starts, and starts it again when it ends. The backend of another Root starts when one of that Root's UIs is opened from the tray menu, serves only those UIs and ends when the last of them closes.

Listeners run only in the current Root's backend. A Telegram bot can have one reader only, and two Roots can be in use at once. When another Root becomes current, the listeners move to it (ARC-1).

When the backend ends, the UIs lose live updates and incoming Telegram messages wait until it is back. No Chat Exchange is touched. When Arbol quits, both parts end and the Exchanges go on. At the next start, everything shown is read again from the database and the Root's folder.

On every App or backend start, Arbol discovers every retained Root through the common catalogue of `arbol-roots` (ARC-1), chooses a compatible manager Build for each, and asks each manager to list its Exchanges. The result identifies the Root and concrete Trunk Build, so running agents belonging to different Roots and Trunks are rediscovered. Cross-Root discovery uses the common metadata reply; detailed content is read only by the matching Root's backend. Changing the current Root, starting a newer Build or restarting the App changes no accepted Exchange's ownership. A failed or unavailable Root is reported individually and does not hide the others.

Observed in version 1: the Swift App passed Bridge calls to Arbol Root. Each UI was a separate `.app` with its renderer bundle baked in, and each open window was a process of its own.

### The command line

Every command-line program of Arbol 2 can be started by its name alone in any terminal window (ARC-D63): each component through its launcher (BLD-0), and the tools `arbol-builds` and `arbol-roots` (ARC-1). For example, `arbol-classifier info` works in a newly opened terminal window, without a path.

`arbol` on the command line is the same program as the backend, used from a terminal. It is small on purpose and does not mirror the UIs. It has one use: sending a message with a chosen Build, Subscription or Brain Recipe, to try things out.

It needs no running backend: it reads the database and calls `arbol-root` itself, so it still works for diagnosis when the backend is down.

Observed in version 1: `arbol-cli` exposed the same method surface as the UIs, as a thin client of Arbol Root and the other services.

### Small model calls

A Trunk sometimes needs a small model call that is not the agent's work: a title, a classification. It makes both itself, with what lies to its right ([ARC-D56](#decisions)):

| Call | How the Trunk makes it | Which model |
|---|---|---|
| A small text, such as a title | It starts a Driver run itself, with `--tools none` and without a chat session, so that nothing is recorded for it (DRV-2) | The one of the *small-call route*, which Arbol hands down beside the route of the Exchange. Arbol resolves it from a Brain Recipe, by default a cheap one |
| A classification | It starts `arbol-classifier` with the text to judge and a list of questions. Each question names its type and its allowed answers. The result gives for each question the chosen answer and its confidence | The pinned Jev version. Jev is an API of its own with its own key, not a Subscription |

For Jev the questions are the output format: the caller states the type and the allowed answers of each, and the result comes back in that form. `arbol-classifier` adds the key from the Keychain, the pinned model version and the limits of size and time. It does not interpret a question, and the caller decides what a low confidence means. Mycel 2 uses Jev in the same way, with an integration of its own ([MYC-14](../../mycel/specs/14-drift-detection.md)). The reply of a small text call is free text: a Trunk that wants structure asks for it in the prompt and checks the reply itself.

Jev is the one model a Trunk reaches without a Driver.

`arbol-classifier` is a component of its own, built from the repository of that name into numbered Builds that belong to no Root, like a Driver's. It is not a Driver: it has no Subscriptions, no tools and no conversation, and the Driver Contract does not apply to it. It has a short contract of its own with a version number, and a Trunk picks the newest working Build that implements the version it speaks. It keeps nothing between two calls. Its specification is [CLS-0](../../arbol-classifier/specs/00-the-classifier.md).

Rules for a small model call:

| Rule | Detail |
|---|---|
| The small-call route is fixed for the Exchange | Like the route, it is resolved before the Exchange starts and recorded with it. A Trunk that was handed none makes no small text call |
| Input and output of `arbol-classifier` | The request arrives on standard input, the result is one JSON document on standard output, and the command-line rules of DRV-0 hold |
| Optional | A missing, slow or failing small call never fails a Chat Exchange. The Trunk sets the time limit and goes on without the result |
| Nothing leftward | `arbol-classifier` reaches Jev and nothing else, and starts no component. A small text call is a Driver run like any other |

Until 13 October 2026 a Trunk made these calls through two helper commands of `arbol`, `ask` and `jev`, which its settings named (ARC-D17, ARC-D18). The owner replaced them that day: `arbol ask` had Arbol start a Driver for a model call, against the rule that it does so for account commands only, and both tied a Trunk of an older Root to the `arbol` Build of the current Root.

### Accounts

The Leather Bag signs in from an Arbol UI. Arbol calls the Driver's account commands directly; Root and Trunk have no part in it. The Driver's `sign-in` says what to show, such as an `open_url` step, and Arbol shows the page ([DRV-1](../driver-contract/01-subscriptions.md)). The Driver Contract does not change.

Subscriptions are shared by all Roots. They are Driver state, and the Drivers lie outside every Root.

### Secrets

Every secret of Arbol 2 is a Keychain item, and the Leather Bag manages all of them in one place: the Secrets page of Seqoya Lab ([ARC-D62](#decisions)). There a secret is entered, replaced and removed. Each is shown only as set or not set, and its value is never shown again.

| Rule | Detail |
|---|---|
| One place for the Leather Bag | The page lists every secret a component of Arbol 2 needs: the key of a Subscription that signs in with a key (DRV-1), the Jev key of `arbol-classifier` (CLS-0), the password of the database server (ARC-1), the keys Mycel reads (MYC-5), and later the credentials of a listener such as Telegram |
| Arbol writes, a component reads | Arbol stores, replaces and removes the Keychain item that the component names. A component reads its own item and is never handed a secret (DRV-0). The one exception is the Jev key: `arbol-classifier add-key` asks the Leather Bag for it at the terminal and stores it in its own item (CLS-D7 in CLS-0) |
| Write-only | A value can be set and removed. It is never displayed, logged or sent to a renderer |
| Readable without a question | Arbol stores an item so that the program that has to read it can do so without a question to the Leather Bag (MYC-5) |
| Before the page exists | The owner stores an item by hand, with the system's `security` command |

What a Driver does to a key of its own accord stays as the Driver Contract says: it removes a key that the vendor rejected (DRV-1).

Observed in version 1: every credential was a Keychain item. The Secrets page of Seqoya Lab managed the credentials of integrations, each token write-only and shown as configured or not. A separate store of named secrets was managed from the command line only, and the credentials of Subscriptions had items of their own.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/05-intelligence-providers.md#Secrets`

### Brain Recipes and the resolved route

A Brain Recipe belongs to Arbol and to nothing else: it is a shortcut that the Leather Bag picks in a UI or names on the command line. Its logic for choosing a model is free. It may weigh several Subscriptions, for example choose one by repository.

Before an Exchange starts, Arbol resolves the Brain Recipe to a *route*: the Driver, the Subscription, the model and the effort. Only the route goes down, through Root to the Trunk, and with it a *small-call route* of the same form, which Arbol resolves from a Brain Recipe for the Trunk's small text calls ([Small model calls](#small-model-calls)). A Trunk never sees a Brain Recipe.

| Consequence | Detail |
|---|---|
| What ran is known | The route is recorded with the Exchange. A retry or a recovery runs what was accepted, and the UI shows the account and the model that ran |
| A Trunk cannot change the route | When a run ends with `rate_limited` ([DRV-4](../driver-contract/04-errors-and-limits.md)), the Trunk ends the Exchange as failed with that cause. Arbol then offers to send again with what the recipe logic picks next. There is no automatic failover inside a Trunk |
| Listeners resolve too | A message that arrives through a listener has its Brain Recipe resolved like any other, because the backend holds that logic whether or not a UI is open |

### Arbol Root

A **Root** is a named, persistent compatibility environment: its identity, settings, database, Exchange folders and compatible component Builds are described in ARC-1. The Root exists while its stored record and state exist. Its identity survives App, backend and manager restarts.

A **Root Build** is a numbered Build of `arbol-root` made for that Root. A **Root invocation** is one command from such a Build. None stays running, and manager invocations keep nothing between them except files. The manager reads metadata; the Trunks and backend keep their existing database-writing responsibilities. `arbol-roots`, outside individual Roots, creates environments and invokes their migration scripts; `arbol-builds` alone builds components. A Root Build carries, in its folder `layout/`, the chat tables of its Root Contract version, the Root's own tables and the Root's migration script ([ARC-D48](#decisions), [ARC-D49](01-roots.md#decisions), [RTM-1](../../arbol-root/specs/01-builds-layouts-and-migration.md)). `arbol-roots` runs them; no manager command opens the database.

| What it does | How |
|---|---|
| Compatible Trunks (`trunks`) | Prints what `arbol-trunk --root <root> list` prints: every Trunk, its Builds, which fit this Root and which one `run` would start ([RTM-0](../../arbol-root/specs/00-the-commands.md)) |
| Start | Starts the named Trunk, or else the Trivial Trunk, with the Build the caller names or else the one `arbol-trunk list` marks chosen, always with an exact `-v` and the Exchange the caller names with `--exchange` (RTM-0) |
| List | Reads the records in the Root's `exchanges/` folder and checks which processes are alive; it starts nothing and settles nothing (RTM-0). Gives each Exchange's heartbeat and what it waits for ([ARC-3](03-stuck-trunks.md)) |
| Stop | Tells one Exchange to stop, and ends its processes by force when it has not ended after 20 seconds or when that is asked for ([ARC-3](03-stuck-trunks.md)) |
| Settle | Has the chosen Build of the Trivial Trunk save what the folder of each Exchange whose process is gone holds: a finished result with its own final state, and otherwise what had arrived, as interrupted (ARC-2, RTM-0). Arbol runs it when its backend starts, when it sees the database return, and after a listing that shows such an Exchange |

The manager supports every Trunk whose Builds list the Root's Root Contract version (RCT-0). A caller names a Trunk by its code name, or gets the Trivial Trunk, the default Trunk of every Root ([RCT-D2](../../arbol-root/contract/00-overview.md#decisions)). The newest working Build of that Trunk that fits is started, or a named Build that fits. No setting of the Root narrows which Builds may run: a Root only has its list of compatible Trunks ([RCT-D28](../../arbol-root/contract/00-overview.md#decisions)). Build numbers of different components are never compared to choose a Trunk. Different compatible Trunks can have Exchanges in progress in the same Root.

Every listing reads this Root's Exchange records anew and checks their processes. It includes Exchanges started by earlier compatible manager Builds and Trunks started by hand with this Root's identity. Its listing (RTM-0) identifies the Root, Exchange, chat, concrete Trunk component and Build, process and state. The App can combine such replies across Roots without interpreting their Trunk-specific files. A new Root never adopts another Root's Exchanges.

The `arbol-root` manager never reads chat content or opens a database. It knows an Exchange only through its ownership and execution metadata. The Root environment owns a database; its backend and Trunks open it, and its migration script is invoked by `arbol-roots`. Environment ownership changes none of the table writers below.

### What any Trunk must offer

This is everything the rest of Arbol needs from a Trunk. The owner confirmed the seven points on 9 October 2026. Point 6 then read "It can export a chat to the file form and import one"; the owner replaced that the same day by a migration script for each Root (ARC-D34). On 13 October 2026 the owner gave the layout of the chat tables to the Root, which changed points 3 and 6 ([ARC-D48](#decisions)), and replaced the helper commands of point 7 ([ARC-D56](#decisions)).

1. **One process per Chat Exchange.** `arbol-root` starts it detached and hands it the route, the small-call route, the Root, the working folder, the chat and the message (RCT-0).
2. **It shows itself in the Root's `exchanges/` folder.** Its record is there, the arriving answer goes there for the Arbol backend to follow, and stop and answers reach it there.
3. **It writes rows into the chat tables of the Root's database.** The Root provides the tables; a Trunk creates and changes none. Arbol reads them.
4. **It never needs Arbol, the Root manager or the database in order to finish.**
5. **Its Build record lists the versions of the Root Contract it implements** (RCT-0).
6. **It keeps to the `layout.sql` of its Root's Root Contract version** (RCT-3). Every Trunk of a Root writes the same tables, and the migration script of a later Root can copy and convert them (ARC-1).
7. **For small calls it uses what lies to its right:** a Driver run without tools on the small-call route it was handed, and `arbol-classifier`.

How a Trunk prepares context, whether it makes titles and how it retries are not stated here. They belong to the specification of each Trunk, for the Trivial Trunk [TRV-0](../../arbol-trunk/trunks/trivial/specs/00-the-trivial-trunk.md). How the chat tables are laid out belongs to the Root (ARC-1).

A Trunk that needs a table or a column that its Root does not have cannot add it. When the older Builds of the Root can ignore the addition, the Root adds it to its layout. Any other change makes a new Root (ARC-1).

A Trunk also shows that it is alive, and ends itself when its work hangs, so that a stuck one is noticed and ended ([ARC-3](03-stuck-trunks.md)).

### Who writes what

| Data | Where | Written by | Read by |
|---|---|---|---|
| Chats: [Chat Sessions](../GLOSSARY.md#chat-session), Exchanges and their content | The Root's database | The Trunk | The Arbol backend, directly with SQL |
| [Drafts](../GLOSSARY.md#draft) and Arbol's own tables | The Root's database | The Arbol backend | The Arbol backend |
| An Exchange in progress: its record and the arriving answer | The Root's folder | The Trunk | Root manager (record only); Arbol backend (record and arriving answer) |
| Stop, and answers to the agent's questions (`control`) | The Exchange's folder | The Root manager (stop), the Arbol backend (answers) | The Trunk |
| Brain Recipes and the settings of `arbol`; `arbol-root` reads none ([RTM-D3](../../arbol-root/specs/00-the-commands.md#decisions)) | `~/.arbol/roots/<root>/` | The Leather Bag, or Arbol for them | `arbol` |
| Subscriptions and all Driver state | The Driver's state directory (DRV-6) | The Driver | The Driver |
| Builds | The build registry (BLD-0) | `arbol-builds` | Everything that starts a Build |
| The list of Roots | The `root.json` files (ARC-1) | `arbol-roots` | The tray menu, the launchers |

One writer for each table is the rule ([ARC-D10](#decisions)). The chat's title is one exception. Making a title is a Trunk's business, and some Trunks make none. The Leather Bag can change a title through Arbol. There is one title, not a generated and a chosen one. The rule that keeps a Trunk from replacing a title the Leather Bag wrote belongs to the Trunk's specification. The other exception is the migration script of a new Root, which fills that Root's tables once, before the Root is used (ARC-1). Writing a table means writing its rows: the tables themselves are created and changed from the Root's layout alone ([ARC-D48](#decisions)).

Arbol reads the chat tables directly, so each Build of the UIs and the backend is made for the table layout of one Root (ARC-1).

### The database server

Chats are kept in PostgreSQL. The server is Arbol's own and not Mycel's, so that Mycel's extensions and upgrades cannot fail both. It is installed directly on the Mac and not in a container: its data folder is then on the Mac's own disk, where Arbol can report its size like that of any folder. It listens on the loopback address only. Its password is in the Keychain, and settings hold only the address, as with Mycel's store. The address is in the file `~/.arbol/database.json` ([ARC-D51](01-roots.md#decisions)).

Arbol reports the server's health and the size of each Root's database, and warns before space runs out. A server that does not answer is not a normal state, and Arbol calls the Leather Bag's attention to it (ARC-2).

Observed in version 1: PostgreSQL ran in a container whose virtual disk the application could not see. One table grew to 87 GB and filled that disk on 25 September 2026. Two days later it had grown to 184 GiB and filled the enlarged disk, and the chat list stopped loading. Nobody saw either coming.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#3. Durable bookkeeping on the streaming path`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#Anti-goals`
- `arbol_deprecated_v1:product-spec/02-chat-sessions.md#Legacy data inventory`

### Languages

`arbol-root`, `arbol-trunk`, `arbol-classifier`, the Arbol backend and the command line are typed Python with a packaged interpreter, as the Drivers are (DRV-D1, BLD-0). The Arbol Swift App is Swift. The renderer bundles are web pages. The build tool, the launchers and the conformance runner are typed Python too, by the owner's decision of 14 October 2026. They are not Builds: the build tool and the launchers run on the pinned interpreter that is installed with `arbol-builds` ([BLD-D15](../builds/00-builds-and-versions.md#decisions)), and so does `arbol-roots`; a Driver's contract check runs the conformance runner with the Python of the Build it checks.

### What fails together

| Failure | What stops |
|---|---|
| One Trunk process | One Chat Exchange |
| The Arbol backend | Live updates in the UIs, and incoming Telegram messages, until the Swift App has started it again |
| The Arbol Swift App, or Arbol quitting | The UIs. No Exchange |
| One Root's folder or database | That Root's chats |
| The PostgreSQL server | New messages in every Root. Exchanges in progress finish and keep their result (ARC-2) |
| One Driver's state, or a vendor | That Subscription, in every Root |
| `arbol-classifier`, or Jev | Classifications. No Exchange: a Trunk goes on without the result |

## Requirements

Every component:

| ID | A component must… | Origin | Verified by |
|---|---|---|---|
| ARC-0.1 | be a command-line program whose command line and files are its only interfaces, and hold none of another component's code | Changed | unit |
| ARC-0.2 | start only components to its right in the order `arbol`, `arbol-root`, `arbol-trunk`, then a Driver or `arbol-classifier`, and never start or call a component to its left | New | unit |
| ARC-0.3 | be written in typed Python with a packaged interpreter, except the Arbol Swift App and the renderer bundles | New | unit |

Arbol:

| ID | Arbol must… | Origin | Verified by |
|---|---|---|---|
| ARC-0.4 | own every Surface: the UIs, the command line and every listener | Changed | journey |
| ARC-0.5 | consist of the Arbol Swift App, outside every Root, and one Arbol backend for each Root in use | Changed | journey |
| ARC-0.6 | pass Bridge messages between a UI and its Root's backend without interpreting them in the Swift App, and never open the database from it | Changed | unit |
| ARC-0.7 | keep the current Root's backend running as long as Arbol runs, start it again when it ends, and run listeners nowhere else | New | drill |
| ARC-0.8 | read the chat tables directly, and write only its own tables and a chat's title when the Leather Bag changes it | Changed | unit |
| ARC-0.9 | resolve a Brain Recipe to a route before an Exchange starts, and hand down that route and a small-call route and nothing else of the recipe | Changed | unit |
| ARC-0.10 | call the Drivers directly for account commands and for nothing else, and show what the Driver's `sign-in` asks it to show | Changed | journey |
| ARC-0.11 | keep its command line to sending a message with a chosen Build, Subscription or Brain Recipe, and let it work while no backend runs | Changed | unit |
| ARC-0.26 | keep every newer Build of the Arbol Swift App working with every Root that still exists | New | journey |
| ARC-0.14 | report the health of the database server and the size of each Root's database, and warn before space runs out | Changed | journey |
| ARC-0.31 | let the Leather Bag enter, replace and remove every secret of every component on the Secrets page of Seqoya Lab, store each as the Keychain item its component names, show it only as set or not set, and never display, log or hand on its value | Changed | journey |
| ARC-0.32 | be started by its name alone, without a path, in any newly opened terminal window, as must the tools `arbol-builds` and `arbol-roots` | New | probe |

ARC-0.12 and ARC-0.13, on the helper commands `ask` and `jev`, were withdrawn on 13 October 2026 by [ARC-D56](#decisions): a Trunk makes its small model calls itself (ARC-0.24, ARC-0.29, ARC-0.30).

The Root manager:

| ID | The Root manager must… | Origin | Verified by |
|---|---|---|---|
| ARC-0.15 | consist of commands that end, keep nothing between two of them except files, and know the Exchanges in progress from the records in the Root's folder alone | Changed | drill |
| ARC-0.16 | pick for a new Exchange the newest working compatible Build of the caller's named Trunk component or the Trivial Trunk, unless the caller names a compatible Build; refuse a Build that does not fit as the launcher `arbol-trunk` refuses it (RCT-0.9) | Changed | unit |
| ARC-0.17 | never read chat content, never open the database, and build nothing | Changed | unit |
| ARC-0.27 | expose every working Trunk implementation and Build whose Build record lists the named Root's Root Contract version, and manage Exchanges of different compatible implementations in that Root | New | unit: RTM-0.3 |
| ARC-0.28 | distinguish the persistent Root identity from its manager Build and invocation, and keep that identity unchanged across compatible Build updates and restarts | New | drill |

A Trunk, seen from outside:

| ID | A Trunk must… | Origin | Verified by |
|---|---|---|---|
| ARC-0.18 | run one Chat Exchange in one process, detached when `arbol-root` starts it (RCT-2), with the route it was handed | Changed | contract |
| ARC-0.19 | keep its record and the arriving answer in the Root's `exchanges/` folder, and take stop and answers there | Changed | contract |
| ARC-0.20 | write rows into the chat tables of the Root's database, and create or change no table | Changed | contract |
| ARC-0.21 | finish an Exchange while Arbol, the Root manager or the database is absent | Changed | drill |
| ARC-0.22 | list in its Build record the versions of the Root Contract it implements (RCT-0.1) | New | unit |
| ARC-0.24 | make its small text calls as Driver runs without tools on the small-call route it was handed, make its classifications through `arbol-classifier`, and go on when such a call is missing, slow or fails | New | contract: RCT-2.22, scenario R19 of [RCT-4](../../arbol-root/contract/04-conformance.md) |

ARC-0.23, which had each Trunk state the layout of its chat tables, was withdrawn on 13 October 2026 by [ARC-D48](#decisions): the layout belongs to the Root ([ARC-1.28](01-roots.md#requirements)).

The classifier:

| ID | `arbol-classifier` must… | Origin | Verified by |
|---|---|---|---|
| ARC-0.29 | take a classification request on standard input and print one JSON result on standard output, under a contract with a version number of its own, and keep nothing between two calls | New | contract: `classify.choice`, `classify.malformed`, `info.identity`, `classify.writes-nothing`, passed on Build 2 of `arbol-classifier` (SYL-157) |
| ARC-0.30 | add the key from the Keychain, the pinned Jev version and the limits of size and time, interpret no question, and start no component | New | unit: `Classify.test_adds_the_key_the_pinned_model_and_the_limits`, `Classify.test_interprets_no_question`, `Classify.test_starts_nothing_but_the_key_command`, passed on Build 2 of `arbol-classifier` (SYL-157); the key from the Keychain item: unit `Classify.test_starts_nothing_but_security_for_the_key_from_the_keychain`, contract `key.keychain`, passed on Build 3 (SYL-161) |

The database server:

| ID | The database server must… | Origin | Verified by |
|---|---|---|---|
| ARC-0.25 | be Arbol's own, installed directly on the Mac, reachable on the loopback address only, with its password in the Keychain and only its address in settings, in the file `~/.arbol/database.json` | Changed | probe |

## Interface

Proposed. These are sketches of what crosses a boundary; the exact forms are fixed with the component that owns them.

```ts
interface Route {                    // Arbol hands down two for one Chat Exchange: the route of the agent's run and the small-call route
  driver: string;                    // "claude" or "codex"
  subscription: string;              // the Subscription's identifier (DRV-1)
  model: string;
  effort?: string;
}
```

```ts
// arbol-classifier classify         a ClassifyRequest on standard input; the exact form is in CLS-0
interface ClassifyRequest {
  state: unknown;                    // the text or data to judge
  questions: Record<string, {        // by a name the caller chooses; the fields are Jev's own
    type: "choice" | "noul" | "score";
    instructions: unknown;           // the question
    criteria?: unknown;              // for a choice: each option and what it means
  }>;
}
interface ClassifyResult {
  model: string;                     // the exact Jev version that answered
  answers: Record<string, unknown>;  // by the same names; for a choice: the option chosen, its probabilities and the confidence
}
```

When `arbol-classifier` refuses a request or fails, it prints `{ "error": … }` with the error object of DRV-4 and ends with status 1.

## Known problems in version 1

Not to be reproduced.

- **Many resident services.** Eleven background services and four UI applications made up a local application for one person. Two of them could each be correct and still not work together.
- **Root did three jobs.** It was the control plane, the gateway of every UI and the place where chats were orchestrated, so a restart of Root touched everything.
- **A resident Trunk with generations.** An old and a new Trunk Runtime ran side by side during an upgrade, each owning its Exchanges until they ended. The machinery to replace one safely grew larger than the product.
- **A command line that mirrored everything.** `arbol-cli` exposed the whole method surface of the services.
- **A database the application could not see.** Its disk filled twice unnoticed.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#4. The upgrade machinery became a second product`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#6. Many resident services with strict, version-coupled contracts`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#Anti-goals`
- `arbol_deprecated_v1:tools/arbol-cli.md`

## Vocabulary changes this specification requires

The Root environment wording below follows ARC-D47 of 12 October 2026. The entries Arbol, Arbol Root, Arbol Trunk and Arbol Swift App have been aligned with this chapter; remaining vocabulary follow-through is named explicitly.

| Entry | Change |
|---|---|
| Root | The named, persistent compatibility environment of ARC-1, described by the Arbol Root entry. It replaces the former Ring concept (ARC-D47) |
| Arbol backend | New. The Python process of a Root's `arbol` Build that answers the Bridge and holds the listeners |
| Root Contract | New. The contract a Root shares with all its Trunks, in place of the name Trunk Contract ([RCT-D1](../../arbol-root/contract/00-overview.md#decisions)) |
| Trivial Trunk | New. The first Trunk, code name `trivial`: one Driver run with the route it is handed. The default Trunk of every Root (RCT-D2, TRV-0) |
| Code name | The name of a Trunk, one lower-case word such as `trivial`, never a number; part of the Arbol Trunk entry (RCT-D2) |
| [Arbol](../GLOSSARY.md#arbol) | The Arbol Swift App and the Arbol backend, over `arbol-root`, Trunks and Drivers |
| [Arbol Root](../GLOSSARY.md#arbol-root) | A named persistent environment that manages all compatible Trunks. Its separately numbered `arbol-root` Builds provide short-lived management commands; App and backend restarts preserve the Root and rediscover its Exchanges |
| [Arbol Trunk](../GLOSSARY.md#arbol-trunk) | Still the owner of a Chat Exchange from end to end. One process per Exchange |
| [Chat Exchange](../GLOSSARY.md#chat-exchange) | One message of the Leather Bag in a chat and the agent's answer to it, from its acceptance by one Trunk process to its end; one row of `exchanges` (RCT-2, RCT-3). No longer owned by a resident Trunk Runtime, and with no retries or failovers inside it |
| [Draft](../GLOSSARY.md#draft) | Kept by Arbol before a Chat Exchange is accepted, no longer inside one |
| [Trunk Runtime](../GLOSSARY.md#trunk-runtime), [Default Arbol Trunk](../GLOSSARY.md#default-arbol-trunk) | History. There is no resident Trunk and no generation of one |
| [Arbol Swift App](../GLOSSARY.md#arbol-swift-app) | A component of its own, `arbol-app`. Its Builds belong to no Root, and each Root names the oldest of them it works with. It passes the Bridge on to the Arbol backend, not to Root, and loads renderer bundles from a Root's Build |
| [UI](../GLOSSARY.md#ui) | Its renderer bundle is no longer baked into an `.app`. Three remain: Elma Chat, Willo Station, Seqoya Lab |
| [CLI](../GLOSSARY.md#cli) | `arbol`, with few commands. No longer a client of Root that mirrors the UIs |
| [Brain Recipe](../GLOSSARY.md#brain-recipe) | Belongs to Arbol alone. No longer built on one Intelligence Provider: its logic may weigh several Subscriptions. It is resolved to a route before an Exchange starts |
| [Arbol Component](../GLOSSARY.md#arbol-component) | The list changes to the processes of this specification |

## Decisions

The decisions below retain their recorded wording. [ARC-D47](01-roots.md#decisions), decided on 12 October 2026, replaces the former Ring concept with named Roots and gives each Root its compatible Trunks; current requirements and interfaces above use that decision. Earlier terminology here is historical.

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| ARC-D1 | How is Arbol 2 divided? | `arbol` manages the UIs, offers a command line and manages what lies below it; `arbol-root` manages Trunks; `arbol-trunk` wraps the Drivers and owns the whole flow of a Chat Exchange; each is shipped as a command-line program | Decided 9 October 2026 by the owner, who proposed it. It replaces the part of scope decision 8 of 5 October 2026 that dropped the Root/Trunk split; the owner went on with the split after that conflict was pointed out |
| ARC-D2 | What is a running Trunk? | One process that runs one Chat Exchange and ends, in the form of a Driver run. Not a resident service | Decided 9 October 2026 by the owner: the proposed default |
| ARC-D3 | How does Root know which Trunks run? | From the records the Trunks keep on disk. Finding them after a restart is the ordinary listing | Decided 9 October 2026 by the owner: the proposed default |
| ARC-D4 | Who builds a Trunk and registers it? | `arbol-builds` alone, as BLD-0 says. Root picks among the Builds and builds nothing | Decided 9 October 2026 by the owner: the proposed default, against the owner's first proposal that Root builds and registers Trunks |
| ARC-D5 | Is Root resident? | No. It is a set of commands, and the Arbol backend calls them | Decided 9 October 2026 by the owner, together with ARC-D6. The owner's stated aim is a narrow blast radius |
| ARC-D6 | What is Arbol itself? | The Arbol Swift App and a backend where all listeners live. Arbol is the glue that holds the UIs and the components together | Decided 9 October 2026 by the owner, in the owner's own words. It replaces a proposed backend that would have ended with the last UI |
| ARC-D7 | Where do listeners run when two Rings are in use, and does the command line need the backend? | Listeners run in the current Ring's backend only. The command line works without a backend | Decided 9 October 2026 by the owner: the proposed default |
| ARC-D8 | Where is chat data kept? | In a store owned by the Trunk | Decided 9 October 2026 by the owner: in Arbol's PostgreSQL database |
| ARC-D9 | How does Arbol read chat data? | Directly from the tables with SQL, for fast lists | Decided 9 October 2026 by the owner: the proposed default |
| ARC-D10 | Who may write a table? | One component for each table: the Trunk writes Exchanges and their content, Arbol writes Drafts and its own tables, Root writes nothing | Decided 9 October 2026, a technical choice made on the owner's go-ahead: the proposed default. The chat's title is the known exception (ARC-D19) |
| ARC-D11 | Where does PostgreSQL run? | A server of Arbol's own, installed directly on the Mac, not in a container and not shared with Mycel | Decided 9 October 2026 by the owner: the proposed default. Nothing is installed yet. Confirmed by the owner on 13 October 2026; on that day port 5432 of the Mac was served by a container named `arbol-postgres`, and no server was installed directly |
| ARC-D12 | How does the Leather Bag sign in? | From an Arbol UI. Arbol calls the Drivers directly for account commands and shows the page the Driver asks for | Decided 9 October 2026 by the owner |
| ARC-D13 | Where do Brain Recipes belong, and what does a Trunk learn of them? | A recipe is resolved once, above the Trunk, to a Subscription, a model and an effort | Decided 9 October 2026 by the owner: Brain Recipes belong to Arbol as a shortcut for its UIs. A recipe does not belong to one Subscription, because its logic may weigh several, for example by repository. Root hands the Trunk the resolved Subscription, model and effort, and a Trunk knows no Brain Recipe |
| ARC-D14 | What happens on a rate limit? | The Trunk ends the Exchange with that outcome and Arbol resolves again. A Trunk does not fail over by itself | Decided 9 October 2026 by the owner: the proposed default |
| ARC-D15 | Are Subscriptions shared? | By all Rings | Decided 9 October 2026 by the owner |
| ARC-D16 | Which languages? | Python for `arbol-root`, `arbol-trunk`, the Arbol backend and the command line | Decided 9 October 2026 by the owner: Python only. The Node.js build tool, launchers and conformance runner stay as they are: a technical choice made on the owner's go-ahead the same day. Superseded in part on 14 October 2026 by the owner: everything in the `arbol` repository, the build tool, the launchers and the conformance runner included, moves to typed Python (BLD-D15) |
| ARC-D17 | How large is the command line, and what are the helper commands? | A small command line. Two generic helpers, `arbol ask` and `arbol jev`, in place of one command for each purpose. For Jev the questions of the request are the output format | Decided 9 October 2026 by the owner. The helper commands were replaced on 13 October 2026 by ARC-D56; the small command line stays |
| ARC-D18 | Which rules hold for a helper command? | The same form in every Ring; input on standard input and a JSON result; optional for its caller; no way back to a Trunk | Decided 9 October 2026 by the owner: the proposed default. Replaced on 13 October 2026 by ARC-D56 |
| ARC-D19 | Who makes a chat's title? | The Arbol backend, when a chat's first Exchange ends | Decided 9 October 2026 by the owner, against the proposed default: titles are a Trunk's business, and some Trunks make none. There is one title, which the Leather Bag can change. A proposed pair of a generated and a chosen title was refused as too complicated |
| ARC-D20 | Is the inside of a Trunk part of this chapter? | No. It is specified in a session of its own, with the first Trunk. This chapter keeps the seven points above | Decided 9 October 2026 by the owner |
| ARC-D21 | How is the Arbol Swift App versioned and installed? | It is built into numbered Builds, as BLD-0 says of every component and BLD-D8 of an application that stays running. Its Builds belong to no Ring, like those of a Trunk or a Driver | Decided 9 October 2026 by the owner: the Swift App is separated from the Arbol backend and the command line, in a repository of its own. It can have a list of the Rings it can work with, and a breaking change may require the Swift App, or a UI in it, to adapt. A first default, one copy without a build number, was withdrawn the same day, when the owner pointed to the earlier decision on Builds. The repository is `arbol-app`, named by the owner the same day |
| ARC-D46 | How does the Arbol Swift App know which Rings it can work with? | Through the versions it implements of a contract between the Swift App and a Ring's `arbol` Build | Decided 9 October 2026 by the owner, against the proposed default and simpler: the Swift App's version is written into a Ring when the Ring is made, and the Swift App reads it from each Ring. No contract number is kept. It follows that a newer Build must keep working with every Ring that still exists |
| ARC-D22 | What becomes of the [Intelligence Provider](../GLOSSARY.md#intelligence-provider-ip)? | Not used in this chapter. Decided with the specification of Brain Recipes | Decided 13 October 2026 by the owner: the Intelligence Provider stays as a named setup in Arbol, one Subscription with one set of rules, and several may use the same Subscription. Which settings it holds is specified with Brain Recipes |
| ARC-D48 | Who owns the layout of the chat tables, each Trunk or the Root? | The Root. Every Trunk of a Root writes the same tables, and a Trunk that needs different tables means a new Root | Decided 13 October 2026 by the owner: "Trunks should not own DB schema. Arbol Root provide it instead." When a Trunk needs a new table there are two cases: a change that breaks nothing is made by the Trunk's Root in its layout, and a breaking change needs a new Root that covers it. ARC-0.23 is withdrawn and ARC-1.28 takes its place |
| ARC-D56 | How does a Trunk make its small model calls? | A small text, such as a title: the Trunk starts a Driver run without tools itself, on a small-call route that Arbol resolves from a Brain Recipe and hands down beside the route of the Exchange. A classification: a small program of its own to the right of the Trunk, with a short contract of its own. It is not a Driver, because it has no sign-in, no tools and no conversation | Decided 13 October 2026 by the owner: agreed, and the program is built from a new repository, `arbol-classifier`. The owner had found the helper commands inconsistent: `arbol ask` made Arbol start a Driver for a model call, against the rule that it does so for account commands only. This replaces ARC-D18 and the helper commands of ARC-D17, and withdraws ARC-0.12 and ARC-0.13 |
| ARC-D62 | Where does the Leather Bag manage secrets? | On the Secrets page of Seqoya Lab, all of them. Arbol writes the Keychain item a component names, and the component only reads it | Decided 13 October 2026 by the owner: "all secrets still should be managed by Seqoya Secrets page." It was said about the Jev key of `arbol-classifier` and holds for every secret. MYC-D15 said the same of Mycel's keys on 8 October 2026. On 14 October 2026 the owner added a second way for the Jev key alone: `arbol-classifier add-key` (CLS-D7 in CLS-0) |
| ARC-D63 | Can every command-line program of Arbol 2 be started from any terminal by its name? | Not stated: BLD-0 puts the launchers in `~/.local/bin` and says that folder has to be on the owner's search path | Decided 14 October 2026 by the owner: all Arbol command-line tools are available globally in the terminal. ARC-0.32 states it |
