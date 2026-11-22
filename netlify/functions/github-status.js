// Tells the page whether publishing is set up, who is signed in, and which repositories the app can write to.
const { loadConfig, configured, json, gh, session } = require('./_shared');
exports.handler = async (event) => {
  const c = await loadConfig(event);
  const slug = c && c.slug || '';
  const installUrl = slug ? `https://github.com/apps/${encodeURIComponent(slug)}/installations/new` : null;
  if (!configured()) return json(200, { configured: false });
  try {
    const got = await session(event), s = got.session, set = got.cookie ? [got.cookie] : [];
    if (!s) return json(200, { configured: true, connected: false, installUrl }, set);
    const user = await gh('/user', s.accessToken);
    const ins = await gh('/user/installations?per_page=100', s.accessToken);
    const repos = [];
    for (const inst of (ins.installations || [])){
      try {
        const r = await gh(`/user/installations/${inst.id}/repositories?per_page=100`, s.accessToken);
        for (const repo of (r.repositories || [])) if (repo.permissions && repo.permissions.push) repos.push({ full_name: repo.full_name, private: repo.private, default_branch: repo.default_branch });
      } catch (e) {}
    }
    repos.sort((a, b) => a.full_name.localeCompare(b.full_name));
    return json(200, { configured: true, connected: true, user: { login: user.login }, repositories: repos, installUrl, csrf: s.csrf }, set);
  } catch (e) {
    if (e.status === 401) return json(200, { configured: true, connected: false, installUrl });
    return json(e.status || 500, { configured: true, error: e.message });
  }
};
