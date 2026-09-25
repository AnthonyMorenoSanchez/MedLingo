from pathlib import Path
import gzip,json,re
root=Path(__file__).resolve().parents[1]
html=(root/'frontend/dist/index.html').read_text()
initial=re.findall(r'(?:src|href)="(/assets/[^\"]+\.js)"',html)
size=sum(len(gzip.compress((root/'frontend/dist'/p.lstrip('/')).read_bytes())) for p in initial)
seed=(root/'data/seed.sqlite').stat().st_size
assert size<350*1024, f'Initial JS over budget: {size}'
assert seed<60*1024*1024, f'Seed over budget: {seed}'
print(json.dumps({'initial_js_gzip_bytes':size,'seed_bytes':seed,'budget':'PASS'},indent=2))
