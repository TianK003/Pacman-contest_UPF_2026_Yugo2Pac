# Learning on top of the greedy agents: RL, tuning and per-map mode selection

Research report, 2026-11-07 (user request). Written by a research agent with three literature sub-agents and local pilots. Repo at `fbc0757`, framework at `54cd83c`.

- **Scope**: how to improve the rule-based agent (`lab5_smart`, E-025) with learned parts, under our constraints: stdlib-only runtime, < 1 s per move, one laptop, ≈ 8 h of compute per night.
- **Status**: nothing here is built or tested in games. Every design is `[untested]` until it has an experiment ID. When one is built it moves to methods.md / proposals.md (RL-1 … RL-6 there are the earlier, shorter version of this file).
- **Tags** (docs/README.md):
  - `[verified]`: measured by us, here or in a cited experiment.
  - `[source: Key]`: from the literature row with that key in section 2, which has the link.
  - `[reported]`: student or blog claims.
  - `[untested]`: our own reasoning.

## 0. Summary

**Top designs, ranked by expected gain per hour of work** (details in section 3; all gains [untested]):

| # | design | key numbers | expected gain |
|---|---|---|---|
| 1 | **CMA-ES on lab5_smart's ~11 constants** (return_at, threat distance, standoff counts, open_goal margin and quantile, endgame length, …) | λ = 24 (default 11), μ = 12; **36 games per candidate** = 2 fresh tuning seeds × 9 opponents (pool + lab5_smart) × 2 colours, the same for the whole generation (CRN); 864 games ≈ 5.8 min per generation; **≈ 57 generations ≈ 49k games in 5.5 h**; report the distribution mean (re-checked every 8 generations on 320 fixed monitor games), not the best sample | +0.05 … +0.15 PPG |
| 2 | **Residual learned modules** trained by the same CMA-ES: a linear target-food scorer (≈ 10 features: bank distance, race margin, dead-end depth, cluster size, capsule distance, belief distance of their defender, …) + a linear bank-threshold correction (≈ 8 features), both initialised to zero, i.e. exactly lab5_smart | ≈ 18 weights, λ = 24, 36 games per candidate, ≈ 55 generations per night; 0.13 ms per move [verified cost] | +0.00 … +0.15 |
| 3 | **Opponent-type detection → best-response formation** (guard / double attack / turtle → mode) | detection in the first ~60 own moves from exact `is_pacman`; type × mode table from ≈ 1,440 CRN games against league specialists | ≈ 0 vs our pool; maybe +0.1 vs a mixed field |
| 4 | **Map-mode selector** (K = 4–6 modes + per-mode ridge regression of the paired gain on ≤ 8 map features) | go/no-go table: 400 tuning maps × 4 modes × 2 rotating opponents × 2 colours = **6,400 games ≈ 45 min**; build only if the cross-validated gain over the best single mode is ≥ +0.05 with CI > 0 | +0.00 … +0.05 |

**Findings that change the plan** [verified, section 1]:
1. **Per-map best-mode labels are noise.** In E-025's 11-mode × 50-map × 7-opponent table, the in-sample per-map oracle gains +0.20 PPG over the best single mode, but **−0.03 when cross-validated**. Never classify argmax labels: regress paired differences.
2. **Per-map effects exist** (τ ≈ 0.25–0.33 PPG for behaviour-changing switches), but **none of 11 cheap map features predicted them** beyond chance on 50 maps.
3. **"Food concentrated top-left" is rare.** The top-half share of enemy food lies in 0.33–0.60 on 90% of 300 maps. The larger half holds ≥ 2/3 of the food on only 9% of maps. Crossings (4–16) and dead-end food share (0.13–0.87) vary far more.
4. **Our seed budget can only resolve ≈ +0.1 PPG.** That needs 70–150 validation seeds of 16 games, and 120 are left. Gains of +0.05 are invisible to the accept rule.
5. **Pure-Python inference is cheap**: a linear model over 30 features takes 6 µs, MLP 30-32-1 0.1 ms, MLP 30-64-64-1 0.5 ms. Runtime is not the blocker for any design.
6. **Deep RL is not realistic tonight.** The blockers are the actor–learner engineering, sparse reward and opponent diversity, not CPU.


## 1. What our own data already says (local pilots, run for this report)

These pilots were run on 2026-11-07 for this report. They reuse existing results and read the framework's map generator; no repo file was changed. The scripts are in the session scratchpad, not in the repo.

### 1.1 Noise levels (E-025 screen, `eval/results/scr_labv5.jsonl`)

The E-025 screen is already a **mode × map × opponent × colour table**: 11 configurations (greedy_v3 and 10 `lab5_*` switch sets) × 50 tuning seeds (151–200) × 7 pool opponents × 2 colours = 7,700 games, all cells complete.

| quantity | value | tag |
|---|---|---|
| points per game (3/1/0), mean / SD | 2.13 / 1.24 | [verified] |
| SD of the per-game *paired* difference (variant − greedy_v3, same seed/opponent/colour) | median 1.21 (range 0.30–1.41) | [verified] |
| share of paired games with identical points | median 76% | [verified] |
| best single mode (SBS) on these 50 maps | `lab5_open`, 2.216 PPG (greedy_v3 2.047) | [verified] |

Consequence [untested arithmetic]:
- A paired comparison with G independent games has SE ≈ 1.2/√G PPG: 64 games → 0.15, 256 → 0.075.
- The seed-cluster bootstrap that the accept rule uses is wider. E-025's validation CI (+0.25 [+0.11, +0.40] over 560 paired games) implies an effective SD of ≈ 1.75 per game [verified arithmetic from the logged CI].
- To detect +0.10 PPG at 80% power (two-sided 5%) needs (2.8 × σ / 0.1)² paired games: ≈ 1,100 at σ = 1.2 and ≈ 2,400 at σ = 1.75, i.e. **70–150 seeds of 16 games**. +0.05 needs four times that.
- **Only 120 validation seeds are left** (evaluation.md section 4). A design whose realistic gain is below ~+0.1 PPG cannot be *accepted* with the current seed lists, whatever it does. Drawing a fresh validation list is a user decision (evaluation.md section 4).

### 1.2 Is there per-map signal to select on? (same table)

Per-map paired effect Δ_k(map) = mean over the map's 14 games of (mode k − greedy_v3). Between-map variance minus the within-map noise term gives the map heterogeneity τ² of each mode's effect. The noise term includes the mode × opponent spread, so τ² is, if anything, **under**estimated.

| mode | between-map var of Δ | noise var / n | τ (PPG) |
|---|---|---|---|
| lab5_open | 0.205 | 0.111 | 0.31 |
| lab5_all | 0.237 | 0.130 | 0.33 |
| lab5_intent | 0.239 | 0.136 | 0.32 |
| lab5_guard | 0.189 | 0.108 | 0.29 |
| lab5_flags | 0.157 | 0.093 | 0.25 |
| lab5_shared | 0.081 | 0.062 | 0.14 |
| lab5_endgame | 0.007 | 0.007 | 0.01 |

| selection test | gain over SBS | tag |
|---|---|---|
| in-sample "oracle best mode per map" (VBS on the noisy table) | **+0.200** (apparent) | [verified] |
| cross-validated per-map oracle: pick the best of 11 modes on a random half of each map's games, score it on the other half (200 splits) | **−0.029** | [verified] |
| cross-validated per-opponent oracle: pick the best mode per opponent on 25 seeds, score on the other 25 | **−0.010** | [verified] |

What this means:
- Each mode's effect does vary by map (τ ≈ 0.25–0.33 PPG for the switches that change behaviour) [verified, lower-bound estimate, assuming games on one seed share only the map].
- But the per-map "best mode" label, measured from 7 games, is noise. The in-sample oracle's +0.20 is pure winner's curse: picking the max of 11 noisy means. Cross-validated, per-map selection *loses* 0.03 [verified].
- So **never train a classifier on "best mode per map" labels**. Regress paired differences on features over many maps instead (section 3.A).

### 1.3 Do cheap map features predict the per-map effect? (same 50 maps)

Eleven features were computed from `maze_generator.generate_maze(seed)`: crossings, share and depth of food in dead ends (leaf pruning), border-to-food distances, food top/bottom offset, capsule-to-border distance, loops per cell, tree fraction. Each was correlated with Δ_k(map) for 4 modes.

- No correlation exceeded what chance gives (|r| ≤ 0.28 at n = 50; about 2 of 44 tests are expected beyond |r| = 0.28 by chance) [verified].
- The largest were tree fraction vs `lab5_flags` −0.28, and capsule-to-border distance vs `lab5_open` −0.21.
- greedy_v3's own per-map PPG correlates −0.26 with the number of crossings: more crossings, fewer points [verified, n = 50, borderline].

Map statistics over 300 tuning maps (34 × 18) [verified]:

| feature (enemy half, as seen by red; maps are point-symmetric, 300/300) | p5 | median | p95 |
|---|---|---|---|
| share of enemy food in the top half | 0.33 | 0.47 | 0.60 |
| share in the larger (top or bottom) half | ≥ 0.50 by definition | 0.57 | 0.67 (max 0.77) |
| share of enemy food in the third nearest the border | 0.23 | 0.37 | 0.53 |
| share in the farthest third | 0.00 | 0.13 | 0.33 |
| border crossings (50 maps) | 4 (min) | 11.9 (mean) | 16 (max) |
| share of enemy food in tree-like dead-end parts (50 maps) | 0.13 (min) | 0.49 (mean) | 0.87 (max) |
| capsules per side | 2 | 2 | 2 |

So the premise "a map whose food is concentrated top-left" is rare: in 90% of maps the top-half share is between 1/3 and 3/5 [verified]. Dead-end share and crossings vary much more, so they are the better candidate selector features [untested].

### 1.4 Cost of tiny learned models in pure CPython 3.8 (this laptop, venv 3.8.10, no numpy)

| model | time per call | tag |
|---|---|---|
| linear, 30 features (`sum(map(mul, w, x))`) | 6.4 µs | [verified] |
| MLP 30-16-16-1 (ReLU) | 85 µs | [verified] |
| MLP 30-32-1 | 102 µs | [verified] |
| MLP 30-64-64-1, nested loops | 928 µs | [verified] |
| MLP 30-64-64-1, `sum(map(mul))` | 502 µs | [verified] |
| MLP 64-64-64-5 | 720 µs | [verified] |
| 30 candidate foods × linear 30 | 0.13 ms | [verified] |
| 30 candidate foods × MLP 30-32-1 | 3.2 ms | [verified] |

That is ≈ 80 ns per multiply-add with `sum(map(operator.mul, row, x))` [verified]. A 50,000-MAC network (a small CNN on an egocentric crop) would take ≈ 4 ms [untested extrapolation]. With lab5_smart's max move at 0.151 s (E-025) and the 0.5 s internal budget, **runtime is not the blocker for any design here** [verified for the sizes above]. The SNOW cluster is probably slower (CLAUDE.md), so keep a 3–5× margin.

---

## 2. Literature

**Read level**: *full* = full text or key sections read; *abstract* = abstract, index page or secondary summary only.

The sources were opened by research agents on 2026-11-07. Numbers are quoted only where an agent saw them in the source. A `[source: Key]` tag elsewhere in this file points to the row with that key, which holds the link.

### 2.1 Per-instance algorithm selection and configuration

| key | reference | read | claims relevant to us |
|---|---|---|---|
| Rice 1976 | J. R. Rice, "The Algorithm Selection Problem", *Advances in Computers* 15:65–118, 1976. [doi:10.1016/S0065-2458(08)60520-3](https://doi.org/10.1016/S0065-2458(08)60520-3) | citation + restatement in Kerschke 2019 | Problem space × algorithm space × performance metric; find a selector S(features(instance)) → algorithm. **Our mapping**: instance = the map, features = startup map statistics, algorithms = modes, metric = points per game |
| Xu 2008 (SATzilla) | Xu, Hutter, Hoos, Leyton-Brown, "SATzilla: Portfolio-based Algorithm Selection for SAT", *JAIR* 32:565–606, 2008. [doi:10.1613/jair.2490](https://doi.org/10.1613/jair.2490), [arXiv 1111.2249](https://arxiv.org/abs/1111.2249) | full (method sections) | One **ridge regression per solver** on log runtime, with forward feature selection and quadratic expansion. Lasso/SVM/GP regression "did not improve predictive performance enough to justify this additional cost". 48 features. Censored (noisy) labels are imputed, not dropped. Because predictions are imperfect, **dropping a solver can improve the portfolio** |
| Xu 2012 (SATzilla 2011/12) | Xu et al., SATzilla2012 solver description, [PDF](https://www.cs.ubc.ca/~kevinlb/papers/2012-SATzilla2012-Solver-Description.pdf); "Evaluating Component Solver Contributions to Portfolio-Based Algorithm Selectors", SAT 2012, [PDF](https://www.cs.ubc.ca/~hoos/Publ/XuEtAl12-preprint.pdf) | full | **Cost-sensitive pairwise** decision forests: one per solver pair, label = which is better, weight = \|performance difference\|, majority vote. Near-ties carry almost no weight. 10-fold CV closed 27.7% / 53.2% / 90.1% of the gap between the category winner and the VBS (Application / Crafted / Random). The most valuable portfolio members were often **not** the best single solvers |
| Lindauer 2015 (AutoFolio) | Lindauer, Hoos, Hutter, Schaub, "AutoFolio: An Automatically Configured Algorithm Selector", *JAIR* 53:745–778, 2015. [doi:10.1613/jair.4726](https://doi.org/10.1613/jair.4726); IJCAI-17 summary [PDF](https://www.ijcai.org/proceedings/2017/0715.pdf) | IJCAI summary (full); JAIR not read | SMAC configures the selector itself (6 approaches + hyperparameters) on 10-fold CV with a held-out test set. On 13 ASlib scenarios: new best on 7, tie on the rest, 1.3–15.4× speed-up over the SBS. **No single selection approach dominates.** On a noisy scenario several fixed approaches were *worse* than the SBS. With few affordable evaluations, a small configuration space is better |
| Kadioglu 2010 (ISAC) | Kadioglu, Malitsky, Sellmann, Tierney, "ISAC – Instance-Specific Algorithm Configuration", ECAI 2010, pp. 751–756. [PDF](https://ai.dmi.unibas.ch/research/reading_group/kadioglu-et-al-ecai2010.pdf) | full | Normalise features, cluster (g-means), dissolve small clusters (minimum 30–100 instances), tune one configuration per cluster plus a global fallback. Instances far from every cluster (≈ 9%) use the fallback. Gains where one configuration is not robust (SAPS 14.6 → 5.0 s); none where it is (Hegel 1.95 → 1.92 s). "Helps prevent over-tuning" |
| Xu 2010 (Hydra) | Xu, Hoos, Leyton-Brown, "Hydra: Automatically Configuring Algorithms for Portfolio-Based Selection", AAAI 2010, pp. 210–216. [PDF](https://www.cs.ubc.ca/~hoos/Publ/XuEtAl10.pdf) | full | Builds the portfolio from **one parameterised solver**. Each iteration tunes a new configuration against "min(candidate, current portfolio)" per instance, so it is rewarded only where it adds. 41 parameters, 7 iterations. PAR-10 631 vs 1129 for the best single challenger (RAND). Test tracked training |
| Bischl 2016 (ASlib) | Bischl et al., "ASlib: A Benchmark Library for Algorithm Selection", *AIJ* 237:41–58, 2016. [arXiv 1506.02465](https://arxiv.org/abs/1506.02465) | abstract | A standard scenario format and repository; the SBS/VBS gap-closed metric is the norm |
| Kerschke 2019 | Kerschke, Hoos, Neumann, Trautmann, "Automated Algorithm Selection: Survey and Perspectives", *Evolutionary Computation* 27(1):3–45, 2019. [arXiv 1811.11597](https://arxiv.org/abs/1811.11597) | key sections | SBS = best on average, VBS = per-instance oracle. State-of-the-art selectors close **25–96%** of the gap. Gains need **high complementarity among the algorithms and cheap, informative features** |
| Lindauer 2019 (AS competitions) | Lindauer, van Rijn, Kotthoff, "The Algorithm Selection Competitions 2015 and 2017", [arXiv 1805.01214](https://arxiv.org/abs/1805.01214) | relevant sections | Best remaining gap ≈ 33% (2015) / 38% (2017). None of the 2015 differences were significant. **On SAT12-RAND (single noisy runs) most systems were no better than the SBS**, although the VBS was 12× faster; the authors recommend removing that scenario. On OPENML-WEKA 6 of 8 submissions were at or below SBS level |
| Cameron 2016 | Cameron, Hoos, Leyton-Brown, "Bias in Algorithm Portfolio Performance Evaluation", IJCAI 2016. [PDF](https://www.cs.ubc.ca/~cchris13/docs/ijcai16_bias.pdf) | abstract + key results | A VBS taken as the minimum over **single noisy runs is optimistically biased**. The bias grows with the number of algorithms and shrinks with more runs. Random SAT PAR-10: biased VBS 5,961 vs unbiased 8,367 (SBS 21,350). **This is exactly our in-sample +0.20 vs cross-validated −0.03 (section 1.2)** |
| Balcan 2021 | Balcan, Sandholm, Vitercik, "Generalization in Portfolio-Based Algorithm Selection", AAAI 2021. [arXiv 2012.13315](https://arxiv.org/abs/2012.13315) | abstract | The generalisation gap grows with portfolio size and selector complexity. **With a large portfolio, overfitting is unavoidable even for a very simple selector** → keep K small |
| Smith & Winkler 2006 | Smith, Winkler, "The Optimizer's Curse: Skepticism and Postdecision Surprise in Decision Analysis", *Management Science* 52(3):311–322, 2006. [doi:10.1287/mnsc.1050.0451](https://doi.org/10.1287/mnsc.1050.0451) | abstract + intro | The maximum of unbiased noisy estimates is biased high. Fix: Bayesian shrinkage, ranking by posterior means |
| Efron 2011 | Efron, "Tweedie's Formula and Selection Bias", *JASA* 106(496):1602–1614, 2011. [doi:10.1198/jasa.2011.tm11181](https://doi.org/10.1198/jasa.2011.tm11181) | citation + abstract fragment | An empirical-Bayes correction for extreme (selected) estimates |
| Cawley & Talbot 2010 | Cawley, Talbot, "On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation", *JMLR* 11:2079–2107, 2010. [link](https://jmlr.org/papers/v11/cawley10a.html) | abstract | Selection-criterion variance causes overfitting "of comparable magnitude to differences in performance between learning algorithms". Keep selection and evaluation separate (already our accept rule, clause 5) |
| Li 2010 (LinUCB) | Li, Chu, Langford, Schapire, "A Contextual-Bandit Approach to Personalized News Article Recommendation", WWW 2010. [arXiv 1003.0146](https://arxiv.org/abs/1003.0146) | abstract | Linear payoff model + UCB, evaluated offline on logged random traffic (33M events): 12.5% click lift over a context-free bandit |
| Agrawal & Goyal 2013 | Agrawal, Goyal, "Thompson Sampling for Contextual Bandits with Linear Payoffs", ICML 2013. [arXiv 1209.3352](https://arxiv.org/abs/1209.3352) | abstract | Thompson sampling with a Gaussian prior for linear contextual bandits, with a regret bound |

**Games**:

| key | reference | read | claims relevant to us |
|---|---|---|---|
| Mendes 2016 | Mendes, Togelius, Nealen, "Hyper-heuristic General Video Game Playing", IEEE CIG 2016. [doi:10.1109/CIG.2016.7860398](https://doi.org/10.1109/CIG.2016.7860398), [PDF](http://www.nealen.net/papers/Mendes2016HyperHeuristic.pdf) | full | 7 controllers, 205 game levels, **14 cheap features of the initial state**, label = best controller. Accuracy: SVM .713 (shuffled CV) but **.637 when CV is grouped by game**; MLP .698 → **.480 (below ZeroR .504)**: overfitting showed only under grouped CV. Victories 721 (SVM selector) vs 654 (best single controller). The selector mostly picked the 3 "safe" strong controllers: **a wrong risky pick costs more than a missed specialist**. (Whether the victory totals are on held-out games is unclear) |
| Bontrager 2016 | Bontrager, Khalifa, Mendes, Togelius, "Matching Games and Algorithms for General Video Game Playing", AIIDE 2016, pp. 122–128. [doi:10.1609/aiide.v12i1.12884](https://doi.org/10.1609/aiide.v12i1.12884) | full | 23 controllers × 49 games × 25 plays. Feature clusters and performance clusters agreed only 40.8%: **"features are not good indicators"**. A decision tree on them "was just memorizing the data". The final 2-feature rule gave 695 vs 637 wins, apparently in-sample |
| Horn 2016 | Horn, Volz, Pérez-Liébana, Preuss, "MCTS/EA Hybrid GVGAI Players and Game Difficulty Estimation", IEEE CIG 2016. [PDF](https://repository.essex.ac.uk/19032/1/MCTSEAHybridGVG.pdf) | abstract + conclusion | Game features vs controller win rates: maximal information coefficient only 0.18–0.41. Feature-based selection is left as future work. The 2015 GVGAI leg winners switched technique by game type (e.g. deterministic → best-first search) |
| Tavares 2016 | Tavares, Azpúrua, Santos, Chaimowicz, "Rock, Paper, StarCraft: Strategy Selection in Real-Time Strategy Games", AIIDE 2016, pp. 93–99. [doi:10.1609/aiide.v12i1.12857](https://ojs.aaai.org/index.php/AIIDE/article/view/12857) | abstract | Strategy (bot) selection as a normal-form game between strategies: Nash play vs safe exploitation. MegaBot beat each of its own components, but placed 9th of 22 at AIIDE 2016 [reported, secondary summary] because no component beat the strongest bots → **selection cannot exceed the portfolio's best member by much** |
| Tavares 2018 | Tavares, Anbalagan, Marcolino, Chaimowicz, "Algorithms or Actions? A Study in Large-Scale Reinforcement Learning", IJCAI 2018. [PDF](https://eprints.lancs.ac.uk/125040/4/ijcai_2018.pdf) | page 1 | Conditions under which learning over a few algorithms beats learning over primitive actions within a finite training budget (supports macro-level learning, as in designs C/E1) |
| Churchill & Buro 2013 | Churchill, Buro, "Portfolio Greedy Search and Simulation for Large-Scale Combat in StarCraft", IEEE CIG 2013. [doi:10.1109/CIG.2013.6633643](https://doi.org/10.1109/CIG.2013.6633643) | abstract | Hill-climbing over assignments of scripts to units beats alpha-beta and UCT in fights of up to 50 vs 50 units at 40 ms per search |
| Barriga 2015 | Barriga, Stanescu, Buro, "Puppet Search: Enhancing Scripted Behavior by Look-Ahead Search with Applications to Real-Time Strategy Games", AIIDE 2015, pp. 9–15. [AAAI OJS](https://ojs.aaai.org/index.php/AIIDE/article/view/12779) | abstract + results | Search over script choices "matches or outperforms all of the individual scripts" (100 games per pair, 10 maps). It is **not significantly better than the best script, but more robust** across opponents. A best script per opponent would require knowing the opponents in advance |
| StarCraft bots | AIIDE StarCraft AI Competition reports; AIUR, PurpleWave, BananaBrain descriptions (via search snippets and the satirist.org blog) | secondary only | [reported] Bots learn opening choice per opponent (UCB-1) and condition on map / start positions, using file I/O across rounds that the organisers allow. Learning helped "modestly". Many table cells rest on 1–5 games. (Our tournament forbids file writes, and cross-game memory is Q11) |
| Gehring 2018 | Gehring et al., "High-Level Strategy Selection under Partial Observability in StarCraft: Brood War", [arXiv 1811.08568](https://arxiv.org/abs/1811.08568) | abstract | RL-learned strategy switching gives "substantial" win-rate gains over a fixed strategy (no numbers in the abstract) |

**What the selection literature implies for design A** [untested synthesis]:
- (1) Selection pays when the portfolio is complementary and the features are informative. Bontrager 2016 and Horn 2016 found game features weakly informative even across *very different* games. Our maps are far more alike than GVGAI games.
- (2) Under noisy labels, most selectors fail to beat the SBS (SAT12-RAND, Lindauer 2019), and the per-instance oracle is optimistically biased (Cameron 2016). Our pilot reproduces both (section 1.2).
- (3) Use cost-sensitive pairwise or regression models with shrinkage, never argmax labels (SATzilla 2012, Smith & Winkler 2006).
- (4) Keep K small (Balcan 2021, AutoFolio).
- (5) Cross-validate grouped by map (Mendes 2016).
- (6) Fall back to the SBS when unsure (ISAC; Mendes' "safe" picks).

### 2.2 Evolution strategies, CMA-ES, noisy fitness, racing

| key | reference | read | claims relevant to us |
|---|---|---|---|
| Salimans 2017 | Salimans, Ho, Chen, Sidor, Sutskever, "Evolution Strategies as a Scalable Alternative to Reinforcement Learning", [arXiv 1703.03864](https://arxiv.org/abs/1703.03864) | full | Antithetic (±ε) sampling and **rank-based fitness shaping** ("removes the influence of outlier individuals"). Fixed σ ("no benefit from adapting σ"). ES's gradient estimate does not depend on the episode length, whereas the policy-gradient variance grows with it. Results: ES needed 3–10× the data of A3C on Atari; it beat 1-day A3C on 23 of 51 games after 1 h on 720 CPUs. One hyperparameter set for all games |
| Hansen 2016 | Hansen, "The CMA Evolution Strategy: A Tutorial", [arXiv 1604.00772](https://arxiv.org/abs/1604.00772) | partial (App. A–B) | λ = 4 + ⌊3 ln n⌋ ("can be increased"; decreasing "is not recommended"), μ = ⌊λ/2⌋. For a random start in [a, b]ⁿ, σ₀ = 0.3(b − a); rescale variables whose ranges differ by orders of magnitude. Change no setting except "increasing the population size … and possibly decreasing α_cov on noisy functions". A flat fitness landscape suggests reformulating the objective |
| Auger & Hansen 2005 (IPOP) | Auger, Hansen, "A Restart CMA Evolution Strategy With Increasing Population Size", IEEE CEC 2005, pp. 1769–1776. [doi:10.1109/CEC.2005.1554902](https://doi.org/10.1109/CEC.2005.1554902) | partial | Restart with λ × 2 each time. On multimodal functions it was significantly better in 29 of 60 cases |
| Hansen et al. 2009 (UH-CMA-ES) | Hansen, Niederberger, Guzzella, Koumoutsakos, "A Method for Handling Uncertainty in Evolutionary Optimization…", *IEEE TEC* 13(1):180–197, 2009. [doi:10.1109/TEVC.2008.924423](https://doi.org/10.1109/TEVC.2008.924423), [draft PDF](http://www.cmap.polytechnique.fr/~nikolaus.hansen/TEC2009.pdf) | partial | "Increasing only λ is inferior to resampling … but **increasing μ and λ is preferable to resampling**" (citing Arnold). Measure noise by re-evaluating a *random* subset (r = max(0.1, 2/λ)) and counting rank changes. If noisy: evaluation time × 1.5 up to a cap, then σ × (1 + 2/(n+10)). Picking the best points for re-evaluation keeps selecting lucky outliers. Implemented as pycma's `NoiseHandler` [verified locally] |
| Hellwig & Beyer 2020 | Hellwig, Beyer, *Theoretical Computer Science* 832:98–122, 2020. [PDF](https://hgbeyer.github.io/www/New-Papers/TCS-HB18b.pdf) | partial (intro) | For (μ/μ_I, λ)-ES on quadratic functions, a larger population beats resampling. Intermediate recombination ("genetic repair") tolerates many rank changes. UH-CMA-ES's rank-change test is "too pessimistic" |
| Arnold & Beyer 2006 | Arnold, Beyer, "A General Noise Model and Its Effects on Evolution Strategy Performance", *IEEE TEC* 10(4):380–391, 2006. [doi:10.1109/TEVC.2005.859467](https://doi.org/10.1109/TEVC.2005.859467) | citation only | (cited for completeness; claims about it above are second-hand via Hansen 2009 / Hellwig & Beyer) |
| Kocsis & Szepesvári 2006 | Kocsis, Szepesvári, "Universal Parameter Optimisation in Games Based on SPSA", *Machine Learning* 63:249–286, 2006. [PDF](https://www.jhuapl.edu/spsa/PDF-SPSA/Kocsis_Szepesvari_MachineLearning06.pdf) | partial | **CRN** works because Var(F⁺ − F⁻) = Var F⁺ + Var F⁻ − 2 Cov. It improves the convergence rate from O(t^−1/3) to O(t^−1/2). **Partial CRN**: share the environment randomness (for us, the map seed) between the variants compared. For a fixed budget, **1 evaluation per perturbation and more perturbations** minimised the error. Plain SPSA "failed to make progress" on poker; with CRN + antithetic + RPROP it gained up to 0.19 small bets per game |
| Kleinman 1999 | Kleinman, Spall, Naiman, "Simulation-Based Optimization with Stochastic Approximation Using Common Random Numbers", *Management Science* 45(11):1570–1578, 1999. [doi:10.1287/mnsc.45.11.1570](https://doi.org/10.1287/mnsc.45.11.1570) | abstract | The CRN rate improvement for finite-difference and SPSA gradient estimates |
| Christophe 2015 | Christophe, Decock, Liu, Teytaud, "Variance Reduction in Population-Based Optimization: Application to Unit Commitment", [doi:10.1007/978-3-319-31471-6_17](https://doi.org/10.1007/978-3-319-31471-6_17) | abstract | CRN can be "very efficient" or "detrimental" depending on the noise model → **check once** that CRN helps us (e.g. compare rank stability with and without shared seeds) |
| Birattari 2002 (F-Race) | Birattari, Stützle, Paquete, Varrentrapp, "A Racing Algorithm for Configuring Metaheuristics", GECCO 2002, pp. 11–18. [PDF](https://cs.ubc.ca/labs/algorithms/Courses/CPSC536H-10/Materials/BirEtAl02.pdf) | full | Evaluate the surviving candidates instance by instance, ranked within each instance (blocking). Drop the significantly worse ones by Friedman test. 256 configurations within 5 × 256 runs ended with ≈ 8 survivors seen on ≈ 78 instances each, matching a brute force that used ≈ 19,950 runs |
| López-Ibáñez 2016 (irace) | López-Ibáñez et al., "The irace package: Iterated racing for automatic algorithm configuration", *Operations Research Perspectives* 3:43–58, 2016. [doi:10.1016/j.orp.2016.09.002](https://doi.org/10.1016/j.orp.2016.09.002) | user guide v2.0 (paper page 403) | Defaults: first test after 5 instances, Friedman test, elitist. Use the t-test when the mean matters (our case: mean points). For heterogeneous instances, raise firstTest to ≈ 10 and test elites on separate instances |
| Hutter 2011 (SMAC) | Hutter, Hoos, Leyton-Brown, "Sequential Model-Based Optimization for General Algorithm Configuration", LION 5, 2011. [PDF](https://www.cs.ubc.ca/~hutter/papers/11-LION5-SMAC.pdf) | partial | A challenger is compared with the incumbent only on the ⟨instance, seed⟩ pairs both have run: "the variance in this comparison is lower if we use the same N instances" (= our paired seeds) |
| MacAlpine 2012 | MacAlpine, Barrett, Urieli, Vu, Stone, "Design and Optimization of an Omnidirectional Humanoid Walk: A Winning Approach at the RoboCup 2011 3D Simulation Competition", AAAI 2012. [PDF](https://www.cs.utexas.edu/~pstone/Papers/bib2html-links/AAAI12-MacAlpine.pdf) | full | CMA-ES on 14 of 40+ parameters, 210,000 evaluations in under a day on a cluster (population size not given). **Fitness from tasks resembling real play worked better**; parameter sets learned in isolation were incompatible. 24/24 wins, 136–0 |
| Urieli 2011 | Urieli, MacAlpine, Kalyanakrishnan, Bentor, Stone, "On Optimizing Interdependent Skills: A Case Study in Simulated 3D Humanoid Robot Soccer", AAMAS 2011, pp. 769–776. [PDF](https://www.cs.utexas.edu/~pstone/Papers/bib2html-links/AAMAS11-urieli.pdf) | partial | With a 15,000-sample budget, CMA-ES did best at **50 generations × population 30 × 10 averaged runs**. A final re-evaluation is "necessary because of the noise". **Win/loss and goal difference were "extremely noisy"**, so they used time-to-score as a proxy. The best walk took ≈ 45,000 samples, 5–7 h |
| MacAlpine & Stone 2018 | MacAlpine, Stone, "Overlapping Layered Learning", *AIJ* 254:21–43, 2018. [doi:10.1016/j.artint.2017.09.001](https://doi.org/10.1016/j.artint.2017.09.001) | partial | CMA-ES with population 150 × 300 generations, on 27–70 parameters per behaviour. Re-opening the "seams" between separately learned behaviours beat sequential learning (supports tuning B and C **jointly in the full game**, not in isolation) |
| Stone 2005 (keepaway) | Stone, Sutton, Kuhlmann, "Reinforcement Learning for RoboCup Soccer Keepaway", *Adaptive Behavior* 13(3), 2005. [PDF](https://www.cs.utexas.edu/~AustinVilla/papers/AB05.pdf) | full (earlier research agent, proposals.md section 6) | SMDP Sarsa(λ) reached 9.6–11.1 s possession after 25 h. The hand-coded policy got 9.6 s when tuned (≈ 30 combinations of 2 parameters) vs 8.2 s untuned → **tune before learning** |
| Coulom 2011 (CLOP) | Coulom, "CLOP: Confident Local Optimization for Noisy Black-Box Parameter Tuning", ACG 13, 2011. [PDF](https://www.remi-coulom.fr/CLOP/CLOP.pdf) | partial | Models win probability per game with local quadratic logistic regression. Beat SPSA, cross-entropy and UCT on artificial problems from 10 to 10⁷ games. An alternative tuner for ≤ ~5 parameters |
| Stockfish SPSA | chessprogramming.org, [Stockfish's Tuning Method](https://chessprogramming.org/Stockfish's_Tuning_Method); [fishtest wiki](https://github.com/official-stockfish/fishtest/wiki/Creating-my-first-test) | web pages | [reported] 7–35 variables tuned at once with "30000–100000 super-fast games"; one SPSA iteration = 2 games (a ± pair) |
| Ha & Schmidhuber 2018 | Ha, Schmidhuber, "World Models", [arXiv 1803.10122](https://arxiv.org/abs/1803.10122), [article](https://worldmodels.github.io/) | appendix | CMA-ES, population 64, **16 rollouts per agent**, 867 parameters, 1,800 generations. The best agent was re-checked on 1,024 rollouts every 25 generations |
| Oquab (CEC?) | Oquab, Rapin, Teytaud, Cazenave, "Parallel Noisy Optimization in Front of Simulators", [PDF](https://www.lamsade.dauphine.fr/~cazenave/papers/games_cec.pdf) (venue unverified) | partial | Population-control methods work well for continuous game parameters (dimensions 12 and 21), but "deceptive noise models exist" |

### 2.3 Learning in the Berkeley Pacman CTF contest (student reports; all [reported])

| key | source | technique and training | what they reported | verdict |
|---|---|---|---|---|
| Pacamon 2020 | Team Pacamon, Melbourne COMP90054 2020, [write-up](https://abhinavcreed13.github.io/projects/ai-team-pacamon/), [repo](https://github.com/abhinavcreed13/ai-capture-the-flag-pacman-contest) | PDDL + MCTS + approximate Q-learning (4 features, shaped rewards), trained 50–100 games vs baseline and their own PDDL agent | Q-learning alone 1W/8T/1L vs baseline. **Q-learning as a fallback** inside the PDDL agent: rank 8 → 5, 73.4% win rate (final hybrid 68.5% over 7,012 games) | learned module helped **only as a fallback inside rules** |
| LuChenyang 2019 | Melbourne 2019, [repo](https://github.com/LuChenyang3842/pacman-contest) | A* on hand-coded goals; a separate approximate-Q defender | "Ranked 3/152" (repo description). The Q defender was not used: "very limited due to the difficulty of defining rewards". Deep Q-learning judged to need "months" | heuristics won |
| Liu & Lago (KTH) | KTH DD2438, [repo + report](https://github.com/xc-liu/pacman-rl-agent) | PPO controlling both agents. Shaped rewards; mixed opponents + self-play + curriculum maps | Shaped: walked into walls, oscillated, "failed to beat random agents". **Terminal-score-only reward**: over 35,000 games, win rate vs random 18% → 70%, but its loss rate vs baseline only fell 85% → 75% | deep RL failed within a course budget |
| Hammarstedt (KTH) | KTH DD2438 2021, [repo](https://github.com/jhammarstedt/PacmanAI) | DQN (CNN), 5,000 episodes vs baseline | "very little learning was done". Their backup heuristic team won the class tournament | heuristics won |
| Li & Chen (Fudan) | Fudan 2017, [report repo](https://github.com/BrightFeather/DQN-for-Pacman-contest) | DQN on 0/1 grid stacks, offence and defence trained 1v1 vs baseline; also imitation of the baseline for defence | Offence "just slightly better than baseline" and **never learned to return food**. Defence "failed to learn" (encounters too rare), even after supervised imitation. Their Q-weight learner "has not yielded results" | combine learning with search, not pure RL |
| Jensen & Gradwohl (UCSC) | UCSC CMPS 140 2017, [repo](https://github.com/jaredjxyz/Pacman-Tournament-Agent) | Linear approximate Q on features, **10 training games**, weights copied by hand; max-flow bottleneck defender; manual overrides | Trained on one map, it "failed miserably" on random seeds until an A* distance feature was added. "Highest win/lose ratio in the class" | small learned part + rules |
| loosh (LMU) | LMU CMSI 4320 2024, [repo](https://github.com/loosh/pacman-ctf-agents) | approximate Q (RL mandated), binary features incl. per-pellet safe/risky; particle filter | won the class tournament (budget not reported) | learning worked where it was mandated and the features carried the logic |
| Oh 2026 (KAIST) | KAIST CS470 2026, [PDF](https://ohdoyoel.github.io/papers/pacman3.pdf) (report says it was written with AI-tool assistance) | 42-weight linear evaluation tuned by **population-based self-play** (pop 12, 20% elite, Gaussian mutation), 3/1/0 fitness vs siblings + **5 fixed "zoo" anchors** against collapse | Retuning on all 13 zoo opponents raised fitness 3.64 → 5.56 but gave **no gain on unseen opponents** (76.5% both) and −10…−13 pp on two known ones. 77.1% wins over 792 games vs 36 external agents | **self-play tuning of a heuristic beats deep RL/MCTS here; pool overfitting is real** |
| infinityglow 2020 | Melbourne 2020 S2, [repo + wiki](https://github.com/infinityglow/COMP90054-Pacman-Contest-Project) | MCTS attacker (depth 5, 20-step rollouts) → rule-based decision tree | MCTS version ranked 15/37 (below staff_top); the rule version 13/76 (above staff_top), best rank 8/88. "using only these techniques is not enough… strategies are needed" | rules won |
| Pac-Champs 2019 | Melbourne 2019, [wiki](https://github.com/kkkkkaran/Berkeley-PacmanCTF/wiki) | Q-learning defender | 30–40% wins vs baseline and > 1 s per move on some layouts ("ineligible"); MC + heuristics won 95–100% vs baseline | rules won |
| Bachfischer 2020 | Melbourne 2020, [blog](https://bachfischer.me/posts/2021/02/reflections_on_pacman_ai_competition/) | approximate Q + hand-written behaviour protocols | top 10%. Feature-function search "eventually abandoned" | hybrid |
| pacAI (UCSC) | UCSC CSE-140, [repo](https://github.com/oasysokubo/pacAI) | alpha-beta and approximate Q abandoned as "too computationally expensive" | choke-point / dead-end features + a midline defender: 55% → ~90% vs baseline | "simplest approaches… often the best" |
| uripont (UPF 2025) | UPF 2025, [repo](https://github.com/uripont/pacman-agent) | heuristic team; parameters tuned with thousands of internal games | RL "out of scope" | — |
| Liu & Stock (UW) | UW CSE 573 2017, [report](https://jadenstock.wordpress.com/wp-content/uploads/2017/03/573_ai_final_report.pdf) | UCT + shared particle filters, 7-step rollouts + heuristic | depth 7 / ~100 nodes at 0.2 s; "consistently win" on the default map (opponent not stated) | — |
| DeNero & Klein 2010 | "Teaching Introductory AI with Pac-Man", EAAI 2010, [PDF](https://cdn.aaai.org/ojs/18829/18829-13-22566-1-10-20210930.pdf) | organisers' view | "Effective entries… combine search, adversarial search, and probabilistic tracking" | [source] |

Pattern [reported, synthesis]:
- **Learning as the main policy failed or was shelved in every report found.** The causes:
  - sparse reward (agents learned to eat but not to bank);
  - shaping traps (oscillation);
  - rare defensive events;
  - single-map overfitting;
  - timeouts.
- **Learning that helped** was small and sat inside rules or search:
  - linear Q weights from 10–100 games as a fallback;
  - self-play or GA tuning of a linear evaluation, safe only with held-out checks.
- **No peer-reviewed RL paper on this exact environment was found.** Jaderberg 2019's Capture the Flag is Quake III, not Pacman.

### 2.4 Learned evaluators, distillation, imitation and hybrids

| key | reference | read | claims relevant to us |
|---|---|---|---|
| Nasu 2018 (NNUE) | Nasu, "Efficiently Updatable Neural-Network-based Evaluation Functions for Computer Shogi", 2018; summary at [chessprogramming.org/NNUE](https://www.chessprogramming.org/NNUE) | secondary | A shallow net whose first-layer accumulator is updated incrementally (2–4 changed inputs per move), with quantised weights and SIMD. Stockfish adopted it in 2020 and became stronger although its search speed roughly halved. The incremental idea carries to pure Python; the SIMD speed does not |
| Rusu 2016 | Rusu et al., "Policy Distillation", ICLR 2016, [arXiv 1511.06295](https://arxiv.org/abs/1511.06295) | abstract | DQN policies distilled by a supervised KL loss "can be compressed by up to 15 times without degradation"; the 62k-parameter student reached 84% of the teacher's score |
| Silver 2018 (residual) | Silver, Allen, Tenenbaum, Kaelbling, "Residual Policy Learning", [arXiv 1812.06298](https://arxiv.org/abs/1812.06298) | abstract | Learn a correction added to a fixed (non-differentiable) controller. Gradient flows only through the residual. Consistent gains over the initial controllers on 6 MuJoCo tasks |
| Ross 2011 (DAgger) | Ross, Gordon, Bagnell, "A Reduction of Imitation Learning and Structured Prediction to No-Regret Online Learning", AISTATS 2011, [PMLR](https://proceedings.mlr.press/v15/ross11a.html) | abstract | Plain behaviour cloning suffers compounding errors, because the learner's own actions shift the state distribution. Querying the expert on the learner's states fixes this |
| Schmitt 2018 (kickstarting) | Schmitt et al., "Kickstarting Deep Reinforcement Learning", [arXiv 1803.03835](https://arxiv.org/abs/1803.03835) | abstract | A teacher-distillation loss during RL: the student matched from-scratch performance in ≈ 10× fewer steps and finished 42% higher (DMLab-30) |
| Lagoudakis & Parr 2003 (RCPI) | Lagoudakis, Parr, "Reinforcement Learning as Classification: Leveraging Modern Classifiers", ICML 2003, pp. 424–431, [mlanthology](https://mlanthology.org/icml/2003/lagoudakis2003icml-reinforcement) | abstract | Approximate policy iteration in which rollouts label the best action per state and a classifier learns the policy; no value-function approximation needed |
| Tesauro & Galperin 1996 | Tesauro, Galperin, "On-line Policy Improvement using Monte-Carlo Search", NIPS 9, 1996, [proceedings](https://proceedings.neurips.cc/paper/1996/hash/996009f2374006606f4c0b0fda878af1-Abstract.html) | abstract | Rollouts of the base policy pick the best move; this cut the base players' error rate by up to 5× or more, from random play to TD-Gammon |
| Tesauro 1995 | Tesauro, "Temporal Difference Learning and TD-Gammon", *CACM* 38(3):58–68, 1995, [doi:10.1145/203330.203343](https://doi.org/10.1145/203330.203343) | abstract | A neural evaluation function learned from self-play outcomes by TD(λ): the classic precedent for design F |

### 2.5 Population / league training and coevolution

| key | reference | read | anti-overfitting mechanism |
|---|---|---|---|
| Jaderberg 2017 (PBT) | Jaderberg et al., "Population Based Training of Neural Networks", [arXiv 1711.09846](https://arxiv.org/abs/1711.09846) | abstract | Weak members of the population are replaced by mutated copies of strong ones |
| Jaderberg 2019 (Quake III CTF) | Jaderberg et al., "Human-level performance in 3D multiplayer games with population-based reinforcement learning", *Science* 364, 2019; [arXiv 1807.01281](https://arxiv.org/abs/1807.01281) | partial | A population of 30. Matchmaking by online Elo keeps opponents of similar skill. **Every game on a new procedurally generated map**: zero-shot generalisation to unseen maps |
| Vinyals 2019 (AlphaStar) | Vinyals et al., *Nature* 575:350–354, 2019, [doi:10.1038/s41586-019-1724-z](https://doi.org/10.1038/s41586-019-1724-z); [DeepMind blog](https://deepmind.google/en/blog/alphastar-grandmaster-level-in-starcraft-ii-using-multi-agent-reinforcement-learning/) | blog + survey (Nature behind login) | Plain self-play forgets and "chases its tail". The league has three roles: main agents use prioritised fictitious self-play (PFSP) and are never reset; main exploiters train against the main agents only; league exploiters train against the whole league. PFSP weights (1 − x)^p focus on hard opponents. Exact ratios unverified |
| Lanctot 2017 (PSRO) | Lanctot et al., "A Unified Game-Theoretic Approach to Multiagent Reinforcement Learning", NeurIPS 2017, [arXiv 1711.00832](https://arxiv.org/abs/1711.00832) | abstract | Independent RL "overfits to other agents' policies". The joint-policy-correlation metric measures this. Best responses are trained to meta-strategy *mixtures* |
| Balduzzi 2019 | Balduzzi et al., "Open-ended Learning in Symmetric Zero-sum Games", ICML 2019, [arXiv 1901.08106](https://arxiv.org/abs/1901.08106) | abstract | Non-transitive games have strategic cycles and "no longer a clear objective". Niching builds diverse populations |
| Balduzzi 2018 | Balduzzi, Tuyls, Pérolat, Graepel, "Re-evaluating Evaluation", NeurIPS 2018, [arXiv 1806.02643](https://arxiv.org/abs/1806.02643) | partial | Elo is "meaningless" in cyclic games, and adding copies of a beaten agent inflates a rating. **Nash averaging** is invariant to redundant opponents. Our evaluation.md already reports an approximation of it |
| Rosin & Belew 1997 | Rosin, Belew, "New Methods for Competitive Coevolution", *Evolutionary Computation* 5(1), 1997, [doi:10.1162/evco.1997.5.1.1](https://doi.org/10.1162/evco.1997.5.1.1) | abstract | Competitive fitness sharing, shared sampling of a strong and diverse opponent set, and a **Hall of Fame** of earlier good individuals as test opponents |
| Miconi 2009 | Miconi, "Why Coevolution Doesn't 'Work'", EuroGP 2009, LNCS 5481:49–60 | abstract | Treating **training opponents as a test set** is a common error |
| Watson & Pollack 2001; Ficici & Pollack 2003 | GECCO 2001 pp. 702–709; GECCO 2003 pp. 286–297 (Nash memory) | citation / abstract | Intransitivity causes cycling and disengagement. A Nash-memory archive acts as a ratchet |

**What this implies for us** [untested synthesis]:
- (1) Every learned or tuned part trains against a *fixed* pool plus past bests (Hall of Fame: greedy_v2, greedy_v3, lab5_smart) and at least one exploiter of the candidate.
  - Our `exploit_v2` was written that way (E-015). An exploiter of the tuned agent could be built the same way.
- (2) Report the per-opponent matrix and the Nash average, not only the mean.
- (3) Never report a result against the opponents it was tuned on as generalisation (Miconi 2009). The held-out teams exist for this.
- (4) A full league is overkill for ≤ 20 parameters. Fixed pool + Hall of Fame + held-out check is the proportionate version.

---

## 3. Designs for our setting, ranked by expected gain per hour of work

**Common ground for every design**:
- **Base agent**: `lab5_smart` (passes the accept rule, E-025; not promoted yet).
- **Compute**: ≈ 9,000 games/hour on 8 workers (≈ 1.3–2 s per game with `--delay-step 0`) [reported by the user; E-009 measured 1.3 s/game/core]. One night of ≈ 8 h is ≈ 70,000 games.
- **Seeds**: tuning seeds only for anything learned or screened. Validation seeds only for the final accept decision. Test and held-out opponents only at the release gate (T-50, T-53).
- **CRN** (common random numbers): every configuration being compared plays the *same* (seed, opponent, colour) games. Our agents are deterministic with private RNGs, and `RANDOM<seed>` fixes the map and the engine's RNG, so these comparisons are paired [verified E-000, evaluation.md section 2].
- **New files only**: a tuned or learned agent goes into a new lab file with the learned numbers as constants. Benchmarked files are never edited (T-48).
  - While this report was being written, a parallel session created `teams/greedy_lab_v6.py` (lab5_smart defaults, identity 18/18 per `HANDOFF.md`, with `plan` and `focus` switches) and `eval/rl/` tools (`cmaes_tune.py`, `mode_table.py`, `map_features.py`, …).
  - This report did not review that code. Its designs apply to that file. Once v6 is benchmarked, the next version is `greedy_lab_v7.py`.
- **Identity check first**: the new file with its learned parts at their initial values must play 18/18 games identically to `lab5_smart` (the identity test used for every lab file).

| rank | design | what is learned | work (h) | compute | expected gain [untested] | confidence |
|---|---|---|---|---|---|---|
| 1 | **B. CMA-ES on lab5_smart's constants** | ~10 numbers | 3–4 | 5–6 h | +0.05 … +0.15 PPG | medium |
| 2 | **C. Residual learned modules** (target-food scorer + bank-threshold correction), trained by the same CMA-ES | 15–20 weights | 6–8 | 5–6 h (another night) | +0.00 … +0.15 | low–medium |
| 3 | **E1. Opponent-type detection → best-response formation** (in-game) | a small type × mode table | 6–10 | 1–2 h | 0 vs our pool; maybe +0.1 vs a mixed field | low (the pool lacks the types) |
| 4 | **A. Map-mode selector** (portfolio + feature-based selector) | K modes + per-mode ridge models | 5–8 | 1–1.5 h for the go/no-go table | +0.00 … +0.05 | medium that it is small (pilot, section 1.2) |
| 5 | F. Learned value function for short lookahead | MLP 30-32-1 | 15–25 | 2–4 h data + training | unknown | low |
| 6 | D. Deep RL (DQN/PPO, or BC + RL) | a whole policy | 40+ | days | negative before it is positive | very low tonight |

Why this order:
- **B first.** It is the cheapest and reuses all our tooling. The literature on tuning hand-built controllers is the most consistent (keepaway, RoboCup, chess SPSA; section 2.2). It also gives C and A their tuned base.
- **C is B with a richer parameterisation.** It gets its own night.
- **A is ranked low on our own evidence.** Per-map labels are noise (section 1.2), and none of 11 cheap features carried the per-map effect (section 1.3). Its go/no-go table is cheap, though, and doubles as a discrete-mode screen, so it is worth one hour of compute.

---

### 3.B CMA-ES tuning of the rule agent's numeric parameters (rank 1)

**What is learned**: θ, about 10 constants of `teams/greedy_lab_v5.py` with the `lab5_smart` switches on. Expose them as `create_team` kwargs in a new lab file; T-47: no `,` or `=` inside values.

| parameter (module constant) | default | search range | type |
|---|---|---|---|
| `return_at` | 8 | 3 – 20 | int |
| `THREAT_DIST` (carrier goes home when a ghost is this close) | 4 | 2 – 8 | int |
| `SCARED_MARGIN` | 3 | 0 – 8 | int |
| `TIME_MARGIN` | 3 | 0 – 10 | int |
| `STANDOFF_MOVES` (blocked moves before switching entry / capsule) | 3 | 1 – 8 | int |
| `STANDOFF_WINDOW` | 12 | 4 – 30 | int |
| `OPEN_MARGIN` (open_goal spare moves) | 4 | 0 – 10 | int |
| `OPEN_QUANTILE` (pessimism of the belief distance) | 0.1 | 0.0 – 0.5 | float |
| `DIRECT_BONUS` (directed belief motion) | 2.0 | 0 – 6 | float |
| `ENEMY_RETURN_DEFAULT` | 5 | 2 – 12 | int |
| `ENDGAME_MOVES` | 40 | 0 – 100 | int |
| (optional) `STAY_WEIGHT`, `EVIDENCE_PLIES` | 0.2, 40 | 0.05–1, 10–100 | float, int |

- **Encoding**: map every parameter linearly to [0, 10], so that one σ is equally meaningful in every coordinate.
  - The tutorial says ranges should not differ by orders of magnitude between variables. For a random start in [a, b] it uses σ₀ = 0.3 (b − a), so that the optimum lies within m ± 3σ [source: Hansen 2016].
  - We start at the hand-tuned defaults, so σ₀ ≈ 2 (0.2 × range) is enough [untested].
- **Integers**: round inside the fitness function, and keep their σ from collapsing [verified: local pycma 3.3.0 source in `venv_rl`].
  - The `integer_variables` option does basic integer handling: it stops the std of those coordinates from getting too small.
  - `cma.fitness_transformations.IntegerMixedFunction` is also available.
  - The `cma.integer` module that pycma's deprecation message points to is not in this version.
  - Default popsize is `4 + 3·ln(N)` and the default μ is `popsize // 2`.
- **Inputs at runtime**: none. The output is a set of constants.
- **Training signal**: **true game points (3/1/0)**, averaged over the candidate's games.
  - CMA-ES uses only the *ranking* of the population [source: Hansen 2016], so the scale does not matter.
  - Do **not** add score margin to the fitness in the first run. It lowers the noise but rewards big wins against weak pool members (reward hacking, section 5). Try it only if the points-only run stalls, and judge the result on points.
- **Opponents per candidate**: the 8-member reference pool, plus `lab5_smart` itself as a 9th. That adds a head-to-head and forgetting guard, like AlphaStar's "minimum win rate against past versions" [source: Vinyals 2019].
- **CRN**: every generation draws **2 new tuning seeds**. All λ candidates of that generation play the same 2 seeds × 9 opponents × 2 colours = **36 games**.
  - Ranks within a generation are then paired (blocked) comparisons, as in SMAC's intensification and the "partial CRN" of game-parameter SPSA [source: Hutter 2011; Kocsis & Szepesvári 2006].
  - New seeds each generation stop the optimiser from fitting particular maps [untested; section 1.2 shows per-map effects of ≈ 0.3 PPG, so one map per generation would be too small a minibatch].
- **Population**: the default is λ = 4 + ⌊3 ln n⌋ = 11 for n = 12, with μ = ⌊λ/2⌋ [source: Hansen 2016; verified in local pycma].
  - Under noise, "increasing μ and λ is preferable to resampling" [source: Hansen et al. 2009, citing Arnold; Hellwig & Beyer 2020].
  - For a fixed budget, one evaluation per perturbation and more perturbations gave the lowest error in game-parameter SPSA [source: Kocsis & Szepesvári 2006].
  - **Use λ = 24, μ = 12** (≈ 2 × default), with **36 games** per candidate rather than many more.
  - The reported sweet spots were moderate averaging with large populations: CMA-ES did best at 50 generations × population 30 × 10 averaged runs on RoboCup skills [source: Urieli 2011]; World Models used population 64 × 16 rollouts [source: Ha & Schmidhuber 2018].
- **Noise per candidate** [verified arithmetic, section 1.1]:
  - SE of a candidate's mean is ≈ 1.24/√36 ≈ 0.21 PPG.
  - SE of the difference between two candidates of one generation is ≈ 1.2/√36 ≈ 0.20 (CRN pairing).
  - Two candidates 0.15 PPG apart are ranked correctly ≈ 77% of the time; at 0.05 apart, ≈ 60%.
  - Weighted recombination over μ = 12 parents averages this ("genetic repair") [source: Hellwig & Beyer 2020]; untested for our game.
- **Optional variance reduction**: mirrored (antithetic) sampling, pycma option `CMA_mirrors`, which exists in the local version [verified]. Combined with CRN, ±ε pairs are then compared on identical games. Salimans 2017 used antithetic pairs with rank-based fitness shaping [source].
- **Uncertainty handling**: optionally pycma's `NoiseHandler`, which implements UH-CMA-ES's rank-change measurement and raises σ or the evaluation count when the ranking is mostly noise [source: Hansen et al. 2009; verified in the local pycma docstring].
  - **Caveat for our deterministic games**: a re-evaluation on the same seeds gives the identical result (T-36). The fitness function must draw *new* seeds for re-evaluations. Hansen 2009 handles such "frozen" noise with a small perturbation; ours needs fresh games.
  - Start without it. Turn it on if σ collapses in the first 10 generations.
- **Budget**:
  - One generation = 24 × 36 = 864 games ≈ 5.8 min at 9,000 games/hour.
  - 5.5 h ≈ **57 generations ≈ 49,000 games**.
  - For scale, chess engines tune 7–35 parameters at once with 30,000–100,000 very fast games per SPSA session [reported: chessprogramming.org, Stockfish's tuning method]. Our budget is in that range.
  - A 12-dim CMA-ES adapts its covariance over a few dozen generations, so expect real movement of the mean, not convergence [untested].
- **Conservative variant**: λ = 16 with 72 games per candidate (4 seeds), 1,152 games per generation, ≈ 44 generations. Choose this if the first 10 generations of the main setting show σ collapsing or the mean jumping around.
- **What to report**: the **distribution mean m**, not the best-sampled candidate. The best sample of a noisy generation is the winner's curse in its purest form [source: Smith & Winkler 2006; section 1.2 shows it on our data].
  - In RoboCup skill tuning, a final re-evaluation was "necessary because of the noise" [source: Urieli 2011].
  - World Models re-checked its best agent every 25 generations on 1,024 rollouts [source: Ha & Schmidhuber 2018].
  - Every 8 generations, play m against `lab5_smart` on a fixed *monitor* set: 20 tuning seeds × 8 pool opponents × 2 colours = 320 paired games, ≈ 2 min.
  - The monitor seeds never enter the CMA fitness.
- **Shipping**: m rounded to legal values becomes the constants of a new lab file (stdlib, no data file needed).
- **Overfitting guards**:
  - (1) Tuning seeds only, fresh ones each generation.
  - (2) Pool uniform over opponent types, as `PPG_P`.
  - (3) Accept-rule clause 3: no per-opponent regression beyond 0.5. Also report the Nash-averaged payoff (evaluation.md section 2), which exposes a θ that exploits one pool member [source: Balduzzi 2018].
  - (4) Held-out teams only at the release gate. Friend teams diagnostics only (user rule).
  - (5) Box constraints within ranges that make tactical sense.
- **Test**:
  - Screen: m vs `lab5_smart` on 40 *fresh tuning* seeds against the pool. Continue only if Δ > 0.
  - Accept: the standard accept rule on ≥ 80 validation seeds. This consumes most of the 120 left, so ask for a fresh validation list first (section 1.1).
- **Expected gain, honestly**:
  - Our own history says the landscape near the hand-set point is flat for single parameters: return thresholds 3 / 12 and adaptive returns were within noise (E-007, E-010, E-011).
  - The gains came from new behaviours (breaker +0.26, shadow +0.16, open_goal +0.17).
  - Joint tuning can find interactions that one-at-a-time tests miss: return-at-8 only helped together with the breaker, E-010. Keepaway's tuned hand policy matched 25 hours of RL [source: Stone, Sutton & Kuhlmann 2005].
  - Estimate: **+0.05 … +0.15 PPG** [untested].

**A cheaper fallback** if CMA-ES infrastructure is too much tonight: a racing screen [source: Birattari 2002 F-Race; López-Ibáñez 2016 irace].
- Try 2 alternative levels per parameter (24 configurations) on CRN seeds, and drop configurations that a paired test shows are worse after every 4 seeds.
- This is ≈ 24 × 72 = 1,700 games per round. Good for finding which 3–4 parameters matter before running CMA-ES on them alone.

---

### 3.C Greedy + learned residual modules (rank 2)

**Idea**: keep every hard safety rule of the greedy agent (race-safety, threat retreat, time margin). Learn only *preferences among safe options*, as an additive residual on the existing rule, initialised so that the agent starts exactly as `lab5_smart`.
- Residual policy learning learns a correction on top of a fixed controller and starts from that controller's performance [source: Silver et al. 2018, [arXiv 1812.06298](https://arxiv.org/abs/1812.06298)].
- In our setting the "residual" is a linear score added to a rule's choice [untested].

**C1. Target-food scorer.** Among the race-safe food candidates (already computed), choose argmax of s(f) = −d(me, f) + Σᵢ wᵢ φᵢ(f), with **w = 0 initially**, which is exactly nearest-food (identity check).

| φᵢ(f) (all from our observation and team belief) | why it might matter |
|---|---|
| d(f, home border) / 10 | the cost of banking after eating f |
| race margin: min over visible ghosts of d(g, f) − d(me, f), capped at 10 | how safe f really is |
| dead-end depth of f (leaf pruning, precomputed per map) | trap risk (E-014: most deaths in dead ends) |
| food within maze distance 3 of f | clusters: more food per trip |
| d(f, nearest enemy capsule) / 10 | an escape option |
| expected distance of the enemy defender to f under the belief (p10 quantile) | hidden danger, using `shared` / `flags` |
| carrying × d(f, home) / 100 | do not wander off when loaded |
| (moves left < 100) × d(f, home) / 10 | late-game caution |
| top-half / bottom-half indicator × our teammate's half | split targets (SM-10) |
| f lies in the region the enemy defender came from | avoid the guard's beat |

**C2. Bank-threshold correction.** return_at(s) = clip(round(R + v·ψ(s)), 1, 30), where R is the (B-tuned) constant and **v = 0 initially**.
- ψ: distance home / 10, nearest visible ghost distance (10 if none), p10 belief distance of the nearest enemy ghost, our moves left / 300, score / 10, food still needed to win / 28, enemy ghosts' scared timer / 40, teammate is a Pacman.
- It generalises the rejected `adaptive` switch (E-011) and the adopted `open_goal` rule into a learned form.

**C3 (only after C1/C2, and with care). Formation gate.** The defender joins the attack when u·χ(s) > 0, with χ = (score, moves left, number of enemy Pacmen [exact via flags], enemy carried food, our carried food, enemy respawn window).
- The bias is initialised so it never fires.
- E-018 / E-020 / E-025 show that formation switches gain against one opponent type and lose against another. Train it only with a pool that contains double attackers (section 5).

- **Optimiser**: the same CMA-ES pipeline as B, on C1 + C2 (≈ 18 weights).
  - Default λ = 4 + ⌊3 ln 18⌋ = 12. **Use λ = 24, μ = 12.**
  - σ₀ chosen so that one σ changes a weight by about the scale of the distance term (≈ 0.3 after feature scaling).
  - Same 36 games per candidate: 864 games per generation ≈ 6 min, ≈ 55 generations per 5.5 h night.
- **Precedent**: a KAIST CS470 report (2026) tuned a 42-weight linear evaluation for this very contest by population-based self-play (population 12, 20% elite, Gaussian mutation, 3/1/0 fitness against siblings + 5 fixed "zoo" anchors). It preferred that over deep RL or MCTS [reported: Oh 2026].
- **Why not policy gradient**:
  - REINFORCE on a softmax over targets would need a stochastic policy and per-decision credit from a game outcome that ~100 target decisions share.
  - ES perturbs parameters rather than actions, so its noise does not grow with the episode length [source: Salimans 2017].
  - For ≤ 50 parameters, ES is the simpler and usually adequate tool [untested here].
- **Why not supervised regression on logs (yet)**:
  - A label such as "points of the game in which this target was chosen" is dominated by everything else in the game.
  - Rollout-based labels (branch the game at a decision, try each option, compare outcomes: RCPI [source: Lagoudakis & Parr 2003]; Monte-Carlo policy improvement [source: Tesauro & Galperin 1996]) are possible offline, because our games are deterministic given the seed. But one decision's effect on the final points is far below the per-game noise (SD 1.2). Rollouts would need short-horizon, shaped labels (food banked minus food lost in the next 40 moves), which brings reward-hacking risk. Keep this as an option for C2 only.
- **Inference cost**: ≤ 30 candidates × ~12 features as a linear score ≈ 0.13 ms plus table lookups [verified, section 1.4].
- **Shipping**: the weights as module constants (or a read-only JSON next to the agent, allowed by Q6).
- **Guards**: as in B. Plus the identity check with w = v = 0. Plus a **trace profile** (`eval/trace_game.py profile`, E-022) to confirm that the module actually changes decisions and where (T-57).
- **Expected gain**:
  - C1 changes the core forager decision. Its upside is larger than B's, but so is its risk of drifting into a timid or greedy local optimum: `lab_tracker`'s timid attacker lost 0.11 (E-007).
  - Estimate +0.00 … +0.15 PPG [untested].

---

### 3.E1 Opponent-type detection → best-response formation (rank 3; "weird but plausible")

**Our own evidence of large mode × opponent interactions** [verified]:
- The defender raid: more points against guards, more conceded against attackers; net −0.07 (E-018).
- `recall`: −0.58 against `double_attack`, never fires against the pool (E-025).

The per-opponent pilot of section 1.2 found no gain only because the `lab5_*` switches barely interact with opponent type. Formation-level modes do.

- **Detection** (first ~60 own moves, then keep updating with hysteresis):
  - share of time each enemy is a Pacman (exact `is_pacman` behind `USE_HIDDEN_OPPONENT_FLAGS`, allowed and recommended, Q3);
  - whether one enemy ghost stays within 3 of the border (guard);
  - whether both enemies invade at once (double attack);
  - whether nobody invades (turtle).
- **Response table**: type → mode, e.g. guard + raider → standard or the decoy/spotter tactics (SM-4/5). Double attack → race: both attack once our lead is safe, never recall (E-025). Turtle / double guard → raid-when-quiet (E-018's raid paid against guards).
- **What is learned**: the type × mode payoff table, offline, with CRN.
  - Each mode plays each opponent of a type on the same seeds.
  - It needs league members of every type: `double_attack`, `turtle`, `camper2`, `rusher` (tuning-pool members, allowed), never the held-out teams.
  - Table cost: 4 modes × 6 opponents × 30 seeds × 2 colours = 1,440 games ≈ 10 min.
- **Literature**:
  - Playbook selection with per-play weights adapted during a game [source: Bowling, Browning & Veloso 2004, already in proposals.md SM-13].
  - Strategy selection as a game between strategies, with opponent-dependent best responses [source: Tavares et al. 2016].
  - Per-opponent strategy learning in the StarCraft AI competitions (section 2.1).
- **Expected gain**:
  - ≈ 0 against our current pool, because every pool member is an attacker-plus-defender type (E-014, E-025).
  - Unknown against the real field. Friend team `friend_aljaz_1` (a heavy attacker, 0.64–0.88 PPG for us) suggests attack-heavy teams exist [verified E-026, diagnostic only].
- **Main risk**: designing for opponent types that we invented. Validate against the held-out teams at the release gate, whose styles are a guard-first team and an aggressive double attack (league.json labels).

---

### 3.A Map-mode selector: portfolio + per-instance selection (rank 4)

This is the algorithm-selection problem [source: Rice 1976]: instance = the map; features = map statistics computed in `register_initial_state`; algorithms = K configurations ("modes") of our agent; performance = points per game.

**Portfolio (K = 4–6)**. Modes must differ in ways that plausibly interact with map structure, and each must be a sensible agent on its own:

| mode | change from M0 | map feature it should interact with [untested] |
|---|---|---|
| M0 | `lab5_smart` (or B's tuned agent) | — |
| M1 bank-early | return_at 5, open_goal margin +2 | long border→food distances, deep pockets |
| M2 bank-late | return_at 12 | short distances, many crossings |
| M3 exit-cautious | `exit_race` (E-018's `lab2_exit`, deaths halved, points flat on average) | high share of food in deep dead ends |
| M4 double-start | both attack until the first enemy Pacman is seen, then the usual roles | few crossings for them (easy to defend late), food near the border |
| M5 capsule-first | take the enemy capsule first when it is near the border (rusher-like) | capsule-to-border distance |

A "region priority" mode (greedy_top_left) is **not** recommended as a discrete mode. Food concentration by region is weak on these maps (section 1.3). A region preference is better expressed as a continuous feature in C1.

`greedy_lab_v6.py`'s `focus` modes are exactly such region modes (`top` / `bottom` / `majority` / `deep` / `shallow` / `cluster` / `far` / `auto`). Section 1.3 predicts for them [untested]:
- `top` / `bottom` / `majority` have little to work with. The larger (top or bottom) half holds a median 57% of the enemy food, ≥ 60% on 36% of maps and ≥ 2/3 on only 9% (300 tuning maps, max 77%) [verified].
- `deep` / `shallow` / `cluster` / `far` act on features that vary much more between maps, so they are the better bets.
- Screen them with the same paired, many-maps design, and judge `auto` only by cross-validation over maps.

**Features** (all computable at startup from walls, food and capsules; colour-invariant because the maps are point-symmetric, 300/300 [verified]):
- crossings;
- share of food in tree-like dead-end parts, and its mean depth;
- mean and max border→food distance;
- capsule→border distance;
- loops per cell;
- number of cut cells on each side, and food behind the largest cut cell (H-M03);
- spawn→border distance (prison length, H-M08).

Our side's geometry equals their side's by symmetry, so the same features describe our defence.

**Building the training table efficiently**:
- **Many maps, few games per map.** The model is a low-capacity regression across maps, and noise averages out over maps. Per-map replication only buys a better (but still unreliable) per-map label.
  - **400 tuning maps × 4 modes × 2 opponents per map** (rotating through the 8 pool members, balanced) **× 2 colours = 6,400 games ≈ 45 min**.
  - The per-map paired Δ then has noise SD ≈ 1.2/√4 = 0.6. With τ ≈ 0.3 of true heterogeneity, a feature explaining 20% of τ² has a standardized slope ≈ 0.13 and SE ≈ 0.6/√400 = 0.03, so it is detectable (t ≈ 4) [untested arithmetic].
- **CRN**: all K modes play the identical (seed, opponent, colour) cells, so Δ_k(map) is paired.
- **Labels**: the *paired difference to M0*, never "the best mode on this map".

**Model**:
- **Per-mode ridge regression** of Δ_k(map) on ≤ 8 standardized features, with the ridge penalty chosen by leave-maps-out cross-validation.
- Select k* = argmax_k Δ̂_k(x). Switch away from M0 only if Δ̂_k*(x) > c, where c (≈ one prediction SE) is also set by cross-validation.
- This is the cost-sensitive, pairwise formulation that SATzilla 2012 moved to, instead of classifying the argmax label [source: Xu et al. 2012; see section 2.1]. Ridge shrinkage is the guard against the noisy labels (empirical-Bayes view) [untested].
- **No bandit needed offline.** We can afford full information: every mode on every map. A contextual bandit (LinUCB / Thompson) [source: Li et al. 2010; Agrawal & Goyal 2013] is for learning online with feedback for the chosen arm only. That would mean learning across tournament games, which is Q11, unanswered and not allowed until it is.

**Winner's-curse guards**:
- (1) Regress differences, never argmax labels (section 1.2: the in-sample per-map oracle shows +0.20 but is −0.03 cross-validated).
- (2) Evaluate the selector with leave-maps-out CV, then as **one frozen agent** on fresh tuning seeds, then validation.
- (3) If several portfolios or selectors are tried, the best one's CV score is biased upward. Confirm on maps not used to choose [source: Cawley & Talbot 2010, cited in evaluation.md section 2, clause 5].

**Go / no-go, pre-registered**:
- **Go**: build the selector only if its cross-validated gain over the single best mode is ≥ +0.05 PPG with a map-bootstrap CI above 0.
- **No-go**: if not, adopt the single best mode if it beats M0 (that is then just configuration). Stop.
- **Tonight's table answers this in ≈ 45 min.**

- **Shipping**: K mode configs + K × (8 + 1) ridge weights + feature means/SDs as constants. Feature computation ≈ the existing `MapInfo` BFS work (< 0.1 s, E-015's cut-cell BFS took 0.03–0.05 s per map [verified]).
- **ISAC / Hydra variants**:
  - ISAC: cluster maps by features, then tune a configuration per cluster [source: Kadioglu et al. 2010].
  - Hydra: add configurations greedily by their marginal contribution to the portfolio [source: Xu, Hoos & Leyton-Brown 2010].
  - Each multiplies the CMA-ES budget by the number of clusters or modes. Only worth it if the go/no-go passes.
- **Expected gain, honestly**:
  - Pilot: τ ≈ 0.3 PPG of per-map heterogeneity, but no cheap feature carried it on 50 maps (section 1.3).
  - Model calculation [untested]: with a 2-mode choice where Δ ~ N(0.17, 0.3²) (like `lab5_open`), a *perfect* per-map oracle would gain only +0.05 over always taking the better mode. A selector capturing 30% of the heterogeneity would gain ≈ +0.013.
  - In algorithm selection for SAT, the gaps between the single best solver and the virtual best are large because runtimes differ by orders of magnitude between instances (section 2.1). Our per-map effects are fractions of a point.
  - **+0.00 … +0.05 PPG**, mostly below what our seed budget can resolve.

---

### 3.F Learned value function for a short lookahead (rank 5)

- **What**: V(s) ≈ E[final points | s, current policy], a linear model or an MLP 30-32-1 over team-observation features: positions as distances, carried food, belief quantiles, score, time, scared timers.
- **Data**: logged states from offline games via a wrapper team (T-58; logging is fine offline, never in the submission). About 600 of our decisions per game, so ≈ 5M (highly correlated) states per hour of games [untested].
- **Labels**: the Monte-Carlo final outcome (unbiased, noisy) or TD(λ) targets. TD-Gammon-style learning is the classic precedent [source: Tesauro & Galperin 1996 for rollouts; TD-Gammon via the same paper].
- **Use**: only in close quarters (an enemy within 5). A 1–2-ply joint lookahead over our 5 moves × the threatening ghost's 5 moves, with leaves scored by V: ≈ 25 × 0.1 ms = 2.5 ms per decision [verified cost basis, section 1.4].
- **Risk**:
  - V is learned under the current policy. Acting greedily on it is one step of policy iteration and can be wrong off-distribution [untested].
  - Feature code must be identical offline and online.
  - Several days of work.
- Distilling slow search into a fast model (expert iteration, M-13) is the principled version, but it needs a strong slow expert that we do not have.

---

### 3.D Deep RL (rank 6): what it would take

- **Runtime is feasible**: a 30-64-64-5 MLP costs ≈ 0.5–0.7 ms, and a small CNN on an egocentric crop ≈ 4 ms in pure Python [verified / extrapolated, section 1.4].
- **Sample throughput is not absurd** [untested estimate]: ≈ 600 of our decisions per game × ≈ 9,000 games/hour ≈ 5M decisions/hour on 8 workers, if a policy forward pass in the training process adds little.
- **What makes it unrealistic tonight**:
  1. **An actor–learner loop around an engine that owns the control flow**: the engine calls `choose_action`, so trajectories must be written by a wrapper and gathered by a learner, with weights synced to 8 worker processes. That is a day of engineering before the first useful update [untested].
  2. **Sparse, delayed reward**: food scores only when banked, and the game result comes after 300 moves. Shaping is needed, and shaping is the classic reward-hacking surface (section 5).
  3. **Opponents**: plain self-play cycles and forgets. A league with exploiters is needed [source: Vinyals 2019; Lanctot 2017; Balduzzi 2019].
  4. **Random maps**: the policy must generalise across procedurally generated layouts. Separate train and test seed sets are needed to see overfitting [source: Cobbe et al. 2019, cited in evaluation.md].
  5. **No successful deep-RL report for this contest** in our earlier search (M-08) or in the new one (section 2.3).
- **Cheapest promising variant**:
  - **(a) Behaviour cloning** of `lab5_smart`'s moves from egocentric features. Expert labels are free, ≈ 5M per hour. The expert can be queried on the student's own states (DAgger) to avoid compounding errors [source: Ross, Gordon & Bagnell 2011].
  - **(b) RL fine-tuning restricted to a decision subset** (macro-actions: which target, bank now, which entry, take capsule) with a KL or distillation term to the BC policy [source: Schmitt et al. 2018, kickstarting; AlphaStar's supervised-then-RL recipe, Vinyals 2019].
  - (b) is design C with policy gradient instead of ES, and C is the cheaper way to test whether that decision subset has headroom at all.
  - **Verdict**: not tonight. Only if C shows that the macro-decision subset has real headroom.

---

### 3.E2–E4 Other "weird but plausible" ideas

| ID | idea | evidence | verdict [untested] |
|---|---|---|---|
| E2 | **In-game bandit over modes** (proposals.md SM-13 / RL-6): sleeping-experts reweighting of plays within one game | Bowling et al. 2004 (a playbook adapting within a game) [source] | Fine as E1's fallback. A play ends maybe 5–15 times per game, so convergence within 300 moves is doubtful |
| E3 | **Startup simulation to pick a mode**: in `register_initial_state` (15 s), simulate K modes on the real map against a model opponent through `generate_successor`, and pick the best | Monte-Carlo policy improvement [source: Tesauro & Galperin 1996] | At ~1,000 engine moves per second, 10 s buys ≈ 8 full games: SE ≈ 0.45 PPG per mode, far above the effects. Truncated rollouts (first 150 moves, food banked) are less noisy but shaped. **Low value.** It must also respect every observation rule (copies only, T-01). Ask before building, since it is novel use of the API |
| E4 | **Opponent-model + best response per enemy agent** (not team type): predict each enemy's next target with the belief + goal recognition (`directed`) and plan against it | E-025: goal-directed motion gave +0.009 on top of flags | Already mostly explored. Low marginal value |

---

## 4. A plan for tonight (≈ 8 h of compute, 8 workers)

Compute is ≈ 9,000 games/hour. Human set-up comes first, with no compute.

| step | what | games | time | decision it feeds |
|---|---|---|---|---|
| 0 | A lab file exposing B's constants as kwargs (defaults = lab5_smart) and a CMA-ES driver around `evaluate.py`'s game runner. Identity check 18/18 vs `lab5_smart`; `check_rules.py`. **Partly done** by the parallel session (`teams/greedy_lab_v6.py`, `eval/rl/cmaes_tune.py`; not reviewed here) | 18 | 2–4 h of work | none |
| 1 | **A's go/no-go table**: 4 modes (M0, M1, M2, M3 or M4), 400 tuning maps, 2 rotating pool opponents per map, 2 colours | 6,400 | 45 min | build the selector or not; also a screen of the 3 discrete modes |
| 2 | **B: CMA-ES**, n ≈ 11, λ = 24, μ = 12, 36 games per candidate (2 fresh seeds × 9 opponents × 2 colours), monitor run every 8 generations | ≈ 49,000 | 5.5 h | the tuned constants m |
| 3 | Screen m vs `lab5_smart` on 40 fresh tuning seeds × 8 opponents × 2 colours | 640 paired | 5 min | go to validation or not |
| 4 | Log E-027 (table) and E-028 (CMA run) in experiments.md, with seeds used | — | — | — |

Next day: the validation accept run (needs the fresh validation list, section 1.1), then C on the tuned base.

Seed bookkeeping:
- Step 1 uses 400 tuning seeds.
- Step 2 uses 2 per generation (≈ 115) plus 20 monitor seeds, so the 600-seed tuning list is nearly exhausted. Reuse seeds already used for step 1 in step 2: they are different experiments, and both are tuning.
- Or generate a second tuning list from a new generator seed and record it.

---

## 5. Pitfalls

### 5.1 Noise and selection bias
- **Winner's curse at three levels**:
  - (a) The best-sampled individual of a CMA-ES generation.
  - (b) The "best mode per map" label: our in-sample per-map oracle shows +0.20, but −0.03 cross-validated [verified, section 1.2].
  - (c) The best of several selectors, portfolios or CMA runs, chosen on the same data.
  - Remedies: report the distribution mean; regress differences instead of classifying argmax labels; confirm on unused seeds [source: Smith & Winkler 2006; Cameron 2016; Cawley & Talbot 2010].
- **Under-powered decisions**: with 120 validation seeds left, effects below ~+0.1 PPG cannot pass the accept rule (section 1.1).
  - Do not "rescue" a small effect by re-running on more seeds until the CI clears 0. That is optional stopping. Use a pre-registered sample size or an SPRT (evaluation.md section 3).
- **Repeated seeds are identical games** (T-36). CMA-ES must not re-evaluate a candidate on the same seed and count it as new information. Re-evaluation must use new seeds.

### 5.2 Overfitting to our own pool
- **Measured generalisation gap**: greedy_v2 scored 1.62 PPG in the pool round robin, but 1.16 against the blind-written held-out teams (a 32% gap, E-015) [verified].
  - Independently trained RL policies lost 34–72% of their reward against unseen partners or opponents [source: Lanctot 2017, as cited in evaluation.md].
  - An optimiser fed only our 8 teams will find their shared blind spots.
- **Pool composition**: every pool member is an attacker-plus-defender team. No pool member ever has both agents on our side (E-014, E-025: `recall` never fired in 800 games) [verified].
  - So CMA-ES or a learned module **never sees a double attack or a turtle** during tuning.
  - Add the league specialists `double_attack`, `turtle` and `camper2` to the *tuning* opponents. They are allowed tuning opponents; held-out and friend teams are not.
  - Or keep any learned formation logic off until it is tested against them.
- **Exploiting one opponent**: a parameter set can gain by exploiting a single pool member's bug, e.g. a loop in `camper`.
  - Guard: accept-rule clause 3 (no per-opponent regression beyond 0.5); also report the per-opponent matrix and the Nash average [source: Balduzzi 2018].
- **Non-transitivity / forgetting**: keep `lab5_smart` and older versions as tuning opponents, and track the minimum PPG against them [source: Vinyals 2019; Balduzzi 2019].
- **Seeds**: tune only on tuning seeds, draw new seeds per CMA generation, and log every seed range used (T-50).

### 5.3 Reward hacking (specification gaming)
- **Score margin, food eaten and survival time are not the objective.**
  - Margin rewards running up the score against weak teams. Food eaten rewards eating without banking. Survival time rewards turtling.
  - 3/1/0 points are the objective (evaluation.md section 1). A shaped signal may be used for *learning*, but every decision is made on points.
- **Ties**: under 3/1/0, a win plus a loss beats two ties. A fitness on win rate or Elo misprices ties.
- **Timing as a hidden cost**: a learned module that is fast on this laptop can approach the limit on SNOW. Keep max move ≤ 0.5 s under 10-way load, and re-measure on WSL (E-016).
- **Rule-adjacent exploits**: an optimiser can find behaviours that only work because of an engine quirk. The rules forbid manipulating game dynamics even when no code rule is broken (CLAUDE.md). Check new behaviour with `trace_game.py`, and ask when unsure.
- **Hidden-opponent fields** (`flags`) are allowed (Q3). Keep every learned use behind `USE_HIDDEN_OPPONENT_FLAGS` so that it can be switched off.
  - With the switch off, a learned weight on such a feature must fall back to a defined default, not crash.

### 5.4 Compliance of learned parts (rules R1–R10)
- **Runtime**: stdlib only. Weights as Python constants, or a read-only data file shipped next to `my_team.py` (Q6).
  - No numpy/torch at runtime unless the professor confirms installation (Q2).
  - Prefer constants: a missing data file in the tournament is a crash.
- **Logging during training**: only through wrapper teams in `eval/` (T-58), never in the submitted file. No file writes or prints in tournament mode (R6).
- **No `random.seed`** on the global module (CMA sampling happens in the tuner process, not in the agent). No threads or processes in the agent. Never catch `TimeoutFunctionException`.
- **Frozen files**: every tuned or learned version gets a new file (T-48).

### 5.5 What failed for others
See section 2.3 for the student reports, all [reported]. The recurring failure modes:
- RL with hand-crafted reward shaping that taught the wrong behaviour.
- Training mostly against the staff baseline, so it did not transfer.
- Too few training games.
- Deep RL that "was never trained enough".
- Q-learning abandoned for heuristics, or used only as a fallback.

Our own record agrees: hand-weighted one-step features ≈ greedy level (E-008, `feature` +0.07 [−0.08, +0.20] on 40 fresh seeds after +0.44 on 10 seeds, a winner's curse we already hit once) [verified].

## 6. How this relates to the existing docs (not edited by this report)

| existing entry | relation |
|---|---|
| proposals.md RL-1 (black-box tuning) | = design B, now with concrete settings (λ, games per candidate, CRN, monitoring) |
| proposals.md RL-2 (learned formation selector) | the offline-table version of design E1. Train only with a pool that includes double attackers and turtles (section 5.2) |
| proposals.md RL-3 (joint value function for search) | = design F |
| proposals.md RL-4 (deep MARL) | = design D, verdict unchanged: stretch only |
| proposals.md RL-5 (league with exploiters) | the proportionate version is section 2.5's "what this implies" |
| proposals.md RL-6 / SM-13 (in-game bandit) | = E2 |
| heuristics.md H-M09 (map profile → parameter set) | = design A. The pilot in sections 1.2–1.3 is its first evidence: per-map effects exist, no cheap feature predicted them on 50 maps |
| methods.md M-02, M-07, M-11 | B and C are M-02 + M-11 (CMA-ES instead of a GA). Student reports favour them over M-07 (section 2.3) |

If the user adopts any design, the follow-ups are:
- give it an experiment ID;
- update the statuses above (H-M09 → "pilot: no predictive feature found", citing that ID);
- add the new lab files to agents.md.

## 7. Open questions for the user

1. **A fresh validation seed list** (evaluation.md section 4) before the next accept decision: 120 seeds can resolve one decision at ≈ +0.1 PPG (section 1.1).
2. **May the CMA-ES tuning pool include league specialists** (`double_attack`, `turtle`, `camper2`) beside the reference pool? They are tuning opponents, not held-out ones, and without them no learned part ever sees a double attack (section 5.2).
3. **Is design E3** (simulating modes through `generate_successor` during the 15 s startup) acceptable? It uses only the public API on copies, but it is a novel use of startup time. The report rates it low value anyway.
4. **Promotion of `lab5_smart`** (release gate open since E-025) before tuning on top of it? Tuning a non-promoted base is fine, but the accept rule compares against the incumbent in `my_team.py`.
