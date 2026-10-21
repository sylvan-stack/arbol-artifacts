---
role: authored
spec: SGM-0
status: draft
---
# Sagas · 00 Priority, Need Attention, Readiness and Momentum

## Purpose

Specify how the Radar explains which work is important, which work needs the
owner now, which work can begin, and which next action is worth taking.
The specification defines evidence and agent assessment before arithmetic:
an exact formula is useful only when its inputs have an agreed meaning.

On 21 October 2026 the owner requested these four metrics and agreed with the
general direction of action-based attention, readiness checks and combined
Momentum. Exact estimates, coefficients and thresholds remain proposals.
Only the priority labels and sibling comparison rule are settled here.
The [Decisions](#decisions) table distinguishes that agreement from open choices.

## Scope

The same rules apply to Sagas, sibling Arcs and sibling Beats. This document
owns the proposed calculations, assessment rubric, aggregation, uncertainty
and explanations of these four metrics. It does not replace the existing
[Radar statistics](../../mycel/operations/radar-stats.md), change the
[rules for taking work](../../mycel/operations/sagas.md#taking-the-next-beat),
or authorize an action merely because it has a high score.

The first version recommends actions. It does not automatically change
priorities, accept requirements, resolve questions, start agents or send
notifications. Momentum is a recommendation score, not measured throughput
or a claim about economic value. Existing progress and Velocity remain
separate observations.

**Contents:** evidence and assessments · Priority · action discovery · Need
Attention and its inputs · Readiness · Momentum · aggregation and updates ·
examples · requirements · interface · limitations · decisions.

## Behaviour

### Evidence, assessment and calculation

Keep three things separate:

| Layer | Responsibility | Example |
|---|---|---|
| Evidence | Read current authoritative records and retain a locator, revision and observation time | A named Beat waits for an unanswered decision |
| Assessment | Apply the rubric to those records, identify the applicable category and explain the causal link | The decision blocks that Beat's next step |
| Calculation | Deterministic code maps categories to values, evaluates formulas and aggregates results | `work_blocked` maps to the candidate Impact value `0.75` |

An agent never chooses a final score, invents a decimal confidence, or uses
general impressions such as "seems important" as evidence. Its assessment
contains the selected category, the source facts, the rule applied and one
sentence explaining what changes if the owner acts. A category mapping is
policy, not an estimate made anew by each agent.

Explicit owner decisions govern priority and preferences. Requirements and
accepted decisions come from their authoritative originals. Status,
assignments and dependencies come from their authoritative work records;
live holds and agent records establish current execution conditions.
A copied document or unresolved thread is read through its latest amendment
or answer before it contributes a pending action.

For each input distinguish `known`, `unknown`, `conflicting` and `stale`.
Only `known` supplies a value. A known absence, such as a verified absence
of an action deadline, can supply zero where the rule says so. An unread
source cannot. Record whether a known value was observed directly or was
assessed by applying the rubric; an assessment does not become an owner decision.

If two categories remain plausible after reading the evidence, retain the
ambiguity and the missing fact. Do not average their values, silently choose
the lower one, or send every ambiguity to the owner. First seek the fact in
the source. Ask the owner only for a choice or preference the sources cannot
settle. Proposed assessment automation is SGM-D2.

### Priority

The owner assigns `low`, `medium`, `high` or `critical`. An agent can propose
a change with a reason; it cannot assign or change an accepted priority on
its own. Missing priority is `unknown`, not `medium`.

Priority compares siblings. In a flattened priority-only view, compare the
path lexicographically: Saga first, then Arc within that Saga, then Beat
within that Arc. A high-priority Arc in a low-priority Saga never outranks an
Arc in a high-priority Saga on Priority. A descendant does not alter its
ancestor's priority. Equal labels retain the owner's explicit sibling order,
then stable identifier order if no such order exists. Unknown priorities
remain visibly unranked. Do not infer labels from existing list positions.

Need Attention and Momentum can order siblings differently because they
consider current circumstances. This does not rewrite Priority. Current
list ordering remains authoritative for taking work until a later accepted
implementation explicitly changes it.

### Find the next actions before scoring

An action is a specific unfinished request or intervention with a named
scope and next actor: answer a question, decide between documented options,
review a result, resolve a named problem, or start/delegate ready work.
It has a stable identity derived from the source request, not from its title.

`NeedsYou` is 1 when current evidence establishes that the owner must act
next, or that an explicit outstanding request is directed to the owner.
It is 0 when no owner action is pending, someone else owns the next step,
or the work can proceed automatically without an owner choice. Unclear
ownership is unknown. A question written by the owner may await another
person's answer; it does not automatically need the owner's attention.

A ready unheld Beat creates a start/delegate action only when starting it
actually requires the owner's choice or assignment. No action is invented
just to raise a score. A healthy running agent creates no attention demand
by itself. A watch signal is evidence to investigate, not proof that the
owner is the necessary next actor.

The same request linked from a Beat, Arc and Saga is one action, shown at
each relevant level without being counted repeatedly. Rewording or copying
it preserves its identity and waiting age. Completion removes the action;
a genuinely new request after completion gets a new occurrence. A completed
unit can still contain a real follow-up action, but its completed execution
work does not become ready again.

### Need Attention

For an action `a`, using a single observation time `t`:

```text
N(a) = 100 × NeedsYou(a) × [wI × I(a) + wU × U(a) + wL × L(a) + wW × W(a)]
```

The weights are nonnegative and sum to 1. Candidate profile for discussion:
`wI = 0.50`, `wU = 0.25`, `wL = 0.15`, `wW = 0.10`. These are not approved
operational defaults. Impact has the largest proposed share so a small,
old request does not win merely by waiting. Priority is not an input here;
it enters Momentum once.

If `NeedsYou = 0`, `N = 0` without assessing irrelevant inputs. Otherwise
every required input must be known for an exact result. Never renormalize
the weights around missing inputs: that would change the meaning of scores.

#### Impact: choose a supported category

Impact describes the present consequence of leaving this particular action
undone. It does not estimate the total value of the Saga or repeat Priority.
The following categories and mappings are proposed in SGM-D3:

| Category | Candidate I | Evidence needed |
|---|---:|---|
| `start_available_work` | 0.25 | Named ready work is unheld; starting or delegating it requires the owner; no stronger consequence is established |
| `requested_input` | 0.50 | An outstanding owner review, decision or answer is requested, while the relevant work can proceed under an explicit valid default or other established path |
| `work_blocked` | 0.75 | A named next step cannot proceed until this owner action is resolved; cite the blocking relation or explicit statement and the affected step |
| `current_harm` | 1.00 | A verified current failure, loss or harmful outcome requires this intervention; cite both the observed harm and why the action can address it |

Choose the highest category whose defining consequence is established.
If evidence conflicts about whether work is blocked or harm is occurring,
the assessment is conflicting until reconciled. A speculative worse outcome
does not qualify as current harm. A critical Priority, long transcript,
high token consumption, old ticket or missed deadline alone does not prove
current harm. An overdue action affects Urgency through its recorded deadline.
An action not covered by the rubric remains unclassified; do not force it
into the nearest category.

#### Urgency: calculate from a real action deadline

```text
U(a) = clamp(1 - (dueAt(a) - t) / H(type(a)), 0, 1)
```

`dueAt` is the recorded time by which this action needs a response, not a
guessed project completion date. `H` is an agreed positive warning interval
for that action type. At or after the deadline, Urgency is 1; at least `H`
before it, Urgency is 0. There is no agreed `H` table yet (SGM-D4).

When the current source inventory establishes that no action deadline
exists, `U = 0` and `H` is unnecessary. An unavailable deadline source is
unknown. A date without a time uses the authoritative source's explicit
time-zone and date convention; if it has none, normalization is unresolved.
A Saga delivery date becomes an action deadline only through a recorded
latest-response time or an agreed scheduling rule. An agent's invented
duration cannot silently create that deadline.

#### Unlock: count work that would become available

```text
n(a, outcome) = largest jointly startable set of otherwise-ready Beats
               immediately released by that outcome
n(a) = minimum n(a, outcome) across the documented possible outcomes
L(a) = min(n(a) / K, 1)
```

`K` is a positive integer in the agreed profile. A candidate cap is 3
(SGM-D5), to limit how much volume can dominate the ranking; it is not yet
an operational default. The count is mechanical once outcomes and dependency
edges have been established:

1. Follow explicit, current blocking edges from the action. Never invent
   dependencies from similar wording or general architectural relevance.
2. Keep only unfinished eligible next Beats for which that outcome removes
   the last blocker and every other readiness check passes now. Count each
   Beat once, not its ancestors, steps or distant successors.
3. Respect mutual territory conflicts and resource limits across the set.
   Three Beats that could only run one after another are not three immediate
   parallel starts. The scorer need only find up to `K` jointly startable
   Beats because the contribution saturates there.
4. For a decision with several possible outcomes, compute each documented
   outcome and use the minimum. This is a conservative opportunity count,
   not a prediction of which option the owner will choose. Record the counts
   by outcome so the restriction is visible.

A complete graph with no immediately released Beat gives `n = 0`. Missing
dependency/readiness data or an incomplete outcome set gives unknown.
For an outcome that cancels work, the canceled Beats do not count as starts.
Unblocking value can cross Saga boundaries without changing either Saga's
Priority. Whether the conservative minimum loses too much useful information
is explicitly open in SGM-D5.

#### Waiting: calculate the time awaiting the owner

```text
W(a) = clamp(ownerWaitingSeconds(a) / T(type(a)), 0, 1)
```

`T` is an agreed positive response interval by action type. There is no
agreed table yet (SGM-D4). Use elapsed wall-clock seconds in recorded
intervals when the same request was outstanding and the owner was the next
actor. Exclude intervals assigned to someone else and explicit deferrals.
A future owner deferral suppresses the action until its recorded resumption
time; editing or duplicating the request does not restart its clock.
If a deferral conflicts with a hard deadline, surface the conflict rather
than quietly suppressing it. No timestamp or missing interval history means
unknown. First discovery by the scorer is not the request's creation time.

### Readiness

Readiness is relative to a declared scope and intended action. The proposed
first version is `ready` (100), `blocked` (0), `unknown`, or `not_applicable`.
It is not a subjective percentage of how prepared the work feels.

```text
R(a) = 100 × Requirements(a) × Questions(a) × Dependencies(a) × Availability(a)
```

Each applicable gate is pass, fail or unknown. Any known fail makes the
action blocked, even if another gate is unknown; preserve all reasons. All
passing gates make it ready. Otherwise it is unknown. A gate may pass as
not applicable only with a reason specific to this action type. Completed
or canceled execution work is not applicable, not 100% ready.

| Gate | Pass rule | What the agent must not infer |
|---|---|---|
| Requirements | The intended scope, its governing requirements and a checkable Done when are recorded; the assessment maps them to the planned work and finds no unresolved contradiction | A long document or checked plan is sufficient proof of completeness |
| Questions | No unresolved question blocks this scope; every relevant open question is classified as blocking, explicitly nonblocking, or unknown with evidence | No discovered question means none exists when the inventory is incomplete |
| Dependencies | All required inputs and predecessors for this action are satisfied in current authoritative records | An old Done label proves a changed prerequisite is still satisfied |
| Availability | A capable next actor and required resources are available and no incompatible territory hold prevents this action | A free process slot establishes capability, or an occupied environment blocks every possible action |

Requirements is a bounded assessment, not proof that no requirement could
ever be discovered. The agent lists the scope and sources inspected, the
requirement-to-work mapping, omissions and contradictions. An incomplete
inventory yields unknown. An accepted specification can supply the governing
requirements, but still needs a match to the proposed scope. Missing required
documents are a known failure; inability to read them is unknown.

To make this assessment repeatable, check the following for the particular
action. Each check records pass, fail or unknown and the supporting source:

| Check | Implementation action | Decision or review action |
|---|---|---|
| Bounded result | Named intended behaviour, scope boundaries and relevant constraints | One question or review target, the decision authority and the result requested |
| Necessary inputs | Governing requirements and required interfaces, artifacts and predecessor results are identified | Current facts and applicable owner criteria are identified; missing facts that could change the choice are named |
| Observable completion | Every in-scope requirement maps to a stated observable result and a possible verification method | The answer or review outcome can be recorded unambiguously and its affected work is identified |
| Alternatives and ambiguity | No unresolved interpretation changes the required behaviour; necessary technical choices are either delegated or settled | Viable options or a concrete proposal are described with their material consequences and a recommendation tied to the stated criteria |
| Coverage | Every governing requirement in the declared scope is mapped; omissions and exclusions are explicit | Every explicitly requested question is covered; unresolved uncertainty is either nonblocking by an explicit rule or still a blocker |

The agent may identify a missing edge case or ambiguity, but must give a
concrete competing interpretation and the different outcome it would cause.
"The specification could be more detailed" is insufficient to fail a check.
Conversely, "looks complete" is insufficient to pass it. This is a review
of the stated scope; it never claims exhaustive knowledge of every possible
future requirement. The gate passes only when every applicable check passes.

For implementation, an unanswered blocking decision fails Questions. For
the action "answer this decision", the unanswered decision is the action
itself, not its own blocker. That action passes only when the question,
options and consequences are prepared well enough for the owner to decide,
and the other applicable gates pass. An agent cannot rename an unprepared
decision "investigate" merely to make Momentum positive; investigation must
be an independently supported next action with a defined result.

For a parent ready to begin additional execution work:

```text
R(parent) = OwnGates(parent) AND ANY Ready(eligible next child)
```

Use three-valued logic: a known ready child proves the ANY condition despite
unknown siblings; if none is ready and the child inventory or any candidate
is unknown, ANY is unknown; a complete inventory with no ready candidate is
false. Apply the parent's own gates afterward. An incomplete decomposition
is unknown, not an empty ready set. A completed parent is not applicable.

This is readiness to begin an identified part of the work, not a promise
that every future child is specified. The owner must settle this scope
interpretation in SGM-D6. Show the ready child and blockers in the UI.
An already-held execution action is unavailable for a new worker; continuing
it by its holder is a different action and does not require releasing its
own hold. Readiness is a snapshot, not a reservation: recheck before taking work.

### Momentum

For unit `u` and each of its outstanding owner actions `a`:

```text
M(u, a) = p(priority(u)) × N(a) × R(a) / 100
Momentum(u) = max M(u, a)
```

Candidate Priority weights: `low = 0.4`, `medium = 0.6`, `high = 0.8`,
`critical = 1.0` (SGM-D7). These encode a proposed preference strength, not
an objectively measured ratio of value. Unknown Priority prevents an exact
positive Momentum score; a known zero Attention or blocked action still
establishes zero regardless of its weight.

Use only `priority(u)` at the tier being ranked. At Saga level, compute all
candidate action scores using that Saga's priority; do not import already
weighted Arc scores. At Arc level, compare sibling Arcs using their own
priorities. A flat action list must retain its Saga and Arc grouping; there
is no cross-parent comparison of local weights.

The action that supplies the maximum is displayed with Momentum. Never
multiply the highest Attention from one action by the Readiness of another.
A Saga can have implementation Readiness 0 and positive Momentum for an
answer or review that is ready. This action-based interpretation, rather
than a literal product of the three Saga-level display fields, is open in
SGM-D8. It must be clear to the user before adoption.

Existing progress does not add a Momentum bonus. A healthy running Saga
may need no owner action. If the owner wants delivery progress to enter the
formula as well, that needs a separate definition; token rate and checked
steps are not automatically a measure of the benefit of intervention.

### Aggregate, explain and update

`NeedAttention(u)` is the maximum `N(a)` across its unique outstanding
actions and descendant actions. `Momentum(u)` is the maximum calculated
above. A complete, checked inventory with no owner action yields zero.
Keep a pending-action count for explanation, not as a score multiplier.

If any relevant candidate is unknown, conflicting or stale, show the known
maximum as a **lower bound**, with the incomplete status and unresolved
candidates. Do not claim it is the exact aggregate or sort an unknown as
zero. A known score of 100 already proves the bounded maximum, but the
incomplete coverage remains visible. Unknown items have a visible assessment
queue, not fabricated attention scores.

Rank exact scores by their unrounded value. Ties retain explicit sibling
order, then stable identifier order. Display at most one decimal and never
describe a score as a probability. No relative normalization against the
current list: removing another Saga must not change this one's score.

Recompute on a changed action, answer, priority, scope, requirement,
dependency, hold, resource, deferral or scoring profile. Time-based inputs
are recomputed at observation time. Retain assessments while their referenced
facts are unchanged; do not ask a model to rerate unchanged text on each
refresh. Re-read current evidence when a change invalidates it. A failed
refresh marks affected inputs stale instead of preserving an exact live score.
Every result records its observation time and profile version.

Show the selected action, the four Attention contributions, Priority weight,
readiness checks, sources, unresolved facts and why the score changed. Keep
the UI explanation short, with details available on request. Assessments
can be corrected without changing the underlying source facts; both versions
remain attributable. Owner corrections govern later matching assessments.

### Worked examples and checks

These are fictional calculations under the candidate coefficients, not
operational measurements or an approved response-time policy. All named
inputs in the table are assumed verified; `R` is readiness of the action.

| Case | Priority | NeedsYou | I | U | L | W | R | N | M |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Healthy autonomous work; no owner request | critical | 0 | — | — | — | — | — | 0 | 0 |
| Ready work needs a launch decision; newly requested | low | 1 | 0.25 | 0 | 0 | 0 | 100 | 12.5 | 5 |
| Prepared blocking decision; no deadline, no released next Beat yet, half its response interval spent | high | 1 | 0.75 | 0 | 0 | 0.5 | 100 | 42.5 | 34 |
| Same decision, but the options needed for the answer are missing | high | 1 | 0.75 | 0 | 0 | 0.5 | 0 | 42.5 | 0 |
| Current harm; action overdue, reaches the unlock cap and waiting cap; response is ready | low | 1 | 1 | 1 | 1 | 1 | 100 | 100 | 40 |

In the blocking-decision example, current unfinished work is paused, but no
otherwise-ready *new* Beat is released, so Impact and Unlock legitimately
differ. Implementation Readiness can remain 0 while the decision action has
Readiness 100. In the fourth case the item remains visible through Need
Attention; a real preparation action can be proposed separately.

With a fictional `H = 24 hours`, a deadline 6 hours away gives `U = 0.75`.
With a fictional `T = 48 hours`, 12 recorded hours awaiting the owner gives
`W = 0.25`. These values illustrate the equations, not proposed defaults.

Conformance examples must also cover: sibling-only Priority; missing
Priority; a low-priority request above healthy critical work; duplicate
requests; conflicting assignments; stale requirements; unknown time policy;
answered questions; an occupied territory; several outcomes with different
unlock sets; mutually overlapping Beats; a partially known parent; a
high-Attention blocked action beside an unrelated ready action; terminal
execution with an outstanding follow-up; and an explicit deferral.

## Requirements

All requirements are proposed and New. `unit` denotes deterministic tests
with fixed evidence, rubric outputs, configuration and time. `scenario`
denotes reviewed cases testing the assessment rubric against source evidence;
it is not a vendor live test or a claim of statistical accuracy.

| ID | Requirement | Origin | Verified by |
|---|---|---|---|
| SGM-0.1 | Compare owner-assigned Priority only among siblings; preserve unknown labels and ancestor precedence in priority-only views | New | unit |
| SGM-0.2 | Keep evidence, categorical assessments and deterministic arithmetic separate; retain source revisions and reasons | New | unit, scenario |
| SGM-0.3 | Discover concrete owner actions, reconcile later replies and deduplicate the same source request across the hierarchy | New | unit, scenario |
| SGM-0.4 | Apply the NeedsYou gate and Impact rubric without inventing ownership, deadlines, harm or dependencies | New | scenario |
| SGM-0.5 | Calculate Urgency, Unlock and Waiting exactly from the defined facts and a versioned, complete profile | New | unit |
| SGM-0.6 | Preserve unknown, conflicting and stale inputs; never substitute zero or renormalize around missing evidence | New | unit |
| SGM-0.7 | Evaluate action Readiness and parent readiness with the defined gates, scope and three-valued rules | New | unit, scenario |
| SGM-0.8 | Calculate Momentum using the same action's Attention and Readiness and only the compared unit's Priority | New | unit |
| SGM-0.9 | Aggregate by maximum, expose partial lower bounds and retain unknown candidates visibly | New | unit |
| SGM-0.10 | Explain the selected action and contributing evidence; retain profile versions, corrections and change reasons | New | unit, scenario |
| SGM-0.11 | Recompute changed facts and time inputs, invalidate stale assessments, and preserve unchanged assessments | New | unit |
| SGM-0.12 | Keep the scorer advisory; do not convert a draft profile or high score into permission to execute or change priorities | New | unit, scenario |
| SGM-0.13 | Preserve request identity and waiting intervals across edits, duplicates, reassignment, deferral and reopening | New | unit |
| SGM-0.14 | Calibrate categorical assessments and ranking choices independently before accepting an operational profile | New | scenario |

## Interface

This is a logical data contract; storage paths, APIs, scheduling and UI layout
are outside this draft. The existing work records remain authoritative.

| Record | Required contents |
|---|---|
| Unit | Stable id, tier, parent, lifecycle, Priority with owner/source, sibling order, declared scope, applicable requirements and child-inventory coverage |
| Action | Stable request and occurrence ids, source unit and linked units, type, intended result, next actor, source request, current state, owner-wait intervals, deadline if present, deferral if present, possible outcomes and their dependency edges |
| Input assessment | Input name, known/unknown/conflicting/stale status, observed/assessed method, category or factual value, source locators and revisions, observation time, assessor, rule/profile version, rationale, unresolved facts and superseded assessment id |
| Profile | Version, approval state, Impact category map, Attention weights, Priority weights, positive warning/response intervals by supported action type, positive integer Unlock cap |
| Result | Unit and action ids, observation time, profile version, input contributions, readiness gate results, exact score or null, lower bound if partial, coverage, winning action(s), missing facts and explanation |

Reject negative/out-of-range weights, an Attention weight sum other than 1,
nonpositive intervals, a nonpositive/noninteger cap, unknown categories and
incompatible profile versions. Require Priority weights in `(0, 1]`, strictly
increasing from low to critical, with critical equal to 1. An unknown action
type requiring an interval produces an unconfigured input. Do not invent
intervals or silently enable omitted terms. Review-only profiles may run
labelled examples but cannot be presented as an approved operational score.

## Known problems and calibration

No automated scorer for these four metrics is claimed here. Current sources
do not necessarily record action ownership, exact waiting intervals, response
deadlines, complete outcome sets or requirement coverage in structured form.
Extracting them is work whose gaps must stay visible.

Two agents may disagree about whether a requirement is sufficiently defined
or an answer truly blocks progress. For a proposed profile, have two
independent assessments of the same fixed examples, then compare the chosen
categories and their evidence. These are a future validation procedure, not
agents started by drafting this file. Resolve disagreements by improving the
rubric or source data before changing arithmetic weights.

Separately compare the computed ranking with the owner's choices between
specific next actions, including healthy critical work, low-priority available
work, blocked decisions and unknown evidence. Record why a ranking differs.
Do not tune away an extraction error with a weight change. Version an accepted
profile and retain the previous one with its examples; changes do not rewrite
historical results. Sample size and acceptance criteria remain open (SGM-D9).

The conservative Unlock count may undervalue a consequential decision with
one outcome that cancels work. A binary Readiness hides preparation progress,
so show the checklist. Action Momentum differs from implementation Readiness
and requires an explicit action label. The owner may prefer a simpler initial
profile with fewer terms; disabling a term is an explicit profile decision,
not a response to missing data (SGM-D10).

## Decisions

Open proposals support discussion and examples only. They do not mark the
specification accepted or approve the numerical values for operation.

| ID | Question | Proposed answer | Outcome |
|---|---|---|---|
| SGM-D1 | What are Priority's labels and comparison scope? | Low, medium, high, critical; compare siblings, with ancestors taking precedence in priority-only views | Decided by the owner, 2026-10-21 |
| SGM-D2 | Can an agent's evidence-backed classification feed the score without approval for every assessment? | Yes, visibly assessed and correctable, when exactly one rubric category is supported; ambiguity stays unknown. Only owner preferences and policy choices require the owner | Open |
| SGM-D3 | Do the Impact categories and Attention weights match how much intervention matters? | Use the four stated categories and candidate 0.50/0.25/0.15/0.10 weights in examples; approve after reviewing contrasting cases | Open |
| SGM-D4 | What warning and response intervals apply to each action type, and what time conventions apply? | Set an explicit table from expected response times and examples; use recorded elapsed waiting intervals. No inferred per-action intervals or operational defaults yet | Open |
| SGM-D5 | How should Unlock value alternative outcomes and parallel capacity? | Count immediate otherwise-ready, jointly startable Beats; use the minimum across documented outcomes and a candidate cap of 3. Review whether this is too conservative | Open |
| SGM-D6 | Does Saga/Arc Readiness mean all future work is specified, or that a defined next portion can begin? | Parent gates plus one ready eligible next child; show that child's scope and do not imply all future work is specified | Open |
| SGM-D7 | How strongly should Priority influence Momentum? | Candidate weights low 0.4, medium 0.6, high 0.8, critical 1.0; calibrate as preferences rather than measured value | Open |
| SGM-D8 | Can a Saga have positive Momentum for a prepared decision while implementation is blocked? | Yes: compute per action, show the action, and keep implementation Readiness separate | Open |
| SGM-D9 | What validation makes a scoring profile ready to adopt? | Review classification disagreements and the owner's pairwise action choices separately; agree sample coverage and acceptance criteria before production | Open |
| SGM-D10 | Should the first operational profile include all four Attention terms? | Keep the full model documented; consider beginning with Impact and verified deadlines while the data for Unlock and Waiting is established, using a separately approved profile | Open |
