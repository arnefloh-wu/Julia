#!/usr/bin/env python3
"""Analysis block 18: gender-(in)congruity penalty in BOTH directions.

Q1: do MALE founders in a FEMALE-typed industry get less than FEMALE founders there?
Q2 (vice versa): do FEMALE founders in a MALE-typed industry get less than MALE founders there?

Founder gender = between (male vs female condition); industry = within (SiteVision
ConTech = male-typed; BalanceUp Wellness = female-typed). 2(founder)x2(industry)
mixed design. Congruity predicts the matching gender > mismatching in each industry.
"""
import csv, os, sys
import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'figures'))
import apa_barchart as apa

SRC = os.path.join(HERE, '..', 'MasterThesis_cleaned.csv')
with open(SRC, newline='') as f:
    rows = list(csv.reader(f))
names, data = rows[0], rows[3:]
i_sv, i_bu, i_tg = names.index('invest_sv'), names.index('invest_bu'), names.index('team_gender')
sv = np.array([float(r[i_sv]) for r in data])
bu = np.array([float(r[i_bu]) for r in data])
g = np.array([r[i_tg] for r in data])
male, female = g == 'male', g == 'female'

def ttest(a, b, lab, dirn):
    t, p2 = stats.ttest_ind(a, b, equal_var=False)
    p1 = p2/2 if (t < 0) == (dirn == 'less') else 1 - p2/2
    sp = np.sqrt(((len(a)-1)*a.var(ddof=1)+(len(b)-1)*b.var(ddof=1))/(len(a)+len(b)-2))
    d = (a.mean()-b.mean())/sp
    print(f'  {lab}')
    print(f'    {a.mean():.2f} (n={len(a)}) vs {b.mean():.2f} (n={len(b)}); '
          f'diff={a.mean()-b.mean():+.2f}, Welch t={t:.2f}, p(2)={p2:.3f}, '
          f'p(1,{dirn})={p1:.3f}, d={d:+.2f}')

print('=' * 74)
print('Gender-(in)congruity penalty within each industry')
print('=' * 74)
print('\nQ1: MALE vs FEMALE founders in the FEMALE-typed industry (BalanceUp)')
print('    [incongruent = male; H: male < female]')
ttest(bu[male], bu[female], 'male-founder BU vs female-founder BU', 'less')

print('\nQ2 (vice versa): FEMALE vs MALE founders in the MALE-typed industry (SiteVision)')
print('    [incongruent = female; H: female < male]')
ttest(sv[female], sv[male], 'female-founder SV vs male-founder SV', 'less')

# ---- founder x industry interaction (difference scores) ----
diff_male = sv[male] - bu[male]      # SV-BU within male founders
diff_female = sv[female] - bu[female]
t, p = stats.ttest_ind(diff_male, diff_female, equal_var=False)
print('\n' + '=' * 74)
print('Founder gender x industry INTERACTION (industry pref SV-BU by founder)')
print('=' * 74)
print(f'  male founders SV-BU   = {diff_male.mean():+.2f}')
print(f'  female founders SV-BU = {diff_female.mean():+.2f}')
print(f'  interaction (diff of diffs) = {diff_male.mean()-diff_female.mean():+.2f}, '
      f't={t:.2f}, p={p:.3f}  (ns => no congruity crossover)')

# main effects
both = male | female
ind_t, ind_p = stats.ttest_rel(sv[both], bu[both])
print(f'\n  Industry main effect (within): SV {sv[both].mean():.2f} vs BU {bu[both].mean():.2f}, '
      f'paired t={ind_t:.2f}, p={ind_p:.2e}')
tot_m, tot_f = (sv[male]+bu[male]), (sv[female]+bu[female])
f_t, f_p = stats.ttest_ind(tot_f, tot_m, equal_var=False)
print(f'  Founder main effect (between): female-founded {tot_f.mean()/2:.2f} vs '
      f'male-founded {tot_m.mean()/2:.2f} (per-startup), p={f_p:.3f}')

# ---- chart: congruent vs incongruent founder within each industry ----
fig, ax = apa.grouped_bar_chart(
    ['Male-typed industry\n(SiteVision)', 'Female-typed industry\n(BalanceUp)'],
    [('Gender-congruent founder', [sv[male].mean(), bu[female].mean()]),
     ('Gender-incongruent founder', [sv[female].mean(), bu[male].mean()])],
    ylabel='Mean amount invested (0–3)',
    errors=[[sv[male].std(ddof=1)/np.sqrt(male.sum()), bu[female].std(ddof=1)/np.sqrt(female.sum())],
            [sv[female].std(ddof=1)/np.sqrt(female.sum()), bu[male].std(ddof=1)/np.sqrt(male.sum())]],
    colors=['#808080', '#D3D3D3'])
ax.set_ylim(0, 3.0)
ax.legend(frameon=False, fontsize=8.5, loc='upper right')
apa.save(fig, os.path.join(HERE, 'figures', 'fig17_incongruity_both'))
print('\nCongruent = founder gender matches industry typing; incongruent = mismatch.')
print('Saved figures/fig17_incongruity_both.{png,pdf,svg}')
