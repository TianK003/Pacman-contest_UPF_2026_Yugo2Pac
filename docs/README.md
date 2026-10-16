# Knowledge base — UPF EUTOPIA Pacman Capture the Flag

This folder is the team's memory: rules, verified engine facts, ideas, and everything we tried.
Read the relevant files before working on the agent, and update them when you finish.

| File | Holds | Update it when |
|---|---|---|
| [rules.md](rules.md) | Contest rules with sources, our hard constraints and fair-play policy, open questions for the instructors | the staff clarify something, or a new rule source turns up |
| [framework.md](framework.md) | Verified facts about the game engine, the observation, the random map generator, and how to run games | you verify (or disprove) an engine fact |
| [heuristics.md](heuristics.md) | Heuristic proposals, split into **map** heuristics (static, from the layout) and **sensory** heuristics (dynamic, from observations) | a heuristic is proposed, implemented, tested, adopted or rejected |
| [methods.md](methods.md) | Ways to build the agent (rules, search, MCTS, RL, ...) and how well each fits this contest | a method is evaluated or chosen |
| [traps.md](traps.md) | Pitfalls, including ways to break the rules by accident | you hit or discover a pitfall |
| [evaluation.md](evaluation.md) | How agents are compared: the objective, the accept rule, statistics, seed and opponent splits, the league, reward-hacking guards, tooling | the protocol or the tooling changes |
| [experiments.md](experiments.md) | Log book of every experiment, including failures | every run that informs a decision |

## Conventions

- **IDs**: map heuristics `H-M##`, sensory heuristics `H-S##`, methods `M-##`, traps `T-##`, experiments `E-###`, rules `R#`, open questions `Q#`. Cross-reference by ID (e.g. "E-004 tests H-M02 with M-03").
- **Status** (heuristics/methods): `idea` → `planned` → `implemented` → `tested` → `adopted` | `rejected`. Each status change needs an experiment ID.
- **Evidence tags**: every claim carries one tag.
  - `[verified]`: we checked it in the code or by running it. Say how, or name the experiment.
  - `[source]`: an official or external document says so. Give the link or file.
  - `[reported]`: another team's write-up claims it. This is anecdotal, and their ranks are self-reported.
  - `[untested]`: our own idea with no evidence yet.
- "Unknown" is a valid answer. Never present a guess as a fact.
- Dates are absolute (`YYYY-MM-DD`).

## Key dates [source: programming_project.pdf]

| Date | Event |
|---|---|
| 2026-11-23 | Test run of the tournament (feedback, changes allowed afterwards) |
| 2026-12-03 23:59 | Deadline |
| 2026-12-04 | Final run |
