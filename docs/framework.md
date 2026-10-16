# Framework facts and how to run games

Everything here was checked against the engine source (`pacman-contest/src/contest/`, submodule commit `54cd83c`) or by running it. See E-000 in [experiments.md](experiments.md). If the submodule is updated, re-check the facts marked as important.

## Where things are

- **`my_team.py` (repo root)**: our submission. It is currently identical to `baseline_team.py` apart from the header comment.
- **`pacman-contest/`**: git submodule `aig-upf/pacman-contest`. **Never edit it.** The engine lives in `pacman-contest/src/contest/`:
  - `capture.py`: the `GameState` API agents use, `AgentRules` (movement, eating, death, capsules), `CaptureRules` (start, end, time limits) and the CLI.
  - `game.py`: the `Game.run` loop, `AgentState`, `Configuration`, `Grid`, `Actions`.
  - `capture_agents.py`: the `CaptureAgent` base class and its helpers.
  - `distance_calculator.py`: all-pairs maze distances, cached in the module-level `distanceMap`, keyed by walls.
  - `maze_generator.py`: the `RANDOM<seed>` maps. `layouts/*.lay` holds the fixed maps.
  - `baseline_team.py`: the only provided opponent. It is weak (reflex agents).
- **`pacman-contest/src/contest/agents/team_name_*`**: copies of the baseline with old import style. Not useful as opponents.
- **Stale scripts**:
  - `scripts/play.sh` calls `runner.py` with `myTeam.py`.
  - `runner.py` crashes after the game (`KeyError: 'game_id'`) [reported by research run].
  - `scripts/config.sh` points to a different fork.
  - Use `capture.py` directly.

## Game loop and agent lifecycle [verified]

1. **Team loading**: `capture.py` loads each team file **once per invocation**, as its own module object, and calls `create_team(first, second, is_red)`.
   - Both agents of a team live in the same process and can share Python objects [verified E-000].
   - The same agent objects are **reused for all `-n` games** of one invocation [verified E-000].
2. **Game start**: `register_initial_state(state.deep_copy())` runs for each agent, with 15 s each.
   - The base implementation sets `self.red` and computes maze distances.
   - Distances are cached globally per wall layout, so the second agent reuses them.
3. **Turn order**: the starting team is random. Turns cycle through indices 0, 1, 2, 3 from the starter, so red and blue alternate.
4. **Each turn**:
   - `observation = agent.observation_function(state.deep_copy())` builds the observation (`make_observation`: it hides far opponents and adds sonar).
   - Then `agent.get_action(observation)` appends it to `observation_history` and calls `choose_action`.
   - Time spent in both counts towards the move.
5. **Applying the move**: `state.generate_successor(agent, action)`, then the end-of-game checks.
6. **Game end**: `final(state)` is called with the **real final state** (not an observation).

## What an observation contains [verified E-000]

| Item | Visible? | Notes |
|---|---|---|
| Walls (whole map) | yes | `get_walls()` returns the **same object as the engine's** layout walls. Read-only! (T-01) |
| Food on both halves, capsules on both halves | yes | full grids; `get_food` / `get_food_you_are_defending` return new half-grids |
| Score | yes | `game_state.get_score()` is red-positive; `self.get_score(gs)` is relative to our team |
| Time left | yes | `game_state.data.timeleft`: starts at 1200, minus 1 per agent move |
| Own and teammate `AgentState` | yes | position, direction, `is_pacman`, `scared_timer`, `num_carrying`, `num_returned` |
| Opponent position and direction | only if within Manhattan 5 of either of our agents | otherwise `configuration is None` and `get_agent_position(i)` returns `None` |
| Opponent `is_pacman`, `scared_timer`, `num_carrying`, `num_returned`, `start` | **yes, even when hidden** | grey zone, see rules.md Q3 |
| Noisy distances `get_agent_distances()` | yes | one reading per agent, including self and teammate |
| Private fields `data._food_eaten`, `_capsule_eaten`, `_food_added`, `_agent_moved` | present | **forbidden** by our fair-play policy |

## Mechanics details [verified in code; scared timer and maze stats also by script]

- **Sonar**:
  - The reading is `int(Manhattan(me, them) + noise)`, with `noise` drawn uniformly from the integers −6…+6 (probability 1/13 each).
  - It is **Manhattan, not maze distance**, and it **can be negative**.
  - A fresh reading is drawn on every observation.
  - `GameState.get_distance_prob(true, noisy)` gives the likelihood.
- **Sight**: an opponent is visible if it is within Manhattan ≤ 5 of either of our agents, and walls do not block sight.
- **Movement**:
  - Agents move one cell per own move.
  - `Stop` is always legal.
  - Pacman/ghost status flips when crossing the middle. The red side is `x < width // 2`, so red's home column is `x = width//2 − 1` and blue's is `x = width//2`.
- **Collisions**:
  - A collision means being on the same cell (tolerance 0.7). It is checked after each move, for the mover against all opponents.
  - A ghost that is not scared eats the Pacman; a scared ghost gets eaten.
- **Death**:
  - A dead Pacman's carried food is dumped by BFS around the death cell, on the side where it died (the defender's side).
  - The Pacman respawns at its start as a ghost, with its scared timer reset.
- **Scared timer**:
  - Eating a capsule sets **both** opponents to 40.
  - The timer decrements **only when that scared agent itself moves**, so 40 of its own moves ≈ 160 plies.
  - Being eaten resets it to 0.
- **Returning food**: crossing home adds the carried food to the score. When the team total of returned food reaches `TOTAL_FOOD/2 − 2` (28 on random maps), the game ends immediately.
- **Crashes and time**:
  - A crash, timeout or failure to load sets the score to −1 (red at fault) or +1 (blue at fault).
  - Time rules: > 1 s gives a warning, and the 3rd warning forfeits. > 3 s forfeits, enforced by `SIGALRM` on Linux only. A total over 900 s per agent forfeits. All of this applies only with `-c`.

## Random maps (`RANDOM<seed>`) [verified over 200–400 seeds, E-000]

- **Size and contents**: always 34 × 18, with 60 food (30 per side) and 4 capsules (2 per side).
- **Symmetry**: point symmetry, so the blue half is the red half rotated 180°.
- **Start positions**:
  - Red agent 0 starts at (1,2) and agent 2 at (1,1), bottom-left.
  - Blue agent 1 starts at (32,15) and agent 3 at (32,16), top-right.
- **"Prison" corridors**: 0–3 vertical wall layers next to the start column form a serpentine corridor out of the start.
  - Distribution over 400 seeds: 0 layers 20%, 1 layer 46%, 2 layers 22%, 3 layers 12.5%.
  - Each layer adds roughly a full board height (~15 steps) to leaving the start, and to getting back after a respawn. These step counts are estimated from seeds 2 and 11.
- **Food placement**:
  - First at dead-end cells (cells with exactly one open neighbour, two passes of the detection), then at random.
  - No food near the start corner or in the prison columns.
  - Random (non-dead-end) food and capsules are never in the 2 columns next to the centre line (x = 15, 16 on red's side, mirrored for blue). Dead-end food can be there.
  - **Consequence: a large share of the food sits in dead ends by construction.**
- **Reseeded RNG**: generating `RANDOM<seed>` reseeds Python's **global** RNG.
  - The starting team and the sonar noise are therefore fixed by the seed (plus the agents' own RNG use).
  - Same seed + deterministic agents = identical game [verified for the generator; game-level identity follows from code reading].
- **Fixed layouts** (`layouts/*.lay`) have other sizes and food counts, and `TOTAL_FOOD` comes from the layout.

## Running games

Run from **`pacman-contest/src/contest`**. On Windows, the default team and layout paths only resolve from there: `DIR_SCRIPT` is built by splitting `__file__` on `/`, which yields an empty string with Windows backslashes [verified].

```powershell
# PowerShell, from pacman-contest\src\contest
..\..\..\venv\Scripts\python.exe capture.py -r ..\..\..\my_team.py -b baseline_team          # watch one game
..\..\..\venv\Scripts\python.exe capture.py -r ..\..\..\my_team.py -b baseline_team -q -c -n 10 -l RANDOM   # 10 timed games, new random map each
..\..\..\venv\Scripts\python.exe capture.py -r baseline_team -b ..\..\..\my_team.py -q -c -l RANDOM13       # we play blue, reproducible map
..\..\..\venv\Scripts\python.exe capture.py -r ..\..\..\my_team.py -b baseline_team --keys1                # play agent 1 yourself (WASD/arrows)
```

On Linux / WSL: `source venv/bin/activate && cd pacman-contest/src/contest && python capture.py ...` (same flags).

| Flag | Meaning |
|---|---|
| `-r FILE`, `-b FILE` | red / blue team file (`.py` optional); `baseline_team` is the built-in baseline |
| `-l NAME` | layout: `defaultCapture`, any name in `layouts/`, `RANDOM` (fresh random map per game) or `RANDOM<seed>` (fixed) |
| `-n N` | number of games. The agents persist across them; a summary is printed when N > 1 |
| `-q` / `-Q` | no graphics / additionally mute agent output |
| `-c` | **enforce time limits and treat exceptions as crashes**, as in the tournament. Use it for every evaluation |
| `-i N` | game length in moves (default 1200) |
| `--record`, `--record-log` | save the replay / log under `www/contest_<name>/` |
| `--replay FILE`, `--replayq FILE` | replay a recorded game (with / without display) |
| `-f`, `--setRandomSeed S` | fix the RNG. Note: `RANDOM<seed>` layout generation reseeds the RNG anyway |
| `--delay-step S` | slow motion |
| `--keys0` … `--keys3` | keyboard control of that agent index |
| `--redOpts` / `--blueOpts` | kwargs for `create_team`. Development only, **not passed in the tournament** |
| `-x N` | first N games are quiet training games |
| `-u NAME`, `-m ID` | contest name and match id. They decide the output path `www/contest_NAME/.../match_ID.*` |

- **Outputs**: every run writes `www/contest_<name>/scores/match_<id>.json` relative to the working directory, by default `www/contest_default/scores/match_0.json`. It is overwritten each run, so give parallel runs distinct `-u` / `-m` values.
- **Speed**: ~40 s per quiet game for baseline-level agents on this Windows laptop [verified E-000]. Heavier agents will be slower.
- **Timing realism**:
  - Windows has no `SIGALRM`, so moves over 3 s are flagged only after they return; they are never killed.
  - WSL `Ubuntu-24.04` is installed on this machine [verified]. Its default Python is 3.12 [not checked here], so Python 3.8 must be installed there separately.
- **Other tools**:
  - `profiler.py` (in `pacman-contest/`): engine profiling, e.g. `python profiler.py -r my_team -b baseline_team -n 5` [reported, untested by us].
  - Full local tournaments: `aig-upf/pacman-eutopia` `contest_manager.py` [reported, untested].

## Testing protocol (summary; CLAUDE.md has the short version)

1. **Smoke test**: one game vs `baseline_team` with no exception and no time warning.
2. **Always use `-c`** for anything that counts. Check the output for `took too long`, `timed out`, `crashed` and `failed to load`.
3. **Benchmark**:
   - Use a fixed list of `RANDOM<seed>` maps, play both colours (swap `-r` / `-b`), and play every opponent in the pool.
   - Report W/T/L, average score, crashes, warnings and the maximum move time per agent.
   - Compare versions **on the same seeds** (paired comparison).
4. **Statistics**: the standard error of a win rate is ≈ √(p(1−p)/n). At n = 40 and p = 0.5 the 95% CI is about ±15 percentage points, so don't claim small improvements from small samples.
5. **Before tagging a submission**: run the benchmark on Linux with Python 3.8 and `-c`.
6. **Log**: put every run that informs a decision in [experiments.md](experiments.md), including the `my_team.py` git commit and the framework commit.

The batch harness `eval/evaluate.py` implements steps 2–4. See [evaluation.md](evaluation.md) for the full protocol and the accept rule.
