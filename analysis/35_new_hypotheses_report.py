#!/usr/bin/env python3
"""Build the comprehensive Word report for the new H1-H5 hypothesis set.
Output: analysis/35_new_hypotheses_report.docx
"""
import os
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, 'figures')
doc = Document()
sec = doc.sections[0]
sec.top_margin = sec.bottom_margin = Inches(1.0)
sec.left_margin = sec.right_margin = Inches(1.0)
style = doc.styles['Normal']; style.font.name = 'Times New Roman'; style.font.size = Pt(12)
style.paragraph_format.space_after = Pt(6)

def body(t):
    p = doc.add_paragraph(); p.paragraph_format.line_spacing = 1.5; p.add_run(t); return p
def H1(t): return doc.add_heading(t, level=1)
def H2(t): return doc.add_heading(t, level=2)
def field(label, text):
    p = doc.add_paragraph(); p.paragraph_format.line_spacing = 1.4
    r = p.add_run(label + ' '); r.bold = True; p.add_run(text); return p
def verdict(v):
    p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(4)
    r = p.add_run('Verdict: '); r.bold = True
    r2 = p.add_run(v); r2.bold = True; r2.italic = True
def figure(num, title, fname, note, width=5.0):
    cap = doc.add_paragraph(); cap.paragraph_format.space_before = Pt(6)
    r = cap.add_run(num); r.bold = True; cap.add_run('  '); r = cap.add_run(title); r.italic = True
    img = doc.add_paragraph(); img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    img.add_run().add_picture(os.path.join(FIG, fname), width=Inches(width))
    np = doc.add_paragraph(); nr = np.add_run('Note. '); nr.italic = True; np.add_run(note)
    for r in np.runs: r.font.size = Pt(10)
    np.paragraph_format.space_after = Pt(10)

# ───────── Title ─────────
doc.add_heading('Statistical Assessment of the Revised Hypotheses (H1–H5)', level=1)
body('Master Thesis — Arne Floh   |   Cleaned sample N = 187   |   June 2026')
body(
    'This report evaluates five hypotheses derived from the experimental results. '
    'Each is assessed for support, full statistical detail, robustness and '
    'methodological considerations, potential confounds and controls, a dedicated '
    'publication-style figure, and theoretical implications. The investment '
    'measure ranges from 0 to 3 per startup. Founder gender was manipulated '
    'between subjects (male / female / mixed teams, both startups sharing the '
    'condition); industry was within subjects (SiteVision = male-typed ConTech; '
    'BalanceUp = female-typed wellness); presentation order was counterbalanced. '
    'Emotional intelligence (EI) was measured with the 16-item WLEIS. Analyses '
    'excluding the mixed condition use N = 117 (62 male-, 55 female-founder).')

# ════════════════════ H1 ════════════════════
H1('H1 — Investors Allocate More to Male-Typed than Female-Typed Industries')
verdict('Supported (robust main effect, but order-moderated and success-mediated).')
field('Interpretation.',
    'On a within-person basis participants invested substantially more in the '
    'male-typed venture (SiteVision) than in the female-typed venture (BalanceUp). '
    'This is the strongest and most reliable effect in the study and establishes '
    'the gender-typing of the choice environment.')
field('Statistical results.',
    'SiteVision M = 2.20 (SD = 0.92); BalanceUp M = 1.72 (SD = 0.91). '
    'Mean within-person difference = 0.481, SE = 0.095, paired t(186) = 5.08, '
    'p < .001, 95% CI [0.294, 0.668], Cohen\'s d_z = 0.37. N = 187.')
field('Methodological considerations.',
    'The effect is highly significant and survives an attention filter (dropping '
    'the fastest 5%: p < .001) and holds in both experience subgroups. It does '
    'not change sign across specifications. The paired design controls for '
    'between-person variance; assumptions (normality of differences, no extreme '
    'outliers) are satisfied and power is ample (achieved power > .99 for d_z = 0.37 '
    'at N = 187).')
field('Potential confounds and controls.',
    'Two variables matter. First, perceived startup success: adding the '
    'success-probability difference reduces the industry coefficient to b = 0.147, '
    'p = .059, and the investment gap correlates r = .75 with the success gap, '
    'indicating that the effect operates largely through perceived viability. '
    'Second, pitch order: the industry × order interaction is b = 1.24, p < .001 — '
    'the preference is +1.08 (p < .001) when SiteVision is shown first but −0.15 '
    '(p = .24) when BalanceUp is shown first. Because order was balanced across '
    'conditions, the average effect is not confounded, but its generalizability is '
    'bounded by this order sensitivity. Participant gender and investment '
    'experience do not materially alter the effect.')
figure('Figure H1', 'Mean Investment by Industry Gender-Typing',
    'figH1_industry.png',
    'Bars show mean amount invested (0–3) with ±1 SE; bracket reports the paired '
    'test. Interpret as a within-person preference for the male-typed venture. '
    'x-axis: startup / industry typing; y-axis: mean amount invested.')
field('Implications.',
    'The result is consistent with role-congruity and lack-of-fit accounts at the '
    'industry level: the male-typed industry is read as more viable. It locates '
    'gender bias in the gender-typing of the sector rather than in founder gender '
    'per se, consistent with Tonoyan and Strohmeyer (2021) and Sperber and Linder.')

# ════════════════════ H2 ════════════════════
H1('H2 — Male Founders in Male Industries > Female Founders in Female Industries')
verdict('Not supported (two-tailed); partially / directionally supported only.')
field('Interpretation.',
    'Comparing the two gender-congruent cells — a male founder in the male-typed '
    'industry (masculine-congruent) versus a female founder in the female-typed '
    'industry (feminine-congruent) — the masculine-congruent venture attracted '
    'numerically more capital, but the difference was not significant on a '
    'conventional two-tailed test. The non-parametric test was significant, so the '
    'evidence is suggestive rather than conclusive. This congruent-cell contrast '
    'should not be confused with the incongruent-cell comparison reported '
    'elsewhere (female-in-male vs male-in-female industry, t = 3.34, p = .001), '
    'which is the genuinely significant founder-by-industry result.')
field('Statistical results.',
    'Masculine-congruent M = 2.13 (SD = 0.91, n = 62); feminine-congruent '
    'M = 1.85 (SD = 0.91, n = 55). Difference = 0.274, SE = 0.169, Welch '
    't(113) = 1.62, two-tailed p = .107, one-tailed p = .054, 95% CI '
    '[−0.060, 0.609], Cohen\'s d = 0.30. Mann–Whitney U one-sided p = .041. '
    'N = 117.')
field('Methodological considerations.',
    'The result is fragile: significant only under a directional or rank-based '
    'test and not under the standard two-tailed t. It is a between-subjects '
    'comparison, so it carries less power than the within-person H1; with n ≈ 60 '
    'per cell, power to detect d = 0.30 is only about .37, so the null is '
    'partly a power limitation. No influential outliers were detected.')
field('Potential confounds and controls.',
    'Perceived success does not explain this contrast (adjusted b = −0.074, '
    'p = .602), unlike H1. Pitch order again moderates strongly: the masculine-'
    'congruent × order interaction is b = 1.51, p < .001, so the difference is '
    'concentrated in the SiteVision-first order. Participant gender and experience '
    'do not change the conclusion.')
figure('Figure H2', 'Investment in Masculine- versus Feminine-Congruent Startups',
    'figH2_congruent.png',
    'Bars show mean amount invested (0–3) with ±1 SE; bracket reports the '
    'two-tailed Welch test and effect size. Interpret cautiously: the gap is '
    'small and significant only under directional/rank tests. x-axis: congruent '
    'cell; y-axis: mean amount invested.')
field('Implications.',
    'Role-congruity theory predicts an advantage for gender-congruent founders. '
    'The direction is consistent with this, but the magnitude is small and '
    'unreliable, indicating that any pure founder-level congruity premium is weak '
    'once the dominant industry effect (H1) is set aside.')

# ════════════════════ H3 ════════════════════
H1('H3 — Lower-EI Investors Show a Larger Masculine-Congruent Preference')
verdict('Not supported (interaction non-significant; direction as predicted).')
field('Interpretation.',
    'The hypothesis is that the masculine-versus-feminine congruence gap shrinks '
    'as EI rises. The estimated EI × congruence interaction is in the predicted '
    'direction — the gap is larger at lower EI (0.46) than at higher EI (0.10) — '
    'but it does not approach significance. A simple low-EI subgroup comparison is '
    'directionally significant (one-tailed p = .032), but the formal moderation '
    'test, which is what H3 asserts, is null.')
field('Statistical results.',
    'OLS focal investment ~ congruence × EI (mean-centred), mixed condition '
    'excluded. Interaction b = −0.143, SE = 0.239, t(113) = −0.60, p = .553, '
    '95% CI [−0.617, 0.332]. Model R² = .026, adjusted R² ≈ .000. N = 117. '
    'Median-split congruence gap: lower-EI = 0.46, higher-EI = 0.10.')
field('Methodological considerations.',
    'The interaction is far from significant and the model explains essentially '
    'no variance. Re-running the moderation for each WLEIS dimension separately '
    'yields no significant interaction (smallest p = .328 for ROE; SEA p = .931, '
    'wrong-signed). Interaction tests are inherently low-powered, so a small true '
    'effect cannot be excluded, but the present data provide no support. No '
    'multicollinearity concern (predictors mean-centred; VIFs near 1).')
field('Potential confounds and controls.',
    'Controlling for perceived success and pitch order leaves the interaction '
    'non-significant (b = −0.082, p = .671). The earlier low-EI subgroup effect is '
    'itself absorbed by perceived success, so the apparent EI patterning likely '
    'reflects success perception rather than EI-specific debiasing.')
figure('Figure H3', 'Congruence Gap at Lower versus Higher EI',
    'figH3_ei_moderation.png',
    'Bars show the masculine-minus-feminine congruence gap (0–3 scale) within '
    'each EI half. A debiasing effect would appear as a much smaller bar at '
    'higher EI; the interaction is non-significant. x-axis: EI group; y-axis: '
    'congruence gap.')
field('Implications.',
    'Emotional-intelligence theory predicts that higher EI attenuates '
    'stereotype-driven allocation. The direction is consistent but the effect is '
    'not statistically reliable, so the data do not support EI as a moderator of '
    'congruence bias in this sample.')

# ════════════════════ H4 ════════════════════
H1('H4 — Male Participants Score Lower on EI than Female Participants')
verdict('Supported (robust; concentrated in the appraisal dimensions).')
field('Interpretation.',
    'Female participants reported significantly higher emotional intelligence than '
    'male participants, driven by the two appraisal facets (self- and others\' '
    'emotion appraisal), with no difference on use or regulation of emotion.')
field('Statistical results.',
    'Total EI: male M = 4.97 (SD = 0.71, n = 84), female M = 5.32 (SD = 0.77, '
    'n = 100). Difference = −0.348, SE = 0.109, Welch t(180) = −3.19, p = .002, '
    '95% CI [−0.564, −0.133], Cohen\'s d = −0.47. By dimension: SEA d = −0.59, '
    'p < .001; OEA d = −0.66, p < .001; UOE d = −0.19, p = .206; ROE d = +0.11, '
    'p = .462. N = 184 (gendered respondents).')
field('Methodological considerations.',
    'The effect is robust and well-powered. It is unchanged after adjusting for '
    'age and STEM field of study (adjusted gender b = 0.355, p = .002), and the '
    'two groups are well matched on these covariates (mean age 23.3 vs 23.6; STEM '
    '23% vs 13%). No assumption violations of note.')
field('Potential confounds and controls.',
    'Age and field do not account for the difference. Note a design implication: '
    'because EI is correlated with participant gender, any analysis that conditions '
    'EI moderation on participant gender operates on a restricted EI range within '
    'each gender and loses sensitivity.')
figure('Figure H4', 'WLEIS Scores by Participant Gender',
    'figH4_ei_gender.png',
    'Bars show mean WLEIS scores (1–7) with ±1 SE for male and female '
    'participants across the total scale and four dimensions. * p < .05, '
    '** p < .01, *** p < .001, ns = not significant. x-axis: EI dimension; '
    'y-axis: mean score.')
field('Implications.',
    'The pattern matches the broader EI literature: women score higher on '
    'perceiving and appraising emotions, with negligible differences in regulation '
    'and instrumental use. It also provides an ironic counterpoint to the '
    '"women are more emotional / less rational" stereotype discussed in the '
    'review, since women here showed higher measured emotional ability.')

# ════════════════════ H5 ════════════════════
H1('H5 — Among Low-EI Investors, Experience Shrinks the Congruence Gap')
verdict('Not supported (interaction non-significant; direction as predicted).')
field('Interpretation.',
    'Within the low-EI subgroup, the masculine-versus-feminine congruence gap was '
    'numerically smaller among investors with prior investment experience (0.35) '
    'than among those without (0.63), consistent with the idea that experience '
    'dampens stereotype-driven allocation. However, the moderation is not '
    'statistically significant and the subgroup is small.')
field('Statistical results.',
    'OLS within low-EI: focal investment ~ congruence × experience. Interaction '
    'b = −0.283, SE = 0.509, t = −0.56, p = .580, 95% CI [−1.304, 0.737]. '
    'Model R² = .067, adjusted R² = .014. N = 57 (no-experience n = 22; '
    'experience n = 35). Congruence gap: no experience = 0.63, experience = 0.35.')
field('Methodological considerations.',
    'This is the least powered test in the set: a three-way contingency '
    '(low-EI × congruence × experience) estimated on 57 observations split into '
    'four cells as small as 10–20. Power to detect even a moderate interaction is '
    'very low, so the non-significant result is uninformative about a true effect. '
    'The wide confidence interval reflects this. No outlier or assumption issues '
    'beyond the sample-size limitation.')
field('Potential confounds and controls.',
    'Given the negligible power, formal confound adjustment is not informative; '
    'the descriptive direction is consistent with experience as a secondary '
    'debiasing factor, but the data cannot establish it. Pitch order again '
    'underlies the broader congruence effect.')
figure('Figure H5', 'Congruence Gap by Investment Experience (Low-EI Investors)',
    'figH5_experience.png',
    'Bars show the masculine-minus-feminine congruence gap (0–3 scale) within the '
    'low-EI subgroup, split by prior investment experience. A smaller bar for '
    'experienced investors would support H5; the interaction is non-significant. '
    'x-axis: experience group; y-axis: congruence gap.')
field('Implications.',
    'The descriptive pattern is compatible with learning- or expertise-based '
    'debiasing accounts, whereby experienced investors rely less on gender-typed '
    'heuristics. The study is underpowered to test this, so it is best framed as a '
    'direction for future, adequately powered research.')

# ════════════════════ Summary ════════════════════
H1('Summary of Outcomes')
t = doc.add_table(rows=1, cols=3); t.style = 'Light List Accent 1'
for i, h in enumerate(['Hypothesis', 'Key statistic', 'Outcome']):
    r = t.rows[0].cells[i].paragraphs[0].add_run(h); r.bold = True
for hh, st, oc in [
    ('H1 Industry effect', 't(186) = 5.08, p < .001, d_z = 0.37', 'Supported (order-moderated)'),
    ('H2 Congruent cells', 't(113) = 1.62, p = .107; MW p = .041, d = 0.30', 'Not supported (directional only)'),
    ('H3 EI moderation', 'b = −0.14, p = .553', 'Not supported'),
    ('H4 EI by gender', 't(180) = −3.19, p = .002, d = −0.47', 'Supported'),
    ('H5 Experience × congruence', 'b = −0.28, p = .580', 'Not supported (underpowered)')]:
    c = t.add_row().cells; c[0].text = hh; c[1].text = st; c[2].text = oc
body('')
body(
    'Overall, the two reliable findings are the industry effect (H1) and the EI '
    'gender difference (H4). The founder-level congruence comparison (H2) is only '
    'directionally supported, and the two EI-moderation hypotheses (H3, H5) are not '
    'supported, although both interactions point in the predicted direction and are '
    'limited by the low power of interaction tests on between-subjects cells. Across '
    'the significant results, perceived success and pitch order are the two '
    'variables that most materially shape interpretation: success perception '
    'mediates the effects, and presentation order moderates them.')

OUT = os.path.join(HERE, '35_new_hypotheses_report.docx')
doc.save(OUT)
print('Saved', OUT)
