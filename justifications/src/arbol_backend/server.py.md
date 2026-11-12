---
role: authored
---
# Justifications

## Backend.__init__

Reason: Bind backend and direct Vigor operations to authoritative installation leases, register PostgreSQL sessions before writes, and stamp detached lifecycle dispatch with the held generation

Origins: ARC-4.4 · Intention i-4f63d0c4 · 2026-11-12

## <before Backend>

Reason: Bind backend and direct Vigor operations to authoritative installation leases, register PostgreSQL sessions before writes, and stamp detached lifecycle dispatch with the held generation

Origins: ARC-4.4 · Intention i-4f63d0c4 · 2026-11-12

## Backend.monitor

Reason: Keep Vigor paused until admitted, resume a due tick after reopening, and leave empty history until a new report.

Origins: ARC-4.4, ARC-4.7 · Intention i-fded1ae6 · 2026-11-12

## Backend.run

Reason: Keep safe saved reads, preserve captured retries and revalidate when maintenance reopens without a database outage.

Origins: ARC-4.4, ARC-4.7 · Intention i-8e23ab0f · 2026-11-12

## Backend.initial_catalogue

Removed: Make App and CLI acquisition share the private installation lifetime lock and readiness contract.

Removed by Intention i-961a1afa · 2026-11-12

## Backend.connection

Reason: Keep safe saved reads, preserve captured retries and revalidate when maintenance reopens without a database outage.

Origins: ARC-4.4, ARC-4.7 · Intention i-8e23ab0f · 2026-11-12

## Backend.listed

Reason: Coalesce inventory by Exchange UUID and verify event folders against the recorded assignment and process.

Origins: ARC-4.1, ARC-4.6 · Intention i-37a0246e · 2026-11-12

## Backend.hello

Reason: Keep safe saved reads, preserve captured retries and revalidate when maintenance reopens without a database outage.

Origins: ARC-4.4, ARC-4.7 · Intention i-8e23ab0f · 2026-11-12

## Backend.watch_maintenance

Reason: Keep safe saved reads, preserve captured retries and revalidate when maintenance reopens without a database outage.

Origins: ARC-4.4, ARC-4.7 · Intention i-8e23ab0f · 2026-11-12

## Backend.task

Reason: Keep Vigor paused until admitted, resume a due tick after reopening, and leave empty history until a new report.

Origins: ARC-4.4, ARC-4.7 · Intention i-fded1ae6 · 2026-11-12

## Backend.wake_vigor

Reason: Keep Vigor paused until admitted, resume a due tick after reopening, and leave empty history until a new report.

Origins: ARC-4.4, ARC-4.7 · Intention i-fded1ae6 · 2026-11-12

