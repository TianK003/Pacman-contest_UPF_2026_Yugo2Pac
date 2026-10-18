# greedy (v1): first submission, 2026-10-16 (E-003) until greedy_v2 (E-013)

- **File**: `teams/greedy_v1.py`, defaults `GreedyAttacker` + `PatrolDefender`.
- **League name**: `greedy`.
- **Next pick**: [greedy_v2](greedy_v2.md).
- **One-line summary**: the simplest agent that clearly beats the baseline. The attacker eats the nearest food it can reach before any ghost it sees and banks at 5. The defender chases visible invaders and otherwise patrols near our food.

## Mindset

- **Attacker: "safe nearest-food eater"**.
  - It only takes food it reaches strictly before every visible ghost.
  - It banks at 5 food and runs when a ghost is within 4 steps.
  - It has no plan for a guard: if a ghost blocks every safe food, it waits at the border.
- **Defender: "chaser and patroller"**.
  - It goes straight at a visible invader and keeps 3 steps away when scared.
  - Otherwise it goes to where our food vanished, or patrols.

## What each agent knows

Visible enemies (Manhattan ≤ 5 of either of our agents); the capsule timer (enemies scared for 40 − 3 of their moves after we eat an enemy capsule); respawn detection (an enemy that vanishes next to us or reappears far away). No memory of hidden enemies.

## Attacker: decision list (trace rule in brackets)

1. **Go home** (`home`) when carrying food and any of these holds:
   - carrying ≥ 5;
   - ≤ 2 food left;
   - this trip would win the game;
   - just enough time left (+3 moves);
   - a dangerous ghost is within 4 maze steps.
2. **Eat** (`eat`): walk to the nearest food it reaches strictly before every dangerous ghost, along cells it reaches first (our side always counts as safe).
3. **Otherwise** head for the nearest home border cell (`no-safe-food`), with capsules as escape targets while threatened. If no safe path exists, it steps away from the nearest ghost (`evade`).

## Defender: decision list

1. **Scared** (`scared`): keep about 3 steps from a visible invader.
2. **Chase** (`chase`) the nearest visible invader.
3. **Last evidence** (`last-evidence`): walk to where our food just vanished or an invader was last seen.
4. **Patrol** (`patrol`): cycle through the 3 border cells nearest the middle of our remaining food.

## How it behaves (rule profile, E-022)

240 games, the same opponents and seeds as for greedy_v2 / v3 (one of them, `greedy`, is its own mirror):

| attacker rule | share | | defender rule | share |
|---|---|---|---|---|
| eat | 44.7% | | patrol | 54.2% |
| no-safe-food | 33.4% | | chase | 24.5% |
| home | 11.8% | | last-evidence | 11.3% |
| evade | 10.1% | | scared | 10.0% |

Against guards it mostly waits. `no-safe-food` is 47% of its attacker's moves against camper and 52% against exploit_v2. This is the 0–0 standoff of E-005, which greedy_v2's breaker fixes. Per-opponent tables: `eval/results/trace_profile_greedy.md`.

## Evidence

| run | result |
|---|---|
| v1 round robin, validation seeds 1–20 (E-002) | best of 5: 2.23 points per game, 40/40 vs baseline, beats every member head-to-head |
| promotion (E-003) | provisional (user decision); 20 seed-pairs, no confirmation |
| sparring pool (E-006) | camper and rusher beat it head-to-head (1.10 / 0.90 points per game for greedy) |
| 7-member round robin (E-017) | 1.21 points per game (6th of 7) |

## Known blind spots

| blind spot | evidence |
|---|---|
| Waits at the border forever against a guard (0–0 standoffs) | E-005, E-006 |
| Dies in dead ends; ignores hidden ghosts | E-005, E-014 |
| Against two attackers, loses scoring races (banks every 5) | E-002, E-005 |
| The defender chases from behind instead of cutting off | E-007 (intercept) |
