# Traps

These are pitfalls that cost games or break the rules, many of them silently. Each entry says what goes wrong, why, and how to prevent it. Add a trap the moment you hit one, and link the experiment where you found it.

Section A matters most: those traps can make us **cheat by accident**.

---

## A. Accidentally cheating or changing the game dynamics

**T-01: Mutating objects the engine shares with your observation** [verified E-000]
- **Shared objects**: the observation is a copy, but several objects inside it are *the same objects* the real game uses:
  - the layout and walls (`game_state.get_walls()`, `game_state.data.layout`)
  - every agent's `Configuration` object
  - `AgentState.start`
- **Consequence**: `walls[x][y] = True` (e.g. to block cells for a search), or `agent_state.configuration.pos = (x, y)` (e.g. to "simulate" a move), changes the **real game**. That alters legal moves or teleports agents: cheating plus undefined behaviour.
- **Prevention**:
  - Treat the observation as read-only.
  - Copy grids (`walls.copy()`) or build our own sets and arrays.
  - To simulate, either use our own lightweight state, or assign a *new* object on our copy: `state.data.agent_states[i].configuration = Configuration(pos, direction)`. That replaces a reference in our copied `AgentState`, which is fine. Never set attributes on existing engine objects.

**T-02: Seeding or reading the global `random` module**
- **Why**: the sonar noise and the starting team come from Python's **global** RNG, the same one the agents use.
  - `random.seed(...)` in agent code (even "just for reproducibility") makes the noise predictable.
  - `random.getstate()` / `setstate()` could be used to predict it.
- **Consequence**: manipulating game dynamics.
- **Prevention**: `self.rng = random.Random(seed)` as our own instance. Never call `random.seed`, `random.setstate` or `random.getstate`. Plain `random.choice` is fine; it only consumes from the stream.

**T-03: Overriding `observation_function`**
- **Why**: the engine passes the **full, unfiltered state** to `agent.observation_function(...)` and trusts the agent to call `make_observation`. Overriding it, or keeping a reference to its argument, exposes hidden opponents.
- **Prevention**: never override it; never touch its argument.

**T-04: Reading internals or using introspection**
- **What counts**:
  - private fields: `data._food_eaten`, `_agent_moved`, `_capsule_eaten`, `_food_added`
  - introspection: `gc`, `inspect`, `sys._getframe`, `__main__._display` (the display receives the true state), the `Game` object, other agents' objects, other teams' modules in `sys.modules`
  - using `final(state)` (it receives the real final state) for anything that affects play
- **Prevention**: public API only (rules.md fair-play policy). Code review: search the code for `._`, `gc`, `inspect`, `__main__`, `sys.modules` and `getstate`.

**T-05: Swallowing the framework's timeout exception**
- **Why**: on Linux the engine raises `TimeoutFunctionException` (a subclass of `Exception`) *inside our code* via `SIGALRM` when a move hits the hard limit. A bare `except:` or `except Exception:` around heavy computation catches it, and the move keeps running past the limit. That circumvents the time rule; RMIT explicitly calls bare `except` tampering.
- **Prevention**:
  - Catch only specific exceptions.
  - If there is a safety net, re-raise first: `except TimeoutFunctionException: raise` (from `contest.util`).
  - Ask the staff (Q9) before relying on any safety net.

**T-06: Monkeypatching or editing the framework**
- **What counts**: changing `capture.SIGHT_RANGE`, `SCARED_TIME` or `AgentRules` / `GameState` methods from `my_team.py`, or editing files under `pacman-contest/`.
- **Consequence**: forbidden (R3). Local edits also make local results meaningless, because the tournament uses its own copy.
- **Prevention**: never edit `pacman-contest/`. `git -C pacman-contest status` should show only generated `www/` and `__pycache__/`.

**T-07: Threads, processes or async**
- **What counts**: `threading`, `multiprocessing`, `concurrent.futures`, `asyncio`, `subprocess`, or work scheduled to continue after `choose_action` returns.
- **Consequence**: disqualification (R2).
- **Fine**: offline tooling such as the benchmark harness may use processes. Only agent code is restricted.

**T-08: Treating the startup state as more than it is**
- **Why**: `register_initial_state` receives a full (unfiltered) copy of the state. At that moment the only hidden information is the opponents' start positions, which are public anyway (`get_initial_agent_position`). Low risk.
- **Prevention**: don't keep the object around expecting it to update.

**T-09: Configuring tournament behaviour via command-line options**
- **Why**: `--redOpts` / `--blueOpts` and the `create_team` kwargs are **not passed in the tournament**.
- **Prevention**: the defaults of `create_team` *are* the tournament configuration. Use options only for experiments.

## B. Forfeits and crashes (lost games)

**T-10: Testing without `-c`**
- **Why**: without `-c` there are **no time limits at all** locally, so a slow agent looks fine.
- **Prevention**: always pass `-c` for evaluation.

**T-11: Trusting Windows or laptop timing**
- **Why**:
  - Windows has no `SIGALRM`, so moves over 3 s are not killed, only flagged after the fact.
  - The SNOW node runs many games in parallel and is probably slower than a laptop.
- **Prevention**:
  - Set an internal move budget far below 1 s (start with 0.5 s and adjust from Linux measurements).
  - Use anytime algorithms with `time.perf_counter()` checks inside loops.
  - Log the maximum move time.
  - Test on Linux / WSL with Python 3.8.

**T-12: Accumulating warnings**
- **Why**: three moves over 1 s in one game forfeits it, so occasional spikes are enough.
- **Prevention**: find the worst-case states (many food, large belief spread, deep search) and make sure the budget holds there too.

**T-13: Startup budget wasted or broken**
- **Why**:
  - The 15 s is per agent; duplicated heavy precomputation wastes it.
  - Forgetting to call `CaptureAgent.register_initial_state` leaves `self.red` and the distancer unset, which crashes later.
- **Prevention**: compute once in a team object. Maze distances are already cached globally per wall layout.

**T-14: Illegal or `None` actions**
- **Why**: either one raises an exception, which is a crash and a lost game.
- **Prevention**: always return an element of `game_state.get_legal_actions(self.index)`. `Stop` is always legal.

**T-15: Simulating hidden opponents with `generate_successor`**
- **Why**: a hidden opponent's `configuration` is `None`, so generating its successor crashes.
- **Prevention**: insert hypothesised positions as **new** `Configuration` objects on our copy (T-01), or use our own forward model.

**T-16: Rare-state exceptions**
- **Examples**:
  - an empty food list near the end
  - no visible enemies
  - a belief that collapses to all zeros (inconsistent evidence)
  - `get_previous_observation()` returning `None` on the first move
  - division by zero
  - an empty `max()`
- **Prevention**: guards plus a fallback action; reinitialise the belief from the evidence when it collapses.

**T-17: Python > 3.8 syntax or library features** (the tournament uses 3.8)
- **Forbidden at runtime**: `list[int]` / `dict[str, int]` (use `typing.List`, or `from __future__ import annotations` for annotations only), `X | Y` types, `match`, `functools.cache` (use `lru_cache(maxsize=None)`), dict `|`, `str.removeprefix`, `zip(strict=)`.
- **Evidence**: [reported] a 2022 UPF disqualification log shows `'type' object is not subscriptable`.
- **Prevention**: always test with `venv` (3.8.10).

**T-18: Third-party imports**
- **Why**: numpy and torch may not exist on SNOW (Q2). An `ImportError` means the team fails to load, which loses every game.
- **Prevention**: stdlib only until the staff confirm otherwise.

**T-19: Helper module name collisions**
- **Why**: `capture.py` adds each team's folder to `sys.path`, and Python caches modules by name in `sys.modules`. If two teams both import e.g. `utils`, the second team silently gets the first team's module.
- **Prevention**: give helpers unique names (e.g. `ourteam_belief.py`), or keep everything in `my_team.py`.

**T-20: Output**
- **Why**: `stdout` / `stderr` are published in the tournament logs, printing slows us down, and touching `sys.stdout` / `sys.stderr` is a disqualification at RMIT/UoM.
- **Prevention**: a `DEBUG = False` flag; no printing in tournament mode.

**T-21: Writing files during games**
- **Why**: the working directory isn't ours, games run in parallel, and CONTEST.md forbids it.
- **Prevention**: don't. Read-only loading of shipped data relative to `__file__` is the only file access (pending Q6).

## C. Wrong assumptions about the engine (all [verified], see framework.md)

| ID | Trap |
|---|---|
| **T-22** | Sonar is **Manhattan** distance plus uniform integer noise in [−6, 6]. It is not maze distance, readings can be negative, and you also get (useless) readings for yourself and your teammate. |
| **T-23** | Sight is Manhattan ≤ 5 **through walls**, from *either* of our agents. |
| **T-24** | `game_state.get_score()` is red-positive. Use `self.get_score(game_state)` for our perspective. |
| **T-25** | Border off-by-one: the red side is `x < width//2`, so red's home column is `width//2 − 1` and blue's is `width//2`. |
| **T-26** | The scared timer counts the scared agent's **own** moves: 40 moves ≈ 160 plies. It resets when the agent is eaten. A capsule scares *both* opponents. |
| **T-27** | `get_previous_observation()` is our state from our previous turn; three agents moved since then, including both opponents. It is `None` on the first move. |
| **T-28** | Locally the same agent objects and module variables **persist across `-n` games**, so reset per game in `register_initial_state`. In self-play, helper modules (not `my_team.py`) are **shared by the red and blue copies**, so global state in a helper corrupts experiments. Prefer a team object created in `create_team`. |
| **T-29** | `timeleft` counts all agents' moves (1200). Each agent has about 300. |
| **T-30** | Food scores only when returned. The game ends **immediately** when a team has returned 28 (random maps). |
| **T-31** | A dead Pacman's food reappears near where it died, on the defending side. Food diffs therefore show *additions* too. |
| **T-32** | On random maps much of the food sits in dead ends **by construction**. Greedy nearest-food play walks into traps. |
| **T-33** | Start "prison" corridors: leaving the start or coming back after a respawn can take ~15–45+ moves. Don't assume the start is near the border. |
| **T-34** | On Windows, run `capture.py` from `pacman-contest/src/contest`. Elsewhere the default team and layout paths don't resolve (the `DIR_SCRIPT` bug). |

## D. Experimentation pitfalls

**T-35: Too few games**
- **Why**: the standard error of a win rate is ≈ √(p(1−p)/n). At 40 games and p = 0.5 the 95% CI is about ±15 pp.
- **Prevention**: fixed seed sets, *paired* comparisons (same seeds for both versions), both colours, and enough games.

**T-36: Repeating the same `RANDOM<seed>` and calling it a sample**
- **Why**: map generation reseeds the global RNG, so the same seed with deterministic agents produces the **identical game**. Repeats are not independent samples.
- **Prevention**: vary seeds instead.

**T-37: Overfitting to `baseline_team`**
- **Why**: beating the baseline is easy and says little about real opponents.
- **Prevention**: keep an opponent pool: older versions of ours, plus specialists such as all-out attack, double defence, capsule rusher and border camper.

**T-38: Overfitting to fixed layouts**
- **Why**: the tournament uses random maps.
- **Prevention**: do the main evaluation on `RANDOM<seed>`, plus a few fixed layouts as a sanity check (they have different sizes and food counts).

**T-39: Testing one colour only**
- **Why**: the colour and the starting team both matter.
- **Prevention**: always test as red **and** blue.

**T-40: Parallel runs clobbering outputs**
- **Why**: `www/contest_default/scores/match_0.json` is overwritten on every run.
- **Prevention**: give each process its own `-u` / `-m`, and parse stdout.

**T-41: Local timing ≠ cluster timing**
- **Prevention**: record timing margins (max move time), not just pass/fail.

**T-46: `-Q` hides the engine's time warnings and crash messages** [verified in `game.py`]
- **Why**: with `-Q` (mute agents), `stdout` / `stderr` are redirected into a per-agent buffer while that agent's turn is processed. The engine prints "took too long", "timed out" and "Red agent crashed" during that window, so they vanish.
- **Prevention**: use `-q` for evaluation, never `-Q`. `eval/evaluate.py` uses `-q`.

**T-47: Passing options through `--redOpts` / `--blueOpts`**
- **Why**:
  - `parse_agent_args` splits on `,` and `=`, so option values must not contain either.
  - In Git Bash, `/c/Users/...` paths given to the Windows Python become wrong paths. Use Windows paths (`C:\...`) or relative paths.
- **Prevention**: `eval/evaluate.py` builds the options and refuses bad values.

**T-49: Machine load causes move-time spikes** [observed E-002]
- **What we saw**: moves that normally take ~2 ms took up to 0.95 s while the PC was low on memory (paging), for every team. In the tournament, "many processes" share SNOW nodes, and 3 moves over 1 s forfeit the game.
- **Prevention**:
  - Keep the per-move compute tiny, with an internal budget far below 1 s.
  - Never run heavy work in rare branches.
  - Read timing results together with how loaded the machine was. Re-run on an idle machine before concluding that the code is slow.

**T-50: Designing on validation seeds by accident** [hit E-005/E-007]
- **What happened**: E-002 ran on validation seeds 1–20. Its tie games were then replayed to diagnose greedy (E-005) and to debug the standoff breaker (E-007), so those maps shaped the candidates.
- **Why it matters**: a decision on the same seeds is then optimistically biased (G2/G3 in evaluation.md).
- **Prevention**:
  - Diagnose and debug on tuning seeds where possible.
  - When a validation map was used anyway, skip it for the decision: `evaluate.py play --seed-offset N` starts after the first N seeds of the list.
  - Log which validation seeds were used for design.

**T-51: The engine sleeps before every move, even in quiet mode** [verified E-009]
- **Why**: `capture.py --delay-step` defaults to 0.03 s, and `game.py` sleeps that long before every move whatever the display. That is 36 s of every ~40 s game.
- **Consequence**: batch runs are ~35× slower than necessary and look CPU-light (10–13% CPU), which can lead to wrong conclusions about hardware or agent speed.
- **Prevention**: pass `--delay-step 0` for every batch run (`eval/evaluate.py` does). It does not change results: the sleep is outside the agents' timed moves (12/12 identical games, E-009).

**T-48: Changing a frozen league file**
- **Why**: league entries (`eval/league.json`) point to team files. Editing a file after it was benchmarked silently changes an "old version" and invalidates past results and the forgetting check.
- **Prevention**: new versions get new files (`greedy_v2.py`). Frozen files are marked `"frozen": true`.

## E. Submission and repo

**T-42: The tournament runs `my_team.py` from the repo root**
- **Why**: not the files in `pacman-contest/src/contest/agents/`.
- **Prevention**: helper files live next to it and must be committed.

**T-43: Framework updates**
- **Why**: `git submodule update --remote` pulls the latest upstream framework, which can change behaviour.
- **Prevention**: note the framework commit in every experiment; re-run benchmarks after an update.

**T-44: `TEAM.md`**
- **Why**: it is an RMIT template ("Semester 2, 2020"). Whether UPF needs it is unknown (Q7).

**T-45: Committing generated or large files**
- **Why**: `venv/`, `__pycache__/` and `*.pyc` are ignored, but `www/` outputs, replays and logs are not.
- **Prevention**: keep them out of commits.
