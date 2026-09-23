"""Read stored v1/v2 outputs only; no simulation or fitting."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parent
v1=json.loads((ROOT/'baseline_result.json').read_text())
v2=json.loads((ROOT/'result.json').read_text())
versions=[('v1',v1,'#00798c','-'),('v2',v2,'#c05a1b','--')]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(2,2,figsize=(12,8.2),layout='constrained')
for col,reg in enumerate(('structured','isotropic')):
    ax=axes[0,col]; arms=axes[1,col]
    for name,data,color,style in versions:
        panel=[c for c in data['summary']['contrasts'] if c['regime']==reg and c['family']!='isotropic']
        x=np.array([float(c['family']) for c in panel]); y=np.array([c['mean_delta'] for c in panel])
        ci=np.array([c['exploratory_pointwise_95_interval'] for c in panel])
        ax.errorbar(x+(-.8 if name=='v1' else .8),y,yerr=[y-ci[:,0],ci[:,1]-y],fmt='o',linestyle=style,
                    color=color,capsize=3,ms=4,label=name+(' elitist' if name=='v1' else ' probabilistic'))
        for field,armcolor in [('organized','#00798c'),('rotated','#8a3ca0')]:
            arms.plot(x,[c['mean_'+field] for c in panel],linestyle=style,marker='o',ms=4,
                      color=armcolor,label=name+' '+field)
    ax.axhline(0,color='#555555',lw=.8)
    ax.set_title(('A' if col==0 else 'B')+'  '+reg.capitalize()+' historical inputs',loc='left',fontweight='bold')
    ax.set_ylabel('Organized − rotated improvement');ax.legend(fontsize=9)
    arms.set_title(('C' if col==0 else 'D')+'  Both arms at generation 25',loc='left',fontweight='bold')
    arms.set_ylabel('Mean normalized improvement');arms.legend(fontsize=9,loc='best',ncol=2)
    for a in (ax,arms):
        a.set_xticks(range(0,91,15));a.set_xlabel('Mismatch angle (degrees)');a.grid(axis='y',alpha=.2)
fig.suptitle('Transfer-selection comparison · same 48 inherited histories and exact target panel',fontweight='bold',fontsize=14)
fig.supxlabel('V2: sequential survival without replacement, weights exp(−10 × squared distance). Error bars: exploratory pointwise 95% history-bootstrap intervals.',fontsize=9)
fig.savefig(ROOT/'v1_v2_performance.png',dpi=180);fig.savefig(ROOT/'v1_v2_performance.svg')
plt.close(fig)
fig=plt.figure(figsize=(12,8.2),layout='constrained');gs=fig.add_gridspec(2,2,width_ratios=[1.1,1])
a=fig.add_subplot(gs[0,0]);b=fig.add_subplot(gs[1,0]);c=fig.add_subplot(gs[:,1])
for axis,reg in [(a,'structured'),(b,'isotropic')]:
    for name,data,color,style in versions:
        panel=[x for x in data['summary']['contrasts'] if x['regime']==reg and x['family']!='isotropic']
        axis.plot([float(x['family']) for x in panel],[100*x['sign_accuracy'] for x in panel],
                  linestyle=style,marker='o',color=color,label=name,ms=4)
    panel=[x for x in v2['summary']['contrasts'] if x['regime']==reg and x['family']!='isotropic']
    axis.plot([float(x['family']) for x in panel],[100*x['always_benefit_accuracy'] for x in panel],'--',color='#888888',label='Always benefit (v2)')
    axis.plot([float(x['family']) for x in panel],[100*x['always_harm_accuracy'] for x in panel],':',color='#444444',label='Always harm (v2)')
    axis.set_title(reg.capitalize()+' historical inputs',loc='left',fontweight='bold')
    axis.set_xticks(range(0,91,15));axis.set_xlabel('Mismatch angle (degrees)');axis.set_ylabel('Predictor sign agreement (%)')
    axis.set_ylim(-3,105);axis.grid(axis='y',alpha=.2);axis.legend(fontsize=8,loc='best')
for history in range(24):
    for name,data,color,offset in [('predicted',v1,'#8a3ca0',-.23),('v1',v1,'#00798c',0),('v2',v2,'#c05a1b',.23)]:
        record=next(x for x in data['summary']['reversal_brackets'] if x['regime']=='structured' and x['history']==history)
        bracket=record['predicted'] if name=='predicted' else record['observed']
        for cross in bracket['crossings']:
            lo,hi=map(float,cross['bracket']);c.plot([lo,hi],[history+offset]*2,color=color,lw=2.2)
        if not bracket['crossings']:c.scatter([98],[history+offset],marker='x',s=12,color=color)
for name,color in [('Predicted','#8a3ca0'),('Observed v1','#00798c'),('Observed v2','#c05a1b')]:c.plot([],[],color=color,lw=2.5,label=name)
c.set_title('Structured-history reversal intervals',loc='left',fontweight='bold');c.set_yticks(range(24));c.set_ylim(23.7,-2.8)
c.set_xticks(range(0,91,15));c.set_xlim(0,105);c.set_ylabel('Stored history ID');c.set_xlabel('Mismatch angle (degrees)');c.grid(axis='x',alpha=.2);c.legend(loc='upper left',fontsize=8)
fig.suptitle('Fixed predictor under two transfer-selection rules',fontsize=14,fontweight='bold')
fig.supxlabel('Descriptive validation; angles within a history are dependent. Intervals are grid brackets, not confidence intervals; × at right = no positive-to-negative bracket.',fontsize=9)
fig.savefig(ROOT/'v1_v2_prediction.png',dpi=180);fig.savefig(ROOT/'v1_v2_prediction.svg')
