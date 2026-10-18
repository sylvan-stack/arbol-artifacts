---
role: authored
spec: BKD-1
status: draft
---
# Arbol backend · 01 The Bridge

The *[Bridge](../GLOSSARY.md#bridge)* is how a window of an Arbol [UI](../GLOSSARY.md#ui) talks to the backend of its Root. The window's renderer, a web page in a web view of the Arbol Swift App, sends *calls*, such as "send this message", and *subscriptions*, such as "tell me everything that happens in this chat"; the backend answers each call once and sends the events of each subscription until it is ended. The Swift App carries every message unchanged between the web view and the backend's socket. For example, a window that opens the chat "What build.sh does" subscribes with `{"type":"subscribe","id":"s2","topic":"chat","params":{"chat":"c3d4e5f6-…"}}` and receives first the whole chat as it is saved, then the lines of the answer still arriving, one batch at a time. This specification states the messages and their form, how they travel, calls and their errors, subscriptions and how a window keeps the truth, the attention items, what happens when the backend goes away, the few requests the Swift App answers itself, and how the window runs before the Swift App exists. It matters because in version 1 errors came back in three different shapes, a delivered update was not an acknowledged one, background windows missed updates without noticing, and every fix for a stale window added another way of reconciling.

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
| `reply` | The backend | The one answer to a call: its `result`, or its `error` |
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
renderer (web page)  ──postMessage(text)──▶  Arbol Swift App  ──one line──▶  backend.sock  ──▶  Arbol backend
renderer             ◀──receive(text)─────  Arbol Swift App  ◀──one line──  backend.sock  ◀──  Arbol backend
```

| Leg | Form |
|---|---|
| Renderer to Swift App | `window.webkit.messageHandlers.arbol.postMessage(text)`, where `text` is the message as a JSON string. A string, not an object, so that nothing of the page's own objects is lost on the way |
| Swift App to renderer | The Swift App calls `window.arbolBridge.receive(text)` with the message as it came |
| Swift App to backend and back | One connection to the Root's `backend.sock` for each window. Each message is one line of UTF-8 JSON ending with a newline, at most 16 MiB |

The Swift App passes every message on unchanged, in the order it came, and reads none of them; it adds only `lost` ([below](#when-the-backend-goes-away)). A window belongs to one Root, and its connection goes to that Root's backend only. The connection itself says which window a message comes from, so when a window closes, its connection closes, and the backend ends its subscriptions and cancels its sign-in.

### Hello

```json
{"type":"hello","bridge":1,"root":{"root":"sapling","name":"First Sapling","status":"working","current":true},"build":"6"}
```

| Field | What the window does with it |
|---|---|
| `bridge` | The version of the Bridge, 1. A window that speaks another version shows that it cannot work with this backend, and sends nothing |
| `root` | The Root's identifier, display name, state and whether it is current, for the header ([BKD-2](02-elma-chat.md#the-window)) |
| `build` | The backend's Build. A window whose renderer bundle came from another Build of `arbol` reloads its page once, so that the Swift App loads the bundle of the Build that runs (SYL-192); when it still differs, the window goes on, because within a Root a later Build only adds ([below](#compatibility-within-a-root)) |

Only a new Root raises the version of the Bridge: a change that older Builds cannot ignore makes a new Root (ARC-1).

### Calls

A call gets exactly one reply. The window gives every call a time limit of its own, 30 seconds unless the table of methods says otherwise ([Interface](#interface)), after which it treats the call as failed with `no_answer`; the backend's reply, when it still comes, is then ignored.

An error has the form `{"code", "message"}`, and for an error that the backend passes on from another program, `source` names that program: `trunk`, `root-manager`, `roots` or `driver`. The message is in plain words and names what it concerns. For example, a message sent to a chat whose answer is still running:

```json
{"type":"reply","id":"c21","error":{"code":"chat_busy","source":"trunk","message":"The chat has an Exchange in progress: 6e2f1a0b-3c4d-4e5f-8a6b-7c8d9e0f1a2b"}}
```

The backend's own codes are in the [Interface](#interface). A code passed on is the code of the program it came from (RCT-2, RTM-0, DRV-4). A window shows a code it does not know with its message.

### Subscriptions

A subscription starts with one event that holds the whole present state of its topic, the *snapshot*, and goes on with the changes. Every event of a subscription carries `seq`, which counts from 1 without gaps:

```json
{"type":"subscribe","id":"s2","topic":"chat","params":{"chat":"c3d4e5f6-0718-4293-a4b5-c6d7e8f90a1b"}}
{"type":"event","id":"s2","seq":1,"event":{"kind":"snapshot","chat":{…},"exchanges":[…],"draft":{…}}}
{"type":"event","id":"s2","seq":2,"event":{"kind":"exchange","exchange":{"exchange":"9b3a2c1e-…","state":"running","waitingFor":"driver","since":"2026-10-18T09:30:01.204Z"}}}
{"type":"event","id":"s2","seq":3,"event":{"kind":"lines","exchange":"9b3a2c1e-…","lines":[{"n":1,"event":{…"type":"started"…}},{"n":2,"event":{…"type":"text_delta","text":"Let me "}}]}}
```

The window keeps the truth this way:

| Rule | Detail |
|---|---|
| A snapshot replaces | The window shows what the snapshot says and forgets what it showed before for that topic |
| A gap re-reads | A window that finds a `seq` missing ends the subscription and starts it again, which brings a new snapshot. A message handed to a web page is not acknowledged, so a lost one is noticed only this way |
| Coming back into view re-reads | A window that was hidden or minimised, and is shown again, starts its subscriptions again, because macOS may hold a hidden page back without anyone noticing |
| No polling | Apart from these, the window reads nothing again on a timer |

The topics are in the [Interface](#interface). For a chat, the snapshot holds the saved Exchanges as the chat tables have them, and for each Exchange still in progress the backend then sends every line of its `events.jsonl` from the first one on, whole and unchanged, in batches of the lines it has read, at most every 50 milliseconds (BKD-0). So a window opened late, opened again or opened twice shows the whole answer so far (ARC-2). When the Exchange is saved, an event `saved` brings its rows as the chat tables have them.

One message stays within 16 MiB: the backend splits a batch of lines into several events where needed. A single line of `events.jsonl` larger than that is sent as `{"n", "tooLarge": true, "bytes"}`, and the window says that this part is too large to show here.

### Sending and repeating

The window chooses the identifier of a new Exchange, a UUID, before it calls `chat.send` or `exchange.sendAgain` ([BKD-D7](00-the-arbol-backend.md#decisions)). When the connection ends before the reply came, the window sends the same call again, with the same identifier, once the backend is back. The Trunk answers with the Exchange it accepted, marked as a repeat, or accepts it then; the message never runs twice (RCT-2).

```json
{"type":"call","id":"c30","method":"chat.send","params":{"chat":"c3d4e5f6-…","exchange":"9b3a2c1e-5c6d-4f70-9a1b-2c3d4e5f6a7b","message":"Add a --clean option to it.","route":{"driver":"claude","subscription":"anthropic","model":"sonnet","effort":"high"},"workingFolder":"/Users/sam/repos/shop","draftRevision":7}}
{"type":"reply","id":"c30","result":{"accepted":true,"duplicate":false,"exchange":"9b3a2c1e-…","chat":"c3d4e5f6-…","number":3}}
```

Every other call either changes nothing, such as `root.get`, or can be sent again with the same effect, such as `chat.rename`, `draft.save` and `exchange.stop`, so the window repeats it the same way.

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
| While it is lost | Keeps showing what it shows, says that it is reconnecting, and keeps every Draft typed meanwhile to send it later |
| Calls under way | Fail with `disconnected`. `chat.send` and `exchange.sendAgain` are sent again after the next `hello`, with the same Exchange identifier ([above](#sending-and-repeating)) |
| After the next `hello` | Starts every subscription again, so each begins with a new snapshot, and sends the Drafts it kept |

So a missed update never leaves a window stale: the window reads the truth again ([ARC-2](../architecture/02-chat-exchange-across-components.md#when-arbol-quits)). No Exchange stops because the backend went away (BKD-0).

### Compatibility within a Root

The renderer bundles and the backend of a Root come from that Root's `arbol` Builds, and a window and its backend may come from different Builds of the same Root, for example after a new Build while a window stayed open. Within a Root the Bridge therefore changes only by additions that older Builds can ignore: a new method, topic, event kind, field or error code. Nothing is removed, and nothing changes its meaning (ARC-1). Both sides ignore a field, an event kind and an attention kind they do not know; a backend answers a method or a topic it does not know with `unknown_method`, and the window says that this needs a newer Build.

### Secrets

A secret travels only from the window to the backend, once, in the call `signIn.storeSecret`, and the backend writes it to the Keychain item that the sign-in step names (BKD-0). No message from the backend to a window ever holds a secret, a key or the database password, and neither the backend nor the Swift App writes one to a log (ARC-0, "Secrets").

### What the Swift App answers itself

A web page cannot open the Mac's folder dialog, and cannot open a window that refuses every host but a few. The window asks the Swift App for these on a channel of its own, the *app channel*, which is not the Bridge and never reaches the backend: `window.webkit.messageHandlers.arbolApp.postMessage(text)`, answered with `window.arbolApp.receive(text)`, in the form of a call and its reply. The first window needs two requests; their exact form is the Swift App's specification (SYL-192), and the proposal is:

| Request | Params | Result |
|---|---|---|
| `app.pickFolder` | `start`: the folder the dialog opens in | `{"folder": "/Users/sam/repos/shop"}`, or `{"folder": null}` when the Leather Bag cancelled |
| `app.openSignIn` | `url`, `allowedHosts` of an `open_url` step (DRV-1) | `{}` once the window is open. The window refuses to load any host not in the list |

### Before the Swift App exists

Until the Arbol Swift App exists (SYL-192), the window runs in a browser on this Mac, through a small *development relay* in the `arbol` repository, so that the window can be built and its journeys checked:

```sh
python scripts/bridge_relay.py --root sapling
# http://127.0.0.1:53114/?token=4f0c…   open this address in a browser
```

The relay serves the renderer bundle of the Root's newest working `arbol` Build over HTTP on the loopback address only, and relays each message of a WebSocket at `/bridge` as one line to `backend.sock` and back, unchanged. It refuses every request that does not carry the token it printed, because every program of the Mac can reach the loopback address. When `window.webkit` is missing, the renderer uses that WebSocket instead. The relay answers the app channel itself: `app.pickFolder` with a field in which a folder is typed, and `app.openSignIn` by opening the address in a new tab of the browser, which refuses no host; it is for development and checks only, never for daily use.

## Requirements

| ID | The Bridge must… | Origin | Verified by |
|---|---|---|---|
| BKD-1.1 | carry only the messages `hello`, `call`, `reply`, `subscribe`, `event`, `unsubscribe`, `ended` and `lost`, each one JSON object, with the `id` of a call or a subscription chosen by the window and unique within its connection | Changed | unit |
| BKD-1.2 | travel from the renderer as a JSON string through `window.webkit.messageHandlers.arbol`, to the renderer through `window.arbolBridge.receive`, and between the Swift App and the backend as one line of UTF-8 JSON of at most 16 MiB on one connection to the Root's `backend.sock` for each window | Changed | unit |
| BKD-1.3 | begin every connection with `hello`, giving the Bridge's version, the Root and the backend's Build; have a window refuse another version of the Bridge, and reload its page once when its bundle came from another Build | New | unit |
| BKD-1.4 | answer every call exactly once, with `result` or with `error` of the form `{code, message}` and, for an error passed on, `source`; have the window give each call a time limit and show a code it does not know with its message | Changed | unit |
| BKD-1.5 | begin every subscription with a snapshot of the whole present state of its topic, number its events with `seq` from 1 without gaps, and have the window start a subscription again when it finds a gap and when it is shown again after being hidden | Changed | unit, journey |
| BKD-1.6 | send in a chat's subscription every line of `events.jsonl` of each Exchange in progress from the first one on, whole, unchanged and in order, then the Exchange's saved rows once it is saved | Changed | unit, journey |
| BKD-1.7 | when the connection ends, have the Swift App send `lost`; have the window keep showing what it shows and the Drafts typed meanwhile, fail its calls under way with `disconnected`, and after the next `hello` start every subscription again and send `chat.send` and `exchange.sendAgain` again with the same Exchange identifier | Changed | drill |
| BKD-1.8 | give every attention item open in the Root to every window that subscribes to `attention`, from its opening to its closing, and have a window show a kind it does not know with its message | New | unit, drill |
| BKD-1.9 | change within a Root only by additions that older Builds can ignore, and have the backend and the window ignore every field, event kind and attention kind they do not know and answer a method or topic they do not know with `unknown_method` | New | unit |
| BKD-1.10 | carry a secret only once, from the window to the backend, in `signIn.storeSecret`, and never from the backend to a window | New | unit |
| BKD-1.11 | keep the requests the Swift App answers itself, `app.pickFolder` and `app.openSignIn`, on a channel of their own, `arbolApp`, which never reaches the backend | New | unit |
| BKD-1.12 | before the Swift App exists, be relayed by the development relay of the `arbol` repository on the loopback address only, refusing every request without the token it printed | New | unit |

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
| `invalid_input` | A call or subscription whose params are missing or wrong, such as a route without a model or a working folder that does not exist |
| `unknown_method` | A method or topic this Build does not know |
| `not_found` | A chat, an Exchange, a Subscription or a sign-in attempt that does not exist |
| `database_unavailable` | The database cannot be reached (BKD-0) |
| `layout_incomplete` | The Root's database lacks the backend's own tables, for a call that needs them |
| `ended` | An answer to an Exchange that has ended |
| `no_answer` | A program the backend started did not answer in its time (BKD-0) |
| `disconnected` | Made by the window, never sent: the connection ended before the reply came |

The calls:

| Method | Params | Result | Time limit of the window |
|---|---|---|---|
| `root.get` | — | `RootInfo` and `layoutComplete: boolean` | 30 s |
| `roots.list` | — | `Discovery` | 30 s |
| `chats.page` | `before?`: the `activityAt` of the oldest chat shown; `limit?`, at most 200, 100 by default | `{ chats: ChatSummary[] }`, older than `before`, newest first | 30 s |
| `chat.send` | `chat`, `exchange`, `message`, `route`, `workingFolder`, `draftRevision?` | `Accepted` | 90 s |
| `exchange.sendAgain` | `exchange` (the one replaced), `newExchange`, `route` | `Accepted` | 90 s |
| `exchange.stop` | `exchange` | `{ ended: "completed" \| "failed" \| "cancelled" \| "interrupted" \| "saved" \| "none" }`, as `arbol-root stop` says (RTM-0) | 60 s |
| `exchange.answer` | `exchange`, `askId`, `answer` (DRV-3 `Answer`) | `{}` once the line is in `control` | 30 s |
| `chat.rename` | `chat`, `title`: a string, or `null` to take the title away | `{ title: string \| null }` | 30 s |
| `draft.save` | `chat`, `text`, `workingFolder?`, `route?` | `{ revision: number }` | 30 s |
| `accounts.list` | — | `{ drivers: Array<{ driver: string; subscriptions?: Subscription[]; error?: BridgeError }> }` (DRV-1 `Subscription`) | 30 s |
| `accounts.check`, `accounts.usage`, `accounts.models`, `accounts.signOut` | `driver`, `subscription` | DRV-1's `Subscription`, `UsageReport`, `ModelCatalog`, `Subscription` | 30 s |
| `signIn.enterCode` | `attempt`, `code` | `{}` | 30 s |
| `signIn.storeSecret` | `attempt`, `secret` | `{}` once the item is stored | 30 s |
| `health.measure` | — | `Measurement` (BKD-0) | 30 s |

The topics:

| Topic | Params | Snapshot | Events after it |
|---|---|---|---|
| `chats` | — | `{ kind: "snapshot", chats: ChatSummary[] }`: the 100 chats with the newest activity, and every new chat that has a Draft | `{ kind: "changed", chats: ChatSummary[] }`: each chat whose summary changed |
| `chat` | `chat` | `{ kind: "snapshot", chat: ChatInfo, exchanges: SavedExchange[], draft?: Draft }`; a chat that does not exist yet, but has a Draft, has `exchanges: []` | `exchange` (`ExchangeStatus`), `lines`, `saved` (`SavedExchange`), `draft` (`Draft`), `title`, `note` (`ExchangeNote`) |
| `attention` | — | `{ kind: "snapshot", items: AttentionItem[] }` | `{ kind: "opened", item }`, `{ kind: "closed", id }` |
| `signIn` | `driver`, `subscription` | `{ kind: "attempt", attempt: string }` | `{ kind: "step", step: SignIn }` (DRV-1); it ends after `done` or `failed`. Ending the subscription cancels the attempt |

```ts
interface Accepted { accepted: true; duplicate: boolean; exchange: string; chat: string; number: number }

interface ChatSummary {
  chat: string;
  title: string | null;                 // NULL until the Leather Bag gives one; the Trivial Trunk makes none (TRV-0)
  firstMessage: string;                 // the first 200 characters of the chat's first message, for the window's placeholder; "" for a new chat
  activityAt: string;                   // the latest of the last Exchange's accepted_at and ended_at, or the Draft's updated_at for a new chat
  last?: { exchange: string; number: number; state: ExchangeState; error?: BridgeError };
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
  items: Array<                         // the message and the answer, in the order of their positions
    | { position: number; kind: "message"; role: "user" | "assistant"; text: string }
    | { position: number; kind: "tool"; name: string; input: unknown; ok: boolean; result?: unknown;
        error?: string; truncated: boolean; interrupted: boolean; ask?: unknown; answer?: unknown }>;
  runs: Array<{ kind: "agent" | "small"; outcome: string; usage: object; started?: object }>;   // started names the Subscription and the model that ran
  note?: ExchangeNote;
}

type ExchangeState = "accepting" | "running" | "stopping" | "ending" | "unsaved" | "interrupted"
                   | "completed" | "failed" | "cancelled";

interface ExchangeStatus {
  exchange: string;
  state: ExchangeState;
  waitingFor?: string;                  // with running: "answer", "tool", "driver", "small-call", "database" (RCT-1)
  since?: string;
  end?: { state: string; at: string; error?: BridgeError };   // from the record, before the database has it
}

// a batch of lines of events.jsonl, unchanged (RCT-1)
interface LinesEvent { kind: "lines"; exchange: string; lines: Array<object | { n: number; tooLarge: true; bytes: number }> }

interface Draft { chat: string; text: string; workingFolder?: string; route?: object; revision: number; updatedAt: string }

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
// window.webkit.messageHandlers.arbolApp.postMessage(text); answers come through window.arbolApp.receive(text)
type AppRequest =
  | { type: "call"; id: string; method: "app.pickFolder"; params: { start?: string } }
  | { type: "call"; id: string; method: "app.openSignIn"; params: { url: string; allowedHosts: string[] } };
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
| BKD-D14 | How does a window know it shows the truth? | Every subscription starts with a snapshot of the whole present state, and numbers its events without gaps. A window that finds a gap, or is shown again after being hidden, or gets a new `hello`, starts its subscriptions again. Nothing is read on a timer. The alternative: reading again every few seconds, as version 1 did, which costs work all the time and still shows an old state between two reads | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D15 | How does a window ask for the Mac's folder dialog and for a sign-in window, which only the Swift App can open? | On a channel of their own, `arbolApp`, which the Swift App answers itself and which never reaches the backend, so the Bridge stays a channel the Swift App does not read. The exact form is SYL-192's. The alternative: the Swift App reads the Bridge and answers some methods itself, against ARC-0 | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D16 | How is the window built and checked before the Swift App exists? | Through a development relay in the `arbol` repository that serves the renderer bundle on the loopback address and relays a WebSocket to `backend.sock`, unchanged, refusing every request without the token it printed. The alternative: wait for the Swift App (SYL-192), which is blocked by this specification, before the first window can be seen | Decided 18 October 2026, a technical choice: the proposed default |
