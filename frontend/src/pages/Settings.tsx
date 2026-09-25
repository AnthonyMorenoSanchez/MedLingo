import {useEffect,useState} from 'react';
import {useProfile} from '../store/profile';
import {notify} from '../lib/tts';
import VoiceSettings from '../components/VoiceSettings';
import AISettings from '../components/AISettings';
export default function Settings(){const {settings,save}=useProfile();const [values,set]=useState(settings);useEffect(()=>{set(settings)},[settings]);return <div className="narrow"><h1>Settings</h1><form className="card setup-form" onSubmit={async e=>{e.preventDefault();try{await save(values);notify('Settings saved')}catch(e){notify((e as Error).message)}}}><label>Theme<select value={values.theme||'system'} onChange={e=>set({...values,theme:e.target.value})}><option value="system">System</option><option value="light">Light</option><option value="dark">Dark</option></select></label><label>Daily goal (minutes)<input type="number" min="1" max="180" value={values.daily_goal||15} onChange={e=>set({...values,daily_goal:+e.target.value})}/></label><VoiceSettings values={values} set={set}/><button className="btn">Save settings</button></form><AISettings/></div>}
