#!/usr/bin/env python3
"""Analysis block 33: additional APA figures for the storyline & robustness.

  fig20  Pitch-order interaction for R1, R2, R3 (the key robustness finding)
  fig21  Robustness coefficient plot — effect size across covariate specs
  fig22  EI by participant gender, per WLEIS dimension
  fig23  Success-perception mechanism: investment gap vs perceived-success gap
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
col = lambda n: names.index(n)
def cols_for(p): return [i for i, n in enumerate(names) if n.startswith(p) and '_DO' not in n]
lik = lambda v: int(re.match(r'\s*(\d+)', v.strip()).group(1))
arr = lambda c: np.array([lik(r[c]) for r in data], float)
mat = lambda cs: np.array([[lik(r[c]) for c in cs] for r in data], float).mean(1)

sv = np.array([float(r[col('invest_sv')]) for r in data])
bu = np.array([float(r[col('invest_bu')]) for r in data])
g = np.array([r[col('team_gender')] for r in data])
order = np.array([r[col('pitch_order')].strip() for r in data])
resp = np.array([r[col('Q16')].strip() for r in data])
male, female = g == 'male', g == 'female'
DIMS = {'SEA': cols_for('Q10 (SEA)'), 'OEA': cols_for('Q11 (OEA)'),
        'UOE': cols_for('Q12 (UOE)'), 'ROE': cols_for('Q13 (ROE)')}
ei = mat(sum(DIMS.values(), []))
succ_sv, succ_bu = arr(col('Q5')), arr(col('Q47'))

apa.apply_apa_style()
GREY, DARK = '#D3D3D3', '#808080'

def lbl(ax, bars, vals, fmt='{:+.2f}', fs=8):
    for rect, v in zip(bars, vals):
        ax.text(rect.get_x()+rect.get_width()/2,
                rect.get_height() + (0.02 if rect.get_height() >= 0 else -0.02),
                fmt.format(v), ha='center',
                va='bottom' if rect.get_height() >= 0 else 'top', fontsize=fs)

# ════════════ fig20: pitch-order interaction ════════════
# effect magnitude (mean difference) per result, split by order
def diff_R1(mask): return (sv[mask] - bu[mask]).mean()
def diff_R2(mask):
    a = sv[female & mask]; b = bu[male & mask]
    return a.mean() - b.mean()
def diff_R3(mask):
    low = ei < np.median(ei)
    a = sv[male & low & mask]; b = bu[female & low & mask]
    return a.mean() - b.mean()
svf, buf = order == 'sv_first', order == 'bu_first'
labels = ['R1\nIndustry', 'R2\nCongruity', 'R3\nLow-EI']
sv_first_vals = [diff_R1(svf), diff_R2(svf), diff_R3(svf)]
bu_first_vals = [diff_R1(buf), diff_R2(buf), diff_R3(buf)]
fig, ax = plt.subplots(figsize=(7.0, 4.6))
x = np.arange(3); bw = 0.38
b1 = ax.bar(x - bw/2, sv_first_vals, bw*0.95, label='SiteVision shown first',
            color=DARK, edgecolor='black', linewidth=0.8, zorder=3)
b2 = ax.bar(x + bw/2, bu_first_vals, bw*0.95, label='BalanceUp shown first',
            color=GREY, edgecolor='black', linewidth=0.8, zorder=3)
lbl(ax, b1, sv_first_vals); lbl(ax, b2, bu_first_vals)
ax.axhline(0, color='black', lw=0.8)
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_ylabel('Effect size (mean investment difference, 0–3)')
ax.set_ylim(-0.6, 1.4)
ax.legend(frameon=False, fontsize=9, loc='upper right')
fig.tight_layout()
apa.save(fig, os.path.join(HERE, 'figures', 'fig20_pitch_order_interaction'))
print('Saved fig20_pitch_order_interaction')

# ════════════ fig21: robustness coefficient plot ════════════
# stored coefficients from block 27/28 (re-using computed values)
specs = ['Baseline', '+ Success', '+ Risk', '+ Competence', '+ Risk trait', '+ All']
R1 = [0.481, 0.147, 0.442, 0.408, 0.481, 0.165]
R1p = [0, .059, 0, 0, .32, .032]
R2 = [0.541, 0.226, 0.481, 0.472, 0.445, 0.217]
R2p = [.001, .091, .002, .004, .007, .106]
R3 = [0.462, 0.093, 0.438, 0.279, 0.528, 0.078]
R3p = [.032, .682, .092, .276, .038, .754]
fig, ax = plt.subplots(figsize=(7.4, 4.6))
x = np.arange(len(specs)); w = 0.27
def plot_series(off, vals, ps, color, lab):
    bars = ax.bar(x + off, vals, w, color=color, edgecolor='black', linewidth=0.7,
                  zorder=3, label=lab)
    for rect, p in zip(bars, ps):
        if p < .05:
            ax.text(rect.get_x()+rect.get_width()/2, rect.get_height()+0.01, '*',
                    ha='center', va='bottom', fontsize=11)
    return bars
plot_series(-w, R1, R1p, DARK, 'R1 Industry')
plot_series(0, R2, R2p, GREY, 'R2 Congruity')
plot_series(w, R3, R3p, '#FFFFFF', 'R3 Low-EI')
ax.set_xticks(x); ax.set_xticklabels(specs, fontsize=9)
ax.set_ylabel('Adjusted effect coefficient (0–3 scale)')
ax.set_ylim(0, 0.65)
ax.legend(frameon=False, fontsize=8.5, loc='upper right')
ax.text(0.01, 0.97, '* p < .05', transform=ax.transAxes, fontsize=8, va='top', style='italic')
fig.tight_layout()
apa.save(fig, os.path.join(HERE, 'figures', 'fig21_robustness_coefficients'))
print('Saved fig21_robustness_coefficients')

# ════════════ fig22: EI by participant gender ════════════
mp, fp = resp == 'Männlich', resp == 'Weiblich'
dims = ['Total', 'SEA', 'OEA', 'UOE', 'ROE']
eivals = {'Total': ei, **{k: mat(c) for k, c in DIMS.items()}}
m_means = [eivals[d][mp].mean() for d in dims]
f_means = [eivals[d][fp].mean() for d in dims]
m_se = [eivals[d][mp].std(ddof=1)/np.sqrt(mp.sum()) for d in dims]
f_se = [eivals[d][fp].std(ddof=1)/np.sqrt(fp.sum()) for d in dims]
pvals = {}
for d in dims:
    _, p = stats.ttest_ind(eivals[d][mp], eivals[d][fp], equal_var=False)
    pvals[d] = p
fig, ax = plt.subplots(figsize=(7.2, 4.6))
x = np.arange(len(dims)); bw = 0.38
b1 = ax.bar(x - bw/2, m_means, bw*0.95, yerr=m_se, capsize=3, label='Male participants',
            color=DARK, edgecolor='black', linewidth=0.8, zorder=3, error_kw=dict(lw=0.8))
b2 = ax.bar(x + bw/2, f_means, bw*0.95, yerr=f_se, capsize=3, label='Female participants',
            color=GREY, edgecolor='black', linewidth=0.8, zorder=3, error_kw=dict(lw=0.8))
star = lambda p: '***' if p < .001 else '**' if p < .01 else '*' if p < .05 else 'ns'
for xi, d in zip(x, dims):
    top = max(m_means[dims.index(d)], f_means[dims.index(d)]) + 0.5
    ax.text(xi, top, star(pvals[d]), ha='center', fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(dims)
ax.set_ylabel('Mean WLEIS score (1–7)')
ax.set_ylim(0, 7)
ax.legend(frameon=False, fontsize=9, loc='lower right')
fig.tight_layout()
apa.save(fig, os.path.join(HERE, 'figures', 'fig22_ei_by_gender'))
print('Saved fig22_ei_by_gender')

# ════════════ fig23: success-perception mechanism scatter ════════════
inv_gap = sv - bu
succ_gap = succ_sv - succ_bu
r, p = stats.pearsonr(inv_gap, succ_gap)
fig, ax = plt.subplots(figsize=(6.2, 4.8))
# jitter for readability
rng = np.random.default_rng(42)
jx = succ_gap + rng.normal(0, 0.08, len(succ_gap))
jy = inv_gap + rng.normal(0, 0.05, len(inv_gap))
ax.scatter(jx, jy, s=22, color=DARK, edgecolor='black', linewidth=0.4, alpha=0.6, zorder=3)
# regression line
b1_, b0_ = np.polyfit(succ_gap, inv_gap, 1)
xs = np.linspace(succ_gap.min(), succ_gap.max(), 50)
ax.plot(xs, b0_ + b1_*xs, color='black', lw=1.4, zorder=4)
ax.axhline(0, color='grey', lw=0.7, ls='--'); ax.axvline(0, color='grey', lw=0.7, ls='--')
ax.set_xlabel('Perceived-success gap (SiteVision − BalanceUp, 1–7)')
ax.set_ylabel('Investment gap (SiteVision − BalanceUp, 0–3)')
ax.text(0.04, 0.96, f'r = {r:.2f}, p < .001', transform=ax.transAxes,
        fontsize=10, va='top', style='italic')
fig.tight_layout()
apa.save(fig, os.path.join(HERE, 'figures', 'fig23_success_mechanism'))
print(f'Saved fig23_success_mechanism (r={r:.3f})')
