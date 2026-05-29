#!/usr/bin/env python3
"""Figure 1: Gender distribution (Q16) in APA style.
Baseline version - to be polished later."""
import csv
from collections import Counter
import matplotlib as mpl
import matplotlib.pyplot as plt

# ---- data ----
SRC = '/home/user/Julia/MasterThesis_cleaned.csv'
with open(SRC, newline='') as f:
    rows = list(csv.reader(f))
names, data = rows[0], rows[3:]
N = len(data)
i_g = names.index('Q16')
order = ['Weiblich', 'Männlich', 'Nicht-binär', 'Keine Angabe']
c = Counter(r[i_g].strip() for r in data)
counts = [c.get(k, 0) for k in order]
pct = [v / N * 100 for v in counts]

# ---- APA style ----
mpl.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Liberation Sans', 'Arial', 'DejaVu Sans'],
    'font.size': 11,
    'axes.edgecolor': 'black',
    'axes.linewidth': 0.8,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'xtick.direction': 'out',
    'ytick.direction': 'out',
    'figure.dpi': 100,
})

fig, ax = plt.subplots(figsize=(6.5, 4.5))
x = range(len(order))
bars = ax.bar(x, counts, width=0.62, color='#666666',
              edgecolor='black', linewidth=0.8, zorder=3)

# axes
ax.set_ylabel('Häufigkeit', labelpad=8)
ax.set_xlabel('Geschlecht', labelpad=8)
ax.set_xticks(list(x))
ax.set_xticklabels(order)
ax.set_ylim(0, 110)
ax.set_yticks(range(0, 111, 20))
ax.tick_params(axis='both', length=4)

# data labels: n and %
for rect, n_, p_ in zip(bars, counts, pct):
    ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height() + 1.5,
            f'{n_}\n({p_:.1f}%)', ha='center', va='bottom', fontsize=9.5)

# APA figure number + title (above plot)
fig.text(0.125, 0.965, 'Abbildung 1', fontweight='bold', fontsize=11, ha='left')
fig.text(0.125, 0.925, 'Geschlechterverteilung der Stichprobe',
         fontstyle='italic', fontsize=11, ha='left')
# APA note (below plot)
fig.text(0.125, 0.015, f'Anmerkung. N = {N}.', fontsize=9.5, ha='left')

plt.subplots_adjust(top=0.86, bottom=0.13, left=0.125, right=0.97)

for ext in ('png', 'pdf', 'svg'):
    fig.savefig(f'/home/user/Julia/analysis/figures/fig01_gender.{ext}',
                dpi=300, bbox_inches='tight')
print('Saved fig01_gender.{png,pdf,svg} | counts:', dict(zip(order, counts)))
