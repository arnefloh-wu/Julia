#!/usr/bin/env python3
"""Analysis block 28: formal pitch-order control + effect x order interaction
for the three storyline results. Quantifies how much of each effect survives
adjustment for presentation order.

R1 industry (SV vs BU, within-person)  -> mixed model proxy via order covariate
R2 congruity (A vs B, between)          -> invest ~ group * order
R3 low-EI congruence (masc vs fem)      -> invest ~ masc * order  (low-EI subset)
"""
import csv, re, os
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'MasterThesis_cleaned.csv')
with open(SRC, newline='') as f:
    rows = list(csv.reader(f))
names, data = rows[0], rows[3:]
col = lambda n: names.index(n)
def cols_for(p): return [i for i, n in enumerate(names) if n.startswith(p) and '_DO' not in n]
likert = lambda v: int(re.match(r'\s*(\d+)', v.strip()).group(1))
mat = lambda cs: np.array([[likert(r[c]) for c in cs] for r in data], float).mean(1)

sv = np.array([float(r[col('invest_sv')]) for r in data])
bu = np.array([float(r[col('invest_bu')]) for r in data])
g = np.array([r[col('team_gender')] for r in data])
order = np.array([r[col('pitch_order')].strip() for r in data])
male, female = g == 'male', g == 'female'
ei = mat(cols_for('Q10 (SEA)') + cols_for('Q11 (OEA)') + cols_for('Q12 (UOE)') + cols_for('Q13 (ROE)'))
star = lambda p: '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else 'ns'
sep = '=' * 80

# ───────────────────────────────────────────────────────────
# R1: long-format, industry x order interaction with subject clustering
# ───────────────────────────────────────────────────────────
print(sep); print('R1  Industry effect with pitch-order control + interaction'); print(sep)
N = len(data)
long = pd.DataFrame({
    'invest': np.concatenate([sv, bu]),
    'industry': [1]*N + [0]*N,                       # 1=SiteVision
    'order_svfirst': np.tile((order == 'sv_first').astype(int), 2),
    'subj': list(range(N)) * 2,
})
# main: industry controlling order
m_main = smf.ols('invest ~ industry + order_svfirst', data=long).fit(
    cov_type='cluster', cov_kwds={'groups': long['subj']})
print(f'  Industry (order-adjusted): b={m_main.params["industry"]:+.3f}  '
      f'p={m_main.pvalues["industry"]:.3f}  {star(m_main.pvalues["industry"])}')
# interaction
m_int = smf.ols('invest ~ industry * order_svfirst', data=long).fit(
    cov_type='cluster', cov_kwds={'groups': long['subj']})
ib, ip = m_int.params['industry:order_svfirst'], m_int.pvalues['industry:order_svfirst']
print(f'  Industry x order interaction: b={ib:+.3f}  p={ip:.3g}  {star(ip)}')
print(f'    -> SV-first simple effect: {m_int.params["industry"] + ib:+.3f}')
print(f'    -> BU-first simple effect: {m_int.params["industry"]:+.3f}')
print('  (Large interaction => the industry preference is largely an order/anchoring effect.)')

# ───────────────────────────────────────────────────────────
# R2: A vs B with order
# ───────────────────────────────────────────────────────────
print('\n' + sep); print('R2  Congruity (A vs B) with pitch-order control + interaction'); print(sep)
A_mask, B_mask = female, male
invest = np.concatenate([sv[A_mask], bu[B_mask]])
grp = np.concatenate([np.ones(A_mask.sum()), np.zeros(B_mask.sum())])  # 1=A
# A saw SV-first? for A the focal is SV; for B focal is BU. Use raw order var.
ord_ab = np.concatenate([(order[A_mask] == 'sv_first').astype(int),
                         (order[B_mask] == 'sv_first').astype(int)])
df2 = pd.DataFrame({'invest': invest, 'group': grp, 'svfirst': ord_ab})
m2_main = smf.ols('invest ~ group + svfirst', data=df2).fit()
print(f'  Group A-vs-B (order-adjusted): b={m2_main.params["group"]:+.3f}  '
      f'p={m2_main.pvalues["group"]:.3f}  {star(m2_main.pvalues["group"])}')
m2_int = smf.ols('invest ~ group * svfirst', data=df2).fit()
ib2, ip2 = m2_int.params['group:svfirst'], m2_int.pvalues['group:svfirst']
print(f'  Group x order interaction: b={ib2:+.3f}  p={ip2:.3g}  {star(ip2)}')

# ───────────────────────────────────────────────────────────
# R3: low-EI masc vs fem with order
# ───────────────────────────────────────────────────────────
print('\n' + sep); print('R3  Low-EI congruence (masc vs fem) with pitch-order control + interaction'); print(sep)
med = np.median(ei); low = ei < med
mm = (g == 'male') & low; fm = (g == 'female') & low
invest3 = np.concatenate([sv[mm], bu[fm]])
masc = np.concatenate([np.ones(mm.sum()), np.zeros(fm.sum())])
ord3 = np.concatenate([(order[mm] == 'sv_first').astype(int),
                       (order[fm] == 'sv_first').astype(int)])
df3 = pd.DataFrame({'invest': invest3, 'masc': masc, 'svfirst': ord3})
m3_main = smf.ols('invest ~ masc + svfirst', data=df3).fit()
print(f'  Masc-vs-fem (order-adjusted): b={m3_main.params["masc"]:+.3f}  '
      f'p={m3_main.pvalues["masc"]:.3f}  {star(m3_main.pvalues["masc"])}')
m3_int = smf.ols('invest ~ masc * svfirst', data=df3).fit()
ib3, ip3 = m3_int.params['masc:svfirst'], m3_int.pvalues['masc:svfirst']
print(f'  Masc x order interaction: b={ib3:+.3f}  p={ip3:.3g}  {star(ip3)}')

print('\n' + sep)
print('SUMMARY: effect sizes before vs after order adjustment')
print(sep)
print(f'  R1 industry:   raw +0.481 (p<.001)  ->  order-adj b={m_main.params["industry"]:+.3f} ({star(m_main.pvalues["industry"])})')
print(f'  R2 A vs B:     raw +0.54  (p=.001)  ->  order-adj b={m2_main.params["group"]:+.3f} ({star(m2_main.pvalues["group"])})')
print(f'  R3 low-EI:     raw +0.46  (p=.032)  ->  order-adj b={m3_main.params["masc"]:+.3f} ({star(m3_main.pvalues["masc"])})')
