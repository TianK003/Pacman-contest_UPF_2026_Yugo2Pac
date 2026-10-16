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

Proposed 2026-10-16 from the E-002 findings. Each candidate changes **one** thing compared with `teams/greedy_v1.py`, so its effect can be attributed.

| ID | Agent / experiment | Question | Heuristics | Depends on |
|---|---|---|---|---|
| P-01 | `baseline_plus` (league opponent) | the baseline attacker plus a return threshold: a stronger simple opponent, since the baseline is saturated | — | — |
| P-02 | `border_camper` (league opponent) | a defender that mirrors our attacker along the border. Can our attacker get past a shadowing ghost? | H-S07 | — |
| P-03 | `capsule_rusher` (league opponent) | an attacker that eats the capsule first and then harvests. Does our defender cope with a scared window? | H-S06 | — |
| P-04 | `greedy_v2`: adaptive return | carry more (e.g. return at 10, or when ≤ 2 food are left) when no enemy ghost has been seen on their side for N turns. Does it fix the double_attack weakness without losing elsewhere? | H-S04, H-S11 | P-01..P-03 for a fair pool |
| P-05 | `greedy_v2`: call back the attacker on 2 invaders | if 2 invaders are detected on our side, the attacker turns back to defend | H-S08 (basic) | P-04 |
| P-06 | `greedy_v2`: endgame / score control | leading late → both defend; behind late → both attack | H-S05 | — |
| P-07 | `RETURN_AT` sweep {3, 5, 8, 12} on **tuning** seeds, then confirm the best on validation | first use of the tuning/validation split | H-S04, M-02 | P-01..P-03 |
| P-08 | Defender interception | go to the cell on the invader's way home that we reach first, instead of chasing it directly | H-S07, H-S03 | — |

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
