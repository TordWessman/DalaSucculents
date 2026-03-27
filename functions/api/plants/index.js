export async function onRequestGet(context) {
  const db = context.env.dala_succulents_db;
  const { results } = await db.prepare(`
    SELECT p.id, p.slug,
           CASE
               WHEN p.subspecies IS NOT NULL THEN g.name || ' ' || p.species || ' subsp. ' || p.subspecies
               WHEN p.variety IS NOT NULL THEN g.name || ' ' || p.species || ' var. ' || p.variety
               WHEN p.form IS NOT NULL THEN g.name || ' ' || p.species || ' f. ' || p.form
               WHEN p.cultivar IS NOT NULL THEN g.name || ' ' || p.species || ' ' || char(39) || p.cultivar || char(39)
               ELSE g.name || ' ' || p.species
           END AS display_name,
           g.name AS genus, g.family,
           p.vegetation_period,
           COUNT(s.id) AS specimen_count,
           SUM(CASE WHEN s.for_sale = 1 THEN 1 ELSE 0 END) AS for_sale_count,
           (SELECT s2.image_url FROM specimens s2 WHERE s2.plant_id = p.id AND s2.image_url IS NOT NULL LIMIT 1) AS image_url
    FROM plants p
    JOIN genera g ON g.id = p.genus_id
    LEFT JOIN specimens s ON s.plant_id = p.id
    GROUP BY p.id
    ORDER BY p.sort_order, g.name, p.species
  `).all();

  return Response.json({ results, success: true }, {
    headers: { 'Access-Control-Allow-Origin': '*' },
  });
}
