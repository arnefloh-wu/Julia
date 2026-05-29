#!/usr/bin/env python3
"""Analysis block 4: H6 - EI and equality of funding allocation.

H6: Participants with higher EI allocate funding more equally between the
    female-typed and male-typed start-up than participants with lower EI.

Design note: founder gender (team_gender) is between-subjects; the within-
person contrast is the gender-typed industry of the two start-ups:
    SiteVision  = ConTech            (male-typed industry)   -> invest_sv
    BalanceUp   = Corporate Wellness (female-typed industry)  -> invest_bu
Equality measure: inequality = |invest_sv - invest_bu| (0-3); lower = more equal.
EI = WLEIS total (mean of 16 items). H6 -> EI correlates NEGATIVELY with inequality.
"""
import csv, re, os, sys
import numpy as np
from scipy import stats

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
sv = np.array([float(r[i_sv]) for r in data])
bu = np.array([float(r[i_bu]) for r in data])
ineq = np.abs(sv - bu)                 # allocation inequality (0-3)
signed = sv - bu                        # + = favours male-typed (SiteVision)
gender = np.array([r[i_tg] for r in data])
N = len(data)

print('=' * 70)
print(f'N = {N}')
print(f'invest SiteVision (male-typed):  M = {sv.mean():.2f}, SD = {sv.std(ddof=1):.2f}')
print(f'invest BalanceUp  (female-typed): M = {bu.mean():.2f}, SD = {bu.std(ddof=1):.2f}')
print(f'Inequality |SV-BU|: M = {ineq.mean():.2f}, SD = {ineq.std(ddof=1):.2f} '
      f'(0 = perfectly equal, 3 = max)')
print(f'Signed (SV-BU):     M = {signed.mean():+.2f}  (+ favours male-typed)')
print('=' * 70)

# ---- H6 test: EI vs inequality (continuous) ----
r, p = stats.pearsonr(ei, ineq)
rho, pr = stats.spearmanr(ei, ineq)
print('\n### H6  (expected: negative r -> higher EI = smaller difference = more equal)')
print(f'  Pearson  r = {r:+.3f}, p = {p:.3f}')
print(f'  Spearman rho = {rho:+.3f}, p = {pr:.3f}')

# ---- median split for descriptives ----
med = np.median(ei)
hi = ei >= med
low = ~hi
print(f'\n### Median split EI at {med:.2f}  (Low n={low.sum()}, High n={hi.sum()})')
def desc(mask):
    return dict(sv=sv[mask].mean(), bu=bu[mask].mean(),
                ineq_m=ineq[mask].mean(),
                ineq_se=ineq[mask].std(ddof=1)/np.sqrt(mask.sum()),
                sv_se=sv[mask].std(ddof=1)/np.sqrt(mask.sum()),
                bu_se=bu[mask].std(ddof=1)/np.sqrt(mask.sum()))
dl, dh = desc(low), desc(hi)
print(f'  {"":8s} {"invest_SV":>10s} {"invest_BU":>10s} {"|SV-BU|":>9s}')
print(f'  {"Low EI":8s} {dl["sv"]:10.2f} {dl["bu"]:10.2f} {dl["ineq_m"]:9.2f}')
print(f'  {"High EI":8s} {dh["sv"]:10.2f} {dh["bu"]:10.2f} {dh["ineq_m"]:9.2f}')

t, pt = stats.ttest_ind(ineq[low], ineq[hi])
d = (ineq[low].mean() - ineq[hi].mean()) / np.sqrt(
    ((low.sum()-1)*ineq[low].var(ddof=1) + (hi.sum()-1)*ineq[hi].var(ddof=1)) / (N-2))
print(f'\n  Inequality Low vs High EI: t({N-2}) = {t:.2f}, p = {pt:.3f}, Cohen d = {d:+.2f}')

# robustness by founder-gender condition
print('\n### Robustness: EI-inequality correlation within each founder condition')
for g in ['male', 'female', 'mixed']:
    m = gender == g
    rr, pp = stats.pearsonr(ei[m], ineq[m])
    print(f'  {g:7s} (n={m.sum():3d}): r = {rr:+.3f}, p = {pp:.3f}')

# ---- chart: allocation to each startup by EI group ----
fig, ax = apa.grouped_bar_chart(
    ['Low EI', 'High EI'],
    [('SiteVision (male-typed)', [dl['sv'], dh['sv']]),
     ('BalanceUp (female-typed)', [dl['bu'], dh['bu']])],
    ylabel='Mean amount invested (0–3)',
    errors=[[dl['sv_se'], dh['sv_se']], [dl['bu_se'], dh['bu_se']]],
    colors=['#D3D3D3', '#808080'],
)
apa.save(fig, os.path.join(HERE, 'figures', 'fig03_H6_EI_equality'))
print('\nSaved figures/fig03_H6_EI_equality.{png,pdf,svg}')
