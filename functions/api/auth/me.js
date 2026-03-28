import { getSessionUser } from '../../_auth.js';

export async function onRequestGet(context) {
  const { request, env } = context;
  const db = env.dala_succulents_db;

  const payload = await getSessionUser(request, env);
  if (!payload) {
    return Response.json({ success: true, user: null }, {
      headers: { 'Access-Control-Allow-Origin': '*' },
    });
  }

  const user = await db.prepare('SELECT id, email, name, picture_url, role FROM users WHERE id = ?')
    .bind(payload.user_id).first();

  return Response.json({ success: true, user: user || null }, {
    headers: { 'Access-Control-Allow-Origin': '*' },
  });
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
