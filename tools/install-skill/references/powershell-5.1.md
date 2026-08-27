# Windows PowerShell 5.1 Helpers

Use Windows PowerShell 5.1 syntax and the exact helpers below. These helpers do
not replace candidate selection, root placement, conflict handling, mismatch
choices, or final confirmation. Keep all source, payload, aggregate, and
temporary-artifact work in the surrounding `try { ... } finally { ... }`.

## Parse and stage sources

```powershell
function Resolve-SkillSource {
    param([Parameter(Mandatory)] [string] $Source)
    $value=$Source.Trim()
    if ($value -match '^https://github\.com/([^/]+)/([^/]+?)(?:\.git)?(?:/tree/([^/]+)(?:/(.+))?)?/?$') {
        return [pscustomobject]@{Kind="github";Owner=$Matches[1];Repo=$Matches[2];Branch=$Matches[3];Subpath=$Matches[4]}
    }
    if ($value -match '^([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)(?:/(.+))?$') {
        return [pscustomobject]@{Kind="github";Owner=$Matches[1];Repo=$Matches[2];Branch=$null;Subpath=$Matches[3]}
    }
    if ($value -match '^https?://') { throw "Only GitHub HTTP URLs are supported." }
    if ([IO.Path]::IsPathRooted($value) -and (Test-Path -LiteralPath $value -PathType Container)) {
        return [pscustomobject]@{Kind="local";Path=(Resolve-Path -LiteralPath $value).Path}
    }
    throw "Unrecognized source: $value"
}

function Get-GitHubDefaultBranch {
    param([string] $Owner,[string] $Repo)
    $gh=Get-Command gh.exe -ErrorAction SilentlyContinue
    if (-not $gh) { return $null }
    try { $json=& $gh.Path api "repos/$Owner/$Repo" } catch { return $null }
    if ($LASTEXITCODE -ne 0) { return $null }
    try { $branch=($json | ConvertFrom-Json -ErrorAction Stop).default_branch } catch { return $null }
    if ([string]::IsNullOrWhiteSpace([string]$branch)) { return $null }
    return [string]$branch
}

function Invoke-CloneToStaging {
    param([string] $Owner,[string] $Repo,[string] $Branch,[string] $Staging)
    $ghArgs=@("repo","clone","$Owner/$Repo",$Staging,"--","--depth","1")
    if ($Branch) { $ghArgs+=@("--branch",$Branch) }
    $gh=Get-Command gh.exe -ErrorAction SilentlyContinue
    $ghOutput=@()
    if ($gh) {
        $ghOutput=@(& $gh.Path @ghArgs 2>&1)
        if ($LASTEXITCODE -eq 0) { return }
    }
    $git=Get-Command git.exe -ErrorAction SilentlyContinue
    if (-not $git) { throw "Install Git for Windows or GitHub CLI to fetch from GitHub." }
    $gitArgs=@("clone","--depth","1")
    if ($Branch) { $gitArgs+=@("--branch",$Branch) }
    $gitArgs+=@("https://github.com/$Owner/$Repo.git",$Staging)
    $gitOutput=@(& $git.Path @gitArgs 2>&1)
    if ($LASTEXITCODE -ne 0) { throw "Clone failed`n$(@($ghOutput+$gitOutput)-join [Environment]::NewLine)" }
}

function Get-ClonedBranch {
    param([string] $RepositoryRoot)
    $branch=& git.exe -C "$RepositoryRoot" branch --show-current
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace([string]$branch)) { return $null }
    return ([string]$branch).Trim()
}

function Copy-LocalToStaging {
    param([string] $Source,[string] $Staging)
    & robocopy "$Source" "$Staging" /MIR /NFL /NDL /NJH /NJS | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy staging failed (code $LASTEXITCODE)" }
}
```

## Discover, copy, and verify payloads

```powershell
function Find-SkillMd {
    param([string] $Root)
    return ,(Get-ChildItem -LiteralPath $Root -Recurse -Depth 4 -Filter SKILL.md -File |
        Where-Object {$_.Name -ceq "SKILL.md"})
}

function Get-RepositoryRelativeCandidatePath {
    param([string] $RepositoryRoot,[string] $CandidateRoot)
    $base=[IO.Path]::GetFullPath($RepositoryRoot).TrimEnd('\')+'\'
    $candidate=[IO.Path]::GetFullPath($CandidateRoot).TrimEnd('\')
    if (-not $candidate.StartsWith($base,[StringComparison]::OrdinalIgnoreCase)) { return $null }
    return $candidate.Substring($base.Length).Replace('\','/').Trim('/')
}

function Copy-IntoCentralRepo {
    param([string] $SkillRoot,[string] $Destination)
    New-Item -ItemType Directory -Force -Path "$Destination" | Out-Null
    & robocopy "$SkillRoot" "$Destination" /MIR /NFL /NDL /NJH /NJS | Out-Null
    if ($LASTEXITCODE -ge 8) { throw "robocopy install failed (code $LASTEXITCODE)" }
}

function Remove-NestedGitDirectories {
    param([string] $SkillRoot)
    foreach ($directory in @(Get-ChildItem -LiteralPath $SkillRoot -Recurse -Force -Directory |
        Where-Object {$_.Name -ceq ".git"})) {
        Remove-Item -Recurse -Force -LiteralPath $directory.FullName
    }
}

function Assert-InstalledPayload {
    param([string] $Destination)
    $skillMd=Join-Path $Destination "SKILL.md"
    if (-not (Test-Path -LiteralPath $skillMd -PathType Leaf)) { throw "destination lacks direct SKILL.md" }
    if (@(Get-ChildItem -LiteralPath $Destination -Recurse -Force -Directory |
        Where-Object {$_.Name -ceq ".git"}).Count -gt 0) { throw "destination contains nested .git" }
}
```

## Validate, mutate, and atomically write aggregates

```powershell
function Assert-ExactProperties {
    param($Object,[string[]] $Expected,[string] $Label)
    if ($null -eq $Object -or -not ($Object -is [PSCustomObject])) { throw "$Label must be a PSCustomObject" }
    $actual=@($Object.PSObject.Properties | ForEach-Object {$_.Name})
    if (@($Expected | Where-Object {$actual -cnotcontains $_}).Count -gt 0 -or
        @($actual | Where-Object {$Expected -cnotcontains $_}).Count -gt 0) {
        throw "$Label must contain exactly: $($Expected -join ', ')"
    }
}

function Assert-ConcreteGitHubTreeUrl {
    param($Value,[string] $PackageName)
    if (-not ($Value -is [string]) -or [string]::IsNullOrWhiteSpace($Value)) { throw "locator '$PackageName' must be a non-empty string" }
    if ($Value -notmatch '^https://github\.com/[^/]+/[^/]+/tree/[^/]+/.+[^/]$') { throw "locator '$PackageName' must be a concrete GitHub tree URL" }
}

function Assert-SkillSourcesAggregate {
    param($Aggregate,[string] $RootPath)
    Assert-ExactProperties $Aggregate @("skills") "aggregate"
    if (-not ($Aggregate.skills -is [PSCustomObject])) { throw "aggregate skills must be a PSCustomObject" }
    if (-not (Test-Path -LiteralPath $RootPath -PathType Container)) { throw "aggregate root does not exist: $RootPath" }
    foreach ($property in @($Aggregate.skills.PSObject.Properties)) {
        $key=[string]$property.Name
        if ([string]::IsNullOrWhiteSpace($key) -or $key.IndexOfAny([char[]]('/\')) -ge 0 -or
            $key -eq '.' -or $key -eq '..' -or [IO.Path]::IsPathRooted($key) -or $key.Contains(':')) {
            throw "aggregate key '$key' must be a direct package directory name"
        }
        $directory=@(Get-ChildItem -LiteralPath $RootPath -Directory -Force |
            Where-Object {$_.Name -ceq $key})
        if ($directory.Count -ne 1 -or
            -not (Test-Path -LiteralPath (Join-Path $directory[0].FullName "SKILL.md") -PathType Leaf)) {
            throw "aggregate key '$key' must name a direct child directory containing SKILL.md"
        }
        Assert-ConcreteGitHubTreeUrl $property.Value $property.Name
    }
}

function Read-SkillSourcesState {
    param([string] $RootPath,[bool] $RootWasEmpty)
    $path=Join-Path $RootPath ".skill-sources.json"
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        if ($RootWasEmpty) { return [pscustomobject]@{Exists=$false;Raw=$null;Aggregate=$null} }
        throw "aggregate is missing for existing non-empty root: $path"
    }
    $raw=[IO.File]::ReadAllText($path)
    if ([string]::IsNullOrWhiteSpace($raw)) { throw "aggregate is empty: $path" }
    $aggregate=$raw | ConvertFrom-Json -ErrorAction Stop
    Assert-SkillSourcesAggregate $aggregate $RootPath
    return [pscustomobject]@{Exists=$true;Raw=$raw;Aggregate=$aggregate}
}

function New-EmptySkillSourcesAggregate {
    return [pscustomobject][ordered]@{skills=[pscustomobject][ordered]@{}}
}

function New-GitHubTreeLocator {
    param([string] $Owner,[string] $Repo,[string] $Branch,[string] $CandidateSubpath)
    $path=$CandidateSubpath.Replace('\','/').Trim('/')
    if ([string]::IsNullOrWhiteSpace($Owner) -or [string]::IsNullOrWhiteSpace($Repo) -or
        [string]::IsNullOrWhiteSpace($Branch) -or [string]::IsNullOrWhiteSpace($path)) { return $null }
    $locator="https://github.com/$Owner/$Repo/tree/$Branch/$path"
    Assert-ConcreteGitHubTreeUrl $locator $path
    return $locator
}

function Set-SkillSourceLocator {
    param($Aggregate,[string] $PackageName,[string] $Locator)
    Assert-ConcreteGitHubTreeUrl $Locator $PackageName
    $property=$Aggregate.skills.PSObject.Properties[$PackageName]
    if ($null -eq $property) { Add-Member -InputObject $Aggregate.skills -MemberType NoteProperty -Name $PackageName -Value $Locator }
    else { $property.Value=$Locator }
}

function Remove-SkillSourceLocator {
    param($Aggregate,[string] $PackageName)
    $Aggregate.skills.PSObject.Properties.Remove($PackageName)
}

function Write-SkillSourcesAggregate {
    param([string] $RootPath,$Aggregate,$PriorState)
    Assert-SkillSourcesAggregate $Aggregate $RootPath
    $path=Join-Path $RootPath ".skill-sources.json"
    $existsNow=Test-Path -LiteralPath $path -PathType Leaf
    if ($existsNow -ne [bool]$PriorState.Exists) { throw "aggregate changed since it was read: $path" }
    if ($existsNow -and [IO.File]::ReadAllText($path) -cne [string]$PriorState.Raw) { throw "aggregate changed since it was read: $path" }
    $temp=Join-Path $RootPath (".skill-sources."+[Guid]::NewGuid().ToString("N")+".tmp")
    $backup=Join-Path $RootPath (".skill-sources."+[Guid]::NewGuid().ToString("N")+".bak")
    try {
        $json=$Aggregate | ConvertTo-Json -Depth 4
        $utf8=New-Object -TypeName System.Text.UTF8Encoding -ArgumentList $false
        [IO.File]::WriteAllText($temp,$json,$utf8)
        [void](([IO.File]::ReadAllText($temp) | ConvertFrom-Json -ErrorAction Stop))
        if ($existsNow) { [IO.File]::Replace($temp,$path,$backup) } else { [IO.File]::Move($temp,$path) }
    } finally {
        if (Test-Path -LiteralPath $temp) { Remove-Item -Force -LiteralPath $temp }
        if (Test-Path -LiteralPath $backup) { Remove-Item -Force -LiteralPath $backup }
    }
}

function Verify-SkillSourcesAggregate {
    param([string] $RootPath,[string] $PackageName,$ExpectedLocator)
    $path=Join-Path $RootPath ".skill-sources.json"
    $raw=[IO.File]::ReadAllText($path)
    $aggregate=$raw | ConvertFrom-Json -ErrorAction Stop
    Assert-SkillSourcesAggregate $aggregate $RootPath
    $property=$aggregate.skills.PSObject.Properties[$PackageName]
    if ($null -eq $ExpectedLocator) {
        if ($null -ne $property) { throw "aggregate key '$PackageName' should be absent" }
    } elseif ($null -eq $property -or [string]$property.Value -cne [string]$ExpectedLocator) {
        throw "aggregate locator '$PackageName' differs from expected URL"
    }
    return [pscustomobject]@{Exists=$true;Raw=$raw;Aggregate=$aggregate}
}
```

After a verified payload, use the current same-root state. Create
`New-EmptySkillSourcesAggregate` only when a verified first payload is entering
an otherwise empty root. Set a locator only for a complete verified GitHub
candidate; otherwise remove or omit the selected key. Write using the state just
read, verify, and retain the returned state for the next selection in that root.
