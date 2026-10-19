---
role: authored
---
# Arbol backend

This chapter specifies three parts of Arbol. The *Arbol backend* is the program that works behind the windows of one [Root](../GLOSSARY.md#arbol-root): it reads the Root's chats, keeps what the [Leather Bag](../GLOSSARY.md#leather-bag) typed and has not sent, the [Drafts](../GLOSSARY.md#draft), and has a Trunk answer each message. The *[Bridge](../GLOSSARY.md#bridge)* is the set of messages a window and its backend send each other. *[Elma Chat](../GLOSSARY.md#elma-chat)'s first version* is the chat window of a Root, as version 1's Elma Chat looked and worked. For example, the Leather Bag opens Elma Chat in First Sapling, types "What does build.sh do?" and presses ⌘⏎: the window sends `chat.send` over the Bridge, the backend has `arbol-root start` start the Trivial Trunk, follows the answer as it arrives in the Exchange's folder and passes it on line by line, and when the Leather Bag opens the chat again the next day the backend reads it from the chat tables.

Three words are kept apart here. A *window* is one Elma Chat window on the screen; each Root has one, and windows of several Roots can be open at once. Its *page* is the web page it shows, loaded from Elma Chat's *renderer bundle*, the files of the [UI](../GLOSSARY.md#ui) in each `arbol` Build. Elma Chat is the UI.

The architecture says where these parts stand ([ARC-0](../architecture/00-components-and-boundaries.md#arbol-the-swift-app-and-the-backend), "Arbol: the Swift App and the backend"; [ARC-1](../architecture/01-roots.md) to [ARC-3](../architecture/03-stuck-trunks.md)). The [Root Contract](../../arbol-root/contract/README.md) says what the backend shares with every Trunk, and the [Root manager's specifications](../../arbol-root/specs/README.md) what the commands of `arbol-root` do and print. The specifications here say what the backend does, what crosses the Bridge, and what the first window shows. Written in SYL-190 on 18 October 2026.

## Specifications

| Spec | Title | Status |
|---|---|---|
| [BKD-0](00-the-arbol-backend.md) | The Arbol backend | review |
| [BKD-1](01-the-bridge.md) | The Bridge | review |
| [BKD-2](02-elma-chat.md) | Elma Chat, its first version | review |

Not here: Brain Recipes and how a route is chosen (SYL-191), the Arbol Swift App with the tray menu and the windows (SYL-192), the command line `arbol` (SYL-193), the pages of Seqoya Lab, the Secrets page among them (SYL-194), listeners such as Telegram ([ARC-D52](../architecture/01-roots.md#decisions)), and bringing one chat over again into a newer Root (SYL-195).

## Where the architecture's and the Root Contract's requirements of Arbol are carried

In the READMEs of the [Root Contract](../../arbol-root/contract/README.md#where-the-architectures-requirements-of-a-trunk-are-carried) and the [Root manager](../../arbol-root/specs/README.md#where-the-architectures-requirements-of-the-root-manager-are-carried), *Arbol's own specification* means that of `arbol` and `arbol-roots`. This chapter carries the backend's and the first window's part; the rows below name the task for every other part. `arbol-roots` has no specification beyond ARC-1 and RTM-1.

| Requirement | Carried by |
|---|---|
| ARC-0.4 | The UIs: BKD-2 for Elma Chat's first version; the command line: SYL-193; listeners: not yet (ARC-D52) |
| ARC-0.5, ARC-0.6, ARC-0.26 | SYL-192; what the Bridge needs of the Swift App: BKD-1.2, BKD-1.11 |
| ARC-0.7 | Keeping the current Root's backend running: SYL-192; no listener outside the current Root: BKD-0.3 |
| ARC-0.8 | BKD-0.5, BKD-0.8 |
| ARC-0.9 | Elma Chat resolves no Brain Recipe: its route is the Leather Bag's choice or a default, and its small-call route a default (BKD-0.11, BKD-0.30, BKD-D3). This narrows ARC-0.9 and the offer after a rate limit in ARC-2 for Elma Chat, by the owner's decision of 19 October 2026; resolving a Brain Recipe where one is used: SYL-191 |
| ARC-0.10 | BKD-0.25 calls the account commands Elma Chat needs; the Leather Bag signs in with the Driver's own command until Seqoya Lab has a page for it, which then shows what `sign-in` asks to show (BKD-D17, SYL-194); BKD-2.20 names the command |
| ARC-0.11 | SYL-193 |
| ARC-0.14 | BKD-0.27, BKD-0.28; BKD-2.21 shows the warning |
| ARC-0.31 | SYL-194; no secret crosses the Bridge or passes through the backend (BKD-1.10, BKD-0.25) |
| ARC-1.2 | BKD-0.7 (the backend's own tables and settings), BKD-1.9 (the Bridge) |
| ARC-1.5 | BKD-0.5, BKD-0.22 |
| ARC-1.6 | The display name in the header of the window, also as the Root's state changes: BKD-2.1, BKD-0.3; the tray menu: SYL-192 |
| ARC-1.7 | BKD-0.3 |
| ARC-1.8 | BKD-0.2, BKD-2.1 |
| ARC-1.10 | BKD-0.30 reads `arbol.json` from `~/.arbol/roots/<root>/` |
| ARC-1.11 | BKD-0.27 measures it; showing it: the tray menu (SYL-192), because version 1's Elma Chat, which BKD-2 keeps, had no place for it |
| ARC-1.18 | The migration itself: RTM-1.7, RTM-1.8 (SYL-189); a Root that is `preparing` in the header of the window: BKD-2.1; in the tray menu, and a failed migration reported there: SYL-192 |
| ARC-1.19, ARC-1.20 | SYL-195 |
| ARC-1.21 | Opening a failed Root that is named: BKD-0.2, BKD-2.1 |
| ARC-1.22 | For the backend's Builds: BKD-0.29 |
| ARC-1.25 | BKD-0.22 |
| ARC-1.26 | BKD-0.21, BKD-0.22 |
| ARC-1.28 | That the backend creates or changes no table: BKD-0.6, with its own tables in the Root's own layout of BKD-0's Interface, which `arbol-roots` runs (RTM-1) |
| ARC-2.1 | BKD-0.11, BKD-0.12; BKD-2.11 puts a refused message back in the composer |
| ARC-2.4 | BKD-0.15; BKD-1.6; BKD-2.5 |
| ARC-2.5 | BKD-0.16, BKD-0.17; BKD-2.13, BKD-2.15 |
| ARC-2.7 | BKD-0.18; BKD-2.16 |
| ARC-2.8 | BKD-0.9, BKD-0.14 |
| ARC-2.9 | Arbol's part: BKD-0.24 keeps the Draft of a message refused while the database is away; BKD-2.11 |
| ARC-2.11 | BKD-0.21; BKD-1.7; BKD-2.22 |
| ARC-2.13 | BKD-0.22 |
| ARC-2.14 | BKD-0.23, BKD-0.24; BKD-2.16, BKD-2.21 |
| ARC-3.9 | BKD-0.19 |
| ARC-3.10 | The looks of ARC-3.9, counted with `CLOCK_UPTIME_RAW`: BKD-0.19 |
| ARC-3.11 | BKD-0.20; BKD-2.16 |
| ARC-3.12 | BKD-0.19; BKD-2.6 |
| ARC-3.13 | BKD-0.16; BKD-2.13 |
| ARC-3.14 | BKD-0.20 keeps what had arrived through `arbol-root stop --force`; BKD-0.14 takes the chat's next message; BKD-2.16 |
| RCT-1.8 | The backend's part: BKD-0.17 |
| RCT-1.9 | The backend's part: BKD-0.15 |
| RCT-1.10 | The backend's part: BKD-0.15 |
| RCT-2.16 | BKD-2.13, BKD-2.14 |
| RCT-3.8 | BKD-0.5, BKD-0.8 |

## Conventions

The chapter follows the conventions of the [Driver Contract](../driver-contract/README.md#conventions) and the additions of the [Architecture](../architecture/README.md#conventions): the shape of a specification, origin, status, decisions and wording, and the checks *journey* and *drill*. Identifiers here start with `BKD`: `BKD-0.4` is requirement 4 of specification 0. Decisions are numbered once for the whole chapter, `BKD-D1` onwards.

**Verified by.** *unit* means a check of the kind `unit` of an `arbol` Build: the backend's tests in its own process, with stand-in programs of `arbol-root`, `arbol-roots` and the Drivers in a folder named with `--bin-dir`, and a PostgreSQL server of the check's own in a temporary folder, as the Root manager's checks have ([RTM-1](../../arbol-root/specs/01-builds-layouts-and-migration.md#the-checks-of-a-build)); for the Bridge and the window, the page's tests in a browser against a stand-in backend. *journey* and *drill* run the installed application on this Mac: until the Arbol Swift App exists (SYL-192), the window runs in a browser through the development relay of [BKD-1](01-the-bridge.md#before-the-swift-app-exists), and what needs the Swift App itself, such as opening a chat from Willo Station, is checked with SYL-192.
