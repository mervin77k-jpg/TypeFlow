// Never trust Sites identity headers outside the Sites dispatch boundary.
export async function GET(){return Response.json({error:'Not found'},{status:404});}
export const POST=GET;
