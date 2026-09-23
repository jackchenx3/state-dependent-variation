"""Check release hashes, source provenance, local links and plotted statistics."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    verified=0
    for line in (ROOT/'SHA256SUMS').read_text().splitlines():
        expected,name=line.split(None,1)
        path=ROOT/name
        assert path.is_file() and sha(path)==expected,name
        verified+=1
    source_map=json.loads((ROOT/'provenance/EXPORT_MAP.json').read_text())
    for record in source_map:
        assert sha(ROOT/record['path'])==record['published_sha256'],record['path']
    checked=0
    for record in json.loads((ROOT/'figures/FIGURE_SOURCES.json').read_text())['sources']:
        q=json.loads((ROOT/record['path']).read_text())
        for component in record['route']:q=q[component]
        assert q==record['value'],record['route']
        checked+=1
    manuscript_records=ROOT/'provenance/MANUSCRIPT_STATISTICS.json'
    if manuscript_records.exists():
        for record in json.loads(manuscript_records.read_text())['displayed_statistics']:
            q=json.loads((ROOT/'results'/record['study']/'summary.json').read_text())['values'][record['key']]
            assert q==record['value'],record['key']
    broken=[];links=0
    for path in ROOT.rglob('*.md'):
        if any(p in path.parts for p in ['.git','_rebuilt']):continue
        for target in re.findall(r'\]\(([^)]+)\)',path.read_text()):
            if target.startswith(('https://','http://','mailto:','#')):continue
            target=target.split('#')[0]
            if target:
                links+=1
                if not (path.parent/target).resolve().exists():broken.append((str(path.relative_to(ROOT)),target))
    assert not broken,broken
    files=[p for p in ROOT.rglob('*') if p.is_file() and not any(v in p.parts for v in ['.git','_rebuilt','__pycache__'])]
    leaks=[]
    for path in files:
        if path.suffix in ['.md','.json','.jsonl','.py','.txt','.yml','.cff']:
            text=path.read_text()
            if re.search(r'/Users/[A-Za-z0-9_.-]+/|/mnt/ccrsf-static/Analysis/[A-Za-z0-9_.-]+/|gh[pousr]_[A-Za-z0-9]{25,}|github_pat_[A-Za-z0-9_]{25,}|-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY',text):
                leaks.append(str(path.relative_to(ROOT)))
    assert not leaks,leaks
    print(json.dumps(dict(status='PASS',manifest_files=verified,source_records=len(source_map),
                          figure_statistic_records=checked,local_links=links,
                          broken_links=0,detected_private_paths_or_secrets=0),indent=2))

if __name__=='__main__':main()
