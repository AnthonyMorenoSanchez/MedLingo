export type Lang='en'|'es';
export type Kind='mcq'|'fill_blank'|'drag_slot'|'drag_order'|'listening'|'encounter';
export interface Payload {hint:{type:string;value:string};giveup:{answer_display:string;explanation_en:string;explanation_es:string;regional_notes:{region:string;es:string;note:string}[]};prompt?:string;prompt_lang?:Lang;audio_text:string;audio_lang:Lang;options?:{id:string;text?:string;text_es?:string;text_en?:string}[];tiles?:{id:string;text:string}[];sentence_masked?:string;lang?:Lang;patient_line_es?:string;patient_line_en?:string;[key:string]:any}
export interface Item {id:number;kind:Kind;direction:string;specialty_id:string;payload:Payload;correct_count?:number;wrong_count?:number;total_time_ms?:number;attempts?:number;last_seen_at?:string}
export interface StudySession{id:number;mode:string;planned_count:number;completed_count:number;correct_count:number;xp_earned:number;ended_at?:string;time_ms?:number;attempts?:any[]}
export interface Batch{session:StudySession;items:Item[]}
export interface Specialty{id:string;name_en:string;name_es:string;color:string;term_count:number}
export interface FeedbackResult{result:string;feedback:string;correct_answer:string;xp:number}
export interface QuestionProps{item:Item;onSubmit:(answer:string)=>void;onGiveUp:()=>void;onHint:()=>void;disabled:boolean}
