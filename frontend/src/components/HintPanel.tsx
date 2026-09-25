import {Lightbulb} from 'lucide-react';export default function HintPanel({text}:{text:string}){return text?<div className="hint-panel" role="status"><Lightbulb size={18}/>{text}</div>:null}
