import pathlib,json,gzip,time
from io_utils import sha,File
P=pathlib.Path(__file__).resolve().parent
LIMIT=512*1024*1024

def read(n):return json.loads((P/n).read_text())
def save(n,value):
 f=P/n;f.parent.mkdir(parents=True,exist_ok=True);tmp=f.with_name(f.name+'.tmp');tmp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');tmp.replace(f)
def rows(n):
 with File(P/n,'r') as source:
  for row in source:yield row

def verify_manifest(n):
 for line in (P/n).read_text().splitlines():h,f=line.split('  ',1);assert sha(P/f)==h,f

def verify_references():
 binding=read('INPUT_BINDINGS.json')
 for n,h in binding['original_manifest_hashes'].items():assert sha(P/('ORIGINAL_'+n))==h
 for n,q in read('INPUT_COPY_MAP.json').items():
  assert sha(P/n)==q['sha256']==binding['files'][q['original_name']]['sha256'],n
  manifest=read_original_manifest(binding['files'][q['original_name']]['original_manifest']);assert manifest[q['original_name']]==q['sha256']
 for n,q in read('DEPENDENCY_HASHES.json').items():assert sha(P/n)==q['sha256']
 assert sha(P/'shape064_reference.py')==read('DESIGN_COMPLETE.json')['files']['source/shape064_reference.py']
 return 10

def read_original_manifest(n):return {line.split(None,1)[1]:line.split(None,1)[0] for line in (P/('ORIGINAL_'+n)).read_text().splitlines()}
def manifest(n,names):(P/n).write_text(''.join(sha(P/f)+'  '+f+'\n' for f in sorted(names)))
def package_bytes():return sum(f.stat().st_size for f in P.rglob('*') if f.is_file() and '__pycache__' not in f.parts)
def freeze_inputs(names):
 manifest('INPUT_SHA256SUMS',names);save('INPUT_FREEZE.json',dict(freeze_unix=time.time(),source_sha256=sha(P/'SOURCE_SHA256SUMS'),manifest_sha256=sha(P/'INPUT_SHA256SUMS'),files={n:sha(P/n) for n in names}))
class BinaryFile(File):
 def write(self,value):self.z.write(value);self.release()
 def read_exact(self,n):
  data=self.z.read(n);assert len(data)==n,'Incomplete binary record';self.release();return data
