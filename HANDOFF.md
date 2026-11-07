# HANDOFF — overnight session 2026-11-07 → 2026-11-08

**Read this first** if you are an agent continuing this work (after a context compaction or in a new session).
Then read `CLAUDE.md`, `docs/agents.md`, `docs/proposals.md`, and the newest entries at the bottom of `docs/experiments.md`.

## The user's request (verbatim intent, 2026-11-07 23:20)
Run autonomously through the night (until at least 08:00 on 2026-11-08). Do not ask questions; keep working.
1. **Width-based planning**: incorporate IW / BFWS / novelty-based planning with heuristics and state-of-the-art solvers. Extra dependencies allowed (document them in requirements / docs).
2. **RL-based heuristics for the greedy agents**: per-map "modes" (e.g. a top-left-heavy map → a `greedy_top_left` configuration), learned selection; combine greedy agents with RL agents. Deep learning (PyTorch) allowed; document it.
- Run research agents first, then many experiments overnight with multiple agents. Try weird approaches too; advisor agents may suggest what to try next.
- Re-read `docs/proposals.md` regularly and update docs when it makes sense.
- Commit regularly (and push after finished experiment rounds, per the user's memory). Never add AI attribution to commits.
- Write/refresh this handoff file regularly; autocompact is set to 60% (`.claude/settings.local.json`, may only apply to new sessions).

## Ground rules that still apply (from CLAUDE.md)
- `my_team.py` is the submission; never edit it directly. New agents = new files `teams/<name>_vN.py`, frozen once benchmarked.
- Promotion to `my_team.py` is a **user decision** (lab5_smart passed the accept rule in E-025 but is not promoted). Do not promote tonight; prepare evidence.
- Runtime: stdlib only (no numpy/torch at runtime unless the professor installs them — not requested). Training may use `venv_rl/` (torch 2.4.1 CPU, numpy 1.24.4, cma 3.3.0). Ship learned weights as Python constants or a read-only data file next to the agent.
- Time budget per move ≤ 0.5 s internal; check with `-c` runs (evaluate.py does this).
- Seeds: tuning (free), validation (accept/reject only; used so far 1–220), test (locked).

## State at start
- `my_team.py` = greedy_v3. Best agent = `lab5_smart` (teams/greedy_lab_v5.py; +0.25 [+0.11, +0.40] vs greedy_v3 on validation 181–220, E-025).
- Reference pool (8): greedy_v3, greedy_v2, greedy, feature, camper, rusher, choke, exploit_v2.

## Plan for the night (see phase tracker; status below is updated as work proceeds)
| # | Track | What | Status |
|---|---|---|---|
| 0 | setup | research agents (width planning → `docs/research/width_planning.md`; RL/modes → `docs/research/rl_and_modes.md`); code map of lab_v5; `venv_rl` | running |
| 1 | ref | `n1_base`: lab5_smart + greedy_v3 vs pool, tuning seeds 261–320 (offset 260, 60 seeds) — reference for all screens tonight | running |
| 2 | infra | `teams/greedy_lab_v6.py` = lab5_smart defaults + exposed parameter vector + "modes" (food-region / entry preferences etc.) | todo |
| 3 | width | IW(1)/RIW/BFWS planner module for the attacker (pure Python, own forward model) | todo |
| 4 | modes | mode × map table on tuning seeds → map-feature selector (trained offline, exported as constants) | todo |
| 5 | ES | CMA-ES tuning of lab6 parameters vs pool (CRN seeds) | todo |
| 6 | hybrid | greedy + learned module (e.g. learned food-target scorer / value net for planner leaves) | todo |
| 7 | validate | best candidates on fresh validation seeds (221+) vs pool, paired with greedy_v3 and lab5_smart | todo |

## Run log (newest last)
- 23:25 started `n1_base` (eval/results/n1_base.jsonl).
- 23:45 `teams/greedy_lab_v6.py` built: defaults = lab5_smart (identity 18/18 verified, run `n1_identity6`).
  New options: `plan` (full|danger|food), `plan_search` (iw|best), `plan_atoms`, `plan_*` params; `focus`
  (top|bottom|deep|shallow|cluster|far|majority|linear|auto) + `focus_w`; `fw_*` weights for focus=linear;
  `threat_dist`, `open_margin`, `standoff_moves` exposed. 14 league entries `lab6_*` added
  (`eval/league_add.py` appends entries without reformatting league.json).
- 23:50 pilot `n1_plan` (6 planner variants, 5 seeds) started.
- Tools: `eval/rl/game_pool.py` (in-process parallel games, any opts), `eval/rl/cmaes_tune.py` (CMA-ES over a
  JSON param spec; logs to eval/rl/runs/, gitignored).
- Planner standalone speed: IW(1) ≤ 22 ms per move at horizon 40 (scratch test), so budget is not an issue.
- 23:45 `n1_base` done: lab5_smart − greedy_v3 = +0.38 [+0.29, +0.49] (60 seeds). Pilot `n1_plan` done (5 seeds):
  plan_danger +0.25, plan_g +0.24, best +0.15, food +0.07, full +0.06 vs lab5_smart (CIs ±0.5).
- Research review found planner bug (dead successors marked atoms seen) → fixed as `plan_v=2`; added
  `plan=override` (+`plan_margin`), v3 options `plan_novelty=piw`, `plan_models=m1m2`, `plan_leaf=net` (LEAF_NET
  still None — train with eval/rl/train_value.py on eval/rl/data/d1_lab6off.npz, then paste the exported list).
  Replay check: patched file reproduces recorded n1_plan2 games exactly.
- RUNNING (started ~23:43–23:50): `n1_modes` (9 modes × 60 seeds, 8,640 games, ETA ~01:40), `n1_plan2`
  (6 planner variants × 40 seeds, 3,840 games, ETA ~01:50; launched with `&`, not tracked by the harness — check
  `wc -l eval/results/n1_plan2.jsonl`), data collection `d1_lab6off` (450 games, 3 workers), advisor agent.
- Docs: E-027 (setup) written; E-028 (planner) and E-029 (modes) written with pre-registered rules, results pending.
- Analysis commands:
  `venv\Scripts\python.exe eval\evaluate.py summary --run n1_base n1_plan2 --compare lab6_p2_danger lab5_smart`
  `venv_rl\Scripts\python.exe eval\rl\mode_table.py --runs n1_base n1_modes --base lab5_smart --modes lab6_focus_top lab6_focus_bottom lab6_focus_majority lab6_focus_deep lab6_focus_shallow lab6_focus_cluster lab6_focus_far lab6_form_lead0 lab6_form_lead5 --features eval/rl/feat_tuning_260_60.json`

## Where things are
- Research reports: `docs/research/`.
- New teams: `teams/greedy_lab_v6.py` (planned), planner modules next to them.
- Training scripts: `eval/rl/` (planned). Training venv: `venv_rl/` (gitignored).
