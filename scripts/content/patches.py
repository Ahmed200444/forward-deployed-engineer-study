"""Code and CSS changes for v30. Each old string must occur exactly once in the v29 page."""

CSS = r"""
/* v30: teach before you ask */
.lesson-path .pq-level{margin:0 2px}
.pq-level{display:inline-block;margin-left:8px;padding:1px 8px;border-radius:99px;font-size:11px;font-weight:600;letter-spacing:.04em;text-transform:uppercase;vertical-align:middle;border:1px solid var(--border);background:var(--surface-2);color:var(--muted);white-space:nowrap}
.pq-level.guided{color:var(--good);border-color:var(--good);background:var(--good-soft)}
.pq-level.independent{color:var(--accent-text);border-color:var(--accent);background:var(--accent-soft)}
.pq-level.challenge{color:var(--warn);border-color:var(--warn);background:var(--warn-soft)}
.pq-before{margin:0 0 12px;padding:10px 14px;border:1px solid var(--border);border-left:3px solid var(--good);border-radius:0 8px 8px 0;background:var(--surface-2);min-width:0}
.pq-before p{margin:4px 0}
.pq-before pre{overflow-x:auto;max-width:100%}
.pq-prereq{font-size:14px;margin:0 0 10px;color:var(--muted)}
.pq-optional{margin:24px 0;border:1px solid var(--border);border-radius:var(--radius);background:var(--surface-2);padding:0 14px;min-width:0}
.pq-optional>summary{cursor:pointer;font-weight:600;padding:12px 2px;min-height:44px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.pq-optional>summary .meta{font-weight:400}
.pq-optional[open]>summary{border-bottom:1px solid var(--border);margin-bottom:6px}
.lesson-out{margin:8px 0 16px}
.lesson-out pre{max-height:none}
.lesson-out-err code{color:var(--bad)}
.lesson-out-fig{padding:10px;background:#fff}
.lesson-out-fig img,.lesson-out-fig svg{display:block;max-width:100%;height:auto}
table.trace caption,table.sql-rows caption{caption-side:top;text-align:left;font-size:13px;font-weight:600;color:var(--muted);padding:8px 12px 0}
table.sql-rows td.null{color:var(--muted);font-style:italic}
.lesson-out .table-wrap{margin:0;border:0;border-radius:0}
/* v31: opened from a folder */
.file-notice{display:none;margin:0 0 16px;padding:12px 14px;border:1px solid var(--warn);border-left-width:4px;border-radius:8px;background:var(--warn-soft);color:var(--text);font-size:14px;line-height:1.5}
html[data-file] .file-notice{display:block}
/* v31: worked examples in New here notes */
.pq-before code.pq-ex{display:block;white-space:pre;overflow-x:auto;max-width:100%;margin:6px 0 4px;padding:8px 10px;border:1px solid var(--border);border-radius:6px;background:var(--surface);font-size:13px;line-height:1.45}
.pq-before li{margin:6px 0;min-width:0}
"""

PATCHES = [
    # every pre in a rewritten lesson carries its own key, so blocks keep their saved edits when lessons are reordered
    ("  function lessonSnippets(l){\n",
     "  // v30: a block's key is lesson#N. Rewritten lessons tag each block with data-snip so old keys survive new blocks.\n"
     "  function preKey(l, pre, i){ return l.id + \"#\" + (pre.getAttribute(\"data-snip\") || i); }\n"
     "  function isLessonCode(pre){ return !pre.closest(\".rec-out, .lesson-out\"); }\n"
     "  function lessonSnippets(l){\n"),
    ("    return Array.prototype.map.call(d.querySelectorAll(\"pre\"), function(pre, i){\n      var key = l.id + \"#\" + i, spec = SNIP.blocks[key] || { mode: \"none\", why: \"\" };\n      var original = spec.code",
     "    return Array.prototype.filter.call(d.querySelectorAll(\"pre\"), isLessonCode).map(function(pre, i){\n      var key = preKey(l, pre, i), spec = SNIP.blocks[key] || { mode: \"none\", why: \"\" };\n      var original = spec.code"),
    ("    view.querySelectorAll(\"pre\").forEach(function(pre, i){\n      var key = l.id + \"#\" + i, spec = SNIP.blocks[key] || { mode: \"none\", why: \"\" };\n      if (spec.mode === \"none\"){ wireEditOnly(pre, key, spec); return; }",
     "    Array.prototype.filter.call(view.querySelectorAll(\"pre\"), isLessonCode).forEach(function(pre, i){\n      var key = preKey(l, pre, i), spec = SNIP.blocks[key] || { mode: \"none\", why: \"\" };\n      if (spec.mode === \"none\"){ wireEditOnly(pre, key, spec); return; }"),
    ("    Array.prototype.filter.call(view.querySelectorAll(\"pre\"), function(pre){ return !pre.closest(\".rec-out\"); }).forEach(function(pre, i){   // recorded-output panels are not lesson code\n      var items = LINE_NOTES[l.id + \"#\" + i];",
     "    Array.prototype.filter.call(view.querySelectorAll(\"pre\"), isLessonCode).forEach(function(pre, i){   // recorded-output panels are not lesson code\n      var items = LINE_NOTES[preKey(l, pre, i)];"),
    ("    Array.prototype.forEach.call(d.querySelectorAll(\"pre\"), function(pre, i){\n      if (pre.closest(\".rec-out\")) return;\n      var key = l.id + \"#\" + i, spec = SNIP.blocks[key] || WEX_EXTRA[key];",
     "    Array.prototype.filter.call(d.querySelectorAll(\"pre\"), isLessonCode).forEach(function(pre, i){\n      var key = preKey(l, pre, i), spec = SNIP.blocks[key] || WEX_EXTRA[key];"),

    # questions: level, a short "before you start" note, prerequisite links, and an Optional practice group
    ("      return { id: q.id, title: q.title, prompt: q.prompt, starter: q.starter, solution: q.solution, files: q.files || {}, setup: \"\", tests: q.tests, lang: \"py\", inline: true, after: q.after, hints: [], qhint: q.hint || \"\" };\n    });\n    if (!list.length) return [];\n    var heads = Array.prototype.filter.call(view.children, function(e){ return e.tagName === \"H2\"; });\n    var placed = [];\n    heads.forEach(function(h){\n      var mine = list.filter(function(q){ return q.after === h.textContent.trim(); });",
     "      return { id: q.id, title: q.title, prompt: q.prompt, starter: q.starter, solution: q.solution, files: q.files || {}, setup: \"\", tests: q.tests, lang: \"py\", inline: true, after: q.after, hints: [], qhint: q.hint || \"\",\n        level: q.level || \"\", optional: !!q.optional, before: q.before || \"\", prereq: q.prereq || \"\" };\n    });\n    if (!list.length) return [];\n    var heads = Array.prototype.filter.call(view.children, function(e){ return e.tagName === \"H2\"; });\n    var placed = [];\n    // v30: optional questions sit together in one closed group before Check yourself, so they never interrupt the core path\n    var extra = list.filter(function(q){ return q.optional; });\n    list = list.filter(function(q){ return !q.optional; });\n    heads.forEach(function(h){\n      var mine = list.filter(function(q){ return q.after === h.textContent.trim(); });"),
    ("      if (next) next.before(holder); else view.appendChild(holder);\n    });\n",
     "      if (next) next.before(holder); else view.appendChild(holder);\n    });\n"
     "    if (extra.length){\n"
     "      var done = extra.filter(function(q){ return (state.qpass || {})[q.id]; }).length;\n"
     "      var grp = document.createElement(\"details\"); grp.className = \"pq-optional\";\n"
     "      if (extra.some(function(q){ return state.drafts[q.id] != null; })) grp.open = true;\n"
     "      grp.innerHTML = '<summary>Optional practice <span class=\"meta\">' + extra.length + ' more question' + (extra.length === 1 ? '' : 's') + (done ? ' · ' + done + ' passed' : '') +\n"
     "        '</span></summary><p class=\"meta\">Extra variations and challenges. Skip them if you are short of time; nothing else depends on them.</p>' +\n"
     "        '<div class=\"pq-inline\" data-ids=\"' + extra.map(function(q){ return q.id; }).join(\" \") + '\"></div>';\n"
     "      var check = heads.filter(function(h){ return h.textContent.trim() === \"Check yourself\"; })[0] || view.querySelector(\"[data-pq-host]\");\n"
     "      if (check) check.before(grp); else view.appendChild(grp);\n"
     "      list = list.concat(extra);\n"
     "    }\n"),
    ("    return '<div class=\"pq\" id=\"pq-' + n + '\"><h3 class=\"pq-h\">Question ' + n + ': ' + esc(ex.title) + (passMap(ex)[ex.id] ? ' <span class=\"done-badge\">✓ Passed</span>' : '') + '</h3>' +\n      '<div class=\"pq-prompt\">' + ex.prompt + '</div>' +",
     "    var LEVELS = { guided: \"Guided\", independent: \"Independent\", challenge: \"Challenge\" };\n"
     "    return '<div class=\"pq\" id=\"pq-' + n + '\"><h3 class=\"pq-h\">Question ' + n + ': ' + esc(ex.title) + (LEVELS[ex.level] ? ' <span class=\"pq-level ' + ex.level + '\">' + LEVELS[ex.level] + '</span>' : '') + (passMap(ex)[ex.id] ? ' <span class=\"done-badge\">✓ Passed</span>' : '') + '</h3>' +\n"
     "      ((ex.before || EX_NEWHERE[ex.id]) ? '<div class=\"pq-before\">' + (ex.before || EX_NEWHERE[ex.id]) + '</div>' : '') +\n"
     "      (ex.prereq ? '<p class=\"pq-prereq\">Taught in: ' + ex.prereq + '</p>' : '') +\n"
     "      '<div class=\"pq-prompt\">' + ex.prompt + '</div>' +"),

    # exercises: the same "new here" note on the exercise page
    ("view.innerHTML = head + '<div class=\"ex-split\"><div class=\"ex-left\"><div class=\"ex-task\">' + ex.prompt + '</div>' +",
     "view.innerHTML = head + '<div class=\"ex-split\"><div class=\"ex-left\"><div class=\"ex-task\">' + (EX_NEWHERE[ex.id] ? '<div class=\"pq-before\">' + EX_NEWHERE[ex.id] + '</div>' : '') + ex.prompt + '</div>' +"),
    ("  var SOL_NOTES = (function(){",
     "  // v30: short notes for exercise features that no earlier lesson shows (see scripts/content/newhere.py)\n"
     "  var EX_NEWHERE = (function(){ var el = document.getElementById(\"ex-newhere\"); try { return el ? JSON.parse(el.textContent) : {}; } catch (e){ return {}; } })();\n"
     "  var SOL_NOTES = (function(){"),
    # Playground: a bare expression on its own line shows its value, as in lesson blocks (a bare DataFrame used to show nothing)
    ("runner.runSnippet(PLAY_SQL, ta.value, function(msg){ status.textContent = msg; }) : runner.run(null, ta.value, function(msg){ status.textContent = msg; });",
     "runner.runSnippet(PLAY_SQL, ta.value, function(msg){ status.textContent = msg; }) : runner.runSnippet(PLAY_PY, ta.value, function(msg){ status.textContent = msg; });"),
    ("  var PLAY_SQL = { mode: \"sql\", setup: \"from db import connect\\nconn = connect()\\n\", files: [\"requests.csv\", \"agencies.csv\", \"db.py\"] };",
     "  var PLAY_SQL = { mode: \"sql\", setup: \"from db import connect\\nconn = connect()\\n\", files: [\"requests.csv\", \"agencies.csv\", \"db.py\"] };\n"
     "  var PLAY_PY = { mode: \"py\", setup: \"\", files: [] };"),

    # a bare plotting call such as ax.hist(...) returns (counts, edges, bars): skip it like other plot objects, keep the chart
    ("    if isinstance(value, (list, tuple)) and value and all(type(v).__module__.startswith(\"matplotlib\") for v in value):\n        return\n    print(repr(value))",
     "    if isinstance(value, (list, tuple)) and value and any((type(v).__module__ or \"\").startswith(\"matplotlib\") for v in value):\n        return\n    print(repr(value))"),
    ("        if value is not None and not (type(value).__module__ or \"\").startswith(\"matplotlib\"):\\n            print(repr(value))\\n",
     "        plot = lambda v: (type(v).__module__ or \"\").startswith(\"matplotlib\")\\n"
     "        if value is not None and not plot(value) and not (isinstance(value, (list, tuple)) and value and any(plot(v) for v in value)):\\n"
     "            print(repr(value))\\n"),
    # v31: Python loads from py/ next to index.html, so the downloaded bundle works from any folder (the hosted site is at the root, so this is still /py/)
    ('<script>window.__PY_BASE__="/py/";</script>',
     '<script>window.__PY_BASE__="py/";if(location.protocol==="file:")document.documentElement.setAttribute("data-file","");</script>'),
    ('      <div class="view" id="view" tabindex="-1"></div>\n',
     '      <div class="file-notice" role="note"><strong>Opened as a file, so Python cannot run.</strong> Browsers block the Python runtime on pages opened straight from a folder. '
     'Close this tab and double-click <b>Start FDE Study</b> in the folder you extracted (on a Mac or Linux, run <code>start.sh</code>). '
     'Lessons still read fine here. Steps are in <code>HOW-TO-START.txt</code>.</div>\n'
     '      <div class="view" id="view" tabindex="-1"></div>\n'),
    ('  function checkPyAssets(){\n    if (pyAssetsChecked) return pyAssetsChecked;\n',
     '  function checkPyAssets(){\n    if (pyAssetsChecked) return pyAssetsChecked;\n'
     '    if (location.protocol === "file:"){\n'
     '      var fe = new Error("This page was opened straight from a file, and browsers do not let Python run that way. Close this tab and double-click Start FDE Study in the folder you extracted (on a Mac or Linux, run start.sh). Your code is still saved here");\n'
     '      fe.deploy = true; return Promise.reject(fe);\n'
     '    }\n'),
    # v31: two tabs creating the same day's Study Log entry (or its lessonIds map) for the first time: merge key by key
    # instead of letting the later save replace the whole record. Counters stay additions even when the parent is new.
    ("      if (depth > 0 && plain(x) && plain(y)){\n",
     "      if (depth > 0 && path[0] === \"log\" && x === undefined && plain(y)) x = {};\n"
     "      if (depth > 0 && plain(x) && plain(y)){\n"),
    # v31: the sidebar's Practice group is split: real projects under Projects, interview prep and the checkpoint under Review
    ('    if (ph.project) ROUTES.push({ id: rid(ph, "project"), phase: P, kind: "project", group: "Practice", title: "Project: " + ph.projectTitle, n: "", ref: ph.project });\n    LOCAL.forEach(function(lp){ if (lp.phase === P) ROUTES.push({ id: "local/" + lp.id, phase: P, kind: "local", group: "Practice",',
     '    if (ph.project) ROUTES.push({ id: rid(ph, "project"), phase: P, kind: "project", group: "Projects", title: ph.projectTitle.charAt(0).toUpperCase() + ph.projectTitle.slice(1), n: "", ref: ph.project });\n    LOCAL.forEach(function(lp){ if (lp.phase === P) ROUTES.push({ id: "local/" + lp.id, phase: P, kind: "local", group: "Projects",'),
    ('    if (P === "ph7") ROUTES.push({ id: "lab/real-model", phase: P, kind: "lab", group: "Practice",',
     '    if (P === "ph7") ROUTES.push({ id: "lab/real-model", phase: P, kind: "lab", group: "Projects",'),
    ('    ROUTES.push({ id: rid(ph, "interview"), phase: P, kind: "interview", group: "Practice", title: "Interview prep", n: "" });\n    ROUTES.push({ id: rid(ph, "checkpoint"), phase: P, kind: "checkpoint", group: "Practice",',
     '    ROUTES.push({ id: rid(ph, "interview"), phase: P, kind: "interview", group: "Review", title: "Interview prep", n: "" });\n    ROUTES.push({ id: rid(ph, "checkpoint"), phase: P, kind: "checkpoint", group: "Review",'),
    # v31: after GitHub sign-in the review could fail to open when the page re-rendered the card in between
    # (the old card took the flag and then found itself gone). Take the flag only when this card opens the review.
    ('      if (flag === ex.id && (j === "connected" || NET.connected)){\n        try { sessionStorage.removeItem("fde-gh-review"); } catch(e){}\n        if (NET.connected){ setTimeout(function(){ if (document.body.contains(card)) openReview("Signed in to GitHub as " + NET.user.login + "."); }, 0); return; }\n      }',
     '      if (flag === ex.id && (j === "connected" || NET.connected)){\n        if (NET.connected){ setTimeout(function(){ var f2 = null; try { f2 = sessionStorage.getItem("fde-gh-review"); } catch(e){} if (f2 === ex.id && document.body.contains(card)){ try { sessionStorage.removeItem("fde-gh-review"); } catch(e){} openReview("Signed in to GitHub as " + NET.user.login + "."); } }, 0); return; }\n        try { sessionStorage.removeItem("fde-gh-review"); } catch(e){}\n      }'),
    # v31: a save arriving from another tab (or from this page before the GitHub sign-in reload) re-rendered the
    # page and closed an open publish review. Treat an open review like typing: refresh the sidebar only.
    ('    var a = document.activeElement, typing = a && view.contains(a) && /^(TEXTAREA|INPUT|SELECT)$/.test(a.tagName);\n    if (why === "restored") navPhase = null;',
     '    var a = document.activeElement, typing = (a && view.contains(a) && /^(TEXTAREA|INPUT|SELECT)$/.test(a.tagName)) || !!view.querySelector("[data-gh-review]:not([hidden])");\n    if (why === "restored") navPhase = null;'),
]


def apply(s):
    for old, new in PATCHES:
        n = s.count(old)
        if n != 1:
            raise SystemExit("patch target found %d times:\n%s" % (n, old[:200]))
        s = s.replace(old, new)
    i = s.index("</style>")
    return s[:i] + CSS + s[i:]
