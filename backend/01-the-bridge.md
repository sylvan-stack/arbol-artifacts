---
role: authored
spec: BKD-1
status: accepted
---
# Arbol backend · 01 The Bridge

The *[Bridge](../GLOSSARY.md#bridge)* is how a window of an Arbol [UI](../GLOSSARY.md#ui) talks to the [Arbol backend](00-the-arbol-backend.md) of its [Root](../GLOSSARY.md#arbol-root). The window's *page*, a web page loaded from the UI's renderer bundle into a web view of the Arbol Swift App, sends *calls*, such as "send this message", and *subscriptions*, such as "tell me everything that happens in this chat"; the backend replies to each call once and sends the events of each subscription until it is ended. The Swift App carries every message unchanged between the web view and the backend's socket. For example, a window that opens the chat "What build.sh does" subscribes with `{"type":"subscribe","id":"s2","topic":"chat","params":{"chat":"c3d4e5f6-…"}}` and receives first the chat as it is saved, then the lines of the answer still arriving in its [Chat Exchange](../GLOSSARY.md#chat-exchange), one batch at a time. This specification states the messages and their form, how they travel, calls and their errors, subscriptions and how a window keeps the truth, sending and sending again, attention items, a backend that goes away, compatibility within a Root, secrets, what the Swift App answers itself, and how the window runs before the Swift App exists. It matters because in version 1 errors came back in three different shapes, a delivered update was not an acknowledged one, background windows missed updates without noticing, and every fix for a stale window added another way of reconciling.

It follows the conventions of the [Driver Contract](../driver-contract/README.md#conventions) and the additions in this chapter's [README](README.md#conventions). It makes exact what [ARC-0](../architecture/00-components-and-boundaries.md#arbol-the-swift-app-and-the-backend) says of the Bridge: the Swift App passes every call and subscription on to the backend, over a socket file in the Root's folder that only the owner can open, and does not interpret what it passes on. The forms are technical choices made on 18 October 2026.

## Scope

Covered: the messages, how they travel, calls, subscriptions, sending and repeating, attention, a backend that goes away, compatibility within a Root, secrets, what the Swift App answers itself, the time before the Swift App exists.

Not covered: what the backend does for each call ([BKD-0](00-the-arbol-backend.md)); what the window shows ([BKD-2](02-elma-chat.md)); how the Swift App loads a renderer bundle, opens and closes windows and starts backends, and its own requirement to read nothing it passes on (ARC-0.6; SYL-192); the calls of Seqoya Lab and of Brain Recipes (SYL-194, SYL-191).

## Behaviour

### The messages

Every message is one JSON object with a `type`:

| `type` | From | What it is |
|---|---|---|
| `hello` | The backend | The first message on every connection: the Bridge's version, the Root and the backend's Build |
| `call` | The window | A request with a `method` and its `params`, such as `chat.send` |
| `reply` | The backend | The one reply to a call: its `result`, or its `error` |
| `subscribe` | The window | A request for the events of a `topic`, such as `chat` with the chat's identifier |
| `event` | The backend | One event of a subscription, numbered |
| `unsubscribe` | The window | The end of a subscription the window no longer needs |
| `ended` | The backend | The end of a subscription by the backend, with an error when it failed |
| `lost` | The Swift App | The connection to the backend has ended |

The window chooses the `id` of each call and each subscription, a string unique within its connection, such as `"c17"` or `"s2"`; the backend's `reply`, `event` and `ended` carry it back.

```json
{"type":"call","id":"c17","method":"chat.rename","params":{"chat":"c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b","title":"What build.sh does"}}
{"type":"reply","id":"c17","result":{"title":"What build.sh does"}}
{"type":"call","id":"c18","method":"chat.rename","params":{"chat":"00000000-0000-4000-8000-000000000000","title":"x"}}
{"type":"reply","id":"c18","error":{"code":"not_found","message":"No chat 00000000-0000-4000-8000-000000000000 in First Sapling."}}
```

### How they travel

```text
page (in a web view)  ──postMessage(text)──▶  Arbol Swift App  ──one line──▶  backend.sock  ──▶  Arbol backend
page                  ◀──receive(text)─────  Arbol Swift App  ◀──one line──  backend.sock  ◀──  Arbol backend
```

| Leg | Form |
|---|---|
| Page to Swift App | `window.webkit.messageHandlers.arbol.postMessage(text)`, where `text` is the message as a JSON string. A string, not an object, so that nothing of the page's own objects is lost on the way |
| Swift App to page | The Swift App calls `window.arbolBridge.receive(text)` with the message as it came |
| Swift App to backend and back | One connection to the Root's `backend.sock` for each window. Each message is one line of UTF-8 JSON ending with a newline, at most 16 MiB. Both ends read lines up to that size, and close a connection whose line is longer |

The Swift App passes every message on unchanged, in the order it came, and reads none of them; it adds only `lost` ([below](#when-the-backend-goes-away)). It passes a message from a page on only when it comes from the main frame of the page that it loaded from the renderer bundle, so that nothing else that might be shown in the web view reaches the backend. A window belongs to one Root, and its connection goes to that Root's backend only. The connection itself says which window a message comes from, so when a window closes, its connection closes, and the backend ends its subscriptions. What the Bridge needs of the Swift App, here and below, is stated so that its specification (SYL-192) can take it over, and is checked with it.

<!-- sources:
arbol:src/arbol_backend/bridge.py#encode
arbol:src/arbol_backend/bridge.py#decode
arbol:src/arbol_backend/bridge.py#Connection.run
arbol:tests/backend/test_bridge.py#Wire.test_complete_line_boundary_and_hello_first
arbol:tests/backend/test_bridge.py#Wire.test_malformed_frames_close_privately
-->

### Hello

```json
{"type":"hello","bridge":1,"root":{"root":"sapling","name":"First Sapling","status":"working","current":true},"build":"6"}
```

| Field | What the window does with it |
|---|---|
| `bridge` | The version of the Bridge, 1. A window that speaks another version shows that it cannot work with this backend, and sends nothing |
| `root` | The Root's identifier, display name, state and whether it is current, for the header ([BKD-2](02-elma-chat.md#the-window)) |
| `build` | The Build the backend runs from. When the window's page came from another Build, for example because a newer one was installed while the window stayed open, the window saves every Draft it holds, waits until no `chat.send` and no `exchange.sendAgain` of it is pending, and reloads its page with `?reloadedFor=<build>` in its address, so that the Swift App loads the bundle of the Build that runs (SYL-192). It reloads at most once for each Build. When it still differs, the window carries on: within a Root a later Build only adds ([below](#compatibility-within-a-root)) |

Only a new Root raises the version of the Bridge: a change that older Builds cannot ignore makes a new Root (ARC-1).

<!-- sources:
arbol:ui/elma/src/bridge.ts
arbol:tests/ui/bridge.mjs
-->

### Calls

A call gets exactly one reply. The window gives every call a time limit of its own, as the table of methods says ([Interface](#interface)), after which it treats the call as failed with `no_answer`; the backend's reply, when it still comes, is then ignored.

An error has the form `{"code", "message"}`, and for an error that the backend passes on from another program, `source` names that program: `trunk`, `root-manager`, `roots` or `driver`. The message is in plain words and names what it concerns. For example, a message sent to a chat whose answer is still running:

```json
{"type":"reply","id":"c21","error":{"code":"chat_busy","source":"trunk","message":"The chat has an Exchange in progress: 6e2f1a0b-3c4d-4e5f-8a6b-7c8d9e0f1a2b"}}
```

The backend's own codes are in the [Interface](#interface). A code passed on is the code of the program it came from (RCT-2, RTM-0, DRV-4). A window shows a code it does not know with its message.

The backend checks every identifier a call names before it touches a file or starts a program: a chat or an Exchange is a UUID written in lower case with hyphens (RCT-0), a Driver is one whose launcher is in the folder of the launchers, and a Subscription is one the Driver gave. Anything else is refused with `invalid_input`. For example, `"exchange":"../../x"` reaches no file.

<!-- sources:
arbol:src/arbol_backend/bridge.py#Registry
arbol:src/arbol_backend/bridge.py#Connection.call
arbol:src/arbol_backend/bridge.py#uuid_id
arbol:src/arbol_backend/bridge.py#driver_id
arbol:src/arbol_backend/bridge.py#subscription_id
arbol:tests/backend/test_bridge.py#Wire.test_calls_independent_one_reply_and_additive_fields
arbol:tests/backend/test_bridge.py#Wire.test_identifiers_before_effects_and_reused_id
-->

### Subscriptions

A subscription starts with one event that holds the present state of its topic, the *snapshot*, and goes on with the changes. Every event of a subscription carries `seq`, which counts from 1 without gaps:

```json
{"type":"subscribe","id":"s2","topic":"chat","params":{"chat":"c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b"}}
{"type":"event","id":"s2","seq":1,"event":{"kind":"snapshot","chat":{…},"exchanges":[…],"more":false,"draft":{…}}}
{"type":"event","id":"s2","seq":2,"event":{"kind":"exchange","exchange":{"exchange":"9b3a2c1e-…","state":"running","waitingFor":"driver","since":"2026-10-18T09:30:01.204Z"}}}
{"type":"event","id":"s2","seq":3,"event":{"kind":"lines","exchange":"9b3a2c1e-…","lines":[{"n":1,"event":{…"type":"started"…}},{"n":2,"event":{…"type":"text_delta","text":"Let me "}}]}}
```

The backend registers a subscription before it reads its snapshot, and sends nothing of it before the snapshot, so that no change falls between the two. A connection has one subscription for each topic and its params; a newer one ends the older. When more than 64 MiB wait to be sent on a connection, because its page does not read them, the backend ends that connection's subscriptions with `slow_reader`.

The window keeps the truth this way:

| Rule | Detail |
|---|---|
| A snapshot replaces | The window shows what the snapshot says and forgets what it showed before for that topic. It keeps where the Leather Bag scrolled to and which tool calls are open |
| A gap re-reads | A window that finds a `seq` missing starts the subscription again, which brings a new snapshot. A message handed to a web page is not acknowledged, so a lost one is noticed only this way |
| Coming back into view checks | A window that was hidden or minimised, and is shown again, calls `subscriptions.check`, which gives the last `seq` the backend sent on each of its subscriptions, and starts again each subscription it is behind on, because macOS may hold a hidden page back without anyone noticing |
| The database returns | The backend sends a new snapshot on every subscription. A window starts again each subscription that ended with `database_unavailable` when the attention item `database_unreachable` closes |
| No polling | Apart from these, the window reads nothing again on a timer |

The topics are in the [Interface](#interface). For a chat, the snapshot holds the last 12 Exchanges as the chat tables have them, as version 1 opened a chat, with `more` true when there are older ones, which `chat.exchanges` gives; a tool call's input and result in it are cut to 8 KiB, marked `cut`, and `toolCall.get` gives them whole when the call is opened. A chat that does not exist yet has an empty snapshot, with its Draft when it has one, never `not_found`. For an Exchange that is still open, the snapshot holds only the Leather Bag's message, and the answer comes only as lines: the backend sends every line of its `events.jsonl` from the first one on, whole and unchanged, in order, leaving out when it catches up only the pieces of a block that is whole in the file (BKD-0). So a window opened late, opened again or opened twice shows the whole answer so far (ARC-2). The window ignores a line whose `n` it already has. When the Exchange is saved, an event `saved` brings its rows as the chat tables have them. The backend also sends an event `exchange` for every Exchange of the chat whose folder appears, whoever started it.

One message stays within 16 MiB: the backend splits a batch of lines into several events where needed. A single line of `events.jsonl` larger than that is sent as `{"n", "tooLarge": true, "bytes"}`, and the window says that this part is too large to show here.

<!-- sources:
arbol:src/arbol_backend/bridge.py#Snapshot
arbol:src/arbol_backend/bridge.py#Topic
arbol:src/arbol_backend/bridge.py#Subscription.begin
arbol:src/arbol_backend/bridge.py#Connection.subscribe
arbol:src/arbol_backend/bridge.py#Connection.check_waiting
arbol:src/arbol_backend/bridge.py#Connection.send
arbol:tests/backend/test_bridge.py#Wire.test_registered_snapshot_race_and_cutoff
arbol:tests/backend/test_bridge.py#Wire.test_exact_backlog_boundary_includes_transport_and_pending
arbol:tests/backend/test_bridge.py#Wire.test_real_slow_socket_isolated_and_buffered_snapshot_bounded
arbol:tests/backend/test_bridge.py#Wire.test_receipt_counts_handoff_not_queue
-->

Live chat replay/control follows BKD-D32. Every snapshot replaces the file replay generation, so open Exchanges are replayed from their first complete line after a replacement snapshot. File event numbers remain the producer's n; Bridge seq remains gapless. Oversized markers count original UTF-8 file bytes including LF and also cover wrapper overflow. A stop that waits for a long pending start can outlive the window's120-second deadline; the backend keeps that shared task, and a repeated call joins it. No stopped state is inferred from a missing reply. Answers support only the current question's listed options (no free text), empty selections for no-option questions, or decline; a control write is not proof that the Driver took it.

<!-- sources:
arbol:ui/elma/src/bridge.ts
arbol:tests/ui/bridge.mjs
arbol:tests/ui/live_browser.mjs
-->

### Backend protocol details (BKD-D29)

The 16 MiB limit counts the complete encoded line, including its final LF, in both directions. Only UTF-8 JSON objects are accepted; duplicate keys, non-finite numbers, invalid UTF-8, malformed JSON and an unfinished line at EOF close that connection without reflecting the input. Unknown fields and unknown message kinds are ignored. A call or subscription id is a nonempty string of at most 128 UTF-8 bytes without control characters, unique across calls and subscriptions for the lifetime of the connection. Reuse, an uncorrelatable envelope, or more than 65,536 ids closes the connection: no duplicate reply or side effect is possible. With a valid fresh id, a malformed known request gets `invalid_input` (`reply` for a call, `ended` for a subscription). Unknown methods/topics get `unknown_method`. An unsubscribe references an existing subscription id and does not allocate a new one. Unknown unsubscribe ids are harmless.

Calls run independently. Methods and topics have parameter validators which return only known fields, before any effect; those normalized params also define subscription replacement. UUID validators accept only canonical lower-case hyphenated UUIDs; Driver and Subscription validation uses a previously obtained launcher/catalogue set, never a path made from unvalidated input. Errors have fixed backend messages; only explicitly constructed forwarded errors carry `source`. Raw input, child output, database exceptions, credentials, configuration records and unknown fields are never logged or copied into replies. Root headers contain only the stated RootInfo fields; a failed Root exposes its failure time with a fixed safe reason, not an arbitrary diagnostic string from disk. This boundary prevents accidental credential fields from escaping; credentials must never be put in a Root display name or other user-visible content.

A topic snapshot returns its publication version with the state read at that version. Registration precedes the snapshot read. Publications during that read are buffered; those at or before the snapshot's version are already represented and are discarded, and later publications follow the snapshot. Sequence numbers are allocated in the resulting send order, starting at 1. A receipt advances when the writer hands the frame to the transport, not when it queues it and not when the page acknowledges it. Ending/replacing a subscription cancels its snapshot and prevents later events from that generation. Already queued events stay ahead of its `ended` frame.

The connection owns a single writer and counts stored encoded frames, buffered publication payload bytes and the transport's write buffer. More than 64 MiB triggers `slow_reader` for all its subscriptions; queued data is discarded to make room for those terminal notices. If those notices cannot drain in one second, that connection closes. No other connection is affected. A frame that cannot fit in 16 MiB ends its subscription with `invalid_input`, or gives a call a fixed `invalid_input` reply; it is never split as arbitrary JSON. Topic-specific batching of Exchange lines belongs to SYL-251.

`root.get` returns `{root: RootInfo, layoutComplete: boolean}`. Completeness means that the four BKD-0 backend tables and `drafts_revision` sequence exist in `public`, not that every future migration has been applied; a database failure gives an error, never `false` or a healthy result. `roots.list` returns `{roots: [{root: RootInfo}, ...]}` at this stage; SYL-252 adds Exchange discovery. Each catalogue access re-runs `arbol-roots list`; simultaneous accesses share only the same in-flight call, never a persisted current selection. `hello` waits for that bounded catalogue read and is always the first frame; if no valid Root header can be obtained the connection closes without an invented current flag. The root observer starts while windows are connected, reads local metadata and the current catalogue independently of calls, and publishes name/state/current changes on a four-second cycle with a catalogue deadline of 0.8 seconds, within five seconds. A failed observation ends affected root subscriptions with a safe error; the window can resubscribe. Neither database reads nor a slow window hold up metadata observation or other calls.

<!-- sources:
arbol:src/arbol_backend/roots.py#Roots
arbol:src/arbol_backend/server.py#Backend.monitor
arbol:src/arbol_backend/process.py#Programs.kill
arbol:tests/backend/test_bridge.py#RootWire
arbol:tests/backend/test_bridge.py#Diagnostics
arbol:scripts/check_backend.py#main
-->

### Sending and repeating

Draft scope, exact bigint revisions, conflict null, send ownership, accepted-mark reconciliation, shared dispatch/request lifetime and result/refusal validation follow BKD-D31. The renderer implementation of BKD-D37 decodes revision/baseRevision integers exactly and encodes their numeric tokens exactly, including beyond JavaScript’s safe integer range; quoted numeric strings do not replace the wire integers. A folder key is normalized absolute and can still be read after its repository disappears; sending separately requires an existing workingFolder. A stale or differently marked Draft cannot be overwritten or stolen by a fresh dispatch. Equivalent in-flight callers join, and a known accepted identifier can be replayed after its Draft is gone.

The development relay reselects the Root’s newest working Arbol Build when serving the renderer document, so the new-Build reload obtains the new renderer. Already-served Builds remain eligible only as fallback roots for their immutable hashed assets while the relay lives; the document itself always comes from the current selection. Private explicit bundle/socket overrides stay fixed. Selection reads Build metadata only, starts no component, and retains the existing loopback/authentication/path boundaries. A new selection without a usable renderer fails visibly rather than claiming a new renderer was loaded.

The window chooses the identifier of a new Exchange, a UUID, before it calls `chat.send` or `exchange.sendAgain` ([BKD-D7](00-the-arbol-backend.md#decisions)). When the call fails with `disconnected`, or with `no_answer`, the window sends the same call again, with the same identifier, once the backend is back. The Trunk replies with the Exchange it accepted, marked as a repeat, or accepts it then; the message never runs twice (RCT-2). The window's time limit for these two calls, 150 seconds, is longer than the backend's longest attempt (BKD-0).

```json
{"type":"call","id":"c30","method":"chat.send","params":{"chat":"c3d4e5f6-…","exchange":"9b3a2c1e-5c6d-4f70-9a1b-2c3d4e5f6a7b","message":"Add a --clean option to it.","route":{"driver":"claude","subscription":"anthropic","model":"sonnet","effort":"high"},"workingFolder":"/Users/sam/repos/shop","draft":{"revision":41}}}
{"type":"reply","id":"c30","result":{"accepted":true,"duplicate":false,"exchange":"9b3a2c1e-…","chat":"c3d4e5f6-…","number":3}}
```

| Calls | Sent again after `disconnected` or `no_answer` |
|---|---|
| `chat.send`, `exchange.sendAgain` | Yes, with the same Exchange identifier |
| `root.get`, `roots.list`, `chats.page`, `chat.exchanges`, `toolCall.get`, `subscriptions.check`, `draft.get`, `chat.rename`, `chat.settings`, `chat.mark`, `exchange.stop`, `accounts.*`, `health.measure` | Yes: they have the same effect when sent twice |
| `paste.save` | Yes: a second file with the same text does no harm, and the window uses the path of the reply it gets |
| `draft.save` | Yes, over the same revision, so that a save that was made already is refused with `draft_conflict` and brings the Draft as it is, which the window takes without asking when it holds the composer's own text |
| `exchange.answer` | Only when the lines of the Exchange hold no `answer` line for that `askId`; otherwise the answer arrived |
| `chat.reimport` | No automatic repeat after disconnected/no_answer; refresh the list and report an uncertain result before another explicit action |

<!-- sources:
arbol:src/arbol_backend/drafts.py#Drafts
arbol:src/arbol_backend/dispatch.py#Dispatch.send
arbol:src/arbol_backend/dispatch.py#Dispatch.result
arbol:tests/backend/test_drafts.py#Drafts
arbol:tests/backend/test_dispatch.py#Sending
arbol:ui/elma/src/wire-json.ts
arbol:ui/elma/src/drafts.svelte.ts
arbol:ui/elma/src/sending.svelte.ts
arbol:tests/ui/sending.mjs
arbol:tests/ui/send_browser.mjs
arbol:tests/ui/send_reload_browser.mjs
arbol:tests/ui/failure_browser.mjs
-->

<!-- sources:
arbol:src/arbol_backend/bridge.py#Subscription.send
arbol:src/arbol_backend/live.py#Live.follow
arbol:src/arbol_backend/live.py#Lines.flush
arbol:src/arbol_backend/controls.py#Controls.stop
arbol:src/arbol_backend/controls.py#Controls.result
arbol:src/arbol_backend/answers.py#Answers.write
arbol:src/arbol_backend/settling.py#Settling.work
-->

Database-outage attention, retained existing chat streams, fresh recovery snapshots and metadata-only Discovery follow BKD-D33. An optional explicit root on exchange.stop routes only to a catalogue Root's own manager; omission remains own-Root and no UUID lookup changes it. Foreign stop status never appears as this Root's chat content. Unknown Root/refusal codes remain safe errors with their source. New SQL chat subscriptions and Draft writes while away fail database_unavailable; existing chat subscriptions stay alive and receive no fabricated saved end. Recovery snapshots reset each subscription's replay generation.

### Attention

An *attention item* is something that is not a normal state and that every window of the Root shows for as long as it lasts ([ARC-D53](../architecture/02-chat-exchange-across-components.md#decisions)). The topic `attention` gives them: a snapshot of every item open now, and then each item as it opens and as it closes.

| `kind` | When | Example of its message |
|---|---|---|
| `database_unreachable` | The database cannot be reached (BKD-0) | "The database server does not answer at 127.0.0.1:5433. New messages cannot be sent; answers in progress go on." |
| `space_low` | Less than 10 GiB is free on the disk of the database; `severity` `urgent` below 2 GiB (BKD-0) | "8.6 GiB left on the disk of the database. First Sapling's chats take 3.2 GiB." |
| `layout_incomplete` | The Root's database lacks the backend's own tables (BKD-0) | "First Sapling's database lacks the table drafts: Drafts are not kept. Run arbol-roots layout sapling." |
| `migration_unavailable` | Comparing the older Root failed; saved marks remain last-known | "The original chats could not be checked. Saved chats are still available." |

A window shows an item of a kind it does not know with its message.

<!-- sources:
arbol:src/arbol_backend/health.py#Health
arbol:src/arbol_backend/chats.py#Chats.attention_snapshot
arbol:src/arbol_backend/recovery.py#Recovery.refresh
arbol:src/arbol_backend/recovery.py#Recovery.returned
arbol:src/arbol_backend/bridge.py#Subscription.send
arbol:src/arbol_backend/discovery.py#Discovery
arbol:src/arbol_backend/controls.py#stop_params
arbol:tests/backend/test_return.py#Returned
arbol:tests/backend/test_discovery.py#AcrossRoots
arbol:tests/backend/test_health.py#Availability
-->

### When the backend goes away

When the connection to the backend ends, because the backend ended or was restarted, the Swift App tells the window with `{"type":"lost"}`, connects again as soon as the backend listens, and the backend's `hello` on the new connection says that it is back (SYL-192).

| | The window |
|---|---|
| While it is lost | Keeps showing what it shows, says that it is reconnecting, and keeps every Draft typed meanwhile to save it later |
| Calls under way | Fail with `disconnected`, and are sent again after the next `hello` as [above](#sending-and-repeating) says |
| After the next `hello` | Starts every subscription again, so each begins with a new snapshot, and saves the Drafts it kept |

So a missed update never leaves a window stale: the window reads the truth again ([ARC-2](../architecture/02-chat-exchange-across-components.md#when-arbol-quits)). No Exchange stops because the backend went away (BKD-0).

Accounts and storage measurements follow BKD-D34: allowlisted public Driver projections and safe driver-scoped errors, fresh shared reads, no credential/sign-in channel, and bounded partial Measurement replies with optional catalogueProblem/diskProblem. A failed Root size or unconfirmed local disk has no fabricated zero. Account and storage work never delays another topic or overwrites database-return/replay ownership.

<!-- sources:
arbol:src/arbol_backend/accounts.py#Accounts
arbol:src/arbol_backend/account_data.py#Public
arbol:src/arbol_backend/measurements.py#Measurements
arbol:src/arbol_backend/metadata.py#Attention.open
arbol:tests/backend/test_account_actions.py#Actions
arbol:tests/backend/test_space_watch.py#Watching
-->

<!-- sources:
arbol:ui/elma/src/bridge.ts
arbol:ui/elma/src/window.svelte.ts
arbol:tests/ui/live_browser.mjs
-->

On development-relay shutdown, stop accepting new connections, close browser writers and cancel/join their handlers, then wait for the listener to close. This ordering includes still-open WebSockets: waiting for server closure before closing its active clients can deadlock on the pinned Python runtime. The relay must exit quietly with a connected browser. The regression is `RelayChecks.test_process_prints_only_bootstrap_and_quiet_shutdown`: it keeps an authenticated WebSocket and its private backend connection open during SIGTERM and requires quiet exit plus EOF within two seconds.

<!-- sources:
arbol:tools/bridge_relay.py#Relay.close
arbol:tests/ui/test_relay.py#RelayChecks.test_process_prints_only_bootstrap_and_quiet_shutdown
-->

### Compatibility within a Root

The renderer bundles and the backend of a Root come from that Root's `arbol` Builds, and a window and its backend may come from different Builds of the same Root, for example after a new Build while a window stayed open. Within a Root the Bridge therefore changes only by additions that older Builds can ignore: a new method, topic, event kind, field or error code. Nothing is removed, and nothing changes its meaning (ARC-1). Both sides ignore a field, an event kind and an attention kind they do not know; the backend replies to a method or a topic it does not know with `unknown_method`, and the window says that this needs a newer Build.

### Secrets

No secret crosses the Bridge, in either direction: no key of a Subscription, no Jev key and no database password. The Leather Bag signs in with the Driver's own command at the terminal, which reads a key from its Keychain item (BKD-0, [BKD-D17](02-elma-chat.md#decisions)). Neither the backend nor the Swift App writes a secret to a log (ARC-0, "Secrets").

<!-- sources:
arbol:src/arbol_backend/bridge.py#safe_error
arbol:src/arbol_backend/roots.py#Roots.info
arbol:src/arbol_backend/roots.py#Roots.catalogue_outcome
arbol:tests/backend/test_bridge.py#Diagnostics.test_private_process_never_logs_input_or_root_diagnostics
arbol:tests/backend/test_bridge.py#RootWire.test_cancelled_catalogue_does_not_log_a_late_failure
-->

The renderer action/open integration follows BKD-D38: it saves its visible Draft and waits for unconfirmed sends before consuming app.takeOpen, serializes native open notices, retains the returned routing target through a failed read, and includes the transition in its Build reload barrier. This adds no backend app-channel message and no credential entry.

### What the Swift App answers itself

A web page cannot open the Mac's folder dialog and should not leave its own page to follow a link, and a request to open a chat comes from outside the page. The window and the Swift App speak about these on a channel of their own, the *app channel*, which is not the Bridge and never reaches the backend: `window.webkit.messageHandlers.arbolApp.postMessage(text)`, answered with `window.arbolApp.receive(text)`, in the form of a call and its reply, and one message the Swift App sends by itself. Their exact form is the Swift App's specification (SYL-192), and the proposal is:

| Request | Params | Result |
|---|---|---|
| `app.pickFolder` | `start`: the folder the dialog opens in | `{"folder": "/Users/sam/repos/shop"}`, or `{"folder": null}` when the Leather Bag cancelled |
| `app.openLink` | `url`, an `http` or `https` address | `{}` once the Mac's default browser has it. Any other scheme is refused |
| `app.takeOpen` | — | The request to open a chat that waits for this window, `{"chat": "c3d4e5f6-…"}`, or `{"folder": "/…/readonly/shop"}` for a new chat in a repository, or `{}` when none waits. The Swift App keeps a request from Willo Station, from its latest chats or from its global keys until a window takes it, so that one made while the window loads is not lost |
| The message `{"type":"open"}` | From the Swift App | Tells a window that is open that a request waits; the window takes it with `app.takeOpen` |

The web view of a window never leaves its page: the Swift App refuses every navigation away from the renderer bundle, so a link in an answer that the agent wrote, such as one a file it read put there, cannot take the window to a page that would then reach the Bridge.

<!-- sources:
arbol:ui/elma/src/app-channel.ts
arbol:tests/ui/bridge.mjs
arbol:tests/ui/response.mjs
-->

### Window bootstrap additions (BKD-D36)

The read-only call workspace.get gives the window repository slots and safe route defaults without exposing the settings file or requiring a filesystem channel in the page. It returns `{repositories: [{name, folder, route}], route}`, with the stack's readonly folder first, then actual Git repository directories immediately under readonly, in name order. Symlinked entries and hidden/non-repository directories are excluded so a slot cannot redirect to a named work area. The window puts its16 recently used repository names ahead of the others after the stack's own slot and chooses its first nine. Every folder is the absolute lexical readonly path; a missing/unreadable readonly directory is an honest fixed no_answer. A fresh call observes added/removed repositories; it creates, changes and books nothing. Only the validated Driver/Subscription/model/effort route fields are returned, from the existing per-repository/default settings, never the original settings object or small-call configuration. The page calls this on opening/hello, not on a timer. Its window deadline is30 seconds.

ChatInfo additionally has firstMessage, the first200 characters of the position-zero message of the first unreplaced Exchange, or an empty string. It is read in the same consistent snapshot as the chat. This makes the80-character first-line title placeholder available even when that Exchange lies outside the newest12; the placeholder is never written back as a title.

<!-- sources:
arbol:src/arbol_backend/workspace.py#Workspace
arbol:src/arbol_backend/chat_data.py#Reader.chat
arbol:src/arbol_backend/server.py#Backend
arbol:tests/backend/test_workspace.py#Bootstrap
arbol:ui/elma/src/window.svelte.ts
-->

### Before the Swift App exists

Until the Arbol Swift App exists (SYL-192), the window runs in a browser on this Mac, through a small *development relay* in the `arbol` repository, so that the window can be built and its journeys checked:

```sh
python tools/bridge_relay.py --root sapling
# http://127.0.0.1:53114/?token=4f0c…   open this address in a browser
```

The relay serves the renderer bundle of the Root's newest working `arbol` Build over HTTP on the loopback address only, and relays each message of a WebSocket at `/bridge` as one line to `backend.sock` and back, unchanged. Every program and every web page on the Mac can reach the loopback address, so the relay lets in only the browser it printed the address for:

| Rule | Detail |
|---|---|
| The token | 128 random bits, made anew at each start of the relay |
| The first request | The one that carries `?token=` gets a cookie that is `HttpOnly` and `SameSite=Strict`, and is sent on to the same address without the token |
| Every request | Needs that cookie, compared in constant time, and the `Host` `127.0.0.1:<port>`; the WebSocket also needs the `Origin` `http://127.0.0.1:<port>`. Anything else is refused |
| Its log | Holds no message |

When `window.webkit` is missing, the page uses that WebSocket instead. The relay answers the app channel itself: `app.pickFolder` with a field in which a folder is typed, `app.openLink` by opening the address in a new tab of the browser, and `app.takeOpen` with the chat named by `?open=<chat>` in the address it was opened with. It is for development and checks only, never for daily use. A check that needs the Swift App itself, such as opening a chat from Willo Station, waits for SYL-192.

<!-- sources:
arbol:tools/bridge_relay.py
arbol:tests/ui/test_relay.py#RelayChecks
arbol:tests/ui/relay_browser.mjs
-->

## Requirements

| ID | The Bridge must… | Origin | Verified by |
|---|---|---|---|
| BKD-1.1 | carry only the messages `hello`, `call`, `reply`, `subscribe`, `event`, `unsubscribe`, `ended` and `lost`, each one JSON object, with the `id` of a call or a subscription chosen by the window and unique within its connection | Changed | unit `bridge.frames`, `bridge.calls`, `bridge.correlation`, `bridge.subscription-end`; Swift `lost` remains SYL-192 |
| BKD-1.2 | travel from the page as a JSON string through `window.webkit.messageHandlers.arbol`, to the page through `window.arbolBridge.receive`, and between the Swift App and the backend as one line of UTF-8 JSON of at most 16 MiB on one connection to the Root's `backend.sock` for each window, a longer line closing the connection; and reach the backend only from the main frame of the page loaded from the renderer bundle | Changed | backend unit `bridge.frames`, `bridge.malformed`, `bridge.output-boundary`; Swift/main-frame relay remains SYL-192 Renderer native JSON-string adapter/framing/correlated independent call lifetime: `tests/ui/bridge.mjs`; actual Swift web view remains SYL-192. (SYL-254; real Chromium/loopback HTTP-WebSocket/private Unix backend stand-in; native Swift host, installed Root/Trunk/vendor journeys remain SYL-192/SYL-257). |
| BKD-1.3 | begin every connection with `hello`, giving the Bridge's version, the Root and the backend's Build; have a window refuse another version of the Bridge, and, when its page came from another Build, save its Drafts, wait for its sends and reload once for that Build | New | backend unit `bridge.frames`, `bridge.root-observation`; Build reload/version refusal in the window remains SYL-254/SYL-192 Renderer version/Root/Build hello, once-per-Build reload and stale-barrier generation checks: `tests/ui/bridge.mjs`; Draft/send save barrier integration: `tests/ui/draft_recovery.mjs`, `tests/ui/sending.mjs`, `tests/ui/send_reload_browser.mjs` (SYL-255; two actual private compiled Builds, receipt/reconciliation before one navigation). (SYL-254; real Chromium/loopback HTTP-WebSocket/private Unix backend stand-in; native Swift host, installed Root/Trunk/vendor journeys remain SYL-192/SYL-257). |
| BKD-1.4 | answer every call exactly once, with `result` or with `error` of the form `{code, message}` and, for an error passed on, `source`; refuse with `invalid_input` an identifier that is not of its kind before a file is touched or a program started; have the window give each call a time limit and show a code it does not know with its message | Changed | backend unit `bridge.calls`, `bridge.errors`, `bridge.identifiers`, `bridge.correlation`, `bridge.root-get`, `chats.identifier-catalogues`, `chats.input-types`, `chats.reimport-validation`, `chats.migration-errors`; Draft/send unit `drafts.conflict-null`, `sending.validate-before-effects`, `sending.safe-errors`, `sending.error-shape`; window deadlines/error display remain SYL-254 Control boundary: `stop.forwarding`, `stop.safe-errors`, `stop.result-identity`, `answers.syntax-before-effects`, `answers.byte-limit` (SYL-251). Account command/error and identifier/privacy boundary: `accounts.public-records`, `accounts.forward-metadata`, `accounts.last-usage`, `accounts.private-projection`, `accounts.no-diagnostic-excerpt`, `accounts.unknown-usage`, `accounts.usage-units`, `accounts.safe-url`, `accounts.public-validation`, `accounts.public-bound`, `accounts.launcher-inventory`, `accounts.list-only`, `accounts.driver-records`, `accounts.driver-isolation`, `accounts.safe-refusal`, `accounts.no-raw-fields`, `accounts.shared-list`, `accounts.fresh-list`, `accounts.no-vendor-poll`, `accounts.caller-shield`, `accounts.cancel-isolation`, `accounts.total-bound`, `accounts.topic-isolation`, `accounts.global-capacity`, `accounts.reply-bound`, `accounts.oversized-driver-isolation`, `accounts.allowed-actions`, `accounts.driver-authority`, `accounts.no-inference`, `accounts.identifier-before-effects`, `accounts.fresh-membership`, `accounts.deleted-subscription`, `accounts.no-stale-action`, `accounts.public-membership-proof`, `accounts.shared-action`, `accounts.fresh-action`, `accounts.action-caller-shield`, `accounts.action-owner`, `accounts.command-bound`, `accounts.action-driver-isolation`, `accounts.check-identity`, `accounts.action-result`, `accounts.unknown-driver-code`, `accounts.process-privacy`, `accounts.no-secret-argv-log` (SYL-253; actual private PostgreSQL/filesystem, private launchers/contract request stand-ins and socket clients; no owner installation/native Driver/vendor). Actual installed Backend/Root/vendor/Swift/renderer journeys remain SYL-257. Readonly window bootstrap/first prompt: `tests/backend/test_workspace.py#Bootstrap.test_readonly_inventory_defaults_freshness_and_failure`, `Bootstrap.test_first_unreplaced_prompt_is_available_outside_page_and_never_stored_as_title` (actual private PostgreSQL/socket); lazy whole tool: `tests/ui/response.mjs`. (SYL-254; real Chromium/loopback HTTP-WebSocket/private Unix backend stand-in; native Swift host, installed Root/Trunk/vendor journeys remain SYL-192/SYL-257). |
| BKD-1.5 | register a subscription before reading its snapshot, begin it with the snapshot, number its events with `seq` from 1 without gaps, keep one subscription for each topic and params on a connection, end a connection's subscriptions with `slow_reader` above 64 MiB waiting; have the window start a subscription again when it finds a gap, when `subscriptions.check` shows it behind after being hidden, and when the database returns | Changed | backend unit `bridge.snapshot-race`, `bridge.subscription-end`, `bridge.topic-params`, `bridge.receipts`, `bridge.backlog-boundary`, `bridge.slow-reader`, `bridge.disconnect`, `chats.view-generation`, `chats.view-isolation`, `chats.mutation-publication-order`; Draft topics unit `drafts.subscriptions`, `drafts.capture-acceptance-race`; database-return snapshots remain SYL-252 and window recovery journey SYL-254/SYL-257 Renderer seq gaps/replaced subscriptions/visibility receipts/database-ended restart: `tests/ui/bridge.mjs`; actual real-relay gap/reconnect/snapshot-reset: `tests/ui/live_browser.mjs`. (SYL-254; real Chromium/loopback HTTP-WebSocket/private Unix backend stand-in; native Swift host, installed Root/Trunk/vendor journeys remain SYL-192/SYL-257). |
| BKD-1.6 | give in a chat's snapshot the last 12 Exchanges, tool inputs and results cut to 8 KiB, the chat's Draft, settings and marks, and for an open Exchange only its message; send every line of `events.jsonl` of each Exchange in progress from the first one on, whole, unchanged and in order, a line larger than 16 MiB as `{n, tooLarge, bytes}`, then its saved rows once it is saved; and announce every Exchange of the chat whose folder appears | Changed | snapshot/read part: unit `chats.contract-assembly`, `chats.consistent-snapshot`, `chats.tool-cuts`, `chats.exchange-pages`, `chats.missing-chat`, `chats.own-root-provenance`, `chats.external-observation`, `chats.title-windows`; Draft/send unit `drafts.subscriptions`, `sending.newer-text`; live lifecycle: unit `live.windows`, `live.replay`, `live.row-first`, `live.saved`, `live.outside-folder`, `live.oversized-wire`, `live.batch-boundary`, `live.snapshot-generation`, `live.slow-window-isolation` (SYL-251); actual window journey remains SYL-257 |
| BKD-1.7 | when the connection ends, have the window, told by `lost`, keep showing what it shows and the Drafts typed meanwhile, fail its calls under way with `disconnected`, and after the next `hello` start every subscription again and send its calls again as the table of repeating says, `chat.send` and `exchange.sendAgain` with the same Exchange identifier | Changed | backend unit `sending.repeat`, `sending.shared-dispatch`, `sending.disconnect`, `sending.detached-shutdown`, `sending.database-cleanup-recovery`; actual window lost/reload/resubscribe journey remains SYL-254/SYL-257 Control repeat/cancellation and fresh replay: `stop.shared`, `stop.shielded`, `stop.retained-manager`, `stop.repeat`, `answers.observed-delivery`, `live.windows`, `live.snapshot-generation` (SYL-251). Renderer lost/newhello retained view and fresh projection replay: `tests/ui/bridge.mjs`, `tests/ui/relay_browser.mjs`, `tests/ui/live_browser.mjs`. (SYL-254; real Chromium/loopback HTTP-WebSocket/private Unix backend stand-in; native Swift host, installed Root/Trunk/vendor journeys remain SYL-192/SYL-257).  Renderer exact send/retry receipt ownership, Draft recovery and actual Build reload gate: `tests/ui/sending.mjs`, `tests/ui/send_browser.mjs`, `tests/ui/send_reload_browser.mjs`, `tests/ui/failure_browser.mjs` (SYL-255; private stand-ins, no vendor). |
| BKD-1.8 | give every attention item open in the Root to every window that subscribes to `attention`, from its opening to its closing, and have a window show a kind it does not know with its message | New | unit `recovery.database-loss`, `recovery.attention`, `recovery.return`, `recovery.statement-timeout`, `recovery.sql-error-is-not-loss`, `recovery.connection-deadline`, `recovery.probe-bound`, `recovery.keychain-classification`, `recovery.safe-cause`, `recovery.credentials-refresh`, `recovery.retry-cadence`, `recovery.whole-probe-confirmation`, `recovery.renew-lock-bound`, `recovery.credential-lock-race`; `recovery.all-topic-snapshots`, `recovery.repeated-return`, `recovery.draft-preserved`, `recovery.draft-snapshot-race`, `recovery.saved-snapshot-race`, `recovery.epoch-race`, `recovery.live-stream-survives-return`, `recovery.independent-discovery`, `recovery.settled-note-retry`, `recovery.backend-restart`, `recovery.pending-note-snapshot`, `recovery.transient-snapshot-retry` (SYL-252; private PostgreSQL, contract files and manager stand-ins). Actual Root/Trunk/vendor/Swift/renderer and Mac-sleep journeys remain SYL-257. Unknown-kind renderer display remains SYL-255/SYL-257. Space attention/return composition: `measurement.thresholds`, `measurement.space-windows`, `measurement.urgent`, `measurement.warning-clear`, `measurement.partial-attention`, `measurement.no-false-clear`, `measurement.awake-300`, `measurement.sleep-excluded`, `measurement.wall-clock`, `measurement.request-keeps-schedule`, `measurement.return-refresh`, `measurement.return-snapshot-isolation`, `measurement.callback-composition`, `measurement.return-after-old-read`, `measurement.return-epoch`, `measurement.return-coalescing`, `measurement.shutdown`, `measurement.utility-reaped`, `measurement.no-trunk-signal` (SYL-253; actual private PostgreSQL/filesystem, private launchers/contract request stand-ins and socket clients; no owner installation/native Driver/vendor). Actual installed Backend/Root/vendor/Swift/renderer journeys remain SYL-257. Unknown-kind renderer display remains SYL-255/SYL-257. |
| BKD-1.9 | change within a Root only by additions that older Builds can ignore, have the backend and the window ignore every field, event kind and attention kind they do not know, and have the backend reply to a method or topic it does not know with `unknown_method` | New | backend unit `bridge.compatibility`, `bridge.topic-params`, `bridge.calls`; window event/attention compatibility remains SYL-254 |
| BKD-1.10 | carry no secret in either direction | Changed | backend unit `bridge.privacy`, `bridge.private-diagnostics`, `bridge.catalogue-cancel-privacy`, `backend.child-cancel-race`, `chats.contract-assembly`, `chats.identifier-catalogues`, `chats.migration-errors`, `chats.paste-wire`; send-error unit `sending.safe-errors`, `sending.error-shape`; Swift/window secrecy remains their checks |
| BKD-1.11 | keep the requests between the window and the Swift App, `app.pickFolder`, `app.openLink` and `app.takeOpen`, and the Swift App's message `open`, on a channel of their own, `arbolApp`, which never reaches the backend; keep a request to open a chat until a window takes it; and keep the web view of a window on its own page | New | unit; the Swift App's part with SYL-192 Separate native/browser app adapter: `tests/ui/bridge.mjs` (folder/new-tab/once-only URL-open/native open notice), `tests/ui/response.mjs` (safe app-only link, unchanged chat URL/no app request to backend). Native host remains SYL-192; window open/actions remain SYL-256. (SYL-254; real Chromium/loopback HTTP-WebSocket/private Unix backend stand-in; native Swift host, installed Root/Trunk/vendor journeys remain SYL-192/SYL-257). |
| BKD-1.12 | before the Swift App exists, be relayed by the development relay of the `arbol` repository on the loopback address only, letting in only requests with its cookie, its `Host` and, for the WebSocket, its `Origin`, and logging no message | New | unit `tests/ui/test_relay.py` (5 cases: token/cookie, exact Host/Origin, bounded strict WS/Unix forwarding, fragmentation/control/shutdown/no-content diagnostics, newest matching unpruned working Build); `tests/ui/relay_browser.mjs` (real Chromium HTTP/WS, cookie, no unauthorized page, CSP, lost/newhello, matching compiled Build) (SYL-254; real Chromium/loopback HTTP-WebSocket/private Unix backend stand-in; native Swift host, installed Root/Trunk/vendor journeys remain SYL-192/SYL-257). |
| BKD-1.13 | carry optional own-Root migration metadata and the bounded chat.reimport call/result, pass structured errors without secrets, and never repeat that mutation automatically after an ambiguous reply | New | backend unit `chats.own-root-provenance`, `chats.provenance-layout`, `chats.migration-check-coalescing`, `chats.migration-unavailable`, `chats.reimport-results`, `chats.reimport-coalescing`, `chats.reimport-validation`, `chats.reimport-uncertain`, `chats.migration-errors`; Root core SYL-195/SYL-247; renderer action and UI uncertainty remain SYL-256/SYL-257 |

## Interface

```ts
type BridgeMessage =
  | { type: "hello"; bridge: 1; root: RootInfo; build: string }
  | { type: "call"; id: string; method: string; params: object }
  | { type: "reply"; id: string; result: unknown }
  | { type: "reply"; id: string; error: BridgeError }
  | { type: "subscribe"; id: string; topic: string; params: object }
  | { type: "event"; id: string; seq: number; event: { kind: string } & object }
  | { type: "unsubscribe"; id: string }
  | { type: "ended"; id: string; error?: BridgeError }
  | { type: "lost" };                                   // from the Swift App alone

interface BridgeError {
  code: string;                         // the backend's own codes below, or the code of the program it came from
  message: string;
  source?: "trunk" | "root-manager" | "roots" | "driver";
  retryAfterSeconds?: number;           // passed on from a Driver's error (DRV-4)
  draft?: Draft | null;                 // with draft_conflict: current Draft, or explicit null after removal
}

interface RootInfo {
  root: string;                         // "sapling"
  name: string;                         // "First Sapling"
  status: "preparing" | "working" | "failed";
  current: boolean;
  failed?: { at: string; reason: string };
}
```

The backend's own error codes:

| Code | When |
|---|---|
| `invalid_input` | A call or subscription whose params are missing or wrong, such as a route without a model, a working folder that does not exist, an identifier that is not of its kind, or a message or Draft of more than 1 MiB |
| `unknown_method` | A method or topic this Build does not know |
| `not_found` | An Exchange, a tool call or a Subscription that does not exist |
| `database_unavailable` | The database cannot be reached (BKD-0) |
| `timeout` | A statement passed its 5 seconds on a database that answers |
| `layout_incomplete` | The Root's database lacks the backend's own tables, for a call that needs them |
| `draft_conflict` | A Draft saved over a revision that is no longer the Draft's; `draft` gives it as it is |
| `ended` | An answer to an Exchange that has ended |
| `no_answer` | A program the backend started did not reply in its time (BKD-0) |
| `slow_reader` | The end of a subscription whose page did not read what was sent |
| `disconnected` | Made by the window, never sent: the connection ended before the reply came |

The calls:

| Method | Params | Result | Time limit of the window |
|---|---|---|---|
| `root.get` | — | `{ root: RootInfo, layoutComplete: boolean }` | 30 s |
| `workspace.get` | — | `{ repositories: Array<{name: string; folder: string; route: object}>; route: object }`, read-only slots/defaults as above | 30 s |
| `roots.list` | — | `Discovery` | 30 s |
| `chats.page` | `before?`: `{ activityAt, chat }` of the oldest chat shown; `limit?`, at most 200, 100 by default | `{ chats: ChatSummary[] }`, without archived chats, older than `before`, by `activityAt` and then `chat`, both newest first | 30 s |
| `chat.exchanges` | `chat`, `beforeNumber`, `limit?`, at most 50, 12 by default | `{ exchanges: SavedExchange[]; more: boolean }` | 30 s |
| `toolCall.get` | `exchange`, `position` | the tool call whole: `{ input, result?, error? }` | 30 s |
| `subscriptions.check` | — | `{ subscriptions: Array<{ id: string; seq: number }> }`: the last `seq` sent on each | 30 s |
| `chat.send` | `chat`, `exchange`, `message`, `route`, `workingFolder`, `draft?`: `{ revision, folder? }`, the Draft it was sent from, the chat's own or, for a new chat, the Draft of the repository folder | `Accepted` | 150 s |
| `exchange.sendAgain` | `exchange` (the one replaced), `newExchange`, `route` | `Accepted` | 150 s |
| `exchange.stop` | `exchange`, optional `root` (omitted: this backend's Root; explicit other Root validated through the catalogue) | `{ ended: "completed" \| "failed" \| "cancelled" \| "interrupted" \| "saved" \| "none" }`, as `arbol-root stop` printed it (RTM-0) | 120 s |
| `exchange.answer` | `exchange`, `askId`, `answer` (DRV-3 `Answer`) | `{}` once the line is in `control` | 30 s |
| `chat.rename` | `chat`, `title`: a string, or `null` to take the title away | `{ title: string \| null }` | 30 s |
| `chat.reimport` | `chat`: canonical target copy UUID | `{ chat: resultChat, previousChat, action: "replaced" or "copied", fromRoot, fromChat }`; the global Root command owns the mutation | 120 s |
| `draft.get` | `chat`, or `folder` for the Draft of a new chat in that repository | `Draft \| null` | 30 s |
| `draft.save` | `chat`, or `folder`; `text`; `baseRevision`: the revision it was made over, `null` when there was no Draft | `{ revision: number }`, or `{ removed: true }` for an empty text | 30 s |
| `chat.settings` | `chat`, `route?`, `workingFolder?` | `{}` once saved for the chat's next message | 30 s |
| `chat.mark` | `chat`, `ongoing?`, `archived?` | `ChatMarks` | 30 s |
| `paste.save` | `text`, of 10,000 characters or more | `{ path: string }`, the file it was saved in | 30 s |
| `accounts.list` | — | `{ drivers: Array<{ driver: string; subscriptions?: Subscription[]; error?: BridgeError }> }` (DRV-1 `Subscription`) | 30 s |
| `accounts.check`, `accounts.usage`, `accounts.models` | `driver`, `subscription` | DRV-1's `Subscription`, `UsageReport`, `ModelCatalog` | 30 s |
| `health.measure` | — | `Measurement` (BKD-0) | 30 s |

<!-- sources:
arbol:src/arbol_backend/chats.py#Chats.__init__
arbol:src/arbol_backend/chats.py#page_params
arbol:src/arbol_backend/chats.py#exchange_params
arbol:src/arbol_backend/chats.py#tool_params
arbol:src/arbol_backend/migration.py#Migration.reimport
arbol:tests/backend/test_chat_wire.py#Windows
arbol:tests/backend/test_chat_migration.py#Delegation
-->

The topics:

| Topic | Params | Snapshot | Events after it |
|---|---|---|---|
| `chats` | — | `{ kind: "snapshot", chats: ChatSummary[] }`: the 100 chats that are not archived, with the newest activity, for the latest chats | `{ kind: "changed", chats: ChatSummary[] }`: each chat whose summary changed, within a second of the change (BKD-0), an archived one with `archived: true` |
| `chat` | `chat` | `{ kind: "snapshot", chat: ChatInfo, exchanges: SavedExchange[], more: boolean, draft: Draft \| null, settings: ChatSettings, marks: ChatMarks }` | `exchange` (`ExchangeStatus`), `lines` (`LinesEvent`), `saved` (`SavedExchange`), `draft` (`Draft \| null`, null once the Draft is removed), `settings`, `marks`, `title`, `note` (`ExchangeNote`) |
| `attention` | — | `{ kind: "snapshot", items: AttentionItem[] }` | `{ kind: "opened", item }`, `{ kind: "closed", id }` |
| `draft` | `chat`, or `folder` for the Draft of a new chat in that repository | `{ kind: "snapshot", draft: Draft \| null }` | `{ kind: "draft", draft: Draft \| null }`, null once the Draft is removed |
| `root` | — | `{ kind: "snapshot", root: RootInfo }` | `{ kind: "root", root: RootInfo }` when the Root's state or display name changed |

<!-- sources:
arbol:src/arbol_backend/chat_data.py#Reader.chat
arbol:src/arbol_backend/chat_data.py#Reader.summaries
arbol:src/arbol_backend/chats.py#Chats.list_snapshot
arbol:src/arbol_backend/chats.py#Chats.chat_changed
arbol:src/arbol_backend/chats.py#Chats.list_changed
arbol:src/arbol_backend/metadata.py#Attention
arbol:src/arbol_backend/views.py#View.snapshot
-->

```ts
interface Accepted { accepted: true; duplicate: boolean; exchange: string; chat: string; number: number }

interface ChatSummary {
  chat: string;
  title: string | null;                 // NULL until the Leather Bag gives one; the Trivial Trunk makes none (TRV-0)
  firstMessage: string;                 // the first 200 characters of the message at position 0 of the lowest-numbered Exchange that was not replaced
  activityAt: string;                   // the latest of the last Exchange's accepted_at and ended_at
  last?: { exchange: string; number: number; state: ExchangeState; error?: BridgeError; waitingFor?: string };
  hasDraft: boolean;
  workingFolder?: string;               // of the last Exchange
  route?: object;                       // of the last Exchange, for the row of the latest chats
  ongoing: boolean;
  migration?: { fromRoot: string; fromChat: string; stale: boolean }; // only when this Root has provenance
  archived?: true;                      // only in a changed event, when the chat was archived
}

interface ChatSettings { route?: object; workingFolder?: string }   // picked for the next message; absent: the last Exchange's (BKD-0)
interface ChatMarks { ongoing: boolean; archivedAt?: string }

interface ChatInfo {
  chat: string;
  title: string | null;
  createdAt?: string;
  firstMessage?: string;                // first200 characters of the first unreplaced prompt; additive BKD-D36
  migration?: { fromRoot: string; fromChat: string; stale: boolean }; // the same own-Root provenance as ChatSummary
  exchangeCount: number;                // every Exchange of the chat that was not replaced, for "Turn n of N"
  usage: { inputTokens: number; outputTokens: number };   // the sum over the chat's runs, for the cockpit
}

interface SavedExchange {               // an Exchange as the chat tables hold it (RCT-3), never a replaced one
  exchange: string;
  number: number;
  state: "open" | "completed" | "failed" | "cancelled" | "interrupted";
  error?: BridgeError;                  // the cause of a failed Exchange, whole (RCT-2)
  route: object;                        // as it was handed
  workingFolder: string;
  acceptedAt: string;
  endedAt?: string;
  items: Array<                         // the message and, once it has ended, the answer, in the order of their positions
    | { position: number; kind: "message"; role: "user" | "assistant"; text: string }
    | { position: number; kind: "tool"; name: string; input: unknown; ok: boolean; result?: unknown;
        error?: string; truncated: boolean; interrupted: boolean; ask?: unknown; answer?: unknown; cut?: boolean }>;
  runs: Array<{ kind: "agent" | "small"; outcome: string; usage: object; started?: object }>;   // started names the Subscription and the model that ran
  note?: ExchangeNote;
}

type ExchangeState = "accepting" | "running" | "stopping" | "ending" | "unsaved" | "gone"
                   | "completed" | "failed" | "cancelled" | "interrupted";
// gone: the listing's interrupted, a process gone without an end and not yet settled (BKD-0).
// A window treats an Exchange as ended only once it has its saved event, or a snapshot that holds it ended.

interface ExchangeStatus {
  exchange: string;
  state: ExchangeState;
  waitingFor?: string;                  // with running: "answer", "tool", "driver", "small-call", "database" (RCT-1)
  since?: string;
  end?: { state: string; at: string; error?: BridgeError };   // from the record, before the database has it
}

// a batch of lines of events.jsonl, unchanged (RCT-1)
interface LinesEvent { kind: "lines"; exchange: string; lines: Array<object | { n: number; tooLarge: true; bytes: number }> }

interface Draft {                      // chat: the Draft of a reply; folder: the Draft of a new chat
  chat?: string; folder?: string; text: string; revision: number; updatedAt: string;
  sentAs?: string;                      // the Exchange it is being sent as
  sentRequest?: { chat: string; route: object; workingFolder: string };   // what it was sent with, for sending it again
}

interface ExchangeNote { exchange: string; kind: "ended_stuck"; at: string }

interface AttentionItem {
  id: string;                           // stable while the item is open, such as "database_unreachable"
  kind: string;                         // "database_unreachable" | "space_low" | "layout_incomplete", and later more
  severity: "warning" | "urgent";
  message: string;                      // plain words, with the cause
  since: string;
}

interface Discovery {                   // BKD-0, "Discovery across Roots"
  roots: Array<{
    root: RootInfo;
    exchanges?: Array<object>;          // the ListedExchange entries of RTM-0, unchanged
    error?: BridgeError;                // what failed for this Root alone
  }>;
}
```

The app channel, which the Swift App answers itself (SYL-192):

```ts
// window.webkit.messageHandlers.arbolApp.postMessage(text); replies come through window.arbolApp.receive(text)
type AppRequest =
  | { type: "call"; id: string; method: "app.pickFolder"; params: { start?: string } }
  | { type: "call"; id: string; method: "app.openLink"; params: { url: string } }
  | { type: "call"; id: string; method: "app.takeOpen"; params: {} };
type AppMessage = { type: "open" };     // from the Swift App: a request to open a chat waits
```

## Known problems in version 1

Not to be reproduced.

- **Errors in several shapes.** A call's error came back as a plain string, and a stream's in three shapes; the window logged only one of them, so an error frame could end a stream without anyone noticing.
- **Delivery taken for an acknowledgement.** A message handed to the web page was taken as received, so the window re-read the whole chat every 750 milliseconds while it ran, and every 2 seconds otherwise.
- **Background windows that missed updates.** macOS held hidden windows back without a disconnect, and they kept showing an old state.
- **One handler for every reconnect.** The reconnect notice was kept under one fixed subscription, so the last window part that registered took it from all the others.
- **No time limit on a call.** A call waited for ever, and a connection stuck while connecting held up every later call.
- **A final "running" that stayed.** The end of a turn came in one message and its new state in a later read, which could be lost.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:renderer/packages/design-system/src/bridge/arbol.ts#__arbolEvent`
- `arbol_deprecated_v1:renderer/packages/events/src/useProjection.ts#RUNNING_PROJECTION_REVALIDATE_MS`
- `arbol_deprecated_v1:app/Arbol/CoreClient.swift#startConnection`
- `arbol_deprecated_v1:daemons/core/arbol_core/server.py#stream`
- `arbol_deprecated_v1:product-spec/09-willo-and-attention.md#Staying live — and never showing a stale "running"`

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| BKD-D13 | In what form do messages cross the Bridge? | One JSON object for each message, of eight kinds, with the id of a call or a subscription chosen by the window; to and from the web page as a JSON string, and on the socket as one line ending with a newline, at most 16 MiB, on one connection for each window. A line is easy to read in a log and to relay, and the JSON of a line holds no newline. The alternative: a frame with its length in front, as version 1 had, which needs no limit but no person can read | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D14 | How does a window know it shows the truth? | Every subscription is registered before its snapshot is read, starts with the snapshot, and numbers its events without gaps. A window that finds a gap, that finds itself behind when it is shown again, or that gets a new `hello` starts its subscriptions again; the backend sends a new snapshot when the database returns. Nothing is read on a timer. The alternative: reading again every few seconds, as version 1 did, which costs work all the time and still shows an old state between two reads | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D15 | How does a window ask for the Mac's folder dialog and a link, which only the Swift App can open, and learn of a request to open a chat? | On a channel of their own, `arbolApp`, which the Swift App answers itself and which never reaches the backend, so the Bridge stays a channel the Swift App does not read; the web view never leaves its page, and only the page's main frame reaches the Bridge. The exact form is SYL-192's. The alternative: the Swift App reads the Bridge and answers some methods itself, against ARC-0 | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D16 | How is the window built and checked before the Swift App exists? | Through a development relay in the `arbol` repository that serves the renderer bundle on the loopback address and relays a WebSocket to `backend.sock`, unchanged, letting in only the browser that got its token. It is for development and checks only, never for daily use. The alternative: wait for the Swift App (SYL-192), which is blocked by this specification, before the first window can be seen | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D23 | How large may a chat's snapshot be? | The last 12 Exchanges, as version 1 opened a chat, with the input and the result of each tool call cut to 8 KiB, and the rest on request (`chat.exchanges`, `toolCall.get`). A Driver may return up to 200 KiB for one tool call (DRV-2), so a whole chat can pass the 16 MiB of a message, and a closed tool call shows one line. The alternative: the whole chat at once, which fails for a long chat | Decided 18 October 2026, a technical choice; 12 Exchanges, as version 1 had them, on 19 October 2026 following BKD-D22 |
| BKD-D29 | How are the protocol boundaries, snapshot races and Root observations made precise for implementation? | The Backend protocol details above: complete-line byte limits, correlated validation, versioned snapshots, bounded per-window queues, receipts on transport handoff, explicit root.get wrapper and fresh bounded catalogue observation | Decided 27 October 2026, a technical choice in SYL-248; the stated details |
| BKD-D36 | How does the page obtain readonly repository slots/defaults and an untitled chat first prompt outside its newest12? | The Window bootstrap additions above: read-only workspace.get and additive ChatInfo.firstMessage in the same snapshot | Decided27 October2026, technical choice in SYL-254, closing a previously missing renderer input without giving the page filesystem access |
