#!/usr/bin/env python3
"""Analysis block 8: H6 variant - EI and equality between MALE and MIXED teams.

H: Participants with higher EI allocate funding more equally between male- and
   mixed-founded start-ups than participants with lower EI.

Between-subjects founder gender -> restrict to male (n=62) and mixed (n=70)
conditions; DV = total investment (invest_sv+invest_bu, 0-6). "More equal" for
high EI = smaller male-vs-mixed difference -> tested as EI x condition interaction.
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

# restrict to male + mixed
keep = np.isin(gender, ['male', 'mixed'])
df = pd.DataFrame({'invest': invest[keep], 'EI': ei[keep], 'cond': gender[keep]})
df['EI_c'] = df.EI - df.EI.mean()
n_male, n_mix = (df.cond == 'male').sum(), (df.cond == 'mixed').sum()

print('=' * 68)
print(f'H6 variant: MALE (n={n_male}) vs MIXED (n={n_mix}) | DV = total investment 0-6')
print('=' * 68)

# ---- interaction test (continuous EI) ----
mod = smf.ols('invest ~ EI_c * C(cond)', data=df).fit()
aov = sm.stats.anova_lm(mod, typ=2)
Fi, pi = aov.loc['EI_c:C(cond)', 'F'], aov.loc['EI_c:C(cond)', 'PR(>F)']
print('\n### EI x condition interaction (Type II ANOVA)  [H needs SIGNIFICANT interaction]')
print(aov.round(3).to_string())
print(f'\n  --> Interaction: F(1,{int(aov.loc["Residual","df"])}) = {Fi:.2f}, p = {pi:.3f}')

print('\n  EI->investment slope within each condition:')
for g in ['male', 'mixed']:
    sub = df[df.cond == g]
    mm = smf.ols('invest ~ EI_c', data=sub).fit()
    print(f'    {g:6s} (n={len(sub):3d}): b = {mm.params["EI_c"]:+.3f}, p = {mm.pvalues["EI_c"]:.3f}')

# ---- equality framing: median split ----
med = np.median(ei)                      # split on full-sample EI median (consistent w/ prior blocks)
hi = ei >= med
print(f'\n### Equality (median split EI at {med:.2f}); gap = |male - mixed| investment')
for lbl, mask in [('Low EI', ~hi), ('High EI', hi)]:
    m_male = invest[(gender == 'male') & mask]
    m_mix = invest[(gender == 'mixed') & mask]
    gap = abs(m_male.mean() - m_mix.mean())
    print(f'  {lbl:8s}: male M={m_male.mean():.2f} (n={len(m_male)}), '
          f'mixed M={m_mix.mean():.2f} (n={len(m_mix)})  -> gap = {gap:.2f}')
print('  H predicts the HIGH-EI gap to be SMALLER.')

# ---- per-dimension interaction (supplement) ----
print('\n### Per-EI-dimension interaction (male vs mixed)')
print(f'{"Dim":6s} | {"F":>6s} | {"p":>6s}')
for d, cols in DIMS.items():
    s = sc(cols)[keep]
    dd = pd.DataFrame({'invest': invest[keep], 'x': s - s.mean(), 'cond': gender[keep]})
    mm = smf.ols('invest ~ x * C(cond)', data=dd).fit()
    a = sm.stats.anova_lm(mm, typ=2)
    print(f'{d:6s} | {a.loc["x:C(cond)","F"]:6.2f} | {a.loc["x:C(cond)","PR(>F)"]:.3f}')

# ---- chart ----
def se(a): return a.std(ddof=1) / np.sqrt(len(a))
low_means = [invest[(gender == c) & (~hi)].mean() for c in ['male', 'mixed']]
high_means = [invest[(gender == c) & hi].mean() for c in ['male', 'mixed']]
low_se = [se(invest[(gender == c) & (~hi)]) for c in ['male', 'mixed']]
high_se = [se(invest[(gender == c) & hi]) for c in ['male', 'mixed']]
fig, ax = apa.grouped_bar_chart(
    ['Male', 'Mixed'],
    [('Low EI', low_means), ('High EI', high_means)],
    ylabel='Mean amount invested (0–6)',
    errors=[low_se, high_se], colors=['#D3D3D3', '#808080'])
apa.save(fig, os.path.join(HERE, 'figures', 'fig07_H6_male_mixed'))
print('\nSaved figures/fig07_H6_male_mixed.{png,pdf,svg}')
