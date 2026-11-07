"""Mode x map table and map-feature selectors (local analysis; run with venv_rl/ for numpy).

For every candidate mode m and map seed s: PPG(m, s) over all games against the pool (both colours),
and the paired gain D(m, s) = PPG(m, s) - PPG(base, s) on the same (opponent, seed, colour) games.
Then compares, with K-fold cross-validation over SEEDS (maps never seen in training):
  - 'best constant': play the mode with the highest mean gain on the training folds;
  - 'oracle': the per-map best mode (an upper bound inflated by noise, the winner's curse);
  - 'ridge-k': per-mode ridge regression of D on map features; play argmax prediction if > 0;
  - 'stump': per mode, the best single-feature threshold rule.

usage: venv_rl\\Scripts\\python.exe eval\\rl\\mode_table.py --runs n1_base n1_modes --base lab5_smart
          --modes lab6_focus_top ... --features eval/rl/feat_tuning_260_60.json [--export]
"""
import argparse
import json
import os
from collections import defaultdict

import numpy as np

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))


def points(sc):
    return 3.0 if sc > 0 else (1.0 if sc == 0 else 0.0)


def load(runs):
    recs = []
    for r in runs:
        with open(os.path.join(REPO, 'eval', 'results', r + '.jsonl')) as fh:
            for line in fh:
                d = json.loads(line)
                if d.get('harness_error') is None and d.get('red_score') is not None:
                    recs.append(d)
    return recs


def game_points(recs, agents):
    """{agent: {(opp, seed, colour): points}}"""
    out = defaultdict(dict)
    for d in recs:
        for colour, me, opp in (('red', d['red'], d['blue']), ('blue', d['blue'], d['red'])):
            if me in agents:
                sc = d['red_score'] if colour == 'red' else -d['red_score']
                out[me][(opp, d['seed'], colour)] = points(sc)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--runs', nargs='+', required=True)
    ap.add_argument('--base', required=True)
    ap.add_argument('--modes', nargs='+', required=True)
    ap.add_argument('--features', required=True)
    ap.add_argument('--exclude-opp', nargs='*', default=[])
    ap.add_argument('--folds', type=int, default=10)
    ap.add_argument('--lam', type=float, default=10.0)
    ap.add_argument('--feat-names', nargs='*', default=None)
    ap.add_argument('--export', action='store_true')
    args = ap.parse_args()

    recs = load(args.runs)
    gp = game_points(recs, set([args.base] + args.modes))
    with open(os.path.join(REPO, args.features)) as fh:
        feats = json.load(fh)
    base = gp[args.base]
    # opponents common to all; exclude mirror games of modes vs base (not paired)
    seeds = sorted(set(k[1] for k in base))
    seeds = [s for s in seeds if str(s) in feats]
    D = np.zeros((len(seeds), len(args.modes)))
    P = np.zeros((len(seeds), len(args.modes) + 1))
    n_games = np.zeros((len(seeds), len(args.modes)))
    for j, m in enumerate(args.modes):
        g = gp[m]
        for i, s in enumerate(seeds):
            keys = [k for k in g if k[1] == s and k in base and k[0] not in args.exclude_opp
                    and k[0] not in (args.base, m)]
            if not keys:
                D[i, j] = np.nan
                continue
            D[i, j] = np.mean([g[k] - base[k] for k in keys])
            P[i, j + 1] = np.mean([g[k] for k in keys])
            P[i, 0] = np.mean([base[k] for k in keys])
            n_games[i, j] = len(keys)
    ok = ~np.isnan(D).any(axis=1)
    D = D[ok]
    seeds = [s for s, o in zip(seeds, ok) if o]
    names = args.feat_names or sorted(feats[str(seeds[0])]['red'].keys())
    X = np.array([[feats[str(s)]['red'][k] for k in names] for s in seeds])
    print('maps: %d   games per (mode, map): %d-%d' % (len(seeds), n_games.min(), n_games.max()))
    print('\nmean paired gain per mode (vs %s), 95%% CI over maps:' % args.base)
    for j, m in enumerate(args.modes):
        d = D[:, j]
        se = d.std(ddof=1) / np.sqrt(len(d))
        print('  %-22s %+.3f  [%+.3f, %+.3f]   maps better/worse %d/%d' % (
            m, d.mean(), d.mean() - 1.96 * se, d.mean() + 1.96 * se, (d > 0).sum(), (d < 0).sum()))
    # correlations feature x gain
    print('\ncorrelation of map features with each mode\'s gain (|r| > 0.25 shown):')
    Xs = (X - X.mean(0)) / (X.std(0) + 1e-9)
    for j, m in enumerate(args.modes):
        d = D[:, j]
        r = [(np.corrcoef(Xs[:, k], d)[0, 1], names[k]) for k in range(len(names))]
        r = [t for t in r if abs(t[0]) > 0.25]
        print('  %-22s %s' % (m, ', '.join('%s %+.2f' % (n, v) for v, n in sorted(r, reverse=True))))

    # cross-validated selection
    rng = np.random.RandomState(0)
    order = rng.permutation(len(seeds))
    folds = np.array_split(order, args.folds)
    res = defaultdict(list)
    for f in folds:
        tr = np.setdiff1d(order, f)
        mu, sd = X[tr].mean(0), X[tr].std(0) + 1e-9
        Xtr = (X[tr] - mu) / sd
        Xte = (X[f] - mu) / sd
        # best constant
        bc = int(np.argmax(D[tr].mean(0)))
        res['best constant'].extend(D[f, bc] if D[tr, bc].mean() > 0 else np.zeros(len(f)))
        res['oracle (noise-inflated)'].extend(np.maximum(D[f].max(1), 0))
        # ridge per mode
        A = np.hstack([Xtr, np.ones((len(tr), 1))])
        At = np.hstack([Xte, np.ones((len(f), 1))])
        preds = np.zeros((len(f), len(args.modes)))
        for j in range(len(args.modes)):
            reg = args.lam * np.eye(A.shape[1])
            reg[-1, -1] = 0
            w = np.linalg.solve(A.T @ A + reg, A.T @ D[tr, j])
            preds[:, j] = At @ w
        pick = preds.argmax(1)
        got = np.where(preds.max(1) > 0, D[f, pick], 0.0)
        res['ridge'].extend(got)
        # stump per mode: best single feature threshold among training medians/quartiles
        stump_pred = np.zeros((len(f), len(args.modes)))
        for j in range(len(args.modes)):
            best = (D[tr, j].mean(), None)
            for k in range(len(names)):
                for q in (25, 50, 75):
                    t = np.percentile(Xtr[:, k], q)
                    for sign in (1, -1):
                        mask = sign * (Xtr[:, k] - t) > 0
                        if mask.sum() < 5:
                            continue
                        v = (D[tr, j][mask].sum()) / len(tr)  # gain if we play j only on mask maps
                        if v > best[0]:
                            best = (v, (k, t, sign, D[tr, j][mask].mean()))
            if best[1] is None:
                stump_pred[:, j] = D[tr, j].mean()
            else:
                k, t, sign, mv = best[1]
                stump_pred[:, j] = np.where(sign * (Xte[:, k] - t) > 0, mv, -1.0)
        pick = stump_pred.argmax(1)
        res['stump'].extend(np.where(stump_pred.max(1) > 0, D[f, pick], 0.0))
    print('\ncross-validated gain of the selection policy over %s (%d folds over maps):' % (args.base, args.folds))
    for k, v in res.items():
        v = np.array(v)
        se = v.std(ddof=1) / np.sqrt(len(v))
        print('  %-26s %+.3f  [%+.3f, %+.3f]' % (k, v.mean(), v.mean() - 1.96 * se, v.mean() + 1.96 * se))

    if args.export:
        mu, sd = X.mean(0), X.std(0) + 1e-9
        A = np.hstack([(X - mu) / sd, np.ones((len(seeds), 1))])
        models = {}
        for j, m in enumerate(args.modes):
            reg = args.lam * np.eye(A.shape[1])
            reg[-1, -1] = 0
            w = np.linalg.solve(A.T @ A + reg, A.T @ D[:, j])
            # fold the standardisation into raw-feature weights
            raw = {names[k]: float(w[k] / sd[k]) for k in range(len(names))}
            bias = float(w[-1] - sum(w[k] * mu[k] / sd[k] for k in range(len(names))))
            models[m] = (bias, raw)
        print('\nFOCUS_MODELS =', json.dumps(models, indent=1))


if __name__ == '__main__':
    main()
