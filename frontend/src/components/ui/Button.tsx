import type {ButtonHTMLAttributes} from 'react';export default function Button(p:ButtonHTMLAttributes<HTMLButtonElement>){return <button {...p} className={'btn '+(p.className||'')}/>}
