---
name: install-skill
description: Install one or more selected skills from a GitHub URL, GitHub repo path, or local folder into ~/.skills/<root>/<package-name>. Use this when the user asks to install, add, fetch, import, or pull skills into the central repository. Discover candidates, confirm semantic or bundle placement, mirror with robocopy, verify payloads, and maintain sparse URL-only root aggregates. Stop before linking.
---

# install-skill

## Purpose and boundary

Install selected packages into the canonical repository:

```text
$env:USERPROFILE\.skills\<root>\<package-name>\
```

Every installed package directly contains `SKILL.md`. A root aggregate is
metadata beside its package directories, not package payload. This skill stages
input, discovers candidates, confirms choices, copies payloads, verifies them,
updates the root aggregate, and cleans staging. It never creates junctions or
edits client configuration. Use `link-skills` to enable packages and
`audit-skills` to inspect them.

## Progressive route

Read the named reference when its branch is reached. Do not load every
reference by default.

- Read `references/source-staging.md` when parsing `Source`, resolving a GitHub
  branch or discovery path, creating staging, cloning, mirroring, or cleaning up.
- Read `references/validation.md` when discovering candidates, checking
  frontmatter or payloads, handling no candidates, or producing the report.
- Read `references/candidate-placement.md` when selecting candidates, inferring
  roots, confirming bundle or collection placement, or rendering a plan.
- Read `references/conflicts-and-frontmatter.md` when a name mismatch, missing
  name, destination conflict, rename, overwrite, or skip is encountered.
- Read `references/payload-and-aggregate.md` before removing nested `.git`,
  copying a selected payload, or reading or mutating an aggregate.
- Read `references/powershell-5.1.md` before executing any helper. These helpers
  are for Windows PowerShell 5.1 and do not replace user decision gates.

## Inputs and roots

Ask only for missing values. Confirm ambiguous root placement before copying.

| Input | Required | Rule |
|---|---|---|
| `Source` | yes | Full GitHub URL, `<owner>/<repo>[/<subpath>]`, or absolute local folder. |
| `Root` | no | Semantic root or explicitly confirmed bundle or collection root. |
| `SkillName` | no | Destination override for exactly one selected candidate. |
| `Branch` | no | Optional Git branch; otherwise use the repository default branch. |
| `Subpath` | no | Discovery path derived from the source when supplied. |

Known semantic roots are `ai`, `backend`, `browser`, `design`, `document`,
`frontend`, `myCreatsSkills`, `research`, `testing`, `tools`, and `writing`.
Known bundle or collection roots are `agent-browser`, `grill`, `openspec`,
`superpowers-plus`, and `ui-ux-pro-max-skill`. Preserve the casing of
`myCreatsSkills`. A root name is not a package name.

Recognize, but never auto-select, these upstream root mappings:

| Root | Upstream |
|---|---|
| `agent-browser` | `vercel-labs/agent-browser` |
| `grill` | `mattpocock/skills` |
| `openspec` | `Fission-AI/OpenSpec` |
| `superpowers-plus` | `xhyqaq/superpowers-plus` |
| `ui-ux-pro-max-skill` | `nextlevelbuilder/ui-ux-pro-max-skill` |

## Universal workflow

Do not mutate a payload or aggregate before the final confirmation.

1. Parse and validate `Source`; resolve the effective branch and discovery root.
2. Create a fresh GUID staging directory and stage the source. GitHub uses the
   GitHub CLI first, then one shallow Git fallback. Local input uses robocopy.
3. Discover every case-sensitive `SKILL.md` to depth `4`. Each parent directory
   is a candidate. Abort with a no-op if none exist.
4. Record each candidate path, frontmatter, safe package name, provisional root,
   destination, and verified repository-relative path when the source is GitHub.
5. Select explicitly. A named single candidate may be installed after the
   normal confirmation; otherwise use `Install / Cancel` for one candidate and
   a native multi-select picker for several. Never install all by default.
6. Confirm root kind and name, evidence, destination, aggregate path, and every
   exceptional bundle or collection placement. Infer semantic roots only from
   strong evidence; a shared owner, repository, URL, or directory is not bundle
   evidence.
7. Build a provisional plan without writing. Resolve conflicts and then name
   mismatches. A rename must repeat mismatch handling.
8. Render the complete plan and ask `Proceed / Change selection / Cancel`.
9. After `Proceed`, remove nested `.git` directories, mirror each selected
   payload, optionally align only copied destination frontmatter, and verify it.
10. Only after payload verification, set or remove the selected aggregate key,
    atomically write it, re-read it, and verify the complete aggregate.
11. For selections sharing a root, re-read and verify the aggregate after each
    row. Never reuse a preflight snapshot.
12. Mark a row `OK` only after both payload and aggregate verification pass.
13. In `finally`, remove staging, verify that it is gone, and report cleanup
    failures together with every partial result.

## Confirmation and outputs

Every selected row must have a confirmed source path, final package name, root
kind and name, destination, aggregate path, frontmatter action, aggregate
action, and conflict choice. Planning is read-only. The final confirmation is
the last gate before nested `.git` removal, payload mirroring, frontmatter
alignment, or aggregate mutation.

Aggregate action is `Set <concrete tree URL>`, `Remove selected key`, or `No
change (conflict skipped)`. A local source and an incomplete or unverifiable
GitHub candidate use removal or omission, never a placeholder. A repository-root
candidate with no package subpath cannot receive a locator.

No candidates, zero picker selections, or a user cancellation are no-op
outcomes. A conflict skip is not a failure and cannot change an aggregate.
Unknown roots, malformed aggregates, duplicate destinations, unsupported source
forms, and failed staging are rejected before copying.

The final report includes all rows and totals, including rows completed before a
later failure. It distinguishes `OK`, `Skipped (<reason>)`, and
`Failed (<reason>)`. A payload that passed its checks but cannot update or verify
the aggregate is retained and is never reported as `OK`.
The report must state the reason whenever a row is skipped or failed.

## Invariants

- `SkillName` is allowed only for one selected candidate and final package names
  use `[a-z0-9-]+`. Reject duplicate final `<root>/<package-name>` destinations.
- Bundle, collection, unknown-root, and new-root placement always require an
  explicit user choice and confirmation. Do not guess or silently broaden scope.
- An existing destination is never silently overwritten. A skipped conflict
  leaves both payload and aggregate untouched.
- Aggregate values are concrete verified GitHub tree URLs only. Never invent a
  path from a package name, frontmatter, folder name, or collection scan.
- Existing malformed aggregate state is rejected before mutation. Preserve
  unrelated valid keys and never add schema, history, hashes, versions, or
  package-local source metadata.
- Robocopy codes `0` through `7` succeed; `8` and above fail without blind retry.
- Stop on the first failure except a user-selected conflict skip. Keep earlier
  successes and report `Payload installed; aggregate update failed (<reason>)`
  when aggregate work fails after payload verification.

For the exact decision rules, helper implementations, aggregate contract, and
report format, follow the conditional references above rather than inventing a
shorter alternative. The workflow ends after selected payloads and sparse
root-level URL-only aggregates are verified; linking and auditing are separate.
