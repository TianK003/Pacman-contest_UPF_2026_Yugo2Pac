# Heuristics

There are two families, kept separate on purpose:

- **Map heuristics (`H-M##`)** are *static and structural*. They are computed once in `register_initial_state` (15 s budget) from walls, food and capsules, and say **where** things are risky or valuable. Because tournament maps are random and unseen (rules.md), they must be generic. Nothing may be hard-coded per layout.
- **Sensory heuristics (`H-S##`)** are *dynamic and local*. They are computed every turn from what the agent perceives (positions, noisy distances, food diffs, timers, score, time), and say **what is happening now**.

The strongest write-ups combine both (Part C). Each entry has an idea, how to compute it, how to use it, its cost, its evidence and its status. All statuses start at `idea`. Change them only together with an experiment ID from [experiments.md](experiments.md).

Evidence tags follow [README.md](README.md). `[reported: X]` means team X's own write-up says so; the sources are at the end. None of it was ablated or verified by us.

---

## Part A: map heuristics

### A0. How the UPF maps shape behaviour (facts, see framework.md)

- **Food sits in traps.** The random map generator places food in dead-end cells *first*, then at random [verified]. A greedy "nearest food" attacker walks into dead ends, which is why the baseline dies so often.
- **Death is expensive.**
  - About 80% of maps have 1–3 "prison" wall layers around the start, and each layer adds roughly a board height (~15 steps) to leaving the start [verified].
  - Being eaten therefore costs ~15–45+ of our 300 moves, on top of the dropped food.
  - The same applies to opponents, so a kill is worth more here than on open maps.
- **Symmetry.** Maps are point-symmetric, so every analysis of our side tells us the same about theirs.
- **Capsules and borders.** Each side has 2 capsules, never in the two columns next to the centre line [verified]. There are 30 food per side, and returning 28 ends the game.

### H-M01: Border cells and home distance
- **Idea**: know where "safety" is.
- **Compute**:
  - Our home column (`x = width//2 − 1` for red, `width//2` for blue) restricted to cells with an open neighbour across the line.
  - `dist_home[c] = min over border cells b of maze_dist(c, b)` for every cell.
- **Use**: return decisions (H-S04), escape checks (H-S03), endgame timing (H-S05).
- **Cost**: trivial with the precomputed distancer.
- **Evidence**: used by essentially every write-up [reported: many].
- **Status**: implemented in `teams/greedy_v1.py` (`MapInfo.home_border`, `dist_home`). Tested only as part of the team (E-002).

### H-M02: Dead ends, pockets and trap depth
- **Idea**: label every cell by how trapped you are in it.
- **Compute**:
  - Repeatedly delete cells of degree 1 (leaf pruning). The deleted cells form *dead-end trees*; each tree hangs off a single *entrance* cell on the remaining graph (the 2-core).
  - `depth[c] = maze_dist(c, entrance[c])`.
  - **Generalisation**: articulation points / biconnected components give *pockets*, i.e. regions with a single entrance even if they contain loops.
- **Use**:
  - Before entering a pocket with entrance `e` to eat food `f`, require `d(me,e) + d(e,f) + d(f,e) < d(nearest dangerous ghost, e)`, with a margin for belief uncertainty (H-S01).
  - Attackers prefer shallow food. Defenders know that an invader deep in a pocket can be trapped at `e`.
- **Cost**: O(cells) for leaf pruning, plus one articulation-point DFS. Both fit easily in the 15 s.
- **Evidence**:
  - The most consistently reported map heuristic [reported: AlanChaw, LuChenyang3842, infinityglow, DXJ3X1, abhinavcreed13].
  - Its absence is blamed for deaths [reported: Pac-Champs, MDB22, KTH report, hima950].
  - Extra relevant here because of A0.
- **Status**: implemented, leaf-pruning version only (no articulation-point pockets), as `DeadEndAttacker` in `teams/greedy_v1.py`. Tested in E-002 with no measurable effect. Both variants beat the baseline 40/40. Over the shared opponents the paired PPG difference (greedy − deadend) was −0.01 [−0.10, +0.07], within δ, and greedy edges it head-to-head (1.43 vs 1.27). It is **not adopted**. The pocket/articulation version and a test against a defender that really guards (P-02) are still open.

### H-M03: Chokepoints for defence
- **Idea**: one defender standing on the right cell can protect a whole region.
- **Compute**:
  - Articulation points on our half that separate the border from food.
  - More generally, a minimum vertex cut (max-flow) between the border cells and groups of our food.
- **Use**:
  - Defender patrol and guard positions (H-S07).
  - Rank food regions by how many cells it takes to seal them.
- **Cost**: max-flow on about 300 cells is cheap within the 15 s.
- **Evidence**: [reported: jaredj.xyz, who went from 13th to 4th the night a max-flow chokepoint defender was added; abhinavcreed13 also uses bottlenecks]. Capsules broke the blockade in the jaredj.xyz case.
- **Status**: idea.

### H-M04: Escape-route count
- **Idea**: a cell with only one way home is risky even if it isn't in a dead end.
- **Compute**: the number of vertex-disjoint paths from the cell to the home border (max-flow with unit vertex capacities), or a cheaper proxy: whether the cell lies in a pocket (H-M02).
- **Use**: a risk term in the attacker's food choice and path cost (M-03).
- **Evidence**: [reported: LuChenyang3842 marks food with 2+ routes home as "safe" and food with 3 surrounding walls as dangerous].
- **Status**: idea.

### H-M05: Food value and clusters
- **Idea**: value food by what a whole trip can earn.
- **Compute**:
  - Cluster food by maze distance.
  - Value a cluster as roughly (number of food) divided by (trip length to it + return length + depth risk).
  - Optionally plan a short multi-food route (a small TSP over 3–6 food dots) that ends at home.
- **Use**: attacker goal selection.
- **Evidence**: mixed [reported: AlanChaw used clustering; iknow1988 found cluster patrolling "took too long"; hima950 found cluster-shaped rewards inefficient].
- **Status**: idea.

### H-M06: Attack entry points
- **Idea**: choose where to cross the border, not only which food to eat.
- **Compute**: for each border cell, its distance to the target food and its distance from where enemy defenders tend to be (H-S11).
- **Use**:
  - Split our two attackers over different entry points.
  - Switch entry point when a defender mirrors us (H-S12).
- **Evidence**: [reported: infinityglow switches attack point when blocked].
- **Status**: idea.

### H-M07: Capsule geometry
- **Idea**: a capsule is worth whatever it unlocks.
- **Compute**: for each enemy capsule, its distance from the border and the food in nearby deep pockets (H-M02) that becomes safe while the enemy is scared. For our own capsules, which of our regions they make attackable.
- **Use**:
  - Capsule timing (H-S06).
  - Defenders may guard the capsule nearest the border.
- **Evidence**: [reported: jhammarstedt rushes capsules early; the KTH report credits capsule rushing for another team's wins].
- **Status**: idea.

### H-M08: Respawn cost
- **Idea**: the cost of dying depends on the map.
- **Compute**: `d(start, nearest home border cell)`, which is large when prison layers exist (A0).
- **Use**: scale risk tolerance. Be more careful as an attacker when the respawn cost is high, and value a kill more as a defender.
- **Evidence**: the map fact is [verified]; the behavioural benefit is [untested].
- **Status**: idea.

### H-M09: Map profile → parameter set
- **Idea**: "how the map affects behaviour", made explicit.
- **Compute**: map features in `register_initial_state`:
  - share of food in pockets
  - mean pocket depth
  - number of border crossings
  - respawn cost (H-M08)
  - loop density (cycles per cell)
  - capsule distance to border
- **Use**: map the features to parameters (risk margin, return threshold, double-attack vs attack+defend, patrol depth). Tune the mapping offline (M-02).
- **Evidence**: [untested].
- **Status**: idea.

### H-M10: Defensive patrol points
- **Idea**: stand where you can reach any likely intrusion fastest.
- **Compute**: cells that minimise the weighted maximum (or mean) distance to border crossings, weighted by how much food each crossing leads to.
- **Use**: idle defender position. Combine with chokepoints (H-M03).
- **Evidence**: [reported: infinityglow's defender targets dense-food cells].
- **Status**: implemented in a simple form in `PatrolDefender` (`teams/greedy_v1.py`): it cycles through the 3 border cells nearest the border cell with the minimum total distance to our food. Tested only as part of the team (E-002).

### H-M11: Precomputed tables (engineering)
- **Idea**: make the 1 s move budget go further.
- **Compute**: cell ids, neighbour lists, the distance matrix (the distancer already does this), `dist_home`, pockets. Store them in **one team object shared by both agents**, so the work isn't done twice.
- **Use**: everything else.
- **Evidence**: the engine already caches maze distances globally [verified].
- **Status**: idea.

---

## Part B: sensory (local, agent-perception) heuristics

### H-S01: Opponent belief tracking
- **Idea**: a probability distribution over cells for each hidden opponent. This is how we "see" beyond the 5-square radius.
- **Update, each of our turns**:
  1. **Motion**: an opponent moves at most 1 cell per move; use uniform or biased transitions. Between two turns of the *same* agent, each opponent moves exactly once. With a shared belief updated on both of our agents' turns, exactly one opponent (the one that just moved) has moved since the previous update, so elapse time for that one only.
  2. **Sonar**: likelihood `1/13` if `|reading − Manhattan(me, cell)| ≤ 6`, else 0. These are hard zeros and prune cells exactly.
  3. **Negative sight**: if the opponent is not visible, zero all cells within Manhattan 5 of *either* of our agents. If it is visible, collapse the belief to the exact cell.
  4. **Food and capsule events** on our side (H-S02): an opponent stood exactly there. Assign the event to the opponent whose belief makes it most likely.
  5. **Respawn**: when we eat an opponent (it collides with us), reset its belief to its start cell.
  6. **Side constraint**: from `is_pacman` (grey zone, Q3, off by default) or inferred from food events.
- **Sharing**: one belief per opponent, owned by the team object and updated by both of our agents, which gives two sonar readings per round.
- **Cost**: exact inference over about 400 cells × 2 opponents is cheap; a particle filter is not needed.
- **Evidence**:
  - [reported: AlanChaw, TianqiPeng, abhinavcreed13 (HMM / exact); loosh, lzheng1026 (particles)].
  - **Warning** [reported: KTH]: adding untested Bayesian tracking that overrode their food-diff logic dropped them from 2nd to 4th.
- **Status**: implemented, **set version** (support only): the `tracker` switch in `teams/greedy_lab_v1.py`. **Tested**: alone it makes the attacker timid, −0.11 vs greedy and −0.40 against turtle (E-007); with the breaker it adds nothing (E-010). Not adopted; a probabilistic version or a defender-side use is untested.

### H-S02: Food-diff invader detection
- **Idea**: missing food gives an exact location.
- **Compute**: compare `get_food_you_are_defending` (and our capsules) between our previous and current observation.
  - **Disappeared** cells: an invader was there within the last ~3 plies.
  - **Appeared** cells: an invader died nearby and dumped food.
- **Use**: defender target, and hard evidence for H-S01.
- **Cost**: trivial.
- **Evidence**: the most widely used trick, with about nine write-ups [reported: infinityglow, LuChenyang3842, jhammarstedt, hima950, pcgotan, DXJ3X1, iknow1988, the KTH winner, TacModd]. Several well-placed teams used *only* this.
- **Status**: implemented in `PatrolDefender`, which heads for the nearest just-eaten cell. Tested only as part of the team (E-002).

### H-S03: Race and threat analysis
- **Idea**: cheap adversarial reasoning. A cell is safe if I get there strictly before any dangerous opponent.
- **Compute**:
  - Compare `d(me, c)` against `d(ghost, c)` for the cells that matter: pocket entrances, home border, capsules.
  - For a hidden ghost, use its belief: worst case for safety, expectation for value. Account for turn order.
  - A ghost is "dangerous" if it is not scared, or if its scared timer runs out before the race ends.
- **Use**:
  - Gate pocket entry (with H-M02).
  - Decide when to escape and where (home vs capsule).
  - Choose the defender's intercept cell (H-S07).
- **Evidence**: [untested] as a formal rule. The "ghost distance" features used by most teams are a weaker version of it.
- **Status**: implemented as a "race-safe BFS" in `GreedyAttacker`. It only expands cells that we reach in strictly fewer steps than every visible dangerous ghost, and cells on our side are always safe. It ignores turn order and hidden ghosts. Tested only as part of the team (E-002).

### H-S04: Adaptive return trigger
- **Idea**: decide when to bank the food.
- **Compute**: return when `carrying ≥ k`, where `k` falls with:
  - distance home
  - threat level (H-S03)
  - time left (H-S05)
  - our score lead

  Always return when the food carried plus our returned food would reach 28 (that wins the game).
- **Evidence**: [reported: jhammarstedt eats about 5 then returns]. Thresholds flapping back and forth is a known failure [reported: LuChenyang3842], so add hysteresis.
- **Status**: implemented with **fixed** triggers in `GreedyAttacker`: carrying ≥ 5, ≤ 2 food left, a return that would win, out of time, or a ghost within maze distance 4. Tested only as part of the team (E-002). A situational version implemented as the `adaptive` switch in `teams/greedy_lab_v1.py`, plus a fixed-threshold sweep (`return_at` 3/8/12). Screening in E-007. **Tested** (E-007, E-010, E-011): alone no fixed threshold or the adaptive rule moved the total beyond noise; with the breaker, return-at-8 was the best (+0.21 tuning, +0.37 validation) and is used in greedy_v2. Return-at-8 **adopted** in my_team.py (greedy_v2) on 2026-10-18 (E-013).

### H-S05: Time and score control (endgame)
- **Idea**: the score and the time left are visible, so use them.
- **Compute**: our remaining moves ≈ `timeleft / 4`.
  - Force a return when `dist_home ≥ remaining − margin`.
  - Ahead late in the game: switch both agents to defence.
  - Behind: both attack, with higher risk tolerance.
- **Evidence**: the facts are [verified] (score and `timeleft` are visible); the strategy is [untested].
- **Status**: partly implemented: the time-based forced return (`TIME_MARGIN = 3`) in `GreedyAttacker`. greedy_v1 has no score-aware role switching. A score-aware endgame (lead → both defend, behind → both attack, last 40 own moves) implemented in the `roles` switch of `teams/greedy_lab_v1.py`. Screening in E-007.

### H-S06: Capsule timing and the scared window
- **Idea**:
  - Eat the capsule when it rescues us (a ghost is closing in and the capsule is reachable first) or when it unlocks deep pockets (H-M07).
  - During the scared window, harvest pockets whose round trip fits the remaining scared moves.
  - Eating a scared ghost sends it through its prison corridor (H-M08).
  - When **we** are scared, keep a safe distance from invaders but shadow them, ready to re-engage.
- **Compute**: track the opponents' scared window ourselves (we know when we ate the capsule, and it lasts 40 of *their* moves). Do not read their hidden `scared_timer` while Q3 is open.
- **Evidence**: [reported: capsule rushing helped some teams; capsules broke a chokepoint defence (jaredj.xyz)].
- **Status**: partly implemented in `V1Agent`:
  - The scared window is derived from enemy capsules disappearing, conservatively: counted from our previous observation, with a 3-move margin.
  - Respawn detection: a ghost that "teleports", or vanishes from Manhattan ≤ 2 of one of us, is marked unscared.
  - Capsules are escape targets when threatened.
  - No deliberate capsule timing in our candidate agents yet.
  - A capsule-first attacker (`CapsuleRusher`, `teams/sparring_v1.py`) was built as a sparring opponent. With greedy's defender it beat greedy head-to-head on tuning seeds, 1.35 vs 0.90 points per game (E-006). Paired with the border camper as `rusher_camper` it is screened in E-007.

### H-S07: Defender interception and shadowing
- **Idea**:
  - Move to the cell on the invader's predicted path (towards its nearest food, or its way home) that we reach first (H-S03).
  - Before it crosses, mirror its position along the border on our side.
  - Never cross into enemy territory as a defender.
  - Use pocket entrances to trap invaders (H-M02/H-M03).
- **Evidence**: [reported: KTH predicts the invader's border entry point from the path between the enemy base and the nearest food; the defender goes to the last eaten food (LuChenyang3842)].
- **Status**: partly implemented in `PatrolDefender`: it chases visible invaders on our side, keeps a distance of about 3 when we are scared, and goes to the last known position; greedy_v1 has no path prediction. Path prediction is implemented as the `intercept` switch in `teams/greedy_lab_v1.py` (E-007). A border-camping defender (`BorderCamper`, `teams/sparring_v1.py`) was built as a sparring opponent; as greedy's defender it beat greedy head-to-head on tuning seeds, 1.25 vs 1.10 points per game (E-006). **Tested** (E-007, E-010): alone +0.01 (no measurable effect); with the breaker +0.17 on tuning seeds (E-010); in greedy_v2 (E-011/E-012). **Adopted** in my_team.py (greedy_v2) on 2026-10-18 (E-013).

### H-S08: Dynamic role assignment
- **Idea**: decide attacker and defender every turn, not once.
- **Compute**: a utility based on the number of invaders (beliefs and food events), score, time, food carried and distances. Add hysteresis so roles don't flap.
- **Variants**: attacker + defender; double attack (no invaders and a weak enemy defence); double defence (ahead late).
- **Evidence**: [reported: the KTH tournament concluded that "rigid roles often resulted in deadlocks, dynamic role switching was a competitive advantage"; abhinavcreed13 switches by number of invaders].
- **Status**: **tested in a basic form** (`roles` switch, E-007): +0.12 [+0.00, +0.23] against the pool, but it **loses head-to-head to greedy** (0.95) and against camper (−0.45). Probable cause: the defender joins the attack and leaves our side open. Not adopted; the next step is to screen its three parts separately.

### H-S09: Teammate coordination
- **Idea**:
  - Don't chase the same food or use the same entry point.
  - Trap invaders in a pincer, each of our agents blocking one exit.
  - Share beliefs and goals through the team object.
- **Compute**: a greedy assignment of goals to agents (2×K, cheap).
- **Evidence**: [untested]. Sharing beliefs via a global [reported: KTH].
- **Status**: idea.

### H-S10: Anti-oscillation and commitment
- **Idea**: detect cycles (e.g. a repeated position in the last 8 moves) and break them. Commit to a goal for N steps unless the threat changes. Break ties at random with our **own** RNG instance (T-02).
- **Evidence**: [reported: abhinavcreed13 stuck detection; infinityglow border wandering; LuChenyang3842 threshold flapping]. We hit it ourselves [verified E-007]: without memory of ghosts that have left sight, greedy cycled through 4 cells on its own side for 180 moves (seed 41952914), and the first breaker version walked back towards the ghosts as soon as they were out of sight.
- **Status**: partly implemented. The standoff breaker commits to its chosen entry and counts blocked moves in a 12-move window (E-007). The F1/F2 attackers penalise revisiting the last 8 cells (E-008).

### H-S11: Opponent profiling
- **Idea**: learn the opponent's style *during the game* and adapt.
- **Compute**: running statistics, e.g.:
  - do they keep a defender at home?
  - where do they cross?
  - do they rush capsules?
  - how deep do they go?
- **Use**: switch parameter sets, e.g. go all-out attack if no defender has been seen for T turns.
- **Evidence**: [reported, only simple forms: iknow1988 assumes opponents eat the nearest food next to what they ate].
- **Status**: idea.

### H-S12: Breaking a border standoff
- **Idea**: when an enemy ghost mirrors our Pacman at the border, either switch to a distant entry point (H-M06), forcing it to travel, or attack with both agents at different points to overload a single defender.
- **Evidence**: [reported: infinityglow]. The standoff happens to us: greedy's attacker stood on the border for 261/300 moves against turtle on seed 97464282 and never scored [verified E-005].
- **Status**: **adopted** (E-013): in `teams/greedy_v2.py` = `my_team.py` since 2026-10-18 (the `breaker` switch). Against greedy: +0.13 [+0.02, +0.24] alone on tuning seeds 11–50 (E-010), +0.26 [+0.15, +0.38] alone on validation seeds 21–60 (E-011), and as part of greedy_v2 +0.42 on validation seeds 21–60 and 61–100 (E-011, E-012).

### H-S13: Deliberate death when carrying nothing
- **Idea**: being eaten with 0 food teleports us to our start.
- **Assessment**: probably bad on UPF maps, because of the prison corridors (A0). Recorded so nobody re-invents it without checking.
- **Evidence**: [untested].
- **Status**: idea, low priority.

---

## Part C: combinations (where the strength probably is)

- **Safe-food set**: food `f` that is safe to target now = H-M02 (pocket / entrance) + H-S01 (where the ghosts may be) + H-S03 (race to the entrance). This is the core attacker rule.
- **Defender position**: H-M03 / H-M10 candidate cells, weighted by H-S01 / H-S02 evidence of where invaders are.
- **Map-dependent parameters**: H-M09 sets the thresholds used by H-S04, H-S06 and H-S08.
- **Evidence**: practically every well-placed team in the write-ups is a hybrid. A rule or decision layer picks goals, search executes them, the map is analysed at startup, and opponents are tracked [reported: see the sources; DeNero & Klein say effective entries "combine search, adversarial search, and probabilistic tracking, and exploit various domain-specific strategies"].

## Sources

| Key | Link |
|---|---|
| DeNero & Klein, AAAI-10 | <https://ojs.aaai.org/index.php/AAAI/article/view/18829/18600> |
| AlanChaw (2nd, COMP90054 S2 2019) | <https://github.com/AlanChaw/comp90054-pacman> |
| LuChenyang3842 (3rd/152) | <https://github.com/LuChenyang3842/pacman-contest> |
| infinityglow (top ~15%, COMP90054 2020) | <https://github.com/infinityglow/COMP90054-Pacman-Contest-Project/wiki> |
| DXJ3X1 (2018 finalist) | <https://github.com/DXJ3X1/Pacman-Capture-the-Flag> |
| jaredj.xyz (UCSC) | <https://jaredj.xyz/blog/pacman-tournament-agent/> |
| abhinavcreed13 (UoM, PDDL + Q-learning) | <https://abhinavcreed13.github.io/projects/ai-team-pacamon/> |
| jhammarstedt (KTH DD2438 winner) | <https://github.com/jhammarstedt/PacmanAI> |
| KTH report | <https://github.com/95-ag/pacman-capture-the-flag> |
| loosh (LMU 2024 winner) | <https://github.com/loosh/pacman-ctf-agents> |
| TianqiPeng (UW #1 seed) | <https://github.com/TianqiPeng/Pacman_CTF> |
| iknow1988 (Team Poison) | <https://github.com/iknow1988/pacman> |
| Pac-Champs | <https://github.com/kkkkkaran/Berkeley-PacmanCTF/wiki> |
| MDB22 | <https://github.com/MDB22/Pacman> |
| hima950 | <https://github.com/hima950/AI-pacman-project> |
| lzheng1026 | <https://github.com/lzheng1026/Pacman-Capture-The-Flag> |
| pcgotan | <https://github.com/pcgotan/PacmanCTF_Agent> |
| TacModd | <https://github.com/TacModd/404-team-name-not-found> |

These are research pointers only. **Do not copy code from them** (rules.md R10).
