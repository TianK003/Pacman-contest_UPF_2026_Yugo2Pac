"""Map features per RANDOM<seed>, computed with the agent's own code (lab6 GreedyAttacker.map_features
on the real initial GameState), for both colours. Local tooling.

usage: python eval/rl/map_features.py OUT.json SEED [SEED ...]   (or --tuning OFFSET N)
"""
import contextlib
import importlib.util
import io
import json
import os
import random
import sys

CWD = os.getcwd()
REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(REPO, 'pacman-contest', 'src'))
os.chdir(os.path.join(REPO, 'pacman-contest', 'src', 'contest'))

import contest.capture as capture  # noqa: E402
import contest.maze_generator as mg  # noqa: E402
from contest.layout import Layout  # noqa: E402


def load_lab6():
    spec = importlib.util.spec_from_file_location('lab6_feat', os.path.join(REPO, 'teams', 'greedy_lab_v6.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def features_for(seed, lab6):
    state = random.getstate()  # tooling only (never in an agent): keep the caller's RNG untouched
    with contextlib.redirect_stdout(io.StringIO()):
        txt = mg.generate_maze(seed)
    random.setstate(state)
    lay = Layout('RANDOM%d' % seed, txt.split('\n'))
    gs = capture.GameState()
    gs.initialize(lay, 4)
    out = {}
    for idx, colour in ((0, 'red'), (1, 'blue')):
        agent = lab6.GreedyAttacker(idx, lab6.Config())
        with contextlib.redirect_stdout(io.StringIO()):
            agent.register_initial_state(gs)
        out[colour] = agent.features
    return out


def main(argv):
    out_path = os.path.join(CWD, argv[0])
    if argv[1] == '--tuning':
        off, n = int(argv[2]), int(argv[3])
        with open(os.path.join(REPO, 'eval', 'seeds', 'tuning.txt')) as fh:
            seeds = [int(l.split()[0]) for l in fh if l.strip() and not l.startswith('#')][off:off + n]
    else:
        seeds = [int(s) for s in argv[1:]]
    lab6 = load_lab6()
    res = {}
    for s in seeds:
        res[str(s)] = features_for(s, lab6)
    with open(out_path, 'w') as fh:
        json.dump(res, fh, indent=0)
    s0 = str(seeds[0])
    print('features for', len(seeds), 'seeds; first red/blue:')
    print(json.dumps(res[s0]['red'], sort_keys=True))
    print(json.dumps(res[s0]['blue'], sort_keys=True))


if __name__ == '__main__':
    main(sys.argv[1:])
