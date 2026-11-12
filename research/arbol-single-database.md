---
role: authored
---
# Arbol with one database

Research for the Arbol Single Database Saga, 12 November 2026. Repository `arbol`, with the Trunk, App, Driver and Forester boundaries included. Depth: standard. The code excerpts are from the local working sources. Source Ref index resolution and retrieval are deferred.

The owner chose to remove Arbol Roots, apply schema changes to one existing PostgreSQL database, adapt incompatible Trunks, snapshot data before schema changes and recover code from known Git revisions. Preserve the Trunk code names, independent Builds and detached Exchange lifecycle. The owner accepted maintenance and authorized an empty start after backup. The transition keeps historical application data in recoverable backups. The [draft specification](../architecture/04-single-database.md) uses the evidence below to define the target behavior.

## Database migration and recovery

The existing whole-migration command selects an explicit destination from the catalogue and recreates it. Its comparison and one-chat modes return before reaching the drop. The whole-migration path is therefore unsuitable for routine in-place upgrades. The clean start removes the need for a one-time history importer.

`arbol:src/arbol_roots/sql.py`, lines 237–242 (`d05503c` baseline):

```python
                        if error.sqlstate in ("55P03","40P01"):
                            raise Refused("busy", "The selected chat or provenance is busy; nothing was replaced.") from error
                        raise
                    return {"root":root,"rootBuild":build.number,**mode_result(raw,mode,record["grewFrom"],chat)}
                database.drop(target)
                database.create(target)
```

Proposed behavior: keep one ordered migration sequence and a record of applied migrations in the database. Stage compatible Builds and verify the snapshot can be restored with the recorded source revisions and Build inputs. Apply breaking upgrades with writers quiesced. Before normal writes resume, a failed upgrade can recover from the snapshot and matching code. After normal writes resume, preserve new records before any restore, or repair the installed schema forward. At the one-time reset, take and verify backups of both existing databases and initialize an empty baseline in the database selected to remain live.

<!-- sources:
arbol:@code/src/arbol_roots/sql.py#migrate
arbol-root:@code/roots/jensen/migrate.sql
arbol-root:@code/roots/jensen/layout.sql
arbol:architecture/01-roots.md#Moving chats between Roots
-->

## Trunk Builds and detached Exchanges

The Trunk launcher uses the Root Contract version from a catalogue record to choose a compatible Build. A Trunk whose last write fails leaves its Exchange folder for settlement. These are separate responsibilities. The first can use installed schema compatibility, and the second still needs a stable Exchange identifier and the accepted Trunk Build. Closing the App cannot establish that all writers have stopped.

`arbol:src/arbol_builds/trunk_launcher.py`, lines 114–122 (`d05503c` baseline):

```python
def fits(record: Record, root: Record) -> bool:
    """A Trunk Build fits a Root when its rootContracts hold the Root's version (RCT-0)."""
    return int(root["rootContract"]) in {int(number) for number in record["rootContracts"]}


def chosen(registry: str, records: list[Record], root: Record) -> Record | None:
    """The newest working Build that fits the Root and has its program: the Build run starts (RCT-0.7)."""
    return next((record for record in records
                 if record["status"] == "working" and runnable(registry, record) and fits(record, root)), None)
```

`arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/end.py`, lines 98–104 (`142e4fc` baseline):

```python
async def finish(saver: Saver, folder: ExchangeFolder, rows_at_end: Sequence[Row], end: End) -> bool:
    """Saves the end and then removes the folder; when the database does not take it within its tries, the folder
    stays, with `end` in its record, for settling (RCT-2)."""
    if not await save_end(saver, folder.exchange, rows_at_end, end):
        return False
    folder.remove()
    return True
```

Proposed behavior: block new work across all entry points, drain active Exchanges and settle pending results before changing an incompatible schema. Guard startup and explicit Build selection against the installed schema. Keep Trunk identity and release numbering independent of schema revision. Use the same Exchange start, list, stop and settle guarantees after moving their implementation out of the Root manager.

<!-- sources:
arbol:@code/src/arbol_builds/trunk_launcher.py#fits
arbol-root:@code/src/arbol_root/start.py#start
arbol-root:@code/src/arbol_root/settle.py#settle
arbol-trunk:@code/trunks/trivial/src/arbol_trunk_trivial/end.py#finish
arbol:architecture/02-chat-exchange-across-components.md#When the database cannot be reached
-->

## Backend, App and administration

The App currently supervises a backend for the current Root and for every Root with an open window. The renderer comes from the App Build. The account list is read through the backend from shared Drivers, while the Vigor CLI opens the selected database. Removing Root names from window titles would leave the backend, state and data selection in place.

`arbol-app:Sources/ArbolApp.swift`, lines 519–524 (`7cf8387` baseline):

```swift
    private func reconcileBackends() {
        guard !departureInProgress else { return }
        let openRoots = Set(allWindows.map(\.rootID))
        let needed = lastRoots.filter { $0.appProblem == nil && ($0.current || openRoots.contains($0.id)) }
        backends.reconcile(Set(needed.map(\.id)))
    }
```

Proposed behavior: use one backend, one settings scope and one administration data source. Keep the shared renderer and Bridge compatibility boundary. Seqoya Lab has one window and begins a new Vigor history after the reset. Elma still picks a Trunk for a new Exchange, and accepted work retains its own Build. Preserve the configuration needed to operate and recover the installation.

<!-- sources:
arbol-app:@code/Sources/ArbolApp.swift
arbol-app:@code/Sources/ElmaWindow.swift
arbol:@code/src/arbol_backend/accounts.py#Accounts.raw_outcome
arbol:@code/src/arbol_radar/cli.py
arbol:backend/03-the-arbol-swift-app.md#Windows and renderer Builds
arbol:sagas/01-subscriptions-vigor.md#The calculation record
-->

## Chat identity and integration records

Trivial Trunk sends both a Root ID and a chat session ID to the Driver. The Claude and Codex paths expose the values in the child environment. Forester's Arbol fallback then uses them to identify a booking owner. A change to window or database scope alone cannot remove the dependency. During the transition, changing the lookup key can strand a live booking or make two copied histories appear to have the same identity.

`forester:src/forester/booking.py`, lines 80–89 (`da5ab40` baseline):

```python
        if not session and os.environ.get(variable):
            tool, session = tool or candidate, os.environ[variable]
    if not session and os.environ.get("ARBOL_CHAT"):
        tool = tool or "arbol"
        session = f"{os.environ.get('ARBOL_ROOT', '')}/{os.environ['ARBOL_CHAT']}"
    if not tool or not session:
        raise ValueError(
            "Supply --tool and --session, or the harness session environment."
        )
    return tool, session
```

Proposed behavior: define one chat identity for new records. Keep old identity values in historical records. Resolve any bookings still open at cutover before retiring their runtime. A clean database needs no mapping from older chats into new chats.

<!-- sources:
arbol-trunk:@code/trunks/trivial/src/arbol_trunk_trivial/request.py
arbol-claude-driver:@code/src/arbol_claude_driver/runtime.py
arbol-codex-driver:@code/src/arbol_codex_driver/app_server.py
forester:@code/src/forester/booking.py#identity
forester:@code/src/forester/hook.py
-->

## Qualification and prior work

The installed migration drill established that both historical Roots could coexist and that an accepted Exchange could finish in the source while the destination held a snapshot. That evidence belongs to the previous design. The new test boundary needs a migration that refuses or waits while a writer can still persist data, recovery on a restored copy and a full launch against the migrated schema. Also qualify chat continuity, stale Build refusal, App and Bridge behavior, and Forester identity through the installed path. The existing runtime can retain unwritten results even after the process has ended, so include pending folders in the drain case.

<!-- sources:
arbol-root:@code/roots/sapling/drills/migration_drills.py
arbol-trunk:@code/trunks/trivial/src/arbol_trunk_trivial/end.py#finish
arbol:architecture/01-roots.md#Moving chats between Roots
-->

## Open questions

- Which configuration and pending files are needed to recover the pre-transition installation? Inventory them during rehearsal and back them up with the databases as appropriate.
- Which commands admit a writer and which storage location coordinates migration with admission, drainage and settlement? Specify one boundary before splitting implementation among repositories.
- Are any Forester bookings still owned by a legacy Arbol chat at cutover? Recheck the live Ledger before retiring its runtime.
- Which compatibility metadata and commands belong in the public Trunk interface? Prefer the smallest shape that lets an explicit or default Build fail clearly on an incompatible installed schema.
