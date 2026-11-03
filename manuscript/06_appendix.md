# Appendix (online e-component)

Cost and non-financial barriers to healthcare in South Korea, 2020–2023:
a four-wave latent transition analysis

All appendix tables are supplied as CSV files in `output/tables/` of the replication
repository and are reproduced here in full. Numbering follows the journal's convention
of distinguishing appendix items from those in the main text.

---

## A. Measures

### A.1 Survey items

The Korea Health Panel unmet-need module puts two filter questions to every household
member aged 19 and over, each referring to the previous twelve months:

* **AH1** — whether there was an occasion on which the respondent thought they needed to
  visit a hospital or clinic but in the end did not go. Response options: (1) yes, in
  the end I could not go; (2) no, there was no such occasion; (3) there was no occasion
  on which hospital or clinic treatment or examination was needed.
* **AH2** — the same question for dental care, with the same three options.

Respondents answering (1) are then shown ten reasons and asked which applied; multiple
reasons may be selected.

### A.2 Construction of the four indicators

| Indicator | Definition |
|---|---|
| Physician care forgone, cost barrier | AH1 = 1 **and** at least one of reasons 1–2 |
| Physician care forgone, non-financial barrier | AH1 = 1 **and** at least one of reasons 3–8 |
| Dental care forgone, cost barrier | AH2 = 1 **and** at least one of reasons 1–2 |
| Dental care forgone, non-financial barrier | AH2 = 1 **and** at least one of reasons 3–8 |

Reason 1 is the cost of care including transport; reason 2 is earnings lost by taking
time off; reason 3 is not being able to find the time; reason 4 is the provider not being
open when wanted or no appointment being available; reason 5 is not knowing which
hospital or department to attend; reason 6 is inconvenient transport or distance;
reason 7 is mobility difficulty or ill health preventing the visit; reason 8 is the
booking procedure being too difficult or complicated.

Reason 9 (care was refused) and reason 10 ("other") are not used. Reason 9 was reported
by 4, 2, 2 and 0 respondents in the four waves. Reason 10 rose from 107 to 361 physician
responses between 2020 and 2021 and then fell back to 57 by 2023, a pattern that
indicates a change in how the category was applied rather than in experience.

Response options (2) and (3) are both coded 0. This matters: the share choosing option
(3) for physician care fell from 444 respondents in 2020 to 34 in 2023, and for dental
care from 1,931 to 597. Collapsing the two categories makes the indicators invariant to
that shift, which would otherwise create spurious transitions.

### A.3 Prescription medicines

The module also asks whether there was an occasion on which the respondent did not fill
a prescription (AH3) and why. Cost was given as the reason by 3, 3, 4 and 1 respondents
across the four waves. The item carries no usable information at this sample size and is
excluded from the indicators; this is stated as a limitation in the main text.

---

## B. Statistical model

### B.1 Likelihood

Let *S*<sub>it</sub> ∈ {1,…,*K*} be the latent status of individual *i* at wave *t*,
*t* = 1,…,4, and *Y*<sub>itj</sub> ∈ {0,1} the *j*-th of *J* = 4 indicators. The model
has three sets of parameters: initial status probabilities δ<sub>k</sub> = P(*S*<sub>i1</sub> = *k*);
wave-specific transition probabilities τ<sub>t,kl</sub> = P(*S*<sub>i,t+1</sub> = *l* | *S*<sub>it</sub> = *k*);
and item-response probabilities ρ<sub>jk</sub> = P(*Y*<sub>itj</sub> = 1 | *S*<sub>it</sub> = *k*),
constrained equal across waves.

With O<sub>it</sub> the set of indicators observed for person-wave (*i*,*t*), the
individual likelihood is

*L*<sub>i</sub> = Σ<sub>s₁=1</sub><sup>K</sup> … Σ<sub>s₄=1</sub><sup>K</sup>
  δ<sub>s₁</sub>
  ∏<sub>t=1</sub><sup>3</sup> τ<sub>t,s<sub>t</sub>s<sub>t+1</sub></sub>
  ∏<sub>t=1</sub><sup>4</sup> ∏<sub>j∈O<sub>it</sub></sub>
  ρ<sub>js<sub>t</sub></sub><sup>y<sub>itj</sub></sup> (1 − ρ<sub>js<sub>t</sub></sub>)<sup>1−y<sub>itj</sub></sup>

and the estimated log-likelihood is Σ<sub>i</sub> *w*<sub>i</sub> log *L*<sub>i</sub>,
with *w*<sub>i</sub> the baseline longitudinal weight rescaled to mean one. A wave the
respondent did not answer has O<sub>it</sub> = ∅, so its measurement product equals 1
and the wave contributes only through the transition terms. This is full-information
maximum likelihood under the assumption that missingness is independent of the
unobserved responses given the observed ones.

Free parameters number (*K* − 1) + 3*K*(*K* − 1) + *JK* for wave-specific transitions,
and (*K* − 1) + *K*(*K* − 1) + *JK* when transitions are held constant across waves; for
the selected model this is 55. The Bayesian information criterion uses the number of
sampled individuals (10,508).

### B.2 Estimation

The sums over latent trajectories are evaluated by the scaled forward–backward
recursion, and the parameters by expectation–maximisation. Plain EM converges very
slowly on this likelihood — the four-status model had not converged to a tolerance of
10⁻⁷ after 5,000 iterations — so each iteration pair is extrapolated by the SQUAREM
scheme, with a stabilising EM step and a fall-back to ordinary EM whenever the
extrapolated point does not improve the likelihood. This reaches the same maximum in
about 3,300 iterations.

Sixty random starting values were drawn (Dirichlet for δ and for the rows of τ,
indicator base rates perturbed by a uniform multiplier for ρ) and run for 300
iterations; the four with the highest likelihood were then iterated to convergence. For
the selected model, 35 of the 60 screened starts had already reached the maximum of
−28,816.85 within the 300-iteration screen, and all four polished starts converged to
it, which indicates that it is not a local solution. The screening likelihoods for every
start are in the run output.

Statuses are ordered by total barrier load, lowest first. In the bootstrap this rule is
not enough on its own, because the cost barrier and the time and availability statuses
have nearly identical total loads (1.07 and 1.17), so an ordering rule flips their
labels in some replicates and produces intervals that straddle both. Each replicate is
therefore matched to the point estimate by the assignment of statuses that minimises the
total squared distance between item-response profiles.

### B.3 Covariate models

Model A is a weighted multinomial logit for latent status in 2020, with no unmet need as
the reference category and standard errors clustered by household. Model B is a weighted
logit for being in any unmet-need status at *t* + 1 among person-waves in one at *t*,
including the status at *t* and interval indicators, with standard errors clustered by
individual. Both are estimated by maximising the weighted log-likelihood directly, with
a cluster-robust sandwich variance, so that the survey weight, the posterior weight used
in the sensitivity analysis and the clustering are handled in one estimator.

The main text reports the modal-assignment version. Appendix Table A5 reports Model B
with every person-wave entered twice, once for each outcome, weighted by the survey
weight times the posterior probability of the relevant status pair; this is the
proportional-assignment analogue of the Bolck–Croon–Hagenaars correction and does not
discard the uncertainty in the assignment.

---

## C. Appendix tables

| Table | Content | File |
|---|---|---|
| A1 | Model selection: one to six statuses, wave-specific and time-homogeneous transitions | `tableA1_model_selection.csv` |
| A2 | Weighted prevalence of each individual reason, by domain and year | `tableA2_reason_prevalence.csv` |
| A3 | Model A in full: multinomial logit for 2020 latent status | `tableA3_model_a_baseline_status.csv` |
| A4 | Model B in full: logit for remaining in an unmet-need status | `tableA4_model_b_persistence.csv` |
| A5 | Model B re-estimated with posterior-probability weights | `tableA5_model_b_posterior_weighted.csv` |
| A6 | Status prevalence among the 7,905 adults who answered all four waves | `tableA6_completecase_prevalence.csv` |
| A7 | Baseline characteristics by number of waves answered | `tableA7_attrition.csv` |
| A8 | Status prevalence with inverse probability of response weighting | `tableA8_ipw_prevalence.csv` |
| A9 | The five-status solution, for comparison with the selected model | `tableA9_five_status_solution.csv` |
| A10 | Models A and B side by side, one row per characteristic | `tableA10_covariates_combined.csv` |

### Notes on the sensitivity analyses

**A6 and A8 (attrition).** Both tables sum the posterior status probabilities rather
than modal assignments, so the only difference from the main estimates is the sample and
the weight. The complete-case estimates differ from the main estimates by at most 0.8
percentage points and the inverse-probability weighted estimates by at most 0.6, for
every status in every year. The response model used for A8 includes age group, sex,
education, income quintile, coverage type, chronic conditions, disability, self-rated
health and region; predicted probabilities are truncated at 0.05.

**A7 (who leaves the panel).** Respondents who answered all four waves differ from those
who answered fewer. Those who left were younger (36.4% versus 25.5% aged 19–39), more
often educated to tertiary level (52.9% versus 47.4%), less often holders of private
health insurance (75.5% versus 81.1%), less often diagnosed with a chronic condition
(32.8% versus 42.4%) and less often in possession of a usual source of care (41.5%
versus 48.6%); employment and self-rated health were almost the same in the two groups.
The young and healthy profile of the leavers is the profile of the time and availability
status, so restricting the analysis to the complete responders would, if anything,
understate that status — which is the direction the complete-case estimates in Table A6
in fact move. This is the pattern the full-information approach is designed to
accommodate, but it cannot be ruled out that leavers differed in unmet need for reasons
the covariates do not capture.

**A9 (number of statuses).** The five-status solution splits the time and availability
status into a physician-dominated version (non-financial barrier to physician care 0.52,
everything else below 0.03) and a version in which both domains are affected
(non-financial barriers 0.60 for physician care and 0.70 for dental care). The cost
barrier status (physician cost 0.30, dental cost 0.60), the compound status and the
pattern of persistence are unchanged, and the new physician-only status is the most
weakly classified of the five (mean posterior probability 0.66, against 0.78–0.93 in the
four-status model). Because the split adds no new barrier type and lowers the Bayesian
information criterion only under the time-homogeneous specification (57,927 against
58,011 for four statuses, while the wave-specific five-status model raises it to 58,156
against 58,143), the four-status model was retained.

---

## D. Reproducibility

Every number in the manuscript is written to `output/logs/numbers.json` by the script
that produces the tables, and the run that produced the submitted version is recorded in
`output/logs/run_log.txt` together with the commit hash. The repository contains:

* `src/` — the complete pipeline, in five numbered steps plus a sensitivity step;
* `input/dictionary/data_dictionary.csv` — every derived variable and the KHP items it
  comes from;
* `input/synthetic/synthetic_unmet_panel.csv` — a synthetic replica of the analysis
  panel, drawn from the fitted model and from the observed covariate margins, which
  allows the whole pipeline to be run without the restricted microdata;
* `notebooks/KHP_UnmetNeed_LTA_Colab.ipynb` — the same analysis as a Google Colab
  notebook.

The Korea Health Panel microdata are released on application at
<https://www.khp.re.kr> under a data-use agreement that forbids redistribution; neither
the source files nor any person-level derivative of them is included in the repository.
