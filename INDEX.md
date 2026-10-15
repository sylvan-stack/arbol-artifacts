# Arbol: Catalog

## Reference

- [`GLOSSARY.md`](GLOSSARY.md): the canonical terms, one per heading. Copied from the legacy corpus on 2026-10-05. Entries that describe the legacy architecture are history.

## Chapters

### `driver-contract/`: what every Driver does

The contract shared by `arbol-claude-driver` and `arbol-codex-driver`. Start at its [README](driver-contract/README.md), which also defines the conventions all Driver specifications follow.

- [`00-overview-and-boundary.md`](driver-contract/00-overview-and-boundary.md) (DRV-0): what a Driver owns in Arbol 2 and what stays with its caller, vendor families, the Driver as a command-line program and the rules of its command line, rules for every operation.
- [`01-subscriptions.md`](driver-contract/01-subscriptions.md) (DRV-1): the Subscription record and states, sign-in exchange, credential rules, usage reports, model catalogs, the commands and their types.
- [`02-inference.md`](driver-contract/02-inference.md) (DRV-2): the run request, the `run` command and its control input, the event stream and its ordering rules, outcomes, conversation continuity, usage, stopping a run, a run without tools.
- [`03-tools-and-permissions.md`](driver-contract/03-tools-and-permissions.md) (DRV-3): the agent runs as trusted and with the vendor tool's full power: every tool, nothing switched off, no permission questions; the run without tools; the common form of a terminal command; sub-agents; questions from the agent to the person.
- [`04-errors-and-limits.md`](driver-contract/04-errors-and-limits.md) (DRV-4): the error object and its closed list of codes, recognising failures, rate limits, rejected credentials, time limits of a run, limit information during a run.
- [`05-conformance.md`](driver-contract/05-conformance.md) (DRV-5): the shared scenario suite run with a stand-in for each vendor tool, and the rules for probes and live checks.
- [`06-state-and-simultaneous-calls.md`](driver-contract/06-state-and-simultaneous-calls.md) (DRV-6): the files a Driver keeps and their formats, locks, records of runs and sign-ins in progress, reaching a running call, leftovers of a killed call, and when a saved conversation is continued.
- [`python-migration-plan-2026-10-07.md`](driver-contract/python-migration-plan-2026-10-07.md): implementation plan for porting the existing Claude and Codex Drivers to Python, with contract/state compatibility, packaged checks, delivery and rollback gates.

### `builds/`: versions and the build registry

- [`00-builds-and-versions.md`](builds/00-builds-and-versions.md) (BLD-0): how the Builds of every component are numbered, build numbers and package versions, where Builds are kept, which one runs when none is named, and how a Build is named on the command line.

### `architecture/`: how Arbol 2 is divided

The components, what each owns, and how Arbol lives with breaking changes. Start at its [README](architecture/README.md). The inside of a Trunk is not part of it.

- [`00-components-and-boundaries.md`](architecture/00-components-and-boundaries.md) (ARC-0): what `arbol`, `arbol-root`, `arbol-trunk`, the Drivers and `arbol-classifier` own and must never do, the processes and their lifetimes, the Arbol Swift App and the Arbol backend, the command line, small model calls, accounts, Brain Recipes and the resolved route, what any Trunk must offer, who writes which data, the database server.
- [`01-roots.md`](architecture/01-roots.md) (ARC-1): a named Root as a persistent compatibility environment with its own folder, database, settings and compatible Builds; Root identity, manager Builds and invocations; what lies outside every Root; names; Builds and Roots; the tray menu and `arbol-roots`; the current Root; cross-Root discovery and migration.
- [`02-chat-exchange-across-components.md`](architecture/02-chat-exchange-across-components.md) (ARC-2): one message from sending to its final state: the folder of an Exchange, the arriving answer as a file, stop and answers, the end, an Exchange whose process is gone, a database that cannot be reached.
- [`03-stuck-trunks.md`](architecture/03-stuck-trunks.md) (ARC-3): when an Exchange counts as stuck, the heartbeat of a Trunk, a Trunk that ends itself, how Arbol notices from outside, a stop that is not obeyed, ending by force, long waits on purpose.

## Conventions

- Every artifact goes into a chapter folder, never directly into the corpus root. `README.md`, `INDEX.md` and a `GLOSSARY.md` are the exceptions.
- List a chapter here when it is created.
- Tasks are tracked in Linear, not in this corpus: project [Arbol](https://linear.app/sylvan-stack/project/arbol-e2185acd2538) in the Sylvan Stack workspace. Specifications are copied there as documents; `.linear.json` maps each file to its copy. The files here are the originals.
