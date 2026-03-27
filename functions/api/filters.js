export async function onRequestGet(context) {
  const db = context.env.dala_succulents_db;

  const { results: familyRows } = await db.prepare(
    'SELECT DISTINCT family FROM genera ORDER BY family'
  ).all();
  const { results: genusRows } = await db.prepare(
    'SELECT DISTINCT name FROM genera ORDER BY name'
  ).all();
  const { results: vegRows } = await db.prepare(
    'SELECT DISTINCT vegetation_period FROM plants WHERE vegetation_period IS NOT NULL ORDER BY vegetation_period'
  ).all();
  const { results: expRows } = await db.prepare(
    'SELECT DISTINCT exposure FROM plants WHERE exposure IS NOT NULL ORDER BY exposure'
  ).all();

  return Response.json({
    family: familyRows.map(r => r.family),
    genus: genusRows.map(r => r.name),
    vegetation_period: vegRows.map(r => r.vegetation_period),
    exposure: expRows.map(r => r.exposure),
    success: true,
  }, {
    headers: { 'Access-Control-Allow-Origin': '*' },
  });
}
