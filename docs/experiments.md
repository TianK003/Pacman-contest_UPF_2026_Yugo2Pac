# Experiment log

This is the log book of everything tried and tested, including failures and aborted runs. Append new entries at the bottom with increasing `E-###` IDs, and never delete old ones. If a result turns out wrong, add a correction entry that references the old one.

Reference heuristics, methods and traps by ID (`H-M02`, `M-03`, `T-11`). When an experiment changes a status in heuristics.md or methods.md, update that file and cite the experiment ID there.

## Template

```markdown
## E-### — <short title> (YYYY-MM-DD)
- Status: planned | running | done | aborted
- Question / hypothesis:
- Variant(s): <my_team.py git commit or branch>, <heuristic/method IDs>, <parameters>
- Setup: opponents; layouts/seeds; games per colour; flags (always -c); OS/machine; Python; framework commit
- Results: per opponent W/T/L, avg score, crashes, time warnings, max move time
- Conclusion: (what we now believe, with the uncertainty)
- Follow-ups:
```

## Planned queue

Proposed 2026-10-16 from the E-002 findings and extended 2026-10-17 (E-005). Each candidate changes **one** thing compared with `teams/greedy_v1.py`, so its effect can be attributed. Status and results are in the entries cited.

| ID | Agent / experiment | Question | Heuristics | Status |
|---|---|---|---|---|
| P-01 | `baseline_plus` (league opponent) | the baseline attacker plus a return threshold: a stronger simple opponent, since the baseline is saturated | — | built, `teams/sparring_v1.py` (E-006) |
| P-02 | `camper`, `camper2` (league opponents) | a defender that guards the border where our attacker would cross. Can our attacker get past it? | H-S07 | built (E-006): greedy gets 1.10 / 1.80 points per game against them |
| P-03 | `rusher` (league opponent) | an attacker that eats the capsule first and then harvests. Does our defender cope with a scared window? | H-S06 | built (E-006): greedy gets 0.90 against it |
| P-04 | `lab_adaptive` (C5) | carry more when no defender has been seen recently, bank early when one has | H-S04, H-S11 | tested (E-007, E-010, E-011): no gain alone; with the breaker +0.18 (tuning) / +0.24 (validation), below return-at-8 |
| P-05 | `lab_roles` (C1): call back the attacker on 2 invaders | if 2 invaders are detected on our side, the attacker turns back to defend | H-S08 (basic) | tested as part of `lab_roles` (E-007): +0.12 vs the pool but **0.95 head-to-head vs greedy**; not adopted |
| P-06 | `lab_roles` (C1): endgame / score control | leading late → both defend; behind late → both attack | H-S05 | tested as part of `lab_roles` (E-007); not adopted (see P-05) |
| P-07 | `RETURN_AT` sweep {3, 5, 8, 12} on **tuning** seeds, then confirm the best on validation | first use of the tuning/validation split | H-S04, M-02 | tested (E-007, E-010): alone within noise; **return-at-8 with the breaker is in greedy_v2** |
| P-08 | `lab_intercept` (C4): defender interception | go to the cell on the invader's way home that we reach first, instead of chasing it directly | H-S07, H-S03 | tested: alone +0.01 (E-007); with the breaker +0.17 (E-010); **in greedy_v2** |
| P-09 | `lab_breaker` (C2): standoff breaker | after being blocked at the border, take a capsule or switch to the entry farthest from the ghosts | H-S12, H-M06 | **tested and validated**: +0.13 (tuning, E-010), +0.26 (validation, E-011); **in greedy_v2** |
| P-10 | `lab_tracker` (C3): possible-position tracking | does remembering hidden ghosts reduce deaths and loops without making the attacker timid? | H-S01, H-S02 | tested: −0.11 alone (timid, E-007), neutral with the breaker (E-010); not adopted |
| P-11 | `feature` (F1): weighted-feature attacker | is the M-02 family viable before tuning? | M-02 | tested: +0.07 [−0.08, +0.20] on 40 tuning seeds (E-010); next: weight tuning (P-16) |
| P-12 | `field` (F2): potential-field attacker | is the potential-field family viable before tuning? | M-14 | tested: −0.04, loses head-to-head to greedy (E-010); rejected for now |
| P-13 | `rusher_camper`: capsule-first attacker + border camper | both parts beat greedy head-to-head in E-006; together? | H-S06, H-S07 | tested: +0.00 (E-007); dropped |
| P-14 | Validation of the screen's winners and a combined `greedy_v2` | accept rule on validation seeds 21+ (T-50) | — | **done**: `greedy_v2` (breaker + intercept + return 8) passes the accept rule, +0.42 on validation seeds 21–60 and 61–100 (E-011, E-012) |
| P-15 | Promote `greedy_v2` to `my_team.py` | user decision; then the release gate: Linux / Python 3.8 timing, ≥ 200 own games, one locked test-seed run | — | **promoted 2026-10-18 (E-013)**; release gate open |
| P-16 | Offline weight tuning of F1 (`feature`) | random search / CMA-ES on tuning seeds, now cheap (E-009); can a tuned F1 beat greedy_v2? | M-02 | planned |
| P-17 | Split `roles` into its three parts | call back on 2 invaders / defender attacks when unopposed / endgame, each screened on top of greedy_v2 | H-S08, H-S05 | planned |
| P-18 | New league members from greedy_v2's weaknesses | an exploiter written against greedy_v2 (evaluation.md section 5); a held-out opponent written by a teammate | — | **built (E-015)**: `choke`, `exploit_v2` (teams/sparring_v2.py); held-out `heldout_a`, `heldout_b` (eval/heldout/, written blind by a separate agent). A teammate-written held-out team is still open |
| P-19 | C1: exit-race check for greedy_v2's attacker | E-014: most deaths are dead-end traps the killer could close; does refusing such food help? | H-M02, H-S03 | **tested (E-018)**: halves deaths but +0.02 [−0.06, +0.10]; not adopted |
| P-20 | Defender that closes in on trapped invaders (cut cells, H-M03 squeeze) | E-014: defence = 29% of lost points; the defender holds but never closes in | H-S07, H-M03 | **tested (E-018)**: +0.02 [−0.01, +0.06], rarely changes a decision; not adopted |
| P-21 | C3: two-entry attack when a standoff persists | E-014: 0–0 standoffs still cost 18% | H-S12, H-S09 | **tested (E-018)** as a raiding defender without shared memory: −0.07 [−0.14, +0.01]; not adopted |
| P-22 | Defender hunts hidden invaders from an exact belief (sonar + sight + food events) | E-014: defence = 29% of lost points; greedy_v2's defender ignores the sonar | H-S01, H-S07, M-04 | tested (E-019): +0.07 [−0.02, +0.17] alone, nothing on top of P-23; not adopted |
| P-23 | Idle defender shadows the raider's likely crossing instead of patrolling | as P-22 | H-S01, H-S07 | **adopted**: accepted in E-019 (validation 101–180 +0.16 [+0.04, +0.28]); test seeds +0.26 pool / +0.17 held-out (E-021); **in my_team.py as greedy_v3** |
| P-24 | Raiding defender (P-21) that the belief calls back while the raider is near our side | E-018: the plain raid scored more against guards but let attackers in | H-S12, H-S09, H-S01 | tested (E-020): −0.01 [−0.06, +0.04] on top of P-23; not adopted |

---

## E-000 — Environment and engine fact checks (2026-10-16)
- **Status**: done
- **Question**: what can an agent actually observe and share, and how does the engine behave on this machine?
- **Variants**:
  - A throwaway probe agent: baseline behaviour plus logging, not kept in the repo.
  - A script that builds `GameState` objects directly.
- **Setup**: Windows 11, venv Python 3.8.10, framework commit `54cd83c`, `-q -c`.
- **Results**:
  - **Games**:
    - Probe vs `baseline_team` on `RANDOM13`: tie 0–0, ~41 s wall time.
    - Probe vs probe, 2 games (`-n 2`) on `RANDOM7`: 28 (red win) and 0 (tie), ~78 s in total.
  - **Shared memory**: a module-level dict was shared by teammates (agents 0 and 2 had the same object). The red and blue copies of the same file got separate modules. The same objects persisted across `-n` games.
  - **Startup state**: opponent positions are visible in `register_initial_state`; they are just the public start positions.
  - **Hidden opponents**: their `is_pacman`, `num_carrying` and `scared_timer` remain readable. Private `data._food_eaten` is set in observations. Score and `data.timeleft` are visible.
  - **Shared objects**: the observation shares the layout/walls object and the `Configuration` objects with the real state, and an in-place `pos` mutation through the observation changed the real state (→ T-01).
  - **Scared timer**: it decrements only for the moving agent (40 → 39 for agent 0, the others still 40).
  - **Random maps** (seeds 1–200): always 34×18, with 60 food and 4 capsules. Prison layers over seeds 1–400: 0 layers 79, 1 layer 184, 2 layers 87, 3 layers 50.
  - **Global RNG**: its state after generating `RANDOM13` is the same regardless of the prior seed.
- **Conclusion**: the facts recorded in framework.md and traps.md (T-01, T-02, T-26, T-28, T-33, T-36) hold for commit `54cd83c`. One baseline-level game takes ~40 s on this machine.
- **Follow-ups**:
  - Measure the cost of `generate_successor` and of our own forward model (needed for M-05/M-06).
  - Build the batch harness (done, E-001).

## E-001 — Evaluation tooling validation (2026-10-16)
- **Status**: done
- **Question**: do `eval/check_rules.py` and `eval/sentinel_team.py` catch the violations listed in traps.md section A, without false positives on legitimate teams? Does `eval/evaluate.py` run end to end?
- **Variants**:
  - A deliberately cheating test team (scratchpad only, not in the repo), derived from the baseline. It includes a `threading` import, `random.seed(1)`, `data._food_eaten`, an item write into `get_walls()`, a write to `Configuration.direction`, a broad `except Exception`, and an overridden `observation_function`.
  - `teams/greedy_v1.py` and `baseline_team` as clean controls.
- **Setup**: Windows 11, Python 3.8.10, framework `54cd83c`, 40–60-move games with `-q -c`.
- **Results**:
  - **Static lint**: flagged 7/7 planted violations. 0 errors on `greedy_v1.py` and `my_team.py`; only `eval()` warnings in the baseline-derived `my_team.py`.
  - **Runtime sentinel**:
    - It flagged all 4 runtime violations that really happened: `observation_function` overridden, global `random.seed` called, walls mutated (an open cell set to wall), and shared `Configuration` mutated (direction changed in place).
    - Writes that don't change a value (e.g. writing `True` into a cell that was already a wall) are correctly *not* flagged.
    - **Bug found and fixed**: walls were first compared against a snapshot from the start of the game, so a mutation was also blamed on the teammate. Snapshots are now taken per call, which gives correct attribution.
  - **Pilot round robin** (`pilot` run): baseline, greedy, greedy_deadend, double_attack and turtle, on 1 validation seed with both colours. 20 games in 95 s with 10 workers. 0 crashes, 0 warnings, 0 violations, max move time 0.109 s.
- **Conclusion**: the tooling works for the planted cases. It is a tripwire, not a proof: the lint can't see every aliasing path, and the sentinel only checks walls, visible `Configuration` objects, the global RNG, threads, subprocesses and file writes.
- **Follow-ups**: E-002 (full round robin). Later: SPRT, behavioural diagnostics.

## E-002 — Round robin of the v1 league (2026-10-16)
- **Status**: done, in two parts.
  - **Part 1**: 160/400 games with 10 workers. It was stopped when Claude Code reaped the background shell because the *system* was low on memory, not because of an agent failure. The 10 orphaned game processes were stopped. 10 turtle-vs-baseline games were cut off after 5–20 s, with no score file and no traceback, crash or warning; they are excluded from the stats.
  - **Part 2**: the 250 missing games were resumed with `--resume --jobs 6`, while the user was freeing memory.
- **Question**: how do the first non-trivial agents compare with the baseline and with each other?
- **Variants** (all from `teams/greedy_v1.py`, via `eval/league.json`):
  - `greedy`: `GreedyAttacker` + `PatrolDefender`. These are the defaults.
  - `greedy_deadend`: `DeadEndAttacker` + `PatrolDefender`.
  - `double_attack`: 2× `GreedyAttacker`.
  - `turtle`: 2× `PatrolDefender`.
  - `baseline`: the framework's `baseline_team`.
- **Setup**: validation seeds 1–20, both colours, `-q -c`, sentinel on every team, 10 workers, Windows 11, Python 3.8.10, framework `54cd83c`. Run `rr_v1` (`eval/results/rr_v1.jsonl`).
- **Results**: 400 scored games (10 pairings × 20 seeds × 2 colours). Summary in `eval/results/rr_v1_summary.md`.

  | agent | games | W-T-L | PPG [95% CI] | win % [exact CI] |
  |---|---|---|---|---|
  | greedy | 160 | 110-26-24 | 2.23 [2.08, 2.38] | 69 [61, 76] |
  | greedy_deadend | 160 | 109-24-27 | 2.19 [2.06, 2.33] | 68 [60, 75] |
  | double_attack | 160 | 63-17-80 | 1.29 [1.03, 1.56] | 39 [32, 47] |
  | baseline | 160 | 35-39-86 | 0.90 [0.79, 1.00] | 22 [16, 29] |
  | turtle | 160 | 0-60-100 | 0.38 [0.26, 0.50] | 0 [0, 2] |

  **Head-to-head PPG** (row vs column):

  | | baseline | double_attack | greedy | greedy_deadend | turtle |
  |---|---|---|---|---|---|
  | baseline | – | 2.50 | 0.00 | 0.00 | 1.10 |
  | double_attack | 0.47 | – | 0.95 | 1.02 | 2.70 |
  | greedy | 3.00 | 1.93 | – | 1.43 | 2.55 |
  | greedy_deadend | 3.00 | 1.85 | 1.27 | – | 2.65 |
  | turtle | 0.95 | 0.15 | 0.23 | 0.17 | – |

  - **Approximate Nash averaging**: greedy carries weight 0.99. Payoffs: greedy_deadend −0.15, double_attack −0.97, turtle −2.33, baseline −3.00.
  - **Paired `greedy − greedy_deadend`** (over shared opponents): −0.01 [−0.10, +0.07]. Per opponent:
    - baseline +0.00
    - double_attack +0.07 [0.00, +0.23]
    - turtle −0.10 [−0.30, 0.00]
  - **Gates**: 0 crashes/forfeits, 0 engine time warnings and 0 sentinel violations in all 400 games. Max startup 1.59 s.
  - **Timing anomaly**:
    - Part 1 had no move > 0.2 s (max 0.154 s).
    - Part 2 had 31 agent-games with a move > 0.2 s. The worst was 0.951 s (turtle), and greedy reached 0.448 s. p95 stayed ≤ 0.035 s.
    - Part 2 wall time per game also rose from 40 s to 52 s on average, with some games taking 80–108 s.
    - The spikes hit every team, including the trivial `PatrolDefender`, and only during the period of memory pressure. So they are most likely caused by the environment (paging or CPU contention), not by our code. This is not proven. See T-49.
- **Conclusions**:
  - **greedy is the best of this pool** and beats every other member head-to-head.
  - **The baseline is saturated**: 40/40 for both greedy variants. It is now only a regression gate.
  - **Dead-end awareness (H-M02, leaf-pruning version) makes no measurable difference** (paired −0.01 [−0.10, +0.07], within δ), and greedy edges it head-to-head (1.43 vs 1.27). Keep the simpler greedy.
  - **Correction of an earlier claim**: the single pilot seed suggested that turtle ties greedy. With 20 seeds, greedy beats turtle at 2.55 PPG. Lesson: one seed proves nothing.
  - **Measured weakness**: **against an opponent with no defence (double_attack), greedy scores *worse* than the baseline** (paired −0.57 [−1.12, −0.07]). The probable cause, a hypothesis not yet tested:
    - Our single defender can't stop two attackers.
    - Our attacker returns every 5 food, while the baseline's attacker carries everything in one uncontested trip.
- **Follow-ups**: see the planned queue (P-01 … P-08).

## E-003 — Promote `greedy` (teams/greedy_v1.py defaults) to my_team.py (2026-10-16)
- **Status**: done. This is a **provisional** promotion by the user's decision ("for now make it the top team"), not a full pass of the accept rule.
- **Basis (the parts of the rule that hold, evaluation.md section 2)**:
  - Gates: lint OK; 0 crashes, warnings and violations in E-002.
  - Head-to-head against the previous incumbent (`my_team.py` was the baseline): 40-0-0, PPG 3.00 ≥ 1.5.
- **Change**: `my_team.py` is now `teams/greedy_v1.py` with a different header comment only (the body was checked with `diff`). Smoke test: it loads from the repo root and beat the baseline in a 120-move game. League entry `submission` added.
- **Accept-rule re-check after E-002 completed** (greedy vs the previous incumbent, the baseline):

  | Rule | Result |
  |---|---|
  | 1. Gates | ✓ 0 crashes, warnings and violations. Max move time 0.448 s ≤ 0.5 s budget, but see the E-002 timing anomaly |
  | 2. Pool improvement | ✓ paired +0.77 [+0.57, +0.95]. **However**, this is 20 seed-pairs per opponent, not the required 40 |
  | 3. No regression > δ = 0.5 | ✓ by the letter: vs double_attack −0.57 [−1.12, −0.07], and the upper bound −0.07 > −0.5. It is still a significant regression against that opponent (CI entirely below 0) |
  | 4. Head-to-head ≥ 1.5 | ✓ 3.00 |
  | 5. Confirmation on unused seeds | ✗ not done |

- **Verdict**: the promotion is justified on the evidence so far, but **not yet confirmed**. Open items: 40 seed-pairs, confirmation seeds, Linux timing, and the double_attack weakness.

## E-004 — How reliable is the evaluation? (2026-10-16)
- **Status**: done
- **Question**: are the paired design and the CIs in `eval/evaluate.py` trustworthy at our sample sizes?
- **Setup**: E-002 data at 229 scored games, plus two extra runs of greedy vs baseline on `RANDOM97464282` (400 moves each, `--record`). A simulation of the seed-bootstrap CI: 400 synthetic runs of 20 seeds × 2 games, with map-level correlation and 1000 bootstrap resamples each.
- **Results**:
  - **Determinism**: the two runs had identical 400-move sequences.
  - **Split-half** (seeds 1–10 vs 11–20):
    - greedy–baseline 3.00 / 3.00
    - turtle–baseline 0.95 / 0.95
    - double_attack–baseline 0.60 / 0.35
    - greedy–double_attack 2.05 / 2.14
    - greedy–greedy_deadend 1.35 / 1.50
  - **Bootstrap 95% CI coverage**: 93.5% (true PPG 1.60), 92.8% (2.60), **73.2% (2.93)**.
- **Conclusions**:
  - Common random numbers hold exactly, so repeats are worthless and seeds are the unit.
  - CIs are roughly right in the middle of the range but too narrow at 20 seeds, and badly overconfident near the ceiling or floor.
  - Added an exact Clopper–Pearson win-rate CI to the summary (40/40 → win rate ≥ 91.2%).
  - Assessment written up in evaluation.md section 9.
- **Follow-ups**: use ≥ 40 seeds for decisions; implement SPRT; behavioural diagnostics.

## E-005 — Where greedy loses points, and why it ties turtle (2026-10-17)
- **Status**: done
- **Question**: which games cost `greedy` points in E-002, and what does its attacker do in the 0–0 games against `turtle`?
- **Variants**:
  - Re-analysis of the E-002 records (`eval/results/rr_v1.jsonl`), final scores only.
  - A scratch probe, not in the repo: a subclass of `GreedyAttacker` that only counts per-move statistics, plus `PatrolDefender`. Its behaviour is unchanged: all 5 scores reproduced E-002 exactly.
- **Setup**: probe (red) vs `turtle` (blue; `greedy_v1.py` with `first=PatrolDefender`). Seeds 97464282, 41952914 and 88617764 (ties in E-002); 86220279 and 32129042 (wins by +23 and +20). 1 game each, `-q -c`. Windows 11, Python 3.8.10, repo `c058ffe`, framework `54cd83c`.
- **Results**:
  - **E-002 score distribution for greedy**:
    - 15 of 160 games ended by the 28-food rule (the sentinel counted fewer than 300 moves per agent); the rest went to the time limit.
    - The team that is ahead at the end is the one that reached 28. Greedy reached it first in 7 games (2 vs baseline, 5 vs double_attack), and double_attack in 8. So **8 of greedy's 11 losses to double_attack were scoring races that double_attack won**.
    - Against the baseline the margins were +6 to +28 (median ≈ +20).
    - vs turtle: 31-9-0. All 9 ties were 0–0, and on 4 seeds both colours tied.
    - vs greedy_deadend (mirror): 15-12-13, with 12 ties at 0–0.
    - vs double_attack: 24-5-11.
  - **Probe (attacker, 300 moves each)**:

    | seed | result | moves as Pacman | moves on home border column | moves with a dangerous ghost visible | max carried | moves at the start cell after move 1 (≈ deaths) |
    |---|---|---|---|---|---|---|
    | 97464282 | tie | 1 | 261 | 261 | 0 | 0 |
    | 41952914 | tie | 7 | 11 | 126 | 1 | 1 |
    | 88617764 | tie | 31 | 10 | 40 | 1 | 5 |
    | 86220279 | +23 | 208 | 26 | 140 | 6 | 1 |
    | 32129042 | +20 | 180 | 22 | 166 | 5 | 2 |

    The probe's "returns" counter also counted deaths, so it is not reported.
- **Conclusions** (3 tie seeds: anecdotal, not a rate):
  - At least two distinct failure modes cause the ties:
    - (a) **Border standoff** (H-S12): on 97464282 the attacker stood on our border column for 261/300 moves with a defender in view and crossed once. The race-safe BFS never finds safe food, so it waits.
    - (b) **Death loop**: on 88617764 it died about 5 times and never carried more than 1. The safety check only sees *visible* ghosts, and on a prison map every death costs many moves.
  - 41952914 is not diagnosed: only 7 moves as a Pacman, 1 death and few moves on the border column. It needs a replay. (Diagnosed later in E-007: a sight-flicker loop on our own side.)
  - Greedy's points are lost (i) to 0–0 ties against real defenders (turtle, mirror) and (ii) to scoring races against two attackers, which collect 28 before we do. Greedy itself cleared 28 in only 7/160 games.
- **Follow-ups**:
  - A standoff breaker (H-S12, H-M06), ghost memory / set tracking (H-S01), and dynamic roles (H-S08).
  - Behavioural diagnostics in the sentinel: deaths, moves as a Pacman, standoff moves, food carried and returned.
  - A border-camper league opponent (P-02), so that these failure modes are measured.

## E-006 — A pool that tells agents apart: four sparring teams (2026-10-17)
- **Status**: done
- **Question**: do the new sparring teams (P-01..P-03) stop greedy from scoring near 3.0 points per game, and what does the extended pool look like?
- **Variants**:
  - New file `teams/sparring_v1.py`: a verbatim copy of the greedy_v1 machinery plus three opponent styles.
    - `camper`: GreedyAttacker + `BorderCamper`, a defender that stands on our border cell nearest to where the enemy (seen, or last seen within 40 plies) would cross.
    - `camper2`: two BorderCampers that never attack.
    - `rusher`: `CapsuleRusher` (capsule first, then a return threshold of 12 and hunting scared ghosts during the window) + PatrolDefender.
    - `baseline_plus`: baseline-style reflex agents with return-at-5 and a ghost-distance penalty.
  - Old members: greedy, baseline, double_attack, turtle.
- **Setup**:
  - Full round robin of the 8 teams on **tuning** seeds 1–10, both colours, 560 games.
  - `-q -c`, sentinel with the new behaviour diagnostics, 8 workers.
  - Windows 11, Python 3.8.10, framework `54cd83c`, repo `c058ffe` plus uncommitted changes (new files).
  - Run `scr1`. Regenerate with `evaluate.py summary --run scr1 --agents greedy baseline double_attack turtle camper camper2 rusher baseline_plus`.
  - Smoke test first (`smoke_sparring`, 16 games): clean.
- **Results**: 0 crashes, 0 time warnings, 0 violations. Max move 0.205 s (the baseline); our files ≤ 0.125 s.

  | agent | W-T-L | PPG [95% CI] | Nash weight |
  |---|---|---|---|
  | camper | 62-70-8 | 1.83 [1.57, 2.11] | 0.99 |
  | greedy | 63-63-14 | 1.80 [1.64, 1.96] | 0.00 (payoff −0.15) |
  | rusher | 59-73-8 | 1.79 [1.51, 2.06] | 0.01 (payoff −0.15) |
  | double_attack | 54-53-33 | 1.54 [1.27, 1.82] | 0 |
  | baseline_plus | 27-52-61 | 0.95 [0.76, 1.18] | 0 |
  | baseline | 23-46-71 | 0.82 [0.66, 1.04] | 0 |
  | camper2 | 0-102-38 | 0.73 [0.54, 0.90] | 0 |
  | turtle | 0-85-55 | 0.61 [0.46, 0.76] | 0 |

  - **Greedy's PPG against each opponent** (20 games each): baseline 2.85, baseline_plus 2.30, turtle 2.30, camper2 1.80, double_attack 1.35, camper 1.10, rusher 0.90.
  - **Head-to-head against greedy**: camper 1.25 vs greedy's 1.10; rusher 1.35 vs greedy's 0.90.
  - **Ties dominate**: 272 of 560 games were ties, 63 of greedy's 140.
  - **Greedy barely attacks a real guard**: against camper, camper2 and rusher its team spent only 21–31 moves per game as a Pacman (182 against the baseline), and it returned 2.4–3.2 food per game.
- **Conclusions** (10 seeds, 20 games per pair: per-pair CIs are about ±0.4–0.6):
  - The pool now discriminates. The baseline is near-saturated (greedy 2.85), but three new members hold greedy to ≤ 1.1.
  - **Greedy is no longer the best team in the pool.** The two sparring teams that swap one of its parts beat it head-to-head. These are tuning-seed results, i.e. hypotheses, not accept decisions.
    - The BorderCamper as defender (camper).
    - The CapsuleRusher as attacker (rusher).
    - Both parts together became the candidate `rusher_camper` in E-007.
  - Against any real guard the game becomes a 0–0 standoff (E-005 at scale). Breaking it is worth up to +2 points per tie converted.
- **Follow-ups**: E-007 screens the candidates against this pool.

## E-007 — Candidate improvements to greedy: build, identity check, screen (2026-10-17)
- **Status**: done (screen). It was stopped once by Claude Code for low *system* memory at 194/1,920 games (no agent failure; 2 cut-off games replayed). It was resumed with `--jobs 6` and, after E-009, without the engine's per-move sleep: the remaining 1,715 games took 8 minutes.
- **Question**: which single change to greedy_v1 raises points per game against the E-006 pool?
- **Variants**: new file `teams/greedy_lab_v1.py`, greedy_v1 plus switches (league entries `lab_*`).
  - `roles` (C1, H-S08/H-S05): both agents can play either role.
    - The attacker defends while two invaders are evident (seen, or our food vanishing away from every visible invader).
    - The defender attacks after 25 own moves without invader evidence, and returns on the first evidence.
    - In the last 40 own moves, a lead makes both defend and a deficit makes both attack.
    - Each agent decides from its own observation; nothing is shared (Q4).
  - `breaker` (C2, H-S12/H-M06): when on our side with no safe food because a ghost blocks us, for 3 of the last 12 moves, it does one of two things:
    - takes a capsule it reaches first;
    - otherwise commits to walking (on our side) to the border entry farthest from the ghosts.
  - `tracker` (C3, H-S01 set version): it keeps the set of cells each hidden enemy can occupy (grown by one step per enemy move, minus cells in sight, minus cells the sonar rules out, and pinned by food events). A hidden, non-scared ghost whose set has ≤ 20 cells counts in the attacker's race-safety.
  - `intercept` (C4, H-S07): the defender does one of three things:
    - catches an invader within 2;
    - holds the exit of the dead end the invader is in (and walks in once it stands between the invader and the exit);
    - otherwise goes to the first cell on the invader's shortest way home that it reaches no later.
  - `return_at` (C5 sweep: 3, 8, 12; greedy uses 5) and `adaptive` (C5, H-S04):
    - threshold 3 if a ghost was seen in the last 5 own moves, 10 after 15 quiet moves;
    - bank ≥ 2 food when home is ≤ 2 away.
  - Also screened:
    - `lab_breaker_tracker` (C2 + C3);
    - `rusher_camper` (sparring_v1: CapsuleRusher + BorderCamper, from E-006);
    - the two families of E-008.
- **Checks before the screen**:
  - **Identity**: `lab_off` (every switch off) against baseline, turtle and camper on tuning seeds 1–3, both colours. **18/18 games identical to greedy**, score and every diagnostic counter. Repeated after each later edit of the file: 18/18 both times (runs `identity_lab`, `identity_lab2`, `identity_lab3`).
  - **Smoke** (`smoke_lab`, 1 seed against baseline and camper): no crash, max move 0.08 s, and every switch changes play in some games.
- **Debugging the breaker on validation maps** (see T-50). The first version did not break any standoff on the E-005 tie maps against turtle. Two traces showed why:
  1. It ranked entries by race lead (ghost distance − our distance). Against guards standing opposite, every lead is ≤ 0, so the nearest entry won and the attacker shuffled between the entries next to the ghosts. **Fix**: go to the entry farthest from the ghosts.
  2. Once the ghosts dropped out of sight, all food looked safe again, and greedy walked straight back towards them. This is the same sight-flicker loop that caused the undiagnosed E-005 tie: greedy spent moves 118–299 of seed 41952914 cycling (12,4)→(11,4)→(11,3)→(11,4) on our own side. **Fix**: commit to the chosen entry until arrival, and count blocked moves in a 12-move window (the loop is blocked only every other move).
  - After the fixes, greedy (red) vs turtle on these validation maps:
    - `breaker`: 3 of the 5 ties became wins (97464282 +14, 83876527 +14, 60969636 +14);
    - `breaker+tracker`: 4 of the 5 (88617764 +14 as well).
  - **Validation seeds 1–20 (all of E-002's) are therefore spent for this design round**. Accept decisions use `--seed-offset 20`.
- **Setup of the screen**:
  - 12 candidates × 8 pool teams on **tuning** seeds 1–10, both colours: 1,920 games.
  - Appended to run `scr1` (`--resume`), so every candidate pairs with greedy's E-006 games on the same seeds.
  - 10 workers, Windows 11, Python 3.8.10, framework `54cd83c`.
- **Results** (run `scr1`, tuning seeds 1–10). Each candidate is paired with greedy over the same 140 games against the 7 other pool teams. 0 crashes, 0 time warnings, 0 violations for every candidate; max move ≤ 0.097 s.

  | candidate | paired Δ vs greedy [95% CI] | worst opponent Δ [CI] | best opponent Δ | head-to-head vs greedy (W-T-L) |
  |---|---|---|---|---|
  | `lab_breaker` | **+0.45 [+0.21, +0.73]** | baseline +0.00 | camper +0.80 | 1.50 (7-9-4) |
  | `feature` (E-008) | **+0.44 [+0.11, +0.81]** | rusher +0.15 [−0.50, +0.85] | double_attack +1.15 | 1.25 (6-7-7) |
  | `lab_breaker_tracker` | **+0.38 [+0.04, +0.71]** | baseline +0.00 | camper2 +0.60 | 1.85 (10-7-3) |
  | `field` (E-008) | **+0.34 [+0.04, +0.69]** | turtle −0.20 [−0.80, +0.40] | double_attack +0.90 | 1.80 (10-6-4) |
  | `lab_roles` | +0.12 [+0.00, +0.23] | camper −0.45 [−1.00, +0.15] | baseline_plus +0.50 | **0.95 (3-10-7)** |
  | `lab_ret8` | +0.11 [−0.01, +0.30] | turtle −0.10 | double_attack +0.60 | 1.30 (4-14-2) |
  | `lab_ret12` | +0.11 [−0.10, +0.36] | turtle −0.20 | double_attack +0.40 | 1.15 (3-14-3) |
  | `lab_adaptive` | +0.05 [−0.06, +0.18] | baseline_plus −0.35 | double_attack +0.70 | 1.30 (4-14-2) |
  | `lab_intercept` | +0.01 [+0.00, +0.04] | baseline +0.00 | camper +0.10 | 1.15 (3-14-3) |
  | `lab_ret3` | +0.01 [−0.11, +0.14] | baseline_plus −0.35 | double_attack +0.25 | 1.15 (3-14-3) |
  | `rusher_camper` | +0.00 [−0.26, +0.33] | turtle −0.40 [−0.70, −0.10] | rusher +0.55 | 1.25 (4-13-3) |
  | `lab_tracker` | −0.11 [−0.29, +0.02] | turtle −0.40 [−0.70, −0.10] | rusher +0.05 | 1.10 (2-16-2) |

  - **Diagnostics of the breaker (its target signal)**: against the guards, the team's moves as a Pacman roughly triple (camper 31 → 105, camper2 27 → 94, rusher 21 → 95, turtle 58 → 106), and so does food returned (camper 3.1 → 8.3, camper2 3.2 → 8.2, rusher 2.4 → 8.0). The price is more deaths (camper 0.35 → 1.05 per game) and more food lost (1.3 → 3.9).
  - **Tracker alone**: fewer Pacman moves and more ties against turtle (−0.40). Remembering hidden ghosts makes the attacker more timid, as feared. Combined with the breaker it is about as good as the breaker alone, with fewer deaths against the baseline (0.30 vs 0.60).
  - **Roles**: see the partial result above; it fails the head-to-head rule.
  - **Return threshold**: neither the sweep nor the adaptive rule moves the total beyond noise. Higher thresholds help against double_attack (+0.40 to +0.70) and cost a little against two-defender teams.
  - **Intercept**: practically no change (+0.01). The intercept rule rarely changes the outcome against this pool.
  - **`rusher_camper`**: 0.00, although each part beat greedy head-to-head in E-006. A reminder that strength in this pool is not additive (G10).
- **Conclusions** (10 tuning seeds; selecting the best of 12 is optimistically biased, G3):
  - Worth validating: **breaker**, **breaker + tracker**, and the two families F1 and F2 (E-008).
  - Dropped for now: tracker alone, roles in this form, intercept, `rusher_camper`.
  - Return threshold: undecided; to be tested combined with the breaker.
- **Follow-ups**: E-010 (a larger screen on fresh tuning seeds 11–50, including breaker combinations), then validation on validation seeds 21+ (P-14).

## E-008 — Two other agent families: weighted features (F1) and potential field (F2) (2026-10-17)
- **Status**: done (screen)
- **Question**: with hand-set weights, does a one-step evaluation attacker reach greedy's level? If so, it is worth tuning offline (M-02 / M-07 without RL).
- **Variants**: new file `teams/families_v1.py`, a copy of the greedy_v1 machinery plus two attackers. Both are paired with greedy's PatrolDefender and keep greedy's forced returns (out of time, winning trip, ≤ 2 food left).
  - `feature` (F1, M-02): it scores each legal move by Σ w·f of the cell it leads to. The features are eat, distance to food, carried × distance home, ghost proximity, caught, trapped in a dead end, capsule distance when threatened, stop, reverse, and revisits in the last 8 moves.
  - `field` (F2, M-14): a potential field.
    - Each food pulls by 0.75^distance, weaker deep in a dead end while a ghost is seen.
    - Home pulls by carried × 0.6 × 0.9^distance.
    - Visible ghosts push by 8 × 0.5^(distance−1), and a cell within 1 of a ghost costs −1000.
    - Capsules pull while threatened. Small penalties for stopping and revisiting.
  - Weights are overridable as `w_<name>` options for later tuning.
- **Smoke** (`smoke_families`, 1 seed against baseline and camper): no crash, max move 0.10 s. Both beat the baseline on that seed.
- **Setup**: in the E-007 screen (`scr1`, tuning seeds 1–10, 7 pool opponents + greedy).
- **Results**: both families **beat greedy** on the screen, with hand-set weights and no tuning:
  - `feature` (F1): paired **+0.44 [+0.11, +0.81]**, no opponent below +0.15, head-to-head 1.25 (6-7-7).
  - `field` (F2): paired **+0.34 [+0.04, +0.69]**, worst turtle −0.20, head-to-head 1.80 (10-6-4).
  - **Diagnostics**: F1 rarely dies (0.15 per game against baseline, camper and double_attack) and returns the most food against the baseline (21.2 per game, greedy 17.3) and double_attack (19.9, greedy 10.1). F2 carries more (max carried 10–12) and loses more food (4.6 per game against the baseline).
  - Both cross the border far more than greedy against the guards (Pacman moves against camper: F1 118, F2 87, greedy 31) without a breaker. A one-step evaluation never "waits" for a fully safe target.
  - 0 crashes, warnings and violations; max move 0.047 s.
- **Conclusions**: both families are viable; on tuning seeds they are at least as strong as greedy plus the breaker. They are the natural targets for offline weight tuning (M-02), since their weights are exposed as options. Validation is next (P-14).

## E-009 — The engine sleeps 30 ms before every move: evaluation 35× faster without it (2026-10-17)
- **Status**: done
- **Question**: is the laptop's CPU the bottleneck of the evaluation runs (user question)?
- **Findings**:
  - **CPU**: AMD Ryzen 5 5500U (6 cores, 12 threads, 15 W, base 2.1 GHz). During the E-007 screen with 6 parallel games it ran at about 127% of base clock, but at **only 10–13% total CPU**. Each game process used about 40 MB.
  - **Cause**: `game.py` line 648 calls `time.sleep(delay)` before every agent move, and `capture.py`'s `--delay-step` defaults to 0.03 s even with `-q`. That is 1,200 × 0.03 = 36 s of sleep in each ~40 s game [verified in code].
  - The sleep happens outside the agents' timed moves (the timer starts after it), so removing it cannot change what the agents compute.
- **Fix**: `eval/evaluate.py` now passes `--delay-step 0`. This is a command-line flag; nothing in the framework changed (R3).
- **Check**:
  - 12 games already recorded in `scr1` (lab_roles vs greedy, camper and rusher; tuning seeds 1–2, both colours) were replayed with `--delay-step 0`.
  - **12/12 identical** in score and every diagnostic counter (run `delay0_check`).
  - Wall time per game: **1.3–1.4 s** instead of 40.6–48.7 s.
- **Consequences**:
  - All runs from now on are CPU-bound and about 35× faster. With 6 workers the remaining 1,715 screen games took 8 minutes.
  - Runs that were impractical (hundreds of seeds, offline weight tuning) are now feasible on the laptop.
  - The ~40 s per game in E-000 and evaluation.md section 3 was this sleep, not the agents. Move-time measurements were never affected: they come from the sentinel, around the agent's own call.

## E-010 — Screen 2: the leaders on 40 fresh tuning seeds, plus breaker combinations (2026-10-17)
- **Status**: done
- **Question**: do the E-007/E-008 leaders hold up on more seeds, and does the breaker combine well with the return threshold, the tracker or the intercepting defender?
- **Variants**:
  - Screened before: `lab_breaker`, `lab_breaker_tracker`, `feature`, `field`.
  - New combinations: `lab_breaker_ret8`, `lab_breaker_adaptive`, `lab_breaker_intercept`.
  - Greedy as the reference.
- **Setup**:
  - Each candidate (and greedy) against greedy, baseline, double_attack, turtle, camper, camper2, rusher and baseline_plus on **tuning seeds 11–50** (`--seed-offset 10 --n-seeds 40`), both colours: 5,040 games.
  - 8 workers, `--delay-step 0` (E-009): 22 minutes.
  - Run `scr2`; summary in `eval/results/scr2_summary.md`.
  - Windows 11, Python 3.8.10, framework `54cd83c`.
- **Tooling bug found**: the summary crashed after the last game. The exact win-rate interval used `math.comb(n, i) * p**i`, which overflows a float beyond ~1,000 games per agent. It now computes the binomial terms in log space; the old values are reproduced (40/40 → ≥ 91.2%, 110/160 → [61, 76]).
- **Results**: 0 crashes, 0 time warnings, 0 violations; max move 0.095 s. Each candidate is paired with greedy over 560 games (7 opponents × 40 seeds × 2 colours).

  | candidate | paired Δ vs greedy [95% CI] | E-007 (10 seeds) | worst opponent Δ | best opponent Δ | head-to-head vs greedy (W-T-L) |
  |---|---|---|---|---|---|
  | `lab_breaker_ret8` | **+0.21 [+0.08, +0.34]** | — | baseline +0.00 | camper +0.51 | 1.50 (35-15-30) |
  | `lab_breaker_adaptive` | **+0.18 [+0.06, +0.31]** | — | baseline +0.04 | camper +0.40 | 1.62 (38-16-26) |
  | `lab_breaker_intercept` | **+0.17 [+0.05, +0.28]** | — | double_attack +0.01 | camper +0.42 | 1.61 (38-15-27) |
  | `lab_breaker` | **+0.13 [+0.02, +0.24]** | +0.45 | baseline +0.00 | camper +0.35 | 1.55 (36-16-28) |
  | `lab_breaker_tracker` | +0.13 [+0.01, +0.25] | +0.38 | double_attack −0.17 | camper +0.42 | 1.65 (39-15-26) |
  | `feature` (F1) | +0.07 [−0.08, +0.20] | +0.44 | camper2 −0.07 | double_attack +0.29 | 1.52 (35-17-28) |
  | `field` (F2) | −0.04 [−0.20, +0.11] | +0.34 | camper2 **−0.40** [−0.70, −0.10] | double_attack +0.47 | **1.05 (24-12-44)** |

- **Conclusions**:
  - **The 10-seed screen overestimated every leader by a factor of about 3** (+0.45 → +0.13 for the breaker, +0.44 → +0.07 for F1, +0.34 → −0.04 for F2). This is the winner's curse of picking the best of 12 on few seeds (G3). Screens need ≥ 40 seeds before they are believed.
  - **The breaker is a real but modest gain**: +0.13, CI above 0 on fresh seeds, and no opponent worse. Its gain is concentrated against the guarding teams (camper +0.35, camper2 and turtle about +0.2).
  - **The breaker combines well**: return-at-8 (+0.21), the adaptive return threshold (+0.18) and the intercepting defender (+0.17) each add a little on top. The differences between these combinations are within noise.
  - **The families**: F1 is about as good as greedy (+0.07) and is still the candidate for weight tuning. F2 loses to greedy head-to-head and against camper2, so it is dropped for now.
  - Tracker alone was negative (E-007) and adds nothing to the breaker here.
- **Follow-ups**: E-011 validates the breaker variants and `breaker + ret8 + intercept` on validation seeds 21–60 (P-14).

## E-011 — Validation of the breaker variants on unused validation seeds 21–60 (2026-10-17)
- **Status**: done
- **Question**: do the E-010 leaders pass the accept rule (evaluation.md section 2) against greedy on validation seeds that were never used for design (T-50)?
- **Variants** (`teams/greedy_lab_v1.py`, frozen):
  - `lab_breaker`
  - `lab_breaker_ret8`
  - `lab_breaker_adaptive`
  - `lab_breaker_ret8_intercept` (C2 + C4 + return at 8; not screened before, it combines the three best single additions of E-010)
  - Greedy as the incumbent.
- **Setup**:
  - Each candidate and greedy against greedy, baseline, baseline_plus, double_attack, turtle, camper, camper2, rusher, feature and field, on **validation seeds 21–60** (`--seed-offset 20 --n-seeds 40`), both colours: 3,920 games.
  - 8 workers, `--delay-step 0`, ~17 minutes. Run `val1`; summary in `eval/results/val1_summary.md`.
  - Windows 11, Python 3.8.10, framework `54cd83c`.
- **Results**: 0 crashes, 0 time warnings, 0 violations; max move 0.106 s (`lab_breaker_ret8_intercept`), budget 0.5 s. Each candidate is paired with greedy over 720 games (9 opponents × 40 seeds × 2).

  | candidate | paired Δ vs greedy [95% CI] | worst opponent Δ | head-to-head vs greedy (W-T-L) | mean PPG over the 10 opponents |
  |---|---|---|---|---|
  | greedy (incumbent) | — | — | — | 1.89 (9 opponents) |
  | `lab_breaker` | +0.26 [+0.15, +0.38] | baseline 0.00 (3.00 both) | 1.52 (33-23-24) | 2.09 |
  | `lab_breaker_adaptive` | +0.24 [+0.13, +0.35] | baseline 0.00 | 1.60 (35-23-22) | 2.08 |
  | `lab_breaker_ret8` | +0.37 [+0.26, +0.49] | baseline 0.00 | 1.68 (37-23-20) | 2.21 |
  | **`lab_breaker_ret8_intercept`** | **+0.42 [+0.30, +0.54]** | baseline 0.00 | **1.76 (40-21-19)** | **2.26** |

  **`lab_breaker_ret8_intercept` vs greedy, per opponent** (80 games each):

  | opponent | candidate PPG | greedy PPG | paired Δ [95% CI] |
  |---|---|---|---|
  | baseline | 3.00 | 3.00 | +0.00 |
  | baseline_plus | 2.85 | 2.64 | +0.21 [+0.05, +0.41] |
  | camper | 1.62 | 1.06 | +0.56 [+0.23, +0.91] |
  | camper2 | 2.73 | 2.20 | +0.53 [+0.30, +0.78] |
  | double_attack | 2.16 | 1.64 | +0.53 [+0.15, +0.88] |
  | feature | 1.60 | 1.20 | +0.40 [+0.06, +0.72] |
  | field | 2.33 | 1.55 | +0.78 [+0.41, +1.16] |
  | rusher | 1.71 | 1.24 | +0.47 [+0.14, +0.82] |
  | turtle | 2.80 | 2.50 | +0.30 [+0.05, +0.57] |

  **Diagnostics (target signals)**:
  - The team spends more moves as a Pacman against the guards (camper 90 vs 55, camper2 89 vs 40, turtle 108 vs 77) and returns more food (camper 9.6 vs 5.8, camper2 8.5 vs 4.2).
  - It reaches 28 food first far more often against double_attack (25 vs 4 games of 80).
  - It dies more against the guards (camper 1.15 vs 0.69 per game).
- **Accept rule** (`lab_breaker_ret8_intercept` vs the incumbent greedy):

  | rule | result |
  |---|---|
  | 1. Gates | ✓ lint OK; 0 crashes, 0 warnings, 0 violations; max move 0.106 s ≤ 0.5 s (Windows, 8 parallel games) |
  | 2. Pool improvement | ✓ +0.42 [+0.30, +0.54]; 40 seed-pairs per opponent |
  | 3. No regression > δ | ✓ every opponent ≥ 0.00 (baseline saturated at 3.00 for both) |
  | 4. Head-to-head ≥ 1.5 | ✓ 1.76 |
  | 5. Confirmation | pending: E-012 on validation seeds 61–100 |

  The other three variants also pass rules 1–4. This one was chosen as the best of four on these seeds, so rule 5 is needed (G3).
- **Note on E-010**: on validation seeds the gains are larger than on tuning seeds 11–50 (breaker +0.26 vs +0.13). The pool differs (feature and field are added here), and the seed sets differ. Both runs agree that ret8 ≥ adaptive ≥ breaker alone. `ret8_intercept` was not in E-010.

## E-012 — Confirmation of `lab_breaker_ret8_intercept` on fresh validation seeds 61–100; `greedy_v2` (2026-10-17)
- **Status**: done
- **Question**: does the E-011 winner (picked as the best of four) hold its gain on validation seeds not used to select it (accept rule 5)?
- **Variants**:
  - `lab_breaker_ret8_intercept` (frozen `teams/greedy_lab_v1.py`) and greedy.
  - New file **`teams/greedy_v2.py`**: a copy of greedy_lab_v1 with `breaker='1'`, `intercept='1'` and `return_at='8'` as the `create_team` **defaults** (the tournament passes no options).
  - Identity check (run `identity_v2`): greedy_v2 with defaults vs baseline, camper and turtle on validation seeds 21–22, both colours. **12/12 games identical** to `lab_breaker_ret8_intercept` in `val1` (score and every diagnostic counter).
- **Setup**:
  - Both against greedy, baseline, baseline_plus, double_attack, turtle, camper, camper2, rusher, feature and field, on **validation seeds 61–100** (`--seed-offset 60 --n-seeds 40`), both colours: 1,520 games.
  - 8 workers, `--delay-step 0`. Run `conf1`; summary in `eval/results/conf1_summary.md`.
  - Windows 11, Python 3.8.10, framework `54cd83c`.
- **Results**: 0 crashes, 0 time warnings, 0 violations; max move 0.054 s.
  - **Paired vs greedy over 720 games: +0.42 [+0.32, +0.51]** (E-011: +0.42 [+0.30, +0.54]).
  - **Head-to-head vs greedy: 2.16 (53-14-13)**.
  - Overall: 618-73-109 (2.41 points per game) vs greedy's 448-164-188 (1.89).

  | opponent | candidate PPG | greedy PPG | paired Δ [95% CI] |
  |---|---|---|---|
  | baseline | 3.00 | 3.00 | +0.00 |
  | baseline_plus | 2.98 | 2.73 | +0.25 [+0.07, +0.45] |
  | camper | 1.96 | 0.90 | **+1.06** [+0.72, +1.40] |
  | camper2 | 2.60 | 2.27 | +0.33 [+0.05, +0.60] |
  | double_attack | 2.33 | 1.90 | +0.42 [+0.09, +0.75] |
  | feature | 1.98 | 1.34 | +0.64 [+0.31, +0.99] |
  | field | 2.31 | 2.00 | +0.31 [+0.00, +0.62] |
  | rusher | 1.98 | 1.50 | +0.47 [+0.15, +0.78] |
  | turtle | 2.80 | 2.55 | +0.25 [+0.07, +0.45] |

- **Accept rule** (evaluation.md section 2), `greedy_v2` (≡ `lab_breaker_ret8_intercept`) vs greedy: **rules 1–5 all pass**.
  - 1. Gates: lint OK, 0/0/0, max move 0.106 s over both runs.
  - 2. +0.42, CI above 0, in both E-011 and E-012.
  - 3. No opponent below 0.
  - 4. Head-to-head 1.76 and 2.16.
  - 5. Confirmed on unused validation seeds.
- **Not done yet** (release gate, evaluation.md section 2): the Linux / Python 3.8 timing check, the single use of the locked test seeds, and ≥ 200 games of greedy_v2 *itself* (so far 12, plus 1,600 of its identical lab twin).
- **Decision**: **promoting greedy_v2 to `my_team.py` is left to the user** (as for E-003). `my_team.py` is unchanged.
- **Caveat**: all of this is measured against our own pool (evaluation.md section 9, weakness 1). The field on 2026-11-23 may behave differently.

## E-013 — Promote `greedy_v2` to my_team.py; reference pool of 5 (2026-10-18)
- **Status**: done (user decision).
- **Change**:
  - `my_team.py` is now `teams/greedy_v2.py` with a different header comment only. The body was checked with `diff` against greedy_v2.py: identical.
  - Lint OK. Smoke test from the repo root against `baseline_team` on RANDOM13 (`-q -c`): won by 12, no exception or warning.
- **Basis**: greedy_v2 (≡ `lab_breaker_ret8_intercept`) passed accept rules 1–5 against greedy (E-011, E-012): +0.42 on validation seeds 21–60 and 61–100; head-to-head 1.76 and 2.16.
- **Release gate still open** (before the test run on 2026-11-23):
  - Linux / Python 3.8 timing;
  - ≥ 200 games of greedy_v2 / my_team.py itself;
  - one logged run on the locked test seeds.
- **Evaluation policy from now on** (user decision): no more all-vs-all round robins. New candidates play only the **reference pool** of the 5 best currently performing agents:

  | member | why | mean PPG on validation seeds 21–60 (E-011) |
  |---|---|---|
  | `greedy_v2` (incumbent = my_team.py) | accepted | 2.26 (its lab twin) |
  | `greedy` (v1) | previous incumbent, forgetting check | 1.89 |
  | `feature` (F1) | best agent of another family | 1.48 |
  | `camper` | strong defence style | 1.36 |
  | `rusher` | capsule-first style | 1.24 |

  - Left out:
    - the `lab_breaker*` variants, near-duplicates of greedy_v2;
    - field (0.95), double_attack (0.94), camper2, turtle, baseline_plus;
    - baseline (saturated; smoke tests only).
  - The member list is in `eval/league.json` (`_reference_pool`). The command is in evaluation.md section 5.
- **Not done**: no new experiments, per the user ("continue in the morning").

## E-014 — Where greedy_v2 loses points (2026-10-18)
- **Status**: done
- **Question**: against which opponents, and in which kinds of games, does greedy_v2 (= `my_team.py`) lose points? What should the next candidates fix?
- **Variants**: `greedy_v2` (`teams/greedy_v2.py`, body identical to `my_team.py`), repo `f026d02`.
- **Setup**:
  - greedy_v2 against greedy, feature, camper, rusher, camper2, double_attack, turtle, baseline_plus and field on **tuning seeds 51–150** (`--seed-offset 50 --n-seeds 100`; never used before), both colours: 1,800 games.
  - 6 workers, `--delay-step 0`, ~17 minutes. Windows 11, Python 3.8.10, framework `54cd83c`. Run `diag_v2`; summary in `eval/results/diag_v2_summary.md`.
  - New tool `eval/replay_probe.py` (local analysis only, never submitted):
    - `classify` sorts every non-win by the sentinel diagnostics.
    - `replay` re-plays chosen games with `--record` (deterministic: every replayed score matched the recorded one), then re-simulates the replay and measures what happened from the **true** state (offline, after the game).
    - Measured: deaths (in a dead end or not; whether the killer was in sight when our agent went into the dead end; whether it could reach the exit first), food returned, invasions, defender distance, standoffs, capsules.
  - Replay samples: 40 random non-wins per opponent (23 against turtle, all it had), and 60 random wins.
- **Results**:
  - **Gates**: 0 crashes, 0 time warnings, 0 violations; max move 0.132 s.
  - **Overall**: 1185-256-359, **2.12 points per game [2.03, 2.20]**.

  | opponent | PPG | wins / 200 | points lost |
  |---|---|---|---|
  | camper | **1.51** | 89 | 297 |
  | greedy (v1) | 1.73 | 102 | 255 |
  | feature | 1.76 | 112 | 247 |
  | rusher | 1.81 | 110 | 237 |
  | double_attack | 2.02 | 126 | 197 |
  | field | 2.09 | 133 | 182 |
  | camper2 | 2.50 | 150 | 100 |
  | turtle | 2.77 | 177 | 46 |
  | baseline_plus | 2.86 | 186 | 28 |

  **Points lost by kind of game** (`replay_probe.py classify`; a tie costs 2, a loss 3; 1,589 points lost in total):

  | kind | points lost | share | mostly against |
  |---|---|---|---|
  | loss: the opponent returned more (our defence) | 465 | 29% | feature 35, camper 29, double_attack 26, greedy 25, field 23 games |
  | loss: our deaths (≥ 3 deaths or ≥ 6 food lost) | 420 | 26% | rusher 38, greedy 27, feature 26, camper 24, field 24 games |
  | tie 0–0, we barely attacked (< 60 Pacman moves) | 292 | 18% | camper2 49, greedy 23, camper 20, rusher 20, turtle 16 games |
  | loss: we returned ≤ 3 | 135 | 8% | camper 22 games |
  | tie with equal scoring | 134 | 8% | |
  | tie 0–0 after attacking | 86 | 5% | |
  | loss: out-raced to 28 | 57 | 4% | double_attack 17 games |

  **Replay probe** (true state; non-wins unless marked):

  | opponent | deaths / game | deaths in a dead end | of those: killer in sight when we went in | of those: killer could reach the exit first | their food returned / game | kills / game | mean defender–invader distance | standoff plies / game | our Pacman plies / game |
  |---|---|---|---|---|---|---|---|---|---|
  | camper | 1.07 | 88% | 84% | 82% | 9.8 | 1.18 | 4.9 | 226 | 56 |
  | camper2 | 0.60 | 38% | 89% | 78% | 0.0 | 0.00 | – | 445 | 11 |
  | double_attack | 0.33 | 46% | 100% | 100% | 15.9 | 0.72 | 7.8 | 84 | 187 |
  | feature | 1.35 | 78% | 88% | 83% | 14.6 | 0.40 | 5.7 | 130 | 106 |
  | field | 1.65 | 82% | 91% | 76% | 12.9 | 0.97 | 6.7 | 139 | 105 |
  | greedy | 1.68 | 94% | 79% | 86% | 9.1 | 1.20 | 5.9 | 167 | 87 |
  | rusher | 2.02 | 90% | 92% | 92% | 11.1 | 0.80 | 8.1 | 155 | 92 |
  | turtle (23 games) | 1.22 | 89% | 88% | 60% | 0.0 | 0.00 | – | 186 | 52 |
  | *wins, all opponents (60)* | 0.90 | 85% | 78% | 76% | 4.3 | 1.22 | 4.9 | 122 | 141 |

  - Only double_attack ever had two invaders on our side at once (52% of its invaded plies).
  - **Mutual-trap freeze** (traced: camper, seed 78390034, a 0–0 tie). From ply ~120 to 1200 all four agents stood still or oscillated in place. Our attacker carried 2 in a corner, held by camper's ghost. Camper's attacker carried 2 on our side, held by our defender on the cell its way home passes through. Our defender never closes in, because the intercept rule only attacks an invader within distance 2. How often this happens was not measured.
  - An earlier version of the probe reported "killer out of sight 1 ply before death" as 0%. That metric is vacuous (a ghost that eats us is always in sight one ply earlier) and was replaced by the entry-time measure above (T-52).
- **Conclusions** (tuning seeds; our classification thresholds; replay samples of 40 per opponent):
  1. **Dead-end deaths are greedy_v2's most frequent avoidable loss.** In non-wins against 6 of 8 opponents, 78–94% of our deaths happen inside a dead end. In 76–92% of those, the killing ghost could reach the dead end's exit before we got back out. In 79–92% it was already in sight when we went in. The same holds in wins (85%).
     - The cause is in the code: the attacker's race-safe BFS checks only the way *to* the food (`food_is_safe`), not the way back out.
     - The exit-race check exists (`DeadEndAttacker`, H-M02 + H-S03; F1's `trapped` feature) but was only tested in E-002, against a pool without real defenders. → candidate C1.
  2. **Defence is the biggest single source of lost points (29%).**
     - In non-wins our defender is on average 5–8 cells from the invader.
     - It kills the feature attacker only 0.40 times per game while conceding 14.6 food.
     - Two invaders at once happen only against double_attack.
     - → candidates: defender improvements (closing in on trapped invaders, H-M03 cut cells), C2 parts.
  3. **Standoffs still cost 18%** (0–0 ties with almost no attacking), mostly against two guards (camper2) and against greedy/camper/rusher. The breaker walks to another entry, and a guard that follows meets it there. → C3 (two-entry attack).
  4. **A mutual-trap freeze exists** (one traced game; frequency unknown).
- **Follow-ups**: E-015 (new league opponents built from these findings); candidates C1–C3 on top of greedy_v2 (user decision pending).

## E-015 — New league opponents: chokepoint defender, an exploiter of greedy_v2, two held-out teams (2026-10-18)
- **Status**: done
- **Question**: do opponents built outside our current pool's styles (a chokepoint defender, an exploiter written against greedy_v2's E-014 weaknesses, blind-written held-out teams) stress greedy_v2 more than the current pool does?
- **Variants**:
  - New file `teams/sparring_v2.py`: a verbatim copy of greedy_v2 plus three classes.
    - `ChokeDefender` (H-M03).
      - At startup, for every home cell g, it computes the home cells reachable from the border only through g (one BFS per cell, 0.03–0.05 s per map).
      - Idle, it stands on the cell that seals off the most of its remaining food, if that is at least 3.
      - It traps a visible invader behind the tightest cut cell it reaches no later than the invader, steps only to neighbours that still seal it off, and eats it when adjacent.
      - Food vanishing sends it to the cut behind that food. Invaders in the open are handled by greedy_v2's intercept.
    - `ShadowDefender`: ChokeDefender's trapping; idle, it stands on the border cell across from the enemy "raider" (the enemy last seen on its side), using the raider's position seen now or within 40 plies.
    - `FeatureAttacker`: a copy of F1 (E-008).
  - League entries:
    - `choke` = greedy_v2's attacker + ChokeDefender, so `choke` vs `greedy_v2` differs only in the defender.
    - `exploit_v2` = FeatureAttacker + ShadowDefender.
  - Held-out `heldout_a` and `heldout_b` (`eval/heldout/`):
    - Written by a separate agent that was told not to read our code, our docs (except framework.md and rules.md) or our results, and to test only against `baseline_team` and each other (seeds RANDOM1–300).
    - We did not read their code (T-53). Their style labels are in league.json.
    - Its report: both 20-0-0 vs the baseline; A vs B 11-0-9; max move 0.045 s (A) and 0.103 s (B, 0.12 s search cap); startup ≤ 1.98 s.
    - Our check: `check_rules.py` OK for both.
- **Setup**:
  - Smoke tests: 4 games each against baseline_team and greedy_v2 (RANDOM7, RANDOM13), plus a quick 80-game check (`quick_new`, tuning seeds 51–70; a subset of `spar2`, identical games). exploit_v2 lost both smoke games to greedy_v2 (−20, −21) but was about even over the 40 quick-check games, which is why the full run went ahead.
  - `choke` and `exploit_v2` against the reference pool (greedy_v2, greedy, feature, camper, rusher) on tuning seeds 51–150, both colours: 2,000 games, run `spar2`.
  - greedy_v2 and greedy against heldout_a and heldout_b on the same seeds: 800 games, run `heldout1`. It was first stopped and restarted with 50 seeds on a wrong runtime estimate, then extended to 100 with `--resume`; deterministic games, so nothing changes.
  - 4–6 workers, `--delay-step 0`, Windows 11, Python 3.8.10, framework `54cd83c`.
- **Results**:
  - **Gates**: 0 crashes, 0 time warnings, 0 violations in all games. Max move 0.141 s (choke), 0.098 s (exploit_v2).
  - **Strength in the pool** (row vs column, points per game, 200 games per pair):

    | | vs greedy_v2 | vs greedy | vs feature | vs camper | vs rusher | mean |
    |---|---|---|---|---|---|---|
    | choke | 1.43 | 1.80 | 1.64 | 1.52 | 1.64 | 1.61 |
    | exploit_v2 | 1.49 | 1.72 | 1.79 | 1.76 | 1.52 | 1.66 |

  - **greedy_v2's points per game against each opponent** (tuning seeds 51–150; E-014 for the old ones):
    - choke **1.40**
    - exploit_v2 **1.42**
    - camper 1.51 (the toughest before)
    - greedy 1.73
    - feature 1.76
    - rusher 1.81
  - **Did the exploiter hit its targets?** greedy_v2's diagnostics against exploit_v2:
    - It kills the F1 attacker only 0.33 times per game (0.12 in its non-wins), against 1.0–1.4 against most opponents.
    - 232 standoff moves per game (camper 265, choke 162).
    - In its non-wins, 71% of its deaths are in dead ends, all of them with the killer able to reach the exit first.
  - **ChokeDefender as a defender**:
    - Against the same opponents it concedes slightly more and kills slightly less than greedy_v2's PatrolDefender (e.g. against camper it concedes 9.2 and kills 1.21; greedy_v2 concedes 8.5 and kills 1.37).
    - In a traced game its idle post was deep in its half (x = 5, border at x = 16), and the invader ate elsewhere.
    - The same trace showed the E-014 mutual-trap freeze again, with greedy_v2's defender holding choke's attacker (= greedy_v2's attacker) in a corner from ply ~100 on. The freeze is a greedy_v2-defender pattern, not specific to camper.
  - **Held-out** (run `heldout1`, 800 games; totals only, T-53):

    | agent | vs heldout_a | vs heldout_b | overall [95% CI] |
    |---|---|---|---|
    | greedy_v2 | 1.43 | **0.89** | 1.16 [1.01, 1.30] |
    | greedy (v1) | 1.25 | 0.60 | 0.92 [0.79, 1.06] |

    - Paired greedy_v2 − greedy over the held-out games: **+0.23 [+0.10, +0.39]** (heldout_a +0.18 [−0.03, +0.41], heldout_b +0.29 [+0.07, +0.52]).
    - **Generalisation gap** (evaluation.md section 4). greedy_v2 averages 1.70 points per game against the four non-mirror reference-pool members on the same seeds (E-014: greedy 1.73, feature 1.76, camper 1.51, rusher 1.81) and 1.16 against the held-out teams: R = (1.70 − 1.16) / 1.70 ≈ **32%**.
    - heldout_b (style label: defence first, a permanent guard plus a cautious raider, turtling when ahead late) beats greedy_v2 clearly (0.89 points per game for greedy_v2). It is the strongest opponent we have.
- **Conclusions**:
  - Both new sparring teams are now the hardest opponents greedy_v2 has *in the pool* (1.40–1.42 points per game) and the two strongest non-mirror agents in it.
  - The exploiter reaches greedy_v2's known weak spots (no kills against an evasive attacker, standoffs, dead-end traps), but it is not a decisive exploit: it is about even with greedy_v2 (1.49 vs 1.42).
  - **External validity is a real problem, now measured.** Against two blind-written teams greedy_v2 drops by about a third, and one of them beats it. Our pool overstates greedy_v2's strength. The accepted v1 → v2 gain does carry over (+0.23, CI above 0), at about half its size in the pool (+0.42).
  - Adding choke / exploit_v2 to the reference pool, and how often to check the held-out pool, are user decisions.

## E-016 — Linux / Python 3.8 timing of my_team.py; Windows–Linux identity (2026-10-18)
- **Status**: done
- **Question**: does `my_team.py` (= greedy_v2) stay far below the 1 s move limit on Linux with Python 3.8 and the engine's real `SIGALRM` time limits, also under full CPU load? Do Linux and Windows play the same games?
- **Setup**:
  - WSL Ubuntu 24.04 on this laptop (12 logical CPUs, 7.4 GB RAM).
  - CPython 3.8.20 installed with `uv` (no sudo), frozendict 2.3.4, framework `54cd83c`, in a mirror of the repo at `~/pacman_wsl` on the Linux filesystem (recipe in framework.md).
  - The `submission` league entry (`my_team.py`) against greedy, feature, camper, rusher, choke and exploit_v2, both colours, `-q -c`, `--delay-step 0`, sentinel timing. The Windows side was idle during both passes.
    - **Serial**: tuning seeds 251–265, `--jobs 1`, 180 games, run `wsl_serial`.
    - **Loaded**: tuning seeds 266–280, `--jobs 12` (all logical CPUs busy; load average ≈ 6), 180 games, run `wsl_loaded`.
  - **Identity**: the serial pass's 180 games replayed on Windows (run `win_vs_wsl`).
- **Results**:

  | pass | games | max move | 99th percentile of per-game max | max p95 | max startup | moves > 0.5 s | engine warnings / timeouts / crashes |
  |---|---|---|---|---|---|---|---|
  | serial | 180 | 0.064 s | 0.031 s | 0.0010 s | 0.59 s | 0 | 0 |
  | loaded (12 jobs) | 180 | 0.087 s | 0.069 s | 0.0039 s | 1.42 s | 0 | 0 |

  - **Identity**: **180/180 games had identical scores** on Linux and Windows.
  - The points per game in these runs (1.39 serial, 1.88 loaded; 30 games per opponent) are noise-level samples on different seeds, not a strength measurement.
- **Conclusions**:
  - On Linux / Python 3.8, greedy_v2 uses < 9% of the 1 s move limit even with every CPU busy, and < 10% of the 15 s startup limit. The release gate's timing item is met for this machine. The cluster's speed is still unknown (T-41), but the margin is about 11×.
  - Windows results transfer to Linux unchanged for this agent, so our Windows evaluations measure the same games the cluster would play.
  - **Release gate status for greedy_v2**:
    - accept rule ✓ (E-011/E-012)
    - ≥ 200 own games with 0 crashes / violations ✓ (E-014: 1,800; E-015: 1,200; E-016: 360)
    - Linux timing ✓ (E-016)
    - locked test seeds: not done
    - held-out pool: measured on tuning seeds (E-015), not yet on test seeds

## E-017 — Reference pool of 7: choke and exploit_v2 join; round robin (2026-10-18)
- **Status**: done
- **Change** (user decision): `choke` and `exploit_v2` (E-015) were added to `_reference_pool` in `eval/league.json`, so the pool now has 7 members: greedy_v2, greedy, feature, camper, rusher, choke, exploit_v2.
- **Question**: does their strength from E-015 hold on fresh seeds in a full round robin of the new pool?
- **Setup**:
  - All 7 members, every pair, on **tuning seeds 281–330** (never used before), both colours: 2,100 games, run `pool7`.
  - 6 workers, `--delay-step 0`, Windows 11, Python 3.8.10, framework `54cd83c`.
  - For part of the run a second evaluation (E-018 `scr3`, 5 workers) shared the CPU.
- **Results**: 0 crashes, 0 time warnings, 0 violations.

  | agent | W-T-L | PPG [95% CI] | Nash-averaged payoff |
  |---|---|---|---|
  | exploit_v2 | 311-70-219 | **1.67** [1.44, 1.89] | −0.27 |
  | greedy_v2 | 302-68-230 | 1.62 [1.47, 1.79] | **+0.00 (weight 0.99)** |
  | choke | 285-64-251 | 1.53 [1.37, 1.70] | −0.18 |
  | feature | 271-65-264 | 1.46 [1.26, 1.66] | −0.45 |
  | camper | 240-111-249 | 1.39 [1.24, 1.54] | −0.33 |
  | greedy | 207-102-291 | 1.21 [1.06, 1.35] | −0.42 |
  | rusher | 191-106-303 | 1.13 [0.97, 1.30] | −0.51 |

  **Head-to-head** (row vs column, points per game, 100 games per pair):

  | | camper | choke | exploit_v2 | feature | greedy | greedy_v2 | rusher |
  |---|---|---|---|---|---|---|---|
  | camper | – | 1.50 | 1.01 | 1.27 | 1.56 | 1.28 | 1.69 |
  | choke | 1.41 | – | 1.45 | 1.45 | 1.71 | 1.32 | 1.85 |
  | exploit_v2 | 1.88 | 1.45 | – | 1.76 | 1.84 | 1.31 | 1.79 |
  | feature | 1.57 | 1.48 | 1.13 | – | 1.70 | 1.24 | 1.66 |
  | greedy | 1.11 | 1.20 | 1.03 | 1.19 | – | 1.24 | 1.46 |
  | greedy_v2 | 1.61 | 1.50 | 1.58 | 1.69 | 1.66 | – | 1.70 |
  | rusher | 1.00 | 1.04 | 1.07 | 1.21 | 1.28 | 1.19 | – |

  - **Move times**: max move 0.158 s for greedy_v2. Spikes of 0.48 s (camper) and 0.43 s (exploit_v2) appeared while 11 games ran at once (T-49). camper's code is trivial, so the spikes are load, not agents.
- **Conclusions**:
  - **The two new members hold up**: exploit_v2 has the highest mean in the pool (1.67) and choke is third (1.53).
  - Against greedy_v2 they are roughly even, depending on the seeds: greedy_v2 scores 1.58 / 1.50 against them here, against 1.42 / 1.40 on seeds 51–150 (E-015).
  - greedy_v2 is still the only member that beats every other member head-to-head (all ≥ 1.50), so the Nash mixture puts all its weight on greedy_v2.

## E-018 — Three candidates from E-014 on top of greedy_v2: exit race, squeeze, raid (2026-10-18)
- **Status**: done (screen). No candidate went to validation (see conclusions).
- **Question**: do the fixes suggested by E-014 raise greedy_v2's points per game against the 7-member reference pool?
- **Variants**: new file `teams/greedy_lab_v2.py`, a copy of greedy_v2 plus three switches that are all off by default (league entries `lab2_*`).
  - `exit_race` (P-19, H-M02 + H-S03): the attacker targets a food only if, for every enemy-side cell that cuts the food off from our side, it gets back past that cell (one step of margin) before any visible ghost can reach it.
    - This generalises `DeadEndAttacker` from dead-end trees to any single-cell cut, so pockets with loops count too.
    - The cut table is one BFS per enemy cell at startup.
  - `squeeze` (P-20, H-M03 + H-S07): `ChokeDefender`'s trap in greedy_v2's defender.
    - It goes to the tightest cut cell it reaches no later than the invader, and closes in only through cells that keep the invader sealed off.
    - If the intercept stalls (8 own moves on ≤ 2 cells with an invader in sight; the E-014 freeze), it chases directly for 10 own moves.
  - `raid` (P-21, H-S12 + H-S09): a `RaidDefender`. If the teammate stood on our side within 2 of the border with a dangerous enemy ghost within Manhattan 6 in 6 of the last 12 own moves, and there was no invader evidence for 10 own moves, it walks to the entry farthest from the teammate and attacks for 40 own moves.
    - It returns on the first invader evidence. It uses only its own observation (no shared memory, Q4).
- **Checks**:
  - Lint OK.
  - **Identity**: `lab2_off` (all new switches off) vs greedy_v2 against baseline, camper and exploit_v2 on tuning seeds 1–3, both colours: **18/18 games identical** (score and every diagnostic counter). Run `identity_labv2`; the name `identity_lab2` was already taken by E-007, and the harness refused to overwrite it.
  - **Smoke** (`smoke_labv2`, 32 games against baseline and camper): 0 crashes / warnings, max move 0.064 s, startup ≤ 1.57 s.
    - `exit_race` changed 1/8 games, `raid` 5/8, `squeeze` **0/8**.
    - A scratch probe (not in the repo) showed the squeeze does act (in one game it chose the move 5 times, 4 of them while sealing an invader off), but those moves equal greedy_v2's intercept, which already handles dead-end trees. The squeeze differs only in pockets with loops and after stalls.
- **Setup of the screen**:
  - Each candidate and greedy_v2 against the 7-member pool on **tuning seeds 151–250**, both colours.
  - Singles: run `scr3`, 5,400 games, 5 workers, 69 minutes. Combinations: run `scr3b`, 5,600 games, 4 workers. Each candidate is paired with greedy_v2 over 1,200 games (6 opponents × 100 seeds × 2).
  - Windows 11, Python 3.8.10, framework `54cd83c`. Part of `scr3` shared the CPU with E-017.
- **Results**: 0 crashes, 0 time warnings, 0 violations in all games.

  | candidate | paired Δ vs greedy_v2 [95% CI] | worst opponent Δ [CI] | best opponent Δ [CI] | head-to-head vs greedy_v2 |
  |---|---|---|---|---|
  | `lab2_exit` (P-19) | +0.02 [−0.06, +0.10] | greedy −0.03, rusher −0.03 | exploit_v2 +0.10 [−0.06, +0.27] | 1.52 |
  | `lab2_squeeze` (P-20) | +0.02 [−0.01, +0.06] | rusher −0.02 [−0.06, +0.00] | camper +0.07 [+0.01, +0.13] | 1.43 |
  | `lab2_raid` (P-21) | **−0.07** [−0.14, +0.01] | greedy −0.20 [−0.35, −0.05] | camper +0.04 | 1.43 |
  | `lab2_exit_squeeze` | +0.05 [−0.04, +0.12] | rusher −0.03 | exploit_v2 +0.10, feature +0.10 | 1.50 |
  | `lab2_exit_raid` | −0.01 [−0.11, +0.09] | feature −0.17 [−0.39, +0.01] | choke +0.21 [+0.01, +0.41] | 1.53 |
  | `lab2_squeeze_raid` | −0.03 [−0.11, +0.06] | greedy −0.19 [−0.34, −0.04] | camper +0.12, exploit_v2 +0.12 | 1.47 |
  | `lab2_all` | +0.03 [−0.08, +0.12] | feature −0.09 [−0.31, +0.12] | choke +0.21 [+0.01, +0.41] | 1.51 |

  - `scr3b` was stopped by the user's time limit at 4,165 of 5,600 games and **completed later the same day** with `--resume` (1,435 games, 6 workers; 0 crashes, 0 time warnings, 0 violations; max move 0.147 s). The rows above are final. Before completion `lab2_squeeze_raid` read −0.02 [−0.10, +0.07] on 1,365 games, and `lab2_all` was not played.

  **Did the switches change what they targeted?** (diagnostics, team totals per game, vs greedy_v2 on the same games):
  - **exit_race**:
    - Deaths fall by about half against every opponent (camper 1.07 → 0.57, greedy 1.03 → 0.53, choke 1.00 → 0.58, feature 1.13 → 0.64, rusher 1.57 → 1.09), and food lost falls by about half (≈ 2.7 → 1.5).
    - But **food returned barely changes** (camper 10.7 → 11.0, greedy 12.4 → 12.4, feature 12.5 → 13.2), and standoff moves rise (camper 236 → 258, greedy 195 → 213).
  - **raid**: returns more (camper 10.7 → 12.1, greedy 12.4 → 13.1) but concedes more (greedy 9.4 → 10.9, rusher 8.5 → 10.3, feature 10.3 → 12.0).
  - **squeeze**: every counter within ±0.1 of greedy_v2's.
- **Conclusions** (tuning seeds 151–250; each Δ over 1,200 paired games resolves about ±0.08):
  - **No candidate shows a gain we can resolve**; none has a CI lower bound above 0. The best is `exit_squeeze` at +0.05 [−0.04, +0.12].
  - **No validation run was started**, deliberately. A real effect of +0.05 would need several hundred validation seeds to pass accept rule 2, and every validation decision spends seeds (evaluation.md section 4).
  - **E-014's diagnosis was right about the mechanism but not about the payoff.** The exit check removes about half of our deaths, yet the points stay flat: the food those deaths cost is not recovered, because the attacker waits instead. Losses "with our deaths" (E-014) are partly a symptom of games that were hard anyway.
  - **Raiding without shared plans leaves the door open**: points rise against pure guards (camper, choke, exploit_v2) and fall against attacking teams (greedy, feature, rusher).
  - **greedy_v2 stays the incumbent.**
- **Follow-ups (ideas, not started)**:
  - Give the moves the exit check saves a productive use (switch targets or entries instead of waiting).
  - A raid that is called off by the sonar as well as by food evidence.
  - ~~Finish `scr3b`~~: done (rows above); `lab2_all` adds nothing either.

## E-019 — A belief tracker for the defender: hunting hidden invaders, shadowing the raider (2026-10-18)
- **Status**: done. `lab3_shadow` **passes the accept rule** on validation seeds 101–180 (+0.16 [+0.04, +0.28]); not promoted (user decision, release gate open).
- **Question**: E-014 found that defence is greedy_v2's biggest source of lost points (29%), while its defender ignores the sonar: it reacts only to invaders it sees and to food that has already gone. Does an exact belief over each enemy's cell (H-S01, M-04) let the defender (a) catch invaders it cannot see, and (b) wait where the enemy attacker will cross, and does that raise points per game?
- **Variants**: new file `teams/greedy_lab_v3.py`, a copy of greedy_v2 plus a belief filter and two switches, all off by default (league entries `lab3_*`).
  - **Belief filter** (`update_belief`, defender only, its own observation; no shared memory, Q4; no grey-zone fields, Q3):
    - Exact forward filter over cells per enemy.
    - Motion: each enemy moves once between two of our turns; staying weighs `STAY_WEIGHT` = 0.2 against 1 per neighbour.
    - Sonar: Manhattan within ±6 of the reading, likelihood 1/13 (T-22).
    - Sight: no cell within Manhattan 5 of either of us unless visible (T-23).
    - Food events: a food or capsule of ours that vanished under no visible enemy pins the most likely hidden enemy to exactly that cell. It cannot have moved since: each enemy moves once between our turns.
    - Respawns: reset to the start cell; greedy_v2's respawn rule is corrected for our own deaths (T-55).
  - `hunt` (P-22): with no invader in sight, a hidden enemy with belief mass ≥ 0.5 on our side counts as an invader at its most likely home cell, and greedy_v2's intercept handles it. The belief replaces the "go to the eaten food" target.
  - `shadow` (P-23): with nothing to chase, the defender waits at the border entry whose cell across is nearest, in expectation, to the **raider**: the enemy most recently evident on our side (seen there, or belief mass ≥ 0.5 there). Before any enemy has come over, it patrols as greedy_v2 does.
- **Belief accuracy check** (`eval/belief_probe/`, local analysis only; usage in the header of `belief_check.py`):
  - Games were played in-process with two wrapper teams. Our wrapper logged the defender's belief after each move. The opponent's wrapper logged each opponent agent's **own** position at its own turn, which equals its position at our turn because it has not moved in between.
  - No engine object was touched.
  - `lab3_hunt_shadow` against greedy_v2, exploit_v2, rusher, feature, camper and choke on tuning seeds 431–435, both colours: 60 games.
  - **Bugs found and fixed before any screen**:
    1. Pruning cells below probability 1e-4 excluded the true cell in 22.8% of hidden turns; at 1e-12 still 2.3% (T-54). No probability pruning now.
    2. A false respawn whenever an enemy ghost ate our attacker (T-55).
    3. The first `shadow` followed the enemy nearest our side, usually their border guard. It showed the guard to our attacker, and a 22–0 win over baseline_team became a 0–0 standoff (T-56). It now follows the raider.
  - **Final file** (60 games, 15,431 hidden enemy-turns):

    | measure | value |
    |---|---|
    | true cell given probability 0 | **0.0%** (22.8% before fix 1) |
    | mean probability on the true cell | 0.16 (STAY_WEIGHT 1.0: 0.13) |
    | median maze distance, most likely cell → true cell | **4** |
    | median maze distance, last-seen position → true cell (greedy_v2's knowledge) | 9 |
    | mean expected distance to the true cell | 7.5 |
    | enemy truly on our side: belief mass ≥ 0.5 there (recall) | 66% |
    | belief mass ≥ 0.5 on our side: enemy truly there (precision) | 57% (72% in the run before the raider fix) |
    | defender move time | max 0.054 s (alongside a 6-worker screen), p99 0.002 s |

- **Checks**:
  - Lint OK.
  - **Identity**: `lab3_off` vs greedy_v2 against baseline, camper and exploit_v2 on tuning seeds 1–3, both colours: **18/18 identical** (score and every diagnostic). Repeated after the raider fix: 18/18 (runs `identity_labv3`, `identity_labv3b`).
  - **Smoke** (`smoke_labv3`, 36 games against baseline, camper, exploit_v2 on tuning seeds 1–2): 0 crashes / warnings, max move 0.036 s. Baseline 0-0-12 after the raider fix (0-2-10 before it).
- **Setup of the screen**: `lab3_hunt`, `lab3_shadow`, `lab3_hunt_shadow` and greedy_v2 against the 7-member pool on **tuning seeds 331–430** (`--seed-offset 330 --n-seeds 100`, never used before), both colours: 5,400 games, run `scr4`, 6 workers, `--delay-step 0`. Windows 11, Python 3.8.10, framework `54cd83c`, repo `07cc84a` + uncommitted lab file.
- **Results** (`scr4`, 5,400 games): 0 crashes, 0 time warnings, 0 violations; max move 0.063 s (lab3_hunt_shadow), 0.051 s (lab3_shadow).

  | candidate | paired Δ vs greedy_v2 [95% CI] | worst opponent Δ [CI] | best opponent Δ [CI] | head-to-head vs greedy_v2 | win % |
  |---|---|---|---|---|---|
  | `lab3_hunt` (P-22) | +0.07 [−0.02, +0.17] | camper −0.06 [−0.23, +0.11] | rusher +0.21 [+0.01, +0.41] | 1.50 | 49 |
  | `lab3_shadow` (P-23) | **+0.34 [+0.23, +0.45]** | greedy +0.19 [+0.01, +0.38] | feature +0.49 [+0.28, +0.73] | **1.62** | 57 |
  | `lab3_hunt_shadow` | **+0.33 [+0.22, +0.45]** | greedy +0.23 [+0.09, +0.39] | exploit_v2 +0.47 [+0.26, +0.69] | 1.56 | 57 |
  | greedy_v2 (same seeds) | – | – | – | – | 43 |

  - `lab3_shadow` per opponent (paired Δ): camper +0.34 [+0.14, +0.54], choke +0.34 [+0.12, +0.57], exploit_v2 +0.45 [+0.23, +0.68], feature +0.49 [+0.28, +0.73], greedy +0.19 [+0.01, +0.38], rusher +0.21 [+0.04, +0.38]. **Every CI is above 0.**

  **What changed** (team totals per game, same games; greedy_v2 → lab3_shadow):

  | opponent | food conceded | kills | food returned | standoff moves |
  |---|---|---|---|---|
  | camper | 8.1 → 6.2 | 1.14 → 0.67 | 9.8 → 9.8 | 267 → 310 |
  | choke | 11.9 → 9.5 | 0.99 → 0.85 | 11.6 → 11.0 | 178 → 227 |
  | exploit_v2 | 9.5 → 6.8 | 0.33 → 0.35 | 9.8 → 9.5 | 232 → 277 |
  | feature | 10.0 → 7.5 | 0.41 → 0.47 | 12.8 → 12.4 | 184 → 226 |
  | greedy | 8.6 → 6.8 | 1.21 → 0.81 | 11.0 → 10.4 | 225 → 292 |
  | rusher | 9.3 → 7.5 | 0.90 → 0.72 | 11.3 → 11.0 | 203 → 248 |

- **Conclusions** (tuning seeds 331–430; best of 3 candidates, so a validation on unused seeds is needed, G3):
  - **Shadowing the raider is the largest single gain since greedy_v2** (+0.34, every opponent's CI above 0, head-to-head 1.62). It works by deterrence, not by kills. A ghost across the border keeps the pool's race-safe attackers from crossing: food conceded falls by 20–30% while kills fall. Our own scoring is almost unchanged.
  - **Hunting adds nothing measurable**, alone (+0.07, CI includes 0) or on top of shadowing (+0.33 vs +0.34). This is consistent with its 57% precision.
  - **Caveat (external validity)**: every pool attacker avoids visible ghosts, which is exactly what a border shadow exploits. An attacker that uses capsules first (rusher) still loses +0.21 to it. Opponents that ignore ghosts or attack with two agents are not in the pool; the held-out teams are the check for that (T-53: release gate only).
  - `teams/greedy_lab_v3.py`'s header comment still describes the first `shadow` rule (the enemy nearest our side). The code and the docstring of `shadow_post` follow the raider. The screen games match the file as it is now (600/600 replays, below), so the comment was left alone rather than editing a benchmarked file.
- **Replication on fresh tuning seeds 451–550** (runs `scr5` + `scr5b`; `scr5b` = greedy_v2 against the pool on the same seeds, 1,200 games):
  - Paired `lab3_shadow` − greedy_v2: **+0.29 [+0.19, +0.39]** over 1,400 games. This counts `lab4_braid_shadow` (E-020) as a seventh opponent (+0.12 there). Over the six pool members alone the mean is +0.32.
  - Per opponent: camper +0.54 [+0.29, +0.77], greedy +0.35 [+0.15, +0.56], feature +0.29 [+0.07, +0.52], exploit_v2 +0.28 [+0.07, +0.49], choke +0.26 [+0.06, +0.45], rusher +0.17 [+0.00, +0.35].
- **Validation**:
  - **`val2`, validation seeds 101–140** (never used before; one pre-registered candidate; 1,040 games): **+0.05 [−0.10, +0.20]**, head-to-head 1.51.
    - Per opponent: greedy +0.26 [+0.04, +0.51], rusher +0.25 [+0.01, +0.54], camper +0.04, choke −0.01, feature −0.09, exploit_v2 −0.14 [−0.46, +0.16].
    - It fails accept rule 2 on its own.
  - **Was the gap a bug?** The screen and the validation disagreed by about 3 standard errors, consistently across all four quarters of each seed list (screen quarters +0.21 to +0.47; validation quarters −0.03 to +0.12). Checks:
    - 600 screen games of `lab3_shadow` (against camper, feature and exploit_v2, all 100 seeds) were replayed with the current file: **600/600 identical scores** (run `repro_scr4`).
    - The validation run used validation-list positions 101–140, with no overlap with the tuning list, as `RANDOM<seed>` maps.
    - The lab file was last written at 19:03, by the raider-fix edit, which also normalised its line endings. The run records carry no start time, so "before the screen started" is inferred from throughput only. The replays above are the actual evidence that the screen games match the current file.
    - No bug was found. The tuning-seed effect then replicated on seeds 451–550 (above).
  - **Decision basis, fixed before the next run**: accept rule 2 judged on validation seeds 101–180 pooled (`val2` + `val3`), with both halves reported. This keeps a second validation run from becoming "play until it passes".
  - **`val3`, validation seeds 141–180** (1,040 games): **+0.26 [+0.07, +0.44]**, head-to-head 1.79.
    - Per opponent: camper +0.54 [+0.17, +0.89], exploit_v2 +0.36 [+0.06, +0.69], feature +0.35 [−0.04, +0.72], choke +0.21, rusher +0.10, greedy +0.00.

  **Accept rule, validation seeds 101–180 pooled** (80 seed pairs per opponent, 960 paired games):

  | rule | result | pass |
  |---|---|---|
  | 1. gates | lint OK; 0 crashes, 0 time warnings, 0 violations in 2,080 games; max move 0.085 s (greedy_v2 0.104 s), 6 workers | ✓ |
  | 2. pool improvement | **+0.16 [+0.04, +0.28]** | ✓ |
  | 3. no regression > 0.5 | per opponent: camper +0.29 [+0.06, +0.52], rusher +0.17 [−0.03, +0.38], feature +0.13 [−0.11, +0.38], greedy +0.13 [−0.06, +0.33], exploit_v2 +0.11 [−0.11, +0.33], choke +0.10 [−0.12, +0.32]; minimum against past versions: greedy 2.09, greedy_v2 1.65 | ✓ |
  | 4. head-to-head vs greedy_v2 ≥ 1.5 | 1.65 (1.51 / 1.79 per half) | ✓ |
  | 5. confirmation on seeds not used for selection | the screen chose among 3 candidates on tuning seeds; every validation seed was unused; `val3` alone +0.26 [+0.07, +0.44] | ✓ |

- **Conclusions**:
  - **`lab3_shadow` beats greedy_v2 under the accept rule.** The size is uncertain: +0.29 to +0.34 on tuning seeds (2 × 100 seeds), +0.16 [+0.04, +0.28] on 80 validation seeds, +0.05 on the first 40 of them. Plan with about **+0.15 to +0.3 points per game** against this pool.
  - The effect varies a lot between sets of 40 maps. A 40-seed validation can miss a real effect of this size, so future validations should use ≥ 80 seeds.
  - Validation seeds used for decisions so far: 1–20, 21–60, 61–100, 101–180. 120 are left (evaluation.md section 4).
  - **Not done** (needs the user): freezing as `teams/greedy_v3.py` and promoting to `my_team.py`; the release gate (held-out teams, locked test seeds, Linux timing of the belief code).
  - External validity is still the open question: every pool attacker avoids visible ghosts (caveat above).
- **Follow-ups**: E-020 (belief-recalled raid on top of shadowing); a held-out checkpoint as part of the release gate if the user wants to promote.

## E-020 — A raid that the belief calls back, on top of shadowing (2026-10-18)
- **Status**: done (screen). Not adopted.
- **Question**: E-018's raiding defender (P-21) scored more against guards but let attacking teams in. Does it help once the belief (E-019) calls the raid back, and holds it back, while the raider is near our side?
- **Variant**: new file `teams/greedy_lab_v4.py`, a copy of `greedy_lab_v3.py` plus the switch `braid` (P-24), off by default.
  - `RaidDefender` is E-018's raid with two changes. Invader evidence includes a hidden enemy that the belief puts on our side (P-22's test). No raid starts or continues while the raider's expected distance to our side is at most our own way home plus 3 cells (`RECALL_MARGIN`).
  - Each agent still uses only its own observation (Q4).
- **Checks**:
  - Lint OK.
  - Identity: `lab4_off` vs greedy_v2 18/18 (`identity_labv4`); `lab4_shadow` vs `lab3_shadow` 18/18 (`identity_labv4s`).
  - Smoke (`smoke_labv4`, 16 games): 0 crashes. The defender raided a little against camper and exploit_v2 and never against greedy.
- **Setup**: `lab4_braid_shadow` and `lab3_shadow` against `lab3_shadow` / greedy_v2 and the other 6 pool members on **tuning seeds 451–550** (never used before), both colours: 3,000 games, run `scr5`, 6 workers; partly alongside `scr5b`. Windows 11, Python 3.8.10, framework `54cd83c`.
- **Results**: 0 crashes, 0 time warnings, 0 violations; max move 0.152 s (lab4_braid_shadow, with 9 games running at once).
  - Paired `lab4_braid_shadow` − `lab3_shadow`: **−0.01 [−0.06, +0.04]** over 1,400 games.
  - Per opponent: choke +0.14 [+0.05, +0.24], greedy_v2 +0.07, camper +0.02, greedy +0.01, rusher −0.04, exploit_v2 −0.10 [−0.24, +0.06], feature −0.18 [−0.35, −0.02].
  - Head-to-head: 1.38 vs 1.32 for `lab3_shadow`.
  - Same trade-off as E-018, smaller: per game it returns 0.2–0.4 more food and concedes 0.3–1.0 more (e.g. feature: returned 11.1 → 11.3, conceded 8.1 → 8.9).
- **Conclusion**: calling the raid back by belief removes E-018's damage against greedy (−0.20 there on top of greedy_v2, +0.01 here on top of shadowing), but the net stays at zero: feature −0.18 and exploit_v2 −0.10 offset choke +0.14. A raid by the defender is not worth its complexity on top of shadowing. Not adopted; the raid line (P-21, P-24) is closed for now.


## E-021 — Release gate for `greedy_v3` on the locked test seeds; promotion decision (2026-10-18)
- **Status**: done. **greedy_v3 promoted to `my_team.py`.** Rules 1–5 pass; rule 6 had one warning that was shown to be environmental (see below).
- **User decision (2026-10-18)**: `lab3_shadow` becomes `greedy_v3`. "Rerun, and if it outperforms greedy_v2, promote it to `my_team.py`."
- **Variant**: new file `teams/greedy_v3.py`, a copy of `teams/greedy_lab_v3.py` with `shadow='1'` as the default and a corrected header. The only code difference is that default.
  - Lint OK.
  - **Identity**: greedy_v3 vs `lab3_shadow` against baseline, camper, exploit_v2 and greedy_v2 on tuning seeds 1–3, both colours: **24/24 identical** (score and every diagnostic; run `identity_v3`).
- **Pre-registered rule** (written before any test-seed game was played). Promote greedy_v3 to `my_team.py` if and only if all of these hold:
  1. **Gates**: 0 crashes / forfeits, 0 engine time warnings and 0 sentinel violations in every game of greedy_v3, with a max move ≤ 0.5 s.
  2. **Pool**: the paired Δ PPG (greedy_v3 − greedy_v2) over the 6 non-mirror reference-pool members (greedy, feature, camper, rusher, choke, exploit_v2) has a 95% CI lower bound > 0.
  3. **No regression**: for every opponent (pool and held-out) the paired Δ has a CI upper bound > −0.5 (δ).
  4. **Held-out**: the paired Δ over the two held-out teams has a CI upper bound > 0, i.e. no significant regression against blind-written teams. Totals only (T-53).
  5. **Head-to-head**: PPG(greedy_v3 vs greedy_v2) ≥ 1.5.
  6. **Linux timing** (WSL, Python 3.8, `-c`, as E-016): 0 time warnings and max move ≤ 0.5 s, serial and with all CPUs loaded.
- **Setup**:
  - greedy_v3 and greedy_v2 against greedy, feature, camper, rusher, choke, exploit_v2, heldout_a and heldout_b, plus greedy_v3 vs greedy_v2, on **all 100 locked test seeds**, both colours: 3,400 games, run `test1`.
  - **Test-seed use 1 of 3** (evaluation.md section 4).
  - Windows 11, Python 3.8.10, framework `54cd83c`, 6 workers, `--delay-step 0`.
- **Results** (run `test1`, 3,400 games; summary in `eval/results/test1_summary.md`):

  | agent | games | W-T-L | PPG [95% CI] | crashes / time warnings / violations | max move |
  |---|---|---|---|---|---|
  | greedy_v3 | 1,800 | 999-232-569 | **1.79** [1.71, 1.88] | 0 / 0 / 0 | 0.091 s |
  | greedy_v2 | 1,800 | 867-196-737 | 1.55 [1.49, 1.63] | 0 / 0 / 0 | 0.098 s |

  **Paired greedy_v3 − greedy_v2 per opponent** (200 games each):

  | opponent | greedy_v3 | greedy_v2 | paired Δ [95% CI] |
  |---|---|---|---|
  | camper | 2.06 | 1.67 | +0.39 [+0.17, +0.62] |
  | feature | 2.10 | 1.83 | +0.27 [−0.01, +0.53] |
  | choke | 1.65 | 1.40 | +0.26 [+0.01, +0.49] |
  | greedy | 2.17 | 1.91 | +0.26 [+0.04, +0.47] |
  | rusher | 2.07 | 1.84 | +0.23 [+0.01, +0.43] |
  | exploit_v2 | 1.75 | 1.60 | +0.15 [−0.07, +0.36] |
  | heldout_b (held-out) | 1.35 | 1.00 | +0.35 [+0.11, +0.59] |
  | heldout_a (held-out) | 1.44 | 1.46 | −0.02 [−0.26, +0.21] |

  - **Generalisation gap** (evaluation.md section 4; mean over the 6 non-mirror pool members vs mean over the 2 held-out teams, test seeds):
    - greedy_v3: 1.97 vs 1.40, R ≈ 29%;
    - greedy_v2: 1.71 vs 1.23, R ≈ 28%.
    - The gain carries over to the blind-written teams at a similar size (+0.17 held-out vs +0.26 pool). The gap itself is unchanged.
  - **Linux / Python 3.8** (WSL Ubuntu 24.04, CPython 3.8.20, `-c` with real `SIGALRM` limits, as E-016). greedy_v3 against greedy, feature, camper, rusher, choke and exploit_v2, both colours, on tuning seeds 551–565 (serial) and 566–580 (`--jobs 12`). Runs `wsl_serial_v3`, `wsl_loaded_v3`; the repo was mirrored with rsync first.

    | pass | games | max move | 99th pct of per-game max | max p95 | max startup | moves > 0.5 s | engine warnings / timeouts / crashes |
    |---|---|---|---|---|---|---|---|
    | serial | 180 | 0.035 s | 0.029 s | 0.0016 s | 0.37 s | 0 | **1** / 0 / 0 |
    | loaded (12 jobs) | 180 | 0.105 s | 0.089 s | 0.0049 s | 1.13 s | 0 | 0 / 0 / 0 |

  - **The one warning** (serial game 36, seed 87250538, greedy_v3 red vs feature):
    - The engine's 1 s clock (`game.py`) covers the engine's `observation_function` deep copy plus the whole `get_action` call, including the sentinel's wrapper. In that game our `choose_action` never took more than 0.002 s. The game took 2.7 s of wall time against a median of 1.1 s.
    - The agents are deterministic, so the same game was replayed 5 times in WSL, serially (runs `wsl_rep36_1..5`): the same score (15) every time, 1.1–1.2 s of wall time, **0 warnings**, max move 0.002–0.003 s.
    - A computation of ours would have repeated, so this was a one-off stall of the WSL process (scheduler or VM), not our code.
    - **Deviation from the pre-registered rule 6**, recorded openly: rule 6 said "0 time warnings". It failed by one warning, which the replays show was not caused by the agent. The promotion went ahead on that basis, under the user's instruction ("if it outperforms greedy_v2, promote it"). The tournament allows 2 warnings per game before a forfeit (`capture.py`).
- **Pre-registered rule**:

  | rule | result | pass |
  |---|---|---|
  | 1. gates | 0 crashes, 0 time warnings, 0 violations in 1,800 games; max move 0.091 s | ✓ |
  | 2. pool, 6 members | **+0.26 [+0.15, +0.36]** | ✓ |
  | 3. no regression > 0.5 | worst: heldout_a −0.02 [−0.26, +0.21] | ✓ |
  | 4. held-out, CI upper bound > 0 | **+0.17 [−0.00, +0.33]** | ✓ |
  | 5. head-to-head vs greedy_v2 ≥ 1.5 | 1.56 | ✓ |
  | 6. Linux timing | max move 0.105 s with all CPUs busy; 1 environmental warning in the serial pass (above) | ✓ with the deviation noted |

- **Promotion**:
  - `my_team.py` is now `teams/greedy_v3.py` with a different header only. The bodies were compared with `diff`: identical.
  - Lint OK. Identity: the `submission` entry vs greedy_v3 against baseline, camper and exploit_v2 on tuning seeds 1–3, both colours, **18/18** (run `identity_submission_v3`).
  - Smoke from the repo root (`capture.py -r ../../../my_team.py -b baseline_team -q -c -l RANDOM13`): won by 16, no warning.
  - `eval/league.json`: greedy_v3 is the incumbent of the reference pool, which now has 8 members (greedy_v2 stays as the previous incumbent).
- **Release gate status of greedy_v3**: accept rule ✓ (E-019); ≥ 200 own games ✓ (1,800 + 360 + 24); Linux timing ✓ (deviation noted); locked test seeds ✓ (use 1 of 3); held-out on test seeds ✓.
- **Caveat**: all numbers are against our own pool and two blind-written teams. The field at the test run on 2026-11-23 is still unknown (evaluation.md section 9).


## E-022 — Decision trace: which rule produced each move; rule profiles of the three picks (2026-10-18)
- **Status**: done.
- **Question** (user request): can every move of our submissions be explained rule by rule, and how much of the game does each rule take up?
- **Tool** (local analysis only, never submitted):
  - `eval/trace_team.py` wraps one of our team files, like the sentinel. It wraps our agents' decision methods on the instances (`follow_entry`, `break_standoff`, `retreat`, `evade`, `bfs_action`, `keep_distance`, `intercept_cell`, `shadow_post`, `next_patrol_point`). The wrappers pass calls and results through unchanged. After each move it names the rule from the calls made and from the agent's own observation (the go-home reasons are re-evaluated).
  - `eval/trace_game.py game` prints one game move by move and saves its replay. `trace_game.py profile` counts rule shares over many games and refuses test seeds; `--check-run` compares final scores with an `evaluate.py` run of the same games.
  - Outputs go to `eval/traces/` (gitignored).
- **Pass-through check**: the traced games ended with exactly the scores the evaluation recorded:
  - greedy_v3 **24/24** (vs run `identity_v3`);
  - greedy_v2 **18/18** (`identity_labv3`);
  - greedy **18/18** (`identity_lab`).
- **Rule profiles**: each pick against greedy, feature, camper, rusher, choke and exploit_v2 on **tuning seeds 581–600**, both colours, 240 games each. 0 engine warnings, 0 trace errors. Files `eval/results/trace_profile_<team>.md`.

  | attacker rule | greedy | greedy_v2 | greedy_v3 | | defender rule | greedy | greedy_v2 | greedy_v3 |
  |---|---|---|---|---|---|---|---|---|
  | eat | 44.7% | 45.5% | 41.9% | | patrol | 54.2% | 51.1% | 16.9% |
  | no-safe-food (v1: waiting) | 33.4% | – | – | | shadow | – | – | 50.8% |
  | entry / switch-entry | – | 24.2% / 1.8% | 25.4% / 2.4% | | chase | 24.5% | 20.3% | 14.3% |
  | blocked | – | 4.5% | 6.5% | | cut-off | – | 5.7% | 3.5% |
  | home | 11.8% | 11.6% | 11.0% | | last-evidence | 11.3% | 12.2% | 7.4% |
  | evade (incl. cut off) | 10.1% | 12.3% | 12.7% | | scared | 10.0% | 10.6% | 7.2% |
  | (points per game in these games) | 1.40 | 1.54 | 1.90 | | | | | |

- **Findings**:
  - The trace makes three behaviours visible that no earlier diagnostic separated:
    1. **Cut off on the enemy side** (`evade` without a go-home reason): about 12% of v2/v3 attacker moves. A ghost stands between our Pacman and home, there is no safe food, and the attacker backs away, often into a corner where it stops.
    2. **Relocating along our border**: 25% of v2/v3 attacker moves, up to 38% against exploit_v2 and 33% against camper.
    3. **v1's waiting at the border**: 47% / 52% of its moves against camper / exploit_v2.
  - The attacker code of v2 and v3 is identical, yet in v3 it eats slightly less (45.5% → 41.9%) and is blocked slightly more (4.5% → 6.5%). A likely cause [untested] is shared sight (T-56): the shadowing defender reveals enemy ghosts to our attacker.
  - The behaviour pages built on this are in `docs/picks/` (one per version that has been in `my_team.py`).
- **Follow-ups (ideas)**: a use for the "cut off" time (e.g. a capsule or a different exit, H-S06); fewer relocation walks against guards (the breaker's entry choice).

## E-023 — Re-check: which fields of a hidden opponent reach our observation (2026-10-22)
- **Status**: done.
- **Question**: the professor's answer to Q3 (rules.md) depends on whether hidden opponents' `is_pacman`, `num_carrying` and `scared_timer` are really available. Is E-000's finding still true, and where in the engine does it come from?
- **Variant**: `eval/probe_hidden_fields.py` (local only, never submitted). It builds the true initial state of `RANDOM13`, sets blue agent 1's `is_pacman`, `num_carrying`, `scared_timer` and `num_returned` on the **true** state, and calls the engine's own `make_observation(0)`, which is what red agent 0 receives every turn.
- **Setup**: Windows 11, Python 3.8.10, framework commit `54cd83c`. Upstream `aig-upf/pacman-contest` `main` was still `54cd83c` on 2026-10-22 (`git ls-remote`), so this is the code the tournament would run if it uses `main` [untested assumption].
- **Results**: agent 1 is 44 cells (Manhattan) from the nearest red agent, so it is hidden.

  | field | true | in agent 0's observation |
  |---|---|---|
  | position | (32, 15) | `None` |
  | `is_pacman` | True | True |
  | `num_carrying` | 7 | 7 |
  | `scared_timer` | 23 | 23 |
  | `num_returned` | 4 | 4 |

- **Where it comes from** (engine code, read-only):
  - `capture.py:254-278` `GameState.make_observation`: deep-copies the state, then for each opponent out of sight sets **only** `configuration = None` (line 277). No other field is touched.
  - `game.py:157-163` `AgentState.copy`: the copy keeps `scared_timer`, `num_carrying`, `num_returned` and `is_pacman` (via the constructor, line 158).
  - `capture.py:128-129` `get_agent_state` returns the `AgentState` as is; `capture_agents.py:136-138` `observation_function` is what calls `make_observation` each turn.
- **Conclusion**: [verified] these fields are available for hidden opponents through the public API; E-000 still holds. `my_team.py` (greedy_v3) reads them only for our own agents.
- **Follow-ups**: confirm to the professor (Q3); a candidate that uses the fields behind `USE_HIDDEN_OPPONENT_FLAGS`.

## E-024 — greedy_v3 (`my_team.py`) vs a friend's team, `friend_andy` (2026-10-23)
- **Status**: done.
- **Question**: how does our submission do against an outside team (a friend's agent, `friends/andy/my_team.py`)?
- **Setup**: `eval/evaluate.py play --candidate submission --vs friend_andy --seeds tuning --n-seeds 250 --jobs 6 --run friend_andy_vs_v3`, i.e. 250 tuning seeds × 2 colours = 500 games, with `-c`. `my_team.py` = greedy_v3 at commit `6e419f9`, framework `54cd83c`, Windows 11, Python 3.8.10. Before running, the friend's file was checked only for safety (imports, file/process calls, `random.seed`); its strategy was not studied. A visual game on `RANDOM13` was also played (us red): Andy won by 4.
- **Results**:

  | agent | games | W-T-L | PPG [95% CI] | win % [exact CI] | avg margin | crash / warnings / violations | max move s |
  |---|---|---|---|---|---|---|---|
  | submission (greedy_v3) | 500 | 329-62-109 | 2.10 [1.96, 2.22] | 66 [61, 70] | +5.2 | 0 / 0 / 0 | 0.080 |
  | friend_andy | 500 | 109-62-329 | 0.78 [0.66, 0.90] | 22 [18, 26] | −5.2 | 0 / 0 / – | 0.154 |

  | side we play | W | T | L |
  |---|---|---|---|
  | red | 165 | 28 | 57 |
  | blue | 164 | 34 | 52 |

  | per game | returned | conceded | deaths | kills | max carried | 28-finishes |
  |---|---|---|---|---|---|---|
  | submission | 12.1 | 6.9 | 1.49 | 1.66 | 7.4 | 7 |
  | friend_andy | 6.9 | 12.1 | 1.66 | 1.49 | 4.3 | 0 |

- **Conclusion**: [verified] greedy_v3 beats `friend_andy` clearly and equally on both colours. It still loses 22% of the games, so the 109 losses are worth classifying (`eval/replay_probe.py`) for weaknesses. The seeds are tuning seeds, so no validation or test budget was used.

## E-025 — Enemy-state agents: hidden fields, shared belief, endgame, intent model (2026-10-28)
- **Status**: done. Pre-registered before any game was played; `lab5_smart` **passes the accept rule** (validation seeds 181–220: +0.25 [+0.11, +0.40]); not promoted (user decision, release gate open).
- **Question** (user request, 2026-10-28): do the hidden-opponent fields (Q3), a shared team belief (Q4), score-aware endgame roles, and a model of what each enemy is doing (sonar tracking + goal recognition, with greedy reactions) raise greedy_v3's points per game? Which combination is best?
- **Research first**: heuristics.md Part D (two literature agents, 2026-10-28) gives the sources for each switch.
- **Variants**: new file `teams/greedy_lab_v5.py`, a copy of `teams/greedy_v3.py` plus the switches below. All are off by default, so `lab5_off` must play exactly like greedy_v3. Every read of a hidden enemy's fields goes through one method behind the module constant `USE_HIDDEN_OPPONENT_FLAGS` (rules.md Q3).

  | switch | heuristic | what it does | needs |
  |---|---|---|---|
  | `flags` (#1) | H-S14 | belief: zero cells on the wrong half (`is_pacman`); the enemy whose `num_carrying` rose ate the vanished food; respawn when carrying → 0 without `num_returned` rising, or `scared_timer` ≥ 2 → 0. Raider = the enemy that is a Pacman now (else the last one). Enemy scared state from its exact `scared_timer` | — |
  | `hunt` (#2, P-22) | H-S01 | with no invader in sight, chase the most likely cell of a hidden enemy on our side. With `flags`, "on our side" is `is_pacman` (exact) instead of belief mass ≥ 0.5 (57% precision, E-019) | — |
  | `shared` (#3) | H-S15 | one team belief, updated at both agents' turns. Only the enemy that just moved, `(index − 1) % 4`, is spread; both agents' sonar is applied; a vanished food dot pins that enemy. Respawns are detected once per team update | — |
  | `endgame` (#4, P-17c) | H-S27 | in the last 40 own moves: ahead → both defend; behind → both attack, and a carrier banks as soon as its food would take the lead | — |
  | `directed` | H-S17 | belief motion model: a neighbour that moves an enemy towards its goal gets weight 1 + 2 instead of 1. Goal: our nearest food while it forages, its home when it returns (carrying ≥ the amount it banked at before, default 5). Ghosts keep the random walk. No cell's weight drops to 0 (T-54) | `flags` |
  | `open_goal` | H-S24 | the attacker ignores `return_at` while no enemy can reach it before it gets home (pessimistic 10% quantile of each enemy's belief distance; scared timers count) + 4 moves | `flags` |
  | `guard` | H-S16 | defender: an invader in sight or hidden (`is_pacman`) is a target; prefer the one carrying most. A hidden returning invader → the border cell across its most likely exit, if we get there first; a hidden forager → the food it most likely eats next, if we get there first; otherwise P-22's chase of its most likely cell | `flags` |
  | `recall` | H-S26 | while both enemies are Pacmen and our attacker is on our side (or carries nothing within 3 of home), it defends too; the two defenders split the invaders by min-max distance | `flags` |

- **Entries** (`eval/league.json`):

  | entry | switches |
  |---|---|
  | `lab5_off` | none (identity check) |
  | `lab5_flags` | flags |
  | `lab5_flags_hunt` | flags + hunt |
  | `lab5_shared` | shared |
  | `lab5_endgame` | endgame |
  | `lab5_track` | flags + directed (the sonar-tracking agent) |
  | `lab5_open` | flags + open_goal |
  | `lab5_guard` | flags + guard |
  | `lab5_recall` | flags + recall |
  | `lab5_intent` | flags + directed + open_goal + guard + recall (the enemy-intent agent) |
  | `lab5_all` | flags + shared + endgame + directed + open_goal + guard + recall |
  | `lab5_smart` | chosen from the screen by the rule below |

- **Checks before the screen**: lint; smoke vs baseline; identity `lab5_off` vs greedy_v3 (baseline, camper, exploit_v2 on tuning seeds 1–3, both colours: must be 18/18 identical); belief probe (accuracy against true positions, `eval/belief_probe/`, tuning seeds 431–435 against the E-019 opponents) for the perception switches.
- **Screen**: tuning seeds 151–200 (50 seeds, both colours) against the 8-member reference pool, with greedy_v3 in the same run, so every Δ is paired.
- **Pre-registered rule for `lab5_smart`**:
  1. `shared`, `endgame` (independent): include if Δ(entry) vs greedy_v3 > 0.
  2. `hunt`, `directed`, `open_goal`, `guard`, `recall` (need `flags`): include if Δ(entry) − Δ(`lab5_flags`) > 0. `hunt` and `guard` are alternatives: if both qualify, keep the larger gain.
  3. `flags`: include if Δ(`lab5_flags`) > 0 or any component of rule 2 is included.
  4. Exclude a component whose entry has any gate failure (crash, time warning, sentinel violation, max move > 0.5 s) or a per-opponent Δ below −0.3.
- **Decision run**: `lab5_smart` on validation seeds 181–220 (40 seeds, fresh) against the pool, paired with greedy_v3, and the accept rule of evaluation.md section 2. No test seeds; promotion is a user decision.
- **Diagnostic, not a decision input**: greedy_v3, `lab5_all` and `lab5_smart` against `friend_aljaz_1` on tuning seeds 1–100, the seeds of the unlogged 2026-10-24 run (`eval/results/friend_aljaz_vs_v3.jsonl`), where greedy_v3 scored 0.64 points per game.
- **Setup**: Windows 11, Python 3.8.10, framework `54cd83c`, `my_team.py` = greedy_v3 at commit `6e419f9`; `--jobs 8` on 12 logical CPUs.
- **Checks** (all before the screen):
  - Lint OK (`eval/check_rules.py teams/greedy_lab_v5.py`).
  - **Smoke** (`smoke_labv5`): all 11 entries vs baseline and camper on tuning seeds 1–2, both colours, 88 games: 0 crashes, 0 time warnings, max move 0.068 s.
  - **Identity** (`identity_labv5`): `lab5_off` vs greedy_v3 against baseline, camper, exploit_v2 on tuning seeds 1–3, both colours: **18/18 identical** (score and every sentinel diagnostic of both teams).
  - **Branches fire**: a smoke comparison on score + Pacman moves + returned food could not tell `hunt` / `directed` / `recall` from `flags` (8/8 equal), because it does not see the defender's path. Counted directly in one game vs baseline (RANDOM27904464, a local wrapper in the scratchpad): the hunt suspect was found 23 times, guard chose a target 39 times, `goal_open` was open in 67 of 75 checks, the directed goal field was used 23 times (only for hidden enemy Pacmen). `recall` cannot fire against baseline or camper: neither ever has both agents on our side.
  - **Belief accuracy** (`eval/belief_probe/`, now with `BELIEF_LAB=teams/greedy_lab_v5.py`; the defender's belief against the opponents' true positions; tuning seeds 431–435 against greedy_v2, exploit_v2, rusher, feature, camper, choke, both colours, 60 games per row; files `rows_greedy_lab_v5_*.json`):

    | variant | hidden enemy-turns | truth ruled out | mean p(true cell) | mean expected distance to truth | median distance, most likely cell → truth | "on our side" recall | precision | defender max move |
    |---|---|---|---|---|---|---|---|---|
    | greedy_v3 (`shadow=1`) | 15,396 | 0.0% | 0.16 | 7.5 | 4 | 66% | 58% | 0.034 s |
    | `flags` | 14,840 | 0.0% | 0.17 | 6.9 | 4 | **100%** | **100%** | 0.032 s |
    | `shared` | 15,461 | 0.0% | 0.24 | 5.5 | **2** | 76% | 67% | 0.039 s |
    | `flags` + `shared` | 14,898 | 0.0% | **0.26** | **5.2** | **2** | **100%** | **100%** | 0.019 s |
    | `flags` + `directed` | 14,840 | 0.0% | 0.18 | 6.8 | 4 | 100% | 100% | 0.032 s |
    | `flags` + `shared` + `directed` | 14,898 | 0.0% | 0.26 | 5.2 | 2 | 100% | 100% | 0.030 s |

    - The greedy_v3 row reproduces E-019 (0.16 / 7.5 / 4 / 9 last-seen / 66% / 57%), which checks the modified tool.
    - [verified] **Sharing halves the error** of the most likely cell (4 → 2 steps) and raises the probability on the true cell by half (0.16 → 0.24). **The fields make the side exact.** The directed motion model adds almost nothing measurable (0.17 → 0.18): it acts only on hidden enemy Pacmen, a small share of the hidden turns.
    - The truth is never ruled out in any variant, so the side constraint, the respawn rules and the exact food attribution of `shared` introduced no false exclusions (T-54, T-55).
- **Screen results** (run `scr_labv5`: tuning seeds 151–200, both colours, 8,700 games):
  - **Gates**: 0 crashes, 0 time warnings, 0 sentinel violations, 0 moves over the 0.5 s budget. Max move per entry 0.065–0.198 s; greedy_v3 0.310 s (all under 8 parallel jobs).
  - **Points** (paired over the 700 games against the 7 pool members other than greedy_v3; head-to-head = 100 games against greedy_v3):

    | entry | paired Δ vs greedy_v3 [95% CI] | exact Δ | worst opponent | best opponent | head-to-head |
    |---|---|---|---|---|---|
    | `lab5_open` | **+0.17 [+0.05, +0.29]** | +0.169 | rusher +0.01 | exploit_v2 +0.39 | 1.63 |
    | `lab5_all` | +0.14 [+0.01, +0.26] | +0.137 | rusher −0.05 | exploit_v2 +0.28 | 1.67 |
    | `lab5_track` | +0.12 [+0.01, +0.23] | +0.120 | rusher −0.19 | exploit_v2 +0.29 | 1.63 |
    | `lab5_flags` | +0.11 [+0.00, +0.22] | +0.111 | rusher −0.19 | exploit_v2 +0.29 | 1.63 |
    | `lab5_recall` | +0.11 [+0.00, +0.22] | +0.111 | rusher −0.19 | exploit_v2 +0.29 | 1.63 |
    | `lab5_flags_hunt` | +0.11 [−0.00, +0.22] | +0.106 | rusher −0.15 | exploit_v2 +0.24 | 1.49 |
    | `lab5_intent` | +0.10 [−0.03, +0.22] | +0.103 | rusher −0.07 | exploit_v2 +0.25 | 1.68 |
    | `lab5_guard` | +0.03 [−0.09, +0.15] | +0.029 | rusher −0.27 | feature +0.21 | 1.60 |
    | `lab5_endgame` | +0.01 [−0.02, +0.03] | +0.006 | choke −0.03 | greedy +0.06 | 1.35 |
    | `lab5_shared` | +0.00 [−0.08, +0.08] | +0.003 | choke −0.10 | exploit_v2 +0.12 | 1.38 |

  - **Diagnostics** (team totals per game against the same 7 opponents):

    | entry | returned | conceded | deaths | kills | max carried | Pacman moves | standoff moves |
    |---|---|---|---|---|---|---|---|
    | greedy_v3 | 12.0 | 8.2 | 1.02 | 0.76 | 7.4 | 124 | 239 |
    | `lab5_flags` | 11.4 | **6.6** | 0.97 | 0.69 | 7.2 | 121 | 256 |
    | `lab5_flags_hunt` | 11.4 | 6.6 | 1.00 | 0.65 | 7.2 | 123 | 254 |
    | `lab5_shared` | 12.0 | 7.8 | 1.03 | 0.79 | 7.5 | 125 | 241 |
    | `lab5_endgame` | 12.1 | 8.6 | 0.98 | 0.76 | 7.4 | 122 | 238 |
    | `lab5_track` | 11.4 | 6.6 | 0.97 | 0.69 | 7.3 | 121 | 256 |
    | `lab5_open` | **12.0** | **6.5** | 0.94 | 0.63 | **8.9** | 117 | 259 |
    | `lab5_guard` | 11.4 | 6.7 | 0.95 | 0.67 | 7.2 | 121 | 259 |
    | `lab5_recall` | 11.4 | 6.6 | 0.97 | 0.69 | 7.2 | 121 | 256 |
    | `lab5_intent` | 11.9 | 6.4 | 0.94 | 0.60 | 8.9 | 117 | 264 |
    | `lab5_all` | 11.5 | 6.3 | 0.90 | 0.59 | 8.7 | 114 | 267 |

  - **Reading** (screen on tuning seeds; with 10 entries, one or two positive CIs are expected by chance):
    - **`flags` works through the defence**: food conceded falls by a fifth (8.2 → 6.6), because the raider identity is now exact (E-025 probe: 58% → 100%). Our own returns fall a little (12.0 → 11.4) and standoff moves rise (239 → 256), plausibly T-56 again: a better-placed defender reveals more of their guards to our attacker [untested].
    - **`open_goal` recovers the attack**: on top of `flags` it carries more per trip (max 8.9) and returns food back to greedy_v3's level, with fewer deaths (0.94). It has the only clearly positive CI, and no opponent below +0.01.
    - **`recall` never fired**: 800/800 games give `lab5_recall` exactly `lab5_flags`'s points. No pool member ever has both agents on our side (as E-014 found), so the screen cannot test it → diagnostic run below.
    - **`shared`** improves the belief (E-025 probe) but not the points (+0.003): the defender's shadow post seldom changes with a 2-step better estimate [untested].
    - **`endgame`** changes little (+0.006): most games are decided before the last 40 moves.
    - **`hunt`** and **`guard`** do not add to `flags`; guard costs against rusher (−0.27), the capsule rusher whose scared windows a chasing defender walks into [untested].
  - **Pre-registered selection** (rules 1–4):

    | component | test | value | included |
    |---|---|---|---|
    | `flags` | Δ > 0 | +0.111 | yes |
    | `shared` | Δ > 0 | +0.003 | yes (noise-level margin) |
    | `endgame` | Δ > 0 | +0.006 | yes (noise-level margin) |
    | `directed` | Δ(track) − Δ(flags) > 0 | +0.009 | yes (noise-level margin) |
    | `open_goal` | Δ(open) − Δ(flags) > 0 | +0.057 | yes |
    | `hunt` | Δ(flags_hunt) − Δ(flags) > 0 | −0.006 | no |
    | `guard` | Δ(guard) − Δ(flags) > 0 | −0.083 | no |
    | `recall` | Δ(recall) − Δ(flags) > 0 | 0.000 (never fired) | no |

    No gate failure and no opponent Δ below −0.3, so rule 4 excluded nothing. **`lab5_smart` = flags + shared + endgame + directed + open_goal** (league entry added). Smoke (`smoke_labv5_smart`): 4/4 vs baseline, 0 warnings, max move 0.040 s.
- **Diagnostic: double attackers** (run `diag_labv5_double`, user request 2026-10-28; not a decision input): greedy_v3, `lab5_flags`, `lab5_recall`, `lab5_guard`, `lab5_intent`, `lab5_all` against `double_attack` (league specialist, 2 × greedy attacker) and `friend_aljaz_1` on the screen's tuning seeds 151–200, both colours, 1,200 games. Gates: 0 crashes, 0 warnings, max move 0.128 s (ours).

  | entry | Δ vs greedy_v3 [95% CI], 200 games | vs double_attack | vs friend_aljaz_1 |
  |---|---|---|---|
  | `lab5_flags` | +0.01 [−0.17, +0.20] | −0.02 | +0.05 |
  | `lab5_recall` | **−0.49 [−0.70, −0.27]** | **−0.58 [−0.90, −0.27]** | **−0.40 [−0.67, −0.12]** |
  | `lab5_guard` | −0.12 [−0.37, +0.12] | −0.08 | −0.16 |
  | `lab5_intent` | −0.29 [−0.53, −0.04] | −0.51 | −0.08 |
  | `lab5_all` | −0.18 [−0.43, +0.07] | −0.33 | −0.04 |

  | entry | opponent | returned | conceded | deaths | kills | our Pacman moves |
  |---|---|---|---|---|---|---|
  | greedy_v3 | double_attack | 19.5 | 14.7 | 0.22 | 1.43 | 207 |
  | `lab5_recall` | double_attack | **12.6** | 14.3 | 0.70 | 1.73 | 138 |
  | greedy_v3 | friend_aljaz_1 | 18.0 | 21.8 | 1.15 | 2.14 | 151 |
  | `lab5_recall` | friend_aljaz_1 | **12.0** | 21.6 | 1.26 | 2.70 | 97 |

  - [verified on these games] **`recall` is harmful exactly where it was meant to help.** Against a double attack it cuts our own returns by a third (19.5 → 12.6; 18.0 → 12.0) and barely reduces theirs (14.7 → 14.3; 21.8 → 21.6). The second defender gets more kills (1.43 → 1.73) but does not stop their scoring. When both enemies attack, their half is empty, and our attacker scores more by staying there.
  - **Lesson for SM-9 / SM-13** (proposals.md): against double attackers, race them; do not pull the attacker back.
  - `lab5_smart` contains none of `recall`, `guard`, `hunt`.
  - friend_aljaz_1 remains the strongest opponent we have: greedy_v3 0.88 points per game on these seeds (0.64 on tuning 1–100, the 2026-10-24 run).

- **Decision run** (run `val_labv5_smart`: **validation seeds 181–220**, unused before, 40 seeds × 2 colours against the pool; 1,200 games):

  | opponent | games | PPG `lab5_smart` | PPG greedy_v3 | paired Δ [95% CI] |
  |---|---|---|---|---|
  | camper | 80 | 1.96 | 1.81 | +0.15 [−0.15, +0.46] |
  | choke | 80 | 1.99 | 1.66 | +0.33 [−0.01, +0.66] |
  | exploit_v2 | 80 | 2.11 | 1.80 | +0.31 [+0.05, +0.59] |
  | feature | 80 | 2.44 | 2.16 | +0.28 [+0.03, +0.54] |
  | greedy | 80 | 2.27 | 1.85 | +0.42 [+0.12, +0.71] |
  | greedy_v2 | 80 | 1.93 | 1.93 | +0.00 [−0.33, +0.34] |
  | rusher | 80 | 2.30 | 2.05 | +0.25 [−0.09, +0.59] |
  | **pool (560 paired games)** | | | | **+0.25 [+0.11, +0.40]** |

  | team totals per game (all 640 games each) | returned | conceded | deaths | kills | max carried |
  |---|---|---|---|---|---|
  | greedy_v3 | 10.0 | 7.4 | 0.96 | 0.59 | 6.8 |
  | `lab5_smart` | 9.9 | **6.5** | 0.95 | 0.53 | 7.6 |

  **Accept rule** (evaluation.md section 2):

  | condition | result | pass |
  |---|---|---|
  | 1. gates: lint; 0 crashes, warnings, violations; max move ≤ 0.5 s | lint OK; 0 / 0 / 0 in 1,200 games (and in the 800 screen games); max move 0.151 s (8 parallel jobs) | ✓ |
  | 2. paired pool Δ > 0 with CI lower bound > 0, validation seeds, ≥ 40 seed-pairs per opponent | **+0.25 [+0.11, +0.40]**, 40 seed-pairs each | ✓ |
  | 3. no opponent with CI upper bound ≤ −0.5; past versions not worse by > 0.5 | worst greedy_v2 +0.00 [−0.33, +0.34]; greedy +0.42, greedy_v2 +0.00 | ✓ |
  | 4. head-to-head vs greedy_v3 ≥ 1.5 | **1.59** (80 games) | ✓ |
  | 5. confirmation on seeds not used for selection | the selection used tuning seeds 151–200 only; validation 181–220 is fresh, so this run is that confirmation | ✓ |

- **Diagnostic, not a decision input** (user instruction 2026-10-28: decisions must not rest on one friend's team, which may simply counter us):

  | opponent | seeds | run | greedy_v3 PPG | `lab5_all` PPG | `lab5_smart` PPG | `lab5_smart` − greedy_v3 [95% CI] |
  |---|---|---|---|---|---|---|
  | friend_aljaz_1 | tuning 1–100 (pre-registered) | `diag_labv5_aljaz` | 0.70 | 0.75 | **1.06** | +0.36 [+0.14, +0.58] |
  | double_attack | tuning 151–200 | `diag_labv5_double` + `diag_labv5_smart_double` | 2.05 | 1.72 | **2.64** | +0.59 [+0.29, +0.89] |

  - Against friend_aljaz_1, `lab5_smart` returns less food than greedy_v3 (15.6 vs 17.5) but ends more games itself by returning 28 (24 vs 9 of 200) and concedes a little less (21.7 vs 22.8).
  - greedy_v3 scored 0.70 here and 0.64 in E-026 on the same seeds and code. Our agents are deterministic, so friend_aljaz_1 probably is not (e.g. a time-limited search) [untested inference]. Its numbers carry extra noise.
  - Gates: 0 crashes, 0 warnings; our max move 0.107 s.
- **Conclusion**: [verified on validation seeds 181–220] **`lab5_smart` passes the accept rule** against greedy_v3: +0.25 [+0.11, +0.40] points per game over the pool, head-to-head 1.59. Its gain comes mainly from defence (food conceded 7.4 → 6.5 per game) at equal returns. The screen attributes it to `flags` (exact raider and side) and `open_goal` (carry more when nobody can catch us). `shared`, `endgame` and `directed` entered on noise-level margins (< +0.01 each).
- **Not done yet (release gate, user decision)**: Linux / Python 3.8 timing under load (E-016 recipe); one locked test-seed run against the pool **and the held-out teams**; promotion to `my_team.py`. Optional Occam check before that: `lab5_open` (2 switches) vs `lab5_smart` (5 switches) on further validation seeds, since three of smart's parts showed no measurable effect.

## E-026 — greedy_v3 (`my_team.py`) vs a friend's five compiled teams, `friend_aljaz_1..5` (2026-10-24; logged 2026-10-28)
- **Status**: partial (interrupted). The run stopped after 411 games: aljaz_1 and aljaz_2 complete, aljaz_3 has 11 games, aljaz_4 and aljaz_5 none. Logged afterwards from `eval/results/friend_aljaz_vs_v3.jsonl` because E-025 relies on it.
- **Question**: how does our submission do against a friend's agents (`friends/aljaz_1-5_windows_x64_python38/`, compiled Cython `.pyd` for Windows x64 / Python 3.8, received 2026-10-23)?
- **Setup**: `--candidate submission --vs friend_aljaz_1 … --seeds tuning --n-seeds 100`, i.e. tuning seeds 1–100, both colours, with `-c`. `my_team.py` = greedy_v3. The binaries were checked only with a strings scan (league.json notes); their strategy was not studied, and they can only run on Windows / Python 3.8.
- **Results**:

  | opponent | games | greedy_v3 W-T-L | greedy_v3 PPG | opponent food returned per game | opponent 28-finishes |
  |---|---|---|---|---|---|
  | friend_aljaz_1 | 200 | 41-5-154 | **0.64** | 22.9 | 71 |
  | friend_aljaz_2 | 200 | 108-21-71 | 1.73 | 13.7 | 11 |
  | friend_aljaz_3 | 11 | 5-0-6 | 1.36 | 18.8 | 1 |

  Gates: 0 crashes, 0 time warnings for both sides; max move 0.058 s (ours), 0.300 s (aljaz_2).
- **Conclusion**: [verified] friend_aljaz_1 is the strongest opponent we have met. It beats greedy_v3 77% of the time, mostly by scoring fast: 22.9 food per game, 71 of 200 games ended by returning 28. It is not in the reference pool. aljaz_4 and aljaz_5 are untested.

## E-027 — Overnight session setup: lab v6, reference run, identity, tooling (2026-11-07)
- **Status**: done.
- **Question** (user request, 2026-11-07 23:20): build and test width-based planning (IW / BFWS / novelty) and RL-based heuristics for the greedy agents (per-map modes, greedy + learned modules), autonomously overnight. This entry records the shared setup; the experiments are E-028 onwards.
- **Research first** (two research agents, reports in the repo): `docs/research/width_planning.md` (IW(k), Rollout IW, p-IW, BFWS, π-IW; Ms Pac-Man evidence; no CTF write-up uses width-based planning; LAPKT has no Windows / Python 3.8 wheel after 0.1.8 and needs PDDL, so it is unusable at runtime) and `docs/research/rl_and_modes.md` (algorithm selection, CMA-ES, student RL reports; re-analysis of E-025 data: per-map best-mode labels are noise, oracle +0.20 but cross-validated −0.03).
- **New file** `teams/greedy_lab_v6.py`: lab5's code with lab5_smart's switches (flags, shared, endgame, directed, open_goal) as defaults, plus new switches, all off by default (header lists them): `plan*` (width-based planner), `focus` / `focus_w` / `fw_*` (food-choice modes and a linear food policy), `formation` / `form_lead`, and `threat_dist`, `open_margin`, `standoff_moves` exposed for tuning. Options were added during the night only as new, default-off switches; identity of earlier entries was re-checked after each change (replays identical).
- **Identity** (`n1_identity6`): `lab6_off` vs `lab5_smart` against baseline, camper, exploit_v2 on tuning seeds 1–3, both colours: **18/18 identical** (score and every sentinel diagnostic).
- **Reference run** (`n1_base`): lab5_smart and greedy_v3 against the 8-member pool on tuning seeds 261–320 (`--seed-offset 260`, 60 seeds, both colours). lab5_smart − greedy_v3 paired over 840 games: **+0.38 [+0.29, +0.49]**, every opponent positive (camper +0.30 … greedy +0.54); lab5_smart 2.17 PPG. Gates: 0 crashes, 0 warnings.
- **Tooling** (local only): `eval/league_add.py` (append league entries without reformatting); `eval/rl/game_pool.py` (in-process parallel games with arbitrary options, `-q -c`); `eval/rl/cmaes_tune.py` (CMA-ES over a JSON parameter spec, common random numbers per generation, fresh tuning seeds each generation, default re-evaluated each generation); `eval/rl/map_features.py` (map features per seed computed with the agent's own `map_features`, colour-invariant: red and blue identical [verified on 60 seeds]); `eval/rl/mode_table.py` (mode × map table, cross-validated selectors); `eval/rl/log_team.py` + `eval/rl/collect.py` (attacker-state datasets; logs live on the agent objects, nothing is written during games); `eval/rl/train_value.py` (torch value net, exported as plain lists).
- **Dependencies**: training only, in a separate `venv_rl/` (gitignored): torch 2.4.1+cpu, numpy 1.24.4, cma 3.3.0 (listed in `eval/rl/requirements-train.txt`). Nothing new is needed at runtime: every team file stays stdlib-only (rule R5), learned weights ship as Python constants.

## E-028 — Width-based planner for the attacker (IW(1) / p-IW / best-first over our own model) (2026-11-07/08)
- **Status**: running.
- **Question**: does a width-based lookahead (IW(1), Lipovetzky & Geffner 2012; with a simulator and rewards as in Lipovetzky, Ramirez & Geffner 2015) over our own forward model of the attacker's world raise points over lab5_smart (= `lab6_off`)?
- **Planner** (`WidthPlanner` in `teams/greedy_lab_v6.py`): state = (cell, carried, food mask, capsule mask, modelled ghost cells, their scared timers); we move, then every modelled enemy ghost moves once (M1: chase when within `plan_r`, else hold; scared: flee; optional M2: walk to the enemy cell across our nearest home-border cell); death = terminal. Rewards: eat +a, bank +(1−a) per food, death −(a·carried + D), scared ghost +1, capsule +0.3; leaf value = carried·(1−a)·γ^dist_home (or a learned net). Atoms: `pos`, `pos_carry` (cell, carry bucket), `pos_food`, `pos_carry_g` (+ ghost-distance bucket). Hidden ghosts sit at their belief's most likely cell (flags give their side). Root action of the best node is played (or, in `override`, only if it beats greedy's action by `plan_margin`). Standalone speed: ≤ 22 ms per call at horizon 40 [verified, scratch benchmark].
- **Modes**: `full` (planner decides whenever its best value > `plan_min`), `danger` (only while a non-scared modelled ghost is within `plan_trigger` = 7), `food` (only instead of the food-target choice), `override` (greedy decides, planner overrides by margin).
- **Pilot** (`n1_plan`, tuning seeds 261–265, 80 games per variant against the pool; v1 planner):

  | variant | paired Δ vs lab5_smart [95% CI] |
  |---|---|
  | `lab6_plan_danger` | +0.25 [−0.26, +0.70] |
  | `lab6_plan_g` (33 games) | +0.24 [−0.09, +0.64] |
  | `lab6_plan_best` | +0.15 [−0.28, +0.66] |
  | `lab6_plan_food` | +0.07 [−0.30, +0.53] |
  | `lab6_plan_full` | +0.06 [−0.47, +0.54] |

  Diagnostics (5 seeds, so indicative only): planner variants returned 11–13 food per game (lab5_smart 10.9), conceded 5.6 (7.1), killed 2.0–2.4 enemies (0.8; mostly scared ghosts after capsules), but died 1.6–1.8 times (1.13) and dropped 6–8 carried food (3.2).
- **Bug found by the research review** (width_planning.md §8 S1): a dying successor still marked its atom as seen, pruning later safe arrivals at that (cell, carry). Fixed under `plan_v=2` (atoms only for surviving states; Stop generated; root children never pruned). v1 entries keep the old behaviour for reproducibility.
- **Screen 2** (`n1_plan2`, tuning seeds 261–300, 40 seeds × 2 colours × 8 pool members = 640 games per variant): `lab6_p2_danger`, `lab6_p2_override`, `lab6_p2_danger_g`, `lab6_p2_full_g`, `lab6_p2_best_g`, and `lab6_plan_danger` (v1 control). Paired against lab5_smart from `n1_base` (same games).
- **Pre-registered rule**: the variant with the largest paired Δ vs lab5_smart goes on (tuning / CMA-ES, then validation) if its Δ > 0 and no opponent's Δ < −0.3; ties within 0.03 go to the simpler variant (danger < override < full; iw < best; pos_carry < pos_carry_g).
- **Screen 2 result (stopped early, 2026-11-08 00:15)**: on the advisor's review (below) the run was stopped after 914 games to move the CPU to a fresh-seed confirmation with ablations (E-030); the selection rule moved there, written down before E-030 started.
  - `lab6_p2_danger` (complete, 640 games): **+0.09 [−0.04, +0.23]** vs lab5_smart; per opponent camper +0.25, greedy_v3 +0.31, rusher +0.20, greedy +0.19, greedy_v2 +0.04, exploit_v2 +0.03, feature −0.12, choke −0.15. 2.32 PPG (lab5_smart 2.17 on the same games). Max move 0.349 s, **p95 0.115 s** under 17 parallel workers: the 0.12 s clock budget was often binding, so searches were load-dependent (non-deterministic) [verified from the sentinel times].
  - `lab6_p2_override` (300 of 640 games): +0.13 [−0.06, +0.32].
  - Not played: `lab6_p2_danger_g`, `lab6_p2_full_g`, `lab6_p2_best_g`, `lab6_plan_danger` (v1 control).
- **Advisor review** (a separate agent, read-only, 2026-11-08 00:05) raised: (1) the code under test was still changing → v6 frozen, new options only in `teams/greedy_lab_v7.py`; (2) a clock-limited search is load-dependent → node cap `plan_nodes`; (3) the gain may be "hunt scared ghosts" rather than lookahead (kills 0.8 → 2.1) → ablations without kill / capsule rewards and a planner-free `hunt_scared` rule; (4) `danger` mode overrides greedy's safety rules (likely source of the extra deaths) → `shield` (veto only) and `override`; (5) winner's curse → confirm on fresh seeds; (6) the real bar is lab5_smart → it joins the opponents; (7) the pool has no double attacker → specialist diagnostic.

## E-030 — Planner confirmation and ablations on fresh tuning seeds (X1) (2026-11-08)
- **Status**: running.
- **File**: `teams/greedy_lab_v7.py` = v6 + default-off options (`plan_nodes`, `plan_kill`, `plan_cap`, `plan_hidden` near/both, `plan='shield'`, `hunt_scared`, `formation='power'`) + the trained leaf net (`LEAF_NET`, used only with `plan_leaf=net`). Identity (`n1_identity7`): `lab7_off` = `lab6_off` 18/18, `lab7_danger` (node cap 2000, clock 0.3 s) = `lab6_p2_danger` 18/18.
- **Leaf value net** (`eval/rl/train_value.py`, data `d1_lab6off`: 450 games of lab6_off against the pool + double_attack on tuning seeds 1–25, 128,242 attacker states): target = food banked minus food dropped by dying over the next 30 own moves; 12 features computable inside the planner; 12-16-1 tanh MLP; held-out games (random 20% of game-sized chunks): **R² 0.46** (linear 0.21). A first split by row order put mostly double_attack games in the test set (R² < 0, distribution shift) and was replaced.
- **Run** `n1_x1`: tuning seeds 401–440 (`--seed-offset 400`, 40 seeds, unused tonight), both colours, against the 8 pool members **and lab5_smart** (720 games per arm). Arms: `lab5_smart` (control), `lab7_danger` (W), `lab7_override`, `lab7_danger_g`, `lab7_danger_nokill`, `lab7_danger_nocap`, `lab7_danger_d8`, `lab7_danger_near`, `lab7_hunt` (no planner), `lab7_shield`, `lab7_danger_net`.
- **Pre-registered rule** (written before the run): C1 = the arm with the largest paired Δ vs lab5_smart over the 8 pool opponents, provided Δ > 0 and no pool opponent's Δ < −0.3; ties within 0.05 go to the simpler arm (hunt > shield > danger > override > danger_g; hand leaf > net). The ablations attribute the gain: if `nokill`/`nocap` lose most of W's gain and `lab7_hunt` matches W, the gain is scared-ghost hunting, not lookahead. If every arm is ≤ 0: fallback = CMA-ES on the linear food policy (`focus=linear`). C1 then gets the CMA-ES planner tuning (E-031) and the validation run.

## E-029 — Map modes: food-region / sensory focus and formations, mode × map table, selector (2026-11-07/08)
- **Status**: running.
- **Question** (user request): do per-map "modes" help, e.g. a map whose enemy food sits mostly in the top half → an attacker that prefers top food (`greedy_top_left`)? Is there a mode that helps on average, and can a selector predict per map which mode to play from map features computed at startup?
- **Modes** (`teams/greedy_lab_v6.py`, `focus` adds `focus_w`·penalty ∈ [0, 1] to the maze distance of each race-safe food, `focus_w` = 3 steps): `top` / `bottom` (own frame: blue's y flipped, so a map gives both colours the same view [verified]), `majority` (the half holding more enemy food: the user's hypothesis as a fixed rule), `deep` / `shallow` (distance from the border), `cluster` (food with many food within 3 steps), `far` (food far from the enemy ghosts' belief cells; sensory, not map-based); formations `lead0` / `lead5` (the home defender attacks too while our score ≤ 0 / ≤ 5).
- **Table** (`n1_modes`): 9 modes × tuning seeds 261–320 (60 maps) × 8 pool members × 2 colours = 8,640 games, paired per (opponent, seed, colour) with lab5_smart from `n1_base` (mode `none`).
- **Map features** (`eval/rl/feat_tuning_260_60.json`): food_y, food_top, food_ystd, food_depth, food_deadend, food_cluster, border_n, cap_n, cap_y, cap_depth, cells, my_food_depth.
- **Pre-registered analysis** (`eval/rl/mode_table.py`): (1) mean paired gain per mode with a CI over maps; (2) 10-fold cross-validation over maps of four selection policies: best constant mode, per-map oracle (noise-inflated upper bound), per-mode ridge regression on the features (play the argmax prediction if > 0), per-mode single-feature threshold rule. A selector counts as useful only if its cross-validated gain beats the best constant mode with a CI above 0. A constant mode with a positive CI goes to validation like any other candidate.
