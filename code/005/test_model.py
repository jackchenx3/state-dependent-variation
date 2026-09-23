import unittest,copy,math,itertools,json,random
from pathlib import Path
from unittest.mock import patch
import model
from analysis import corrected,cov,mean,classify,checkpoint_summary
from baseline_model import seed_for
from switch_model import advance,draws
class Correctness(unittest.TestCase):
 def fixture(self):
  c=json.loads(Path('config.json').read_text());cp=dict(regime='structured',history=0,family='0',task=0,angle=.4,target=[1.,0.],populations={e:[(.01*i,.002*i,.4) for i in range(32)] for e in 'OR'});cp['decisions']={e:{p:dict(predicted_O_minus_R_loss=.03,choice='R',tie=False) for p in 'MGE'} for e in 'OR'};return c,cp
 def test_angle_replacement_preserves_input(self):
  c,cp=self.fixture();old=copy.deepcopy(cp);p=model.initialize(cp)
  self.assertEqual(cp,old)
  for cell,pop in p.items():
   self.assertEqual([x[:2] for x in pop],[tuple(x[:2]) for x in cp['populations'][cell[0]]]);self.assertTrue(all(x[2]==cp['angle']+(math.pi/2 if cell[1]=='R' else 0) for x in pop))
 def test_paired_streams_and_branch_identity(self):
  c,cp=self.fixture();old=copy.deepcopy(cp);seen=[]
  def adv(pop,target,cfg,z,u):seen.append((id(z),id(u)));return advance(pop,target,cfg,z,u)
  with patch('model.advance',side_effect=adv):tr=model.evaluate(c,cp,dict(mutation_seed=81,survival_seed=91))
  self.assertEqual(cp,old);self.assertEqual(len(tr),20)
  for g in range(20):self.assertEqual(len(set(seen[g*4:g*4+4])),1);self.assertEqual(tr[g][0],tr[g][2]);self.assertEqual(tr[g][1],tr[g][3])
  mut=random.Random(81);sur=random.Random(91);z,u=draws(mut,sur,32);pop=advance(model.initialize(cp)['OR'],cp['target'],c['transfer'],z,u);self.assertEqual(model.performance(pop,cp['target'],c['transfer']['metric_matrix']),tr[0][1])
 def test_future_state_not_used(self):
  c,cp=self.fixture();seeds=dict(mutation_seed=31,survival_seed=42);a=model.evaluate(c,cp,seeds);cp['mutation_random_state']='invalid old future';cp['survival_random_state']='invalid';self.assertEqual(a,model.evaluate(c,cp,seeds))
 def test_variance_covariance_and_identity(self):
  x=[1.,2.,4.,-1.];y=[2.,3.,1.,0.];a=.7;r=corrected(a,x,y);self.assertAlmostEqual(cov(x,x),13/3);self.assertAlmostEqual(r['B25'],r['B6']+r['H']+r['X']);self.assertAlmostEqual(r['X'],r['X_direct'])
 def test_unbiased_correction_exact_enumeration(self):
  support=[(-1.,2.),(2.,1.),(3.,-2.)];a=.4;vals=[]
  for sample in itertools.product(support,repeat=2):vals.append(corrected(a,[v[0] for v in sample],[v[1] for v in sample]))
  mx=mean([v[0] for v in support]);my=mean([v[1] for v in support]);self.assertAlmostEqual(mean([v['B6'] for v in vals]),(a-mx)**2);self.assertAlmostEqual(mean([v['B25'] for v in vals]),(a-my)**2);self.assertAlmostEqual(mean([v['H'] for v in vals]),(my-mx)**2)
 def test_negative_corrected_estimates_retained(self):
  r=corrected(0.,[-1.,1.],[1.,-1.]);self.assertLess(r['B6'],0);self.assertLess(r['B25'],0);self.assertLess(r['H'],0)
 def test_sign_pairing_and_checkpoint_bootstrap(self):
  c,cp=self.fixture();trajectories=[]
  for j in range(24):
   tr=[[.5,.6+j*.001,.5,.6+j*.001] for _ in range(20)];tr[-1]=[.7,.4-j*.001,.7,.4-j*.001];trajectories.append(tr)
  r=checkpoint_summary(cp,'O',trajectories,c);self.assertEqual(r['conditional_classification'],{'6':'positive','25':'negative'});self.assertEqual(r['values']['ranking_reversal'],1);self.assertEqual(r['values']['M_resolved_agreement_g6'],1);self.assertEqual(r['values']['M_resolved_contradiction_g25'],1);self.assertLess(r['values']['covariance_D6_D25'],0)
  x=r['replicate_contrasts']['6'];y=r['replicate_contrasts']['25'];rng=random.Random(r['checkpoint_ci_seed']);b=[]
  for _ in range(2000):ids=[rng.randrange(24) for i in range(24)];b.append(sum(x[i] for i in ids)/24)
  b.sort();z=1999*.0125;i=int(z);self.assertAlmostEqual(r['conditional_ci975']['6'][0],b[i]*(1-z+i)+b[i+1]*(z-i))
 def test_seed_namespaces_and_classifications(self):
  a=seed_for(2026092108,'diagnostic-mutation','structured',0,'0',0,0);self.assertNotEqual(a,seed_for(2026092108,'diagnostic-mutation','isotropic',0,'0',0,0));self.assertNotEqual(a,seed_for(2026092108,'diagnostic-survival','structured',0,'0',0,0));self.assertEqual(classify([-1.,0.]),'unresolved');self.assertEqual(classify([0.,1.]),'unresolved');self.assertEqual(classify([.01,1.]),'positive')
if __name__=='__main__':unittest.main()
