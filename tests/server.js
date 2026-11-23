// Local test host: serves the site over HTTPS, runs the Netlify functions, and mocks GitHub (no real GitHub calls).
const https = require('https'), fs = require('fs'), path = require('path'), crypto = require('crypto'), url = require('url');
const ROOT = process.argv[2] || require('path').join(__dirname, '..'), PORT = +(process.argv[3] || 8820);
const BASE = `https://localhost:${PORT}`;
Object.assign(process.env, { GITHUB_CLIENT_ID: 'cid', GITHUB_CLIENT_SECRET: 'csecret', SESSION_SECRET: 'test-session-secret', GITHUB_APP_SLUG: 'mock-app',
  SITE_URL: BASE, GITHUB_API_BASE: BASE + '/gh-api', GITHUB_WEB_BASE: BASE + '/gh-web', NODE_TLS_REJECT_UNAUTHORIZED: '0' });
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.json': 'application/json', '.wasm': 'application/wasm', '.zip': 'application/zip', '.whl': 'application/zip', '.txt': 'text/plain' };
const missing = new Set();   // tests can hide files: POST /__test/hide {path}
// ---- mock GitHub state ----
let G;
function sha(x){ return crypto.createHash('sha1').update(String(x) + Math.random()).digest('hex'); }
function blob(c){ const b = Buffer.from(c, 'utf8'); return crypto.createHash('sha1').update(`blob ${b.length}\0`).update(b).digest('hex'); }
function resetGH(){
  G = { log: [], repos: {} };
  for (const [name, priv, files] of [['Ahmed200444/ai-engineer-portfolio', false, { 'README.md': '# Portfolio\n' }], ['Ahmed200444/fde-publish-test', true, { 'README.md': '# test\n' }], ['Ahmed200444/empty-test', true, null]]){
    const r = { full_name: name, private: priv, default_branch: 'main', branches: {}, commits: {}, trees: {} };
    if (files){ const t = sha('t'); r.trees[t] = Object.fromEntries(Object.entries(files).map(([p, c]) => [p, { sha: blob(c), content: c }])); const c = sha('c'); r.commits[c] = { tree: t, parents: [], message: 'init' }; r.branches.main = c; }
    G.repos[name.toLowerCase()] = r;
  }
}
resetGH();
function ghApi(req, body, p, q){
  const send = (s, d) => ({ s, d });
  if (req.headers.authorization !== 'Bearer tok-1') return send(401, { message: 'Bad credentials' });
  if (p === '/user') return send(200, { login: 'Ahmed200444' });
  if (p === '/user/installations') return send(200, { installations: [{ id: 1 }] });
  if (p === '/user/installations/1/repositories') return send(200, { repositories: Object.values(G.repos).map(r => ({ full_name: r.full_name, private: r.private, default_branch: 'main', permissions: { push: true } })) });
  let m = p.match(/^\/repos\/([^/]+)\/([^/]+)(\/.*)?$/); if (!m) return send(404, { message: 'Not Found' });
  const r = G.repos[(decodeURIComponent(m[1]) + '/' + decodeURIComponent(m[2])).toLowerCase()]; if (!r) return send(404, { message: 'Not Found' });
  const rest = m[3] || '';
  if (!rest && req.method === 'GET') return send(200, { full_name: r.full_name, private: r.private, visibility: r.private ? 'private' : 'public', default_branch: r.default_branch, size: Object.keys(r.commits).length ? 10 : 0, permissions: { push: true } });
  if ((m = rest.match(/^\/git\/ref\/heads\/(.+)$/)) && req.method === 'GET'){
    if (!Object.keys(r.commits).length) return send(409, { message: 'Git Repository is empty.' });
    const b = decodeURIComponent(m[1]); return r.branches[b] ? send(200, { object: { sha: r.branches[b] } }) : send(404, { message: 'Not Found' }); }
  if ((m = rest.match(/^\/git\/commits\/(\w+)$/))) return r.commits[m[1]] ? send(200, { sha: m[1], tree: { sha: r.commits[m[1]].tree } }) : send(404, {});
  if ((m = rest.match(/^\/git\/trees\/(\w+)$/))) { const t = r.trees[m[1]]; return t ? send(200, { sha: m[1], truncated: false, tree: Object.entries(t).map(([path, v]) => ({ path, type: 'blob', sha: v.sha })) }) : send(404, {}); }
  if (rest === '/git/trees' && req.method === 'POST'){
    const base = { ...(r.trees[body.base_tree] || {}) }; for (const f of body.tree) base[f.path] = { sha: blob(f.content), content: f.content };
    const same = Object.entries(r.trees).find(([k, v]) => JSON.stringify(Object.entries(v).map(([a, b]) => [a, b.sha]).sort()) === JSON.stringify(Object.entries(base).map(([a, b]) => [a, b.sha]).sort()));
    if (same) return send(201, { sha: same[0] });
    const t = sha('t'); r.trees[t] = base; return send(201, { sha: t }); }
  if (rest === '/git/commits' && req.method === 'POST'){ const c = sha('c'); r.commits[c] = { tree: body.tree, parents: body.parents, message: body.message }; G.log.push({ op: 'commit', repo: r.full_name, sha: c, message: body.message }); return send(201, { sha: c }); }
  if ((m = rest.match(/^\/contents\/(.+)$/)) && req.method === 'GET'){
    const fp = m[1].split('/').map(decodeURIComponent).join('/'), c = r.commits[q.ref] || r.commits[r.branches[q.ref]];
    if (!c) return send(404, { message: 'No commit found for the ref' });
    const t = r.trees[c.tree]; return Object.keys(t).some(k => k === fp || k.startsWith(fp + '/')) ? send(200, [{ path: fp }]) : send(404, { message: 'Not Found' }); }
  if ((m = rest.match(/^\/git\/refs\/heads\/(.+)$/)) && req.method === 'PATCH'){ const b = decodeURIComponent(m[1]); if (G.noWorkflow && Object.keys(r.trees[r.commits[body.sha].tree]).some(k => k.startsWith('.github/workflows/') && !(r.trees[r.commits[r.branches[b]].tree][k]))) return send(422, { message: 'refusing to allow a GitHub App to create or update workflow `.github/workflows/x.yml` without `workflows` permission' }); if (!r.commits[body.sha] || r.commits[body.sha].parents[0] !== r.branches[b]) return send(422, { message: 'Update is not a fast forward' }); r.branches[b] = body.sha; G.log.push({ op: 'update-ref', repo: r.full_name, branch: b, sha: body.sha }); return send(200, {}); }
  if (rest === '/git/refs' && req.method === 'POST'){ const b = body.ref.replace('refs/heads/', ''); if (r.branches[b]) return send(422, { message: 'Reference already exists' }); r.branches[b] = body.sha; G.log.push({ op: 'create-ref', repo: r.full_name, branch: b }); return send(201, {}); }
  if ((m = rest.match(/^\/contents\/(.+)$/)) && req.method === 'PUT'){
    const fp = m[1].split('/').map(decodeURIComponent).join('/'), b = body.branch, head = r.branches[b], tree = head ? { ...r.trees[r.commits[head].tree] } : {};
    const content = Buffer.from(body.content, 'base64').toString('utf8'); tree[fp] = { sha: blob(content), content };
    const t = sha('t'); r.trees[t] = tree; const c = sha('c'); r.commits[c] = { tree: t, parents: head ? [head] : [], message: body.message }; r.branches[b] = c; G.log.push({ op: 'commit', repo: r.full_name, sha: c, via: 'contents' });
    return send(201, { commit: { sha: c } }); }
  return send(404, { message: 'Not Found: ' + rest });
}
async function runFunction(name, req, body, q){
  const file = path.join(ROOT, 'netlify/functions', name + '.js'); if (!fs.existsSync(file)) return null;
  delete require.cache[require.resolve(file)]; Object.keys(require.cache).filter(k => k.includes('_shared')).forEach(k => delete require.cache[k]);
  const fn = require(file);
  const headers = {}; for (const [k, v] of Object.entries(req.headers)) headers[k.toLowerCase()] = v;
  return fn.handler({ httpMethod: req.method, headers, queryStringParameters: q, body });
}
https.createServer({ key: fs.readFileSync(process.env.TLS_KEY || __dirname + '/key.pem'), cert: fs.readFileSync(process.env.TLS_CERT || __dirname + '/cert.pem') }, async (req, res) => {
  const u = url.parse(req.url, true); let raw = ''; for await (const ch of req) raw += ch;
  const json = (s, d, h = {}) => { res.writeHead(s, { 'Content-Type': 'application/json', ...h }); res.end(JSON.stringify(d)); };
  try {
    if (u.pathname === '/__test/gh') return json(200, G);
    if (u.pathname === '/__test/reset'){ resetGH(); missing.clear(); return json(200, { ok: true }); }
    if (u.pathname === '/__test/hide'){ missing.add(u.query.path); return json(200, { ok: true }); }
    if (u.pathname === '/__test/unhide'){ missing.delete(u.query.path); return json(200, { ok: true }); }
    if (u.pathname === '/__test/move'){ const r = G.repos[u.query.repo.toLowerCase()]; const c = sha('c'); r.commits[c] = { tree: r.commits[r.branches.main].tree, parents: [r.branches.main], message: 'external' }; r.branches.main = c; return json(200, { sha: c }); }
    if (u.pathname === '/__test/noworkflow'){ G.noWorkflow = u.query.on === '1'; return json(200, { ok: true }); }
    if (u.pathname === '/__test/rmpath'){ const r = G.repos[u.query.repo.toLowerCase()], b = u.query.branch || 'main', t0 = r.trees[r.commits[r.branches[b]].tree];
      const t = Object.fromEntries(Object.entries(t0).filter(([k]) => !(k === u.query.path || k.startsWith(u.query.path + '/')))); const tid = sha('t'); r.trees[tid] = t;
      const c = sha('c'); r.commits[c] = { tree: tid, parents: [r.branches[b]], message: 'remove' }; r.branches[b] = c; return json(200, { sha: c }); }
    if (u.pathname === '/__test/rename'){ const r = G.repos[u.query.repo.toLowerCase()]; r.branches[u.query.to] = r.branches[u.query.from]; delete r.branches[u.query.from]; return json(200, { ok: true }); }
    if (u.pathname === '/__test/revoke'){ delete G.repos[u.query.repo.toLowerCase()]; return json(200, { ok: true }); }
    if (u.pathname.startsWith('/gh-web/login/oauth/authorize')){ res.writeHead(302, { Location: u.query.redirect_uri + '?code=code-1&state=' + u.query.state }); return res.end(); }
    if (u.pathname === '/gh-web/login/oauth/access_token') return json(200, { access_token: 'tok-1', expires_in: 28800, refresh_token: 'ref-1' });
    if (u.pathname.startsWith('/gh-api/')){ const r = ghApi(req, raw ? JSON.parse(raw) : {}, u.pathname.slice(7), u.query); return json(r.s, r.d); }
    let m = u.pathname.match(/^\/(?:api\/github|\.netlify\/functions\/github)[/-]([a-z]+)$/);
    if (m){
      const out = await runFunction('github-' + m[1], req, raw, u.query);
      if (!out) return json(404, { error: 'no function' });
      const h = { ...(out.headers || {}) }; if (out.multiValueHeaders && out.multiValueHeaders['Set-Cookie']) h['Set-Cookie'] = out.multiValueHeaders['Set-Cookie'];
      res.writeHead(out.statusCode, h); return res.end(out.body || '');
    }
    let p = decodeURIComponent(u.pathname); if (p === '/') p = '/index.html';
    const f = path.join(ROOT, p);
    if (!f.startsWith(ROOT) || missing.has(p) || !fs.existsSync(f) || fs.statSync(f).isDirectory()){ res.writeHead(404, { 'Content-Type': 'text/html' }); return res.end('<!doctype html><h1>Page not found</h1>'); }
    res.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' }); fs.createReadStream(f).pipe(res);
  } catch (e) { console.error(e); json(500, { error: String(e) }); }
}).listen(PORT, () => console.log('listening', BASE));
