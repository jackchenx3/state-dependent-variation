import unittest,random,math,json
from pathlib import Path
import model
from v3_model import transfer
class Correctness(unittest.TestCase):
    def setUp(self):
        self.cfg=json.loads(Path('config.json').read_text());self.cfg['transfer']['population']=4;self.cfg['endpoint']=8;self.cfg['transfer']['test_generations']=8
        self.row=dict(angle=.31,target=[math.cos(.7),math.sin(.7)],mutation_seed=42,survival_seed=79)
    def test_original_arms_exact_recovery(self):
        r,cp=model.experiment(self.cfg,self.row);old=transfer(self.cfg['transfer'],.31,self.row['target'],42,79)
        self.assertEqual([[x['OO']['performance'],x['RR']['performance']] for x in r['trajectory']],old)
    def test_checkpoint_continuation_and_random_states(self):
        r,cp=model.experiment(self.cfg,self.row)
        for cell in model.CELLS:
            m=random.Random();s=random.Random();m.setstate(cp['mutation_random_state']);s.setstate(cp['survival_random_state'])
            pop=model.set_rule(cp['populations'][cell[0]],.31+(math.pi/2 if cell[1]=='R' else 0))
            for g in range(5,8):
                normals,uniforms=model.draws(m,s,4);pop=model.advance(pop,self.row['target'],self.cfg['transfer'],normals,uniforms)
                self.assertEqual(model.measure(pop,self.row['target'],self.cfg['transfer']['metric_matrix']),r['trajectory'][g][cell])
    def test_rule_switch_preserves_traits_order_every_angle(self):
        p=[(2.,3.,9.),(5.,-7.,8.),(1.,1.,7.)];q=model.set_rule(p,.31)
        self.assertEqual([x[:2] for x in q],[x[:2] for x in p]);self.assertTrue(all(x[2]==.31 for x in q));self.assertEqual(p[0][2],9.)
    def test_noop_switch(self):
        p=[(2.,3.,.31),(5.,-7.,.31)];self.assertEqual(model.set_rule(p,.31),p)
        self.assertEqual(model.set_rule(model.set_rule(p,.31+math.pi/2),.31),p)
    def test_population_covariance_N_and_loss_identity(self):
        p=[(0.,0.,0.),(2.,4.,0.)];m=model.measure(p,[1.,0.],[[1.,0.],[0.,1.]])
        self.assertEqual(m['centroid'],[1.,2.]);self.assertEqual(m['covariance'],[[1.,2.],[2.,4.]])
        self.assertEqual(m['centroid_loss'],4.);self.assertEqual(m['dispersion_loss'],5.);self.assertEqual(m['performance'],-8.)
    def test_anisotropic_identity(self):
        rng=random.Random(10);p=[(rng.gauss(0,1),rng.gauss(0,1),.31) for _ in range(32)]
        m=model.measure(p,self.row['target'],self.cfg['transfer']['metric_matrix']);self.assertLess(m['identity_error'],1e-12)
    def test_factorial_identity_known_and_random(self):
        c=model.contrasts(dict(OO=1.,OR=2.,RO=4.,RR=8.));self.assertEqual(c,dict(rule_given_O=-1.,rule_given_R=-4.,state_given_O=-3.,state_given_R=-6.,interaction=3.,rule=-2.5,state=-4.5,original=-7.))
        rng=random.Random(2)
        for _ in range(100):
            c=model.contrasts({k:rng.uniform(-2,1) for k in model.CELLS});self.assertAlmostEqual(c['rule']+c['state'],c['original'])
    def test_same_state_same_rule_same_draws(self):
        pop=[(0.,0.,.31) for _ in range(4)];m=random.Random(5);s=random.Random(6);z,u=model.draws(m,s,4)
        self.assertEqual(model.advance(pop,self.row['target'],self.cfg['transfer'],z,u),model.advance(list(pop),self.row['target'],self.cfg['transfer'],z,u))
if __name__=='__main__':unittest.main(verbosity=2)
