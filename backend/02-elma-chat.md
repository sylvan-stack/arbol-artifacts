---
role: authored
spec: BKD-2
status: accepted
---
# Arbol backend · 02 Elma Chat, its first version

[Elma Chat](../GLOSSARY.md#elma-chat) is the [UI](../GLOSSARY.md#ui) in which the [Leather Bag](../GLOSSARY.md#leather-bag) talks with an agent. Its first version in Arbol 2, in First Sapling, looks and works as Elma Chat of version 1 did ([BKD-D22](#decisions)): one window with a navigation panel on the left, the chat on the right showing one [Chat Exchange](../GLOSSARY.md#chat-exchange) at a time (*Exchange* for short: one message of the Leather Bag and the agent's answer to it), the composer below it, and a status bar at the bottom. For example, the Leather Bag presses ⌘2 to start a chat in the second repository, types "What does build.sh do?" and presses ⌘⏎: the message is pinned at the top, "Starting agent…" turns into the answer arriving word by word, the agent's `cat build.sh` shows as one closed line, and once the answer is complete the tool calls stand above a line, the *Answer Threshold*, and the answer below it. The next day ⌃⇧⌘C lists the chat among the latest, and Return opens it again. This specification states what the window shows and does, which parts of version 1 it keeps, which it changes because Arbol 2 works differently, and which are not in First Sapling. The backend it talks to is [BKD-0](00-the-arbol-backend.md), and the messages they exchange are [BKD-1](01-the-bridge.md). It matters because the owner decided that the window keeps version 1's form, and because version 1 showed "Stopped" before anything had stopped, lost the text still arriving in a window opened late, and let Drafts be overwritten.

It follows the conventions of the [Driver Contract](../driver-contract/README.md#conventions) and the additions in this chapter's [README](README.md#conventions). *Observed in version 1* below means version 1's Elma Chat as its product specification and its renderer describe it. Where nothing else is said, the first version keeps it; *Changed* says what differs, and why.

## Scope

Covered: the window, the navigation panel, the Exchange shown, the answer as it arrives, the status of an Exchange, the composer and Drafts, the route, the repositories, sending and stopping, questions of the agent, a failed Exchange, the chat's own actions, the latest chats, opening a chat from elsewhere, signing in, attention, coming back, the renderer bundle, and what First Sapling leaves out.

Not covered: the tray menu, the global hotkeys, resizing the window from its header and the native panel of the latest chats, which are the Swift App's (SYL-192); Willo Station's own side of opening a chat, which is its own specification; the tool with which an agent books a work area ([BKD-D4](00-the-arbol-backend.md#decisions)); the Root-owned migration SQL/global commands (SYL-195); their additive display/action binding is below and implemented in the Backend Arc.

## Behaviour

### The window

Observed in version 1: one Elma window, which closing did not quit. Arbol 2 has one Elma Chat window for each Root, opened from the tray menu (SYL-192). There is no list of chats in the window: other chats are reached with the latest chats (⌃⇧⌘C), the repository slots, and from Willo Station.

```text
┌ ✦ Elma Chat · First Sapling - What build.sh does ──────────────────── ↔  A+ A−  ◐ ┐
│ What build.sh does           │ What does build.sh do?                         ‹ 2/3 › │
│ Turn 2 of 3                  │ ────────────────────────────────────────────────────── │
│ ○ Ongoing  ∑ 11.8k ↑9.1k ↓2.7k │ Message sent 09:30 · Agent started responding 09:30 · │
│ + Repositories               │ Agent responded 09:30                                  │
│ History · 3 turns            │ ▸ shell  cat build.sh                              ✓   │
│  Older turn ⌘[               │ ──────────────────── Answer ──────────────────────── │
│  Newer turn ⌘]               │ It compiles the three packages and copies them to      │
│  Jump to turn… ⌘P            │ dist/.                                      Completed  │
│  Quick actions… ⇧⏎           │                                                        │
│ + Intelligence               │ Press Enter to start new message ⏎                     │
├──────────────────────────────┴────────────────────────────────────────────────────────┤
│ arbol-trunk – claude · anthropic – sonnet::high                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

| Part | What it shows |
|---|---|
| The header | The Elma glyph and "Elma Chat · <Root's display name> - <the chat's title>". The Root's display name is the one addition to version 1, because every UI shows its Root ([ARC-1](../architecture/01-roots.md#the-tray-menu-and-arbol-roots)); a Root that is not `working` says so beside it, "preparing", or "failed" with its reason, and the header follows a change of the Root's state (BKD-1). A moving mark while the agent works. On the right, the reading width, the text size (A+, A−) and the theme, twelve wood themes, Redwood unless another was picked |
| The navigation panel | On the left, top to bottom: the chat's title and "Turn n of N"; the chat's own panel, *the cockpit*, once the chat exists; "Repositories"; "History · N turns"; "Intelligence" ([below](#the-navigation-panel)) |
| The chat | On the right: the pinned message, the answer, the questions of the agent above the composer, and the composer ([below](#the-exchange-shown)) |
| The status bar | At the bottom: "<repository> – <Driver> · <Subscription> – <model>::<effort>", such as "arbol-trunk – claude · anthropic – sonnet::high" |
| Attention | A line across the top of the chat for each attention item of the Root ([below](#attention)) |

The window shows what the backend says. In the page's own storage it keeps only conveniences: the chat shown last, the last chat shown for each repository, the 16 repositories used last, the 100 chats shown last, the reading width, the text size and the theme, and text typed and not yet saved ([below](#the-composer)).

**On opening**, the window shows, in this order of what exists: the chat it is asked to open ([below](#opening-a-chat-from-elsewhere)), the chat shown last, the chat last shown in the first repository of the slots, and else an empty chat in that repository with its new-chat Draft.

<!-- sources:
arbol:ui/elma/src/App.svelte
arbol:ui/elma/src/window.svelte.ts
arbol:ui/elma/src/preferences.ts
arbol:ui/elma/design-system/src/sections/ElmaFrame.svelte
arbol:tests/ui/frame.mjs
-->

### The navigation panel

| Part | What it holds |
|---|---|
| The title | The chat's title. A chat without one shows the first line of its first message, at most 80 characters, in a lighter type, here and in the header; "New Chat" before its first message. Below it, "Turn n of N": the place of the Exchange shown among the chat's Exchanges |
| The cockpit | Once the chat exists: the pill "Ongoing" or "Not ongoing", which ⌥0 changes; and the chat's tokens, ∑ in all, and in and out, with the rate at which they grow while the agent works |
| Repositories | The slots ⌘1 to ⌘9 and "Other… ⌘0" ([below](#the-repositories)) |
| History | "Older turn ⌘[", "Newer turn ⌘]" and "Jump to turn… ⌘P" when the chat has more than one Exchange, and "Quick actions… ⇧⏎" |
| Intelligence | "Model: <model> ⌃M" and "Thinking: <effort> ⌃⇥", and one row for each route, ⌃1 to ⌃9 ([below](#the-route)) |

"Repositories" and "Intelligence" open and close with a click on their header (+, −). Both are open in an empty chat and close once the chat has an Exchange, as in version 1.

### A copy with new messages in its original Root

A stale chat shows “New messages in <source Root display name>” and “Bring over again” in its chat actions/list entry, using only Bridge migration metadata and the Root catalogue’s display name. Save the current Draft before the action, call chat.reimport once, then open the returned chat. A replaced copy opens as updated history; a copied result opens as another chat while the continued copy stays. Do not infer the result chat from a title or the source UUID, and never stop or move an agent. After disconnected/no_answer, keep the current content/Draft, refresh the chat list and show “The import may have finished. Check the chat list before trying again.”; no automatic second call. A failed comparison remains visible through attention, without claiming fresh state. No SQL/tool/package details appear in this flow.

### The Exchange shown

The chat shows one Exchange at a time: its message pinned at the top, and its answer below it. A chat opens on its newest Exchange, where the Leather Bag last scrolled to in it.

| Part | Detail |
|---|---|
| The pinned message | The Leather Bag's message, at most three lines, with "See more"; "Copy prompt"; and, when the chat has more than one Exchange, the stepper "‹ 2/3 ›" |
| Moving | ⌘[ and ⌘] step through the chat's Exchanges in the order of their numbers, leaving out every Exchange a message sent again replaced (RCT-3). The counter, and ⌘P, open the history: the chat's messages, newest first, where digits jump to one and "Search" finds a word in the messages loaded |
| More of a long chat | A chat opens with its 12 newest Exchanges; stepping older than the first of them brings the 12 before (`chat.exchanges`, BKD-1). "Turn n of N" and the history count every Exchange of the chat (BKD-1) |

The answer, top to bottom:

| Part | Detail |
|---|---|
| The lifecycle line | "Message sent · Agent started responding · Agent responded", each with its time; times within 3 seconds of each other share a line |
| Thinking | Each block of the model's reasoning, open: "Thinking", or "Thinking 1/2" when there are several ([BKD-D20](#decisions)) |
| A tool call | One closed line: the tool's name, a mark (… running, ✓ done, ! failed, interrupted), and one line of what it did, such as the command of `shell` or the path of `Read`; calls that run side by side say "waiting on this call · 2 of 3 running". Opened: when known, when it started and ended and how long it took; its input and its output. The saved Root Contract rows keep no tool timestamps, so an unobserved saved call says "Not recorded" for those times instead of guessing them; times already observed remain until the chat is read again. A running call shows its time after 60 seconds; an output the Driver cut says so (DRV-2); in a long chat, an input or output that was cut for the Bridge loads whole when opened (`toolCall.get`, BKD-1) |
| The Answer Threshold | Once the Exchange is complete: every block of reasoning and every tool call above a line, and the answer's text below it, as Markdown. While the Exchange runs, there is no line and everything stands in the order it came |
| The status | The status of the Exchange ([below](#the-status-of-an-exchange)), and "Copy answer", which copies the text below the threshold |

Changed from version 1: the chat tables keep no reasoning (RCT-3). When an Exchange is saved, the window keeps the reasoning it showed until the chat is read again, after a reload, a reconnection or a new snapshot; an Exchange read from the database has none.

Markdown in an answer shows headings, lists, emphasis, links, tables and code blocks. Raw HTML in it is shown as text, never run. A link opens in the Mac's default browser through the Swift App (`app.openLink`, BKD-1), and only when it is `http` or `https`; any other link is shown as text, and the window never leaves its own page.

**Scrolling.** An answer that arrives keeps its end in view until the Leather Bag scrolls up. A complete answer opens with the threshold at the top of the view, and while the threshold lies below the view, a small *Answer Beacon* points to it. ⌘⇧⌥8 and ⌘⇧⌥7 jump to the previous and the next reading stop. The window keeps, for each chat, where it was scrolled to while the window lives.

<!-- sources:
arbol:ui/elma/design-system/src/sections/PinnedMessage.svelte
arbol:ui/elma/design-system/src/sections/Response.svelte
arbol:ui/elma/design-system/src/sections/ResponseReader.svelte
arbol:ui/elma/design-system/src/sections/ToolCall.svelte
arbol:ui/elma/design-system/src/components/SafeMarkdown.svelte
arbol:ui/elma/design-system/src/markdown.ts
arbol:ui/elma/design-system/src/sections/HistoryTree.svelte
arbol:tests/ui/navigation.mjs
arbol:tests/ui/response.mjs
arbol:tests/ui/reading.mjs
-->

### The answer as it arrives

While an Exchange is in progress, the window shows the lines of its `events.jsonl` as they come, from the first one on, however late the window was opened ([BKD-1](01-the-bridge.md#subscriptions), ARC-2). It reads them by the Driver's events ([DRV-2](../driver-contract/02-inference.md#the-event-stream)):

| Line | The window |
|---|---|
| `text_delta`, then `text` | Writes the pieces as they come, and puts the whole block in their place when its `text` arrives, because the block is the truth |
| `thinking_delta`, `thinking` | Writes the block of reasoning, open |
| `tool_started`, `tool_output_delta`, `tool_finished` | Opens the line of the tool call with its running mark, keeps its output, and closes it with its result |
| An event with `parentCallId` | Shows what a sub-agent does inside the tool call that started it, while it runs; the saved chat leaves it out (RCT-3) |
| `ask_opened`, `answer`, `ask_closed` | Shows the question above the composer ([below](#questions-of-the-agent)), then the answer given, then closes it |
| `notice` | A short line, such as "The vendor moved the run to another model" |
| `usage` | The tokens in the cockpit |
| `control_refused` | "The answer was not taken: …", with the Driver's message |
| The end | The Exchange's final state ([below](#the-status-of-an-exchange)) |

<!-- sources:
arbol:ui/elma/src/live.ts
arbol:ui/elma/src/window.svelte.ts
arbol:tests/ui/live.mjs
arbol:tests/ui/live_browser.mjs
-->

### The status of an Exchange

One label at a time, the first that holds, in version 1's order, with "Stopping…" and the times of waiting added (ARC-3.12, ARC-3.13):

| The Exchange | Label |
|---|---|
| failed | "Failed" ([below](#a-failed-exchange)) |
| is being stopped | "Stopping…" |
| waits for the Leather Bag's answer | "Waiting for your answer since 14:02" |
| accepted, before the run's `started` event | "Starting agent…" |
| runs a tool call | "Waiting for tools… 2 h 10 min", the time since it waits, from its signs of life (ARC-3) |
| writes reasoning | "Thinking…" |
| writes the answer | "Responding…" |
| any other moment of the run | "<Driver> · <Subscription> is working…" |
| has ended | "Completed", "Canceled", "Interrupted", or "Ended because it was stuck" |

Arbol never ends an Exchange for waiting, however long it waits (ARC-D61): the Leather Bag stops it when that is wanted. The Trivial Trunk itself ends a run that gives no event for 16 minutes while a command left in the background runs, as failed with `driver_silent` (TRV-0, RCT-D30).

Changed from version 1: there is no label "Routing to …" and no waiting for a rate limit to pass, because a Trunk takes the route it is handed and ends an Exchange that met a rate limit as failed (ARC-2); no waiting for an approval, because no agent asks for permission (DRV-3); and no "Ready", because a chat without an Exchange shows the empty composer.

| Changed state | The window says |
|---|---|
| `interrupted` | "Interrupted: the agent's process ended before the answer was finished. What had arrived is kept." |
| `interrupted`, with the note `ended_stuck` | "Ended because it was stuck. What had arrived is kept." ([ARC-3](../architecture/03-stuck-trunks.md#ending-a-stuck-exchange)) |
| `unsaved` | The answer from its folder, marked "Not yet saved", until the backend has had it settled ([ARC-D53](../architecture/02-chat-exchange-across-components.md#decisions)) |
| `gone` | "Interrupted", until it is settled and then as saved ([ARC-2](../architecture/02-chat-exchange-across-components.md#an-exchange-whose-process-is-gone)) |

<!-- sources:
arbol:ui/elma/src/live.ts
arbol:ui/elma/design-system/src/sections/elma-response.ts
arbol:tests/ui/live.mjs
arbol:tests/ui/live_browser.mjs
-->

### The composer

The composer is the field below the answer in which the next message is typed.

| Part | Detail |
|---|---|
| An empty chat | The line "<repository> · <Driver> · <Subscription> · model: <model> · thinking: <effort>", then the composer of at least 10 lines, in the middle, with "Message <repository>…" and the hint "⌘⏎ to Send". There are no buttons |
| A chat with Exchanges | The composer is closed to the line "Press Enter to start new message ⏎", with "Scroll to top" and "Scroll to bottom"; Return opens it, at least 3 lines, with the hint "⌘⏎ to Send · Esc to collapse", and Escape closes it again. A chat whose Draft holds text opens with the composer open and in focus |
| Keys | ⌘⏎ or ⌃⏎ sends; Return makes a new line; Escape closes the composer |
| A long paste | Text of 10,000 characters or more that is pasted is saved as a file (`paste.save`, BKD-1), and the composer gets `[Pasted text (12,345 characters)](<path>)` in its place. Meanwhile the hint says "Saving pasted text…", and a ⌘⏎ pressed meanwhile sends once the link is in. Changed from version 1: the file stays in the Root's folder `pastes/`, not in the system's temporary folder, because the chat names it |

**Drafts.** Observed in version 1, and kept: each chat has one Draft of its reply, and each repository one Draft of a new chat. A Draft holds the text; the route and the folder are the chat's settings ([below](#the-route)). The window saves the Draft 350 milliseconds after the Leather Bag stops typing, and at once when the composer loses the focus or another chat is shown (`draft.save`), each time over the revision it last saw ([BKD-0](00-the-arbol-backend.md#drafts)).

Changed from version 1, so that a Draft has one owner, the backend:

| | |
|---|---|
| A failed save | Is said below the composer, "Draft not saved: the database does not answer", and the window tries again every 5 seconds |
| Text not yet saved | The page keeps only text not yet saved, with the revision it was typed over. After a reload it offers that text back only while the backend's Draft still has that revision |
| A conflict | When a save is refused because the Draft was saved from another connection meanwhile, such as the browser tab of the development relay or a page reloaded while its old connection closed (BKD-1), the composer shows both texts, "Changed elsewhere", with "Keep mine" and "Take theirs". A conflict whose Draft holds the composer's own text is taken without asking |

### The route

The *route* is what answers a message: a Driver with one of its Subscriptions, a model and an effort, such as `claude · anthropic · sonnet · high`. Elma Chat uses no Brain Recipe: the route is the Leather Bag's choice, or a default ([BKD-D3](00-the-arbol-backend.md#decisions)).

| Picker | Keys | What it offers |
|---|---|---|
| The route rows | ⌃1 to ⌃9 | One row for each Subscription of each Driver, such as "claude · anthropic", "claude · zai" and "codex · chatgpt" (`accounts.list`). A Subscription that cannot be used is shown with its state, "logged out" or "needs attention", and cannot be picked ([below](#signing-in)) |
| Model | ⌃M | Goes to the next model of the Subscription's catalog (`accounts.models`, DRV-1) |
| Thinking | ⌃⇥ | Goes to the next effort the model accepts, in the vendor's words (DRV-1) |

Observed in version 1: a model or effort picked was saved for the chat at once and counted from its next message on, also while the agent worked, and a route picked counted from the next message. Changed: a chat that exists saves a route picked at once too (`chat.settings`, BKD-1). In an empty chat a choice stays in the window and goes with the first message, as in version 1. Picking another route sets the model and the effort to that route's defaults.

The defaults of a new chat, the first of these whose Subscription is signed in, as in version 1 ([BKD-0](00-the-arbol-backend.md#settings)):

| | Default |
|---|---|
| The route | The default route of the chat's repository in `arbol.json`, else the default route of `arbol.json`, else the first signed-in Subscription of the first Driver |
| The model | The model the route names, else the catalog's default model (DRV-1) |
| The effort | The effort the route names, else the model's default effort, else `high` where the model accepts it |

Changed from version 1: version 1 picked an Intelligence Provider, a named route that Seqoya Lab bound to a Subscription, with settings of its own and seven thinking levels. Arbol 2 keeps the Intelligence Provider ([ARC-D22](../architecture/00-components-and-boundaries.md#decisions)), but its settings come with SYL-191; until then a row is a Subscription, and the efforts are those the vendor names for the model.

### The repositories

Observed in version 1, and kept: the slots ⌘1 to ⌘9 offer repositories, first the stack's folder itself, then the repositories used last, then the others; "Other… ⌘0" opens the Mac's folder dialog (`app.pickFolder`, BKD-1). A key always starts a new chat in that repository. A click on a slot while a chat is shown moves that chat to the repository, which is refused while its agent works ("Wait for the current turn to finish before changing Repo") and confirmed with "Repo changed to …"; a click with no chat shown is the same as the key. Changing the repository of a chat that has Exchanges says "The agent still gets every message of this chat, but no longer remembers what it read and ran before", because a Driver continues its saved conversation only in the same folder and otherwise builds it anew from the chat (TRV-0).

Changed from version 1, as the owner decided ([BKD-D4](00-the-arbol-backend.md#decisions)): a slot gives the agent the repository's folder in `~/repos/sylvan-stack/readonly/`, which always holds the last merged `main` and which nobody edits, and the stack's own slot `~/repos/sylvan-stack/readonly/` itself. The slots list the repositories of `readonly/` and never the named work areas. An agent that has to change files books a work area with its tool when it needs one, and the chat's folder stays as it is. A folder picked with "Other…" is used as it is. Also changed: a key brings back the repository's new-chat Draft, which version 1 did not.

### Sending and stopping

**Sending.** ⌘⏎ sends the message with the chat's route and folder (`chat.send`, BKD-1). The new Exchange appears at once, its message pinned and "Starting agent…" below it, and the composer closes. Then:

| The backend replies | The window |
|---|---|
| Accepted | Follows the Exchange as it arrives. The chat is marked ongoing ([below](#the-chats-own-actions)) |
| Refused | Takes the Exchange out, puts the text back in the composer as it was, and says why below the composer, such as "Not sent: the database does not answer" ([ARC-2](../architecture/02-chat-exchange-across-components.md#the-steps)) |
| `disconnected` or `no_answer` | Keeps the Exchange as being sent, and sends the same call again, with the same Exchange identifier, at once or once the backend is back, so that the message runs once (BKD-1) |

**A chat that is busy.** Observed in version 1: sending while the chat's last Exchange runs asks "Stop current response?"; "Confirm" stops it and then sends (ARC-D54). Changed: the question comes only while the backend says that the Exchange runs, never on a chat whose Exchange has ended, and the window sends only once the stopped Exchange is saved. A message refused with `chat_busy`, because a message of the same chat was sent elsewhere at the same moment, such as from the command line (SYL-193), goes back into the composer with "Another message of this chat is running".

**Stopping.** ⌘Esc stops the Exchange in progress (`exchange.stop`). Changed from version 1: from that moment until it has ended, the Exchange shows "Stopping…", and "Canceled", with the line "⏹ Stopped", only once its end says `cancelled` ([ARC-3](../architecture/03-stuck-trunks.md#a-stop-that-is-not-obeyed), RCT-2). When the Root manager had to end it by force, it shows "Interrupted"; when it had ended otherwise before the stop reached it, that state. A stopped Exchange shown again later is still "Canceled", because its end is kept.

The window counts an Exchange as ended, for sending, "Retry" and "Continue from failure point", only once it is saved (BKD-1).

### Questions of the agent

Observed in version 1: the questions of the agent stand above the composer, each with its header, its text and its options, one choice or several ("You can pick more than one"). "Submit" can be pressed once every question that has options has a choice; "Continue" shows instead when no question has options. There is no answer in free text. Changed: "Cancel" declines, which ends the run as cancelled (DRV-3), and the window shows the answer as given only once its `answer` line is in the file (`exchange.answer`), and the question closed at `ask_closed`; an answer the Driver did not take shows its `control_refused` message, and the question stays.

### A failed Exchange

Observed in version 1, and kept: a failed Exchange shows "Failed", "Failed at: <time>", "Error: <cause>" and, at the end, "⚠︎ <cause>", with two buttons, "Retry" and "Continue from failure point".

| | |
|---|---|
| The cause | In plain words, with the code and the message of the error below it, so that nothing of the cause is lost; a code the window does not know is shown with its message ([RCT-2](../../arbol-root/contract/02-starting-stopping-and-settling.md#the-end)) |
| Retry | Sends the message again in its place: the answer is replaced and changes the agent made to files stay (`exchange.sendAgain`, RCT-2). It runs in the folder of the Exchange it replaces, also when the chat was moved since |
| Continue from failure point | Sends "proceed" as the chat's next message, with the chat's route |
| `rate_limited` | "The account reached its limit", and with `retryAfterSeconds` "It resets at 15:30". "Retry" goes with the route the rows show, so another route can be picked first ([ARC-2](../architecture/02-chat-exchange-across-components.md#a-rate-limit)) |
| `not_signed_in`, `credential_rejected` | "The account is not signed in", with how to sign it in ([below](#signing-in)) |

| Code | In plain words |
|---|---|
| `context_exceeded` | "The chat is too long for this model" |
| `driver_failed` | "The Driver could not run" |
| `driver_silent` | "The Driver stopped answering" |
| `events_file_full` | "The answer grew too large" |
| `database_unavailable` | "The database did not answer" |
| `folder_unwritable` | "The Exchange's folder could not be written" |
| `trunk_failed` | "The Trunk failed" |

Changed from version 1: "Retry" and "Continue from failure point" show only on the chat's last Exchange. Version 1 retried a failed Exchange wherever it stood and continued from it as a branch; branches come with a later Root ([BKD-D22](#decisions), RCT-D21).

### The chat's own actions

| Action | Keys | Detail |
|---|---|---|
| Rename | ⌘-click the title in the header, or the quick action R | An inline field with "OK" and "Cancel" (`chat.rename`); before the chat's first message, "Start a chat before renaming". A title has at most 240 characters. Changed from version 1: an empty title takes the title away, where version 1 refused it, and a chat without a title shows a placeholder that is never stored ([BKD-D19](#decisions)) |
| Ongoing | ⌥0, or the pill in the cockpit | Every accepted message marks the chat ongoing; only ⌥0 or the pill clears it, with "Marked ongoing" or "Cleared ongoing" (`chat.mark`) |
| Archive | ⌘⌫, or the quick action A | After a confirmation that says a running answer is stopped first: stops it, archives the chat, which leaves the latest chats, forgets it as the chat shown last and as its repository's last chat, and shows an empty chat in the same repository with its new-chat Draft. Nothing archives a chat by itself, and no chat is deleted (`chat.mark`) |
| Copy session ID | The quick action C | Copies the chat's identifier |
| Quick actions | ⇧⏎ | "Rename chat session" R, "Archive" A, "Copy session ID" C |

### The latest chats

Observed in version 1: ⌃⇧⌘C shows the latest chats, at most 100, without the chat that is shown: first the chats shown in Elma, the last shown first, then the others by their latest activity. Each row has the title, the repository, the route, the state of the last Exchange and how long ago. Digits 1 to 0 open the first ten, the arrows and Return any, and Escape closes the list (the `chats` topic, BKD-1). Archived chats are not in it. In version 1 the list was a panel of the native shell, and in Arbol 2 it is the Swift App's (SYL-192); until it exists, the window shows the same list over itself, with the same keys.

### Opening a chat from elsewhere

Observed in version 1: Willo Station, the latest chats and the native shell could ask Elma to open a chat, and the request waited until Elma took it, so that one made while Elma loaded was not lost. Kept: the Swift App keeps such a request, the chat to open and, for a new chat, the repository, until the window takes it (`app.takeOpen`, BKD-1), and tells an open window at once. The window saves the Draft of the chat it shows, then shows the chat asked for, with its Draft. Opening a chat from Willo Station is needed in First Sapling (the owner, 19 October 2026): this is Elma Chat's side of it, and Willo Station's side, which card or result asks for which chat, is Willo Station's own specification.

### Signing in

The Leather Bag signs in with the Driver's own command, at the terminal, until Seqoya Lab has a page for it ([BKD-D17](#decisions)). A route row of a Subscription that cannot be used, and a failed Exchange whose account is not signed in, say so and name the command, for example "claude · zai: logged out. Sign in with: arbol-claude-driver subscriptions sign-in zai". The window takes no code and no key, and no secret crosses the Bridge ([BKD-D10](00-the-arbol-backend.md#decisions)). Once the Subscription is signed in, the row can be picked; the window reads the Subscriptions again when it is shown and when a row is clicked (`accounts.list`). Version 1 signed in on the Subscriptions page of Seqoya Lab.

### Attention

Every attention item of the Root is a line across the top of the chat for as long as it lasts, with its message: a warning in the colour of warnings, an urgent one in the colour of errors ([BKD-1](01-the-bridge.md#attention)). For example, while the database server is away: "The database server does not answer at 127.0.0.1:5433. New messages cannot be sent; answers in progress go on." ([ARC-D53](../architecture/02-chat-exchange-across-components.md#decisions)). Version 1's Elma had no such line; a database that does not answer is not a normal state, and Arbol says so.

### Coming back

| When | The window shows |
|---|---|
| A chat opened again later | The chat as the chat tables hold it. An Exchange that is still in progress is followed from its first line on, so the whole answer so far is there ([ARC-2](../architecture/02-chat-exchange-across-components.md#the-arriving-answer-is-a-file)) |
| The same chat on two connections, such as the window and the browser tab of the development relay, or a page reloaded while its old connection closes | The same chat on both, with the answer arriving on both |
| The backend goes away | A line "Reconnecting…" across the top. The chat stays as it was shown, the composer still takes text, and when the backend is back the window reads everything again and saves the Draft (BKD-1) |
| The database cannot be reached | The attention line. The chat shown stays shown, a chat that is opened says that it cannot be read now, a message is refused with its cause and stays in the composer, and answers in progress keep arriving |

### Its renderer bundle

Each window shows a page loaded from Elma Chat's *renderer bundle*, the files built from the folder `ui/elma/` of the `arbol` repository into `ui/elma/` of each `arbol` Build, where the Swift App loads them ([BKD-0](00-the-arbol-backend.md#its-program-and-its-build)). It is written in TypeScript with Svelte 5, as version 1's Elma was, from the components of the Arbol design system, the repository `arbol-design-system`, and its pages `elma-new-chat`, `elma-conversation` and `elma-history`. Where a component of the design system differs from version 1, such as a "Send" button, an answer in free text, reasoning shown closed, or another stepper, the window follows version 1, and the design system is brought in line with it, as its own rules ask ([BKD-D18](#decisions)). The bundle holds everything it needs, fonts included, and reaches nothing but the Bridge and the app channel: its content security policy allows no other address.

<!-- sources:
arbol:ui/elma/package.json
arbol:ui/elma/vite.config.ts
arbol:ui/elma/index.html
arbol:tools/elma_bundle.py
arbol:scripts/package_backend.py#package
arbol:scripts/backend_package.py#verify
arbol:tools/sync_elma_design.py
arbol:tools/bridge_relay.py
arbol:tests/ui/test_bundle.py#Bundle
arbol:tests/ui/relay_browser.mjs
-->

### Renderer implementation boundaries (BKD-D35)

The application imports a checked source snapshot of the maintained design system: only the used successor components, their type/style/theme files and locally licensed fonts, never heritage code. Its manifest binds the design-system commit and each copied file hash; an explicit sync/check command fails on divergence. The Arbol source therefore builds independently of any sibling checkout. The design-system source stays the maintained reference and is changed and qualified in the same Beat. Package versions and npm integrity lockfiles are pinned. The renderer CSP allows only its bundled scripts/styles/fonts and its same-origin development WebSocket, with no network Markdown resources, frames, forms, object embedding or inline scripts. A native file-loaded bundle needs no socket address beyond its app/Bridge adapters.

The page and transport have separate lifetimes. Calls have the method table's deadlines and reject disconnected/no_answer without inferring mutation success. The renderer's send/Draft integration supplies a reload barrier: save its unsaved Drafts and wait for pending chat.send/exchange.sendAgain before a once-per-Build reload. Subscription replacement uses a fresh id and ignores old frames. A snapshot replaces that topic's projection, including the replay cursor; saved rows retain reasoning already shown until the next snapshot. A visibility check resubscribes missing or mismatching receipts; no content polling timer is added. Topic failures remain visible and can be retried explicitly; subscriptions ended for database_unavailable resume when database_unreachable closes.

Tool/lifecycle times are shown only when supplied by actual live events or saved run/Exchange metadata; missing times or durations are not fabricated. Saved tool rows contain no timestamps, and no Root schema or retained audit-file read is added to manufacture them. A window keeps timestamps it already observed until its next snapshot, as it keeps shown reasoning.

Markdown is parsed into typed text/element nodes, never inserted as raw HTML. Parsing failure or excessive nesting preserves the source as unformatted text rather than dropping content. Only http/https link targets become clickable; all link activation is canceled in-page and sent to the app adapter. Remote images and active HTML remain text. The development relay supplies a browser app-channel adapter: folder input, safe user-activated new-tab links and one consumption of the address's open request, without sending any app request to the backend. Native navigation/main-frame/folder-dialog delivery remains SYL-192.

### Composer implementation boundaries (BKD-D37)

The renderer keeps Draft revisions and baseRevision tokens exact throughout decoding, equality/CAS, local recovery and encoding. The pinned MIT lossless-json4.3.3 codec preserves unsafe integral revision/baseRevision tokens as JavaScript bigint and writes them as numeric JSON tokens; safe revisions and other numeric fields retain their current number representation. A quoted numeric string is not a revision. The backend's existing bigint wire format and1MiB/valid-Unicode/no-NUL Draft contract of BKD-D31 apply. The codec also formats bigint tool values without truncating them. Library provenance: [the published parser](https://github.com/josdejong/lossless-json), npm4.3.3 and its integrity-locked dependency entry.

Each Root/chat or Root/repository composition has a controller that outlives its visible field. Initial loading acquires a canonical Draft revision before the field is editable. One save owns its captured text/base revision; typing meanwhile stays in the editor, and an older save reply cannot acknowledge or replace later text. A matching own-text publication or draft_conflict is an acknowledgement without a prompt. A different current Draft, including a removed one, shows both versions and waits for Keep mine or Take theirs. A failed write retains the editor and retries after5seconds; normal typing debounces350ms. Switching contexts attempts a flush and retains an unresolved composition independently.

Unsaved text/revision and one unconfirmed send intent use session storage scoped to the Root and composition in that browser window. Reloads can offer text only over the same canonical revision; a newer canonical revision does not resurrect an old cached text. This storage isolates relay tabs. A send intent additionally retains its chat/Exchange UUIDs, route, folder and selected Draft revision so the exact call can be repeated; it is cleared on a definitive outcome. Ordinary saved transcript content is not written to this store.

The normal First Sapling composer has no Send or attachment buttons. Its controlled presentation emits actions; application controllers perform them, and design fixtures supply local fictional callbacks. While a send is unconfirmed that composition stays closed/read-only with its captured text retained, until acceptance or refusal; other compositions remain usable. The existing pre-reload barrier flushes Drafts and waits for unconfirmed sends. A stopped Exchange enables a queued message only after saved terminal data, even when exchange.stop already returned. Agent answers become visible as given only from their file line; a control reply alone is not that acknowledgement. Pasted-character counts use Unicode codepoints, matching the backend, and a queued send waits for every outstanding paste-save insertion.

While a long paste is being saved, its raw text remains in the controlled editor and unsaved-text recovery. Draft flushing waits for all pending paste operations, so it captures the resulting links. Edits outside a pending pasted range preserve that range through the edit. An overlapping edit is kept as typed and cancels the queued send rather than replacing those edits with an older file. A failed paste save reports the failure, retains the raw text and cancels a queued send. Repeated send shortcuts while files are pending queue one send after all successful insertions.

Route defaults are resolved only from configured routes and the public signed-in Subscription/model catalog. A configured model remains the configured choice even when an incomplete catalog does not list it. If neither configuration nor the catalog names a default model, the UI leaves the model unselected and explains that the Leather Bag can pick one with the model control; it does not invent a default. An explicit next-model action starts with the first catalog row when no current row matches. Settings writes for a chat are ordered, and an older reply/publication cannot replace a newer local choice; failures remain visible.

A click that moves an existing chat with Exchanges first shows the stated continuity consequence with Cancel and Change repository. The confirmation is tied to that Root/chat/context and is rechecked against the current working state before the settings call; a shortcut always starts the repository’s new-chat composition instead. A folder picker result is ignored if its originating context changed. The chat.settings reply is an empty acknowledgement; the chat subscription carries settings. A receipt can fill an unobserved local change but cannot erase settings published since the call started.

A send stores its exact Root/composition, method, identifiers, text/route/folder and Draft revision before dispatch; if that recovery record cannot be kept, it retains the Draft and does not start the send. One per-Root identifier remembers which unconfirmed send was visible, while other unconfirmed sends can finish independently. Recovery repeats the stored call or a valid backend Draft sentAs/sentRequest with the same identity. A provisional Exchange has no invented backend acceptance time. The reload barrier waits through its definitive receipt and view reconciliation. Before dispatch, changing composition cancels a queued paste/send or stop/send and leaves its text in the original Draft; after dispatch, changing composition does not cancel its receipt recovery. A stop/send queue waits for a saved terminal Exchange from the chat subscription, never the stop reply or a folder end line.

Question selections remain local until submitted. A successful exchange.answer reply keeps a waiting state; only a new answer file position confirms that submission, and ask_closed closes the question. A control_refused file position or a refused call keeps the question available for another valid choice. File positions distinguish a new submission’s receipt from an earlier answer already displayed. A malformed or future Ask is shown as literal data with no fabricated choice or free-text answer; Cancel can still decline its known askId. Closed questions with recorded answers remain readable, including the ask/answer data kept with a saved tool call.

### What First Sapling leaves out

Version 1's Elma had more than this first version. These parts are not in First Sapling:

| Part of version 1 | Why |
|---|---|
| Branches: the branch switcher, "Branch" mode, editing and removing a message, the remembered branch, the history's branch points, retrying or continuing an Exchange that is not the last | For a more advanced Root (the owner, 19 October 2026); the Root Contract has none (RCT-D21) |
| Images in a message, entity chips, Chat Notes, Quick Text, a title block in a message, tags | Not in First Sapling (the owner, 19 October 2026) |
| Approvals of tool calls | No agent asks for permission in Arbol 2 (DRV-3); dropped |
| Signing in from Elma or Seqoya Lab | The Driver's own command until Seqoya Lab has a page for it (the owner, 19 October 2026) |
| The settings of each Intelligence Provider, version 1's routes: its default model, which models and efforts it offers, the repositories where it may not be used, full permissions, fast mode | They come with SYL-191 (ARC-D22), as the owner agreed on 19 October 2026 |
| The Thread Inspector, the document panel, "What's wrong?", "Finalize", the search of a repository's documents on ⌘R | Each needs a specification of its own |
| Unread chats and read receipts | Willo Station shows them, in its own specification |
| Additional folders of a chat | Version 1 set them from the command line only (SYL-193) |

## Requirements

| ID | Elma Chat's first version must… | Origin | Verified by |
|---|---|---|---|
| BKD-2.1 | be one window for each Root, with no list of chats in it, belong to its Root and talk only to its backend, with the header "Elma Chat · <Root's display name> - <title>", the Root's state when it is not `working` and as it changes, a moving mark while the agent works, and the reading width, text size and theme | Changed | `tests/ui/frame.mjs` (Root/name/status changes, first-open priority/ghost fallback/Unicode title); `tests/ui/bridge.mjs` (native adapter protocol/lifecycle), `tests/ui/relay_browser.mjs` (real transport) (SYL-254; real Chromium/loopback HTTP-WebSocket/private Unix backend stand-in; native Swift host, installed Root/Trunk/vendor journeys remain SYL-192/SYL-257). |
| BKD-2.2 | have version 1's layout: the navigation panel with the title and "Turn n of N", the cockpit, "Repositories" and "Intelligence", open in an empty chat and closed once it has an Exchange, and the history; the chat; the status bar "<repository> – <Driver> · <Subscription> – <model>::<effort>"; and open on the chat it is asked to open, else the chat shown last, else the first repository's last chat, else an empty chat there | Kept | `tests/ui/frame.mjs`; shared `scripts/check-elma.mjs` (empty/first Exchange panels, controls, history/focus); `tests/ui/reading.mjs` and shared `scripts/check-elma-reading.mjs` (12 actual theme canvases, contrast, densities/narrow/scaling) (SYL-254; real Chromium/loopback HTTP-WebSocket/private Unix backend stand-in; native Swift host, installed Root/Trunk/vendor journeys remain SYL-192/SYL-257). |
| BKD-2.3 | show one Exchange at a time, its message pinned with "See more", "Copy prompt" and the stepper, step with ⌘[ and ⌘], open the history with ⌘P, leave out every replaced Exchange, bring a long chat 12 Exchanges at a time, and count every Exchange in "Turn n of N" | Kept | `tests/ui/navigation.mjs` (one Exchange/prompt/copy/expand, full unreplaced counts, shortcuts/history/digits/search, exact12 paging, stale reply rejection); `tests/ui/reading.mjs` (fresh paging restores older selection) (SYL-254; real Chromium/loopback HTTP-WebSocket/private Unix backend stand-in; native Swift host, installed Root/Trunk/vendor journeys remain SYL-192/SYL-257). |
| BKD-2.4 | show an answer with its lifecycle line, its reasoning open, its tool calls closed to one line with their mark and opened to their times, input and output, and, once complete, the Answer Threshold with "Copy answer", the Answer Beacon, the scroll rules and each chat's scroll position | Kept | `tests/ui/response.mjs`, shared `scripts/check-elma-response.mjs` (lifecycle, reasoning/tools, lazy whole details/error/retry, null/false, Markdown safety/copy/app links); `tests/ui/reading.mjs` and shared `scripts/check-elma-reading.mjs` (threshold/Beacon/three reading stops, tail/user release, in-memory offsets, snapshot/tool restoration) (SYL-254; real Chromium/loopback HTTP-WebSocket/private Unix backend stand-in; native Swift host, installed Root/Trunk/vendor journeys remain SYL-192/SYL-257). |
| BKD-2.5 | show an Exchange in progress from the first line of its `events.jsonl` on, as it arrives, however late the window was opened, and keep the reasoning it showed once the Exchange is saved until the chat is read again | Changed | `tests/ui/live.mjs`, `tests/ui/live_browser.mjs` (all line kinds, late replay, authoritative whole blocks, nested activity, usage totals, duplicate/unknown/oversized lines, saved reasoning/timing retention, snapshot reset, actual seq gap and reconnect) (SYL-254; real Chromium/loopback HTTP-WebSocket/private Unix backend stand-in; native Swift host, installed Root/Trunk/vendor journeys remain SYL-192/SYL-257). |
| BKD-2.6 | show one status label at a time in version 1's order, "Stopping…" right after "Failed", with what the Exchange waits for and for how long, such as "Waiting for tools… 2 h 10 min" or "Waiting for your answer since 14:02", and never end it for waiting | Changed | `tests/ui/live.mjs`, `tests/ui/live_browser.mjs` (exact status priorities, real wait timestamps, very long waits remain active, saved terminal boundary) (SYL-254; real Chromium/loopback HTTP-WebSocket/private Unix backend stand-in; native Swift host, installed Root/Trunk/vendor journeys remain SYL-192/SYL-257). |
| BKD-2.7 | keep version 1's composer: the empty chat's line and composer, the closed composer of a chat with Exchanges, opened when its Draft holds text, ⌘⏎ and ⌃⏎ to send, Return for a new line, Escape to close, and a paste of 10,000 characters or more saved in the Root's folder and replaced by the link `[Pasted text (n characters)](<path>)` | Changed | journey |
| BKD-2.8 | keep one Draft of the reply for each chat and one Draft of a new chat for each repository, saved 350 milliseconds after typing stops and at once on losing the focus or showing another chat, over the revision last seen; say when a save failed and try again; keep in the page only text not yet saved, offered back after a reload only while the Draft has the revision it was typed over; and show both texts on a conflict, taking without asking one that holds the composer's own text | Changed | journey, drill |
| BKD-2.9 | offer the route as one row for each Subscription of each Driver with ⌃1 to ⌃9, a Subscription that cannot be used marked and not pickable, the model with ⌃M and the effort with ⌃⇥ from the Subscription's catalog; save a choice for an existing chat at once for its next message, keep an empty chat's choice for its first message, and start a new chat with the first signed-in of the defaults of `arbol.json` and the catalog | Changed | journey |
| BKD-2.10 | offer the repositories of `readonly/` and the stack's own folder with ⌘1 to ⌘9 and "Other… ⌘0", start a new chat with a key, bringing back the repository's new-chat Draft, move the chat shown with a click, refused while its agent works, and say what moving a chat that has Exchanges costs | Changed | journey |
| BKD-2.11 | on sending, show the Exchange at once with "Starting agent…", mark the chat ongoing once it is accepted, put a refused message back in the composer with the refusal's cause, and send a call that got no reply again with the same Exchange identifier | Changed | journey, drill |
| BKD-2.12 | ask "Stop current response?" only while the backend says the chat's Exchange runs, and on "Confirm" stop it, wait until it is saved and send | Changed | journey |
| BKD-2.13 | on ⌘Esc, show "Stopping…" from the request until the Exchange has ended, then "Canceled" with "⏹ Stopped" only when its end says `cancelled`, and otherwise its true final state, and count an Exchange as ended only once it is saved | Changed | journey, drill |
| BKD-2.14 | show a failed Exchange with "Failed", its time and its cause in plain words with its code and message, a code it does not know with its message, "Retry" and "Continue from failure point" on the chat's last Exchange, Retry in the replaced Exchange's folder, and for `rate_limited` the time it resets | Changed | journey |
| BKD-2.15 | show the questions of the agent above the composer with their options, "Submit", "Continue" only when no question has options, and "Cancel" as a decline, no answer in free text, the answer only once its `answer` line is in `events.jsonl`, and the question kept after a `control_refused` | Changed | journey |
| BKD-2.16 | show an Exchange whose process is gone as interrupted, one that ended while the database was away from its folder marked "Not yet saved", and one the backend ended because it was stuck with "Ended because it was stuck" | New | drill Renderer projection/status: `tests/ui/live.mjs`, `tests/ui/live_browser.mjs`, shared Response Interrupted/NotSaved stories. (SYL-254; real Chromium/loopback HTTP-WebSocket/private Unix backend stand-in; native Swift host, installed Root/Trunk/vendor journeys remain SYL-192/SYL-257). Actual installed failure drill remains SYL-257. |
| BKD-2.17 | rename a chat with ⌘-click on its title or R, an empty title taking it away and a placeholder never stored; mark every chat with an accepted message ongoing and clear it with ⌥0; archive it with ⌘⌫ or A after a confirmation, stopping a running answer first and then showing an empty chat in its repository; and offer these as quick actions on ⇧⏎ | Changed | journey |
| BKD-2.18 | list the latest chats on ⌃⇧⌘C, at most 100 and none archived, without the chat shown, those shown in Elma first, each with its title, repository, route, state and age, digits opening the first ten, over the window until the Swift App has its panel | Changed | journey |
| BKD-2.19 | open the chat that the Swift App asks it to open, from Willo Station or elsewhere, taking a request made while it loaded, after saving the Draft of the chat it shows | Kept | journey; the Swift App's part with SYL-192 |
| BKD-2.20 | say on a Subscription that cannot be used, and on a failed Exchange whose account is not signed in, that it is not signed in and which command of its Driver signs it in, and take no code and no key | Changed | journey |
| BKD-2.21 | show every attention item of its Root across the top of the chat for as long as it lasts | New | drill |
| BKD-2.22 | when the backend goes away, say that it reconnects, keep showing the chat and taking text, and read everything again once it is back | Changed | drill |
| BKD-2.23 | be a renderer bundle in `ui/elma/` of the `arbol` Build, in TypeScript with Svelte 5 from the components of `arbol-design-system`, follow version 1 where they differ, reach nothing but the Bridge and the app channel, never leave its own page, open an `http` or `https` link only through `app.openLink`, and keep in the page's own storage only the conveniences of version 1 and text not yet saved | Kept | `ui/elma` check/build, `tools/sync_elma_design.py --check`, `tests/ui/test_bundle.py` (`elma.package-relocation`, `elma.package-identity`, `elma.package-hashes`, `elma.package-csp`, `elma.package-fonts`, `elma.package-paths`), `tests/ui/test_relay.py`, `tests/ui/relay_browser.mjs`; private numbered image/packaged Python/relay/browser and113-file independent payload reproducibility; paired maintained design check/build/catalog/affected browser checks (SYL-254; real Chromium/loopback HTTP-WebSocket/private Unix backend stand-in; native Swift host, installed Root/Trunk/vendor journeys remain SYL-192/SYL-257). |
| BKD-2.24 | show truthful stale-copy metadata and a Bring over again action, save the Draft, call reimport once and open its actual result chat while retaining divergent content, and expose comparison/ambiguous-result failures without automatic retry | New | pending Backend Arc SYL-256/SYL-257; Root core is SYL-195 |

## Interface

The window uses the calls and topics of [BKD-1](01-the-bridge.md#interface) and the app channel's `app.pickFolder`, `app.openLink` and `app.takeOpen`. Its keys, as in version 1:

| Key | Does |
|---|---|
| ⌘⏎, ⌃⏎ | Sends |
| Return | A new line; opens a closed composer |
| Escape | Closes the composer, a panel or the history |
| ⌘Esc | Stops the Exchange in progress |
| ⌘[, ⌘] | The older and the newer Exchange |
| ⌘P | The history |
| ⇧⏎ | The quick actions |
| ⌘⌫ | Archives the chat, after a confirmation |
| ⌥0 | Ongoing, or not |
| ⌘1 to ⌘9, ⌘0 | A new chat in that repository; "Other…" |
| ⌃1 to ⌃9 | The route |
| ⌃M, ⌃⇥ | The next model, the next effort |
| ⌘⇧⌥8, ⌘⇧⌥7 | The previous and the next reading stop |
| ⌃⇧⌘C | The latest chats |

## Known problems in version 1

Not to be reproduced.

- **"Stopped" before anything had stopped.** The window showed the stop at once and ignored a failed cancel; a stopped answer opened again looked completed, because nothing marked it.
- **Text missing in a late window.** A window opened while an answer was arriving missed the text not yet sealed.
- **Drafts with several owners.** A copy in the page's storage and the saved Draft could disagree, windows overwrote each other's Drafts, a late "clear" could delete newer text, and a save that failed was never shown.
- **"Stop current response?" on an idle chat.** The window and the coordinator disagreed on whether the chat ran.
- **A placeholder stored as the title.** The window stored "Elma · <repository>" as the title, so no title was ever made for chats started there.
- **A window that stopped listening.** After its first local change, the window stopped rebuilding the chat from the backend, so changes made elsewhere showed only when the chat was opened again.
- **Two chats in one checkout.** Every chat on a repository worked in its one checkout, so two agents changed the same files.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/03-turn-execution.md#Known problems and lessons`
- `arbol_deprecated_v1:product-spec/03-turn-execution.md#Cancel`
- `arbol_deprecated_v1:product-spec/04-composer-drafts-and-branching.md#Known problems and lessons`
- `arbol_deprecated_v1:product-spec/12-lessons-and-invariants.md#9. A draft had more than one owner`
- `arbol_deprecated_v1:product-spec/02-chat-sessions.md#Known problems and lessons`
- `arbol_deprecated_v1:product-spec/02-chat-sessions.md#Finding sessions: lists, ordering and grouping`
- `arbol_deprecated_v1:product-spec/04-composer-drafts-and-branching.md#Moving around inside a chat`
- `arbol_deprecated_v1:product-spec/05-intelligence-providers.md#The IP of a new chat`
- `arbol_deprecated_v1:product-spec/07-agent-context.md#Repo slots and choosing a repo in Elma`
- `arbol_deprecated_v1:product-spec/07-agent-context.md#Working Directory and additional directories`
- `arbol_deprecated_v1:renderer/apps/elma/src/App.svelte#stopAgent`
- `arbol_deprecated_v1:renderer/apps/elma/src/nav/NavigationPanel.svelte`
- `arbol_deprecated_v1:renderer/apps/elma/src/chat/largeTextPaste.ts`

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| BKD-D17 | Where does the Leather Bag sign in, in the first thin path, the first version that goes once through every part (ARC-1)? | In Elma Chat's window: a panel opened from a Subscription that cannot be used and from a failed Exchange, which shows the Driver's sign-in steps. The alternative: no sign-in in the window, and signing in at the terminal | Decided 19 October 2026 by the owner: "Before Seqoya Secrets page is implemented we can use Driver own authentication flow", made exact the same day: "I meant signing in using driver cli command." The Leather Bag signs in with the Driver's own command, such as `arbol-claude-driver subscriptions sign-in zai`; the window names it and takes no code or key |
| BKD-D18 | In what is the window written? | TypeScript with Svelte 5, as version 1's Elma was, from the components and pages of `arbol-design-system`; where they differ from version 1, the window follows version 1 and the design system is brought in line. The alternative: another framework, which would rebuild those components | Decided 19 October 2026, a technical choice following BKD-D22 |
| BKD-D19 | What does a chat without a title show? | The first line of its first message, at most 80 characters, in a lighter type, never stored, because a stored placeholder kept titles from being made in version 1 and RCT-3 forbids it. The Trivial Trunk makes no titles (TRV-0), so every chat of the first thin path shows it until it is renamed | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D20 | Is the reasoning of the model shown? | Yes, open, as version 1 showed it. The chat tables keep none (RCT-3), so the window keeps what it showed until the chat is read again, and an Exchange read from the database has none | Decided 19 October 2026, a technical choice following BKD-D22 |
| BKD-D21 | When is a Draft saved, and what if it is saved from two connections? | As version 1: 350 milliseconds after typing stops, and at once when the composer loses the focus or another chat is shown. Changed: a failed save is said and tried again every 5 seconds; each save names the revision it was made over, and a conflict shows both texts with "Keep mine" and "Take theirs"; the page keeps only text not yet saved, offered back after a reload only while the Draft still has the revision it was typed over, so the backend stays the Draft's one owner. Version 1 kept a whole copy in the page, which made a second owner | Decided 19 October 2026, a technical choice following BKD-D22 |
| BKD-D22 | What can the first version of Elma Chat do? | One kind of window with the chats of its Root on the left and one chat on the right, in which you start a chat, send, see the answer arrive, answer the agent's questions, stop, send again, rename, sign in and open a chat again later | Decided 19 October 2026 by the owner: "UX/UI should be the same as in deprecated version of Arbol." The first version has version 1's layout, navigation, keys, pickers, states and wording, with the changes Arbol 2 needs, each said where it stands; it has no list of chats in the window. The same day the owner settled what First Sapling leaves out: branches, editing and removing go to a more advanced Root; images, entity chips, Chat Notes, Quick Text and tags are not in First Sapling; and opening a chat from Willo Station is needed |
| BKD-D35 | How are independent packaging, shared design provenance, renderer recovery and safe content made concrete? | The Renderer implementation boundaries above: hashed successor-source snapshot, pinned local bundle/fonts/CSP, independent call/subscription lifetimes and safe typed Markdown; browser-only app adapter with no backend forwarding | Decided27 October2026, technical choice in SYL-254; composer255/actions256 and native192 keep their named scope |
| BKD-D37 | How does the composer keep exact Draft ownership, local recovery and uncertain sends through browser lifetimes? | The composer boundaries above: pinned exact numeric revision codec, revision-fenced single-save controllers, per-window unsaved/intent storage and backend/file-confirmed outcomes | Decided27 October2026, technical choice in SYL-255 before code; existing Draft/send wire methods remain the authority |
