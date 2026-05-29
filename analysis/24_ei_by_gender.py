#!/usr/bin/env python3
"""Analysis block 24: is EI affected by participant gender, and does it
survive controlling for age and field of study?

Participant gender = Q16; age = Q17; field = Q21 (STEM vs non-STEM grouping).
Reports Welch t-tests (raw) and OLS with age + STEM covariates.
"""
import csv, re, os, sys
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'MasterThesis_cleaned.csv')
with open(SRC, newline='') as f:
    rows = list(csv.reader(f))
names, data = rows[0], rows[3:]
def cols(p): return [i for i, n in enumerate(names) if n.startswith(p) and '_DO' not in n]
DIMS = {'SEA': cols('Q10 (SEA)'), 'OEA': cols('Q11 (OEA)'),
        'UOE': cols('Q12 (UOE)'), 'ROE': cols('Q13 (ROE)')}
lik = lambda v: int(re.match(r'\s*(\d+)', v.strip()).group(1))
sc = lambda c: np.array([[lik(r[i]) for i in c] for r in data], float).mean(1)
EI = {k: sc(v) for k, v in DIMS.items()}; EI['Total'] = sc(sum(DIMS.values(), []))

i16, i17, i21 = names.index('Q16'), names.index('Q17'), names.index('Q21')
resp = np.array([r[i16].strip() for r in data])
def age_of(r):
    m = re.search(r'\d+', r[i17])
    return float(m.group()) if m else np.nan
age = np.array([age_of(r) for r in data])
STEM = {'Naturwissenschaften', 'Wirtschaftsinformatik',
        'Ingenieurwesen / Technische Wissenschaften', 'Informatik'}
stem = np.array([1 if r[i21].strip() in STEM else 0 for r in data])

star = lambda p: '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else 'ns'
m = resp == 'Männlich'; w = resp == 'Weiblich'
order = ['Total', 'SEA', 'OEA', 'UOE', 'ROE']

print('=' * 78)
print(f'EI by participant gender  (Male n={m.sum()}, Female n={w.sum()})')
print('=' * 78)
print(f'{"Dim":6s} | {"raw t":>7s} {"p":>7s} {"d":>6s} | {"adj. gender b":>13s} {"p":>7s}  (controls: age, STEM)')
mw = m | w
df = pd.DataFrame({'female': w[mw].astype(int), 'age': age[mw], 'stem': stem[mw]})
for k in order:
    a, b = EI[k][m], EI[k][w]
    t, p = stats.ttest_ind(a, b, equal_var=False)
    sp = np.sqrt(((len(a)-1)*a.var(ddof=1)+(len(b)-1)*b.var(ddof=1))/(len(a)+len(b)-2))
    d = (a.mean()-b.mean())/sp
    df['ei'] = EI[k][mw]
    mod = smf.ols('ei ~ female + age + stem', data=df.dropna()).fit()
    bb, pp = mod.params['female'], mod.pvalues['female']
    print(f'{k:6s} | {t:+7.2f} {p:7.3f} {d:+6.2f} | {bb:+13.3f} {pp:7.3f}{star(pp):>3s}')
print('\nadj. gender b = female-minus-male EI difference after controlling age + STEM field.')
print('(positive b = women higher.)  Covariate context:')
# covariate balance
print(f'  Age: male M={np.nanmean(age[m]):.1f} vs female M={np.nanmean(age[w]):.1f}')
print(f'  STEM share: male {stem[m].mean()*100:.0f}% vs female {stem[w].mean()*100:.0f}%')
