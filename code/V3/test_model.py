import copy,json,math,unittest
from pathlib import Path
from unittest.mock import patch
import model,v2_model,analysis
from baseline_model import rotate,predictor

class Correctness(unittest.TestCase):
    def cfg(self):
        c=json.loads((Path(__file__).parent/'config.json').read_text());c.update(population=4,test_generations=4);return c
    def test_metric_entries_and_initial_loss(self):
        h=self.cfg()['metric_matrix'];self.assertAlmostEqual(h[0][0]*h[1][1]-h[0][1]**2,4)
        for target in ([1,0],[0,1],[.3,.7]):
            self.assertAlmostEqual(model.normalized_loss([0,0],target,h),1)
            self.assertEqual(model.normalized_loss(target,target,h),0)
        major=rotate([1,0],math.pi/6);minor=rotate([0,1],math.pi/6)
        self.assertAlmostEqual(model.quadratic(major,h),4)
        self.assertAlmostEqual(model.quadratic(minor,h),1)
    def test_identity_loss_and_transfer_recovery(self):
        c=self.cfg();c['metric_matrix']=[[1.,0.],[0.,1.]]
        target=[1.,0.];x=[.4,-.2]
        self.assertAlmostEqual(model.normalized_loss(x,target,c['metric_matrix']),.4)
        a=model.transfer(c,.2,target,91,92);b=v2_model.transfer(c,.2,target,91,92)
        for p,q in zip(a,b):
            for u,v in zip(p,q):self.assertAlmostEqual(u,v,places=12)
    def test_metric_scale_invariance(self):
        c=self.cfg();h=c['metric_matrix'];scaled=[[7*x for x in row] for row in h]
        self.assertAlmostEqual(model.normalized_loss([.2,.3],[1.,0.],h),model.normalized_loss([.2,.3],[1.,0.],scaled))
        args=(.37,[1.,0.])
        self.assertAlmostEqual(model.log_expected_weight(*args,h,.12,.02,10),model.log_expected_weight(*args,scaled,.12,.02,10),places=12)
    def test_diagonal_analytic_oracle(self):
        target=[.6,.8];h=[[4.,0.],[0.,1.]];den=4*.6**2+.8**2
        expected=sum(-.5*math.log(1+20*q*v)-10*q*t*t/(1+20*q*v)
                     for q,v,t in zip([4/den,1/den],[.12**2,.02**2],target))
        self.assertAlmostEqual(model.log_expected_weight(0,target,h,.12,.02,10),expected,places=12)
    def test_zero_covariance_and_isotropic_rotation(self):
        c=self.cfg();h=c['metric_matrix'];t=[.6,.8]
        self.assertAlmostEqual(model.log_expected_weight(.2,t,h,0,0,10),-10,places=12)
        self.assertAlmostEqual(model.log_expected_weight(.1,t,h,.1,.1,10),model.log_expected_weight(1.3,t,h,.1,.1,10),places=12)
    def test_analytic_expectation_against_quadrature(self):
        # Independent Simpson integration in standard normal coordinates.
        c=self.cfg();h=c['metric_matrix'];t=[.6,.8];angle=.47
        n=160;step=20/n;ca,sa=math.cos(angle),math.sin(angle);total=0.
        for i in range(n+1):
            u=-10+i*step;wi=1 if i in (0,n) else (4 if i%2 else 2)
            for j in range(n+1):
                v=-10+j*step;wj=1 if j in (0,n) else (4 if j%2 else 2)
                x=.12*ca*u-.02*sa*v;y=.12*sa*u+.02*ca*v
                dx,dy=x-t[0],y-t[1]
                d=h[0][0]*t[0]**2+2*h[0][1]*t[0]*t[1]+h[1][1]*t[1]**2
                loss=(h[0][0]*dx**2+2*h[0][1]*dx*dy+h[1][1]*dy**2)/d
                total+=wi*wj*math.exp(-.5*(u*u+v*v)-10*loss)/(2*math.pi)
        integral=total*(step/3)**2
        self.assertAlmostEqual(model.log_expected_weight(angle,t,h,.12,.02,10),math.log(integral),places=8)
    def test_joint_rotation_equivariance(self):
        c=self.cfg();h=c['metric_matrix'];a=.63;r=[[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]]
        rotated=[[sum(r[i][k]*h[k][l]*r[j][l] for k in (0,1) for l in (0,1)) for j in (0,1)] for i in (0,1)]
        a0=model.transfer(c,.3,[1,0],15,16);other=copy.deepcopy(c);other['metric_matrix']=rotated
        a1=model.transfer(other,.3+a,rotate([1,0],a),15,16)
        for p,q in zip(a0,a1):
            for x,y in zip(p,q):self.assertAlmostEqual(x,y,places=11)
        self.assertAlmostEqual(model.log_expected_weight(.3,[1,0],h,.12,.02,10),model.log_expected_weight(.3+a,rotate([1,0],a),rotated,.12,.02,10),places=12)
    def test_euclidean_resources_not_metric_resources(self):
        h=self.cfg()['metric_matrix'];a=model.covariance(0,.12,.02);b=model.covariance(math.pi/2,.12,.02)
        self.assertAlmostEqual(a[0][0]+a[1][1],b[0][0]+b[1][1])
        self.assertAlmostEqual(a[0][0]*a[1][1]-a[0][1]**2,b[0][0]*b[1][1]-b[0][1]**2)
        metric=lambda c:sum(h[i][j]*c[j][i] for i in (0,1) for j in (0,1))
        self.assertGreater(abs(metric(a)-metric(b)),.001)
    def test_unchanged_sampling_no_replacement(self):
        self.assertEqual(model.sample_indices([0,math.log(2)/10,math.log(4)/10],[.6,.81,0]),[1,2,0])
        self.assertEqual(model.sample_indices([0,.01],[.99]),[1])
        self.assertEqual(model.sample_indices([0,1000,2000],[.5]*3),[0,1,2])
    def test_negative_values_valid(self):
        c=self.cfg();h=c['metric_matrix'];self.assertEqual(model.normalized_loss([-1,0],[1,0],h),4)
        b=dict(rows=[dict(regime='structured',history=0,family='0',task=0,angle=.2,target=[1.,0.],predictor=predictor(.2,[1.,0.],.12,.02))])
        fixed=model.freeze_predictions(c,b);rows=model.assay_panel(c,fixed)
        rows[0].update(organized=-2.,rotated=-3.,delta=1.,trajectory=[[.2,.1],[-.1,-.2],[-1.,-2.],[-2.,-3.]])
        model.validate_rows(c,b,fixed,rows)
        bad=copy.deepcopy(rows);bad[0]['trajectory'][1][0]=float('nan')
        with self.assertRaises(ValueError):model.validate_rows(c,b,fixed,bad)
    def test_predictors_frozen_without_outcome_access(self):
        c=self.cfg();b=dict(rows=[dict(regime='structured',history=0,family='0',task=0,angle=.2,target=[1.,0.],predictor=predictor(.2,[1.,0.],.12,.02))])
        with patch('baseline_model.train',side_effect=AssertionError('training')),patch('model.transfer',side_effect=AssertionError('transfer before freeze')):
            p=model.freeze_predictions(c,b);b['rows'][0].update(delta=999,organized=-999,rotated=999)
            self.assertEqual(p,model.freeze_predictions(c,b))
        self.assertEqual(p[0]['predictor'],b['rows'][0]['predictor'])
        self.assertAlmostEqual(p[0]['geometry_predictor'],p[0]['log_weight_organized']-p[0]['log_weight_rotated'])
    def test_all_crossing_directions_ties_and_missing(self):
        a=analysis.crossings(['0','15','30','45','60'],[1,-1,0,1,-1])
        self.assertEqual([x['direction'] for x in a['crossings']],['positive_to_negative','negative_to_positive','positive_to_negative'])
        self.assertEqual(a['crossings'][1]['tie_points'],['30'])
        empty=analysis.crossings(['0','15'],[1,1]);observed=analysis.crossings(['0','15'],[-1,1])
        self.assertEqual(analysis.crossing_category(empty,observed),'observed_only')
        self.assertEqual(analysis.crossing_category(observed,empty),'predicted_only')
        self.assertEqual(analysis.crossing_category(observed,observed),'same_crossings')
        self.assertEqual(analysis.crossing_category(empty,empty),'neither_detected')
        self.assertEqual(analysis.signed(1e-13),0)
    def test_frozen_config_panel_and_seed_changes(self):
        c=json.loads((Path(__file__).parent/'config.json').read_text());b=json.loads((Path(__file__).parent/'baseline_result.json').read_text())
        model.validate_config(c);model.validate_baseline(c,b)
        bad=copy.deepcopy(c);bad['metric_matrix'][0][0]=3
        with self.assertRaises(ValueError):model.validate_config(bad)
        bad=copy.deepcopy(c);bad['population']=33
        with self.assertRaises(ValueError):model.validate_baseline(bad,b)

if __name__=='__main__':unittest.main()
