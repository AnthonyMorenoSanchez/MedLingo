import type {ReactNode} from 'react';export default function Tooltip({text,children}:{text:string;children:ReactNode}){return <span title={text}>{children}</span>}
