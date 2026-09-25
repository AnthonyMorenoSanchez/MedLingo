import {useEffect,useState} from 'react';
import {api} from '../api/client';
import {notify,cancelSpeech} from '../lib/tts';
export default function ProfilePicker({onSelected}:{onSelected?:()=>void}){
 const [profiles,set]=useState<{id:number;name:string}[]>([]),[name,setName]=useState(''),[creating,setCreating]=useState(false);
 const selected=localStorage.getItem('medlingo.profile')||'';
 useEffect(()=>{api('/profiles').then(set).catch(e=>notify(e.message))},[]);
 function select(id:string){cancelSpeech();localStorage.setItem('medlingo.profile',id);if(onSelected)onSelected();else window.location.assign('/')}
 return <div className="profile-picker"><label>User <select aria-label="Active profile" value={selected} onChange={e=>{if(e.target.value)select(e.target.value)}}><option value="" disabled>Choose a profile</option>{profiles.map(p=><option key={p.id} value={p.id}>{p.name}</option>)}</select></label><button className="text-btn" onClick={()=>setCreating(!creating)}>Create user</button>{creating&&<form onSubmit={async e=>{e.preventDefault();try{const p=await api('/profiles','POST',{name});select(String(p.id))}catch(e){notify((e as Error).message)}}}><input aria-label="New profile name" placeholder="Name" maxLength={60} value={name} onChange={e=>setName(e.target.value)}/><button className="btn" disabled={!name.trim()}>Create</button></form>}</div>
}
