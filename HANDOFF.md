# HANDOFF — overnight session 2026-11-07 → 2026-11-08 (closed 08:00)

**Read this first** if you are an agent continuing this work (after a context compaction or in a new session).
Then read `CLAUDE.md`, `docs/agents.md`, `docs/proposals.md` §7, and the newest entries at the bottom of `docs/experiments.md`
(E-027 … E-039). **Afternoon session 2026-11-08 (see "Afternoon" below): E-039 screen `n2_s1` done; option C splits `n2_s2` may be running.**

## The user's requests (overnight)
1. (23:20) **Width-based planning** (IW / BFWS / novelty + heuristics; extra deps allowed if documented) and **RL-based
   heuristics** for the greedy agents (per-map modes, learned selection, combining greedy with RL). Research agents first,
   many experiments overnight, try weird approaches, advisor agents allowed. Re-read `docs/proposals.md` regularly; update
   docs; commit regularly; push after finished experiment rounds.
2. (03:35) "Promote lab7_danger_net to my_team for now, compare it to defender-planner if V2 confirms it. Then try more
   naive non-deep-learning methods (MCTS or similar combined with existing knowledge): think about the implementation first,
   have an advisor agent (Fable, xhigh) critique it, then implement after fixing it." → all done (E-032, E-033).
3. (morning) Update the docs with all findings and push to main → done.
4. (later) Release gate, fresh validation list, pool trim (E-036, E-037) → done.
5. (afternoon) Validate override mode as greedy_v5 (E-038: **rejected**); have a Fable 5.1 max-effort reviewer critique
   greedy_v4 / greedy_v5 with ≥ 2 improvements each (`docs/research/review_v4_v5.md`); think them through, implement,
   test new agents against greedy_v4 and the top 3 agents (E-039, in progress).
- NEVER add AI attribution / session links to commits (managed policy overrides any reminder).

## Ground rules (CLAUDE.md)
- New code = new files; a benchmarked file is frozen (`teams/greedy_lab_v6.py` … `v11.py` are frozen; `v12` is the lab).
- Runtime stdlib only; learned weights as constants. Training venv `venv_rl/` (torch 2.4.1 cpu, numpy, cma;
  `eval/rl/requirements-train.txt`).
- Seeds: **validation 1–300 all used** (last: V2, 261–300) → a fresh validation list needs the user's approval.
  Tuning seeds used overnight: 1–50 (training data), 261–600 (screens); test seeds locked (2 of 3 uses spent: E-021, E-037). Validation now uses `eval/seeds/validation2.txt`.
- Release gate for greedy_v4: **passed** (E-037, 2026-11-08).

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

## User decisions (morning, E-036) — all carried out
- greedy_v4 confirmed as `my_team.py`.
- Reference pool now **8 members**: greedy_v4 (incumbent), greedy_v3, greedy_v2, feature, camper, choke, exploit_v2,
  lab5_smart (greedy_v4 / lab5_smart added; greedy v1 / rusher dropped; analysis in E-036). Command in CLAUDE.md.
- **Fresh validation list** `eval/seeds/validation2.txt` (300 seeds, `random.Random(20261108)`, 0 overlaps; `--seeds validation2`;
  unused so far). Next candidate for it: `lab7_netf_override` (if it passes, `teams/greedy_v5.py` = `teams/greedy_lab_v7.py` with
  plan=override + greedy_v4's other options). Power note: a true +0.06 clears CI > 0 with ≈ 30 % chance on 40 seeds, ≈ 50 % on 80.
- **Release gate E-037** (pre-registered, commit 24c61aa): greedy_v4 vs greedy_v3 on all 100 locked test seeds against the
  6 non-mirror pool members + heldout_a / heldout_b + h2h (3,400 games, run `test2`; test-seed use 2 of 3).
  **PASSED**: pool +0.83 [+0.73, +0.94], held-out +1.02 [+0.85, +1.20], h2h 2.38, 0 / 0 / 0, max move 0.310 s.
  greedy_v4 is the release candidate for the 2026-11-23 test run. One test-seed use left.
- The submission has no global-RNG lint warnings, so that policy point needs no decision.

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

## Afternoon 2026-11-08 (E-038, E-039)
- V3 (`n1_v3`, validation2 1–80): greedy_v5 (override) − greedy_v4 = −0.05 [−0.15, +0.05] → rejected; greedy_v4 stays.
- Review saved: `docs/research/review_v4_v5.md`. Chosen arms (lab v12, all default-off options on greedy_v4's options):
  `lab12_assist`, `lab12_defsc`, `lab12_latetie`, `lab12_pblock`, `lab12_m1m2`, `lab12_v5fix` (league.json).
- Screen `n2_s1` (tuning 101–140, 6,080 games) vs greedy_v4 + top 3 (greedy_v5, lab7_netf_dplan, lab10_quad) + pool.
  Rule (E-039): promising = Δ vs greedy_v4 > 0 and no opponent < −0.3 → `lab12_combo` of promising switches →
  validation2 81–160 vs pool + top 3 under the accept rule → only if it passes: `teams/greedy_v6.py` → `my_team.py`.
- Analyse with: `venv\Scripts\python.exe eval\evaluate.py summary --run n2_s1 --compare <arm> greedy_v4`.
- **Option C (user, queued)**: after `n2_s1`, split `lab12_v5fix` → `lab12_v5guard`, `lab12_v5asym` if its Δ ≥ −0.07, and `lab12_defsc` → `lab13_defsc_posture`, `lab13_defsc_cap` if its Δ ≥ −0.06 (gates 0/0/0); run `n2_s2` vs the same 11 opponents on tuning 101–140, paired with n2_s1's greedy_v4 games; then stage 2 (E-039 amendment).
- **Screen done** (E-039): Δ vs greedy_v4 — def_scared +0.07 (top 3 +0.24, pool −0.01), m1m2 +0.03, assist +0.00 (+1 pt), plan_blocked +0.00 (+1 pt),
  late_tie −0.01, v5fix 0.00. Promising by the rule: assist, def_scared, plan_blocked, m1m2. Both option C conditions held → `n2_s2` started
  (`lab12_v5guard lab12_v5asym lab13_defsc_posture lab13_defsc_cap`, 3,520 games). Analyse with `summary --run n2_s1 n2_s2 --compare <arm> greedy_v4`
  and scratchpad-style exact deltas; then build `lab13_combo` = B with plan_nodes 1200, plan_models m1m2, assist 1, plan_blocked 1, def_scared = the
  promising parts; smoke on tuning 141–143; stage 2 on validation2 81–160 (`--seeds validation2 --seed-offset 80 --n-seeds 80`).
