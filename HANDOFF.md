# HANDOFF — overnight session 2026-11-07 → 2026-11-08 (closed 08:00)

**Read this first** if you are an agent continuing this work (after a context compaction or in a new session).
Then read `CLAUDE.md`, `docs/agents.md`, `docs/proposals.md` §7, and the newest entries at the bottom of `docs/experiments.md`
(E-027 … E-035). The overnight session is over: **nothing is running**, and the next steps below need user decisions.

## The user's requests (overnight)
1. (23:20) **Width-based planning** (IW / BFWS / novelty + heuristics; extra deps allowed if documented) and **RL-based
   heuristics** for the greedy agents (per-map modes, learned selection, combining greedy with RL). Research agents first,
   many experiments overnight, try weird approaches, advisor agents allowed. Re-read `docs/proposals.md` regularly; update
   docs; commit regularly; push after finished experiment rounds.
2. (03:35) "Promote lab7_danger_net to my_team for now, compare it to defender-planner if V2 confirms it. Then try more
   naive non-deep-learning methods (MCTS or similar combined with existing knowledge): think about the implementation first,
   have an advisor agent (Fable, xhigh) critique it, then implement after fixing it." → all done (E-032, E-033).
3. (morning) Update the docs with all findings and push to main → done.
- NEVER add AI attribution / session links to commits (managed policy overrides any reminder).

## Ground rules (CLAUDE.md)
- New code = new files; a benchmarked file is frozen (`teams/greedy_lab_v6.py` … `v10.py` are frozen; `v11` is the lab).
- Runtime stdlib only; learned weights as constants. Training venv `venv_rl/` (torch 2.4.1 cpu, numpy, cma;
  `eval/rl/requirements-train.txt`).
- Seeds: **validation 1–300 all used** (last: V2, 261–300) → a fresh validation list needs the user's approval.
  Tuning seeds used overnight: 1–50 (training data), 261–600 (screens); test seeds locked (1 of 3 uses spent, E-021).
- Release gate (locked test seeds + held-out teams; Linux timing is done) = user decision; not done for greedy_v4.

## State of the submission
- **`my_team.py` = `teams/greedy_v4.py`** (promoted 03:40, commit e95a786; docs in `docs/picks/greedy_v4.md`):
  lab5_smart + IW(1) attacker planner in danger (ghost ≤ 7) with the learned leaf value (`LEAF_NET`, fast code `netf`).
  V1 (validation 221–260): +0.95 [+0.78, +1.13] vs greedy_v3, +0.58 [+0.42, +0.74] vs lab5_smart.
- V2 (validation 261–300): `lab7_netf_dplan` (greedy_v4 + defender planner) **rejected**, −0.03 [−0.11, +0.05] (h2h 1.69).
- Linux / Python 3.8 timing under full load: 40 games, 0 warnings, max move 0.283 s (E-032).

## Results overnight (paired PPG Δ; tuning seeds unless marked)
| run | what | result |
|---|---|---|
| n1_base | lab5_smart − greedy_v3 | +0.38 [+0.29, +0.49] |
| n1_plan2 (E-028) | IW planner, hand leaf (danger) − lab5_smart | +0.09 [−0.04, +0.23] |
| X1 (E-030, 401–440) | **planner + learned leaf (danger_net) − lab5_smart** | **+0.57 [+0.37, +0.76]**; deaths 0.40/g (hand leaf 1.31) |
| X1 others | danger_g +0.24, dplan +0.19, override (hand leaf) +0.12, danger/d8 +0.06, nokill +0.04, near +0.03, nocap/shield 0.00, hunt −0.23, power −0.23 | |
| **V1 (validation 221–260)** | danger_net vs greedy_v3 / lab5_smart | **+0.95 / +0.58**, all opponents CI > 0 → accepted, promoted as greedy_v4 |
| X2 (E-031, 441–480) | vs lab5_smart: danger_net +0.50, net_dplan +0.60, g_net_dplan +0.52, g_net +0.46 | net_dplan → V2 |
| X3 (E-031, 481–520) | second-iteration nets vs first: net2 −0.04, net3 −0.15 | RL loop closed |
| modes (E-029, 261–320) | focus modes −0.07…−0.01; formations lead0 −0.76, lead5 −1.05; CV selectors ≤ +0.04 | map modes closed |
| **V2 (validation 261–300)** | defender planner on greedy_v4 | −0.03 [−0.11, +0.05] → rejected |
| E-033 (521–600) | non-DL vs greedy_v4: **quad leaf −0.02 [−0.09, +0.04] (≈ net)**, lin −0.11, table −0.33, MC re-check −0.43, mcts −0.52, fmc −0.67…−0.72 | MC rejected (T-60); smoothness > R² (T-59) |
| E-034 (321–400) | vs greedy_v4: trigger 5/9 −0.04/−0.00, horizon 40 −0.03, plan_min 0.3 +0.01, 60-move target −0.03, full −0.38, **override +0.06 [+0.00, +0.12]** (1,440 games, worst opponent −0.06) | flat optimum; override = candidate |
| E-035 (501–510, diagnostic) | greedy_v4 − greedy_v3 vs 13 outside opponents | +0.77 [+0.57, +0.98], none negative |

## Open decisions for the user
1. **Release gate for greedy_v4**: one locked test-seed run + held-out teams (`heldout_a`, `heldout_b`).
2. **Fresh validation seed list** (new generator seed). Then validate `lab7_netf_override` by the accept rule; if it
   passes, build `teams/greedy_v5.py` = `teams/greedy_lab_v7.py` with plan=override + greedy_v4's other options.
3. **Reference pool update**: add greedy_v4 and lab5_smart (and maybe drop weak members).
4. Policy: global-RNG draws are only a lint warning (T-02 allows them).

## Files made overnight
- `teams/greedy_lab_v6.py` … `v10.py` (FROZEN), **`teams/greedy_lab_v11.py`** (lab). v6: planner, modes, formations;
  v7: node cap, ablations, learned leaf; v8: plan_leaf=table|lin, plan=fmc|mcts; v9: mc_check, mc_leaf=net;
  v10: plan_leaf=quad; v11: plan_leaf=net60f. `teams/greedy_v4.py` (= submission).
- `eval/rl/`: game_pool.py, cmaes_tune.py (not run), map_features.py, mode_table.py, log_team.py + collect.py, train_value.py,
  embed_net.py, fit_leaves.py (non-DL leaves), leaf_net_v*.py, leaf_net_h60.py, leaf_nondl_v*.py, leaf_quad_v1.py;
  data_d1/d2/d3.log (collection summaries; the datasets themselves are gitignored in `eval/rl/data/`).
- `eval/league_add.py`; `eval/check_rules.py` warns on global-RNG draws.
- `docs/research/width_planning.md`, `rl_and_modes.md`, `mcts_design.md` (draft 2 after the advisor review).

## Ideas not run (in `docs/proposals.md` §7 and `docs/agents.md` "Open ideas")
- MC-2 race leaf with a fitted τ; MC-3 IW + scenario re-check; LF-1 smoothed table (direct T-59 test);
  GM-1 ghost model calibrated from replays; MM-2 CMA-ES on the linear food policy; JX-1 junction-graph macro-IW.
