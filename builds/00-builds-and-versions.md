---
role: authored
spec: BLD-0
status: accepted
---
# Builds · 00 Builds and versions

Every component of Arbol 2 is built into numbered [Builds](../GLOSSARY.md#build). The Builds of a component are kept side by side on the machine and listed in one registry. Whoever starts a component gets its newest eligible working Build, or names another one; for `arbol` and `arbol-root`, eligibility is restricted to the selected [Root](../architecture/01-roots.md). This specification states the numbering, the registry, the rule for the default and how a Build or a Root is named on the command line. It matters because version 1 could run only what was installed last, named its builds with a timestamp nobody could type, and grew upgrade machinery larger than the product. Here a Build is a folder and a number, and choosing one means reading a few small files.

It follows the conventions of the [Driver Contract](../driver-contract/README.md#conventions).

## Scope

Covered: components and Builds, build numbers and package versions, the registry and its records, when a Build counts as working, the default Build, running a named Build, Root associations and Trunk compatibility, building, withdrawing and pruning, data shared by several Builds.

Not covered: how each component is compiled, which belongs to its repository; replacing an application or a coordinator while it runs, which belongs to that component; creating, migrating and removing Roots ([ARC-1](../architecture/01-roots.md)); the versions of the Driver Contract and the [Root Contract](../../arbol-root/contract/README.md), which number interfaces and not Builds ([DRV-0](../driver-contract/00-overview-and-boundary.md#the-command-line), [RCT-0](../../arbol-root/contract/00-overview.md#versions-what-fits-together)).

## Behaviour

### Components and Builds

A *component* is one repository of Sylvan Stack 2 that builds into a program, or a folder `trunks/<code name>/` inside the repository `arbol-trunk`: `arbol-app`, `arbol`, `arbol-root`, `arbol-trunk/trivial`, `arbol-claude-driver`, `arbol-codex-driver`, `arbol-classifier`, `mycel`. A Build is the result of building one component once. The Glossary keeps the word Artifact for documents, so what a build produces is called a Build here, never an artifact.

A **Root** is a named, persistent environment: its folder, database, settings and compatible Builds. A **Root Build** is a numbered Build of `arbol-root`, the manager of that environment and all Trunks compatible with it. A Root outlives every invocation of its manager; an invocation is a short command. The Builds of `arbol` and `arbol-root` each name the Root they were made for. The Arbol Swift App, Drivers, Trunk Builds, registry and launchers lie outside every Root. The global `arbol-roots` command manages the catalogue, creation, readiness, failure, minimum App Build, migration and removal of Roots ([ARC-1](../architecture/01-roots.md)); `arbol-builds` manages Builds.

Each distinct Trunk implementation is a component of its own, `arbol-trunk/<code name>`, with its own build-number count. The first is `arbol-trunk/trivial`, the Trivial Trunk (RCT-0). A Trunk's record is recognised by `rootContracts`; Drivers declare the Driver Contract and have no `rootContracts`.

### Build numbers and package versions

The Builds of a component are counted 1, 2, 3 and so on, and the count is written in hexadecimal: `1` to `9`, then `a` to `f`, then `10`, `11` and onwards. Lower case, no prefix, no leading zero. This count is the *build number*: Build `a3` is the 163rd Build of its component.

Each component counts by itself, across all Roots: a Root does not start a new count. A number is given when a build starts and is never given twice: a build that fails keeps its number, and the next build gets the next one. A Build is named by component and build number together, as in `arbol-codex-driver@a3`, and `arbol-trunk/trivial@4` for a Trunk.

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

A Trunk's Builds lie in `builds/arbol-trunk/<code name>/<build>/`: `builds/arbol-trunk/` is a folder of Trunks, not a component.

`build.json` is the Build's record: its build number, its package version, its status, when it was built, and from which commit. For `arbol` and `arbol-root` it also names the Root; for a Trunk it lists the Root Contract versions it implements. The registry is nothing more than these records. Listing the Builds reads them; the registry needs no running service or source checkout. A record that is damaged or missing takes only its own Build out of use. A pruned record stays with `prunedAt`, and its Build cannot be run. The default is chosen among eligible working Builds whose files are still present. A Build's own Root and shared-data requirements still apply when it runs.

### Working, failed, withdrawn

| Status | Meaning | Can be run |
|---|---|---|
| `building` | The build has started and not finished | No |
| `failed` | The build did not finish, or one of the component's checks did not pass. The record and the log are kept | Only when named, and only when its program is there |
| `working` | The build finished and every check passed | Yes |
| `withdrawn` | Was `working` and was later marked as not to be used, with a reason | Only when named |

The checks of a Driver come in two parts, and both must pass. The first needs no network, no account and no quota: its unit tests and the contract suite of [DRV-5](../driver-contract/05-conformance.md). The second is one real message: one prompt, as small as possible, sent through the installed vendor tool on the Driver's test Subscription. It spends a little quota on every build.

A build whose real message could not be sent at all, because there was no network, the test Subscription was signed out or its allowance was used up, is `failed` like any other, and its record names the check that stopped it. The component is built again when the cause is gone; build numbers are not scarce.

A component with no vendor tool behind it has only the first part, until its own specification says otherwise.

A Build that passed its checks and then proves bad in use is withdrawn. Nothing is deleted: the Build can still be run by its build number, to look into what went wrong.

### The default Build

For a component whose Builds belong to no Root, the default Build is the one with the highest build number among those with the status `working`. It is not a setting. It is worked out from the records every time a component is started, so:

- a build that fails changes nothing: the last working Build stays the default;
- a new working Build is the default from the moment its record says `working`;
- withdrawing the newest Build makes the one before it the default again.

For `arbol` and `arbol-root`, the default is the working Build with the highest build number among those made for the named Root. When no Root is named, it is the newest working Build of the current Root, which ARC-1 defines as the Root created last among those in the state `working`. A Build for another Root is never a fallback. If the selected Root has no runnable working Build, the command is refused and names the component and Root that need one. A failed or preparing Root is never selected as current, but may be named explicitly under ARC-1.

Trunk Builds belong to no Root and are numbered independently per implementation. For a new Exchange the caller names a Trunk by its code name, or gets the Trivial Trunk, the default Trunk of every Root. The launcher `arbol-trunk` then chooses the newest working Build of that Trunk whose `rootContracts` hold the Root's `rootContract`; an explicitly named Build must also fit (RCT-0.7). Build numbers of different Trunk implementations are never compared to choose an implementation. If the selected Trunk has no runnable working Build that fits, the launcher refuses the call with `no_fit` (RCT-0.9). `arbol-trunk list`, which `arbol-root trunks` prints, lists the Trunks and their Builds. Roots that use the same Root Contract version share every Trunk Build that fits one of them, so one Trunk Build can serve both without being rebuilt. Compatibility comes from records, not from the Trunk's build number ([ARC-0](../architecture/00-components-and-boundaries.md#arbol-root), [ARC-1](../architecture/01-roots.md#builds-and-roots)).

<!-- sources:
arbol:src/arbol_builds/root_launcher.py#select_root_build
arbol:src/arbol_builds/root_launcher.py#root_default_record
arbol:src/arbol_builds/service.py#list_builds
arbol:src/arbol_builds/service.py#show_build
arbol:tests/test_builds.py#RootComponents
-->

### Running a Build

Each component has one small *launcher* on the search path, named after the component, except the Trunks, which share the launcher `arbol-trunk` (RCT-0). The launcher does one thing: it picks the Build and starts it.

```sh
arbol-codex-driver run --subscription chatgpt "say hi"          # the default Build
arbol-codex-driver -v a3 run --subscription chatgpt "say hi"    # Build a3
```

For a component outside Roots, except the Trunks (below), `-v <build number>` is recognised only as the first argument. Everything after the selection prefix goes to the Build unchanged, and so do standard input, standard output, signals and the exit status. A caller cannot tell the launcher from the Build it started, except by the time it takes, which must stay too short to notice. The Python launcher ([BLD-D15](#decisions)) differs from a direct start in a few small ways it cannot avoid: a caller's choice to ignore the signals SIGPIPE or SIGXFSZ is not passed on, because Python changes both when it starts and the launcher sets them back to their default; when `LC_ALL` is not set and the caller's character type comes out as `C` (`LC_CTYPE=C` or `LANG=C`, or no locale variable at all), the Build sees `LC_CTYPE=C.UTF-8` instead; and macOS adds `__CF_USER_TEXT_ENCODING` to the environment when the caller did not set it. A Ctrl-C that arrives while Python itself is starting still ends the launcher by SIGINT before the Build starts, but can first print `KeyboardInterrupt` on standard error, and in rare cases Python stops with status 1 instead. A standard input, output or error that the caller closed reaches the Build as `/dev/null`, as with the earlier Node.js launcher. Unlike that launcher, the Python launcher does not raise the limit of open files: the Build gets the caller's limit, as on a direct start.

The launchers of `arbol` and `arbol-root` additionally recognise `--root <identifier>` before `-v`. Their selection prefix is `[--root <identifier>] [-v <build number>]`; all later arguments are passed unchanged. With `--root` alone they start that Root's default Build. With neither option they start the current Root's default Build. A Build named by `-v` supplies its own Root from its record and needs no `--root`; if both are supplied and disagree, the launcher refuses the call. The Driver and `arbol-app` launchers keep the existing `-v` form and accept no Root selector. The launcher `arbol-trunk` takes `[--root <identifier>] [<code name>] [-v <build number>]` before the command, hands the Build `--root <root>` before it, refuses with `unknown_root`, `unknown_trunk` and `no_fit`, and answers `list` itself (RCT-0.7 to RCT-0.10).

For the Root-component launchers, the selectors are only the ordered prefix
`[--root <identifier>] [-v <build>]`. An empty command after that prefix is
passed to the Build too. The Root record is read on every start with the same
reader and current-Root choice as `arbol-trunk`. An explicitly selected Root
may be preparing or failed; an implicit current Root must be working. A named
Build supplies its own Root, whose record must still be readable; it never
uses the current Root instead. The launcher adds no `--root` argument to the
Build: the Build reads its Root from its own record (BLD-D21).

| Root-component refusal | When |
|---|---|
| `unknown_root` | A Root selector has no valid identifier, the selected Root has no readable valid record, or no Root/Build was named and no working Root exists |
| `build_unavailable` | The named Build cannot run, or the selected Root has no runnable working Build; the message names the component and Root when known |
| `invalid_input` | A Root selector contradicts the Root of the named Build |

These refusals keep the component launcher's form: exit 1 and one
`{ "error": { "code", "message", "available" } }` line. `available` lists only
runnable Builds of the selected Root when it is known, newest first, and is
empty when no Root can be selected. Named failed and withdrawn Builds keep
the existing warning and runnable rules. Root-specific selection filters the
records before the existing global default chooser; plain component and
Trunk launcher text and selection stay unchanged.

`arbol-builds list --root <identifier>` chooses defaults for that Root in the
Root components and keeps global defaults for other components. With no
selector and no current Root, inventory still succeeds: Root components have
no default, while other components retain theirs. A named Root selector must
resolve to a valid record. `show` of a Root component without a Build number
requires a selected/current Root and returns its default; named `show` keeps
record introspection even after that Root's record is gone, and only checks
that an explicit Root selector agrees with the Build's stored Root. An
explicit non-Root component's `list` or `show` refuses `--root` as inapplicable.
Tool refusals keep their existing `builds_failed` wrapper and explain the
selection problem (BLD-D21).

How `arbol-trunk` reads a call and the Roots ([BLD-D17](#decisions)). `--root` counts only as the first argument. The next argument is the code name, unless it is `-v`, a command word of the Root Contract (`run`, `settle`, `list`) or begins with `-`. A Root's record is `root.json` in its folder `~/Library/Application Support/Arbol/roots/<root>/`, reached from the home folder and read at every start, as the Build records are; a record that is missing or damaged takes only its own Root out of use. Without `--root` the launcher reads the record of every Root and takes the current Root, the one created last among those in the state `working` (ARC-1). Except `list`, which it answers itself, every command, `run` and `settle` and any that a later version of the Root Contract adds, goes to the Build with everything after it, and the Build refuses what it does not know. It checks the call, then the Root, then the Trunk, then the Build, and refuses:

| Code | When |
|---|---|
| `invalid_input` | The call has no command, or `list` comes after `-v` or has more arguments after it |
| `unknown_root` | `--root` has no value, or one that is not one lower-case word of letters and digits; the Root named has no readable record; no Root is named and none is `working`. The message says which |
| `unknown_trunk` | The code name is not one, or `builds/arbol-trunk/` has no folder of that name |
| `no_fit` | The named Build is unknown, still `building`, pruned, `failed` without its program, or does not fit the Root; or, with no Build named, no working Build of the Trunk fits it |

A refusal is one line `{ "error": { "code", "message" }, "available": [...] }` with exit status 1. `available` stands beside `error`, as RCT-0 gives it, where the launcher of a component puts it inside `error`. In a refusal `no_fit` it lists the runnable Builds of the Trunk that fit the Root, newest first, and in the others it is empty.

```sh
arbol --root sapling send …                  # First Sapling's default arbol Build
arbol-root --root sapling list               # First Sapling's default Root Build
arbol-root -v a3 list                       # Build a3, in the Root its record names
arbol-root --root sapling -v a3 list          # only if Build a3 belongs to First Sapling
```

A named Build that is still `building`, pruned or unknown, or `failed` without its program, is refused, and the refusal lists the Builds that can be run. A named Build that is `withdrawn` runs, with a line on standard error that says so and gives the reason. A named Build that is `failed` and has its program runs too, with a line on standard error that says so and names the step that failed ([BLD-D13](#decisions)). For example, `arbol-classifier -v 3 add-key` runs Build 3 before any Build of the classifier has passed its real question to Jev.

The launcher is the only part of a component that is not chosen by build number. It is kept to the behaviour of this section so that it rarely has to change.

<!-- sources:
arbol:src/arbol_builds/root_launcher.py#read_root_call
arbol:src/arbol_builds/root_launcher.py#launch_root
arbol:scripts/install_builds.py#served
arbol:tests/launcher_benchmark.py
-->

### Building, withdrawing, pruning

One tool, `arbol-builds`, writes the registry.

| Command | What it does |
|---|---|
| `arbol-builds build <component> [--root <identifier>]` | Takes the next number, builds the component from its repository into the new folder, runs the checks and writes the record, including its Root or its declared Root Contract versions. For `arbol` and `arbol-root`, `--root` names the Root the Build is made for; it is written as `root` into the record when the build starts, and the build is refused without it ([RTM-D9](../../arbol-root/specs/01-builds-layouts-and-migration.md#decisions)). For any other component the build is refused with it. Ends with status 0 for `working` and 1 for `failed` |
| `arbol-builds list [<component>] [--root <identifier>]` | Prints the records, newest first, and marks the default for the named Root, or the current Root when none is named; components outside Roots keep their global default |
| `arbol-builds show <component>[@<build number>] [--root <identifier>]` | Prints one record; without a build number, the selected Root's default for `arbol` or `arbol-root`, and the global default for other components. A named Build supplies its own Root |
| `arbol-builds withdraw <component>@<build number> --reason <text>` | Marks a working Build as withdrawn |
| `arbol-builds prune <component> --keep <n>` | Removes the files of all but the newest *n* working Builds, the newest working Build of each retained Root, and for a Trunk the newest working Build that fits each Root Contract version a retained Root uses. Records stay with `prunedAt`, and neither the default nor a Locked Build is removed. `n` is a positive whole number; withdrawn, failed and building Builds are left alone |
| `arbol-builds prune --unused` | Removes the files of every Build, of any component, that was not started for longer than the time in `~/.arbol/arbol-builds.json`. With no time there it removes nothing ([Unused Builds and Locked Builds](#unused-builds-and-locked-builds)) |
| `arbol-builds lock <component>@<build number>`, `arbol-builds unlock <component>@<build number>` | Marks a Build Locked, or takes the mark away |

Nothing is pruned unless one of these commands is run. Arbol runs `prune --unused` when it starts and once a day while it runs; while no time is set, that removes nothing. Builds are managed by this tool alone, and it belongs to Arbol: a Driver neither builds, withdraws nor removes a Build, its own included.

The protection for retained Roots applies to `arbol` and `arbol-root`, even when a retained Root is `preparing` or `failed`; it may keep more than *n* Builds. It does not create a per-Root count for Trunks or Drivers: a Trunk is kept by Root Contract version, as above, and the Driver Build that an older Root needs is kept by locking it. The build tool and launchers may read Root identities, states and compatibility records, but hold no backend, UI code, migration script or table layout of a Root. `arbol-roots` owns Root catalogue changes.

For count-based pruning, a retained Root is a folder with a valid Root
identifier that still has a `root.json` directory entry, in any state. A
missing record protects nothing. A damaged, unreadable, dangling or
nonregular record still protects that folder identifier's newest runnable
working Build of `arbol` or `arbol-root`: unreadable content does not make
the Root cease to exist. The identifier comes from the folder, so a damaged
record cannot protect some other identifier instead (BLD-D22).

For a Trunk, every retained Root must have a readable valid record before
anything is removed, because an unknown `rootContract` could need any old
Build. One unresolved record therefore refuses the whole component's prune,
names the affected Root identifiers and changes no Build record or file.
An absent Roots catalogue means no retained Roots; another error listing it
refuses Root-component and Trunk pruning before any change. Components
outside Roots do not read that catalogue at all.

The existing newest-*n*, Locked and global-default protections remain; the
Root and version protections are additional. For each retained identifier or
version the tool protects the newest **runnable working** Build, as the
launchers do. A higher working record whose executable has disappeared does
not replace protection of the older runnable one. A single Trunk Build can
protect several versions; Build numbers from different components are never
compared. Failed, withdrawn, building and already pruned records keep their
existing treatment. Retained records, logs and `last-start` files are kept
when payloads are pruned.

The tool reads one catalogue snapshot inside the component's existing
mutation reservation, before marking or removing anything. It reads the
catalogue anew on the next prune. It holds no catalogue lock and changes no
Root record; a Root catalogue change after that snapshot belongs to the next
prune's view. Nonregular records are not opened as blocking streams. These
pruning-only reads do not change the embedded launcher readers or their
selection rules (BLD-D22).

### Unused Builds and Locked Builds

The owner decides how long an unused Build is kept, and can keep any Build for good ([BLD-D12](#decisions)).

| Rule | Detail |
|---|---|
| The last start is recorded | A launcher writes the time of each start into the file `last-start` in the Build's folder. A start never waits for this and never fails because of it. A Build that was never started counts from the end of its build |
| A time the owner sets | `removeUnusedAfterDays` in `~/.arbol/arbol-builds.json`. `arbol-builds prune --unused` removes the files of the Builds that were not started for longer. While no time is set, no Build is removed for being unused; that is the default |
| Locked | A Build marked with `arbol-builds lock` is never removed, neither by `prune --keep` nor by `prune --unused`, until it is unlocked |
| Never removed for being unused | A Locked Build; the default Build of a component, and for `arbol` and `arbol-root` the default of every retained Root; a Trunk Build that a retained Root would run; a Build that an Exchange in progress runs on, as the managers of the Roots list them ([ARC-0](../architecture/00-components-and-boundaries.md#arbol-root)) |
| The record stays | As with `prune --keep`, the record, the log and `last-start` remain, with `prunedAt` |
| When it runs | Arbol runs `arbol-builds prune --unused` when it starts and once a day while it runs |

`lock <component>@<build>` and `unlock <component>@<build>` each print the
stored Build record. They accept every known, unpruned Build, whether it is
`building`, `failed`, `working` or `withdrawn`. Both refuse an unknown or
already pruned Build. The first lock records the current UTC millisecond time
as `lockedAt`; locking it again succeeds and keeps that original time. Unlocking
removes `lockedAt`; unlocking an already unlocked Build succeeds unchanged.
A `lockedAt` that is not a valid record timestamp makes the record damaged.
`list` and `show` include the mark unchanged.

These commands use the same per-component reservation as record changes and
pruning. Each later write by an in-flight Build reads the current lock mark,
or its absence, under that reservation, so finishing a build cannot undo a
concurrent lock or unlock. `prune --keep` keeps the newest requested working
Builds as before and every Locked Build as well, without counting an older
Locked Build against that requested count. A lock that wins the reservation
first keeps its files; a prune that wins first removes them and makes the
subsequent lock fail (BLD-D20).

The file `last-start` holds one UTC timestamp and a newline, in the same
millisecond form as a Build record, for example `2026-10-26T10:00:00.123Z`.
A component launcher and `arbol-trunk` record it immediately before handing
over to the selected Build, including a failed or withdrawn Build named with
`-v`. A refused selection and `arbol-trunk list` record nothing. The launcher
writes a private temporary file beside it and replaces `last-start` atomically.
It takes no lock, retries nothing and requests no disk flush. Every recording
error is ignored; a failed write leaves the previous timestamp intact, and
the launcher removes its temporary file when it can. The launcher restores
SIGXFSZ to its normal launch behaviour only after this attempt, so a file-size
limit does not kill it while recording (BLD-D19).

`arbol-builds list` and `show` add two derived fields; neither is saved in
`build.json`. `lastStart` is the recorded timestamp, or `null` when none can
be recovered. If a regular `last-start` file is damaged or cannot be read,
its modification time is used; a non-regular file is ignored, and unreadable
metadata does not fail the command. `unusedSince` is `lastStart` when present,
otherwise the build's `finishedAt`, or `startedAt` while the build is unfinished.
A missing timestamp means no start was recorded: older Builds may have run
before recording was installed. Both fields remain available after pruning,
because `last-start` is retained with the record and log.

<!-- sources:
arbol:src/arbol_builds/launcher.py#record_start
arbol:src/arbol_builds/launcher.py#launch
arbol:src/arbol_builds/trunk_launcher.py#launch_trunk
arbol:src/arbol_builds/service.py#last_start
arbol:src/arbol_builds/service.py#build_details
arbol:src/arbol_builds/service.py#list_builds
arbol:src/arbol_builds/service.py#prune_builds
arbol:src/arbol_builds/cli.py#main
arbol:tests/test_builds.py#StartRecords
arbol:tests/test_builds.py#Install
arbol:src/arbol_builds/service.py#lock_build
arbol:src/arbol_builds/service.py#save_record
arbol:src/arbol_builds/launcher.py#valid_record
arbol:tests/test_builds.py#Locking
-->

Seqoya Lab, the administration UI, has a page *Builds*. It lists the Builds of each component with their last start, has a Locked switch for each Build and one field for the time; an empty field means that no Build is removed for being unused. The page calls `arbol-builds` and writes the setting, and removes nothing itself. Until Seqoya Lab exists, the same is done with `arbol-builds lock`, `arbol-builds unlock` and the settings file.

### What a repository says about its build

A component's repository holds one file, `arbol-build.json`, at its top. It tells `arbol-builds` everything it needs:

| Entry | Meaning |
|---|---|
| `component` | The component's name |
| `build` | The commands that build it, run in the repository in order. Each finds the folder of the new Build in `ARBOL_BUILD_DIR` and its build number in `ARBOL_BUILD_NUMBER` |
| `entry` | The program to start, as a path inside the Build's folder |
| `checks` | The checks, each a name and a command. A check passes when its command ends with status 0 |
| `contract`, `dataFormat` | For a Driver: the version of the Driver Contract it implements and the format number of its data |
| `rootContracts` | For a Trunk: the versions of the Root Contract it implements, such as `[1]`. Required |

`arbol-builds build` takes the package version from the repository's package file, creates the Build's folder with a record that says `building` and, for `arbol` and `arbol-root`, the Root named with `--root`, runs the build commands, then the checks, and writes the outcome. Build commands and check commands are strings run with `/bin/sh -c`, in the repository, in order. They get the caller's environment with `ARBOL_BUILD_DIR` and `ARBOL_BUILD_NUMBER` added; when `LC_ALL` is not set and the caller's character type comes out as `C`, Python, which runs `arbol-builds`, also makes it `LC_CTYPE=C.UTF-8` ([BLD-D15](#decisions)). `entry` is a relative path to an executable file within the Build, with no path outside that folder. A Driver names at least one check of each kind `unit`, `contract` and `live`; the build tool refuses an incomplete description before reserving a number. Other components need at least one check. A Trunk names `rootContracts` and no `contract`, and no other component names `rootContracts`; the tool refuses any other description before reserving a number too ([BLD-D16](#decisions)). A check starts the Build's own program, by `entry` in `ARBOL_BUILD_DIR`. It does not go through the launcher, which would refuse a Build that is still `building`.

### Python Driver delivery

From SYL-95, each Python Driver artifact contains its own pinned standalone CPython 3.14 distribution, runtime modules, fixtures and packaged `unittest` checks. Its executable directly execs that interpreter, preserving process identity, arguments, standard streams and working directory. The artifact records interpreter patch, distribution, architecture and archive SHA-256; it is verified after relocation to its final folder. Normal invocation needs no source checkout, virtual environment, uv, download or installation. uv is used only to prepare development and build tooling. Minimal `package.json` version metadata remains, because the build tool reads the version from it, and packaging verifies agreement with `pyproject.toml`. Driver package/check scripts are Python; since 14 October 2026 the shared build tool and launchers are typed Python too ([BLD-D15](#decisions)). Both Drivers' working numbered Builds require packaged unit tests, all 38 scenarios and exactly one designated test-account message. Codex Build 1 completed these checks in SYL-94; its earlier development candidate remains historical evidence. Withdrawal/rollback is rehearsed in an isolated registry before production cutover.

### How a Build knows its own number

A Build's program reads the record `build.json` in its own folder: the build number and the package version it reports come from there. A program started outside any Build's folder, as in development, reports the build number `0`.

### Where the build tool and the launchers are

`arbol-builds` belongs to the `arbol` repository and is installed from there by that repository's install script, run in `~/repos/sylvan-stack/readonly/arbol`, the clone of the last merged `main` ([BLD-D18](#decisions)). It is not itself a Build: there is one of it, and it is replaced when it is installed again.

`arbol-builds` and its launchers are typed Python that uses only the standard library ([BLD-D15](#decisions)). The install command, run in the repository, is `uv run --no-sync python scripts/install_builds.py [--bin-dir <folder>]`. It puts the tool into the folder `.arbol-builds` inside the given folder, `~/.local/bin` by default, together with the same pinned standalone CPython that every Build carries, checked by its SHA-256, and writes the program `arbol-builds` beside it. The tool and every launcher name that interpreter by its absolute path in their first line, which cannot hold a space or a `#` and must stay short, so the install refuses such a folder before it changes anything. Installing again replaces the tool and rewrites every launcher already in that folder with the current launcher code, keeping the component and the registry each one serves, launchers written by the earlier Node.js tool included ([BLD-D14](#decisions)). A Node.js launcher that is starting at the very moment it is rewritten can fail once with a Node.js error, so the first Python install is run while no component is starting.

A launcher is a small Python program without dependencies, started by the interpreter of the `arbol-builds` that wrote it. The installed tool names its pinned interpreter; `bin/arbol-builds`, which runs the tool from the checkout, names the checkout's development Python until the next install rewrites the launcher. `arbol-builds` writes one per component, when the component is first built, into the folder `~/.local/bin`, or into the folder named with `--bin-dir`; for a Trunk it writes the launcher `arbol-trunk`, which every Trunk shares (RCT-0), when a Trunk is first built, and installing `arbol-builds` again rewrites it as every launcher. The folder has to be on the owner's search path. The launcher uses `os.execv` to replace itself with the Build's executable, preserving its process identity, its arguments and environment byte for byte, its working folder and its open standard streams.

### Data shared by Builds

All Builds of a Driver work on the same state directory and the homes of its Subscriptions, shared by every Root. A Driver writes a format number into its data. A Build that meets data with a higher number than it knows refuses to run and names both numbers. A Build raises the number only when it changes the data in a way older Builds cannot read; a change older Builds can ignore does not raise it. This accepted Driver rule is unchanged.

Builds of `arbol` and `arbol-root` share data only within the Root their records name: its database, folder and settings. A breaking change creates a new Root beside the old one, with migration governed by ARC-1; it never changes another Root's data in place. Trunk Builds operate on a Root whose Root Contract version they list. The Arbol Swift App is shared and discovers the retained Roots on each start; each Root records its minimum App Build. Changing a default Build or Root changes the choice for the next invocation, and never moves an Exchange already accepted: its record retains its `root` and Trunk Build.

Observed in version 1: every build was stamped with branch, commit, build time and source checkout, an older build could be run again, and old builds could be pruned to the newest four. Exactly one version was installed at a time. A Driver build was named like `claude@20260612T135543Z-a1b2c3`. Going back to an earlier build was code-only, and data changes had to stay readable by the older one.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/11-administration-and-automation.md#Health, build identity and triage`
- `arbol_deprecated_v1:product-spec/11-administration-and-automation.md#Install and update expectations`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#4. The upgrade machinery became a second product`

## Requirements

The existing check names below verify the Driver and shared build-tool behaviour recorded on 5–8 October 2026. Root-specific selection, metadata and pruning are accepted extensions from [ARC-D47](../architecture/01-roots.md#decisions), recorded on 12 October 2026. Those extensions have separate checks, rather than relying on the earlier Driver checks. Since SYL-155, on 16 October 2026, BLD-0.17 and 0.21 to 0.23 are implemented and their checks are named; since SYL-179, the same day, the launcher `arbol-trunk` is, and its checks are named under BLD-0.9, 0.16 and 0.22; since SYL-158, on 26 October 2026, Root-component default selection and selectors are implemented under BLD-0.18 and 0.19, with inventory that agrees. The remaining extension checks are pending.

| ID | The registry, its tool and the launchers must… | Origin | Verified by |
|---|---|---|---|
| BLD-0.1 | number the Builds of each component 1, 2, 3 and so on, written in lower-case hexadecimal without prefix or leading zero | New | SYL-95 Python: `build.relocated-unit`, `build.folder-alone`, `build.launcher-default-and-named`, `build.failed-check-preserves-default`, `build.withdrawal-rollback`; production `build.unit`, `build.contract`, `dev.build-check` and launcher records; Codex was a candidate at SYL-95; current numbered verification is below; prior verification: `builds.numbering`, `builds.two-builds`; Codex SYL-94 Build 1: `build.clean-working`, `build.failed-check-preserves-default` |
| BLD-0.2 | give a number when a build starts and never give it twice, also after a failed build and after pruning | New | SYL-95 Python: `build.relocated-unit`, `build.folder-alone`, `build.launcher-default-and-named`, `build.failed-check-preserves-default`, `build.withdrawal-rollback`; production `build.unit`, `build.contract`, `dev.build-check` and launcher records; Codex was a candidate at SYL-95; current numbered verification is below; prior verification: `builds.concurrent`, `builds.concurrent-mutations`, `builds.failed-check`, `builds.prune`, `builds.interrupted-build`; Codex SYL-94 Build 1: `build.failed-check-preserves-default` |
| BLD-0.3 | keep each Build in a folder of its own with its record, and need nothing but that folder to run it | Changed | SYL-95 Python: `build.relocated-unit`, `build.folder-alone`, `build.launcher-default-and-named`, `build.failed-check-preserves-default`, `build.withdrawal-rollback`; production `build.unit`, `build.contract`, `dev.build-check` and launcher records; Codex was a candidate at SYL-95; current numbered verification is below; prior verification: `builds.folder-alone`; Codex SYL-94 Build 1: `build.folder-alone`, `build.source-and-runtime` |
| BLD-0.4 | record for every Build its package version and its source: repository, branch, commit, and whether the checkout held uncommitted changes | Kept | SYL-95 Python: `build.relocated-unit`, `build.folder-alone`, `build.launcher-default-and-named`, `build.failed-check-preserves-default`, `build.withdrawal-rollback`; production `build.unit`, `build.contract`, `dev.build-check` and launcher records; Codex was a candidate at SYL-95; current numbered verification is below; prior verification: `builds.source`; Codex SYL-94 Build 1: `build.clean-working`, `build.source-and-runtime` |
| BLD-0.5 | mark a Build `working` only when the build finished and every check the component runs on each build passed, for a Driver the one real message through the installed vendor tool included | New | SYL-95 Python: `build.relocated-unit`, `build.folder-alone`, `build.launcher-default-and-named`, `build.failed-check-preserves-default`, `build.withdrawal-rollback`; production `build.unit`, `build.contract`, `dev.build-check` and launcher records; Codex was a candidate at SYL-95; current numbered verification is below; prior verification: `builds.description`, `builds.driver-checks` (scripted live outcome); Claude: `build.clean-working`, `build.checks`, `dev.build-check` (Build 1, one real Haiku message), `build.failed-check`; Codex SYL-94 Build 1: `build.clean-working`, `build.checks`, `dev.build-check`, `build.failed-check-preserves-default` |
| BLD-0.6 | keep the record and the log of a failed build | New | SYL-95 Python: `build.relocated-unit`, `build.folder-alone`, `build.launcher-default-and-named`, `build.failed-check-preserves-default`, `build.withdrawal-rollback`; production `build.unit`, `build.contract`, `dev.build-check` and launcher records; Codex was a candidate at SYL-95; current numbered verification is below; prior verification: `builds.failed-check`, `builds.failed-command`, `builds.interrupted-build`; Codex SYL-94 Build 1: `build.failed-check-preserves-default` |
| BLD-0.7 | for a component outside Roots, take as the default the `working` Build with the highest build number, worked out from the records at every start, with no stored setting | Changed | SYL-95 Python: `build.relocated-unit`, `build.folder-alone`, `build.launcher-default-and-named`, `build.failed-check-preserves-default`, `build.withdrawal-rollback`; production `build.unit`, `build.contract`, `dev.build-check` and launcher records; Codex was a candidate at SYL-95; current numbered verification is below; prior verification: `builds.two-builds`, `builds.withdraw`, `builds.damaged-record`; Codex SYL-94 Build 1: `build.launcher-default`, `build.failed-check-preserves-default` |
| BLD-0.8 | for a component outside Roots, run the named Build when the launcher's first argument is `-v <build number>`, refuse a Build that cannot be run, and list those that can | New | SYL-95 Python: `build.relocated-unit`, `build.folder-alone`, `build.launcher-default-and-named`, `build.failed-check-preserves-default`, `build.withdrawal-rollback`; production `build.unit`, `build.contract`, `dev.build-check` and launcher records; Codex was a candidate at SYL-95; current numbered verification is below; prior verification: `builds.launch-refusal`, `builds.prune`; Codex SYL-94 Build 1: `build.launcher-named`, `build.failed-check-preserves-default`; a named `failed` Build (BLD-D13): `builds.failed-check`, passed 14 October 2026 |
| BLD-0.9 | pass arguments, standard input and output, signals and the exit status through the launcher unchanged, except that the launcher `arbol-trunk` hands the Build `--root <root>` before the command (RCT-0.8) | New | SYL-95 Python: `build.relocated-unit`, `build.folder-alone`, `build.launcher-default-and-named`, `build.failed-check-preserves-default`, `build.withdrawal-rollback`; production `build.unit`, `build.contract`, `dev.build-check` and launcher records; Codex was a candidate at SYL-95; current numbered verification is below; prior verification: `builds.streams`, `builds.signals`; the launcher `arbol-trunk`, which hands the Build `--root <root>` (SYL-179): `builds.trunk-launch`, `builds.trunk-selection`, `builds.trunk-pass-through`, `builds.trunk-first-build` |
| BLD-0.10 | let a damaged or missing record take only its own Build out of use | New | SYL-95 Python: `build.relocated-unit`, `build.folder-alone`, `build.launcher-default-and-named`, `build.failed-check-preserves-default`, `build.withdrawal-rollback`; production `build.unit`, `build.contract`, `dev.build-check` and launcher records; Codex was a candidate at SYL-95; current numbered verification is below; prior verification: `builds.damaged-record` |
| BLD-0.11 | prune only on command or by the time the owner set (BLD-0.26), keep every record, and never remove the default Build | Kept | SYL-95 Python: `build.relocated-unit`, `build.folder-alone`, `build.launcher-default-and-named`, `build.failed-check-preserves-default`, `build.withdrawal-rollback`; production `build.unit`, `build.contract`, `dev.build-check` and launcher records; Codex was a candidate at SYL-95; current numbered verification is below; prior verification: `builds.prune`, `builds.concurrent-prune`, `builds.concurrent-mutations` |
| BLD-0.15 | build a component as its repository's `arbol-build.json` says, hand the build commands and the checks the Build's folder and number in `ARBOL_BUILD_DIR` and `ARBOL_BUILD_NUMBER`, and run the checks against the Build's own program, not through the launcher | New | SYL-95 Python: `build.relocated-unit`, `build.folder-alone`, `build.launcher-default-and-named`, `build.failed-check-preserves-default`, `build.withdrawal-rollback`; production `build.unit`, `build.contract`, `dev.build-check` and launcher records; Codex was a candidate at SYL-95; current numbered verification is below; prior verification: `builds.description`, `builds.driver-checks`, `builds.invalid-description`; Claude: `build.clean-working`, `build.checks` (81 unit tests and 38 conformance scenarios from the numbered Build); Codex SYL-94 Build 1: `build.checks`, `build.source-and-runtime` |
| BLD-0.16 | write a component's launcher, a Python program that uses only the standard library, into `~/.local/bin` or the folder named with `--bin-dir` when the component is first built | New | SYL-95 Python: `build.relocated-unit`, `build.folder-alone`, `build.launcher-default-and-named`, `build.failed-check-preserves-default`, `build.withdrawal-rollback`; production `build.unit`, `build.contract`, `dev.build-check` and launcher records; Codex was a candidate at SYL-95; current numbered verification is below; prior verification: `builds.paths`, `builds.install`; Codex SYL-94 Build 1: `build.launcher-default`, `build.launcher-named`; the launcher `arbol-trunk`, written by the build of any Trunk and rewritten by installing again (SYL-179): `builds.trunk-components`, `builds.trunk-first-build`, `builds.trunk-launcher-text`, `builds.install-refreshes-launchers` |

Root-specific extensions:

| ID | The registry, its tool and the launchers must… | Origin | Verified by |
|---|---|---|---|
| BLD-0.17 | associate each Build of `arbol` and `arbol-root` with exactly one Root, named with `arbol-builds build --root`, and number Builds per component across all Roots | New | `builds.root-of-build` |
| BLD-0.18 | choose for `arbol` and `arbol-root` the newest runnable working Build of the named Root, or of the current Root when none is named, and refuse rather than choose another Root when that Build is absent | Changed | unit: `builds.root-default`, `builds.root-refusals`, `builds.root-inventory` |
| BLD-0.19 | accept `[--root <identifier>] [-v <build number>]` as the selection prefix of `arbol` and `arbol-root`, take a named Build's Root from its record and refuse conflicting selectors, while keeping Driver and App launchers independent of Roots | New | unit: `builds.root-named`, `builds.root-pass-through`, `builds.root-launcher-text`, `builds.install-refreshes-launchers`; existing plain Driver/App and Trunk checks |
| BLD-0.20 | preserve the newest working Build of `arbol` and `arbol-root` for every retained Root when pruning, and of each Trunk the newest working Build that fits each Root Contract version a retained Root uses, even if this keeps more than the requested count | Changed | unit (pending) |
| BLD-0.21 | record each Trunk Build's list of Root Contract versions, without assigning the Build to one Root, so one Build serves every Root of those versions | New | `builds.trunk-root-contracts` |
| BLD-0.22 | keep distinct Trunk implementations as distinct components with independent numbering, and never use build numbers across components to choose an implementation | New | `builds.trunk-components`; `arbol-trunk` never takes a Build of another Trunk (SYL-179): `builds.trunk-no-fit`, `builds.trunk-selection` |
| BLD-0.23 | keep the registry, launchers and `arbol-builds` outside every Root, and hold no Root's backend, UI code, migration script or table layout in them | New | `builds.outside-roots` |

Last-start recording and locking, accepted on 13 October 2026 ([BLD-D12](#decisions)), are implemented by SYL-153 and SYL-154. Removing unused Builds and the Seqoya Lab page remain pending. *journey* is the check of that name in the [Architecture](../architecture/README.md#conventions):

| ID | The registry, its tool, the launchers and Arbol must… | Origin | Verified by |
|---|---|---|---|
| BLD-0.24 | record the time of each start of a Build in its folder, without delaying the start or failing it | New | `builds.last-start`, `builds.last-start-write-failure`, `builds.last-start-disk-full`, `builds.last-start-refusal`, `builds.trunk-last-start`, `builds.last-start-inventory`, `builds.last-start-fallback`, `builds.install-refreshes-launchers` |
| BLD-0.25 | let a Build be marked Locked and unmarked, and never remove the files of a Locked Build | New | `builds.locked-record`, `builds.lock-unlock`, `builds.lock-states`, `builds.lock-refusal`, `builds.lock-building`, `builds.locked-prune`, `builds.lock-prune-race`, in `Locking` of `tests/test_builds.py` (SYL-154) |
| BLD-0.26 | remove, when the owner has set a time and only then, the files of the Builds that were not started for longer than that time, keep their records, and never remove a default Build, a Locked Build, a Trunk Build that a retained Root would run or a Build that an Exchange in progress runs on | New | unit (pending) |
| BLD-0.27 | offer in Seqoya Lab a page that lists the Builds of each component with their last start, a Locked switch for each and the field for the time, and run the removal when Arbol starts and once a day while it runs | New | journey (pending) |

Every component must:

| ID | A component must… | Origin | Verified by |
|---|---|---|---|
| BLD-0.12 | report its package version and the build number of the Build that is running, wherever it reports about itself | Kept | SYL-95 Python: `build.relocated-unit`, `build.folder-alone`, `build.launcher-default-and-named`, `build.failed-check-preserves-default`, `build.withdrawal-rollback`; production `build.unit`, `build.contract`, `dev.build-check` and launcher records; Codex was a candidate at SYL-95; current numbered verification is below; prior verification: Claude Driver: `base.info`, `base.packaged-info`, `build.launcher-default`, `build.launcher-named`; Codex Driver: `base.info`, `base.packaged-info`, `C32` (info; numbered run identity verified by SYL-94); other components pending; Codex SYL-94 Build 1: `build.launcher-default`, `build.launcher-named`, `build.contract (C32 and numbered started events)` |
| BLD-0.13 | write a format number into the data its Builds share, refuse data with a higher number than it knows, and raise the number only for a change older Builds cannot read | Changed | SYL-95 Python: `build.relocated-unit`, `build.folder-alone`, `build.launcher-default-and-named`, `build.failed-check-preserves-default`, `build.withdrawal-rollback`; production `build.unit`, `build.contract`, `dev.build-check` and launcher records; Codex was a candidate at SYL-95; current numbered verification is below; prior verification: Claude Driver: `base.state-newer`; build tool delegation and declared formats: `builds.shared-data-format`; Codex Driver: `state.format`, `base.state-newer`; other components pending; Codex SYL-94 Build 1: `build.test-state-cleanup`, `build.unit (format refusal)`, `build.contract (C38)` |
| BLD-0.14 | read its build number and its package version from the record in its own folder, and report the build number `0` when it runs outside a Build's folder | New | SYL-95 Python: `build.relocated-unit`, `build.folder-alone`, `build.launcher-default-and-named`, `build.failed-check-preserves-default`, `build.withdrawal-rollback`; production `build.unit`, `build.contract`, `dev.build-check` and launcher records; Codex was a candidate at SYL-95; current numbered verification is below; prior verification: Claude Driver: `base.build-identity`, `base.packaged-info`, `build.launcher-default`, `build.launcher-named`; Codex Driver: `base.build-identity`, `base.packaged-info`; other components pending; Codex SYL-94 Build 1: `build.unit (build identity)`, `build.launcher-default`, `build.folder-alone` |

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
  root?: string;                       // required for arbol and arbol-root; absent for the App, Drivers and Trunks
  contract?: number;                   // a Driver: Driver Contract; arbol-classifier: its own contract
  rootContracts?: number[];            // required for a Trunk: the versions of the Root Contract it implements, [1]
  dataFormat?: number;                 // the format number of the data it reads and writes
  withdrawn?: { at: string; reason: string };
  prunedAt?: string;                   // files removed; the record, log and last-start remain
  lockedAt?: string;                   // Locked: the files are never removed
  failure?: { stage: "build" | "entry" | "check" | "launcher"; name: string; message: string };
}
```

```ts
interface BuildsSettings {             // ~/.arbol/arbol-builds.json
  removeUnusedAfterDays?: number;      // absent: no Build is removed for being unused
}
```

The commands of `arbol-builds` are in the table above. Each prints JSON on standard output. `list` prints an array of records with a `default` boolean, grouped by component name and highest build number first within each component; `show`, `build`, `withdraw`, `lock` and `unlock` print a record; `prune` prints `{ component, pruned: string[] }`, and `prune --unused` an array of these, one for each component. A refused command prints `{ error: { code, message } }` and exits 1. A launcher refusal uses the same envelope and includes an `available` array of runnable build numbers.

For `arbol` and `arbol-root`, `list` retains the full inventory but marks `default` only for the selected Root; `show` without a build number uses that same selection. A named record supplies its own Root, and a conflicting `--root` is refused. Trunk compatibility fields are inventory metadata; the launcher `arbol-trunk` chooses the Build, and `arbol-root` names the Trunk and the exact Build it starts (RCT-0.7, [RCT-2](../../arbol-root/contract/02-starting-stopping-and-settling.md#how-the-root-manager-uses-a-trunk)). A Build that does not fit is reported with the Builds that fit (RCT-0.9), not a comparison of build numbers across components.

The global `--registry-dir <folder>` option selects another registry, and `--bin-dir <folder>` selects the launcher destination. Defaults remain those above. `build` finds the repository at `~/repos/sylvan-stack/readonly/<component>`, and `arbol-trunk/<code name>` in `~/repos/sylvan-stack/readonly/arbol-trunk/trunks/<code name>/`: the clones that always hold the last merged `main` and that nobody edits ([BLD-D18](#decisions)); `--repo <folder>` overrides that location for this build, and `--root <identifier>` names the Root of a Build of `arbol` or `arbol-root` (RTM-D9). These options accept both `--name value` and `--name=value`, before or after the command. A launcher remembers the registry selected when it was written.

`list` returns Build records with `default: boolean`, `lastStart: string | null`
and `unusedSince: string`. `show` returns one Build record with `lastStart`
and `unusedSince`. These are output fields, not stored Build-record fields;
[Unused Builds and Locked Builds](#unused-builds-and-locked-builds) defines their fallback.

```ts
interface BuildDescription {           // arbol-build.json
  component: string;
  build: string[];                     // nonempty POSIX shell commands
  entry: string;                       // executable within the Build
  checks: Array<{ name: string; command: string; kind?: "unit" | "contract" | "live" }>;
  contract?: number;                   // required positive whole number for a Driver; absent for a Trunk (RCT-D3)
  rootContracts?: number[];            // required for a Trunk: the versions of the Root Contract it implements, distinct positive whole numbers, at least one; absent for every other component
  dataFormat?: number;                 // required positive whole number for a Driver
}
```

Reserving a number uses an atomic creation of its directory; all numbered directories count, including damaged records. A Trunk's numbered directories lie in `builds/arbol-trunk/<code name>/`. Metadata updates use atomic replacement of `build.json`. Record changes, withdrawal and pruning are serialised per component, so a simultaneous withdrawal cannot make a Build the default while pruning removes its files. Short-lived process reservations in `.writers/` protect these changes; dead processes are ignored, and listing or running never needs those reservations. Build commands and checks run outside the reservation. A build stopped by the caller is failed and keeps its log. After an uncatchable kill its unfinished record stays `building`, cannot run, and still consumes its number. BLD-0.13 belongs to each component: the build tool records its declared `dataFormat` and never changes shared component data.

Every time in a record has the form that JavaScript's `toISOString` writes, for example `2026-10-15T09:30:00.000Z`. The tool and the launchers accept the ECMAScript date-time format, which includes that form; a record with a time in any other form counts as damaged ([BLD-D15](#decisions)).

## Known problems in version 1

Not to be reproduced.

- **One version at a time.** Trying an older or a newer build meant installing it over the current one.
- **Upgrade machinery larger than the product.** A controller took a census of processes, pinned executables by content hash and journalled every step. When its own records were lost, nothing could be rebuilt or restarted for two days.
- **Names nobody could type.** A build was identified by a timestamp and a hash.
- **Slow starts.** A packaged one-shot command spent about 4.5 seconds before doing any work. A launcher in front of every call must not add to that.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#4. The upgrade machinery became a second product`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#6. Many resident services with strict, version-coupled contracts`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#Anti-goals`

## SYL-165 build tool verification, 15 October 2026

`arbol-builds` and the launchers are typed Python since `arbol` commit `682e388` ([BLD-D15](#decisions)); the fixes from two reviews are in `3ed089f` and `bc6bc7a`. On 15 October 2026 the tool was installed into `~/.local/bin` with its pinned CPython 3.14.8. The installation rewrote the three launchers then in use, `arbol-classifier`, `arbol-claude-driver` and `arbol-codex-driver` ([BLD-D14](#decisions)), and removed the Node.js tool; a copy of that tool and its launchers is kept in `~/.local/share/arbol-builds-node-backup-2026-10-15`. From a clean login shell, `arbol-builds list` lists all 21 records, and `info` of each component reports its default Build: classifier 6, Claude Driver a, Codex Driver 5. A named older working Build (`arbol-claude-driver -v 9 info`) runs; a named failed Build that has its program (`arbol-classifier -v 5 info`) runs and prints its warning line; an unknown number is refused with the list of Builds that can run. No vendor request was sent.

All 45 checks of `arbol:tests/test_builds.py` pass, and so do Ruff and strict mypy. The 22 checks of the TypeScript tool keep their names, the `builds.*` names in the Requirements table, so those names now verify the Python tool; 23 more cover what the Python tool adds and what the two reviews found untested. Of 53 faults planted in the code one at a time, every one makes a check fail; two of them, the two copies of one Ctrl-C safeguard, only together. Both Drivers' rehearsals (`scripts/verify_build.py`, synthetic checks, no vendor request) pass with the Python tool.

A launcher adds 15.19 ms to a direct start (median of 60 rounds; 95th percentile 16.96 ms), against 23.46 ms for a Node.js launcher timed in the same rounds.

## SYL-155 Root and Trunk verification, 16 October 2026

`arbol-builds build arbol --root <identifier>` and `build arbol-root --root <identifier>` write the Root into the record when the build starts; the build is refused without `--root` for those two and with it for every other component, before a number is reserved. A Trunk is the component `arbol-trunk/<code name>`, built from `~/repos/sylvan-stack/arbol-trunk/trunks/<code name>/` unless `--repo` names another folder, into `builds/arbol-trunk/<code name>/<build>/`, with its own count, and gets no launcher of its own. Its record copies `rootContracts` from its description. `list` and `show` print `root` and `rootContracts`, and a record of `arbol` or `arbol-root` without a valid `root`, or of a Trunk without valid `rootContracts`, counts as damaged. Nothing chooses by these fields yet: the default Build of a Root and `--root` on the launchers are SYL-158, the launcher `arbol-trunk` is SYL-179, pruning by Root and Root Contract version is SYL-159.

All 49 checks of `arbol:tests/test_builds.py` pass, and so do Ruff and strict mypy. Four are new: `builds.root-of-build` (BLD-0.17, ARC-1.12) builds a sample `arbol-root` twice for one Root and twice for another, which get the numbers 1 to 4; `builds.trunk-components` (BLD-0.22) builds the sample Trunks `arbol-trunk/alpha` and `arbol-trunk/beta` from their folders; `builds.trunk-root-contracts` (BLD-0.21) refuses a Trunk without `rootContracts` before a number is reserved; `builds.outside-roots` (BLD-0.23). Of 26 faults planted in the new code one at a time, every one but one makes a check fail; that one changes nothing that can be seen, since a record is written with whole numbers in any case. Both Drivers' rehearsals (`scripts/verify_build.py`, synthetic checks, no vendor request) pass with this tool.

## SYL-179 launcher arbol-trunk verification, 16 October 2026

The launcher `arbol-trunk` is the text of `arbol:src/arbol_builds/launcher.py`, `roots.py` and `trunk_launcher.py`, without their imports from the package, followed by one call of `launch_trunk` that names the registry. `arbol-builds build` of any Trunk writes it, and installing the tool again rewrites it (BLD-D14). It reads the Roots as BLD-D17 says, and picks, starts and refuses as RCT-0 and "Running a Build" say.

All 61 checks of `arbol:tests/test_builds.py` pass, and so do Ruff and strict mypy. Twelve are new: `builds.root-records` and `builds.current-root`, the Roots as the launchers read them (ARC-1.7); `builds.trunk-launch`, RCT-0's example with First Sapling and a second Root on version 1, a third Root on version 2, and Builds 3, 4 and 5 of `trivial` with `[1]`, `[1, 2]` and `[2]`; `builds.trunk-selection`, `builds.trunk-named-build` and `builds.trunk-pass-through` (RCT-0.7, 0.8, BLD-0.9); `builds.trunk-refusals` and `builds.trunk-no-fit` (RCT-0.9); `builds.trunk-list` and `builds.trunk-list-chosen` (RCT-0.10); `builds.trunk-launcher-text`, which checks that the three modules define no name twice; and `builds.trunk-first-build`, a sample Trunk built three times with the tool and started through the launcher it wrote. `builds.trunk-components` and `builds.install-refreshes-launchers` now check that the build of a Trunk writes `arbol-trunk` and that installing again rewrites it. Of 43 faults planted in the new and changed code one at a time, every one but one makes a check fail. That one takes away the Ctrl-C safeguard inside `launch_trunk`, which the launcher's first line already applies; removing both copies makes `builds.trunk-pass-through` fail, as with a component's launcher in SYL-165. A Ctrl-C while Python itself starts can print a traceback at line 0 of the launcher, or stop Python with status 1, before any of its code runs (8 of 1000 tries); none points into the launcher's own lines. Both Drivers' rehearsals (`scripts/verify_build.py`, synthetic checks, no vendor request) pass with this tool.

`arbol-trunk` adds a median of 15.49 ms (95th percentile 16.83 ms) to a direct start of the same Build for `run` with the current Root, and 15.57 ms (16.70 ms) for the call `arbol-root` makes, which names the Root, the Trunk and the Build. A component's launcher, timed in the same 60 rounds with the installed tool's pinned Python, adds 14.07 ms (15.10 ms). The launcher `arbol-trunk` is 29,441 bytes, a component's 16,127.

The tool was installed again into `~/.local/bin` the same day, from a clean login shell; a copy of what it replaced is kept in `~/.local/share/arbol-builds-backup-2026-10-16-syl179`. It rewrote the launchers of the classifier and both Drivers; `arbol-builds list` lists all 23 records, and each `info` reports its default Build: classifier 6, Claude Driver b, Codex Driver 6. No Trunk is built there yet, so `~/.local/bin` holds no `arbol-trunk`; the first build of the Trivial Trunk writes it (SYL-180). Not done: RCT-0's requirement table does not name these checks yet, because RCT-0 was held by another task (SYL-171) that day.

## Root extension verification, 12 October 2026

BLD-0.17–23 were then accepted requirements with pending unit checks. The installed `arbol-builds` tool and launchers did not yet implement Root association, `--root`, current-Root defaults, per-Root pruning protection or Trunk compatibility inventory. The Driver build and launcher checks below verify the existing global Driver path only. They do not establish that any Root-aware path works, and no Root-aware requirement is marked implemented by this edit. `arbol-app`, `arbol`, the Root manager and the first Trunk need their own Build checks before those components can be described as implemented. At that date BLD-0.24–27, accepted on 13 October 2026, were not implemented either. SYL-153 now implements BLD-0.24 as described in “Unused Builds and Locked Builds”; SYL-154 implements `lock`, `unlock` and Locked pruning protection (BLD-0.25). `prune --unused` and the Seqoya Lab page remain pending.

The existing source was checked on 12 October 2026: `arbol:builds/records.ts#BuildRecord` has no Root or chat-table association; `#launch` recognises `-v` and selects a global default; `arbol:builds/cli.ts#main` has no `--root` option; and `arbol:builds/service.ts#pruneBuilds` protects the global default. These are the implementation gaps, not verification of the new requirements. Since the port to Python on 14 October 2026 the same gaps are in `arbol:src/arbol_builds/launcher.py#valid_record` and `#launch`, `arbol:src/arbol_builds/cli.py#main` and `arbol:src/arbol_builds/service.py#prune_builds`; the TypeScript locators refer to commit `037468f`.

## SYL-94 numbered Build verification, 7 October 2026

Codex Build `1`, package version `1.0.0`, is the first working numbered Python
Build and the production default. It was built from a clean checkout of
`19fb51de21b074f62984fe28ad2450c3b1b09268`, using the repository's
`arbol-build.json` with locked uv setup, Ruff, strict mypy and standalone
packaging. The Build's own CPython 3.14.8 ran all 128 packaged unit tests; its
direct executable passed all 38 shared conformance scenarios, including
numbered `info` and `started` identity. The final `dev.build-check` passed with
exactly one no-tools ready request on `test-chatgpt`, using `gpt-5.6-luna` with
low effort. Its report retains actual tokens, tool/source/runtime provenance
and usage before and after. Contract and state format remain `1`.

Default and explicitly named launcher invocations both report Build `1` and
package version `1.0.0`. The direct executable also runs from an unrelated
folder with only HOME, PATH and LANG, without a source checkout or external
Python/uv/Node on PATH. Package and registry source records agree, and the
pinned standalone interpreter and packaged file digests passed verification.
The test state has no active run or temporary residue after the live gate.

An intentionally failing first check reserved Build `2`, retained its failed
record and log, and spent no inference quota. Build `1` stayed the default;
explicit selection of Build `2` was refused and listed only Build `1` as
available. The production build tool and launchers required no changes.
Extended vendor live checks were not run; previously unobserved real vendor
failures remain unobserved. Earlier candidate and migration records stay
historical.

Acceptance names and raw records:
`~/Artifacts/arbol-codex-driver/research/first-working-build-2026-10-07/verification.json`,
`coverage-audit.json`, `working-build.log`, `failed-build.log` and
`dev-build-check.json`. The numbered folder and launcher remain installed at
`~/Library/Application Support/Arbol/builds/arbol-codex-driver/1/` and
`~/.local/bin/arbol-codex-driver`.

## Python migration verification, 7 October 2026

SYL-95 verification is recorded in the requirement-level `~/Artifacts/arbol/driver-contract/python-migration-coverage-2026-10-07.json` and the Driver records `research/python-migration-2026-10-07/verification.json`. Python check names identify the copied standard-library unittest suites and the unchanged shared scenarios. Prior Driver unit/probe/live names refer to historical TypeScript evidence; unchanged shared build-tool and runner names remain active. Claude passes the complete 38-scenario suite; Codex passes its five original scoped groups (29 scenario invocations, with the same exclusions), and remains a development candidate. No historical live result is treated as fresh Python evidence, and previously unobserved vendor failures stay unobserved.

## Decisions

The 6–7 October decisions below remain as recorded. The Root-specific extension is BLD-D11; it refines the default and launcher scope for `arbol` and `arbol-root`, and leaves the Driver contract, checks and shared-data rule unchanged.

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| BLD-D1 | How are versions numbered? | A count per component, starting at 1, written in hexadecimal | Decided 6 October 2026 by the owner |
| BLD-D2 | Which version runs when none is named? | The last working one that was built successfully | Decided 6 October 2026 by the owner |
| BLD-D3 | How is a version named on the command line? | `-v <version>` as the first argument, as in `arbol-codex-driver -v a3 …` | Decided 6 October 2026 by the owner |
| BLD-D4 | What makes a Build working? | The build finished and the component's own automatic checks passed. Checks that spend quota are not among them. A Build that fails later in use is withdrawn by hand | Decided 6 October 2026 by the owner: the automatic checks and, on top of them, one real message through the real tool on every build (SYL-31) |
| BLD-D5 | Where is the registry? | `~/Library/Application Support/Arbol/builds/` | Decided 6 October 2026 by the owner: the proposed default (SYL-32) |
| BLD-D6 | What becomes of the version numbers in `package.json` and in the repositories' README files (2.0.0, 1.0.0)? | `package.json` keeps a number because npm needs one, and it means nothing. The registry's number is the component's version. The README files are corrected when the first Builds exist | Decided 6 October 2026 by the owner, against the proposed default: both numbers stay. 2.0.0 and 1.0.0 are package versions, and the hexadecimal count is the build number (SYL-33) |
| BLD-D7 | How many Builds are kept? | All, until `prune` is run. Suggested habit: the newest four working ones, as in version 1 | Decided 6 October 2026 by the owner: managing Builds, pruning included, is Arbol's work and never a Driver's. With that the proposed default stands (SYL-51). Extended on 13 October 2026 by BLD-D12 |
| BLD-D8 | Is a version named the same way for a component that stays running, such as the application? | Yes, `-v` starts that Build. Only one Build of such a component runs at a time, and replacing it while it runs is specified with that component | Decided 6 October 2026 by the owner: `-v` means the same for every component. It runs exactly that Build, and without it the newest working one runs. Any number of invocations can run at once, of one Build or of several. Whether a component that stays running can run twice at the same time is left to that component's own specification and is not settled here (SYL-52) |
| BLD-D10 | How are unspecified command, pruning and launcher details represented? | POSIX shell command strings, optional check kinds with all three required for Drivers, executable relative entries, explicit path overrides, a `prunedAt` field, atomic directory reservation and record replacement, and `process.execve` launchers. Shared data formats remain each component's responsibility | Decided 7 October 2026 during SYL-76, a technical choice; the Interface and Behaviour sections give the details. Since 14 October 2026 the launchers are Python and use `os.execv` (BLD-D15) |
| BLD-D9 | Where are the build tool and the launchers, and how does a repository describe its build? | `arbol-builds` is part of the `arbol` repository and is not a Build itself. Launchers go to `~/.local/bin`, where the vendor tools already are on this machine. A repository describes its build in one file, `arbol-build.json` | Decided 6 October 2026, a technical choice made in drafting on the owner's go-ahead |
| BLD-D11 | How do numbered Builds fit persistent Roots and several Trunk implementations? | Root-bound `arbol` and `arbol-root` Builds, global numbering and inventory, named/current Root defaults, `--root` before `-v`, per-retained-Root pruning protection, and Trunk compatibility recorded by contract and chat-table layout | Decided 12 October 2026 by the owner in [ARC-D47](../architecture/01-roots.md#decisions): Root replaces Ring as the persistent environment. This integrates ARC-D32's selection and pruning rules, now for Roots; each Trunk implementation remains a separate globally numbered component. The Root extensions are accepted specification work and are not implemented by the existing Driver build tool. Changed 15 October 2026 by [RCT-D3](../../arbol-root/contract/00-overview.md#decisions): a Trunk's compatibility is recorded as the list of Root Contract versions it implements, `rootContracts`, in place of `contract` and `chatTablesOf` |
| BLD-D12 | How are Builds that are no longer used removed, and how is a Build kept for good? | A time after which a Build that was not started is removed, and a Locked mark that keeps a Build. The launchers record each start. Nothing is removed for being unused while no time is set. Arbol runs the removal when it starts and once a day. The form is a page in Seqoya Lab, and the same is possible through `arbol-builds` | Decided 13 October 2026 by the owner, who asked for a simple form for managing Builds, with a time after which old Builds without activity are removed and a Locked mark that keeps a Build from being removed, and confirmed the proposed details. It extends BLD-D7 and leaves `prune --keep` as it is. The file `last-start`, the setting `removeUnusedAfterDays` and the commands `lock`, `unlock` and `prune --unused` are a technical choice made the same day |
| BLD-D13 | Can a Build that failed its checks be started? | Yes, when it is named with `-v` and its program is there, with a line on standard error that says it failed and names the step. Without `-v` only a `working` Build is chosen, as before. Until a component has its first working Build, this is the only way to start it by its name, as `arbol-classifier -v 3 add-key` needs | Decided 14 October 2026 by the owner: the proposed default |
| BLD-D14 | How do the launchers already installed get a change to the launcher code? | Installing `arbol-builds` again rewrites every launcher in its folder with the current launcher code, keeping each one's component and registry, launchers of the earlier Node.js tool included. The alternative: a launcher changes only when its component is next built, which for a Driver costs a real message and makes a new Build | Chosen 14 October 2026 as a technical choice, for SYL-165 |
| BLD-D15 | In which language are `arbol-builds` and the launchers written, and which interpreter runs them? | Typed Python with the standard library only. The interpreter is the pinned standalone CPython that every Build carries, installed once with the tool in `.arbol-builds` beside it, and named by its absolute path in the first line of the tool and of every launcher the installed tool writes. A launcher sets SIGPIPE and SIGXFSZ back to their default before the hand-over, passes arguments and environment on byte for byte, and reports a hand-over that fails as `launch_failed`. Times in records must be in the ECMAScript date-time format; forms that only the Node.js tool also accepted now count as damaged | Decided 14 October 2026 by the owner: everything in the `arbol` repository moves to typed Python. The interpreter, its place and the launcher details are a technical choice made the same day, for SYL-165. This replaces the TypeScript/Node part of BLD-D10 and DRV-D1 for these tools |
| BLD-D16 | What does `arbol-builds` accept as a Root identifier and as a Trunk's `rootContracts`? | A Root identifier is one lower-case word of the letters `a` to `z` and the digits, as RCT-0 refuses any other; nothing checks that the Root exists, since `arbol-roots` comes later and a build only records the Root. `rootContracts` is a list of at least one positive whole number, each named once; a Trunk lists no `contract`, and no other component lists `rootContracts`. A description that breaks this is refused before a number is reserved, and a record that breaks it counts as damaged | Chosen 16 October 2026 as a technical choice, for SYL-155 |
| BLD-D17 | How does `arbol-trunk` read a call and the Roots, and what does it answer for a Root identifier that is not one lower-case word, when no Root is named and none is working, and for a call it cannot read? | `--root` only first; the next argument is the code name unless it is `-v`, a command word or begins with `-`. The launcher reads `root.json` of the Root named, or of every Root to find the current one, at every start. A record counts as damaged unless `root` is its folder's name, `status` is `preparing`, `working` or `failed`, `createdAt` is a time in the form of the Build records and `rootContract` is a positive whole number; it reads no other field. The current Root is the working Root with the latest `createdAt`, and of two created at the same millisecond the one whose identifier sorts last. `unknown_root` for a Root identifier that is not one, for a Root without a readable record, and when no Root is named and none is working, with a message that says which; `unknown_trunk` for a code name that is not one or has no folder in the registry; `no_fit` for every call that leaves no Build to start; `invalid_input` for a call without a command, and for `list` after `-v` or with more arguments. Only `list` is answered by the launcher: any other command goes to the Build, so a later Root Contract version can add one without a new launcher. `available` stands beside `error`, as RCT-0's `Refusal` gives it | Chosen 16 October 2026 as a technical choice, for SYL-179. The Known gaps of the Arbol 2 Foundation Saga asked to settle the first two points in RCT-0; RCT-0 was held by another task that day, and the launcher's refusals are listed here in BLD-0 already, so they are settled here |
| BLD-D18 | Where does `arbol-builds build` take a repository from when `--repo` names none, and where does a Build's check take the suite of another repository from? | From `~/repos/sylvan-stack/readonly/<repo>`, the clone of each repository that always holds the last merged `main` and that nobody edits, and for a Trunk from its folder `trunks/<code name>/` in `readonly/arbol-trunk`. A check that runs the suite of another repository takes it from there too: for a Trunk, the Root Contract's suite from `readonly/arbol-root` ([RCT-4](../../arbol-root/contract/04-conformance.md#how-a-trunk-builds-check-runs-it)); for a Driver, the Driver Contract's suite from `readonly/arbol`, unless `ARBOL_CONFORMANCE_REPO` names another checkout. `arbol-builds` itself is installed from `readonly/arbol`. The repositories' own folders `~/repos/sylvan-stack/<repo>` belong to the owner and to the agents started there, and can hold unmerged edits or another branch; `--repo` still builds from any checkout | Decided 16 October 2026 by the owner, together with the named work areas of the guide Working in Sagas, in which every Beat is merged into `main`; written for SYL-209 |
| BLD-D19 | How are Build starts recorded and shown? | One UTC millisecond timestamp and newline in `last-start`; an atomic best-effort replacement without locks, retries or flushing before the launchers hand over. `list` and `show` derive `lastStart` and `unusedSince` without changing `build.json`, using the regular file’s modification time if its contents cannot be read and the build time if no start is recoverable. Pruning keeps `last-start` | Chosen 26 October 2026 as a technical choice for SYL-153, carrying forward the earlier hand-over and keeping BLD-D12’s start-failure rule |
| BLD-D20 | What do repeated lock/unlock calls do, which Build states can be locked, and how do they race with building and pruning? | Both commands accept every known unpruned Build, including building, failed and withdrawn, and refuse unknown or pruned records. Lock is idempotent and preserves its original lockedAt; unlock is idempotent and removes it. Both print the stored record. Validate lockedAt like other record times. Serialize mutations per component; an in-flight Build preserves the current mark or its absence at each record write. Prune keeps the newest requested working Builds plus any older Locked Builds, with lock-first retaining files and prune-first making lock fail. The alternative of refusing building records would narrow the owner’s ability to keep any Build | Chosen 26 October 2026 as a technical choice for SYL-154, before implementation |
| BLD-D21 | How do Root-component launchers and inventory select or refuse a Root? | Parse only [--root id] [-v build] before passing every later argument unchanged, including an empty command; add no Root argument to the Build. Reuse the Root reader, allow explicit preparing/failed Roots and require a working implicit current Root. A named Build takes its own retained Root; contradictory selectors are invalid_input, missing/unreadable Roots unknown_root, and unavailable Builds build_unavailable, with scoped available and component/Root diagnostics. Inventory with no current Root still lists records with no Root-component default; explicit Root selectors must resolve, except named show preserves stored-record introspection and only checks agreement. A non-Root component’s explicit list/show rejects --root; global inventory keeps its global defaults. Tool errors keep builds_failed. Filter records for the selected Root before the unchanged global chooser, keeping plain and Trunk launchers unchanged | Chosen 26 October 2026 as a technical choice for SYL-158, before implementation |
| BLD-D22 | What does count-based pruning retain when a Root record is unreadable or damaged? | A valid identifier folder with a root.json directory entry is retained in any state, including a damaged, unreadable, dangling or nonregular record. Root components protect that folder identifier’s newest runnable working Build. Trunks refuse the whole prune before mutation when any retained Root lacks a readable valid record, since its required version is unknown. A missing catalogue means no Roots; other listing failures refuse Root/Trunk pruning, while outside components never read it. Add these protections to newest-n, Locked and existing global-default retention. Read one snapshot under the component reservation, without a catalogue lock; later catalogue changes enter the next prune’s view. Use a pruning-only reader with shared Root validation, leaving embedded launcher readers unchanged | Chosen 26 October 2026 as a technical choice for SYL-159, before implementation |
