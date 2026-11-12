---
role: authored
---
# Justifications

## Database.__init__

Reason: Hold ordinary admission over backend mutations and prevent cancellation from detaching a protected file write.

Origins: ARC-4.4 · Intention i-b70c1b8e · 2026-11-12

## Database.session

Reason: Measure only the configured installation and refresh status and views when schema access returns.

Origins: ARC-4.1, ARC-4.7 · Intention i-bd55831d · 2026-11-12

## credentials

Reason: Measure only the configured installation and refresh status and views when schema access returns.

Origins: ARC-4.1, ARC-4.7 · Intention i-bd55831d · 2026-11-12

## <before Unavailable>

Removed: Resolve a single installation configuration and enforce the installed schema contract before database work.

Removed by Intention i-fd7b43a3 · 2026-11-12

## <before Schema>

Reason: Hold ordinary admission over backend mutations and prevent cancellation from detaching a protected file write.

Origins: ARC-4.4 · Intention i-b70c1b8e · 2026-11-12

## Database.read_schema

Reason: Measure only the configured installation and refresh status and views when schema access returns.

Origins: ARC-4.1, ARC-4.7 · Intention i-bd55831d · 2026-11-12

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

Reason: Hold ordinary admission over backend mutations and prevent cancellation from detaching a protected file write.

Origins: ARC-4.4 · Intention i-b70c1b8e · 2026-11-12

## Admission

Reason: Hold ordinary admission over backend mutations and prevent cancellation from detaching a protected file write.

Origins: ARC-4.4 · Intention i-b70c1b8e · 2026-11-12

## Admission.permit

Reason: Hold ordinary admission over backend mutations and prevent cancellation from detaching a protected file write.

Origins: ARC-4.4 · Intention i-b70c1b8e · 2026-11-12

## Admission.status

Reason: Hold ordinary admission over backend mutations and prevent cancellation from detaching a protected file write.

Origins: ARC-4.4 · Intention i-b70c1b8e · 2026-11-12

## Database.permit

Reason: Hold ordinary admission over backend mutations and prevent cancellation from detaching a protected file write.

Origins: ARC-4.4 · Intention i-b70c1b8e · 2026-11-12

## protected_thread

Reason: Hold ordinary admission over backend mutations and prevent cancellation from detaching a protected file write.

Origins: ARC-4.4 · Intention i-b70c1b8e · 2026-11-12

