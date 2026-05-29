#!/usr/bin/env python3
"""Build a Word subsection: 'Emotional Intelligence by Participant Gender'.
Reports raw and covariate-adjusted (age + STEM) gender differences in WLEIS.
Output: analysis/25_ei_gender_subsection.docx
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

def body(t):
    p = doc.add_paragraph(t); p.paragraph_format.line_spacing = 1.5; return p

doc.add_heading('Emotional Intelligence by Participant Gender', level=2)
body(
    'Because emotional intelligence is the central individual-difference variable '
    'in this study, gender differences in the WLEIS were examined before testing '
    'the substantive hypotheses. Female participants (n = 100) reported '
    'significantly higher total emotional intelligence than male participants '
    '(n = 84), M = 5.32 (SD = 0.77) versus M = 4.97 (SD = 0.71), Welch '
    't(182) = 3.19, p = .002, d = 0.47. The difference was concentrated in the two '
    'appraisal dimensions: self-emotion appraisal (SEA), M = 5.46 vs. 4.83, '
    'p < .001, d = 0.59, and others’ emotion appraisal (OEA), M = 5.74 vs. 5.05, '
    'p < .001, d = 0.66. In contrast, the use of emotion (UOE; p = .206) and '
    'regulation of emotion (ROE; p = .462) dimensions did not differ by gender, '
    'with ROE being numerically — though non-significantly — higher among men.'
)
body(
    'To rule out demographic confounds, each WLEIS score was regressed on '
    'participant gender while controlling for age and field of study (STEM vs. '
    'non-STEM). The gender effect was unchanged: women remained higher on total '
    'EI (b = 0.36, p = .002), SEA (b = 0.65, p < .001), and OEA (b = 0.66, '
    'p < .001), while UOE and ROE remained non-significant. The samples were well '
    'matched on age (M = 23.6 vs. 23.3 years) and comparable in STEM enrolment '
    '(13% vs. 23%), so the difference reflects gender rather than these covariates.'
)
body(
    'This pattern is consistent with the broader emotional-intelligence '
    'literature, in which women typically score higher on perceiving and '
    'appraising emotions, whereas gender differences in the regulation and '
    'instrumental use of emotion are small or absent. The finding also has a '
    'methodological implication for the present design: because emotional '
    'intelligence is correlated with participant gender, tests of whether EI’s '
    'moderating role differs between male and female participants operate on a '
    'restricted EI range within each gender, reducing their sensitivity. This is '
    'noted as a limitation where relevant.'
)
OUT = os.path.join(HERE, '25_ei_gender_subsection.docx')
doc.save(OUT)
print('Saved', OUT)
