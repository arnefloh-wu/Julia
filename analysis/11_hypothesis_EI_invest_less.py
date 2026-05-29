#!/usr/bin/env python3
"""Analysis block 11: 'Higher EI -> invests less.'

DV = total investment (invest_sv + invest_bu, 0-6), full sample (N=187).
Test EI total and each WLEIS dimension (SEA, OEA, UOE, ROE).
Hypothesis -> NEGATIVE correlation with investment.
"""
import csv, re, os, sys
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'figures'))
import apa_barchart as apa
import matplotlib.pyplot as plt

SRC = os.path.join(HERE, '..', 'MasterThesis_cleaned.csv')
with open(SRC, newline='') as f:
    rows = list(csv.reader(f))
names, data = rows[0], rows[3:]

def cols_for(p): return [i for i, n in enumerate(names) if n.startswith(p) and '_DO' not in n]
DIMS = {'SEA': cols_for('Q10 (SEA)'), 'OEA': cols_for('Q11 (OEA)'),
        'UOE': cols_for('Q12 (UOE)'), 'ROE': cols_for('Q13 (ROE)')}
all_items = sum(DIMS.values(), [])
i_sv, i_bu, i_tg = names.index('invest_sv'), names.index('invest_bu'), names.index('team_gender')
likert = lambda v: int(re.match(r'\s*(\d+)', v.strip()).group(1))
sc = lambda cols: np.array([[likert(r[i]) for i in cols] for r in data], float).mean(axis=1)

invest = np.array([float(r[i_sv]) + float(r[i_bu]) for r in data])
gender = np.array([r[i_tg] for r in data])
N = len(data)
star = lambda p: '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else ''
specs = [('SEA', DIMS['SEA']), ('OEA', DIMS['OEA']), ('UOE', DIMS['UOE']),
         ('ROE', DIMS['ROE']), ('Total', all_items)]

print('=' * 76)
print(f'H: higher EI -> invests LESS  | DV = total investment (0-6), N = {N}')
print(f'investment: M = {invest.mean():.2f}, SD = {invest.std(ddof=1):.2f}  (expect r < 0)')
print('=' * 76)
print(f'{"EI measure":8s} | {"Pearson r":>11s} {"p":>7s} | {"Spearman":>9s} {"p":>7s} | '
      f'{"b|cond":>7s} {"p":>6s}')
print('-' * 76)
res = {}
for d, cols in specs:
    s = sc(cols)
    r, p = stats.pearsonr(s, invest)
    rho, pr = stats.spearmanr(s, invest)
    # robustness: EI coefficient controlling for founder condition
    df = pd.DataFrame({'invest': invest, 'x': s, 'cond': gender})
    m = smf.ols('invest ~ x + C(cond)', data=df).fit()
    res[d] = (r, p)
    print(f'{d:8s} | {r:+11.3f} {p:6.3f}{star(p):2s}| {rho:+9.3f} {pr:6.3f}{star(pr):2s}| '
          f'{m.params["x"]:+7.3f} {m.pvalues["x"]:.3f}')

# median split descriptive on total EI
tot = sc(all_items); med = np.median(tot); hi = tot >= med
ml, mh = invest[~hi].mean(), invest[hi].mean()
t, pt = stats.ttest_ind(invest[~hi], invest[hi])
dcoh = (mh - ml) / np.sqrt(((( ~hi).sum()-1)*invest[~hi].var(ddof=1) +
        (hi.sum()-1)*invest[hi].var(ddof=1)) / (N-2))
print('-' * 76)
print(f'Median split (Total EI): Low-EI invest M={ml:.2f} (n={(~hi).sum()}), '
      f'High-EI M={mh:.2f} (n={hi.sum()})')
print(f'  t({N-2}) = {t:.2f}, p = {pt:.3f}, Cohen d = {mh-ml:+.2f} raw / {dcoh:+.2f} std')

# ---- chart: EI-investment correlation per measure ----
apa.apply_apa_style()
fig, ax = plt.subplots(figsize=(7.0, 4.5))
labels = ['SEA', 'OEA', 'UOE', 'ROE', 'Total']
vals = [res[d][0] for d in labels]
cols = ['#D3D3D3'] * 4 + ['#4D4D4D']
bars = ax.bar(range(len(labels)), vals, 0.6, color=cols, edgecolor='black', linewidth=0.8, zorder=3)
for rect, v, d in zip(bars, vals, labels):
    va = 'bottom' if v >= 0 else 'top'
    ax.text(rect.get_x()+rect.get_width()/2, v + (0.005 if v >= 0 else -0.005),
            f'{v:+.2f}{star(res[d][1])}', ha='center', va=va, fontsize=9)
ax.axhline(0, color='black', lw=0.8)
ax.axhspan(-0.20, 0.20, color='grey', alpha=0.10, zorder=0)
ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels)
ax.set_ylabel('Correlation of EI with investment (r)')
ax.set_ylim(-0.3, 0.3)
fig.text(0.5, 0.005, 'Hypothesis predicts negative r; shaded band ≈ below the N=187 MDES (|r|<.20)',
         ha='center', fontsize=8, style='italic')
fig.tight_layout(rect=[0, 0.03, 1, 1])
apa.save(fig, os.path.join(HERE, 'figures', 'fig10_EI_invest_less'))
print('\nSaved figures/fig10_EI_invest_less.{png,pdf,svg}')
