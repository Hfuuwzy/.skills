# Payload and Aggregate

Read this reference immediately before applying a confirmed plan. It owns
payload mutation, nested Git removal, the root-level aggregate contract, and
atomic verified writes.

## Payload order

For each non-skipped selected candidate, remove every nested directory named
`.git` from the selected candidate root before copying. Mirror the candidate to
the confirmed destination with robocopy `/MIR`; codes `0` through `7` succeed
and `8` or above fail. Do not blindly retry. If the mismatch choice was Align,
change only the copied destination `SKILL.md`, never staging. Then run the
destination checks in `validation.md`.

Only a verified payload may affect an aggregate. The order is:

```text
payload copy -> payload verification -> aggregate mutation -> aggregate verification -> OK
```

## URL-only aggregate

The aggregate is beside package directories at:

```text
$env:USERPROFILE\.skills\<root>\.skill-sources.json
```

It has exactly one top-level property, `skills`, whose value is a
`PSCustomObject`. It is a sparse map keyed by direct package directory name.
Every value is a non-empty concrete URL:

```text
https://github.com/<owner>/<repo>/tree/<branch>/<repository-relative-package-path>
```

Do not create package-local source metadata. Do not add `schemaVersion`,
provenance, history, hashes, revisions, versions, or updater fields.

A complete verified GitHub candidate gets a locator only when owner, repository,
effective branch, and exact candidate path relative to the cloned repository
root are all non-empty and verified. Normalize separators to `/`, trim leading
and trailing `/`, and build the concrete tree URL from those verified values.
Never guess a path from package name, frontmatter, directory name, or a scan.
A local candidate or incomplete or unverifiable GitHub candidate removes or
omits its selected final key; never write a placeholder. A repository-root
candidate without a non-empty package subpath is not representable.

## Read and reject state

Before final confirmation, parse any existing aggregate and reject empty JSON,
malformed JSON, extra top-level properties, a non-object `skills`, empty values,
object values, or values that are not concrete GitHub tree URLs. Preserve every
unrelated valid key. If an existing non-empty root has no aggregate, stop and
ask the user to repair the root. Also reject every key unless it case-sensitively
names a direct child directory under `RootPath` that directly contains `SKILL.md`;
reject separators and path traversal keys. Empty `skills` maps are valid.

For a root with no direct packages and no aggregate, create an empty in-memory
aggregate only after its first copied payload passes payload verification.

## Safe writes and sequential state

For every write, use a unique temporary sibling and, for an existing aggregate,
a unique sibling backup with `[IO.File]::Replace`. Delete temporary and backup
artifacts in `finally`. Remember whether the aggregate existed and its exact raw
text when read. Immediately before replacement, compare both existence and raw
text and abort if either changed.

After replacement, parse and verify the file again. Use that verified raw text
and parsed state for the next selection in the same root. Process same-root
aggregate changes sequentially; never reuse a preflight snapshot. Verify the
complete aggregate and selected key outcome before reporting `OK`.

Aggregate action is exactly one of `Set <concrete tree URL>`, `Remove selected
key`, or `No change (conflict skipped)`. If aggregate serialization,
replacement, parsing, or verification fails after payload verification, retain
the payload and report `Payload installed; aggregate update failed (<reason>)`.
