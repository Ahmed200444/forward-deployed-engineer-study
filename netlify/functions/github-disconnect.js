// Signs out: revokes the user token at GitHub (when possible) and clears the cookie.
const { COOKIE, cookie, json, session, csrfOk, loadConfig, cfg } = require('./_shared');
exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') return json(405, { error: 'Method not allowed.' });
  const clear = [cookie(COOKIE, '', 0)];
  try {
    if (!(await loadConfig(event))) return json(200, { ok: true }, clear);
    const { session: s } = await session(event);
    if (s && csrfOk(event, s)){
      const basic = Buffer.from(`${cfg().clientId}:${cfg().clientSecret}`).toString('base64');
      await fetch(`https://api.github.com/applications/${encodeURIComponent(cfg().clientId)}/token`, {
        method: 'DELETE', headers: { Accept: 'application/vnd.github+json', Authorization: `Basic ${basic}`, 'User-Agent': 'FDE-Study-Publisher', 'Content-Type': 'application/json' },
        body: JSON.stringify({ access_token: s.accessToken }) }).catch(() => {});
    }
  } catch (e) {}
  return json(200, { ok: true }, clear);
};
