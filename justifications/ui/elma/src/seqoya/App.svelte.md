---
role: authored
---
# Justifications

## <end>

Reason: Sync the published design snapshot and connect tab selection to the existing account reader. Load the account list when the first Subscriptions tab connects or is reselected, preserve refresh and reconnection behavior, and reuse the existing vendor and activity reads. Verify types and snapshot provenance. Serves BKD-3.17.

Origins: BKD-3.17 · Intention i-5b2335a8 · 2026-11-12

## script

Reason: Sync the published design snapshot. Apply the fixed label catalog to each returned account in the Seqoya adapter, by exact Driver and vendor family. Include the six default classifications and GPT-6-Astra from the specification. Retain account and usage data, keep Codex distinct from Pi's ChatGPT, and preserve the current connection and refresh paths. Serves BKD-3.17.

Origins: BKD-3.17 · Intention i-5f439d61 · 2026-11-12

