"""Constructed fixtures only: no scientific reshape, continuation or production draws."""
import unittest,random,math,json,hashlib
from unittest.mock import patch
from common import read,verify_references
from operators064 import *
from analysis064 import *
from shape064_reference import sample_q,positive_qr,seed_for
from hpc_control import normalize,parse_accounting

class Fixtures(unittest.TestCase):
 def test_authentication_and_registry(self):
  self.assertEqual(verify_references(),10);entries=read('SHAPE_SEEDS.json');self.assertEqual(len(entries),1536);self.assertEqual(len({e['seed'] for e in entries}),1536)
  for i,e in enumerate(entries):
   self.assertEqual(e['index'],i);self.assertEqual(e['seed'],seed_for(e['history'],e['family'],e['task']))
   self.assertEqual(e['seed'],int(hashlib.sha256(('2026092564|state-shape064-row-orthogonal|%s|%s|%s'%(e['history'],e['family'],e['task'])).encode()).hexdigest()[:16],16))
 def test_sampler_order_and_positive_norm(self):
  q=sample_q(42);r=random.Random(42);g=[[r.gauss(0.,1.) for _ in range(31)] for _ in range(31)];self.assertEqual(q,positive_qr(g));orthogonality(q);basis_check()
  self.assertEqual(positive_qr([[-2.,0.],[0.,3.]]),[[-1.,0.],[0.,1.]])
  with self.assertRaises(ValueError):positive_qr([[0.,0.],[0.,0.]])
  with self.assertRaises(ValueError):positive_qr([[float('nan')]])
 def test_moments_rank_zero_and_branches(self):
  q=sample_q(43);h=[[3.25,1.299038105676658],[1.299038105676658,1.75]]
  for p in ([(.3,-.2,float(i)) for i in range(32)],[(i/100.,i/50.,float(i)) for i in range(32)],[(math.sin(i)/10.,math.cos(i)/10.,float(i)) for i in range(32)]):
   shaped,e=transform(p,q,(1.,.2),h);self.assertLessEqual(max(e['errors'].values()),1e-12)
   b=branches({'O':shaped,'R':shaped},.4);self.assertEqual(len({id(v) for v in b.values()}),4)
   for c in b:self.assertTrue(all(t[2]==.4+(math.pi/2 if c[1]=='R' else 0.) for t in b[c]))
   saved=b['OR'][0];b['OO'][0]=(9.,9.,9.);self.assertEqual(b['OR'][0],saved)
 def test_rng_cache_and_original_operator(self):
  m=random.Random(12);s=random.Random(13);m.gauss(0,1);self.assertIsNotNone(m.getstate()[2]);checkpoint=json.loads(json.dumps(dict(mutation_random_state=m.getstate(),survival_random_state=s.getstate())));a,b=restore(checkpoint)
  self.assertEqual(draws(m,s,32),draws(a,b,32));cfg=read('native_config002.json')['transfer'];pop=[(.01*i,-.005*i,.7) for i in range(32)]
  for _ in range(4):
   z,u=draws(a,b,32);expected=advance(pop,(1.,.2),cfg,z,u);actual,ids=advance_indices(pop,(1.,.2),cfg,z,u);self.assertEqual(actual,expected);self.assertEqual(len(set(ids)),32);pop=actual
 def test_stored_extraction(self):
  trajectory=[{c:dict(performance=-g-i/10.) for i,c in enumerate(('OO','OR','RO','RR'))} for g in range(25)];record=dict(trajectory=trajectory,endpoints={c:q['performance'] for c,q in trajectory[-1].items()});v=native_controls(record)
  self.assertEqual(len(v['trajectory']),21)
  for j,row in enumerate(v['trajectory']):
   for c in ('OO','OR','RO','RR'):self.assertEqual(row['NATIVE_'+c],trajectory[j+4][c])
  self.assertTrue(all(x<0 for x in v['endpoints'].values()))
 def test_metric_signs(self):
  y={c:float(i) for i,c in enumerate(CELLS)};y['NATIVE_OO']-=2;v=checked_metrics(y);self.assertEqual(len(v),20);self.assertEqual(v['DELTA'],-2.);self.assertEqual(v['G_MEAN'],-4.5)
  for cell in CELLS:
   x={c:float(c==cell) for c in CELLS};v=checked_metrics(x);expected=(1,-1,-1,1,-1,1,1,-1)[CELLS.index(cell)];self.assertEqual(v['DELTA'],expected)
 def test_all8_pairing_and_intervals(self):
  fixtures=[]
  for r in REGIMES:
   for h in range(24):
    for i,f in enumerate(FAMILIES):
     for t in range(8):fixtures.append(dict(regime=r,history=h,family=f,metrics={m:h+i+t/8.+(2 if r=='structured' else 0) for m in METRICS}))
  histories,groups=aggregate(fixtures);self.assertEqual(groups['structured|ALL8'][0]['DELTA'],5.9375);self.assertEqual(groups['structured_MINUS_isotropic|ALL8'][23]['DELTA'],2.)
  indices=[[i%24]*24 for i in range(2000)];est=estimate(groups,indices);self.assertEqual(len(est),380);self.assertEqual(est['structured_MINUS_isotropic|ALL8|DELTA']['ci95'],[2.,2.]);self.assertEqual(quantile([0,10],.25),2.5)
 def test_separate_audit_arithmetic(self):
  import audit064 as audit
  q=sample_q(44);self.assertEqual(q,audit.q_at(44));pop=[(.01*i,-.004*i,.2) for i in range(32)];cfg=read('native_config002.json')['transfer'];shaped,_=transform(pop,q,(1.,.2),cfg['metric_matrix']);independent=audit.reshape(pop,q)
  self.assertEqual([list(p[:2]) for p in shaped],independent)
  m=random.Random(14);s=random.Random(15)
  for _ in range(5):
   z,u=draws(m,s,32);actual,ids=advance_indices(pop,(1.,.2),cfg,z,u);expected,other_ids=audit.step([p[:2] for p in pop],(1.,.2),.2,z,u,cfg['metric_matrix']);self.assertEqual(ids,other_ids);self.assertEqual([p[:2] for p in actual],expected);pop=actual
 def test_memory_monitor_error_propagation(self):
  import resource_guard055 as guardmod
  guard=guardmod.Guard()
  def fail(_):raise RuntimeError('constructed monitor failure')
  with patch.object(guardmod,'save') as saved:guardmod.monitor(guard,fail);self.assertTrue(saved.called)
  with self.assertRaises(RuntimeError):guard.check()
 def test_binary_roundtrip_constructed(self):
  import tempfile,pathlib,os,struct
  from common import BinaryFile
  with tempfile.TemporaryDirectory() as d:
   f=pathlib.Path(d)/'fixture.gz'
   with patch.object(os,'fdatasync',getattr(os,'fdatasync',os.fsync),create=True):
    with BinaryFile(f,'w') as out:out.write(struct.pack('<4d',1.,-2.,3.,4.))
    with BinaryFile(f,'r') as source:self.assertEqual(struct.unpack('<4d',source.read_exact(32)),(1.,-2.,3.,4.))
 def test_submission_is_at_most_once(self):
  import tempfile,pathlib
  import hpc_control as controller
  from common import save as original_save
  with tempfile.TemporaryDirectory() as folder:
   root=pathlib.Path(folder)
   def rd(name):return json.loads((root/name).read_text())
   def wr(name,value):(root/name).write_text(json.dumps(value))
   with patch.object(controller,'P',root),patch.object(controller,'read',rd),patch.object(controller,'save',wr),patch.object(controller,'verify_manifest'),patch.object(controller,'verify_references'),patch.object(controller.subprocess,'run') as run:
    wr('submission.json',{'job_id':'123'})
    self.assertEqual(controller.submit()['job_id'],'123');run.assert_not_called();(root/'submission.json').unlink();wr('submission_attempt.json',{'ambiguous':True})
    with self.assertRaises(AssertionError):controller.submit()
    run.assert_not_called()
 def test_scheduler_unknown_never_success(self):
  self.assertEqual(normalize('COMPLETED','0:0'),'COMPLETE');self.assertEqual(normalize('COMPLETED','1:0'),'FAILED');self.assertEqual(normalize('','0:0'),'UNKNOWN');self.assertIsNone(parse_accounting('garbage','123'))
if __name__=='__main__':unittest.main(verbosity=2)
