---
role: authored
---
# Mimo upstream source snapshot · 27 October 2026

Source evidence for [the Mimo Driver investigation](mimo-driver.md), pinned to
[MiMo-Code v0.1.16](https://github.com/XiaomiMiMo/MiMo-Code/releases/tag/v0.1.16),
commit [`b8dbe084ed8e77be2f75a85a9c880031aed699c9`](https://github.com/XiaomiMiMo/MiMo-Code/commit/b8dbe084ed8e77be2f75a85a9c880031aed699c9).
The installed command reports the same version; that is not a build-provenance
attestation. This snapshot records source, not runtime outcomes or release
qualification. Runtime material stays in ignored local `generated/` output.

Each excerpt names immutable upstream lines. SHA-256 covers its complete source
file. Mimo is an OpenCode fork; leftover OpenCode names and documentation are
not authoritative descriptions when executable source differs. The excerpt
set is deliberately selective; consult the complete linked file for context.
The repository identifies the code package as MIT-licensed.

## M01 Package identity

File: [packages/cli/package.json](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/package.json).

SHA-256: `b86348d9e6619d52a140bdc6d021af0864d19f78da726a2a57210579bd4ea4f0`.

[Lines 3–9](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/package.json#L3-L9):

~~~~text
  "version": "0.1.16",
  "name": "@mimo-ai/cli",
  "type": "module",
  "license": "MIT",
  "publishConfig": {
    "access": "public"
  },
~~~~

## M02 Serve lifecycle

File: [packages/cli/src/cli/cmd/serve.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/cli/cmd/serve.ts).

SHA-256: `f49f9b13114bc17e414d16944e5894e07a29a935d4b13b378c9fe6e22f36fbec`.

[Lines 25–39](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/cli/cmd/serve.ts#L25-L39):

~~~~text
    // Server.listen publishes this process into the llm-server address registry
    // (cwd) and unpublishes on stop, so `mimo llm-server issue` can resolve base_url.
    const server = await Server.listen(opts)
    console.log(`mimocode server listening on http://${server.hostname}:${server.port}`)

    // Force-close: graceful stop waits on live SSE/WS streams, and Ctrl-C would hang.
    const shutdown = () => server.stop(true)
    const onSignal = () => {
      void shutdown()
        .then(() => process.exit(0))
        .catch(() => process.exit(1))
    }
    process.once("SIGINT", onSignal)
    process.once("SIGTERM", onSignal)

~~~~

## M03 Run session policy

File: [packages/cli/src/cli/cmd/run.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/cli/cmd/run.ts).

SHA-256: `d0eb283ba0f82d6744d839fbed0fbb1f00673743638f7bf2ab21ad0499d68a79`.

[Lines 368–380](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/cli/cmd/run.ts#L368-L380):

~~~~text
    const rules: Permission.Ruleset = [
      {
        permission: "question",
        action: "deny",
        pattern: "*",
      },
      {
        permission: "plan_exit",
        action: "deny",
        pattern: "*",
      },
    ]

~~~~

## M04 Run event projection

File: [packages/cli/src/cli/cmd/run.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/cli/cmd/run.ts).

SHA-256: `d0eb283ba0f82d6744d839fbed0fbb1f00673743638f7bf2ab21ad0499d68a79`.

[Lines 481–494](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/cli/cmd/run.ts#L481-L494):

~~~~text
              const part = event.properties.part
              if (part.sessionID !== sessionID) continue

              if (part.type === "tool" && (part.state.status === "completed" || part.state.status === "error")) {
                if (emit("tool_use", { part })) continue
                if (part.state.status === "completed") {
                  tool(part)
                  continue
                }
                inline({
                  icon: "✗",
                  title: `${part.tool} failed`,
                })
                UI.error(part.state.error)
~~~~

## M05 Run reasoning projection

File: [packages/cli/src/cli/cmd/run.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/cli/cmd/run.ts).

SHA-256: `d0eb283ba0f82d6744d839fbed0fbb1f00673743638f7bf2ab21ad0499d68a79`.

[Lines 527–538](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/cli/cmd/run.ts#L527-L538):

~~~~text
              }

              if (part.type === "reasoning" && part.time?.end && args.thinking) {
                if (emit("reasoning", { part })) continue
                const text = part.text.trim()
                if (!text) continue
                const line = `Thinking: ${text}`
                if (process.stdout.isTTY) {
                  UI.empty()
                  UI.println(`${UI.Style.TEXT_DIM}\u001b[3m${line}\u001b[0m${UI.Style.TEXT_NORMAL}`)
                  UI.empty()
                  continue
~~~~

## M06 ACP construction

File: [packages/cli/src/cli/cmd/acp.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/cli/cmd/acp.ts).

SHA-256: `085ff8ea8c93983e1fe9f3fb3c3dbad2a4d4450eeb51ff6b01b57fd2d5edfae4`.

[Lines 26–36](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/cli/cmd/acp.ts#L26-L36):

~~~~text
      // Private HTTP shim for this ACP session's SDK client — not a task-token host.
      // Advertising would hand `issue`/`list` a base_url that only works for callers
      // already inside this process's directory scope.
      const server = await Server.listen({ ...opts, advertise: false })

      const sdk = createOpencodeClient({
        baseUrl: `http://${server.hostname}:${server.port}`,
      })

      const input = new WritableStream<Uint8Array>({
        write(chunk) {
~~~~

## M07 ACP capabilities

File: [packages/cli/src/acp/agent.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/acp/agent.ts).

SHA-256: `c21d2c9dee0d8d5b3ac3222f9c35727917e3ce6488da7cc33b7c6ca8c2f73432`.

[Lines 517–531](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/acp/agent.ts#L517-L531):

~~~~text
      agentCapabilities: {
        loadSession: true,
        mcpCapabilities: {
          http: true,
          sse: true,
        },
        promptCapabilities: {
          embeddedContext: true,
          image: true,
        },
        sessionCapabilities: {
          fork: {},
          list: {},
          resume: {},
        },
~~~~

## M08 ACP prompt forwarding

File: [packages/cli/src/acp/agent.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/acp/agent.ts).

SHA-256: `c21d2c9dee0d8d5b3ac3222f9c35727917e3ce6488da7cc33b7c6ca8c2f73432`.

[Lines 1399–1412](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/acp/agent.ts#L1399-L1412):

~~~~text
      const response = await this.sdk.session.prompt({
        sessionID,
        model: {
          providerID: model.providerID,
          modelID: model.modelID,
        },
        variant: this.sessionManager.getVariant(sessionID),
        parts,
        agent,
        directory,
      })
      const msg = response.data?.info

      await sendUsageUpdate(this.connection, this.sdk, sessionID, directory)
~~~~

## M09 Memory write switch

File: [packages/cli/src/config/config.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/config/config.ts).

SHA-256: `f5eb5062d596fe9cec9df83953a1a0ae08b4728dadce5848985ecbc131604fac`.

[Lines 337–346](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/config/config.ts#L337-L346):

~~~~text
  memory: Schema.optional(
    Schema.Struct({
      disable_write: Schema.optional(Schema.Boolean).annotate({
        description:
          "Stop WRITING new memory. Default: false (memory is written). When true, no new memory is produced — session checkpoint.md, project MEMORY.md, notes.md and per-task progress.md are never written, the high-pressure 'save your learnings to memory' nudge is suppressed, and automatic dream/distill runs are skipped. Existing memory stays READABLE on demand: the builtin `memory` search tool keeps working and the files can still be read directly. What does stop is the AUTOMATIC injection — checkpoint rebuild is short-circuited to compaction while writing is off, and the memory dumps that a rebuild would have placed in context are only produced by that rebuild, so nothing is loaded on its own; an agent that wants memory has to search or read for it. Nothing is ever deleted — set it back to false to resume writing on top of the existing files.",
      }),
      cc_index: Schema.optional(Schema.Boolean).annotate({
        description:
          "Index Claude Code memory (~/.claude/projects/<slug>/memory) and expose under scope='cc'. Default: false. Note: when enabled, every mimocode agent (build/explore/subagents) can search these memories via the builtin `memory` tool — including CC's `type: user` (your role/preferences) and `type: feedback` (your guidance) categories. CC originally writes them for future CC sessions; flipping this on widens the consumer set to mimocode agents on the same machine. Leave disabled (default) if you don't want personal context recallable from a prompt-injection-vulnerable agent.",
      }),
~~~~

## M10 Memory prompt construction

File: [packages/cli/src/session/llm.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/llm.ts).

SHA-256: `8406b460251b8037963269431e9385c799c209d8a4b9dc22baa5babd1cc40b35`.

[Lines 368–379](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/llm.ts#L368-L379):

~~~~text
        // the "agent edits MEMORY.md before any checkpoint" path. Idempotent.
        yield* Effect.promise(() => migrateProjectMemory(projectID)).pipe(Effect.ignore)
        system.push(buildMemoryInstructions(yield* memory.root()))
      }

      // Plugins transform the stable base before the caller-controlled tail.
      yield* plugin.trigger(
        "experimental.chat.system.transform",
        { sessionID: input.sessionID, model: input.model },
        { system },
      )

~~~~

[Lines 349–358](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/llm.ts#L349-L358):

~~~~text
      // Memory-instructions section. Always injected for main/peer actors —
      // memory paths/ownership are independent of checkpoint. The checkpoint
      // flag only narrows which subsections buildMemoryInstructions emits
      // (writer/ckpt/Active-recall extras). Project ID is resolved from the
      // ALS-bound Instance with a safe fallback to `ProjectID.global`
      // (mirrors session/checkpoint.ts) for the MEMORY.md migration only; the
      // block itself names no project. system-spawned actors
      // (checkpoint-writer et al.) stay out via servesCheckpoint.
      if (servesCheckpoint) {
        const projectID =
~~~~

## M11 Native directories

File: [packages/shared/src/global.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/shared/src/global.ts).

SHA-256: `d15f77dabb310176cc9a538faa0487731cdea031f87ea7222d29f7ebb7623562`.

[Lines 27–41](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/shared/src/global.ts#L27-L41):

~~~~text
  const home = env.MIMOCODE_HOME
  if (home) {
    if (!path.isAbsolute(home)) {
      throw new Error(
        `MIMOCODE_HOME must be an absolute path, got: ${JSON.stringify(home)}`,
      )
    }
    return {
      mode: "mimocode_home",
      root: home,
      data: path.join(home, "data"),
      cache: path.join(home, "cache"),
      config: path.join(home, "config"),
      state: path.join(home, "state"),
    }
~~~~

[Lines 36–48](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/shared/src/global.ts#L36-L48):

~~~~text
      root: home,
      data: path.join(home, "data"),
      cache: path.join(home, "cache"),
      config: path.join(home, "config"),
      state: path.join(home, "state"),
    }
  }
  return {
    mode: "xdg",
    data: path.join(xdgData!, APP),
    cache: path.join(xdgCache!, APP),
    config: path.join(xdgConfig!, APP),
    state: path.join(xdgState!, APP),
~~~~

## M12 Native credential store

File: [packages/cli/src/auth/index.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/auth/index.ts).

SHA-256: `e4c4347269cc479dda3033db139e466282b28c2e6d10a53a81b7e3e85ca1b7ab`.

[Lines 9–21](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/auth/index.ts#L9-L21):

~~~~text
const file = path.join(Global.Path.data, "auth.json")

/**
 * Credentials supplied by an embedding host (the desktop app runs the engine in-process).
 *
 * Kept in memory on purpose: the previous channel was `MIMOCODE_AUTH_CONTENT`, and anything in
 * the environment is readable by every child the engine spawns — the bash tool alone turns
 * `echo $MIMOCODE_AUTH_CONTENT` into a credential dump, and a sibling can still read
 * `/proc/<pid>/environ` even after the child's own env is scrubbed. A module-level value has no
 * such surface. The env var is still honored so workspace children keep working (they receive it
 * explicitly), but hosts should prefer `inject`.
 */
let injected: string | undefined
~~~~

[Lines 76–87](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/auth/index.ts#L76-L87):

~~~~text
      const raw = injected ?? process.env.MIMOCODE_AUTH_CONTENT
      if (raw) {
        try {
          return JSON.parse(raw)
        } catch (err) {}
      }

      const data = (yield* fsys.readJson(file).pipe(Effect.orElseSucceed(() => ({})))) as Record<string, unknown>
      return Record.filterMap(data, (value) => Result.fromOption(decode(value), () => undefined))
    })

    const get = Effect.fn("Auth.get")(function* (providerID: string) {
~~~~

## M13 Xiaomi browser authorization

File: [packages/cli/src/plugin/mimo.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/plugin/mimo.ts).

SHA-256: `392c0e2dc5720adf56818a81bd0da7ed6093ae067c6d965471a0ef99cea8d030`.

[Lines 170–184](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/plugin/mimo.ts#L170-L184):

~~~~text
              callback: async (code?: string) => {
                if (code) {
                  try {
                    const result = decrypt(privateKeyDer, code.trim())
                    server.close()
                    const metadata: Record<string, string> = { uid: result.uid }
                    if (result.url) metadata.base_url = result.url
                    return { type: "success" as const, key: result.sk ?? "", metadata }
                  } catch {
                    return { type: "failed" as const }
                  }
                }
                try {
                  const result = await serverCallbackPromise
                  server.close()
~~~~

## M14 Prompt input and persistence

File: [packages/cli/src/session/prompt.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/prompt.ts).

SHA-256: `3d7566c7f663f02c113bde2c8f26dbe82d22e7d88c43c2365a0ff24e872f6cc3`.

[Lines 7722–7736](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/prompt.ts#L7722-L7736):

~~~~text
  system: z
    .string()
    .optional()
    .describe("Additional system prompt selected by the session's first user query. Later values are ignored."),
  systemMode: z
    .enum(["append", "replace-agent"])
    .optional()
    .describe("Whether the selected system prompt appends to or replaces the agent prompt. Later values are ignored."),
  harness: z
    .enum(["auto", "codex", "default"])
    .optional()
    .describe(
      "Harness mode selected by the session's first user query. Later values are ignored. Auto preserves model/process inference and explicit default forces the native tool schema for non-GPT models. MIMOCODE_CODEX_MODE=false forces the default harness for every model, including GPT.",
    ),
  variant: z.string().optional(),
~~~~

## M15 Prompt context role

File: [packages/cli/src/session/llm.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/llm.ts).

SHA-256: `8406b460251b8037963269431e9385c799c209d8a4b9dc22baa5babd1cc40b35`.

[Lines 234–243](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/llm.ts#L234-L243):

~~~~text
export function turnContextMessages(user: MessageV2.User): ModelMessage[] {
  if (user.systemMode === "replace-agent") return []
  const context = user.system?.trim()
  if (!context) return []
  return [{
      role: "user",
      content: `<system-reminder>\n${context}\n</system-reminder>`,
  }]
}

~~~~

## M16 Native history import

File: [packages/cli/src/cli/cmd/import.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/cli/cmd/import.ts).

SHA-256: `43379a2078c5e4a79d365cc499b88f2d6863f3ce2a489360f21678bc53cacf20`.

[Lines 90–103](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/cli/cmd/import.ts#L90-L103):

~~~~text
  const parsed = messages.map((message) => {
    const msg = MessageV2.Info.parse(message.info)
    if (msg.sessionID !== info.id || messageIDs.has(msg.id)) throw new Error(`Invalid imported message: ${msg.id}`)
    messageIDs.add(msg.id)
    const parts = message.parts.map((value) => {
      const part = MessageV2.Part.parse(value)
      if (part.sessionID !== info.id || part.messageID !== msg.id || partIDs.has(part.id))
        throw new Error(`Invalid imported part: ${part.id}`)
      partIDs.add(part.id)
      return part
    }).sort((a, b) => a.id.localeCompare(b.id))
    return { info: { ...msg, agentID: msg.agentID ?? "main" }, parts }
  }).sort((a, b) => a.info.id.localeCompare(b.info.id))
  Database.transaction((tx) => {
~~~~

[Lines 155–159](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/cli/cmd/import.ts#L155-L159):

~~~~text
  command: "import <file>",
  describe: "import session data from JSON or URL without starting runs or transferring live process ownership",
  builder: (yargs: Argv) => {
    return yargs.positional("file", {
      describe: "path to JSON file or share URL",
~~~~

## M17 Completion tracking

File: [packages/cli/src/cli/cmd/run-completion.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/cli/cmd/run-completion.ts).

SHA-256: `6987c2d3015d3b5af3136b1e01426720df9a567dae3db62b1bb159cba16f97ce`.

[Lines 51–55](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/cli/cmd/run-completion.ts#L51-L55):

~~~~text
    }
    if (done || !started) return
    if (!info || info.type === "idle") finish()
  }

~~~~

[Lines 68–75](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/cli/cmd/run-completion.ts#L68-L75):

~~~~text
    onEvent(event) {
      if (done) return
      if (matchesSession(event)) started = true
      if (isIdleStatusForSession(event)) finish()
    },
    get done() { return done },
    completion,
    stop() { finish() },
~~~~

## M18 Bash cancellation

File: [packages/cli/src/tool/bash.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/tool/bash.ts).

SHA-256: `088836392435fa6a45c8d09636e3596170c6cf1334c40e59a27934c659ba918f`.

[Lines 780–794](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/tool/bash.ts#L780-L794):

~~~~text
          const exit = yield* Effect.raceAll([
            handle.exitCode.pipe(Effect.map((code) => ({ kind: "exit" as const, code }))),
            abort.pipe(Effect.map(() => ({ kind: "abort" as const, code: null }))),
            timeout.pipe(Effect.map(() => ({ kind: "timeout" as const, code: null }))),
          ])

          if (exit.kind === "abort") {
            aborted = true
            yield* handle.kill({ forceKillAfter: "3 seconds" }).pipe(Effect.orDie)
          }
          if (exit.kind === "timeout") {
            expired = true
            yield* handle.kill({ forceKillAfter: "3 seconds" }).pipe(Effect.orDie)
          }

~~~~

## M19 Event delivery

File: [packages/cli/src/server/routes/instance/event.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/server/routes/instance/event.ts).

SHA-256: `7d723ed9adce36d5b8eb93ad1ed0b51bcf12087df7f5b191e78548ae4b6a9a5f`.

[Lines 57–64](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/server/routes/instance/event.ts#L57-L64):

~~~~text
        // Bounded buffer: the bus delta firehose (per-token PartDelta) is pushed
        // here synchronously and never blocks the producer. A slow/stalled SSE
        // consumer would otherwise let this grow without limit and exhaust the
        // server's memory. Events are best-effort telemetry (DB is authoritative
        // + heartbeat), so drop-oldest is safe under sustained backpressure.
        const q = new AsyncQueue<string | null>({ capacity: EVENT_QUEUE_CAPACITY })
        let done = false

~~~~

[Lines 103–105](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/server/routes/instance/event.ts#L103-L105):

~~~~text
          if (disposed === directory) stream.abort()
        })
        stream.onAbort(stop)
~~~~

## M20 Retry defaults

File: [packages/cli/src/session/retry.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/retry.ts).

SHA-256: `04debcacbd028724b4826c932ec5f8e82d79bd191878b1895a909c5ef7ebcc5d`.

[Lines 100–114](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/retry.ts#L100-L114):

~~~~text
  // Recoverable kinds wait with exponential backoff — longer wait raises recovery odds.
  // They must NOT be short-circuited by phase=request (product: no phase-based kill window).
  server: {
    mode: "persistent",
    maxElapsedMs: 0,
    initialDelayMs: RETRY_INITIAL_DELAY,
    maxDelayMs: RETRY_MAX_DELAY_NO_HEADERS,
    jitterRatio: RETRY_JITTER_RATIO,
  },
  rateLimit: {
    mode: "persistent",
    maxElapsedMs: 0,
    initialDelayMs: RETRY_INITIAL_DELAY,
    maxDelayMs: RETRY_MAX_DELAY_MESSAGE,
    jitterRatio: RETRY_JITTER_RATIO,
~~~~

[Lines 93–99](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/retry.ts#L93-L99):

~~~~text
  network: {
    mode: "persistent",
    maxElapsedMs: 0,
    initialDelayMs: NETWORK_INITIAL_DELAY_MS,
    maxDelayMs: NETWORK_MAX_DELAY_MS,
    jitterRatio: 0,
  },
~~~~

## M21 Runtime configuration

File: [packages/cli/src/config/config.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/config/config.ts).

SHA-256: `f5eb5062d596fe9cec9df83953a1a0ae08b4728dadce5848985ecbc131604fac`.

[Lines 866–875](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/config/config.ts#L866-L875):

~~~~text
        if (process.env.MIMOCODE_CONFIG_CONTENT) {
          const source = "MIMOCODE_CONFIG_CONTENT"
          const next = yield* loadConfig(process.env.MIMOCODE_CONFIG_CONTENT, {
            dir: ctx.directory,
            source,
          })
          yield* merge(source, next, "local")
          log.debug("loaded custom config from MIMOCODE_CONFIG_CONTENT")
        }

~~~~

## M22 Permission semantics

File: [packages/cli/src/config/config.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/config/config.ts).

SHA-256: `f5eb5062d596fe9cec9df83953a1a0ae08b4728dadce5848985ecbc131604fac`.

[Lines 948–957](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/config/config.ts#L948-L957):

~~~~text
        if (Flag.MIMOCODE_DANGEROUSLY_SKIP_PERMISSIONS) {
          // Allow-all base, merged UNDER user config so an explicit deny still
          // wins. Matches `mimo run --dangerously-skip-permissions`: auto-approve
          // everything not explicitly denied.
          result.permission = mergeDeep({ "*": "allow" } as ConfigPermission.Info, result.permission ?? {})
        }

        if (Flag.MIMOCODE_PERMISSION) {
          result.permission = mergeDeep(result.permission ?? {}, JSON.parse(Flag.MIMOCODE_PERMISSION))
        }
~~~~

## M23 Question bridge

File: [packages/cli/src/server/routes/instance/question.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/server/routes/instance/question.ts).

SHA-256: `ce8788bd3d7d332f3354e493d97d90beac3b9a87e2fe28f40861f3c6a982d6dc`.

[Lines 117–131](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/server/routes/instance/question.ts#L117-L131):

~~~~text
      validator("json", Reply),
      async (c) =>
        jsonRequest("QuestionRoutes.reply", c, function* () {
          const params = c.req.valid("param")
          const json = c.req.valid("json")
          const svc = yield* Question.Service
          yield* svc.reply({
            requestID: params.requestID,
            answers: json.answers,
          })
          return true
        }),
    )
    .post(
      "/:requestID/reject",
~~~~

## M24 Provider catalog

File: [packages/cli/src/server/routes/instance/provider.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/server/routes/instance/provider.ts).

SHA-256: `e5f7459d86bf5bdab75bb3f171bda3a73cee3c1d66e2cea011c037875b60f07d`.

[Lines 50–63](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/server/routes/instance/provider.ts#L50-L63):

~~~~text
          const connected = yield* svc.list()
          const providers = Object.assign(
            mapValues(filtered, (x) => Provider.fromModelsDevProvider(x)),
            connected,
          )
          return {
            all: Object.values(providers),
            default: Provider.defaultModelIDs(providers),
            connected: Object.keys(connected),
            authenticated: Object.keys(yield* auth.all().pipe(Effect.orDie)),
          }
        }),
    )
    .get(
~~~~

## M25 Native event identities

File: [packages/cli/src/session/message-v2.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/message-v2.ts).

SHA-256: `f161a9013523b453a63fa621eeac08d3874c9f0053c97be59cbca8ac9c428c27`.

[Lines 419–432](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/message-v2.ts#L419-L432):

~~~~text
export const ToolStateRunning = z
  .object({
    status: z.literal("running"),
    input: z.record(z.string(), z.any()),
    title: z.string().optional(),
    metadata: z.record(z.string(), z.any()).optional(),
    time: z.object({
      start: z.number(),
    }),
  })
  .meta({
    ref: "ToolStateRunning",
  })
export type ToolStateRunning = z.infer<typeof ToolStateRunning>
~~~~

[Lines 499–511](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/message-v2.ts#L499-L511):

~~~~text
export const ToolPart = PartBase.extend({
  type: z.literal("tool"),
  execution: z.enum(["not-started", "started"]).optional(),
  callID: z.string(),
  tool: z.string(),
  state: ToolState,
  metadata: z.record(z.string(), z.any()).optional(),
}).meta({
  ref: "ToolPart",
})
export type ToolPart = z.infer<typeof ToolPart>

const Base = z.object({
~~~~

## M26 Run cancellation and queued admission

File: [packages/cli/src/server/routes/instance/session.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/server/routes/instance/session.ts).

SHA-256: `44eeabf60bd88f4f5f5a81bfa9a6268add9edefadaf4cb2f657fe656e0ebf705`.

[Lines 527–535](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/server/routes/instance/session.ts#L527-L535):

~~~~text
        const epoch = await runRequest(
          "SessionRoutes.abort",
          c,
          SessionPrompt.Service.use((svc) => svc.cancel(sessionID)),
        )
        return c.json({ ok: true, epoch })
      },
    )
    .post(
~~~~

[Lines 1288–1300](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/server/routes/instance/session.ts#L1288-L1300):

~~~~text
        if (busy) {
          const queued = await runRequest(
            "SessionRoutes.prompt.queue",
            c,
            SessionPrompt.Service.use((svc) => svc.promptAsync({ ...body, sessionID })),
          )
          if (!queued.receiptId) return c.body(null, 204)
          return c.json({
            info: queued.message.info,
            parts: queued.message.parts,
            receiptId: queued.receiptId,
          }, 202)
        }
~~~~

## M27 Public plugin hooks

File: [packages/plugin/src/index.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/plugin/src/index.ts).

SHA-256: `87fc4165ff2edd4e7c7bd348abc6096d04fa5af8e02b3e76ae012f9a934ab320`.

[Lines 465–479](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/plugin/src/index.ts#L465-L479):

~~~~text
  "tool.execute.before"?: (
    input: { tool: string; sessionID: string; callID: string },
    output: { args: any; cancel?: boolean; cancelReason?: string },
  ) => Promise<void>
  "shell.env"?: (
    input: { cwd: string; sessionID?: string; callID?: string },
    output: { env: Record<string, string> },
  ) => Promise<void>
  "tool.execute.after"?: (
    input: { tool: string; sessionID: string; callID: string; args: any },
    output: {
      title: string
      output: string
      metadata: any
    },
~~~~

[Lines 490–498](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/plugin/src/index.ts#L490-L498):

~~~~text
  "experimental.chat.system.transform"?: (
    input: { sessionID?: string; model: Model },
    output: {
      system: string[]
    },
  ) => Promise<void>
  /**
   * Called before session compaction starts. Allows plugins to customize
   * the compaction prompt.
~~~~

## M28 Local account display

File: [packages/cli/src/cli/cmd/providers.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/cli/cmd/providers.ts).

SHA-256: `30758686d421dfb98c8730f33b8830938fe498493766e2a486666ac58dece1e6`.

[Lines 632–646](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/cli/cmd/providers.ts#L632-L646):

~~~~text
export const ProvidersWhoamiCommand = cmd({
  command: "whoami",
  describe: "show current logged-in user info",
  async handler(_args) {
    UI.empty()
    prompts.intro("Current user")
    const info = await AppRuntime.runPromise(
      Effect.gen(function* () {
        const auth = yield* Auth.Service
        return yield* auth.get("xiaomi")
      }),
    )
    if (!info) {
      prompts.log.error("Not logged in. Run `mimo auth login` to log in.")
      return
~~~~

[Lines 648–657](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/cli/cmd/providers.ts#L648-L657):

~~~~text
    if (info.type === "api" && info.metadata) {
      prompts.log.info(`Provider: MiMo`)
      prompts.log.info(`User ID: ${info.metadata.uid ?? "unknown"}`)
    } else {
      prompts.log.info(`Provider: MiMo`)
      prompts.log.info(`Type: ${info.type}`)
    }
    prompts.outro("")
  },
})
~~~~

## M29 Tools map and dispatch

File: [packages/cli/src/session/prompt.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/prompt.ts).

SHA-256: `3d7566c7f663f02c113bde2c8f26dbe82d22e7d88c43c2365a0ff24e872f6cc3`.

[Lines 3722–3730](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/prompt.ts#L3722-L3730):

~~~~text
        const permissions: Permission.Ruleset = []
        for (const [t, enabled] of Object.entries(input.tools ?? {})) {
          permissions.push({ permission: t, action: enabled ? "allow" : "deny", pattern: "*" })
        }
        if (permissions.length > 0) {
          session.permission = permissions
          yield* sessions.setPermission({ sessionID: session.id, permission: permissions })
        }

~~~~

[Lines 2327–2338](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/prompt.ts#L2327-L2338):

~~~~text
      if (searchExposed) {
        input.processor.registerTool(MCP_TOOL_USE_ID)
        tools[MCP_TOOL_USE_ID] = tool({
          description: MCP_TOOL_USE_DESCRIPTION,
          inputSchema: jsonSchema(ProviderTransform.schema(input.model, z.toJSONSchema(McpToolUseParameters))),
          execute(args: z.infer<typeof McpToolUseParameters>, options) {
            const dispatch = mcpDispatch.get(args.name)
            if (dispatch) return dispatch(args.arguments ?? {}, options)
            return run.promise(
              input.processor.executeTool(
                MCP_TOOL_USE_ID,
                options.toolCallId,
~~~~

## M30 Native database concurrency

File: [packages/cli/src/storage/db.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/storage/db.ts).

SHA-256: `0532950904375842d1f372da55234829e2ea01052526e189798026e871f589b7`.

[Lines 90–100](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/storage/db.ts#L90-L100):

~~~~text
  // The WAL pragma itself takes a lock. Install the busy handler first so
  // simultaneous engine connections do not fail before reaching title CAS.
  db.run("PRAGMA busy_timeout = 5000")
  db.run("PRAGMA journal_mode = WAL")
  db.run("PRAGMA synchronous = NORMAL")
  db.run("PRAGMA cache_size = -64000")
  db.run("PRAGMA foreign_keys = ON")
  db.run("PRAGMA wal_checkpoint(PASSIVE)")

  // Schema = sum of migration/*.sql. The runner only treats ALTER ADD/DROP
  // and CREATE INDEX replay-safe no-ops as already-applied on a desynced journal.
~~~~

## M31 Native detached shell groups

File: [packages/cli/src/tool/bash.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/tool/bash.ts).

SHA-256: `088836392435fa6a45c8d09636e3596170c6cf1334c40e59a27934c659ba918f`.

[Lines 444–455](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/tool/bash.ts#L444-L455):

~~~~text
  const finalCommand =
    process.platform === "win32" && name === "cmd" ? `${Shell.CMD_UTF8_PREFIX}${command}` : command

  return ChildProcess.make(finalCommand, [], {
    shell,
    cwd,
    env,
    stdin: "ignore",
    detached: process.platform !== "win32",
  })
}

~~~~

## M32 Conditional durable event storage

File: [packages/cli/src/sync/index.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/sync/index.ts).

SHA-256: `b032db5167442291147f7a19cded4d002f1dc5a40c42ff90fca4d23cceb4f146`.

[Lines 119–133](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/sync/index.ts#L119-L133):

~~~~text
    if (Flag.MIMOCODE_EXPERIMENTAL_WORKSPACES || options.replay) {
      tx.insert(EventSequenceTable)
        .values({
          aggregate_id: event.aggregateID,
          seq: event.seq,
        })
        .onConflictDoUpdate({
          target: EventSequenceTable.aggregate_id,
          set: { seq: event.seq },
        })
        .run()
      tx.insert(EventTable)
        .values({
          id: event.id,
          seq: event.seq,
~~~~

## M33 Native frozen prompt prefix

File: [packages/cli/src/session/prompt.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/prompt.ts).

SHA-256: `3d7566c7f663f02c113bde2c8f26dbe82d22e7d88c43c2365a0ff24e872f6cc3`.

[Lines 6016–6030](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/prompt.ts#L6016-L6030):

~~~~text
                const prebuiltSystem = resolvedPrefix.prefix.system
                const modelMsgs = resolvedPrefix.prefix.inheritedMessages
                lastSystemPrompt = prebuiltSystem
                const cfg = yield* config.get()
                const maxModeCfg = cfg.experimental?.maxMode
                const useMaxMode =
                  agent.name === MaxMode.MAX_MODE_AGENT && maxModeCfg !== undefined && format.type !== "json_schema"

                const processArgs = {
                  user: lastUser,
                  agent,
                  permission: session.permission,
                  sessionID,
                  parentSessionID: session.parentID,
                  system: [],
~~~~

## M34 Memory and all-tool cancellation hooks

File: [packages/cli/src/session/prompt.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/prompt.ts).

SHA-256: `3d7566c7f663f02c113bde2c8f26dbe82d22e7d88c43c2365a0ff24e872f6cc3`.

[Lines 1962–1976](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/prompt.ts#L1962-L1976):

~~~~text
                const beforeOutput: { args: any; cancel?: boolean; cancelReason?: string } = { args }
                yield* plugin.trigger(
                  "tool.execute.before",
                  { tool: item.id, sessionID: ctx.sessionID, callID: ctx.callID },
                  beforeOutput,
                )
                if (beforeOutput.cancel) {
                  gate.fail(gateTool)
                  const cancelOutput = {
                    title: "Cancelled",
                    output: beforeOutput.cancelReason || "Tool call cancelled by hook",
                    metadata: { cancelled: true },
                  }
                  yield* bus
                    .publish(Metrics.ToolCall, {
~~~~

## M35 Public event subscription

File: [packages/cli/src/plugin/index.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/plugin/index.ts).

SHA-256: `187121e5588fb4c00184de9745b19f038c6d95f035b71f20f2873840632d6c64`.

[Lines 370–384](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/plugin/index.ts#L370-L384):

~~~~text
        // Subscribe to bus events, fiber interrupted when scope closes
        yield* bus.subscribeAll().pipe(
          Stream.runForEach((input) =>
            Effect.sync(() => {
              for (const hook of hooks) {
                if (!isHookObject(hook)) continue
                void hook["event"]?.({ event: input as any })
              }
            }),
          ),
          Effect.forkScoped,
        )

        return { hooks, hooksWithMeta }
      }),
~~~~

## M36 Durable event catch-up

File: [packages/cli/src/server/routes/instance/sync.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/server/routes/instance/sync.ts).

SHA-256: `91ac9f9288652564a877faa94ef977483879ecf83ad88c464d431933569d898d`.

[Lines 177–187](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/server/routes/instance/sync.ts#L177-L187):

~~~~text
        const body = c.req.valid("json")
        const exclude = Object.entries(body)
        const where =
          exclude.length > 0
            ? not(or(...exclude.map(([id, seq]) => and(eq(EventTable.aggregate_id, id), lte(EventTable.seq, seq))))!)
            : undefined
        const rows = Database.use((db) => db.select().from(EventTable).where(where).orderBy(asc(EventTable.seq)).all())
        return c.json(rows)
      },
    ),
)
~~~~

## M37 Actor history slices

File: [packages/cli/src/server/routes/instance/session.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/server/routes/instance/session.ts).

SHA-256: `44eeabf60bd88f4f5f5a81bfa9a6268add9edefadaf4cb2f657fe656e0ebf705`.

[Lines 820–832](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/server/routes/instance/session.ts#L820-L832):

~~~~text
        // Default to main-agent slice when omitted; `"*"` and explicit
        // actorIDs forward verbatim to Session.messages, which now owns the
        // slice contract.
        const agentID = query.agent_id ?? "main"

        if (query.limit === undefined || query.limit === 0) {
          const messages = await runRequest(
            "SessionRoutes.messages",
            c,
            Effect.gen(function* () {
              const session = yield* Session.Service
              yield* session.get(sessionID)
              return yield* session.messages({ sessionID, agentID, limit: 1000 })
~~~~

## M38 Actor inventory

File: [packages/cli/src/server/routes/instance/session.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/server/routes/instance/session.ts).

SHA-256: `44eeabf60bd88f4f5f5a81bfa9a6268add9edefadaf4cb2f657fe656e0ebf705`.

[Lines 1631–1643](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/server/routes/instance/session.ts#L1631-L1643):

~~~~text
      "/:sessionID/actors",
      describeRoute({
        summary: "List session actors",
        description: "List actors with execution status in this server runtime; persisted outcomes are preserved.",
        operationId: "session.actors",
        responses: {
          200: {
            description: "Actor list",
          },
          ...errors(400, 404),
        },
      }),
      validator(
~~~~

## M39 Prefix snapshot persistence

File: [packages/cli/src/session/prefix-snapshot.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/prefix-snapshot.ts).

SHA-256: `82eb1dfeac8263acbcaacf1719eb9e414b5ebfe880c5024b76bc00007ae66344`.

[Lines 115–129](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/prefix-snapshot.ts#L115-L129):

~~~~text
  yield* Effect.sync(() =>
    Database.use((db) =>
      db
        .insert(SessionPrefixSnapshotTable)
        .values({
          session_id: input.sessionID,
          profile_key: input.profileKey,
          system: input.system,
          system_hash: systemHash(input.system),
          tools_hash: input.toolsHash,
          tools: input.tools,
          watermark_message_id: input.watermarkMessageID,
          revision: 1,
          created_at: now,
          updated_at: now,
~~~~

## M40 MCP dispatch availability

File: [packages/cli/src/session/prompt.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/prompt.ts).

SHA-256: `3d7566c7f663f02c113bde2c8f26dbe82d22e7d88c43c2365a0ff24e872f6cc3`.

[Lines 2076–2087](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/prompt.ts#L2076-L2087):

~~~~text
        const available =
          input.tools?.[key] !== false &&
          !disabledMcpTools.has(key) &&
          (!agentToolAllowlist || agentToolAllowlist.has(key))
        const searchable = available && (!whitelist || whitelist.has(key))
        const entry: McpToolSearchEntry | undefined = searchable
          ? { name: key, description: item.description ?? "", parameters: transformed as unknown as JSONObject }
          : undefined
        if (entry) mcpSearchEntries.push(entry)
        // `batch` is the model-facing tool part this call executes under: the MCP
        // tool itself for a direct call, `mcp_tool_use` for a dispatched one, and
        // undefined for exec guest calls (script-controlled concurrency).
~~~~

## M42 Memory search independent of write control

File: [packages/cli/src/memory/service.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/memory/service.ts).

SHA-256: `5fadc62b0ce14417ca09b306790cf20fb28ee58e0f07d03555d8fad0dfdf8e0a`.

[Lines 52–66](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/memory/service.ts#L52-L66):

~~~~text
    const search = Effect.fn("Memory.search")(function* (input: {
      query: string
      scope?: string
      scope_id?: string
      type?: string
      limit?: number
    }) {
      // Lazy reconcile before search (covers off-tool writes); honour config flag.
      const cfg = yield* config.get()
      if (cfg.checkpoint?.memory_reconcile_on_search ?? true) {
        const cc = cfg.memory?.cc_index ? ccBase : undefined
        yield* Effect.promise(() => reconcileMemory({ mimo: root, cc }))
      }

      const limit = input.limit ?? 10
~~~~

## M43 Official non-inference model catalog

Source: [Xiaomi List Models](https://mimo.mi.com/docs/en-US/api/model/list-models),
read 27 October 2026. The official reference documents authenticated GET
`https://api.xiaomimimo.com/v1/models`, accepting an API-key or Bearer header,
and a list of model identifiers. It is a catalog request, not generation.
This documents the endpoint; observations with the native credential and an
invalid control are private runtime material, not part of this source snapshot.

## M44 Official allowance and billing distinction

Sources: [MiMo Code integration](https://mimo.mi.com/docs/en-US/tokenplan/integration/mimo-code),
[API integration FAQ](https://mimo.mi.com/docs/en-US/quick-start/faq/api-integration),
and [Token Plan](https://mimo.mi.com/docs/tokenplan/subscription), read
27 October 2026. The browser authorization creates a CLI-specific API key for
pay-as-you-go use. Token Plan has separate credentials, endpoint and allowance;
its quota and expiry are shown in the platform's Token Plan page. These pages
do not document a programmatic remaining-allowance endpoint. This scoped
observation is not a claim that no internal console endpoint exists.
## M41 Variant provider options

File: [packages/cli/src/session/llm.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/llm.ts).

SHA-256: `8406b460251b8037963269431e9385c799c209d8a4b9dc22baa5babd1cc40b35`.

[Lines 434–448](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/session/llm.ts#L434-L448):

~~~~text
      const variant =
        !input.small && input.model.variants && input.user.model.variant
          ? input.model.variants[input.user.model.variant]
          : {}
      const base = input.small
        ? ProviderTransform.smallOptions(input.model)
        : ProviderTransform.options({
            model: input.model,
            sessionID: input.sessionID,
            providerOptions: item.options,
          })
      const options: Record<string, any> = pipe(
        base,
        mergeDeep(input.model.options),
        mergeDeep(input.agent.options),
~~~~


## M45 Native shell environment selection

File: [packages/cli/src/shell/shell.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/shell/shell.ts).

SHA-256: `3cab612f6c18381c50fc658f9f26d71c463ffb4c58a6cee214c2afc6fcf8ac10`.

[Lines 106–111](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/shell/shell.ts#L106-L111):

~~~~text
}

export const preferred = lazy(() => select(process.env.SHELL))

export const acceptable = lazy(() => select(process.env.SHELL, { acceptable: true }))

~~~~

## M46 Native command-scoped shell environment hook

File: [packages/cli/src/tool/bash.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/tool/bash.ts).

SHA-256: `088836392435fa6a45c8d09636e3596170c6cf1334c40e59a27934c659ba918f`.

[Lines 648–653](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/tool/bash.ts#L648-L653):

~~~~text
    const shellEnv = Effect.fn("BashTool.shellEnv")(function* (ctx: Tool.Context, cwd: string) {
      const extra = yield* plugin.trigger(
        "shell.env",
        { cwd, sessionID: ctx.sessionID, callID: ctx.callID },
        { env: {} },
      )
~~~~

## M47 Native original-command permission scan

File: [packages/cli/src/tool/bash.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/tool/bash.ts).

SHA-256: `088836392435fa6a45c8d09636e3596170c6cf1334c40e59a27934c659ba918f`.

[Lines 935–947](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/tool/bash.ts#L935-L947):

~~~~text
              const autoApproveDelete =
                scan.deletes.size > 0 && ctx.autoApproveDelete ? yield* ctx.autoApproveDelete() : false
              const skipDeleteAsk = scan.deletes.size === 0 || (yield* tmpOnlyDelete(root, cwd, ps, shell))
              if (!skipDeleteAsk) {
                yield* askDelete(ctx, scan, params.command)
                if (autoApproveDelete) yield* ask(ctx, scan)
              } else {
                yield* ask(ctx, scan)
              }

              // Interactive mode: hand terminal to user for direct interaction
              if (params.interactive) {
                const env = yield* shellEnv(ctx, cwd)
~~~~

## M48 Effect process spawner defaults to detached groups

File: [packages/cli/src/effect/cross-spawn-spawner.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/effect/cross-spawn-spawner.ts).

SHA-256: `73b0bf8c5774cd49354261584ee4cd61c8626f6fbe82ddeec1049b8d0792a16f`.

[Lines 375–383](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/effect/cross-spawn-spawner.ts#L375-L383):

~~~~text
          const [proc, signal] = yield* Effect.acquireRelease(
            spawn(command, {
              cwd: dir,
              env: env(command.options),
              stdio: stdios(sin, sout, serr, extra),
              detached: command.options.detached ?? process.platform !== "win32",
              shell: command.options.shell,
              windowsHide: process.platform === "win32",
            }),
~~~~

## M49 Public formatter command override

File: [packages/cli/src/format/index.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/format/index.ts).

SHA-256: `55b9603fb1b858757f7343417073e70fb9a492638c55cb4eab23a9afac765991`.

[Lines 150–157](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/format/index.ts#L150-L157):

~~~~text
            const info = mergeDeep(builtIn ?? { extensions: [] }, item)

            formatters[name] = {
              ...info,
              name,
              extensions: info.extensions ?? [],
              enabled: builtIn && !info.command ? builtIn.enabled : async (_context) => info.command ?? false,
            }
~~~~

## M50 Public language-server command override

File: [packages/cli/src/lsp/lsp.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/lsp/lsp.ts).

SHA-256: `d2ea61e46d4696920366c4f8f59cc54f5f948bbdadf35ec855d0915abd3d468d`.

[Lines 187–198](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/lsp/lsp.ts#L187-L198):

~~~~text
              servers[name] = {
                ...existing,
                id: name,
                root: existing?.root ?? (async (_file, ctx) => ctx.directory),
                extensions: item.extensions ?? existing?.extensions ?? [],
                spawn: async (root) => ({
                  process: lspspawn(item.command[0], item.command.slice(1), {
                    cwd: root,
                    env: item.env,
                  }),
                  initialization: item.initialization,
                }),
~~~~

## M51 Public auth loader interface

Inspected 28 October 2026 at the same pinned native revision. This establishes
a public integration surface, not a qualified Mimo Driver credential-snapshot
implementation or account-race result.

File: [packages/plugin/src/index.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/plugin/src/index.ts).

SHA-256: `87fc4165ff2edd4e7c7bd348abc6096d04fa5af8e02b3e76ae012f9a934ab320`.

[Lines 89–99](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/plugin/src/index.ts#L89-L99):

~~~~text
export type AuthHook = {
  provider: string
  loader?: (auth: () => Promise<Auth>, provider: Provider) => Promise<Record<string, any>>
  methods: (
    | {
        type: "oauth"
        label: string
        prompts?: Array<
          | {
              type: "text"
              key: string
~~~~

## M52 Provider auth loader composition

Inspected 28 October 2026 at the same pinned native revision. This establishes
a public integration surface, not a qualified Mimo Driver credential-snapshot
implementation or account-race result.

File: [packages/cli/src/provider/provider.ts](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/provider/provider.ts).

SHA-256: `8e3d007be9c22acd96a8bf905e6606491f8506b65559de23c95230d904781dea`.

[Lines 1480–1488](https://github.com/XiaomiMiMo/MiMo-Code/blob/b8dbe084ed8e77be2f75a85a9c880031aed699c9/packages/cli/src/provider/provider.ts#L1480-L1488):

~~~~text
          const options = yield* Effect.promise(() =>
            plugin.auth!.loader!(
              () => bridge.promise(auth.get(providerID).pipe(Effect.orDie)) as any,
              catalog,
            ),
          )
          const opts = options ?? {}
          const patch: Partial<Info> = providers[providerID] ? { options: opts } : { source: "custom", options: opts }
          mergeProvider(providerID, patch)
~~~~
