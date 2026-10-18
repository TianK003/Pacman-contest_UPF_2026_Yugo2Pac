"""Replay probe (local analysis tool, never submitted; docs/evaluation.md section 8).

Where does an agent lose points? Two subcommands:

  classify  reads an evaluate.py run and sorts the focus agent's non-wins into failure types,
            using only the sentinel diagnostics already stored per game.
  replay    re-plays chosen games with --record (the games are deterministic, E-004), then
            re-simulates every move from the replay and reports what really happened from the
            TRUE state: deaths (where, carrying what, killed by a ghost we could see or not, in a
            dead end or not), food returned per side, invasions and how far our defender was,
            border standoffs, capsules. Offline analysis of a finished game, so reading the full
            state is fine here; agents never get this information.

Examples (repo root, venv python):
  python eval/replay_probe.py classify --run diag_v2 --agent greedy_v2
  python eval/replay_probe.py replay --run diag_v2 --agent greedy_v2 --opponent camper --worst 5
  python eval/replay_probe.py replay --agent greedy_v2 --game greedy_v2 camper 12345678
"""
import argparse
import contextlib
import io
import os
import pickle
import random
import shutil
import subprocess
import sys
from collections import Counter

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVAL = os.path.join(REPO, 'eval')
CONTEST_DIR = os.path.join(REPO, 'pacman-contest', 'src', 'contest')
sys.path.insert(0, EVAL)
sys.path.insert(0, os.path.join(REPO, 'teams'))

import evaluate as ev  # noqa: E402

SIGHT = 5


# --------------------------------------------------------------------------- classify

def classify_game(points, margin, mine, theirs, early):
    """One label per non-win, from the focus team's point of view."""
    if points == 3:
        return 'win'
    if early and margin < 0:
        return 'loss: out-raced (they returned 28 first)'
    if margin == 0:
        if mine['returned'] == 0 and theirs['returned'] == 0:
            if mine['pacman_moves'] < 60:
                return 'tie 0-0: we barely attacked (<60 Pacman moves)'
            return 'tie 0-0: we attacked but returned nothing'
        return 'tie: equal trade'
    if mine['deaths'] >= 3 or mine['food_lost'] >= 6:
        return 'loss: our deaths (>=3 deaths or >=6 food lost)'
    if mine['returned'] <= 3:
        return 'loss: we returned <=3'
    return 'loss: they returned more (defence)'


def game_label(g):
    """classify_game for one per_agent_games tuple."""
    _, _, _, colour, pts, margin, rec = g
    other = 'blue' if colour == 'red' else 'red'
    mine, theirs = ev.team_diag(rec.get(colour + '_sentinel')), ev.team_diag(rec.get(other + '_sentinel'))
    if mine is None or theirs is None:
        return 'no diagnostics (crash?)'
    early = max(mine['moves'], theirs['moves']) < 300
    return classify_game(pts, margin, mine, theirs, early)


def cmd_classify(args):
    games = [g for g in ev.per_agent_games(ev.read_records(args.run)) if g[0] == args.agent]
    by_opp = {}
    for g in games:
        by_opp.setdefault(g[1], []).append((game_label(g), g[4]))
    labels = sorted({l for rows in by_opp.values() for l, _ in rows if l != 'win'})
    print('| opponent | games | PPG | wins | ' + ' | '.join(labels) + ' | points lost vs 3/game |')
    print('|---' * (len(labels) + 5) + '|')
    total = Counter()
    for opp in sorted(by_opp):
        rows = by_opp[opp]
        counts = Counter(l for l, _ in rows)
        total.update(counts)
        ppg = sum(p for _, p in rows) / len(rows)
        lost = sum(3 - p for _, p in rows)
        print('| %s | %d | %.2f | %d | %s | %d |' % (opp, len(rows), ppg, counts['win'],
                                                    ' | '.join(str(counts[l]) for l in labels), lost))
    n = sum(len(r) for r in by_opp.values())
    lost = sum(3 - p for rows in by_opp.values() for _, p in rows)
    print('| **all** | %d | %.2f | %d | %s | %d |' % (n, 3 - lost / n, total['win'],
                                                     ' | '.join(str(total[l]) for l in labels), lost))
    print()
    print('Points lost per label (a tie loses 2, a loss 3):')
    lost_by = Counter()
    for rows in by_opp.values():
        for l, p in rows:
            lost_by[l] += 3 - p
    for l, v in lost_by.most_common():
        if v:
            print('- %s: %d (%.0f%%)' % (l, v, 100.0 * v / lost))


# --------------------------------------------------------------------------- replay

def record_game(red, blue, seed, league, tag):
    """Plays one game with --record (no sentinel; behaviour is identical, E-007 identity checks)
    and returns (replay dict, engine output)."""
    name = 'probe_%s' % tag
    cmd = [sys.executable, 'capture.py', '-q', '-c', '-l', 'RANDOM%d' % seed, '--delay-step', '0',
           '--record', '-u', name, '-m', '0']
    for colour, key in (('red', red), ('blue', blue)):
        entry = league[key]
        cmd += ['-r' if colour == 'red' else '-b', os.path.join(REPO, entry['path'])]
        opts = ','.join('%s=%s' % kv for kv in sorted(entry.get('opts', {}).items()))
        if opts:
            cmd += ['--%sOpts' % colour, opts]
    proc = subprocess.run(cmd, cwd=CONTEST_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          universal_newlines=True, timeout=900)
    folder = os.path.join(CONTEST_DIR, 'www', 'contest_' + name)
    try:
        with open(os.path.join(folder, 'replays', 'match_0.replay'), 'rb') as f:
            replay = pickle.load(f)
    finally:
        shutil.rmtree(folder, ignore_errors=True)
    return replay, proc.stdout


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def analyse(replay, focus_red, trace=None):
    """Re-simulates the replay and returns event statistics for the focus team. trace=(first, last,
    step) prints every agent's position, side and food carried for those plies."""
    from contest.capture import CaptureRules
    from contest import text_display
    from greedy_v2 import MapInfo

    rules = CaptureRules(quiet=True)
    with contextlib.redirect_stdout(io.StringIO()):  # new_game prints which team starts
        game = rules.new_game(replay['layout'], replay['agents'], text_display.NullGraphics(),
                              replay['length'], False, False)
    state = game.state
    ours = state.get_red_team_indices() if focus_red else state.get_blue_team_indices()
    theirs = state.get_blue_team_indices() if focus_red else state.get_red_team_indices()
    m = MapInfo(state.get_walls(), focus_red)
    starts = {k: state.get_initial_agent_position(k) for k in ours + theirs}

    out = {'deaths': [], 'kills': [], 'our_returns': [], 'their_returns': [], 'capsules': [],
           'standoff': {k: 0 for k in ours}, 'pacman': {k: 0 for k in ours},
           'invaded_plies': 0, 'two_invader_plies': 0, 'defender_gap': [], 'plies': 0}
    history = []  # positions of all agents after each ply
    for ply, (mover, action) in enumerate(replay['actions']):
        prev = state
        state = state.generate_successor(mover, action)
        history.append({k: state.get_agent_position(k) for k in ours + theirs})
        out['plies'] = ply + 1
        for k in ours + theirs:
            before, after = prev.get_agent_position(k), state.get_agent_position(k)
            if after == starts[k] and before != starts[k] and m.d(before, starts[k]) > 1:
                carried = prev.get_agent_state(k).num_carrying
                enemies = theirs if k in ours else ours
                killer_i = min(enemies, key=lambda j: m.d(prev.get_agent_position(j), before))
                killer = prev.get_agent_position(killer_i)
                team = ours if k in ours else theirs
                seen = any(manhattan(killer, prev.get_agent_position(t)) <= SIGHT for t in team)
                # when it died inside a dead end: was the killer in sight of our team on the last
                # ply it stood outside the dead end (i.e. when it committed to going in)?
                seen_at_entry, entry_lead = None, None
                if m.depth[before] > 0:
                    for p in range(len(history) - 2, -1, -1):
                        if m.depth[history[p][k]] == 0:
                            here = history[p]
                            seen_at_entry = any(manhattan(here[killer_i], here[t]) <= SIGHT for t in team)
                            exit_cell = m.entrance[before]
                            entry_lead = m.d(here[killer_i], exit_cell) - (
                                m.d(here[k], before) + m.d(before, exit_cell))
                            break
                event = {'ply': ply, 'agent': k, 'pos': before, 'carried': carried,
                         'depth': m.depth[before], 'killer_seen_before': seen,
                         'killer_seen_at_entry': seen_at_entry, 'entry_lead': entry_lead,
                         'dist_home': m.dist_home[before] if k in ours else None}
                (out['deaths'] if k in ours else out['kills']).append(event)
            got = state.get_agent_state(k).num_returned - prev.get_agent_state(k).num_returned
            if got > 0:
                (out['our_returns'] if k in ours else out['their_returns']).append((ply, k, got))
        if set(prev.get_capsules()) != set(state.get_capsules()):
            out['capsules'].append((ply, mover, 'ours' if mover in ours else 'theirs'))
        if mover in ours:
            me = state.get_agent_state(mover)
            pos = state.get_agent_position(mover)
            if me.is_pacman:
                out['pacman'][mover] += 1
            elif min(m.d(pos, b) for b in m.home_border) <= 1:
                enemy_ghosts = [state.get_agent_position(j) for j in theirs
                                if not state.get_agent_state(j).is_pacman]
                if any(manhattan(pos, g) <= SIGHT for g in enemy_ghosts):
                    out['standoff'][mover] += 1
        else:
            invaders = [state.get_agent_position(j) for j in theirs if state.get_agent_state(j).is_pacman]
            if invaders:
                out['invaded_plies'] += 1
                if len(invaders) == 2:
                    out['two_invader_plies'] += 1
                ghosts = [state.get_agent_position(k) for k in ours if not state.get_agent_state(k).is_pacman]
                if ghosts:
                    out['defender_gap'].append(min(m.d(g, i) for g in ghosts for i in invaders))
        if trace and trace[0] <= ply <= trace[1] and (ply - trace[0]) % trace[2] == 0:
            cells = []
            for k in sorted(ours + theirs):
                s = state.get_agent_state(k)
                cells.append('%s%d%s%s c%d' % ('*' if k in ours else ' ', k, state.get_agent_position(k),
                                               'P' if s.is_pacman else 'G', s.num_carrying))
            print('ply %4d mover %d %-5s | %s' % (ply, mover, action, ' | '.join(cells)))
        rules.process(state, game)
        if game.game_over:
            break
    out['score'] = state.data.score if focus_red else -state.data.score
    return out


def summarise_events(label, ev_out):
    d = ev_out['deaths']
    gap = ev_out['defender_gap']
    return {
        'game': label,
        'score': ev_out['score'],
        'plies': ev_out['plies'],
        'our returned': sum(g for _, _, g in ev_out['our_returns']),
        'their returned': sum(g for _, _, g in ev_out['their_returns']),
        'our deaths': len(d),
        'food lost': sum(e['carried'] for e in d),
        'deaths in dead end': sum(1 for e in d if e['depth'] > 0),
        'dead-end deaths, killer out of sight at entry': sum(1 for e in d if e['killer_seen_at_entry'] is False),
        'kills': len(ev_out['kills']),
        'standoff plies (ghost at border, enemy ghost in sight)': sum(ev_out['standoff'].values()),
        'our Pacman plies': sum(ev_out['pacman'].values()),
        'invaded plies': ev_out['invaded_plies'],
        'two-invader plies': ev_out['two_invader_plies'],
        'mean defender gap': (sum(gap) / len(gap)) if gap else None,
        'capsules ours/theirs': '%d/%d' % (sum(1 for c in ev_out['capsules'] if c[2] == 'ours'),
                                         sum(1 for c in ev_out['capsules'] if c[2] == 'theirs')),
    }


def probe_one(job):
    """Worker: record one game and analyse it (runs in its own process)."""
    agent, opp, seed, colour, margin, tag, trace = job
    league = ev.load_league()
    red, blue = (agent, opp) if colour == 'red' else (opp, agent)
    replay, _ = record_game(red, blue, seed, league, tag)
    if trace:
        return job, analyse(replay, colour == 'red', trace)
    with contextlib.redirect_stdout(io.StringIO()):
        return job, analyse(replay, colour == 'red')


def aggregate(results):
    """Totals over many analysed games (deaths of the focus team, defence numbers)."""
    deaths = [e for r in results for e in r['deaths']]
    n = len(results)
    gaps = [g for r in results for g in r['defender_gap']]
    invaded = sum(r['invaded_plies'] for r in results)
    inside = [e for e in deaths if e['depth'] > 0]

    def share(items, cond):
        return '%d%%' % round(100.0 * sum(1 for e in items if cond(e)) / len(items)) if items else '-'

    lines = ['| games | deaths/game | food lost/game | deaths in a dead end | of those: killer out of sight when we went in '
             '| of those: killer could beat us to the exit when we went in | carried at death (mean) '
             '| our returned/game | their returned/game | kills/game '
             '| invaded plies/game | share of invaded plies with 2 invaders | mean defender gap '
             '| standoff plies/game | our Pacman plies/game |',
             '|---' * 15 + '|']
    lines.append('| %d | %.2f | %.1f | %s | %s | %s | %.1f | %.1f | %.1f | %.2f | %.0f | %s | %s | %.0f | %.0f |' % (
        n, len(deaths) / n, sum(e['carried'] for e in deaths) / n,
        share(deaths, lambda e: e['depth'] > 0),
        share(inside, lambda e: e['killer_seen_at_entry'] is False),
        share(inside, lambda e: e['entry_lead'] is not None and e['entry_lead'] <= 0),
        (sum(e['carried'] for e in deaths) / len(deaths)) if deaths else 0.0,
        sum(g for r in results for _, _, g in r['our_returns']) / n,
        sum(g for r in results for _, _, g in r['their_returns']) / n,
        sum(len(r['kills']) for r in results) / n,
        invaded / n,
        '%d%%' % round(100.0 * sum(r['two_invader_plies'] for r in results) / invaded) if invaded else '-',
        '%.1f' % (sum(gaps) / len(gaps)) if gaps else '-',
        sum(sum(r['standoff'].values()) for r in results) / n,
        sum(sum(r['pacman'].values()) for r in results) / n))
    return '\n'.join(lines)


def cmd_replay(args):
    from concurrent.futures import ProcessPoolExecutor
    if args.game:
        a, b, seed = args.game[0], args.game[1], int(args.game[2])
        games = [(a, b, seed, 'red', None)]
    else:
        rows = [g for g in ev.per_agent_games(ev.read_records(args.run))
                if g[0] == args.agent and (not args.opponent or g[1] == args.opponent)
                and (g[4] < 3 or args.include_wins)]
        if args.label:
            rows = [g for g in rows if game_label(g) == args.label]
        rows.sort(key=lambda g: (g[4], g[5], g[2], g[3]))  # losses first, then by margin
        if args.sample:
            rows = random.Random(args.sample_seed).sample(rows, min(args.sample, len(rows)))
        else:
            rows = rows[:args.worst]
        games = [(g[0], g[1], g[2], g[3], g[5]) for g in rows]
    jobs = [g + ('%d_%d' % (os.getpid(), i), args.trace) for i, g in enumerate(games)]
    table, results = [], []
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        outcomes = list(pool.map(probe_one, jobs))
    for (agent, opp, seed, colour, margin, _, _), result in outcomes:
        if margin is not None and result['score'] != margin:
            print('WARNING: replay score %d != recorded margin %d for %s vs %s seed %d'
                  % (result['score'], margin, agent, opp, seed), file=sys.stderr)
        results.append(result)
        row = summarise_events('%s vs %s, %d (%s)' % (agent, opp, seed, colour), result)
        table.append(row)
        if args.events:
            print('### %s' % row['game'])
            for e in result['deaths']:
                print('- death ply %d agent %d at %s carrying %d, depth %d, dist home %s, killer in sight '
                      'at dead-end entry: %s, killer lead to the exit at entry: %s'
                      % (e['ply'], e['agent'], e['pos'], e['carried'], e['depth'], e['dist_home'],
                         e['killer_seen_at_entry'], e['entry_lead']))
            print('- our returns (ply, agent, food): %s' % result['our_returns'])
            print('- their returns (ply, agent, food): %s' % result['their_returns'])
            print('- capsules (ply, mover, side): %s' % result['capsules'])
            print()
    if table and not args.aggregate_only:
        keys = list(table[0])
        print('| ' + ' | '.join(keys) + ' |')
        print('|---' * len(keys) + '|')
        for row in table:
            print('| ' + ' | '.join('%.1f' % v if isinstance(v, float) else str(v) for v in row.values()) + ' |')
    if results:
        print()
        print(aggregate(results))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command')
    c = sub.add_parser('classify')
    c.add_argument('--run', required=True, nargs='+')
    c.add_argument('--agent', required=True)
    r = sub.add_parser('replay')
    r.add_argument('--run', nargs='+')
    r.add_argument('--agent', required=True)
    r.add_argument('--opponent')
    r.add_argument('--worst', type=int, default=5, help='how many of the worst non-wins to replay')
    r.add_argument('--game', nargs=3, metavar=('AGENT', 'OPPONENT', 'SEED'),
                   help='one game, AGENT playing red')
    r.add_argument('--events', action='store_true', help='also print the event list per game')
    r.add_argument('--trace', nargs=3, type=int, metavar=('FIRST', 'LAST', 'STEP'),
                   help='print all positions for plies FIRST..LAST every STEP plies (* = focus team)')
    r.add_argument('--label', help='only non-wins with this classify label')
    r.add_argument('--include-wins', action='store_true', help='also consider won games')
    r.add_argument('--sample', type=int, help='random sample of this many games instead of the worst')
    r.add_argument('--sample-seed', type=int, default=1)
    r.add_argument('--jobs', type=int, default=4)
    r.add_argument('--aggregate-only', action='store_true', help='print only the totals table')
    args = parser.parse_args()
    if args.command == 'classify':
        cmd_classify(args)
    elif args.command == 'replay':
        if not args.game and not args.run:
            parser.error('replay needs --run or --game')
        cmd_replay(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
