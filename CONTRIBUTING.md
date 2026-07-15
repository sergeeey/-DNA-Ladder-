# Contributing to DNA Ladder

## Tracks first

Put new work under the matching track:

- Super-enhancer / LLPS / G4 / R-loop / heritability → `tracks/se_llps/`
- Alu/SVA rare SNV vs 3D/activity (C1 / prospective panel) → `tracks/te_alu_3d/`
- Shared rejects / meta-closures → `null_results/` at **repo root**

Do not mix track data directories. If a hypothesis spans tracks, open an Issue and agree on a home track first.

## Experiment folder contract (`se_llps`)

```
tracks/se_llps/experiments/exp_<slug>/
  claim.md      # pre-registered
  decision.md   # PASS / REJECT / INCONCLUSIVE + what it does NOT mean
  results.json  # numeric evidence
```

Scripts live in `tracks/se_llps/scripts/`; verifiers in `tracks/se_llps/tests/`.

## TE desk contract (`te_alu_3d`)

- Claims and GO notes: `09_outputs/prospective/`
- Runnable desk code: `pilot_scaffold/`
- Do **not** commit `.env`, API keys, sealed holdout VCFs/TSVs, or full `.hic` matrices
- Do **not** open the holdout or reshape Stage-3 after reporter results without a written human GO

## Null results

Every REJECT / INCONCLUSIVE / CLOSED must get a short filing under `null_results/` and a row in `null_results/INDEX.md`. Include “what this does NOT mean”.

## What not to commit

- `.env`, keys, credentials notes with local paths that imply a live key is in-repo
- `*.hic`, juicer `.jar`, clinvar/rmsk full dumps, holdout raw files
- `__pycache__`, large OT dumps, Capture-C bait quote blobs unless they are small text

See root `.gitignore` and each track's `DATA.md`.

## PR hygiene

1. One track per PR when possible
2. Point to `claim.md` / decision artifact
3. Say whether the result updates `null_results/`
4. Keep secrets out of the diff

## Multi-agent / multi-session git coordination

This repo is worked on by more than one agent/session at once (Claude Code + Cursor,
sometimes concurrently). The track split (`se_llps` vs `te_alu_3d`) already prevents most
real conflicts -- 2026-07-15's two concurrent pushes (monorepo restructure + a P3
kill-test, both from a Cursor session, landed while a Claude Code session was mid-work)
resolved cleanly with zero real content conflicts, purely because neither session's changes
touched the other's track. Keep doing that. A few rules to keep it that way:

- **`git fetch` before every push, not just once per session.** A "fetch first" rejection
  is expected in a multi-agent repo, not a bug -- treat it as routine, not alarming.
- **Never force-push `master`.** If push is rejected, `git fetch` + `git log
  <local>..origin/master` + `git show --stat <new-commit>` to see what changed *before*
  merging. If the new commit touches only the other track, the merge is safe and
  low-risk; if it touches your own track or shared root files, read the diff properly
  before resolving conflicts.
- **Root-level shared files are the highest-conflict-risk zone**: `README.md`,
  `CLAUDE.md`, `CONTRIBUTING.md`, `null_results/INDEX.md`. Both tracks touch these. Prefer
  small, additive edits (append a row/section) over large rewrites when another
  session might be active, and expect to reconcile via `git merge` (usually trivial for
  append-only changes like `null_results/INDEX.md` rows) rather than needing manual
  conflict resolution.
- **Push reasonably often rather than batching many local commits.** Smaller, more
  frequent pushes shrink the reconciliation window and make `git show --stat` on the
  other session's commits cheap to review.
- **On an add/add conflict for a file you never authored** (check with `git log --follow
  -- <path>` -- if your own history shows it only entering via a merge commit, not a
  commit you wrote), it's safe to take the other side's version wholesale
  (`git checkout --theirs <path>`) rather than hand-merging content you don't own.
