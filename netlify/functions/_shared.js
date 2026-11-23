// Shared helpers for the GitHub publishing functions.
// Pattern taken from the CS & AI Mastery site: GitHub App user sign-in, an AES-256-GCM
// encrypted HttpOnly cookie for the session, and secrets only in Netlify environment variables.
const crypto = require('crypto');
const COOKIE = 'fde_gh_session';
const STATE_COOKIE = 'fde_gh_state';
const API_VERSION = '2022-11-28';
const SESSION_AGE = 60 * 60 * 24 * 180;
// Overridable only so the functions can be tested against a local mock of GitHub; production uses the defaults.
const API_BASE = (process.env.GITHUB_API_BASE || 'https://api.github.com').replace(/\/$/, '');
const WEB_BASE = (process.env.GITHUB_WEB_BASE || 'https://github.com').replace(/\/$/, '');

// App settings come from Netlify environment variables if they are set, otherwise from the
// site's Netlify Blobs store, where the one-time setup (github-setup.js) saves them. The browser never sees them.
let CFG = null;
function store(event){
  try {
    const { getStore, connectLambda } = require('@netlify/blobs');
    if (event && event.blobs) connectLambda(event);
    return getStore('github-publisher');
  } catch (e) { return null; }
}
async function loadConfig(event){
  const e = process.env;
  if (e.GITHUB_CLIENT_ID && e.GITHUB_CLIENT_SECRET && e.SESSION_SECRET) return (CFG = { clientId: e.GITHUB_CLIENT_ID, clientSecret: e.GITHUB_CLIENT_SECRET, slug: e.GITHUB_APP_SLUG || '', sessionSecret: e.SESSION_SECRET });
  if (CFG) return CFG;
  const st = store(event); if (!st) return null;
  const c = await st.get('config', { type: 'json' }).catch(() => null);
  if (c && c.clientId && c.clientSecret && c.sessionSecret) CFG = c;
  return CFG;
}
async function saveConfig(event, c){ const st = store(event); if (!st) throw new Error('Netlify Blobs is not available.'); await st.setJSON('config', c); CFG = c; }
function cfg(){ if (!CFG) throw new Error('GitHub publishing is not set up.'); return CFG; }
function configured(){ return !!CFG; }
function siteUrl(){ return (process.env.SITE_URL || process.env.URL || '').replace(/\/$/, ''); }
function key(){ return crypto.createHash('sha256').update(cfg().sessionSecret).digest(); }
function b64url(buf){ return Buffer.from(buf).toString('base64url'); }
function encrypt(obj){
  const iv = crypto.randomBytes(12), cipher = crypto.createCipheriv('aes-256-gcm', key(), iv);
  const body = Buffer.concat([cipher.update(JSON.stringify(obj), 'utf8'), cipher.final()]);
  return [b64url(iv), b64url(cipher.getAuthTag()), b64url(body)].join('.');
}
function decrypt(v){
  if (!v) return null;
  try {
    const [i, t, b] = v.split('.').map(x => Buffer.from(x, 'base64url'));
    const d = crypto.createDecipheriv('aes-256-gcm', key(), i); d.setAuthTag(t);
    return JSON.parse(Buffer.concat([d.update(b), d.final()]).toString('utf8'));
  } catch (e) { return null; }
}
function cookies(event){
  const raw = (event.headers.cookie || event.headers.Cookie || ''), out = {};
  raw.split(';').forEach(p => { const i = p.indexOf('='); if (i > 0) out[p.slice(0, i).trim()] = decodeURIComponent(p.slice(i + 1).trim()); });
  return out;
}
function cookie(name, value, maxAge){ return `${name}=${encodeURIComponent(value)}; Path=/; SameSite=Lax; Secure; HttpOnly; Max-Age=${maxAge}`; }
const NO_STORE = { 'Cache-Control': 'no-store' };
function json(status, body, setCookies = []){
  const out = { statusCode: status, headers: { 'Content-Type': 'application/json; charset=utf-8', ...NO_STORE }, body: JSON.stringify(body) };
  if (setCookies.length) out.multiValueHeaders = { 'Set-Cookie': setCookies };
  return out;
}
function redirect(url, setCookies = []){
  const out = { statusCode: 302, headers: { Location: url, ...NO_STORE }, body: '' };
  if (setCookies.length) out.multiValueHeaders = { 'Set-Cookie': setCookies };
  return out;
}
function header(event, name){ const h = event.headers || {}; return h[name] || h[name.toLowerCase()] || ''; }
function originAllowed(event){ const allowed = siteUrl(), o = header(event, 'origin'); return !allowed || !o || o === allowed; }
function csrfOk(event, s){ return originAllowed(event) && !!s && !!s.csrf && header(event, 'x-fde-csrf') === s.csrf; }

async function gh(path, token, options = {}){
  const r = await fetch(`${API_BASE}${path}`, { ...options, headers: {
    Accept: 'application/vnd.github+json', Authorization: `Bearer ${token}`, 'X-GitHub-Api-Version': API_VERSION,
    'User-Agent': 'FDE-Study-Publisher', ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...(options.headers || {}) } });
  const text = await r.text(); let data = {}; try { data = text ? JSON.parse(text) : {}; } catch (e) {}
  if (!r.ok){ const err = new Error(data.message || `GitHub request failed (${r.status})`); err.status = r.status; throw err; }
  return data;
}
async function tokenRequest(params){
  const body = new URLSearchParams({ client_id: cfg().clientId, client_secret: cfg().clientSecret, ...params });
  const r = await fetch(`${WEB_BASE}/login/oauth/access_token`, { method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/x-www-form-urlencoded' }, body });
  const d = await r.json().catch(() => ({}));
  if (!r.ok || d.error) throw new Error(d.error_description || d.error || 'GitHub sign-in failed.');
  return d;
}
function sessionFrom(d, old = {}){
  return { ...old, accessToken: d.access_token, refreshToken: d.refresh_token || old.refreshToken || null,
    expiresAt: d.expires_in ? Date.now() + d.expires_in * 1000 : null,
    csrf: old.csrf || crypto.randomBytes(24).toString('hex') };
}
// Returns {session, cookie}; cookie is set when an expired user token was refreshed.
async function session(event){
  const s = decrypt(cookies(event)[COOKIE]);
  if (!s || !s.accessToken) return { session: null, cookie: null };
  if (!s.expiresAt || s.expiresAt > Date.now() + 60000) return { session: s, cookie: null };
  if (!s.refreshToken) return { session: null, cookie: cookie(COOKIE, '', 0) };
  try {
    const n = sessionFrom(await tokenRequest({ grant_type: 'refresh_token', refresh_token: s.refreshToken }), s);
    return { session: n, cookie: cookie(COOKIE, encrypt(n), SESSION_AGE) };
  } catch (e) { return { session: null, cookie: cookie(COOKIE, '', 0) }; }
}
function strongSecret(text){
  const rules = [[/github_pat_[A-Za-z0-9_]{20,}/, 'GitHub token'], [/gh[pousr]_[A-Za-z0-9]{20,}/, 'GitHub token'], [/sk-(?:ant-)?[A-Za-z0-9_-]{20,}/, 'API key'],
    [/AKIA[0-9A-Z]{16}/, 'AWS access key'], [/AIza[0-9A-Za-z_-]{30,}/, 'Google API key'], [/xox[baprs]-[A-Za-z0-9-]{10,}/, 'Slack token'], [/-----BEGIN [A-Z ]*PRIVATE KEY-----/, 'private key']];
  for (const [re, n] of rules) if (re.test(text)) return n;
  return null;
}
function safePath(p){
  p = String(p || '').replace(/\\/g, '/').replace(/^\/+/, '').replace(/\/+$/, '');
  if (!p || p.length > 300 || p.split('/').some(x => !x || x === '.' || x === '..' || x === '.git' || !/^[A-Za-z0-9._ -]+$/.test(x))) { const e = new Error('Invalid file path: ' + p); e.status = 400; throw e; }
  return p;
}
// The review token: what the learner saw on the review screen (destination, branch head, exact files),
// signed with the session key. Publish refuses to write anything that does not match it.
function gitBlobSha(content){ const b = Buffer.from(content, 'utf8'); return crypto.createHash('sha1').update(`blob ${b.length}\0`).update(b).digest('hex'); }
function filesDigest(files){ const h = crypto.createHash('sha256'); for (const f of [...files].sort((a, b) => a.path < b.path ? -1 : 1)) h.update(f.path + '\0' + gitBlobSha(f.content) + '\n'); return h.digest('hex'); }
function signReview(o){ const body = b64url(JSON.stringify(o)); return body + '.' + b64url(crypto.createHmac('sha256', key()).update('review.' + body).digest()); }
function readReview(t){
  const [body, mac] = String(t || '').split('.');
  if (!body || !mac) return null;
  const want = b64url(crypto.createHmac('sha256', key()).update('review.' + body).digest());
  if (want.length !== mac.length || !crypto.timingSafeEqual(Buffer.from(want), Buffer.from(mac))) return null;
  try { return JSON.parse(Buffer.from(body, 'base64url').toString('utf8')); } catch (e) { return null; }
}
function safeBranch(b){
  b = String(b || '').trim();
  if (!b) return '';
  if (b.length > 100 || !/^[A-Za-z0-9._/-]+$/.test(b) || /(^|\/)\.|\.\.|\/\/|\/$|^\/|\.lock$|^-/.test(b)) { const e = new Error('Invalid branch name: ' + b); e.status = 400; throw e; }
  return b;
}
// Check and normalise a publish request body (used by both preview and publish, so they agree exactly).
function readRequest(b){
  const repository = String(b.repository || '').trim();
  if (!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(repository) || /\/\.+$/.test(repository)) { const e = new Error('Invalid repository name.'); e.status = 400; throw e; }
  const folder = safePath(b.folder);
  const names = Object.keys(b.files || {});
  if (!names.length || names.length > 80) { const e = new Error('Nothing to publish, or too many files.'); e.status = 400; throw e; }
  let total = 0;
  const files = names.map(n => {
    const content = String(b.files[n] ?? ''); total += Buffer.byteLength(content, 'utf8');
    const found = strongSecret(content); if (found){ const e = new Error(`Remove the ${found} in ${n} before publishing.`); e.status = 400; throw e; }
    return { name: n, path: safePath(folder + '/' + safePath(n)), content };
  });
  if (total > 2000000) { const e = new Error('These files are too large to publish from the browser.'); e.status = 413; throw e; }
  if (!files.some(f => /\/README\.md$/.test(f.path))) { const e = new Error('The README is missing.'); e.status = 400; throw e; }
  return { repository, folder, files, branch: safeBranch(b.branch) };
}
module.exports = { API_BASE, WEB_BASE, gitBlobSha, filesDigest, signReview, readReview, safeBranch, readRequest, COOKIE, STATE_COOKIE, SESSION_AGE, loadConfig, saveConfig, cfg, configured, siteUrl, encrypt, decrypt, cookies, cookie, json, redirect, header, csrfOk, gh, tokenRequest, sessionFrom, session, strongSecret, safePath };
