import Studio from './studio';
import {getChatGPTUser} from './chatgpt-auth';
export const dynamic='force-dynamic';
export default async function Page(){const user=await getChatGPTUser();return <Studio user={user?{name:user.email}:null}/>}
