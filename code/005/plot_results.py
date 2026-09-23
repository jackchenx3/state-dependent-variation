from pathlib import Path
import json,gzip
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent;S=json.loads((P/'summary.json').read_text());R=[json.loads(s) for s in gzip.open(P/'checkpoint_results.jsonl.gz','rt')];colors={'M':'#3b6ab3','G':'#bd6812','E':'#008577'}
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
def get(reg,f='ALL',e='BOTH'):return next(g for g in S['groups'] if g['regime']==reg and g['family']==f and g['early']==e)
def save(fig,name):
 for ext in ['png','svg']:fig.savefig(P/(name+'.'+ext),dpi=180,facecolor='white')
 plt.close(fig)
fig,axs=plt.subplots(1,2,figsize=(12,5),layout='constrained')
for ax,reg in zip(axs,['structured','isotropic']):
 g=get(reg)
 for i,p in enumerate('MGE'):
  ss=[g['values'][p+'_B'+str(h)] for h in [6,25]];y=[v['mean'] for v in ss];ax.errorbar([0+i*.08,1+i*.08],y,yerr=[[a-v['ci95'][0] for a,v in zip(y,ss)],[v['ci95'][1]-a for a,v in zip(y,ss)]],marker='o',capsize=3,label=p,color=colors[p])
 ax.axhline(0,color='gray',lw=1);ax.set_xticks([.08,1.08]);ax.set_xticklabels(['Generation 6','Generation 25']);ax.set_ylabel('Noise-corrected squared contrast error B');ax.set_title(reg.capitalize());ax.legend();ax.grid(axis='y',alpha=.15)
fig.suptitle('Local approximation and terminal discrepancy',fontweight='bold');fig.supxlabel('Pointwise whole-history 95% intervals. Lower B indicates better contrast calibration, not necessarily better ranking.',fontsize=9);save(fig,'squared_errors')
fig,axs=plt.subplots(1,2,figsize=(12,5),layout='constrained');keys=['E_B6','H','E_X','E_B25']
for ax,reg in zip(axs,['structured','isotropic']):
 ss=[get(reg)['values'][k] for k in keys];y=[v['mean'] for v in ss];ax.errorbar(range(4),y,yerr=[[a-v['ci95'][0] for a,v in zip(y,ss)],[v['ci95'][1]-a for a,v in zip(y,ss)]],fmt='o',capsize=4,color=colors['E']);ax.axhline(0,color='gray');ax.set_xticks(range(4));ax.set_xticklabels(['E: local B₆','Horizon H','Cross term X','E: terminal B₂₅']);ax.set_title(reg.capitalize());ax.set_ylabel('Noise-corrected error component');ax.grid(axis='y',alpha=.15)
fig.suptitle('The cross term can amplify or cancel discrepancies',fontweight='bold');fig.supxlabel('B₂₅ = B₆ + H + X. Mathematical components, not disjoint causal percentages. Pointwise history intervals.',fontsize=9);save(fig,'error_components')
fig,axs=plt.subplots(1,2,figsize=(11,5),layout='constrained');states=['negative','unresolved','positive']
for ax,reg in zip(axs,['structured','isotropic']):
 counts=get(reg)['counts'];matrix=[[counts['rank_'+a+'_to_'+b] for b in states] for a in states];im=ax.imshow(matrix,cmap='Blues',vmin=0,vmax=768)
 for i in range(3):
  for j in range(3):ax.text(j,i,str(matrix[i][j]),ha='center',va='center',fontsize=15,color='black')
 ax.set_xticks(range(3));ax.set_xticklabels(states);ax.set_yticks(range(3));ax.set_yticklabels(states);ax.set_xlabel('Generation-25 expected-contrast classification');ax.set_ylabel('Generation-6 classification');ax.set_title(reg.capitalize()+' (768 checkpoints)')
fig.suptitle('Both reversal directions and all unresolved categories',fontweight='bold');fig.supxlabel('97.5% marginal paired-replicate bootstrap intervals; nominal joint 95% per checkpoint, no simultaneous panel guarantee.',fontsize=8);save(fig,'ranking_categories')
fig,axs=plt.subplots(1,2,figsize=(11,5),layout='constrained')
for ax,reg in zip(axs,['structured','isotropic']):
 rows=[r for r in R if r['regime']==reg]
 for tag,color in [('resolved same','#357dab'),('resolved reversal','#b95930'),('unresolved at either','#aaaaaa')]:
  ss=[r for r in rows if ('resolved reversal' if r['values']['ranking_reversal'] else ('unresolved at either' if r['values']['ranking_unresolved_either'] else 'resolved same'))==tag];ax.scatter([r['values']['D6'] for r in ss],[r['values']['D25'] for r in ss],s=9,alpha=.55,label=tag,color=color)
 ax.axhline(0,color='gray',lw=1);ax.axvline(0,color='gray',lw=1);ax.set_title(reg.capitalize());ax.set_xlabel('Mean paired loss contrast D₆');ax.set_ylabel('Mean paired loss contrast D₂₅');ax.legend(fontsize=8)
fig.suptitle('Independent continuations: conditional rule value can change',fontweight='bold');fig.supxlabel('Each point is a frozen checkpoint; positive contrast favors R. All 1,536 checkpoints retained.',fontsize=9);save(fig,'horizon_contrasts')
