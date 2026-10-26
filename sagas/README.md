---
role: authored
---
# Sagas

Specifications for the [Saga](../GLOSSARY.md#saga) family, its presentation
in the [Radar](../GLOSSARY.md#radar), and the Radar's Subscription metrics. A Saga contains Arcs, and an Arc contains
Beats. The existing workflow remains in [Working in Sagas](../../mycel/operations/sagas.md).

## Specifications

| Spec | Title | Status |
|---|---|---|
| [SGM-0](00-metrics.md) | Priority, Need Attention, Readiness, Volume and Momentum | draft |
| [SGM-1](01-subscriptions-vigor.md) | Subscriptions Vigor | draft |

## Conventions

This chapter follows the specification shape, origin, verification, status
and wording conventions of the [Driver Contract](../driver-contract/README.md#conventions).
Requirements use `SGM-0.1` onwards; decisions use `SGM-D1` onwards, never
reusing an identifier. Examples are fictional. These metrics are new design,
not a description of an implemented scorer.

An open decision has a concrete proposal that can be discussed and used in
labelled examples. It does not approve production coefficients, change an
existing Saga's priority, or enable scheduling. The chapter remains draft
while its estimation and calibration rules are being settled.
