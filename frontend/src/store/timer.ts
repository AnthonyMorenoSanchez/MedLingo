import {create} from 'zustand';
interface Timer{elapsed:number;started:number|null;reset:()=>void;pause:()=>void;resume:()=>void;read:()=>number}
export const useTimer=create<Timer>((set,get)=>({elapsed:0,started:null,reset:()=>set({elapsed:0,started:document.hidden?null:performance.now()}),pause:()=>{const s=get();set({elapsed:s.elapsed+(s.started===null?0:performance.now()-s.started),started:null})},resume:()=>{if(get().started===null)set({started:performance.now()})},read:()=>{const s=get();return Math.round(s.elapsed+(s.started===null?0:performance.now()-s.started))}}));
