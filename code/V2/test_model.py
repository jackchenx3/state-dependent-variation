import copy
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch
import model
from baseline_model import rotate,seed_for,predictor,summarize

class Correctness(unittest.TestCase):
    def cfg(self):
        c=json.loads((Path(__file__).parent/'config.json').read_text())
        c.update(population=4,test_generations=3)
        return c

    def test_first_draw_probability_oracle(self):
        # Weights 1 and 1/3: deterministic midpoint quadrature of exact CDF.
        draws=[model.sample_indices([0.,math.log(3)/10],[(i+.5)/1000])[0] for i in range(1000)]
        self.assertEqual(draws.count(0),750)
        self.assertEqual(draws.count(1),250)

    def test_conditional_without_replacement_oracle(self):
        distances=[0.,math.log(2)/10,math.log(4)/10]
        self.assertEqual(model.sample_indices(distances,[.6,.81,0.]),[1,2,0])
        # After index0 is drawn, weights .5,.25 renormalize to 2/3,1/3.
        second=[model.sample_indices(distances,[0.,(i+.5)/900])[1] for i in range(900)]
        self.assertEqual(second.count(1),600)
        self.assertEqual(second.count(2),300)

    def test_equal_candidates_remain_distinct(self):
        self.assertEqual(model.sample_indices([1,1,1],[0.,0.,0.]),[0,1,2])
        self.assertEqual(model.sample_indices([1,1,1],[.99,.99,.99]),[2,1,0])

    def test_best_candidate_can_die(self):
        self.assertEqual(model.sample_indices([0.,.01],[.99]),[1])

    def test_underflow_recenter_after_removal(self):
        self.assertEqual(model.sample_indices([0.,1000.,2000.],[.5,.5,.5]),[0,1,2])

    def test_loss_shift_invariance(self):
        a=[.1,.3,.7,.9]; u=[.71,.31,.94]
        self.assertEqual(model.sample_indices(a,u),model.sample_indices([x+5 for x in a],u))

    def test_sampler_rejects_invalid_input(self):
        for losses,u in [([],[]),([0],[0,0]),([-1],[.5]),([float('nan')],[.5]),([0],[1.]),([0],[-.1])]:
            with self.assertRaises(ValueError): model.sample_indices(losses,u)

    def test_negative_performance_is_valid(self):
        self.assertEqual(model.performance([(-1.,0.,0.)],(1.,0.)),-3.)
        with self.assertRaises(ValueError): model.performance([(0,0,0)],(0,0))

    def test_coordinate_equivariance(self):
        c=self.cfg(); a=model.transfer(c,.3,[1.,0.],991,882)
        b=model.transfer(c,1.0,rotate([1.,0.],.7),991,882)
        for x,y in zip(a,b):
            for u,v in zip(x,y): self.assertAlmostEqual(u,v,places=12)

    def test_reproducible_streams_and_no_global_rng(self):
        c=self.cfg()
        a=model.transfer(c,.2,[1.,0.],87,88)
        self.assertEqual(a,model.transfer(c,.2,[1.,0.],87,88))
        self.assertNotEqual(a,model.transfer(c,.2,[1.,0.],87,89))
        self.assertNotEqual(seed_for(c['seed'],'v2-mutation',0,'0',0),seed_for(c['seed'],'v2-survival',0,'0',0))

    def panel(self):
        c=self.cfg()
        p=predictor(.2,[1.,0.],c['major_sd'],c['minor_sd'])
        old=dict(regime='structured',history=0,family='0',task=0,angle=.2,target=[1.,0.],predictor=p)
        return c,dict(histories=[dict(regime='structured',history=0,angle=.2)],rows=[old])

    def test_no_training_or_outcome_leakage(self):
        c,b=self.panel()
        with patch('baseline_model.train',side_effect=AssertionError('training called')):
            histories,rows=model.assay_panel(c,b)
            changed=copy.deepcopy(b)
            changed['rows'][0].update(organized=-999,rotated=999,delta=-1998,trajectory=[[999,999]])
            _,other=model.assay_panel(c,changed)
        self.assertEqual(rows,other)
        self.assertEqual(histories,b['histories'])
        self.assertEqual(rows[0]['target'],b['rows'][0]['target'])
        self.assertEqual(rows[0]['angle'],b['rows'][0]['angle'])
        self.assertEqual(rows[0]['predictor'],b['rows'][0]['predictor'])

    def test_validator_accepts_decreases_and_negative_scores(self):
        c,b=self.panel(); _,rows=model.assay_panel(c,b)
        rows[0].update(organized=-2.,rotated=-3.,delta=1.,trajectory=[[.5,.4],[-1.,-.5],[-2.,-3.]])
        model.validate_rows(c,b,rows)
        bad=copy.deepcopy(rows);bad[0]['trajectory'][0][0]=float('nan')
        with self.assertRaises(ValueError):model.validate_rows(c,b,bad)
        bad=copy.deepcopy(rows);bad[0]['organized']=1.1
        with self.assertRaises(ValueError):model.validate_rows(c,b,bad)
        with self.assertRaises(ValueError):model.validate_rows(c,b,rows+rows)
        with self.assertRaises(ValueError):model.validate_rows(c,b,[])

    def test_fixed_coefficient_and_panel(self):
        c=json.loads((Path(__file__).parent/'config.json').read_text())
        b=json.loads((Path(__file__).parent/'baseline_result.json').read_text())
        model.validate_config(c);model.validate_baseline(c,b)
        changed=dict(c);changed['selection_coefficient']=11
        with self.assertRaises(ValueError):model.validate_config(changed)
        changed=dict(c);changed['test_generations']=24
        with self.assertRaises(ValueError):model.validate_baseline(changed,b)

    def test_summary_handles_negative_values(self):
        c=dict(seed=1,histories_per_regime=2,mismatch_degrees=[0],bootstrap_replicates=100)
        rows=[dict(regime=reg,family=f,history=h,delta=-1.,predictor=-.01,organized=-2.,rotated=-1.)
              for reg in ('structured','isotropic') for f in ('0','isotropic') for h in range(2)]
        out=summarize(c,rows)
        for contrast in out['contrasts']:
            self.assertEqual(contrast['mean_delta'],-1.)
            self.assertEqual(contrast['mean_organized'],-2.)
            self.assertEqual(contrast['classification'],'harm')

if __name__=='__main__':unittest.main()
