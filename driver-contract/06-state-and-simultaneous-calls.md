---
role: authored
spec: DRV-6
status: accepted
---
# Driver Contract · 06 State and simultaneous calls

A Driver is started anew for every operation, so everything it knows from one call to the next is in files. This specification names those files and their formats, says how several calls that run at the same moment keep out of each other's way, how one call reaches another that is already running, and what is done about the leftovers of a call that was killed. It matters because a Driver has no process that stays running and could keep order: the files and the rules for writing them are the only coordination there is.

## Scope

Covered: the layout of the state directory, the format of each file in it, how files are written, the data format number, the map from chat sessions to the vendor tools' saved conversations and how a Driver decides whether a saved conversation still fits, records of runs and sign-ins in progress, locks, stopping a run from another call, replacing a sign-in, leftovers of a killed call, what the Driver remembers about the vendor tool's program.

Not covered: what the vendor tool keeps in its own home, which is the tool's ([DRV-0](00-overview-and-boundary.md#the-vendor-tools-home)); the settings file, which is not in the state directory (DRV-0); the registry of Builds (BLD-0).

## Behaviour

### The state directory

All of a Driver's files are under one folder, by default `~/Library/Application Support/Arbol/drivers/<driver>/`, or the folder named with `--state-dir`. Folders are readable by the owner only, files likewise.

```text
<state directory>/
  format                        the data format number, one line
  tool.json                     what the Driver last learnt about the vendor tool's program
  subscriptions/
    <subscription id>/
      record.json               the Subscription
      lock                      present only while record.json is being rewritten
      sign-in.json              present only while a sign-in is pending
      home/                     historical test-profile home, preserved until explicit cleanup; current qualification uses existing real profiles
      chats/
        <chat key>.json         one entry of the map per chat session
  runs/
    <run id>.json               present only while that run is in progress
  tmp/
    <run id>/                   files that live as long as one run
```

Nothing else is kept. A folder or file that is missing is created when it is first needed, so an empty state directory is a valid one. A `home/` that an earlier Build made for a Subscription that is not a test one is no longer used; the Driver leaves it as it is.

### Writing a file

A durable state file is always written whole: the Driver writes the new content to a temporary file in the same folder and renames it over the old one. A reader therefore sees the old content or the new, never a part. Durable state files are JSON in UTF-8, except `format`. Scratch files under `tmp` may be scripts or process ledgers in text form.

### The data format number

`format` holds one whole number, `1` for the layout of this specification. A Driver writes it when it creates the state directory. A Build that finds a higher number than it knows does nothing and fails with `state_newer`, naming both numbers (BLD-0.13). The number rises only when a change makes the files unreadable for older Builds.

### A Subscription's record

`record.json` holds what the Driver knows about a Subscription between calls: the fields of `Subscription` (DRV-1) except two. The `settings` are read from the settings file whenever the record is returned. The state `signing_in` is never stored: a Subscription is `signing_in` exactly while its `sign-in.json` names a process that is alive.

The Subscriptions a Driver has from the start need no file: one that has no folder yet is `signed_out`, and its folder is created with its first change.

### Locks

Two calls may want to change the same Subscription at the same moment. A change is: read `record.json`, alter it, write it. For exactly that long the call holds the Subscription's lock.

The lock is the file `lock`, created in a way that fails when the file exists, and holding the process that owns it. A call that finds the lock taken waits and tries again every 50 milliseconds. A lock whose owner is no longer alive is taken over. After 10 seconds without success the call fails with `internal`, naming the owner.

A lock is never held across anything slow: not across a request to the vendor, not while the vendor tool runs, not during a sign-in. Whatever lasts is not a lock but a record with its owner in it: a run in progress, a pending sign-in. One Subscription never waits for another, and reading takes no lock.

### Knowing that a process is alive

Every record of something in progress names its owner by two values: the process identifier and the time that process was started. An owner is alive when a process with that identifier exists and was started at that time, give or take two seconds. The second value keeps a new, unrelated process that happens to receive the same identifier from being taken for the owner.

### A run in progress

At its start a run creates `runs/<run id>.json`, in a way that fails when the file exists, and removes it after its final event. The record holds the run's identifier, its owner, its Subscription, when it started, the caller's labels, the chat key and the vendor tool's conversation it uses, and, once the vendor tool is running, that tool's process and start time.

The record is how other calls learn about the run:

| Another call wants to | It does |
|---|---|
| Use a run identifier | Finds the file. With a live owner the identifier is refused with `in_use`. With a dead owner the leftovers are cleared first (below) |
| List the runs (`runs list`) | Reads the records and returns those whose owner is alive |
| Stop a run (`runs stop`) | Sends the owner the termination signal and waits until the record is gone, for at most 20 seconds. The owner stops its run as DRV-2.16 says. A record with a dead owner is cleared; a run that is not there counts as stopped |
| Sign a Subscription out or remove it, forced | Stops every run whose record names that Subscription, in the same way, then goes on (DRV-1.12) |
| Continue a saved conversation | Looks for a live run that names the same conversation. If there is one, it does not wait: it builds a new conversation (below) |

Files that live as long as the run are in `tmp/<run id>/`: the empty working folder of a run that was given none, and pictures the vendor tool needs as files. The folder goes with the run.

### A sign-in in progress

A `sign-in` command writes `sign-in.json` with its owner and the time the attempt ends, and removes it when the attempt is over. A second `sign-in` for the same Subscription that finds a live owner sends it the termination signal, waits up to 5 seconds for the file to go, and then starts its own attempt. The first command ends with a `failed` step whose error is `in_use`, saying that another sign-in took its place.

### Leftovers of a killed call

A call that is killed outright cannot tidy up. The next call that comes across its traces does it:

| Trace | What is done |
|---|---|
| A run record with a dead owner | If the vendor tool's process it names is still alive, that process and everything it started are ended. The run's folder under `tmp` is removed, then the record. The entry of the map that the run was continuing is removed, as after any run that did not complete |
| A `sign-in.json` with a dead owner | Removed. The Subscription is then `signed_out`, or whatever its record says |
| A `lock` with a dead owner | Taken over |
| A temporary file of an unfinished write | Removed when it is older than one minute |

Every `run`, `runs list`, `runs stop` and every command that changes a Subscription looks for these traces before it does its own work.

### The map of chat sessions

For every chat session that completed a run on a Subscription there is one file, `chats/<chat key>.json`, in that Subscription's folder. The chat key is the SHA-256 of the caller's chat session identifier, written in hexadecimal, so that any identifier makes a valid file name.

The entry says which saved conversation of the vendor tool belongs to the chat session and what that conversation covers:

| Field | Meaning |
|---|---|
| The chat session identifier | As the caller named it |
| The conversation | The vendor tool's own identifier of the saved conversation |
| The working folder | The real path the run worked in. `claude` files its conversations by folder |
| Messages | How many messages the conversation covers, the user's and the replies, those of the last run included |
| Digest | A fingerprint of those messages in order: their text, and the pictures of the user's messages |
| System prompt digest | A digest of the system prompt the conversation was last run with |

No message is in the map, only counts, digests and identifiers.

**Whether a saved conversation still fits.** A run continues the saved conversation only when all of these hold. Otherwise it builds a new one from the caller's history and says why in `started`:

| Check | Reason given when it fails |
|---|---|
| The request names a chat session | `no_chat_session` |
| An entry exists for it on this Subscription | `first_run` |
| The messages of the history, the user's and the replies, are as many as the entry counts and have the entry's digest | `history_differs` |
| The working folder is the entry's | `working_folder_changed` |
| The system prompt has the entry's digest. Checked only by a Driver whose vendor tool keeps the first prompt of a conversation it continues (DRV-D31) | `system_prompt_changed` |
| The vendor tool still has the conversation | `conversation_gone` |
| No other run in progress uses the conversation | `in_use` |
| The vendor tool accepts continuing it | `resume_refused` |

The history check finds an edited, removed or branched message of the user. It also finds a reply that was replaced while no message of the user changed, as when a reply was made again on the other Driver. For that the caller hands the text of every reply back exactly as the run's `text` events carried it (DRV-2).

The digest is the SHA-256, in hexadecimal, of the JSON text of a list with one entry per message, in order: its role, its text, and for a message of the user one pair per picture of its media type and the SHA-256 of the picture's bytes. Replies that follow one another with no message of the user between them count as one message, their texts joined with nothing in between, so it does not matter into how many pieces a reply was split. Tool calls are not part of the digest. The system prompt digest is the SHA-256 of the prompt's text. Each message entry in the JSON list is `[role, text]` for an assistant and `[role, text, [[mediaType, imageDigest], …]]` for a user, with an empty picture list when it has none. JSON has no added whitespace; text is UTF-8. Assistant messages separated only by tool calls are joined too.

**Writing and removing an entry.** An entry is written when a run has completed, and only then: it names the conversation the run used and covers the history, the run's own message and the text of the run's reply. A run that ends in any other way removes the entry it was continuing, if that entry still names the same conversation, so that the next run builds the conversation again. When two runs of one chat session complete, the later one's entry stands.

### What the Driver remembers about the vendor tool

`tool.json` holds the path of the vendor tool's program, the size and the change time of that file, and the version the program stated. A call that needs the version uses the stored one as long as path, size and change time are unchanged, and otherwise runs the program to ask. The path comes from `toolPath` in the settings file, or else from the search path (DRV-0).

## SYL-92 verification, 7 October 2026

SYL-92 passed the complete 38-scenario shared registry for both Python Drivers. Codex also passed 128 unit methods, Ruff and strict mypy from source; its standalone CPython 3.14.8 development candidate passed the same units and all 38 scenarios, and its relocated copy passed metadata and unit checks under a minimal environment. A fresh packaged `dev probe` passed against codex-cli 0.159.2 with zero inference requests. The packaged build gate sent exactly one no-tools ready message through `test-chatgpt`; it completed and reported tokens and usage before/after. The extended five-turn `dev live-check` orchestration and refusal gates passed offline, but the extended vendor run was not requested. Contract and state format remain 1. The first numbered Codex Build is the separate SYL-94 task.

Current records and source/package provenance: `~/Artifacts/arbol-codex-driver/research/conformance-2026-10-07/verification.json`, `coverage-audit.json`, `packaged-probe.json` and `packaged-build-check.txt` in that folder. Dated migration and TypeScript evidence below remains historical; unobserved real vendor failures remain unobserved. The coverage audit retains every former Verified by cell before this update.

## Requirements

| ID | A Driver must… | Origin | Verified by |
|---|---|---|---|
| DRV-6.1 | keep its files in the layout above, under the state directory alone, readable by the owner only, and treat a missing file or folder as empty | New | Claude Python: `C38`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C38`, `Foundation.test_state_private_layout_higher_format_and_safe_ids` |
| DRV-6.2 | write every durable state file whole, by writing a temporary file in the same folder and renaming it | New | Claude Python: `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `Foundation.test_atomic_write_failure_cleanup_and_no_symlink_traversal` |
| DRV-6.3 | write the data format number when it creates the state directory, and do nothing but fail with `state_newer` when it finds a higher number than it knows | New | Claude Python: `C38`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C38`, `Foundation.test_state_private_layout_higher_format_and_safe_ids` |
| DRV-6.4 | hold a Subscription's lock only while it rewrites that Subscription's record, never across a request to the vendor, a run of the vendor tool or a sign-in | New | Claude Python: `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C2`, `C18`, `C38`, `ConformanceState.test_another_subscription_changes_while_first_lock_is_held` |
| DRV-6.5 | wait for a taken lock in steps of 50 milliseconds, take over a lock whose owner is dead, and fail with `internal` after 10 seconds | New | Claude Python: `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C38`, `ConformanceState.test_another_subscription_changes_while_first_lock_is_held`, `ConformanceState.test_taken_lock_polls_every_50ms_and_fails_after_10s_with_owner`, `Foundation.test_state_lock_serializes_and_reclaims_dead_owner` |
| DRV-6.6 | name the owner of every lock and of every record of something in progress by process identifier and start time, and count an owner as alive only when both match | New | Claude Python: `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C6`, `C38`, `Foundation.test_state_lock_serializes_and_reclaims_dead_owner`, `ProcessGroupTests.test_same_owner_requires_pid_and_start_time_with_two_second_tolerance` |
| DRV-6.7 | keep `runs/<run id>.json` from the start of a run to its final event, created so that a second run with the same identifier fails | New | Claude Python: `C33`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C33` |
| DRV-6.8 | stop a run of another call by sending its owner the termination signal and waiting until its record is gone, for at most 20 seconds | New | Claude Python: `C33`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C33`, `Lifecycle.test_control_signals_eof_and_peer_stop_interrupt_once_then_cleanup` |
| DRV-6.9 | end a pending sign-in of another call in the same way before starting its own, and end a replaced sign-in with a `failed` step whose error is `in_use` | New | Claude Python: `C2`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C2`, `Accounts.test_login_replacement_cancels_pending_and_sign_out_clears_credentials` |
| DRV-6.10 | clear the leftovers of a killed call, as the table above says, before a `run`, `runs list`, `runs stop` or a change to a Subscription does its own work, ending a vendor tool that outlived its Driver | New | Claude Python: `C38`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C38`, `Foundation.test_atomic_write_failure_cleanup_and_no_symlink_traversal`, `Foundation.test_continuity_selection_order_conditional_settlement_and_killed_owner` |
| DRV-6.11 | keep one entry of the map per chat session and Subscription, in a file named after the SHA-256 of the chat session identifier, holding the fields above and no message | New | Claude Python: `C14`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C14`, `Foundation.test_continuity_selection_order_conditional_settlement_and_killed_owner` |
| DRV-6.12 | continue a saved conversation only when every check of the table above holds, and otherwise build a new one and give the first reason that failed, in the order of the table | New | Claude Python: `C14`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C14`, `Foundation.test_continuity_selection_order_conditional_settlement_and_killed_owner` |
| DRV-6.13 | compute the digest of the messages and the system prompt digest as stated above | New | Claude Python: `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C14`, `Foundation.test_migration_golden_vectors_and_nonmutating_stream_snapshots` |
| DRV-6.14 | write an entry of the map only after a completed run, and remove the entry a run was continuing when that run ends any other way and the entry still names the same conversation | New | Claude Python: `C14`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C14`, `Foundation.test_continuity_selection_order_conditional_settlement_and_killed_owner` |
| DRV-6.15 | never wait for another run that uses the same saved conversation: build a new conversation instead | New | Claude Python: `C14`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C14`, `Foundation.test_continuity_selection_order_conditional_settlement_and_killed_owner` |
| DRV-6.16 | ask the vendor tool's program for its version only when its path, size or change time differs from what `tool.json` holds | New | Claude Python: `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `ConformanceState.test_version_cache_reuses_unchanged_tool_and_invalidates_path_size_and_mtime` |

## Interface

```ts
interface Owner { pid: number; startedAt: string }      // the process, and when it was started

// subscriptions/<id>/record.json: Subscription (DRV-1) without `settings`; `state` is never "signing_in"
type SubscriptionRecord = Omit<Subscription, "settings">;

interface LockFile { owner: Owner }                      // subscriptions/<id>/lock

interface SignInRecord {                                 // subscriptions/<id>/sign-in.json
  owner: Owner;
  expiresAt: string;
  attempt?: string;                       // token distinguishing successive account operations
  byCode?: boolean;                       // device-code login does not reserve the local callback
  operation?: "sign_in" | "sign_out" | "remove"; // absent means sign_in; other operations reserve credential changes without a long-held lock
  stopReason?: "replaced" | "signed_out";  // set under the Subscription lock before signalling
  tool?: Owner;                         // allows a later call to end an orphaned login child
}

interface RunRecord {                                    // runs/<run id>.json
  runId: string;
  owner: Owner;
  subscriptionId: string;
  startedAt: string;
  labels?: Record<string, string>;
  chatKey?: string;                                      // absent when the request named no chat session
  conversation?: string;                                 // the vendor tool's conversation the run uses
  tool?: Owner;                                          // the vendor tool's process, once it runs
  continuedConversation?: string;                        // the prior map entry to invalidate on failure or recovery
  cleanupOwner?: Owner;                                  // a call recovering a killed run, elected under the Subscription lock
}

interface ChatEntry {                                    // subscriptions/<id>/chats/<chat key>.json
  chatSessionId: string;
  conversation: string;
  workingDirectory: string;                              // real path
  messages: number;                                      // the user's and the replies, joined as stated above
  digest: string;                                        // SHA-256, hexadecimal
  systemPromptDigest: string;                            // SHA-256 of the text; of the empty text when there is none
  writtenAt: string;
}

interface ToolRecord {                                   // tool.json
  path: string;
  size: number;
  changedAt: string;
  version: string;
  askedAt: string;
}
```

Beside them, in DRV-2: `started.rebuildReason` is one of the reasons in the table above. In DRV-4: the error code `state_newer`.

## Known problems in version 1

Not to be reproduced.

- **Everything was in the memory of a process that had to stay alive.** A restart lost the running turns, and a second copy of a Driver during an upgrade needed a protocol of its own to hand them over.
- **Leftovers were nobody's job.** One saved session per attempt was never read again and never removed, and commands the Codex route had started were left running on purpose.
- **One lock, held too long, stopped everything.** Root collected the answers to all open questions before it delivered any.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:daemons/shared/arbol_shared/turn_store.py#TurnStore`
- `arbol_deprecated_v1:drivers/codex/arbol_driver_codex/tool_process.py#ToolProcess._cleanup`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#6. Many resident services with strict, version-coupled contracts`

## Python migration compatibility, 7 October 2026

SYL-95 records the TypeScript baseline at Claude 5ea45f2 and Codex 37daaf8, with golden history/snapshot/path/Keychain vectors generated using Node 24.21.0. The Claude baseline hashes adjacent assistant blocks containing separate halves of one UTF-16 surrogate pair differently from the same complete Unicode message; Codex already buffers the trailing half. Python uses the complete-message digest for that case, retaining the legacy result as an explicit regression fixture rather than reproducing the defect. A previously saved Claude entry with that defective digest is safely rebuilt with the existing history_differs reason; its JSON state shape is unchanged. All other golden vectors retain exact TypeScript bytes/digests, including isolated surrogates, controls and decoded image bytes. This corrects message-block merging required by DRV-2 and changes neither contract 1 nor state format 1. Python recovery also rechecks both the claimed reservation and cleanupOwner before releasing or deleting a stale run record; the Claude baseline could otherwise remove a newer writer after cleanup. This enforces the existing conditional-state rule, keeps the same JSON records, and has a regression test that replaces the run record during cleanup.

## Python migration verification, 7 October 2026

SYL-95 verification is recorded in the requirement-level `~/Artifacts/arbol/driver-contract/python-migration-coverage-2026-10-07.json` and the Driver records `research/python-migration-2026-10-07/verification.json`. Python check names identify the copied standard-library unittest suites and the unchanged shared scenarios. Prior Driver unit/probe/live names refer to historical TypeScript evidence; unchanged shared build-tool and runner names remain active. Claude passes the complete 38-scenario suite; Codex passes its five original scoped groups (29 scenario invocations, with the same exclusions), and remains a development candidate. No historical live result is treated as fresh Python evidence, and previously unobserved vendor failures stay unobserved.

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| DRV-D40 | How do simultaneous calls recover a killed run safely? | A short Subscription lock elects cleanupOwner in the run record; cleanup runs outside the lock. Other calls wait for that cleanup or take it over if its owner died. Under the lock, remove only the map entry matching continuedConversation, then remove the run record after its processes and temporary folder. Record the tool owner as soon as it starts and also publish its identity from its shell launcher before exec, so death while the Driver discovers the child leaves a recoverable identity. Scratch launchers and the shell ledger may be text files; durable state remains JSON | Decided 7 October 2026 during SYL-83, a technical choice |
| DRV-D39 | How are continuity digests and simultaneous resumes made deterministic? | Use the message tuples stated above. Under the Subscription lock, read the map, choose the conversation and publish the run record that reserves it; release the lock before starting the tool. Under that same short lock, write a completed map entry or conditionally remove the entry that a failed run continued | Decided 7 October 2026 during SYL-82, a technical choice |
| DRV-D38 | How are sign-in replacement and late vendor answers coordinated? | Reserve sign-in.json under the Subscription lock for sign-in, sign-out or removal; only a sign-in reservation presents the state signing_in; set stopReason before signalling its owner, then wait outside the lock. The owner checks this reason before storing a result. Record the login child owner for cleanup after a killed command; attempt files live in tmp/sign-in-<subscription id>. A status or usage answer updates only the record revision it checked, so a late answer cannot restore a signed-out account. Removing an initial family Subscription clears its stored data and leaves its implicit signed-out record available | Decided 6 October 2026 during SYL-78, a technical choice |
| DRV-D36 | How are base state errors and process identities read? | A malformed `format` or progress record fails with `internal`, without its contents in the error. On macOS and Linux, process start times come from `/bin/ps` with a clean environment and the C locale. A lock is published by linking a complete temporary owner record into place, failing if `lock` exists, so no reader sees a half-written owner | Decided 6 October 2026 during SYL-75, a technical choice |
| DRV-D28 | How does a Driver notice that the last answer of a chat was replaced, when no message of the user changed? | The caller stores, with each answer and tool call, the identifier of the run that produced it, and hands it back in the history. The Driver compares the last one with the run its saved conversation ends in. Without it a chat that had its last answer made again on the other Driver would be continued with the old answer | Withdrawn 6 October 2026. The owner had understood the fingerprint to cover the whole conversation, so the text of the replies became part of it (DRV-D10), and no run identifier is needed (SYL-72) |
| DRV-D29 | How do calls that run at the same moment keep out of each other's way? | A lock file per Subscription, created so that a second creation fails, held only while one record is rewritten. Whatever lasts is a record naming its owner, never a lock. File locks of the operating system are not used: Node.js offers none without an add-on | Decided 6 October 2026, a technical choice made in drafting on the owner's go-ahead |
| DRV-D30 | How does one call reach another that is already running? | By the termination signal, sent to the process named in the record of the run or of the sign-in. A Driver already stops its run on that signal (DRV-2.26), so nothing new is needed | Decided 6 October 2026, a technical choice made in drafting on the owner's go-ahead |
| DRV-D31 | Is a saved conversation continued when the system prompt has changed? | Where the vendor tool takes the new prompt, yes. Where it keeps the first one, a new conversation is built, which is always right and costs the tool's own record of the conversation | Decided 6 October 2026 by the real test that SYL-30 listed, a technical choice. `claude` takes the new prompt when it is started with `--system-prompt-snapshot off`, so the Claude Driver continues. `codex` kept the first prompt whatever `thread/resume` was given, so the Codex Driver rebuilds |

## Real existing profiles for qualification · 12 November 2026

The owner prohibited test profiles and required real existing profiles. Probes and live qualification select an existing real provider profile and Subscription ID directly. Discover and verify that selection before inference. The gate must refuse a missing or signed-out selection. Creating a test profile, creating a profile alias, copying authentication or starting a new sign-in to satisfy qualification is prohibited.

Keep application database, runtime, Build registry and evidence disposable and separate from provider profile selection. A real live run uses the existing profile's native credential binding and records its actual inference, completion and usage outcome. Keep the complete documented Build gates. Earlier test-profile decisions and qualification records remain historical evidence of their original releases.

## Identity format 2 and maintenance boundary · 14 November 2026

This amendment governs the new Browser producer; earlier format-1 descriptions and verification remain historical/current legacy compatibility. Identity-qualified new state is format **2**. Ordinary new Builds may read/write existing format 1 under its original rules, but cannot emit positive identity proof from it and never auto-upgrade it. No new field is added to the old `record.json` shape. All format-2 writers, including auth verdict/usage/delayed completion/recovery paths, preserve the proof sidecars and use the admission rules below. New normal state starts at format 2; ordinary list may initialize state as before, but never materializes a witness.

```text
<state directory>/
  format                         2, durable publication fence
  identity.json                  {version:1,generation:<32-byte token>}
  identity.guard                 stable inode for OS shared/exclusive admission lock
  identity-upgrade.json           present only during offline 1 -> 2 conversion
  subscriptions/<canonical id>/
    identity.json                {version:1,witness:<32-byte token>,state:"active"|"retired"}
    identity-pending.json        interrupted local create/remove settlement, when needed
    record.json                  existing Driver-specific shape, no witness/auth coupling
    lock                         existing short per-Subscription lock
```

The two `identity.json` forms are strict objects with exactly the fields shown; version is integer 1 and tokens obey DRV-1.28. Bound files to 4096 bytes and retain existing private permissions/symlink/ownership protections. A missing/invalid root identity in format 2 is a refusal, never regeneration on an ordinary read. Missing Subscription identity may be materialized under its short lock with a fresh random witness after a valid local record/built-in is established. A retired sidecar for a currently absent nonbuilt-in yields `not_found`; a newly created record or reappearing permitted built-in replaces it with fresh active evidence. Missing sidecars cannot recover or guess old proof.

### Admission, publication and races

Every format-2 invocation holds a shared OS lock on the stable `identity.guard` inode from before reading root generation/format until its last state effect/output. Recheck the format and generation after acquiring it. Offline upgrade, reset and restore take the exclusive lock, which prevents overlap with **all** admitted new invocations, not only recorded runs. Keep the guard inode for the state's lifetime; never unlink/replace it while admitted invocations exist. This is a maintenance admission gate, not a Subscription record lock; it may span a vendor operation, but never permits a Subscription lock across one. Within it, use only existing short per-Subscription locks for record/proof mutation. Normal unrelated Subscription operations remain concurrent under shared admission.

Under a Subscription lock, identity capture reads the active sidecar; only a valid current local record or implicit built-in can get one. Create publishes its witness before success. Remove first honors native refusal and run/sign-in handling; when removal becomes locally committed, retire its witness and commit record deletion before success. Publish a strict `identity-pending.json` transaction record before a multi-file create/remove change: `{version:1,operation:"create"|"remove",witness:<token>,phase:"prepared"|"committed"}`. With that record present, identity refuses and ordinary same-Subscription mutation must settle recovery under the same lock. Create recovery either finishes the valid new record with that exact witness or leaves the selector absent/retired; it never acknowledges a different lifetime under the same proof. Remove recovery completes retirement/deletion only after the operation's existing credential/native cleanup has a proven successful outcome; otherwise preserve unavailability pending the concrete conservative `identity-recover` operation below, never automatically reactivate an ambiguous witness. Clear the journal only after all required writes/deletions and directory fsyncs are durable. No witness from an uncommitted create or ambiguous remove can be emitted as successful proof. Producer plans must map this journal to each Driver's existing operation receipt; no vendor work occurs under the short lock.

Atomic file publication means write temporary file, fsync file, atomic rename, fsync parent; deletion likewise fsyncs its parent. Serialize witness capture, materialization, expected-proof comparison, create/remove commit and recovery on the same canonical Subscription lock. Late auth/usage updates carry the captured witness internally and discard their write when the current lifetime differs or is pending/retired; an old completion cannot recreate a removed record or transplant its proof. Auth sign-out/reattachment keeps proof even if auth metadata is replaced wholesale.

### Offline upgrade and compatibility

The explicit administrative command is `state upgrade --from-format 1 --confirm-quiescent --maintenance <absolute-receipt> --backup <absolute-empty-directory>`, with the common absolute `--state-dir`. It returns `{version:1,format:2,generation:<token>}`, exit 0, only when complete; repeated invocation on valid format 2 returns that same generation. Wrong source format/arguments return `invalid_input`, newer format `state_newer`, incomplete/unsafe conversion `internal`. This command changes no credential, vendor home, settings, chat map or application database.

`--confirm-quiescent` records the caller's maintenance assertion; it is **not** an autonomous guarantee that legacy calls stopped. The supported provider is the shared Build launcher/maintenance implementation allocated to ABR-39 below, not an unspecified external service. Administrative upgrade/reset/restore/recovery is unavailable if that provider's exact closed-and-drained handoff cannot be verified. Normal `subscriptions identity` capture/compare instead uses ordinary qualified-launch shared admission while the component is normal; it requires no maintenance receipt and remains usable after reopening. A scan of run files alone never supplies it. No online/automatic format-1 upgrade is supported. ABR-34–37 implement the receipt check and local conversion; ABR-39 implements launch closure/custody/drain; ABR-38 qualifies their composition. Production activation requires concrete maintenance scope; this corpus work activates nothing.

The required backup destination is private, absolute, outside the state tree and initially empty for a **new** attempt. A resume may reuse only the exact immutable backup named/hash-bound in its durable journal/result; mismatched reuse refuses. Before changing `format`, copy only the files this operation can change (`format` and preexisting identity/journal metadata) into an immutable numbered backup entry, with a relative-path/type/size/SHA-256 manifest and recorded source format. Do not read/copy vendor homes, credential stores, old per-Subscription `home/` trees, account values or chat contents; upgrade leaves their files untouched. Stage the new root identity and journal in private temporary files with fsync before the format fence. Preserve the manifest and every failed attempt; refuse mismatched backup reuse or a nonempty destination for a fresh attempt. Resume verifies the exact backup and staged generation rather than overwriting them. This is recoverable metadata conversion, not a credential/state export.

Take exclusive `identity.guard`, recheck format and absence of active owned work, then durably write `identity-upgrade.json` as `{version:1,from:1,to:2,generation:<fresh token>,backup:<absolute path>,backupSha256:<manifest SHA-256>}` and publish `format` as 2 **before any proof sidecar**. This immediately fences later old Builds (`state_newer`). Finish root identity and per-record validation; no legacy record is assigned the proof of an earlier application binding. Per-Subscription sidecars can be lazily materialized by identity after completion. Fsync and remove the upgrade record last. A crash before the format fence leaves unchanged format 1 with a pending offline upgrade; the same explicit command resumes that journal/generation under the external fence. A crash after the fence leaves format 2 plus journal: ordinary new operations refuse, old Builds refuse, and only the explicit command completes the same generation. Do not delete a marker or lower `format` to make an old writer accept converted state. Failure preserves the backup and blocked state. Recovery after conversion requires an explicit offline restore/reset below, never piecemeal copying sidecars.

The format marker alone cannot fence an old process that already passed format-1 admission; that is why the external stop/launch fence is a hard supported-upgrade precondition. All pre-identity Builds are unqualified for writing format 2. Gate tests must include old readers/writers refusing format 2 before mutation and interrupted conversion remaining blocked, not merely new readers ignoring unknown fields. The contract does not claim compatibility with a legacy process deliberately launched past the documented fence.

### Supported restore/reset and observability

The administrative command `state identity-reset --confirm-quiescent --maintenance <absolute-receipt>` takes the same external maintenance fence and exclusive admission lock. On valid format 2 it durably replaces only root generation with a fresh token and returns `{version:1,format:2,generation:<new token>}`; each successful invocation rotates, including after interrupted acknowledgement. Existing witnesses/auth state remain; the changed equality key invalidates every old accepted mapping. Format-1 input requires upgrade first. An incomplete/unsafe state refuses and must be recovered offline from the preserved backup; no normal identity/list operation repairs root identity.

Every **supported** Driver state restore/reset/copy into an admitted installation runs identity-reset after file restoration and before releasing admission, even when the copied files look identical. Restoring to a fresh location starts a fresh root generation before use. Preserve the guard/fence while replacing restored payloads; do not publish a restored guard inode. An Arbol application-database restore/reset also invalidates all restored proof mappings/bindings (`needs_rebind`) under its existing database maintenance fence before Backend admission; it cannot reuse matching restored proof rows as authority. The Backend continuation in ABR-17 owns that integration. If a route cannot prove the invalidation completed, its Browser binding admission remains refused; standalone ordinary Browser remains independent. Release tooling must name every supported entry point; an undocumented manual file copy is not retroactively certified as a supported restore.

An unobservable byte-for-byte rollback of **all** authorities and maintenance evidence cannot be detected from those same restored files. There is no anti-rollback anchor here. This observability limit does not waive invalidation for a restore/reset the supported tool/caller knows occurred, and does not permit claiming unknown legacy continuity. No stronger guarantee or owner-only backup policy is invented by this amendment.

| ID | Requirement | Origin | Verified by |
|---|---|---|---|
| DRV-6.17 | implement format-2 root/per-Subscription evidence, private durable publication, short-lock materialization and transaction recovery; ordinary format-1/list paths do not assert proof | DRV-1.28/.29; BRW-D32 | pending ABR-38 |
| DRV-6.18 | fence format-2 invocations and maintenance, require exclusive offline legacy conversion, preserve backups and crash journals, and make old Builds refuse before proof can be discarded | BRW-1.14 | pending ABR-38 offline conversion/old-writer qualification |
| DRV-6.19 | rotate the root generation before supported restored/reset Driver state is admitted and require consumer invalidation on known application restore; preserve refusal and state on uncertainty | BRW-1.11/.14 | pending ABR-38 producer and ABR-19 application restore qualification |
| DRV-6.20 | preserve lifetime evidence across all auth/usage/recovery writes, discard stale lifetime completions and serialize identity/remove/recreate races without vendor work under the Subscription lock | DRV-1.29 | pending ABR-38 |

### Existing format guards

Codex and Claude initialize by checking their format file before normal state preparation; Pi checks higher formats before chmod/mkdir; Mimo checks through its descriptor-based root access. None currently implements the new shared admission guard or identity journal. Therefore adding a file without the format fence would leave silent legacy writers unsafe. ABR-34–37 own the new guards and all their writer call sites; ABR-38 must qualify old/new combinations.

<!-- sources:
arbol-codex-driver:src/arbol_codex_driver/state.py#State.initialize
arbol-claude-driver:src/arbol_claude_driver/state.py#State.initialize
arbol-pi-driver:src/arbol_pi_driver/state.py#State
arbol-mimo-driver:src/arbol_mimo_driver/state.py#Store
-->


### Shared launcher maintenance provider and supported entry points

This is a new implementation obligation, **not a capability of today's launcher**. ABR-39 owns `arbol:src/arbol_builds/launcher.py`, `service.py`, `cli.py` and a new `driver_state.py` helper, plus short-booked package metadata/copy rules required to deliver it. The current launcher source is copied by `service.write_launcher` into installed component launchers and ultimately calls `os.execv`; its existing Build-use fd is not sufficient lifetime custody for this protocol. ABR-39 must preserve explicit `-v`, default selection, inherited environment, exit status, signal/EOF behavior and interactive TTY/stdin/stdout/stderr semantics while providing the gate. It may not assume an old Driver forwards a new fd to its vendor helpers.

The gate is component-wide, under `<registry>/<component>/.driver-admission/` for each of the four exact Driver component names. It therefore covers every `--state-dir`, relative argument form, default state and old `-v` Build selected through that component launcher, without parsing an old Build's options. Use private stable OS lock inodes and durable strict control state `{version:1,phase:"normal"|"draining"|"exclusive",session:<random token or null>,epoch:<random token>}`. Control publication and launch registration share a short control mutex: a launch cannot pass a normal check and register after draining starts. Missing/invalid authority after gate installation refuses launch. No new invocation, including an old explicit Build, starts while draining/exclusive; return a bounded existing launcher `launch_failed` error before running component code.

Each accepted launch publishes a durable owner/custody record before child execution, naming its random invocation id, exact selected payload/Build, PID+kernel start identity, execution group/session, guardian and independent watcher. Hold shared component admission through the entire observed Driver/vendor/helper lifetime. The guardian is a real lifetime supervisor, not a descriptor inherited only by the main: it must keep an independently owned watcher/custody record when that main or the launcher dies. Signal forwarding/TTY handling preserves the original CLI contract. Driver removal of a run file or death of the main process is not exit evidence for vendor/helper descendants. A remaining custody record, lost observation, escaped/unresolved owned group or dead guardian with unknown descendants blocks maintenance until verified cleanup. Never signal an unrelated/reused PID or accept an empty freshly created inventory over unresolved records. ABR-39's cold implementation plan must identify the concrete process-observation/containment mechanism supported on the target OS before coding; unavailable containment means refusal, not invented proof.

The administrative interface is local `arbol-builds driver-state`:

- `begin --component <driver-component> --session <canonical-uuid>` durably closes launch admission (`draining`) before waiting for existing custody. It returns one bounded JSON status (`version:1`, `component`, `session`, `phase`) and does not cancel work implicitly. A repeated same session resumes; another session refuses. The component's installed gate/payload manifest is verified first.
- `drain --component ... --session ... [--stop]` verifies exact owners/groups/watchers and waits at most 20 seconds per call. Without stop, live work remains draining. With explicit `--stop`, use the Driver's normal cancellation/control first and its existing bounded escalation rules; no inference replay, auth/store mutation or unverified broad process kill. Persist unresolved custody and remain draining on timeout/uncertainty. Only complete verified child/helper exit and exclusive acquisition of component admission allows `exclusive` and a private `maintenance.json` receipt, at most 4096 bytes, containing `version:1`, component, session, current epoch, `phase:"exclusive"` and exact gate/payload manifest SHA-256.
- `execute --component ... --session ... --build <exact-build> --state-dir <absolute-path> --operation upgrade|identity-reset|restore|identity-recover --backup <absolute-empty-directory> [--source <absolute-metadata-backup>]` validates the exact qualified payload/capability manifest and live exclusive lease, then runs only its matching administrative operation with the inherited maintenance context. Upgrade forwards the specified from-format/quiescent/backup arguments. Restore accepts only this protocol’s private metadata backup with manifest verification, preserves native/credential files and live guards, then follows the exact format1/2 recovery route below. Capture the child’s bounded successful result into a private durable result receipt bound to component/session/epoch/payload/state-directory digest; emit its absolute receipt path, not account data. Unknown operations, missing source for restore or any nonmatching payload/lease refuse before mutation. A pending valid conversion normally resumes through upgrade with its original backup/journal. Explicit restore recovery may conservatively abandon that attempt only by the durable closed-fence procedure below; it never deletes a journal and reopens the old proof.
- `status --component ... --session ...` reports current phase/custody summary without changing it. `finish --component ... --session ... --result <absolute-result-receipt>` verifies completed local upgrade/reset/restore receipt and exact maintenance epoch, absence of pending conversion/custody and all required durable state checks before atomically reopening with a fresh gate epoch. Failed/missing result leaves the fence closed. No bare `--force` or marker deletion opens it.

All commands return one JSON document, bounded to 4096 bytes; failures use the existing launcher/tool error shape and nonzero exit, never a success-shaped empty receipt. Session ids are canonical UUIDs; components are the fixed four Driver names. Results include no account/credential/argv values. A receipt alone never grants mutation. Each administrative command reacquires the exclusive component OS lease and verifies matching control epoch/session plus unresolved custody before acting; no process is required to retain that lease between one-shot commands. Durable draining/exclusive control blocks all intervening normal launches. A maintenance receipt becomes a live child handoff only during `execute`, while its parent retains that exclusive lease. The shared helper passes a narrowly scoped inherited maintenance fd/context only to the exact selected qualified Driver upgrade/reset child; the Driver validates that descriptor, control state, registry/component and receipt bytes before mutation. It does not trust an arbitrary JSON file, environment variable, PID or `--confirm-quiescent` alone. Supervisor loss preserves closed control state; a same-session recovery re-verifies/drains custody and reacquires the exclusive lease before resuming the exact upgrade journal. Old/current state results cannot reopen a later session. The driver-state helper itself is the sole authorized invocation path during exclusive admission and is not blocked by its own launch gate.

Supported production entry points are the registered named/default Build launchers, App/backend invocations through those launchers, and the driver-state helper invoking the exact immutable qualified payload for upgrade/reset/restore. The initial gate deployment is an explicit maintenance operation: stop and disable the known App/backend/automation callers, inventory and terminate/settle pre-gate launchers/Drivers and their proven vendor/helper ownership using existing component procedures, atomically install/verify all four gate launchers, then establish their custody baseline and re-enable callers only after the gate passes qualification. Save prior launchers/Build selections privately. Gate installation does not make an already running pre-gate process observable retroactively. Unresolved pre-gate work blocks upgrade; its absence must be independently observed against the stopped-caller process/group inventory. ABR-39 implements this deploy/preflight procedure and manifest checks; ABR-38 qualifies it on disposable processes. Owner-state deployment remains under later explicit operational scope.

Direct invocation of an extracted old binary, copied old launcher, manually replaced gate, arbitrary same-user file edits or unknown external callers deliberately bypassing the documented rollout are outside this supported launch boundary. The contract cannot prevent a same-user program doing that. It must state this limit while preserving the real usable installed-launcher upgrade route. A supported tool must never choose a bypass to escape a refusal. Fresh isolated format-2 producer tests can use their own qualified gate registry and state without installing anything normally.

Supported Driver restore/reset is the same closed/drained helper route: restore only declared Driver-owned metadata, leave native credential stores/homes intact, retain the live guard inode, rotate root generation through the exact qualified payload, verify its durable result, then finish the component fence. A restored/copy payload cannot contain authoritative maintenance receipts or reopen control. Arbitrary native/vendor backup restore is not a new Driver-owned entry point.

| ID | Requirement | Origin | Verified by |
|---|---|---|---|
| DRV-6.21 | supply the concrete shared installed-launcher maintenance gate, complete old/current Driver-helper lifetime custody and verified drain, epoch-bound maintenance handoff, recoverable rollout and fail-closed reopen before format conversion/reset/restore | DRV-6.18/.19; BRW-1.14 | pending ABR-39 implementation and ABR-38 composition/old-Build/helper-death qualification |

<!-- sources:
arbol:@code/src/arbol_builds/launcher.py#launch
arbol:@code/src/arbol_builds/launcher.py#hold_build_use
arbol:@code/src/arbol_builds/service.py
-->


### Exact maintenance handoff and command lifetime

The following wire boundary is shared by ABR-34–37 and39. All protocol JSON is UTF-8, one strict object, no duplicate keys, maximum 4096 bytes per document, integer version 1, no additional fields in persisted control/receipt/context objects. Canonical serialization for SHA-256 is sorted object keys, no insignificant whitespace, UTF-8, one trailing LF. Token fields are the canonical 32-byte base64url encoding from DRV-1; SHA-256 fields are 64 lowercase hex characters. Paths are bounded absolute canonical physical paths under the verified private registry/state/backup roots, never symlinks. JSON validation errors refuse without printing values.

`maintenance.json` is exactly `{version:1,kind:"driver-state-maintenance",component:<one of four Driver component names>,session:<canonical UUID>,epoch:<token>,phase:"exclusive",gateSha256:<hex>}`. It is a durable receipt of drained admission, **not a held lease**. `begin`, `drain`, `execute` and `finish` each independently acquire the short control mutex, check the session/epoch, and acquire/recheck the relevant admission lease before mutation. `drain` can publish exclusive only with complete custody already resolved and an exclusive component lease; it releases its lease after publishing the receipt, while durable exclusive phase continues refusing launches. `execute` reacquires that exclusive lease and fresh custody verification; `finish` does the same. A crash between commands keeps the durable closed phase. Same-session commands can resume; another session cannot overwrite it. No resident service is added.

During `execute`, the supervisor retains the exclusive component admission descriptor and passes a duplicate referring to the **same locked open-file description** to the selected qualified child, with close-on-exec cleared only on that duplicate. `ARBOL_DRIVER_MAINTENANCE_FD` is its canonical decimal descriptor number (3 or greater). `ARBOL_DRIVER_MAINTENANCE_CONTEXT` is the absolute path of a private context file, not JSON in argv/environment. Clear any inherited versions before constructing this pair. The context is exactly `{version:1,kind:"driver-state-context",component,session,epoch,gateSha256,payloadSha256,stateDirectory,operation,attempt,receiptSha256}`. Operation is `upgrade`, `identity-reset`, `restore` or `identity-recover`; attempt is a fresh token, stateDirectory is the canonical physical path and receiptSha256 hashes the exact verified maintenance receipt. The exact payload hash comes from the selected immutable manifest; it is not the executable path alone.

Before touching state, the child validates context, receipt/hash and current closed control tuple, verifies its own expected component/payload and requested state-directory/operation, and verifies the descriptor's device/inode/owner/mode match the private registry component `admission.lock`. The descriptor must successfully reassert nonblocking exclusive flock on that same open-file description while a separate independent descriptor cannot acquire it. Do not open a replacement inode or infer custody from a PID/environment variable. Parent and child retain the lease through all child state effects/output; child closes it after completion, parent verifies child exit and unresolved custody before releasing its copy. A child/main or supervisor death leaves the durable component phase closed and the attempt record unresolved; recovery re-verifies exact process/custody and reacquires the lease before retry. Same-user adversarial forgery remains outside the local-state trust model, but a copied receipt or stale descriptor never suffices for a normal caller.

`execute` writes `operation.json` before starting the child: the exact context above plus `phase:"pending"` and the verified backup/source manifest hashes (null when inapplicable). Its immutable attempt binds later output. A successful child returns its ordinary `{version:1,format:2,generation:<token>}` plus `maintenance:{component,session,epoch,operation,attempt,payloadSha256,stateDirectorySha256}` matching context; stateDirectorySha256 hashes canonical UTF-8 path bytes with no LF. The parent checks exact bounded stdout, exit0, no remaining relevant journal and a fresh local format/root-generation observation. It then durably writes `result.json` exactly `{version:1,kind:"driver-state-result",component,session,epoch,operation,attempt,payloadSha256,stateDirectorySha256,format:2,generation,status:"complete",backupSha256:<hex or null>}` and marks/removes the pending attempt only after receipt publication. An interrupted acknowledgement retries by observing that same durable result, not inventing a success or rolling back proof. `finish` accepts only that exact current attempt/result, freshly checks the target generation/format/no pending state and absence of custody, then atomically publishes normal with a new epoch. If any check fails, admission stays closed. All four Driver implementations consume this exact boundary; ABR-39 produces/supervises it and ABR-38 qualifies it.

### Executable offline restore and ambiguous-remove resolution

The metadata backup is read-only recovery input. For a known valid interrupted upgrade, the default is resume with its original backup/journal and generation. To explicitly abandon an unsafe or unrecoverable conversion, `execute --operation restore --source <verified-backup> --backup <fresh-output-directory>` first preserves the failed format/identity/journal metadata in the fresh immutable attempt archive, records `operation.json` under the live closed component fence, then restores only the declared metadata paths from the source manifest. It does not copy native homes, credentials, records, chats or a backed-up guard inode. It never opens normal admission with the restored proof.

If the restored format is 1, the same qualified administrative child, still under the live maintenance handoff, runs the specified 1→2 conversion with a **fresh generation**, a fresh child conversion journal and its own verified metadata backup entry inside the new attempt archive. It clears/archives the abandoned journal only after durable restoration intent and before staging that new conversion; every crash checkpoint is resumable by the same restore attempt, never by normal identity. Existing old per-Subscription sidecars cannot establish continuity because the root generation is fresh. If restored format is 2, validate its metadata and perform identity-reset with a fresh generation before success. Unknown/malformed source format refuses and remains fenced. An interrupted restore remains in `operation.json` and can resume only with the same source/archive hashes. A result is complete only after format2/root identity/no pending state validates, then the exact `result.json` permits finish. A reused immutable archive is accepted only for that exact resumed attempt; a fresh restore invocation needs a fresh empty archive. Thus a format1 backup does not strand the user behind an identity-reset refusal, and rollback never silently reopens old continuity.

Ambiguous local remove recovery is `state identity-recover --subscription <canonical-id> --retire --confirm-quiescent --maintenance <receipt>`, invoked only by `driver-state execute --operation identity-recover --subscription <canonical-id> ...` under the same live handoff. The context additionally includes `subscription` for this operation (mandatory, absent otherwise), and its result additionally includes `subscription` (same exact id). This is a **conservative abandonment** of the interrupted operation, not evidence that credential cleanup succeeded. It performs no vendor/native/Keychain/secret-source action. Under the short Subscription lock, preserve the strict pending journal in the immutable operation archive, durably publish its old witness as retired, leave the currently present `record.json` and credential references as they are (or leave an absent record absent), then durably clear/archive the pending marker. A crash repeats retirement of that same witness before clearing; no old active proof is emitted at any point. A current record/built-in can subsequently materialize a fresh witness on normal identity, which necessarily requires explicit application rebind. It cannot reuse the abandoned witness even if the pending record was already partly changed. If current files are malformed/unsafe, remain fenced and use verified metadata restoration rather than overwrite account data.

The create/remove journal must therefore carry exactly `{version:1,operation:"create"|"remove",witness:<token>,phase:"prepared"|"committed"}`. Prepared means local final record/proof settlement is not durably complete; committed is published only after existing required cleanup and record/proof writes succeeded. Normal recovery can finish a committed outcome idempotently. A prepared create may finish its existing valid created record with that exact witness, or abandon it while retiring the witness; a prepared remove with no provable successful cleanup cannot auto-complete deletion or reactivate proof and uses the conservative command above. Only the original operation's valid owner/progress evidence may establish completion; a timeout, missing process or auth counter cannot. The conservative operation itself returns format2/generation plus the maintenance result tuple, with no claim of successful removal and no account fields. ABR-34–37 implement these durable phases and local resolver; ABR-39 passes/supervises the named operation; ABR-38 qualifies crash-before/after retirement/clear and usable fresh proof/rebind refusal. It is not a permanent unavailable branch.
