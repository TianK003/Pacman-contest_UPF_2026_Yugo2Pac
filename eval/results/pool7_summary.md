### Summary: 2100 games, 7 agents, 50 seeds

| agent | games | W-T-L | PPG [95% CI] | win % [exact 95% CI] | avg margin | crash/forfeit | time warnings | max move s | p95 move s | over budget | violations |
|---|---|---|---|---|---|---|---|---|---|---|---|
| camper | 600 | 240-111-249 | 1.39 [1.24, 1.54] | 40 [36, 44] | -0.6 | 0 | 0 | 0.482 | 0.004 | 0 | - |
| choke | 600 | 285-64-251 | 1.53 [1.37, 1.70] | 48 [43, 52] | +0.5 | 0 | 0 | 0.147 | 0.011 | 0 | - |
| exploit_v2 | 600 | 311-70-219 | 1.67 [1.44, 1.89] | 52 [48, 56] | +1.5 | 0 | 0 | 0.426 | 0.005 | 0 | - |
| feature | 600 | 271-65-264 | 1.46 [1.26, 1.66] | 45 [41, 49] | +0.2 | 0 | 0 | 0.156 | 0.003 | 0 | - |
| greedy | 600 | 207-102-291 | 1.21 [1.06, 1.35] | 34 [31, 38] | -1.3 | 0 | 0 | 0.146 | 0.004 | 0 | - |
| greedy_v2 | 600 | 302-68-230 | 1.62 [1.47, 1.79] | 50 [46, 54] | +1.4 | 0 | 0 | 0.158 | 0.003 | 0 | - |
| rusher | 600 | 191-106-303 | 1.13 [0.97, 1.30] | 32 [28, 36] | -1.5 | 0 | 0 | 0.180 | 0.003 | 0 | - |

PPG CIs: seed-clustered percentile bootstrap. They are too narrow near PPG 0 or 3 (E-004: ~73% coverage at a 97% win rate), so trust the exact win-rate CI there.

Head-to-head PPG (row agent vs column opponent; 3 = always wins):

| | camper | choke | exploit_v2 | feature | greedy | greedy_v2 | rusher |
|---|---|---|---|---|---|---|---|
| camper | - | 1.50 | 1.01 | 1.27 | 1.56 | 1.28 | 1.69 |
| choke | 1.41 | - | 1.45 | 1.45 | 1.71 | 1.32 | 1.85 |
| exploit_v2 | 1.88 | 1.45 | - | 1.76 | 1.84 | 1.31 | 1.79 |
| feature | 1.57 | 1.48 | 1.13 | - | 1.70 | 1.24 | 1.66 |
| greedy | 1.11 | 1.20 | 1.03 | 1.19 | - | 1.24 | 1.46 |
| greedy_v2 | 1.61 | 1.50 | 1.58 | 1.69 | 1.66 | - | 1.70 |
| rusher | 1.00 | 1.04 | 1.07 | 1.21 | 1.28 | 1.19 | - |

Approximate Nash averaging (payoff vs the equilibrium mixture of this pool; >0 = beats the mix):

| agent | Nash weight | Nash-avg payoff |
|---|---|---|
| greedy_v2 | 0.99 | +0.00 |
| choke | 0.00 | -0.18 |
| exploit_v2 | 0.00 | -0.27 |
| camper | 0.00 | -0.33 |
| greedy | 0.00 | -0.42 |
| feature | 0.00 | -0.45 |
| rusher | 0.00 | -0.51 |

Diagnostics (team totals per game; kills = opponent deaths):

| agent | games | returned | conceded | deaths | kills | food lost | Pacman moves | standoff moves | max carried | 28-finish us / them |
|---|---|---|---|---|---|---|---|---|---|---|
| camper | 600 | 8.6 | 9.2 | 1.11 | 0.75 | 2.5 | 102 | 266 | 4.6 | 0 / 7 |
| choke | 600 | 11.7 | 11.2 | 1.26 | 0.84 | 3.3 | 122 | 148 | 7.6 | 15 / 7 |
| exploit_v2 | 600 | 10.5 | 9.0 | 0.41 | 0.78 | 1.0 | 148 | 235 | 7.6 | 5 / 4 |
| feature | 600 | 10.6 | 10.4 | 0.51 | 1.08 | 1.1 | 145 | 214 | 7.5 | 8 / 4 |
| greedy | 600 | 8.8 | 10.1 | 1.13 | 0.82 | 2.3 | 97 | 252 | 4.6 | 0 / 9 |
| greedy_v2 | 600 | 11.8 | 10.4 | 1.20 | 0.86 | 3.4 | 125 | 188 | 7.5 | 15 / 4 |
| rusher | 600 | 8.1 | 9.7 | 0.92 | 1.40 | 2.5 | 101 | 253 | 6.2 | 2 / 10 |
