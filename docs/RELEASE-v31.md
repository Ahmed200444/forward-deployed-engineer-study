# v31: offline copy, two-tab Study Log fix, sidebar split, more teaching

Builds on [v30](RELEASE-v30.md). Lesson routes, exercise IDs, question IDs, quiz IDs, the progress key
(`ai-study-phase0-v1`) and the backup format are unchanged, so drafts, passes, saved progress and old backups
keep working.

## 1. Downloadable offline copy
- The page now loads its Python runtime from the relative folder `py/` instead of `/py/`. Opened from a
  Windows folder, `/py/` meant `C:\py\`.
- `python scripts/make-bundle.py OUT` writes `fde-study-offline.zip`: `index.html`, the whole `py/` runtime
  (Pyodide 0.26.4 with numpy, pandas, matplotlib, scikit-learn, scipy, pytest, SQLite and the rest of the lock
  file), `Start FDE Study.cmd` + `serve.ps1` (Windows, PowerShell only, nothing installed), `start.sh`
  (Mac/Linux, python3) and `HOW-TO-START.txt`.
- The launchers serve the folder at `http://localhost:8765/` (this computer only) and open the browser. The port
  is fixed so the browser finds the same saved progress each time.
- Opened straight from a file, the page says so at the top and the Run buttons explain how to start it, instead
  of failing. Lessons can still be read that way.
- Progress in the offline copy is separate from the online site (browsers keep it per address). Backup and
  restore moves it between them. Publish to GitHub works only online.

## 2. Two-tab Study Log fix
When two tabs finished different lessons on a day with no log entry yet, the second save replaced the day's
whole record, so one lesson's log entry was lost (and, with the lessonIds map new on both sides, one lesson id).
The transactional save now merges a log record field by field even when it did not exist before: lesson ids are
merged one by one and counters are applied as separate increments.

## 3. Sidebar: Projects and Review
The Practice group is split. **Projects** holds the phase project, local projects, the integrated capstone and the
real-model lab. **Review** holds Interview prep and the phase checkpoint. The phase project shows its own name
without the `Project:` prefix (Phase 0: "Text-tools analyzer"). Every link goes where it went before.

## 4. Teaching
- Every "New here" note that only linked to documentation is now a worked example with its real output
  (TfidfVectorizer, GridSearchCV, TimeSeriesSplit, metrics, SQL functions, pandas/string/datetime methods...).
  Notes show the imports they need. 0 notes are doc-link only.
- **ph2-l7 SQL: joins, CTEs and window functions** is rebuilt on the six-row table from lesson 6 plus a
  two-row agencies table: the rows after an inner join and a left join, `julianday` worked by hand for one request,
  the raw float noise and `ROUND`, each CTE step's rows, and the window steps (counts, numbered rows, `rnk = 1`,
  `RANK` vs `ROW_NUMBER` on a tie). The four original code blocks now run on the same small tables.
  New guided questions q:ph2-l7-5 to q:ph2-l7-8, each followed by the existing independent question.
- **ph3-l2 Vectors, dot products and similarity**: each calculation is worked by hand in a table first (dot
  product, `X @ w + b`, length of [3, 4], cosine for four vectors), then in code, then an arrow chart labelled
  with the cosines; plus a shape-error example. New guided questions q:ph3-l2-5 to q:ph3-l2-7.
- Fixed a v30 bug: some notes showed NumPy 2 output such as `np.float64(5.0)`; the site's Python prints `5.0`.
  The build now runs with the same library versions as the in-browser runtime.
- SQL row tables print whole floats the way the live runner does (`12`, not `12.0`).

## Fixed while retesting
After signing in to GitHub from Publish, the review panel sometimes did not open, and an open review could be
closed by a save arriving from another tab. A save from elsewhere now refreshes only the sidebar while a review is
open, and the sign-in flag is used only by the card that actually opens the review.

## Build
`cd scripts/content && python build.py BASE OUT [REPORT]` with Python 3.12, numpy 1.26.4, pandas 2.2.0,
scikit-learn 1.4.2 and scipy 1.12.0, the same versions as the bundled Pyodide 0.26.4 runtime, so printed output
matches the site. The bundled runtime has Matplotlib 3.5.2, which has no Python 3.12 wheel for a normal
computer, so CPython uses Matplotlib 3.8.4 only to check a chart block's printed output. Every chart shown in a
lesson is then drawn again by `scripts/content/pyodide_run.js` in the bundled runtime (Matplotlib 3.5.2), and the
build stops if that run's printed output or number of charts differs from the CPython run. Needs Node.js.
New sources: `lessons_v31.py`, `newhere_v31.py`, `pyodide_run.js`, `scripts/bundle/`, `scripts/make-bundle.py`.

## Tests
New: `tests/studylog.js` (two tabs from an empty day), `tests/bundle.js` (a freshly extracted zip served by its
own launcher with all outside requests blocked, plus the file:// behaviour), `tests/v31.js` (sidebar groups and
destinations compared with v30). `tests/v30.js` now also covers ph2-l7 and ph3-l2.

## Known limitations
- The Windows launcher (`serve.ps1`) was not run in the build environment: PowerShell is not available there.
  The Mac/Linux launcher and the same files served on the same address were tested.
- The page still asks Google Fonts for its fonts. Offline, that request fails and the page uses system fonts.
- The offline copy is about 160 MB, almost all of it the Python runtime.
