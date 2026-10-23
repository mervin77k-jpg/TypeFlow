export const COMPANION_URL='http://127.0.0.1:31965';
export async function companionRequest(token,path,body,timeout=4000){
 const response=await fetch(COMPANION_URL+path,{method:body===undefined?'GET':'POST',credentials:'omit',cache:'no-store',headers:{Authorization:'Bearer '+token,...(body===undefined?{}:{'Content-Type':'application/json'})},body:body===undefined?undefined:JSON.stringify(body),signal:AbortSignal.timeout(timeout)});
 const data=await response.json();
 if(!response.ok)throw Error(data.error||'The Windows companion rejected the request.');
 return data;
}

