#!/usr/bin/env python3
"""Analysis block 23: extended hypotheses H7-H9, linked to the 3 core results.

Core results recap:
  R1 industry effect (SV>BU); R2 congruity advantage (A vs B, p=.001);
  R3 low-EI masculine-congruence preference (p=.032).

H7  The EI moderation of the congruity preference (R3) is driven specifically
    by SEA (self-emotion appraisal), controlling for OEA/UOE/ROE.
H8  EI's moderation of the gender-based investment gap is stronger among MALE
    than FEMALE participants  (EI x founder-gender x participant-gender).
H9  Female-founded startups receive lower WARMTH ratings than male-founded ones,
    and this warmth deficit MEDIATES the investment gap among low-EI participants.

Warmth = mean(Q9_7..Q9_12 / Q49_7..Q49_12); Competence = mean(Q9_1..6 / Q49_1..6).
Founder gender is between-subjects (condition). Mixed excluded for H7-H9.
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
def cols_for(p): return [i for i, n in enumerate(names) if n.startswith(p) and '_DO' not in n]
DIMS = {'SEA': cols_for('Q10 (SEA)'), 'OEA': cols_for('Q11 (OEA)'),
        'UOE': cols_for('Q12 (UOE)'), 'ROE': cols_for('Q13 (ROE)')}
likert = lambda v: int(re.match(r'\s*(\d+)', v.strip()).group(1))
sc = lambda c: np.array([[likert(r[i]) for i in c] for r in data], float).mean(1)

i_sv, i_bu, i_tg, i_g16 = (names.index('invest_sv'), names.index('invest_bu'),
                           names.index('team_gender'), names.index('Q16'))
sv = np.array([float(r[i_sv]) for r in data]); bu = np.array([float(r[i_bu]) for r in data])
g = np.array([r[i_tg] for r in data])
resp = np.array([r[i_g16].strip() for r in data])

# warmth / competence (items 7-12 vs 1-6)
def items(prefix, idx): return [names.index(f'{prefix}_{i}') for i in idx]
warm_sv = sc(items('Q9', range(7, 13))); warm_bu = sc(items('Q49', range(7, 13)))
comp_sv = sc(items('Q9', range(1, 7)));  comp_bu = sc(items('Q49', range(1, 7)))

EI = {k: sc(c) for k, c in DIMS.items()}
EI['Total'] = sc(sum(DIMS.values(), []))
star = lambda p: '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else 'ns'
sep = '=' * 80

male, female = g == 'male', g == 'female'
mf = male | female

# ── congruity dataset (focal = congruent startup) ──
# masculine-congruent = SV for male condition; feminine-congruent = BU for female cond
focal   = np.where(male, sv, bu)[mf]
focal_w = np.where(male, warm_sv, warm_bu)[mf]
focal_c = np.where(male, comp_sv, comp_bu)[mf]
typ     = np.where(male[mf], 1, 0)          # 1=masc-congruent, 0=fem-congruent
cong = pd.DataFrame({'invest': focal, 'warm': focal_w, 'comp': focal_c, 'masc': typ,
                     'resp': resp[mf]})
for k in EI: cong[k] = EI[k][mf]

# ═══════════════════════════════════════════════════════════════
# H7: is the EI moderation of congruity driven by SEA, net of others?
# ═══════════════════════════════════════════════════════════════
print(sep); print('H7  SEA-specific moderation of the congruity preference (R3)'); print(sep)
# center EI dims
d2 = cong.copy()
for k in ['SEA', 'OEA', 'UOE', 'ROE']:
    d2[k + 'c'] = d2[k] - d2[k].mean()
# full model: invest ~ masc * (SEA+OEA+UOE+ROE)
m = smf.ols('invest ~ masc * (SEAc + OEAc + UOEc + ROEc)', data=d2).fit()
print('Interaction terms (masc x dimension) — H7: only masc:SEAc significant & negative')
print(f'{"term":14s} {"b":>9s} {"p":>8s}')
for k in ['SEAc', 'OEAc', 'UOEc', 'ROEc']:
    t = f'masc:{k}'
    print(f'{t:14s} {m.params[t]:+9.3f} {m.pvalues[t]:8.3f}  {star(m.pvalues[t])}')
# simple single-dim moderation for comparison
print('\nFor comparison — single-predictor moderation (each dim alone):')
for k in ['SEA', 'OEA', 'UOE', 'ROE']:
    dd = cong.copy(); dd['xc'] = dd[k] - dd[k].mean()
    mm = smf.ols('invest ~ masc * xc', data=dd).fit()
    print(f'  {k}: masc:xc b={mm.params["masc:xc"]:+.3f}  p={mm.pvalues["masc:xc"]:.3f}  {star(mm.pvalues["masc:xc"])}')

# ═══════════════════════════════════════════════════════════════
# H8: EI x gender-gap moderation stronger for MALE participants
# ═══════════════════════════════════════════════════════════════
print('\n' + sep); print('H8  EI x founder-gender x PARTICIPANT-gender (three-way)'); print(sep)
total = (sv + bu)                      # capital to founder team (0-6)
dh8 = pd.DataFrame({'tot': total[mf], 'male_found': male[mf].astype(int),
                    'resp': resp[mf]})
dh8['EIc'] = EI['Total'][mf] - EI['Total'][mf].mean()
dh8 = dh8[dh8.resp.isin(['Männlich', 'Weiblich'])].copy()
dh8['p_male'] = (dh8.resp == 'Männlich').astype(int)
m8 = smf.ols('tot ~ EIc * male_found * p_male', data=dh8).fit()
three = 'EIc:male_found:p_male'
print(f'  Three-way {three}:')
print(f'    b={m8.params[three]:+.3f}  p={m8.pvalues[three]:.3f}  {star(m8.pvalues[three])}')
# simple EI x founder-gender slopes within each participant gender
print('\n  EI x founder-gender interaction WITHIN each participant gender:')
for lab, val in [('Male participants', 'Männlich'), ('Female participants', 'Weiblich')]:
    sub = dh8[dh8.resp == val]
    ms = smf.ols('tot ~ EIc * male_found', data=sub).fit()
    n = len(sub)
    print(f'    {lab:20s} (n={n}): EIc:male_found b={ms.params["EIc:male_found"]:+.3f}  '
          f'p={ms.pvalues["EIc:male_found"]:.3f}  {star(ms.pvalues["EIc:male_found"])}')

# ═══════════════════════════════════════════════════════════════
# H9: warmth deficit for female-founded; mediation among low-EI
# ═══════════════════════════════════════════════════════════════
print('\n' + sep); print('H9  Warmth deficit + mediation of investment gap (low-EI)'); print(sep)
# Step A: do female-founded teams get lower warmth than male-founded?
warm_team = np.where(male, (warm_sv + warm_bu) / 2, (warm_sv + warm_bu) / 2)  # team warmth both pitches
wm = ((warm_sv + warm_bu) / 2)
tw, pw = stats.ttest_ind(wm[male], wm[female], equal_var=False)
print(f'  Warmth: male-founded M={wm[male].mean():.2f} vs female-founded M={wm[female].mean():.2f}  '
      f't={tw:.2f}  p={pw:.3f}  {star(pw)}')
cw_m, cw_f = ((comp_sv+comp_bu)/2)[male], ((comp_sv+comp_bu)/2)[female]
tc, pc = stats.ttest_ind(cw_m, cw_f, equal_var=False)
print(f'  Competence: male M={cw_m.mean():.2f} vs female M={cw_f.mean():.2f}  '
      f't={tc:.2f}  p={pc:.3f}  {star(pc)}')
print('  (H9 predicts female-founded < male-founded on warmth; positive t = male higher.)')

# Step B: mediation among low-EI (median split on Total EI, full sample)
med = np.median(EI['Total'])
low = EI['Total'] < med
lowmf = low & mf
X = male[lowmf].astype(int)              # 1=male founder, 0=female founder
M = ((warm_sv + warm_bu) / 2)[lowmf]     # warmth (mediator)
Y = ((sv + bu) / 2)[lowmf]               # per-startup investment
dmed = pd.DataFrame({'X': X, 'M': M, 'Y': Y})
a_m = smf.ols('M ~ X', data=dmed).fit()
b_m = smf.ols('Y ~ X + M', data=dmed).fit()
c_m = smf.ols('Y ~ X', data=dmed).fit()
a, b = a_m.params['X'], b_m.params['M']
cprime, ctot = b_m.params['X'], c_m.params['X']
print(f'\n  Mediation (low-EI, n={lowmf.sum()}): X=male founder, M=warmth, Y=investment')
print(f'    a (X->M)        = {a:+.3f}  p={a_m.pvalues["X"]:.3f}')
print(f'    b (M->Y|X)      = {b:+.3f}  p={b_m.pvalues["M"]:.3f}')
print(f'    c total (X->Y)  = {ctot:+.3f}  p={c_m.pvalues["X"]:.3f}')
print(f"    c' direct (X->Y|M)= {cprime:+.3f}  p={b_m.pvalues['X']:.3f}")
# bootstrap indirect effect
rng = np.random.default_rng(42)
idx = np.arange(len(X)); ind = []
for _ in range(10000):
    s = rng.choice(idx, len(idx), replace=True)
    dd = dmed.iloc[s]
    try:
        aa = smf.ols('M ~ X', data=dd).fit().params['X']
        bb = smf.ols('Y ~ X + M', data=dd).fit().params['M']
        ind.append(aa * bb)
    except Exception:
        pass
ind = np.array(ind); ci = np.percentile(ind, [2.5, 97.5])
print(f'    indirect a*b    = {a*b:+.3f}  bootstrap 95% CI [{ci[0]:+.3f}, {ci[1]:+.3f}]  '
      f'({"sig" if ci[0]>0 or ci[1]<0 else "ns"})')

print('\n' + sep); print('Done.')
