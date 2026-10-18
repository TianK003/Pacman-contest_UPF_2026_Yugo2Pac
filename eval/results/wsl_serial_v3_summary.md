### Summary: 180 games, 7 agents, 15 seeds

| agent | games | W-T-L | PPG [95% CI] | win % [exact 95% CI] | avg margin | crash/forfeit | time warnings | max move s | p95 move s | over budget | violations |
|---|---|---|---|---|---|---|---|---|---|---|---|
| camper | 30 | 10-5-15 | 1.17 [0.57, 1.80] | 33 [17, 53] | -2.4 | 0 | 0 | 0.025 | 0.001 | 0 | - |
| choke | 30 | 9-4-17 | 1.03 [0.60, 1.47] | 30 [15, 49] | -1.7 | 0 | 0 | 0.030 | 0.001 | 0 | - |
| exploit_v2 | 30 | 10-2-18 | 1.07 [0.53, 1.63] | 33 [17, 53] | -2.7 | 0 | 0 | 0.028 | 0.001 | 0 | - |
| feature | 30 | 8-1-21 | 0.83 [0.30, 1.43] | 27 [12, 46] | -3.8 | 0 | 0 | 0.026 | 0.001 | 0 | - |
| greedy | 30 | 7-1-22 | 0.73 [0.37, 1.10] | 23 [10, 42] | -3.6 | 0 | 0 | 0.022 | 0.000 | 0 | - |
| greedy_v3 | 180 | 110-15-55 | 1.92 [1.67, 2.14] | 61 [54, 68] | +2.9 | 0 | 1 | 0.035 | 0.002 | 0 | - |
| rusher | 30 | 11-2-17 | 1.17 [0.63, 1.73] | 37 [20, 56] | -3.2 | 0 | 0 | 0.027 | 0.001 | 0 | - |

PPG CIs: seed-clustered percentile bootstrap. They are too narrow near PPG 0 or 3 (E-004: ~73% coverage at a 97% win rate), so trust the exact win-rate CI there.

Head-to-head PPG (row agent vs column opponent; 3 = always wins):

| | camper | choke | exploit_v2 | feature | greedy | greedy_v3 | rusher |
|---|---|---|---|---|---|---|---|
| camper | - | - | - | - | - | 1.17 | - |
| choke | - | - | - | - | - | 1.03 | - |
| exploit_v2 | - | - | - | - | - | 1.07 | - |
| feature | - | - | - | - | - | 0.83 | - |
| greedy | - | - | - | - | - | 0.73 | - |
| greedy_v3 | 1.67 | 1.83 | 1.87 | 2.13 | 2.23 | - | 1.77 |
| rusher | - | - | - | - | - | 1.17 | - |

Diagnostics (team totals per game; kills = opponent deaths):

| agent | games | returned | conceded | deaths | kills | food lost | Pacman moves | standoff moves | max carried | 28-finish us / them |
|---|---|---|---|---|---|---|---|---|---|---|
| camper | 30 | 8.8 | 11.2 | 0.93 | 1.30 | 1.5 | 79 | 275 | 4.9 | 0 / 0 |
| choke | 30 | 12.7 | 14.4 | 1.13 | 0.93 | 3.9 | 119 | 146 | 7.7 | 1 / 0 |
| exploit_v2 | 30 | 9.6 | 12.3 | 0.07 | 1.07 | 0.2 | 102 | 231 | 7.1 | 0 / 1 |
| feature | 30 | 9.8 | 13.6 | 0.33 | 1.30 | 0.4 | 109 | 232 | 7.3 | 0 / 1 |
| greedy | 30 | 9.3 | 12.8 | 0.97 | 1.43 | 1.8 | 82 | 268 | 5.0 | 0 / 0 |
| greedy_v3 | 180 | 12.8 | 9.9 | 1.29 | 0.69 | 4.0 | 136 | 222 | 7.7 | 2 / 1 |
| rusher | 30 | 9.4 | 12.7 | 0.70 | 1.70 | 2.1 | 103 | 250 | 8.2 | 0 / 0 |
