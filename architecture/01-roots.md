---
role: authored
spec: ARC-1
status: accepted
---
# Architecture · 01 Roots

A Root is a named, persistent environment that holds compatible [Arbol Trunks](../GLOSSARY.md#arbol-trunk) together. It has an identity, a folder, a database, settings, and the [Builds](../GLOSSARY.md#build) of `arbol` and `arbol-root` made for it. Several Roots are kept side by side, and each stays usable. This specification states what belongs to a Root, how its manager finds compatible Trunks, how Arbol discovers work across Roots, and how chats move from an older Root to a newer one. It matters because version 1 could run one version only, and its last upgrade tried to convert all of history in place behind a gate that never closed. Here a breaking change, even a complete rewrite of Arbol, starts beside the Root in use and never touches its chats.

It follows the conventions of the [Driver Contract](../driver-contract/README.md#conventions) and the additions in this chapter's [README](README.md#conventions).

## Scope

Covered: Root identity and its manager, compatible Trunks and when a new Root is needed, what belongs to a Root and what lies outside, names, a Root on disk, its database, Builds and Roots, the tray menu and `arbol-roots`, discovery across Roots, the states of a Root and the current Root, moving chats between Roots, settings, storage, a place for tests, what is built first.

Not covered: what the migration script of a given Root contains; the components themselves ([ARC-0](00-components-and-boundaries.md)); an Exchange in progress ([ARC-2](02-chat-exchange-across-components.md)); numbering and the registry of Builds ([BLD-0](../builds/00-builds-and-versions.md)).

## Behaviour

### What a Root is

A **Root** is the persistent identity and compatibility environment. A **Root Build** is a numbered Build of the `arbol-root` program that manages that Root. A **Root invocation** runs one command and ends (ARC-0). The Root exists while none of its commands or its backend is running. Restarting the Arbol backend or Swift App, or replacing the manager with a compatible Root Build, creates no new Root and changes no Exchange ownership.

Inside a Root, compatible Builds come and go and the chats stay: a new Build of `arbol`, of `arbol-root`, of a Trunk or of a Driver works on the same folder and the same database. Root manages every Trunk implementation whose Builds list the Root's [Root Contract](../../arbol-root/contract/README.md) version ([RCT-0](../../arbol-root/contract/00-overview.md#versions-what-fits-together)). A new implementation that satisfies that condition belongs to the same Root; it does not require a new environment merely because its communication strategy is different.

A change makes a new Root when the Builds of the present Root cannot live with it: its Trunks need another Root Contract version, the chat tables or settings change in a way older Builds cannot read, or the backend and UIs change the way they work together incompatibly. A change that older Builds can ignore, such as a new column or a new table, stays inside the Root (BLD-0.13). The newer Root supports the changed components while the older Root keeps managing its own compatible Trunks and their Exchanges.

Root now includes the compatibility environment formerly specified as a Ring ([ARC-D47](#decisions)). It is not a resident service or a Trunk process generation. A running Exchange belongs to one Root identity and one concrete Trunk Build; a new Root or Root Build never takes that Exchange over.

Observed in version 1: exactly one version was installed at a time. Trying an older or a newer build meant installing it over the current one.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/11-administration-and-automation.md#Install and update expectations`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#4. The upgrade machinery became a second product`

### Inside a Root and outside

| Outside every Root: one of each | Belongs to a Root |
|---|---|
| The [Arbol Swift App](../GLOSSARY.md#arbol-swift-app), with the tray menu. Its Builds belong to no Root, and each Root's record names the oldest of them it works with | The Builds of `arbol`: the Arbol backend, the renderer bundles of the [UIs](../GLOSSARY.md#ui), the command line |
| The launchers, the build registry and `arbol-builds` (BLD-0) | The Builds of `arbol-root`, which carry the Root's table layout and its migration script |
| `arbol-roots` and the list of Roots | The Root's folder |
| The [Drivers](../GLOSSARY.md#driver), their state and their [Subscriptions](../GLOSSARY.md#subscription) | The Root's database |
| The Trunk Builds. They are numbered on their own, and each lists the Root Contract versions it implements | The Root's settings |
| The PostgreSQL server | |
| The Builds of `arbol-classifier` (ARC-0) | |

Nothing inside a Root can be relied on in the next one. What lies outside must therefore stay small and change rarely. The launchers, the build registry, `arbol-builds` and `arbol-roots` hold no implementation code or table layout of any Root. They read the small Root and Build records and start the matching programs. The table layout and the migration script of a Root are carried by that Root's `arbol-root` Builds ([ARC-D49](#decisions)). The Arbol Swift App can be reached by a breaking change, so each Root's record names the oldest Build of the Swift App it works with (ARC-0).

### Names

A Root is not numbered. It has a loud name of its own, such as "First Sapling".

A Root has an *identifier*, one lower-case word such as `sapling`, and a *display name*, "First Sapling" ([ARC-D26](#decisions)). The identifier names the Root's folders, its database and its Builds, and is what `--root sapling` takes. The display name is shown in the tray menu and in the header of every UI. Because there is no number, the Root's record says which Root it grew from; that gives the direction in which chats are migrated.

### A Root on disk

Settings are plain files under `~/.arbol`, and state is under the application folder, as with the Drivers (DRV-D3, DRV-D24).

```text
~/.arbol/                                 settings: plain files the owner can edit
  arbol-codex-driver.json                 a Driver's, shared by all Roots
  arbol-classifier.json                   the classifier's, shared by all Roots
  database.json                           the address of the database server
  arbol-builds.json                       when unused Builds are removed (BLD-0)
  arbol-trunk/                            the Trunks' settings (RCT-0)
    trivial.json                          the Trivial Trunk's, shared by all Roots
  roots/
    sapling/
      arbol.json                          Brain Recipes and the settings of the UIs of this Root

~/Library/Application Support/Arbol/      state: written by the programs
  builds/                                 every Build of every component (BLD-0)
  database/                               the database server: its data folder, its socket and its log (ARC-0, ARC-D64)
  drivers/                                Driver state, shared by all Roots (DRV-6)
  roots/
    sapling/
      root.json                           the Root's record
      exchanges/                          one folder for each Chat Exchange in progress (ARC-2)
      backend.sock                        the Arbol backend's socket file, while it runs (ARC-0)
    <second>/                             a second Root, made from First Sapling
      root.json
      exchanges/
```

The list of Roots is nothing more than the `root.json` files. These records have a small shared form that the catalogue can read without loading a Root's code, settings or chat tables. A record that is damaged or missing takes only its own Root out of use, as with a Build's record (BLD-0.10).

<!-- sources:
arbol:src/arbol_roots/model.py#Places
arbol:src/arbol_roots/model.py#catalogue
arbol:src/arbol_roots/model.py#save_record
arbol:src/arbol_roots/model.py#validate_record
arbol:src/arbol_builds/roots.py#valid_root
arbol:tests/test_roots.py#Catalogue
arbol:src/arbol_roots/operations.py#exchanges_directory
arbol:src/arbol_roots/operations.py#Creation
arbol:src/arbol_roots/operations.py#ready
arbol:tests/test_roots.py#Commands.test_roots_ready_repairs_a_legacy_exchange_directory_and_preserves_existing_payload_and_mode
arbol:tests/test_roots.py#Commands.test_roots_ready_refuses_file_and_symlink_exchange_paths_without_changing_the_record
-->

### The database of a Root

Each Root has one database on the one PostgreSQL server (ARC-0), named in its `root.json`, for example `arbol_sapling`. A chat has no column that names a Root, because its database is the Root. A program of one Root never opens the database of another: a UI Build reads the tables it was made for and no others. The one exception is a Root's migration script, which reads the database of the Root it grew from ([below](#moving-chats-between-roots)).

Every table of a Root's database is created from the Root's *table layout*, which the Root's `arbol-root` Builds carry ([ARC-D48](00-components-and-boundaries.md#decisions), [ARC-D49](#decisions)). The chat tables come from the `layout.sql` of the Root's Root Contract version (`contract/<version>/layout.sql` in the `arbol-root` repository), shared by every Root of that version; Arbol's own tables, and the record of where each migrated chat came from, come from the Root's own layout ([RCT-3](../../arbol-root/contract/03-the-chat-tables.md), [RCT-D25](../../arbol-root/contract/03-the-chat-tables.md#decisions)). No Trunk and no backend creates or changes a table. `arbol-roots create` makes the database empty. `arbol-roots migrate` then creates the tables from the layout and, for a Root that grew from another, fills them with that Root's migration script ([ARC-D34](#decisions)). For the first Root it creates the tables and brings nothing over.

Owning a database is an environment property. The `arbol-root` manager never opens the database or reads chat content. `arbol-roots` arranges database creation and runs the layout and the migration script that the target Root's newest working `arbol-root` Build carries; Trunks and the Arbol backend write the rows of their tables (ARC-0). The global tool contains no Root's table layout. It finds the server through the address in `~/.arbol/database.json` and the password in the Keychain ([ARC-D51](#decisions)).

Inside a Root a table changes only by additions that older Builds can ignore. Any other change makes a new Root. An addition is made by the Root: a later `arbol-root` Build of the same Root carries the layout with the addition, and `arbol-roots layout` applies it. A Trunk or a backend that needs a new table or column gets it this way and adds none itself. For the chat tables, an addition belongs to a Root Contract version; how one is made is decided with the first ([RCT-D24](../../arbol-root/contract/03-the-chat-tables.md#decisions)).

`arbol-roots` creates and drops databases through `psql` connected to the
maintenance database `postgres`, as the role in the configured address, never
by opening a Root's database for these commands. Creation uses `CREATE
DATABASE` with `TEMPLATE template0` and UTF-8, so it starts without user
tables; removal uses `DROP DATABASE IF EXISTS`, without `FORCE`. Names are
quoted SQL identifiers, not shell text. The default name is `arbol_<root>`;
when that exceeds PostgreSQL's 63-byte identifier limit it uses `arbol_`,
the first 40 identifier characters, `_` and 16 SHA-256 hex characters. A
create-only `--database-name` selects a different name. Empty, NUL-containing,
overlong, maintenance and template names are refused; no two retained Roots
may claim the same database (ARC-D65).

The address comes from `~/.arbol/database.json`, which names no database or
password. The tool connects to `postgres` by adding that database to the
address. It reads the password with `security find-generic-password -w`,
service `com.sylvan-stack.arbol.database` and the address's role as account,
with a two-second limit. Status 44 means no item and no `PGPASSWORD`; another
failure or timeout is `database_unavailable` naming the Keychain. The psql
environment has only `HOME`, `PATH`, `LANG` and, when found, `PGPASSWORD`.
It disables psql startup files and password prompts, stops on SQL errors,
uses a 30-second limit and never returns a password in a diagnostic. Server SQL refusals are identified by their SQLSTATE, including a confirmed refusal returned with psql status 1; a lost connection or unknown completion remains uncertain. Verbose SQLSTATE diagnostics are captured for this distinction, with source-location noise omitted from the returned error.
[PostgreSQL 17 CREATE DATABASE](https://www.postgresql.org/docs/17/sql-createdatabase.html),
[DROP DATABASE](https://www.postgresql.org/docs/17/sql-dropdatabase.html) and
[psql](https://www.postgresql.org/docs/17/app-psql.html) define these commands
and their maintenance-connection and transaction restrictions.

The catalogue commands take `--roots-dir`, `--settings-dir`,
`--registry-dir` and `--database-config` overrides. Defaults are the Roots
folder, `~/.arbol/roots/`, the Build registry and `~/.arbol/database.json`.
`--psql` and `--security` select executable stand-ins for isolated tests;
normal calls use psql on the search path and `/usr/bin/security`. These
settings belong to this invocation and change no stored defaults. Only
create accepts `--database-name`, `--from`, `--root-contract` and `--name`;
only fail accepts `--reason`. migrate and layout remain SYL-185.

Mutations hold one nonblocking advisory catalogue lock, in
`.catalogue.lock` under the selected Roots folder, through their preflight,
SQL and file changes. A concurrent mutation is `busy`; list/show read atomic
records without this lock. Create refuses existing state/settings targets
before SQL, reserves new folders exclusively, copies settings without
following symlinks, and publishes `root.json` atomically only after confirmed
database creation. It records a private `.creating.json` receipt while doing
so. A later local failure rolls back a confirmed database creation and the
new folders. If database creation has an uncertain outcome, or rollback
itself fails, the receipt and reserved folders remain and the JSON failure
names the recovery location; it does not claim a complete rollback or risk
dropping an existing database. A hard process loss can leave the same receipt.
Remove refuses the current Root under the same lock and refuses duplicate
database claims or symlinked target folders. It drops the database before
removing the named folders; a failed DROP leaves the files intact. A later
filesystem failure is reported truthfully, and remove can be retried because
DROP uses IF EXISTS. No command force-terminates database connections.

<!-- sources:
arbol:src/arbol_roots/database.py#connection
arbol:src/arbol_roots/database.py#keychain_password
arbol:src/arbol_roots/database.py#Database
arbol:src/arbol_roots/operations.py#Creation
arbol:tests/test_roots.py#DatabaseAccess
arbol:tests/test_roots.py#real_server_example
-->

### Builds and Roots

Root-aware selection in BLD-0 qualifies a component's default Build by the Root. Picking the newest Build across all Roots would start a manager made for a different environment:

| Build of `arbol-root` | Made for |
|---|---|
| 5 | First Sapling |
| 6 | First Sapling |
| 7 | The second Root |
| 8 | The second Root |

Opening the First Sapling has to start Build 6, not Build 8. The selection rules are ([ARC-D32](#decisions), with the terminology replaced by ARC-D47):

| Change | Detail |
|---|---|
| A Build names its Root | The record of a Build of `arbol` or of `arbol-root` says which Root it was made for |
| The default is worked out for a Root | The default Build is the working Build with the highest build number among those of the Root that was asked for. When no Root is named, that is the current Root, the newest working one. The whole rule is: the newest working Build of the newest working Root |
| Naming a Root | `--root <identifier>` as the launcher's first argument, in the way of `-v`. A Build named with `-v` needs no Root: its record says which one it belongs to |
| Pruning | Pruning keeps the newest working Build of every Root that still exists |
| Trunks and Drivers | Their Builds belong to no Root. A record says what the Build is compatible with: for a Driver the contract version it implements, and for a Trunk the Root Contract versions it implements. For a Trunk, Root first chooses the caller's named Trunk or else the Trivial Trunk, then the newest working Build of that Trunk that fits (ARC-0, RCT-0) |
| A Root that leaves the chat tables as they were | Its record names the same Root Contract version as the Root before it. A Trunk Build that lists that version serves both Roots and is not built again ([ARC-D40](#decisions)) |
| The Arbol Swift App | A component of its own, `arbol-app`. Its Builds are numbered as BLD-0 says and belong to no Root (ARC-D21) |

Within a Root, `arbol-root trunks` lists every Trunk and its Builds, marking those that list the Root's Root Contract version and the one `run` would start (ARC-0, RCT-0). Compatibility is evaluated for every Trunk component in the registry, not just for versions of a single implementation. For new work, `arbol-root` chooses the named Trunk or else the Trivial Trunk, then the Build `arbol-trunk list` marks chosen, which it starts with an exact `-v` ([RTM-0](../../arbol-root/specs/00-the-commands.md#starting-a-trunk)). It never compares independent components' Build numbers to choose an implementation. An accepted Exchange keeps its recorded concrete Build. The inventory and selection build nothing: `arbol-builds` remains the only build tool.

Since SYL-155, on 16 October 2026, a Build record names its Root or its Trunk Root Contract versions. SYL-179 added the shared Root reader and compatible Trunk selection. Since SYL-158, on 26 October 2026, the launchers of `arbol` and `arbol-root` select only Builds of the named/current Root, and `arbol-builds list` and `show` agree with them. The 5/6 versus 7/8 example above is an actual build-to-launch check. SYL-159 adds count-based pruning that retains a runnable working Build per retained Root and per required Trunk Root Contract version, including preparing/failed Roots and conservative treatment of damaged records (BLD-D22). SYL-160 adds the global catalogue lifecycle, empty database creation/removal, copied settings, readiness and App minimum records. Unused-Build pruning, the per-Root manager and backend/UI behavior remain the work of their own Beats; the specification alone does not supply them.

<!-- sources:
arbol:src/arbol_builds/root_launcher.py#select_root_build
arbol:src/arbol_builds/service.py#list_builds
arbol:src/arbol_builds/service.py#show_build
arbol:tests/test_builds.py#RootComponents
arbol:src/arbol_builds/pruning.py#retained_roots
arbol:src/arbol_builds/service.py#prune_protections
arbol:src/arbol_builds/service.py#prune_builds
arbol:tests/test_builds.py#PruningRoots
-->

### The tray menu and `arbol-roots`

The tray menu of the Arbol Swift App lists the Roots, marks the current one, and opens the UIs of the Root that is picked. Every UI shows the display name of its Root in its header, so the Leather Bag always sees which Root a window belongs to.

One tool, `arbol-roots`, creates and changes Roots. It lies beside `arbol-builds` in the `arbol` repository and, like it, is outside every Root and is not itself a Build. The tray menu calls it. Its commands ([ARC-D35](#decisions)):

| Command | What it does |
|---|---|
| `arbol-roots create <identifier> --name <display name> [--from <root>] [--root-contract <version>]` | Makes the folder, the record and the empty database of a Root in the state `preparing`. Records the oldest Build of `arbol-app` the Root works with, by default the newest working one. With `--from`, records the Root it grows from and copies its settings once. Writes the Root Contract version named with `--root-contract` into the record as `rootContract`; without the option, the version of the `--from` Root, and 1 when there is none (RCT-0.11). It runs no script, because the Root's Builds do not exist yet |
| `arbol-roots list` | Prints the records, newest first, and marks the current Root |
| `arbol-roots show [<identifier>]` | Prints one record; without an identifier, the current Root's |
| `arbol-roots ready <identifier>` | Marks a Root `working`: a new Root that is ready to be used, or a failed one that works again. It does so only while a working Build of the Trivial Trunk lists the Root's Root Contract version (RCT-0.13) |
| `arbol-roots fail <identifier> --reason <text>` | Marks a working Root `failed` |
| `arbol-roots app <identifier> <build number>` | Raises the oldest Build of `arbol-app` the Root works with, when a later Build of the Root needs a newer Swift App |
| `arbol-roots migrate <identifier> [--chat <chat>] [--check]` | Without either option, preparing-only whole migration recreates the destination and runs its verified copied SQL as before. --check or --chat is allowed for a working/failed Root with lineage and matching copied mode support, never drops/recreates a database or changes current/state, and does not apply layouts. They are mutually exclusive; chat is a canonical target copy UUID. The Root script owns comparison/replacement/new-copy behavior and machine replies (RTM-1, D28–D30). A continued copy stays intact and the reply names the imported resultChat; a missing chat is unknown_chat, contention busy, and unsupported/mismatched SQL build_unavailable before SQL. Backend/UI integration uses BKD-0.33/BKD-1.13/BKD-2.24 |
| `arbol-roots layout <identifier>` | Runs `layout/chat-tables.sql` and `layout/root-tables.sql` of the Root's newest working `arbol-root` Build on a Root in use: it adds what is missing and changes nothing else |
| `arbol-roots remove <identifier>` | Removes a Root's folder, settings and database. Never the current Root |

This global tool can list the catalogue and create the first Root without selecting a Root Build first. The per-Root `arbol-root` program manages compatible Trunks and Exchanges inside an existing Root. They are separate entry points with different scopes.

Since SYL-160, on 26 October 2026, create/list/show/ready/fail/app/remove are implemented by typed Python in `arbol:src/arbol_roots/`. `scripts/install_builds.py` installs `arbol-roots` beside `arbol-builds` on the same pinned interpreter, with package staging/rollback and existing launcher refresh retained. The repeatable private drill and explicit disposable-database acceptance are in `scripts/roots_drill.py` and `tests/test_roots.py`. migrate/layout remain SYL-185, the per-Root manager remains SYL-181 onward, and the tray menu remains UI work.

The catalogue and the launchers share Root header validation and the
current-Root function: identifier, state, creation time and Root Contract
version decide whether a record can participate. Catalogue reading safely
ignores unreadable/nonregular records and preserves extra fields; metadata
such as database and App minimum is additionally validated when a command
uses it. Thus minimal compatible records remain readable without a second
current-Root rule. New records contain the complete shared form. A default
show with no current Root is `unknown_root`. list still succeeds with no
current Root, marking none.

Before any runnable working `arbol-app` Build exists, create records `app:
"0"`, a bootstrap sentinel meaning no released App minimum has yet been
chosen. Otherwise it records the newest runnable working App Build. The app
command takes an available runnable working App Build and may raise the
minimum or repeat it unchanged; it never lowers it. This sentinel changes
no real Build numbering and is replaced when a minimum is chosen (ARC-D66).

ready requires a runnable working Trivial Trunk Build whose rootContracts
include the Root's version on every call, including repeated ready. It may
make a preparing or failed Root working, clearing an old failure. fail takes
only a working Root and a nonblank reason. It records the failure time and
reason and preserves creation time, lineage, database, App minimum and Root
Contract. Catalogue order is newest created first, with descending identifier
as the tie breaker, the same tie rule as current selection. No change of
state rewrites the Root Contract.

CLI refusals use `invalid_input`, `unknown_root`, `already_exists`,
`build_unavailable`, `no_fit`, `current_root`, `database_unavailable`, `busy`
or `operation_failed`, always with the shared error code/message envelope
and exit 1. Success is one record, except list's array; remove returns the
removed record. Root creation builds nothing and runs no Root SQL script.
These are technical command and failure choices for SYL-160 (ARC-D67).

<!-- sources:
arbol:src/arbol_roots/cli.py#main
arbol:src/arbol_roots/operations.py#catalogue_lock
arbol:src/arbol_roots/operations.py#create
arbol:src/arbol_roots/operations.py#ready
arbol:src/arbol_roots/operations.py#fail
arbol:src/arbol_roots/operations.py#app
arbol:src/arbol_roots/operations.py#remove
arbol:src/arbol_roots/model.py#list_roots
arbol:src/arbol_roots/model.py#selected
arbol:scripts/install_builds.py#install
arbol:scripts/install_builds.py#install_package
arbol:bin/arbol-roots
arbol:bin/roots_entry.py
arbol:tests/test_roots.py#Commands
-->

### Discovery across Roots

The Swift App and Arbol backend discover running work through the global catalogue, including work in a Root that is not current and has no UI open. `arbol-roots list` supplies the Root records. For each retained Root, the caller selects a working `arbol-root` Build made for that Root and asks it to list its Exchanges. Each manager reads its own Exchange records anew; no resident Root process has to be found or restarted.

The shared listing envelope identifies the Root, Exchange, concrete Trunk component and Build, chat, process and state (ARC-0). It is kept compatible so a global caller can combine those listings without interpreting the different Trunks' files or chat tables. A missing or failing manager is reported for its Root and does not hide the other Roots' work. Management commands go back through a compatible manager of the recorded owning Root. Starting a newer Root, or restarting the App or backend, never reassigns an existing Exchange.

This catalogue is an operational view, not a shared chat database. Detailed chat content is opened through the `arbol` backend and UI Builds made for the owning Root. An older Root's backend may have ended when its last UI closed; its detached Exchanges still run and appear in the global listing without starting that backend. Only the current Root's backend runs listeners.

<!-- sources:
arbol-root:src/arbol_root/listing.py#listing
arbol-root:tests/test_listing_form.py#ListingForm.test_two_root_listings_combine_by_their_exchange_entries
-->

### The states of a Root and the current Root

| State | Meaning | Can be current |
|---|---|---|
| `preparing` | Created and not yet declared ready: its Builds are being made, chats are being migrated, it is being tried | No |
| `working` | Declared ready with `arbol-roots ready` | Yes |
| `failed` | Was `working`, and the owner marked it as not working as expected, with a reason. Its Builds may all have passed their checks | No. It is still opened when it is named |

The *current* Root is the newest Root in the state `working`, where newest means created last. It is not a setting. It is worked out from the records at every start, as the default Build is (BLD-0), so:

- a Root in preparation changes nothing: the Root in use stays current;
- a Root is current from the moment its record says `working`, when no newer Root is working;
- marking the newest Root `failed` makes the Root before it current again.

The current Root is the Root that a command without `--root` goes to, the one whose backend runs as long as Arbol runs, and the only one whose backend runs listeners (ARC-0). When another Root becomes current, the listeners move with it. How a running Arbol hands them over is not specified yet: Telegram, the only listener so far, is postponed, and the hand-over is specified when Telegram is built ([ARC-D52](#decisions)).

An older Root stays usable for as long as its folder, its database and its Builds are kept: it is opened from the tray menu, and chats can be continued in it. The same holds for a failed Root, which the tray menu shows as failed, with the reason. When a newer Root does not work as expected, the owner marks it `failed` and works on in the Root before it. Chats written in the failed Root stay there.

A Root leaves `preparing` only by `arbol-roots ready`, never by a build that succeeds ([ARC-D36](#decisions)). Becoming current moves the listeners, and a new Root should be tried with its migrated chats before it is used.

An older Root can run agents only as long as the Drivers still serve the version of the Driver Contract its Trunks speak. It stays readable for as long as it is kept.

<!-- sources:
arbol:src/arbol_builds/roots.py#current_root
arbol:src/arbol_builds/roots.py#read_roots
arbol:tests/test_builds.py#Roots
arbol:src/arbol_roots/operations.py#ready
arbol:src/arbol_roots/operations.py#fail
arbol:src/arbol_roots/model.py#list_roots
-->

### Moving chats between Roots

A new Root starts with the chats of the Root it grew from. They are brought over while the Root is prepared, by the new Root's *migration script*, and the originals stay where they are. Creating the new Root stops or moves no Exchange in the older Root. Its Trunk continues there with its original Root identity and concrete Build.

A new Root always means that something broke, but seldom in every table. The script therefore goes table by table:

| A table that… | What the script does |
|---|---|
| did not change | Copies it as it is, structure and rows |
| changed | Creates it in the new layout and converts the rows |
| is new | Creates it |

```text
arbol-roots create <second> --name "<its loud name>" --from sapling
  1. makes the empty database arbol_<second>
  2. copies First Sapling's settings
arbol-builds build arbol-root --root <second>
  3. makes a Build of arbol-root for the second Root; it carries the second Root's table layout and migration script in layout/
arbol-roots migrate <second>
  4. creates the second Root's tables from the layout
  5. runs the second Root's migration script, which only reads arbol_sapling
  → The second Root is `preparing`. First Sapling stays current and untouched
```

| Rule | Detail |
|---|---|
| One script for each Root | It is written together with the breaking change, for the one step from the Root the new Root grows from. It is the only program of the newer Root that knows the older tables |
| The older Root is only read | The script changes and removes nothing there |
| Repeatable | While the new Root is `preparing`, its database can be thrown away and the migration run again as often as needed. The Root in use stays current meanwhile, so a migration never stands in the way of daily work. `arbol-roots migrate` makes it empty again before each run, and refuses once the Root has left `preparing` (RTM-1) |
| A failure is loud | A migration that fails leaves the new Root `preparing` and names what failed. Nothing is cut or skipped silently |
| Nothing in progress is carried over | An Exchange that was open in the older Root is copied as history at the migration snapshot. The migration script writes its target copy as interrupted, ended at the time of the snapshot (RTM-1); the original Exchange and its process continue untouched in the older Root |
| Text is kept exactly | The text of every message arrives as it was. A Driver continues the vendor's saved conversation only when the history it is sent matches what that conversation covers, and otherwise builds it again from the history ([DRV-6](../driver-contract/06-state-and-simultaneous-calls.md)). An agent therefore never remembers turns of another Root that its own transcript does not show |
| One direction | From the Root a Root grew from, into that Root. Converting from a newer Root to an older one is not built |

Both Roots can be written. A chat can therefore go on in the older Root after the migration (what the newer Root does about it is not in the first thin path: [RTM-D12](../../arbol-root/specs/01-builds-layouts-and-migration.md#decisions)):

| The chat was continued… | What the newer Root does |
|---|---|
| in the older Root only | Marks its copy *stale* and offers to bring it over again. The new copy replaces the old one |
| in the newer Root only | Nothing. The older Root cannot show that its chat is behind: its code was written before the newer Root existed |
| in both | Marks its copy stale. Bringing it over again adds the older Root's chat as a second chat beside the first, so that nothing written in either Root is lost |

For this each migrated chat records the Root and the chat it came from, and how far that original had got, in the table `migrated_chats` of the Root's own layout (RTM-1).

<!-- sources:
arbol-root:roots/jensen/migration-modes.json
arbol-root:roots/jensen/layout.sql
arbol-root:roots/jensen/migrate.sql
arbol-root:scripts/migration_modes.py#read_modes
arbol-root:scripts/migration_modes.py#branch
arbol-root:scripts/migration_protocol.py#mode_protocol
arbol-root:scripts/sql_support.py#BuildInput
arbol-root:scripts/chat_migration_check.py#check_modes
arbol-root:scripts/chat_migration_check.py#copied
arbol-root:scripts/check_migration.py#check_migration
arbol-root:scripts/verify_sql_build.py#qualify
arbol-root:tests/test_layout_copy.py#LayoutCopy.test_optional_modes_copy_exactly_and_bad_or_lineageless_capabilities_write_nothing
arbol-root:tests/test_chat_migration.py#Capabilities
arbol-root:tests/test_chat_migration.py#ChatModes
arbol-root:roots/sapling/drills/chat_reimport_drills.py#upgrade
arbol-root:roots/sapling/drills/chat_reimport_drills.py#replace
arbol-root:roots/sapling/drills/chat_reimport_drills.py#diverged
arbol-root:roots/sapling/drills/chat_reimport_drills.py#copied
arbol-root:roots/sapling/drills/chat_reimport_drills.py#run
arbol-root:tests/test_migration_drills.py#ReimportJudgment
arbol:src/arbol_roots/cli.py#main
arbol:src/arbol_roots/sql.py#selected_sql
arbol:src/arbol_roots/sql.py#migrate
arbol:src/arbol_roots/sql.py#mode_result
arbol:src/arbol_roots/database.py#Database
arbol:tests/test_roots_sql.py#InUseModes
-->

Only the migration script may look into the older database, so it also makes this comparison. The Arbol backend of the newer Root runs `arbol-roots migrate <identifier> --check` when it starts and when a UI of that Root opens its chat list. The check changes nothing in the older Root and nothing in the newer one except the stale marks. This timing is the proposed default: the owner was not sure of it on 13 October 2026 and had it built first, to see how it works ([ARC-D50](#decisions)). The check is not in the first thin path (RTM-D12).

The same script brings one chat over again ([ARC-D41](#decisions)). A migration is therefore written so that it can run for all chats or for one; the form for one chat is not in the first thin path (RTM-D12). No file form is used: the older tables are read directly, by this script alone.

A Root's migration script is kept with the Root's table layout in the `arbol-root` repository, and the Root's `arbol-root` Builds carry both ([ARC-D49](#decisions), which replaced ARC-D45 on 13 October 2026). `arbol-roots` runs the script of the newest working Build.

Observed in version 1: the replacement runtime was to take over only after every past attempt, receipt and obligation had been converted. That gate was still open at its 137th checkpoint, more than ninety of them within three days. An earlier cutover truncated 34 oversized records in place and kept the originals in a backup table.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#8. Proving replaced delivering`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#5. Everyday operations cost in proportion to total history`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#Anti-goals`

<!-- sources:
arbol-root:scripts/check_migration.py#run_migration
arbol-root:scripts/check_migration.py#judge
arbol-root:scripts/migration_protocol.py#protocol
arbol-root:scripts/migration_fixtures.py#seed
arbol-root:tests/test_migration_check.py
arbol:src/arbol_roots/sql.py#selected_sql
arbol:src/arbol_roots/sql.py#migrate
arbol:src/arbol_roots/sql.py#layout
arbol:src/arbol_roots/database.py#Database.file
arbol:tests/test_roots_sql.py
arbol:scripts/roots_sql_drill.py#drill
-->

<!-- sources:
arbol-root:roots/sapling/drills/migration_drills.py#preparing
arbol-root:roots/sapling/drills/migration_drills.py#failure
arbol-root:roots/sapling/drills/migration_drills.py#open_exchange
arbol-root:roots/sapling/drills/migration_drills.py#ready
arbol-root:roots/sapling/drills/migration_drills.py#continuation
arbol-root:roots/sapling/drills/migration_drills.py#judge_history
arbol-root:roots/sapling/drills/migration_drills.py#sql_row_equal
arbol-root:roots/sapling/drills/migration_drills.py#reconcile_continuation
arbol-root:roots/sapling/drills/migration_support.py#fingerprints
arbol-root:roots/sapling/drills/migration_support.py#MigrationFrame
arbol-root:roots/sapling/drills/trunk_drill_support.py#Exchange
-->

### Settings

The settings of `arbol`, Brain Recipes among them, are kept for each Root in `~/.arbol/roots/<root>/`; `arbol-root` reads no settings file ([RTM-D3](../../arbol-root/specs/00-the-commands.md#decisions)). Otherwise the programs of an older Root would have to read a file whose shape a newer Root had changed. `~/.arbol` itself keeps only the settings of what lies outside every Root: the Drivers, each Trunk that has settings in `arbol-trunk/<code name>.json` ([RCT-0](../../arbol-root/contract/00-overview.md)), `arbol-classifier`, the address of the database server in `database.json` ([ARC-D51](#decisions)) and the rule for removing unused Builds in `arbol-builds.json` (BLD-0). This narrows DRV-D24, which gave every component one file in `~/.arbol`.

The settings are copied once from the Root a new Root grows from, when it is created ([ARC-D33](#decisions)). After that the two sets are separate.

<!-- sources:
arbol:src/arbol_roots/operations.py#create
arbol:tests/test_roots.py#Commands.test_roots_create_from_records_lineage_inherits_or_overrides_contract_and_copies_settings_once
-->

### Storage

Every Root holds a full copy of the chats that were migrated into it. Arbol shows the size of each Root's database (ARC-0). A Root is removed only by `arbol-roots remove`, and nothing removes one by itself.

### A place for tests

A test does not get a Root of its own. It runs the Builds of the very Root it tests, on another folder and another database that are named with options, as a Driver takes `--state-dir` and `arbol-builds` takes `--registry-dir` ([ARC-D37](#decisions)). `arbol-root`, which opens no database, takes `--root-dir` and `--bin-dir` (RTM-0); the layouts and the migration script are checked on a database server of the check's own (RTM-1). A Trunk Build, which belongs to no Root, is tested in a separate test folder of its own, a temporary home, as a Driver is in its conformance suite (DRV-5); the live checks are the one exception, because they need the real test account kept in the Driver's test state folder ([RCT-4](../../arbol-root/contract/04-conformance.md), [RCT-D29](../../arbol-root/contract/04-conformance.md#decisions)). No test can then reach the chats of a Root in use.

Observed in version 1: a test fixture dropped every schema with a test name in whatever database it reached, and a scratch database alone did not isolate sockets and launch records.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#Validation practice`

<!-- sources:
arbol:scripts/roots_drill.py#drill
arbol:tests/test_roots.py#real_server_example
arbol:tests/test_roots.py#Commands.test_roots_default_state_and_settings_paths_stay_inside_the_callers_private_home
arbol:pyproject.toml
arbol-root:scripts/verify_build.py#qualify
arbol-root:tests/test_commands.py#Commands
arbol-root:tests/test_layout_copy.py#LayoutCopy
-->

### What is built first

One thin path through every part before anything is widened: the tray menu, opening the first Root, sending one message, a Trunk, a Driver, the streamed answer, the saved chat, the chat opened again. A second, trivial Root is created at the start and the chat is migrated into it. Otherwise the first real breaking change would be the first time a migration ever runs.

Observed in version 1: each architectural step was accepted on tests and isolated harnesses while the installed application was seldom run from end to end. The first real cutover then exposed 24 defects in two days.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#1. The architecture grew faster than the installed product was exercised`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#Validation practice`

<!-- sources:
arbol-root:roots/sapling/drills/sapling_creation.py#make_sapling
arbol-root:roots/sapling/drills/sapling_messages.py#real_messages
arbol-root:roots/sapling/drills/sapling_messages.py#usage_available
arbol-root:roots/sapling/drills/drill_support.py#Budget
arbol-root:tests/test_sapling_drills.py#Creation
-->

<!-- sources:
arbol-root:roots/sapling/drills/trunk_drill_support.py#Frame
arbol-root:roots/sapling/drills/trunk_drill_support.py#StandinHome
arbol-root:roots/sapling/drills/trunk_drill_support.py#existing_rows_unchanged
arbol-root:roots/sapling/drills/trunk_drill_support.py#processes
arbol-root:roots/sapling/drills/trunk_drills.py#entry
arbol-root:roots/sapling/drills/trunk_drills.py#run_drill
arbol-root:roots/sapling/drills/run-trunk-drills.py
arbol-root:roots/sapling/drills/drill-trunk-killed.py
arbol-root:roots/sapling/drills/drill-trunk-hangs.py
arbol-root:roots/sapling/drills/drill-starter-gone.py
arbol-root:roots/sapling/drills/drill-database-away-mid-run.py
arbol-root:roots/sapling/drills/drill-database-away-through-end.py
arbol-root:roots/sapling/drills/drill-folder-unwritable.py
arbol-root:roots/sapling/drills/drill-failed-exchange.py
arbol-root:roots/sapling/drills/drill-cancelled-exchange.py
arbol-root:tests/test_trunk_drills.py#PrivateDriver
arbol-root:tests/test_trunk_drills.py#ProcessAndRows
arbol-root:tests/test_sapling_drills.py#Outage.test_installed_stop_completes_smart_shutdown_with_an_established_private_connection
-->

<!-- sources:
arbol-root:roots/sapling/drills/stopping_drills.py#newer_build
arbol-root:roots/sapling/drills/stopping_drills.py#reuse_build
arbol-root:roots/sapling/drills/stopping_drills.py#build_journal
arbol-root:roots/sapling/drills/stopping_drills.py#run_drill
arbol-root:roots/sapling/drills/stopping_drills.py#entry
arbol-root:roots/sapling/drills/stopping_support.py#frozen
arbol-root:roots/sapling/drills/stopping_support.py#Manager
arbol-root:roots/sapling/drills/stopping_child.py#main
arbol-root:roots/sapling/drills/stopping_wrapper.py#main
arbol-root:tests/test_stopping_drills.py#Freeze
arbol-root:tests/test_stopping_drills.py#IgnoredChild
arbol-root:tests/test_stopping_drills.py#StoppingJudgment
arbol-root:roots/sapling/drills/drill-stop-obeyed.py
arbol-root:roots/sapling/drills/drill-stop-not-obeyed.py
arbol-root:roots/sapling/drills/drill-stop-end-already-written.py
arbol-root:roots/sapling/drills/drill-stop-force.py
arbol-root:roots/sapling/drills/drill-stop-force-ignored-term.py
arbol-root:roots/sapling/drills/drill-root-killed-while-waiting.py
arbol-root:roots/sapling/drills/drill-root-killed-while-forcing.py
arbol-root:roots/sapling/drills/drill-newer-build.py
arbol-root:roots/sapling/drills/run-stopping-drills.py
-->

<!-- sources:
arbol-root:roots/sapling/drills/jensen_creation.py#entry
arbol-root:roots/sapling/drills/migration_drills.py#qualified
arbol-root:roots/sapling/drills/migration_drills.py#original_chat
arbol-root:roots/sapling/drills/migration_drills.py#chat_history
arbol-root:roots/sapling/drills/migration_drills.py#target_preserved
arbol-root:roots/sapling/drills/migration_drills.py#run_phase
arbol-root:roots/sapling/drills/migration_drills.py#entry
arbol-root:tests/test_migration_drills.py#ContinuationJudgment
arbol-root:tests/test_migration_drills.py#ReadyJudgment
arbol-root:tests/test_migration_drills.py#RootOwnership
arbol-root:roots/sapling/drills/make-second-root.py
arbol-root:roots/sapling/drills/drill-migration-fails.py
arbol-root:roots/sapling/drills/drill-migration-open-exchange.py
arbol-root:roots/sapling/drills/second-root-ready.py
arbol-root:roots/sapling/drills/migrated-chat-goes-on.py
-->

## Requirements

Roots:

| ID | Arbol must… | Origin | Verified by |
|---|---|---|---|
| ARC-1.1 | give every Root an identifier, a display name, a folder, a database, settings and its own Builds of `arbol` and `arbol-root` | New | catalogue: `roots.create`, `roots.create-from`, `roots.default-paths`; installed `sapling.creation` in roots/sapling/drills/make-sapling.py (SYL-186) creates the real First Sapling, qualifies manager Build 1 and proves empty tables/current selection. Backend/App Builds remain their own work Installed `sapling.second-root-created` creates Jensen Root/jensen with copied settings, empty database, lineage/contract and qualified manager Build 4 (SYL-189). |
| ARC-1.2 | keep inside a Root only changes that the older Builds of that Root can ignore, and make a new Root for any other change | Changed | Root own-table part: unit check `layout`, `root.layout-compatible-additions`, `root.layout-edited-statement`, `root.layout-required-column`, `root.layout-new-constraints`, `root.layout-baseline`; private `root.private-sql-builds` (SYL-184). Contract v1 has no chat-table additions (RCT-D24); settings, backend and windows wait for Arbol's own specification |
| ARC-1.3 | hold no code and no table layout of any Root in the launchers, the build registry, `arbol-builds` and `arbol-roots` | New | unit: `roots.boundary` (SYL-160), `builds.outside-roots` (SYL-155); global catalogue/Build tools hold no Root implementation or table layout |
| ARC-1.4 | take the `root.json` files as the whole list of Roots, and let a damaged or missing record take only its own Root out of use | New | drill: `arbol:scripts/roots_drill.py`, checked by `roots.damaged-drill`; unit: `roots.catalogue-damaged`, `roots.catalogue` (SYL-160); existing launcher record checks |
| ARC-1.5 | keep the chats of each Root in a database of its own, and never open one Root's database from a program of another, except from the migration script of the Root that grows from it | New | catalogue lifecycle part: unit `roots.database-access`, `roots.database-ddl`, `roots.boundary`; real-server acceptance proves separate empty databases (SYL-160). Root data readers, backend and migration isolation remain their own components/Beats |
| ARC-1.6 | list the Roots in the tray menu, mark the current one, open the UIs of the Root that is picked, and show the Root's display name in the header of every UI | New | journey |
| ARC-1.7 | take as the current Root the newest Root in the state `working`, worked out from the records at every start with no stored setting, send a command without a named Root to it, and run listeners in its backend alone | New | catalogue/current part: unit `roots.catalogue`, `roots.states`, `roots.damaged-drill` (SYL-160); shared reader/launchers: `builds.current-root`, `builds.root-records`, `builds.root-refusals`. Backend listeners and hand-over remain pending Installed `sapling.jensen-ready` makes Jensen current, verifies default manager selection and explicit Sapling use (SYL-189). |
| ARC-1.8 | keep an older Root usable, for reading and for continuing chats, as long as its folder, database and Builds exist | New | Root/Trunk path: installed `sapling.jensen-ready` leaves Sapling working and completes an explicit Sapling message after Jensen becomes current; migrated stand-in and real Haiku continuation in Jensen leave every Sapling row unchanged (SYL-189). Reading/continuation through a UI remains backend/UI work |
| ARC-1.9 | create Roots, mark them ready or failed, and remove them through `arbol-roots` alone, and remove one only on command and never the current one | New | unit: `roots.create`, `roots.ready`, `roots.states`, `roots.remove`, `roots.remove-refusal`, `roots.remove-retry`, `roots.state-busy`, `roots.catalogue-lock`, `roots.creation-rollback`, `roots.creation-recovery`, `roots.creation-identity`, `roots.sqlstate`, `roots.exchanges`, `roots.exchanges-refusal`; disposable installed-server `real_server_example` (SYL-160/SYL-186) and real First Sapling creation/legacy-directory repair Installed `sapling.second-root-created`/`sapling.jensen-ready` create/ready Jensen only through the global tool and preserve both Roots (SYL-189). |
| ARC-1.10 | keep the settings of `arbol` for each Root in `~/.arbol/roots/<root>/` (`arbol-root` reads none: RTM-D3) | Changed | unit: `roots.default-paths`, `roots.create-from`, `roots.create-from-failure`; real-server settings-copy acceptance (SYL-160). The per-Root manager still reads no settings (RTM-0) |
| ARC-1.11 | show the size of each Root's database | New | journey |
| ARC-1.21 | let the owner mark a working Root `failed` with a reason, never take a failed Root as current, and still open it when it is named | New | catalogue part: unit `roots.states`, `roots.catalogue`; explicit failed-Root launch: `builds.root-refusals` (SYL-158). Backend/UI opening remains pending |
| ARC-1.23 | name in each Root's record the oldest Build of `arbol-app` the Root works with, and offer in the tray menu only the Roots the running Swift App is new enough for | New | record/minimum part: unit `roots.create`, `roots.app` with bootstrap sentinel 0 (SYL-160). Swift App tray filtering remains pending |
| ARC-1.22 | run a test with the Builds of the Root under test on a folder and a database of the test's own, and a test of a Trunk Build in a separate test folder of its own, a temporary home, except its live checks (RCT-4, RCT-D29), so that it cannot reach the chats of a Root in use | Changed | catalogue part: unit `roots.default-paths`, `roots.create`, `roots.damaged-drill`, and real-server acceptance using only unique disposable database names (SYL-160). Trunk Build isolation is RCT-4.1; Root Build checks remain SYL-181/SYL-184 |
| ARC-1.24 | support all working Trunk implementations and Builds whose Build records list the Root's Root Contract version, and expose them through `arbol-root trunks` | New | unit: `root.trunks`, `root.trunks-refusal`; private `root.private-build` (SYL-181), plus `builds.trunk-list`/selection checks (SYL-179) |
| ARC-1.25 | rediscover Exchanges across retained Roots through the shared Root catalogue and each Root's matching manager, isolate a failing Root's listing, and route management to the recorded owning Root | New | Root manager listing/combinability part: unit `root.list-combined`, `root.list-form`, `root.list-states`, `root.list-boundary` (SYL-182). Catalogue discovery, asking every retained Root, failure isolation and routing are specified by accepted BKD-0.22 and remain backend implementation/drill work |
| ARC-1.26 | keep a Root's identity independent of its manager invocation and compatible Build replacements, and change no established Exchange ownership when the App or backend restarts | New | Root manager part: installed `sapling.newer-build` qualifies compatible manager replacement with all three packaged checks, unchanged Root/catalogue/current and accepted Exchange ownership, stop and settle; `sapling.root-killed-while-waiting`/`sapling.root-killed-while-forcing` recover command restarts (SYL-188). App/backend restart part remains their drills |
| ARC-1.28 | create and change every table of a Root's database from the table layout that the Root's `arbol-root` Builds carry, apply to a Root in use only additions that its older Builds can ignore, for the chat tables as their Root Contract version allows (RCT-D24), and let no Trunk and no backend create or change a table | New | Root-owned copied layouts: `roots.sql-selection`, `roots.sql-preflight`, `roots.sql-pruning`, `roots.layout`, `roots.layout-cli`; explicit installed-server `roots.runtime-sql` proves additive/repeated layouts and earlier rows unchanged (SYL-185). Compatibility is qualified by the SYL-184 layout check; contract v1 permits no additions (RCT-D24). The backend no-DDL part is accepted BKD-0.6 and remains backend implementation work |

Builds:

| ID | The registry, its tool and the launchers must… | Origin | Verified by |
|---|---|---|---|
| ARC-1.12 | record for a Build of `arbol` or `arbol-root` the Root it was made for | New | unit: `builds.root-of-build` |
| ARC-1.13 | take as the default the working Build with the highest build number among the Builds of the Root asked for, and the current Root when none is named | Changed | unit: `builds.root-default`, `builds.root-refusals`, `builds.root-inventory` (SYL-158) |
| ARC-1.14 | keep the newest working Build of every existing Root when pruning | Changed | unit: `builds.prune-roots`, `builds.prune-root-retention`, `builds.prune-root-catalogue-refusal`, `builds.prune-catalogue`, `builds.prune-catalogue-failure` (SYL-159); Trunk version protection: `builds.prune-versions`, `builds.prune-version-fallback`, `builds.prune-version-refusal` |

Moving chats:

| ID | A migration must… | Origin | Verified by |
|---|---|---|---|
| ARC-1.15 | read the database of the older Root without changing or removing anything there, and be the only program of the newer Root that knows the older tables | Changed | Migration check part: `root.migration-whole`, `root.migration-protocol`, `root.migration-protocol-refusal`, source rows/schema unchanged and READ ONLY write refusal (SYL-184). arbol-roots execution is SYL-185; installed `sapling.jensen-failure` and `sapling.jensen-open-exchange` prove unchanged source fingerprints/current selection during failure and successful snapshot copying (SYL-189) |
| ARC-1.16 | go in one direction, from the Root a Root grew from, and be repeatable: for the whole database while the Root is `preparing`, and for one chat afterwards (one chat is not in the first thin path: RTM-D12) | New | Whole-database preparing-only/repeatable path: `roots.migrate`, `roots.migrate-refusal`, `roots.migrate-failure`, `roots.migrate-interruption`; explicit installed-server `roots.runtime-sql` proves recreated destination, exact rows and unchanged source (SYL-185). One chat is not in the first thin path (RTM-D12), remains SYL-195; installed `sapling.jensen-failure` then `sapling.jensen-open-exchange` prove successful explicit retry from an empty preparing destination, and `sapling.jensen-ready` refuses whole migration after ready (SYL-189) |
| ARC-1.17 | copy a table that did not change as it is, convert the rows of a table that changed, keep the text of every message exactly as it was, and transfer no running Exchange or process | Changed | Unchanged-table copy part: `root.migration-whole`, `root.migration-text-fault`, `root.migration-open-fault`, `root.migration-snapshot-fault`, all five tables and exact text/JSON (SYL-184). Converting a changed table waits for the first Root that changes one; installed `sapling.jensen-open-exchange` copies exact saved rows while the original remains in Sapling, then completes there with target snapshot unchanged (SYL-189) |
| ARC-1.18 | leave the Root in use current and untouched while it runs and when it fails, and name what failed without cutting or skipping anything silently | Changed | Installed `sapling.jensen-failure` returns a named bounded database refusal, leaves Jensen preparing/empty and Sapling current/unchanged, and restores the unchanged service; `sapling.jensen-open-exchange` succeeds afterwards without source changes. Only explicit `sapling.jensen-ready` changes current selection (SYL-189). Tray menu preparing state and failure presentation remain App/backend/UI work |
| ARC-1.19 | mark a migrated chat stale when its original has gone further, checking when the Arbol backend of the newer Root starts and when its chat list is opened, and offer to bring it over again (not in the first thin path: RTM-D12) | New | journey |
| ARC-1.20 | replace a copy only when the copy was not continued in the newer Root, and otherwise bring the original in as a second chat (not in the first thin path: RTM-D12) | New | unit |
| ARC-1.27 | leave an original running Exchange and its process untouched in the older Root, and write only its target history copy as interrupted when that Exchange was open at the migration snapshot | New | Installed `sapling.jensen-open-exchange` verifies the accepted Sapling Root/Exchange/chat/Trunk/Build plus same live PID/start/group during the copied snapshot, interrupts only the Jensen row at that snapshot, and then lets the original complete only in Sapling with Jensen unchanged (SYL-189) |
| ARC-1.29 | be carried, together with the Root's table layout, by the `arbol-root` Builds of the Root it fills, and be run on a Root's database by `arbol-roots` alone, and otherwise only by the checks of an `arbol-root` Build on a database server of the check's own (RTM-1) | New | Copied-file selection and psql execution: `roots.sql-selection`, `roots.sql-preflight`, `roots.sql-databases`, `roots.layout`, `roots.migrate`, `roots.sql-failure`, `roots.sql-timeout`; explicit installed-server `roots.runtime-sql` (SYL-185). Build checks use their own server (SYL-184); Root manager commands never connect (SYL-181–183) |

## Interface

Proposed. The shared Root record and listing envelope are read outside any one Root and must retain compatibility. They expose identity and operational metadata; Root-specific settings, chat schemas and Trunk file formats remain behind the matching programs.

```ts
interface RootRecord {                 // root.json
  root: string;                        // the identifier, "sapling"
  name: string;                        // the display name, "First Sapling"
  status: "preparing" | "working" | "failed";
  createdAt: string;                   // ISO 8601, UTC; the newest working Root is the current one
  grewFrom?: string;                   // the identifier of the Root it grew from; absent for the first Root
  database: string;                    // the name of its database, "arbol_sapling"
  app: string;                         // the oldest Build of arbol-app this Root works with, "7"; "0" before any App Build (ARC-D66)
  rootContract: number;                // the one version of the Root Contract this Root uses, 1; never changes (RCT-0)
  failed?: { at: string; reason: string };
}
```

The Root and compatibility fields of the `BuildRecord` of BLD-0 are:

```ts
interface BuildRecord {
  // …
  root?: string;                       // a Build of arbol or arbol-root: the Root it was made for. Absent for a Trunk, a Driver and the Arbol Swift App
  contract?: number;                   // a Driver: the contract version it implements
  rootContracts?: number[];            // a Trunk: the versions of the Root Contract it implements, [1] (RCT-0)
}
```

The launcher of `arbol` and of `arbol-root` takes `--root <identifier>` as its first argument, in the way BLD-0 gives `-v`. With neither, it starts the default Build of the current Root. A caller discovering work across Roots names each Root explicitly; it never applies the current Root's manager to all of them.

```ts
interface DatabaseSettings {           // ~/.arbol/database.json
  address: string;                     // "postgresql://arbol@127.0.0.1:5432"; never a password
}
```

The password of the database server is the Keychain item with the service `com.sylvan-stack.arbol.database` and, as its account, the role that the address names.

Each command of `arbol-roots` prints JSON on standard output: `list` an array of records, each with a `current` boolean, the others one record. A refused command prints `{ error: { code, message } }` and ends with status 1, as `arbol-builds` does.

## Known problems in version 1

Not to be reproduced.

- **One version at a time.** A new version could be tried only by installing it over the one in use.
- **Conversion as a release gate.** The replacement was to take over only after all historical execution state had been converted. The gate never closed.
- **History rewritten during an upgrade.** Oversized records were truncated in place, and a paging bug would have silently used 6% of the largest history.
- **Tests that could reach real data.** A fixture dropped schemas in whatever database it reached.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#5. Everyday operations cost in proportion to total history`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#8. Proving replaced delivering`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#Validation practice`

## Decisions

The entries below retain the terminology and outcomes recorded on 9 October 2026. ARC-D47 supersedes Ring terminology and the separation between a Ring environment and its Root manager. The data isolation, compatibility, coexistence and migration decisions continue to apply to named Roots unless ARC-D47 states otherwise. Historical proposals and the earlier implementation status are not current interface descriptions.

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| ARC-D23 | How does Arbol live with breaking changes? | A second place, with its own folder and database, is made on purpose and stays rare | Decided 9 October 2026 by the owner: breaking changes are expected, a complete rewrite of Arbol included, and must be supported. Each one is a named entry in a list, its name is shown in the header or the tray menu, it has a database of its own, and the chats of the entry before it are migrated into its tables while the originals stay |
| ARC-D24 | What is such an entry called? | Ring | Decided 9 October 2026 by the owner: Ring, in place of the owner's "milestone" or "generation" |
| ARC-D25 | How are Rings named? | By number, as in the examples of the discussion | Decided 9 October 2026 by the owner: not by number. Each has a loud name of its own |
| ARC-D26 | What stands for the number? | An identifier of one lower-case word and a display name. The Ring's record names the Ring it grew from | Decided 9 October 2026 by the owner: the proposed default |
| ARC-D27 | What lies outside every Ring? | The tray menu, the launchers, the build registry and the list of Rings, with none of a Ring's code | Decided 9 October 2026 by the owner: the proposed default; the tray menu has this function. Drivers and Trunks are numbered on their own, and Root chooses among them |
| ARC-D28 | One database for all Rings, or one for each? | One for each Ring, on one server | Decided 9 October 2026 by the owner: Rings that break with each other have their own databases |
| ARC-D29 | What does an import bring, and when? | Conversation content only; a new Ring works with fresh chats first; one chat at a time and repeatable; a failing chat is listed | Decided 9 October 2026 by the owner: the proposed default. Changed the same day by ARC-D34: a new Ring starts with the chats migrated, table by table, and not with fresh chats only |
| ARC-D30 | May an older Ring still be written once a newer one exists? | No. It becomes read-only unless the Leather Bag switches back | Decided 9 October 2026 by the owner, against the proposed default: an older Ring stays usable, for the case that the newer one fails. A chat continued there is marked stale in the newer Ring and can be imported again. Converting from a newer Ring to an older one is not built now |
| ARC-D31 | A chat was continued in both Rings and is imported again. What happens? | It arrives as a second chat beside the first. Nothing is overwritten | Decided 9 October 2026 by the owner: the proposed default |
| ARC-D41 | Who reads the older Ring, when a Ring is created and when a stale chat is brought over again? | The older Ring's own Trunk Build exports chats to a documented file form, and the newer Ring imports that. No program of the newer Ring reads the older tables | Decided 9 October 2026 by the owner as proposed, then replaced the same day by ARC-D34: the newer Ring's migration script reads the older tables. That the same script also brings one chat over again, and that the file form is dropped, is a technical choice made on the owner's go-ahead the same day |
| ARC-D32 | How does BLD-0 learn of Rings? | A Build names its Ring; the default Build is worked out for the Ring asked for, and for the current Ring when none is named; `--ring` names a Ring to a launcher; pruning keeps the newest working Build of every Ring | Decided 9 October 2026 by the owner, with one point made exact: when no Ring is named, the rule is the newest working Build of the newest working Ring. BLD-0 itself is not yet changed |
| ARC-D33 | Where are a Ring's settings? | In `~/.arbol/rings/<ring>/`, copied once from the Ring it grows from | Decided 9 October 2026 by the owner: the proposed default, the single copy included |
| ARC-D34 | Who creates a Ring's database and tables, and may a table change inside a Ring? | `arbol-rings` creates the database empty, each table is created by the component that writes it, and inside a Ring a table changes only by additions | Decided 9 October 2026 by the owner, against the proposed default: a new Ring's database is not created empty. A new Ring always means breaking changes, but not in every table, so a script is written for it that copies the structure and the data of the parts that did not change, creates new tables for the parts that broke, and migrates their data to the new layout. That a table changes only by additions inside a Ring was agreed by the owner the same day |
| ARC-D35 | Which tool manages Rings? | `arbol-rings`, beside `arbol-builds` in the `arbol` repository, outside every Ring and not itself a Build | Decided 9 October 2026 by the owner. Its commands, in the table above, are a technical choice made on the owner's go-ahead the same day |
| ARC-D36 | Which states does a Ring have, and which Ring is current? | `preparing`, `current`, `kept`, with the current Ring marked by a command | Decided 9 October 2026 by the owner, against the proposed default: a state `failed` that the owner sets, for a Ring whose build succeeded and which still does not work as expected; and the newest working Ring is the one used when none is named (ARC-D32). From the two it follows that being current is worked out and not stored, and the states are `preparing`, `working`, `failed`. That a Ring leaves `preparing` only by a command is a technical choice made on the owner's go-ahead the same day |
| ARC-D37 | Where do tests run? | On another folder and another database, named with options, with the Builds of an existing Ring | Decided 9 October 2026 by the owner: the proposed default. The Ring is the very Ring that is to be tested |
| ARC-D38 | How much space may Rings take? | Arbol shows the size of each Ring's database, and a Ring is removed only on command | Decided 9 October 2026 by the owner: the proposed default |
| ARC-D39 | What is built first? | One thin path through every part, and a trivial second Ring with an import at the start | Decided 9 October 2026 by the owner: the proposed default |
| ARC-D45 | Where is a Ring's migration script kept? | With the definition of the Ring, beside `arbol-rings` in the `arbol` repository. It is written together with the breaking change | Decided 9 October 2026 by the owner: the proposed default. Replaced on 13 October 2026 by ARC-D49: the script is kept in the `arbol-root` repository and carried by the Root's `arbol-root` Builds |
| ARC-D40 | A new Ring leaves the chat tables as they were. Must every Trunk be built again for it? | No. The Ring's record names the Ring whose table layout it uses, and a Trunk Build that writes that layout serves both | Decided 9 October 2026 by the owner: the proposed default. The exact form is fixed with the Trunk Contract. Changed 15 October 2026 by [RCT-D3](../../arbol-root/contract/00-overview.md#decisions): the exact form is a shared Root Contract version, which each Root's record names as `rootContract`, in place of `chatTablesOf` |
| ARC-D47 | Are Rings needed as a separate concept, and what does Root organize? | A named Root holds all compatible Trunk implementations and inherits the environment identity, isolation, settings, retained Builds and migration responsibilities; Roots coexist across breaking changes | Decided 12 October 2026 by the owner: use Roots in place of Rings throughout the current specifications. Root is the persistent compatibility environment, a Root Build is its versioned manager, and a manager invocation is one command. An incompatible change creates another retained Root; compatible implementations and Builds stay in the same Root. Arbol discovers running Exchanges across Roots after restart, through each owning Root's compatible manager, without transferring accepted work. This supersedes ARC-D24's name and the former separation between the Ring environment and Root manager. The shared `root.json` catalogue, `roots/` paths, `--root` option and global `arbol-roots` bootstrap tool are the corresponding interface choices |
| ARC-D49 | Where are a Root's table layout and its migration script kept, and who creates the tables? | In the `arbol-root` repository, carried by that Root's `arbol-root` Builds and run by `arbol-roots`. The layout covers every table of the Root's database, Arbol's own tables included. The script of the first Root only creates the tables. Creating a Root and filling it become two steps: create the record, build, then migrate | Decided 13 October 2026 by the owner: agreed. It follows from ARC-D48 and replaces ARC-D45, which kept the script beside `arbol-roots` in the `arbol` repository. The command `arbol-roots layout` and the option `migrate --check` are a technical choice made the same day |
| ARC-D50 | When does a newer Root check whether a chat went on in the older Root? | When the Arbol backend of the newer Root starts and when its chat list is opened. The check only compares and marks | Decided 13 October 2026 by the owner, for now: "Not sure yet. Let's implement your suggestion first and we'll see how it works." To be looked at again once it is in use. Changed 15 October 2026 by [RTM-D12](../../arbol-root/specs/01-builds-layouts-and-migration.md#decisions): not built in the first thin path; the owner left the choice to the agent; SYL-195 settles the Root forms and additive backend/Bridge/UI bindings in RTM-D28–D30 and BKD-D26; their actual integration remains the Backend Arc |
| ARC-D51 | In which file is the address of the database server, and under which name is its password in the Keychain? | `~/.arbol/database.json`, with the address and nothing else. The Keychain item has the service `com.sylvan-stack.arbol.database` and the role of the address as its account | Decided 13 October 2026 by the owner: the agent chooses the file. Chosen: the proposed default. The owner confirmed the direct install of ARC-D11 the same day |
| ARC-D52 | How does a running Arbol hand the listeners over when another Root becomes current? | The Arbol Swift App watches the Root records. When the current Root changes, it stops the listeners of the old backend and then starts the new backend | Decided 13 October 2026 by the owner: Telegram is postponed. It is the only listener so far, so the hand-over is specified when Telegram is built, and the proposed default is not adopted |
| ARC-D65 | How does arbol-roots make and remove a Root database? | psql on postgres as the configured role, minimal environment plus a Keychain password read within two seconds; CREATE DATABASE from template0 in UTF-8, DROP DATABASE IF EXISTS without FORCE, quoted/validated names and a 30-second limit. Distinguish confirmed server SQL refusals by SQLSTATE from uncertain connection/completion outcomes, including psql status 1. Serialize catalogue mutations; reserve folders exclusively and publish the record after creation. Roll back confirmed creation failures; preserve a private receipt when an outcome or rollback is uncertain. DROP failure leaves files intact, and later filesystem failure permits a truthful retry | Chosen 26 October 2026 as a technical choice for SYL-160, before implementation |
| ARC-D66 | What App minimum is recorded before an arbol-app Build exists? | app is the string 0 as a bootstrap sentinel; otherwise create uses the newest runnable working App Build. The app command names an available runnable working Build and raises or repeats the minimum without lowering it; the sentinel is no real Build | Chosen 26 October 2026 as a technical choice for SYL-160, before implementation |
| ARC-D67 | What are the catalogue command, record and failure boundaries? | Shared header validation/current selection with the launchers, atomic writes preserving compatible fields, command-specific metadata validation, newest-created order and identifier tie break. Invocation overrides isolate roots/settings/registry/database and executable stand-ins; mutations use a nonblocking catalogue lock. ready checks a runnable working compatible Trivial Trunk each time; fail takes only working Roots; remove never takes current or a shared database claim. Refusals use the documented code/message envelope. Creation neither builds nor runs Root SQL | Chosen 26 October 2026 as a technical choice for SYL-160, before implementation |
| ARC-D68 | How are the First Roots drills repeatable without silently recreating data or overspending the approved messages? | Standard-library scripts in roots/sapling/drills call component CLIs and inspect SQL in read-only transactions; they import no other component’s code. Actual manager Builds read merged readonly source, even while a new drill is being developed. Creation owns only a newly absent sapling and preserves receipts; a replay never migrates or deletes an existing Root blindly. The two-message script uses the owner’s normal signed-in anthropic Subscription and haiku, no small-call route, and reserves each submission under a private locked durable ledger before starting. The owner’s existing ten-message allowance across SYL-186–189 is enforced; an ambiguous attempt is never automatically retried and still counts until its outcome is proved. A known vendor rate-limit retry deadline blocks fresh drill submissions until it passes, even when the cached usage report says capacity remains. A reached cached window expires for preflight only when its valid fetchedAt predates its valid resetsAt and that reset has passed. A future reset, an unknown/malformed timestamp or a reached report fetched after its reset still refuses; any other active window also refuses. The Driver exposes its last run’s report, so this expiry allows one explicitly approved fresh check after reset without falsifying the cached report or automatically retrying a submission. Evidence and usage/cost stay outside Git, with aggregate counts and replay details in hand-overs | Decided 27 October 2026, technical choice before SYL-186 code; the ten-message limit and normal owner Subscription were authorized on 15 October and are not new defaults |
| ARC-D69 | How is an installed-server failure drill restored after failure or interruption? | Verify the expected launch agent and a healthy server, and require no running Exchanges before stopping it. Use launchctl bootout for the recorded service. A smart shutdown can leave existing sessions usable, so if its postmaster.pid remains, require the same PID/data-directory/start header recorded before bootout and complete pg_ctl stop -m fast -w -t 20 on that exact data directory through the fixed PostgreSQL 17 tool. Require the PID file gone as well as failed new connections before the drill body. Prove this on a private server with an open connection. Bootstrap the unchanged saved plist afterwards. A scoped SIGINT/SIGTERM handler unwinds through restoration, with prior handlers restored; verify the server answers again before reporting a verdict. Test the same stop/restore control flow on a throwaway server first. A restoration failure is reported with an actionable receipt, never hidden by a successful acceptance-refusal check | Decided 27 October 2026, technical choice for SYL-186: reuse the existing service definition rather than reinstall/reconfigure the server during a failure drill |
| ARC-D70 | Who establishes a fresh Root’s exchanges directory before a Trunk locks it? | arbol-roots create makes a private mode-0700 exchanges directory inside its exclusively owned new Root before publishing root.json. ready idempotently ensures that directory for an older Root before marking it working, after finding a fitting Trivial Build. Existing contents and modes stay; a non-directory or symlink refuses before changing the Root record. No database schema, Trunk behavior or Root Contract version changes | Decided 27 October 2026 during SYL-186: the first real start exposed the catalogue omission; RCT-0 already says the Root gives this directory and TRV-D16 locks its existing descriptor |
| ARC-D71 | How do First Sapling’s installed Trunk failure drills isolate the Driver and leave the Root usable? | Each deterministic Exchange gets a temporary stand-in HOME, its existing RCT-4 scenario/release files and received log, a private wrapper that fixes that HOME and interpreter, and a byte-identical copy of the installed arbol-trunk launcher passed through --bin-dir. The Trunk keeps the actual Root/database, while the stand-in sees no owner credentials or normal Driver state. Reuse the existing R13/R7/R12/R2/R5/R11 scripts without changing the Driver or production component. Verify the recorded Exchange/PID/start/group before signalling only its Trunk; wait for owned group/stand-in children and restore private modes. Outage drills require all other retained Roots/normal Driver runs idle, allow only the drill’s named Exchanges, and restore the unchanged service even after a failed assertion or SIGINT/SIGTERM. Compare all pre-existing Root rows before/after; preserve new drill history. Use real timing for the sixty-second watch/final database retry and an owned pseudo-terminal for starter loss. Only the explicit killed-run --real check reserves one approved normal Haiku submission; the aggregate runner uses no real vendor call. No ambiguous submission is automatically retried; partial runs report only usage/cost actually observed, with missing cost unknown. Judgments use RCT-3’s exact row mapping: whole top-level text blocks persist, fragments do not become messages, and settling never invents a whole text event from them. A first real killed run exposed an overbroad drill assertion after it settled correctly; qualify its saved acceptance/events/rows and a stand-in continuation, without another vendor call. Evidence is private outside Git; default CLI calls only preflight, --run performs the named drill | Chosen 27 October 2026 before SYL-187 code; extends ARC-D68/D69 without changing Trunk behavior or the shared ten-submission limit |
| ARC-D72 | How do the installed stopping/manager drills freeze and recover owned processes without leaving work stuck? | Reuse D71’s private stand-in frame and real timing. A freeze guard anchors a positive PID/start identity, sends SIGSTOP only to that owned process, and always sends SIGCONT to the same surviving identity on normal exit, failure or catchable interruption; it never resumes a reused PID. Manager commands are direct children with captured JSON replies/control/termination markers and are killed only by their owning Popen handle. A private run wrapper may start one same-group child that records but ignores SIGTERM, for the actual five-second escalation window, with PID/start metadata and no credential access. Cleanup restores/thaws before final owned stop/settle and refuses success with a survivor. An already ended live record follows RTM-D20/D21 and returns its end without forcing; ended:saved follows RTM-D6 and is checked against persisted state. The newer manager is built only from clean merged readonly while a stand-in Exchange runs, with its exact source and all packaged checks recorded; the aggregate reuses that qualified receipt only after verifying the retained installed Build/source/status and same Root identity. No real vendor submission or branch installation is part of these checks | Chosen 27 October 2026 before SYL-188 code; the old draft’s force-after-end expectation is superseded by the accepted manager specification |
| ARC-D73 | How are the installed Jensen migration failure and live-copy drills observed without changing its packaged SQL or source history? | Jensen Root/jensen is the owner’s RTM-D24 choice. Each explicit phase has unique private receipts and refuses automatic replay over existing state or an ambiguous outcome. Snapshot/fingerprint all contract tables (and destination provenance) in one REPEATABLE READ READ ONLY transaction, with fixed UTC and deterministic primary-key order; hash the server’s encoded row values so text, JSON numbers and whitespace are not silently normalized through Python floats. For the fault only, with no unrelated Exchange or normal Driver run, hold a temporary ACCESS EXCLUSIVE lock on source chats without changing rows; pg_stat_activity and pg_blocking_pids must show the migration’s source COPY blocked by that exact owned lock. Find only the psql direct child of the started migration command, verify PID/start/group and executable before freezing it, completely stop the existing service through D69’s verified shutdown, thaw the same client, capture a bounded explicit refusal, then restore the unchanged service before fingerprint/empty-destination judgments. Guards terminate/reap only owned clients and release locks/copy folders on failure or catchable interruption. For the successful snapshot use a private R12 stand-in held at a saved checkpoint: its original Trunk/group/record remains alive in Sapling while migration copies its open Exchange as interrupted; release it only after exact snapshot/provenance comparison and then prove it completes only in Sapling. No SQL/runtime change or vendor loop is part of the fault/copy checks; current selection changes only at explicit ready, and one later explicit budgeted Haiku continuation uses the owner’s normal Subscription | Chosen 27 October 2026 before SYL-189 code; PostgreSQL 17 locking/blocker documentation checked; private process/server tests precede installed use |
| ARC-D74 | How is the deferred one-chat path added after the first two Roots work? | Keep SQL/table knowledge in the Root package, advertise/verify optional modes, and keep whole preparing migration separate from exclusive non-dropping in-use check/chat calls. Preserve a continued copy and return a new result chat. First Roots SYL-195 qualifies the core; explicit Backend Arc leaves implement startup/list checks, Bridge metadata/call, UI action and journeys. No current Root, running ownership or source data is changed by comparison/import | Chosen 27 October 2026 before SYL-195 code; owner’s D50 timing default retained, no automatic retry of ambiguous copy mutation |
