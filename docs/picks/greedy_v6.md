# greedy_v6: current submission (since 2026-11-12, E-046; user decision)

`teams/greedy_v6.py` = `teams/greedy_lab_v16.py` with the `lab16_c2` options as defaults (identity 16/16 recorded games vs `lab16_c2`, E-046). `my_team.py` was a byte-for-byte copy until 2026-11-21; since then it has the same code with a short header and without version / experiment tags in the comments (syntax tree identical to `teams/greedy_v6.py`, E-048). The full history of every option is in the header of `teams/greedy_v6.py`. (`greedy_v5` was a rejected candidate, E-038, and was never the submission.)

**In one line**: greedy_v4 plus a **team brain** shared by both agents, with two plays: the attacker stops waiting for ghosts that only our defender can see (`eyes`), and when the attacking body dies the body already at the border takes over the attack (`relay`).

**Release gate: not run.** The locked test seeds and the held-out teams were not used for this version (one use of the test seeds is left; the user's call).

## Mindset

- Everything greedy_v4 does stays: the rule-based greedy team with lab5_smart's enemy-state switches, and the width-based planner with the learned leaf value near ghosts. See [greedy_v4.md](greedy_v4.md).
- **The two agents now know what the other is doing.** One `TeamBrain` object is shared by both. Every turn each agent posts its role, the rule it used, how long it has been idle, its entry, target and load; the brain keeps the team situation (invaders at home, defender scared, attacker raiding / idle / dead, clock and score) and one latch that both agents read, so a role change is always seen by both.
- The brain by itself changes no move (896/896 screen games identical to greedy_v4, E-044). Only the two plays below do.

## Play 1: `eyes` (whose sight is it)

- Sight is shared in this game: our attacker sees every enemy within 5 of *either* of our agents. In greedy_v4 a ghost that our defender saw far away counted as a threat for the attacker's greedy safety checks, and the attacker waited at the border (trap T-56).
- Rule: in the attacker's greedy safety checks (`dangerous_ghosts`: safe food, safe way home, standoff count) a visible ghost is dropped when it is more than Manhattan 5 from the attacker, more than `eyes_maze` = 10 maze steps away, and has not been in the attacker's own sight during its last 8 moves.
- The planner is untouched: it still models that ghost from the shared belief.
- No role changes. Fires on 35–39 attacker moves per game, in about 90 % of games.

## Play 2: `relay` (prepare for the attacker's death)

- The brain detects that the attacking body was eaten (it jumps to its start cell).
- The two home roles are swapped when the other body is at least 8 steps nearer the border and has no invader within 6, and home is quiet; or the other body is scared for 8 or more moves (the respawned body is then our only unscared ghost); or the respawned body is nearer the likeliest invader.
- The body at the border attacks at once; the respawned body defends from where it stands. There is always exactly one attacker and one defender. The roles are looked at again only at the next respawn.
- Fires 0.20 times per game, in about 17 % of games.

## Attacker and defender

Decision lists as in [greedy_v4.md](greedy_v4.md) (special cases, planner near ghosts, greedy rules; intercepting / shadowing defender; endgame roles), with the two changes above. Both agents are `BrainAgent` objects (a subclass of greedy_v4's `RoleAgent`).

## What changed from greedy_v4

| change | from | evidence |
|---|---|---|
| team brain (posts, situation, play latch) | E-044 | changes no move alone: 896/896 games identical |
| `eyes` | E-044 | alone, validation3 1–80: pool +0.031 [+0.006, +0.057], last-year 14 +0.061 [+0.033, +0.091] |
| `relay` | E-044 | alone, screen: pool +0.062 [+0.002, +0.138], last-year 7 +0.020; on top of eyes (validation3 1–80): pool −0.012 [−0.042, +0.017], last-year +0.017 [+0.002, +0.032] |

## Evidence (all paired with greedy_v4 on the same opponent, seed and colour)

- **Decision + confirmation runs** (E-044, validation3 seeds 1–80, 3,520 games of this configuration): pool (7) **+0.020 [−0.019, +0.062]**, last year's 14 teams **+0.078 [+0.052, +0.104]**, head-to-head vs greedy_v4 **56-51-53**; every pool member within ±0.08; 0 crashes / time warnings / violations; max move 0.220 s. Decision rule: pool guard + last-year gain (user, 2026-11-11).
- In games, against last year's 14 teams (2,240 games): 1960-178-102 → **2038-118-84** (win rate 87.5 % → 91.0 %); 0-0 ties 138 → 87; deaths per game unchanged; food returned +1.0 per game. Against the pool (1,120 games): 907-76-137 → 919-62-139.
- Attacker idle moves per game 40 → 28, evade moves 14 → 8 (screen 2 counters, E-044).
- The second validation block was about half the first (last-year +0.106 → +0.049) and both are below the screen (+0.114): quote the 80-seed numbers.
- **Diagnostic** vs four friend teams (E-044, tuning 365–394, 240 games; not a decision input): +0.092 [−0.037, +0.229]; no team worse.
- **Promotion checks** (E-046): `eval/check_rules.py` OK; `my_team.py` identical to `lab16_c2` in 16/16 recorded games; smoke 48 games 37-3-8 with 0 crashes / warnings / violations, max move 0.251 s; Linux / Python 3.8 with real time limits and the CPU saturated: 60 games, 46-8-6, 0 crashes, 0 time warnings, max move 0.326 s, worst p95 0.281 s, max startup 4.5 s.
- **No rule profile** (`trace_game.py profile`) was made for this page: the run was stopped on the user's instruction ("no need to test anything anymore", 2026-11-12). The counters above come from the validation runs.

## Parameters

| parameter | value | where |
|---|---|---|
| relay, eyes | 1, 1 (the brain is on when a play is on) | `V6_DEFAULTS` |
| EYES_MAZE (`eyes_maze`), EYES_MEMORY | 10 maze steps, 8 own moves | constants / `V6_DEFAULTS` |
| RELAY_NEARER, RELAY_BUSY, RELAY_SCARED | 8, 6, 8 | constants |
| planner and greedy parameters | as greedy_v4 (plan=danger, plan_v=2, plan_nodes=2000, plan_budget=0.3 s, plan_leaf=netf; return_at 8) | `V6_DEFAULTS`, `create_team` defaults |
| other plays in the file (`push`, `relief`, `swap`, `cover`, `pocket`, `cash`) | off | `V6_DEFAULTS` |

## Known blind spots

- **Not through the release gate**: no locked test seeds, no held-out teams. The gain was measured on our pool and on last year's public entries, which the plays were also screened against.
- **The mirror is even**: against greedy_v4 itself it is 56-51-53. The gain is against teams that stand off at the border, not against our own family; the pool gain's interval includes 0.
- **`eyes` trusts that an unseen-by-me ghost is far**: a ghost more than 10 maze steps away that closes in is seen again by the attacker's own sight (Manhattan 5) only late. Deaths did not rise in 3,520 games, but an opponent that intercepts from far away is the case to watch.
- **`relay` leaves the shadow post empty** for the moves the respawned body needs to reach it; games with two or more swaps were slightly negative in screen 1 (−0.2, 29 games).
- **Big loads lost in dead ends** (E-045) are unchanged from greedy_v4: about 3 % of games; four restrictions aimed at it have failed.
- Everything listed for greedy_v4 (timing on a slower cluster, the ghost model, double attackers) still applies. `trace_game.py` labels a `BrainAgent` defender's walk to its last evidence as "eat".
