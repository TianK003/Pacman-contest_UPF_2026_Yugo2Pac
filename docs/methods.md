# Methods for building the agent

A method is *how* the agent decides: rules, search, learning. The heuristics in [heuristics.md](heuristics.md) are the knowledge those methods use. Statuses start at `idea`. Change them only together with an experiment ID.

## Constraints that decide which methods are viable

| Constraint | Consequence |
|---|---|
| ≤ 1 s per move, likely on a loaded cluster node; Python 3.8; stdlib only until Q2 is answered | Runtime methods must be cheap and *anytime* (return the best answer so far when time runs out). Heavy neural nets need numpy/torch, which may be missing. |
| 15 s startup per agent | Map analysis and loading precomputed parameters fit. Per-game training does not. |
| Random, unseen 34×18 maps | Nothing can be tuned per layout. Learned components need map-agnostic inputs. |
| Partial observability (5-square sight, noisy Manhattan sonar) | Search and learning need a belief or a determinisation of hidden opponents (H-S01). |
| 2 cooperating agents vs 2 adversaries | Coordination matters (shared team object, roles). |
| A game takes ~1.3 s of CPU for cheap agents once the engine's per-move sleep is switched off (`--delay-step 0`, E-009; it was ~40 s with the sleep); `generate_successor` copies the state on every call | Deep lookahead with `GameState` is expensive. Measure its cost before choosing a search depth (planned). Learning methods that need millions of steps would need our own fast simulator. |
| About 7 weeks to the deadline (2026-10-16 → 2026-12-03); test run on 2026-11-23 | Prefer methods that give a working agent early and improve step by step. |
| No staff reference teams locally; only `baseline_team` | We must build our own opponent pool (self-play, older versions, specialists) to evaluate or train anything. |

## Overview

| ID | Method | Role in the agent | Effort | Risk | Evidence in this contest | Verdict |
|---|---|---|---|---|---|---|
| M-01 | Rule-based / FSM / behaviour tree ("fixed policy") | strategic + tactical core | medium | low | strongest in write-ups | **recommended core** |
| M-02 | Feature-weighted evaluation + offline parameter tuning | scoring layer + tuning | low–medium | low | baseline style; tuning [untested] | **recommended** |
| M-03 | BFS / A* / Dijkstra with risk-weighted costs | motion planning | low | low | used by nearly all top teams | **recommended** |
| M-04 | HMM exact filtering / particle filter | perception | medium | medium | mixed but common | **recommended, behind tests** |
| M-05 | Local minimax / expectimax (alpha-beta, iterative deepening) | close-quarters tactics | medium | medium | mixed | optional module |
| M-06 | MCTS (UCT / ISMCTS) with pruning | tactical module | high | high | weak when used alone | experiment only |
| M-07 | Approximate Q-learning (linear features) | learned weights | medium | medium | mixed | optional, compare with M-02 |
| M-08 | Deep RL (DQN, PPO, MAPPO) | learned policy | very high | very high | no successful report found | stretch only |
| M-09 | Classical planning (PDDL + Metric-FF) | planning core | high | high (planner availability) | one UoM team did well | not recommended |
| M-10 | Pursuit–evasion "race" analysis | adversarial shortcut | low | low | [untested] formally | **recommended** (= H-S03) |
| M-11 | Evolutionary search (GA / NEAT) over parameters or tree structure | offline tuner | medium | medium | [untested] | optional tuner |
| M-12 | Imitation learning | — | — | — | no strong demonstrator available | not feasible now |
| M-13 | Expert iteration / distilling search into a fast policy | fast policy layer | high | medium | [untested] here | stretch, after M-05/M-06 exist |
| M-14 | Potential field / influence map | attacker policy | low | medium | none found | experiment (E-008) |

---

### M-01: Rule-based / behaviour tree / FSM ("fixed policies")
- **What**:
  - Hand-written decision logic picks the *goal*, e.g. "role = attacker; target = safest valuable food; escape if threatened; return when H-S04 fires".
  - Search (M-03) executes the goal.
  - Structure it as a behaviour tree or prioritised rules, so each rule can be tested and switched off.
- **Why it fits**: cheap at runtime, transparent when debugging from replays, and it degrades gracefully.
- **Evidence**: most well-placed teams in the write-ups use a rule or decision layer plus search [reported: LuChenyang3842 3rd/152, infinityglow, AlanChaw 2nd, jhammarstedt winner (heuristic A*)].
- **Risks**: rule conflicts and oscillation (H-S10), and hand-tuned thresholds. Fix the thresholds with M-02.
- **Status**: implemented (v1, prioritised rules) in `teams/greedy_v1.py` and tested in E-002: 40-0-0 vs the baseline.

### M-02: Feature-weighted evaluation + offline tuning
- **What**:
  - Score candidate actions or goals with `Σ wᵢ·fᵢ`, as in `baseline_team.py`.
  - Tune the weights and the rule thresholds **offline**: run batched games against an opponent pool on many random seeds and optimise the win rate or score.
  - Optimisers to try: random search, CMA-ES, SPSA, a GA (M-11).
  - Only the resulting constants ship in `my_team.py`, so there is no runtime dependency.
- **Why it fits**: the most improvement per hour of work once the harness exists. Offline tuning may use any library on our machines.
- **Risks**:
  - Overfitting to the opponent pool (T-37).
  - Noisy fitness (T-35), so use paired seeds.
  - Games cost ~1.3 s each with `--delay-step 0` (E-009), i.e. ~2,500 games per hour per process; parallelise across cores.
- **Status**: **tested** as the F1 `FeatureAttacker` (`teams/families_v1.py`) with hand-set weights: +0.44 on 10 tuning seeds (E-008), but **+0.07 [−0.08, +0.20] on 40 fresh tuning seeds** (E-010), i.e. about greedy's level. Weights are exposed for offline tuning, which is now cheap (E-009). Not tuned yet.

### M-03: Path planning with risk-weighted costs
- **What**: BFS, A* or Dijkstra over our own cell graph (not over `GameState`).
  - Edge cost = 1 + penalties near ghost beliefs and inside pockets (H-M02/H-M04).
  - Optional hard constraint "never enter a cell the ghost reaches first" (H-S03).
- **Why it fits**: microseconds-to-milliseconds per query on 34×18 maps, and it is exact.
- **Status**: implemented (unweighted BFS with a race-safety constraint, own all-pairs BFS table) in `teams/greedy_v1.py`.
  - E-002 timing: max move 0.073 s, p95 0.002 s, startup ≤ 1.6 s, all under 10-way parallel load.
  - The risk-weighted cost version is not built yet.

### M-04: Belief-state estimation (HMM exact filtering / particle filter)
- **What**: implements H-S01, i.e. the forward algorithm over cells with the motion model, sonar likelihood, negative sight and food events. Exact filtering is cheap at this map size; particles are optional.
- **Evidence**:
  - Common [reported: AlanChaw, TianqiPeng, abhinavcreed13, loosh, lzheng1026].
  - Two cautions [reported: KTH dropped after adding it untested; abhinavcreed13 saw misjudgements on big maps].
- **Plan**: introduce it behind a switch, and A/B test it against food-diff-only tracking (H-S02).
- **Status**: set version (support only, no probabilities) implemented as the `tracker` switch in `teams/greedy_lab_v1.py` (E-007). The probabilistic HMM is not built.

### M-05: Local adversarial search (minimax / expectimax)
- **What**:
  - Depth-limited search with alpha-beta and iterative deepening.
  - Only the agents involved in a local fight (us + the nearest 1–2 opponents).
  - Our own lightweight state (positions, food bitsets), not `GameState`.
  - Leaf evaluation uses the map heuristics.
- **Use**: escapes and chases when an opponent is within about 6 cells.
- **Evidence**:
  - [reported: TianqiPeng used HMM + expectimax and was #1 seed (lost the semifinal to a more defensive agent)].
  - [reported: in the KTH report, an opponent's depth-4 minimax "walked into dead ends"]. A shallow search needs pocket-aware evaluation.
- **Status**: idea.

### M-06: MCTS with pruning
- **What**: UCT, or **ISMCTS** (information-set MCTS: sample opponent positions from the belief at each iteration) for the hidden opponents.
- **Pruning and speed ideas**:
  - Drop `Stop`.
  - Drop reversing unless forced.
  - Drop moves into pockets that fail the race test (H-S03).
  - Short horizon (10–20 plies) with a heuristic rollout policy and an evaluation at the leaf.
  - Reuse the tree between moves.
  - Hard time check.
- **Prerequisite**: a fast custom forward model. `GameState.generate_successor` is likely too slow for useful iteration counts within 1 s (to be measured).
- **Evidence**: weak as the *core* method [reported]:
  - infinityglow: MCTS "would also return an unreasonable action, some of them are fatal".
  - abhinavcreed13: MCTS alone 0 wins / 10 ties vs the baseline.
  - iknow1988: MCT ranked 33/37.
  - DXJ3X1 (finalist) used MCTS only to decide whether to enter single-entry food areas.
- **Verdict**: an experimental tactical module (e.g. for pocket-entry decisions), not the core.
- **Status**: idea.

### M-07: Approximate Q-learning (linear function approximation)
- **What**: CS188-style `Q(s,a) = Σ wᵢ·fᵢ(s,a)`, trained offline by self-play with reward shaping. Ship the weights as constants.
- **Evidence**: mixed [reported]:
  - loosh won its course tournament, but RL was mandated there.
  - iknow1988 reached 76% win rate, rank 17/147.
  - LuChenyang3842 found it "very limited due to the difficulty of defining rewards".
- **Verdict**: an alternative way to set the M-02 weights. Compare both on the same harness; keep the simpler one if they tie.
- **Status**: idea.

### M-08: Deep RL (DQN / PPO / MAPPO)
- **What**: a neural policy and value function trained by RL.
  - **MAPPO** (multi-agent PPO with a centralised critic; Yu et al. 2021, "The Surprising Effectiveness of PPO in Cooperative Multi-Agent Games") fits the structure: two cooperating agents, partial observability.
  - Under *centralised training, decentralised execution*, the critic may see the full state **during offline training only**. The deployed actor uses only its own observation, so this does not break R4.
- **Blockers**:
  1. **Runtime libraries are unknown (Q2).** Without numpy/torch the network would have to run in pure Python. A small MLP (a few thousand to tens of thousands of multiply-adds) is probably fine within 1 s, but that is an estimate, not measured.
  2. **Training needs a fast, faithful re-implementation of the rules.** The engine runs at ~1.3 s per game without its per-move sleep (E-009), about 1,000 agent moves per second, which is still far too slow for millions of RL steps. Any difference from the real rules is a "sim-to-real" risk, and a cheating risk if the simulator gives the policy information it won't have.
  3. **Generalising to random maps** needs map-agnostic inputs (egocentric crops, distance-based features).
  4. **Opponent diversity**: plain self-play overfits, so it needs a league / fictitious self-play.
  5. **Compute and time**: about 7 weeks, and GPU access is unknown.
- **Evidence**: no successful deep-RL entry found in the write-ups. [reported: the KTH DQN agent "was never trained enough"].
- **Verdict**: a stretch experiment only after M-01..M-04 give a strong baseline. A cheaper middle ground: RL / black-box tuning of the M-02 parameters.
- **Status**: idea.

### M-09: Classical planning (PDDL + Metric-FF)
- **What**: model goals as PDDL and call a planner. UoM encouraged this approach.
- **Problems**:
  - The planner binary belongs to RMIT's infrastructure; its availability on SNOW is unknown.
  - Calling a subprocess conflicts with R2.
  - A pure-Python planner would be too slow.
- **Evidence**: [reported: the abhinavcreed13 PDDL core had a 66.9% win rate, 73.4% with a Q-learning fallback; "susceptible to being cornered (dead-end)"].
- **Verdict**: not recommended.
- **Status**: idea, not recommended. It fails R2 as long as it needs a subprocess, and planner availability depends on Q2.

### M-10: Pursuit–evasion "race" analysis
- **What**: closed-form adversarial reasoning from distance tables ("who reaches cell c first, given turn order"). See H-S03. It replaces most of what deep minimax would compute in chases, at negligible cost.
- **Status**: implemented in its simple form as greedy's race-safe BFS (H-S03). The intercepting defender (E-007) uses the same "who arrives first" test.

### M-11: Evolutionary search
- **What**: a GA or NEAT (`neat-python`, offline only) over parameter vectors or behaviour-tree structure, with fitness from the batched harness. It is a sibling of M-02's optimisers.
- **Status**: idea.

### M-12: Imitation learning
- **What**: learn from demonstrations, e.g. replays of strong agents.
- **Blocker**: we have no strong agent to imitate; past UPF top teams' code is not public [reported].
- **Revisit**: maybe later, to distil our own slow search (M-05/M-06) into a fast policy.
- **Status**: idea, low priority.

### M-13: Expert iteration / distillation (fast policy learned from slow search)
- **What**:
  - Anthony, Tian & Barber, "Thinking Fast and Slow with Deep Learning and Tree Search", NeurIPS 2017 [source: <https://arxiv.org/abs/1705.08439>].
  - A slow "expert" (tree search) produces strong decisions, and a fast "apprentice" learns to imitate them. The apprentice then guides the search, which improves the expert.
- **For us**:
  - Run a slow offline expert: deep M-05/M-06 search with a large time budget.
  - Distil its choices into a model that runs in pure Python within the move budget: a decision tree, linear weights, or a tiny MLP exported as plain lists.
  - The distillation could also tune the M-02 feature weights.
- **Prerequisites**:
  - A strong slow expert, which we don't have yet.
  - A fast forward model.
  - Q2 (libraries) for anything bigger than a few thousand parameters.
- **Status**: idea, stretch goal.

### M-14: Potential field / influence map
- **What**: every cell gets a value from attractions (food, home in proportion to food carried, capsules when threatened) and repulsions (ghosts), each decaying with maze distance. The agent steps to the best neighbouring cell. It is a classic game-AI technique and a special case of M-02, where the features are field values summed over all objects.
- **Why it might fit**: it trades off several goals at once and drifts towards food clusters without explicit clustering (H-M05). It costs O(cells × objects) per move with the distance table.
- **Risks**: local maxima and dithering between two attractors, so it needs anti-oscillation (H-S10).
- **Evidence**: no capture-the-flag write-up found (research agent, 2026-10-17); [untested].
- **Status**: **tested** as the F2 `FieldAttacker` (`teams/families_v1.py`): +0.34 on 10 tuning seeds (E-008), but −0.04 [−0.20, +0.11] on 40 fresh tuning seeds, losing head-to-head to greedy (1.05) and against camper2 (−0.40) (E-010). Rejected for now.

---

## Proposed architecture (not yet decided; to be validated by experiments)

A layered hybrid, matching what the evidence favours. Each layer can be tested on its own:

1. **Startup** (`register_initial_state`, shared team object): map analysis H-M01–H-M11 and loading the tuned parameters.
2. **Perception**: food diffs (H-S02) → belief tracker (M-04 / H-S01).
3. **Strategy**: role assignment (H-S08) with score / time control (H-S05).
4. **Tactics**: goal selection per role with rules and utilities (M-01 + M-02), using the safe-food set (heuristics Part C). Race analysis (M-10) or a small local search (M-05) when an opponent is close.
5. **Motion**: risk-weighted A* (M-03).
6. **Safety**: a time guard (anytime design, `time.perf_counter()` checks against an internal budget well below 1 s), a legality check, and a safe fallback action. Never swallow the framework's timeout (T-05).
7. **Offline loop**: the batch harness, the opponent pool and parameter tuning (M-02 / M-07 / M-11), with every run logged in experiments.md.

## Proposed timeline (draft)

| Until | Goal |
|---|---|
| ~2026-10-26 | Batch benchmark harness + opponent pool v0; map analysis (H-M01, H-M02); rule-based attacker/defender (M-01 + M-03) that clearly beats the baseline |
| ~2026-11-09 | Food-diff tracking + beliefs (H-S02, M-04, A/B tested); roles (H-S08); chokepoint defence (H-M03); race analysis (M-10) |
| ~2026-11-20 | Parameter tuning (M-02); Linux / Python 3.8 timing check; freeze the test-run version |
| 2026-11-23 | Test run → analyse the logs and replays |
| 2026-12-03 | Fixes from the test run, opponent profiling (H-S11), optional stretch modules (M-05/M-06) only if A/B tests show gains |
