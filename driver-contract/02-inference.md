---
role: authored
spec: DRV-2
status: accepted
---
# Driver Contract · 02 Inference

A *run* is one start of the vendor tool for one request: a Subscription, a model, model settings, a conversation and a new message go in, and a stream of events comes out that ends in exactly one outcome. A Driver keeps no conversation of its own: chat sessions and their history belong to the caller. This specification states what every Driver offers for runs. It matters because the run is where money is spent and where version 1 lost the most: failures reported as success, turns that never ended, and an agent that forgot its own work between messages.

## Scope

Covered: the run request, the run as a process and its command, the event stream and its ordering rules, the three outcomes, how a conversation is continued, usage reporting, stopping a run, a run without tools, several runs at once.

Not covered: the tools an agent may use and its questions to the person (DRV-3); the list of error codes, rate limits and time limits (DRV-4); what each vendor tool is asked to do (CLD-2, CDX-2); which Subscription and model a message gets, retries and failover, chat sessions and their history, titles, all of which belong to the caller.

## Behaviour

### A run and the caller's units

The caller thinks in [Chat Exchanges](../GLOSSARY.md#chat-exchange): one message and everything needed to settle its answer. One Exchange normally needs one run and may need more, when the caller retries or moves to another route. A run corresponds to one [Agent Attempt](../GLOSSARY.md#agent-attempt). Inside a run the agent takes as many [Turns](../GLOSSARY.md#turn) as it needs: each tool call ends one Turn and its result starts the next. The Driver does not know Exchanges or Chat Sessions; a caller may attach labels of its own to a request and gets them back on every event.

A Driver never starts a run again by itself. Whether a failed run is repeated is the caller's decision, and the Driver's final event carries what that decision needs: whether anything was produced, and which tool calls were started and not finished.

Observed in version 1: the Driver ran one attempt per request and left retries to Root. Root repeated an attempt automatically only while nothing of it had been stored, at most twice for transient errors, and never repeated a tool whose effect was uncertain.

<!-- sources:
arbol:product-spec/03-turn-execution.md#Three nested units
arbol:product-spec/03-turn-execution.md#Rules to preserve
-->

### The run as a process

A run is one invocation of the Driver's `run` command and one process. The events leave on standard output, one per line, and the process ends after its final event.

What a run needs reaches it in two ways. A few short values are options on the command line: the Subscription, the model, the effort, the message. Everything else is in a *request file*: a JSON file that the caller writes before the run and names with `--request`. It holds what an option cannot: the earlier conversation of the chat with its tool calls, the system prompt, images, the limits. Together these are often larger than the 1 MiB that macOS allows for the arguments and environment of a program, they contain line breaks and quotation marks, and arguments can be read by every other process on the machine. The Driver reads the file once, at the start, and neither changes nor keeps it; the caller removes it when the run has ended. A run that needs only the short values, such as one question without tools, needs no request file. An example is in the Interface section.

A run needs no permission from its caller on its way (DRV-3). Two things can still pass from the caller to a run in progress: the answer to a question the agent asks the person, and stop. For both a run is started with a *control input*: the caller keeps the run's standard input open and writes lines to it. Without a control input a run takes nothing from the caller once it has started: the agent cannot ask the person anything, and the run is stopped by a signal or by `runs stop`.

A run does not outlive its caller. The Driver stops the run as soon as it can no longer write an event, and, where there is a control input, as soon as that input ends.

### The event stream

Every run produces one ordered stream. Each event carries the run's identifier and a sequence number that starts at 1 and has no gaps.

| Event | Meaning |
|---|---|
| `started` | The tool is running. Says how the conversation was continued (below), which model the tool reports, which tool version runs and which Build of the Driver |
| `text_delta` | A piece of the answer as it is produced. A hint: it may be missing or partial |
| `text` | One complete block of the answer. The truth for that block; it repeats what its deltas said |
| `thinking_delta`, `thinking` | The same pair for the model's reasoning, or the summary of it the vendor releases |
| `tool_started` | The agent called a tool: call identifier, tool name, input |
| `tool_output_delta` | A piece of a running tool's output, where the tool streams it |
| `tool_finished` | The call ended: success or failure, and its result, cut to the size limit with a flag when it was cut |
| `ask_opened`, `ask_closed` | The agent asked the person a question, and it was answered or withdrawn (DRV-3) |
| `usage` | The run's token and cost totals so far |
| `notice` | Something worth showing that changes nothing: the tool retried a request, the vendor moved the run to another model |
| `control_refused` | A line on the control input was not accepted: the error, and the question it named where it named one |
| `finished` | The outcome. Always the last event, exactly once |

Ordering rules: a `text` block that precedes a tool call is emitted before that call's `tool_started`, so prose and tool rows keep their true order. Every `tool_started` is followed by exactly one `tool_finished` for the same call before `finished`. Every `ask_opened` is followed by exactly one `ask_closed` before `finished`. An event that reports what a sub-agent did names the call that started the sub-agent, and a sub-agent's text is no part of the answer (DRV-3).

Observed in version 1: the Claude route streamed text and reasoning in pieces and emitted a tool call at its block boundary so that prose landed before the tool that followed it. The Codex route emitted text only as whole items at their end and command output only when the command had finished. Neither had a complete-block event beside the pieces; a caller that missed pieces had to wait for stored output.

<!-- sources:
arbol:drivers/claude/arbol_driver_claude/turn.py#TurnRunner._handle_stream_record
arbol:drivers/codex/arbol_driver_codex/protocol.py#map_exec_event
arbol:product-spec/03-turn-execution.md#Rules to preserve
-->

### Outcomes

| Outcome | When | What the final event carries |
|---|---|---|
| `completed` | The tool ended the run normally and did not mark its result as an error | Final usage |
| `failed` | Anything else that was not asked for: the tool reported an error, the vendor refused, the tool ended without a result, a limit was hit, the Driver could not start the tool | The error, with the vendor's own words where there are any; final usage; whether output was produced; the tool calls left unfinished |
| `cancelled` | The caller stopped the run | Final usage as far as known |

A failed or cancelled run keeps everything it emitted: events already sent stay valid and are not withdrawn. Tokens spent by a failed run are reported.

Observed in version 1: on the Claude route only wording about rate limits or authentication made a result a failure; every other error result ended the turn as completed. A probe on 5 October 2026 showed the installed tool reporting a failed login as a result of subtype `success` with its error flag set, which that rule also reads as completed. A rate-limited turn was stored as completed in the Driver's own bookkeeping.

<!-- sources:
arbol:drivers/claude/arbol_driver_claude/turn.py#TurnRunner._run_native
arbol:drivers/claude/arbol_driver_claude/rate_limit.py#is_rate_limit_signal
arbol:daemons/shared/arbol_shared/turn_store.py#_status_for_done
arbol:product-spec/03-turn-execution.md#Rules to preserve
-->

### The conversation

The caller owns the conversation. Chat sessions, their history, branches and edits belong to Arbol and its Trunks, and a Driver keeps none of it. With every run the caller sends the earlier conversation, oldest first, and the new message. The earlier conversation is everything the caller was told about it: the messages, and every tool call the agent made with its result. The caller hands the text of every reply back exactly as the run's `text` events carried it, because the Driver recognises a conversation by that text (DRV-6). A run must work from those alone, so a chat can change Subscription, model or Driver between messages and can branch from any point.

**Continuing the tool's own conversation.** The vendor tools save each conversation themselves, in the Subscription's home, and a saved conversation still holds what the agent read and did. So that the agent keeps this, the caller names its chat session with every run, by an identifier of its own. That is all the caller knows: it never sees a session of the vendor tool.

The Driver keeps a small map (DRV-6). For each chat session and Subscription it says which saved conversation of the tool belongs to it and which messages that conversation covers. The map holds identifiers and a digest, never the messages. A conversation is therefore stored in two places only: the vendor tool's folder and the caller's own store. Of the two, the caller's store is the source of truth. The tool's saved conversation is a working copy that exists for inference only: it may be removed at any time, and the Driver then builds a new one from the messages.

With each run the Driver looks the chat session up. When the map names a saved conversation for it on this Subscription, that conversation still exists, and it covers exactly the messages the caller sent, the Driver continues it. In every other case the Driver builds a new saved conversation from what the caller sent, in the tool's own format, as if the tool had held that conversation all along, and records it in the map once the run has completed. A run that fails or is stopped leaves no entry, and removes the one it was continuing, so that the next run builds the conversation again. The earlier tool calls go into it with their results, and the pictures with their messages, so the agent still knows what it saw, read and ran. This holds for tool calls made through the other Driver as well. This is what happens when a chat moves to another Subscription or to the other Driver, and when the Leather Bag has edited an earlier message or branched. The `started` event says which happened:

**Writing a tool call back.** A tool call of a history carries no identifier, so a Driver makes one up where its vendor tool wants one. Where the vendor tool takes a result as text, every Driver writes it by one rule:

| The result | Written as |
|---|---|
| Is text | That text |
| Is the result of `shell` | Its `output`, with a last line `exit code: <n>` when the call reported an exit code other than 0 |
| Is anything else | JSON text |
| Belongs to a failed call | The result as above where there is one, then the error text |

A result that was cut to the size limit is written as cut.

**The text form.** Where a vendor tool refuses a conversation built in its own format, the Driver sends the earlier conversation as text, in one message together with the new one:

```text
Earlier conversation, for context:

[User]
<text>
[Assistant]
<text>
[Tool call: <name>]
<input as JSON text>
[Tool result]            or: [Tool error]
<result as text, by the rule above>

New message:

<text of the new message>
```

Pictures of earlier messages are sent with the new message, in their order, and the text of an earlier message that had pictures ends with a line saying how many. The run's `started` event still says `rebuilt`, and a `notice` says that the text form was used.

The `started` event names one of three:

| Continuity | Meaning |
|---|---|
| `fresh` | No earlier messages; a new conversation |
| `resumed` | The tool's saved conversation was continued; the agent still has its tool trail |
| `rebuilt` | A new saved conversation was built from the caller's messages, with the reason, one of those listed in DRV-6 |

A run that names no chat session is built from its messages, and nothing is recorded for it.

Observed in version 1: no vendor-side conversation identifier was stored. The Claude route rewrote the tool's saved session from Arbol's history before every follow-up, and the Codex route started a new conversation for every attempt with the earlier messages written into the prompt. In both, the agent saw what it had said between messages but not what it had read or done, every message re-sent everything, and long chats grew until the vendor rejected them. The Product Specification proposes native resuming with a visible fallback as the default for the rewrite.

<!-- sources:
arbol:product-spec/03-turn-execution.md#Conversation continuity towards the provider
arbol:product-spec/12-lessons-and-invariants.md#Decisions for the successor's design
arbol:drivers/claude/arbol_driver_claude/jsonl.py#history_to_jsonl_lines
arbol:drivers/codex/arbol_driver_codex/protocol.py#render_prompt
-->

### Usage

A `usage` event carries the run's totals so far, not an increment: a caller that misses one loses nothing, and adding events up is never needed. Fields the vendor does not report are absent, never zero. Cost is present only where the vendor states one.

Observed in version 1: each report was an increment that Root summed within an attempt. On the Claude route sums from intermediate records could count the same tokens twice. On the Codex route cached and reasoning tokens were dropped and the model reported was the one asked for, also after the vendor had moved the run to another.

<!-- sources:
arbol:product-spec/03-turn-execution.md#Usage accounting
arbol:drivers/claude/arbol_driver_claude/protocol.py#extract_usage
arbol:drivers/codex/arbol_driver_codex/protocol.py#usage_from
-->

### Stopping a run

A run is stopped in one of three ways, all with the same effect: a `stop` line on its control input, an interrupt or termination signal to its process, or the command `runs stop` from another invocation. The Driver first asks the tool to stop, where the tool has a way to be asked. If the tool has not ended after 2 seconds the Driver ends its processes, the tool and everything it started. The whole stop is given 15 seconds; after that the Driver reports the run as cancelled and names what it could not end. Open questions are closed as withdrawn. Tool calls that were running get a `tool_finished` saying they were interrupted. The final event is `cancelled`.

Stopping a run that has already ended, or that the Driver does not know, succeeds and changes nothing, so a caller can always use stop to get back to a state in which it can send.

Nothing a run started is left running after its final event, also when the run ends normally or its caller goes away. One kind of program is out of a Driver's reach: a program that cuts itself loose from the command that started it, by moving into a process group or a session of its own, as a server does that makes itself a background service. It stays until somebody ends it (DRV-D33).

A stop reaches the sub-agents of a run as it reaches the agent: after the final event no sub-agent works on.

Observed with the installed tools on 6 October 2026, real runs: a process that a command left behind with `nohup … &` was gone on `codex` by the time the call was reported as complete; on `claude` it was still running after the tool had exited, in the process group of the shell call that had started it. A process that moved itself into a session of its own was still running after `codex` had exited, with the system's first process as its parent and nothing that names the run. Asked to stop its turn, `codex` ended the agent's turn and let a sub-agent work on until its own turn was stopped as well; `claude` ended a background sub-agent with the agent.

Observed in version 1: stop ended the tool's processes without telling the tool, with a forced kill after 2 seconds and 15 seconds for cleanup in total. On the Codex route commands the agent had started were left running on purpose.

<!-- sources:
arbol:product-spec/03-turn-execution.md#Cancel
arbol:product-spec/03-turn-execution.md#Limits and defaults
arbol:drivers/claude/arbol_driver_claude/turn.py#TurnRunner.cancel
arbol:drivers/codex/arbol_driver_codex/tool_process.py#ToolProcess._cleanup
-->

### A run without tools

A request may switch all tools off. Such a run is one prompt in and one text out. Where a vendor tool cannot be started without its tools, the Driver locks the run down instead, as its specification states, and reports what the agent does nonetheless (CDX-3). When the run also has no working folder, the Driver runs it in an empty folder of its own and removes the folder afterwards. This is what the caller uses for a [Completion](../GLOSSARY.md#completion), such as a chat title.

Observed in version 1: Completions for Anthropic and z.ai started the Claude tool once in a fresh empty folder with every tool disallowed; Completions for ChatGPT called the vendor's backend directly. They lived in Root, with their own retry loop.

<!-- sources:
arbol:daemons/core/arbol_core/completion.py
arbol:product-spec/05-intelligence-providers.md#Completions
-->

### Several runs at once

Any number of runs may be in progress at the same time, on one Subscription or on several. They share nothing but the Subscription's home: each is a process of its own. While a run lasts it keeps a record of itself in the state directory. That record is how another invocation lists the runs in progress, refuses a run identifier that is in use, and stops a run by its identifier.

Finding a run again after the process that started it has gone is not part of this contract: the run ends with its caller. See DRV-D2 in [DRV-0](00-overview-and-boundary.md#decisions).

## Requirements

| ID | A Driver must… | Origin | Verified by |
|---|---|---|---|
| DRV-2.1 | run exactly what the request names: Subscription, model, effort, system prompt, folders, conversation, message. A missing Subscription, model or effort is taken from the Driver's settings file, and where that names none, from the Driver's default Subscription and the vendor tool's own default model and effort | Kept | Claude: `C10`, `C40`, `run.request`, `C14`; Codex pending |
| DRV-2.2 | refuse a request, before anything is sent to the vendor, when the Subscription is not `signed_in`, a folder does not exist, the run identifier is already in use, or the Driver can tell that the tool will not accept the model or the effort | Changed | Claude: `C40`, `run.validation`; Codex pending |
| DRV-2.3 | emit one ordered stream per run with gapless sequence numbers, and end it with exactly one `finished` event on every path, including a failure to start and a failure inside the Driver | Kept | Claude: `C10`, `C12`, `C42`, `C43`, `run.failures`; cancellation pending SYL-83; Codex pending |
| DRV-2.4 | emit `text` and `thinking` blocks as complete blocks, whether or not their pieces were emitted | New | Claude: `C10`, `run.protocol`; Codex pending |
| DRV-2.5 | emit a `text` block that precedes a tool call before that call's `tool_started` | Kept | Claude: `C11`; Codex pending |
| DRV-2.6 | close every `tool_started` with one `tool_finished` and every `ask_opened` with one `ask_closed` before `finished` | Changed | Claude: `C11`, `C42` (tool calls); questions pending SYL-84; Codex pending |
| DRV-2.7 | report `completed` only when the tool ended the run without marking its result as an error | Changed | Claude: `C12`, `live.run` (completed results); failure envelopes recorded in `tool-probes-2026-10-05.md`; Codex pending |
| DRV-2.8 | keep everything already emitted when a run fails or is cancelled, and report the tokens it spent | Kept | Claude: `C42` (failed run); cancellation pending SYL-83; Codex pending |
| DRV-2.9 | say in the final event of a failed run whether output was produced and which tool calls were left unfinished | New | Claude: `C42`; Codex pending |
| DRV-2.10 | never start a run again by itself | Kept | Claude: `C42`; Codex pending |
| DRV-2.11 | produce a correct run from the caller's history alone, its messages and its tool calls, whatever Subscription, model or Driver served the earlier ones | Kept | Claude: `C14`, `continuity.session`; Codex pending |
| DRV-2.12 | continue the tool's saved conversation when its map names one for the request's chat session and Subscription, that conversation exists and it covers exactly the messages sent; otherwise build a new one from the messages in the tool's own format and record it | Changed | Claude: `C14`, `continuity.concurrent`; live verification pending renewed test-anthropic sign-in; Codex pending |
| DRV-2.13 | state in `started` whether the conversation is `fresh`, `resumed` or `rebuilt`, with the reason for a rebuild | New | Claude: `C14`; Codex pending |
| DRV-2.15 | report usage as totals for the run so far; leave out what the vendor does not report; name the model that actually ran | Changed | Claude: `C13`, `run.usage`, `run.zai`, `live.run`; Codex pending |
| DRV-2.16 | on stop, ask the tool to stop where it can be asked, end its processes after 2 seconds, and finish within 15 seconds in total | Changed | contract |
| DRV-2.17 | on stop, close open questions as withdrawn and running tool calls as interrupted, then emit `finished` with outcome `cancelled` | Kept | contract |
| DRV-2.18 | treat a stop of an ended or unknown run as success | Kept | contract |
| DRV-2.19 | leave no process a run started alive after its final event, and no sub-agent at work, except a process that left the command that started it for a process group or a session of its own (DRV-D33) | Changed | contract, live |
| DRV-2.20 | run a request with all tools switched off as one prompt in and one text out, in an empty folder of its own when none is given; where the vendor tool cannot be started without its tools, lock the run down as the Driver's specification states and report what the agent does nonetheless | Changed | Claude: `C19`, `live.run`; Codex pending |
| DRV-2.21 | keep runs independent: a failure, a stop or a slow consumer of one run never delays or fails another | Changed | Claude: `C18`; stop isolation pending SYL-83; Codex pending |
| DRV-2.22 | cut a tool result to 200 KiB, whatever its shape, and flag that it was cut | Changed | Claude: `C20`, `run.truncation`; Codex pending |
| DRV-2.23 | accept images with the message and with earlier messages as PNG, JPEG, WebP or GIF, and refuse any other type before starting the tool | Kept | Claude: `run.validation`, `run.images`, `C14`, `continuity.session`; Codex pending |
| DRV-2.24 | echo the caller's labels of a request on every event of its run and give them no meaning | New | Claude: `C10`, `run.images`, `run.refusal`; Codex pending |
| DRV-2.25 | write the events of a run to the standard output of its `run` command, one JSON object per line, and end the process after `finished` with the exit status of the outcome | New | Claude: `C10`, `C12`, `C33`, `C42`, `C43` (completed and failed); cancellation pending SYL-83; Codex pending |
| DRV-2.26 | stop a run, as in DRV-2.16, on a `stop` line, on an interrupt or termination signal, on `runs stop`, when its events can no longer be written, and when its control input ends | Changed | contract |
| DRV-2.27 | keep a record of every run in progress in the state directory, so that another invocation can list the runs, refuse a run identifier in use and stop a run by its identifier | New | Claude: `C33`, `C40` (active records, listing, exclusive IDs); stop pending SYL-83; Codex pending |
| DRV-2.28 | answer a line on the control input that it does not accept with a `control_refused` event, and let the run go on | New | Claude: `C33`; question answers pending SYL-84; Codex pending |
| DRV-2.34 | keep a map from the caller's chat session and the Subscription to the tool's saved conversation, holding identifiers and a digest of what that conversation covers and no message; write an entry only after a completed run and remove the entry of a conversation whose run ended any other way; keep no other record of a conversation | New | Claude: `C14`, `continuity.map`; Codex pending |
| DRV-2.35 | when it builds a conversation, write into it the earlier tool calls with their results, whichever Driver reported them, and the images of the earlier messages, all in the tool's own form, a `shell` call as the tool's own command call (DRV-3.19); fall back to text only where the tool refuses | New | Claude: `C14`, `continuity.session`, `probe.continuity`; live verification pending renewed test-anthropic sign-in; Codex pending |
| DRV-2.36 | write the result of a history's tool call as text by the rule above wherever its vendor tool takes results as text, and use the text form above, with a `notice`, where the vendor tool refuses a conversation built in its own format | New | Claude: `continuity.results`, `continuity.session`, `C14`; Codex pending |

DRV-2.14 switched off the vendor tool's own memory and the instructions of the working folder. It was withdrawn on 6 October 2026 with DRV-D26, and its number is not used again.

## Interface

Types are given in TypeScript. Times are ISO 8601 strings in UTC.

```ts
interface RunRequest {
  runId?: string;                    // chosen by the caller, or assigned by the Driver
  subscriptionId?: string;           // without it, the default Subscription (DRV-0, the settings file)
  model?: string;                    // an id from the Subscription's model catalog
  effort?: string;                   // one of that model's effort levels
  serviceTier?: string;              // where the catalog lists tiers for the model
  systemPrompt?: string;             // complete text, used as given
  workingDirectory?: string;         // absolute; required unless tools are off
  additionalDirectories?: string[];
  history: HistoryItem[];            // the earlier conversation of this branch, oldest first
  input: Message;                    // the new message, role "user"
  chatSessionId?: string;            // the caller's own identifier of the conversation; opaque to the Driver
  tools: Tools;                      // DRV-3: "all" or "none"
  limits?: RunLimits;                // DRV-4
  searchPath?: string[];             // extra folders for commands the agent runs
  labels?: Record<string, string>;   // the caller's own, echoed on every event
}

interface Message {
  role: "user" | "assistant";
  text: string;
  images?: Array<{ mediaType: "image/png" | "image/jpeg" | "image/webp" | "image/gif"; data: string }>; // base64
}

type HistoryItem =
  | ({ type: "message" } & Message)
  | { type: "tool_call";             // as the Driver reported it in tool_started and tool_finished
      name: string; input: unknown;
      ok: boolean; result?: unknown; error?: string };

type RebuildReason = "no_chat_session" | "first_run" | "history_differs" | "working_folder_changed"
  | "system_prompt_changed" | "conversation_gone" | "in_use" | "resume_refused";   // DRV-6

type RunEvent = { runId: string; seq: number; at: string; labels?: Record<string, string>;
                  parentCallId?: string }   // on what a sub-agent did: the call that started it (DRV-3)
  & (
  | { type: "started"; continuity: "fresh" | "resumed" | "rebuilt"; rebuildReason?: RebuildReason;
      subscriptionId: string; model?: string; effort?: string;   // what the run uses, named or taken from defaults
      toolVersion: string;
      driverBuild: string }            // the build number of the Build that runs, e.g. "a3" (BLD-0)
  | { type: "text_delta"; text: string }
  | { type: "text"; text: string }
  | { type: "thinking_delta"; text: string }
  | { type: "thinking"; text: string }
  | { type: "tool_started"; callId: string; name: string; input: unknown }
  | { type: "tool_output_delta"; callId: string; text: string }
  | { type: "tool_finished"; callId: string; ok: boolean; result?: unknown; error?: string;
      truncated?: boolean; interrupted?: boolean }
  | { type: "ask_opened"; askId: string; ask: Ask }                    // DRV-3
  | { type: "ask_closed"; askId: string; reason: "answered" | "withdrawn" }
  | { type: "usage"; usage: RunUsage }
  | { type: "notice"; code: string; message: string }
  | { type: "control_refused"; error: DriverError; askId?: string }
  | { type: "finished"; outcome: "completed" | "failed" | "cancelled";
      error?: DriverError;             // present exactly when outcome is "failed"
      usage?: RunUsage;
      producedOutput: boolean;
      unfinishedCalls: string[] }      // callIds started and not finished by the tool itself
);

interface RunUsage {
  model?: string;                      // the model that ran
  inputTokens?: number;                // includes cached input
  cachedInputTokens?: number;
  outputTokens?: number;               // includes reasoning output
  reasoningTokens?: number;
  costUsd?: number;
}

type ControlLine =                     // one JSON object per line on the standard input of `run --control`
  | { type: "answer"; askId: string; answer: Answer }   // DRV-3
  | { type: "stop" };
```

The commands, under the rules of the command line in [DRV-0](00-overview-and-boundary.md#the-command-line):

| Command | Input | Standard output |
|---|---|---|
| `run` | A `RunRequest`, from the options below and from `--request`. With `--control`, `ControlLine`s on standard input | One `RunEvent` per line, the last being `finished`. Exit status 0 for `completed`, 1 for `failed`, 2 for `cancelled` |
| `runs list` | none | The runs in progress: `runId`, `subscriptionId`, start time, labels |
| `runs stop <runId>` | none | Nothing. The command ends when the run's final event has been emitted |

The options of `run`:

| Option | Meaning |
|---|---|
| `--request <file>` | The whole `RunRequest` as JSON. With `-` it is read as the first line of standard input. Options given beside it replace its fields |
| `--subscription <id>` | `subscriptionId`. Without it, the default Subscription |
| `--model <id>`, `--effort <level>`, `--service-tier <tier>` | `model`, `effort`, `serviceTier` |
| `--system-prompt-file <file>` | `systemPrompt`, read from the file |
| `--cwd <folder>`, `--add-dir <folder>` | `workingDirectory`, and one entry of `additionalDirectories` each time it is given |
| `--tools <all or none>` | `tools`. With neither a request file nor `--tools`, tools are off |
| `--chat-session <id>`, `--run-id <id>` | `chatSessionId`, `runId` |
| `--label <key=value>` | One entry of `labels` each time it is given |
| The last argument | The text of `input` |
| `--control` | Standard input stays open for `ControlLine`s after the request |
| `--output <form>` | `events`, the default, or `text`: only the text of the answer, for use by hand |

History, images, limits and the search path have no option. They come in the request file. A request file for the third message of a chat, started with `arbol-claude-driver run --request /tmp/request-41.json --control`:

```json
{
  "subscriptionId": "zai",
  "model": "glm-5.3-flash",
  "effort": "high",
  "systemPrompt": "You are working in the repository at /Users/sam/repos/shop. …",
  "workingDirectory": "/Users/sam/repos/shop",
  "history": [
    { "type": "message", "role": "user", "text": "What does build.sh do?" },
    { "type": "tool_call", "name": "Read", "input": { "file_path": "/Users/sam/repos/shop/build.sh" },
      "ok": true, "result": "#!/bin/sh\nset -e\n…" },
    { "type": "message", "role": "assistant", "text": "It compiles the three packages and copies them to dist/." }
  ],
  "input": { "role": "user", "text": "Add a --clean option to it." },
  "chatSessionId": "chat-2041",
  "tools": "all"
}
```

Errors, from the list in DRV-4. Refusals of `run`, reported in a `finished` event that is then the only event of the stream: `not_found` (Subscription), `not_signed_in`, `invalid_input`, `in_use`, `tool_missing`, `tool_unsupported`. Errors of a failed run: `credential_rejected`, `rate_limited`, `context_exceeded`, `vendor_error`, `vendor_unavailable`, `tool_failed`, `limit_reached`, `internal`, and `invalid_input` or `tool_unsupported` where the fault shows only once the vendor or the tool has been asked.

## Known problems in version 1

Not to be reproduced.

- **A failure could look like success.** See Outcomes.
- **A turn could wait forever.** No time limit of any kind existed, and a question from the tool that the Driver did not understand was never answered.
- **The agent forgot its work between messages.** See The conversation.
- **Two ways to end a failed turn.** On the Codex route a failure reported by the tool closed the turn with one sequence of events and a failure of the connection with another.
- **Usage had to be added up, and did not always add up.** See Usage.
- **One malformed message from the tool disabled every later turn** of every chat on the Claude route until the Driver was restarted.
- **Everything was kept in the Driver's memory.** The replay copy of each turn held every piece of output, was never compacted, and was released only when the next turn started.

<!-- sources:
arbol:product-spec/03-turn-execution.md#Known problems and lessons
arbol:daemons/shared/arbol_shared/turn_store.py#TurnStore
arbol:drivers/codex/arbol_driver_codex/turn.py#TurnRunner._run_one_cycle
-->

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| DRV-D9 | Is resuming the tool's own conversation in the first release? | Yes, with rebuilding as the fallback. It is the Product Specification's default, and it is what gives the agent its tool trail back | Decided 6 October 2026 by the owner: a Driver continues the tool's saved conversation when it can and builds a new one from the history otherwise (DRV-D23) |
| DRV-D10 | How does a Driver know that a saved conversation still fits the messages it is sent? | By what its map records for the conversation: the number of messages it covers and a digest of the user messages in order, with their images. The Driver compares these with the messages of the request; an edited, removed or branched message makes them differ and causes a rebuild. The text of assistant messages is left out of the digest, because it came from the tool and the caller may store it in another form | Decided 6 October 2026 by the owner: the proposed default (SYL-41). That fingerprint covered the user's messages only. On the same day the owner said that the whole conversation was meant, after a replaced reply turned out to go unnoticed otherwise, and the text of the replies became part of it; tool calls stay out (SYL-72). The exact digest and the further checks are in DRV-6 |
| DRV-D11 | Does a run without a working folder leave anything behind? | No: its folder and the tool's saved conversation for it are removed, and nothing is recorded for it in the map | Decided 6 October 2026 by the owner: the proposed default (SYL-42). Such a run belongs to no chat: the tool is told to save nothing for it, and a conversation file the Driver itself wrote for it is removed when the run ends. This is not the clean-up of a chat's conversation, which a Driver never does (CLD-D7, CDX-D6) |
| DRV-D22 | Who keeps chat sessions and their history? | The caller: Arbol and its Trunks. A Driver is a bridge to the agent and keeps no conversation of its own; it is sent the messages with every run | Decided 6 October 2026 by the owner |
| DRV-D23 | How does a Driver find the tool's saved conversation for a chat? | The caller names its own chat session with every run and knows nothing of the vendor tools' sessions. The Driver keeps the map from chat session and Subscription to the tool's saved conversation. Conversations themselves are stored only in the vendor tools' folders and in the caller's store | Decided 6 October 2026 by the owner |
| DRV-D33 | A program that makes itself a background service cuts every tie to the command that started it, and a Driver cannot find it again when the run ends. Is that accepted? | Yes. A Driver ends what stayed with the agent's commands, which covers a command simply left in the background. The vendor tools' own command-line programs leave such a program running too. Finding it needs what version 1 had: every run started as a job of the system's service manager, a large piece of code and one more step at the start of every message | Decided 6 October 2026 by the owner: accepted, the proposed default (SYL-73) |
