---
role: authored
---
# BLD-1 · Cleanup of completed build and test runs

**Status:** accepted scope · 19 November 2026

## Purpose and scope

Keep the internal disk from filling with disposable output from completed
build and test runs under `~/Builds`. Registered Builds remain under [BLD-0](00-builds-and-versions.md).
The retired Arbol 1 worker cache is outside this scope. Keep retained evidence
and archives in the places named in the [Build output guide](../../mycel/operations/build-output.md).

## Behaviour

A runner releases its run after its processes have finished and its evidence
has been saved outside `~/Builds`. The runner calls the shared finalization
command as its last use of the run directory. A completed run whose output is
still needed stays in place. Exit status and file age carry no release authority.

Release moves one run into a private cleanup queue on the same filesystem.
The command refuses symlinked run paths, a missing evidence report and runs
with attached disk images. Unreleased directories already on disk remain
eligible for a later explicit release by their owner or runner.

The installed backend sweeps the shared queue when it starts and every 25
minutes while running. Sweeps stay off the request path, cannot overlap and
skip a run if attachment information is unavailable or the run is in use by
a mounted disk image. Removal cannot cross a filesystem mount. A failed or
interrupted removal leaves its remaining files queued for a later sweep.
An isolated backend never sweeps the installation's queue.

## Requirements

| ID | Arbol must | Origin | Verified by |
|---|---|---|---|
| BLD-1.1 | Give build and test runners one finalization command that queues an individual completed run after its evidence is saved, and refuses an unsafe path or an attached disk image. Only the runner's release makes output eligible. | New · owner, 19 November 2026; [OG-2](../../goals/OG-2.md), [OG-3](../../goals/OG-3.md), [OG-4](../../goals/OG-4.md) | Disposable run cleanup drill · pending |
| BLD-1.2 | Sweep released runs from the installed backend on startup and every 25 minutes, without delaying requests or following mounts. Serialize sweeps and retry remaining queued files after failures or interruptions. | New · owner, 19 November 2026 | Disposable run cleanup drill · pending |
| BLD-1.3 | Let a runner explicitly declare that it owns a disposable output directory. Save its original evidence at a new location outside `~/Builds` before releasing it. Preserve outputs when ownership or shutdown is uncertain or when saving evidence fails. | New · owner, 19 November 2026 | Runner completion and isolated backend qualification · pending |

## Interface

`arbol-builds release-run <run-directory> --evidence <report>` takes one
run under `~/Builds/<repository>/<run-id>` or
`~/Builds/<organization>/<repository>/<run-id>`. The report is an existing
regular file outside `~/Builds`. On success the command returns the original
and queued paths in JSON. A refusal leaves the run at its original path.

Call the command at the end of each runner that produces disposable output,
after joining its processes and writing the saved report. The runner can
release a failed run after writing its failure evidence. Follow-up work that
needs the run's files keeps the run at its original path until that work ends.

For the Build runner and its packaged checks, give a new run's `registry` and
`bin` children as the isolated locations and pass `--release-to <new-evidence-directory>`.
The runner saves the terminal Build record and full Build log, including its
checks, then queues the run. A normal installed Build keeps its registry.
For the standalone session import drill, `--release-to <new-evidence-directory>`
saves the evidence tree of a completed drill with a dedicated `--run` folder
and external Build inputs. A partial phase or uncertain shutdown keeps the run.
A handoff failure reports the cleanup error separately from the check result.

## Known problems

Older directories contain a mixture of completed and active work. Arbol Browser
builds can keep disk images attached, and the current Browser build script
references a runtime archive in a prior run. A runner must finish with an output
before releasing it, even if the process that created the output already exited.

<!-- sources:
arbol-browser:@code/scripts/package-host.mjs#preservedStockArchive
arbol:@code/src/arbol_backend/server.py#Backend.run
arbol:@code/src/arbol_builds/cli.py#main
arbol:@code/src/arbol_installation/build_output.py#release_run
arbol:@code/src/arbol_installation/build_output.py#sweep
arbol:@code/src/arbol_installation/build_output.py#sweep_periodically
-->

## Decisions

| Decision | Outcome |
|---|---|
| Cadence and location | Arbol's backend checks every 25 minutes. The owner selected completed build and test runs under `~/Builds` on 19 November 2026. |
| Authority to release | Build and test runners release output after saving evidence, as selected by the owner on 19 November 2026. |
