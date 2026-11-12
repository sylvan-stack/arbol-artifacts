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

Arbol still starts one detached Trunk per accepted Exchange. Each accepted Exchange retains the concrete Build that started it. Discovery, stopping and settlement use the Exchange identity and the single installation. The App uses one backend. Seqoya Lab has one administration window and reads the installation's subscription data and saved Vigor. Chat identity for new activity uses the chat UUID. Historical integration records keep the identity they recorded.

### Maintenance and recovery

Before a schema migration, record the Git revisions and Build inputs that identify the running release and take a restorable database snapshot. For a breaking migration, enter maintenance before the snapshot. Block new Exchanges and ordinary writes through the App, CLI and listeners. Allow already accepted Exchanges and controlled settlement to finish writing during drainage. Apply the change only after incompatible writers have finished or been stopped through their normal lifecycle. If a long Exchange is still running, the maintenance can wait or be rescheduled.

Apply the migration to the existing database and verify the compatible Builds before accepting normal work again. A failed upgrade before reopening can recover the snapshot and the matching Builds. A restore after reopening must account for writes accepted since the snapshot. Keep release recovery based on known Git revisions and their recorded Build inputs.

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
