---
role: authored
spec: ARC-2
status: accepted
---
# Architecture · 02 A Chat Exchange across the components

This specification follows one message from the moment the [Leather Bag](../GLOSSARY.md#leather-bag) sends it to the final state of its [Chat Exchange](../GLOSSARY.md#chat-exchange), and states what passes between Arbol, Arbol Root and the Trunk on the way. It matters because version 1 chained the end of a turn to a separate service that could refuse it, and wrapped every streamed fragment in database rows: chats stayed "running" for ever, one failed turn blocked every other chat, and the disk filled twice. Here an Exchange is one process with one folder, its arriving answer is a file, and its end needs nobody's permission.

It follows the conventions of the [Driver Contract](../driver-contract/README.md#conventions) and the additions in this chapter's [README](README.md#conventions).

## Scope

Covered: the steps between the components, the folder of an Exchange, the arriving answer, stop and answers to the agent's questions, the end, an Exchange whose process is gone, a database that cannot be reached, a rate limit, Arbol quitting.

Not covered: what a Trunk does inside an Exchange, which each Trunk's own specification states, and the formats of the files in the folder, which are fixed in the [Root Contract](../../arbol-root/contract/README.md) ([RCT-1](../../arbol-root/contract/01-the-exchange-folder.md), [RCT-2](../../arbol-root/contract/02-starting-stopping-and-settling.md)); the components ([ARC-0](00-components-and-boundaries.md)); Roots ([ARC-1](01-roots.md)); the Driver's run ([DRV-2](../driver-contract/02-inference.md)); a message sent while its chat is busy, which will steer the running agent once that is specified ([ARC-D54](#decisions)); detecting and ending a stuck Trunk ([ARC-3](03-stuck-trunks.md)).

## Behaviour

### The steps

1. The Leather Bag sends a message in a [UI](../GLOSSARY.md#ui). The Arbol backend takes the route the Leather Bag picked, or resolves a [Brain Recipe](../GLOSSARY.md#brain-recipe) to one, and calls `arbol-root` (ARC-0).
2. A compatible `arbol-root` Build selects a compatible Build of the chosen Trunk implementation and starts it detached, handing it the route and the named Root's identity.
3. The Trunk makes its folder under that Root's `exchanges/`, records the Root identity and its concrete Trunk component and Build, writes the message to that Root's database and answers that the message is accepted. From here on the Exchange is the Trunk's, within that Root.
4. While the agent works, the Trunk appends what arrives to a file in its folder, and the Arbol backend follows that file for the UIs. Each finished message or tool call goes to the database.
5. A stop, or an answer to a question the agent asks, reaches the Trunk through its folder.
6. At the end the Trunk writes the final state to the database and removes its folder.

A message that is not accepted starts nothing, and its [Draft](../GLOSSARY.md#draft) stays in the composer.

<!-- sources:
arbol-root:roots/sapling/drills/sapling_messages.py#real_messages
arbol-root:roots/sapling/drills/sapling_messages.py#judge
arbol-root:roots/sapling/drills/drill_support.py#Inspector
arbol-root:tests/test_sapling_drills.py#Messages
-->

### The folder of an Exchange

```text
~/Library/Application Support/Arbol/roots/sapling/exchanges/
  7f3a…/                 one folder for each Chat Exchange in progress
    record.json          the Root identity, process, Trunk component and Build, chat, route
    events.jsonl         the answer as it arrives
    control              stop, and answers to the agent's questions
```

The folder is the whole interface between a running Trunk and everything else. A compatible manager Build of the owning Root reads the records to list what runs. That Root's backend follows `events.jsonl`; stop and answers are written to `control` using its compatible interface. Cross-Root callers use the common management reply and delegate to the owning Root instead of interpreting another Root's Trunk files. The file names are those of the discussion of 9 October 2026; their formats are fixed in the Root Contract (RCT-1, RCT-2), with the ownership requirements here.

Every Exchange record identifies the persistent Root and the concrete Trunk component and Build that accepted it. The manager Build that started it may also be recorded as provenance; it is not the Root's identity. A compatible manager update changes neither that ownership nor the running Trunk Build. New Roots and migration copies do not take over the original process.

A folder exists only while its Exchange is in progress, or until what is left of an Exchange has been settled.

<!-- sources:
arbol-root:scripts/check_migration.py#judge
arbol-root:tests/test_migration_check.py#MigrationCheck
-->

### The arriving answer is a file

`events.jsonl` holds every event of the answer as it arrives, finished parts too; finished parts also go to the database, and no row is written for a fragment (RCT-1, [RCT-D9](../../arbol-root/contract/01-the-exchange-folder.md#decisions)).

| Reason | Detail |
|---|---|
| The database holds only what lasts | No row is written for a fragment, so the database does not grow with the length of an answer |
| The answer keeps arriving | A slow or restarting database does not stop what the Leather Bag sees |
| Late and second readers | A UI opened late, opened again or opened twice reads the same file from its start. No resident service has to replay what was missed |
| Nothing to clean up | The file goes with its folder |

The file has a limit of size, as every buffer must have.

Observed in version 1: the design said that streamed text is never stored, but every publication and delivery of a fragment was wrapped in two permanent database rows. An inventory held about 950,000 such rows beside 6,227 conversation records, and one table reached 184 GiB for 12 MiB of live data. Writes to storage on the loop that served every chat stalled all of them, for up to nine seconds.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#3. Durable bookkeeping on the streaming path`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#7. Blocking storage calls on the loop that serves every chat`

<!-- sources:
arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/events.py#EventsFile
arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/rows.py#RowMaker
arbol-trunk:trunks/trivial/tests/test_events.py#Events
arbol-root:contract/conformance/rct_conformance/scenarios/r15.py
-->

### Stop, and answers

A stop is a line in `control`. The Trunk stops the Driver's run (DRV-2) and ends the Exchange as cancelled. A UI shows "stopped" when the Trunk reports that the agent has stopped, and not before.

An answer to a question the agent asks the Leather Bag ([DRV-3](../driver-contract/03-tools-and-permissions.md)) takes the same way.

### The end

A Trunk ends an Exchange by itself: it writes the final state to the database and removes its folder. No other component has to accept, confirm or record the end. The final states seen from outside are completed, failed with its cause, cancelled, and interrupted; a rate limit is the cause of `failed`, not a state of its own (RCT-2).

### An Exchange whose process is gone

A Trunk that is killed leaves its folder behind, with a record whose process no longer lives. Whether a process lives is told as a Driver tells it (DRV-6).

"Running" has one source, which is a record in the folder together with a live process ([ARC-D44](#decisions)). An Exchange that is open in the database with no live process is shown as interrupted. Root lists it as interrupted, or as unsaved when its record already has its end ([RTM-0](../../arbol-root/specs/00-the-commands.md#the-listing)), and `arbol-root settle` has a Trunk Build settle it; Arbol runs it when its backend starts, when it sees the database return, and after a listing that shows it ([RTM-0](../../arbol-root/specs/00-the-commands.md#settling)). Settling saves what the folder holds, with its true state ([ARC-D53](#decisions)). When the folder holds a finished result that could not be saved, the Trunk Build saves it with its own final state: completed, failed or cancelled. When the process died before it finished, the Trunk Build saves what the agent had produced, with the state interrupted. Then it removes the folder. No repair names a turn, and no script is needed.

A failed, stuck or cancelled Exchange concerns its own chat only. Other chats go on and new chats start. After a failed or a cancelled Exchange the same chat takes a new message. A stuck Exchange is still in progress, so its chat stays busy until that Exchange is ended. How a stuck Trunk is detected and ended is the subject of [ARC-3](03-stuck-trunks.md).

Observed in version 1: when a turn's end could not be recorded, the chat showed "running" for ever. Crashed turns kept a shared lock that blocked every upgrade. About fifteen one-off repair scripts, keyed to single turns, were the way out.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#2. One turn's failure could block everything else`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#Product guarantees the rewrite must keep`

### When the database cannot be reached

| When | What happens |
|---|---|
| At acceptance | The message is refused with the cause. Nothing is started and the Draft stays |
| While the agent works | The answer keeps arriving in the file. The Trunk writes finished parts when the database is back |
| At the end | The Trunk tries again for a while. If it has to end first, it leaves the result in its folder, and the folder stays until the result is in the database ([ARC-D43](#decisions)). Settling saves it with its own final state (`arbol-root settle`, RTM-0), at the next start of Arbol or when the Arbol backend sees the database return. Until then a UI shows the answer from the folder, marked as not yet saved ([ARC-D53](#decisions)) |

A Trunk never needs the database in order to finish, and what an agent produced is never lost because the database was away.

A database that does not answer is not a normal state. For as long as it lasts, Arbol calls the Leather Bag's attention to it and names the cause ([ARC-D53](#decisions)).

<!-- sources:
arbol-root:roots/sapling/drills/sapling_outage.py#database_away
arbol-root:roots/sapling/drills/sapling_outage.py#stopped
arbol-root:roots/sapling/drills/sapling_outage.py#Installed
arbol-root:roots/sapling/drills/sapling_outage.py#DirectoryWatch
arbol-root:tests/test_sapling_drills.py#Outage
-->

### A rate limit

When the Driver's run ends with `rate_limited` ([DRV-4](../driver-contract/04-errors-and-limits.md)), the Trunk ends the Exchange as failed with that cause. It does not take another route by itself. Arbol offers to send again with what the Brain Recipe's logic picks next (ARC-0); Elma Chat, which uses no Brain Recipe, offers to send again with the route the Leather Bag picks ([BKD-2](../backend/02-elma-chat.md)).

<!-- sources:
arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/end.py#end_of_run
arbol-trunk:trunks/trivial/tests/test_run.py#WholeExchange.test_a_failed_run_keeps_the_drivers_error_whole
arbol-root:contract/conformance/rct_conformance/scenarios/r11.py#driver_failures
-->

### When Arbol quits

Quitting Arbol, closing every UI or losing the Arbol backend stops no Exchange. On App or backend restart, Arbol enumerates every retained Root through `arbol-roots`, selects a compatible manager Build for each, and asks it to list its Exchanges. Each reply identifies the Root, Exchange, concrete Trunk component and Build, chat, process and state. Arbol combines this execution metadata to rediscover running agents across different Trunks and Roots; an unavailable Root is reported separately and does not prevent discovery of the others.

The backend compatible with each Root reads that Root's database and Exchange files to show what was produced meanwhile. Cross-Root discovery grants no access to another Root's chat tables or Trunk-specific formats. No running Exchange is reassigned to the current Root or a newer Trunk Build. A missed live update never leaves a chat stale: a UI recovers the truth by reading again.

<!-- sources:
arbol-root:roots/sapling/drills/trunk_drills.py#killed
arbol-root:roots/sapling/drills/trunk_drills.py#judge_real_interrupted
arbol-root:roots/sapling/drills/trunk_drills.py#database_mid_run
arbol-root:roots/sapling/drills/trunk_drills.py#database_through_end
arbol-root:roots/sapling/drills/trunk_drills.py#failed_or_cancelled
-->

## Requirements

| ID | The components together must… | Origin | Verified by |
|---|---|---|---|
| ARC-2.1 | count a message as accepted when the Trunk has its record in the folder and the message in the database, and before that start nothing and keep the Draft | Changed | Root/Trunk acceptance refusal: installed drill `sapling.database-away` in roots/sapling/drills/database-away.py (SYL-186), private `sapling.restore`, `sapling.restore-failure`, `sapling.no-driver-run`. The installed `sapling.real-messages` check passed on 27 October 2026 through manager Build 1, Trivial Build 3 and Claude Build d: two accepted/running Exchanges in one chat, both answers persisted with positive input/output tokens and the second recalling the random word; Exchange folders removed. Unit `sapling.messages-expired-usage` / `sapling.messages-unproved-reset` prove the cached-limit reset boundary. Keeping the Draft is backend BKD-0.10/BKD-0.12 and remains pending backend implementation; this drill does not close that UI part |
| ARC-2.2 | keep the arriving answer in a file in the Exchange's folder, with a limit of size, and write no database row for a fragment | Changed | unit: `Events`, `Rows` and `WholeExchange.test_a_full_file_fails_the_exchange_and_keeps_only_rows_from_written_lines` in `trunks/trivial/tests/` of `arbol-trunk`; contract: R15 (SYL-178), with tool-output and whole-file limits |
| ARC-2.3 | write each finished message or tool call to the database when it is finished | Changed | contract: RCT-3.2, scenario R1 of [RCT-4](../../arbol-root/contract/04-conformance.md) (SYL-171) |
| ARC-2.4 | show a UI that is opened late, opened again or opened twice the whole answer so far | Changed | journey |
| ARC-2.5 | take a stop and an answer to the agent's question through the Exchange's folder, and show "stopped" only when the Trunk reports that the agent has stopped | Changed | drill |
| ARC-2.6 | let a Trunk end its Exchange by itself, with no other component accepting or confirming the end | Changed | installed deterministic `sapling.starter-gone`, `sapling.failed-exchange`, `sapling.cancelled-exchange` and `sapling.database-away-through-end` (SYL-187), with exactly one file end matching the persisted state and unchanged accepted Root/Trunk/Build identity |
| ARC-2.7 | show an Exchange whose process is gone as interrupted, settle it without a script that names it, keep what the agent had produced, and save a finished result that is still in its folder with its own final state | Changed | Root/Trunk part: installed `sapling.trunk-killed` (stand-in and one real Haiku run), `sapling.trunk-hangs` and `sapling.database-away-through-end` (SYL-187), interrupted/unsaved listing and exact settled rows; whole text blocks/open calls/runs follow RCT-3, fragments are not message rows. Backend/UI recovery and display remain BKD-0 implementation, outside these drills |
| ARC-2.8 | keep a failed, stuck or cancelled Exchange to its own chat: other chats go on and new chats start, and after a failed or a cancelled Exchange the same chat takes a new message | Changed | Root/Trunk part: installed `sapling.failed-exchange` and `sapling.cancelled-exchange` (SYL-187), same-chat next Exchange while another held chat stays running and later completes; `sapling.trunk-killed` resumes an interrupted chat. Backend/UI presentation remains BKD-0 implementation |
| ARC-2.9 | refuse a new message while the database cannot be reached, and lose no result of an Exchange in progress | Changed | new-message refusal: installed `sapling.database-away` (SYL-186), bounded database_unavailable with no folder/Driver run/row changes. Existing Exchange: `sapling.database-away-mid-run` and `sapling.database-away-through-end` (SYL-187) after complete connected-server shutdown, ordered whole blocks/tool/run usage retried or settled, actual sixty-second retry and healthy service restored |
| ARC-2.10 | end an Exchange as failed with the cause `rate_limited` when its run met a rate limit, and take no other route inside the Trunk | Changed | contract: R11 (SYL-177); unit: `WholeExchange.test_a_failed_run_keeps_the_drivers_error_whole` and `WholeExchange.test_a_refusal_can_be_the_only_event_and_no_other_route_is_tried` in `trunks/trivial/tests/test_run.py` of `arbol-trunk` |
| ARC-2.11 | stop no Exchange when Arbol quits, every UI closes or the Arbol backend ends, and show on return what was produced meanwhile | Kept | drill |
| ARC-2.12 | record each accepted Exchange's persistent Root identity and concrete Trunk component and Build, retain them through compatible updates and restarts, and leave the original process with its Root when another Root is created or history is migrated | New | Migration-copy part: `root.migration-whole`, `root.migration-open-fault`, `root.migration-snapshot-fault` preserve Trunk/Build rows, record the source Root and leave source data untouched (SYL-184). Existing contract R1/R16 and manager identity checks cover acceptance/listing; compatible updates/restarts and original process ownership across real migration remain SYL-187/SYL-189 and backend drills |
| ARC-2.13 | rediscover Exchanges across every retained Root on App or backend restart through the common Root catalogue and matching manager replies, isolate discovery failures by Root, and delegate detailed reads and controls to the owning Root's compatible components | New | drill |
| ARC-2.14 | call the Leather Bag's attention to a database that cannot be reached for as long as it lasts, and show a finished answer that is not yet saved from its folder, marked as such | New | drill |

## Interface

The folder of an Exchange, as in *The folder of an Exchange* above. The formats of `record.json`, `events.jsonl` and `control`, and the commands of a Trunk, are fixed in the Root Contract (RCT-1, RCT-2).

## Known problems in version 1

Not to be reproduced.

- **An end that could be refused.** The end of a turn had to be accepted by a separate service against a closed list of allowed combinations. A legitimate failure could not be recorded, and the chat showed "running" for ever.
- **One turn blocking all.** A rejected write paused all new turn activity, and crashed turns kept a lock that blocked every upgrade.
- **Database rows for streamed fragments.** They filled the disk twice and ended long answers in mid-stream.
- **Storage on the path of every chat.** A slow write stalled every chat served by the same process.
- **Repair by script.** About fifteen one-off programs, keyed to single turns, were the recovery path.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#2. One turn's failure could block everything else`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#3. Durable bookkeeping on the streaming path`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#7. Blocking storage calls on the loop that serves every chat`

## Decisions

The decisions below retain their recorded wording. [ARC-D47](01-roots.md#decisions), decided on 12 October 2026, replaces the former Ring concept with named Roots and gives each Root its compatible Trunks; current requirements and interfaces above use that decision. Earlier terminology here is historical.

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| ARC-D42 | How does a UI see an answer while a detached Trunk produces it? | The Trunk appends the arriving answer to one file for each Exchange, and the UI follows the file. Finished parts go to the database. Stop and answers reach the Trunk through the same folder | Decided 9 October 2026 by the owner: files, after asking why the answer is not written directly to the database as in version 1. That the folder also carries stop and answers was confirmed the same day |
| ARC-D43 | What does a Trunk do when the database cannot be reached? | At acceptance the message is refused and the Draft stays. Later the Trunk tries again, and if it has to end it leaves the result in its folder | Decided 9 October 2026 by the owner as to the principle: a Trunk never needs the database in order to finish. The details are the proposed default, a technical choice made on the owner's go-ahead the same day |
| ARC-D44 | What does "running" mean, and who settles an Exchange whose process is gone? | A record in the folder together with a live process. Anything else that is still open is shown as interrupted, and Root has a Trunk Build settle it | Decided 9 October 2026 by the owner: the proposed default |
| ARC-D53 | A Trunk finished while the database was away and left its result in its folder. Who saves it, and as what? | Settling saves whatever the folder holds, with its true state: a finished result as completed, failed or cancelled, and what a dead process had produced as interrupted. It runs at every start of Arbol and when the Arbol backend sees the database return. Until then a UI shows the answer from the folder, marked as not yet saved | Decided 13 October 2026 by the owner: agreed. The owner added that a database that does not answer is not a normal state, and that Arbol may call the Leather Bag's attention to it |
| ARC-D54 | What does a chat do with a message sent while its Exchange is in progress? | The rule of version 1: one Exchange in a chat at a time. A UI offers to stop the running Exchange and send then; the command line is refused | Decided 13 October 2026 by the owner: a new message will be able to steer the running agent, maybe not in the first version. The owner did not rule on the time before that; the proposed default stands for it |
| ARC-D55 | How is a stuck Trunk detected and ended? | When a Trunk has not confirmed a stop after 15 seconds, `arbol-root` ends its process and the Exchange is settled as interrupted | Decided 13 October 2026 by the owner: this gets a specification of its own, because the decision is important. The proposed default is not adopted here. The specification is ARC-3, drafted the same day |
