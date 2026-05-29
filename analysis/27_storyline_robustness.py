#!/usr/bin/env python3
"""Analysis block 27: comprehensive robustness battery for the storyline results.

Storyline results
  R1  Industry effect:    SiteVision > BalanceUp (within-person, N=187)
  R2  Congruity (A vs B):  female/male-industry vs male/female-industry (p=.001)
  R3  Low-EI congruence:   low-EI masc-congruent > fem-congruent (one-tailed p=.032)

Robustness levers
  (1) Expected success      Q5 (SV), Q47 (BU)            7-pt
  (2) Startup risk assess.  Q6_1-3 (SV), Q48_1-3 (BU)    7-pt, mean
  (3) Risk trait            Q14 general, Q15 financial   1-10 (Dohmen)
  (4) Pitch order           sv_first vs bu_first
  (5) Attention             drop fastest 5% by Duration
  (6) Entrepreneurial exp.  Q24 (Ja/Nein)
  (7) Competence ratings    Q9_1-6 (SV), Q49_1-6 (BU)    alt. perceptual covariate
Each result is re-estimated with covariates / within subgroups / after exclusions.
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
arr = lambda c: np.array([likert(r[c]) for r in data], float)
mat = lambda cs: np.array([[likert(r[c]) for c in cs] for r in data], float).mean(1)

sv = np.array([float(r[col('invest_sv')]) for r in data])
bu = np.array([float(r[col('invest_bu')]) for r in data])
g = np.array([r[col('team_gender')] for r in data])
male, female = g == 'male', g == 'female'

# moderators / covariates
succ_sv, succ_bu = arr(col('Q5')), arr(col('Q47'))
risk_sv = mat([col('Q6_1'), col('Q6_2'), col('Q6_3')])
risk_bu = mat([col('Q48_1'), col('Q48_2'), col('Q48_3')])
comp_sv = mat([col(f'Q9_{i}') for i in range(1, 7)])
comp_bu = mat([col(f'Q49_{i}') for i in range(1, 7)])
risk_gen, risk_fin = arr(col('Q14')), arr(col('Q15'))
ent_exp = np.array([r[col('Q24')].strip() for r in data])
order = np.array([r[col('pitch_order')].strip() for r in data])
dur = np.array([float(r[col('Duration (in seconds)')]) for r in data])
ei_cols = cols_for('Q10 (SEA)') + cols_for('Q11 (OEA)') + cols_for('Q12 (UOE)') + cols_for('Q13 (ROE)')
ei = mat(ei_cols)

star = lambda p: '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else 'ns'
keep_fast = dur >= np.percentile(dur, 5)   # attention filter
sep = '=' * 80

# ════════════════════════════════════════════════════════════
print(sep); print('R1  INDUSTRY EFFECT  (SiteVision > BalanceUp)'); print(sep)
d_ind = sv - bu
t0, p0 = stats.ttest_rel(sv, bu)
print(f'  Baseline paired t={t0:.2f}, p={p0:.2e}, mean diff={d_ind.mean():+.3f}')

# covariate-adjusted: regress invest on industry + each control set (long format)
def long_model(extra_cols, formula_extra):
    base = {'invest': np.concatenate([sv, bu]),
            'industry': [1]*len(sv) + [0]*len(bu)}
    for nm, (a, b) in extra_cols.items():
        base[nm] = np.concatenate([a, b])
    df = pd.DataFrame(base)
    return smf.ols(f'invest ~ industry {formula_extra}', data=df).fit()

print('\n  Industry coefficient after adding covariates (long format, per-startup):')
specs = [
    ('+ success',            {'succ': (succ_sv, succ_bu)},                 '+ succ'),
    ('+ startup risk',       {'risk': (risk_sv, risk_bu)},                 '+ risk'),
    ('+ competence',         {'comp': (comp_sv, comp_bu)},                 '+ comp'),
    ('+ success+risk+comp',  {'succ': (succ_sv, succ_bu), 'risk': (risk_sv, risk_bu),
                              'comp': (comp_sv, comp_bu)},                 '+ succ + risk + comp'),
]
for lab, ec, fx in specs:
    m = long_model(ec, fx)
    b, p = m.params['industry'], m.pvalues['industry']
    print(f'    {lab:22s}: industry b={b:+.3f}  p={p:.3f}  {star(p)}')

# risk-trait moderation (between-person trait on within-person diff)
print('\n  Risk-trait moderation of the industry preference (d = SV-BU):')
for nm, x in [('general risk (Q14)', risk_gen), ('financial risk (Q15)', risk_fin)]:
    df = pd.DataFrame({'d': d_ind, 'x': x - x.mean()})
    m = smf.ols('d ~ x', data=df).fit()
    print(f'    {nm:22s}: slope b={m.params["x"]:+.3f}  p={m.pvalues["x"]:.3f}  {star(m.pvalues["x"])}')

# pitch order + attention + entrepreneurial subgroups
print('\n  Subgroup / exclusion robustness (paired t on SV-BU):')
def paired_sub(mask, lab):
    a, b = sv[mask], bu[mask]
    t, p = stats.ttest_rel(a, b)
    print(f'    {lab:26s} n={mask.sum():3d}  diff={ (a-b).mean():+.3f}  t={t:.2f}  p={p:.3g}  {star(p)}')
paired_sub(order == 'sv_first', 'SV shown first')
paired_sub(order == 'bu_first', 'BU shown first')
paired_sub(keep_fast, 'attention filter (drop 5%)')
paired_sub(ent_exp == 'Ja', 'has founded a company')
paired_sub(ent_exp == 'Nein', 'never founded')

# ════════════════════════════════════════════════════════════
print('\n' + sep); print('R2  CONGRUITY  A (female/male-ind) vs B (male/female-ind)'); print(sep)
A_mask, B_mask = female, male
def r2_test(extra_mask=None, lab='baseline'):
    am = A_mask & (extra_mask if extra_mask is not None else True)
    bm = B_mask & (extra_mask if extra_mask is not None else True)
    A, B = sv[am], bu[bm]
    if len(A) < 2 or len(B) < 2:
        print(f'    {lab}: too few'); return
    t, p = stats.ttest_ind(A, B, equal_var=False)
    print(f'    {lab:26s} A n={len(A):2d} M={A.mean():.2f}  B n={len(B):2d} M={B.mean():.2f}  '
          f't={t:.2f}  p={p:.3g}  {star(p)}')
print(f'  Baseline:')
r2_test(None, 'A vs B (full)')

# covariate-adjusted OLS A vs B
print('\n  A vs B group coefficient after covariates:')
def r2_cov(cov):
    A_idx = np.where(A_mask)[0]; B_idx = np.where(B_mask)[0]
    invest = np.concatenate([sv[A_mask], bu[B_mask]])
    grp = np.concatenate([np.ones(A_mask.sum()), np.zeros(B_mask.sum())])
    base = {'invest': invest, 'group': grp}
    for nm, full in cov.items():
        base[nm] = np.concatenate([full[A_mask], full[B_mask]])
    df = pd.DataFrame(base)
    f = 'invest ~ group + ' + ' + '.join(k for k in cov)
    m = smf.ols(f, data=df).fit()
    return m.params['group'], m.pvalues['group']
# build per-group covariate values: for A use SV-side perception, for B use BU-side
def side(full_sv, full_bu):  # value for the focal startup each group saw
    v = np.empty(len(data)); v[A_mask] = full_sv[A_mask]; v[B_mask] = full_bu[B_mask]; return v
succ_f = side(succ_sv, succ_bu); risk_f = side(risk_sv, risk_bu); comp_f = side(comp_sv, comp_bu)
for lab, cov in [('+ success', {'succ': succ_f}),
                 ('+ startup risk', {'risk': risk_f}),
                 ('+ competence', {'comp': comp_f}),
                 ('+ risk trait', {'rg': risk_gen, 'rf': risk_fin}),
                 ('+ all', {'succ': succ_f, 'risk': risk_f, 'comp': comp_f,
                            'rg': risk_gen, 'rf': risk_fin})]:
    b, p = r2_cov(cov)
    print(f'    {lab:22s}: group b={b:+.3f}  p={p:.3f}  {star(p)}')

print('\n  Subgroup / exclusion robustness:')
r2_test(order == 'sv_first', 'SV first')
r2_test(order == 'bu_first', 'BU first')
r2_test(keep_fast, 'attention filter')
r2_test(ent_exp == 'Nein', 'never founded')

# ════════════════════════════════════════════════════════════
print('\n' + sep); print('R3  LOW-EI CONGRUENCE  (masc-congruent > fem-congruent)'); print(sep)
med = np.median(ei); low = ei < med
def r3_test(extra_mask, lab):
    mm = (g == 'male') & low & extra_mask
    fm = (g == 'female') & low & extra_mask
    ms, fs = sv[mm], bu[fm]
    if len(ms) < 2 or len(fs) < 2:
        print(f'    {lab}: too few'); return
    t, p2 = stats.ttest_ind(ms, fs, equal_var=False)
    p1 = p2/2 if t > 0 else 1 - p2/2
    print(f'    {lab:26s} masc n={len(ms):2d} M={ms.mean():.2f}  fem n={len(fs):2d} M={fs.mean():.2f}  '
          f't={t:.2f}  p1={p1:.3g}  {star(p1)}')
allmask = np.ones(len(data), bool)
print('  Baseline:'); r3_test(allmask, 'low-EI masc vs fem')

# covariate-adjusted OLS within low-EI
print('\n  Masc-vs-fem (low-EI) coefficient after covariates:')
mm = (g == 'male') & low; fm = (g == 'female') & low
def r3_cov(cov):
    invest = np.concatenate([sv[mm], bu[fm]])
    typ = np.concatenate([np.ones(mm.sum()), np.zeros(fm.sum())])
    base = {'invest': invest, 'masc': typ}
    for nm, (a, b) in cov.items():
        base[nm] = np.concatenate([a[mm], b[fm]])
    df = pd.DataFrame(base)
    f = 'invest ~ masc + ' + ' + '.join(cov)
    m = smf.ols(f, data=df).fit()
    return m.params['masc'], m.pvalues['masc']
for lab, cov in [('+ success', {'succ': (succ_sv, succ_bu)}),
                 ('+ startup risk', {'risk': (risk_sv, risk_bu)}),
                 ('+ competence', {'comp': (comp_sv, comp_bu)}),
                 ('+ risk trait', {'rg': (risk_gen, risk_gen), 'rf': (risk_fin, risk_fin)}),
                 ('+ all', {'succ': (succ_sv, succ_bu), 'risk': (risk_sv, risk_bu),
                            'comp': (comp_sv, comp_bu), 'rg': (risk_gen, risk_gen),
                            'rf': (risk_fin, risk_fin)})]:
    b, p = r3_cov(cov)
    print(f'    {lab:22s}: masc b={b:+.3f}  p={p:.3f}  {star(p)}')

print('\n  Subgroup / exclusion robustness:')
r3_test(order == 'sv_first', 'SV first')
r3_test(order == 'bu_first', 'BU first')
r3_test(keep_fast, 'attention filter')
r3_test(ent_exp == 'Nein', 'never founded')
# low-EI defined by bottom tertile (alt. operationalisation)
t1 = np.quantile(ei, 1/3); low2 = ei <= t1
def r3_tertile():
    ms = sv[(g == 'male') & low2]; fs = bu[(g == 'female') & low2]
    t, p2 = stats.ttest_ind(ms, fs, equal_var=False); p1 = p2/2 if t > 0 else 1-p2/2
    print(f'    {"low-EI = bottom tertile":26s} masc n={len(ms):2d} M={ms.mean():.2f}  '
          f'fem n={len(fs):2d} M={fs.mean():.2f}  t={t:.2f}  p1={p1:.3g}  {star(p1)}')
r3_tertile()

print('\n' + sep); print('Done.')
