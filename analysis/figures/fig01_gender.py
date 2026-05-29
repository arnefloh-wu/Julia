#!/usr/bin/env python3
"""Figure: Gender distribution (Q16).

Uses the shared APA bar-chart layout (apa_barchart.py); English labels.
"""
import csv, sys, os
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))   # analysis/  -> labels.py
sys.path.insert(0, HERE)                     # figures/   -> apa_barchart.py
import labels as L
import apa_barchart as apa

# ---- data ----
SRC = '/home/user/Julia/MasterThesis_cleaned.csv'
with open(SRC, newline='') as f:
    rows = list(csv.reader(f))
names, data = rows[0], rows[3:]
N = len(data)
c = Counter(r[names.index('Q16')].strip() for r in data)
cats = [L.GENDER[k] for k in L.GENDER_ORDER]
counts = [c.get(k, 0) for k in L.GENDER_ORDER]

# ---- chart ----
fig, ax = apa.bar_chart(cats, counts, N, ylabel='Frequency')
apa.save(fig, os.path.join(HERE, 'fig01_gender'))
print('Saved fig01_gender.{png,pdf,svg} | counts:', dict(zip(cats, counts)))
