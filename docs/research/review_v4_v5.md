# Review of greedy_v4 and greedy_v5 (external reviewer, 2026-11-08)

- **Who / how**: a separate agent (Fable 5.1, maximum effort), read-only, asked by the user to inspect the logic of `teams/greedy_v4.py` (= `my_team.py`) and `teams/greedy_v5.py` (override mode), critique it and propose at least two improvements for each.
- **Data it was allowed**: tuning-seed runs (`n1_x1`, `n1_x2`, `n1_x4a–e`, `n1_x5a–e`, `n1_diag_v4`) and the old-validation runs `n1_v1`, `n1_v2`. **Not** allowed (and not opened): the locked test-seed runs, anything with the held-out teams, the running validation `n1_v3`, friends' code.
- It ran 3 games on tuning seeds (`trace_game.py`, `replay_probe.py replay`) and two offline planner probes (scripts in the session scratchpad, not in the repo).
- What we did with it: E-039 in `docs/experiments.md`. Line numbers refer to `teams/greedy_v4.py` (v5: +8 from line 3 on).
- The text below is the reviewer's report, unchanged except for this header.

---

## 1. Summary of the logic

**Team construction.** `create_team` (241–260) with `endgame=1` builds two `RoleAgent`s (2269–2387) sharing one `TeamMemory` (941–1027). Each agent's `choose_action` (2288–2305): `perceive` → `role_of` → attack or defend; a called-back Pacman first retreats (2297–2301).

**Perception (both agents).** `fields()` (1078–1085) is the single read of hidden opponents' `is_pacman / num_carrying / scared_timer / num_returned` behind `USE_HIDDEN_OPPONENT_FLAGS` (115) and `flags`. `TeamMemory.update` (965–1027) keeps an exact forward belief per enemy: only the enemy that moved since the last update is spread (968, 1003–1004), with the directed motion model (`elapse` 1279–1300, `goal_field` 1302–1312, DIRECT_BONUS=2), sonar/sight consistency (988–991), side constraint from `is_pacman` (`side_ok` 1098–1100), respawn detection by vanish-near-us and by field jumps (`field_respawn` 1087–1096), food/capsule events pin the mover (1008–1012). Scared timers are exact (`enemy_scared` 1414–1417, margin 3).

**Attacker (`attack_core` 1789–1851).** Order: `threatened` = visible non-scared ghost ≤ `threat_dist` 4 (1800); `enough` = carrying ≥ 8 unless `open_goal` says no enemy can reach us before home + 4 (1802–1804, `goal_open` 1374–1395 with the 0.1 belief quantile); endgame bank when behind late (1806–1807); `go_home` (1808–1813). Then, in danger mode only, the **planner block** (1816–1827): if no special case, `plan_move` (1730–1743) runs when a non-scared *modelled* ghost (visible, or hidden at its belief argmax, `plan_ghosts` 1674–1706) is within 7; its move is played if `best_value ≥ 0.05` and legal, and the breaker's counter gets a `False`. Otherwise greedy: `follow_entry` (1829–1832), nearest race-safe food by BFS (`food_is_safe` 1917–1919 and `safe_fn` 1496–1503 use *visible* ghosts only), `break_standoff` (1875–1904: after 3 blocked moves in 12 → capsule if safely reachable, else walk on our side to the border cell whose cross cell is farthest from the ghosts), else `retreat` (1853–1860: BFS home, capsules as targets when threatened) → `evade` (1921–1927).

**Planner (`WidthPlanner._search` 390–741).** IW(1) breadth-first over our moves (+Stop, 616–617); atoms (cell, carry bucket) for surviving states only (682–714); root children always kept. Model per generated child: eat +0.5, capsule +0.3 and all ghosts scared 37 (626–638), bank +0.5·carried (646–648); ghosts then move once: scared → maximise distance (655–663), within 6 → minimise distance to our new cell (664–672), else hold; death if a ghost ends on our cell on their side (639–645, 673–678): −(0.5·carried + 3) (679–680). Node value = discounted path reward + γ·leaf (691), leaf = `LEAF_NET` (12-16-1 tanh, 281–285, fast path `leaf_netf` 519–562) minus 0.5·carried. `root_best[a]` = max over the subtree of root action a (731–733); the played move is the root action of the best node anywhere in the tree (734–741). Cap 2000 nodes, 0.3 s clock (594–598). I checked the 12 features against the training code: `eval/rl/log_team.py:29–66` computes them with the same `plan_ghosts` placement and `eval/rl/train_value.py:5` drops exactly score/ghost1_visible/mate_attacking, so feature order and scaling match [verified].

**Defender (`defend` 1968–2033).** Visible invaders → `intercept_cell` (2087–2110: chase within 2; hold a dead end's exit if first; else the first cell on the invader's shortest way home we reach no later). Scared and an invader visible → `keep_distance` 3 (2147–2153). Else: eaten-food cell (1977–1982), else `shadow_post` (2134–2145: the border entry across from the raider's expected cell; raider = the enemy that is a Pacman now, 1361–1365), else `next_patrol_point` (3 border cells nearest the food centroid, 2155–2167). `hunt`, `guard`, `dplan` are off.

**Endgame roles** (`role_of` 2333–2347, `late` 1748–1750): last 40 own moves, score > 0 → both defend, score < 0 → both attack, 0 → home roles.

**v5 override (`attack_override` 1757–1787).** Greedy's move `g = attack_core(gs, False)` is computed first (with all its side effects); specials return `g`; if a non-scared modelled ghost is within 7 the planner runs on the same state and `action` replaces `g` iff `root_values[action] − root_values[g] > 0.3` and it is legal. There is no `plan_min` test in this path.

---

## 2. Where points go (greedy_v4, tuning seeds)

**2a. Non-wins by type** (`replay_probe.py classify`, runs `n1_x4a–e` + `n1_x5a–e`, 4,240 games, opponents = pool + lab arms). Points lost vs 3/game = 3,038:

| failure type | share of lost points |
|---|---|
| loss: they returned more (defence) | **45 %** |
| tie: equal trade | 23 % |
| loss: our deaths (≥ 3 deaths or ≥ 6 food lost) | 12 % |
| tie 0-0: we barely attacked (< 60 Pacman moves) | 10 % |
| loss: we returned ≤ 3 | 6 % |
| tie 0-0: attacked but returned nothing | 2 % |
| loss: out-raced (they hit 28 first) | 2 % |

**2b. Per pool opponent** (runs `n1_x4a–e, n1_x5a–e, n1_x2, n1_diag_v4, n1_v2`; 400 games each; team totals per game; att/def = our attacker/defender index):

| opp | PPG | W-T-L | returned | conceded | deaths att/def | food lost att | attacker standoff moves | kills |
|---|---|---|---|---|---|---|---|---|
| lab5_smart | 2.21 | 274-61-65 | 14.7 | 9.5 | 0.27/0.08 | 0.9 | 67 | 1.13 |
| greedy_v3 | 2.38 | 302-48-50 | 15.3 | 8.6 | 0.26/0.08 | 1.1 | 71 | 1.08 |
| exploit_v2 | 2.60 | 336-30-34 | 16.1 | 6.1 | 0.26/0.07 | 1.3 | 65 | 0.49 |
| greedy_v2 | 2.60 | 338-28-34 | 16.3 | 8.5 | 0.33/0.08 | 1.3 | 59 | 1.14 |
| choke | 2.62 | 340-28-32 | 17.0 | 8.4 | 0.30/0.07 | 1.2 | 49 | 1.08 |
| camper | 2.67 | 345-32-23 | 16.6 | 5.8 | 0.31/0.05 | 1.4 | **84** | 0.91 |
| rusher | 2.69 | 351-21-28 | 16.7 | 6.4 | 0.28/**0.49** | 1.0 | 73 | 0.84 |
| greedy | 2.78 | 364-20-16 | 16.5 | 5.7 | 0.24/0.04 | 1.0 | 77 | 0.94 |
| feature | 2.80 | 369-14-17 | 17.3 | 6.0 | 0.29/0.07 | 1.2 | 64 | 0.52 |

Readings: the attacker spends 49–84 of its 300 moves (16–28 %) as a ghost near the border with an enemy ghost in sight (sentinel `standoff_moves`). Our defender dies 0.49/game against the capsule-first `rusher` vs 0.04–0.08 against everyone else: a ghost on its own side can only die while scared. Deaths of the attacker are already low (0.24–0.33/game, ≈ 4 food each).

**2c. Games bucketed by the attacker's Pacman moves** (pool only, 2,880 games):

| attacker Pacman moves | share of games | PPG | our returned | conceded | attacker standoff moves |
|---|---|---|---|---|---|
| 0–29 | 5.2 % | **1.20** | 1.0 | 1.5 | 183 |
| 30–59 | 5.6 % | 2.04 | 7.2 | 4.7 | 121 |
| 60–119 | 26.1 % | 2.64 | 14.2 | 5.9 | 87 |
| 120–179 | 41.5 % | 2.81 | 19.4 | 7.8 | 57 |
| 180+ | 21.6 % | 2.57 | 18.0 | 8.6 | 27 |

The "held at the border" games (10.8 %) cost ≈ 0.1 PPG; they are not chokepoint maps: over 60 tuning maps the central two columns are open on 6–16 of 16 rows (median 12), but the *openings from the corridor into the maze* number only 2–16 per side (26/60 maps have ≤ 4) [verified by generating the mazes]. Per seed, the worst maps (PPG 1.3–1.8 over 18 games) are open, high-scoring maps (we return 16–20, concede 14–18); only 3 of 200 seeds are "nobody crosses" maps (e.g. 62941804: 14 of 18 games 0-0), worth ≈ 0.01 PPG overall.

**2d. Two replayed worst losses vs greedy_v3** (`replay_probe replay --worst 2`, run `n1_x5a`) [verified]:
- Seed 53643535 (blue), 0–13: our attacker had **0 Pacman plies** in 1,200 plies (341 standoff plies); their attacker ate our capsule at ply 563 and returned 8 + 5. Trace labels for our attacker: no-safe-food 36 %, eat 29 %, entry 26 %, blocked 6 %, switch-entry 3 %; moves 150–175 walk the whole corridor (17,16)→(17,1)→(17,16) while the guard mirrors.
- Seed 50630759 (red), 8–16: capsules eaten by both sides at plies 228/229; our **scared defender died at ply 357 in a dead end (depth 6) on our side**; our attacker died at ply 715 **carrying 11**, "killer not in sight at the dead-end entry" (open_goal had let it exceed 8).

**2e. Outside the pool** (`n1_diag_v4`, 20 games each, diagnostic only): vs the double-attacking `friend_aljaz_1/4/5` we concede 13–18/game (their *defender* returns 5.7–10.1), our max carry rises to 15–17 (open_goal: both enemies are Pacmen, so "nobody can catch us") and food lost is 3.4–5.2/game vs ≈ 1.1 in the pool.

---

## 3. Critique / bugs

1. **The planner switches the standoff breaker off exactly when it is needed** [verified: code + probe]. `attack_core` 1823–1827 appends `False` to `self.blocked` on every planner move, and `break_standoff` (1847–1850) is only reached when the planner returns `None`. The probe (RANDOM53643535 blue, guard on the cross cell, carry 0) gives best root values 0.093–0.17 at 250 steps left, 0.056–0.074 at 200, and 0.29–0.36 on RANDOM62941804 at 120 — all ≥ `plan_min` 0.05, so the planner keeps control and plays North/South/Stop along the border on leaf differences of 0.01–0.05 (the crossing move is −3.00). v4's standoff behaviour is therefore the planner's shuffle, not the designed breaker; v5 runs the breaker first, which is a structural difference between the two versions that E-034 never isolated.
2. **The breaker's entry choice cannot work on RANDOM maps** [verified: maps + trace]. `away()` (1898–1902) ranks the 16 *border cells* by the guard's distance to the cross cell; the two central columns are a corridor open over most of its height, so a mirroring guard (shadow_post, camper) keeps distance 1–2 at equal speed; the attacker walks 15 cells to the far end and back (trace 53643535, moves 150–175). The real chokepoints are the 2–16 openings into the maze (section 2c), which `MapInfo` does not represent (`home_border`/`cross` 871–873).
3. **v5 has no `plan_min` / all-die guard** [verified: code 1779–1787 vs 1738]. In v4, `plan_move` hands back to greedy when `best_value < 0.05`; in v5 the override fires on the margin alone. Combined with item 4 this matters in trapped states.
4. **Death is priced inconsistently between the tree and the leaf** [verified: code 679–680, 560–562]. An in-tree death costs −(0.5·c + 3) after +0.5 per food eaten, i.e. −3 flat relative to not eating; a leaf-predicted death is ≈ y − 0.5c with y ≈ −c, i.e. −1.5c. Max-backup hides this when any survivor exists (hence `d8` played identical games), but when *all* continuations die the planner prefers the earliest, cheapest in-model death. Probe (2 steps inside a dead end, ghost at the entrance or one step outside): in 3/12 (53643535) and 8/30 (62941804) cases the best root action walks *towards* the ghost with a negative value, several exactly at the death value (e.g. carry 6: −5.82 = −6·0.97 vs −8.23 for the deeper move). v4 returns these to greedy (`evade`); v5 overrides `evade` whenever the gap exceeds 0.3. Whether dying early or running deeper is better against real defenders (ours and `choke` hold the exit and never enter: running deeper is then a stalemate, not a death) is [untested]; what is verified is that v5 diverges from v4 there by construction.
5. **Scared defender is both useless and killable** [verified: code; frequency partly verified]. `keep_distance` (2147–2153) only minimises |d − 3| over neighbours on our side, with no dead-end or exit awareness; when the invader is *not visible* a scared defender keeps following eaten-food targets, i.e. walks towards the invader (1977–1982, 2021–2022). Nothing in `defend` ever considers our own capsules. Data: defender deaths 0.49/game vs `rusher` (0.04–0.08 otherwise); both replayed worst losses were preceded by the enemy eating our capsule (section 2d). Greedy-family attackers take capsules as an *escape* when threatened (`retreat` 1856), so our intercept pressure is what sends them to the capsule.
6. **`open_goal` has no carry cap and trusts a 0.1-quantile of a possibly wide belief** [verified: code 1374–1395; one death verified]. Replayed death with 11 carried where the killer was out of sight at the dead-end entry; vs double attackers max carry reaches 15–17 and food lost 3.4–5.2/game. How many of those deaths open_goal caused is [untested].
7. **Side effects of `attack_core(gs, False)` leak into v5's override** [verified: code 1761, 1826, 1886, 1902]. `blocked`, `entry` and `ghost_seen` are updated by the greedy pass even when the planner then overrides; `follow_entry` (1829–1832) keeps pulling the attacker toward a stale entry on later turns unless the planner beats it by 0.3 each turn. Oscillation frequency [untested].
8. **Ghost model: chase within 6 or hold** (664–672). A shadowing or intercepting guard is only represented through the leaf. The built `m2` intercept scenario (`plan_models='m1m2'`, 370–371, 664–665) was never evaluated (agents.md: "not played"). [verified: code + docs]
9. **Minor, not bugs**: hidden-ghost argmax placement can trigger the planner on an arbitrary cell when the belief is diffuse ('near' tested flat); at an agent's very first move `TeamMemory.update` spreads the mover's prior once although it has not moved yet (968, 1003–1004; harmless); a visible scared ghost with timer ≤ 3 is modelled as a chaser (1688), consistent with `enemy_scared`. Timing is comfortable: p95 0.117 s, max 0.276 s under 7–8 parallel jobs (E-034 runs), planner on ≈ 17 % of attacker moves; there is ≈ 0.2 s per move of unused budget.

---

## 4. Proposals for greedy_v4 (all also apply to v5 unless noted)

### V4-A. Scared-defender posture and capsule denial (defender)
- **Where**: `PatrolDefender.defend` 1968–2033 (before 1988), `keep_distance` 2147–2153.
- **Change**:
  ```
  if scared and invader known (visible, or likely_cell of the raider):
      exit = min(home_border, key=d(invader, ·))            # its way home
      cands = cells on our side with d(c, invader) >= 2 and depth[c] == 0 (no dead ends)
      target = argmin over cands of (d(c, exit), d(pos, c)); BFS to it (on our side)
      resume intercept when my_scared_timer <= d(pos, invader) - 1
  elif invaders visible and our capsules remain:
      cap = nearest capsule to the invader
      if d(invader, cap) < d(pos, cap) + 1 and d(invader, cap) <= 8:   # it gets there first
          target = cap  (stand on it: a Pacman stepping onto a non-scared ghost dies)
  ```
- **Why**: item 5; 45 % of lost points are "they returned more", and the two replayed losses both ran through our capsule. Standing on the capsule denies it completely; keeping to the exit path while scared makes the timer's end an interception instead of a respawn walk.
- **Expected**: conceded −1…−2/game vs capsule-using attackers (rusher, baseline-style, greedy-family escapes), defender deaths vs rusher 0.49 → ≈ 0.1; neutral vs camper/choke.
- **Test**: `--diag` conceded and defender deaths per opponent; `replay_probe replay` capsules column. Cheap: a few BFS per move. Risk: standing on the capsule frees the rest of the half; bounded by the distance condition. Compliance: public API only.

### V4-B. Heavy-carrier safety with the belief (attacker)
- **Where**: `attack_core` 1802–1804 and 1837; `food_is_safe` 1917–1919; `goal_open` 1374–1395.
- **Change**: (a) `enough = True` when carrying ≥ 12 regardless of open_goal; (b) when carrying ≥ `return_at`, `goal_open` uses quantile 0.2 and additionally requires the belief support of every hidden non-scared ghost to be ≤ 40 cells; (c) for carrying ≥ 5, `food_is_safe(f)` with `depth[f] > 0` adds an exit race against hidden ghosts at their 0.1-quantile distance to `entrance[f]`: `d_q(g, entrance) > d(pos, f) + depth[f] + 1`.
- **Why**: item 6; the planner only sees hidden ghosts within 7 by argmax. The tracker's timidity (E-007) came from applying hidden ghosts to *all* food; restricting to heavy carriers caps the downside.
- **Expected**: food lost −0.3…−0.5/game in the pool, −1…−2 vs double attackers; returned nearly unchanged. **Test**: food lost, deaths, max carry, returned; vs feature/exploit_v2 for timidity. Cost: O(belief × food) per move, < 5 ms.

### V4-C. Let the breaker run under the planner (v4-specific; diagnosis-driven)
- **Where**: `attack_core` 1823–1827.
- **Change**: after `plan_move`, if the planner's `best_value < 0.5`, we are a ghost, carry 0 and a non-scared ghost is visible: `self.blocked.append(True)` instead of `False`, and if `sum(self.blocked) >= standoff_moves` call `break_standoff` (with V5-E's entry choice) and prefer its move.
- **Why**: item 1 [verified]. Expected sign unknown: E-034's override result (+0.06, with the breaker active) is the only hint that letting greedy's standoff logic run helps; vs camper it was −0.06. **Test**: attacker standoff moves (70/game), share of games with < 30 attacker Pacman moves (5.2 %), PPG vs camper/greedy_v3/lab5_smart vs feature/exploit_v2. Cost 0.

### V4-D. Two-pronged entry on a long standoff (bold; SM-4 with a strict trigger)
- **Where**: `RoleAgent.role_of` 2333–2347 plus a `standoff_since` field the attacker writes into `TeamMemory`.
- **Trigger** (all): attacker on our side, carry 0, non-scared enemy ghost visible within 3 for ≥ 25 consecutive own moves; both enemies are ghosts (`fields` is_pacman False); our food count unchanged over those moves; score ≤ 0; not `late`. **Action**: the defender attacks with `entry` fixed to the border cell across from the maze opening farthest (along the corridor) from the attacker's opening; it reverts to defend the moment any enemy `is_pacman` is True, our food drops, or after 40 own moves.
- **Why**: a shadow/camper guard can mirror one raider; the un-shadowed one has race-safe food. 10.8 % of pool games are held-at-border games (PPG 1.2/2.0); the 0–13 replay had 0 Pacman plies.
- **Honest prior**: `raid` (E-018/E-020), `lead0/lead5` (E-029, −0.76/−1.05) and `power` (E-030, −0.23) all lost with broader triggers and without the flags-based instant recall. Expected gain small and uncertain; test on the shadow-guard opponents first and stop if feature/exploit_v2 regress. Cost: a few ms.

### V4-E. Run the built-but-untested `plan_models='m1m2'` arm (cheap)
A league entry with `plan_models=m1m2`, `plan_nodes=1200` (two searches share the 0.3 s clock) addresses the "hold when far" blind spot (item 8). Risk T-60 (min over models makes it timid): watch returned and standoff moves. Zero build cost.

---

## 5. Proposals for greedy_v5 (override mechanism)

### V5-A. Restore the all-die guard in the override path
- **Where**: `attack_override` 1779 (v5: 1787).
- **Change**: `if action is None or action == g or info['best_value'] < self.cfg.plan_min: return g`.
- **Why**: items 3–4 [verified]: without it, v5 replaces greedy's `evade` by the planner's cheapest in-model death (walking into the ghost) whenever every continuation dies in the model. Expected: identical to v5 except in trapped states; deaths and food lost should not rise and may fall against exit-holding defenders (ours, choke). **Test**: identity run vs v5 on 3 seeds (should differ in a few games only), then deaths/food lost paired vs v5 on tuning seeds. Cost 0.

### V5-B. Asymmetric margin
- **Where**: 1784 (v5: 1792).
- **Change**: `margin = plan_margin if rv.get(g, -1e9) >= 0.0 else 0.1`.
- **Why**: the 0.3 margin protects greedy's food sequencing where both options are fine (the reason `full` mode lost 0.38); when greedy's own subtree is negative, its continuation loses food, and a 0.1–0.3 better planner line is a real escape, not a sequencing quibble. **Test**: deaths, food lost, returned; add a local-only override counter (`plan_uses` already exists, 1785) to confirm the override rate rises only in negative states. Cost 0.

### V5-C. Commitment / hysteresis for overrides
- **Where**: `attack_override`; store `(next_cell, ghost_cells)` of the overriding line in `self.plan_info`.
- **Change**: on the next move, if we stand on the stored next cell and the modelled ghosts moved ≤ 1 cell each, apply margin 0 for the stored line's next action; otherwise the normal margin.
- **Why**: item 7 — greedy and the planner can alternate (toward food / away) because `g` is recomputed from scratch and the breaker's `entry` persists. **Test**: count immediate reversals of the attacker's direction while a ghost is within 7 (needs a small local diag); returned and standoff moves. [untested] Cost 0.

### V5-D. Wider trigger in override mode only
- **Where**: 1774 (v5: 1782).
- **Change**: also run the planner when `carrying >= 5` and a non-scared modelled ghost is within 10, or when greedy's next cell has `depth > 0` and a modelled ghost is within 10.
- **Why**: override keeps greedy by default, so a wider trigger costs only compute (≈ +30 % planner calls; p99 0.12 s now). E-034's flat `t9` was for *danger* mode, where the trigger changes who decides. Targets the heavy-carrier dead-end deaths of item 6. **Test**: food lost, deaths, p95/max move time. [untested]

### V5-E. Gap-aware breaker entry (matters more in v5, where the breaker actually runs; also V4-C's companion)
- **Where**: `break_standoff.away()` 1898–1902.
- **Change**: define for each border cell `b` its opening `gap(b)` = first enemy-side cell beyond `cross[b]` on the shortest path to the nearest enemy food; score `lead(b) = min_g d(g, gap(b)) − (d(pos, b) + d(b, gap(b)))`; choose the best `b` only if `lead ≥ 1`, else Stop at the current opening (do not walk the corridor).
- **Why**: item 2 [verified]: the corridor walk never gains a step against a mirroring guard. **Test**: attacker standoff moves, Pacman moves, PPG vs camper/greedy_v3/lab5_smart. Cost: one BFS per border cell per game (precompute in `register_initial_state`).

---

## 6. Ranking (expected gain ÷ cost) and test order

| rank | proposal | versions | cost | evidence quality | expected |
|---|---|---|---|---|---|
| 1 | V5-A all-die guard | v5 | 1 line | mechanism verified | small +, removes a v4→v5 divergence |
| 2 | V4-A scared defender + capsule denial | both | ~40 lines | mechanism verified in 2/2 replays; 0.49 defender deaths vs rusher | + on conceded (largest loss bucket) |
| 3 | V4-B heavy-carrier safety | both | ~30 lines | one verified death; food-lost data | + on food lost; watch timidity |
| 4 | V5-B asymmetric margin | v5 | 1 line | reasoning | small + |
| 5 | V5-E gap-aware breaker (+ V4-C for v4) | both | ~40 lines | standoff mechanics verified; sign untested | uncertain |
| 6 | V4-E m1m2 arm | both | 0 | untested arm | uncertain; T-60 risk |
| 7 | V5-D wider trigger | v5 | 5 lines | untested | small |
| 8 | V5-C hysteresis | v5 | ~20 lines | untested | small |
| 9 | V4-D two-pronged entry | both | ~80 lines | three prior negatives | high variance |

Suggested order: (1) `greedy_v5b` = v5 + V5-A, identity-check vs v5 (expect a handful of differing games), screen paired vs v5 and v4 on 40 tuning seeds with the pool; (2) a `lab12` file on top of v4 with switches `def_scared`, `def_capsule`, `heavy_safe`, `gap_entry`, `plan_blocked`, `margin_asym`, `trigger_wide`, screened as single switches against v4 (danger) and v5 (override) on the same seeds; only switches with positive point estimates go to a combination; (3) validation on unused `validation2` seeds (81–160) against the 8-member pool under the accept rule. Diagnostics to read per switch: conceded, defender deaths, attacker food lost, attacker standoff moves, share of games with < 30 attacker Pacman moves, 28-finishes, p95/max move time. All proposals are stdlib-only, deterministic, within the 1 s budget (V4-E/V5-D add compute but stay under the 0.3 s planner clock) and read nothing beyond the public API and the already-switched hidden fields.

---

## 7. Ideas considered and rejected

- Comparing the planner's best against a *rollout* of greedy's policy (instead of `root_values[g]`): max-backup vs a single line always favours the planner, so it collapses override into danger mode (E-034: −0.38 for always-plan).
- Raising `plan_death` or rescaling the leaf's death pricing: masked by max-backup except in all-die states, which V5-A handles.
- Per-map chokepoint detection: the border is a corridor open over most rows on every generated map; the relevant structure is the maze openings (V5-E), not entries.
- Pre-shadowing the enemy attacker before it crosses: T-56 (our defender reveals the guard to our attacker; 0-0 vs baseline in E-019).
- MC-2 race leaf, LF-1 smoothed table: the quadratic leaf already equals the net (E-033); only informative.
- MC-3 scenario re-check of IW's top nodes: the same scenario ghosts made every MC arm timid (T-60).
- GM-1 ghost model calibration from replays: sound, but all available opponents are ours; calibrating on them tunes to our pool.
- JX-1 macro-IW over junctions: large build; the probe shows IW(1) already explores the whole reachable home side (≈ 100 nodes) in standoffs — the limit is the model/leaf, not the horizon.
- Retuning `return_at`, `threat_dist`, `plan_trigger`, `plan_h`, `plan_min`: flat optimum (E-007/E-010/E-034).
- Scared-ghost hunting, focus modes, defender planner, second-iteration nets, formation lead/power: tested and rejected (agents.md).
