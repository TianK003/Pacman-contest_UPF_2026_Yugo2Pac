# Rules, hard constraints and fair-play policy

## Source hierarchy

1. **`programming_project.pdf`**: the course assignment for 2026-27. This is the authoritative source for us.
2. **What UPF actually runs**:
   - the `aig-upf/pacman-contest` code (our submodule at commit `54cd83c`, identical to upstream `main` on 2026-10-16)
   - the results site <https://pacman-contest.upf.edu/>
3. **`pacman-contest/src/contest/CONTEST.md` and `pacman-contest/README.md`**: mostly copied from RMIT's contest (they mention the Nectar cloud, `Staff-` teams and chocolate prizes). Indicative only.
4. **Berkeley / RMIT / Univ. of Melbourne rules**: not binding, but they show what organisers of this game consider fair.

## Game rules (PDF §2)

- **Layout**: red is the left half and blue the right half. Red agent indices are even (0, 2) and blue are odd (1, 3). An agent is a ghost on its own side and a Pacman on the enemy side.
- **Scoring**: eaten food is carried, and scores 1 point per dot once the Pacman returns to its own side. Red scores are positive and blue scores negative. A Pacman that is eaten drops the food it carries back onto the board.
- **Eating a Pacman**: it respawns at its start position as a ghost. Kills give no points.
- **Capsules**: the opponents become scared for 40 moves, or until they are eaten. A Pacman that touches a scared ghost sends that ghost back to its start.
- **Observations**: an opponent's position is visible only within Manhattan distance 5 of you or your teammate. Every agent always gets a noisy distance to every agent.
- **Winning**: the game ends when a team returns all but two of the opponent's dots. In code that is `returned ≥ TOTAL_FOOD/2 − 2`, i.e. 28 on 60-food maps. Otherwise the game ends after 1200 agent moves (300 each) and the higher score wins; a score of 0 is a tie.
- **Time**: one action per second, otherwise a warning. Three warnings, or a single move over 3 s, forfeits the game. `register_initial_state` gets 15 s. Errors appear in the downloadable logs.

## Tournament facts

- **Dates**: test run 2026-11-23, deadline 2026-12-03 23:59, final run 2026-12-04 [source: PDF].
- **Hardware**: games run on the UPF SNOW cluster with "many processes" at once [source: PDF §2.7]. The CPU per game is probably slower than a laptop [untested assumption]. Plan with a large time margin.
- **Python**: 3.8 [source: PDF §3.1].
- **Maps**:
  - [verified 2026-10-16] The 2024 final shows "Layouts: 1 (0 fixed + 1 random)": every game used a different `RANDOM<seed>` map. It had 18 teams and 765 games, i.e. 5 games per pair. See <https://pacman-contest.upf.edu/final_2024/results_0.html>.
  - [reported by our web research, not re-checked] All tournaments from Dec 2023 to Dec 2024 used random maps; 2022 used `defaultCapture` only.
  - The agent must work on *any* capture layout.
- **Ranking**:
  - Points are win 3, tie 1, loss 0. The results table shows Points %, Points, Win, Tie, Lost, FAILED and Score Balance.
  - A crash or timeout sets the score to ±1, which is a loss [verified: `CaptureRules.agent_crash`].
- **Submission**:
  - The tournament loads `my_team.py` from our repository root [source: PDF §3.3, README; also reported from pacman-eutopia code].
  - Our repository (public since 2026-11-21, user decision): <https://github.com/TianK003/Pacman-contest_UPF_2026>; this URL was submitted to UPF, so the repo must keep this name. Everything pushed to `main` is visible to everyone, including other teams.
  - It calls `create_team(first_index, second_index, is_red)` with **no extra arguments**, so the defaults are what plays.
- **Time limits are enforced**: the tournament runs with `catch_exceptions=True` (`-c`) [reported by research from pacman-eutopia `contest_manager.py` and a tournament log].

## Hard constraints: never violate

| # | Constraint | Source / reason |
|---|---|---|
| R1 | Each `choose_action` takes < 1 s on the tournament machine (our internal budget is much lower, see T-11). Never > 3 s. `register_initial_state` takes < 15 s per agent. The code also has a 900 s total cap per agent. | PDF §2.7, `capture.py` |
| R2 | No multithreading, multiprocessing, subprocesses or background computation. No computing during the opponent's turn. | CONTEST.md (same text at Berkeley and RMIT): disqualification |
| R3 | Never modify the framework (`pacman-contest/`), neither on disk nor at runtime (monkeypatching, changing constants, overriding engine methods). | CONTEST.md "Supporting files (do not modify)"; RMIT: "never tamper with the Pacman infrastructure" |
| R4 | Use information only through the provided API, i.e. the observation passed to `register_initial_state` / `choose_action` and the `CaptureAgent` helpers. See the fair-play policy below. | CONTEST.md "respect the provided APIs" |
| R5 | Never change the game dynamics. Do not mutate shared engine objects (T-01), seed the global `random` module (T-02), override `observation_function` (T-03), or swallow the framework's timeout exception (T-05). | R3/R4, and fairness |
| R6 | Never crash. An illegal action or an uncaught exception loses the game. | `game.py`, `capture.py` |
| R7 | Do not touch `sys.stdout` / `sys.stderr`. Print nothing confidential (logs are published), and keep printing off in tournament mode. | CONTEST.md "Warning"; RMIT/UoM disqualify for touching stdout/stderr |
| R8 | Do not write files to the current working directory during games. | CONTEST.md |
| R9 | Code must run on Python 3.8 with the standard library plus what the framework installs (`frozendict`). Any other library must first be requested from the professor, who installs on demand, and confirmed as installed (Q2). | PDF §3.1; Q2 answer 2026-10-22 |
| R10 | Academic integrity: our own original work. Do not copy other teams' code. (The README also says not to share the repo; the user made it public on 2026-11-21 for the tournament, Q5. Other people's code, `friends/` and `last_year_winners/`, is gitignored and has never been committed [verified 2026-11-21: `git log --all` on both paths is empty].) | `pacman-contest/README.md` |

## Fair-play policy (ours, stricter than the written rules)

The principle: **the agent may only use what an honest player watching its own observation could know.**

**Allowed**
- **Public accessors**: `get_walls`, `get_food` / `get_food_you_are_defending`, capsules, `get_score` / `self.get_score`, `get_agent_distances`, `get_distance_prob`, `get_initial_agent_position`, `get_legal_actions`, `get_agent_position`.
- **Own and teammate state**: our own and our teammate's `AgentState`.
- **Visible opponents**: an opponent's configuration when it is visible.
- **Our own memory**: of earlier observations (`observation_history`, our own data structures).
- **Values we can derive exactly**: time left (count moves, or read `data.timeleft`, which is not a private field), and when *we* ate a capsule.
- **Simulation on our own copies**, built without mutating shared objects: own data structures, or `generate_successor` on our copy with **newly created** `Configuration` objects for hypothesised opponents.
- **Shared memory between our two agents** (one shared Python object): allowed [source: professor, Q4, 2026-10-22].
- **Data files shipped next to `my_team.py`** (e.g. tuned weights), loaded read-only at startup: allowed [source: professor, Q6, 2026-10-22]. Resolve the path from `__file__`, never the working directory (T-21).

**Hidden-opponent fields: allowed (Q3, answered 2026-10-22)**
- Fields of *hidden* opponents that the engine leaves in the observation: `is_pacman`, `num_carrying`, `scared_timer`, `num_returned` [verified: E-000, E-023]. They are read through the public `get_agent_state(i)`, and reveal more than the documented observation model (position hidden; noisy distance only).
- The professor's answer: "If it is [available], I recommend you to use it and I'll make this info public to the rest of the teams" [source: email, 2026-10-22]. It is available (E-023). Our confirmation was sent (user), and the professor forwarded the information to every team [reported by the user, 2026-11-21], so all teams may use these fields.
- Implementation rule (kept): read them only through one switch (e.g. `USE_HIDDEN_OPPONENT_FLAGS`), so that turning it off is a one-line change if the ruling changes. New candidates may set it to `True`. `my_team.py` (greedy_v6) reads them (`USE_HIDDEN_OPPONENT_FLAGS = True`).

**Forbidden**
- **Mutating shared engine objects**: anything reachable from the observation that the engine shares, i.e. walls / layout, `Configuration` objects and `AgentState.start` (T-01).
- **Touching the global RNG**: calling `random.seed`, `random.setstate` or `random.getstate` on the global module (T-02).
- **Overriding** `observation_function` or `get_action`'s observation handling (T-03).
- **Private engine fields**: anything starting with `_`, e.g. `data._food_eaten`, `data._agent_moved`, `data._capsule_eaten`, `data._food_added` (T-04). Use public diffs instead.
- **Introspection**: `gc`, `inspect`, `sys._getframe`, `sys.modules` lookups of other teams, `__main__._display`, the `Game` object or other agents' objects.
- **Catching the timeout**: catching `TimeoutFunctionException`, including through bare `except:` or `except Exception:` around long computations (T-05).
- **External access**: network access, subprocesses, reading other teams' files.
- **Launch-time configuration**: anything that depends on command-line options (`--redOpts`) for tournament behaviour (T-09).

## Open questions for the instructors

| # | Question | Why it matters | Status |
|---|---|---|---|
| Q1 | What is the policy on AI/LLM tools? No source mentions it (PDF, UPF, EUTOPIA, RMIT, UoM, Berkeley). | academic integrity | **not asked**: left out of the email that was sent |
| Q2 | Which Python libraries exist on SNOW (numpy, scipy, torch)? CONTEST.md's library list is RMIT's text; the UPF tournament `requirements.txt` has no numpy [reported]. | whether learned models or vectorised code can run | **answered 2026-10-22**: installed on demand; tell the professor which ones (see below) |
| Q3 | May we use hidden opponents' `is_pacman`, `num_carrying`, `scared_timer` (readable via `get_agent_state`)? | hidden-opponent fields above | **answered 2026-10-22**: recommended, if available (it is, E-023) |
| Q4 | Is shared memory between our own two agents (team object / module variable) explicitly allowed? | coordination design | **answered 2026-10-22**: yes |
| Q5 | Public or private repo? The README says keep it private; the tournament code comments say it clones "a public repository" [reported]. | submission | **decided by the user 2026-11-21**: the repo is public for the test run, at <https://github.com/TianK003/Pacman-contest_UPF_2026> (not asked to the instructors) |
| Q6 | May we ship data files (e.g. learned weights) and load them in `register_initial_state`? RMIT/UoM allow it; UPF is silent. | learned methods | **answered 2026-10-22**: yes |
| Q7 | Grading: how much is tournament placement vs other deliverables (report? TEAM.md?)? The PDF says nothing. | priorities | not asked |
| Q8 | May we use public code from other teams as **local sparring opponents only** (never submitted)? | testing | not asked |
| Q9 | Is a `try/except` safety net in `choose_action` acceptable if it re-raises the framework's timeout exception? | crash safety vs R5 | not asked |
| Q10 | Are fixed layouts also used this year, or only `RANDOM<seed>`? | tuning targets | not asked |
| Q11 | Does the tournament play several games of a match in one process, and if so, may our agents keep what they learned about an opponent **in memory** (never in files) from one game to the next? | proposals.md section 4 (opponent learning across games) | not asked (added 2026-10-28); not used until answered |

When a question is answered, write the answer, the date and who answered, and update the affected rules and traps.

### Questions sent to the course professor, and the answers (2026-10-22)

Four questions were sent by email. Q1 (AI/LLM policy) was drafted on 2026-10-18 but **left out** of the email, so it is still unasked. Answers are quoted from the professor's reply, recorded 2026-10-22 [source].

| # (table above) | Question as sent | Answer (quoted) | What it means for us |
|---|---|---|---|
| Q2 | Which Python libraries are installed on the tournament machines (numpy, scipy, torch etc.)? | "We install them on-demand. Let me know which ones you are going to use." | Stdlib only until we name a library to him and he confirms it is installed. Request it before the test run (2026-11-23), so the test run would show an install problem. The lint (`eval/check_rules.py`) keeps rejecting these imports until then. |
| Q3 | May agents read `is_pacman`, `num_carrying` and `scared_timer` of opponents that are out of sight, through `get_agent_state`? Would accessing this information be considered a rule violation? | "I do not remember now, but is this information available? If it is, I recommend you to use it and I'll make this info public to the rest of the teams (pls, lmk)." | Allowed: it is available (E-023). Confirmation sent; the professor told every team [reported by the user, 2026-11-21]. Keep the single switch. |
| Q4 | Is shared memory between our own two agents (one shared Python object) allowed? | "Yes, there is no problem with that." | Shared beliefs and plans between our agents are open (H-S01, H-S09; agents.md ideas that waited on Q4). |
| Q6 | May we ship a data file next to `my_team.py`, for example tuned weights, and load it at startup? | "Yes, you can." | Tuned parameters may live in a separate read-only file, loaded relative to `__file__` (T-21). |
