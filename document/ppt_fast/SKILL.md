---
name: ppt_fast
description: Fast, classroom-ready PPT production workflow for Chinese academic/technical presentations. Use when creating, revising, auditing, or regenerating PowerPoint decks from notes, papers, markdown drafts, or topic briefs, especially when the user wants a clean light-background style, large readable fonts, diagrams/tables paired with explanation text, PPTX plus HTML preview outputs, and strict formatting QA. Coordinates with brainstorming, ckm:slides, ckm:design-system, ckm:ui-styling, ui-ux-pro-max, pptx-generator, pptx, pptx-html-fidelity-audit, ppt-keynote, playwright, and visual-qa.
---

# ppt_fast

Build teaching-ready PPT decks quickly, with the quality bar learned from the KG 网络嵌入 deck.

## Non-negotiables

- Use a light, readable classroom style. Avoid dark sci-fi, neon glow, tiny dense text, decorative emoji, and generic AI-poster visuals.
- Keep **every visible text run at least 16pt**. This includes page numbers, footers, captions, formulas, references, table cells, chart labels, and chips. If content does not fit at 16pt, split the slide, reduce copy, or change the layout. Do not solve overflow by shrinking to 9-15pt.
- Use one Chinese-safe font family throughout, preferably `Microsoft YaHei` on Windows. Keep fallback families only in HTML previews.
- Pair words and visuals on nearly every slide: explanation text on one side, diagram/table/formula/cards on the other. Do not make pure text pages unless the user explicitly asks.
- Verify with actual tooling before final status. Never say a deck is done from visual intuition alone.

## Default visual system

Use this palette unless the user gives a brand guide:

- Background: warm white `#F7F4ED`
- Paper/card: `#FFFFFF`
- Ink: `#1B2733`
- Muted text: `#475467`
- Divider line: `#D9DEE7`
- Primary blue: `#1B365D`
- Teal accent: `#2F8F83`
- Amber accent: `#D88A24`
- Soft blue: `#E8EEF8`
- Soft teal: `#E7F3F1`
- Soft amber: `#FFF1DA`

Typography defaults:

- Cover title: 48-56pt.
- Slide title: 34-42pt, short and top-left.
- Main narrative: 20-24pt.
- Bullets: 18-22pt.
- Tables/cards/captions/references/page numbers: **16pt minimum**.
- Prefer fewer larger words over many small labels.

## Slide architecture

Use an 18-slide maximum for a classroom topic unless the user requests otherwise. A good teaching structure is:

1. Cover.
2. Roadmap/目录.
3. Why the topic matters.
4. Formal definition or core mechanism.
5. Method timeline.
6. Evaluation/task setup.
7-10. Main method families.
11-13. Recent or advanced direction.
14. Downstream applications.
15. Challenges.
16. Future directions.
17. Summary spine.
18. References, split into multiple slides if 16pt references do not fit.

Do not copy this outline mechanically. Preserve the user’s topic logic, but keep a clear narrative spine: problem → representation/mechanism → method evolution → applications → limits → takeaway.

## Production workflow

1. **Load supporting skills.** For creative/visual PPT tasks, use or load: `brainstorming`, `ckm:slides`, `ckm:design-system`, `pptx-generator`, `pptx`, and `visual-qa`. For UI/HTML preview work, also use `ckm:ui-styling`, `ui-ux-pro-max`, `ppt-keynote`, and `playwright`. For PPTX/HTML drift, use `pptx-html-fidelity-audit`.
2. **Read the source.** Inspect the user’s draft/notes and current deck if one exists. Identify what to compress, what to explain visually, and what must be backed by real sources.
3. **Research selectively.** For academic content, use librarian/background research for claims, model names, performance numbers, and citations. Do not invent papers, metrics, or results.
4. **Create a single content guide.** Write or update a markdown guide that contains the slide plan, design rules, sources, and per-slide copy. Treat it as the deck’s source of truth.
5. **Generate both HTML and PPTX.** Prefer a script-based pipeline so edits are repeatable. HTML is for browser visual QA and quick navigation; PPTX is the final editable deliverable.
6. **Use cursor-flow layout.** Place content with explicit x/y/w/h rails and fail on overflow. Keep footer and header inside the 16pt rule or remove them.
7. **Audit fonts and overflow.** Run PPTX structure checks, XML wrapping checks, and font-floor checks. A passing deck must have no visible text under 16pt.
8. **Visual QA.** Render key slides in a browser or inspect exported screenshots. Check CJK readability, no clipping, no tiny labels, and no dark/neon style drift. Use Oracle/visual-qa for significant decks before final delivery.

## Layout patterns that worked

- Left explanation + right visual/table is the default. It prevents “only pictures” and “only bullets”.
- A slide should usually contain: one short title, one 1-2 sentence narrative, up to 3 bullets, one visual block, and one takeaway.
- For method comparisons, use stacked method cards or large-row tables. If a table needs small text, split it across slides.
- For GraphRAG/RAG-style comparisons, use a 3-column comparison table with large cells rather than dense prose.
- For summaries, use a visible flow spine plus 2-3 large takeaway statements.
- For references, do not use 9pt bibliography grids. Use 16pt cards, fewer references, or multiple reference slides.

## Lessons from the KG 网络嵌入 deck

- The generated deck originally used some 9-15pt text for page numbers, footers, table cells, chips, and references. This was readable on a monitor but too small for classroom projection. `ppt_fast` upgrades this into a hard 16pt floor.
- Dense reference pages are the first place where PPT generators regress to tiny text. Split references instead.
- Footer chrome is optional. If it forces 10pt text, remove the footer or make it 16pt and reduce other decoration.
- Method cards with two text lines are better than large tables, but the cards must still keep 16pt labels and enough vertical height.
- HTML hash navigation must be tested if an HTML preview is produced; stale hash behavior can invalidate screenshot QA.

## Required verification commands/patterns

- Run Python compile on deck-generation scripts.
- Run any layout verifier bundled with the project.
- Inspect PPTX XML for `wrap_none` and `spAutoFit`; the target is zero unless intentionally justified.
- Run `scripts/check_pptx_font_floor.py <deck.pptx> --min-size 16` from this skill or copy its logic into the project. Treat any failure as a deck issue, not a cosmetic warning.
- Capture or inspect key slides after regeneration: cover, a method/table slide, the densest comparison slide, the summary slide, and the references slide.

## Final delivery checklist

- PPTX exists and opens structurally.
- HTML preview exists if requested or useful for QA.
- All visible text runs are >=16pt.
- No slide has content outside the safe rail.
- No clipped CJK text, no overlapped footer, no dense reference grid.
- Final answer lists output files and the exact verification evidence.
