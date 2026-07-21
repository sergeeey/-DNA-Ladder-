<#
.SYNOPSIS
    Install ALL Boyko skills + Boyko Agent onto the local Windows Claude/Cursor trees.

.DESCRIPTION
    Clones (or reuses) https://github.com/sergeeey/Claude-cod-top-2026.git, then copies:
      - skills/extensions/boyko-*  ->  %UserHome%\.claude\skills\<name>\
      - agents/navigator.md       ->  %UserHome%\.claude\agents\navigator.md
                                   +  %UserHome%\.claude\agents\boyko-agent.md
    Also mirrors into .claude\skills\extensions\, .cursor\skills\, .agents\skills
    when those trees already exist (or always if -ForceMirrors).

    Overwrite strategy: backup existing destinations, then copy (robocopy preferred).

.PARAMETER UserHome
    Windows user home. Default: C:\Users\sboi

.PARAMETER RepoUrl
    Source git URL.

.PARAMETER PinCommit
    Optional commit SHA to checkout after clone (reproducible install).
    Default matches the inventory in MANIFEST.md.

.PARAMETER RepoPath
    If set, use an existing clone instead of cloning fresh.

.PARAMETER WorkDir
    Where to clone when RepoPath is not set. Default: %TEMP%\Claude-cod-top-2026-boyko-install

.PARAMETER IncludeHook
    Also copy hooks\boyko_protocol_guard.py into .claude\hooks\
    (does NOT wire settings.json — manual / full install.sh needed for activation).

.PARAMETER ForceMirrors
    Create .cursor\skills, .agents\skills, .cursor\agents even if missing.

.PARAMETER DryRun
    List planned copies without writing.

.EXAMPLE
    Set-ExecutionPolicy -Scope Process Bypass
    .\Install-BoykoSkills.ps1

.EXAMPLE
    .\Install-BoykoSkills.ps1 -IncludeHook -ForceMirrors

.EXAMPLE
    .\Install-BoykoSkills.ps1 -RepoPath D:\src\Claude-cod-top-2026 -DryRun
#>
[CmdletBinding()]
param(
    [string]$UserHome = "C:\Users\sboi",
    [string]$RepoUrl = "https://github.com/sergeeey/Claude-cod-top-2026.git",
    [string]$PinCommit = "1e1807809983b786b67a0a1e4f0cd24df273319d",
    [string]$RepoPath = "",
    [string]$WorkDir = "",
    [switch]$IncludeHook,
    [switch]$ForceMirrors,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Write-Info([string]$Msg)  { Write-Host $Msg -ForegroundColor Cyan }
function Write-Ok([string]$Msg)    { Write-Host "  OK  $Msg" -ForegroundColor Green }
function Write-Warn([string]$Msg)  { Write-Host "  !!  $Msg" -ForegroundColor Yellow }
function Write-Skip([string]$Msg)  { Write-Host "  --  $Msg" -ForegroundColor DarkGray }

function Ensure-Dir([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path)) {
        if ($DryRun) {
            Write-Skip "Would create dir: $Path"
            return
        }
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
}

function Backup-IfExists {
    param(
        [string]$Path,
        [string]$BackupRoot
    )
    if (-not (Test-Path -LiteralPath $Path)) {
        return $false
    }
    $leaf = Split-Path -Leaf $Path
    $parentRel = Split-Path -Parent $Path
    # Keep a short relative hint under backup root
    $stampLeaf = $leaf
    $dest = Join-Path $BackupRoot $stampLeaf
    $n = 1
    while (Test-Path -LiteralPath $dest) {
        $dest = Join-Path $BackupRoot ("{0}.bak{1}" -f $stampLeaf, $n)
        $n++
    }
    if ($DryRun) {
        Write-Skip "Would backup: $Path -> $dest"
        return $true
    }
    Ensure-Dir (Split-Path -Parent $dest)
    if (Test-Path -LiteralPath $Path -PathType Container) {
        Copy-Item -LiteralPath $Path -Destination $dest -Recurse -Force
    } else {
        Copy-Item -LiteralPath $Path -Destination $dest -Force
    }
    Write-Warn "Backed up existing: $Path -> $dest"
    return $true
}

function Copy-Tree {
    param(
        [string]$Source,
        [string]$Destination
    )
    if (-not (Test-Path -LiteralPath $Source)) {
        throw "Source missing: $Source"
    }
    if ($DryRun) {
        Write-Skip "Would copy: $Source -> $Destination"
        return
    }
    Ensure-Dir (Split-Path -Parent $Destination)
    $robocopy = Get-Command robocopy -ErrorAction SilentlyContinue
    if ($robocopy -and (Test-Path -LiteralPath $Source -PathType Container)) {
        # /E copy subdirs including empty; /NFL /NDL /NJH /NJS quiet-ish; /R:1 /W:1 retry
        $null = & robocopy $Source $Destination /E /NFL /NDL /NJH /NJS /R:1 /W:1
        # robocopy exit codes 0-7 are success-ish
        if ($LASTEXITCODE -ge 8) {
            throw "robocopy failed ($LASTEXITCODE): $Source -> $Destination"
        }
    } else {
        if (Test-Path -LiteralPath $Destination) {
            Remove-Item -LiteralPath $Destination -Recurse -Force
        }
        Copy-Item -LiteralPath $Source -Destination $Destination -Recurse -Force
    }
}

function Copy-File {
    param(
        [string]$Source,
        [string]$Destination
    )
    if (-not (Test-Path -LiteralPath $Source)) {
        throw "Source missing: $Source"
    }
    if ($DryRun) {
        Write-Skip "Would copy file: $Source -> $Destination"
        return
    }
    Ensure-Dir (Split-Path -Parent $Destination)
    Copy-Item -LiteralPath $Source -Destination $Destination -Force
}

function Test-SkillInstalled {
    param([string]$SkillRoot)
    $skillMd = Join-Path $SkillRoot "SKILL.md"
    return (Test-Path -LiteralPath $skillMd)
}

# --- resolve paths ---
if (-not $WorkDir) {
    $WorkDir = Join-Path $env:TEMP "Claude-cod-top-2026-boyko-install"
}

$ClaudeDir  = Join-Path $UserHome ".claude"
$CursorDir  = Join-Path $UserHome ".cursor"
$AgentsHome = Join-Path $UserHome ".agents"

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupRoot = Join-Path $ClaudeDir ("backups\boyko-skills-" + $stamp)

Write-Info "Boyko skills + agent installer"
Write-Host "  UserHome   : $UserHome"
Write-Host "  ClaudeDir  : $ClaudeDir"
Write-Host "  PinCommit  : $PinCommit"
Write-Host "  DryRun     : $DryRun"
Write-Host "  IncludeHook: $IncludeHook"
Write-Host "  ForceMirrors: $ForceMirrors"
Write-Host ""

if (-not (Test-Path -LiteralPath $UserHome)) {
    throw "UserHome does not exist: $UserHome"
}

# --- ensure git ---
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    throw "git not found on PATH. Install Git for Windows first."
}

# --- obtain source tree ---
if ($RepoPath) {
    if (-not (Test-Path -LiteralPath $RepoPath)) {
        throw "RepoPath not found: $RepoPath"
    }
    $SourceRoot = (Resolve-Path -LiteralPath $RepoPath).Path
    Write-Ok "Using existing repo: $SourceRoot"
} else {
    if (Test-Path -LiteralPath $WorkDir) {
        Write-Warn "Removing previous workdir: $WorkDir"
        if (-not $DryRun) {
            Remove-Item -LiteralPath $WorkDir -Recurse -Force
        }
    }
    Write-Info "Cloning $RepoUrl ..."
    if (-not $DryRun) {
        $cloned = $false
        if ($PinCommit) {
            New-Item -ItemType Directory -Path $WorkDir -Force | Out-Null
            Push-Location $WorkDir
            $pinOk = $false
            try {
                git init -q
                git remote add origin $RepoUrl
                git fetch --depth 1 origin $PinCommit
                if ($LASTEXITCODE -eq 0) {
                    git checkout --quiet FETCH_HEAD
                    if ($LASTEXITCODE -eq 0) { $pinOk = $true }
                }
            } finally {
                Pop-Location
            }
            if (-not $pinOk) {
                Write-Warn "Pinned shallow fetch failed; falling back to full clone + checkout..."
                if (Test-Path -LiteralPath $WorkDir) {
                    Remove-Item -LiteralPath $WorkDir -Recurse -Force
                }
                git clone $RepoUrl $WorkDir
                if ($LASTEXITCODE -ne 0) { throw "git clone failed" }
                Push-Location $WorkDir
                try {
                    git checkout --quiet $PinCommit
                    if ($LASTEXITCODE -ne 0) { throw "Could not checkout pin $PinCommit" }
                } finally {
                    Pop-Location
                }
            }
            $got = (git -C $WorkDir rev-parse HEAD).Trim()
            Write-Ok "Checked out $got (requested pin $PinCommit)"
            $cloned = $true
        }
        if (-not $cloned) {
            git clone --depth 1 $RepoUrl $WorkDir
            if ($LASTEXITCODE -ne 0) { throw "git clone failed" }
        }
    } else {
        Write-Skip "Would clone $RepoUrl -> $WorkDir and checkout $PinCommit"
    }
    $SourceRoot = $WorkDir
}

$SkillsSrcRoot = Join-Path $SourceRoot "skills\extensions"
$AgentSrc      = Join-Path $SourceRoot "agents\navigator.md"
$HookSrc       = Join-Path $SourceRoot "hooks\boyko_protocol_guard.py"

if (-not $DryRun) {
    if (-not (Test-Path -LiteralPath $SkillsSrcRoot)) {
        throw "skills/extensions not found under $SourceRoot"
    }
    if (-not (Test-Path -LiteralPath $AgentSrc)) {
        throw "agents/navigator.md (boyko-agent) not found under $SourceRoot"
    }
}

$BoykoSkills = @(
    "boyko-goal-expansion-100",
    "boyko-knowledge-audit",
    "boyko-method",
    "boyko-specialist",
    "boyko-triangle-audit",
    "boyko-why-ladder"
)

# Discover any extra boyko-* dirs present in source (future-proof)
if (-not $DryRun) {
    $discovered = Get-ChildItem -LiteralPath $SkillsSrcRoot -Directory -Filter "boyko-*" |
        Select-Object -ExpandProperty Name
    foreach ($d in $discovered) {
        if ($BoykoSkills -notcontains $d) {
            Write-Warn "Extra boyko skill discovered (will install): $d"
            $BoykoSkills += $d
        }
    }
}

Ensure-Dir $ClaudeDir
Ensure-Dir (Join-Path $ClaudeDir "skills")
Ensure-Dir (Join-Path $ClaudeDir "agents")
if (-not $DryRun) { Ensure-Dir $BackupRoot }

# Mirror skill destination roots
$SkillDestRoots = New-Object System.Collections.Generic.List[string]
$SkillDestRoots.Add((Join-Path $ClaudeDir "skills"))

$extRoot = Join-Path $ClaudeDir "skills\extensions"
if ((Test-Path -LiteralPath $extRoot) -or $ForceMirrors) {
    Ensure-Dir $extRoot
    $SkillDestRoots.Add($extRoot)
} else {
    Write-Skip "Skip .claude\skills\extensions (missing; pass -ForceMirrors to create)"
}

$cursorSkills = Join-Path $CursorDir "skills"
if ((Test-Path -LiteralPath $cursorSkills) -or $ForceMirrors) {
    Ensure-Dir $cursorSkills
    $SkillDestRoots.Add($cursorSkills)
} else {
    Write-Skip "Skip .cursor\skills (missing; pass -ForceMirrors to create)"
}

$agentsSkills = Join-Path $AgentsHome "skills"
if ((Test-Path -LiteralPath $agentsSkills) -or $ForceMirrors) {
    Ensure-Dir $agentsSkills
    $SkillDestRoots.Add($agentsSkills)
} else {
    Write-Skip "Skip .agents\skills (missing; pass -ForceMirrors to create)"
}

Write-Info "Installing $($BoykoSkills.Count) Boyko skills..."
$installedSkills = @()
foreach ($name in $BoykoSkills) {
    $src = Join-Path $SkillsSrcRoot $name
    if (-not $DryRun -and -not (Test-Path -LiteralPath $src)) {
        Write-Warn "Missing skill source: $src"
        continue
    }
    foreach ($root in $SkillDestRoots) {
        $dest = Join-Path $root $name
        Backup-IfExists -Path $dest -BackupRoot (Join-Path $BackupRoot ("skills-" + (Split-Path -Leaf $root)))
        Copy-Tree -Source $src -Destination $dest
        if (-not $DryRun) {
            if (Test-SkillInstalled $dest) {
                Write-Ok "$name -> $dest"
            } else {
                Write-Warn "Copied but SKILL.md missing at $dest"
            }
        }
    }
    $installedSkills += $name
}

Write-Info "Installing Boyko Agent (agents/navigator.md)..."
$agentDestRoots = New-Object System.Collections.Generic.List[string]
$agentDestRoots.Add((Join-Path $ClaudeDir "agents"))

$cursorAgents = Join-Path $CursorDir "agents"
if ((Test-Path -LiteralPath $cursorAgents) -or $ForceMirrors) {
    Ensure-Dir $cursorAgents
    $agentDestRoots.Add($cursorAgents)
} else {
    Write-Skip "Skip .cursor\agents (missing; pass -ForceMirrors to create)"
}

foreach ($root in $agentDestRoots) {
    foreach ($fname in @("navigator.md", "boyko-agent.md")) {
        $dest = Join-Path $root $fname
        Backup-IfExists -Path $dest -BackupRoot (Join-Path $BackupRoot "agents")
        Copy-File -Source $AgentSrc -Destination $dest
        if (-not $DryRun) {
            Write-Ok "boyko-agent -> $dest"
        }
    }
}

if ($IncludeHook) {
    Write-Info "Installing boyko_protocol_guard.py hook (optional)..."
    $hooksDir = Join-Path $ClaudeDir "hooks"
    Ensure-Dir $hooksDir
    $hookDest = Join-Path $hooksDir "boyko_protocol_guard.py"
    Backup-IfExists -Path $hookDest -BackupRoot (Join-Path $BackupRoot "hooks")
    if (-not $DryRun -and (Test-Path -LiteralPath $HookSrc)) {
        Copy-File -Source $HookSrc -Destination $hookDest
        Write-Ok "hook -> $hookDest"
        Write-Warn "Hook file copied only — wire it into settings.json (or run full install.ps1) to activate."
    } elseif ($DryRun) {
        Copy-File -Source $HookSrc -Destination $hookDest
    } else {
        Write-Warn "Hook source missing: $HookSrc"
    }
}

# --- verification summary ---
Write-Host ""
Write-Info "Verification"
$fail = 0
foreach ($name in $installedSkills) {
    $primary = Join-Path (Join-Path $ClaudeDir "skills") $name
    if ($DryRun) {
        Write-Skip "Would verify $primary\SKILL.md"
        continue
    }
    if (Test-SkillInstalled $primary) {
        Write-Ok "SKILL.md present: $name"
    } else {
        Write-Warn "MISSING SKILL.md: $primary"
        $fail++
    }
}
$nav = Join-Path (Join-Path $ClaudeDir "agents") "navigator.md"
$ba  = Join-Path (Join-Path $ClaudeDir "agents") "boyko-agent.md"
if (-not $DryRun) {
    foreach ($p in @($nav, $ba)) {
        if (Test-Path -LiteralPath $p) {
            $head = Get-Content -LiteralPath $p -TotalCount 5 -ErrorAction SilentlyContinue
            $isBoyko = ($head -join "`n") -match "name:\s*boyko-agent"
            if ($isBoyko) { Write-Ok "Agent frontmatter boyko-agent: $p" }
            else { Write-Warn "Agent file present but frontmatter unexpected: $p"; $fail++ }
        } else {
            Write-Warn "MISSING agent file: $p"
            $fail++
        }
    }
}

Write-Host ""
if ($DryRun) {
    Write-Info "Dry run complete — no files written."
} elseif ($fail -eq 0) {
    Write-Host "Install complete. Backup root: $BackupRoot" -ForegroundColor Green
    Write-Host "Restart Claude Code / Cursor (or reload window) so skills/agents are rediscovered." -ForegroundColor Green
} else {
    Write-Host "Install finished with $fail verification issue(s). See warnings above." -ForegroundColor Yellow
    exit 1
}
