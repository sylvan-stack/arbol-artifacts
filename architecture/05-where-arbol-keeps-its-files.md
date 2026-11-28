---
role: authored
spec: ARC-5
status: accepted
---
# Architecture · 05 Where Arbol keeps its files

## Purpose

Arbol keeps all its files in `~/Library/Application Support/Arbol/`. The owner finds files there hard to find and check. On 17 November 2026 the owner decided that the session import keeps nothing there ([IMP-D9](../session-import/00-the-import.md#decisions)) and asked for the same for the whole of Arbol: working state in `~/.arbol/`, the folder in the owner's home that already holds Arbol's settings, with the database in `~/.arbol/postgres/`, and archival material on the external drive Mercury. No `~/Arbol/` folder is used. This specification gives the new layout and the one-time move of the installed release. The evidence is in [Arbol out of Application Support](../research/arbol-out-of-application-support.md). The owner accepted this specification on 17 November 2026.

## Scope

Covered:
- where each kind of Arbol file lives after the move;
- how components find those places;
- what stays where macOS or a vendor tool requires it;
- what Arbol does when Mercury is not mounted;
- the one-time move of the live installation, its checks and its recovery;
- the files left over from Arbol 1.

Not covered: `~/Library/Application Support/Forester/`, which belongs to Forester; `~/Builds/`, except for the rule that it holds only current Builds ([ARC-D95](#decisions)); the vendor tools' own homes outside Arbol, such as `~/.claude`.

This specification amends [ARC-4](04-single-database.md). ARC-4's rules for maintenance, writer admission, release records and recovery apply to the move unchanged.

## Behaviour

### The layout

Arbol's working state is in one folder, `~/.arbol/`, on the Mac's internal disk, beside the settings already there. Its sub-folders keep today's names, so that what the owner already knows still applies, except that the database folder is called `postgres/` ([ARC-D83](#decisions)):

```text
~/.arbol/                         the installation and its settings, mode 0700
  database.json, arbol-*.json    the settings, unchanged (ARC-D90)
  postgres/                      the PostgreSQL server, today's database/
    data/                        its data folder, with the server's log/
    socket/                      .s.PGSQL.5433, mode 0700
    launchd.log                  the launch agent's output
  runtime/                       backend.sock, backend.lock, exchanges/, writer-admission/
  app/                           the App's resident and handoff locks
  builds/                        the Build registry (BLD-0)
  drivers/<driver>/              each Driver's state, with the native homes it owns
  native-resources/              resources a Driver packages for its tool, such as Mimo's
  browser/                       Arbol Browser profiles (BRW-1), when built
  agents/                        agent records (AGR-0), when built
  imports/                       the session importer's working files (IMP-0)
```

Archival material is on Mercury, in `/Volumes/Mercury/Arbol/`:

```text
/Volumes/Mercury/Arbol/
  imports/                       the session import's raw archive (IMP-0)
  backups/                       ARC-4 snapshots and release records (ARC-D89), and earlier backups such as SYL-314's
  legacy/arbol-1/                the files left over from Arbol 1, as they were, secrets included
```

Archival means kept for history or recovery and not read by Arbol while it runs. Nothing Arbol needs to run or to settle an Exchange is on Mercury. Database snapshots are only on Mercury, so a schema change and a restore from a snapshot need it ([ARC-D89](#decisions)).

Modes stay as today: folders 0700 and files 0600 where the component asks for them. The App, the runtime and the Trunks keep checking that their folders are the owner's and private. `~/.arbol/` is hidden in Finder because its name starts with a dot; the owner opens it with Go to Folder (Shift-Command-G) or shows hidden files with Shift-Command-period.

For example, a pending Exchange folder is `~/.arbol/runtime/exchanges/<exchange uuid>/` instead of `~/Library/Application Support/Arbol/runtime/exchanges/<exchange uuid>/`, and the Codex Driver's state is `~/.arbol/drivers/codex/`.

### The database stays on the internal disk

The data folder and socket are working state and stay on the internal disk. The probe keeps refusing a data folder on an external or removable disk. Mercury is never a place for the live database ([ARC-D84](#decisions)).

### How components find the places

Each repository defines the installation folder once and builds every installed path from it: the database places, the runtime, the App's locks, the registry, each Driver's default state, the browser state and the agent records. Every guard that refuses to let a test or candidate use the installed places takes its path from the same definition. The existing overrides, such as `--state-dir`, `--runtime-dir`, `--registry-dir` and `ARBOL_AGENTS_DIR`, keep working for isolated use.

The folder is `~/.arbol/`, fixed, as `~/Library/Application Support/Arbol/` is fixed today ([ARC-D93](#decisions)). The settings stay in `~/.arbol/` ([ARC-D90](#decisions)).

No component creates anything under `~/Library/Application Support/`. Where code today creates its Application Support ancestors, it creates `~/.arbol/` instead, owner-only.

### What stays put

| Item | Why it stays |
|---|---|
| `~/Library/LaunchAgents/com.sylvan-stack.arbol.database.plist` and `com.sylvan-stack.arbol.app.plist` | launchd reads agents only there. The database plist is rewritten to the new data folder and log |
| Keychain items, such as `com.sylvan-stack.arbol.database` | The Keychain holds secrets; their names do not change |
| `~/.local/bin/` launchers | The shell finds them there. They are regenerated to name `~/.arbol/builds` |
| `~/Library/Preferences/`, `~/Library/WebKit/`, `~/Library/Caches/` entries of the App | macOS keeps them for the App bundle |
| `~/.claude` and other vendor homes outside Arbol | They belong to the vendor tool and the owner |
| `/Library/Application Support/opencode` | The system's managed configuration of Mimo's vendor tool, read only |

### Builds made for the old layout

A Build packages its code, and its code names its places. A Build made before the move looks in the old places. On the moved installation it must not run.

Each Build made for the new layout declares it in its Build description and record, for example `"installationLayout": 2`. Builds without it have layout 1. The launcher and the runtime refuse a layout-1 Build at a default or explicit start, and at writer admission, as they refuse an incompatible schema, and list compatible alternatives on `no_fit`. The move removes no Build, so layout-1 Builds are still there for recovery before reopening. After that they are older Builds like any other: BLD-0 may prune them, and a later recovery rebuilds them from their recorded source revisions ([ARC-D88](#decisions), [ARC-D95](#decisions)).

The layout is not part of `schemaCompatibility`: the move changes no schema. It is a separate fit check, because a component can be schema-compatible and still look in the wrong place.

### When Mercury is not mounted

Arbol runs and settles Exchanges without Mercury. An operation that needs the archive refuses with `archive_unavailable` before it changes anything when `/Volumes/Mercury` is not mounted or `/Volumes/Mercury/Arbol/` is missing:
- a real session import (IMP-0);
- a schema change, whose ARC-4 snapshot and release record go to the archive, refused before maintenance begins ([ARC-D89](#decisions));
- restoring a snapshot;
- the archiving steps of the one-time move.

A path under `/Volumes/` can also exist as a plain folder on the internal disk when the drive is absent. Arbol checks that `/Volumes/Mercury` is a mount point of a volume with Mercury's volume UUID before it writes there, so it never fills the internal disk by mistake.

Mercury does not enforce file modes, and anyone using an unlocked Mercury can read it. The owner accepted that archived secrets, such as Arbol 1's tokens, are protected there only by FileVault while the drive is locked ([ARC-D86](#decisions)). The session import still archives no credentials (IMP-0.13).

### The one-time move

The move runs once, by an operator command, under ARC-4 maintenance. It changes no schema.

1. **Prepare.** Stage the release made for layout 2: every component that names an installed path, with its new launchers and the rewritten database plist. Use the verification scope below to check the affected layout boundaries. Probe, sending no prompt and spending no quota, that Claude Code test homes and the Codex home still work from a new path; record the tool versions. Record the prior release (layout 1) and the staged one as ARC-4 requires.
2. **Fence.** Enter draining, then exclusive maintenance (ARC-4). Wait for accepted Exchanges to finish and settle; an unsettled Exchange, a pending folder or an unaccounted writer blocks the move. Do not force a healthy Exchange.
3. **Snapshot.** Take an ARC-4 snapshot into `/Volumes/Mercury/Arbol/backups/` and verify it by restoring it to isolated state ([ARC-D89](#decisions)). Without Mercury the move does not begin.
4. **Stop.** Stop the App, the backend and, through its launch agent, the database server. Confirm that no process runs from the registry or has a file open under the old folder.
5. **Move the working state.** `~/.arbol/` already exists with mode 0700; check that it does. Rename each working item of [the layout](#the-layout) from the old folder into it, `database/` becoming `postgres/`. No name is taken in `~/.arbol/` today. A rename on the same volume keeps every file, mode, attribute and inode, and copies nothing. The writer admission state moves inside `runtime/`, so the exclusive fence is still held.
6. **Point the system at it.** Change `unix_socket_directories` in `postgresql.conf` to the new socket folder. Rewrite the database plist and the launchers. Mark `~/.arbol/postgres/data` for Time Machine to skip ([ARC-D92](#decisions)). Activate the layout-2 Builds as the selected ones.
7. **Check.** Start the database server through its launch agent and run its probe, including `data-folder` on the internal disk. Check the schema pair and that it matches the snapshot. Check each Driver's account read for its normal Subscriptions and their sign-in state. Check that the old folder holds no working item, and that a layout-1 Build is refused.
8. **Reopen.** Reopen admission to the verified layout-2 release and record the boundary, as ARC-4 requires.
9. **Archive.** Copy the Arbol 1 leftovers, secrets included, to `/Volumes/Mercury/Arbol/legacy/arbol-1/`, and the SYL-314 backup and `~/.arbol/backups/` (one Pi Driver settings backup of 26 October 2026) to `/Volumes/Mercury/Arbol/backups/` ([ARC-D85](#decisions), [ARC-D86](#decisions), [ARC-D95](#decisions)). Verify the copy against a listing of every path, size, mode and SHA-256 recorded before copying. Keep the listing with the copy and on the internal disk. Only then remove the originals. Leave nothing at `~/Library/Application Support/Arbol/` ([ARC-D87](#decisions)).

Step 9 needs no fence, because no current component reads those files. It can run after reopening, or later when Mercury is mounted.

### Recovery

Before reopening, recovery keeps the fence and puts everything back: stop what the move started, rename every item back, restore the original `postgresql.conf`, plist and launchers from their saved copies, reselect the layout-1 Builds, which the move left in place, and verify the prior release before reopening it. If the database cannot be brought back, restore the step-3 snapshot from Mercury as ARC-4 describes.

After reopening, repair forward. Layout-1 Builds stay refused, and may be pruned. A return to the old place would be a new move, under the same rules.

### Verification scope

The owner narrowed verification on 25 November 2026. Reuse existing applicable results. Run existing unit tests for affected behavior and use a short, isolated offline integration check only for a critical boundary that still lacks evidence. Layout refusal at writer admission is such a boundary when its existing coverage does not apply. Full component gates, foreground and provider checks, and repeated move and recovery trials are retired as closeout requirements. Close out the already installed layout 2 using preserved records and state any gaps.

For a future authorized move, use the maintenance, snapshot verification, continuity and recovery procedure above.

## Requirements

| ID | Arbol must | Origin | Verified by |
|---|---|---|---|
| ARC-5.1 | After the move, keep no file or folder of Arbol under `~/Library/Application Support/`, and create none there | Owner, 17 November 2026; IMP-D9 | Installed move journey |
| ARC-5.2 | Keep the installation's working state in `~/.arbol/` with the layout above, owner-only, and keep archival material on Mercury in `/Volumes/Mercury/Arbol/` | Owner, 17 November 2026; ARC-D83 | Installed move journey |
| ARC-5.3 | Keep the database data folder and socket on the internal disk in `~/.arbol/postgres/`, and keep refusing a data folder on an external or removable disk | ARC-D64; ARC-D84 | probe |
| ARC-5.4 | Run and settle Exchanges without Mercury; refuse an archive write, a schema change or a snapshot restore with `archive_unavailable`, before any change, unless Mercury's own volume is mounted | IMP-0.13; ARC-D89 | unit |
| ARC-5.5 | Build every installed path, every default state folder and every guard against the installed places from one definition per repository, and keep the isolation overrides | Research | unit |
| ARC-5.6 | Declare the installation layout in Build descriptions and records, and refuse a Build of another layout at default and explicit start and at writer admission | ARC-4.3; ARC-D88 | Retained layout refusal evidence; focused writer-admission integration only for a critical gap |
| ARC-5.7 | Move the installation once under exclusive ARC-4 maintenance, after a verified snapshot, with the App, backend and database stopped and no active or pending Exchange, by renames on the internal volume; verify it, then reopen with a recorded boundary | ARC-4.4, ARC-4.5; Owner, 17 November 2026 | Installed evidence of exclusive drained maintenance, service stop, verified snapshot, rename and recorded reopen |
| ARC-5.8 | Before reopening, restore the prior layout and release with the fence held when any step fails | ARC-4.5 | Recovery unit tests and retained recovery evidence |
| ARC-5.9 | Keep the Driver sign-ins of normal Subscriptions and their Keychain service names, move native homes inside Driver state whole, never move a vendor home outside Arbol, and list the test Subscriptions that need a new sign-in | ARC-D81; CLD-D20 | probe |
| ARC-5.10 | Archive all the Arbol 1 leftovers on Mercury, secrets included, verify the copy against a recorded listing with hashes, and only then remove the originals | ARC-D85, ARC-D86 | Archive verification record |
| ARC-5.11 | Mark the live database data folder for Time Machine to skip | ARC-D92 | probe |

## Interface

| What | Before | After |
|---|---|---|
| Database data folder | `~/Library/Application Support/Arbol/database/data` | `~/.arbol/postgres/data` |
| Database socket folder | `…/Arbol/database/socket` (75-byte socket path) | `~/.arbol/postgres/socket` (48 bytes) |
| Runtime and backend socket | `…/Arbol/runtime/` (66-byte socket path) | `~/.arbol/runtime/` (39 bytes) |
| Exchange folders | `…/Arbol/runtime/exchanges/` | `~/.arbol/runtime/exchanges/` |
| App locks | `…/Arbol/app/` | `~/.arbol/app/` |
| Build registry | `…/Arbol/builds/` | `~/.arbol/builds/` |
| Driver default state | `…/Arbol/drivers/<driver>/` | `~/.arbol/drivers/<driver>/` |
| Mimo native resource | `…/Arbol/native-resources/mimo/` | `~/.arbol/native-resources/mimo/` |
| Browser profiles | `…/Arbol/browser/` | `~/.arbol/browser/` |
| Agent records | `…/Arbol/agents/` | `~/.arbol/agents/` |
| Session import | (IMP-0) | `~/.arbol/imports/`, `/Volumes/Mercury/Arbol/imports/` |
| Settings | `~/.arbol/` | `~/.arbol/`, unchanged, beside the working state |
| Build field | none | `installationLayout`, a positive integer; absent means 1 |
| Refusal | none | `archive_unavailable` |

## Known problems

- **Records name removed folders.** ASD-4 to ASD-19 name private evidence under `~/Builds/sylvan-stack/arbol/`, including the ASD-16 cutover evidence and both legacy database backups. The owner removed those files on purpose on 17 November 2026 ([ARC-D95](#decisions)); the records stay as history. See the [research](../research/arbol-out-of-application-support.md#older-builds-and-backups).
- **Codex keeps absolute conversation paths.** Codex's own database records where each conversation's file is. After the move, Codex may not find the file of a conversation started before it. Arbol does not write to a vendor tool's database. The step-1 probe shows the effect; one Codex conversation exists today ([ARC-D94](#decisions)).
- **Claude Code test homes need a new sign-in.** Claude Code names its Keychain item after the home's path. Each `test-*` Subscription of the Claude Driver signs in again after the move. The owner's own `anthropic` sign-in in `~/.claude` is not affected.
- **macOS Spotlight.** macOS Spotlight indexes the current folder today, and does not index the hidden `~/.arbol/` (on 17 November 2026 `mdfind -onlyin ~/.arbol` found nothing). After the move, Arbol's files no longer appear in Spotlight searches. Arbol does not change macOS Spotlight settings ([ARC-D91](#decisions)).
- **Many documents name the old path.** About 20 specifications and READMEs spell it out. They change when this specification is accepted, listed in the supersession map below.

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| ARC-D83 <!-- 6c9d7319-0f50-4f02-9a44-8965221b646b --> | Where does Arbol keep its files? | Working state in `~/Arbol/`, archival material on Mercury in `/Volumes/Mercury/Arbol/`, nothing under `~/Library/Application Support/` | Decided 17 November 2026 by the owner: the direction, and the layout above with the defaults the owner accepted the same day. Changed later that day by the owner: the working state goes in `~/.arbol/`, beside the settings, with the database in `~/.arbol/postgres/`, and no `~/Arbol/` folder is used |
| ARC-D84 <!-- bed90192-f957-44a4-8946-de524e107246 --> | Can the live database go on Mercury? | No. The data folder and socket stay on the internal disk in `~/.arbol/postgres/` | Decided 17 November 2026 by the owner: the proposed default (the owner's "proceed" on the open decisions) |
| ARC-D85 <!-- a801ef3c-24a1-4b5f-a0cb-9da5c330524b --> | What happens to the 41 GB left over from Arbol 1, which no current code reads? | Archive all of it, as it is, in `/Volumes/Mercury/Arbol/legacy/arbol-1/`, verify the copy, then remove it from the internal disk | Decided 17 November 2026 by the owner: the proposed default |
| ARC-D86 <!-- f359114a-d2ad-408f-bd0f-e71283b2e04f --> | Can secrets go on Mercury, where file modes are not enforced? | No, as IMP-0.13. Files known to hold secrets, such as Arbol 1's tokens and dispatcher credentials and the SYL-314 auth file, go to `~/Arbol/backups/` on the internal disk | Decided 17 November 2026 by the owner: yes. They go to Mercury with the rest; FileVault protects them while the drive is locked |
| ARC-D87 <!-- f49f51f7-e29d-461f-b365-f2b5756fb62d --> | Does anything stay at the old path, such as a link to `~/Arbol/`? | No. Nothing remains under `~/Library/Application Support/`. Layout-1 Builds are refused instead | Decided 17 November 2026 by the owner: the proposed default |
| ARC-D88 <!-- 619d3f50-7f12-4c39-a76d-8da21e8fc871 --> | What happens to Builds made for the old layout? | They stay in place during the move and the launcher refuses them. Afterwards BLD-0 may prune them like any older Build; recovery rebuilds them from the source revisions in the release record. BLD-0 still protects Builds in use or needed to settle an Exchange | Decided 17 November 2026 by the owner: the proposed default (the owner's "proceed" on the open decisions). The default changed earlier the same day to follow ARC-D95; the first default kept them as recovery payloads |
| ARC-D89 <!-- d3071886-5228-44a5-9e68-032b2ca21255 --> | Where do ARC-4 snapshots and release records go? | On Mercury in `/Volumes/Mercury/Arbol/backups/`, and the latest verified one also in `~/Arbol/backups/` until the next. A schema change refuses with `archive_unavailable` when Mercury is not mounted | Decided 17 November 2026 by the owner: only on Mercury, with no copy on the internal disk. A schema change and a restore need Mercury mounted |
| ARC-D90 <!-- 8dd8901b-a400-46aa-8d06-23cb75ae5cfb --> | Do the settings in `~/.arbol/` move too? | No. They are not under Application Support, and about 30 places name them | Decided 17 November 2026 by the owner: the proposed default (the owner's "proceed" on the open decisions). Since the change to ARC-D83 the working state joins the settings in `~/.arbol/` |
| ARC-D91 <!-- e1bf3143-0565-4494-b212-8aa79056836f --> | Does Arbol keep `~/Arbol/` out of macOS Spotlight? | No. It is indexed today in Application Support. The owner can list folders under Spotlight Privacy | Decided 17 November 2026 by the owner: the proposed default (the owner's "proceed" on the open decisions). Since the change to ARC-D83 the folder is the hidden `~/.arbol/`, which macOS Spotlight does not index |
| ARC-D92 <!-- 68208dea-1ddb-4a6f-94ef-f886ab00709b --> | Does Time Machine back up the live database folder? | No. The move marks `~/.arbol/postgres/data` for Time Machine to skip; ARC-4 snapshots are the database's backup | Decided 17 November 2026 by the owner: the proposed default (the owner's "proceed" on the open decisions) |
| ARC-D93 <!-- 93ffca9d-37b9-436e-867f-792e6107d1ff --> | How do components find `~/.arbol/`? | A fixed path, defined once per repository, with today's isolation overrides | Decided 17 November 2026 by the owner: the proposed default (the owner's "proceed" on the open decisions) |
| ARC-D94 <!-- 9e9f31db-f9fc-4abf-9a85-d8d6839d4156 --> | What if Codex cannot find a conversation started before the move? | Run the probe in step 1 first. If Codex cannot resume a moved conversation, bring the result to the owner before the move | Decided 17 November 2026 by the owner: the proposed default (the owner's "proceed" on the open decisions) |
| ARC-D95 <!-- 0659ba68-db53-4598-837a-e29f396de225 --> | What may `~/Builds` hold, and where do backups and older recovery material go? | `~/Builds` holds only current Builds. Nothing relies on an older Build being there, because any component can be rebuilt from its source revision. Backups and older recovery material go on Mercury, never in `~/Builds` | Decided 17 November 2026 by the owner, after removing older files from `~/Builds`, which had grown to 150 GB: the stated rule. That removal, including the ASD-15 and ASD-16 evidence and both legacy database backups, was deliberate. Also recorded the same day as the Owner Goals OG-2, OG-3 and OG-4 (constraints, `~/Artifacts/goals/`) |
| ARC-D96 <!-- 4b270570-ba08-4a84-a919-ce1114efaf29 --> | A rebuilt App is not the same signed binary. How is a prior release's App recovered? | Archive the prior release's signed App bundle (about 12 MB) with its release record in `/Volumes/Mercury/Arbol/backups/`, not in `~/Builds` | Decided 17 November 2026 by the owner: the proposed default (the owner's "proceed" on the open decisions) |

## Supersession map

Applied on acceptance, 17 November 2026: each accepted specification below carries a File layout amendment naming ARC-5, and its affected Decisions an Amended note. Code READMEs change with the Beats that change their code. Their historical decisions keep their dates; the amendment names ARC-5.

| Earlier text | ARC-5 treatment |
|---|---|
| [ARC-0](00-components-and-boundaries.md) ARC-D64, the data folder | `~/.arbol/postgres/data`; the internal-disk rule stays |
| [ARC-4](04-single-database.md) installation runtime directory | `~/.arbol/runtime/`; Build fit adds the layout check |
| [BLD-0](../builds/00-builds-and-versions.md) BLD-D5, the registry | `~/.arbol/builds/`; Build descriptions add `installationLayout` |
| [DRV-0](../driver-contract/00-overview-and-boundary.md) DRV-D3 and [DRV-6](../driver-contract/06-state-and-simultaneous-calls.md) | Default state `~/.arbol/drivers/<driver>/` |
| [BKD-0](../backend/00-the-arbol-backend.md) data folder and examples | New paths |
| [AGR-0](../agent-records/00-the-agent-record.md) AGR-0.1 | `~/.arbol/agents/` |
| [BRW-0](../../arbol-browser/specs/00-the-browser-component.md), [BRW-1](../../arbol-browser/specs/01-profiles-and-browser-data.md) | `~/.arbol/browser/` |
| Codex, Mimo and Pi Driver specifications naming the default state | New default |
| [IMP-0](../session-import/00-the-import.md) IMP-0.13 | ARC-5 adopts its rule. Its working files and IMP-1's Mimo copy moved from `~/Arbol/imports/` to `~/.arbol/imports/` on 17 November 2026 (ARC-D83) |
| [ARC-4](04-single-database.md) release records, verification and recovery; `arbol/database/README.md` "Database recovery before reopening" | Snapshots, restore receipts and release records go in `/Volumes/Mercury/Arbol/backups/` (ARC-D89, ARC-D95). "Retain or verify access to the payloads or reproducible inputs" is met by recorded source revisions, except the signed App (ARC-D96) |
| [Cutover runbook](../../forester/sagas/sylvan-stack/arbol-single-database/installed-transition/cutover-runbook.md) step 1, `RUN` under `~/Builds/sylvan-stack/arbol/`; step 2, saving the signed App | A future run keeps recovery material on Mercury. A dated note in the runbook says so |
| [BLD-0](../builds/00-builds-and-versions.md) retention and pruning | Unchanged for Builds in use, needed to settle an Exchange, Locked or default. Older Builds are not recovery inputs; recovery rebuilds them (ARC-D95) |
| Mycel's [Build output guide](../../mycel/operations/build-output.md), "Retained outputs and test runtimes" in `~/Builds/` | To reconcile with ARC-D95: only current Builds stay in `~/Builds`; older retained output goes to Mercury or is rebuilt |
| READMEs: `arbol/database/README.md`, `arbol/builds/README.md`, the Driver and App READMEs; Mycel's [Build output guide](../../mycel/operations/build-output.md) | New paths |

## Evidence and related specifications

[Research](../research/arbol-out-of-application-support.md) inventories every item, its size and owner, the code that names its path, and the constraints above. [ARC-4](04-single-database.md) governs the maintenance and recovery the move uses. [IMP-0](../session-import/00-the-import.md#the-raw-archive) set the rule this specification extends.

<!-- sources:
arbol:research/arbol-out-of-application-support.md
arbol:architecture/04-single-database.md#Maintenance and writer admission
arbol:architecture/04-single-database.md#Release records, verification and recovery
arbol:session-import/00-the-import.md#The raw archive
-->
