// Step 2 of sign-in: check the state, swap the code for a user token, keep it in an encrypted HttpOnly cookie.
const { COOKIE, STATE_COOKIE, SESSION_AGE, siteUrl, encrypt, decrypt, cookies, cookie, redirect, tokenRequest, sessionFrom } = require('./_shared');
exports.handler = async (event) => {
  const q = event.queryStringParameters || {}, saved = decrypt(cookies(event)[STATE_COOKIE]);
  const back = saved && saved.back ? saved.back : '';
  try {
    if (!q.code || !q.state || !saved || saved.state !== q.state || Date.now() - saved.at > 600000) throw new Error('state');
    const s = sessionFrom(await tokenRequest({ code: q.code, redirect_uri: `${siteUrl()}/api/github/callback` }));
    return redirect(`${siteUrl()}/?github=connected${back}`, [cookie(COOKIE, encrypt(s), SESSION_AGE), cookie(STATE_COOKIE, '', 0)]);
  } catch (e) {
    return redirect(`${siteUrl()}/?github=error${back}`, [cookie(STATE_COOKIE, '', 0)]);
  }
};
