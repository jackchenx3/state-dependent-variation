"""Rebuild publication figures solely from included saved statistical grids."""
from pathlib import Path
import argparse,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
C=['#176b8c','#cc6c39','#378566','#8964a4']
plt.rcParams.update({'font.size':10,'axes.titlesize':12,'axes.labelsize':10,
 'figure.facecolor':'white','axes.spines.top':False,'axes.spines.right':False,
 'savefig.dpi':210,'svg.fonttype':'none','pdf.fonttype':42})
SOURCES=[]
def read(rel):return json.loads((ROOT/rel).read_text())
def record(path,route,value):
 SOURCES.append({'path':path,'route':route,'value':value});return value
def point(study,regime,key,family='ALL',early='BOTH'):
 path=f'results/{study}/summary.json';s=read(path)
 kind='families' if study in ['002','003'] else 'groups'
 for i,g in enumerate(s[kind]):
  if g['regime']==regime and g['family']==family and g.get('early','BOTH')==early:
   return record(path,[kind,i,'values',key],g['values'][key])
 raise KeyError((study,regime,family,early,key))
def bp(study,key):
 path=f'results/{study}/summary.json';return record(path,['values',key],read(path)['values'][key])
def err(ax,x,p,color,label=None,offset=0,scale=1):
 y=np.array([q['mean'] for q in p])*scale;ci=np.array([q['ci95'] for q in p])*scale
 ax.errorbar(np.array(x)+offset,y,yerr=np.stack([y-ci[:,0],ci[:,1]-y]),
  fmt='o-',lw=1.5,ms=4,capsize=2.3,color=color,label=label)
def save(fig,name,out):
 fig.savefig(out/(name+'.png'),bbox_inches='tight')
 fig.savefig(out/(name+'.svg'),bbox_inches='tight')
 fig.savefig(out/(name+'.pdf'),bbox_inches='tight')
 plt.close(fig)
def style(ax,xlabel,ylabel):
 ax.axhline(0,color='#78838a',lw=.8,zorder=0);ax.set_xlabel(xlabel);ax.set_ylabel(ylabel)
 ax.grid(axis='y',alpha=.16)
def forest(rows,title,out,name):
 fig,axs=plt.subplots(1,2,figsize=(10.8,max(3.5,len(rows)*.56+1.1)),sharey=True,layout='constrained')
 for ai,(ax,metric,heading) in enumerate(zip(axs,['U','U40'],['Mean accuracy, updates 1–40','Terminal accuracy, update 40'])):
  for y,(label,study,key) in enumerate(rows):
   p=bp(study,key+'|'+metric);m=p['mean']*100;l,h=np.array(p['ci95'])*100
   ax.errorbar(m,y,xerr=[[m-l],[h-m]],fmt='o',ms=5,capsize=3,color=C[ai])
  ax.axvline(0,color='#78838a',lw=.8);ax.grid(axis='x',alpha=.16)
  ax.set_title(heading);ax.set_xlabel('Accuracy difference (percentage points)')
 axs[0].set_yticks(range(len(rows)),[r[0] for r in rows]);axs[0].invert_yaxis()
 fig.suptitle(title,fontweight='bold');save(fig,name,out)
def paper_a(out):
 regimes=['structured','isotropic'];angles=list(range(0,91,15));ticks=angles+[112];labs=[str(a)+'°' for a in angles]+['Uniform']
 fig,axs=plt.subplots(1,2,figsize=(9.5,3.65),sharey=True,layout='constrained')
 path='results/V3/HORIZON_DIAGNOSTIC.json';rows=read(path)['timecourse']
 for ax,r in zip(axs,regimes):
  for k,c,label in [('predictor',C[0],'Directional variance'),('geometry_predictor',C[1],'Exact local weight')]:
   vals=[record(path,['timecourse',i,r,k],g[r][k]) for i,g in enumerate(rows)]
   ax.plot([g['generation'] for g in rows],vals,color=c,lw=2,label=label)
  ax.set_title(r.title()+' histories');ax.set_xlabel('Generation');ax.set_xlim(1,25);ax.set_ylim(120,169);ax.grid(alpha=.15)
 axs[0].set_ylabel('Matched signs / 168');axs[0].legend(fontsize=8,loc='lower right')
 fig.suptitle('Starting-state predictions change rank across the horizon',fontweight='bold')
 save(fig,'horizon_diagnostic',out)
 fig,axs=plt.subplots(2,2,figsize=(10,6.5),sharex=True,layout='constrained')
 for col,r in enumerate(regimes):
  for row,keys in enumerate([['rule_given_O','rule_given_R'],['state_given_O','state_given_R']]):
   ax=axs[row,col]
   for j,key in enumerate(keys):
    label=('Earlier '+key[-1]+' state') if row==0 else ('Later '+key[-1]+' rule')
    err(ax,ticks,[point('002',r,key,str(x) if x!=112 else 'isotropic') for x in ticks],C[j],label,offset=(j-.5)*1.5)
   style(ax,'Target direction','Later-rule effect: O − R' if row==0 else 'Earlier-state effect: O − R')
   ax.set_xticks(ticks,labs,fontsize=8);ax.legend(fontsize=8)
   if row==0:ax.set_title(r.title()+' histories')
 fig.suptitle('Conditional rule and state effects at generation 25',fontweight='bold')
 save(fig,'state_rule_effects',out)
 fig,axs=plt.subplots(1,2,figsize=(10,4.2),sharey=True,layout='constrained')
 for ax,r in zip(axs,regimes):
  for j,key in enumerate(['IM_O','IM_R','IS_O','IS_R']):
   label={'IM_O':'Centroid × rule | config. O','IM_R':'Centroid × rule | config. R','IS_O':'Config. × rule | centroid O','IS_R':'Config. × rule | centroid R'}[key]
   err(ax,ticks,[point('003',r,key,str(x) if x!=112 else 'isotropic') for x in ticks],C[j],label,offset=(j-1.5)*1.1)
  style(ax,'Target direction','Difference of rule effects');ax.set_title(r.title()+' histories');ax.set_xticks(ticks,labs,fontsize=8)
 fig.legend(*axs[0].get_legend_handles_labels(),fontsize=8,loc='outside lower center',ncol=2)
 fig.suptitle('Both state features modify the subsequent rule effect',fontweight='bold')
 save(fig,'state_feature_interactions',out)
 keys=['E_minus_M','E_minus_G','G_minus_M']+[f'{p}_minus_{b}' for p in ['M','G','E'] for b in ['CONTINUE','SWITCH','HALF']]
 fig,axs=plt.subplots(1,2,figsize=(9.8,6.5),sharey=True,layout='constrained')
 for ax,r in zip(axs,regimes):
  for y,k in enumerate(keys):
   p=point('004',r,k);m=p['mean'];l,h=p['ci95']
   ax.errorbar(m,y,xerr=[[m-l],[h-m]],fmt='o',color=C[0],ms=4,capsize=2)
  ax.axvline(0,color='#78838a',lw=.8);ax.axvline(.02,color=C[1],ls='--',lw=1,label='E − M usefulness target: .02')
  ax.set_xlabel('Generation-25 performance difference');ax.set_title(r.title()+' histories');ax.grid(axis='x',alpha=.16)
 axs[0].set_yticks(range(len(keys)),[k.replace('_minus_',' − ') for k in keys]);axs[0].invert_yaxis();axs[1].legend(fontsize=7,loc='lower right')
 fig.suptitle('Prospective policy contrasts on fresh histories',fontweight='bold');save(fig,'policy_contrasts',out)
 fig,axs=plt.subplots(1,2,figsize=(9.5,4),sharey=True,layout='constrained')
 for ax,r in zip(axs,regimes):
  for j,p in enumerate(['M','G','E']):err(ax,[0,1],[point('005',r,p+'_B'+str(g)) for g in [6,25]],C[j],p,offset=(j-1)*.06)
  ax.set_title(r.title()+' histories');ax.set_xticks([0,1],['Generation 6','Generation 25']);ax.set_xlim(-.2,1.2);ax.set_ylabel('Corrected squared contrast discrepancy');ax.grid(axis='y',alpha=.16)
 axs[0].legend(title='State summary',fontsize=8)
 fig.suptitle('Better local calibration need not improve terminal calibration',fontweight='bold');save(fig,'squared_errors',out)
 fig,axs=plt.subplots(1,2,figsize=(9.3,4.3),layout='constrained');classes=['negative','unresolved','positive'];nice=['O favored','Unresolved','R favored']
 for ax,r in zip(axs,regimes):
  path='results/005/summary.json';s=read(path);idx=next(i for i,g in enumerate(s['groups']) if g['regime']==r and g['family']=='ALL' and g['early']=='BOTH')
  mat=np.array([[record(path,['groups',idx,'counts',f'rank_{a}_to_{b}'],s['groups'][idx]['counts'][f'rank_{a}_to_{b}']) for b in classes] for a in classes])
  assert mat.sum()==768
  ax.imshow(mat,cmap='Blues',vmin=0,vmax=500)
  for y in range(3):
   for x in range(3):ax.text(x,y,str(mat[y,x]),ha='center',va='center',fontsize=16,color='white' if mat[y,x]>280 else '#17354b')
  ax.set_xticks(range(3),nice,fontsize=9);ax.set_yticks(range(3),nice,fontsize=9);ax.set_xlabel('Generation-25 classification');ax.set_ylabel('Generation-6 classification');ax.set_title(r.title()+' histories (768 checkpoints)')
 fig.suptitle('All conditional ranking outcomes, including uncertainty',fontweight='bold');save(fig,'ranking_categories',out)
 fig,axs=plt.subplots(1,2,figsize=(10,4),sharey=True,layout='constrained')
 for ax,r in zip(axs,regimes):
  for j,v in enumerate(['V1','V2','V3']):
   path=f'results/{v}/summary.json';s=read(path);pts=[]
   for a in angles:
    idx=next(i for i,g in enumerate(s['contrasts']) if g['regime']==r and g['family']==str(a));q=record(path,['contrasts',idx],s['contrasts'][idx]);pts.append({'mean':q['mean_delta'],'ci95':q.get('pointwise_95_interval',q.get('exploratory_pointwise_95_interval'))})
   err(ax,angles,pts,C[j],v,offset=(j-1)*1.5)
  style(ax,'Target direction','Terminal performance: O − R');ax.set_title(r.title()+' histories');ax.set_xticks(angles)
 axs[0].legend(fontsize=8);fig.suptitle('Transfer comparisons (objectives differ across settings)',fontweight='bold');save(fig,'transfer_overview',out)
def paper_b(out):
 forest([('Persistent: memory − current','032','BINARY|MEMORY-CURRENT4'),('Persistent: fallback − memory','033','BINARY|BEST_AVAILABLE-MEMORY'),('Persistent: fallback − current children','034','BINARY|BEST_AVAILABLE-CURRENT_CHILDREN'),('Independent: fallback − current children','035','IID|BEST_AVAILABLE-CURRENT_CHILDREN'),('Independent: fallback − scouts','036','IID|BEST_AVAILABLE-RANDOM_RESTART'),('Persistent: fallback − scouts','036','BINARY|BEST_AVAILABLE-RANDOM_RESTART')], 'Memory value depends on the comparator',out,'01_comparators')
 forest([(f'Cohort {c}: {label}',s,reg+'|BEST_AVAILABLE-RANDOM_RESTART') for c,s in [(1,'037'),(2,'038')] for label,reg in [('independent','IID'),('recurrent','RECUR'),('recurrence interaction','RECUR_MINUS_IID')]],'History minus scouts: partial replication of the ranking switch',out,'02_replication')
 fig,ax=plt.subplots(figsize=(9,4),layout='constrained')
 for j,(reg,lab) in enumerate([('IID','Independent targets'),('RECUR','Recurrent targets')]):err(ax,range(1,9),[bp('038',reg+'|BEST_AVAILABLE-RANDOM_RESTART|E'+str(w)) for w in range(1,9)],C[j],lab,offset=(j-.5)*.04,scale=100)
 style(ax,'Update window','Mean accuracy difference (percentage points)');ax.set_xticks(range(1,9),[f'{5*i+1}–{5*i+5}' for i in range(8)]);ax.legend(fontsize=9);ax.set_title('Cohort 2: early recurrent losses precede later benefits',fontweight='bold');save(fig,'03_windows',out)
 forest([('Independent: hybrid − scouts','039','IID|HYBRID-RANDOM_RESTART'),('Recurrent: hybrid − history','039','RECUR|HYBRID-BEST_AVAILABLE'),('Equal-weight benchmark','039','BALANCED|HYBRID-REFERENCE')],'A fixed hybrid improves the named cumulative benchmark',out,'04_hybrid')
 forest([('Independent: retained − current','040','IID|HYBRID-CURRENT_SCOUT'),('Recurrent: retained − current','040','RECUR|HYBRID-CURRENT_SCOUT'),('Recurrence interaction','040','RECUR_MINUS_IID|HYBRID-CURRENT_SCOUT')],'Retention contributes with scouting and allocation held fixed',out,'05_retention')
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output-dir',type=Path,default=ROOT/'_rebuilt/figures');args=parser.parse_args();args.output_dir.mkdir(parents=True,exist_ok=True)
 (paper_a if (ROOT/'results/V1').exists() else paper_b)(args.output_dir)
 (args.output_dir/'FIGURE_SOURCES.json').write_text(json.dumps({'sources':SOURCES,'intervals':'Approximate pointwise intervals; dependence and endpoint scope are stated in the manuscript.'},indent=2)+'\n')
 print(json.dumps({'figures':len(list(args.output_dir.glob('*.png'))),'source_records':len(SOURCES),'output':str(args.output_dir)}))
if __name__=='__main__':main()
