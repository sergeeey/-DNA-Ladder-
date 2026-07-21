# Install Boyko skills + Boyko Agent (Windows)

Cloud agents cannot write to `C:\Users\sboi\`. Run this on the Windows machine.

## What gets installed

See [MANIFEST.md](./MANIFEST.md): 6 `boyko-*` skills + `boyko-agent` (`agents/navigator.md`).

## Run

In PowerShell:

```powershell
cd <path-to-dna-ladder>\tools\boyko-skills-install
Set-ExecutionPolicy -Scope Process Bypass
.\Install-BoykoSkills.ps1
```

Useful flags:

```powershell
.\Install-BoykoSkills.ps1 -DryRun
.\Install-BoykoSkills.ps1 -ForceMirrors          # also create .cursor/.agents trees
.\Install-BoykoSkills.ps1 -IncludeHook           # copy boyko_protocol_guard.py
.\Install-BoykoSkills.ps1 -RepoPath D:\src\Claude-cod-top-2026
```

Default destinations under `C:\Users\sboi\`:

- `.claude\skills\<boyko-*>\`
- `.claude\agents\navigator.md` and `boyko-agent.md`
- mirrors into `.claude\skills\extensions\`, `.cursor\skills\`, `.agents\skills\` when those trees exist

Existing targets are backed up under `.claude\backups\boyko-skills-<timestamp>\` before overwrite.

## Source pin

Clone pin: `1e1807809983b786b67a0a1e4f0cd24df273319d` from `sergeeey/Claude-cod-top-2026`.  
GitHub releases have **no** skill zip assets — install is always from git.
