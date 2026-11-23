// Rechecks a saved "Published" record against GitHub: is the repository still reachable, does the branch still exist,
// and is the project folder still on it? Read-only. The page shows "Previously published · link unavailable" when
// the folder or branch is gone, and keeps the record with a separate note when GitHub cannot be checked.
const { loadConfig, json, gh, session, csrfOk, safeBranch, safePath } = require('./_shared');

exports.handler = async (event) => {
  if (event.httpMethod !== 'POST') return json(405, { error: 'Method not allowed.' });
  let set = [];
  try {
    if (!(await loadConfig(event))) return json(503, { error: 'GitHub publishing is not set up yet.' });
    const got = await session(event), s = got.session; set = got.cookie ? [got.cookie] : [];
    if (!s) return json(401, { error: 'Sign in to GitHub to check.' }, set);
    if (!csrfOk(event, s)) return json(403, { error: 'Security check failed. Reload the page and try again.' }, set);
    let b; try { b = JSON.parse(event.body || '{}'); } catch (e) { return json(400, { error: 'Invalid request.' }, set); }
    const repository = String(b.repository || '').trim();
    if (!/^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/.test(repository)) return json(400, { error: 'Invalid repository name.' }, set);
    const folder = safePath(b.folder), wanted = safeBranch(b.branch);
    const [o, r] = repository.split('/').map(encodeURIComponent);
    let info;
    try { info = await gh(`/repos/${o}/${r}`, s.accessToken); }
    catch (e) {
      if (e.status === 404 || e.status === 403) return json(200, { ok: true, state: 'noaccess', note: `GitHub did not show ${repository} to this account. It may be deleted, renamed, or the publishing app may have lost access.` }, set);
      throw e;
    }
    const branch = wanted || info.default_branch;
    let head;
    try { head = (await gh(`/repos/${o}/${r}/git/ref/heads/${encodeURIComponent(branch)}`, s.accessToken)).object.sha; }
    catch (e) {
      if (e.status === 404 || e.status === 409) return json(200, { ok: true, state: 'gone', reason: 'branch', branch, note: `The branch ${branch} is no longer in ${info.full_name}.` }, set);
      throw e;
    }
    try { await gh(`/repos/${o}/${r}/contents/${folder.split('/').map(encodeURIComponent).join('/')}?ref=${encodeURIComponent(head)}`, s.accessToken); }
    catch (e) {
      if (e.status === 404) return json(200, { ok: true, state: 'gone', reason: 'folder', branch, note: `${folder}/ is no longer on ${branch} in ${info.full_name}.` }, set);
      throw e;
    }
    const base = `https://github.com/${info.full_name}`;
    return json(200, { ok: true, state: 'ok', branch, head, repository: info.full_name,
      folderUrl: `${base}/tree/${encodeURIComponent(branch)}/${folder.split('/').map(encodeURIComponent).join('/')}`, repoUrl: base }, set);
  } catch (e) {
    return json(e.status && e.status < 500 ? e.status : 502, { error: e.message || 'Could not check GitHub.' }, set);
  }
};
