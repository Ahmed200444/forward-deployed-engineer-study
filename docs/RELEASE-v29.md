# v29: QA brief passes 2 and 3, theme switch

Builds on [v29 pass 1](RELEASE-v29-pass1.md). The routes, lessons, exercises, quizzes and progress key are
unchanged: 622 routes, 161 lessons, 234 exercises, 12 phase projects, 6 portfolio projects, 10 local projects,
490 quiz questions, 876 lesson questions. Old bookmarks and saved progress keep working.

## Pass 2: learning workflows
- **Quizzes.** Choices are shown in a new order on each attempt and graded by a stable choice ID, so best scores
  and Review do not depend on position. Questions with "all of the above" keep their written order. Wording
  fixes from the brief (l1 Q2 lockfile question, fde-l8 explanation, "runs on your own computer" callouts).
- **PowerShell downloads** are saved as `.ps1`, and the note says they run locally in PowerShell.
- **Projects** are grouped as 6 portfolio, 12 phase and 10 local projects (28 in all: 18 in the browser, 10 local),
  with the same counts on Home and the Projects page. Local cards also show a publish status.
- **Study log** counts distinct lessons: marking a lesson read, unread and read again counts it once. Older days
  keep their old counter.
- **Playground** has Undo clear, separately for Python and SQL, kept across reloads.
- **Search** shows "Showing 1–50 of N", Show more until the last result, filters by type with counts, and Back
  returns to the result you opened with keyboard focus on it.
- **Backup** shows a comparison before restoring and rejects wrong file types, malformed JSON, other JSON and
  newer versions without changing anything. Undo last restore is kept across reloads, warns when progress was
  saved after the restore, and can be dismissed.
- **CI at the repository root.** Publishing a local project into a portfolio offers its workflow at
  `.github/workflows/<project>-ci.yml`, scoped to the project folder (path filters and working directory), and the
  README gains a "Continuous integration" section. It needs an explicit tick and can be unticked. If the GitHub
  App lacks the Workflows permission, the page says so and nothing is written.
- **Recheck published status.** "Check it is still there" (and once per page when signed in) asks GitHub whether the
  repository, branch and folder still exist. Gone: "Previously published · link unavailable" with Clear this record.
  No access or offline: the record stays, with a separate note.
- **Local projects** each include `.python-version` (3.12) and a `uv.lock`, CI runs `uv sync --locked`, ruff and
  pytest on Ubuntu and Windows, and the READMEs explain the lockfile.
- Exercise checks that compare values now say "expected X, got Y".

## Pass 3: design
- Exercises: on wide screens the task sits on the left and the editor, Run and test output on the right; the
  worked example, hints and solution follow under "Stuck?".
- Breadcrumb on every course page (All phases / Phase / Lesson / Exercise) with a link to the phase checkpoint.
- The sidebar lists every phase as an expandable section with its progress count (replaces the phase menu).
- Home starts with a Continue card (where you are, the next step, a Continue button) and a progress summary.
- Focus ring tokens for both themes and 44 px touch targets on phones.
- **Theme switch:** a sun and moon switch at the top of the sidebar and in the phone header. The chosen theme is
  saved with your progress and stays on every page, after reload and in new tabs.

## Tests run for this release (all on the local HTTPS test host with mock GitHub)
rt 22/22, store 33/33, pub 43/43, smoke 27/27, v29 70/70, lay 602/602, full sweep (234 exercises, 18 projects,
876 lesson questions, 171 worked examples, 187 snippets; 2 snippets raise on purpose). The 10 local projects pass
their CI steps on Linux with Python 3.12 (see the project READMEs). Windows CI has not been run yet.
