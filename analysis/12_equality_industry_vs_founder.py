#!/usr/bin/env python3
"""Analysis block 12: does HIGH EI -> investing LESS equally?
Two distinct kinds of (in)equality:

  A) ACROSS INDUSTRIES (within-person, N=187):
     inequality = |invest_sv - invest_bu|  (SiteVision ConTech vs BalanceUp wellness)
     test: r(EI, inequality);  "less equal" -> POSITIVE r.

  B) ACROSS FOUNDER-TEAM GENDER (between-subjects):
     EI x team_gender interaction on total investment; equality = uniformity of
     investment across male/female/mixed.  "less equal for high EI" -> larger
     spread of condition means among high-EI participants.

Tested for Total EI and each WLEIS dimension.
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

def cols_for(p): return [i for i, n in enumerate(names) if n.startswith(p) and '_DO' not in n]
DIMS = {'SEA': cols_for('Q10 (SEA)'), 'OEA': cols_for('Q11 (OEA)'),
        'UOE': cols_for('Q12 (UOE)'), 'ROE': cols_for('Q13 (ROE)')}
all_items = sum(DIMS.values(), [])
i_sv, i_bu, i_tg = names.index('invest_sv'), names.index('invest_bu'), names.index('team_gender')
likert = lambda v: int(re.match(r'\s*(\d+)', v.strip()).group(1))
sc = lambda cols: np.array([[likert(r[i]) for i in cols] for r in data], float).mean(axis=1)

sv = np.array([float(r[i_sv]) for r in data]); bu = np.array([float(r[i_bu]) for r in data])
invest = sv + bu
ineq_ind = np.abs(sv - bu)              # industry inequality (within-person)
gender = np.array([r[i_tg] for r in data])
N = len(data)
star = lambda p: '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else ''
specs = [('SEA', DIMS['SEA']), ('OEA', DIMS['OEA']), ('UOE', DIMS['UOE']),
         ('ROE', DIMS['ROE']), ('Total', all_items)]

# ---------- A) industries (within-person) ----------
print('=' * 74)
print('A) LESS EQUAL ACROSS INDUSTRIES  | DV = |invest_sv - invest_bu| (0-3), N=187')
print(f'   inequality: M = {ineq_ind.mean():.2f}, SD = {ineq_ind.std(ddof=1):.2f}   '
      f'("less equal" -> POSITIVE r)')
print('=' * 74)
print(f'{"EI":8s} | {"r":>8s} {"p":>7s} | {"Spearman":>9s} {"p":>7s}')
rA = {}
for d, cols in specs:
    s = sc(cols); r, p = stats.pearsonr(s, ineq_ind); rho, pr = stats.spearmanr(s, ineq_ind)
    rA[d] = (r, p)
    print(f'{d:8s} | {r:+8.3f} {p:6.3f}{star(p):2s}| {rho:+9.3f} {pr:6.3f}{star(pr):2s}')

# ---------- B) founder gender (between-subjects) ----------
print('\n' + '=' * 74)
print('B) LESS EQUAL ACROSS FOUNDER-TEAM GENDER | EI x team_gender on total investment')
print('=' * 74)
print(f'{"EI":8s} | {"interaction F(2,181)":>20s} {"p":>7s}')
pB = {}
for d, cols in specs:
    s = sc(cols)
    df = pd.DataFrame({'invest': invest, 'x': s - s.mean(), 'cond': gender})
    a = sm.stats.anova_lm(smf.ols('invest ~ x * C(cond)', data=df).fit(), typ=2)
    F, p = a.loc['x:C(cond)', 'F'], a.loc['x:C(cond)', 'PR(>F)']
    pB[d] = (F, p)
    print(f'{d:8s} | {F:20.2f} {p:6.3f}{star(p)}')

# equality descriptives by EI group (median split on Total EI)
tot = sc(all_items); med = np.median(tot); hi = tot >= med
print(f'\nEquality descriptives (median split Total EI at {med:.2f}):')
print(f'{"EI grp":7s} | {"|SV-BU| (industry)":>18s} | '
      f'{"male":>6s} {"female":>7s} {"mixed":>6s} | {"spread SD":>9s}')
spreads = {}
for lbl, mask in [('Low', ~hi), ('High', hi)]:
    ind_eq = ineq_ind[mask].mean()
    cms = [invest[(gender == c) & mask].mean() for c in ['male', 'female', 'mixed']]
    sd = np.std(cms, ddof=1)
    spreads[lbl] = (ind_eq, sd)
    print(f'{lbl:7s} | {ind_eq:18.2f} | {cms[0]:6.2f} {cms[1]:7.2f} {cms[2]:6.2f} | {sd:9.2f}')

# ---------- chart: 2 panels ----------
apa.apply_apa_style()
fig, (axA, axB) = plt.subplots(1, 2, figsize=(10, 4.4))

# Panel A: r(EI, industry inequality)
labs = ['SEA', 'OEA', 'UOE', 'ROE', 'Total']
vals = [rA[d][0] for d in labs]
colsA = ['#D3D3D3'] * 4 + ['#4D4D4D']
bA = axA.bar(range(5), vals, 0.6, color=colsA, edgecolor='black', linewidth=0.8, zorder=3)
for rect, v, d in zip(bA, vals, labs):
    axA.text(rect.get_x()+rect.get_width()/2, v + (0.006 if v >= 0 else -0.006),
             f'{v:+.2f}{star(rA[d][1])}', ha='center',
             va='bottom' if v >= 0 else 'top', fontsize=8.5)
axA.axhline(0, color='black', lw=0.8)
axA.axhspan(-0.20, 0.20, color='grey', alpha=0.10, zorder=0)
axA.set_xticks(range(5)); axA.set_xticklabels(labs)
axA.set_ylabel('r (EI with |SV−BU|)')
axA.set_ylim(-0.3, 0.3)
axA.set_title('A) Across industries (within-person)\npositive = less equal', fontsize=10)

# Panel B: investment spread across founder conditions, Low vs High EI
sd_low, sd_high = spreads['Low'][1], spreads['High'][1]
bB = axB.bar([0, 1], [sd_low, sd_high], 0.55, color=['#D3D3D3', '#808080'],
             edgecolor='black', linewidth=0.8, zorder=3)
for rect, v in zip(bB, [sd_low, sd_high]):
    axB.text(rect.get_x()+rect.get_width()/2, v + 0.005, f'{v:.2f}',
             ha='center', va='bottom', fontsize=9)
axB.set_xticks([0, 1]); axB.set_xticklabels(['Low EI', 'High EI'])
axB.set_ylabel('SD of investment across founder conditions')
axB.set_ylim(0, max(sd_low, sd_high) * 1.4 + 0.05)
axB.set_title('B) Across founder-team gender (between)\nhigher = less equal (interaction ns)', fontsize=10)

fig.tight_layout()
apa.save(fig, os.path.join(HERE, 'figures', 'fig11_equality_industry_vs_founder'))
print('\nSaved figures/fig11_equality_industry_vs_founder.{png,pdf,svg}')
