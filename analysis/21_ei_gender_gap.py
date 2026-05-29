#!/usr/bin/env python3
"""Analysis block 21: how does EI affect the GENDER FUNDING GAP?

Design note: founder gender is BETWEEN-subjects (each participant sees two
startups that share the SAME founder gender). So the gender funding gap is a
between-subjects contrast on TOTAL capital allocated to the founder team:
    total = invest_sv + invest_bu   (range 0-6)
    per-startup mean = total / 2     (range 0-3)
Gender funding gap = male-founded − female-founded (positive = pro-male bias).

We test whether EI (Total + 4 WLEIS dimensions) MODERATES this gap.

Hypotheses
  H1  Debiasing:  higher EI shrinks the male-favouring gap (EI x gender interaction
                  on total investment; gap decreases as EI rises).
  H2  Pro-female: higher EI raises allocation to female founders specifically.
  H3  Dimension-specific: the regulation/appraisal of EMOTION dimensions (ROE/OEA)
                  drive any moderation more than use/self-appraisal.
Mixed-team condition included as a third level for completeness.
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
likert = lambda v: int(re.match(r'\s*(\d+)', v.strip()).group(1))
sc = lambda c: np.array([[likert(r[i] ) for i in c] for r in data], float).mean(1)

i_sv, i_bu, i_tg = names.index('invest_sv'), names.index('invest_bu'), names.index('team_gender')
sv = np.array([float(r[i_sv]) for r in data]); bu = np.array([float(r[i_bu]) for r in data])
g = np.array([r[i_tg] for r in data])
total = sv + bu                       # capital to the (gendered) founder team, 0-6
EI = {'Total': sc(all_items), **{k: sc(c) for k, c in DIMS.items()}}
star = lambda p: '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else 'ns'
order = ['Total', 'SEA', 'OEA', 'UOE', 'ROE']

print('=' * 78)
print('GENDER FUNDING GAP and EI moderation')
print('per-startup mean invested (total/2, range 0-3) by founder-gender condition')
print('=' * 78)
for cond in ['male', 'female', 'mixed']:
    t = total[g == cond] / 2
    print(f'  {cond:7s}: M={t.mean():.3f}  SD={t.std(ddof=1):.3f}  n={(g==cond).sum()}')
gap_mf = total[g=='male'].mean()/2 - total[g=='female'].mean()/2
t_mf, p_mf = stats.ttest_ind(total[g=='male'], total[g=='female'], equal_var=False)
print(f'\n  Raw gender gap (male − female, per-startup) = {gap_mf:+.3f}  '
      f't={t_mf:.2f}  p={p_mf:.3f}  {star(p_mf)}')

# ───────────────────────────────────────────────────────────
# H1: does EI moderate the male-vs-female gap? (interaction)
# ───────────────────────────────────────────────────────────
print('\n' + '=' * 78)
print('H1  Debiasing — EI x founder-gender interaction on total investment (male vs female)')
print('=' * 78)
mf = np.isin(g, ['male', 'female'])
print(f'{"EI dim":7s} | {"interaction b":>13s} {"p":>7s} | {"gap LowEI":>9s} {"gap HighEI":>10s}')
gaps = {}
for k in order:
    x = EI[k]
    df = pd.DataFrame({'tot': total[mf], 'x': (x - x.mean())[mf],
                       'gen': g[mf]})
    # code male=1, female=0 so positive interaction = gap grows with EI
    df['male'] = (df.gen == 'male').astype(int)
    m = smf.ols('tot ~ x * male', data=df).fit()
    b, p = m.params['x:male'], m.pvalues['x:male']
    med = np.median(x[mf]); xm = x[mf]; hi = xm >= med
    gen_mf = g[mf]
    def gap(mask):
        return total[mf][(gen_mf=='male') & mask].mean()/2 - total[mf][(gen_mf=='female') & mask].mean()/2
    gL, gH = gap(~hi), gap(hi)
    gaps[k] = (b, p, gL, gH)
    print(f'{k:7s} | {b:+13.3f} {p:7.3f}{"":1s}| {gL:+9.2f} {gH:+10.2f}  {star(p)}')
print('\n(b>0: gap widens with EI; b<0: EI shrinks the male-favouring gap = debiasing.')
print(' gap = male − female per-startup investment within each EI half.)')

# ───────────────────────────────────────────────────────────
# H2: does EI raise allocation to FEMALE founders specifically?
# ───────────────────────────────────────────────────────────
print('\n' + '=' * 78)
print('H2  Pro-female — EI correlated with investment, within each founder condition')
print('=' * 78)
print(f'{"EI dim":7s} | {"r(female cond)":>14s} {"p":>7s} | {"r(male cond)":>12s} {"p":>7s}')
for k in order:
    x = EI[k]
    rf, pf = stats.pearsonr(x[g=='female'], total[g=='female'])
    rm, pm = stats.pearsonr(x[g=='male'], total[g=='male'])
    print(f'{k:7s} | {rf:+14.3f} {pf:7.3f}{star(pf):>3s}| {rm:+12.3f} {pm:7.3f} {star(pm)}')
print('\n(H2 supported if r is positive & significant in the FEMALE condition'
      ' and larger than in the male condition.)')

# ───────────────────────────────────────────────────────────
# H3: full model including mixed + omnibus interaction test
# ───────────────────────────────────────────────────────────
print('\n' + '=' * 78)
print('H3  Omnibus EI x founder-gender (3 levels incl. mixed), Total EI')
print('=' * 78)
xT = EI['Total']
dfm = pd.DataFrame({'tot': total, 'x': xT - xT.mean(), 'gen': g})
m_full = smf.ols('tot ~ x * C(gen)', data=dfm).fit()
m_red  = smf.ols('tot ~ x + C(gen)', data=dfm).fit()
from statsmodels.stats.anova import anova_lm
cmp = anova_lm(m_red, m_full)
F = cmp['F'].iloc[1]; pdf = cmp['Pr(>F)'].iloc[1]
print(f'  Interaction block F={F:.2f}, p={pdf:.3f}  {star(pdf)}')
print('  (ns => EI does not significantly moderate the funding gap across conditions)')

# ───────────────────────────────────────────────────────────
# chart: gender gap at Low vs High EI per dimension
# ───────────────────────────────────────────────────────────
apa.apply_apa_style()
fig, ax = plt.subplots(figsize=(7.4, 4.6))
x = np.arange(len(order)); bw = 0.38
gL = [gaps[k][2] for k in order]; gH = [gaps[k][3] for k in order]
ax.bar(x - bw/2, gL, bw*0.95, label='Low EI', color='#D3D3D3', edgecolor='black', linewidth=0.8, zorder=3)
ax.bar(x + bw/2, gH, bw*0.95, label='High EI', color='#808080', edgecolor='black', linewidth=0.8, zorder=3)
for xi, v in zip(x - bw/2, gL):
    ax.text(xi, v + (0.01 if v >= 0 else -0.01), f'{v:+.2f}', ha='center',
            va='bottom' if v >= 0 else 'top', fontsize=7.5)
for xi, v in zip(x + bw/2, gH):
    ax.text(xi, v + (0.01 if v >= 0 else -0.01), f'{v:+.2f}', ha='center',
            va='bottom' if v >= 0 else 'top', fontsize=7.5)
ax.axhline(0, color='black', lw=0.8)
ax.set_xticks(x); ax.set_xticklabels(order)
ax.set_ylabel('Gender funding gap\n(male − female, per startup 0–3)')
ax.legend(frameon=False, fontsize=9, loc='upper right')
fig.tight_layout()
apa.save(fig, os.path.join(HERE, 'figures', 'fig19_ei_gender_gap'))
print('\nSaved figures/fig19_ei_gender_gap.{png,pdf,svg}')
