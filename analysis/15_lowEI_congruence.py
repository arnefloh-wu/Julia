#!/usr/bin/env python3
"""Analysis block 15: focused test of
   'Low-EI participants invest more in masculine- than feminine-congruent startups.'

masculine-congruent = invest_sv among MALE-condition pts (male founder + male industry)
feminine-congruent  = invest_bu among FEMALE-condition pts (female founder + female industry)
Low EI via full-sample Total-EI median split. Between-subjects -> independent
samples. Directional ('more') -> one- and two-tailed; robustness: Mann-Whitney,
bootstrap CI, and a bottom-tertile definition of 'low EI'.
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
ei_cols = [i for i, n in enumerate(names)
           if n.startswith(('Q10 (SEA)', 'Q11 (OEA)', 'Q12 (UOE)', 'Q13 (ROE)')) and '_DO' not in n]
i_sv, i_bu, i_tg = names.index('invest_sv'), names.index('invest_bu'), names.index('team_gender')
likert = lambda v: int(re.match(r'\s*(\d+)', v.strip()).group(1))
ei = np.array([[likert(r[i]) for i in ei_cols] for r in data], float).mean(axis=1)
sv = np.array([float(r[i_sv]) for r in data])
bu = np.array([float(r[i_bu]) for r in data])
g = np.array([r[i_tg] for r in data])

def report(low_mask, tag):
    masc = sv[(g == 'male') & low_mask]      # masculine-congruent
    fem = bu[(g == 'female') & low_mask]     # feminine-congruent
    n1, n2 = len(masc), len(fem)
    m1, m2 = masc.mean(), fem.mean()
    s1, s2 = masc.std(ddof=1), fem.std(ddof=1)
    diff = m1 - m2
    # Welch t
    t, p2 = stats.ttest_ind(masc, fem, equal_var=False)
    p1 = p2 / 2 if t > 0 else 1 - p2 / 2
    dfw = (s1**2/n1 + s2**2/n2)**2 / ((s1**2/n1)**2/(n1-1) + (s2**2/n2)**2/(n2-1))
    se = np.sqrt(s1**2/n1 + s2**2/n2)
    tcrit = stats.t.ppf(.975, dfw)
    ci = (diff - tcrit*se, diff + tcrit*se)
    # Cohen d (pooled)
    sp = np.sqrt(((n1-1)*s1**2 + (n2-1)*s2**2) / (n1+n2-2))
    d = diff / sp
    # Mann-Whitney
    u, pmw = stats.mannwhitneyu(masc, fem, alternative='greater')
    # bootstrap CI of diff
    rng = np.random.default_rng(42)
    boot = np.array([rng.choice(masc, n1).mean() - rng.choice(fem, n2).mean() for _ in range(10000)])
    bci = np.percentile(boot, [2.5, 97.5])
    print(f'\n### {tag}')
    print(f'  masculine-congruent: M={m1:.2f}, SD={s1:.2f}, n={n1}')
    print(f'  feminine-congruent : M={m2:.2f}, SD={s2:.2f}, n={n2}')
    print(f'  difference = {diff:+.2f}, 95% CI [{ci[0]:+.2f}, {ci[1]:+.2f}]')
    print(f'  Welch t({dfw:.0f}) = {t:.2f}, p(2-tail) = {p2:.3f}, p(1-tail) = {p1:.3f}, Cohen d = {d:+.2f}')
    print(f'  Mann-Whitney U (one-sided, masc>fem): p = {pmw:.3f}')
    print(f'  bootstrap 95% CI of difference [{bci[0]:+.2f}, {bci[1]:+.2f}] '
          f'({"excludes" if bci[0] > 0 or bci[1] < 0 else "includes"} 0)')
    return m1, s1/np.sqrt(n1), m2, s2/np.sqrt(n2), p1, p2

print('=' * 72)
print('Low-EI: masculine-congruent vs feminine-congruent investment (0-3)')
print('=' * 72)
med = np.median(ei)
res = report(ei < med, f'PRIMARY: low EI = below median ({med:.2f})')
# robustness: bottom tertile
t1 = np.quantile(ei, 1/3)
report(ei <= t1, f'ROBUSTNESS: low EI = bottom tertile (<= {t1:.2f})')

# ---- chart (primary, median-split low-EI group) ----
m1, se1, m2, se2, p1, p2 = res
apa.apply_apa_style()
fig, ax = plt.subplots(figsize=(5.4, 4.6))
bars = ax.bar([0, 1], [m1, m2], 0.6, yerr=[se1, se2], capsize=4,
              color=['#808080', '#D3D3D3'], edgecolor='black', linewidth=0.8,
              error_kw=dict(lw=0.9), zorder=3)
for rect, v in zip(bars, [m1, m2]):
    ax.text(rect.get_x()+rect.get_width()/2, rect.get_height()+0.02, f'{v:.2f}',
            ha='center', va='bottom', fontsize=10)
# significance bracket
yb = max(m1, m2) + 0.35
ax.plot([0, 0, 1, 1], [yb, yb+0.05, yb+0.05, yb], color='black', lw=0.9)
ax.text(0.5, yb+0.07, f'one-tailed p = {p1:.3f}', ha='center', va='bottom', fontsize=9)
ax.set_xticks([0, 1])
ax.set_xticklabels(['Masculine-\ncongruent', 'Feminine-\ncongruent'])
ax.set_ylabel('Mean amount invested (0–3)')
ax.set_ylim(0, 3.0)
ax.set_title('Low-EI participants', fontsize=11)
fig.tight_layout()
apa.save(fig, os.path.join(HERE, 'figures', 'fig14_lowEI_congruence'))
print('\nSaved figures/fig14_lowEI_congruence.{png,pdf,svg}')
