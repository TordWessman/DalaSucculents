import { getSessionUser } from '../../../_auth.js';

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export async function onRequestOptions() {
  return new Response(null, { status: 204, headers: CORS_HEADERS });
}

export async function onRequestGet(context) {
  const { slug } = context.params;
  const db = context.env.dala_succulents_db;

  const plant = await db.prepare('SELECT id FROM plants WHERE slug = ?').bind(slug).first();
  if (!plant) {
    return Response.json({ error: 'Not found', success: false }, {
      status: 404, headers: CORS_HEADERS,
    });
  }

  const { results: images } = await db.prepare(`
    SELECT id, image_url, caption, sort_order
    FROM plant_images WHERE plant_id = ?
    ORDER BY sort_order, id
  `).bind(plant.id).all();

  return Response.json({ results: images, success: true }, { headers: CORS_HEADERS });
}

export async function onRequestPost(context) {
  const user = await getSessionUser(context.request, context.env);
  if (!user || user.role !== 'admin') {
    return Response.json({ error: 'Admin access required', success: false }, {
      status: 403, headers: CORS_HEADERS,
    });
  }

  const { slug } = context.params;
  const db = context.env.dala_succulents_db;
  const bucket = context.env.IMAGES_BUCKET;
  const publicUrl = context.env.R2_PUBLIC_URL || '';

  const plant = await db.prepare('SELECT id FROM plants WHERE slug = ?').bind(slug).first();
  if (!plant) {
    return Response.json({ error: 'Plant not found', success: false }, {
      status: 404, headers: CORS_HEADERS,
    });
  }

  const formData = await context.request.formData();
  const file = formData.get('file');
  if (!file || !(file instanceof File)) {
    return Response.json({ error: 'Missing file', success: false }, {
      status: 400, headers: CORS_HEADERS,
    });
  }

  const allowed = new Set(['image/jpeg', 'image/png', 'image/webp']);
  if (!allowed.has(file.type)) {
    return Response.json({ error: 'Invalid image type (jpeg/png/webp only)', success: false }, {
      status: 400, headers: CORS_HEADERS,
    });
  }

  if (file.size > 10 * 1024 * 1024) {
    return Response.json({ error: 'File too large (max 10 MB)', success: false }, {
      status: 413, headers: CORS_HEADERS,
    });
  }

  const caption = formData.get('caption') || '';
  let ext = file.type.split('/')[1];
  if (ext === 'jpeg') ext = 'jpg';
  const key = `prod/plants/${plant.id}/${crypto.randomUUID()}.${ext}`;

  await bucket.put(key, file.stream(), {
    httpMetadata: { contentType: file.type },
  });

  const imageUrl = `${publicUrl}/${key}`;
  const result = await db.prepare(
    'INSERT INTO plant_images (plant_id, image_url, caption) VALUES (?, ?, ?) RETURNING id, image_url, caption, sort_order'
  ).bind(plant.id, imageUrl, caption).first();

  return Response.json({ result, success: true }, {
    status: 201, headers: CORS_HEADERS,
  });
}
