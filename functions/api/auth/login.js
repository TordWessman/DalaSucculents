import { signJWT } from '../../_auth.js';

export async function onRequestPost(context) {
  const { request, env } = context;
  const db = env.dala_succulents_db;

  let credential;
  try {
    const body = await request.json();
    credential = body.credential;
  } catch {
    return Response.json({ error: 'Invalid request body', success: false }, { status: 400 });
  }

  if (!credential) {
    return Response.json({ error: 'Missing credential', success: false }, { status: 400 });
  }

  // Verify Google ID token
  const verifyRes = await fetch(`https://oauth2.googleapis.com/tokeninfo?id_token=${credential}`);
  if (!verifyRes.ok) {
    return Response.json({ error: 'Invalid Google token', success: false }, { status: 401 });
  }
  const idinfo = await verifyRes.json();

  const google_id = idinfo.sub;
  const email = idinfo.email;
  const name = idinfo.name || '';
  const picture = idinfo.picture || '';

  const adminEmails = (env.ADMIN_EMAILS || '').split(',').map(e => e.trim());
  const role = adminEmails.includes(email) ? 'admin' : 'user';

  // Upsert user
  await db.prepare(`
    INSERT INTO users (google_id, email, name, picture_url, role, last_login)
    VALUES (?, ?, ?, ?, ?, datetime('now'))
    ON CONFLICT(google_id) DO UPDATE SET
      email = excluded.email,
      name = excluded.name,
      picture_url = excluded.picture_url,
      role = excluded.role,
      last_login = datetime('now')
  `).bind(google_id, email, name, picture, role).run();

  const user = await db.prepare('SELECT id, email, name, picture_url, role FROM users WHERE google_id = ?')
    .bind(google_id).first();

  const exp = Math.floor(Date.now() / 1000) + 7 * 24 * 60 * 60; // 7 days
  const token = await signJWT({ user_id: user.id, email, role, exp }, env.JWT_SECRET);
  const cookie = `session=${token}; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=604800`;

  return Response.json({
    success: true,
    user: { id: user.id, email, name, picture_url: picture, role },
  }, {
    headers: {
      'Set-Cookie': cookie,
      'Access-Control-Allow-Origin': '*',
    },
  });
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
