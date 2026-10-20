---
role: authored
spec: DRV-1
status: accepted
---
# Driver Contract · 01 Subscriptions

A [Subscription](../GLOSSARY.md#subscription) is one signed-in account with a vendor. This specification states what every Driver offers for managing Subscriptions: creating them, signing in and out, telling whether an account still works, reading its usage and listing its models. It matters because a Subscription is the unit that gets billed and rate-limited, and because an account that Arbol believes is signed in but is not produces failures that look like vendor outages.

## Next-release routing decision

Decided by the owner on 20 October 2026: the first OpenCode Driver must support z.ai and DeepSeek using the API keys already stored in OpenCode; the target Claude Driver serves only the Anthropic subscription family. The saved OpenCode connections are Z.AI Coding Plan and DeepSeek. The [OpenCode Integration Specs Saga](https://linear.app/sylvan-stack/project/opencode-integration-specs-saga-f1bdce69e9da) specifies the change, including [OPC-0's routing and cutover requirements](https://linear.app/sylvan-stack/document/opc-0-opencode-driver-overview-and-boundary-de78a2d90e10).

This decision supersedes the older routing scope below for the next release. The z.ai-on-Claude behaviour and its verification below describe the pre-cutover contract. SYL-265 must reconcile the detailed family, credential and capability requirements, and SYL-267 must review their compatibility and cutover checks before implementation. The new OpenCode specification set is still draft. No installed route or credential is changed by this notice; after cutover, a stale Claude z.ai request must fail before inference rather than run as Anthropic.

## Scope

Covered: the Subscription record and its states, every Subscription operation, the sign-in exchange with the caller, credential rules, usage reports, model catalogs.

Not covered: what each vendor tool is asked to do ([Claude Driver](../../arbol-claude-driver/specs/01-subscriptions.md), [Codex Driver](../../arbol-codex-driver/specs/01-subscriptions.md)); using a Subscription for inference, including what happens when a run meets a rate limit (DRV-2, DRV-4); which Subscription a chat uses, and which models are enabled, which stay with the caller's route settings; default models and efforts, which are in the Driver's settings file (DRV-0); the named-secret store and integration credentials, which are not Subscriptions.

## Behaviour

### The record

A Driver has one Subscription for each vendor family it serves from the start, named after the family: `anthropic` and `zai` for the Claude Driver, `chatgpt` for the Codex Driver. One of them is the Driver's default, used by a run that names none. Further Subscriptions of a family can be created through the Driver. A Subscription has a stable identifier, a short name that a caller types on the command line ([DRV-D21](#decisions)), a vendor family, a label the Leather Bag can edit, family-specific settings that contain no secret and are written in the Driver's settings file (DRV-0), a state, and what the vendor reports about the account. Several Subscriptions of the Anthropic family or of a key family can exist side by side, each with its own credential. The ChatGPT family has one, `chatgpt`, on the owner's own sign-in of `codex` ([DRV-0](00-overview-and-boundary.md#the-vendor-tools-home)).

Observed in version 1: exactly three Subscriptions existed, one per vendor family, declared in code. They could not be added, renamed or removed.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:daemons/core/arbol_core/subscriptions.py#DEFAULT_SUBSCRIPTIONS`
- `arbol_deprecated_v1:daemons/core/arbol_core/db/subscriptions.py#upsert_subscription`
- `arbol_deprecated_v1:product-spec/05-intelligence-providers.md#A new requirement, not parity`

### States

| State | Meaning | Usable for inference |
|---|---|---|
| `signed_out` | No credential | No |
| `signing_in` | A sign-in attempt is pending | No |
| `signed_in` | A credential is stored and the last check or use did not reject it | Yes |
| `needs_attention` | A credential is stored and the vendor rejected it. The record carries the reason and what to do | No |

Transitions:

| From | Event | To |
|---|---|---|
| `signed_out` | Sign-in started | `signing_in` |
| `signing_in` | Vendor confirmed | `signed_in` |
| `signing_in` | Vendor refused, attempt cancelled, attempt timed out, or a new attempt replaced it | `signed_out` (the caller receives the reason; nothing is stored) |
| `signed_in` | Vendor rejects the credential in any operation or run | `needs_attention` |
| `needs_attention` | Sign-in started | `signing_in` |
| `needs_attention` | A later check finds the credential working | `signed_in` |
| any | Sign-out | `signed_out` |

Observed in version 1: three reachable states, logged out, logged in and error, where error meant only "the last sign-in attempt failed". A fourth, expired, was declared and never set. An account whose credential the vendor rejected during a turn kept the state logged in.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/05-intelligence-providers.md#Sign-in and sign-out`
- `arbol_deprecated_v1:product-spec/05-intelligence-providers.md#Expiry and what the Leather Bag sees`
- `arbol_deprecated_v1:daemons/core/arbol_core/db/subscriptions.py#set_subscription_auth`
- `arbol_deprecated_v1:daemons/core/arbol_core/rpc/subscription.py#_await_login_completion`

### Signing in

Signing in is an exchange in steps. The Driver says what the caller must show or collect; the caller never knows which vendor mechanism is behind it.

| Step the Driver returns | What the caller does |
|---|---|
| `open_url` | Shows the address to the Leather Bag in a window that refuses every host not in the step's host list. When the step carries a code, shows that code too: the Leather Bag types it on the vendor's page, which may be opened on another device. The Driver notices completion itself |
| `enter_code` | Collects a short text the vendor displayed and hands it back. Such a code works once and is of no use afterwards |
| `store_secret` | Collects a secret, such as a key, in a concealed field and stores it in the Keychain item the step names. The caller does not hand it to the Driver and does not keep or log it. The Driver reads the item and goes on by itself |
| `done` | Nothing. The Subscription is `signed_in` |
| `failed` | Shows the error |

One `sign-in` command lasts for the whole attempt. It writes each step as one line on standard output. The only thing it reads is the code of an `enter_code` step, as one line on standard input. Ending the command cancels the attempt.

A secret never travels through the command. For a `store_secret` step the caller stores the secret in the Keychain item the step names, and the Driver reads it there. The owner can also store it by hand with the system's own Keychain tools, before the attempt or during it: a `sign-in` that finds the item filled goes straight on.

Where the settings file names a command as the source of a Subscription's key (DRV-0), there is no `store_secret` step. The Driver runs the command, takes what it prints as the key, and goes on.

One attempt per Subscription is pending at a time; starting another ends the first. An attempt that is not completed ends by itself after five minutes. An attempt does not outlive its command: a Subscription recorded as `signing_in` whose command is gone is `signed_out`.

Observed in version 1: the Anthropic family used an authorisation page in an Arbol-owned window with a local callback listener, a pending attempt was replaced by a second login, and a background watcher gave up after about five minutes. The ChatGPT family had no in-app sign-in: a credential file left by the vendor tool was copied. The z.ai family took a pasted key.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:daemons/core/arbol_core/subscription_login.py#start_login`
- `arbol_deprecated_v1:daemons/core/arbol_core/subscription_login.py#complete_login`
- `arbol_deprecated_v1:daemons/core/arbol_core/rpc/subscription.py#_login`
- `arbol_deprecated_v1:daemons/core/arbol_core/rpc/subscription.py#_set_token`
- `arbol_deprecated_v1:daemons/core/arbol_core/universe_import.py#import_from_auth_json`

### Credentials

`anthropic` and `chatgpt` use the owner's own sign-in of the tool, which the tool keeps and renews in its default home ([DRV-0](00-overview-and-boundary.md#the-vendor-tools-home)). The Driver does not copy it. A further Subscription of the Anthropic family uses a long-lived token instead: its sign-in runs `claude setup-token` in a temporary home that is removed afterwards, so the owner's own sign-in is never touched, and the Driver keeps the token like a key. A token is not renewed by the tool; when the vendor rejects it, the Subscription needs attention and is signed in again. A key or a token is in the Keychain, one item per Subscription, under the Driver's own service name with the Subscription's identifier as the account. The caller or the owner puts it there. The Driver reads it there and nowhere else: a key is never an argument, never on standard input and never in a file. A Driver that runs with another state directory than the default one uses a service name of its own for it: the usual name, a dot, and the first 12 hexadecimal digits of the SHA-256 of that directory's real path. A test or a second installation therefore never touches the owner's items. The owner can name another source in the settings file: a command that prints the key. The Driver then runs that command whenever it needs the key and keeps what it prints nowhere.

A key is checked when the Driver reads it at sign-in: printable ASCII without spaces. A rejection names up to three offending characters with their code points, because a paste mangled by a notes application otherwise fails much later with an encoding error. A key that fails this check, or that the vendor rejects at sign-in, is removed from the item, so that a rejected key is not left behind. A key that came from a command cannot be removed by the Driver: the sign-in fails and says so.

Observed in version 1: every credential was a Keychain item written through the Security framework, never through the system's command-line helper. A copied ChatGPT credential went stale because the vendor tool rotated its renewal token after the copy was taken; the recovery was to copy again. Two concurrent turns on one Anthropic account could both renew the same credential in the legacy runtime; the newer runtime added a lock per Subscription.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:daemons/core/arbol_core/subscriptions.py#SubscriptionCredentialStore`
- `arbol_deprecated_v1:daemons/shared/arbol_shared/macos_keychain.py`
- `arbol_deprecated_v1:daemons/core/arbol_core/rpc/subscription.py#_set_token`
- `arbol_deprecated_v1:daemons/shared/arbol_shared/state/credentials.py#ProviderCredentials.options`
- `arbol_deprecated_v1:daemons/core/arbol_core/orchestration/agent_attempt_execution.py#AgentAttemptExecutionService._refresh_bound_subscription_token`

### Usage

A usage report answers "how much of this account's allowance is used and when does it reset". It is fetched when asked for, never in the background. The outcome is always one of four, and only the first carries numbers:

| Outcome | Meaning |
|---|---|
| `ok` | The vendor answered; windows follow |
| `needs_sign_in` | The Subscription is not `signed_in` |
| `unavailable` | The vendor could not be reached or answered something unreadable; the message says which |
| `unsupported` | This family offers no usage reading |

The Driver keeps the last `ok` report with the Subscription so a caller can show it at once on start-up and replace it when a fresh one arrives.

Observed in version 1: usage was fetched when the accounts page opened, after sign-in and on Refresh; nothing polled. The last good Anthropic reading was cached. Three different sources were in use, one of them a web page read in a hidden browser session.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/05-intelligence-providers.md#Usage and rate-limit information`
- `arbol_deprecated_v1:daemons/core/arbol_core/rpc/subscription.py#_zai_usage`
- `arbol_deprecated_v1:daemons/core/arbol_core/rpc/subscription.py#_codex_usage`
- `arbol_deprecated_v1:daemons/core/arbol_core/db/subscriptions.py#set_subscription_usage_cache`

### Model catalog

The model catalog lists what this Subscription can run. It always comes from the Subscription's own vendor family. When the vendor cannot be asked, the Driver answers with a built-in list for that family and marks it as built-in; it never answers with another family's list. Fetching a catalog spends no inference quota. Where the vendor tool reports which effort levels a model accepts, the catalog carries them per model in the vendor's own words.

Observed in version 1: the Anthropic list was read from the vendor's interface with the account's token and each model was then probed with a one-token request; the ChatGPT list came from a backend address that only reveals newer models to a recent enough client version; the z.ai list came from z.ai's own interface. One vocabulary of seven thinking levels was mapped onto every route, and three of the seven requested nothing or the same thing on some routes.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:daemons/core/arbol_core/provider_models.py#fetch_claude_models`
- `arbol_deprecated_v1:daemons/core/arbol_core/provider_models.py#_filter_claude_entitled`
- `arbol_deprecated_v1:daemons/core/arbol_core/provider_models.py#fetch_codex_models`
- `arbol_deprecated_v1:daemons/core/arbol_core/provider_models.py#fetch_zai_models`
- `arbol_deprecated_v1:product-spec/05-intelligence-providers.md#Thinking level`

## SYL-92 verification, 7 October 2026

SYL-92 passed the complete 38-scenario shared registry for both Python Drivers. Codex also passed 128 unit methods, Ruff and strict mypy from source; its standalone CPython 3.14.8 development candidate passed the same units and all 38 scenarios, and its relocated copy passed metadata and unit checks under a minimal environment. A fresh packaged `dev probe` passed against codex-cli 0.159.2 with zero inference requests. The packaged build gate sent exactly one no-tools ready message through `test-chatgpt`; it completed and reported tokens and usage before/after. The extended five-turn `dev live-check` orchestration and refusal gates passed offline, but the extended vendor run was not requested. Contract and state format remain 1. The first numbered Codex Build is the separate SYL-94 task.

Current records and source/package provenance: `~/Artifacts/arbol-codex-driver/research/conformance-2026-10-07/verification.json`, `coverage-audit.json`, `packaged-probe.json` and `packaged-build-check.txt` in that folder. Dated migration and TypeScript evidence below remains historical; unobserved real vendor failures remain unobserved. The coverage audit retains every former Verified by cell before this update.

## Requirements

| ID | A Driver must… | Origin | Verified by |
|---|---|---|---|
| DRV-1.1 | have one Subscription per vendor family from the start, named after the family, with one of them as its default; let further ones be created, relabelled and removed through its commands | Changed | Claude Python: `C1`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C1`, `Accounts.test_local_concurrent_creation_update_preserves_owner_settings_and_remove_isolated` |
| DRV-1.2 | give every Subscription its own credential and apply it to its own runs only: the owner's own sign-in of the tool for `anthropic` and `chatgpt`, and for any other a token or a key in the environment of that run's child alone. Refuse to create a second Subscription of the ChatGPT family with `invalid_input`, except the test Subscription `test-chatgpt` (DRV-5), which alone keeps a home of its own | Changed | contract |
| DRV-1.3 | never return, log or emit a credential value. No operation exports one | Kept | Claude Python: `C7`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C7`, `C37`, `Accounts.test_unsigned_refusals_and_malformed_state_do_not_start_vendor_or_disclose_contents`, `EventPrivacy.test_every_event_and_text_output_scrubs_nested_private_values`, `EventPrivacy.test_split_values_and_open_suffixes_are_hidden_in_all_delta_streams` |
| DRV-1.4 | check a key when it reads it at sign-in and reject anything but printable ASCII without spaces, naming up to three offending characters | Kept | Claude Python: `C3`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C3` |
| DRV-1.5 | keep one pending sign-in per Subscription; a new one replaces it; an unfinished one ends after five minutes and leaves the Subscription `signed_out` | Kept | Claude Python: `C2`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C2`, `Accounts.test_login_replacement_cancels_pending_and_sign_out_clears_credentials` |
| DRV-1.6 | tell the caller which hosts a sign-in page may visit, so the caller's window can refuse all others | Kept | Claude Python: `C2`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C2` |
| DRV-1.7 | move a Subscription to `needs_attention`, with the reason and the remedy, as soon as the vendor rejects its credential in any operation or run | Changed | Claude Python: `C4`, `C28`; Codex Python: `C4`, `Accounts.test_usage_last_good_cache_rejection_and_catalog_fallback`, `ErrorRuns.test_rejected_retry_before_turn_start_reply_interrupts_accepted_turn`, `Foundation.test_catalog_pagination_fallback_usage_and_unknown_identifiers` |
| DRV-1.8 | never hold a copy of a credential that the vendor tool renews by itself | Changed | Claude Python: `C7`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C7`, `Accounts.test_login_replacement_cancels_pending_and_sign_out_clears_credentials` |
| DRV-1.10 | serialise sign-in, sign-out and removal of one Subscription across processes | Kept | Claude Python: `C38`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C38`, `Accounts.test_login_replacement_cancels_pending_and_sign_out_clears_credentials` |
| DRV-1.11 | refuse a run and a request for the model catalog for a Subscription that is not `signed_in`, with the error `not_signed_in`, before any vendor tool is started. `check` works in every state but `signed_out`, and `usage` answers a Subscription that is not signed in with the outcome `needs_sign_in` | Changed | Claude Python: `C4`, `C40`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C4`, `C40`, `Accounts.test_unsigned_refusals_and_malformed_state_do_not_start_vendor_or_disclose_contents` |
| DRV-1.12 | on sign-out remove the credential, the account details and the stored usage report. Sign-out and removal are refused while a run uses the Subscription, unless forced, in which case the runs are cancelled first | Changed | Claude Python: `C5`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C5`, `Accounts.test_login_replacement_cancels_pending_and_sign_out_clears_credentials` |
| DRV-1.13 | on removal delete the Subscription's Keychain item. Refuse to sign out or remove a Subscription that uses the owner's own sign-in of the tool, with `invalid_input` (DRV-D43) | New | contract |
| DRV-1.14 | answer `list` from stored state without contacting a vendor, and contact a vendor only in `check`, `usage`, `models` and sign-in | New | Claude Python: `C1`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C1` |
| DRV-1.15 | apply a partial update by changing only the fields given | Changed | Claude Python: `C1`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C1`, `Accounts.test_local_concurrent_creation_update_preserves_owner_settings_and_remove_isolated` |
| DRV-1.16 | fetch usage only when asked; never poll | Kept | Claude Python: `C41`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C41` |
| DRV-1.17 | report usage with one of the four outcomes; an unknown value is absent, never zero | Kept | Claude Python: `C41`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C41`, `Accounts.test_usage_last_good_cache_rejection_and_catalog_fallback`, `Foundation.test_catalog_pagination_fallback_usage_and_unknown_identifiers` |
| DRV-1.18 | store the last `ok` usage report with the Subscription and return it with the record | Kept | Claude Python: `C30`, `C41`; Codex Python: `C30`, `C41`, `RunUsageStorage.test_late_report_does_not_restore_account_or_overwrite_newer_usage` |
| DRV-1.19 | take a model catalog only from the Subscription's own vendor family and mark a built-in fallback as such | Kept | Claude Python: `C41`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C41`, `AppServerTests.test_private_home_configuration_clean_environment_and_owner_cleanup`, `Foundation.test_catalog_pagination_fallback_usage_and_unknown_identifiers` |
| DRV-1.20 | fetch a model catalog without spending inference quota | Changed | Claude Python: `C41`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C41`, `Foundation.test_catalog_pagination_fallback_usage_and_unknown_identifiers` |
| DRV-1.21 | report per model the effort levels the vendor tool accepts, in the vendor's own words, where the tool exposes them | Changed | Claude Python: `C41`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C41`, `Foundation.test_catalog_pagination_fallback_usage_and_unknown_identifiers` |
| DRV-1.22 | take account name, e-mail, organisation and plan only from the vendor and clear them at sign-out | Kept | Claude Python: `C41`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C41` |
| DRV-1.23 | print the new record as the result of every command that changes a Subscription | New | Claude Python: `C1`, `C32`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C1`, `C32` |
| DRV-1.24 | treat a Subscription recorded as `signing_in` whose `sign-in` command no longer runs as `signed_out` | New | Claude Python: `C6`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C6`, `Accounts.test_live_progress_dead_and_reused_owner_recovery` |
| DRV-1.25 | carry a sign-in attempt in one `sign-in` command: steps as lines on standard output, the code of an `enter_code` step as a line on standard input, and the attempt cancelled when the command is ended | New | Claude Python: `C2`, `C6`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C2`, `C6`, `Accounts.test_login_replacement_cancels_pending_and_sign_out_clears_credentials` |
| DRV-1.26 | read a key only from the source its settings file names for the Subscription. For the Keychain, which is the default: name the Subscription's item in the `store_secret` step, go on by itself once the item is filled, and remove from it a key that fails the check of DRV-1.4 or that the vendor rejects at sign-in. For a command: run it whenever the key is needed, keep what it prints nowhere, and fail the sign-in on a key that is refused | Changed | Claude Python: `C3`, `C32`, `test_runtime.StateTests`, `test_runtime.CompatibilityTests`; Codex Python: `C3`, `C32` |

DRV-1.9 had a Driver renew a credential. It was withdrawn on 6 October 2026: the vendor tools renew their own logins and a key is never renewed, so no family has a credential a Driver could renew. Its number is not used again.

## Interface

Types are given in TypeScript. Times are ISO 8601 strings in UTC.

```ts
interface Subscription {
  id: string;                       // a short name, unique within the Driver, stable
  family: string;                   // e.g. "anthropic", "zai", "chatgpt"
  label: string;
  auth: "vendor_login" | "key";
  state: "signed_out" | "signing_in" | "signed_in" | "needs_attention";
  account?: { name?: string; email?: string; organization?: string; plan?: string };
  problem?: DriverError;            // present exactly when state is "needs_attention"
  settings: Record<string, unknown>;   // family-specific, never a secret; as read from the settings file (DRV-0)
  lastUsage?: UsageReport;          // the last report with outcome "ok"
  createdAt: string;
  updatedAt: string;
  checkedAt?: string;               // last time the vendor confirmed or rejected the credential
}

interface Family {
  id: string;
  label: string;
  auth: "vendor_login" | "key";
  settings: object;                 // JSON Schema of the family's settings, with defaults
}

type SignIn =
  | { step: "open_url"; url: string; allowedHosts: string[]; userCode?: string; expiresAt: string }
  | { step: "enter_code"; prompt: string; expiresAt: string }
  | { step: "store_secret"; prompt: string; keychain: { service: string; account: string }; expiresAt: string }
  | { step: "done"; subscription: Subscription }
  | { step: "failed"; error: DriverError };

interface UsageReport {
  outcome: "ok" | "needs_sign_in" | "unavailable" | "unsupported";
  message?: string;                 // present unless outcome is "ok"
  fetchedAt: string;
  plan?: string;
  windows: Array<{
    kind: "session" | "weekly" | "other";
    label: string;
    usedPercent?: number;           // 0 to 100
    resetsAt?: string;
    windowMinutes?: number;
    limitReached?: boolean;
  }>;
  detailsUrl?: string;              // the vendor's own usage page
  extra?: Record<string, unknown>;  // family-specific, e.g. totals per model
}

interface ModelCatalog {
  source: "vendor" | "tool" | "builtin";   // "tool": reported by the vendor tool
  fetchedAt: string;
  models: Array<{
    id: string;                     // the value passed back in an inference request
    label: string;
    description?: string;
    efforts?: string[];             // accepted effort levels, vendor's wording
    serviceTiers?: string[];        // the tiers the model can run at, where the vendor tool lists any
    defaultEffort?: string;
    isDefault?: boolean;
  }>;
}
```

The commands, under the rules of the command line in [DRV-0](00-overview-and-boundary.md#the-command-line):

| Command | Options and input | Result on standard output | Contacts the vendor |
|---|---|---|---|
| `subscriptions families` | none | `Family[]` | No |
| `subscriptions list` | none | `Subscription[]` | No |
| `subscriptions create` | `--family <family>`, `--label <text>`, optionally `--id <name>` | `Subscription` in state `signed_out` | No |
| `subscriptions update <id>` | `--label <text>` | `Subscription` | No |
| `subscriptions remove <id>` | `--force` | nothing | No |
| `subscriptions sign-in <id>` | The code of an `enter_code` step, as one line on standard input: `{ "input": string }`. Never a secret. With the option `--by-code` the sign-in uses a code typed on another device, where the family has such a sign-in | One `SignIn` step per line; the last is `done` or `failed` | Yes |
| `subscriptions sign-out <id>` | `--force` | `Subscription` | Where the vendor tool offers a sign-out |
| `subscriptions check <id>` | none | `Subscription` | Yes, without inference |
| `subscriptions usage <id>` | none | `UsageReport` | Yes |
| `subscriptions models <id>` | none | `ModelCatalog` | Yes, or the vendor tool |

A sign-in is cancelled by ending its command; there is no command to continue or cancel one from another invocation.

Errors, from the list in DRV-4: `not_found`, `invalid_input`, `not_signed_in`, `credential_rejected`, `in_use`, `vendor_unavailable`, `tool_missing`, `tool_unsupported`, `unsupported`.

## Known problems in version 1

Not to be reproduced.

- **A signed-out account still ran.** The Claude route started the vendor tool without a token and the tool used whatever login its profile folder held. The Codex route never received a credential at all, so the state shown in Arbol and the account doing the work could differ.
- **The state lied after a rejection.** A rejected credential failed the turn and left the account marked as logged in.
- **A rotating credential was copied.** The ChatGPT credential was imported from the vendor tool's file. The tool then rotated its renewal token, and Arbol's own renewal request failed from then on.
- **Vendor interfaces were imitated.** The Anthropic sign-in used the vendor tool's public client identifier and its user-agent text; the ChatGPT model list and usage readings imitated the vendor tool's headers and version. Each broke when the vendor changed something.
- **Listing models spent quota.** Every fetch of the Anthropic catalog sent one real request per listed model.
- **A partial update erased settings.** The command-line client documented that omitted options keep their value; the receiving side reset several of them.
- **One account per vendor.** A second account of a vendor could not be configured.

Historical evidence (frozen version 1; ordinary locators, not Source Refs):

- `arbol_deprecated_v1:product-spec/05-intelligence-providers.md#Known problems and lessons`
- `arbol_deprecated_v1:product-spec/05-intelligence-providers.md#Can two accounts of one vendor run at the same time, isolated?`
- `arbol_deprecated_v1:daemons/shared/arbol_shared/subscription_oauth.py`
- `arbol_deprecated_v1:daemons/core/arbol_core/provider_models.py#_arbol_fetch_codex_models_payload`
- `arbol_deprecated_v1:daemons/core/arbol_core/universe_usage.py#build_headers`

## Python migration verification, 7 October 2026

SYL-95 verification is recorded in the requirement-level `~/Artifacts/arbol/driver-contract/python-migration-coverage-2026-10-07.json` and the Driver records `research/python-migration-2026-10-07/verification.json`. Python check names identify the copied standard-library unittest suites and the unchanged shared scenarios. Prior Driver unit/probe/live names refer to historical TypeScript evidence; unchanged shared build-tool and runner names remain active. Claude passes the complete 38-scenario suite; Codex passes its five original scoped groups (29 scenario invocations, with the same exclusions), and remains a development candidate. No historical live result is treated as fresh Python evidence, and previously unobserved vendor failures stay unobserved.

## Decisions

| ID | Question | Proposed default | Outcome |
|---|---|---|---|
| DRV-D43 | `anthropic` and `chatgpt` use the owner's own sign-in of the tool (DRV-D42). What do sign-out and removal do to them? | Both are refused with `invalid_input`, and the message says to sign out in the tool itself. Signing out would sign out every session of that tool on the Mac, the owner's own included. `sign-in` stays: it runs the tool's own sign-in in its default home, which is what the owner would do by hand. `check` reports what the tool says about its sign-in | Open: technical consequence of DRV-D42, proposed 19 October 2026 |
| DRV-D6 | Does version 1's "Open in VS Code" for an account belong to a Driver? | No. It would need an operation that hands out a credential, which DRV-1.3 forbids. If wanted later, the caller can start an editor with the Subscription's home in its environment | Decided 6 October 2026 by the owner: no (SYL-39) |
| DRV-D7 | How many Subscriptions per family must work in the first release? | The design allows any number. The first release is accepted with one per family; two accounts of one family running at once is a `live` check that may follow | Decided 6 October 2026 by the owner: further accounts of a family stay possible. One per family is enough for the first release |
| DRV-D8 | Should per-run token and cost records be kept by the Driver? | No. A run reports its usage in its final event (DRV-2) and the caller keeps the history | Decided 6 October 2026 by the owner: the proposed default (SYL-40) |
| DRV-D37 | How do the local Subscription commands choose identifiers and dates? | Identifiers use the safe file-name form of DRV-6: 1 to 128 ASCII letters, digits, underscores, dots or hyphens, starting with a letter or digit. An automatic identifier takes the first available family-number name, starting at 2, and is reserved while its record is written under its own lock. The implicit family records use the creation time of the state format file for their dates until their first change. A partial update with no fields returns the unchanged record | Decided 6 October 2026 during SYL-78, a technical choice |
| DRV-D21 | What does a caller type to name a Subscription on the command line? | Its identifier, which is a short readable name. The Subscription a Driver has from the start is named after its family (`anthropic`, `zai`, `chatgpt`). A further one gets the name given with `--id`, otherwise the family's name with a number (`anthropic-2`). It never changes; the label can | Decided 6 October 2026, together with the Subscriptions a Driver has from the start (DRV-D24) |
