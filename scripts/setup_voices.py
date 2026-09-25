"""Download voice packs once; synthesis and Spanish transcription then work offline."""
from pathlib import Path
import argparse
import json
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile

ROOT=Path(__file__).resolve().parents[1]
BASE='https://huggingface.co/rhasspy/piper-voices/resolve/main/'
DEFAULT=['en_US-lessac-medium','en_US-ryan-medium','es_MX-ald-medium','es_AR-daniela-high']

def download(url,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(path.suffix+'.part')
    try:
        with urllib.request.urlopen(url,timeout=120) as source,tmp.open('wb') as target:
            shutil.copyfileobj(source,target)
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--voices',nargs='+',default=DEFAULT)
    parser.add_argument('--microphone',action='store_true',help='Also download the 39 MB Spanish Vosk model')
    parser.add_argument('--list',action='store_true',help='List English/Spanish packs from the current Piper catalog')
    args=parser.parse_args()
    if not args.list:
        subprocess.run([sys.executable,'-m','pip','install','piper-tts>=1.3,<2','edge-tts>=7,<8','vosk>=0.3.45,<0.4'],check=True)
    with urllib.request.urlopen(BASE+'voices.json',timeout=60) as response:
        catalog=json.load(response)
    if args.list:
        print('\n'.join(k for k in catalog if k.startswith(('en_','es_'))));return
    for vid in args.voices:
        if vid not in catalog:
            raise SystemExit(f'{vid} not in the catalog; run --list to see available packs.')
        for name in catalog[vid]['files']:
            if name.endswith(('.onnx','.onnx.json')):
                target=ROOT/'data/voices'/Path(name).name
                if not target.exists():
                    print('Downloading',name,flush=True);download(BASE+name,target)
        # Retain the model card for voice provenance/license alongside each pack.
        voice_path=next(n for n in catalog[vid]['files'] if n.endswith('.onnx'))
        card=str(Path(voice_path).parent/'MODEL_CARD')
        try:
            download(BASE+card,ROOT/'data/voices'/(vid+'.MODEL_CARD'))
        except OSError:
            print('Model card available at',BASE+card)
    if args.microphone and not (ROOT/'data/stt/es').exists():
        with tempfile.TemporaryDirectory() as folder:
            archive=Path(folder)/'model.zip'
            download('https://alphacephei.com/vosk/models/vosk-model-small-es-0.42.zip',archive)
            with zipfile.ZipFile(archive) as z:
                for name in z.namelist():
                    if not (Path(folder)/name).resolve().is_relative_to(Path(folder).resolve()):
                        raise SystemExit('Unsafe archive path')
                z.extractall(folder)
            target=ROOT/'data/stt/es';target.parent.mkdir(parents=True,exist_ok=True)
            shutil.move(str(Path(folder)/'vosk-model-small-es-0.42'),str(target))
    print('Ready. Restart MedLingo and select installed Piper voices in Settings. Internet is no longer needed for these voices.')
if __name__=='__main__':
    main()
