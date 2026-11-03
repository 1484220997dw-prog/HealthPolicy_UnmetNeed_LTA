# Cost and non-financial barriers to healthcare in South Korea, 2020–2023: a four-wave latent transition analysis

<!-- Working note, not part of the submission: every estimate below is checked against the analysis output by src/07_check_manuscript.py. -->

---

## Abstract

**Background:** Countries monitor unmet healthcare need as an annual prevalence figure. Such figures show how many people went without needed care, not whether the same people keep going without it, and rarely separate barriers money can remove from barriers it cannot. South Korea is an informative case: near-universal enrolment combined with high cost sharing and a thin dental benefit.

**Objective:** To establish how long unmet healthcare need lasts, and whether cost-related and non-financial barriers behave as one phenomenon or two.

**Methods:** Longitudinal analysis of four annual waves of the Korea Health Panel, 2020–2023, following 10,508 adults aged 19 and over (36,605 person-wave observations). Forgone physician and dental care were each classified by whether the stated barrier was cost, giving four binary indicators. A latent transition model with measurement invariance across waves was fitted by weighted maximum likelihood, with 400 bootstrap replications and three-step covariate models.

**Results:** Any unmet need fell from 21.8% to 14.9%. Four statuses fitted the data: no unmet need, a cost barrier concentrated in dental care, a time and availability barrier, and a small compound status. Movement between the two single-barrier statuses was rare (0.1–6.5% per year). Cost barriers tracked income (lowest versus highest quintile, relative risk ratio 3.67, 95% CI 2.27–5.93); time barriers did not (0.84, 0.59–1.19).

**Conclusions:** Financial protection and service organisation reach different populations and cannot substitute for one another. Systems should report unmet need by barrier type and persistence, not as a single annual rate.

**Keywords:** unmet healthcare need; universal coverage; latent transition analysis; financial protection; dental care; Korea

---

## Research in context

**What is already known about the topic?** Cross-national monitoring treats unmet healthcare need as an annual prevalence indicator, and most national studies are cross-sectional. Work in Korea has shown that reported unmet need predicts later health and that non-financial reasons are given more often than cost. How durable these states are, and whether the person reporting a cost barrier in one year is the one reporting a non-financial barrier in the next, is not known.

**What does this study add to the literature?** Following a national cohort through four annual waves, we show that unmet need in a universal coverage system separates into a cost-driven status concentrated in dental care and a time-and-availability status among working adults, and that people almost never move between them. The cost status is the more persistent despite being the less prevalent, and the headline rate fell because fewer people entered, not because more left.

**What are the policy implications?** Benefit expansion and service redesign are not interchangeable: each reaches a different population. Health systems should publish unmet need split by barrier type and by how long it lasts, and treat repeated unmet need as the indicator that matters for targeting.

---

## 1\. Background

Unmet healthcare need has been used as a health-system indicator for fifty years, since Carr and Wolfe proposed it as a sociomedical measure of the gap between need and care received \[1\]. Its conceptual basis is the distinction between having a need, being able to reach care, and actually using it \[2–4\]. Self-reported unmet need captures that gap from the patient's side, including obstacles that utilisation data cannot see; its weakness is that the report depends on what the respondent believes they needed and on what counts locally as a legitimate reason for going without \[5\].

In practice the indicator is published as a single annual percentage, usually disaggregated by income and sometimes by stated reason \[6–8\]. Both the Organisation for Economic Co-operation and Development and the global monitoring of universal health coverage treat it as a complement to financial-protection measures \[9\]. This has two consequences that matter for policy. First, an annual rate cannot distinguish a population in which many people are briefly shut out from one in which a minority is shut out repeatedly, although the two call for different responses. Second, pooling reasons hides the fact that different barriers respond to different instruments: cost barriers are the target of benefit expansion and cost-sharing reform, whereas barriers of time, opening hours or distance are the target of service organisation.

South Korea is a useful setting for separating the two. Its National Health Insurance achieved universal enrolment within twelve years of its introduction, and is often cited as a model of rapid coverage expansion \[10\], yet it combines that coverage with persistently high cost sharing and a substantial non-benefit sector, which has kept catastrophic household spending on the policy agenda \[11\]. Ko showed with panel data that reported unmet need in Korea is followed by measurable declines in self-rated health and quality of life, so the indicator is not merely a reporting artefact \[12\]. Hwang, separating availability, accessibility and acceptability, found that the correlates differ sharply by reason \[13\], and Chung, in the most directly comparable longitudinal analysis, found that non-financial barriers are roughly four times as common as financial ones and that household income is not associated with the non-financial kind \[14\]. Dental care is the clearest instance of the financial side: the benefit package covers little of it, out-of-pocket shares are far higher than for physician care, and unmet dental need is strongly graded by income \[15,16\]. Against this, the benefit expansion announced in 2017 has been found to reduce spending on non-covered services only partially \[17\] while being associated with lower amenable mortality \[18\], and earlier catastrophic-coverage expansions reduced out-of-pocket spending on non-covered services \[19\].

The 2020–2023 window adds a further reason to look at persistence rather than levels. Across high-income countries the pandemic produced a wave of forgone care \[20\] that had not fallen back to its earlier level two years later \[7\], and whether it receded for everyone or left a residue concentrated in particular groups is an open question.

We therefore ask three questions. Do the reasons people give for going without care cluster into distinguishable statuses? How long does each status last from one year to the next? And do the same people move between cost-related and non-financial barriers, or are these separate populations?

## 2\. Methods

### 2.1 Data and study population

We analysed the second phase of the Korea Health Panel Survey (KHP), an annual nationally representative household panel conducted jointly by the Korea Institute for Health and Social Affairs and the National Health Insurance Service, using the four waves covering calendar years 2020–2023 (annual data version 2.4). The unmet-need module is administered to household members aged 19 and over.

The analysis cohort comprises all 10,508 adults who answered the unmet-need module in the 2020 wave. Respondents were retained in the likelihood for every subsequent wave, whether or not they answered it, so that attrition is handled by full-information maximum likelihood rather than by restricting the sample to complete responders. This yields 36,605 person-wave observations with the module answered, and 7,905 adults who answered in all four waves. Analyses are weighted by the KHP longitudinal individual weight from the baseline wave, rescaled to a mean of one.

### 2.2 Measures

Two survey items identify care that was needed but not obtained: one for physician or hospital care and one for dental care. Respondents who report going without care are then asked which of ten reasons applied, and may give more than one. We grouped the reasons into a **cost** group (the cost of care or of transport; earnings lost by taking time off) and a **non-financial** group (could not find the time; the provider was not open or no appointment was available; did not know where to go; transport or distance; mobility or health prevented the visit; the booking procedure was too complicated). Crossing the two domains with the two reason groups gives four binary indicators.

Two reasons were excluded from the indicators. Care being refused was reported by between none and four respondents per year, too few to carry information. "Other" was excluded because its frequency more than tripled in 2021 and fell back by 2023, a pattern more consistent with a change in how the category was applied than with a change in experience. Respondents who said they needed no care and those who said their need was met are coded alike, which makes the indicators invariant to a marked drift over the four waves in how often the "no care was needed" option was chosen.

Covariates, measured at each wave, were age group, sex, education, living with a partner, economic activity, equivalised household income quintile (household income divided by the square root of household size, ranked within wave), health coverage type (employment-based National Health Insurance, self-employed National Health Insurance, or Medical Aid), private health insurance, any of 30 physician-diagnosed chronic conditions, registered disability, self-rated health, having a usual source of care, and region of residence.

### 2.3 Statistical analysis

We fitted a latent transition model \[21,22\]. Each respondent occupies one of *K* unobserved statuses at each wave; the four indicators are conditionally independent given the status, with item-response probabilities held equal across waves, and transitions between waves follow a first-order Markov process with wave-specific matrices. Holding the measurement part invariant is what allows the transitions to be read as movement between fixed statuses rather than as change in the meaning of the statuses. For an individual *i* with indicator responses **y** the contribution to the likelihood is

> *L*ᵢ = Σ δ(s₁) ∏ₜ₌₁³ τₜ(sₜ₊₁ ∣ sₜ) ∏ₜ₌₁⁴ ∏ⱼ∈Oᵢₜ ρⱼ(yᵢₜⱼ ∣ sₜ)

where the sum runs over every sequence of statuses (s₁, s₂, s₃, s₄) the respondent could have occupied, and Oᵢₜ is the set of indicators observed for that person-wave, so that an unanswered wave contributes to the transition part but not the measurement part.

The number of statuses was chosen on the Bayesian information criterion, the size and interpretability of the resulting statuses, and classification quality measured by relative entropy \[23,24\]. Models with one to six statuses were fitted with wave-specific and with time-homogeneous transitions. Estimation used weighted expectation–maximisation \[25\] accelerated by squared extrapolation \[26\], with 60 random starting values screened and the best four iterated to convergence. The selected maximum was reached by 35 of the 60 screened starts and by all four of the polished ones, so it is not a local solution. Confidence intervals come from 400 non-parametric bootstrap replications over individuals, with each replicate's statuses matched to those of the point estimate by their item-response profiles.

Covariate associations were estimated in a three-step design \[27–29\]: the measurement model first, then assignment of respondents to statuses, then weighted regression. Model A is a multinomial logit for baseline status, reported as relative risk ratios against having no unmet need. Model B is a logit for being in any unmet-need status one year later, among person-waves that begin in one, with interval indicators and cluster-robust standard errors by individual. Both models were re-estimated weighting each respondent by the posterior probability of each status instead of using the modal assignment; results were materially unchanged (Appendix Table A5).

Prespecified sensitivity analyses restricted the sample to the 7,905 adults who answered all four waves, and reweighted that group by the inverse of a modelled probability of responding to all four waves (Appendix Tables A6–A8).

Analyses were carried out in Python 3.12. All code, the data dictionary, a synthetic replica of the analysis panel, and every table, figure and quoted number are available at \[GITHUB URL\]; the KHP microdata are released on application and may not be redistributed by the authors.

## 3\. Results

### 3.1 Levels and trends

Across the cohort, reported unmet need for physician or hospital care fell from 14.2% in 2020 to 11.0% in 2023, and unmet dental need from 15.3% to 9.6%. The fall was steeper for cost-related than for non-financial barriers in dental care (7.0% to 4.0% versus 8.9% to 6.0%) and modest for physician care (3.6% to 2.9% and 10.7% to 8.5%). Among non-financial reasons, not being able to find the time dominated throughout, reported by 8.6% of respondents for physician care and 7.4% for dental care in 2020; transport, distance and mobility together accounted for under 2% in every wave (Appendix Table A2).

### 3.2 Four statuses of unmet need

The Bayesian information criterion was minimised at four statuses among models with wave-specific transitions (58,143 for four statuses, against 58,545 for three and 58,156 for five; Appendix Table A1). Classification was sharp, with a relative entropy of 0.814 and mean posterior probabilities of 0.78 to 0.93 for the assigned status. Information criteria continued to fall for time-homogeneous models with five and six statuses, but the additional statuses subdivided the non-financial status without altering the picture of persistence, and the six-status solution classified respondents markedly less sharply (relative entropy 0.68); the five-status solution is reported in Appendix Table A9.

Table 2 shows what the four statuses are. The first, holding 78.2% of the cohort in 2020 and 85.1% in 2023, reports essentially no barriers. The second combines a high probability of forgoing dental care for cost (0.54) with a moderate probability of forgoing physician care for cost (0.31) and little else; we call it the **cost barrier** status, and it fell from 8.0% to 4.6%. The third is its mirror image: forgoing physician care (0.59) and dental care (0.47) for non-financial reasons, with cost probabilities below 0.08. Because the non-financial reasons behind it are overwhelmingly time and appointment availability rather than geography or supply, we call it the **time and availability barrier** status; it fell from 13.2% to 9.9%. The fourth is small, 0.6% in 2020 and 0.5% in 2023, and reports every barrier in both domains with probabilities above 0.94; we call it the **compound barrier** status.

Taking the three unmet-need statuses together, 21.8% of the cohort was in one in 2020 and 14.9% in 2023\.

### 3.3 Persistence and movement

Transitions were markedly asymmetric (Table 3). Averaged over the three intervals, 92.9% of those with no unmet need remained there, so the annual entry rate into some form of unmet need was 7.1%. Of those in the cost barrier status, 60.6% were still in it a year later and 34.0% had moved to no unmet need. The time and availability status was less sticky: 50.3% remained and 47.0% moved to no unmet need. The compound status retained only 22.1%, but its members rarely moved directly to having no unmet need (17.8% on average, ranging from 3.5% to 31.7% across the three intervals); they moved instead into one of the two single-barrier statuses.

The two single-barrier statuses barely exchanged members. Movement from cost to time and availability ranged from 1.2% to 6.5% a year, and in the other direction from 0.1% to 2.5%. Someone whose barrier was money in one year was very unlikely to report a non-financial barrier the next, and vice versa.

Among the 7,905 adults who answered all four waves, 69.0% were never in an unmet-need status, 15.3% were in one in a single year, and 15.7% in two or more years, including 8.0% in three or more and 3.6% in all four. Conditional on being in an unmet-need status, the probability of still being in one a year later was 50.9%, and it was higher in both later intervals than in the first: relative to 2020–2021, the adjusted odds of remaining were 2.66 (95% CI 2.16–3.27) for 2021–2022 and 1.64 (1.33–2.03) for 2022–2023. The headline rate therefore fell because fewer people entered, not because more of those already affected got out.

### 3.4 Who is in each status, and who stays

Table 1 shows that the two single-barrier statuses describe different populations. In 2020, 30.6% of the cost barrier status was in the lowest income quintile against 13.8% of the cohort, 32.5% had middle-school education or less, 11.0% held Medical Aid against 3.2% overall, and 28.1% were aged 65 or over. The time and availability status ran the other way: 61.2% had tertiary education, 37.2% were in the highest income quintile, 77.9% were in work, and only 11.3% were aged 65 or over. The compound status was the youngest, with 50.0% aged 19–39 and 87.4% in work.

The adjusted models confirm the dissociation (Figure 1, Appendix Tables A3–A4). Relative to the highest income quintile, the lowest quintile had a relative risk ratio of 3.67 (95% CI 2.27–5.93) for the cost barrier status, with a clear gradient across quintiles (2.54, 1.79 and 1.48 for the second, third and fourth), and Medical Aid coverage carried a ratio of 2.18 (1.44–3.29). For the time and availability status, income was not associated with membership at all (lowest quintile 0.84, 0.59–1.19); being in work was (1.66, 1.32–2.09), as was registered disability (1.42, 1.02–1.97), while being aged 65 or over was associated with lower risk (0.57, 0.41–0.80). Poor or very poor self-rated health predicted every unmet-need status.

Persistence was predicted less by social position than by which status a person started in. Starting in the compound status raised the odds of remaining in some unmet-need status by 4.44 (2.07–9.52) relative to starting in the cost barrier status, while starting in the time and availability status lowered them to 0.67 (0.54–0.82). Being in work (1.48, 1.15–1.89) and poor self-rated health (1.28, 1.03–1.60) were also associated with staying; income was not, once the starting status was accounted for.

Results were robust to restricting the sample to the complete responders and to inverse probability of response weighting: no status prevalence moved by more than 0.8 percentage points in any year (Appendix Tables A6–A8).

## 4\. Discussion

Three findings stand out. First, unmet healthcare need in a universal coverage system is not one phenomenon but at least two, and they are empirically separable: a cost-driven status concentrated in dental care, and a status driven by time and appointment availability. Second, the two are durable and nearly non-interchangeable. Fewer than one in fifteen members of either single-barrier status moved to the other within a year, which is the strongest evidence here that these are distinct populations rather than different expressions of a single underlying difficulty. Third, the cost status is the more persistent of the two even though it is the less prevalent, and the fall in the headline rate over 2020–2023 came from reduced entry rather than from increased exit.

These results extend the Korean literature in a specific way. Chung established with the same panel programme that non-financial barriers are the more common kind and are not graded by income \[14\]; our cross-sectional associations reproduce that, with an income gradient for cost barriers and none for time and availability barriers. What the longitudinal design adds is that the less prevalent barrier is the more lasting one, and that the two do not feed into each other. An annual prevalence figure, by pooling them, reports mostly on the more transient of the two.

The policy reading follows directly. Benefit expansion and service redesign are not alternative routes to the same destination. Expanding the dental benefit package would reach a population that is older, poorer, less educated and disproportionately covered by Medical Aid — and would address the barrier that lasts longer. Measures aimed at time and availability, such as extended opening hours, same-day appointment capacity and employment protections for medical visits, would reach working adults in the upper half of the income distribution, among whom income tells us nothing about risk. Since the groups scarcely overlap, progress on one will not show up as progress on the other, and a reform evaluated on the pooled indicator may appear to have failed when it has succeeded on the barrier it targeted. Korea's own experience illustrates the point: the 2017 expansion has been credited with lower amenable mortality \[18\] while reducing spending on non-covered services only partially \[17\].

The compound status deserves attention out of proportion to its size. At 0.5% of adults it is small as a share but not as a count, it is the status people are least likely to leave for having no unmet need at all, and it is concentrated among young working adults in poor self-rated health. Its members typically move into one of the single-barrier statuses rather than out of unmet need, which is what one would expect if two barriers must be removed in sequence. For targeting purposes, a system that reports only annual prevalence by income cannot see this group.

Our findings also bear on how unmet need is monitored internationally. Cross-national comparability of the indicator is already known to be fragile, with differences in question wording and in reporting norms producing different levels in surveys of the same country \[6–8\]. The present results suggest a second problem that is independent of wording: a single annual rate confounds the frequency of the condition with its duration, and two systems with identical rates can differ substantially in how much repeated deprivation they contain. Reporting the share of the population with unmet need in two or more years of a four-year panel, by barrier type, would be a modest and feasible addition to existing survey programmes, since the panel components needed already exist in several of them.

### 4.1 Limitations

The measure is subjective. It records care that respondents believed they needed and did not obtain, which is both its value and its limitation, since the threshold for reporting is shaped by expectations and by what counts locally as an acceptable reason \[5\]. Our non-financial status is dominated by not finding the time, which blends genuine constraint with the opportunity cost of a visit; it should not be read as a pure measure of service inaccessibility.

The design is descriptive. The window coincides both with the receding pandemic and with continuing benefit expansion, and we make no attempt to attribute the fall in prevalence to either; the transition estimates describe what happened, not what caused it.

One adult in four did not answer all four waves: 7,905 of the 10,508 in the baseline cohort did. We addressed this with full-information maximum likelihood, complete-case analysis and inverse probability of response weighting, and the three agree closely, but all three rest on the assumption that attrition is unrelated to unmet need given the observed covariates. Panel conditioning may also matter: the second phase of the KHP began in 2019, so our window starts early in the panel's life, when reporting may still be settling.

Three further constraints should be noted. The compound status is estimated from few respondents, so its transition probabilities carry wide intervals and its covariate associations — including an apparently protective association with chronic conditions, which most plausibly reflects the status being young rather than healthy — should be treated as provisional. Our indicators omit prescription medicines, where cost-related non-adherence was reported by too few respondents to model. And the findings describe one high-income single-payer system with unusually high cost sharing and an unusually thin dental benefit; the separation of barrier types should transfer to systems with a comparable split between covered and non-covered care, but the balance between them need not.

## 5\. Conclusion

Unmet healthcare need in South Korea fell between 2020 and 2023, yet roughly one adult in seven still went without care they believed they needed in 2023, and the fall came almost entirely from fewer people entering that state rather than from more people leaving it. Cost-related and non-financial barriers behave as separate, durable conditions affecting different populations, and the cost-related barrier — concentrated in dental care, graded by income, and most common among Medical Aid beneficiaries — is the more persistent of the two.

For policy-makers in Korea, the specific implications are to extend the dental benefit package, where the persistent cost barrier is concentrated, and to pursue time and availability measures as a separate track with its own target population, rather than expecting either to register on the pooled indicator. For health systems more generally, and for the agencies that monitor universal health coverage, the implication is about measurement: annual prevalence of unmet need should be reported split by barrier type and alongside a measure of persistence, such as the share of the population reporting unmet need in two or more of four consecutive survey years. Both are available in existing panel surveys and neither requires new data collection.

---

## Tables and figure

**Table 1\.** Characteristics of the 2020 baseline cohort, overall and by latent status (weighted percentages; unweighted *n*). *p*\-values are from Pearson tests on weighted shares rescaled to the Kish effective sample size.

**Table 2\.** Item-response probabilities, status prevalence by year and classification quality for the four-status model (95% bootstrap intervals from 400 replications).

**Table 3\.** Annual transition probabilities between latent statuses, 2020–2021, 2021–2022 and 2022–2023 (95% bootstrap intervals).

**Figure 1\.** (A) Prevalence of each unmet-need status by year, with 95% bootstrap intervals; the share of the cohort with no unmet need is printed beneath each year rather than plotted, so that the three unmet-need statuses remain legible. (B) Adjusted odds of being in an unmet-need status one year later among person-waves that begin in one, from Model B, with interval indicators omitted from the plot.

## References

[1] Carr W, Wolfe S. Unmet needs as sociomedical indicators. Int J Health Serv 1976;6(3):417–30.

[2] Andersen RM. Revisiting the behavioral model and access to medical care: does it matter? J Health Soc Behav 1995;36(1):1–10.

[3] Gulliford M, Figueroa-Munoz J, Morgan M, Hughes D, Gibson B, Beech R, et al. What does 'access to health care' mean? J Health Serv Res Policy 2002;7(3):186–8.

[4] Levesque JF, Harris MF, Russell G. Patient-centred access to health care: conceptualising access at the interface of health systems and populations. Int J Equity Health 2013;12:18.

[5] Allin S, Grignon M, Le Grand J. Subjective unmet need and utilization of health care services in Canada: what are the equity implications? Soc Sci Med 2010;70(3):465–72.

[6] OECD. Health for everyone? Social inequalities in health and health systems. Paris: OECD Publishing; 2019.

[7] OECD, European Commission. Health at a glance: Europe 2022. Paris: OECD Publishing; 2022.

[8] OECD. Health at a glance 2023. Paris: OECD Publishing; 2023.

[9] World Health Organization, World Bank. Tracking universal health coverage: 2023 global monitoring report. Geneva: WHO; 2023.

[10] Kwon S. Thirty years of national health insurance in South Korea: lessons for achieving universal health care coverage. Health Policy Plan 2009;24(1):63–71.

[11] Kim Y, Yang B. Relationship between catastrophic health expenditures and household incomes and expenditure patterns in South Korea. Health Policy 2011;100(2–3):239–46.

[12] Ko H. Unmet healthcare needs and health status: panel evidence from Korea. Health Policy 2016;120(6):646–53.

[13] Hwang J. Understanding reasons for unmet health care needs in Korea: what are health policy implications? BMC Health Serv Res 2018;18:557.

[14] Chung W. Characteristics associated with financial or non-financial barriers to healthcare in a universal health insurance system: a longitudinal analysis of Korea Health Panel survey data. Front Public Health 2022;10:828318.

[15] Kim NH, Kim CB, Shin HS. Inequality in unmet dental care needs among South Korean adults. BMC Oral Health 2017;17:80.

[16] Sohn M, Che X, Park HJ. Unmet dental care needs among Korean National Health Insurance beneficiaries based on income inequalities: results from five waves of a population-based panel study. Healthcare 2020;8(2):124.

[17] Ji S, Lee M, Choi M. The impact of the expanded health insurance coverage policy on healthcare spending: evidence from South Korea. Int J Equity Health 2024;23:122.

[18] Eun SJ. Evaluating the effects of the 2017 National Health Insurance coverage expansion on amenable mortality in South Korea. Soc Sci Med 2024;344:116574.

[19] Kim M, Shin D, Shin H. Effects of catastrophic coverage expansion on out-of-pocket spending for non-covered services and financial equity: evidence from South Korea's National Health Insurance. Healthcare 2026;14(3):302.

[20] Smolić Š, Čipin I, Međimurec P. Access to healthcare for people aged 50+ in Europe during the COVID-19 outbreak. Eur J Ageing 2021;19(4):793–809.

[21] Collins LM, Lanza ST. Latent class and latent transition analysis: with applications in the social, behavioral, and health sciences. Hoboken: Wiley; 2010.

[22] Lanza ST, Collins LM. A new SAS procedure for latent transition analysis: transitions in dating and sexual risk behavior. Dev Psychol 2008;44(2):446–56.

[23] Nylund KL, Asparouhov T, Muthén BO. Deciding on the number of classes in latent class analysis and growth mixture modeling: a Monte Carlo simulation study. Struct Equ Modeling 2007;14(4):535–69.

[24] Nylund-Gibson K, Choi AY. Ten frequently asked questions about latent class analysis. Transl Issues Psychol Sci 2018;4(4):440–61.

[25] Dempster AP, Laird NM, Rubin DB. Maximum likelihood from incomplete data via the EM algorithm. J R Stat Soc Series B Stat Methodol 1977;39(1):1–22.

[26] Varadhan R, Roland C. Simple and globally convergent methods for accelerating the convergence of any EM algorithm. Scand J Stat 2008;35(2):335–53.

[27] Vermunt JK. Latent class modeling with covariates: two improved three-step approaches. Polit Anal 2010;18(4):450–69.

[28] Bakk Z, Oberski DL, Vermunt JK. Relating latent class assignments to external variables: standard errors for correct inference. Polit Anal 2014;22(4):520–40.

[29] Bakk Z, Kuha J. Two-step estimation of models between latent classes and external variables. Psychometrika 2018;83(4):871–92.
