// Shared helpers for the GitHub publishing functions.
// Pattern taken from the CS & AI Mastery site: GitHub App user sign-in, an AES-256-GCM
// encrypted HttpOnly cookie for the session, and secrets only in Netlify environment variables.
const crypto = require('crypto');
const COOKIE = 'fde_gh_session';
const STATE_COOKIE = 'fde_gh_state';
const API_VERSION = '2022-11-28';
const SESSION_AGE = 60 * 60 * 24 * 180;

function env(name){ const v = process.env[name]; if (!v) throw new Error(`Missing environment variable: ${name}`); return v; }
function configured(){ return !!(process.env.GITHUB_CLIENT_ID && process.env.GITHUB_CLIENT_SECRET && process.env.SESSION_SECRET); }
function siteUrl(){ return (process.env.SITE_URL || process.env.URL || '').replace(/\/$/, ''); }
function key(){ return crypto.createHash('sha256').update(env('SESSION_SECRET')).digest(); }
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
  const r = await fetch(`https://api.github.com${path}`, { ...options, headers: {
    Accept: 'application/vnd.github+json', Authorization: `Bearer ${token}`, 'X-GitHub-Api-Version': API_VERSION,
    'User-Agent': 'FDE-Study-Publisher', ...(options.body ? { 'Content-Type': 'application/json' } : {}), ...(options.headers || {}) } });
  const text = await r.text(); let data = {}; try { data = text ? JSON.parse(text) : {}; } catch (e) {}
  if (!r.ok){ const err = new Error(data.message || `GitHub request failed (${r.status})`); err.status = r.status; throw err; }
  return data;
}
async function tokenRequest(params){
  const body = new URLSearchParams({ client_id: env('GITHUB_CLIENT_ID'), client_secret: env('GITHUB_CLIENT_SECRET'), ...params });
  const r = await fetch('https://github.com/login/oauth/access_token', { method: 'POST', headers: { Accept: 'application/json', 'Content-Type': 'application/x-www-form-urlencoded' }, body });
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
module.exports = { COOKIE, STATE_COOKIE, SESSION_AGE, env, configured, siteUrl, encrypt, decrypt, cookies, cookie, json, redirect, header, csrfOk, gh, tokenRequest, sessionFrom, session, strongSecret, safePath };
