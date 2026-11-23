# Browser regression tests

These run the real site in headless Chromium (Playwright) against a local HTTPS host that also runs the
Netlify functions and a mock of the GitHub API, so no real repository is ever written to.

```
cd tests
openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 30 -subj "/CN=localhost"
node server.js .. 8820 &          # serves the site at https://localhost:8820
node rt.js                         # Python + SQL in worker and compatibility mode, startup failure handling
node store.js                      # two-tab saves, migration, interrupted migration, restore with a stale tab
node pub.js                        # GitHub review screen, cancel, publish, update, moved branch, test branch, root CI
                                   #   workflow, missing Workflows permission, recheck: folder removed, branch renamed, access lost
node smoke.js                      # one model solution per phase + every phase project (compatibility mode)
node lay.js                        # 18 screens x 7 widths x 2 themes: no page overflow, sidebar beside content on desktop,
                                   #   Course contents on mobile, theme switch on screen, review panel fits, duplicate ids
node v29.js                        # quiz shuffle/grading, Review, Study log, Playground undo, search paging and Back,
                                   #   backup preview/errors/restore/undo, .ps1 download, project counts, local ZIP = export,
                                   #   breadcrumb, phase navigation, Continue card, theme kept across pages, checker messages
node studylog.js                   # two tabs finish different lessons from an empty day: both completions and log entries survive
node v31.js ../path/to/v30/index.html  # sidebar Projects/Review, same destinations as v30
node v30.js                        # rewritten lessons: live output equals the shown panel, SQL row tables, chart, question
                                   #   levels and Optional practice, old drafts kept, every question in the 6 lessons via the buttons,
                                   #   new-here notes, Playground bare expression, ax.hist without its tuple
for i in 0 1 2 3; do node sweep.js $i 4 > sweep-$i.jsonl & done   # every exercise, inline question, project, example, snippet
```

Test switches the page understands (they do nothing unless a test sets them):
`window.__PY_MODE__` = "main" or "worker", `window.__STORE_TEST__` = { abortMigration, abortNextWrite, onOps }.

The mock GitHub (server.js) also has test endpoints: `/__test/rmpath`, `/__test/rename`, `/__test/revoke` and
`/__test/noworkflow?on=1` (refuses new workflow files the way GitHub does without the Workflows permission).

`node ../scripts/export-local-projects.js ../index.html OUT [ids...]` writes the 10 local projects exactly as their ZIPs contain them.

Offline copy: `python ../scripts/make-bundle.py OUT`, unzip `OUT/fde-study-offline.zip` into an empty folder, run
`sh start.sh` inside it, then `node bundle.js http://localhost:8765/ /path/to/fde-study-offline` (blocks every
request that leaves localhost, and checks the file:// behaviour).
