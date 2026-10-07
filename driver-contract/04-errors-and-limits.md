---
role: authored
spec: DRV-4
status: accepted
---
# Driver Contract · 04 Errors and limits

Every failure a Driver reports is one object with a code from a closed list. This specification defines that list, what a caller may conclude from each code, how rate limits and rejected credentials are told apart from everything else, and the time limits of a run. It matters because the caller's next step depends on it: wait and try again, try another route, ask the Leather Bag to sign in, or stop. Version 1 made that choice by matching error text in two places, and each tool update moved the text.

## Scope

Covered: the error object and its codes, retrying, rate limits, rejected credentials, the vendor tool's own retries, the time limits of a run, limit information that arrives during a run.

Not covered: what the caller does with an error: retries, waiting out a limit, moving to another route (the caller; [Product Specification, Turn execution](../../arbol_deprecated_v1/product-spec/03-turn-execution.md)); how each Driver recognises a failure in its tool's output (CLD-4, CDX-4).

## Behaviour

### The error object

A Driver reports a failure in one of two places: as the result of a command that was refused or failed, or in the final event of a run that failed. Both carry the same object: a code, a message, whether trying again can help, and where known a time to wait and a remedy.

The message is written for the Leather Bag. It says what happened in the vendor's own words where the vendor gave any, and it never contains a credential or a whole response of the vendor. Technical detail travels beside it: the vendor's status, the vendor's own error code, the tool's exit status and version, and at most 1 KiB from the end of the tool's log.

| Code | Meaning | Trying again can help | Typical remedy |
|---|---|---|---|
| `invalid_input` | The request is wrong: an unknown family or setting, a folder that does not exist, a model the vendor does not offer this account, an effort the model does not take, an answer a question does not accept | No | Change the request |
| `not_found` | The Subscription, run or question does not exist, or the question was withdrawn | No | |
| `in_use` | The run identifier is taken, or the Subscription has runs in progress | No | Wait for the runs, or force |
| `unsupported` | This Driver does not offer the operation or the option | No | |
| `not_signed_in` | The Subscription is not `signed_in` | No | Sign in |
| `credential_rejected` | The vendor rejected the Subscription's credential, and the tool's own renewal did not help | No | Sign in again, or replace the key |
| `rate_limited` | The account has reached a limit of the vendor: too many requests, or an allowance used up | Yes, after waiting | Wait until the stated time, or use another Subscription |
| `context_exceeded` | The conversation no longer fits the model | No | Start a new chat, or continue from a shorter history |
| `vendor_unavailable` | The vendor could not be reached, was overloaded, or failed on its side | Yes | Try again |
| `vendor_error` | The vendor refused the request for another reason, such as its usage policy | No | Read the message |
| `tool_missing` | The vendor tool was not found | No | Install the tool |
| `tool_unsupported` | The vendor tool is too old, does not accept what the Driver sends, or is too old for the model | No | Update the tool |
| `tool_failed` | The vendor tool ended without a result, broke its own protocol, or could not be started | No | Read the detail |
| `limit_reached` | A time limit of the request was reached | No | Raise the limit, or try again |
| `state_newer` | The state directory was written by a newer Build of this Driver (DRV-6) | No | Run that Build, or a newer one |
| `internal` | A defect in the Driver | No | |

A failure the Driver cannot place is `vendor_error` when the vendor said something and `tool_failed` when it did not. Neither is marked as worth trying again: an unknown failure is treated as permanent.

Observed in version 1: a failure was an event with a free text. The Claude route added one flag for authentication failures. Root decided what to do by matching phrases in that text, with its own copy of the phrase list. A missing executable surfaced as "launch outcome remains unresolved".

<!-- sources:
arbol:drivers/claude/arbol_driver_claude/protocol.py#AUTH_ERROR_INDICATORS
arbol:daemons/core/arbol_core/orchestration/support.py#_is_claude_auth_error
arbol:product-spec/03-turn-execution.md#Failures and what the Leather Bag sees
-->

### Recognising a failure

A Driver classifies by what its tool states in fields: an error code, a status number, a reason for ending. It falls back to the wording of a message only when the tool states nothing, and then records that it did. The fallback lists are those of version 1, kept deliberately generous for rate limits, because a wrongly assumed limit costs a wait and a missed one costs a failed turn.

Observed in version 1: both routes classified by wording alone. The match was a search for short fragments anywhere in the text, so a login failure that mentioned a quota became a rate limit, and "retry after 5 minutes" was read as five seconds. The tools' own fields, including the error information of the Codex protocol and the limit records of the Claude stream, were not read.

<!-- sources:
arbol:drivers/claude/arbol_driver_claude/rate_limit.py#is_rate_limit_signal
arbol:drivers/claude/arbol_driver_claude/rate_limit.py#extract_recovery_seconds
arbol:drivers/codex/arbol_driver_codex/rate_limit.py#is_rate_limit_text
-->

### Rate limits

A run that hits a limit of the account fails with `rate_limited`. Where the vendor says when the limit ends, the error carries the wait in seconds; where it does not, the error carries none, and the Driver does not invent one. The Driver does not wait and does not start the run again: how long to wait, whether to try another route, and when to give up are the caller's decisions.

A limit concerns the account, so the Subscription stays `signed_in`.

Observed in version 1: the Driver reported the limit with an optional hint in seconds. Root then avoided that route until the hint had passed, or for 60 seconds without one, waited at most 300 seconds on the same route when there was no other, and made at most three attempts per message.

<!-- sources:
arbol:product-spec/03-turn-execution.md#Limits and defaults
arbol:product-spec/05-intelligence-providers.md#The IP of each later turn
arbol:daemons/core/arbol_core/rate_limit_tracker.py#RateLimitTracker
-->

### Rejected credentials

When the vendor rejects the credential in a run or in any other operation, the error is `credential_rejected` and the Subscription moves to `needs_attention` with the same remedy (DRV-1.7). The vendor tools renew their own logins; a rejection that reaches the Driver has survived that. The Driver does not wait while the tool keeps retrying with a credential the vendor has already refused: it ends the run at the first such refusal it can see.

Observed in version 1: Root renewed the Anthropic token before a turn when it was about to expire, and once after a failure, repeating the turn only if nothing had been produced. With a wrong gateway key, the installed tool retries ten times over almost three minutes before it gives up.

<!-- sources:
arbol:product-spec/05-intelligence-providers.md#Expiry and what the Leather Bag sees
arbol:daemons/core/arbol_core/orchestration/agent_attempt_execution.py#AgentAttemptExecutionService._refresh_bound_subscription_token
-->

### Time limits of a run

| Limit | Meaning | Default |
|---|---|---|
| Start | From starting the tool to its first sign that the run is under way | 60 seconds |
| Idle | Time without any sign of life from the tool, counted only while no tool call is running, no command the agent left in the background is running and no question is open | 15 minutes |
| Total | From start to the final event | None |

The request may set the idle and the total limit. When a limit is reached the Driver stops the run as it stops any run (DRV-2.16) and finishes it as `failed` with `limit_reached`, naming the limit.

A command the agent runs is never ended for being slow: the idle limit does not count while it runs, also when the agent left it running in the background (DRV-3.32), and how long a command may run is the vendor tool's own setting. A question from the agent waits for its answer without limit (DRV-3.27).

The vendor tools retry failed requests to the vendor by themselves. A Driver reports each retry as a `notice` and bounds the retrying where the tool lets it.

Observed in version 1: no limit of any kind. A silent turn held its processes until someone stopped it, and a separate scan marked a chat as stalled after 15 minutes without acting on it.

<!-- sources:
arbol:product-spec/03-turn-execution.md#Limits and defaults
arbol:product-spec/06-tools-and-permissions.md#Rules to preserve
-->

### Limit information during a run

Both vendor tools report the account's limit windows while a run is in progress, unasked and at no cost. A Driver keeps the latest such report of a run and, when the run ends, stores it as the Subscription's last usage report (DRV-1.18). This is not polling: nothing is requested.

## Requirements

| ID | A Driver must… | Origin | Verified by |
|---|---|---|---|
| DRV-4.1 | report every failure as one error object with a code from the table above | Changed | SYL-95 Python: Claude `C26`, `test_runtime.CompatibilityTests`, `test_runtime.ProtocolTests`, `test_runtime.TransportTests`; Codex `test_app_server.AppServerTests`, `test_request_events.Mapper` (existing scoped coverage; pending features unchanged); prior verification: Claude: `base.errors`, `base.cli`, `C26`; Codex: `errors`, `base.cli`, `base.tool-failure`, `C12`, `C42`, `run.failures` (base errors and baseline vendor/tool failures; classification pending SYL-91) |
| DRV-4.2 | write the message for the Leather Bag, in the vendor's words where there are any, without a credential and without more than 1 KiB of the tool's output | Kept | SYL-95 Python: Claude `test_runtime.CompatibilityTests`, `test_runtime.ProtocolTests`, `test_runtime.TransportTests`; Codex `test_app_server.AppServerTests`, `test_request_events.Mapper` (existing scoped coverage; pending features unchanged); prior verification: Claude: `base.error-text`, `base.settings`, `errors.diagnostics`; Codex: `errors`, `settings`, `base.tool-failure` (redaction, Unicode-safe one-KiB excerpts and withheld faulty values) |
| DRV-4.3 | mark an error as worth trying again only for `rate_limited` and `vendor_unavailable` | Kept | SYL-95 Python: Claude `test_runtime.CompatibilityTests`, `test_runtime.ProtocolTests`, `test_runtime.TransportTests`; Codex `test_app_server.AppServerTests`, `test_request_events.Mapper` (existing scoped coverage; pending features unchanged); prior verification: Claude: `base.errors`, `C26`; Codex: `errors` (exact retry policy) |
| DRV-4.4 | classify by the fields the tool states, fall back to wording only where it states none, and record in the detail which was used | Changed | SYL-95 Python: Claude `C26`, `test_runtime.CompatibilityTests`, `test_runtime.ProtocolTests`, `test_runtime.TransportTests`; Codex pending SYL-91 (run classification, retries, limits and clocks) (existing scoped coverage; pending features unchanged); prior verification: Claude: `errors.precedence`, `C26`; Codex pending |
| DRV-4.5 | give the wait of a `rate_limited` error only when the vendor names a time | Changed | SYL-95 Python: Claude `C27`, `test_runtime.CompatibilityTests`, `test_runtime.ProtocolTests`, `test_runtime.TransportTests`; Codex pending SYL-91 (run classification, retries, limits and clocks) (existing scoped coverage; pending features unchanged); prior verification: Claude: `errors.wait`, `C27`; Codex pending |
| DRV-4.6 | never wait out a limit and never start a run again after one | Kept | SYL-95 Python: Claude `C27`, `test_runtime.CompatibilityTests`, `test_runtime.ProtocolTests`, `test_runtime.TransportTests`; Codex pending SYL-91 (run classification, retries, limits and clocks) (existing scoped coverage; pending features unchanged); prior verification: Claude: `C26`, `C27`; Codex pending |
| DRV-4.7 | move the Subscription to `needs_attention` together with every `credential_rejected` error | Changed | SYL-95 Python: Claude `C4`, `C28`, `test_runtime.CompatibilityTests`, `test_runtime.ProtocolTests`, `test_runtime.TransportTests`; Codex pending SYL-91 (run classification, retries, limits and clocks) (existing scoped coverage; pending features unchanged); prior verification: Claude: `C4`, `C28`, `errors.run-report`; Codex pending |
| DRV-4.8 | end a run at the first refusal of the credential it can see, without waiting for the tool's retries | New | SYL-95 Python: Claude `C28`, `test_runtime.CompatibilityTests`, `test_runtime.ProtocolTests`, `test_runtime.TransportTests`; Codex pending SYL-91 (run classification, retries, limits and clocks) (existing scoped coverage; pending features unchanged); prior verification: Claude: `C28`, `probe.errors`; Codex pending |
| DRV-4.9 | apply the start limit of 60 seconds and the idle and total limits of the request, with the defaults above | Changed | SYL-95 Python: Claude `C29`, `test_runtime.CompatibilityTests`, `test_runtime.ProtocolTests`, `test_runtime.TransportTests`; Codex pending SYL-91 (run classification, retries, limits and clocks) (existing scoped coverage; pending features unchanged); prior verification: Claude: `C29`, `errors.clocks`; Codex pending |
| DRV-4.10 | stop the idle clock while a tool call or a command left in the background is running, or a question is open | New | SYL-95 Python: Claude `C29`, `test_runtime.CompatibilityTests`, `test_runtime.ProtocolTests`, `test_runtime.TransportTests`; Codex pending SYL-91 (run classification, retries, limits and clocks) (existing scoped coverage; pending features unchanged); prior verification: Claude: `C29`, `errors.clocks`; Codex pending |
| DRV-4.11 | on a reached limit stop the run as in DRV-2.16 and finish it as `failed` with `limit_reached` | New | SYL-95 Python: Claude `C29`, `test_runtime.CompatibilityTests`, `test_runtime.ProtocolTests`, `test_runtime.TransportTests`; Codex pending SYL-91 (run classification, retries, limits and clocks) (existing scoped coverage; pending features unchanged); prior verification: Claude: `C29`; Codex pending |
| DRV-4.12 | report the vendor tool's own retries as `notice` events and bound them where the tool allows | New | SYL-95 Python: Claude `C28`, `test_runtime.CompatibilityTests`, `test_runtime.ProtocolTests`, `test_runtime.TransportTests`; Codex pending SYL-91 (run classification, retries, limits and clocks) (existing scoped coverage; pending features unchanged); prior verification: Claude: `C28`, `probe.errors`; Codex pending |
| DRV-4.13 | store the latest limit information a run received as the Subscription's last usage report when the run ends | New | SYL-95 Python: Claude `C30`, `test_runtime.CompatibilityTests`, `test_runtime.ProtocolTests`, `test_runtime.TransportTests`; Codex pending SYL-91 (run classification, retries, limits and clocks) (existing scoped coverage; pending features unchanged); prior verification: Claude: `C30`, `errors.usage`, `live.errors-usage`; Codex pending |
| DRV-4.14 | name the tool, the found version and the needed version in `tool_missing` and `tool_unsupported` | New | SYL-95 Python: Claude `C31`, `test_runtime.CompatibilityTests`, `test_runtime.ProtocolTests`, `test_runtime.TransportTests`; Codex `C31`, `test_app_server.AppServerTests`, `test_request_events.Mapper` (existing scoped coverage; pending features unchanged); prior verification: Claude: `base.tool-missing`, `base.tool-old`, `C31`; Codex: `base.tool-missing`, `base.tool-old`, `C31` |
| DRV-4.15 | finish a run as `failed` with `internal` when the Driver itself fails, and never leave a run without a final event | Kept | SYL-95 Python: Claude `C43`, `test_runtime.CompatibilityTests`, `test_runtime.ProtocolTests`, `test_runtime.TransportTests`; Codex `C43`, `test_app_server.AppServerTests`, `test_request_events.Mapper` (existing scoped coverage; pending features unchanged); prior verification: Claude: `C43`, `run.failures`; Codex: `C43`, `run.failures` (internal state failure and transport/protocol failures each end with one final event) |

## Interface

```ts
interface DriverError {
  code: "invalid_input" | "not_found" | "in_use" | "unsupported" | "not_signed_in" | "credential_rejected"
      | "rate_limited" | "context_exceeded" | "vendor_unavailable" | "vendor_error"
      | "tool_missing" | "tool_unsupported" | "tool_failed" | "limit_reached" | "state_newer" | "internal";
  message: string;
  retryable: boolean;
  retryAfterSeconds?: number;        // only with "rate_limited", only when the vendor names a time
  remedy?: string;
  detail?: {
    basis: "fields" | "wording";     // how the failure was classified
    vendorStatus?: number;
    vendorCode?: string;
    limit?: "start" | "idle" | "total";
    toolExit?: number;
    toolVersion?: string;
    neededVersion?: string;
    excerpt?: string;                // at most 1 KiB from the end of the tool's log
  };
}

interface RunLimits {
  idleSeconds?: number;              // default 900; 0 switches the limit off
  totalSeconds?: number;             // default none
}
```

## Known problems in version 1

Not to be reproduced.

- **Error text was the interface.** Two components matched phrases, and their lists differed.
- **A login failure could become a rate limit**, and a wait of minutes could be read as seconds.
- **The tools' own error fields were ignored.**
- **Nothing ended a silent turn.**
- **A wrong key cost minutes**, because nothing ended the tool's retries.

<!-- sources:
arbol:product-spec/03-turn-execution.md#Known problems and lessons
arbol:drivers/codex/arbol_driver_codex/rate_limit.py#extract_recovery_seconds
-->

## Python migration verification, 7 October 2026

SYL-95 verification is recorded in the requirement-level `~/Artifacts/arbol/driver-contract/python-migration-coverage-2026-10-07.json` and the Driver records `research/python-migration-2026-10-07/verification.json`. Python check names identify the copied standard-library unittest suites and the unchanged shared scenarios. Prior Driver unit/probe/live names refer to historical TypeScript evidence; unchanged shared build-tool and runner names remain active. Claude passes the complete 38-scenario suite; Codex passes its five original scoped groups (29 scenario invocations, with the same exclusions), and remains a development candidate. No historical live result is treated as fresh Python evidence, and previously unobserved vendor failures stay unobserved.

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| DRV-D15 | Is there an idle limit by default? | Yes, 15 minutes, counted only between signs of life while no tool call runs and no question is open. Version 1 had none and called a chat stalled after the same time | Decided 6 October 2026 by the owner: yes, 15 minutes, because nothing else tells a tool that hangs from an agent that thinks for long. Both are silent, and the tool's process is alive in both cases (SYL-46) |
| DRV-D16 | Is a conversation that no longer fits its own code? | Yes, `context_exceeded`: the caller's remedy differs from every other refusal | Decided 6 October 2026 by the owner: yes (SYL-47) |
| DRV-D17 | Does the Driver ask the vendor for the reset time when a limit error names none? | Only where the tool offers a request for it at no cost; otherwise the error carries no wait | Decided 6 October 2026 by the owner: the proposed default. The Codex Driver has such a request and uses it (CDX-D12; SYL-48, SYL-69) |
