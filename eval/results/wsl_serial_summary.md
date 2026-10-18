### Summary: 180 games, 7 agents, 15 seeds

| agent | games | W-T-L | PPG [95% CI] | win % [exact 95% CI] | avg margin | crash/forfeit | time warnings | max move s | p95 move s | over budget | violations |
|---|---|---|---|---|---|---|---|---|---|---|---|
| camper | 30 | 8-7-15 | 1.03 [0.57, 1.53] | 27 [12, 46] | -1.4 | 0 | 0 | 0.032 | 0.001 | 0 | - |
| choke | 30 | 14-2-14 | 1.47 [1.17, 1.77] | 47 [28, 66] | +0.4 | 0 | 0 | 0.029 | 0.001 | 0 | - |
| exploit_v2 | 30 | 17-2-11 | 1.77 [1.30, 2.23] | 57 [37, 75] | +0.7 | 0 | 0 | 0.031 | 0.001 | 0 | - |
| feature | 30 | 14-3-13 | 1.50 [0.97, 2.03] | 47 [28, 66] | -1.6 | 0 | 0 | 0.064 | 0.001 | 0 | - |
| greedy | 30 | 9-5-16 | 1.07 [0.67, 1.47] | 30 [15, 49] | -1.8 | 0 | 0 | 0.041 | 0.001 | 0 | - |
| rusher | 30 | 18-6-6 | 2.00 [1.63, 2.37] | 60 [41, 77] | +2.9 | 0 | 0 | 0.041 | 0.001 | 0 | - |
| submission | 180 | 75-25-80 | 1.39 [1.17, 1.60] | 42 [34, 49] | +0.1 | 0 | 0 | 0.064 | 0.001 | 0 | - |

PPG CIs: seed-clustered percentile bootstrap. They are too narrow near PPG 0 or 3 (E-004: ~73% coverage at a 97% win rate), so trust the exact win-rate CI there.

Head-to-head PPG (row agent vs column opponent; 3 = always wins):

| | camper | choke | exploit_v2 | feature | greedy | rusher | submission |
|---|---|---|---|---|---|---|---|
| camper | - | - | - | - | - | - | 1.03 |
| choke | - | - | - | - | - | - | 1.47 |
| exploit_v2 | - | - | - | - | - | - | 1.77 |
| feature | - | - | - | - | - | - | 1.50 |
| greedy | - | - | - | - | - | - | 1.07 |
| rusher | - | - | - | - | - | - | 2.00 |
| submission | 1.73 | 1.47 | 1.17 | 1.40 | 1.77 | 0.80 | - |

Diagnostics (team totals per game; kills = opponent deaths):

| agent | games | returned | conceded | deaths | kills | food lost | Pacman moves | standoff moves | max carried | 28-finish us / them |
|---|---|---|---|---|---|---|---|---|---|---|
| camper | 30 | 8.7 | 10.0 | 1.17 | 1.07 | 3.2 | 113 | 226 | 4.8 | 0 / 0 |
| choke | 30 | 10.9 | 10.4 | 1.13 | 1.07 | 3.0 | 121 | 124 | 7.2 | 0 / 0 |
| exploit_v2 | 30 | 10.9 | 10.3 | 0.40 | 1.23 | 0.6 | 145 | 184 | 6.1 | 0 / 0 |
| feature | 30 | 11.7 | 13.3 | 0.37 | 1.13 | 0.5 | 138 | 202 | 6.6 | 1 / 0 |
| greedy | 30 | 9.1 | 10.9 | 1.37 | 1.27 | 3.5 | 109 | 218 | 4.7 | 0 / 0 |
| rusher | 30 | 12.8 | 9.9 | 0.67 | 2.00 | 1.0 | 164 | 178 | 8.0 | 0 / 0 |
| submission | 180 | 10.8 | 10.7 | 1.29 | 0.85 | 2.9 | 130 | 177 | 6.9 | 0 / 1 |
