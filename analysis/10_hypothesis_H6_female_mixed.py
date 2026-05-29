#!/usr/bin/env python3
"""Analysis block 10: H6 variant - EI and equality between FEMALE and MIXED teams.

H: Participants with higher EI allocate funding more equally between female- and
   mixed-founded start-ups than participants with lower EI.

Between-subjects founder gender -> restrict to female (n=55) and mixed (n=70);
DV = total investment (invest_sv+invest_bu, 0-6). "More equal" for high EI =
smaller female-vs-mixed difference -> tested as EI x condition interaction.
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
invest = np.array([float(r[i_sv]) + float(r[i_bu]) for r in data])
gender = np.array([r[i_tg] for r in data])

keep = np.isin(gender, ['female', 'mixed'])
df = pd.DataFrame({'invest': invest[keep], 'EI': ei[keep], 'cond': gender[keep]})
df['EI_c'] = df.EI - df.EI.mean()
n_fem, n_mix = (df.cond == 'female').sum(), (df.cond == 'mixed').sum()

print('=' * 68)
print(f'H6 variant: FEMALE (n={n_fem}) vs MIXED (n={n_mix}) | DV = total investment 0-6')
print('=' * 68)

mod = smf.ols('invest ~ EI_c * C(cond)', data=df).fit()
aov = sm.stats.anova_lm(mod, typ=2)
Fi, pi = aov.loc['EI_c:C(cond)', 'F'], aov.loc['EI_c:C(cond)', 'PR(>F)']
print('\n### EI x condition interaction (Type II ANOVA)  [H needs SIGNIFICANT interaction]')
print(aov.round(3).to_string())
print(f'\n  --> Interaction: F(1,{int(aov.loc["Residual","df"])}) = {Fi:.2f}, p = {pi:.3f}')

print('\n  EI->investment slope within each condition:')
for g in ['female', 'mixed']:
    sub = df[df.cond == g]
    mm = smf.ols('invest ~ EI_c', data=sub).fit()
    print(f'    {g:6s} (n={len(sub):3d}): b = {mm.params["EI_c"]:+.3f}, p = {mm.pvalues["EI_c"]:.3f}')

med = np.median(ei); hi = ei >= med
print(f'\n### Equality (median split EI at {med:.2f}); gap = |female - mixed| investment')
for lbl, mask in [('Low EI', ~hi), ('High EI', hi)]:
    m_fem = invest[(gender == 'female') & mask]; m_mix = invest[(gender == 'mixed') & mask]
    print(f'  {lbl:8s}: female M={m_fem.mean():.2f} (n={len(m_fem)}), '
          f'mixed M={m_mix.mean():.2f} (n={len(m_mix)})  -> gap = {abs(m_fem.mean()-m_mix.mean()):.2f}')
print('  H predicts the HIGH-EI gap to be SMALLER.')

print('\n### Per-EI-dimension interaction (female vs mixed)')
print(f'{"Dim":6s} | {"F":>6s} | {"p":>6s}')
for d, cols in DIMS.items():
    s = sc(cols)[keep]
    dd = pd.DataFrame({'invest': invest[keep], 'x': s - s.mean(), 'cond': gender[keep]})
    a = sm.stats.anova_lm(smf.ols('invest ~ x * C(cond)', data=dd).fit(), typ=2)
    print(f'{d:6s} | {a.loc["x:C(cond)","F"]:6.2f} | {a.loc["x:C(cond)","PR(>F)"]:.3f}')

def se(a): return a.std(ddof=1) / np.sqrt(len(a))
low_means = [invest[(gender == c) & (~hi)].mean() for c in ['female', 'mixed']]
high_means = [invest[(gender == c) & hi].mean() for c in ['female', 'mixed']]
low_se = [se(invest[(gender == c) & (~hi)]) for c in ['female', 'mixed']]
high_se = [se(invest[(gender == c) & hi]) for c in ['female', 'mixed']]
fig, ax = apa.grouped_bar_chart(
    ['Female', 'Mixed'],
    [('Low EI', low_means), ('High EI', high_means)],
    ylabel='Mean amount invested (0–6)',
    errors=[low_se, high_se], colors=['#D3D3D3', '#808080'])
apa.save(fig, os.path.join(HERE, 'figures', 'fig09_H6_female_mixed'))
print('\nSaved figures/fig09_H6_female_mixed.{png,pdf,svg}')
