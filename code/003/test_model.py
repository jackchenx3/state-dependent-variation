import unittest,json,random,math
from pathlib import Path
import model,switch_model
class Correctness(unittest.TestCase):
    def setUp(self):
        self.cfg=json.loads(Path('config.json').read_text());self.pops={'O':[(0.,2.,.2),(2.,0.,.2),(1.,4.,.2)],'R':[(4.,-1.,.2),(7.,3.,.2),(1.,-2.,.2)]}
    def test_centroid_offsets_and_order(self):
        out,e=model.construct(self.pops,'O','R',.7);mu=model.centroid(self.pops['O']);donor=model.centroid(self.pops['R'])
        for i in (0,1):self.assertAlmostEqual(model.centroid(out)[i],mu[i])
        for x,y in zip(out,self.pops['R']):
            for i in (0,1):self.assertAlmostEqual(x[i]-mu[i],y[i]-donor[i])
        self.assertLess(e,1e-12);self.assertTrue(all(p[2]==.7 for p in out))
    def test_covariance_and_pairwise_geometry(self):
        out,_=model.construct(self.pops,'O','R',.7)
        for a,b in zip(out,self.pops['R']):
            for c,d in zip(out,self.pops['R']):
                self.assertAlmostEqual(sum((a[i]-c[i])**2 for i in (0,1)),sum((b[i]-d[i])**2 for i in (0,1)))
        def cov(pop):
            m=model.centroid(pop);return [[sum((p[i]-m[i])*(p[j]-m[j]) for p in pop)/len(pop) for j in (0,1)] for i in (0,1)]
        for a,b in zip(cov(out),cov(self.pops['R'])):
            for x,y in zip(a,b):self.assertAlmostEqual(x,y)
    def test_controls_exact_and_independent_containers(self):
        for arm in 'OR':
            out,_=model.construct(self.pops,arm,arm,.1)
            self.assertEqual([p[:2] for p in out],[p[:2] for p in self.pops[arm]]);self.assertIsNot(out,self.pops[arm]);out[0]=(9,9,9);self.assertNotEqual(out[0],self.pops[arm][0])
    def test_absolute_angles(self):
        for rule in 'OR':
            a=.25+(math.pi/2 if rule=='R' else 0);out,_=model.construct(self.pops,'R','O',a);self.assertTrue(all(p[2]==a for p in out))
    def test_checkpoint_continuation_exact_controls(self):
        c=json.loads(json.dumps(self.cfg));c['transfer']['population']=4
        row=dict(angle=.3,target=[.8,.6],mutation_seed=10,survival_seed=11)
        old,cp=switch_model.experiment(c,row);cp=dict(row,**json.loads(json.dumps(cp)))
        new=model.experiment(c,cp)
        for cell,previous in model.CONTROLS.items():
            for g in range(5,26):self.assertEqual(new['trajectory'][g-5][cell],old['trajectory'][g-1][previous])
    def test_known_factorial_identity(self):
        # response = 3*M*R + 5*S*R + 7*M*S*R, indicators O=1/R=0
        y={k:3*(k[0]=='O')*(k[2]=='O')+5*(k[1]=='O')*(k[2]=='O')+7*(k[0]=='O')*(k[1]=='O')*(k[2]=='O') for k in model.CELLS};v=model.contrasts(y)
        self.assertEqual(v['IM_O'],10);self.assertEqual(v['IM_R'],3);self.assertEqual(v['IS_O'],12);self.assertEqual(v['IS_R'],5);self.assertEqual(v['three_factor'],7);self.assertEqual(v['I_joint'],15);self.assertEqual(v['J_M'],6.5);self.assertEqual(v['J_S'],8.5)
    def test_random_factorial_and_loss_identities(self):
        rng=random.Random(55)
        for _ in range(100):
            v=model.contrasts({k:rng.uniform(-3,1) for k in model.CELLS});self.assertAlmostEqual(v['J_M']+v['J_S'],v['I_joint']);self.assertAlmostEqual(v['three_factor'],v['IS_O']-v['IS_R'])
        for m in 'OR':
            for s in 'OR':
                p,_=model.construct(self.pops,m,s,.2);v=model.measure(p,[1.,0.],self.cfg['transfer']['metric_matrix']);self.assertLess(v['identity_error'],1e-12)
if __name__=='__main__':unittest.main(verbosity=2)
