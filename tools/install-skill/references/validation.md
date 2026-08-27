# Candidate and Result Validation

Read this reference while discovering candidates, checking their metadata, or
rendering the final report. It defines validation order and failure semantics.

## Candidate records

For each discovered candidate, read `name:` and `description:` from its direct
`SKILL.md`. Record the staged candidate root, candidate-relative path, safe
package name, provisional root, provisional destination, and for GitHub the
verified repository-relative candidate path. A candidate must have its
`SKILL.md` directly in its package root.

Show the candidate relative path, inferred root and destination, sanitized name,
and the first approximately 80 characters of its description. Page lists longer
than about 15 candidates while preserving existing selections. Zero picker
selections are cancellation and a no-op. Reject duplicate final
`<root>/<package-name>` destinations before copying.

## Checks after copying

Run these destination-only checks in order for every non-skipped selected row:

1. The destination exists and directly contains `SKILL.md`.
2. Destination frontmatter has non-empty `name:` and `description:`. A
   confirmed upstream mismatch is reported; an aligned copy must match the
   final directory name.
3. No directory named `.git` exists anywhere under the destination.
4. The destination and root kind/name match the confirmed plan.
5. Only then mutate, atomically write, parse, and verify the full aggregate and
   the selected key outcome.

The success order is:

```text
payload copy -> payload verification -> aggregate mutation -> aggregate verification -> OK
```

`OK` is forbidden until both payload and aggregate verification pass.

## Reporting and failures

Stop on the first failure except a user-selected conflict `Skip`. Keep earlier
successful rows and always report every row, including partial results:

```text
Package  Root kind/name  Destination  Aggregate path  Frontmatter action  Aggregate action  Status
```

Use `OK`, `Skipped (<reason>)`, or `Failed (<reason>)`, include totals, and
remind the user:

```text
Next step: run the link-skills skill to enable the OK rows for OpenCode, Claude, or Codex.
```

If aggregate serialization, replacement, parsing, or verification fails after
payload verification, retain the payload and report exactly:

```text
Payload installed; aggregate update failed (<reason>)
```

Never hide clone, robocopy, malformed aggregate, picker, duplicate destination,
or cleanup errors. Report paths and robocopy codes for copy failures. Treat
unknown roots and malformed existing aggregates as preflight failures, not as
reasons to fabricate a fallback.
