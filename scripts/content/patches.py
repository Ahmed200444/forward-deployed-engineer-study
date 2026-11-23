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
]


def apply(s):
    for old, new in PATCHES:
        n = s.count(old)
        if n != 1:
            raise SystemExit("patch target found %d times:\n%s" % (n, old[:200]))
        s = s.replace(old, new)
    i = s.index("</style>")
    return s[:i] + CSS + s[i:]
