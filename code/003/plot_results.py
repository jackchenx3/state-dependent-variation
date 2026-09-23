"""Figures for all fixed state-feature comparisons; no simulation."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parent;data=json.loads((P/'summary.json').read_text());regs=('structured','isotropic')
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
colors=['#007c91','#c15b12','#466cba','#9a429f']
def groups(reg):return [r for r in data['families'] if r['regime']==reg and r['family']!='isotropic']
def save(fig,name):
    for ext in ('png','svg'):fig.savefig(P/(name+'.'+ext),dpi=180,facecolor='white')
    plt.close(fig)
def effects(ax,rows,keys,labels=None):
    x=[int(r['family']) for r in rows]
    for k,color,label in zip(keys,colors,labels or keys):
        y=[r['values'][k]['mean'] for r in rows];lo=[a-r['values'][k]['ci95'][0] for a,r in zip(y,rows)];hi=[r['values'][k]['ci95'][1]-a for a,r in zip(y,rows)]
        ax.errorbar(x,y,yerr=[lo,hi],capsize=3,marker='o',markersize=4,label=label,color=color)
    ax.axhline(0,color='#777777',lw=1);ax.set_xticks(x);ax.set_xlabel('Target angle (degrees)');ax.grid(axis='y',alpha=.15);ax.legend(fontsize=9)
fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
for j,reg in enumerate(regs):
    rows=groups(reg);x=[int(r['family']) for r in rows]
    for i,s in enumerate('OR'):
        keys=[m+s+r for m in 'OR' for r in 'OR']
        for k,c in zip(keys,colors):axes[i,j].plot(x,[r['values'][k]['mean'] for r in rows],'-o',color=c,label=k,markersize=4)
        axes[i,j].set_title(reg.capitalize()+'; configuration '+s);axes[i,j].set_ylabel('Generation-25 mean performance');axes[i,j].set_xticks(x);axes[i,j].set_xlabel('Target angle (degrees)');axes[i,j].legend();axes[i,j].grid(axis='y',alpha=.15)
fig.suptitle('Eight cell outcomes: centroid × centered configuration × later rule',fontweight='bold');fig.supxlabel('Letters identify donors/rule in that order. All cell intervals and uniform-direction references are in ENDPOINT_TABLES.md.',fontsize=9);save(fig,'eight_cell_outcomes')
fig,axes=plt.subplots(1,2,figsize=(12,4.8),layout='constrained')
for ax,reg in zip(axes,regs):effects(ax,groups(reg),['F_OO','F_OR','F_RO','F_RR'],['O centroid / O configuration','O centroid / R configuration','R centroid / O configuration','R centroid / R configuration']);ax.set_title(reg.capitalize());ax.set_ylabel('Later-rule effect (O − R)')
fig.suptitle('Conditional rule effects for every crossed state',fontweight='bold');fig.supxlabel('Paired pointwise 95% history-bootstrap intervals; 24 histories per group, dependent angles.',fontsize=9);save(fig,'conditional_rule_effects')
fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
for j,reg in enumerate(regs):
    effects(axes[0,j],groups(reg),['IM_O','IM_R'],['O configuration','R configuration']);effects(axes[1,j],groups(reg),['IS_O','IS_R'],['O centroid','R centroid'])
    axes[0,j].set_title(reg.capitalize());axes[0,j].set_ylabel('Centroid × rule interaction');axes[1,j].set_ylabel('Configuration × rule interaction')
for ax in axes.flat:ax.set_ylim(-.28,.015)
fig.suptitle('Which state feature changes rule value?',fontweight='bold');fig.supxlabel('Same outcome scale; pointwise exploratory intervals. Centered configuration includes more than covariance.',fontsize=9);save(fig,'conditional_interactions')
fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
for j,reg in enumerate(regs):
    effects(axes[0,j],groups(reg),['J_M','J_S','I_joint'],['J_M: centroid average','J_S: configuration average','Original joint interaction']);effects(axes[1,j],groups(reg),['J_M_minus_J_S','three_factor'],['J_M − J_S','Three-factor interaction'])
    axes[0,j].set_title(reg.capitalize());axes[0,j].set_ylabel('Symmetric interaction summary');axes[1,j].set_ylabel('Prespecified comparison / interaction')
fig.suptitle('Symmetric comparisons retain the joint and three-factor effects',fontweight='bold');fig.supxlabel('J_M + J_S = joint interaction by definition; no unique causal attribution or mediation percentage.',fontsize=9);save(fig,'symmetric_interactions')
# Original, prespecified illustrative case; no selection from new outcomes.
rr=data['illustrative_case']['trial_rows'];fig,axes=plt.subplots(2,2,figsize=(12,8),layout='constrained')
for j,s in enumerate('OR'):
    keys=[m+s+r for m in 'OR' for r in 'OR']
    for i,metric in enumerate(('performance','centroid_loss')):
        for k,c in zip(keys,colors):axes[i,j].plot(range(5,26),[sum(row['trajectory'][g][k][metric] for row in rr)/8 for g in range(21)],label=k,color=c)
        axes[i,j].set_title('Configuration '+s);axes[i,j].set_xlabel('Generation');axes[i,j].set_ylabel('Mean performance' if i==0 else 'Centroid loss');axes[i,j].legend();axes[i,j].grid(axis='y',alpha=.15)
fig.suptitle('Original illustrative case: structured history 0 / target 75°',fontweight='bold');fig.supxlabel('Constructed populations start at generation 5. Eight paired trials; selected illustration, not representative.',fontsize=9);save(fig,'illustrative_trajectories')
