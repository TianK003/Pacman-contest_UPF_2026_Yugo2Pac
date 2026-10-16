### Summary: 160 games, 5 agents, 20 seeds, 10 unscored (harness errors)

| agent | games | W-T-L | PPG [95% CI] | avg margin | crash/forfeit | time warnings | max move s | p95 move s | over budget | violations |
|---|---|---|---|---|---|---|---|---|---|---|
| baseline | 150 | 35-29-86 | 0.89 [0.78, 1.00] | -9.9 | 0 | 0 | 0.154 | 0.006 | 0 | - |
| double_attack | 40 | 6-1-33 | 0.47 [0.15, 0.88] | -2.6 | 0 | 0 | 0.039 | 0.002 | 0 | - |
| greedy | 40 | 40-0-0 | 3.00 [3.00, 3.00] | +19.6 | 0 | 0 | 0.058 | 0.002 | 0 | - |
| greedy_deadend | 40 | 40-0-0 | 3.00 [3.00, 3.00] | +20.2 | 0 | 0 | 0.073 | 0.002 | 0 | - |
| turtle | 30 | 0-28-2 | 0.93 [0.83, 1.00] | -0.3 | 0 | 0 | 0.107 | 0.002 | 0 | - |

Head-to-head PPG (row agent vs column opponent; 3 = always wins):

| | baseline | double_attack | greedy | greedy_deadend | turtle |
|---|---|---|---|---|---|
| baseline | - | 2.50 | 0.00 | 0.00 | 1.13 |
| double_attack | 0.47 | - | - | - | - |
| greedy | 3.00 | - | - | - | - |
| greedy_deadend | 3.00 | - | - | - | - |
| turtle | 0.93 | - | - | - | - |

Paired comparison over 40 shared games: PPG(greedy) - PPG(greedy_deadend) = +0.00 [95% CI +0.00, +0.00]
