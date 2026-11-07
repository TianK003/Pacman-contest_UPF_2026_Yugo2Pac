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
| [`greedy_v3`](picks/greedy_v3.md) (`teams/greedy_v3.py`) | greedy_v2 + belief-based shadowing defender | H-S01, H-S07, M-04 | E-019 (+0.16 [+0.04, +0.28] vs greedy_v2 on validation seeds); E-021 test seeds +0.26 pool / +0.17 held-out | **since 2026-10-18 (E-021)** |

## Our teams

### `teams/greedy_v1.py`: the first agents (E-002)

| name | what it is | tested in | key result | verdict |
|---|---|---|---|---|
| `greedy` | `GreedyAttacker` (nearest food it reaches before any visible ghost; home at 5 carried, when threatened, out of time) + `PatrolDefender` (chases visible invaders, goes to eaten food, patrols 3 border cells near our food) | E-002, E-005, E-006, E-017 | best of the v1 league (2.23 PPG, 40/40 vs baseline); loses 0–0 standoffs to guards and scoring races to double attackers (E-005) | **past version**, pool |
| `greedy_deadend` | greedy with `DeadEndAttacker`: enters a dead end only if it can get back to the exit before a visible ghost (H-M02 leaf version) | E-002 | Δ −0.01 [−0.10, +0.07] vs greedy | **rejected**. The generalised version (`lab2_exit`) halves deaths but gains no points (E-018) |
| `double_attack` | 2 × `GreedyAttacker`, no defence | E-002, E-006, E-014 | 1.29 PPG in E-002; wins scoring races against greedy | **league** (specialist) |
| `turtle` | 2 × `PatrolDefender`, never attacks | E-002, E-005 | 0.38 PPG; produces 0–0 standoffs | **league** (specialist) |

### `teams/sparring_v1.py`: sparring opponents (E-006)

| name | what it is | tested in | key result | verdict |
|---|---|---|---|---|
| `camper` | greedy attacker + `BorderCamper` (stands on our border cell nearest where the enemy would cross, seen or last seen within 40 plies) | E-006, E-014, E-017 | 1.83 PPG in E-006, beat greedy head-to-head; greedy_v2's hardest old opponent (1.51) | **pool** |
| `camper2` | 2 × `BorderCamper` | E-006 | 0.73 PPG; 0–0 standoffs | **league** |
| `rusher` | `CapsuleRusher` (capsule first, return at 12, hunts scared ghosts) + `PatrolDefender` | E-006, E-014, E-017 | 1.79 PPG in E-006, beat greedy head-to-head | **pool** |
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
| `greedy_v3` | `lab3_shadow` as defaults (24/24 identical) | E-019, E-021 | locked test seeds (E-021): 1.79 PPG vs greedy_v2's 1.55; paired **+0.26 [+0.15, +0.36]** over the pool, **+0.17 [−0.00, +0.33]** over the held-out teams (heldout_b +0.35, heldout_a −0.02), head-to-head 1.56; Linux max move 0.105 s under full load | **incumbent** (`my_team.py` since 2026-10-18) |

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
| `lab5_smart` | flags + shared + endgame + directed + open_goal (the pre-registered selection from the screen) | **validation seeds 181–220: +0.25 [+0.11, +0.40]** over the pool, worst opponent greedy_v2 +0.00, h2h 1.59; food conceded 7.4 → 6.5; 0 crashes / warnings, max move 0.151 s | **passes the accept rule** (E-025); release gate open (Linux timing, test seeds + held-out); promotion = user decision |

### `teams/greedy_lab_v6.py`: width-based planner, map modes, formations (E-027–E-029; frozen 2026-11-08)

All entries are lab5_smart (= `lab6_off`, identity 18/18) plus the named switches. Δ = paired points per game vs lab5_smart over the 8-member pool on tuning seeds (E-028: 261–265 pilot, 261–300 screen).

| name | switch(es) | key result | verdict |
|---|---|---|---|
| `lab6_off` | none | 18/18 identical to lab5_smart | **identity** |
| `lab6_plan_full`, `_danger`, `_food`, `_best`, `_g`, `_nohid` | v1 planner (with the dead-successor novelty bug, E-028) in full / danger / food mode, best-first, ghost-bucket atoms, visible ghosts only | pilot (5 seeds): +0.06, +0.25, +0.07, +0.15, +0.24 (33 games), not played | superseded by v2 |
| `lab6_p2_danger` | planner v2, only while a modelled ghost is within 7 | **+0.09 [−0.04, +0.23]** (640 games); choke −0.15, feature −0.12; more returns and kills, more deaths | carried to E-030 as `lab7_danger` |
| `lab6_p2_override` | planner v2 overrides greedy by margin 0.3 | +0.13 [−0.06, +0.32] (300 of 640 games; run stopped early) | carried to E-030 as `lab7_override` |
| `lab6_p2_danger_g`, `_full_g`, `_best_g` | ghost-bucket atoms; full control; best-first | not played (screen stopped early for the fresh-seed confirmation) | `_danger_g` carried to E-030 |
| `lab6_focus_*` (top, bottom, majority, deep, shallow, cluster, far), `lab6_form_lead0/5` | map / sensory food-choice modes; double attack while not leading | E-029 (mode table) | see E-029 |

### `teams/greedy_lab_v7.py`: v6 + node cap, ablations, shield, hunt, power play, learned leaf value (E-030–)

| name | switch(es) | key result | verdict |
|---|---|---|---|
| `lab7_off` | none | 18/18 identical to lab6_off | **identity** |
| `lab7_danger` | = lab6_p2_danger + 2,000-node cap | 18/18 identical to lab6_p2_danger | E-030 |
| `lab7_override`, `lab7_danger_g`, `lab7_danger_nokill`, `lab7_danger_nocap`, `lab7_danger_d8`, `lab7_danger_near`, `lab7_hunt`, `lab7_shield`, `lab7_danger_net`, `lab7_power` | see league.json notes and E-030 | E-030 | pending |

## Opponents we did not write

| name | what it is | use |
|---|---|---|
| `baseline` | the framework's `baseline_team` (reflex attacker that returns only at ≤ 2 food; reflex defender) | saturated: every recent agent beats it 100%; smoke tests and regression gate only |
| `heldout_a` | **held-out**, written blind by a separate agent: aggressive double attack with capsule use | release gate and rare checkpoints only; never read its code or replays, never tune against it (T-53) |
| `heldout_b` | **held-out**: defence first, permanent guard + cautious raider, turtles when ahead late | same as `heldout_a`; the strongest opponent we have (greedy_v2 scored 0.89 against it, E-015) |
| `submission` | whatever is in `my_team.py` | release gates (E-016) |
| `friend_andy` | a friend's team (`friends/andy/my_team.py`, received 2026-10-23): `OffensiveAgent` + `DefensiveAgent` sharing a belief tracker. Its code is not studied for design and never copied (rule 7) | sparring. E-024: greedy_v3 scored 2.10 PPG against it, 329-62-109 over 500 games. Not in the reference pool |
| `friend_aljaz_1` … `_5` | a friend's five teams, compiled Cython `.pyd` (Windows x64, Python 3.8 only), received 2026-10-23; not inspected beyond a strings scan | sparring. E-026 (partial): greedy_v3 0.64 PPG vs aljaz_1 (it returns 22.9 food per game), 1.73 vs aljaz_2; aljaz_4/5 untested. E-025: 0.88 vs aljaz_1 on tuning 151–200. **Strongest opponent we have**. Not in the reference pool |

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

## Open (untested) ideas

The planned queue in experiments.md and [proposals.md](proposals.md) have the details. The main ones:
- weight tuning of F1 (P-16);
- belief-based choice of the attack entry;
- shared-mind team tactics (proposals.md SM-1..SM-13: power play, spotter, decoy, bait-and-trap, play selector);
- TrailMax escape for the "cut off" attacker (heuristics.md H-S20).

Tested on 2026-10-28 (E-025):
- the hidden-opponent fields (`flags`);
- the shared belief (`shared`);
- the endgame part of roles (`endgame`, P-17c).
