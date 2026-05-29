#!/usr/bin/env python3
"""Analysis block 19: is the gender-CONGRUITY effect moderated by EI?

Congruity effect = founder gender x industry interaction. Per person,
d = invest_sv - invest_bu (industry preference; SiteVision male-typed minus
BalanceUp female-typed). For MALE founders the congruent startup is SV, for
FEMALE founders it is BU, so the congruity effect = d(male founders) - d(female
founders). EI moderation of congruity = three-way EI x founder x industry,
tested as the EI x founder interaction on d:  d ~ EI_c * C(founder).
Run for Total EI and each WLEIS dimension. (Mixed condition excluded.)
"""
import csv, re, os, sys
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'figures'))
import apa_barchart as apa
import matplotlib.pyplot as plt

SRC = os.path.join(HERE, '..', 'MasterThesis_cleaned.csv')
with open(SRC, newline='') as f:
    rows = list(csv.reader(f))
names, data = rows[0], rows[3:]
def cols_for(p): return [i for i, n in enumerate(names) if n.startswith(p) and '_DO' not in n]
DIMS = {'SEA': cols_for('Q10 (SEA)'), 'OEA': cols_for('Q11 (OEA)'),
        'UOE': cols_for('Q12 (UOE)'), 'ROE': cols_for('Q13 (ROE)')}
all_items = sum(DIMS.values(), [])
i_sv, i_bu, i_tg = names.index('invest_sv'), names.index('invest_bu'), names.index('team_gender')
likert = lambda v: int(re.match(r'\s*(\d+)', v.strip()).group(1))
sc = lambda c: np.array([[likert(r[i]) for i in c] for r in data], float).mean(1)

sv = np.array([float(r[i_sv]) for r in data]); bu = np.array([float(r[i_bu]) for r in data])
g = np.array([r[i_tg] for r in data])
keep = np.isin(g, ['male', 'female'])
d = (sv - bu)[keep]                 # industry preference per person
founder = g[keep]
EI = {'Total': sc(all_items)[keep], **{k: sc(c)[keep] for k, c in DIMS.items()}}
star = lambda p: '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else ''

print('=' * 76)
print('Does EI moderate the gender-CONGRUITY effect? (3-way EI x founder x industry)')
print('congruity effect = d(male founders) - d(female founders), d = invest_sv - invest_bu')
print('=' * 76)
print(f'{"EI":7s} | {"3-way b":>8s} {"p":>7s} | {"congruity Low":>13s} {"congruity High":>14s}')
order = ['Total', 'SEA', 'OEA', 'UOE', 'ROE']
res = {}
for k in order:
    x = EI[k]
    df = pd.DataFrame({'d': d, 'x': x - x.mean(), 'f': founder})
    m = smf.ols('d ~ x * C(f)', data=df).fit()
    iname = [t for t in m.params.index if ':' in t][0]
    b, p = m.params[iname], m.pvalues[iname]
    # congruity effect by EI median split
    med = np.median(x); hi = x >= med
    def cong(mask):
        return d[(founder == 'male') & mask].mean() - d[(founder == 'female') & mask].mean()
    cL, cH = cong(~hi), cong(hi)
    res[k] = (b, p, cL, cH)
    print(f'{k:7s} | {b:+8.3f} {p:7.3f}{star(p):2s}| {cL:+13.2f} {cH:+14.2f}')

print('\n(congruity > 0 = matching-gender founder favoured; 3-way p tests whether')
print(' the congruity effect differs by EI. All near zero / ns expected.)')

# ---- chart: congruity effect at Low vs High EI, per dimension ----
apa.apply_apa_style()
fig, ax = plt.subplots(figsize=(7.2, 4.5))
labs = ['Total', 'SEA', 'OEA', 'UOE', 'ROE']
x = np.arange(len(labs)); bw = 0.38
cL = [res[k][2] for k in labs]; cH = [res[k][3] for k in labs]
ax.bar(x - bw/2, cL, bw*0.95, label='Low EI', color='#D3D3D3', edgecolor='black', linewidth=0.8, zorder=3)
ax.bar(x + bw/2, cH, bw*0.95, label='High EI', color='#808080', edgecolor='black', linewidth=0.8, zorder=3)
for xi, v in zip(x - bw/2, cL):
    ax.text(xi, v + (0.01 if v >= 0 else -0.01), f'{v:+.2f}', ha='center',
            va='bottom' if v >= 0 else 'top', fontsize=7.5)
for xi, v in zip(x + bw/2, cH):
    ax.text(xi, v + (0.01 if v >= 0 else -0.01), f'{v:+.2f}', ha='center',
            va='bottom' if v >= 0 else 'top', fontsize=7.5)
ax.axhline(0, color='black', lw=0.8)
ax.set_xticks(x); ax.set_xticklabels(labs)
ax.set_ylabel('Congruity effect\n(matching − mismatching founder)')
ax.set_ylim(-0.8, 0.8)
ax.legend(frameon=False, fontsize=9, loc='upper right')
fig.text(0.5, 0.005, 'Positive = matching-gender founder favoured; '
         'EI moderation = Low vs High bars differ (all 3-way interactions ns)',
         ha='center', fontsize=7.5, style='italic')
fig.tight_layout(rect=[0, 0.03, 1, 1])
apa.save(fig, os.path.join(HERE, 'figures', 'fig18_congruity_x_ei'))
print('\nSaved figures/fig18_congruity_x_ei.{png,pdf,svg}')
