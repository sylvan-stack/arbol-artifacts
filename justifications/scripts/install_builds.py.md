---
role: authored
---
# Justifications

## install

Reason: Retire generation and installation of the Root runtime launchers

Origins: ARC-4.1, ARC-4.8 · Intention i-de10fbd4 · 2026-11-12

## <before probe>

Reason: Use the same installation lease to protect Build recovery inputs and stage its private module in both consumers.

Origins: ARC-4.4, ARC-4.5 · Intention i-e245baed · 2026-11-12

## install_schema_reader

Reason: Protect the installed schema’s default Trunk from pruning and run the delivered reader with the pinned psycopg dependency.

Origins: ARC-4.1, ARC-4.3 · Intention i-53c98edf · 2026-11-12

