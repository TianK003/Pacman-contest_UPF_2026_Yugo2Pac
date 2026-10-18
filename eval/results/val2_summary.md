### Summary: 1040 games, 8 agents, 40 seeds

| agent | games | W-T-L | PPG [95% CI] | win % [exact 95% CI] | avg margin | crash/forfeit | time warnings | max move s | p95 move s | over budget | violations |
|---|---|---|---|---|---|---|---|---|---|---|---|
| camper | 160 | 43-33-84 | 1.01 [0.78, 1.26] | 27 [20, 34] | -2.7 | 0 | 0 | 0.040 | 0.001 | 0 | - |
| choke | 160 | 55-40-65 | 1.28 [1.04, 1.53] | 34 [27, 42] | -0.4 | 0 | 0 | 0.035 | 0.001 | 0 | - |
| exploit_v2 | 160 | 69-23-68 | 1.44 [1.12, 1.76] | 43 [35, 51] | -0.5 | 0 | 0 | 0.044 | 0.001 | 0 | - |
| feature | 160 | 61-11-88 | 1.21 [0.90, 1.52] | 38 [31, 46] | -1.7 | 0 | 0 | 0.051 | 0.001 | 0 | - |
| greedy | 160 | 37-31-92 | 0.89 [0.64, 1.16] | 23 [17, 30] | -3.5 | 0 | 0 | 0.049 | 0.001 | 0 | - |
| greedy_v2 | 560 | 267-102-191 | 1.61 [1.48, 1.75] | 48 [43, 52] | +1.6 | 0 | 0 | 0.058 | 0.001 | 0 | - |
| lab3_shadow | 560 | 282-103-175 | 1.69 [1.53, 1.86] | 50 [46, 55] | +2.1 | 0 | 0 | 0.060 | 0.002 | 0 | - |
| rusher | 160 | 40-29-91 | 0.93 [0.68, 1.19] | 25 [19, 32] | -4.0 | 0 | 0 | 0.047 | 0.001 | 0 | - |

PPG CIs: seed-clustered percentile bootstrap. They are too narrow near PPG 0 or 3 (E-004: ~73% coverage at a 97% win rate), so trust the exact win-rate CI there.

Head-to-head PPG (row agent vs column opponent; 3 = always wins):

| | camper | choke | exploit_v2 | feature | greedy | greedy_v2 | lab3_shadow | rusher |
|---|---|---|---|---|---|---|---|---|
| camper | - | - | - | - | - | 1.05 | 0.97 | - |
| choke | - | - | - | - | - | 1.25 | 1.31 | - |
| exploit_v2 | - | - | - | - | - | 1.41 | 1.46 | - |
| feature | - | - | - | - | - | 1.16 | 1.26 | - |
| greedy | - | - | - | - | - | 1.00 | 0.78 | - |
| greedy_v2 | 1.76 | 1.48 | 1.49 | 1.76 | 1.79 | - | 1.25 | 1.76 |
| lab3_shadow | 1.80 | 1.46 | 1.35 | 1.68 | 2.05 | 1.51 | - | 2.01 |
| rusher | - | - | - | - | - | 1.05 | 0.81 | - |

Diagnostics (team totals per game; kills = opponent deaths):

| agent | games | returned | conceded | deaths | kills | food lost | Pacman moves | standoff moves | max carried | 28-finish us / them |
|---|---|---|---|---|---|---|---|---|---|---|
| camper | 160 | 8.4 | 11.1 | 1.11 | 1.07 | 2.9 | 97 | 264 | 5.1 | 0 / 0 |
| choke | 160 | 9.9 | 10.4 | 0.99 | 0.96 | 2.7 | 108 | 147 | 7.2 | 0 / 1 |
| exploit_v2 | 160 | 9.9 | 10.4 | 0.31 | 1.02 | 0.7 | 116 | 234 | 7.5 | 2 / 0 |
| feature | 160 | 10.2 | 11.8 | 0.36 | 1.28 | 0.6 | 122 | 225 | 7.4 | 2 / 0 |
| greedy | 160 | 8.0 | 11.5 | 1.10 | 1.07 | 2.8 | 96 | 249 | 5.1 | 0 / 0 |
| greedy_v2 | 560 | 11.2 | 9.6 | 1.19 | 0.91 | 3.1 | 115 | 203 | 7.2 | 1 / 3 |
| lab3_shadow | 560 | 10.9 | 8.8 | 1.16 | 0.75 | 3.2 | 116 | 232 | 7.4 | 1 / 2 |
| rusher | 160 | 7.9 | 11.8 | 0.76 | 1.66 | 2.3 | 109 | 244 | 6.8 | 0 / 0 |

Paired comparison over 480 shared games: PPG(lab3_shadow) - PPG(greedy_v2) = +0.05 [95% CI -0.10, +0.20]

| opponent | games | PPG(lab3_shadow) | PPG(greedy_v2) | paired diff [95% CI] |
|---|---|---|---|---|
| camper | 80 | 1.80 | 1.76 | +0.04 [-0.25, +0.33] |
| choke | 80 | 1.46 | 1.48 | -0.01 [-0.33, +0.33] |
| exploit_v2 | 80 | 1.35 | 1.49 | -0.14 [-0.46, +0.16] |
| feature | 80 | 1.68 | 1.76 | -0.09 [-0.39, +0.17] |
| greedy | 80 | 2.05 | 1.79 | +0.26 [+0.04, +0.51] |
| rusher | 80 | 2.01 | 1.76 | +0.25 [+0.01, +0.54] |
