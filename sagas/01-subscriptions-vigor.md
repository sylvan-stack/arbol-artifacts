---
role: authored
spec: SGM-1
status: draft
---
# Sagas · 01 Subscriptions Vigor

## Purpose

Specify Vigor: how urgent it is to use a [Subscription](../GLOSSARY.md#subscription)
now, because allowance it still holds will expire unused at a coming reset.
Subscriptions Vigor is the [Radar](../GLOSSARY.md#radar)'s view of that number
for every Subscription on this computer, so the owner can send work where
allowance would otherwise be wasted. As in SGM-0, the inputs and their meaning
come before the arithmetic.

The owner asked for the metric on 26 October 2026 and settled, in the session
that drafted this chapter, where it is computed, that shorter windows count
with less weight, the pace assumption, that the Radar owns the rollup, that
unknown is always shown with its reason, that every calculation is logged, and
the allowance source for Kimi Code, and that a blocked Subscription shows
zero with its recovery, and that the contract's window says what it counts.
The weight placeholder's value and the first operational profile remain
proposals. The [Decisions](#decisions) table distinguishes them.

## Scope

This chapter owns the definition of a window's loss, a Subscription's Vigor,
the blocked state and the next change, prediction after a reset, stale and
unknown inputs, the calculation record, the Radar rollup, and what each Driver
must deliver for the calculation. It does not own how a Driver fetches usage,
which is the [Driver Contract](../driver-contract/01-subscriptions.md) and each
Driver's own specification; spend and cost; or [Burn](../GLOSSARY.md#burn),
[Load](../GLOSSARY.md#load) and [Velocity](../GLOSSARY.md#velocity).

The first version computes and logs Vigor and answers a read through
`arbol-cli`. It displays nothing in [radar-stats](../../mycel/operations/radar-stats.md),
which reads the Sagas corpus and runs without Arbol. Vigor recommends where to
spend; it never routes a Turn or changes a Chat's Intelligence Provider.

## Behaviour

### What a usage report says

Every Driver reports usage in one shape, the Driver Contract's `UsageReport`: a
list of windows, each with a kind, a label, the used share as a percentage,
the reset time, the length in minutes and whether the limit is reached. A
report is fetched only when asked (DRV-1.16); a vendor tool also reports the
windows during a run at no cost, and the Driver stores the latest such report
when the run ends (DRV-4.13). The last `ok` report is stored with the
Subscription and returned with its record (DRV-1.18). An unknown value is
absent, never zero (DRV-1.17).

Observed on 27 October 2026 on the installed Builds, Claude `d`, Codex `9`
and Pi `6`, where each family's report comes from and what each window counts:

| Family | Driver | Source of the report | Windows |
|---|---|---|---|
| Anthropic | Claude | `rate_limit_info.unifiedWindows` in the tool's stream during a run. `usage` on demand returns the stored report and `unsupported` before the first run | five hours (`session`, 300 min) and seven days (`weekly`, 10,080 min), both `tokens`; a used share above 100 % is reported as such when the account spends overage |
| ChatGPT | Codex | the app server's rate-limit read on demand and its notifications during a run | five hours and weekly as the app server reports them, with no `resource`, since the app server names no unit |
| Kimi Code | Pi | `GET https://api.kimi.com/coding/v1/usages` on the coding API with the Bearer token Pi already holds. Probed and adopted 26 October 2026 (SYL-288, Pi Build 5) | five hours, `calls`; the month's Kimi Code share and the month's total across all Kimi products, both `credits`, on a 30-day cycle |
| z.ai, DeepSeek | Pi | none: `usage` answers `unsupported`, a known gap since the cutover moved both families from the Claude Driver to Pi. The Claude Driver's reading of z.ai's quota API, which gave a five-hour window, a weekly window where the plan has one and a monthly count of MCP calls, is the candidate for qualification in Pi | none |

<!-- sources:
arbol:driver-contract/01-subscriptions.md#Usage
arbol-claude-driver:src/arbol_claude_driver/protocol.py#limit_report
arbol-claude-driver:src/arbol_claude_driver/subscriptions.py#normalize_quota
arbol-codex-driver:src/arbol_codex_driver/catalog.py#normalize_window
arbol-pi-driver:src/arbol_pi_driver/accounts.py#Accounts.usage
-->

The Kimi probe, with the owner's own token: the endpoint answered 200 with a
`limits` list holding the five-hour window as limit, used, remaining and reset
time, and a `usages` object with `limit_5h`, `limit_month_total` and
`limit_month_code`, each a used ratio and a reset time. An expired token gives
401. The neighbouring paths `/coding/v1/usage`, `/coding/v1/quota` and
`/coding/usage` are 404. The Kimi Console's own gateway, the billing and
membership services under `www.kimi.ai/apiv2/`, rejects the coding token even
when fresh, with a signing-method error: the Console needs the web session's
token, which no Driver holds. Reading the Console page in a hidden browser,
which version 1 did for Anthropic, is therefore not adopted (SGM-D23). The Pi
Driver's own specification records the adopted endpoint, its negative controls
and its requirement row
([PI-1 Subscriptions](../../arbol-pi-driver/specs/subscriptions.md), SYL-288).

Two facts about reports shape everything below. A report is a floor on the
used share: every logged-in device and key of the same account spends from
the same windows, so the owner's own terminal sessions move the numbers
between reports. And an Anthropic report refreshes only through a run, so an
idle Claude Subscription's report ages until the next run or an explicit
fetch where the family supports one.

### Stores and gates

Every window is a bucket that refills at its reset; whatever is left in it at
that moment is thrown away. The buckets differ in size and are nested: the
week's bucket holds many five-hour buckets' worth, and the week can only be
spent through the five-hour bucket. So the longest token window of a
Subscription is its **store**, where the allowance of consequence expires, and
every shorter token window is a **gate**, which bounds how fast the store can
be spent and, when reached, stops spending altogether until it resets.

Only windows whose resource is tokens or credits take part in the sum. A
window that counts something else, such as Kimi's five-hour window of calls
or z.ai's monthly MCP calls, is shown but not summed (SGM-D24); it can still
block, see below. When several windows share the longest length, as Kimi's
monthly code share and monthly total do, the store is the one scoped to the
coding product the Subscription serves; the others of that length are shown
and not summed (SGM-D25).

### The loss of one window

To say how much of a window will be left at its reset, the calculation
assumes a pace from now until then. The reference is the window's **even
pace**: the allowance spread evenly over the window's length, the pace that
drains the whole bucket exactly by its reset. The loss of a window is the
share of its allowance that expires unused if spending continues at that even
pace from now.

```text
For a token window w of a Subscription, from its last usage report:
  r(w)    = 1 − usedPercent(w) / 100        the share still unspent
  t(w)    = resetsAt(w) − now               the time until its reset
  T(w)    = windowMinutes(w)                its length
  loss(w) = max(0, r(w) − t(w) / T(w))      the share expiring unused at even pace
```

A window on or ahead of its even pace loses nothing. A window at its start
loses nothing, however full. A window minutes from its reset loses almost all
of what is unspent.

### Vigor of a Subscription

```text
Vigor = min(1, Σ over the Subscription's token windows of weight(w) × loss(w))
weight(store)  = 1
weight(gate)   = the gate's allowance as a share of the store's allowance;
                 until learned, the placeholder 0.1
```

The weight says how much allowance a bucket holds relative to the store.
Vendors do not publish the ratio, but it can be learned: whenever one run
moves both a gate and the store, the two changes in used share give it
(see [The calculation record](#the-calculation-record)). Until the learned
value is calibrated and approved, every gate uses the placeholder `0.1`,
chosen because Anthropic's published plan limits put a week at roughly ten
five-hour windows; it is a placeholder, not a measured value (SGM-D15).

Vigor is near 1 only when most of the store is unspent and its reset is near.
It is 0 when the reset is far, when the store is mostly spent, or when a gate
blocks spending right now.

### Blocked Subscriptions and the next change

A Subscription is **blocked** while any window that gates inference is
reached, whatever it counts: the vendor refuses every request until that
window resets, and Kimi's five-hour window of calls blocks exactly as a token
window does. A window scoped to one tool, such as z.ai's MCP count, gates only
that tool and does not block (SGM-D27). The report marks a reached window with
`limitReached`. A reached window with paid overage switched on
is not a block, since the account keeps spending; the Claude report says so in
`extra.isUsingOverage`, and the Codex report keeps the vendor's related
fields in `extra`. A reached window's own loss is zero in either case, because
nothing is left in it.

Vigor measures the urge to use the Subscription now. While it cannot be used,
that urge is zero. A blocked Subscription therefore shows `0`, with its
**recovery** beside it, the next change: the earliest reset among the windows, and the Vigor
the Subscription will have at that moment, computed on the predicted windows
below. "0 now, 0.39 at 13:20" tells the Radar when a blocked Subscription is
worth using again (SGM-D16).

Every result carries its next change, blocked or not, since Vigor also jumps
when a store resets and its unspent share is lost.

### After a reset without a report

When a window's reset time passes and no newer report has arrived, the
calculation **predicts** a fresh window: used share 0, reset one length later,
reached cleared. The prediction is marked as such on the window and on every
result that uses it. A fresh report, from a run or from an explicit fetch,
replaces every predicted window. An explicit fetch through the Driver's
`usage` operation is also the owner's manual recalculation: it replaces
predictions with the vendor's numbers, including after a manual reset or an
extra-usage purchase on the vendor's side (SGM-D20).

### Stale and unknown

As in SGM-0, each input is `known`, `unknown` or `stale`; only `known` supplies
a value, and a known absence never becomes zero.

A result is **stale** when the report it rests on is older than the
Subscription's shortest token window. It is still computed, from the report
and the clock, and shown with the report's age, since the owner's other
devices may have spent allowance the report does not show.

A result is **unknown** when the Subscription's Vigor cannot be computed, and
unknown is always shown with its reason, never as a blank or a zero
(SGM-D19). Two reasons are told apart, because one is a defect to fix and the
other a known gap:

| Reason | Shown as | Meaning |
|---|---|---|
| A token window of an `ok` report lacks its used share, length or reset time | `unknown: <field> missing in the <family> report` | A Driver defect; name the Driver and the field |
| The report's outcome is `unsupported` | `unknown: allowance not supported for <family>` | A family without a qualified allowance reading |
| The report's outcome is `needs_sign_in` or `unavailable` | `unknown: <outcome>` with the report's message | Sign in, or the vendor was unreachable |
| No report yet | `unknown: no report yet` | Nothing has run and nothing was fetched |

### The calculation record

Every calculation is logged, and so is every report as it arrives (SGM-D22).
The record is for learning, not for display: it is what teaches the gate
weights, checks predictions against later reports and lets a changed formula
be replayed over history. Records live in Arbol's database, never in a
corpus or in git.

A calculation record holds the Subscription, the moment, the report used with
every window's used share, reset time, length and reached flag, which windows
were predicted, the pace assumption and the weights with their profile
version, each window's loss, the result, its stale and unknown state with the
reason, and the next change with its value. A report record holds the report
as delivered, the Subscription, the moment, and the run that produced it when
a run did.

Learning the gate weight: for two consecutive reports of one Subscription
around one run, with no other device active, the change in the store's used
share divided by the change in the gate's used share is the gate's allowance
as a share of the store's. Single observations are noisy, since other devices
share the account; the learned weight is a calibrated estimate over many
pairs, versioned like a profile of SGM-0, and replaces the placeholder only
when approved (SGM-D17).

### Subscriptions Vigor on the Radar

The Radar is the gathering point for machine-wide work statistics, and the
glossary already names usage rollups per Subscription among them. Subscriptions
Vigor is that rollup: every Subscription on this computer with its Vigor, its
next change, its stale or unknown state with the reason, sorted by Vigor. The
headline is the highest value, named with its Subscription. Values are never
added across Subscriptions: a sum of Claude's and Codex's shares means
nothing (SGM-D18).

A Subscription, not an Intelligence Provider, is the unit: two Intelligence
Providers bound to the same account share one Vigor. Unknown Subscriptions
stay in the list, below the known ones, with their reason.

### Worked examples

Monday 10:00, a Claude Subscription whose week resets Thursday 10:00:

| Window | Used | Resets | t | T | t / T | r | loss | weight | contribution |
|---|---|---|---|---|---|---|---|---|---|
| Five hours | 35 % | 13:20 | 200 min | 300 | 0.67 | 0.65 | 0 | 0.1 | 0 |
| Seven days | 20 % | Thu 10:00 | 4,320 min | 10,080 | 0.43 | 0.80 | 0.37 | 1 | 0.37 |

Vigor `0.37`: at even pace, more than a third of the week's allowance expires
unused. Next change: 13:20, the five-hour reset, at which the value is `0.39`:
the week's loss has grown with the 200 minutes that passed, and the fresh
five-hour window loses nothing.

The same account with the five-hour window reached:

| Moment | Vigor | Why |
|---|---|---|
| Now | 0 | the five-hour gate is reached; nothing can be spent |
| 13:20 | 0.39 | computed on the predicted five-hour window; the week has 4,120 minutes left, so its loss is 0.39 |

A Codex Subscription with 70 % of its week used and 24 hours to its reset:
`r = 0.30`, `t / T = 0.14`, loss `0.16`, five-hour window on pace, Vigor
`0.16`.

A Kimi Code Subscription 26 days into its 30-day cycle, 40 % of the month's
Kimi Code share used, its five-hour window 70 % used with an hour to go:

| Window | r | t / T | loss | weight | contribution |
|---|---|---|---|---|---|
| Five hours, calls | 0.30 | 0.20 | 0.10 | not summed | shown only |
| Month, Kimi Code share | 0.60 | 0.13 | 0.47 | 1 | 0.47 |

Vigor `0.47`: most of a month's coding allowance expires in four days. The
five-hour window counts calls, so it is shown and not summed, though reaching
it would block. The month's total across all products has the same length
and is shown, not summed.

The Radar then reads, highest first: Kimi Code `0.47`, Claude `0.37`, Codex
`0.16`. With the five-hour window of the Claude account reached instead:
Kimi Code `0.47`, Codex `0.16`, Claude `0` now and `0.39` at 13:20.

## Requirements

All requirements are proposed and New. `unit` denotes deterministic tests with
fixed reports, clock and profile. `scenario` denotes reviewed cases comparing
computed values and rankings with the owner's choices. `probe` and `live`
belong to the Drivers' own specifications for the reports they deliver.

| ID | Requirement | Origin | Verified by |
|---|---|---|---|
| SGM-1.1 | Compute Vigor in Arbol from a Subscription's last usage report and the clock; Drivers deliver windows and never a Vigor | New | unit |
| SGM-1.2 | Take into the sum only windows whose resource is tokens or credits and whose used share, length and reset time are known; show the others | New | unit |
| SGM-1.3 | Compute each window's loss as the share expiring unused at the window's even pace, never below zero | New | unit |
| SGM-1.4 | Combine losses as the sum capped at 1, with the longest window weighted 1 and each shorter window by its share of the longest window's allowance, using the placeholder until a learned weight is approved | New | unit |
| SGM-1.5 | Treat a Subscription with a reached inference-gating window and no overage as blocked, whatever that window counts, a tool-scoped window excepted; report its Vigor as 0 and carry its recovery: the next change's moment and value | New | unit |
| SGM-1.6 | Carry with every result the earliest reset among the windows and the Vigor at that moment, computed on the predicted windows | New | unit |
| SGM-1.7 | After a reset passes without a newer report, predict a fresh window, mark the prediction on the window and the result, and drop every prediction when a report arrives | New | unit |
| SGM-1.8 | Mark a result stale when its report is older than the Subscription's shortest token window, and show the report's age | New | unit |
| SGM-1.9 | Show unknown with its reason, telling a missing field in an `ok` report apart from an unsupported family, a sign-in need, an unreachable vendor and no report yet; never substitute zero | New | unit |
| SGM-1.10 | Record every calculation with its inputs, weights, profile version, per-window losses, result, state and next change, and every report as it arrives with its run | New | unit |
| SGM-1.11 | Learn gate weights from consecutive report pairs around one run, version them as a profile, and replace the placeholder only after calibration is approved | New | unit, scenario |
| SGM-1.12 | Roll up per Subscription, sorted by Vigor, with unknown Subscriptions kept visible; the headline is the maximum named with its Subscription; never sum across Subscriptions | New | unit |
| SGM-1.13 | Answer a read of every Subscription's current Vigor without contacting any vendor | New | unit |
| SGM-1.14 | Recompute when a report arrives, when a reset passes and when the clock advances by the display's interval; replay a changed formula over recorded reports | New | unit |
| SGM-1.15 | Keep Vigor advisory: it never routes a Turn, changes a binding or spends allowance | New | unit |

## Interface

A logical data contract; storage, scheduling, the `arbol-cli` verb and UI
layout are outside this draft. The usage report stays the Driver Contract's.

| Record | Required contents |
|---|---|
| Window | Kind, label, resource, used share, reset time, length, reached flag, predicted flag, source report id |
| Report | Subscription, outcome, fetched time, windows as delivered, `extra` as delivered, arrival time, producing run if any |
| Profile | Version, approval state, pace assumption, gate weights per family and window with placeholder or learned marking, stale rule |
| Result | Subscription, moment, report id, profile version, per-window loss and contribution, Vigor or null, blocked, stale with report age, unknown with reason, next change moment and value |
| Rollup | Moment, every Subscription's result, headline value and Subscription |

Reject a weight outside `[0, 1]`, a store weight other than 1, a nonpositive
length, a reset time before the report's fetch time, and a profile version the
calculation does not know. A window of an unknown resource is shown and not
summed. A used share below 0 marks the window unknown with the field named; one
above 100, which Claude reports when an account spends overage, counts as
100 with the raw value kept.

The Driver Contract's window carries `resource`, `tokens`, `credits` or
`calls`, since DRV-1.27 (SGM-D24), and every installed Driver reports it
where its vendor states a unit. Codex leaves it absent, since the app server
names none; the calculation treats a window without the field as tokens and
says so on the result.

## Known problems and calibration

No scorer is implemented. The even pace is a reference, not a forecast: it
says how far behind an even spend the owner is, which is stable and
explainable, and it will overstate the loss for someone who spends in bursts
and understate it for someone who stops. The learned ratio and the owner's
own recent pace are the two refinements on record; neither replaces the even
pace before calibration against the owner's choices.

The report is a floor. Other devices on the same account spend between
reports, so a stale result can show more allowance than exists. An Anthropic
report refreshes only through a run; version 1 read the vendor's usage page
in a hidden browser session for this, and that reading was deliberately
dropped with the Driver's browser (see the Claude Driver's
[CLD-1 Subscriptions](../../arbol-claude-driver/specs/01-subscriptions.md)). A
cheap run would refresh the report at the cost of allowance; whether to offer
that is not decided here.

The Claude Driver maps the five-hour and seven-day windows only. The stream
carries no model-specific weekly window: probed on 26 October 2026 with the
test account on the `max` plan and Claude Code 2.1.304, `unifiedWindows` holds
`five_hour` and `seven_day` and nothing else (SGM-D26). Should the tool add a
model-scoped key, the Driver maps it as a further `weekly` window scoped by
model with `tokens`, and Vigor takes it like any other token window.

The placeholder weight `0.1` is a guess from one vendor's published limits
applied to every gate of every family. Calibration needs report pairs with no
other device active, which the record cannot tell apart on its own; the
learning procedure must mark pairs it cannot trust.

Logging every calculation at a one-minute display interval for four
Subscriptions is a few thousand small rows a day. If that proves too much,
the cheaper rule is to log when inputs change and at least hourly otherwise;
that is a profile choice, not a reason to lose records.

## Decisions

Open proposals support discussion and examples only. They do not approve a
profile for operation.

| ID | Question | Proposed answer | Outcome |
|---|---|---|---|
| SGM-D14 | Where is Vigor computed? | In Arbol's Radar layer, from the Driver Contract's usage report and the clock; Drivers deliver complete windows and never a Vigor | Decided by the owner, 2026-10-26 |
| SGM-D15 | Do shorter windows count, and how much? | Yes: every token window's loss counts, weighted by its share of the longest window's allowance; placeholder `0.1` for every gate until a learned weight is approved | Decided by the owner, 2026-10-26; the placeholder's value is a placeholder, calibration open |
| SGM-D16 | What does a blocked Subscription show? | `0`, with its recovery beside it: the moment the reached window resets and the Vigor at that moment | Decided by the owner, 2026-10-26: zero, with the information when it recovers |
| SGM-D17 | What pace does the loss assume? | The window's even pace first; learn the gate-to-store ratio from recorded report pairs as the second step, for the weight and for an "unavoidable even at full tilt" figure | Decided by the owner, 2026-10-26 |
| SGM-D18 | Who owns the cross-Subscription view, and what is its headline? | The Radar; the headline is the highest Vigor named with its Subscription, the list beneath; never a sum. The first version computes, logs and answers a read, and displays nothing in radar-stats | Decided by the owner, 2026-10-26 |
| SGM-D19 | How is unknown shown? | Always visibly with its reason; a missing field is named as a Driver defect, an unsupported family as a known gap | Decided by the owner, 2026-10-26 |
| SGM-D20 | How does the owner recalculate by hand, and what happens after a reset with no report? | An explicit `usage` fetch replaces predicted windows; after a reset without a report the window is predicted fresh and marked predicted | Decided by the owner, 2026-10-26 |
| SGM-D21 | Where does this specification live? | As SGM-1 beside SGM-0 in the sagas folder, with glossary entries Vigor and Subscriptions Vigor | Decided by the owner, 2026-10-26 |
| SGM-D22 | What is logged? | Every calculation and every report arrival, with full inputs and outputs, in Arbol's database | Decided by the owner, 2026-10-26 |
| SGM-D23 | Where does Kimi Code's report come from? | `GET https://api.kimi.com/coding/v1/usages` through the Pi Driver with the token it already holds; the Console gateway and hidden-browser page reading are not used | Decided by the owner, 2026-10-26; adopted the same day in SYL-288 and installed as Pi Build 5 |
| SGM-D24 | Which windows take part, and how does the calculation know? | Only tokens and credits; `resource` on the Driver Contract's window says which. Until every Driver reports it, exclude the Claude Driver's z.ai window labelled `MCP` and treat the rest as tokens | Decided by the owner, 2026-10-26: added to the contract as DRV-1.27 and DRV-D46; reported since Claude Build `d`, Codex Build `9` (absent, no unit) and Pi Build `6` (SYL-290 to SYL-292, 27 October 2026) |
| SGM-D25 | Which of several equal-length longest windows is the store? | The one scoped to the coding product the Subscription serves; the others of that length are shown and not summed | Open; proposed default in use |
| SGM-D26 | Do model-specific weekly windows of the Anthropic family enter the report? | Add them scoped by model if the stream reports them; not verified | Settled by a probe, 2026-10-26 (SYL-290): the stream reports none; `unifiedWindows` carries `five_hour` and `seven_day` only, for the test account on the `max` plan with Claude Code 2.1.304, so nothing enters the report today. The proposal stands for a tool version that adds a model-scoped key: the Claude Driver maps it as a further `weekly` window with `tokens`. Record: `~/Artifacts/arbol-claude-driver/research/anthropic-rate-limit-windows-probe-2026-10-26.md` |
| SGM-D27 | Which reached windows block a Subscription? | Every window that gates inference, whatever it counts, so Kimi's five-hour window of calls blocks; a window scoped to one tool, such as z.ai's MCP count, does not | Open; proposed default in use |
