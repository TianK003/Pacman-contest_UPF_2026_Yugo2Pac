"""Draw eval/seeds/validation2.txt: a fresh validation list (2026-11-08, user decision, E-036).

The first lists (tuning / validation / test) were drawn once with random.Random(20261016). validation.txt was used up by
2026-11-08 (seeds 1-300, E-002 ... E-032). This draws 300 new 8-digit seeds (like the tournament's RANDOM<seed> maps)
from a new generator seed and rejects any seed already in tuning.txt, validation.txt or test.txt.

Run once from the repo root: python eval/seeds/make_validation2.py   (refuses to overwrite an existing list)
"""
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'validation2.txt')
GEN_SEED = 20261108
N = 300


def read(name):
    with open(os.path.join(HERE, name)) as f:
        return [int(line) for line in f if line.strip() and not line.startswith('#')]


def main():
    if os.path.exists(OUT):
        raise SystemExit('validation2.txt exists; not overwriting')
    used = set(read('tuning.txt')) | set(read('validation.txt')) | set(read('test.txt'))
    rng = random.Random(GEN_SEED)
    seeds = []
    while len(seeds) < N:
        s = rng.randrange(10 ** 7, 10 ** 8)
        if s not in used:
            used.add(s)
            seeds.append(s)
    with open(OUT, 'w', newline='\n') as f:
        f.write('# Validation seeds, list 2 (validation.txt was used up on 2026-11-08). For accept/reject decisions only '
                '(docs/evaluation.md). Drawn by make_validation2.py with random.Random(%d); none is in tuning, validation '
                'or test.\n' % GEN_SEED)
        for s in seeds:
            f.write('%d\n' % s)
    print('wrote %d seeds to %s' % (len(seeds), OUT))


if __name__ == '__main__':
    main()
