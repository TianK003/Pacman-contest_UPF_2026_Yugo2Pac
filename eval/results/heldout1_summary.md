### Summary: 800 games, 4 agents, 100 seeds

| agent | games | W-T-L | PPG [95% CI] | win % [exact 95% CI] | avg margin | crash/forfeit | time warnings | max move s | p95 move s | over budget | violations |
|---|---|---|---|---|---|---|---|---|---|---|---|
| greedy | 400 | 111-36-253 | 0.92 [0.79, 1.06] | 28 [23, 32] | -3.2 | 0 | 0 | 0.085 | 0.003 | 0 | - |
| greedy_v2 | 400 | 146-25-229 | 1.16 [1.01, 1.30] | 36 [32, 41] | -1.7 | 0 | 0 | 0.098 | 0.002 | 0 | - |
| heldout_a | 400 | 198-36-166 | 1.57 [1.38, 1.77] | 50 [44, 55] | +1.6 | 0 | 0 | 0.083 | 0.008 | 0 | - |
| heldout_b | 400 | 284-25-91 | 2.19 [2.04, 2.34] | 71 [66, 75] | +3.4 | 0 | 0 | 0.121 | 0.044 | 0 | - |

PPG CIs: seed-clustered percentile bootstrap. They are too narrow near PPG 0 or 3 (E-004: ~73% coverage at a 97% win rate), so trust the exact win-rate CI there.

Head-to-head PPG (row agent vs column opponent; 3 = always wins):

| | greedy | greedy_v2 | heldout_a | heldout_b |
|---|---|---|---|---|
| greedy | - | - | 1.25 | 0.60 |
| greedy_v2 | - | - | 1.43 | 0.89 |
| heldout_a | 1.65 | 1.50 | - | - |
| heldout_b | 2.33 | 2.06 | - | - |

Diagnostics (team totals per game; kills = opponent deaths):

| agent | games | returned | conceded | deaths | kills | food lost | Pacman moves | standoff moves | max carried | 28-finish us / them |
|---|---|---|---|---|---|---|---|---|---|---|
| greedy | 400 | 9.0 | 12.2 | 1.48 | 0.41 | 2.7 | 128 | 216 | 4.7 | 2 / 9 |
| greedy_v2 | 400 | 11.7 | 13.5 | 1.47 | 0.45 | 3.3 | 145 | 159 | 7.4 | 8 / 9 |
| heldout_a | 400 | 13.1 | 11.5 | 0.55 | 1.94 | 1.9 | 152 | 119 | 8.3 | 16 / 3 |
| heldout_b | 400 | 12.5 | 9.2 | 0.31 | 1.01 | 0.6 | 156 | 221 | 7.0 | 2 / 7 |

Paired comparison over 400 shared games: PPG(greedy_v2) - PPG(greedy) = +0.23 [95% CI +0.10, +0.39]

| opponent | games | PPG(greedy_v2) | PPG(greedy) | paired diff [95% CI] |
|---|---|---|---|---|
| heldout_a | 200 | 1.43 | 1.25 | +0.18 [-0.03, +0.41] |
| heldout_b | 200 | 0.89 | 0.60 | +0.29 [+0.07, +0.52] |
