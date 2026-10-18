---
role: authored
spec: BKD-2
status: draft
---
# Arbol backend · 02 Elma Chat, its first version

[Elma Chat](../GLOSSARY.md#elma-chat) is the [UI](../GLOSSARY.md#ui) in which the [Leather Bag](../GLOSSARY.md#leather-bag) talks with an agent. Its first version is one kind of window: on the left the chats of one [Root](../GLOSSARY.md#arbol-root), newest first; on the right the chat that is open, with the composer below it. Several such windows can be open at once. Each shows a *page* loaded from Elma Chat's *renderer bundle*, the files built from `ui/elma/` of the `arbol` repository into each `arbol` Build. A chat is a list of [Chat Exchanges](../GLOSSARY.md#chat-exchange), *Exchanges* for short: each is one message of the Leather Bag and the agent's answer to it. In it the Leather Bag reads a chat, sends a message, sees the answer arrive, answers a question of the agent, stops the answer, sends a message again, renames a chat, signs in to an account, and opens a chat again later. For example, the Leather Bag opens Elma Chat in First Sapling from the tray menu, picks "New chat", chooses the folder `~/repos/shop`, types "What does build.sh do?" and presses Return: the message appears at once, the answer arrives word by word, the agent's `cat build.sh` shows as one line that opens to its output, and the chat appears at the top of the list, named after its first words until it is given a title. This specification states what the window shows and does; the backend it talks to is [BKD-0](00-the-arbol-backend.md), and the messages they exchange are [BKD-1](01-the-bridge.md). It matters because in version 1 the window showed "Stopped" before anything had stopped, a cancelled answer looked completed when it was opened again, a window opened late missed the text still arriving, Drafts had several owners that overwrote each other, and a placeholder was stored as the title.

It follows the conventions of the [Driver Contract](../driver-contract/README.md#conventions) and the additions in this chapter's [README](README.md#conventions). The forms are technical choices made on 18 October 2026; the questions only the owner can settle are rows of the Decisions table with a proposed answer.

## Scope

Covered: the window, the list of chats, reading a chat, an answer as it arrives, the composer, sending and stopping, questions of the agent, a failed Exchange, sending again and renaming, accounts, attention, coming back, the renderer bundle.

Not covered: the tray menu, opening and closing windows, and the requests the Swift App answers itself (SYL-192); Brain Recipes in the route picker (SYL-191); branches, edited messages, search, tags, archiving and deleting a chat, attachments, and a message that steers a running agent, which come later (RCT-D21, ARC-D54); Willo Station and Seqoya Lab; marking a migrated chat stale (SYL-195).

## Behaviour

### The window

A window belongs to one Root, the one picked in the tray menu, and talks only to that Root's backend. Several windows of the same Root, or of different Roots, can be open at once.

```text
┌ First Sapling ─────────────────────────────────────────────────────────── [Root] ┐
│ + New chat                │ What build.sh does                             Rename │
│ ───────────────────────── │ ─────────────────────────────────────────────────────│
│ ● What build.sh does   2m │ You: What does build.sh do?                          │
│   shop                    │   ▸ shell  cat build.sh                          ✓   │
│ Add a --clean option… 1h  │ It compiles the three packages and copies them to    │
│   shop · Failed           │ dist/.                                               │
│ New chat · Draft          │ claude · anthropic · sonnet · 5.9k tokens            │
│                           │ ─────────────────────────────────────────────────────│
│                           │ [ Add a --clean option to it.                      ] │
│                           │ ~/repos/shop ▾   claude · anthropic · sonnet · high ▾ │
└───────────────────────────┴──────────────────────────────────────────────────────┘
```

| Part | What it shows |
|---|---|
| The header | The Root's display name, as every UI shows it ([ARC-1](../architecture/01-roots.md#the-tray-menu-and-arbol-roots)). A Root that is not `working` says so beside it: "preparing", or "failed" with its reason |
| The Root's panel | Opened from the header: the Root's identifier, state and Build, the size of every Root's database, the size of the data folder of the database server and the free space of its disk, whether the server answers, and the Exchanges running in other Roots, each Root by its display name ([below](#the-roots-panel)) |
| The list of chats | On the left ([below](#the-list-of-chats)) |
| The chat | On the right: its title, its Exchanges, the composer |
| Attention | A line across the top of the window for each attention item of the Root ([below](#attention)) |

The window shows what the backend says and keeps nothing of its own beyond the window's life: which chat is open, and the text typed since the last save of a Draft. It writes nothing into the page's own storage.

### The list of chats

The list holds every chat of the Root, the chat with the newest activity first: the latest time an Exchange of it was accepted or ended. It shows the first 100, and more as it is scrolled down (`chats.page`).

| A row shows | Detail |
|---|---|
| The title | The chat's title. A chat without one shows the first line of its first message, at most 80 characters, in a lighter type. That text is a placeholder for the eye only and is never stored as a title ([RCT-3](../../arbol-root/contract/03-the-chat-tables.md#the-tables)) |
| When | How long ago its activity was: "2m", "1h", "Mon", "12 Oct" |
| Its folder | The last part of the working folder of its last Exchange, such as `shop` |
| Its state | Of its last Exchange: a moving mark while it runs, "Waiting for you" while the agent waits for an answer, "Stopping", "Not yet saved", and "Failed", "Interrupted" or "Stopped" when it ended so. A completed one shows no mark |
| A Draft | "Draft" when the chat has one |

A new chat appears at the top as "New chat" with the start of its Draft, from the moment something is typed in it, until its first message is accepted or its Draft is emptied.

### Reading a chat

A chat shows its Exchanges in the order of their numbers, leaving out every Exchange a message sent again replaced (RCT-3). Each Exchange shows, in the order of their positions:

| Item | How it is shown |
|---|---|
| The Leather Bag's message | As it was sent, marked as the Leather Bag's |
| A block of the answer | Its text as Markdown: headings, lists, emphasis, links, tables and code blocks. Raw HTML in it is shown as text, never run. A link opens in the Mac's default browser through the Swift App (`app.openLink`, BKD-1), and only when it is `http` or `https`; any other link is shown as text. The window never leaves its own page |
| A tool call | One line, closed: the tool's name, a short form of its input, such as the command of `shell` or the path of `Read`, and a mark for done, failed or interrupted. Opened, it shows the input and the result whole, and says when the Driver cut the result to its limit |
| A question of the agent | The question with its options, and the answer the Leather Bag gave, or "Declined" |

Below the Exchange stand the Subscription and the model that ran, from the run's `started` event (ARC-0, RCT-3), and the tokens of its runs, such as "claude · anthropic · sonnet · 5.9k tokens". An Exchange that did not complete says how it ended:

| State | The window says |
|---|---|
| `cancelled` | "Stopped" |
| `failed` | "Failed" with its cause ([below](#a-failed-exchange)) |
| `interrupted` | "Interrupted: the agent's process ended before the answer was finished. What had arrived is kept." |
| `interrupted`, with the note `ended_stuck` | "Ended because it was stuck. What had arrived is kept." ([ARC-3](../architecture/03-stuck-trunks.md#ending-a-stuck-exchange)) |

### An answer as it arrives

While an Exchange is in progress, the window shows the lines of its `events.jsonl` as they come, from the first one on ([BKD-1](01-the-bridge.md#subscriptions)). It reads them by the Driver's events ([DRV-2](../driver-contract/02-inference.md#the-event-stream)):

| Line | The window |
|---|---|
| `text_delta`, then `text` | Writes the pieces as they come, and puts the whole block in their place when its `text` arrives, because the block is the truth |
| `thinking_delta`, `thinking` | Shows the reasoning in a closed block "Thinking", which can be opened. It is shown only while the answer arrives, because the chat tables keep none (RCT-3) |
| `tool_started`, `tool_output_delta`, `tool_finished` | Opens a line for the tool call with a moving mark, shows its last line of output as it streams, and closes it with its result |
| An event with `parentCallId` | Shows what a sub-agent does inside the tool call that started it, while it runs; the saved chat leaves it out (RCT-3) |
| `ask_opened`, `answer`, `ask_closed` | Shows the question to answer ([below](#questions-of-the-agent)), then the answer given, then closes it |
| `notice` | A short line in a lighter type, such as "The vendor moved the run to another model" |
| `usage` | The tokens so far |
| `control_refused` | "The answer was not taken: …", with the Driver's message |
| The end | The Exchange's final state, as above |

Beside the Exchange the window shows what it waits for and for how long, from its signs of life ([ARC-3](../architecture/03-stuck-trunks.md#long-waits-on-purpose)):

| `waitingFor` | Shown as |
|---|---|
| `tool` | "Running a command for 2 h 10 min", or "Running Read for 4 s" |
| `answer` | "Waiting for your answer since 14:02" |
| `driver` | "Working" |
| `database` | "Waiting for the database since 14:02" |
| `small-call` | "Finishing" |
| One it does not know | The value as it is given, with the time since |

Arbol never ends an Exchange for waiting, however long it waits (ARC-D61): the Leather Bag stops it when that is wanted. The Trivial Trunk itself ends a run that gives no event for 16 minutes while a command left in the background runs, as failed with `driver_silent` (TRV-0, RCT-D30).

### The composer

The composer is the field below the chat in which the next message is typed. Its text, its working folder and its route are the chat's Draft ([BKD-0](00-the-arbol-backend.md#drafts)).

| Part | Detail |
|---|---|
| The text | Return sends; Shift-Return makes a new line |
| The working folder | Where the agent works. A chat that has messages shows the folder of its last Exchange; a new chat the folder of the Root's last message. "Choose…" opens the Mac's folder dialog through the Swift App (`app.pickFolder`, BKD-1), and the list offers the folders of the Root's recent chats. Changing the folder, or the Subscription, of a chat that has messages says "The agent still gets every message of this chat, but no longer remembers what it read and ran before", because a Driver continues its saved conversation only with the same folder and Subscription and otherwise builds it anew from the chat (TRV-0) ([BKD-D4](00-the-arbol-backend.md#decisions)) |
| The route | The Driver with one of its Subscriptions, the model and the effort, shown as "claude · anthropic · sonnet · high". A chat keeps the route of its last message; a new chat starts with the route of the Root's last message, or with the `route` of `arbol.json` ([BKD-D3](00-the-arbol-backend.md#decisions)). The picker lists every Subscription of every Driver: one that is not signed in is shown with its state and "Sign in…", and cannot be picked. The models and efforts are those of the Subscription's own catalogue (DRV-1) |

**Saving the Draft.** The window saves the Draft half a second after the Leather Bag stops typing, and at once when another chat is opened, before a message is sent, and when the window closes (`draft.save`), each time over the revision it last saw. A Draft that cannot be saved, for example because the database is away, is said so below the composer, "Draft not saved: the database does not answer", and the window tries again every 5 seconds while it keeps the text. A Draft is restored in every window that opens its chat. When another window saves a newer Draft of the same chat, this window takes it at once while its own composer holds nothing unsaved. When it holds unsaved text, its next save is refused with `draft_conflict`, and the composer shows both texts, "Changed in another window", with "Keep mine" and "Take theirs", so that no window overwrites text it has not seen.

### Sending and stopping

**Sending.** Return or the button "Send" sends the message with the composer's folder and route (`chat.send`, BKD-1). The window shows the message in the chat at once, marked as being sent, and then:

| The backend answers | The window |
|---|---|
| Accepted | Follows the Exchange as it arrives. The composer is empty |
| Refused | Takes the message out of the chat, keeps the Draft in the composer as it was, and says why below the composer, such as "Not sent: the database does not answer" ([ARC-2](../architecture/02-chat-exchange-across-components.md#the-steps)) |
| `disconnected` or `no_answer` | Keeps the message marked as being sent, and sends it again with the same Exchange identifier, at once or once the backend is back, so that it runs once (BKD-1) |

**A chat that is busy.** A chat takes one Exchange at a time (ARC-D54). Observed in version 1: a message sent while the agent ran asked "Stop current response?" first, and that question also came on chats where nothing ran. While its last Exchange is in progress, the button "Send" becomes "Stop", and the Leather Bag can go on typing the next message. Return then offers "Stop and send": the window stops the Exchange, waits until it is saved, and sends the message. A message the Trunk refuses with `chat_busy`, because another window sent one at the same moment, is kept in the composer with the message "Another message of this chat is running".

**Stopping.** "Stop", or ⌘-period, asks the backend to stop the Exchange (`exchange.stop`). From that moment until it has ended, the Exchange shows "Stopping…", in every window that shows it ([ARC-3](../architecture/03-stuck-trunks.md#a-stop-that-is-not-obeyed)). It shows "Stopped" only once its end says `cancelled`; when the Root manager had to end it by force, it shows "Interrupted", and when it had ended otherwise before the stop reached it, that state (RCT-2). The window counts the Exchange as ended, and offers "Send" and "Send again", only once it is saved (BKD-1), and the chat then takes a new message.

### Questions of the agent

When the agent asks the Leather Bag something (DRV-3), the Exchange shows the questions with their options, one choice or several as each question allows, a button "Answer" and a button "Decline", and the chat's row in the list shows "Waiting for you". "Answer" sends the chosen options (`exchange.answer`); "Decline" sends a decline, which ends the run as cancelled (DRV-3). The window shows the answer as given once the line `answer` is in the file, and the question closed at `ask_closed`; an answer the Driver did not take shows its `control_refused` message, and the question stays open.

### A failed Exchange

A failed Exchange shows "Failed" and its cause in plain words, with the code and the message of the error below it in a lighter type, so that nothing of the cause is lost ([RCT-2](../../arbol-root/contract/02-starting-stopping-and-settling.md#the-end)):

| Code | The window says |
|---|---|
| `rate_limited` | "The account reached its limit." With `retryAfterSeconds`: "It resets at 15:30." It offers "Send again", with the route picker open, so that another Subscription or model can be picked ([ARC-2](../architecture/02-chat-exchange-across-components.md#a-rate-limit)). Picking what a Brain Recipe chooses next comes with SYL-191 |
| `not_signed_in`, `credential_rejected` | "The account is not signed in", with "Sign in…" ([below](#accounts)) |
| `context_exceeded` | "The chat is too long for this model" |
| `driver_failed` | "The Driver could not run" |
| `driver_silent` | "The Driver stopped answering" |
| `events_file_full` | "The answer grew too large" |
| `database_unavailable` | "The database did not answer" |
| `folder_unwritable` | "The Exchange's folder could not be written" |
| `trunk_failed` | "The Trunk failed" |
| One it does not know | The code and its message ([RCT-2](../../arbol-root/contract/02-starting-stopping-and-settling.md#the-end)) |

The chat takes a new message after a failed Exchange ([ARC-2](../architecture/02-chat-exchange-across-components.md#an-exchange-whose-process-is-gone)).

### Sending again and renaming

**Sending again.** The chat's last Exchange, once it has ended and is saved, offers "Send again": at once below a failed, stopped or interrupted Exchange, and in the Exchange's menu below a completed one. It opens a small panel with the route picker, set to the route the Exchange ran with, and the line "The answer below is replaced. Changes the agent made to files stay." "Send" there sends the message again (`exchange.sendAgain`): once it is accepted, the old answer disappears from the chat and the new one arrives in its place ([RCT-2](../../arbol-root/contract/02-starting-stopping-and-settling.md#sending-a-message-again)).

**Renaming.** "Rename" in the chat's header, or a click on its title, makes the title editable: Return keeps it (`chat.rename`), Escape goes back, and an empty title takes the title away, so the chat shows its placeholder again. A title has at most 240 characters.

### Accounts

The window lists the accounts of every Driver in a panel opened from the route picker ("Accounts…"), and from "Sign in…" of a failed Exchange or of a Subscription in the picker ([ARC-0](../architecture/00-components-and-boundaries.md#accounts), [BKD-D17](#decisions)):

| For each Subscription | Detail |
|---|---|
| What it is | Its Driver, its label and its identifier, such as "Claude · Anthropic (`anthropic`)" |
| Its state | Signed in, signed out, signing in, or needs attention with the vendor's reason and what to do (DRV-1) |
| Its usage | The windows of its last usage report: how much is used and when it resets, with "Refresh" (`accounts.usage`) |
| What can be done | "Sign in" when it is not signed in or needs attention, "Sign out", and "Check" (`accounts.check`) |

**Signing in** shows the Driver's steps in the panel as they come ([DRV-1](../driver-contract/01-subscriptions.md#signing-in)):

| Step | The panel |
|---|---|
| `open_url` | Shows the address and, when the step has one, the code to type on the vendor's page, and opens the address through the Swift App in a window that refuses every other host (`app.openSignIn`, BKD-1). It says when the attempt expires |
| `enter_code` | A field for the code the vendor showed, with the step's prompt |
| `store_secret` | The step's prompt and the Keychain item it names, with the words "Store the key on the Secrets page of Seqoya Lab", and until that page exists the `security` command that stores it by hand. The panel takes no key; it waits until the Driver finds the item filled and goes on ([BKD-D10](00-the-arbol-backend.md#decisions)) |
| `done` | "Signed in", and the Subscription can be picked |
| `failed` | The error, with "Try again" |

The panel follows the attempt the backend gave it (`signIn.start`, BKD-1), so a window that was hidden while the vendor's page was open finds the attempt where it was. "Cancel" ends the attempt (`signIn.cancel`); closing the panel ends it too, and the backend ends it by itself 30 seconds after the window's connection closed (BKD-0).

### Attention

Every attention item of the Root is a line across the top of the window for as long as it lasts, with its message: a warning in the colour of warnings, an urgent one in the colour of errors ([BKD-1](01-the-bridge.md#attention)). For example, while the database server is away: "The database server does not answer at 127.0.0.1:5433. New messages cannot be sent; answers in progress go on." ([ARC-D53](../architecture/02-chat-exchange-across-components.md#decisions)). The line goes when the item closes.

### The Root's panel

| Line | Example |
|---|---|
| The Root | "First Sapling (`sapling`), working, Build 6" |
| The chats | Every retained Root's database, such as "First Sapling: 3.2 GiB" |
| The database server | "Answers. Its data folder: 3.5 GiB. Free on its disk: 8.6 GiB" |
| Other Roots | "Running in other Roots: <the second Root's display name>, 1 Exchange", or what failed for a Root |

The panel measures again when it opens (`health.measure`) and asks for the other Roots' Exchanges (`roots.list`).

### Coming back

| When | The window shows |
|---|---|
| A chat opened again later | The chat as the chat tables hold it. An Exchange that is still in progress is followed from its first line on, so the whole answer so far is there ([ARC-2](../architecture/02-chat-exchange-across-components.md#the-arriving-answer-is-a-file)) |
| A chat open in two windows | The same chat in both, with the answer arriving in both |
| The backend goes away | A line "Reconnecting…" across the top. The chat stays as it was shown, the composer still takes text, and when the backend is back the window reads everything again and saves the Draft (BKD-1) |
| The database cannot be reached | The attention line. Chats already shown stay shown, a chat that is opened says that it cannot be read now, a message is refused with its cause and stays in the composer, and answers in progress keep arriving |
| An Exchange that ended while the database was away | Its answer from its folder, marked "Not yet saved", until the backend has had it settled ([ARC-D53](../architecture/02-chat-exchange-across-components.md#decisions)) |
| An Exchange whose process is gone | "Interrupted", until it is settled and then as saved ([ARC-2](../architecture/02-chat-exchange-across-components.md#an-exchange-whose-process-is-gone)) |
| A stuck Exchange that the backend ended | "Ended because it was stuck" ([ARC-3](../architecture/03-stuck-trunks.md#ending-a-stuck-exchange)) |

### Its renderer bundle

Each window shows a page loaded from Elma Chat's *renderer bundle*, the files built from the folder `ui/elma/` of the `arbol` repository into `ui/elma/` of each `arbol` Build, where the Swift App loads them ([BKD-0](00-the-arbol-backend.md#its-program-and-its-build)). It is written in TypeScript with Svelte 5, from the components of the Arbol design system, the repository `arbol-design-system`: the conversation, the composer, the response, the tool call and the question ([BKD-D18](#decisions)). The bundle holds everything it needs, fonts included, and reaches nothing but the Bridge and the app channel: its content security policy allows no other address.

## Requirements

| ID | Elma Chat's first window must… | Origin | Verified by |
|---|---|---|---|
| BKD-2.1 | belong to one Root and talk only to its backend, and show in its header the Root's display name and, for a Root that is not `working`, its state, with the reason of a failed one | Changed | journey |
| BKD-2.2 | list every chat of its Root, the newest activity first, each with its title or else the first line of its first message as a placeholder that is never stored, the last part of its working folder, the state of its last Exchange and whether it has a Draft | Changed | journey |
| BKD-2.3 | show a chat's Exchanges in the order of their numbers without the replaced ones, each with its message, its blocks of text as Markdown that runs no HTML, its tool calls closed to one line, its questions with their answers, the Subscription and the model that ran, its tokens, and how it ended when it did not complete | Changed | journey |
| BKD-2.4 | show an Exchange in progress from the first line of its `events.jsonl` on, as it arrives, in every window that shows its chat, however late the window was opened, with the model's reasoning in a closed block while it arrives | Changed | journey, drill |
| BKD-2.5 | show beside an Exchange in progress what it waits for and since when, such as "Running a command for 2 h 10 min" or "Waiting for your answer since 14:02", and never end it for waiting | Changed | journey |
| BKD-2.6 | keep the composer's text, folder and route as the chat's Draft, saved half a second after typing stops and at once on leaving the chat, sending and closing; say when a Draft could not be saved and try again; restore it in every window; save only over the revision it last saw, and show both texts when another window saved meanwhile; and write nothing into the page's own storage | Changed | journey, drill |
| BKD-2.7 | let the Leather Bag pick the working folder through the Mac's folder dialog or the recent folders, and the route from every Subscription of every Driver, with the models and efforts of its catalogue, offering a Subscription that is not signed in only for signing in, and say what changing the folder or the Subscription of a chat costs | Changed | journey |
| BKD-2.8 | on a stop, show "Stopping…" from the request until the Exchange has ended, then "Stopped" only when its end says `cancelled`, and otherwise its true final state, and count an Exchange as ended, for sending and sending again, only once it is saved | Changed | journey, drill |
| BKD-2.9 | show a failed Exchange with its cause in plain words and its code and message, a code it does not know with its message, and for `rate_limited` the time it resets and "Send again" with the route picker open | Changed | journey |
| BKD-2.10 | show an Exchange whose process is gone as interrupted, and one that ended while the database was away from its folder, marked "Not yet saved", until each is settled | Changed | drill |
| BKD-2.11 | keep a refused message in the composer as it was, with the refusal's cause below it | Changed | drill |
| BKD-2.12 | while its chat's last Exchange is in progress, replace "Send" with "Stop", go on taking text, and offer "Stop and send" | Kept | journey |
| BKD-2.13 | show under an Exchange the backend ended because it was stuck "Ended because it was stuck", and that what had arrived is kept | New | drill |
| BKD-2.14 | offer "Send again" on the chat's last Exchange once it has ended, with the route it ran with, saying that its answer is replaced and changes to files stay; and let the chat be renamed, an empty title taking the title away | Changed | journey |
| BKD-2.15 | list the Subscriptions of every Driver with their state and usage, and sign one in by showing each step of the Driver's `sign-in` as it comes: the address opened in a window that refuses other hosts, a field for a code, and for a key the Keychain item to fill on the Secrets page, taking no key itself | Changed | journey; the host limit with SYL-192 |
| BKD-2.16 | show every attention item of its Root across the top of the window for as long as it lasts, and in the Root's panel the size of every retained Root's database, the data folder's size, the free space of its disk, whether the server answers, and the Exchanges running in other Roots | New | journey, drill |
| BKD-2.17 | when the backend goes away, say that it reconnects, keep showing the chat and taking text, and read everything again once it is back | Changed | drill |
| BKD-2.18 | be a renderer bundle in `ui/elma/` of the `arbol` Build, written in TypeScript with Svelte 5 from the components of `arbol-design-system`, that reaches nothing but the Bridge and the app channel, never leaves its own page, and opens an `http` or `https` link only through `app.openLink`, showing any other link as text | Kept | unit |
| BKD-2.19 | show a question of the agent with its options, one or several as each question allows, "Answer" and "Decline", mark its chat "Waiting for you", show the answer only once its `answer` line is in `events.jsonl`, and keep the question open after a `control_refused` | Changed | journey |

## Interface

The window uses the calls and topics of [BKD-1](01-the-bridge.md#interface) and the app channel's `app.pickFolder` and `app.openSignIn`. Its keys:

| Key | In | Does |
|---|---|---|
| Return | The composer | Sends; while the chat is busy, offers "Stop and send" |
| Shift-Return | The composer | A new line |
| ⌘-period | The window | Stops the open chat's Exchange in progress |
| Escape | A title being renamed, a panel | Goes back, closes the panel |
| ⌘N | The window | A new chat |

## Known problems in version 1

Not to be reproduced.

- **"Stopped" before anything had stopped.** The window showed the stop at once and ignored a failed cancel; a cancelled answer opened again looked completed, because nothing marked it.
- **A placeholder stored as the title.** The window stored "Elma · <repository>" as the title, so no title was ever made for chats started there.
- **Text missing in a late window.** A window opened while an answer was arriving missed the text not yet sealed.
- **Drafts with several owners.** Windows overwrote each other's Drafts, a late "clear" could delete newer text, and a save that failed was never shown.
- **A window that stopped listening.** After its first local change, the window stopped rebuilding the chat from the backend, so changes made in another window showed only when the chat was opened again.
- **"Stop current response?" on an idle chat.** The window and the coordinator disagreed on whether the chat ran.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/03-turn-execution.md#Known problems and lessons`
- `arbol_deprecated_v1:product-spec/02-chat-sessions.md#Known problems and lessons`
- `arbol_deprecated_v1:product-spec/04-composer-drafts-and-branching.md#Known problems and lessons`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#9. A draft had more than one owner`
- `arbol_deprecated_v1:renderer/apps/elma/src/App.svelte#stopAgent`

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| BKD-D17 | Where does the Leather Bag sign in, in the first thin path, the first version that goes once through every part (ARC-1)? | In Elma Chat's window: a panel of accounts opened from the route picker and from a failed Exchange, which lists every Subscription with its state and usage and shows the Driver's sign-in steps, because the first thin path then needs no second UI and ARC-0 has the Leather Bag sign in from an Arbol UI. A key is never typed there: a Subscription that signs in with a key is sent to the Secrets page of Seqoya Lab, and until that page exists the panel shows the Keychain item to fill by hand (ARC-D62). For example: "claude · anthropic: Signed out", "Sign in" opens the vendor's page in a window that refuses other hosts, and after you approve there the panel shows "Signed in" and the route can be picked. When Seqoya Lab has a page of Subscriptions, the panel can move there. The alternative: no sign-in in the first window; the window only says that an account needs it, and you sign in at the terminal with `arbol-claude-driver subscriptions sign-in anthropic` until Seqoya Lab has the page | Open: a question for the owner |
| BKD-D18 | In what is the window written? | TypeScript with Svelte 5, from the components of `arbol-design-system`, which already holds the conversation, the composer, the response, the tool call and the question in that form; built into the `arbol` Build. The alternative: another framework, which would rebuild those components | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D19 | What does the list show for a chat without a title? | The first line of its first message, at most 80 characters, in a lighter type, never stored, because a stored placeholder kept titles from being made in version 1 and RCT-3 forbids it. The Trivial Trunk makes no titles (TRV-0), so every chat of the first thin path shows its placeholder until it is renamed | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D20 | Is the reasoning of the model shown? | Yes, while the answer arrives, in a closed block that can be opened. The chat tables keep none (RCT-3), so a chat opened again shows none. The alternative: never shown, which hides what the agent is doing during a long think | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D21 | When is a Draft saved, and what if two windows type in it? | Half a second after typing stops, and at once on leaving the chat, sending and closing the window; a failed save is said and tried again every 5 seconds. Each save names the revision it was made over; when another window saved meanwhile, the save is refused and the composer shows both texts, with "Keep mine" and "Take theirs". The alternative: the last save wins, which loses text typed in the other window; or a copy in the page's own storage as well, as version 1 had, which made a second owner of the Draft | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D22 | What can the first version of Elma Chat do? | One kind of window, of which several can be open: the chats of its Root on the left, newest first, one chat on the right. In it you start a chat in a folder you choose, send a message, see the answer arrive, answer the agent's questions, stop an answer, send a message again, rename a chat, sign in to an account, and open a chat again later. For example, in First Sapling you open "New chat", choose `~/repos/shop`, ask "What does build.sh do?", and the next day find the chat at the top of the list, named after its first words until you rename it, because the Trivial Trunk makes no titles (TRV-0). The model's reasoning is shown while it arrives and is not kept (RCT-3). Branches, edited messages, search, tags, archiving and deleting chats, attachments, and Willo Station and Seqoya Lab come later. The alternative: a smaller first window, one chat only with no list, which the first thin path could pass with but which cannot open a chat again from the window | Open: a question for the owner |
