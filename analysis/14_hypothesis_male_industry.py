#!/usr/bin/env python3
"""Analysis block 14: 'Lower EI -> invest more in male-dominated industries.'

Male-dominated industry  = SiteVision (ConTech)   -> invest_sv
Female-dominated industry = BalanceUp (Wellness)  -> invest_bu
Within-person (N=187). Two readings:
  (a) absolute: invest_sv               (lower EI -> higher  => r<0)
  (b) preference: invest_sv - invest_bu (lower EI -> higher  => r<0)
Directional hypothesis -> report two-tailed AND one-tailed.
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

def cols_for(p): return [i for i, n in enumerate(names) if n.startswith(p) and '_DO' not in n]
DIMS = {'SEA': cols_for('Q10 (SEA)'), 'OEA': cols_for('Q11 (OEA)'),
        'UOE': cols_for('Q12 (UOE)'), 'ROE': cols_for('Q13 (ROE)')}
all_items = sum(DIMS.values(), [])
i_sv, i_bu = names.index('invest_sv'), names.index('invest_bu')
likert = lambda v: int(re.match(r'\s*(\d+)', v.strip()).group(1))
sc = lambda cols: np.array([[likert(r[i]) for i in cols] for r in data], float).mean(axis=1)

sv = np.array([float(r[i_sv]) for r in data])
bu = np.array([float(r[i_bu]) for r in data])
pref = sv - bu                       # male-industry preference (signed)
N = len(data)
specs = [('SEA', DIMS['SEA']), ('OEA', DIMS['OEA']), ('UOE', DIMS['UOE']),
         ('ROE', DIMS['ROE']), ('Total', all_items)]

def one_tailed(r, p, direction='neg'):
    # H predicts negative r
    return p / 2 if (r < 0) == (direction == 'neg') else 1 - p / 2

print('=' * 78)
print(f'Lower EI -> invest more in MALE-dominated industry (SiteVision). N={N}')
print(f'invest_sv (male ind.):  M={sv.mean():.2f} SD={sv.std(ddof=1):.2f}')
print(f'invest_bu (female ind.): M={bu.mean():.2f} SD={bu.std(ddof=1):.2f}')
print(f'preference (sv-bu):     M={pref.mean():+.2f} SD={pref.std(ddof=1):.2f}  '
      f'(+ = favours male-dominated industry)')
print('=' * 78)

for dv, lab in [(sv, '(a) ABSOLUTE invest in male industry (invest_sv)'),
                (pref, '(b) PREFERENCE male-female industry (invest_sv - invest_bu)')]:
    print(f'\n### {lab}   [H: r<0]')
    print(f'{"EI":8s} | {"r":>8s} {"p(2-tail)":>10s} {"p(1-tail)":>10s}')
    for d, cols in specs:
        s = sc(cols); r, p = stats.pearsonr(s, dv)
        print(f'{d:8s} | {r:+8.3f} {p:10.3f} {one_tailed(r,p):10.3f}')

# median split (Total EI)
tot = sc(all_items); med = np.median(tot); hi = tot >= med
print(f'\n### Median split (Total EI at {med:.2f})')
print(f'{"EI grp":7s} | {"male ind (SV)":>13s} | {"female ind (BU)":>15s} | {"preference":>10s}')
desc = {}
for lbl, mask in [('Low', ~hi), ('High', hi)]:
    desc[lbl] = (sv[mask].mean(), bu[mask].mean(), pref[mask].mean(),
                 sv[mask].std(ddof=1)/np.sqrt(mask.sum()),
                 bu[mask].std(ddof=1)/np.sqrt(mask.sum()))
    print(f'{lbl:7s} | {sv[mask].mean():13.2f} | {bu[mask].mean():15.2f} | {pref[mask].mean():+10.2f}')
print('  H predicts Low-EI invest MORE in male industry / higher preference than High-EI.')
t, p = stats.ttest_ind(sv[~hi], sv[hi])
print(f'  invest_sv Low vs High EI: t={t:.2f}, p(2)={p:.3f}')
t, p = stats.ttest_ind(pref[~hi], pref[hi])
print(f'  preference Low vs High EI: t={t:.2f}, p(2)={p:.3f}, p(1)={one_tailed(pref[~hi].mean()-pref[hi].mean(),p):.3f}')

# chart: investment in each industry by EI group
fig, ax = apa.grouped_bar_chart(
    ['Low EI', 'High EI'],
    [('Male-dominated industry (SiteVision)', [desc['Low'][0], desc['High'][0]]),
     ('Female-dominated industry (BalanceUp)', [desc['Low'][1], desc['High'][1]])],
    ylabel='Mean amount invested (0–3)',
    errors=[[desc['Low'][3], desc['High'][3]], [desc['Low'][4], desc['High'][4]]],
    colors=['#808080', '#D3D3D3'])
ax.legend(frameon=False, fontsize=8.5, loc='upper right')
apa.save(fig, os.path.join(HERE, 'figures', 'fig13_male_industry'))
print('\nSaved figures/fig13_male_industry.{png,pdf,svg}')
