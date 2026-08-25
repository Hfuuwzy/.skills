---
name: weekly-report-literature-note
description: Write or rewrite Chinese Markdown literature-reading notes for my weekly report (每周汇报/周报/每周笔记). Use when asked to draft a paper note in my first-year grad student voice: grounded, lightly critical, learns writing tricks; default to exactly four subheadings under each paper entry (简介/概念或问题/关键设计点/实验与收获), keep first-person minimal, avoid excessive scare quotes, and do not add extra subsections.
---

# Weekly Report Literature Note

Use this skill to create or edit one paper-reading note block inside my weekly report markdown file.

Filling a paper note involves these steps:
1. Collect minimal inputs (file path, target location, paper title, key facts)
2. Read nearby notes to match tone and numbering
3. Draft using the 4-heading template (no extra subsections)
4. Tighten wording (reduce first-person + reduce scare quotes)
5. Run the final checklist

## Inputs to collect (ask only if missing)

- Target markdown file path
- Target location (where the paper note should live): e.g. `# 第三次汇报(YYYY.M.D)` -> `## 二、文献阅读`
- Paper title
- Key facts to include (3-8 bullets): what it proposes, what's new, how it's trained/evaluated
- Evidence anchors if available (optional): `Table X`, `Figure Y`
- 1-2 sentences: why this topic/paper is worth reading now (motivation)

If facts are NOT provided and no PDF/analysis note is given, do NOT guess. Ask the user for 3-5 bullets and 1-2 evidence anchors.

## Decide the operation

1. **Editing an existing paper entry**: there is already a `### N、<Paper Title>` block.
2. **Creating a new paper entry**: there is no `### ...` block yet.

## Workflow: Editing an existing paper entry

1. Read the target markdown file around `## 二、文献阅读` (and 1-2 existing paper notes) to match tone.
2. Find the paper entry line `### N、<Paper Title>`.
3. Under it, ensure there are EXACTLY 4 subheadings, and ONLY these 4:
   - `#### N.1 简介`
   - `#### N.2 概念/问题定义`
   - `#### N.3 关键设计点`
   - `#### N.4 实验与收获`
4. Rewrite ONLY the text under those headings. Do not touch other sections of the file.
5. Run the final checklist before finishing.

## Workflow: Creating a new paper entry

1. Read the target markdown file to find `## 二、文献阅读` and the existing `### <number>、...` entries.
2. Choose the next index `N` (max existing + 1), unless the user specifies `N`.
3. Insert this template at the requested position (default: append under `## 二、文献阅读`).
4. Fill content using the guidance below.
5. Run the final checklist.

## Output template (keep exactly 4 headings)

```markdown
### N、<Paper Title>

#### N.1 简介
<why this is worth reading now + what the paper mainly does + 1 sentence on paper structure>

#### N.2 概念/问题定义
<define the key concept/problem + threat model boundaries if relevant>

#### N.3 关键设计点
<core idea/pipeline at a high level + why it is needed>

#### N.4 实验与收获
<2-4 memorable results + one key ablation + 1-2 writing tricks learned>
```

## Tone rules (match my style)

- First-year grad student voice: grounded, not pretending to be an expert.
- Keep first-person minimal. Prefer: `这篇/这里/这部分/这种设置/从结果能看出...` over repeated `我觉得/我感觉/我认为...`.
- Avoid emotive scare-quote adjectives like `“恶心”` / `“很论文”`. Use quotes mainly for actual terms (e.g., `trigger`, `token`).
- Include 1 small critique, but keep it factual (point to a setting/metric choice and why it might be questionable).
- Avoid AI-summary vibe: no long outlines, no many-level headings, no excessive “全面总结”.

## Content guidance per subsection

### `#### N.1 简介` (short)

Include (2-4 sentences total):
- Why this direction has many papers now (e.g., supply chain risk, finetuning/deployment complexity)
- What the paper mainly does (one clean sentence)
- How the paper is structured (one clean sentence): definition/threat model -> method -> data/training trick -> experiments/defenses

### `#### N.2 概念/问题定义`

- Define the core concept/problem in plain language.
- If applicable, state the threat model boundary: who can attack (developer/provider vs end user).
- Add 1 sentence connecting the definition to why it matters in real systems (chain effect: description -> reasoning -> decision).

### `#### N.3 关键设计点`

- Explain the core idea/pipeline at a high level.
- Explain why the design is needed (e.g., stealth, utility preservation).
- Mention any key dataset/training trick in 2-4 sentences.

### `#### N.4 实验与收获`

- Prefer a small set of memorable results: 2-4 numbers max.
- If you cite numbers, attach anchors like `(Table 1)` / `(Figure 4)` when known.
- Call out ONE key ablation that teaches something.
- End with 1-2 sentences: writing tricks learned (how they define metrics, how they build the story).

## Safety constraint

- Do NOT output executable attack steps, PoC code, or instructions for deploying backdoors. Keep to high-level academic understanding.

## Final checklist (must pass)

- Exactly 4 `#### N.x` headings under the paper entry; no extra subsections.
- First-person is rare (aim: `我` <= 3 occurrences; avoid repeating `我觉得/我感觉`).
- Quotes used mainly for terms; avoid scare-quote adjectives.
- Includes: motivation + what it does + structure (in N.1), definition/threat model (N.2), key idea (N.3), experiments + takeaway + writing tricks (N.4).
- Only edits the intended paper block; does not reformat the whole file.
