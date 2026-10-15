---
role: authored
---
# Architecture

How Arbol 2 is divided into components, what each one owns, and how Arbol stays usable when a later version breaks with an earlier one. The owner decided the original points on 9 October 2026 and on 12 October merged the former Ring environment into the named Root (ARC-D47). Each decision is recorded with its outcome in a *Decisions* table. On 13 October 2026 the owner had ARC-0 to ARC-2 assessed and decided the points the assessment raised (ARC-D48 to ARC-D56), had ARC-3 written and decided its five points (ARC-D57 to ARC-D61), and accepted all four specifications.

The inside of an [Arbol Trunk](../GLOSSARY.md#arbol-trunk) is absent on purpose. This chapter says only what the rest of Arbol needs from any Trunk ([ARC-0](00-components-and-boundaries.md#what-any-trunk-must-offer)). How a Trunk works is specified separately, for the first Trunk in the [Trivial Trunk's specifications](../../arbol-trunk/trunks/trivial/specs/README.md).

## Specifications

| Spec | Title | Status |
|---|---|---|
| [ARC-0](00-components-and-boundaries.md) | Components and boundaries | accepted |
| [ARC-1](01-roots.md) | Roots | accepted |
| [ARC-2](02-chat-exchange-across-components.md) | A Chat Exchange across the components | accepted |
| [ARC-3](03-stuck-trunks.md) | Stuck Trunks | accepted |

## The whole in one picture

```text
Arbol Swift App                    one, outside every Root: tray menu, hotkeys, the UIs' web views
  └─ Arbol backend                 one per Root in use: answers the Bridge, holds the listeners
Named Root                         persistent identity, settings, database and compatible components
  └─ arbol-root Build              one command per call; no manager stays running
arbol-trunk                        one detached process per Chat Exchange in progress
  ├─ arbol-codex-driver run        one per run (DRV-2)
  │    └─ codex                    the vendor tool
  └─ arbol-classifier              one per classification, to Jev
PostgreSQL                         one server on the Mac, one database per Root
```

A [Root](01-roots.md) is a named persistent compatibility environment: its own folder, database, settings and compatible Builds of `arbol` and `arbol-root`. Its manager supports every compatible Trunk implementation. Compatible releases provide new Builds in the same Root; incompatible contracts or durable state require another Root alongside it. The Drivers, their Subscriptions and the Trunk Builds are shared by all Roots. On App or backend restart, Arbol discovers each retained Root and asks its compatible manager to list its running Exchanges; no accepted Exchange changes Root or Trunk Build. The Arbol Swift App is built from a repository of its own, `arbol-app`, and each Root names the oldest of its Builds that the Root works with.

## Conventions

The chapter follows the conventions of the [Driver Contract](../driver-contract/README.md#conventions): the shape of a specification, requirement identifiers (`ARC-1.4` is requirement 4 of specification 1), origin, status, decisions and wording. Decisions are numbered once for the whole chapter, `ARC-D1` onwards.

**Verified by.** Two kinds of check are added to those of the Driver Contract, both taken from the validation practice that the version 1 incidents taught:

| Check | Meaning |
|---|---|
| journey | The installed application performs the step on realistic data, and something looks at what is displayed |
| drill | A failure is caused on purpose (a process killed, the database stopped, a folder deleted) and the application ends in a truthful state and stays usable |

*probe* is used here also for a scripted check against the installed database server.

*contract*, in a requirement that a Trunk must meet, means the conformance suite of the [Root Contract](../../arbol-root/contract/README.md) ([RCT-4](../../arbol-root/contract/04-conformance.md)).

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#Validation practice`
