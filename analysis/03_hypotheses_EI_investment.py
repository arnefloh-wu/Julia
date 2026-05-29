#!/usr/bin/env python3
"""Analysis block 3: EI and investment by founder gender.

H1: Participants with LOWER EI invest MORE in male-founded start-ups.
H2: Participants with HIGHER EI invest MORE in female-founded start-ups.

EI         = WLEIS total (mean of 16 items: SEA, OEA, UOE, ROE; 7-pt Likert).
Investment = invest_sv + invest_bu (0-6); team_gender is between-subjects, so
             this is investment in (male/female/mixed)-founded start-ups.
Tests: within-condition Pearson correlations (H1 male, H2 female) plus an
EI x gender interaction OLS (male+female). Descriptives via median-split chart.
"""
import csv, re, os, sys
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

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
i_isv, i_ibu = names.index('invest_sv'), names.index('invest_bu')
i_tg = names.index('team_gender')

def likert(v):
    m = re.match(r'\s*(\d+)', v.strip())
    return int(m.group(1)) if m else np.nan

EI = np.array([[likert(r[i]) for i in ei_cols] for r in data], float)
ei_total = EI.mean(axis=1)
invest = np.array([float(r[i_isv]) + float(r[i_ibu]) for r in data])
gender = np.array([r[i_tg] for r in data])

# ---- Cronbach's alpha (16-item EI) ----
k = EI.shape[1]
alpha = k / (k - 1) * (1 - EI.var(axis=0, ddof=1).sum() / EI.sum(axis=1).var(ddof=1))

print('=' * 70)
print(f'EI (WLEIS, 16 items): M = {ei_total.mean():.2f}, SD = {ei_total.std(ddof=1):.2f}, '
      f'Cronbach alpha = {alpha:.2f}')
print(f'Investment (invest_sv+invest_bu, 0-6): M = {invest.mean():.2f}, '
      f'SD = {invest.std(ddof=1):.2f}')
print('=' * 70)

def corr_block(label, mask, expected):
    x, y = ei_total[mask], invest[mask]
    r, p = stats.pearsonr(x, y)
    rho, pr = stats.spearmanr(x, y)
    print(f'\n{label} (n = {mask.sum()})  [expected: {expected}]')
    print(f'  invest: M = {y.mean():.2f}, SD = {y.std(ddof=1):.2f}')
    print(f'  Pearson  r = {r:+.3f}, p = {p:.3f}')
    print(f'  Spearman rho = {rho:+.3f}, p = {pr:.3f}')
    return r, p

print('\n### HYPOTHESIS TESTS (within-condition correlation of EI with investment)')
r_m, p_m = corr_block('H1  Male-founded', gender == 'male', 'negative r')
r_f, p_f = corr_block('H2  Female-founded', gender == 'female', 'positive r')
corr_block('(ref) Mixed', gender == 'mixed', 'n/a')
corr_block('(ref) Overall', np.ones(len(data), bool), 'n/a')

# ---- EI x gender interaction (male + female only) ----
mf = np.isin(gender, ['male', 'female'])
df = pd.DataFrame({'invest': invest[mf], 'EI': ei_total[mf], 'g': gender[mf]})
df['EI_c'] = df.EI - df.EI.mean()
df['female'] = (df.g == 'female').astype(int)
m = smf.ols('invest ~ EI_c * female', data=df).fit()
print('\n### EI x GENDER INTERACTION (OLS, male+female, EI centered)')
print(f'  EI slope in MALE cond.   b = {m.params["EI_c"]:+.3f}, '
      f'p = {m.pvalues["EI_c"]:.3f}   (H1)')
inter = m.params['EI_c:female']
print(f'  Interaction (slope diff) b = {inter:+.3f}, '
      f'p = {m.pvalues["EI_c:female"]:.3f}')
# female slope via linear combination
fem = smf.ols('invest ~ EI_c * C(g, Treatment("female"))', data=df).fit()
print(f'  EI slope in FEMALE cond. b = {fem.params["EI_c"]:+.3f}, '
      f'p = {fem.pvalues["EI_c"]:.3f}   (H2)')
print(f'  Model R^2 = {m.rsquared:.3f}')

# ---- descriptives: median split EI x condition ----
med = np.median(ei_total)
hi = ei_total >= med
print(f'\n### DESCRIPTIVES (median split EI at {med:.2f}; '
      f'Low n={(~hi).sum()}, High n={hi.sum()})')
conds = [('Male', 'male'), ('Female', 'female'), ('Mixed', 'mixed')]
low_means, high_means, low_se, high_se = [], [], [], []
print(f'{"Condition":10s} | {"EI":5s} | {"n":>3s} | {"M":>5s} | {"SD":>5s} | {"SE":>5s}')
for lbl, g in conds:
    for grp, label, ML, SL, EL in [((~hi), 'Low', low_means, None, low_se),
                                   ((hi), 'High', high_means, None, high_se)]:
        msk = (gender == g) & grp
        y = invest[msk]
        M, SD, SE = y.mean(), y.std(ddof=1), y.std(ddof=1) / np.sqrt(len(y))
        ML.append(M); EL.append(SE)
        print(f'{lbl:10s} | {label:5s} | {len(y):3d} | {M:5.2f} | {SD:5.2f} | {SE:5.2f}')

# ---- chart ----
labels = [c[0] for c in conds]
fig, ax = apa.grouped_bar_chart(
    labels,
    [('Low EI', low_means), ('High EI', high_means)],
    ylabel='Mean amount invested (0–6)',
    errors=[low_se, high_se],
    colors=['#D3D3D3', '#808080'],
)
apa.save(fig, os.path.join(HERE, 'figures', 'fig02_EI_investment'))
print('\nSaved figures/fig02_EI_investment.{png,pdf,svg}')
