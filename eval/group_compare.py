"""Paired comparison of two agents over groups of opponents (local analysis tool, never submitted; E-043).

Same statistics as evaluate.py's paired_comparison (points per game, differences on the same
(opponent, seed, colour) games, percentile bootstrap that resamples whole seeds), but pooled per opponent
GROUP, plus the head-to-head of A vs B and the gates of A. Used for the "pool guard + last-year gain" rule
(user decision 2026-11-11, docs/evaluation.md).

  python eval/group_compare.py --run scr14 --a lab14_stuck --b greedy_v4 \
      --group pool greedy_v3 greedy_v2 feature camper choke exploit_v2 lab5_smart \
      --group lyw lyw_flagrats lyw_pacman_agent ...
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


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--run', nargs='+', required=True)
    p.add_argument('--a', required=True)
    p.add_argument('--b', required=True)
    p.add_argument('--group', nargs='+', action='append', default=[], metavar=('NAME', 'OPPONENT'))
    args = p.parse_args()
    records = ev.read_records(args.run)
    games = list(ev.per_agent_games(records))
    table = {}
    h2h = []
    for agent, opp, seed, colour, pts, _, _ in games:
        if agent == args.a and opp == args.b:
            h2h.append(pts)
        if agent in (args.a, args.b) and opp not in (args.a, args.b):
            table.setdefault((opp, seed, colour), {})[agent] = pts
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
        print('Head-to-head PPG(%s vs %s) = %.2f over %d games' % (args.a, args.b, sum(h2h) / len(h2h), len(h2h)))
    else:
        print('Head-to-head: no games')
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
