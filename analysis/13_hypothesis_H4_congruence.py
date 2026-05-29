#!/usr/bin/env python3
"""Analysis block 13: H4 - gender-congruent startup preference x EI.

H4: Participants with LOWER EI invest more in male-founded start-ups in
    male-dominated industries than in female-founded start-ups in
    female-dominated industries.

Gender-congruent cells (between-subjects):
  masculine-congruent = invest_sv among MALE-condition pts (SiteVision/ConTech,
                        male founders + male-typed industry)        n=62
  feminine-congruent  = invest_bu among FEMALE-condition pts (BalanceUp/Wellness,
                        female founders + female-typed industry)    n=55
DV = focal investment (0-3). H4 -> masculine > feminine, esp. for LOW EI
(=> EI x type interaction; masculine-feminine gap larger at low EI).
NOTE: type bundles founder gender AND industry/pitch, so the main effect is
confounded with the baseline SiteVision>BalanceUp preference; the EI moderation
is the more specific test.
"""
import csv, re, os, sys
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
import statsmodels.api as sm

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'figures'))
import apa_barchart as apa

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
sc = lambda cols: np.array([[likert(r[i]) for i in cols] for r in data], float).mean(axis=1)

ei = sc(all_items)
invest_sv = np.array([float(r[i_sv]) for r in data])
invest_bu = np.array([float(r[i_bu]) for r in data])
gender = np.array([r[i_tg] for r in data])
male, female = gender == 'male', gender == 'female'

# congruent cells
masc_y, masc_ei = invest_sv[male], ei[male]
fem_y, fem_ei = invest_bu[female], ei[female]

print('=' * 72)
print('H4: masculine-congruent (SV|male) vs feminine-congruent (BU|female)')
print('=' * 72)
print(f'masculine-congruent: M = {masc_y.mean():.2f}, SD = {masc_y.std(ddof=1):.2f}  (n={len(masc_y)})')
print(f'feminine-congruent : M = {fem_y.mean():.2f}, SD = {fem_y.std(ddof=1):.2f}  (n={len(fem_y)})')
t, p = stats.ttest_ind(masc_y, fem_y, equal_var=False)
d = (masc_y.mean()-fem_y.mean()) / np.sqrt((masc_y.var(ddof=1)+fem_y.var(ddof=1))/2)
print(f'main effect (masc - fem) = {masc_y.mean()-fem_y.mean():+.2f}, '
      f'Welch t = {t:.2f}, p = {p:.3f}, d = {d:+.2f}')
print('  (confounded with baseline SiteVision>BalanceUp preference)')

# ---- EI moderation (continuous) ----
df = pd.DataFrame({'y': np.r_[masc_y, fem_y],
                   'EI': np.r_[masc_ei, fem_ei],
                   'type': ['masc']*len(masc_y) + ['fem']*len(fem_y)})
df['EI_c'] = df.EI - df.EI.mean()
df['masc'] = (df.type == 'masc').astype(int)
mod = smf.ols('y ~ EI_c * masc', data=df).fit()
print('\n### EI x type interaction (continuous EI; masc=1, fem=0)')
print(f'  type (masc-fem gap @mean EI): b = {mod.params["masc"]:+.3f}, p = {mod.pvalues["masc"]:.3f}')
print(f'  EI_c (slope in feminine):     b = {mod.params["EI_c"]:+.3f}, p = {mod.pvalues["EI_c"]:.3f}')
print(f'  EI_c:masc (interaction):      b = {mod.params["EI_c:masc"]:+.3f}, '
      f'p = {mod.pvalues["EI_c:masc"]:.3f}')
print('  H4 -> NEGATIVE interaction (masc-fem gap shrinks as EI rises).')

# ---- median split ----
med = np.median(ei)
print(f'\n### Median split (Total EI at {med:.2f})')
print(f'{"EI grp":7s} | {"masc M":>7s} {"n":>3s} | {"fem M":>7s} {"n":>3s} | {"gap":>6s} | {"t":>5s} {"p":>6s}')
cells = {}
for lbl in ['Low', 'High']:
    sel = (masc_ei < med) if lbl == 'Low' else (masc_ei >= med)
    selF = (fem_ei < med) if lbl == 'Low' else (fem_ei >= med)
    a, b = masc_y[sel], fem_y[selF]
    tt, pp = stats.ttest_ind(a, b, equal_var=False)
    cells[lbl] = (a.mean(), a.std(ddof=1)/np.sqrt(len(a)), b.mean(), b.std(ddof=1)/np.sqrt(len(b)))
    print(f'{lbl:7s} | {a.mean():7.2f} {len(a):3d} | {b.mean():7.2f} {len(b):3d} | '
          f'{a.mean()-b.mean():+6.2f} | {tt:5.2f} {pp:6.3f}')
print('  H4 -> Low-EI gap (masc-fem) larger & positive.')

# ---- per dimension interaction ----
print('\n### Per-EI-dimension interaction (EI_dim x type)')
print(f'{"Dim":6s} | {"b_intxn":>8s} {"p":>6s}')
for d_, cols in DIMS.items():
    s = sc(cols)
    dd = pd.DataFrame({'y': np.r_[invest_sv[male], invest_bu[female]],
                       'x': np.r_[s[male], s[female]] - np.r_[s[male], s[female]].mean(),
                       'masc': [1]*male.sum() + [0]*female.sum()})
    mm = smf.ols('y ~ x * masc', data=dd).fit()
    print(f'{d_:6s} | {mm.params["x:masc"]:+8.3f} {mm.pvalues["x:masc"]:.3f}')

# ---- chart ----
low_m = [cells['Low'][0], cells['Low'][2]]; low_se = [cells['Low'][1], cells['Low'][3]]
high_m = [cells['High'][0], cells['High'][2]]; high_se = [cells['High'][1], cells['High'][3]]
fig, ax = apa.grouped_bar_chart(
    ['Low EI', 'High EI'],
    [('Masculine-congruent (male founder, male industry)', [low_m[0], high_m[0]]),
     ('Feminine-congruent (female founder, female industry)', [low_m[1], high_m[1]])],
    ylabel='Mean amount invested (0–3)',
    errors=[[low_se[0], high_se[0]], [low_se[1], high_se[1]]],
    colors=['#808080', '#D3D3D3'])
ax.legend(frameon=False, fontsize=8, loc='upper right')
apa.save(fig, os.path.join(HERE, 'figures', 'fig12_H4_congruence'))
print('\nSaved figures/fig12_H4_congruence.{png,pdf,svg}')
