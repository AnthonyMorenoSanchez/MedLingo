export async function api<T=any>(path:string,method='GET',body?:unknown):Promise<T>{
 const response=await fetch('/api'+path,{method,headers:{'Content-Type':'application/json','X-Profile-ID':localStorage.getItem('medlingo.profile')||'1'},...(body===undefined?{}:{body:JSON.stringify(body)})});
 const data=await response.json();if(!response.ok)throw new Error(data.error?.message||'Request failed');return data as T;
}
