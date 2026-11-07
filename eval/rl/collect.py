"""Collect attacker-state datasets for value learning (local tooling; run with venv_rl/).

Plays games in-process (worker pool), our team wrapped by eval/rl/log_team.py, and turns each of
our agents' trajectories into rows: features of the state + labels over the next H own moves:
  y_value = food banked by this agent - food it dropped by dying     (food units)
  y_death = 1 if it died within the next 10 own moves
Writes eval/rl/data/<name>.npz (gitignored).

usage: venv_rl\\Scripts\\python.exe eval\\rl\\collect.py --name d1 --team lab6_off --opponents greedy_v3 choke ...
          --seed-offset 0 --n-seeds 100 --workers 10 --horizon 30
"""
import argparse
import contextlib
import io
import multiprocessing as mp
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from game_pool import REPO, league_team, _init, _opts  # noqa: E402

LOG_TEAM = os.path.join(HERE, 'log_team.py')


def labels(traj, start, H):
    rows = []
    T = len(traj)
    ok = [t for t in traj if t[0] != 'error']
    if len(ok) != T:
        traj = ok
        T = len(traj)
    deaths = [0] * T
    for k in range(1, T):
        p, q = traj[k][3], traj[k - 1][3]
        if p == start and q != start and abs(p[0] - q[0]) + abs(p[1] - q[1]) > 1:
            deaths[k] = traj[k - 1][1]  # carried food dropped
            deaths[k] = max(deaths[k], 0) + 0  # keep int
            deaths[k] = (deaths[k], 1)
        else:
            deaths[k] = (0, 0)
    deaths[0] = (0, 0)
    for t in range(T):
        feat, carried, returned, pos, attacking = traj[t]
        if not attacking:
            continue
        end = min(T - 1, t + H)
        banked = traj[end][2] - returned
        lost = sum(deaths[k][0] for k in range(t + 1, end + 1))
        died10 = 1 if any(deaths[k][1] for k in range(t + 1, min(T, t + 11))) else 0
        rows.append((feat, banked - lost, died10, banked, lost))
    return rows


def play_collect(job):
    red, ropts, blue, bopts, seed, our_colour, H = job
    import contest.capture as capture
    argv = ['-r', red, '-b', blue, '-q', '-c', '-l', 'RANDOM%d' % seed, '--delay-step', '0',
            '-u', 'coll_%d' % os.getpid()]
    if ropts:
        argv += ['--redOpts', _opts(ropts)]
    if bopts:
        argv += ['--blueOpts', _opts(bopts)]
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        options = capture.read_command(argv)
        games = capture.run_games(**options)
    g = games[0]
    out = []
    ours = (0, 2) if our_colour == 'red' else (1, 3)
    for i in ours:
        a = g.agents[i]
        log = getattr(a, 'rl_log', None)
        if not log:
            continue
        out.extend(labels(log, a.rl_start, H))
    score = g.state.data.score if our_colour == 'red' else -g.state.data.score
    return out, score, bool(g.agent_crashed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--name', required=True)
    ap.add_argument('--team', required=True)
    ap.add_argument('--fixed', default='')
    ap.add_argument('--opponents', nargs='+', required=True)
    ap.add_argument('--seed-offset', type=int, default=0)
    ap.add_argument('--n-seeds', type=int, default=50)
    ap.add_argument('--workers', type=int, default=10)
    ap.add_argument('--horizon', type=int, default=30)
    args = ap.parse_args()
    path, opts = league_team(args.team)
    if args.fixed:
        opts.update(dict(kv.split('=', 1) for kv in args.fixed.split(',')))
    wrapped = dict(opts, team=path)
    with open(os.path.join(REPO, 'eval', 'seeds', 'tuning.txt')) as fh:
        seeds = [int(l.split()[0]) for l in fh if l.strip() and not l.startswith('#')]
    seeds = seeds[args.seed_offset:args.seed_offset + args.n_seeds]
    jobs = []
    for o in args.opponents:
        op, oo = league_team(o)
        for s in seeds:
            jobs.append((LOG_TEAM, wrapped, op, oo, s, 'red', args.horizon))
            jobs.append((op, oo, LOG_TEAM, wrapped, s, 'blue', args.horizon))
    ctx = mp.get_context('spawn')
    pool = ctx.Pool(args.workers, initializer=_init, maxtasksperchild=30)
    t0 = time.time()
    X, Y, D, B, L = [], [], [], [], []
    pts = []
    crashed = 0
    for rows, score, cr in pool.imap_unordered(play_collect, jobs):
        crashed += cr
        pts.append(3 if score > 0 else (1 if score == 0 else 0))
        for f, y, d, b, l in rows:
            X.append(f)
            Y.append(y)
            D.append(d)
            B.append(b)
            L.append(l)
    pool.close()
    os.makedirs(os.path.join(HERE, 'data'), exist_ok=True)
    out = os.path.join(HERE, 'data', args.name + '.npz')
    np.savez_compressed(out, X=np.array(X, dtype=np.float32), y=np.array(Y, dtype=np.float32),
                        death=np.array(D, dtype=np.float32), banked=np.array(B, dtype=np.float32),
                        lost=np.array(L, dtype=np.float32))
    print('games %d  rows %d  ppg %.2f  crashed %d  %.0fs -> %s' % (
        len(jobs), len(X), float(np.mean(pts)), crashed, time.time() - t0, out))


if __name__ == '__main__':
    main()
