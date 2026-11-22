// One-time setup: GitHub sends the browser here after "Create GitHub App" on the manifest page.
// It swaps the one-time code for the new app's ID and secret, saves them in this site's Netlify
// Blobs store (never shown, never sent to the browser) and sends the owner on to install the app.
// Only an app created by the site owner's GitHub account is accepted.
const crypto = require('crypto');
const { loadConfig, saveConfig, configured, siteUrl } = require('./_shared');
const OWNER = (process.env.SITE_OWNER || 'Ahmed200444').toLowerCase();
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
function page(body){
  return { statusCode: 200, headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer', 'X-Robots-Tag': 'noindex' },
    body: `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>GitHub publishing setup</title>
<style>body{font:16px/1.55 system-ui,sans-serif;max-width:720px;margin:32px auto;padding:0 16px;color:#1d2433;background:#fff}code,pre{font-family:ui-monospace,Consolas,monospace}
pre{background:#f3f5f9;border:1px solid #d9dee8;border-radius:8px;padding:10px 12px;overflow:auto;white-space:pre-wrap;word-break:break-all}.warn{background:#fff6e0;border:1px solid #f0d58a;border-radius:8px;padding:10px 12px}
a{color:#3b5bdb}@media (prefers-color-scheme:dark){body{background:#0f1420;color:#e6e9f0}pre{background:#171d2b;border-color:#2b3447}.warn{background:#2c2410;border-color:#6b5520}a{color:#8ea6ff}}</style></head><body>${body}</body></html>` };
}
exports.handler = async (event) => {
  await loadConfig(event);
  if (configured()) return page('<h1>Already set up</h1><p>GitHub publishing is already configured on this site. <a href="/">Back to the site</a>.</p>');
  const code = String((event.queryStringParameters || {}).code || '');
  if (!/^[A-Za-z0-9_-]{8,80}$/.test(code)) return page('<h1>No setup code</h1><p>Start from <a href="/github-setup.html">the setup page</a>.</p>');
  const r = await fetch(`https://api.github.com/app-manifests/${code}/conversions`, { method: 'POST', headers: { Accept: 'application/vnd.github+json', 'User-Agent': 'FDE-Study-Publisher' } });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) return page(`<h1>Setup code did not work</h1><p>${esc(d.message || 'GitHub refused the code')}. Codes work once and expire after an hour. Start again from <a href="/github-setup.html">the setup page</a>.</p>`);
  const owner = d.owner && d.owner.login ? d.owner.login.toLowerCase() : '';
  if (owner !== OWNER) return page('<h1>Not the site owner</h1><p>Only the owner of this site can set up publishing. Nothing was saved.</p>');
  const conf = { clientId: d.client_id, clientSecret: d.client_secret, slug: d.slug, appId: d.id, sessionSecret: crypto.randomBytes(32).toString('hex'), createdAt: new Date().toISOString() };
  const install = `https://github.com/apps/${encodeURIComponent(d.slug)}/installations/new`;
  try {
    await saveConfig(event, conf);
    return { statusCode: 302, headers: { Location: install, 'Cache-Control': 'no-store' }, body: '' };
  } catch (e) {
    // Blobs unavailable: fall back to showing the values once for Netlify's environment variables.
    const site = process.env.SITE_NAME || '';
    const envUrl = site ? `https://app.netlify.com/sites/${encodeURIComponent(site)}/configuration/env` : 'https://app.netlify.com/';
    const vars = [['GITHUB_CLIENT_ID', conf.clientId], ['GITHUB_CLIENT_SECRET', conf.clientSecret], ['GITHUB_APP_SLUG', conf.slug], ['SESSION_SECRET', conf.sessionSecret]];
    return page(`<h1>Your GitHub App "${esc(d.name)}" is ready</h1>
<p class="warn"><b>This page is shown once.</b> The site could not save the settings by itself, so copy the four values now. Don't share them or put them in the repository.</p>
<h2>1. Add these to Netlify</h2><p>Open <a href="${esc(envUrl)}" target="_blank" rel="noopener">your site's environment variables</a>, add each one (scope: Functions), then redeploy.</p>
${vars.map(([k, v]) => `<p><b>${k}</b></p><pre>${esc(v)}</pre>`).join('')}
<h2>2. Install the app</h2><p><a href="${esc(install)}" target="_blank" rel="noopener">Install it</a> on the repository you publish to.</p>`);
  }
};
