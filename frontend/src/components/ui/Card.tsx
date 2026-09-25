import type {HTMLAttributes} from 'react';export default function Card(p:HTMLAttributes<HTMLDivElement>){return <div {...p} className={'card '+(p.className||'')}/>}
