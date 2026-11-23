"""Build v31.2 (fixes from the v31.1 audit) on top of the v31.1 page.

    python scripts/content/v312.py BASE.html OUT.html

BASE is the v31.1 build (sha256 a8cd131b...46b3). Every change is a checked text or data edit:
  1. ph9-e12: the demo at the bottom of the starter, given code and solution deletes runs.db first,
     so pressing Run twice no longer fails with "run r1 already exists".
  2. Seven inline questions get a happy-path check, so an answer that skips the main job fails.
  3. Quiz options from quiz_v312.json: wrong options rewritten so the right answer is not simply the longest.
  4. Page code: honest README status, whole-sentence summary, "repository not found" handled as gone,
     a "Page not found" note, level chips on every question, 44 px Hint target.
  5. "New here" notes (explanation plus a worked example whose output is computed) for the 51 items the
     audit found using a feature with no note. Each item keeps its existing optional hint.
Needs Python 3.12 with numpy, pandas and scikit-learn (for the worked examples).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import newhere as NH  # noqa: E402

REPORT = {}


def sub1(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f"{label}: expected 1 match, found {n}")
    return s.replace(old, new)


def inline_q(s):
    i = s.index("var INLINE_Q = ") + len("var INLINE_Q = ")
    obj, end = json.JSONDecoder().raw_decode(s, i)
    return obj, i, end


def json_block(s, bid):
    m = re.search(r'(<script type="application/json" id="' + bid + r'">)(.*?)(</script>)', s, re.S)
    return m, json.loads(m.group(2))


def put_json_block(s, bid, obj):
    m, _ = json_block(s, bid)
    return s[:m.start(2)] + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + s[m.end(2):]


# ------------------------------------------------------------------ 1. run twice
FRESH = ('import os\n'
         'if os.path.exists("runs.db"):\n'
         '    os.remove("runs.db")   # start from an empty file each time you press Run\n'
         'store = RunStore("runs.db")\n')


def fix_run_twice(s):
    a = s.index('<section class="ex-src" data-phase="ph9" data-id="ph9-e12"')
    b = s.index("</section>", a)
    sec = s[a:b]
    n = sec.count('\nstore = RunStore("runs.db")\n')
    if n != 3:
        raise SystemExit(f"ph9-e12: expected 3 demo lines, found {n}")
    sec = sec.replace('\nstore = RunStore("runs.db")\n', "\n" + FRESH)
    s = s[:a] + sec + s[b:]
    _, notes = json_block(s, "solution-notes")
    lst = notes["ph9-e12"]
    k = next(i for i, it in enumerate(lst) if it[0] == 'store = RunStore("runs.db")')
    lst[k:k + 1] = [["import os", "For the file check below."],
                    ['if os.path.exists("runs.db"):', "The browser keeps files between runs, so an earlier run's database would still be there."],
                    ['    os.remove("runs.db")   # start from an empty file each time you press Run',
                     'Deleting it first means <code>start("r1", ...)</code> works every time you press Run. In a real app you keep the file: that is the point of the store.'],
                    ['store = RunStore("runs.db")', "A database file."]]
    s = put_json_block(s, "solution-notes", notes)
    REPORT["run_twice"] = "ph9-e12 starter, given and solution"
    return s


# ------------------------------------------------------------------ 2. happy-path checks
HAPPY = {
    "q:ph5-l12-3": [("Answers 202 with the job id",
                     'q = []\nassert submit(q, {"x": 1}) == (202, {"job_id": "job-1"})\n'
                     'assert submit(q, {"x": 2}) == (202, {"job_id": "job-2"}) and q[1]["id"] == "job-2"\n')],
    "q:ph6-l15-3": [("A repeat is answered from the cache",
                     'n = []\nc = {}\nf = lambda b, p: n.append(1) or "desc:" + p\n'
                     'assert cached_describe(b"x", "a", c, f) == "desc:a"\n'
                     'assert cached_describe(b"x", "a", c, f) == "desc:a" and len(n) == 1\n'
                     'cached_describe(b"y", "a", c, f)\nassert len(n) == 2, "a different image is a new call"\n')],
    "q:ph9-l4-3": [("Same request runs once",
                    'j, n = {}, []\nf = lambda t: n.append(t) or len(n)\n'
                    'assert once(j, "r1", "a", {"t": 1}, f) == 1\n'
                    'assert once(j, "r1", "a", {"t": 1}, f) == 1 and len(n) == 1, "the second call must return the stored result"\n')],
    "q:ph9-l9-3": [("Reads each line and skips blanks",
                    'assert read_messages(\'{"id": 1}\\n\\n{"id": 2}\\n\') == [{"id": 1}, {"id": 2}]\n'
                    'assert read_messages("") == []\n')],
    "q:ph9-l13-2": [("Steps come after what they need",
                     'plan = [{"id": "reply", "after": ["order", "policy"]}, {"id": "order", "after": []}, {"id": "policy", "after": []}]\n'
                     'assert run_order(plan) == ["order", "policy", "reply"]\n'
                     'assert run_order([]) == []\n')],
    "q:ph9-l14-2": [("Allowed moves",
                     'assert next_state("submitted", "start") == "working"\n'
                     'assert next_state("working", "need_input") == "input-required"\n'
                     'assert next_state("input-required", "reply") == "working"\n'
                     'assert next_state("working", "finish") == "completed"\n'
                     'assert next_state("working", "error") == "failed"\n'
                     'assert next_state("input-required", "cancel") == "canceled"\n')],
    "q:ph9-l16-1": [("Fills in the answer and leaves the saved state alone",
                     'cp = {"t1": {"order": "A1002", "waiting_for": "approval"}}\n'
                     'new = resume(cp, "t1", {"approved": True})\n'
                     'assert new == {"order": "A1002", "approval": {"approved": True}, "waiting_for": None}\n'
                     'assert cp["t1"]["waiting_for"] == "approval", "return a new state; do not change the saved one"\n'
                     'try:\n    resume(cp, "nope", 1)\n    assert False, "an unknown thread must raise KeyError"\nexcept KeyError:\n    pass\n')],
}


def fix_weak(iq):
    by = {q["id"]: q for qs in iq.values() for q in qs}
    for qid, tests in HAPPY.items():
        q = by[qid]
        names = {t["name"] for t in q["tests"]}
        q["tests"] = [{"name": n, "code": c} for n, c in tests if n not in names] + q["tests"]
    REPORT["happy_tests"] = len(HAPPY)
    return iq


# ------------------------------------------------------------------ 3. quiz options
def fix_quiz(s):
    path = os.path.join(HERE, "quiz_v312.json")
    if not os.path.exists(path):
        REPORT["quiz"] = "no quiz_v312.json"
        return s
    edits = json.load(open(path, encoding="utf-8"))   # {"lesson": {"index": {"o": [...], "q"?: str}}}
    done = 0
    out, pos = [], 0
    for m in re.finditer(r'(<script type="application/json" class="quiz-data">)(.*?)(</script>)', s, re.S):
        data = json.loads(m.group(2))
        for lid, qs in data.items():
            for k, e in (edits.get(lid) or {}).items():
                q = qs[int(k)]
                if "check" in e and e["check"] != q["o"][q["a"]][:40]:
                    raise SystemExit(f"quiz {lid}#{k}: answer changed under the edit")
                if len(e["o"]) != len(q["o"]):
                    raise SystemExit(f"quiz {lid}#{k}: option count")
                q["o"] = e["o"]
                done += 1
        out.append(s[pos:m.start(2)])
        out.append(json.dumps(data, ensure_ascii=False, indent=1).replace("</", "<\\/"))
        pos = m.end(2)
    out.append(s[pos:])
    REPORT["quiz_edited"] = done
    return "".join(out)


# ------------------------------------------------------------------ 4. page code
JS = [
    # README: whole first sentence, never cut mid-word, never a list run together
    ('  function firstSentence(t){ var m = String(t).replace(/\\s+/g, " ").trim().match(/^.{20,240}?[.!?](?=\\s|$)/); return m ? m[0] : String(t).replace(/\\s+/g, " ").trim().slice(0, 200); }',
     '  function firstSentence(t){\n'
     '    // v31.2: the first sentence of the first paragraph; a long one is cut at a word, with an ellipsis\n'
     '    var para = String(t).split(/\\n\\s*\\n/)[0].replace(/\\s+/g, " ").trim();\n'
     '    var m = para.match(/^.{20,300}?[.!?](?=\\s|$)/); if (m) return m[0];\n'
     '    if (para.length <= 300) return para.replace(/:$/, ".");\n'
     '    var cut = para.slice(0, 240); cut = cut.slice(0, Math.max(cut.lastIndexOf(" "), 1)); return cut.replace(/[\\s,;:]+$/, "") + "…";\n'
     '  }\n'
     '  // v31.2: has the learner changed the starting template? An untouched template is never described as a solution.\n'
     '  function startedOn(ex, code){ return String(code || "").replace(/\\s+$/, "") !== String(ex.starter || "").replace(/\\s+$/, ""); }',
     "firstSentence"),
    # jsReadme
    ('    md += "## Overview\\n\\nAn exercise from **Phase " + ph.n + ": " + ph.title + "** of my forward deployed engineer study path. My solution is in `main.js` and the automated checks are in `tests/main.test.js`.\\n\\n";\n'
     '    md += "## The problem\\n\\n" + task + "\\n\\n";\n'
     '    if (ideas) md += "## Key ideas\\n\\n" + ideas + "\\n\\n";',
     '    var solved = checks.passed === checks.total, started = startedOn(ex, code);\n'
     '    md += "## Overview\\n\\nAn exercise from **Phase " + ph.n + ": " + ph.title + "** of my forward deployed engineer study path. " +\n'
     '      (solved ? "My solution is in `main.js`" : started ? "My work in progress is in `main.js`" : "`main.js` still holds the starting template: I have not solved it yet") + " and the automated checks are in `tests/main.test.js`.\\n\\n";\n'
     '    md += "## The problem\\n\\n" + task + "\\n\\n";\n'
     '    if (ideas && solved) md += "## Key ideas\\n\\n" + ideas + "\\n\\n";',
     "jsReadme overview"),
    ('    md += "## Testing\\n\\n" + checksText(ex, checks) + ex.tests.map(function(t){ return "- " + t.name; }).join("\\n") + "\\n\\n";\n'
     '    if (note) md += "## What I learned\\n\\n" + note + "\\n\\n";\n'
     '    md += "---\\n\\n_This README was generated from the code and task by my forward deployed engineer study site._\\n";',
     '    md += "## Testing\\n\\n" + checksText(ex, checks, code) + ex.tests.map(function(t){ return "- " + t.name; }).join("\\n") + "\\n\\n";\n'
     '    if (note) md += "## What I learned\\n\\n" + note + "\\n\\n";\n'
     '    md += "---\\n\\n_This README was generated from the code and task by my forward deployed engineer study site._\\n";',
     "jsReadme tests"),
    # smartReadme
    ('    var ideas = htmlToMd(ex.explain || "");\n    var folder = defaultFolder(ex).split("/").pop();',
     '    var ideas = htmlToMd(ex.explain || "");\n'
     '    var solved = checks.passed === checks.total, started = startedOn(ex, code);\n'
     '    var folder = defaultFolder(ex).split("/").pop();',
     "smartReadme status"),
    ('The problem is stated below; my solution is in `main.py`" + (',
     'The problem is stated below; " + (solved ? "my solution is in `main.py`" : started ? "my work in progress is in `main.py`" : "`main.py` still holds the starting template (not solved yet)") + (',
     "smartReadme overview"),
    ('    if (ideas) md += "## Key ideas\\n\\nWhy a solution to this problem works, and what it practises:\\n\\n" + ideas + "\\n\\n";',
     '    if (ideas && solved) md += "## Key ideas\\n\\nWhy a solution to this problem works, and what it practises:\\n\\n" + ideas + "\\n\\n";',
     "smartReadme ideas"),
    ('    md += "\\n## How it works\\n\\n- **Main file:** `main.py`, " + lines + " lines of code (without blank lines and comments)\\n";\n    if (s.fns.length) md += "- **Functions:** " + codeList(s.fns, 8) + "\\n";',
     '    md += "\\n## How it works\\n\\n- **Main file:** `main.py`, " + (started ? lines + " lines of code (without blank lines and comments)" : "the starting template, not solved yet") + "\\n";\n    if (s.fns.length) md += "- **Functions:** " + codeList(s.fns, 8) + "\\n";',
     "smartReadme lines"),
    ('    md += "\\n## Design decisions\\n\\n" + dec.slice(0, 5).map(function(x){ return "- " + x; }).join("\\n") + "\\n";',
     '    if (started) md += "\\n## Design decisions\\n\\n" + dec.slice(0, 5).map(function(x){ return "- " + x; }).join("\\n") + "\\n";',
     "smartReadme design"),
    ('    if (checks.passed === checks.total) md += "All " + checks.total + " automated checks pass in my study site\'s checker. The same checks are in `tests/test_main.py`:\\n\\n";\n'
     '    else if (checks.fresh)',
     '    if (checks.passed === checks.total) md += "All " + checks.total + " automated checks pass in my study site\'s checker. The same checks are in `tests/test_main.py`:\\n\\n";\n'
     '    else if (!started) md += "Not solved yet, so none of the " + checks.total + " automated checks pass. The checks are:\\n\\n";\n'
     '    else if (checks.fresh)',
     "smartReadme tests"),
    ('  function checksText(ex, checks){\n    if (checks.passed === checks.total) return "All " + checks.total + " automated checks pass:\\n\\n";',
     '  function checksText(ex, checks, code){\n    if (checks.passed === checks.total) return "All " + checks.total + " automated checks pass:\\n\\n";\n'
     '    if (code != null && !startedOn(ex, code)) return "Not solved yet, so none of the " + checks.total + " automated checks pass. The checks are:\\n\\n";',
     "checksText"),
    ('    md += "\\n## Testing\\n\\n" + checksText(ex, checks) + ex.tests.map(',
     '    md += "\\n## Testing\\n\\n" + checksText(ex, checks, code) + ex.tests.map(',
     "portfolio tests"),
    ('      checks_status: checks.passed === checks.total ? "all pass" : checks.fresh ? checks.passed + " of " + checks.total + " pass" : "not all pass yet",',
     '      checks_status: checks.passed === checks.total ? "all pass" : !startedOn(ex, code) ? "not started: the code is the unchanged starting template, so do not describe it as a solution" : checks.fresh ? checks.passed + " of " + checks.total + " pass" : "not all pass yet",',
     "readmePrompt status"),
    # verify: a repository GitHub no longer shows is reported like a missing folder, with what to do next
    ('          else if (x.d.state === "gone") cur.verify = { state: "gone", at: Date.now(), note: x.d.note, reason: x.d.reason };',
     '          else if (x.d.state === "gone") cur.verify = { state: "gone", at: Date.now(), note: x.d.note, reason: x.d.reason };\n'
     '          else if (x.d.state === "noaccess") cur.verify = { state: "gone", at: Date.now(), reason: "repo", note: (x.d.note || "GitHub did not show that repository.") + " Choose another repository the next time you publish." };',
     "verify noaccess"),
    ('x.d.state === "gone" ? "It is no longer where it was published." :',
     'x.d.state === "gone" || x.d.state === "noaccess" ? "It is no longer where it was published." :',
     "verify message"),
    # every question shows a level; questions without one get it from their starter
    ('    var LEVELS = { guided: "Guided", independent: "Independent", challenge: "Challenge" };\n',
     '    var LEVELS = { guided: "Guided", independent: "Independent", challenge: "Challenge" };\n'
     '    // v31.2: a question without a set level is Challenge when optional, Guided when its starter already has\n'
     '    // code inside the function, otherwise Independent (the same rule the hand-set levels follow).\n'
     '    if (!LEVELS[ex.level]) ex.level = ex.optional ? "challenge" : String(ex.starter || "").split("\\n").some(function(l){ var t = l.trim(); return /^\\s/.test(l) && t && t.charAt(0) !== "#" && !/^(pass|\\.\\.\\.|return None|return;?|\\/\\/.*)$/.test(t); }) ? "guided" : "independent";\n',
     "levels"),
    # unknown address: say so instead of silently showing Home
    ('    if (r.id === "home") renderHome();\n    else if (r.id === "playground") renderPlayground();',
     '    if (r.id === "home"){\n'
     '      renderHome();\n'
     '      var asked = (location.hash || "").replace(/^#\\/?/, "");\n'
     '      if (/^#\\//.test(location.hash || "") && asked && asked !== "home" && routeIndex[asked] == null)\n'
     '        view.insertAdjacentHTML("afterbegin", \'<div class="callout not-found" role="status"><p><b>Page not found.</b> There is no page at <code>#/\' + esc(asked) + \'</code>, so here is the home page. Use the course contents or Search to find it.</p></div>\');\n'
     '    }\n    else if (r.id === "playground") renderPlayground();',
     "not found"),
    # publish: a clear success message with a link, and a new publish clears an old "could not confirm" note
    ('            it.status = "published"; it.url = x.d.folderUrl || ""; it.repoUrl = x.d.repoUrl || ""; it.commitUrl = x.d.commitUrl || ""; it.sha = x.d.sha || ""; it.doneAt = Date.now(); it.error = ""; save(); refresh();\n'
     '            closeReview(x.d.unchanged ? "GitHub already has exactly these files, so nothing new was committed." : "Published " + x.d.files + " files to " + it.repo + " (" + it.branch + ") in one commit.");',
     '            it.status = "published"; it.url = x.d.folderUrl || ""; it.repoUrl = x.d.repoUrl || ""; it.commitUrl = x.d.commitUrl || ""; it.sha = x.d.sha || ""; it.doneAt = Date.now(); it.error = ""; it.verify = null; save(); refresh();\n'
     '            closeReview("");\n'
     '            st.innerHTML = \'<span class="gh-ok">✓ \' + (x.d.unchanged ? "Already on GitHub: these exact files are there, so nothing new was committed." :\n'
     '              "Published to GitHub: " + x.d.files + " files in " + esc(it.repo) + " (" + esc(it.branch) + ")" + (x.d.commits > 1 ? ", in " + x.d.commits + " commits." : ", in one commit.")) + "</span>" +\n'
     '              (it.url ? \' <a href="\' + esc(it.url) + \'" target="_blank" rel="noopener">Open on GitHub</a>\' : "");',
     "publish success"),
]

CSS = [(".pq-hint{margin-top:10px}\n",
        ".pq-hint{margin-top:10px}\n.pq-hint > summary{min-height:44px;display:flex;align-items:center;cursor:pointer}\n.gh-ok{color:var(--good);font-weight:600}\n", "hint css")]



def fix_code(s):
    for old, new, label in JS + CSS:
        s = sub1(s, old, new, label)
    REPORT["code_patches"] = len(JS) + len(CSS)
    return s


# ------------------------------------------------------------------ 5. new-here notes
EXTRA = {
    "syntax:for loop": ("<code>for item in items:</code> runs its indented block once for each item, in order (lesson Lists, dicts and loops).",
                        "#show\ntotal = 0\nfor n in [2, 3, 5]:\n    total = total + n\n", ["total"]),
    "method:.split": ("<code>text.split(sep)</code> cuts text into a list at each <code>sep</code>; with no argument it splits on any run of spaces (lesson Values, names and strings).",
                      "", ['"a,b,c".split(",")', '"  two   words ".split()']),
    "method:.join": ("<code>sep.join(items)</code> glues a list of strings into one string with <code>sep</code> between them. It is the reverse of <code>split</code>.",
                     "", ['"-".join(["a", "b", "c"])', '" ".join("hi there".split())']),
}
NH.GLOSS.update(EXTRA)
FOLD = {"syntax:raise": "builtin:ValueError"}   # the ValueError note shows raise


def merge_box(existing, items):
    lis = "".join(items)
    if existing and existing.rstrip().endswith("</ul>") and "<b>New here</b>" in existing:
        e = existing.rstrip()
        return e[:-5] + lis + "</ul>"
    box = '<p><b>New here</b> (not shown earlier in the course):</p><ul>' + lis + "</ul>"
    return (existing or "") + box


def fix_notes(s, iq):
    unc = json.load(open(os.path.join(HERE, "audit", "uncovered_v311.json"), encoding="utf-8"))
    examples = NH.evaluate()
    by = {q["id"]: q for qs in iq.values() for q in qs}
    m, exn = json_block(s, "ex-newhere")
    n_inline = n_ex = 0
    skipped = []
    for lesson, item, kind, feats in unc:
        feats = list(dict.fromkeys(FOLD.get(f, f) for f in feats if f not in NH.NOT_NEW))
        if not feats:
            skipped.append(item)
            continue
        items = [NH.note_html(f, examples) for f in feats]
        if kind == "inline":
            by[item]["before"] = merge_box(by[item].get("before"), items); n_inline += 1
        else:
            exn[item] = merge_box(exn.get(item), items); n_ex += 1
    s = put_json_block(s, "ex-newhere", exn)
    REPORT["notes"] = {"inline": n_inline, "exercises": n_ex, "skipped": skipped}
    return s, iq


def main(base, out):
    s = open(base, encoding="utf-8").read()
    s = fix_run_twice(s)
    iq, i, end = inline_q(s)
    iq = fix_weak(iq)
    s, iq = fix_notes(s, iq)
    iq2, i, end = inline_q(s)     # notes changed only other blocks; write the edited questions back
    s = s[:i] + json.dumps(iq, ensure_ascii=False).replace("</", "<\\/") + s[end:]
    s = fix_quiz(s)
    s = fix_code(s)
    open(out, "w", encoding="utf-8").write(s)
    print(json.dumps(REPORT, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
