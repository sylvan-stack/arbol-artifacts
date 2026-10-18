---
role: authored
---
# Arbol backend

What Arbol itself does for the [Leather Bag](../GLOSSARY.md#leather-bag) while a chat is read, written and answered: the *Arbol backend*, the one process of a Root's `arbol` Build that reads the Root's database, starts and follows [Chat Exchanges](../GLOSSARY.md#chat-exchange) through `arbol-root` and keeps the [Drafts](../GLOSSARY.md#draft); the *[Bridge](../GLOSSARY.md#bridge)*, the messages a window and its backend send each other; and the first [UI](../GLOSSARY.md#ui), a first version of [Elma Chat](../GLOSSARY.md#elma-chat) with one window that lists the Root's chats and shows one of them. For example, the Leather Bag opens Elma Chat in First Sapling, types "What does build.sh do?" and presses Return: the window sends `chat.send` over the Bridge, the backend has `arbol-root start` start the Trivial Trunk, follows the answer as it arrives in the Exchange's folder and passes it on line by line, and when the Leather Bag opens the chat again the next day the backend reads it from the chat tables.

The architecture says where these parts stand ([ARC-0](../architecture/00-components-and-boundaries.md#arbol-the-swift-app-and-the-backend), "Arbol: the Swift App and the backend"; [ARC-1](../architecture/01-roots.md) to [ARC-3](../architecture/03-stuck-trunks.md)). The [Root Contract](../../arbol-root/contract/README.md) says what the backend shares with every Trunk, and the [Root manager's specifications](../../arbol-root/specs/README.md) what the commands of `arbol-root` do and print. The specifications here say what the backend does, what crosses the Bridge, and what the first window shows. Written in SYL-190 on 18 October 2026.

## Specifications

| Spec | Title | Status |
|---|---|---|
| [BKD-0](00-the-arbol-backend.md) | The Arbol backend | draft |
| [BKD-1](01-the-bridge.md) | The Bridge | draft |
| [BKD-2](02-elma-chat.md) | Elma Chat, its first window | draft |

Not here: Brain Recipes and how a route is chosen (SYL-191), the Arbol Swift App with the tray menu and the windows (SYL-192), the command line `arbol` (SYL-193), the pages of Seqoya Lab (SYL-194), listeners such as Telegram ([ARC-D52](../architecture/01-roots.md#decisions)), and bringing one chat over again into a newer Root (ARC-1.19, ARC-1.20; SYL-195).

## Where the architecture's and the Root Contract's requirements of Arbol are carried

*Arbol's own specification* in the READMEs of the [Root Contract](../../arbol-root/contract/README.md#where-the-architectures-requirements-of-a-trunk-are-carried) and the [Root manager](../../arbol-root/specs/README.md#where-the-architectures-requirements-of-the-root-manager-are-carried) means this chapter, except where a row below names another task.

| Requirement | Carried by |
|---|---|
| ARC-0.4 | The UIs: BKD-2 for Elma Chat's first window; the command line: SYL-193; listeners: not yet (ARC-D52) |
| ARC-0.8 | BKD-0.6, BKD-0.7 |
| ARC-0.9 | BKD-0.10 hands down a route and no small-call route; resolving a Brain Recipe: SYL-191 |
| ARC-0.10 | BKD-0.24, BKD-0.25; BKD-2.15 shows the steps |
| ARC-0.11 | SYL-193 |
| ARC-0.14 | BKD-0.26, BKD-0.27; BKD-2.16 shows the warning |
| ARC-1.2 | BKD-0.8 (the backend's own tables and settings), BKD-1.9 (the Bridge) |
| ARC-1.5 | BKD-0.6 |
| ARC-1.6 | The display name in the header of the window: BKD-2.1; the tray menu: SYL-192 |
| ARC-1.7 | BKD-0.3 |
| ARC-1.8 | BKD-0.2, BKD-2.1 |
| ARC-1.11 | BKD-0.26; BKD-2.16 shows it |
| ARC-1.18 | BKD-2.1 shows a Root that is `preparing`; reporting a failed migration in the tray menu: SYL-192 |
| ARC-1.25 | BKD-0.21 |
| ARC-1.26 | BKD-0.20, BKD-0.21 |
| ARC-1.28 | BKD-0.7, and the Root's own layout of BKD-0's Interface, which `arbol-roots` runs |
| ARC-2.1 | BKD-0.10, BKD-0.11; BKD-2.6 keeps the Draft in the composer |
| ARC-2.4 | BKD-0.14; BKD-1.6; BKD-2.4 |
| ARC-2.5 | BKD-0.15, BKD-0.16; BKD-2.8 |
| ARC-2.7 | BKD-0.17; BKD-2.10 |
| ARC-2.8 | BKD-0.12, BKD-0.13 |
| ARC-2.11 | BKD-0.20; BKD-1.7 |
| ARC-2.13 | BKD-0.21 |
| ARC-2.14 | BKD-0.22, BKD-0.23; BKD-2.11, BKD-2.12 |
| ARC-3.9 | BKD-0.18 |
| ARC-3.10 | The looks of ARC-3.9: BKD-0.18, counted with `CLOCK_UPTIME_RAW` |
| ARC-3.11 | BKD-0.19; BKD-2.13 |
| ARC-3.12 | BKD-0.18; BKD-2.5 |
| ARC-3.13 | BKD-0.15; BKD-2.8 |
| ARC-3.14 | BKD-0.19 |
| RCT-1.8 | The backend's part: BKD-0.16 |
| RCT-1.9 | The backend's part: BKD-0.14 |
| RCT-1.10 | The backend's part: BKD-0.14 |
| RCT-2.16 | BKD-2.8, BKD-2.9 |
| RCT-3.8 | BKD-0.6, BKD-0.9 |

## Conventions

The chapter follows the conventions of the [Driver Contract](../driver-contract/README.md#conventions) and the additions of the [Architecture](../architecture/README.md#conventions): the shape of a specification, origin, status, decisions and wording, and the checks *journey* and *drill*. Identifiers here start with `BKD`: `BKD-0.4` is requirement 4 of specification 0. Decisions are numbered once for the whole chapter, `BKD-D1` onwards.

**Verified by.** *unit* means a check of the kind `unit` of an `arbol` Build: the backend's tests in its own process, with stand-in programs of `arbol-root`, `arbol-roots` and the Drivers in a folder named with `--bin-dir`, and a PostgreSQL server of the check's own in a temporary folder, as the Root manager's checks have ([RTM-1](../../arbol-root/specs/01-builds-layouts-and-migration.md#the-checks-of-a-build)); for the Bridge and the window, the renderer's tests in a browser against a stand-in backend. *journey* and *drill* run the installed application on this Mac: until the Arbol Swift App exists (SYL-192), the window runs in a browser through the development relay of [BKD-1](01-the-bridge.md#before-the-swift-app-exists).
