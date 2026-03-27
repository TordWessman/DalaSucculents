export async function onRequestGet(context) {
  const slug = context.params.slug;
  const db = context.env.dala_succulents_db;

  const plant = await db.prepare(`
    SELECT p.*, g.name AS genus, g.family
    FROM plants p
    JOIN genera g ON g.id = p.genus_id
    WHERE p.slug = ?
  `).bind(slug).first();

  if (!plant) {
    return Response.json({ error: 'Not found', success: false }, {
      status: 404,
      headers: { 'Access-Control-Allow-Origin': '*' },
    });
  }

  // Build display_name
  let display_name = plant.genus + ' ' + plant.species;
  if (plant.subspecies) display_name += ' subsp. ' + plant.subspecies;
  else if (plant.variety) display_name += ' var. ' + plant.variety;
  else if (plant.form) display_name += ' f. ' + plant.form;
  else if (plant.cultivar) display_name += " '" + plant.cultivar + "'";

  const { results: countries } = await db.prepare(`
    SELECT c.name FROM plant_countries pc
    JOIN countries c ON c.alpha3 = pc.country_alpha3
    WHERE pc.plant_id = ?
    ORDER BY c.name
  `).bind(plant.id).all();

  const { results: specimens } = await db.prepare(`
    SELECT id, specimen_code, for_sale, price, propagation_method,
           propagation_date, image_url
    FROM specimens WHERE plant_id = ?
    ORDER BY specimen_code
  `).bind(plant.id).all();

  const { results: images } = await db.prepare(`
    SELECT id, image_url, caption, sort_order
    FROM plant_images WHERE plant_id = ?
    ORDER BY sort_order, id
  `).bind(plant.id).all();

  const result = {
    id: plant.id,
    slug: plant.slug,
    display_name,
    genus: plant.genus,
    family: plant.family,
    species: plant.species,
    author_citation: plant.author_citation,
    cultivation: {
      vegetation_period: plant.vegetation_period,
      substrate: plant.substrate,
      winter_temp_range: plant.winter_temp_range,
      watering: plant.watering,
      exposure: plant.exposure,
    },
    conservation: {
      red_list_status: plant.red_list_status,
      red_list_url: plant.red_list_url,
      cites_listing: plant.cites_listing,
      llifle_url: plant.llifle_url,
    },
    countries: countries.map(r => r.name),
    notes: plant.notes,
    specimens: specimens.map(s => ({ ...s, for_sale: Boolean(s.for_sale) })),
    images,
  };

  return Response.json({ result, success: true }, {
    headers: { 'Access-Control-Allow-Origin': '*' },
  });
}
