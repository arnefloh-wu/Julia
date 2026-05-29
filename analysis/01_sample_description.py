#!/usr/bin/env python3
"""Analysis block 1: Sample description.

Strict cleaned dataset (N=187). All output is in English (thesis language);
the raw CSV stays German and is mapped to English via analysis/labels.py.
Demographics: Q16 gender, Q17 age, Q18 nationality, Q19-Q24
(Q25 seat number = administrative, excluded).
"""
import csv, statistics as st, sys, os
from collections import Counter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import labels as L

SRC = '/home/user/Julia/MasterThesis_cleaned.csv'
with open(SRC, newline='') as f:
    rows = list(csv.reader(f))
names, data = rows[0], rows[3:]
N = len(data)
col = {n: names.index(n) for n in
       ['Q16', 'Q17', 'Q18', 'Q19', 'Q20', 'Q21', 'Q22', 'Q23', 'Q24']}

def val(r, q): return r[col[q]].strip()

out = []
def w(s=''): out.append(s)

w(f'# Sample Description (N = {N})\n')

def freq_table(q, title, labelmap=None, order=None):
    c = Counter(val(r, q) for r in data if val(r, q) != '')
    miss = sum(1 for r in data if val(r, q) == '')
    base = sum(c.values())
    w(f'## {title}')
    w(f'valid n = {base}' + (f' (missing = {miss})' if miss else ''))
    w('')
    w('| Category | n | % (valid) |')
    w('|---|---:|---:|')
    keys = order if order else [k for k, _ in c.most_common()]
    for k in keys:
        if k in c:
            disp = labelmap.get(k, k) if labelmap else k
            w(f'| {disp} | {c[k]} | {c[k] / base * 100:.1f} |')
    w('')
    return c

# ---- Q16 gender ----
freq_table('Q16', 'Gender (Q16)', L.GENDER, L.GENDER_ORDER)

# ---- Q17 age (numeric + groups) ----
age_fix = {'20 Jahre': '20'}
ages, groups = [], Counter()
for r in data:
    v = age_fix.get(val(r, 'Q17'), val(r, 'Q17'))
    try:
        a = int(float(v)); ages.append(a)
        g = ('<20' if a < 20 else '20-24' if a < 25 else '25-29' if a < 30
             else '30-39' if a < 40 else '40+')
        groups[g] += 1
    except ValueError:
        if v.lower().startswith(('ü', 'u')) and '40' in v:
            groups['40+'] += 1   # 'Ü40' -> 40+ group only
w('## Age (Q17)')
w(f'numeric n = {len(ages)} (1 response "over 40" counted only in the 40+ group)')
w('')
w(f'- **M = {st.mean(ages):.1f}**, SD = {st.stdev(ages):.1f}, '
  f'Median = {int(st.median(ages))}, Min = {min(ages)}, Max = {max(ages)}')
w('')
w('| Age group | n | % |')
w('|---|---:|---:|')
for g in ['<20', '20-24', '25-29', '30-39', '40+']:
    if groups[g]:
        w(f'| {g} | {groups[g]} | {groups[g] / N * 100:.1f} |')
w('')

# ---- Q18 nationality (normalized, detailed) ----
natc, unmapped = Counter(), []
for r in data:
    v = val(r, 'Q18')
    if v in L.NATIONALITY:
        natc[L.NATIONALITY[v]] += 1
    elif v != '':
        unmapped.append(v)
w('## Nationality (Q18, normalized)')
w(f'valid n = {sum(natc.values())}'
  + (f'  WARNING unmapped: {unmapped}' if unmapped else ''))
w('')
w('| Nationality | n | % |')
w('|---|---:|---:|')
for k, c in natc.most_common():
    w(f'| {k} | {c} | {c / N * 100:.1f} |')
w('')

# ---- Q19-Q24 categoricals ----
freq_table('Q19', 'Highest Completed Education (Q19)', L.EDUCATION, L.EDUCATION_ORDER)
freq_table('Q20', 'Degree Currently Pursued (Q20)', L.DEGREE, L.DEGREE_ORDER)
freq_table('Q21', 'Field of Study (Q21)', L.FIELD)
freq_table('Q22', 'Enrolled at WU Vienna (Q22)', L.YESNO, ['Ja', 'Nein'])
freq_table('Q23', 'Experience with Financial Investments (Q23)', L.YESNO, ['Ja', 'Nein'])
freq_table('Q24', 'Entrepreneurial Experience (Q24)', L.YESNO, ['Ja', 'Nein'])

text = '\n'.join(out)
print(text)
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       '01_sample_description.md'), 'w') as f:
    f.write(text + '\n')
