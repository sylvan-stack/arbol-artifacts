---
role: authored
---
# Justifications

## <before Measurements>

Reason: The backend and admission must agree on the new runtime directory and PostgreSQL guards while preserving isolated overrides.

Origins: ARC-5.1, ARC-5.2, ARC-5.3, ARC-5.5 · Intention i-7edd5e18 · 2026-11-19

## Measurements.__init__

Reason: Measure only the configured installation and refresh status and views when schema access returns.

Origins: ARC-4.1, ARC-4.7 · Intention i-bd55831d · 2026-11-12

## Measurements.collect

Reason: Measure only the configured installation and refresh status and views when schema access returns.

Origins: ARC-4.1, ARC-4.7 · Intention i-bd55831d · 2026-11-12

## Measurements.mark

Reason: Measure only the configured installation and refresh status and views when schema access returns.

Origins: ARC-4.1, ARC-4.7 · Intention i-bd55831d · 2026-11-12

## Measurements.limited_disk

Reason: The backend and admission must agree on the new runtime directory and PostgreSQL guards while preserving isolated overrides.

Origins: ARC-5.1, ARC-5.2, ARC-5.3, ARC-5.5 · Intention i-7edd5e18 · 2026-11-19

