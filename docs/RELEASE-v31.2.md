# v31.2: fixes from the v31.1 audit

Builds on v31.1 (sha256 `a8cd131b…46b3`). Lesson routes, exercise ids, question ids, quiz ids, the
progress key (`ai-study-phase0-v1`) and the backup format are unchanged, so drafts, passes, saved progress and
old backups keep working. Built by `python scripts/content/v312.py BASE OUT` from the v31.1 page.

## 1. Run twice (ph9-e12 "Store runs in SQLite")
The demo at the bottom of the starter, given code and model solution now deletes `runs.db` before opening it.
The browser keeps files between runs, so pressing Run a second time used to fail with
`ValueError: run r1 already exists`. Saved drafts made before v31.2 keep their old demo line; deleting those
two lines from the draft, or pressing Reset, fixes them.

## 2. Checks that a wrong answer could pass
Seven inline questions had a single test for an edge case only. Each now also checks the main job:
ph5-l12 Q3 (the 202 reply), ph6-l15 Q3 (a repeat comes from the cache), ph9-l4 Q3 (the same request runs once),
ph9-l9 Q3 (valid lines are read), ph9-l13 Q2 (a valid order), ph9-l14 Q2 (the allowed moves), ph9-l16 Q1 (the
answer is filled in and the saved state is left alone).

## 3. Quiz options
In 391 of 490 questions the right answer was the one longest option. 291 questions were edited
(`scripts/content/quiz_edits/`, compiled to `quiz_v312.json`): wrong options made as specific as the right
one, or the right answer said more briefly. Option order, the keyed answer and every explanation are unchanged.
The right answer is now the unique longest option in 130 of 490 (27%, about chance for four options).

## 4. Publish to GitHub
- The README never calls an unchanged starting template a solution: it says "not solved yet", leaves out the
  model solution's Key ideas, the line count and the design notes, and says none of the checks pass.
  Work in progress is described as work in progress.
- The summary line under the title is the first whole sentence of the task, never cut mid-word or run together
  with a list.
- After Publish now, the page says **✓ Published to GitHub: N files in owner/repo (branch)** with an
  **Open on GitHub** link. A new publish clears an old "could not confirm" note.
- An empty repository gets two commits (the README creates the branch, then every other file in one commit)
  instead of one commit per file. GitHub's Git Data API cannot write to a repository with no commits, so one
  commit is not possible there.
- A repository GitHub no longer shows (deleted, renamed or access removed) is marked "Previously published ·
  link unavailable" with "Choose another repository the next time you publish", instead of
  "Could not check GitHub just now".

## 5. Teaching
- "New here" notes (explanation plus a worked example with its real output) on the 50 items the audit found
  using a feature with no note, including Phase 0 Lesson 1's optional challenge questions (split, join,
  append, f-strings, comprehensions, for loops, raise). Every item keeps its optional hint. One flagged item
  (ph7-e16) was a false alarm: the methods are the ones the task asks you to write.
- Every question shows a level chip. Hand-set levels are kept; others are Challenge when optional, Guided when
  the starter already has code inside the function, otherwise Independent.

## 6. Smaller fixes
- The inline "Hint" control is 44 px tall, so it is easy to tap on a phone.
- A mistyped address shows "Page not found" above the home page instead of the home page alone.

## Not changed
- Exercise labels (E1, E2, ...) follow the order in the sidebar, and a few differ from their internal ids
  (ph3-e7 is shown as E8). The ids are the keys of saved progress, so they stay as they are.
