"""Bounded sequence encoding and advisory release of this execution's I/O ranges."""
import os,json,gzip,hashlib,resource,time,pathlib
WINDOW=64*1024*1024
ADVICE=dict(supported=hasattr(os,"posix_fadvise"),attempts=0,errors=[])
def advise(fd,start,length):
 if ADVICE["supported"]:
  ADVICE["attempts"]+=1
  try:os.posix_fadvise(fd,start,length,os.POSIX_FADV_DONTNEED)
  except OSError as e:ADVICE["errors"].append(str(e))
class File:
 def __init__(self,path,mode):
  self.raw=open(path,mode+'b');self.z=gzip.GzipFile(fileobj=self.raw,mode=mode+'b',compresslevel=1);self.mode=mode;self.released=0
 def release(self,force=False):
  pos=self.raw.tell()
  if force or pos-self.released>=WINDOW:
   if self.mode=='w':self.z.flush();self.raw.flush();os.fdatasync(self.raw.fileno());pos=self.raw.tell()
   end=pos//4096*4096
   if end>self.released and hasattr(os,'posix_fadvise'):
    advise(self.raw.fileno(),self.released,end-self.released)
   self.released=end
 def write(self,v):
  b=json.dumps(v,separators=(',',':'),allow_nan=False).encode()+b'\n'
  assert len(b)<2**21,'single sequence encoding exceeds frozen2MiB cap'
  for start in range(0,len(b),2**20):self.z.write(b[start:start+2**20])
  self.release()
 def __iter__(self):return self
 def __next__(self):
  line=self.z.readline()
  if not line:raise StopIteration
  v=json.loads(line);self.release();return v
 def close(self):
  self.release(True);self.z.close()
  if self.mode=='w':self.raw.flush();os.fdatasync(self.raw.fileno())
  advise(self.raw.fileno(),0,0);self.raw.close()
 def __enter__(self):return self
 def __exit__(self,*args):self.close()
def sha(path):
 h=hashlib.sha256();last=0
 with open(path,'rb') as f:
  for b in iter(lambda:f.read(2**20),b''):
   h.update(b);pos=f.tell()
   if pos-last>=WINDOW and hasattr(os,'posix_fadvise'):
    advise(f.fileno(),last,pos-last)
    last=pos
  if hasattr(os,'posix_fadvise'):
   advise(f.fileno(),0,0)
 return h.hexdigest()
def save(path,v):
 with open(path,'w') as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
def telemetry(stage):
 return dict(stage=stage,time=time.time(),process_peak_rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,pid=os.getpid())
