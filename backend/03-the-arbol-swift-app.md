---
role: authored
spec: BKD-3
status: accepted
---
# Arbol backend · 03 The Arbol Swift App

## Purpose

The Arbol Swift App is the macOS program that stays in the menu bar. It opens the windows of any retained Root it can serve. Open Elma Chat under First Sapling and the window shows First Sapling's page, talks to First Sapling's backend and stays there when another Root becomes current.

## Scope

One Swift App, its numbered Builds, the tray menu, global shortcuts, native windows and Latest chats panel, and the host side of the Bridge and of opening a chat. [ARC-0](../architecture/00-components-and-boundaries.md#arbol-the-swift-app-and-the-backend) and [ARC-1](../architecture/01-roots.md) give the boundaries. [BKD-0](00-the-arbol-backend.md), [BKD-1](01-the-bridge.md) and [BKD-2](02-elma-chat.md) give the backend, the Bridge and Elma Chat. This specification also covers Seqoya Lab’s read-only Subscriptions listing. Willo Station’s pages, the other Seqoya Lab pages and Telegram listeners have separate specifications. The owner’s choices for startup, Root selection and relaunch are in [Decisions](#decisions).

## Behaviour

### One App and its Builds

The Swift and AppKit source lives in `arbol-app`. `arbol-builds build arbol-app` packages the signed macOS application bundle, including its executable entry, into the component's registry folder. The repository declares the entry `Arbol.app/Contents/MacOS/Arbol` and its build commands in `arbol-build.json`. The Build gate verifies the packaged plist and signature. Runtime qualification is separate. The App reads its running Build number from its own `build.json` and shows it in the tray. The package version remains in Build and bundle metadata. [BLD-0](../builds/00-builds-and-versions.md) governs the independent hexadecimal count, records, default, launcher and explicit `-v`. App Builds belong to no Root and are named `arbol-app@<build>`. The bundle is `<registry>/arbol-app/<build>/Arbol.app`. A development run outside the registry reports Build `0`.

There is one running App per signed-in user on the Mac. Concurrent launches agree which process owns the tray, hotkeys and backend lifetimes before any of them start. An explicit request to show the tray activates the resident App. A repeated background launch leaves the tray resident. A separate `-v` invocation for a different Build reports the running Build. The tray and `arbol-app --restart` can switch a running App. One owner-only file lock records the resident Build. The handoff reserves the transfer before it releases that lock. The ordinary launcher can pass `--show-tray` to request the menu from the resident.

The tray shows **Current Trunk**, the default Trunk for new windows in the current Root, and **Running Build**, the running App’s hexadecimal Build number. A packaged preview shows Build 0.

When a newer runnable working `arbol-app` Build is available, **Start new version** is the first action below the information section, with the target Build number beside it (BKD-D46). The tray icon shows a small exclamation badge for the same available Build. Its accessibility label and tooltip identify the available Build. The App checks the Build registry when it starts, wakes and opens the menu, and periodically while it runs, so the badge updates with the menu closed. The completed rebuild supplies the target. On selection, revalidate that exact Build, start the replacement through the normal launcher with `-v <build>` and wait for it to be ready. Allow each window to save or preserve its Draft, then give up tray and backend ownership so the replacement can take it. The resident process exits after the replacement confirms it started. Keep both Build payloads available against normal pruning until the handoff succeeds or recovery completes. A failed rebuild leaves the current App available. If the target becomes unavailable before shutdown, keep the current App running and show the cause. If the replacement fails before confirming startup, restore the prior App and report the failure. Exchanges keep running through the switch. The replacement starts in the tray and reads the current Root from the catalogue. Under [BLD-0.28](../builds/00-builds-and-versions.md#retaining-the-newest-build), the Build tool removes the previous App payload after the replacement confirms readiness and the previous process exits. If a newer successful Build arrives before the owner switches, it replaces the earlier waiting Build. Retention reconciliation remains pending.

Run `arbol-app --restart` to ask the resident App to switch to the newest runnable working App Build. The App reads the registry for the request and uses the same departure and handoff as the tray. The command reports the confirmed replacement Build or that the resident is already current. A busy, absent or unresponsive resident, a failed registry read or a refused handoff returns an error. The command neither opens the tray menu nor rebuilds the App.

Installation writes one per-user Aqua LaunchAgent with RunAtLoad and the absolute ordinary launcher path with `--background`. The login entry is independent of the numbered package and loads at the next login. At login macOS runs the ordinary launcher, which selects the working default Build. Only the tray icon appears. The menu stays closed and no window or panel takes focus. The App starts the compatible current Root's backend in the background. An explicit request for a UI opens its target. Closing the last window keeps the App and the current Root's backend running. Quit ends the App's backend ownership. The login entry starts the launcher again at the next login (BKD-D43).

<!-- sources:
arbol-app:Sources/ResidentApp.swift#ResidentApp
arbol-app:Sources/AppBuildHandoff.swift#AppBuildHandoff
arbol-app:Sources/ArbolApp.swift#ArbolApp
arbol-app:README.md#start-at-login
-->

### The tray menu and the catalogue

Read the current Root through `arbol-roots list` and open each UI for it through its shortcut. Use `arbol-roots use <identifier>` or `arbol-roots use --auto` to change that Root. Root creation, migration, readiness, failure marking and removal also use `arbol-roots`. Keep ownership of needed backends during a transient failed catalogue read.

**Trunks** lists the code names with a chosen runnable working Build in the current Root’s `arbol-root trunks` result. Mark the selected Trunk. The App stores the tray’s default per Root, initially `trivial`. Confirm a selection against a fresh catalogue before saving it, and show refusals on the Current Trunk row. Disable the menu when no eligible Trunk is available. An unavailable saved selection stays visible so the owner can choose another Trunk.

Outside the Trunks submenu, show each Root's database size from the backend's `health.measure` reply, by Root identifier. Use the current Root's running backend, or an already running backend for an open window if the current Root is unavailable. Never start an otherwise idle Root solely to measure it. Loading, unavailable and old measurements have distinct labels. A partial result preserves the values it actually measured and shows the affected Root's reason. Zero is a measurement only when the backend reports zero. Refresh asynchronously so a slow or failing measure leaves the open actions usable.

A failed whole-Root migration leaves its destination preparing and leaves the current Root alone. The implemented command reports this refusal to its caller. To show it on a later tray opening, `arbol-roots` publishes an optional Root-local `migrationProblem` in the catalogue. It gives the attempt time and a bounded, safe reason from the migration command, and clears on a successful whole migration or explicit readiness. The status display labels it “Migration failed” alongside the Root's actual state. When the command cannot confirm the outcome, its reason says so and the tray labels it “Migration outcome unknown”. Publish the problem only for an attempted whole migration of that preparing Root. A catalogue write failure leaves the original command refusal available. A comparison failure or failed one-chat reimport stays with that operation's existing BKD attention or error. No new catalogue flag makes a Root current or marks it failed.

<!-- sources:
arbol:src/arbol_roots/model.py#list_roots
arbol:src/arbol_roots/operations.py#ready
arbol:src/arbol_roots/operations.py#fail
arbol:src/arbol_roots/sql.py#migrate
arbol:src/arbol_backend/measurements.py#Measurements
-->

### Windows and renderer Builds

There is one window for each pair of Root and UI. Opening a second time raises and restores the same window. A minimized or hidden window is still open. Close saves the frame, gives the renderer a chance to save or preserve its unsaved Draft using the existing departure path, releases the web view and its socket, and leaves the menu-bar App available. Give each Root and UI its own saved window size and position. Restore a reachable frame after a display is disconnected. Keep native traffic lights, resize edges and system window actions. Drag the window from the background or passive content of the integrated header, including the area beside the traffic lights. Links, editable text, dropdowns, buttons and other controls keep their pointer and keyboard interactions. The shared header shows the window’s selected Trunk, as BKD-2.1 does for Elma Chat.

The App starts the named Root's backend through the launcher and opens the verified Elma renderer packaged in its own signed App Build. The App Build compiles the renderer from a pinned `arbol` source revision and records its provenance. Verify the renderer manifest against the running App Build and expose only its verified assets. A missing or damaged bundle yields a native error with Retry. Root availability comes from the Root's backend and existing minimum App requirement.

A backend rebuild can reconnect the same page through a fresh `hello`. Compatibility follows the Bridge version. An App Build update can run a new renderer against the same older compatible backend. Keep navigation, saved frame, Draft shadow and open target state isolated between Roots and UIs. Serve the shared verified bytes through WebKit at a stable origin for each Root and UI.

Before close, Quit or Build handoff, preserve the departing renderer’s bounded Draft shadow and pending open entries in WebKit storage at that same origin. Restore the entries to the next document before it starts. If preservation fails, keep the page and show a native error with Retry. Draft contents stay in the renderer’s storage.

Historical evidence: `arbol-design-system:heritage/app/Arbol/AppDelegate.swift#restoreFrame`, `arbol-design-system:heritage/app/Arbol/AppDelegate.swift#applicationShouldTerminateAfterLastWindowClosed`. The maintained contract for native chrome is [Native and auxiliary surfaces](https://github.com/sylvan-stack/arbol-design-system/blob/2ab1d528f93044b6ded9ecfbca87afdefd0b244c/docs/design-system/08-native-and-auxiliary.md).

<!-- sources:
arbol:scripts/package_backend.py
arbol:tools/elma_bundle.py#verify
arbol:ui/elma/src/bridge.ts
arbol:ui/elma/src/drafts.svelte.ts
arbol:ui/elma/src/opening.svelte.ts
arbol-app:Sources/ElmaWindow.swift#ElmaWindow
arbol-app:Sources/RendererBundle.swift#RendererBundle
arbol-design-system:src/pages/NativeSurface.svelte
-->

### The lifetime of a Root's backend

The App needs a backend for a compatible current Root as long as it runs, and for each other compatible Root as long as a window for that Root is open. A user opening Latest chats in an idle Root counts as one temporary window. The App reconciles this set when the catalogue or windows change. A newly current Root needs its backend even before a window opens. The previous current Root keeps its backend while one of its windows remains. Existing windows stay pinned to their original Root. When a Root is removed or its minimum rises above the running App, its windows show why the connection can no longer be used and the App stops its own backend for it. An incompatible current Root stays marked current, with no other Root promoted in its place.

The App uses `arbol --root <identifier> backend`, with a pipe it owns for standard input. It observes the ready or refusal line of [BKD-0](00-the-arbol-backend.md#the-process), verifies the Root and expected socket path, and retains the child handle. One launch at a time per Root is enough even if several windows open together. If the backend reports `already_running`, use the verified private socket of the existing backend. An App that did not start that process neither signals it nor takes responsibility for ending it. If it goes away while needed, the App starts one of its own.

A child ending while needed starts one replacement using the then-selected working Build. A rapid series of failures delays subsequent attempts up to a bounded retry interval and leaves the cause visible. A fresh catalogue or manual Retry can resume after repair. A failure in one Root leaves the others running. Once an owned child is no longer needed, close its input pipe and wait for BKD-0's shutdown before replacing it or ending the App. Termination fallback targets only the owned child. App failure closes the pipe as well. No App action stops or reassigns an Exchange or restarts a Trunk. Listeners belong to the current Root only. The listener handover remains with ARC-D52.

At startup the App also discovers Exchanges in retained Roots using each Root's matching `arbol-root --root <identifier> list` as in ARC-1.25. Log a manager refusal with its Root. This metadata needs no backend for an idle Root. A restart of the App or a backend uses that Root's own manager and restores live views from fresh subscriptions. Wake rechecks the catalogue, owned children and sockets, and lets the renderer check its subscription receipts. Sleep or a slow database alone is no reason to kill a healthy backend or change the Root of a window.

<!-- sources:
arbol-app:Sources/RootBackend.swift#RootBackend
arbol-app:Sources/RootSocket.swift#RootSocket
arbol-app:Sources/ArbolTools.swift#ArbolTools
-->

### Passing the Bridge on

Each loaded window connects once to its Root's owner-only `backend.sock`. The App accepts JSON strings on the `arbol` script message handler only from the current trusted bundle document in that window's main frame. It adds the LF frame terminator and forwards the UTF-8 bytes in order up to BKD-1's 16 MiB limit including LF. It passes reply strings as data to `window.arbolBridge.receive(text)`, in order and without reading their JSON fields. WebKit receives message text as a JavaScript argument. The App accepts no page-supplied socket address. It confirms the socket and its location belong to the current user and closes a connection with oversized, incomplete or invalid UTF-8 framing. Queue bounds and backpressure keep a slow or closed view from accumulating unbounded data.

A trusted renderer gets the backend's first `hello` once its receiver is ready. Reloading or closing the page closes that connection and cancels delivery to the previous document. A broken connection tells the loaded page `{"type":"lost"}` once and reconnects when that Root listens again. The page sees a fresh `hello` and restores its own subscriptions. The App replays no calls and retains no conversation or Bridge log.

Block navigations, popups, subframes and resource loads outside the verified bundle. An internal reload retains the same verified renderer and the window's own Root. Host controls and any native error page have no route to the Bridge. The App opens web links in the default browser through the app channel. It never opens a database. Tray and panel reads are a separate, bounded native client of the documented backend calls, with its own socket. This client parses its own replies and cannot receive a web view's traffic.

Platform references: [WKWebView navigation and local content](https://developer.apple.com/documentation/webkit/wkwebview), [frame identity](https://developer.apple.com/documentation/webkit/wkscriptmessage/frameinfo), [JavaScript arguments](https://developer.apple.com/documentation/webkit/wkwebview/callasyncjavascript(_:arguments:in:contentworld:)).

<!-- sources:
arbol-app:Sources/BridgeConnection.swift#BridgeConnection
arbol-app:Sources/ElmaWindow.swift#ElmaWindow
-->

### Hotkeys and Latest chats

Register the global keys from the one resident App. Register Option+E and Option+Q while the App is resident and release them before handing residence to a replacement. When either shortcut fires, re-read the catalogue and open or raise its UI for the current Root. If the current Root or requested renderer is unavailable, show the cause in the tray. If macOS refuses registration, show that the shortcut is unavailable. The rest of the global keys stay available. A renderer handles its own local keys, including the Elma latest-chats fallback when the native panel does not take the shortcut.

| Shortcut | Action |
|---|---|
| ⌥E | Open or raise Elma Chat |
| ⌃⌥⇧⌘W | Open or raise Willo Station when its bundle ships |
| ⌥Q | Open or raise Seqoya Lab when its bundle ships |
| ⌃⇧⌘C | Open or dismiss Latest chats |

A global hotkey uses the catalogue’s current Root, wherever focus is (BKD-D44). While the panel is open, its Root is fixed and named in its header. If the current Root has no compatible App or requested bundle, show the cause. The owner can change the current Root through `arbol-roots use` before invoking the shortcut again.

Latest chats is a native panel. It takes keyboard focus when invoked and can be used before Elma is open. If the owner selects a row in an idle Root, open Elma before releasing the panel’s hold on the backend. Use BKD-1's `chats` summaries for the selected Root, with the bounded candidate set in BKD-2.18. Exclude archived chats and the one shown in that Root's open Elma window. Order by that Root's Elma recent-view UUIDs first, then by descending activity, then UUID as the backend does. Each row shows title or title placeholder, repository, route, last Exchange state and age. Unavailable values are explicit. A new connection or a missed update starts a fresh subscription snapshot. The list shows loading, empty and failed reads with Retry. Digit keys 1 through 9 then 0 open the first ten rows, and arrows, Return and click reach all rows. Escape or clicking outside dismisses it and restores prior focus when appropriate.

Selection uses the same Draft-safe open path as a request from Willo Station. Preserve focus, the existing chat and the failed row on a refused open. Retry or dismiss the request from the panel. Stale migrated rows keep their distinct Bring over again action. The action is handled by the Elma renderer, with BKD-2.24's Draft and send barrier, actual result Chat, and uncertain-result handling. A native panel only requests an action. The renderer sends the mutation after its barrier.

Historical evidence: `arbol-design-system:heritage/app/Arbol/UISwitcherHotkeys.swift#bindings`, `arbol-design-system:heritage/app/Arbol/AppDelegate.swift#LatestChatSessionsHotkeyController`, `arbol-design-system:heritage/app/Arbol/AppDelegate.swift#LatestChatSessionsModel`. Use the maintained [Elma picker and opening contract](https://github.com/sylvan-stack/arbol-design-system/blob/09ae88b8be0c5871389fe7724001bf9c24b6be49/docs/design-system/05-elma.md) and [native surface reference](https://github.com/sylvan-stack/arbol-design-system/blob/09ae88b8be0c5871389fe7724001bf9c24b6be49/src/pages/NativeSurface.svelte). Implement and validate the native and design-system behavior together after acceptance, with fictional fixtures in the reference.

### Shared UI shell header

Each Arbol UI uses WorkspaceShell to render the design system’s WorkspaceHeader. Elma Chat and Seqoya Lab use this component in the App today. The component owns the shared title and workspace mark, Trunk dropdown, navigation control and native-control spacing. Each UI supplies its title and may add surface controls through slots. When a verified renderer advertises this header, the App places the native close, minimize and zoom controls in its leading space and hides the separate AppKit title bar. The window keeps native dragging, resizing and geometry. A renderer without the shared header retains native title-bar clearance.

The shared header places the same text size and theme controls in both UIs. Each page remembers its appearance for its own Root. Elma also supplies reading width for its conversation pane and can increase response text beyond the window text size (BKD-2.1).

Seqoya Lab opens for the current Root with **Option+Q**. Its shared header and navigation rail open Intelligence Providers. The page has Subscriptions, Vigor and Routing tabs, in that order. Subscriptions opens first and reads the selected Root’s accounts when it becomes active. Routing has a placeholder until it is implemented. The renderer reads its Root identity from the named backend’s Bridge hello through the trusted host. While at least one Seqoya Lab window is open, the resident Arbol App participates in the macOS application switcher as Arbol. The tray application uses its accessory policy again when the last Seqoya Lab window closes.

Subscriptions lists every account returned by that Root’s `accounts.list` (BKD-1). The page reads the list on entry, on Refresh and after reconnecting while open. It identifies the vendor family separately from the Driver and shows the stored sign-in state. A missing usage report is not zero. A Driver failure is shown alongside the other Drivers’ accounts. The last snapshot stays visible, marked as stale, after a failed read or lost connection to the same Root; a Root change clears it. No credentials cross the Bridge. Refresh reads the stored list without contacting a vendor. DeepSeek and z.ai offer a separate Refresh usage action for signed-in accounts. It calls the Driver through `accounts.usage` on demand and rereads the saved list. If the request fails, keep any saved report and show the cause on its card.

The Subscriptions card body shows allowance metrics. Preserve a vendor heading, the account identity when useful, sign-in state, and the existing explicit usage refresh and provider-console actions. The renderer’s fixed performance and cost metadata remains available for provider selection.

| Subscription (Driver/vendor family) | Model | Performance | Cost |
|---|---|---|---|
| Claude Code (`claude/anthropic`) | Opus 5.5 (default) | Top | Expensive |
| Codex (`codex/chatgpt`) | GPT-6.1-Sol (default) | Top | Expensive |
| Codex (`codex/chatgpt`) | GPT-6-Astra | Top | Expensive |
| Kimi Code (`pi/kimi-coding`) | Default | High | Moderate |
| z.ai (`pi/zai`) | Default | Medium | Moderate |
| DeepSeek (`pi/deepseek`) | Default | Medium | Cheap |
| MiMo (`mimo/xiaomi`) | Default | Low | Cheap |

Each card shows one section per applicable reported allowance window, ordered by earliest end, with a balance section for DeepSeek when the report provides a balance. Show the window length, reset timestamp, time remaining, expiration timestamp, used and remaining percentages, estimated output-token equivalents used and remaining, and estimated remaining equivalents per hour. Take percentages and absolute quantities from the same reading. Omit the reading timestamp from the Subscriptions card. Format timestamps that fall on the current local date as 24-hour HH:mm. Keep the date for other days. Compute the rate only with a positive time remaining. Preserve elapsed readings as historical and show elapsed time as zero. For active subscription plans supply measured numbers or labeled estimates with a reference model. DeepSeek API balance fields may be unavailable when the provider does not report them. A known reset without a separate expiry says No separate expiry. An elapsed window has no hourly rate and shows Period closed. A fresh z.ai five-hour window with no usage or reset time starts with the next use. A verified non-expiring allowance has expiration zero and displays Never. An account balance with no scheduled reset displays No scheduled reset, with unknown expiration when the vendor does not disclose it. Label a window Terminal when the provider forfeits unused allowance at its end. The MiMo Token Plan period and the Kimi membership monthly credits use their reported boundary as the expiration. Mark the derived values for these windows as terminal together with the window and label elapsed windows “Reset time passed” or “Allowance expired” when the corresponding time boundary passes. The label describes the time boundary independently of whether the usage limit was reached. [MiMo expiration policy](https://mimo.mi.com/docs/en-US/quick-start/faq/token-plan) · [Kimi membership credit rules](https://www.kimi.com/en/help/membership/membership-update-rules)

Show Available limit resets at the end of the card only when its count is positive. Show only unexpired reset entries with their reported names or scopes and expiry times when known. A single reset that covers multiple windows counts once. Use the saved report’s reset inventory, excluding an individual reset whose expiry has passed when the reported count and detailed available entries agree. Otherwise use the reported count. Subscriptions is read-only for reset grants. The metrics use existing report history and its nested windows.

Subscriptions and Vigor show quota issues beside the affected account. Identify the source of a window and elapsed resets. Show the recorded time when known in Vigor. For a signed-in MiMo account, prefer the current Driver report. Until the installed Driver exposes the credit count, accept a dated manual reading for the same binding or the Root’s last unpredicted Radar window. Explicit **Refresh usage** calls the MiMo Driver and preserves the last usable reading if the read fails. Xiaomi's monthly credits are separate from activity. Divide reported total and remaining credits by 600 to show a conservative estimate of `mimo-v2.6-pro` output-token equivalents. [Xiaomi Token Plan rates](https://mimo.mi.com/docs/en-US/quick-start/faq/token-plan/Usage%26Quota)

Pi’s Sign in with ChatGPT integration has no documented automatic quota read. A dated dashboard snapshot may show the verified app cap and shared five-hour and weekly windows for its own account. Indicate if plan access is disabled and report that the app’s own consumption is unknown when its cap is below 100%. Open the vendor dashboard to update the snapshot. Keep the distinction between the shared ChatGPT windows and an app-specific allowance, and flag elapsed readings. The native host may read one bounded, typed, optional `seqoya-usage-evidence.json` in the selected Root’s settings folder. It forwards only the specified usage fields, dates and allowed plan names. Manual Pi and MiMo entries match the listed subscription ID and saved update time; a changed binding cannot receive an earlier snapshot. The file contains no credentials or account identifiers beyond local Subscription IDs. The existing Seqoya-only `app.readVigor` takes an empty object and also returns optional `usageEvidence` and `usageEvidenceError` fields. The host reads at most 16 KiB from a private regular file, omits absent evidence, and reports unreadable or malformed evidence without exposing its content. The optional `piChatGPT` entry carries the subscription ID, binding update time, observed time, verified plan (`plus` or `pro`), plan access flag, app cap percent, and optional remaining percent and reset timestamp for each window. The optional `mimo` entry carries the subscription ID, binding update time, observed time, reset, and decimal total and remaining credits. The optional `codex` entry carries the subscription ID, creation and last identity-check times, plan (`plus` or `pro`), weekly reset, sample start and end, percentage-point movement and the three Astra token counts. [OpenAI tracking usage](https://developers.openai.com/siwc/token-sharing-open-source/profiles-and-sessions#tracking-usage)

For Codex, when local observations correspond to its weekly allowance, extrapolate a reference capacity from observed use and the observed percentage-point change. The evidence names the local Subscription ID, its creation and last identity-check times, the reported plan, calibration reset and observation period. Use the matching Codex account and plan only. A changed identity check requires a new calibration. Restrict the estimate to observations that ended in the last 28 days, with at least five percentage points of movement in one weekly window. Label a later weekly reset as a previous-window calibration. Use published GPT-6 Astra Standard credit weights to normalize its observed uncached input, cached input and output tokens and the GPT-6.1 Sol Standard output weight to express the result in output-token equivalents. Report the arithmetic, the source and the assumptions, including possible shared-plan use. Derive estimated remaining tokens from the current reported weekly share before its reset. Keep these estimates informational in Vigor. For providers with no credible conversion or calibration, show the specific missing input. [Codex credit rates](https://learn.chatgpt.com/docs/pricing#token-rates)

For z.ai model credit windows, match the cap verified from the bound account’s quota reply. Estimate GLM-5.3 Standard output equivalents as credits × 10,000 ÷ 24. Do not apply the model conversion to MCP call quotas. Estimate Claude and Kimi credit-window capacity by dividing observed local output tokens by the same window’s recorded used share. Estimate Kimi call capacity by multiplying the reported call count by the observed median output per local turn. Estimate the Pi ChatGPT shared windows from matched local Codex observations of the same Plus windows and published Standard credit weights. These are reference workload estimates. Show their basis and observation date in the estimate’s details. Apply each estimate to the same account and named window only, using the latest recorded percentage for that window. Keep the Vigor calculations separate. [z.ai quota and credit conversion](https://docs.z.ai/devpack/overview.md#usage-instruction)

The optional Root evidence file may include up to sixteen typed window estimates. Each identifies the source basis, local Subscription ID, last identity-check time, the window label, observation time and bounded numerical operands. Accept recognized basis and label pairs only. Never apply an estimate when the reported identity-check time changes. Existing evidence files remain readable. If evidence is missing or no longer matches the binding, explain which estimate needs a new reading. Populate the matching estimates from the verified account readings and local observations for the current Root.

Vigor shows a compact ranked list for the window’s Root. Activate a row to show the calculation, its reset or recovery, and the saved window losses, weights and contributions. Show report age, predicted windows and exhaustion when reported. On tab entry and Refresh, read the latest saved rollup through the trusted App and the public account listing for sign-in state and available balances. These reads make no vendor usage request. Keep previous results visible when a read fails and report partial failures.

Seqoya uses the saved timed-window score when it exists. For active accounts with no score, label the displayed value Estimated and show its basis. Give an exhausted account or a confirmed insufficient balance a zero. Give other active accounts without usable allowance data a provisional score of 0.05 and show the missing input. Only an account known to be inactive shows Unavailable. An account with unreadable sign-in state can still display its saved score or a provisional estimate with the reason.

For a DeepSeek balance with no reported reset, estimate how many output tokens it can buy at the `deepseek-flash` peak output rate. Use the documented rates of USD 1.20 or CNY 8 per million tokens. If both currencies are returned, use the larger token estimate. Score that capacity as `0.5 × tokens / (tokens + 1,000,000)`. A larger usable balance scores higher, with 0.25 at one million tokens. Show the estimated tokens, rate and formula in the row. The estimate uses the saved balance and the rate snapshot. [USD rates](https://api-docs.deepseek.com/quick_start/pricing/) · [CNY rates](https://api-docs.deepseek.com/zh-cn/quick_start/pricing/)

Vigor details show the numerical calculation for the displayed score. For a timed window, show used share, remaining minutes, total minutes, loss and weight with the substituted arithmetic when those inputs were saved. Show the summed contributions and cap or the exhaustion rule. For a balance estimate, show both the balance conversion and score with values substituted. Explain the provisional score as a fixed value when the inputs are unavailable. Show the last 30 days of recorded Root activity for Pi’s ChatGPT account and MiMo when available, alongside their score and its basis. Activity does not supply quota.

The header displays the window’s Trunk. A new window starts with the tray’s default for its Root. The dropdown lists Trunks available for that window’s Root and selects one for that window only. Show loading, no compatible Trunks and refusal states. Selection stays in the same window and does not affect its Root or any accepted Exchange. A selection request belongs to the originating trusted document. A new Exchange uses the window’s selected Trunk at dispatch, including an explicit retry or Continue. A transport retry repeats the captured Trunk and Exchange identifier. Older backends support the default `trivial` path; Elma refuses to dispatch a non-default Trunk until the backend advertises support.

<!-- sources:
arbol-design-system:src/patterns/WorkspaceHeader.svelte
arbol-design-system:src/patterns/WorkspaceShell.svelte
arbol:ui/elma/src/seqoya/App.svelte
arbol-design-system:src/sections/SubscriptionList.svelte
arbol:ui/elma/src/preferences.ts
-->

### Opening a chat and using native controls

The *app channel* is the small set of requests the App itself answers. It is available only to the same trusted document as the Bridge. It validates each method, parameter and caller and returns one reply with the request's ID. An open request names an explicit target Root and exactly one chat UUID or absolute new-chat folder. A request cannot supply a program, a URL for the web view or a backend path. A Willo renderer can submit a chat from its own Root or from a Root it identifies in its discovery view. The App validates the Root, checks its App minimum, queues the request before opening Elma and returns an explicit refusal if it cannot queue it. This gives Willo's First Sapling hand-over a receiver. Willo's own UI and its choice of target stay with that specification.

There is a queue for each target Root. A request arriving while Elma loads stays in that queue. The App sends `{"type":"open"}` when the loaded page can receive it. When a renderer calls `app.takeOpen` after its Draft and pending-operation barrier, the App hands it the next target. Retain it until delivery to that document succeeds. A failed delivery leaves it waiting. After delivery, the renderer retains its target through a page reload and reports read failures with Retry and Dismiss, as BKD-2.19 specifies. A Root change, an unrelated window and a later request cannot take or overwrite that target. An App relaunch starts a fresh native queue. Chats and Drafts already saved belong to the backend.

Older compatible bundles continue to speak BKD-1's three app calls. The initial native panel can read the old backend's chat summaries and deliver the original open target to those bundles. The Elma page then owns the open result and retains its own fallback list and migration actions. An updated Elma advertises panel support with `app.elmaState`. It supplies its current and recent chat IDs and reports each selected action's outcome. The panel keeps that row pending until Elma reports the result. On older renderers the native list uses activity order when no recent-view state is known and Elma shows the outcome of the handoff. The original call and result forms remain valid across new App Builds. An owner-authorized compatibility change that requires newer host behavior can declare a new minimum through `arbol-roots app`.

For folder picking the App opens the macOS folder dialog attached to the requesting window. The optional starting folder is a hint. The owner chooses a directory or cancels; cancellation returns null. Elma waits up to 30 seconds for an app call. End the picker by that deadline and close it when its document leaves, so a late selection cannot apply to another page. For links the App accepts a well-formed absolute HTTP or HTTPS URL and asks the default browser to open it. It returns a safe refusal for other schemes or a failure to open.

<!-- sources:
arbol-app:Sources/ElmaAppChannel.swift#ElmaAppChannel
arbol-app:Sources/ElmaAppChannel.swift#ElmaOpenQueue
-->

## Requirements

| ID | The App must | Origin and basis | Verified by |
|---|---|---|---|
| BKD-3.1 | Package `arbol-app` as a global numbered Build, launch the selected Build through BLD-0, and show the running Build number | Changed · ARC-D21, BLD-0 | Installed default and exact Build launch |
| BKD-3.2 | Start one resident App per signed-in user at login with only the tray icon, and badge the tray icon and offer Start new version as the first action when a newer runnable working Build is ready. Accept `arbol-app --restart` through the same handoff and report its outcome | Changed · ARC-0.5, BKD-D43, BKD-D46 | Login, last-close, concurrent start and failed/successful Build handoff journey |
| BKD-3.3 | List only Trunks with a chosen runnable working Build for the current Root. Select the default Trunk for new windows in that Root and show catalogue and selection refusals on the Current Trunk row | Changed · owner request, ARC-1.6, 1.7, 1.21, 1.23, BKD-D45 | Tray and CLI journey with eligible and ineligible Roots, an older selection, relaunch and refusal |
| BKD-3.4 | Show Root measurements and migration refusals with the actual Root state outside the Roots submenu | New · ARC-1.11, 1.18; BKD-0.27 | Tray journey with partial measurement and failed migration |
| BKD-3.5 | Bind one reusable window per Root and UI to the verified renderer in the shared App Build, allow dragging from passive header areas and restore usable native chrome and geometry | Changed · ARC-0.5, ARC-1.6, BKD-2.1 | Two-Root window and display-change journey |
| BKD-3.6 | Start and supervise the compatible current Root's backend and the backends of other Roots with open windows, and end only owned children when released | New · ARC-0.7, BKD-0.2–3 | Installed crash, wake, overlapping open, promotion, last-close and quit drill |
| BKD-3.7 | Rediscover retained Roots' Exchanges through the matching managers, isolate discovery failures and leave accepted Exchange ownership intact through restarts | New · ARC-1.25–26, BKD-0.21–22 | Multi-Root restart drill with an Exchange in progress |
| BKD-3.8 | Relay opaque BKD-1 frames on one private socket per trusted window, refuse untrusted content and isolate connection and page generations | Changed · ARC-0.6, BKD-1.1–3, 1.11 | Native wire and WebKit boundary checks |
| BKD-3.9 | Deliver disconnect and fresh hello, retain the renderer across compatible backend Build changes and preserve Drafts across App departure | New · ARC-0.26, BKD-1.3, BKD-2.22 | Installed reconnect and retained old Root/Build journey |
| BKD-3.10 | Open or raise Elma Chat with global Option+E and Seqoya Lab with global Option+Q. Send the available global shortcuts to the catalogue’s current Root regardless of focus. Report registration failures and keep explicit Root opens available | Changed · owner request, BKD-2.18, BKD-D44 | Native key journey with focus in a different Root or application |
| BKD-3.11 | Show and select Root-local Latest chats with the existing ordering, keyboard and Draft-safe behavior, including the separate reimport action on capable renderers | Kept · BKD-2.18, 2.24 | Native panel journey, including failed read and failed selection |
| BKD-3.12 | Answer the native folder and link calls and deliver queued opens only to the intended Root's Elma document | Kept · BKD-1.11, BKD-2.19 | Native app-channel and Willo open journey, including cold window and Draft conflict |
| BKD-3.13 <!-- 206cc66a-8fb5-4100-92be-649300a25d89 --> | Show the default Trunk for new windows and the running App’s Build number in read-only rows above the tray actions | Changed · owner request, 11 November 2026 | Tray journey across Root selection and App Build handoff |
| BKD-3.14 <!-- 15658f18-630e-4ae0-8387-634608110c03 --> | keep the running App and newest ready Build during handoff and have the Build tool retire the previous payload after the replacement is ready and the previous process exits | Changed · BLD-D25, BLD-0.28 | Installed retention handoff drill pending |
| BKD-3.15 <!-- 53a6f4a4-cbaf-470e-ba8f-7cf056484a19 --> | Refresh the Current Trunk row and submenu checkmark after a selection or catalogue update, with explicit loading and unavailable states | Changed · owner request, 11 November 2026 | Tray journey across Root selection and clearing |
| BKD-3.16 <!-- ba8c172c-bdbc-4d20-8cc3-ffe68e930ef7 --> | Use one shared header with integrated native controls and a Trunk dropdown that selects a compatible Trunk for the originating window only, with availability feedback | New · owner request, 11 November 2026 | Two-Root dropdown journey with an open Draft and a refused target |
| BKD-3.17 <!-- 1e2a3635-e381-4f89-8c8d-686bddb48fd7 --> | Open Seqoya Lab in its own window for each available Root. Use the shared header and one Intelligence Providers page with Subscriptions, Vigor and Routing tabs. Start on Subscriptions and participate in the macOS application switcher while Seqoya Lab is open. In Subscriptions, list accounts and saved usage from `accounts.list`, allow explicit DeepSeek, z.ai and MiMo usage reads, show one metrics section per allowance window and the subscription’s on-demand reset inventory, using reported or dated dashboard values and explicit unknowns | New · owner request | Open both surfaces for one Root and select a window-local Trunk in Seqoya; verify stored-only Refresh, partial and stale results, reconnect in Subscriptions, terminal windows, elapsed readings, and known and unknown reset inventories |
| BKD-3.18 <!-- f9b70c2f-a809-4208-b534-211d8219d961 --> | Show the bound Root’s Vigor as ranked, expandable rows with substituted numerical calculations, Pi and MiMo Root activity, quota and capacity evidence, and clearly marked estimates for active accounts lacking a saved score. Account for available token capacity in the estimate for a balance with no reported reset. Reserve Unavailable for accounts known to be inactive | Changed · owner request | Open Vigor in the installed App and inspect calculated, estimated, exhausted and inactive rows |

Verification descriptions name future evidence. The App implementation will follow the owner's separate testing and Build policy.

## Interface

| Boundary | Form |
|---|---|
| App start | `arbol-app [-v <build>]` via BLD-0. Login passes `--background` to the default launcher. `--show-tray` requests the resident menu. `--restart` requests the newest runnable working Build through the resident handoff. Tray relaunch names the prepared Build. The Build record declares the executable entry inside the macOS app bundle |
| Default UI Root | One persisted Root identifier, or follow the catalogue current flag when absent. Scope is the App per user |
| Catalogue and Build inventory | `arbol-roots list`, `arbol-builds show arbol@<build> --root <root>`, and `arbol-builds show arbol --root <root>` for a Root's default. ARC-1 and BLD-0 give their records and refusal envelopes |
| Catalogue extension | Optional `migrationProblem: { at: string, reason: string, uncertain?: true }` on a Root record. Older records without it report no recorded migration failure |
| Backend | `arbol --root <root> backend`, ready/refusal line and stdin ownership from BKD-0.2. Private socket and web view handlers from BKD-1.2 |
| Native reads | Separate backend client uses `health.measure` for the tray, `chats` for the picker and read-only `workspace.get` when resolving repository labels. It checks the backend's Root and supported Bridge version before sending its own calls |
| App channel | `window.webkit.messageHandlers.arbolApp.postMessage(text)` sends `{type:"call", id, method, params}`. `window.arbolApp.receive(text)` takes `{type:"reply", id, result}`, `{type:"reply", id, error:{code,message}}` or `{type:"open"}`. Text is JSON, as in the implemented Elma adapter |

| App method | Parameters | Successful result |
|---|---|---|
| `app.pickFolder` | `{start?: string}` | `{folder: string}` or `{folder: null}` |
| `app.openLink` | `{url: string}` | `{}` after the system accepts the open |
| `app.currentTrunk` | `{}` from a trusted UI | `{trunk: string}` for the bound window |
| `app.listTrunks` | `{}` from a trusted UI | `{trunks: string[]}` for the bound window’s Root |
| `app.readVigor` | `{}` from a trusted Seqoya document | The saved SGM-1 rollup for the window’s bound Root, with optional typed `usageEvidence` or `usageEvidenceError` |
| `app.selectTrunk` | `{trunk: string}` from a trusted UI | `{trunk: string}` after validating and applying it to that window |
| `app.takeOpen` | `{}` | `{chat: string}`, `{folder: string}` or `{}` |
| `app.openChat` | `{root: string, chat: string}` from Willo Station | `{}` after the host queues the request |
| `app.elmaState` | `{shown: string or null, recent: string[], panel: 1}` from Elma | `{panel: 1}` on a host that implements this adapter |
| `app.openResult` | `{request, status, error?}` from Elma, for a correlated panel action | `{}` after the host records the outcome |

When both ends support `panel: 1`, a panel selection extends the `app.takeOpen` chat reply with an opaque `request` identifier and an `action` of `open` or `reimport`. The renderer retains them with its pending target across reload. Keep a taken request in the same page session through the existing Draft barrier. If an outcome goes missing, show that the open could not be confirmed and let the owner dismiss or check the chat. It reports `opened`, `failed`, or `dismissed` for that identifier, with a safe error on failure. An uncertain reimport reports failure with the BKD-2.24 message and permits a fresh read, without retrying the mutation. Ordinary chat and folder replies retain their original shape. A native panel and its result are bound to the target Root and request. A panel that closes cannot be changed by a late outcome. Older hosts and the development relay can ignore the added method and keep the renderer fallback.

Use `invalid_input` for malformed arguments, `unknown_root` for an unavailable catalogue entry, `app_build_required` with the minimum for an incompatible Root, `build_unavailable` for a missing UI and `operation_failed` with a safe cause for a native failure. The additive panel adapter carries only the shown chat, up to 100 recent chat IDs, supported actions and a request-correlated outcome. Negotiate that adapter before using it. The initial BKD-1 call forms need no capability exchange.

<!-- sources:
arbol:ui/elma/src/app-channel.ts
arbol:ui/elma/src/opening.svelte.ts
arbol:ui/elma/src/chats.svelte.ts
arbol:ui/elma/src/preferences.ts
arbol:src/arbol_builds/service.py#show_build
-->

## Known problems in version 1

- **One app bundle per UI.** Each bundle embedded its renderer and needed its own process. Multiple processes negotiated which one owned the global keys. One App now opens Root-selected pages and owns the keys once.
- **One global recent history.** The native Latest chats panel shared one set of active and recent session IDs. Root-local views and queues now keep one Root's chat from being selected in another.
- **Restoring a window on a disconnected display.** A saved frame only partly on a connected display could still leave the useful controls out of reach. Restore a reachable frame.

Historical evidence: `arbol-design-system:heritage/app/Arbol/UISwitcherHotkeys.swift#UISwitcherHotkeysController`, `arbol-design-system:heritage/app/Arbol/AppDelegate.swift#LatestChatSessionsHistory`, `arbol-design-system:heritage/app/Arbol/AppDelegate.swift#restoreFrame`.

## Decisions

| ID | Question | Outcome | Status |
|---|---|---|---|
| BKD-D43 | What should an ordinary start show, and should Arbol start at login? | Start Arbol at login with only the tray icon. Open a window or panel on an explicit request | Decided by the owner · 11 November 2026 |
| BKD-D44 | Which Root should a global shortcut use? | Send global shortcuts to the catalogue’s current Root, regardless of focus. A panel stays on the Root it opened with | Decided by the owner · 11 November 2026 |
| BKD-D45 | What Root information and selection belong in the tray? | Show the catalogue’s current Root and let the owner change it for UI opens, global shortcuts and implicit CLI routing. The tray uses `arbol-roots` for this change. Root administration continues through that tool | Changed by the owner · 11 November 2026 |
| BKD-D46 | How should the resident App switch to a newer or explicitly selected Build? | Badge the tray icon with an exclamation mark and show **Start new version** as the first action when a newer runnable working App Build is available. Use that prepared Build for the handoff. Offer the same handoff through `arbol-app --restart` | Changed by the owner · 11 November 2026 |
| BKD-D47 | How does the App start and stop a backend without owning a manually started process? | Reconcile the compatible current Root and the Roots of open windows. Reuse a verified already-running socket and use child-input ownership for shutdown and restart of App-started children | Technical choice · 11 November 2026 |
| BKD-D48 | How can the App stay an opaque relay and still draw native surfaces? | Keep a separate read-only native client for tray and panel data. Use an additive app-channel adapter for Elma's local view state and selection outcomes. Keep mutating work and its Draft barrier in Elma | Technical choice · 11 November 2026 |
| BKD-D49 | Where does the tray learn about a whole-Root migration refusal after the command exits? | Add an optional safe problem to the existing catalogue, using the Root command as its writer and clearing it on success or readiness | Technical choice · 11 November 2026 |
| BKD-D50 | How do login and concurrent starts share the resident App? | A per-user Aqua LaunchAgent runs the default launcher at login. A private lock records the resident Build and a second lock reserves the existing tray handoff. The login installation takes effect at the next login. | Technical choice · 11 November 2026 |
| BKD-D51 | How does an older renderer keep its state at native departure? | Each Root and UI has a stable, bundle-only WebKit origin. Before departure keep only the renderer's bounded recovery entries in WebKit storage. Restore them to the next document before it runs, or keep the current page if preservation fails. | Technical choice · 11 November 2026 |
