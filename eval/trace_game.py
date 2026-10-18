# trace_game.py
# -------------
# LOCAL ANALYSIS TOOL - never submitted. Plays games with eval/trace_team.py wrapped around one of
# our teams and reports which rule produced each move (E-022). Decisions are deterministic, so a
# traced game is the same game the evaluation played (checked with --check-run).
#
# One game, move by move, plus a replay to watch alongside:
#   venv\Scripts\python.exe eval\trace_game.py game --team submission --vs camper --seed 27904464 --colour red
#   venv\Scripts\python.exe eval\trace_game.py game --team greedy_v3 --vs feature --seed 27904464 --from 40 --to 80 --agent defender
# Rule profile (how often each rule fires) over many games:
#   venv\Scripts\python.exe eval\trace_game.py profile --team greedy_v3 --vs greedy feature camper rusher choke exploit_v2 --seeds tuning --seed-offset 580 --n-seeds 10 --jobs 6
# Pass-through check against an evaluate.py run of the same team on the same games:
#   venv\Scripts\python.exe eval\trace_game.py profile --team greedy_v3 --vs baseline camper exploit_v2 --seeds tuning --n-seeds 3 --check-run identity_v3
#
# Outputs go to eval/traces/ (gitignored): <tag>.json (the trace) and <tag>.replay (with `game`).
# Watch a replay from pacman-contest/src/contest:
#   ..\..\..\venv\Scripts\python.exe capture.py --replay=..\..\..\eval\traces\<tag>.replay --delay-step 0.1

import argparse
import json
import os
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

EVAL = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(EVAL)
CONTEST_DIR = os.path.join(REPO, 'pacman-contest', 'src', 'contest')
TRACE_TEAM = os.path.join(EVAL, 'trace_team.py')
TRACES = os.path.join(EVAL, 'traces')
ROLE = {'GreedyAttacker': 'attacker', 'DeadEndAttacker': 'attacker', 'PatrolDefender': 'defender'}

sys.path.insert(0, EVAL)
from evaluate import load_league, load_seeds  # noqa: E402


def team_cli(colour, path, opts):
    flag = '-r' if colour == 'red' else '-b'
    args = [flag, path]
    if opts:
        args += ['--%sOpts' % colour, ','.join('%s=%s' % kv for kv in opts.items())]
    return args


def play(job):
    """job = (tag, our league entry, opponent name, opponent league entry, seed, our colour, record)."""
    tag, ours, vs, theirs, seed, colour, record = job
    os.makedirs(TRACES, exist_ok=True)
    log = os.path.join(TRACES, tag + '.json')
    our_opts = dict(ours.get('opts', {}))
    our_opts.update(team=os.path.join(REPO, ours['path']), log=log)
    other = 'blue' if colour == 'red' else 'red'
    contest = 'trace_' + tag
    cmd = [sys.executable, 'capture.py', '-q', '-c', '-l', 'RANDOM%d' % seed, '--delay-step', '0',
           '-u', contest, '-m', '0']
    if record:
        cmd.append('--record')
    cmd += team_cli(colour, TRACE_TEAM, our_opts)
    cmd += team_cli(other, os.path.join(REPO, theirs['path']), theirs.get('opts', {}))
    proc = subprocess.run(cmd, cwd=CONTEST_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          universal_newlines=True)
    out = proc.stdout
    replay = None
    if record:
        src = os.path.join(CONTEST_DIR, 'www', 'contest_' + contest, 'replays', 'match_0.replay')
        if os.path.isfile(src):
            replay = os.path.join(TRACES, tag + '.replay')
            shutil.copyfile(src, replay)
    shutil.rmtree(os.path.join(CONTEST_DIR, 'www', 'contest_' + contest), ignore_errors=True)
    try:
        with open(log) as f:
            trace = json.load(f)
    except (OSError, ValueError):
        trace = None
    problems = [line for line in out.splitlines()
                if any(k in line for k in ('took too long', 'timed out', 'crashed', 'failed to load', 'Traceback'))]
    return {'tag': tag, 'vs': vs, 'seed': seed, 'colour': colour, 'trace': trace, 'replay': replay,
            'problems': problems, 'output_tail': out[-1500:] if trace is None else ''}


def ours_entry(league, name):
    entry = league[name]
    if not entry.get('ours'):
        sys.exit('%s is not one of our teams (trace_team.py only wraps our own files)' % name)
    return entry


def timeline(trace, first, last, which):
    rows = []
    for idx, moves in trace['moves'].items():
        for m in moves:
            role = ROLE.get(m['role'], m['role'])
            if which != 'all' and role != which:
                continue
            if first <= m['move'] <= last:
                rows.append((m['ply'], m))
    print('| ply | move | agent | pos | action | carrying | score | rule | why |')
    print('|---|---|---|---|---|---|---|---|---|')
    for _, m in sorted(rows, key=lambda r: r[0]):
        print('| %d | %d | %s %s | %s | %s | %d | %+d | %s | %s |' % (
            m['ply'], m['move'], ROLE.get(m['role'], m['role']), m['index'], tuple(m['pos']) if m['pos'] else '-',
            m['action'], m['carrying'], m['score'], m['rule'], m['text']))


def rule_table(counts):
    roles = sorted(counts)
    rules = sorted({r for c in counts.values() for r in c}, key=lambda r: (-sum(counts[x][r] for x in roles), r))
    print('| rule | ' + ' | '.join('%s share of moves' % r for r in roles) + ' |')
    print('|---|' + '---|' * len(roles))
    for rule in rules:
        cells = []
        for role in roles:
            total = sum(counts[role].values())
            cells.append('%.1f%%' % (100.0 * counts[role][rule] / total) if counts[role][rule] else '-')
        print('| %s | %s |' % (rule, ' | '.join(cells)))
    print('| (moves) | ' + ' | '.join(str(sum(counts[r].values())) for r in roles) + ' |')


def count_rules(traces):
    counts = defaultdict(Counter)
    for t in traces:
        for moves in t['moves'].values():
            for m in moves:
                counts[ROLE.get(m['role'], m['role'])][m['rule']] += 1
    return counts


def cmd_game(args):
    league = load_league()
    ours, theirs = ours_entry(league, args.team), league[args.vs]
    tag = '%s_vs_%s_%d_%s' % (args.team, args.vs, args.seed, args.colour)
    res = play((tag, ours, args.vs, theirs, args.seed, args.colour, True))
    if res['trace'] is None:
        sys.exit('no trace written (crash?):\n' + res['output_tail'])
    t = res['trace']
    print('### %s (%s) vs %s on RANDOM%d: final score for us %+d' % (args.team, args.colour, args.vs, args.seed, t['final_score']))
    for p in res['problems']:
        print('ENGINE: ' + p)
    print()
    timeline(t, args.first, args.last, args.agent)
    print()
    rule_table(count_rules([t]))
    print()
    print('trace:  %s' % os.path.join(TRACES, tag + '.json'))
    if res['replay']:
        print('replay: from pacman-contest/src/contest run')
        print('  ..\\..\\..\\venv\\Scripts\\python.exe capture.py --replay=..\\..\\..\\eval\\traces\\%s.replay --delay-step 0.1' % tag)
        print('  (the "ply" column counts agent moves from 0; each agent moves every 4th ply)')


def cmd_profile(args):
    league = load_league()
    ours = ours_entry(league, args.team)
    seeds = load_seeds(args.seeds, args.n_seeds, args.seed_offset)
    jobs = [('%s_vs_%s_%d_%s' % (args.team, vs, s, c), ours, vs, league[vs], s, c, False)
            for vs in args.vs for s in seeds for c in ('red', 'blue')]
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(play, jobs))
    by_opp = defaultdict(list)
    for r in results:
        by_opp[r['vs']].append(r)
    missing = [r['tag'] for r in results if r['trace'] is None]
    problems = [(r['tag'], p) for r in results for p in r['problems']]
    traces = [r['trace'] for r in results if r['trace'] is not None]
    errors = sum(1 for t in traces for ms in t['moves'].values() for m in ms if m['rule'] == 'trace-error')
    pts = [3 if t['final_score'] > 0 else (1 if t['final_score'] == 0 else 0) for t in traces]
    print('### Rule profile: %s, %d games vs %s (%s seeds %d-%d, both colours)' % (
        args.team, len(results), ', '.join(args.vs), args.seeds, args.seed_offset + 1, args.seed_offset + len(seeds)))
    print()
    print('PPG %.2f; games without a trace: %d; engine warnings/crashes: %d; trace errors: %d'
          % (sum(pts) / max(1, len(pts)), len(missing), len(problems), errors))
    for tag, p in problems[:10]:
        print('  %s: %s' % (tag, p))
    print()
    rule_table(count_rules(traces))
    if args.by_opponent:
        for vs in args.vs:
            print()
            print('#### vs %s' % vs)
            print()
            rule_table(count_rules([r['trace'] for r in by_opp[vs] if r['trace'] is not None]))
    if args.check_run:
        check(args, results)


def check(args, results):
    """Pass-through check: the traced games must end with the scores an evaluate.py run recorded."""
    path = os.path.join(EVAL, 'results', args.check_run + '.jsonl')
    recorded = {}
    with open(path) as f:
        for line in f:
            r = json.loads(line)
            if r.get('red_score') is None:
                continue
            if r['red'] == args.team:
                recorded[(r['blue'], r['seed'], 'red')] = r['red_score']
            if r['blue'] == args.team:
                recorded[(r['red'], r['seed'], 'blue')] = -r['red_score']
    same = differ = 0
    for r in results:
        key = (r['vs'], r['seed'], r['colour'])
        if key in recorded and r['trace'] is not None:
            if recorded[key] == r['trace']['final_score']:
                same += 1
            else:
                differ += 1
                print('DIFFERENT: %s traced %+d, %s recorded %+d' % (r['tag'], r['trace']['final_score'],
                                                                     args.check_run, recorded[key]))
    print()
    print('Pass-through check against run %s: %d identical, %d different' % (args.check_run, same, differ))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='cmd')
    g = sub.add_parser('game', help='one traced game, move by move, with a replay')
    g.add_argument('--team', default='submission')
    g.add_argument('--vs', required=True)
    g.add_argument('--seed', type=int, required=True, help='map seed (RANDOM<seed>)')
    g.add_argument('--colour', choices=('red', 'blue'), default='red')
    g.add_argument('--from', dest='first', type=int, default=1, help='first own move to print')
    g.add_argument('--to', dest='last', type=int, default=300, help='last own move to print')
    g.add_argument('--agent', choices=('all', 'attacker', 'defender'), default='all')
    p = sub.add_parser('profile', help='how often each rule fires, over many games')
    p.add_argument('--team', default='submission')
    p.add_argument('--vs', nargs='+', required=True)
    p.add_argument('--seeds', default='tuning')
    p.add_argument('--n-seeds', type=int, default=10)
    p.add_argument('--seed-offset', type=int, default=0)
    p.add_argument('--jobs', type=int, default=6)
    p.add_argument('--by-opponent', action='store_true')
    p.add_argument('--check-run', help='evaluate.py run of the same team to compare final scores with')
    args = parser.parse_args()
    if args.cmd == 'game':
        cmd_game(args)
    elif args.cmd == 'profile':
        if args.seeds == 'test':
            sys.exit('test seeds are locked (evaluation.md section 4)')
        cmd_profile(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
