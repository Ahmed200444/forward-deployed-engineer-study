// Step 1 of sign-in: send the browser to GitHub with a random state, remembered in a short-lived cookie.
const crypto = require('crypto');
const { STATE_COOKIE, env, configured, siteUrl, encrypt, cookie, redirect } = require('./_shared');
exports.handler = async (event) => {
  if (!configured()) return redirect(`${siteUrl()}/?github=not-set-up`);
  const state = crypto.randomBytes(24).toString('hex');
  let back = String((event.queryStringParameters || {}).return || '');
  if (!/^#\/[A-Za-z0-9/_-]{0,120}$/.test(back)) back = '';
  const q = new URLSearchParams({ client_id: env('GITHUB_CLIENT_ID'), redirect_uri: `${siteUrl()}/api/github/callback`, state });
  return redirect(`https://github.com/login/oauth/authorize?${q}`, [cookie(STATE_COOKIE, encrypt({ state, at: Date.now(), back }), 600)]);
};
