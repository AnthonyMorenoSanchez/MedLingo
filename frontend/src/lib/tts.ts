import {useProfile} from '../store/profile';
export interface Voice{id:string;name:string;lang:string;local?:boolean}
export interface TTSProvider{id:string;label:string;speak:(text:string,lang:'es'|'en',opts?:{voice?:string})=>Promise<void>;cancel:()=>void;voices:()=>Promise<Voice[]>}
export function notify(message:string){window.dispatchEvent(new CustomEvent('toast',{detail:message}))}
export function chooseVoice(voices:SpeechSynthesisVoice[],lang:string,preferred?:string){const matching=voices.filter(v=>v.localService&&v.lang.toLowerCase().startsWith(lang.toLowerCase()));return matching.find(v=>v.name===preferred)||matching[0]}
export class WebSpeechProvider implements TTSProvider{
 id='web_speech';label='Device voices (offline)';
 async voices(){if(!('speechSynthesis'in window))return [];return speechSynthesis.getVoices().filter(v=>v.localService).map(v=>({id:v.name,name:v.name,lang:v.lang,local:v.localService}))}
 cancel(){window.speechSynthesis?.cancel()}
 async speak(text:string,lang:'es'|'en',opts?:{voice?:string}){if(!('speechSynthesis'in window))throw new Error('Device speech unavailable. Choose a Piper offline voice in Settings.');this.cancel();let voices=speechSynthesis.getVoices();if(!voices.length){await new Promise(resolve=>setTimeout(resolve,300));voices=speechSynthesis.getVoices()}const voice=chooseVoice(voices,lang,opts?.voice);if(!voice)throw new Error(`No offline ${lang==='es'?'Spanish':'English'} device voice is installed. Choose Piper or install a matching Windows speech language pack.`);const u=new SpeechSynthesisUtterance(text);u.lang=voice.lang;u.voice=voice;u.rate=lang==='es'?.9:1;speechSynthesis.speak(u)}
}
const device=new WebSpeechProvider();let audio:HTMLAudioElement|null=null;let audioUrl:string|null=null;let generation=0;
export function cancelSpeech(){generation++;device.cancel();audio?.pause();if(audioUrl)URL.revokeObjectURL(audioUrl);audio=null;audioUrl=null}
export function activeProvider(){return device}
export async function speak(text:string,lang:'es'|'en'){
 cancelSpeech();const request=generation;const settings=useProfile.getState().settings;const provider=settings['tts_'+lang]||'web_speech';const voice=settings['voice_'+lang];
 try{
  if(provider==='web_speech'){await device.speak(text,lang,{voice});return}
  if(!voice)throw new Error('Select a voice for this language in Settings.');
  const response=await fetch('/api/voice/speak',{method:'POST',headers:{'Content-Type':'application/json','X-Profile-ID':localStorage.getItem('medlingo.profile')||'1'},body:JSON.stringify({text,lang,provider,voice})});
  if(!response.ok){const data=await response.json();throw new Error(data.error?.message||'Speech failed')}
  const blob=await response.blob();if(request!==generation)return;audioUrl=URL.createObjectURL(blob);audio=new Audio(audioUrl);await audio.play();
 }catch(e){notify((e as Error).message)}
}
