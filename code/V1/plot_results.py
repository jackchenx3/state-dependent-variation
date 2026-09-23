"""Plot stored results with Matplotlib. No simulation or fitted predictions."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT=Path(__file__).resolve().parent
r=json.loads((ROOT/'result.json').read_text())
cs=r['summary']['contrasts']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig=plt.figure(figsize=(12.5,8.2),layout='constrained')
gs=fig.add_gridspec(2,2,width_ratios=[1.2,1])
a=fig.add_subplot(gs[0,0]); b=fig.add_subplot(gs[1,0]); c=fig.add_subplot(gs[:,1])
colors={'structured':'#00798c','isotropic':'#ad5a18'}
for regime,offset in [('structured',-.9),('isotropic',.9)]:
    panel=[x for x in cs if x['regime']==regime and x['family']!='isotropic']
    angles=np.array([float(x['family']) for x in panel])
    means=np.array([x['mean_delta'] for x in panel])
    ci=np.array([x['exploratory_pointwise_95_interval'] for x in panel])
    a.errorbar(angles+offset,means,yerr=np.array([means-ci[:,0],ci[:,1]-means]),fmt='o-',
               capsize=3,color=colors[regime],label=regime.capitalize()+' history',lw=1.5,ms=4)
    b.plot(angles,[100*x['sign_accuracy'] for x in panel],'o-',color=colors[regime],
           label=regime.capitalize()+' history',ms=4,lw=1.5)
structured=[x for x in cs if x['regime']=='structured' and x['family']!='isotropic']
b.plot([float(x['family']) for x in structured],[100*x['always_benefit_accuracy'] for x in structured],
       '--',color='#8c8c8c',label='Always benefit (structured)')
b.plot([float(x['family']) for x in structured],[100*x['always_harm_accuracy'] for x in structured],
       ':',color='#4a4a4a',label='Always harm (structured)')
a.axhline(0,color='#444444',lw=.8); a.set_title('A  Benefit becomes relative harm',loc='left',fontweight='bold')
a.set_ylabel('Organized − rotated performance'); a.set_xlabel('Mismatch angle (degrees)')
a.set_xticks(range(0,91,15)); a.legend(fontsize=9,loc='lower left'); a.grid(axis='y',alpha=.18)
b.set_title('B  Fixed predictor sign agreement',loc='left',fontweight='bold')
b.set_ylabel('Agreement (%)'); b.set_xlabel('Mismatch angle (degrees)'); b.set_xticks(range(0,91,15)); b.set_ylim(-3,106)
b.legend(fontsize=8,loc='center left'); b.grid(axis='y',alpha=.18)
for record in r['summary']['reversal_brackets']:
    if record['regime']!='structured': continue
    h=record['history']
    for key,color,offset in [('predicted','#8b3ca0',-.14),('observed','#00798c',.14)]:
        for crossing in record[key]['crossings']:
            lo,hi=map(float,crossing['bracket'])
            c.plot([lo,hi],[h+offset,h+offset],color=color,lw=2.5,solid_capstyle='butt')
            c.scatter([(lo+hi)/2],[h+offset],color=color,s=8)
    if record['agreement']!='same_bracket': c.text(96,h,'miss',color='#a12e28',va='center',fontsize=8)
c.plot([],[],color='#8b3ca0',lw=3,label='Predicted interval');c.plot([],[],color='#00798c',lw=3,label='Observed interval')
c.set_title('C  Reversal intervals: 22/24 match',loc='left',fontweight='bold')
c.set_xlabel('Mismatch angle (degrees)');c.set_ylabel('Structured history (zero-based ID)')
c.set_xticks(range(0,91,15));c.set_yticks(range(24));c.set_xlim(0,110);c.set_ylim(23.7,-1.8);c.legend(loc='upper left',fontsize=9)
c.grid(axis='x',alpha=.18)
fig.suptitle('Exploratory mismatch/reversal experiment · 48 histories, fixed 25-generation endpoint',fontsize=14,fontweight='bold')
fig.supxlabel('A: pointwise 95% history-bootstrap intervals, not multiplicity adjusted. B–C: descriptive; nested outcomes are not independent replicates.',fontsize=9)
fig.savefig(ROOT/'mismatch_reversal.png',dpi=180)
fig.savefig(ROOT/'mismatch_reversal.svg')
