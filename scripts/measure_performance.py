"""Measure local process RSS and session creation latency on a disposable database."""
from pathlib import Path
import os,sys,subprocess,tempfile,shutil,time,urllib.request,json,statistics
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory() as tmp:
    env=dict(os.environ,MEDLINGO_USER_DB=str(Path(tmp)/'user.sqlite'),MEDLINGO_SEED_DB=str(root/'data/seed.sqlite'))
    p=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--port','8767'],cwd=root/'backend',env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        for _ in range(100):
            try:urllib.request.urlopen('http://127.0.0.1:8767/api/health',timeout=1);break
            except Exception:time.sleep(.1)
        pages=int(Path(f'/proc/{p.pid}/statm').read_text().split()[1]);rss=pages*os.sysconf('SC_PAGE_SIZE')
        times=[]
        for _ in range(20):
            req=urllib.request.Request('http://127.0.0.1:8767/api/sessions',data=json.dumps({'count':20,'specialties':['urology']}).encode(),headers={'Content-Type':'application/json'})
            start=time.perf_counter();response=json.load(urllib.request.urlopen(req));times.append((time.perf_counter()-start)*1000)
            assert response['session']['planned_count']==20
        result={'environment':'Linux container, not a laptop benchmark','idle_rss_mb':round(rss/1024/1024,2) if rss>10*1024*1024 else None,'session_create_p95_ms':round(sorted(times)[18],2),'session_create_median_ms':round(statistics.median(times),2),'samples':20}
        (root/'data/performance.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
        if rss>10*1024*1024:assert rss<150*1024*1024
        assert sorted(times)[18]<300
    finally:p.terminate();p.wait(timeout=10)
