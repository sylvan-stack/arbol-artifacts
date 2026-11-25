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

Reason: Fence restored database targets before accepting Browser bindings, recheck the exact Driver proof under that authority, and package the verifier at revision 6.

Origins: BRW-1.14, DRV-6.19 · Intention i-086414eb · 2026-11-25

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

Reason: The backend and admission must agree on the new runtime directory and PostgreSQL guards while preserving isolated overrides.

Origins: ARC-5.1, ARC-5.2, ARC-5.3, ARC-5.5 · Intention i-7edd5e18 · 2026-11-19

## database_fields

Reason: Start and retry the same Exchange through the installation runtime and preserve the concrete acceptance receipt.

Origins: ARC-4.6, ARC-4.7 · Intention i-d912d724 · 2026-11-12

## explicit_target

Reason: Start and retry the same Exchange through the installation runtime and preserve the concrete acceptance receipt.

Origins: ARC-4.6, ARC-4.7 · Intention i-d912d724 · 2026-11-12

## private_socket

Reason: The backend and admission must agree on the new runtime directory and PostgreSQL guards while preserving isolated overrides.

Origins: ARC-5.1, ARC-5.2, ARC-5.3, ARC-5.5 · Intention i-7edd5e18 · 2026-11-19

## Database.connection

Reason: Verify import reads against the admitted connection identity and the installed migration ledger

Origins: IMP-0.19, IMP-0.22, ARC-4.4 · Intention i-15647c06 · 2026-11-21

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

## Database.import_read

Reason: Verify import reads against the admitted connection identity and the installed migration ledger

Origins: IMP-0.19, IMP-0.22, ARC-4.4 · Intention i-15647c06 · 2026-11-21

## Database.browser_authority

Reason: Fence restored database targets before accepting Browser bindings, recheck the exact Driver proof under that authority, and package the verifier at revision 6.

Origins: BRW-1.14, DRV-6.19 · Intention i-086414eb · 2026-11-25

## Database.browser_endpoint

Reason: Fence restored database targets before accepting Browser bindings, recheck the exact Driver proof under that authority, and package the verifier at revision 6.

Origins: BRW-1.14, DRV-6.19 · Intention i-086414eb · 2026-11-25

## Database.verify_browser_epoch

Reason: Fence restored database targets before accepting Browser bindings, recheck the exact Driver proof under that authority, and package the verifier at revision 6.

Origins: BRW-1.14, DRV-6.19 · Intention i-086414eb · 2026-11-25

