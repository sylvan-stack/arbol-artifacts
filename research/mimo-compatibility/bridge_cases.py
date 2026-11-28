"""Adversarial native Mimo checks for the command-group ownership bridge."""
import json
import os
from pathlib import Path
import shlex
import signal
import subprocess
import sys
import time

from bridge import admin, group_members, recover


def read(path):
    return json.loads(path.read_text())


def events(n):
    path = n.bridge_root / 'bridge-events.jsonl'
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def guards(n, category='bash'):
    return {key: x for key, x in read(n.bridge_root / 'ledger.json')['resources'].items()
            if x.get('category') == category}


def fixture(n, name, *, ignore=False, double=False):
    script = n.work / (name + '.py')
    pidfile = n.work / (name + '.pid')
    release = n.work / (name + '.release')
    script.write_text('import os,time,signal\nfrom pathlib import Path\n' +
        ('if os.fork(): os._exit(0)\nif os.fork(): os._exit(0)\n' if double else '') +
        ('signal.signal(signal.SIGTERM,signal.SIG_IGN)\n' if ignore else '') +
        'Path(' + repr(str(pidfile)) + ').write_text(str(os.getpid()))\n' +
        'while not Path(' + repr(str(release)) + ').exists(): time.sleep(.02)\n' +
        'print(' + repr('tail-' + name) + ',flush=True)\n')
    return shlex.join([sys.executable, str(script)]), pidfile, release


def cleanup_check(n, checks, name):
    from run import alive
    n.close()
    final = read(n.bridge_root / 'terminal.json')
    endpoint = read(n.bridge_root / 'endpoint.json')
    checks.add(name, final['clean'] and not any(final['groups'].values()) and
               not alive(endpoint['owner']['pid']) and not alive(endpoint['watcher']['pid']) and
               not Path(endpoint['socket']).exists(), final)
    return final


def bridge_background(root, peer, checks):
    from run import Native, wait_for, all_tool_parts, alive
    n = Native(root / 'native', peer, bridge=True)
    try:
        n.set_mode(memoryOff=True)
        for name, double, redirected in [('background', False, True), ('double_fork', True, True), ('late_output', False, False)]:
            command, pidfile, release = fixture(n, name, double=double)
            command += (' </dev/null >/dev/null 2>&1' if redirected else '') + ' &\nprintf "parent-exited\\n"'
            future = n.async_prompt(name, [{'calls': [('bash', {'command': command, 'description': name})]}])
            pid = int(wait_for(lambda: pidfile.read_text() if pidfile.exists() else None))
            key = wait_for(lambda: next((k for k, x in guards(n).items()
                                        if x['pgid'] == os.getpgid(pid)), None))
            wait_for(lambda: any(e['kind'] == 'guard_shell_exit' and e['key'] == key for e in events(n)))
            snapshot = events(n)
            checks.add(name + '_held_after_immediate_shell_exit', alive(pid) and not future.done() and
                       len(peer.records_for(name)) == 1 and not any(e['kind'] == 'released' and e['key'] == key for e in snapshot),
                       {'pid': pid, 'group': os.getpgid(pid), 'key': key})
            resource = guards(n)[key]
            calls = [e for e in snapshot if e.get('key') == key]
            published = {e['key']: e['seq'] for e in snapshot if e['kind'] == 'published'}
            admissions = [e for e in calls if e['kind'] == 'admitted']
            checks.add(name + '_published_before_execution', len(admissions) == 3 and
                       published[key] < admissions[0]['seq'] and
                       published[key + ':group_anchor'] < admissions[1]['seq'] and
                       published[key + ':shell'] < admissions[2]['seq'] and
                       bool(resource['call'].get('sessionID')) and bool(resource['call'].get('callID')), calls)
            release.touch()
            result = future.result(12)
            parts = all_tool_parts(n, result)
            checks.add(name + '_release_precedes_native_continuation', not alive(pid) and not group_members(resource['pgid']) and
                       any(e['kind'] == 'released' and e['key'] == key and e['empty'] and e['closed'] for e in events(n)))
            if not redirected:
                checks.add('background_late_output_preserved', any('tail-' + name in p['state'].get('output', '') for p in parts))
        cleanup_check(n, checks, 'background_full_support_cleanup')
    finally:n.close()


def bridge_cancel(root, peer, checks):
    from run import Native, wait_for, alive
    n = Native(root / 'native', peer, bridge=True)
    try:
        n.set_mode(memoryOff=True)
        for name, timeout in [('cancel', False), ('timeout', True)]:
            background, bgfile, _ = fixture(n, name + '_background', ignore=True)
            foreground, fgfile, _ = fixture(n, name + '_foreground', ignore=True)
            command = background + ' </dev/null >/dev/null 2>&1 &\n' + foreground
            sid = n.session()['id']
            arguments = {'command': command, 'description': name}
            if timeout:arguments['timeout'] = 800
            future = n.async_prompt(name, [{'calls': [('bash', arguments)]}], session=sid)
            pids = [int(wait_for(lambda file=file: file.read_text() if file.exists() else None)) for file in (bgfile, fgfile)]
            pgid = os.getpgid(pids[0])
            start = time.monotonic()
            if not timeout:n.api('/session/' + sid + '/abort', {})
            future.result(12)
            wait_for(lambda: not group_members(pgid), seconds=8)
            elapsed = time.monotonic() - start
            checks.add(name + '_kills_term_ignoring_foreground_and_background', not any(alive(p) for p in pids) and elapsed < 8,
                       {'pids': pids, 'group': pgid, 'elapsed': elapsed})
            checks.add(name + '_release_is_acknowledged', any(e['kind'] == 'released' and e['empty'] and e['closed'] and
                       guards(n)[e['key']]['pgid'] == pgid for e in events(n) if e.get('key') in guards(n)))
        cleanup_check(n, checks, 'cancel_full_support_cleanup')
    finally:n.close()


def bridge_death(root, peer, checks):
    from run import Native, wait_for, alive, stop
    n = Native(root / 'native', peer, bridge=True)
    unrelated_script = n.work / 'unrelated.py'
    unrelated_script.write_text('import time\ntime.sleep(45)\n')
    unrelated = subprocess.Popen([sys.executable, str(unrelated_script)], start_new_session=True)
    try:
        n.set_mode(memoryOff=True)
        bg, bgfile, _ = fixture(n, 'death_background', ignore=True)
        fg, fgfile, _ = fixture(n, 'death_foreground', ignore=True)
        future = n.async_prompt('controller_death', [{'calls': [('bash', {'command': bg + ' </dev/null >/dev/null 2>&1 &\n' + fg,
                                                                      'description': 'Controller death'})]}])
        pids = [int(wait_for(lambda file=file: file.read_text() if file.exists() else None)) for file in (bgfile, fgfile)]
        wait_for(lambda: n.output.joinpath('mcp.pid').exists())
        mcp_pid = int((n.output / 'mcp.pid').read_text())
        ledger = read(n.bridge_root / 'ledger.json')
        native = next(x['owner']['pid'] for k, x in ledger['resources'].items()
                      if k.endswith(':shell') and ledger['resources'][k[:-6]].get('category') == 'native')
        os.kill(n.process.pid, signal.SIGKILL);n.process.wait(4)
        start = time.monotonic()
        recovery = recover(n.bridge_root)
        checks.add('controller_sigkill_cleans_native_background_foreground_and_mcp',
                   recovery['clean'] and not any(alive(p) for p in [*pids, native, mcp_pid]),
                   {'pids': pids, 'native': native, 'mcp': mcp_pid, 'elapsed': time.monotonic() - start, 'recovery': recovery})
        checks.add('controller_death_preserves_unrelated_group', unrelated.poll() is None)
        audit = read(n.bridge_root / 'observations.json')
        checks.add('independent_watcher_retains_microsecond_identities', audit['terminal'] and audit['clean'] and
                   all('.' in member['startedAt'] for g in audit['groups'].values() for member in g['members']), audit)
        try:future.result(5)
        except Exception:pass
    finally:
        stop(unrelated);n.close()


def bridge_faults(root, peer, checks):
    from run import Native, wait_for, alive
    for target in ('guard', 'anchor'):
        n = Native(root / target, peer, bridge=True)
        try:
            n.set_mode(memoryOff=True)
            command, pidfile, _ = fixture(n, target + '_fault', ignore=True)
            future = n.async_prompt(target + '_fault', [{'calls': [('bash', {'command': command, 'description': target + ' loss'})]}])
            pid = int(wait_for(lambda: pidfile.read_text() if pidfile.exists() else None))
            key = wait_for(lambda: next(iter(guards(n)), None))
            resource_key = key if target == 'guard' else key + ':group_anchor'
            victim = read(n.bridge_root / 'ledger.json')['resources'][resource_key]['owner']['pid']
            os.kill(victim, signal.SIGKILL)
            wait_for(lambda: not alive(pid), seconds=8)
            wait_for(lambda: (n.bridge_root / 'terminal.json').exists(), seconds=12)
            final = cleanup_check(n, checks, target + '_death_cleans_all_groups')
            checks.add(target + '_death_cannot_acknowledge_success', not final['successful'],
                       {'victim': victim, 'work': pid, 'terminal': final})
            try:future.result(4)
            except Exception:pass
        finally:n.close()


def bridge_races(root, peer, checks):
    from run import Native, wait_for, alive
    for action in ('seal', 'death'):
        n = Native(root / action, peer, bridge=True)
        try:
            n.set_mode(memoryOff=True)
            # Ensure support bootstrap has completed before pausing new shells.
            n.prompt(action + '_ready')
            gate = n.bridge_root / 'pause-admit_shell';gate.touch()
            marker = n.work / 'not-admitted.txt'
            command = 'printf admitted > ' + shlex.quote(str(marker))
            future = n.async_prompt(action + '_race', [{'calls': [('bash', {'command': command, 'description': 'Admission race'})]}])
            paused = wait_for(lambda: read(n.bridge_root / 'paused.json') if (n.bridge_root / 'paused.json').exists() else None)
            ledger = read(n.bridge_root / 'ledger.json')
            shell = ledger['resources'][paused['key'] + ':shell']
            checks.add(action + '_shell_is_registered_but_gated', alive(shell['owner']['pid']) and not marker.exists() and shell['state'] == 'prepared', shell)
            if action == 'seal':
                current = admin(n.bridge_root / 'endpoint.json', 'status')
                busy = admin(n.bridge_root / 'endpoint.json', 'seal', watermark=current['seq'])
                checks.add('completion_seal_rejects_pending_admission', not busy['sealed'] and busy['reason'] == 'work_pending')
                result = admin(n.bridge_root / 'endpoint.json', 'freeze')
                checks.add('seal_closes_admission_at_recorded_watermark', not result['admission'] and result['seq'] >= ledger['seq'])
                gate.unlink()
                future.result(12)
                checks.add('seal_racing_shell_never_executes', not marker.exists() and
                           any(e['kind'] == 'admission_rejected' and e['key'] == paused['key'] for e in events(n)))
                # Native still runs; a further command cannot acquire a guard.
                before = len(guards(n))
                try:n.prompt('after_seal', [{'calls': [('bash', {'command': command, 'description': 'After seal'})]}])
                except (OSError, RuntimeError):pass
                checks.add('post_seal_launch_fails_closed', not marker.exists() and len(guards(n)) == before and
                           any(e['kind'] == 'fault' and e.get('message') == 'bridge admission closed' for e in events(n)))
                cleanup_check(n, checks, 'sealed_run_support_cleanup')
            else:
                os.kill(n.process.pid, signal.SIGKILL);n.process.wait(4)
                recovery = recover(n.bridge_root)
                checks.add('controller_death_before_ack_never_executes', not marker.exists() and recovery['clean'], recovery)
                try:future.result(5)
                except Exception:pass
        finally:n.close()


def bridge_support(root, peer, checks):
    from run import Native, wait_for, alive, all_tool_parts
    n = Native(root / 'native', peer, bridge=True)
    try:
        n.set_mode(memoryOff=True)
        command = 'printf "%s|%s|%s\\n" "$PWD" "$SHELL" "$MIMO_SHELL_ENV_SENTINEL"; printf "quoted:$value; `literal`\\n"; printf err >&2; exit 7'
        # Single quotes make shell metacharacters literal, exactly as on native Bash.
        command = command.replace('printf "quoted:$value; `literal`\\n"', "printf 'quoted:$value; `literal`\\n'")
        result = n.prompt('semantics', [{'calls': [('bash', {'command': command, 'description': 'Command semantics'})]}])
        parts = all_tool_parts(n, result)
        part = next(p for p in parts if p['tool'] == 'bash')
        checks.add('native_command_input_output_cwd_shell_env_and_exit_preserved', part['state']['input']['command'] == command and
                   part['state']['metadata']['exit'] == 7 and str(n.work) + '|/bin/bash|native-shell-env-preserved' in part['state']['output'] and
                   'quoted:$value; `literal`' in part['state']['output'] and 'err' in part['state']['output'], part)
        denied = n.work / 'denied.txt'
        before = len(guards(n))
        n.prompt('denied', [{'calls': [('bash', {'command': 'touch ' + shlex.quote(str(denied)), 'description': 'Denied fixture'})]}], tools={'bash': False})
        checks.add('native_tool_permission_denial_precedes_bridge', not denied.exists() and len(guards(n)) == before)
        n.prompt('mcp_owned', [{'calls': [('mcp_tool_search', {'query': 'fixture echo'})]},
                              {'calls': [('mcp_tool_use', {'name': 'fixture_echo', 'arguments': {'text': 'owned-support'}})]}])
        mcp_pid = int(wait_for(lambda: (n.output / 'mcp.pid').read_text() if (n.output / 'mcp.pid').exists() else None))
        checks.add('native_mcp_is_owned_support_after_main_answer', alive(mcp_pid) and len(guards(n, 'mcp')) == 1 and
                   (n.output / 'mcp.calls').exists(), {'pid': mcp_pid, 'guards': guards(n, 'mcp')})
        cleanup_check(n, checks, 'support_final_requires_mcp_and_native_reap')
        checks.add('mcp_ignoring_stdin_eof_is_gone', not alive(mcp_pid))
    finally:n.close()


def bridge_actors(root, peer, checks):
    from run import Native, wait_for, alive
    n = Native(root / 'native', peer, bridge=True)
    try:
        n.set_mode(memoryOff=True)
        command, pidfile, _ = fixture(n, 'actor_background', ignore=True)
        peer.plan('owned_child', [{'calls': [('bash', {'command': command + ' </dev/null >/dev/null 2>&1 &',
                                                       'description': 'Actor background'})]}])
        sid = n.session()['id']
        future = n.async_prompt('owned_root', [{'calls': [('actor', {'operation': {'action': 'spawn',
            'description': 'Owned actor', 'prompt': 'CASE:owned_child', 'subagent_type': 'general'}})]}], session=sid)
        pid = int(wait_for(lambda: pidfile.read_text() if pidfile.exists() else None))
        key = next(k for k, v in guards(n).items() if v['pgid'] == os.getpgid(pid))
        wait_for(lambda: len(peer.records_for('owned_root')) >= 2)
        actors = n.api('/session/' + sid + '/actors')
        checks.add('root_answer_with_live_actor_is_only_a_candidate', alive(pid) and
                   guards(n)[key]['state'] == 'admitted' and any(x.get('actorID') != 'main' and
                   x.get('status') in ('running', 'pending') for x in actors), actors)
        messages = n.api('/session/' + sid + '/message?agent_id=*')
        call = guards(n)[key]['call']
        matching = [m for m in messages if m['info'].get('agentID') not in (None, 'main') and
                    any(p.get('callID') == call.get('callID') for p in m['parts'])]
        checks.add('actor_command_retains_session_and_child_call_lineage', call.get('sessionID') == sid and bool(matching))
        n.api('/session/' + sid + '/abort', {})
        wait_for(lambda: not alive(pid), seconds=8)
        future.result(12)
        wait_for(lambda: not group_members(guards(n)[key]['pgid']), seconds=8)
        checks.add('session_abort_cleans_actor_background_group', not group_members(guards(n)[key]['pgid']))
        cleanup_check(n, checks, 'actor_full_support_cleanup')
    finally:n.close()


def bridge_resources(root, peer, checks):
    from run import Native, wait_for, alive
    n = Native(root / 'native', peer, bridge=True, resource_fixture=True)
    try:
        n.set_mode(memoryOff=True)
        target = n.work / 'example.mimofmt'
        future = n.async_prompt('formatter_owned', [{'calls': [('write', {'file_path': str(target), 'content': 'original'})]}])
        pid = int(wait_for(lambda: (n.output / 'format_background.pid').read_text()
                           if (n.output / 'format_background.pid').exists() else None))
        owned = guards(n, 'formatter')
        checks.add('native_formatter_background_is_registered_and_holds_tool', len(owned) == 1 and alive(pid) and not future.done() and
                   os.getpgid(pid) == next(iter(owned.values()))['pgid'] and 'MIMO_FORMATTED_SENTINEL' in target.read_text(), owned)
        status = admin(n.bridge_root / 'endpoint.json', 'status')
        seal = admin(n.bridge_root / 'endpoint.json', 'seal', watermark=status['seq'])
        checks.add('formatter_work_prevents_completion_seal', not seal['sealed'] and seal['reason'] == 'work_pending')
        (n.output / 'formatter.release').touch()
        future.result(15)
        checks.add('formatter_background_ended_before_native_followup', not alive(pid) and
                   not group_members(next(iter(owned.values()))['pgid']))
        target = n.work / 'example.mimolsp'
        n.prompt('lsp_owned', [{'calls': [('write', {'file_path': str(target), 'content': 'lsp fixture'})]}])
        pid = int(wait_for(lambda: (n.output / 'lsp.pid').read_text() if (n.output / 'lsp.pid').exists() else None))
        requests = (n.output / 'lsp.requests').read_text()
        checks.add('native_lsp_discovery_and_protocol_are_preserved', alive(pid) and len(guards(n, 'lsp')) == 1 and
                   'initialize' in requests and 'textDocument/didOpen' in requests, {'pid': pid, 'requests': requests})
        status = admin(n.bridge_root / 'endpoint.json', 'status')
        stale = admin(n.bridge_root / 'endpoint.json', 'seal', watermark=status['seq'] - 1)
        checks.add('completion_seal_rejects_stale_watermark', not stale['sealed'] and stale['reason'] == 'stale_watermark')
        status = admin(n.bridge_root / 'endpoint.json', 'status')
        sealed = admin(n.bridge_root / 'endpoint.json', 'seal', watermark=status['seq'])
        checks.add('empty_work_epoch_seals_while_idle_support_is_owned', sealed['sealed'] and not sealed['admission'] and not status['work'] and
                   alive(pid) and bool(guards(n, 'mcp')), sealed)
        final = cleanup_check(n, checks, 'formatter_lsp_mcp_and_native_final_cleanup')
        checks.add('sealed_resource_run_has_no_ownership_fault', final['successful'] and not alive(pid))
    finally:n.close()


def bridge_shells(root, peer, checks):
    from run import Native, wait_for, all_tool_parts
    for shell in ('/bin/bash', '/bin/zsh'):
        n = Native(root / Path(shell).name, peer, bridge=True, real_shell=shell)
        try:
            n.set_mode(memoryOff=True)
            command, pidfile, release = fixture(n, Path(shell).name + '_background')
            command += ' </dev/null >/dev/null 2>&1 &\nprintf "%s\\n" "$SHELL"'
            future = n.async_prompt(Path(shell).name + '_shell', [{'calls': [('bash', {'command': command, 'description': 'Native shell selection'})]}])
            wait_for(lambda: pidfile.exists())
            checks.add(Path(shell).name + '_background_held', not future.done() and len(guards(n)) == 1)
            release.touch();result = future.result(12)
            parts = all_tool_parts(n, result)
            checks.add(Path(shell).name + '_original_shell_restored_for_command', any(p['state'].get('output', '').strip() == shell for p in parts))
            cleanup_check(n, checks, Path(shell).name + '_shell_cleanup')
        finally:n.close()


def bridge_permissions(root, peer, checks):
    from run import Native, all_tool_parts
    n = Native(root / 'native', peer, bridge=True,
               permission={'*': 'allow', 'bash': {'*': 'allow', 'touch *': 'deny'}})
    try:
        n.set_mode(memoryOff=True)
        marker = n.work / 'original-command-denied.txt'
        command = 'touch ' + shlex.quote(str(marker))
        result = n.prompt('native_command_deny', [{'calls': [('bash', {'command': command, 'description': 'Original command permission'})]}])
        parts = all_tool_parts(n, result)
        checks.add('original_command_permission_pattern_is_enforced_before_shim', not marker.exists() and not guards(n) and
                   any(p['tool'] == 'bash' and p['state']['status'] == 'error' for p in parts), parts)
        result = n.prompt('native_command_allow', [{'calls': [('bash', {'command': 'printf allowed', 'description': 'Allowed original command'})]}])
        parts = all_tool_parts(n, result)
        checks.add('allowed_original_command_keeps_native_permission_and_tool_path', len(guards(n)) == 1 and
                   any(p['tool'] == 'bash' and p['state'].get('output') == 'allowed' for p in parts))
        cleanup_check(n, checks, 'command_permission_profile_cleanup')
    finally:n.close()
