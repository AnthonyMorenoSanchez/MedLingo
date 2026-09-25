from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parents[1]
processes=[subprocess.Popen([sys.executable,'-m','uvicorn','app.main:app','--reload','--port','8000'],cwd=root/'backend'),subprocess.Popen(['npm','run','dev'],cwd=root/'frontend')]
try:
    for p in processes:p.wait()
except KeyboardInterrupt:
    for p in processes:p.terminate()
finally:
    for p in processes:
        p.terminate()
        p.wait()
