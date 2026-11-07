"""In-process parallel game runner for offline tuning / RL (local tooling only, never submitted).

Each worker process imports the engine once and plays games through capture.read_command +
capture.run_games with -q -c (time limits on, crashes count), so a game costs only the game itself.
Team options are passed as create_team string kwargs (--redOpts / --blueOpts), so arbitrary
parameter vectors can be evaluated without league entries.

    from game_pool import GamePool, league_team
    pool = GamePool(workers=10)
    jobs = [(red_path, red_opts, blue_path, blue_opts, seed, tag), ...]
    for res in pool.run(jobs): ...   # dicts: tag, seed, score (red-relative), crashed, timeout, warnings

Works with venv/ (stdlib) and venv_rl/ (both Python 3.8.10, contest installed editable).
"""
import contextlib
import io
import json
import multiprocessing as mp
import os
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
CONTEST = os.path.join(REPO, 'pacman-contest', 'src', 'contest')
LEAGUE = os.path.join(REPO, 'eval', 'league.json')


def league_team(name):
    """(absolute path, opts dict) of a league entry."""
    with open(LEAGUE, encoding='utf-8') as fh:
        league = json.load(fh)
    e = league[name]
    path = e['path']
    if not os.path.isabs(path):
        path = os.path.join(REPO, path)
    return path, dict(e.get('opts', {}))


def _init():
    sys.path.insert(0, os.path.join(REPO, 'pacman-contest', 'src'))
    os.chdir(CONTEST)


def _opts(d):
    return ','.join('%s=%s' % (k, d[k]) for k in sorted(d))


def play(job):
    red_path, red_opts, blue_path, blue_opts, seed, tag = job
    import contest.capture as capture
    argv = ['-r', red_path, '-b', blue_path, '-q', '-c', '-l', 'RANDOM%d' % seed,
            '--delay-step', '0', '-u', 'pool_%d' % os.getpid()]
    if red_opts:
        argv += ['--redOpts', _opts(red_opts)]
    if blue_opts:
        argv += ['--blueOpts', _opts(blue_opts)]
    t0 = time.time()
    err = None
    score = 0
    crashed = timeout = False
    warnings = 0
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            options = capture.read_command(argv)
            games = capture.run_games(**options)
        g = games[0]
        score = g.state.data.score
        crashed = bool(g.agent_crashed)
        timeout = bool(getattr(g, 'agent_timeout', False))
        warnings = getattr(g, 'total_agent_time_warnings', 0)
        if isinstance(warnings, (list, tuple)):
            warnings = sum(warnings)
    except Exception as exc:  # harness failure, not an agent failure (agent ones are caught by -c)
        err = repr(exc)
    return {'tag': tag, 'seed': seed, 'score': score, 'crashed': crashed, 'timeout': timeout,
            'warnings': warnings, 'wall': time.time() - t0, 'error': err}


class GamePool:
    def __init__(self, workers=10):
        ctx = mp.get_context('spawn')
        self.pool = ctx.Pool(processes=workers, initializer=_init, maxtasksperchild=40)

    def run(self, jobs):
        return list(self.pool.imap_unordered(play, jobs, chunksize=1))

    def close(self):
        self.pool.close()
        self.pool.join()


def points(score_for_us):
    return 3 if score_for_us > 0 else (1 if score_for_us == 0 else 0)


def paired_jobs(cand_path, cand_opts, opponents, seeds, tag):
    """Both colours on every (opponent, seed). opponents: list of (name, path, opts)."""
    jobs = []
    for name, path, opts in opponents:
        for s in seeds:
            jobs.append((cand_path, cand_opts, path, opts, s, (tag, name, s, 'red')))
            jobs.append((path, opts, cand_path, cand_opts, s, (tag, name, s, 'blue')))
    return jobs


def our_points(res):
    """Points for the candidate from a result whose tag ends with the candidate's colour."""
    colour = res['tag'][-1]
    sc = res['score'] if colour == 'red' else -res['score']
    if res['error']:
        return None
    return points(sc)


if __name__ == '__main__':
    # quick self-test: lab6_off vs greedy_v3 on 2 seeds, both colours
    p6, o6 = league_team('lab6_off')
    pg, og = league_team('greedy_v3')
    pool = GamePool(workers=4)
    t0 = time.time()
    res = pool.run(paired_jobs(p6, o6, [('greedy_v3', pg, og)], [11, 12], 'test'))
    for r in res:
        print(r['tag'], r['score'], r['crashed'], r['warnings'], round(r['wall'], 2), r['error'])
    print('total %.1fs' % (time.time() - t0))
    pool.close()
