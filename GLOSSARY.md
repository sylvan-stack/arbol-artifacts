# Arbol Glossary

<!-- mycel:cues
literal: section_headings
heading-levels:
  - 2
target-scope: local_section
-->

Authoritative flat-list reference for every first-class term in Arbol. Alphabetical; no grouping. When code, docs, or UI copy disagree with a definition here, rename to match. Each term is a stable anchor — link directly as `GLOSSARY.md#aggregate`, `GLOSSARY.md#turn`, etc.

The installed production authority remains the [Event Log Service](#event-log-service).
Event/replay descriptions below apply to the legacy profile. The implemented
explicit [State Runtime Profile](#state-runtime-profile) has separate current-row
authority; building it does not activate production or authorize retention cleanup.

The Arbol 2 definitions of Arbol, Arbol Root, Arbol Swift App, Arbol Trunk and Exchange Assignment follow the [current architecture](architecture/README.md). Trunk Runtime is retained as a historical term. The other definitions describing legacy processes and Event Log interactions have not been rewritten by that architecture revision.

**Table of Contents**

- **A** — [A-Nex](#a-nex) · [Action Item](#action-item) · [Activity](#activity) · [Activity Execution](#activity-execution) · [Activity Graph](#activity-graph) · [Activation Rule](#activation-rule) · [Admission Boundary](#admission-boundary) · [Agent Attempt](#agent-attempt) · [Agent Record](#agent-record) · [Aggregate](#aggregate) · [Answer Beacon](#answer-beacon) · [Answer Threshold](#answer-threshold) · [Arbol](#arbol) · [Arbol Trunk](#arbol-trunk) · [Arbol Component](#arbol-component) · [Arbol Root](#arbol-root) · [Arbol Internals](#arbol-internals) · [Arbol Secret](#arbol-secret) · [Arbol Swift App](#arbol-swift-app) · [Arbol-Initiated Chat Session](#arbol-initiated-chat-session) · [Arc](#arc) · [Artifact](#artifact) · [Artifact Chapter](#artifact-chapter) · [Artifact Corpus](#artifact-corpus) · [Artifact Space](#artifact-space) · [Attestation](#attestation) · [Authoritative Input](#authoritative-input) · [Authority Epoch](#authority-epoch)
- **B** — [Beat](#beat) · [better-grep](#better-grep) · [Blueprint](#blueprint) · [Blueprint Chain](#blueprint-chain) · [Book](#book) · [Brain Recipe](#brain-recipe) · [Branch](#branch) · [Branch Overlay](#branch-overlay) · [Bridge](#bridge) · [Build](#build) · [Burn](#burn)
- **C** — [Cell](#cell) · [Change Walkthrough](#change-walkthrough) · [Chat Exchange](#chat-exchange) · [Chat Note](#chat-note) · [Chat Session](#chat-session) · [Checkpoint](#checkpoint) · [Chunk](#chunk) · [Chunking](#chunking) · [CLI](#cli) · [Code Corpus](#code-corpus) · [Code Map](#code-map) · [Code Scout](#code-scout) · [Command](#command) · [Communicado](#communicado) · [Communicado Action](#communicado-action) · [Communicado Delivery](#communicado-delivery) · [Communicado Descriptor](#communicado-descriptor) · [Communicado Family](#communicado-family) · [Communicado Presentation](#communicado-presentation) · [Communicado Species](#communicado-species) · [Communicado State](#communicado-state) · [Companion](#companion) · [Completion](#completion) · [Corpus](#corpus) · [Corpus Watcher](#corpus-watcher) · [Coupling](#coupling) · [Cue](#cue) · [Cue Channel](#cue-channel) · [Cue Command](#cue-command) · [Cue Detection Catalog](#cue-detection-catalog) · [Cue Target](#cue-target) · [Cue Target Cache](#cue-target-cache)
- **D** — [Decision](#decision) · [Default Arbol Trunk](#default-arbol-trunk) · [Delegate](#delegate) · [Dense Retrieval](#dense-retrieval) · [Derivation](#derivation) · [Design Token](#design-token) · [Detection](#detection) · [Diff](#diff) · [Diff View](#diff-view) · [Draft](#draft) · [Drift](#drift) · [Drift Candidate](#drift-candidate) · [Driver](#driver) · [Driver Instance](#driver-instance)
- **E** — [Effector](#effector) · [Email Source Item](#email-source-item) · [Elma Chat](#elma-chat) · [Elma View Page](#elma-view-page) · [Embedder Profile](#embedder-profile) · [Embedding](#embedding) · [Embedding Provider](#embedding-provider) · [Entity](#entity) · [Entity Card](#entity-card) · [Entity Card Content](#entity-card-content) · [Entity Card Resolver](#entity-card-resolver) · [Entity Chip](#entity-chip) · [Entity Context Menu](#entity-context-menu) · [Entity Edge](#entity-edge) · [Entity Kind](#entity-kind) · [Entity Shape](#entity-shape) · [Entity URI](#entity-uri) · [Env Keepers](#env-keepers) · [Errand](#errand) · [Event Log](#event-log) · [Event Log Service](#event-log-service) · [Event Sourcing](#event-sourcing) · [Exchange Assignment](#exchange-assignment)
- **F** — [Fanout](#fanout) · [Flyer](#flyer) · [Fold / Projection](#fold--projection) · [Font Scale](#font-scale) · [Free-standing](#free-standing)
- **G** — [Generation](#generation)
- **H** — [H-Nex](#h-nex) · [Heartwood](#heartwood) · [Hold](#hold) · [Hunk Review](#hunk-review)
- **I** — [Identity Reconciliation](#identity-reconciliation) · [Ignore Rule](#ignore-rule) · [Index Store](#index-store) · [Ingest](#ingest) · [Initiator](#initiator) · [Instructions Hub](#instructions-hub) · [Intelligence Provider (IP)](#intelligence-provider-ip)
- **K** — [Knowledge System](#knowledge-system)
- **L** — [Ladder](#ladder) · [Leather Bag](#leather-bag) · [Living Topic](#living-topic) · [Load](#load)
- **M** — [Mac OS Communicado](#mac-os-communicado) · [Mandate](#mandate) · [Mycel](#mycel) · [Mycel Operation](#mycel-operation) · [Mycel Skill](#mycel-skill) · [Mycel-enabled](#mycel-enabled) · [Mycel-integrated](#mycel-integrated)
- **N** — [Native Tool Call](#native-tool-call) · [Nex](#nex) · [Nex Colab](#nex-colab) · [Nex Knowledge Map](#nex-knowledge-map) · [Normalizer](#normalizer) · [Now Line](#now-line)
- **O** — [Oaken](#oaken) · [Objectives](#objectives) · [Organization](#organization) · [Origin](#origin) · [Origin Coverage](#origin-coverage) · [Origin Link](#origin-link)
- **P** — [Parse Result](#parse-result) · [Parser](#parser) · [Parser Pipeline](#parser-pipeline) · [Provider](#provider)
- **R** — [Radar](#radar) · [RAPTOR Rebuild](#raptor-rebuild) · [RAPTOR Summarization](#raptor-summarization) · [RAPTOR Tree](#raptor-tree) · [Reference](#reference) · [Refresh](#refresh) · [Release](#release) · [Repo](#repo) · [Repo Folder](#repo-folder) · [Repo Picker](#repo-picker) · [Requirement](#requirement) · [Research Trip](#research-trip) · [Retrieval](#retrieval) · [Root Contract](#root-contract) · [Routine](#routine) · [Runbook](#runbook)
- **S** — [Saga](#saga) · [Scan](#scan) · [Signal](#signal) · [Signal Rule](#signal-rule) · [Signal Type](#signal-type) · [Seqoya Lab](#seqoya-lab) · [Source Ref](#source-ref) · [Sparse Retrieval](#sparse-retrieval) · [Spotlight](#spotlight) · [Stale](#stale) · [Stale Summary Regeneration](#stale-summary-regeneration) · [State Runtime Profile](#state-runtime-profile) · [Steward](#steward) · [Stint](#stint) · [Subscription](#subscription) · [Summary Node](#summary-node) · [Surface](#surface) · [Sync Pass](#sync-pass)
- **T** — [Taproot](#taproot) · [Text Snapshot](#text-snapshot) · [Theme](#theme) · [Tool](#tool) · [Tool Request](#tool-request) · [Tracked Source](#tracked-source) · [Trivial Trunk](#trivial-trunk) · [Trunk Runtime](#trunk-runtime) · [Turn](#turn)
- **U** — [UI](#ui) · [UIShell / Chrome](#uishell--chrome)
- **V** — [Velocity](#velocity) · [Visit](#visit)
- **W** — [Willo Station](#willo-station) · [Working Directory](#working-directory) · [Workload](#workload) · [Workspace](#workspace) · [Workspace Ledger](#workspace-ledger) · [Worktree](#worktree) · [Worktree Container](#worktree-container)

---

## A-Nex

**Agent nex**: the AI agent participant in a continuing [Nex](#nex) partnership, with its capabilities, accumulated context, assigned or agreed goals, responsibilities, and scope for initiative. The `A-` prefix identifies the kind of participant; it does not assign a permanently subordinate role. An A-Nex can contribute expertise, learn context from an [H-Nex](#h-nex), propose and implement solutions, question assumptions, and take initiative within its capabilities and agreed autonomy. Its role can shift between teaching, learning, collaborating, and acting independently as the situation requires.

**Example:** An A-Nex reviews a teammate's pull request, then works through the findings, evidence, and uncertainty with the H-Nex so the H-Nex can explain and stand behind the review.

## Action Item

A durable [Communicado](#communicado) whose common status is `action_required`. It asks the [Leather Bag](#leather-bag) for a bounded decision, input, approval, acknowledgement, or other explicit response. **Action Item is a semantic category and conversational noun, not a separate Entity Kind or persistence record**: a Communicado becomes a current Action Item while its persisted status is `action_required`, and stops being one when its status becomes `resolved`. Opening or dismissing a Presentation does not resolve it.

Action Item and [Spotlight](#spotlight) are orthogonal. Creating an Action Item does not Spotlight it; Spotlighting or removing it does not alter its status; resolving it does not remove an independent Spotlight designation.

**Example:** A pending tool approval is persisted as an `action_required` Communicado and appears in Willo Station's Action Items section until the user approves or rejects it. The user may independently Spotlight that Communicado to keep it visible after resolution.

## Activation Rule

An active, durable listener that evaluates a complex logical expression of atomic events and emits a [Signal](#signal) when its conditions are met. Atomic inputs may be time events such as cron schedules, subscriptions to other Signals with payload analysis, or intermediate **semi-activation flags** that remember one matched event and its timestamp while waiting for another event within a bounded time window.

An Activation Rule is independent of [Stewards](#steward) and [Mandates](#mandate): it stores no foreign key to either and does not directly start an agent. Its emitted Signal payload may contain any data—including Steward or Mandate identifiers. Separate dispatch logic can interpret that Signal to start a Steward and assign or revoke runtime Mandates.

**Example:** A rule remembers `deployment.started`, waits up to 30 minutes for either `deployment.succeeded` or `deployment.failed`, and emits `steward.release.check.requested` with the project and suggested Steward ID only when the resulting condition matches.

## Activity

An independently executable unit of [Arbol Trunk](#arbol-trunk) work with declared required inputs and produced outputs. An Activity may occur before, during, between, or after agent [Turns](#turn); independent Activities may run concurrently as soon as their inputs exist. The full Activity and Activity Graph contracts are under active design.

**Example:** Detecting literal Cues, extracting one Cue Target, invoking an agent, and settling one Tool Request are candidate Activities in an Arbol Trunk.

## Activity Execution

One occurrence of an [Activity](#activity) running with specific immutable inputs. An Activity Execution records its input identities, causal lifecycle, outputs, and failure independently of other executions of the same Activity.

**Example:** Literal Cue detection runs for draft revision 7 and later for the authoritative submitted message; these are two Activity Executions rather than one mutable result.

## Activity Graph

The runtime causal and dependency graph formed by [Activity Executions](#activity-execution) and the immutable inputs and outputs connecting them inside an [Arbol Trunk](#arbol-trunk). The realized graph is dynamic: actual input and Activity output determine which executions and edges exist. Trunk definitions and dependency rules may remain code-owned; the graph that actually ran must be reconstructable from [Event Log](#event-log) facts. Activity Graph does not imply a YAML workflow, a database-configured DAG, or a general-purpose scheduler.

**Example:** Literal Cue detection produces three target-extraction executions; their outputs join at instruction composition before an Agent Attempt starts. Another Exchange with no Cues realizes a smaller graph.

## Admission Boundary

The actual SQL/native permission to accept new domain work for a verified installation and generation. Closing admission records a hold; it does not by itself prove accepted execution, delivery, receiver or cleanup obligations have settled. Reopening requires the owned controller's real authority and exact verification/reopen receipts. See [State Runtime Profile](#state-runtime-profile).

## Agent Attempt

One bounded run by an [Arbol Trunk](#arbol-trunk) to complete the agent-facing part of a [Chat Exchange](#chat-exchange) through one selected [Intelligence Provider](#intelligence-provider-ip) and one concrete [Driver Instance](#driver-instance). “Attempt” names the retry/failover scope; it does not imply that failure is expected. A normal successful Exchange commonly has one Agent Attempt. The Attempt is durably identified and remains pinned to that Driver Instance for invocation, event replay, cancellation, and recovery. It ends in successful terminal response, retry/failover, permanent failure, or cancellation.

An Agent Attempt is not one raw LLM response generation and is not another name for [Turn](#turn). It may contain multiple Turns and Tool Request continuations while using the same recoverable provider/Driver execution. Retry or failover normally starts a new Agent Attempt. Current `active_turn_attempts` and `attempt_id` code are migration material and do not define every future semantic edge case.

**Example:** Claude handles several Bash-result continuations in Agent Attempt 1, then rate-limits; the Trunk opens Agent Attempt 2 on Codex, all within one Chat Exchange.

## Agent Record

The small file that one agent session on this Mac keeps up to date while it lives, whatever tool runs it: who the agent is, which process owns it, what it waits for and since when, and when it ended. Claude Code and Codex write it through their own hooks; an [Arbol Trunk](#arbol-trunk)'s [Chat Exchange](#chat-exchange) takes part through the record it already keeps. The [Radar](#radar) and the holds of [Beats](#beat) read it. Specified in [Agent records](agent-records/README.md).

**Example:** A Codex thread that runs `make` has a record that says it waits for a command since 13:51; when the agent asks which branch to push to, it says it waits for an answer; when the thread is archived, the record gets its end.

## Aggregate

A small per-entity state machine ([Chat Session](#chat-session) / [Turn](#turn) / [Tool Request](#tool-request)). State exists only to guard which event may be appended next. See also: [Event Log](#event-log), [Fold / Projection](#fold--projection).

**Example:** A `Turn` aggregate may allow `USER_MESSAGE_APPENDED` → `IP_STARTED` → `IP_COMPLETED`, but reject a second completion event for the same turn.

## Answer Beacon

The text-free, clickable sunset-horizon image above the [Elma Chat](#elma-chat) Composer that navigates to the [Answer Threshold](#answer-threshold). It appears only while a threshold exists outside the response viewport and disappears as soon as any pixel of that threshold becomes visible.

**Example:** After a long agent tool run pushes the final answer below the fold, clicking the Answer Beacon smoothly scrolls the response to the Answer Threshold.

## Answer Threshold

The text-free sunrise separator marking the transition from an agent's visible thinking and tool activity to its user-facing final answer in [Elma Chat](#elma-chat). It is also the intermediate semantic navigation stop used by response hotkeys and the target of the [Answer Beacon](#answer-beacon).

**Example:** `Cmd+Down` moves from the start of a response to its Answer Threshold before moving to the response end.

## Arbol

The local, single-user macOS application, consisting of one global [Arbol Swift App](#arbol-swift-app) and one backend for each [Arbol Root](#arbol-root) in use. A Root's `arbol` Build supplies its backend and UI renderer bundles; the Swift App hosts those bundles in web views and passes their Bridge calls to that Root's backend. The backend holds listeners, resolves Brain Recipes and calls the Root's manager to start [Arbol Trunks](#arbol-trunk), which run [Drivers](#driver). The command line is also `arbol` and works without a running backend. Roots keep separate chat databases and settings; the Swift App and Drivers are shared. See [components and boundaries](architecture/00-components-and-boundaries.md).

**Example:** Elma Chat opened in First Sapling uses First Sapling's renderer bundle and backend. Its accepted Exchange keeps running in a detached Trunk process when Arbol quits; reopening Arbol discovers the retained Roots and reads First Sapling's database and Exchange records again.

## Arbol Backend

The one process of a Root's `arbol` [Build](#build) that serves the [Leather Bag](#leather-bag)'s windows in that Root: it reads the Root's chat tables, keeps the [Drafts](#draft), sends a message by having `arbol-root` start an [Arbol Trunk](#arbol-trunk), follows the answer as it arrives in the Exchange's folder, and passes stops and answers on. One runs for each Root in use, started by the [Arbol Swift App](#arbol-swift-app). Specified in [BKD-0](backend/00-the-arbol-backend.md).

**Example:** First Sapling's backend listens on `~/Library/Application Support/Arbol/roots/sapling/backend.sock`; an [Elma Chat](#elma-chat) window of First Sapling sends `chat.send` there through the [Bridge](#bridge).

## Arbol Trunk

A complete, versionable implementation of an Arbol communication strategy, named by a *code name* such as `trivial`. Each distinct implementation is a component `arbol-trunk/<code name>`, kept with every other Trunk in the repository `arbol-trunk`, with its own numbered [Builds](#build). It owns one [Chat Exchange](#chat-exchange) from accepted input to its final state, including its chat data. Each Exchange runs in one process, started from a Trunk Build whose list of [Root Contract](#root-contract) versions holds its [Arbol Root](#arbol-root)'s version, and detached when `arbol-root` starts it. Its record retains the `root` and Trunk Build; changing a default or starting another Root never moves accepted work. The Trunk receives the resolved Driver, Subscription, model and effort, and does not choose another route or require Arbol, its Root manager or the database to finish. The inside of the first Trunk, the [Trivial Trunk](#trivial-trunk), is specified separately; the common boundary is [what any Trunk must offer](architecture/00-components-and-boundaries.md#what-any-trunk-must-offer).

**Naming warning:** **Arbol Trunk** is the new architectural term. The established bare [Branch](#branch) term continues to name a Git branch Entity; Arbol Trunk is unambiguous.

**Example:** First Sapling lists a conversational Trunk and a research Trunk whose Builds both list its Root Contract version. The caller picks the research component; First Sapling's Root Build starts that component's newest compatible working Build for this Exchange. A later Exchange in the same Chat Session may use the conversational Trunk.

## Arbol Component

Any runnable instance/process that makes up a running [Arbol](#arbol). Components differ in lifecycle: the **[Arbol Swift App](#arbol-swift-app)** is user-launched (one process per open window); the **daemons** are long-lived and expected to stay up; **[Driver Instances](#driver-instance)** are launched **on demand** by [Arbol Root](#arbol-root), versioned, run side-by-side during a safe rebuild, then drained and garbage-collected; the **CLI** is short-lived (one process per invocation). The full set:

- **[Arbol Swift App](#arbol-swift-app)** — the shell binary backing every window; one process per open [UI](#ui).
- **[Arbol Root](#arbol-root)** — control plane and UI gateway. The current `arbol-core` implementation is also the sole Event Log writer and still contains chat execution responsibilities that move behind Trunk boundaries. *(daemon)*
- **[Event Log](#event-log) service** — independently supervised stable append/replay service backed by PostgreSQL; a target component extracted from current Root-owned persistence. *(daemon; planned target topology)*
- **[Trunk Runtime](#trunk-runtime)** — a concrete versioned process generation executing one [Arbol Trunk](#arbol-trunk); old and new generations run side by side while Trunk-owned [Chat Exchanges](#chat-exchange) drain. *(independently supervised process)*
- **[Effector](#effector)** — executes and settles [Tool Requests](#tool-request). *(daemon)*
- **Integrations** — the *Integrator* daemon (Slack / IMAP / HTTP and other side-channels). *(daemon)*
- **[Taproot](#taproot)** — the resident [Mycel](#mycel) knowledge host: Corpus Watcher, sync/embed/RAPTOR jobs, and the `knowledge.*` RPCs [Arbol Root](#arbol-root) proxies. *(daemon)*
- **[Driver Instance](#driver-instance)** — a versioned `<provider>@<build_id>` process with its own binary, launchd job, and socket; launched on demand by [Arbol Root](#arbol-root).
- **[CLI](#cli)** (`arbol-cli`) — a short-lived client process (one per invocation) driving the same [Arbol Root](#arbol-root)/daemon RPC the UIs use. Also a [Surface](#surface).

**Example:** You can restart the Swift App, Root, Effector, and Integrations together; [Arbol Root](#arbol-root) then launches [Driver Instances](#driver-instance) on demand as turns route to each provider; an `arbol-cli` invocation is a fifth component that comes and goes.

## Arbol-Initiated Chat Session

Umbrella term for any [Chat Session](#chat-session) a [Leather Bag](#initiator) did **not** start directly — one started by an agent, such as the conversational agent in another Chat Session, a [Delegate](#delegate), or a [Steward](#steward). Used only as the genus; in practice each is a concrete type such as a [Companion](#companion), [Research Trip](#research-trip), [Errand](#errand), or [Routine](#routine). Contrast a *Leather-Bag-initiated* Chat Session — the live conversation a person drives in [Elma Chat](#elma-chat). Whatever started it, it is still an ordinary Chat Session (Turns, tools, [Event Log](#event-log)); the [Initiator](#initiator) is a property, not a separate aggregate.

**Example:** When the agent in a Chat Session needs the auth module summarised without bloating its context, it spawns a [Research Trip](#research-trip) — an Arbol-Initiated Chat Session — and reads back only the findings.

## Arbol Internals

Arbol-owned metadata attached to an external [Entity](#entity). It can add properties the external system does not have or override an external property when Arbol has better local knowledge. The external value is retained for provenance; consumers use the Arbol override as the effective value when one exists. Name an individual field with the concise `Arbol` prefix — for example **Arbol status** (`arbol_status`) — rather than “Arbol Internal Status.”

**Example:** An external tracker reports an issue as `In Development`, but local work has reached review. Its `arbol_status: In Code Review` makes `In Code Review` the effective status in Oaken while the tracker's original status remains available for provenance.

## Arbol Secret

An [Entity](#entity) (kind `secret`, tag `sec`): a user-provided value containing secrets that can be *used* in work **without exposing its contents to the agent**. *(Planned feature.)*

**Example:** A user attaches an API key as an Arbol Secret; the agent can reference and use it through Arbol without the raw value ever entering the model context.

## Arbol Swift App

The native macOS Swift/AppKit component built from `arbol-app`, with its own numbered [Builds](#build) outside every [Arbol Root](#arbol-root). One process holds the tray menu, hotkeys, native surfaces and the web views of the UIs. It discovers the retained Roots on every start and loads each selected Root's renderer bundles from that Root's `arbol` Build. It exposes the [Bridge](#bridge) and passes calls and subscriptions to the selected Root's backend without interpreting them or opening its database. Each Root records its minimum App Build; the tray menu offers Roots the running App can serve and says which Build the others need. See [the Swift App and the backend](architecture/00-components-and-boundaries.md#arbol-the-swift-app-and-the-backend).

**Example:** One Swift App shows First Sapling and a second Root in its tray menu. Opening Elma Chat in each loads that Root's renderer and connects it to that Root's backend; neither operation creates another Swift App process.

## Arc

The middle tier of a [Saga](#saga): a coherent sub-stream of related [Beats](#beat) within one Saga — for example one subsystem's share of a migration. A specific Arc is named by proper name plus tier word — "Glossary Arc", "Arbol Specs Arc" (see [Saga](#saga) **Usage**). Like every Saga tier, an Arc declares its own territory, and its Beats are exclusive while active — overlapping Beats queue instead of running together. Nesting stops at Beats: an Arc cannot contain another Arc.

**Example:** The "Semantic Research Saga" has a "Glossary Arc"; that Arc groups the Beats that change the glossary and nothing else.

## Artifact

A documentation file — a working document for a [Repo](#repo). Artifacts may live in the Repo's [Artifact Space](#artifact-space), `~/Artifacts/<repo-name>/`, or inside the Repo folder itself. They are almost always Markdown and are not source code, but an Artifact may be **any format** (`.txt`, `.pdf`, `.html`, or even source code used as documentation) — what makes a file an Artifact is its *purpose* (documentation / working notes), not its location or extension. **Not build output** — the files a [Build](#build) produces are never Artifacts. Representable as an [Entity](#entity) of kind `artifact`.

**Example:** `turn-composition/01-intake/README.md` in an Artifact Space is an Artifact; so are a Repo-root `README.md`, a `.pdf` design export, or a quick `.html` mockup created as documentation.

## Artifact Chapter

A group of [Artifacts](#artifact) covering one high-level topic within an [Artifact Space](#artifact-space), represented by a folder directly in the Artifact Space root or directly inside a root chapter.

**Naming is a conversational convention, not a parsing rule.** Chapters at either depth may be referred to by their own name followed by **Chapter**: **Plans Chapter** can refer to `plans/`, and **Integrations Chapter** can refer to `architecture/integrations/`. A chapter name does not imply a depth or a unique path. Without other context, an unqualified request to create an **Artifact Chapter** defaults to a root chapter, but users may use the term for either root or nested chapters.

Before resolving a named chapter to a folder, agents should scan all root and nested chapter names in the relevant Artifact Space, retaining their full relative paths so duplicate names are visible. The same name may occur under different root chapters, or at both root and nested levels; do not stop at the first match or automatically prefer a root match. Interpret the whole request using the conversation, explicit paths or containment phrases, and the existing folder structure. Context may also indicate that a name describes a containing chapter rather than the target itself. For discovery questions, consider both root and nested chapters unless the user narrows the scope. If multiple plausible destinations remain after using context, ask a focused clarification with their paths; otherwise proceed with the best-supported interpretation.

**Usage examples:**

- “Create new Artifact Chapter where we would store RAPTOR summaries” — normally create a suitable topic folder at the Artifact Space root, using context and existing organization to choose its name and location.
- “Do we have some artifact chapter for code reviews?” — look for relevant chapters at both root and nested levels.
- “Create new artifact chapter 'integrations' in Architecture Chapter” — treat `architecture/` as the containing chapter and create `<artifact-space>/architecture/integrations/`.
- “Open the Plans Chapter” — refers to `plans/` when the chapter-name scan and context identify it; “create a Plans Chapter about storybook” may mean `plans/storybook/`, depending on context.
- “Open the Integrations Chapter” — can refer to a nested chapter. If both `architecture/integrations/` and `plans/integrations/` exist, use context to distinguish them or ask which path the user means. “Open the Integrations Chapter in Architecture” identifies `architecture/integrations/`.

The structural scope remains two folder depths: `plans/` and `plans/safe-restart/` can both be chapters; `plans/safe-restart/rollout/` is a deeper folder within a chapter. The Artifact Space itself and individual Artifact files are not chapters. These boundaries describe the organization; they do not require users to use the terminology precisely.

## Artifact Corpus

One of the two kinds of [Corpus](#corpus) a [Repo](#repo) has: the logical collection formed by **the Repo's [Artifact Space](#artifact-space) plus the [Artifacts](#artifact) inside the Repo folder itself**. In other words, the Artifact Space is the dedicated out-of-repo filesystem area, while the Artifact Corpus spans both that area and repository-owned documentation—usually Markdown, not source code. [Mycel](#mycel) [ingests](#ingest) the corpus into [Chunks](#chunk) keyed by heading path. Named per Repo: the **Arbol Artifact Corpus** includes `~/Artifacts/Arbol/` and the Artifacts in the Arbol Repo. Contrast the [Code Corpus](#code-corpus), the same Repo's source code.

**Example:** Artifact-Space files such as `GLOSSARY.md` and `architecture/external-tools.md`, together with Repo files such as the root `README.md` and documentation under `docs/`, belong to the Arbol Artifact Corpus. Source files beside those documents belong to the Code Corpus instead.

## Artifact Space

A top-level folder directly inside `~/Artifacts/`. An Artifact Space is the dedicated filesystem home for one coherent body of [Artifacts](#artifact) outside a Repo folder. It forms the out-of-repo portion of a Repo's broader [Artifact Corpus](#artifact-corpus); the Artifact Corpus also includes Artifacts stored in the Repo itself. `~/Artifacts/` is the container of Artifact Spaces, not an Artifact Space, and folders nested inside an Artifact Space are not separate Artifact Spaces.

**Example:** `~/Artifacts/Arbol/` and `~/Artifacts/mycel/` are Artifact Spaces; `~/Artifacts/Arbol/architecture/` is a folder within the Arbol Artifact Space, not another Artifact Space.

## Attestation

A recorded verification of some content — an [Artifact](#artifact), a chunk, an agent's result — capturing **who/what vouched** (a passing test suite, a compiler, a competent [Leather Bag](#initiator), another agent on a [Research Trip](#research-trip)), **how** (ran tests, type-checked, read-and-confirmed, cross-checked against source), and **against which version** (a content hash). It is *trust earned by verification*, and a **separate axis** from who produced the content: in Arbol almost everything is written by an agent, so "an agent wrote it" — or even "a [Leather Bag](#initiator) started the session" — says nothing about correctness. Two states follow:

- **Unattested** — no current verification exists. The **default** for any fresh agent output: it may well be correct, just unchecked.
- **Attested** — a current attestation vouches for it. Not binary but **graded** by the strength of its source — a reproducible machine check (tests, compile) outranks a skim by a non-expert. This strength is the chunk's **trust score**; re-verification refreshes it, and a score that falls below threshold is what promotes a [Drift Candidate](#drift-candidate) to a [Drift](#drift).

An attestation **decays**: it is bound to the version it verified, so when the content (or what it was checked against) changes, it no longer applies and the thing is Unattested again — the same mechanism that makes a *derived* chunk go stale against its source, generalised from "still matches its source" to "has been verified". Distinct from approval: an [Effector](#effector) approve/reject grants *permission to act* (run a [Tool Request](#tool-request)); it does not vouch for the *result*. The dangerous, common case is **Leather-Bag-initiated + Unattested** — work a person delegated, an agent did, and nobody competent checked.

**Example:** A [Delegate](#delegate) runs an [Errand](#errand) editing a config file and the changelog. A [Routine](#routine) later runs the test suite — the passing tests are a machine attestation of the config against that commit; the changelog prose, which no test covers, stays Unattested until a competent reader confirms it. Change the config afterwards and its attestation decays to Unattested.

## Attention Item

Something that is not a normal state of a Root and that every window of the Root shows for as long as it lasts, with its cause, such as a database server that does not answer or a disk that is nearly full. The [Arbol Backend](#arbol-backend) opens and closes it and sends it over the [Bridge](#bridge). Specified in [BKD-1](backend/01-the-bridge.md#attention).

**Example:** While the database server restarts, every window of First Sapling shows "The database server does not answer at 127.0.0.1:5433", and the line goes when the server answers again.

## Authoritative Input

The exact initiator input durably accepted by an [Arbol Trunk](#arbol-trunk) as the request to execute in one [Chat Exchange](#chat-exchange). Before acceptance, Composer content is a provisional [Draft](#draft) and may trigger speculative Activities; after acceptance, the immutable Authoritative Input is the only text and attachment set that may determine the Exchange's agent invocation and required effects. Accepting Authoritative Input is distinct from [Exchange Assignment](#exchange-assignment): assignment binds the Exchange to its Root, Trunk Build and process, while input acceptance establishes what that Exchange must process.

**Example:** A Draft mentions “Arbol Trunk,” starts speculative Cue extraction, and is then edited before Send. Only the exact text and attachments accepted on Send are Authoritative Input; removed provisional Cues cannot affect the agent invocation.

## Authority Epoch

The persisted state generation used with database and installation identity to fence stale SQL/runtime owners. Epoch mismatch rejects authority; elapsed time or an epoch change alone does not establish native process exclusion, successful cleanup or a receiver ACK. See [State Runtime Profile](#state-runtime-profile).

## Beat

The leaf tier of a [Saga](#saga): the task-sized unit of work an agent picks up and runs to done or abandoned — typically through an [Errand](#errand). A specific Beat is named by proper name plus tier word — "Trunk Implementation Beat", "Workflow Semantics Beat" (see [Saga](#saga) **Usage**). A Beat declares its own territory like every other tier, may carry [Objectives](#objectives) as its done-when, and is where progress is measured: a Saga's or Arc's progress is read from its Beats' outcomes, which is what a future board visualization would show per unit.

**Example:** The "Idempotency Key Column Beat" touches `migrations/…` and `ledger/writer.py` only; while a [Delegate](#delegate) works it, no other active Beat, Arc, or Saga may claim those files.

## better-grep

The level-2 retrieval tool (see `operations/code-research-levels.md`): a **drop-in grep replacement** — swap the word, keep every flag — whose contract is *grep fidelity first*. The exact arm literally runs `grep` with the caller's arguments (byte-identical output, grep's exit codes, so scripts branching on them stay correct), then two labeled [Mycel](#mycel) sections append: **related by meaning** ([Dense](#dense-retrieval) + doc-bridge hits with `⇐ via` attribution) and **documented in** ([Runbook](#runbook)/research sections whose [Source Refs](#source-ref) cite the matched code, with ⚠ stale trust flags). The tail is informational only and suppressible (`BETTER_GREP_PLAIN=1`); scope (repo + [Branch Overlay](#branch-overlay) view) is inferred from the CWD/path operands. It is the on-ramp from grep habit to Mycel: exact search stays exact, the tail rescues vocabulary gaps and pushes documentation at the reader.

**Example:** `better-grep -rn "session reminder" apps/limit` finds nothing literal — the tail surfaces `RealityCheckProcessorService` via `GLOSSARY.md › Reality Check`, because "reality check" is the code's word for it.

## Blueprint

A named, reusable **definition of agent work**: instructions plus typed input/output parameters, from which Arbol launches a goal-driven [Chat Session](#chat-session) (usually background) to do the job — the **non-deterministic analog of a function**, for work that needs an agent rather than code. A Blueprint declares *what the agent is given and what it must produce*; each run binds the inputs, executes through a chosen [Brain Recipe](#brain-recipe), and ends when the goal is reached. The definition is a **portable Mycel document** — any agent (Claude Code in VS Code, codex) can execute one manually; the Arbol engine merely automates runs. A Blueprint is **atomic** — one agent session's worth of work; control flow never enters its contract — deterministic composition (sequences, gates, loops) is a [Blueprint Chain](#blueprint-chain). The first Blueprint exists: `blueprints/deep-research.md` (level-4 deep research); design and delivery live in `plans/blueprints.md`. *(Planned feature — the term is adopted from Arco, replacing the earlier working name "Custom Workflows"; the word "workflow" is not part of Arbol vocabulary.)*

**Example:** A `deep-research` Blueprint takes `{repo, topic}` as input and produces a research [Artifact](#artifact) with [Source Refs](#source-ref); "research withdrawal flows in Arbol" is one background run of that Blueprint.
## Blueprint Chain

A **deterministic composition of [Blueprint](#blueprint) runs** — the *program* to the Blueprint's *function*: real code (sequence, gates, retries, fan-out) calling Blueprints, whose typed inputs/outputs are the ABI that makes deterministic chaining possible. Control flow is never YAML-encoded: a Blueprint Chain is a **plain Python script** — itself a [Tool](#tool) — living in `~/Artifacts/mycel/chains/` (the Mycel corpus — a Mycel Operation usable from any repo, deliberately NOT in the Arbol repo or corpus) with its [Runbook](#runbook) as a same-name sibling `.md`. Shared plumbing comes from `chainlib`: an append-only process log (`~/.infer/chains/<run-id>/chain.jsonl`), resume of unfinished runs, Promise.all-style `parallel()`, and parent labels when chains call chains. A chain's steps are its [Cells](#cell) (Tool / Blueprint / lambda); each agent Cell runs as its own [Chat Session](#chat-session) — fresh context per Cell, so the verifier is never the context that produced the work — and gates are enforced by code, not hoped for in instructions: an unmet `done_when` ABORTS the chain. In degraded mode a chain stays a readable script an agent drives by hand (`--dry-run` prints exactly what by-hand means). Design + plumbing: `plans/blueprints.md`.

**Example:** A chain script runs a research Blueprint, aborts when its `done_when` is unmet, and only then starts a planning Blueprint in a fresh Chat Session; a second chain that needs the same first steps duplicates them rather than sharing a sub-chain — chains evolve independently and each reads whole.


## Book

A synonym of [Hold](#hold): to **book Beaver Workspace** means an agent has
started working in **Beaver Workspace**, reserving it for that work.
**Booking** and **holding** name the same operation and reservation.

## Brain Recipe

A reusable, named **brain recipe**: built on a specific [Intelligence Provider](#intelligence-provider-ip) — which supplies the [Subscription](#subscription) and the repo rules (including which [Repos](#repo) are prohibited) — with **one model + one thinking level** pinned from that provider's set. E.g. `safe-claude` + `opus-4.8` + thinking *max* (an expensive brain), or a Codex IP + `gpt-5.3-spark` + thinking *low* (a cheap one). Where an IP spans **all** of a provider's models (with a *default*), a Brain Recipe pins exactly **one**. Built and configured in [Seqoya Lab](#seqoya-lab); today a recipe is selected **directly** — e.g. the summariser recipe that [RAPTOR Summarization](#raptor-summarization) runs its [Completions](#completion) through. A [Blueprint](#blueprint) or [Blueprint Chain](#blueprint-chain) declares its recipe with two fields — `recipe` (a hard pin; default `inherit`) and `default-recipe` (the fallback) — resolved as **pin → caller → default → error**, where *caller* means a calling chain or a user-named recipe, never the chat session that triggered the run: a session's own model is not an inheritable recipe (`plans/blueprints.md`). A recipe may also be described **ad hoc** at the call site — `--recipe model:thinking` (e.g. `fable:xhigh`; full form `ip:model:thinking`) — for brains not configured in `~/.mycel/config.toml`: the model passes to the claude binary verbatim, thinking maps onto the CLI's `--effort` tiers, and configured names always win over descriptors. Assembling recipes into [Ladders](#ladder) (rung-based escalation) is planned.

**Example:** `safe-claude` + `opus-4.8` + max and a `codex` IP + `gpt-5.3-spark` + low are two Brain Recipes; a [Ladder](#ladder) puts the cheap one on a low rung and the expensive one on a high rung.

## Branch

<!-- mycel:cues
literal: exclude
target-scope: local_section
-->

An [Entity](#entity) (kind `branch`, tag `brn`): a git branch plus the metadata Arbol tracks about it. Like any Entity it connects to others via [Entity Edges](#entity-edge)—to the `commit`/`mr` Entities raised on it, the [Chat Sessions](#chat-session) that worked there, and the `ticket` it implements. Its `path` is the branch's [Worktree](#worktree) root when checked out; multiple Worktrees are why one [Repo](#repo) can expose several branch directories. Fields:

- `name` — full branch name
- `repo` — the [Repo](#repo) code name this branch belongs to (e.g. `Arbol`)
- `path` — path to the branch's checked-out [Worktree](#worktree), when present
- `isWorktree` — whether the branch lives in a git worktree · `worktreeName` — that folder's name (when `isWorktree`)
- `isFeatureBranch` · `isSubBranch` · `isReleaseBranch` · `isMaster` — branch-role flags

*(Planned feature.)*

**Example:** `feature/auth-refactor`, checked out as a worktree, links to the ticket it implements, the commits and MR raised on it, and the Chat Sessions that worked there.

## Branch Overlay

An **ephemeral, diff-scoped chunk namespace** (`<repo>@<branch>`) layered over a [Repo's](#repo) base corpus at query time — [Mycel](#mycel) seeing "the repo as this branch sees it". Contains chunks ONLY for the files the branch changes relative to the local `master` (merge-base diff; uncommitted edits and untracked files included), embedded with the **base repo's** [Embedder Profile](#embedder-profile) (the interlock is inherited, never re-decided). At query time, **shadowing** applies: base chunks under overlay-covered paths are suppressed and the overlay's stand in; deleted files are tombstoned paths that suppress without replacement. Lifecycle is bound 1:1 to a git worktree in the repo's [Worktree Container](#worktree-container) (`mycel wt add/drop` manages both together, daemon-less); the [Corpus Watcher](#corpus-watcher) and every [Sync Pass](#sync-pass) re-diff registered worktrees, so a week-long task branch trickles into its overlay as it changes. Overlays are a **proposed future** — exempt from [Detection](#detection)/[Drifts](#drift), [RAPTOR](#raptor-tree) and status counts, the mirror-image of [Heartwood](#heartwood)'s frozen past: neither makes claims about present master. Because changed chunks share natural keys with their base counterparts, their [Source Ref](#source-ref) reverse edges surface in review: "this MR drifts N research docs".

**Example:** `mycel wt add Arbol --mr 1234` fetches the MR into a branch-named worktree and builds its overlay in minutes; `better-grep` and `code-search` run from inside that worktree automatically search master-with-the-MR's-changes, with overlay hits marked.

## Bridge

The Swift↔renderer communication channel (`window.webkit.messageHandlers.arbol`). The UI `call`s RPC methods and `subscribe`s to streams. When absent, the UI runs standalone.

**Example:** Elma Chat calls `window.webkit.messageHandlers.arbol` to create a [Chat Session](#chat-session); in Storybook or a browser preview, the bridge may be absent and mocked.

## Build

<!-- mycel:cues
literal: exclude
target-scope: local_section
-->

The versioned set of build outputs (binaries, app/renderer bundles) produced by one `build.sh` run, identified by a `build_id`. A [Driver Instance](#driver-instance) is a [Driver](#driver) pinned to one Build. *(Build outputs are not [Artifacts](#artifact) — different sense of the word.)*

**Example:** Running `build.sh` at 13:55 can produce build `20260612T135543Z`; a driver instance may then be pinned to that exact build.

## Burn

The **accumulated token consumption** of saga work: every token spent by the agents working a unit, from its start to now, reportable per [Subscription](#subscription), [Brain Recipe](#brain-recipe), and [Stint](#stint). Burn is a stock, not a rate — the rate of token generation is [Velocity](#velocity). Scoped like every Radar metric: "**Research Saga Burn**" is one unit's total, **Radar Burn** the machine-wide total (see [Radar](#radar)). *(Planned feature.)*

**Example:** "Semantic Research Saga" has burned 412k tokens across two Delegates — 300k of them on the second [Brain Recipe](#brain-recipe) of its [Ladder](#ladder).

## Cell

One step of a [Blueprint Chain](#blueprint-chain) — the chain's **unit of execution, resume, and rendering**. A chain is a *sequence of Cells* the way a notebook is a sequence of cells: each Cell runs in order, produces its declared output, is independently **skippable on resume** (a completed Cell is not re-run — `--until N` stops after Cell N and the next invocation resumes there), and is **gated** by code (a failed gate ABORTS the whole chain — the guarantee a chain adds over instructions). A Cell is one of three **kinds**: a **[Tool](#tool) Cell** (deterministic subprocess, no agent — e.g. a `mycel sync`; gate = exit 0), a **[Blueprint](#blueprint) Cell** (a named [Blueprint Run](#blueprint) in its own fresh [Chat Session](#chat-session); gate = `done_when`), or a **lambda Cell** (an inline anonymous agent — a fresh Chat Session with a prompt but no reusable Blueprint; gate = the session completing). Every agent Cell (Blueprint or lambda) gets **fresh context**, so the verifier is never the context that produced the work. A Cell is NOT a Blueprint's internal **Step** (`### Step N` — sequential messages accumulating in ONE session): Steps share one context, Cells never do — the word *Cell* exists precisely to keep the two apart. The **code keeps the short name `step`** (`chain_step=N` labels, `--until N`, `step_started`/`step_finished` log events); *Cell* is the leather-bag term — the same split as [Chat Session](#chat-session) vs the `session` code name. Each Cell's start/finish/skip is one line in the chain's process log (`~/.infer/chains/<run-id>/chain.jsonl`), rendered `Cell N/total · kind · title`.

**Example:** A chain runs 4 Cells — Cell 1 *sync* (Tool) → Cell 2 *research* (Blueprint) → Cell 3 *objectives* (lambda) → Cell 4 *plan* (Blueprint). `--until 2` stops after Cell 2; re-running with the same input resumes at Cell 3.

## Change Walkthrough

A guided inspection of code changes on a dedicated Elma page: the Leather Bag selects a [Repo](#repo) and a [Diff View](#diff-view) for its current checkout, then uses [Hunk Review](#hunk-review) to inspect the resulting code changes and gather bounded context for questions or correction requests to an agent. **Walkthrough** is the accepted short form when the context is unambiguous. The Change Walkthrough Page is a top-level sibling of Elma's Chat Page—not a child page, mode, response replacement, or side panel of a [Chat Session](#chat-session). Elma's header switches bidirectionally between Chat and Change Walkthrough, and **⌥Tab** provides the same sibling-page toggle; both pages retain their in-memory state. The first general visit has no Chat Session restrictions. A Quick Action may pass the current Chat Session as optional launch/handoff context and use its [Repo Folder](#repo-folder) to preselect the matching Repo, and the repository folder is the checkout inspected. A Change Walkthrough is not a separate reviewer agent, Chat Session, or Oaken work item; automated review lenses and durable reviewed/unread state may assist it later but are not required by the term.

**Example:** After implementing a feature in the `Arbol` repository folder, the Leather Bag invokes **Walk through changes…**. Elma inspects that checkout; **Ask agent** returns the selected hunk to the Chat Page and Composer.

## Chat Exchange

One message of the [Leather Bag](#leather-bag) in a [Chat Session](#chat-session) and the agent's answer to it, from its acceptance by one [Arbol Trunk](#arbol-trunk) process ([RCT-2](../arbol-root/contract/02-starting-stopping-and-settling.md#accepting-a-message)) to its end; one row of `exchanges` in the chat tables of its [Arbol Root](#arbol-root)'s database ([RCT-3](../arbol-root/contract/03-the-chat-tables.md)). A message that is refused is no Exchange: it leaves no row, starts nothing, and its [Draft](#draft) stays in the composer. From acceptance the one process owns the Exchange and runs it with the one route it was handed, with no retry on another route and no failover. It ends the Exchange by itself as completed, failed with its cause, or cancelled; when the process died first, settling ends it as interrupted. An Exchange may hold several agent [Turns](#turn) and tool calls. **Chat Exchange** replaces the old broad product use of “Turn”; `Exchange` is the accepted short form when context is unambiguous. See [a Chat Exchange across the components](architecture/02-chat-exchange-across-components.md).

In version 1 an Exchange was owned by a resident [Trunk Runtime](#trunk-runtime) through an assignment recorded in the [Event Log](#event-log), began when the composing of a message began, and could hold Draft revisions, retries and failovers.

**Example:** One message leads to ten Bash tool calls and then a final answer: that is one Chat Exchange, one row of `exchanges`. The next message in the same Chat Session is another Exchange, and may run on a newer Trunk Build.

## Chat Note

A durable user-role entry added to a [Chat Session](#chat-session) without opening a [Turn](#turn) or requesting an agent response. A Chat Note is part of the applicable conversation-branch history and may be included when a later Turn is composed. Adding one does not invoke the Principal Agent. **Chat Note** is the canonical term; do not call it a “Context Message.”

**Example:** A user adds “The migration must remain backward compatible” as a Chat Note, then sends a separate message asking the agent to implement the migration.

## Chat Session

The complete lifecycle of one conversation, beginning when a Leather Bag opens its Composer or another authorized [Initiator](#initiator) opens the conversation and ending when it is closed or archived. It includes provisional Drafts and initial selections before the first submitted message, all [Chat Exchanges](#chat-exchange), user/agent communication, [Activities](#activity), [Turns](#turn), tools, retries, recovery, and outcomes. Whether it was started by a person or an agent is an Initiator property, not a separate session type; an agent-started one is an [Arbol-Initiated Chat Session](#arbol-initiated-chat-session). **Always write “Chat Session,” never bare “Session.”**

The existing `session` aggregate and `session.*` RPC namespace are current implementation names and may temporarily model only part of this lifecycle. They do not narrow the product definition. The retired **Conversation Thread** split is no longer used.

**Example:** Opening a new Composer starts a Chat Session before any message is sent; selecting a Worktree, editing Drafts, exchanging several agent Turns, handling tools, and finally archiving the conversation all belong to that Chat Session.

## Checkpoint

An identity-bound durable Provider output unit in the [State Runtime Profile](#state-runtime-profile), including complete bounded text/thinking/tool output and its exact hash. ACK follows commit; a commit with a lost ACK is recovered by readback. Reusing the identity with different bytes refuses. Provider transport sequence and checkpoint identity are separate cursor/deduplication domains.

## Chunk

The unit of knowledge [Mycel](#mycel) tracks. From an [Artifact Corpus](#artifact-corpus): a section of an [Artifact](#artifact), keyed by heading path. From a [Code Corpus](#code-corpus): a symbol — function, method, class header, module preamble, or Svelte block — keyed `path#symbol`, carrying language, symbol kind, and line span. A [RAPTOR Tree](#raptor-tree)'s [Summary Nodes](#summary-node) are Chunks too. Each Chunk has a **stable identity** — an immutable id plus a mutable `natural_key`, maintained by [Identity Reconciliation](#identity-reconciliation) so it survives edits and renames — a **content hash**, an [Embedding](#embedding), and a **role** summarising its edge situation: `authored` (nothing governs it — it may govern others, or stand [Free-standing](#free-standing)), `derived` (at least one [Derivation](#derivation) points at it), or `unclassified` (a leather bag hasn't yet decided which — a docs-only state). Defaults follow origin: a doc chunk starts `unclassified` (a section may be an original decision or a restatement of one made elsewhere — unknowable without a leather bag); a code chunk starts `authored` (undocumented code is de-facto self-authoritative — the only truth about what the system does, until an edge asserts otherwise); a [Summary Node](#summary-node) is born `derived` (created by its generation edges). Asserting a Derivation flips the child chunk to `derived`.

**Example:** The `## Attestation` section of `GLOSSARY.md` is one Chunk; so is `daemons/core/arbol_core/pg.py#connect`. Editing either changes its content hash, which is how [Detection](#detection) notices downstream chunks may have drifted.

## Chunking

The step of [Ingest](#ingest) that splits one corpus file's text into **chunk candidates** — raw sections that only *become* [Chunks](#chunk) (with identity) after [Identity Reconciliation](#identity-reconciliation). Deterministic: the same text always yields the same candidates. Per format: **Markdown** splits by heading path; **Python** by symbol via the language's own syntax tree (function / method / class header / module preamble); **Svelte** by block (`<script>` / `<style>` / markup). A file that fails to parse becomes a single whole-file candidate rather than being dropped.

**Example:** A Python file with two functions and a class with three methods yields ~seven candidates: a module preamble, two functions, a class header, and three methods — each with its own line span.

## CLI

<!-- mycel:cues
literal: exclude
target-scope: local_section
-->

`arbol-cli`: the command-line client — both an [Arbol Component](#arbol-component) (a short-lived process, one per invocation) and a terminal [Surface](#surface). A thin, stateless RPC client that reaches [Arbol Root](#arbol-root) and the other daemons over their Unix sockets, exposing the *same* method surface the [UIs](#ui) use — `session.*`, `ip.*`, `subscription.*`, `secrets.*`, `integration.*`, plus `healthz` / `triage` / `audit` / `watch` / `pending` / `approve`. It owns no state; every daemon it calls is the real owner. Built by `build.sh` (→ `dist/Arbol/bin/arbol-cli`) and installed to `$PREFIX/bin`. Serves as the headless admin / diagnostic / scripting interface: `gc-ip-instances.sh` drives [Driver Instance](#driver-instance) garbage-collection through it (`ip gc-candidates` / `ip collect`), and `rebuild-and-restart.sh` gates Root readiness on `arbol-cli healthz`.

**Example:** `arbol-cli session list` or `arbol-cli ip collect <id>` performs the same RPC a [UI](#ui) would, straight from a terminal — useful for debugging a wedged daemon without opening a window.

## Code Map

A **mechanically generated per-repo overview document** (`generated/code-map.md` in the repo's [Artifact Corpus](#artifact-corpus)): directory sections listing each code file's classes and methods, built purely from existing [Chunks](#chunk) — no LLM — and regenerated by any [Sync Pass](#sync-pass) that changed the code corpus (`operations/code-map.md`). Embedded like any document, it gives overview-shaped queries a landing chunk, and its file-level [Source Refs](#source-ref) give every code file a `documented_in` pointer back to its section. Marked `generated: true`: exempt from [Detection](#detection) and [RAPTOR](#raptor-tree) — searchable, never stale.

**Example:** "what services exist in the limit domain" lands on the map's `apps/limit/src/domain/services` section; any file listed there carries `documented_in: generated/code-map.md`.

## Code Scout

The **reconnaissance pass over a codebase** — fast, wide, and shallow, the deliberate opposite of deep research. A Code Scout sweeps cheap signals (retrieval, `better-grep`, the [Code Map](#code-map)) *for* a ticket's [Objectives](#objectives) and hands later work a map of **where to dig**: files/modules each with a one-line why, first hunches explicitly marked unverified, surprises the ticket's framing did not predict, and blind spots where the scan found nothing. Signals, not conclusions — a scout that starts verifying has stopped scouting. Embodied as the `scout-codebase` [Blueprint](#blueprint) (read-only, producing `code-scout.md`).

**Example:** For a limits ticket, the scout lists `apps/limit/src/domain/services` ("objective 2 — recalculation lives here"), flags an unexpected feature toggle guarding the old path as a *surprise*, and admits it found nothing about the notification requirement — so deep research knows exactly where to spend its hour.

## Code Corpus

One of the two kinds of [Corpus](#corpus) a [Repo](#repo) has: its **source code**, [ingested](#ingest) into [Chunks](#chunk) keyed `path#symbol` (with language, symbol kind, and line span). Chunking is code-aware per language: Python via stdlib `ast`, Svelte block-aware, TypeScript/TSX/JavaScript via tree-sitter, ops scripts/plists/Swift as whole-file chunks. Named per enabled Repo, rooted by its `~/.mycel/config.toml` entry. The frozen `arbol_deprecated_v1` code and artifact corpora are excluded from indexing. Version 1's Arbol code roots included `daemons/`, `drivers/`, `renderer/apps/`, `cli/`, `scripts/`, `launchd/`, and `tests/`; these are historical locations, not the active Arbol index scope. It powers hybrid code search (`mycel search --only code`) and is the substrate for the planned code↔doc [Derivations](#derivation). Contrast the [Artifact Corpus](#artifact-corpus), the same Repo's documents.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `mycel_deprecated_v1:mycel/knowledge/code_chunker.py`

**Example:** Saving a change to `raptor.py` makes the [Corpus Watcher](#corpus-watcher) fire a [Sync Pass](#sync-pass): only the edited symbols re-chunk and re-embed.

## Cue

A provisional, traceable weak signal derived from analysed text. A Cue records what a [Cue Channel](#cue-channel) detected and where it was detected; it does not by itself establish the text's meaning. The Cue Channel contract—not a universal confidence rule—determines which [Cue Command](#cue-command) the finding produces.

**Example:** Finding the exact string “team lead” records a literal Cue. The observation that the string occurred is certain, while what the Leather Bag meant by it may remain uncertain.

## Cue Channel

A named end-to-end rule that defines both how [Cues](#cue) are detected and which [Cue Command](#cue-command) every successful detection produces. Different channels may use different detection methods and downstream contracts. In the `literal` channel, boundary-aware literal matching always commands inclusion of every associated [Cue Target](#cue-target) in the next system prompt; there is no later relevance assessment.

**Example:** The `literal` channel matches “Arbol Trunk” anywhere as a term and commands inclusion of its glossary section, while a future `skill` channel may require an exact slash command at the beginning of a submitted message.

## Cue Command

A requested downstream effect produced according to a [Cue Channel](#cue-channel)'s contract after that channel detects a [Cue](#cue). A Cue Command is data passed to later [Activities](#activity), not an effect performed by the detector itself. Multiple commands for the same effect and [Cue Target](#cue-target) are deduplicated before execution.

**Example:** A literal Cue for “Arbol Trunk” produces `include target in next system prompt` for the Arbol Trunk glossary target; target extraction and prompt composition execute that command later.

## Cue Detection Catalog

A generated catalog of rules consumed by one [Cue Channel](#cue-channel), distinct from the runtime [Cues](#cue) found in text. The literal channel's `generated/cue-detection/literal.json` is a flat JSON array with one unique `literal` and one-or-more `targets`. Mycel-style `mycel:cues` HTML-comment declarations compile into it. In `GLOSSARY.md`, one file-level declaration derives literals from selected section headings; `literal: exclude` suppresses a heading-derived rule locally, and an ordinary local literal list adds aliases. A heading such as `Fold / Projection` derives separate `Fold` and `Projection` rules that share one section target.

**Example:** `{"literal":"Team Lead","targets":["Arbol:GLOSSARY.md#Arbol Glossary > Team Lead"]}` tells the literal channel which text to match and which target its command must include.

## Cue Target

A locator for Artifact content named by a [Cue Command](#cue-command). A Cue Target identifies either a whole file or one Markdown section; it is not the extracted content itself. Section targets use the corpus, corpus-relative path, and full Markdown heading path so nested sections and duplicate local heading names resolve unambiguously.

**Example:** `Arbol:GLOSSARY.md` targets the whole glossary, while `Arbol:GLOSSARY.md#Arbol Glossary > Arbol Trunk` targets only the Arbol Trunk section and its nested subsections.

## Cue Target Cache

The bounded, runtime-wide cache of content extracted from [Cue Targets](#cue-target), shared by all ongoing Drafts and [Chat Sessions](#chat-session). It is keyed by the target and source version, so unchanged content prepared from a provisional draft Cue can be reused at submission or by another active conversation. The cache stores no Cues, makes no inclusion decision, and cannot keep a superseded draft Cue active.

**Example:** After one draft extracts the Team Lead glossary section, another active Chat Session can reuse the cached section while the glossary source remains unchanged; each message still needs its own Cue and Cue Command before inclusion.

## Command

<!-- mycel:cues
literal: exclude
target-scope: local_section
-->

An *intent* to change state — imperative, present/future tense (`SendMessage`, `CreateChatSession`), the counterpart to an [Event](#event-log) (a past-tense fact). A Command is *requested*, never stored as truth: [Arbol Root](#arbol-root) validates it against the current [folded](#fold--projection) state via the [Aggregate](#aggregate) guard, and on success it produces one or more events; on failure it is **rejected** (e.g. `IllegalTransition`). Events are immutable and cannot be rejected; Commands can be edited or refused right up until they are accepted. A [Draft](#draft) is a durable, editable representation of not-yet-accepted input; its revision and lifecycle facts may be event-sourced without turning the provisional content into accepted [Authoritative Input](#authoritative-input). See also: [Draft](#draft), [Aggregate](#aggregate), [Event Log](#event-log).

**Example:** "Send this message" is a Command. If the [Chat Session](#chat-session) is `archived`, the guard rejects it; if legal, it is accepted and appended as the `USER_SENT_MESSAGE` event — at which point it is a fact and can no longer be unsent, only superseded by later events.

## Communicado

One concrete, user-addressed communication produced by a [Communicado Species](#communicado-species). A Communicado can merely inform, ask for a decision, expose [Actions](#communicado-action), or represent attention needed while work continues. Its durable common status is `active`, `action_required`, or `resolved`; a Communicado with status `action_required` is an [Action Item](#action-item). Species-specific [Communicado State](#communicado-state) may add detail without replacing this common lifecycle. It is not synonymous with a notification, card, dialog, or Slack message: those are possible [Presentations](#communicado-presentation) and [Deliveries](#communicado-delivery) of the Communicado. **Communicado means the instance only**; do not use it for its reusable implementation.

A Communicado is an [Entity](#entity) (kind `communicado`, tag `com`, shape `mark`) and may be independently [Spotlighted](#spotlight). Status and Spotlight never imply or mutate one another.

**Example:** “Pipeline #1842 failed on MR !418” is one Communicado produced by the Pipeline Failure Species; its Willo card, macOS notification, and Slack message may all present that same instance. A tool approval Communicado remains persisted with `action_required` status until answered.

## Communicado Action

A choice a [Communicado Species](#communicado-species) offers on one [Communicado](#communicado). Selecting an Action expresses user intent; it should enter Arbol as a [Command](#command), which [Arbol Root](#arbol-root) validates before resulting facts are recorded—not let a renderer append an event or execute an arbitrary RPC directly.

**Example:** **Retry**, **Open pipeline**, and **Dismiss** can be three Actions on a failed-pipeline Communicado.

## Communicado Delivery

One attempt or record of exposing a [Communicado](#communicado) through a [Surface](#surface) or external destination. Delivery is separate from [Presentation](#communicado-presentation): Presentation determines representation; Delivery records that the representation was actually sent or shown. One Communicado may have several Deliveries without becoming several Communicados.

**Example:** Posting a macOS notification and sending Slack blocks are two Deliveries of one pipeline-failure Communicado.

## Communicado Descriptor

The typed navigation target carried by a [Communicado](#communicado) when activating its [Presentation](#communicado-presentation) should redirect the user. A Descriptor names a supported destination rather than embedding an arbitrary command. The first forms are an Arbol-app destination (`{type: app, ui, query}`) and a validated link destination (`{type: link, kind: http|file, target}`).

**Example:** A finished-turn Communicado carries `{type: app, ui: elma, query: {session_id: …}}`, so clicking its macOS notification opens the relevant Chat Session in Elma.

## Communicado Family

An optional grouping of related [Communicado Species](#communicado-species). A Family is organizational only; it does not supply instance behavior, lifecycle, or rendering.

**Example:** A CI/CD Family may group Pipeline Failure, Deployment Ready, and Deployment Failure Species.

## Communicado Presentation

A [Communicado Species](#communicado-species)’ representation on one [Surface](#surface). Presentations may be fundamentally different implementations—not skins of a universal card—and a Species need not support every Surface. Shared primitives are conveniences, never a requirement that all Communicados have a title/body/buttons shape.

**Example:** One Pipeline Failure Species can use a rich Willo card, compact macOS notification content, and Slack Block Kit as three Presentations.

## Communicado Species

The complete reusable implementation that creates and governs a family of [Communicado](#communicado) instances. A Species may own its instance-data contract, creation policy, [State](#communicado-state) and lifecycle, [Actions](#communicado-action), authorization, grouping/deduplication, expiry, supported [Surfaces](#surface), and a distinct [Presentation](#communicado-presentation) for each Surface. **Species is not an OOP class and not merely a schema, category, template, or renderer**; the term exists to preserve how behaviorally and visually diverse Communicados may be.

**Example:** Tool Approval and Weekly Digest are different Species: one can block work and accept several Actions in Elma/Willo, while the other can be an immutable document visible only in Willo Station.

## Communicado State

The Species-specific state of one [Communicado](#communicado), governed by its [Communicado Species](#communicado-species). It may evolve while retaining the Communicado’s identity, but it must not duplicate the authoritative state of the domain operation that caused it.

**Example:** A retry Action may evolve one Communicado from “failed” to “retrying” to “passed,” while the pipeline remains the authoritative source for whether the retry actually succeeded.

## Companion

An [Arbol-Initiated Chat Session](#arbol-initiated-chat-session) attached to a **parent** Chat Session as a follow-up, running alongside it to assist (summarise, fetch context, watch). Inherited from the Arco app. The one Arbol-initiated type **meant to be read by the [Leather Bag](#initiator)**, so it appears in [Willo Station](#willo-station) like any Chat Session — but rendered to make its link to the parent clear. Defined by its **parent edge**; the other types are rootless. Run by a [Delegate](#delegate).

**Example:** After a long refactor Chat Session, a Companion is spawned to draft the MR description; it shows in Willo Station beneath its parent, visibly tied to it.

## Completion

A **one-shot, non-agentic** model call: a single prompt → output via a [Brain Recipe](#brain-recipe), with no tools, approvals, multi-turn, or [Event Log](#event-log) — the counterpart to an agentic [Chat Session](#chat-session). Use it when a model should *transform* input into output, not *do work*. [RAPTOR Summarization](#raptor-summarization) (cluster → [Summary Node](#summary-node)) and other simple [Generation](#generation) tasks are Completions; an [Embedding](#embedding) call is the same shape (a stateless API call). When generation needs to read code, run tools, or iterate, it stops being a Completion and becomes a Chat Session — an [Errand](#errand)/[Routine](#routine) run by a [Delegate](#delegate).

**Example:** RAPTOR runs each cluster through a Completion — prompt in, summary out — instead of spinning up a throwaway Chat Session per cluster.

<a id="core"></a>
## Arbol Root

**Arbol Root**, or **Root**, is a named, persistent environment for all [Arbol Trunks](#arbol-trunk) compatible with it: its identifier, display name, folder, database, settings and the Builds of `arbol` and `arbol-root` made for it. A **Root Build** is a numbered Build of `arbol-root`, the manager of that environment. It lists compatible Trunk components and Builds, selects a compatible working Build within the caller's chosen component or the [Trivial Trunk](#trivial-trunk), starts Exchanges detached, lists and stops them, and delegates interrupted-Exchange settlement to a Trunk. Each invocation is a short command; no resident Root process is required. The environment outlives its manager's invocations and Builds. See [Roots](architecture/01-roots.md) and [the Root manager](architecture/00-components-and-boundaries.md#arbol-root).

Roots replace the proposed name Ring. A breaking change creates a new Root beside the old one, preserving the old Root's chats and usability. The global `arbol-roots` command, outside every Root, manages the catalogue, creation, readiness, failure, minimum App Build, migration and removal. The global Swift App discovers Roots again when it starts; each Root has its own backend and renderer Builds. Drivers, Subscriptions, Trunk Builds, the App and the build registry are shared. The Root manager holds compatibility and lifecycle policy, reads Exchange records and never reads chat content or opens the database. An accepted Exchange keeps its `root` and Trunk Build and continues when the manager, backend or App ends.

**Example:** First Sapling uses Root Build `6`; a second Root uses Root Build `8`. Both can use a compatible research Trunk Build when both use the same Root Contract version. Replacing First Sapling's Root Build changes later command invocations, while its existing Exchanges continue in the processes already started for them.

## Corpus

A set of files [Mycel](#mycel) watches and reasons over (plural: *corpora*). Each [Repo](#repo) has two: its [Artifact Corpus](#artifact-corpus) (documents under `~/Artifacts/<repo-name>/`) and its [Code Corpus](#code-corpus) (indexed source roots) — named per Repo, e.g. the *Arbol Artifact Corpus* and the *Arbol Code Corpus*. A corpus is turned into stored [Chunks](#chunk) by [Ingest](#ingest); the stored graph is a **projection** of the corpus — accurate only as of the last ingest, which is why the [Corpus Watcher](#corpus-watcher) re-syncs it whenever corpus files change.

**Example:** `~/Artifacts/Arbol/` and the Arbol repo's source roots are Arbol's two corpora; editing `GLOSSARY.md` re-ingests just that file, and [Detection](#detection) flags anything derived from the changed text.

## Corpus Watcher

The event trigger for keeping [Mycel](#mycel) current: a file-system watcher (FSEvents) on every [Corpus](#corpus) root. When a relevant file changes (`.md`, `.py`, `.svelte`; build/dependency directories ignored), it arms a **debounce** — a short quiet-period (30 s) so a burst of saves coalesces into a single [Sync Pass](#sync-pass) instead of one per keystroke. A slow hourly **sweep** remains as the only timer, purely a fallback for events the watcher might miss.

**Example:** Saving five files during a refactor fires one Sync Pass thirty seconds after the last save — not five passes — and only the changed symbols re-chunk and re-embed.

## Coupling

A **consistency-only** relation between two [Chunks](#chunk) that carries **no authority** — neither governs the other (unlike a [Derivation](#derivation)). It records a *consistency obligation*: when one side changes, the other may now be wrong and must be **re-verified** — not regenerated. Usually **directed** (B depends on A); **symmetric** only for genuine mutual-consistency pairs. Deliberately **non-transitive** (it flags the directly-coupled neighbour, one hop — it does *not* cascade the way Derivation does), and its remedy is to **decay the neighbour's [Attestation](#attestation)** (mark it for re-verification), so couplings degrade gracefully instead of spamming urgent work.

Use **sparingly**. A reference or link is *not* a Coupling — promote it only when a change to one side could make the other **incorrect**. Most apparent couplings are really a **missing shared source**: if A and B both depend on a fact, state that fact once as its own authoritative chunk and [derive](#derivation) both from it (a hub), rather than coupling the peers. Reserve Coupling for consistency that genuinely **cannot** be factored into a single source.

**Example:** A request-schema [Chunk](#chunk) and a response-schema Chunk that must stay compatible — neither governs, but editing one should open a *re-verify* [Drift](#drift) on the other. Two docs that merely link to each other are **not** coupled.

## Decision

A choice the owner made about a product, recorded as one row of a specification's Decisions table: its human id such as `MYC-D45`, the question, the proposed default and the outcome with its date. A Decision is an [Entity](#entity) (kind `decision`, tag `dec`, shape `note`), keyed by a UUID that stands in the row's first cell in an HTML comment after the human id, invisible to readers and read by [Mycel](#mycel), and addressed by an [Entity URI](#entity-uri) `[dec:<uuid>:<title>]`. Mycel keeps it as a [Chunk](#chunk) of its own beside the section that holds the row, so that code and documents can name it as their [Origin](#origin) through an [Origin Link](#origin-link), and so that editing the row marks what rests on it [Stale](#stale) as a [Derivation](#derivation) does. The human id is its display name and is never edited; the row can move between chapters without changing identity, and a withdrawn id stays reserved. Its Discussion column names the chats in which it was taken, as chat Entity URIs; a discussion never makes the Decision stale. Contrast [Requirement](#requirement), which says what the product must do.

**Example:** `| MYC-D45 <!-- 9b6984cc-db34-4a84-b948-0eaefbea916a --> | What is a requirement or decision in the Index Store? | … | Decided 19 October 2026 by the owner: … |` is one Decision; `mycel read '[dec:9b6984cc-db34-4a84-b948-0eaefbea916a:…]'` returns the row and the content of the chats its Discussion cell names.

## Default Arbol Trunk

The first [Arbol Trunk](#arbol-trunk), created by behavior-preserving isolation of the chat communication implementation currently centered on `ChatSessionOrchestrator`. It is the compatibility baseline used while Root–Trunk process boundaries, complete Chat Session Event Sourcing, and side-by-side Trunk replacement are introduced. “Default” names this specific Trunk implementation, not a permanently privileged architecture role; later Trunks may be selected for future [Chat Exchanges](#chat-exchange). It is not the [Trivial Trunk](#trivial-trunk), the default Trunk of every Root in Arbol 2.

**Example:** During the first migration, all new Exchanges are assigned to a Default Arbol Trunk runtime even though old and new runtime generations may coexist during a safe rebuild.

## Delegate

The agent **role** of a background worker: an agent dispatched by another agent — the conversational agent in a regular [Chat Session](#chat-session), another Delegate, or a [Steward](#steward) — to perform bounded work off the main thread in an [Arbol-Initiated Chat Session](#arbol-initiated-chat-session), such as a [Companion](#companion), [Research Trip](#research-trip), or [Errand](#errand). Delegate is Arbol's word for a **background agent** or **subagent** — the canonical term for conversation and docs. The CLI that runs the agent session is `infer`, but `infer` is role-blind; being a Delegate is a property of how the agent was dispatched. As an [Initiator](#initiator), a Delegate is an agent that itself spawned a further session.

**Example:** Three Delegates run in parallel — one [Research Trip](#research-trip) and two [Errands](#errand) — while the agent in the parent Chat Session keeps the conversation with the [Leather Bag](#initiator) going.

## Dense Retrieval

Search **by meaning**: every [Chunk](#chunk) has an [Embedding](#embedding) — a short list of numbers (1024 here) in which *every slot is filled* and no single slot means a word; the meaning is spread across all of them together. A query is embedded the same way, and search returns the chunks whose vectors are **closest** — closest in meaning, regardless of wording. Called *dense* because the vector is densely packed with values, in contrast to [Sparse Retrieval](#sparse-retrieval)'s mostly-zero word-count vector. Intuition: a dense vector is a **coordinate on a map of meanings** — an individual number is as meaningless as a raw latitude, but *distance* between two coordinates is how related two texts are.

**Example:** The query "how is authentication handled" finds a chunk saying "the login flow validates credentials" — zero shared words, near coordinates on the meaning-map.

## Derivation

A directed edge in [Mycel](#mycel) recording **authority**: the **source** chunk governs, and the **derived** chunk must *conform* to it. Direction is about authority/conformance only — **not** creation order or who was written first (documenting existing code *recovers* the requirement that governs it; it does not derive the doc from the code). A derived [Chunk](#chunk) may answer to **several** sources (many-to-one). The edge stores the source's content hash **as last reconciled** (`hash_at_gen`); when the source moves past that mark, [Detection](#detection) marks the derived chunk [Stale](#stale), from which a [Drift](#drift) can be opened. Three flavours: a **generation edge** (the derived node can be mechanically (re)produced from the source), an **assertion edge** (a leather bag or agent *declares* the governs/conforms link via RPC), and a **declared edge** — an assertion made *in the derived document itself* via a [Source Ref](#source-ref), where the file is the truth: ingest keeps these edges exactly matching the refs, so removing a ref removes its edge. Contrast [Coupling](#coupling), which carries no authority.

**Example:** A requirement [Artifact](#artifact) governs the code that implements it — `artifact → code`, code derived. Edit the requirement and the code is flagged stale, in the right direction, regardless of which was written first.

## Design Token

An `--arbol-*` CSS custom property (colour/space/radius/type/shadow). The only way colour, space, radius, and type is expressed in the design system. Theme-invariant except colours. *(Distinct from a [Subscription](#subscription)'s auth token.)*

**Example:** `--arbol-space-3` or `--arbol-radius-card` should be used instead of hard-coded `12px`; `--arbol-color-accent` changes with the theme.

## Detection

The process that finds out-of-date derived [Chunks](#chunk): walk every [Derivation](#derivation) edge, compare the source's *current* content hash against the hash recorded on the edge (`hash_at_gen`); a mismatch marks the derived Chunk [Stale](#stale) — and staleness **propagates**: a chunk derived from a stale chunk is stale too. Pure hash comparison — cheap, no model calls — run at the end of every [Refresh](#refresh). [Heartwood](#heartwood) chunks are exempt: their truth is indexed to a past moment, so "source changed since" is a category error there. Detection only *marks*; opening [Drifts](#drift) for review and any regeneration are separate steps.

The designed refinement handles a source change on **two channels**, by *what kind* of change it is. A **content / meaning** change runs the [Drift Candidate](#drift-candidate) flow (change score → maybe re-verify dependents), so a typo never fans out. An **identity** change — a target renamed, moved, or removed — instead triggers cheap **resolution** checks on the [References](#reference) pointing at it; a broken pointer is a "fix the link" item, no re-verification needed.

**Example:** Editing a plan section that two [Summary Nodes](#summary-node) were built from → the next Detection marks both Stale, and the "Regenerate stale (2)" badge lights up in [Seqoya Lab](#seqoya-lab).

## Draft

Composer input—text, attachments, and related editable selections—that the [Leather Bag](#leather-bag) has not sent yet, before a [Chat Exchange](#chat-exchange) is accepted. A Draft belongs to Arbol: the Arbol backend keeps it in Arbol's own tables of the Root's database, apart from the chat tables a Trunk writes (see [who writes what](architecture/00-components-and-boundaries.md#who-writes-what)). It may have durable, coalesced revisions so it survives a restart of a UI or of the backend, and so speculative [Activity Executions](#activity-execution) can identify the exact [Text Snapshot](#text-snapshot) they observed. Sending hands the message to a Trunk: once the Trunk accepts it, it is the Exchange's [Authoritative Input](#authoritative-input); when it is refused, nothing starts and the Draft stays in the composer ([the Exchange steps](architecture/02-chat-exchange-across-components.md#the-steps)). Abandoning a Draft starts no Exchange.

In version 1 a Draft was placed inside a provisional, Trunk-owned Chat Exchange, which abandoning the Draft closed or cancelled; the implementation stored new-chat Drafts on their own and made the chat's record only on Send.

**Example:** The Leather Bag types in a new chat's Composer, and several coalesced revisions may trigger speculative Cue extraction. On Send a Trunk accepts the text, and a Chat Exchange begins. Had the database been away, the message would have been refused, and the Draft would have stayed in the Composer.

## Drift

The work item [Mycel](#mycel) opens when a [Drift Candidate](#drift-candidate) **fails re-verification** — its [trust score](#attestation) fell below threshold, confirming a `derived` or [Coupled](#coupling) [Chunk](#chunk) is genuinely out of sync (its source changed in a way that broke conformance, the source was removed, or an upstream chunk is itself stale). A Drift records **every** contributing source, not just one. Surfaced in [Seqoya Lab](#seqoya-lab)'s Refresher for review. Detection-only: a Drift says something needs attention — it does not fix it. (A benign source change that survives re-verification is reconciled silently and never becomes a Drift — see [Drift Candidate](#drift-candidate).)

**Example:** Editing the documented token TTL drops a derived chunk's trust score below threshold → a Drift, naming the changed source. Fixing a typo in that same source would not: its candidates re-verify clean and reconcile silently.

## Drift Candidate

A **suspected** [Drift](#drift), not yet confirmed. When a source [Chunk](#chunk) changes, the change is first scored **on the source itself** — a **change score** measuring how much its *meaning* moved (a typo or reword scores low; a redefinition scores high). Below threshold the change is surface-only: every [derived](#derivation) or [Coupled](#coupling) dependent is **reconciled** outright (its `hash_at_gen` advanced) with **no fan-out**. Only when the change score clears the threshold do those dependents become Drift Candidates — each a hint it *might* now be out of sync.

A cheap **re-verification** then runs on each candidate and yields a [trust score](#attestation):

- **trust holds** → **reconcile**: bump `hash_at_gen` to the new source version, close the candidate;
- **trust drops below threshold** → promote to a real [Drift](#drift).

So **two gates**: the *change score* on the source decides whether to fan out at all (a typo never re-verifies its dependents); the *trust score* on each dependent decides reconcile-vs-Drift. Together they stop hash-churn from flooding [Drifts](#drift) — only meaning changes that actually erode a dependent reach a person. Because closing a candidate is the *trust-asserting* (dangerous) direction, an **unsure** verifier escalates to a Drift rather than reconciling silently. Re-verification resolves the [Repo](#repo) to its highest-priority clearing [Ladder](#ladder) and climbs the rungs as a [Delegate](#delegate) — rung 1 (cheapest) first, stepping up only when confidence stays low. If **no** Ladder clears the Repo, re-verification can't run at all: Arbol raises an explicit error to the user rather than silently reconciling or opening a Drift.

**Example:** A typo fix scores below the change-score threshold → its dependents reconcile with no re-verification at all. Rewording the definition of "Errand" scores high → its dependents become Drift Candidates → the ones that actually relied on the old meaning fail re-verification and become Drifts.

## Diff

The computed set of code changes produced by comparing two Git states. A Diff is the result, not the choice of comparison boundary and not the component that renders it. When precision matters, say **Diff View** for the selected boundary and **Hunk Review** for the inspection component; use “diff” only for the resulting file and line changes.

**Example:** Selecting the `parent` Diff View constructs a Diff that Hunk Review displays.

## Diff View

One selected Git comparison boundary for a Worktree. The shared **Diff View Switcher** presents these four options in this fixed order:

1. **uncommited** — the staged and unstaged working-copy delta from `HEAD`; no committed branch changes are included.
2. **commit** — `HEAD` compared with `HEAD^`; working-copy changes are excluded.
3. **parent** — all committed and working-copy changes on the current branch relative to the branch from which it was created. It is unavailable when that parent cannot be resolved.
4. **main** or **master** — all committed and working-copy changes relative to the repository’s one resolved primary branch. Arbol presents only the resolved name, never both. The view is unavailable when that primary branch is already checked out.

The Diff View Switcher is a presentation and loading-policy control; Git/RPC ownership remains with its host. It must use the same semantics in Worktree status and Change Walkthrough. It never keeps a disabled Diff View selected: on the primary `main` or `master` Worktree, selecting or carrying `parent` or the primary-branch view normalizes immediately to `uncommited`. Its primary-branch option displays exactly the resolved branch name—`main` or `master`—never a combined label.

**Example:** On `feature/login`, selecting `commit` constructs the Diff for only the latest commit. Selecting `main` constructs the Diff containing that commit plus staged and unstaged edits since divergence from `main`.

## Driver

The code that speaks one provider's CLI/API and Arbol's request protocol (`drivers/claude/`, `drivers/codex/`, …). Build-agnostic and subscription-agnostic. One Driver per [Provider](#provider); several [Intelligence Providers](#intelligence-provider-ip) can share it.

**Example:** The Claude driver knows how to talk to Claude Code, while the Codex driver knows how to talk to Codex; both translate provider behavior into Arbol events.

## Driver Instance

A concrete, versioned build of a [Driver](#driver), identified `<provider>@<build_id>` (e.g. `claude@20260612T135543Z-…`). The unit that is started, run side-by-side during a safe rebuild, drained, and garbage-collected. One or more [Intelligence Providers](#intelligence-provider-ip) route to one Driver Instance per [Build](#build). *(Not "daemon" — that term is reserved for [Arbol Root](#arbol-root) and [Effector](#effector) background processes. The binary/socket/launchd filenames, e.g. `arbol-driver-claude` / `driver.claude.sock` / `com.arbol.driver.claude`, are implementation details.)*

**Example:** `claude@20260612T135543Z-a1b2c3` and `claude@20260613T090000Z-d4e5f6` can run side-by-side while Agent Attempts pinned to the old instance drain.

## Effector

The daemon that executes and settles [Tool Requests](#tool-request): run / run-always / reject.

**Example:** If an agent asks to run `rm -rf build`, the Effector classifies the request and can reject it instead of executing it.

## Elma Chat

The conversation [UI](#ui): a [Chat Session](#chat-session) rendered as a branching tree of [Turns](#turn).

**Example:** A user asks “fix the failing tests” in Elma Chat, then branches from an earlier turn to try a different solution.

## Elma View Page

The second column of [Elma Chat](#elma-chat), which renders any document for read-only viewing.

**Example:** While chatting, the user opens `README.md` or a generated patch in the right-hand read-only column.

## Embedding

A [Chunk](#chunk)'s semantic vector: a 1024-dimension representation of its meaning (Voyage `voyage-code-3`, stored in pgvector), used for [Dense Retrieval](#dense-retrieval) — finding chunks by *what they mean* rather than what they literally say (contrast [Sparse Retrieval](#sparse-retrieval)). An Embedding is bound to the content it encoded: when [Ingest](#ingest) sees a chunk's content change, the vector is **cleared** and the chunk becomes **pending**; the next [Sync Pass](#sync-pass) re-embeds only the pending chunks (the *embed delta*), so vectors never silently describe old text.

**Example:** A query for "retry with backoff" finds `completion.py#complete` even though the code never says "backoff" — the Embeddings of query and chunk are close in meaning-space.

## Embedding Provider

The **standalone app that holds the warm on-device embedding model** — `mycel_embedder` (`embedder/`), serving `POST /embed` + `GET /healthz` on localhost HTTP (`127.0.0.1:7331`; `MYCEL_EMBEDDER_URL` overrides). Holding a ~640 MB ONNX session is an *application's* nature, so it lives outside [Mycel](#mycel), which stays per-task and residency-free: Mycel's local-embedding module is a thin HTTP client, and one of Mycel's exactly **two optional outward edges** (the other being the completion provider). Venv-run — no build, no signing, no launchd required; Arbol mode wraps it in launchd for convenience. Provider absent → retrieval degrades to lexical-only with a start-command message; nothing errors. Company-repo text still never leaves the machine — inference is in-process CPU onnxruntime inside the provider.

**Example:** `python -m mycel_embedder serve --preload` in a terminal is a fully functioning setup; kill it and `arbol search` still answers, BM25-only, telling you how to start it back.

## Email Source Item

One durable, provider-message-level input to email automation. Its private external capture is stored raw-first under `~/Artifacts/mirrors/emails/`; a versioned Normalizer writes canonical text, structured metadata, and sanitized HTML under `~/Artifacts/emails/`. Root keeps a rebuildable index with provider message/thread identity, an immutable acceptance sequence, content hash, provenance paths, and evidence-based completeness (`preview`, `partial`, `rendered_complete`, or `raw_complete`). Gmail DOM captures may be `rendered_complete`, never `raw_complete`.

**Example:** One rendered notification inside a Gmail conversation becomes an Email Source Item distinct from the inbox-row/thread preview and from other messages in that conversation.

## Embedder Profile

Per-[Repo](#repo) setting naming **which embedding model** the repo's [Chunks](#chunk) are embedded with: `voyage` (the external Voyage API — personal repos only) or `local` (on-device `Qwen3-Embedding-0.6B` via ONNX — company repos, whose source must never reach an external API; both are 1024-d, so they share one vector column). The profile **is** the interlock: embedding routes every pending chunk by its repo's profile, so a local-profile chunk is structurally unreachable by the external API — and queries embed with the same model as the repo's stored vectors.

**Example:** `Arbol → voyage`; a repo with restricted source → `local` — its chunks embed on-device; no path sends its source to Voyage.

## Entity

Any first-class Arbol citizen — an MR, a commit, a git [Branch](#branch), a ticket, a glossary term, a [Chat Session](#chat-session), an email, a Slack message, an artifact, a requirement, an invariant — and more kinds as they are added. Entities are numerous and get connected to one another by [Entity Edges](#entity-edge). Rendered uniformly on every [Surface](#surface) via `EntityChip` / `EntityCard` — never re-styled per Surface. An optional **state** value recolours an entity (an `mr` green when `merged`, a ticket red when `blocked`). See also: [Entity Kind](#entity-kind), [Entity Shape](#entity-shape), [Entity Edge](#entity-edge). Kinds (tags lowercase):

| kind | tag | shape |
| --- | --- | --- |
| `ticket` | tic | mark |
| `saga` | sag | note |
| `mr` | mr | mark |
| `commit` | cmt | mark |
| `slack` | slk | mark |
| `email` | eml | mark |
| `communicado` | com | mark |
| `chat` | cht | span |
| `artifact` | arf | note |
| `requirement` | req | note |
| `decision` | dec | note |
| `invariant` | inv | note |
| `glossary` | glo | note |
| `secret` | sec | note |
| `flyer` | fly | note |
| `branch` | brn | note |
| `living_topic` | liv | note |
| `mandate` | mnd | note |
| `prompt` | pmt | mark |
| `response` | rsp | mark |

**Example:** A ticket, a merge request, a [Chat Session](#chat-session), and a glossary term are all Entities, so the UI renders each as an `EntityChip` or `EntityCard`.

## Entity Card

The reusable, standalone UI representation of one [Entity](#entity), addressed by an [Entity URI](#entity-uri). In its initial collapsed state it shows the title decoded from the URI without resolving Entity data. **See more** expands the card to show its [Entity Card Content](#entity-card-content); **See less** hides that content without changing it. The content may already have been supplied—for example, when a context attachment was created—or the first expansion may invoke the [Entity Card Resolver](#entity-card-resolver) supplied for that use. The card owns the consistent shell, disclosure, loading, empty, error, and retry behavior. It hides locator syntax and other technical identifiers during ordinary display. It is the canonical detailed Entity rendering on every graphical [Surface](#surface), not a Surface-specific card.

**Example:** A collapsed ticket Entity Card shows “Remove Feature Toggle”; choosing **See more** reveals its context-specific Entity Card Content, and **See less** returns to the title-first summary.

## Entity Card Content

The plain source string shown in an expanded [Entity Card](#entity-card). It may contain Markdown, but it is data—not an arbitrary UI component or a separate hidden agent payload. An [Entity Card Resolver](#entity-card-resolver) fetches the relevant Entity data, selects and redacts fields for one use, and composes this string. When an Entity Card is attached as Chat context, that same source string is persisted with the attachment: the UI renders it for **See more**, and the active [Arbol Trunk](#arbol-trunk) sends the same semantic content to the agent when appropriate. Rendering Markdown blocks or adding an explicit transport wrapper is allowed; independently projecting, enriching, or substituting different agent-only content is not. Creating the context attachment may therefore resolve and persist its content eagerly, even though **See more** controls only whether the user currently sees it. Attaching it as a [Chat Note](#chat-note) does not itself trigger an agent response.

**Example:** A Turn Inspection Result card stores one Markdown string containing the selected source Chat Session and inspection fields. The user can inspect that string with **See more**, and the next Turn gives the agent that same content.

## Entity Card Resolver

A use-case-specific function that receives a parsed [Entity URI](#entity-uri), fetches any required data, selects and redacts fields, formats them, and returns [Entity Card Content](#entity-card-content) as a plain string. Different resolvers may return different content for the same Entity because the useful context depends on where the card is used. Entity Card owns display and disclosure behavior; the resolver owns the content. A normal inspectable card may invoke its resolver lazily on the first **See more**. A durable Chat-context attachment invokes its resolver when the attachment is created and persists the returned string, so the later agent context does not depend on whether the user expanded the card.

**Example:** A Turn Inspection Result resolver for Chat context can compose a Markdown string containing the source Chat Session and selected inspection fields, while another resolver for the same Entity can return a shorter operational summary.

## Entity Chip

The reusable compact UI representation of an [Entity URI](#entity-uri). It parses the URI and renders the decoded Base64 title as its only visible content, hiding the raw URI, Repo code, Entity Kind token, Arbol database ID, and encoded title. Rendering is request-free: the chip never resolves Entity data merely to display itself. **Cmd-click** activates the shared **Go to** behavior, which routes to the Entity's destination according to its Entity Kind; any lookup needed for navigation happens only after that explicit interaction, not during rendering. It is the canonical compact Entity rendering on every graphical [Surface](#surface), not a Surface-specific badge.

**Example:** `[myc:arf:9b6984cc-db34-4a84-b948-0eaefbea916a:VG9vbCBDYWxscw==]` renders as a compact Entity Chip titled “Tool Calls”, without displaying `myc`, `arf`, the UUID, or the Base64 text.

## Entity Context Menu

The shared UI **context menu** displayed for any component associated with an [Entity](#entity), including Chat Session cards, tickets, and Sagas, Arcs, and Beats. It provides the Entity-generic actions **Link to entity…** and **Send to** → **Saga**, **Arc**, **Beat**, or **Spotlight**. Entity types and host surfaces may extend it with additional, entity-specific items; those additions appear after the shared actions and do not replace them. The component is implemented in the design system as `openEntityContextMenu` and attaches to Entity-backed chips, cards, rows, and detail surfaces through `entityLinkTarget`.

**Example:** Right-clicking a Chat Session card opens its Entity Context Menu, where **Send to → Spotlight** adds that Chat Session to the current Spotlight; a ticket may also show ticket-specific actions below the common section.

## Entity Edge

A typed relationship between two [Entities](#entity) — the connections that turn the entity set into a graph.

**Example:** A requirement Entity has an edge to the ticket that requested it, and a merge request Entity has edges to the commit Entities it contains.

## Entity Kind

An [Entity's](#entity) type (`ENTITIES.KINDS`): glyph + tag + label + [Entity Shape](#entity-shape) + hue. Keys are stable; the set extends as kinds are added. Its tag is the `short-entity-type` used in an [Entity URI](#entity-uri) and is limited to at most three characters. This three-character limit applies only to Entity Kind tags, not to Repo short codes.

**Example:** `mr` renders with the MR tag and its configured hue; `glossary` uses `glo` as its URI tag.

## Entity Shape

How an [Entity](#entity) renders in time: **span** (has duration → a bar; live → grows to [Now Line](#now-line)) · **mark** (a point in time → a dot + chip) · **note** (durable/authored → listed and inspected; pins to a time as a mark).

**Example:** A [Chat Session](#chat-session) block is a `span` (it has duration; live → grows to the [Now Line](#now-line)); a commit is a `mark` (one point in time); a requirement is a `note` (durable knowledge).

## Entity URI

A plain-string locator for one [Entity](#entity), with either form `[<short-repo>:<short-entity-type>:<entity-id>:<title-base64>]` or `[<short-entity-type>:<entity-id>:<title-base64>]`. The surrounding square brackets and three or four non-empty parts are required. `short-repo` is optional: when present, it is the Repo's registered short code and carries [Repo](#repo) context; it is not restricted to three characters. Repo-less Entities such as prompts and responses normally use the three-part form. Omitting `short-repo` is semantically equivalent to the explicit `any` Repo code: parsers normalize a three-part URI to `any`, never to a null Repo value. `[any:...]` remains a valid explicit spelling when a four-part URI is useful. `short-entity-type` is the [Entity Kind](#entity-kind)'s registered tag and is limited to at most three characters. `entity-id` is the Entity's ID in the Arbol database, never an ID from an external system. `title-base64` is the Base64 encoding of a UTF-8 title or other human-readable description selected when the URI is created. Entity identity is the pair `(short-entity-type, entity-id)`: neither `short-repo` nor `title-base64` participates in identity. The Repo code is routing/provenance context, and the encoded title is a stable display snapshot that lets a [Surface](#surface) render a useful, request-free [Entity Chip](#entity-chip).

An Entity's canonical Entity URI is generated when the Entity is created and stored in the Arbol database with the Entity. The creation path derives or copies an appropriate display title from the Entity data, Base64-encodes it, and persists the resulting URI; consumers copy that stored URI rather than repeatedly choosing a title and regenerating it. An ordinary later title change does not automatically rewrite already stored or distributed Entity URIs. If another URI carries a different title snapshot but the same Entity Kind tag and Entity ID, it still identifies the same Entity. The code-level type name is `EntityUri`.

| Repo | short-repo |
| --- | --- |
| Arbol | `arb` |
| Mycel | `myc` |
| Universe | `uni` |
| Infer | `inf` |
| Blueprint | `blue` |

**Examples:** `[pmt:message-1:UGxlYXNlIGluc3BlY3Q=]` (“Please inspect”) · `[rsp:turn-1:RG9uZQ==]` (“Done”) · `[arb:arf:903b027c-4af2-46db-a47a-7763e45ae8d8:VHVybiBDb21wb3NpdGlvbg==]` (“Turn Composition”) · `[myc:arf:9b6984cc-db34-4a84-b948-0eaefbea916a:VG9vbCBDYWxscw==]` (“Tool Calls”).

## Env Keepers

The **gitignored-but-precious files** a fresh checkout or worktree needs but git will not carry: `.env*` files, `.npmrc`, IDE configs, local-dev patches. Backed up path-preserving under `~/.arbol/env-backups/<repo>/`, and **seeded into every new worktree** by `mycel wt add` (existing files are never overwritten) — so a [Worktree Container](#worktree-container) worktree is dev-ready without hand-copying secrets. The backup dir doubles as the home for salvage patches (e.g. unlanded work rescued from old stashes). When you create a new keeper file, add it to the backup dir too — that is what future worktrees inherit.

**Example:** a service repo's per-service `.env.*.local` files land in every new task or review worktree automatically; without the seed, half the services fail to boot locally.

## Errand

An [Arbol-Initiated Chat Session](#arbol-initiated-chat-session) for one-off background work the dispatching agent could have done itself but delegates — usually to run tasks in parallel. Run by a [Delegate](#delegate). Distinct from a [Research Trip](#research-trip) (which only gathers and reports back) and a [Routine](#routine) (which recurs): an Errand does a discrete piece of work, **once**.

**Example:** While the agent in the parent Chat Session keeps talking to the [Leather Bag](#initiator), it fires an Errand to update the changelog in a worktree, then folds the result back in.

## Event Log

The single source of truth: an append-only, ordered, durable record of facts. Everything else is derived from it. In the Arbol Trunk target architecture, Trunks author chat facts and append them through an independently supervised **Event Log service** backed by required PostgreSQL storage; [Arbol Root](#arbol-root) replays those facts for projections and UIs. The service owns ordering, idempotency, validation, replay, and database-facing persistence, but not chat orchestration.

If the Event Log service or PostgreSQL briefly restarts, Trunks remain alive and retain their Exchanges but pause at durability boundaries until they reconnect and reconcile. Root must show an explicit database/service-unavailable error while the dependency is down. See also: [Aggregate](#aggregate), [Fold / Projection](#fold--projection), [Fanout](#fanout).

**Example:** Instead of storing “current chat text” as the source of truth, Arbol stores events such as message appended, tool requested, and tool settled. Root can restart and rebuild its view while independently running Trunks and the Event Log preserve the conversation.

## Event Log Service

The independently supervised Arbol daemon that provides the stable append, read, replay, subscription, ordering, optimistic-concurrency, idempotency, validation, and upcasting boundary for the [Event Log](#event-log), backed by required PostgreSQL storage. It persists facts authored by [Arbol Trunks](#arbol-trunk) and serves replay to [Arbol Root](#arbol-root), but it does not select Trunks, run Activities, invoke agents, settle tools, or implement UI policy. Old and new Trunk Runtime generations may use compatible versions of its protocol concurrently.

If the Event Log Service or PostgreSQL restarts briefly, Trunks remain alive and retain Exchange ownership but pause at durability boundaries, reconnect, reconcile by stable identities and revisions, and continue. PostgreSQL unavailability is a hard application error, not a degraded mode that permits unrecorded chat effects.

**Example:** Root is killed while a Default Trunk continues an Exchange. The Trunk keeps appending facts through the still-running Event Log Service; a later brief PostgreSQL restart pauses the Trunk for several seconds without failing or duplicating the Exchange.

## Event Sourcing

The architecture in which accepted state changes are represented first as immutable facts in an [Event Log](#event-log), while current state, guards, timelines, and UI views are deterministic folds or projections of those facts. Event Sourcing is an architectural method, not a process: [Arbol Trunks](#arbol-trunk) author chat facts, the [Event Log Service](#event-log-service) persists them, and [Arbol Root](#arbol-root) rebuilds presentation projections from them. High-frequency transient token deltas need not be individual events, but consequential Chat Session, Exchange, Activity, agent, tool, and outcome facts must be recoverable and causally inspectable.

**Example:** After Root restarts, it replays Chat Session and Chat Exchange events to reconstruct messages, active work, pending Action Items, and owning Trunk Runtimes instead of trusting the process state it lost.

## Exchange Assignment

The acceptance boundary that binds a new [Chat Exchange](#chat-exchange) to its [Arbol Root](#arbol-root), selected Trunk Build and process. The Root manager starts the selected compatible Build with the resolved route and Root. The Trunk writes the Exchange record in that Root's folder and the submitted message in its database before reporting acceptance. From acceptance to the final state the Exchange is Trunk-owned and retains its `root` and Trunk Build. It continues when the manager or Arbol is absent; it is never reassigned by a Build or Root change. If input is refused before acceptance, the Draft stays in the composer. See [the Exchange steps](architecture/02-chat-exchange-across-components.md#the-steps).

This replaces the legacy assignment to a resident Trunk Runtime generation. There is one process per accepted Exchange; the precise command and file formats, including duplicate-submission handling, belong to the [Root Contract](#root-contract) ([RCT-2](../arbol-root/contract/02-starting-stopping-and-settling.md#a-repeat-after-a-lost-answer): a repeat with the same Exchange identifier starts nothing) and are not specified by this definition.

**Example:** First Sapling's manager starts research Trunk Build `a3` for Exchange E4. The Trunk records E4's First Sapling `root`, Build and process, writes its input and acknowledges acceptance. Opening a second Root later does not move E4; it finishes in First Sapling.

## Fanout

Pub/sub delivery of appended events to live subscribers.

**Example:** When Root appends a new turn event, Elma Chat and a status bar subscriber both receive the update live.

## Flyer

An [Entity](#entity) (kind `flyer`, tag `fly`): any excerpt of text carrying important information, extractable from any other Entity. *(Planned feature.)*

**Example:** A key paragraph lifted out of a long design doc or [Chat Session](#chat-session) becomes a Flyer that can be linked and surfaced on its own.

## Fold / Projection

A deterministic reduce over [Event Log](#event-log) events into a derived view (a read model in [Arbol Root](#arbol-root), `project()` in a UI). Disposable and rebuildable.

**Example:** To render a conversation tree, the UI folds message and branch events into the current tree; deleting the projection is safe because it can be rebuilt from the Event Log.

## Font Scale

`--arbol-font-scale` (and `--arbol-content-font-scale`). The Header A−/A+ control scales all text through it.

**Example:** Clicking A+ in the header increases `--arbol-font-scale`, making chat text, labels, and cards larger without changing each component separately.

## Free-standing

The **default connectivity state** of a [Chunk](#chunk): no [Derivation](#derivation) or [Coupling](#coupling) touches it — nothing governs it, it governs nothing, no consistency obligation binds it. Not a defect and not a backlog: in a corpus where most code has no documentation, free-standing is the honourable normal — edges are *earned* (asserted by a leather bag or created by [Generation](#generation)), never presumed. Orthogonal to **role** (a free-standing code chunk is still `authored`) and to [Heartwood](#heartwood) (connectivity vs temporality — three separate axes with [role](#chunk)). [Detection](#detection) has nothing to check on it, so it can never be [Stale](#stale); it participates in [Retrieval](#retrieval), and that is the whole of its obligations.

**Example:** Nearly every chunk of a large repo's [Code Corpus](#code-corpus) is free-standing — searchable, `authored`, bound to nothing. Asserting "this requirements [Artifact](#artifact) governs that service" ends the free-standing state of exactly those chunks, and no others.

## Generation

<!-- mycel:cues
literal: exclude
target-scope: local_section
-->

The umbrella for [Mycel](#mycel)'s **productive** side: *producing or regenerating* a `derived` [Chunk](#chunk) from its source(s) — as opposed to [Detection](#detection), which only notices what's out of date. Always model work, always deliberately triggered (never part of a [Sync Pass](#sync-pass)); its output starts [Unattested](#attestation) until verified. Concrete instances: **[RAPTOR Summarization](#raptor-summarization)** and **[Stale Summary Regeneration](#stale-summary-regeneration)** (built); *doc-from-code generation* (recreate documentation from the [Code Corpus](#code-corpus) with source→derived edges) and *drift-driven doc regeneration* via a [Routine](#routine) (planned).

**Example:** A [Routine](#routine) could regenerate a stale "API reference" [Chunk](#chunk) from the code it derives from, then leave it Unattested for a competent reviewer — that's Generation; the [Detection](#detection) that flagged it stale is not.

## Hold

To **hold** or **book** **Beaver Workspace** means an agent has started
working there and reserved the complete area for that work. The verbs are
synonyms; a **hold** or **booking** is the resulting reservation. Ending it
is [Release](#release). Existing ownership and territory rules remain those
of [Working in Sagas](../mycel/operations/sagas.md#holds).

**Example:** "Hold Beaver Workspace" and "Book Beaver Workspace" mean the
same operation.

## Hunk Review

The shared component that displays a selected **Diff** as changed files, code changes, and the commit information relevant to its current [Diff View](#diff-view). Hunk Review does not create or persist views: its host selects the Diff View and supplies the constructed Diff.

**Example:** Change Walkthrough hosts Hunk Review after the Leather Bag chooses `parent` in the Diff View Switcher.

## H-Nex

**Human nex**: the human participant in a continuing [Nex](#nex) partnership, with their own experience, knowledge, goals, judgment, and responsibilities. The `H-` prefix identifies the kind of participant; it does not assign a permanently supervisory or student role. An H-Nex may understand one domain more deeply than an [A-Nex](#a-nex) while relying on it in another. Technical contribution can include architectural reasoning, decisions, evaluation, and accountability even when the H-Nex rarely writes code.

An H-Nex's knowledge varies by domain and develops over time. The [Nex Knowledge Map](#nex-knowledge-map) describing it is a revisable estimate across projects and conversations. General domain familiarity and understanding the reasoning behind a particular piece of agent work are distinct. One H-Nex may collaborate with several A-Nexes. [Leather Bag](#leather-bag) remains the operational term for the person driving Arbol; H-Nex names that person's role in the partnership.

**Example:** An H-Nex joining a company knows software architecture but is unfamiliar with its systems. Their A-Nex explains the missing organizational context, while the H-Nex contributes architectural judgment and later helps the A-Nex understand newly learned domain constraints.

## Heartwood

A document whose **truth-conditions are frozen in time**: a past research note, task write-up, or design snapshot that was accurate *then* and makes **no claim about the present** — so no present change can falsify it. *(Completed plans are not heartwooded — `plans/` docs are deleted when their work ships, after re-homing any durable content; see the INDEX conventions.)* Named for a tree's core wood: no longer living, still load-bearing. Declared **in-band**, in the file itself — frontmatter `status: heartwood`, with two optional free-form time pins answering the two questions an outdated document raises: `implemented:` (when it became true — first commit/date) and `outdated:` (when it stopped being true — last commit/date). Behaviour: exempt from [Detection](#detection) and [Drifts](#drift) (its [Derivation](#derivation) edges degrade to historical annotations; any open Drift on it is closed), excluded from [RAPTOR Summarization](#raptor-summarization) clustering (summaries describe the *current* corpus), never a [Generation](#generation) target — but still ingested by every [Sync Pass](#sync-pass) and fully searchable via [Retrieval](#retrieval), where hits carry a badge so a record can never masquerade as current truth. With a commit pin, a Heartwood artifact is an **index into git history**: semantic search finds the era, `git show <pin>:<path>` reads the actual code of that era — [Mycel](#mycel) stores no past versions itself (git is the time machine; when a living document is substantially rewritten, snapshot the old version to a dated file marked heartwood — one file, one moment).

**Example:** `operations/archive/deep-research-cursor-era.md` — the snapshot of the engine that powered deep-research before its successor: marked heartwood with `implemented: 2026-03` / `outdated: 2026-07-05`. It stops appearing in Drifts and summaries, but "how did the Cursor-era phase loop work?" still finds it — badged heartwood.

## Identity Reconciliation

The step of [Ingest](#ingest) that decides, for every chunk candidate produced by [Chunking](#chunking), *which stored [Chunk](#chunk) it is* — so a chunk's immutable id, and everything hanging off it ([Derivations](#derivation), [Embedding](#embedding), history), survives edits and renames instead of being destroyed and recreated.

Within one file, candidates are matched against the stored chunks in two rounds:

1. **By natural key** (heading path for documents, `path#symbol` for code): a match means *same chunk* — **unchanged** if the content hash also matches, **edited** if not.
2. **By content hash**, for candidates with no key match: identical content under a new key means the chunk was **renamed** (a heading reworded, a function renamed) — it keeps its id, and the old key is remembered.

Whatever matches neither round is **new** (fresh id); stored chunks left unmatched are **orphaned** (kept and flagged absent — never deleted). Every decision — unchanged / edited / renamed / new / orphaned — is recorded in the **identity log**, the audit trail of why each chunk kept or changed identity.

**Example:** Renaming `## Retry policy` to `## Backoff policy` without touching its body → round 2 matches by content: same Chunk, same id, edges and vector intact, decision `renamed`. Editing one sentence in it instead → round 1 matches by key: decision `edited`, vector cleared, downstream flagged by [Detection](#detection).

## Ignore Rule

Mutable user configuration that prevents a matching external source from being retained, displayed, parsed, classified, or used to emit future [Signals](#signal). Email Ignore Rules match one canonical sender or one domain plus label-bounded subdomains and are enforced by [Arbol Root](#arbol-root) before private Artifact writes. Creating one purges matching retained source/derived content and suppresses matching local Signals while retaining only invisible correctness tombstones; removing it permits later provider synchronization but does not restore purged content.

**Example:** Ignoring domain `com` intentionally suppresses every sender in `.com`; the confirmation previews the impact rather than prohibiting that broad rule.

## Index Store

[Mycel](#mycel)'s own PostgreSQL database with ParadeDB, at the address its settings name, holding the [Chunks](#chunk), their versions and vectors, the edges ([Derivations](#derivation), [Couplings](#coupling) and [Origin Links](#origin-link)), the marks such as [Stale](#stale), the [Requirement](#requirement) and [Decision](#decision) entities, and the record of its work. It is a different database from Arbol's: Mycel reads Arbol's database as data when a decision's discussion is shown, and writes nothing there. Most of the Index Store can be made again from the files; what exists nowhere else is what a person asserted or confirmed in it, such as stated Origin Links.

**Example:** `mycel init` makes the structure of the Index Store at the address in `~/.mycel/config.toml`, and `mycel ingest` fills it from the repository's files.

## Ingest

The operation that synchronizes one [Corpus](#corpus) into [Mycel](#mycel)'s stored graph. Three steps, in order: **[Scan](#scan)** (read files, hash them, skip the byte-identical ones) → **[Chunking](#chunking)** (split each changed file into chunk candidates) → **[Identity Reconciliation](#identity-reconciliation)** (decide which stored [Chunk](#chunk) each candidate is). After reconciliation, each changed chunk's content hash is recorded and its [Embedding](#embedding) cleared, making it *pending* for the next embed. Mechanical — no model calls; runs per-corpus (an Artifact-Corpus ingest and a Code-Corpus ingest are the same operation over different roots and chunkers).

**Example:** After a refactor touching two files, Ingest re-reads the corpus but only those two files pass [Scan](#scan); five symbols come back `edited`, one `renamed`, the rest of the corpus is untouched.

## Initiator

The actor that started a [Chat Session](#chat-session) — a property of every session, not a separate type. An Initiator is either a **[Leather Bag](#leather-bag)** (a person at the keyboard — *Leather Bag*, not "user", because not every user of Arbol is a person) or an **agent**. Agent Initiators include the conversational agent in another Chat Session, a [Delegate](#delegate), and a [Steward](#steward); provenance preserves the actual agent identity, its role where applicable, and its parent Chat Session. A Leather-Bag-initiated session is the live conversation; an agent-initiated one is an [Arbol-Initiated Chat Session](#arbol-initiated-chat-session). Initiator is *who started it* — independent of both the authority under which it acted and whether the result can be trusted. For a Steward, provenance therefore records the Steward as Initiator and the [Mandate](#mandate) version used. Trust is a separate axis earned by verification, see [Attestation](#attestation) (a Leather-Bag-initiated session is not authoritative just because a person kicked it off).

**Example:** A Chat Session opened in [Elma Chat](#elma-chat) has Initiator = Leather Bag; a Research Trip spawned from it has Initiator = the actual conversational agent; an [Errand](#errand) that Research Trip spawns in turn has Initiator = its [Delegate](#delegate); a scheduled monitor that decides to open a new investigation has Initiator = its [Steward](#steward).

## Instructions Hub

The **one stable address every knowledge consumer memorizes**: `~/Artifacts/mycel/README.md` — in the Mycel corpus, which owns everything about *how to work* (operations, tools, blueprints, chains, skills). (`~/Artifacts/Arbol/README.md` is now a redirect stub, so the old address still resolves.) Claude Code skills, codex agents, Arbol [Chat Sessions](#chat-session), and humans all point there and only there; the file is a **router** — a route-by-need table into [Operations](#mycel-operation), [Blueprints](#blueprint), [Runbooks](#runbook), and the glossary — so documents move freely underneath without any consumer changing. Its rows are **task shapes, never individual documents** (~ten, stable); document growth is absorbed by the families, selection within a family belongs to retrieval (`arbol search`). Invariant: if the table outgrows one screen, a family is missing — add a family, not rows. Deliberately NOT a catalog (that is [INDEX](#index)'s job) and not a monolith — each routed document keeps its own [Source Refs](#source-ref) and [Detection](#detection) coverage. Each repo's glossary carries a single pointer to it, closing the repo-scoped-retrieval gap (this knowledge lives in repo `mycel`, invisible to another repo's scoped search).

**Example:** a codex agent in a repo worktree searches "how to run deep research", hits that glossary's pointer entry, opens `~/Artifacts/mycel/README.md`, and routes to the deep-research Blueprint — three hops, zero per-feature pointers.

## Intelligence Provider (IP)

A configured, build-agnostic way to run inference: a [Driver](#driver) + a bound [Subscription](#subscription) + repo rules + a **default** model + thinking, **spanning all the models that provider offers** (the default is just that — a default, not the only model it may run). A given run can pin a specific model + thinking via a [Brain Recipe](#brain-recipe), still subject to the IP's repo rules. The unit [Seqoya Lab](#seqoya-lab) manages and a [Chat Session](#chat-session) is pinned to. Deployed IPs: `bro-claude`, `safe-claude`, `codex`, `cursor`. Several IPs can share one Driver — `bro-claude` and `safe-claude` both run on the `claude` Driver; [Arbol Root](#arbol-root) hands the IP's bound Subscription token to the Driver per [Turn](#turn), so the Driver itself is subscription-agnostic. **IP refers to this layer only.**

**Example:** `safe-claude` pairs the Claude driver with Alex’s Claude subscription, a default model + conservative thinking, and strict repo rules; a given run may pin a different model + thinking via a [Brain Recipe](#brain-recipe), still bound by those repo rules.

## Knowledge System

Former name of [Mycel](#mycel) — renamed to avoid colliding with the (unrelated) Obsidian vault of the same name.

## Ladder

A named, first-class entity: an **ordered list of exactly three [Brain Recipes](#brain-recipe)**, cheapest (rung 1) to most capable (rung 3). The rungs may draw on **different [IPs](#intelligence-provider-ip)** (mixed providers), and the order *is* the escalation path — re-verification and other [Drift Candidate](#drift-candidate) work climb rung 1 → 2 → 3, stepping up only when a cheaper rung isn't confident enough.

A Ladder is assigned to **0+ [Repos](#repo)**, and a Repo may have several Ladders ranked by **priority** (managed on the Ladders Settings page). It is **usable on a Repo only if all three** of its Brain Recipes are permitted there — checked against each recipe's IP repo rules, **upfront**, so a climb never dead-ends mid-ladder. For a Repo, selection takes the **highest-priority Ladder whose three recipes all clear**. If **no** Ladder clears (none assigned, or every one has a prohibited rung), Arbol does **not** proceed silently: it raises an explicit **error**, notifies the user, and halts the work until the configuration is fixed. *(Planned.)*

**Example:** Repo `Arbol` has two Ladders by priority; the first includes an IP that `Arbol` prohibits, so it's skipped; the second clears all three rungs and is used. A Repo with no clearing Ladder stops with a visible error — never a silent [Drift](#drift).

## Leather Bag

The carbon-based decision unit at the keyboard — the person driving Arbol. **The canonical operational term**: outside the [Nex](#nex) partnership vocabulary, the h-word is banned in this project's code, docs, and artifacts; write *Leather Bag* (noun), *leather bags* (plural), or *leather-bag-* in compounds (*leather-bag-readable*, *Leather-Bag-initiated*). One of the two broad classes of [Initiator](#initiator) — **Leather Bag or agent**. Questions no amount of grep can answer — priorities, ownership, taste, regulatory intent — get addressed to Leather Bags.

[H-Nex](#h-nex) names the person as a participant in an ongoing Nex partnership. H-Nex, its expansion *human nex*, and the human–AI wording used to define that partnership are explicit exceptions to the terminology restriction above.

**Example:** A research doc ends with "Open questions to leather bags: runtime toggle states, data prevalence, and who owns the Snowflake view" — all things only a Leather Bag can answer.

## Living Topic

An [Entity](#entity) (kind `living_topic`, tag `liv`, shape `note`): a durable, evolving context hub for a subject whose continuity spans multiple independent events or periods of work. A Living Topic relates [Chat Sessions](#chat-session), [Artifacts](#artifact), tickets, [Sagas](#saga), [Arcs](#arc), [Beats](#beat), messages, requirements, and any other Entities that concern the same subject over time. These are [Entity Edges](#entity-edge), not ownership or filesystem containment: one Entity may be linked to several Living Topics, and deleting a Living Topic deletes only the topic and its links.

A Living Topic is not bounded work, a schedule, or a current-attention designation. A [Saga](#saga), [Arc](#arc), or [Beat](#beat) represents work that can be completed or abandoned; a [Spotlight](#spotlight) identifies what the Leather Bag currently wants kept in focus; a Living Topic preserves continuity even while the concern is quiet and after individual manifestations are resolved. Living Topics are created, edited, deleted, expanded, and linked to Entities on the `Seqoya[Living Topics]` page. **Link Entity** opens standard Entity Search; pressing Enter links the selected Entity to that topic.

**Example:** “Intermittent authentication failures” remains one Living Topic while separate incidents, Slack discussions, Chat Sessions, investigation Artifacts, tickets, and fixes appear over months in different forms.

## Load

The **instantaneous measure of agent work in flight**: how many agents are actively working a scope and how much live [Chat Session](#chat-session) context they hold. **Radar Load** is the total across all projects and sagas on this computer — the machine's agentic load at this moment; a unit's load is the agents it employs. Load is what the capacity question reads against: units that add no Load but hold runnable territory are exactly what could start next. Scoped per unit and machine-wide (see [Radar](#radar)). *(Planned feature.)*

**Example:** Radar Load: four Delegates, ~380k tokens of live context. "Glossary Arc": one Delegate at 60k context — and two Beats whose territories overlap nothing active, ready to start.

## Mac OS Communicado

The first concrete [Communicado Species](#communicado-species). It accepts a `title`, `content`, and [Communicado Descriptor](#communicado-descriptor), has one Presentation—a native macOS notification—and redirects through the Descriptor when the user clicks that notification. It does not have a Willo Station Presentation and is not durable in the Communicados page in its first implementation. The code identifier is `macos`, and renderer callers use `communicado.macos.deliver`.

**Example:** Elma can deliver “Agent finished” with a Descriptor for that Chat Session; clicking the notification activates Elma and opens the session.

## Mandate

An [Entity](#entity) (kind `mandate`, tag `mnd`, shape `note`) representing one durable, bounded **permission to do something**. A Mandate is like an access card, credential, or key: it defines an authorized action and its bounds, but it does not know who carries it, what mission they have, or what caused them to run. In particular, a Mandate has no [Steward](#steward) or [Activation Rule](#activation-rule) reference.

A Steward may hold any number of Mandates. Assigning or revoking that relationship is state of the Steward, and may be static or happen at runtime. Editing a Mandate's permission creates a new immutable version; provenance of an exercised permission records the acting Steward and exact Mandate version separately. Initial permissions include reading the Steward's Chat Session history, creating Chat Sessions, posting in existing Chat Sessions, using named [Brain Recipes](#brain-recipe), and calling named [Blueprints](#blueprint).

**Example:** “May post in release Chat Sessions” is a Mandate. It can exist before any Steward holds it and contains no schedule or activation condition; a Release Steward must hold the Mandate before posting.

## Mycel

The knowledge engine *(formerly the "Knowledge System"; named for **mycelium**, the underground network through which real trees share nutrients and signals — what this system is to Arbol's tree-named apps)*. Mycel turns each [Repo](#repo)'s [Corpora](#corpus) into a *maintained, trustworthy, queryable* knowledge graph. Its source and build live in the independent `~/repo/sylvan-stack/mycel` repository; it publishes the standalone `mycel` and `better-grep` commands to `~/bin`. Mycel is a **pure library + per-task CLI — NO daemon of its own**. It owns the `kn_`-prefixed Postgres tables and `~/.mycel/config.toml` (repositories, database, embedding, and mirror settings); Brain Recipes belong to the independent Infer tool in `~/.infer/config.toml`. Mycel never imports or invokes Arbol code or instructions, although it may read Arbol databases, logs, source, and artifacts as data. Arbol is one consumer: its own **[Taproot](#taproot)** daemon (`daemons/taproot/`, `taproot.sock`) bundles Mycel's public library in the allowed direction to add a Corpus Watcher, sync loop, and UI-facing RPCs. Mycel invokes the independent `infer` executable when [RAPTOR](#raptor-tree) needs completions and has no Arbol Root fallback. See the [external tool architecture](../arbol_deprecated_v1/architecture/external-tools.md) for the repository and contract boundaries. Its capabilities span the full lifecycle of a [Chunk](#chunk):

- **[Ingest](#ingest)** — files → [Chunks](#chunk) → stable identity → hashes *(built)*
- **[Derivation](#derivation)** — record where each chunk came from *(built)*
- **[Detection](#detection)** — mark [Stale](#stale) chunks, raise [Drifts](#drift) *(built; [Drift Candidate](#drift-candidate) scoring designed)*
- **Sync** — keep it all current automatically: [Corpus Watcher](#corpus-watcher) → [Sync Pass](#sync-pass) *(built)*
- **[Retrieval](#retrieval)** — semantic search, hybrid code search, the agent tool *(built)*
- **[Generation](#generation)** — produce/regenerate derived chunks *(built for [Summary Nodes](#summary-node); doc-from-code planned)*
- **Classification** — assign chunk roles (`authored` / `derived`) *(planned)*
- **[Attestation](#attestation)** — verify content, record who/how/version *(planned)*

The mechanical capabilities run themselves; everything that spends model calls (Generation) waits for a person.

**Strict rule: Mycel is PROHIBITED from running as a daemon — its only sanctioned forms are the per-task `mycel` CLI and its public library.** No resident process, socket server, launchd entry, or serve mode may ship from `~/repo/sylvan-stack/mycel`. Anything that must stay resident — the `taproot.sock` RPC server, [Corpus Watcher](#corpus-watcher), sync loop, and UI-facing `knowledge.*` RPCs — is **Arbol's**, lives in the Arbol-owned **[Taproot](#taproot)** (`daemons/taproot/`, label `com.arbol.taproot`, binary `arbol-taproot`), and dies with Arbol without taking a Mycel capability with it. The enforcement test is severance: with every `com.arbol.*` process stopped, ingest, embedding, retrieval, overlays, and the activity feed still work through `~/bin/mycel`. Freshness without residency comes from **fresh-on-read** (`mycel search` mtime-scans and auto-syncs the delta) plus optional git/session hooks — never from a Mycel process that outlives its task.

**Example:** "Mycel flagged 2 stale summaries" — a doc edit synced automatically, [Detection](#detection) marked the [Summary Nodes](#summary-node) derived from it, and the badge waits for the user to trigger [Stale Summary Regeneration](#stale-summary-regeneration).

## Mycel-enabled

The per-[Repo](#repo) **opt-in gate** for [Mycel](#mycel): only enabled repos are watched by the [Corpus Watcher](#corpus-watcher), [ingested](#ingest), and embedded — and only they appear in the Repo Picker. Off by default; doubles as the safety interlock for company code, since enabling a repo is what authorizes its [Embedder Profile](#embedder-profile) to run. Toggled via `repos.set_mycel`.

**Example:** Arbol is enabled; other repos sit disabled until the flag is deliberately flipped — nothing about them is scanned, chunked, or embedded meanwhile.


## Mycel-integrated

The completion state meant by **“according to Mycel”** for newly authored or changed knowledge: every relevant [Artifact](#artifact), implementation symbol, and behavioral test is covered by an enabled [Corpus](#corpus), [ingested](#ingest) as stable [Chunks](#chunk), connected by the real authority or [Coupling](#coupling) edges its claims require, checked by [Detection](#detection), embedded, and verified through retrieval and reverse context. Passing tests or merely using Mycel to research the change is not sufficient. The governing operation is [`operations/authored-work-integration.md`](../mycel/operations/authored-work-integration.md).

**Example:** A Turn submission contract section, the `TurnSubmissionAcceptor.accept` implementation, and its exact-retry/rollback tests are Mycel-integrated only after all are ingested and the implementation and test chunks derive from the contract sections they enforce.

## Mycel Operation

A reusable, **tool-agnostic process** described as portable instructions in `~/Artifacts/mycel/operations/`. The category emerged from decoupling process knowledge from [Arbol](#arbol): capabilities that had depended on Arbol were extracted into Mycel artifacts so an agent in another host—especially Claude Code—can follow the same process. The most common adapter is a thin Claude Code Skill that routes the agent to the corresponding Mycel Operation, but a Blueprint, Chain, UI, CLI, RPC, Arbol Chat Session, or human may invoke the same process.

A Mycel Operation defines **what should happen and why** independently of the tool used to carry it out. A [Runbook](#runbook), by contrast, is a technical manual for **how to use a particular Tool**: commands, parameters, outputs, exit codes, and tool-specific failures. A Tool may implement all or part of a Mycel Operation; the operation remains the general process authority and links to the Runbook only where concrete invocation help is needed.

“Mycel Operation” is architectural and catalog vocabulary, not terminology to burden the executing agent with. Artifacts in `operations/` use ordinary task-facing titles and prose—such as “Guide,” “Process,” or the activity's direct name—and must not title or describe themselves as “Operation: …”. The folder and catalog preserve the category; the instructions themselves stay portable and immediately useful.

**Example:** `operations/worktree-lifecycle.md` describes the general branch-context process. A Claude Code Skill can route an agent to that guide, while the `mycel` Runbook explains the exact `mycel wt add` syntax; neither the process nor its meaning depends on that command being the invocation surface.

## Mycel Skill

A provider-agnostic, named **activation and dispatch contract** for a task shape. Native Codex CLI and Claude Code CLI expose the same capability through thin adapters that route through the [Instructions Hub](#instructions-hub). The portable process lives in Mycel, not in the adapters.

Creating or changing a Mycel Skill means supporting **both native Codex CLI and Claude Code CLI**. Universe is deprecated. The canonical shared adapter lives at `~/Artifacts/mycel/skills/<name>/SKILL.md`, linked into `~/.agents/skills/<name>` for Codex and `~/.claude/skills/<name>` for Claude. Provider-specific metadata may require a separate thin adapter, but never a copied process. Follow the [creation guide](../mycel/operations/create-skill.md) for layout, invocation policy, and validation.

**Example:** `code-research` is one Mycel Skill, invoked as `$code-research` in Codex or `/code-research` in Claude. Both discover the same activation contract and route through the Hub to `operations/code-research.md`.

## Nex

An individual participant in a continuing human–AI partnership, developing shared understanding and contributing to shared work. **Nex** is the shared identity for both [H-Nex](#h-nex) (human nex) and [A-Nex](#a-nex) (agent nex). The relationship is reciprocal: either participant can teach, learn, propose, question, initiate, or delegate according to the situation. Knowledge, expertise, initiative, and responsibilities can differ and change over time; neither participant has a permanently superior position by definition.

A Nex names the participant, not the pair, a conversation, or a project. The participant's identity can continue across projects and relationships. Partnership does not require identical capabilities, permissions, or responsibilities; autonomy and authority depend on the particular arrangement.

**Usage:** Use **Nex**, **H-Nex**, and **A-Nex** in glossary entries, diagrams, and interfaces; ordinary prose may use *nex* when the distinction is clear. Plurals are *nexes*, *H-Nexes*, and *A-Nexes*.

**Example:** The H-Nex explains a project's history to an A-Nex, the A-Nex contributes implementation expertise, and they work through the resulting design together. Each is the other's nex.

## Nex Colab

An exchange in which an [H-Nex](#h-nex) asks to learn something and an [A-Nex](#a-nex) answers at the depth the H-Nex's [Nex Knowledge Map](#nex-knowledge-map) says is missing. The A-Nex explains only what the map shows as not yet known and says in one line what it skipped; when there is more than one way to go deeper, it offers them as numbered options and the H-Nex picks by number; it logs every learning attempt, and raises a level in the map when the H-Nex's questions show understanding. Started with the skill `/colab "prompt"`, about a question in general or about something in the current [Chat Session](#chat-session). The map is specified in CLB-0 and the exchange in CLB-1, in `~/Artifacts/colab/specs/`.

**Example:** The H-Nex asks why a lock taken inside a transaction is gone at commit. The map shows transactions as *practical* and advisory locks as *ignorant*, so the A-Nex explains advisory locks only, pitched for someone who uses transactions every day, logs the attempt, and offers two ways deeper as options 1 and 2.

## Nex Knowledge Map

A revisable estimate of what an [H-Nex](#h-nex) knows, kept as files in the private corpus `~/Artifacts/colab/`: a tree of nested topics, each with one of five levels, *ignorant*, *superficial*, *practical*, *advanced* and *design*, with free links between related topics anywhere in the tree, and in each topic the list of its children with their levels, because a level says nothing about the children. It describes general knowledge, as a software developer first and in any other field the H-Nex adds, and never knowledge of a repository, a project or a product. An [A-Nex](#a-nex) writes it in [Nex Colab](#nex-colab) exchanges, with its evidence in a learning log; the H-Nex writes it through showup, `/colab showup "prompt"`, and may mark a topic *not interested*, which takes it and everything under it out of the map's summaries and out of any agent's teaching. Specified in CLB-0, `~/Artifacts/colab/specs/00-the-nex-knowledge-map.md`.

**Example:** Under `software-development/swift/concurrency/` the topic is *practical*, its child `actors/` is *ignorant*, and it links to `software-development/python/asyncio` as related.

## Normalizer

A pure, versioned conversion [Entity](#entity) that turns external-provider data already stored in a raw mirror into the stable user-facing representation Arbol consumes. A Normalizer never fetches, reads credentials, mutates raw data, writes a projection, or reads the clock; the caller durably mirrors first, invokes the Normalizer, writes the derived output, then records a hash-linked normalization manifest. A Normalizer may produce derived Markdown [Artifacts](#artifact); the Slack Normalizer produces Willo Slack Surface write models. The common contract and provider conversion rules live in [`architecture/normalizers/`](../arbol_deprecated_v1/architecture/normalizers/README.md).

**Example:** A Normalizer deterministically converts a raw API envelope held in the mirror into its derived output; the sibling manifest records the Normalizer/output-schema versions and the SHA-256 of the raw file.

## Native Tool Call

A tool the [Driver](#driver)'s CLI runs itself (`Bash, Read, Write, Edit, Glob, Grep`) instead of emitting an Arbol fence. The CLI executes; Arbol decides and audits. Permission asks ride the CLI's stdio bridge to [Arbol Root](#arbol-root), which routes each through the [Effector](#effector) classifier (a *decide-only* batch — same approve/deny/click pipeline, no execution) and answers the CLI. Two audit tracks linked by `tool_use_id`: the decision track (the [Tool Request](#tool-request) family with `origin: native`, only when the bridge is consulted) and the observational execution track (`IP_INVOKED_NATIVE_TOOL` / `IP_SETTLED_NATIVE_TOOL`, every execution). The legacy fence path survives as fallback for policy-denied commands and capabilities the tools don't cover. Per-IP, [Seqoya Lab](#seqoya-lab)-gated (`ip_settings.native_tools`); off keeps the fence-only path byte-identical.

**Example:** Claude Code may directly call its `Read` tool for `README.md`; Arbol records that native tool execution and, when needed, routes permission decisions through Effector.

## Now Line

The glowing accent rule at the current time on the [Oaken](#oaken) time axis. The anchor everything measures against: spent vs remaining, overdue, live-span growth, countdowns.

**Example:** In Oaken, a live task bar grows until it touches the Now Line; if the task's deadline sits below the Now Line, the task is overdue.

## Oaken

The task-management and delivery workspace [UI](#ui). See also: [Saga](#saga), [Radar](#radar), [Now Line](#now-line).

**Example:** A delivery lead uses Oaken to follow Sagas for product workstreams and how much of each is done.


## Objectives

The **verifiable completion conditions of a ticket or task** — not a restatement of its requirements, but the checklist consulted **when the work is done** to decide whether the objectives are met. Written *before* the work starts, checked *after* — they define "done" before "doing". The ticket-level analog of a [Blueprint](#blueprint)'s `done_when`: same shape, one level up. Objectives drive downstream judgment — context gathering includes only objective-relevant material, deep research angles derive from them, and a future Close-Ticket chain verifies them as its gate.

**Example:** a ticket "check if redlock is released in activity.interceptor" yields objectives like "the lock's release path under every interceptor exit (success, error, timeout) is IDENTIFIED with file:line evidence, and a verdict released/leaked is stated per path" — checkable at the end, not a paraphrase of the title.

## Organization

A named set of [Repos](#repo) belonging to one organizational unit. An Organization has a common filesystem folder containing its repositories. Its name also serves as its alias, matched case-insensitively, for work spanning multiple member Repos or work whose specific Repo has not yet been identified; separate configured aliases are ignored. Each member keeps its own Repo identity and policy. Organizations can be managed in Seqoya's Organizations page; names, folders, and GitHub URLs are stored in Mycel configuration, while VIP/ignored repository preferences and original/fork metadata are stored by Arbol.

**Example:** [Euro-Office](https://github.com/Euro-Office) is the Organization rooted at `~/repo/Euro-Office/`. Its name, `Euro-Office` (also accepted as `euro-office`), refers to all member Repos when a request spans repositories or only identifies the Organization. A request naming a specific member Repo uses that Repo's scope instead. New organizations default to `~/repos/<organization-name>/` and can be assigned another folder.

## Origin

The [Chunk](#chunk) at the source end of an [Origin Link](#origin-link): what ordered the chunk at the other end. An Origin is of any kind: a [Requirement](#requirement), a [Decision](#decision), a document section, or a code chunk when nothing better exists, as in an undocumented open-source repository. The word is used for nothing else in [Mycel](#mycel); the former `Origin` column of the requirement tables, which said whether a requirement was kept, changed, new or dropped from version 1, is named `From v1`. An Origin is written as an [Entity URI](#entity-uri) when it has a UUID and as a Mycel source address otherwise.

**Example:** The requirement `MYC-2.13` is the Origin of the function that marks a chunk stale; the Origin Link from that function names the requirement by its Entity URI.

## Origin Coverage

What the command `mycel origins` reports: which [Chunks](#chunk) of a repository have an [Origin Link](#origin-link) and which have none, and which [Requirements](#requirement) and [Decisions](#decision) nothing rests on. It is a report for the agent or person who asks, on demand; no gate, hook or release step depends on it.

**Example:** `mycel origins --changes`, run in Beaver Workspace after changing `src/mycel/_derive.py`, lists `DeriveStore.apply` as a chunk without Origin.

## Origin Link

A directed link from a [Chunk](#chunk) to its [Origin](#origin): a claim that this chunk exists because of that requirement, decision, section or code chunk, and never a proof. Its fields are the `method` by which it was made (`stated` by a person, `proven` by a check, `inferred` by a model, `recovered` from history), a `confidence_score` from 0 to 1, the `confidence` band the score falls in (`asserted` above 0.9, `proven` 0.8 to 0.9, `inferred` 0.5 to 0.8, `candidate` below 0.5; the thresholds are example values set in one place), who made it and when, and its `review`. A chunk has a list of Origin Links; the score rises by a review or a passing check and falls by a failed conformance check. Origin Links live in the [Index Store](#index-store), never in the code; they are stated with `mycel justify`, listed with `mycel origins`, inferred with `mycel recovery` and disputed with `mycel audit`. Contrast [Derivation](#derivation), which records authority and conformance, and [Reference](#reference), a locator.

**Example:** `mycel justify 'mycel:@code/src/mycel/_derive.py#DeriveStore.apply' '[req:9b6984cc-…:…]'` records an Origin Link with `method: stated` from that method to the requirement.

## Parse Result

An immutable, durable, typed result of running one versioned [Parser](#parser) against one content hash of an [Email Source Item](#email-source-item). It records `matched`, `not_matched`, `partial`, or `failed`, extracted data, parser/output/pipeline versions, stage provenance, diagnostics, and a private result Artifact. Results are reusable by multiple Signal Rules and cache by source content plus Parser versions.

**Example:** A code-host Parser produces a partial Parse Result from a Gmail preview containing `kind: pipeline.failed`, project, branch, commit, and detection evidence.

## Parser

A named, code-owned, versioned extractor that turns one [Email Source Item](#email-source-item) into typed semantic data. A Parser may use deterministic stages and explicitly requested Completion-backed classification stages, but it does not express user policy and does not directly decide which Signal to emit.

**Example:** A provider Parser such as `email.<provider>@1` recognizes that provider's notification structure and extracts MR, pipeline, project, branch, participant, comment, and provider-instance fields.

## Parser Pipeline

The ordered or dispatching composition of [Parser](#parser) stages used to produce a [Parse Result](#parse-result). Pipelines are code-owned in V1; users configure Signal Rules rather than executable parser code.

**Example:** Provider detection routes an MR-comment email to deterministic extraction, followed only when a Rule requires it by an urgency classifier.

## Provider

The inference vendor / model family: `claude`, `codex`, `cursor`, `zai` (and `mock`, test-only). The grouping key; there is exactly one [Driver](#driver) per Provider.

Two distinct layers carry a provider value, and they deliberately differ for gateway-backed accounts:

- **Transport provider** (the [Intelligence Provider](#intelligence-provider-ip) / [Driver](#driver) level): which CLI/API protocol the bytes speak. The `glm` IP's transport is `claude` — the claude CLI pointed at z.ai's Anthropic-compatible endpoint.
- **Vendor family** (the [Subscription](#subscription) level): who you actually pay and whose usage/models/branding apply. The glm subscription's family is `zai` (Z.AI), never Anthropic — even though its transport is the claude CLI.

**Example:** `claude` is the transport provider for both `bro-claude` and `safe-claude`; `codex` is a different provider with its own driver. The `glm` IP rides the `claude` transport while its bound subscription belongs to the `zai` family — so its model picker offers GLM models and its usage comes from z.ai's quota API, never claude.ai or api.anthropic.com.

## Radar

The live overview of all saga work: every [Saga](#saga), [Arc](#arc), and [Beat](#beat), its state and progress, and which agent holds each active unit. The Radar is a living picture, not a registry — units appear when they start, advance as they progress, and clear when they finish — so it answers the two standing questions directly: what could run right now (the units whose declared territories overlap no active territory), and which part of the project each running agent is in. *(Planned feature.)*

The Radar watches work, not processes: monitoring Arbol processes themselves remains [Willo Station](#willo-station)'s job. Typically rendered as an [Oaken](#oaken) view.

The Radar is also the gathering point for work statistics (under design): the [Workload](#workload) family — [Burn](#burn) (accumulated token consumption), [Load](#load) (agents working now and their live context), [Velocity](#velocity) (token generation rate) — together with summaries of the work done, estimated progress, and spend and usage rollups per [Subscription](#subscription), [Brain Recipe](#brain-recipe), and [Stint](#stint). Radar metrics scope symmetrically: per unit — "**Research Saga Burn**" — and machine-wide — **Radar Burn**, **Radar Load**, **Radar Velocity** — all projects and sagas on this computer.

**Example:** The Radar shows the "Semantic Research Saga" with its "Glossary Arc" three Beats along, the "Trunk Implementation Beat" held by a [Delegate](#delegate), and the "Implementing Specs Saga" greyed out as queued — its territory overlaps the active "Writing Specs Saga". The corner reads "Radar Load: 4 Delegates · ~380k tokens live" and "Radar Velocity: 520 tok/s".

## RAPTOR Rebuild

Clear-and-rebuild of the whole [RAPTOR Tree](#raptor-tree): delete all [Summary Nodes](#summary-node), re-cluster the corpus embeddings **globally**, and run [RAPTOR Summarization](#raptor-summarization) tier by tier. Needed when cluster *membership* should change — above all when new [Chunks](#chunk) have joined the corpus (clustering is global, so newcomers can't be slotted into an existing tree). Guarded by a plan/approve gate: clicking Rebuild first shows the predicted shape (chunks in, summaries out, per tier); [Generation](#generation) starts only on "Approve & Run". Contrast [Stale Summary Regeneration](#stale-summary-regeneration), which keeps the tree's structure.

**Example:** After ingesting a new [Artifact Chapter](#artifact-chapter), the plan predicts `1,431 chunks → ~36 summaries across 2 tiers`; approving rebuilds the tree with the new material clustered in.

## RAPTOR Summarization

[Mycel](#mycel)'s built instance of [Generation](#generation): producing one [Summary Node](#summary-node) per cluster of related [Chunks](#chunk). Each cluster's member texts are sent through a [Completion](#completion) using the configured summariser [Brain Recipe](#brain-recipe); the returned summary is stored as a derived Chunk with **generation edges** to every member (each edge pinning the member's hash — what lets [Detection](#detection) notice when a summary goes [Stale](#stale)). Summaries within a tier run concurrently. The clustering itself (soft GMM over [Embeddings](#embedding), BIC-chosen cluster count, capped so upper tiers converge) is mechanical; only the summarising spends model calls.

**Example:** A cluster of 42 auth-related chunks becomes one retrievable paragraph summarising how authentication works — findable by a query too broad for any single leaf chunk to answer.

## RAPTOR Tree

The hierarchical summary layer over a [Corpus](#corpus): tier 0 is the corpus [Chunks](#chunk) themselves (leaves); tier 1 groups them into clusters and gives each a [Summary Node](#summary-node) via [RAPTOR Summarization](#raptor-summarization); tier 2 clusters *those* summaries; and so on until few enough nodes remain. [Retrieval](#retrieval) searches the **collapsed** tree — leaves and summaries together — so a broad question can land on a tier-1 theme summary while a specific one lands on a leaf. Built for the [Artifact Corpus](#artifact-corpus); a structure-aware variant for code (along the real file/module tree rather than embedding clusters) is a considered future step.

**Example:** Arbol's current tree: 1,281 leaves → 33 tier-1 summaries → 1 tier-2 root — "what does the effector subsystem do" hits a tier-1 summary; "where is `hash_at_gen` set" hits a leaf.

## Reference

A **locator**: a pointer to a target — a file path, [Artifact](#artifact)-section anchor, code-symbol path, http link, or ticket link (a "see also" is one too). Its only integrity question is **does it still resolve**: a Reference breaks when its target is **renamed, moved, or removed**, *not* when the target's content changes (a linked ticket can be rewritten and the link stays valid). It's checked by **resolution** — a cheap lookup ("does this path / anchor / ticket still exist?"), needing no model and no [trust score](#attestation); a broken Reference is just a "fix the pointer" item. Distinct from an [Entity Edge](#entity-edge) (a structural tie in the entity graph) and — crucially — from **using a term's meaning**, which is *not* a Reference but a meaning-dependency ([Derivation](#derivation) / [Coupling](#coupling)) checked by re-verification instead.

**Example:** `[see auth](auth.md#tokens)`, a ticket link, and a path like `core/session.py` are References — they survive content edits to their targets and break only on rename / move / remove. A sentence that *relies on what "Errand" means* is, by contrast, a [Derivation](#derivation) — not a Reference.

## Refresh

<!-- mycel:cues
literal: exclude
target-scope: local_section
-->

The [Artifact Corpus](#artifact-corpus) maintenance step: an [Ingest](#ingest) of the Artifact Corpus, then a re-hash of every [Tracked Source](#tracked-source), then [Detection](#detection). Mechanical and detection-only: no model calls, no [Generation](#generation), nothing regenerated.

Relation to its siblings: a Refresh is the Artifact-Corpus step *inside* a [Sync Pass](#sync-pass) (which additionally ingests the [Code Corpus](#code-corpus) and embeds the delta); the "Refresh" button in [Seqoya Lab](#seqoya-lab)'s Refresher runs just this step on demand.

**Example:** After editing `GLOSSARY.md` by hand, a Refresh re-chunks it, clears the edited chunks' [Embeddings](#embedding), and [Detection](#detection) marks the [Summary Node](#summary-node) derived from them [Stale](#stale) — the badge updates; regeneration waits for a person.

## Release

To **release Beaver Workspace** means ending the agent's hold or booking of
**Beaver Workspace**. **Unhold** and **unbook** are synonyms; **release** is
the standard operation name. The existing rules for
[returning the booked area](../mycel/operations/sagas.md#stopping-and-finishing)
still apply.

## Repo

A git repository, identified by a short **code name**—not by a path, checkout, branch, or origin URL. It is the stable identity to which the work graph and policy bind: a [Branch](#branch) and every [Worktree](#worktree) belong to a Repo, while [Intelligence Providers](#intelligence-provider-ip) carry default/prohibited rules per Repo ([Seqoya Lab](#seqoya-lab)-configured). A Repo may belong to an [Organization](#organization). A Repo's configured filesystem location is its standard Git checkout folder. Known code names: `Arbol`, `Slack Bridge`, `BroPulse`, `hyperkey`, `AppRecorder`.

**Example:** The `Arbol` Repo lives directly at `~/repo/sylvan-stack/Arbol`, with source files and `.git` in that folder.

## Repo Folder

The standard Git checkout associated with a [Repo](#repo), containing its source files and `.git` directly. A [Chat Session](#chat-session) uses this folder as its [Working Directory](#working-directory). Nested `main/`, `master/`, and branch worktree folders are deprecated.

## Repo Picker

The UIShell-header dropdown selecting which [Repo](#repo) an app's [Mycel](#mycel) views are scoped to. Lists only [Mycel-enabled](#mycel-enabled) repos. Empty on an app's first run — pages that need a repo ([Seqoya Lab](#seqoya-lab)'s Chunks Viewer, Refresher, Artifacts, Retrieval) stay disabled until one is chosen — after which the selection is persisted **per UI** (each app remembers its own). A lens, not a power switch: [Sync Passes](#sync-pass) keep *all* enabled repos fresh regardless of what any picker shows.

**Example:** Seqoya's picker on "Arbol" scopes every Mycel page to the Arbol corpora; switching to another enabled repo re-scopes the same pages instantly — neither repo's data is touched.

## Requirement

One thing a product must do, recorded as one row of a specification's Requirements table: its human id such as `MYC-2.13`, the text beginning "Mycel must…", whether it is kept, changed or new from version 1 (`From v1`) and the kind of check that verifies it. A Requirement is an [Entity](#entity) (kind `requirement`, tag `req`, shape `note`), keyed by a UUID that stands in the row's first cell in an HTML comment after the human id, invisible to readers and read by [Mycel](#mycel), and addressed by an [Entity URI](#entity-uri) `[req:<uuid>:<title>]`. Mycel keeps it as a [Chunk](#chunk) of its own beside the section that holds the row, so that code and documents can name it as their [Origin](#origin) through an [Origin Link](#origin-link), and so that editing the row marks what rests on it [Stale](#stale) as a [Derivation](#derivation) does. The human id is its display name and is never edited; the row can move between chapters without changing identity, and a withdrawn id stays reserved. Contrast [Decision](#decision), a choice the owner made.

**Example:** `| MYC-2.13 <!-- 9b6984cc-db34-4a84-b948-0eaefbea916a --> | mark a chunk stale when a source of it has a content hash other than the one its edge stores … | Changed | store |` is one Requirement; its Entity URI is `[req:9b6984cc-db34-4a84-b948-0eaefbea916a:<title>]`.

## Research Trip

An [Arbol-Initiated Chat Session](#arbol-initiated-chat-session) dispatched to research a question and **return only the findings**, so the dispatcher's context window isn't polluted by the raw exploration. Run by a [Delegate](#delegate), typically dispatched by the agent in another Chat Session. Go out, look around, come back with a report — the conversational counterpart to an [Errand](#errand) (which does work rather than gathering it).

**Example:** Before editing, the agent in a Chat Session sends a Research Trip to map how Chat Sessions are persisted; it returns a three-paragraph summary instead of fifty files of context.

## Retrieval

[Mycel](#mycel)'s capability for **querying** the [Corpora](#corpus) — finding the right [Chunks](#chunk) to answer a question or feed an agent's context — as opposed to maintaining them ([Sync Pass](#sync-pass)) or producing them ([Generation](#generation)). Built: semantic search over the [Artifact Corpus](#artifact-corpus) (collapsed [RAPTOR Tree](#raptor-tree) — leaves and summaries together) and **hybrid code search** over the [Code Corpus](#code-corpus) (meaning via [Embeddings](#embedding) + exact identifiers via BM25, rank-fused), exposed to agents as `mycel search --only code`.

**Example:** A [Research Trip](#research-trip) uses Retrieval to pull only the chunks relevant to "how are turns persisted" instead of reading whole files.

## Root Contract

The contract that an [Arbol Root](#arbol-root) shares with all its [Arbol Trunks](#arbol-trunk): the command `arbol-trunk`, the folder of each [Chat Exchange](#chat-exchange) while it runs, the chat tables of the Root's database, and a conformance suite that every Trunk Build passes. Only the Root Contract has version numbers: a Root uses one version, named as `rootContract` in its record, and each Trunk Build lists the versions it implements as `rootContracts`. A Trunk Build fits a Root when its list holds the Root's version, and Roots of the same version share every Trunk Build that fits. It replaces the name Trunk Contract. See [the Root Contract](../arbol-root/contract/README.md).

**Example:** First Sapling and a second Root made from it both use version 1, so Build 4 of the [Trivial Trunk](#trivial-trunk), with `"rootContracts": [1, 2]`, runs in both without being built again.

## Routine

Recurring or triggered work performed by a [Steward](#steward), commonly maintenance such as re-ingesting a corpus, sweeping stale chunks, or garbage-collecting. Each run that requires agent work is an [Arbol-Initiated Chat Session](#arbol-initiated-chat-session) whose [Initiator](#initiator) is the Steward. A schedule or event supplies an activation opportunity and the Steward's activation policy decides whether to act; neither the trigger nor Mandate condition is the Initiator. The Steward's authority is recorded through the exact [Mandate](#mandate) version used. Distinct from an [Errand](#errand), which is one-off delegated work.

**Example:** A nightly Routine re-ingests `~/Artifacts/Arbol/` and records work items for any chunk whose source moved since it was last generated.

## Runbook

A **technical manual for a tool**, kept **near its file** (the runbook-near-file rule): CLI tools whose code lives in repos get theirs in a `tools/` [Artifact Chapter](#artifact-chapter) — `~/Artifacts/mycel/tools/` for the client-agnostic Tools (mycel, infer, blueprint, better-grep), `~/Artifacts/Arbol/tools/` for Arbol-only ones (arbol-cli, deployment); a [Blueprint Chain's](#blueprint-chain) runbook sits NEXT to its script in `~/Artifacts/mycel/chains/` as a same-name sibling `.md`. Contents: syntax, parameters, inputs/outputs, data structures, exit codes, and failure modes with cures — carrying [Source Refs](#source-ref) to the implementing scripts/modules (repo-hosted code only; sibling scripts aren't indexed, so proximity is the link). A runbook contains **no process reasoning**: it answers "how do I *say* it", never "what should happen" — that is a [Mycel Operation's](#mycel-operation) job. Runbooks serve every actor that **learns at runtime** — humans and agents alike, whether hosted in Claude Code, codex, or an Arbol [Chat Session](#chat-session) (conversational agents, [Delegates](#delegate), and [Stewards](#steward) operating tools are prime consumers). Only **compiled code** (UI buttons calling RPCs, daemon internals) consults nothing at runtime — it is instead what runbooks *cite*, so [Detection](#detection) flags the manual when the tool changes. The **Arbol Runbook** (`tools/arbol-cli.md`) is the reference for all `arbol-cli` commands. Discovery works both ways: forward via [Retrieval](#retrieval); backward via the refs' reverse edges — [better-grep](#better-grep) shows `documented in: tools/…` the moment an agent touches the tool's code. Freshness by [Detection](#detection); retirement by [Heartwood](#heartwood). The habit: a new command or hard-won failure-mode lesson gets its section in the same breath as the change.

**Example:** `tools/deployment.md`'s failure-mode table (poisoned-package zlib crashes, orphan-core reaping, socket-wait timing) carries refs to `rebuild-and-restart.sh` — edit that script and Detection flags the section for review.

## Saga

An **independent stream of work** that does not interfere with other Sagas: no two concurrently active Sagas make changes in the same code and/or [Artifacts](#artifact). Each unit declares a **territory** — the code, files, and artifacts it may touch — and a territory is **exclusive while active**: declared territories may overlap, but a unit cannot start or keep running while an active unit's territory overlaps its own. Overlap therefore means sequencing, not a violation — phases of one effort queue behind each other — and the parallel-capacity question stays countable at every tier: at any moment, how many units overlap no active territory, and which part of the project each running one owns. *(Planned feature.)*

Sagas nest exactly **two levels deep**: a top-level **Saga** — a high-level direction of work — contains **[Arcs](#arc)**, and an Arc contains **[Beats](#beat)**. All three tiers are one record kind, a Saga at different levels of nesting, and every one of them is an independent stream. The exclusivity rule settles only units outside a containment line — sibling Beats of one Arc, sibling Arcs of one Saga, and unrelated Sagas never run concurrently on overlapping territory, while an ancestor runs through its descendants. Nesting goes no deeper — an Arc cannot contain another Arc, and a Beat contains nothing. How a territory is declared, held and checked is in the [Sagas guide](../mycel/operations/sagas.md).

Not the distributed-systems "saga pattern" (compensating transactions): a Saga names a direction of work, not a transaction scheme. Distinct from an [Errand](#errand) (the delegated session through which an agent works a Beat — the Errand is execution, the Saga is the work) and [Activities](#activity) (trunk-internal execution units below the Saga layer).

**Usage:** A specific unit is always referred to by its proper name followed by its tier word, with the tier word capitalized — "Semantic Research Saga", "Glossary Arc", "Trunk Implementation Beat". Prose, UI labels, and code use the full form for a specific unit (code identifiers end in the tier: `semantic_research_saga`); the bare tier word is reserved for generic statements about a tier ("an Arc cannot contain another Arc") and back-references whose antecedent is unambiguous in the same paragraph. Unqualified **Saga** (plural **Sagas**) may also denote a unit of any tier when the family sense is meant; when the tier matters, name it.

**Example:** The "Semantic Research Saga" contains the "Glossary Arc" and the "Arbol Specs Arc"; the "Glossary Arc" contains the "Trunk Implementation Beat" and the "Workflow Semantics Beat". The two Beats touch disjoint files, so two [Delegates](#delegate) can work them at once. The "Writing Specs Saga" and the "Implementing Specs Saga" declare overlapping territories — both change the spec artifacts — so they never run at the same time: "Implementing Specs Saga" becomes runnable the moment "Writing Specs Saga" finishes.

## Scan

The first step of [Ingest](#ingest): read every file of a [Corpus](#corpus) from disk and compute each file's whole-file content hash. Read-only — no database writes — and it produces the picture of "what exists right now" the rest of Ingest works from. A file whose hash matches the stored one is **skipped entirely** (its chunks are provably identical, since [Chunking](#chunking) is deterministic); this short-circuit is what makes an idle Ingest sub-second.

**Example:** A [Sync Pass](#sync-pass) on an untouched corpus is a Scan and nothing more — ~360 files read and hashed, zero writes, done in well under a second.

## Seqoya Lab

The administration [UI](#ui): [Intelligence Providers](#intelligence-provider-ip), [Subscriptions](#subscription), usage.

**Example:** An admin opens Seqoya Lab to add a Claude subscription, configure `safe-claude`, or inspect usage limits.

## Signal

One immutable business-relevant fact Arbol observed or derived, stored in the append-only durable Signal Journal before live publication. A Signal has a dotted Signal Type, source/source reference, occurrence/send times, schema-validated data, a journal sequence, idempotency identity, and derivation provenance. It is not editable configuration and is semantically separate from an Event Log event.

**Example:** A new matching source emits one `<provider>.pipeline.failed` Signal whose provenance identifies its Signal Rule version and Parse Result.

## Signal Rule

Editable user automation configuration that evaluates typed source/[Parse Result](#parse-result) paths and maps a match into one declared [Signal Type](#signal-type). Each edit creates an immutable version with a future-only Email Source acceptance cutoff; retained email can be used only for a non-emitting Test. Rules can be enabled, disabled, archived, or restored without deleting versions or Signal provenance.

**Example:** A Rule matches `parsed.kind == pipeline.failed` and a provider project, then maps branch and commit into `<provider>.pipeline.failed`.

## Signal Type

A code-owned lower-case dotted name plus a versioned data schema for one family of [Signals](#signal). Signal Rule mappings are validated against it before activation and emissions are validated before journaling.

**Example:** `<provider>.merge_request.comment@1` requires project, merge-request IID, and comment fields.

## Source Ref

An in-file provenance declaration — `repo:path[#symbol]` — that [Ingest](#ingest) materializes into a `declared` [Derivation](#derivation). Only enabled repositories may be named by Source Refs. Citations to disabled or frozen repositories use ordinary Markdown links or historical evidence locators and create no provenance edges. Two homes: per-section refs in an HTML comment (`<!-- sources: … -->`, one ref per line — invisible in rendered markdown, readable in the raw file, attached to the section's own [Chunk](#chunk)), and frontmatter `sources:` for *document-wide governors* (the ticket snapshot, the extract this document answers to — attached to the document's first chunk). Refs use the chunk's **natural key**, never its id: the ULID is the projection's bookkeeping; documents speak the external identity, and ingest translates. Granularity follows the claim: `path#symbol` pins one function (the default for code research), `path#ClassName` watches the class *family* (header + methods), bare `path` the whole file, `file.md#Heading` a section of another artifact. The rule for *what deserves a ref*: an edge follows a **claim, not attention** — cite what a section says something about (including recorded dismissals), never everything that was merely read. The file is the truth: removing a ref removes its edge on the next ingest; a ref that fails to resolve is recorded **loudly** on the chunk (visible in the Chunks Viewer) and retried on later passes — never silently dropped.

**Example:** A Driver specification cites the enabled contract section `arbol:driver-contract/02-inference.md#Behaviour` in its `sources:` comment. When that contract section changes, [Detection](#detection) marks exactly that section [Stale](#stale) — edits elsewhere in the file stay silent. (The complete `<!-- sources: … -->` form is deliberately not spelled out here: ingest reads raw text, so a complete comment would bind this very entry to that contract section — an illustration is not a claim. The earlier example, `arbol_deprecated_v1:daemons/core/arbol_core/artifact_reconciler.py#classify_artifact`, is now an ordinary historical locator.)

## Sparse Retrieval

Search **by exact words** (BM25 / keyword / *lexical* search): a text is represented as a huge checklist with one slot per word in the vocabulary — a count in the slots for the words it actually contains, **zero everywhere else** (hence *sparse*: almost all slots empty). Two texts match only where their checkmarks overlap, weighted so rare words count more (that is BM25's ranking formula). Blind to meaning — "authentication" and "login" live in unrelated slots — but unbeatable for identifiers and exact phrases, which is why [Retrieval](#retrieval)'s hybrid code search pairs it with [Dense Retrieval](#dense-retrieval) and fuses the two rankings.

**Example:** The query `hash_at_gen` instantly tops the chunks containing that literal token — no embedding involved; asking "where is drift pinned to a source version" instead needs the dense arm.

## Spotlight

A durable, Leather-Bag-controlled designation attached to exactly one [Entity](#entity), indicating that the Entity belongs to the Leather Bag's current area of interest. Spotlight answers only **“What do I want Arbol to keep in focus?”** It is not a container, work item, schedule, response request, authority grant, or execution trigger. A [Beat](#beat) is a bounded piece of work; an [Action Item](#action-item) is a Communicado requiring a response.

Spotlight is persisted as current set membership only: a database row means the Entity is Spotlighted; removing it deletes that row. It has no start/end dates, inactive rows, expiration, or retained Spotlight history. A Spotlight may target any Entity Kind, including a Communicado. It is fully orthogonal to Communicado status: Action Items are not Spotlighted automatically, and resolving a Spotlighted Action Item leaves its Spotlight intact.

Willo Station renders the complete durable Spotlight set in a persistent column visible on every full Station page. Slack's 👀 reaction is one input gesture that Spotlights the canonical Slack thread-root Entity; it is removed after Root persists that designation.

**Example:** Spotlighting a Slack thread keeps it visible throughout Willo Station and allows a separate Reaction to recognize future replies in that thread. It does not by itself ask the user to act or authorize an agent.

## Stale

One of the two states of a [Chunk](#chunk)'s up-to-dateness; the other is **fresh**. A chunk is Stale when a source it derives from has moved past the version recorded on the [Derivation](#derivation) edge (`hash_at_gen`) — or when an upstream chunk is itself Stale (staleness propagates). Set and cleared by [Detection](#detection); purely a *flag*, carrying no judgement of severity. The escalation ladder, from mildest to strongest: **Stale** (the flag) → [Drift Candidate](#drift-candidate) (a suspicion worth re-verifying) → [Drift](#drift) (a confirmed work item). Orthogonal to [Unattested](#attestation), which is about whether anyone *verified* the content, not whether its sources moved.

**Example:** Editing two glossary sections makes the [Summary Node](#summary-node) built from them Stale — the "Regenerate stale (1)" badge lights up; the summary's *text* hasn't changed, only its standing.

## Stale Summary Regeneration

The **incremental** path for repairing a [RAPTOR Tree](#raptor-tree): re-run [RAPTOR Summarization](#raptor-summarization) for only the [Summary Nodes](#summary-node) that [Detection](#detection) marked [Stale](#stale) — **in place** (each keeps its id and its cluster membership), tier-ascending so a refreshed tier-1 summary feeds its tier-2 parent. Handles edited and deleted members; what it *cannot* do is admit **new** [Chunks](#chunk) into the tree — membership is fixed, so new material waits for a [RAPTOR Rebuild](#raptor-rebuild). Triggered by the "Regenerate stale (N)" button; a form of [Generation](#generation), so it never runs automatically.

**Example:** An edit to one plan section makes 2 of 34 summaries Stale; regeneration re-summarises exactly those 2 — seconds and pennies instead of rebuilding the whole tree.

## State Runtime Profile

The explicit `state` build/install selection whose dedicated Root, Default Trunk and Provider entrypoints use controller-bound PostgreSQL current-state authority and direct domain transactions. Its package contains no ELS executable; compiled/runtime import guards reject legacy authority, replay, aggregates/projections, snapshots and the separate offline importer. Typed render DTOs, Provider delivery sequences, current-state history, live overlays and dirty hints remain reusable. The default installed production profile remains `legacy` until actual acceptance and separately authorized production conversion. See [architecture](../arbol_deprecated_v1/architecture/state-runtime.md) and [operator contract](../arbol_deprecated_v1/tools/state-runtime.md).

## Steward

A [Delegate](#delegate) activated by an [Activation Rule](#activation-rule) in order to accomplish a mission or task rather than by a direct request in a regular [Chat Session](#chat-session). The Steward persists as an identity between runs even though no agent process needs to remain alive. Its identity owns the mission, default [Brain Recipe](#brain-recipe), runtime metadata, Chat Session history, and the set of [Mandates](#mandate) it currently holds.

Mandates—not activation—allow a Steward to perform actions on the person's behalf that regular conversational agents cannot normally perform, such as reading all of its own Chat Sessions, creating new Chat Sessions, posting to existing ones, selecting other Brain Recipes, or calling permitted [Blueprints](#blueprint). A Steward may have any number of static Mandates; Activation Rules or runtime logic may assign or revoke additional Mandates. Provenance records the Steward as actor, the Signal that prompted its run, and every exact Mandate version exercised.

**Example:** A Release Steward starts when it receives `steward.release.check.requested`. It reads its previous investigations using a history Mandate and, when needed, exercises separate Mandates to post in the release chat or create a new investigation.

## Stint

A named set of stop criteria for one agent **run**: how much work the run is asked to do and how much it may spend. A Stint bounds measures such as elapsed time, tokens spent and findings produced with minimums and maximums, each soft or hard. It says nothing about which brain does the work or how hard it thinks; that is the [Brain Recipe](#brain-recipe). Naming a Stint in a request replaces spelling out the limits, and a limit stated in the request overrides the Stint's limit for that run.

Stints are defined once in the [stints guide](../mycel/operations/stints.md), which also owns how to add or change one. A Stint is agreed with the user before it is written: the agent recommends each limit and gives its basis. A process must say that it honours Stints and what each measure counts; the first to do so is the [deep pull-request review](../mycel/operations/pr-deep-review.md#stop-criteria).

**Example:** “Continue the review, overnight stint” applies every limit stored under the name `overnight`; “overnight stint, but at most one million tokens” changes only the token limit and keeps the rest.

## Subscription

An authenticated account with a provider vendor family (login state + usage/limits). Bound to an [Intelligence Provider](#intelligence-provider-ip); its credential is passed to the [Driver](#driver) per [Turn](#turn). The subscription's `provider` is the **vendor family** — the account's real vendor — which may differ from the bound IP's transport provider (`zai` subscription on a `claude`-transport IP). `auth_mode` is `oauth` (PKCE web flow) or `api_key` (a static key, e.g. z.ai; no refresh token — rotate by re-running `subscription set-token`).

**Example:** Alex’s logged-in Claude account is a subscription; `safe-claude` can be bound to it so turns run using that account’s token. The `glm` subscription is Z.AI’s GLM Coding Plan (family `zai`, auth_mode `api_key`): a static z.ai key whose usage Arbol reads from z.ai’s quota API.

## Summary Node

One node of a [RAPTOR Tree](#raptor-tree): a `derived` [Chunk](#chunk) holding the summary of one cluster, at a given **tier** (1 = summarises corpus leaves; 2 = summarises tier-1 summaries; …). Joined to every member it summarises by a **generation edge** ([Derivation](#derivation)) pinning that member's hash — which is exactly what lets [Detection](#detection) mark the summary [Stale](#stale) when a member changes. A Summary Node is a full citizen: it has an [Embedding](#embedding) (so [Retrieval](#retrieval) finds it), stable identity, and appears in the Chunks Viewer under the RAPTOR toggle.

**Example:** `raptor/L1/01KW…` summarises 42 auth-related chunks; edit one of them and the node goes Stale — regenerate it and its tier-2 parent refreshes next.

## Surface

Any environment or channel through which something interacts with [Arbol](#arbol)—inbound or outbound, and not only a GUI. Surfaces include the four **[UIs](#ui)** (windowed surfaces), the **[CLI](#cli)** (a terminal surface), native macOS Notification Center, and Integrations such as Slack / IMAP / HTTP. A [Communicado Species](#communicado-species) explicitly supports whichever Surfaces it can inhabit and may provide a different [Presentation](#communicado-presentation) for each. *(A [UI](#ui) is one kind of Surface, not a synonym for it.)*

**Example:** A Slack message arriving through the Integrator, a user typing in [Elma Chat](#elma-chat), an `arbol-cli session send`, and a Communicado delivered to macOS Notification Center are interactions on different Surfaces.

## Sync Pass

One run of the routine that **synchronizes [Mycel](#mycel)'s stored graph with the filesystem**: an [Ingest](#ingest) of the [Artifact Corpus](#artifact-corpus) (as a [Refresh](#refresh), i.e. including [Tracked Source](#tracked-source) re-hashing and [Detection](#detection)), an Ingest of the [Code Corpus](#code-corpus), then **embedding the delta** — re-embedding only the pending [Chunks](#chunk). Entirely mechanical: the only model-adjacent cost is the embedding call, and it never performs [Generation](#generation) — a pass may *mark* summaries [Stale](#stale), never regenerate them. Triggered by the [Corpus Watcher](#corpus-watcher) (or on demand via `knowledge.sync`); an idle pass short-circuits at [Scan](#scan) and is read-only.

**Example:** Save three doc edits → thirty seconds after the last save one Sync Pass runs: the edited chunks re-ingest, their vectors re-embed, and the stale badge updates — the graph is current again without anyone clicking anything.

## Taproot

Arbol's resident knowledge daemon — the tree's always-on main root into the [Mycel](#mycel) network (`daemons/taproot/`, binary `arbol-taproot`, label `com.arbol.taproot`, socket `taproot.sock`; formerly the "mycel client"). An Arbol-owned host that bundles Mycel's public library in the allowed direction to keep everything that must stay resident on the Arbol side of the dependency law: the [Corpus Watcher](#corpus-watcher), the debounced [Sync Pass](#sync-pass) loop, embedding and [RAPTOR](#raptor-tree) job supervision, search freshness, and every `knowledge.*`/`overlay.*`/`artifacts.*`/`repos.*` RPC that [Arbol Root](#arbol-root) proxies to it. Exists because Mycel itself is prohibited from running as a daemon; Taproot may die with Arbol without taking any Mycel capability with it (the severance test).

**Example:** Seqoya's Dashboard polls `knowledge.activity` through Root → Taproot, while an agent's `mycel activity` reads the same feed daemon-less — same library, one resident host, one per-task CLI.

## Text Snapshot

An immutable capture of the exact text observed by an [Arbol Trunk](#arbol-trunk) at one moment. A Text Snapshot identifies its source and version: commonly a provisional Draft revision or an authoritative submitted user message. Activities process the snapshot rather than mutable composer state, so outputs can be traced to the precise text that caused them and results from superseded revisions cannot silently affect submission.

**Example:** A draft snapshot containing “Ask the Team Lead” can produce a Cue; after the phrase is deleted, the newer snapshot does not contain that Cue, and only the exact submitted-message snapshot determines final prompt inclusion.

## Theme

One of the 12-step brightness ladder (dark→light), set via `data-theme` on the document root. Default: **redwood**.

**Example:** Switching from a dark redwood theme to a lighter theme changes token values while components keep using the same design tokens.

## Tool

Any **CLI or script that does work** — the reusable units of external logic the intelligence system runs (`mycel`, `infer`, `blueprint`, `better-grep`, `mycel-embedder`, `arbol-cli`, or an ad-hoc script). Distinct from a [Mycel Operation](#mycel-operation) (a *process* — what should happen) and a [Blueprint](#blueprint) (agent *work*): a Tool is a concrete executable with a fixed interface — inputs, outputs, exit codes. Every Tool carries a **[Runbook](#runbook)** (its motivation + how-to), kept near its file: client-agnostic CLIs document in `~/Artifacts/mycel/tools/` (Arbol-only ones in `~/Artifacts/Arbol/tools/`), chains next to their script in `~/Artifacts/mycel/chains/` — with [Source Refs](#source-ref) to repo-hosted implementing code so [Detection](#detection) flags the manual when the tool changes. Tools are the composable substrate [Blueprints](#blueprint) and [Blueprint Chains](#blueprint-chain) lean on: rather than embed bash inline, a step or chain **calls a documented Tool** — external logic stays a named, versioned, runbook'd unit instead of a copy-pasted snippet. A [Blueprint Chain](#blueprint-chain) is itself a Tool (a script composing blueprint runs).

**Example:** a research guide step says "run `mycel search --repo <repo> "<question>"`" — a Tool call with a runbook — rather than open-coding the retrieval query; when the tool changes, Detection flags its runbook, not every guide that uses it.

## Tool Request

A tool invocation the [Intelligence Provider](#intelligence-provider-ip) asks for during a [Turn](#turn), settled by the [Effector](#effector).

**Example:** The agent emits a request to write `app/config.py`; Arbol shows it for approval and Effector settles it as run, run-always, or rejected.

## Tracked Source

A whole-file hash record for a [Derivation](#derivation) source that isn't itself a [Chunk](#chunk) — typically a code file a doc chunk derives from. Tracking stores just enough (path + content hash) for [Detection](#detection) to notice the source changed, without [Chunking](#chunking) it. As the [Code Corpus](#code-corpus) matures, sources that today are merely tracked can become real code Chunks with proper per-symbol edges.

**Example:** A design doc chunk derived from `session.py` before code ingestion existed: the file is a Tracked Source, so editing it still flags the doc chunk [Stale](#stale) — file-level granularity instead of symbol-level.

## Trivial Trunk

The first [Arbol Trunk](#arbol-trunk), code name `trivial`: for each [Chat Exchange](#chat-exchange) it makes one Driver run with the route it is handed, and nothing else. It is the default Trunk of every [Arbol Root](#arbol-root), so a command that names no Trunk gets it, and a Root is marked working only while a working Build of it fits the Root. It carries as little logic as it can, so that Arbol keeps working when every other Trunk fails. It is not the [Default Arbol Trunk](#default-arbol-trunk) of version 1. See [the Trivial Trunk's specifications](../arbol-trunk/trunks/trivial/specs/README.md).

**Example:** `arbol-trunk run "What does build.sh do?"` starts the newest working Build of `trivial` that fits the current Root.

## Trunk Runtime

Historical name for a resident process generation that hosted several [Chat Exchanges](#chat-exchange). It belongs to the version 1 topology and is not carried over into Arbol 2. Current [Arbol Trunks](#arbol-trunk) run one accepted Exchange per process; their numbered Builds may coexist without resident runtime generations or a draining upgrade protocol. See [components and boundaries](architecture/00-components-and-boundaries.md).

**Example:** A version 1 upgrade kept runtime generation A running until its Exchanges drained into final states. Arbol 2 instead starts a chosen compatible Build for each new Exchange, while existing Exchange processes finish independently.

## Turn

One standard agent interaction interval: it begins when an agent is invoked/called and ends when that agent stops responding because it requires another input before it can continue. The required input may be a Tool Request result or decision, new user instructions, or another explicit continuation input.

A complete [Chat Exchange](#chat-exchange) may span several Turns, retries, failovers, and tool interactions. The current implementation's broad `turn_id` often identifies an Exchange-like request/execution scope and requires migration or compatibility naming; code compatibility does not redefine this product term.

**Example:** The agent responds with a Tool Request and waits: that agent invocation is one Turn. After Arbol supplies the tool result and invokes the agent again, the continuation is another Turn.


## UI

A windowed [Surface](#surface): one window in the Arbol family. Each is a separate `.app` sharing one [Arbol Swift App](#arbol-swift-app) binary, with its own renderer bundle baked in. The four UIs:

- **[Elma Chat](#elma-chat)** — conversation: a [Chat Session](#chat-session) as a branching tree of [Turns](#turn).
- **[Seqoya Lab](#seqoya-lab)** — administration: [Intelligence Providers](#intelligence-provider-ip), [Subscriptions](#subscription), usage.
- **[Willo Station](#willo-station)** — station/control: the [Event Log](#event-log) monitor/inspector.
- **[Oaken](#oaken)** — task management and delivery workspace.

**Example:** Elma Chat and Oaken are different UIs: one is for conversation, the other is for delivery planning, but both run inside the Arbol app family.

## UIShell / Chrome

The shared three-row window frame (Header / Viewport / Status Bar) every UI mounts, with `headerLead` / `headerExtras` slots.

**Example:** The same header/status-bar frame wraps Elma Chat, Oaken, Seqoya Lab, and Willo Station, while each surface fills the viewport differently.

## Willo Station

The station/control surface [UI](#ui).

**Example:** Willo Station can act as the control-room view for monitoring or operating Arbol processes.

## Working Directory

The repository folder in which a Chat Session executes commands. It is the first selected repository directory. Existing persisted Arbol/main paths resolve to the standard Arbol folder after migration. Worktree selection is deprecated.

## Velocity

The **rate of token generation**: tokens per second produced by the agents working a unit. A flow — the rate counterpart of [Burn](#burn)'s stock. **Radar Velocity** is the machine-wide total. Scoped per unit and machine-wide (see [Radar](#radar)). *(Planned feature.)*

**Example:** "Writing Specs Saga" runs at ~180 tok/s while its Delegate drafts; the machine totals ~520 tok/s across four Delegates.

## Visit

A **Visit** occurs when an Entity becomes the current or active Entity because the user is fully focused on that Entity in its own dedicated page or view. Visiting updates Arbol’s most-recently-visited Entity context. Merely expanding, previewing, or selecting an Entity within a list of peer Entities is not a Visit. When the current page has no active Entity of its own, features that need Entity context may use the most recently visited Entity.

## Workload

The umbrella for the agent-work measurements the [Radar](#radar) reports: [Burn](#burn) (accumulated token consumption), [Load](#load) (agents working now and their live [Chat Session](#chat-session) context), and [Velocity](#velocity) (token generation rate) — together with summaries of the work done and estimated progress. A unit's workload and the machine's workload are the same measures at different scopes.

**Example:** "How is the workload?" asks after Burn, Load, and Velocity together — on one Saga or across the machine.

<a id="environment"></a>

## Workspace

A reusable working area for parallel agent work, with one clone of every
repository and its development dependencies installed. Always use the full
animal name with the term: **Badger Workspace**, **Beaver Workspace**,
**Fox Workspace**, **Hare Workspace**, **Lynx Workspace**, **Otter Workspace**,
**Owl Workspace**, **Panda Workspace**, **Raven Workspace** and
**Wolf Workspace**, in that booking order. Do not shorten an individual name
to the animal alone or use the term without its name. Generic instructions
can refer to the booked area or the pool.

**Beaver Workspace** is reached at `~/repos/sylvan-stack/beaver/`. The Mycel
repository in **Beaver Workspace** is `~/repos/sylvan-stack/beaver/mycel`;
name the repository separately from the area's full name. A hold reserves
one complete area for a Beat or an Arbol chat, keeping its repositories
together. The owner's own checkouts and `readonly/` are outside the pool.

The owner chose the animal names and this term on 26 October 2026,
replacing the former term *Environment* and the earlier *prepared folder*.
Animal paths remain aliases to the existing physical color folders, which
stay in place for running agents, saved sessions and installed dependencies.
Color and numbered paths still name the same ten areas; existing holds keep
their recorded paths. The legacy `#environment` link remains an alias to
this definition. See [Working in Sagas](../mycel/operations/sagas.md#named-work-areas)
for the name mapping, booking, branches, setup and return.

## Workspace Ledger

The `ledger.jsonl` file that records a history of work items while an agent
works in a named area, such as **Beaver Workspace**. When identifying one
particular ledger, say **Workspace Ledger for Beaver Workspace**.

The file's function and behavior will be described later.

## Worktree

Git's working tree terminology remains valid, but Arbol's managed worktree selection and lifecycle are deprecated as of 2026-09-16. Work directly in the [Repo Folder](#repo-folder); Arbol no longer creates, switches, or deletes linked worktrees.

## Worktree Container

Deprecated as of 2026-09-16. Arbol uses standard [Repo Folders](#repo-folder), not `.bare` stores with nested branch checkouts. Historical references describe the retired layout.
