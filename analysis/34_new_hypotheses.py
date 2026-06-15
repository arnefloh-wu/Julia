#!/usr/bin/env python3
"""Analysis block 34: comprehensive assessment of the new H1-H5 hypothesis set.
Computes all statistics, robustness/confound models, generates one figure per
hypothesis, and writes the full Word report (34_new_hypotheses_report.docx).

H1 Industry effect: male-typed > female-typed industry (within-person)
H2 Masculine-congruent > feminine-congruent (male founder/male ind vs female/female)
H3 EI moderates the masc-vs-fem congruent gap (lower EI -> larger gap)
H4 Male participants score lower on EI than female participants
H5 Among low-EI, investment experience shrinks the masc-vs-fem gap
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
exp = np.array([r[col('Q23')].strip() for r in data])
male, female = g == 'male', g == 'female'
DIMS = {'SEA': cols_for('Q10 (SEA)'), 'OEA': cols_for('Q11 (OEA)'),
        'UOE': cols_for('Q12 (UOE)'), 'ROE': cols_for('Q13 (ROE)')}
ei = mat(sum(DIMS.values(), []))
eidim = {k: mat(c) for k, c in DIMS.items()}
succ_sv, succ_bu = arr(col('Q5')), arr(col('Q47'))
N = len(data)
apa.apply_apa_style()
GREY, DARK = '#D3D3D3', '#808080'

def cohen_d_ind(a, b):
    n1, n2 = len(a), len(b)
    sp = np.sqrt(((n1-1)*a.var(ddof=1)+(n2-1)*b.var(ddof=1))/(n1+n2-2))
    return (a.mean()-b.mean())/sp
def welch_ci(a, b):
    n1, n2 = len(a), len(b); s1, s2 = a.var(ddof=1), b.var(ddof=1)
    se = np.sqrt(s1/n1+s2/n2)
    dfw = (s1/n1+s2/n2)**2/((s1/n1)**2/(n1-1)+(s2/n2)**2/(n2-1))
    tc = stats.t.ppf(.975, dfw); diff = a.mean()-b.mean()
    return diff, se, dfw, (diff-tc*se, diff+tc*se)

R = {}   # results store

# ══════════════ H1: industry effect (within-person) ══════════════
d1 = sv - bu
t1, p1 = stats.ttest_rel(sv, bu)
se1 = d1.std(ddof=1)/np.sqrt(N); dz = d1.mean()/d1.std(ddof=1)
ci1 = (d1.mean()-stats.t.ppf(.975, N-1)*se1, d1.mean()+stats.t.ppf(.975, N-1)*se1)
# confound model (long): success + order
long = pd.DataFrame({'invest': np.concatenate([sv, bu]),
                     'industry': [1]*N+[0]*N,
                     'succ': np.concatenate([succ_sv, succ_bu]),
                     'svfirst': np.tile((order=='sv_first').astype(int), 2)})
m1_succ = smf.ols('invest ~ industry + succ', data=long).fit()
m1_ord = smf.ols('invest ~ industry * svfirst', data=long).fit()
R['H1'] = dict(mean=d1.mean(), se=se1, t=t1, df=N-1, p=p1, ci=ci1, dz=dz,
               sv=sv.mean(), bu=bu.mean(), svsd=sv.std(ddof=1), busd=bu.std(ddof=1),
               p_succ=m1_succ.pvalues['industry'], b_succ=m1_succ.params['industry'],
               int_b=m1_ord.params['industry:svfirst'], int_p=m1_ord.pvalues['industry:svfirst'])
print('H1', R['H1'])

# ══════════════ H2: masc-congruent vs fem-congruent ══════════════
masc = sv[male]; fem = bu[female]
t2, p2_2 = stats.ttest_ind(masc, fem, equal_var=False)
p2_1 = p2_2/2 if t2 > 0 else 1-p2_2/2
diff2, se2, dfw2, ci2 = welch_ci(masc, fem)
d2 = cohen_d_ind(masc, fem)
u2, pmw2 = stats.mannwhitneyu(masc, fem, alternative='greater')
# confound: OLS with success + order
foc_succ = np.concatenate([succ_sv[male], succ_bu[female]])
foc_ord = np.concatenate([(order[male]=='sv_first').astype(int),
                          (order[female]=='sv_first').astype(int)])
dfc = pd.DataFrame({'invest': np.concatenate([masc, fem]),
                    'masc': [1]*len(masc)+[0]*len(fem),
                    'succ': foc_succ, 'svfirst': foc_ord})
m2_succ = smf.ols('invest ~ masc + succ', data=dfc).fit()
m2_ord = smf.ols('invest ~ masc * svfirst', data=dfc).fit()
R['H2'] = dict(masc=masc.mean(), fem=fem.mean(), mascsd=masc.std(ddof=1), femsd=fem.std(ddof=1),
               n1=len(masc), n2=len(fem), diff=diff2, se=se2, t=t2, df=dfw2,
               p2=p2_2, p1=p2_1, ci=ci2, d=d2, pmw=pmw2,
               p_succ=m2_succ.pvalues['masc'], b_succ=m2_succ.params['masc'],
               int_b=m2_ord.params['masc:svfirst'], int_p=m2_ord.pvalues['masc:svfirst'])
print('H2', R['H2'])

# ══════════════ H3: EI moderation of congruent gap (continuous) ══════════════
keep = male | female
focal = np.where(male, sv, bu)[keep]
typ = male[keep].astype(int)               # 1=masc-congruent
eik = ei[keep]
df3 = pd.DataFrame({'focal': focal, 'masc': typ, 'ei': eik - eik.mean(),
                    'succ': np.where(male, succ_sv, succ_bu)[keep],
                    'svfirst': (order[keep]=='sv_first').astype(int)})
m3 = smf.ols('focal ~ masc * ei', data=df3).fit()
ib3, ip3 = m3.params['masc:ei'], m3.pvalues['masc:ei']
se3 = m3.bse['masc:ei']
ci3 = m3.conf_int().loc['masc:ei'].tolist()
# robustness: + success + order interaction controls
m3b = smf.ols('focal ~ masc * ei + succ + svfirst', data=df3).fit()
# per-dimension interactions
dimres = {}
for k, x in eidim.items():
    xk = x[keep]
    dd = pd.DataFrame({'focal': focal, 'masc': typ, 'x': xk-xk.mean()})
    mm = smf.ols('focal ~ masc * x', data=dd).fit()
    dimres[k] = (mm.params['masc:x'], mm.pvalues['masc:x'])
# median-split gap for interpretation/figure
medei = np.median(eik); hi = eik >= medei
gap_low = focal[(typ==1)&~hi].mean() - focal[(typ==0)&~hi].mean()
gap_high = focal[(typ==1)&hi].mean() - focal[(typ==0)&hi].mean()
R['H3'] = dict(b=ib3, se=se3, t=m3.tvalues['masc:ei'], p=ip3, ci=ci3,
               r2=m3.rsquared, r2a=m3.rsquared_adj, n=len(focal),
               gap_low=gap_low, gap_high=gap_high, dimres=dimres,
               p_ctrl=m3b.pvalues['masc:ei'], b_ctrl=m3b.params['masc:ei'])
print('H3', R['H3'])

# ══════════════ H4: EI by participant gender ══════════════
mp, fp = resp == 'Männlich', resp == 'Weiblich'
t4, p4 = stats.ttest_ind(ei[mp], ei[fp], equal_var=False)
diff4, se4, dfw4, ci4 = welch_ci(ei[mp], ei[fp])
d4 = cohen_d_ind(ei[mp], ei[fp])
dim4 = {}
for k, x in eidim.items():
    tt, pp = stats.ttest_ind(x[mp], x[fp], equal_var=False)
    dim4[k] = (x[mp].mean(), x[fp].mean(), tt, pp, cohen_d_ind(x[mp], x[fp]))
# covariate-adjusted (age, STEM)
def age_of(r):
    m = re.search(r'\d+', r[col('Q17')]); return float(m.group()) if m else np.nan
age = np.array([age_of(r) for r in data])
STEM = {'Naturwissenschaften','Wirtschaftsinformatik','Ingenieurwesen / Technische Wissenschaften','Informatik'}
stem = np.array([1 if r[col('Q21')].strip() in STEM else 0 for r in data])
mwp = mp | fp
df4 = pd.DataFrame({'ei': ei[mwp], 'female': fp[mwp].astype(int), 'age': age[mwp], 'stem': stem[mwp]}).dropna()
m4adj = smf.ols('ei ~ female + age + stem', data=df4).fit()
R['H4'] = dict(m_mean=ei[mp].mean(), f_mean=ei[fp].mean(), m_sd=ei[mp].std(ddof=1), f_sd=ei[fp].std(ddof=1),
               nm=mp.sum(), nf=fp.sum(), diff=diff4, se=se4, t=t4, df=dfw4, p=p4, ci=ci4, d=d4,
               dim=dim4, adj_b=m4adj.params['female'], adj_p=m4adj.pvalues['female'])
print('H4', R['H4'])

# ══════════════ H5: low-EI, experience shrinks masc-fem gap ══════════════
low = ei < np.median(ei)
sub = (male | female) & low
fl = np.where(male, sv, bu)[sub]
tl = male[sub].astype(int)
el = exp[sub]
df5 = pd.DataFrame({'focal': fl, 'masc': tl, 'exp': el})
df5 = df5[df5.exp.isin(['Ja', 'Nein'])].copy()
df5['hasexp'] = (df5.exp == 'Ja').astype(int)
m5 = smf.ols('focal ~ masc * hasexp', data=df5).fit()
ib5, ip5 = m5.params['masc:hasexp'], m5.pvalues['masc:hasexp']
se5 = m5.bse['masc:hasexp']; ci5 = m5.conf_int().loc['masc:hasexp'].tolist()
# subgroup gaps
def gap(mask):
    a = df5.focal[(df5.masc==1)&mask]; b = df5.focal[(df5.masc==0)&mask]
    return a.mean()-b.mean(), len(a), len(b)
gap_exp = gap(df5.hasexp==1); gap_noexp = gap(df5.hasexp==0)
R['H5'] = dict(b=ib5, se=se5, t=m5.tvalues['masc:hasexp'], p=ip5, ci=ci5,
               r2=m5.rsquared, r2a=m5.rsquared_adj, n=len(df5),
               gap_exp=gap_exp, gap_noexp=gap_noexp)
print('H5', R['H5'])

# ════════════════════════ FIGURES ════════════════════════
def savefig(fig, stem): apa.save(fig, os.path.join(HERE, 'figures', stem))

# H1 figure
fig, ax = plt.subplots(figsize=(5.6, 4.6))
mns = [sv.mean(), bu.mean()]; ses = [sv.std(ddof=1)/np.sqrt(N), bu.std(ddof=1)/np.sqrt(N)]
b = ax.bar([0,1], mns, 0.6, yerr=ses, capsize=4, color=[DARK, GREY], edgecolor='black',
           linewidth=0.8, zorder=3, error_kw=dict(lw=0.9))
for r_, v in zip(b, mns): ax.text(r_.get_x()+r_.get_width()/2, v+0.03, f'{v:.2f}', ha='center', fontsize=10)
yb = max(mns)+0.3
ax.plot([0,0,1,1],[yb,yb+.05,yb+.05,yb], color='black', lw=.9)
ax.text(.5, yb+.07, f'p < .001, d_z = {dz:.2f}', ha='center', fontsize=9)
ax.set_xticks([0,1]); ax.set_xticklabels(['SiteVision\n(male-typed)', 'BalanceUp\n(female-typed)'])
ax.set_ylabel('Mean amount invested (0–3)'); ax.set_ylim(0, 3); ax.set_title('H1: Industry effect', fontsize=11)
fig.tight_layout(); savefig(fig, 'figH1_industry'); plt.close(fig)

# H2 figure
fig, ax = plt.subplots(figsize=(5.6, 4.6))
mns = [masc.mean(), fem.mean()]; ses = [masc.std(ddof=1)/np.sqrt(len(masc)), fem.std(ddof=1)/np.sqrt(len(fem))]
b = ax.bar([0,1], mns, 0.6, yerr=ses, capsize=4, color=[DARK, GREY], edgecolor='black',
           linewidth=0.8, zorder=3, error_kw=dict(lw=0.9))
for r_, v in zip(b, mns): ax.text(r_.get_x()+r_.get_width()/2, v+0.03, f'{v:.2f}', ha='center', fontsize=10)
yb = max(mns)+0.3
ax.plot([0,0,1,1],[yb,yb+.05,yb+.05,yb], color='black', lw=.9)
ax.text(.5, yb+.07, f'p = {p2_2:.3f}, d = {d2:.2f}', ha='center', fontsize=9)
ax.set_xticks([0,1]); ax.set_xticklabels(['Masculine-congruent\n(male founder /\nmale industry)', 'Feminine-congruent\n(female founder /\nfemale industry)'])
ax.set_ylabel('Mean amount invested (0–3)'); ax.set_ylim(0, 3); ax.set_title('H2: Congruent-cell comparison', fontsize=11)
fig.tight_layout(); savefig(fig, 'figH2_congruent'); plt.close(fig)

# H3 figure: gap at low vs high EI
fig, ax = plt.subplots(figsize=(6.0, 4.6))
b = ax.bar([0,1], [gap_low, gap_high], 0.6, color=[GREY, DARK], edgecolor='black', linewidth=0.8, zorder=3)
for r_, v in zip(b, [gap_low, gap_high]): ax.text(r_.get_x()+r_.get_width()/2, v+0.01, f'{v:+.2f}', ha='center', fontsize=10)
ax.axhline(0, color='black', lw=0.8)
ax.set_xticks([0,1]); ax.set_xticklabels(['Lower EI\n(below median)', 'Higher EI\n(at/above median)'])
ax.set_ylabel('Congruence gap\n(masculine − feminine investment)')
ax.set_title(f'H3: EI × congruence interaction (b = {ib3:+.2f}, p = {ip3:.2f}, ns)', fontsize=10)
fig.tight_layout(); savefig(fig, 'figH3_ei_moderation'); plt.close(fig)

# H4 figure: EI by gender across dims
fig, ax = plt.subplots(figsize=(7.0, 4.6))
dims = ['Total','SEA','OEA','UOE','ROE']
allei = {'Total': ei, **eidim}
mm = [allei[d][mp].mean() for d in dims]; ff = [allei[d][fp].mean() for d in dims]
mse = [allei[d][mp].std(ddof=1)/np.sqrt(mp.sum()) for d in dims]
fse = [allei[d][fp].std(ddof=1)/np.sqrt(fp.sum()) for d in dims]
x = np.arange(5); bw = 0.38
ax.bar(x-bw/2, mm, bw*.95, yerr=mse, capsize=3, label='Male participants', color=DARK, edgecolor='black', linewidth=.8, zorder=3, error_kw=dict(lw=.8))
ax.bar(x+bw/2, ff, bw*.95, yerr=fse, capsize=3, label='Female participants', color=GREY, edgecolor='black', linewidth=.8, zorder=3, error_kw=dict(lw=.8))
star = lambda p: '***' if p<.001 else '**' if p<.01 else '*' if p<.05 else 'ns'
pmap = {'Total': p4, **{k: dim4[k][3] for k in eidim}}
for xi, d in zip(x, dims):
    ax.text(xi, max(mm[dims.index(d)], ff[dims.index(d)])+0.55, star(pmap[d]), ha='center', fontsize=9)
ax.set_xticks(x); ax.set_xticklabels(dims); ax.set_ylabel('Mean WLEIS score (1–7)')
ax.set_ylim(0, 7.2); ax.legend(frameon=False, fontsize=9, loc='lower right'); ax.set_title('H4: EI by participant gender', fontsize=11)
fig.tight_layout(); savefig(fig, 'figH4_ei_gender'); plt.close(fig)

# H5 figure: masc-fem gap by experience (low-EI)
fig, ax = plt.subplots(figsize=(6.0, 4.6))
vals = [gap_noexp[0], gap_exp[0]]
b = ax.bar([0,1], vals, 0.6, color=[GREY, DARK], edgecolor='black', linewidth=0.8, zorder=3)
for r_, v in zip(b, vals): ax.text(r_.get_x()+r_.get_width()/2, v+0.01, f'{v:+.2f}', ha='center', fontsize=10)
ax.axhline(0, color='black', lw=0.8)
ax.set_xticks([0,1]); ax.set_xticklabels([f'No investment\nexperience\n(n={gap_noexp[1]}+{gap_noexp[2]})',
                                          f'Has investment\nexperience\n(n={gap_exp[1]}+{gap_exp[2]})'])
ax.set_ylabel('Congruence gap\n(masculine − feminine investment)')
ax.set_title(f'H5: experience × congruence (low-EI)\nb = {ib5:+.2f}, p = {ip5:.2f}, ns', fontsize=10)
fig.tight_layout(); savefig(fig, 'figH5_experience'); plt.close(fig)
print('Figures saved.')

# save results for the doc builder
import json
with open(os.path.join(HERE, '_h_results.json'), 'w') as f:
    json.dump({k: {kk: (vv if not isinstance(vv, (np.floating, np.integer)) else float(vv))
                   for kk, vv in v.items() if not isinstance(vv, dict) and not isinstance(vv, tuple)}
               for k, v in R.items()}, f, indent=2, default=str)
print('Done analysis.')
