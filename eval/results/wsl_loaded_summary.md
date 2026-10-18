### Summary: 180 games, 7 agents, 15 seeds

| agent | games | W-T-L | PPG [95% CI] | win % [exact 95% CI] | avg margin | crash/forfeit | time warnings | max move s | p95 move s | over budget | violations |
|---|---|---|---|---|---|---|---|---|---|---|---|
| camper | 30 | 8-3-19 | 0.90 [0.47, 1.30] | 27 [12, 46] | -2.9 | 0 | 0 | 0.074 | 0.004 | 0 | - |
| choke | 30 | 9-5-16 | 1.07 [0.60, 1.57] | 30 [15, 49] | -2.3 | 0 | 0 | 0.075 | 0.003 | 0 | - |
| exploit_v2 | 30 | 10-3-17 | 1.10 [0.57, 1.60] | 33 [17, 53] | -2.2 | 0 | 0 | 0.059 | 0.003 | 0 | - |
| feature | 30 | 10-2-18 | 1.07 [0.50, 1.67] | 33 [17, 53] | -2.3 | 0 | 0 | 0.073 | 0.002 | 0 | - |
| greedy | 30 | 7-2-21 | 0.77 [0.40, 1.17] | 23 [10, 42] | -5.3 | 0 | 0 | 0.101 | 0.003 | 0 | - |
| rusher | 30 | 11-3-16 | 1.20 [0.63, 1.77] | 37 [20, 56] | -3.2 | 0 | 0 | 0.073 | 0.004 | 0 | - |
| submission | 180 | 107-18-55 | 1.88 [1.66, 2.13] | 59 [52, 67] | +3.0 | 0 | 0 | 0.087 | 0.004 | 0 | - |

PPG CIs: seed-clustered percentile bootstrap. They are too narrow near PPG 0 or 3 (E-004: ~73% coverage at a 97% win rate), so trust the exact win-rate CI there.

Head-to-head PPG (row agent vs column opponent; 3 = always wins):

| | camper | choke | exploit_v2 | feature | greedy | rusher | submission |
|---|---|---|---|---|---|---|---|
| camper | - | - | - | - | - | - | 0.90 |
| choke | - | - | - | - | - | - | 1.07 |
| exploit_v2 | - | - | - | - | - | - | 1.10 |
| feature | - | - | - | - | - | - | 1.07 |
| greedy | - | - | - | - | - | - | 0.77 |
| rusher | - | - | - | - | - | - | 1.20 |
| submission | 2.00 | 1.77 | 1.80 | 1.87 | 2.17 | 1.70 | - |

Diagnostics (team totals per game; kills = opponent deaths):

| agent | games | returned | conceded | deaths | kills | food lost | Pacman moves | standoff moves | max carried | 28-finish us / them |
|---|---|---|---|---|---|---|---|---|---|---|
| camper | 30 | 8.1 | 11.0 | 1.80 | 1.17 | 2.9 | 98 | 264 | 4.5 | 0 / 0 |
| choke | 30 | 11.0 | 13.3 | 1.57 | 1.50 | 3.9 | 132 | 152 | 7.1 | 0 / 0 |
| exploit_v2 | 30 | 8.9 | 11.1 | 0.20 | 1.23 | 0.2 | 165 | 216 | 6.4 | 0 / 0 |
| feature | 30 | 8.9 | 11.2 | 0.17 | 1.87 | 0.2 | 164 | 223 | 6.4 | 0 / 0 |
| greedy | 30 | 6.8 | 12.1 | 2.17 | 1.63 | 3.3 | 102 | 209 | 4.0 | 0 / 0 |
| rusher | 30 | 10.0 | 13.2 | 1.53 | 2.27 | 3.3 | 135 | 205 | 7.4 | 0 / 0 |
| submission | 180 | 12.0 | 9.0 | 1.61 | 1.24 | 3.6 | 114 | 204 | 7.3 | 0 / 0 |
