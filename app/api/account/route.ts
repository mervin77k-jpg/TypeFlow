/** Cloud account API is intentionally unavailable until a Vercel-compatible backend is configured. */
export async function GET(){return Response.json({error:'Cloud accounts are not configured on this deployment. Use the local studio and device profiles.',code:'BACKEND_NOT_CONFIGURED'},{status:503});}
export const POST=GET;
