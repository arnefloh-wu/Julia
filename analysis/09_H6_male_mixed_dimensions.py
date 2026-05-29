#!/usr/bin/env python3
"""Analysis block 9: male-vs-mixed equality hypothesis, per EI dimension.

H: higher EI -> more equal funding between MALE- and MIXED-founded start-ups.
Between-subjects -> restrict to male (n=62) & mixed (n=70); DV = total
investment (0-6). For each WLEIS dimension (and Total):
  * EI_dim x condition interaction on investment  (the inferential test)
  * EI slope within each condition
  * signed male-mixed gap by Low/High EI_dim (descriptive equality)
Closer-to-zero gap for High EI would support the hypothesis.
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
def smat(cols): return np.array([[likert(r[i]) for i in cols] for r in data], float)
def cronbach(M): k = M.shape[1]; return k/(k-1)*(1 - M.var(axis=0, ddof=1).sum()/M.sum(axis=1).var(ddof=1))

invest = np.array([float(r[i_sv]) + float(r[i_bu]) for r in data])
gender = np.array([r[i_tg] for r in data])
keep = np.isin(gender, ['male', 'mixed'])

specs = list(DIMS.items()) + [('Total', all_items)]
star = lambda p: '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else ''

print('=' * 86)
print('H6 variant (MALE vs MIXED), per EI dimension  | DV = total investment (0-6)')
print('=' * 86)
header = (f'{"Dim":6s} {"alpha":>5s} | {"intxn F":>7s} {"p":>6s} | '
          f'{"b_male":>7s} {"b_mix":>7s} | {"gapLow":>7s} {"gapHigh":>7s}')
print(header); print('-' * len(header))

chart = {}
for d, cols in specs:
    M = smat(cols); s = M.mean(axis=1)
    a = cronbach(M)
    df = pd.DataFrame({'invest': invest[keep], 'x': s[keep] - s[keep].mean(), 'cond': gender[keep]})
    mod = smf.ols('invest ~ x * C(cond)', data=df).fit()
    aov = sm.stats.anova_lm(mod, typ=2)
    Fi, pi = aov.loc['x:C(cond)', 'F'], aov.loc['x:C(cond)', 'PR(>F)']
    b_male = smf.ols('invest ~ x', data=df[df.cond == 'male']).fit().params['x']
    b_mix = smf.ols('invest ~ x', data=df[df.cond == 'mixed']).fit().params['x']
    med = np.median(s); hi = s >= med
    def diff_se(mask):
        mm = invest[(gender == 'male') & mask]; mx = invest[(gender == 'mixed') & mask]
        return (mm.mean() - mx.mean(),
                np.sqrt(mm.var(ddof=1)/len(mm) + mx.var(ddof=1)/len(mx)))
    gL, seL = diff_se(~hi); gH, seH = diff_se(hi)
    chart[d] = (gL, seL, gH, seH)
    print(f'{d:6s} {a:5.2f} | {Fi:7.2f} {pi:6.3f}{star(pi):3s}| '
          f'{b_male:+7.3f} {b_mix:+7.3f} | {gL:+7.2f} {gH:+7.2f}')

print('\ngap = mean(male) - mean(mixed) total investment; closer to 0 = more equal.')
print('H predicts |gapHigh| < |gapLow| AND a significant interaction (none observed).')

# ---------- chart: signed male-mixed gap by EI group, per dimension ----------
apa.apply_apa_style()
fig, ax = plt.subplots(figsize=(7.2, 4.5))
dims4 = ['SEA', 'OEA', 'UOE', 'ROE']
x = np.arange(len(dims4)); bw = 0.36
gL = [chart[d][0] for d in dims4]; seL = [chart[d][1] for d in dims4]
gH = [chart[d][2] for d in dims4]; seH = [chart[d][3] for d in dims4]
b1 = ax.bar(x - bw/2, gL, bw*0.95, yerr=seL, label='Low EI', color='#D3D3D3',
            edgecolor='black', linewidth=0.8, capsize=3, error_kw=dict(lw=0.8), zorder=3)
b2 = ax.bar(x + bw/2, gH, bw*0.95, yerr=seH, label='High EI', color='#808080',
            edgecolor='black', linewidth=0.8, capsize=3, error_kw=dict(lw=0.8), zorder=3)
ax.axhline(0, color='black', lw=0.8)
ax.set_xticks(x); ax.set_xticklabels(dims4)
ax.set_ylabel('Investment gap (male − mixed)')
ax.set_ylim(-0.8, 0.8)
ax.legend(frameon=False, fontsize=9, loc='upper right')
fig.text(0.5, 0.005, 'Closer to 0 = more equal allocation between male- and mixed-founded start-ups',
         ha='center', fontsize=8, style='italic')
fig.tight_layout(rect=[0, 0.03, 1, 1])
apa.save(fig, os.path.join(HERE, 'figures', 'fig08_H6_male_mixed_dims'))
print('\nSaved figures/fig08_H6_male_mixed_dims.{png,pdf,svg}')
