// Publishes one item (code, data, tests and the generated README) to a folder in one commit.
// It only writes what the learner confirmed on the review screen: the request must carry the token from
// github-preview for the same account, repository, branch, folder and files, and the branch must not have
// moved since the review. Uses the Git Data API so every file lands in a single atomic commit; an empty
// repository (no branch yet) gets its README through the Contents API first, then the rest in one commit.
const { loadConfig, json, gh, session, csrfOk, readRequest, filesDigest, readReview } = require('./_shared');

class Changed extends Error { constructor(m){ super(m); this.status = 409; this.changed = true; } }

async function commitTree(o, r, branch, expectedHead, files, message, token){
  const ref = await gh(`/repos/${o}/${r}/git/ref/heads/${encodeURIComponent(branch)}`, token);
  const parent = ref.object.sha;
  if (parent !== expectedHead) throw new Changed(`${branch} changed on GitHub after you reviewed it. Review the publish again.`);
  const head = await gh(`/repos/${o}/${r}/git/commits/${parent}`, token);
  const tree = await gh(`/repos/${o}/${r}/git/trees`, token, { method: 'POST', body: JSON.stringify({
    base_tree: head.tree.sha, tree: files.map(f => ({ path: f.path, mode: '100644', type: 'blob', content: f.content })) }) });
  if (tree.sha === head.tree.sha) return { unchanged: true, sha: parent };
  const commit = await gh(`/repos/${o}/${r}/git/commits`, token, { method: 'POST', body: JSON.stringify({ message, tree: tree.sha, parents: [parent] }) });
  try {
    await gh(`/repos/${o}/${r}/git/refs/heads/${encodeURIComponent(branch)}`, token, { method: 'PATCH', body: JSON.stringify({ sha: commit.sha, force: false }) });
  } catch (e) { if (e.status === 422 && !/workflow/i.test(e.message || '')) throw new Changed(`${branch} changed on GitHub while publishing. Nothing was written. Review the publish again.`); throw e; }
  return { unchanged: false, sha: commit.sha, commits: 1 };
}
async function contentsFallback(o, r, branch, files, message, token){
  // v31.2: an empty repository has no commit for the Git Data API to build on, so the first file (the README)
  // creates the branch through the Contents API and every other file follows in one more commit: two commits, not one per file.
  const first = files.find(f => /(^|\/)README\.md$/.test(f.path)) || files[0];
  const path = first.path.split('/').map(encodeURIComponent).join('/');
  const saved = await gh(`/repos/${o}/${r}/contents/${path}`, token, { method: 'PUT', body: JSON.stringify({ message, content: Buffer.from(first.content, 'utf8').toString('base64'), branch }) });
  const rest = files.filter(f => f !== first);
  const sha = saved.commit && saved.commit.sha;
  if (!rest.length) return { unchanged: false, sha, commits: 1 };
  const res = await commitTree(o, r, branch, sha, rest, message, token);
  return { unchanged: false, sha: res.sha, commits: res.unchanged ? 1 : 2 };
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
    const rv = readReview(b.review);
    if (b.confirmed !== true || !rv) return json(428, { error: 'Review the destination and press Publish now to confirm. Nothing was written.', review: true }, set);
    if (rv.exp < Date.now()) return json(409, { error: 'That review is more than 15 minutes old. Review the publish again.', changed: true }, set);
    if (rv.repository.toLowerCase() !== req.repository.toLowerCase() || rv.folder !== req.folder || (req.branch || rv.branch) !== rv.branch || rv.digest !== filesDigest(req.files))
      return json(409, { error: 'The files or destination changed after the review. Review the publish again. Nothing was written.', changed: true }, set);
    const user = await gh('/user', s.accessToken);
    if (user.login !== rv.login) return json(409, { error: 'You are signed in to a different GitHub account than the one you reviewed. Review again.', changed: true }, set);
    const message = String(b.message || `Publish ${req.folder}`).replace(/[\r\n]+/g, ' ').slice(0, 200);
    const [o, r] = rv.repository.split('/').map(encodeURIComponent);
    const info = await gh(`/repos/${o}/${r}`, s.accessToken);
    if (info.permissions && !info.permissions.push) return json(403, { error: `You can't write to ${rv.repository}.` }, set);
    const branch = rv.branch;
    let res;
    if (rv.head) res = await commitTree(o, r, branch, rv.head, req.files, message, s.accessToken);
    else if (rv.base){
      // New branch the learner chose on the review screen: start it from the default branch they saw.
      try { await gh(`/repos/${o}/${r}/git/refs`, s.accessToken, { method: 'POST', body: JSON.stringify({ ref: `refs/heads/${branch}`, sha: rv.base }) }); }
      catch (e) { if (e.status === 422) throw new Changed(`A branch called ${branch} appeared after you reviewed. Review again.`); throw e; }
      res = await commitTree(o, r, branch, rv.base, req.files, message, s.accessToken);
    } else {
      // Empty repository: the README creates the branch, then the other files land in one commit.
      let now = null; try { now = await gh(`/repos/${o}/${r}/git/ref/heads/${encodeURIComponent(branch)}`, s.accessToken); } catch (e) { if (e.status !== 404 && e.status !== 409) throw e; }
      if (now) throw new Changed(`${rv.repository} is no longer empty. Review the publish again.`);
      res = await contentsFallback(o, r, branch, req.files, message, s.accessToken);
    }
    const base = `https://github.com/${info.full_name}`;
    return json(200, { ok: true, unchanged: res.unchanged, files: req.files.length, repository: info.full_name, branch, folder: req.folder, sha: res.sha || null, commits: res.unchanged ? 0 : res.commits || 1,
      folderUrl: `${base}/tree/${encodeURIComponent(branch)}/${req.folder.split('/').map(encodeURIComponent).join('/')}`,
      commitUrl: res.sha ? `${base}/commit/${res.sha}` : null, repoUrl: base }, set);
  } catch (e) {
    // GitHub refuses workflow files from an app without the Workflows permission; say so plainly.
    if (!e.changed && /workflow/i.test(e.message || '') && (e.status === 403 || e.status === 404 || e.status === 422))
      return json(403, { error: 'GitHub refused the CI workflow file: the publishing app needs the Workflows (read and write) permission. Nothing was written. Untick "Include the CI workflow" to publish without it, or give the app that permission.', workflowPermission: true }, set);
    const status = e.status === 404 ? 404 : e.status || 500;
    const msg = e.status === 404 ? 'Repository not found, or the publishing app has no access to it.' : e.message || 'Publishing failed.';
    return json(status, { error: msg, changed: !!e.changed }, set);
  }
};
