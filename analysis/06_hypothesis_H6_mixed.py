#!/usr/bin/env python3
"""Analysis block 6: H6 (revised) - EI and equality across founder-team types.

H6: Participants with higher EI allocate funding more equally between female-,
    male- and mixed-founded start-ups than participants with lower EI.

Design: founder-team gender (team_gender) is BETWEEN-subjects (male/female/mixed);
both of a participant's start-ups share it. So "equality across the three
founder types" is operationalized at the group level: higher-EI participants
should invest more UNIFORMLY across the three conditions (smaller condition
effect) than lower-EI participants -> tested as an EI x team_gender interaction
on total investment (invest_sv + invest_bu, 0-6).
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
ei_cols = [i for i, n in enumerate(names)
           if n.startswith(('Q10 (SEA)', 'Q11 (OEA)', 'Q12 (UOE)', 'Q13 (ROE)'))
           and '_DO' not in n]
i_sv, i_bu, i_tg = names.index('invest_sv'), names.index('invest_bu'), names.index('team_gender')
likert = lambda v: int(re.match(r'\s*(\d+)', v.strip()).group(1))
EI = np.array([[likert(r[i]) for i in ei_cols] for r in data], float)
ei = EI.mean(axis=1)
invest = np.array([float(r[i_sv]) + float(r[i_bu]) for r in data])
gender = np.array([r[i_tg] for r in data])
N = len(data)

df = pd.DataFrame({'invest': invest, 'EI': ei, 'cond': gender})
df['EI_c'] = df.EI - df.EI.mean()

print('=' * 70)
print(f'N = {N} | DV = total investment (invest_sv+invest_bu, 0-6)')
print(f'overall: M = {invest.mean():.2f}, SD = {invest.std(ddof=1):.2f}')
print('=' * 70)

# ---- H6 test: EI x founder-condition interaction (continuous EI) ----
m = smf.ols('invest ~ EI_c * C(cond)', data=df).fit()
aov = sm.stats.anova_lm(m, typ=2)
print('\n### EI x team_gender interaction (Type II ANOVA, continuous EI)')
print(aov.round(3).to_string())
inter_p = aov.loc['EI_c:C(cond)', 'PR(>F)']
print(f'\n  --> Interaction (EI x founder type): F = {aov.loc["EI_c:C(cond)","F"]:.2f}, '
      f'p = {inter_p:.3f}  [H6 needs a SIGNIFICANT interaction]')

# per-condition EI slopes
print('\n  EI->investment slope within each founder condition:')
for g in ['male', 'female', 'mixed']:
    sub = df[df.cond == g]
    mm = smf.ols('invest ~ EI_c', data=sub).fit()
    print(f'    {g:7s} (n={len(sub):3d}): b = {mm.params["EI_c"]:+.3f}, p = {mm.pvalues["EI_c"]:.3f}')

# ---- equality framing: median split, spread across the 3 conditions ----
med = np.median(ei); hi = ei >= med
print(f'\n### EQUALITY ACROSS FOUNDER TYPES (median split EI at {med:.2f})')
conds = ['male', 'female', 'mixed']
disp = {}
print(f'{"EI group":9s} | ' + ' | '.join(f'{c:>7s}' for c in conds) + ' |  range   SD')
for lbl, mask in [('Low', ~hi), ('High', hi)]:
    means = [invest[(gender == c) & mask].mean() for c in conds]
    rng = max(means) - min(means)
    sd = np.std(means, ddof=1)
    disp[lbl] = (means, rng, sd,
                 [invest[(gender == c) & mask].std(ddof=1) / np.sqrt(((gender == c) & mask).sum())
                  for c in conds])
    print(f'{lbl:9s} | ' + ' | '.join(f'{x:7.2f}' for x in means) + f' | {rng:5.2f}  {sd:5.2f}')
print('  H6 predicts the HIGH-EI spread (range/SD across conditions) to be SMALLER.')

# one-way ANOVA of investment across the 3 conditions, within each EI group
for lbl, mask in [('Low', ~hi), ('High', hi)]:
    groups = [invest[(gender == c) & mask] for c in conds]
    f, p = stats.f_oneway(*groups)
    print(f'  {lbl}-EI: founder-type effect on investment  F = {f:.2f}, p = {p:.3f}')

# ---- chart: investment by founder condition x EI group ----
labels = ['Male', 'Female', 'Mixed']
low_means, _, _, low_se = disp['Low']
high_means, _, _, high_se = disp['High']
fig, ax = apa.grouped_bar_chart(
    labels,
    [('Low EI', low_means), ('High EI', high_means)],
    ylabel='Mean amount invested (0–6)',
    errors=[low_se, high_se],
    colors=['#D3D3D3', '#808080'],
)
apa.save(fig, os.path.join(HERE, 'figures', 'fig05_H6_mixed'))
print('\nSaved figures/fig05_H6_mixed.{png,pdf,svg}')
