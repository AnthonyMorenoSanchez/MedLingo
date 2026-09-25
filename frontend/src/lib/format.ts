export const pretty=(s:string)=>s.replaceAll('_',' ').replace(/^./,x=>x.toUpperCase());export const number=(n:number)=>new Intl.NumberFormat().format(n);
