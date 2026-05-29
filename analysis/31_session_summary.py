#!/usr/bin/env python3
"""Build a detailed Word summary of the full analysis session.
Output: analysis/31_session_summary.docx
"""
import os
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH

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

def bl(t, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.line_spacing = 1.3
    if bold_prefix:
        r = p.add_run(bold_prefix); r.bold = True
        p.add_run(t)
    else:
        p.add_run(t)
    return p

def h2(t): return doc.add_heading(t, level=2)
def h3(t): return doc.add_heading(t, level=3)

def tbl(headers, rows, font_size=10):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = 'Light List Accent 1'
    for i, h in enumerate(headers):
        run = t.rows[0].cells[i].paragraphs[0].add_run(h)
        run.bold = True; run.font.size = Pt(font_size)
    for row in rows:
        c = t.add_row().cells
        for i, v in enumerate(row):
            c[i].text = v
            for p in c[i].paragraphs:
                for r in p.runs: r.font.size = Pt(font_size)
    return t

# ── Title ──
title = doc.add_heading('Session Summary: EI and Gender-Role Congruity in Startup Funding', level=1)
body('Master Thesis Analysis — Arne Floh  |  Data: N = 187  |  May 2026')
body(
    'This document summarises the full analysis session conducted in Claude Code, '
    'covering data preparation, hypothesis testing, robustness checks, and '
    'the resulting theoretical storyline for the master thesis. All scripts are '
    'committed to the branch claude/keen-tesla-1KzdH in the repository arnefloh-wu/Julia.'
)

# ══════════════════════════════════════════════════════
doc.add_heading('1. Data Preparation', level=1)
# ══════════════════════════════════════════════════════
h2('1.1  Raw Data and Cleaning')
body(
    'The study used a Qualtrics survey with 230 recorded responses. Two '
    'manipulation checks were applied sequentially. Q7 verified correct recall of '
    'the two startups\' industries (ConTech / Wellness); Q8 verified correct recall '
    'of the founding team\'s gender composition. Participants who selected '
    '"don\'t remember" or gave the wrong answer were excluded. Applying both checks '
    'strictly reduced the sample to N = 187 (strict-clean version saved as '
    'MasterThesis_cleaned.csv). A weaker variant retaining only Q7 failures '
    '(N = 203) was saved separately as MasterThesis_mc-weak.csv for future '
    'sensitivity checks.'
)
h2('1.2  Design')
body(
    'The study used a 3 (founder gender: male / female / mixed) × 2 (industry: '
    'SiteVision ConTech = male-typed / BalanceUp Wellness = female-typed) mixed '
    'design. Founder gender was a between-subjects factor: each participant '
    'evaluated two startups sharing the same founder gender condition. Industry '
    'was a within-subjects factor. Participants also saw the pitches in one of two '
    'orders (SiteVision first or BalanceUp first), which later proved to be a '
    'critical moderator. Investment was operationalised as a budget-constrained '
    'allocation (invest + save = 3 per startup, scale 0–3).'
)
h2('1.3  Key Variables')
tbl(['Variable', 'Description', 'Column(s)'],
    [['invest_sv', 'Investment in SiteVision (0–3)', 'invest_sv'],
     ['invest_bu', 'Investment in BalanceUp (0–3)', 'invest_bu'],
     ['team_gender', 'Founder gender condition (male/female/mixed)', 'team_gender'],
     ['Total EI', 'WLEIS total score (mean of 16 items, 7-pt)', 'Q10–Q13'],
     ['SEA', 'Self-emotion appraisal (4 items)', 'Q10 (SEA)'],
     ['OEA', 'Others\' emotion appraisal (4 items)', 'Q11 (OEA)'],
     ['UOE', 'Use of emotion (4 items)', 'Q12 (UOE)'],
     ['ROE', 'Regulation of emotion (4 items)', 'Q13 (ROE)'],
     ['Expected success', 'Perceived success probability, 7-pt', 'Q5 (SV), Q47 (BU)'],
     ['Startup risk', 'Perceived investment risk, 3 items, 7-pt', 'Q6_1-3 (SV), Q48_1-3 (BU)'],
     ['Warmth/Competence', 'SCM ratings, 6 items each, 7-pt', 'Q9_7-12 / Q49_7-12'],
     ['Risk trait', 'Dohmen general + financial risk, 1-10', 'Q14, Q15'],
     ['Investment exp.', 'Prior investment experience (Yes/No)', 'Q23'],
     ['Pitch order', 'SiteVision first vs BalanceUp first', 'pitch_order']])

# ══════════════════════════════════════════════════════
doc.add_heading('2. Sample Description', level=1)
# ══════════════════════════════════════════════════════
body(
    'The final sample comprised N = 187 participants (strict manipulation-check '
    'exclusion). Female participants made up the majority (n = 100, 53.5%), '
    'followed by male (n = 84, 44.9%), non-binary (n = 2), and prefer-not-to-say '
    '(n = 1). Mean age was 23.5 years (SD = 3.6, range 19–57). The sample was '
    'predominantly German (≈ 37%) and Austrian (≈ 30%), with the remainder '
    'spanning a range of European nationalities. Most participants were students at '
    'the Vienna University of Economics and Business (WU), pursuing Bachelor\'s '
    '(48.4%) or Master\'s (31.7%) degrees in Business Administration or related '
    'fields. Investment experience was reported by 60.4% of participants; only '
    '11.8% had prior entrepreneurial experience.'
)
h2('EI by Participant Gender')
body(
    'Female participants scored significantly higher on total EI (M = 5.32, '
    'SD = 0.77) than male participants (M = 4.97, SD = 0.71), Welch t(182) = 3.19, '
    'p = .002, d = 0.47. The difference was driven by the two appraisal dimensions: '
    'SEA (d = 0.59, p < .001) and OEA (d = 0.66, p < .001). The use-of-emotion '
    '(UOE) and regulation-of-emotion (ROE) dimensions showed no significant gender '
    'difference. The EI–gender correlation was robust to age and STEM-field controls. '
    'Because EI is correlated with participant gender, tests of EI moderation '
    'conditioned on participant gender (H8) operate on a restricted EI range and '
    'are less sensitive.'
)

# ══════════════════════════════════════════════════════
doc.add_heading('3. Hypothesis Tests', level=1)
# ══════════════════════════════════════════════════════
body('All EI moderation tests were run for total WLEIS and each of the four '
     'dimensions (SEA, OEA, UOE, ROE) separately.')

h2('H1 – EI and Male-Founded Investment (lower EI → more in male-founded)')
body('Not supported. Correlation between EI and investment in male-founded startups '
     'was near zero for all dimensions (all p > .30). No within-condition or '
     'between-condition EI effect on raw founder-gender investment was found.')

h2('H2 – EI and Female-Founded Investment (higher EI → more in female-founded)')
body('Not supported. Correlations within the female-founded condition were all ns '
     '(largest r = .12, OEA, p = .40). EI does not predict generosity toward '
     'female founders.')

h2('H4 – Low-EI Preference for Male-Founded in Male-Typed Industry')
body('Partially supported. Low-EI participants (below median) showed a suggestive '
     'preference for the masculine-congruent startup over the feminine-congruent '
     'one (one-tailed p = .032, Mann–Whitney p = .021, d = 0.50). The two-way '
     'EI × congruity interaction on the full sample was ns (p = .294), '
     'and the three-way EI × founder × industry interaction was ns across all '
     'EI dimensions (smallest p = .48). This result is sensitive to robustness '
     'checks (see section 5).')

h2('H6 – Higher EI → More Equal Allocation Across Founder Genders')
body('Not supported. The EI × founder-gender interaction on total investment was '
     'ns for all dimensions and all pairwise gender comparisons (male/female, '
     'male/mixed, female/mixed). The omnibus three-level interaction was F = 0.35, '
     'p = .705.')

h2('H7 – EI Moderation Driven Specifically by SEA')
body('Not supported. In the full model with all four EI dimensions entered '
     'simultaneously, the SEA × congruity interaction was b = +0.05, p = .77 — '
     'wrong-signed relative to the hypothesis. No dimension significantly moderated '
     'the congruity preference.')

h2('H8 – EI Moderation Stronger for Male Participants')
body('Not supported. The three-way EI × founder-gender × participant-gender '
     'interaction was b = +0.03, p = .97. Within-gender slopes were near-identical '
     'for male (p = .86) and female participants (p = .79).')

h2('H9 – Warmth Deficit Mediates Investment Gap Among Low-EI Participants')
body('Not supported on both legs. Female-founded teams were rated equal-to-slightly '
     'higher on warmth (M = 3.68 vs 3.63, p = .39). The bootstrap indirect effect '
     'a × b = −0.05, 95% CI [−0.15, +0.04], included zero. The operative '
     'mediator was perceived success, not warmth.')

# ══════════════════════════════════════════════════════
doc.add_heading('4. The Storyline: Three Significant Results', level=1)
# ══════════════════════════════════════════════════════
body('Three results reached significance and form the core of the thesis narrative, '
     'organised as a nested sequence from industry context to congruity to '
     'individual-difference moderation.')

h2('R1 — Industry Effect: SiteVision > BalanceUp')
body('Participants invested significantly more in SiteVision (male-typed ConTech) '
     'than BalanceUp (female-typed Wellness) on a within-person basis: '
     'paired t(186) = 5.08, p < .001, mean difference = +0.48. The effect held '
     'across both experienced and inexperienced investors (both p ≤ .002) with no '
     'experience moderation (p = .851). This establishes the industry gender-typing '
     'of the choice environment.')

h2('R2 — Gender-Role Congruity: A > B (p = .001, d = 0.62)')
body('Comparing Cell A (female founder / male-typed industry = SiteVision) with '
     'Cell B (male founder / female-typed industry = BalanceUp): A received '
     'significantly more funding (M = 2.22 vs 1.68, Welch t(115) = 3.34, p = .001, '
     'd = 0.62). This is interpreted as a congruity advantage: the gender-typed '
     'industry is favoured regardless of whether the founder matches it. Notably, '
     'female-founded ventures were rated as significantly more likely to succeed '
     'in this context (M = 5.07 vs 4.34, p = .002), suggesting the investment '
     'difference is mediated by perceived viability rather than founder gender '
     'directly.')

h2('R3 — Low-EI Masculine-Congruent Preference (one-tailed p = .032)')
body('Among participants below the median on total WLEIS, investment in the '
     'masculine-congruent startup (SiteVision / male founder) exceeded investment '
     'in the feminine-congruent startup (BalanceUp / female founder): '
     'M = 2.22 vs 1.76, one-tailed Welch t, p = .032; Mann–Whitney p = .021; '
     'd = 0.50. The same low-EI participants rated the masculine-congruent startup '
     'as more likely to succeed (p = .008) and riskier (p = .045), consistent '
     'with stereotype-driven heuristic processing.')

h2('Additional Finding: No Raw Gender Funding Gap')
body('When founder gender was collapsed to a simple male-vs-female between-subjects '
     'comparison, the gap was non-significant and directionally reversed: '
     'male-founded M = 1.90, female-founded M = 2.04, Welch t = −1.14, p = .257. '
     'EI did not moderate this non-existent gap (omnibus p = .705). The gender '
     'effect in the data is an interaction, not a main effect — it surfaces only '
     'in the founder × industry congruity cells.')

# ══════════════════════════════════════════════════════
doc.add_heading('5. Robustness Battery', level=1)
# ══════════════════════════════════════════════════════
body('✓ = holds, ↓ = attenuated/borderline, ✗ = absorbed')
tbl(['Lever', 'R1 Industry', 'R2 Congruity', 'R3 Low-EI'],
    [['Baseline', 'p < .001 ✓', 'p = .001 ✓', 'p₁ = .032 ✓'],
     ['+ Expected success', 'p = .059 ↓', 'p = .091 ↓', 'p = .68 ✗'],
     ['+ Startup risk', 'p < .001 ✓', 'p = .002 ✓', 'p = .092 ↓'],
     ['+ Competence ratings', 'p < .001 ✓', 'p = .004 ✓', 'p = .28 ✗'],
     ['+ Risk trait (Q14/Q15)', 'not moderated ✓', 'p = .007 ✓', 'p = .038 ✓'],
     ['+ All covariates', 'p = .032 ✓', 'p = .106 ↓', 'p = .75 ✗'],
     ['SiteVision shown first', '+1.08, p < .001', 't = 5.89, p < .001', 't = 4.79, p < .001'],
     ['BalanceUp shown first', '−0.15, p = .24 ✗', 't = −0.85, p = .40 ✗', 't = −1.21, p = .88 ✗'],
     ['Effect × order interaction', 'b = 1.24, p < .001', 'b = 1.40, p < .001', 'b = 1.62, p < .001'],
     ['Attention filter (drop 5%)', 'p < .001 ✓', 'p = .001 ✓', 'p₁ = .052 ↓'],
     ['Investment experience', 'both groups ✓', 'only inexperienced ✓', 'only inexperienced ✓'],
     ['Never-founded subgroup', 'p < .001 ✓', 'p < .001 ✓', 'p₁ = .059 ↓'],
     ['Bottom-tertile EI def.', '—', '—', 'p₁ = .050 ↓'],
     ['EI-dimension specificity', '—', '—', 'all ns; SEA p = .77 ✗']],
    font_size=9)

h2('Robustness Conclusions')
bl('Perceived success is the dominant covariate: it attenuates or absorbs all '
   'three effects (r = .75 with investment gap). Effects operate through '
   'perceived venture viability, not founder gender directly.', '')
bl('Pitch order strongly moderates all three results: large effects when SiteVision '
   'is shown first, absent/reversed when BalanceUp is first. Average estimates '
   'are unconfounded (order was balanced) but generalizability is limited — '
   'report as a boundary condition.', '')
bl('R1 and R2 are robust to risk, competence, risk-trait controls, attention '
   'filtering, and experience subgroups. R3 is fragile under nearly every check '
   'and should be presented as suggestive.', '')
bl('EI-dimension specificity (H7) is null. No single WLEIS facet drives R3.', '')

# ══════════════════════════════════════════════════════
doc.add_heading('6. Literature Review Comparison', level=1)
# ══════════════════════════════════════════════════════
h2('Confirmations')
bl('Industry gender-typing as a key boundary condition (Sperber & Linder; Tonoyan & Strohmeyer) — confirmed by R1.')
bl('No female penalty in female-typed industries (Tonoyan & Strohmeyer 2021) — confirmed: no raw gap (p = .257).')
bl('EI linked to risk perception and financial decision-making quality (Yip & Cote; Bucciol) — consistent with success-perception mechanism.')

h2('Contradictions (additions needed in review)')
bl('Gender funding gap as a main effect — contradicted. The gap is a congruity '
   'interaction, not a universal main effect. Add boundary-condition paragraph.')
bl('Warmth-deficit premise (SCM → H9) — contradicted. Female founders rated '
   'equal/higher warmth; warmth did not mediate investment. Reframe SCM section '
   'toward competence/viability; demote H9 to exploratory.')
bl('SEA as the specific mechanism — contradicted. The SEA subsection overcommits; '
   'soften to "candidate mechanism" and cite 2024 ability-EI inconsistency literature.')
bl('"Women more emotional" stereotype — counterpoint: women scored higher on '
   'EI (d up to 0.66 for OEA). Worth noting in the discussion.')

h2('Papers to Add')
bl('Science Advances (2020) — female penalty for lack of industry fit (no male penalty). '
   'https://www.science.org/doi/10.1126/sciadv.abd7664')
bl('Svetek (2023) — competence not warmth drives women\'s early-stage funding success. '
   'https://journals.sagepub.com/doi/10.1177/10422587221127000')
bl('Warmth/competence in crowdfunding (2022) — comparable total funding, competence pathway. '
   'https://www.sciencedirect.com/science/article/abs/pii/S2352673421000664')
bl('Ability-EI decision-making review (2024) — dimension-specific effects weak/inconsistent. '
   'https://pmc.ncbi.nlm.nih.gov/articles/PMC12070655/')

# ══════════════════════════════════════════════════════
doc.add_heading('7. Scripts and Outputs', level=1)
# ══════════════════════════════════════════════════════
tbl(['Block', 'Script', 'Content'],
    [['01', '01_sample_description.py', 'Demographic frequency tables'],
     ['02', '02_sample_description_draft.py', 'Word draft: sample description + Figure 1 + Tables 1–2'],
     ['03', '03_hypotheses_EI_investment.py', 'H1/H2: EI–investment correlations (all ns)'],
     ['05', '05_bootstrap_power.py', 'Bootstrap + Fisher-z power analysis; fig04 power curve'],
     ['13', '13_hypothesis_H4_congruence.py', 'H4: EI × congruity two-way ANOVA'],
     ['15', '15_lowEI_congruence.py', 'R3: low-EI focused test; fig14'],
     ['16', '16_congruence_moderators.py', 'Congruence gap by EI/gender/experience; fig15 forest plot'],
     ['17', '17_incongruent_penalty.py', 'R2: A vs B comparison; fig16'],
     ['18', '18_incongruity_both_directions.py', 'Within-industry founder comparisons; fig17'],
     ['19', '19_congruity_x_ei.py', 'Three-way EI × founder × industry (all ns); fig18'],
     ['20', '20_robustness_moderators.py', 'First robustness pass: exp., success, risk'],
     ['21', '21_ei_gender_gap.py', 'EI moderation of raw gender gap (all ns); fig19'],
     ['22', '22_storyline_draft.py', 'Consolidated Word storyline draft (main deliverable)'],
     ['23', '23_extended_H7_H9.py', 'H7 SEA specificity, H8 participant gender, H9 warmth (all ns)'],
     ['24', '24_ei_by_gender.py', 'EI by participant gender, covariate-adjusted'],
     ['25', '25_ei_gender_subsection.py', 'Word subsection: EI by participant gender'],
     ['26', '26_litreview_comparison_memo.py', 'Word memo: lit review vs results, edits, papers to add'],
     ['27', '27_storyline_robustness.py', 'Full robustness battery (7 levers × 3 results)'],
     ['28', '28_pitch_order_models.py', 'Formal pitch-order control + effect × order interactions'],
     ['29', '29_robustness_section_draft.py', 'Word: full robustness section with tables'],
     ['30', '30_robustness_onepager.py', 'Word: one-page robustness summary table']],
    font_size=9)

OUT = os.path.join(HERE, '31_session_summary.docx')
doc.save(OUT)
print('Saved', OUT)
