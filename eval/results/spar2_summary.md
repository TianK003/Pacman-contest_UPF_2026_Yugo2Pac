### Summary: 2000 games, 7 agents, 100 seeds

| agent | games | W-T-L | PPG [95% CI] | win % [exact 95% CI] | avg margin | crash/forfeit | time warnings | max move s | p95 move s | over budget | violations |
|---|---|---|---|---|---|---|---|---|---|---|---|
| camper | 400 | 144-55-201 | 1.22 [1.07, 1.37] | 36 [31, 41] | -1.8 | 0 | 0 | 0.138 | 0.004 | 0 | - |
| choke | 1000 | 494-126-380 | 1.61 [1.48, 1.74] | 49 [46, 53] | +1.3 | 0 | 0 | 0.141 | 0.008 | 0 | - |
| exploit_v2 | 1000 | 504-146-350 | 1.66 [1.51, 1.82] | 50 [47, 54] | +2.0 | 0 | 0 | 0.098 | 0.003 | 0 | - |
| feature | 400 | 136-53-211 | 1.15 [1.01, 1.30] | 34 [29, 39] | -2.0 | 0 | 0 | 0.230 | 0.003 | 0 | - |
| greedy | 400 | 131-51-218 | 1.11 [0.96, 1.25] | 33 [28, 38] | -2.5 | 0 | 0 | 0.236 | 0.003 | 0 | - |
| greedy_v2 | 400 | 170-53-177 | 1.41 [1.25, 1.56] | 42 [38, 48] | -0.4 | 0 | 0 | 0.154 | 0.003 | 0 | - |
| rusher | 400 | 149-60-191 | 1.27 [1.11, 1.41] | 37 [32, 42] | -1.6 | 0 | 0 | 0.115 | 0.004 | 0 | - |

PPG CIs: seed-clustered percentile bootstrap. They are too narrow near PPG 0 or 3 (E-004: ~73% coverage at a 97% win rate), so trust the exact win-rate CI there.

Head-to-head PPG (row agent vs column opponent; 3 = always wins):

| | camper | choke | exploit_v2 | feature | greedy | greedy_v2 | rusher |
|---|---|---|---|---|---|---|---|
| camper | - | 1.34 | 1.09 | - | - | - | - |
| choke | 1.52 | - | - | 1.64 | 1.80 | 1.43 | 1.64 |
| exploit_v2 | 1.76 | - | - | 1.79 | 1.72 | 1.49 | 1.52 |
| feature | - | 1.26 | 1.04 | - | - | - | - |
| greedy | - | 1.08 | 1.14 | - | - | - | - |
| greedy_v2 | - | 1.40 | 1.42 | - | - | - | - |
| rusher | - | 1.24 | 1.30 | - | - | - | - |

Diagnostics (team totals per game; kills = opponent deaths):

| agent | games | returned | conceded | deaths | kills | food lost | Pacman moves | standoff moves | max carried | 28-finish us / them |
|---|---|---|---|---|---|---|---|---|---|---|
| camper | 400 | 7.7 | 9.5 | 0.94 | 0.65 | 2.3 | 103 | 276 | 4.4 | 1 / 1 |
| choke | 1000 | 11.7 | 10.3 | 1.28 | 0.98 | 3.5 | 116 | 158 | 7.2 | 3 / 6 |
| exploit_v2 | 1000 | 9.3 | 7.3 | 0.40 | 0.64 | 0.8 | 128 | 265 | 6.7 | 13 / 4 |
| feature | 400 | 9.4 | 11.4 | 0.41 | 0.80 | 0.7 | 132 | 222 | 6.6 | 4 / 5 |
| greedy | 400 | 7.9 | 10.4 | 0.90 | 0.73 | 2.1 | 96 | 266 | 4.4 | 1 / 7 |
| greedy_v2 | 400 | 10.9 | 11.3 | 1.00 | 0.72 | 2.8 | 121 | 197 | 6.7 | 4 / 2 |
| rusher | 400 | 8.3 | 9.9 | 0.80 | 1.30 | 2.1 | 116 | 248 | 6.5 | 0 / 1 |
