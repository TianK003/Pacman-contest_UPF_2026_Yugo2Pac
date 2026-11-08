# Top picks: every version that has been our submission

One page per version that has been in `my_team.py`. Each page explains the version's behaviour rule by rule ("mindset", decision lists, parameters), what changed from the previous pick, the evidence that it was better, and its known blind spots. The rule names match the decision trace (`eval/trace_game.py`, E-022), so any move in any game can be looked up.

| version | file | in `my_team.py` | accepted on | page |
|---|---|---|---|---|
| greedy_v4 | `teams/greedy_v4.py` | since 2026-11-08 (E-032) | validation 221–260: +0.95 [+0.78, +1.13] vs greedy_v3, +0.58 [+0.42, +0.74] vs lab5_smart (E-031); release gate open | [greedy_v4.md](greedy_v4.md) |
| greedy_v3 | `teams/greedy_v3.py` | 2026-10-18 (E-021) → 2026-11-08 (E-032) | validation +0.16 [+0.04, +0.28] vs greedy_v2 (E-019); test seeds +0.26 pool / +0.17 held-out (E-021) | [greedy_v3.md](greedy_v3.md) |
| greedy_v2 | `teams/greedy_v2.py` | 2026-10-18 (E-013) → 2026-10-18 (E-021) | validation +0.42 vs greedy, twice (E-011, E-012) | [greedy_v2.md](greedy_v2.md) |
| greedy (v1) | `teams/greedy_v1.py` | 2026-10-16 (E-003) → 2026-10-18 (E-013) | provisional: best of the first league, 40/40 vs the baseline (E-002, E-003) | [greedy_v1.md](greedy_v1.md) |

**Rule**: every promotion to `my_team.py` adds a page here, built from the code and a rule profile (`trace_game.py profile`). Every team ever built, including rejected ones, is listed in [../agents.md](../agents.md).

## How to see why an agent did something

`eval/trace_game.py` (local analysis only, never submitted) plays a game with `eval/trace_team.py` wrapped around one of our teams. The wrapper records which rule produced every move. It passes every call through unchanged: traced games end with exactly the scores the evaluation recorded (60/60 games across the three picks, E-022).

```powershell
# one game, move by move (filter with --from/--to own moves, --agent attacker|defender), plus a replay
venv\Scripts\python.exe eval\trace_game.py game --team submission --vs camper --seed 72943214 --colour red --from 20 --to 40
# watch that replay (from pacman-contest\src\contest); the trace's "ply" counts agent moves from 0
..\..\..\venv\Scripts\python.exe capture.py --replay=..\..\..\eval\traces\submission_vs_camper_72943214_red.replay --delay-step 0.1
# how often each rule fires, over many games (tuning seeds only; test seeds are refused)
venv\Scripts\python.exe eval\trace_game.py profile --team greedy_v3 --vs greedy feature camper rusher choke exploit_v2 --seeds tuning --seed-offset 580 --n-seeds 20 --by-opponent
```

### Rule names in the trace

| agent | rule | meaning |
|---|---|---|
| attacker | `eat` | walking to the nearest food it reaches before every visible ghost |
| attacker | `home` | carrying food and a go-home condition holds (the reasons are listed); while a ghost is close, a capsule also counts as an escape |
| attacker | `evade` | no safe path home (or none at all): stepping away from the nearest ghost; "cut off" when it is not even trying to go home |
| attacker | `blocked` | on our side, a ghost blocks every safe food: waiting at the border (counting towards the standoff breaker) |
| attacker | `switch-entry` / `entry` | standoff breaker (v2+): chose / is walking to the border entry farthest from the ghosts |
| attacker | `capsule` | standoff breaker (v2+): going for a capsule it reaches first |
| attacker | `no-safe-food` | v1 (no breaker): no safe food, so it heads back to the border and waits |
| defender | `chase` | going straight at a visible invader |
| defender | `cut-off` / `hold` | intercept (v2+): going to / holding the cell on the invader's way home that it reaches first |
| defender | `scared` | our defender is scared (they ate our capsule): keeping 3 steps from the invader |
| defender | `last-evidence` | going to where our food just vanished (or an invader was last seen) |
| defender | `shadow` | v3: waiting at the border entry across from where the raider most likely is |
| defender | `patrol` | cycling through the 3 border cells nearest the middle of our remaining food |
