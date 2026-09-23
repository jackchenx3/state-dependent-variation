"""Scientific figures from completed outcomes; no simulation."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent;S=json.loads((P/'summary.json').read_text());colors={'OO':'#007c91','OR':'#de7100','RO':'#4865b4','RR':'#993fa5'}
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
def save(fig,name):
    for ext in ('png','svg'):fig.savefig(P/(name+'.'+ext),dpi=180,facecolor='white')
    plt.close(fig)
def panel(reg):return [s for s in S['families'] if s['regime']==reg and s['family']!='isotropic']
fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
for j,reg in enumerate(('structured','isotropic')):
    ss=panel(reg);x=[int(s['family']) for s in ss]
    for cell in colors:axes[0,j].plot(x,[s['values'][cell]['mean'] for s in ss],'-o',label=cell,color=colors[cell],markersize=4)
    for k,color in [('original','#555555'),('rule','#bc4b16'),('state','#326ac4')]:
        y=[s['values'][k]['mean'] for s in ss];lo=[v-s['values'][k]['ci95'][0] for v,s in zip(y,ss)];hi=[s['values'][k]['ci95'][1]-v for v,s in zip(y,ss)]
        axes[1,j].errorbar(x,y,yerr=[lo,hi],marker='o',capsize=3,label=k,color=color)
    axes[0,j].set_title(reg.capitalize()+' histories');axes[0,j].set_ylabel('Generation-25 mean performance');axes[1,j].set_ylabel('Paired normalized performance contrast');axes[1,j].axhline(0,color='#777777',lw=1)
    for ax in axes[:,j]:ax.set_xticks(x);ax.set_xlabel('Target angle from historical axis (degrees)');ax.legend();ax.grid(axis='y',alpha=.15)
fig.suptitle('Generation-5 state × later variation rule\nFour cell means and symmetric paired summaries',fontweight='bold')
fig.supxlabel('First letter: early population (O/R); second: rule in generations 6–25. Intervals: pointwise 95% history bootstrap.',fontsize=9)
save(fig,'factorial_outcomes')
fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
for j,reg in enumerate(('structured','isotropic')):
    ss=panel(reg);x=[int(s['family']) for s in ss]
    for i,names in enumerate((('rule_given_O','rule_given_R'),('state_given_O','state_given_R'))):
        for k,color in zip(names,('#007c91','#bb4b12')):
            y=[s['values'][k]['mean'] for s in ss];lo=[v-s['values'][k]['ci95'][0] for v,s in zip(y,ss)];hi=[s['values'][k]['ci95'][1]-v for v,s in zip(y,ss)]
            axes[i,j].errorbar(x,y,yerr=[lo,hi],marker='o',capsize=3,label=k.replace('_',' '),color=color)
        axes[i,j].axhline(0,color='#777777',lw=1);axes[i,j].legend();axes[i,j].set_xticks(x);axes[i,j].set_xlabel('Target angle (degrees)');axes[i,j].grid(axis='y',alpha=.15)
    axes[0,j].set_title(reg.capitalize()+' histories');axes[0,j].set_ylabel('Conditional later-rule effect (O − R)');axes[1,j].set_ylabel('Conditional early-state effect (O − R)')
fig.suptitle('Conditional effects retain state–rule dependence',fontweight='bold');fig.supxlabel('Exploratory pointwise 95% paired history-bootstrap intervals; unresolved is not equivalence.',fontsize=9);save(fig,'conditional_effects')
for reg in ('structured','isotropic'):
    fig,axes=plt.subplots(2,4,figsize=(14,7),layout='constrained')
    ss=[s for s in S['families'] if s['regime']==reg]
    for ax,s in zip(axes.flat,ss):
        for cell in colors:ax.plot(range(1,26),[r[cell]['performance'] for r in s['mean_trajectories']],color=colors[cell],label=cell)
        ax.axvline(5,color='#777777',ls=':',lw=1);ax.set_title('Uniform directions' if s['family']=='isotropic' else s['family']+'°');ax.set_xlabel('Generation');ax.set_ylabel('Mean performance');ax.grid(axis='y',alpha=.15)
    axes[0,0].legend();fig.suptitle(reg.capitalize()+' histories: every target family and all four trajectories',fontweight='bold');fig.supxlabel('Switch after generation 5; same early-state branches coincide through generation 5. No horizon-wise inference.',fontsize=9);save(fig,'trajectories_'+reg)
ex=S['illustrative_case'];fig,axes=plt.subplots(1,3,figsize=(14,4.8),layout='constrained')
for ax,m,label in zip(axes,('performance','centroid_loss','dispersion_loss'),('Mean performance','Centroid loss','Within-population dispersion loss')):
    for cell in colors:ax.plot(range(1,26),[r[cell][m] for r in ex['trajectories']],color=colors[cell],label=cell)
    ax.axvline(5,color='#777777',ls=':');ax.set_xlabel('Generation');ax.set_ylabel(label);ax.legend();ax.grid(axis='y',alpha=.15)
fig.suptitle('Original illustrative case: structured history 0, target 75°',fontweight='bold');fig.supxlabel('Eight paired trials. Centroid + dispersion = mean loss: accounting, not causal mediation. Selected illustration, not representative.',fontsize=9);save(fig,'illustrative_components')
