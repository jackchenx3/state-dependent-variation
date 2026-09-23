from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent;S=json.loads((P/'summary.json').read_text());colors={'M':'#466cba','G':'#bc6812','E':'#008478','CONTINUE':'#777777','SWITCH':'#98429d'}
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
def get(reg,fam='ALL',early='BOTH'):return next(r for r in S['groups'] if r['regime']==reg and r['family']==fam and r['early']==early)
def save(fig,name):
 for ext in ('png','svg'):fig.savefig(P/(name+'.'+ext),dpi=180,facecolor='white')
 plt.close(fig)
keys=['E_minus_M','E_minus_G','G_minus_M']+[p+'_minus_'+c for p in 'MGE' for c in ('CONTINUE','SWITCH','HALF')]
fig,axes=plt.subplots(1,2,figsize=(13,7),layout='constrained')
for ax,reg in zip(axes,('structured','isotropic')):
 g=get(reg);y=list(range(len(keys)));x=[g['values'][k]['mean'] for k in keys];lo=[a-g['values'][k]['ci95'][0] for a,k in zip(x,keys)];hi=[g['values'][k]['ci95'][1]-a for a,k in zip(x,keys)]
 ax.errorbar(x,y,xerr=[lo,hi],fmt='o',capsize=3,color='#007c91');ax.axvline(0,color='#777777');ax.axvline(.02,color='#b56814',ls='--',label='.02 usefulness target');ax.set_yticks(y);ax.set_yticklabels([k.replace('_minus_',' − ') for k in keys]);ax.invert_yaxis();ax.set_title(reg.capitalize());ax.set_xlabel('Generation-25 performance difference');ax.legend();ax.grid(axis='x',alpha=.15)
fig.suptitle('Fresh cohort: all prespecified aggregate policy contrasts',fontweight='bold');fig.supxlabel('Equal averages over eight families and both early arms within each history; paired pointwise 95% intervals, 24 histories/regime.',fontsize=9);save(fig,'aggregate_policy_contrasts')
families=['0','15','30','45','60','75','90','isotropic'];labels=['0','15','30','45','60','75','90','uniform']
fig,axes=plt.subplots(2,2,figsize=(13,8),layout='constrained')
for j,reg in enumerate(('structured','isotropic')):
 for i,early in enumerate('OR'):
  ax=axes[i,j]
  for key,color in [('E_minus_M','#007c91'),('E_minus_G','#bc6812'),('G_minus_M','#466cba')]:
   ss=[get(reg,f,early)['values'][key] for f in families];y=[v['mean'] for v in ss];ax.errorbar(range(8),y,yerr=[[a-v['ci95'][0] for a,v in zip(y,ss)],[v['ci95'][1]-a for a,v in zip(y,ss)]],marker='o',capsize=2,label=key.replace('_minus_',' − '),color=color,markersize=3)
  ax.axhline(0,color='#777777');ax.axhline(.02,color='#777777',ls='--');ax.set_xticks(range(8));ax.set_xticklabels(labels);ax.set_title(reg.capitalize()+' / early '+early);ax.set_ylabel('Generation-25 contrast');ax.set_xlabel('Target family');ax.legend();ax.grid(axis='y',alpha=.15)
fig.suptitle('Policy gains and harms by target family and early arm',fontweight='bold');fig.supxlabel('Pointwise history-bootstrap intervals; dashed line is the fixed .02 engineering target. Subgroups are dependent.',fontsize=9);save(fig,'family_policy_contrasts')
fig,axes=plt.subplots(2,2,figsize=(13,8),layout='constrained')
for j,reg in enumerate(('structured','isotropic')):
 for i,early in enumerate('OR'):
  ax=axes[i,j]
  for p,color in colors.items():ax.plot(range(8),[get(reg,f,early)['values'][p]['mean'] for f in families],'-o',label=p,color=color,markersize=3)
  ax.set_title(reg.capitalize()+' / early '+early);ax.set_xticks(range(8));ax.set_xticklabels(labels);ax.set_xlabel('Target family');ax.set_ylabel('Mean generation-25 performance');ax.legend(fontsize=8);ax.grid(axis='y',alpha=.15)
fig.suptitle('Both early states: policy levels and unconditional comparators',fontweight='bold');fig.supxlabel('Complete level intervals, absolute-rule outcomes, HALF and labeled hindsight references are in ENDPOINT_TABLES.md.',fontsize=9);save(fig,'family_policy_levels')
fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
for j,reg in enumerate(('structured','isotropic')):
 g=get(reg)
 for p,color in list(colors.items())[:3]:
  ss=[g['values'][p+'_sign_accuracy_g'+str(n)] for n in (6,25)];v=[x['mean'] for x in ss];axes[0,j].errorbar([6,25],v,yerr=[[a-b['ci95'][0] for a,b in zip(v,ss)],[b['ci95'][1]-a for a,b in zip(v,ss)]],color=color,marker='o',capsize=3,label=p)
  ss=[g['values'][p+'_decision_error_g'+str(n)] for n in (6,25)];v=[x['mean'] for x in ss];axes[1,j].errorbar([6,25],v,yerr=[[a-b['ci95'][0] for a,b in zip(v,ss)],[b['ci95'][1]-a for a,b in zip(v,ss)]],color=color,marker='o',capsize=3,label=p)
 axes[0,j].set_title(reg.capitalize());axes[0,j].set_ylabel('Predicted/observed loss-contrast sign agreement');axes[1,j].set_ylabel('Chosen-branch error frequency')
 for ax in axes[:,j]:ax.set_xticks([6,25]);ax.set_xlabel('Prespecified diagnostic generation');ax.set_ylim(0,1);ax.legend();ax.grid(axis='y',alpha=.15)
fig.suptitle('One-step and terminal decision diagnostics',fontweight='bold');fig.supxlabel('Frozen generation-5 predictions; errors compare the chosen branch with its realized alternative. No endpoint replacement.',fontsize=9);save(fig,'decision_diagnostics')
