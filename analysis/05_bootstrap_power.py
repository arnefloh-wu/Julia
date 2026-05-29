#!/usr/bin/env python3
"""Analysis block 5: Bootstrap robustness + power/sensitivity analysis.

For the null findings (H1, H2, H6):
  1) Non-parametric bootstrap (10,000 resamples) -> 95% CIs and bootstrap p.
  2) Sensitivity power analysis: minimum detectable effect (MDES) at our Ns,
     and power to detect small/medium benchmark effects. (No circular
     'observed power'.)
"""
import csv, re, os, sys
import numpy as np
from scipy import stats
from statsmodels.stats.power import TTestIndPower

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'figures'))
import apa_barchart as apa
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)
B = 10000

# ---------- data ----------
SRC = os.path.join(HERE, '..', 'MasterThesis_cleaned.csv')
with open(SRC, newline='') as f:
    rows = list(csv.reader(f))
names, data = rows[0], rows[3:]
ei_cols = [i for i, n in enumerate(names)
           if n.startswith(('Q10 (SEA)', 'Q11 (OEA)', 'Q12 (UOE)', 'Q13 (ROE)'))
           and '_DO' not in n]
i_sv, i_bu, i_tg = names.index('invest_sv'), names.index('invest_bu'), names.index('team_gender')
likert = lambda v: int(re.match(r'\s*(\d+)', v.strip()).group(1))
EI = np.array([[likert(r[i]) for i in ei_cols] for r in data], float)
ei = EI.mean(axis=1)
sv = np.array([float(r[i_sv]) for r in data])
bu = np.array([float(r[i_bu]) for r in data])
invest = sv + bu
ineq = np.abs(sv - bu)
gender = np.array([r[i_tg] for r in data])

# ---------- bootstrap helpers ----------
def boot_r(x, y, B=B):
    n = len(x)
    idx = rng.integers(0, n, size=(B, n))
    rs = np.array([stats.pearsonr(x[i], y[i])[0] for i in idx])
    return rs

def report_boot(label, x, y, expected):
    r0 = stats.pearsonr(x, y)[0]
    rs = boot_r(x, y)
    lo, hi = np.percentile(rs, [2.5, 97.5])
    p_boot = 2 * min((rs <= 0).mean(), (rs >= 0).mean())
    inc0 = 'includes 0' if lo <= 0 <= hi else 'excludes 0'
    print(f'{label} (n={len(x)})  expected {expected}')
    print(f'   r = {r0:+.3f}   95% bootstrap CI [{lo:+.3f}, {hi:+.3f}]  ({inc0})')
    print(f'   bootstrap p = {p_boot:.3f}')
    return r0, lo, hi

print('=' * 72)
print(f'BOOTSTRAP ({B:,} resamples, seed=42)')
print('=' * 72)
report_boot('H1  EI x invest | MALE-founded ', ei[gender=='male'],   invest[gender=='male'],  'r<0')
report_boot('H2  EI x invest | FEMALE-founded', ei[gender=='female'], invest[gender=='female'],'r>0')
report_boot('H6  EI x inequality |SV-BU|     ', ei,                    ineq,                    'r<0')

# H6 group difference (Low vs High EI), bootstrap within groups
med = np.median(ei); hi_m = ei >= med; lo_m = ~hi_m
a, b = ineq[lo_m], ineq[hi_m]
diffs = np.array([rng.choice(a, len(a)).mean() - rng.choice(b, len(b)).mean() for _ in range(B)])
lo, hi = np.percentile(diffs, [2.5, 97.5])
print(f'H6  inequality Low-High EI diff = {a.mean()-b.mean():+.3f}  '
      f'95% CI [{lo:+.3f}, {hi:+.3f}]  ({"includes 0" if lo<=0<=hi else "excludes 0"})')

# ---------- sensitivity power analysis ----------
def power_corr(r, n, alpha=0.05):
    """Two-sided power for Pearson r via Fisher z."""
    if n <= 3:
        return np.nan
    lam = np.arctanh(abs(r)) * np.sqrt(n - 3)
    zc = stats.norm.ppf(1 - alpha / 2)
    return (1 - stats.norm.cdf(zc - lam)) + stats.norm.cdf(-zc - lam)

def mdes_corr(n, alpha=0.05, power=0.80):
    zc = stats.norm.ppf(1 - alpha / 2); zp = stats.norm.ppf(power)
    return np.tanh((zc + zp) / np.sqrt(n - 3))

print('\n' + '=' * 72)
print('SENSITIVITY POWER ANALYSIS (alpha=.05 two-tailed, target power=.80)')
print('=' * 72)
print(f'{"Test":34s} {"n":>4s} {"MDES r":>7s} {"pow@.10":>8s} {"pow@.30":>8s}')
for label, n in [('H6  full sample', len(ei)),
                 ('H1  male-founded', (gender=='male').sum()),
                 ('H2  female-founded', (gender=='female').sum())]:
    print(f'{label:34s} {n:4d} {mdes_corr(n):7.2f} '
          f'{power_corr(0.10,n):8.2f} {power_corr(0.30,n):8.2f}')

# two-group inequality test power (Low vs High EI)
tp = TTestIndPower()
n1, n2 = lo_m.sum(), hi_m.sum()
mdes_d = tp.solve_power(effect_size=None, nobs1=n1, alpha=.05, power=.80, ratio=n2/n1, alternative='two-sided')
pow_small = tp.power(effect_size=0.2, nobs1=n1, alpha=.05, ratio=n2/n1, alternative='two-sided')
pow_med = tp.power(effect_size=0.5, nobs1=n1, alpha=.05, ratio=n2/n1, alternative='two-sided')
print(f'\nH6 two-group (Low n={n1} vs High n={n2}): MDES d = {mdes_d:.2f}, '
      f'power@d=0.2 = {pow_small:.2f}, power@d=0.5 = {pow_med:.2f}')

# ---------- power curve figure ----------
apa.apply_apa_style()
fig, ax = plt.subplots(figsize=(6.5, 4.5))
rr = np.linspace(0, 0.6, 200)
for n, ls, lab in [(len(ei), '-', f'H6 full (N={len(ei)})'),
                   ((gender=='male').sum(), '--', f'H1 male (n={(gender=="male").sum()})'),
                   ((gender=='female').sum(), ':', f'H2 female (n={(gender=="female").sum()})')]:
    ax.plot(rr, [power_corr(r, n) for r in rr], ls, color='black', lw=1.5, label=lab)
ax.axhline(0.80, color='grey', lw=0.8, ls='-')
ax.text(0.005, 0.815, '80% power', fontsize=8.5, color='grey')
ax.axvline(0.10, color='grey', lw=0.6, alpha=0.6); ax.text(0.105, 0.05, 'small', fontsize=8, color='grey')
ax.axvline(0.30, color='grey', lw=0.6, alpha=0.6); ax.text(0.305, 0.05, 'medium', fontsize=8, color='grey')
ax.set_xlabel('True effect size (Pearson r)')
ax.set_ylabel('Statistical power')
ax.set_xlim(0, 0.6); ax.set_ylim(0, 1.02)
ax.legend(frameon=False, fontsize=9, loc='lower right')
fig.tight_layout()
apa.save(fig, os.path.join(HERE, 'figures', 'fig04_power_curve'))
print('\nSaved figures/fig04_power_curve.{png,pdf,svg}')
