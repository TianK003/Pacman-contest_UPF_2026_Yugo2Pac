# Agent catalogue

Every team we have built or played against, what it is, what it was tested on, and what we concluded. **Read this before building a "new" idea**: many ideas have already been tried, and the experiment IDs say where.

- **Names** are the entries in `eval/league.json`, which hold the file path and the `create_team` options.
- **Numbers**:
  - "Δ vs X" is the paired difference in points per game (3/1/0) against the incumbent X on the same games, with a 95% CI.
  - "PPG" is mean points per game.
  - Numbers from different experiments used different pools and seeds, so compare them only within one experiment (evaluation.md).
- **Verdicts**:
  - **incumbent** = in `my_team.py`.
  - **past version** = a former incumbent, kept for the forgetting check.
  - **pool** = a member of the reference pool that new candidates play.
  - **league** = an opponent available for broader checks.
  - **rejected** = tested and not adopted.
  - **identity** = only exists to check that a lab file with its switches off plays like its parent.
- **Freeze rule**: files are never edited after they have been benchmarked (T-48). A new version gets a new file.

## Lineage of our submission

Each version that has been in `my_team.py` has a behaviour page in [picks/](picks/README.md): its decision rules, parameters, rule profile, evidence and blind spots.

| version | = | adds | accepted in | in `my_team.py` |
|---|---|---|---|---|
| [`greedy`](picks/greedy_v1.md) (`teams/greedy_v1.py`) | race-safe greedy attacker + patrol defender | — | E-002/E-003 (provisional) | 2026-10-16 → 2026-10-18 |
| [`greedy_v2`](picks/greedy_v2.md) (`teams/greedy_v2.py`) | greedy + standoff breaker + intercepting defender + return at 8 | H-S12, H-S07, H-S04 | E-011, E-012 (+0.42 vs greedy) | 2026-10-18 (E-013) → 2026-10-18 (E-021) |
| [`greedy_v3`](picks/greedy_v3.md) (`teams/greedy_v3.py`) | greedy_v2 + belief-based shadowing defender | H-S01, H-S07, M-04 | E-019 (+0.16 [+0.04, +0.28] vs greedy_v2 on validation seeds); E-021 test seeds +0.26 pool / +0.17 held-out | 2026-10-18 (E-021) → 2026-11-08 (E-032) |
| [`greedy_v4`](picks/greedy_v4.md) (`teams/greedy_v4.py`) | greedy_v3 + lab5_smart switches + IW(1) attacker planner with learned leaf value | M-15, H-S01, Q3 flags | E-031 (+0.95 [+0.78, +1.13] vs greedy_v3, +0.58 vs lab5_smart on validation 221–260) | **since 2026-11-08 (E-032)**; release gate passed (E-037: test seeds +0.83 pool, +1.02 held-out) |

## Our teams

### `teams/greedy_v1.py`: the first agents (E-002)

| name | what it is | tested in | key result | verdict |
|---|---|---|---|---|
| `greedy` | `GreedyAttacker` (nearest food it reaches before any visible ghost; home at 5 carried, when threatened, out of time) + `PatrolDefender` (chases visible invaders, goes to eaten food, patrols 3 border cells near our food) | E-002, E-005, E-006, E-017 | best of the v1 league (2.23 PPG, 40/40 vs baseline); loses 0–0 standoffs to guards and scoring races to double attackers (E-005) | **past version**, league (left the pool 2026-11-08, E-036) |
| `greedy_deadend` | greedy with `DeadEndAttacker`: enters a dead end only if it can get back to the exit before a visible ghost (H-M02 leaf version) | E-002 | Δ −0.01 [−0.10, +0.07] vs greedy | **rejected**. The generalised version (`lab2_exit`) halves deaths but gains no points (E-018) |
| `double_attack` | 2 × `GreedyAttacker`, no defence | E-002, E-006, E-014 | 1.29 PPG in E-002; wins scoring races against greedy | **league** (specialist) |
| `turtle` | 2 × `PatrolDefender`, never attacks | E-002, E-005 | 0.38 PPG; produces 0–0 standoffs | **league** (specialist) |

### `teams/sparring_v1.py`: sparring opponents (E-006)

| name | what it is | tested in | key result | verdict |
|---|---|---|---|---|
| `camper` | greedy attacker + `BorderCamper` (stands on our border cell nearest where the enemy would cross, seen or last seen within 40 plies) | E-006, E-014, E-017 | 1.83 PPG in E-006, beat greedy head-to-head; greedy_v2's hardest old opponent (1.51) | **pool** |
| `camper2` | 2 × `BorderCamper` | E-006 | 0.73 PPG; 0–0 standoffs | **league** |
| `rusher` | `CapsuleRusher` (capsule first, return at 12, hunts scared ghosts) + `PatrolDefender` | E-006, E-014, E-017 | 1.79 PPG in E-006, beat greedy head-to-head | league (left the pool 2026-11-08, E-036) |
| `baseline_plus` | baseline-style reflex team, return at 5, ghost avoidance | E-006 | 0.95 PPG | **league** |
| `rusher_camper` | `CapsuleRusher` + `BorderCamper` (both parts had beaten greedy) | E-007 | Δ +0.00 [−0.26, +0.33] vs greedy | **rejected** (strength is not additive) |

### `teams/greedy_lab_v1.py`: switches on top of greedy_v1 (E-007, E-010, E-011)

All entries are greedy_v1 plus the named switches.

| name | switch(es) | tested in | key result | verdict |
|---|---|---|---|---|
| `lab_off` | none | E-007 | 18/18 identical to greedy | **identity** |
| `lab_roles` | `roles`: attacker defends on 2 invaders; defender attacks after 25 quiet moves; endgame lead → both defend, deficit → both attack | E-007 | Δ +0.12 [+0.00, +0.23], but **head-to-head 0.95** vs greedy, camper −0.45 | **rejected** in this form; parts re-tested as raids (E-018, E-020) |
| `lab_breaker` | `breaker`: after 3 blocked moves at the border, take a capsule or walk to the entry farthest from the ghosts | E-007, E-010, E-011 | +0.13 [+0.02, +0.24] (tuning 11–50), +0.26 [+0.15, +0.38] (validation 21–60) | **adopted** in greedy_v2 |
| `lab_tracker` | `tracker`: set of cells each hidden ghost can be in, used in the attacker's race-safety | E-007, E-010 | −0.11 [−0.29, +0.02] alone (the attacker becomes timid); nothing on top of the breaker | **rejected** for the attacker (see T-56) |
| `lab_intercept` | `intercept`: the defender goes to the cell on the invader's way home that it reaches first, or holds its dead end's exit | E-007, E-010 | +0.01 alone; +0.17 with the breaker | **adopted** in greedy_v2 |
| `lab_ret3`, `lab_ret8`, `lab_ret12` | `return_at` 3 / 8 / 12 (greedy: 5) | E-007, E-010 | alone within noise; 8 best with the breaker | **8 adopted** in greedy_v2 |
| `lab_adaptive` | `adaptive`: return at 3 right after seeing a ghost, at 10 after 15 quiet moves, bank when home is ≤ 2 away | E-007, E-010, E-011 | +0.05 alone; +0.24 with the breaker, below return-at-8 (+0.37) | **rejected** (return-at-8 is simpler and better) |
| `lab_breaker_tracker` | breaker + tracker | E-007, E-010 | +0.13, same as the breaker alone | **rejected** |
| `lab_breaker_ret8` | breaker + return at 8 | E-010, E-011 | +0.21 (tuning), +0.37 (validation) | superseded by the next row |
| `lab_breaker_adaptive` | breaker + adaptive | E-010, E-011 | +0.18 (tuning), +0.24 (validation) | **rejected** |
| `lab_breaker_intercept` | breaker + intercept | E-010 | +0.17 (tuning) | superseded |
| `lab_breaker_ret8_intercept` | breaker + intercept + return at 8 | E-011, E-012 | **+0.42** on validation 21–60 and 61–100, head-to-head 1.76 / 2.16 | **became greedy_v2** |

### `teams/families_v1.py`: other agent families (E-008)

| name | what it is | tested in | key result | verdict |
|---|---|---|---|---|
| `feature` | F1: one-step weighted-feature attacker (M-02, hand-set weights) + `PatrolDefender` | E-007, E-008, E-010, E-011, E-017 | +0.44 on 10 seeds, but **+0.07 [−0.08, +0.20] on 40 fresh seeds** vs greedy; rarely dies | **pool**. Weight tuning (P-16) is still untested |
| `field` | F2: potential-field attacker (M-14) + `PatrolDefender` | E-007, E-008, E-010 | −0.04 [−0.20, +0.11] vs greedy, head-to-head 1.05, camper2 −0.40 | **rejected** |

### `teams/greedy_v2.py` (E-012, E-013)

| name | what it is | tested in | key result | verdict |
|---|---|---|---|---|
| `greedy_v2` | greedy_v1 + breaker + intercept + return at 8 (`lab_breaker_ret8_intercept` as defaults) | E-011–E-021 | +0.42 vs greedy (validation); 1.62 PPG in the 7-member round robin (E-017), the only member that beats every other; **1.16 PPG against the held-out teams** (E-015, a 32% generalisation gap); 1.55 PPG on the test seeds (E-021) | **past version**, pool (incumbent 2026-10-18, E-013 → E-021) |

### `teams/sparring_v2.py`: opponents built from greedy_v2's weaknesses (E-015)

| name | what it is | tested in | key result | verdict |
|---|---|---|---|---|
| `choke` | greedy_v2's attacker + `ChokeDefender` (guards the cut cell that seals off the most food, traps invaders behind cut cells; H-M03) | E-015, E-017 | 1.61 PPG mean in E-015; greedy_v2 scores 1.40 against it | **pool** |
| `exploit_v2` | F1 attacker + `ShadowDefender` (stands across from the last-seen raider, traps behind cut cells), written against greedy_v2 | E-015, E-017 | highest mean in the 7-member round robin (1.67) | **pool** |

### `teams/greedy_lab_v2.py`: fixes for E-014's findings (E-018)

All entries are greedy_v2 plus the named switches. Δ is against greedy_v2 on tuning seeds 151–250, 1,200 paired games each.

| name | switch(es) | key result | verdict |
|---|---|---|---|
| `lab2_off` | none | 18/18 identical to greedy_v2 | **identity** |
| `lab2_exit` | `exit_race`: target food only if we get back past every cut cell before any visible ghost | +0.02 [−0.06, +0.10]; deaths halve, but the attacker waits instead of scoring | **rejected** |
| `lab2_squeeze` | `squeeze`: trap invaders behind cut cells, close in, chase after a stalled intercept | +0.02 [−0.01, +0.06]; rarely changes a decision | **rejected** |
| `lab2_raid` | `raid`: defender attacks through the far entry while our attacker is held at the border | −0.07 [−0.14, +0.01]; scores more against guards, concedes more against attackers | **rejected** |
| `lab2_exit_squeeze`, `lab2_exit_raid`, `lab2_squeeze_raid`, `lab2_all` | combinations | +0.05, −0.01, −0.03, +0.03 (every CI includes 0) | **rejected** |

### `teams/greedy_lab_v3.py`: belief tracker for the defender (E-019)

All entries are greedy_v2 plus an exact belief filter over enemy cells. The filter uses only each agent's own observation: sonar, sight and food events. It does not use shared memory or grey-zone fields. **Verified** against true positions (`eval/belief_probe/`): the true cell is never ruled out, and the most likely cell is a median 4 steps from the truth.

| name | switch(es) | key result | verdict |
|---|---|---|---|
| `lab3_off` | none | 18/18 identical to greedy_v2 | **identity** |
| `lab3_hunt` | `hunt`: chase a hidden enemy that the belief puts on our side (mass ≥ 0.5) | +0.07 [−0.02, +0.17] vs greedy_v2; trigger precision only 57% | **rejected** |
| `lab3_shadow` | `shadow`: with nothing to chase, wait at the entry across from where the raider (the enemy last evident on our side) probably is | +0.34 (tuning 331–430), +0.29 (tuning 451–550), **+0.16 [+0.04, +0.28] (validation 101–180)**, head-to-head 1.65; works by deterrence (20–30% less food conceded) | **became greedy_v3** (in `my_team.py`) |
| `lab3_hunt_shadow` | hunt + shadow | +0.33, the same as shadow alone | **rejected** (hunt adds nothing) |

### `teams/greedy_lab_v4.py`: raid recalled by the belief (E-020)

| name | switch(es) | key result | verdict |
|---|---|---|---|
| `lab4_off`, `lab4_shadow` | none / shadow | 18/18 identical to greedy_v2 / lab3_shadow | **identity** |
| `lab4_braid` | `braid`: E-018's raid, held back and called back while the raider is expected near our side | smoke test only | not screened alone |
| `lab4_braid_shadow` | braid + shadow | −0.01 [−0.06, +0.04] vs lab3_shadow (tuning 451–550) | **rejected**; the raid line is closed for now |

### `teams/greedy_v3.py` (E-021)

| name | what it is | tested in | key result | verdict |
|---|---|---|---|---|
| `greedy_v3` | `lab3_shadow` as defaults (24/24 identical) | E-019, E-021 | locked test seeds (E-021): 1.79 PPG vs greedy_v2's 1.55; paired **+0.26 [+0.15, +0.36]** over the pool, **+0.17 [−0.00, +0.33]** over the held-out teams (heldout_b +0.35, heldout_a −0.02), head-to-head 1.56; Linux max move 0.105 s under full load | **past version**, pool (incumbent 2026-10-18 → 2026-11-08, E-021 → E-032) |

### `teams/greedy_lab_v5.py`: enemy-state switches on top of greedy_v3 (E-025)

All entries are greedy_v3 plus the named switches. Δ is against greedy_v3 on tuning seeds 151–200, paired over the 700 games against the 7 other pool members; h2h = head-to-head against greedy_v3. Research behind each switch: heuristics.md Part D.

| name | switch(es) | key result | verdict |
|---|---|---|---|
| `lab5_off` | none | 18/18 identical to greedy_v3 | **identity** |
| `lab5_flags` | `flags` (#1, H-S14): hidden fields for the belief's side, food attribution, respawns, the raider, scared timers | +0.11 [+0.00, +0.22], h2h 1.63; food conceded 8.2 → 6.6; side detection 58% → 100% | part of `lab5_smart` |
| `lab5_flags_hunt` | flags + `hunt` (#2) | +0.11 [−0.00, +0.22], −0.006 on top of flags, h2h 1.49 | **rejected** (hunt still adds nothing) |
| `lab5_shared` | `shared` (#3, H-S15): one team belief from both agents' sonar | belief error 4 → 2 steps [verified]; points +0.00 [−0.08, +0.08], h2h 1.38 | part of `lab5_smart` (rule margin +0.003) |
| `lab5_endgame` | `endgame` (#4, P-17c) | +0.01 [−0.02, +0.03], h2h 1.35 | part of `lab5_smart` (rule margin +0.006) |
| `lab5_track` | flags + `directed` (H-S17): goal-directed motion in the belief | +0.12 [+0.01, +0.23], +0.009 on top of flags; belief p(true) 0.17 → 0.18 | part of `lab5_smart` (rule margin +0.009) |
| `lab5_open` | flags + `open_goal` (H-S24): ignore return_at while nobody can reach us before home | **+0.17 [+0.05, +0.29]**, +0.057 on top of flags, no opponent below +0.01, h2h 1.63; max carried 7.4 → 8.9 | part of `lab5_smart`; best single entry |
| `lab5_guard` | flags + `guard` (H-S16): defender targets hidden invaders by carrying and likely goal | +0.03 [−0.09, +0.15], −0.08 on top of flags; rusher −0.27; vs double attackers −0.12 | **rejected** |
| `lab5_recall` | flags + `recall` (H-S26): two enemy Pacmen → attacker defends | never fired against the pool (800/800 = flags); **−0.58** vs double_attack, **−0.40** vs friend_aljaz_1 | **rejected** (it cuts our returns by a third) |
| `lab5_intent` | flags + directed + open_goal + guard + recall | +0.10 [−0.03, +0.22]; −0.29 vs double attackers (recall) | **rejected** |
| `lab5_all` | flags + shared + endgame + directed + open_goal + guard + recall | +0.14 [+0.01, +0.26]; −0.18 vs double attackers (recall) | **rejected** |
| `lab5_smart` | flags + shared + endgame + directed + open_goal (the pre-registered selection from the screen) | **validation seeds 181–220: +0.25 [+0.11, +0.40]** over the pool, worst opponent greedy_v2 +0.00, h2h 1.59; food conceded 7.4 → 6.5; 0 crashes / warnings, max move 0.151 s | passed the accept rule (E-025), never promoted: greedy_v4 (built on it) was promoted instead. **pool** since 2026-11-08 (user decision, E-036) |

### `teams/greedy_lab_v6.py`: width-based planner, map modes, formations (E-027–E-029; frozen 2026-11-08)

All entries are lab5_smart (= `lab6_off`, identity 18/18) plus the named switches. Δ = paired points per game vs lab5_smart over the 8-member pool on tuning seeds (E-028: 261–265 pilot, 261–300 screen).

| name | switch(es) | key result | verdict |
|---|---|---|---|
| `lab6_off` | none | 18/18 identical to lab5_smart | **identity** |
| `lab6_plan_full`, `_danger`, `_food`, `_best`, `_g`, `_nohid` | v1 planner (with the dead-successor novelty bug, E-028) in full / danger / food mode, best-first, ghost-bucket atoms, visible ghosts only | pilot (5 seeds): +0.06, +0.25, +0.07, +0.15, +0.24 (33 games), not played | superseded by v2 |
| `lab6_p2_danger` | planner v2, only while a modelled ghost is within 7 | **+0.09 [−0.04, +0.23]** (640 games); choke −0.15, feature −0.12; more returns and kills, more deaths | carried to E-030 as `lab7_danger` |
| `lab6_p2_override` | planner v2 overrides greedy by margin 0.3 | +0.13 [−0.06, +0.32] (300 of 640 games; run stopped early) | carried to E-030 as `lab7_override` |
| `lab6_p2_danger_g`, `_full_g`, `_best_g` | ghost-bucket atoms; full control; best-first | not played (screen stopped early for the fresh-seed confirmation) | `_danger_g` carried to E-030 |
| `lab6_focus_*` (top, bottom, majority, deep, shallow, cluster, far), `lab6_form_lead0/5` | map / sensory food-choice modes; double attack while not leading | E-029 (60 maps, 8,640 games): every focus mode −0.07 … −0.01 vs lab5_smart (all CIs include 0); lead0 −0.76, lead5 −1.05; cross-validated selectors ≤ +0.04 [−0.05, +0.13] | **rejected**: no mode and no per-map selector helps |

### `teams/greedy_lab_v7.py`: v6 + node cap, ablations, shield, hunt, power play, learned leaf value (E-030–)

| name | switch(es) | key result | verdict |
|---|---|---|---|
| `lab7_off` | none | 18/18 identical to lab6_off | **identity** |
| `lab7_danger` | = lab6_p2_danger + 2,000-node cap | 18/18 identical to lab6_p2_danger | E-030 |
| `lab7_danger_net` | danger planner + learned leaf value (12-16-1 MLP of the greedy policy's 30-move value, trained on 450 lab6_off games) | X1 (tuning 401–440) **+0.57 [+0.37, +0.76]** vs lab5_smart, all opponents > 0; **V1 (validation 221–260): +0.95 [+0.78, +1.13] vs greedy_v3, +0.58 [+0.42, +0.74] vs lab5_smart, h2h 2.56 / 2.31**; deaths 0.36 / game (lab5_smart 1.00), returned 17.3 (11.5); X2 +0.50 | **passes the accept rule** (E-031); promotion = user decision |
| `lab7_danger_netf` | = lab7_danger_net with faster leaf code | 24/24 identical games; planner time halved | the version to ship |
| `lab7_danger_g` | ghost-distance-bucket atoms (hand leaf) | X1 +0.24 [+0.02, +0.44] | superseded by the net |
| `lab7_override` | planner overrides greedy by margin | X1 +0.12 [−0.09, +0.31] | not pursued |
| `lab7_danger_d8` | death penalty 8 | identical games to lab7_danger (max backup ignores D) | rejected |
| `lab7_danger_nokill`, `lab7_danger_nocap` | no scared-ghost / capsule rewards | +0.04 / 0.00 vs lab7_danger's +0.06 | ablation: the gain is not kill-farming |
| `lab7_danger_near` | hidden ghosts at the nearest likely cell | +0.03 | rejected |
| `lab7_shield` | planner as veto only | never fires (identical to lab5_smart) | rejected |
| `lab7_hunt` | planner-free scared-ghost chasing | −0.23 [−0.37, −0.11] | rejected |
| `lab7_dplan` | IW(1) defender planner only | X1b +0.19 [+0.03, +0.35] | combined in `lab7_net_dplan` |
| `lab7_power` | SM-3 power play | X1b −0.23 [−0.32, −0.15] | rejected |
| `lab7_net_dplan` / `lab7_netf_dplan` | learned-leaf attacker planner + defender planner (netf = identical fast leaf) | X2 (tuning 441–480) +0.60 [+0.43, +0.77] vs lab5_smart (lab7_danger_net +0.50 on the same games); **V2 (validation 261–300): −0.03 [−0.11, +0.05] vs greedy_v4**, head-to-head 1.69, max move 0.443 s | **rejected** (E-032): pool gain not above 0 |
| `lab7_g_net` | ghost-bucket atoms + net | X2 +0.47 | no gain over the net alone |
| `lab7_net2`, `lab7_net3` | second RL-loop iteration nets (on lab6_off + planner games / planner games only) | X3 (tuning 481–520, complete) −0.04 [−0.12, +0.04] / −0.15 [−0.28, −0.03] vs lab7_danger_netf | not adopted (the first net stays) |
| `lab7_danger_piw`, `_m1m2`, `_both`, `lab7_danger_dplan` | p-IW, two ghost models, two placements, planner + dplan (hand leaf) | not played (X1b stopped) | — |

### `teams/greedy_lab_v8.py`: v7 + non-deep-learning search (E-033; frozen once the screen started)

| name | switch(es) | key result | verdict |
|---|---|---|---|
| `lab8_off` | none | 18/18 identical to lab7_off / lab6_off | **identity** |
| `lab8_v4` | greedy_v4's options | 17/18 identical to greedy_v4; the 18th differs only because the 0.3 s planner clock fired under load (identical with the clock off) | **identity** |
| `lab8_table` | IW planner, 5-D lookup-table leaf (R² 0.453) | E-033: −0.33 [−0.46, −0.21] vs greedy_v4; deaths 0.67, dropped food 3.3 / game | rejected (search exploits the table, T-59) |
| `lab8_lin` | IW planner, linear leaf (R² 0.209) | −0.11 [−0.24, +0.02] | rejected (not better) |
| `lab8_fmc` | flat paired MC, 12 scenarios, H = 20, hand cutoff, margin 0.3 | −0.67 [−0.87, −0.47]; returned 9.6 / game | rejected (timid, T-60) |
| `lab8_fmc_table` | flat paired MC, H = 12, table cutoff | −0.72 [−0.91, −0.53] | rejected |
| `lab8_mcts` | fmc + open-loop UCT (depth 4, 150 iterations) | −0.52 [−0.70, −0.33] | rejected |

### `teams/greedy_lab_v9.py` / `teams/greedy_lab_v10.py`: reserve arms (E-033 parts C, D)

| name | switch(es) | key result | verdict |
|---|---|---|---|
| `lab9_v4_check` | greedy_v4 + flat paired MC re-check of the chosen move (margin 0.3) | −0.43 [−0.61, −0.24] vs greedy_v4 | rejected |
| `lab9_fmc_net` | flat MC, H = 12, learned-net cutoff | −0.72 [−0.93, −0.52] | rejected |
| `lab10_quad` | IW planner + quadratic ridge leaf (non-DL, 91 terms, R² 0.461) | −0.05 [−0.15, +0.05] vs greedy_v4 (720 games), h2h 1.40; deaths 0.38, returned 16.2 | **≈ greedy_v4**: part E (561–600) +0.00 [−0.08, +0.08]; pooled −0.02 [−0.09, +0.04] over 1,440 games; h2h 1.51. Equal, not better: not promoted; fallback if a neural net is ever unwelcome |

### Parameter / target checks around greedy_v4 (E-034; tuning 321–360, paired with greedy_v4)

| name | switch(es) | key result | verdict |
|---|---|---|---|
| `lab7_netf_t5`, `lab7_netf_t9` | planner trigger 5 / 9 (greedy_v4: 7) | −0.04 [−0.11, +0.03] / −0.00 [−0.06, +0.06] | flat: keep 7 |
| `lab11_net60` (`teams/greedy_lab_v11.py`) | leaf net trained on a 60-move target (R² 0.402) | −0.03 [−0.14, +0.08] | rejected (RL-T closed) |
| `lab7_netf_full` | planner decides on every attacker move | −0.38 [−0.56, −0.20]; returned 12.8 / game | rejected: plan only near ghosts |
| `lab7_netf_h40` | planner horizon 40 (greedy_v4: 30) | −0.03 [−0.09, +0.04] | flat: keep 30 |
| `lab7_netf_override` | greedy decides; the net-leaf planner overrides near ghosts by margin 0.3 | +0.03 [−0.05, +0.12] on 321–360; **+0.09 [+0.02, +0.17] on 361–400; pooled +0.06 [+0.00, +0.12]** over 1,440 games, h2h 1.57 | validated as `greedy_v5` in E-038: **rejected** (−0.05 on validation2 1–80) |
| `lab7_netf_min03` | plan_min 0.3 (greedy_v4: 0.05) | +0.01 [−0.05, +0.07] (matches) | flat: keep 0.05 |

### `teams/greedy_v4.py` (E-031, E-032)

| name | what it is | tested in | result | verdict |
|---|---|---|---|---|
| `greedy_v4` | `lab7_danger_netf` as defaults: lab5_smart + IW(1) attacker planner near ghosts with the learned leaf value (identity 18/18) | E-031 (V1), E-032, E-033, E-034, E-035, E-037 | locked test seeds (E-037): **+0.83 [+0.73, +0.94]** over the pool, **+1.02 [+0.85, +1.20]** over the held-out teams vs greedy_v3, 0 / 0 / 0, max move 0.310 s; validation 221–260: **+0.95 [+0.78, +1.13]** vs greedy_v3, +0.58 vs lab5_smart; Linux timing max 0.283 s under load; nothing tested since beats it | **incumbent** (`my_team.py` since 2026-11-08, confirmed by the user), **pool**; release gate passed (E-037) |

### `teams/greedy_v5.py` (E-038)

| name | what it is | tested in | result | verdict |
|---|---|---|---|---|
| `greedy_v5` | greedy_v4 with `plan='override'` as default (= `lab7_netf_override`, identity 8/8) | E-034 (as lab7_netf_override), E-038 (V3) | tuning 321–400: +0.06 [+0.00, +0.12]; **validation2 1–80: −0.05 [−0.15, +0.05]** vs greedy_v4, h2h 1.51 | **rejected** (V3); kept as a league opponent ≈ greedy_v4 strength |

### `teams/greedy_lab_v12.py` / `teams/greedy_lab_v13.py`: proposals from the external review (E-039)

v12 = v11 + default-off options `assist`, `def_scared`, `late_tie`, `plan_blocked`, `ov_guard`, `ov_asym` (header; review in `docs/research/review_v4_v5.md`). v13 = v12 with `def_scared` split into 'posture' | 'cap'. Every arm = greedy_v4 + one switch, screened on tuning 101–140 (`n2_s1`) against greedy_v4, the top 3 (greedy_v5, lab7_netf_dplan, lab10_quad) and the 7 other pool members, paired with greedy_v4.

| name | what it is | tested in | result (Δ vs greedy_v4, 800 paired) | verdict |
|---|---|---|---|---|
| `lab12_assist` | attacker, as a non-scared ghost on our side, intercepts a visible invader within 6 | E-039 screen | +0.00 [−0.07, +0.08]; conceded −0.46 but returned −0.33 per game | promising by the letter of the rule (+1 point) → in the stage-2 combo |
| `lab12_defsc` | scared-defender posture + capsule guard | E-039 screen | **+0.07 [−0.02, +0.15]**; top 3 +0.24 [+0.03, +0.46], pool −0.01 | promising; split in `n2_s2` (option C) |
| `lab12_latetie` | bank late when tied and carrying | E-039 screen | −0.01 [−0.03, +0.00] (changes ≈ 1 % of games) | not promising |
| `lab12_pblock` | standoff breaker allowed to act while the danger planner is on | E-039 screen | +0.00 [−0.10, +0.10]; standoff moves +28, food lost −0.17 | promising by the letter of the rule (+1 point) → in the stage-2 combo |
| `lab12_m1m2` | planner ghost models chase + intercept, 1,200 nodes | E-039 screen | +0.03 [−0.05, +0.11], even across opponents | promising → in the stage-2 combo |
| `lab12_v5fix` | override mode + all-die guard + margin 0.1 when greedy's root value < 0 | E-039 screen | 0.00 [−0.09, +0.09] | not promising; split in `n2_s2` (option C) |
| `lab12_v5guard`, `lab12_v5asym`, `lab13_defsc_posture`, `lab13_defsc_cap` | the option C split parts | E-039 `n2_s2` | running | — |

## Opponents we did not write

| name | what it is | use |
|---|---|---|
| `baseline` | the framework's `baseline_team` (reflex attacker that returns only at ≤ 2 food; reflex defender) | saturated: every recent agent beats it 100%; smoke tests and regression gate only |
| `heldout_a` | **held-out**, written blind by a separate agent: aggressive double attack with capsule use | release gate and rare checkpoints only; never read its code or replays, never tune against it (T-53) |
| `heldout_b` | **held-out**: defence first, permanent guard + cautious raider, turtles when ahead late | same as `heldout_a`; the strongest opponent we have (greedy_v2 scored 0.89 against it, E-015) |
| `submission` | whatever is in `my_team.py` | release gates (E-016) |
| `friend_andy` | a friend's team (`friends/andy/my_team.py`, received 2026-10-23): `OffensiveAgent` + `DefensiveAgent` sharing a belief tracker. Its code is not studied for design and never copied (rule 7) | sparring. E-024: greedy_v3 scored 2.10 PPG against it, 329-62-109 over 500 games. E-035 (diagnostic, tuning 501–510): greedy_v4 2.75 vs greedy_v3 1.95. Not in the reference pool |
| `friend_aljaz_1` … `_5` | a friend's five teams, compiled Cython `.pyd` (Windows x64, Python 3.8 only), received 2026-10-23; not inspected beyond a strings scan | sparring. E-026 (partial): greedy_v3 0.64 PPG vs aljaz_1 (it returns 22.9 food per game), 1.73 vs aljaz_2; aljaz_4/5 untested. E-025: 0.88 vs aljaz_1 on tuning 151–200. E-035 (diagnostic, tuning 501–510, 20 games each): greedy_v4 1.65 / 2.35 / 2.70 / 1.85 / 2.15 vs aljaz_1..5 (greedy_v3 0.80 / 1.35 / 1.35 / 1.05 / 0.85). **Strongest opponent we have** (aljaz_1, aljaz_4). Not in the reference pool |

## Ideas already tested: don't redo them without a new reason

| idea | where | what happened | only worth retesting if … |
|---|---|---|---|
| Hidden-ghost memory in the attacker's safety check | E-007 (`lab_tracker`) | the attacker becomes timid (−0.11) | it is used to choose *where* to attack, not to avoid more |
| Return thresholds 3 / 12, adaptive returns | E-007, E-010, E-011 | within noise; return-at-8 adopted | the attacker changes a lot |
| Dead-end / exit-race checks | E-002, E-018 | deaths halve, points flat | the saved moves get a productive use (another target or entry) |
| Dynamic roles (C1 as one switch) | E-007 | loses head-to-head (0.95) | the parts are tested separately with a safe defence |
| Defender raids (with or without belief recall) | E-018, E-020 | gains against guards = losses against attackers | coordination through shared memory (rules.md Q4, allowed since 2026-10-22) is built |
| Cut-cell squeeze in the defender | E-018 | rarely changes a decision | — |
| Hunting hidden invaders by belief | E-019, E-025 | +0.07, CI includes 0; with exact `is_pacman` (E-025) still −0.006 on top of the fields; a goal-recognition version (`guard`) −0.08 | the defender gets a different way to catch them (e.g. two defenders, SM-8) |
| Attacker comes back on two invaders (`recall`) | E-007 (as part of `roles`), E-025 | −0.58 vs double_attack, −0.40 vs friend_aljaz_1: our returns fall by a third, theirs barely | — (against a double attack, race instead; proposals.md SM-9) |
| Potential-field attacker (F2) | E-008, E-010 | worse than greedy | — |
| Capsule rusher + border camper | E-006, E-007 | 0.00 | — |
| Food-region focus modes (top / bottom / majority half, deep, shallow, cluster, far from ghosts) and a per-map mode selector | E-029 | every mode −0.07 … −0.01 vs lab5_smart; no cross-validated selector beats "no mode" (per-map labels are noise: oracle +0.28, CV ≤ +0.04) | the attacker's food choice changes a lot |
| Both agents attack while behind (`formation` lead0 / lead5), power play on a capsule | E-029, E-030 | −0.76 / −1.05; power play −0.23: the empty home lets the enemy score | the home side can be held by something other than the defender |
| IW planner with a hand-made leaf; `shield` veto; planner-free scared-ghost hunting | E-028, E-030 | hand leaf +0.06 (dies more: max backup over a deterministic model is optimistic); shield never fires; hunting −0.23 | — (use an outcome-trained leaf, M-15) |
| Defender planner (`dplan`) on top of the attacker planner | E-030, E-031, E-032 (V2) | +0.10 on tuning seeds, −0.03 [−0.11, +0.05] on validation 261–300 (wins h2h 1.69 only) | tournament opponents turn out to be planner attackers like ours |
| Second-iteration leaf nets (approximate policy iteration), 60-move leaf target | E-031 (X3), E-034 | −0.04 / −0.15; 60-move target −0.03: better prediction of the target does not give better play | the planner or the policy after it changes |
| Monte-Carlo search: flat paired MC, open-loop UCT, MC re-check of greedy_v4's move, with hand / table / net cutoffs | E-033 | −0.43 … −0.72 vs greedy_v4: the scenario ghost model makes the attacker timid (T-60) | the ghost model is calibrated on real opponent behaviour |
| Lookup-table leaf (5-D, R² ≈ net) | E-033 | −0.33 vs greedy_v4: the search exploits its jumps (T-59); a smooth quadratic leaf with the same R² ≈ greedy_v4 | the table is smoothed (interpolated) |
| Planner on every attacker move (`full`); trigger 5 / 9, horizon 40, plan_min 0.3 | E-034 | full −0.38; the others within ±0.05 of greedy_v4 (flat optimum) | — |

## Open (untested) ideas

The planned queue in experiments.md and [proposals.md](proposals.md) have the details. The main ones:
- weight tuning of F1 (P-16);
- belief-based choice of the attack entry;
- shared-mind team tactics (proposals.md SM-1..SM-13: power play, spotter, decoy, bait-and-trap, play selector);
- TrailMax escape for the "cut off" attacker (heuristics.md H-S20);
- **validation of `lab7_netf_override`** (override mode: pooled +0.06 [+0.00, +0.12] on tuning seeds 321–400, E-034), which needs a fresh validation seed list (user decision);
- reserve ideas from the E-033 review: a race leaf with a fitted τ (proposals MC-2), IW with a scenario re-check of its top nodes, a smoothed (interpolated) table leaf as a direct test of T-59, a ghost model calibrated from replays.

Tested on 2026-10-28 (E-025):
- the hidden-opponent fields (`flags`);
- the shared belief (`shared`);
- the endgame part of roles (`endgame`, P-17c).
