# Conflicts and Frontmatter

Read this reference whenever naming or destination state is ambiguous. Resolve
all choices before the final plan confirmation and before any mutation.

## Package names and mismatch

For one selected candidate only, `SkillName` may override the destination name.
Otherwise use non-empty frontmatter `name:`, then the source folder name, and
sanitize the final directory name to `[a-z0-9-]+`. If `name:` is missing, warn,
use and sanitize the source folder name, and skip the candidate if the result is
empty.

After every override and conflict `Rename`, compare final directory name with a
non-empty frontmatter `name:`. For each mismatch, ask the user to choose:

1. Keep upstream frontmatter unchanged. Copy staging as-is, key the aggregate
   by the final directory name, and report the confirmed mismatch.
2. Align only the copied destination `SKILL.md`. Copy first, then change only
   destination frontmatter before payload verification. Never edit staging.
3. Cancel or change placement. Return to selection, root, or name choice, drop
   the candidate, or cancel.

The frontmatter action must be visible in the final plan. An aligned copy must
have `name:` matching its final directory name and must still have a non-empty
`description:`.

## Existing destinations

When a final destination exists and is not empty, present exactly these choices:

1. **Overwrite.** Explain that robocopy `/MIR` deletes destination extras, then
   mirror the confirmed staged payload.
2. **Rename.** Suggest `<package-name>-2`, then the first free suffix. Re-run
   mismatch handling for the new final name.
3. **Skip.** Leave payload and aggregate untouched, mark the row skipped, and
   continue with other selected rows.

Never silently overwrite, hand-merge, or mutate an aggregate for a skipped row.
Do not apply conflict decisions until the final selected names and roots have
been confirmed. Reject duplicate final destinations before copying.
