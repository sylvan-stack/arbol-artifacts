---
role: authored
---
<!-- mycel:cues
type: literal
match: ["refresh Seqoya usage"]
-->

# Refresh Seqoya usage from Arbol Browser

Use this procedure when the owner requests a dashboard usage refresh for Seqoya Lab. It uses the owner-operated Arbol Browser preview and the installed Seqoya evidence format. The operation runs when requested.

## Inputs

- The Seqoya Subscriptions to refresh, identified by Driver and current Subscription ID.
- The owner-confirmed Browser profile ID and provider usage page for each Subscription. Keep native Codex and Pi/ChatGPT separate, even when their dashboards share a hostname.

## Procedure

1. **Match the account.** Refresh the Seqoya catalogue and confirm the selected Subscription is active. Follow the Browser Operational Artifact to locate the running preview. Use `profiles`, `tabs`, and `status` to select and verify the existing profile and tab. Match the signed-in account in that profile to the Subscription. If the match is ambiguous, stop that Subscription and ask the owner. A display name alone is insufficient. [Work with Arbol Browser](/Users/msix/Artifacts/arbol-browser/operations/work-with-arbol-browser.md)
2. **Read the usage page.** Use the existing dashboard tab in the verified profile, or navigate an available tab in that profile with `go URL`. Use `status` to confirm the profile and destination after redirects. Use a focused `inspect` selector for the allowance or credit section. Capture the observation time, period, used or remaining value and unit, reset, expiry, and available resets where shown. For rounded countdowns, mark the derived reset approximate. Keep numbers and dates only in the evidence from the site.
3. **Update the affected evidence only.** For Claude, Pi/ChatGPT, and MiMo, use the typed records below. This file has one slot per dashboard source today. If a slot already belongs to a different Subscription, preserve it and report the conflict. Keep a private backup, preserve the other readings and calibrations, and check that the Subscription and evidence file have stayed current. Write validated JSON to a temporary file with mode `0600` in the same directory, then atomically replace `~/.arbol/seqoya-usage-evidence.json`. For Codex, Kimi, z.ai, and DeepSeek, use the existing Seqoya refresh to fetch the Driver report and use dashboard numbers for comparison. [Seqoya evidence format](/Users/msix/repos/sylvan-stack/arbol-app/Sources/SeqoyaUsageEvidence.swift) · [Seqoya usage behavior](/Users/msix/Artifacts/arbol/backend/03-the-arbol-swift-app.md:155)
4. **Verify the card.** Refresh **Intelligence Providers → Subscriptions** and check the intended card. It should reflect the accepted reading or a newer valid Driver report. Restore the Browser’s previous visibility, leave the owner’s tabs open, and report which Subscriptions updated, which kept newer Driver data, and which could not be refreshed. [Work with Arbol Browser](/Users/msix/Artifacts/arbol-browser/operations/work-with-arbol-browser.md#5-hand-off-the-page-and-finish)

## Evidence records

Each record uses the current local `subscription` ID and an ISO 8601 `observedAt`. Use the exact catalogue timestamps and a verified plan where required. In allowance windows, use `remainingPercent` and `resetsAt`. If the dashboard reports percent used, subtract it from 100.

| Record | Binding fields | Dashboard values |
| --- | --- | --- |
| `claudeDashboard` | `createdAt`, `checkedAt` | Plan, five-hour and weekly windows, available reset expiries when shown |
| `piChatGPT` | `updatedAt` | Set `browser` to true. Record the verified plan, access state, app cap, and shared five-hour and weekly windows when shown |
| `mimo` | `updatedAt` | Set `browser` to true. Record the reset and decimal strings for total and remaining credits. Subtract used credits from total when the dashboard shows used credits |

## Stop conditions

Preserve the prior reading and report the issue if the selected profile or account cannot be verified, the page requires sign-in, the numbers are missing or ambiguous, or the Subscription changes during the operation. For sign-in, use the private handoff in the Browser procedure. Continue with the other verified Subscriptions.

## Automatic refresh in Seqoya

When the Subscriptions tab opens, Seqoya can execute this operation locally against the running Arbol Browser preview. It uses the documented preview controller and the current format-1 Driver records. One refresh can run at a time. A recent successful reading can be reused for two minutes.

The Arbol Swift App also schedules this operation while the Seqoya Lab window is closed. The first run follows backend readiness, then refreshes run every five minutes while the App is running. After sleep, run one overdue refresh. Scheduled runs require a running, hidden preview and normal installation state. A visible preview or a pending manual handoff defers the run. Scheduled and on-open refresh share the same reader and saved evidence. [BKD-3.20](../backend/03-the-arbol-swift-app.md#requirements)

Use the owner-confirmed mapping from Driver and Subscription ID to the exact named preview profile. Check the current Subscription creation time, the physical profile directory and the verified Browser tab and dashboard before saving. Keep the separate ChatGPT profiles and check their expected plans. When any target fails, preserve that Subscription's last valid reading and report its issue on the card. A Browser session that needs sign-in stays with the owner. Preserve open drafts and restore the previous tab selection and visibility.

Use the existing typed evidence for Claude, Pi/ChatGPT and MiMo. Store Codex, Kimi and z.ai quota windows and the DeepSeek API balance as bounded, dated Browser readings. Prefer verified current Browser readings while keeping the existing Driver path available for other readings. Keep approximate times marked. This operation only reads provider dashboards and preserves Driver credentials and the installation schema.

For MiniMax, use the owner-confirmed `pi/minimax` profile and the [Plan Usage dashboard](https://platform.minimax.io/console/usage). Save the plan status, credit balance, and LLM usage and cache-hit percentage with their selected period in the bound Browser report. Unreported plan windows stay absent. The MiniMax card shows the reported figures and observation time.
