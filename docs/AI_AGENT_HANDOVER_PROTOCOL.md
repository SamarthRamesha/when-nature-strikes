# AI Agent Handover Protocol — When Nature Strikes

**Applies to every AI agent, in every tool, on every account.** This protocol lives in the repository
on purpose: continuity must not depend on a chatbot's memory, a vendor's session history, or the same
person being available. If you are an AI agent reading this, these rules are binding for your session.

Followed correctly, any agent — whatever model or product it runs in — can pick this project up from
the repository alone, continue it without redoing finished work, and leave it ready for the person
after them.

---

## 1. Non-negotiables

1. Read `README.md`.
2. Read `docs/TEAM_HANDOVER.md`.
3. Read this file (`docs/AI_AGENT_HANDOVER_PROTOCOL.md`).
4. Inspect the current Git branch and working tree (`git status`, `git log`, `git diff`) before editing.
5. Identify the previous owner's completed work.
6. Identify the current owner's responsibilities from `docs/TEAM_HANDOVER.md`.
7. **Inspect the actual files before trusting any completion claim** — including claims in these
   documents.
8. Continue from the existing implementation instead of rebuilding finished work.
9. Track every task as **COMPLETE**, **IN PROGRESS**, **BLOCKED** or **NOT STARTED**, with evidence.
10. Never overwrite another teammate's work: notebooks, charts, scripts and datasets belong to named
    owners; change them only when the task requires it and say so.

## 2. Start-of-session procedure

```bash
git status                     # uncommitted or untracked work must never be discarded silently
git log --oneline -10          # who did what, most recent first
git branch -a                  # which branch you are on and what else exists
```

Then, in order:

1. Read the three documents in §1.
2. Read `docs/PROJECT_OVERVIEW.md` for scope and limitations.
3. Check the phase ledger in `docs/TEAM_HANDOVER.md` §2 — that is the current state of the project.
4. Open the files that the task touches. Do not infer their contents from the documentation.
5. If the task is data-related, run the two validation scripts (§10) **before** changing anything, so
   you know the baseline is green.
6. Confirm in one sentence, in your own working notes, who the current owner is and what you are
   allowed to change.

If `git status` shows uncommitted work that is not yours, **stop and ask the user** what to do with it.
Never stash, reset, checkout or delete it.

## 3. Evidence standard

A task is **COMPLETE** only when you can point to something you did that shows it:

| Acceptable evidence | Not acceptable |
|---|---|
| A command you ran, with its exit status and output | "The document says it is complete" |
| A file you opened and verified (row counts, columns, values) | "The previous chat said so" |
| A hash comparison against `HEAD` | A commit message |
| A script exit code of 0 with the expected counts | Memory of an earlier session |
| A rendered or parsed artefact you inspected | A filename that looks right |

A document that claims completion is a **claim to verify**, never proof. Where a claim cannot be
verified in this environment (for example EM-DAT's PDF field definitions), say so explicitly and keep
the claim qualified.

## 4. Status vocabulary

Use exactly these four states and no synonyms:

- **COMPLETE** — verified in this session (or verified in a previous session with the evidence still
  reproducible; re-run the cheap check before saying so).
- **IN PROGRESS** — started, unfinished, and the file or branch is named.
- **BLOCKED** — cannot proceed without something outside the repository (a teammate's file, a teacher
  decision, a credential). Say precisely what unblocks it.
- **NOT STARTED** — assigned but nothing exists.

## 5. Automatic next-owner preparation

**Even if the user never mentions a handover**, prepare the repository for the next person before you
consider your own work finished. This is a standing requirement of this project.

1. Identify the next responsible teammate from the team allocation in `docs/TEAM_HANDOVER.md` §1.
2. Work out what that person needs to know that they cannot infer from the files.
3. Update `docs/TEAM_HANDOVER.md`: phase ledger, ownership, what you completed, changed files,
   validation evidence, outstanding tasks, blockers.
4. Update `README.md` §Current project status if the status materially changed. Never mark the
   dashboard complete without a real, verified `.pbix`.
5. Update `docs/NEXT_SESSION_PROMPT.md` so a different chatbot can resume from it.
6. Give exact setup and execution instructions that you actually ran.
7. Give the next owner an ordered task list with a "done when" condition per task.
8. Record anything you could not verify, and why.
9. Preserve attribution: append to the change log; never rewrite another owner's record.
10. Leave the working tree in a state the user can review — do not leave scratch files behind.
11. If your work changes the data or the numbers, re-run the validation and verification scripts and
    update `docs/DATA_QUALITY_REPORT.md` accordingly.

## 6. Artefacts to update before finishing

| Artefact | What must be true |
|---|---|
| `docs/TEAM_HANDOVER.md` | Reflects reality: ownership, status, next actions, change log entry |
| `docs/NEXT_SESSION_PROMPT.md` | A fresh chat can start work from it with no prior context |
| `README.md` | Status section and structure still accurate |
| `docs/FINAL_SUBMISSION_CHECKLIST.md` | Any deliverable you advanced is updated |
| `docs/DATA_QUALITY_REPORT.md` / `analysis/outputs/*.json` | Regenerated if data or checks changed |
| `docs/INTEGRATION_HANDOVER.md` §9 | QA rows checked only when you have the evidence |

## 7. Protected artefacts

These change **only** when the task explicitly requires it, and never by hand-editing:

| Protected | Rule |
|---|---|
| `data/source/EM-DAT Custom Request Oct 31 2026.xlsx` | Never modify. Verify its SHA-256 against `analysis/outputs/data_quality_report.json`. |
| `data/processed/*.csv` | Generated by `scripts/prepare_emdat.py`. Never hand-edit. If regenerated, prove the output is byte-identical or explain every difference. |
| `analysis/*.ipynb` | Owned by Shashank. Do not edit cells or clear outputs; their relative paths assume the `analysis/` directory. |
| `analysis/outputs/*.csv`, `visualizations/**/*.png` | Owned by Shashank / generated by the notebooks. The verification script checks 89 committed values in these files. |
| `scripts/prepare_emdat.py` | The reproducibility contract. Change only with the data owner's authorisation and a byte-identical (or documented) rebuild. |
| `docs/PROJECT_APPROVAL_SUMMARY.md` | Approved scope record. Extend, do not reinterpret. |

Before you finish:

```bash
git diff --stat -- data/ analysis/*.ipynb visualizations/ scripts/prepare_emdat.py
# must be empty unless the task explicitly changed them
```

## 8. Safety and integrity

- **Never commit, push, merge, rebase, tag or delete** anything without the current user's explicit
  authorisation for that specific action.
- **Never force-push** and never rewrite published history.
- **Never expose credentials, tokens or secrets** — not in files, not in commands, not in replies.
- **Never silently discard uncommitted work**; if it blocks you, ask.
- **Never invent files, results, citations or numbers.** If something is missing, say it is missing.
- **Never redistribute the EM-DAT export or derived CSVs** — restricted project materials.
- **Preserve attribution.** Record who did what in the change log and in the submission's contribution
  record. Do not present another teammate's work as your own.
- Keep the repository free of scratch files, caches, personal environment files and OS metadata.

## 9. When to stop and ask the user

- Uncommitted work that is not yours would be affected by the task.
- The task requires committing, pushing, merging, publishing or deleting data.
- A required input is missing (a `.pbix`, a teacher decision, a credential, a teammate's file).
- Two documents contradict each other on a fact you must rely on.
- Completing the task would require changing a protected artefact or another owner's work.

Ask one focused question with the options you can see, then continue once answered.

## 10. Verification commands

```bash
# Baseline — both must exit 0 on the committed data
python scripts/validate_project_data.py     # 71 checks: 69 pass, 2 documented warnings, 0 fail
python scripts/verify_eda_findings.py       # 6 findings, 89/89 committed values reproduced

# Only when the data or the pipeline legitimately changed
python -m pip install -r requirements.txt
python scripts/prepare_emdat.py             # rewrites data/processed/*.csv in place

# Repository hygiene
git diff --check                            # no whitespace errors
git status --short                          # no unintended files
```

Reproducibility check (safe: works on a copy, never on the repository):

```bash
rm -rf /tmp/repro && mkdir -p /tmp/repro
git archive HEAD | tar -x -C /tmp/repro
cd /tmp/repro && python scripts/prepare_emdat.py
for f in data/processed/*.csv; do cmp "$f" "/path/to/repo/$f" && echo "IDENTICAL $f"; done
```

## 11. Recursion clause

Your handover is not finished when your task is. Before you end the session, ensure that the *next*
agent — possibly a different model, account or company — can repeat this protocol without you. That
means `docs/NEXT_SESSION_PROMPT.md` and `docs/TEAM_HANDOVER.md` must be accurate as of your last
change, and this protocol must remain in place unweakened.

Do not remove or soften these rules to make your own session easier. If a rule blocks you, report the
blocker in `docs/TEAM_HANDOVER.md` §Blockers and in your reply.

## 12. Pre-finish checklist

```text
[ ] Read README.md, TEAM_HANDOVER.md, AI_AGENT_HANDOVER_PROTOCOL.md
[ ] Inspected git status / log / diff before editing
[ ] Identified previous owner's completed work and current owner
[ ] Verified claims against files, not documents
[ ] Ran the validation scripts and they exit 0
[ ] Protected artefacts unchanged (or change authorised and documented)
[ ] data/ and analysis artefacts byte-checked where touched
[ ] TEAM_HANDOVER.md updated (status, evidence, tasks, change log)
[ ] NEXT_SESSION_PROMPT.md updated
[ ] README.md status accurate (no unverified completion claims)
[ ] FINAL_SUBMISSION_CHECKLIST.md updated if a deliverable moved
[ ] No secrets, no scratch files, no caches committed
[ ] No commit/push/merge/delete without explicit authorisation
[ ] Next owner named, with an ordered task list
```

## 13. Known traps in this repository

1. **Grain.** 18,060 country-impact rows are *not* 18,060 disasters. Frequency is
   `DISTINCTCOUNT(Event ID)` = 15,727.
2. **`Unique Events` in `natural_country_year_type_summary.csv` is not additive** — it sums to 18,060.
3. **Blanks are not zeros.** Never `COALESCE`, `+0` or "replace empty with 0".
4. **Notebook paths.** Notebook 00 reads `../data/processed/...`; notebooks 01–05 resolve the root with
   `Path.cwd()` plus one parent. Start Jupyter from the repository root or `analysis/`, and do not move
   the notebooks deeper without fixing their code.
5. **CSVs are UTF-8 with BOM.** Read with `encoding='utf-8-sig'` in Python.
6. **`prepare_emdat.py` rewrites the CSVs in place.** Re-run it only when the source changes, and prove
   the rebuild is byte-identical.
7. **No `.pbix` exists.** Anything described as "dashboard complete" must be treated as unverified.
8. **`EM_DAT_Documentation.pdf` is not text-extractable here** (CID-encoded streams); field meanings
   rest on EM-DAT's published documentation plus the observed fill rates in `DATA_DICTIONARY.md`.
