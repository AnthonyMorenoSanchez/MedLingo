import importlib.util
import io
import json
import re
import wave
from functools import lru_cache
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.config import ROOT

router=APIRouter(prefix='/voice')
VOICE_DIR=ROOT/'data/voices'
# Users can add Piper .onnx + .onnx.json pairs in data/voices.
CATALOG=[
 {'id':'en_US-lessac-medium','name':'Lessac · US English · female','lang':'en-US'},
 {'id':'en_US-ryan-medium','name':'Ryan · US English · male','lang':'en-US'},
 {'id':'en_GB-alan-medium','name':'Alan · British English · male','lang':'en-GB'},
 {'id':'es_MX-ald-medium','name':'Ald · Mexican Spanish · male','lang':'es-MX'},
 {'id':'es_AR-daniela-high','name':'Daniela · Argentine Spanish · female','lang':'es-AR'},
 {'id':'es_ES-davefx-medium','name':'Dave · Spain Spanish · male','lang':'es-ES'},
]

def voices():
    found={v['id']:v for v in CATALOG}
    for path in VOICE_DIR.glob('*.onnx'):
        vid=path.stem
        if vid not in found and re.fullmatch(r'[\w-]+',vid):
            found[vid]={'id':vid,'name':vid,'lang':vid.split('-')[0].replace('_','-')}
    return [{**v,'installed':(VOICE_DIR/(v['id']+'.onnx')).exists() and (VOICE_DIR/(v['id']+'.onnx.json')).exists()} for v in found.values()]

@router.get('/catalog')
def catalog():
    return {'piper':voices(),'piper_available':importlib.util.find_spec('piper') is not None,'edge_available':importlib.util.find_spec('edge_tts') is not None,'stt_available':importlib.util.find_spec('vosk') is not None and (ROOT/'data/stt/es').is_dir()}

@router.get('/online-voices')
async def online_voices():
    try:
        import edge_tts
        data=await edge_tts.list_voices()
        return [{'id':v['ShortName'],'name':v['FriendlyName']+' · '+v['Gender'],'lang':v['Locale']} for v in data if v['Locale'].startswith(('en-','es-'))]
    except ImportError as exc:
        raise HTTPException(409,'Install optional speech dependencies using the setup instructions.') from exc
    except Exception as exc:
        raise HTTPException(502,'Online voice catalog unavailable. Offline voices still work.') from exc

class Speech(BaseModel):
    text: str=Field(min_length=1,max_length=5000)
    lang: Literal['es','en']
    provider: Literal['piper','edge']='piper'
    voice: str=Field(min_length=1,max_length=150,pattern=r'^[\w-]+$')

@lru_cache(maxsize=2)
def load_voice(path):
    from piper import PiperVoice
    return PiperVoice.load(path)

@router.post('/speak')
async def speak(body: Speech):
    if not body.voice.replace('_','-').lower().startswith(body.lang+'-'):
        raise HTTPException(422,'Choose a voice matching the text language.')
    if body.provider=='edge':
        try:
            import edge_tts
            audio=bytearray()
            async for chunk in edge_tts.Communicate(body.text,body.voice).stream():
                if chunk['type']=='audio':
                    audio.extend(chunk['data'])
            return Response(bytes(audio),media_type='audio/mpeg')
        except ImportError as exc:
            raise HTTPException(409,'Install optional speech dependencies first.') from exc
        except Exception as exc:
            raise HTTPException(502,'Online speech failed. Switch to an offline voice.') from exc
    path=VOICE_DIR/(body.voice+'.onnx')
    if not path.exists() or not path.with_suffix('.onnx.json').exists():
        raise HTTPException(409,'Download this Piper voice using the voice setup script first.')
    try:
        from starlette.concurrency import run_in_threadpool
        def synthesize():
            buffer=io.BytesIO()
            with wave.open(buffer,'wb') as wav:
                load_voice(str(path)).synthesize_wav(body.text,wav)
            return buffer.getvalue()
        audio=await run_in_threadpool(synthesize)
        return Response(audio,media_type='audio/wav')
    except ImportError as exc:
        raise HTTPException(409,'Install piper-tts using the voice setup instructions.') from exc
    except Exception as exc:
        raise HTTPException(502,'Offline speech failed. Check the voice pack and Piper installation.') from exc

@lru_cache(maxsize=1)
def speech_model():
    from vosk import Model
    return Model(str(ROOT/'data/stt/es'))

@router.post('/transcribe')
async def transcribe(request: Request):
    audio=bytearray()
    async for chunk in request.stream():
        audio.extend(chunk)
        if len(audio)>4_000_000:
            raise HTTPException(413,'Recording is too long. Record up to one minute.')
    try:
        with wave.open(io.BytesIO(audio),'rb') as wav:
            if wav.getnchannels()!=1 or wav.getsampwidth()!=2 or wav.getframerate()!=16000:
                raise HTTPException(422,'Use 16 kHz mono PCM WAV audio.')
            frames=wav.readframes(wav.getnframes())
        if not (ROOT/'data/stt/es').is_dir():
            raise HTTPException(409,'Install the offline Spanish microphone model with scripts/setup_voices.py --microphone.')
        from starlette.concurrency import run_in_threadpool
        from vosk import KaldiRecognizer
        def recognize():
            recognizer=KaldiRecognizer(speech_model(),16000)
            recognizer.AcceptWaveform(frames)
            return json.loads(recognizer.FinalResult()).get('text','')
        return {'text':await run_in_threadpool(recognize)}
    except ImportError as exc:
        raise HTTPException(409,'Install optional speech dependencies first.') from exc
    except (wave.Error,EOFError) as exc:
        raise HTTPException(422,'Invalid WAV audio.') from exc
