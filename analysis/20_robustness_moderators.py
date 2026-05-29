#!/usr/bin/env python3
"""Analysis block 20: robustness checks for the 3 significant results.

Result 1: Industry effect  – SiteVision > BalanceUp (within-person, N=187)
Result 2: A vs B           – female/male-industry vs male/female-industry (t=3.34, p=.001)
Result 3: Low-EI congruence – low-EI masc-congruent > fem-congruent (one-tailed p=.032)

Moderators / controls:
  (a) Investment experience  Q23  (Ja/Nein)
  (b) Perceived success prob Q5 (SV) / Q47 (BU)  — 7-pt scale
  (c) Risk perception        Q6_1-3 (SV) / Q48_1-3 (BU) — 7-pt scale, mean per startup

For each result the script reports:
  * Result holds within each subgroup (experience split)
  * OLS with moderator as covariate / interaction term
  * Partial-correlation controlling for success and risk
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

def col(name): return names.index(name)
def cols_for(p): return [i for i, n in enumerate(names) if n.startswith(p) and '_DO' not in n]

likert = lambda v: int(re.match(r'\s*(\d+)', v.strip()).group(1))
arr = lambda c: np.array([likert(r[c]) for r in data], float)

i_sv, i_bu, i_tg = col('invest_sv'), col('invest_bu'), col('team_gender')
sv = np.array([float(r[i_sv]) for r in data])
bu = np.array([float(r[i_bu]) for r in data])
g  = np.array([r[i_tg] for r in data])
male, female = g == 'male', g == 'female'

# moderators
exp   = np.array([r[col('Q23')].strip() for r in data])
succ_sv = arr(col('Q5'))
succ_bu = arr(col('Q47'))
risk_sv = np.array([[likert(r[c]) for c in [col('Q6_1'), col('Q6_2'), col('Q6_3')]]
                    for r in data], float).mean(1)
risk_bu = np.array([[likert(r[c]) for c in [col('Q48_1'), col('Q48_2'), col('Q48_3')]]
                    for r in data], float).mean(1)

# EI for Result 3
ei_all = cols_for('Q10 (SEA)') + cols_for('Q11 (OEA)') + cols_for('Q12 (UOE)') + cols_for('Q13 (ROE)')
ei = np.array([[likert(r[i]) for i in ei_all] for r in data], float).mean(1)

star = lambda p: '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else 'ns'

sep = '=' * 76
print(sep)
print('ROBUSTNESS CHECKS – moderators: experience, success probability, risk')
print(sep)

# ───────────────────────────────────────────────────────────────
# RESULT 1: Industry effect  SV > BU  (within-person, all N=187)
# ───────────────────────────────────────────────────────────────
print('\n' + sep)
print('RESULT 1: SiteVision > BalanceUp industry effect')
print(sep)

d_ind = sv - bu  # positive = prefer SV

# (a) experience subgroups
print('\n(a) Investment experience subgroups:')
for lab, mask in [('Has exp (Ja)', exp == 'Ja'), ('No exp (Nein)', exp == 'Nein')]:
    sub = d_ind[mask]
    t, p = stats.ttest_1samp(sub, 0)
    print(f'  {lab:18s} n={mask.sum():3d}  SV-BU mean={sub.mean():+.3f}  '
          f't({mask.sum()-1})={t:.2f}  p={p:.3f}  {star(p)}')

# experience × industry interaction: OLS on long format
df_exp = pd.DataFrame({
    'invest': np.concatenate([sv, bu]),
    'industry': ['sv']*len(sv) + ['bu']*len(bu),
    'exp': np.tile(exp, 2)
})
df_exp = df_exp[df_exp.exp.isin(['Ja','Nein'])].copy()
m = smf.ols('invest ~ C(industry) * C(exp)', data=df_exp).fit()
ip = [k for k in m.pvalues.index if ':' in k][0]
print(f'\n  Interaction (industry × experience): b={m.params[ip]:+.3f}  p={m.pvalues[ip]:.3f}  {star(m.pvalues[ip])}')

# (b) controlling for success probability
print('\n(b) Partial correlation of (SV-BU) with success difference (succ_SV - succ_BU):')
succ_d = succ_sv - succ_bu
r, p = stats.pearsonr(d_ind, succ_d)
print(f'  r(invest-diff, succ-diff) = {r:+.3f}  p={p:.3f}  {star(p)}')
# ANCOVA: industry effect after controlling for success and risk
df_anc = pd.DataFrame({'d': d_ind, 'succ': succ_d, 'risk': risk_sv - risk_bu})
m2 = smf.ols('d ~ succ + risk', data=df_anc).fit()
# residual mean test
resid_mean = m2.resid.mean()
t_r, p_r = stats.ttest_1samp(m2.resid, 0)
print(f'  Industry gap after controlling success+risk:  '
      f'residual mean={resid_mean:+.3f}  t={t_r:.2f}  p={p_r:.3f}  {star(p_r)}')

# (c) success and risk as covariates in long-format model
print('\n(c) OLS with success prob and risk as covariates:')
df_long = pd.DataFrame({
    'invest': np.concatenate([sv, bu]),
    'industry': [1]*len(sv) + [0]*len(bu),
    'succ': np.concatenate([succ_sv, succ_bu]),
    'risk': np.concatenate([risk_sv, risk_bu])
})
m3 = smf.ols('invest ~ industry + succ + risk', data=df_long).fit()
print(f'  industry coef={m3.params["industry"]:+.3f}  p={m3.pvalues["industry"]:.3f}  {star(m3.pvalues["industry"])}')
print(f'  succ coef    ={m3.params["succ"]:+.3f}  p={m3.pvalues["succ"]:.3f}  {star(m3.pvalues["succ"])}')
print(f'  risk coef    ={m3.params["risk"]:+.3f}  p={m3.pvalues["risk"]:.3f}  {star(m3.pvalues["risk"])}')

# ───────────────────────────────────────────────────────────────
# RESULT 2: A vs B  (female/male-industry vs male/female-industry)
# ───────────────────────────────────────────────────────────────
print('\n' + sep)
print('RESULT 2: A (female founder / male industry) vs B (male founder / female industry)')
print(sep)

A_mask, B_mask = female, male
A, B = sv[A_mask], bu[B_mask]
# moderator arrays aligned to A and B groups
expA, expB = exp[A_mask], exp[B_mask]
succA, succB = succ_sv[A_mask], succ_bu[B_mask]
riskA, riskB = risk_sv[A_mask], risk_bu[B_mask]

# (a) experience subgroups
print('\n(a) Investment experience subgroups:')
for lab, mA, mB in [('Has exp (Ja)', expA == 'Ja', expB == 'Ja'),
                    ('No exp (Nein)', expA == 'Nein', expB == 'Nein')]:
    a_s, b_s = A[mA], B[mB]
    if len(a_s) < 2 or len(b_s) < 2:
        print(f'  {lab}: too few observations'); continue
    t, p = stats.ttest_ind(a_s, b_s, equal_var=False)
    print(f'  {lab:18s}  A n={len(a_s)} M={a_s.mean():.2f}  '
          f'B n={len(b_s)} M={b_s.mean():.2f}  '
          f't={t:.2f}  p={p:.3f}  {star(p)}')

# experience × group interaction in OLS
df_ab = pd.DataFrame({'invest': np.concatenate([A, B]),
                      'group': ['A']*len(A) + ['B']*len(B),
                      'exp': np.concatenate([expA, expB])})
df_ab = df_ab[df_ab.exp.isin(['Ja','Nein'])].copy()
m = smf.ols('invest ~ C(group) * C(exp)', data=df_ab).fit()
ip = [k for k in m.pvalues.index if ':' in k][0]
print(f'\n  Interaction (group × experience): b={m.params[ip]:+.3f}  p={m.pvalues[ip]:.3f}  {star(m.pvalues[ip])}')

# (b) controlling for success probability
print('\n(b) OLS A vs B controlling for perceived success:')
df_ab2 = pd.DataFrame({'invest': np.concatenate([A, B]),
                       'group': [1]*len(A) + [0]*len(B),
                       'succ': np.concatenate([succA, succB]),
                       'risk': np.concatenate([riskA, riskB])})
m4 = smf.ols('invest ~ group + succ + risk', data=df_ab2).fit()
print(f'  group coef (A vs B) = {m4.params["group"]:+.3f}  p={m4.pvalues["group"]:.3f}  {star(m4.pvalues["group"])}')
print(f'  succ coef           = {m4.params["succ"]:+.3f}  p={m4.pvalues["succ"]:.3f}  {star(m4.pvalues["succ"])}')
print(f'  risk coef           = {m4.params["risk"]:+.3f}  p={m4.pvalues["risk"]:.3f}  {star(m4.pvalues["risk"])}')

# (c) success difference A vs B (are they rated differently?)
print('\n(c) Success/risk perception: A vs B comparison (potential confound check):')
t_s, p_s = stats.ttest_ind(succA, succB, equal_var=False)
t_r2, p_r2 = stats.ttest_ind(riskA, riskB, equal_var=False)
print(f'  Success: A M={succA.mean():.2f} vs B M={succB.mean():.2f}  t={t_s:.2f}  p={p_s:.3f}  {star(p_s)}')
print(f'  Risk:    A M={riskA.mean():.2f} vs B M={riskB.mean():.2f}  t={t_r2:.2f}  p={p_r2:.3f}  {star(p_r2)}')
print('  (If success/risk differ between A and B, they may partly explain the investment gap.)')

# ───────────────────────────────────────────────────────────────
# RESULT 3: Low-EI masc-congruent > fem-congruent
# ───────────────────────────────────────────────────────────────
print('\n' + sep)
print('RESULT 3: Low-EI masculine-congruent > feminine-congruent investment')
print(sep)

med_ei = np.median(ei)
low_ei = ei < med_ei
masc = sv[(g == 'male') & low_ei]
fem  = bu[(g == 'female') & low_ei]
masc_exp = exp[(g == 'male') & low_ei]
fem_exp  = exp[(g == 'female') & low_ei]
masc_succ = succ_sv[(g == 'male') & low_ei]
fem_succ  = succ_bu[(g == 'female') & low_ei]
masc_risk = risk_sv[(g == 'male') & low_ei]
fem_risk  = risk_bu[(g == 'female') & low_ei]

# (a) experience subgroups
print('\n(a) Investment experience subgroups (low-EI only):')
for lab, mmask, fmask in [('Has exp (Ja)', masc_exp == 'Ja', fem_exp == 'Ja'),
                           ('No exp (Nein)', masc_exp == 'Nein', fem_exp == 'Nein')]:
    ms, fs = masc[mmask], fem[fmask]
    if len(ms) < 2 or len(fs) < 2:
        print(f'  {lab}: too few observations'); continue
    t, p2 = stats.ttest_ind(ms, fs, equal_var=False)
    p1 = p2/2 if t > 0 else 1 - p2/2
    print(f'  {lab:18s}  masc n={len(ms)} M={ms.mean():.2f}  '
          f'fem n={len(fs)} M={fs.mean():.2f}  '
          f't={t:.2f}  p1={p1:.3f}  {star(p1)}')

# (b) success and risk as covariates
print('\n(b) OLS masc vs fem (low-EI) controlling for success and risk:')
df_c = pd.DataFrame({'invest': np.concatenate([masc, fem]),
                     'type': [1]*len(masc) + [0]*len(fem),
                     'succ': np.concatenate([masc_succ, fem_succ]),
                     'risk': np.concatenate([masc_risk, fem_risk])})
m5 = smf.ols('invest ~ type + succ + risk', data=df_c).fit()
print(f'  type coef (masc vs fem) = {m5.params["type"]:+.3f}  p={m5.pvalues["type"]:.3f}  {star(m5.pvalues["type"])}')
print(f'  succ coef               = {m5.params["succ"]:+.3f}  p={m5.pvalues["succ"]:.3f}  {star(m5.pvalues["succ"])}')
print(f'  risk coef               = {m5.params["risk"]:+.3f}  p={m5.pvalues["risk"]:.3f}  {star(m5.pvalues["risk"])}')

# (c) does success/risk mediate? compare masc vs fem on these perceptions
print('\n(c) Do low-EI participants perceive masc/fem startups differently?')
t_sm, p_sm = stats.ttest_ind(masc_succ, fem_succ, equal_var=False)
t_rm, p_rm = stats.ttest_ind(masc_risk, fem_risk, equal_var=False)
print(f'  Success: masc M={masc_succ.mean():.2f} vs fem M={fem_succ.mean():.2f}  t={t_sm:.2f}  p={p_sm:.3f}  {star(p_sm)}')
print(f'  Risk:    masc M={masc_risk.mean():.2f} vs fem M={fem_risk.mean():.2f}  t={t_rm:.2f}  p={p_rm:.3f}  {star(p_rm)}')

print('\n' + sep)
print('Done.')
