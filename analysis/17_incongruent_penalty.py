#!/usr/bin/env python3
"""Analysis block 17: do female founders in male-typed industries receive less
funding than male founders in female-typed industries?

Incongruent cells (between-subjects):
  A = invest_sv among FEMALE-condition pts  (female founders, male-typed ConTech)   n=55
  B = invest_bu among MALE-condition pts    (male founders, female-typed Wellness)  n=62
H: A < B.  Directional -> two- and one-tailed; robustness MW + bootstrap.
Full 2x2 (founder gender x industry) reported for context, since SiteVision
(ConTech) is the generally more-funded pitch (confounds the raw comparison).
"""
import csv, re, os, sys
import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'figures'))
import apa_barchart as apa
import matplotlib.pyplot as plt

SRC = os.path.join(HERE, '..', 'MasterThesis_cleaned.csv')
with open(SRC, newline='') as f:
    rows = list(csv.reader(f))
names, data = rows[0], rows[3:]
i_sv, i_bu, i_tg = names.index('invest_sv'), names.index('invest_bu'), names.index('team_gender')
sv = np.array([float(r[i_sv]) for r in data])
bu = np.array([float(r[i_bu]) for r in data])
g = np.array([r[i_tg] for r in data])
male, female = g == 'male', g == 'female'

# 2x2 (founder gender x industry), mixed excluded
cells = {
    'Male founder / Male industry (congruent)':   sv[male],
    'Male founder / Female industry (INCONGRUENT B)': bu[male],
    'Female founder / Male industry (INCONGRUENT A)': sv[female],
    'Female founder / Female industry (congruent)': bu[female],
}
print('=' * 74)
print('2x2 context: mean investment (0-3) by founder gender x industry')
print('=' * 74)
for k, v in cells.items():
    print(f'  {k:46s}: M={v.mean():.2f}, SD={v.std(ddof=1):.2f}, n={len(v)}')

A = sv[female]   # female founders, male-typed industry
B = bu[male]     # male founders, female-typed industry
n1, n2 = len(A), len(B)
m1, m2 = A.mean(), B.mean()
s1, s2 = A.std(ddof=1), B.std(ddof=1)
diff = m1 - m2
t, p2 = stats.ttest_ind(A, B, equal_var=False)
p1 = p2/2 if t < 0 else 1 - p2/2          # H: A<B -> expect t<0
dfw = (s1**2/n1+s2**2/n2)**2 / ((s1**2/n1)**2/(n1-1)+(s2**2/n2)**2/(n2-1))
se = np.sqrt(s1**2/n1+s2**2/n2); tc = stats.t.ppf(.975, dfw)
ci = (diff-tc*se, diff+tc*se)
sp = np.sqrt(((n1-1)*s1**2+(n2-1)*s2**2)/(n1+n2-2)); d = diff/sp
u, pmw = stats.mannwhitneyu(A, B, alternative='less')
rng = np.random.default_rng(42)
boot = np.array([rng.choice(A, n1).mean() - rng.choice(B, n2).mean() for _ in range(10000)])
bci = np.percentile(boot, [2.5, 97.5])

print('\n' + '=' * 74)
print('FOCUSED TEST: A (female founder/male industry) vs B (male founder/female industry)')
print('=' * 74)
print(f'  A: M={m1:.2f}, SD={s1:.2f}, n={n1}')
print(f'  B: M={m2:.2f}, SD={s2:.2f}, n={n2}')
print(f'  A - B = {diff:+.2f}, 95% CI [{ci[0]:+.2f}, {ci[1]:+.2f}]   (H: A<B, i.e. diff<0)')
print(f'  Welch t({dfw:.0f}) = {t:.2f}, p(2-tail)={p2:.3f}, p(1-tail, A<B)={p1:.3f}, Cohen d={d:+.2f}')
print(f'  Mann-Whitney (A<B): p={pmw:.3f}')
print(f'  bootstrap 95% CI of (A-B): [{bci[0]:+.2f}, {bci[1]:+.2f}] '
      f'({"excludes" if bci[0]>0 or bci[1]<0 else "includes"} 0)')
verdict = ('SUPPORTED' if (diff < 0 and p1 < .05) else
           'NOT supported (A is not < B)' if diff >= 0 else 'directional only / ns')
print(f'  --> {verdict}')

# ---- chart: 2x2 grouped ----
fig, ax = apa.grouped_bar_chart(
    ['Male-typed industry\n(SiteVision)', 'Female-typed industry\n(BalanceUp)'],
    [('Male founders', [sv[male].mean(), bu[male].mean()]),
     ('Female founders', [sv[female].mean(), bu[female].mean()])],
    ylabel='Mean amount invested (0–3)',
    errors=[[sv[male].std(ddof=1)/np.sqrt(male.sum()), bu[male].std(ddof=1)/np.sqrt(male.sum())],
            [sv[female].std(ddof=1)/np.sqrt(female.sum()), bu[female].std(ddof=1)/np.sqrt(female.sum())]],
    colors=['#808080', '#D3D3D3'])
ax.set_ylim(0, 3.0)
ax.legend(frameon=False, fontsize=9, loc='upper right')
ax.annotate('B', (1 - 0.175, bu[male].mean()), fontsize=11, fontweight='bold', ha='center', va='bottom')
ax.annotate('A', (0 + 0.175, sv[female].mean()), fontsize=11, fontweight='bold', ha='center', va='bottom')
apa.save(fig, os.path.join(HERE, 'figures', 'fig16_incongruent_penalty'))
print('\nA = female founders in male industry; B = male founders in female industry.')
print('Saved figures/fig16_incongruent_penalty.{png,pdf,svg}')
