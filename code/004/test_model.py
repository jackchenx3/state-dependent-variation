import unittest,math,random,json,inspect
from pathlib import Path
import policy,model
from v3_model import transfer,covariance
class Correctness(unittest.TestCase):
    def setUp(self):self.cfg=json.loads(Path('config.json').read_text())
    def test_frozen_targets_survive_libm_roundoff(self):
        frozen=[dict(history=0,target=[.6,.8])]
        generated=[dict(history=0,target=[.6+1e-16,.8],angle=.2)]
        rows,info=model.bind_frozen_roster(generated,frozen);self.assertEqual(rows[0]['target'],frozen[0]['target']);self.assertEqual(rows[0]['angle'],.2)
        with self.assertRaises(ValueError):model.bind_frozen_roster([dict(history=1,target=[.6,.8],angle=.2)],frozen)
        with self.assertRaises(ValueError):model.bind_frozen_roster([dict(history=0,target=[.61,.8],angle=.2)],frozen)
    def test_zero_and_diagonal(self):
        a=[[2.,0.],[0.,.5]];r=[1.,2.];t=[0.,0.]
        self.assertEqual(policy.component(r,policy.ZERO,t,a,3.),(-12.,4.))
        cov=[[.2,0.],[0.,.3]];z,q=policy.component(r,cov,t,a,3.)
        d=[1+6*cov[i][i]*a[i][i] for i in (0,1)]
        self.assertAlmostEqual(z,-.5*sum(math.log(x) for x in d)-3*sum(r[i]**2*a[i][i]/d[i] for i in (0,1)))
        self.assertAlmostEqual(q,sum(a[i][i]*((r[i]/d[i])**2+cov[i][i]/d[i]) for i in (0,1)))
    def test_singular_covariance(self):
        z,q=policy.component([.2,.3],[[.1,0.],[0.,0.]],[0.,0.],[[1.,.2],[.2,2.]],10.);self.assertTrue(math.isfinite(z) and q>0)
    def test_noncommuting_quadrature(self):
        mean=[.3,-.2];target=[.8,.2];a=[[2.,.6],[.6,1.]];cov=[[.12,.035],[.035,.08]];beta=2.
        z,q=policy.component(mean,cov,target,a,beta);l00=math.sqrt(cov[0][0]);l10=cov[1][0]/l00;l11=math.sqrt(cov[1][1]-l10*l10);den=0.;num=0.;step=.1
        for i in range(-80,81):
            u=i*step
            for j in range(-80,81):
                v=j*step;x=[mean[0]+l00*u-target[0],mean[1]+l10*u+l11*v-target[1]];loss=policy.dot(x,policy.mv(a,x));w=math.exp(-.5*(u*u+v*v)-beta*loss)*step*step/(2*math.pi);den+=w;num+=w*loss
        self.assertAlmostEqual(math.exp(z),den,places=11);self.assertAlmostEqual(q,num/den,places=11)
    def test_identical_points_reduction(self):
        pop=[(.2,.3,0.)]*32;covs={'O':covariance(.2,.12,.02),'R':covariance(.2+math.pi/2,.12,.02)};d=policy.decisions(pop,[1.,0.],[[1.,.1],[.1,2.]],10.,covs,'O')
        for k in ('predicted_O_loss','predicted_R_loss'):
            self.assertAlmostEqual(d['M'][k],d['G'][k]);self.assertAlmostEqual(d['M'][k],d['E'][k])
    def test_stable_mixture(self):
        self.assertAlmostEqual(policy.mixture([(-10000.,1.),(-10001.,3.)]),(1+3/math.e)/(1+1/math.e));self.assertEqual(policy.mixture([(-100000.,2.),(-200000.,1.)]),2.)
    def test_rule_swapping(self):
        pop=[(.1,.2,0.),(.3,-.1,0.)];covs={'O':covariance(.2,.12,.02),'R':covariance(1.3,.12,.02)};args=(pop,[1.,0.],[[1.,.3],[.3,2.]],10.)
        a=policy.decisions(*args,covs,'O');b=policy.decisions(*args,{'O':covs['R'],'R':covs['O']},'R')
        for p in 'MGE':self.assertAlmostEqual(a[p]['predicted_O_minus_R_loss'],-b[p]['predicted_O_minus_R_loss']);self.assertNotEqual(a[p]['choice'],b[p]['choice'])
    def test_numerical_ties_retain(self):
        for early in 'OR':self.assertEqual(policy.choose(.2,.2+1e-13,early)['choice'],early);self.assertTrue(policy.choose(.2,.2,early)['tie'])
    def test_checkpoint_and_future_isolation(self):
        cfg=json.loads(json.dumps(self.cfg));cfg['transfer']['population']=4;row=dict(regime='structured',history=0,family='0',task=0,angle=.3,target=[1.,0.],target_seed=9,mutation_seed=10,survival_seed=11)
        cp=model.checkpoint(cfg,row);before=model.decide(cfg,cp);altered=dict(cp,regime='other',mutation_seed=999,survival_seed=888,mutation_random_state=None,survival_random_state=None)
        self.assertEqual(before,model.decide(cfg,altered));self.assertEqual(list(inspect.signature(policy.decisions).parameters),['pop','target','a','beta','covariances','early','tol'])
        traj=model.continue_branches(cfg,json.loads(json.dumps(cp)));ref=transfer(cfg['transfer'],.3,[1.,0.],10,11)
        self.assertEqual([[g['OO']['performance'],g['RR']['performance']] for g in traj],ref)
    def test_branch_composition(self):
        traj=[{k:{'performance':v} for k,v in zip(model.CELLS,[.1,.2,.3,.4])}]*25;decision={p:{'choice':'R'} for p in 'MGE'};y=model.compose(traj,decision,'O')
        self.assertEqual(y['E'],[.2]*25);self.assertEqual(y['CONTINUE'],[.1]*25);self.assertEqual(y['SWITCH'],[.2]*25);self.assertAlmostEqual(y['HALF'][0],.15)
    def test_budget_and_canonical_roster(self):
        b=model.budget();self.assertEqual(b['per_policy_new_offspring'],800);self.assertEqual(b['per_policy_selection_candidate_scores'],1600);self.assertEqual(b['per_checkpoint_policy_component_evaluations'],dict(M=4,G=4,E=128));self.assertEqual(b['evaluator_selection_candidate_scores_per_pair'],5760)
        hh=[dict(regime=r,history=0,angle=.1) for r in ['structured','isotropic']];rows=model.seed_roster(self.cfg,hh)
        for a,b in zip(rows[:64],rows[64:]):
            for k in ['target','mutation_seed','survival_seed','target_seed']:self.assertEqual(a[k],b[k])
        self.assertTrue(all(isinstance(r['family'],str) for r in rows))
if __name__=='__main__':unittest.main(verbosity=2)
