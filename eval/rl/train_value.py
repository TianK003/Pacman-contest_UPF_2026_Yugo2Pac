"""Train the planner's leaf value net (local tooling; venv_rl/ with torch).

Target: food the agent banks minus food it drops by dying over its next 30 own moves, under the
policy that generated the data (Monte-Carlo policy evaluation of the greedy attacker).
Inputs: the 12 planner-computable features (log_team.FEATURE_NAMES minus score, ghost1_visible,
mate_attacking). Model: 12 -> H tanh -> 1 (small, so pure-Python inference stays ~40 us per leaf).
Exports (W1, b1, w2, b2) as plain Python lists to eval/rl/leaf_net_<name>.py for pasting into a team.

usage: venv_rl\\Scripts\\python.exe eval\\rl\\train_value.py --data d1_lab6off [d2 ...] --hidden 16 --name v1
"""
import argparse
import os

import numpy as np
import torch

HERE = os.path.dirname(os.path.abspath(__file__))
COLS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', nargs='+', required=True)
    ap.add_argument('--hidden', type=int, default=16)
    ap.add_argument('--epochs', type=int, default=40)
    ap.add_argument('--name', required=True)
    args = ap.parse_args()
    Xs, ys = [], []
    for d in args.data:
        z = np.load(os.path.join(HERE, 'data', d + '.npz'))
        Xs.append(z['X'][:, COLS])
        ys.append(z['y'])
    X = np.concatenate(Xs).astype(np.float32)
    y = np.concatenate(ys).astype(np.float32)
    n = len(y)
    cut = int(n * 0.8)  # rows of one game are contiguous: this split is (almost) by game
    Xtr, ytr, Xte, yte = X[:cut], y[:cut], X[cut:], y[cut:]
    print('rows %d (train %d, test %d); y mean %.3f sd %.3f' % (n, cut, n - cut, y.mean(), y.std()))

    # linear baseline (least squares)
    A = np.hstack([Xtr, np.ones((cut, 1))])
    w = np.linalg.lstsq(A, ytr, rcond=None)[0]
    pred = np.hstack([Xte, np.ones((n - cut, 1))]) @ w
    r2_lin = 1 - ((pred - yte) ** 2).mean() / yte.var()
    print('linear R2 (test) %.3f' % r2_lin)

    torch.manual_seed(0)
    model = torch.nn.Sequential(torch.nn.Linear(12, args.hidden), torch.nn.Tanh(), torch.nn.Linear(args.hidden, 1))
    opt = torch.optim.Adam(model.parameters(), lr=3e-3)
    Xt, yt = torch.tensor(Xtr), torch.tensor(ytr).unsqueeze(1)
    Xv, yv = torch.tensor(Xte), torch.tensor(yte).unsqueeze(1)
    best = (1e9, None)
    for ep in range(args.epochs):
        perm = torch.randperm(cut)
        model.train()
        for k in range(0, cut, 1024):
            idx = perm[k:k + 1024]
            opt.zero_grad()
            loss = torch.nn.functional.mse_loss(model(Xt[idx]), yt[idx])
            loss.backward()
            opt.step()
        model.eval()
        with torch.no_grad():
            vl = torch.nn.functional.mse_loss(model(Xv), yv).item()
        if vl < best[0]:
            best = (vl, [p.detach().clone() for p in model.parameters()])
        if ep % 10 == 0 or ep == args.epochs - 1:
            print('epoch %d  test mse %.4f  R2 %.3f' % (ep, vl, 1 - vl / float(yte.var())))
    W1, b1, W2, b2 = [p.numpy() for p in best[1]]
    print('best test R2 %.3f (linear %.3f)' % (1 - best[0] / float(yte.var()), r2_lin))
    out = os.path.join(HERE, 'leaf_net_%s.py' % args.name)
    with open(out, 'w') as fh:
        fh.write('# trained by eval/rl/train_value.py on %s; test R2 %.3f\n' % (args.data, 1 - best[0] / float(yte.var())))
        fh.write('LEAF_NET = (\n    %r,\n    %r,\n    %r,\n    %r)\n' % (
            [[round(float(v), 5) for v in row] for row in W1], [round(float(v), 5) for v in b1],
            [round(float(v), 5) for v in W2[0]], round(float(b2[0]), 5)))
    print('wrote', out)


if __name__ == '__main__':
    main()
