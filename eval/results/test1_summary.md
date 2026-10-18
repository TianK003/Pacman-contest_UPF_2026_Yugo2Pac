### Summary: 3400 games, 10 agents, 100 seeds

| agent | games | W-T-L | PPG [95% CI] | win % [exact 95% CI] | avg margin | crash/forfeit | time warnings | max move s | p95 move s | over budget | violations |
|---|---|---|---|---|---|---|---|---|---|---|---|
| camper | 400 | 118-50-232 | 1.01 [0.85, 1.18] | 30 [25, 34] | -3.1 | 0 | 0 | 0.076 | 0.002 | 0 | - |
| choke | 400 | 151-69-180 | 1.30 [1.17, 1.44] | 38 [33, 43] | -0.3 | 0 | 0 | 0.074 | 0.002 | 0 | - |
| exploit_v2 | 400 | 138-58-204 | 1.18 [1.00, 1.37] | 34 [30, 39] | -1.6 | 0 | 0 | 0.049 | 0.001 | 0 | - |
| feature | 400 | 116-33-251 | 0.95 [0.80, 1.10] | 29 [25, 34] | -3.7 | 0 | 0 | 0.085 | 0.002 | 0 | - |
| greedy | 400 | 93-53-254 | 0.83 [0.69, 0.98] | 23 [19, 28] | -3.6 | 0 | 0 | 0.081 | 0.002 | 0 | - |
| greedy_v2 | 1800 | 867-196-737 | 1.55 [1.49, 1.63] | 48 [46, 51] | +0.8 | 0 | 0 | 0.098 | 0.003 | 0 | - |
| greedy_v3 | 1800 | 999-232-569 | 1.79 [1.71, 1.88] | 56 [53, 58] | +2.3 | 0 | 0 | 0.091 | 0.005 | 0 | - |
| heldout_a | 400 | 192-22-186 | 1.50 [1.32, 1.67] | 48 [43, 53] | +0.5 | 0 | 0 | 0.068 | 0.003 | 0 | - |
| heldout_b | 400 | 226-26-148 | 1.76 [1.58, 1.94] | 56 [51, 61] | +0.6 | 0 | 0 | 0.062 | 0.013 | 0 | - |
| rusher | 400 | 105-51-244 | 0.92 [0.76, 1.07] | 26 [22, 31] | -2.6 | 0 | 0 | 0.070 | 0.002 | 0 | - |

PPG CIs: seed-clustered percentile bootstrap. They are too narrow near PPG 0 or 3 (E-004: ~73% coverage at a 97% win rate), so trust the exact win-rate CI there.

Head-to-head PPG (row agent vs column opponent; 3 = always wins):

| | camper | choke | exploit_v2 | feature | greedy | greedy_v2 | greedy_v3 | heldout_a | heldout_b | rusher |
|---|---|---|---|---|---|---|---|---|---|---|
| camper | - | - | - | - | - | 1.22 | 0.80 | - | - | - |
| choke | - | - | - | - | - | 1.46 | 1.16 | - | - | - |
| exploit_v2 | - | - | - | - | - | 1.28 | 1.07 | - | - | - |
| feature | - | - | - | - | - | 1.08 | 0.82 | - | - | - |
| greedy | - | - | - | - | - | 0.96 | 0.69 | - | - | - |
| greedy_v2 | 1.67 | 1.40 | 1.60 | 1.83 | 1.91 | - | 1.27 | 1.46 | 1.00 | 1.84 |
| greedy_v3 | 2.06 | 1.65 | 1.75 | 2.10 | 2.17 | 1.56 | - | 1.44 | 1.35 | 2.07 |
| heldout_a | - | - | - | - | - | 1.49 | 1.50 | - | - | - |
| heldout_b | - | - | - | - | - | 1.95 | 1.57 | - | - | - |
| rusher | - | - | - | - | - | 1.03 | 0.80 | - | - | - |

Diagnostics (team totals per game; kills = opponent deaths):

| agent | games | returned | conceded | deaths | kills | food lost | Pacman moves | standoff moves | max carried | 28-finish us / them |
|---|---|---|---|---|---|---|---|---|---|---|
| camper | 400 | 7.7 | 10.9 | 1.05 | 0.89 | 2.2 | 91 | 270 | 4.4 | 0 / 6 |
| choke | 400 | 11.0 | 11.3 | 0.96 | 0.88 | 2.7 | 106 | 159 | 7.0 | 3 / 6 |
| exploit_v2 | 400 | 9.1 | 10.8 | 0.32 | 0.84 | 0.7 | 121 | 238 | 6.7 | 8 / 3 |
| feature | 400 | 9.0 | 12.7 | 0.34 | 1.13 | 0.6 | 122 | 229 | 6.6 | 9 / 2 |
| greedy | 400 | 8.1 | 11.8 | 1.06 | 1.03 | 2.1 | 93 | 260 | 4.6 | 0 / 4 |
| greedy_v2 | 1800 | 11.7 | 10.9 | 1.14 | 0.78 | 2.8 | 123 | 188 | 7.3 | 24 / 31 |
| greedy_v3 | 1800 | 11.8 | 9.5 | 1.07 | 0.63 | 2.8 | 125 | 224 | 7.5 | 26 / 23 |
| heldout_a | 400 | 13.5 | 13.0 | 0.52 | 1.61 | 2.1 | 158 | 131 | 8.7 | 23 / 4 |
| heldout_b | 400 | 12.4 | 11.9 | 0.38 | 0.94 | 0.5 | 146 | 192 | 7.0 | 1 / 11 |
| rusher | 400 | 9.3 | 11.9 | 0.76 | 1.66 | 1.7 | 120 | 236 | 7.0 | 4 / 8 |

Paired comparison over 1600 shared games: PPG(greedy_v3) - PPG(greedy_v2) = +0.23 [95% CI +0.15, +0.32]

| opponent | games | PPG(greedy_v3) | PPG(greedy_v2) | paired diff [95% CI] |
|---|---|---|---|---|
| camper | 200 | 2.06 | 1.67 | +0.39 [+0.17, +0.62] |
| choke | 200 | 1.65 | 1.40 | +0.26 [+0.01, +0.49] |
| exploit_v2 | 200 | 1.75 | 1.60 | +0.15 [-0.07, +0.36] |
| feature | 200 | 2.10 | 1.83 | +0.27 [-0.01, +0.53] |
| greedy | 200 | 2.17 | 1.91 | +0.26 [+0.04, +0.47] |
| heldout_a | 200 | 1.44 | 1.46 | -0.02 [-0.26, +0.21] |
| heldout_b | 200 | 1.35 | 1.00 | +0.35 [+0.11, +0.59] |
| rusher | 200 | 2.07 | 1.84 | +0.23 [+0.01, +0.43] |

### Pool only (6 non-mirror reference-pool members)

Paired comparison over 1200 shared games: PPG(greedy_v3) - PPG(greedy_v2) = +0.26 [95% CI +0.15, +0.36]

### Held-out only (totals, T-53)

Paired comparison over 400 shared games: PPG(greedy_v3) - PPG(greedy_v2) = +0.17 [95% CI -0.00, +0.33]
