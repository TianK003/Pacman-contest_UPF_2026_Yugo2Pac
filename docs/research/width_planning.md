# Width-based planning for our CTF team (research report)

- **Date**: 2026-11-07. Written by a research agent from web sources plus one scratch benchmark. Nothing here has been tested in our game yet.
- **Scope**: IW(k), Rollout IW, p-IW, BFWS / k-BFWS, π-IW and learned guidance; Pacman evidence; libraries; designs for our agent; pitfalls.
- **Tags**:
  - `[source]`: in a paper or page I opened (link in the row or in section 2). "abstract only" means I read only the abstract.
  - `[reported]`: a student or blog claim.
  - `[verified]`: measured by me in a scratch script, on this laptop. The script is not in the repo.
  - `[untested]`: my own design idea or estimate.
- **Related docs**: methods M-05 / M-06 / M-13 (`docs/methods.md`), H-S03 race safety (`docs/heuristics.md`), T-56 timid attacker (`docs/traps.md`).
- **Draft code**: `teams/greedy_lab_v6.py` (untracked, being edited during this session) already contains a first IW(1) planner (`WidthPlanner`, switch `plan`). Section 8 reviews it.

---

## 0. Summary

1. **What it is**:
   - Width-based planners are breadth-first or best-first searches that keep a state only if it makes some feature ("atom") true for the first time.
   - IW(1) visits at most about |atoms| states, so its cost depends on the feature set, not on the size of the state space [source: W01].
   - The method works with a black-box simulator plus features, so it fits our own forward model [source: W02, W04, W05].
2. **Closest Pacman evidence**: Atari Ms. Pac-Man.
   - IW(1) over RAM scored 21,695 and UCT 22,336; blind breadth-first search scored 1,709 [source: W02].
   - At a 0.5 s budget, Rollout IW(1) scored 9,178, and **9,178 → 15,115 with a large death penalty** ("risk-averse"); the human reference is 15,693 [source: W05].
   - That emulator is a perfect, deterministic model of the ghosts. Ours will be an approximate model of adversaries we can only partly observe, so these numbers are an upper bound [untested].
3. **Capture the flag**: no public Berkeley or Melbourne CTF write-up uses IW, BFWS or novelty (section 3.3).
   - COMP90054 does teach IW [source: W18].
   - The top CTF write-ups we know of use rules, heuristic search and HMMs [reported: W19, W20; methods.md M-01].
4. **Cost in pure Python**: on a toy CTF model in Python 3.8, IW(1) runs at about 170k–260k generated nodes/s [verified, section 5.3].
   - (cell, carried-bucket) atoms: ~1k nodes, about 6 ms.
   - (cell, enemy-ghost cell) pair atoms: ~15–20k nodes, 100–300 ms.
   - A real model will be slower per node, so width 1 over cell-based atoms is affordable, but full width 2 is not [untested estimate].
5. **No evidence** shows width-based planning beating a tuned rule-based greedy agent in adversarial pursuit-evasion (section 9.2). The ceiling should be measured first: deaths with food, failed escapes, poor food order.

**Top 3 designs** (expected gain per effort, all `[untested]`):

| rank | design | key parameters | effort | main risk |
|---|---|---|---|---|
| 1 | **A. Contact lookahead: IW(1) / p-IW** (section 7.a), the lab6 `plan` switch plus the fixes in section 8 | atoms (cell, carried bucket) [± ghost-distance bucket]; width 1; horizon 30; budget 0.12 s; chase-within-6 ghost model; death penalty D ∈ {3, 6, 12}; γ 0.97; trigger: non-scared ghost ≤ 7 steps; 1-ply safety prepruning; death states do not update the novelty table | medium (mostly written) | optimism under a wrong ghost model; too timid if D is large (T-56) |
| 2 | **C. 1-BFWS raid sequencer** (section 7.c): pick the next food target, food order and the moment to bank | state (cell, eaten mask over ≤ 12 targets, t); static race-danger map from the ghosts and the belief quantile; f = ⟨w_{#g}, #g, h⟩ pruned at w > 1; replan every move | low–medium (no adversary simulation) | greedy's nearest-food choice may already be near-optimal |
| 3 | **B. Rollout IW(1) with greedy as base policy** (section 7.b) | first rollout = greedy's own path, then softmax rollouts (τ ≈ 1); depth-based novelty over (cell, carried bucket); rollout cap 40; budget 0.15 s; max-backup plus leaf value; overrides greedy only by a margin δ | medium–high | tuning cost; model fidelity |

---

## 1. Background (short)

### 1.1 Novelty and IW(k) [source: W01]
- **Novelty**: a newly generated state has novelty i if the smallest tuple of atoms that it makes true *for the first time in the search* has size i.
- **IW(i)**: a breadth-first search that prunes states with novelty > i.
- **Cost**: IW(1) keeps O(n) states and IW(i) keeps O(n^i), where n is the number of atoms.
- **Width**: if a problem has width w, IW(w) solves it optimally in time exponential in w.
- **IW**: calls IW(0), IW(1), ... until the problem is solved.
- **Benchmarks**: over 37,921 single-goal instances, 37.0% have effective width 1, 51.3% width 2 and 11.7% more than 2.
  - IW solves 34,627 of them.
  - Iterative deepening solves 9,010, breadth-first search 8,762, and greedy best-first with h_add 34,849.
- **SIW** (serialized IW): runs IW once per subgoal and achieves one more goal atom each time. It solved 819 of 1,150 IPC instances, against 789 for greedy best-first with h_add.
  - SIW is **incomplete when there are dead ends**, because it commits to intermediate states.
  - On VisitAll (visit every cell of a grid, the closest classical analogue to "eat all food"), SIW solved 19 of 20 instances and greedy best-first 3 [source: W01, Table 3].

### 1.2 IW with a simulator and rewards [source: W02, W04]
- **Atari atoms**: one atom per (RAM byte, value): 128 × 256 = 32,768 atoms.
  - Worst case for IW(1): n·D·b = 589,824 nodes.
  - IW(2) would need about 1.9·10^10 nodes, so only IW(1) was used.
- **Action choice**: keep the discounted reward along each kept path (γ = 0.995) and play the first action of the best path.
- **Child order** is randomised "to avoid being trapped into loops".
- **Budget**: 150,000 emulator frames per decision, with actions every 5 frames.
- **Tree reuse**: the subtree under the chosen action is kept. **Cached states are not pruned and do not update the novelty table.**
- **Result**: IW(1) beat UCT in 31 of 54 games [source: W02].
- **Lives**: the planners "do not care much about losing lives until there is just one life left", which motivated the later risk-averse variants [source: W02].
- **GVGAI** (stochastic games, 40 ms per decision) [source: W04]:
  - Atoms are at(cell, sprite-type) plus avatar(cell, orientation, type), e.g. at most 1,800 atoms for 100 cells and 10 sprite types.
  - IW(1) ignores stochasticity: it uses the first sampled outcome of each simulator call.
  - To temper that optimism, **"safety prepruning"** samples the 1-step successors of each root action M = 10 times and drops the actions with more deaths.

### 1.3 Rollout IW [source: W05]
- **Rollouts**: depth-first rollouts from the root replace breadth-first search, which gives better anytime behaviour.
- **Novelty table**: stores, per atom f, the smallest depth d[f] at which f was reached. A node is novel if it reaches some atom at a depth below d[f].
  - A rollout continues while it improves some d[f].
  - Otherwise the tip is labelled SOLVED, and a node is SOLVED when all its children are.
- **Guarantees**: the tree holds at most |F|² nodes. Rollout IW(1) reaches every width-1 goal in polynomial time.
  - Run to completion, it does *not* beat IW(1); its advantage is under short budgets.
- **Risk-averse (RA)**: negative rewards are multiplied by α = 50,000, and a death scores −10α.
- **Subscoring (RAS)**: one novelty table per log₂ bucket of the path reward.
  - The base form is IW_G(1): **one novelty table per number of goals achieved**.
  - This is the theoretical reason our (cell, food-eaten-count) and (cell, carried-bucket) atoms make sense.
- **Budgets**: 0.5 s and 32 s per decision, frameskip 15, results averaged over 5 runs on EC2 m4.16xlarge.

### 1.4 Reward-aware novelty: prioritized IW (p-IW) [source: W03]
Two changes to IW(i):
1. Ties in the breadth-first queue go to the state with the higher accumulated reward.
2. Each atom stores the best accumulated reward of any state that made it true. A new state is kept iff, for some atom, its reward **exceeds** the stored value; then the stored values are updated.

The authors frame this as an over-approximation of duplicate detection *with re-opening*. It eases IW's "single tunnel" problem: two states block each other's children, and plain IW picks between them arbitrarily. p-IW(1) "rather consistently" beat IW(1) over 53 games.

They also argue that choosing the root action is better treated as a bandit competition between the root actions than as optimising one action sequence.

### 1.5 BFWS and k-BFWS [source: W06, W07]
- **Novelty relative to heuristics**: w_{h1..hm}(s) compares s only with earlier states that have the same values h1..hm. This partitions the novelty tables.
- **BFWS(f5)**: f5 = ⟨w_{#g,#r}, #g⟩, compared lexicographically.
  - #g = number of unachieved goals.
  - #r = number of atoms of the last relaxed plan that have been made true. Relaxed plans are computed only when #g drops.
  - Novelty is computed only to 3 levels (1, 2, >2).
- **Novelty first works better**: ⟨w, h⟩ beat ⟨h, w⟩, because the heuristic-first order "is too greedy" on plateaus.
- **Results**: BFWS(f5) solved 192 problems against LAMA's 171. Pushing novelty in front of a landmark/FF heuristic raised coverage from 99 to 149 [source: W06].
- **k-BFWS**: prunes w > k, which makes the search polynomial but incomplete. It beat both BFWS(f5) and LAMA / FF over all IPC instances [source: W07].

### 1.6 Learned guidance
- **π-IW** [source: W08]:
  - Replaces the uniform rollout policy of Rollout IW with a softmax neural-network policy.
  - The target policy comes from the max-backup R_i = r_i + γ·max_j R_j at the root.
  - Features can come from the network's last hidden layer.
  - Matches Rollout IW on Atari with about 30× less planning budget.
  - The preliminary version is W09.
- **π-IW(1)+** (as described in W12):
  - Breaks ties between root actions in favour of the branch with **the most nodes**.
  - Adds a learned value: max{V̂, R}.
- **Hierarchical IW** [source: W10]:
  - Two levels: IW(1) over abstract features plus IW(1) over low-level features, which solves width-2 classical problems.
  - With a learned policy and value it beats flat IW on sparse-reward Atari games.
  - The high level uses count-based rollouts.
- **VAE-IW** [source: W11, abstract only]: boolean features learned by a VAE beat hand-crafted B-PROST with Rollout IW.
- **N-CPL** [source: W12]:
  - Learned policy and value. The value net scores non-terminal leaves, where earlier width-based methods used 0.
  - The "classic" novelty test is competitive with the depth-based one inside Rollout IW.
  - Strongest on games with large branching or sparse rewards.
- **Cost-to-go for stochastic shortest paths** [source: W13, abstract only]: estimating costs-to-go fixes width-based lookaheads there; they beat UCT and RTDP.
- **Olive** [source: W14, abstract only]: VAE features updated online beat Rollout IW 42–11 over 55 games.
- **Approximate novelty** [source: W15, abstract only]: random sampling plus Bloom filters cut the cost of novelty tests.

### 1.7 Novelty without pruning, in adversarial games [source: W17]
- Baier & Kaisers add **novelty as a bonus in MCTS selection**, mixed linearly with the value, rather than pruning on it.
- They test 4 novelty measures on six two-player board games and report gains in many settings.
- This is the only adversarial-game evidence I found for novelty. It is soft novelty, not IW-style pruning.

---

## 2. Sources

| ID | Title | Authors | Venue, year | URL | Read |
|---|---|---|---|---|---|
| W01 | Width and Serialization of Classical Planning Problems | N. Lipovetzky, H. Geffner | ECAI 2012 (FAIA 242: 540–545) | <https://nirlipo.github.io/publication/lipovetzky-2012-width/width-ecai-12.pdf> (read the mirror <https://gwern.net/doc/reinforcement-learning/model/2012-lipovetzky.pdf>) | full text |
| W02 | Classical Planning with Simulators: Results on the Atari Video Games | N. Lipovetzky, M. Ramírez, H. Geffner | IJCAI 2015: 1610–1616 | <https://www.ijcai.org/Abstract/15/230>; PDF <https://www-i6.informatik.rwth-aachen.de/~hector.geffner/www.dtic.upf.edu/~hgeffner/nir-ijcai-2015.pdf> | full text |
| W03 | Blind Search for Atari-Like Online Planning Revisited | A. Shleyfman, A. Tuisov, C. Domshlak | IJCAI 2016: 3251–3257 | <http://www.ijcai.org/Proceedings/16/Papers/460.pdf> | sections 1–3 and results text (tables garbled in extraction) |
| W04 | Width-Based Planning for General Video-Game Playing | T. Geffner, H. Geffner | AIIDE 2015: 23–29 | <https://ojs.aaai.org/index.php/AIIDE/article/view/12786> | full text |
| W05 | Planning with Pixels in (Almost) Real Time | W. Bandres, B. Bonet, H. Geffner | AAAI 2018 | <https://arxiv.org/abs/1801.03354>; code <https://github.com/bonetblai/rollout-iw> (C++, BSD-3) | full text |
| W06 | Best-First Width Search: Exploration and Exploitation in Classical Planning | N. Lipovetzky, H. Geffner | AAAI 2017: 3590–3596 | <https://nirlipo.github.io/publication/lipovetzky-2017-best/bfws-aaai-17.pdf> | method and results |
| W07 | A Polynomial Planning Algorithm that Beats LAMA and FF | N. Lipovetzky, H. Geffner | ICAPS 2017: 195–199 | <https://nirlipo.github.io/publication/lipovetzky-2017-polynomial/poly-bfws-icaps-17.pdf> | abstract, intro, variants |
| W08 | Deep Policies for Width-Based Planning in Pixel Domains (π-IW) | M. Junyent, A. Jonsson, V. Gómez | ICAPS 2019: 646–654 | <https://arxiv.org/abs/1904.07091>; code <https://github.com/aig-upf/pi-IW> (Python, no licence detected) | algorithm and results text |
| W09 | Improving Width-Based Planning with Compact Policies | M. Junyent, A. Jonsson, V. Gómez | arXiv 2018 | <https://arxiv.org/abs/1806.05898> | abstract only |
| W10 | Hierarchical Width-Based Planning and Learning | M. Junyent, V. Gómez, A. Jonsson | ICAPS 2021: 519–527 | <https://arxiv.org/abs/2101.06177> | abstract and parts |
| W11 | Planning from Pixels in Atari with Learned Symbolic Representations | A. Dittadi, F. K. Drachmann, T. Bolander | AAAI 2021 | <https://arxiv.org/abs/2012.09126> | abstract only |
| W12 | Width-based Lookaheads with Learnt Base Policies and Heuristics Over the Atari-2600 Benchmark | S. O'Toole, N. Lipovetzky, M. Ramirez, A. Pearce | NeurIPS 2021 | <https://arxiv.org/abs/2106.12151> | sections 1–4 |
| W13 | Width-Based Lookaheads Augmented with Base Policies for Stochastic Shortest Paths | S. O'Toole, M. Ramirez, N. Lipovetzky, A. Pearce | ICAPS HSDIP workshop 2019 | <https://nirlipo.github.io/publication/o-2019-width> | abstract only |
| W14 | Is Policy Learning Overrated?: Width-Based Planning and Active Learning for Atari | B. Ayton, M. Asai | ICAPS 2022 (per arXiv page) | <https://arxiv.org/abs/2109.15310> | abstract only |
| W15 | Approximate Novelty Search | A. Singh, N. Lipovetzky, M. Ramirez, J. Segovia-Aguas | ICAPS 2021 | <https://arxiv.org/abs/2105.07691> | abstract only |
| W16 | Planning for Novelty: Width-Based Algorithms for Common Problems in Control, Planning and RL | N. Lipovetzky | IJCAI 2021 (early-career spotlight) | <https://www.ijcai.org/proceedings/2021/0702.pdf> | skimmed |
| W17 | Novelty in Monte Carlo Tree Search | H. Baier, M. Kaisers | IEEE Trans. on Games 17(4), 2025 | <https://ir.cwi.nl/pub/35890/35890.pdf> | abstract, intro, conclusion |
| W18 | COMP90054 "Search Algorithms" slides (IW, novelty, SIW) | course site | n/a | <https://comp90054.github.io/reinforcement-learning/slides/search.html> | page |
| W19 | AlanChaw/comp90054-pacman (2nd place, Sem 2 2019) | student team | GitHub | <https://github.com/AlanChaw/comp90054-pacman> | README |
| W20 | abhinavcreed13/ai-capture-the-flag-pacman-contest | student team | GitHub | <https://github.com/abhinavcreed13/ai-capture-the-flag-pacman-contest> | README |
| W21 | LAPKT | LAPKT-dev | GitHub / PyPI / docs | <https://github.com/LAPKT-dev/LAPKT-public>, <https://pypi.org/project/lapkt/>, <https://lapkt-dev.github.io/docs/modules> | README, docs, PyPI JSON |

Index of further pointers I did not open: <https://nirlipo.github.io/project/width-based-planning>. It lists MA-BFWS (cooperative multi-agent planning, Gerevini et al., ICAPS 2019) and continuous-state width planning (Teichteil-Königsbuch et al., IJCAI 2020).

---

## 3. Pacman evidence

### 3.1 Atari Ms. Pac-Man (deterministic emulator, perfect model)

| planner | budget | score | source |
|---|---|---|---|
| Human reference | n/a | 15,693 | W05 Table 2 |
| BrFS (blind breadth-first) | 150k frames | 1,709 | W02 Table 1 |
| UCT | 150k frames | 22,336 | W02 |
| IW(1), RAM atoms | 150k frames | 21,695 | W02, W05 |
| 2BFS (novelty queue + reward queue) | 150k frames | 18,927 | W02 |
| IW(1), screen features | 0.5 s / 32 s | 2,578 / 20,622.8 | W05 Table 2 |
| Rollout IW(1) | 0.5 s / 32 s | 9,178.4 / 19,667.0 | W05 |
| RA Rollout IW(1) (death ≫ any reward) | 0.5 s / 32 s | **15,115.0** / 23,033.0 | W05 |
| RAS Rollout IW(1) | 0.5 s / 32 s | 13,746.8 / 21,833.0 | W05 |
| DQN | learned | 2,311 | W05 Table 1 |

Takeaways for us:
- **Rollouts beat breadth-first search under a short budget**: 9.2k vs 2.6k at 0.5 s [source: W05].
- **A big death penalty matters in a ghost-chase game**: 9.2k → 15.1k at 0.5 s [source: W05].
- The simulator in these results is exact. Ours will not be [untested].

### 3.2 GVGAI: stochastic games, with a myopic baseline [source: W04]

| game set (250 games each) | MCTS | OLMCTS | IW(1) | 1-step lookahead | random |
|---|---|---|---|---|---|
| Set 1, 40 ms | 89 | 93 | 145 | 67 (flat over time) | 20 |
| Set 1, 1 s | 108 | 108 | 191 | | |
| Set 2, 40 ms / 1 s | 68 / 77 | 70 / 90 | 104 / 183 | 62 | 28 |
| Set 3 (puzzles), 1 s | 59 | 60 | ≤ 45 | | |

- **Puzzles need more width**: on set 3, IW(2) reached 81 wins at 1 s.
- **IW(3/2)** reached **100**. It keeps only the atom pairs that contain an avatar atom, which is the template for our "pairs that include our own cell" [source: W04].
- **Caveat**: these games are not two-team adversarial; the NPCs are scripted.

### 3.3 Berkeley / Melbourne capture the flag
- **Searches run** (Google-style web search, 2026-11-07): "COMP90054 pacman capture the flag novelty / BFWS / iterated width github", "pacman iterated width / width-based capture the flag", "COMP90054 width novelty IW pacman", "github pacman BFWS / best-first width search", "pacman contest myTeam.py novelty IW", plus an extended search.
- **Result**: **no CTF write-up, repository or report that uses IW, BFWS or novelty**. Absence of evidence: student repositories are often private or unindexed.
- **The course teaches IW**: COMP90054's search slides cover novelty, IW(k), its O(n^k) bound and SIW [source: W18]. The course was taught by Lipovetzky, author of W01, W02, W06 and W07 [reported: brief; search-result listing].
- **Technique rule**: at least 2 techniques from a list (heuristic search, classical planning / PDDL, value or policy iteration, MCTS / UCT, RL, goal recognition, game theory) [reported: W20 README].
- **Strong teams used other methods**:
  - The Sem 2 2019 runner-up used heuristic search, a rule-based decision tree, HMM tracking, maze-distance clustering, dead-end detection and "some minimax" [reported: W19].
  - Earlier notes: search-only agents (MCTS) fared poorly in CTF write-ups [reported: methods.md M-06].

---

## 4. Libraries and code (research pointers only; we write our own code)

| question | answer |
|---|---|
| pip package? | `lapkt` on PyPI; latest 0.2.1 uploaded 2026-08-02; `requires_python >= 3.7` [verified: PyPI JSON API, 2026-11-07] |
| Windows + Python 3.8? | **only up to lapkt 0.1.8** (2022-10-12, `cp38 win_amd64` wheel). 0.2.0 and 0.2.1 ship cp38 only for manylinux; the Windows wheels are cp39 and up [verified: PyPI file list]. The README says Windows supports 3.9–3.12 [source: W21] |
| What it runs | PDDL via the FF or FD parsers into STRIPS. Planners: IW, IW+, SIW, SIW+, DFS+, BFS(f), anytime variants, approximate-novelty BFWS. An "agnostic" C++ interface builds STRIPS tasks in code [source: W21 docs] |
| Custom simulator / black box? | **not documented**. The Atari IW code (ALE-Atari-Width, C++, GPL-2) was *adapted* from LAPKT rather than plugged into it [source: repo description] |
| Licence | PyPI says MIT; docs say Apache-2.0 (inconsistent) [verified / source] |
| Usable at runtime? | **No.** A compiled C++ extension, not stdlib (R5), and it would need the professor to install it (Q2) |
| Usable offline? | Only for PDDL abstractions of our game. Our model is a simulator, not PDDL, so the gain is small [untested]. Not recommended |
| Code to learn from | `bonetblai/rollout-iw` (C++, BSD-3): reference Rollout IW. `aig-upf/pi-IW` (Python + TF, **no licence detected by GitHub**, so it cannot be copied anyway): Rollout IW / π-IW in Python. `nirlipo/BFWS-public` (C++, GPL-3). `miquelramirez/ALE-Atari-Width` (C++, GPL-2) [verified: GitHub API metadata]. Rule R7: read for ideas, never copy |

---

## 5. What transfers to our game

### 5.1 Atari vs our game

| aspect | Atari / GVGAI (where IW was tested) | our CTF | consequence |
|---|---|---|---|
| Model | exact emulator (Atari) or the game's own simulator (GVGAI) | our own approximate model: our moves exact; enemy moves guessed | the planner is only as good as the enemy model [untested] |
| Observability | full (RAM) or full screen | enemies hidden beyond Manhattan 5; belief available | hidden enemies must be determinized or sampled |
| Adversary | scripted NPCs | adaptive teams, unknown policies | GVGAI-style risky optimism is likely; prepruning and robust aggregation are needed |
| Branching | 18 (Atari) / 5 (GVGAI) | ≤ 5 per agent | small; good for IW |
| Atoms | 32k (RAM), millions (pixels) | ~313 cells × small extras | tiny; IW(1) is very cheap |
| Rewards | dense or sparse game score | food only counts when banked; death = lose carried food + long respawn | needs shaping, a leaf value and risk aversion |

### 5.2 Width-1 with cell atoms adds little, but augmented atoms change that [untested analysis]
- **Cell atoms only**:
  - IW(1) with atom = our cell keeps the first *surviving* path to each cell.
  - With a deterministic chase model this is close to the race-safe BFS greedy already uses (H-S03).
  - So plain cell atoms are expected to add little.
- **(cell, carried bucket)** or **(cell, eaten count)**:
  - Paths that reach the same cell with more food stay alive. The search then enumerates "eat a detour and still get home" options that greedy's nearest-food rule does not compare.
  - This is the IW_G / subscoring idea of W05: one novelty table per goal count or score bucket.
- **What can never be novel**:
  - With (cell, carried) atoms, **waiting is never novel**: Stop, or stepping back and forth, gives the same cell with the same carried food.
  - Waiting plans exist only if atoms include time or the enemy's relative position, e.g. a ghost-distance bucket, or p-IW reward-aware novelty.

### 5.3 Cost [verified: scratch benchmark, not in repo]
- **Toy model**:
  - Red attacker vs 2 enemy ghosts that chase whenever the attacker is a Pacman.
  - Food as an int bitmask. No capsules, no leaf value. Depth cap 40.
  - Python 3.8.10 (repo venv) on this laptop, unloaded.
  - 6 maps (RANDOM 1, 2, 3, 5, 8, 13) × 5 random start positions.

| atoms | generated nodes / run | ms / run, median (max) | gen nodes / s |
|---|---|---|---|
| cell | 653 | 2.8 (4.1) | 264k |
| (cell, carried bucket of 4) | 1,066 | 5.6 (8.2) | 218k |
| (cell, eaten count) | 3,025 | 17.6 (39.9) | 181k |
| (cell, carried) + (cell, ghost-1 cell) | 15,194 | 95 (189) | 177k |
| pairs (cell, g1) and (cell, g2) (IW(3/2)-like) | 20,668 | 112 (301) | 170k |

- **Map facts** [verified, seeds 1–40]: 313 open cells on average (296–334), 157 on each half, 108 cells with 3+ open neighbours, 20 dead-end cells.
- **Estimate** [untested]: a full model (capsules, scared timers, leaf value, list copies) will be 2–5× slower per node, and the tournament machine possibly slower again.
  - Budget for 10k–40k generated nodes per 0.12–0.2 s on the cluster.
  - Width 1 over (cell, small extra) atoms fits.
  - Pair atoms with an enemy cell fit only as anytime search (cut by the clock).
  - Full IW(2) over ~2.5k atoms (~3M pairs) does not fit.

### 5.4 Where greedy is myopic (the targets) [untested; ceiling unmeasured]
1. **Escapes while carrying**: greedy's retreat follows race-safety but does not compare escape routes that also eat food, or that lead through a capsule.
2. **Food order inside a pocket or cluster**: nearest-first plus return at 8 (or `open_goal`) can strand the agent deep in a pocket.
3. **Capsule timing**: the capsule is taken only by the standoff breaker or by chance.
4. **Waiting at a pocket mouth** for a ghost to leave: impossible for cell-only planners (section 5.2).

**First step before building more**: run `eval/replay_probe.py replay` on the incumbent against the **reference pool only** (never the held-out teams, T-53). Count deaths carrying ≥ 3, deaths in dead ends, and food stranded at game end. This bounds the possible gain.

---

## 6. Common forward model (shared by designs A, B, C and D) [untested]

### 6.1 State (per planner call, built from our observation only)

| field | content | note |
|---|---|---|
| `me` | our cell index | exact |
| `carried` | our `num_carrying` | exact |
| `food` | int bitmask over enemy-side food (≤ 30 bits) | exact (food is fully visible) |
| `caps` | bitmask over enemy capsules | exact |
| `g[k]`, `sc[k]` | each modelled enemy ghost's cell, and its scared moves left (minus a margin) | visible: exact. Hidden: belief cell (section 6.3). `scared_timer` is a hidden field behind the `flags` switch (Q3) |
| `t` | plies used; `steps_left` = own moves left | terminal at `timeleft // 4` |
| (optional) `mate` | teammate cell following its committed path from shared memory | cheap; we control it |

Static data, built once per game: cell index, neighbour lists, an all-pairs distance table (greedy already has one), distance to home, dead-end depth and entrance (`MapInfo`). Never touch the engine's objects (T-01); work on copies or on index arrays.

### 6.2 Actions and turn order
- **Our actions**: moves to neighbouring cells, **plus Stop as an option** (only useful with time or ghost-relative atoms; section 5.2).
- **One planning ply**: our move, then each modelled enemy ghost moves once. The real order is 0, 1, 2, 3 cyclic; between the two enemy moves our teammate moves, which is ignored or scripted.
- **Collisions**, as in the engine:
  - We step onto a non-scared ghost on its side: death.
  - A ghost steps onto us: death.
  - A scared ghost on our cell: it is eaten and leaves the model (it respawns far away).

### 6.3 Enemy models (pick per design; aggregate for robustness)

| model | rule | use |
|---|---|---|
| M1 chase-in-range | non-scared ghost within r (6) of us: step that minimises maze distance to us, staying on its side; else stay | lab6 default; cheap |
| M2 intercept | ghost walks to the home-border cell on our shortest way home | catches the "cut-off" defenders (our own `intercept` idea mirrored) |
| M3 flee | scared ghost: step that maximises distance to us | while capsule time is left |
| M4 sight-limited | a hidden ghost chases only once within Manhattan 5 of us (it sees what we see), else follows M1's "stay" or walks toward its belief of us | principled symmetric sight |
| M5 belief samples | K = 3 determinizations of each hidden ghost: most-likely cell + 2 cells sampled from the belief (farthest-point among cells with mass ≥ 0.05) | robustness to belief error (median 2 steps with shared sonar) |
| M6 reach-set (worst case) | hidden ghost occupies every cell within t of its belief support at ply t | **pessimistic**; caused timidity before (T-56, `lab_tracker` rejected) |

- **Root aggregation**: Q(a) = min over {M1, M2} for visible ghosts, and min or 20th percentile over the M5 samples for hidden ones. Cost: one search per determinization, ×2–3.
- **Safety prepruning** (GVGAI style [source: W04], adapted [untested]): before searching, drop root actions whose next cell is within 1 step of a visible non-scared ghost on its side, unless every action is like that.

### 6.4 Rewards, terminals, leaf value

| item | value | rationale |
|---|---|---|
| eat food | +a (a = 0.5) | potential-style split of the food's value (lab6 default) |
| bank k food | +(1 − a)·k | total of 1 per banked food |
| death | −(a·carried + D), terminal | D in food units: respawn plus the prison walk is ~15–45+ steps (framework.md). **D ∈ {3, 6, 12}** to tune; RA (W05) argues for large, T-56 for not too large |
| capsule | +0.3 | lab6 default |
| eat a scared ghost | +1 | lab6 default |
| time out | carried food is worth 0 if `dist_home > steps_left` | the game ends; unbanked food is lost |
| discount γ | 0.97 per ply | earlier banking preferred (W02 used 0.995 per 5 frames) |
| leaf value V(s) | carried·(1 − a)·γ^{dist_home} if home is reachable in time, else −a·carried; small −0.02·(distance to nearest food) while carrying < 3 | cost-to-go at leaves helps width-based lookaheads [source: W12, W13] |

### 6.5 Root decision
- **Value of a root action**: best (discounted reward + γ^d·V) over the nodes of its subtree, as in W02 and W05.
- **Ties**: prefer the larger subtree (more options, a mobility proxy: π-IW(1)+ [source: W12]), then greedy's action.
- **Override margin**: play the planner's action only if Q(best) − Q(greedy's action) ≥ δ (`plan_min`-like). This gives hysteresis against oscillation (H-S10).
- **Never worse than greedy in the model**: add greedy's own planned path as a **cached branch**, which is not pruned and does not update novelty, as W02 does with reused subtrees. The best node is then never below greedy's path *in the model* [untested].

### 6.6 Anytime and timing (R1, R2)
- **Clock checks**: `time.perf_counter()` every 16–64 generated nodes. Planner budget 0.12–0.2 s, below the team's internal budget.
- **On timeout**: return the best root action found so far, or greedy's action if fewer than 2 root actions were evaluated.
- **No threads**, and never catch `TimeoutFunctionException`.
- **Tie randomisation** with a per-game `random.Random(seed)` instance, never the global `random` (rules).
- **No printing.**

### 6.7 Integration contract: the planner proposes, the rules dispose
- **Rules keep control** of mode choice and of special cases: endgame, `food_to_win`, the time margin, the standoff breaker's entry, and defender duties.
- **Trigger**: the planner runs only in its trigger situation (per design) and returns `(action, info)`.
- **Validation**: the action must be in `get_legal_actions`; otherwise greedy decides.
- **Tracing**: record `info` (expanded nodes, time, best value, chosen vs greedy action) for `eval/trace_game.py`, so every planner move is attributable (E-022).

---

## 7. Designs

State, actions, enemy models, rewards, root decision and timing follow section 6 unless a row says otherwise.

### 7.a IW(1) / p-IW contact lookahead for the attacker (rank 1) [untested]

| item | choice |
|---|---|
| Purpose | escapes while carrying, "one more food then home" choices, capsule use under threat |
| Trigger | attacker on the enemy side (or ≤ 2 steps from the border) **and** a modelled non-scared ghost ≤ 7 maze steps away (lab6 `plan='danger'`, `plan_trigger=7`). Variant: also when carrying ≥ 1 and a ghost ≤ 10 |
| Search | breadth-first IW(1) (lab6 `plan_search='iw'`). Variant: **p-IW** (each atom stores its best accumulated value; a node is novel iff it beats the stored value for some atom; queue ties by value) [source: W03] |
| Atoms | baseline `(cell, carried bucket)` with log-like buckets 0,1,2,3,4,4,5,5,5,6… (≈ RAS subscoring [source: W05]); variant `(cell, carried bucket, ghost-distance bucket {≤2, 3–5, ≥6})` (lab6 `pos_carry_g`); variant `(cell, food-eaten count)` = IW_G(1) |
| Width | 1 (plus IW(3/2)-style pairs with our cell only if the budget allows) |
| Horizon | 30 own moves (`plan_h=30`), capped by `steps_left` |
| Enemy model | M1 + M3 for visible ghosts; hidden ghosts at their belief's most likely cell (`plan_hidden`). Robust variant: min over M1/M2 and over the M5 samples |
| Death handling | terminal, −(a·carried + D). **Death nodes do not update the novelty table**, so a later safe arrival at the same (cell, carried) is not pruned (section 8, S1) |
| Value / goal | Atari-style accumulated discounted reward + leaf value (section 6.4); root decision as in section 6.5 |
| Cost | (cell, carried): ~1k nodes, ~6 ms in the toy model; expected well under 0.12 s in the real model. With the ghost bucket: up to 3× the atoms |
| Anytime | breadth-first; a partial search is still valid, but deep options are missing when the clock cuts. If budget cuts are frequent (`timed_out` in `info`), switch to the rollout version (7.b) |
| Expected effect | fewer deaths carrying food, more food per raid. **Watch** for timidity (food returned per game falls) and for model-optimism deaths (deaths in contact rise) |

### 7.b Rollout IW(1) with greedy as the base policy (rank 3) [untested]

| item | choice |
|---|---|
| Purpose | policy improvement over greedy for every attacker move on the enemy side, with better anytime behaviour than breadth-first IW (W05) |
| Rollouts | from the root, follow the base policy among unsolved children until a node is not novel, a terminal (death or bank-and-game-end), or depth H = 40 |
| Base policy | **rollout 1 = greedy's deterministic choice at every step**. Later rollouts: softmax over hand scores s(a) = −w₁·d(next, target food) − w₂·danger(next) + w₃·[a = greedy's action] − w₄·[a reverses], temperature τ ≈ 1; equivalently ε-greedy with ε ≈ 0.3 |
| Learned option (offline only) | fit softmax weights to logged (state features, greedy or planner action) pairs, π-IW-style; ship constants (data files allowed, Q6). Features must come from the observation only |
| Novelty | depth-based table d[f] over (cell, carried bucket) (W05); try "classic" too (W12: competitive) |
| SOLVED labels | as in W05: terminal / non-novel tips are SOLVED; a parent is SOLVED when all its children are; stop when the root is SOLVED or the clock runs out |
| Backup / choice | R_n = r_n + γ·max_child R, leaves scored with V(s) (section 6.4) [source: W08, W12]; root decision as in section 6.5 with override margin δ |
| Tree reuse | keep the subtree of the played action only if the observed state equals the predicted one (our cell, carried, visible ghost cells); cached nodes do not update novelty [source: W02, W08]; otherwise rebuild |
| Budget | 0.15 s; rollouts are cheap (one child per step) |
| Enemy model | as 7.a; with M5 samples, rotate the determinization per rollout and keep the per-root-action minimum |
| Effort | medium–high: shares the model with 7.a, but adds rollout logic, SOLVED propagation, reuse and policy weights |

### 7.c 1-BFWS raid sequencer for food order (rank 2) [untested]

| item | choice |
|---|---|
| Purpose | choose *which* food next and *in what order*, and when to bank, inside a raid; replaces greedy's "nearest race-safe food" target only |
| Model | **no enemy simulation**. A static danger map τ(c) = min over modelled ghosts of their maze distance to c (hidden ghosts: belief 20% quantile, `belief_quantile`). Entering c at time t is allowed iff t + m < τ(c), margin m = 1 (greedy's race rule extended along the path) |
| State | (cell, eaten mask over T, t); T = up to 12 nearest race-safe foods (+ capsules optionally) |
| Goal | eat k = min(\|T\|, return target − carried) foods, then reach home; #g = (k − eaten) + [not home] |
| Evaluation | f = ⟨w_{#g}, #g, h⟩ (BFWS(f5) with #r dropped), or ⟨w_{#g,#r}, #g, h⟩ where #r = cells of the current nearest-neighbour tour through the remaining targets already visited (a cheap analogue of the relaxed plan) [source: W06 for f5] |
| Pruning | k = 1: drop nodes with w > 1 (polynomial; W07). Atom = cell, novelty tables partitioned by (#g [, #r]) |
| h | distance to the nearest remaining target + that target's distance home (or `dist_home` when only the home goal is left) |
| Output | the first target of the best plan (max eaten / steps, minus a time cost); greedy's motion layer walks there with its usual race-safety; replan every move |
| Death / termination | no deaths in this model: unsafe cells are forbidden (race test). A node is terminal at the goal, or when `t + dist_home > steps_left` |
| Anytime | best-first with a small budget (0.02–0.05 s); on timeout take the best goal node found, else greedy's usual target |
| Cost | nodes ≤ cells × (#g values) × (#r values); in practice a few thousand. The node step is just a table lookup, so expect 5–10× cheaper per node than 7.a |
| Evidence | SIW / BFWS do well on VisitAll-like coverage (W01, W06). No game evidence |
| Effort | low–medium; it can be screened on its own as a target-selection switch |

### 7.d Team and defender versions (low priority) [untested]

| variant | sketch | assessment |
|---|---|---|
| d1. Interception planner (defender) | state (defender cell, invader cell, invader carried); invader model = goes home (minimise `dist_enemy_side`) unless that brings it within 1 of us, else maximise distance; switches to "nearest food" below its estimated return threshold (`enemy_return_at`). Atoms = pairs (our cell, invader cell) only (IW(3/2)-style, ≤ 157² ≈ 25k). Goal: capture (+1 + carried) or seal (the invader cannot reach home before us) | affordable (~0.1 s in the toy). But our defender gains came from **deterrence** (shadow, E-019), and chase-style additions were rejected (`hunt` in E-019 and E-025, `guard` in E-025). Expected gain small |
| d2. Pincer (two defenders vs one invader) | joint actions 5 × 5 = 25 per ply; atoms (a1, inv), (a2, inv); only when both are ≤ 8 from the invader | rare situation; SM-8 in proposals.md. No literature on adversarial IW |
| d3. Joint double raid | team-brain IW over both attackers' (cell, carried) atoms, joint actions | 12× the cost of 7.a. Only if a double-attack mode is adopted |

Multi-agent width-based planning exists only for *cooperative* planning (MA-BFWS, Gerevini et al. 2019; pointer, not opened). I found no adversarial pursuit-evasion work with IW.

### 7.e Weird but plausible [untested]

| ID | idea | why it might work | risk |
|---|---|---|---|
| e1 | **Junction-graph macro-IW** (hierarchical, in the spirit of W10): compress the maze into junctions (~108 per map) and corridors; a macro-action walks a corridor (cost = its length, safety from the race test); IW(1) over (junction, carried bucket) | the horizon grows from ~30 to ~100+ steps for the same node count; good for picking which pocket to raid | ghost interactions mid-corridor are approximated |
| e2 | **Novelty over tactical features**, not cells: atoms = (dist_home bucket, nearest-ghost-distance bucket, carried bucket, eaten-count bucket); a few hundred atoms | finds *qualitatively different* futures cheaply ("dynamic features" spirit, W08); use it as an option generator compared against greedy | too abstract; may miss the exact path |
| e3 | **Scouting as VisitAll**: when idle, plan the defender's patrol path to maximise belief mass seen (sight = Manhattan 5); atoms = "belief cell observed" | coverage is width 1 in classical planning (VisitAll, W01) | the shadow defender already works by deterrence; small gain |
| e4 | **Novelty-diverse determinizations**: choose hidden-ghost samples by farthest-point in maze distance among belief cells with mass ≥ ε, then plan per sample and aggregate by min | covers distinct threats with few samples | ×K cost; may revive timidity |
| e5 | **Offline privileged teacher → distillation** (M-13): offline Rollout IW with a large budget *and the true state* labels decisions; fit a linear softmax or decision tree on observation-only features; ship constants | turns slow planning into a fast policy; the runtime uses only the observation | the teacher may differ from what is achievable without privileged information; grey-zone check needed (offline full state is allowed for training per M-08's CTDE note, but confirm) |
| e6 | **Soft novelty instead of pruning** inside an expectimax or MCTS attacker (count-based bonus, W10 / W17) | pruning discards states only because of features, which is risky with adversaries; a bonus keeps them reachable | it is no longer IW; more tuning |

---

## 8. Review of the lab6 draft planner (`teams/greedy_lab_v6.py`, read 2026-11-07, file untracked and still changing)

**What it is**: breadth-first IW(1), or best-first by value with novelty pruning (`plan_search='best'`, close in spirit to k-BFWS with value as the tie-breaker). It uses atoms `pos` / `pos_carry` / `pos_food` / `pos_carry_g`, ghost models M1 + M3, hidden ghosts at the belief argmax, and the potential-style rewards and leaf value of section 6.4. The root action of the best-valued node is played. This matches design 7.a.

| ID | observation | suggestion | tag |
|---|---|---|---|
| S1 | a successor that **dies** still adds its atom to `seen` (the atom is added before the `dead` check), so a later, safe arrival at the same (cell, carried bucket) is pruned | add atoms only for surviving successors (death nodes can still be recorded as candidates for `best_v`) | [untested] |
| S2 | the moves come from `nbr[c]` only, so **Stop is never generated**; with `pos` / `pos_carry` atoms waiting could never be novel anyway | add Stop at least under `pos_carry_g`, or with time-bucket atoms | [untested] |
| S3 | children are expanded in fixed `nbr` order, so ties are broken systematically | randomise the child order with a per-game `random.Random` (W02 did this against loops), or break ties by subtree size (W12) | [source: W02, W12] |
| S4 | `plan_death=3` is mild compared with RA (W05: death ≫ any reward, which gave 9.2k → 15.1k in Ms. Pac-Man) | screen D ∈ {3, 6, 12}; track deaths per game *and* food returned per game (timidity, T-56) | [source W05 / untested] |
| S5 | there is no 1-ply safety prepruning and only one ghost model | add GVGAI-style prepruning (section 6.3) and optionally min over M1/M2 | [source W04 / untested] |
| S6 | the planner can pick an action whose model value is below greedy's path | inject greedy's path as a cached, non-pruned branch, or compare against greedy's action value with margin δ (section 6.5) | [untested] |
| S7 | the novelty table resets every move (fine); there is no subtree reuse | keep as is for IW. Reuse matters only for Rollout IW (7.b) | [source: W02, W05] |
| S8 | `plan_search='best'` pops by value only; BFWS found novelty-first beats heuristic-first on plateaus (⟨w,h⟩ > ⟨h,w⟩) | with k = 1 pruning every kept node has w = 1, so this is effectively 1-BFWS with value as #g. Fine, but partition novelty by a goal count (eaten count) as BFWS does with w_{#g} | [source: W06, W07] |

---

## 9. Pitfalls and expected value

### 9.1 Known failure modes

| # | failure mode | evidence | mitigation |
|---|---|---|---|
| P1 | **Risky optimism** with a stochastic or adversarial world: IW trusts one sampled outcome | GVGAI motivated safety prepruning for this [source: W04] | prepruning; min over enemy models; risk-averse aggregation |
| P2 | **Novelty pruning discards the only good path** ("single tunnel"; a later arrival at the same atom is pruned even when the ghost has left) | W03 | p-IW reward-aware novelty; time or ghost-relative atoms; S1 |
| P3 | **Sparse or delayed reward beyond the horizon** (food counts only when banked) | leaf values improve width lookaheads [source: W12, W13] | leaf value V(s); potential-style split of the food reward |
| P4 | **Deaths underweighted** | planners ignore lost lives until the last one [source: W02]; RA fix [source: W05] | death penalty D; but large D → timid (our T-56) |
| P5 | **Dead ends / pockets** when the ghost model says "stay" | SIW incomplete with dead ends [source: W01]; our E-018 exit-race rule halved deaths but gained no points | pocket-aware leaf value; pessimistic model (M6) only inside pockets |
| P6 | **Width blow-up**: IW(2) over ~2.5k atoms is millions of pairs | W02 (Atari IW(2) infeasible) | IW(3/2)-style pairs that include our cell only (W04); hierarchy (e1) |
| P7 | **Fixed child order** gives loops or bias | W02 | randomise with an RNG instance |
| P8 | **Model mismatch with real opponents**; gains on the pool may not transfer (greedy_v2 had a 32% gap to the held-out teams, agents.md) | our E-015 | fit the ghost model to observed pool behaviour (offline); check against the held-out teams only at the release gate |
| P9 | **Python speed / timeouts** | section 5.3 | clock every 16–64 nodes; budget ≤ 0.2 s; Linux timing check (E-016) |
| P10 | **Oscillation** between planner and rules | H-S10 | override margin δ; commit to the planner while the trigger holds |
| P11 | **Stale cached subtrees** | W08 notes outdated cached nodes | reuse only after an exact prediction match |

### 9.2 Does width-based planning beat greedy / A* in adversarial pursuit-evasion?
- **Atari Ms. Pac-Man**: IW(1) ≈ UCT, both ≫ blind breadth-first search. No greedy or A* baseline is reported, and the model is perfect [source: W02, W05].
- **GVGAI**: IW(1) won 191 vs 67 games for a myopic 1-step lookahead (set 1, 1 s). The games are not team-adversarial [source: W04].
- **CTF**: no evidence either way (section 3.3). Search-centred CTF agents did poorly in student write-ups [reported: methods.md M-05 / M-06].
- **Verdict**: **unknown**. No source shows IW beating a tuned rule-based greedy agent against adaptive adversaries.

### 9.3 Expected value for us [untested]
- **Bound**: the gain is limited by the points we lose where planning helps (section 5.4). Measure it before investing beyond design A.
- **Cheapest test**: design A, with the draft already written.
- **Cheapest independent test**: design C, which has no adversary model.
- **Design B**: only worthwhile if A shows that the model is good enough, i.e. A wins with few model-optimism deaths.

---

## 10. Test plan (fits `docs/evaluation.md`) [untested]

1. **Model fidelity (offline, local replays only)**:
   - From recorded games, compare the one-ply prediction of our next cell, carried food and death with what happened.
   - For visible enemy ghosts, measure how often the real move equals M1's and M2's prediction, per pool opponent.
2. **Timing**: planner time per move (p50 / p95 / max) on WSL Python 3.8 under parallel load (E-016 protocol), with a goal of max move < 0.5 s. Log `timed_out` rates.
3. **Screen** on tuning seeds against the reference pool, each as one switch on top of `lab6_off`:
   - A: `plan='danger'` × atoms {`pos_carry`, `pos_carry_g`} × D {3, 6, 12} × fixes S1–S6 on or off.
   - C: as a `food` target selector.
   - Metrics: PPG, deaths per game, deaths carrying ≥ 3, food returned per game, planner usage rate.
4. **Pre-register** the selection rule (as for `lab5_smart`) before the validation seeds. Then apply the accept rule (paired gain CI > 0, no opponent regression > 0.5, zero violations).
5. **Log** every run in `docs/experiments.md`. Add each team to `docs/agents.md`, and update M-05 / M-06 or a new method entry in `docs/methods.md`.

---

## 11. Open questions / unknowns
- What share of lost points comes from contact deaths and stranded food? (measure, section 5.4)
- How do the pool's ghosts actually move: chase, intercept, guard posts? (fit offline)
- How fast is the tournament CPU relative to this laptop? (unknown; the 2026-11-23 test run may tell)
- Is an offline teacher with full state (e5) acceptable under the fair-play policy? (ask before building; rules.md)
- Does the belief's argmax (median error 2 steps) suffice for hidden ghosts, or are the M5 samples needed? (A/B test inside design A)
