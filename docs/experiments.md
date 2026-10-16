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
  - Build the batch harness.
