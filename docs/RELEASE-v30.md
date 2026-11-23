# v30: teach before you ask

Builds on [v29](RELEASE-v29.md). Goal: every question can be answered from what the site has already shown,
without opening the solution. Routes, lesson links, exercise IDs, quiz IDs and the progress key are unchanged
(622 routes, 161 lessons, 234 exercises, 490 quiz questions). Lesson questions go from 876 to 880 (4 new guided
questions). Saved drafts, passes and "marked as read" keep working: old code-block keys are kept with a
`data-snip` attribute, and question IDs are unchanged.

## Rewritten lessons
Hard topics now follow: plain English, a worked example with real input and output, a guided question, then
1-2 independent questions. Extra variations moved into a closed **Optional practice** group before
"Check yourself". Questions show a level chip (Guided, Independent, Challenge).

| Lesson | What is now taught before the questions |
|---|---|
| l1 Setup | New "How the coding questions work" with a worked function and `startswith`/slicing |
| l2 Values, names and strings | Split into Parts 1-3: types, f-strings, string methods on one card, chaining, accumulating in a loop. New guided question q:l2-14 |
| l4 Lists, dicts and loops | Append loop, running total, numbering and comprehensions, dicts, counting, grouping, sorting with a key (and stability), choosing a structure, sets |
| l5 Files and errors | Reading (shows the file), pathlib helpers, what an error looks like when data is wrong, raising your own errors, writing files |
| ph2-l6 SQL grouping | The shape of a query, then the query built one clause at a time with the rows after each clause (FROM, WHERE, GROUP BY, HAVING, ORDER BY), SQLite from Python with `?` parameters, NULL. New guided question q:ph2-l6-4 |
| ph3-l1 A model is a function | Worked by hand in a table, then in code, then a chart; finding slope and intercept from two points; many inputs. New guided questions q:ph3-l1-4, q:ph3-l1-5 |

Every output panel, SQL row table and chart in these lessons was produced by running the code at build time
(41 outputs, 7 SQL tables, 1 chart), and the browser test re-runs each block and compares.

## "New here" notes
229 questions (159 lesson questions, 70 exercises) in 111 lessons use a function or feature that no earlier
lesson shows. Each now has a short "Before you start" box with a one-line explanation and a real example with
its output, shown on the first question that needs it. Specialised library features get a link to the official
docs instead.

## Fixes from the brief
- A bare plotting call such as `ax.hist(...)` no longer prints its `(counts, edges, bars)` tuple; the chart still shows.
- A bare DataFrame (or any expression) on the last line in the Playground now shows its value instead of
  "(nothing was printed)".

## Build
`scripts/content/` holds the sources: `lessons.py`, `questions.py`, `newhere.py`, `patches.py`, the audit in
`audit/`, and `build.py BASE OUT [REPORT]` (needs numpy, pandas and matplotlib).

## Known limitations
- Lessons were split into Parts inside the same route rather than new routes, to keep every link.
- About 45 questions still use a specialised feature with only a doc link (for example TfidfVectorizer,
  GridSearchCV, heapq).
- Gap detection is automated on functions and syntax; a missing reasoning step is not detected.
- The static error example in l5 shows CPython's `Errno 2`; the in-browser Python reports `Errno 44` for the same error.
