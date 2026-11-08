# Proposals: shared-mind tactics and team learning

Ideas proposed but not yet built, with the reasoning behind each, what it targets and how we would test it.
- When a proposal is built, it moves to the heuristics/methods files and gets an experiment ID.
- When it has been tested, its result also goes into [agents.md](agents.md).

**IDs**: shared-mind tactics `SM-##`, learning options `RL-##`.
**Status**: `idea` → `planned` → `built` → `tested` → `adopted` | `rejected`, each change with an experiment ID (README conventions).

First written 2026-10-28 (user request).
- A row's *use for our game* is `[untested]` unless it cites an experiment.
- The literature behind the rows (a research agent, 2026-10-28, which opened every source) is in section 6. Its numbers come from other games (RoboCup, Ms Pac-Man, hockey, StarCraft), so their transfer to ours is untested.

---

## 1. The idea: one team brain with two bodies

Shared memory between our two agents is allowed [source: professor, rules.md Q4, 2026-10-22].
- Without it, each agent decides alone and has to guess what its teammate will do.
- With it, the two agents can be run by **one team brain**: a single object, created in `create_team`, that sees what either agent sees and plans for both.
- Each agent's `choose_action` then executes the brain's current plan for that body, updated with the freshest observation.
- All computation still happens inside our own `choose_action` / `register_initial_state` calls (no threads, rule 2).

**Theory** [source: Oliehoek & Amato 2016, §2.4.3 and §8.3.1.2]:
- With instant, free, noise-free sharing, a decentralised POMDP (Dec-POMDP) reduces to a *multiagent POMDP*: one "puppeteer" picks joint actions from a joint belief. Sharing every local observation at each step is then optimal.
- That is also the cheaper problem class: finite-horizon Dec-POMDPs are NEXP-hard even for two agents, while a POMDP is PSPACE-complete [source: Bernstein et al. 2002].
- For us [untested]: the game becomes a two-team zero-sum partially observable game in which our team is **one player**. It can plan over 5 × 5 = 25 joint moves from the shared belief. A centralised policy grows exponentially with the number of agents, which does not matter for two.

What the team brain can know:

| information | available because | status |
|---|---|---|
| every enemy within Manhattan 5 of **either** agent | the engine already pools sight (T-23) | [verified] |
| both agents' sonar readings each round | shared memory (Q4) | [verified E-025]: a shared belief halves the tracking error (most likely cell 4 → 2 steps from the truth) |
| exactly one enemy moved between our two agents' turns: `(index − 1) % 4` | fixed turn order (`game.py`) | [verified] (H-S15) |
| each enemy's side, food carried and scared timer, even when hidden | hidden fields (Q3) | [verified E-023]; side detection 58% → 100% correct (E-025) |
| exact respawn windows (an eaten enemy is behind its prison corridors) | respawn detection + map | [verified] engine facts (heuristics.md A0, H-S14) |
| both agents' plans and targets | shared memory | by construction |

---

## 2. Shared-mind tactics

Columns: what it exploits, which measured weakness it targets, cost, risk, and how it would be tested. "Success" for every row is first a positive screen against the reference pool, then the accept rule of evaluation.md section 2 on validation seeds. The "sign it works" column is the diagnostic we would check to see *why*, never a decision input.

| ID | tactic | how it works | shared information used | weakness targeted (evidence) | sign it works | effort | risk | status |
|---|---|---|---|---|---|---|---|---|
| SM-1 | **Team brain** | One object sets roles, targets and entries for both agents each turn, and does the map analysis once (H-M11) | everything | needed by every row below | `lab_off`-style identity with all tactics off | medium | low (structure only) | idea |
| SM-2 | **Shared belief** | One belief per enemy, updated at both agents' turns: spread only the enemy that just moved; apply both agents' sonar; a vanished food pins that enemy exactly | sonar, sight, food events | defender's tracking (E-019: median error 4) | belief error | — | — | **built** (`shared`, E-025): error 4 → 2, truth never ruled out; screen pending |
| SM-3 | **Power play** | After we kill an enemy (it is in its prison for a known number of moves) or eat their capsule (exact scared timer), the defender joins the attack and comes back before the window closes | respawn detection, exact timers, belief | raids by the defender gained against guards and lost the same against attackers (E-018, E-020); a known window removes the attackers | food returned per game rises; food conceded does not rise | low | medium | **built** as `formation='power'` (`lab7_power`, teams/greedy_lab_v7.py); screen E-030 |
| SM-4 | **Decoy / two-entry overload** | Agent A shows itself at entry X; the enemy guard shadows A (visible in the shared belief); agent B crosses at a far entry Y | belief of their guard, both positions | 0–0 standoffs (18% of lost points, E-014); 25% of attacker moves are walks between entries (E-022) | fewer standoff moves, more Pacman moves | medium | medium | idea |
| SM-5 | **Spotter** | Before the attacker picks an entry, the defender stands where it reveals the enemy guard; the attacker then crosses where the guard is not | pooled sight | T-56 (our defender showing the guard to our attacker made it wait) turned into an advantage; entry walks (E-022) | fewer `entry` / `blocked` moves in the trace profile (E-022 tool) | low | low | idea |
| SM-6 | **Border bait-and-trap** | A chased carrier runs home past our teammate waiting just inside our border; a chasing ghost that crosses becomes a Pacman next to our ghost and is eaten | both positions, the chaser's position | carriers chased home by a ghost; how often a chaser follows across the border is **not measured** (E-014 found most deaths inside dead ends, a different case) | kills of chasers on our side | low | low (only fires if they chase across) | idea |
| SM-7 | **Distraction escort** | When our attacker is cut off, the teammate crosses near the blocking ghost; a ghost can chase only one of them | positions, belief | 12% of attacker moves are "cut off" (E-022) | fewer `evade` moves; fewer deaths with food | medium | medium | idea |
| SM-8 | **Two-ghost pincer / cover** | When both defend: maximise the cells we reach before the invader (cover pursuit, H-S19), or take the front and back exits of its corridor (H-S25) | shared belief, both positions | defence = 29% of lost points (E-014); double attackers (friend_aljaz_1, heldout_a) | kills per invasion; food conceded | medium | low | idea |
| SM-9 | **Formation selector** | One rule picks attack + defend / double attack / double defend / power play / decoy from enemy-Pacman count, score, time, carried food and respawn windows, with hysteresis | everything | generalises `recall` + `endgame` (E-025) and SM-3; H-S26 | points against both guard-type and attack-type teams | medium | medium (role flapping, H-S08) | idea |
| SM-10 | **Split targets** | When both attack: different food clusters and entries, by assignment | both plans | the two agents duplicating each other | fewer shared targets | low | low | idea |
| SM-11 | **Plan broadcast** | Each agent posts its next k cells; the teammate avoids blocking it in corridors and knows what will be revealed | plans | corridor collisions; surprise reveals (T-56) | — | low | low | idea |
| SM-12 | **Pooled thinking time** | A search started in one agent's turn is continued in the other's turn (anytime, inside each `choose_action`) | the team brain's search state | makes local adversarial search (M-05) fit the 1 s budget | deeper search at the same move time | high | medium (timing, rule 1) | idea |
| SM-13 | **In-game play selector** (from the literature search) | A small playbook (standard, raid-when-quiet, double attack, double defence, power play), each with applicability conditions. A "sleeping experts" bandit reweights a play each time it ends: ×3/2 on success, ×2/3 on failure. Reward = food returned minus food lost while it ran. Switching is damped, and roles are kept when the play changes | the whole team state | the raid gained against guards and lost the same against attackers (E-018, E-020); the team would learn *during the game* which play pays against this opponent | the play weights move to the play that scores; points against both guard-type and attack-type teams | medium | medium: maybe too few play decisions per game to converge [untested] | idea |

Evidence from the literature (section 6 has the links):

| ID | what the sources report | transfer to our game |
|---|---|---|
| SM-2, SM-5 | Ms Pac-Man vs a partially observing ghost team: no communication 17,257 points; an "I saw her" broadcast 5,769 (33%); fully observing ghosts 3,896. Keeping a sighting ~50 ticks was best [source: Williams et al. 2016] | sharing sightings is worth a lot; our E-025 probe already shows the belief gain (4 → 2 steps) [verified] |
| SM-3 | NHL 2008-09 goals per 60 min: 5-on-5 2.37, 5-on-4 6.54 (×2.8), 5-on-3 18.97 [source: Buttrey et al. 2011] | analogy only [untested] |
| SM-4 | Deception has a "last deceptive point"; two ways to deceive: show a false goal, or hide the real one. No game results reported [source: Masters & Sardina 2017] | no CTF write-up measures two-entry attacks (gap) |
| SM-8 | A 4-cycle is not cop-win: one pursuer cannot guarantee a capture [source: cop-win graphs]. In Ms Pac-Man work a "pincer" means every escape path blocked; the MCTS ghost team NQKIEN won CEC'11 [reported]. A Melbourne CTF write-up rewarded both agents for a trapped invader [reported: Sharma ~2020] | two defenders needed on loops [untested] |
| SM-9, SM-13 | Flexible positions plus set plays beat a rigid team: 34 wins and 3 ties in 38 games [source: Stone & Veloso 1999]. Hysteresis in every switching condition, roles kept across play switches; 4th of 24 at RoboCup 2005 [source: McMillen & Veloso 2006]. A playbook whose weights moved to the scoring play within a single game: RoboCup 2002 quarter-finals, American Open '03 champions [source: Bowling, Browning & Veloso 2004] | no numbers exist for the effect of hysteresis alone (gap) |
| SM-12 | Tree reuse between moves under a 40 ms limit; 2nd at WCCI'12, 1st at CIG'12 (abstract only, no ablation numbers seen) [source: Pepels, Winands & Lanctot 2014] | — |

Relation to earlier work:
- SM-3 meets the retest condition that agents.md set for defender raids ("coordination through shared memory is built").
- SM-8 builds on the research entries H-S19 (cover pursuit) and H-S25 (pincer) in heuristics.md Part D.
- SM-9 is the general form of E-025's `recall` and `endgame` switches. **First evidence (E-025)**:
  - `recall` ("two enemy Pacmen → our attacker defends") **loses** −0.58 against `double_attack` and −0.40 against `friend_aljaz_1`.
  - It cuts our returns by a third and barely reduces theirs.
  - So a formation selector must not answer a double attack with a double defence: their half is empty, so racing pays.
  - `endgame` is neutral (+0.006).

---

## 3. Learning options (RL and tuning)

With one team brain, the team is in effect **one agent with two bodies** (section 1). The usual multi-agent machinery is then less needed:
- QMIX, VDN and MAPPO exist so that policies trained together can still run separately [source].
- DIAL and CommNet learn the messages themselves [source].
- With shared memory, sharing every observation is already optimal [source: Oliehoek & Amato 2016], so a learner can choose joint actions directly [untested].

**Lesson from keepaway** [source: Stone, Sutton & Kuhlmann 2005]:
- RL over macro-actions (SMDP Sarsa(λ)) reached 9.6–11.1 s of ball possession after 25 hours of training.
- The hand-coded policy got 9.6 s when tuned and 8.2 s untuned. Tuning just two of its parameters (about 30 combinations) matched the learned policy.
- **Tune before learning**: RL-1 before RL-2.

| ID | method | what is learned | what it needs | fit |
|---|---|---|---|---|
| RL-1 | **Black-box tuning** [tooling built 2026-11-08: `eval/rl/cmaes_tune.py`; runs E-031] (CMA-ES or random search, M-02 / M-11) of the team brain's thresholds: power-play margins, decoy distances, recall and endgame rules, SM-13's multipliers | about 5–15 numbers | ~1,000s of harness games on tuning seeds (~2,500 games per hour per process, E-009); shipped as constants or a data file (Q6). Reported: CMA-ES tuned 14 of 40+ RoboCup 3D parameters with 210,000 evaluations in under a day on a cluster, and fitness on tasks resembling real play worked better; that team then won 24/24 games, 136–0 [source: MacAlpine et al. 2012] | **first step**: cheap, low risk |
| RL-2 | **Learned formation selector**: a contextual bandit or tabular Q-learning over a small abstract state (score, time, enemy Pacmen, carried food, respawn window), choosing SM-9's formation every N moves | a small table | ~10k games against the pool; a data file (Q6) | good; medium effort. Overfitting risk (T-37): validate on fresh seeds and check the held-out teams |
| RL-3 | **Joint value function for search** [first version built 2026-11-08: a 12-16-1 value net for the width planner's leaves, trained on greedy games (E-030 `lab7_danger_net`)]: a learned evaluation, distilled from a slow offline search (M-13) | evaluation weights | a fast simulator of the rules | stretch |
| RL-4 | **Deep multi-agent RL** (MAPPO, QMIX; M-08) | a whole policy | a fast simulator, maybe numpy (Q2: on request), millions of steps | stretch; with shared memory the multi-agent parts add little |
| RL-5 | **League with exploiters** around any learned part (evaluation.md section 5) | — | our existing league tooling. Reported: plain self-play forgets and cycles, exploiter agents expose the main agent's flaws [source: Vinyals et al. 2019, AlphaStar] | required with RL-2 or RL-4 |
| RL-6 | **In-game bandit** (SM-13): learns within one game which play pays, no training games | play weights, reset every game | nothing offline; within-game memory only (not Q11's across-game memory) | medium; may not converge within 300 moves [untested] |

---

## 4. Open question (not ours to decide)

- **Memory across games**: keeping what we learned about an opponent in memory from one game of a match to the next (never in files; rule 6 forbids writing files).
  - Whether the tournament plays several games in one process is unknown, and whether this is allowed is a ruling.
  - Recorded as **Q11** in [rules.md](rules.md). Not to be used until it is answered.

---

## 5. Suggested order

| step | proposals | why first |
|---|---|---|
| 1 | SM-3 power play, SM-5 spotter | cheap; each targets a measured loss (raids, entry walks) |
| 2 | SM-4 decoy, SM-6 bait-and-trap | the standoffs and carrier deaths |
| 3 | SM-9 formation selector, or SM-13 in-game play selector over the plays of steps 1–2; thresholds tuned with RL-1 | only after E-025 shows whether `recall` / `endgame` help. SM-13 is the literature's best-supported cheap option, and it attacks the raid problem directly |
| 4 | RL-2 learned selector | only if SM-9 / SM-13 show gains, and only after RL-1 (the keepaway lesson) |

All of them need SM-1 (the team brain) first, built so that it plays exactly like the incumbent with every tactic off.

---

## 6. Sources (research agent, 2026-10-28; every one opened, unless marked)

| key | link |
|---|---|
| Oliehoek & Amato 2016, *A Concise Introduction to Decentralized POMDPs* | <https://www.khoury.northeastern.edu/home/camato/publications/OliehoekAmato16book.pdf> |
| Bernstein, Givan, Immerman & Zilberstein 2002 (Dec-POMDP complexity) | <https://people.cs.umass.edu/~immerman/pub/bgizAbs.html> |
| Boutilier 1996 (MMDP) | <https://www.cs.toronto.edu/~cebly/Papers/tark96-abs.html> |
| Gupta, Egorov & Kochenderfer 2017 | <https://ala2017.cs.universityofgalway.ie/papers/ALA2017_Gupta.pdf> |
| Bowling, Browning & Veloso, ICAPS 2004 (playbook selection) | <https://icaps04.icaps-conference.org/icapspapers/ICAPS04BowlingM.pdf> |
| Tavares et al., AIIDE 2016 (StarCraft strategy selection) | <https://ojs.aaai.org/index.php/AIIDE/article/view/12857> |
| Stone & Veloso, AIJ 1999 (locker-room agreements, formations) | <https://www.cs.utexas.edu/~pstone/Papers/99aij/node23.html> |
| McMillen & Veloso, RoboCup 2006 (plays with hysteresis) | <https://mcmillen.dev/papers/McMillen-2006-RoboCup-final.pdf> |
| Buttrey, Washburn & Price, JQAS 2011 (NHL scoring rates) | <https://faculty.nps.edu/awashburn/docs/EstimatingNHLScoringRates.pdf> |
| Cop-win graphs | <https://en.wikipedia.org/wiki/Cop-win_graph> |
| Pepels & Winands, CIG 2012 | <https://dke.maastrichtuniversity.nl/m.winands/documents/CIG2012_paper_106.pdf> |
| Sharma, COMP90054 write-up (~2020) | <https://abhinavcreed13.github.io/projects/ai-team-pacamon> |
| Masters & Sardina, IJCAI 2017 (deceptive path-planning) | <https://www.ijcai.org/proceedings/2017/610> |
| Pepels, Winands & Lanctot, IEEE TCIAIG 2014 (abstract only) | <https://cris.maastrichtuniversity.nl/en/publications/real-time-monte-carlo-tree-search-in-ms-pac-man/> |
| Williams, Perez-Liebana & Lucas, CIG 2016 | <https://arxiv.org/abs/1609.02316> |
| MacAlpine et al., AAAI 2012 (CMA-ES team tuning) | <https://ojs.aaai.org/index.php/AAAI/article/view/8317> |
| Stone, Sutton & Kuhlmann, Adaptive Behavior 2005 (keepaway) | <https://www.cs.utexas.edu/~AustinVilla/papers/AB05.pdf> |
| Vinyals et al. 2019, AlphaStar (DeepMind blog) | <https://deepmind.google/en/blog/alphastar-grandmaster-level-in-starcraft-ii-using-multi-agent-reinforcement-learning/> |
| QMIX / VDN / MAPPO / DIAL / CommNet | <https://arxiv.org/abs/1803.11485>, <https://arxiv.org/abs/1706.05296>, <https://arxiv.org/abs/2103.01955>, <https://arxiv.org/abs/1605.06676>, <https://arxiv.org/abs/1605.07736> |

Gaps the search could not fill (unknown, not guessed):
- No Berkeley CTF write-up measures double attacks, capsule-timed plays or two-entry attacks.
- No source gives numbers for the effect of role hysteresis.
- The hockey and cop-number transfers are analogies.
- The Pepels 2014 tree-reuse paper was read as an abstract only.

---

## 7. Added 2026-11-08 (overnight session, E-027..)

| ID | idea | status |
|---|---|---|
| WP-1 | Width-based lookahead (IW(1) / p-IW / novelty best-first) for the attacker near ghosts, over our own forward model (methods.md M-15) | built (`plan*` in lab6/lab7); screened E-028, confirmed/ablated E-030 |
| WP-2 | Planner as veto only (`shield`) / override by margin | built (lab7). Hand leaf: shield never fires, override +0.12 (E-030). Net leaf override: +0.06 [+0.00, +0.12] vs greedy_v4 over 1,440 tuning games (E-034), but **−0.05 [−0.15, +0.05] on validation2 (E-038, as greedy_v5): rejected** |
| WP-3 | Learned leaf value for the planner (greedy policy's Monte-Carlo value, 12-16-1 MLP) — "greedy + RL" | built; **adopted** in greedy_v4 (E-030/E-031/E-032); second RL iteration did not help (X3) |
| WP-4 | Planner-free scared-ghost hunting (`hunt_scared`), to tell lookahead from kill-farming | built (lab7); E-030 |
| MM-1 | Map-mode portfolio + selector from map features (methods.md M-16; the user's "greedy_top_left" idea) | built; **rejected** (E-029: no mode > 0, no selector beats "no mode") |
| MM-2 | Linear food-choice policy (`focus=linear`, `fw_*` weights) tuned by CMA-ES | built (lab6/lab7); CMA-ES tuning not run (the planner track won the CPU) |
| JX-1 | Junction-graph macro-IW (longer horizon), novelty over tactical features, offline privileged-teacher distillation (docs/research/width_planning.md §7.e) | idea |
| MC-1 | Non-deep-learning search (methods.md M-17): flat paired Monte Carlo over enumerated ghost scenarios, open-loop UCT, lookup-table / linear leaves | built; MC search **rejected** (−0.43 … −0.72); quadratic leaf ≈ net (E-033) |
| RL-T | Leaf target horizon: the leaf nets / table predict food banked − dropped within 30 moves, which undervalues safely carried food that `open_goal` banks later (table: carrying 5, ghost far, 6 from home → only +1.5). Try H = 60 or "until banked or dead" as the target | tested (E-034): 60-move target −0.03 [−0.14, +0.08] vs greedy_v4; **closed** |
| MC-2 | Race-analysis leaf with fitted escape probability (logistic fit of "dropped food within 30 moves" on the escape margin) | idea (needs a collection that logs the margin); advisor: modest |
| MC-3 | IW planner + scenario re-check of its best few nodes (E-033 reserve arm): keep IW's line, but price its top-8 nodes against the weighted ghost scenarios | idea; risk: the scenario model made every MC arm timid (T-60) |
| LF-1 | Smoothed (interpolated) lookup-table leaf: a direct test of T-59 (smoothness, not R², is what a max-backup search needs) | idea; the quadratic leaf already ≈ net (E-033), so only informative |
| GM-1 | Ghost model calibrated from replays (how often enemy ghosts chase / intercept / hold, by distance) for the planner and any MC scenario | idea; would address T-60 and greedy_v4's "chase within 6 or hold" blind spot |

