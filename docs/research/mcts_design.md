# Design: non-deep-learning search for the attacker (MCTS and knowledge leaves) — draft for review

Status: **draft 2, 2026-11-08 04:10** = what was built in `teams/greedy_lab_v8.py` (E-033). Draft 1 (03:45, kept below as history) was critiqued by an advisor agent (Fable, xhigh effort) before any code was written. Tags as in docs/README.md; everything is [untested] unless cited.

## Draft 2: changes after the review

| draft 1 | review finding | draft 2 (built) |
|---|---|---|
| UCT, 150 iterations, c = 2 on raw returns, most-visited root | noise-dominated: per-child SE 0.3–0.8 vs decision gaps 0.3–1.0; c = 2 on a ~17-unit return range is near-greedy selection | **flat paired MC** (`plan=fmc`): every root move is simulated against the *same* scenarios, so the scenario effect cancels in differences; UCT kept only as an extra arm (`plan=mcts`, depth ≤ 4, min-max normalised UCB, c = 1). The tree only *proposes* a line; root values come from the paired re-evaluation |
| i.i.d. sampling of top-8 belief cells | wastes budget | **enumerated** top-4 cells per hidden ghost, best 4 joint placements, weights = belief mass |
| per-step ghost mixture (0.7 chase / 0.2 intercept / 0.1 random), unaware ghosts stay 70 % | the ghost makes ~0.7 steps of progress per ply, too slow, so the mean stays optimistic; our own pool infers our position | **one type per ghost per scenario**, deterministic: chase 0.5, intercept 0.3, camp 0.2. Visible ghosts are aware; hidden ones until we come within `plan_r` or eat food in the simulation |
| ε = 0.1 random rollout moves | 92 % of 24-move rollouts contain a random move; near ghosts that is a death the real agent would not choose (timidity) | **ε = 0**, deterministic greedy-in-model; threat distance 4 = greedy's; target committed, re-picked every 4 moves; rollout ends at banking |
| death checks unspecified along open-loop paths | alive / dead is not deterministic along a path | a simulation ends at the first death; backup only through the nodes it reached |
| root decision by visits; `mcts_override` as a separate arm | — | **override-by-margin for every MC arm**: greedy's move unless the best is > `mc_margin` = 0.3 better in the same paired evaluation |
| race leaf with τ = 1, offset 0.5, D_leaf = 1.5 | m = 0 is death, not P = 0.62; parameters must be fitted; one D | **not built yet** (needs a collection that logs the margin m); reserve arm |
| tabular leaf on (carried, ghost, home) | omits side (a ghost across the border is harmless) and scared | **5-D table** (+ side, + nearest ghost scared ≥ distance + 1), 1,372 cells, shrunk to (carried, ghost, side). Held-out R² 0.453 vs net 0.464 on the same rows |
| speed estimate 0.3–0.6 ms per iteration | 2–3× optimistic; 30-food scans per step | target commitment, flat lists, no copies per step: **fmc p99 14 ms, mcts p99 59 ms** under full load (E-033) |
| global `random` unconstrained | a rollout drawing from the global RNG would consume the engine's sonar-noise stream; the lint does not catch it | **no random numbers at all**; the lint now warns on `random.<draw>(` |

Screen and pre-stated reading: E-033.

---

# Draft 1 (history)


## 1. Why (what the deep-learning result taught us)

E-030/E-031 [verified]: the IW(1) attacker planner with a **hand-made leaf** was barely better than lab5_smart (+0.06), while the same planner with a **learned leaf value** (12-16-1 MLP predicting food banked − food dropped over the next 30 moves under the greedy policy) gained +0.57 (tuning) / +0.58 (validation vs lab5_smart) and cut deaths from 1.31 to 0.36–0.40 per game. Diagnosis [verified, E-030]: the planner backs up the **max** over a **deterministic** ghost model, so a root action is only "dangerous" if every continuation dies (death penalty 3 vs 8 changed no decision; the shield veto never fired). The net instead prices a state by its *expected* outcome under real play.

Hypothesis [untested]: three non-DL ways get the same effect, each combining search with existing knowledge:
- **A. Information-set MCTS** with greedy-policy rollouts under a *stochastic* ghost model and belief sampling: the **mean** backup is risk-aware by construction.
- **B. Race-analysis leaf** for the existing IW planner: an explicit escape probability from the race test we already trust (H-S03, the intercept cell, dead-end exits).
- **C. Tabular Monte-Carlo leaf** (naive RL: lookup table of the mean 30-move outcome by (carried, nearest-ghost distance, distance home) buckets, from the same 128k states the net used); **D. linear leaf** (least squares on the net's 12 features) as the "is it the nonlinearity?" control.

The user asked for MCTS "or similar, combined with existing knowledge"; A is the main design, B–D are cheap controls in the same file.

## 2. Shared integration (unchanged from greedy_v4)

- Trigger: the attacker plans only while a non-scared modelled ghost (visible, or hidden at its belief cell via flags) is within `plan_trigger` = 7 maze steps; otherwise greedy (lab5_smart rules) moves.
- Special rules keep control: `len(food) <= 2`, `returned + carrying >= food_to_win`, endgame banking, time margin home.
- The planner's action must be legal, else greedy's.
- Model data: `WidthModel` (cell indices, `nbr`, `gnbr` = enemy-side neighbours, `dist` all-pairs lists, `home`, `dhome`, `icept` = enemy cell across our nearest home-border cell, `depthv`), built once per game.
- Rules: own `random.Random` per agent, reseeded at `register_initial_state` (determinism and paired evaluation); no global RNG; no threads; never catch `TimeoutFunctionException`; stdlib only.

## 3. Design A: open-loop information-set MCTS ("ISMCTS-lite")

### 3.1 State and transition
- Our state along a tree path is **deterministic** given our actions (ghosts never block us): cell, carried, food mask, capsule mask, step. Only ghost cells / scared timers are random. So the tree is keyed by our action sequence (open loop), and legal actions per node are well defined.
- Turn order approximation: we move, then each modelled ghost moves once (as in the IW model).
- Collision on the enemy side: ghost not scared → we die (terminal); scared → ghost eaten (+kill, removed).
- Ghosts never cross to our side (`gnbr`).

### 3.2 Determinization (once per iteration)
- Visible enemy ghosts: exact cell, exact scared timer (visible state).
- Hidden enemy ghosts with `is_pacman == False` (flags): sample one cell from the shared belief restricted to their side, among the top-8 cells by mass (renormalised). No mass on their side → not modelled.
- Enemy Pacmen are irrelevant to our attacker on their side (not modelled).

### 3.3 Stochastic ghost policy (per ghost, per step)
- Scared (`s > 0`): flee (step maximising maze distance to us) with p = 0.8, else a random enemy-side neighbour or stay; `s -= 1`.
- **Aware** (Manhattan distance to us ≤ 5 = sight, or maze distance ≤ `plan_r` = 6): with p_chase = 0.7 step minimising maze distance to us; p_int = 0.2 step toward `icept[our cell]` (cut us off from home); 0.1 random neighbour / stay.
- Unaware: stay with p = 0.7, else random enemy-side neighbour.
(The mixture stands for unknown opponent types: chasers, interceptors, campers. Parameters are guesses → tunable.)

### 3.4 Tree policy
- UCB1 on mean return: `Q/N + c * sqrt(ln N_parent / N_child)`, `c = mcts_c` (default 2.0; returns are roughly in [−6, +8] food units).
- Unvisited children are tried first, **greedy's action first** (knowledge as move ordering / progressive bias); optional prior bonus `w_prior / (1 + N)` for greedy's action.
- Expansion: one node per iteration; tree depth ≤ 10.
- Actions: legal neighbour moves + Stop.

### 3.5 Rollout policy (existing knowledge = the greedy attacker, in the model)
From the tree leaf until total depth H = 24 (tree + rollout) or death; ε = 0.1 uniform random move:
1. **Home mode** if carried ≥ 8 (`return_at`), or carried > 0 and a non-scared ghost is within 3 maze steps, or steps left ≤ dist_home + 3: step to the neighbour minimising `dhome`, skipping cells within 1 of a non-scared ghost (if all are, maximise ghost distance).
2. **Food mode** otherwise: target = nearest food f with `dist[us][f] < min_g dist[g][f]` (race-safe vs non-scared ghosts); step minimising `dist[n][f]`, skipping ghost-adjacent cells; no safe food → home mode.
3. After banking, keep foraging (food mode) until the horizon.

### 3.6 Value
- Rewards as in the IW planner: eat +a (a = 0.5), bank +(1 − a) per food, death −(a·carried + D) with **D = 3** (now meaningful: mean backup), scared ghost +1, capsule +0.3, discount γ = 0.97 per step.
- Cutoff value at H: hand leaf `carried·(1−a)·γ^dhome` if home is reachable in time, else `−a·carried` (variant: race leaf B).
- Backup: mean discounted return per (node, action).

### 3.7 Decision and budget
- Fixed iteration count `mcts_iters` = 150 (deterministic), clock safety net `plan_budget` = 0.25 s.
- Final move: most-visited root child; ties → higher mean.
- Modes: `mcts` (MCTS decides in the danger trigger) and `mcts_override` (play MCTS's move only if mean(best) − mean(greedy's action) > 0.2 and greedy's action has ≥ 10 visits).
- Estimated cost [untested]: ≈ 24 model steps × (2 ghosts × 4 neighbour checks + ≤ 30-food scan) ≈ 1–2 k Python operations per iteration ≈ 0.3–0.6 ms → 150 iterations ≈ 50–90 ms; to be measured.

## 4. Design B: race-analysis leaf for IW (no learning)
For a non-terminal leaf at cell c with carried k, ghosts g (non-scared):
- On our side: value 0 (+ the existing small food-distance shaping).
- On their side: escape margin `m = min( min_g dist[g][icept[c]] − (dhome[c] − 1),  min_g dist[g][c] − 2,  dead-end term )`, dead-end term (if c is in a dead-end tree) = `min_g dist[g][entrance] − dist[c][entrance]`.
- `P = 1 / (1 + exp(−(m + 0.5) / τ))`, τ = 1.
- `V = P · k·(1−a)·γ^dhome − (1 − P) · (a·k + D_leaf)`, D_leaf = 1.5, + food shaping.

## 5. Design C / D: naive learned leaves
- **C (tabular MC)**: buckets carried {0,1,2,3–4,5–7,8–11,12+} × nearest-ghost distance {≤1,2,3,4–5,6–8,9–12,13+} × dist_home {0,1–2,3–5,6–9,10–14,15–20,21+} = 343 cells; cell value = mean of the 30-move outcome (banked − dropped) over the d1 + d2 states in it; shrink sparse cells to the (carried, ghost) marginal: `(n·mean + 30·parent)/(n + 30)`. Leaf = T − a·k (same convention as the net). Shipped as a constant.
- **D (linear)**: least squares on the net's 12 features (held-out R² 0.21–0.34 vs MLP 0.46–0.59). 13 constants.

## 6. Screen plan (E-033)
- New file `teams/greedy_lab_v8.py` = v7 + `plan='mcts'|'mcts_override'`, `mcts_*` options, `plan_leaf='race'|'table'|'lin'`; defaults off. Identity: `lab8_off` = lab7_off; lab8 with greedy_v4's options = greedy_v4 (18 games each).
- Fresh tuning seeds 521–560, against the 8 pool members + lab5_smart + greedy_v4, paired with greedy_v4 (the incumbent): arms `lab8_mcts`, `lab8_mcts_override`, `lab8_race`, `lab8_table`, `lab8_lin`, and `lab8_mcts_race` (MCTS with the race leaf at the cutoff).
- Gates as always (0 crashes / warnings / violations, max move ≤ 0.5 s under load).
- Question answered: does any non-DL arm match greedy_v4 (Δ ≥ 0 within CI)? Which ingredient carries the effect (stochastic expectation, race knowledge, tabular values)?

## 7. Open questions for the reviewer
1. Is open-loop MCTS right here, given our own state is deterministic along a path, or should ghost outcomes be chance nodes (closed loop)?
2. Are 150 iterations enough to beat noise for a 5-way root decision? Should the root use greedy's action as a default unless clearly worse (override), or decide outright?
3. The ghost mixture parameters are guesses: risk of mis-modelling chasers vs campers? Better: sample a ghost *type* per iteration (chaser / interceptor / camper) rather than mixing per step?
4. Rollout policy cost vs quality: is a 30-food scan per step affordable, or should rollouts use a precomputed "next step toward nearest food" table?
5. Anything that would break determinism, the time limit, or the rules?
