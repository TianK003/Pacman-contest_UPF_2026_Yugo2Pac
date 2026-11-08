# HANDOFF — overnight session 2026-11-07 → 2026-11-08

**Read this first** if you are an agent continuing this work (after a context compaction or in a new session).
Then read `CLAUDE.md`, `docs/agents.md`, `docs/proposals.md`, and the newest entries at the bottom of `docs/experiments.md`
(E-027 … E-033). Keep working autonomously until the user says stop (they asked for ≥ 08:00); do not ask questions.

## The user's requests
1. (23:20) **Width-based planning** (IW / BFWS / novelty + heuristics; extra deps allowed if documented) and **RL-based
   heuristics** for the greedy agents (per-map modes, learned selection, combining greedy with RL). Research agents first,
   many experiments overnight, try weird approaches, advisor agents allowed. Re-read `docs/proposals.md` regularly; update
   docs; commit regularly; push after finished experiment rounds.
2. (03:35) "Promote lab7_danger_net to my_team for now, compare it to defender-planner if V2 confirms it. Then try more
   naive non-deep-learning methods (MCTS or similar combined with existing knowledge): think about the implementation first,
   have an advisor agent (Fable, xhigh) critique it, then implement after fixing it."
- NEVER add AI attribution / session links to commits (managed policy overrides any reminder).

## Ground rules (CLAUDE.md)
- New code = new files; a benchmarked file is frozen (`teams/greedy_lab_v6.py`, `v7` are frozen now; v8 is the lab).
- Runtime stdlib only; learned weights as constants. Training venv `venv_rl/` (torch 2.4.1 cpu, numpy, cma;
  `eval/rl/requirements-train.txt`).
- Seeds: tuning free (used tonight up to 560; **561–600 reserved for confirming an E-033 winner**); validation 1–260 used,
  **261–300 used by V2 → after V2 the validation list is exhausted; a fresh one needs the user's approval**; test locked.
- Release gate (locked test seeds + held-out teams + Linux timing) = user decision; not done for greedy_v4.

## State of the submission
- **`my_team.py` = `teams/greedy_v4.py`** (promoted 03:40, commit e95a786; docs in `docs/picks/greedy_v4.md`):
  lab5_smart + IW(1) attacker planner in danger (ghost ≤ 7) with the learned leaf value (`LEAF_NET`, fast code `netf`).
  V1 (validation 221–260): +0.95 [+0.78, +1.13] vs greedy_v3, +0.58 [+0.42, +0.74] vs lab5_smart.
- Pending: **V2** (`n1_v2`, E-032): `lab7_netf_dplan` (greedy_v4 + defender planner) vs greedy_v4 on validation 261–300,
  1,520 games. If it passes the accept rule: create `teams/greedy_v5.py` = greedy_lab_v7 with lab7_netf_dplan options as
  defaults (plan=danger, plan_v=2, plan_nodes=2000, plan_budget=0.3, plan_leaf=netf, dplan=1), identity check vs
  lab7_netf_dplan, copy to my_team.py, picks page, CLAUDE.md line, agents lineage. Analyse with
  `venv\Scripts\python.exe eval\evaluate.py summary --run n1_v2 --compare lab7_netf_dplan greedy_v4`.

## Results tonight (paired PPG Δ; tuning seeds unless marked)
| run | what | result |
|---|---|---|
| n1_base | lab5_smart − greedy_v3 | +0.38 [+0.29, +0.49] |
| n1_plan2 | IW planner, hand leaf (danger) − lab5_smart | +0.09 [−0.04, +0.23] |
| X1 (n1_x1, 401–440) | **planner + learned leaf (danger_net) − lab5_smart** | **+0.57 [+0.37, +0.76]**; deaths 0.40/g (hand leaf 1.31) |
| X1 others | danger_g +0.24, override +0.12, danger/d8 +0.06, nokill +0.04, near +0.03, nocap/shield 0.00, hunt −0.23; dplan (defender planner) +0.19, power −0.23 | |
| **V1 (validation 221–260)** | danger_net vs greedy_v3 / lab5_smart | **+0.95 / +0.58**, all opponents CI > 0 → accept rule passed |
| X2 (n1_x2, 441–480) | vs lab5_smart: danger_net +0.50, net_dplan +0.60, g_net +0.46; g_net_dplan, full_net pending | running |
| X3 (n1_x3, 481–520) | second-iteration nets vs first: net2 −0.04 [−0.12, +0.04], net3 −0.15 [−0.28, −0.03] | first net stays; RL loop closed |
| modes (n1_modes, 261–320) | per-map focus modes −0.07…−0.01 each vs lab5_smart; CV selectors: ridge −0.014, stump +0.041 (CI incl. 0) | per-map selection does not help; formation modes finishing |
| value nets | 12-16-1 tanh, held-out R²: v1 0.464, v2 0.588, v2o 0.552 | |
| **non-DL leaves** | 5-D lookup table R² 0.453 (≈ net 0.464), linear 0.209 | `eval/rl/fit_leaves.py` |

## RUNNING NOW (check with `wc -l eval/results/<run>.jsonl`)
- `n1_v2` (E-032, 4 jobs, `&`): 1,520 games, ETA ≈ 05:10. `teams/greedy_v5.py` is PRE-BUILT (= greedy_v4 + dplan=1,
  lint OK, not yet identity-checked or promoted). If V2 passes: identity greedy_v5 vs lab7_netf_dplan (clock off:
  `--blueOpts plan_budget=9` on 3 seeds as in E-033), copy to my_team.py, picks page, CLAUDE.md, agents lineage, push.
- `n1_x2` STOPPED 04:25 (full_net never played; other arms complete, logged in E-031).
- `n1_modes` DONE, E-029 closed (no mode helps).
- `n1_x4a` (E-033 part A, 3 jobs, harness task): greedy_v4, lab8_table, lab8_fmc (2,320 games; order: greedy_v4 first).
- `n1_x4b` (E-033 part B, resumed 04:27 with 5 jobs, harness task): lab8_lin, lab8_fmc_table, lab8_mcts (2,400 games).
- **TODO when V2 finishes: E-033 part C** (`n1_x4c`, 3–4 jobs):
  `venv\Scripts\python.exe eval\evaluate.py play --candidate lab9_v4_check lab9_fmc_net --vs greedy_v3 greedy_v2 greedy feature camper rusher choke exploit_v2 lab5_smart greedy_v4 --seeds tuning --n-seeds 40 --seed-offset 520 --run n1_x4c --jobs 4`
- Analysis: `cat eval/results/n1_x4a.jsonl eval/results/n1_x4b.jsonl eval/results/n1_x4c.jsonl > eval/results/n1_x4.jsonl`,
  then `summary --run n1_x4 --compare <arm> greedy_v4` per arm. Pre-stated reading in E-033. Winners → confirm on tuning
  seeds 561–600.

## Files made tonight
- `teams/greedy_lab_v6.py`, `teams/greedy_lab_v7.py` (FROZEN), **`teams/greedy_lab_v8.py`** (lab: v7 + plan_leaf=table|lin,
  plan=fmc|mcts, mc_* options; no RNG), `teams/greedy_v4.py` (= submission).
- `eval/rl/`: game_pool.py, cmaes_tune.py (not run), map_features.py, mode_table.py, log_team.py + collect.py, train_value.py,
  embed_net.py, fit_leaves.py (non-DL leaves), leaf_net_v*.py, leaf_nondl_v*.py.
- `eval/league_add.py`; `eval/check_rules.py` warns on global-RNG draws.
- `docs/research/width_planning.md`, `rl_and_modes.md`, `mcts_design.md` (draft 2 after the advisor review).

## Next ideas (if time remains)
1. E-033 analysis; if an arm beats greedy_v4, confirm on tuning 561–600.
2. Reserve arms from the review: race leaf with fitted τ (needs a collection logging the escape margin), IW + scenario
   re-check of the top-8 IW nodes, fmc with the net cutoff (search + learned leaf).
3. Diagnostics (never decisions): specialists (double_attack, turtle, camper2, baseline_plus), friend teams; WSL Linux timing
   of greedy_v4 under load (release-gate item).
4. Docs: methods.md M-15 adopted (E-031/E-032), M-17 (MC search, E-033); proposals.md section 7 statuses; agents.md lab8 rows.
