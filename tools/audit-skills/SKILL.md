---
name: audit-skills
description: Audit the user's skill ecosystem - central repo at ~/.skills/, OpenCode global at ~/.config/opencode/skills/, Claude global at ~/.claude/skills/, and project-level .opencode/skills + .claude/skills. Report duplicates, name conflicts, malformed frontmatter, broken junctions, drifted copies, missing SKILL.md, and orphan entries. Use this when user asks to audit, check, validate, lint, or diff their skills. Read-only by default; suggests fixes but never mutates without confirmation.
---

# audit-skills

## Purpose

Provide a single, read-only health report of the user's entire skill ecosystem.
This skill **inspects and reports**. It never creates, modifies, links, or deletes
anything. All remediation is delegated to sister skills (`install-skill`,
`link-skills`) and only after explicit user confirmation.

The output is a Markdown report covering every known discovery location an LLM
client (OpenCode, Claude Desktop/Code, project-scoped agents) might consult, so
the user can quickly answer:

- "Is my central repo the source of truth?"
- "Did anything drift between central and the global mirrors?"
- "Are any junctions broken after a Windows update or a cloud-sync hiccup?"
- "Do I have orphan skills sitting in `~/.claude/skills` that aren't in central?"
- "Is any SKILL.md malformed and silently being skipped by the loader?"

## When to Use

Trigger this skill when the user says any of:

- "audit my skills"
- "check / validate / lint my skills"
- "are my skills in sync?"
- "diff central vs global skills"
- "why isn't skill X showing up?"
- "find broken skill links / junctions"
- "list duplicate or orphan skills"

If the user asks to *fix* something, run this audit first, present findings,
then hand off to `install-skill` or `link-skills` only after the user
confirms.

## Scope of Audit

By default, scan **all** locations below. If a location does not exist, skip it
and emit an `INFO` note. Do not error out.

| ID  | Role                  | Path                                            | Depth of skills |
| --- | --------------------- | ----------------------------------------------- | --------------- |
| C   | Central (canonical)   | `$env:USERPROFILE\.skills`                      | depth 2 (`<category>\<skill>\SKILL.md`) |
| OG  | OpenCode global       | `$env:USERPROFILE\.config\opencode\skills`      | depth 1 (`<skill>\SKILL.md`) |
| CG  | Claude global         | `$env:USERPROFILE\.claude\skills`               | depth 1 (`<skill>\SKILL.md`) |
| OP  | Project OpenCode      | `<repoRoot>\.opencode\skills`                   | depth 1 |
| CP  | Project Claude        | `<repoRoot>\.claude\skills`                     | depth 1 |

`<repoRoot>` is auto-detected by walking up from the current working directory
and stopping at the first ancestor containing any of: `.git`, `package.json`,
`pom.xml`, `AGENTS.md`. If no root is found, skip OP/CP with an `INFO` note.

**Skill detection rule (strict):**

- A *skill* is a directory that **directly contains** `SKILL.md`.
- In **central** (`C`), valid skills live at depth 2: `~/.skills/<category>/<skill>/SKILL.md`.
- In all other locations, valid skills live at depth 1: `<root>/<skill>/SKILL.md`.
- Anything else (loose files, deeper nesting, missing `SKILL.md`) is reported
  under check `C6` (malformed) or simply ignored if clearly unrelated.

**Project `.opencode` artifact rule:**

- Project skills require only `<repoRoot>\.opencode\skills\<skill>\SKILL.md`.
- Files such as `<repoRoot>\.opencode\package.json`, `package-lock.json`, `bun.lock`, `.gitignore`, and the folder `node_modules\` are **not** skill requirements.
- If present, report them as an `INFO` note named `OP-artifacts` only when auditing the project root. Treat them as likely OpenCode plugin/npm artifacts. Do not mark them as skill errors and never suggest `install-skill` or `link-skills` as the fix.
- This audit skill is read-only: do not delete or modify those artifacts. If the user asks to clean them, first check for `.opencode\plugins\`, `.opencode\tools\`, `opencode.json`, or `opencode.jsonc`, then propose a manual cleanup plan.

## Inputs

The skill takes **no required arguments**. By default it scans all five
locations above. Optional behavior modifiers the user may request:

- "only check central" → restrict to `C`.
- "only check global" → restrict to `OG` + `CG`.
- "only check this project" → restrict to `OP` + `CP`.
- "deep diff" → for `C2` drift, also diff every file inside the skill folder,
  not just `SKILL.md` (slower; mention but do not perform unless asked).

## Checks Performed

| ID  | Severity default | What it catches |
| --- | ---------------- | --------------- |
| C1  | WARNING          | Same skill name present in two or more locations. Central is canonical; copies elsewhere are expected when linked, but should match central. |
| C2  | ERROR            | Drift: same name, but `SKILL.md` SHA256 differs between locations. Indicates a stale copy or hand-edit outside central. |
| C3  | ERROR / WARNING  | Frontmatter validity. ERROR if missing delimiters or required keys; WARNING if `description` is short or `name` violates `[a-z0-9-]+`. |
| C4  | ERROR            | Broken junction: directory at OG/CG/OP/CP is a junction whose target no longer resolves. Skill is invisible to its loader. |
| C5  | INFO / WARNING   | Orphan: skill present at OG/CG/OP/CP but absent in central. INFO if it looks intentional; WARNING if it shadows a removed central skill. |
| C6  | ERROR            | Empty or malformed `SKILL.md` (zero bytes, missing both `---` delimiters, unreadable). |
| C7  | ERROR            | Permission failure: current user cannot read the skill folder or its `SKILL.md`. |

## Reporting Format

Always output Markdown in this shape:

```markdown
# Skill Audit Report

_Scanned: <UTC timestamp>; Host: <COMPUTERNAME>; User: <USERNAME>_

## Summary

| Location | Path | Skills found | ERROR | WARNING | INFO |
| -------- | ---- | -----------: | ----: | ------: | ---: |
| Central (C)  | ... | 42 | 0 | 1 | 0 |
| OpenCode Global (OG) | ... | 12 | 1 | 0 | 2 |
| Claude Global (CG)   | ... | 10 | 0 | 1 | 1 |
| Project OpenCode (OP) | ... | 0 | 0 | 0 | 1 (skipped: not present) |
| Project Claude (CP)   | ... | 0 | 0 | 0 | 1 (skipped: not present) |

**Totals:** ERROR=1, WARNING=2, INFO=4

## Findings

### Central (C) — `C:\Users\WZY\.skills`
- (none)

### OpenCode Global (OG) — `C:\Users\WZY\.config\opencode\skills`
- **[ERROR][C4] git-master** — broken junction
  - Path: `C:\Users\WZY\.config\opencode\skills\git-master`
  - Target: `C:\Users\WZY\.skills\process\git-master` (missing)
  - Fix: invoke `link-skills` to re-link `git-master` to OpenCode-Global; this recreates the junction.

### Claude Global (CG) — `C:\Users\WZY\.claude\skills`
- **[WARNING][C5] foo-helper** — orphan, not in central
  - Path: `C:\Users\WZY\.claude\skills\foo-helper`
  - Fix: invoke `install-skill` on `C:\Users\WZY\.claude\skills\foo-helper` with category `process` to import,
    or have the user remove it manually after confirmation.

## Notes
- Project locations not detected (no repo root found above CWD).
```

Rules for the report:

- One section per location, in order C, OG, CG, OP, CP.
- Findings sorted: ERROR > WARNING > INFO, then alphabetical by skill name.
- Each finding line includes: `[SEVERITY][CHECK_ID] skill-name — short reason`.
- Always include a Fix line referencing **install-skill** or **link-skills** by
  name. Never fabricate other tools.
- Exception: `OP-artifacts` informational notes about `.opencode` npm/plugin artifacts should not reference `install-skill` or `link-skills`; explain that they are outside skill management and require separate user-confirmed cleanup if desired.
- If a SKILL.md happens to contain something that looks like a token (`ghp_…`,
  `sk-…`, `xox[bp]-…`, AWS-style `AKIA…`, long hex/base64 over 32 chars next to
  the words `key`, `token`, `secret`, `password`), **redact the value** as
  `<redacted>` in any quoted snippet in the report.

## Severity Levels

- **ERROR** — Blocks discovery or correctness. Loader will skip the skill,
  the link is dead, or the file is unreadable. User must fix.
- **WARNING** — Works today but is risky: drift between copies, orphan likely
  to confuse, weak frontmatter that hurts triggering.
- **INFO** — Style or environmental notes (location absent, optional cleanup).

## Suggested Fixes (mapped to sister skills)

All "fixes" are natural-language invocations of sister skills, not CLI commands. There is no `link-skills`/`install-skill` executable; these are LLM-invoked skills, so describe the action and let the agent route to the right sister skill.

| Finding pattern                                | Suggested invocation (natural language) |
| ---------------------------------------------- | --------------------------------------- |
| C1 duplicate where copy matches central         | No action; informational. |
| C2 drift, central is correct                    | Invoke `link-skills`: re-link `<name>` from central to `<OG\|CG\|OP\|CP>`, choosing Overwrite when prompted. |
| C2 drift, copy is newer / hand-edited           | Ask user. If keep edits: invoke `install-skill` with the copy's path and category to import it into central, then invoke `link-skills` to re-mirror. |
| C3 frontmatter invalid                          | Open the offending `SKILL.md` and fix manually; do not auto-edit. |
| C4 broken junction                              | Invoke `link-skills`: re-link `<name>` to `<where>`; this recreates the junction. |
| C5 orphan, user wants to keep                   | Invoke `install-skill` with the orphan's path and an inferred category to bring it into central. |
| C5 orphan, user wants to drop                   | Confirm with user, then they remove manually. This skill never deletes. |
| C6 malformed SKILL.md                           | User repairs file; re-run audit. |
| C7 permission failure                           | User adjusts ACLs; out of scope here. |
| OP-artifacts npm/plugin files under `.opencode` | Informational only; outside skill management. If user wants cleanup, inspect plugins/tools/config first and ask for confirmation. |

Never invent fix actions beyond invoking `install-skill` or `link-skills`, except for `OP-artifacts`, which is explicitly outside skill management and should only suggest user-confirmed cleanup after inspecting plugin/tool/config usage.

## Workflow

Follow these steps in order. Each step is a discrete PowerShell phase.

1. **Resolve locations.** Compute `C`, `OG`, `CG`. Walk up from `(Get-Location).Path`
   to find `<repoRoot>`; if found, compute `OP`, `CP`. For each location, record
   `Exists = Test-Path -LiteralPath $path`.
2. **Enumerate candidate folders per location** using the depth rules above.
   Do **not** filter on `SKILL.md` yet, because broken junctions must still be
   surfaced by `C4`. Record at minimum: `Name`, `Folder`, `SkillMdPath`,
   `HasSkillMd`, `IsJunction`, `LinkTarget`, `LinkTargetExists`.
3. **Read and parse frontmatter** for each `SKILL.md`. Extract `name` and
   `description`. Run check `C3`. Run check `C6` if the file is empty / has no
   second `---`.
4. **Hash every `SKILL.md`** with `Get-FileHash -Algorithm SHA256`. Group by
   skill name across locations.
5. **Cross-location analysis.**
   - For each name appearing in 2+ locations: emit `C1` (WARNING informational
     unless a stronger finding fires).
   - For each name with mismatched hashes across locations: emit `C2` ERROR.
   - For each name in OG/CG/OP/CP missing from C: emit `C5` INFO/WARNING.
6. **Junction analysis (C4).** For OG/CG/OP/CP only, for every skill folder
   check `(Get-Item -LiteralPath $p).LinkType`. If `Junction` or `SymbolicLink`,
   resolve target and verify existence. Flag if missing.
7. **Permissions (C7).** Wrap each read in `try { ... } catch { ... }`. Any
   failure becomes a `C7` ERROR finding for that path.
8. **Render the report** using the format above. Include the Summary table,
   per-location sections, totals, and any skipped-location notes.
9. **Stop.** Do not propose to apply fixes automatically. Offer to call
   `install-skill` or `link-skills` only after the user explicitly confirms.

## PowerShell Reference Snippets

These are reference snippets, not a script bundle. Adapt inline as needed. All
are Windows PowerShell 5.1 compatible.

### Resolve locations and repo root

```powershell
$U = $env:USERPROFILE
$Locations = @(
    [pscustomobject]@{ Id='C';  Role='Central';          Path=Join-Path $U '.skills';                       Depth=2 }
    [pscustomobject]@{ Id='OG'; Role='OpenCode-Global';  Path=Join-Path $U '.config\opencode\skills';        Depth=1 }
    [pscustomobject]@{ Id='CG'; Role='Claude-Global';    Path=Join-Path $U '.claude\skills';                 Depth=1 }
)

function Find-RepoRoot {
    param([string]$Start = (Get-Location).Path)
    $markers = @('.git','package.json','pom.xml','AGENTS.md')
    $dir = (Resolve-Path -LiteralPath $Start).Path
    while ($true) {
        foreach ($m in $markers) {
            if (Test-Path -LiteralPath (Join-Path $dir $m)) { return $dir }
        }
        $parent = Split-Path -Parent $dir
        if (-not $parent -or $parent -eq $dir) { return $null }
        $dir = $parent
    }
}

$root = Find-RepoRoot
if ($root) {
    $Locations += [pscustomobject]@{ Id='OP'; Role='OpenCode-Project'; Path=Join-Path $root '.opencode\skills'; Depth=1 }
    $Locations += [pscustomobject]@{ Id='CP'; Role='Claude-Project';   Path=Join-Path $root '.claude\skills';   Depth=1 }
}
```

### Enumerate skills per location

```powershell
function Get-SkillFolders {
    param([string]$Root, [int]$Depth)
    if (-not (Test-Path -LiteralPath $Root)) { return @() }
    if ($Depth -eq 1) {
        Get-ChildItem -LiteralPath $Root -Directory -Force -ErrorAction SilentlyContinue
    } else {
        Get-ChildItem -LiteralPath $Root -Directory -Force -ErrorAction SilentlyContinue | ForEach-Object {
            Get-ChildItem -LiteralPath $_.FullName -Directory -Force -ErrorAction SilentlyContinue
        }
    }
}
```

### Junction detection (C4)

```powershell
function Get-LinkInfo {
    param([string]$Path)
    try {
        $item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
        $type = $item.LinkType   # $null, 'Junction', 'SymbolicLink', 'HardLink'
        $target = $null
        if ($type) { $target = ($item.Target | Select-Object -First 1) }
        $targetExists = $true
        if ($type -and $target) { $targetExists = Test-Path -LiteralPath $target }
        [pscustomobject]@{ IsLink=[bool]$type; LinkType=$type; Target=$target; TargetExists=$targetExists }
    } catch {
        [pscustomobject]@{ IsLink=$false; LinkType=$null; Target=$null; TargetExists=$false }
    }
}
```

### Tiny frontmatter parser (no yaml module)

```powershell
function Read-Frontmatter {
    param([string]$SkillMdPath)
    $result = [pscustomobject]@{ Ok=$false; Name=$null; Description=$null; Reason=$null; RawLength=0 }
    try {
        $bytes = (Get-Item -LiteralPath $SkillMdPath -ErrorAction Stop).Length
        $result.RawLength = $bytes
        if ($bytes -eq 0) { $result.Reason = 'empty'; return $result }
        $lines = Get-Content -LiteralPath $SkillMdPath -ErrorAction Stop
        if ($lines.Count -lt 2 -or $lines[0].Trim() -ne '---') { $result.Reason = 'no-open-delim'; return $result }
        $end = -1
        for ($i = 1; $i -lt $lines.Count; $i++) {
            if ($lines[$i].Trim() -eq '---') { $end = $i; break }
        }
        if ($end -lt 0) { $result.Reason = 'no-close-delim'; return $result }
        $kv = @{}
        $currentKey = $null
        for ($i = 1; $i -lt $end; $i++) {
            $ln = $lines[$i]
            if ($ln -match '^([A-Za-z0-9_\-]+)\s*:\s*(.*)$') {
                $currentKey = $matches[1].ToLower()
                $kv[$currentKey] = $matches[2].Trim().Trim('"').Trim("'")
            } elseif ($currentKey -and $ln -match '^\s+\S') {
                $kv[$currentKey] += ' ' + $ln.Trim()
            }
        }
        $result.Name = $kv['name']
        $result.Description = $kv['description']
        $result.Ok = [bool]($result.Name -and $result.Description)
        if (-not $result.Ok) { $result.Reason = 'missing-name-or-description' }
    } catch {
        $result.Reason = "read-error: $($_.Exception.Message)"
    }
    return $result
}
```

### Hash and drift grouping

```powershell
function Get-SkillHash {
    param([string]$SkillMdPath)
    try { (Get-FileHash -LiteralPath $SkillMdPath -Algorithm SHA256 -ErrorAction Stop).Hash }
    catch { $null }
}
# Group $allSkills by .Name; within each group, distinct hashes > 1 ⇒ C2 drift.
```

### Frontmatter sanity (C3)

```powershell
$nameRegex = '^[a-z0-9-]+$'
function Test-Frontmatter {
    param($fm)   # output of Read-Frontmatter
    $issues = New-Object System.Collections.Generic.List[string]
    if (-not $fm.Ok) { $issues.Add("ERROR: $($fm.Reason)"); return $issues }
    if ($fm.Name -notmatch $nameRegex) { $issues.Add("WARNING: name '$($fm.Name)' violates [a-z0-9-]+") }
    if (($fm.Description | Out-String).Trim().Length -lt 30) { $issues.Add('WARNING: description shorter than 30 chars') }
    return $issues
}
```

### Secret redaction for quoted snippets

```powershell
function Redact-Secrets {
    param([string]$Text)
    if (-not $Text) { return $Text }
    $patterns = @(
        'ghp_[A-Za-z0-9]{20,}',
        'sk-[A-Za-z0-9_\-]{20,}',
        'xox[bp]-[A-Za-z0-9\-]{10,}',
        'AKIA[0-9A-Z]{16}',
        '(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*[''"]?[A-Za-z0-9+/=_\-]{16,}[''"]?'
    )
    foreach ($p in $patterns) { $Text = [regex]::Replace($Text, $p, '<redacted>') }
    return $Text
}
```

### Per-skill record assembly

```powershell
$records = New-Object System.Collections.Generic.List[object]
foreach ($loc in $Locations) {
    if (-not (Test-Path -LiteralPath $loc.Path)) {
        $records.Add([pscustomobject]@{ LocationId=$loc.Id; LocationRole=$loc.Role; LocationPath=$loc.Path; Skipped=$true })
        continue
    }
    foreach ($folder in (Get-SkillFolders -Root $loc.Path -Depth $loc.Depth)) {
        $skillMd = Join-Path $folder.FullName 'SKILL.md'
        $hasSkillMd = Test-Path -LiteralPath $skillMd
        $link = Get-LinkInfo -Path $folder.FullName
        $fm = if ($hasSkillMd) {
            Read-Frontmatter -SkillMdPath $skillMd
        } else {
            [pscustomobject]@{ Ok=$false; Name=$null; Description=$null; Reason='SKILL.md missing or unreachable' }
        }
        $hash = if ($hasSkillMd) { Get-SkillHash -SkillMdPath $skillMd } else { $null }
        $records.Add([pscustomobject]@{
            LocationId       = $loc.Id
            LocationRole     = $loc.Role
            LocationPath     = $loc.Path
            Name             = $folder.Name
            FolderName       = $folder.Name
            FolderPath       = $folder.FullName
            SkillMd          = $skillMd
            HasSkillMd       = $hasSkillMd
            IsLink           = $link.IsLink
            LinkType         = $link.LinkType
            LinkTarget       = $link.Target
            LinkTargetExists = $link.TargetExists
            Frontmatter      = $fm
            Hash             = $hash
        })
    }
}
```

## Examples

### Example 1 — Clean ecosystem

User: "audit my skills"

Expected output (abridged):

```markdown
# Skill Audit Report

## Summary
| Location | Path | Skills | ERROR | WARNING | INFO |
| Central (C)         | C:\Users\WZY\.skills                    | 42 | 0 | 0 | 0 |
| OpenCode Global (OG)| C:\Users\WZY\.config\opencode\skills    | 12 | 0 | 0 | 0 |
| Claude Global (CG)  | C:\Users\WZY\.claude\skills             | 10 | 0 | 0 | 0 |
| Project OpenCode (OP) | (skipped: no repo root)               |  0 | 0 | 0 | 1 |
| Project Claude (CP)   | (skipped: no repo root)               |  0 | 0 | 0 | 1 |

**Totals:** ERROR=0, WARNING=0, INFO=2

## Findings
_All locations clean. Central matches every mirrored copy by SHA256._
```

### Example 2 — Drift between central and OpenCode global

```markdown
### OpenCode Global (OG)
- **[ERROR][C2] git-master** — SKILL.md hash differs from Central
  - Central:  C:\Users\WZY\.skills\process\git-master\SKILL.md
              SHA256 4f3a…b21c
  - OG copy:  C:\Users\WZY\.config\opencode\skills\git-master\SKILL.md
              SHA256 9d77…02ee
  - Fix (keep central): invoke `link-skills` to re-link `git-master` to OpenCode-Global with Overwrite.
  - Fix (keep edits):   invoke `install-skill` on `C:\Users\WZY\.config\opencode\skills\git-master` with category `process`, then invoke `link-skills` to re-mirror.
```

### Example 3 — Broken junction

```markdown
### Claude Global (CG)
- **[ERROR][C4] webapp-testing** — junction target missing
  - Path:   C:\Users\WZY\.claude\skills\webapp-testing
  - Target: C:\Users\WZY\.skills\testing\webapp-testing  (does not exist)
  - Fix: invoke `link-skills` to re-link `webapp-testing` to Claude-Global (this recreates the junction).
```

### Example 4 — Orphan in Claude global

```markdown
### Claude Global (CG)
- **[WARNING][C5] foo-helper** — present in CG but not in Central
  - Path: C:\Users\WZY\.claude\skills\foo-helper
  - Fix (import): invoke `install-skill` on `C:\Users\WZY\.claude\skills\foo-helper` with category `process`.
  - Fix (drop):   confirm with user, then they remove manually. This skill never deletes.
```

### Example 5 — Malformed frontmatter

```markdown
### Central (C)
- **[ERROR][C3] my-skill** — frontmatter missing closing `---`
  - Path: C:\Users\WZY\.skills\process\my-skill\SKILL.md
  - Reason: no-close-delim
  - Fix: open the file and add a closing `---` line; re-run audit.

- **[WARNING][C3] BadName_Skill** — name violates [a-z0-9-]+ and description is 12 chars
  - Path: C:\Users\WZY\.skills\process\BadName_Skill\SKILL.md
  - Fix: rename folder + frontmatter `name:` to lowercase-hyphen form; expand description.
```

## Limitations

- **Read-only.** This skill never modifies, deletes, or links anything. It only
  reports. Even when a fix is "obvious", hand off to `install-skill` or
  `link-skills` and require user confirmation.
- **No `rm`.** Removal is out of scope. If the user wants to remove an orphan,
  they do it manually after confirming.
- **No external parsers.** YAML is parsed line-by-line with regex; only the
  frontmatter block is inspected. Complex YAML (multi-line block scalars beyond
  simple indented continuations, anchors, flow style) is best-effort. Flag with
  `C3 WARNING: complex-yaml` if a value cannot be cleanly extracted.
- **Hash fast-path.** `C2` compares SHA256 of `SKILL.md` only. If the user asks
  for "deep diff", extend the comparison to every file under the skill folder
  (still read-only). Do not run deep diff by default.
- **Junctions only on NTFS.** `LinkType` works on NTFS volumes; on other
  filesystems treat all directories as non-links and skip `C4`.
- **PowerShell 5.1.** No PS7-only cmdlets. No external modules.
- **Windows Dev Mode may be off.** That's fine for auditing; only `link-skills`
  cares about creating links.
- **Secret redaction is best-effort.** If a SKILL.md happens to include a
  credential, the report substitutes `<redacted>`, but the user should still
  rotate the credential and clean the file. Flag as `WARNING` alongside the
  original finding.
- **No network.** This skill does not reach out to remote registries; it only
  inspects the local filesystem.
