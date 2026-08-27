# Candidate Selection and Placement

Read this reference after discovery and before any provisional plan. It owns
selection, root inference, semantic versus bundle placement, and plan
confirmation. It does not authorize copying.

## Selection

For one candidate, ask `Install / Cancel` unless the user named that candidate
explicitly. For multiple candidates, use a native multi-select picker. Never
install every discovered candidate by default. Show relative path, inferred root
and destination, sanitized package name, and the first approximately 80
characters of `description:`. Page lists longer than about 15 candidates while
preserving selections.

## Root choice

Use a semantic root for an independent package. If `Root` is omitted, inspect
`description:` first and `name:` second with case-insensitive heuristics. Use
only a strong match and show the evidence. Weak or overlapping matches require
an explicit choice. New roots require explicit confirmation.

Never infer bundle or collection placement from a shared owner, repository, URL,
or discovery directory. Bundle or collection placement is an explicit exception
for coupled members, shared runtime or distribution, or a maintained collection.
Infer and confirm the root separately for every selected candidate.

Use these semantic signals only as evidence:

| Signals | Root |
|---|---|
| browser, playwright, selenium, puppeteer, web automation | `browser` |
| api, rest, backend, server, database, sql, service contract, mcp | `backend` |
| rag, vector, embedding, retrieval, llm, prompt | `ai` |
| canvas, art, poster, visual design, ui/ux design, design system | `design` |
| vue, react, svelte, css, tailwind, frontend, component, tui | `frontend` |
| pdf, docx, pptx, xlsx, spreadsheet, obsidian | `document` |
| paper, literature, citation, pubmed, arxiv, peer review, research | `research` |
| test, testing, tdd, qa, regression | `testing` |
| install, link, audit, package, skill manager, cli tool | `tools` |
| documentation, blog, markdown, report, content, writing | `writing` |
| personal, custom, my skill, explicit myCreatsSkills | `myCreatsSkills` |

Recognize but do not auto-select these known upstream collections:

| Root | Upstream collection |
|---|---|
| `agent-browser` | `vercel-labs/agent-browser` |
| `grill` | `mattpocock/skills` |
| `openspec` | `Fission-AI/OpenSpec` |
| `superpowers-plus` | `xhyqaq/superpowers-plus` |
| `ui-ux-pro-max-skill` | `nextlevelbuilder/ui-ux-pro-max-skill` |

## Plan gates

Confirm root kind and name, evidence, destination, aggregate path, and every
bundle or collection exception for each selection. Build a provisional plan
without writing. The final plan must show:

```text
Source path  Package  Root kind/name  Destination  Aggregate path  Frontmatter action  Aggregate action  Conflict
```

Render the complete plan after conflict and mismatch decisions, then ask exactly
`Proceed / Change selection / Cancel`. A change returns to the relevant choice;
cancel leaves payloads and aggregates untouched.
