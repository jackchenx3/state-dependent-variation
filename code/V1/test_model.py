import math
import random
import unittest
from model import rotate, proposal, loss, select, predictor, transfer, train, seed_for, summarize, crossing_record, localization, signed, validate_config, validate_roster

class Correctness(unittest.TestCase):
    def cfg(self):
        return dict(seed=7, population=4, training_generations=6, environment_period=2,
                    orientation_sd=.1, major_sd=.2, minor_sd=.03, test_generations=4)

    def test_spectrum_and_norm(self):
        # Gram matrix of transformed principal-axis basis preserves eigenvalues.
        a, b = proposal((1,0), .73, .2, .03), proposal((0,1), .73, .2, .03)
        self.assertAlmostEqual(sum(x*x for x in a), .04)
        self.assertAlmostEqual(sum(x*x for x in b), .0009)
        self.assertAlmostEqual(sum(x*y for x,y in zip(a,b)), 0)
        z = (.4, -1.7)
        u, v = proposal(z,.73,.2,.03), proposal(z,.73+math.pi/2,.2,.03)
        self.assertAlmostEqual(sum(x*x for x in u), sum(x*x for x in v))

    def test_exact_unselected_identity(self):
        # Four-point distribution has exactly identity covariance; no MC tolerance.
        x, t = (.3,-.2), (1.,0.)
        for angle in (0., .27, 1.8):
            values=[]
            for z in ((math.sqrt(2),0),(-math.sqrt(2),0),(0,math.sqrt(2)),(0,-math.sqrt(2))):
                d=proposal(z,angle,.2,.03)
                values.append(loss((x[0]+d[0],x[1]+d[1]),t))
            self.assertAlmostEqual(sum(values)/4,loss(x,t)+.04+.0009)

    def test_selection_oracle(self):
        p=[(2.,0.,0.),(0.,0.,0.),(.75,0.,0.),(1.,0.,0.)]
        self.assertEqual(select(p,(1.,0.),2), [p[3],p[2]])

    def test_coordinate_equivariance(self):
        c=self.cfg(); angle=.31; turn=.77
        a=transfer(c,angle,(1.,0.),17)
        b=transfer(c,angle+turn,rotate((1.,0.),turn),17)
        for x,y in zip(a,b):
            for i in range(2): self.assertAlmostEqual(x[i],y[i],places=12)

    def test_predictor_axis_and_swap(self):
        self.assertGreater(predictor(0,(1,0),.2,.03),0)
        self.assertLess(predictor(0,(0,1),.2,.03),0)
        self.assertAlmostEqual(predictor(.4,(1,0),.2,.03),-predictor(.4+math.pi/2,(1,0),.2,.03))
        self.assertEqual(predictor(.4,(1,0),.2,.2),0)

    def test_no_test_leakage(self):
        for regime in ('structured','isotropic'):
            c=self.cfg(); a=train(c,regime,0)
            c.update(test_generations=1000,mismatch_degrees=[89],tasks_per_family=999,
                     bootstrap_replicates=40,max_result_bytes=1)
            self.assertEqual(a,train(c,regime,0))
        self.assertNotEqual(seed_for(7,'train',0),seed_for(7,'transfer',0))

    def test_reproducible_and_monotone_selection(self):
        c=self.cfg(); a=transfer(c,.1,(1,0),12)
        self.assertEqual(a,transfer(c,.1,(1,0),12))
        for i in range(2):
            values=[0.]+[r[i] for r in a]
            self.assertTrue(all(-1e-12<=v<=1+1e-12 for v in values))
            self.assertTrue(all(x<=y+1e-12 for x,y in zip(values,values[1:])))
        with self.assertRaises(ValueError): transfer(c,0,(0,0),12)

    def test_history_is_inference_unit(self):
        c=dict(seed=1,histories_per_regime=2,mismatch_degrees=[0],bootstrap_replicates=100)
        rows=[]
        for regime in ('structured','isotropic'):
            for family in ('0','isotropic'):
                for h,d in enumerate((-.2,.4)):
                    rows.append(dict(regime=regime,family=family,history=h,delta=d,
                                     predictor=d,organized=.5+d,rotated=.5))
        a=summarize(c,rows); b=summarize(c,rows*5)
        self.assertEqual(a['localization_agreement'],b['localization_agreement'])
        for x,y in zip(a['contrasts'],b['contrasts']):
            self.assertEqual(x['classification'],y['classification'])
            for key in ('mean_delta','mean_predictor','sign_accuracy'):
                self.assertAlmostEqual(x[key],y[key],places=12)
            for u,v in zip(x['exploratory_pointwise_95_interval'],y['exploratory_pointwise_95_interval']):
                self.assertAlmostEqual(u,v,places=12)
        # Unequal nested counts must still give equal history weights.
        unequal=rows+[r for r in rows if r['history']==0]*4
        self.assertAlmostEqual(summarize(c,unequal)['contrasts'][0]['mean_delta'],.1)
        self.assertEqual(a['contrasts'][0]['classification'],'inconclusive')

    def test_reversal_ties_and_localization(self):
        grid=['0','45','90']
        for center in (0.,1e-13,-1e-13):
            r=crossing_record(grid,[1,center,-1])
            self.assertEqual(r['crossings'],[dict(bracket=['0','90'],tie_points=['45'])])
            self.assertEqual(localization(r,r),'ambiguous_ties')
        empty=crossing_record(grid,[0,0,0])
        simple=crossing_record(grid,[1,-1,-1])
        different=crossing_record(grid,[1,1,-1])
        multiple=crossing_record(['0','1','2','3'],[1,-1,1,-1])
        self.assertEqual(localization(empty,empty),'neither')
        self.assertEqual(localization(empty,simple),'observed_only')
        self.assertEqual(localization(simple,empty),'predicted_only')
        self.assertEqual(localization(simple,simple),'same_bracket')
        self.assertEqual(localization(simple,different),'different_bracket')
        self.assertEqual(localization(multiple,simple),'multiple')
        self.assertEqual(crossing_record(grid,[-1,0,1])['crossings'],[])
        self.assertEqual(signed(1e-12),0)

    def test_predictor_known_magnitude(self):
        self.assertAlmostEqual(predictor(0,(1,0),.2,.1),.03)
        self.assertAlmostEqual(predictor(math.pi/6,(1,0),.2,.1),.015)
        self.assertEqual(signed(predictor(math.pi/4,(1,0),.2,.1)),0)

    def test_config_and_roster_rejections(self):
        import json
        from pathlib import Path
        c=json.loads((Path(__file__).parent/'config.json').read_text())
        validate_config(c)
        for key,value in [('population',0),('major_sd',float('nan')),('max_attempts',2),
                          ('mismatch_degrees',[0,0]),('mismatch_degrees',[90,0])]:
            bad=dict(c); bad[key]=value
            with self.assertRaises(ValueError): validate_config(bad)
        c.update(histories_per_regime=2,tasks_per_family=1,mismatch_degrees=[0],test_generations=1)
        rows=[dict(regime=reg,history=h,family=f,task=0,predictor=0.,organized=.5,
                   rotated=.5,delta=0.,trajectory=[[.5,.5]])
              for reg in ('structured','isotropic') for h in range(2) for f in ('0','isotropic')]
        validate_roster(c,rows)
        with self.assertRaises(ValueError): validate_roster(c,rows[:-1])
        with self.assertRaises(ValueError): validate_roster(c,rows[:-1]+[rows[0]])
        bad=[dict(r) for r in rows]; bad[0]['delta']=float('nan')
        with self.assertRaises(ValueError): validate_roster(c,bad)

if __name__=='__main__': unittest.main()
