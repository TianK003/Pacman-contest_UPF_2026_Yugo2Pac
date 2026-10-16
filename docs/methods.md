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
| The engine is slow: ~40 s per game for cheap agents [verified E-000]; `generate_successor` copies the state on every call | Deep lookahead with `GameState` is expensive. Measure its cost before choosing a search depth (planned). Learning methods that need millions of steps would need our own fast simulator. |
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
| M-13 | "JEV" | ? | ? | ? | ? | **unclear, see below** |

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
  - Slow games, so parallelise; ~40 s per game means ~90 games per hour per process.
- **Status**: idea.

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
- **Status**: idea.

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
  2. **Training needs a fast, faithful re-implementation of the rules.** The engine runs at ~40 s per game. Any difference from the real rules is a "sim-to-real" risk, and a cheating risk if the simulator gives the policy information it won't have.
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
- **Status**: idea.

### M-11: Evolutionary search
- **What**: a GA or NEAT (`neat-python`, offline only) over parameter vectors or behaviour-tree structure, with fitness from the batched harness. It is a sibling of M-02's optimisers.
- **Status**: idea.

### M-12: Imitation learning
- **What**: learn from demonstrations, e.g. replays of strong agents.
- **Blocker**: we have no strong agent to imitate; past UPF top teams' code is not public [reported].
- **Revisit**: maybe later, to distil our own slow search (M-05/M-06) into a fast policy.
- **Status**: idea, low priority.

### M-13: "JEV": unclear, awaiting clarification
- I don't recognise "JEV" as the name of an established decision-making model, so I won't guess what it means. Two possibilities:
  - **JEPA** (Joint-Embedding Predictive Architecture; LeCun / Meta). A self-supervised representation / world-model approach.
    - Fit: poor. Our rules and map are fully known and can be simulated exactly, so a learned latent world model adds little.
    - It needs a deep-learning stack at runtime (Q2).
    - No use in this contest found.
  - **Joint expected value** of the two agents' *joint* actions: evaluate the up to 5 × 5 action pairs by expected value under the belief, then pick the best pair.
    - Fit: plausible and cheap. A coordination layer on top of M-01/M-05.
- **Status**: unclear. Replace this entry once the intended meaning is known.

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
