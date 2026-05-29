#!/usr/bin/env python3
"""Analysis block 1: Sample description (Stichprobenbeschreibung).
Reads the strict cleaned dataset (N=187) and produces demographic frequencies.
Demographics: Q16 gender, Q17 age, Q18 nationality, Q19-Q24, (Q25 seat = admin, excluded)."""
import csv, statistics as st
from collections import Counter

SRC = '/home/user/Julia/MasterThesis_cleaned.csv'
with open(SRC, newline='') as f:
    rows = list(csv.reader(f))
names, data = rows[0], rows[3:]
N = len(data)
col = {n: names.index(n) for n in
       ['Q16','Q17','Q18','Q19','Q20','Q21','Q22','Q23','Q24']}

def val(r, q): return r[col[q]].strip()

out = []
def w(s=''): out.append(s)

w(f'# Stichprobenbeschreibung (N = {N})\n')

# ---- Q16 Gender ----
def freq_table(q, title, order=None):
    c = Counter(val(r, q) for r in data if val(r, q) != '')
    miss = sum(1 for r in data if val(r, q) == '')
    base = sum(c.values())
    w(f'## {title}')
    w(f'gültig n = {base}' + (f' (fehlend = {miss})' if miss else ''))
    w('')
    w('| Kategorie | n | % (gültig) |')
    w('|---|---:|---:|')
    keys = order if order else [k for k,_ in c.most_common()]
    for k in keys:
        if k in c:
            w(f'| {k} | {c[k]} | {c[k]/base*100:.1f} |')
    w('')
    return c

freq_table('Q16', 'Geschlecht (Q16)',
           order=['Weiblich','Männlich','Nicht-binär','Keine Angabe'])

# ---- Q17 Age (numeric + groups) ----
age_fix = {'20 Jahre':'20'}      # obvious recode
ages, nonspec = [], 0
groups = Counter()
for r in data:
    v = val(r,'Q17'); v = age_fix.get(v, v)
    try:
        a = int(float(v)); ages.append(a)
        g = ('<20' if a<20 else '20–24' if a<25 else '25–29' if a<30
             else '30–39' if a<40 else '40+')
        groups[g]+=1
    except ValueError:
        nonspec += 1
        if v.lower().startswith(('ü','u')) and '40' in v:
            groups['40+'] += 1   # 'Ü40' -> 40+
w('## Alter (Q17)')
w(f'numerisch auswertbar n = {len(ages)} (1 Angabe "Ü40" nur als Gruppe 40+ gewertet)')
w('')
w(f'- **M = {st.mean(ages):.1f}**, SD = {st.stdev(ages):.1f}, '
  f'Median = {int(st.median(ages))}, Min = {min(ages)}, Max = {max(ages)}')
w('')
w('| Altersgruppe | n | % |')
w('|---|---:|---:|')
for g in ['<20','20–24','25–29','30–39','40+']:
    if groups[g]: w(f'| {g} | {groups[g]} | {groups[g]/N*100:.1f} |')
w('')

# ---- Q18 Nationality (normalized, detailed) ----
NAT = {
 'Deutsch':'Deutsch','deutsch':'Deutsch','Deutschland':'Deutsch','ger':'Deutsch','German':'Deutsch',
 'Österreich':'Österreichisch','österreichisch':'Österreichisch','Österreichisch':'Österreichisch',
 'AT':'Österreichisch','AUT':'Österreichisch','Austria':'Österreichisch','Oesterreich':'Österreichisch',
 'Österrreich':'Österreichisch','österreicherin':'Österreichisch',
 'Ukraine':'Ukrainisch','Ukrainische':'Ukrainisch','Ukrainerin':'Ukrainisch','Ukrainisch':'Ukrainisch',
 'Bulgarien':'Bulgarisch','Bulgarisch':'Bulgarisch','bulgarisch':'Bulgarisch','Bulgarian':'Bulgarisch',
 'Russisch':'Russisch','Russin':'Russisch','Russiche Föderation':'Russisch','RUS':'Russisch',
 'Rumänien':'Rumänisch','Ungarn':'Ungarisch','Ungarisch':'Ungarisch','ungarisch':'Ungarisch','ungarn':'Ungarisch',
 'Slowakei':'Slowakisch','slowakei':'Slowakisch','Slowakisch':'Slowakisch',
 'Italien':'Italienisch','Italienisch':'Italienisch','Italien (Südtirol)':'Italienisch',
 'Indien':'Indisch','türkisch':'Türkisch','Türkisch':'Türkisch','Polnisch':'Polnisch','Polen':'Polnisch',
 'Kroatien':'Kroatisch','Serbisch':'Serbisch','Schwedisch':'Schwedisch','Lettland':'Lettisch',
 'USA':'US-amerikanisch','Luxemburgisch':'Luxemburgisch','Kolumbien':'Kolumbianisch','Albanien':'Albanisch',
 'Tschetschenisch':'Tschetschenisch','Bosnien und Herzegowina':'Bosnisch','schweiz':'Schweizerisch',
 'Kasach':'Kasachisch','Portuguese':'Portugiesisch','guatemala':'Guatemaltekisch','Guatemala City':'Guatemaltekisch',
 'D,NL':'Deutsch & Niederländisch','Österreich, Kroatien':'Österreichisch & Kroatisch',
 'AT & NL':'Österreichisch & Niederländisch','bulgarisch, türkisch':'Bulgarisch & Türkisch',
 'Ungarisch, Deutsch':'Ungarisch & Deutsch',
}
natc, unmapped = Counter(), []
for r in data:
    v = val(r,'Q18')
    if v in NAT: natc[NAT[v]] += 1
    elif v=='' : pass
    else: unmapped.append(v)
w('## Nationalität (Q18, normalisiert)')
w(f'gültig n = {sum(natc.values())}' + (f'  ⚠ nicht zugeordnet: {unmapped}' if unmapped else ''))
w('')
w('| Nationalität | n | % |')
w('|---|---:|---:|')
for k,c in natc.most_common():
    w(f'| {k} | {c} | {c/N*100:.1f} |')
w('')

# ---- Q19-Q24 categoricals ----
freq_table('Q19','Höchster abgeschlossener Bildungsabschluss (Q19)',
           order=['Matura / Abitur / Hochschulreife','Bachelor','Master','Lehre / Berufsausbildung'])
freq_table('Q20','Aktuell angestrebter Abschluss (Q20)',
           order=['Bachelor','Master','PhD / Doktorat','Sonstige Ausbildung','Ich strebe derzeit keinen Abschluss an'])
freq_table('Q21','Studienfach (Q21)')
freq_table('Q22','Studium an der WU Wien (Q22)', order=['Ja','Nein'])
freq_table('Q23','Erfahrung mit Finanzinvestitionen (Q23)', order=['Ja','Nein'])
freq_table('Q24','Gründungserfahrung (Q24)', order=['Ja','Nein'])

text = '\n'.join(out)
print(text)
with open('/home/user/Julia/analysis/01_sample_description.md','w') as f:
    f.write(text + '\n')
