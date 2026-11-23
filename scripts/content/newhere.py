"""'New here' notes for questions outside the rewritten lessons (v30).

The audit (scripts/content/audit/) lists, for every question, the Python or SQL features its reference
solution needs that no earlier lesson section shows. For each such feature this file holds a short
plain-English explanation and one or two example expressions. build.py evaluates every example in a
real Python process and prints its true value, so the notes cannot drift from what the code does.

A note is shown on the first question of a lesson that needs the feature; later questions in the
same lesson rely on it. Features without a glossary entry get a link to the official documentation,
so nothing a question needs is left unexplained or unlinked.
"""
import html
import json
import os
import re
import subprocess
import sys

esc = lambda t: html.escape(t, quote=False)
NP = "import numpy as np\n"

# feature -> (explanation HTML, setup, [example expressions])
GLOSS = {
    "builtin:float": ("<code>float(x)</code> turns a whole number or numeric text into a decimal number.", "", ['float("2.5")', "float(3)"]),
    "builtin:int": ("<code>int(x)</code> turns numeric text into a whole number, or drops the decimals of a float.", "", ['int("42")', "int(3.9)"]),
    "builtin:min": ("<code>min(...)</code> returns the smallest item; <code>max(...)</code> the largest. Both take a list or several values.", "", ["min([4, 1, 7])", "min(3, 8)"]),
    "builtin:max": ("<code>max(...)</code> returns the largest item. <code>key=</code> picks what to compare, as in sorting.", "", ["max([4, 1, 7])", 'max(["fig", "apple"], key=len)']),
    "builtin:sum": ("<code>sum(items)</code> adds up a list of numbers.", "", ["sum([1, 2, 3])"]),
    "builtin:abs": ("<code>abs(x)</code> is the size of a number without its sign.", "", ["abs(-3.5)"]),
    "builtin:round": ("<code>round(x, n)</code> rounds to <code>n</code> decimal places. Decimal arithmetic leaves tiny errors, which rounding hides.", "", ["0.1 + 0.2", "round(0.1 + 0.2, 10)"]),
    "builtin:all": ("<code>all(...)</code> is True when every item is true; <code>any(...)</code> when at least one is. Both often wrap a generator expression.", "", ["all(n > 0 for n in [1, 2, 3])", "all(n > 0 for n in [1, -2])"]),
    "builtin:any": ("<code>any(...)</code> is True when at least one item is true.", "", ["any(n < 0 for n in [1, -2])", "any([])"]),
    "builtin:bool": ("<code>bool(x)</code> turns a value into True or False. Zero, empty text and empty lists count as False.", "", ["bool(0)", 'bool("hi")', "bool([])"]),
    "builtin:tuple": ("<code>tuple(items)</code> makes a tuple: a list that cannot be changed.", "", ["tuple([1, 2])"]),
    "builtin:isinstance": ("<code>isinstance(x, T)</code> checks a value's type.", "", ["isinstance(3, int)", 'isinstance("3", int)']),
    "builtin:reversed": ("<code>reversed(items)</code> walks a list from the end; wrap it in <code>list()</code> to see it.", "", ["list(reversed([1, 2, 3]))"]),
    "builtin:zip": ("<code>zip(a, b)</code> pairs the first items, then the second, and so on. It stops at the shorter list without an error.", "", ["list(zip([1, 2], ['a', 'b']))"]),
    "builtin:getattr": ("<code>getattr(obj, name, default)</code> reads an attribute by its name as text, with a default if it is missing.", "", ['getattr("text", "upper")()', 'getattr(3, "missing", None)']),
    "builtin:ValueError": ("<code>raise ValueError(\"message\")</code> stops with an error you choose (lesson Files and errors).", "", []),
    "builtin:RuntimeError": ("<code>RuntimeError</code> is the general error for \"this should not happen now\". Raise it like <code>ValueError</code>.", "", []),
    "syntax:generator expression": ("A generator expression is a list comprehension without the square brackets, passed straight to a function such as <code>sum</code> or <code>\"\".join</code>.", "", ["sum(n * n for n in [1, 2, 3])", '"".join(w[0] for w in ["ada", "lovelace"])']),
    "syntax:dict comprehension": ("A dict comprehension builds a dict in one line: <code>{key: value for item in items}</code>.", "", ["{w: len(w) for w in ['fig', 'kiwi']}"]),
    "syntax:set comprehension": ("A set comprehension is a list comprehension in curly braces; repeats disappear.", "", ["sorted({w[0] for w in ['ant', 'ape', 'bee']})"]),
    "syntax:list comprehension": ("A list comprehension builds a list in one line: <code>[expr for x in items if condition]</code> (lesson Lists, dicts and loops).", "", ["[n * 2 for n in [1, 2, 3] if n != 2]"]),
    "syntax:f-string": ("An f-string puts values into text: <code>f\"{name} is {age}\"</code> (lesson Values, names and strings).", "", []),
    "syntax:while loop": ("<code>while condition:</code> repeats its block as long as the condition stays true. Make sure something inside changes it.", "", []),
    "syntax:// (floor division)": ("<code>a // b</code> divides and rounds down to a whole number.", "", ["7 // 2", "-7 // 2"]),
    "method:.tolist": ("<code>.tolist()</code> turns a NumPy array (or pandas Series) into a plain Python list, which is what tests usually compare.", NP, ["np.array([1, 2]).tolist()"]),
    "method:.sort": ("<code>items.sort()</code> sorts a list in place and returns None; <code>sorted(items)</code> returns a new list.", "", []),
    "method:.index": ("<code>items.index(x)</code> gives the position of the first <code>x</code>; it raises ValueError if <code>x</code> is missing.", "", ['["a", "b", "c"].index("b")']),
    "method:.extend": ("<code>a.extend(b)</code> adds every item of <code>b</code> to the end of <code>a</code>; <code>append</code> would add <code>b</code> as one item.", "", []),
    "method:.copy": ("<code>.copy()</code> makes a separate copy, so changing it leaves the original alone.", "", []),
    "method:.isdigit": ("<code>text.isdigit()</code> is True when the text is all digits.", "", ['"123".isdigit()', '"12a".isdigit()']),
    "method:.capitalize": ("<code>text.capitalize()</code> makes the first letter a capital and the rest lower case.", "", ['"hELLO".capitalize()']),
    "method:.rstrip": ("<code>rstrip()</code> strips only the right end; <code>lstrip()</code> only the left.", "", ['"  hi  ".rstrip()']),
    "method:.lstrip": ("<code>lstrip()</code> strips only the left end of the text.", "", ['"  hi  ".lstrip()']),
    "method:.pop": ("<code>items.pop()</code> removes and returns the last item; <code>d.pop(key)</code> removes a dict entry.", "", []),
    "method:.remove": ("<code>items.remove(x)</code> deletes the first <code>x</code> from a list.", "", []),
    "method:.update": ("<code>d.update(other)</code> copies every key and value of <code>other</code> into <code>d</code>.", "", []),
    "method:.append": ("<code>items.append(x)</code> adds <code>x</code> to the end of a list (lesson Lists, dicts and loops).", "", []),
    "import:re": ("<code>import re</code> loads regular expressions: patterns that match text. <code>\\d+</code> means one or more digits, <code>\\s</code> any space, <code>[a-z]</code> one letter.", "import re\n", ['re.findall(r"\\d+", "a1 b22")']),
    "func:re.sub": ("<code>re.sub(pattern, new, text)</code> replaces every match of a pattern. <code>\\s+</code> matches a run of spaces.", "import re\n", ['re.sub(r"\\s+", " ", "a   b\\tc")']),
    "func:re.findall": ("<code>re.findall(pattern, text)</code> returns every match as a list.", "import re\n", ['re.findall(r"\\d+", "rooms 3, baths 2")']),
    "func:re.search": ("<code>re.search(pattern, text)</code> finds the first match or returns None; <code>.group()</code> is the matched text.", "import re\n", ['re.search(r"\\d+", "id 42").group()', 're.search(r"\\d", "none")']),
    "func:re.match": ("<code>re.match</code> is like <code>re.search</code> but only matches at the start of the text.", "import re\n", ['re.match(r"\\d", "a1")']),
    "func:re.fullmatch": ("<code>re.fullmatch</code> matches only when the whole text fits the pattern.", "import re\n", ['bool(re.fullmatch(r"\\d+", "123"))', 'bool(re.fullmatch(r"\\d+", "12a"))']),
    "func:re.compile": ("<code>re.compile(pattern)</code> prepares a pattern once, to reuse it many times.", "", []),
    "func:math.ceil": ("<code>math.ceil(x)</code> rounds up to the next whole number (<code>import math</code>).", "import math\n", ["math.ceil(2.1)", "math.ceil(2.0)"]),
    "func:math.log": ("<code>math.log(x)</code> is the natural logarithm: how many times you multiply by e (about 2.718) to reach x.", "import math\n", ["round(math.log(1), 3)", "round(math.log(10), 3)"]),
    "func:math.isclose": ("<code>math.isclose(a, b)</code> compares decimals while ignoring tiny rounding errors.", "import math\n", ["0.1 + 0.2 == 0.3", "math.isclose(0.1 + 0.2, 0.3)"]),
    "func:np.asarray": ("<code>np.asarray(x)</code> turns a list into a NumPy array (and leaves an array as it is), so maths like <code>x * 2</code> works on every item at once.", NP, ["np.asarray([1, 2, 3]) * 2"]),
    "func:np.mean": ("<code>np.mean(x)</code> is the average: add up, divide by how many.", NP, ["np.mean([2, 4, 9])"]),
    "func:np.median": ("<code>np.median(x)</code> is the middle value once sorted.", NP, ["np.median([2, 4, 9])"]),
    "func:np.sum": ("<code>np.sum(x)</code> adds every item of an array.", NP, ["np.sum([1, 2, 3])"]),
    "func:np.where": ("<code>np.where(condition, a, b)</code> picks <code>a</code> where the condition is true and <code>b</code> elsewhere, item by item.", NP, ["np.where(np.array([1, -2, 3]) > 0, 1, 0)"]),
    "func:np.log": ("<code>np.log(x)</code> is the natural logarithm of every item.", NP, ["np.round(np.log(np.array([1, 10])), 3)"]),
    "func:np.log10": ("<code>np.log10(x)</code> is the base-10 logarithm: the number of zeros for 10, 100, 1000.", NP, ["np.log10(np.array([10, 1000]))"]),
    "func:np.exp": ("<code>np.exp(x)</code> is e (about 2.718) to the power x, item by item; it undoes <code>np.log</code>.", NP, ["np.round(np.exp(np.array([0, 1])), 3)"]),
    "func:np.maximum": ("<code>np.maximum(a, b)</code> keeps the larger value at each position (<code>np.minimum</code> the smaller). With 0 it clips negatives.", NP, ["np.maximum(np.array([-1, 2]), 0)"]),
    "func:np.minimum": ("<code>np.minimum(a, b)</code> keeps the smaller value at each position.", NP, ["np.minimum(np.array([-1, 2]), 0)"]),
    "func:np.clip": ("<code>np.clip(x, low, high)</code> limits every value to the range low to high.", NP, ["np.clip(np.array([-5, 3, 9]), 0, 5)"]),
    "func:np.round": ("<code>np.round(x, n)</code> rounds every item to <code>n</code> decimals.", NP, ["np.round(np.array([1.234, 5.678]), 1)"]),
    "func:np.zeros": ("<code>np.zeros(n)</code> makes an array of n zeros; <code>np.zeros((rows, cols))</code> a grid.", NP, ["np.zeros(3)"]),
    "func:np.zeros_like": ("<code>np.zeros_like(x)</code> makes zeros with the same shape as <code>x</code>.", NP, ["np.zeros_like(np.array([4, 5]))"]),
    "func:np.ones": ("<code>np.ones(n)</code> makes an array of ones.", NP, ["np.ones(2)"]),
    "func:np.argsort": ("<code>np.argsort(x)</code> gives the positions that would sort <code>x</code>, smallest first.", NP, ["np.argsort(np.array([30, 10, 20]))"]),
    "func:np.argmax": ("<code>np.argmax(x)</code> is the position of the largest value.", NP, ["np.argmax(np.array([3, 9, 2]))"]),
    "func:np.abs": ("<code>np.abs(x)</code> drops the sign of every item.", NP, ["np.abs(np.array([-2, 3]))"]),
    "func:np.histogram": ("<code>np.histogram(x, bins)</code> counts how many values fall into each bin; it returns (counts, bin edges).", NP, ["np.histogram([1, 2, 2, 8], bins=2)"]),
    "func:np.percentile": ("<code>np.percentile(x, p)</code> is the value below which p% of the data lies; 50 is the median.", NP, ["np.percentile([1, 2, 3, 4, 100], 50)"]),
    "func:np.std": ("<code>np.std(x)</code> is the standard deviation: the typical distance from the mean.", NP, ["np.std([2, 4, 4, 4, 5, 5, 7, 9])"]),
    "func:np.arange": ("<code>np.arange(n)</code> is 0, 1, ..., n-1 as an array.", NP, ["np.arange(4)"]),
    "func:np.cumsum": ("<code>np.cumsum(x)</code> is the running total.", NP, ["np.cumsum([3, 1, 4])"]),
    "func:np.diff": ("<code>np.diff(x)</code> is the difference between each item and the one before it.", NP, ["np.diff([1, 4, 9])"]),
    "func:np.unique": ("<code>np.unique(x)</code> gives the distinct values, sorted.", NP, ["np.unique([3, 1, 3])"]),
    "func:np.bincount": ("<code>np.bincount(x)</code> counts how often each whole number 0, 1, 2, ... appears.", NP, ["np.bincount([0, 2, 2])"]),
    "func:np.isclose": ("<code>np.isclose(a, b)</code> compares decimals item by item, ignoring rounding noise.", NP, ["np.isclose(0.1 + 0.2, 0.3)"]),
    "method:.reshape": ("<code>a.reshape(rows, cols)</code> gives the same numbers a new shape; -1 means \"work it out\".", NP, ["np.arange(4).reshape(2, -1)"]),
    "method:.ravel": ("<code>a.ravel()</code> flattens an array into one row.", NP, ["np.array([[1, 2], [3, 4]]).ravel()"]),
    "method:.permutation": ("<code>rng.permutation(n)</code> shuffles the numbers 0 to n-1, with <code>rng = np.random.default_rng(seed)</code>; the same seed gives the same shuffle.", NP, ["np.random.default_rng(0).permutation(4)"]),
    "func:random.Random": ("<code>random.Random(seed)</code> makes a random-number generator that repeats the same sequence for the same seed, so tests stay stable.", "import random\n", ["random.Random(1).randint(1, 6) == random.Random(1).randint(1, 6)"]),
    "method:.shuffle": ("<code>rng.shuffle(items)</code> shuffles a list in place.", "", []),
    "method:.uniform": ("<code>rng.uniform(a, b)</code> draws a random decimal between a and b.", "", []),
    "func:json.loads": ("<code>json.loads(text)</code> turns JSON text into Python dicts and lists (<code>import json</code>).", "import json\n", ['json.loads(\'{"a": [1, 2]}\')']),
    "func:pd.Series": ("<code>pd.Series(values, index=labels)</code> is a pandas column: values with labels.", "import pandas as pd\n", []),
    "func:pd.to_numeric": ("<code>pd.to_numeric(col, errors=\"coerce\")</code> turns text into numbers and bad values into NaN (missing).", "import pandas as pd\n", []),
    "method:.dropna": ("<code>df.dropna()</code> drops rows with missing values; <code>subset=[...]</code> checks only some columns.", "", []),
    "method:.reset_index": ("<code>.reset_index()</code> turns the index (row labels, often from a groupby) back into an ordinary column.", "", []),
    "method:.assign": ("<code>df.assign(new_col=values)</code> returns a copy of the table with a new column.", "", []),
    "method:.to_numpy": ("<code>.to_numpy()</code> turns a pandas column or table into a NumPy array.", "", []),
    "func:re.split": ("<code>re.split(pattern, text)</code> cuts text at every match of a pattern, like <code>split</code> with a pattern.", "import re\n", ['re.split(r"[,;]\\s*", "a, b;c")']),
    "func:np.quantile": ("<code>np.quantile(x, q)</code> is <code>np.percentile</code> with q from 0 to 1 instead of 0 to 100.", NP, ["np.quantile([1, 2, 3, 4, 100], 0.5)"]),
    "func:np.searchsorted": ("<code>np.searchsorted(sorted_x, v)</code> gives the position where <code>v</code> would be inserted to keep the array sorted.", NP, ["np.searchsorted(np.array([1, 3, 5]), 4)"]),
    "func:np.array_equal": ("<code>np.array_equal(a, b)</code> is True when two arrays have the same shape and values.", NP, ["np.array_equal(np.array([1, 2]), np.array([1, 2]))"]),
    "func:np.corrcoef": ("<code>np.corrcoef(x, y)</code> returns a 2 by 2 grid of correlations; the value at <code>[0, 1]</code> is the correlation of x with y, from -1 to 1.", NP, ["round(float(np.corrcoef([1, 2, 3], [2, 4, 7])[0, 1]), 3)"]),
    "func:np.ones_like": ("<code>np.ones_like(x)</code> makes ones with the same shape as <code>x</code>.", NP, ["np.ones_like(np.array([4, 5]))"]),
    "func:np.diag": ("<code>np.diag(m)</code> takes the values on the diagonal of a square grid.", NP, ["np.diag(np.array([[1, 2], [3, 4]]))"]),
    "func:np.stack": ("<code>np.stack([a, b])</code> puts arrays of the same length on top of each other as rows.", NP, ["np.stack([np.array([1, 2]), np.array([3, 4])])"]),
    "func:math.isnan": ("<code>math.isnan(x)</code> is True for NaN, the \"not a number\" value; NaN is not equal even to itself.", "import math\n", ['math.isnan(float("nan"))', 'float("nan") == float("nan")']),
    "func:recall_score": ("<code>recall_score(y_true, y_pred)</code> from <code>sklearn.metrics</code>: of the real positives, the share the model found.", "", []),
    "func:f1_score": ("<code>f1_score(y_true, y_pred)</code> from <code>sklearn.metrics</code>: one number balancing precision and recall.", "", []),
    "func:roc_auc_score": ("<code>roc_auc_score(y_true, scores)</code> from <code>sklearn.metrics</code>: how well the scores rank positives above negatives, 0.5 is random and 1 is perfect.", "", []),
    "func:average_precision_score": ("<code>average_precision_score(y_true, scores)</code> from <code>sklearn.metrics</code>: the area under the precision-recall curve, useful when positives are rare.", "", []),
    "func:RandomForestClassifier": ("<code>RandomForestClassifier(n_estimators=..., random_state=0)</code> from <code>sklearn.ensemble</code> trains many decision trees and lets them vote. Use <code>.fit(X, y)</code>, then <code>.predict(X)</code>.", "", []),
    "sql:MAX": ("<code>MAX(col)</code> in SQL is the largest value in a column (per group with GROUP BY); <code>MIN</code> the smallest.", "", []),
    "import:random": ("<code>import random</code> loads Python's random numbers; <code>random.Random(seed)</code> gives a generator that repeats for the same seed.", "", []),
    "sql:ROUND": ("<code>ROUND(x, n)</code> in SQL rounds to n decimals.", "", []),
    "sql:AVG": ("<code>AVG(col)</code> in SQL is the average of a column, per group with GROUP BY.", "", []),
    "sql:julianday": ("<code>julianday(t)</code> in SQLite turns a date-time into a day number, so <code>julianday(closed) - julianday(created)</code> is the time between them in days; times 24 gives hours.", "", []),
    "sql:COALESCE": ("<code>COALESCE(a, b)</code> in SQL gives <code>a</code>, or <code>b</code> when <code>a</code> is NULL.", "", []),
}

DOCS = {"builtin": "https://docs.python.org/3/library/functions.html#{n}", "np": "https://numpy.org/doc/stable/reference/generated/numpy.{n}.html",
        "re": "https://docs.python.org/3/library/re.html#re.{n}", "math": "https://docs.python.org/3/library/math.html#math.{n}",
        "str": "https://docs.python.org/3/library/stdtypes.html#str.{n}", "pd": "https://pandas.pydata.org/docs/reference/api/pandas.{n}.html",
        "sql": "https://www.sqlite.org/lang_corefunc.html", "py": "https://docs.python.org/3/search.html?q={n}"}


def label(f):
    kind, name = f.split(":", 1)
    return name if kind != "syntax" else name


def doc_link(f):
    kind, name = f.split(":", 1)
    n = name.lstrip(".")
    if kind == "builtin":
        u = DOCS["builtin"].format(n=n)
    elif kind == "func" and n.startswith("np."):
        u = DOCS["np"].format(n=n[3:])
    elif kind == "func" and n.startswith("re."):
        u = DOCS["re"].format(n=n[3:])
    elif kind == "func" and n.startswith("math."):
        u = DOCS["math"].format(n=n[5:])
    elif kind == "func" and n.startswith("pd."):
        u = DOCS["pd"].format(n=n[3:])
    elif kind == "sql":
        u = DOCS["sql"]
    else:
        u = DOCS["py"].format(n=n.split(".")[-1])
    return u


EVAL = r'''
import json, sys
out = []
for setup, exprs in json.load(open(sys.argv[1])):
    ns = {}
    exec(setup, ns)
    out.append([repr(eval(e, ns)) for e in exprs])
print(json.dumps(out))
'''


def evaluate():
    items = [(v[1], v[2]) for v in GLOSS.values()]
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "g.json"); json.dump(items, open(p, "w"))
        r = os.path.join(d, "e.py"); open(r, "w").write(EVAL)
        res = subprocess.run([sys.executable, "-I", r, p], capture_output=True, text=True, timeout=120)
        if res.returncode:
            raise SystemExit(res.stderr)
        vals = json.loads(res.stdout)
    return {f: list(zip(GLOSS[f][2], v)) for f, v in zip(GLOSS, vals)}


def note_html(f, examples):
    if f in GLOSS:
        h = GLOSS[f][0]
        ex = examples.get(f) or []
        if ex:
            h += "<br>" + "; ".join("<code>" + esc(e) + "</code> → <code>" + esc(v) + "</code>" for e, v in ex)
        return "<li>" + h + "</li>"
    return ('<li><code>' + esc(label(f)) + '</code> is not explained earlier in this course. '
            '<a href="' + doc_link(f) + '" target="_blank" rel="noopener">Read what it does</a> before you start.</li>')


def apply(iq, rows):
    """Add notes to questions outside the rewritten lessons. rows: the audit of the build without notes, in reading order."""
    examples = evaluate()
    skip = {"l1", "l2", "l4", "l5", "ph2-l6", "ph3-l1"}
    byid = {q["id"]: q for qs in iq.values() for q in qs}
    exnotes, seen, lessons, count, nfeat = {}, {}, set(), 0, 0
    for r in rows:
        if r["lesson"] in skip:
            continue
        done = seen.setdefault(r["lesson"], set())
        feats = [f for f in r["missing"] if f != "UNPLACED" and f not in done]
        if not feats:
            continue
        done.update(feats)
        box = '<p><b>New here</b> (not shown earlier in the course):</p><ul>' + "".join(note_html(f, examples) for f in feats) + "</ul>"
        if r["kind"] == "inline":
            q = byid[r["qid"]]
            q["before"] = (q.get("before") or "") + box
        else:
            exnotes[r["qid"]] = box
        count += 1; lessons.add(r["lesson"]); nfeat += len(feats)
    return iq, exnotes, {"count": count, "inline": count - len(exnotes), "exercises": len(exnotes), "lessons": len(lessons),
                         "features": nfeat, "glossary": len(GLOSS)}
