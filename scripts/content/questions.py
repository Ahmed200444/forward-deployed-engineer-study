"""Inline question changes for the priority lessons (v30).

ORDER[lesson] lists every question of the lesson in reading order. Each entry is either an existing
question id with the fields to change, or a new question (NEW). Ids never change, so saved drafts
(state.drafts[id]) and passes (state.qpass[id]) carry over. A changed starter only shows for people
who have no draft yet.

Fields: level (guided | independent | challenge), optional (moves it into Optional practice),
before (HTML shown above the question), prereq ([(route, label)] links), after (the heading it follows).
"""

def L(lid, title):
    return ("#/lesson/" + lid, title)

L1 = L("l1", "How the coding questions work (lesson 1)")
L2 = L("l2", "Values, names and strings")
L3 = L("l3", "Functions")
L4 = L("l4", "Lists, dicts and loops")
L5 = L("l5", "Files and errors")

NEW = {}

def new(qid, title, problem, sig, starter, solution, tests, hint="", files=None):
    NEW[qid] = {"id": qid, "title": title, "problem": problem, "sig": sig, "starter": starter, "solution": solution,
                "tests": [{"name": n, "code": c} for n, c in tests], "hint": hint, "files": files or {}}
    return qid


ORDER = {}

# ---------------------------------------------------------------- l1
ORDER["l1"] = [
    ("q:l1-1", dict(after="How the coding questions work", level="guided", starter='''def tool_for(job):
    if job in ("move between folders", "read error messages"):
        return "PowerShell"
    # add an if for the two uv jobs, and one for "write code", like the lines above
    return "unknown"


print(tool_for("run tests"))
''')),
    ("q:l1-6", dict(level="independent")),
    ("q:l1-10", dict(level="independent")),
    ("q:l1-8", dict(level="independent", optional=True, solution='''def file_role(name):
    if name == "pyproject.toml":
        return "what the project needs"
    if name == "uv.lock":
        return "exact versions"
    if name == ".venv":
        return "installed packages"
    if name.endswith(".py"):
        return "your code"
    return "other"


print(file_role("uv.lock"))
''')),
    ("q:l1-9", dict(level="independent", optional=True)),
    ("q:l1-2", dict(level="challenge", optional=True, prereq=[L2, L4],
                    before="<p><b>New here:</b> <code>path.split(\"\\\\\")</code> cuts the path into a list of folder names at each backslash, "
                           "<code>parts[:-1]</code> is the list without its last item, <code>parts.append(name)</code> adds one, and "
                           "<code>\"\\\\\".join(parts)</code> glues the list back together. Lessons 2 and 4 teach these; come back after them if this is hard.</p>")),
    ("q:l1-3", dict(level="challenge", optional=True, prereq=[L2, L4],
                    before="<p><b>New here:</b> a list is written <code>[\"a\", \"b\"]</code>, and <code>f\"uv init {name}\"</code> puts the value of <code>name</code> into the text. Both are taught in lessons 2 and 4.</p>")),
    ("q:l1-4", dict(level="challenge", optional=True, prereq=[L4],
                    before="<p><b>New here:</b> the answer loops over a list and keeps some items. Lesson 4 teaches that loop and the one-line list comprehension.</p>")),
    ("q:l1-5", dict(level="challenge", optional=True, prereq=[L2, L5],
                    before="<p><b>New here:</b> <code>raise ValueError(\"message\")</code> stops the function with an error (lesson 5), and <code>f\"uv run python {filename}\"</code> builds the text (lesson 2).</p>")),
    ("q:l1-7", dict(level="challenge", optional=True, prereq=[L4],
                    before="<p><b>New here:</b> <code>for cmd in commands:</code> runs the indented lines once per command. Lesson 4 teaches loops; remember a True/False in a variable such as <code>seen_pwd</code>.</p>")),
]

# ---------------------------------------------------------------- l2
ORDER["l2"] = [
    ("q:l2-6", dict(after="Part 1: Values and variables", level="guided", starter='''def count_after(start, steps):
    count = start
    for _ in range(steps):
        pass  # replace pass: add 1 to count
    return count


print(count_after(3, 4))
''')),
    (new("q:l2-14", "Add the same amount each time",
         "Write a function <code>add_each_time(start, steps, amount)</code> that starts a variable at <code>start</code>, adds <code>amount</code> to it <code>steps</code> times in a loop, and returns it.",
         "def add_each_time(start, steps, amount):",
         "def add_each_time(start, steps, amount):\n    # your code here\n    pass\n\n\nprint(add_each_time(10, 3, 5))\n",
         "def add_each_time(start, steps, amount):\n    total = start\n    for _ in range(steps):\n        total = total + amount\n    return total\n\n\nprint(add_each_time(10, 3, 5))\n",
         [("Adds three times", "assert add_each_time(10, 3, 5) == 25\n"), ("Decimals", "assert add_each_time(0, 4, 2.5) == 10.0\n"),
          ("No steps", "assert add_each_time(7, 0, 100) == 7\n")],
         hint="Same shape as the last question: set a variable to <code>start</code>, loop <code>steps</code> times, add <code>amount</code> each time, return it."),
     dict(after="Part 1: Values and variables", level="independent")),
    ("q:l2-1", dict(after="Part 1: Values and variables", level="independent")),
    ("q:l2-7", dict(after="Part 2: f-strings", level="guided", starter='''def price_tag(item, price):
    return f"{item}: ${price}"   # add a format so 2.5 shows as 2.50


print(price_tag("Tea", 2.5))
''')),
    ("q:l2-2", dict(after="Part 2: f-strings", level="independent")),
    ("q:l2-3", dict(after="Part 3a: Cleaning text", level="guided", starter='''def is_yes(answer):
    cleaned = answer.strip()   # also make it lower case
    return cleaned in ("yes", "y")


print(is_yes("  YES "))
''')),
    ("q:l2-13", dict(after="Part 3b: Splitting and joining", level="guided", starter='''def both_splits(text):
    any_spaces = len(text.split())
    single_space = 0   # replace 0: count the parts from text.split(" ")
    return any_spaces, single_space


print(both_splits("a  b"))
''')),
    ("q:l2-8", dict(after="Part 3c: Indexes and slices", level="guided", starter='''def ends(word):
    if word == "":
        return ""
    return word[0]   # add the last letter


print(ends("hello"))
''')),
    ("q:l2-9", dict(after="Part 3c: Indexes and slices", level="independent")),
    ("q:l2-11", dict(after="Part 3d: Replacing and repeating", level="independent")),
    ("q:l2-5", dict(after="Chaining", level="independent")),
    ("q:l2-12", dict(level="challenge", optional=True, prereq=[L4],
                     before="<p><b>New here:</b> the neatest answer is a list comprehension, <code>[w.lower() for w in words]</code>, from lesson 4. A loop that appends to a new list works too.</p>")),
    ("q:l2-10", dict(level="challenge", optional=True, prereq=[L4],
                     before="<p><b>New here:</b> split first, then clean every part with a list comprehension (lesson 4): <code>[part.strip() for part in parts]</code>.</p>")),
    ("q:l2-4", dict(level="challenge", optional=True, prereq=[L4],
                    before="<p><b>New here:</b> <code>\"\".join(...)</code> can take a loop written inside the brackets, called a generator expression: "
                           "<code>\"\".join(w[0] for w in words)</code> joins the first letter of every word. Lesson 4 covers the same idea as a list comprehension.</p>")),
]

# ---------------------------------------------------------------- l4
ORDER["l4"] = [
    ("q:l4-1", dict(after="Part 1: Lists and the append loop", level="guided", starter='''def evens(numbers):
    result = []
    for n in numbers:
        pass   # replace pass: if n is even, append it to result
    return result


print(evens([1, 2, 3, 4, 5, 6]))
''')),
    ("q:l4-2", dict(after="Part 1b: Keeping a running total", level="independent")),
    ("q:l4-7", dict(after="Part 2: Numbering and comprehensions", level="independent")),
    ("q:l4-8", dict(after="Part 2: Numbering and comprehensions", level="independent")),
    ("q:l4-9", dict(after="Part 3: Dicts: look up by key", level="guided", starter='''def bill(menu, order):
    total = 0
    for item in order:
        pass   # replace pass: add this item's price (0 if it is not on the menu)
    return total


print(bill({"tea": 2, "cake": 3}, ["tea", "cake", "tea", "soup"]))
''')),
    ("q:l4-3", dict(after="Dicts: counting", level="independent")),
    ("q:l4-4", dict(after="Part 4: Grouping into lists", level="independent")),
    ("q:l4-5", dict(after="Sorting with a key", level="guided", starter='''def sort_by_length(words):
    return sorted(words, key=lambda w: len(w))   # make ties sort a-z


print(sort_by_length(["pear", "fig", "kiwi", "apple"]))
''')),
    ("q:l4-10", dict(after="Sorting with a key", level="independent")),
    ("q:l4-6", dict(after="Choosing a structure", level="independent")),
    ("q:l4-12", dict(level="independent", optional=True)),
    ("q:l4-11", dict(level="challenge", optional=True,
                     before="<p>This one combines counting (Dicts: counting) with sorting (Sorting with a key). <code>if not counts:</code> is true for an empty dict.</p>")),
]

# ---------------------------------------------------------------- l5
ORDER["l5"] = [
    ("q:l5-1", dict(after="Part 1: Reading a file", level="guided", starter='''def count_lines(path):
    count = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            pass   # replace pass: add 1 to count when the line has text
    return count


print(count_lines("notes.txt"))
''')),
    ("q:l5-6", dict(after="Whole-file helpers: pathlib", level="independent")),
    ("q:l5-2", dict(after="Whole-file helpers: pathlib", level="independent")),
    ("q:l5-3", dict(after="Part 2: When the data is wrong", level="guided", starter='''def to_int(text, default=0):
    try:
        return int(text)
    except ValueError:
        pass   # replace pass: return the default instead


print(to_int("abc", -1))
''')),
    ("q:l5-4", dict(after="Part 2: When the data is wrong", level="independent")),
    ("q:l5-5", dict(after="Raising your own errors", level="independent")),
    ("q:l5-8", dict(after="Part 3: Writing a file", level="independent")),
    ("q:l5-7", dict(level="independent", optional=True, prereq=[L4],
                    before="<p><b>New here:</b> <code>sorted(n for n in names if ...)</code> sorts only the names that pass the test, like a list comprehension (lesson 4).</p>")),
    ("q:l5-9", dict(level="independent", optional=True,
                    before="<p><b>New here:</b> dividing by zero raises <code>ZeroDivisionError: division by zero</code>. Catch it the same way as <code>ValueError</code>.</p>")),
    ("q:l5-10", dict(level="challenge", optional=True,
                     before="<p><b>New here:</b> <code>line.split(\"=\", 1)</code> splits at the first <code>=</code> only, so <code>\"a = b = c\"</code> gives <code>['a ', ' b = c']</code>. "
                            "<code>name, value = parts</code> puts the two items into two names. <code>if not name:</code> is true for an empty string.</p>")),
]

# ---------------------------------------------------------------- ph2-l6
MAKE_DB = '''import sqlite3


def make_db():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE requests (id INTEGER, agency TEXT, borough TEXT, complaint TEXT, created TEXT, closed TEXT)")
    conn.executemany("INSERT INTO requests VALUES (?, ?, ?, ?, ?, ?)", [
        (1, "DOT", "BRONX", "Pothole", "2024-01-01 08:00", "2024-01-01 20:00"),
        (2, "DEP", "QUEENS", "Noise", "2024-01-01 09:00", "2024-01-01 11:00"),
        (3, "DOT", "BRONX", "Pothole", "2024-01-02 10:00", None),
        (4, "NYPD", "BRONX", "Noise", "2024-01-02 11:00", "2024-01-02 12:00"),
        (5, "DEP", None, "Water", "2024-01-03 12:00", "2024-01-04 12:00"),
        (6, "DOT", "QUEENS", "Streetlight", "2024-01-03 13:00", "2024-01-05 13:00"),
    ])
    conn.execute("CREATE TABLE agencies (code TEXT, name TEXT)")
    conn.executemany("INSERT INTO agencies VALUES (?, ?)", [("DOT", "Transportation"), ("DEP", "Environment")])
    return conn


conn = make_db()
'''
ORDER["ph2-l6"] = [
    (new("q:ph2-l6-4", "Count per agency (guided)",
         "Using the six-row table, write a function <code>count_by_agency(conn)</code> that returns one row <code>(agency, n)</code> per agency: how many requests it has, most first, ties in a-z order. "
         "The query below is nearly done; it is missing the clause that makes one row per agency.",
         "def count_by_agency(conn):",
         MAKE_DB + '''

def count_by_agency(conn):
    sql = "SELECT agency, COUNT(*) AS n FROM requests ORDER BY n DESC, agency"   # add the GROUP BY
    return conn.execute(sql).fetchall()


print(count_by_agency(conn))
''',
         MAKE_DB + '''

def count_by_agency(conn):
    sql = "SELECT agency, COUNT(*) AS n FROM requests GROUP BY agency ORDER BY n DESC, agency"
    return conn.execute(sql).fetchall()


print(count_by_agency(conn))
''',
         [("One row per agency", 'assert count_by_agency(conn) == [("DOT", 3), ("DEP", 2), ("NYPD", 1)]\n'),
          ("Ties a-z", 'c2 = make_db()\nc2.execute("INSERT INTO requests VALUES (7, \'NYPD\', \'BRONX\', \'Noise\', \'2024-01-04 09:00\', NULL)")\n'
                       'assert count_by_agency(c2) == [("DOT", 3), ("DEP", 2), ("NYPD", 2)]\n')],
         hint="<code>GROUP BY</code> goes after <code>FROM requests</code> and before <code>ORDER BY</code>. Group by the column you want one row for."),
     dict(after="SQLite from Python", level="guided")),
    ("q:ph2-l6-1", dict(after="SQLite from Python", level="independent")),
    ("q:ph2-l6-2", dict(after="NULL is not a value", level="independent")),
    ("q:ph2-l6-3", dict(level="challenge", optional=True,
                        before="<p><b>New here:</b> after <code>cur = conn.execute(sql)</code>, <code>cur.description</code> describes the result columns: one tuple per column, and the first item of each is the column name. "
                               "For <code>SELECT id, agency ...</code> the names are <code>['id', 'agency']</code>. <code>dict(zip(names, row))</code> pairs each name with the value in the same position: "
                               "<code>dict(zip(['id', 'agency'], (1, 'DOT')))</code> is <code>{'id': 1, 'agency': 'DOT'}</code>.</p>")),
]

# ---------------------------------------------------------------- ph3-l1
ORDER["ph3-l1"] = [
    ("q:ph3-l1-1", dict(after="The simplest model", level="guided", starter='''def predict_all(xs, w, b):
    predictions = []
    for x in xs:
        pass   # replace pass: work out w * x + b and append it
    return predictions


print(predict_all([0, 10], 2.0, 5.0))
''')),
    (new("q:ph3-l1-4", "The slope from two points (guided)",
         "Write a function <code>slope(x1, y1, x2, y2)</code> that returns the slope <code>w</code> of the line through two points: the rise (how far y moves) divided by the run (how far x moves). "
         "The rise is done for you. Check it by hand first: for (2, 1) and (6, 9), the rise is 8 and the run is 4.",
         "def slope(x1, y1, x2, y2):",
         "def slope(x1, y1, x2, y2):\n    rise = y2 - y1\n    run = 1   # replace 1: how far x moves from the first point to the second\n    return rise / run\n\n\nprint(slope(2, 1, 6, 9))\n",
         "def slope(x1, y1, x2, y2):\n    rise = y2 - y1\n    run = x2 - x1\n    return rise / run\n\n\nprint(slope(2, 1, 6, 9))\n",
         [("Up the line", "assert slope(2, 1, 6, 9) == 2.0\n"), ("Down the line", "assert slope(0, 4, 2, 0) == -2.0\n"),
          ("The lesson's points", "assert slope(1, 3, 4, 9) == 2.0\n")],
         hint="The run is the second x minus the first x, the same order as the rise."),
     dict(after="Find the knobs from two points", level="guided")),
    ("q:ph3-l1-2", dict(after="Find the knobs from two points", level="independent")),
    (new("q:ph3-l1-5", "Two features (guided)",
         "Write a function <code>predict_two(x1, x2, w1, w2, b)</code> that returns the prediction for two features: <code>w1*x1 + w2*x2 + b</code>. "
         "Work the printed example by hand first: 3 × 1 + 0.5 × 4 − 1.",
         "def predict_two(x1, x2, w1, w2, b):",
         "def predict_two(x1, x2, w1, w2, b):\n    return w1 * x1 + b   # add the second feature's term\n\n\nprint(predict_two(1, 4, 3, 0.5, -1))\n",
         "def predict_two(x1, x2, w1, w2, b):\n    return w1 * x1 + w2 * x2 + b\n\n\nprint(predict_two(1, 4, 3, 0.5, -1))\n",
         [("The lesson's example", "assert predict_two(3, 2, 0.5, 2, 1) == 6.5\n"), ("Another one", "assert predict_two(1, 4, 3, 0.5, -1) == 4.0\n"),
          ("Only the bias", "assert predict_two(0, 0, 5, 5, 2) == 2\n")],
         hint="Each feature is multiplied by its own weight: <code>w2 * x2</code> is the missing term."),
     dict(after="Many inputs", level="guided")),
    ("q:ph3-l1-3", dict(after="Many inputs", level="independent",
                        before="<p>Raising <code>ValueError</code> is covered in <a href=\"#/lesson/l5\">Files and errors</a>; the lengths check comes first, then the sum. The reference solution wraps the result in <code>round(total, 10)</code>, because decimal sums leave tiny errors: <code>0.1 + 0.2</code> is <code>0.30000000000000004</code>.</p>")),
]
