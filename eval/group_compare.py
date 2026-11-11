"""Paired comparison of two agents over groups of opponents (local analysis tool, never submitted; E-043).

Same statistics as evaluate.py's paired_comparison (points per game, differences on the same
(opponent, seed, colour) games, percentile bootstrap that resamples whole seeds), but pooled per opponent
GROUP, plus the head-to-head of A vs B and the gates of A. Used for the "pool guard + last-year gain" rule
(user decision 2026-11-11, docs/evaluation.md).

  python eval/group_compare.py --run scr14 --a lab14_stuck --b greedy_v4 \
      --group pool greedy_v3 greedy_v2 feature camper choke exploit_v2 lab5_smart \
      --group lyw lyw_flagrats lyw_pacman_agent ...

E-044 additions: the head-to-head as W-T-L and net wins (W - L)/n with a seed-bootstrap CI (T-62);
--fired KEY ... names the team-brain counters (sentinel 'brain' dict of A) that mean "the play fired in this
game": prints the firing rate, the delta on fired games only and the leak check (a game where the play never
fired must end with B's score); --census prints A's mean counters per game.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import evaluate as ev  # noqa: E402


def gate_counts(records, name):
    """crashes/forfeits caused by `name`, engine time warnings, sentinel violations, max move time."""
    crash = warn = 0
    viol, max_s, games = set(), 0.0, 0
    for r in records:
        for col in ('red', 'blue'):
            if r.get(col) != name or r.get('red_score') is None:
                continue
            games += 1
            eng = r.get(col + '_engine') or {}
            crash += sum(eng.get(k, 0) for k in ('crashed', 'failed_to_load', 'max_warnings', 'move_timeout',
                                                  'total_time', 'startup_timeout'))
            warn += eng.get('warning', 0)
            for agent in (r.get(col + '_sentinel') or {}).values():
                max_s = max(max_s, agent.get('max_s', 0.0))
                viol.update(agent.get('violations', []))
    return games, crash, warn, sorted(viol), max_s


def brain_counts(record, colour):
    """The team-brain counters of the team playing `colour` (both agents hold the same shared dict)."""
    out = {}
    for agent in (record.get(colour + '_sentinel') or {}).values():
        for k, v in (agent.get('brain') or {}).items():
            out[k] = max(out.get(k, 0), v)
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--run', nargs='+', required=True)
    p.add_argument('--a', required=True)
    p.add_argument('--b', required=True)
    p.add_argument('--group', nargs='+', action='append', default=[], metavar=('NAME', 'OPPONENT'))
    p.add_argument('--fired', nargs='+', default=[], metavar='KEY',
                   help="brain counters of A whose sum > 0 means the play fired in that game")
    p.add_argument('--census', action='store_true', help="mean brain counters of A per game")
    args = p.parse_args()
    records = ev.read_records(args.run)
    games = list(ev.per_agent_games(records))
    table = {}
    detail = {}   # (opp, seed, colour) -> {agent: (margin, brain counters)}
    h2h = []
    h2h_seed = {}
    for agent, opp, seed, colour, pts, margin, rec in games:
        if agent == args.a and opp == args.b:
            h2h.append(pts)
            h2h_seed.setdefault(seed, []).append(1 if margin > 0 else (-1 if margin < 0 else 0))
        if agent in (args.a, args.b) and opp not in (args.a, args.b):
            table.setdefault((opp, seed, colour), {})[agent] = pts
            detail.setdefault((opp, seed, colour), {})[agent] = (margin, brain_counts(rec, colour))
    print('### %s vs %s (paired on the same opponent, seed and colour)' % (args.a, args.b))
    print()
    print('| group | opponents | paired games | PPG %s | PPG %s | delta [95%% CI] |' % (args.a, args.b))
    print('|---|---|---|---|---|---|')
    rows = []
    for g in args.group:
        name, opps = g[0], set(g[1:])
        by_seed, pa, pb = {}, [], []
        for (opp, seed, colour), e in table.items():
            if opp in opps and args.a in e and args.b in e:
                by_seed.setdefault(seed, []).append(e[args.a] - e[args.b])
                pa.append(e[args.a])
                pb.append(e[args.b])
        if not by_seed:
            print('| %s | %d | 0 | - | - | - |' % (name, len(opps)))
            continue
        m, lo, hi = ev.bootstrap_ci(by_seed)
        print('| %s | %d | %d | %.3f | %.3f | %+.3f [%+.3f, %+.3f] |'
              % (name, len(opps), len(pa), sum(pa) / len(pa), sum(pb) / len(pb), m, lo, hi))
        for opp in sorted(opps):
            bs, xa, xb = {}, [], []
            for (o, seed, colour), e in table.items():
                if o == opp and args.a in e and args.b in e:
                    bs.setdefault(seed, []).append(e[args.a] - e[args.b])
                    xa.append(e[args.a])
                    xb.append(e[args.b])
            if bs:
                mm, ll, hh = ev.bootstrap_ci(bs)
                rows.append((name, opp, len(xa), sum(xa) / len(xa), sum(xb) / len(xb), mm, ll, hh))
    print()
    if h2h:
        w, t, l = h2h.count(ev.POINTS['win']), h2h.count(ev.POINTS['tie']), h2h.count(ev.POINTS['loss'])
        net, lo, hi = ev.bootstrap_ci(h2h_seed)
        print('Head-to-head %s vs %s: %d-%d-%d (W-T-L) over %d games, PPG %.2f, net wins (W-L)/n %+.3f [%+.3f, %+.3f]'
              % (args.a, args.b, w, t, l, len(h2h), sum(h2h) / len(h2h), net, lo, hi))
    else:
        print('Head-to-head: no games')
    if args.fired or args.census:
        print()
        if args.fired:
            print('Play counters: %s' % ' + '.join(args.fired))
            print()
            print('| group | games | fired | rate | delta on fired games [95%% CI] | not fired | of those, score differs from %s (leak) |'
                  % args.b)
            print('|---|---|---|---|---|---|---|')
        allc, n_all = {}, 0
        for g in args.group:
            name, opps = g[0], set(g[1:])
            fired_seed, n, n_fired, quiet, leak = {}, 0, 0, 0, 0
            for (opp, seed, colour), e in detail.items():
                if opp not in opps or args.a not in e or args.b not in e:
                    continue
                n += 1
                (ma, ca), (mb, _) = e[args.a], e[args.b]
                n_all += 1
                for k, v in ca.items():
                    allc.setdefault(k, [0, 0])
                    allc[k][0] += v
                    allc[k][1] += 1 if v else 0
                if sum(ca.get(k, 0) for k in args.fired) > 0:
                    n_fired += 1
                    pair = table[(opp, seed, colour)]
                    fired_seed.setdefault(seed, []).append(pair[args.a] - pair[args.b])
                else:
                    quiet += 1
                    leak += 1 if ma != mb else 0
            if args.fired and n:
                if fired_seed:
                    m, lo, hi = ev.bootstrap_ci(fired_seed)
                    dtxt = '%+.3f [%+.3f, %+.3f]' % (m, lo, hi)
                else:
                    dtxt = '-'
                print('| %s | %d | %d | %.1f%% | %s | %d | %d |'
                      % (name, n, n_fired, 100.0 * n_fired / n, dtxt, quiet, leak))
        if args.census and n_all:
            print()
            print('Team-brain counters of %s, mean per game over %d games (and games where > 0):' % (args.a, n_all))
            print()
            print('| counter | per game | games > 0 |')
            print('|---|---|---|')
            for k in sorted(allc):
                print('| %s | %.2f | %.1f%% |' % (k, allc[k][0] / float(n_all), 100.0 * allc[k][1] / n_all))
    n, crash, warn, viol, max_s = gate_counts(records, args.a)
    print('Gates of %s: %d games, crashes/forfeits %d, time warnings %d, violations %s, max move %.3f s'
          % (args.a, n, crash, warn, ', '.join(viol) or '-', max_s))
    print()
    print('| group | opponent | games | PPG %s | PPG %s | delta [95%% CI] |' % (args.a, args.b))
    print('|---|---|---|---|---|---|')
    for name, opp, k, a, b, mm, ll, hh in rows:
        print('| %s | %s | %d | %.2f | %.2f | %+.2f [%+.2f, %+.2f] |' % (name, opp, k, a, b, mm, ll, hh))


if __name__ == '__main__':
    main()
