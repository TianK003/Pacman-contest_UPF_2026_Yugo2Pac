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
- **Status**: done (screen stopped early; conclusions in E-030).
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

## E-029 — Map modes: food-region / sensory focus and formations, mode × map table, selector (2026-11-07/08)
- **Status**: done (2026-11-08 04:20). Conclusion: no mode and no selector helps.
- **Question** (user request): do per-map "modes" help, e.g. a map whose enemy food sits mostly in the top half → an attacker that prefers top food (`greedy_top_left`)? Is there a mode that helps on average, and can a selector predict per map which mode to play from map features computed at startup?
- **Modes** (`teams/greedy_lab_v6.py`, `focus` adds `focus_w`·penalty ∈ [0, 1] to the maze distance of each race-safe food, `focus_w` = 3 steps): `top` / `bottom` (own frame: blue's y flipped, so a map gives both colours the same view [verified]), `majority` (the half holding more enemy food: the user's hypothesis as a fixed rule), `deep` / `shallow` (distance from the border), `cluster` (food with many food within 3 steps), `far` (food far from the enemy ghosts' belief cells; sensory, not map-based); formations `lead0` / `lead5` (the home defender attacks too while our score ≤ 0 / ≤ 5).
- **Table** (`n1_modes`): 9 modes × tuning seeds 261–320 (60 maps) × 8 pool members × 2 colours = 8,640 games, paired per (opponent, seed, colour) with lab5_smart from `n1_base` (mode `none`).
- **Map features** (`eval/rl/feat_tuning_260_60.json`): food_y, food_top, food_ystd, food_depth, food_deadend, food_cluster, border_n, cap_n, cap_y, cap_depth, cells, my_food_depth.
- **Pre-registered analysis** (`eval/rl/mode_table.py`): (1) mean paired gain per mode with a CI over maps; (2) 10-fold cross-validation over maps of four selection policies: best constant mode, per-map oracle (noise-inflated upper bound), per-mode ridge regression on the features (play the argmax prediction if > 0), per-mode single-feature threshold rule. A selector counts as useful only if its cross-validated gain beats the best constant mode with a CI above 0. A constant mode with a positive CI goes to validation like any other candidate.
- **Results** [verified, `n1_modes` complete: 8,640 games, 16 games per (mode, map); `eval/rl/mode_table.py`]. Mean paired gain vs lab5_smart, 95% CI over the 60 maps:

  | mode | gain [95% CI] | maps better / worse |
  |---|---|---|
  | focus top | −0.066 [−0.153, +0.022] | 17 / 21 |
  | focus bottom | −0.033 [−0.121, +0.054] | 20 / 22 |
  | focus majority (the user's hypothesis as a fixed rule) | −0.040 [−0.144, +0.065] | 20 / 25 |
  | focus deep | −0.011 [−0.125, +0.103] | 20 / 19 |
  | focus shallow | −0.030 [−0.086, +0.026] | 17 / 16 |
  | focus cluster | −0.056 [−0.147, +0.035] | 18 / 25 |
  | focus far (from the ghosts' belief) | −0.023 [−0.103, +0.058] | 24 / 22 |
  | formation lead0 (both attack while score ≤ 0) | **−0.756 [−0.963, −0.550]** | 10 / 48 |
  | formation lead5 (both attack while score ≤ 5) | **−1.051 [−1.236, −0.866]** | 3 / 56 |

  Cross-validated selection policies (10 folds over maps), gain over lab5_smart: best constant mode −0.045 [−0.111, +0.021]; per-map oracle +0.277 [+0.183, +0.371] (noise-inflated upper bound: it picks the luckiest mode per map); ridge −0.014 [−0.115, +0.088]; single-feature stump +0.041 [−0.047, +0.128]. No map feature correlates with any focus mode's gain beyond |r| = 0.46 (cluster mode vs food_cluster, r = −0.46, 60 maps).
- **Reading**: [verified on tuning seeds 261–320]
  - **No food-region mode helps on average**, and the user's "top-left-heavy map → greedy_top_left" idea (focus majority) is −0.04. The nearest race-safe food is already close to the best target; a region preference only adds detours.
  - **No selector beats the best constant**, which is "no mode": the per-map labels are mostly noise (oracle +0.28 vs cross-validated ≤ +0.04), as the research re-analysis of E-025 predicted.
  - **Double attack while behind loses badly** (−0.76 / −1.05): the empty home lets the enemy raider score freely. It agrees with lab7_power (−0.23, E-030) and the endgame rule only doubling up in the last 40 moves.
  - The map-mode track (proposals MM-1) is closed. The linear food policy (MM-2, CMA-ES) was not run: the planner track used the CPU.

## E-030 — Planner confirmation and ablations on fresh tuning seeds (X1) (2026-11-08)
- **Status**: done. C1 = `lab7_danger_net`.
- **File**: `teams/greedy_lab_v7.py` = v6 + default-off options (`plan_nodes`, `plan_kill`, `plan_cap`, `plan_hidden` near/both, `plan='shield'`, `hunt_scared`, `formation='power'`) + the trained leaf net (`LEAF_NET`, used only with `plan_leaf=net`). Identity (`n1_identity7`): `lab7_off` = `lab6_off` 18/18, `lab7_danger` (node cap 2000, clock 0.3 s) = `lab6_p2_danger` 18/18.
- **Leaf value net** (`eval/rl/train_value.py`, data `d1_lab6off`: 450 games of lab6_off against the pool + double_attack on tuning seeds 1–25, 128,242 attacker states): target = food banked minus food dropped by dying over the next 30 own moves; 12 features computable inside the planner; 12-16-1 tanh MLP; held-out games (random 20% of game-sized chunks): **R² 0.46** (linear 0.21). A first split by row order put mostly double_attack games in the test set (R² < 0, distribution shift) and was replaced.
- **Run** `n1_x1`: tuning seeds 401–440 (`--seed-offset 400`, 40 seeds, unused tonight), both colours, against the 8 pool members **and lab5_smart** (720 games per arm). Arms: `lab5_smart` (control), `lab7_danger` (W), `lab7_override`, `lab7_danger_g`, `lab7_danger_nokill`, `lab7_danger_nocap`, `lab7_danger_d8`, `lab7_danger_near`, `lab7_hunt` (no planner), `lab7_shield`, `lab7_danger_net`.
- **Pre-registered rule** (written before the run): C1 = the arm with the largest paired Δ vs lab5_smart over the 8 pool opponents, provided Δ > 0 and no pool opponent's Δ < −0.3; ties within 0.05 go to the simpler arm (hunt > shield > danger > override > danger_g; hand leaf > net). The ablations attribute the gain: if `nokill`/`nocap` lose most of W's gain and `lab7_hunt` matches W, the gain is scared-ghost hunting, not lookahead. If every arm is ≤ 0: fallback = CMA-ES on the linear food policy (`focus=linear`). C1 then gets the CMA-ES planner tuning (E-031) and the validation run.

- **X1b** (`n1_x1b`, same seeds and opponents, paired with X1's lab5_smart games; 2 workers, added 00:25, before any X1 result was looked at): `lab7_dplan` (defender planner only: IW(1) over (defender cell, invader cell) atoms against a modelled invader that forages and flees home; overrides the rule defender by margin 0.3; in 3 smoke games it fired 21 times and overrode 8 times, max 64 ms), `lab7_power` (SM-3 power play), `lab7_danger_dplan`, `lab7_danger_piw`, `lab7_danger_m1m2`, `lab7_danger_both`. Same rule as X1; X1b arms compete for C1 only if X1b finishes before the CMA-ES run starts, otherwise they are reported as a secondary screen.
- **Value-net capacity check**: 12-32-1 reaches held-out R² 0.471 vs 0.464 for 12-16-1, so the smaller (faster) net is kept.


- **Results** (`n1_x1`, complete: 11 arms × 640 pool games + 80 head-to-head games against lab5_smart; X1b partial: `lab7_dplan` and `lab7_power` complete, the other X1b arms were stopped at 02:00 to free the CPU). Gates: 0 crashes, 0 time warnings, 0 violations in all arms; max move 0.31 s (`lab7_danger_net`, p95 0.21 s) under 14–21 parallel workers.

  | arm | Δ vs lab5_smart (pool, 640 games) [95% CI] | PPG (720 games) | h2h vs lab5_smart | deaths / game | food returned / game |
  |---|---|---|---|---|---|
  | `lab7_danger_net` | **+0.57 [+0.37, +0.76]** (every opponent +0.46 … +0.79, all CIs > 0) | 2.60 | **2.31** | **0.40** | **15.8** |
  | `lab7_danger_g` | +0.24 [+0.02, +0.44] | 2.25 | 1.86 | 1.16 | 12.6 |
  | `lab7_dplan` (X1b) | +0.19 [+0.03, +0.35] | 2.16 | 1.43 | – | – |
  | `lab7_override` | +0.12 [−0.09, +0.31] | 2.13 | 1.71 | – | – |
  | `lab7_danger` | +0.06 [−0.14, +0.24] | 2.07 | 1.64 | 1.31 | 11.4 |
  | `lab7_danger_d8` | +0.06 (game-for-game identical to `lab7_danger`) | 2.07 | 1.64 | 1.31 | 11.4 |
  | `lab7_danger_nokill` | +0.04 [−0.15, +0.23] | 2.06 | 1.65 | – | – |
  | `lab7_danger_near` | +0.03 [−0.16, +0.21] | 2.05 | 1.66 | 1.34 | 11.5 |
  | `lab7_danger_nocap` | −0.00 [−0.21, +0.20] | 2.01 | 1.64 | – | – |
  | `lab7_shield` | +0.00 [+0.00, +0.00] (never fires: identical to lab5_smart) | 1.97 | 1.24 | – | – |
  | `lab7_hunt` | −0.23 [−0.37, −0.11] | 1.76 | 1.18 | – | – |
  | `lab7_power` (X1b) | −0.23 [−0.32, −0.15] | 1.80 | 1.46 | – | – |
  | `lab5_smart` (control) | 0 | 1.51 (incl. the strong new arms as opponents) | – | 0.92 | 9.0 |

- **Reading**:
  - [verified on these games] **The learned leaf value is what makes the planner work.** With the hand-made leaf, the planner dies more than lab5_smart (1.31 vs 0.92 per game) and drops 7.8 carried food per game; with the net, deaths fall to 0.40 and dropped food to 1.2, and returns rise to 15.8. The net was trained on lab6_off games from tuning seeds 1–25 (no map overlap with X1's seeds 401–440).
  - **Why the hand-made planner was optimistic**: a root action's value is the best node in its subtree (max backup over a deterministic model), so a death branch only matters when every continuation dies. `plan_death` 3 vs 8 changed **no decision** (identical games), and `shield` (veto when greedy's move is predicted deadly) never fired. The learned value instead prices the danger of a state from real outcomes.
  - **Not kill-farming**: removing the scared-ghost reward (+0.04) or both kill and capsule rewards (0.00) costs little against the plain planner (+0.06), and the planner-free hunting rule loses (−0.23).
  - **Richer novelty helps**: ghost-distance-bucket atoms (+0.24 vs +0.06) let the search revisit a cell at a different distance from the ghosts.
  - **The defender planner** helps on its own (+0.19) and is orthogonal to the attacker planner (X2 tests the combination).
  - **Power play loses** (−0.23): the defender leaves while the scared window lasts and the enemies' second agent scores.
- **C1** (pre-registered rule) = **`lab7_danger_net`** (largest Δ, all opponents > −0.3) → V1 validation and the X2 / X3 follow-ups (E-031).

## E-031 — Learned-leaf planner: validation (V1) and combinations (X2) (2026-11-08)
- **Status**: done (V1 passed 02:53; X2 and X3 complete; conclusions below). Written at 02:00, after X1's interim table (lab7_danger_net +0.57 [+0.38, +0.75] on 605 of 720 games; lab7_dplan +0.19 [+0.03, +0.35] in X1b) and before the runs below.
- **C1** (E-030 rule: largest Δ, Δ > 0) = `lab7_danger_net`, pending the per-opponent check (no pool opponent below −0.3) on the complete arm.
- **V1** (`n1_v1`, accept-rule run): **validation seeds 221–260** (`--seeds validation --seed-offset 220 --n-seeds 40`, unused), candidates `lab7_danger_net`, `lab5_smart`, `greedy_v3`, each against the 8 pool members and lab5_smart. Decision: the accept rule of evaluation.md §2 against the incumbent greedy_v3, and the same rule applied against lab5_smart (the better, unpromoted agent).
- **X2** (`n1_x2`, screen): tuning seeds 441–480 (unused), arms `lab5_smart`, `lab7_danger_net` (second confirmation), `lab7_net_dplan`, `lab7_g_net`, `lab7_g_net_dplan`, `lab7_full_net`, against the pool + lab5_smart.
- **Pre-registered rule for C2**: the X2 arm with the largest Δ vs lab5_smart; it goes to the second validation block (seeds 261–300) if Δ(C2 − lab7_danger_net) on X2 > 0 and Δ(C2 − lab5_smart) has its CI lower bound > 0; otherwise seeds 261–300 confirm C1 (accept-rule clause 5).
- **X2 result** [verified, `n1_x2`; `lab7_full_net` never played: X2 was stopped at 04:25 after the other arms completed, to give the CPU to E-033]. Δ vs lab5_smart over the 8 pool opponents (640 paired games): `lab7_danger_net` **+0.50 [+0.33, +0.66]** (second confirmation of X1's +0.57), **`lab7_net_dplan` +0.60 [+0.43, +0.77]**, `lab7_g_net_dplan` +0.52 [+0.35, +0.70], `lab7_g_net` +0.46 [+0.29, +0.62]. Direct pairs: net_dplan − danger_net = **+0.10 [+0.03, +0.17]** (720 games incl. lab5_smart as opponent); g_net_dplan − net_dplan = −0.08 [−0.17, +0.00]. → C2 = `lab7_net_dplan` by the rule (largest Δ, beats danger_net, CI > 0) → V2 (E-032, as `lab7_netf_dplan`, the identical fast-leaf version). Ghost-bucket atoms add nothing once the net is the leaf.
- **RL loop** (approximate policy iteration): collect on-policy data from `lab7_danger_net` games (tuning seeds 26–50), retrain the leaf net (`v2`), embed as a second constant, screen against `lab7_danger_net`.
- **V1 result** (`n1_v1`, validation seeds 221–260, 1,920 games; finished 02:53):

  | opponent | `lab7_danger_net` PPG | greedy_v3 PPG | Δ vs greedy_v3 [95% CI] | lab5_smart PPG | Δ vs lab5_smart [95% CI] |
  |---|---|---|---|---|---|
  | camper | 2.69 | 2.17 | +0.51 [+0.23, +0.82] | 2.36 | +0.33 [+0.04, +0.66] |
  | choke | 2.42 | 1.20 | +1.23 [+0.90, +1.50] | 1.69 | +0.74 [+0.38, +1.07] |
  | exploit_v2 | 2.45 | 1.51 | +0.94 [+0.50, +1.38] | 1.85 | +0.60 [+0.26, +0.94] |
  | feature | 2.55 | 1.74 | +0.81 [+0.47, +1.18] | 2.05 | +0.50 [+0.20, +0.82] |
  | greedy | 2.60 | 1.99 | +0.61 [+0.34, +0.89] | 2.17 | +0.42 [+0.07, +0.78] |
  | greedy_v2 | 2.50 | 1.25 | +1.25 [+0.89, +1.61] | 1.60 | +0.90 [+0.54, +1.24] |
  | greedy_v3 | 2.56 | – | (h2h) | 2.01 | +0.55 [+0.24, +0.88] |
  | lab5_smart | 2.31 | 0.89 | +1.43 [+0.93, +1.90] | – | (h2h) |
  | rusher | 2.65 | 1.81 | +0.84 [+0.50, +1.20] | 2.08 | +0.57 [+0.24, +0.94] |
  | **pool (640 paired games)** | | | **+0.95 [+0.78, +1.13]** | | **+0.58 [+0.42, +0.74]** |

  | team totals per game (720 games each) | returned | conceded | deaths | kills | food lost | max carried | 28-finish us / them |
  |---|---|---|---|---|---|---|---|
  | lab5_smart | 11.5 | 9.3 | 1.00 | 0.52 | 2.6 | 8.1 | 7 / 5 |
  | `lab7_danger_net` | **17.3** | **8.6** | **0.36** | 0.79 | **0.9** | 10.9 | **25 / 3** |

  **Accept rule** (evaluation.md §2) against the incumbent greedy_v3:

  | condition | result | pass |
  |---|---|---|
  | 1. gates | lint OK; 0 crashes, 0 warnings, 0 violations, 0 moves over 0.5 s in 720 games; max move 0.319 s, p95 0.178 s (≈ 12 parallel workers) | ✓ |
  | 2. pool Δ > 0, CI lower bound > 0, validation seeds, ≥ 40 seed-pairs per opponent | **+0.95 [+0.78, +1.13]**, 40 seed-pairs each | ✓ |
  | 3. no opponent with CI upper ≤ −0.5; past versions not worse by > 0.5 | worst camper +0.51 [+0.23, +0.82]; greedy +0.61, greedy_v2 +1.25 | ✓ |
  | 4. head-to-head vs greedy_v3 ≥ 1.5 | **2.56** (80 games) | ✓ |
  | 5. confirmation on seeds not used for selection | selection used tuning seeds 401–440 (E-030); validation 221–260 unused | ✓ |

  The same rule against lab5_smart (the better, unpromoted agent) also passes: +0.58 [+0.42, +0.74], every opponent's CI above 0, head-to-head 2.31.
- **Conclusion (V1)**: [verified on validation seeds 221–260] **`lab7_danger_net` passes the accept rule** against greedy_v3 and against lab5_smart. `lab7_danger_netf` (faster code, 24/24 identical games) is the version to ship if promoted. **Not done (release gate, user decision)**: Linux timing under load (WSL run planned tonight as a diagnostic), one locked test-seed run with the held-out teams, promotion to `my_team.py`.
- **RL loop, iteration 2** (written before X3): data `d2_net` = 450 games of `lab7_danger_net` (pool + double_attack, tuning seeds 26–50; 123,096 states; it scored 2.55 PPG there vs lab6_off's 2.11 in `d1`). Nets: `v2` on d1 + d2 (held-out R² 0.588, linear 0.344) → `LEAF_NET2` / `plan_leaf=net2f`; `v2o` on d2 only (R² 0.552) → `LEAF_NET3` / `net3f`. **X3** (`n1_x3`): `lab7_danger_netf`, `lab7_net2`, `lab7_net3` against the 8 pool members on tuning seeds 481–520 (unused), 640 games each. Rule: the better of net2/net3 replaces net in the candidate if its paired Δ vs lab7_danger_netf > 0.
- **X3 result** [verified, `n1_x3`, 1,920 games]: `lab7_net2` (trained on d1 + d2) − lab7_danger_netf = **−0.04 [−0.12, +0.04]**; `lab7_net3` (on-policy d2 only) = **−0.15 [−0.28, −0.03]** (camper −0.29). Neither replaces the first net, though both predict the 30-move outcome better (R² 0.59 / 0.55 vs 0.46). Better held-out prediction of the target did not give better play. One plausible reason [untested]: the first net was trained on the greedy policy, which is what the leaf is meant to price (the planner hands control back to greedy after the trigger), while the planner's own games mix policies. Approximate policy iteration stops after one step here; X3 closes the RL-loop track (proposals RL-1).
- `lab7_danger_netf` (fast leaf code) = `lab7_danger_net`: 24/24 identical games (`n1_identity_netf`), planner time p50 47 → 21 ms, p99 178 → 116 ms.

## E-032 — Promote the learned-leaf planner to `my_team.py` (greedy_v4); V2: defender planner on top (2026-11-08)
- **Status**: done. Promotion done; **V2: `lab7_netf_dplan` rejected, greedy_v4 stays** (04:50).
- **Decision** (user, 2026-11-08 03:35, after the V1 report): promote `lab7_danger_net` "for now"; then compare it with the defender-planner version if V2 confirms it.
- **File** `teams/greedy_v4.py` = `teams/greedy_lab_v7.py` with the `lab7_danger_netf` options as defaults (plan=danger, plan_v=2, plan_nodes=2000, plan_budget=0.3, plan_leaf=netf); no other change. Lint OK. **Identity** (`n1_identity_v4`): greedy_v4 = lab7_danger_net on 18/18 X2 games; `lab7_netf_dplan` = `lab7_net_dplan` on 18/18 X2 games. `my_team.py` = copy of greedy_v4 (commit below); smoke vs baseline both colours: wins, 0 warnings.
- **Release gate items still open** (evaluation.md §2): Linux / Python 3.8 timing under load (WSL run planned), one locked test-seed run with the held-out teams (user decision).
- **V2** (`n1_v2`, pre-registered before the run): `lab7_netf_dplan` vs the new incumbent greedy_v4 on **validation seeds 261–300** (the last 40 unused validation seeds), both against the 8 pool members + lab5_smart, plus their head-to-head. Decision: the accept rule of evaluation.md §2 with greedy_v4 as incumbent. If it passes, `teams/greedy_v5.py` (= lab7_netf_dplan as defaults) replaces greedy_v4 in `my_team.py` (user's instruction). After V2 the validation list is used up (seeds 1–300): a fresh validation list needs the user's approval.
- **V2 result** [verified, `n1_v2`, 1,520 games, validation seeds 261–300]:

  | criterion | result | needed |
  |---|---|---|
  | gates | 0 crashes, 0 time warnings, 0 violations; max move 0.443 s (greedy_v4 0.283 s), p95 0.182 s (0.134 s) | 0 / 0 / 0 ✓ |
  | paired Δ vs greedy_v4 over pool + lab5_smart (720 games) | **−0.03 [−0.11, +0.05]** | CI > 0 ✗ |
  | per opponent | camper −0.17 [−0.40, −0.01], choke −0.15, greedy −0.11, greedy_v3 +0.15, feature +0.09, others ±0.07 | no regression beyond 0.5 ✓ |
  | head-to-head vs greedy_v4 (80 games) | **1.69** (greedy_v4 1.01) | ≥ 1.5 ✓ |

  Team totals per game (lab7_netf_dplan / greedy_v4): returned 16.8 / 16.7, conceded 8.2 / 8.9, kills 0.63 / 0.85, standoff moves 177 / 215, 28-food finishes 16 / 10 of 800.
- **Decision** (pre-registered rule): **rejected**: the pool gain is not above 0, so greedy_v4 stays in `my_team.py`; the pre-built `teams/greedy_v5.py` was deleted unbenchmarked, so the name stays free for the next real promotion.
- **Reading**: [verified on these games] the defender planner concedes a little less (8.2 vs 8.9 per game) and clearly wins the head-to-head against greedy_v4's planner attacker (1.69), but it does not convert into points against the pool. On X2's tuning seeds it was +0.10 [+0.03, +0.17] (E-031): a tuning-seed gain that did not survive fresh seeds. [untested] It may only help against planner attackers like ours; whether tournament opponents are like that is unknown.
- **Validation seeds are now exhausted** (1–300 used). Any further accept decision needs a fresh validation list (user decision).
- **Linux timing of greedy_v4 (release-gate item, 05:10)** [verified]: WSL Ubuntu 24.04, CPython 3.8.20, `~/pacman_wsl` mirror re-synced (`my_team.py` byte-identical to `teams/greedy_v4.py`); `submission` vs greedy_v3, choke, exploit_v2, lab5_smart on tuning seeds 516–520 (reused: a timing check tunes nothing), both colours, `-q -c` (real SIGALRM limits), 2 WSL workers **while the Windows side ran 12 game workers** (CPU saturated). Result: 40 games, 35-5-0, **0 crashes, 0 time warnings, max move 0.283 s, p95 0.191 s** (run `wsl_v4_loaded`, kept in the WSL mirror). The remaining release-gate item is the locked test-seed run with the held-out teams (user decision).

## E-033 — Non-deep-learning search: Monte-Carlo planners and lookup-table leaves (2026-11-08)
- **Status**: done (06:05). No non-DL arm beats greedy_v4. The quadratic (non-DL) leaf is practically equivalent to the net (pooled −0.02 [−0.09, +0.04]). Monte-Carlo search loses.
- **Why** (user, 03:35): after the learned-leaf result, try simpler non-deep-learning methods "e.g. using MCTS or similar to combine it with existing knowledge"; design first, have an advisor critique it, then build.
- **Design**: `docs/research/mcts_design.md`. Draft 1 (03:45) was critiqued by an advisor agent (Fable, xhigh effort), with these main points:
  1. UCT with 150 iterations is noise-dominated: SE 0.3–0.8 per root child against decision gaps of 0.3–1.0.
  2. Per-step ghost mixing makes ghosts too slow, so the mean backup stays optimistic.
  3. ε-random rollouts make corridors look deadly.
  4. A table leaf without side and scared would price border standoffs as deaths.
  5. Use enumerated weighted scenarios, deterministic rollouts and override-by-margin; fit leaf parameters instead of guessing them.

  Draft 2 = what was built, with all of these points applied.
- **File** `teams/greedy_lab_v8.py` = v7 + default-off options (header lists them). No random numbers anywhere.
  - `plan_leaf=table`: IW leaf = 7×7×7×2×2 lookup table of the mean 30-move outcome (carried, nearest ghost, distance home, side, nearest ghost scared ≥ distance + 1), sparse cells shrunk to the (carried, ghost, side) parent (K = 30). Fitted by `eval/rl/fit_leaves.py` on the same data and split as LEAF_NET (d1, 128k states): **held-out R² 0.453 vs the net's 0.464 on the same rows** (the 3-D table without side / scared was not kept).
  - `plan_leaf=lin`: least squares on the net's 12 features (R² 0.209).
  - `plan=fmc`: flat paired Monte Carlo.
    - Scenarios: every legal root move is simulated against the same weighted ghost scenarios. A scenario is a joint placement (the top 4 belief cells per hidden ghost, best 4 joint placements) × a ghost type per ghost: chase 0.5, intercept 0.3 (heads for the enemy cell across our nearest home border, chases within 2), camp 0.2 (chases within 3). The 12 heaviest scenarios are kept.
    - Ghost awareness: visible ghosts know where we are. Hidden ones hold their post until we come within 6 or eat food.
    - Rollouts: deterministic greedy-in-model, of 20 moves, ending at banking.
    - Value = weighted mean return.
    - Greedy's move is replaced only when the best move is > 0.3 better (`mc_margin`), under the same trigger as plan=danger.
  - `plan=mcts`: fmc + open-loop UCT over the next 4 moves (150 iterations, scenarios round-robin by weight, UCB on min-max normalised returns, c = 1). Each root move's most visited line is re-evaluated on all scenarios; the root value is the better of the flat and tree values.
  - `eval/check_rules.py` now warns (not errors: T-02 allows it) on draws from the global `random` module.
- **Identity** (`n1_identity8`, tuning seeds 1–3 × baseline, camper, exploit_v2, both colours):
  - `lab8_off` = `lab7_off` = `lab6_off`: 18/18.
  - `lab8_v4` = greedy_v4: 17/18. The 18th game had a 0.31 s move in both versions (the planner's 0.3 s clock fired under a 30-process load); replayed with the clock off, both score identically (blue +12).
- **Timing** (3 games each vs greedy_v3 / choke / greedy_v2, laptop under full load), planner call times:

  | arm | p50 | p99 | max | time-outs |
  |---|---|---|---|---|
  | fmc | 2 ms | 14 ms | 15 ms | 0 |
  | mcts | 14 ms | 59 ms | 73 ms | 0 |
  | IW + table | 9 ms | 35 ms | 46 ms | 0 |
  | IW + lin | 20 ms | 136 ms | 257 ms | 0 |
  | greedy_v4 (IW + net) | 30 ms | 106 ms | 170 ms | 0 |

  Most fmc rollouts stop after one move: on our side with no race-safe food the line is worth 0.
- **Screen** (`n1_x4a` + `n1_x4b`, merged for the analysis):
  - Arms: `lab8_table`, `lab8_lin`, `lab8_fmc`, `lab8_fmc_table` (H = 12, table cutoff), `lab8_mcts`, each paired with the incumbent `greedy_v4`.
  - Seeds and opponents: fresh tuning seeds 521–560, both colours, against the 8 pool members + lab5_smart + greedy_v4.
- **Pre-stated reading**:
  - An arm **matches** greedy_v4 if its paired Δ ≥ 0 with a CI lower bound > −0.15, and **beats** it if the CI is above 0.
  - Any arm that beats greedy_v4 is confirmed on fresh tuning seeds 561–600 before anything else. The validation seeds are used up after V2, and a fresh validation list is the user's decision.
  - Ingredient reading: the planner with the hand leaf scored +0.06 vs lab5_smart (E-030) and the net leaf +0.57. If the order comes out hand < lin < table ≈ net, the gain comes from the outcome signal, not the model class.
  - Gates as always: 0 crashes / warnings / violations.
- **Part C** (`n1_x4c`, added 04:51 after V2 finished, same seeds/opponents, paired with part A's greedy_v4 games): `lab9_v4_check` (greedy_v4 + flat paired MC re-check of the chosen move, margin 0.3) and `lab9_fmc_net` (flat MC, H = 12, learned-net cutoff). `teams/greedy_lab_v9.py` = v8 + `mc_check`, `mc_leaf=net`; identity with greedy_v4's options = greedy_v4 and v9 defaults = v8 defaults (3/3 games each, planner clock off).
- **Part D** (`n1_x4d`, added 05:05; **a follow-up chosen after seeing interim results**, so it is weaker evidence than parts A–C): the final `lab8_lin` (−0.11 [−0.24, +0.02], R² 0.209) played much better than the partial `lab8_table` (−0.37 at 305 games, R² 0.453). Hypothesis [untested]: a max-backup search exploits the errors of a piecewise-constant leaf (it seeks out overestimated cells), so smoothness matters more than R². Test: `lab10_quad` = IW planner with a **smooth non-DL leaf as accurate as the net**: a quadratic ridge regression on the net's 12 features (91 terms, λ = 30 picked on the held-out split, R² 0.461 vs net 0.464; `eval/rl/leaf_quad_v1.py`). `teams/greedy_lab_v10.py` = v9 + `plan_leaf=quad`; the per-cell decomposition equals the direct formula (max error 9e-15 over 1,000 random vectors); identity with greedy_v4's options = greedy_v4 (2/2, clock off); planner p99 97 ms under load. Reading: if quad ≈ greedy_v4 (matches by the rule above), the learned net can be replaced by a polynomial, and leaf smoothness is the property that matters.
- **Interim (05:05; part B complete)** [verified, `n1_x4a` + `n1_x4b`, pairs over 720 games vs greedy_v4]:

  | arm | Δ vs greedy_v4 [95% CI] | PPG | returned / game | deaths / game | standoff moves / game |
  |---|---|---|---|---|---|
  | `lab8_lin` | −0.11 [−0.24, +0.02] | 2.36 | 14.7 | 0.62 | 276 |
  | `lab8_mcts` | −0.52 [−0.70, −0.33] | 1.94 | 11.1 | 0.40 | 263 |
  | `lab8_fmc_table` | −0.72 [−0.91, −0.53] | 1.73 | 9.0 | 0.48 | 288 |

  The Monte-Carlo arms die rarely but score little: under the scenario ghosts (aware chasers and interceptors) crossing looks dangerous, so the override keeps the attacker at the border (timidity, T-56-like). Final table / fmc / part C / part D results below when complete.
- **Results, parts A–D (complete, 05:45)** [verified; tuning seeds 521–560; each arm 800 games, paired with greedy_v4 over 720 games vs the pool + lab5_smart; 0 crashes, 0 time warnings, 0 violations in every arm]:

  | arm | what | Δ vs greedy_v4 [95% CI] | PPG | h2h vs greedy_v4 | returned / g | deaths / g | food lost / g | max move s |
  |---|---|---|---|---|---|---|---|---|
  | `greedy_v4` | IW + learned net leaf (incumbent) | 0 | 2.46 | – | 15.8 | 0.42 | 1.2 | 0.33 |
  | `lab10_quad` (part D, post-hoc) | IW + quadratic ridge leaf (non-DL, R² 0.461) | **−0.05 [−0.15, +0.05]** | 2.43 | 1.40 | 16.2 | 0.38 | 1.0 | 0.29 |
  | `lab8_lin` | IW + linear leaf (R² 0.209) | −0.11 [−0.24, +0.02] | 2.36 | 1.32 | 14.7 | 0.62 | 1.7 | 0.31 |
  | `lab8_table` | IW + lookup-table leaf (R² 0.453) | −0.33 [−0.46, −0.21] | 2.16 | 1.23 | 13.8 | 0.67 | 3.3 | 0.09 |
  | `lab9_v4_check` | greedy_v4 + flat-MC re-check | −0.43 [−0.61, −0.24] | 2.01 | 0.69 | 11.0 | 0.40 | 1.0 | 0.23 |
  | `lab8_mcts` | flat MC + open-loop UCT | −0.52 [−0.70, −0.33] | 1.94 | 0.74 | 11.1 | 0.40 | 1.0 | 0.11 |
  | `lab8_fmc` | flat paired MC, hand cutoff | −0.67 [−0.87, −0.47] | 1.80 | 0.74 | 9.6 | 0.52 | 1.3 | 0.10 |
  | `lab8_fmc_table` | flat MC, table cutoff | −0.72 [−0.91, −0.53] | 1.73 | 0.53 | 9.0 | 0.48 | 1.1 | 0.07 |
  | `lab9_fmc_net` | flat MC, net cutoff | −0.72 [−0.93, −0.52] | 1.75 | 0.66 | 8.9 | 0.50 | 1.1 | 0.09 |

  (h2h = points per game against greedy_v4 in their 80 direct games; returned / deaths / lost = team totals per game.)
- **Reading** [verified on these games]:
  - **No non-DL arm beats greedy_v4**, and by the pre-stated rule none "matches" it (all point estimates < 0). No confirmation was triggered.
  - **Monte-Carlo search loses clearly (−0.43 … −0.72), in every form**: flat, with UCT, with any cutoff (hand, table, net), and even as a re-check on top of greedy_v4. The paired scenarios remove sampling noise, so this is model error: under aware chasing / intercepting scenario ghosts crossing looks dangerous and the override keeps the attacker home. These arms die rarely (0.40–0.52) but return 9–11 food per game instead of 16 (new trap T-60).
  - **The leaf matters through its smoothness, not its R²**: table (R² 0.453) −0.33 with 3.3 dropped food per game; linear (R² 0.209) −0.11; quadratic (R² 0.461) −0.05 ≈ net. A max-backup search exploits the jumps and noisy cells of a piecewise-constant leaf (new trap T-59). The learned net can be matched by a degree-2 polynomial fitted by ridge regression on the same data: no neural network is needed for this gain [parts D + E].
  - Ingredient order vs lab5_smart (E-030 scale: greedy_v4 ≈ lab5_smart + 0.5): hand leaf ≈ +0.06 < table ≈ +0.2 < lin ≈ +0.4 < quad ≈ net ≈ +0.5; MC arms ≈ −0.2 … 0. The outcome-trained leaf is the ingredient; a smooth model class is required to use it.
- **Part E (pre-registered 05:40, before part D's head-to-head games were complete)**: an **equivalence measurement, not a promotion decision**. By the rule above, lab10_quad does not "match" (pool Δ −0.05 [−0.15, +0.05] over 720 games: the point estimate is below 0), so no confirmation is triggered. Because it is the only non-DL arm close to greedy_v4, `lab10_quad` and `greedy_v4` play the reserved tuning seeds 561–600 against the same opponents (run `n1_x4e`). Reported: the pooled Δ over parts D + E (1,440 paired games) and its CI. Reading: if the pooled CI lies within ±0.10, the quadratic leaf is practically equivalent to the net; if it excludes 0 from below, the net is better.
- **Part E result** [verified, `n1_x4e`, 1,520 games, tuning seeds 561–600; 0 crashes / warnings / violations, max move 0.181 s]: lab10_quad − greedy_v4 = **+0.00 [−0.08, +0.08]** (720 paired games; every opponent within ±0.16, none significant); head-to-head 1.62 (part D: 1.40). **Pooled D + E: −0.02 [−0.09, +0.04] over 1,440 paired games**; head-to-head 1.51 over 160 games.
- **Conclusion (E-033)** [verified on tuning seeds 521–600]:
  1. **A quadratic ridge regression is practically equivalent to the neural leaf.** The pooled CI lies within ±0.10, so by the pre-stated reading the gain of greedy_v4 needs no neural network: 91 coefficients fitted by least squares on the same data do the same job.
  2. **Smoothness is what matters in a leaf under max-backup search, not R²** (T-59). The table, with the same R², loses 0.33.
  3. **Monte-Carlo search does not help here** in any form tried (−0.43 … −0.72); the scenario ghost model makes the attacker timid (T-60).
  4. No change to the submission: the quadratic leaf is equal, not better. [untested] It would be the fallback if the course ever objects to a trained neural net in the submission.

## E-034 — Leaf target horizon (RL-T) and planner trigger distance (2026-11-08)
- **Status**: done (08:00). Pre-registered 05:50; parts B–D added and pre-registered one at a time. greedy_v4's settings are a flat optimum; override mode is the one candidate for the next validation round.
- **Why**:
  - **RL-T** (proposals): the leaf nets and the table predict food banked − dropped within **30** moves. Under `open_goal` a safe carrier keeps eating and banks later, so carried food is undervalued (the table gives carrying 5, ghost far, 6 from home only +1.5).
  - **Trigger** (`plan_trigger` = 7) was never varied.
- **Data**: `d3_h60` = the d1 games replayed (lab6_off vs the 8 pool members + double_attack, tuning seeds 1–25, both colours; deterministic agents, so the same trajectories) with labels over **60** moves (`eval/rl/collect.py --horizon 60`).
- **Net**: `net60` = 12-16-1 tanh trained by `eval/rl/train_value.py` exactly as LEAF_NET, embedded as `LEAF_NET60` in `teams/greedy_lab_v11.py` (`plan_leaf=net60f`). The planner, rewards and discount are otherwise unchanged. γ^30 ≈ 0.40, so the leaf sits at a depth where the 60-move value is still discounted by the planner path.
- **Screen** (`n1_x5`): `lab11_net60`, `lab7_netf_t5`, `lab7_netf_t9`, each paired with greedy_v4. Unused-tonight tuning seeds 321–360, both colours, vs the 8 pool members + lab5_smart + greedy_v4.
- **Pre-stated reading**: as E-033 (match: Δ ≥ 0 with CI lower bound > −0.15; beat: CI > 0). A beating arm would need a fresh validation list (validation exhausted; user decision) before any promotion. No promotion tonight.
- **Build (06:05)**: `d3_h60` reproduced d1's games exactly (450 games, 128,242 rows, PPG 2.11: deterministic agents), only the labels differ. `net60` held-out R² **0.402** (linear 0.301; the 30-move net had 0.464, the longer horizon is harder to predict). `teams/greedy_lab_v11.py` = v10 + `plan_leaf=net60f`; identity with greedy_v4's options = greedy_v4 (2/2, clock off); net60 planner p99 108 ms, max 114 ms under load. Runs started: `n1_x5a` (greedy_v4, t5, t9; 7 jobs) and `n1_x5b` (lab11_net60; 3 jobs).
- **Results** [verified, `n1_x5a` + `n1_x5b`, tuning seeds 321–360, 720 paired games each vs greedy_v4; 0 crashes / warnings / violations]:

  | arm | Δ vs greedy_v4 [95% CI] | PPG | max move s |
  |---|---|---|---|
  | `lab7_netf_t5` (trigger 5) | −0.04 [−0.11, +0.03] | 2.41 | 0.23 |
  | `lab7_netf_t9` (trigger 9) | −0.00 [−0.06, +0.06] | 2.44 | 0.31 |
  | `lab11_net60` (60-move leaf target, R² 0.402) | −0.03 [−0.14, +0.08] | 2.43 | 0.24 |

  Reading: greedy_v4 sits on a flat optimum in these directions. The 60-move target changes the style a little (33 of 800 games ended by returning 28 food) but not the points: as in X3, changing what the leaf predicts does not improve play. RL-T closed.
- **Part B** (`n1_x5c`, pre-registered 06:52, same seeds and opponents, paired with n1_x5a's greedy_v4 games): `lab7_netf_full` (the planner decides on every attacker move, not only near ghosts; the never-played X2 arm `full_net` with the fast leaf) and `lab7_netf_h40` (planner horizon 40 instead of 30). Same reading; no promotion tonight.
- **Part B results** [verified, `n1_x5c`, 720 paired games each vs greedy_v4; 0 crashes / warnings / violations]: `lab7_netf_full` (planner on every attacker move) **−0.38 [−0.56, −0.20]**, returned 12.8 / game (greedy_v4 ≈ 16); `lab7_netf_h40` (horizon 40) −0.03 [−0.09, +0.04]. Reading: the planner should take over only near ghosts. [untested] Plausible reason: the leaf prices states under the greedy policy, which is what follows when the planner hands back control in danger mode; in full mode that no longer holds, and the planner's food sequencing is worse than greedy's nearest-safe-food rule.
- **Part C** (`n1_x5d`, pre-registered 07:22, same seeds / opponents / pairing): `lab7_netf_override` (greedy decides; the net-leaf planner overrides only when its best root value beats greedy's move by 0.3; X1's override used the hand leaf) and `lab7_netf_min03` (plan_min 0.3 instead of 0.05). Same reading; no promotion tonight.
- **Part C results** [verified, `n1_x5d`, 720 paired games each vs greedy_v4; 0 crashes / warnings / violations]: `lab7_netf_override` **+0.03 [−0.05, +0.12]** (deaths 0.40, returned 16.2, max move 0.20 s); `lab7_netf_min03` +0.01 [−0.05, +0.07] (deaths 0.57). Both **match** greedy_v4 by the pre-stated rule; neither beats it.
- **Part D** (`n1_x5e`, pre-registered 07:42, informational): `lab7_netf_override` and `greedy_v4` on unused tuning seeds 361–400 against the same opponents, to see whether the only positive point estimate tonight replicates. Pooled C + D Δ reported. Even a positive pooled CI would only make it a candidate for a fresh validation list (user decision).
- **Part D result** [verified, `n1_x5e`, 1,520 games, tuning seeds 361–400; 0 crashes / warnings / violations, max move 0.186 s]: lab7_netf_override − greedy_v4 = **+0.09 [+0.02, +0.17]** (720 paired games), head-to-head 1.68 (part C: 1.45). **Pooled C + D: +0.06 [+0.00, +0.12] over 1,440 paired games**, head-to-head 1.57 over 160.
  Reading: a small, consistent edge for **override mode** (greedy decides; the planner replaces greedy's move near ghosts only when its best root value is > 0.3 better than greedy's own move in the same search tree). The CI touches 0 and it is tuning-seed evidence. It is the only candidate from tonight worth a validation run, which needs a fresh validation list (user decision). Accept-rule shape so far: pool Δ > 0 (borderline), head-to-head ≥ 1.5 (1.57), no opponent regression beyond 0.5 (pooled per-opponent table below).
  Pooled C + D per opponent [verified, `summary --run n1_x5a n1_x5d n1_x5e --compare lab7_netf_override greedy_v4`, 160 paired games each]:

  | opponent | override PPG | greedy_v4 PPG | paired diff [95% CI] |
  |---|---|---|---|
  | camper | 2.57 | 2.62 | −0.06 [−0.17, +0.07] |
  | choke | 2.59 | 2.53 | +0.06 [−0.08, +0.20] |
  | exploit_v2 | 2.43 | 2.46 | −0.03 [−0.17, +0.12] |
  | feature | 2.77 | 2.79 | −0.01 [−0.11, +0.08] |
  | greedy | 2.72 | 2.72 | +0.00 [−0.10, +0.10] |
  | greedy_v2 | 2.70 | 2.49 | +0.21 [+0.08, +0.34] |
  | greedy_v3 | 2.54 | 2.40 | +0.14 [−0.03, +0.31] |
  | lab5_smart | 2.30 | 2.11 | +0.19 [−0.02, +0.42] |
  | rusher | 2.64 | 2.60 | +0.04 [−0.10, +0.19] |

  Team totals per game (override / greedy_v4, same runs): returned 16.2 / 15.9, conceded 8.0 / 9.1, deaths 0.39 / 0.43, 28-food finishes 35 / 37 of 1,600 / 1,840 games. The edge comes from the three greedy-family opponents (greedy_v2, greedy_v3, lab5_smart); against the other six it is ±0.06. [untested] Override keeps greedy's moves unless the planner sees a clear gain, so it differs from greedy_v4 mostly in close calls near ghosts.
- **Conclusion (E-034)** [verified on tuning seeds 321–400]: greedy_v4's planner settings sit on a flat optimum. Trigger 5/9, horizon 40, plan_min 0.3 and a 60-move leaf target are all within ±0.05 of it; planning on every move clearly hurts (−0.38); **override-by-margin is slightly better (+0.06 [+0.00, +0.12] over 80 seeds)**, the one candidate for the next validation round.

## E-035 — Diagnostic: greedy_v4 vs greedy_v3 against opponents outside the reference pool (2026-11-08)
- **Status**: done (06:40). **Diagnostic only, never a decision input** (friend teams: user rule; specialists are not in the pool).
- **Setup** (`n1_diag_v4`): greedy_v4 and greedy_v3 against double_attack, turtle, camper2, baseline_plus, field, rusher_camper, greedy_deadend, friend_andy, friend_aljaz_1..5; tuning seeds 501–510, both colours; 520 games; 0 crashes / warnings / violations; greedy_v4 max move 0.176 s.
- **Result** [verified]: greedy_v4 − greedy_v3 = **+0.77 [+0.57, +0.98]** (260 paired games); PPG 2.57 vs 1.80; win rate 84 % vs 56 %.

  | opponent | greedy_v4 | greedy_v3 | paired diff [95% CI] |
  |---|---|---|---|
  | baseline_plus | 2.80 | 2.70 | +0.10 [+0.00, +0.30] |
  | camper2 | 2.60 | 2.50 | +0.10 [−0.20, +0.40] |
  | double_attack | 2.85 | 2.20 | +0.65 [+0.20, +1.15] |
  | field | 3.00 | 1.65 | +1.35 [+0.60, +2.05] |
  | friend_aljaz_1 | 1.65 | 0.80 | +0.85 [+0.00, +1.70] |
  | friend_aljaz_2 | 2.35 | 1.35 | +1.00 [+0.20, +1.80] |
  | friend_aljaz_3 | 2.70 | 1.35 | +1.35 [+0.60, +2.10] |
  | friend_aljaz_4 | 1.85 | 1.05 | +0.80 [−0.10, +1.65] |
  | friend_aljaz_5 | 2.15 | 0.85 | +1.30 [+0.40, +2.20] |
  | friend_andy | 2.75 | 1.95 | +0.80 [+0.05, +1.65] |
  | greedy_deadend | 2.90 | 2.00 | +0.90 [+0.40, +1.40] |
  | rusher_camper | 2.85 | 2.10 | +0.75 [+0.10, +1.50] |
  | turtle | 3.00 | 2.90 | +0.10 [+0.00, +0.30] |

- **Reading**: the gain over greedy_v3 is larger outside the pool (+0.77) than inside it (+0.95 on validation 221–260, E-031, same scale), and no opponent goes negative. The planner-with-learned-leaf gain is not specific to our pool. The strongest outside teams remain friend_aljaz_1 and _4 (greedy_v4 1.65 / 1.85 PPG). The release gate (locked test seeds + held-out teams) is still the user's decision.

## E-036 — User decisions after the overnight session: greedy_v4 confirmed, reference pool 8 → 10 (2026-11-08)
- **Status**: done (decisions only, no games).
- **Decisions** (user, 2026-11-08 morning, after the overnight report):
  1. greedy_v4 is confirmed as `my_team.py` (it had been promoted "for now" at 03:35, E-032).
  2. `greedy_v4` and `lab5_smart` join the reference pool, which now has **10 members**: greedy_v4 (incumbent), greedy_v3, greedy_v2, greedy, feature, camper, rusher, choke, exploit_v2, lab5_smart. No member was dropped.
- **Changes**: `_reference_pool` and its doc string in `eval/league.json` (and the `submission` notes, which still said greedy_v3); evaluation.md §5; CLAUDE.md; agents.md verdicts (greedy_v3 → past version, lab5_smart → pool, new greedy_v4 row).
- **Consequences**: the accept rule's pool Δ is now over the 9 members other than the incumbent (the incumbent's games are the head-to-head). Pool numbers before this date used the 8-member pool (with lab5_smart and greedy_v4 as extra opponents in E-030 … E-035), so compare them only within one experiment. A candidate run plays 10 instead of 8 opponents (+25 % games).
- **Second round of decisions** (user, same morning): (3) run the release gate now (E-037); (4) draw a fresh validation list now; (5) drop greedy (v1) and rusher from the pool, plus any other member the analysis finds unnecessary (permission given for this once).
- **Pool trim** [verified analysis of the overnight runs; scratch script `pool_signal.py`]: per-opponent paired Δ of every arm against its reference in X1 (12 arms vs lab5_smart), X2 (4), E-033 (8 vs greedy_v4) and E-034 (7 vs greedy_v4):

  | member | between-arm signal sd (mean of 4 groups) | corr with rest-of-pool Δ | reference arm PPG against it | decision |
  |---|---|---|---|---|
  | lab5_smart | 0.21 (2 groups) | +0.91 | 2.20 | keep (closest rule-based relative) |
  | greedy_v2 | 0.17 | +0.95 | 2.35 | keep (past version, most signal) |
  | greedy_v3 | 0.16 | +0.82 | 2.21 | keep (previous incumbent) |
  | feature | 0.16 | +0.77 | 2.57 | keep (only simple patrol-defender team left; punishes timid candidates) |
  | greedy (v1) | 0.15 | +0.78 | 2.56 | **drop** (user; saturated, oldest) |
  | rusher | 0.13 | +0.84 | 2.48 | **drop** (user) |
  | exploit_v2 | 0.12 | +0.75 | 2.40 | keep (shadow defender) |
  | choke | 0.10 | +0.86 | 2.41 | keep (cut-cell defender) |
  | camper | 0.09 | +0.86 | 2.46 | keep (border camper) |

  Every member tracks the rest of the pool closely (corr 0.75–0.95), so two fewer members lose little signal. The low-signal members (camper, choke) are kept for their style: style diversity matters more than signal for generalisation to unknown tournament teams, and all pool teams are our own. New pool (**8**): greedy_v4, greedy_v3, greedy_v2, feature, camper, choke, exploit_v2, lab5_smart.
- **Fresh validation list**: see the entry for `eval/seeds/validation2.txt` in evaluation.md §4 (below).
- **Still open**: none of the earlier decisions; the release gate is E-037.

## E-037 — Release gate for `greedy_v4` on the locked test seeds (2026-11-08)
- **Status**: done. **Release gate passed** (all 5 pre-registered criteria). Pre-registered (commit 24c61aa) before any test-seed game was played.
- **Why**: user decision (2026-11-08, E-036): run the release gate of evaluation.md §2 for greedy_v4, which is in `my_team.py` (promoted E-032, confirmed by the user) and will play the tournament test run on 2026-11-23.
- **Already satisfied**: accepted under the rule (V1, E-031); ≥ 200 games with 0 crashes / violations (V1: 720); Linux / Python 3.8 timing under load (E-032: 40 games, 0 warnings, max move 0.283 s).
- **Setup**: `my_team.py` is byte-identical to `teams/greedy_v4.py` [verified, `cmp`], so the league entry `greedy_v4` stands for the submission. greedy_v4 and the previous incumbent greedy_v3 each play the non-mirror members of the new 8-member pool (greedy_v2, feature, camper, choke, exploit_v2, lab5_smart) and the two held-out teams (heldout_a, heldout_b), plus greedy_v4 vs greedy_v3, on **all 100 locked test seeds**, both colours: 17 pairs × 200 = 3,400 games, run `test2`, `--jobs 8`, `-q -c`, `--delay-step 0`. Repo commit at pre-registration in the commit message; framework `54cd83c`; Windows 11, Python 3.8.10.
- **Test-seed use 2 of 3** (evaluation.md §4). Held-out teams: totals per team only; their code and replays are not read (T-53).
- **Pre-registered rule** (as E-021). The release gate **passes** if and only if all hold:
  1. **Gates**: 0 crashes / forfeits, 0 engine time warnings, 0 sentinel violations in every greedy_v4 game; max move ≤ 0.5 s.
  2. **Pool**: paired Δ PPG (greedy_v4 − greedy_v3) over the 6 non-mirror pool members has a 95% CI lower bound > 0.
  3. **No regression**: for every opponent (pool and held-out) the paired Δ has a CI upper bound > −0.5.
  4. **Held-out**: the paired Δ over the two held-out teams has a CI upper bound > 0 (no significant regression against blind-written teams).
  5. **Head-to-head**: PPG(greedy_v4 vs greedy_v3) ≥ 1.5.
- **Action**: pass → greedy_v4 is the confirmed release candidate for the 2026-11-23 test run. Fail → greedy_v4 stays in `my_team.py` for now (the user confirmed it) and the failed criterion goes to the user, whose call a fallback to greedy_v3 would be. Also reported: the generalisation gap R (evaluation.md §4: mean PPG over the 6 pool members vs over the 2 held-out teams) for both agents, compared with E-021 (greedy_v3 R ≈ 29 %).
- **Results** [verified, run `test2`, 3,400 games, 2,556 s with 8 workers; summary in `eval/results/test2_summary.md`]:

  | agent | games | W-T-L | PPG [95% CI] | crashes / time warnings / violations | max move | p95 move |
  |---|---|---|---|---|---|---|
  | greedy_v4 | 1,800 | 1443-143-214 | **2.48** [2.40, 2.56] | 0 / 0 / 0 | 0.310 s | 0.125 s |
  | greedy_v3 | 1,800 | 813-252-735 | 1.50 [1.42, 1.57] | 0 / 0 / 0 | 0.065 s | 0.003 s |

  **Paired greedy_v4 − greedy_v3 per opponent** (200 games each):

  | opponent | greedy_v4 | greedy_v3 | paired Δ [95% CI] |
  |---|---|---|---|
  | lab5_smart | 2.23 | 1.04 | +1.18 [+0.91, +1.44] |
  | greedy_v2 | 2.54 | 1.56 | +0.98 [+0.74, +1.21] |
  | exploit_v2 | 2.64 | 1.75 | +0.89 [+0.69, +1.10] |
  | choke | 2.48 | 1.65 | +0.83 [+0.60, +1.06] |
  | feature | 2.65 | 2.10 | +0.56 [+0.38, +0.74] |
  | camper | 2.60 | 2.06 | +0.55 [+0.34, +0.74] |
  | heldout_a (held-out) | 2.48 | 1.44 | +1.04 [+0.77, +1.29] |
  | heldout_b (held-out) | 2.35 | 1.35 | +1.00 [+0.75, +1.24] |

  | criterion | result | pass |
  |---|---|---|
  | 1. gates | 0 crashes / forfeits, 0 time warnings, 0 sentinel violations in 1,800 greedy_v4 games; max move 0.310 s ≤ 0.5 s | ✓ |
  | 2. pool (6 non-mirror members, 1,200 paired games) | **+0.83 [+0.73, +0.94]** | ✓ |
  | 3. no regression (CI upper > −0.5 for every opponent) | worst camper +0.55 [+0.34, +0.74]; every opponent's CI is above 0 | ✓ |
  | 4. held-out (400 paired games) | **+1.02 [+0.85, +1.20]** | ✓ |
  | 5. head-to-head vs greedy_v3 (200 games) | **2.38** (greedy_v3 0.50) | ✓ |

  Team totals per game (greedy_v4 / greedy_v3): returned 16.9 / 11.2, conceded 9.0 / 10.7, deaths 0.48 / 0.99, food lost 1.3 / 2.6, games ended by returning 28 food 78 / 24 (of 1,800).
- **Generalisation gap** (evaluation.md §4; mean PPG over the 6 pool members vs over the 2 held-out teams, test seeds): greedy_v4 2.52 vs 2.42, **R ≈ 4 %**; greedy_v3 1.69 vs 1.40, R ≈ 18 % (E-021 measured 29 % for greedy_v3 against the old pool with greedy v1 and rusher, so the two R values are not comparable across experiments).
- **Reproducibility check** [verified]: greedy_v3's results against the opponents shared with E-021 on the same seeds are identical (camper 2.06, feature 2.10, choke 1.65, exploit_v2 1.75, heldout_a 1.44, heldout_b 1.35): deterministic agents replay the same games one month later, on the same framework commit.
- **Decision** (pre-registered rule): **the release gate passes**. greedy_v4 is the confirmed release candidate for the tournament test run on 2026-11-23. All release-gate items of evaluation.md §2 are now done: accepted (E-031), ≥ 200 clean games, Linux timing (E-032), locked test seeds + held-out teams (this entry).
- **Reading**: the gain over greedy_v3 holds on maps nobody looked at (+0.83 on the pool, +0.95 on validation 221–260) and is, if anything, larger against the two blind-written teams (+1.02) than against our own pool. The held-out teams were never used to build or tune greedy_v4 (T-53), and the planner's learned leaf was trained only against our own pool, so this is the best evidence we have that it generalises. Test seeds: 1 use left before new ones must be drawn.

## E-038 — V3: validation of override mode (`greedy_v5`) against greedy_v4 (2026-11-08)
- **Status**: done. **Rejected**: pool Δ −0.05 [−0.15, +0.05]; greedy_v4 stays. Pre-registered (commit 80c0506) before any game was played.
- **Why**: user request (2026-11-08): validate the one candidate left from the overnight session, `lab7_netf_override` (E-034: +0.06 [+0.00, +0.12] vs greedy_v4 over 1,440 tuning games on seeds 321–400, h2h 1.57, worst opponent camper −0.06).
- **File** `teams/greedy_v5.py` = `teams/greedy_v4.py` with one default changed: `plan='override'` (greedy decides; near a non-scared ghost the planner replaces greedy's move only when its best root value beats greedy's move by 0.3). Lint OK. **Identity**: greedy_v5 = `greedy_lab_v7.py` with lab7_netf_override's options, 8/8 games identical (seeds 27904464 / 85254603 × greedy_v3 / sparring_v2 × both colours, planner clock off).
- **Run** `n1_v3`: **validation2 seeds 1–80** (`--seeds validation2 --n-seeds 80`, the first use of the fresh list), candidates greedy_v5 and greedy_v4 against the 8-member pool (greedy_v4 = head-to-head, greedy_v3, greedy_v2, feature, camper, choke, exploit_v2, lab5_smart): 15 pairs × 160 = 2,400 games, `--jobs 8`. 80 seeds because a true +0.06 has only ≈ 30 % power at 40 seeds (≈ 50 % at 80; evaluation.md §2 prefers ≥ 80 seeds per decision, E-019).
- **Decision rule** (accept rule, evaluation.md §2, incumbent greedy_v4):
  1. Gates: lint OK; 0 crashes / forfeits, 0 time warnings, 0 sentinel violations in greedy_v5's games; max move ≤ 0.5 s.
  2. Pool: paired Δ PPG (greedy_v5 − greedy_v4) over the 7 non-incumbent pool members (1,120 paired games) has a 95% CI lower bound > 0.
  3. No regression: every opponent's paired Δ has a CI upper bound > −0.5; the minimum PPG against the past versions (greedy_v3, greedy_v2) does not drop by more than 0.5.
  4. Head-to-head: PPG(greedy_v5 vs greedy_v4) ≥ 1.5 (160 games).
  5. Confirmation: selection used tuning seeds 321–400 only; validation2 is unused ✓.
- **Action**: pass → `teams/greedy_v5.py` is copied to `my_team.py` (user: "if it passes, it becomes greedy_v5"), with its own behaviour page; WSL timing check of greedy_v5; the locked test-seed run (last of 3 uses) is kept for the final release candidate before 2026-11-23. Fail → greedy_v4 stays; `teams/greedy_v5.py` stays in the league as a rejected candidate (frozen once benchmarked), and the next promoted version gets the next free name.
- **V3 result** [verified, `n1_v3`, 2,400 games, validation2 seeds 1–80, 1,789 s with 8 workers]:

  | criterion | result | pass |
  |---|---|---|
  | 1. gates | lint OK; 0 crashes, 0 time warnings, 0 sentinel violations; max move 0.192 s (greedy_v4 0.320 s) | ✓ |
  | 2. pool Δ (greedy_v5 − greedy_v4, 7 members, 1,120 paired games) | **−0.05 [−0.15, +0.05]** | ✗ |
  | 3. no regression | worst exploit_v2 −0.13 [−0.28, +0.01], choke −0.12 [−0.28, +0.03]; past versions greedy_v3 −0.03, greedy_v2 +0.04 | ✓ |
  | 4. head-to-head vs greedy_v4 (160 games) | 1.51 (greedy_v4 1.23) | ✓ |

  Per opponent (greedy_v5 / greedy_v4 PPG): camper 2.61 / 2.67, choke 2.50 / 2.62, exploit_v2 2.49 / 2.62, feature 2.74 / 2.76, greedy_v2 2.56 / 2.51, greedy_v3 2.36 / 2.39, lab5_smart 2.29 / 2.31. Team totals per game (v5 / v4): returned 17.0 / 16.6, conceded 9.0 / 8.8, deaths 0.36 / 0.39, food lost 1.1 / 1.4, standoff moves 234 / 219, 28-food finishes 40 / 48.
- **Decision** (pre-registered rule): **rejected**. greedy_v4 stays in `my_team.py`; `teams/greedy_v5.py` stays in the league as a rejected candidate (frozen); the next promoted version gets the next free name (greedy_v6).
- **Reading**: the tuning-seed edge (+0.06 [+0.00, +0.12] over 1,440 games, E-034) did not replicate on fresh seeds; it is the second time tonight that a small tuning gain vanished on validation (the defender planner: +0.10 on tuning, −0.03 on V2). Override mode dies a little less and drops less food but concedes a little more and finishes fewer games by returning 28; overall it is equal to danger mode within ±0.15. [untested] Selecting the best of several E-034 arms on the same tuning seeds inflated its estimate (winner's curse, evaluation.md G3).

## E-039 — Improvements from the external review of greedy_v4 / greedy_v5 (2026-11-08)
- **Status**: done. Stage 2 **rejected** `lab12_combo` (pool −0.06 [−0.15, +0.02], h2h 1.37); greedy_v4 stays. Screen and option C splits pre-registered before any game. Screen pre-registered before any game was played.
- **Why** (user, 2026-11-08): have an external reviewer (Fable 5.1, maximum effort) inspect greedy_v4 and greedy_v5, propose at least two improvements to each, then think them through, implement them and test the new agents against greedy_v4 and our top 3 agents. Review: `docs/research/review_v4_v5.md` (read-only reviewer; tuning-seed data only, no test seeds, no held-out teams, no running validation).
- **Base**: greedy_v4 (V3 rejected greedy_v5 while the review ran, E-038), so the v4 proposals are arms on greedy_v4 and the v5 proposals one arm on override mode.
- **What was chosen and why** (from the review's 9 proposals plus two of ours):
  - `assist` (ours): 45 % of lost points are "they returned more" (review §2a) and the attacker spends 16–28 % of its moves as a ghost at the border (§2b). A non-scared attacker that is a ghost on our side intercepts a visible invader within 6 steps with the defender's intercept rule (cut its way home): two defenders instead of one, using time that is otherwise standoff. Differs from the rejected `recall` (E-025: called the attacker back from the enemy side on two invaders) in that it never leaves the enemy side for it and only acts on a visible, nearby invader.
  - `def_scared` (review V4-A, corrected): scared-defender posture (≥ 2 from the invader, on its way home, no dead ends; act normally once our timer ends before we can meet) and a capsule guard. The review's capsule condition sent the defender to a capsule the invader reaches first (it would arrive scared); ours requires that we get there strictly first, that the invader is within 5 and nearer the capsule than its own side.
  - `late_tie` (ours): 23 % of lost points are ties (§2a). In the last 40 own moves the attacker banks as soon as it carries food while the score is tied (before: only when behind).
  - `plan_blocked` (review V4-C): the reviewer verified that in danger mode the planner keeps control in border standoffs (its best values stay ≥ plan_min), so the standoff breaker never runs in greedy_v4; this lets the breaker count and act there.
  - `m1m2` (review V4-E): the built but never-played chase + intercept ghost models (min over models), 1,200 nodes each. Zero build cost; T-60 risk noted.
  - `v5fix` (review V5-A + V5-B): override mode with the all-die guard (keep greedy's move when every line dies in the model) and margin 0.1 instead of 0.3 when greedy's own root value is negative.
  - Not built this round, with reason: V4-B heavy-carrier safety (pool food lost is only 1.0–1.4 per game, little headroom; the gain is mostly against double attackers, which only the friend teams are, and they are diagnostics only); V4-D two-pronged entry (three prior negatives; its target situation, both enemies at home for 25 moves, is rare in our pool, so the screen could only show harm); V5-C hysteresis and V5-D wider trigger (low rank in the review; the trigger was flat in E-034); V5-E gap-aware breaker (sign untested even by the reviewer, and its fallback 'Stop at the opening' gives up the chance that a guard loses sight of a walking attacker).
- **File** `teams/greedy_lab_v12.py` = v11 + options `assist`, `assist_d`, `def_scared`, `late_tie`, `plan_blocked`, `ov_guard`, `ov_asym` (header). Lint OK. **Identity** (planner clock off): v12 with greedy_v4's options = greedy_v4, 3/3 games; v12 with greedy_v5's options = greedy_v5, 3/3. Smoke (`smoke12`, tuning seeds 141–143 vs greedy_v3 / lab5_smart, 12 games per arm): 0 crashes / warnings; games differing from greedy_v4: assist 4/12, def_scared 12/12, late_tie 1/12, plan_blocked 9/12, m1m2 10/12, v5fix 10/12 (every switch fires); max move 0.168 s (m1m2), others ≤ 0.095 s.
- **Screen** (`n2_s1`): arms `lab12_assist`, `lab12_defsc`, `lab12_latetie`, `lab12_pblock`, `lab12_m1m2`, `lab12_v5fix` and the reference `greedy_v4`, each against greedy_v4 (head-to-head), **the top 3 other agents** (greedy_v5: ≈ greedy_v4 on validation; lab7_netf_dplan: −0.03 vs greedy_v4 but wins the head-to-head 1.69; lab10_quad: ≈ greedy_v4, pooled −0.02) and the rest of the pool (greedy_v3, greedy_v2, feature, camper, choke, exploit_v2, lab5_smart); tuning seeds 101–140 (`--seed-offset 100`, last used in October for greedy_v2/v3-era screens, never for the leaf nets), both colours: 76 pairs × 80 = 6,080 games, `--jobs 8`.
- **Pre-registered rule**:
  - Per arm: paired Δ PPG vs greedy_v4 over the 10 non-incumbent opponents (800 paired games), per-opponent Δ, head-to-head vs greedy_v4 (80 games), diagnostics (returned, conceded, deaths, food lost, standoff moves).
  - An arm is **promising** if its Δ > 0 and no opponent's Δ is below −0.3.
  - **Stage 2**: candidate `lab12_combo` = greedy_v4 + every promising danger-mode switch (assist, def_scared, late_tie, plan_blocked, m1m2). `v5fix` competes only if it is promising and its Δ exceeds every promising danger-mode arm's; then it is the candidate alone. The candidate is validated on **validation2 seeds 81–160** against the 8-member pool plus the 3 top agents, paired with greedy_v4, under the accept rule (evaluation.md §2; criterion 2 over the 7 non-incumbent pool members; Δ over all 10 opponents reported). Only if it passes: `teams/greedy_v6.py` = v12 with the candidate's options as defaults (identity-checked) is copied to `my_team.py`, as for every accepted version. No arm promising → no stage 2.
- **Amendment (option C, user request, written while `n2_s1` was running and before any of its results was looked at; only the game count had been checked)**: split the two bundled arms after the screen, each only if its screen result is within the expected range stated to the user beforehand:
  - **A** (`v5fix` → `lab12_v5guard` = override + ov_guard only, `lab12_v5asym` = override + ov_asym 0.1 only): runs if `lab12_v5fix`'s Δ vs greedy_v4 ≥ −0.07 and its gates are 0 / 0 / 0.
  - **B** (`def_scared` → `lab13_defsc_posture` = scared-defender parts only, `lab13_defsc_cap` = capsule guard only; `teams/greedy_lab_v13.py` = v12 with `def_scared` widened to '1' | 'posture' | 'cap', lint OK, v13 `def_scared=1` = v12 `def_scared=1` on 2/2 games with the clock off): runs if `lab12_defsc`'s Δ ≥ −0.06 and its gates are 0 / 0 / 0.
  - Expected ranges given to the user beforehand (PPG Δ vs greedy_v4, [untested] estimates): assist +0.03 (−0.05 … +0.10), def_scared 0.00 (−0.06 … +0.05), late_tie +0.01 (0 … +0.02), plan_blocked +0.01 (−0.05 … +0.05), m1m2 −0.03 (−0.10 … +0.03), v5fix 0.00 (−0.07 … +0.05). Detection limit of the screen: CI half-width ≈ 0.08–0.10 per arm (800 paired games), so effects of +0.01 … +0.03 cannot be told from 0 here.
  - Run `n2_s2`: the split arms against the same 11 opponents on the same seeds (tuning 101–140, both colours), paired with greedy_v4's games in `n2_s1` (880 games per arm).
  - **Stage 2 with option C**: a split part replaces its bundle in the stage-2 rule; it is promising by the same rule (Δ > 0, no opponent below −0.3). If a bundle was not split, the bundle itself counts. Then stage 2 as above.
- **Screen result** [verified, `n2_s1`, 6,080 games, 5,839 s with 8 workers, `my_team.py` e95a786, framework 54cd83c]. Gates for every arm: lint OK, 0 crashes, 0 time warnings, 0 sentinel violations; max move ≤ 0.317 s (greedy_v4's own max 0.317 s).

  | arm | Δ vs greedy_v4, 10 opponents (800 paired) | exact | worst opponent | h2h vs greedy_v4 (80) | max move s | expected beforehand | promising (rule) |
  |---|---|---|---|---|---|---|---|
  | assist | +0.00 [−0.07, +0.08] | +0.0013 | lab10_quad −0.16 | 1.41 | 0.276 | +0.03 (−0.05 … +0.10) | yes, by the letter (+1 point in 800 games) |
  | def_scared | **+0.07 [−0.02, +0.15]** | +0.0663 | greedy_v2 −0.10 | 1.51 | 0.262 | 0.00 (−0.06 … +0.05) | yes (above the expected range) |
  | late_tie | −0.01 [−0.03, +0.00] | −0.0125 | lab10_quad −0.06 | 1.35 | 0.317 | +0.01 (0 … +0.02) | no |
  | plan_blocked | +0.00 [−0.10, +0.10] | +0.0013 | camper −0.18 | 1.39 | 0.150 | +0.01 (−0.05 … +0.05) | yes, by the letter (+1 point in 800 games) |
  | m1m2 | +0.03 [−0.05, +0.11] | +0.0300 | feature −0.03 | 1.34 | 0.268 | −0.03 (−0.10 … +0.03) | yes |
  | v5fix | +0.00 [−0.09, +0.09] | 0.0000 | camper −0.13 | 1.36 | 0.231 | 0.00 (−0.07 … +0.05) | no (Δ not > 0) |

  Per opponent (paired Δ vs greedy_v4, 80 games each; CI half-width ≈ 0.15–0.30):

  | opponent | assist | def_scared | late_tie | plan_blocked | m1m2 | v5fix |
  |---|---|---|---|---|---|---|
  | greedy_v5 | −0.03 | +0.25 | −0.04 | −0.12 | +0.04 | −0.11 |
  | lab7_netf_dplan | +0.06 | +0.23 | 0.00 | +0.11 | −0.01 | +0.10 |
  | lab10_quad | −0.16 | +0.24 | −0.06 | +0.14 | +0.06 | +0.07 |
  | greedy_v3 | +0.14 | +0.09 | 0.00 | +0.16 | +0.01 | +0.12 |
  | greedy_v2 | −0.03 | −0.10 | −0.03 | +0.04 | 0.00 | −0.03 |
  | feature | +0.04 | −0.07 | 0.00 | −0.11 | −0.03 | −0.04 |
  | camper | −0.10 | −0.05 | 0.00 | −0.17 | +0.14 | −0.12 |
  | choke | 0.00 | −0.09 | −0.03 | +0.03 | +0.01 | 0.00 |
  | exploit_v2 | +0.07 | +0.05 | +0.03 | −0.10 | +0.01 | 0.00 |
  | lab5_smart | +0.01 | +0.12 | 0.00 | +0.05 | +0.06 | 0.00 |

  Split by opponent group (post-hoc, not part of the rule; `summary --agents`):

  | arm | 7 pool members (560 paired) | top 3 (greedy_v5, lab7_netf_dplan, lab10_quad; 240 paired) |
  |---|---|---|
  | assist | +0.02 [−0.07, +0.11] | −0.04 [−0.16, +0.09] |
  | def_scared | −0.01 [−0.09, +0.06] | **+0.24 [+0.03, +0.46]** |
  | late_tie | −0.00 [−0.02, +0.01] | −0.03 [−0.07, +0.00] |
  | plan_blocked | −0.02 [−0.14, +0.10] | +0.04 [−0.11, +0.20] |
  | m1m2 | +0.03 [−0.05, +0.12] | +0.03 [−0.11, +0.18] |
  | v5fix | −0.01 [−0.10, +0.09] | +0.02 [−0.15, +0.20] |

  Diagnostics (team totals per game over the same 800 games; greedy_v4 on those games: returned 15.81, conceded 10.08, deaths 0.42, kills 0.68, food lost 1.45, standoff moves 217):

  | arm | returned | conceded | deaths | kills | food lost | standoff moves |
  |---|---|---|---|---|---|---|
  | assist | 15.48 | **9.62** | 0.41 | 0.77 | 1.39 | 225 |
  | def_scared | 15.92 | 9.83 | 0.38 | 0.73 | 1.41 | 234 |
  | late_tie | 15.77 | 10.08 | 0.42 | 0.68 | 1.47 | 217 |
  | plan_blocked | 15.89 | 10.17 | 0.39 | 0.69 | 1.28 | 245 |
  | m1m2 | 15.98 | 10.14 | 0.39 | 0.71 | 1.33 | 210 |
  | v5fix | 15.70 | 9.98 | 0.44 | 0.70 | 1.38 | 239 |
- **Reading**:
  - `def_scared` is the only arm with a visible effect, and it comes from the three strong opponents (+0.24 [+0.03, +0.46] over 240 games), which raid with capsules; against the 7 pool members it is −0.01. [untested] It is also the best of six arms on the same seeds (winner's curse, evaluation.md G3), so its true effect is likely smaller.
  - `assist` does what it was built for (conceded −0.46 per game, kills +0.09) but costs as much on attack (returned −0.33): zero net.
  - `plan_blocked` lets the breaker act (standoff moves +28, food lost −0.17) with no net effect; `late_tie` changes ≈ 1 % of games, net −0.01; `m1m2` is a small, even +0.03 everywhere.
- **Decisions under the rule**:
  - Promising: `assist`, `def_scared`, `plan_blocked`, `m1m2`. `assist` and `plan_blocked` qualify by +1 point in 800 games each; they stay in by the letter of the pre-registered rule (no change after seeing the data).
  - Not promising: `late_tie`, `v5fix`.
  - Option C: both conditions hold (`v5fix` 0.00 ≥ −0.07, `def_scared` +0.07 ≥ −0.06, gates 0 / 0 / 0), so `n2_s2` runs all four split arms (3,520 games).
  - [untested] Consequence for stage 2: criterion 2 counts the 7 pool members only, where `def_scared` is ≈ 0; its gain is against the top 3, which are reported but not counted.
- **Option C result** [verified, `n2_s2`, 3,520 games, 3,173 s with 8 workers; paired with greedy_v4's games in `n2_s1`]. Gates for all four arms: 0 crashes, 0 time warnings, 0 sentinel violations; max move ≤ 0.302 s.

  | arm | Δ vs greedy_v4, 10 opponents (800 paired) | exact | worst opponent | 7 pool members | top 3 | h2h vs greedy_v4 | promising (rule) |
  |---|---|---|---|---|---|---|---|
  | def_scared: posture only | **+0.07 [−0.02, +0.16]** | +0.0663 | greedy_v2 −0.14 | −0.01 [−0.09, +0.06] | **+0.25 [+0.04, +0.46]** | 1.44 | yes |
  | def_scared: capsule guard only | +0.01 [−0.03, +0.04] | +0.0088 | greedy_v3 −0.07 | −0.00 [−0.04, +0.03] | +0.04 [−0.05, +0.12] | 1.40 | yes |
  | v5fix: all-die guard only | +0.02 [−0.07, +0.11] | +0.0175 | camper −0.14 | +0.02 [−0.07, +0.12] | +0.01 [−0.17, +0.21] | 1.31 | yes, but below posture (+0.0663): does not compete |
  | v5fix: margin 0.1 only | +0.00 [−0.11, +0.11] | +0.0025 | camper −0.09 | −0.03 [−0.16, +0.09] | +0.08 [−0.10, +0.28] | 1.48 | yes, but below posture: does not compete |

  Reading: the whole `def_scared` effect is the scared-defender posture (+0.0663, the same as the bundle); the capsule guard changes few games. The two override fixes are each ≈ 0 (the guard alone +0.02, food lost per game with margin 0.1: 1.02 vs 1.45). [untested] Selection over ten arms on one seed set inflates the best one (G3).
- **Stage-2 candidate (by the rule)**: promising danger-mode parts are `assist`, both `def_scared` parts (so `def_scared='1'`, the full bundle), `plan_blocked` and `m1m2`; the v5 parts do not exceed the best promising danger-mode arm. `lab12_combo` (league.json) = greedy_v4's options + `plan_nodes=1200, plan_models=m1m2, assist=1, def_scared=1, plan_blocked=1` on `teams/greedy_lab_v12.py`. Lint OK. Smoke (`smoke_combo`, tuning 141–143 vs greedy_v3 / lab5_smart, 12 games): 8-2-2, 0 crashes / warnings / violations, max move 0.171 s.
- **Stage 2, pre-registered before any stage-2 game** (`n2_val`):
  - Command: `--candidate lab12_combo greedy_v4 --vs greedy_v4 greedy_v3 greedy_v2 feature camper choke exploit_v2 lab5_smart greedy_v5 lab7_netf_dplan lab10_quad --seeds validation2 --seed-offset 80 --n-seeds 80 --run n2_val --jobs 8`: validation2 seeds 81–160 (never used), both colours, 21 pairings × 160 = 3,360 games.
  - **Accept** `lab12_combo` over greedy_v4 if all hold (evaluation.md §2):
    1. lint OK; 0 crashes, 0 time warnings, 0 sentinel violations; max move ≤ 0.5 s.
    2. Paired Δ PPG over the 7 non-incumbent pool members (greedy_v3, greedy_v2, feature, camper, choke, exploit_v2, lab5_smart; 1,120 paired games) > 0 with 95 % CI lower bound > 0.
    3. No pool member with CI upper bound ≤ −0.5; min PPG against past versions (greedy_v3, greedy_v2) not down by more than 0.5.
    4. Head-to-head vs greedy_v4 ≥ 1.5 (160 games).
    5. Selection used tuning seeds 101–140 only, so these validation seeds are not selection seeds and this run is also the confirmation.
  - Reported, not counted: Δ over all 10 opponents and over the top 3.
  - If accepted: `teams/greedy_v6.py` = v12 with `lab12_combo`'s options as defaults (identity-checked) → `my_team.py`, picks page. It would then not yet have passed the release gate (locked test seeds have 1 use left; Linux timing), which is a separate step before 2026-11-23. If rejected: greedy_v4 stays.
- **Stage-2 result** [verified, `n2_val`, validation2 seeds 81–160, 3,360 games]. The run was stopped once by Claude Code at 2,492 games (the laptop ran low on memory) and resumed with `--resume --jobs 6` (871 games, 1,348 s): the 3 games in flight at the stop have records without a score ("no score file", harness errors from the stop, not agent crashes); `summary` skips them and all 3,360 scheduled games were scored.

  | criterion | result | pass |
  |---|---|---|
  | 1. gates | lint OK; 0 crashes, 0 time warnings, 0 sentinel violations; max move **0.424 s** (greedy_v4 0.349 s), p95 0.279 s (greedy_v4 0.126 s) | ✓ |
  | 2. pool Δ (lab12_combo − greedy_v4, 7 members, 1,120 paired games) | **−0.06 [−0.15, +0.02]** | ✗ |
  | 3. no regression | worst camper −0.25 [−0.43, −0.07] (upper > −0.5); past versions: greedy_v3 2.46 vs 2.61, greedy_v2 2.66 vs 2.67 | ✓ |
  | 4. head-to-head vs greedy_v4 (160 games) | **1.37** (63-30-67) | ✗ |

  Reported, not counted: all 10 opponents −0.07 [−0.16, +0.02]; top 3 −0.08 [−0.26, +0.11] (greedy_v5 −0.14, lab10_quad −0.23, lab7_netf_dplan +0.13). Per pool member: camper −0.25, greedy_v3 −0.14, feature −0.04, exploit_v2 −0.03, choke −0.01, greedy_v2 −0.01, lab5_smart +0.04.

  Team totals per game (lab12_combo / greedy_v4, all games): returned 14.5 / 15.3, conceded 9.3 / 9.4, deaths 0.34 / 0.33, food lost 0.8 / 1.0, Pacman moves 129 / 136, standoff moves 243 / 207, 28-food finishes 10 / 23.
- **Decision** (pre-registered rule): **rejected** (criteria 2 and 4). greedy_v4 stays in `my_team.py`; no greedy_v6. `lab12_combo` stays in the league as a rejected candidate.
- **Reading**:
  - The combination attacks less: fewer Pacman moves (−7), more standoff moves (+36), fewer returned (−0.8) and less than half the 28-food finishes, for no defensive gain (conceded −0.1). [untested] Three of its four switches each take time from the attack (`assist` sends the attacker to defend, `plan_blocked` hands border standoffs to the waiting breaker, `m1m2` plans against more pessimistic ghosts); alone each was ≈ 0 on tuning, together they add up.
  - `def_scared`'s tuning-seed gain against the top 3 (+0.24) does not show here (the combo's top-3 Δ is −0.08), but the combo cannot separate it from the other switches.
  - `m1m2` roughly doubles the planner's p95 move time (0.279 s vs 0.126 s); max 0.424 s is close to the 0.5 s budget.
  - Third time today that tuning-seed gains did not survive validation (defender planner E-032, override E-038, this). Two of the four "promising" arms were +1 point in 800 games: "Δ > 0" lets noise into a combination (new trap T-61).

## E-040 — greedy_v4 (`my_team.py`) vs the friend's second version, `friend_andy_v2` (2026-11-08)
- **Status**: done. Diagnostic only (friend teams are never decision inputs).
- **Question** (user, 2026-11-08): how does our submission do against the friend's new team (`friends/andy/andy_v2.py`, received 2026-11-08), with the same evaluation as for the other friend teams (E-024)?
- **Setup**: `eval/evaluate.py play --candidate submission --vs friend_andy_v2 --seeds tuning --n-seeds 250 --jobs 6 --run friend_andy_v2_vs_v4`: tuning seeds 1–250 (the same as E-024), both colours, 500 games, with `-c`; 564 s. `my_team.py` = greedy_v4 (byte-identical to `teams/greedy_v4.py`, commit e95a786), framework 54cd83c, Windows 11, Python 3.8.10. Before running, the friend's file was checked only for safety with a grep (imports: `random`, `heapq`, the framework; the only `eval(...)` is the template's `create_team`; no file / process / thread calls, no `random.seed`, no catch-all `except`); its strategy was not studied. League entry `friend_andy_v2`; `friends/` stays gitignored.
- **Results** [verified]:

  | agent | games | W-T-L | PPG [95% CI] | win % [exact CI] | avg margin | crash / warnings / violations | max move s |
  |---|---|---|---|---|---|---|---|
  | submission (greedy_v4) | 500 | 419-52-29 | **2.62 [2.54, 2.70]** | 84 [80, 87] | +9.0 | 0 / 0 / 0 | 0.193 |
  | friend_andy_v2 | 500 | 29-52-419 | 0.28 [0.21, 0.35] | 6 [4, 8] | −9.0 | 0 / 0 / – | 0.076 |

  | side we play | W | T | L |
  |---|---|---|---|
  | red | 213 | 22 | 15 |
  | blue | 206 | 30 | 14 |

  | per game | returned | conceded | deaths | kills | food lost | max carried | 28-finishes |
  |---|---|---|---|---|---|---|---|
  | submission | 15.7 | 6.7 | 0.76 | 1.67 | 1.3 | 10.5 | 21 |
  | friend_andy_v2 | 6.7 | 15.7 | 1.67 | 0.76 | 1.4 | 4.8 | 0 |

- **Comparison with earlier friend runs** (different versions on both sides, so not a like-for-like test): E-024 greedy_v3 vs friend_andy (v1), same seeds: 2.10 PPG, 329-62-109. E-035 greedy_v4 vs friend_andy (v1), tuning 501–510: 2.75 over 20 games.
- **Conclusion**: [verified] greedy_v4 beats `friend_andy_v2` clearly on both colours (84 % wins, 6 % losses). [untested] Whether andy_v2 is stronger than andy v1 would need greedy_v4 vs friend_andy on the same 250 seeds. Tuning seeds only; no validation or test budget used.

## E-041 — greedy_v4 and greedy_v3 vs 15 public entries from last year's (2025) UPF contest (2026-11-11)
- **Status**: done. Diagnostic only (outside teams are never decision inputs; no accept/reject decision made).
- **Question** (user, 2026-11-11): how do our agents do against last year's contest entries, some of which placed near the top? The user put 15 public repos in `last_year_winners/` (gitignored, like `friends/`).
- **Setup**: before running, each `my_team.py` was checked only for safety with a grep: stdlib + framework imports only, the only `eval(...)` is the template's `create_team`, no file / process / thread / network calls, no `random.seed`. Their strategies were not studied (rule 7). League entries `lyw_*` (`ours: false`, frozen). For LL_Autonomous_Pacman the repo-root `my_team.py` was used (it differs from `pacman-agent/my_team.py`). Smoke run `lyw_smoke` (tuning seed 1, both colours), then `eval/evaluate.py play --candidate greedy_v4 greedy_v3 --vs <14 lyw teams> --seeds tuning --seed-offset 1 --n-seeds 25 --jobs 8 --run lyw_vs_v4v3`: tuning seeds 2–26, both colours, 1400 games, `-c`, 1613 s. greedy_v4 = `my_team.py` (byte-identical, commit e95a786), framework 54cd83c, Windows 11, Python 3.8.10.
- **Excluded**: `In-The-Fridge` crashes on its first move every game on this framework (`AttributeError: 'dict_keys' object has no attribute 'mapping'`, its line 240) [verified, smoke run + direct run]. It was not patched.
- **Opponent bug**: `despookjes` crashes in about 41 % of games (`UnboundLocalError: local variable 'min_invader_distance'`, its line 373, reproduced on RANDOM99112321) and is also slow (max move 1.37 s, 21 time warnings, 3 max-warning forfeits). Those games count as our wins; the table also gives PPG without them.
- **Results** [verified] (50 games per pairing; sorted by greedy_v4 PPG; v4 − v3 is paired on the same seed and colour):

  | opponent | v4 W-T-L | v4 PPG | v4 avg margin | v3 W-T-L | v3 PPG | v4 − v3 [95% CI] | opp. forfeits vs v4 | v4 PPG excl. forfeits |
  |---|---|---|---|---|---|---|---|---|
  | flagrats | 29-7-14 | **1.88** | +3.1 | 32-7-11 | 2.06 | −0.18 [−0.63, +0.27] | 0 | 1.88 |
  | pacman_agent | 33-8-9 | 2.14 | +2.7 | 22-9-19 | 1.50 | +0.64 [+0.21, +1.07] | 0 | 2.14 |
  | dotgobblers | 38-6-6 | 2.40 | +7.3 | 29-9-12 | 1.92 | +0.48 [+0.07, +0.89] | 0 | 2.40 |
  | autsys_pacman | 38-11-1 | 2.50 | +11.2 | 33-13-4 | 2.24 | +0.26 [−0.15, +0.67] | 0 | 2.50 |
  | pacman_as | 39-10-1 | 2.54 | +9.8 | 37-10-3 | 2.42 | +0.12 [−0.16, +0.40] | 0 | 2.54 |
  | despookjes | 42-4-4 | 2.60 | +5.6 | 40-6-4 | 2.52 | +0.08 [−0.28, +0.44] | 19 | 2.35 |
  | ll_autonomous_pacman | 41-7-2 | 2.60 | +8.6 | 23-13-14 | 1.64 | +0.96 [+0.54, +1.38] | 0 | 2.60 |
  | pacmancontest | 40-10-0 | 2.60 | +9.7 | 34-8-8 | 2.20 | +0.40 [+0.03, +0.77] | 0 | 2.60 |
  | pacman_agent_bonatarda | 43-6-1 | 2.70 | +13.5 | 43-4-3 | 2.66 | +0.04 [−0.26, +0.34] | 0 | 2.70 |
  | thedotdominators | 43-7-0 | 2.72 | +13.4 | 40-10-0 | 2.60 | +0.12 [−0.16, +0.40] | 0 | 2.72 |
  | clingho_pacman | 46-4-0 | 2.84 | +13.1 | 42-7-1 | 2.66 | +0.18 [−0.06, +0.42] | 0 | 2.84 |
  | idontthink | 48-1-1 | 2.90 | +15.2 | 39-3-8 | 2.40 | +0.50 [+0.16, +0.84] | 0 | 2.90 |
  | pacboys | 48-2-0 | 2.92 | +16.5 | 48-2-0 | 2.92 | +0.00 [−0.11, +0.11] | 0 | 2.92 |
  | toopac | 50-0-0 | 3.00 | +19.1 | 46-0-4 | 2.76 | +0.24 [+0.01, +0.47] | 0 | 3.00 |

  | overall (700 games each) | W-T-L | PPG [95% CI] | win % | excl. opponent forfeits | crash / warnings / max move s |
  |---|---|---|---|---|---|
  | greedy_v4 | 578-83-39 | **2.60 [2.51, 2.68]** | 83 | 2.58 (681 games) | 0 / 0 / 0.312 |
  | greedy_v3 | 508-101-91 | 2.32 [2.22, 2.43] | 73 | 2.30 (678 games) | 0 / 0 / 0.080 |
  | v4 − v3, paired | | **+0.27 [+0.18, +0.37]** | | | |

  greedy_v4 by colour: red 287-36-27, blue 291-47-12.
- **Notes**: the sentinel's "agent is not a CaptureAgent" flag on 8 of the teams only means they import `capture_agents` without the `contest.` prefix (a second copy of the class); it does not change their play. "No sentinel report" on our side happens only in games the opponent forfeited early; our engine records show 0 problems in all 1400 games.
- **Conclusion**: [verified] greedy_v4 beats every one of the 14 working entries on average (lowest 1.88 PPG vs flagrats), and it is ahead of greedy_v3 overall (+0.27, CI above 0), the same direction as E-032/E-037 on our own pool. The hardest opponents here are `flagrats` (14 losses in 50, the only pairing where v4 is not ahead of v3) and `pacman_agent` (9 losses). [untested] Why we lose to flagrats; `eval/replay_probe.py classify` on those games would show it. Tuning seeds only; no validation or test budget used.
- **Follow-up: idea study** (user request, 2026-11-11). The six teams that scored most against us or held our scoring lowest (flagrats, DotGobblers, pacman_agent, LL_Autonomous_Pacman, AutSys, TheDotDominators; plus pacman_AS) were read for ideas only, by three reading agents briefed to describe tactics in words and never reproduce code (rule 10); no code was copied. Findings [source = their code; effects on play untested]:
  - flagrats: both agents attack whenever no enemy is a Pacman (reads hidden `is_pacman`); once an invader appears, the agent closer to it (or the one on its start square, or the one carrying less) defends; two attackers split food by top / bottom half of the map; ghost cells and their neighbours are walls in the food search.
  - DotGobblers: ghost-penalised path cost (each step costs 1 + 10·max(0, 5 − ghost distance)), food chosen by path cost minus cluster size, homing pressure carried × home distance growing with time (small loads), a per-move penalty for staying home, and a scared defender that crosses to eat while scared.
  - pacman_agent: a defender that stands still halfway between our-side capsule and the border, goes to just-eaten food, chases only visible invaders; the attacker takes the capsule first and returns at 3 (10 while ghosts are scared).
  - LL_Autonomous: particle filters with hidden `is_pacman` to hunt a hidden raider, border interception, camping on a precomputed food-sealing bottleneck, layered return triggers (carried × distance home).
  - AutSys / TheDotDominators / pacman_AS: one fixed visible-only defender each; they barely attack, so our raider meets two ghosts (likely why our returns are low against them).
  - Already tested by us in some form: capsule guard (E-039 `cap`), bottleneck / choke defence (`choke`, H-M03), belief hunting of hidden invaders (E-019, E-025), food clusters (E-029), return thresholds (E-007/E-010/E-011).
- **flagrats split by its double attack** [verified, E-041 games; "double attack" = both its agents > 60 Pacman moves]:

  | | games | our W-T-L | they return | we return |
  |---|---|---|---|---|
  | greedy_v4, flagrats single attack | 24 | 14-6-4 | 3.7 | 9.8 |
  | greedy_v4, flagrats double attack | 26 | 15-1-10 | 19.8 | 20.0 |
  | greedy_v3, flagrats single attack | 32 | 20-7-5 | 5.8 | 10.9 |
  | greedy_v3, flagrats double attack | 18 | 12-0-6 | 18.2 | 21.7 |

  Double-attack games become scoring races, and 10 of greedy_v4's 14 losses to flagrats are in them. New untested ideas are listed in agents.md "Open (untested) ideas".

## E-042 — greedy_v4 vs flagrats, 500 games: where we lose points (2026-11-11)
- **Status**: done. Diagnostic only (an outside team; no accept/reject decision).
- **Question** (user, 2026-11-11): play 500 games of greedy_v4 against the strongest last-year entry (flagrats, E-041), 250 as red and 250 as blue on random maps, and find our common pitfalls.
- **Setup**: `eval/evaluate.py play --candidate greedy_v4 --vs lyw_flagrats --seeds tuning --seed-offset 26 --n-seeds 250 --jobs 8 --run flagrats_500`: 250 `RANDOM<seed>` maps (tuning seeds 27–276), each played once per colour, `-c`. greedy_v4 = `my_team.py` (commit e95a786), framework 54cd83c, Windows 11, Python 3.8.10. Then `eval/replay_probe.py classify`, `replay --worst 99 --events` (every non-win), `replay --include-wins --sample 100 --sample-seed 1 --events`, `eval/pitfall_probe.py` on all 500 games (new local tool: re-records each game and measures double invasions, scared windows and the attacker's home moves from the true state; re-recorded scores = original scores in 500/500 games), and `eval/trace_game.py game` on single games.
- **Result** [verified]: greedy_v4 **401-35-64, 2.48 PPG [2.38, 2.57]**, 80 % wins; 0 crashes / warnings / violations, max move 0.305 s. Per game: returned 18.6, conceded 11.6, deaths 0.52, kills 1.51; 28-food finishes 65 us / 19 them. (E-041 on 50 games: 1.88; this larger sample puts it at 2.48.)
- **Non-wins by type** (classify + true-state replays, 99 games, 262 points lost):

  | type | games | points lost | what happens |
  |---|---|---|---|
  | they return more, close margin (−1 … −6 mostly) | 30 | 78 (30 %) | two invaders 39 % of invaded plies; our defender scared for long stretches |
  | out-raced: they reach 28 first | 19 | 57 (22 %) | two invaders 52 % of invaded plies; defender gap 10.2; we return 13.4 |
  | our deaths (≥ 3 or ≥ 6 food lost) | 15 | 45 (18 %) | 2.2 deaths, 10.7 food dropped per game |
  | equal trade | 17 | 34 (13 %) | — |
  | 0-0, we crossed but returned nothing | 12 | 24 (9 %) | standoff: 151 standoff plies per game |
  | 0-0, we never crossed | 6 | 12 (5 %) | standoff: attacker loops at one border entry all game |

- **Pitfall 1: their capsule opens our half** [verified]. Per game, losses vs wins: their capsules eaten 1.69 vs 0.96 (≥ 1 in 94 % of losses, 59 % of wins; from the 99 non-wins and the 83 wins in the sample); plies our defender is scared 214 vs 116; food they eat while our defender is scared 11.7 vs 6.5; our scared defender eaten 0.44 vs 0.19. In the non-wins 36 of our defender's 39 deaths are as a scared ghost on our side, 24 of them in dead ends. In plies with two invaders our defender is scared 48 % of the time. [source: flagrats' code, E-041 follow-up] its attacker heads for the capsule when chased by a visible ghost within 5.
- **Pitfall 2: double invasions** [verified]. Losses vs wins: 267 vs 149 plies with two invaders, 5.7 vs 3.6 double-invasion episodes, they eat 14.2 vs 7.6 food in those plies; our attacker is on their side in 70 % of those plies (82 % in wins); kills 1.16 vs 1.64 and the invaders we kill carry 2.7 vs 4.5 food. Pitfalls 1 and 2 overlap (scared defender + two invaders).
- **Pitfall 3: chokepoint standoffs end 0-0** [verified]. 18 of 500 games (36 points). Example RANDOM44089071 (red and blue both 0-0): both flagrats agents sit at the choke (20, 10)/(20, 11) all game (attackers frozen by our shadowing defender at (16, 10)/(16, 11)); our attacker, carrying 0, is "blocked" and the standoff breaker keeps "switching" to the entry it already stands at, (16, 1): a 3-cell loop (16, 1)–(16, 3) from its move 49 to 300. Attacker moves at home within 2 of the border: 104 per game in ties vs 66 in wins. On the 14 standoff maps greedy_v4 scores 1.50 PPG over both colours (`trace_game.py profile`, 28 games).
- **Pitfall 4: big loads die when the winning trip is on** [verified on one trace]. Six of our attacker's deaths in non-wins carry ≥ 10 food (28, 22, 20, 14, 12, 12), one in the 83 sampled wins. RANDOM44089071 is not this case; RANDOM20986694 (blue): behind 0–23, `open_goal` let the attacker keep eating to 28 carried (both enemies were on our side), it then went home under "this trip wins", met a returning ghost, and `evade` stepped back and forth in a pocket (8 deep) until eaten, −25 final. The planner is off in that state (greedy_v4 decision list: special cases "fewer than 3 food left" and "returned + carried reaches the win threshold" stay with greedy).
- **Other numbers**: attacker deaths 0.70 per game in losses vs 0.23 in wins; dead-end deaths in non-wins: the killer was in sight at the entry in 80 % and could beat us to the exit in 89 %.
- **Conclusion**: [verified] most lost points against flagrats come from our defence when flagrats eats our capsule and/or sends both agents (pitfalls 1–2, about 135 of 262 points), then 0-0 chokepoint standoffs (36) and deaths with a large load (pitfall 4). [untested] Whether fixing them helps beyond flagrats; E-039 already found the scared-defender posture worth +0.24 [+0.03, +0.46] against the three strong opponents that raid with capsules, and ≈ 0 against our pool. Tuning seeds only.

## E-043 — Fixes for the pitfalls found against last year's teams (2026-11-11)
- **Status**: pre-registered (this entry was committed before any screening or validation game was played).
- **Why**: user request (2026-11-11) after E-042: build fixes for the pitfalls, think before implementing, and test against our own agents as well as last year's teams.
- **New evidence used for the design** (tuning seeds only; these games are design data, so the screen and the validation below use other seeds):
  - Against the 14 last-year teams (E-041 data, tuning 2–26) **0-0 ties are 10.4 % of greedy_v4's games and 58 % of its non-wins** (71 of 122); against our pool they are 0.6 % (E-039 `n2_s1`, 1,280 games). Big-load deaths (one death carrying ≥ 10) are 2–3 % of games against both.
  - Two 0-0 mechanisms, from traces (`trace_game.py`, `replay_probe.py`):
    - **P3a, breaker loop** (RANDOM69598886 vs AutSys; RANDOM44089071 vs flagrats): no race-safe food (`food_is_safe` treats every visible ghost as an optimal interceptor, and our defender's sight shows the enemies to the attacker), the standoff breaker picks the entry whose crossing is farthest from the ghosts, which is the entry it just tried: a 3-cell loop (16, 1)–(16, 3) for the whole game.
    - **P3b, frozen carrier** (RANDOM79095214 vs pacman_agent, also 0-0 vs AutSys and pacManContest): the attacker carries 8, a stationary guard sits 15 steps away near the border, greedy finds no race-safe way home, the planner is not triggered (no ghost within 7), and `evade` stands still for ~240 moves.
  - Pitfall 4 (E-042, RANDOM20986694): `open_goal` checks whether an enemy can reach *us*, not whether it can reach our *crossing* first, and its margin does not grow with the load; then the special case "this trip wins" keeps the planner off.
- **Code**: `teams/greedy_lab_v14.py` = v13 + five default-off options (header). Lint OK. **Identity**: v14 with greedy_v4's options and every new option off makes exactly the same moves as greedy_v4 in 32/32 recorded games (4 maps × 4 opponents × 2 colours, full action sequences compared). Smoke (`smoke_lab14`, 30 games): 0 crashes / warnings / violations, max move 0.127 s. Single-game sanity check on the design games (not a decision input): plan_stuck turns the frozen-carrier and breaker-loop 0-0s into +8 and +13, brk_tabu the loop into +13; plan_special does not change the 28-food game (no line survives in the pocket either).
- **Arms** (each = greedy_v4 + one switch; league entries):

  | arm | league entry | switch | pitfall | expected Δ vs greedy_v4 [untested estimate] |
  |---|---|---|---|---|
  | stuck planner | `lab14_stuck` | `plan_stuck=1` (`stuck_moves` 8) | 3 (P3a, P3b) | last-year +0.10 (0 … +0.25), pool −0.02 (−0.10 … +0.05) |
  | breaker tabu | `lab14_tabu` | `brk_tabu=1` | 3 (P3a) | last-year +0.05 (0 … +0.12), pool 0.00 (−0.05 … +0.05) |
  | special-case planner | `lab14_special` | `plan_special=1` | 4 | ±0.02 |
  | safer open_goal | `lab14_opensafe` | `open_safe=1` | 4 | 0.00 (−0.10 … +0.08): fewer big losses, but banks earlier |
  | scared raid | `lab14_raid` | `scared_raid=1` | 1, 2 | +0.03 (−0.08 … +0.10) |
  | scared posture | `lab13_defsc_posture` (existing) | `def_scared=posture` | 1 | +0.03 (E-039: +0.07 tuning, +0.25 vs capsule raiders, −0.01 pool) |

- **Screen** (`--run scr14`): candidates greedy_v4 and the six arms, each against the 7 non-mirror pool members (greedy_v3, greedy_v2, feature, camper, choke, exploit_v2, lab5_smart), greedy_v4 (head-to-head; skipped for itself) and 7 last-year teams (flagrats, pacman_agent, autsys_pacman, pacmancontest, pacman_as, dotgobblers, ll_autonomous_pacman), on **tuning seeds 561–584** (24 maps × 2 colours; no overlap with the design data, tuning 2–276), `-c`, 8 workers. 4,992 games.
  - **Promising** (all must hold): gates pass (0 crashes / forfeits caused by the arm, 0 time warnings, 0 violations, max move ≤ 0.5 s); paired Δ over the 7 last-year teams **≥ +0.05**; paired Δ over the 7 pool members **≥ −0.03**; head-to-head vs greedy_v4 **≥ 1.40**. (T-61: arms ≈ 0 are never combined.)
  - **Stage-2 candidate** = greedy_v4 + every promising arm (they are compatible: raid acts only while every enemy is a Pacman, posture otherwise; tabu and stuck act in different branches). None promising → stop and report.
- **Stage 2 = decision run** (`--run val14`): the candidate and greedy_v4 against the same 7 pool members, greedy_v4 (head-to-head) and **all 14 working last-year teams**, on **validation2 seeds 161–200** (fresh), both colours, `-c`.
  - **Accept rule** (user decision 2026-11-11, "pool guard + last-year gain"; replaces the pool-improvement criterion of evaluation.md §2 for this decision only): (1) gates as above for the candidate; (2) pool guard: paired Δ over the 7 pool members ≥ −0.03 (point estimate) and every pool member's paired-Δ CI upper bound > −0.5; (3) head-to-head PPG(candidate vs greedy_v4) ≥ 1.5; (4) **paired Δ over the 14 last-year teams, pooled with equal weight, 95 % CI lower bound > 0** (`eval/group_compare.py`, bootstrap over whole seeds). Single last-year teams are reported, never decisive.
  - **Action**: pass → the candidate becomes the proposed incumbent; it goes into `my_team.py` only after the user confirms, and a release gate on the locked test seeds (use 3 of 3) is the user's call. Fail → greedy_v4 stays; results are logged.
- **Screen result** (`scr14`, 4,992 games, my_team.py = greedy_v4 at e95a786, framework 54cd83c) [verified]. Paired Δ vs greedy_v4 on the same opponent, seed and colour (`eval/group_compare.py`); every arm passed the gates (0 crashes / forfeits / warnings / violations; max move 0.22–0.34 s):

  | arm | Δ pool (7) [95 % CI] | Δ last-year (7) [95 % CI] | h2h vs greedy_v4 | max move | promising? |
  |---|---|---|---|---|---|
  | `lab14_stuck` | +0.000 [−0.030, +0.027] | **+0.068 [+0.027, +0.113]** | 1.44 | 0.265 s | **yes** |
  | `lab14_tabu` | +0.006 [0.000, +0.018] | +0.006 [0.000, +0.018] | 1.48 | 0.285 s | no (last-year < +0.05) |
  | `lab14_special` | 0.000 (identical games) | 0.000 (identical games) | 1.42 | 0.221 s | no |
  | `lab14_opensafe` | −0.006 [−0.086, +0.065] | +0.060 [−0.042, +0.170] | **1.27** | 0.247 s | no (h2h < 1.40) |
  | `lab14_raid` | 0.000 (identical games) | +0.036 [−0.027, +0.104] | 1.42 | 0.343 s | no (last-year < +0.05) |
  | `lab13_defsc_posture` | **−0.036** [−0.119, +0.027] | +0.009 [−0.104, +0.116] | 1.50 | 0.298 s | no (pool < −0.03) |

  - `lab14_stuck` per opponent: gains vs autsys +0.21, pacman_as +0.15, pacmancontest +0.08, ll_autonomous +0.04, lab5_smart +0.06; loss vs choke −0.08 [−0.21, 0.00]; identical games vs flagrats, pacman_agent, dotgobblers and 4 pool members. So the frozen-carrier / breaker-loop 0-0s it targets appear in only a few of these 24 maps.
  - `lab14_special` never changed a game: the "≤ 2 food" and "trip wins" situations with a ghost within 7 are rare, and in them the planner chose greedy's move.
  - `lab14_opensafe`: +0.35 vs pacman_agent, −0.15 vs dotgobblers, and it loses the mirror (1.27): banking earlier costs points against an equal opponent.
  - **Stage-2 candidate** = greedy_v4 + `plan_stuck` = the existing entry `lab14_stuck` (no new file or entry needed).
- **Stage-2 result** (`val14`, validation2 161–200, 3,440 games; my_team.py = greedy_v4 at e95a786, framework 54cd83c) [verified]. The run was stopped by Claude Code at 3,375 games because the laptop ran low on memory (not the run's fault) and finished with `--resume --jobs 4`; no game was replayed or dropped.

  | accept criterion (pre-registered) | result | pass? |
  |---|---|---|
  | (1) gates: 0 crashes / forfeits / warnings / violations | 1,760 games: 0 / 0 / 0 / none; max move 0.342 s (greedy_v4 0.334 s) | yes |
  | (2) pool guard: Δ over the 7 pool members ≥ −0.03 | −0.011 [−0.036, +0.014] (560 paired) | yes |
  | (2) every pool member's CI upper > −0.5 | worst exploit_v2 −0.07 [−0.17, 0.00] | yes |
  | (3) head-to-head PPG(lab14_stuck vs greedy_v4) ≥ 1.5 | **1.32** (80 games, **26-28-26**); greedy_v4 vs lab14_stuck also 1.32 | **no** |
  | (4) Δ over the 14 last-year teams, CI lower > 0 | **+0.051 [+0.029, +0.074]** (1,120 paired) | yes |

  | last-year team | PPG lab14_stuck | PPG greedy_v4 | Δ [95 % CI] |
  |---|---|---|---|
  | pacman_agent | 2.29 | 2.11 | +0.17 [+0.04, +0.34] |
  | thedotdominators | 2.92 | 2.80 | +0.12 [+0.03, +0.28] |
  | autsys_pacman | 2.83 | 2.74 | +0.09 [0.00, +0.20] |
  | flagrats | 2.56 | 2.48 | +0.09 [0.00, +0.23] |
  | pacman_as | 2.90 | 2.81 | +0.09 [−0.03, +0.21] |
  | clingho / idontthink | 2.84 / 2.89 | 2.80 / 2.85 | +0.04 each |
  | despookjes / pacboys / pacmancontest | 2.83 / 2.96 / 2.96 | 2.80 / 2.94 / 2.94 | +0.03 each |
  | dotgobblers / ll_autonomous / bonatarda / toopac | — | — | 0.00 |

  - Ties against the 14 last-year teams: 49 for lab14_stuck vs 64 for greedy_v4 (of 1,120 games each): the fix does what it was built for, and never lowers the PPG against any single last-year team.
  - **Verdict by the letter of the rule: fail** (criterion 3); greedy_v4 stays. The head-to-head is a dead heat (26-28-26; screen 20-9-19), not a loss.
  - **Finding (T-62)**: the threshold 1.5 is evaluation.md's "A is not losing to the incumbent", but with ties PPG = 1.5 − T/(2n) when wins = losses, so an *equal* agent scores 1.5 only without ties. Here 35 % of the mirror games are ties, so an equal agent scores ≈ 1.32 and the criterion demands a head-to-head *win*. Whether to keep the rule as written, or to re-read criterion 3 as "wins ≥ losses" for this decision, is the user's call; it was not changed after seeing the data.
- **Stage 3 = confirmation run** (user decision 2026-11-11 after stage 2: "confirm on fresh seeds"; this bullet was committed before any stage-3 game was played). `--run conf14`: lab14_stuck and greedy_v4 against the same 7 pool members and each other (head-to-head) on **validation2 seeds 201–240** (fresh, unused), both colours, `-c`, 1,200 games. The last-year gain is not re-tested (stage 2 already measured it on 14 teams).
  - **Accept** (all must hold): (1) gates as above; (2) pool guard: paired Δ over the 7 pool members ≥ −0.03 and every member's CI upper bound > −0.5; (3) head-to-head **wins ≥ losses** for lab14_stuck vs greedy_v4 over these 80 games (replaces "PPG ≥ 1.5", T-62).
  - **Action**: pass → lab14_stuck is the proposed incumbent (into `my_team.py` only after the user confirms; release gate on the locked test seeds is the user's call). Fail → greedy_v4 stays.
- **Stage-3 result** (`conf14`, validation2 201–240, 1,200 games, 0 harness errors; my_team.py = greedy_v4 at e95a786, framework 54cd83c) [verified]:

  | accept criterion (pre-registered, commit 4155471) | result | pass? |
  |---|---|---|
  | (1) gates | 640 games: 0 crashes / forfeits / warnings / violations; max move 0.301 s (greedy_v4 0.315 s) | yes |
  | (2) pool guard: Δ over the 7 pool members ≥ −0.03 | **+0.027 [0.000, +0.062]** (560 paired) | yes |
  | (2) every pool member's CI upper > −0.5 | worst lab5_smart −0.01 [−0.04, 0.00]; best exploit_v2 +0.10 | yes |
  | (3) head-to-head wins ≥ losses | **29-25-26** (PPG 1.40) | yes |

  - **Verdict: pass.** lab14_stuck (= greedy_v4 + `plan_stuck`) is the **proposed incumbent**. Over all E-043 decision games: pool −0.011 (161–200) and +0.027 (201–240); last-year 14 teams +0.051 [+0.029, +0.074]; head-to-head 55-53-52 over 160 games. Goes into `my_team.py` only after the user confirms; the release gate (locked test seeds, 3rd and last use; held-out teams; Linux timing) is the user's call.
- **Addendum: 1,000-game head-to-head** (user request 2026-11-11, diagnostic, not a decision input; `--run h2h14_1000`, tuning seeds 1–500 × 2 colours, 6 workers; 275 of these maps (2–276) were E-041/E-042 design maps, but only in games against last-year teams) [verified]:

  | | lab14_stuck vs greedy_v4 |
  |---|---|
  | W-T-L | **340-318-342** |
  | PPG [95 % CI, seed bootstrap] | 1.338 [1.315, 1.360] (greedy_v4: 1.342) |
  | (W − L) / games [95 % CI] | −0.002 [−0.010, +0.005] |
  | mean score margin | −0.01 |
  | gates | 0 crashes / forfeits / warnings / violations in 1,000 games; max move 0.272 s (greedy_v4 0.294 s) |

  - Per map (both colours): 336 maps one win each, 156 maps two ties, and only **8 of 500 maps** differ from the colour mirror (lab14_stuck +1 on 4, −1 on 2, −2 on 2). So in the mirror the switch almost never fires: the head-to-head is decided by the map and the colour, which is why the CI on W − L is so narrow. 31.8 % of mirror games are ties (the score records do not say how many are 0-0).
  - Reading: the head-to-head is a true dead heat; the 1.5 threshold (T-62) could not have been met by this candidate on any seed list.
- **Decision (user, 2026-11-11)**: **not promoted**: "basically the same agent" (head-to-head 340-318-342; the gain is +0.05 vs last year's teams only). greedy_v4 stays in `my_team.py`; lab14_stuck stays a league entry and the `plan_stuck` switch stays available in `teams/greedy_lab_v14.py`.

## E-044 — Team brain: the attacker and the defender know each other's situation (2026-11-11 night → 2026-11-12)
- **Status**: screen 1 done (23:44): `relay`, `eyes`, `relief` promising, `push` not; screen 2 done (01:34): `c2` (relay + eyes) and `swap` promising; c3, c4, `cover` not; decision run `val15` (validation3 1–40) done (03:34): `lab15_eyes` and `lab16_c2` pass, `lab16_swap` fails; confirmation run `conf15` (validation3 41–80) done (05:44): **both are confirmed candidates**, proposed to the user; nothing promoted during the night. Afterwards the user promoted `lab16_c2` as `teams/greedy_v6.py` = `my_team.py` (2026-11-12, E-046). Pre-registered (this entry was committed before any screening or validation game was played). Plan: `C:\Users\Tian\.claude\plans\tranquil-growing-tarjan.md` (approved by the user 2026-11-11 21:45).
- **Why**: user request (2026-11-11): a brain / attention mechanism so that each agent knows what the other is doing and how it will react, for proactive planning (help in good situations such as late pushes, prepare for bad ones such as the attacker being chased or dying). Base mindset stays attacker + defender. Three brainstorm agents (defender lens, attacker lens, architect + sceptic) produced the proposals; the user approved the plan.
- **User decisions for this experiment**: roles bend only as temporary help with a return rule; a run stopped for low memory may be resumed automatically with fewer workers; a fresh list `eval/seeds/validation3.txt` (300 seeds, `make_validation3.py`, `random.Random(20261111)`, disjoint from tuning / validation / validation2 / test [verified: 0 overlaps]) is used for decisions; pass rules set by the assistant; nothing is promoted without the user.
- **Code**: `teams/greedy_lab_v15.py` = copy of `greedy_lab_v14.py` + `TeamBrain` (one shared object: what each agent posts, a situation classifier, a play state machine, in-memory counters) + `BrainAgent(RoleAgent)`, built only when `brain=1` or a play is on. Second wave: `teams/greedy_lab_v16.py`.
- **Arms** (each = greedy_v4 + one switch; all [untested], expected Δ are guesses):

  | arm | switch | what it does | return rule | expected Δ (pool / last-year) |
  |---|---|---|---|---|
  | `lab15_brain` | `brain=1` | census: brain on, no play; must reproduce greedy_v4's games | — | 0 / 0 exactly |
  | `lab15_relay` | `relay=1` | handover when the attacker dies: the body near the border attacks, the respawned body defends | always one attacker + one defender; re-evaluated at the next respawn | 0 … +0.04 / 0 … +0.05 |
  | `lab15_eyes` | `eyes=1` | the attacker's greedy safety checks ignore a ghost that is > Manhattan 5 and > 10 maze steps from it and was not in its own sight during its last 8 moves (the planner still models it) | no role bends | −0.02 … +0.04 / +0.03 … +0.08 |
  | `lab15_push` | `push=1` | late tie-break push: with score ≤ 0 the defender attacks when the opponent has been passive (≤ 120 moves left, no enemy Pacman for 80 moves, no return of ours for 60 moves, defender sees no enemy) or when no enemy can still bank | an enemy becomes a Pacman, or we lead | 0 … +0.03 / +0.02 … +0.06 |
  | `lab15_relief` | `relief=1` | the defender helps a stuck attacker (stuck ≥ 6 with a ghost in sight) while home is quiet or it is scared ≥ 12: crosses at another entry, food within 6 of home, banks at 2 | an enemy becomes a Pacman; attacker unstuck 3 moves; 25 moves; cooldown 20 | 0 ± 0.03 / +0.02 … +0.10 |
  | second wave (`lab16_*`) | `cover`, `relay` pre-walk, revisions | an idle attacker closes the invader's second exit; the defender pre-walks to an entry when the attacker is doomed; at most one revision per first-wave arm, only for a flaw the counters name | per arm | — |

- **Groups**: pool = greedy_v3, greedy_v2, feature, camper, choke, exploit_v2, lab5_smart; last-year 7 (screens) = flagrats, pacman_agent, autsys_pacman, pacmancontest, pacman_as, dotgobblers, ll_autonomous_pacman; last-year 14 (decisions) = all working `lyw_*`. Every Δ is paired with greedy_v4 on the same opponent, seed and colour (`eval/group_compare.py`, bootstrap over whole seeds).
- **Build gates** (before a screen): `check_rules.py` passes; identity: v15 with all new switches off and with `brain=1` alone makes greedy_v4's moves in recorded games (full action sequences); smoke with 0 crashes / warnings / violations, max move ≤ 0.5 s; every play fires on at least one game chosen for it.
- **Screen 1** (`--run scr15`): the arms and greedy_v4 vs the pool, greedy_v4 (head-to-head) and last-year 7 on **tuning seeds 301–332**, both colours, `-c`, 6 workers. **Screen 2** (`--run scr16`): second wave on **tuning seeds 333–364**. Same rule:
  - **Promising** (all must hold): gates (0 crashes / forfeits caused by the arm, 0 time warnings, 0 violations, max move ≤ 0.5 s); (Δ last-year ≥ +0.05 and Δ pool ≥ −0.03) or (Δ pool ≥ +0.05 and Δ last-year ≥ −0.03); head-to-head net wins (W − L)/n ≥ −0.10.
  - A play that fires in fewer than 5 % of its games is reported as "not triggered", not as failed. The census arm must show Δ = 0 exactly; in every arm, games in which the play never fired must have greedy_v4's score (leak check).
- **Decision run** (`--run val15`): **validation3 seeds 1–40**, both colours, `-c`, vs the pool, greedy_v4 (head-to-head) and last-year 14. At most 2 candidates: the best promising arm (highest mean of its two group Δ), and the combination of all promising arms if two or more are promising and act in different situations (T-61).
  - **Accept** (all must hold): gates; guards: Δ pool ≥ −0.03, Δ last-year ≥ −0.03, every pool member's paired-Δ CI upper bound > −0.5, head-to-head net wins (W − L)/n ≥ −0.10 with its 95 % CI upper bound ≥ 0 (T-62); gain: the 95 % CI lower bound of Δ pool **or** of Δ last-year is > 0.
- **Confirmation run** (`--run conf15`): **validation3 seeds 41–80**, same opponents, for whatever passes the decision run: same gates and guards; the gain's point estimate > 0 again; the CI of that Δ over both blocks together above 0. Passing both = **confirmed candidate**, proposed to the user (promotion and the release gate are the user's call). Passing only the decision run = single-pass candidate.
- **Not done**: no promotion, no test seeds, no held-out teams, `plan_stuck` not mixed in.
- **Build log (2026-11-11, before any screen game)**:
  - `teams/greedy_lab_v15.py` built (v14 + 576 lines): `TeamBrain`, `BrainAgent(RoleAgent)`, switches `brain`, `relay`, `eyes`, `push`, `relief`; two inert hooks in v14's code (`attack_food()` in `attack_core`, the `create_team` branch). `eval/check_rules.py`: OK [verified].
  - How the brain works in the code: `perceive` → `brain.tick` (deaths of our bodies from position jumps, enemies' `is_pacman` history, our last return, own-sight memory, the plays, a per-round census) → the unchanged v14 decision → `brain.post` (role, rule label, idle count, entry, target, load). A play changes roles only through one latch read by `role_of`; `relay` swaps the shared `home_roles` dict. The teammate's code is never re-run.
  - One build detail added to the pre-registered `relief` rule, before any scored game: it starts only if some enemy food lies within the leash (6 steps of home); otherwise the helper would only stand at the border.
  - Tooling: `eval/sentinel_team.py` copies the brain's in-memory counters into each game record (key `brain`); `eval/group_compare.py` prints the head-to-head as W-T-L with net wins and a seed-bootstrap CI, the firing rate (`--fired`), the Δ on fired games, the leak check and the census (`--census`).
  - League entries: `lab15_off` (identity), `lab15_brain`, `lab15_relay`, `lab15_eyes`, `lab15_push`, `lab15_relief`.
  - **Build gates** [verified, 2026-11-11 22:20]:

    | gate | result |
    |---|---|
    | `eval/check_rules.py teams/greedy_lab_v15.py` | OK |
    | identity, all v15 switches off (`lab15_off`) vs greedy_v4, full action sequences, 4 maps × 4 opponents (lyw_flagrats, lyw_pacman_agent, lyw_autsys_pacman, camper) × 2 colours | 32 / 32 identical (12 / 12 again on the final file, after the `relief` leash-food detail) |
    | identity, `brain=1` alone (`lab15_brain`) | 32 / 32 identical (12 / 12 again on the final file) |
    | smoke `smoke15`: 5 arms + greedy_v4 vs lyw_flagrats, lyw_pacman_agent, camper, choke, baseline, tuning seeds 291–293, 180 games, `-c` | our arms: 0 crashes, 0 time warnings, 0 violations; max move 0.438 s (`lab15_relay`); `lab15_brain` = greedy_v4's score in 30 / 30 paired games |
    | each play fires (30 games per arm) | `relay`: 2 swaps (4 attacker deaths: 2 swaps, 1 "busy", 1 "held"); `eyes`: 97 % of games, 27 moves per game; `push`: (a) 13 % of games, (b) 10 %; `relief`: 33 % of games (+ 3 % scared mode) |

  - Spot check of one `relay` game with `eval/trace_game.py` (vs camper, RANDOM60790497, red): the attacking body was eaten at move 130 as a scared ghost on our side; from the next move the body at the border attacks and the respawned body defends [verified]. The trace tool labels a `RoleAgent` defender that walks to its last evidence as "eat" (it has no defender call to recognise): a labelling limit of the tool, not a role error.
- **Screen 1 result** (`scr15`, 5,696 games, tuning seeds 301–332, 22:20–23:44; my_team.py = greedy_v4, framework 54cd83c) [verified]. Paired Δ vs greedy_v4 on the same opponent, seed and colour (`eval/group_compare.py`); every arm: 0 crashes / forfeits, 0 time warnings, 0 violations.

  | arm | Δ pool (7) [95 % CI] | Δ last-year (7) [95 % CI] | h2h vs greedy_v4 W-T-L, net wins [CI] | play fired in (pool / last-year) | Δ on fired games (pool / last-year) | leak | max move | promising? |
  |---|---|---|---|---|---|---|---|---|
  | `lab15_brain` (census) | 0.000 | 0.000 | 20-24-20, 0.000 | — | — | 0 / 896 | 0.352 s | identical to greedy_v4 in 896 / 896 paired games |
  | `lab15_relay` | **+0.062 [+0.002, +0.138]** | +0.020 [−0.013, +0.056] | 20-24-20, 0.000 [−0.047, +0.047] | 21.7 % / 14.3 % | +0.289 [+0.010, +0.621] / +0.141 [−0.104, +0.351] | 0 | 0.419 s | **yes** (pool ≥ +0.05) |
  | `lab15_eyes` | +0.009 [−0.031, +0.047] | **+0.080 [+0.020, +0.145]** | 20-24-20, 0.000 [−0.062, +0.078] | 96.2 % / 90.6 % | +0.009 / +0.089 [+0.025, +0.159] | 0 | 0.155 s | **yes** (last-year ≥ +0.05) |
  | `lab15_push` | +0.018 [−0.013, +0.049] | +0.036 [+0.011, +0.067] | 23-20-21, +0.031 [−0.031, +0.109] | 7.8 % / 22.8 % | +0.229 [−0.152, +0.679] / +0.157 [+0.045, +0.273] | 0 | 0.191 s | no (below +0.05 on both groups; the sign is positive everywhere) |
  | `lab15_relief` | +0.016 [−0.062, +0.089] | **+0.069 [+0.009, +0.136]** | 19-21-24, −0.078 [−0.219, +0.047] | 44.9 % / 34.2 % | +0.035 / +0.203 [+0.021, +0.386] | 0 | 0.311 s | **yes** (last-year ≥ +0.05; h2h ≥ −0.10) |

  - Leak check: in every arm, every game in which the play never fired has greedy_v4's score (0 leaks). The other session's 500 games (E-045) ran on this laptop during the screen; the census arm still equals greedy_v4 in 896 / 896 games, so the extra load did not change any game.
  - What changes on the board (per game, greedy_v4 → arm):

    | arm | group | W-T-L | 0-0 ties | deaths | food returned |
    |---|---|---|---|---|---|
    | greedy_v4 | pool / last-year | 360-27-61 / 364-53-31 | 8 / 40 | 0.41 / 0.40 | 17.7 / 15.2 |
    | relay | pool / last-year | 371-22-55 / 368-50-30 | 2 / 39 | 0.44 / 0.43 | 18.2 / 15.5 |
    | eyes | pool / last-year | 362-25-61 / 381-38-29 | 7 / 26 | 0.39 / 0.38 | 17.8 / 15.9 |
    | push | pool / last-year | 365-20-63 / 375-36-37 | 3 / 25 | 0.41 / 0.42 | 17.7 / 15.6 |
    | relief | pool / last-year | 362-28-58 / 382-30-36 | 3 / 21 | 0.43 / 0.50 | 17.7 / 16.6 |

  - Per opponent (Δ PPG, 64 games each; reported, never decisive): the last-year gain of `eyes` and `relief` comes mostly from lyw_autsys_pacman (+0.41, +0.39: its 0-0 standoffs become wins), then dotgobblers (+0.14 eyes), pacman_agent (+0.16 relief); `relay`: exploit_v2 +0.16, camper +0.11, ll_autonomous_pacman +0.11; worst single cells: `relief` vs greedy_v3 −0.17, `eyes` vs lab5_smart −0.08.
  - Counters: `relay` swaps 0.26 / 0.17 per game (attacker deaths 0.35 / 0.25; "too far" 0.03, "busy" 0.02–0.04, "held" 0.02–0.03); games with one swap +0.41 / +0.21, games with two or more (18 / 11 games) −0.22 / −0.18. `eyes` drops a ghost on 34 / 43 attacker moves per game; attacker idle moves 29 → 24 (pool) and 38 → 26 (last-year), evade moves vs last-year 17.8 → 8.3, deaths unchanged. `push`: (a) 0.03 / 0.13 and (b) 0.05 / 0.12 entries per game, both modes positive. `relief`: 0.64 / 0.54 entries per game, 6.0 / 4.6 helper moves; exits: attacker unstuck 0.31 / 0.19, an enemy became a Pacman 0.27 / 0.28, 25-move limit 0.06 / 0.04, helper died 0.01 / 0.02; the gain is in the quiet-home mode vs last-year (+33 points over 141 games).
  - **Situation census** (greedy_v4's own games via `lab15_brain`, own moves per game, pool / last-year): no invader 203 / 216, one 94 / 67, two 0.6 / 11.7; defender scared 28 / 21; attacker on their side 146 / 165 (carrying ≥ 5: 70 / 104), walking back from deep at home 49 / 45, near the border at home 102 / 85; attacker idle (≥ 6 moves in a row without a safe target or progress) 29 / 39, of which 24 / 35 with no invader at home; no enemy Pacman for 80 moves: 58 / 85; score tied 103 / 127, late and tied 2.3 / 6.3; attacker deaths 0.31 / 0.20, defender deaths 0.10 / 0.19.
- **Amendment before screen 2 (2026-11-11 23:55, before any `scr16` or validation3 game)**; reasons in one line each:
  - The second wave screens `swap` (role handover at a border standoff: when the attacker's breaker has chosen another entry, the defender is ≥ 6 steps nearer to it and no enemy is a Pacman, the body near the entry attacks and the blocked body defends) **instead of the `relay` pre-walk**: the counters show the defender is almost never too far when the attacker dies ("too far" 0.03 per game), so a pre-walk has no room; entry walks are 25–28 % of attacker moves.
  - No revision of a first-wave arm: no counter names a flaw (no leaks, no dead play, exits as designed).
  - Screen 2 also screens three **combinations** on fresh seeds, because three arms are promising and two of them (`eyes`, `relief`) gain on the same standoff games: `c3` = relay + eyes + relief (the pre-registered "combination of all promising arms"), `c2` = relay + eyes (never empties home), `c4` = c3 + push (does the tie-break push add anything). And the two fixes of E-045 (`pocket`, `cash`), under the same rule.
  - **Decision-run candidates, fixed after screen 2, at most 3**: (1) the best single promising arm of screens 1–2 (highest mean of its two group Δ); (2) the best screened combination, if it is promising in screen 2 by the same rule; (3) the better E-045 arm, if promising. A second-wave arm that is promising but was not screened inside a combination is carried only as a single arm. The accept and confirmation rules are unchanged.
- **Second-wave build log (2026-11-12 00:00, before any `scr16` game)**:
  - `teams/greedy_lab_v16.py` = `greedy_lab_v15.py` (frozen after screen 1) + 230 lines: switches `swap`, `cover` (both need the hidden opponents' fields and are off without `flags`), sub-mode options `eyes_maze`, `push_modes`, `relief_modes` (defaults = v15's behaviour), and E-045's `pocket`, `cash`. All default off.
  - League entries: `lab16_off`, `lab16_c3`, `lab16_c2`, `lab16_c4`, `lab16_swap`, `lab16_cover`, `lab16_pocket`, `lab16_cash` (the last two run with `brain=1` so that their counters reach the game record; the brain alone changes no move, checked below).
  - **Build gates** [verified, 2026-11-12 00:00]:

    | gate | result |
    |---|---|
    | `eval/check_rules.py teams/greedy_lab_v16.py` | OK |
    | identity, every switch off vs greedy_v4 (full action sequences, 12 recorded games: 6 opponents, both colours) | 12 / 12 identical |
    | identity, v16 with one v15 switch on vs the same v15 arm (`relay`, `eyes`, `push`, `relief`) | 12 / 12 identical, each |
    | identity, `pocket` / `cash` with `brain=1` vs the same switch without the brain | 12 / 12 identical, each |
    | smoke `smoke16`: 7 arms + greedy_v4 vs lyw_flagrats, lyw_pacman_agent, camper, choke, baseline, tuning seeds 294–296, 240 games, `-c` | our arms: 0 crashes, 0 time warnings, 0 violations; max move 0.072 s |
    | each play fires (30 games per arm) | `swap`: 0.37 swaps per game, 23 % of games; `cover`: 17 % of games, 1.1 moves per game (exits: invader gone 2, late 2, 8-move limit 1); `pocket`: 90 % of games, 64 attacker moves per game; `cash`: 53 % of games, 14 moves per game; inside `c3`: relay 17 %, eyes 93 %, relief 20 % of games; `c4` adds push in 2 games |

  - Smoke observation on `pocket` (not scored, not tuned on): with a hidden enemy the pessimistic belief removes most dead-end food once the attacker carries 5 ("3 safe of 25" in one traced game), so it walks to open food instead; food lost per game 0.7 (greedy_v4 1.5), food returned 12.3 (12.7). Two games on map 45445946 scored below greedy_v4; both traces end in greedy_v4's own known stalemates (cornered with 8 food by baseline's defender; dithering at the border with nothing carried), reached through the different route, not in a pocket-specific fault. Screened as built.
- **Screen 2 result** (`scr16`, 7,616 games, tuning seeds 333–364, 2026-11-12 00:13–01:34, 6 workers; my_team.py = greedy_v4, framework 54cd83c) [verified]. Paired Δ vs greedy_v4 on the same opponent, seed and colour; every arm: 0 crashes / forfeits, 0 time warnings, 0 violations, 0 leaks. greedy_v4 on these seeds: pool 375-31-42 (2.580 PPG), last-year 375-36-37 (2.592).

  | arm | Δ pool (7) [95 % CI] | Δ last-year (7) [95 % CI] | h2h vs greedy_v4 W-T-L, net wins [CI] | play fired in (pool / last-year) | Δ on fired games (pool / last-year) | max move | promising? |
  |---|---|---|---|---|---|---|---|
  | `lab16_c2` (relay + eyes) | +0.040 [−0.033, +0.107] | **+0.114 [+0.038, +0.194]** | 26-12-26, 0.000 [−0.141, +0.141] | 91.3 % / 93.1 % | +0.044 / +0.122 [+0.043, +0.212] | 0.180 s | **yes** |
  | `lab16_c3` (relay + eyes + relief) | **−0.036** [−0.150, +0.065] | +0.114 [+0.022, +0.208] | 28-8-28, 0.000 [−0.203, +0.188] | 95.5 % / 95.1 % | −0.037 / +0.120 | 0.113 s | no (pool below −0.03) |
  | `lab16_c4` (c3 + push) | **−0.040** [−0.152, +0.060] | +0.127 [+0.040, +0.221] | 29-6-29, 0.000 [−0.219, +0.219] | 95.5 % / 95.5 % | −0.042 / +0.133 | 0.251 s | no (pool below −0.03) |
  | `lab16_swap` | −0.029 [−0.096, +0.036] | **+0.056 [+0.004, +0.114]** | **30-13-21, +0.141 [+0.047, +0.250]** | 50.0 % / 19.9 % | −0.058 [−0.183, +0.078] / +0.281 [+0.021, +0.563] | 0.201 s | **yes** (last-year ≥ +0.05; pool inside the guard by 0.001) |
  | `lab16_cover` | +0.016 [−0.051, +0.087] | +0.009 [−0.018, +0.033] | 22-15-27, −0.078 [−0.203, +0.047] | 25.7 % / 12.7 % | +0.061 / +0.070 | 0.126 s | no |
  | `lab16_pocket` (E-045) | −0.004 [−0.062, +0.058] | −0.031 [−0.089, +0.029] | 20-17-27, −0.109 [−0.266, +0.047] | 92.2 % / 88.2 % | −0.005 / −0.035 | 0.168 s | no |
  | `lab16_cash` (E-045) | **−0.038 [−0.080, −0.004]** | +0.022 [−0.011, +0.051] | 21-17-26, −0.078 [−0.172, 0.000] | 45.5 % / 59.2 % | −0.083 [−0.161, −0.010] / +0.038 | 0.121 s | no |

  - What changes on the board (per game):

    | arm | group | W-T-L | 0-0 ties | deaths | food returned | food lost | conceded |
    |---|---|---|---|---|---|---|---|
    | greedy_v4 | pool / last-year | 375-31-42 / 375-36-37 | 17 / 29 | 0.40 / 0.42 | 15.8 / 14.9 | 1.32 / 0.96 | 7.3 / 6.5 |
    | c2 | pool / last-year | 384-22-42 / 395-27-26 | 12 / 18 | 0.38 / 0.43 | 16.9 / 16.3 | 1.10 / 1.02 | 8.0 / 6.7 |
    | c3 | pool / last-year | 376-12-60 / 398-18-32 | 3 / 10 | 0.46 / 0.48 | 17.2 / 16.9 | 1.21 / 1.10 | 8.9 / 7.2 |
    | c4 | pool / last-year | 376-10-62 / 401-15-32 | 2 / 6 | 0.46 / 0.49 | 17.2 / 17.0 | 1.22 / 1.10 | 9.0 / 7.2 |
    | swap | pool / last-year | 372-27-49 / 384-34-30 | 13 / 28 | 0.41 / 0.44 | 16.6 / 15.4 | 1.38 / 0.93 | 8.3 / 6.8 |
    | cover | pool / last-year | 376-35-37 / 376-37-35 | 22 / 29 | 0.38 / 0.44 | 15.6 / 14.9 | 1.40 / 1.02 | 6.9 / 6.5 |
    | pocket | pool / last-year | 374-32-42 / 371-34-43 | 18 / 28 | 0.39 / 0.45 | 15.4 / 14.7 | 1.18 / 1.11 | 7.2 / 6.6 |
    | cash | pool / last-year | 370-29-49 / 379-34-35 | 16 / 27 | 0.40 / 0.43 | 15.5 / 15.0 | 1.26 / 0.87 | 7.3 / 6.5 |

  - **`relief` does not survive the combination**: on the same games c3 − c2 = −0.076 on the pool and 0.000 against last year's teams. With `eyes` on, the standoff games `relief` won in screen 1 are already won; what remains is its cost: pool ties turn into losses as often as into wins (384-22-42 → 376-12-60, conceded 8.0 → 8.9 per game). `push` on top adds nothing measurable (c4 − c3: −0.004 / +0.013).
  - `swap`: 0.86 swaps per game, in 35 % of games; the gain against last year's teams is on the games where it fires (+0.281) and it is the only arm that wins the mirror (30-13-21); against the pool it is mixed (camper +0.09, lab5_smart +0.08, feature **−0.23 [−0.42, −0.05]**, exploit_v2 −0.12).
  - `cover`: enters 0.35 times per game (21 % of games), 2.1 moves per game; 0.20 of the 0.35 entries end at the 8-move limit, 0.06 with the invader gone: the invader rarely comes to the covered exit. No effect.
  - Counters inside c2: relay swaps 0.21 per game (18 % of games), eyes 34 attacker moves per game (90 %); attacker idle moves 40 → 28 per game, evade moves 14 → 8, attacker deaths 0.27 → 0.28.
  - Per opponent (reported, never decisive): c2's best cells are lyw_pacman_agent +0.23 [+0.06, +0.45], choke +0.19 [+0.05, +0.36], lyw_autsys_pacman +0.17 [+0.03, +0.34]; worst greedy_v3 −0.06, exploit_v2 −0.02.
- **Decision-run candidates (fixed 2026-11-12 01:38, before any validation3 game)**:

  | # | candidate | why it is in | screens (Δ pool / last-year) |
  |---|---|---|---|
  | 1 | `lab15_eyes` | best single promising arm (mean of the two group Δ: eyes 0.045, relief 0.043, relay 0.041, swap 0.014) | scr15: +0.009 / +0.080 |
  | 2 | `lab16_c2` (relay + eyes) | best screened combination and promising in screen 2 | scr16: +0.040 / +0.114 |
  | 3 | `lab16_swap` | **amendment**: the third place was reserved for an E-045 arm and neither is promising; `swap` takes it as the only promising second-wave arm and the only arm whose mirror result is above 0. The number of candidates stays within the pre-registered 3 and the accept rule is unchanged | scr16: −0.029 / +0.056, h2h +0.141 |

  Not carried: `relay`, `relief` as single arms (not the best single), c3 / c4 (pool below the guard), `push`, `cover`, `pocket`, `cash` (not promising). A combination with `swap` was not screened, so none is validated (T-61).
- **Decision run result** (`val15`, 6,960 games, validation3 seeds 1–40 [verified: exactly the first 40 of the list], 2026-11-12 01:38–03:34, 6 workers; my_team.py = greedy_v4, framework 54cd83c) [verified]. Paired Δ vs greedy_v4; last-year = all 14 teams. greedy_v4 on these seeds: pool 452-41-67 (2.495 PPG), last-year 983-94-43 (2.717).

  | candidate | Δ pool (7) [95 % CI] | Δ last-year (14) [95 % CI] | h2h vs greedy_v4 W-T-L, net wins [CI] | worst pool member [CI] | crashes / warnings / violations | max move | accept rule |
  |---|---|---|---|---|---|---|---|
  | `lab15_eyes` | +0.023 [−0.014, +0.061] | **+0.086 [+0.046, +0.125]** | 30-20-30, 0.000 [−0.100, +0.087] | greedy_v3 −0.06 [−0.16, 0.00] | 0 / 0 / 0 | 0.161 s | **pass** |
  | `lab16_c2` (relay + eyes) | +0.023 [−0.025, +0.077] | **+0.106 [+0.074, +0.138]** | 32-18-30, +0.025 [−0.100, +0.150] | greedy_v3 −0.04 [−0.11, 0.00] | 0 / 0 / 0 | 0.204 s | **pass** |
  | `lab16_swap` | **−0.036** [−0.114, +0.039] | +0.010 [−0.010, +0.031] | 32-17-31, +0.013 [−0.050, +0.075] | greedy_v2 −0.16 [−0.33, 0.00] | 0 / 0 / 0 | 0.166 s | **fail** (pool below −0.03; no gain with a CI above 0) |

  | arm | group | W-T-L | 0-0 ties | deaths | food returned | food lost | conceded |
  |---|---|---|---|---|---|---|---|
  | greedy_v4 | pool / last-year | 452-41-67 / 983-94-43 | 13 / 73 | 0.34 / 0.35 | 16.0 / 15.4 | 1.07 / 0.87 | 7.0 / 3.9 |
  | eyes | pool / last-year | 457-39-64 / 1025-64-31 | 14 / 47 | 0.33 / 0.34 | 16.1 / 16.2 | 1.00 / 0.84 | 6.9 / 3.9 |
  | c2 | pool / last-year | 459-33-68 / 1035-57-28 | 11 / 41 | 0.38 / 0.35 | 16.4 / 16.6 | 1.14 / 0.80 | 7.5 / 4.2 |
  | swap | pool / last-year | 448-33-79 / 990-84-46 | 11 / 62 | 0.37 / 0.35 | 16.6 / 15.7 | 1.16 / 0.90 | 7.8 / 4.1 |

  - Where the last-year gain is (per opponent, 80 games each, reported only): c2 gains on lyw_clingho_pacman +0.33 [+0.15, +0.50], lyw_autsys_pacman +0.30 [+0.12, +0.49], lyw_pacman_agent +0.24 [+0.05, +0.44], lyw_flagrats +0.17 [+0.01, +0.36], lyw_pacman_as +0.17, lyw_dotgobblers +0.14, lyw_thedotdominators +0.12; its worst cells are −0.04 (lyw_despookjes, lyw_idontthink, greedy_v3). The gain is ties turned into wins (last-year ties 94 → 57, 0-0 ties 73 → 41) and fewer losses (43 → 28), with deaths unchanged.
  - Counters: eyes drops a ghost on 35–38 attacker moves per game (90 % of games); attacker idle moves 28 / 25 per game (swap, which has no eyes: 32) and evade moves 7 (swap: 15); relay swaps 0.20 per game (17 % of games); swap 0.92 swaps per game (30 % of games).
  - `swap` did not repeat its screen (+0.056 last-year, mirror 30-13-21 → +0.010, 32-17-31) and costs against our own family (greedy_v2 −0.16, greedy_v3 −0.11). **Rejected.**
  - Leak check: the tool flags 1 / 4 / 4 games (eyes / c2 / swap). All nine are games against lyw_despookjes in which that team crashed in the candidate's game and not in greedy_v4's (a win for us both times; a crashed game writes no report, so its counters read as "not fired"). No game with an unfired play differs otherwise. lyw_despookjes crashed in 136 of its 320 games (its own code, as in E-041).
  - **Next**: confirmation run `conf15` (validation3 seeds 41–80) for `lab15_eyes` and `lab16_c2`, started 03:36.
- **Confirmation run result** (`conf15`, 5,200 games, validation3 seeds 41–80 [verified: exactly seeds 41–80 of the list], 2026-11-12 03:35–05:44, 6 workers; my_team.py = greedy_v4, framework 54cd83c) [verified]. greedy_v4 on these seeds: pool 455-35-70 (2.500 PPG), last-year 977-84-59 (2.692).

  | candidate | seeds | Δ pool (7) [95 % CI] | Δ last-year (14) [95 % CI] | h2h vs greedy_v4 W-T-L, net wins [CI] | worst pool member [CI] | crashes / warnings / violations | max move |
  |---|---|---|---|---|---|---|---|
  | `lab15_eyes` | 41–80 | +0.039 [+0.007, +0.077] | +0.037 [+0.001, +0.077] | 22-34-24, −0.025 [−0.075, 0.000] | camper 0.00 [0.00, 0.00] | 0 / 0 / 0 | 0.196 s |
  | `lab15_eyes` | 1–80 | **+0.031 [+0.006, +0.057]** | **+0.061 [+0.033, +0.091]** | 52-54-54, −0.013 [−0.069, +0.037] | greedy_v3 0.00 [−0.07, +0.07] | 0 / 0 / 0 | 0.196 s |
  | `lab16_c2` (relay + eyes) | 41–80 | +0.016 [−0.041, +0.079] | +0.049 [+0.014, +0.089] | 24-33-23, +0.013 [−0.062, +0.087] | feature −0.04 [−0.26, +0.19] | 0 / 0 / 0 | 0.220 s |
  | `lab16_c2` (relay + eyes) | 1–80 | +0.020 [−0.019, +0.062] | **+0.078 [+0.052, +0.104]** | 56-51-53, +0.019 [−0.056, +0.087] | greedy_v3 0.00 [−0.07, +0.07] | 0 / 0 / 0 | 0.220 s |

  | confirmation rule | `lab15_eyes` | `lab16_c2` |
  |---|---|---|
  | gates (0 crashes / warnings / violations, max move ≤ 0.5 s) | ✓ | ✓ |
  | Δ pool ≥ −0.03 and Δ last-year ≥ −0.03 | ✓ (+0.039, +0.037) | ✓ (+0.016, +0.049) |
  | every pool member's CI upper bound > −0.5 | ✓ | ✓ |
  | h2h net wins ≥ −0.10, CI upper bound ≥ 0 | ✓ (−0.025; upper bound exactly 0.000, at the limit) | ✓ (+0.013) |
  | the gain's point estimate > 0 again (Δ last-year) | ✓ (+0.037) | ✓ (+0.049) |
  | CI of that Δ over both blocks above 0 | ✓ ([+0.033, +0.091]) | ✓ ([+0.052, +0.104]) |
  | **verdict** | **confirmed candidate** | **confirmed candidate** |

  | games over both blocks (W-T-L; 0-0 ties) | pool (1,120 games) | last-year 14 (2,240 games) |
  |---|---|---|
  | greedy_v4 | 907-76-137; 24 | 1960-178-102; 138 |
  | `lab15_eyes` | 921-69-130; 26 | 2020-135-85; 99 |
  | `lab16_c2` | 919-62-139; 22 | 2038-118-84; 87 |

  - **What `relay` adds to `eyes`** (c2 − eyes on the same 3,360 games): pool −0.012 [−0.042, +0.017], last-year +0.017 [+0.002, +0.032]. Most of the gain is `eyes`; `relay` (0.20 swaps per game, in 17 % of games) adds a little against last year's teams and nothing against the pool.
  - The second block is smaller than the first for both (last-year +0.086 → +0.037 and +0.106 → +0.049) and both are below their screens (+0.080, +0.114): the usual shrinkage after a selection. The 80-seed numbers are the ones to quote.
  - What changes on the board over both blocks, c2 vs greedy_v4 against last year's teams: +78 wins, −60 ties (0-0 ties 138 → 87), −18 losses in 2,240 games (win rate 87.5 % → 91.0 %); deaths per game unchanged (0.35–0.39), food returned +1.0 per game, conceded +0.2. Against the pool: +12 wins, −14 ties, +2 losses in 1,120 games.
  - Leak check: 0 flagged for eyes; 3 for c2, all lyw_despookjes games in which that team crashed in the candidate's game only (wins both times). lyw_despookjes crashed in 128 of its 240 games (its own code).
- **Outcome of E-044**: two **confirmed candidates**, `lab15_eyes` and `lab16_c2`; nothing promoted during the night (`my_team.py` = greedy_v4, the user's call). Later on 2026-11-12 the user promoted `lab16_c2` as `greedy_v6` (E-046). Not used: test seeds, held-out teams. Rejected: `swap` (decision run), `relief`, `push`, `cover` (screens). Seeds used: tuning 291–296 (smokes), 301–364 (screens); validation3 1–80 of 300.
- **Linux timing of the two confirmed candidates (05:48–05:57)** [verified]: WSL Ubuntu 24.04, CPython 3.8.20, `~/pacman_wsl` mirror re-synced; `eval/check_rules.py` OK on both files there. `lab15_eyes` and `lab16_c2` vs greedy_v3, choke, exploit_v2, lab5_smart, lyw_flagrats on tuning seeds 516–520 (reused: a timing check tunes nothing), both colours, `-q -c` (real `SIGALRM` limits), 12 workers on 12 logical CPUs (load average 8) (run `wsl_c2_loaded`, kept in the WSL mirror).

  | agent | games | W-T-L | crashes | time warnings | timeouts | violations | max move | worst p95 | max startup |
  |---|---|---|---|---|---|---|---|---|---|
  | `lab15_eyes` | 50 | 43-6-1 | 0 | 0 | 0 | 0 | 0.229 s | 0.141 s | 1.70 s |
  | `lab16_c2` | 50 | 43-6-1 | 0 | 0 | 0 | 0 | 0.166 s | 0.104 s | 1.42 s |

  Same level as greedy_v4's own Linux check (max move 0.283 s, E-032): the plays add no measurable move time.
- **Diagnostic after the decision (pre-stated 06:00, not a decision input)**: run `diag15`: greedy_v4, `lab15_eyes`, `lab16_c2` vs the friend teams (`friend_diego`, `friend_andy`, `friend_andy_v2`, `friend_aljaz_1..5`) on tuning seeds 365–394, both colours, `-c`. Purpose: E-045 started from losses against a friend's agent, so the user will want to know whether the confirmed plays change anything there. Friend teams are diagnostics only (user rule 2026-11-11): whatever this shows, the verdict above stands.
- **Diagnostic result** (`diag15` + `diag15b`, tuning seeds 365–394, both colours, `-c`, 06:00–06:37) [verified]; **not a decision input**. The run as pre-stated was stopped at 379 of 1,440 games: `friend_aljaz_2..4` take about a minute per game and it would have ended after 08:00. greedy_v4's finished pairings are kept (`diag15`); the two candidates then played the four fast friend teams on the same seeds (`diag15b`, 480 games). `friend_aljaz_2` / `_3` have greedy_v4 games only (2.53 / 2.37 PPG), `_4` / `_5` nothing usable.

  | opponent (60 games each) | greedy_v4 W-T-L (PPG) | `lab15_eyes` W-T-L (PPG) | Δ [95 % CI] | `lab16_c2` W-T-L (PPG) | Δ [95 % CI] |
  |---|---|---|---|---|---|
  | `friend_diego` | 47-3-10 (2.40) | 49-3-8 (2.50) | +0.10 [−0.15, +0.35] | 48-4-8 (2.47) | +0.07 [−0.27, +0.40] |
  | `friend_andy` | 51-7-2 (2.67) | 53-7-0 (2.77) | +0.10 [−0.05, +0.27] | 52-7-1 (2.72) | +0.05 [−0.13, +0.25] |
  | `friend_andy_v2` | 51-6-3 (2.65) | 51-6-3 (2.65) | 0.00 [−0.10, +0.10] | 51-6-3 (2.65) | 0.00 [−0.10, +0.10] |
  | `friend_aljaz_1` | 30-1-29 (1.52) | 35-0-25 (1.75) | +0.23 [−0.08, +0.57] | 35-1-24 (1.77) | +0.25 [−0.05, +0.58] |
  | **all four (240 games)** | 2.308 | 2.417 | **+0.108 [−0.013, +0.229]** | 2.400 | **+0.092 [−0.037, +0.229]** |

  Both candidates: 0 crashes, 0 time warnings, max move 0.209 s / 0.162 s. Reading: no friend team gets worse and the sign is positive, but with 240 games the interval includes 0. The plays do not address what E-045 found against `friend_diego` (big loads lost in dead ends); `friend_aljaz_1` remains the opponent we are level with (30-1-29 → 35-1-24).
- **Decisions taken by the assistant during the night** (user, 2026-11-11 ~23:30: "all decisions from now on should be autonomous - you make them", each with a 1–2 sentence reason):

  | # | time | decision | why (1-2 sentences) |
  |---|---|---|---|
  | 1 | 22:10 | `relief` starts only if some enemy food lies within the 6-step leash | Without it the helper would only stand at the border; added before any scored game. |
  | 2 | 22:20 | Second wave gets `swap` (role handover at a border standoff) instead of the planned `relay` pre-walk | The smoke counters show the defender is already at the border when the attacker dies (relay "too far" = 0), so a pre-walk has nothing to gain; entry walks are 25-28 % of attacker moves. |
  | 3 | 23:15 | Took on the other session's loss diagnosis as E-045, sharing screen 2 and the decision runs | It is the same kind of work the user asked for in E-042/E-043 and fits the compute budget only if it shares runs. |
  | 4 | 23:15 | Asked the other session to run no more games tonight | Its 500 games overlapped screen 1; extra load can change moves under the 0.3 s planner budget. |
  | 5 | 23:30 | No promotion to `my_team.py` whatever passes | The pre-registered rule says candidates are proposed to the user; the test run is on 11-23, so nothing is lost by waiting. |
  | 6 | 23:30 | No AI/session line in commit messages | The organisation's policy forbids AI attribution in git metadata and outranks the session reminder. |
  | 7 | 23:55 | Screen 2 also screens three combinations (relay+eyes+relief, relay+eyes, all four) and at most 3 candidates go to the decision run | Three arms were promising in screen 1 and two of them gain on the same standoff games, so a combination must be screened on fresh seeds before validation seeds are spent on it. |
  | 8 | 23:55 | `push` is not carried as a single candidate | It missed the pre-registered +0.05 bar on both groups (+0.018 / +0.036); it stays only inside the 4-play combination. |
  | 9 | 00:05 | `pocket` screened as built, although two smoke games scored below greedy_v4 | Both traces end in greedy_v4's own known stalemates, not a pocket fault; tuning on 2 smoke games would be overfitting. |
  | 10 | 00:10 | E-045's fixes limited to `pocket` and `cash` | Only hypothesis A (big loads lost in dead ends) was confirmed on the pool and last-year games; B, C, E already have failed or pending tests, F has no mechanism. |
  | 11 | 01:38 | Decision-run candidates: `lab15_eyes`, `lab16_c2` (relay + eyes), `lab16_swap` | eyes is the best single arm and c2 the only promising combination (the pre-registered picks); swap takes the place left empty by the E-045 arms because it is promising and the only arm that wins the mirror. |
  | 12 | 01:38 | `relief` and `push` dropped from the combination | On the same games, adding relief to relay + eyes costs 0.076 on the pool and adds 0.000 against last year's teams; push adds nothing measurable. |
  | 13 | 01:38 | `pocket` and `cash` (E-045) not carried | Neither is promising: pocket -0.004 / -0.031, cash -0.038 / +0.022, both lose the mirror. |
  | 14 | 03:36 | `swap` rejected; confirmation run started for `lab15_eyes` and `lab16_c2` | Pre-registered rule: swap is below the pool guard (-0.036) and shows no gain; the other two pass every guard with a last-year gain whose CI is above 0. |
  | 15 | 05:47 | Both `lab15_eyes` and `lab16_c2` reported as confirmed candidates; `lab16_c2` suggested first | Both pass the pre-registered confirmation; c2 has the larger gain against last year's teams (+0.078 vs +0.061) at no pool cost, eyes is the simpler fallback. |
  | 16 | 05:48 | Linux timing check run for both candidates | The plan lists it for any confirmed candidate and it costs 10 minutes. |
  | 17 | 06:00 | Extra diagnostic run against the friend teams, with no decision attached | E-045 started from losses to a friend's agent; the table answers "does it help there" without touching the verdict. |
  | 18 | 06:00 | No `plan_stuck` combination screened and no shippable file (`greedy_v6`) built | The approved plan excludes mixing in plan_stuck tonight, and which candidate to ship is the user's choice. |
  | 19 | 06:28 | Diagnostic cut to the four fast friend teams (diego, andy, andy_v2, aljaz_1) | Three of the compiled aljaz teams take about a minute per game, so the full run would have ended after 08:00; greedy_v4 games against the dropped teams are kept but unpaired. |

## E-045 — Loss diagnosis of greedy_v4 against a friend's agent, and two greedy fixes from it (2026-11-11 night → 2026-11-12)
- **Status**: diagnosis logged and confirmed on the pool and last-year games (hypothesis A); two fixes (`lab16_pocket`, `lab16_cash`) pre-registered below, before any screen game of them; **screened in `scr16` (E-044): neither is promising** (result at the end of this entry).
- **Why**: a second Claude session working in this repository ran greedy_v4 against a friend's agent for the user, diagnosed our losses and passed the findings to this session at ~23:15 with the user's request to "plan changes to the greedy agent as well with the knowledge gathered", overnight, next to E-044. [reported: the request reached this session through the other session's message, not from the user directly.] Friend teams are diagnostics only (user rule 2026-11-11): nothing below is decided on this opponent.
- **Diagnostic run** (by the other session; `eval/results/diego_vs_v4.jsonl`): `eval/evaluate.py play --candidate greedy_v4 --vs friend_diego --seeds tuning --n-seeds 250 --jobs 2 --run diego_vs_v4`: tuning seeds 1–250, both colours, 500 games, `-c`, 22:20–22:51. `friend_diego` = `friends/diego/my_team.py` (packed source; [reported] checked for safety by decoding names only; never read for design; kept local, `friends/` is git-ignored). greedy_v4 = `my_team.py`, framework 54cd83c.
  - **Result** [verified from the result file]: greedy_v4 **340-45-115, 2.13 PPG**, red 179-20-51, blue 161-25-64; 75 of the 115 losses are by ≤ 5 points; 20 maps lost from both colours, 123 won from both; 0 crashes / warnings / violations, max move 0.349 s. [reported] CI [2.01, 2.25].
  - **Overlap with E-044** [verified from file times]: these 500 games (22:20–22:51) and the replay probes after them (to 23:21) ran on this laptop while screen 1 of E-044 (`scr15`, 6 workers) was running. Effect on `scr15`: see its leak check (E-044).
- **Where the points go** (other session: `replay_probe.py classify`, then `replay --events` on all 160 non-wins and on a random 100 games, 69 of them wins; files `eval/results/diego_vs_v4_replay_nonwins.md`, `..._sample100.md`, parsing script `..._event_stats.py.txt`). The per-game numbers below are [verified]: I re-ran the parsing script on the two replay files; the classify shares are [reported].

  | per game | wins (69) | losses (115) | ties (45) |
  |---|---|---|---|
  | attacker deaths | 0.29 | 0.94 | 0.67 |
  | food lost by the attacker | 0.86 | 5.07 | 2.91 |
  | attacker deaths carrying ≥ 5 (total) | 5 | 44 | 11 |
  | defender deaths | 0.16 | 0.36 | 0.04 |
  | games in which they ate a capsule | 68 % | 93 % | 49 % |
  | our deaths per third (plies 0–399 / 400–799 / 800+) | 0.09 / 0.19 / 0.17 | 0.24 / 0.51 / 0.54 | 0.13 / 0.22 / 0.36 |
  | our returns per third | 1.6 / 12.6 / 6.7 | 1.3 / 9.1 / 3.7 | 2.1 / 6.5 / 2.0 |
  | their returns per third | 3.5 / 7.0 / 2.7 | 5.1 / 9.8 / 5.4 | 2.6 / 5.2 / 2.8 |
  | behind at ply 800 (games) | 15 | 80 | 10 |
  | median ply of our last return | 904 | 785 | 656 |

  - [reported] classify, points lost: out-defended 37 %, our deaths (≥ 3 or ≥ 6 food lost) 30 %, equal trade 14 %, out-raced 7 %, we returned ≤ 3: 5 %, 0-0 ties 7 %. Standoff plies per game: wins 124, ties 246, losses 110. In non-wins about 33 % of invaded plies have two invaders.
  - **Attacker deaths by load** (the 160 non-wins, 138 attacker deaths, 714 food lost) [verified, my own parse of the replay file]:

    | carried at death | deaths | of them in a dead end | food lost | of it in dead ends |
    |---|---|---|---|---|
    | 0 | 48 | 0 | 0 | 0 |
    | 1–4 | 35 | 32 | 99 | 92 |
    | 5–7 | 17 | 13 | 94 | 70 |
    | ≥ 8 | 38 | 32 | 521 | 438 |

    73 % of the food our attacker loses is lost in deaths that carry 8 or more, i.e. after `open_goal` let the trip go on past `return_at` = 8, and 84 % of that is lost inside a dead end. In the 115 losses, 57 of 108 attacker deaths are in a dead end; in 34 of the 57 the killer was in sight when we entered and in 41 it could reach the exit before us [verified].
- **Hypotheses** (from the other session, ranked by points; each is a hypothesis until seen on the pool / last-year games):

  | # | hypothesis | already known? | earlier tests |
  |---|---|---|---|
  | A | the attacker dies with a big load in dead ends it cannot leave | yes: E-014, E-042 pitfall 4 (2–3 % of games against the pool and last-year teams have a death carrying ≥ 10, E-043) | exit-race checks at every load: deaths halve, points flat (E-002, E-018); a stricter `open_goal` margin (`open_safe`): loses the mirror, h2h 1.27 (E-043) |
  | B | one defender against frequent small raids, two invaders a third of the time | yes: E-042 pitfall 2 | attacker recall −0.58 (E-025), assist 0.00 (E-039); `cover` is in E-044's second wave |
  | C | their capsule: in 93 % of losses; our defender dies twice as often | yes: E-042 pitfall 1 | scared posture: +0.07 tuning, not repeated (E-039, E-043); capsule guard within noise (E-039); scared raid +0.04 (E-043) |
  | D | late collapse: behind at ply 800 in 80 of 115 losses, deaths triple in the last third, last return at ply ~785 | new measurement | late tie banking and endgame horizons within noise (E-039, E-044 plan) |
  | E | stalls in ties: 246 standoff plies | yes: E-042 pitfall 3 | `plan_stuck` +0.05 vs last-year, not promoted (E-043); E-044's `relief`, `push`, `eyes`, `swap` aim at it |
  | F | 20 maps lost from both colours; blue is worse (161-25-64 vs 179-20-51) | new | — |
- **Confirmation on the pool and last-year games** (2026-11-11 23:52) [verified]: `eval/replay_probe.py replay --run scr15 --agent greedy_v4 --worst 2000 --events` replayed every non-win of greedy_v4 in screen 1 of E-044 (387 games, tuning seeds 301–332) with the true state; parsed by load and dead end.

  | opponents | games | non-wins | attacker deaths in them | food lost | deaths carrying ≥ 8 (food) | share of the lost food | of that inside a dead end | dead-end deaths: killer in sight at entry | killer first at the exit |
  |---|---|---|---|---|---|---|---|---|---|
  | pool (7) | 448 | 88 | 51 | 291 | 19 (180) | 62 % | 93 % | 18 / 41 | 29 / 41 |
  | last-year (7) | 448 | 84 | 19 | 177 | 11 (174) | 98 % | 100 % | 6 / 12 | 5 / 12 |
  | our own v15 arms (mirror games) | 320 | 215 | 46 | 296 | 20 (197) | 67 % | 70 % | 21 / 36 | 32 / 36 |

  | opponents | carried at death: 0 | 1–4 | 5–7 | ≥ 8 | non-wins with a death carrying ≥ 8 | non-wins in which they ate a capsule | our returns per third | their returns per third |
  |---|---|---|---|---|---|---|---|---|
  | pool (7) | 8 | 11 (11 in a dead end) | 13 (12) | 19 (18) | 16 of 88 | 72 | 2.8 / 5.8 / 3.1 | 4.6 / 6.0 / 5.1 |
  | last-year (7) | 7 | 1 (1) | 0 | 11 (11) | 11 of 84 | 38 | 0.5 / 2.0 / 2.5 | 1.5 / 4.0 / 1.4 |

  - **A is confirmed** on both groups: most of the food our attacker loses is lost in a death that carries 8 or more inside a dead end, and in most dead-end deaths the killer reaches the exit first. From the sentinel data of the whole screen, greedy_v4's attacker loses per game 1.03 / 2.93 / 3.48 food in wins / ties / losses against the pool and 0.73 / 0.47 / 4.90 against last year's teams.
  - **Size of the prize**: a death carrying ≥ 8 occurs in 16 of 448 pool games (3.6 %) and 11 of 448 last-year games (2.5 %) that we did not win. Even if every one of them became a win, the gain is at most about +0.1 points per game; a realistic share is +0.02 … +0.04, at the edge of what a screen resolves.
  - **D** shows against the pool (their returns in the last third 5.1 vs ours 3.1) but not against last year's teams (1.4 vs 2.5). **C**: the capsule is eaten in 82 % of pool non-wins and 45 % of last-year non-wins. B, E, F were not re-measured here.
- **Fixes, pre-registered before any screen game** (in `teams/greedy_lab_v16.py`, default off, [untested]):

  | arm | switch | what it does | aims at | expected Δ (pool / last-year) |
  |---|---|---|---|---|
  | `lab16_pocket` | `pocket=1` (`pocket_load` 5, `pocket_margin` 2) | carrying 5 or more, a food inside a dead end is a target (for greedy and for the planner) only if the attacker is back at that dead end's entrance 2 moves before any enemy can stand there (seen enemy: exact distance; hidden: pessimistic quantile of the belief, as `open_goal`; a scared enemy counts from the end of its timer); the other dead-end food waits until the load is banked | A | −0.03 … +0.04 / 0 … +0.04 |
  | `lab16_cash` | `cash=1` (`cash_moves` 100, `cash_at` 3) | in the last 100 own moves the attacker goes home with 3 food and `open_goal` no longer extends the trip | D (and A late in the game) | 0 ± 0.03 / 0 ± 0.02 |

  - How `pocket` differs from the earlier tests of A: the exit-race checks (E-002, E-018) applied at every load and cost as much food as they saved; `open_safe` (E-043) made the whole trip extension stricter. `pocket` leaves trips with a small load alone and only removes dead-end targets whose exit we cannot win, when there is a load to lose.
  - **Test**: screen 2 of E-044 (`scr16`, tuning seeds 333–364, pool + greedy_v4 + last-year 7), E-044's "promising" rule; the better of the two, if promising, is the third decision-run candidate (E-044 amendment). Firing is counted by `pocket_moves` / `cash_moves` (attacker moves on which the rule changed the target list / the return threshold applied).
  - **Not built**: B (`cover` of E-044 is the only untested idea; recall and assist failed), C (three earlier tests within noise), E (E-044's plays aim at it), F (no mechanism proposed; a map / colour effect needs its own measurement).
- **Screen result** (`scr16`, tuning seeds 333–364, table in E-044) [verified]: `lab16_pocket` −0.004 [−0.062, +0.058] pool / −0.031 [−0.089, +0.029] last-year, h2h 20-17-27; `lab16_cash` **−0.038 [−0.080, −0.004]** / +0.022 [−0.011, +0.051], h2h 21-17-26. **Neither is promising; neither goes to the decision run.**
  - `pocket` fires in 90 % of games (64 attacker moves per game) and does what it says against the pool (food lost 1.32 → 1.18 per game), but the attacker returns less (15.8 → 15.4) and loses the mirror (20-17-27); against last year's teams it loses more food, not less (0.96 → 1.11). This is the fourth restriction aimed at hypothesis A (exit-race checks E-002 / E-018, `open_safe` E-043, `pocket`) and the fourth that saves about as much as it costs: the dead ends hold most of the food, so keeping a loaded attacker out of them costs eating time.
  - `cash` loses against the pool (greedy_v3 −0.14 [−0.30, −0.02]): banking 3 food late gives up the bigger last trip that decides close games against our own family.
  - **Verdict**: hypothesis A is real (most of the lost food) but small (a death carrying ≥ 8 in about 3 % of games), and avoiding the dead ends is not the way to collect it. Open idea, [untested]: keep eating there but escape better (the cut-off attacker's TrailMax escape, heuristics.md H-S20).

## E-046 — Promote relay + eyes to `my_team.py` (`greedy_v6`) (2026-11-12)
- **Status**: done. `my_team.py` = `teams/greedy_v6.py` since 2026-11-12. **Release gate not run.**
- **Decision** (user, 2026-11-12, after the E-044 morning brief): "Put lab16_c2 into my_team and push all changes to remote repo". Of the two confirmed candidates of E-044 the user chose `lab16_c2` (relay + eyes).
- **Build**: `teams/greedy_v6.py` = `teams/greedy_lab_v16.py` (frozen) with `lab16_c2`'s options as defaults in `V6_DEFAULTS` (plan=danger, plan_budget=0.3, plan_v=2, plan_leaf=netf, plan_nodes=2000, relay=1, eyes=1) and a new header; no other line differs [verified by diff]. The number 5 is skipped: `teams/greedy_v5.py` is the rejected candidate of E-038. League entry `greedy_v6` added; `submission` note updated.
- **Checks before and after the copy** [verified]:

  | check | result |
  |---|---|
  | `eval/check_rules.py my_team.py teams/*.py` | OK, every file |
  | identity `greedy_v6` vs `lab16_c2` (the validated league entry), full action sequences, 16 recorded games (10 opponents incl. greedy_v4, greedy_v3, 3 last-year teams, baseline; both colours) | 16 / 16 identical |
  | `my_team.py` byte-identical to `teams/greedy_v6.py` (`cmp`) | yes |
  | identity `submission` (`my_team.py` as the engine loads it) vs `lab16_c2`, same 16 games | 16 / 16 identical |
  | smoke through `capture.py -q -c` vs `baseline_team` on RANDOM13, both colours | +19 (red), +16 (blue); no exception, no time warning |
  | smoke `smoke_v6`: `submission` vs baseline, greedy_v4, camper, choke, lyw_flagrats, lyw_autsys_pacman, tuning seeds 395–398, 48 games, `-c` | 37-3-8; 0 crashes, 0 time warnings, 0 violations; max move 0.251 s, p95 0.101 s; eyes fires in 85 % of games, relay swaps in 19 % |
  | Linux timing: WSL Ubuntu 24.04, CPython 3.8.20, mirror re-synced (`my_team.py` = `teams/greedy_v6.py` there too); `submission` vs greedy_v4, greedy_v3, choke, exploit_v2, lab5_smart, lyw_flagrats on tuning seeds 516–520 (reused: a timing check tunes nothing), both colours, `-q -c` (real `SIGALRM` limits), 12 workers on 12 logical CPUs while the Windows side ran 4 more game workers (run `wsl_v6_loaded`, kept in the WSL mirror) | 60 games, 46-8-6; **0 crashes, 0 time warnings, 0 timeouts, 0 violations; max move 0.326 s, worst p95 0.281 s, max startup 4.5 s** |

- **Not done**:
  - **Release gate** (evaluation.md section 2): the locked test seeds (1 of 3 uses left) and the held-out teams were not used. greedy_v6's evidence is the E-044 validation (validation3 seeds 1–80) against the pool and last year's 14 public entries.
  - **Rule profile** for the picks page (`trace_game.py profile`): started and stopped on the user's instruction ("Just push, no need to test anything anymore"). `docs/picks/greedy_v6.md` uses the counters of the validation runs instead.
  - **Reference pool**: unchanged (8 members, without greedy_v6). New candidates should be paired with greedy_v6; whether it joins the pool is the user's decision, as in E-036.
- **Docs**: `docs/picks/greedy_v6.md` (new), `docs/picks/README.md`, `docs/agents.md` (lineage, arm verdicts), `docs/evaluation.md`, `CLAUDE.md` (current state, incumbent).
- **Commits**: framework 54cd83c; `my_team.py` changed in the commit that adds this entry.
