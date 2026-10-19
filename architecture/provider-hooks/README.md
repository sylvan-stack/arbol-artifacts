---
role: authored
---
# Provider hooks

A *provider hook* is a command that the tool of a [Provider](../../GLOSSARY.md#provider), Claude Code or Codex, runs by itself at fixed moments of a session, such as before every tool call, and to which it hands a short JSON description of that moment. It is the only way to watch, or steer, a session that Arbol did not start without changing the tool. This chapter holds what the two tools do with hooks, which hooks are on this Mac or planned, and the rules every hook that Arbol or its checks install must follow. The specifications that use hooks, such as the [agent records](../../agent-records/README.md) and the check from outside of the guide [Working in Sagas](../../../mycel/operations/sagas.md), say only what their own hook does and point here for the rest.

For example, when the Leather Bag types a message in `claude`, Claude Code runs every command listed under `UserPromptSubmit` in `~/.claude/settings.json`, hands each one `{"hook_event_name": "UserPromptSubmit", "session_id": "…", "cwd": "…", "prompt": "…"}` on its standard input, and waits for them before the model sees the message.

The chapter was taken out of [AGR-1](../../agent-records/01-the-hooks.md) on 19 October 2026, at the owner's request, so that the tools' behaviour is written once for every hook. Nothing in AGR-1 changed in meaning.

## Specifications

| Spec | Title | Status |
|---|---|---|
| [PHK-0](00-hooks-of-claude-code-and-codex.md) | The hooks of Claude Code and Codex | draft |
| [PHK-1](01-hooks-on-this-mac.md) | The hooks on this Mac, and the rules for installing one | draft |

## The hooks in one picture

```text
~/.claude/settings.json  (terminal claude, claude-zai, Claude desktop app)
  ├─ arbol-agents hook claude-code   the agent record, 17 events (AGR-1)     accepted, not installed (SYL-202)
  └─ agent-watch-hook                steer or stop, PreToolUse (SYL-221)     planned
~/.codex/hooks.json  (codex in a terminal, Codex app)                        does not exist yet
  ├─ arbol-agents hook codex         the agent record, 12 events (AGR-1)     accepted, not installed (SYL-202)
  └─ agent-watch-hook                steer or stop, PreToolUse (SYL-221)     planned
~/.codex/config.toml  notify = […]   Computer Use, once per finished turn    installed; not a hook
A Driver's run, in ~/.claude or ~/.codex (DRV-D42)                           runs every hook above
```

## Conventions

The chapter follows the conventions of the [Driver Contract](../../driver-contract/README.md#conventions) and the additions of the [Architecture](../README.md#conventions) chapter. Requirement identifiers are `PHK-1.4` (requirement 4 of specification 1); decisions are numbered once for the whole chapter, `PHK-D1` onwards. *probe* and *live* have the Driver Contract's meaning: a probe checks the installed tool without sending a message, a live check sends short messages on a test account, in a test home; either names the tool's version and the date.

What this chapter says about the tools was seen in the live checks of 16 October 2026 ([PHK-0](00-hooks-of-claude-code-and-codex.md#live-checks-of-16-october-2026)) or read on this Mac on 19 October 2026 (Claude Code 2.1.301, Codex CLI 0.162.1). What was not tried is said where it is used.

Version 1 used no hooks of either tool. Every requirement is therefore *New*.
