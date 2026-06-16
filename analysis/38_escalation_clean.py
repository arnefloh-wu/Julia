#!/usr/bin/env python3
"""Analysis block 38: clean escalation figure (full -> H3 -> H4 subgroups).

Re-issues figH3H5_escalation without the legend/annotation overlap: the legend
is moved below the plot, the Delta/d annotations sit centred above each pair with
extra headroom, and subgroup labels use the FINAL hypothesis numbering
(Lower EI = H3; Lower EI & no experience = H4).
"""
import csv, re, os, sys
import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'figures'))
import apa_barchart as apa
import matplotlib.pyplot as plt

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
MED = np.median(ei)


def cell(mask):
    a = sv[(g == 'male') & mask]; b = bu[(g == 'female') & mask]
    n1, n2 = len(a), len(b)
    sp = np.sqrt(((n1-1)*a.std(ddof=1)**2 + (n2-1)*b.std(ddof=1)**2) / (n1+n2-2))
    return dict(m1=a.mean(), m2=b.mean(), se1=a.std(ddof=1)/np.sqrt(n1),
                se2=b.std(ddof=1)/np.sqrt(n2), diff=a.mean()-b.mean(),
                d=(a.mean()-b.mean())/sp)


FULL = cell(np.ones(len(ei), bool))
H3 = cell(ei < MED)
H4 = cell((ei < MED) & (exp == 'Nein'))

apa.apply_apa_style()
DARK, GREY = '#808080', '#D3D3D3'
groups = ['Full\nsample', 'Lower EI\n(H3)', 'Lower EI &\nno experience\n(H4)']
masc_m = [FULL['m1'], H3['m1'], H4['m1']]
fem_m = [FULL['m2'], H3['m2'], H4['m2']]
masc_se = [FULL['se1'], H3['se1'], H4['se1']]
fem_se = [FULL['se2'], H3['se2'], H4['se2']]

fig, ax = plt.subplots(figsize=(7.4, 5.2))
x = np.arange(3); bw = 0.38
b1 = ax.bar(x - bw/2, masc_m, bw*0.95, yerr=masc_se, capsize=3,
            color=DARK, edgecolor='black', linewidth=0.8, zorder=3,
            error_kw=dict(lw=0.8), label='Masculine-congruent')
b2 = ax.bar(x + bw/2, fem_m, bw*0.95, yerr=fem_se, capsize=3,
            color=GREY, edgecolor='black', linewidth=0.8, zorder=3,
            error_kw=dict(lw=0.8), label='Feminine-congruent')
# Delta / d annotation centred above each pair, clear of the bars
for xi, rr in zip(x, [FULL, H3, H4]):
    top = max(rr['m1'] + rr['se1'], rr['m2'] + rr['se2'])
    ax.text(xi, top + 0.12, f"$\\Delta$ = {rr['diff']:+.2f}\nd = {rr['d']:.2f}",
            ha='center', va='bottom', fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(groups)
ax.set_ylabel('Mean amount invested (0–3)')
ax.set_ylim(0, 3.0)
# legend OUTSIDE the plot (below), so it never overlaps bars or annotations
ax.legend(frameon=False, fontsize=9.5, loc='upper center',
          bbox_to_anchor=(0.5, -0.13), ncol=2)
fig.tight_layout()
apa.save(fig, os.path.join(HERE, 'figures', 'figH3H4_escalation'))
plt.close(fig)
print('saved figH3H4_escalation  '
      f"(FULL d={FULL['d']:.2f}, H3 d={H3['d']:.2f}, H4 d={H4['d']:.2f})")
