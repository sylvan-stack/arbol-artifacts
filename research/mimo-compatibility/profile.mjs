import fs from 'node:fs';

// Probe-only integration through public plugin hooks. Native code is unmodified.
export default async function MimoCompatibilityProfile() {
  let sequence = 0;
  const mode = () => {
    try { return JSON.parse(fs.readFileSync(process.env.ARBOL_MIMO_PROBE_MODE, 'utf8')); }
    catch { return {}; }
  };
  const log = (kind, data) => fs.appendFileSync(process.env.ARBOL_MIMO_PROBE_HOOK_LOG,
    JSON.stringify({ kind, data, at: Date.now() }) + '\n');
  log('loaded', { pid: process.pid });
  return {
    event: async ({ event }) => log('native_event', { seq: ++sequence, event }),
    'experimental.chat.system.transform': async (_, out) => {
      const m = mode();
      if (m.memoryOff) {
        const retained = out.system.filter(s => !s.startsWith('# Memory system\n'));
        out.system.splice(0, out.system.length, ...retained);
      }
      if (m.context) out.system.push(m.context);
      log('system', { memoryOff: !!m.memoryOff, context: m.context || null });
    },
    'experimental.chat.messages.transform': async (_, out) => {
      if (!mode().memoryOff) return;
      for (const message of out.messages) {
        message.parts = message.parts.filter(p => !(p.type === 'text' &&
          p.text.startsWith('<system-reminder>\nMemory paths for this conversation')));
      }
    },
    'tool.execute.before': async (input, out) => {
      const m = mode();
      if (m.noTools || (m.memoryOff && input.tool === 'memory')) {
        out.cancel = true;
        out.cancelReason = 'Arbol compatibility profile: native tool execution disabled for this probe';
      }
      log('before', { ...input, cancelled: !!out.cancel });
    },
    'tool.execute.after': async (input) => log('after', input),
    'shell.env': async (input, out) => {
      if (process.env.ARBOL_MIMO_BRIDGE_ENDPOINT) {
        out.env.ARBOL_MIMO_BRIDGE_CALL = JSON.stringify(input);
        // Positive control: native shell.env extensions reach the actual command.
        out.env.MIMO_SHELL_ENV_SENTINEL = 'native-shell-env-preserved';
      }
    },
  };
}
