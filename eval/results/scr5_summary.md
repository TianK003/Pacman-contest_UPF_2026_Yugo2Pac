### Summary: 4200 games, 9 agents, 100 seeds

| agent | games | W-T-L | PPG [95% CI] | win % [exact 95% CI] | avg margin | crash/forfeit | time warnings | max move s | p95 move s | over budget | violations |
|---|---|---|---|---|---|---|---|---|---|---|---|
| camper | 600 | 138-113-349 | 0.88 [0.74, 1.02] | 23 [20, 27] | -3.1 | 0 | 0 | 0.134 | 0.003 | 0 | - |
| choke | 600 | 207-101-292 | 1.20 [1.05, 1.36] | 34 [31, 38] | -1.6 | 0 | 0 | 0.108 | 0.003 | 0 | - |
| exploit_v2 | 600 | 198-50-352 | 1.07 [0.91, 1.25] | 33 [29, 37] | -2.5 | 0 | 0 | 0.072 | 0.002 | 0 | - |
| feature | 600 | 216-49-335 | 1.16 [0.99, 1.34] | 36 [32, 40] | -2.5 | 0 | 0 | 0.108 | 0.002 | 0 | - |
| greedy | 600 | 128-129-343 | 0.85 [0.72, 0.99] | 21 [18, 25] | -3.1 | 0 | 0 | 0.086 | 0.003 | 0 | - |
| greedy_v2 | 1600 | 714-293-593 | 1.52 [1.43, 1.61] | 45 [42, 47] | +0.8 | 0 | 0 | 0.105 | 0.003 | 0 | - |
| lab3_shadow | 1600 | 871-288-441 | 1.81 [1.74, 1.89] | 54 [52, 57] | +2.6 | 0 | 0 | 0.109 | 0.003 | 0 | - |
| lab4_braid_shadow | 1600 | 882-252-466 | 1.81 [1.73, 1.90] | 55 [53, 58] | +2.3 | 0 | 0 | 0.152 | 0.006 | 0 | - |
| rusher | 600 | 156-105-339 | 0.95 [0.79, 1.12] | 26 [23, 30] | -2.3 | 0 | 0 | 0.086 | 0.003 | 0 | - |

PPG CIs: seed-clustered percentile bootstrap. They are too narrow near PPG 0 or 3 (E-004: ~73% coverage at a 97% win rate), so trust the exact win-rate CI there.

Head-to-head PPG (row agent vs column opponent; 3 = always wins):

| | camper | choke | exploit_v2 | feature | greedy | greedy_v2 | lab3_shadow | lab4_braid_shadow | rusher |
|---|---|---|---|---|---|---|---|---|---|
| camper | - | - | - | - | - | 1.23 | 0.69 | 0.71 | - |
| choke | - | - | - | - | - | 1.36 | 1.19 | 1.06 | - |
| exploit_v2 | - | - | - | - | - | 1.23 | 0.94 | 1.06 | - |
| feature | - | - | - | - | - | 1.26 | 1.01 | 1.21 | - |
| greedy | - | - | - | - | - | 1.07 | 0.74 | 0.75 | - |
| greedy_v2 | 1.57 | 1.41 | 1.69 | 1.62 | 1.69 | - | 1.23 | 1.20 | 1.76 |
| lab3_shadow | 2.10 | 1.67 | 1.97 | 1.92 | 2.04 | 1.54 | - | 1.32 | 1.94 |
| lab4_braid_shadow | 2.12 | 1.81 | 1.87 | 1.73 | 2.06 | 1.61 | 1.38 | - | 1.91 |
| rusher | - | - | - | - | - | 1.04 | 0.88 | 0.94 | - |

Diagnostics (team totals per game; kills = opponent deaths):

| agent | games | returned | conceded | deaths | kills | food lost | Pacman moves | standoff moves | max carried | 28-finish us / them |
|---|---|---|---|---|---|---|---|---|---|---|
| camper | 600 | 6.3 | 9.4 | 0.86 | 0.92 | 1.9 | 73 | 306 | 4.1 | 2 / 2 |
| choke | 600 | 9.6 | 11.2 | 0.99 | 0.98 | 2.4 | 93 | 173 | 6.4 | 2 / 5 |
| exploit_v2 | 600 | 7.9 | 10.3 | 0.29 | 0.86 | 0.5 | 111 | 253 | 6.7 | 10 / 6 |
| feature | 600 | 8.8 | 11.4 | 0.31 | 1.31 | 0.7 | 116 | 236 | 7.1 | 11 / 4 |
| greedy | 600 | 6.8 | 9.9 | 0.96 | 1.07 | 2.1 | 78 | 290 | 4.2 | 1 / 5 |
| greedy_v2 | 1600 | 10.3 | 9.6 | 1.11 | 0.86 | 2.5 | 104 | 218 | 6.7 | 11 / 16 |
| lab3_shadow | 1600 | 10.3 | 7.7 | 1.05 | 0.67 | 2.6 | 106 | 262 | 6.8 | 10 / 11 |
| lab4_braid_shadow | 1600 | 10.5 | 8.2 | 1.09 | 0.71 | 2.7 | 110 | 250 | 6.8 | 12 / 10 |
| rusher | 600 | 8.1 | 10.4 | 0.75 | 1.70 | 1.9 | 102 | 270 | 6.5 | 2 / 2 |

Paired comparison over 1400 shared games: PPG(lab4_braid_shadow) - PPG(lab3_shadow) = -0.01 [95% CI -0.06, +0.04]

| opponent | games | PPG(lab4_braid_shadow) | PPG(lab3_shadow) | paired diff [95% CI] |
|---|---|---|---|---|
| camper | 200 | 2.12 | 2.10 | +0.02 [-0.09, +0.12] |
| choke | 200 | 1.81 | 1.67 | +0.14 [+0.05, +0.24] |
| exploit_v2 | 200 | 1.87 | 1.97 | -0.10 [-0.24, +0.06] |
| feature | 200 | 1.73 | 1.92 | -0.18 [-0.35, -0.02] |
| greedy | 200 | 2.06 | 2.04 | +0.01 [-0.07, +0.10] |
| greedy_v2 | 200 | 1.61 | 1.54 | +0.07 [-0.07, +0.20] |
| rusher | 200 | 1.91 | 1.94 | -0.04 [-0.12, +0.05] |

Diagnostics for lab3_shadow per opponent (team totals per game):

| opponent | games | returned | conceded | deaths | kills | food lost | Pacman moves | standoff moves | max carried | 28-finish us / them |
|---|---|---|---|---|---|---|---|---|---|---|
| camper | 200 | 9.2 | 5.2 | 0.85 | 0.69 | 2.9 | 100 | 319 | 6.1 | 1 / 0 |
| choke | 200 | 11.0 | 9.0 | 0.98 | 0.86 | 2.7 | 114 | 220 | 7.1 | 2 / 1 |
| exploit_v2 | 200 | 10.0 | 6.7 | 0.86 | 0.27 | 2.2 | 106 | 264 | 6.9 | 2 / 3 |
| feature | 200 | 11.1 | 8.1 | 1.30 | 0.34 | 3.4 | 113 | 227 | 7.3 | 0 / 4 |
| greedy | 200 | 9.8 | 6.0 | 1.01 | 0.81 | 2.7 | 107 | 293 | 6.4 | 2 / 0 |
| greedy_v2 | 200 | 11.2 | 9.8 | 1.01 | 0.87 | 2.6 | 114 | 237 | 7.3 | 2 / 1 |
| lab4_braid_shadow | 200 | 9.4 | 9.4 | 0.79 | 0.79 | 2.0 | 89 | 270 | 6.3 | 1 / 2 |
| rusher | 200 | 10.4 | 7.5 | 1.57 | 0.71 | 2.6 | 102 | 265 | 6.6 | 0 / 0 |

Diagnostics for lab4_braid_shadow per opponent (team totals per game):

| opponent | games | returned | conceded | deaths | kills | food lost | Pacman moves | standoff moves | max carried | 28-finish us / them |
|---|---|---|---|---|---|---|---|---|---|---|
| camper | 200 | 9.6 | 5.7 | 0.88 | 0.79 | 3.0 | 104 | 307 | 6.4 | 0 / 0 |
| choke | 200 | 11.3 | 9.0 | 0.97 | 0.95 | 2.6 | 116 | 215 | 7.2 | 1 / 1 |
| exploit_v2 | 200 | 10.4 | 7.7 | 0.90 | 0.28 | 2.3 | 116 | 243 | 7.1 | 3 / 3 |
| feature | 200 | 11.3 | 8.9 | 1.36 | 0.33 | 3.6 | 117 | 211 | 7.4 | 1 / 4 |
| greedy | 200 | 10.1 | 6.3 | 1.02 | 0.90 | 2.7 | 111 | 285 | 6.5 | 2 / 0 |
| greedy_v2 | 200 | 11.4 | 10.1 | 1.04 | 0.92 | 2.6 | 120 | 225 | 7.3 | 2 / 1 |
| lab3_shadow | 200 | 9.4 | 9.4 | 0.79 | 0.79 | 1.9 | 88 | 268 | 6.0 | 2 / 1 |
| rusher | 200 | 10.8 | 8.4 | 1.74 | 0.73 | 2.8 | 106 | 245 | 6.8 | 1 / 0 |

Paired comparison over 1400 shared games: PPG(lab3_shadow) - PPG(greedy_v2) = +0.29 [95% CI +0.19, +0.39]

| opponent | games | PPG(lab3_shadow) | PPG(greedy_v2) | paired diff [95% CI] |
|---|---|---|---|---|
| camper | 200 | 2.10 | 1.57 | +0.54 [+0.29, +0.77] |
| choke | 200 | 1.67 | 1.41 | +0.26 [+0.06, +0.45] |
| exploit_v2 | 200 | 1.97 | 1.69 | +0.28 [+0.07, +0.49] |
| feature | 200 | 1.92 | 1.62 | +0.29 [+0.07, +0.52] |
| greedy | 200 | 2.04 | 1.69 | +0.35 [+0.15, +0.56] |
| lab4_braid_shadow | 200 | 1.32 | 1.20 | +0.12 [-0.10, +0.35] |
| rusher | 200 | 1.94 | 1.76 | +0.17 [+0.00, +0.35] |
