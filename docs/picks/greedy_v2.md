# greedy_v2: submission from 2026-10-18 (E-013) until greedy_v3 the same day (E-021)

- **File**: `teams/greedy_v2.py`. It is `teams/greedy_lab_v1.py` with three switches on by default: `breaker`, `intercept` and `return_at=8`.
- **Previous pick**: [greedy (v1)](greedy_v1.md).
- **Next pick**: [greedy_v3](greedy_v3.md).
- **One-line summary**: greedy v1 plus three fixes for what E-005/E-006 found:
  - it breaks border standoffs instead of waiting;
  - it banks at 8 food instead of 5;
  - the defender cuts off an invader's way home instead of chasing it.

## Mindset

- **Attacker: "cautious opportunist"**.
  - It only takes food it can provably reach before any ghost it can see.
  - It banks at 8 and runs when a ghost is within 4 steps.
  - When a guard blocks every safe food, it walks to the entry farthest from the ghosts instead of waiting.
- **Defender: "reactive patroller with interception"**.
  - It patrols near our food.
  - When an invader is visible, it heads for the cell where it can cut off the invader's way home.
  - It knows nothing about enemies it can't see, except where our food just vanished.

## What each agent knows

The same as greedy_v3, minus the probability map, and with the original respawn rule. An enemy that vanishes next to one of us counts as eaten, even when it was our agent that got eaten (T-55). This only affects the scared-timer guess.

## Attacker: decision list

The same code as greedy_v3: see [greedy_v3.md](greedy_v3.md#attacker-decision-list-trace-rule-in-brackets). In short: go home (`home`) → keep walking to the chosen entry (`entry`) → eat the nearest safe food (`eat`) → standoff breaker (`blocked`, `capsule`, `switch-entry`) → fall back towards our border or step away from the ghost (`evade`).

## Defender: decision list

1. **Scared** (`scared`): keep about 3 steps from a visible invader.
2. **Intercept** a visible invader (`chase` within 2 steps; otherwise `cut-off` / `hold` the dead-end exit or the first cell on its way home that we reach first).
3. **Last evidence** (`last-evidence`): walk to where our food just vanished.
4. **Patrol** (`patrol`): cycle through the 3 border cells nearest the middle of our remaining food.

## What changed from greedy (v1)

| change | v1 | v2 | heuristic | screened / validated |
|---|---|---|---|---|
| Standoff breaker | waits at the border while a guard blocks (`no-safe-food`, ~50% of moves against guards) | after 3 blocked moves: capsule, or walk to the entry farthest from the ghosts | H-S12, H-M06 | E-007, E-010, E-011 |
| Return threshold | 5 | 8 | H-S04 | E-007, E-010, E-011 |
| Defender against a visible invader | goes straight at it | intercepts its way home / holds its dead-end exit | H-S07 | E-007, E-010 |

## How it behaves (rule profile, E-022)

240 games, the same opponents and seeds as for greedy_v3. Shares of each agent's moves:

| attacker rule | share | | defender rule | share |
|---|---|---|---|---|
| eat | 45.5% | | patrol | 51.1% |
| entry | 24.2% | | chase | 20.3% |
| evade | 12.3% | | last-evidence | 12.2% |
| home | 11.6% | | scared | 10.6% |
| blocked | 4.5% | | cut-off | 5.7% |
| switch-entry | 1.8% | | | |
| capsule | 0.1% | | | |

The breaker turns greedy v1's waiting at the border into walking: against guards, `entry` takes 33–36% of moves (camper, exploit_v2), where v1 spent 47–52% on `no-safe-food`. Per-opponent tables: `eval/results/trace_profile_greedy_v2.md`.

## Evidence

| run | result |
|---|---|
| validation seeds 21–60 (E-011, as `lab_breaker_ret8_intercept`) | +0.42 [+0.30, +0.54] vs greedy, head-to-head 1.76 |
| validation seeds 61–100 (E-012, confirmation) | +0.42 [+0.32, +0.51], head-to-head 2.16 |
| 7-member round robin (E-017) | 1.62 points per game, the only member that beats every other head-to-head |
| held-out teams (E-015, tuning seeds) | 1.16 points per game (heldout_b: 0.89), generalisation gap R ≈ 32% |
| locked test seeds (E-021) | 1.55 points per game; lost to greedy_v3 by −0.26 (pool) and −0.17 (held-out) |

## Known blind spots (E-014, where greedy_v2 loses points)

| kind of lost points | share | cause |
|---|---|---|
| our defence (opponent returned more) | 29% | the defender is 5–8 cells from the invader on average and never closes in; it ignores the sonar → fixed in part by greedy_v3's shadowing |
| our deaths | 26% | 78–94% of deaths are in dead ends whose exit the ghost could reach first; the race-safety check only looks at the way *to* the food |
| 0–0 ties with barely any attack | 18% | a guard follows the breaker to the new entry |
| a "mutual-trap freeze" | unknown | both teams hold each other's attacker until the end (traced once) |

Fixes tried for these and rejected (E-018): exit-race check, cut-cell squeeze, raiding defender. See [../agents.md](../agents.md).
