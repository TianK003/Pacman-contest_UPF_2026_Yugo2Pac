3400 games to play (17 pairs x 100 seeds x 2 colours, 0 already scored) with 8 workers -> C:\Users\Tian\Desktop\Pacman-contest_UPF_2026\eval\results\test2.jsonl
### Summary: 3400 games, 10 agents, 100 seeds

| agent | games | W-T-L | PPG [95% CI] | win % [exact 95% CI] | avg margin | crash/forfeit | time warnings | max move s | p95 move s | over budget | violations |
|---|---|---|---|---|---|---|---|---|---|---|---|
| camper | 400 | 55-51-294 | 0.54 [0.43, 0.66] | 14 [11, 18] | -7.2 | 0 | 0 | 0.051 | 0.002 | 0 | - |
| choke | 400 | 85-59-256 | 0.79 [0.66, 0.91] | 21 [17, 26] | -4.1 | 0 | 0 | 0.085 | 0.002 | 0 | - |
| exploit_v2 | 400 | 76-47-277 | 0.69 [0.57, 0.81] | 19 [15, 23] | -5.9 | 0 | 0 | 0.048 | 0.002 | 0 | - |
| feature | 400 | 67-24-309 | 0.56 [0.44, 0.69] | 17 [13, 21] | -7.3 | 0 | 0 | 0.056 | 0.002 | 0 | - |
| greedy_v2 | 400 | 94-49-257 | 0.83 [0.70, 0.96] | 24 [19, 28] | -4.9 | 0 | 0 | 0.053 | 0.002 | 0 | - |
| greedy_v3 | 1800 | 813-252-735 | 1.50 [1.42, 1.57] | 45 [43, 47] | +0.5 | 0 | 0 | 0.065 | 0.003 | 0 | - |
| greedy_v4 | 1800 | 1443-143-214 | 2.48 [2.40, 2.56] | 80 [78, 82] | +7.9 | 0 | 0 | 0.310 | 0.125 | 0 | - |
| heldout_a | 400 | 126-19-255 | 0.99 [0.86, 1.13] | 32 [27, 36] | -2.8 | 0 | 0 | 0.051 | 0.004 | 0 | - |
| heldout_b | 400 | 139-21-240 | 1.09 [0.94, 1.25] | 35 [30, 40] | -4.0 | 0 | 0 | 0.120 | 0.024 | 0 | - |
| lab5_smart | 400 | 132-75-193 | 1.18 [1.07, 1.29] | 33 [28, 38] | -1.9 | 0 | 0 | 0.070 | 0.003 | 0 | - |

PPG CIs: seed-clustered percentile bootstrap. They are too narrow near PPG 0 or 3 (E-004: ~73% coverage at a 97% win rate), so trust the exact win-rate CI there.

Head-to-head PPG (row agent vs column opponent; 3 = always wins):

| | camper | choke | exploit_v2 | feature | greedy_v2 | greedy_v3 | greedy_v4 | heldout_a | heldout_b | lab5_smart |
|---|---|---|---|---|---|---|---|---|---|---|
| camper | - | - | - | - | - | 0.80 | 0.28 | - | - | - |
| choke | - | - | - | - | - | 1.16 | 0.41 | - | - | - |
| exploit_v2 | - | - | - | - | - | 1.07 | 0.30 | - | - | - |
| feature | - | - | - | - | - | 0.82 | 0.30 | - | - | - |
| greedy_v2 | - | - | - | - | - | 1.27 | 0.38 | - | - | - |
| greedy_v3 | 2.06 | 1.65 | 1.75 | 2.10 | 1.56 | - | 0.50 | 1.44 | 1.35 | 1.04 |
| greedy_v4 | 2.60 | 2.48 | 2.64 | 2.65 | 2.54 | 2.38 | - | 2.48 | 2.35 | 2.23 |
| heldout_a | - | - | - | - | - | 1.50 | 0.48 | - | - | - |
| heldout_b | - | - | - | - | - | 1.57 | 0.61 | - | - | - |
| lab5_smart | - | - | - | - | - | 1.71 | 0.65 | - | - | - |

Diagnostics (team totals per game; kills = opponent deaths):

| agent | games | returned | conceded | deaths | kills | food lost | Pacman moves | standoff moves | max carried | 28-finish us / them |
|---|---|---|---|---|---|---|---|---|---|---|
| camper | 400 | 6.2 | 13.4 | 0.82 | 0.58 | 1.5 | 69 | 295 | 3.9 | 0 / 7 |
| choke | 400 | 9.8 | 13.9 | 0.90 | 0.65 | 2.1 | 92 | 174 | 6.4 | 1 / 13 |
| exploit_v2 | 400 | 7.6 | 13.5 | 0.42 | 0.55 | 0.7 | 96 | 247 | 5.7 | 4 / 8 |
| feature | 400 | 7.7 | 15.0 | 0.43 | 0.74 | 0.5 | 98 | 246 | 5.6 | 3 / 11 |
| greedy_v2 | 400 | 9.9 | 14.8 | 0.96 | 0.69 | 2.2 | 93 | 214 | 6.6 | 2 / 14 |
| greedy_v3 | 1800 | 11.2 | 10.7 | 0.99 | 0.58 | 2.6 | 119 | 221 | 7.2 | 24 / 30 |
| greedy_v4 | 1800 | 16.9 | 9.0 | 0.48 | 0.78 | 1.3 | 145 | 202 | 11.1 | 78 / 13 |
| heldout_a | 400 | 12.4 | 15.2 | 0.56 | 1.33 | 1.8 | 147 | 145 | 8.4 | 17 / 11 |
| heldout_b | 400 | 11.9 | 15.9 | 0.45 | 0.75 | 0.5 | 139 | 200 | 6.6 | 3 / 24 |
| lab5_smart | 400 | 10.5 | 12.4 | 0.94 | 0.67 | 2.0 | 96 | 231 | 8.0 | 5 / 6 |

Paired comparison over 1600 shared games: PPG(greedy_v4) - PPG(greedy_v3) = +0.88 [95% CI +0.79, +0.97]

| opponent | games | PPG(greedy_v4) | PPG(greedy_v3) | paired diff [95% CI] |
|---|---|---|---|---|
| camper | 200 | 2.60 | 2.06 | +0.55 [+0.34, +0.74] |
| choke | 200 | 2.48 | 1.65 | +0.83 [+0.60, +1.06] |
| exploit_v2 | 200 | 2.64 | 1.75 | +0.89 [+0.69, +1.10] |
| feature | 200 | 2.65 | 2.10 | +0.56 [+0.38, +0.74] |
| greedy_v2 | 200 | 2.54 | 1.56 | +0.98 [+0.74, +1.21] |
| heldout_a | 200 | 2.48 | 1.44 | +1.04 [+0.77, +1.29] |
| heldout_b | 200 | 2.35 | 1.35 | +1.00 [+0.75, +1.24] |
| lab5_smart | 200 | 2.23 | 1.04 | +1.18 [+0.91, +1.44] |
