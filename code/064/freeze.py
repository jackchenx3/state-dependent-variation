"""Freeze authenticated source and passing fixture evidence, never production outcomes."""
import ast,tarfile
from common import *

def main():
 assert not (P/'SOURCE_SHA256SUMS').exists() and not (P/'RUN_STARTED.json').exists();assert read('TEST_STATUS.json')['status']=='PASS';verify_references()
 excluded={'EXECUTOR_STATUS.json','LOCAL_HANDOFF.json','NOTIFICATION_STATUS.json'}
 files=[f.name for f in sorted(P.iterdir()) if f.is_file() and f.name not in excluded and not f.name.startswith('.') and not f.name.endswith('.tmp')]
 for n in files:
  if n.endswith('.py'):ast.parse((P/n).read_text(),feature_version=(3,6))
 assert sha(P/'ASSIGNMENT.md')=='7c442d12806f069bdaf736fac8e9d1e4f9b08d0828fd0cf99d8d4a44df4ac1a8'
 save('DESIGN_FREEZE.json',dict(task_id='ORG-STATE-SHAPE-064',revision=1,freeze_unix=time.time(),task_sha256=sha(P/'ASSIGNMENT.md'),registry_sha256=sha(P/'SHAPE_SEEDS.json'),catalog_sha256=sha(P/'METRIC_CATALOG.json'),scientific_transformations=0,scientific_continuations=0,production_shape_matrices=0,production_bootstrap_draws=0))
 files.append('DESIGN_FREEZE.json');manifest('SOURCE_SHA256SUMS',files);verify_manifest('SOURCE_SHA256SUMS');assert package_bytes()<=LIMIT
 archive=P.parent/'shape064-source.tar'
 with tarfile.open(str(archive),'w') as t:
  for n in files+['SOURCE_SHA256SUMS']:t.add(str(P/n),arcname=n)
 print(json.dumps(dict(files=len(files),source_manifest_sha256=sha(P/'SOURCE_SHA256SUMS'),archive=str(archive),archive_sha256=sha(archive),archive_bytes=archive.stat().st_size)))
if __name__=='__main__':main()
