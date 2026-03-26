export async function onRequestGet(context) {
  const db = context.env.dala_succulents_db;
  const { results } = await db.prepare('SELECT * FROM products ORDER BY sort_order').all();
  return Response.json({ results, success: true }, {
    headers: { 'Access-Control-Allow-Origin': '*' },
  });
}
