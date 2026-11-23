"""v31 teach-before-you-ask rewrites: SQL joins, durations, CTEs and window functions (ph2-l7), and vectors (ph3-l2).
Same markers as lessons.py. Every rows table and output is produced by running the block at build time."""
from lessons import PATH_NOTE, TOY_DB, trace

TOY_DB2 = TOY_DB + '''conn.execute("CREATE TABLE agencies (code TEXT, name TEXT)")
conn.executemany("INSERT INTO agencies VALUES (?, ?)", [("DOT", "Transportation"), ("DEP", "Environment")])
'''
NOTE2 = "The six-row requests table from lesson 6 plus an agencies table with two rows (DOT and DEP). NYPD has no row in agencies."


def sql(code, caption=None):
    b = {"mode": "sql", "setup": TOY_DB2, "note": NOTE2, "code": code}
    if caption:
        b["caption"] = caption
    return b


PH2L7 = '''<p class="lede">Joins combine tables, CTEs name intermediate steps, and window functions rank or compare rows inside groups without collapsing them.</p>
''' + PATH_NOTE.format(parts="It has four parts: joins, durations, CTEs and window functions. Every step runs on the same six requests from lesson 6, and you see the rows it returns.", extra="") + '''
<h2>JOIN</h2>
<p>A join puts rows from two tables side by side when a key matches. Here the key is the agency code: <code>requests.agency</code> holds DOT, DEP or NYPD, and <code>agencies.code</code> holds the code with the agency's full name. The agencies table has only two rows:</p>
[[code j0]]
[[rows j0]]
<p><b>Inner join.</b> <code>JOIN agencies AS a ON a.code = r.agency</code> pairs each request with the agency row whose code matches. Request 4 is NYPD, and there is no NYPD row, so it has no partner and drops out: 6 requests in, 5 rows out.</p>
[[code j1]]
[[rows j1]]
<p><b>Left join.</b> <code>LEFT JOIN</code> keeps every row of the left table (requests). When there is no match, the columns from the right table are <code>NULL</code>. Request 4 is back, with no name.</p>
[[code j2]]
[[rows j2]]
''' + trace("Which rows survive", ["Join", "Request 4 (NYPD)", "Rows"], [["JOIN (inner)", "dropped: no matching agency", "5"], ["LEFT JOIN", "kept, name is NULL", "6"]]) + '''
<p>Then you can group the joined rows like any table. This counts the requests per agency name; NYPD's request is not counted because the inner join dropped it, so 5 of the 6 requests are counted:</p>
[[keep 0]]
[[rows 0]]
<p>A missing match is easy to miss: an inner join silently shrinks your data. When the row count matters, count before and after the join, as the next two questions do.</p>
<h2>Durations in SQLite</h2>
<p>SQLite stores these timestamps as text, so you cannot subtract them directly. <code>julianday(t)</code> turns a timestamp into a day number with a fraction for the time of day: 18:00 is three quarters of the way through a day, so it ends in .75.</p>
[[code d1]]
[[rows d1]]
<p>By hand for request 1: it was created at 08:00 and closed at 20:00 on the same day.</p>
''' + trace("By hand: request 1", ["Step", "Working", "Result"],
            [["1. Day numbers", "2460310.8333 (08:00) and 2460311.3333 (20:00)", ""], ["2. Subtract", "2460311.3333 − 2460310.8333", "0.5 days"],
             ["3. Times 24", "0.5 × 24", "12 hours"]]) + '''
<p>The day numbers are decimals, so the subtraction leaves tiny errors: 2 hours comes out as 2.0000000037. Request 3 is still open, so <code>closed</code> is NULL and so is its duration.</p>
[[code d2]]
[[rows d2]]
<p><code>ROUND(x, 1)</code> hides the noise, and <code>WHERE closed IS NOT NULL</code> drops the open request:</p>
[[code d3]]
[[rows d3]]
<p>The expression to remember (it is a piece of a query, not a whole one):</p>
[[keep 1]]
<h2>CTEs: name each step</h2>
<p>A CTE (common table expression) gives a query a name with <code>WITH name AS (...)</code>, so the next query can read from it like a table. Build it in two steps and check the rows of each.</p>
<p><b>Step 1</b> is the durations query from the last part, named <code>durations</code>. On its own, <code>SELECT * FROM durations</code> shows exactly its rows:</p>
[[code c1]]
[[rows c1]]
<p><b>Step 2</b> groups those rows by agency. DOT has 12 and 48 hours, so its average is 30. DEP has 2 and 24, average 13. NYPD has 1.</p>
[[code c2]]
[[rows c2]]
<p>The same pattern works for any first step. This CTE counts requests per borough and complaint, and the outer query keeps the pairs with at least 2. Only BRONX potholes qualify:</p>
[[keep 2]]
[[rows 2]]
<p>Written as one nested query, the same steps are harder to read. A CTE reads top to bottom like a pipeline. When a number looks wrong, run the CTE's own <code>SELECT</code> and look at its rows, as above.</p>
<h2>Window functions</h2>
<p><code>GROUP BY</code> collapses each group into one row. A window function keeps every row and adds a value computed over a group of rows, its window. <code>ROW_NUMBER() OVER (PARTITION BY borough ORDER BY n DESC, complaint)</code> numbers the rows 1, 2, 3, ... inside each borough, biggest count first.</p>
<p><b>Step 1</b>, the counts per borough and complaint (row 5 has no borough, so it is left out):</p>
[[code w1]]
[[rows w1]]
<p><b>Step 2</b>, number the rows inside each borough. <code>PARTITION BY borough</code> restarts the numbering for each borough. In QUEENS, Noise and Streetlight both have 1, so <code>complaint</code> breaks the tie a to z and Noise is first.</p>
[[code w2]]
[[rows w2]]
<p><b>Step 3</b>, keep the first row of each borough. A window function cannot go in <code>WHERE</code> (it is worked out after <code>WHERE</code>), so the numbering goes in a CTE and the outer query filters on it:</p>
[[code w3]]
[[rows w3]]
<p><b>RANK and ROW_NUMBER.</b> They differ only on ties. Order by the count alone, and Noise and Streetlight in QUEENS tie: <code>ROW_NUMBER</code> still gives them 1 and 2 (which one gets 1 is not defined), while <code>RANK</code> gives both 1.</p>
[[code w4]]
[[rows w4]]
<p>The numbering step on its own, as you will write it in the questions (it reads from a <code>counts</code> CTE like the one above):</p>
[[keep 3]]
[[rows 3]]
<h2>Check yourself</h2>
<ul><li>What happens to requests with no matching agency in an inner join?</li><li>What is the difference between RANK and ROW_NUMBER?</li></ul>
'''

PH2L7_BLOCKS = {
    "j0": sql("SELECT * FROM agencies;\n", "The agencies table"),
    "j1": sql("SELECT r.id, r.agency, a.name\nFROM requests AS r\nJOIN agencies AS a ON a.code = r.agency\nORDER BY r.id;\n", "Rows after the inner join"),
    "j2": sql("SELECT r.id, r.agency, a.name\nFROM requests AS r\nLEFT JOIN agencies AS a ON a.code = r.agency\nORDER BY r.id;\n", "Rows after the left join"),
    "d1": sql("SELECT id, created, closed,\n       julianday(created) AS start_day,\n       julianday(closed) AS end_day\nFROM requests\nORDER BY id;\n", "Day numbers"),
    "d2": sql("SELECT id, (julianday(closed) - julianday(created)) * 24 AS hours\nFROM requests\nORDER BY id;\n", "Hours, before rounding"),
    "d3": sql("SELECT id, ROUND((julianday(closed) - julianday(created)) * 24, 1) AS hours\nFROM requests\nWHERE closed IS NOT NULL\nORDER BY id;\n", "Hours, rounded, closed requests only"),
    "c1": sql("WITH durations AS (\n    SELECT agency, (julianday(closed) - julianday(created)) * 24 AS hours\n    FROM requests\n    WHERE closed IS NOT NULL\n)\nSELECT agency, ROUND(hours, 1) AS hours FROM durations;\n", "Rows of the CTE"),
    "c2": sql("WITH durations AS (\n    SELECT agency, (julianday(closed) - julianday(created)) * 24 AS hours\n    FROM requests\n    WHERE closed IS NOT NULL\n)\nSELECT agency, ROUND(AVG(hours), 1) AS avg_hours\nFROM durations\nGROUP BY agency\nORDER BY agency;\n", "Rows after grouping the CTE"),
    "w1": sql("SELECT borough, complaint, COUNT(*) AS n\nFROM requests\nWHERE borough IS NOT NULL\nGROUP BY borough, complaint\nORDER BY borough, n DESC, complaint;\n", "Counts per borough and complaint"),
    "w2": sql("WITH counts AS (\n    SELECT borough, complaint, COUNT(*) AS n\n    FROM requests\n    WHERE borough IS NOT NULL\n    GROUP BY borough, complaint\n)\nSELECT borough, complaint, n,\n       ROW_NUMBER() OVER (PARTITION BY borough ORDER BY n DESC, complaint) AS rnk\nFROM counts\nORDER BY borough, rnk;\n", "Rows numbered inside each borough"),
    "w3": sql("WITH counts AS (\n    SELECT borough, complaint, COUNT(*) AS n\n    FROM requests\n    WHERE borough IS NOT NULL\n    GROUP BY borough, complaint\n), ranked AS (\n    SELECT borough, complaint, n,\n           ROW_NUMBER() OVER (PARTITION BY borough ORDER BY n DESC, complaint) AS rnk\n    FROM counts\n)\nSELECT borough, complaint, n\nFROM ranked\nWHERE rnk = 1\nORDER BY borough;\n", "The top complaint per borough"),
    "w4": sql("WITH counts AS (\n    SELECT borough, complaint, COUNT(*) AS n\n    FROM requests\n    WHERE borough = 'QUEENS'\n    GROUP BY borough, complaint\n)\nSELECT complaint, n,\n       RANK() OVER (ORDER BY n DESC) AS rank_no\nFROM counts\nORDER BY rank_no, complaint;\n", "RANK on a tie in QUEENS"),
}

# ---------------------------------------------------------------- ph3-l2
PH3L2 = '''<p class="lede">A row of features is a vector. A dataset is a matrix. A linear model is a dot product. Comparing embeddings is cosine similarity.</p>
''' + PATH_NOTE.format(parts="It has four parts: the dot product, a whole dataset at once, length, and cosine similarity. Each calculation is done by hand first, then in code; the last part also draws the vectors.", extra="") + '''
<h2>Dot product</h2>
<p>A dot product multiplies matching positions of two vectors and adds the results. It is the weighted sum from lesson 1: <code>x</code> holds one request's features and <code>w</code> one weight per feature.</p>
''' + trace("By hand: x = [3, 1, 2] and w = [0.5, 2, −1]", ["Position", "x", "w", "x × w"],
            [["1", "3", "0.5", "1.5"], ["2", "1", "2", "2"], ["3", "2", "−1", "−2"], ["Sum", "", "", "1.5 + 2 − 2 = 1.5"]]) + '''
<p>In NumPy, <code>@</code> does the same multiply-and-add:</p>
[[keep 0]]
[[out 0]]
<h2>A whole dataset at once</h2>
<p>Stack several rows of features and you have a matrix <code>X</code>. <code>X @ w</code> does one dot product per row, so you get one prediction per row. By hand, adding the bias 0.1:</p>
''' + trace("By hand: X @ w + 0.1, one row at a time", ["Row", "Features", "Dot product with w = [0.5, 2, −1]", "+ 0.1"],
            [["1", "[3, 1, 2]", "1.5 + 2 − 2 = 1.5", "1.6"], ["2", "[1, 0, 4]", "0.5 + 0 − 4 = −3.5", "−3.4"]]) + '''
[[keep 1]]
[[out 1]]
<p>The shapes must line up: <code>X</code> is 2 rows by 3 features, shape (2, 3), and <code>w</code> has 3 weights, shape (3,). The 3s must match, and the result has one value per row, shape (2,). Most shape errors you will meet in ML are this rule being broken:</p>
[[code s1]]
[[out s1]]
<h2>Length and direction</h2>
<p>The length (norm) of a vector is the distance from the origin to its tip: square each number, add them up, take the square root. This is Pythagoras, and it works the same in any number of dimensions.</p>
''' + trace("By hand: the length of [3, 4]", ["Step", "Working", "Result"],
            [["1. Square each number", "3² and 4²", "9 and 16"], ["2. Add them", "9 + 16", "25"], ["3. Square root", "√25", "5"]]) + '''
<p>In NumPy, <code>np.linalg.norm</code> does all three steps in one call. For the lesson's <code>x = [3, 1, 2]</code> it is √(9 + 1 + 4) = √14 ≈ 3.74. The line below only computes the value; a script shows nothing until you print it, as the next block does.</p>
[[keep 2]]
<p>Divide a vector by its length and you get a vector of length 1 pointing the same way, called a unit vector: <code>[3, 4] / 5</code> is <code>[0.6, 0.8]</code>. The block checks all three numbers from the table:</p>
[[code n1]]
[[out n1]]
<h2>Cosine similarity</h2>
<p>Cosine similarity compares directions: the dot product divided by both lengths. 1 means the same direction, 0 means at right angles (unrelated), −1 means opposite. Length does not matter, only direction.</p>
''' + trace("By hand: a = [1, 0] against three vectors", ["b", "a · b", "|a|", "|b|", "cosine = a · b ÷ (|a| × |b|)"],
            [["[1, 1]", "1×1 + 0×1 = 1", "1", "√2 ≈ 1.414", "1 ÷ 1.414 ≈ 0.707"],
             ["[2, 2]", "1×2 + 0×2 = 2", "1", "√8 ≈ 2.828", "2 ÷ 2.828 ≈ 0.707"],
             ["[0, 1]", "1×0 + 0×1 = 0", "1", "1", "0 ÷ 1 = 0"],
             ["[−1, 0]", "1×(−1) + 0×0 = −1", "1", "1", "−1 ÷ 1 = −1"]]) + '''
<p>[1, 1] and [2, 2] point the same way, so they get the same cosine even though one is twice as long. The code below computes the same numbers and draws the vectors:</p>
[[keep 3]]
<p>The next block uses the same function on the four vectors from the table, then labels each arrow with its cosine:</p>
[[code k1]]
[[out k1]]
<p>In Phase 7 you will turn documents into vectors (embeddings) and use exactly this to find the ones closest to a question.</p>
<h2>Check yourself</h2>
<ul><li>What is [1, 2] @ [3, 4]?</li><li>Why does cosine similarity ignore vector length?</li></ul>
'''

NP = "import numpy as np\n"
PH3L2_BLOCKS = {
    "s1": {"mode": "py", "setup": NP, "code": '''X = np.array([[3.0, 1.0, 2.0],
              [1.0, 0.0, 4.0]])
print(X.shape)

w_ok = np.array([0.5, 2.0, -1.0])
print((X @ w_ok).shape)

w_short = np.array([0.5, 2.0])
try:
    X @ w_short
except ValueError as e:
    print("ValueError:", e)
'''},
    "n1": {"mode": "py", "setup": NP, "code": '''v = np.array([3.0, 4.0])
length = np.linalg.norm(v)
print(length)
print(v / length)
print(np.linalg.norm(v / length))
'''},
    "k1": {"mode": "py", "setup": NP, "code": '''import matplotlib.pyplot as plt


def cosine(a, b):
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    return (a @ b) / (np.linalg.norm(a) * np.linalg.norm(b))


a = [1, 0]
others = {"[1, 1]": [1, 1], "[2, 2]": [2, 2], "[0, 1]": [0, 1], "[-1, 0]": [-1, 0]}
for name, b in others.items():
    print(name, round(cosine(a, b), 3))

fig, ax = plt.subplots(figsize=(5, 4))
ax.annotate("", xy=a, xytext=(0, 0), arrowprops=dict(arrowstyle="->", color="crimson", lw=2))
ax.text(1.05, -0.15, "a = [1, 0]", color="crimson")
for name, b in others.items():
    ax.annotate("", xy=b, xytext=(0, 0), arrowprops=dict(arrowstyle="->", color="steelblue"))
    ax.text(b[0] + 0.05, b[1] + 0.05, name + ": " + str(round(cosine(a, b), 2)))
ax.set_xbound(-1.5, 3.3)
ax.set_ybound(-0.5, 2.5)
ax.set_aspect("equal")
ax.axhline(0, color="grey", lw=0.5)
ax.axvline(0, color="grey", lw=0.5)
ax.set_title("Cosine with a: 45 degrees 0.71, right angle 0, opposite -1")
plt.show()
'''},
}

# The original four blocks run on the same six requests as the rest of the lesson (they used the larger 311 sample before).
PH2L7_BLOCKS.update({
    "0": dict(sql("""SELECT a.name, COUNT(*) AS n
FROM requests AS r
JOIN agencies AS a ON a.code = r.agency       -- inner join: unmatched requests drop out
GROUP BY a.name;
""", "Rows after this step"), note=NOTE2),
    "1": dict(sql("""SELECT id, created, closed,
       (julianday(closed) - julianday(created)) * 24 AS hours     -- hours between two timestamps
FROM requests;
"""), note="The lesson shows one expression. Here it sits inside a full query so you can run it. " + NOTE2),
    "2": sql("""WITH counts AS (
    SELECT borough, complaint, COUNT(*) AS n
    FROM requests
    WHERE borough IS NOT NULL
    GROUP BY borough, complaint
)
SELECT * FROM counts WHERE n >= 2;
"""),
    "3": dict(sql("""WITH counts AS (
    SELECT borough, complaint, COUNT(*) AS n
    FROM requests
    WHERE borough IS NOT NULL
    GROUP BY borough, complaint
)
SELECT borough, complaint, n,
       ROW_NUMBER() OVER (PARTITION BY borough ORDER BY n DESC, complaint) AS rnk
FROM counts;
""", "Rows when it runs with the counts CTE"), note="This query needs the counts table, so the WITH part is included. " + NOTE2),
})

LESSONS = {"ph2-l7": (PH2L7, PH2L7_BLOCKS), "ph3-l2": (PH3L2, PH3L2_BLOCKS)}
