# greedy_v3: current submission

- **File**: `teams/greedy_v3.py`. `my_team.py` is the same code with a different header.
- **In `my_team.py`**: since 2026-10-18 (E-021).
- **Previous pick**: [greedy_v2](greedy_v2.md).
- **One-line summary**: greedy_v2's cautious attacker, plus a defender that keeps a probability map of where each enemy is. When there is nothing to chase, it stands across from the enemy attacker's likely crossing point.

## Mindset

- **Attacker: "cautious opportunist"** (unchanged from greedy_v2).
  - It only takes food it can provably reach before any ghost it can see.
  - It banks at 8 food and runs when a ghost is within 4 steps.
  - When a guard blocks it, it walks to another border entry.
- **Defender: "goalkeeper who watches the striker"** (new).
  - It reacts to invaders like greedy_v2: intercept, chase, or keep its distance when scared.
  - Its idle time goes to standing across the border from the enemy raider, rather than to a fixed patrol.
  - Most attackers, like ours, won't cross where a ghost would reach them first. So this stops crossings before they happen. It works by **deterrence**: fewer invasions, fewer kills.

Both agents decide every move by a fixed priority list (first match wins). They don't search ahead, have no learned weights, and share no memory. Their only randomness is a private random generator that breaks exact ties.

## What each agent knows

| information | attacker | defender |
|---|---|---|
| Walls, all food, capsules, score, time left | yes | yes |
| Enemies within Manhattan 5 of either of our agents (exact position) | yes | yes |
| Capsule timer: when an enemy-side capsule disappears (only we can eat those), both enemy ghosts count as scared for 40 − 3 of their moves, unless seen respawning | yes | yes |
| Enemy respawns: an enemy seen within 2 of one of us that vanishes, or that reappears far away | yes | yes (with the T-55 fix: our own teammate's death doesn't count) |
| **Probability map** (belief) over the cells of each enemy | – | **yes** |

**The probability map** (`update_belief`). The defender updates it every turn from its own observation only, without the grey-zone fields (rules.md Q3, Q4):
1. Each enemy takes one step: it stays with weight 0.2, or moves to each neighbouring cell with weight 1.
2. Cells within Manhattan 5 of either of our agents are removed, because the enemy would be visible there. A visible enemy is placed on its exact cell.
3. Cells whose Manhattan distance to us is more than 6 away from our noisy distance reading are removed.
4. If one of our food dots or capsules vanished with no enemy on it, the most likely enemy is placed exactly on that cell. It can't have moved since: each enemy moves once between our turns.
5. An enemy that was eaten is reset to its start cell.
6. The map is renormalised. Nothing is dropped for being merely unlikely (T-54).

It was verified against true positions: the true cell is never ruled out, and the most likely cell is a median 4 steps from the truth, against 9 for "last seen" (E-019).

## Attacker: decision list (trace rule in brackets)

The attacker counts a ghost as dangerous when it is visible, on its own side, and not believed scared.

1. **Go home** (`home`) when carrying food and any of these holds:
   - carrying ≥ 8;
   - ≤ 2 food left;
   - this trip would win the game;
   - just enough time left to get home (+3 moves);
   - a dangerous ghost is within 4 maze steps.

   It takes the shortest path home through "race-safe" cells only: cells it reaches strictly before every dangerous ghost (cells on our side always count as safe). While threatened, a capsule counts as an escape target too.
2. **Keep walking to the chosen entry** (`entry`), if the standoff breaker committed to one.
3. **Eat** (`eat`): walk to the nearest food that it reaches strictly before every dangerous ghost, along race-safe cells.
4. **Standoff breaker** (on our side only, when a ghost blocks every safe food):
   - It counts blocked moves (`blocked`).
   - After 3 blocked moves within its last 12, it goes for a capsule it reaches first (`capsule`).
   - Otherwise it commits to the border entry whose cell across is farthest from the ghosts and walks there on our side (`switch-entry`, then `entry`).
5. **Fallback**: head back towards our border. If no safe path exists, it steps away from the nearest ghost (`evade`), and the trace says "cut off" when it isn't even trying to go home.

## Defender: decision list

1. **Scared** (`scared`): if they ate our capsule and an invader is visible, it keeps about 3 steps from it, on our side.
2. **Intercept** a visible invader:
   - within 2 steps → go at it (`chase`);
   - in a dead end whose exit is on our side → hold the exit (`cut-off` / `hold`), or walk in if it already stands between the invader and the exit;
   - otherwise → go to the first cell on the invader's shortest way home that it reaches no later than the invader (`cut-off` / `hold`).
3. **Last evidence** (`last-evidence`): walk to where our food just vanished.
4. **Shadow** (`shadow`), new in v3: stand at the home border cell whose cell across has the smallest expected maze distance to the **raider**, using the probability map; ties go to the nearer cell.
   - The raider is the enemy most recently evident on our side: seen there, or with ≥ 50% of its probability there.
   - It stays the raider until the other enemy shows the same evidence.
5. **Patrol** (`patrol`): until any enemy has come over, it cycles through the 3 border cells nearest the "centre" of our remaining food, exactly like greedy_v2.

The defender never crosses into enemy territory.

## What changed from greedy_v2

| | greedy_v2 | greedy_v3 |
|---|---|---|
| Idle defender | patrols 3 border cells near the middle of our food | stands across from the raider's most likely crossing (rule 4) |
| Defender's knowledge of hidden enemies | none (last eaten food only) | probability map per enemy |
| Respawn bookkeeping | "enemy vanished next to us = eaten", even when *we* were eaten | our teammate's own death no longer counts (T-55) |
| Attacker | — | identical code |

## How it behaves (rule profile, E-022)

240 games against greedy, feature, camper, rusher, choke and exploit_v2 on tuning seeds 581–600, both colours. Shares of each agent's own moves:

| attacker rule | greedy_v3 | greedy_v2 | | defender rule | greedy_v3 | greedy_v2 |
|---|---|---|---|---|---|---|
| eat | 41.9% | 45.5% | | **shadow** | **50.8%** | – |
| entry | 25.4% | 24.2% | | patrol | 16.9% | 51.1% |
| evade | 12.7% | 12.3% | | chase | 14.3% | 20.3% |
| home | 11.0% | 11.6% | | last-evidence | 7.4% | 12.2% |
| blocked | 6.5% | 4.5% | | scared | 7.2% | 10.6% |
| switch-entry | 2.4% | 1.8% | | cut-off | 3.5% | 5.7% |
| capsule | 0.1% | 0.1% | | | | |

How to read it:
- **The defender** spends half its moves shadowing and less time chasing, going to eaten food or being scared. Fewer invasions reach our side.
- **The attacker** is the same code, yet it eats slightly less and is blocked slightly more than in greedy_v2. A likely cause [untested] is shared sight (T-56): the shadowing defender stands at the border and reveals enemy ghosts to our attacker, which then waits.
- **"Walking to an entry" takes about a quarter of the attacker's moves**, up to 38% against guards (exploit_v2, camper).
- **The attacker is "cut off"** (`evade`) about 12% of the time.

Per-opponent tables are in `eval/results/trace_profile_greedy_v3.md`.

**Outcome statistics** (team totals per game, greedy_v2 → greedy_v3, E-019):
- Food conceded falls by 20–30% against every pool opponent (e.g. camper 8.1 → 6.2, feature 10.0 → 7.5).
- Kills fall (e.g. camper 1.14 → 0.67).
- Food returned is about unchanged.

## Evidence

| run | seeds | greedy_v3 − greedy_v2 [95% CI] |
|---|---|---|
| screen (E-019, as `lab3_shadow`) | tuning 331–430 | +0.34 [+0.23, +0.45] |
| replication (E-019) | tuning 451–550 | +0.29 [+0.19, +0.39] |
| validation (E-019) | validation 101–180 | +0.16 [+0.04, +0.28] |
| release gate, pool (E-021) | locked test seeds, 100 | +0.26 [+0.15, +0.36] |
| release gate, held-out teams (E-021) | locked test seeds, 100 | +0.17 [−0.00, +0.33] |

- Head-to-head vs greedy_v2: 1.56 points per game (E-021).
- Timing: max move 0.091 s (Windows, 6 parallel games) and 0.105 s (Linux / Python 3.8 with every CPU busy). Startup ≤ 1.13 s.

## Parameters

| constant | value | role |
|---|---|---|
| `return_at` | 8 | food carried before going home |
| `THREAT_DIST` | 4 | maze distance at which a visible ghost sends a carrier home |
| `TIME_MARGIN` | 3 | spare own moves when racing the clock home |
| `SCARED_TIME`, `SCARED_MARGIN` | 40, 3 | enemy moves a capsule lasts; treated as over 3 moves early |
| `STANDOFF_MOVES`, `STANDOFF_WINDOW` | 3, 12 | blocked moves within the last 12 that trigger the breaker |
| intercept "close" | 2 | within this maze distance the defender goes straight at the invader |
| keep distance | 3 | while our defender is scared |
| patrol | 3 cells | border cells nearest the middle of our food |
| `HUNT_MASS` | 0.5 | probability on our side that marks an enemy as the raider |
| `STAY_WEIGHT` | 0.2 | probability-map motion model: stay vs each neighbour (1) |
| `SIGHT`, `SONAR_NOISE` | 5, 6 | engine sight range and sonar noise (T-22, T-23) |

The switches `hunt`, `roles`, `tracker` and `adaptive` exist in the file but are off. They were tested and rejected (see [../agents.md](../agents.md)).

## Known blind spots

| blind spot | effect | evidence |
|---|---|---|
| The attacker ignores ghosts it can't see | most deaths happen in dead ends a ghost can close | E-014 (greedy_v2, same attacker) |
| The attacker gets cut off on the enemy side | ~12% of its moves spent backing away from a ghost that blocks the way home | E-022 profile |
| Relocating between entries | ~25% of attacker moves walking along our border against guards | E-022 profile |
| Raider identity is a guess | the "≥ 50% on our side" evidence is right about 57% of the time; against two attackers it shadows one | E-019 probe |
| Deterrence assumes ghost-avoiding attackers | every attacker in our pool avoids visible ghosts; one that ignores ghosts would not be deterred | E-019 caveat; held-out +0.17 suggests it carries over |
| No coordination | the agents share nothing (designed while Q4 was open; shared memory is allowed since 2026-10-22); the defender never attacks | design |
| Generalisation | 1.97 points per game against the pool, 1.40 against the blind-written teams (R ≈ 29%) | E-021 |
