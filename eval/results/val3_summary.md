### Summary: 1040 games, 8 agents, 40 seeds

| agent | games | W-T-L | PPG [95% CI] | win % [exact 95% CI] | avg margin | crash/forfeit | time warnings | max move s | p95 move s | over budget | violations |
|---|---|---|---|---|---|---|---|---|---|---|---|
| camper | 160 | 41-28-91 | 0.94 [0.69, 1.21] | 26 [19, 33] | -3.1 | 0 | 0 | 0.069 | 0.002 | 0 | - |
| choke | 160 | 49-28-83 | 1.09 [0.89, 1.31] | 31 [24, 38] | -2.4 | 0 | 0 | 0.052 | 0.001 | 0 | - |
| exploit_v2 | 160 | 65-13-82 | 1.30 [0.99, 1.66] | 41 [33, 49] | -1.7 | 0 | 0 | 0.063 | 0.001 | 0 | - |
| feature | 160 | 48-16-96 | 1.00 [0.70, 1.30] | 30 [23, 38] | -2.5 | 0 | 0 | 0.052 | 0.001 | 0 | - |
| greedy | 160 | 30-24-106 | 0.71 [0.49, 0.94] | 19 [13, 26] | -3.7 | 0 | 0 | 0.054 | 0.001 | 0 | - |
| greedy_v2 | 560 | 270-90-200 | 1.61 [1.46, 1.77] | 48 [44, 52] | +1.2 | 0 | 0 | 0.104 | 0.001 | 0 | - |
| lab3_shadow | 560 | 335-86-139 | 1.95 [1.77, 2.11] | 60 [56, 64] | +3.3 | 0 | 0 | 0.085 | 0.002 | 0 | - |
| rusher | 160 | 46-27-87 | 1.03 [0.78, 1.29] | 29 [22, 36] | -2.5 | 0 | 0 | 0.094 | 0.001 | 0 | - |

PPG CIs: seed-clustered percentile bootstrap. They are too narrow near PPG 0 or 3 (E-004: ~73% coverage at a 97% win rate), so trust the exact win-rate CI there.

Head-to-head PPG (row agent vs column opponent; 3 = always wins):

| | camper | choke | exploit_v2 | feature | greedy | greedy_v2 | lab3_shadow | rusher |
|---|---|---|---|---|---|---|---|---|
| camper | - | - | - | - | - | 1.24 | 0.65 | - |
| choke | - | - | - | - | - | 1.18 | 1.01 | - |
| exploit_v2 | - | - | - | - | - | 1.51 | 1.09 | - |
| feature | - | - | - | - | - | 1.16 | 0.84 | - |
| greedy | - | - | - | - | - | 0.68 | 0.75 | - |
| greedy_v2 | 1.61 | 1.62 | 1.44 | 1.73 | 2.14 | - | 0.96 | 1.75 |
| lab3_shadow | 2.15 | 1.84 | 1.80 | 2.08 | 2.14 | 1.79 | - | 1.85 |
| rusher | - | - | - | - | - | 1.07 | 0.99 | - |

Diagnostics (team totals per game; kills = opponent deaths):

| agent | games | returned | conceded | deaths | kills | food lost | Pacman moves | standoff moves | max carried | 28-finish us / them |
|---|---|---|---|---|---|---|---|---|---|---|
| camper | 160 | 6.4 | 9.5 | 1.27 | 0.97 | 2.2 | 85 | 282 | 4.0 | 0 / 0 |
| choke | 160 | 8.7 | 11.1 | 1.19 | 1.07 | 3.0 | 101 | 149 | 6.0 | 0 / 0 |
| exploit_v2 | 160 | 7.5 | 9.2 | 0.32 | 0.85 | 0.6 | 118 | 249 | 6.2 | 0 / 0 |
| feature | 160 | 8.7 | 11.2 | 0.42 | 1.34 | 0.7 | 124 | 236 | 7.0 | 0 / 0 |
| greedy | 160 | 6.2 | 9.9 | 1.34 | 1.20 | 2.5 | 84 | 268 | 3.9 | 0 / 0 |
| greedy_v2 | 560 | 10.1 | 8.9 | 1.17 | 1.14 | 2.8 | 109 | 208 | 6.6 | 0 / 1 |
| lab3_shadow | 560 | 10.0 | 6.6 | 1.18 | 0.82 | 3.1 | 107 | 246 | 6.8 | 0 / 0 |
| rusher | 160 | 8.0 | 10.5 | 1.24 | 1.68 | 2.5 | 105 | 241 | 6.5 | 1 / 0 |

Paired comparison over 480 shared games: PPG(lab3_shadow) - PPG(greedy_v2) = +0.26 [95% CI +0.07, +0.44]

| opponent | games | PPG(lab3_shadow) | PPG(greedy_v2) | paired diff [95% CI] |
|---|---|---|---|---|
| camper | 80 | 2.15 | 1.61 | +0.54 [+0.17, +0.89] |
| choke | 80 | 1.84 | 1.62 | +0.21 [-0.05, +0.47] |
| exploit_v2 | 80 | 1.80 | 1.44 | +0.36 [+0.06, +0.69] |
| feature | 80 | 2.08 | 1.73 | +0.35 [-0.04, +0.72] |
| greedy | 80 | 2.14 | 2.14 | +0.00 [-0.29, +0.26] |
| rusher | 80 | 1.85 | 1.75 | +0.10 [-0.23, +0.44] |

### Pooled with val2 (validation seeds 101-180; pre-registered decision basis, E-019)

Paired comparison over 960 shared games: PPG(lab3_shadow) - PPG(greedy_v2) = +0.16 [95% CI +0.04, +0.28]

| opponent | games | PPG(lab3_shadow) | PPG(greedy_v2) | paired diff [95% CI] |
|---|---|---|---|---|
| camper | 160 | 1.98 | 1.69 | +0.29 [+0.06, +0.52] |
| choke | 160 | 1.65 | 1.55 | +0.10 [-0.12, +0.32] |
| exploit_v2 | 160 | 1.57 | 1.46 | +0.11 [-0.11, +0.33] |
| feature | 160 | 1.88 | 1.74 | +0.13 [-0.11, +0.38] |
| greedy | 160 | 2.09 | 1.96 | +0.13 [-0.06, +0.33] |
| rusher | 160 | 1.93 | 1.76 | +0.17 [-0.03, +0.38] |
