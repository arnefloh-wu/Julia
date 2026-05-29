#!/usr/bin/env python3
"""Analysis block 7: H1 / H2 / H6 rerun for each EI (WLEIS) dimension.

Dimensions (4 items each, 7-pt): SEA, OEA, UOE, ROE; Total = mean of 16.
  H1  (male cond, n=62):   r(dim, total investment)        expected negative
  H2  (female cond, n=55): r(dim, total investment)        expected positive
  H6a (equality, N=187):   r(dim, |invest_sv-invest_bu|)   expected negative
  H6b (revised, N=187):    dim x team_gender interaction on total investment
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
import matplotlib.pyplot as plt

SRC = os.path.join(HERE, '..', 'MasterThesis_cleaned.csv')
with open(SRC, newline='') as f:
    rows = list(csv.reader(f))
names, data = rows[0], rows[3:]

def cols_for(prefix):
    return [i for i, n in enumerate(names) if n.startswith(prefix) and '_DO' not in n]

DIMS = {'SEA': cols_for('Q10 (SEA)'), 'OEA': cols_for('Q11 (OEA)'),
        'UOE': cols_for('Q12 (UOE)'), 'ROE': cols_for('Q13 (ROE)')}
all_items = sum(DIMS.values(), [])
i_sv, i_bu, i_tg = names.index('invest_sv'), names.index('invest_bu'), names.index('team_gender')
likert = lambda v: int(re.match(r'\s*(\d+)', v.strip()).group(1))

def score(cols):
    M = np.array([[likert(r[i]) for i in cols] for r in data], float)
    return M, M.mean(axis=1)

def cronbach(M):
    k = M.shape[1]
    return k / (k - 1) * (1 - M.var(axis=0, ddof=1).sum() / M.sum(axis=1).var(ddof=1))

scores = {d: score(c) for d, c in DIMS.items()}
Mtot, tot = score(all_items)
scores['Total'] = (Mtot, tot)

sv = np.array([float(r[i_sv]) for r in data])
bu = np.array([float(r[i_bu]) for r in data])
invest = sv + bu
ineq = np.abs(sv - bu)
gender = np.array([r[i_tg] for r in data])
male, female = gender == 'male', gender == 'female'

def star(p): return '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else ''

order = ['SEA', 'OEA', 'UOE', 'ROE', 'Total']
print('=' * 78)
print('EI DIMENSIONS: reliability & descriptives')
print('=' * 78)
print(f'{"Dim":6s} {"items":>5s} {"alpha":>6s} {"M":>6s} {"SD":>6s}')
for d in order:
    M, s = scores[d]
    print(f'{d:6s} {M.shape[1]:5d} {cronbach(M):6.2f} {s.mean():6.2f} {s.std(ddof=1):6.2f}')

print('\n' + '=' * 78)
print('H1 (male, expect r<0) | H2 (female, expect r>0) | H6a equality (expect r<0)')
print('=' * 78)
print(f'{"Dim":6s} | {"H1 r (male)":>14s} | {"H2 r (female)":>15s} | {"H6a r |SV-BU|":>15s}')
res = {}
for d in order:
    s = scores[d][1]
    r1, p1 = stats.pearsonr(s[male], invest[male])
    r2, p2 = stats.pearsonr(s[female], invest[female])
    r6, p6 = stats.pearsonr(s, ineq)
    res[d] = (r1, p1, r2, p2, r6, p6)
    print(f'{d:6s} | {r1:+.3f} {star(p1):3s} ({p1:.2f}) | '
          f'{r2:+.3f} {star(p2):3s} ({p2:.2f}) | {r6:+.3f} {star(p6):3s} ({p6:.2f})')

print('\n' + '=' * 78)
print('H6b: dimension x team_gender interaction on total investment (3 conditions)')
print('=' * 78)
print(f'{"Dim":6s} | {"interaction F(2,181)":>20s} | {"p":>6s}')
for d in order:
    s = scores[d][1]
    df = pd.DataFrame({'invest': invest, 'x': s - s.mean(), 'cond': gender})
    mod = smf.ols('invest ~ x * C(cond)', data=df).fit()
    aov = sm.stats.anova_lm(mod, typ=2)
    F, p = aov.loc['x:C(cond)', 'F'], aov.loc['x:C(cond)', 'PR(>F)']
    print(f'{d:6s} | {F:20.3f} | {p:.3f} {star(p)}')

# ---------- summary chart: correlations per dimension ----------
apa.apply_apa_style()
fig, ax = plt.subplots(figsize=(7.2, 4.5))
dims4 = ['SEA', 'OEA', 'UOE', 'ROE']
x = np.arange(len(dims4))
series = [('H1: male cond. (invest)', [res[d][0] for d in dims4], '#BFBFBF'),
          ('H2: female cond. (invest)', [res[d][2] for d in dims4], '#808080'),
          ('H6: equality |SV−BU|', [res[d][4] for d in dims4], '#4D4D4D')]
bw = 0.26
for j, (name, vals, col) in enumerate(series):
    off = (j - 1) * bw
    bars = ax.bar(x + off, vals, bw * 0.95, label=name, color=col,
                  edgecolor='black', linewidth=0.8, zorder=3)
    for rect, v in zip(bars, vals):
        va = 'bottom' if v >= 0 else 'top'
        ax.text(rect.get_x() + rect.get_width() / 2, v + (0.006 if v >= 0 else -0.006),
                f'{v:+.2f}', ha='center', va=va, fontsize=7.5)
ax.axhline(0, color='black', lw=0.8)
ax.axhspan(-0.2, 0.2, color='grey', alpha=0.10, zorder=0)  # ~ below MDES band
ax.set_xticks(x); ax.set_xticklabels(dims4)
ax.set_ylabel('Correlation with outcome (r)')
ax.set_ylim(-0.3, 0.3)
ax.legend(frameon=False, fontsize=8.5, loc='upper center', ncol=3,
          bbox_to_anchor=(0.5, 1.12))
fig.tight_layout()
apa.save(fig, os.path.join(HERE, 'figures', 'fig06_ei_dimensions'))
print('\nShaded band ~ |r|<.20 (below the full-sample MDES).')
print('Saved figures/fig06_ei_dimensions.{png,pdf,svg}')
