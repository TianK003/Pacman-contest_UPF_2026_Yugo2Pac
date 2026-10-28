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
  - **Re-opened by E-014** (replays of greedy_v2, the incumbent, which has no exit check):
    - In its non-wins against 6 of 8 pool opponents, 78–94% of its deaths happen inside a dead end (85% in wins too).
    - In 76–92% of those, the killing ghost could reach the exit before we got back out, and it was usually in sight when we went in.
    - So the exit-race check should matter now that the pool has real defenders. Re-test on top of greedy_v2 (candidate C1).
  - **Re-tested (E-018)** as the `exit_race` switch, generalised to any single-cell cut, on top of greedy_v2 against the 7-member pool:
    - It **halves our deaths and the food we lose** against every opponent.
    - But it adds only +0.02 [−0.06, +0.10] points per game, because food returned barely rises and border waiting rises. The refused food is not replaced by anything productive.
    - Not adopted. Avoiding traps alone is not worth points; it would need a better use of the moves it saves (e.g. other targets, a two-agent attack).

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
- **Status**: implemented in a **single-cell-cut** form as `ChokeDefender` in `teams/sparring_v2.py`, a league opponent and not our agent (E-015).
  - At startup it computes, for every home cell g, the home cells reachable from the border only through g: one BFS per cell, 0.03–0.05 s per map.
  - On 20 random maps the best single cell seals off 7.5 of our 30 food on average (range 2–22).
  - It guards that cell and traps invaders behind a cut cell it reaches first, closing in only through cells that still seal them off.
  - Max-flow / multi-cell cuts are not built. For results as an opponent see E-015. Using it in our own defender is untested.

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
  6. **Side constraint**: from `is_pacman` (allowed since Q3 was answered, behind the switch; untested) or inferred from food events.
- **Sharing**: one belief per opponent, owned by the team object and updated by both of our agents, which gives two sonar readings per round.
- **Cost**: exact inference over about 400 cells × 2 opponents is cheap; a particle filter is not needed.
- **Evidence**:
  - [reported: AlanChaw, TianqiPeng, abhinavcreed13 (HMM / exact); loosh, lzheng1026 (particles)].
  - **Warning** [reported: KTH]: adding untested Bayesian tracking that overrode their food-diff logic dropped them from 2nd to 4th.
- **Status**: implemented, **set version** (support only): the `tracker` switch in `teams/greedy_lab_v1.py`. **Tested**: alone it makes the attacker timid, −0.11 vs greedy and −0.40 against turtle (E-007); with the breaker it adds nothing (E-010). Not adopted.
  - **Probabilistic version** (E-019): an exact forward filter for the defender (`update_belief` in `teams/greedy_lab_v3.py`). Each agent uses only its own readings (Q4), with no grey-zone fields (Q3).
    - It uses steps 1–5 above; step 6 only through food events.
    - **Verified** against the opponents' true positions (60 games, 15,431 hidden enemy-turns): the true cell never gets probability 0. The most likely cell is a median 4 maze steps from the truth, against 9 for the last-seen position.
    - "Mass ≥ 0.5 on our side" detects a hidden invader with 66% recall and 57% precision.
    - Two pitfalls hit while building it: T-54 (pruning small probabilities) and T-55 (false respawns).
    - Uses in the defender (E-019):
      - `shadow` (H-S07) **passes the accept rule** (+0.16 [+0.04, +0.28] on validation seeds 101–180) and is **adopted** in `my_team.py` as greedy_v3 (E-021).
      - `hunt` adds nothing measurable: +0.07 [−0.02, +0.17] alone, nothing on top of `shadow`.
    - As the alarm of a raiding defender it adds nothing on top of `shadow` (E-020).

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
- **Compute**: track the opponents' scared window ourselves (we know when we ate the capsule, and it lasts 40 of *their* moves). Reading their hidden `scared_timer` directly is allowed since Q3 was answered (behind the switch).
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
  - **Known gaps** (E-014):
    - In greedy_v2's non-wins the defender is on average 5–8 cells from the invader, and it concedes 9–16 food per game.
    - It never closes in on an invader it holds off, because it only attacks within distance 2. One traced game froze into a 0–0 for ~1,000 plies.
    - The cut-cell "squeeze" in `ChokeDefender` (H-M03) is one possible fix.
  - **Tested (E-018)**: the `squeeze` switch (cut-cell trap + direct chase after a stalled intercept) adds +0.02 [−0.01, +0.06] (camper +0.07 [+0.01, +0.13]).
    - It rarely changes a decision: greedy_v2's intercept already holds dead-end exits.
    - Not adopted alone.
  - **Belief-based shadowing (E-019, `shadow` switch in `teams/greedy_lab_v3.py`)**: with nothing to chase, the defender waits at the border entry across from where the *raider* (the enemy last evident on our side) most likely is, using the H-S01 belief.
    - Screen +0.34 [+0.23, +0.45] and replication +0.29 [+0.19, +0.39] on tuning seeds; validation seeds 101–180 **+0.16 [+0.04, +0.28]**, head-to-head 1.65. **Passes the accept rule.** On the locked test seeds (E-021): +0.26 [+0.15, +0.36] over the pool and +0.17 [−0.00, +0.33] over the held-out teams. **Adopted in `my_team.py` as greedy_v3 (E-021).**
    - It works by deterrence, not kills: food conceded falls by 20–30%, kills fall.
    - Shadowing the enemy *nearest* our side follows their guard instead and shows it to our own attacker, which then stands blocked (T-56).

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
- **Status**: **adopted** (E-013): in `teams/greedy_v2.py` = `my_team.py` since 2026-10-18 (the `breaker` switch).
  - **Second half tested (E-018)**: the defender raiding through the farthest entry while our attacker is held at the border (`raid` switch, own observation only). Result: **−0.07** [−0.14, +0.01].
    - It returns about 1 more food per game but concedes 1.2–1.6 more, mostly against attacking teams (greedy −0.20 [−0.35, −0.05]).
    - Not adopted. Against greedy: +0.13 [+0.02, +0.24] alone on tuning seeds 11–50 (E-010), +0.26 [+0.15, +0.38] alone on validation seeds 21–60 (E-011), and as part of greedy_v2 +0.42 on validation seeds 21–60 and 61–100 (E-011, E-012).

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

---

## Part D: research survey 2026-10-28 (grid-maze heuristics and inferring hidden enemies)

Two research agents searched the literature on 2026-10-28; they opened every source cited here unless it is marked otherwise.
- **Topic 1**: movement, safety, territory and pursuit in 4-connected grid mazes.
- **Topic 2**: inferring what hidden enemies are doing from noisy sensors, and reacting to it.

The numbers are the sources' own, mostly from other games (Ms Pac-Man, Tron, robot pursuit, human judgements). Carrying them over to our game is [untested] throughout. Entries marked "E-025" are built in `teams/greedy_lab_v5.py`.

### D1. Perception: what the enemy is and where it is

| ID | heuristic | idea and computation in our game | use | cost | source | status |
|---|---|---|---|---|---|---|
| H-S14 | **Hidden-field perception** | Read the hidden enemies' fields (rules.md Q3) through one switch: `is_pacman` zeroes the belief on the wrong half; `num_carrying` +1 names the enemy that ate a vanished food; carrying → 0 without `num_returned` rising, or `scared_timer` dropping to 0 from ≥ 2, means it was eaten (respawn); `scared_timer` gives the exact scared window. "Not seen" and side information act as likelihoods, as in probabilistic pursuit-evasion [source: Vidal et al. 2002] | both | negligible | Vidal et al. 2002; engine `capture.py:487-495, 666-727` [verified] | **tested** (E-025, `flags`): side detection 58% → 100% correct, truth never ruled out; screen +0.11 [+0.00, +0.22] vs greedy_v3, food conceded 8.2 → 6.6 per game; in `lab5_smart` |
| H-S15 | **Shared team belief with exact one-enemy steps** | Turn order is fixed (0→1→2→3, random starter), so between our two agents' consecutive turns exactly **one** enemy moves: `(my_index − 1) % 4` [verified: `game.py:644-749`]. One team belief, updated at both agents' turns, spreads that enemy only, applies both agents' sonar readings, and attributes a vanished food dot to that enemy exactly | defender (both agents feed it) | halves the per-agent work | engine fact; sharing allowed (Q4) | **tested** (E-025, `shared`): most-likely-cell error 4 → 2 steps, p(true cell) 0.16 → 0.24 [verified]; but screen points +0.003 [−0.08, +0.08]; in `lab5_smart` by the pre-registered rule |
| H-S16 | **Cost-difference goal recognition** | A near-rational agent most likely heads to the goal that its route so far cost the least extra to reach: X_g(n) = d(n,g) − d(s,g), P(g\|n) ∝ e^(−βX) / (1 + e^(−βX)) [source]. Over a belief: P(g) = Σ_n b(n) P(g\|n). Goals: our food while the invader carries little, its home border once it carries a lot. Same ranking as Ramírez–Geffner, 4–12× faster [source]; probabilities flatten on long paths [source] | defender | ~1–2k lookups per enemy per turn | Masters & Sardina, AAMAS 2017; Ramírez & Geffner, AAAI 2010 | simplified version (next food = the nearest food under the belief; exit = the crossing nearest in expectation) **tested** (E-025, `guard`): +0.03 [−0.09, +0.15], −0.08 against `flags` alone, rusher −0.27; not in `lab5_smart` |
| H-S17 | **Goal-directed motion model in the HMM** | Replace the random walk by "roughly optimal toward a goal": π(s'\|s,g) ∝ exp(β(d(s,g) − d(s',g))), mixed with the random walk (ε > 0) so the true cell is never ruled out (T-54) [source: Ziebart et al. 2009, planning-based prediction]. Mode-switching filters (attack / return / escape) generalise it [source: Liao et al. 2004: goal prediction 0.66 → 0.98 along a trip, against 0.69 for a Markov baseline] | both | ~20k operations per enemy per turn, or one BFS field per mode | Ziebart et al., IROS 2009; Liao, Fox & Kautz, AAAI 2004 | built as a 2-mode bonus (forage → nearest food, return → home); **tested** (E-025, `directed`): belief p(true cell) 0.17 → 0.18 only; screen +0.009 on top of `flags`; in `lab5_smart` by the rule (noise-level) |
| H-S18 | **Goals that change; recency** | Bayesian inverse planning in which the goal can change with probability γ per step fits human judgements best (r = 0.97); "the goal it most recently moved toward" is almost as good (0.96); a fixed goal much worse (0.82) [source] | defender | O(\|G\|) | Baker, Saxe & Tenenbaum, Cognition 2009 | idea (supports re-estimating the goal every turn, as E-025 does) |
| H-S28 | **Opponent type classification** | Each enemy is one of K types (raider, camper, rusher, capsule-taker); update a posterior over types from windowed counts (share of turns as Pacman, carrying when it turns home, time to first crossing), with Beta / Dirichlet priors; switch formation when one type passes ~0.8 [source] | both | O(K) | Albrecht & Stone, AIJ 2018; Riley & Veloso, DARS 2000; Southey et al., UAI 2005 | partly: E-025 learns each enemy's return amount from its own past returns |

### D2. Defence and pursuit

| ID | heuristic | idea and computation in our game | use | cost | source | status |
|---|---|---|---|---|---|---|
| H-S19 | **Cover-maximising pursuit (CRA)** | The cover is the set of cells some pursuer reaches before the target. Each pursuer picks the move that makes the cover largest, given the other's position, which surrounds the target instead of trailing it. With 2 pursuers: 253/300 captures vs MTS 234 and minimax 211 [source]. Ours: count home cells where min(our two distances) < the invader's distance; for a hidden invader weight by the belief | defender, 2 defenders | ≤ 10 × O(N) | Isaza, Lu, Bulitko & Greiner, AIIDE 2008 | idea |
| H-S21 | **Global-max belief pursuit** | Move to the reachable cells that maximise the belief mass captured, not the single most likely cell (local-max has no progress guarantee; global-max has a bound on expected capture time) [source]. A one-step variant: pick the move whose sight disc (Manhattan 5) covers the most belief mass [source: Hespanha et al. 2000] | defender | ≤ 100 pairs | Vidal et al. 2002; Hespanha, Prandini & Sastry 2000 | idea |
| H-S25 | **Pincer roles, anti-clumping** | Each pursuer targets the junction in front of or behind the evader; no two pursuers in the same corridor in the same direction [source: Pepels & Winands 2012]. Arcade ghosts: Pinky aims 4 tiles ahead; Clyde chases from far and retreats when close [source: Pac-Man Dossier] | 2 defenders | O(1) | Pepels & Winands, CIG 2012; Pittman, Pac-Man Dossier | idea |
| H-M14 | **Cop-number structure** | One cop always catches a robber on a tree; a cycle longer than 3 needs two [source]. A lone defender should chase only inside dead-end trees and otherwise hold a cut cell or wait for its partner; one cop can guard a shortest path between two border cells (a basis for shadowing) | defender | precomputed | Aigner & Fromme 1984 (via Wikipedia, *Cop number*) | idea |
| H-S26 | **Formation by enemy-Pacman count** | Roles are swapped at run time on triggers [source: Stone & Veloso 1999]; assign agents to targets so the longest travel is shortest [source: SCRAM, MacAlpine et al. 2015]. Ours: 0 enemy Pacmen → normal; 1 → the defender marks it; 2 → both defend, split by min-max distance | both | trivial | Stone & Veloso, AIJ 1999; MacAlpine, Price & Stone, AAAI 2015 | built as `recall`; never fired against the pool (E-025, 800 games). Against double attackers (E-025 diagnostic): **−0.58** vs `double_attack`, **−0.40** vs `friend_aljaz_1`. It cuts our returns by a third and barely reduces theirs. **Rejected** in this form: against a double attack, race instead |

### D3. Attack and escape

| ID | heuristic | idea and computation in our game | use | cost | source | status |
|---|---|---|---|---|---|---|
| H-S20 | **TrailMax escape** | Spread from evader and pursuer together, drop the evader cells the pursuer has reached, run to the evader cell the pursuer reaches last. 98.3% of optimal survival time, against 80.3% for minimax(11) and 76.0% for greedy distance (perfect information, cop at speed 2) [source]. Ours: for the "cut off" 12% of attacker moves (E-022), go to the cell we reach first that the ghosts reach last, buying time for the capsule, the scare timer or the teammate | attacker | one BFS | Moldenhauer & Sturtevant, IJCAI 2009 | idea (**top candidate for the next round**: it targets a measured loss) |
| H-M12 | **Junction graph with a safe-edge test** | Search over junctions instead of cells; a move is safe if its corridor holds no ghost coming towards us and we reach the next junction before every ghost; switch to survival when the best survival rate falls below 0.7; reward clearing a whole corridor (no isolated food left behind). Removing the rule-based playouts cut the score from 107,561 to 44,758 [source] | attacker | built once at startup | Pepels & Winands, CIG 2012 | idea |
| H-M13 | **Voronoi territory, chambers, battlefront** | Each cell belongs to whoever reaches it first; score K1·cells + K2·edges with K2 ≈ 3.5·K1; across cut vertices a chamber tree chooses which region to claim [source]. Ours: an invader whose region holds no border cell is sealed in, so hold the sealing cut cell instead of chasing | both | O(N) per position | Sloane (a1k0n), Google AI Challenge post-mortem 2010 | idea |
| H-S22 | **Capsule lure** | Eat the capsule only when it pays: wait next to it while safe, eat it when a defender comes within k, then eat the defender (its respawn behind the prison is expensive) [source: Brauers 2011; ICE Pambush 3 reported] | attacker | O(1) | Brauers, BSc paper, Maastricht 2011 | idea |
| H-S23 | **Orienteering trip builder** | Choose a trip of several food dots that still gets home within a budget: sample the next stop among the top 4 by (prize / distance)^4 [reported: Tsiligirides 1984 via Kool et al. 2019]; a survival-constrained variant accepts a trip only if its estimated survival probability is ≥ p_s [source: Jorgensen et al. 2016, abstract only] | attacker | O(F²) per trip | Kool, van Hoof & Welling, ICLR 2019; Jorgensen et al., arXiv 2016 | idea |
| H-S24 | **Marginal value rule for returning** | Leave a patch when its intake rate falls to the habitat's average including travel; longer travel → stay longer [source]. Ours: with long prison corridors, carry more when no defender can reach us before we get home | attacker | trivial | Charnov 1976 (via Wikipedia, *Marginal value theorem*) | **tested** (E-025, `open_goal`): screen **+0.17 [+0.05, +0.29]**, +0.057 on top of `flags`, max carried 7.4 → 8.9, deaths 1.02 → 0.94; in `lab5_smart` |
| H-S27 | **Bold play when behind, timid when ahead** | To reach a target, bold play is optimal at unfavourable odds and timid play at favourable odds [reported: Dubins & Savage]; generalised to two-person games [source: Secchi 1997]; in hockey, pulling the goalie at ~5:40 left when down one is optimal although it raises the opponent's scoring rate more [reported: Asness & Brown]. Ours: maximise 3·P(W) + P(T): ahead late → both defend; behind late → both attack and bank as soon as a trip would take the lead | both | trivial | Secchi, J. Appl. Prob. 1997; Asness & Brown (via Chicago Booth Review) | **tested** (E-025, `endgame`): screen +0.006 [−0.02, +0.03]; in `lab5_smart` by the rule (noise-level) |
| H-S29 | **Deceptive routing** | An observer using H-S16 is only certain within a goal's "radius of maximum probability"; keep two food clusters tied on cost difference as long as possible [source] | attacker | precomputed heat map | Masters & Sardina, IJCAI 2017 | idea |

Checked and found nothing new for us: the Ms Pac-Man vs Ghost Team CIG 2016 competition (partial observability by line of sight; ghosts remember the last sighting for ~50 ticks; sharing sightings cut Ms Pac-Man's score to 33%) [source: Williams, Perez-Liebana & Lucas 2016]. Our exact belief and Q4 sharing cover it.

Sources the agents could not open (status unknown): Blom & Bar-Shalom 1988 (IMM), Bruce & Gordon 2004 (PDF 404), Dubins & Savage (book), Baudiš 2011 (403), Asness & Brown's original (403).

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
| Isaza, Lu, Bulitko & Greiner, AIIDE 2008 (cover pursuit) | <https://cdn.aaai.org/ojs/18672/18672-52-22262-1-10-20210927.pdf> |
| Huang et al., CDC-ECC 2011 (Voronoi pursuit) | <https://skoge.folk.ntnu.no/prost/proceedings/cdc-ecc-2011/data/papers/1841.pdf> |
| Moldenhauer & Sturtevant, IJCAI 2009 (TrailMax) | <https://ijcai.org/proceedings/2009/0103.pdf> |
| Sloane (a1k0n), 2010 (Tron Voronoi / chambers) | <https://www.a1k0n.net/2010/03/04/google-ai-postmortem.html> |
| Pepels & Winands, CIG 2012 (MCTS Ms Pac-Man) | <https://dke.maastrichtuniversity.nl/m.winands/documents/CIG2012_paper_106.pdf> |
| Brauers, BSc paper 2011 (capsule lure) | <https://project.dke.maastrichtuniversity.nl/games/files/bsc/Brauers_BSc-paper.pdf> |
| Kool, van Hoof & Welling, ICLR 2019 (orienteering, App. D.3) | <https://arxiv.org/pdf/1803.08475> |
| Jorgensen et al., 2016 (Team Surviving Orienteers) | <https://arxiv.org/abs/1612.03232> |
| Cop number (Aigner & Fromme 1984) | <https://en.wikipedia.org/wiki/Cop_number> |
| Hespanha, Prandini & Sastry, 2000 (one-step Nash pursuit) | <https://web.ece.ucsb.edu/~hespanha/published/one-nash.pdf> |
| Pittman, The Pac-Man Dossier | <https://pacman.holenet.info/> |
| Marginal value theorem (Charnov 1976) | <https://en.wikipedia.org/wiki/Marginal_value_theorem> |
| Williams, Perez-Liebana & Lucas, 2016 (Ms Pac-Man vs Ghost Team) | <https://arxiv.org/abs/1609.02316> |
| Masters & Sardina, AAMAS 2017 (cost-based goal recognition) | <https://ifaamas.csc.liv.ac.uk/Proceedings/aamas2017/pdfs/p750.pdf> |
| Ramírez & Geffner, AAAI 2010 (probabilistic plan recognition) | <https://ojs.aaai.org/index.php/AAAI/article/view/7745> |
| Sohrabi, Riabov & Udrea, IJCAI 2016 | <https://www.ijcai.org/Abstract/16/461> |
| Ziebart et al., IROS 2009 (planning-based prediction) | <https://publications.ri.cmu.edu/planning-based-prediction-for-pedestrians> |
| Vidal et al., IEEE T-RA 2002 (probabilistic pursuit-evasion) | <https://people.eecs.berkeley.edu/~sastry/pubs/PDFs%20of%20Pubs2000-2005/Pdfs%20of%20Misc.Others/Vidal/VidalShakerniaProbabilistic2002.pdf> |
| Baker, Saxe & Tenenbaum, Cognition 2009 (inverse planning) | <https://dspace.mit.edu/handle/1721.1/60852> |
| Liao, Fox & Kautz, AAAI 2004 (transportation routines) | <https://www.cs.virginia.edu/~rmw7my/papers/gps-tracking.pdf> |
| Stone & Veloso, AIJ 1999 (formations) | <https://www.cs.utexas.edu/~pstone/Papers/bib2html/b2hd-AIJ99.html> |
| MacAlpine, Price & Stone, AAAI 2015 (SCRAM) | <https://ojs.aaai.org/index.php/AAAI/article/view/9424> |
| Secchi, J. Appl. Prob. 1997 (red-and-black games) | <https://www.cambridge.org/core/journals/journal-of-applied-probability/article/twoperson-redandblack-stochastic-games/82AFFDDFFB59F5D9E574C16FB2C1111F> |
| Asness & Brown via Chicago Booth Review | <https://www.chicagobooth.edu/review/when-hockey-teams-and-money-managers-should-go-broke> |
| Albrecht & Stone, AIJ 2018 (agents modelling agents) | <https://arxiv.org/abs/1709.08071> |
| Riley & Veloso, DARS 2000 (adversary classes) | <https://www.cs.cmu.edu/~coral/old/publications/b2hd-DARS-AdvClass.html> |
| Southey et al., UAI 2005 (Bayes' bluff) | <https://arxiv.org/abs/1207.1411> |
| Masters & Sardina, IJCAI 2017 (deceptive path-planning) | <https://www.ijcai.org/proceedings/2017/610> |

These are research pointers only. **Do not copy code from them** (rules.md R10).
