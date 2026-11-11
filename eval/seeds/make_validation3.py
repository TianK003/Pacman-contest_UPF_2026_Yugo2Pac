"""Draw eval/seeds/validation3.txt: a third validation list (2026-11-11, user decision, E-044).

The first lists (tuning / validation / test) were drawn once with random.Random(20261016); validation2.txt with
random.Random(20261108) (240 of its 300 seeds used by 2026-11-11). This draws 300 new 8-digit seeds (like the tournament's
RANDOM<seed> maps) from a new generator seed and rejects any seed already in tuning, validation, validation2 or test.

Run once from the repo root: python eval/seeds/make_validation3.py   (refuses to overwrite an existing list)
"""
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'validation3.txt')
GEN_SEED = 20261111
N = 300


def read(name):
    with open(os.path.join(HERE, name)) as f:
        return [int(line) for line in f if line.strip() and not line.startswith('#')]


def main():
    if os.path.exists(OUT):
        raise SystemExit('validation3.txt exists; not overwriting')
    used = set(read('tuning.txt')) | set(read('validation.txt')) | set(read('validation2.txt')) | set(read('test.txt'))
    rng = random.Random(GEN_SEED)
    seeds = []
    while len(seeds) < N:
        s = rng.randrange(10 ** 7, 10 ** 8)
        if s not in used:
            used.add(s)
            seeds.append(s)
    with open(OUT, 'w', newline='\n') as f:
        f.write('# Validation seeds, list 3 (2026-11-11, E-044). For accept/reject decisions only '
                '(docs/evaluation.md). Drawn by make_validation3.py with random.Random(%d); none is in tuning, validation, validation2 '
                'or test.\n' % GEN_SEED)
        for s in seeds:
            f.write('%d\n' % s)
    print('wrote %d seeds to %s' % (len(seeds), OUT))


if __name__ == '__main__':
    main()
