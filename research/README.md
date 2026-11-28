---
role: authored
---
# Arbol research

Research that prepares changes to Arbol's contracts and specifications. These
documents distinguish source observations, proposed designs and matters still
requiring a probe or an owner's decision. They do not accept specifications or
claim release qualification.

Use the [deep-research guide](../../mycel/operations/deep-research.md) and
[Source Refs conventions](../../mycel/operations/source-refs-authoring.md).
Keep external evidence in a dated source snapshot with immutable upstream
links. Code excerpts name the file, revision and line range. Runtime results,
credentials and personal account data stay outside Git. Update an existing
topic before creating another document and list new topics in
[the corpus catalog](../INDEX.md).

- [Mimo Driver investigation](mimo-driver.md): installed CLI interfaces, native
  Xiaomi login, history and prompt semantics, memory and ownership gaps, and
  the qualification needed before specifications are accepted.
- [Mimo 0.1.16 source snapshot, 27 October 2026](mimo-upstream-2026-10-27.md):
  immutable upstream excerpts supporting that investigation; runtime probe
  material stays in ignored local output.
- [Mimo compatibility probes](mimo-compatibility/README.md): native history,
  memory/context controls, normal resource discovery, tools, questions, events,
  actors, errors and process ownership; retains the server-only EOF guardian
  counterexample and the tested command-group ownership bridge that closes
  the pre-specification feasibility blocker. Read the investigation's scope
  before drafting.
- [Importing native harness sessions](native-session-import.md): on-disk session
  formats of Claude Code, Codex, Kimi Code, Pi and Mimo, their mapping to the
  chat tables plus a raw archive, and the questions for Spec Writing.
- [Arbol out of Application Support](arbol-out-of-application-support.md):
  every item under `~/Library/Application Support/Arbol/`, its size, owner and
  the code that names its path; what goes to `~/.arbol/` and what to Mercury;
  the constraints of the move, and the missing cutover archive.
