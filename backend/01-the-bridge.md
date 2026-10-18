---
role: authored
spec: BKD-1
status: review
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

### Calls

A call gets exactly one reply. The window gives every call a time limit of its own, as the table of methods says ([Interface](#interface)), after which it treats the call as failed with `no_answer`; the backend's reply, when it still comes, is then ignored.

An error has the form `{"code", "message"}`, and for an error that the backend passes on from another program, `source` names that program: `trunk`, `root-manager`, `roots` or `driver`. The message is in plain words and names what it concerns. For example, a message sent to a chat whose answer is still running:

```json
{"type":"reply","id":"c21","error":{"code":"chat_busy","source":"trunk","message":"The chat has an Exchange in progress: 6e2f1a0b-3c4d-4e5f-8a6b-7c8d9e0f1a2b"}}
```

The backend's own codes are in the [Interface](#interface). A code passed on is the code of the program it came from (RCT-2, RTM-0, DRV-4). A window shows a code it does not know with its message.

The backend checks every identifier a call names before it touches a file or starts a program: a chat or an Exchange is a UUID written in lower case with hyphens (RCT-0), a Driver is one whose launcher is in the folder of the launchers, and a Subscription or an attempt is one the Driver or the backend gave. Anything else is refused with `invalid_input`. For example, `"exchange":"../../x"` reaches no file.

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

The topics are in the [Interface](#interface). For a chat, the snapshot holds the last 20 Exchanges as the chat tables have them, with `more` true when there are older ones, which `chat.exchanges` gives; a tool call's input and result in it are cut to 8 KiB, marked `cut`, and `toolCall.get` gives them whole when the call is opened. A chat that does not exist yet has an empty snapshot, with its Draft when it has one, never `not_found`. For an Exchange that is still open, the snapshot holds only the Leather Bag's message, and the answer comes only as lines: the backend sends every line of its `events.jsonl` from the first one on, whole and unchanged, in order, leaving out when it catches up only the pieces of a block that is whole in the file (BKD-0). So a window opened late, opened again or opened twice shows the whole answer so far (ARC-2). The window ignores a line whose `n` it already has. When the Exchange is saved, an event `saved` brings its rows as the chat tables have them. The backend also sends an event `exchange` for every Exchange of the chat whose folder appears, whoever started it.

One message stays within 16 MiB: the backend splits a batch of lines into several events where needed. A single line of `events.jsonl` larger than that is sent as `{"n", "tooLarge": true, "bytes"}`, and the window says that this part is too large to show here.

### Sending and repeating

The window chooses the identifier of a new Exchange, a UUID, before it calls `chat.send` or `exchange.sendAgain` ([BKD-D7](00-the-arbol-backend.md#decisions)). When the call fails with `disconnected`, or with `no_answer`, the window sends the same call again, with the same identifier, once the backend is back. The Trunk replies with the Exchange it accepted, marked as a repeat, or accepts it then; the message never runs twice (RCT-2). The window's time limit for these two calls, 150 seconds, is longer than the backend's longest attempt (BKD-0).

```json
{"type":"call","id":"c30","method":"chat.send","params":{"chat":"c3d4e5f6-…","exchange":"9b3a2c1e-5c6d-4f70-9a1b-2c3d4e5f6a7b","message":"Add a --clean option to it.","route":{"driver":"claude","subscription":"anthropic","model":"sonnet","effort":"high"},"workingFolder":"/Users/sam/repos/shop","draftRevision":41}}
{"type":"reply","id":"c30","result":{"accepted":true,"duplicate":false,"exchange":"9b3a2c1e-…","chat":"c3d4e5f6-…","number":3}}
```

| Calls | Sent again after `disconnected` or `no_answer` |
|---|---|
| `chat.send`, `exchange.sendAgain` | Yes, with the same Exchange identifier |
| `root.get`, `roots.list`, `chats.page`, `chat.exchanges`, `toolCall.get`, `subscriptions.check`, `chat.rename`, `exchange.stop`, `accounts.*`, `health.measure`, `signIn.start`, `signIn.cancel` | Yes: they have the same effect when sent twice |
| `draft.save` | Yes, over the same revision, so that a save that was made already is refused with `draft_conflict` and brings the Draft as it is |
| `exchange.answer` | Only when the lines of the Exchange hold no `answer` line for that `askId`; otherwise the answer arrived |
| `signIn.enterCode` | Never: the window says that the connection was lost, and the Leather Bag signs in again when the code was not taken |

### Attention

An *attention item* is something that is not a normal state and that every window of the Root shows for as long as it lasts ([ARC-D53](../architecture/02-chat-exchange-across-components.md#decisions)). The topic `attention` gives them: a snapshot of every item open now, and then each item as it opens and as it closes.

| `kind` | When | Example of its message |
|---|---|---|
| `database_unreachable` | The database cannot be reached (BKD-0) | "The database server does not answer at 127.0.0.1:5433. New messages cannot be sent; answers in progress go on." |
| `space_low` | Less than 10 GiB is free on the disk of the database; `severity` `urgent` below 2 GiB (BKD-0) | "8.6 GiB left on the disk of the database. First Sapling's chats take 3.2 GiB." |
| `layout_incomplete` | The Root's database lacks the backend's own tables (BKD-0) | "First Sapling's database lacks the table drafts: Drafts are not kept. Run arbol-roots layout sapling." |

A window shows an item of a kind it does not know with its message.

### When the backend goes away

When the connection to the backend ends, because the backend ended or was restarted, the Swift App tells the window with `{"type":"lost"}`, connects again as soon as the backend listens, and the backend's `hello` on the new connection says that it is back (SYL-192).

| | The window |
|---|---|
| While it is lost | Keeps showing what it shows, says that it is reconnecting, and keeps every Draft typed meanwhile to save it later |
| Calls under way | Fail with `disconnected`, and are sent again after the next `hello` as [above](#sending-and-repeating) says |
| After the next `hello` | Starts every subscription again, so each begins with a new snapshot, and saves the Drafts it kept |

So a missed update never leaves a window stale: the window reads the truth again ([ARC-2](../architecture/02-chat-exchange-across-components.md#when-arbol-quits)). No Exchange stops because the backend went away (BKD-0).

### Compatibility within a Root

The renderer bundles and the backend of a Root come from that Root's `arbol` Builds, and a window and its backend may come from different Builds of the same Root, for example after a new Build while a window stayed open. Within a Root the Bridge therefore changes only by additions that older Builds can ignore: a new method, topic, event kind, field or error code. Nothing is removed, and nothing changes its meaning (ARC-1). Both sides ignore a field, an event kind and an attention kind they do not know; the backend replies to a method or a topic it does not know with `unknown_method`, and the window says that this needs a newer Build.

### Secrets

No secret crosses the Bridge, in either direction: no key of a Subscription, no Jev key and no database password. A sign-in step that asks for a key names the Keychain item it goes into, and the Leather Bag stores it on the Secrets page of Seqoya Lab, or by hand until that page exists (BKD-0, [ARC-D62](../architecture/00-components-and-boundaries.md#decisions)).

### What the Swift App answers itself

A web page cannot open the Mac's folder dialog, cannot open a window that refuses every host but a few, and should not leave its own page to follow a link. The window asks the Swift App for these on a channel of its own, the *app channel*, which is not the Bridge and never reaches the backend: `window.webkit.messageHandlers.arbolApp.postMessage(text)`, answered with `window.arbolApp.receive(text)`, in the form of a call and its reply. The first window needs three requests; their exact form is the Swift App's specification (SYL-192), and the proposal is:

| Request | Params | Result |
|---|---|---|
| `app.pickFolder` | `start`: the folder the dialog opens in | `{"folder": "/Users/sam/repos/shop"}`, or `{"folder": null}` when the Leather Bag cancelled |
| `app.openSignIn` | `url`, `allowedHosts` of an `open_url` step (DRV-1) | `{}` once the window is open. The window refuses to load any host not in the list, also after the first address |
| `app.openLink` | `url`, an `http` or `https` address | `{}` once the Mac's default browser has it. Any other scheme is refused |

The web view of a window never leaves its page: the Swift App refuses every navigation away from the renderer bundle, so a link in an answer that the agent wrote, such as one a file it read put there, cannot take the window to a page that would then reach the Bridge.

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

When `window.webkit` is missing, the page uses that WebSocket instead. The relay answers the app channel itself: `app.pickFolder` with a field in which a folder is typed, `app.openSignIn` and `app.openLink` by opening the address in a new tab of the browser, which refuses no host. It is for development and checks only, never for daily use. A check that needs the Swift App itself, such as the host limit of a sign-in window, waits for SYL-192.

## Requirements

| ID | The Bridge must… | Origin | Verified by |
|---|---|---|---|
| BKD-1.1 | carry only the messages `hello`, `call`, `reply`, `subscribe`, `event`, `unsubscribe`, `ended` and `lost`, each one JSON object, with the `id` of a call or a subscription chosen by the window and unique within its connection | Changed | unit |
| BKD-1.2 | travel from the page as a JSON string through `window.webkit.messageHandlers.arbol`, to the page through `window.arbolBridge.receive`, and between the Swift App and the backend as one line of UTF-8 JSON of at most 16 MiB on one connection to the Root's `backend.sock` for each window, a longer line closing the connection; and reach the backend only from the main frame of the page loaded from the renderer bundle | Changed | unit; the Swift App's part with SYL-192 |
| BKD-1.3 | begin every connection with `hello`, giving the Bridge's version, the Root and the backend's Build; have a window refuse another version of the Bridge, and, when its page came from another Build, save its Drafts, wait for its sends and reload once for that Build | New | unit |
| BKD-1.4 | answer every call exactly once, with `result` or with `error` of the form `{code, message}` and, for an error passed on, `source`; refuse with `invalid_input` an identifier that is not of its kind before a file is touched or a program started; have the window give each call a time limit and show a code it does not know with its message | Changed | unit |
| BKD-1.5 | register a subscription before reading its snapshot, begin it with the snapshot, number its events with `seq` from 1 without gaps, keep one subscription for each topic and params on a connection, end a connection's subscriptions with `slow_reader` above 64 MiB waiting; have the window start a subscription again when it finds a gap, when `subscriptions.check` shows it behind after being hidden, and when the database returns | Changed | unit, journey |
| BKD-1.6 | give in a chat's snapshot the last 20 Exchanges, tool inputs and results cut to 8 KiB, and for an open Exchange only its message; send every line of `events.jsonl` of each Exchange in progress from the first one on, whole, unchanged and in order, a line larger than 16 MiB as `{n, tooLarge, bytes}`, then its saved rows once it is saved; and announce every Exchange of the chat whose folder appears | Changed | unit, journey |
| BKD-1.7 | when the connection ends, have the window, told by `lost`, keep showing what it shows and the Drafts typed meanwhile, fail its calls under way with `disconnected`, and after the next `hello` start every subscription again and send its calls again as the table of repeating says, `chat.send` and `exchange.sendAgain` with the same Exchange identifier and never `signIn.enterCode` | Changed | drill |
| BKD-1.8 | give every attention item open in the Root to every window that subscribes to `attention`, from its opening to its closing, and have a window show a kind it does not know with its message | New | unit, drill |
| BKD-1.9 | change within a Root only by additions that older Builds can ignore, have the backend and the window ignore every field, event kind and attention kind they do not know, and have the backend reply to a method or topic it does not know with `unknown_method` | New | unit |
| BKD-1.10 | carry no secret in either direction | Changed | unit |
| BKD-1.11 | keep the requests the Swift App answers itself, `app.pickFolder`, `app.openSignIn` and `app.openLink`, on a channel of their own, `arbolApp`, which never reaches the backend, and keep the web view of a window on its own page | New | unit; the Swift App's part with SYL-192 |
| BKD-1.12 | before the Swift App exists, be relayed by the development relay of the `arbol` repository on the loopback address only, letting in only requests with its cookie, its `Host` and, for the WebSocket, its `Origin`, and logging no message | New | unit |

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
  draft?: Draft;                        // with draft_conflict: the Draft as it is
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
| `not_found` | An Exchange, a tool call, a Subscription or a sign-in attempt that does not exist |
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
| `root.get` | — | `RootInfo` and `layoutComplete: boolean` | 30 s |
| `roots.list` | — | `Discovery` | 30 s |
| `chats.page` | `before?`: `{ activityAt, chat }` of the oldest chat shown; `limit?`, at most 200, 100 by default | `{ chats: ChatSummary[] }`, older than `before`, by `activityAt` and then `chat`, both newest first | 30 s |
| `chat.exchanges` | `chat`, `beforeNumber`, `limit?`, at most 50, 20 by default | `{ exchanges: SavedExchange[]; more: boolean }` | 30 s |
| `toolCall.get` | `exchange`, `position` | the tool call whole: `{ input, result?, error? }` | 30 s |
| `subscriptions.check` | — | `{ subscriptions: Array<{ id: string; seq: number }> }`: the last `seq` sent on each | 30 s |
| `chat.send` | `chat`, `exchange`, `message`, `route`, `workingFolder`, `draftRevision?` | `Accepted` | 150 s |
| `exchange.sendAgain` | `exchange` (the one replaced), `newExchange`, `route` | `Accepted` | 150 s |
| `exchange.stop` | `exchange` | `{ ended: "completed" \| "failed" \| "cancelled" \| "interrupted" \| "saved" \| "none" }`, as `arbol-root stop` printed it (RTM-0) | 120 s |
| `exchange.answer` | `exchange`, `askId`, `answer` (DRV-3 `Answer`) | `{}` once the line is in `control` | 30 s |
| `chat.rename` | `chat`, `title`: a string, or `null` to take the title away | `{ title: string \| null }` | 30 s |
| `draft.save` | `chat`, `text`, `workingFolder?`, `route?`, `baseRevision`: the revision it was made over, `null` for a chat without a Draft | `{ revision: number }` | 30 s |
| `accounts.list` | — | `{ drivers: Array<{ driver: string; subscriptions?: Subscription[]; error?: BridgeError }> }` (DRV-1 `Subscription`) | 30 s |
| `accounts.check`, `accounts.usage`, `accounts.models`, `accounts.signOut` | `driver`, `subscription` | DRV-1's `Subscription`, `UsageReport`, `ModelCatalog`, `Subscription` | 30 s |
| `signIn.start` | `driver`, `subscription` | `{ attempt: string }`: a new attempt, or the one that runs for that Subscription | 30 s |
| `signIn.enterCode` | `attempt`, `code` | `{}` | 30 s |
| `signIn.cancel` | `attempt` | `{}` | 30 s |
| `health.measure` | — | `Measurement` (BKD-0) | 30 s |

The topics:

| Topic | Params | Snapshot | Events after it |
|---|---|---|---|
| `chats` | — | `{ kind: "snapshot", chats: ChatSummary[] }`: the 100 chats with the newest activity, and every new chat that has a Draft | `{ kind: "changed", chats: ChatSummary[] }`: each chat whose summary changed, within a second of the change (BKD-0) |
| `chat` | `chat` | `{ kind: "snapshot", chat: ChatInfo, exchanges: SavedExchange[], more: boolean, draft: Draft \| null }` | `exchange` (`ExchangeStatus`), `lines` (`LinesEvent`), `saved` (`SavedExchange`), `draft` (`Draft \| null`, null once the Draft is removed), `title`, `note` (`ExchangeNote`) |
| `attention` | — | `{ kind: "snapshot", items: AttentionItem[] }` | `{ kind: "opened", item }`, `{ kind: "closed", id }` |
| `signIn` | `attempt` | `{ kind: "step", step: SignIn \| null }`: the last step so far | `{ kind: "step", step: SignIn }` (DRV-1); it ends after `done` or `failed`. Ending the subscription changes nothing; `signIn.cancel` cancels |

```ts
interface Accepted { accepted: true; duplicate: boolean; exchange: string; chat: string; number: number }

interface ChatSummary {
  chat: string;
  title: string | null;                 // NULL until the Leather Bag gives one; the Trivial Trunk makes none (TRV-0)
  firstMessage: string;                 // the first 200 characters of the message at position 0 of the lowest-numbered Exchange that was not replaced; "" for a new chat
  activityAt: string;                   // the latest of the last Exchange's accepted_at and ended_at, or the Draft's updated_at for a new chat
  last?: { exchange: string; number: number; state: ExchangeState; error?: BridgeError; waitingFor?: string };
  hasDraft: boolean;
  workingFolder?: string;               // of the last Exchange
}

interface ChatInfo { chat: string; title: string | null; createdAt?: string }

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

interface Draft { chat: string; text: string; workingFolder?: string; route?: object; revision: number; sentAs?: string; updatedAt: string }

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
  | { type: "call"; id: string; method: "app.openSignIn"; params: { url: string; allowedHosts: string[] } }
  | { type: "call"; id: string; method: "app.openLink"; params: { url: string } };
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
| BKD-D15 | How does a window ask for the Mac's folder dialog, a sign-in window and a link, which only the Swift App can open? | On a channel of their own, `arbolApp`, which the Swift App answers itself and which never reaches the backend, so the Bridge stays a channel the Swift App does not read; the web view never leaves its page, and only the page's main frame reaches the Bridge. The exact form is SYL-192's. The alternative: the Swift App reads the Bridge and answers some methods itself, against ARC-0 | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D16 | How is the window built and checked before the Swift App exists? | Through a development relay in the `arbol` repository that serves the renderer bundle on the loopback address and relays a WebSocket to `backend.sock`, unchanged, letting in only the browser that got its token. It is never for daily use, because its sign-in tab cannot be limited to the vendor's hosts. The alternative: wait for the Swift App (SYL-192), which is blocked by this specification, before the first window can be seen | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D23 | How large may a chat's snapshot be? | The last 20 Exchanges, with the input and the result of each tool call cut to 8 KiB, and the rest on request (`chat.exchanges`, `toolCall.get`). A Driver may return up to 200 KiB for one tool call (DRV-2), so a whole chat can pass the 16 MiB of a message; 20 Exchanges fill several screens, and a closed tool call shows one line. The alternative: the whole chat at once, which fails for a long chat | Decided 18 October 2026, a technical choice: the proposed default, the values to start with |
