# HANDOFF — overnight session 2026-11-07 → 2026-11-08

**Read this first** if you are an agent continuing this work (after a context compaction or in a new session).
Then read `CLAUDE.md`, `docs/agents.md`, `docs/proposals.md`, and the newest entries at the bottom of `docs/experiments.md`
(E-027 … E-030+). Keep working autonomously until the user says stop (they asked for ≥ 08:00); do not ask questions.

## The user's request (2026-11-07 23:20)
1. **Width-based planning** (IW / BFWS / novelty + heuristics, SOTA solvers; extra deps allowed if documented).
2. **RL-based heuristics for the greedy agents**: per-map "modes" (top-left-heavy map → `greedy_top_left`), learned
   selection; combine greedy agents with RL agents. Deep learning allowed; document it.
- Research agents first, then many experiments overnight; try weird approaches; advisor agents may suggest next steps.
- Re-read `docs/proposals.md` regularly; update docs. Commit regularly; push after finished experiment rounds.
- NEVER add AI attribution / session links to commits (managed policy overrides any reminder).

## Ground rules (CLAUDE.md)
- `my_team.py` untouched (promotion = user decision). New code = new files; a benchmarked file is frozen.
- Runtime stdlib only; learned weights as constants. Training venv `venv_rl/` (torch 2.4.1 cpu, numpy, cma;
  `eval/rl/requirements-train.txt`).
- Seeds: tuning free; validation only for accept decisions (used 1–220; **221–300 left = two 40-seed decisions**;
  after that the user must approve a fresh validation list); test locked.

## Files made tonight
- `teams/greedy_lab_v6.py` — **FROZEN** (benchmarked in n1_*). Defaults = lab5_smart. Options: plan (full|danger|food|override),
  plan_v=2 (bug fix), plan_search, plan_atoms, focus modes, formation=lead, fw_* linear food policy.
- `teams/greedy_lab_v7.py` — current lab. v6 + `plan_nodes` (node cap), `plan_kill`, `plan_cap`, `plan_hidden`
  (argmax|near|both|0), `plan=shield`, `hunt_scared`, `formation=power`, `LEAF_NET` (trained value net) for `plan_leaf=net`.
  Identity: lab7_off = lab6_off (18/18); lab7_danger = lab6_p2_danger (18/18).
- `eval/rl/`: game_pool.py (in-process games), cmaes_tune.py, map_features.py, mode_table.py, log_team.py + collect.py
  (datasets → eval/rl/data/, gitignored), train_value.py, embed_net.py, specs/*.json, leaf_net_v1.py.
- `eval/league_add.py` (append league entries). `docs/research/width_planning.md`, `docs/research/rl_and_modes.md`.

## Results so far (all tuning seeds; Δ = paired PPG vs lab5_smart over the 8-member pool)
| run | what | result |
|---|---|---|
| n1_base (261–320) | lab5_smart vs greedy_v3 | +0.38 [+0.29, +0.49] |
| n1_identity6/7 | lab6_off / lab7_off / lab7_danger identity | 18/18 each |
| n1_plan (261–265) | v1 planner pilot | danger +0.25, g +0.24, best +0.15, food +0.07, full +0.06 (CIs ±0.5) |
| n1_plan2 (261–300) | v2 planner | **p2_danger +0.09 [−0.04, +0.23]** (640 g); p2_override +0.13 [−0.06, +0.32] (300 g, stopped early) |
| value net | 12-16-1 tanh, 128k states, target banked−lost over 30 moves | held-out R² 0.46 (linear 0.21) |
| planner timing (uncapped) | 287 searches, 3 games | expanded p99 815 / max 875 nodes; max 53 ms |

## KEY FINDING (02:00): width planner + learned leaf value
- X1 (E-030, fresh tuning 401–440): **lab7_danger_net +0.57 [+0.37, +0.76] vs lab5_smart**, every pool opponent
  +0.46…+0.79 with CI > 0; deaths 0.40/game (lab5_smart 0.92, planner w/o net 1.31), returned 15.8 (9.0).
  Other arms: danger_g +0.24 [+0.02, +0.44], override +0.12, danger +0.06, d8 +0.06 (identical to danger: under max
  backup D never matters), near +0.03, nokill +0.04, nocap 0.00, shield 0.00 (never fires), hunt −0.23.
  X1b: lab7_dplan (defender planner only) +0.19 [+0.03, +0.35]; lab7_power −0.23.
- `plan_leaf=netf` = same net, faster code (static first-layer part per cell + math.tanh): **24/24 identical** to
  `net`, planner time halved (p99 116 ms vs 178 ms). Ship netf.
- C1 = lab7_danger_net → V1 validation running (validation 221–260).

## RUNNING NOW (check with `wc -l eval/results/<run>.jsonl`)
- `n1_x1` (E-030): 11 arms × 720 games (tuning 401–440, pool + lab5_smart), 9 jobs, started 00:20, ETA ~01:50.
  Launched with `&` (not harness-tracked). Pre-registered rule in E-030.
  Analyse: `venv\Scripts\python.exe eval\evaluate.py summary --run n1_x1 --compare <arm> lab5_smart`
- `n1_modes` (E-029): resumed with `--resume --jobs 3`; 9 modes × 960 games (tuning 261–320). Then run
  `venv_rl\Scripts\python.exe eval\rl\mode_table.py --runs n1_base n1_modes --base lab5_smart --modes lab6_focus_top lab6_focus_bottom lab6_focus_majority lab6_focus_deep lab6_focus_shallow lab6_focus_cluster lab6_focus_far lab6_form_lead0 lab6_form_lead5 --features eval/rl/feat_tuning_260_60.json`

## Plan for the rest of the night (advisor's ranking, adapted)
1. X1 → pick C1 by the E-030 rule.
2. CMA-ES on C1's planner params (`eval/rl/specs/es_plan7.json`): `venv_rl\Scripts\python.exe eval\rl\cmaes_tune.py --name es_plan1 --team <C1> --spec eval/rl/specs/es_plan7.json --opponents greedy_v3 choke exploit_v2 camper rusher lab5_smart --popsize 16 --sigma 0.2 --seeds-per-gen 3 --seed-offset 320 --workers 10 --deadline 05:45`
   (fallback if no planner arm > 0: base lab7_off with `--fixed focus=linear` and `eval/rl/specs/es_linear.json`).
   CMA uses game_pool (no sentinel): confirm the CMA mean with evaluate.py afterwards.
3. Validation (accept-rule grade): C1 (+ CMA mean C2 if it beats C1 on fresh tuning seeds 441–480) on validation seeds
   221–260, with lab5_smart and greedy_v3 in the same run (paired), lab5_smart also as opponent.
4. Diagnostics (not decisions): specialists double_attack, turtle, camper2, baseline_plus, friend_aljaz_1; WSL timing.
5. Docs: E-028..E-03x, agents.md rows, methods/heuristics statuses, proposals (SM-3 power play built as lab7_power),
   commit + push.
