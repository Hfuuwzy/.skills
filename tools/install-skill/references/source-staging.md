# Source and Staging

Read this reference for every run before source resolution. It owns accepted
source forms, discovery-root resolution, staging lifetime, clone fallback, and
cleanup. Use the exact helper implementations in `powershell-5.1.md`.

## Resolve the source

Accept a full `https://github.com/...` URL, `<owner>/<repo>` shorthand,
`<owner>/<repo>/<subpath>` shorthand, or an absolute local directory. A full
GitHub URL may contain `tree/<branch>/<subpath>`. Derive the discovery subpath
from the URL or shorthand, and use an explicitly supplied `Branch` when given.
Only GitHub HTTP URLs are supported. Reject files, archives, missing paths, and
non-GitHub HTTP URLs instead of inventing another fetch mode.

Source parsing and aggregate locator construction are separate. A repository or
collection URL is useful for discovery, but is not itself an aggregate locator.
The eventual locator must identify the selected candidate's exact path.

## Stage safely

Set `$ErrorActionPreference = "Stop"`, create a fresh staging directory under
`$env:TEMP\.skills-staging\<GUID>`, and keep all work inside:

```powershell
try {
    # resolve, stage, select, confirm, copy, verify, and report
}
finally {
    # remove staging, verify it is gone, and report cleanup failure
}
```

Do not mutate a package payload or aggregate before the final plan confirmation.

For GitHub input, resolve the default branch with `gh api` when no branch was
provided. If that lookup fails, leave the branch unset and clone the repository
default without `--branch`; this must not block the fallback. Try `gh repo clone`
first. If that attempt fails, make exactly one shallow `git clone` fallback. If
both tools are unavailable, explain that GitHub CLI or Git for Windows is
required. Capture clone errors and stop after the one fallback attempt.

For local input, resolve the absolute directory and mirror it to staging with
robocopy `/MIR`. Treat exit codes `0` through `7` as success and `8` or above as
failure. Report the code and paths for a failure; do not retry blindly.

## Resolve and discover

After staging, verify the effective discovery root exists beneath the staged
source. For GitHub, retain the cloned repository root separately from the
discovery subpath. For every candidate, compute its normalized path relative to
the cloned repository root. Do not derive that path from a package name,
frontmatter, scan label, or guessed collection layout.

Discovery is exact and bounded: find every file named `SKILL.md` with a
case-sensitive comparison, no deeper than depth `4`. Each file's parent is a
candidate. A source with no candidates is cancellation and a no-op.

Always remove the staging directory in `finally`, verify it no longer exists,
and include cleanup failure in the final report. This applies to cancellation,
clone failure, picker cancellation, partial installation, and success.
