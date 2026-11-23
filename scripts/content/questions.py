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

# ---------------------------------------------------------------- ph2-l7 (v31)
def _db_q(fn, body_starter, body_solution, call):
    return (MAKE_DB + "\n\n" + fn + "\n" + body_starter + "\n\n" + call + "\n",
            MAKE_DB + "\n\n" + fn + "\n" + body_solution + "\n\n" + call + "\n")


_s, _sol = _db_q("def agency_names(conn):",
    '    sql = """SELECT r.id, a.name FROM requests AS r\n             JOIN agencies AS a ON a.code = r.agency\n             ORDER BY r.id"""   # keep every request: change the kind of join\n    return conn.execute(sql).fetchall()',
    '    sql = """SELECT r.id, a.name FROM requests AS r\n             LEFT JOIN agencies AS a ON a.code = r.agency\n             ORDER BY r.id"""\n    return conn.execute(sql).fetchall()',
    "print(agency_names(conn))")
_s2, _sol2 = _db_q("def days_open(conn):",
    '    sql = """SELECT id, ROUND(julianday(closed) - julianday(created), 1) AS days\n             FROM requests\n             ORDER BY id"""   # add the WHERE that keeps closed requests only\n    return conn.execute(sql).fetchall()',
    '    sql = """SELECT id, ROUND(julianday(closed) - julianday(created), 1) AS days\n             FROM requests\n             WHERE closed IS NOT NULL\n             ORDER BY id"""\n    return conn.execute(sql).fetchall()',
    "print(days_open(conn))")
_s3, _sol3 = _db_q("def avg_hours(conn):",
    '    sql = """WITH durations AS (\n               SELECT agency, (julianday(closed) - julianday(created)) * 24 AS hours\n               FROM requests WHERE closed IS NOT NULL\n             )\n             SELECT agency, ROUND(AVG(hours), 1) FROM durations\n             ORDER BY agency"""   # one row per agency: add the GROUP BY\n    return conn.execute(sql).fetchall()',
    '    sql = """WITH durations AS (\n               SELECT agency, (julianday(closed) - julianday(created)) * 24 AS hours\n               FROM requests WHERE closed IS NOT NULL\n             )\n             SELECT agency, ROUND(AVG(hours), 1) FROM durations\n             GROUP BY agency\n             ORDER BY agency"""\n    return conn.execute(sql).fetchall()',
    "print(avg_hours(conn))")
_s4, _sol4 = _db_q("def number_in_agency(conn):",
    '    sql = """SELECT agency, id,\n                    ROW_NUMBER() OVER (ORDER BY created) AS n\n             FROM requests\n             ORDER BY agency, n"""   # restart the numbering for each agency\n    return conn.execute(sql).fetchall()',
    '    sql = """SELECT agency, id,\n                    ROW_NUMBER() OVER (PARTITION BY agency ORDER BY created) AS n\n             FROM requests\n             ORDER BY agency, n"""\n    return conn.execute(sql).fetchall()',
    "print(number_in_agency(conn))")

ORDER["ph2-l7"] = [
    (new("q:ph2-l7-5", "Keep every request (guided)",
         "Write a function <code>agency_names(conn)</code> that returns <code>(id, name)</code> for every request, ordered by id, with the agency's full name from <code>agencies</code>. "
         "The query below uses an inner join, so request 4 (NYPD) is missing. Change one word so it comes back with <code>None</code> as its name.",
         "def agency_names(conn):", _s, _sol,
         [("All six requests", "rows = agency_names(conn)\nassert len(rows) == 6\n"),
          ("NYPD has no name", "assert agency_names(conn)[3] == (4, None)\n"),
          ("Names match", "assert agency_names(conn)[0] == (1, 'Transportation') and agency_names(conn)[1] == (2, 'Environment')\n")],
         hint="<code>LEFT JOIN</code> keeps every row of the table on the left (requests)."),
     dict(after="JOIN", level="guided")),
    ("q:ph2-l7-1", dict(after="JOIN", level="independent")),
    (new("q:ph2-l7-6", "Days open (guided)",
         "Write a function <code>days_open(conn)</code> that returns <code>(id, days)</code> for closed requests only, ordered by id, with days rounded to 1 decimal. "
         "The subtraction is done for you. Request 3 is still open, so its <code>closed</code> is <code>NULL</code> and its days come out as <code>None</code>: filter it out.",
         "def days_open(conn):", _s2, _sol2,
         [("Five closed requests", "assert [r[0] for r in days_open(conn)] == [1, 2, 4, 5, 6]\n"),
          ("Request 1 by hand", "assert days_open(conn)[0] == (1, 0.5)\n"),
          ("No None values", "assert all(d is not None for _, d in days_open(conn))\n")],
         hint="<code>WHERE closed IS NOT NULL</code> goes after <code>FROM requests</code>. <code>= NULL</code> never matches."),
     dict(after="Durations in SQLite", level="guided")),
    ("q:ph2-l7-2", dict(after="Durations in SQLite", level="independent")),
    (new("q:ph2-l7-7", "Average from a CTE (guided)",
         "Write a function <code>avg_hours(conn)</code> that returns <code>(agency, avg_hours)</code> per agency, ordered by agency, average rounded to 1 decimal. "
         "The <code>durations</code> CTE is written for you. The final <code>SELECT</code> averages over all rows at once; make it one row per agency.",
         "def avg_hours(conn):", _s3, _sol3,
         [("One row per agency", "assert avg_hours(conn) == [('DEP', 13.0), ('DOT', 30.0), ('NYPD', 1.0)]\n")],
         hint="Add <code>GROUP BY agency</code> before <code>ORDER BY</code>, the same as lesson 6."),
     dict(after="CTEs: name each step", level="guided")),
    ("q:ph2-l7-3", dict(after="CTEs: name each step", level="independent")),
    (new("q:ph2-l7-8", "Number inside each agency (guided)",
         "Write a function <code>number_in_agency(conn)</code> that returns <code>(agency, id, n)</code> where <code>n</code> counts each agency's requests in the order they were created, starting again at 1 for every agency. "
         "The window below numbers all six rows in one run; make it restart per agency.",
         "def number_in_agency(conn):", _s4, _sol4,
         [("Restarts per agency", "assert number_in_agency(conn) == [('DEP', 2, 1), ('DEP', 5, 2), ('DOT', 1, 1), ('DOT', 3, 2), ('DOT', 6, 3), ('NYPD', 4, 1)]\n")],
         hint="<code>PARTITION BY agency</code> goes inside <code>OVER (...)</code>, before <code>ORDER BY created</code>."),
     dict(after="Window functions", level="guided")),
    ("q:ph2-l7-4", dict(after="Window functions", level="independent")),
]

# ---------------------------------------------------------------- ph3-l2 (v31)
ORDER["ph3-l2"] = [
    (new("q:ph3-l2-5", "Dot product with a loop (guided)",
         "Write a function <code>dot_loop(a, b)</code> that returns the dot product of two lists of the same length. "
         "The loop walks both lists together; fill in the line that adds one product to the total. Check it by hand first: 3 × 0.5 + 1 × 2 + 2 × (−1) = 1.5.",
         "def dot_loop(a, b):",
         "def dot_loop(a, b):\n    total = 0\n    for x, y in zip(a, b):\n        pass   # replace pass: add x times y to total\n    return total\n\n\nprint(dot_loop([3.0, 1.0, 2.0], [0.5, 2.0, -1.0]))\n",
         "def dot_loop(a, b):\n    total = 0\n    for x, y in zip(a, b):\n        total = total + x * y\n    return total\n\n\nprint(dot_loop([3.0, 1.0, 2.0], [0.5, 2.0, -1.0]))\n",
         [("The lesson's vectors", "assert dot_loop([3.0, 1.0, 2.0], [0.5, 2.0, -1.0]) == 1.5\n"),
          ("Small whole numbers", "assert dot_loop([1, 2], [3, 4]) == 11\n"),
          ("Opposite signs cancel", "assert dot_loop([1, -1], [1, 1]) == 0\n")],
         hint="<code>total = total + x * y</code> inside the loop."),
     dict(after="Dot product", level="guided")),
    ("q:ph3-l2-1", dict(after="Dot product", level="independent")),
    ("q:ph3-l2-2", dict(after="A whole dataset at once", level="independent")),
    (new("q:ph3-l2-6", "Length of a vector (guided)",
         "Write a function <code>length(v)</code> that returns the length of a list of numbers: the square root of the sum of the squares. "
         "The squares are summed for you. By hand for [3, 4]: 9 + 16 = 25, and the square root of 25 is 5.",
         "def length(v):",
         "import math\n\n\ndef length(v):\n    total = sum(x * x for x in v)\n    return total   # take the square root with math.sqrt\n\n\nprint(length([3, 4]))\n",
         "import math\n\n\ndef length(v):\n    total = sum(x * x for x in v)\n    return math.sqrt(total)\n\n\nprint(length([3, 4]))\n",
         [("3, 4, 5", "assert length([3, 4]) == 5.0\n"), ("Three numbers", "assert length([1, 2, 2]) == 3.0\n"),
          ("Matches NumPy", "import numpy as np\nassert abs(length([0.3, -1.2, 2.5]) - np.linalg.norm([0.3, -1.2, 2.5])) < 1e-12\n")],
         hint="<code>math.sqrt(total)</code> is the square root."),
     dict(after="Length and direction", level="guided")),
    ("q:ph3-l2-3", dict(after="Length and direction", level="independent")),
    (new("q:ph3-l2-7", "Cosine of two vectors (guided)",
         "Write a function <code>cosine(a, b)</code> that returns the cosine similarity of two NumPy vectors: their dot product divided by the product of their lengths. "
         "The dot product is done for you. By hand for [1, 0] and [1, 1]: the dot product is 1, the lengths are 1 and 1.414, so the cosine is about 0.707.",
         "def cosine(a, b):",
         "import numpy as np\n\n\ndef cosine(a, b):\n    top = a @ b\n    return top   # divide by np.linalg.norm(a) * np.linalg.norm(b)\n\n\nprint(round(cosine(np.array([1.0, 0.0]), np.array([1.0, 1.0])), 3))\n",
         "import numpy as np\n\n\ndef cosine(a, b):\n    top = a @ b\n    return top / (np.linalg.norm(a) * np.linalg.norm(b))\n\n\nprint(round(cosine(np.array([1.0, 0.0]), np.array([1.0, 1.0])), 3))\n",
         [("45 degrees", "assert abs(cosine(np.array([1.0, 0.0]), np.array([1.0, 1.0])) - 0.70710678) < 1e-6\n"),
          ("Same direction, different length", "assert abs(cosine(np.array([1.0, 2.0]), np.array([3.0, 6.0])) - 1.0) < 1e-12\n"),
          ("Opposite", "assert abs(cosine(np.array([1.0, 0.0]), np.array([-2.0, 0.0])) + 1.0) < 1e-12\n")],
         hint="Put the product of the two lengths in brackets: <code>top / (np.linalg.norm(a) * np.linalg.norm(b))</code>."),
     dict(after="Cosine similarity", level="guided")),
    ("q:ph3-l2-4", dict(after="Cosine similarity", level="independent")),
]
