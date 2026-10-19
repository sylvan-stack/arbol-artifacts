---
role: authored
spec: BKD-2
status: review
---
# Arbol backend · 02 Elma Chat, its first version

[Elma Chat](../GLOSSARY.md#elma-chat) is the [UI](../GLOSSARY.md#ui) in which the [Leather Bag](../GLOSSARY.md#leather-bag) talks with an agent. Its first version in Arbol 2 looks and works as Elma Chat of version 1 did ([BKD-D22](#decisions)): one window with a navigation panel on the left, the chat on the right showing one [Chat Exchange](../GLOSSARY.md#chat-exchange) at a time (*Exchange* for short: one message of the Leather Bag and the agent's answer to it), the composer below it, and a status bar at the bottom. For example, the Leather Bag presses ⌘1 to start a chat in the first repository, types "What does build.sh do?" and presses ⌘⏎: the message is pinned at the top, "Starting agent…" turns into the answer arriving word by word, the agent's `cat build.sh` shows as one closed line, and once the answer is complete the tool calls stand above a line, the *Answer Threshold*, and the answer below it. The next day ⌃⇧⌘C lists the chat among the latest, and Return opens it again. This specification states what the window shows and does, which parts of version 1 it keeps, which it changes because Arbol 2 works differently, and which come later. The backend it talks to is [BKD-0](00-the-arbol-backend.md), and the messages they exchange are [BKD-1](01-the-bridge.md). It matters because the owner decided that the window keeps version 1's form, and because version 1 showed "Stopped" before anything had stopped, lost the text still arriving in a window opened late, and let Drafts be overwritten by another window.

It follows the conventions of the [Driver Contract](../driver-contract/README.md#conventions) and the additions in this chapter's [README](README.md#conventions). *Observed* below means version 1's Elma Chat as its product specification and its renderer describe it; where nothing else is said, the first version keeps it.

## Scope

Covered: the window, the navigation panel, the chat and the Exchange shown, the answer as it arrives, the status of an Exchange, the composer and Drafts, the pickers of the route, the repositories, sending and stopping, questions of the agent, a failed Exchange, the chat's own actions, the latest chats, attention, coming back, signing in, the renderer bundle, and what comes later.

Not covered: the tray menu, the global hotkeys and the native panel of the latest chats, which are the Swift App's (SYL-192); Willo Station and Seqoya Lab; which folder on disk a repository gives the agent, which waits for the owner ([BKD-D4](00-the-arbol-backend.md#decisions)); marking a migrated chat stale (SYL-195).

## Behaviour

### The window

Observed in version 1: one Elma window, which closing did not quit. The first version keeps one Elma Chat window for each Root, opened from the tray menu (SYL-192).

```text
┌ ✦ Elma Chat · First Sapling - What build.sh does ──────────────────────── ↔  A+ A− ┐
│ What build.sh does           │ What does build.sh do?                        ‹ 2/3 › │
│ Turn 2 of 3                  │ ───────────────────────────────────────────────────── │
│ ○ Ongoing   ∑ 11.8k  ↑9.1k ↓2.7k │ Message sent 09:30 · Agent started responding 09:30 · │
│ Repositories                 │ Agent responded 09:30                                 │
│  ⌘1 shop                     │ ▸ shell  cat build.sh                             ✓   │
│  ⌘2 arbol-trunk              │ ─────────────────── Answer ───────────────────────── │
│  ⌘0 Other…                   │ It compiles the three packages and copies them to     │
│ History · 3 turns            │ dist/.                                     Completed  │
│  Older ⌘[  Newer ⌘]  Jump ⌘P │                                                       │
│ Intelligence                 │ Press Enter to start new message ⏎                    │
│  Model: sonnet ⌃M            │                                                       │
│  Thinking: high ⌃⇥           │                                                       │
│  ⌃1 claude · anthropic       │                                                       │
│  ⌃2 codex · chatgpt          │                                                       │
├──────────────────────────────┴───────────────────────────────────────────────────────┤
│ shop – claude · anthropic – sonnet::high                                             │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

| Part | What it shows |
|---|---|
| The header | The Elma glyph and "Elma Chat · <Root's display name> - <the chat's title>", or without the title for a chat that has none. The Root's display name is the one addition to version 1, because every UI shows its Root ([ARC-1](../architecture/01-roots.md#the-tray-menu-and-arbol-roots)); a Root that is not `working` says so beside it, "preparing", or "failed" with its reason. A moving mark while the agent works. On the right, the reading width and the font size (A+, A−) |
| The navigation panel | On the left, top to bottom: the chat's title, or "New Chat", and "Turn n of N"; the chat's own panel, *the cockpit*, once the chat exists; "Repositories"; "History · N turns"; "Intelligence" ([below](#the-navigation-panel)) |
| The chat | On the right: the pinned message, the answer, the questions of the agent above the composer, and the composer ([below](#the-exchange-shown)) |
| The status bar | At the bottom: "<repository> – <Driver> · <Subscription> – <model>::<effort>", such as "shop – claude · anthropic – sonnet::high" |
| Attention | A line across the top of the chat for each attention item of the Root ([below](#attention)) |

The window shows what the backend says. Of its own it keeps, in the page's own storage, only conveniences: the chat shown last, the chat last shown for each repository, and the 16 repositories used last. A Draft is never kept there ([BKD-D21](#decisions)).

**On opening**, the window shows, in this order of what exists: the chat it is told to open, the chat shown last, the chat last shown in the first repository of the slots, and else an empty chat in that repository with its new-chat Draft.

### The navigation panel

| Part | What it holds |
|---|---|
| The title | The chat's title, or the placeholder of a chat without one ([below](#the-chats-own-actions)), and "Turn n of N": the place of the Exchange shown among the chat's Exchanges |
| The cockpit | Once the chat exists: the pill "Ongoing" or "Not ongoing", which ⌥0 changes; and the tokens of the chat, ∑ in all, and in and out, with the rate at which they grow while the agent works |
| Repositories | The slots ⌘1 to ⌘9 and "Other… ⌘0" ([below](#the-repositories)) |
| History | "Older ⌘[", "Newer ⌘]" and "Jump to turn… ⌘P" when the chat has more than one Exchange, and "Quick actions… ⇧⏎" |
| Intelligence | "Model: <model> ⌃M" and "Thinking: <effort> ⌃⇥", and one row for each route, ⌃1 to ⌃9 ([below](#the-route)) |

### The Exchange shown

The chat shows one Exchange at a time: its message pinned at the top, and its answer below it. A chat opens on its newest Exchange.

| Part | Detail |
|---|---|
| The pinned message | The Leather Bag's message, at most three lines, with "See more"; "Copy prompt"; and, when the chat has more than one Exchange, the stepper "‹ 2/3 ›" |
| Moving | Older ⌘[ and Newer ⌘] step through the chat's Exchanges in the order of their numbers, leaving out every Exchange a message sent again replaced (RCT-3). The counter, and ⌘P, open the history: the chat's messages, newest first, where digits jump to one and "Search" finds a word in the messages |
| More of a long chat | A chat opens with its 12 newest Exchanges; stepping older than the first of them brings the 12 before (`chat.exchanges`, BKD-1) |

The answer, top to bottom:

| Part | Detail |
|---|---|
| The lifecycle line | "Message sent · Agent started responding · Agent responded", each with its time; times within 3 seconds of each other share a line |
| Thinking | Each block of the model's reasoning, "Thinking 1/2", open, while the answer arrives. The chat tables keep no reasoning (RCT-3), so an Exchange shown again from the database has none ([BKD-D20](#decisions)) |
| A tool call | One closed line: the tool's name, a mark (… running, ✓ done, ! failed, interrupted), and one line of what it did, such as the command of `shell` or the path of `Read`. Opened: when it started and ended, how long it took, its input, and its output; a running call shows its time after 60 seconds; an output the Driver cut says so (DRV-2); in a long chat, an input or output that was cut for the Bridge loads whole when opened (`toolCall.get`, BKD-1) |
| The Answer Threshold | Once the Exchange is complete: every block of reasoning and every tool call above a line, and the answer's text below it, as Markdown. While the Exchange runs, there is no line and everything stands in the order it came |
| The status | The status of the Exchange ([below](#the-status-of-an-exchange)), and "Copy answer", which copies the text below the threshold |

Markdown in an answer shows headings, lists, emphasis, links, tables and code blocks. Raw HTML in it is shown as text, never run. A link opens in the Mac's default browser through the Swift App (`app.openLink`, BKD-1), and only when it is `http` or `https`; any other link is shown as text, and the window never leaves its own page.

**Scrolling.** An answer that arrives keeps its end in view until the Leather Bag scrolls up. A complete answer opens with the threshold at the top of the view, and while the threshold lies below the view, a small *Answer Beacon* points to it. ⌘⇧⌥8 and ⌘⇧⌥7 jump to the previous and the next reading stop.

**Observed in version 1, and kept**: one Exchange at a time, the pinned message and its stepper, the history on ⌘P, pages of 12 Exchanges, the lifecycle line, reasoning open, tool calls closed, the Answer Threshold, the Answer Beacon and the scroll rules.

### The answer as it arrives

While an Exchange is in progress, the window shows the lines of its `events.jsonl` as they come, from the first one on, in every window that shows it, however late the window was opened ([BKD-1](01-the-bridge.md#subscriptions), ARC-2). It reads them by the Driver's events ([DRV-2](../driver-contract/02-inference.md#the-event-stream)):

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

### The status of an Exchange

One label at a time, the first that holds of these, as version 1 had them:

| The Exchange | Label |
|---|---|
| failed | "Failed" ([below](#a-failed-exchange)) |
| waits for the Leather Bag's answer | "Waiting for your answer since 14:02" |
| accepted, before the run's `started` event | "Starting agent…" |
| runs a tool call | "Waiting for tools… 2 h 10 min", the time since it waits, from its signs of life (ARC-3) |
| writes reasoning | "Thinking…" |
| writes the answer | "Responding…" |
| any other moment of the run | "<Driver> · <Subscription> is working…" |
| is being stopped | "Stopping…" |
| has ended | "Completed", "Canceled", "Interrupted", or "Ended because it was stuck" |

Arbol never ends an Exchange for waiting, however long it waits (ARC-D61): the Leather Bag stops it when that is wanted. The Trivial Trunk itself ends a run that gives no event for 16 minutes while a command left in the background runs, as failed with `driver_silent` (TRV-0, RCT-D30).

Changed from version 1: there is no label "Routing to …" and no waiting for a rate limit to pass, because a Trunk takes the route it is handed and ends an Exchange that met a rate limit as failed (ARC-2); and there is no waiting for an approval, because no agent asks for permission (DRV-3).

| Changed state | The window says |
|---|---|
| `interrupted` | "Interrupted: the agent's process ended before the answer was finished. What had arrived is kept." |
| `interrupted`, with the note `ended_stuck` | "Ended because it was stuck. What had arrived is kept." ([ARC-3](../architecture/03-stuck-trunks.md#ending-a-stuck-exchange)) |
| `unsaved` | The answer from its folder, marked "Not yet saved", until the backend has had it settled ([ARC-D53](../architecture/02-chat-exchange-across-components.md#decisions)) |
| `gone` | "Interrupted", until it is settled and then as saved ([ARC-2](../architecture/02-chat-exchange-across-components.md#an-exchange-whose-process-is-gone)) |

### The composer

The composer is the field below the answer in which the next message is typed.

| Part | Detail |
|---|---|
| An empty chat | A line "<repository> · <Driver> · <Subscription> · <model> · <effort>", then the composer of at least 10 lines, in the middle, with "Message <repository>…" and the hint "⌘⏎ to Send". There are no buttons |
| A chat with Exchanges | The composer is closed to the line "Press Enter to start new message ⏎", with "Scroll to top" and "Scroll to bottom"; Return opens it, at least 3 lines, and Escape closes it again |
| Keys | ⌘⏎ or ⌃⏎ sends; Return makes a new line; Escape closes the composer |
| A long paste | Text of 10,000 characters or more that is pasted is saved as a file in the Root's folder `pastes/` and replaced in the message by the file's path (`paste.save`, BKD-1), so that the agent reads it from there |

**Drafts.** Observed in version 1, and kept: each chat has one Draft of its reply, and each repository has one Draft of a new chat. A Draft holds the text; the pickers are the chat's own settings ([below](#the-route)). The window saves the Draft 350 milliseconds after the Leather Bag stops typing, and at once when the composer loses the focus or another chat is shown (`draft.save`), each time over the revision it last saw ([BKD-0](00-the-arbol-backend.md#drafts)). Changed from version 1:

| | |
|---|---|
| A failed save | Is said below the composer, "Draft not saved: the database does not answer", and the window tries again every 5 seconds while it keeps the text |
| Another window | When another window saved a newer Draft of the same chat, this window takes it at once while its own composer holds nothing unsaved; otherwise its next save is refused with `draft_conflict`, and the composer shows both texts, "Changed in another window", with "Keep mine" and "Take theirs" |
| No second copy | The page keeps no copy of a Draft in its own storage, so a Draft has one owner, the backend |

### The route

The *route* is what answers a message: a Driver with one of its Subscriptions, a model and an effort, such as `claude · anthropic · sonnet · high`. Elma Chat uses no Brain Recipe: the route is the Leather Bag's choice, or a default ([BKD-D3](00-the-arbol-backend.md#decisions)).

| Picker | Keys | What it offers |
|---|---|---|
| The route rows | ⌃1 to ⌃9 | One row for each Subscription of each Driver, such as "claude · anthropic" and "codex · chatgpt" (`accounts.list`). A Subscription that cannot be used is shown with its state, "signed out" or "needs attention", and "Sign in…" ([below](#signing-in)); it cannot be picked |
| Model | ⌃M | Goes to the next model of the Subscription's catalog (`accounts.models`, DRV-1) |
| Thinking | ⌃⇥ | Goes to the next effort the model accepts, in the vendor's words (DRV-1) |

A choice is saved for the chat at once (`chat.settings`, BKD-1), counts from the next message on, and may be made while the agent works. Picking another route sets the model and the effort to that route's defaults.

The defaults of a new chat, in this order of what exists ([BKD-0](00-the-arbol-backend.md#settings)):

| | Default |
|---|---|
| The route | The default route of the chat's repository in `arbol.json`, else the default route of `arbol.json`, else the first signed-in Subscription of the first Driver |
| The model | The model the route names, else the catalog's default model (DRV-1) |
| The effort | The effort the route names, else the model's default effort, else `high` where the model accepts it |

Observed in version 1, and changed: version 1 picked an Intelligence Provider, a named route that Seqoya Lab bound to a Subscription, with seven thinking levels of its own. Arbol 2 has no Intelligence Provider yet ([ARC-D22](../architecture/00-components-and-boundaries.md#decisions)), so a row is a Subscription, and the efforts are those the vendor names for the model.

### The repositories

Observed in version 1, and kept: the slots ⌘1 to ⌘9 offer repositories, and "Other… ⌘0" opens the Mac's folder dialog (`app.pickFolder`, BKD-1). A key always starts a new chat in that repository, with the repository's new-chat Draft. A click on a slot while a chat is shown moves that chat to the repository, which is refused while its agent works ("Wait for the current turn to finish before changing Repo") and confirmed with "Repo changed to …"; a click with no chat shown is the same as the key. Changing the repository of a chat that has Exchanges says "The agent still gets every message of this chat, but no longer remembers what it read and ran before", because a Driver continues its saved conversation only in the same folder and otherwise builds it anew from the chat (TRV-0).

Which repositories the slots list, in which order, and which folder on disk a repository gives the agent, now that agents work at once in prepared folders, waits for the owner ([BKD-D4](00-the-arbol-backend.md#decisions)).

### Sending and stopping

**Sending.** ⌘⏎ sends the message with the chat's route and folder (`chat.send`, BKD-1). The new Exchange appears at once, its message pinned and "Starting agent…" below it, and the composer closes. Then:

| The backend replies | The window |
|---|---|
| Accepted | Follows the Exchange as it arrives |
| Refused | Takes the Exchange out, puts the text back in the composer as it was, and says why below the composer, such as "Not sent: the database does not answer" ([ARC-2](../architecture/02-chat-exchange-across-components.md#the-steps)) |
| `disconnected` or `no_answer` | Keeps the Exchange as being sent, and sends the same call again, with the same Exchange identifier, at once or once the backend is back, so that the message runs once (BKD-1) |

**A chat that is busy.** Observed in version 1, and kept: sending while the chat's last Exchange runs asks "Stop current response?"; "Confirm" stops it, waits until it is saved, and then sends (ARC-D54). The question comes only when the backend says that the Exchange runs, never on a chat whose Exchange has ended. A message the Trunk refuses with `chat_busy`, because another window sent one at the same moment, goes back into the composer with "Another message of this chat is running".

**Stopping.** ⌘Esc stops the Exchange in progress (`exchange.stop`). Changed from version 1: from that moment until it has ended, the Exchange shows "Stopping…", in every window that shows it, and "Canceled", with the line "⏹ Stopped", only once its end says `cancelled` ([ARC-3](../architecture/03-stuck-trunks.md#a-stop-that-is-not-obeyed), RCT-2). When the Root manager had to end it by force, it shows "Interrupted"; when it had ended otherwise before the stop reached it, that state. A stopped Exchange shown again later is still "Canceled", because its end is kept.

The window counts an Exchange as ended, for sending, "Retry" and "Continue from failure point", only once it is saved (BKD-1).

### Questions of the agent

Observed in version 1, and kept: the questions of the agent stand above the composer, each with its header, its text and its options, one choice or several ("You can pick more than one"). "Submit" can be pressed once every question that has options has a choice; a question without options shows "Continue". There is no answer in free text. "Cancel" declines, which ends the run as cancelled (DRV-3). The window shows the answer as given once its `answer` line is in the file (`exchange.answer`), and the question closed at `ask_closed`; an answer the Driver did not take shows its `control_refused` message, and the question stays.

### A failed Exchange

Observed in version 1, and kept: a failed Exchange shows "Failed", "Failed at: <time>", "Error: <cause>" and, at the end, "⚠︎ <cause>", with two buttons, "Retry" and "Continue from failure point".

| | |
|---|---|
| The cause | In plain words, with the code and the message of the error below it, so that nothing of the cause is lost; a code the window does not know is shown with its message ([RCT-2](../../arbol-root/contract/02-starting-stopping-and-settling.md#the-end)) |
| Retry | Sends the message again in its place: the answer is replaced and changes the agent made to files stay (`exchange.sendAgain`, RCT-2). Only the chat's last Exchange can be sent again; a failed Exchange that is not the last shows no "Retry" |
| Continue from failure point | Sends "proceed" as the chat's next message, with the chat's route |
| `rate_limited` | "The account reached its limit", and with `retryAfterSeconds` "It resets at 15:30". "Retry" goes with the route the rows show, so another route can be picked first ([ARC-2](../architecture/02-chat-exchange-across-components.md#a-rate-limit)) |
| `not_signed_in`, `credential_rejected` | "The account is not signed in", with "Sign in…" ([below](#signing-in)) |

| Code | In plain words |
|---|---|
| `context_exceeded` | "The chat is too long for this model" |
| `driver_failed` | "The Driver could not run" |
| `driver_silent` | "The Driver stopped answering" |
| `events_file_full` | "The answer grew too large" |
| `database_unavailable` | "The database did not answer" |
| `folder_unwritable` | "The Exchange's folder could not be written" |
| `trunk_failed` | "The Trunk failed" |

Changed from version 1: "Retry" replaced the failed Exchange and everything below it, wherever it stood; in Arbol 2 only the last Exchange can be sent again, until a Root Contract version brings branches (RCT-D21).

### The chat's own actions

| Action | Keys | Detail |
|---|---|---|
| Rename | ⌘-click the title in the header, or the quick action R | An inline field with "OK" and "Cancel" (`chat.rename`). An empty title takes the title away. A title has at most 240 characters. A chat without a title shows the first line of its first message, at most 80 characters, in a lighter type, and that text is never stored as a title ([BKD-D19](#decisions)) |
| Ongoing | ⌥0, or the pill in the cockpit | Marks the chat as one the Leather Bag is still busy with, or not (`chat.mark`) |
| Archive | ⌘⌫, or the quick action A | After a confirmation that says a running answer is stopped first: stops it, then archives the chat, which leaves the latest chats. Nothing archives a chat by itself, and no chat is deleted (`chat.mark`) |
| Copy the chat's identifier | The quick action C | |
| Quick actions | ⇧⏎ | A small list of the actions above, each with its letter |

### The latest chats

Observed in version 1, and kept: ⌃⇧⌘C shows the latest chats, at most 100, without the chat that is shown: first the chats shown in this window, the last shown first, then the others by their latest activity. Each row has the title, the repository, the route, the state of the last Exchange and how long ago. Digits 1 to 0 open the first ten, the arrows and Return any, and Escape closes the list (the `chats` topic, BKD-1). In version 1 the list was a panel of the native shell, and in Arbol 2 it is the Swift App's (SYL-192); until it exists, the window shows the same list over itself, with the same keys.

### Signing in

A route row of a Subscription that cannot be used, and a failed Exchange whose account is not signed in, offer "Sign in…". It opens a small panel that shows the Driver's own sign-in steps as they come (`signIn.start`, BKD-1; [BKD-D17](#decisions)):

| Step | The panel |
|---|---|
| `open_url` | The address and, when the step has one, the code to type on the vendor's page; the address opens through the Swift App in a window that refuses every other host (`app.openSignIn`, BKD-1). It says when the attempt expires |
| `enter_code` | A field for the code the vendor showed, with the step's prompt |
| `store_secret` | Until the Secrets page of Seqoya Lab exists, a concealed field for the key, with the step's prompt (`signIn.storeSecret`, [BKD-D10](00-the-arbol-backend.md#decisions)). The key is sent once, and the field is emptied at once |
| `done` | "Signed in", and the row can be picked |
| `failed` | The error, with "Try again" |

"Cancel" ends the attempt (`signIn.cancel`); the backend also ends it by itself 30 seconds after the window's connection closed, and a window shown again finds the attempt where it was (BKD-0). Version 1 signed in on the Subscriptions page of Seqoya Lab; when Seqoya Lab has that page, the panel can move there.

### Attention

Every attention item of the Root is a line across the top of the chat for as long as it lasts, with its message: a warning in the colour of warnings, an urgent one in the colour of errors ([BKD-1](01-the-bridge.md#attention)). For example, while the database server is away: "The database server does not answer at 127.0.0.1:5433. New messages cannot be sent; answers in progress go on." ([ARC-D53](../architecture/02-chat-exchange-across-components.md#decisions)). Version 1's Elma had no such line; a database that does not answer is not a normal state, and Arbol says so.

### Coming back

| When | The window shows |
|---|---|
| A chat opened again later | The chat as the chat tables hold it. An Exchange that is still in progress is followed from its first line on, so the whole answer so far is there ([ARC-2](../architecture/02-chat-exchange-across-components.md#the-arriving-answer-is-a-file)) |
| The same chat in two windows, such as Elma Chat of the same Root opened again | The same chat in both, with the answer arriving in both |
| The backend goes away | A line "Reconnecting…" across the top. The chat stays as it was shown, the composer still takes text, and when the backend is back the window reads everything again and saves the Draft (BKD-1) |
| The database cannot be reached | The attention line. The chat shown stays shown, a chat that is opened says that it cannot be read now, a message is refused with its cause and stays in the composer, and answers in progress keep arriving |

### Its renderer bundle

Each window shows a page loaded from Elma Chat's *renderer bundle*, the files built from the folder `ui/elma/` of the `arbol` repository into `ui/elma/` of each `arbol` Build, where the Swift App loads them ([BKD-0](00-the-arbol-backend.md#its-program-and-its-build)). It is written in TypeScript with Svelte 5, as version 1's Elma was, from the components of the Arbol design system, the repository `arbol-design-system`, and its pages `elma-new-chat`, `elma-conversation` and `elma-history`. Where a component of the design system differs from version 1, such as a "Send" button, an answer in free text, reasoning shown closed, or another stepper, the window follows version 1, and the design system is brought in line with it, as its own rules ask ([BKD-D18](#decisions)). The bundle holds everything it needs, fonts included, and reaches nothing but the Bridge and the app channel: its content security policy allows no other address.

### What comes later

Version 1's Elma had more than this first version. These parts come later, each for the reason given:

| Part of version 1 | Why later |
|---|---|
| Branches: the branch switcher, "Branch" mode, editing and removing a message, the remembered branch, the history's branch points | The Root Contract has no branches or edited messages yet (RCT-D21) |
| Images in a message | A message of the Root Contract is text (RCT-0) |
| Approvals of tool calls | No agent asks for permission in Arbol 2 (DRV-3); dropped, not later |
| Entity chips, Chat Notes, Quick Text, a title block in a message, tags | Each needs a specification of its own |
| The Thread Inspector, the document panel, "What's wrong?", "Finalize" | Each needs a specification of its own |
| Opening a chat from Willo Station, its Draft cards and its search | Willo Station |
| The routes' settings: default and allowed models and efforts, repositories where a route is not allowed, fast mode | Seqoya Lab and the Intelligence Providers (ARC-D22) |
| Additional folders of a chat | Version 1 set them from the command line only (SYL-193) |

## Requirements

| ID | Elma Chat's first version must… | Origin | Verified by |
|---|---|---|---|
| BKD-2.1 | be one window for each Root, belong to its Root and talk only to its backend, with the header "Elma Chat · <Root's display name> - <title>", the Root's state when it is not `working`, a moving mark while the agent works, and the reading width and font size | Changed | journey |
| BKD-2.2 | have version 1's layout: the navigation panel with the title and "Turn n of N", the cockpit, the repositories, the history and the intelligence; the chat; the status bar "<repository> – <Driver> · <Subscription> – <model>::<effort>"; and open on the chat it is told to open, else the chat shown last, else the first repository's last chat, else an empty chat there | Kept | journey |
| BKD-2.3 | show one Exchange at a time, its message pinned with "See more", "Copy prompt" and the stepper, step with ⌘[ and ⌘], open the history with ⌘P, leave out every replaced Exchange, and bring a long chat 12 Exchanges at a time | Kept | journey |
| BKD-2.4 | show an answer with its lifecycle line, its reasoning open while it arrives, its tool calls closed to one line with their mark and opened to their times, input and output, and, once complete, the Answer Threshold with "Copy answer", the Answer Beacon and the scroll rules | Kept | journey |
| BKD-2.5 | show an Exchange in progress from the first line of its `events.jsonl` on, as it arrives, in every window that shows its chat, however late the window was opened | Changed | journey, drill |
| BKD-2.6 | show one status label at a time in version 1's order, with what the Exchange waits for and for how long, such as "Waiting for tools… 2 h 10 min" or "Waiting for your answer since 14:02", and never end it for waiting | Changed | journey |
| BKD-2.7 | keep version 1's composer: the empty chat's line and composer, the closed composer of a chat with Exchanges, ⌘⏎ and ⌃⏎ to send, Return for a new line, Escape to close, and a paste of 10,000 characters or more saved as a file whose path takes its place | Kept | journey |
| BKD-2.8 | keep one Draft of the reply for each chat and one Draft of a new chat for each repository, saved 350 milliseconds after typing stops and at once on losing the focus or showing another chat, over the revision last seen; say when a save failed and try again; show both texts when another window saved meanwhile; and keep no copy of a Draft in the page's own storage | Changed | journey, drill |
| BKD-2.9 | offer the route as one row for each Subscription of each Driver with ⌃1 to ⌃9, a Subscription that cannot be used marked and offered only for signing in, the model with ⌃M and the effort with ⌃⇥ from the Subscription's catalog, save a choice for the chat at once for the next message, and start a new chat with the defaults of `arbol.json` and the catalog | Changed | journey |
| BKD-2.10 | offer the repositories with ⌘1 to ⌘9 and "Other… ⌘0", start a new chat with a key, move the chat shown with a click, refused while its agent works, and say what moving a chat that has Exchanges costs | Kept | journey |
| BKD-2.11 | on sending, show the Exchange at once with "Starting agent…", put a refused message back in the composer with the refusal's cause, and send a call that got no reply again with the same Exchange identifier | Changed | journey, drill |
| BKD-2.12 | ask "Stop current response?" only while the backend says the chat's Exchange runs, and on "Confirm" stop it, wait until it is saved and send | Kept | journey |
| BKD-2.13 | on ⌘Esc, show "Stopping…" from the request until the Exchange has ended, then "Canceled" with "⏹ Stopped" only when its end says `cancelled`, and otherwise its true final state, and count an Exchange as ended only once it is saved | Changed | journey, drill |
| BKD-2.14 | show a failed Exchange with "Failed", its time and its cause in plain words with its code and message, a code it does not know with its message, "Retry" on the chat's last Exchange and "Continue from failure point", and for `rate_limited` the time it resets | Changed | journey |
| BKD-2.15 | show the questions of the agent above the composer with their options, "Submit", "Continue" and "Cancel", no answer in free text, the answer only once its `answer` line is in `events.jsonl`, and the question kept after a `control_refused` | Kept | journey |
| BKD-2.16 | show an Exchange whose process is gone as interrupted, one that ended while the database was away from its folder marked "Not yet saved", and one the backend ended because it was stuck with "Ended because it was stuck" | New | drill |
| BKD-2.17 | rename a chat with ⌘-click on its title or R, an empty title taking it away and a placeholder never stored; mark it ongoing with ⌥0; archive it with ⌘⌫ or A after a confirmation, stopping a running answer first; and offer these as quick actions on ⇧⏎ | Kept | journey |
| BKD-2.18 | list the latest chats on ⌃⇧⌘C, at most 100, without the chat shown, those shown in the window first, each with its title, repository, route, state and age, digits opening the first ten | Kept | journey |
| BKD-2.19 | offer "Sign in…" on a Subscription that cannot be used and on a failed Exchange whose account is not signed in, and show each step of the Driver's `sign-in` as it comes: the address opened in a window that refuses other hosts, a field for a code, and, until the Secrets page exists, a concealed field for a key that is emptied once sent | Changed | journey; the host limit with SYL-192 |
| BKD-2.20 | show every attention item of its Root across the top of the chat for as long as it lasts | New | drill |
| BKD-2.21 | when the backend goes away, say that it reconnects, keep showing the chat and taking text, and read everything again once it is back | Changed | drill |
| BKD-2.22 | be a renderer bundle in `ui/elma/` of the `arbol` Build, in TypeScript with Svelte 5 from the components of `arbol-design-system`, follow version 1 where they differ, reach nothing but the Bridge and the app channel, never leave its own page, open an `http` or `https` link only through `app.openLink`, and keep in the page's own storage only the chat shown last, the last chat of each repository and the repositories used last | Kept | unit |

## Interface

The window uses the calls and topics of [BKD-1](01-the-bridge.md#interface) and the app channel's `app.pickFolder`, `app.openSignIn` and `app.openLink`. Its keys, as in version 1:

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
- **A window that stopped listening.** After its first local change, the window stopped rebuilding the chat from the backend, so changes made in another window showed only when the chat was opened again.

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
- `arbol_deprecated_v1:renderer/apps/elma/src/App.svelte#stopAgent`
- `arbol_deprecated_v1:renderer/apps/elma/src/pages/ElmaPage.svelte`

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| BKD-D17 | Where does the Leather Bag sign in, in the first thin path, the first version that goes once through every part (ARC-1)? | In Elma Chat's window: a panel opened from a Subscription that cannot be used and from a failed Exchange, which shows the Driver's sign-in steps. A key is never typed there; until the Secrets page exists, the panel shows the Keychain item to fill by hand (ARC-D62). The alternative: no sign-in in the first window, and signing in at the terminal | Decided 19 October 2026 by the owner: "Before Seqoya Secrets page is implemented we can use Driver own authentication flow." The panel shows the Driver's own sign-in steps, a key included ([BKD-D10](00-the-arbol-backend.md#decisions)), until the Secrets page of Seqoya Lab exists |
| BKD-D18 | In what is the window written? | TypeScript with Svelte 5, as version 1's Elma was, from the components and pages of `arbol-design-system`; where they differ from version 1, the window follows version 1 and the design system is brought in line. The alternative: another framework, which would rebuild those components | Decided 19 October 2026, a technical choice following BKD-D22 |
| BKD-D19 | What does a chat without a title show? | The first line of its first message, at most 80 characters, in a lighter type, never stored, because a stored placeholder kept titles from being made in version 1 and RCT-3 forbids it. The Trivial Trunk makes no titles (TRV-0), so every chat of the first thin path shows it until it is renamed | Decided 18 October 2026, a technical choice: the proposed default |
| BKD-D20 | Is the reasoning of the model shown? | Yes, open, as version 1 showed it, while the answer arrives. The chat tables keep none (RCT-3), so an Exchange shown again from the database has none | Decided 19 October 2026, a technical choice following BKD-D22 |
| BKD-D21 | When is a Draft saved, and what if two windows type in it? | As version 1: 350 milliseconds after typing stops, and at once when the composer loses the focus or another chat is shown. Changed: a failed save is said and tried again every 5 seconds; each save names the revision it was made over, and when another window saved meanwhile, the composer shows both texts with "Keep mine" and "Take theirs"; the page keeps no copy of a Draft, which in version 1 made a second owner of it | Decided 19 October 2026, a technical choice following BKD-D22 |
| BKD-D22 | What can the first version of Elma Chat do? | One kind of window with the chats of its Root on the left and one chat on the right, in which you start a chat, send, see the answer arrive, answer the agent's questions, stop, send again, rename, sign in and open a chat again later | Decided 19 October 2026 by the owner: "UX/UI should be the same as in deprecated version of Arbol." The first version has version 1's layout, navigation, keys, pickers, states and wording, as above, with the changes Arbol 2 needs and said where they stand; the parts in *What comes later* follow, each for the reason given there |
