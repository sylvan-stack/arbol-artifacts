---
role: authored
---
# Agent records

How Arbol sees every agent session on this Mac, whatever tool runs it: Claude Code and Codex, in a terminal or in their apps, and the [Chat Exchanges](../GLOSSARY.md#chat-exchange) of Arbol's own Trunks. Each session keeps one small file, its *agent record*, that says who the agent is, which process owns it, what it waits for and since when, and when it ended. Claude Code and Codex write it through their own hooks, set once in their settings, so neither tool is changed and both keep their full power. An Exchange takes part through the record it already keeps ([RCT-1](../../arbol-root/contract/01-the-exchange-folder.md)).

For example, when a Codex thread starts a long build, its record says that it waits for a command; when the agent asks the Leather Bag which branch to use, it says that it waits for an answer; when the thread is archived, the record gets its end.

It was decided on 15 October 2026 that Arbol must not lock anyone into its own app, and that the tools' hooks write one shared agent record. Two readers are planned: Arbol's [Radar](../GLOSSARY.md#radar), and the check of holds in the guide [Working in Sagas](../../mycel/operations/sagas.md), which releases the [Beat](../GLOSSARY.md#beat) of an agent that is gone and only shows one that is silent.

## Specifications

| Spec | Title | Status |
|---|---|---|
| [AGR-0](00-the-agent-record.md) | The agent record | review |
| [AGR-1](01-the-hooks.md) | The hooks of Claude Code and Codex | review |

## Conventions

The chapter follows the conventions of the [Driver Contract](../driver-contract/README.md#conventions): the shape of a specification, requirement identifiers (`AGR-1.4` is requirement 4 of specification 1), origin, status, decisions and wording. Decisions are numbered once for the whole chapter, `AGR-D1` onwards. *probe* and *live* have the Driver Contract's meaning: a probe checks the installed Claude Code or Codex without sending a message, and a live check sends short messages on a test account, in a test home. Either names the tool's version and the date. *drill* has the meaning given in the [Architecture](../architecture/README.md#conventions) chapter.

Version 1 had no counterpart: it saw only the agents it started itself. Every requirement is therefore *New*.
