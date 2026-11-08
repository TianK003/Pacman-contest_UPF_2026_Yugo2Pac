# greedy_v4: current submission (since 2026-11-08, E-032; confirmed by the user the same day)

`teams/greedy_v4.py` = `teams/greedy_lab_v7.py` with the `lab7_danger_netf` options as defaults (identity 18/18 vs `lab7_danger_net`, E-032). `my_team.py` is a copy.

**In one line**: greedy_v3's rule-based team plus lab5_smart's enemy-state switches, with a **width-based planner** that takes over the attacker's move while an enemy ghost is near, and judges the futures it finds with a **learned value** of the greedy policy.

## Mindset

- Most of the time it is still the greedy team: eat the nearest food we reach before every visible ghost, bank at 8 unless nobody can catch us (open_goal), break standoffs, defend by shadowing the raider's likely crossing.
- **Near ghosts it looks ahead.** When a non-scared enemy ghost (visible, or hidden at its belief cell) is within 7 maze steps, the attacker runs an IW(1) search over its own moves in a small model of the world (ghosts chase within 6 steps or hold their post). Each future is scored by the food it banks and eats along the way plus a **learned estimate** of what the state is worth over the next 30 moves (food banked minus food dropped by dying, under the greedy policy). The first move of the best future is played.
- The learned value is what makes the lookahead safe. The hand-made version was optimistic and died more than greedy (E-030).

## What each agent knows (unchanged from lab5_smart, E-025)

- Exact belief over each enemy's cell, shared by both agents (both agents' sonar; food events pin an enemy).
- Hidden enemies' side, food carried and scared timer (`flags`, rules.md Q3: allowed).
- Map analysis: all-pairs maze distances, home border, dead-end depth.

## Attacker: decision list

1. **Special cases stay with greedy** (in this order): fewer than 3 food left; our team's returned + carried food reaches the win threshold; endgame banking (last 40 moves, behind, a trip takes the lead); not enough moves left to get home.
2. **Planner** (`plan=danger`), if a non-scared modelled ghost is within `plan_trigger` = 7:
   - Search: breadth-first IW(1), novelty atom = (cell, carried bucket), horizon 30, at most 2,000 expanded nodes, 0.3 s clock safety net.
   - Atoms only for surviving states (`plan_v=2`); Stop is generated; every root action keeps a value.
   - Model: we move, then each ghost moves (chase within 6 maze steps, else hold; scared ghosts flee); death on contact on their side.
   - Rewards: eat +0.5, bank +0.5 per food, death −(0.5·carried + 3), eat a scared ghost +1, capsule +0.3, discount 0.97.
   - Leaf: `LEAF_NET` (12 features: carried, distance home, two nearest ghost distances, scared time, food left / nearest / within 5, time left, side, capsule distance, dead-end depth → 16 tanh → 1), minus 0.5·carried. Fast code path `netf`.
   - The planner's move is played if its best value > 0.05 and the move is legal. Otherwise greedy decides.
3. **Greedy rules otherwise** (greedy_v3 / lab5_smart; see [greedy_v3.md](greedy_v3.md)): go home when carrying ≥ 8 (ignored while `open_goal` says nobody can catch us), when threatened (ghost ≤ 4), or out of time; else follow the standoff breaker's entry, else eat the nearest race-safe food, else break the standoff (capsule or far entry).

How often the planner decides [verified, 48 agent-games vs greedy_v3 and choke on tuning seeds 591–596]: 51 of each agent's 300 moves on average (max 163), **17% of all our moves**. `eval/trace_game.py` does not label planner moves yet: it infers greedy rules after the fact.

## Defender

Unchanged from lab5_smart: intercepts visible invaders, goes to eaten food, shadows the raider's likely crossing with the shared belief, patrols. Endgame: ahead in the last 40 moves → both defend; behind → both attack. See [greedy_v3.md](greedy_v3.md) for the rules and the trace names.

## What changed from greedy_v3

| change | from | evidence |
|---|---|---|
| hidden-enemy fields, shared belief, endgame roles, directed belief, open_goal | lab5_smart (E-025) | validation 181–220: +0.25 [+0.11, +0.40] vs greedy_v3 |
| width-based attacker planner with learned leaf value | E-028–E-031 | tuning 401–440: +0.57 vs lab5_smart; **validation 221–260: +0.95 [+0.78, +1.13] vs greedy_v3, +0.58 [+0.42, +0.74] vs lab5_smart** |

## Evidence

- **V1** (E-031, validation seeds 221–260, 1,920 games): accept rule passed against greedy_v3 (pool Δ +0.95, every opponent's CI > 0, head-to-head 2.56) and against lab5_smart (+0.58, head-to-head 2.31). Gates: 0 crashes / warnings / violations; max move 0.319 s, p95 0.178 s under ≈ 12 parallel workers (slow leaf code; the shipped fast code halves planner time).
- Team totals per game in V1: returned 17.3 (lab5_smart 11.5), conceded 8.6 (9.3), deaths 0.36 (1.00), carried food dropped 0.9 (2.6), games ended by returning 28 food: 25 of 720 (7).
- Also positive on two independent tuning blocks vs lab5_smart: 401–440 (+0.57), 441–480 (+0.50).
- **Settings are a flat optimum** (E-034, tuning 321–400, paired with greedy_v4): trigger 5 / 9, horizon 40, plan_min 0.3 and a 60-move leaf target are all within ±0.05; planning on every attacker move loses 0.38. Only override mode (greedy decides, the planner overrides near ghosts by margin 0.3) is slightly better: +0.06 [+0.00, +0.12] over 1,440 games, the candidate for the next validation round.
- **The neural net is replaceable** (E-033): a quadratic ridge regression on the same 12 features (91 coefficients, `teams/greedy_lab_v10.py` `plan_leaf=quad`) plays equal, pooled −0.02 [−0.09, +0.04] over 1,440 games. A lookup table with the same R² loses 0.33 (T-59). Monte-Carlo search on top loses 0.43 (T-60).
- **Second-iteration nets** trained on the planner's own games do not help (−0.04 / −0.15, X3 in E-031).

## Parameters

| parameter | value | where |
|---|---|---|
| plan / plan_v | danger / 2 | `V6_DEFAULTS` |
| plan_trigger, plan_r, plan_h | 7, 6, 30 | `V6_DEFAULTS` |
| plan_a, plan_death, plan_gamma, plan_min | 0.5, 3, 0.97, 0.05 | `V6_DEFAULTS` |
| plan_nodes, plan_budget | 2000, 0.3 s | `V6_DEFAULTS` |
| plan_leaf | netf (`LEAF_NET`) | trained by `eval/rl/train_value.py` on 450 lab6_off games (tuning seeds 1–25), held-out R² 0.46 |
| lab5_smart switches | flags, shared, endgame, directed, open_goal = 1 | `create_team` defaults |
| return_at, threat_dist, open_margin | 8, 4, 4 | as greedy_v3 / lab5_smart |

## Known blind spots

- **Generalisation**: decisions used only our own pool (the net was trained against it). A diagnostic against 13 outside opponents, including friend teams, gave +0.77 [+0.57, +0.98] over greedy_v3 with no opponent negative (E-035; not a decision input). Held-out teams and the locked test seeds have not been used (release gate, user decision).
- **Timing**: planner time p99 ≈ 0.12 s, max ≈ 0.13 s with the fast code on this laptop under load. A slower cluster would hit the 0.3 s safety clock more often: still safe, but then decisions depend on load. Linux / Python 3.8 with real time limits, CPU saturated: 40 games, 0 warnings, max move 0.283 s (E-032).
- **Ghost model**: chase-within-6 or hold. An opponent that intercepts from far away is modelled only through the learned leaf.
- **Double attackers** (both enemies on our side) are not in the pool; the planner is attacker-only.
- `trace_game.py` mislabels planner moves as greedy rules.
