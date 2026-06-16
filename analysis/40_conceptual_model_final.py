#!/usr/bin/env python3
"""Analysis block 40: final publication-ready conceptual model (grey tones).

Cleans up the user's draw.io model: same structure and hypothesis paths, but in
a consistent grey-scale APA palette, overlap-free, with a clear legend.

Roles encoded by greyscale shade (not colour):
  - main-path predictors (industry gender-typing, founder-industry congruence): light grey
  - outcome / dependent variable (capital allocation): medium grey
  - subgroup-boundary constructs (EI, investment experience, participant gender): white
Solid arrow = hypothesised positive effect; dashed arrow onto a path = subgroup
boundary (a simple subgroup effect, not a statistical moderator).
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'figures'))
import apa_barchart as apa
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

HERE = os.path.dirname(os.path.abspath(__file__))
apa.apply_apa_style()

PRED_FC = '#E4E4E4'    # predictors on the main path
OUT_FC = '#C4C4C4'     # outcome (DV)
BOUND_FC = '#FFFFFF'   # subgroup-boundary constructs
EDGE = '#4D4D4D'
SOLID = '#404040'
DASH = '#6E6E6E'
TXT = '#1A1A1A'

fig, ax = plt.subplots(figsize=(11.2, 8.2))
ax.set_xlim(0, 12); ax.set_ylim(0, 8.8); ax.axis('off')


def box(cx, cy, w, h, title, fc, sub=None):
    ax.add_patch(FancyBboxPatch((cx-w/2, cy-h/2), w, h,
                 boxstyle='round,pad=0.02,rounding_size=0.10',
                 fc=fc, ec=EDGE, lw=1.3, zorder=3))
    if sub:
        ax.text(cx, cy+0.16, title, ha='center', va='center', fontsize=11,
                color=TXT, zorder=4)
        ax.text(cx, cy-0.22, sub, ha='center', va='center', fontsize=8.5,
                color='#555555', style='italic', zorder=4)
    else:
        ax.text(cx, cy, title, ha='center', va='center', fontsize=11,
                color=TXT, zorder=4)


def solid(p1, p2):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle='-|>', mutation_scale=16,
                 lw=1.8, color=SOLID, shrinkA=0, shrinkB=0, zorder=2))


def dashed(pts):
    for a, b in zip(pts[:-1], pts[1:]):
        last = b is pts[-1]
        ax.add_patch(FancyArrowPatch(a, b,
                     arrowstyle='-|>' if last else '-', mutation_scale=15,
                     lw=1.6, color=DASH, ls=(0, (5, 3)),
                     shrinkA=0, shrinkB=0, zorder=2))


def lab(x, y, t, fs=10):
    ax.text(x, y, t, ha='center', va='center', fontsize=fs, color=TXT,
            fontweight='bold', zorder=5,
            bbox=dict(boxstyle='round,pad=0.12', fc='white', ec='none', alpha=0.9))


# ── boxes ──
box(2.1, 7.55, 2.8, 1.05, 'Industry\ngender-typing', PRED_FC)
box(2.1, 5.85, 2.8, 1.05, 'Founder–industry\ncongruence', PRED_FC)
box(10.0, 6.95, 2.6, 1.2, 'Capital\nallocation', OUT_FC)
box(2.1, 3.05, 2.8, 1.05, 'Participant gender', BOUND_FC, sub='men score lower on EI')
box(6.05, 3.05, 2.6, 1.05, 'Emotional\nintelligence', BOUND_FC)
box(10.0, 3.05, 2.6, 1.05, 'Investment\nexperience', BOUND_FC)

# ── main-path solid arrows ──
# H1: industry -> capital
solid((3.5, 7.40), (8.72, 7.32))
lab(5.7, 7.55, 'H1 (+)')
# H2: congruence -> capital
solid((3.5, 5.95), (8.72, 6.62))
lab(4.95, 6.34, 'H2 (+)')
# H5: participant gender -> EI
solid((3.5, 3.05), (4.72, 3.05))
lab(4.11, 3.32, 'H5', fs=9.5)

# ── subgroup-boundary dashed arrows ──
# H3: EI boundary onto the H2 path  (meet H2 line at x=6.05)
# H2 line: from (3.5,5.95) to (8.72,6.62): y(x)=5.95+(x-3.5)*(0.67/5.22)
y_on_H2 = 5.95 + (6.05 - 3.5) * (0.67 / 5.22)
dashed([(6.05, 3.58), (6.05, y_on_H2)])
lab(6.05, 5.45, 'H3 (+)', fs=9.5)
# H4: experience boundary onto the H3 path (nested), elbow at y=4.55
dashed([(10.0, 3.58), (10.0, 4.55), (6.15, 4.55)])
lab(8.05, 4.78, 'H4 (+)', fs=9.5)

# ── legend (own clear band at the bottom) ──
lx, ly, lw, lh = 0.55, 0.35, 8.3, 1.45
ax.add_patch(FancyBboxPatch((lx, ly), lw, lh,
             boxstyle='round,pad=0.02,rounding_size=0.06',
             fc='#F7F7F7', ec='#BFBFBF', lw=1.0, zorder=1))
ax.text(lx+0.3, ly+lh-0.30, 'How to read the model', fontsize=10,
        fontweight='bold', va='center', color=TXT)
ax.add_patch(FancyArrowPatch((lx+0.35, ly+0.78), (lx+1.35, ly+0.78),
             arrowstyle='-|>', mutation_scale=14, lw=1.8, color=SOLID, zorder=2))
ax.text(lx+1.6, ly+0.78, '(+) hypothesised positive effect on the outcome',
        fontsize=9, va='center', color=TXT)
ax.add_patch(FancyArrowPatch((lx+0.35, ly+0.32), (lx+1.35, ly+0.32),
             arrowstyle='-|>', mutation_scale=14, lw=1.6, color=DASH,
             ls=(0, (5, 3)), zorder=2))
ax.text(lx+1.6, ly+0.32, 'dashed arrow onto a path = subgroup boundary '
        '(simple effect, not a statistical moderator)', fontsize=9, va='center',
        color=TXT)

fig.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
apa.save(fig, os.path.join(HERE, 'figures', 'fig_conceptual_model_final'))
plt.close(fig)
print('saved fig_conceptual_model_final')
