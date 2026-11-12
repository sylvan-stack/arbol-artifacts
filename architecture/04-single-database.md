---
role: authored
spec: ARC-4
status: draft
---
# Architecture · 04 Single database and schema upgrades

Arbol uses one installed PostgreSQL database. Trunks keep their identities and independent Builds as the database changes. A breaking schema change ships with compatible Builds of the Trunks and other consumers it affects. The owner chose this architecture on 12 November 2026, accepted maintenance windows, and authorized an empty start after backing up the existing databases. The specification is drafted in ASD-1 of the Arbol Single Database Saga.

## Scope

The installed database, schema changes and compatibility, Exchange drainage during maintenance, backup and recovery, the one-time clean start, and removal of Root identity from the running product. Once accepted, this specification replaces the operating model in [ARC-1](01-roots.md) and governs amendments to ARC-0/2/3, Builds, the Trunk runtime, the backend and Bridge, Driver chat identity, Subscriptions Vigor, the App and Forester integrations. The existing specifications retain their historical decisions and evidence.

## Behaviour

### Database and compatible Builds

The installation has one database and one ordered schema migration sequence. Arbol's migration tooling applies the schema and records the installed revision. Trunks can add features that require tables or columns through this sequence. They use the installed schema when running an Exchange. A compatible change can leave existing Builds usable. A breaking change is delivered with adaptations for every affected Trunk and other consumer needed by the installation. Both default and explicit Build selection check compatibility with the installed schema.

The database records a migration revision and a schema compatibility version. An additive migration that preserves existing behavior advances the revision and retains the compatibility version. A breaking migration advances both. A Build declares the compatibility versions it supports and the minimum migration revision it needs for each. A launch is eligible when its Build supports the installed compatibility version and the installed revision meets that minimum. A legacy Build record that declares only a Root Contract is ineligible on the single database. An older Trunk can therefore keep working after an additive migration, while a Build that needs a newly added table waits for the migration that creates it.

Arbol still starts one detached Trunk per accepted Exchange. Each accepted Exchange retains the concrete Build that started it. Discovery, stopping and settlement use the Exchange identity and the single installation. The App uses one backend. Seqoya Lab has one administration window and reads the installation's subscription data and saved Vigor. Chat identity for new activity uses the chat UUID. Historical integration records keep the identity they recorded.

The installation Bridge uses a new protocol version because its hello replaces the Root record with installation context. The App and backend activate as a matching pair. A mismatched Bridge version receives a visible compatibility refusal and sends no operations. Recovery uses the App and backend versions that belong to the restored release.

The existing `arbol-trunk run` command starts an Exchange from the terminal with the App closed. It uses the installed schema and the same admission boundary as App starts. The `arbol` command exposes backend and Vigor operations for the single installation. A temporary database outage can leave health and Driver-only reads available. An incompatible schema prevents database-dependent operations and yields a distinct refusal.

When calling Claude or Codex, an Arbol Trunk marks its `chatSessionId` as an Arbol chat with `arbolChat: true`. Those Drivers require a lowercase UUID with hyphens in that case and set `ARBOL_CHAT` from it for that run. Standalone requests can continue using opaque `chatSessionId` values for continuity. An absent marker leaves `ARBOL_CHAT` unset. Both paths ignore inherited Arbol identity variables and keep the existing continuity lookup. Claude and Codex refuse malformed marked requests and legacy `rootId` requests before starting a vendor tool. Trunks send `chatSessionId` for continuity to Pi and MiMo without either identity marker. Pi and MiMo keep their current continuity behavior. The cutover activates matching Trunk and Driver Builds together. Arbol hooks use `ARBOL_CHAT` to recognize new Arbol runs. Historical records retain the original identity values.

### Maintenance and recovery

Before a schema migration, record the Git revisions and Build inputs that identify the running release and take a restorable database snapshot. For a breaking migration, enter maintenance first. Block new Exchanges and ordinary writes through the App, CLI and listeners. Allow already accepted Exchanges and controlled settlement to finish writing during drainage. Take the snapshot after drainage and settlement, while writes are still blocked, and then apply the migration. If a long Exchange is still running, maintenance can wait or be rescheduled.

During drainage, answering or stopping an accepted Exchange and completing its recovery writes use controlled admission. Once exclusive migration starts, those writes are fenced too. Read paths can return saved data while the schema can be read safely. When a read would also reconcile a Draft or another record, defer the write until normal admission returns. Pause writes from manual and periodic Vigor refreshes and ordinary backend writes, including saving a paste to the installation's file store. Driver account reads and cache refreshes can proceed if they touch only Driver state outside the installed database.

Apply the migration to the existing database and verify the compatible Builds before accepting normal work again. A failed upgrade before reopening can recover the snapshot and the matching Builds. After reopening, repair the installed release forward by default. Restore an older snapshot only after re-entering maintenance and verifying that every write accepted since that snapshot has been captured and can be reapplied without loss. If that cannot be verified, repair forward. Keep release recovery based on known Git revisions and their recorded Build inputs.

### First installation without Roots

Use a maintenance window for the transition. Back up both existing databases and verify that their backups restore outside the live installation. Preserve the configuration and source revisions needed for recovery. Then clear and initialize the new baseline in the existing database chosen to remain live. Keep the earlier database data in the backups. Start with empty chats, Drafts and Vigor history. The database reset does not require resetting Driver sign-ins.

The maintenance procedure resolves pending Exchange files and open bookings that belong to the old runtime before retiring it. Old launch paths must be unable to write to the reinitialized database. Confirm the new baseline is empty before reopening for normal work. Later schema migrations preserve existing application data according to the migration.

## Requirements

| ID | Arbol must | Origin | Verified by |
|---|---|---|---|
| ARC-4.1 | Use one installed PostgreSQL database, one backend and one schema migration sequence, without named Root environments | Owner, 12 November 2026 | Installed application and CLI journey |
| ARC-4.2 | Apply future schema migrations in place, record the installed schema revision and preserve existing data through the specified transformations | Owner, 12 November 2026 | Migration on a populated disposable database |
| ARC-4.3 | Keep Trunk identities and Builds independently versioned and refuse incompatible Builds at default and explicit start | Owner direction and existing Build selection guarantees | Compatible and incompatible Build journeys |
| ARC-4.4 | Prevent new write work during breaking maintenance, allow existing Exchanges to finish and settle pending results before changing the schema | Owner accepted maintenance, ARC-2 lifecycle | Maintenance drill with active and unsettled Exchanges |
| ARC-4.5 | Take a database snapshot before a schema migration, record the source revisions and Build inputs, and recover the previous release from matching data and code | Owner, 12 November 2026 | Restore and recovery rehearsal |
| ARC-4.6 | Keep accepted Exchanges associated with their concrete Trunk Build and support discovery, stopping and settlement across app restarts | ARC-2 and ARC-3 | Detached Exchange restart and recovery journeys |
| ARC-4.7 | Serve the App and administration without Root selection, and preserve chat identity and historical integration records | Owner removes Root concept, BKD and DRV identity behavior | Seqoya Lab and both Driver/Forester paths |
| ARC-4.8 | Verify recoverable backups of both existing databases before the one-time reset, initialize an empty baseline in the retained database, and retire old write paths before reopening | Owner authorized empty start after backup, 12 November 2026 | Clean-start rehearsal and installed cutover evidence |

## Decisions

| ID | Decision | Status |
|---|---|---|
| ARC-D76 | Replace named Roots with one installed database. Upgrade that database in place and adapt incompatible Trunks while keeping their identities. | Owner, 12 November 2026 |
| ARC-D77 | Take database snapshots before schema changes. Recover code from recorded Git revisions. | Owner, 12 November 2026 |
| ARC-D78 | Use a maintenance window for the installed transition and breaking schema changes. Start the new installation with empty application data after backup. | Maintenance accepted and clean start authorized by the owner, 12 November 2026 |

## Evidence and related specifications

[Research](../research/arbol-single-database.md) traces database, Build, Exchange, App and integration dependencies. Reconcile the affected interfaces and configuration requirements before opening implementation Beats. Implementation plans specify the files and internal mechanisms that satisfy them.

<!-- sources:
arbol:research/arbol-single-database.md
arbol:architecture/01-roots.md#What a Root is
arbol:architecture/02-chat-exchange-across-components.md#When the database cannot be reached
arbol:backend/03-the-arbol-swift-app.md#Windows and renderer Builds
-->
