"""Build the v30 teaching changes into index.html.

    python scripts/content/build.py BASE.html OUT.html

BASE is the v29 build (commit cf73789). The script:
  1. rewrites the priority lessons from lessons.py, keeping every original code block's key
     (data-snip="N" -> lesson#N) so saved edits, line notes and recorded outputs still match;
  2. runs every new and kept block in a fresh Python process and writes its real output into the
     lesson (text, SQL rows, and a static copy of any chart);
  3. reorders and labels the inline questions from questions.py, adds the new ones, and writes the
     expected output of new questions from their solutions;
  4. adds the "new here" notes from newhere.py to questions in other lessons;
  5. patches the page code (data-snip keys, question levels, Optional practice, Playground echo,
     plot-object echo) and its CSS.
Needs numpy and matplotlib for the chart blocks.
"""
import base64
import html
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lessons as LS  # noqa: E402
import lessons_v31 as L31  # noqa: E402
LS.LESSONS.update(L31.LESSONS)
import questions as QS  # noqa: E402
import newhere as NH  # noqa: E402
import patches as PT  # noqa: E402

esc = lambda t: html.escape(t, quote=False)


# ------------------------------------------------------------------ page data blocks
def json_block(s, bid):
    m = re.search(r'(<script type="application/json" id="' + bid + r'">)(.*?)(</script>)', s, re.S)
    return m, json.loads(m.group(2))


def put_json_block(s, bid, obj):
    m, _ = json_block(s, bid)
    txt = json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")
    return s[:m.start(2)] + txt + s[m.end(2):]


def inline_q(s):
    i = s.index("var INLINE_Q = ") + len("var INLINE_Q = ")
    obj, end = json.JSONDecoder().raw_decode(s, i)
    return obj, i, end


# ------------------------------------------------------------------ running code like the page
RUNNER = r'''
import ast, contextlib, io, json, os, sys, traceback
spec = json.load(open(sys.argv[1]))
os.chdir(spec["dir"]); sys.path.insert(0, spec["dir"])
for name, text in spec["files"].items():
    open(name, "w", encoding="utf-8").write(text)
import matplotlib
matplotlib.use("Agg")
matplotlib.rcParams["svg.fonttype"] = "none"
out = io.StringIO(); res = {"stdout": "", "error": None, "rows": None, "figs": []}
ns = {"__name__": "__main__"}
def echo(v):
    if v is None: return
    m = type(v).__module__ or ""
    if m.startswith("matplotlib"): return
    if isinstance(v, (list, tuple)) and v and any((type(x).__module__ or "").startswith("matplotlib") for x in v): return
    print(repr(v))
with contextlib.redirect_stdout(out):
    try:
        exec(compile(spec["setup"], "<setup>", "exec"), ns)
        if spec["mode"] == "sql":
            conn = ns["conn"]; cur = conn.execute(spec["code"])
            if cur.description:
                res["rows"] = {"columns": [d[0] for d in cur.description], "rows": [list(r) for r in cur.fetchall()]}
        else:
            for node in ast.parse(spec["code"], "main.py").body:
                if isinstance(node, ast.Expr):
                    echo(eval(compile(ast.Expression(node.value), "main.py", "eval"), ns))
                else:
                    exec(compile(ast.Module([node], type_ignores=[]), "main.py", "exec"), ns)
    except BaseException as e:
        res["error"] = f"{type(e).__name__}: {e}"
plt = sys.modules.get("matplotlib.pyplot")
if plt is not None:
    for num in plt.get_fignums():
        b = io.StringIO(); plt.figure(num).savefig(b, format="svg", bbox_inches="tight"); res["figs"].append(b.getvalue())
res["stdout"] = out.getvalue()
print(json.dumps(res))
'''


def run_block(spec, code, files):
    with tempfile.TemporaryDirectory() as d:
        sp = os.path.join(d, "_spec.json")
        work = os.path.join(d, "work"); os.mkdir(work)
        json.dump({"dir": work, "files": files, "setup": spec.get("setup", ""), "mode": spec["mode"], "code": code}, open(sp, "w"))
        rp = os.path.join(d, "_run.py"); open(rp, "w").write(RUNNER)
        p = subprocess.run([sys.executable, "-I", rp, sp], capture_output=True, text=True, timeout=120)
        if p.returncode != 0:
            raise SystemExit("runner failed for block:\n" + code + "\n" + p.stderr)
        res = json.loads(p.stdout.strip().splitlines()[-1])
        if res["figs"]:
            # draw charts with the bundled Pyodide runtime (Matplotlib 3.5.2), the same one the site runs
            q = subprocess.run(["node", os.path.join(HERE, "pyodide_run.js"), rp, sp], capture_output=True, text=True, timeout=300)
            if q.returncode != 0:
                raise SystemExit("Pyodide runner failed for block:\n" + code + "\n" + q.stderr)
            pres = json.loads(q.stdout.strip().splitlines()[-1])
            if pres["stdout"] != res["stdout"] or pres["error"] != res["error"] or len(pres["figs"]) != len(res["figs"]):
                raise SystemExit("Pyodide and CPython disagree on block:\n" + code + "\n" + json.dumps([pres["stdout"], res["stdout"], pres["error"], res["error"]]))
            res["figs"] = pres["figs"]
            REPORT["charts_pyodide"] = REPORT.get("charts_pyodide", 0) + len(pres["figs"])
        return res


def out_panel(res, label="Output"):
    body = res["stdout"].rstrip("\n")
    parts = ['<div class="out lesson-out"><div class="out-head">' + label + ' <span class="rec-tag">from a real run of the block above</span></div>']
    if body:
        parts.append('<pre class="lesson-out-text"><code>' + esc(body) + '</code></pre>')
    if res["error"]:
        parts.append('<pre class="lesson-out-text lesson-out-err"><code>' + esc(res["error"]) + '</code></pre>')
    for svg in res["figs"]:
        svg = re.sub(r'<\?xml[^>]*\?>\s*', "", svg)
        svg = re.sub(r'<!DOCTYPE[^>]*>\s*', "", svg)
        svg = re.sub(r'<metadata>.*?</metadata>', "", svg, flags=re.S)
        # an <img> keeps matplotlib's element ids out of the page (the lesson source and the view would both hold them)
        uri = "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")
        parts.append('<div class="lesson-out-fig"><img src="' + uri + '" alt="Chart drawn by the code above"></div>')
    parts.append("</div>")
    return "".join(parts)


def rows_panel(res, caption):
    if res["error"]:
        raise SystemExit("SQL block failed: " + res["error"])
    r = res["rows"]
    # same text the live SQL runner shows: JavaScript prints 12.0 as 12
    fmt = lambda v: str(int(v)) if isinstance(v, float) and v.is_integer() and abs(v) < 1e21 else str(v)
    cell = lambda v: '<td class="null">NULL</td>' if v is None else "<td>" + esc(fmt(v)) + "</td>"
    head = "".join("<th scope=\"col\">" + esc(c) + "</th>" for c in r["columns"])
    body = "".join("<tr>" + "".join(cell(v) for v in row) + "</tr>" for row in r["rows"])
    n = len(r["rows"])
    return ('<div class="out lesson-out"><div class="out-head">' + caption + ' <span class="rec-tag">' + str(n) + (" row" if n == 1 else " rows") +
            ', from a real run</span></div><div class="table-wrap"><table class="sql-rows"><thead><tr>' + head + '</tr></thead><tbody>' + body +
            '</tbody></table></div></div>')


def file_panel(name, text):
    return ('<div class="out lesson-out"><div class="out-head"><code>' + esc(name) + '</code> <span class="rec-tag">the sample file</span></div>'
            '<pre class="lesson-out-text"><code>' + esc(text) + '</code></pre></div>')


# ------------------------------------------------------------------ lessons
def section_span(s, lid):
    m = re.search(r'<section class="lesson-src"[^>]*\bdata-id="' + re.escape(lid) + r'"[^>]*>', s)
    end = s.index("</section>", m.end())
    return m.end(), end


PRE_RE = re.compile(r"<pre>(.*?)</pre>", re.S)


def pre_text(pre_inner):
    return html.unescape(re.sub(r"</?code>", "", pre_inner)).rstrip() + "\n"


REPORT = {"lessons": {}, "outputs": 0, "sql_tables": 0, "charts": 0}


def expand(lid, tpl, blocks, orig_pres, snip):
    def spec_for(k):
        if k in blocks:
            b = dict(blocks[k]); b.setdefault("setup", ""); b.setdefault("files", []); return b
        return snip["blocks"].get(lid + "#" + k, {"mode": "none"})

    def code_for(k):
        if k in blocks:
            return blocks[k]["code"]
        sp = snip["blocks"].get(lid + "#" + k, {})
        return sp.get("code") or pre_text(orig_pres[int(k)])

    def files_for(spec):
        return {n: snip["files"][n] for n in spec.get("files", [])}

    used = []

    def rep(m):
        kind, k = m.group(1), m.group(2)
        if kind == "keep":
            used.append(k)
            return '<pre data-snip="' + k + '">' + orig_pres[int(k)] + "</pre>"
        if kind == "code":
            used.append(k)
            return '<pre data-snip="' + k + '"><code>' + esc(blocks[k]["code"].rstrip("\n")) + "</code></pre>"
        if kind == "file":
            return file_panel(k, snip["files"][k])
        spec = spec_for(k)
        res = run_block(spec, code_for(k), files_for(spec))
        REPORT["outputs"] += 1
        REPORT["charts"] += len(res["figs"])
        if kind == "rows":
            REPORT["sql_tables"] += 1
            cap = blocks.get(k, {}).get("caption") if k in blocks else None
            return rows_panel(res, cap or ("Rows after this step" if k != "w0" else "The whole table"))
        if k in blocks and blocks[k].get("show_code") is False:
            return out_panel(res, "What Python prints").replace("from a real run of the block above", "from a real run")
        return out_panel(res)

    out = re.sub(r"\[\[(keep|code|out|rows|file) ([^\]]+)\]\]", rep, tpl)
    return out, used


def apply_lessons(s, snip):
    for lid, (tpl, blocks) in LS.LESSONS.items():
        a, b = section_span(s, lid)
        orig = PRE_RE.findall(s[a:b])
        new, used = expand(lid, tpl, blocks, orig, snip)
        missing = [str(i) for i in range(len(orig)) if str(i) not in used]
        if missing:
            raise SystemExit(lid + ": original blocks not kept: " + ", ".join(missing))
        for k, blk in blocks.items():
            if k in used:
                spec = {"mode": blk["mode"], "setup": blk.get("setup", ""), "files": blk.get("files", [])}
                if blk.get("note"):
                    spec["note"] = blk["note"]
                if k.isdigit() and blk.get("code"):
                    spec["code"] = blk["code"]   # a kept block that runs a fuller version of the code shown
                snip["blocks"][lid + "#" + k] = spec
        s = s[:a] + "\n" + new + s[b:]
        REPORT["lessons"][lid] = {"blocks_kept": len(orig), "blocks_new": len([k for k in used if not k.isdigit()])}
    for lid, (marker, tpl, blocks) in LS.INSERTS.items():
        a, b = section_span(s, lid)
        body = s[a:b]
        idx = [0]

        def tag(m):
            i = idx[0]; idx[0] += 1
            return '<pre data-snip="' + str(i) + '">' + m.group(1) + "</pre>"
        body = PRE_RE.sub(tag, body)
        new, used = expand(lid, tpl, blocks, [], snip)
        if marker not in body:
            raise SystemExit(lid + ": insert marker missing")
        body = body.replace(marker, new + marker, 1)
        for k, blk in blocks.items():
            snip["blocks"][lid + "#" + k] = {"mode": blk["mode"], "setup": blk.get("setup", ""), "files": blk.get("files", [])}
        s = s[:a] + body + s[b:]
        REPORT["lessons"][lid] = {"blocks_kept": idx[0], "blocks_new": len(used)}
    return s


# ------------------------------------------------------------------ questions
def qbox(problem, sig, expected):
    return ('<div class="qbox" role="region" aria-label="The question"><div class="qbox-problem"><p>' + problem + '</p></div>'
            '<pre class="qbox-sig"><code>' + esc(sig) + '</code></pre><div class="qbox-expected"><span class="qbox-io">Expected output</span>'
            '<pre><code>' + esc(expected) + '</code></pre><p class="meta">What the <code>print</code> line at the bottom of your editor shows once your code is right.</p></div></div>')


def prereq_html(links):
    return "".join('<a href="' + h + '">' + esc(t) + "</a>" + (", " if i < len(links) - 1 else "") for i, (h, t) in enumerate(links))


def apply_questions(iq):
    for lid, order in QS.ORDER.items():
        old = {q["id"]: q for q in iq[lid]}
        seen, out = set(), []
        for qid, ch in order:
            if qid in QS.NEW:
                n = QS.NEW[qid]
                res = run_block({"mode": "py"}, n["solution"], n["files"])
                if res["error"]:
                    raise SystemExit(qid + " solution failed: " + res["error"])
                q = {"id": qid, "after": ch["after"], "title": n["title"], "prompt": qbox(n["problem"], n["sig"], res["stdout"].rstrip("\n")),
                     "hint": n["hint"], "starter": n["starter"], "solution": n["solution"], "files": n["files"], "tests": n["tests"]}
            else:
                q = dict(old[qid])
            for f in ("after", "starter", "solution"):
                if f in ch:
                    q[f] = ch[f]
            q["level"] = ch.get("level")
            if ch.get("optional"):
                q["optional"] = True
            if ch.get("before"):
                q["before"] = ch["before"]
            if ch.get("prereq"):
                q["prereq"] = prereq_html(ch["prereq"])
            seen.add(qid); out.append(q)
        lost = set(old) - seen
        if lost:
            raise SystemExit(lid + ": questions dropped: " + ", ".join(sorted(lost)))
        iq[lid] = out
    return iq


def check_afters(s, iq):
    for lid, qs in iq.items():
        a, b = section_span(s, lid)
        heads = [html.unescape(re.sub(r"<[^>]+>", "", h)).strip() for h in re.findall(r"<h2>(.*?)</h2>", s[a:b], re.S)]
        for q in qs:
            if not q.get("optional") and q["after"] not in heads:
                raise SystemExit(q["id"] + ": heading not found: " + q["after"])


def main(base, out):
    s = open(base, encoding="utf-8").read()
    _, snip = json_block(s, "snippet-data")
    s = apply_lessons(s, snip)
    s = put_json_block(s, "snippet-data", snip)
    iq, i, end = inline_q(s)
    iq = apply_questions(iq)
    check_afters(s[:i] + json.dumps(iq) + s[end:], iq)
    # audit the page without notes, then add a note for every remaining gap outside the rewritten lessons
    with tempfile.TemporaryDirectory() as d:
        pre = os.path.join(d, "pre.html"); open(pre, "w", encoding="utf-8").write(s[:i] + json.dumps(iq, ensure_ascii=False) + s[end:])
        aud = os.path.join(d, "audit.json")
        subprocess.run([sys.executable, os.path.join(HERE, "audit", "audit.py"), pre, aud], check=True, capture_output=True)
        rows = json.load(open(aud))["rows"]
    iq, exnotes, nh = NH.apply(iq, rows)
    REPORT["newhere"] = nh
    s = s[:i] + json.dumps(iq, ensure_ascii=False).replace("</", "<\\/") + s[end:]
    m, _ = json_block(s, "recorded-output")
    s = s[:m.end(3)] + '\n<script type="application/json" id="ex-newhere">' + json.dumps(exnotes, ensure_ascii=False).replace("</", "<\\/") + "</script>" + s[m.end(3):]
    s = PT.apply(s)
    open(out, "w", encoding="utf-8").write(s)
    json.dump(REPORT, open(os.path.join(os.path.dirname(os.path.abspath(out)), "build-report.json") if len(sys.argv) < 4 else sys.argv[3], "w"), indent=1)
    print(json.dumps({k: v for k, v in REPORT.items() if k != "newhere"}, indent=1))
    print("new-here notes:", json.dumps(nh))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
