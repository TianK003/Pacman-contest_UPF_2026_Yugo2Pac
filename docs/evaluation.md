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
- **Budget** [verified pilot]: about 5 s per game of wall time with 10 parallel workers on this laptop, i.e. 400 games ≈ 30–35 min.
- **Saturation**: an opponent that every candidate beats 100% of the time no longer discriminates (research: one UoM team found the baseline at 10/10 for several variants). Keep it in the gates, but don't let it dominate `PPG_P`.

## 4. Data splits (anti-overfitting)

**Seeds** (`eval/seeds/`, generated once with `random.Random(20261016)`, 8-digit like the tournament):

| Split | Size | Use |
|---|---|---|
| `tuning.txt` | 600 | anything: parameter search, RL training, debugging |
| `validation.txt` | 300 | accept/reject decisions (section 2) |
| `test.txt` | 100 | **locked**. Only for confirming a frozen release candidate, each use logged in experiments.md, at most 3 uses before new test seeds are drawn |

- If validation seeds have been used for many decisions (rule of thumb: > 10), draw a fresh validation list from a new generator seed and record it. Repeated decisions on the same seeds overfit them too [source: Cobbe et al. 2019 used separate train and test seed sets for procedurally generated levels; Zhang et al. 2018].
- Fixed layouts (`defaultCapture`, ...) are sanity checks only, because the tournament uses random maps.

**Opponents**:
- **Tuning pool**: opponents an optimiser may train or tune against.
- **Held-out pool**: never seen by any optimiser or by the person tuning [source: the Melting Pot test populations "are only for testing"].
- **Generalisation gap**: report `R = (PPG_tuning_pool − PPG_heldout) / PPG_tuning_pool`. This is our analogue of the joint-policy-correlation metric in Lanctot et al. 2017, where independently trained RL lost 34–72% of its reward against unseen partners or opponents.

## 5. The league (opponent pool, `eval/league.json`)

| Group | Members | Purpose |
|---|---|---|
| Reference | `baseline` | floor, saturation check |
| Our past versions | every accepted incumbent, frozen (`greedy`, ...) | forgetting check, non-transitivity |
| Specialists | `double_attack`, `turtle`, later: capsule rusher, border camper, kamikaze | style coverage |
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
4. **Screen**: about 10 seed-pairs against the incumbent and 2–3 pool members, on validation seeds. Drop clear failures.
5. **Full validation**: ≥ 40 seed-pairs against the whole pool, paired with the incumbent → apply the accept rule (section 2).
6. If accepted: freeze it, add it to `league.json` as a past version, and log it in experiments.md.
7. **Release**: release gate (section 2) → copy the frozen file to `my_team.py`.

## 8. Tooling (`eval/`)

| File | What |
|---|---|
| `evaluate.py` | runs colour-swapped game pairs in parallel through `capture.py -q -c` on seed lists; writes `eval/results/<run>.jsonl`; prints the summary: PPG + bootstrap CI, win % + exact Clopper–Pearson CI, W-T-L, crashes, time warnings, move-time stats, violations, head-to-head matrix, approximate Nash averaging, and with `--compare A B` a paired comparison overall **and per opponent** (needed for accept rule 3); `--resume` / `--dry-run` |
| `sentinel_team.py` | wraps a team during evaluation only. It records move times and runtime violations: walls mutated, shared `Configuration` mutated, global RNG seeded or read, thread / subprocess / `os.system`, file writes, `observation_function` overridden, illegal action |
| `check_rules.py` | AST lint for our team files: forbidden modules, private fields, global-RNG calls, shared-object writes, broad `except`, Python ≥ 3.9 syntax, prints and file I/O |
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

- **Memory**: each game uses about 50 MB (launcher + engine). On 2026-10-16 the system ran low on memory with other projects open, and the run was stopped (E-002). Use `--jobs 6` or fewer when other heavy programs are running.

**Known limitations**:
- There is no SPRT yet.
- There are no behavioural diagnostics yet (food eaten vs returned, deaths).
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
