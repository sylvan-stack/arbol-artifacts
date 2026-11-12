---
role: authored
---
# Justifications

## Database.__init__

Reason: Keep safe saved reads, preserve captured retries and revalidate when maintenance reopens without a database outage.

Origins: ARC-4.4, ARC-4.7 · Intention i-8e23ab0f · 2026-11-12

## Database.session

Reason: Keep safe saved reads, preserve captured retries and revalidate when maintenance reopens without a database outage.

Origins: ARC-4.4, ARC-4.7 · Intention i-8e23ab0f · 2026-11-12

## credentials

Reason: Start and retry the same Exchange through the installation runtime and preserve the concrete acceptance receipt.

Origins: ARC-4.6, ARC-4.7 · Intention i-d912d724 · 2026-11-12

## <before Unavailable>

Removed: Resolve a single installation configuration and enforce the installed schema contract before database work.

Removed by Intention i-fd7b43a3 · 2026-11-12

## <before Schema>

Reason: Bind backend and direct Vigor operations to authoritative installation leases, register PostgreSQL sessions before writes, and stamp detached lifecycle dispatch with the held generation

Origins: ARC-4.4 · Intention i-4f63d0c4 · 2026-11-12

## Database.read_schema

Reason: Start and retry the same Exchange through the installation runtime and preserve the concrete acceptance receipt.

Origins: ARC-4.6, ARC-4.7 · Intention i-d912d724 · 2026-11-12

## Schema

Reason: Resolve a single installation configuration and enforce the installed schema contract before database work.

Origins: ARC-4.1, ARC-4.4 · Intention i-fd7b43a3 · 2026-11-12

## Schema.pair

Reason: Resolve a single installation configuration and enforce the installed schema contract before database work.

Origins: ARC-4.1, ARC-4.4 · Intention i-fd7b43a3 · 2026-11-12

## Schema.require

Reason: Resolve a single installation configuration and enforce the installed schema contract before database work.

Origins: ARC-4.1, ARC-4.4 · Intention i-fd7b43a3 · 2026-11-12

## release_history

Reason: Hold ordinary admission over backend mutations and prevent cancellation from detaching a protected file write.

Origins: ARC-4.4 · Intention i-b70c1b8e · 2026-11-12

## <before Admission>

Removed: Bind backend and direct Vigor operations to authoritative installation leases, register PostgreSQL sessions before writes, and stamp detached lifecycle dispatch with the held generation

Removed by Intention i-4f63d0c4 · 2026-11-12

## Admission

Removed: Bind backend and direct Vigor operations to authoritative installation leases, register PostgreSQL sessions before writes, and stamp detached lifecycle dispatch with the held generation

Removed by Intention i-4f63d0c4 · 2026-11-12

## Admission.permit

Removed: Bind backend and direct Vigor operations to authoritative installation leases, register PostgreSQL sessions before writes, and stamp detached lifecycle dispatch with the held generation

Removed by Intention i-4f63d0c4 · 2026-11-12

## Admission.status

Removed: Bind backend and direct Vigor operations to authoritative installation leases, register PostgreSQL sessions before writes, and stamp detached lifecycle dispatch with the held generation

Removed by Intention i-4f63d0c4 · 2026-11-12

## Database.permit

Reason: Bind backend and direct Vigor operations to authoritative installation leases, register PostgreSQL sessions before writes, and stamp detached lifecycle dispatch with the held generation

Origins: ARC-4.4 · Intention i-4f63d0c4 · 2026-11-12

## protected_thread

Reason: Hold ordinary admission over backend mutations and prevent cancellation from detaching a protected file write.

Origins: ARC-4.4 · Intention i-b70c1b8e · 2026-11-12

## configured_target

Reason: Start and retry the same Exchange through the installation runtime and preserve the concrete acceptance receipt.

Origins: ARC-4.6, ARC-4.7 · Intention i-d912d724 · 2026-11-12

## database_fields

Reason: Start and retry the same Exchange through the installation runtime and preserve the concrete acceptance receipt.

Origins: ARC-4.6, ARC-4.7 · Intention i-d912d724 · 2026-11-12

## explicit_target

Reason: Start and retry the same Exchange through the installation runtime and preserve the concrete acceptance receipt.

Origins: ARC-4.6, ARC-4.7 · Intention i-d912d724 · 2026-11-12

## private_socket

Reason: Start and retry the same Exchange through the installation runtime and preserve the concrete acceptance receipt.

Origins: ARC-4.6, ARC-4.7 · Intention i-d912d724 · 2026-11-12

## Database.connection

Reason: Bind backend and direct Vigor operations to authoritative installation leases, register PostgreSQL sessions before writes, and stamp detached lifecycle dispatch with the held generation

Origins: ARC-4.4 · Intention i-4f63d0c4 · 2026-11-12

## Database.observe_maintenance

Reason: Keep safe saved reads, preserve captured retries and revalidate when maintenance reopens without a database outage.

Origins: ARC-4.4, ARC-4.7 · Intention i-8e23ab0f · 2026-11-12

## Database.readable

Reason: Keep safe saved reads, preserve captured retries and revalidate when maintenance reopens without a database outage.

Origins: ARC-4.4, ARC-4.7 · Intention i-8e23ab0f · 2026-11-12

## <before current_lease>

Reason: Bind backend and direct Vigor operations to authoritative installation leases, register PostgreSQL sessions before writes, and stamp detached lifecycle dispatch with the held generation

Origins: ARC-4.4 · Intention i-4f63d0c4 · 2026-11-12

## current_lease

Reason: Bind backend and direct Vigor operations to authoritative installation leases, register PostgreSQL sessions before writes, and stamp detached lifecycle dispatch with the held generation

Origins: ARC-4.4 · Intention i-4f63d0c4 · 2026-11-12

