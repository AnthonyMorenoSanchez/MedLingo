"""Isolated browser tests and a test-only restart control endpoint."""
from pathlib import Path
import subprocess,sys,os,tempfile,shutil,time,threading
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
import urllib.request
root=Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='medlingo-e2e-') as temp:
    env=dict(os.environ,MEDLINGO_USER_DB=str(Path(temp)/'user.sqlite'),MEDLINGO_SEED_DB=str(Path(temp)/'seed.sqlite'),MEDLINGO_TEST_URL='http://127.0.0.1:8765',MEDLINGO_HEARTBEAT_SECONDS='0.5')
    shutil.copy(root/'data/seed.sqlite',env['MEDLINGO_SEED_DB'])
    log=(root/'data/e2e-server.log').open('w')
    process=None
    def start():
        global process
        process=subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8765'],cwd=root/'backend',env=env,stdout=log,stderr=log)
        for _ in range(100):
            try:
                urllib.request.urlopen('http://127.0.0.1:8765/api/health',timeout=1).read();return
            except Exception:time.sleep(.1)
        raise RuntimeError('Test server did not start')
    class Control(BaseHTTPRequestHandler):
        def do_POST(self):
            if self.path!='/restart':self.send_error(404);return
            process.terminate();process.wait(timeout=10);start()
            self.send_response(200);self.end_headers();self.wfile.write(b'OK')
        def log_message(self,*args):pass
    control=ThreadingHTTPServer(('127.0.0.1',8766),Control)
    threading.Thread(target=control.serve_forever,daemon=True).start()
    try:
        start()
        result=subprocess.run(['npx','playwright','test',*sys.argv[1:]],cwd=root/'frontend',env=env)
    finally:
        control.shutdown()
        if process:process.terminate();process.wait(timeout=10)
        log.close()
    raise SystemExit(result.returncode)
