# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Goal

Build our team's two-agent Pacman Capture-the-Flag team for the UPF/EUTOPIA contest (course "Autonomous Systems", EMAI 2026-27, group project; spec in `programming_project.pdf`).
- **What gets submitted**: `my_team.py` in the repo root, plus any helper modules next to it.
- **Where it plays**: UPF's tournament on its SNOW cluster against teams from other universities, on random maps.
- **Dates**: test run 2026-11-23, deadline 2026-12-03 23:59, final run 2026-12-04.
- **Current state**: `my_team.py` = `teams/greedy_v3.py` (greedy_v2 + a defender that waits across from the enemy raider's likely crossing, using an exact belief from its own sonar), promoted on 2026-10-18 after the release gate on the locked test seeds (`docs/experiments.md` E-019, E-021). Before that: `teams/greedy_v2.py` (greedy_v1 + standoff breaker + intercepting defender + return at 8, E-011..E-013). `docs/agents.md` lists every team and what was tested. Never edit `my_team.py` directly: build `teams/<name>_vN.py`, pass the accept rule in `docs/evaluation.md`, then copy it over.

## Knowledge base: read before working, update after

`docs/` is the team's memory. Read the relevant files before changing the agent:

| File | Contents |
|---|---|
| `docs/README.md` | index, ID scheme (`H-M##`, `H-S##`, `M-##`, `T-##`, `E-###`), evidence tags |
| `docs/rules.md` | rules with sources, hard constraints R1–R10, fair-play policy, open questions for the instructors (Q1–Q10) |
| `docs/framework.md` | verified engine facts, observation contents, random map generator, all CLI flags, testing protocol |
| `docs/heuristics.md` | map heuristics (`H-M`) vs sensory heuristics (`H-S`), with status and evidence |
| `docs/methods.md` | agent-building methods (`M-`), their fit, the proposed architecture and timeline |
| `docs/traps.md` | pitfalls, including ways to cheat by accident (section A) |
| `docs/experiments.md` | log book: every run that informs a decision, with a template |
| `docs/evaluation.md` | how agents are compared: objective (3/1/0 points), accept rule, seed and opponent splits, league, reward-hacking guards |
| `docs/picks/` | one behaviour page per version that has been in `my_team.py` (rules, parameters, rule profile, evidence, blind spots). **The current one explains what our agent does** |
| `docs/agents.md` | catalogue of every team (league entry): what it is, what was tested, result, verdict; ideas already rejected. **Check it before building an idea** so tested agents are not redone |

When you finish:
- Log every experiment in `docs/experiments.md`, including failures.
- Update statuses in `heuristics.md` / `methods.md`, citing the experiment ID.
- Add every new team or league entry to `docs/agents.md`, with what was tested and the verdict.
- When a version is promoted to `my_team.py`, add its page to `docs/picks/` (decision rules from the code, a `trace_game.py profile`, evidence, blind spots).
- Add any new trap to `traps.md`.
- Tag every claim `[verified]`, `[source]`, `[reported]` or `[untested]`. "Unknown" beats a guess.

## Hard constraints: never violate (details and sources in docs/rules.md)

1. **Time**: `choose_action` < 1 s on the tournament machine. Use an internal budget well below that, with anytime checks via `time.perf_counter()`. Never > 3 s. `register_initial_state` < 15 s per agent. Three slow moves, or one > 3 s, forfeit the game.
2. **No concurrency**: no threads, processes, subprocesses, async, or computation outside our own `choose_action` / `register_initial_state` calls.
3. **No framework changes**: never modify anything in `pacman-contest/`, on disk or at runtime. No monkeypatching, no changing engine constants or methods.
4. **No crashes**: always return an action from `game_state.get_legal_actions(self.index)`. An exception or illegal action loses the game.
5. **Python 3.8, stdlib only** (plus the framework's `frozendict`) until the staff confirm other libraries (Q2). No `list[int]`, `X | Y`, `match`, `functools.cache`.
6. **Output and files**: don't print in tournament mode (logs are published), never touch `sys.stdout` / `sys.stderr`, never write files during games.
7. **Own work only**: never copy other teams' code (public repos are research pointers, not sources).

**No cheating, and no manipulating the game dynamics in our favour.** The agent may use only what its observation honestly provides, through the public API. Concretely:
- **Never mutate objects reachable from the observation.** The walls/layout and the `Configuration` objects are *shared with the real game* [verified]. Copy grids; build new `Configuration`s on our own copies (`docs/traps.md` T-01).
- **Never** call `random.seed` / `setstate` / `getstate` on the global `random` module. It drives the sonar noise and the starting team. Use `random.Random()` instances instead.
- **Never** override `observation_function`. The engine passes it the full true state.
- **No private engine fields** (`data._food_eaten`, `_agent_moved`, ...) and **no introspection** (`gc`, `inspect`, frames, `__main__._display`, the `Game` object, other teams' modules).
- **Never** catch the framework's `TimeoutFunctionException`, so no bare `except:` / `except Exception:` around heavy work without re-raising it.
- **Grey zone** (rules.md Q3): hidden opponents' `is_pacman`, `num_carrying` and `scared_timer` are readable. Keep their use behind a single switch that defaults to off until the staff confirm.
- **If you are unsure**: stop and ask the user. Don't decide a grey area yourself.

## How the game works (short)

- **Teams and sides**: red agents 0 and 2 on the left half (`x < width//2`), blue agents 1 and 3 on the right. An agent is a ghost at home and a Pacman on the enemy half.
- **Scoring**: food scores only when carried home. An eaten Pacman drops its food and respawns at its start.
- **Capsules**: a capsule scares both opponents for 40 of *their own* moves.
- **End of game**: when a team has returned 28 food (random maps: 30 per side, all but 2), or after 1200 agent moves (300 each). Then the higher score wins, and 0 is a tie.
- **What agents see**: walls, all food, capsules, the score and the time left are fully visible. Opponents are visible only within Manhattan 5 of either of our agents; otherwise there is only a noisy Manhattan distance (uniform ±6).
- **Tournament maps** are random `RANDOM<seed>` maps: 34×18, food placed in dead ends first, and "prison" corridors that make respawns expensive.

## Commands

Setup (fresh clone, per README.md): `git submodule update --init --remote`, `python3.8 -m venv venv`, activate it, then `cd pacman-contest`, `pip install -r requirements.txt`, `pip install -e .`. The existing `venv/` is Python 3.8.10 on Windows.

Run games from `pacman-contest/src/contest`. On Windows the default paths only resolve from there.

```powershell
# watch one game: us (red) vs baseline (blue)
..\..\..\venv\Scripts\python.exe capture.py -r ..\..\..\my_team.py -b baseline_team
# evaluation-style: no graphics, time limits enforced (-c), 10 games on fresh random maps
..\..\..\venv\Scripts\python.exe capture.py -r ..\..\..\my_team.py -b baseline_team -q -c -n 10 -l RANDOM
# reproducible single map, playing blue; record and replay
..\..\..\venv\Scripts\python.exe capture.py -r baseline_team -b ..\..\..\my_team.py -q -c -l RANDOM13 --record
..\..\..\venv\Scripts\python.exe capture.py --replay=www\contest_default\replays\match_0.replay
# play yourself as agent 1 (WASD / arrow keys)
..\..\..\venv\Scripts\python.exe capture.py -r ..\..\..\my_team.py -b baseline_team --keys1
```

- **Speed**: add `--delay-step 0` to batch runs. Otherwise the engine sleeps 0.03 s before every move even with `-q`: ~40 s instead of ~1.3 s per game, with identical results (E-009, T-51). `eval/evaluate.py` already does this.
- **Linux / WSL**: `source venv/bin/activate && cd pacman-contest/src/contest && python capture.py ...`, with the same flags.
  - On this laptop, WSL Ubuntu 24.04 has a Python 3.8.20 mirror of the repo in `~/pacman_wsl`, set up with `uv` (no sudo). Re-sync it with `rsync` before use; the recipe is in `docs/framework.md`.
  - Use it for the Linux timing check (E-016).
- **Other tools**: there is no lint config and no unit-test suite. `runner.py` and `scripts/play.sh` are stale; use `capture.py`. All flags are in `docs/framework.md`.

## Evaluation (decisions between agents): see docs/evaluation.md

```powershell
# from the repo root
venv\Scripts\python.exe eval\check_rules.py my_team.py teams\*.py          # static rules check (must pass)
venv\Scripts\python.exe eval\evaluate.py play --agents baseline greedy turtle --seeds validation --n-seeds 20 --run <name>
venv\Scripts\python.exe eval\evaluate.py play --candidate <new> --vs <incumbent> baseline turtle --seeds validation --n-seeds 40 --run <name> --compare <new> <incumbent>
venv\Scripts\python.exe eval\evaluate.py summary --run <name>
```

- **How a run works**: `evaluate.py` plays colour-swapped game pairs on fixed `RANDOM<seed>` maps through `capture.py -q -c`. Every team is wrapped in `eval/sentinel_team.py`, which records move times and runtime rule violations (local only, never submitted). Each run writes `eval/results/<run>.jsonl` and prints a markdown summary.
- **Seeds**: `eval/seeds/tuning.txt` is free to use; `validation.txt` is for accept/reject decisions; `test.txt` is **locked**, only for confirming a frozen release candidate, and each use is logged.
- **League**: entries live in `eval/league.json` (path + `create_team` options). **Never edit a file after it was benchmarked**; new versions get new files (`teams/greedy_v4.py`). Since 2026-10-18 new candidates play only the **reference pool** of 8 (`greedy_v3` = incumbent, `greedy_v2`, `greedy`, `feature`, `camper`, `rusher`, `choke`, `exploit_v2`; `_reference_pool` in league.json), not all-vs-all: `--candidate <new> greedy_v3 --vs greedy_v3 greedy_v2 greedy feature camper rusher choke exploit_v2 --compare <new> greedy_v3`.
- **Held-out opponents**: `eval/heldout/` (`heldout_a`, `heldout_b`; `_heldout_pool` in league.json) were written blind (E-015).
  - Never read their code or replays, and never screen, tune or debug against them (T-53).
  - Use them only for the release gate and rare logged checkpoints.
- **Diagnosis**: `eval/replay_probe.py` (`classify`, `replay`) shows where an agent loses points (E-014). `eval/trace_game.py` (`game`, `profile`) shows which rule produced every move of our agents, with a replay to watch alongside (E-022).
- **Accepting an agent**: a new agent replaces the incumbent only under the accept rule in `docs/evaluation.md` section 2. That rule needs zero crashes, warnings and violations, a paired points-per-game gain with a CI above 0 on validation seeds, no per-opponent regression beyond 0.5, and confirmation on unused seeds for releases. Any sentinel or lint violation is an automatic reject, whatever the score.

## Testing protocol

1. **Smoke test**: one game vs `baseline_team` with no exceptions and no time warnings.
2. **Always use `-c`** for anything that counts. Without it, no time limits are enforced. Check the output for `took too long`, `timed out`, `crashed` and `failed to load`.
3. **Benchmark**:
   - Use a fixed list of `RANDOM<seed>` maps, play **both colours** (swap `-r` / `-b`), and play every opponent in the pool: baseline, our older versions, specialist variants.
   - Compare versions on the **same seeds**.
   - Report W/T/L, average score, crashes, warnings and the max move time.
   - Win-rate CI at 40 games is about ±15 pp.
   - Repeating the same seed with deterministic agents replays the identical game, so vary seeds instead.
4. **Timing**: Windows never kills a slow move (no `SIGALRM`), and the cluster is probably slower than this laptop. Before freezing a submission, check timing on Linux / WSL with Python 3.8 and `-c`.
5. **Parallel runs**: they overwrite `www/contest_default/...`, so give each one a distinct `-u <name>` / `-m <id>`.
6. **Log the run** in `docs/experiments.md`, with the `my_team.py` commit and the framework commit.

Steps 2–5 are automated by `eval/evaluate.py` (see "Evaluation" above).

## Architecture (engine, big picture)

- **`capture.py`**: `GameState` (the agent-facing API: food, walls, capsules, score, noisy distances, `generate_successor`), `AgentRules` (moves, eating, deaths, food dumping, capsules), `CaptureRules` (game start and end, time limits) and the CLI (`read_command` → `run_games`).
- **`game.py`**: the `Game.run` loop.
  - Each turn it calls `agent.observation_function(state.deep_copy())` (which runs `make_observation`: it hides opponents beyond sight and adds sonar), then `agent.get_action(obs)`, then `state.generate_successor`.
  - With `-c`, it enforces time via `util.TimeoutFunction`.
- **`capture_agents.py`**: the `CaptureAgent` base class.
  - `register_initial_state` sets `self.red` and builds `self.distancer` (all-pairs maze distances, cached globally per wall layout in `distance_calculator.distanceMap`).
  - `get_action` stores the observation in `observation_history` and calls `choose_action`.
  - Helpers: `get_food`, `get_food_you_are_defending`, `get_opponents`, `get_score` (team-relative), `get_maze_distance`.
- **Agent lifecycle**: `capture.py` loads each team file once per invocation (one module per team), and `create_team(first_index, second_index, is_red)` builds both agents in the same process.
  - Teammates can share Python objects; prefer a team object created in `create_team`.
  - The same objects are reused across `-n` games, so reset per game in `register_initial_state`.
  - The tournament passes no extra `create_team` arguments, so the defaults are the tournament configuration.
- **Maps**: `maze_generator.py` builds the `RANDOM<seed>` maps; `layouts/*.lay` are the fixed maps.
- **Repo layout**:
  - `my_team.py`: ours; the submission.
  - `teams/`: our team versions, one self-contained file each. They are frozen once benchmarked and are also league opponents.
  - `eval/`: evaluation tooling: harness, sentinel, rules lint, league, seed splits, results.
  - `pacman-contest/`: the submodule `aig-upf/pacman-contest` at commit `54cd83c`. Read-only for us.
  - `docs/`: the knowledge base.
  - `scripts/`: stale.
  - `TEAM.md`: an unfilled RMIT template; whether UPF requires it is unknown (Q7).
