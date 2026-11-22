// Publishes one item (code, data, tests and the generated README) to a folder in one commit.
// Uses the Git Data API so every file lands in a single atomic commit; an empty repository
// (no branch yet) falls back to the Contents API, which creates the first commit.
const { loadConfig, json, gh, session, csrfOk, strongSecret, safePath } = require('./_shared');
const MAX_FILES = 80, MAX_BYTES = 2000000;

async function commitTree(o, r, branch, files, message, token){
  const ref = await gh(`/repos/${o}/${r}/git/ref/heads/${encodeURIComponent(branch)}`, token);
  const parent = ref.object.sha;
  const head = await gh(`/repos/${o}/${r}/git/commits/${parent}`, token);
  const tree = await gh(`/repos/${o}/${r}/git/trees`, token, { method: 'POST', body: JSON.stringify({
    base_tree: head.tree.sha, tree: files.map(f => ({ path: f.path, mode: '100644', type: 'blob', content: f.content })) }) });
  if (tree.sha === head.tree.sha) return { unchanged: true, sha: parent };
  const commit = await gh(`/repos/${o}/${r}/git/commits`, token, { method: 'POST', body: JSON.stringify({ message, tree: tree.sha, parents: [parent] }) });
  await gh(`/repos/${o}/${r}/git/refs/heads/${encodeURIComponent(branch)}`, token, { method: 'PATCH', body: JSON.stringify({ sha: commit.sha, force: false }) });
  return { unchanged: false, sha: commit.sha };
}
async function contentsFallback(o, r, branch, files, message, token){
  let sha = null;
  for (const f of files){
    const path = f.path.split('/').map(encodeURIComponent).join('/');
    let old = null; try { old = await gh(`/repos/${o}/${r}/contents/${path}?ref=${encodeURIComponent(branch)}`, token); } catch (e) { if (e.status !== 404) throw e; }
    const body = { message, content: Buffer.from(f.content, 'utf8').toString('base64'), branch }; if (old && old.sha) body.sha = old.sha;
    const saved = await gh(`/repos/${o}/${r}/contents/${path}`, token, { method: 'PUT', body: JSON.stringify(body) });
    sha = saved.commit && saved.commit.sha;
  }
  return { unchanged: false, sha, multiple: files.length > 1 };
}

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') return json(405, { error: 'Method not allowed.' });
  let set = [];
  try {
    if (!(await loadConfig(event))) return json(503, { error: 'GitHub publishing is not set up yet.' });
    const got = await session(event), s = got.session; set = got.cookie ? [got.cookie] : [];
    if (!s) return json(401, { error: 'Sign in to GitHub first.' }, set);
    if (!csrfOk(event, s)) return json(403, { error: 'Security check failed. Reload the page and try again.' }, set);
    let b; try { b = JSON.parse(event.body || '{}'); } catch (e) { return json(400, { error: 'Invalid request.' }, set); }
    const repository = String(b.repository || '').trim();
    if (!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(repository) || /\/\.+$/.test(repository)) return json(400, { error: 'Invalid repository name.' }, set);
    const folder = safePath(b.folder);
    const names = Object.keys(b.files || {});
    if (!names.length || names.length > MAX_FILES) return json(400, { error: 'Nothing to publish, or too many files.' }, set);
    let total = 0;
    const files = names.map(n => {
      const content = String(b.files[n] ?? ''); total += Buffer.byteLength(content, 'utf8');
      const found = strongSecret(content); if (found){ const e = new Error(`Remove the ${found} in ${n} before publishing.`); e.status = 400; throw e; }
      return { path: safePath(folder + '/' + safePath(n)), content };
    });
    if (total > MAX_BYTES) return json(413, { error: 'These files are too large to publish from the browser.' }, set);
    if (!files.some(f => /\/README\.md$/.test(f.path))) return json(400, { error: 'The README is missing.' }, set);
    const message = String(b.message || `Publish ${folder}`).replace(/[\r\n]+/g, ' ').slice(0, 200);
    const [o, r] = repository.split('/').map(encodeURIComponent);
    const info = await gh(`/repos/${o}/${r}`, s.accessToken);
    if (info.permissions && !info.permissions.push) return json(403, { error: `You can't write to ${repository}.` }, set);
    const branch = info.default_branch || 'main';
    let res;
    try {
      res = await commitTree(o, r, branch, files, message, s.accessToken);
    } catch (e) {
      if (e.status === 409 || (e.status === 404 && info.size === 0)) res = await contentsFallback(o, r, branch, files, message, s.accessToken);
      else if (e.status === 422) res = await commitTree(o, r, branch, files, message, s.accessToken); // branch moved; try once more
      else throw e;
    }
    const base = `https://github.com/${info.full_name}`;
    return json(200, { ok: true, unchanged: res.unchanged, files: files.length, repository: info.full_name, branch,
      folderUrl: `${base}/tree/${encodeURIComponent(branch)}/${folder.split('/').map(encodeURIComponent).join('/')}`,
      commitUrl: res.sha ? `${base}/commit/${res.sha}` : null, repoUrl: base }, set);
  } catch (e) {
    const status = e.status === 404 ? 404 : e.status || 500;
    const msg = e.status === 404 ? 'Repository not found, or the publishing app has no access to it.' : e.message || 'Publishing failed.';
    return json(status, { error: msg }, set);
  }
};
