// One-time setup: GitHub sends the browser here after "Create GitHub App" on the manifest page.
// It swaps the one-time code for the new app's ID and secret and shows them once, so they can be
// pasted into Netlify's environment variables. Nothing is stored here.
const crypto = require('crypto');
const { configured } = require('./_shared');
const esc = s => String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
function page(body){
  return { statusCode: 200, headers: { 'Content-Type': 'text/html; charset=utf-8', 'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer', 'X-Robots-Tag': 'noindex' },
    body: `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex"><title>GitHub publishing setup</title>
<style>body{font:16px/1.55 system-ui,sans-serif;max-width:720px;margin:32px auto;padding:0 16px;color:#1d2433;background:#fff}code,pre{font-family:ui-monospace,Consolas,monospace}
pre{background:#f3f5f9;border:1px solid #d9dee8;border-radius:8px;padding:10px 12px;overflow:auto;white-space:pre-wrap;word-break:break-all}.warn{background:#fff6e0;border:1px solid #f0d58a;border-radius:8px;padding:10px 12px}
a{color:#3b5bdb}@media (prefers-color-scheme:dark){body{background:#0f1420;color:#e6e9f0}pre{background:#171d2b;border-color:#2b3447}.warn{background:#2c2410;border-color:#6b5520}a{color:#8ea6ff}}</style></head><body>${body}</body></html>` };
}
exports.handler = async (event) => {
  if (configured()) return page('<h1>Already set up</h1><p>GitHub publishing is already configured on this site. <a href="/">Back to the site</a>.</p>');
  const code = String((event.queryStringParameters || {}).code || '');
  if (!/^[A-Za-z0-9_-]{8,80}$/.test(code)) return page('<h1>No setup code</h1><p>Start from <a href="/github-setup.html">the setup page</a>.</p>');
  const r = await fetch(`https://api.github.com/app-manifests/${code}/conversions`, { method: 'POST', headers: { Accept: 'application/vnd.github+json', 'User-Agent': 'FDE-Study-Publisher' } });
  const d = await r.json().catch(() => ({}));
  if (!r.ok) return page(`<h1>Setup code did not work</h1><p>${esc(d.message || 'GitHub refused the code')}. Codes work once and expire after an hour. Start again from <a href="/github-setup.html">the setup page</a>.</p>`);
  const site = process.env.SITE_NAME || '';
  const envUrl = site ? `https://app.netlify.com/sites/${encodeURIComponent(site)}/configuration/env` : 'https://app.netlify.com/';
  const vars = [['GITHUB_CLIENT_ID', d.client_id], ['GITHUB_CLIENT_SECRET', d.client_secret], ['GITHUB_APP_SLUG', d.slug], ['SESSION_SECRET', crypto.randomBytes(32).toString('hex')]];
  return page(`<h1>Your GitHub App "${esc(d.name)}" is ready</h1>
<p class="warn"><b>This page is shown once.</b> Copy the four values now. Don't share them or put them in the repository.</p>
<h2>1. Add these to Netlify</h2><p>Open <a href="${esc(envUrl)}" target="_blank" rel="noopener">your site's environment variables</a>, choose <b>Add a variable</b> for each one (scope: Functions), then save.</p>
${vars.map(([k, v]) => `<p><b>${k}</b></p><pre>${esc(v)}</pre>`).join('')}
<h2>2. Redeploy</h2><p>In Netlify, open <b>Deploys</b> and choose <b>Trigger deploy</b>, then <b>Deploy site</b>, so the functions pick up the new values.</p>
<h2>3. Give the app your portfolio repository</h2><p><a href="https://github.com/apps/${esc(encodeURIComponent(d.slug))}/installations/new" target="_blank" rel="noopener">Install the app</a>, choose <b>Only select repositories</b> and pick the repository you publish to.</p>
<h2>4. Publish</h2><p>Open any exercise or project on the site and press <b>Publish to GitHub</b>. The first time, GitHub asks you to sign in and authorise the app.</p>`);
};
