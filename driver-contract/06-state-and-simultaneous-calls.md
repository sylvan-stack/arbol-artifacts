---
role: authored
spec: DRV-6
status: accepted
---
# Driver Contract · 06 State and simultaneous calls

A Driver is started anew for every operation, so everything it knows from one call to the next is in files. This specification names those files and their formats, says how several calls that run at the same moment keep out of each other's way, how one call reaches another that is already running, and what is done about the leftovers of a call that was killed. It matters because a Driver has no process that stays running and could keep order: the files and the rules for writing them are the only coordination there is.

## Scope

Covered: the layout of the state directory, the format of each file in it, how files are written, the data format number, the map from chat sessions to the vendor tools' saved conversations and how a Driver decides whether a saved conversation still fits, records of runs and sign-ins in progress, locks, stopping a run from another call, replacing a sign-in, leftovers of a killed call, what the Driver remembers about the vendor tool's program.

Not covered: what is inside a Subscription's home, which belongs to the vendor tool (CLD-1, CDX-1); the settings file, which is not in the state directory (DRV-0); the registry of Builds (BLD-0).

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
      home/                     the vendor tool's home for this Subscription
      chats/
        <chat key>.json         one entry of the map per chat session
  runs/
    <run id>.json               present only while that run is in progress
  tmp/
    <run id>/                   files that live as long as one run
```

Nothing else is kept. A folder or file that is missing is created when it is first needed, so an empty state directory is a valid one.

### Writing a file

A file is always written whole: the Driver writes the new content to a temporary file in the same folder and renames it over the old one. A reader therefore sees the old content or the new, never a part. Every file is JSON in UTF-8, except `format`.

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

## Requirements

| ID | A Driver must… | Origin | Verified by |
|---|---|---|---|
| DRV-6.1 | keep its files in the layout above, under the state directory alone, readable by the owner only, and treat a missing file or folder as empty | New | Claude: `base.info`, `state.lock` (base layout and privacy); contract pending C38; Codex pending |
| DRV-6.2 | write every file whole, by writing a temporary file in the same folder and renaming it | New | Claude: `state.atomic-write`; Codex pending |
| DRV-6.3 | write the data format number when it creates the state directory, and do nothing but fail with `state_newer` when it finds a higher number than it knows | New | Claude: `base.state-newer`; contract pending C38; Codex pending |
| DRV-6.4 | hold a Subscription's lock only while it rewrites that Subscription's record, never across a request to the vendor, a run of the vendor tool or a sign-in | New | Claude: `subscriptions.create`, `subscriptions.update`, `subscriptions.independent`, `C2`, `C5`, `subscriptions.late-check` (vendor calls outside locks); run operations and Codex pending |
| DRV-6.5 | wait for a taken lock in steps of 50 milliseconds, take over a lock whose owner is dead, and fail with `internal` after 10 seconds | New | Claude: `state.lock` (contention, dead owner, timeout, dead reaper); contract pending C38; Codex pending |
| DRV-6.6 | name the owner of every lock and of every record of something in progress by process identifier and start time, and count an owner as alive only when both match | New | Claude: `state.owner`, `state.lock`; Codex pending |
| DRV-6.7 | keep `runs/<run id>.json` from the start of a run to its final event, created so that a second run with the same identifier fails | New | Claude: `C33`, `C40`; Codex pending |
| DRV-6.8 | stop a run of another call by sending its owner the termination signal and waiting until its record is gone, for at most 20 seconds | New | contract |
| DRV-6.9 | end a pending sign-in of another call in the same way before starting its own, and end a replaced sign-in with a `failed` step whose error is `in_use` | New | Claude: `C2`, `C6`; Codex pending |
| DRV-6.10 | clear the leftovers of a killed call, as the table above says, before a `run`, `runs list`, `runs stop` or a change to a Subscription does its own work, ending a vendor tool that outlived its Driver | New | contract |
| DRV-6.11 | keep one entry of the map per chat session and Subscription, in a file named after the SHA-256 of the chat session identifier, holding the fields above and no message | New | Claude: `C14`, `continuity.map`; Codex pending |
| DRV-6.12 | continue a saved conversation only when every check of the table above holds, and otherwise build a new one and give the first reason that failed, in the order of the table | New | Claude: `C14`; Codex pending |
| DRV-6.13 | compute the digest of the messages and the system prompt digest as stated above | New | Claude: `continuity.digest`; Codex pending |
| DRV-6.14 | write an entry of the map only after a completed run, and remove the entry a run was continuing when that run ends any other way and the entry still names the same conversation | New | Claude: `C14`, `continuity.map`; Codex pending |
| DRV-6.15 | never wait for another run that uses the same saved conversation: build a new conversation instead | New | Claude: `C14`, `continuity.concurrent`; Codex pending |
| DRV-6.16 | ask the vendor tool's program for its version only when its path, size or change time differs from what `tool.json` holds | New | Claude: `base.tool-cache`; Codex pending |

## Interface

```ts
interface Owner { pid: number; startedAt: string }      // the process, and when it was started

// subscriptions/<id>/record.json: Subscription (DRV-1) without `settings`; `state` is never "signing_in"
type SubscriptionRecord = Omit<Subscription, "settings">;

interface LockFile { owner: Owner }                      // subscriptions/<id>/lock

interface SignInRecord {                                 // subscriptions/<id>/sign-in.json
  owner: Owner;
  expiresAt: string;
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

<!-- sources:
arbol:daemons/shared/arbol_shared/turn_store.py#TurnStore
arbol:drivers/codex/arbol_driver_codex/tool_process.py#ToolProcess._cleanup
arbol:product-spec/12-lessons-and-invariants.md#6. Many resident services with strict, version-coupled contracts
-->

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| DRV-D39 | How are continuity digests and simultaneous resumes made deterministic? | Use the message tuples stated above. Under the Subscription lock, read the map, choose the conversation and publish the run record that reserves it; release the lock before starting the tool. Under that same short lock, write a completed map entry or conditionally remove the entry that a failed run continued | Decided 7 October 2026 during SYL-82, a technical choice |
| DRV-D38 | How are sign-in replacement and late vendor answers coordinated? | Reserve sign-in.json under the Subscription lock for sign-in, sign-out or removal; only a sign-in reservation presents the state signing_in; set stopReason before signalling its owner, then wait outside the lock. The owner checks this reason before storing a result. Record the login child owner for cleanup after a killed command; attempt files live in tmp/sign-in-<subscription id>. A status or usage answer updates only the record revision it checked, so a late answer cannot restore a signed-out account. Removing an initial family Subscription clears its stored data and leaves its implicit signed-out record available | Decided 6 October 2026 during SYL-78, a technical choice |
| DRV-D36 | How are base state errors and process identities read? | A malformed `format` or progress record fails with `internal`, without its contents in the error. On macOS and Linux, process start times come from `/bin/ps` with a clean environment and the C locale. A lock is published by linking a complete temporary owner record into place, failing if `lock` exists, so no reader sees a half-written owner | Decided 6 October 2026 during SYL-75, a technical choice |
| DRV-D28 | How does a Driver notice that the last answer of a chat was replaced, when no message of the user changed? | The caller stores, with each answer and tool call, the identifier of the run that produced it, and hands it back in the history. The Driver compares the last one with the run its saved conversation ends in. Without it a chat that had its last answer made again on the other Driver would be continued with the old answer | Withdrawn 6 October 2026. The owner had understood the fingerprint to cover the whole conversation, so the text of the replies became part of it (DRV-D10), and no run identifier is needed (SYL-72) |
| DRV-D29 | How do calls that run at the same moment keep out of each other's way? | A lock file per Subscription, created so that a second creation fails, held only while one record is rewritten. Whatever lasts is a record naming its owner, never a lock. File locks of the operating system are not used: Node.js offers none without an add-on | Decided 6 October 2026, a technical choice made in drafting on the owner's go-ahead |
| DRV-D30 | How does one call reach another that is already running? | By the termination signal, sent to the process named in the record of the run or of the sign-in. A Driver already stops its run on that signal (DRV-2.26), so nothing new is needed | Decided 6 October 2026, a technical choice made in drafting on the owner's go-ahead |
| DRV-D31 | Is a saved conversation continued when the system prompt has changed? | Where the vendor tool takes the new prompt, yes. Where it keeps the first one, a new conversation is built, which is always right and costs the tool's own record of the conversation | Decided 6 October 2026 by the real test that SYL-30 listed, a technical choice. `claude` takes the new prompt when it is started with `--system-prompt-snapshot off`, so the Claude Driver continues. `codex` kept the first prompt whatever `thread/resume` was given, so the Codex Driver rebuilds |
