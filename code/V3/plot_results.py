"""Plots of stored outcomes and both fixed predictors; no model execution."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
P=Path(__file__).resolve().parent
r=json.loads((P/'result.json').read_text());s=r['summary']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained',sharey='row')
for col,reg in enumerate(('structured','isotropic')):
    panel=[c for c in s['contrasts'] if c['regime']==reg and c['family']!='isotropic']
    x=np.array([float(c['family']) for c in panel]);y=np.array([c['mean_delta'] for c in panel]);ci=np.array([c['pointwise_95_interval'] for c in panel])
    a=axes[0,col];b=axes[1,col]
    a.errorbar(x,y,yerr=[y-ci[:,0],ci[:,1]-y],fmt='o-',color='#00798c',capsize=3)
    a.axhline(0,color='#555555',lw=.8);a.set_ylabel('Organized − rotated improvement')
    a.set_title(reg.capitalize()+' historical inputs',loc='left',fontweight='bold')
    for arm,color in [('organized','#00798c'),('rotated','#8a3ca0')]:
        b.plot(x,[c[arm]['mean'] for c in panel],'o-',color=color,label=arm.capitalize())
    b.set_title('Both arms at generation 25',loc='left',fontweight='bold');b.set_ylabel('Mean improvement in anisotropic loss');b.legend()
    for axis in (a,b):axis.set_xticks(range(0,91,15));axis.set_xlabel('Target angle from historical axis (degrees)');axis.grid(axis='y',alpha=.2)
fig.suptitle('V3 population outcomes · unequal fitness costs, same 48 inherited inputs',fontweight='bold',fontsize=14)
fig.supxlabel('H = R(30°) diag(4,1) R(30°)ᵀ; normalized start loss = 1. Error bars: exploratory pointwise 95% history-bootstrap intervals.',fontsize=9)
fig.savefig(P/'v3_population.png',dpi=180);fig.savefig(P/'v3_population.svg');plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(12,4.8),layout='constrained',sharey=True)
for ax,reg in zip(axes,('structured','isotropic')):
    panel=[c for c in s['contrasts'] if c['regime']==reg and c['family']!='isotropic'];x=[float(c['family']) for c in panel]
    for pred,color,name,style in [('predictor','#8a3ca0','Original directional variance','--'),('geometry_predictor','#c05a1b','Geometry-aware log expected weight','-')]:
        ax.plot(x,[100*c['sign_accuracy'][pred] for c in panel],marker='o',linestyle=style,color=color,label=name)
    ax.plot(x,[100*c['always_benefit_accuracy'] for c in panel],':',color='#777777',label='Always benefit')
    ax.plot(x,[100*c['always_harm_accuracy'] for c in panel],'-.' ,color='#aaaaaa',label='Always harm')
    ax.set_title(reg.capitalize()+' historical inputs',loc='left',fontweight='bold');ax.set_xticks(range(0,91,15));ax.set_ylim(-3,105)
    ax.set_xlabel('Target angle from historical axis (degrees)');ax.grid(axis='y',alpha=.2);ax.legend(fontsize=8,loc='best')
axes[0].set_ylabel('History-level sign agreement (%)')
fig.suptitle('Two predictors fixed before v3 outcomes',fontweight='bold',fontsize=14)
fig.supxlabel('Seven angles per history are dependent. Geometry-aware predictor is local, not a theorem about the population endpoint.',fontsize=9)
fig.savefig(P/'v3_predictors.png',dpi=180);fig.savefig(P/'v3_predictors.svg');plt.close(fig)
fig,axes=plt.subplots(1,2,figsize=(12,10),layout='constrained',sharey=True)
for ax,reg in zip(axes,('structured','isotropic')):
    for row in s['all_crossings']:
        if row['regime']!=reg:continue
        h=row['history']
        for label,record,color,offset in [('Original',row['predicted']['predictor'],'#8a3ca0',-.23),('Geometry-aware',row['predicted']['geometry_predictor'],'#c05a1b',0),('Observed',row['observed'],'#00798c',.23)]:
            if not record['crossings']:ax.scatter([99],[h+offset],marker='x',color=color,s=14)
            for c in record['crossings']:
                lo,hi=map(float,c['bracket']);pos=c['direction']=='positive_to_negative'
                ax.plot([lo,hi],[h+offset]*2,color=color,lw=2,linestyle='-' if pos else '--')
                ax.scatter([(lo+hi)/2],[h+offset],marker='v' if pos else '^',color=color,s=18)
    for name,color in [('Original','#8a3ca0'),('Geometry-aware','#c05a1b'),('Observed','#00798c')]:ax.plot([],[],color=color,lw=2,label=name)
    ax.set_title(reg.capitalize()+' historical inputs',loc='left',fontweight='bold');ax.set_xticks(range(0,91,15));ax.set_yticks(range(24));ax.set_ylim(23.7,-2.3);ax.set_xlim(0,106)
    ax.set_xlabel('Target-angle bracket (degrees)');ax.grid(axis='x',alpha=.2);ax.legend(fontsize=8,loc='upper left')
axes[0].set_ylabel('Stored history ID')
fig.suptitle('All v3 crossings · no unique reversal assumed',fontweight='bold',fontsize=14)
fig.supxlabel('▼ solid: positive→negative; ▲ dashed: negative→positive; × at right: no crossing detected. Brackets are not confidence intervals.',fontsize=9)
fig.savefig(P/'v3_all_crossings.png',dpi=180);fig.savefig(P/'v3_all_crossings.svg')
