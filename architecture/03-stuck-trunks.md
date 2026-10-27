---
role: authored
spec: ARC-3
status: accepted
---
# Architecture · 03 Stuck Trunks

An [Arbol Trunk](../GLOSSARY.md#arbol-trunk) is *stuck* when its process is alive and does nothing: it gives no sign of life, or it was told to stop and does not. This specification states how that differs from waiting on purpose, how it is noticed although nothing but Arbol stays running, and how a stuck [Chat Exchange](../GLOSSARY.md#chat-exchange) is ended so that its chat can be used again. It matters because version 1 had no limit of any kind: a silent turn held its processes until someone stopped it, chats showed "running" for ever, and about fifteen one-off repair scripts were the way out.

It follows the conventions of the [Driver Contract](../driver-contract/README.md#conventions) and the additions in this chapter's [README](README.md#conventions). The owner asked for this specification on 13 October 2026, because the decision is an important one ([ARC-D55](02-chat-exchange-across-components.md#decisions)), and decided its five points the same day (ARC-D57 to ARC-D61). The times are the values to start with.

## Scope

Covered: what counts as stuck and what does not, the signs of life of a Trunk, a Trunk that ends itself, how Arbol notices from outside, ending a stuck Exchange, a stop that is not obeyed, a Driver that falls silent, long waits on purpose, a Mac that slept.

Not covered: an Exchange whose process is gone, which is settled as interrupted ([ARC-2](02-chat-exchange-across-components.md)); a vendor tool that hangs inside a run, which the Driver ends by its own time limits ([DRV-4](../driver-contract/04-errors-and-limits.md)); the formats of the files in the folder of an Exchange, which are fixed in the [Root Contract](../../arbol-root/contract/README.md) ([RCT-1](../../arbol-root/contract/01-the-exchange-folder.md)); a message that steers a running agent (ARC-D54).

## Behaviour

### Slow is not stuck

An Exchange can take long for six reasons. Two of them are stuck.

| The Exchange… | Example | Stuck? | Who acts |
|---|---|---|---|
| waits for the Leather Bag | The agent asked a question (DRV-3) | No, however long it lasts | The Leather Bag answers, or stops it |
| waits for a command the agent runs | A build, or a server that runs for hours. The Driver's idle limit does not count meanwhile (DRV-4) | No. It is shown with what it waits for and for how long | The Leather Bag stops it ([ARC-D61](#decisions)) |
| waits for a vendor tool that says nothing | The tool hangs | Not in the sense of this specification | The Driver: it ends the run after its idle limit of 15 minutes, as `failed` with `limit_reached` (DRV-4) |
| gives no sign of life, with a live process | The Trunk hangs in a call that never returns | **Yes** | This specification |
| was told to stop and has not stopped | The stop was never read | **Yes** | This specification |
| has no live process | The Trunk was killed | No: it is interrupted | Settling (ARC-2) |

### The signs of life of a Trunk

The folder of an Exchange is the whole interface of a running Trunk (ARC-2). A Trunk keeps two facts up to date in it ([ARC-D58](#decisions)):

| Fact | What it is |
|---|---|
| The *heartbeat* | A counter that the Trunk raises from the loop that does its work, at least every 10 seconds, whatever it is waiting for. No timer of its own raises it, so a Trunk whose work has hung stops raising it |
| What it waits for | The Driver, a tool call or command, an answer from the Leather Bag, the database or a small model call, and since when |

A heartbeat that goes on means that the Trunk works or waits on purpose, and the second fact says which. Only a heartbeat that stands still means stuck.

A Trunk is therefore written so that no single step of its work takes longer than a few seconds: every wait in it has a time limit, after which the loop comes round again.

<!-- sources:
arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/life.py#SignsOfLife
arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/life.py#waiting_for
arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/run.py#drive
arbol-trunk:trunks/trivial/tests/test_life.py
arbol-root:contract/conformance/rct_conformance/scenarios/r6.py
arbol-root:src/arbol_root/listing.py#project
arbol-root:tests/test_listing.py#Listing.test_all_six_states_are_read_from_records_alone_in_deterministic_order
arbol-root:tests/fixtures/listing-v1.json
-->

### Two lines of defence

Nothing stays running except Arbol. A stuck Trunk is therefore caught in two ways.

**1. The Trunk watches itself** ([ARC-D59](#decisions)). A part of the Trunk's process that does nothing else looks at the heartbeat. When the work has not raised it for 60 seconds, that part ends the Trunk's own process and everything the Trunk started. From then on the Exchange is one whose process is gone, and it is settled as interrupted (ARC-2). This works while Arbol is not running, and in a Root that is not current.

**2. Arbol looks from outside.** `arbol-root list` gives for each Exchange its heartbeat and what it waits for. The Arbol backend of a Root asks every 30 seconds while it runs. An Exchange whose process lives and whose heartbeat did not move between two looks that are at least 90 seconds apart is stuck. This catches a process that is frozen as a whole, in which the part that watches is frozen too.

Time during which the Mac slept does not count. Both lines measure with a clock that stands still during sleep, so that waking the Mac does not make every Exchange look stuck.

While no Arbol backend of a Root runs, only the first line works for that Root. A Trunk that is frozen as a whole then stays until a backend of its Root runs again. It calls no model and writes nothing meanwhile.

<!-- sources:
arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/watch.py#Watch
arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/run.py#run_exchange
arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/termination.py#end_group
arbol-root:contract/conformance/rct_conformance/scenarios/r7.py
arbol-root:src/arbol_root/clock.py#awake
arbol-root:tests/test_groups.py#GroupIdentity
arbol-trunk:trunks/trivial/tests/test_loop.py#StoppingTheRun
arbol-trunk:trunks/trivial/tests/test_loop.py#SilentRuns
arbol-trunk:trunks/trivial/tests/test_watch.py#Watching
arbol-trunk:trunks/trivial/tests/test_time_scale.py#TimeScaledWaits
-->

### Ending a stuck Exchange

A stuck Exchange is ended without asking ([ARC-D57](#decisions)). By its definition it is doing nothing, so ending it loses nothing. Arbol says in the chat that the Exchange was ended because it was stuck.

The command is `arbol-root stop --force <exchange>`:

1. It sends SIGTERM to the process group the Trunk leads ([RCT-2](../../arbol-root/contract/02-starting-stopping-and-settling.md#one-process-group)).
2. After 5 seconds it ends by force what is still alive of them.
3. It has the chosen Build of the Trivial Trunk settle the Exchange ([RTM-0](../../arbol-root/specs/00-the-commands.md#settling)): what had arrived is saved, the final state is interrupted, unless its end was already written (RCT-2), and the folder is removed (ARC-2).

The Driver's run ends with its caller (DRV-2), and the next call of that Driver clears what a killed call left behind (DRV-6).

| | |
|---|---|
| Kept | Every finished message and tool call, which are in the database already, and the part of the answer that had arrived in the file |
| Not undone | Changes the agent made to files, and commands it had completed |
| Afterwards | The chat takes a new message (ARC-2) |

<!-- sources:
arbol-root:src/arbol_root/stop.py#stop
arbol-root:src/arbol_root/groups.py#force_group
arbol-root:src/arbol_root/settle.py#settle_after_stop
arbol-root:tests/test_groups.py#NativeForce
-->

<!-- sources:
arbol-root:roots/sapling/drills/stopping_drills.py#force
arbol-root:roots/sapling/drills/stopping_drills.py#killed_while_forcing
arbol-root:roots/sapling/drills/stopping_support.py#ignored_child
arbol-root:roots/sapling/drills/stopping_child.py#main
-->

### A stop that is not obeyed

A stop is a line in the `control` file of the Exchange (ARC-2). The Trunk stops the Driver's run, which may take 15 seconds (DRV-2), and ends the Exchange as cancelled.

`arbol-root stop <exchange>` writes that line and waits. When the Exchange has not ended after 20 seconds, the same command ends it by force, as above ([ARC-D60](#decisions)). The Exchange is then interrupted and not cancelled, because the Trunk never confirmed the stop, unless its end was already written ([RCT-2](../../arbol-root/contract/02-starting-stopping-and-settling.md)).

A UI shows "stopping" from the request until the Exchange has ended, and then its true final state. Stopping an Exchange that has ended already, or that is unknown, succeeds and changes nothing, as with a run (DRV-2). The Leather Bag can therefore always use stop to bring a chat back to a state in which it takes a message.

<!-- sources:
arbol-root:src/arbol_root/stop.py#stop
arbol-root:src/arbol_root/clock.py#awake
arbol-root:tests/test_stop.py#Stopping.test_graceful_deadline_calls_escalation_after_twenty_awake_seconds
arbol-root:tests/test_groups.py#GroupIdentity.test_complete_stop_uses_20_5_5_with_an_in_process_moved_clock
-->

<!-- sources:
arbol-root:roots/sapling/drills/stopping_drills.py#obeyed
arbol-root:roots/sapling/drills/stopping_drills.py#not_obeyed
arbol-root:roots/sapling/drills/stopping_drills.py#end_already_written
arbol-root:roots/sapling/drills/stopping_drills.py#killed_while_waiting
-->

### A Driver that falls silent

A Driver ends a silent vendor tool by itself (DRV-4). The Driver's own process can hang too. A Trunk therefore does not wait for a silent Driver without end: when a run has given no event for one minute longer than its idle limit, while no tool call and no question is open, and, where the Trunk's own specification says how it tells one, no command left in the background, the Trunk ends the run's process and ends the Exchange as failed, naming the cause. Telling such commands apart is for future Trunks ([RCT-D30](../../arbol-root/contract/02-starting-stopping-and-settling.md#decisions)). The Trivial Trunk tells none: with it, a command left running in the background that gives no event for 16 minutes ends the run as failed, a departure from [ARC-D61](#decisions) for the Trivial Trunk alone ([TRV-0](../../arbol-trunk/trunks/trivial/specs/00-the-trivial-trunk.md)).

This is ordinary work of a Trunk whose heartbeat goes on. It needs nothing from outside.

<!-- sources:
arbol-trunk:trunks/trivial/src/arbol_trunk_trivial/run.py#drive
arbol-trunk:trunks/trivial/tests/test_loop.py#SilentRuns
arbol-root:contract/conformance/rct_conformance/scenarios/r18.py
-->

### Long waits on purpose

A command the agent runs is never ended for being slow, and a question waits for its answer without limit (DRV-4, DRV-3). On 6 October 2026 the owner left to Arbol what is done about runs that wait for long.

Decided ([ARC-D61](#decisions)): nothing is ended automatically. A UI shows what the Exchange waits for and for how long, for example "running a command for 2 h 10 min" or "waiting for your answer since 14:02", and the Leather Bag stops it when that is wanted.

Observed in version 1: there was no time limit of any kind. A scan marked a chat as stalled after 15 minutes without acting on it. Stop ended the agent's whole process group, with a forced kill after 2 seconds and 15 seconds in total, and cancel doubled as repair: on a chat that was marked running although nothing ran, it reset the chat to idle. On 24 September 2026 long turns stayed "running" for ever, because the failure itself could not be recorded.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/03-turn-execution.md#Cancel`
- `arbol_deprecated_v1:product-spec/03-turn-execution.md#Limits and defaults`
- `arbol_deprecated_v1:product-spec/03-turn-execution.md#States and transitions`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#2. One turn's failure could block everything else`

<!-- sources:
arbol-root:roots/sapling/drills/trunk_drills.py#hangs
arbol-root:roots/sapling/drills/trunk_drill_support.py#Exchange.capture_processes
arbol-root:roots/sapling/drills/trunk_drill_support.py#Exchange.gone
-->

## Requirements

A Trunk:

| ID | A Trunk must… | Origin | Verified by |
|---|---|---|---|
| ARC-3.1 | raise a heartbeat in the folder of its Exchange from the loop that does its work, at least every 10 seconds, whatever it is waiting for | New | contract: R6 (SYL-176); unit: `Heartbeat`, `RoundsWithLife` and `TimeScaledWaits` in `trunks/trivial/tests/` of `arbol-trunk` |
| ARC-3.2 | state in that folder what it is waiting for and since when: the Driver, a tool call or command, an answer, the database or a small model call | New | contract: R6 for Driver, tool and answer waits (SYL-176); unit: `Waiting` for all five values, priority and `since`, in `trunks/trivial/tests/test_life.py` of `arbol-trunk` |
| ARC-3.3 | end its own process and everything it started when its work has not raised the heartbeat for 60 seconds | New | installed real-scale `sapling.trunk-hangs` in roots/sapling/drills/drill-trunk-hangs.py (SYL-187): unchanged heartbeat, no forged end, own watch ends the Trunk/Driver and separate stand-in child after sixty seconds plus group grace; listing/settling recover interrupted |
| ARC-3.4 | end a Driver run that gave no event for one minute longer than its idle limit while no tool call or question was open, nor a command left in the background where its own specification says how it tells one, and end the Exchange as failed with that cause | New | contract: R18 (SYL-178), through RCT-2.21, including a background command that the Trivial Trunk does not distinguish; unit: `SilentRuns` and `WholeExchange.test_a_silent_run_is_stopped_and_the_exchange_fails_with_its_own_cause` in `trunks/trivial/tests/` of `arbol-trunk` |

The Root manager:

| ID | The Root manager must… | Origin | Verified by |
|---|---|---|---|
| ARC-3.5 | give in every listing each Exchange's heartbeat and what it is waiting for | New | unit: `root.list-states`, `root.list-form`, `root.list-forward-compatible` (SYL-182), RTM-0.6 |
| ARC-3.6 | on `stop`, write the stop and wait, end the Trunk's processes by force when the Exchange has not ended after 20 seconds, and have it settled as interrupted, unless its end was already written (RCT-2) | Changed | Root manager unit `root.stop-control`, `root.stop-grace-clock`, `root.stop-complete-clock`, `root.stop-dead`, `root.stop-settle-refusal` (SYL-183); installed real-scale `sapling.stop-obeyed`, `sapling.stop-not-obeyed` (actual twenty seconds), `sapling.stop-end-already-written` (known end/no force) and `sapling.root-killed-while-waiting`, all in `sapling.stopping-drills` (SYL-188). UI presentation remains backend/UI work |
| ARC-3.7 | on `stop --force`, send the Trunk's processes the signal to end, end by force after 5 seconds what is still alive, leave none of them alive, and have the Exchange settled as interrupted, unless its end was already written (RCT-2) | Changed | Root manager unit `root.stop-force-term`, `root.stop-force-kill`, `root.stop-orphaned-child`, `root.stop-group-identity`, `root.stop-complete-clock` (SYL-183); installed `sapling.stop-force`, `sapling.stop-force-ignored-term` (actual five-second grace and no survivor), `sapling.root-killed-while-forcing` and known-end refusal to force, all in `sapling.stopping-drills` (SYL-188) |
| ARC-3.8 | treat the stop of an Exchange that has ended or is unknown as success | Kept | unit `root.stop-none`, `root.stop-ended`, `root.stop-dead`, `root.stop-disappearance`, `root.stop-settle-refusal` (SYL-183) |

Arbol:

| ID | Arbol must… | Origin | Verified by |
|---|---|---|---|
| ARC-3.9 | look at the Exchanges of every Root whose backend runs every 30 seconds, and call an Exchange stuck when its process lives and its heartbeat did not move between two looks at least 90 seconds apart | New | Backend implementation/drill pending under accepted BKD-0.19; Root manager record-only listing is verified by RTM-0.6 |
| ARC-3.10 | never count time during which the Mac slept towards any limit of this specification | New | Trunk moved-clock unit: StoppingTheRun.test_a_driver_still_alive_16_seconds_after_its_stop_line_is_killed_then_and_not_later (SYL-173), Watching.test_only_sixty_awake_seconds_without_a_raise_trigger_the_end and test_a_wall_clock_jump_does_not_count_as_awake_time (SYL-176), SilentRuns.test_sixteen_minutes_without_a_first_event_uses_the_awake_clock_and_the_scaled_duration and test_a_mac_asleep_for_an_hour_does_not_add_an_hour_to_silence (SYL-178), TimeScaledWaits; Root manager unit `root.stop-awake-clock`, `root.stop-complete-clock` (SYL-183). Actual Mac-sleep drill and backend looks remain pending implementation/qualification under accepted BKD-0.19 |
| ARC-3.11 | end a stuck Exchange by force without asking, and say in its chat that it was ended because it was stuck | Changed | drill |
| ARC-3.12 | never end an Exchange because it waits for an answer or for a command the agent runs, and show what it waits for and for how long | Changed | journey |
| ARC-3.13 | show "stopping" from a stop request until the Exchange has ended, and then its true final state | Changed | journey |
| ARC-3.14 | keep what the agent had produced when an Exchange is ended by force, and let its chat take a new message afterwards | Kept | drill |

## Interface

The exact forms are in RCT-1 and RTM-0.

```ts
// in record.json under signsOfLife (RCT-1), and for each Exchange in the listing of arbol-root (RTM-0)
interface SignsOfLife {
  heartbeat: number;                 // the Trunk's counter; it only grows
  waitingFor: "driver" | "tool" | "answer" | "database" | "small-call";
  since: string;                     // ISO 8601, UTC: since when it waits for that
}

// arbol-root stop <exchange> [--force]
interface StopResult {
  root: string;                      // "sapling"
  exchange: string;
  ended: "cancelled" | "interrupted" | "completed" | "failed" | "saved" | "none";   // saved: the folder went before the end could be read, or settling printed none; none: it had ended already, or is unknown
  forced: boolean;                   // true: a signal was sent to the Trunk's process group
  settling?: SettleOutcome;          // what settling printed, or the refusal that kept it from running (RTM-0)
}
```

## Known problems in version 1

Not to be reproduced.

- **No limit of any kind.** A silent turn held its processes until someone stopped it.
- **A scan that only marked.** A chat was called stalled after 15 minutes, and nothing was done about it.
- **"Running" for ever.** When the end of a turn could not be recorded, the chat stayed running and could not be used.
- **Two opinions on "running".** The window and the coordinator could disagree, and the dialog "Stop current response?" appeared on chats that were idle.
- **Repair by script.** About fifteen one-off programs, keyed to single turns, were the way out of a stuck chat.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/03-turn-execution.md#Sending while running, and several sessions at once`
- `arbol_deprecated_v1:product-spec/03-turn-execution.md#Known problems and lessons`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#2. One turn's failure could block everything else`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#Product guarantees the rewrite must keep`

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| ARC-D57 | Is a stuck Exchange ended automatically, or only when the Leather Bag says so? | Automatically. A stuck Trunk is doing nothing by definition, so nothing is lost, and what had arrived is kept. Arbol says in the chat that it was ended because it was stuck. The alternative: Arbol only marks the chat as stuck and offers a button | Decided 13 October 2026 by the owner: the proposed default |
| ARC-D58 | What counts as stuck, and after how long? | Only a heartbeat that stands still while the process lives: 60 seconds as the Trunk sees itself, 90 seconds as Arbol sees it from outside. Waiting for an answer or for a command the agent runs is never stuck, however long it lasts | Decided 13 October 2026 by the owner: the proposed default |
| ARC-D59 | Does a Trunk end itself when its own work hangs? | Yes, after 60 seconds without a heartbeat. It is the only watch that works while Arbol is not running. The alternative: only Arbol watches, and a hung Trunk stays until Arbol runs again | Decided 13 October 2026 by the owner: the proposed default |
| ARC-D60 | What happens when a stop is not obeyed? | After 20 seconds the same `arbol-root stop` ends the Trunk's processes by force. The Exchange is then shown as interrupted, not as cancelled. The 20 seconds leave room for the 15 seconds a Driver may take to stop a run | Decided 13 October 2026 by the owner: the proposed default |
| ARC-D61 | What does Arbol do about an Exchange that waits for hours for a command the agent runs? | Nothing by itself. A UI shows what the Exchange waits for and for how long, and the Leather Bag stops it. The alternative: a limit after which Arbol stops it, or asks | Decided 13 October 2026 by the owner: the proposed default. Narrowed 15 October 2026 by [RCT-D30](../../arbol-root/contract/02-starting-stopping-and-settling.md#decisions): the Trivial Trunk ends a run that gives no event for 16 minutes also while a command left in the background runs ([TRV-0](../../arbol-trunk/trunks/trivial/specs/00-the-trivial-trunk.md)); telling such commands apart is for future Trunks |
