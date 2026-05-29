#!/usr/bin/env python3
"""Build a thorough, prose-based Word review of the entire analysis session.
Output: analysis/32_detailed_review.docx
"""
import os
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figures')

HERE = os.path.dirname(os.path.abspath(__file__))
doc = Document()
sec = doc.sections[0]
sec.top_margin = sec.bottom_margin = Inches(1.0)
sec.left_margin = sec.right_margin = Inches(1.1)
style = doc.styles['Normal']
style.font.name = 'Times New Roman'; style.font.size = Pt(12)
style.paragraph_format.space_after = Pt(6)

def body(t):
    p = doc.add_paragraph(); p.paragraph_format.line_spacing = 1.5
    p.add_run(t); return p

def H1(t): return doc.add_heading(t, level=1)
def H2(t): return doc.add_heading(t, level=2)

def figure(num, title, fname, note, width=5.8):
    cap = doc.add_paragraph(); cap.paragraph_format.space_before = Pt(8)
    r = cap.add_run(num); r.bold = True
    cap.add_run('  '); r = cap.add_run(title); r.italic = True
    img = doc.add_paragraph(); img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    img.add_run().add_picture(os.path.join(FIG, fname), width=Inches(width))
    np = doc.add_paragraph(); nr = np.add_run('Note. '); nr.italic = True
    np.add_run(note); np.paragraph_format.space_after = Pt(10)
    for r in np.runs: r.font.size = Pt(10)

def tbl(headers, rows, fs=10):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = 'Light List Accent 1'
    for i, h in enumerate(headers):
        r = t.rows[0].cells[i].paragraphs[0].add_run(h); r.bold = True; r.font.size = Pt(fs)
    for row in rows:
        c = t.add_row().cells
        for i, v in enumerate(row):
            c[i].text = v
            for p in c[i].paragraphs:
                for r in p.runs: r.font.size = Pt(fs)
    return t

# ─────────────────────────── Title ───────────────────────────
t = doc.add_heading('Comprehensive Analysis Review', level=0) if False else doc.add_heading(
    'Comprehensive Analysis Review: Emotional Intelligence and Gender-Role Congruity in Startup Funding', level=1)
body('Master Thesis — Arne Floh   |   Cleaned sample N = 187   |   Prepared May 2026')
body(
    'This document provides a detailed, narrative account of the complete analysis '
    'conducted for the thesis, from data preparation through hypothesis testing, '
    'the identification of three significant results, an extensive robustness '
    'battery, and a comparison with the literature review. It is written so that '
    'each step, each hypothesis, and each outcome is described in full sentences '
    'and can be read independently of the underlying code. All analysis scripts '
    'are committed to the branch claude/keen-tesla-1KzdH in the repository '
    'arnefloh-wu/Julia.')

# ─────────────────────────── 1 ───────────────────────────
H1('1. Background and Research Aim')
body(
    'The study investigates whether emotional intelligence (EI) shapes gender bias '
    'in startup investment decisions. The broader motivation, developed in the '
    'literature review, is that the persistent gender funding gap in '
    'entrepreneurship is driven less by the objective quality of female-led '
    'ventures than by investor biases, and specifically by emotional reactions to '
    'gender-role incongruity that evaluators misattribute to the qualities of the '
    'founder or venture. Building on the Stereotype Content Model and on '
    'role-congruity theory, the central proposition was that emotionally '
    'intelligent investors, being better able to recognise and discount '
    'stereotype-driven emotional reactions, should display less gender bias. The '
    'empirical question for this analysis was therefore twofold: first, whether '
    'gender bias appears in the investment data at all, and second, whether EI '
    '(total score and its four sub-dimensions) moderates that bias.')

# ─────────────────────────── 2 ───────────────────────────
H1('2. Study Design and Measures')
body(
    'The study employed a mixed experimental design. Founder gender was '
    'manipulated between subjects in three conditions: a male founding team, a '
    'female founding team, and a mixed team. Crucially, the two startups that each '
    'participant evaluated always shared the same founder-gender condition, so the '
    'design does not permit a within-person comparison of male- versus '
    'female-founded ventures. Industry was varied within subjects: every '
    'participant evaluated SiteVision, a construction-technology (ConTech) venture '
    'representing a male-typed industry, and BalanceUp, a corporate-wellness '
    'venture representing a female-typed industry. The order in which the two '
    'pitches were presented was counterbalanced (SiteVision first or BalanceUp '
    'first); this ordering variable later proved to be a critical moderator of the '
    'results.')
body(
    'Investment was measured as a budget-constrained allocation in which '
    'participants distributed a fixed endowment between investing in and saving '
    'from each startup, with investment in each venture ranging from 0 to 3. '
    'Emotional intelligence was measured with the 16-item Wong and Law Emotional '
    'Intelligence Scale (WLEIS) on a seven-point scale, yielding a total score and '
    'four sub-dimensions: self-emotion appraisal (SEA), others\' emotion appraisal '
    '(OEA), use of emotion (UOE), and regulation of emotion (ROE). The survey also '
    'recorded perceived probability of success for each startup (Q5 for SiteVision, '
    'Q47 for BalanceUp), perceived investment risk (three items each, Q6 and Q48), '
    'founder-team ratings on the Stereotype Content Model dimensions of competence '
    'and warmth (six items each, Q9 and Q49), dispositional risk tolerance using '
    'the Dohmen general and financial risk items (Q14 and Q15), and a full set of '
    'demographic and experience variables.')

# ─────────────────────────── 3 ───────────────────────────
H1('3. Data Preparation and Manipulation Checks')
body(
    'The raw Qualtrics export contained 230 recorded responses, with three header '
    'rows (variable names, item labels, and import-id metadata) followed by the '
    'actual data. Two manipulation checks were applied in sequence. The first '
    '(Q7) verified that participants could correctly recall the two startups\' '
    'industries, and the second (Q8) verified correct recall of the founding teams\' '
    'gender composition. Participants who answered incorrectly, and those who '
    'explicitly indicated that they could not remember, were excluded. Applying '
    'both checks strictly reduced the sample from 230 to 187 valid responses, which '
    'became the primary analysis dataset (MasterThesis_cleaned.csv). A more lenient '
    'variant that removed only the clear Q8 failures and retained the '
    '"don\'t remember" responses yielded 203 cases and was preserved separately '
    '(MasterThesis_mc-weak.csv) for possible sensitivity analyses. A small pilot '
    'wave of the first eight respondents, who shared an identical timestamp and '
    'were missing several later demographic items, was identified and, on the '
    'user\'s decision, retained in the final sample.')

# ─────────────────────────── 4 ───────────────────────────
H1('4. Sample Description')
body(
    'The final sample of 187 participants was slightly majority female: 100 '
    'participants (53.5%) identified as female, 84 (44.9%) as male, two as '
    'non-binary, and one preferred not to disclose. The mean age was approximately '
    '23.5 years, with most participants falling in the 20–24 bracket, reflecting a '
    'predominantly student sample. The sample was dominated by German and Austrian '
    'nationals, who together accounted for roughly two thirds of respondents, with '
    'the remainder spanning a range of mostly European nationalities. Most '
    'participants were enrolled at the Vienna University of Economics and Business, '
    'pursuing Bachelor\'s or Master\'s degrees, most commonly in Business '
    'Administration or Management. About 60% reported prior experience with '
    'financial investments, whereas only around 12% had founded or co-founded a '
    'company. These descriptive results, together with a gender bar chart in APA '
    'style and full demographic tables, were assembled into a Word draft of the '
    'sample-description section.')
H2('4.1  Emotional Intelligence by Participant Gender')
body(
    'Because EI is the central individual-difference variable, gender differences '
    'in the WLEIS were examined before the substantive hypotheses. Female '
    'participants reported significantly higher total emotional intelligence '
    '(M = 5.32, SD = 0.77) than male participants (M = 4.97, SD = 0.71), '
    'Welch t(182) = 3.19, p = .002, d = 0.47. This difference was concentrated in '
    'the two appraisal dimensions: self-emotion appraisal (M = 5.46 vs 4.83, '
    'p < .001, d = 0.59) and others\' emotion appraisal (M = 5.74 vs 5.05, '
    'p < .001, d = 0.66). The use-of-emotion and regulation-of-emotion dimensions '
    'showed no significant gender difference, with regulation being numerically, '
    'though not significantly, higher among men. The gender effect on total EI, '
    'SEA, and OEA remained essentially unchanged after controlling for age and for '
    'STEM versus non-STEM field of study, and the two gender groups were well '
    'matched on these covariates. This pattern is consistent with the wider EI '
    'literature, in which women score higher on perceiving and appraising emotions '
    'while regulation and instrumental use show small or null differences. It also '
    'carries a methodological implication: because EI is correlated with '
    'participant gender, any test of whether EI\'s moderating role differs between '
    'male and female participants necessarily operates on a restricted EI range '
    'within each gender and is correspondingly less sensitive.')
figure('Figure 1', 'Emotional Intelligence by Participant Gender',
       'fig22_ei_by_gender.png',
       'WLEIS means (±1 SE) for male and female participants. '
       '* p < .05, ** p < .01, *** p < .001; ns = not significant.')

# ─────────────────────────── 5 ───────────────────────────
H1('5. Hypothesis Tests')
body(
    'A series of hypotheses linking EI to investment behaviour was tested. Unless '
    'otherwise noted, every EI moderation analysis was run for the total WLEIS '
    'score and for each of the four sub-dimensions separately, and directional '
    'predictions were evaluated with both one- and two-tailed tests supplemented '
    'by non-parametric (Mann–Whitney) and bootstrap robustness checks. The results '
    'are described in turn.')

H2('5.1  H1 — Lower EI and Greater Investment in Male-Founded Startups')
body(
    'H1 predicted that participants with lower EI would invest more in male-founded '
    'startups. This hypothesis was not supported. Correlations between EI and '
    'investment within the male-founder condition were essentially zero for the '
    'total score and for every sub-dimension, with all p-values well above '
    'conventional thresholds. There was no evidence that lower-EI participants '
    'favoured male-founded ventures.')

H2('5.2  H2 — Higher EI and Greater Investment in Female-Founded Startups')
body(
    'H2 predicted the complementary effect, that participants with higher EI would '
    'invest more in female-founded startups. This was also not supported. Within '
    'the female-founder condition the EI–investment correlations were all small and '
    'non-significant (the largest being r = .12 for OEA, p = .40), and they were no '
    'larger than the corresponding correlations in the male-founder condition. '
    'Higher EI did not translate into greater generosity toward female founders.')

H2('5.3  H6 — Higher EI and More Equal Allocation Across Founder Genders')
body(
    'H6 proposed that higher-EI participants would allocate funding more equally '
    'across founder-gender conditions than lower-EI participants. Because founder '
    'gender is a between-subjects factor, this was operationalised as an EI × '
    'founder-gender interaction on total investment, and the analysis was repeated '
    'for pairwise comparisons among male, female, and mixed teams and for each EI '
    'dimension. No interaction reached significance in any specification. The '
    'omnibus three-level interaction was F = 0.35, p = .705. A bootstrap and '
    'Fisher-z power analysis indicated that this test was adequately powered to '
    'detect a moderate interaction at N = 187, so the null result is informative '
    'rather than merely underpowered. H6 was not supported.')

H2('5.4  H4 — Low-EI Preference for Masculine- over Feminine-Congruent Startups')
body(
    'H4 predicted that lower-EI participants would invest more in male-founded '
    'startups operating in male-dominated industries than in female-founded '
    'startups operating in female-dominated industries — that is, a preference for '
    'the masculine-congruent over the feminine-congruent venture. This hypothesis '
    'received partial, directional support. Among participants below the median on '
    'total EI, investment in the masculine-congruent startup (SiteVision evaluated '
    'in the male-founder condition) exceeded investment in the feminine-congruent '
    'startup (BalanceUp evaluated in the female-founder condition): M = 2.22 versus '
    '1.76, a one-tailed Welch test p = .032, Mann–Whitney p = .021, Cohen\'s '
    'd = 0.50. The two-tailed test was marginal (p = .064). However, the formal '
    'EI × congruity interaction on the full sample was non-significant '
    '(p = .294 in the two-way analysis), and the three-way EI × founder × industry '
    'interaction was non-significant for every EI dimension (smallest p = .48). The '
    'effect therefore exists as a simple comparison within the low-EI subgroup but '
    'not as a statistically significant moderation, and it later proved fragile '
    'under robustness testing.')

H2('5.5  H7 — Self-Emotion Appraisal as the Specific Driver')
body(
    'H7, derived from the most committed section of the literature review, proposed '
    'that any EI moderation of the congruity preference would be driven '
    'specifically by self-emotion appraisal (SEA), controlling for the other three '
    'dimensions. This was not supported, and indeed the data ran contrary to the '
    'prediction. In a model entering all four dimensions and their interactions '
    'with congruity simultaneously, the SEA × congruity interaction was b = +0.05, '
    'p = .77 — not only non-significant but wrong-signed relative to the '
    'hypothesis. No individual WLEIS dimension significantly moderated the '
    'congruity preference, whether tested jointly or in isolation. The moderation '
    'of the low-EI effect, to the extent that it exists, is diffuse across the '
    'total score and does not localise to SEA.')

H2('5.6  H8 — Stronger EI Moderation Among Male Participants')
body(
    'H8 proposed that EI\'s moderation of the gender-based investment gap would be '
    'stronger among male than female participants. This was not supported. The '
    'three-way EI × founder-gender × participant-gender interaction was b = +0.03, '
    'p = .97, and the EI × founder-gender slopes estimated separately within each '
    'participant-gender group were near-identical and both non-significant '
    '(male participants p = .86; female participants p = .79). This null is partly '
    'attributable to the fact, noted above, that there is no raw gender gap for EI '
    'to moderate, and partly to the restricted EI range within each gender.')

H2('5.7  H9 — Warmth Deficit as a Mediator Among Low-EI Participants')
body(
    'H9 proposed that female-founded startups would receive lower warmth ratings '
    'than male-founded startups and that this warmth deficit would mediate the '
    'investment gap among lower-EI participants. This hypothesis failed on both '
    'legs. First, there was no warmth deficit: female-founded teams were rated '
    'equal to, or slightly higher than, male-founded teams on the six-item warmth '
    'scale (M = 3.68 versus 3.59, p = .39), and the same held for competence '
    '(p = .48). Second, the mediation did not hold: within the low-EI subgroup the '
    'bootstrap indirect effect of founder gender on investment through warmth was '
    '−0.05, with a 95% confidence interval of [−0.15, +0.04] that comfortably '
    'included zero. The operative perceptual mechanism in the data was perceived '
    'probability of success, not warmth.')

# ─────────────────────────── 6 ───────────────────────────
H1('6. The Three Significant Results')
body(
    'Against this largely null backdrop, three results reached significance and '
    'were developed into the thesis storyline. They form a nested sequence that '
    'moves from the industry context, to a founder-by-industry congruity effect, '
    'to an individual-difference moderation by EI.')

H2('6.1  Result 1 — The Industry Effect (SiteVision > BalanceUp)')
body(
    'On a within-person basis, participants invested significantly more in '
    'SiteVision, the male-typed ConTech venture, than in BalanceUp, the '
    'female-typed wellness venture: paired t(186) = 5.08, p < .001, with a mean '
    'difference of +0.48 on the 0–3 scale. This was the strongest and most '
    'consistent effect in the study. It held across both experienced and '
    'inexperienced investors (both p ≤ .002) and showed no moderation by experience '
    '(interaction p = .851), establishing it as a stable, sample-wide preference '
    'for the male-typed venture and defining the gender-typing of the choice '
    'environment within which the founder-level effects operate.')

H2('6.2  Result 2 — The Gender-Role Congruity Effect (A versus B)')
body(
    'The second result compared the two off-diagonal cells of the founder-by-'
    'industry design. Cell A consisted of investment in SiteVision among '
    'participants in the female-founder condition (a female founder in a male-typed '
    'industry), and Cell B consisted of investment in BalanceUp among participants '
    'in the male-founder condition (a male founder in a female-typed industry). '
    'Cell A received significantly more funding than Cell B: M = 2.22 versus 1.68, '
    'Welch t(115) = 3.34, p = .001, Cohen\'s d = 0.62 — a medium-to-large effect '
    'and one of the strongest in the dataset. It is important to be precise about '
    'the interpretation. The originally framed hypothesis had been that female '
    'founders in male-typed industries would be penalised relative to male founders '
    'in female-typed industries; the data reversed this, because the male-typed '
    'industry (SiteVision) is the generally more-funded venture. The significant '
    'result therefore reflects a congruity or, more precisely, an industry-driven '
    'advantage rather than a penalty against incongruent female founders. '
    'Consistent with this, female-founded SiteVision ventures were rated as '
    'significantly more likely to succeed than male-founded BalanceUp ventures '
    '(M = 5.07 versus 4.34, p = .002), pointing to perceived viability as the '
    'proximal driver. A complementary within-industry analysis confirmed that there '
    'was no female penalty inside either industry once the venture itself was held '
    'constant.')
figure('Figure 2', 'Investment by Founder Gender and Industry Typing',
       'fig16_incongruent_penalty.png',
       'Mean amount invested (±1 SE). Cell A = female founders in the male-typed '
       'industry (SiteVision); Cell B = male founders in the female-typed industry '
       '(BalanceUp).')

H2('6.3  Result 3 — The Low-EI Masculine-Congruent Preference')
body(
    'The third result is the EI-relevant one. Among participants below the median '
    'on total WLEIS, investment in the masculine-congruent startup (a male founder '
    'in the male-typed SiteVision) exceeded investment in the feminine-congruent '
    'startup (a female founder in the female-typed BalanceUp): M = 2.22 versus '
    '1.76, one-tailed Welch p = .032, Mann–Whitney p = .021, d = 0.50. The same '
    'low-EI participants rated the masculine-congruent venture as both more likely '
    'to succeed (p = .008) and somewhat riskier (p = .045), a profile consistent '
    'with stereotype-consistent, heuristic processing that is not corrected by '
    'emotional self-regulation. This result is the empirical anchor for the thesis\'s '
    'claim that EI conditions the expression of gender-congruity bias, although, as '
    'set out below, it is statistically the most fragile of the three.')
figure('Figure 3', 'Low-EI Participants: Masculine- versus Feminine-Congruent Investment',
       'fig14_lowEI_congruence.png',
       'Mean amount invested (±1 SE) among participants below the median on total '
       'WLEIS. The bracket reports the one-tailed test.', width=4.8)

H2('6.4  The Absence of a Raw Gender Funding Gap')
body(
    'An important clarifying analysis showed that, when founder gender was '
    'collapsed into a simple male-versus-female between-subjects comparison, there '
    'was no funding gap and the direction was if anything reversed: per-startup '
    'investment averaged 1.90 in the male-founder condition and 2.04 in the '
    'female-founder condition, Welch t = −1.14, p = .257. EI did not moderate this '
    'non-existent gap, with an omnibus EI × founder-gender interaction of '
    'F = 0.35, p = .705. The substantive implication is that the gender effect in '
    'these data is not a main effect but an interaction: it appears only in the '
    'founder-by-industry congruity cells, which is precisely where Results 2 and 3 '
    'locate it. This reframing — congruity rather than a simple gap — is central to '
    'interpreting the study honestly.')

# ─────────────────────────── 7 ───────────────────────────
H1('7. Robustness Battery')
body(
    'The three significant results were subjected to an extensive robustness '
    'battery, comprising adjustment for perceptual and dispositional covariates, a '
    'formal treatment of presentation order, an attention filter, and re-estimation '
    'within experience-based subgroups. The findings are summarised in the table '
    'and then discussed.')
tbl(['Robustness lever', 'R1 Industry', 'R2 Congruity', 'R3 Low-EI'],
    [['Baseline', '+0.48, p < .001', '+0.54, p = .001', '+0.46, p₁ = .032'],
     ['+ Expected success (Q5/Q47)', 'p = .059', 'p = .091', 'p = .68'],
     ['+ Startup risk (Q6/Q48)', 'p < .001', 'p = .002', 'p = .092'],
     ['+ Competence (Q9/Q49)', 'p < .001', 'p = .004', 'p = .28'],
     ['+ Risk trait (Q14/Q15)', 'not moderated', 'p = .007', 'p = .038'],
     ['+ All covariates', 'p = .032', 'p = .106', 'p = .75'],
     ['SiteVision shown first', '+1.08, p < .001', 't = 5.89, p < .001', 't = 4.79, p < .001'],
     ['BalanceUp shown first', '−0.15, p = .24', 't = −0.85, p = .40', 't = −1.21, p = .88'],
     ['Effect × order interaction', 'b = 1.24, p < .001', 'b = 1.40, p < .001', 'b = 1.62, p < .001'],
     ['Attention filter (drop 5%)', 'p < .001', 'p = .001', 'p₁ = .052'],
     ['Investment experience', 'both groups hold', 'inexperienced only', 'inexperienced only (.016)'],
     ['Never-founded subgroup', 'p < .001', 'p < .001', 'p₁ = .059'],
     ['Bottom-tertile EI definition', '—', '—', 'p₁ = .050'],
     ['EI-dimension specificity', '—', '—', 'all ns; SEA p = .77']],
    fs=9)

H2('7.1  Adjustment for Perceived Success, Risk, Competence, and Risk Trait')
body(
    'The single most consequential covariate was perceived probability of success. '
    'Entering it reduced all three effects substantially: the industry effect fell '
    'to p = .059, the congruity effect to p = .091, and the low-EI effect to '
    'p = .68. The within-person investment gap correlated r = .75 with the '
    'corresponding difference in perceived success, indicating that the effects '
    'operate largely through perceived venture viability rather than through '
    'founder gender directly. By contrast, perceived startup risk and founder '
    'competence did not account for the industry and congruity effects, which '
    'remained significant at p < .005 after adjusting for each; only the fragile '
    'low-EI effect was absorbed by these covariates. Dispositional risk tolerance '
    '(the Dohmen general and financial items) did not threaten any result; if '
    'anything the congruity and low-EI effects strengthened when risk traits alone '
    'were controlled (p = .007 and p = .038 respectively).')
figure('Figure 4', 'Adjusted Effect Coefficients Across Robustness Specifications',
       'fig21_robustness_coefficients.png',
       'Effect coefficient (0–3 scale) for each result under successive covariate '
       'adjustments. * p < .05. Note how adding perceived success collapses all '
       'three effects.')
figure('Figure 5', 'Perceived-Success Mechanism',
       'fig23_success_mechanism.png',
       'Within-person investment gap (SiteVision − BalanceUp) plotted against the '
       'perceived-success gap, with linear fit. Points jittered for legibility.',
       width=5.2)

H2('7.2  Sensitivity to Presentation Order')
body(
    'The most important robustness finding concerns pitch presentation order. '
    'Because order was counterbalanced and approximately balanced across '
    'conditions, including it as a covariate left the average effect estimates '
    'essentially unchanged (the industry coefficient remained 0.48, p < .001; the '
    'congruity coefficient 0.54, p = .001; the low-EI coefficient 0.46, but now '
    'p = .069). However, the effect-by-order interaction was large and highly '
    'significant for all three results. Each effect was very large when SiteVision '
    'was presented first and disappeared, or numerically reversed, when BalanceUp '
    'was presented first: the industry preference was +1.08 (p < .001) versus '
    '−0.15 (p = .24); the congruity comparison was t = 5.89 (p < .001) versus '
    't = −0.85 (p = .40); and the low-EI comparison was t = 4.79 (p < .001) versus '
    't = −1.21 (p = .88). This pattern is consistent with a primacy or anchoring '
    'contribution, whereby participants allocated more to whichever pitch they saw '
    'first; because SiteVision is the masculine-typed venture, such an order effect '
    'mechanically resembles an industry or congruity effect. Two implications '
    'follow. The average effects are not the product of a simple confound, since '
    'order was balanced across conditions; but their generalisability is limited, '
    'because they are not stable across presentation orders. This order dependence '
    'should be disclosed transparently as a boundary condition.')
figure('Figure 6', 'Effect Size by Pitch Presentation Order',
       'fig20_pitch_order_interaction.png',
       'Mean investment difference (0–3 scale) underlying each result, split by '
       'whether SiteVision or BalanceUp was presented first. All three effects are '
       'present only when SiteVision is shown first.')

H2('7.3  Attention Filter and Subgroup Stability')
body(
    'Excluding the fastest five percent of respondents as a careless-responding '
    'filter left the industry and congruity effects unchanged (p < .001 and '
    'p = .001), while the low-EI effect slipped to borderline significance '
    '(one-tailed p = .052). The low-EI effect was likewise borderline under a '
    'bottom-tertile definition of low EI (p = .050) and within the never-founded '
    'subgroup (p = .059), and it reached significance only among inexperienced '
    'investors (p = .016). The industry and congruity effects, in contrast, held '
    'firmly across investment- and entrepreneurial-experience subgroups.')

H2('7.4  Overall Robustness Assessment')
body(
    'Taken together, the robustness battery supports three conclusions. First, '
    'perceived probability of success is the proximal covariate that accounts for '
    'all three effects, reinforcing a viability-based rather than warmth-based '
    'mechanism and aligning with the failure of the warmth-mediation hypothesis '
    '(H9). Second, the industry effect (R1) and the congruity effect (R2) are '
    'robust to adjustment for risk, competence, and risk traits, to attention '
    'filtering, and to subgroup variation, and are threatened only by the success '
    'covariate (which mediates them) and by presentation order (which moderates '
    'them). Third, the low-EI congruence effect (R3) is fragile, falling to '
    'borderline or non-significant under almost every check, and should therefore '
    'be reported as suggestive rather than confirmatory.')

# ─────────────────────────── 8 ───────────────────────────
H1('8. Comparison with the Literature Review')
body(
    'The results were compared against the thesis literature review. The review is '
    'largely structured to predict effects that the data did not produce, so the '
    'comparison identifies both points of agreement and several points requiring '
    'revision.')
H2('8.1  Points of Agreement')
body(
    'The data confirm the review\'s emphasis on industry gender-typing as a key '
    'boundary condition: SiteVision, the male-typed venture, was systematically '
    'favoured (Result 1). They also confirm the proposition, associated with '
    'Tonoyan and Strohmeyer, that female founders are not penalised in female-typed '
    'or gender-neutral industries — indeed, there was no raw funding gap at all and '
    'female-founded ventures were rated slightly higher. Finally, the prominence of '
    'perceived success and risk in the robustness analyses is broadly consistent '
    'with the review\'s treatment of EI, risk perception, and the affective shaping '
    'of financial judgment.')
H2('8.2  Points of Contradiction and Required Revisions')
body(
    'Four tensions require attention in the review. First, the review opens by '
    'asserting a robust gender funding gap, whereas the experiment found none as a '
    'main effect; the review should add a paragraph conceding that experimental '
    'evidence is mixed and that the gap is conditional on industry congruity. '
    'Second, the review builds its Stereotype-Content-Model argument and the H9 '
    'mediation on the premise that female founders elicit a warmth deficit, but the '
    'data show no such deficit and no warmth-based mediation; this section should '
    'be reframed toward competence and perceived viability, and warmth mediation '
    'marked as exploratory. Third, the extended subsection arguing that '
    'self-emotion appraisal is the specific mechanism is contradicted by the null, '
    'wrong-signed SEA result, and should be softened from a claim to a candidate '
    'hypothesis, supported by recent work noting that dimension-specific EI effects '
    'on decision-making are weak and inconsistent. Fourth, the review presents the '
    'stereotype that women are more emotional and less able to regulate emotion, '
    'yet in this sample women scored higher on measured emotional intelligence, '
    'particularly on the appraisal dimensions — an ironic empirical counterpoint '
    'worth noting in the discussion.')
H2('8.3  Literature to Add')
body(
    'Several papers should be incorporated. On the contradicting and nuancing side, '
    'the Science Advances (2020) study on the penalty for lack of industry fit '
    'provides the cleanest prior congruity result and should be engaged directly, '
    'since the present data show the industry effect but not the female-specific '
    'fit penalty; the crowdfunding warmth-and-competence literature, including '
    'Svetek (2023), shows that competence rather than warmth drives women\'s '
    'funding success and that female-led campaigns can raise comparable total '
    'amounts; and a 2024 review of ability emotional intelligence documents the '
    'weakness of dimension-specific EI effects. On the confirming side, Tonoyan and '
    'Strohmeyer (2021) should be drawn on more heavily, and the EI–risk-perception '
    'mediation literature can be used to connect the success and risk findings to '
    'the EI framework.')

# ─────────────────────────── 9 ───────────────────────────
H1('9. Summary of Hypotheses and Outcomes')
tbl(['Hypothesis', 'Prediction', 'Outcome'],
    [['H1', 'Lower EI → more investment in male-founded startups', 'Not supported (all r ≈ 0)'],
     ['H2', 'Higher EI → more investment in female-founded startups', 'Not supported (all ns)'],
     ['H4', 'Low-EI prefer masculine- over feminine-congruent', 'Partial / directional (p₁ = .032); fragile'],
     ['H6', 'Higher EI → more equal allocation across genders', 'Not supported (omnibus p = .705)'],
     ['H7', 'EI moderation driven specifically by SEA', 'Not supported (SEA p = .77, wrong sign)'],
     ['H8', 'EI moderation stronger for male participants', 'Not supported (three-way p = .97)'],
     ['H9', 'Warmth deficit mediates gap among low-EI', 'Not supported (no deficit; indirect CI incl. 0)'],
     ['R1', 'Industry effect: SiteVision > BalanceUp', 'Supported, robust (p < .001)'],
     ['R2', 'Congruity advantage: A > B', 'Supported, robust (p = .001, d = .62)'],
     ['R3', 'Low-EI masculine-congruent preference', 'Supported but fragile (p₁ = .032)']],
    fs=10)

H1('10. Overall Conclusion')
body(
    'The analysis does not support a simple account in which emotional intelligence '
    'reduces a gender funding gap, principally because no raw gender funding gap '
    'was present to be reduced. What the data do show is, first, a strong and '
    'robust preference for the male-typed industry; second, a medium-to-large '
    'congruity advantage that is driven by that industry\'s perceived viability '
    'rather than by a penalty against female founders; and third, a suggestive but '
    'fragile tendency for lower-EI participants to favour the masculine-congruent '
    'venture. Across all three results the unifying mechanism is perceived '
    'probability of success, and the most serious threat to inference is the '
    'dependence of the effects on pitch presentation order. The honest narrative '
    'for the thesis is therefore one of a congruity-and-viability effect, '
    'conditioned weakly by emotional intelligence and bounded by an order '
    'sensitivity that must be reported, rather than a clean demonstration of EI as '
    'a debiasing resource.')

# ─────────────────────────── 11 ───────────────────────────
H1('11. Integrating the Literature Review with the Findings')
body(
    'This closing chapter draws the theoretical framework of the literature review '
    'and the empirical findings into a single, coherent account. The aim is to show '
    'where the data substantiate the theory, where they redirect it, and how the '
    'overall argument of the thesis should be positioned in light of both.')

H2('11.1  From the Gender Funding Gap to Industry Congruity')
body(
    'The literature review opens from the premise of a systematic gender funding '
    'gap, attributing it to investor biases rather than to differences in venture '
    'quality. The present data refine this starting point rather than confirm it. '
    'No gap emerged when founder gender was considered in isolation; instead, the '
    'organising variable was the gender-typing of the industry, with the male-typed '
    'venture systematically favoured (Result 1) and the congruity advantage '
    'following from it (Result 2). This is precisely the boundary condition the '
    'review attributes to Tonoyan and Strohmeyer (2021) and to the lack-of-fit and '
    'role-congruity traditions: bias is not a uniform main effect but is '
    'concentrated where the gender-typing of the role or industry is salient. The '
    'thesis can therefore retain the review\'s theoretical scaffolding while '
    'reframing its empirical claim from "a gender funding gap" to "a gender-by-'
    'industry congruity effect."')

H2('11.2  Stereotype Content, Warmth, and the Shift to Perceived Viability')
body(
    'The review develops the Stereotype Content Model and the BIAS-map argument of '
    'Cuddy, Fiske and Glick (2007), proposing that female founders elicit a warmth '
    'deficit and that warmth-linked emotions mediate discriminatory behaviour; this '
    'is the theoretical engine behind H9. The data do not bear this out: female-'
    'founded teams were rated no lower on warmth, and warmth did not mediate '
    'investment. What did consistently account for the effects was perceived '
    'probability of success, which correlated strongly with the investment gap and '
    'attenuated every result when controlled. Read through the Stereotype Content '
    'Model, this points away from the warmth dimension and toward the competence '
    'dimension and its behavioural correlate of perceived viability. The review can '
    'preserve the SCM framing but should pivot its emphasis from warmth-based '
    'antipathy to competence- and viability-based judgment, treating warmth '
    'mediation as an exploratory rather than central claim.')

H2('11.3  Emotional Intelligence as a Conditional, Diffuse Moderator')
body(
    'The review\'s central contribution is the proposition that emotional '
    'intelligence acts as a debiasing mechanism, with a specific theoretical bet on '
    'self-emotion appraisal as the operative dimension, grounded in Yip and Cote '
    '(2013) and the appraisal-misattribution account. The findings offer only '
    'qualified support. Emotional intelligence did not moderate a gender funding '
    'gap, because there was none to moderate, and it did not operate through '
    'self-emotion appraisal: the SEA interaction was null and wrong-signed, and no '
    'single WLEIS dimension carried the effect. The one EI-linked result — the '
    'tendency of lower-EI participants to favour the masculine-congruent venture '
    '(Result 3) — was diffuse across the total score and statistically fragile. The '
    'review should therefore present emotional intelligence as a conditional and '
    'diffuse moderator of congruity-based judgment rather than as a dimension-'
    'specific debiasing mechanism, and should soften the self-emotion-appraisal '
    'subsection from a claim to a candidate hypothesis.')

H2('11.4  Risk, Emotion, and the Role of Perceived Success')
body(
    'The review devotes substantial attention to risk perception and to the '
    'affective shaping of financial judgment, citing Dohmen et al. (2011) on '
    'dispositional risk and Lerner and Keltner and Yip and Cote on emotion and '
    'risk. The data align with this literature in an instructive way. Dispositional '
    'risk tolerance, measured with the Dohmen items, did not confound any result, '
    'and perceived startup risk played only a secondary role. The dominant '
    'affective-cognitive variable was instead perceived success, which behaved as '
    'the proximal driver of allocation. This positions perceived viability, rather '
    'than risk per se, as the channel through which gender-typed expectations '
    'translate into investment — a refinement the review can incorporate by '
    'connecting its risk-perception section to a success- or viability-perception '
    'mechanism.')

H2('11.5  A Coherent Narrative for the Thesis')
body(
    'Brought together, the literature review and the findings support a single, '
    'defensible narrative. Gender bias in startup funding, in this sample, is not a '
    'blunt gap against female founders but a congruity effect organised around '
    'industry gender-typing, expressed primarily through perceptions of venture '
    'viability, weakly and diffusely conditioned by emotional intelligence, and '
    'bounded by a sensitivity to presentation order that limits generalisability. '
    'This narrative keeps the review\'s theoretical foundations — role congruity, '
    'the Stereotype Content Model, and emotional intelligence as an individual-'
    'difference moderator — while honestly redirecting each in light of the '
    'evidence: from gap to congruity, from warmth to viability, and from a '
    'SEA-specific mechanism to a conditional, diffuse one. Presented this way, the '
    'thesis contributes a nuanced, empirically grounded qualification of the '
    'investor-bias literature rather than a simple confirmation of it.')

OUT = os.path.join(HERE, '32_detailed_review.docx')
doc.save(OUT)
print('Saved', OUT)
