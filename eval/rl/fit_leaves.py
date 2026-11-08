"""Fit the non-deep-learning leaf values for lab v8 (local tooling; numpy in venv_rl/).

Same data, target and train/test split as train_value.py (target: food banked minus food dropped
over the next 30 own moves under the policy that made the data; split: random 300-row chunks).
- table: mean target per (carried, nearest-ghost distance, distance home, side, nearest ghost scared
  long enough to be harmless) cell: 7 x 7 x 7 x 2 x 2 = 1372 cells. Sparse cells are shrunk to the
  (carried, ghost, side) parent, which is shrunk to the carried marginal: (n*mean + K*parent) / (n + K).
  (Side and scared matter: a ghost at distance 1 across the border, or a scared one, is harmless.)
- lin: least squares on the net's 12 features.
Prints held-out R2 for both (and the 12-16-1 net if a leaf_net file is given) and writes
eval/rl/leaf_nondl_<name>.py with LEAF_TABLE and LEAF_LIN constants.

usage: venv_rl\\Scripts\\python.exe eval\\rl\\fit_leaves.py --data d1_lab6off --name v1
"""
import argparse
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
COLS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12]   # as train_value.py
# bucket upper bounds (inclusive); the last bucket is open
CARRY_B = (0, 1, 2, 4, 7, 11)          # -> 7 buckets: 0,1,2,3-4,5-7,8-11,12+
GHOST_B = (1, 2, 3, 5, 8, 12)          # -> 7 buckets: <=1,2,3,4-5,6-8,9-12,13+ (15 = none/far)
HOME_B = (0, 2, 5, 9, 14, 20)          # -> 7 buckets: 0,1-2,3-5,6-9,10-14,15-20,21+


def bucket(v, bounds):
    for k, b in enumerate(bounds):
        if v <= b:
            return k
    return len(bounds)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', nargs='+', required=True)
    ap.add_argument('--name', required=True)
    ap.add_argument('--shrink', type=float, default=30.0)
    ap.add_argument('--net', default=None, help='leaf_net_<x>.py to score on the same test rows')
    args = ap.parse_args()
    Xs, ys = [], []
    for d in args.data:
        z = np.load(os.path.join(HERE, 'data', d + '.npz'))
        Xs.append(z['X'])
        ys.append(z['y'])
    Xall = np.concatenate(Xs).astype(np.float64)
    y = np.concatenate(ys).astype(np.float64)
    n = len(y)
    rng = np.random.RandomState(0)
    chunk = np.arange(n) // 300
    te = (rng.rand(chunk.max() + 1) < 0.2)[chunk]
    print('rows %d (train %d, test %d); y mean %.3f sd %.3f' % (n, (~te).sum(), te.sum(), y.mean(), y.std()))

    # raw values back from the normalised features
    carried = np.rint(Xall[:, 0] * 20).astype(int)
    dhome = np.rint(Xall[:, 1] * 40).astype(int)
    g1 = np.rint(Xall[:, 2] * 15).astype(int)
    sc1 = np.rint(Xall[:, 4] * 40).astype(int)
    kc = np.array([bucket(v, CARRY_B) for v in carried])
    kg = np.array([bucket(v, GHOST_B) for v in g1])
    kh = np.array([bucket(v, HOME_B) for v in dhome])
    ks = (Xall[:, 10] > 0.5).astype(int)                  # on the enemy side (is_pacman)
    kx = (sc1 >= g1 + 1).astype(int)                      # nearest ghost scared long enough
    nb = (len(CARRY_B) + 1, len(GHOST_B) + 1, len(HOME_B) + 1, 2, 2)

    tr = ~te
    s5 = np.zeros(nb)
    n5 = np.zeros(nb)
    np.add.at(s5, (kc[tr], kg[tr], kh[tr], ks[tr], kx[tr]), y[tr])
    np.add.at(n5, (kc[tr], kg[tr], kh[tr], ks[tr], kx[tr]), 1)
    s3 = s5.sum(axis=(2, 4))                              # (carried, ghost, side)
    n3 = n5.sum(axis=(2, 4))
    s1 = s3.sum(axis=(1, 2))
    n1 = n3.sum(axis=(1, 2))
    glob = y[tr].mean()
    K = args.shrink
    m1 = (s1 + K * glob) / (n1 + K)                       # carried marginal, shrunk to the mean
    m3 = (s3 + K * m1[:, None, None]) / (n3 + K)          # (carried, ghost, side), shrunk to carried
    m5 = (s5 + K * m3[:, :, None, :, None]) / (n5 + K)    # full cell, shrunk to (carried, ghost, side)
    n3, m3 = n5, m5
    pred_t = m5[kc[te], kg[te], kh[te], ks[te], kx[te]]
    var = y[te].var()
    r2_table = 1 - ((pred_t - y[te]) ** 2).mean() / var
    print('table R2 (test) %.3f   cells %d, empty %d, < 30 rows %d' % (
        r2_table, n3.size, int((n3 == 0).sum()), int((n3 < 30).sum())))

    X = Xall[:, COLS]
    A = np.hstack([X[tr], np.ones((tr.sum(), 1))])
    w = np.linalg.lstsq(A, y[tr], rcond=None)[0]
    pred_l = np.hstack([X[te], np.ones((te.sum(), 1))]) @ w
    r2_lin = 1 - ((pred_l - y[te]) ** 2).mean() / var
    print('linear R2 (test) %.3f' % r2_lin)

    if args.net:
        ns = {}
        exec(open(os.path.join(HERE, args.net)).read(), ns)
        W1, b1, w2, b2 = [np.array(v) for v in ns['LEAF_NET']]
        h = np.tanh(X[te] @ W1.T + b1)
        pred_n = h @ w2.reshape(-1) + float(np.array(b2).reshape(-1)[0])
        print('net %s R2 (same test rows) %.3f' % (args.net, 1 - ((pred_n - y[te]) ** 2).mean() / var))

    out = os.path.join(HERE, 'leaf_nondl_%s.py' % args.name)
    with open(out, 'w') as fh:
        fh.write('# fitted by eval/rl/fit_leaves.py on %s; test R2 table %.3f, linear %.3f\n' % (
            args.data, r2_table, r2_lin))
        fh.write('# LEAF_TABLE flat, index (((kc * 7 + kg) * 7 + kh) * 2 + side) * 2 + scared; bounds %r %r %r\n' % (
            CARRY_B, GHOST_B, HOME_B))
        flat = m5.reshape(-1)
        fh.write('LEAF_TABLE = (\n')
        for k in range(0, len(flat), 14):
            fh.write('    %s,\n' % ', '.join('%.3f' % v for v in flat[k:k + 14]))
        fh.write(')\n')
        fh.write('# LEAF_LIN: weights for the 12 net features (train_value.py order) + bias\n')
        fh.write('LEAF_LIN = (%s)\n' % ', '.join('%.5f' % v for v in w))
    print('wrote', out)


if __name__ == '__main__':
    main()
