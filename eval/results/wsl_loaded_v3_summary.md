### Summary: 180 games, 7 agents, 15 seeds

| agent | games | W-T-L | PPG [95% CI] | win % [exact 95% CI] | avg margin | crash/forfeit | time warnings | max move s | p95 move s | over budget | violations |
|---|---|---|---|---|---|---|---|---|---|---|---|
| camper | 30 | 5-7-18 | 0.73 [0.37, 1.20] | 17 [6, 35] | -3.9 | 0 | 0 | 0.096 | 0.004 | 0 | - |
| choke | 30 | 8-9-13 | 1.10 [0.67, 1.53] | 27 [12, 46] | -1.2 | 0 | 0 | 0.076 | 0.003 | 0 | - |
| exploit_v2 | 30 | 10-5-15 | 1.17 [0.67, 1.70] | 33 [17, 53] | -0.3 | 0 | 0 | 0.073 | 0.003 | 0 | - |
| feature | 30 | 9-3-18 | 1.00 [0.50, 1.57] | 30 [15, 49] | -3.7 | 0 | 0 | 0.062 | 0.005 | 0 | - |
| greedy | 30 | 6-6-18 | 0.80 [0.40, 1.20] | 20 [8, 39] | -3.9 | 0 | 0 | 0.112 | 0.005 | 0 | - |
| greedy_v3 | 180 | 100-36-44 | 1.87 [1.58, 2.18] | 56 [48, 63] | +2.7 | 0 | 0 | 0.105 | 0.005 | 0 | - |
| rusher | 30 | 6-6-18 | 0.80 [0.47, 1.13] | 20 [8, 39] | -3.4 | 0 | 0 | 0.080 | 0.003 | 0 | - |

PPG CIs: seed-clustered percentile bootstrap. They are too narrow near PPG 0 or 3 (E-004: ~73% coverage at a 97% win rate), so trust the exact win-rate CI there.

Head-to-head PPG (row agent vs column opponent; 3 = always wins):

| | camper | choke | exploit_v2 | feature | greedy | greedy_v3 | rusher |
|---|---|---|---|---|---|---|---|
| camper | - | - | - | - | - | 0.73 | - |
| choke | - | - | - | - | - | 1.10 | - |
| exploit_v2 | - | - | - | - | - | 1.17 | - |
| feature | - | - | - | - | - | 1.00 | - |
| greedy | - | - | - | - | - | 0.80 | - |
| greedy_v3 | 2.03 | 1.60 | 1.67 | 1.90 | 2.00 | - | 2.00 |
| rusher | - | - | - | - | - | 0.80 | - |

Diagnostics (team totals per game; kills = opponent deaths):

| agent | games | returned | conceded | deaths | kills | food lost | Pacman moves | standoff moves | max carried | 28-finish us / them |
|---|---|---|---|---|---|---|---|---|---|---|
| camper | 30 | 4.1 | 8.0 | 0.73 | 0.80 | 1.5 | 70 | 350 | 4.0 | 0 / 1 |
| choke | 30 | 6.9 | 8.1 | 0.93 | 1.20 | 2.7 | 89 | 212 | 5.4 | 0 / 0 |
| exploit_v2 | 30 | 6.3 | 6.6 | 0.17 | 1.07 | 0.6 | 100 | 302 | 5.7 | 0 / 0 |
| feature | 30 | 6.0 | 9.7 | 0.23 | 1.40 | 0.3 | 101 | 284 | 5.4 | 0 / 0 |
| greedy | 30 | 4.7 | 8.6 | 0.83 | 1.00 | 1.8 | 58 | 349 | 3.9 | 0 / 0 |
| greedy_v3 | 180 | 8.4 | 5.6 | 1.17 | 0.61 | 3.4 | 108 | 276 | 6.0 | 1 / 0 |
| rusher | 30 | 5.7 | 9.1 | 0.73 | 1.53 | 1.6 | 110 | 291 | 5.0 | 0 / 0 |
