### Summary: 410 games, 5 agents, 20 seeds, 10 unscored (harness errors)

| agent | games | W-T-L | PPG [95% CI] | win % [exact 95% CI] | avg margin | crash/forfeit | time warnings | max move s | p95 move s | over budget | violations |
|---|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 160 | 35-39-86 | 0.90 [0.79, 1.00] | 22 [16, 29] | -9.2 | 0 | 0 | 0.154 | 0.006 | 0 | - |
| double_attack | 160 | 63-17-80 | 1.29 [1.03, 1.56] | 39 [32, 47] | +1.5 | 0 | 0 | 0.463 | 0.017 | 0 | - |
| greedy | 160 | 110-26-24 | 2.23 [2.08, 2.38] | 69 [61, 76] | +7.9 | 0 | 0 | 0.448 | 0.034 | 0 | - |
| greedy_deadend | 160 | 109-24-27 | 2.19 [2.06, 2.33] | 68 [60, 75] | +8.2 | 0 | 0 | 0.494 | 0.035 | 0 | - |
| turtle | 160 | 0-60-100 | 0.38 [0.26, 0.50] | 0 [0, 2] | -8.3 | 0 | 0 | 0.951 | 0.033 | 1 | - |

PPG CIs: seed-clustered percentile bootstrap. They are too narrow near PPG 0 or 3 (E-004: ~73% coverage at a 97% win rate), so trust the exact win-rate CI there.

Head-to-head PPG (row agent vs column opponent; 3 = always wins):

| | baseline | double_attack | greedy | greedy_deadend | turtle |
|---|---|---|---|---|---|
| baseline | - | 2.50 | 0.00 | 0.00 | 1.10 |
| double_attack | 0.47 | - | 0.95 | 1.02 | 2.70 |
| greedy | 3.00 | 1.93 | - | 1.43 | 2.55 |
| greedy_deadend | 3.00 | 1.85 | 1.27 | - | 2.65 |
| turtle | 0.95 | 0.15 | 0.23 | 0.17 | - |

Approximate Nash averaging (payoff vs the equilibrium mixture of this pool; >0 = beats the mix):

| agent | Nash weight | Nash-avg payoff |
|---|---|---|
| greedy | 0.99 | +0.00 |
| greedy_deadend | 0.00 | -0.15 |
| double_attack | 0.00 | -0.97 |
| turtle | 0.00 | -2.33 |
| baseline | 0.00 | -3.00 |

Paired comparison over 120 shared games: PPG(greedy) - PPG(greedy_deadend) = -0.01 [95% CI -0.10, +0.07]
