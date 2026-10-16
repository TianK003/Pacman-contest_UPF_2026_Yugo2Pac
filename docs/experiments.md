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

| ID | Question | Depends on |
|---|---|---|
| — | (empty) | |

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

## E-002 — Round robin of the v1 league (2026-10-16) — PARTIAL
- **Status**: aborted at 160/400 games. Claude Code stopped the background run because the *system* was low on memory; about 3.5 GB of 15.3 GB was free, with other projects running. It was not an agent failure.
  - The 10 orphaned game processes were stopped.
  - 10 turtle-vs-baseline games were cut off mid-game, after 5–20 s, with no score file. They contain no traceback, crash or warning, and are excluded from the stats.
  - Resume with `--resume` (250 games missing).
- **Question**: how do the first non-trivial agents compare with the baseline and with each other?
- **Variants** (all from `teams/greedy_v1.py`, via `eval/league.json`):
  - `greedy`: `GreedyAttacker` + `PatrolDefender`. These are the defaults.
  - `greedy_deadend`: `DeadEndAttacker` + `PatrolDefender`.
  - `double_attack`: 2× `GreedyAttacker`.
  - `turtle`: 2× `PatrolDefender`.
  - `baseline`: the framework's `baseline_team`.
- **Setup**: validation seeds 1–20, both colours, `-q -c`, sentinel on every team, 10 workers, Windows 11, Python 3.8.10, framework `54cd83c`. Run `rr_v1` (`eval/results/rr_v1.jsonl`).
- **Results**: only the 4 pairings *against the baseline* finished (40 games each; 30 scored for turtle).

  | agent vs baseline | games | W-T-L | PPG [95% CI] | margin min/median/max |
  |---|---|---|---|---|
  | greedy | 40 | 40-0-0 | 3.00 [3.00, 3.00] | 6 / 20 / 28 |
  | greedy_deadend | 40 | 40-0-0 | 3.00 [3.00, 3.00] | 11 / 20 / 28 |
  | double_attack | 40 | 6-1-33 | 0.47 [0.15, 0.88] | −16 / −7 / 28 |
  | turtle | 30 | 0-28-2 | 0.93 [0.83, 1.00] | −5 / 0 / 0 |

  - **Gates**: 0 crashes/forfeits, 0 engine time warnings, 0 sentinel violations across all 150 scored games. Max move time 0.154 s (the baseline's) and 0.073 s for ours. Max startup 1.59 s.
  - **Paired diagnostic** (margin, not a decision metric): `greedy_deadend − greedy` = +0.53 [−0.38, +1.43] over 40 games. Deadend was better in 14 games, equal in 18 and worse in 8.
  - Mean game wall time was 40 s under 10-way parallelism.
- **Conclusions**:
  - **v1 beats the baseline in every game, as both colours.** The baseline is now **saturated**: it can no longer separate our variants (as the literature warns, evaluation.md section 3). From now on it serves only as a regression gate.
  - **No evidence yet that dead-end awareness (H-M02) helps.** It only matters against ghosts that guard their side, and the baseline defender is weak.
  - **Defence matters.** Two attackers with no defender lose 33/40 to the baseline. The baseline's attacker, uncontested, returns nearly all of our food.
  - **A double defence (turtle) ties the baseline** (28 ties of 30), but still lost 2 games. The single pilot seed (E-001) showed turtle also *tying our greedy agent*. If that holds, our attacker cannot break a two-ghost defence, a likely weakness against defensive teams. This rests on 1 seed only and needs the remaining pairs.
- **Follow-ups**:
  - Resume E-002 with fewer workers (e.g. `--jobs 6`) to get the head-to-head pairs between our variants.
  - Build harder opponents (exploiters / specialists).

## E-003 — Promote `greedy` (teams/greedy_v1.py defaults) to my_team.py (2026-10-16)
- **Status**: done. This is a **provisional** promotion by the user's decision ("for now make it the top team"), not a full pass of the accept rule.
- **Basis (the parts of the rule that hold, evaluation.md section 2)**:
  - Gates: lint OK; 0 crashes, warnings and violations in E-002.
  - Head-to-head against the previous incumbent (`my_team.py` was the baseline): 40-0-0, PPG 3.00 ≥ 1.5.
- **Not yet shown**:
  - A pool improvement with CI > 0, because the E-002 pairings against the other variants are missing.
  - Confirmation on unused validation seeds.
  - Linux timing.
- **Change**: `my_team.py` is now `teams/greedy_v1.py` with a different header comment only (the body was checked with `diff`). Smoke test: it loads from the repo root and beat the baseline in a 120-move game. League entry `submission` added.
- **Follow-up**: re-check against the accept rule once E-002 is complete.
