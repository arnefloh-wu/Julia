#!/usr/bin/env python3
"""Analysis block 16: link the congruence preference to moderators.

Congruence preference = invest in masculine-congruent (SiteVision|male, type='masc')
vs feminine-congruent (BalanceUp|female, type='fem'); between-subjects, N=117
(62 male-condition + 55 female-condition). For each moderator test whether the
masc-vs-fem gap depends on it (type x moderator interaction):
  * EI total and each dimension (SEA/OEA/UOE/ROE) - continuous
  * participant gender (Q16)
  * participant investment experience (Q23)
Forest plot shows the masc-fem gap (+95% CI) within each subgroup.
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
i_g16, i_q23 = names.index('Q16'), names.index('Q23')
likert = lambda v: int(re.match(r'\s*(\d+)', v.strip()).group(1))
smat = lambda cols: np.array([[likert(r[i]) for i in cols] for r in data], float)

ei = {d: smat(c).mean(1) for d, c in DIMS.items()}
ei['Total'] = smat(all_items).mean(1)
sv = np.array([float(r[i_sv]) for r in data]); bu = np.array([float(r[i_bu]) for r in data])
g = np.array([r[i_tg] for r in data])
resp = np.array([r[i_g16].strip() for r in data])
exp = np.array([r[i_q23].strip() for r in data])

# build congruence dataset (one focal value per participant)
male, female = g == 'male', g == 'female'
keep = male | female
focal = np.where(male, sv, bu)[keep]
typ = np.where(male[keep], 'masc', 'fem')
df = pd.DataFrame({'focal': focal, 'type': typ,
                   'resp': resp[keep], 'exp': exp[keep]})
for d in ei:
    df[d] = ei[d][keep]
N = len(df)
print(f'Congruence dataset: N={N} (masc={ (typ=="masc").sum() }, fem={ (typ=="fem").sum() })')

def gap_ci(sub):
    a = sub.focal[sub.type == 'masc']; b = sub.focal[sub.type == 'fem']
    if len(a) < 2 or len(b) < 2: return None
    diff = a.mean() - b.mean()
    se = np.sqrt(a.var(ddof=1)/len(a) + b.var(ddof=1)/len(b))
    dfw = (a.var(ddof=1)/len(a)+b.var(ddof=1)/len(b))**2 / (
        (a.var(ddof=1)/len(a))**2/(len(a)-1)+(b.var(ddof=1)/len(b))**2/(len(b)-1))
    tc = stats.t.ppf(.975, dfw)
    return diff, diff-tc*se, diff+tc*se, len(a), len(b)

forest = [('Overall', gap_ci(df))]

print('\n### Interaction tests (does the masc-fem gap depend on the moderator?)')
print(f'{"Moderator":18s} | {"interaction b/F":>16s} {"p":>7s}')

# continuous EI moderators
med = {}
for d in ['Total', 'SEA', 'OEA', 'UOE', 'ROE']:
    dd = df.copy(); dd['m'] = dd[d] - dd[d].mean()
    mod = smf.ols('focal ~ C(type) * m', data=dd).fit()
    b, p = mod.params['C(type)[T.masc]:m'], mod.pvalues['C(type)[T.masc]:m']
    print(f'EI {d:15s}| {b:+16.3f} {p:7.3f}')
    md = df[d].median(); med[d] = md
    forest.append((f'{d} EI: Low', gap_ci(df[df[d] < md])))
    forest.append((f'{d} EI: High', gap_ci(df[df[d] >= md])))

# participant gender
dg = df[df.resp.isin(['Männlich', 'Weiblich'])].copy()
mod = smf.ols('focal ~ C(type) * C(resp)', data=dg).fit()
ip = [k for k in mod.pvalues.index if ':' in k][0]
print(f'{"Participant gender":18s} | {mod.params[ip]:+16.3f} {mod.pvalues[ip]:7.3f}')
forest.append(('Resp: Male', gap_ci(df[df.resp == 'Männlich'])))
forest.append(('Resp: Female', gap_ci(df[df.resp == 'Weiblich'])))

# investment experience
de = df[df.exp.isin(['Ja', 'Nein'])].copy()
mod = smf.ols('focal ~ C(type) * C(exp)', data=de).fit()
ip = [k for k in mod.pvalues.index if ':' in k][0]
print(f'{"Investment exp.":18s} | {mod.params[ip]:+16.3f} {mod.pvalues[ip]:7.3f}')
forest.append(('Invest exp: Yes', gap_ci(df[df.exp == 'Ja'])))
forest.append(('Invest exp: No', gap_ci(df[df.exp == 'Nein'])))

print('\n### Masc-fem congruence gap within each subgroup')
print(f'{"Subgroup":16s} | {"gap":>6s}  {"95% CI":>16s}  {"n(m/f)":>8s}')
for lab, res in forest:
    if res:
        d_, lo, hi, n1, n2 = res
        print(f'{lab:16s} | {d_:+6.2f}  [{lo:+.2f}, {hi:+.2f}]  {n1:>3d}/{n2:<3d}')

# ---------- forest plot ----------
apa.apply_apa_style()
labels = [l for l, r in forest if r]
gaps = [r[0] for l, r in forest if r]
los = [r[1] for l, r in forest if r]
his = [r[2] for l, r in forest if r]
y = np.arange(len(labels))[::-1]
fig, ax = plt.subplots(figsize=(7.2, 7.0))
for yi, gpv, lo, hi in zip(y, gaps, los, his):
    sig = (lo > 0) or (hi < 0)
    ax.plot([lo, hi], [yi, yi], color='black', lw=1.2, zorder=2)
    ax.plot(gpv, yi, 'o', ms=7, color=('black' if sig else 'white'),
            markeredgecolor='black', markeredgewidth=1.0, zorder=3)
ax.axvline(0, color='grey', lw=0.9, ls='--')
ax.set_yticks(y); ax.set_yticklabels(labels, fontsize=9)
ax.set_xlabel('Congruence gap: masculine − feminine investment (0–3 scale)')
ax.set_title('Masculine-congruence preference by moderator (95% CI)', fontsize=10)
ax.set_xlim(-1.2, 1.6)
fig.tight_layout()
apa.save(fig, os.path.join(HERE, 'figures', 'fig15_congruence_moderators'))
print('\nFilled dot = 95% CI excludes 0. Saved figures/fig15_congruence_moderators.{png,pdf,svg}')
