export async function onRequestPost() {
  const cookie = 'session=; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=0';

  return Response.json({ success: true }, {
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
