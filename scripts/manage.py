"""Cross-platform launcher. All subprocess arguments preserve spaces in paths."""
from pathlib import Path
import argparse
import os
import shutil
import subprocess
import sys
import venv

ROOT=Path(__file__).resolve().parents[1]
PY=ROOT/'.venv'/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
def run(args,cwd=ROOT):
    subprocess.run([str(x) for x in args],cwd=cwd,check=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('command',choices=['setup','run','build','voices','ollama','test'],nargs='?',default='run')
    args=parser.parse_args()
    if sys.version_info<(3,11):
        raise SystemExit('MedLingo requires Python 3.11 or newer. Install Python 3.11/3.12 and rerun.')
    if args.command=='setup':
        if not PY.exists():
            venv.EnvBuilder(with_pip=True).create(ROOT/'.venv')
        run([PY,'-m','pip','install','-e',ROOT/'backend'])
        if not (ROOT/'.env').exists():
            shutil.copy(ROOT/'.env.example',ROOT/'.env')
        print('Setup complete. Start with: python scripts/manage.py run')
    else:
        if not PY.exists():
            raise SystemExit('Run setup first.')
        if args.command=='run':
            run([PY,ROOT/'scripts/serve.py'])
        elif args.command=='build':
            npm=shutil.which('npm.cmd' if os.name=='nt' else 'npm')
            if not npm:
                raise SystemExit('Install Node.js/npm to rebuild; not required to run the bundled frontend.')
            run([npm,'ci'],ROOT/'frontend');run([npm,'run','build'],ROOT/'frontend')
        elif args.command=='test':
            run([PY,'-m','pytest'],ROOT/'backend')
        else:
            run([PY,ROOT/'scripts'/('setup_voices.py' if args.command=='voices' else 'setup_ollama.py'), *(['--microphone'] if args.command=='voices' else [])])
if __name__=='__main__':
    try:
        main()
    except subprocess.CalledProcessError as exc:
        raise SystemExit(exc.returncode)
