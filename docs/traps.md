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
- **Why**: numpy and torch are installed on SNOW only on request (Q2). An `ImportError` means the team fails to load, which loses every game.
- **Prevention**: stdlib only until we have requested a library and the professor has confirmed it is installed; request before the test run (2026-11-23) so it is exercised there.

**T-19: Helper module name collisions**
- **Why**: `capture.py` adds each team's folder to `sys.path`, and Python caches modules by name in `sys.modules`. If two teams both import e.g. `utils`, the second team silently gets the first team's module.
- **Prevention**: give helpers unique names (e.g. `ourteam_belief.py`), or keep everything in `my_team.py`.

**T-20: Output**
- **Why**: `stdout` / `stderr` are published in the tournament logs, printing slows us down, and touching `sys.stdout` / `sys.stderr` is a disqualification at RMIT/UoM.
- **Prevention**: a `DEBUG = False` flag; no printing in tournament mode.

**T-21: Writing files during games**
- **Why**: the working directory isn't ours, games run in parallel, and CONTEST.md forbids it.
- **Prevention**: don't. Read-only loading of shipped data relative to `__file__` is the only file access (allowed, Q6).

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
- **Measured (E-016)**: greedy_v2 on WSL Linux / Python 3.8.20 with real `SIGALRM` limits: max move 0.064 s serial, 0.087 s with all 12 CPUs busy; startup ≤ 1.42 s. Re-measure whenever an agent adds search.

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
  - The engine's 1 s clock covers more than `choose_action`: its own deep copy of the state and the whole `get_action` call. A warning while the sentinel's `max_s` is tiny points to the environment. Our agents are deterministic, so **replay the same game**: a cause in our code repeats, a stall does not. E-021: one warning in 180 serial WSL games; 5 replays gave 0 warnings and the same score.

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

**T-52: A death metric that is always true** [hit E-014]
- **What happened**: the first replay probe asked "was the killer in sight one ply before the death?" and reported 0% unseen against every opponent. A ghost that eats us stands next to us one ply earlier, so it is always in sight. The metric said nothing.
- **Prevention**:
  - Measure at the moment of decision, not at the outcome: e.g. "was the killer in sight when we went into the dead end?" (E-014).
  - Sanity-check any 0% or 100% diagnostic before believing it.

**T-53: Leaking the held-out opponents into design** [E-015]
- **Why**: a held-out opponent is useful only while nobody tunes against it. Reading its code, watching its replays or screening candidates against it makes it part of the tuning pool, and the generalisation gap it measures shrinks to nothing.
- **Prevention**:
  - `eval/heldout/` is for the release gate and rare logged checkpoints only, and only totals are reported.
  - Its style labels in league.json are all a designer should know.

**T-57: A coarse diff says "no effect" when the change is in the defender's path** [hit E-025]
- **What happened**: comparing smoke games on score, Pacman moves, returned food and move counts found `hunt`, `directed` and `recall` "identical" to `flags` in 8/8 games. Counting branch calls showed hunt and directed did fire (23 times each in one game vs baseline); those diagnostics simply never see where a ghost walks.
- **Prevention**: to show that a switch changes nothing, compare every diagnostic of both teams (as the identity checks do), or count the branch directly. To show that a switch does something, count its branch.

**T-58: `capture.py` loads its own copy of a team module** [hit E-025]
- **Why**: the engine imports the team file by path into a fresh module. Patching classes in a module you imported yourself (for counting or tracing) changes nothing in the game.
- **Prevention**: wrap the team through a small team file whose `create_team` loads the target and patches that copy (as `eval/trace_team.py` and `eval/belief_probe/probe_team.py` do). Local analysis only, never submitted.

**T-61: Combining screen arms that are ≈ 0** [hit E-039]
- **Why**: with ~800 paired games a screen arm's CI half-width is ≈ 0.08–0.10, so "Δ > 0" admits arms that are pure noise (two E-039 arms qualified by +1 point). Switches that are each ≈ 0 can still share a direction of harm (E-039: three of them took time from the attack) and add up in the combination: −0.07 on validation.
- **Prevention**: pre-register a screen threshold well above 0 (e.g. Δ ≥ +0.05 or CI lower > −0.02), validate the best single arm rather than a bundle, and check the diagnostics of the arms for a shared side effect before combining.

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

## F. Agent-logic pitfalls

**T-54: Dropping "negligible" belief cells loses enemies that walk straight** [hit E-019]
- **What happened**: the first belief filter (H-S01) dropped cells below probability 1e-4, then 1e-12. Under a random-walk motion model an enemy that walks k cells straight has a probability of about (1/3)^k, so its true cell was pruned. The belief then gave the true cell probability 0 in **22.8%** (1e-4) and 2.3% (1e-12) of hidden turns, measured against the opponents' own positions.
- **Prevention**:
  - Never prune by probability: zeros may come only from hard evidence (sight, sonar range, food events).
  - Check a tracker against true positions offline before using it. "Truth excluded" must be ≈ 0%; after the fix it was 0.0% of ~15,000 hidden turns.

**T-55: "It vanished next to us, so it was eaten" is also true when *we* were eaten** [hit E-019]
- **Why**: greedy_v2's respawn rule says that an enemy seen within 2 of one of us last turn and gone now must have been eaten, because it would still be within sight. But if that enemy ate *our* agent, our agent teleports home and the enemy is simply out of sight.
- **Consequence**: the belief jumped to the enemy's start while the enemy still stood where our attacker had died; in the E-019 probe the true cell then had probability 0 in the following turns.
- **Prevention**: only count teammates that moved at most one cell since the previous observation (implemented behind the belief switches in `teams/greedy_lab_v3.py`; greedy_v2 still has the old rule, where it only affects the scared-timer guess).

**T-56: The defender's position changes what our attacker sees** [hit E-007, E-019]
- **Why**: sight is shared (T-23): our attacker sees every enemy within 5 of *either* of us. A defender that stands at the border across from the enemy guard shows that guard to our attacker. greedy's race-safe attacker then treats the guard as blocking and waits.
- **What happened**: the first shadowing defender followed the enemy "nearest our side", usually their border guard, and turned a 22–0 win over baseline_team into a 0–0 standoff (E-019 smoke). The tracker switch of E-007 made the attacker timid the same way, through extra (remembered) ghosts.
- **Prevention**: when a change gives the attacker more ghost sightings, re-check the attacker's standoff and Pacman-move counts. The defender should follow the enemy that has actually come over, not their guard.

**T-59: A search exploits the errors of its leaf; a good R² is not enough** [hit E-030, E-033]
- **Why**: a planner that backs up the best node (IW, max over continuations) seeks out the states its evaluation overrates. A piecewise-constant leaf (lookup table) has jumps at bucket edges and noisy sparse cells; the search walks to them.
- **What happened**: in E-033 the 5-D lookup-table leaf predicted the 30-move outcome as well as the net (held-out R² 0.453 vs 0.464) but played −0.33 vs greedy_v4, with 0.67 deaths and 3.3 dropped food per game (net: 0.42 / 1.2). The linear leaf (R² 0.21, smooth) lost only −0.11 and a smooth quadratic leaf with the net's R² (0.461) −0.05. The hand-made leaf of E-030 was the same story: optimism over a deterministic model.
- **Prevention**: judge a leaf by play, not by R². Prefer smooth function classes (polynomial, small MLP) for leaves under max-backup search; if a table is used, interpolate or smooth it.

**T-60: Pessimistic opponent scenarios make a Monte-Carlo planner timid**
- **Why**: averaging over scenarios where every ghost is aware and chases or cuts us off makes any crossing look dangerous, so a margin-based override keeps choosing to wait at the border.
- **What happened**: E-033's flat paired Monte Carlo and UCT arms died rarely (0.40–0.52 per game) but returned only 8.9–11.1 food per game (greedy_v4 15.8) and lost 0.43–0.72 PPG to greedy_v4, even as a re-check on top of greedy_v4.
- **Prevention**: calibrate a ghost model against real ghost behaviour (e.g. fit type weights from replays) before trusting expectations under it; watch returns and standoff moves, not only deaths.

**T-62: "PPG ≥ 1.5 head-to-head" is not "not losing" when the mirror has ties** [hit E-043]
- **Why**: a tie gives 1 point to each side, so with wins = losses the head-to-head PPG is 1.5 − T/(2n). Near-identical agents tie often (E-043: 28 of 80 games, PPG 1.32 for both sides), so the threshold silently becomes "must beat the incumbent", which a fix aimed at other opponents cannot do.
- **Prevention**: when pre-registering, state the head-to-head criterion as W ≥ L (or a CI on W − L), or report the tie rate next to the PPG. Never change the criterion after seeing the result; ask the user.
