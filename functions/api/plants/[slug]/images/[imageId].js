import { getSessionUser } from '../../../../_auth.js';

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'DELETE, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export async function onRequestOptions() {
  return new Response(null, { status: 204, headers: CORS_HEADERS });
}

export async function onRequestDelete(context) {
  const user = await getSessionUser(context.request, context.env);
  if (!user || user.role !== 'admin') {
    return Response.json({ error: 'Admin access required', success: false }, {
      status: 403, headers: CORS_HEADERS,
    });
  }

  const { slug, imageId } = context.params;
  const db = context.env.dala_succulents_db;
  const bucket = context.env.IMAGES_BUCKET;
  const publicUrl = context.env.R2_PUBLIC_URL || '';

  const plant = await db.prepare('SELECT id FROM plants WHERE slug = ?').bind(slug).first();
  if (!plant) {
    return Response.json({ error: 'Plant not found', success: false }, {
      status: 404, headers: CORS_HEADERS,
    });
  }

  const image = await db.prepare(
    'SELECT id, image_url FROM plant_images WHERE id = ? AND plant_id = ?'
  ).bind(imageId, plant.id).first();

  if (!image) {
    return Response.json({ error: 'Image not found', success: false }, {
      status: 404, headers: CORS_HEADERS,
    });
  }

  // Extract R2 key from URL and delete from bucket
  if (publicUrl && image.image_url.startsWith(publicUrl)) {
    const r2Key = image.image_url.slice(publicUrl.length + 1);
    try {
      await bucket.delete(r2Key);
    } catch {
      // best-effort R2 cleanup
    }
  }

  await db.prepare('DELETE FROM plant_images WHERE id = ?').bind(imageId).run();

  return Response.json({ success: true }, { headers: CORS_HEADERS });
}
