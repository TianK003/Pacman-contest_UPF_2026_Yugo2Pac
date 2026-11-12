# Evaluation and agent comparison

This file says how we decide whether agent A is better than agent B, and how the evaluation is protected against overfitting and reward hacking.

- **Tools**: `eval/` (section 8).
- **Evidence tags**: as in [README.md](README.md).
- **Literature**: the references at the end were verified by our research agent on 2026-10-16 (title, venue and URL checked; some only via the abstract).

---

## 1. What we are actually optimising

**Tournament facts**:
- The tournament is a round-robin with 3/1/0 points per game, on a fresh `RANDOM<seed>` map every game.
  - [verified] The 2024 final had 18 teams and 5 games per pair.
  - [source: research] The 2024-25 UL final had 63 teams and about 124 games per team (about 2 per opponent); the winner earned 83% of the maximum points.
- A crash or timeout is a loss [verified].

**True objective**:

`J(agent) = E[ points per game | opponent ~ F, map ~ RANDOM, colour, starting team ]`

Here F is the unknown field of entrants.

**Consequences**:
1. **Optimise points, not win rate, Elo or score margin.** Under 3/1/0, a win plus a loss (3 points) beats two ties (2 points). Elo-style ½-point ties hide that [source: scoring rule; research note].
2. **Reliability is first-order.** One crash costs as much as a lost game, and most of the field is weaker than the top teams. Dropping points against weak teams hurts more than a narrow loss to the best.
3. **F is unknown**, so we need robustness over a *diverse* pool. Maximising against one opponent is not enough. Real game strategy spaces have cyclic (non-transitive) structure: A beats B beats C beats A [source: Czarnecki et al. 2020; Balduzzi et al. 2018].

## 2. Definitions

**Game pair.** One `RANDOM<seed>` map played twice, with colours swapped. This is the unit of analysis. It follows the "duplicate" format of computer poker (Littman & Zinkevich 2006) and the colour-reversed opening pairs of chess-engine testing (Fishtest; Van den Bergh), where treating the two games of a pair as independent is statistically wrong. Pair points ∈ {0, 1, 2, 3, 4, 6}.

**Common random numbers.**
- Candidate and incumbent are compared on the *same* (opponent, seed, colour) games.
- `RANDOM<seed>` fixes the map, the starting team and the engine's RNG stream, and our agents use fixed-seed private RNGs. So such games are reproducible [verified E-000], and differences come from the agents, not from luck of the draw.

**Pool (league) P.** The reference set of opponents (section 5).
- `PPG(A vs p)` is A's mean points per game against pool member p.
- `PPG_P(A)` is the weighted mean over the pool's distinct opponent *types*. Until we have a better model of the field, the weights are uniform, and the full matrix is always reported too.

**Metrics.** Every summary from `eval/evaluate.py` reports:

| Kind | Metric | Role |
|---|---|---|
| Primary | `PPG_P(A)` with a 95% bootstrap CI (resampling whole seeds) | what we try to raise |
| Head-to-head | `PPG(A vs B)` matrix | non-transitivity check |
| Robustness | `min_p PPG(A vs p)`; Nash-averaged payoff (max-entropy-Nash idea from Balduzzi 2018; we approximate it with multiplicative weights) | guards against "better on average, exploitable somewhere" |
| Gates | crashes/forfeits, engine time warnings, sentinel violations, lint errors, max move time | must be zero / under budget, otherwise rejected |
| Diagnostics | W-T-L, average margin, p95 move time; later: food eaten vs returned, deaths, stall time | understanding only, **never optimised** |

**Definition: A beats incumbent B ("accept A").** All of the following must hold:

1. **Compliance gates**:
   - A passes `eval/check_rules.py`.
   - Every evaluation game has 0 crashes/forfeits, 0 engine time warnings and 0 sentinel violations.
   - Max move time ≤ the internal budget (0.5 s, measured under 10-way parallel load).
2. **Pool improvement**: the paired `PPG_P(A) − PPG_P(B)` is > 0 with the 95% CI lower bound > 0, on **validation** seeds. This needs ≥ 40 seed-pairs per opponent, or a passed SPRT once that exists (section 3).
3. **No regression**: for every pool member p, the paired ΔPPG(A − B vs p) has a CI upper bound > −δ, with δ = 0.5. Also, the minimum PPG against all past versions must not drop by more than δ. This catches forgetting [source: AlphaStar tracked the "minimum win-rate against all past versions"].
4. **Head-to-head**: `PPG(A vs B) ≥ 1.5`, i.e. A is not losing to the incumbent.
5. **Confirmation** (release candidates only): repeat on validation seeds *not* used to select A. Picking the best of K variants on the same seeds is optimistically biased [source: Cawley & Talbot 2010, the "winner's curse"].

**Definition: A is "equivalent" to B** (for refactors and speed-ups): the CI of the paired Δ lies within [−δ, δ], and the gates pass.

**Release gate** (before the test run on 2026-11-23 and the final on 2026-12-04):
- Accepted under the rule above.
- ≥ 200 games with 0 crashes and 0 violations.
- Max move time within budget on Linux with Python 3.8.
- Evaluated **once** on the locked test seeds against the full pool *plus the held-out opponents*.
- The result is logged in experiments.md.

## 3. Statistics

- **Noise level** [verified pilot]: the points per game take values in {0, 1, 3}, with a standard deviation of roughly 1.2–1.5. So the 95% CI is about ±0.4 PPG at 40 games, ±0.2 at 160. Paired comparisons shrink this when outcomes correlate across versions.
- **Bootstrap** [implemented]: percentile bootstrap that resamples **seeds** (clusters). All games on one map stay together.
- **Sequential testing** [planned, not implemented]:
  - Wald's SPRT, as in Fishtest: pre-registered bounds (e.g. H0: Δ ≤ 0, H1: Δ ≥ 0.3 PPG), α = β = 0.05, a normal approximation on pair-level point differences.
  - Stop only by the rule, never by peeking.
  - Fishtest's worst-case expected length is about 1,046,535 / (nElo₁ − nElo₀)² games. By that estimate, small effects need many hundreds of games, so we can only resolve large effects. That is fine early on, when changes are big.
- **Budget** [verified E-009]: with `--delay-step 0` a game takes ~1.3 s on one core of this laptop (Ryzen 5 5500U); 6 workers play ~1,700 games in 8 minutes. (Before E-009 the engine's per-move sleep made it ~40 s per game.)
- **Saturation**: an opponent that every candidate beats 100% of the time no longer discriminates (research: one UoM team found the baseline at 10/10 for several variants). Keep it in the gates, but don't let it dominate `PPG_P`.

## 4. Data splits (anti-overfitting)

**Seeds** (`eval/seeds/`, generated once with `random.Random(20261016)`, 8-digit like the tournament):

| Split | Size | Use |
|---|---|---|
| `tuning.txt` | 600 | anything: parameter search, RL training, debugging, and **screening** candidates (decision 2026-10-17, see section 7) |
| `validation.txt` | 300 | accept/reject decisions (section 2). **Used up on 2026-11-08** (seeds 1–300) |
| `validation2.txt` | 300 | accept/reject decisions from 2026-11-08 on (user decision, E-036). Drawn by `eval/seeds/make_validation2.py` with `random.Random(20261108)`, 8-digit, none in tuning / validation / test [verified: 0 overlaps]. `--seeds validation2`. Used so far: 1–80 (E-038, V3: greedy_v5 rejected), 81–160 (E-039 stage 2: lab12_combo rejected), 161–240 (E-043: lab14_stuck passed, not promoted) |
| `validation3.txt` | 300 | accept/reject decisions of the team-brain experiment (user decision 2026-11-11, E-044). Drawn by `eval/seeds/make_validation3.py` with `random.Random(20261111)`, none in tuning / validation / validation2 / test [verified: 0 overlaps]. `--seeds validation3`. Used so far: 1–40 (E-044 decision run), 41–80 (E-044 confirmation run): `lab15_eyes` and `lab16_c2` confirmed, `lab16_swap` rejected |
| `test.txt` | 100 | **locked**. Only for confirming a frozen release candidate, each use logged in experiments.md, at most 3 uses before new test seeds are drawn. **Used 2 of 3** (E-021, greedy_v3 vs greedy_v2; E-037, greedy_v4 vs greedy_v3) |

- **Validation seeds used so far**: 1–20 (E-002), 21–60 (E-011), 61–100 (E-012), 101–180 (E-019), 181–220 (E-025, lab5_smart), 221–260 (E-031 V1, greedy_v4 accepted), 261–300 (E-032 V2, defender planner rejected). E-019 showed that one set of 40 maps can miss a real effect of about +0.2 (+0.05 on seeds 101–140, +0.26 on 141–180), so prefer ≥ 80 seeds per decision. **All 300 seeds of `validation.txt` are used (2026-11-08)**; decisions now use `validation2.txt` (table above). Keep a log of its use here like this one.
- **Tuning seeds used in the overnight session 2026-11-07/08** (screens, free to reuse but better avoided for a confirmation): 1–50 (leaf-net training data), 261–600 (E-028 … E-035).
- If validation seeds have been used for many decisions (rule of thumb: > 10), draw a fresh validation list from a new generator seed and record it. Repeated decisions on the same seeds overfit them too [source: Cobbe et al. 2019 used separate train and test seed sets for procedurally generated levels; Zhang et al. 2018].
- Fixed layouts (`defaultCapture`, ...) are sanity checks only, because the tournament uses random maps.

**Opponents**:
- **Tuning pool**: opponents an optimiser may train or tune against.
- **Held-out pool**: never seen by any optimiser or by the person tuning [source: the Melting Pot test populations "are only for testing"].
- **Generalisation gap**: report `R = (PPG_tuning_pool − PPG_heldout) / PPG_tuning_pool`. This is our analogue of the joint-policy-correlation metric in Lanctot et al. 2017, where independently trained RL lost 34–72% of its reward against unseen partners or opponents.

## 5. The league (opponent pool, `eval/league.json`)

**Reference pool (user decision 2026-10-18, E-013)**: we no longer play every league member against every other.
- New candidates play **only the 5 best currently performing agents**: `greedy_v2` (the incumbent, = `my_team.py`), `greedy` (v1), `feature` (F1), `camper` and `rusher`.
- They are listed in `eval/league.json` under `_reference_pool`.
- They were chosen by mean points per game on validation seeds 21–60 (E-011): greedy_v2's lab twin 2.26, greedy 1.89, feature 1.48, camper 1.36, rusher 1.24.
  - The next ones were field 0.95 and double_attack 0.94.
  - The `lab_breaker*` variants scored higher but were left out as near-duplicates of greedy_v2 (redundancy, below).
- The incumbent plays the same other members on the same seeds, so every candidate gets a paired comparison against it, plus its head-to-head game against it.
- The baseline is saturated (3.00 for every recent agent) and is kept only for smoke tests.
- Revise the pool when a candidate is accepted, or when another agent clearly outperforms a member. Log every change in experiments.md.
- **Update 2026-10-18 (user decision, E-017)**: `choke` and `exploit_v2` (E-015) joined, so the pool has **7 members**: `greedy_v2`, `greedy`, `feature`, `camper`, `rusher`, `choke`, `exploit_v2`. They were the hardest opponents for greedy_v2 in the pool (1.40 and 1.42 points per game for greedy_v2). Their strength in the 7-member round robin is in E-017.
  - `choke`: greedy_v2's attacker + `ChokeDefender` (H-M03), in `teams/sparring_v2.py`.
  - `exploit_v2`: the F1 attacker + `ShadowDefender`, written against greedy_v2's E-014 weaknesses.
- **Update 2026-10-18 (E-021)**: `greedy_v3` replaced greedy_v2 as the incumbent (= `my_team.py`). greedy_v2 stays in the pool as the previous incumbent, so the pool has **8 members**: `greedy_v3`, `greedy_v2`, `greedy`, `feature`, `camper`, `rusher`, `choke`, `exploit_v2`. Trimming it (e.g. dropping greedy v1 or rusher, the weakest in E-017) is a user decision.
- **Update 2026-11-08 (E-032)**: `greedy_v4` replaced greedy_v3 as the incumbent (= `my_team.py`). The pool members are unchanged until the user decides (adding greedy_v4 / lab5_smart, dropping weak members). Meanwhile new candidates are paired with greedy_v4 and also play greedy_v4 and lab5_smart as opponents.
- **Update 2026-11-08 (user decision, E-036)**: greedy_v4 is confirmed as the incumbent, and **`greedy_v4` and `lab5_smart` join the pool**, which now has **10 members**: `greedy_v4` (incumbent), `greedy_v3`, `greedy_v2`, `greedy`, `feature`, `camper`, `rusher`, `choke`, `exploit_v2`, `lab5_smart`. None was dropped. The pool Δ of the accept rule is over the members other than the incumbent; the games against the incumbent are the head-to-head. Pool numbers before this date used the old 8-member pool, so compare them only within one experiment.
- **Update 2026-11-12 (user decision, E-046)**: `greedy_v6` (= `lab16_c2`: greedy_v4 + the team brain's `relay` and `eyes`) replaced greedy_v4 as the incumbent (= `my_team.py`). It is a league entry; the pool members are unchanged until the user decides. Pair new candidates with greedy_v6 and play it head-to-head. Release gate of greedy_v6: not run.
- **Update 2026-11-08, later (user decision, E-036)**: `greedy` (v1) and `rusher` leave the pool (the user named them as the weakest / oldest and left further drops to the analysis). The pool now has **8 members**: `greedy_v4` (incumbent), `greedy_v3`, `greedy_v2`, `feature`, `camper`, `choke`, `exploit_v2`, `lab5_smart`. Analysis of the overnight runs (E-030, E-031, E-033, E-034; per-opponent paired Δ of 4–12 arms against their reference): every member's Δ correlates 0.75–0.95 with the rest of the pool's, so dropping two costs little signal; greedy and feature are the most saturated (reference arm 2.56 / 2.57 PPG). No further member was dropped, because each remaining one is a distinct style: feature is the only simple patrol-defender team left (it catches timid candidates: the Monte-Carlo arms lost most against it, E-033), camper the border camper, choke the cut-cell defender, exploit_v2 the shadow defender, greedy_v3 / greedy_v2 the past versions for the forgetting check (greedy_v2 had the most signal), lab5_smart the closest rule-based relative of the incumbent. greedy and rusher stay in the league for broader checks.

```powershell
# evaluate a new candidate against the reference pool (incumbent greedy_v4 paired on the same seeds; self-pairings are skipped)
venv\Scripts\python.exe eval\evaluate.py play --candidate <new> greedy_v4 --vs greedy_v4 greedy_v3 greedy_v2 feature camper choke exploit_v2 lab5_smart --seeds tuning --n-seeds 40 --run <name> --compare <new> greedy_v4
```

The full league below remains available for occasional broader checks.

**Specialists added 2026-10-18 (E-015)** live in `teams/sparring_v2.py`; see E-015 for how they were built.

**Held-out pool (2026-10-18, E-015)**: `heldout_a` and `heldout_b` in `eval/heldout/`, listed under `_heldout_pool` in `eval/league.json`.
- They were written by a separate agent that was told not to read our code, docs (except framework.md and rules.md) or results. It tested them only against `baseline_team` and each other.
- Isolation was by instruction, not enforced. That agent saw CLAUDE.md, which names greedy_v2's three features in one line.
- **Rules**:
  - Never screen, tune or debug against them, and never read their code or replays while designing candidates.
  - Use them for the release gate and for rare, logged checkpoints. Report only totals.
- Style labels (all we know): A = aggressive double attack with capsule use; B = defence first with a permanent guard and a cautious raider.
- A teammate writing a third one without seeing our code would make the pool more independent.


| Group | Members | Purpose |
|---|---|---|
| Reference | `baseline` | floor, saturation check |
| Our past versions | every accepted incumbent, frozen (`greedy`, ...) | forgetting check, non-transitivity |
| Specialists | `double_attack`, `turtle`; since 2026-10-17 (`teams/sparring_v1.py`): `camper` (greedy attacker + border camper), `camper2` (two border campers), `rusher` (capsule-first attacker), `baseline_plus` (baseline-style reflex team with return-at-5 and ghost avoidance); later: kamikaze | style coverage |
| Exploiters (planned) | agents written specifically to beat the current incumbent | find weaknesses before the tournament does [source: AlphaStar "main exploiters"; Timbers et al. 2022: head-to-head strength and exploitability are complementary] |
| Held-out (planned) | e.g. opponents a teammate writes without seeing our code; after 2026-11-23, proxies of real opponents' styles from the test-run replays | generalisation |

- **Freeze rule**: a league entry's file never changes after it has been benchmarked. New versions get new files (`greedy_v2.py`).
- **Redundancy**: near-duplicate versions would distort a plain average or Elo [source: Balduzzi et al. 2018], so group them, or watch the Nash-averaged score.

## 6. Reward hacking and Goodhart guards (for the tuning and RL stages)

**Threat model**:
- Any optimiser will exploit gaps between what we measure and J. That includes a black-box parameter tuner, an RL learner, and a human or AI assistant editing code until the number goes up [source: Amodei et al. 2016; Krakovna et al. 2020].
- No proxy is unhackable in general: raising the proxy can lower the true return unless one of the rewards is trivial [source: Skalse et al. 2022].
- Goodhart variants to expect [source: Manheim & Garrabrant 2018]:
  - regressional: the winner's curse
  - extremal: weird corner cases
  - adversarial: exploiting the evaluator

| # | Hack / failure | Guard |
|---|---|---|
| G1 | Overfit to one opponent's quirks. The baseline attacker only returns home when ≤ 2 food are left [verified in code], so beating it says little. | diverse pool; held-out opponents; `min_p` gate; exploiters |
| G2 | Overfit to evaluation seeds | seed splits; fresh confirmation seeds; locked test seeds |
| G3 | Winner's curse when picking the best of K variants | re-measure the winner on unused validation seeds before accepting |
| G4 | Shaped-reward farming in RL. In this game: eat food → die → the food is dumped back → eat it again. Let invaders in to farm kill rewards. Stall to farm survival rewards. (Same family as the looping CoastRunners boat.) | the reward is the true outcome (game points / returned food); shaping must be potential-based, `F = γΦ(s′) − Φ(s)`, which provably keeps optimal policies [source: Ng, Harada & Russell 1999]; behaviour audits from diagnostics and replays |
| G5 | Exploiting our own fast simulator (if we build one for RL), e.g. bugs or information the real game hides | final evaluation only ever in the real engine (`capture.py -c`); sim-vs-real agreement test |
| G6 | Rule-breaking "improvements": mutating shared engine objects, seeding the global RNG, overriding `observation_function`, private fields, swallowing timeouts | `check_rules.py` (static) + `sentinel_team.py` (runtime) in every evaluation. **Any violation is an automatic reject, whatever the score.** |
| G7 | Timing exploits: Windows never kills slow moves; deeper search "wins" locally and forfeits in the tournament | max/p95 move-time gate against the internal budget under parallel load; Linux check before release |
| G8 | Harness spoofing: printing fake result lines, writing score files | results come from the engine's score JSON; prints and writes are flagged by lint and the sentinel. Never use `-Q` for evaluation, because it also hides the engine's time warnings (T-46) |
| G9 | Margin inflation (crushing weak opponents) | margin is diagnostic only; the primary metric is points |
| G10 | Cycling: each version beats the previous one but loses to an older one | evaluate against the whole league, the head-to-head matrix and the minimum against past versions |
| G11 | Selective reporting (by us) | pre-registered accept rule; **every** run is logged in experiments.md, including failures and dead ends |

Ties are *not* a hack. Under 3/1/0 a tie against a stronger team is real value. We still watch the tie rate and wins, because the ranking breaks ties by wins.

## 7. Procedure

1. A new idea becomes a new team file or version, never an edit to a frozen file.
2. `python eval/check_rules.py <file>` passes.
3. Smoke test: one game per colour vs the baseline.
4. **Screen**: about 10 seed-pairs against the incumbent and the pool, on **tuning** seeds. Drop clear failures.
   - Decision 2026-10-17 (user): screening moved from validation to tuning seeds. With about 10 candidates per round, screening on validation seeds would exceed the "> 10 decisions" limit of section 4 within a week. Validation seeds are now used only for accept/reject decisions (step 5).
5. **Full validation**: ≥ 40 seed-pairs against the whole pool, paired with the incumbent → apply the accept rule (section 2).
6. If accepted: freeze it, add it to `league.json` as a past version, and log it in experiments.md.
7. **Release**: release gate (section 2) → copy the frozen file to `my_team.py`.

## 8. Tooling (`eval/`)

| File | What |
|---|---|
| `evaluate.py` | runs colour-swapped game pairs in parallel through `capture.py -q -c` on seed lists; writes `eval/results/<run>.jsonl`; prints the summary: PPG + bootstrap CI, win % + exact Clopper–Pearson CI, W-T-L, crashes, time warnings, move-time stats, violations, head-to-head matrix, approximate Nash averaging, the behaviour diagnostics table, and with `--compare A B` a paired comparison overall **and per opponent** (needed for accept rule 3); `--resume` / `--dry-run`. `--candidate` takes several entries (each plays every `--vs` entry), so candidates added later with `--resume` pair with the games already in the run. `summary` takes several runs (`--run r1 r2`), an `--agents` filter, and `--diag AGENT` for per-opponent diagnostics |
| `sentinel_team.py` | wraps a team during evaluation only. It records move times and runtime violations: walls mutated, shared `Configuration` mutated, global RNG seeded or read, thread / subprocess / `os.system`, file writes, `observation_function` overridden, illegal action. Since 2026-10-17 it also records **behaviour diagnostics** per agent from that agent's own observation: moves as Pacman, deaths (respawn at the start cell when the move led elsewhere), food carried at death, max carried, food returned (`num_returned` at the end), and standoff moves (a ghost within 2 columns of the border while an enemy ghost is in view; this counts defenders too) |
| `check_rules.py` | AST lint for our team files: forbidden modules, private fields, global-RNG calls, shared-object writes, broad `except`, Python ≥ 3.9 syntax, prints and file I/O |
| `replay_probe.py` | where an agent loses points (E-014). `classify --run R --agent A` sorts A's non-wins by kind (out-raced, deaths, defence, 0–0 standoff, ...) from the stored diagnostics. `replay --run R --agent A [--opponent O] [--label L] [--sample N] [--jobs J]` re-plays games with `--record` (deterministic; it warns if a replayed score differs) and re-simulates them from the true state: deaths in dead ends, whether the killer was in sight when we went in, food returned, invasions, defender distance, standoffs, capsules. `--trace FIRST LAST STEP` prints all positions; `--events` lists deaths and returns. Offline analysis only |
| `trace_team.py`, `trace_game.py` | decision trace (E-022). `trace_team.py` wraps one of our teams and records which rule produced every move; it passes every call through unchanged (60/60 traced games identical to evaluation records). `trace_game.py game --team T --vs O --seed S [--colour] [--from/--to] [--agent]` prints one game move by move and saves its replay; `profile --team T --vs ... --seeds tuning ...` gives rule shares over many games (`--by-opponent`, `--check-run RUN` for the pass-through check; test seeds refused). Outputs in `eval/traces/` (gitignored). Offline analysis only |
| `belief_probe/` | belief accuracy check (E-019): plays games in-process with two wrapper teams, ours logging the defender's belief and the opponent's agents logging their own positions, and reports how often the true cell is excluded, the probability on it, the distance from the most likely cell, and invader detection recall/precision. Offline analysis only |
| `league.json` | the opponent pool (path + `create_team` options) |
| `seeds/*.txt` | tuning / validation / test seed lists |

```powershell
# from the repo root
venv\Scripts\python.exe eval\check_rules.py teams\greedy_v1.py
venv\Scripts\python.exe eval\evaluate.py play --agents baseline greedy turtle --seeds validation --n-seeds 20 --run my_run
venv\Scripts\python.exe eval\evaluate.py play --candidate greedy_v2 --vs greedy baseline turtle --seeds validation --n-seeds 40 --run cand_v2 --compare greedy_v2 greedy
venv\Scripts\python.exe eval\evaluate.py summary --run my_run --compare greedy greedy_deadend
# continue an interrupted run (plays only games without a scored record); --dry-run just counts them
venv\Scripts\python.exe eval\evaluate.py play --agents baseline greedy turtle --seeds validation --n-seeds 20 --run my_run --resume --jobs 6
```

- **Memory**: each game uses about 50 MB (launcher + engine). On 2026-10-16 the system ran low on memory with other projects open, and the run was stopped (E-002). Use `--jobs 6` or fewer when other heavy programs are running. It happened again on 2026-10-17 with `--jobs 10` (E-007 screen stopped at 194/1,920 games; 4.4–4.8 GB of 15.3 GB were free before and after). Default to `--jobs 6` for long runs.

**Known limitations**:
- There is no SPRT yet.
- Behaviour diagnostics exist since 2026-10-17 (see the sentinel row). They are for understanding only and are **never optimised** (section 2). The summary shows team totals per game; "kills" are the opponent's deaths and "28-finish us / them" counts games that ended by the food rule, attributed to the team that was ahead. Not measured yet: food eaten (as opposed to returned), time spent per role.
- Progress lines of a background run appear only at the end on Python 3.8 (stderr is block-buffered when redirected to a file). Count the lines of `eval/results/<run>.jsonl` instead.
- The sentinel and the linter are tripwires, not proofs of compliance.
- Timing is measured on Windows under parallel load. That is pessimistic about load but optimistic about the hard 3 s kill (T-11).

## 9. How reliable is this? (assessment, E-004)

**Backed by established practice** (each element has a published source; see the references):
- Colour-swapped game pairs and common random numbers (chess-engine testing, poker duplicate matches).
- Clustered resampling (Agarwal et al. 2021; Van den Bergh on game pairs).
- Separate seed sets for tuning, selection and final testing (Cobbe et al. 2019; Cawley & Talbot 2010).
- A held-out opponent set (Leibo et al. 2021; Lanctot et al. 2017).
- Pool, matrix and Nash views (Balduzzi et al. 2018; Czarnecki et al. 2020).
- Potential-based shaping (Ng et al. 1999).
- Sequential tests (Wald 1945; Fishtest).

**Not backed by any paper (our choices)**:
- The thresholds: δ = 0.5, ≥ 40 seed-pairs, the 0.5 s budget, at most 3 test-seed uses.
- Uniform pool weights.
- Using multiplicative weights to approximate the Nash. It finds *a* Nash, not necessarily the max-entropy one that Balduzzi's invariance argument needs.
- The research found **no published evaluation methodology for Pacman CTF specifically**, so this exact protocol has not been validated by anyone else.

**Checked empirically by us**:

| Check | Result | Meaning |
|---|---|---|
| Determinism: the same seed played twice (greedy vs baseline, 400 moves) | identical move sequence [verified] | paired comparisons use exactly common random numbers. Repeating a seed adds **no** information, so the sample size is (seeds × colours) |
| Split-half: PPG on validation seeds 1–10 vs 11–20 | greedy–baseline 3.00/3.00; turtle–baseline 0.95/0.95; double_attack–baseline 0.60/0.35; greedy–double_attack 2.05/2.14 | the halves agree within the expected noise |
| Coverage of our seed-bootstrap 95% CI (simulated, 20 seeds × 2 games) | 93.5% at a 50% win rate; 92.8% at 85%; **73.2% at 97%** | slightly too narrow at 20 seeds, and **unreliable near PPG 0 or 3** (a 40/40 record prints [3.00, 3.00]). The summary now also prints an exact Clopper–Pearson win-rate CI. For 40/40 that is a win rate ≥ 91.2% |

**Remaining weaknesses, by importance**:
1. **External validity is the biggest unknown.** Every number measures performance *against our own pool*. The real field is unknown until the test run on 2026-11-23. A pool of our own variants shares our blind spots; the planned held-out opponents and exploiters only partly fix this.
   - **First measurement (E-015)**: greedy_v2 scores 1.70 points per game against the non-mirror reference pool but 1.16 against two blind-written held-out teams, a generalisation gap of R ≈ 32%. One of them (heldout_b) beats it.
   - The v1 → v2 gain carried over at about half its size (+0.23 vs +0.42).
2. **Small samples.** 20–40 seeds resolve only large differences (about ±0.3–0.4 PPG). Small improvements are invisible without hundreds of games.
3. **Independence assumptions.** The exact CI treats games as independent, while the two games on one map are correlated, so it is slightly optimistic.
4. **Multiple comparisons.** Scanning many pairings will produce some "significant" differences by chance. Hence the confirmation step.
5. **Timing.** Timing is measured on Windows under parallel load, not on the cluster.

## References (verified 2026-10-16 by the research agent unless marked)

- Balduzzi, Tuyls, Perolat, Graepel. *Re-evaluating Evaluation.* NeurIPS 2018. <https://papers.nips.cc/paper/2018/hash/cdf1035c34ec380218a8cc9a43d438f9-Abstract.html>
- Omidshafiei et al. *α-Rank: Multi-Agent Evaluation by Evolution.* Scientific Reports 9, 2019. <https://doi.org/10.1038/s41598-019-45619-9>
- Wellman. *Methods for Empirical Game-Theoretic Analysis.* AAAI 2006 (abstract only). <https://mlanthology.org/aaai/2006/wellman2006aaai-methods/>
- Lanctot et al. *A Unified Game-Theoretic Approach to Multiagent RL.* NIPS 2017. <https://arxiv.org/abs/1711.00832>
- Czarnecki et al. *Real World Games Look Like Spinning Tops.* NeurIPS 2020. <https://arxiv.org/abs/2004.09468>
- Vinyals et al. *Grandmaster level in StarCraft II using multi-agent RL.* Nature 575, 2019. <https://doi.org/10.1038/s41586-019-1724-z>
- Leibo et al. *Scalable Evaluation of Multi-Agent RL with Melting Pot.* ICML 2021. <https://proceedings.mlr.press/v139/leibo21a.html>
- Timbers et al. *Approximate Exploitability: Learning a Best Response.* IJCAI 2022. <https://ijcai.org/proceedings/2022/484>
- Bradley & Terry 1952, <https://doi.org/10.2307/2334029>. Davidson 1970 (ties; verified only via citations). Herbrich, Minka, Graepel, *TrueSkill*, NIPS 2006. Glickman 1999 (Glicko).
- Fishtest Mathematics: <https://github.com/official-stockfish/fishtest/wiki/Fishtest-Mathematics>. Van den Bergh, *The Accounting Identity*: <https://www.cantate.be/Fishtest/accounting_identity.pdf>. *Normalized Elo*: <https://www.cantate.be/Fishtest/normalized_elo_practical.pdf>
- Littman & Zinkevich. *The 2006 AAAI Computer Poker Competition.* ICGA Journal 2006 (duplicate matches). <https://www.martin.zinkevich.org/publications/competition.pdf>
- Burch et al. *AIVAT.* AAAI 2018. <https://ojs.aaai.org/index.php/AAAI/article/view/11481>
- Agarwal et al. *Deep RL at the Edge of the Statistical Precipice.* NeurIPS 2021. <https://arxiv.org/abs/2108.13264>
- Henderson et al. *Deep RL that Matters.* AAAI 2018. <https://ojs.aaai.org/index.php/AAAI/article/view/11694>
- Cawley & Talbot. *On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation.* JMLR 11, 2010. <https://www.jmlr.org/papers/v11/cawley10a.html>
- Wald. *Sequential Tests of Statistical Hypotheses.* Ann. Math. Statist. 1945. <https://projecteuclid.org/euclid.aoms/1177731118>
- Cobbe et al. *Quantifying Generalization in RL.* ICML 2019. <https://proceedings.mlr.press/v97/cobbe19a.html>
- Zhang, Vinyals, Munos, Bengio. *A Study on Overfitting in Deep RL.* 2018 (abstract only). <https://arxiv.org/abs/1804.06893>
- Amodei et al. *Concrete Problems in AI Safety.* 2016. <https://arxiv.org/abs/1606.06565>
- Krakovna et al. *Specification gaming: the flip side of AI ingenuity.* DeepMind blog 2020. <https://deepmind.google/discover/blog/specification-gaming-the-flip-side-of-ai-ingenuity/>
- Skalse et al. *Defining and Characterizing Reward Gaming* (arXiv title: "...Reward Hacking"). NeurIPS 2022. <https://arxiv.org/abs/2209.13085>
- Ng, Harada, Russell. *Policy invariance under reward transformations.* ICML 1999 (verified only via citations).
- Manheim & Garrabrant. *Categorizing Variants of Goodhart's Law.* 2018. <https://arxiv.org/abs/1803.04585>
