---
role: authored
---
# Session Import

Turning the saved chat sessions of the vendor tools into Arbol chats. The tools are Claude Code, Codex, Kimi Code, Pi and Mimo.

The owner worked in those tools for months before Arbol was ready for daily use, and wants those conversations in Arbol as training material. On 17 November 2026 the owner decided:
- an imported chat fills the normal chat tables, and its native session is kept whole in a raw archive;
- the chats go into the installed single database;
- sub-agents are nested in their parent chat;
- imported chats are read-only and archived;
- the Mimo importer is built now.

The evidence is in [Importing native harness sessions](../research/native-session-import.md). The work is planned in the [Session Import Saga](/Users/msix/Artifacts/forester/sagas/sylvan-stack/session-import/saga.md).

## Specifications

| Spec | Title | Status |
|---|---|---|
| [IMP-0](00-the-import.md) | The import: the command, which sessions, from a session to a chat, provenance, the raw archive, importing again, read-only chats, admission | accepted |
| [IMP-1](01-reading-each-tool.md) | Reading each tool: where sessions live, their kinds, duplicates, turns, items, sub-agents, usage and liveness for each tool | accepted |

## Conventions

The chapter follows the conventions of the [Driver Contract](../driver-contract/README.md#conventions), with the checks *journey* and *drill* of the [Architecture](../architecture/README.md#conventions). Requirement identifiers are `IMP-0.x` and `IMP-1.x`, and Decisions are numbered once for the chapter, `IMP-D1` onwards. Version 1 had no import, so the Origin column names the owner's decision or the research finding a requirement rests on.

Examples are fictional. No document in this chapter quotes conversation content, credentials or account identifiers.
