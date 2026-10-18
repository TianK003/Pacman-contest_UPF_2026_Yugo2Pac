# Summarise rows_*.json from belief_check.py (E-019; local analysis only).
import json
import sys
from collections import defaultdict


def q(xs, f):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(f * len(xs)))] if xs else float('nan')


rows = json.load(open(sys.argv[1]))
groups = defaultdict(list)
for r in rows:
    groups[r['opp']].append(r)
groups['ALL'] = rows
print('| opponent | hidden rows | truth excluded | mean p(true) | mean E[dist] | median MAP dist | median last-seen dist | invader recall (mass>=0.5 when on our side) | invader precision | invader rows |')
print('|---|---|---|---|---|---|---|---|---|---|')
for opp, rs in groups.items():
    n = len(rs)
    excl = sum(1 for r in rs if r['p_true'] == 0) / n
    pt = sum(r['p_true'] for r in rs) / n
    ee = sum(r['exp_err'] for r in rs if r['exp_err'] is not None) / n
    me = q([r['map_err'] for r in rs if r['map_err'] is not None], 0.5)
    le = q([r['ls_err'] for r in rs], 0.5)
    inv = [r for r in rs if r['true_ours']]
    flag = [r for r in rs if r['mass_ours'] >= 0.5]
    rec = sum(1 for r in inv if r['mass_ours'] >= 0.5) / len(inv) if inv else float('nan')
    prec = sum(1 for r in flag if r['true_ours']) / len(flag) if flag else float('nan')
    print('| %s | %d | %.1f%% | %.2f | %.1f | %d | %d | %.0f%% | %.0f%% | %d |'
          % (opp, n, 100 * excl, pt, ee, me, le, 100 * rec, 100 * prec, len(inv)))
secs = [r['secs'] for r in rows]
print('defender move time: max %.4f s, p99 %.4f s, median %.4f s' % (max(secs), q(secs, .99), q(secs, .5)))
