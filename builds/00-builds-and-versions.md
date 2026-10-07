---
role: authored
spec: BLD-0
status: accepted
---
# Builds · 00 Builds and versions

Every component of Arbol 2 is built into numbered [Builds](../GLOSSARY.md#build). The Builds of a component are kept side by side on the machine and listed in one registry. Whoever starts a component gets its newest working Build, or names another one. This specification states the numbering, the registry, the rule for the default and how a Build is named on the command line. It matters because version 1 could run only what was installed last, named its builds with a timestamp nobody could type, and grew upgrade machinery larger than the product. Here a Build is a folder and a number, and choosing one means reading a few small files.

It follows the conventions of the [Driver Contract](../driver-contract/README.md#conventions).

## Scope

Covered: components and Builds, build numbers and package versions, the registry and its records, when a Build counts as working, the default Build, running a named Build, building, withdrawing and pruning, data shared by several Builds.

Not covered: how each component is compiled, which belongs to its repository; replacing an application or a coordinator while it runs, which belongs to that component; the version of the Driver Contract, which numbers an interface and not a Build ([DRV-0](../driver-contract/00-overview-and-boundary.md#the-command-line)).

## Behaviour

### Components and Builds

A *component* is one repository of Sylvan Stack 2 that builds into a program: `arbol`, `arbol-root`, `arbol-trunk`, `arbol-claude-driver`, `arbol-codex-driver`, `mycel`. A Build is the result of building one component once. The Glossary keeps the word Artifact for documents, so what a build produces is called a Build here, never an artifact.

### Build numbers and package versions

The Builds of a component are counted 1, 2, 3 and so on, and the count is written in hexadecimal: `1` to `9`, then `a` to `f`, then `10`, `11` and onwards. Lower case, no prefix, no leading zero. This count is the *build number*: Build `a3` is the 163rd Build of its component.

Each component counts by itself. A number is given when a build starts and is never given twice: a build that fails keeps its number, and the next build gets the next one. A Build is named by component and build number together, as in `arbol-codex-driver@a3`.

A component also has a *package version*: 2.0.0 for `arbol`, 1.0.0 for the Drivers. It is the number in the repository's package file, and the owner changes it by hand. Many Builds share one package version. The build number alone says which Build runs; the package version is recorded with each Build and shown beside it.

### The registry

The registry is one folder, `~/Library/Application Support/Arbol/builds/`. Inside it every Build has a folder of its own:

```text
builds/
  arbol-codex-driver/
    a2/   build.json   and the files of the Build
    a3/   build.json   and the files of the Build
    a4/   build.json   build.log          (failed: no files to run)
  arbol-claude-driver/
    1f/   …
```

`build.json` is the Build's record: its build number, its package version, its status, when it was built, and from which commit. The registry is nothing more than these records. Listing the Builds reads them, and nothing else has to exist for a Build to run. A record that is damaged or missing takes only its own Build out of use. A pruned record stays with `prunedAt`, and its Build cannot be run. The default is chosen among working Builds whose files are still present.

### Working, failed, withdrawn

| Status | Meaning | Can be run |
|---|---|---|
| `building` | The build has started and not finished | No |
| `failed` | The build did not finish, or one of the component's checks did not pass. The record and the log are kept | No |
| `working` | The build finished and every check passed | Yes |
| `withdrawn` | Was `working` and was later marked as not to be used, with a reason | Only when named |

The checks of a Driver come in two parts, and both must pass. The first needs no network, no account and no quota: its unit tests and the contract suite of [DRV-5](../driver-contract/05-conformance.md). The second is one real message: one prompt, as small as possible, sent through the installed vendor tool on the Driver's test Subscription. It spends a little quota on every build.

A build whose real message could not be sent at all, because there was no network, the test Subscription was signed out or its allowance was used up, is `failed` like any other, and its record names the check that stopped it. The component is built again when the cause is gone; build numbers are not scarce.

A component with no vendor tool behind it has only the first part, until its own specification says otherwise.

A Build that passed its checks and then proves bad in use is withdrawn. Nothing is deleted: the Build can still be run by its build number, to look into what went wrong.

### The default Build

The default Build of a component is the one with the highest build number among those with the status `working`. It is not a setting. It is worked out from the records every time a component is started, so:

- a build that fails changes nothing: the last working Build stays the default;
- a new working Build is the default from the moment its record says `working`;
- withdrawing the newest Build makes the one before it the default again.

### Running a Build

Each component has one small *launcher* on the search path, named after the component. The launcher does one thing: it picks the Build and starts it.

```sh
arbol-codex-driver run --subscription chatgpt "say hi"          # the default Build
arbol-codex-driver -v a3 run --subscription chatgpt "say hi"    # Build a3
```

`-v <build number>` is recognised only as the first argument. Everything after it goes to the Build unchanged, and so do standard input, standard output, signals and the exit status. A caller cannot tell the launcher from the Build it started, except by the time it takes, which must stay too short to notice.

A named Build that is `failed`, still `building`, pruned or unknown is refused, and the refusal lists the Builds that can be run. A named Build that is `withdrawn` runs, with a line on standard error that says so and gives the reason.

The launcher is the only part of a component that is not chosen by build number. It is kept to the behaviour of this section so that it rarely has to change.

### Building, withdrawing, pruning

One tool, `arbol-builds`, writes the registry.

| Command | What it does |
|---|---|
| `arbol-builds build <component>` | Takes the next number, builds the component from its repository into the new folder, runs the checks and writes the record. Ends with status 0 for `working` and 1 for `failed` |
| `arbol-builds list [<component>]` | Prints the records, newest first, and marks the default |
| `arbol-builds show <component>[@<build number>]` | Prints one record; without a build number, the default's |
| `arbol-builds withdraw <component>@<build number> --reason <text>` | Marks a working Build as withdrawn |
| `arbol-builds prune <component> --keep <n>` | Removes the files of all but the newest *n* working Builds. Records stay with `prunedAt`, and the default is never removed. `n` is a positive whole number; withdrawn, failed and building Builds are left alone |

Nothing is pruned unless this command is run. Builds are managed by this tool alone, and it belongs to Arbol: a Driver neither builds, withdraws nor removes a Build, its own included.

### What a repository says about its build

A component's repository holds one file, `arbol-build.json`, at its top. It tells `arbol-builds` everything it needs:

| Entry | Meaning |
|---|---|
| `component` | The component's name |
| `build` | The commands that build it, run in the repository in order. Each finds the folder of the new Build in `ARBOL_BUILD_DIR` and its build number in `ARBOL_BUILD_NUMBER` |
| `entry` | The program to start, as a path inside the Build's folder |
| `checks` | The checks, each a name and a command. A check passes when its command ends with status 0 |
| `contract`, `dataFormat` | For a Driver: the version of the Driver Contract it implements and the format number of its data |

`arbol-builds build` takes the package version from the repository's package file, creates the Build's folder with a record that says `building`, runs the build commands, then the checks, and writes the outcome. Build commands and check commands are strings run with `/bin/sh -c`, in the repository, in order. `entry` is a relative path to an executable file within the Build, with no path outside that folder. A Driver names at least one check of each kind `unit`, `contract` and `live`; the build tool refuses an incomplete description before reserving a number. Other components need at least one check. A check starts the Build's own program, by `entry` in `ARBOL_BUILD_DIR`. It does not go through the launcher, which would refuse a Build that is still `building`.

### How a Build knows its own number

A Build's program reads the record `build.json` in its own folder: the build number and the package version it reports come from there. A program started outside any Build's folder, as in development, reports the build number `0`.

### Where the build tool and the launchers are

`arbol-builds` belongs to the `arbol` repository and is installed from there by that repository's install script. It is not itself a Build: there is one of it, and it is replaced when it is installed again.

A launcher is a small Node.js program without dependencies. `arbol-builds` writes one per component, when the component is first built, into the folder `~/.local/bin`, or into the folder named with `--bin-dir`. The folder has to be on the owner's search path. The repository install command is `npm run install:builds -- --bin-dir <folder>`; it compiles the tool and installs a standalone copy without runtime npm dependencies. On macOS and other POSIX systems the launcher uses Node.js 24's `process.execve` to replace itself with the Build's executable, preserving its process identity, arguments, environment, working folder and open standard streams.

### Data shared by Builds

All Builds of a component work on the same data: for a Driver, its state directory and the homes of its Subscriptions. A component therefore writes a format number into its data. A Build that meets data with a higher number than it knows refuses to run and names both numbers. A Build raises the number only when it changes the data in a way older Builds cannot read; a change older Builds can ignore does not raise it.

Observed in version 1: every build was stamped with branch, commit, build time and source checkout, an older build could be run again, and old builds could be pruned to the newest four. Exactly one version was installed at a time. A Driver build was named like `claude@20260612T135543Z-a1b2c3`. Going back to an earlier build was code-only, and data changes had to stay readable by the older one.

<!-- sources:
arbol:product-spec/11-administration-and-automation.md#Health, build identity and triage
arbol:product-spec/11-administration-and-automation.md#Install and update expectations
arbol:product-spec/12-lessons-and-invariants.md#4. The upgrade machinery became a second product
-->

## Requirements

| ID | The registry, its tool and the launchers must… | Origin | Verified by |
|---|---|---|---|
| BLD-0.1 | number the Builds of each component 1, 2, 3 and so on, written in lower-case hexadecimal without prefix or leading zero | New | `builds.numbering`, `builds.two-builds` |
| BLD-0.2 | give a number when a build starts and never give it twice, also after a failed build and after pruning | New | `builds.concurrent`, `builds.concurrent-mutations`, `builds.failed-check`, `builds.prune`, `builds.interrupted-build` |
| BLD-0.3 | keep each Build in a folder of its own with its record, and need nothing but that folder to run it | Changed | `builds.folder-alone` |
| BLD-0.4 | record for every Build its package version and its source: repository, branch, commit, and whether the checkout held uncommitted changes | Kept | `builds.source` |
| BLD-0.5 | mark a Build `working` only when the build finished and every check the component runs on each build passed, for a Driver the one real message through the installed vendor tool included | New | `builds.description`, `builds.driver-checks` (scripted live outcome); real Driver build checks: SYL-93 and SYL-94 |
| BLD-0.6 | keep the record and the log of a failed build | New | `builds.failed-check`, `builds.failed-command`, `builds.interrupted-build` |
| BLD-0.7 | take as the default the `working` Build with the highest build number, worked out from the records at every start, with no stored setting | Changed | `builds.two-builds`, `builds.withdraw`, `builds.damaged-record` |
| BLD-0.8 | run the named Build when the launcher's first argument is `-v <build number>`, refuse a Build that cannot be run, and list those that can | New | `builds.launch-refusal`, `builds.prune` |
| BLD-0.9 | pass arguments, standard input and output, signals and the exit status through the launcher unchanged | New | `builds.streams`, `builds.signals` |
| BLD-0.10 | let a damaged or missing record take only its own Build out of use | New | `builds.damaged-record` |
| BLD-0.11 | prune only on command, keep every record, and never remove the default Build | Kept | `builds.prune`, `builds.concurrent-prune`, `builds.concurrent-mutations` |
| BLD-0.15 | build a component as its repository's `arbol-build.json` says, hand the build commands and the checks the Build's folder and number in `ARBOL_BUILD_DIR` and `ARBOL_BUILD_NUMBER`, and run the checks against the Build's own program, not through the launcher | New | `builds.description`, `builds.driver-checks`, `builds.invalid-description` |
| BLD-0.16 | write a component's launcher, a Node.js program without dependencies, into `~/.local/bin` or the folder named with `--bin-dir` when the component is first built | New | `builds.paths`, `builds.install` |

Every component must:

| ID | A component must… | Origin | Verified by |
|---|---|---|---|
| BLD-0.12 | report its package version and the build number of the Build that is running, wherever it reports about itself | Kept | Claude Driver: `base.info`, `base.packaged-info`; other components pending |
| BLD-0.13 | write a format number into the data its Builds share, refuse data with a higher number than it knows, and raise the number only for a change older Builds cannot read | Changed | Claude Driver: `base.state-newer`; build tool delegation and declared formats: `builds.shared-data-format`; other components pending |
| BLD-0.14 | read its build number and its package version from the record in its own folder, and report the build number `0` when it runs outside a Build's folder | New | Claude Driver: `base.build-identity`, `base.packaged-info`; other components pending |

## Interface

```ts
interface BuildRecord {                // build.json
  component: string;                   // "arbol-codex-driver"
  build: string;                       // the build number, "a3"
  packageVersion: string;              // from the package file, "1.0.0"
  status: "building" | "failed" | "working" | "withdrawn";
  startedAt: string;                   // ISO 8601, UTC
  finishedAt?: string;
  source: { repository: string; branch: string; commit: string; uncommittedChanges: boolean };
  entry?: string;                      // the program the launcher starts, relative to the Build's folder
  checks: Array<{ name: string; passed: boolean }>;
  contract?: number;                   // a Driver: the version of the Driver Contract it implements
  dataFormat?: number;                 // the format number of the data it reads and writes
  withdrawn?: { at: string; reason: string };
  prunedAt?: string;                   // files removed; the record and log remain
  failure?: { stage: "build" | "entry" | "check" | "launcher"; name: string; message: string };
}
```

The commands of `arbol-builds` are in the table above. Each prints JSON on standard output. `list` prints an array of records with a `default` boolean, grouped by component name and highest build number first within each component; `show`, `build` and `withdraw` print a record; `prune` prints `{ component, pruned: string[] }`. A refused command prints `{ error: { code, message } }` and exits 1. A launcher refusal uses the same envelope and includes an `available` array of runnable build numbers.

The global `--registry-dir <folder>` option selects another registry, and `--bin-dir <folder>` selects the launcher destination. Defaults remain those above. `build` finds the repository at `~/repos/sylvan-stack/<component>`; `--repo <folder>` overrides that location for this build. These options accept both `--name value` and `--name=value`, before or after the command. A launcher remembers the registry selected when it was written.

```ts
interface BuildDescription {           // arbol-build.json
  component: string;
  build: string[];                     // nonempty POSIX shell commands
  entry: string;                       // executable within the Build
  checks: Array<{ name: string; command: string; kind?: "unit" | "contract" | "live" }>;
  contract?: number;                   // required positive whole number for a Driver
  dataFormat?: number;                 // required positive whole number for a Driver
}
```

Reserving a number uses an atomic creation of its directory; all numbered directories count, including damaged records. Metadata updates use atomic replacement of `build.json`. Record changes, withdrawal and pruning are serialised per component, so a simultaneous withdrawal cannot make a Build the default while pruning removes its files. Short-lived process reservations in `.writers/` protect these changes; dead processes are ignored, and listing or running never needs those reservations. Build commands and checks run outside the reservation. A build stopped by the caller is failed and keeps its log. After an uncatchable kill its unfinished record stays `building`, cannot run, and still consumes its number. BLD-0.13 belongs to each component: the build tool records its declared `dataFormat` and never changes shared component data.

## Known problems in version 1

Not to be reproduced.

- **One version at a time.** Trying an older or a newer build meant installing it over the current one.
- **Upgrade machinery larger than the product.** A controller took a census of processes, pinned executables by content hash and journalled every step. When its own records were lost, nothing could be rebuilt or restarted for two days.
- **Names nobody could type.** A build was identified by a timestamp and a hash.
- **Slow starts.** A packaged one-shot command spent about 4.5 seconds before doing any work. A launcher in front of every call must not add to that.

<!-- sources:
arbol:product-spec/12-lessons-and-invariants.md#4. The upgrade machinery became a second product
arbol:product-spec/12-lessons-and-invariants.md#6. Many resident services with strict, version-coupled contracts
arbol:product-spec/12-lessons-and-invariants.md#Anti-goals
-->

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| BLD-D1 | How are versions numbered? | A count per component, starting at 1, written in hexadecimal | Decided 6 October 2026 by the owner |
| BLD-D2 | Which version runs when none is named? | The last working one that was built successfully | Decided 6 October 2026 by the owner |
| BLD-D3 | How is a version named on the command line? | `-v <version>` as the first argument, as in `arbol-codex-driver -v a3 …` | Decided 6 October 2026 by the owner |
| BLD-D4 | What makes a Build working? | The build finished and the component's own automatic checks passed. Checks that spend quota are not among them. A Build that fails later in use is withdrawn by hand | Decided 6 October 2026 by the owner: the automatic checks and, on top of them, one real message through the real tool on every build (SYL-31) |
| BLD-D5 | Where is the registry? | `~/Library/Application Support/Arbol/builds/` | Decided 6 October 2026 by the owner: the proposed default (SYL-32) |
| BLD-D6 | What becomes of the version numbers in `package.json` and in the repositories' README files (2.0.0, 1.0.0)? | `package.json` keeps a number because npm needs one, and it means nothing. The registry's number is the component's version. The README files are corrected when the first Builds exist | Decided 6 October 2026 by the owner, against the proposed default: both numbers stay. 2.0.0 and 1.0.0 are package versions, and the hexadecimal count is the build number (SYL-33) |
| BLD-D7 | How many Builds are kept? | All, until `prune` is run. Suggested habit: the newest four working ones, as in version 1 | Decided 6 October 2026 by the owner: managing Builds, pruning included, is Arbol's work and never a Driver's. With that the proposed default stands (SYL-51) |
| BLD-D8 | Is a version named the same way for a component that stays running, such as the application? | Yes, `-v` starts that Build. Only one Build of such a component runs at a time, and replacing it while it runs is specified with that component | Decided 6 October 2026 by the owner: `-v` means the same for every component. It runs exactly that Build, and without it the newest working one runs. Any number of invocations can run at once, of one Build or of several. Whether a component that stays running can run twice at the same time is left to that component's own specification and is not settled here (SYL-52) |
| BLD-D10 | How are unspecified command, pruning and launcher details represented? | POSIX shell command strings, optional check kinds with all three required for Drivers, executable relative entries, explicit path overrides, a `prunedAt` field, atomic directory reservation and record replacement, and `process.execve` launchers. Shared data formats remain each component's responsibility | Decided 7 October 2026 during SYL-76, a technical choice; the Interface and Behaviour sections give the details |
| BLD-D9 | Where are the build tool and the launchers, and how does a repository describe its build? | `arbol-builds` is part of the `arbol` repository and is not a Build itself. Launchers go to `~/.local/bin`, where the vendor tools already are on this machine. A repository describes its build in one file, `arbol-build.json` | Decided 6 October 2026, a technical choice made in drafting on the owner's go-ahead |
