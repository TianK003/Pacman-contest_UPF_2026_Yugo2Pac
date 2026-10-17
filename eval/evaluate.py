"""Batch evaluation harness (local tooling, never submitted). Protocol: docs/evaluation.md.

Plays colour-swapped game pairs on fixed RANDOM<seed> maps through the real engine (capture.py,
always -q -c), wraps every team in eval/sentinel_team.py (timing + integrity), stores one JSON
line per game, and prints a markdown summary (points per game, W/T/L, crashes, timing,
violations, head-to-head matrix, approximate Nash averaging, paired comparisons).

Examples (from the repo root, with the venv python):
  python eval/evaluate.py play --agents baseline greedy greedy_deadend --seeds validation --n-seeds 20 --run rr_v1
  python eval/evaluate.py play --candidate greedy --vs baseline turtle --seeds validation --n-seeds 20 --run cand
  python eval/evaluate.py summary --run rr_v1 [--compare greedy greedy_deadend]
"""
import argparse
import itertools
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(REPO, 'eval')
CONTEST_DIR = os.path.join(REPO, 'pacman-contest', 'src', 'contest')
SENTINEL = os.path.join(EVAL, 'sentinel_team.py')
RESULTS = os.path.join(EVAL, 'results')
POINTS = {'win': 3, 'tie': 1, 'loss': 0}

ENGINE_PATTERNS = {
    'warning': re.compile(r'Agent (\d+) took too long'),
    'move_timeout': re.compile(r'Agent (\d+) timed out on a single move'),
    'max_warnings': re.compile(r'Agent (\d+) exceeded the maximum number of warnings'),
    'total_time': re.compile(r'Agent (\d+) ran out of time'),
    'startup_timeout': re.compile(r'Agent (\d+) ran out of time on startup'),
}


# --------------------------------------------------------------------------- setup helpers

def load_league():
    with open(os.path.join(EVAL, 'league.json')) as f:
        league = json.load(f)
    return {k: v for k, v in league.items() if not k.startswith('_')}


def load_seeds(name, n, offset=0):
    """Seeds offset+1 .. offset+n of a list (all from offset+1 when n is 0)."""
    path = name if os.path.isfile(name) else os.path.join(EVAL, 'seeds', name + '.txt')
    with open(path) as f:
        seeds = [int(line) for line in f if line.strip() and not line.startswith('#')]
    seeds = seeds[offset:]
    return seeds[:n] if n else seeds


def lint(league, names):
    sys.path.insert(0, EVAL)
    import check_rules
    failed = []
    for name in names:
        entry = league[name]
        if entry.get('ours'):
            findings = check_rules.check_file(os.path.join(REPO, entry['path']))
            errors = [f for f in findings if f[0] == 'ERROR']
            if errors:
                failed.append((name, errors))
    return failed


# --------------------------------------------------------------------------- playing

def team_args(colour, entry, log, budget):
    opts = ['team=' + os.path.join(REPO, entry['path']), 'log=' + log, 'budget=%g' % budget]
    opts += ['%s=%s' % (k, v) for k, v in sorted(entry.get('opts', {}).items())]
    for o in opts:
        if ',' in o.split('=', 1)[1] or '=' in o.split('=', 1)[1]:
            raise ValueError('option values may not contain "," or "=": %s' % o)
    flag = '-r' if colour == 'red' else '-b'
    return [flag, SENTINEL, '--%sOpts' % colour, ','.join(opts)]


def play_game(job):
    run, game_id, red, blue, seed, league, budget = job
    tmp = os.path.join(RESULTS, run + '_tmp', str(game_id))
    os.makedirs(tmp, exist_ok=True)
    contest_name = 'eval_%s_%d' % (run, game_id)
    # --delay-step 0: the engine otherwise sleeps 0.03 s before every move even with -q (game.py),
    # i.e. 36 of the ~40 s of a game. The sleep is outside the agents' timed moves (E-009).
    cmd = [sys.executable, 'capture.py', '-q', '-c', '-l', 'RANDOM%d' % seed, '--delay-step', '0',
           '--red-name', red, '--blue-name', blue, '-u', contest_name, '-m', '0']
    cmd += team_args('red', league[red], os.path.join(tmp, 'red.json'), budget)
    cmd += team_args('blue', league[blue], os.path.join(tmp, 'blue.json'), budget)
    started = time.time()
    try:
        proc = subprocess.run(cmd, cwd=CONTEST_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              universal_newlines=True, timeout=1800)
        output, harness_error, returncode = proc.stdout, None, proc.returncode
    except subprocess.TimeoutExpired as e:
        output, harness_error, returncode = (e.stdout or ''), 'harness timeout', None
    record = {'run': run, 'game': game_id, 'seed': seed, 'red': red, 'blue': blue,
              'wall_s': round(time.time() - started, 1), 'harness_error': harness_error,
              'returncode': returncode}
    score_file = os.path.join(CONTEST_DIR, 'www', 'contest_' + contest_name, 'scores', 'match_0.json')
    try:
        with open(score_file) as f:
            game = json.load(f)['games'][0]  # [red, blue, layout, score, winner, time, match]
        record['red_score'] = game[3] if game[4] == red else (-game[3] if game[4] == blue else 0)
    except (OSError, ValueError, KeyError, IndexError):
        record['red_score'] = None
        record['harness_error'] = record['harness_error'] or 'no score file'
        record['output_tail'] = (output or '')[-1500:]
    shutil.rmtree(os.path.join(CONTEST_DIR, 'www', 'contest_' + contest_name), ignore_errors=True)

    for colour, parity in (('red', 0), ('blue', 1)):
        events = {key: sum(1 for m in pattern.finditer(output) if int(m.group(1)) % 2 == parity)
                  for key, pattern in ENGINE_PATTERNS.items()}
        events['crashed'] = int(('%s agent crashed' % colour.capitalize()) in output)
        events['failed_to_load'] = int(('%s team failed to load' % colour.capitalize()) in output)
        record[colour + '_engine'] = events
        try:
            with open(os.path.join(tmp, colour + '.json')) as f:
                record[colour + '_sentinel'] = json.load(f)['agents']
        except (OSError, ValueError):
            record[colour + '_sentinel'] = None  # no final() => crash or forfeit
    if 'Traceback' in output:
        record['traceback'] = output[output.index('Traceback'):][:2000]
    shutil.rmtree(tmp, ignore_errors=True)
    return record


def cmd_play(args):
    league = load_league()
    if args.candidate:
        names = list(dict.fromkeys(args.candidate + args.vs))
        pairs, seen = [], set()
        for cand in args.candidate:
            for other in args.vs:
                if other != cand and frozenset((cand, other)) not in seen:
                    seen.add(frozenset((cand, other)))
                    pairs.append((cand, other))
    else:
        names = args.agents
        pairs = list(itertools.combinations(args.agents, 2))
    unknown = [n for n in names if n not in league]
    if unknown:
        sys.exit('unknown league entries: %s' % unknown)
    failed = lint(league, names)
    if failed:
        for name, errors in failed:
            print('rules check FAILED for %s:' % name, file=sys.stderr)
            for _, line, message in errors:
                print('  line %d: %s' % (line, message), file=sys.stderr)
        sys.exit('refusing to evaluate agents that fail eval/check_rules.py')

    seeds = load_seeds(args.seeds, args.n_seeds, args.seed_offset)
    os.makedirs(RESULTS, exist_ok=True)
    out_path = os.path.join(RESULTS, args.run + '.jsonl')
    if os.path.exists(out_path) and not args.resume:
        sys.exit('%s exists; use a new --run name or --resume to add only the missing games' % out_path)
    done_games, next_id = set(), 0
    if args.resume and os.path.exists(out_path):
        previous = read_records(args.run)
        done_games = {(r['red'], r['blue'], r['seed']) for r in previous if r.get('red_score') is not None}
        next_id = max((r['game'] for r in previous), default=-1) + 1
    jobs, game_id = [], next_id
    for a, b in pairs:
        for seed in seeds:
            for red, blue in ((a, b), (b, a)):
                if (red, blue, seed) in done_games:
                    continue
                jobs.append((args.run, game_id, red, blue, seed, league, args.budget))
                game_id += 1
    print('%d games to play (%d pairs x %d seeds x 2 colours, %d already scored) with %d workers -> %s'
          % (len(jobs), len(pairs), len(seeds), len(done_games), args.jobs, out_path), file=sys.stderr)
    if args.dry_run:
        return
    started = time.time()
    with open(out_path, 'a') as out, ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = [pool.submit(play_game, job) for job in jobs]
        for done, future in enumerate(as_completed(futures), 1):
            record = future.result()
            out.write(json.dumps(record) + '\n')
            out.flush()
            if done % 10 == 0 or done == len(jobs):
                elapsed = time.time() - started
                print('  %d/%d games, %.0f s elapsed, ~%.0f s left'
                      % (done, len(jobs), elapsed, elapsed / done * (len(jobs) - done)), file=sys.stderr)
    shutil.rmtree(os.path.join(RESULTS, args.run + '_tmp'), ignore_errors=True)
    print(summarize(read_records(args.run), args.compare))


# --------------------------------------------------------------------------- analysis

def read_records(run):
    """Records of one run, or of several runs (a list of names) concatenated."""
    if isinstance(run, (list, tuple)):
        return [r for name in run for r in read_records(name)]
    with open(os.path.join(RESULTS, run + '.jsonl')) as f:
        return [json.loads(line) for line in f if line.strip()]


def per_agent_games(records):
    """Yields (agent, opponent, seed, colour, points, margin, record) for every scored game."""
    for r in records:
        if r.get('red_score') is None:
            continue
        s = r['red_score']
        red_pts = POINTS['win'] if s > 0 else POINTS['tie'] if s == 0 else POINTS['loss']
        blue_pts = POINTS['win'] if s < 0 else POINTS['tie'] if s == 0 else POINTS['loss']
        yield r['red'], r['blue'], r['seed'], 'red', red_pts, s, r
        yield r['blue'], r['red'], r['seed'], 'blue', blue_pts, -s, r


def bootstrap_ci(values_by_seed, stat=lambda xs: sum(xs) / len(xs), reps=2000, rng_seed=12345):
    """Percentile bootstrap that resamples whole seeds (all games on one map stay together)."""
    seeds = list(values_by_seed)
    if not seeds:
        return None, None, None
    flat = [v for s in seeds for v in values_by_seed[s]]
    point = stat(flat)
    rng = random.Random(rng_seed)
    stats = []
    for _ in range(reps):
        sample = [v for _ in seeds for v in values_by_seed[rng.choice(seeds)]]
        stats.append(stat(sample))
    stats.sort()
    return point, stats[int(0.025 * reps)], stats[int(0.975 * reps) - 1]


def clopper_pearson(k, n, alpha=0.05):
    """Exact binomial CI for k wins in n games. Unlike the bootstrap it stays honest at 0/n and n/n
    (E-004: bootstrap coverage fell to ~73% at a 97% win rate). Treats games as independent."""
    if n == 0:
        return None, None

    def pmf(i, p):  # binomial term in log space: math.comb(n, i) overflows a float beyond n ~ 1000
        log_c = math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1)
        return math.exp(log_c + i * math.log(p) + (n - i) * math.log(1 - p))

    def tail_ge(p):  # P(X >= k | p)
        return sum(pmf(i, p) for i in range(k, n + 1))

    def tail_le(p):  # P(X <= k | p)
        return sum(pmf(i, p) for i in range(0, k + 1))

    def bisect(f, target, increasing):
        lo, hi = 0.0, 1.0
        for _ in range(60):
            mid = (lo + hi) / 2
            if (f(mid) < target) == increasing:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    lower = 0.0 if k == 0 else bisect(tail_ge, alpha / 2, increasing=True)
    upper = 1.0 if k == n else bisect(tail_le, alpha / 2, increasing=False)
    return lower, upper


def nash_average(names, matrix, iters=20000):
    """Approximate Nash of the symmetric zero-sum meta-game A[i][j] = PPG(i vs j) - PPG(j vs i)
    via multiplicative weights (average strategy). Returns (mixture, payoff vs mixture)."""
    n = len(names)
    payoff = [[(matrix[i][j] - matrix[j][i]) if i != j else 0.0 for j in range(n)] for i in range(n)]
    weights = [1.0] * n
    avg = [0.0] * n
    eta = 0.05
    for _ in range(iters):
        total = sum(weights)
        p = [w / total for w in weights]
        for i in range(n):
            avg[i] += p[i]
        gains = [sum(payoff[i][j] * p[j] for j in range(n)) for i in range(n)]
        top = max(gains)
        weights = [w * pow(2.718281828, eta * (g - top)) for w, g in zip(weights, gains)]
    mix = [a / iters for a in avg]
    scores = [sum(payoff[i][j] * mix[j] for j in range(n)) for i in range(n)]
    return mix, scores


def summarize(records, compare=None):
    lines = []
    games = list(per_agent_games(records))
    names = sorted({g[0] for g in games})
    broken = [r for r in records if r.get('red_score') is None]
    lines.append('### Summary: %d games, %d agents, %d seeds%s'
                 % (len(records), len(names), len({r['seed'] for r in records}),
                    ', %d unscored (harness errors)' % len(broken) if broken else ''))
    lines.append('')
    lines.append('| agent | games | W-T-L | PPG [95% CI] | win % [exact 95% CI] | avg margin | crash/forfeit | time warnings | max move s | p95 move s | over budget | violations |')
    lines.append('|---|---|---|---|---|---|---|---|---|---|---|---|')
    for name in names:
        mine = [g for g in games if g[0] == name]
        by_seed = {}
        for g in mine:
            by_seed.setdefault(g[2], []).append(g[4])
        ppg, lo, hi = bootstrap_ci(by_seed)
        w = sum(1 for g in mine if g[4] == 3)
        t = sum(1 for g in mine if g[4] == 1)
        l = sum(1 for g in mine if g[4] == 0)
        margin = sum(g[5] for g in mine) / len(mine)
        crash = warn = over = 0
        max_s, p95_s, violations = 0.0, 0.0, set()
        for g in mine:
            colour, rec = g[3], g[6]
            eng = rec.get(colour + '_engine') or {}
            crash += eng.get('crashed', 0) + eng.get('failed_to_load', 0) + eng.get('max_warnings', 0) \
                + eng.get('move_timeout', 0)
            warn += eng.get('warning', 0)
            sentinel = rec.get(colour + '_sentinel')
            if sentinel is None:
                violations.add('no sentinel report (crash/forfeit?)')
                continue
            for agent in sentinel.values():
                max_s = max(max_s, agent['max_s'] or 0)
                p95_s = max(p95_s, agent['p95_s'] or 0)
                over += agent['over_budget']
                violations.update(agent['violations'])
        wlo, whi = clopper_pearson(w, len(mine))
        lines.append('| %s | %d | %d-%d-%d | %.2f [%.2f, %.2f] | %.0f [%.0f, %.0f] | %+.1f | %d | %d | %.3f | %.3f | %d | %s |'
                     % (name, len(mine), w, t, l, ppg, lo, hi, 100.0 * w / len(mine), 100 * wlo, 100 * whi,
                        margin, crash, warn, max_s, p95_s, over, '; '.join(sorted(violations)) or '-'))
    lines.append('')
    lines.append('PPG CIs: seed-clustered percentile bootstrap. They are too narrow near PPG 0 or 3 '
                 '(E-004: ~73% coverage at a 97% win rate), so trust the exact win-rate CI there.')

    index = {n: i for i, n in enumerate(names)}
    sums = [[0.0] * len(names) for _ in names]
    counts = [[0] * len(names) for _ in names]
    for agent, opp, _, _, pts, _, _ in games:
        sums[index[agent]][index[opp]] += pts
        counts[index[agent]][index[opp]] += 1
    matrix = [[sums[i][j] / counts[i][j] if counts[i][j] else None for j in range(len(names))]
              for i in range(len(names))]
    lines.append('')
    lines.append('Head-to-head PPG (row agent vs column opponent; 3 = always wins):')
    lines.append('')
    lines.append('| | ' + ' | '.join(names) + ' |')
    lines.append('|---' * (len(names) + 1) + '|')
    for i, name in enumerate(names):
        cells = ['-' if matrix[i][j] is None else '%.2f' % matrix[i][j] for j in range(len(names))]
        lines.append('| %s | %s |' % (name, ' | '.join(cells)))

    complete = all(matrix[i][j] is not None for i in range(len(names)) for j in range(len(names)) if i != j)
    if complete and len(names) > 2:
        mix, scores = nash_average(names, [[m or 0.0 for m in row] for row in matrix])
        lines.append('')
        lines.append('Approximate Nash averaging (payoff vs the equilibrium mixture of this pool; >0 = beats the mix):')
        lines.append('')
        lines.append('| agent | Nash weight | Nash-avg payoff |')
        lines.append('|---|---|---|')
        for i in sorted(range(len(names)), key=lambda k: -scores[k]):
            lines.append('| %s | %.2f | %+.2f |' % (names[i], mix[i], scores[i]))

    diag = diagnostics_table(games, names)
    if diag:
        lines.append('')
        lines.append(diag)

    if compare:
        a, b = compare
        lines.append('')
        lines.append(paired_comparison(games, a, b))
    return '\n'.join(lines)


DIAG_KEYS = ('returned', 'deaths', 'food_lost', 'pacman_moves', 'standoff_moves', 'max_carry')


def team_diag(sentinel):
    """Sum the per-agent sentinel diagnostics of one team (max for max_carry); None if missing."""
    if not sentinel or any(a.get('diag') is None for a in sentinel.values()):
        return None
    out = {}
    for key in DIAG_KEYS:
        values = [a['diag'][key] for a in sentinel.values()]
        out[key] = max(values) if key == 'max_carry' else sum(values)
    out['moves'] = max(a['moves'] for a in sentinel.values())
    return out


def diag_rows(games):
    """Per-game diagnostics means for a list of per_agent_games tuples (agent's view)."""
    acc, n, early_ours, early_theirs = {}, 0, 0, 0
    for _, _, _, colour, _, margin, rec in games:
        other = 'blue' if colour == 'red' else 'red'
        mine, theirs = team_diag(rec.get(colour + '_sentinel')), team_diag(rec.get(other + '_sentinel'))
        if mine is None or theirs is None:
            continue
        n += 1
        for key in DIAG_KEYS:
            acc[key] = acc.get(key, 0) + mine[key]
        acc['conceded'] = acc.get('conceded', 0) + theirs['returned']
        acc['kills'] = acc.get('kills', 0) + theirs['deaths']
        if max(mine['moves'], theirs['moves']) < 300:  # ended by the food rule: the leader reached it
            early_ours += margin > 0
            early_theirs += margin < 0
    if not n:
        return None
    means = {k: v / n for k, v in acc.items()}
    means['n'], means['early_ours'], means['early_theirs'] = n, early_ours, early_theirs
    return means


def format_diag(label, m):
    return ('| %s | %d | %.1f | %.1f | %.2f | %.2f | %.1f | %.0f | %.0f | %.1f | %d / %d |'
            % (label, m['n'], m['returned'], m['conceded'], m['deaths'], m['kills'], m['food_lost'],
               m['pacman_moves'], m['standoff_moves'], m['max_carry'], m['early_ours'], m['early_theirs']))


DIAG_HEADER = ['| %s | games | returned | conceded | deaths | kills | food lost | Pacman moves | standoff moves '
               '| max carried | 28-finish us / them |',
               '|---|---|---|---|---|---|---|---|---|---|---|']


def diagnostics_table(games, names, by_opponent=None):
    """Behavioural diagnostics (docs/evaluation.md: for understanding only, never optimised)."""
    if by_opponent:
        mine = [g for g in games if g[0] == by_opponent]
        rows = [(opp, diag_rows([g for g in mine if g[1] == opp])) for opp in sorted({g[1] for g in mine})]
        title = 'Diagnostics for %s per opponent (team totals per game):' % by_opponent
        first = 'opponent'
    else:
        rows = [(name, diag_rows([g for g in games if g[0] == name])) for name in names]
        title = 'Diagnostics (team totals per game; kills = opponent deaths):'
        first = 'agent'
    rows = [(label, m) for label, m in rows if m]
    if not rows:
        return ''
    lines = [title, '', DIAG_HEADER[0] % first, DIAG_HEADER[1]]
    lines += [format_diag(label, m) for label, m in rows]
    return '\n'.join(lines)


def paired_comparison(games, a, b):
    """Mean point difference a - b over games with the same (opponent, seed, colour)."""
    table = {}
    for agent, opp, seed, colour, pts, _, _ in games:
        if agent in (a, b) and opp not in (a, b):
            table.setdefault((opp, seed, colour), {})[agent] = pts
    diffs_by_seed = {}
    for (opp, seed, colour), entry in table.items():
        if a in entry and b in entry:
            diffs_by_seed.setdefault(seed, []).append(entry[a] - entry[b])
    if not diffs_by_seed:
        return 'Paired comparison %s vs %s: no shared (opponent, seed, colour) games.' % (a, b)
    mean, lo, hi = bootstrap_ci(diffs_by_seed)
    n = sum(len(v) for v in diffs_by_seed.values())
    lines = ['Paired comparison over %d shared games: PPG(%s) - PPG(%s) = %+.2f [95%% CI %+.2f, %+.2f]'
             % (n, a, b, mean, lo, hi),
             '', '| opponent | games | PPG(%s) | PPG(%s) | paired diff [95%% CI] |' % (a, b), '|---|---|---|---|---|']
    for opp in sorted({key[0] for key in table}):  # per-opponent rows: accept rule 3 (no regression > delta)
        by_seed, pa, pb = {}, [], []
        for (o, seed, colour), entry in table.items():
            if o == opp and a in entry and b in entry:
                by_seed.setdefault(seed, []).append(entry[a] - entry[b])
                pa.append(entry[a])
                pb.append(entry[b])
        if by_seed:
            m, l, h = bootstrap_ci(by_seed)
            lines.append('| %s | %d | %.2f | %.2f | %+.2f [%+.2f, %+.2f] |'
                         % (opp, len(pa), sum(pa) / len(pa), sum(pb) / len(pb), m, l, h))
    return '\n'.join(lines)


def cmd_summary(args):
    records = read_records(args.run)
    if args.agents:
        records = [r for r in records if r['red'] in args.agents and r['blue'] in args.agents]
    print(summarize(records, args.compare))
    for name in args.diag or []:
        print()
        print(diagnostics_table(list(per_agent_games(records)), None, by_opponent=name))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command')
    play = sub.add_parser('play')
    group = play.add_mutually_exclusive_group(required=True)
    group.add_argument('--agents', nargs='+', help='round robin between these league entries')
    group.add_argument('--candidate', nargs='+', help='play each of these entries against every entry in --vs')
    play.add_argument('--vs', nargs='+', default=[])
    play.add_argument('--seeds', default='validation', help='seed list name in eval/seeds/ or a file path')
    play.add_argument('--n-seeds', type=int, default=20)
    play.add_argument('--seed-offset', type=int, default=0,
                      help='skip the first N seeds of the list (e.g. seeds already used to design a candidate)')
    play.add_argument('--run', required=True, help='run name; results go to eval/results/<run>.jsonl')
    play.add_argument('--jobs', type=int, default=max(1, (os.cpu_count() or 2) - 2))
    play.add_argument('--budget', type=float, default=0.5, help='internal per-move budget (s) to count overruns')
    play.add_argument('--compare', nargs=2, metavar=('A', 'B'))
    play.add_argument('--resume', action='store_true',
                      help='append to an existing run, playing only games without a scored record')
    play.add_argument('--dry-run', action='store_true', help='only print how many games would be played')
    summary = sub.add_parser('summary')
    summary.add_argument('--run', required=True, nargs='+', help='one or more runs, analysed together')
    summary.add_argument('--compare', nargs=2, metavar=('A', 'B'))
    summary.add_argument('--agents', nargs='+', help='only games where both teams are in this list')
    summary.add_argument('--diag', nargs='+', metavar='AGENT', help='per-opponent diagnostics for these agents')
    args = parser.parse_args()
    if args.command == 'play':
        if args.candidate and not args.vs:
            parser.error('--candidate needs --vs')
        cmd_play(args)
    elif args.command == 'summary':
        cmd_summary(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
