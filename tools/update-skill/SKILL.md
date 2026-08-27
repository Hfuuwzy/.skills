---
name: update-skill
description: Update, refresh, or pull the latest version of existing central skills from their stored concrete GitHub tree URLs. Use this model-invoked router only for overwrite updates of packages already under ~/.skills; do not use it to add, rebind, link, or audit skills.
---

# update-skill
## Purpose and boundary
Update existing canonical packages in:

```text
$env:USERPROFILE\.skills\<root>\<package>\
```

This overwrite updater operates only on a direct package directory that already
contains `SKILL.md` and has a stored concrete GitHub tree URL in that root's
`.skill-sources.json`. The stored locator is the only source of truth. Never
discover a source, accept a user URL or local path, rebind a locator, compare
versions or hashes, or mutate a source map.

Use `install-skill` to add or rebind a source; `link-skills` to publish a central
package to a client; and `audit-skills` for read-only inspection.

## Read these references at the named phases
Reuse the installer's helpers; do not copy them into this skill:

- Read `../install-skill/references/source-staging.md` before parsing or staging
  a stored locator, cloning, or cleanup.
- Read `../install-skill/references/powershell-5.1.md` before running any helper.
  Use Windows PowerShell 5.1 syntax, `-LiteralPath`, and its exact clone,
  relative-path, copy, and destination-validation helpers.
- Read `../install-skill/references/payload-and-aggregate.md` for read-only
  aggregate validation and payload mirroring. Do not perform its aggregate
  writes or create an aggregate entry.
- Read `../install-skill/references/validation.md` for destination-only checks
  and result semantics.

## Fresh root and package scan

Set `$ErrorActionPreference = "Stop"`. Derive the central path from
`$env:USERPROFILE`; never hard-code a user path. At runtime, scan the immediate
children of `~/.skills`. A selectable root is one with either:

1. one or more direct package directories (directories directly containing
   `SKILL.md`), or
2. a valid root-level `.skill-sources.json` aggregate.

Do not use a hard-coded root list or treat `browser` as selectable merely
because it is documented. For each candidate root, read the aggregate with the
installer's read-only validation. A non-empty root without an aggregate, a
missing or malformed map, or a map key that does not name a direct package is a
read-only failure; stop before staging or destination mutation. An empty root
with no map is not updateable and need not be offered. The updater itself is a
new source-less package and must not receive a fake map entry.

## Per-root package tabs

After the fresh scan and read-only validation, use exactly one native multi-select
root picker with `multiple:true`. Offer every valid selectable root in that
picker. Zero selected roots is a no-op.

After roots are selected, freshly enumerate and sort the selected roots, then
enumerate and sort each root's direct updateable packages. An updateable package
has a valid concrete GitHub tree URL in the validated aggregate. Build the
package stage as one native batched call shaped like this:

```text
question({
  questions: [
    {
      header: "<root>",
      question: "Select updateable skills from <root>.",
      multiple: true,
      options: [...]
    },
    {
      header: "<root> 1/N",
      question: "Select updateable skills from <root> (page 1/N).",
      multiple: true,
      options: [...]
    }
  ]
})
```

Generate the same four fields for every root or root/page tab. The `options`
array contains only updateable packages. OpenCode has no disabled option, so
never put an unavailable package line in `options`; show each line in that
root tab's `question` text or in an adjacent per-root summary instead.

Each question entry is a switchable per-root or per-root/page tab. A root with
15 or fewer selectable packages gets one tab headed `<root>`. For more than 15,
calculate `N = ceil(count / 15)` and create `<root> 1/N`, `<root> 2/N`, through
`<root> N/N`; each tab contains at most 15 selectable package options. Every tab
uses `multiple:true`, and every selectable option is labeled `<root>/<package>`.
Keep choices checked when switching among all tabs. After the package-stage
submit, union and deduplicate all selected package identities before planning.
Prefer all tabs in one `question({ questions:[...] })` call, not sequential
one-root prompts. Only when a runtime hard tab limit prevents that call, split
the tabs into the fewest batched calls, carry selections explicitly between
calls, and union them without dropping or duplicating identities.

Within the tab set for each selected root, show every direct package with no stored locator as
`<root>/<package> — Skipped (unavailable: no stored locator)`. Keep these lines
visible but non-selectable in the root tab's `question` text or adjacent summary,
never in `options`, and do not count them toward the 15 selectable-option
capacity. On every restart or `Change selection`, discard picker metadata and
repeat a fresh disk scan, then recompute root ordering, package ordering, counts,
`N`, tab headers, and options; never reuse stale labels. Zero selected packages,
including a scan with no updateable packages, is a no-op. A missing locator is a
skip, not an update failure. Do not accept typed URLs, local sources, or alternate
sources, and do not make selections automatically.

## Read-only plan and source validation

For each selected package, retain its root, package name, existing destination,
and exact stored locator. The locator must be a non-empty concrete URL of this
form:

```text
https://github.com/<owner>/<repo>/tree/<branch>/<repo-relative-package-path>
```

Parse and stage that locator alone using `source-staging.md`. Try GitHub CLI
clone first, then exactly one shallow `git clone` fallback. Do not retry or
discover another source. Keep the fresh GUID staging directory in `try/finally`.

Resolve the locator's exact repository-relative path beneath the cloned
repository root. Require all of the following before touching a destination:

- the normalized candidate remains under the staging repository root;
- the candidate directory exists and directly contains case-sensitive `SKILL.md`;
- `Get-RepositoryRelativeCandidatePath` returns the exact locator path after
  separator normalization and trimming; and
- no missing, escaping, ambiguous, or mismatched path is tolerated.

Reject the row before execution when any check fails. Do not infer a path from
the package name, frontmatter, repository layout, or discovery scan. Do not
modify the staged source's frontmatter or the central map.

## Final multi-root confirmation and concurrency guard

Build a complete multi-root table before execution with exactly these columns:

| Root | Package | Destination | Stored locator | Staged source | Action |
|---|---|---|---|---|---|

Use `Mirror staged source into existing destination` as the action. Explain
that `/MIR` overwrites the existing package and deletes destination-only files
that are not in the staged upstream payload. Ask with the native question tool:
`Proceed / Change selection / Cancel`. If `Change selection` is chosen, discard
the plan and restart both fresh pickers from disk: rescan roots, then rebuild the
per-root/page tab package picker. If `Cancel` is chosen, do nothing.

Immediately before asking for the final choice, re-read every selected root
aggregate and every selected package directory. Compare each aggregate's
existence and exact raw contents, each stored locator, each package path,
direct `SKILL.md` presence, and package-root identity with the preflight state.
Abort safely without destination or aggregate mutation if any map, locator, or
package changed, disappeared, or became invalid. Clean staging through `finally`
and report the failure. This is a path/state guard, not a version or hash
comparison.

## Execute only after `Proceed`

Process rows in order and stop on the first execution failure, retaining all
completed rows. For each row:

1. Confirm the destination is the original existing package path. Remove every
   nested `.git` directory from the staged candidate using the referenced
   helper, never from the destination.
2. Mirror the staged candidate into the existing destination with `robocopy
   /MIR`. Codes `0..7` succeed; `8+` fails without a blind retry.
3. Run destination-only validation: destination exists, directly contains
   `SKILL.md`, contains no nested `.git`, and remains at the confirmed root and
   package name. Never align or rewrite frontmatter.
4. Report `OK` only after destination validation succeeds. Do not mutate,
   rewrite, or add anything to `.skill-sources.json`.

Never alter root placement, directory name, frontmatter alignment, links, junctions,
client configuration, or any other package. A junction loader sees central updates
live; a copied leaf needs `link-skills` refreshed afterward.

## Results and cleanup

Always report every planned row, grouped by root, plus multi-root totals. Use
exactly `OK`, `Skipped (<reason>)`, or `Failed (<reason>)`. A skipped or
untracked source is not a failure. Stop on the first failure, retain completed
rows, and include the robocopy or validation reason. Report staging cleanup from
`finally`, including whether staging was removed; cleanup failure is reported
separately and never hidden.

The final multi-root report must identify each selected root, state that maps
were unchanged, and warn that `/MIR` may delete destination extras. Do not create
history, provenance, schema versions, versions, revisions, hashes, package-local
metadata, or source-map entries.
