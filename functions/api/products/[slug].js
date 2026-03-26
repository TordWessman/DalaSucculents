export async function onRequestGet(context) {
  const slug = context.params.slug;
  const db = context.env.dala_succulents_db;
  const result = await db.prepare('SELECT * FROM products WHERE slug = ?').bind(slug).first();

  if (!result) {
    return Response.json({ error: 'Not found', success: false }, {
      status: 404,
      headers: { 'Access-Control-Allow-Origin': '*' },
    });
  }

  return Response.json({ result, success: true }, {
    headers: { 'Access-Control-Allow-Origin': '*' },
  });
}
