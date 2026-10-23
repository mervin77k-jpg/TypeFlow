export const DEVICE_PROFILES_KEY='typeflow-device-profiles';
export function readDeviceProfiles(storage){try{const value=JSON.parse(storage.getItem(DEVICE_PROFILES_KEY)||'[]');return Array.isArray(value)?value.filter(p=>p&&typeof p.id==='string'&&typeof p.name==='string'&&p.settings&&typeof p.settings==='object'):[]}catch{return []}}
export function changeDeviceProfiles(storage,action,createId=()=>crypto.randomUUID()){
 let profiles=readDeviceProfiles(storage);
 if(action.action==='profile'){
  const name=String(action.name||'').trim();if(!name||name.length>80)throw Error('Choose a profile name with 1–80 characters.');
  const index=profiles.findIndex(p=>p.id===action.id);
  if(index<0&&profiles.length>=2)throw Error('Device mode includes two profiles. Edit or delete an existing profile.');
  const profile={id:index<0?createId():action.id,name,settings:action.settings};
  if(index<0)profiles.push(profile);else profiles[index]=profile;
 }else if(action.action==='delete')profiles=profiles.filter(p=>p.id!==action.id);
 else throw Error('Cloud accounts are not configured on this deployment.');
 storage.setItem(DEVICE_PROFILES_KEY,JSON.stringify(profiles));return profiles;
}
