# Browser regression tests

These run the real site in headless Chromium (Playwright) against a local HTTPS host that also runs the
Netlify functions and a mock of the GitHub API, so no real repository is ever written to.

```
cd tests
openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 30 -subj "/CN=localhost"
node server.js .. 8820 &          # serves the site at https://localhost:8820
node rt.js                         # Python + SQL in worker and compatibility mode, startup failure handling
node store.js                      # two-tab saves, migration, interrupted migration, restore with a stale tab
node pub.js                        # GitHub review screen, cancel, publish, update, moved branch, test branch
node smoke.js                      # one model solution per phase + every phase project (compatibility mode)
node lay.js                        # no page overflow / review panel fits, 7 widths, both themes, duplicate ids
for i in 0 1 2 3; do node sweep.js $i 4 > sweep-$i.jsonl & done   # every exercise, inline question, project, example, snippet
```

Test switches the page understands (they do nothing unless a test sets them):
`window.__PY_MODE__` = "main" or "worker", `window.__STORE_TEST__` = { abortMigration, abortNextWrite, onOps }.
