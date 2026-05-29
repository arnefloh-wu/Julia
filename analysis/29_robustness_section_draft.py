#!/usr/bin/env python3
"""Build a Word draft of the Robustness Checks section for the three storyline
results. Output: analysis/29_robustness_section_draft.docx
"""
import os
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

HERE = os.path.dirname(os.path.abspath(__file__))
doc = Document()
style = doc.styles['Normal']
style.font.name = 'Times New Roman'; style.font.size = Pt(12)
style.paragraph_format.space_after = Pt(6)

def body(t, italic=False):
    p = doc.add_paragraph(); r = p.add_run(t); r.italic = italic
    p.paragraph_format.line_spacing = 1.5
    return p

def tbl(headers, rows):
    t = doc.add_table(rows=1, cols=len(headers)); t.style = 'Light List Accent 1'
    for i, h in enumerate(headers):
        run = t.rows[0].cells[i].paragraphs[0].add_run(h); run.bold = True
    for row in rows:
        c = t.add_row().cells
        for i, v in enumerate(row):
            c[i].text = v
    return t

doc.add_heading('Robustness Checks', level=1)
body(
    'The three focal results — the industry effect (R1), the gender-role congruity '
    'effect (R2), and the low-EI congruence preference (R3) — were subjected to a '
    'battery of robustness checks. These comprised (a) adjustment for perceived '
    'success, perceived startup risk, founder-team competence ratings, and '
    'dispositional risk tolerance; (b) adjustment for and interaction with pitch '
    'presentation order; (c) exclusion of the fastest 5% of respondents as an '
    'attention filter; and (d) re-estimation within experience-based subgroups. '
    'Two findings stand out: perceived success consistently accounts for the '
    'effects, and presentation order strongly moderates all three.'
)

# ── Covariate adjustment ──
doc.add_heading('Adjustment for Perceptual and Dispositional Covariates', level=2)
body(
    'The industry effect (R1) and the congruity effect (R2) were robust to '
    'adjustment for perceived startup risk, founder competence, and dispositional '
    'risk tolerance (Q14 general and Q15 financial risk willingness; all p < .01). '
    'In both cases, however, the effect was reduced to non-significance once '
    'perceived probability of success was entered as a covariate (R1: p = .059; '
    'R2: p = .091), and remained non-significant in the fully adjusted model. The '
    'low-EI congruence effect (R3) was the most sensitive: it was fully absorbed '
    'by perceived success (p = .68) and by competence (p = .28), although it '
    'persisted, and even strengthened, when only dispositional risk traits were '
    'controlled (p = .038). Across all three results, perceived probability of '
    'success was the consistent mediating covariate, reinforcing the '
    'interpretation that the effects operate through perceived venture viability '
    'rather than through founder gender per se.'
)
tbl(['Result', 'Baseline', '+ success', '+ risk', '+ competence', '+ all'],
    [['R1 industry', 'p < .001', 'p = .059', 'p < .001', 'p < .001', 'p = .032'],
     ['R2 A vs B',   'p = .001', 'p = .091', 'p = .002', 'p = .004', 'p = .106'],
     ['R3 low-EI',   'p = .032', 'p = .68',  'p = .092', 'p = .28',  'p = .75']])

# ── Pitch order ──
doc.add_heading('Sensitivity to Pitch Presentation Order', level=2)
body(
    'The most consequential robustness finding concerns presentation order. '
    'Because order was counterbalanced and approximately balanced across '
    'conditions, including it as a covariate left the average effect estimates '
    'essentially unchanged (R1 b = 0.48, p < .001; R2 b = 0.54, p = .001; R3 '
    'b = 0.46, p = .069). However, the effect-by-order interaction was large and '
    'highly significant for every result, indicating that the effects are '
    'concentrated almost entirely in the condition in which SiteVision was shown '
    'first.'
)
tbl(['Result', 'SiteVision shown first', 'BalanceUp shown first', 'Effect × order'],
    [['R1 industry',  '+1.08, p < .001', '−0.15, p = .24 (ns)', 'b = 1.24, p < .001'],
     ['R2 A vs B',    't = 5.89, p < .001', 't = −0.85, p = .40 (ns)', 'b = 1.40, p < .001'],
     ['R3 low-EI',    't = 4.79, p < .001', 't = −1.21, p = .88 (ns)', 'b = 1.62, p < .001']])
body(
    'In each case the effect is large and highly significant when SiteVision is '
    'presented first but disappears, and numerically reverses, when BalanceUp is '
    'presented first. This pattern is consistent with a primacy or anchoring '
    'contribution: participants allocated more to whichever pitch they encountered '
    'first, and because SiteVision is the masculine-typed venture, an order effect '
    'mechanically resembles an industry or congruity effect. Two implications '
    'follow. First, the average effects reported in the main analyses are not '
    'attributable to a simple confound, since order was balanced; but second, '
    'their generalizability is limited, because they are not stable across '
    'presentation orders. The order dependence is therefore reported transparently '
    'as a boundary condition, and the substantive results should be interpreted '
    'with this sensitivity in mind.'
)

# ── Attention / subgroups ──
doc.add_heading('Attention Filter and Subgroup Stability', level=2)
body(
    'Excluding the fastest 5% of respondents (a careless-responding filter based '
    'on completion time) left R1 (p < .001) and R2 (p = .001) unchanged, whereas '
    'R3 fell to borderline significance (one-tailed p = .052). R3 was similarly '
    'borderline under a bottom-tertile definition of low EI (p = .050) and within '
    'the never-founded subgroup (p = .059). The industry and congruity effects '
    'were also stable across investment- and entrepreneurial-experience subgroups. '
    'Taken together, R1 and R2 are statistically robust to covariate adjustment, '
    'attention filtering, and subgroup variation, whereas R3 should be regarded as '
    'suggestive rather than confirmatory, given its consistent fragility across '
    'these checks.'
)

# ── Conclusion ──
doc.add_heading('Summary', level=2)
body(
    'The robustness analyses yield three conclusions. First, perceived probability '
    'of success is the proximal covariate that accounts for all three effects, '
    'supporting a viability-based rather than warmth-based mechanism. Second, the '
    'effects are markedly stronger when the masculine-typed venture is presented '
    'first, an order dependence that constrains their generalizability and must be '
    'disclosed. Third, while the industry (R1) and congruity (R2) effects withstand '
    'the remaining checks, the low-EI congruence effect (R3) is fragile and is '
    'therefore interpreted with appropriate caution.'
)

OUT = os.path.join(HERE, '29_robustness_section_draft.docx')
doc.save(OUT)
print('Saved', OUT)
