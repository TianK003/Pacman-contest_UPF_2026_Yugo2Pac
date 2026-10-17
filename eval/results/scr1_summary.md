### Summary: 560 games, 8 agents, 10 seeds

| agent | games | W-T-L | PPG [95% CI] | win % [exact 95% CI] | avg margin | crash/forfeit | time warnings | max move s | p95 move s | over budget | violations |
|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 140 | 23-46-71 | 0.82 [0.66, 1.04] | 16 [11, 24] | -6.0 | 0 | 0 | 0.205 | 0.007 | 0 | - |
| baseline_plus | 140 | 27-52-61 | 0.95 [0.76, 1.18] | 19 [13, 27] | -6.2 | 0 | 0 | 0.089 | 0.004 | 0 | - |
| camper | 140 | 62-70-8 | 1.83 [1.57, 2.11] | 44 [36, 53] | +4.1 | 0 | 0 | 0.106 | 0.002 | 0 | - |
| camper2 | 140 | 0-102-38 | 0.73 [0.54, 0.90] | 0 [0, 3] | -2.4 | 0 | 0 | 0.125 | 0.004 | 0 | - |
| double_attack | 140 | 54-53-33 | 1.54 [1.27, 1.82] | 39 [30, 47] | +4.5 | 0 | 0 | 0.102 | 0.002 | 0 | - |
| greedy | 140 | 63-63-14 | 1.80 [1.64, 1.96] | 45 [37, 54] | +4.7 | 0 | 0 | 0.101 | 0.002 | 0 | - |
| rusher | 140 | 59-73-8 | 1.79 [1.51, 2.06] | 42 [34, 51] | +5.3 | 0 | 0 | 0.080 | 0.004 | 0 | - |
| turtle | 140 | 0-85-55 | 0.61 [0.46, 0.76] | 0 [0, 3] | -3.9 | 0 | 0 | 0.070 | 0.003 | 0 | - |

PPG CIs: seed-clustered percentile bootstrap. They are too narrow near PPG 0 or 3 (E-004: ~73% coverage at a 97% win rate), so trust the exact win-rate CI there.

Head-to-head PPG (row agent vs column opponent; 3 = always wins):

| | baseline | baseline_plus | camper | camper2 | double_attack | greedy | rusher | turtle |
|---|---|---|---|---|---|---|---|---|
| baseline | - | 1.10 | 0.20 | 1.00 | 2.15 | 0.15 | 0.15 | 1.00 |
| baseline_plus | 1.85 | - | 0.35 | 1.70 | 0.10 | 0.35 | 0.60 | 1.70 |
| camper | 2.60 | 2.30 | - | 1.80 | 1.55 | 1.25 | 1.20 | 2.10 |
| camper2 | 1.00 | 0.65 | 0.60 | - | 0.55 | 0.60 | 0.70 | 1.00 |
| double_attack | 0.80 | 2.80 | 0.95 | 1.90 | - | 1.20 | 0.90 | 2.20 |
| greedy | 2.85 | 2.30 | 1.10 | 1.80 | 1.35 | - | 0.90 | 2.30 |
| rusher | 2.85 | 1.95 | 1.05 | 1.60 | 1.50 | 1.35 | - | 2.20 |
| turtle | 1.00 | 0.65 | 0.45 | 1.00 | 0.40 | 0.35 | 0.40 | - |

Approximate Nash averaging (payoff vs the equilibrium mixture of this pool; >0 = beats the mix):

| agent | Nash weight | Nash-avg payoff |
|---|---|---|
| camper | 0.99 | +0.00 |
| rusher | 0.01 | -0.15 |
| greedy | 0.00 | -0.15 |
| double_attack | 0.00 | -0.60 |
| camper2 | 0.00 | -1.20 |
| turtle | 0.00 | -1.65 |
| baseline_plus | 0.00 | -1.95 |
| baseline | 0.00 | -2.40 |

Diagnostics (team totals per game; kills = opponent deaths):

| agent | games | returned | conceded | deaths | kills | food lost | Pacman moves | standoff moves | max carried | 28-finish us / them |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 140 | 4.6 | 10.6 | 3.66 | 0.54 | 7.8 | 55 | 87 | 10.9 | 23 / 10 |
| baseline_plus | 140 | 2.1 | 8.3 | 1.19 | 0.62 | 1.8 | 67 | 180 | 3.2 | 0 / 18 |
| camper | 140 | 6.2 | 2.1 | 0.46 | 0.73 | 1.4 | 76 | 369 | 3.3 | 1 / 0 |
| camper2 | 140 | 0.0 | 2.4 | 0.06 | 0.63 | 0.0 | 0 | 418 | 0.0 | 0 / 1 |
| double_attack | 140 | 11.6 | 7.1 | 0.61 | 0.54 | 1.6 | 145 | 275 | 3.6 | 14 / 15 |
| greedy | 140 | 7.4 | 2.7 | 0.44 | 1.29 | 1.3 | 84 | 325 | 3.5 | 1 / 3 |
| rusher | 140 | 7.6 | 2.3 | 0.40 | 1.48 | 1.6 | 93 | 319 | 5.4 | 10 / 2 |
| turtle | 140 | 0.0 | 3.9 | 0.17 | 1.17 | 0.0 | 0 | 318 | 0.0 | 0 / 0 |
