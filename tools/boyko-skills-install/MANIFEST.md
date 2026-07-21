# Boyko skills + agent — inventory

**Source repo:** https://github.com/sergeeey/Claude-cod-top-2026.git  
**Pinned commit (inventory date 2026-07-21):** `1e1807809983b786b67a0a1e4f0cd24df273319d`  
**Latest release checked:** `v3.10.0` — **no downloadable assets** (skills live in git tree only).  
**Search patterns:** `boyko-*`, `*boyko*`, content `Boyko`/`Бойко`, agent frontmatter `name: boyko-agent`.

Cloud agent cannot write to `C:\Users\sboi\`. Deliverable = `Install-BoykoSkills.ps1` (run on the Windows machine).

---

## Skills found (6)

| Skill | Source path | Version (plugin.json) | Files |
|---|---|---|---|
| `boyko-goal-expansion-100` | `skills/extensions/boyko-goal-expansion-100/` | 1.0.0 | 14 |
| `boyko-knowledge-audit` | `skills/extensions/boyko-knowledge-audit/` | 3.1.1 | 6 |
| `boyko-method` | `skills/extensions/boyko-method/` | 1.3.0 | 2 |
| `boyko-specialist` | `skills/extensions/boyko-specialist/` | 1.2.0 | 2 |
| `boyko-triangle-audit` | `skills/extensions/boyko-triangle-audit/` | 1.0.0 | 2 |
| `boyko-why-ladder` | `skills/extensions/boyko-why-ladder/` | 1.0.1 | 2 |

**Total skill files:** 28

### Full source file list

```
skills/extensions/boyko-goal-expansion-100/evals/expected-properties.md
skills/extensions/boyko-goal-expansion-100/evals/test-cases.md
skills/extensions/boyko-goal-expansion-100/plugin.json
skills/extensions/boyko-goal-expansion-100/README.md
skills/extensions/boyko-goal-expansion-100/references/domain-lenses.md
skills/extensions/boyko-goal-expansion-100/references/quality-gates.md
skills/extensions/boyko-goal-expansion-100/references/scoring-model.md
skills/extensions/boyko-goal-expansion-100/scripts/detect_duplicates.py
skills/extensions/boyko-goal-expansion-100/scripts/validate_output.py
skills/extensions/boyko-goal-expansion-100/SKILL.md
skills/extensions/boyko-goal-expansion-100/templates/final-report.md
skills/extensions/boyko-goal-expansion-100/templates/idea-card.md
skills/extensions/boyko-goal-expansion-100/templates/input-template.md
skills/extensions/boyko-goal-expansion-100/templates/research-plan.md
skills/extensions/boyko-knowledge-audit/evals/evals.json
skills/extensions/boyko-knowledge-audit/plugin.json
skills/extensions/boyko-knowledge-audit/references/domain-modes.md
skills/extensions/boyko-knowledge-audit/references/hierarchy-details.md
skills/extensions/boyko-knowledge-audit/references/worked-example.md
skills/extensions/boyko-knowledge-audit/SKILL.md
skills/extensions/boyko-method/plugin.json
skills/extensions/boyko-method/SKILL.md
skills/extensions/boyko-specialist/plugin.json
skills/extensions/boyko-specialist/SKILL.md
skills/extensions/boyko-triangle-audit/plugin.json
skills/extensions/boyko-triangle-audit/SKILL.md
skills/extensions/boyko-why-ladder/plugin.json
skills/extensions/boyko-why-ladder/SKILL.md
```

---

## Agent found (1)

| Agent | Invocation name | Source path | Notes |
|---|---|---|---|
| **Boyko Agent** | `boyko-agent` | `agents/navigator.md` | Frontmatter `name: boyko-agent`. Legacy filename `navigator.md` kept for compatibility. |

No separate `boyko-agent.md` file exists in the repo; identity is the frontmatter of `navigator.md`.

---

## Related (optional, included by script flag `-IncludeHook`)

| Item | Source path | Notes |
|---|---|---|
| `boyko_protocol_guard.py` | `hooks/boyko_protocol_guard.py` | SubagentStop hook that checks boyko-agent Output Format. Needs hooks wiring in `settings.json` to be active — copy alone is not enough. |

---

## Not found / notes

- No paths under `.claude/skills/` named `boyko-*` (only `insight-architect` lives there).
- No Cursor-native skill trees in the source repo (`.cursor/`, `.agents/`).
- GitHub release assets for `v3.10.0` / `v3.8.0` / `v3.2.0`: **empty** — install from git clone.
- Teams under `agents/teams/` do not mention Boyko by name.

---

## Destination map (Windows user `sboi`)

| Artifact | Primary destination | Mirrors (if tree exists, or `-ForceMirrors`) |
|---|---|---|
| Each skill dir | `C:\Users\sboi\.claude\skills\<skill-name>\` | `...\skills\extensions\<skill-name>\` (parity with full `install.ps1`); `C:\Users\sboi\.cursor\skills\<skill-name>\`; `C:\Users\sboi\.agents\skills\<skill-name>\` |
| Boyko agent | `C:\Users\sboi\.claude\agents\navigator.md` **and** `boyko-agent.md` (same content) | `C:\Users\sboi\.cursor\agents\` (if exists / forced) |

**Overwrite strategy:** if destination exists → timestamped backup under  
`C:\Users\sboi\.claude\backups\boyko-skills-<yyyyMMdd_HHmmss>\` then robocopy/copy.
