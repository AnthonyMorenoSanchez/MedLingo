// PCM capture stays in the browser and is transcribed by the local Vosk backend.
export async function recordSpanish():Promise<{stop:()=>Promise<string>;cancel:()=>void}>{
 const stream=await navigator.mediaDevices.getUserMedia({audio:true});
 let context:AudioContext;
 try{context=new AudioContext()}catch(e){stream.getTracks().forEach(t=>t.stop());throw e}
 const source=context.createMediaStreamSource(stream);const processor=context.createScriptProcessor(4096,1,1);const chunks:Float32Array[]=[];let size=0,closed=false;
 const rate=context.sampleRate;
 processor.onaudioprocess=e=>{if(size<rate*60){const data=new Float32Array(e.inputBuffer.getChannelData(0));chunks.push(data);size+=data.length}};
 source.connect(processor);processor.connect(context.destination);
 const cleanup=()=>{if(closed)return;closed=true;processor.disconnect();source.disconnect();stream.getTracks().forEach(t=>t.stop());void context.close()};
 const timer=setTimeout(cleanup,60000);
 return {cancel:()=>{clearTimeout(timer);cleanup()},stop:async()=>{
  clearTimeout(timer);cleanup();const input=new Float32Array(size);let offset=0;chunks.forEach(c=>{input.set(c,offset);offset+=c.length});const n=Math.floor(size*16000/rate);const buffer=new ArrayBuffer(44+n*2);const view=new DataView(buffer);
  const write=(at:number,s:string)=>{for(let i=0;i<s.length;i++)view.setUint8(at+i,s.charCodeAt(i))};write(0,'RIFF');view.setUint32(4,36+n*2,true);write(8,'WAVE');write(12,'fmt ');view.setUint32(16,16,true);view.setUint16(20,1,true);view.setUint16(22,1,true);view.setUint32(24,16000,true);view.setUint32(28,32000,true);view.setUint16(32,2,true);view.setUint16(34,16,true);write(36,'data');view.setUint32(40,n*2,true);
  for(let i=0;i<n;i++){const start=Math.floor(i*rate/16000),end=Math.max(start+1,Math.floor((i+1)*rate/16000));let sum=0;for(let j=start;j<end&&j<input.length;j++)sum+=input[j];const sample=Math.max(-1,Math.min(1,sum/(end-start)));view.setInt16(44+i*2,sample<0?sample*32768:sample*32767,true)}
  const r=await fetch('/api/voice/transcribe',{method:'POST',headers:{'Content-Type':'audio/wav','X-Profile-ID':localStorage.getItem('medlingo.profile')||'1'},body:buffer});const data=await r.json();if(!r.ok)throw new Error(data.error?.message||'Transcription failed');return data.text;
 }};
}
