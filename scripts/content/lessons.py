"""Teach-before-you-ask rewrites of the priority lessons (v30).

Each lesson is an HTML template with these markers, which build.py expands:

  [[keep N]]   the lesson's original code block number N, unchanged, tagged data-snip="N" so its saved
               edits, line notes and recorded output keep their old key (lesson#N)
  [[code K]]   a new code block from BLOCKS[lesson][K], tagged data-snip="K" (key lesson#K)
  [[out K]]    the real output of block K, produced by running it in CPython at build time
  [[rows K]]   the real result rows of SQL block K, as a table
  [[file F]]   the exact text of the sample file F that the page provides

Prose is plain HTML. Code inside BLOCKS is raw text; build.py escapes it.
"""

PATH_NOTE = ('<div class="callout lesson-path"><p><b>How this lesson works.</b> {parts} Each part explains one idea in plain English, '
             'runs one complete example with its real output, then asks a <span class="pq-level guided">Guided</span> question '
             '(part of the code is written for you) and an <span class="pq-level independent">Independent</span> one (you write it all). '
             'Extra questions sit in <b>Optional practice</b> near the end; they do not block anything.{extra}</p></div>')


def trace(caption, head, rows):
    h = "".join("<th>" + c + "</th>" for c in head)
    b = "".join("<tr>" + "".join("<td>" + c + "</td>" for c in r) + "</tr>" for r in rows)
    return ('<div class="table-wrap"><table class="trace"><caption>' + caption + '</caption><thead><tr>' + h +
            '</tr></thead><tbody>' + b + '</tbody></table></div>')


TOY_DB = '''import sqlite3
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
'''
TOY_NOTE = "A six-row requests table, the same rows the questions in this lesson use."

# ---------------------------------------------------------------- l1: one new section
L1_BRIDGE = '''<h2>How the coding questions work</h2>
<p>Every coding question on this site asks you to finish a small <b>function</b>: a named piece of code that takes inputs and hands back an answer. Lesson 3 covers functions fully. This section is the part you need to answer questions from now on.</p>
[[code w1]]
[[out w1]]
<ul>
<li><code>def greet(word):</code> makes a function called <code>greet</code> with one input called <code>word</code>. The indented lines under it are its body.</li>
<li><code>if word == "hi":</code> runs the indented line under it only when the condition is true. <code>==</code> asks "are these equal?". A single <code>=</code> stores a value instead, so it cannot go in an <code>if</code>.</li>
<li><code>return</code> hands a value back and ends the function at once. The first <code>return</code> that runs wins, so the last line, <code>return "?"</code>, only runs when no <code>if</code> matched.</li>
<li><code>word in ("bye", "see you")</code> is true when <code>word</code> is any of the options in the brackets.</li>
<li><code>print(greet("hi"))</code> calls the function with the input <code>"hi"</code> and prints what it returned. The checks call your function the same way, with other inputs too.</li>
</ul>
<p>Two text checks come up in many questions. <code>text.startswith("go ")</code> and <code>text.endswith(".py")</code> answer <code>True</code> or <code>False</code>. To cut a known beginning off some text, take everything after its length:</p>
[[code w2]]
[[out w2]]
<p><code>task[8:]</code> means "from position 8 to the end", counting from 0; lesson 2 covers this fully. <code>or</code> is true when either side is true, <code>and</code> needs both sides, and <code>not</code> turns True into False.</p>
<div class="callout"><p><b>Answering a question.</b> Replace the line <code>pass</code> (which means "do nothing yet") with your code, then press <b>Run and check</b>. The checks list which input gave the wrong answer. The solution stays hidden until you press Show solution.</p></div>
'''

L1_BLOCKS = {
    "w1": {"mode": "py", "code": '''def greet(word):
    if word == "hi":
        return "Hello!"
    if word in ("bye", "see you"):
        return "Goodbye!"
    return "?"


print(greet("hi"))
print(greet("see you"))
print(greet("thanks"))
'''},
    "w2": {"mode": "py", "code": '''task = "go into notes"
print(task.startswith("go into "))
print(len("go into "))
print(task[len("go into "):])

name = "main.py"
print(name.endswith(".py") or name.endswith(".txt"))
'''},
}

# ---------------------------------------------------------------- l2
L2 = '''<p class="lede">Every program moves values around. Text processing, which is what <code>text-tools</code> does, is mostly string work.</p>
''' + PATH_NOTE.format(parts="It has three parts: values and variables, f-strings, and string methods.",
                       extra=' Every answer is a small function. If <code>def</code> and <code>return</code> are new to you, read <a href="#/lesson/l1">How the coding questions work</a> in lesson 1 first.') + '''
<h2>Part 1: Values and variables</h2>
<p>A value is one piece of data: a number, some text, True or False. Python has a handful of basic types:</p>
[[keep 0]]
[[out 0]]
<p><code>type(value)</code> tells you a value's type. To get just the name as text, add <code>.__name__</code>: <code>type(2.5).__name__</code> is <code>"float"</code>. <code>None</code> means "no value yet". Test for it with <code>value is None</code>, not <code>==</code>.</p>
<p>A <b>variable</b> is a name that points at a value. <code>count = count + 1</code> works right to left: Python reads the value <code>count</code> points at now, adds 1, then points the name at the new value.</p>
<p>A <b>loop</b> repeats the indented lines under it. <code>for _ in range(4):</code> runs them 4 times. <code>range(4)</code> counts 0, 1, 2, 3, and the name <code>_</code> means "I do not need the number itself". A complete run:</p>
[[code w1]]
[[out w1]]
''' + trace("Trace: the value of count on each pass of the loop", ["Pass", "count before", "count + 1", "count after"],
            [["start", "", "", "3"], ["1", "3", "4", "4"], ["2", "4", "5", "5"], ["3", "5", "6", "6"], ["4", "6", "7", "7"]]) + '''
<p>Inside a function the pattern is the same: set the variable from an input, loop, then <code>return</code> it. The first question below has that skeleton written for you.</p>
<h2>Part 2: f-strings</h2>
<p>An f-string is text with an <code>f</code> just before the opening quote. Anything inside <code>{ }</code> is worked out and put into the text. Everything outside the braces, including <code>$</code>, <code>%</code>, <code>:</code> and spaces, is copied as it is.</p>
[[keep 1]]
[[out 1]]
<p>After a colon inside the braces you can say how a number should look:</p>
''' + trace("Number formats inside the braces", ["Inside the braces", "Value", "Shows"],
            [["<code>{price}</code>", "2.5", "2.5"], ["<code>{price:.2f}</code>", "2.5", "2.50 (exactly two decimals)"],
             ["<code>{price:.1f}</code>", "2.46", "2.5 (rounded to one decimal)"],
             ["<code>{score / total * 100:.1f}</code>", "45 and 50", "90.0 (sums work inside the braces)"]]) + '''
[[code w2]]
[[out w2]]
<h2>Part 3a: Cleaning text</h2>
<p>A <b>method</b> is a function that belongs to a value. You call it with a dot: <code>answer.strip()</code>. String methods never change the original text; they return a new string.</p>
<ul>
<li><code>strip()</code> removes spaces (and newlines) from both ends. <code>strip("()!")</code> removes those characters from both ends instead.</li>
<li><code>lower()</code>, <code>upper()</code> and <code>title()</code> change capital letters. <code>title()</code> capitalises the first letter of each word.</li>
<li><code>string.punctuation</code>, from <code>import string</code>, is a ready-made string of every punctuation character, handy with <code>strip</code>.</li>
</ul>
[[code w3]]
[[out w3]]
<p>The square brackets in the first two lines are only there to make the spaces visible. Methods can be chained left to right: <code>answer.strip().lower()</code> strips first, then lowers the result.</p>
<h2>Part 3b: Splitting and joining</h2>
<p><code>text.split()</code> cuts text into a list of words at any run of spaces. <code>text.split(",")</code> cuts at each comma instead, and <code>text.split(" ")</code> cuts at every single space, so two spaces in a row leave an empty string <code>''</code> between them. <code>"-".join(words)</code> goes the other way and glues a list of strings together with <code>-</code> between them. <code>len()</code> counts the items in a list, or the letters in a string.</p>
[[code w4]]
[[out w4]]
<p>The last two lines show a function that returns two values at once: <code>return a, b</code> hands back a pair, which Python prints as <code>(a, b)</code> and calls a <b>tuple</b>.</p>
<h2>Part 3c: Indexes and slices</h2>
<p>Each letter in a string has a position, counted from 0. Negative positions count from the end.</p>
''' + trace('Positions in "hello"', ["Letter", "h", "e", "l", "l", "o"],
            [["Position", "0", "1", "2", "3", "4"], ["From the end", "-5", "-4", "-3", "-2", "-1"]]) + '''
<p><code>word[0]</code> is one letter. <code>word[1:4]</code> is a <b>slice</b>: from position 1 up to, but not including, position 4. Leave out a side to go to the start or the end: <code>word[:2]</code>, <code>word[2:]</code>.</p>
[[code w5]]
[[out w5]]
<p>A slice never fails: if it runs past the text, you get a shorter or empty string. A single index does fail: <code>""[0]</code> raises <code>IndexError: string index out of range</code>, so check for empty text first.</p>
<h2>Part 3d: Replacing and repeating</h2>
<p><code>text.replace(old, new)</code> swaps every copy of <code>old</code> for <code>new</code>. Multiplying a string repeats it: <code>"*" * 4</code> is <code>"****"</code>.</p>
[[code w6]]
[[out w6]]
<h2>String methods on one card</h2>
<p>Everything from Part 3 in one block, to come back to later. A line with only an expression on it shows its value when you press Edit and run.</p>
[[keep 2]]
[[out 2]]
<div class="callout"><p><b>Strings never change in place.</b> <code>text.lower()</code> returns a new string and leaves <code>text</code> as it was. Write <code>text = text.lower()</code> if you want to keep the result.</p></div>
<h2>Chaining</h2>
<p>Because each method returns a new string, you can chain them: <code>raw.strip().lower()</code>. Read it left to right. Chains longer than three steps are easier to debug when split over several lines with names.</p>
<h2>Check yourself</h2>
<ul><li>What does <code>"  Hi  ".strip().upper()</code> return?</li><li>Why does <code>"a  b".split(" ")</code> give a different result from <code>"a  b".split()</code>, when there are two spaces between the a and the b? Try it in the playground.</li></ul>
'''

L2_BLOCKS = {
    "w1": {"mode": "py", "code": '''count = 3
for _ in range(4):
    count = count + 1
    print("count is now", count)
print("final:", count)
'''},
    "w2": {"mode": "py", "code": '''item = "Tea"
price = 2.5
print(f"{item}: ${price}")
print(f"{item}: ${price:.2f}")

score = 45
total = 50
print(f"{score} of {total} is {score / total * 100:.1f}%")
'''},
    "w3": {"mode": "py", "code": '''import string

answer = "  Yes "
print("[" + answer + "]")
print("[" + answer.strip() + "]")
print(answer.strip().lower())
print(answer.strip().lower() in ("yes", "y"))

print("ada lovelace".upper())
print("ada lovelace".title())
print("(hello!)".strip("()!"))
print(string.punctuation)
print("'Hello,'".strip(string.punctuation))
'''},
    "w4": {"mode": "py", "code": '''line = "ada  lovelace london"
print(line.split())
print(line.split(" "))
print("ada,36,London".split(","))
print("-".join(["hello", "world"]))
print(len(line.split()))


def two_counts(text):
    return len(text.split()), len(text.split(","))


print(two_counts("a,b c"))
'''},
    "w5": {"mode": "py", "code": '''word = "hello"
print(word[0], word[-1])
print(word[1:4])
print(word[1:-1])
print(word[:2], word[2:])
print(len(word))
print("[" + "hi"[1:-1] + "]")
'''},
    "w6": {"mode": "py", "code": '''text = "my pin is 1234 and 1234"
print(text.replace("1234", "****"))
print("*" * 4)
print(len("1234"))
print(text)
'''},
}

# ---------------------------------------------------------------- l4
L4 = '''<p class="lede">Counting words is a list problem (the words) and a dict problem (word to count). Most data work is these two shapes.</p>
''' + PATH_NOTE.format(parts="It goes in this order: lists, loops over lists, dicts, counting with a dict, sorting, and sets.", extra="") + '''
<h2>Part 1: Lists and the append loop</h2>
<p>A <b>list</b> holds items in order: <code>[3, -1, 4]</code>. <code>len(xs)</code> counts the items, and <code>xs[0]</code> is the first one. <code>[]</code> is an empty list, and <code>result.append(x)</code> adds <code>x</code> to its end.</p>
<p>The most common loop in data work: start with an empty list, look at each item, and keep the ones you want. <code>for n in numbers:</code> runs the indented lines once per item, with <code>n</code> pointing at that item.</p>
[[code w1]]
[[out w1]]
''' + trace("Trace: the loop above, one item at a time", ["n", "n &gt; 0?", "positives after this pass"],
            [["3", "yes", "[3]"], ["-1", "no", "[3]"], ["4", "yes", "[3, 4]"], ["-5", "no", "[3, 4]"], ["9", "yes", "[3, 4, 9]"]]) + '''
<p>The last line uses <code>%</code>, the <b>remainder</b> after dividing: <code>7 % 2</code> is 1 and <code>8 % 2</code> is 0. So <code>n % 2 == 0</code> is true exactly when <code>n</code> is even.</p>
<h2>Part 1b: Keeping a running total</h2>
<p><code>total += p</code> is short for <code>total = total + p</code>. Start the total at 0 before the loop and add each item inside it.</p>
[[code w2]]
[[out w2]]
''' + trace("Trace: total on each pass", ["p", "total before", "total after"],
            [["4", "0", "4"], ["10", "4", "14"], ["1", "14", "15"]]) + '''
<h2>Part 2: Numbering and comprehensions</h2>
[[keep 0]]
[[out 0]]
<p><code>enumerate(words, start=1)</code> gives pairs (number, item), and <code>for i, word in ...</code> unpacks each pair into two names. A <b>list comprehension</b> is a one-line way to write the append loop from Part 1:</p>
''' + trace("The same list, two ways", ["Append loop", "List comprehension"],
            [["<code>long = []</code><br><code>for w in words:</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;if len(w) &gt; 2:</code><br><code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;long.append(w)</code>",
              "<code>long = [w for w in words if len(w) &gt; 2]</code>"]]) + '''
<p>Read it as "w, for each w in words, if len(w) &gt; 2". The part before <code>for</code> can change the item too: <code>[w.upper() for w in words]</code>.</p>
<h2>Part 3: Dicts: look up by key</h2>
<p>A <b>dict</b> maps keys to values: <code>{"tea": 2, "cake": 3}</code>. <code>menu["tea"]</code> looks a value up, and fails with <code>KeyError</code> when the key is missing. <code>menu.get("soup", 0)</code> returns 0 instead of failing. <code>key in menu</code> checks whether a key is there, <code>menu["soup"] = 4</code> adds or replaces a value, and <code>menu.items()</code> gives every (key, value) pair for a loop.</p>
[[code w3]]
[[out w3]]
<h2>Dicts: counting</h2>
[[keep 1]]
[[out 1]]
''' + trace('Trace: counting ["the", "cat", "the"]', ["word", "counts.get(word, 0)", "counts after this pass"],
            [["the", "0", "{'the': 1}"], ["cat", "0", "{'the': 1, 'cat': 1}"], ["the", "1", "{'the': 2, 'cat': 1}"]]) + '''
<p><code>counts.get(word, 0)</code> returns 0 when the word is not there yet, instead of raising <code>KeyError</code>. The standard library also has <code>collections.Counter</code>, which does this for you. Write it by hand once so you understand what Counter does.</p>
<p>A loop over a string gives one character at a time, and <code>ch.isalpha()</code> tells you whether a character is a letter:</p>
[[code w4]]
[[out w4]]
<h2>Part 4: Grouping into lists</h2>
<p>Sometimes each key needs a list of items rather than a count. Make an empty list the first time you see a key, then append to it:</p>
[[code w5]]
[[out w5]]
<p><code>groups.setdefault(key, []).append(word)</code> does both steps in one line: it returns the list for <code>key</code>, creating an empty one first if needed.</p>
<h2>Sorting with a key</h2>
<p><code>sorted(items)</code> returns a new sorted list and leaves the original alone. <code>key=</code> takes a function that gives each item's sort value. <code>lambda w: len(w)</code> is a one-line function: "given w, return len(w)". When the key returns a tuple, Python compares the first part, and only looks at the second part to break ties.</p>
[[code w6]]
[[out w6]]
<p>With <code>key=lambda w: len(w)</code> alone, "pear" stays ahead of "kiwi": they tie on length, and <code>sorted</code> keeps tied items in their original order. The tuple key breaks the tie a to z.</p>
<p>For pairs from <code>counts.items()</code>, <code>kv[1]</code> is the count. A minus sign sorts numbers high first, and <code>[:2]</code> keeps the first two:</p>
[[keep 2]]
[[out 2]]
<p>The second form gives a stable, predictable order for ties, which matters when tests compare exact output.</p>
<h2>Choosing a structure</h2>
<div class="table-wrap"><table>
<thead><tr><th>Need</th><th>Use</th><th>Why</th></tr></thead>
<tbody>
<tr><td>Ordered items, duplicates allowed</td><td>list</td><td>Keeps order; index by position</td></tr>
<tr><td>Look up a value by a key</td><td>dict</td><td>Average constant-time lookup</td></tr>
<tr><td>Unique items, fast "is it in there?"</td><td>set</td><td>Membership check without scanning</td></tr>
<tr><td>A fixed small group, like (word, count)</td><td>tuple</td><td>Cannot be changed by accident</td></tr>
</tbody></table></div>
<p>A <b>set</b> holds each item at most once. <code>set()</code> makes an empty one, <code>seen.add(x)</code> adds an item, <code>x in seen</code> checks quickly, and <code>a &amp; b</code> keeps the items two sets share. A set has no fixed order, so wrap it in <code>sorted()</code> before you print or compare it. <code>else:</code> runs when the <code>if</code> above it was false.</p>
[[code w7]]
[[out w7]]
<h2>Check yourself</h2>
<ul><li>What does <code>counts.get("dog", 0)</code> return if "dog" was never counted?</li><li>Why sort by <code>(-count, word)</code> rather than just count?</li></ul>
'''

L4_BLOCKS = {
    "w1": {"mode": "py", "code": '''numbers = [3, -1, 4, -5, 9]
positives = []
for n in numbers:
    if n > 0:
        positives.append(n)
print(positives)
print(len(positives), positives[0])
print(7 % 2, 8 % 2)
'''},
    "w2": {"mode": "py", "code": '''prices = [4, 10, 1]
total = 0
for p in prices:
    total += p
    print("after", p, "the total is", total)
print(total)
'''},
    "w3": {"mode": "py", "code": '''menu = {"tea": 2, "cake": 3}
print(menu["tea"])
print("soup" in menu)
print(menu.get("soup", 0))
menu["soup"] = 4
print(menu)
for item, price in menu.items():
    print(item, "costs", price)
'''},
    "w4": {"mode": "py", "code": '''for ch in "Hi 2!":
    print(repr(ch), ch.isalpha())
'''},
    "w5": {"mode": "py", "code": '''groups = {}
for word in ["apple", "bear", "avocado"]:
    key = word[0]
    if key not in groups:
        groups[key] = []
    groups[key].append(word)
print(groups)
'''},
    "w6": {"mode": "py", "code": '''words = ["pear", "fig", "apple", "kiwi"]
print(sorted(words))
print(sorted(words, key=lambda w: len(w)))
print(sorted(words, key=lambda w: (len(w), w)))
'''},
    "w7": {"mode": "py", "code": '''seen = set()
for x in [3, 1, 3]:
    if x in seen:
        print(x, "seen before")
    else:
        print(x, "new")
        seen.add(x)
print(sorted(seen))
print(sorted({"tea", "milk"} & {"milk", "tea", "jam"}))
'''},
}

# ---------------------------------------------------------------- l5
L5 = '''<p class="lede">Real programs read files that may be missing, empty or messy. Handle the failures you expect and let the others surface loudly.</p>
''' + PATH_NOTE.format(parts="It goes in this order: reading a file, what happens when the data is wrong, raising your own errors, then writing a file.", extra="") + '''
<h2>Part 1: Reading a file</h2>
<p>The examples and questions here can read a small file called <code>notes.txt</code>. This is exactly what is in it, blank lines and leading spaces included:</p>
[[file notes.txt]]
[[keep 0]]
[[out 0]]
<p><code>with</code> closes the file for you, even if an error happens halfway. Always pass <code>encoding="utf-8"</code> on Windows; the default there can differ and break on accented letters.</p>
<p>Each <code>line</code> still ends with a hidden newline character, <code>\\n</code>. <code>repr(line)</code> shows it. <code>line.strip()</code> removes it together with any spaces, so a blank line becomes the empty string <code>''</code>, and <code>if line.strip():</code> is false for it.</p>
[[code w1]]
[[out w1]]
''' + trace("Trace: which lines are kept", ["line (as repr shows it)", "line.strip()", "kept?"],
            [["'first line\\n'", "'first line'", "yes"], ["'\\n'", "''", "no"], ["'  second line\\n'", "'second line'", "yes"],
             ["'\\n'", "''", "no"], ["'third\\n'", "'third'", "yes"]]) + '''
<h2>Whole-file helpers: pathlib</h2>
<p>The <code>pathlib</code> module is a tidy alternative:</p>
[[keep 1]]
<p><code>Path(name).read_text(encoding="utf-8")</code> returns the whole file as one string. On that string, <code>splitlines()</code> gives a list of lines without the newlines, and <code>split()</code> gives a list of words. <code>Path(name).suffix</code> is the ending such as <code>".txt"</code>, and <code>.name</code> is the file name without its folder. Inside <code>with open(...) as f</code>, <code>f.read()</code> also returns the whole text.</p>
[[code w2]]
[[out w2]]
<h2>Part 2: When the data is wrong</h2>
<p>When Python cannot do something, it raises an <b>exception</b> and stops. Two you will meet constantly, with the exact last line Python prints:</p>
[[out w3]]
<p>A <code>try</code> block lets you handle an exception you expect. Python runs the <code>try</code> lines; if one raises the named error, it jumps straight to the <code>except</code> lines instead of stopping.</p>
[[keep 2]]
[[out 2]]
<p>Catch the specific error you expect. A bare <code>except:</code> also swallows typos and bugs, and you lose the message that would have told you what went wrong.</p>
<p>A complete example with one input that works and one that does not. <code>default=None</code> in the first line gives the input a value to use when the caller leaves it out.</p>
[[code w4]]
[[out w4]]
''' + trace("Trace: the two calls", ["Call", "Inside try", "Then"],
            [['<code>to_number("42")</code>', "int works, so <code>return 42</code> runs", "except is skipped; the result is 42"],
             ['<code>to_number("ten")</code>', "int raises ValueError", 'except runs: it prints a message and returns the default, None']]) + '''
<p>The same shape handles a missing file. <code>except FileNotFoundError as e</code> also gives you the error itself, and <code>e.filename</code> is the name it could not find:</p>
[[code w5]]
[[out w5]]
<h2>Raising your own errors</h2>
<p><code>raise ValueError("message")</code> stops the function at once with an error you choose. In an f-string, <code>{line!r}</code> shows the value the way <code>repr</code> does, with quotes, so empty text and stray spaces are visible in the message.</p>
[[keep 3]]
[[out 3]]
<p>The first call works; the second stops with the message. <code>int(" 91")</code> works because <code>int</code> ignores spaces at the ends, but it raises <code>ValueError</code> itself for text such as <code>"abc"</code>.</p>
<p>A clear error at the point where bad data enters is far easier to debug than a strange result three functions later.</p>
<h2>Part 3: Writing a file</h2>
<p><code>open(path, "w", encoding="utf-8")</code> opens a file for writing: it creates the file, or empties it if it already exists. <code>"a"</code> adds to the end instead. <code>f.write(text)</code> writes exactly the text you give it and does not add a newline, so add <code>"\\n"</code> yourself. <code>f.readlines()</code> reads it back as a list of lines.</p>
[[code w6]]
[[out w6]]
<h2>Check yourself</h2>
<ul><li>What does <code>with</code> guarantee?</li><li>Which error does <code>open("missing.txt")</code> raise?</li></ul>
'''

L5_SETUP = '''import os
os.makedirs("data", exist_ok=True)
for name, text in [("a.txt", "alpha"), ("b.txt", "beta")]:
    with open(os.path.join("data", name), "w", encoding="utf-8") as f:
        f.write(text)
'''
L5_BLOCKS = {
    "w1": {"mode": "py", "setup": L5_SETUP, "files": ["notes.txt"], "code": '''kept = []
with open("notes.txt", encoding="utf-8") as f:
    for line in f:
        print(repr(line))
        if line.strip():
            kept.append(line.strip())
print(kept)
'''},
    "w2": {"mode": "py", "setup": L5_SETUP, "files": ["notes.txt"], "code": '''from pathlib import Path

text = Path("notes.txt").read_text(encoding="utf-8")
print(repr(text))
print(text.splitlines())
print(text.split())
print(len(text.split()))
print(Path("data/a.txt").suffix, Path("data/a.txt").name)
'''},
    "w3": {"mode": "py", "setup": L5_SETUP, "files": ["notes.txt"], "show_code": False, "code": '''for attempt in ['int("ten")', 'open("missing.txt")']:
    try:
        eval(attempt)
    except Exception as e:
        print(attempt, "->", type(e).__name__ + ":", e)
'''},
    "w4": {"mode": "py", "setup": L5_SETUP, "files": ["notes.txt"], "code": '''def to_number(text, default=None):
    try:
        return int(text)
    except ValueError:
        print("not a whole number:", text)
        return default


print(to_number("42"))
print(to_number("ten"))
'''},
    "w5": {"mode": "py", "setup": L5_SETUP, "files": ["notes.txt"], "code": '''try:
    with open("missing.txt", encoding="utf-8") as f:
        print(f.read())
except FileNotFoundError as e:
    print("No file called", e.filename)
'''},
    "w6": {"mode": "py", "setup": L5_SETUP, "files": ["notes.txt"], "code": '''with open("out.txt", "w", encoding="utf-8") as f:
    f.write("first\\n")
    f.write("second\\n")
with open("out.txt", "a", encoding="utf-8") as f:
    f.write("third\\n")

with open("out.txt", encoding="utf-8") as f:
    lines = f.readlines()
print(lines)
print(len(lines))
'''},
}

# ---------------------------------------------------------------- ph2-l6
PH2L6 = '''<p class="lede">SQL is how most company data is queried. You describe the result you want; the database works out how to get it.</p>
''' + PATH_NOTE.format(parts="First the shape of a query, then the same query built one clause at a time on a six-row table so you can see the rows after every step, then running SQL from Python.", extra="") + '''
<h2>The shape of a query</h2>
[[keep 0]]
<p>The numbers show the order the database applies the clauses. That is why <code>WHERE</code> cannot use <code>COUNT(*)</code>: groups do not exist yet. Filter groups with <code>HAVING</code>. The next section shows each step on real rows.</p>
<h2>Build it one clause at a time</h2>
<p>Here is a small <code>requests</code> table with six rows. The questions in this lesson use exactly these rows. Every block below runs on it when you press Edit and run.</p>
[[code w0]]
[[rows w0]]
<p><b>Step 1, WHERE keeps some rows.</b> <code>WHERE</code> checks each row on its own and keeps the ones where the condition is true. Rows 1, 3 and 4 are in the Bronx. Row 5 has no borough at all (<code>NULL</code>), so it is not kept either.</p>
[[code w1]]
[[rows w1]]
<p><b>Step 2, GROUP BY makes one row per group.</b> <code>GROUP BY complaint</code> puts the kept rows with the same complaint together: Pothole gets rows 1 and 3, Noise gets row 4. Each group becomes one result row, and <code>COUNT(*)</code> counts the rows in it.</p>
''' + trace("Which rows went into each group", ["complaint", "rows in the group", "COUNT(*)"],
            [["Noise", "4", "1"], ["Pothole", "1, 3", "2"]]) + '''
[[code w2]]
[[rows w2]]
<p><b>Step 3, HAVING keeps some groups.</b> <code>HAVING</code> runs after the groups exist, so it can use <code>COUNT(*)</code>. Noise has only one row, so it goes.</p>
[[code w3]]
[[rows w3]]
<p><b>Step 4, ORDER BY sorts the result.</b> With one row left there is nothing to sort, so this example drops the <code>WHERE</code> and the <code>HAVING</code> to show a sort with ties. <code>n DESC</code> puts the biggest counts first, and <code>complaint</code> breaks ties a to z.</p>
[[code w4]]
[[rows w4]]
<p>Build your own queries the same way: run <code>FROM</code> and <code>WHERE</code>, check the rows, then add <code>GROUP BY</code>, then <code>HAVING</code>, then <code>ORDER BY</code>. When a step gives a surprise, you know which clause caused it.</p>
<h2>SQLite from Python</h2>
[[keep 2]]
<p>In the exercises, <code>from db import connect</code> gives you a database with the <code>requests</code> and <code>agencies</code> tables already loaded.</p>
<p><code>conn.execute(sql)</code> runs a query and returns a <b>cursor</b>. <code>.fetchall()</code> gives every result row as a list of tuples. <code>.fetchone()</code> gives the first row as one tuple, so <code>.fetchone()[0]</code> is the first value in it.</p>
<p>To put a value into a query, write <code>?</code> where it goes and pass the values as a tuple after the SQL. A complete example on the six-row table:</p>
[[code w5]]
[[out w5]]
<ul>
<li>The values fill the <code>?</code> marks in order.</li>
<li><code>("QUEENS",)</code> needs the comma: that is what makes a one-item tuple. <code>("QUEENS")</code> is just a string in brackets, and SQLite rejects it.</li>
<li>Do not build the SQL with an f-string. A value such as <code>O'Brien</code> breaks the quotes, and text a user typed could change what the query does (SQL injection). With <code>?</code>, the database inserts the value safely.</li>
</ul>
<h2>NULL is not a value</h2>
[[keep 1]]
<p><code>NULL</code> means "unknown". A comparison with it is never true, so <code>borough = NULL</code> matches no rows at all, even row 5:</p>
[[code w6]]
[[rows w6]]
[[code w7]]
[[rows w7]]
<h2>Check yourself</h2>
<ul><li>Why can't <code>WHERE</code> filter on <code>COUNT(*)</code>?</li><li>How do you find rows where a column is missing?</li></ul>
'''

PH2L6_BLOCKS = {
    "w0": {"mode": "sql", "setup": TOY_DB, "note": TOY_NOTE, "code": "SELECT * FROM requests;\n"},
    "w1": {"mode": "sql", "setup": TOY_DB, "note": TOY_NOTE, "code": "SELECT id, borough, complaint\nFROM requests\nWHERE borough = 'BRONX';\n"},
    "w2": {"mode": "sql", "setup": TOY_DB, "note": TOY_NOTE, "code": "SELECT complaint, COUNT(*) AS n\nFROM requests\nWHERE borough = 'BRONX'\nGROUP BY complaint;\n"},
    "w3": {"mode": "sql", "setup": TOY_DB, "note": TOY_NOTE, "code": "SELECT complaint, COUNT(*) AS n\nFROM requests\nWHERE borough = 'BRONX'\nGROUP BY complaint\nHAVING COUNT(*) >= 2;\n"},
    "w4": {"mode": "sql", "setup": TOY_DB, "note": TOY_NOTE, "code": "SELECT complaint, COUNT(*) AS n\nFROM requests\nGROUP BY complaint\nORDER BY n DESC, complaint;\n"},
    "w5": {"mode": "py", "setup": TOY_DB, "note": TOY_NOTE, "code": '''borough = "BRONX"
rows = conn.execute(
    "SELECT id, complaint FROM requests WHERE borough = ? ORDER BY id",
    (borough,),
).fetchall()
print(rows)

row = conn.execute("SELECT COUNT(*) FROM requests WHERE borough = ?", ("QUEENS",)).fetchone()
print(row)
print(row[0])
'''},
    "w6": {"mode": "sql", "setup": TOY_DB, "note": TOY_NOTE, "code": "SELECT COUNT(*) AS n\nFROM requests\nWHERE borough = NULL;      -- always 0 rows: use IS NULL\n"},
    "w7": {"mode": "sql", "setup": TOY_DB, "note": TOY_NOTE, "code": "SELECT id, borough, closed\nFROM requests\nWHERE closed IS NULL OR borough IS NULL;\n"},
}

# ---------------------------------------------------------------- ph3-l1
PH3L1 = '''<p class="lede">Every model you will build takes numbers in and gives a number out. Training means choosing the knobs inside that function.</p>
''' + PATH_NOTE.format(parts="It has three parts: one input, finding the knobs from two points, and many inputs. The maths is worked by hand first, then in code, then on a graph.", extra="") + '''
<h2>The simplest model</h2>
[[keep 0]]
[[out 0]]
<ul>
<li><code>w</code> (weight) sets the slope: how much the output changes when <code>x</code> goes up by 1.</li>
<li><code>b</code> (bias) shifts everything up or down.</li>
</ul>
<p>By hand, with <code>w = 2</code> and <code>b = 5</code>: multiply, then add.</p>
''' + trace("Predictions by hand for w = 2, b = 5", ["x", "w * x", "w * x + b"],
            [["0", "2 × 0 = 0", "0 + 5 = 5"], ["1", "2 × 1 = 2", "2 + 5 = 7"], ["10", "2 × 10 = 20", "20 + 5 = 25"]]) + '''
<h2>See what the knobs do</h2>
[[keep 1]]
<p>Paste this into the Playground and change the numbers. Building intuition by changing a knob and watching is the point of this whole phase.</p>
<h2>Find the knobs from two points</h2>
<p>If you know two points on a line, you can work out <code>w</code> and <code>b</code>. Take the points (1, 3) and (4, 9).</p>
''' + trace("By hand: the line through (1, 3) and (4, 9)", ["Step", "Working", "Result"],
            [["1. Rise: how far y moves", "9 − 3", "6"], ["2. Run: how far x moves", "4 − 1", "3"],
             ["3. Slope w = rise ÷ run", "6 ÷ 3", "w = 2"], ["4. Bias b = y1 − w × x1", "3 − 2 × 1", "b = 1"],
             ["5. Check the first point", "2 × 1 + 1", "3 ✓"], ["6. Check the second point", "2 × 4 + 1", "9 ✓"]]) + '''
<p>Substituting both points back in is the check: if either one misses, a step above is wrong. Now the same working in code, with a graph of the line and the two points:</p>
[[code w1]]
[[out w1]]
<p>In code, the slope is <code>w = (y2 - y1) / (x2 - x1)</code> and the bias is <code>b = y1 - w * x1</code>. If <code>x1 == x2</code> the run is 0, the line is vertical, and Python raises <code>ZeroDivisionError</code>: no <code>w</code> and <code>b</code> can describe it.</p>
<h2>Many inputs</h2>
<p>With several features, each gets its own weight, and the prediction is a weighted sum: <code>w1*x1 + w2*x2 + ... + b</code>. Lesson 2 shows that this sum is a dot product, which is why linear algebra appears in ML at all.</p>
<p>A two-feature example by hand: <code>x = [3, 2]</code> (say, rooms and bathrooms), <code>w = [0.5, 2]</code> and <code>b = 1</code>.</p>
''' + trace("By hand: a weighted sum of two features", ["Feature", "x", "w", "x × w"],
            [["1", "3", "0.5", "1.5"], ["2", "2", "2", "4"], ["Sum", "", "", "5.5"], ["+ b", "", "", "5.5 + 1 = 6.5"]]) + '''
<p>In code, <code>zip(x, w)</code> pairs the first feature with the first weight, the second with the second, and so on. Multiply each pair and add them up:</p>
[[code w2]]
[[out w2]]
<p>The lengths must match: every feature needs exactly one weight. <code>zip</code> stops at the shorter list without any error, so the last line silently drops the 7 and would give a wrong prediction. Check the lengths yourself and raise an error when they differ.</p>
<div class="callout"><p><b>Why it matters:</b> logistic regression, neural network layers and the attention inside LLMs are all built from this weighted sum, with something extra wrapped around it.</p></div>
<h2>Check yourself</h2>
<ul><li>What happens to the line if you double <code>w</code>?</li><li>What does <code>b</code> do?</li></ul>
'''

PH3L1_BLOCKS = {
    "w1": {"mode": "py", "setup": "import numpy as np\n", "code": '''import matplotlib.pyplot as plt

x1, y1 = 1, 3
x2, y2 = 4, 9
w = (y2 - y1) / (x2 - x1)
b = y1 - w * x1
print("w =", w, "and b =", b)
print("check:", w * x1 + b, w * x2 + b)

xs = [0, 1, 2, 3, 4, 5]
fig, ax = plt.subplots(figsize=(6, 3))
ax.plot(xs, [w * x + b for x in xs], label="y = 2x + 1")
ax.scatter([x1, x2], [y1, y2], color="crimson", zorder=3, label="the two points")
ax.set_title("The line through (1, 3) and (4, 9)")
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.legend()
plt.show()
'''},
    "w2": {"mode": "py", "setup": "import numpy as np\n", "code": '''x = [3, 2]
w = [0.5, 2]
b = 1
print(list(zip(x, w)))

total = 0
for xi, wi in zip(x, w):
    total += xi * wi
print(total + b)

print(sum(xi * wi for xi, wi in zip(x, w)) + b)
print(list(zip([3, 2, 7], [0.5, 2])))
'''},
}

LESSONS = {"l2": (L2, L2_BLOCKS), "l4": (L4, L4_BLOCKS), "l5": (L5, L5_BLOCKS), "ph2-l6": (PH2L6, PH2L6_BLOCKS), "ph3-l1": (PH3L1, PH3L1_BLOCKS)}
# l1 keeps its text; the bridge section is inserted after the tools table.
INSERTS = {"l1": ("<h2>PowerShell basics</h2>", L1_BRIDGE, L1_BLOCKS)}
