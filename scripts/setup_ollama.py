"""Interactive local setup; downloads are never triggered on application startup."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app.services.hardware import detect

def main():
    hardware=detect()
    print(json.dumps(hardware,indent=2))
    executable=shutil.which('ollama')
    if not executable:
        answer=input('Install Ollama in this Windows/WSL environment? [y/N] ').lower()
        if answer!='y':
            print('Download manually from https://ollama.com/download then rerun this script.');return
        if os.name=='nt':
            winget=shutil.which('winget')
            if not winget:
                print('Open https://ollama.com/download/windows and install Ollama, then rerun.');return
            subprocess.run([winget,'install','--id','Ollama.Ollama','-e','--accept-package-agreements','--accept-source-agreements'],check=True)
            executable=shutil.which('ollama')
            default=Path(os.environ.get('LOCALAPPDATA',''))/'Programs/Ollama/ollama.exe'
            if not executable and default.is_file():
                executable=str(default)
        else:
            with tempfile.TemporaryDirectory() as folder:
                script=Path(folder)/'install.sh'
                urllib.request.urlretrieve('https://ollama.com/install.sh',script)
                subprocess.run(['sh',str(script)],check=True)
            executable=shutil.which('ollama')
    if not executable:
        print('Open a new terminal after installation and rerun this script.');return
    def reachable():
        try:
            with urllib.request.urlopen('http://127.0.0.1:11434/api/tags',timeout=2):
                return True
        except OSError:
            return False
    if not reachable():
        log=ROOT/'data/ollama.log';log.parent.mkdir(exist_ok=True)
        with log.open('ab') as output:
            kwargs={'creationflags':subprocess.CREATE_NEW_PROCESS_GROUP} if os.name=='nt' else {'start_new_session':True}
            subprocess.Popen([executable,'serve'],stdout=output,stderr=output,**kwargs)
        for _ in range(20):
            if reachable():
                break
            time.sleep(1)
    if not reachable():
        print('Ollama did not start. Run ollama serve and inspect data/ollama.log.');return
    recommended=hardware['recommended_model']
    chosen=input(f'Model [{recommended}] (Enter accepts; or type another Ollama model): ').strip() or recommended
    if chosen.startswith('-') or len(chosen)>100:
        raise SystemExit('Invalid model name')
    if input(f'Download {chosen}? Allow several GB of disk space. [y/N] ').lower()=='y':
        subprocess.run([executable,'pull',chosen],check=True)
        print(f'Ready. In MedLingo Settings choose Ollama, base URL http://127.0.0.1:11434, model {chosen}, then Save & test connection.')
if __name__=='__main__':
    main()
