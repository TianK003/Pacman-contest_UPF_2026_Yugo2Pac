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
| P-18 | New league members from greedy_v2's weaknesses | an exploiter written against greedy_v2 (evaluation.md section 5); a held-out opponent written by a teammate | — | planned |

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
