#!/usr/bin/env python3
"""Analysis block 37: paper-ready figure set for the FINAL hypothesis order.

H1: Startups in male-dominated industries receive higher investment than in
    female-dominated industries            (industry effect, within-subjects)
H2: Male founders in male-dominated industries receive higher investment than
    female founders in female-dominated industries   (masculine- vs feminine-
    congruent, full sample, between-subjects)
H3: Among lower-EI investors, masculine-congruent > feminine-congruent
H4: Among lower-EI investors without investment experience,
    masculine-congruent > feminine-congruent
H5: Male participants score lower on EI than female participants

One clean, consistent, overlap-free two-bar figure per hypothesis. Numbers are
computed here so they are guaranteed correct and mutually consistent.
"""
import csv, re, os, sys
import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'figures'))
import apa_barchart as apa
import matplotlib.pyplot as plt

with open(os.path.join(HERE, '..', 'MasterThesis_cleaned.csv'), newline='') as f:
    rows = list(csv.reader(f))
names, data = rows[0], rows[3:]
L = lambda v: int(re.match(r'\s*(\d+)', v.strip()).group(1))
colp = lambda p: [i for i, n in enumerate(names) if n.startswith(p) and '_DO' not in n]
eic = colp('Q10 (SEA)') + colp('Q11 (OEA)') + colp('Q12 (UOE)') + colp('Q13 (ROE)')
ei = np.array([[L(r[i]) for i in eic] for r in data], float).mean(1)
sv = np.array([float(r[names.index('invest_sv')]) for r in data])
bu = np.array([float(r[names.index('invest_bu')]) for r in data])
g = np.array([r[names.index('team_gender')] for r in data])
exp = np.array([r[names.index('Q23')] for r in data])
resp = np.array([r[names.index('Q16')].strip() for r in data])
MED = np.median(ei)

apa.apply_apa_style()
DARK, GREY = '#808080', '#D3D3D3'


def two_bar(fname, title, labels, m, se, n, colors, annot, ymax, yticks=None,
            ylabel='Mean amount invested (0–3)'):
    """Consistent, overlap-free two-bar chart with a significance bracket."""
    fig, ax = plt.subplots(figsize=(5.6, 5.0))
    bars = ax.bar([0, 1], m, 0.58, yerr=se, capsize=4,
                  color=colors, edgecolor='black', linewidth=0.9,
                  error_kw=dict(lw=1.0, capthick=1.0), zorder=3)
    # value label ABOVE the error-bar cap (never overlaps the bar or whisker)
    lab_off = ymax * 0.022
    for rect, v, s in zip(bars, m, se):
        ax.text(rect.get_x()+rect.get_width()/2, v + s + lab_off,
                f'{v:.2f}', ha='center', va='bottom', fontsize=11, zorder=4)
    # n inside the bar, near the base, white
    for rect, nn in zip(bars, n):
        ax.text(rect.get_x()+rect.get_width()/2, ymax*0.035,
                f'n = {nn}', ha='center', va='bottom', fontsize=9,
                color='white', zorder=4)
    # significance bracket above the taller value label
    top = max(mi + si for mi, si in zip(m, se)) + lab_off
    yb = top + ymax * 0.085
    ax.plot([0, 0, 1, 1], [yb, yb + ymax*0.02, yb + ymax*0.02, yb],
            color='black', lw=1.0, zorder=4)
    ax.text(0.5, yb + ymax*0.035, annot, ha='center', va='bottom',
            fontsize=9.5, zorder=4)
    ax.set_xticks([0, 1]); ax.set_xticklabels(labels, fontsize=10.5)
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, ymax)
    if yticks is not None:
        ax.set_yticks(yticks)
    ax.set_title(title, fontsize=11.5, fontweight='bold', pad=10)
    fig.tight_layout()
    apa.save(fig, os.path.join(HERE, 'figures', fname))
    plt.close(fig)
    print('saved', fname)


def welch(a, b, one_tailed=False):
    n1, n2 = len(a), len(b)
    m1, m2, s1, s2 = a.mean(), b.mean(), a.std(ddof=1), b.std(ddof=1)
    t, p2 = stats.ttest_ind(a, b, equal_var=False)
    dfw = (s1**2/n1 + s2**2/n2)**2 / ((s1**2/n1)**2/(n1-1) + (s2**2/n2)**2/(n2-1))
    sp = np.sqrt(((n1-1)*s1**2 + (n2-1)*s2**2) / (n1+n2-2))
    d = (m1 - m2) / sp
    p1 = p2/2 if t > 0 else 1 - p2/2
    return dict(m1=m1, m2=m2, se1=s1/np.sqrt(n1), se2=s2/np.sqrt(n2),
                n1=n1, n2=n2, t=t, dfw=dfw, d=d, p=p1 if one_tailed else p2)


def ptxt(p):
    return 'p < .001' if p < .001 else f'p = {p:.3f}'


# ───────────── H1: industry effect (within-subjects, paired, one-tailed) ─────────────
t1, p1two = stats.ttest_rel(sv, bu)
p1 = p1two / 2 if t1 > 0 else 1 - p1two / 2   # directional: SiteVision > BalanceUp
dz = (sv - bu).mean() / (sv - bu).std(ddof=1)
two_bar(
    'fig_H1', 'H1: Investment by industry type',
    ['SiteVision\n(male-typed)', 'BalanceUp\n(female-typed)'],
    [sv.mean(), bu.mean()],
    [sv.std(ddof=1)/np.sqrt(len(sv)), bu.std(ddof=1)/np.sqrt(len(bu))],
    [len(sv), len(bu)], [DARK, GREY],
    f'Paired t(186) = {t1:.2f},  {ptxt(p1)} (one-tailed),  d$_z$ = {dz:.2f}', 3.0)

# ───────────── H2: masculine- vs feminine-congruent, full sample ─────────────
masc_f = sv[g == 'male']; fem_f = bu[g == 'female']
r2 = welch(masc_f, fem_f, one_tailed=True)
two_bar(
    'fig_H2', 'H2: Masculine- vs. feminine-congruent founders',
    ['Masculine-\ncongruent', 'Feminine-\ncongruent'],
    [r2['m1'], r2['m2']], [r2['se1'], r2['se2']], [r2['n1'], r2['n2']],
    [DARK, GREY],
    f"Welch t({r2['dfw']:.0f}) = {r2['t']:.2f},  {ptxt(r2['p'])} (one-tailed),  d = {r2['d']:.2f}",
    3.0)

# ───────────── H3: lower-EI subgroup ─────────────
masc3 = sv[(g == 'male') & (ei < MED)]; fem3 = bu[(g == 'female') & (ei < MED)]
r3 = welch(masc3, fem3, one_tailed=True)
two_bar(
    'fig_H3', 'H3: Congruity preference among lower-EI investors',
    ['Masculine-\ncongruent', 'Feminine-\ncongruent'],
    [r3['m1'], r3['m2']], [r3['se1'], r3['se2']], [r3['n1'], r3['n2']],
    [DARK, GREY],
    f"Welch t({r3['dfw']:.0f}) = {r3['t']:.2f},  {ptxt(r3['p'])} (one-tailed),  d = {r3['d']:.2f}",
    3.0)

# ───────────── H4: lower-EI + no investment experience ─────────────
mask4 = (ei < MED) & (exp == 'Nein')
masc4 = sv[(g == 'male') & mask4]; fem4 = bu[(g == 'female') & mask4]
r4 = welch(masc4, fem4, one_tailed=False)
two_bar(
    'fig_H4', 'H4: Congruity preference (lower-EI, no experience)',
    ['Masculine-\ncongruent', 'Feminine-\ncongruent'],
    [r4['m1'], r4['m2']], [r4['se1'], r4['se2']], [r4['n1'], r4['n2']],
    [DARK, GREY],
    f"Welch t({r4['dfw']:.0f}) = {r4['t']:.2f},  {ptxt(r4['p'])},  d = {r4['d']:.2f}",
    3.0)

# ───────────── H5: EI by participant gender ─────────────
eim = ei[resp == 'Männlich']; eif = ei[resp == 'Weiblich']
r5 = welch(eim, eif, one_tailed=False)
two_bar(
    'fig_H5', 'H5: Emotional intelligence by participant gender',
    ['Male\nparticipants', 'Female\nparticipants'],
    [r5['m1'], r5['m2']], [r5['se1'], r5['se2']], [r5['n1'], r5['n2']],
    [DARK, GREY],
    f"Welch t({r5['dfw']:.0f}) = {abs(r5['t']):.2f},  {ptxt(r5['p'])},  d = {abs(r5['d']):.2f}",
    7.0, yticks=range(0, 8), ylabel='Mean WLEIS score (1–7)')

print('\nValues used:')
print(f"H1 SiteVision {sv.mean():.2f} / BalanceUp {bu.mean():.2f}")
print(f"H2 masc {r2['m1']:.2f} (n{r2['n1']}) / fem {r2['m2']:.2f} (n{r2['n2']})")
print(f"H3 masc {r3['m1']:.2f} (n{r3['n1']}) / fem {r3['m2']:.2f} (n{r3['n2']})")
print(f"H4 masc {r4['m1']:.2f} (n{r4['n1']}) / fem {r4['m2']:.2f} (n{r4['n2']})")
print(f"H5 male {r5['m1']:.2f} (n{r5['n1']}) / female {r5['m2']:.2f} (n{r5['n2']})")
