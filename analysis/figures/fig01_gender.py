#!/usr/bin/env python3
"""Figure: Gender distribution (Q16), APA style, English labels.

Minimal version per request: no axis titles, no note, no figure label.
Keeps category tick labels, y-axis scale, and n + % data labels on bars.
"""
import csv, sys, os
from collections import Counter
import matplotlib as mpl
import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import labels as L

# ---- data ----
SRC = '/home/user/Julia/MasterThesis_cleaned.csv'
with open(SRC, newline='') as f:
    rows = list(csv.reader(f))
names, data = rows[0], rows[3:]
N = len(data)
i_g = names.index('Q16')
c = Counter(r[i_g].strip() for r in data)
cats = [L.GENDER[k] for k in L.GENDER_ORDER]
counts = [c.get(k, 0) for k in L.GENDER_ORDER]
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
})

fig, ax = plt.subplots(figsize=(6.5, 4.5))
x = range(len(cats))
bars = ax.bar(x, counts, width=0.62, color='#D3D3D3',
              edgecolor='black', linewidth=0.8, zorder=3)

# axes: y-axis title + tick labels + scale (no x-axis title)
ax.set_ylabel('Frequency', labelpad=8)
ax.set_xticks(list(x))
ax.set_xticklabels(cats)
ax.set_ylim(0, 110)
ax.set_yticks(range(0, 111, 20))
ax.tick_params(axis='both', length=4)

# data labels: n and %
for rect, n_, p_ in zip(bars, counts, pct):
    ax.text(rect.get_x() + rect.get_width() / 2, rect.get_height() + 1.5,
            f'{n_}\n({p_:.1f}%)', ha='center', va='bottom', fontsize=9.5)

plt.tight_layout()
for ext in ('png', 'pdf', 'svg'):
    fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             f'fig01_gender.{ext}'), dpi=300, bbox_inches='tight')
print('Saved fig01_gender.{png,pdf,svg} | counts:', dict(zip(cats, counts)))
