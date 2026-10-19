---
role: authored
---
# Driver Contract

What every Arbol 2 [Driver](../GLOSSARY.md#driver) does, written once. The two Drivers, `arbol-claude-driver` and `arbol-codex-driver`, each carry their own specifications that mirror the numbering here and say how the contract is met with one vendor tool.

A Driver in Arbol 2 is a bridge to a vendor's agent. It does two things: it manages [Subscriptions](../GLOSSARY.md#subscription) (sign-in, credential, status, usage, model list), and it runs inference with a Subscription, a model and model settings that the caller names. It decides nothing else and keeps no conversation: chat sessions and their history belong to Arbol and its Trunks. Each Driver is a command-line program of its own: Arbol starts it once per operation and holds none of its code.

## Specifications

| Spec | Title | Status |
|---|---|---|
| [DRV-0](00-overview-and-boundary.md) | Overview and boundary | accepted |
| [DRV-1](01-subscriptions.md) | Subscriptions | accepted |
| [DRV-2](02-inference.md) | Inference | accepted |
| [DRV-3](03-tools-and-permissions.md) | Tools and permissions | accepted |
| [DRV-4](04-errors-and-limits.md) | Errors and limits | implemented |
| [DRV-5](05-conformance.md) | Conformance | accepted |
| [DRV-6](06-state-and-simultaneous-calls.md) | State and simultaneous calls | accepted |

Driver specifications: [Claude Driver](../../arbol-claude-driver/specs/README.md) (`CLD`), [Codex Driver](../../arbol-codex-driver/specs/README.md) (`CDX`).

## Conventions

**Shape of a specification.** Purpose, Scope, Behaviour, Requirements, Interface, Known problems, Decisions. Behaviour sections that describe version 1 end with ordinary historical evidence locators such as `arbol_deprecated_v1:path#symbol`, so a changed or disputed claim can be checked against the frozen code or corpus. These citations are not machine-readable Source Ref declarations and create no provenance edges.

**Source Refs.** A [Source Ref](../GLOSSARY.md#source-ref) may name only an enabled repository. Use machine-readable section comments or frontmatter `sources:` only for claims about enabled repositories; active contract references such as `arbol:driver-contract/02-inference.md#Behaviour` stay Source Refs. References to disabled or frozen repositories remain ordinary Markdown links or historical locators, with their exact paths and symbols preserved.

**Requirement identifiers.** `DRV-1.4` is requirement 4 of contract specification 1. A Driver specification with the same number refines it: `CLD-1.x` and `CDX-1.x` state how `DRV-1` is met. A number is never reused. A withdrawn requirement leaves its table and is named in a sentence below it, with the date and the decision that withdrew it.

**Origin.** Every requirement says where it comes from, relative to version 1:

| Origin | Meaning |
|---|---|
| Kept | Version 1 behaved this way and the behaviour is carried over |
| Changed | Version 1 behaved differently; *Known problems* says why |
| New | Version 1 had no counterpart |
| Dropped | Version 1 behaviour deliberately not carried over, listed so it is not reintroduced by accident |

**Verified by.** The kind of check that proves a requirement, replaced by the test's name once it exists:

| Check | Meaning |
|---|---|
| unit | Automated, no vendor tool involved |
| contract | The shared conformance suite of DRV-5, run against each Driver with a scripted stand-in for the vendor tool |
| probe | A scripted check against the installed vendor tool that sends no prompt and spends no quota. Its record names the tool version and the date |
| live | A check against a real account that spends quota. Run on demand, never in the automatic suite |

**Status.** `draft` → `review` → `accepted` → `implemented`. Implementation work is opened only for an accepted specification. A specification is `implemented` when every requirement names its check and the checks pass.

**Decisions.** A question the old code cannot settle is a row in the specification's *Decisions* table with a proposed default. Work proceeds on the default. When the owner decides, the row records the outcome and the date, and the requirements are updated in the same change.

**Wording.** *Observed* means read in the version 1 source or seen in a probe recorded here. *Proposed* means a design for Arbol 2. Requirements are Proposed by nature; their origin column says what they rest on. Examples are fictional: no credentials, account names or conversation content.
