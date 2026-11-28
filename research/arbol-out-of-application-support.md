---
role: authored
---
# Arbol out of Application Support

Research of 17 November 2026 for moving all of Arbol's files out of `~/Library/Application Support/Arbol/`. Working state goes to `~/.arbol/`, beside Arbol's settings, with the database in `~/.arbol/postgres/`. The research first planned a new `~/Arbol/` folder; later on 17 November the owner chose `~/.arbol/` instead, so no `~/Arbol/` folder is used ([ARC-D83](../architecture/05-where-arbol-keeps-its-files.md#decisions)). Archival material goes to the external drive Mercury, at `/Volumes/Mercury/Arbol/`. Depth: standard. The specification it prepares is [ARC-5](../architecture/05-where-arbol-keeps-its-files.md).

**Why.** On 17 November 2026, while specifying the session import, the owner decided that nothing of the import goes under Application Support ([IMP-D9](../session-import/00-the-import.md#decisions)), because files there are hard to find and check. The owner then asked to plan the same move for the whole of Arbol.

**Method.** Every folder and file under `~/Library/Application Support/Arbol/` was listed and measured with `du`. The newest modification date of each was read. The repositories in `~/repos/sylvan-stack/` were searched for every spelling of the path, and each match was read. Launch agents, `~/.arbol/`, `~/.local/bin/`, the Keychain service names (names only, no secrets), the running processes and Mercury's volume properties were read. Nothing was moved, written or started.

**Revisions read.** `arbol` 9496503bca24, `arbol-app` 6367473e1927, `arbol-trunk` 4625dd3b3955, `arbol-claude-driver` f207d4c38b72, `arbol-codex-driver` 94ab305e7b15, `arbol-pi-driver` 937cd5d0a530, `arbol-mimo-driver` 4eb2c0bb0552, `arbol-browser` f36bbe0e2bce, `arbol-root` 7271a4eb0831. A locator `repo:path:line` below is at that revision.

## Summary

- The folder holds **43 GB**. Only **about 3 GB** of it belongs to the installed single-database release: the database, the runtime, the App's locks, the Build registry, Driver state and one Mimo resource. Everything else, **about 41 GB**, is left over from Arbol 1. No file of it was written after 7 October 2026, and no current code names it. A 38 GB cache is most of it.
- The path is spelled out in **at least 40 places in current code**, across 9 repositories, and in about 20 specifications. No component reads it from one shared setting. Each one builds it from the home folder.
- Several of those places are **guards**: they refuse to let a test or a candidate Build use the installed folder. If the folder moves and a guard keeps the old path, the guard protects nothing and says nothing.
- Builds carry the path **in their packaged code**. A Build made before the move keeps looking in the old place. The schema compatibility of ARC-4 does not catch this, because the move is not a schema change.
- Three things are tied to the path itself, not only to its contents: the **Claude Driver's Keychain service name**, **Claude Code's own Keychain item** for each test home, and **Codex's saved conversation paths** in its database.
- `~/.arbol/` is on the same internal volume as `~/Library/`. Moving there is a rename: instant, with no copy. Moving to Mercury is a copy.
- PostgreSQL must stay on the internal disk. The installed probe refuses any other disk, and the database is working state, not archive.
- **`~/Builds` holds only current Builds.** On 17 November 2026 the owner removed older files from `~/Builds`, which had grown to 150 GB, among them the ASD-15 and ASD-16 evidence and both legacy database backups. Any component can be rebuilt from its source revision; backups and older recovery material belong on Mercury. See [Older Builds and backups](#older-builds-and-backups).

## Inventory

Sizes are from `du -sh` on 17 November 2026. "Newest" is the newest file's modification date. Paths are relative to `~/Library/Application Support/Arbol/` unless they start with `~` or `/`.

### State of the installed release

| Item | Size | Newest | Owner | What names the path |
|---|---|---|---|---|
| `database/data/` PostgreSQL data folder, with the server's `log/` (1.1 MB) | 75 MB | today | Database server (ARC-0, ARC-D64) | `arbol:database/database_server.py:39` (`Places.folder`), `:43` `data`; `arbol:src/arbol_backend/measurements.py:82` (disk measurement); the launch agent's `-D` argument; `arbol:database/README.md:23` |
| `database/socket/` with `.s.PGSQL.5433` and its lock | 4 KB | today | Database server | `arbol:database/database_server.py:47`; `postgresql.conf` line 853 `unix_socket_directories`; guards in `arbol:src/arbol_backend/database.py:170` and `arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/root.py:55` |
| `database/launchd.log` | 8 KB | 11 Nov | launchd for the database | `arbol:database/database_server.py:51`; the plist's `StandardOutPath`, `StandardErrorPath` and `WorkingDirectory` |
| `database/backups/` copies of replaced `pg_hba.conf` and `postgresql.conf` | 40 KB | 16 Oct | Database installation | `arbol:database/database_server.py:55`; `arbol:database/README.md:25` |
| `runtime/backend.sock`, `backend.lock` | 0 | 13 Nov | Backend | `arbol:src/arbol_backend/model.py:151`; `arbol-app:Sources/RootSocket.swift:6-8` |
| `runtime/exchanges/` private Exchange folders (empty now) | 0 | 13 Nov | Installation runtime, detached Trunks | `arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/root.py:84` and `:79` (`exchanges`) |
| `runtime/writer-admission/` `state.json` and three locks | 4 KB | 13 Nov | Installation runtime (ARC-4 admission) | `arbol:src/arbol_installation/admission.py:44`; `arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/admission.py:39` |
| `app/resident.lock`, `handoff.lock` | 0 | 13 Nov | App | `arbol-app:Sources/ResidentApp.swift:27` |
| `builds/` the Build registry: `arbol` 182 MB, `arbol-app` 12 MB, `arbol-classifier` 541 MB, `arbol-claude-driver` 75 MB, `arbol-codex-driver` 76 MB, `arbol-mimo-driver` 296 MB, `arbol-pi-driver` 938 MB, `arbol-root` 480 KB, `arbol-trunk` 111 MB | 2.2 GB | today | Builds (BLD-0, BLD-D5) | `arbol:src/arbol_builds/config.py:36`; the generated launchers in `~/.local/bin/` (for example `arbol` line 522, `arbol-trunk` line 702, each Driver's line 452); guards in `arbol:src/arbol_builds/driver_payload.py:468,603`, `arbol-claude-driver:src/arbol_claude_driver/admission.py:139`, `arbol-codex-driver:src/arbol_codex_driver/payload.py:501`, `arbol-pi-driver:src/arbol_pi_driver/identity_protocol.py:700`, `arbol-mimo-driver:src/arbol_mimo_driver/identity_protocol.py:700`, `arbol-browser:src/runtime/authorities.ts:120`, `arbol-browser:src/runtime/host-bootstrap.mm:54` |
| `drivers/claude/` normal Claude Driver state (Subscriptions `anthropic`, `zai`; runs, research) | 5.7 MB | 15 Nov | Claude Driver (DRV-D3) | `arbol-claude-driver:src/arbol_claude_driver/cli.py:80,89`; Keychain naming at `subscriptions.py:261-265` |
| `drivers/codex/` normal Codex Driver state, with the native home of `chatgpt` (`CODEX_HOME`, its `auth.json`, SQLite databases and sessions) | 132 MB | 13 Nov | Codex Driver; the home is Codex's own | `arbol-codex-driver:src/arbol_codex_driver/state.py:26`; home check at `app_server.py:281-286` |
| `drivers/pi/` normal Pi Driver state (`chatgpt`, `deepseek`, `kimi-coding`, `zai`) | 24 KB | today | Pi Driver | `arbol-pi-driver:src/arbol_pi_driver/cli.py:134` |
| `drivers/mimo/` normal Mimo Driver state (`xiaomi`) | 12 KB | 12 Nov | Mimo Driver | `arbol-mimo-driver:src/arbol_mimo_driver/cli.py:125`; guard at `accounts.py:42` |
| `drivers/arbol-claude-driver/`, `arbol-codex-driver/`, `arbol-pi-driver/`, `arbol-mimo-driver/` test state of each Driver's Build checks (`test-*` Subscriptions with their own native homes) | 23 MB, 194 MB, 148 KB, 11 MB | 11–12 Nov | Each Driver's Build check | `arbol-codex-driver:README.md:150`; the Build check scripts packaged in each Build |
| `native-resources/mimo/aws-proxy-1.7.0` | 203 MB | 28 Oct | Mimo Driver | `arbol-mimo-driver:src/arbol_mimo_driver/owner_resources.py:85` |
| `backups/SYL-314-2026-10-29/` a Mimo home and an auth file saved before the owner's sign-in | 96 MB | 27 Oct | Mimo Driver qualification (SYL-314) | named only in `~/Artifacts/arbol-mimo-driver/specs/SYL-314-unpaid-qualification.md` |

Not yet created, but named by current code or specifications:

| Item | Owner | What names it |
|---|---|---|
| `browser/` Browser profiles | Arbol Browser (BRW-0, BRW-1) | `arbol-browser:src/profiles/paths.ts:85`; `arbol-browser:src/cli/main.ts:29`; guard in `authorities.ts:121` and `host-bootstrap.mm:54`; `~/Artifacts/arbol-browser/specs/01-profiles-and-browser-data.md:41` |
| `agents/` agent records | `arbol-agents` (AGR-0) | `arbol:src/arbol_agents/records.py:24`; AGR-0.1 |
| `roots/` Root folders | Arbol 2 before ARC-4; now historical | `arbol:src/arbol_builds/roots.py:21`, `arbol:src/arbol_roots/model.py:37`, `arbol-root:src/arbol_root/model.py:75`, `arbol-root:scripts/build.py:22`, drills and conformance under `arbol-root:roots/sapling/drills/` and `arbol-root:contract/conformance/` |

### Left over from Arbol 1

No file in these was written after 7 October 2026. None of their names appears in current code. Arbol 1's `com.arbol.*` services are not loaded.

| Item | Size | Newest | What it is |
|---|---|---|---|
| `cache/native-workers/` 343 folders of about 161 MB | 38 GB | 27 Sep | Arbol 1 native worker cache |
| `trunks/` (`first-adoption`, `registry`, `admission-target.json`) | 1.0 GB | 4 Oct | Arbol 1 Trunk adoption |
| `deployments/` 113 folders | 514 MB | 5 Oct | Arbol 1 deployments |
| `logs/` 266 files | 339 MB | 7 Oct | Arbol 1 service logs |
| `recovery/` with its README of 24 September 2026 | 180 MB | 28 Sep | Arbol 1 recovery stack and scripts |
| `development/arbol-codex-driver` | 152 MB | 7 Oct | Arbol 1 Driver development state |
| `run/` including `dispatcher-credentials/` with 18,724 files | 100 MB | 5 Oct | Arbol 1 dispatcher runtime |
| `provider-retirement/`, `rebuilds/`, `selective-build/`, `ip/`, `db/`, `config/` (holds `event-log-service.token`) | under 1 MB each | Sep–Oct | Arbol 1 records |
| Loose files: `organizations.json`, `detached-views.json`, `entity-search-cache.json`, `knowledge-synchronization.json`, `last-active-ui`, `rebuild-and-restart.zsh`, nine `*.lock` files, `rebuild-complete-notification.pending` | 100 KB | Sep–Oct | Arbol 1 UI state and locks |
| `~/Library/Application Support/Arbol-retired-migration-20260923T110411/` | 200 KB | 23 Sep | A sibling folder: an Arbol 1 migration record |

Some of these hold Arbol 1 secrets, such as `config/event-log-service.token` and `run/dispatcher-credentials/`. Arbol 1 is retired, but the files are still secrets until shown otherwise.

### Outside the folder

| Item | Owner | Path it names |
|---|---|---|
| `~/Library/LaunchAgents/com.sylvan-stack.arbol.database.plist` | Database installation | `-D …/database/data`, the log and the working folder |
| `~/Library/LaunchAgents/com.sylvan-stack.arbol.app.plist` | App | `~/.local/bin/arbol-app --background`; no Application Support path |
| `~/.local/bin/arbol`, `arbol-app`, `arbol-trunk`, the Driver launchers | Builds | each embeds `…/Arbol/builds` (generated from `arbol:src/arbol_builds/config.py:36`) |
| `~/.arbol/database.json`, `arbol-pi-driver.json`, `seqoya-usage-evidence.json`, `backups/`, `pi-cutovers/` | Settings | none; address and settings only |
| Keychain `com.sylvan-stack.arbol.database`, `com.sylvan-stack.arbol.classifier` | Database, classifier | none |
| Keychain `Claude Code-credentials-<8 hex>`, 11 items | Claude Code, one per `CLAUDE_CONFIG_DIR` it was started with | the hash of each home's path |
| Keychain `com.arbol.secrets`, `com.arbol.subscription-credentials`, `com.arbol.embedder` | Arbol 1 | none |
| `~/Library/Preferences/com.sylvan-stack.arbol*.plist`, `~/Library/WebKit/`, `~/Library/Caches/` entries | macOS for the App and probes | none |
| `~/Library/Application Support/Forester/` | Forester, not Arbol | out of scope |
| Running now: `postgres` from the data folder (since 11 Nov), App Build 27 and backend Build `c` from the registry (since 13 Nov) | | their executables live in the folder |

Forester's hooks take the chat from `ARBOL_CHAT` (`forester:src/forester/booking.py:86`) and read no Arbol path. Mycel and the Workspace Ledger name none either.

<!-- sources:
arbol:@code/database/database_server.py#Places
arbol:@code/src/arbol_builds/config.py#locations
arbol:@code/src/arbol_installation/admission.py#runtime_folder
arbol:@code/src/arbol_backend/model.py
arbol:database/README.md
-->

## What each item becomes

| Item | Proposed place | Kind | Reason |
|---|---|---|---|
| Database data folder, socket, launchd log, config copies | `~/.arbol/postgres/` | Working | Live data. Must be on the internal disk (see below) |
| Runtime: backend socket and lock, Exchange folders, writer admission | `~/.arbol/runtime/` | Working | Live; the owner may want to look at a pending Exchange folder |
| App locks | `~/.arbol/app/` | Working | Live |
| Build registry | `~/.arbol/builds/` | Working | Selected Builds, and those BLD-0 protects, such as one needed to settle an Exchange, must stay reachable without Mercury. Older Builds are rebuilt from source when needed (ARC-D95) |
| Normal Driver state with native homes | `~/.arbol/drivers/<driver>/` | Working | Live sign-ins, continuity and runs |
| Driver test state | `~/.arbol/drivers/arbol-<x>-driver/` | Working | Used by Build checks; keeps their current names |
| Mimo native resource | `~/.arbol/native-resources/mimo/` | Working | Read by the Mimo Driver |
| Browser profiles, agent records (new) | `~/.arbol/browser/`, `~/.arbol/agents/` | Working | Live once built |
| Session import working files | `~/.arbol/imports/` | Working | IMP-D9 |
| Session import archive | `/Volumes/Mercury/Arbol/imports/` | Archive | IMP-D9 |
| Arbol 1 leftovers, 41 GB | `/Volumes/Mercury/Arbol/legacy/arbol-1/` | Archive | Not read by anything; kept for history |
| SYL-314 Mimo backup | `/Volumes/Mercury/Arbol/backups/` | Archive | Holds a credential; the owner accepted secrets on Mercury (ARC-D86) |
| Future ARC-4 snapshots and release records | `/Volumes/Mercury/Arbol/backups/` only (ARC-D89) | Archive | There is no other backup on this Mac |
| Launch agents, Keychain items, Preferences, WebKit data, `~/.local/bin` launchers | Stay | Stay | macOS and the shell require these places. The plist and the launchers are rewritten to the new paths |
| `~/.arbol/` settings | Stay, unless the owner chooses otherwise | Stay | Not under Application Support; about 30 places name it |
| `/Library/Application Support/opencode` (system folder read by `arbol-mimo-driver:src/arbol_mimo_driver/native_profile.py:158`) | Stay | Stay | The vendor tool's managed configuration, not Arbol's |

## Constraints

### PostgreSQL stays on the internal disk

The probe's `data-folder` check refuses a data folder that is not on an internal, non-removable disk (`arbol:database/probe_database_server.py:340-348`). Mercury reports `Device Location: External` and `Protocol: USB`, so the probe would fail there. The database is also live working state: unplugging the drive would stop every chat write, and USB bridges do not always honour the cache flushes PostgreSQL relies on. `~/.arbol/postgres/` is on the internal volume and passes the check as it is.

### A move inside the internal disk is a rename

`~/.arbol/` and `~/Library/` are on the same APFS volume (`/dev/disk3s1s1`). `~/.arbol/` already exists with mode 0700 and holds settings files (`database.json`, `arbol-pi-driver.json`, `seqoya-usage-evidence.json`, `pi-cutover.json`) and the folders `backups/` and `pi-cutovers/`; none of the new sub-folder names is taken. Renaming keeps every file, its inode, its mode and its extended attributes. It takes no time and no extra space. The internal disk has 144 GiB free; Mercury has 1.4 TB free.

### Everything must be stopped first

The App (Build 27) and the backend (Build `c`) run from files in `builds/`, and `postgres` runs on `database/data`. A program keeps open files across a rename, but it opens new ones by path. Python imports modules lazily, and the App loads its renderer resources from its bundle. So the App, the backend and the database server must be stopped, and no Trunk or Driver run may be active, for the whole move.

ARC-4 already has this state: exclusive maintenance. It confirms there are no in-flight write permits, unresolved starts, active Exchanges, open Exchange rows or pending results ([ARC-4](../architecture/04-single-database.md#maintenance-and-writer-admission)). A stopped but unsettled Exchange blocks it. The move is not a schema change, but it needs the same fence.

### The fence lives in the folder that moves

The writer admission state is `runtime/writer-admission/state.json`. Renaming the whole `runtime/` folder carries the exclusive state with it, so the fence is still held at the new place. A Build that still looks in the old place finds no state. That is a refusal: `arbol:src/arbol_installation/admission.py:239` says "A missing state never grants admission", and `prepare_directory` is the explicit operator setup only. An old Build therefore fails closed after the move, as ARC-4 requires of an unknown state.

### Old Builds keep the old path

Every Build packages its code, and the code spells out the path (for example 230 files in `builds/` contain it; in `builds/arbol/c` they include `admission.py`, `model.py`, `database.py` and `measurements.py`). ARC-4 selects Builds by `schemaCompatibility`. A move that changes no schema leaves old Builds "compatible" by that rule. Without a further marker, the launcher could still pick a pre-move Trunk Build, which would then refuse for want of admission state, or a pre-move Driver Build, which would create a fresh, empty state folder at the old path and look signed out.

So every Build made before the move must be refused on the moved installation, by a marker that the launcher checks as it checks schema compatibility. ARC-4 already allows this: "Incompatible older payloads may remain archived and must be refused on the live installation." A pending Exchange must not exist at the move, because ARC-D80 settles one with its recorded Build, and that Build would look in the old place.

### The guards must move with the path

These checks compare a path with the installed one and refuse when they match, so that a test or candidate never touches the live installation:

- `arbol:src/arbol_backend/model.py:151-155`: an isolated backend cannot use the installed runtime;
- `arbol:src/arbol_backend/database.py:170` and `arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/root.py:55`: an isolated connection cannot use the installed socket;
- `arbol:src/arbol_builds/driver_payload.py:468,603`, `arbol-claude-driver:src/arbol_claude_driver/admission.py:139`, `arbol-codex-driver:src/arbol_codex_driver/payload.py:501`, `arbol-pi-driver` and `arbol-mimo-driver` `identity_protocol.py:700`: a candidate Build cannot be accepted in the installed registry;
- `arbol-mimo-driver:src/arbol_mimo_driver/accounts.py:42`: test Subscriptions only outside the normal state;
- `arbol-browser:src/runtime/authorities.ts:120-121` and `host-bootstrap.mm:54`: the browser may not overlap the registry or its own state.

If the folder moves and a guard keeps the old path, the guard silently stops protecting the new one. All of them must change in the same release, and the simplest way is for every component to take the path from one definition.

### The Claude Driver names its Keychain item after its folder

`arbol-claude-driver:src/arbol_claude_driver/subscriptions.py:261-265`:

```python
def keychain_service(directory: Path, home: str = ACTUAL_HOME) -> str:
    path = str(directory.resolve())
    normal = str((Path(home) / 'Library/Application Support/Arbol/drivers/claude').resolve())
    service = 'com.sylvan-stack.arbol.claude-driver'
    return service if path == normal else service + '.' + hashlib.sha256(path.encode()).hexdigest()[:12]
```

The normal state gets the plain service name; any other folder gets a name with a hash of its path. If the normal folder moves without this line changing, the Driver looks for a different Keychain item. No item with the plain name exists today (the normal `anthropic` Subscription uses the owner's own `~/.claude`), so nothing is lost now. The rule must still follow the move.

### Claude Code names its Keychain item after its home

Claude Code keeps the sign-in of a home started with `CLAUDE_CONFIG_DIR` in a Keychain item `Claude Code-credentials-<8 hex>`, derived from that path. Eleven such items exist. The Driver gives a home of its own only to test Subscriptions (`subscriptions.py:215-219`, CLD-D20). Moving those homes, such as `drivers/arbol-claude-driver/subscriptions/test-anthropic/home`, makes Claude Code look for a new item: each test Subscription must sign in again. The owner's normal `anthropic` sign-in in `~/.claude` is not affected. This needs a probe that sends no prompt, recorded with the Claude Code version.

### Codex saves conversation paths in its own database

The `chatgpt` home keeps its sign-in in `auth.json` (`cli_auth_credentials_store = "file"`), which moves with the folder. But Codex's `state_5.sqlite` table `threads` has a `rollout_path` column with absolute paths; its one thread points under Application Support. After the move, Codex may not find that conversation's file when Arbol continues the chat. Arbol never writes into a vendor tool's database. A probe on a copy of the home, sending no prompt, shows whether Codex finds the file by its id. Only one Codex conversation exists, so the effect is small either way.

The Driver itself checks that the home Codex reports equals the home it started (`arbol-codex-driver:src/arbol_codex_driver/app_server.py:281-286`), which holds after a rename if both sides use the new path.

### Unix socket length

macOS allows 103 bytes for a socket path; the backend refuses a longer one (`arbol:src/arbol_backend/model.py:156`, `arbol:database/database_server.py:28`). The paths get shorter: the database socket from 75 to 48 bytes (`~/.arbol/postgres/socket/.s.PGSQL.5433`), the backend socket from 66 to 39. The space in "Application Support" also goes, which TRV-D23 had to work around.

### Mercury

`diskutil info /Volumes/Mercury` reports case-sensitive APFS, `Owners: Disabled`, `Protocol: USB`, `Device Location: External`, `FileVault: Yes`, 1.4 TB free in a 1.7 TB container. Consequences:

- **Removable.** Nothing Arbol needs to run may live there. Only writing to the archive needs it, and such an operation refuses when the drive is absent, as IMP-0 does with `archive_unavailable`.
- **Ownership disabled.** Modes are stored but not enforced. Anyone using this Mac account, or another Mac the drive is plugged into after unlocking, can read it. FileVault protects it only while locked. Secrets therefore need a decision before they go there: the Arbol 1 tokens and dispatcher credentials, and the SYL-314 auth file.
- **Case-sensitive.** The internal volume is case-insensitive. A copy from the internal disk cannot collide, because one folder there cannot hold two names differing only in case. A later copy back from Mercury could. The Arbol 1 file names checked are lowercase hex or fixed names.
- **macOS Spotlight** indexes Mercury; **Time Machine** excludes it.

### macOS Spotlight and Time Machine

macOS Spotlight already indexes the current folder: `mdfind` finds 144 `build.json` files under `builds/`. `~/.arbol/` is a hidden folder, and macOS Spotlight does not index it: on 17 November 2026 `mdfind -onlyin ~/.arbol` found none of the settings files there. After the move Arbol's files leave Spotlight searches. macOS Spotlight skips a folder the owner lists under Spotlight Privacy, or a folder whose name ends in `.noindex`. Arbol cannot change macOS Spotlight settings itself.

Time Machine has no destination on this Mac (`tmutil destinationinfo`: none configured) and there are no local snapshots. So nothing of Arbol is backed up today, except what ARC-4 snapshots record. If Time Machine is set up later, it should skip the live data folder, because a file copy of a running PostgreSQL server is not a consistent backup. `tmutil addexclusion` marks a folder with an attribute that a rename keeps.

### ARC-4 rules for the move

- Enter draining, then exclusive maintenance, before stopping anything ([ARC-4](../architecture/04-single-database.md#maintenance-and-writer-admission)).
- A long healthy Exchange is waited for, not forced. An unsettled one blocks the move.
- No schema changes. ARC-D79's snapshot rule applies to schema changes, but the move touches every file of the database, so a verified snapshot before it is the safe default.
- Record the prior and new release: the Builds made for the new layout are a new release, and the reopening is the recorded change of admission ARC-4 describes.
- Prefer repair forward after reopening. Before reopening, recovery is to rename the folders back and restore the plist and launchers, while the fence is held.

### Detached Trunks and Exchange folders

ARC-4 lets an accepted Exchange keep running in a detached Trunk while Arbol quits. Such a Trunk holds its Exchange folder by path under `runtime/exchanges/` (`root.py:79`). A rename under it would make its later writes fail. Exclusive maintenance already rules this out: no active Exchange, no pending folder. The folder is empty today.

### Driver homes and native tool homes

- Normal Driver state moves whole; each Driver's default (`--state-dir` absent) must name the new place.
- Native homes inside Driver state move with it: Codex `chatgpt`, the test homes.
- Native homes outside Arbol stay: `~/.claude`, and any tool home in the owner's folder. Arbol never moves a vendor tool's own home.
- The settings files stay in `~/.arbol/`.

<!-- sources:
arbol:@code/database/probe_database_server.py#check_data_folder
arbol:@code/src/arbol_installation/admission.py#prepare_directory
arbol-claude-driver:@code/src/arbol_claude_driver/subscriptions.py#keychain_service
arbol-codex-driver:@code/src/arbol_codex_driver/app_server.py
arbol:architecture/04-single-database.md#Maintenance and writer admission
arbol:session-import/00-the-import.md#The raw archive
-->

## Older Builds and backups

ARC-4 step 3 calls both final backups of the legacy databases the archive. ASD-16 recorded them, with the cutover evidence, under `~/Builds/sylvan-stack/arbol/asd-16-2026-11-13/` (`~/Artifacts/forester/sagas/sylvan-stack/arbol-single-database/installed-transition/ASD-16.md`, line 138), and the cutover runbook put its whole execution directory, snapshots and restores included, under `~/Builds/sylvan-stack/arbol/` (runbook, line 25). Earlier Beats of the Saga (ASD-4, ASD-8, ASD-11, ASD-14, ASD-19) did the same with their private evidence.

On 17 November 2026 the owner said they had removed those files on purpose: `~/Builds` had grown to 150 GB and there is no clean-up feature yet. Their rule, recorded as [ARC-D95](../architecture/05-where-arbol-keeps-its-files.md#decisions):

- `~/Builds` holds only current Builds;
- nothing may rely on an older Build being there, because any component can be rebuilt from its source revision;
- backups and older recovery material go on Mercury, never in `~/Builds`.

The records that name the removed folders stay as history. The rule touches three assumptions elsewhere:

- **Snapshots and restore receipts.** The cutover runbook and ARC-4's recovery steps keep them in a private folder; from now on that is `/Volumes/Mercury/Arbol/backups/` (ARC-D89).
- **Old Builds as recovery inputs.** ARC-4 retains "the payloads or reproducible inputs" of the prior release, and BLD-0 protects the newest Builds and those in use. Rebuilding from the recorded source revisions is the reproducible-inputs path ARC-D77 already names. BLD-0's protection of Builds in use, or needed to settle an Exchange, still applies.
- **The signed App.** The runbook (line 44) and `arbol:database/README.md` line 104 keep the exact signed App, because a rebuild does not reproduce the same signed binary. That conflicts with "rebuild from source" and is an open decision ([ARC-D96](../architecture/05-where-arbol-keeps-its-files.md#decisions)).

## Questions for Spec Writing

On 17 November 2026 the owner answered questions 1 to 4 ([ARC-D85, ARC-D86, ARC-D87 and ARC-D89](../architecture/05-where-arbol-keeps-its-files.md#decisions)): archive all of Arbol 1 on Mercury; secrets may go there; nothing stays at the old path; snapshots only on Mercury. The same day the owner accepted the proposed defaults of the rest (ARC-D84, ARC-D88, ARC-D90 to ARC-D94 and ARC-D96): settings stay in `~/.arbol/`, and Arbol leaves macOS Spotlight as it is.

1. Should the Arbol 1 leftovers (41 GB) be archived on Mercury whole, archived without the 38 GB cache, or deleted?
2. May secrets go to Mercury, where file modes are not enforced?
3. Should a link remain at the old path for a while, so that old Builds can still be used for recovery?
4. Where do ARC-4 snapshots and release records go from now on?
5. Should `~/.arbol/` settings move into `~/Arbol/` too? (Settled by the owner's choice of `~/.arbol/` for everything.)
6. Should macOS Spotlight skip `~/Arbol/`, or parts of it? (Moot: `~/.arbol/` is hidden and not indexed.)
7. ~~Where are the ASD-15 and ASD-16 evidence folders?~~ Removed by the owner on purpose, 17 November 2026 (ARC-D95).
