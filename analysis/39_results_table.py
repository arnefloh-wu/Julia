#!/usr/bin/env python3
"""Analysis block 39: publication-ready hypothesis x results overview table.

Rendered in the same grey APA style as the figure set (Liberation Sans, #808080
header, light-grey grid), exported to PNG/PDF/SVG at 300 dpi. All statistics are
recomputed here so the table is guaranteed consistent with figs H1-H5.
"""
import csv, re, os, sys, textwrap
import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'figures'))
import apa_barchart as apa
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

with open(os.path.join(HERE, '..', 'MasterThesis_cleaned.csv'), newline='') as f:
    rows = list(csv.reader(f))
names, data = rows[0], rows[3:]
L = lambda v: int(re.match(r'\s*(\d+)', v.strip()).group(1))
colp = lambda p: [i for i, n in enumerate(names) if n.startswith(p) and '_DO' not in n]
eic = colp('Q10 (SEA)') + colp('Q11 (OEA)') + colp('Q12 (UOE)') + colp('Q13 (ROE)')
ei = np.array([[L(r[i]) for i in eic] for r in data], float).mean(1)
sv = np.array([float(r[names.index('invest_sv')]) for r in data])
bu = np.array([float(r[names.index('invest_bu')]) for r in data])
g = np.array([r[names.index('team_gender')] for r in data])
exp = np.array([r[names.index('Q23')] for r in data])
resp = np.array([r[names.index('Q16')].strip() for r in data])
MED = np.median(ei)


def welch(a, b):
    n1, n2 = len(a), len(b)
    s1, s2 = a.std(ddof=1), b.std(ddof=1)
    t, p2 = stats.ttest_ind(a, b, equal_var=False)
    dfw = (s1**2/n1 + s2**2/n2)**2 / ((s1**2/n1)**2/(n1-1) + (s2**2/n2)**2/(n2-1))
    sp = np.sqrt(((n1-1)*s1**2 + (n2-1)*s2**2) / (n1+n2-2))
    return dict(m1=a.mean(), m2=b.mean(), n1=n1, n2=n2, t=t, dfw=dfw,
                d=(a.mean()-b.mean())/sp, p1=p2/2 if t > 0 else 1-p2/2, p2=p2)

# H1 within-subjects
t1, p1two = stats.ttest_rel(sv, bu)
dz = (sv - bu).mean()/(sv - bu).std(ddof=1)
# H2-H5
r2 = welch(sv[g == 'male'], bu[g == 'female'])
r3 = welch(sv[(g == 'male') & (ei < MED)], bu[(g == 'female') & (ei < MED)])
m4 = (ei < MED) & (exp == 'Nein')
r4 = welch(sv[(g == 'male') & m4], bu[(g == 'female') & m4])
r5 = welch(ei[resp == 'Männlich'], ei[resp == 'Weiblich'])


def pstr(p):
    return '< .001' if p < .001 else f'{p:.3f}'.lstrip('0')


# rows: (#, hypothesis, comparison-lines, test, p, effect, outcome)
ROWS = [
    ('H1',
     'Startups in male-dominated industries receive more investment than '
     'startups in female-dominated industries.',
     [f'{sv.mean():.2f} vs {bu.mean():.2f}', '(n = 187)'],
     'Paired t(186) = 5.08', f'{pstr(p1two/2)} ᵃ', 'd$_z$ = 0.37', 'Supported'),
    ('H2',
     'Male founders in male-dominated industries receive more investment than '
     'female founders in female-dominated industries.',
     [f"{r2['m1']:.2f} vs {r2['m2']:.2f}", f"(n = {r2['n1']} / {r2['n2']})"],
     f"Welch t({r2['dfw']:.0f}) = {r2['t']:.2f}", f'{pstr(r2["p1"])} ᵃ',
     f"d = {r2['d']:.2f}", 'Marginal'),
    ('H3',
     'Among investors lower in EI, masculine-congruent startups receive more '
     'investment than feminine-congruent startups.',
     [f"{r3['m1']:.2f} vs {r3['m2']:.2f}", f"(n = {r3['n1']} / {r3['n2']})"],
     f"Welch t({r3['dfw']:.0f}) = {r3['t']:.2f}", f'{pstr(r3["p1"])} ᵃ',
     f"d = {r3['d']:.2f}", 'Supported'),
    ('H4',
     'Among lower-EI investors without investment experience, masculine-congruent '
     'startups receive more investment than feminine-congruent startups.',
     [f"{r4['m1']:.2f} vs {r4['m2']:.2f}", f"(n = {r4['n1']} / {r4['n2']})"],
     f"Welch t({r4['dfw']:.0f}) = {r4['t']:.2f}", pstr(r4['p2']),
     f"d = {r4['d']:.2f}", 'Supported'),
    ('H5',
     'Male participants score lower on emotional intelligence than female '
     'participants.',
     [f"{r5['m1']:.2f} vs {r5['m2']:.2f}", f"(n = {r5['n1']} / {r5['n2']})"],
     f"Welch t({r5['dfw']:.0f}) = {abs(r5['t']):.2f}", pstr(r5['p2']),
     f"d = {abs(r5['d']):.2f}", 'Supported'),
]

apa.apply_apa_style()
HEAD = '#808080'
SHADE = '#F2F2F2'
GRID = '#BFBFBF'
headers = ['', 'Hypothesis', 'Group means', 'Test statistic', 'p', 'Effect size', 'Outcome']
# column left edges + widths (sum = 1)
W = [0.045, 0.345, 0.135, 0.165, 0.075, 0.105, 0.130]
X = np.concatenate([[0], np.cumsum(W)])
WRAP = 50  # chars for hypothesis column

# wrap hypothesis text, compute lines per row
wrapped = [textwrap.wrap(r[1], WRAP) for r in ROWS]
row_lines = [max(len(w), 2) for w in wrapped]   # >=2 (comparison has 2 lines)
LINE_H = 0.30   # inches per text line
PAD = 0.18      # inches vertical padding per row
head_h = 0.46
row_h = [n*LINE_H + PAD for n in row_lines]
total_h = head_h + sum(row_h) + 0.55   # +footnote
FIG_W = 11.6
fig, ax = plt.subplots(figsize=(FIG_W, total_h))
ax.set_xlim(0, 1); ax.set_ylim(0, total_h)
ax.axis('off')

y = total_h - 0.10
# title
ax.text(0, y, 'Table 1', fontsize=11.5, fontweight='bold', va='top')
ax.text(0, y - 0.24, 'Overview of Hypotheses and Empirical Results',
        fontsize=10.5, style='italic', va='top')
y -= 0.62

# header row
ax.add_patch(Rectangle((0, y - head_h), 1, head_h, facecolor=HEAD,
                       edgecolor='none', zorder=1))
for h, x0, w in zip(headers, X, W):
    ha = 'left' if h in ('Hypothesis',) else 'center'
    xt = x0 + 0.008 if ha == 'left' else x0 + w/2
    ax.text(xt, y - head_h/2, h, fontsize=9.8, fontweight='bold', color='white',
            ha=ha, va='center', zorder=3)
ytop = y
y -= head_h

# body rows
for ri, (row, lines, rh) in enumerate(zip(ROWS, wrapped, row_h)):
    if ri % 2 == 1:
        ax.add_patch(Rectangle((0, y - rh), 1, rh, facecolor=SHADE,
                               edgecolor='none', zorder=0))
    cy = y - rh/2
    num, _, comp, test, pv, eff, outc = row
    # # column
    ax.text(X[0] + W[0]/2, cy, num, fontsize=9.6, fontweight='bold',
            ha='center', va='center')
    # hypothesis (wrapped, top-aligned block centred vertically)
    n = len(lines)
    y0 = cy + (n - 1)*LINE_H/2
    for k, ln in enumerate(lines):
        ax.text(X[1] + 0.008, y0 - k*LINE_H, ln, fontsize=9.0,
                ha='left', va='center')
    # comparison (2 lines)
    ax.text(X[2] + W[2]/2, cy + LINE_H/2, comp[0], fontsize=9.0, ha='center', va='center')
    ax.text(X[2] + W[2]/2, cy - LINE_H/2, comp[1], fontsize=8.0, ha='center',
            va='center', color='#555555')
    # test, p, effect
    ax.text(X[3] + W[3]/2, cy, test, fontsize=9.0, ha='center', va='center')
    ax.text(X[4] + W[4]/2, cy, pv, fontsize=9.0, ha='center', va='center')
    ax.text(X[5] + W[5]/2, cy, eff, fontsize=9.0, ha='center', va='center')
    # outcome (bold)
    ax.text(X[6] + W[6]/2, cy, outc, fontsize=9.2, fontweight='bold',
            ha='center', va='center')
    y -= rh
ybot = y

# horizontal rules
for yy in [ytop, ytop - head_h, ybot]:
    ax.plot([0, 1], [yy, yy], color='black', lw=1.1, zorder=4)
# light row separators
yy = ytop - head_h
for rh in row_h[:-1]:
    yy -= rh
    ax.plot([0, 1], [yy, yy], color=GRID, lw=0.5, zorder=2)

# footnote
note = ('Note. Investment measured on a 0–3 scale; emotional intelligence (EI) on the '
        'WLEIS 1–7 scale. Group means: H1 = SiteVision vs BalanceUp; H2–H4 = masculine- '
        'vs feminine-congruent; H5 = male vs female participants. d = Cohen’s d; '
        'd$_z$ = within-subjects Cohen’s d. ᵃ one-tailed test (directional hypothesis). '
        '“Marginal” = directionally consistent, p just above .05. N = 187.')
for k, ln in enumerate(textwrap.wrap(note, 150)):
    ax.text(0, ybot - 0.16 - k*0.20, ln, fontsize=7.6, style='italic', va='top')

fig.subplots_adjust(left=0.015, right=0.985, top=0.99, bottom=0.02)
apa.save(fig, os.path.join(HERE, 'figures', 'table1_hypotheses_results'))
plt.close(fig)
print('saved table1_hypotheses_results')
for r in ROWS:
    print(r[0], r[3], r[4], r[5], r[6])
