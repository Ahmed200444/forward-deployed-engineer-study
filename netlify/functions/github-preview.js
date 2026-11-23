// Review step: says exactly where a publish would go and what it would change, without writing anything.
// The page shows this to the learner; only the signed token it returns lets github-publish write.
const { loadConfig, json, gh, session, csrfOk, readRequest, gitBlobSha, filesDigest, signReview } = require('./_shared');
const REVIEW_AGE_MS = 15 * 60 * 1000;

async function headOf(o, r, branch, token){
  try { const ref = await gh(`/repos/${o}/${r}/git/ref/heads/${encodeURIComponent(branch)}`, token); return ref.object.sha; }
  catch (e) { if (e.status === 404 || e.status === 409) return null; throw e; }
}
async function existing(o, r, head, folder, extra, token){
  // Files already in the folder on that branch (plus any requested root files), as path -> blob sha.
  const out = {}, rootHave = {};
  if (!head) return { files: out, root: rootHave, truncated: false };
  const commit = await gh(`/repos/${o}/${r}/git/commits/${head}`, token);
  const tree = await gh(`/repos/${o}/${r}/git/trees/${commit.tree.sha}?recursive=1`, token);
  for (const t of tree.tree || []) if (t.type === 'blob'){
    if (t.path.startsWith(folder + '/')) out[t.path] = t.sha;
    else if (extra.includes(t.path)) rootHave[t.path] = t.sha;
  }
  return { files: out, root: rootHave, truncated: !!tree.truncated };
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
    const req = readRequest(b);
    const [o, r] = req.repository.split('/').map(encodeURIComponent);
    const [user, info] = await Promise.all([gh('/user', s.accessToken), gh(`/repos/${o}/${r}`, s.accessToken)]);
    if (info.permissions && !info.permissions.push) return json(403, { error: `You can't write to ${req.repository}.` }, set);
    const defaultBranch = info.default_branch || 'main';
    const branch = req.branch || defaultBranch;
    const defaultHead = await headOf(o, r, defaultBranch, s.accessToken);
    const head = branch === defaultBranch ? defaultHead : await headOf(o, r, branch, s.accessToken);
    const empty = !defaultHead;
    if (empty && branch !== defaultBranch) return json(400, { error: `${info.full_name} is empty. Publish to ${defaultBranch} first, or add a README on github.com.` }, set);
    const have = await existing(o, r, head, req.folder, req.files.filter(f => f.root).map(f => f.path), s.accessToken);
    const all = Object.assign({}, have.files, have.root);
    const files = req.files.map(f => ({ path: f.path, name: f.name, root: !!f.root, bytes: Buffer.byteLength(f.content, 'utf8'),
      action: !(f.path in all) ? 'add' : all[f.path] === gitBlobSha(f.content) ? 'unchanged' : 'replace' }));
    const others = Object.keys(have.files).filter(p => !files.some(f => f.path === p)).sort();
    const review = { v: 1, login: user.login, repository: info.full_name, branch, head: head || null, base: head ? null : defaultHead || null,
      folder: req.folder, digest: filesDigest(req.files), exp: Date.now() + REVIEW_AGE_MS };
    return json(200, { ok: true, account: user.login, repository: info.full_name, private: !!info.private,
      visibility: info.visibility || (info.private ? 'private' : 'public'), defaultBranch, branch, branchExists: !!head, empty,
      head: head || null, folder: req.folder, folderExists: Object.keys(have.files).length > 0, treeTruncated: have.truncated,
      files, others, changes: files.filter(f => f.action !== 'unchanged').length, token: signReview(review),
      repoUrl: `https://github.com/${info.full_name}` }, set);
  } catch (e) {
    const status = e.status === 404 ? 404 : e.status || 500;
    const msg = e.status === 404 ? 'Repository not found, or the publishing app has no access to it.' : e.message || 'Could not check the destination.';
    return json(status, { error: msg }, set);
  }
};
