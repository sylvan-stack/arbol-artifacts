---
role: authored
---
# Hermes Agent upstream source snapshot · 27 October 2026

This is a source-evidence snapshot for [the Driver investigation](hermes-agent-driver.md),
not a runtime probe or a claim of support. Excerpts are copied from the public
[NousResearch/hermes-agent repository](https://github.com/NousResearch/hermes-agent)
at commit [`b63fbbac4d27d1e4b8585ff7065e6dceb6207394`](https://github.com/NousResearch/hermes-agent/commit/b63fbbac4d27d1e4b8585ff7065e6dceb6207394),
committed 27 October 2026 at 19:35:50 UTC. The latest GitHub release returned at
capture was [v0.22.5](https://github.com/NousResearch/hermes-agent/releases/tag/v0.22.5),
published 23 October 2026, commit `bf0203a794a07aac3ff764972ab9087baa4e4f4e`. Main and the release are different
source baselines; no installed version was qualified.

Each entry names the immutable upstream file and exact source lines. SHA-256
covers the complete source file, not just the excerpt. These excerpts preserve
the evidence used by this investigation; they are not a complete repository mirror.
The live documentation's three-interface overview is orientation; executable
construction and ownership code decide the findings when the descriptions differ.


## H01 Integration surfaces

File: [`website/docs/developer-guide/programmatic-integration.md`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/website/docs/developer-guide/programmatic-integration.md).

SHA-256: `41f2454c8ca1c46dbd04dba6f8ea54d53c7913a1b6c8ad17235bb340cc17fb7f`.


[Lines 9–17](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/website/docs/developer-guide/programmatic-integration.md#L9-L17):

~~~~text
Hermes ships three protocols for driving the agent from external programs — IDE plugins, custom UIs, CI pipelines, embedded sub-agents. Pick the one that matches your transport and consumer.

| Protocol | Transport | Best for | Defined by |
|----------|-----------|----------|------------|
| **ACP** | JSON-RPC over stdio | IDE clients (VS Code, Zed, JetBrains) that already speak the [Agent Client Protocol](https://github.com/zed-industries/agent-client-protocol) | `acp_adapter/` |
| **TUI gateway** | JSON-RPC over stdio (or WebSocket) | Custom hosts that want fine-grained control of sessions, slash commands, approvals, and streaming events | `tui_gateway/server.py` |
| **API server** | HTTP + Server-Sent Events | OpenAI-compatible frontends (Open WebUI, LobeChat, LibreChat…) and language-agnostic web clients | `gateway/platforms/api_server.py` |

All three drive the same `AIAgent` core. They differ only in wire format and which set of features they expose.
~~~~


[Lines 23–32](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/website/docs/developer-guide/programmatic-integration.md#L23-L32):

~~~~text
`hermes acp` starts a stdio JSON-RPC server speaking ACP. Used in production by VS Code (Zed Industries' ACP extension), Zed, and any JetBrains IDE with an ACP plugin.

Capabilities exposed: session creation, prompt submission, streaming agent message chunks, tool-call events, permission requests, session fork, cancel, and authentication. Tool output is rendered into ACP `Diff`/`ToolCall` content blocks the IDE understands.

Full lifecycle, event bridge, and approval flow: [ACP Internals](./acp-internals).

```bash
hermes acp                  # serve ACP on stdio
hermes acp --check          # verify ACP dependencies and adapter imports
hermes acp --setup          # interactive provider/model setup for ACP terminal auth
~~~~


## H02 ACP dispatch to a gateway

File: [`acp_adapter/server.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/acp_adapter/server.py).

SHA-256: `d1118e723b5197300ae192420e4ba2b552ecde0eb6370e80527a834e6b786e62`.


[Lines 247–258](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/acp_adapter/server.py#L247-L258):

~~~~python
            from acp_adapter.gateway_server import GatewayACPAgent
            return GatewayACPAgent()
        return super().__new__(cls)

    def __init__(self, session_manager: SessionManager | None = None):
        super().__init__()
        self.session_manager = session_manager or SessionManager()
        self._conn: Optional[acp.Client] = None

    # ---- Connection lifecycle -----------------------------------------------

    def on_connect(self, conn: acp.Client) -> None:
~~~~


## H03 ACP viewer lifetime

File: [`acp_adapter/entry.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/acp_adapter/entry.py).

SHA-256: `77ea948af74acff2b0b20192477080be7d56ff4072378c20745506169e167ba0`.


[Lines 204–216](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/acp_adapter/entry.py#L204-L216):

~~~~python
    async def serve():
        # MCP and execution belong to the daemon. Close only this viewer, while
        # its event loop is still alive, including on protocol/transport errors.
        try:
            await acp.run_agent(agent, use_unstable_protocol=True)
        finally:
            await agent.aclose()

    try:
        asyncio.run(serve())
    except KeyboardInterrupt:
        logger.info("Shutting down (KeyboardInterrupt)")
    except Exception:
~~~~


[Lines 222–229](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/acp_adapter/entry.py#L222-L229):

~~~~python


if __name__ == "__main__":
    main()
~~~~


## H04 Automatic gateway startup

File: [`hermes_cli/gateway_client.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/hermes_cli/gateway_client.py).

SHA-256: `530c563e6a19f0a79a4d74157afd1d6e7d893b125226a32179e17c15f9804cbd`.


[Lines 270–278](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/hermes_cli/gateway_client.py#L270-L278):

~~~~python
async def connect_gateway(endpoint=None, subject=None, *, max_size=8 * 1024 * 1024):
    """Attach to this home's owner. ``endpoint``: an already-discovered ready owner to dial as-is
    (maintenance that must never start a gateway); default ensures one, starting it if needed.
    ``subject``: mint the ticket for this principal (the caller's authenticated dashboard user)
    rather than the socket identity; only a peer the owner already trusts may name one.
    ``max_size``: the largest frame accepted; a ``session.resume`` answer carries the whole history."""
    from websockets.asyncio.client import connect
    from hermes_constants import get_hermes_home
    from hermes_cli.gateway_runtime import attachable, ensure_gateway_runtime, gateway_profile_home
~~~~


[Lines 293–307](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/hermes_cli/gateway_client.py#L293-L307):

~~~~python
        # A per-task overlay home is served by the profile its symlinked lock names (#138949).
        home = gateway_profile_home(get_hermes_home())
        # A client's own start: the daemon it may launch ends itself once idle (no client, adapter,
        # cron/kanban work or admission), and the next client starts a fresh one.
        result = await asyncio.to_thread(ensure_gateway_runtime, home, idle_exit=True)
        if not attachable(result):
            detail = getattr(result, "detail", None)
            if result.reason_code == "runtime_exited" and detail:
                # A multi-line startup report (redacted traceback tail + where the full log is).
                raise GatewayUnavailableError(f"Gateway could not start: {detail}", result.state)
            detail = f" ({detail})" if detail else ""
            raise GatewayUnavailableError(f"Gateway {result.state}: {result.reason_code or 'not_ready'}{detail}",
                                          result.state)
        endpoint = result.endpoint
        ticket = await asyncio.to_thread(_session_ticket, home, endpoint)
~~~~


## H05 Standalone home ownership

File: [`tui_gateway/entry.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/entry.py).

SHA-256: `e58c125e3b5d7b2cfd310cd9d63f77590baa170cba2eb7ce589eb7e7e82b5736`.


[Lines 273–287](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/entry.py#L273-L287):

~~~~python
def _claim_launch_home():
    """Reserve the launch home exactly as the gateway does, or None when it is already owned.

    No product surface launches this standalone stdio server any more: Ink and Desktop attach to
    the profile's gateway over WS (``ui-tui/scripts/gateway_bootstrap.py``). Dev harnesses still
    run it against a sandbox home (``apps/desktop/e2e/real-session-builder.ts``), and it opens that
    home's ``state.db`` as a writer, so it must be the home's only owner: the gateway's
    ``gateway.lock`` reservation refuses it beside a live gateway (or a second entry), and holding
    that lock keeps a gateway from starting on the home while this process writes."""
    from gateway.runtime_ownership import OwnershipConflict, process_ownership
    home = server._launch_home()
    try:
        process_ownership.reserve([home])
    except OwnershipConflict:
        return None
~~~~


[Lines 291–301](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/entry.py#L291-L301):

~~~~python
def main():
    home = _claim_launch_home()
    if home is None:
        _log_exit(f"refused: {server._launch_home()} is owned by a running gateway; attach to it instead")
        sys.exit(1)
    try:
        _serve()
    finally:
        from gateway.runtime_ownership import process_ownership
        process_ownership.release(home)

~~~~


## H06 Canonical store ownership

File: [`website/docs/developer-guide/session-storage.md`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/website/docs/developer-guide/session-storage.md).

SHA-256: `1149f4d2c43aaebd15dbd1cbfa8f4df318b9256e1d96393f44e86357519f5929`.


[Lines 3–13](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/website/docs/developer-guide/session-storage.md#L3-L13):

~~~~text
Hermes Agent uses a SQLite database (`~/.hermes/state.db`) to persist session
metadata, full message history, and model configuration across CLI and gateway
sessions. This replaces the earlier per-session JSONL file approach.

The profile's gateway is the **only writer of canonical sessions**: `hermes chat`,
the TUI, Desktop (local), the API server, ACP, cron, Bot Chat and Kanban workers are
clients that admit input to its session authority over `/api/ws` (see
[Gateway local sessions](./gateway-local-sessions.md)). Out-of-process managed
workers write through that owner (`RuntimeSessionStore` RPC), never by opening
`state.db` for transcript writes themselves.

~~~~


[Lines 17–28](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/website/docs/developer-guide/session-storage.md#L17-L28):

~~~~text

`get_hermes_home()` is the authoritative filesystem resolver for state and
configuration. It uses a context-local override first, then the `HERMES_HOME`
environment variable, and finally the platform default (`~/.hermes` on macOS
and Linux; `%LOCALAPPDATA%/hermes` on Windows). Consequently, the default
database is always `get_hermes_home() / "state.db"`, not a path that callers
should hard-code as `~/.hermes/state.db`.

Named profiles are isolated directories: a profile named `coder`, for example,
uses `<default Hermes root>/profiles/coder/` and therefore has its own
`state.db`, configuration, logs, and other profile-scoped state. A process that
creates a database, reads configuration, or starts a child process for a
~~~~


## H07 Session create overrides

File: [`tui_gateway/contracts/sessions.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/sessions.py).

SHA-256: `e7974045b07d5a0094229026c5945d75771055de6ebe6e336dcbc218ae912ff6`.


[Lines 118–132](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/sessions.py#L118-L132):

~~~~python
class SessionCreateParams(ProfileParams):
    cols: int | None = None
    source: str | None = None
    cwd: str | None = None
    # #52589: provenance for ``cwd`` — true only for a deliberate workspace pick;
    # an inherited app-global workspace must yield to a named profile's terminal.cwd.
    cwd_explicit: bool | None = None
    messages: list[SeedMessage] | None = None
    parent_session_id: str | None = None
    title: str | None = None
    model: str | None = None
    provider: str | None = None
    reasoning_effort: str | None = None
    fast: bool | None = None  # presence is the contract: omitted inherits, true pins priority, false pins normal
    service_tier: str | None = None
~~~~


[Lines 133–139](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/sessions.py#L133-L139):

~~~~python
    close_on_disconnect: bool = False
    hidden: bool = False
    room_plumbing: bool = False
    follow_profile_config: bool = False
    # #65410: stable caller-chosen key so a retried create (response lost in
    # transit) returns the SAME session instead of a duplicate child.
    idempotency_key: str | None = None
~~~~


## H08 Seed history coercion

File: [`tui_gateway/session_history.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/session_history.py).

SHA-256: `6abd9fe71a07e53d4c461558afe5ecd54a1b1b9f7107b115a1db0080ababf241`.


[Lines 373–386](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/session_history.py#L373-L386):

~~~~python
def _coerce_seed_history(value: Any) -> list[dict]:
    history = []
    for item in value if isinstance(value, list) else ():
        if not isinstance(item, dict) or item.get("role") not in ("user", "assistant", "system"):
            continue
        content = item.get("text") if item.get("content") is None else item.get("content")
        if isinstance(content, str) and content.strip():
            row = {"role": item["role"], "content": content}
            # "hidden" is the one display_kind a seeding client may author: model-facing scaffolding the
            # renderer must not paint (a guided-chat runbook). Every other kind is stamped by the gateway
            # at turn time, so it is not accepted from the wire.
            if item.get("display_kind") == "hidden":
                row["display_kind"] = "hidden"
            history.append(row)
~~~~


## H09 Seed message wire

File: [`tui_gateway/contracts/sessions.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/sessions.py).

SHA-256: `e7974045b07d5a0094229026c5945d75771055de6ebe6e336dcbc218ae912ff6`.


[Lines 104–116](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/sessions.py#L104-L116):

~~~~python
class SeedMessage(Params):
    """One create-time transcript row (``session_history._coerce_seed_history``); ``text`` is the
    legacy alias of ``content``; only ``display_kind: "hidden"`` is accepted from the wire. Clients
    forward stored rows verbatim (``_row_id``, ``timestamp``, …) and the coercer drops what it does
    not use, so the row stays open."""

    model_config = Params.model_config | {"extra": "allow"}

    role: str
    content: str | None = None
    text: str | None = None
    display_kind: str | None = None

~~~~


## H10 Foreign import scope

File: [`hermes_cli/foreign_sessions.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/hermes_cli/foreign_sessions.py).

SHA-256: `c69003a9c0814bb41b1771786a0d745b0f0b2b6ccaafe325386c3172568e8393`.


[Lines 109–115](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/hermes_cli/foreign_sessions.py#L109-L115):

~~~~python
def _message_turn(message: Any) -> Optional[tuple[str, str]]:
    """Normalize one message dict into a ``(role, text)`` turn, or None when it is not importable."""
    role = message.get("role") if isinstance(message, dict) else None
    if role not in ("user", "assistant"):
        return None
    text = _flatten_blocks(message.get("content"))
    return None if not text or (role == "user" and _WRAPPER_TAG_RE.match(text.lstrip())) else (role, text)
~~~~


[Lines 232–246](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/hermes_cli/foreign_sessions.py#L232-L246):

~~~~python
def import_foreign_session(source: str, path) -> str:
    """Import one foreign session through the gateway's ``session.mutate import`` (the gateway is the
    only state.db writer, #106742); returns the new Hermes session id. The row lands as an ordinary
    ``cli`` session bound to this importer, so ``hermes --resume`` continues it writable.

    Raises ``ValueError`` on unknown source or a session with no usable conversation turns, and
    ``GatewayClientError`` (a ``ValueError``) when the gateway refuses the import."""
    source = (source or "").strip().lower().lstrip("@")
    if source not in _SOURCE_LABELS:
        raise ValueError(f"Unknown foreign session source: {source!r}")
    path = Path(path).expanduser()
    if not path.is_file():
        raise ValueError(f"Session file not found: {path}")
    parsed = _parser(source)(path)
    turns = parsed["turns"]
~~~~


[Lines 247–248](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/hermes_cli/foreign_sessions.py#L247-L248):

~~~~python
    if not turns:
        raise ValueError(f"No user/assistant conversation turns found in {path}")
~~~~


[Lines 252–263](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/hermes_cli/foreign_sessions.py#L252-L263):

~~~~python
    from hermes_cli.gateway_client import GatewayClientError
    from hermes_cli.gateway_session_store import session_store
    store = session_store()
    session_id = new_session_id()
    cwd = parsed.get("cwd")
    # Resume refuses a folder missing here (another machine's, or deleted), as the Desktop import does.
    row = {"id": session_id, "source": "cli", "cwd": cwd if cwd and Path(cwd).is_dir() else None, "messages": turns}
    receipt = store.call("session.mutate", session_id=session_id, request_id=uuid.uuid4().hex, expected_revision=0,
                         operation="import", payload={"sessions": [row]})
    # Titles are UNIQUE (a re-import's is taken), so the title is a separate, cosmetic rename.
    with contextlib.suppress(GatewayClientError):
        store.call("session.mutate", session_id=session_id, request_id=uuid.uuid4().hex,
~~~~


## H11 Rich import authority

File: [`gateway/session_mutations.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/gateway/session_mutations.py).

SHA-256: `4ab780142434aeab660db4809042980181c86bff0cc54ab6793854c5988738fa`.


[Lines 26–37](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/gateway/session_mutations.py#L26-L37):

~~~~python
def _authorize_import(authority, actor, ref, params):
    """Import authorization; returns the imported session ids the write must claim."""
    if actor.profile_id != authority.profile_id or ref.profile_id != authority.profile_id:
        raise RuntimeStoreError('profile_mismatch')
    if 'session:create' not in actor.capabilities:
        raise RuntimeStoreError('permission_denied')
    from hermes_state_mutations import validate_action
    validate_action('import', params['payload'])
    normalized, errors = authority.db._validate_import_payload(params['payload']['sessions'])
    if errors:
        raise RuntimeStoreError('invalid_params')
    return tuple(item['session']['id'] for item in normalized)
~~~~


## H12 Rich import fields

File: [`hermes_state_portability.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/hermes_state_portability.py).

SHA-256: `3eca72538fae87b2fccac6fd3be8f44654d4a589184cd7d9664fbd63141fa001`.


[Lines 31–42](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/hermes_state_portability.py#L31-L42):

~~~~python
_IMPORT_SESSION_TEXT_FIELDS = (
    "source", "user_id", "model", "system_prompt", "end_reason", "cwd", "git_branch", "git_repo_root",
    "billing_provider", "billing_base_url", "billing_mode", "cost_status", "cost_source", "pricing_version", "title",
)
# ``role`` is validated separately (non-empty string).
_IMPORT_MESSAGE_TEXT_FIELDS = (
    "tool_call_id", "tool_name", "effect_disposition", "finish_reason",
    "reasoning", "reasoning_content", "platform_message_id", "message_id",
)
_IMPORT_MESSAGE_JSON_FIELDS = (
    "reasoning_details", "codex_reasoning_items", "codex_message_items", "absorbed_message_uids", "tool_call_uids",
)
~~~~


[Lines 574–588](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/hermes_state_portability.py#L574-L588):

~~~~python
    def _normalize_import_message(self, message: dict[str, Any], message_index: int) -> dict[str, Any]:
        """Type-check one payload message; raises ValueError naming the offending field."""
        clean_message = dict(message)
        role = clean_message.get("role")
        if not isinstance(role, str) or not role:
            raise ValueError(f"messages[{message_index}].role must be a non-empty string")
        for field in _IMPORT_MESSAGE_TEXT_FIELDS:
            clean_message[field] = self._import_text_or_none(clean_message.get(field), field)
        token_count = self._import_int_or_none(clean_message.get("token_count"), "token_count")
        if token_count is not None and not (self._SQLITE_INT_MIN <= token_count <= self._SQLITE_INT_MAX):
            raise ValueError("token_count is outside SQLite's integer range")
        clean_message["token_count"] = token_count
        message_path = f"session.messages[{message_index}]"
        timestamp = clean_message.get("timestamp")
        if timestamp is not None and coerce_epoch(timestamp, field="messages[].timestamp") is None:
~~~~


[Lines 589–590](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/hermes_state_portability.py#L589-L590):

~~~~python
            raise ValueError(f"{message_path}.timestamp must be a supported Unix timestamp")
        self._validate_import_message_content(clean_message.get("content"), message_path)
~~~~


[Lines 610–620](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/hermes_state_portability.py#L610-L620):

~~~~python
    def _validate_import_message_content(cls, content: Any, message_path: str) -> None:
        """Scalar message content must be bindable and later serializable."""
        if isinstance(content, int) and not isinstance(content, bool) and not (
                cls._SQLITE_INT_MIN <= content <= cls._SQLITE_INT_MAX):
            # SQLite can't bind a wider int: this reached INSERT and raised OverflowError.
            raise ValueError(f"{message_path}.content is outside SQLite's integer range")
        if isinstance(content, float) and not math.isfinite(content):
            raise ValueError(f"non-finite number at {message_path}.content")
        if isinstance(content, (bytes, bytearray)):
            raise ValueError(f"{message_path}.content must be a string, list, object, finite number, or null")

~~~~


## H13 Agent construction controls

File: [`run_agent.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/run_agent.py).

SHA-256: `05b9bf47d71dd54b67d905fca20c329260b0447a21ab12227afe37653bfac4ff`.


[Lines 243–255](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/run_agent.py#L243-L255):

~~~~python
        enabled_toolsets: list[str] | None = None, disabled_toolsets: list[str] | None = None,
        save_trajectories: bool = False, verbose_logging: bool = False, quiet_mode: bool = False,
        tool_progress_mode: str = "all", ephemeral_system_prompt: str | None = None,
        log_prefix_chars: int = 100, log_prefix: str = "",
        providers_allowed: list[str] | None = None, providers_ignored: list[str] | None = None, providers_order: list[str] | None = None,
        provider_sort: str | None = None, provider_require_parameters: bool = False, provider_data_collection: str | None = None,
        openrouter_min_coding_score: Optional[float] = None,
        session_id: str | None = None,
        tool_progress_callback: Callable[..., Any] | None = None, tool_start_callback: Callable[..., Any] | None = None,
        tool_complete_callback: Callable[..., Any] | None = None, thinking_callback: Callable[..., Any] | None = None,
        reasoning_callback: Callable[..., Any] | None = None, clarify_callback: Callable[..., Any] | None = None,
        read_terminal_callback: Callable[..., Any] | None = None, read_preview_callback: Callable[..., Any] | None = None,
        drive_preview_callback: Callable[..., Any] | None = None, read_window_below_callback: Callable[..., Any] | None = None,
~~~~


[Lines 263–277](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/run_agent.py#L263-L277):

~~~~python
        event_callback: Optional[Callable[[str, dict], None]] = None,
        reaction_callback: Optional[Callable[[str], None]] = None,
        max_tokens: int | None = None, reasoning_config: dict[str, Any] | None = None, service_tier: str | None = None,
        request_overrides: dict[str, Any] | None = None, prefill_messages: list[dict[str, Any]] | None = None,
        platform: str | None = None, user_id: str | None = None, user_id_alt: str | None = None, user_name: str | None = None,
        chat_id: str | None = None, chat_name: str | None = None, chat_type: str | None = None, thread_id: str | None = None,
        gateway_session_key: str | None = None,
        skip_context_files: bool = False, load_soul_identity: bool = False,
        skip_memory: bool = False, skip_background_review: bool = False,
        session_db=None, parent_session_id: str | None = None,
        iteration_budget: IterationBudget = None, run_budget_seconds: Optional[float] = None,
        fallback_model: dict[str, Any] | None = None, credential_pool=None,
        checkpoints_enabled: bool = False, checkpoint_max_snapshots: int = 20,
        checkpoint_max_total_size_mb: int = 500, checkpoint_max_file_size_mb: int = 10,
        pass_session_id: bool = False, requested_provider: str | None = None,
~~~~


[Lines 278–280](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/run_agent.py#L278-L280):

~~~~python
        capabilities: dict[str, bool] | None = None, cwd: str | None = None,
        side_agent: bool = False, memory_manager=None,
        tool_result_metadata_callback: Optional[Callable[..., dict]] = None,
~~~~


## H14 Core conversation input

File: [`agent/conversation_loop.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/agent/conversation_loop.py).

SHA-256: `04e078c88a02499f9b871e0e72b3d20f4415916a46537b2f38d1d694e2c667e5`.


[Lines 1775–1788](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/agent/conversation_loop.py#L1775-L1788):

~~~~python
def run_conversation(
    agent,
    user_message: Any,
    system_message: str | None = None,
    conversation_history: list[dict[str, Any]] | None = None,
    task_id: str | None = None,
    stream_callback: Optional[callable] = None,
    persist_user_message: Optional[Any] = None,
    persist_user_timestamp: Optional[float] = None,
    persist_user_display_kind: Optional[str] = None,
    persist_user_display_metadata: Optional[dict[str, Any]] = None,
    persist_user_platform_id: Optional[str] = None,
    moa_config: Optional[dict[str, Any]] = None,
    turn_author: Optional[dict[str, Any]] = None,
~~~~


## H15 Native setup and coupled memory switch

File: [`tui_gateway/agent_factory.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/agent_factory.py).

SHA-256: `f73462dcc0e0674de09f45a90cc46312b0fcf404f1d2b55aa897d3f537919977`.


[Lines 634–648](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/agent_factory.py#L634-L648):

~~~~python
    # AC-4 test seam: dead unless armed by the isolated certify harness.
    from tui_gateway.synthetic_turn import maybe_build_synthetic_agent
    synthetic = maybe_build_synthetic_agent(session_id or key, model_override)
    if synthetic is not None:
        return synthetic
    from agent.onboarding_session import onboarding_toolsets
    from run_agent import AIAgent
    # MCP discovery runs in a daemon thread (a dead server can't freeze the shell); the agent snapshots its tool
    # list once, so briefly wait for in-flight discovery. Dashboard /api/ws uses mcp_startup; TUI stdio uses entry.
    for _mod in ("hermes_cli.mcp_startup", "tui_gateway.entry"):
        with contextlib.suppress(Exception):
            importlib.import_module(_mod).wait_for_mcp_discovery()
    cfg = _load_cfg()
    # Load hooks alongside the same profile config used to construct this agent.
    from agent.shell_hooks import register_from_config
~~~~


[Lines 674–685](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/agent_factory.py#L674-L685):

~~~~python
        provider_data_collection=_pr.get("data_collection"), platform=platform, session_id=session_id or key,
        cwd=cwd_override,
        # The dashboard login identity reaches memory providers as the runtime user, like a gateway user id.
        # Builds that run before the record exists (branch, eager resume, compute host) pass it explicitly.
        user_id=auth_user_id if auth_user_id is not None else _session_auth_user_id(session),
        session_db=session_db if session_db is not None else _get_db(), ephemeral_system_prompt=system_prompt or None,
        checkpoints_enabled=_resolve_checkpoints_enabled(cfg),
        pass_session_id=is_truthy_value(os.environ.get("HERMES_TUI_PASS_SESSION_ID")),
        skip_context_files=ignore_rules, skip_memory=ignore_rules, fallback_model=_load_fallback_model(),
        # The resolved provider's request body (a custom entry's extra_body), as the CLI/cron/gateway pass it.
        request_overrides=runtime.get("request_overrides"),
        prefill_messages=_load_prefill_messages() or None, **_agent_cbs(sid))
~~~~


## H16 Memory initialization

File: [`agent/agent_init.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/agent/agent_init.py).

SHA-256: `6a1a4b4cc8304950578a4e04127440e279cc0c94c88d8ea019b72c7ec0625db0`.


[Lines 1223–1237](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/agent/agent_init.py#L1223-L1237):

~~~~python
    # skip_memory skips the external *provider*; enabled_toolsets=["memory"] still gets the
    # built-in store so the memory tool never sees store=None.
    # Flush/background agents can still pass enabled_toolsets=["memory"] so the built-in file store exists
    # and the memory tool does not fail with store=None (#65429). A toolset on disabled_toolsets is not a
    # request: a caller that denylists memory while its default toolset still names it must not get
    # MEMORY.md loaded by an enabled-only check. (Cron agents now run with skip_memory=False and take the
    # normal path here.)
    _memory_toolset_requested = (
        "memory" in (agent.enabled_toolsets or [])
        and "memory" not in (agent.disabled_toolsets or [])
    )
    if not skip_memory or _memory_toolset_requested:
        # Memory is optional — don't break agent init
        with suppress(Exception):
            from tools.memory_tool import (
~~~~


[Lines 1238–1238](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/agent/agent_init.py#L1238-L1238):

~~~~python
                MemoryStore, get_builtin_memory_config, get_builtin_memory_store_flags,
~~~~


[Lines 1254–1267](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/agent/agent_init.py#L1254-L1267):

~~~~python
    # External memory provider plugin (one at a time, alongside built-in): memory.provider.
    agent._memory_manager = None
    if memory_manager is not None and not skip_memory:
        # A caller that rebuilds the agent per turn (gateway api_server) hands back the session's
        # already-initialized manager: providers keep their prefetch/retain state across turns instead
        # of being re-initialized (#120116). No initialize_all — the providers are already bound.
        agent._memory_manager = memory_manager
    elif not skip_memory:
        try:
            _mem_provider_name = mem_config.get("provider", "") if mem_config else ""
            if not is_core_memory_provider(_mem_provider_name):
                from agent.memory_manager import MemoryManager as _MemoryManager
                agent._memory_manager = _MemoryManager()
                _mp = resolve_memory_provider(_mem_provider_name, say=agent._emit_startup_warning)
~~~~


## H17 Memory defaults

File: [`tools/memory_tool.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tools/memory_tool.py).

SHA-256: `00c86420cb4d824dbfe2806b1f748a1fc182b8c11ea2f902e8b77d3d035624dd`.


[Lines 306–318](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tools/memory_tool.py#L306-L318):

~~~~python
def get_builtin_memory_store_flags(config: Optional[dict[str, Any]] = None) -> tuple[bool, bool]:
    """Return ``(memory_enabled, user_profile_enabled)`` from resolved config."""
    section = get_builtin_memory_config(config)
    return tuple(is_truthy_value(section.get(k), default=True) for k in ("memory_enabled", "user_profile_enabled"))


@no_cache_check_fn
def check_memory_requirements() -> bool:
    """Snapshot store flags and report whether the built-in tool is available."""
    _memory_surface_flags.set(None)
    flags = get_builtin_memory_store_flags()
    _memory_surface_flags.set(flags)
    return flags[0] or flags[1]
~~~~


## H18 Work after delivery

File: [`agent/turn_finalizer.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/agent/turn_finalizer.py).

SHA-256: `d9cff7b2f05b29c062a0162f49f3a4075a53225a5e4f75a7960f546ec337e103`.


[Lines 845–859](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/agent/turn_finalizer.py#L845-L859):

~~~~python
    # Background memory/skill review runs AFTER delivery so it never competes with the
    # user's task. Suppressed by skip_background_review (e.g. cron): the fork costs
    # ~30K tokens / event with no human-in-the-loop benefit. Best-effort; the review
    # clones the snapshot structurally so its sanitizers can't reach the live transcript.
    if (
        final_response
        and not interrupted
        and not getattr(agent, "skip_background_review", False)
        and (_should_review_memory or _should_review_skills)
    ):
        with suppress(Exception):
            agent._spawn_background_review(
                messages_snapshot=list(messages), review_memory=_should_review_memory,
                review_skills=_should_review_skills,
            )
~~~~


[Lines 861–864](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/agent/turn_finalizer.py#L861-L864):

~~~~python
    # Opt-in (compression.prepare_ahead): near the trigger, write the next compaction summary
    # between turns. No-op otherwise; never raises.
    from agent.prepared_compaction import maybe_prepare
    maybe_prepare(agent, messages, origin="turn-end")
~~~~


## H19 Process sessions and persistence

File: [`tools/process_registry.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tools/process_registry.py).

SHA-256: `5eb3f04e4f3c5204c3838fcf74be108788cf0062b8f7f9ba3cbea6b51491e78c`.


[Lines 567–575](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tools/process_registry.py#L567-L575):

~~~~python
    wsl_chain: bool = False                     # spawned via wsl[.exe]: the host PID is the short-lived
                                                # launcher; Linux-side workers outlive it (#120546)
    handoff_note: str = ""                      # why a subagent handed this process to its parent (rides the notice)
    persist_on_release: bool = False           # opt out of agent-lifecycle cleanup (release()/turn-abandon kill
                                                # sweeps), per terminal(background=true, persist_on_release=true) (#41225)
    output_log: str = ""                        # file the process writes to (worker spawns; no pipe to lose)
    # Watcher/notification routing (persisted for crash recovery)
    watcher_platform: str = ""
    watcher_chat_id: str = ""
~~~~


[Lines 1218–1231](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tools/process_registry.py#L1218-L1231):

~~~~python
        # start_new_session is REQUIRED with systemd-run --scope too: the scope does not
        # give the worker a new session, so from an interactive TUI the worker would
        # share the foreground process group and background spawns would stop the whole
        # session (observed as dead TUIs in state T). Cgroup isolation is unaffected —
        # the scope attaches to the invoked process, not the spawning session.
        output = open_output_log(log) if log else subprocess.PIPE
        try:
            proc = subprocess.Popen(
                spawn_argv, text=True, cwd=session.cwd, env=spawn_env, encoding="utf-8",
                errors="replace", stdout=output, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                start_new_session=True, **_popen_kwargs)
        finally:
            if log:
                os.close(output)
~~~~


[Lines 2512–2526](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tools/process_registry.py#L2512-L2526):

~~~~python
    def kill_all(
        self, task_id: Optional[str] = None, *, exclude_ids: frozenset = frozenset(),
        source: str = "kill_all", consume_output: bool = False) -> int:
        """Kill all running processes, optionally only those ``task_id`` spawned (its ``owner_task_id``).
        Returns how many it stopped. A session whose systemd scope did not stop is not counted
        (its descendants may live on), and a later sweep retries it even after it finished.

        Sessions with ``persist_on_release=True`` are skipped when ``source`` is an
        agent-lifecycle sweep (the default ``kill_all`` release path, a gateway turn
        timeout, or ``agent_close``): an explicitly persisted background job must survive
        session end / compression / error recovery (#41225). An explicit operator stop
        (``process.kill`` via process_manage, CLI /stop) passes its own source and still
        reaches them, so the user can always stop a persisted process on purpose."""
        lifecycle = source in self._LIFECYCLE_KILL_SOURCES
        with self._lock:
~~~~


[Lines 2527–2535](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tools/process_registry.py#L2527-L2535):

~~~~python
            targets = [
                s for s in (*self._running.values(), *self._finished.values())
                if (task_id is None or s.owner_task_id == task_id)
                and s.id not in exclude_ids and (not s.exited or s._scope_stop_pending)
                and not (lifecycle and s.persist_on_release)
            ]
        results = [self.kill_process(s.id, source=source, consume_output=consume_output) for s in targets]
        return sum(
            r.get("status") in {"killed", "already_exited"} and "scope_stop_failed" not in r
~~~~


## H20 Agent close

File: [`run_agent.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/run_agent.py).

SHA-256: `05b9bf47d71dd54b67d905fca20c329260b0447a21ab12227afe37653bfac4ff`.


[Lines 938–951](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/run_agent.py#L938-L951):

~~~~python
    def close(self) -> None:
        """Release every resource this agent holds (idempotent); each phase is guarded so one failure never
        blocks the rest."""
        session_messages = getattr(self, "_session_messages", None)
        _quietly(self.shutdown_memory_provider, session_messages if isinstance(session_messages, list) else None)
        self._close_task_resources(getattr(self, "session_id", None) or "")
        self._close_active_children(soft=False)
        from agent.prepared_compaction import release_for_agent
        _quietly(release_for_agent, self)
        _quietly(self._drop_shared_client, lambda c: self._close_openai_client(c, reason="agent_close", shared=True))
        self._close_request_clients("agent_close")
        _quietly(self._close_codex_session)
        # Free conversation history proactively: callers may still hold the closed agent. The DB-flush
        # settled-prefix snapshot and the streamed-text accumulator are shadow copies of the same transcript;
~~~~


## H21 Provider resolution ladder

File: [`hermes_cli/runtime_provider.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/hermes_cli/runtime_provider.py).

SHA-256: `a7a04db0bbd53b8e49b841a0ddc297bf173ac8e3f8efa3576dbd9fb5cf97f1e4`.


[Lines 1042–1056](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/hermes_cli/runtime_provider.py#L1042-L1056):

~~~~python
def resolve_runtime_provider(*, requested: Optional[str] = None, explicit_api_key: Optional[str] = None,
                             explicit_base_url: Optional[str] = None, target_model: Optional[str] = None) -> dict[str, Any]:
    """Resolve runtime provider credentials for agent execution. Ladder (order is behavior — each
    rung returns or raises, else falls to the next):
      1. disabled-provider guard (``providers.<name>.enabled: false``)
      2. requested-name shortcuts: moa, anthropic@azure, azure-foundry, vertex
      3. named custom provider / llamacpp alias / bare-custom direct alias
      4. local-endpoint bypass (no explicit creds, config base_url at a non-cloud host)
      5. ``auth.resolve_provider`` → explicit --api-key/--base-url path
      6. credential pool (OpenRouter pool only without custom endpoint/override)
      7. OAuth specs (nous/codex/xai/qwen; "auto" swallows AuthError, logs, and stamps it on a
         keyless fallback as ``auth_error``) → minimax-oauth
         → external-process → anthropic env → bedrock → registry api_key providers
      8. OpenRouter / bare-custom fallback
      9. ``model.openai_runtime`` overlay (openai/openai-codex, named custom providers): rewrites the picked rung's
~~~~


[Lines 1057–1060](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/hermes_cli/runtime_provider.py#L1057-L1060):

~~~~python
         api_mode to ``codex_app_server``; the rung's credential/endpoint is then not used
    target_model overrides model_cfg["default"] when computing provider-specific api_mode (e.g.
    OpenCode Zen/Go where different models route through different API surfaces)."""
    requested_provider = resolve_requested_provider(requested)
~~~~


[Lines 1071–1084](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/hermes_cli/runtime_provider.py#L1071-L1084):

~~~~python
    runtime = next(r for r in _ladder_rungs(requested_provider, explicit_api_key, explicit_base_url, target_model) if r)
    _raise_for_credentialless_bare_custom(requested_provider, runtime)
    # model.openai_runtime is applied ONCE, after the ladder: every rung (pool, OAuth store,
    # explicit --api-key/--base-url, env key) hardcodes the wire api_mode for openai/openai-codex,
    # so applying the opt-in inside one rung left the others on codex_responses (#115169).
    api_mode = _maybe_apply_codex_app_server_runtime(
        provider=runtime.get("provider", ""), api_mode=runtime.get("api_mode", ""), model_cfg=_get_model_config(),
        requested_provider=requested_alias)
    if api_mode != runtime.get("api_mode"):
        logger.info("model.openai_runtime=codex_app_server overrides the %s runtime (source=%s); its credential/endpoint "
                    "is not used — the app-server authenticates with its own login", runtime.get("provider"), runtime.get("source"))
    runtime["api_mode"] = api_mode
    return runtime

~~~~


## H22 Retry and recovery defaults

File: [`agent/agent_init.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/agent/agent_init.py).

SHA-256: `6a1a4b4cc8304950578a4e04127440e279cc0c94c88d8ea019b72c7ec0625db0`.


[Lines 1340–1352](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/agent/agent_init.py#L1340-L1352):

~~~~python
    # App-level API retry count (wraps each model API call). Default 3; 1 = single attempt.
    try:
        _api_retries = max(int(_agent_section.get("api_max_retries", 3)), 1)
    except (TypeError, ValueError):
        _api_retries = 3
    agent._api_max_retries = _api_retries
    # Bounded post-exhaustion auto-recovery cycles once retries AND the fallback chain are spent
    # on a transient outage (agent/turn_recovery_autorecover.py). 0 disables the ladder.
    try:
        agent._auto_recovery_cycles = max(int(_agent_section.get("auto_recovery_cycles", 5)), 0)
    except (TypeError, ValueError):
        agent._auto_recovery_cycles = 5

~~~~


## H23 Message events

File: [`tui_gateway/contracts/events.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/events.py).

SHA-256: `4081b6e18a695eea85441ec922f6392b36c3faced3a131776072ef61fc0965f1`.


[Lines 154–168](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/events.py#L154-L168):

~~~~python
class StreamDeltaPayload(Payload):
    """``prompt_turn._invoke_agent._stream`` (message.delta: ``text`` + optional ``rendered``),
    ``agent_callbacks._agent_cbs`` (reasoning.delta / thinking.delta), ``tool_progress._progress_reasoning``
    (reasoning.available). ``verbose`` rides only when the session's verbose reasoning mode is on."""

    text: str
    rendered: str | None = None
    verbose: bool | None = None


class MessageDeltaPayload(StreamDeltaPayload):
    """``message.delta``. A session-authority local-viewer turn also publishes ``text: null``: the
    reply segment boundary (the agent's ``stream_delta_callback(None)``, before tool lines) that
    closes the classic CLI's reply box. Every other viewer ignores an empty chunk.

~~~~


[Lines 169–173](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/events.py#L169-L173):

~~~~python
    A prompt turn stamps ``turn_id`` + ``segment`` (interim seals before it) + ``offset`` (UTF-16 code
    units of that segment already sent): a client drops a re-sent chunk it already applied."""

    text: str | None
    turn_id: str | None = None
~~~~


[Lines 281–295](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/events.py#L281-L295):

~~~~python
class MessageCompletePayload(Payload):
    """``prompt_turn._complete_turn_payload`` / ``session_auto_continue._emit_terminal_turn_error`` /
    ``agent_callbacks._mirror_subagent_to_child`` (child watch mirror: ``text`` only) /
    ``compute_host_bridge`` (``text`` + ``status``)."""

    text: str | JsonValue = ""
    usage: Usage | None = None
    status: TurnStatus | None = None
    reasoning: str | None = None
    warning: str | None = None
    response_previewed: bool | None = None
    #: ``text`` is a response this turn already delivered (streamed and/or sealed) — it adds no text.
    response_reused: bool | None = None
    response_transformed: bool | None = None
    billing: BillingBlock | None = None
~~~~


[Lines 296–296](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/events.py#L296-L296):

~~~~python
    failure_reason: str | None = None
~~~~


[Lines 297–305](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/events.py#L297-L305):

~~~~python
    rendered: str | None = None
    error: str | None = None
    recoverable: bool | None = None
    error_surface: ErrorSurface | None = None
    partial: bool | None = None
    persisted_turn: PersistedTurn | None = None


event("message.complete", MessageCompletePayload, doc="The turn ended: final text, usage and outcome.")
~~~~


## H24 Tool events

File: [`tui_gateway/contracts/events.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/events.py).

SHA-256: `4081b6e18a695eea85441ec922f6392b36c3faced3a131776072ef61fc0965f1`.


[Lines 399–413](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/events.py#L399-L413):

~~~~python
class ToolStartPayload(Payload):
    """``tool_progress._on_tool_start`` (+ ``agent_callbacks._mirror_subagent_to_child`` rows with
    ``preview`` and empty ``args``). ``todos``/``revision`` are NOT set by the emitter; kept optional
    because tool.start rows may pass through connector redaction unchanged."""

    tool_id: str
    name: str
    context: str | None = None
    args: dict[str, JsonValue] | None = None
    args_text: str | None = None
    preview: str | None = None
    labels: list[ToolLabel] | None = None


event("tool.start", ToolStartPayload, doc="A tool call began (stable id + full args).")
~~~~


[Lines 416–430](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/events.py#L416-L430):

~~~~python
class ToolCompletePayload(Payload):
    """``tool_progress._on_tool_complete``; ``todos``/``revision`` merged in for the todo tools."""

    tool_id: str
    name: str
    args: dict[str, JsonValue] | None = None  # mirrored child rows / room relays omit it
    duration_s: float | None = None
    result: JsonValue = None
    summary: str | None = None
    result_text: str | None = None
    inline_diff: str | None = None
    todos: list[JsonValue] | None = None
    revision: int | None = None
    labels: list[ToolLabel] | None = None

~~~~


[Lines 431–431](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/events.py#L431-L431):

~~~~python

~~~~


## H25 Questions and capability negotiation

File: [`tui_gateway/server_requests.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/server_requests.py).

SHA-256: `10e64a801daf59efd1e60d085c548649ca998901ca1eb7c3a49cfd61f7e03f20`.


[Lines 1–15](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/server_requests.py#L1-L15):

~~~~python
"""Server→client JSON-RPC requests: the backend asks the renderer a question and waits for the
response frame carrying the same ``id``.

JSON-RPC is peer-to-peer; this is the backend's half. Every "ask the renderer" bridge (clarify,
approval, sudo, secret, vault prompts, desktop GUI reads, MCP setup consent, the tour) is one
:func:`send` (blocking) or :func:`send_async` (queue-backed approvals) and one response frame from
the client — no paired ``*.request`` notification / ``*.respond`` method, no per-kind ``*.expire``.

Ids are ``srq-<12 hex>``: strings never collide with client-minted integer ids, and the random
part keeps a compute-host child's requests distinct from the parent's when both reach one socket.
A request that times out or is cancelled (interrupt, session close, shutdown) emits ONE
``request.cancel {id, method, reason}`` notification so every renderer tears the card down the
same way. A response for an id that is no longer open is dropped — the wait already returned.

Reconnect: unanswered requests are returned as ``open_requests`` by ``session.resume`` /
~~~~


[Lines 16–17](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/server_requests.py#L16-L17):

~~~~python
``session.activate`` / ``session.events.since`` (:func:`open_requests`); the shared TypeScript
channel re-delivers them as if they had just arrived, so the notification replay ring never
~~~~


[Lines 29–34](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/server_requests.py#L29-L34):

~~~~python

Capability: a client says once per connection that it answers server→client requests
(``client.capabilities {server_requests: true}`` → :func:`advertise`). A WebSocket client that never
did is a build older than this half of the protocol — it drops the frame silently and the agent
would wait the full deadline (clarify's 300s) for nothing — so :func:`send` / :func:`send_async`
return the same ``None`` an error response produces without writing the frame (#112548).
~~~~


## H26 Clarification deadline

File: [`tui_gateway/server.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/server.py).

SHA-256: `365503fd6145056e0f455ed7e47fc28b1d09841fcf3747c21aac5265c48b775d`.


[Lines 1099–1107](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/server.py#L1099-L1107):

~~~~python

def _clarify_timeout_seconds() -> float | None:
    """Clarify wait for the TUI/desktop bridge from the canonical config (gateway/CLI parity); 300s
    historical default if config can't be read; ``<= 0`` = unlimited → None (never auto-skip)."""
    with contextlib.suppress(Exception):
        from tools.clarify_gateway import get_clarify_timeout
        timeout = get_clarify_timeout()
        return timeout if timeout > 0 else None
    return 300
~~~~


## H27 Child attribution

File: [`tui_gateway/tool_progress.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/tool_progress.py).

SHA-256: `f7d69cf0dfca61c98cb87315178d01f99c2cb76406c159fc61adecf9a38d74d8`.


[Lines 457–468](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/tool_progress.py#L457-L468):

~~~~python
# Optional subagent.* payload fields in WIRE ORDER: (source key, present-when, coerce). Identity fields
# are all optional: older emitters omit them and the TUI spawn tree falls back to flat rendering.
# `tool_name`/`text` are fed from the positional name/preview; `output_tail` is a list of dicts.
_SUBAGENT_FIELDS = (
    ("subagent_id", bool, str), ("parent_id", bool, str), ("child_session_id", bool, str),
    ("delegation_id", bool, str), ("depth", _not_none, int), ("model", bool, str), ("tool_count", _not_none, int),
    ("toolsets", bool, _str_list), ("input_tokens", _not_none, _int_or_skip), ("output_tokens", _not_none, _int_or_skip),
    ("reasoning_tokens", _not_none, _int_or_skip), ("api_calls", _not_none, _int_or_skip),
    ("files_read", bool, _str_list), ("files_written", bool, _str_list), ("output_tail", bool, list),
    ("tool_name", bool, str), ("text", bool, str), ("status", bool, str), ("summary", bool, str),
    ("duration_seconds", _not_none, float),
)
~~~~


[Lines 489–499](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/tool_progress.py#L489-L499):

~~~~python
def _progress_subagent(sid: str, name: str, preview, kw, event_type):
    payload = _subagent_payload(event_type, name, preview, kw, show_reasoning=bool(_session_show_reasoning(sid)))
    # subagent.text is the child's per-token reply, relayed solely to feed a watch window's live mirror
    # (keyed off the child sid); on the parent it's hundreds of ignored frames, so skip it.
    if event_type != "subagent.text":
        _emit(event_type, sid, payload)
    # The child runs under the PARENT's profile: the mirror and its liveness registry are scoped to
    # that home. A parent record already gone (close / WS orphan reap mid-turn) cannot be attributed
    # to a profile — bind nothing rather than fold the run into the launch profile.
    if (parent := _sessions.get(sid)) is not None:
        _mirror_subagent_to_child(event_type, payload, parent.get("profile_home"))
~~~~


## H28 Usage fields

File: [`tui_gateway/contracts/common.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/common.py).

SHA-256: `07213a40356a8fed318a21b288ebec50bd6bd072d2c5fc67150f2062f1039104`.


[Lines 28–42](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/common.py#L28-L42):

~~~~python
class Usage(OpenModel):
    """``tui_gateway/server.py::_get_usage`` + ``agent/context_breakdown.py::context_usage_fields``."""

    model: str = ""
    input: int = 0
    output: int = 0
    reasoning: int = 0
    prompt: int = 0
    completion: int = 0
    total: int = 0
    calls: int = 0
    compressions: int | None = None
    context_used: int | None = None
    context_max: int | None = None
    context_percent: int | None = None
~~~~


[Lines 43–54](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/common.py#L43-L54):

~~~~python
    context_source: str | None = None
    context_estimated: bool | None = None
    cache_hit_pct: int | None = None
    cache_read: int | None = None
    cache_write: int | None = None
    avg_latency_s: float | None = None
    avg_tps: float | None = None
    active_subagents: int | None = None
    dev_credits_spent_micros: int | None = None
    cost_usd: float | None = None
    cost_status: str | None = None
    plan_gauge: PlanGauge | None = None
~~~~


## H29 HTTP run API

File: [`gateway/platforms/api_server.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/gateway/platforms/api_server.py).

SHA-256: `ecb1ad0b511643ac587a753982e9d14b56818b06873c812ff617809c7457e2a3`.


[Lines 59–73](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/gateway/platforms/api_server.py#L59-L73):

~~~~python
# /v1/capabilities "endpoints" table: name -> (method, path[, feature]). An entry naming a
# feature is advertised only while that "features" flag is truthy on this listener.
_CAPABILITY_ENDPOINTS = (
    ("health", ("GET", "/health")), ("health_detailed", ("GET", "/health/detailed")),
    ("models", ("GET", "/v1/models")), ("model_options", ("GET", "/api/model/options")),
    ("chat_completions", ("POST", "/v1/chat/completions")),
    ("responses", ("POST", "/v1/responses")), ("runs", ("POST", "/v1/runs")),
    ("run_status", ("GET", "/v1/runs/{run_id}")),
    ("run_events", ("GET", "/v1/runs/{run_id}/events")),
    ("run_approval", ("POST", "/v1/runs/{run_id}/approval")),
    ("run_steer", ("POST", "/v1/runs/{run_id}/steer")),
    ("run_unknown_resolution", ("POST", "/v1/runs/{run_id}/resolve-unknown", "run_unknown_resolution")),
    ("run_stop", ("POST", "/v1/runs/{run_id}/stop")), ("skills", ("GET", "/v1/skills")),
    ("toolsets", ("GET", "/v1/toolsets")), ("sessions", ("GET", "/api/sessions")),
    ("session_create", ("POST", "/api/sessions")),
~~~~


[Lines 74–74](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/gateway/platforms/api_server.py#L74-L74):

~~~~python
    ("session", ("GET", "/api/sessions/{session_id}")),
~~~~


## H30 Canonical create controls

File: [`tui_gateway/contracts/canonical_sessions.py`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/canonical_sessions.py).

SHA-256: `a321c08cfef7e54825fb3c820ad3e826ccfd7fd166d505eddaeea58ff551235e`.


[Lines 21–35](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/canonical_sessions.py#L21-L35):

~~~~python
class CanonicalCreateParams(ProfileParams):
    request_id: str | None = None
    source: Literal['cli', 'tui', 'gui', 'acp', 'tool', 'oneshot'] = 'cli'
    cwd: str | None = None
    # The sessions-row ``cwd`` when it differs from the execution ``cwd`` (the classic CLI records
    # main's stamp: the launch dir, ``""`` = none); ``cwd`` stays where the tools run.
    row_cwd: str | None = None
    model: str | None = None
    provider: str | None = None
    base_url: str | None = None
    api_key: str | None = None
    toolsets: list[str] | None = None
    reasoning: str | None = None
    max_turns: int | str | None = None
    ignore_rules: bool = False
~~~~


[Lines 36–36](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/canonical_sessions.py#L36-L36):

~~~~python
    yolo: bool = False
~~~~


[Lines 37–49](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/tui_gateway/contracts/canonical_sessions.py#L37-L49):

~~~~python
    safe_mode: bool = False
    ignore_user_config: bool = False
    skills: list[str] | None = None
    checkpoints: bool = False
    accept_hooks: bool = False
    pass_session_id: bool = False
    editor: dict[str, JsonValue] | None = None
    title: str | None = None
    hidden: bool = False
    follow_profile_config: bool | None = None
    service_tier: str | None = None
    cwd_explicit: bool | None = None
    # Wall-clock budget per run in seconds (the classic CLI's `--run-budget`).
~~~~


## H31 Provider-aware model catalogs

File: [`website/docs/developer-guide/programmatic-integration.md`](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/website/docs/developer-guide/programmatic-integration.md).

SHA-256: `41f2454c8ca1c46dbd04dba6f8ea54d53c7913a1b6c8ad17235bb340cc17fb7f`.


[Lines 154–165](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/website/docs/developer-guide/programmatic-integration.md#L154-L165):

~~~~text
### Model catalog surfaces

The OpenAI-compatible API intentionally keeps `GET /v1/models` minimal: it is
the compatibility endpoint frontends expect, not the full Hermes provider/model
picker catalog.

If an external control plane needs Hermes' curated provider rows, per-model
pricing, or capability hints, use one of the authenticated picker surfaces:

- API server REST: `GET /api/model/options` with the API-server bearer key
- Dashboard backend REST: `GET /api/model/options` with `X-Hermes-Session-Token`
- TUI gateway RPC: `model.options`
~~~~


[Lines 167–176](https://github.com/NousResearch/hermes-agent/blob/b63fbbac4d27d1e4b8585ff7065e6dceb6207394/website/docs/developer-guide/programmatic-integration.md#L167-L176):

~~~~text
Those surfaces share the same payload builder and the same custom-provider
probe policy:

- Normal open: probe only the current custom provider so offline saved
  endpoints do not stall the picker.
- Explicit refresh (`refresh=1` or `refresh: true`): bust the provider-model
  cache and probe all saved custom providers so live catalogs repopulate fully.

Use `/v1/models` for OpenAI-client compatibility. Use `/api/model/options` or
`model.options` when you are building a Hermes-aware model picker.
~~~~


## Release comparison

The following exact blocks were also read at release v0.22.5. They establish
that the ACP viewer and exclusive standalone-home behavior were already in that
release; other main-branch behavior in this snapshot is not thereby qualified
for v0.22.5.


[`acp_adapter/server.py`, release lines 245–250](https://github.com/NousResearch/hermes-agent/blob/bf0203a794a07aac3ff764972ab9087baa4e4f4e/acp_adapter/server.py#L245-L250):

~~~~python
    def __new__(cls, session_manager=None):
        if session_manager is None:
            from acp_adapter.gateway_server import GatewayACPAgent
            return GatewayACPAgent()
        return super().__new__(cls)

~~~~


[`acp_adapter/entry.py`, release lines 201–203](https://github.com/NousResearch/hermes-agent/blob/bf0203a794a07aac3ff764972ab9087baa4e4f4e/acp_adapter/entry.py#L201-L203):

~~~~python
    # MCP discovery and execution belong to the gateway daemon; this process is a viewer.
    agent = HermesACPAgent()

~~~~


[`tui_gateway/entry.py`, release lines 273–287](https://github.com/NousResearch/hermes-agent/blob/bf0203a794a07aac3ff764972ab9087baa4e4f4e/tui_gateway/entry.py#L273-L287):

~~~~python
def _claim_launch_home():
    """Reserve the launch home exactly as the gateway does, or None when it is already owned.

    No product surface launches this standalone stdio server any more: Ink and Desktop attach to
    the profile's gateway over WS (``ui-tui/scripts/gateway_bootstrap.py``). Dev harnesses still
    run it against a sandbox home (``apps/desktop/e2e/real-session-builder.ts``), and it opens that
    home's ``state.db`` as a writer, so it must be the home's only owner: the gateway's
    ``gateway.lock`` reservation refuses it beside a live gateway (or a second entry), and holding
    that lock keeps a gateway from starting on the home while this process writes."""
    from gateway.runtime_ownership import OwnershipConflict, process_ownership
    home = server._launch_home()
    try:
        process_ownership.reserve([home])
    except OwnershipConflict:
        return None
~~~~


## License

Upstream excerpts are reproduced under the following upstream license.

~~~~text
MIT License

Copyright (c) 2025 Nous Research

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
~~~~
