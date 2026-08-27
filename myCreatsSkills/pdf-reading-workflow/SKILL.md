---
name: pdf-reading-workflow
description: Standard workflow for reading or analyzing PDF files in OpenCode across different models. Use whenever the user provides, mentions, or asks to read/analyze/summarize a PDF, paper, article, report, scanned document, or .pdf file, especially when the active model may not support native PDF input. Always convert PDFs to text/markdown cache files beside the source PDF before analysis, then read the cache instead of the PDF.
---

# PDF Reading Workflow

Use this skill whenever a PDF must be read, summarized, analyzed, translated, or used as source material.

## Non-negotiable rule

Do **not** rely on native PDF reading. First convert the PDF to cache files, then read the generated `.txt` or `.md` file.

## Cache location

For a PDF at:

```text
<folder>/<paper>.pdf
```

write cache files to:

```text
<folder>/.pdf_cache/
```

Never write PDF extraction caches to global temp directories unless the user explicitly asks.

## Default workflow

1. Resolve the absolute PDF path.
2. Run `scripts/pdf_to_text.py` with the PDF path.
3. The script creates or reuses:
   - `<pdf-folder>/.pdf_cache/<pdf-stem>.txt`
   - `<pdf-folder>/.pdf_cache/<pdf-stem>.md`
   - `<pdf-folder>/.pdf_cache/<pdf-stem>.meta.json`
4. Read the `.txt` or `.md` cache file with the file-reading tool.
5. Perform the requested analysis from the cache text.

## Command

```powershell
python "C:\Users\WZY\.config\opencode\skills\pdf-reading-workflow\scripts\pdf_to_text.py" "<absolute-pdf-path>"
```

Useful options:

```powershell
# Force regeneration even if cache appears fresh
python "C:\Users\WZY\.config\opencode\skills\pdf-reading-workflow\scripts\pdf_to_text.py" "<pdf>" --force

# Only extract selected pages, 1-indexed inclusive
python "C:\Users\WZY\.config\opencode\skills\pdf-reading-workflow\scripts\pdf_to_text.py" "<pdf>" --pages 1-5
```

## Cache reuse policy

Reuse existing cache when `.meta.json` says the source PDF path, size, modified time, and extractor version match. Regenerate when any of these differ, or when extraction quality looks poor.

## Tool choice

The bundled script uses PyMuPDF by default. If PyMuPDF is missing, install it once:

```powershell
pip install PyMuPDF
```

If the PDF is scanned or text extraction is empty, use OCR fallback only after telling the user that OCR is slower and heavier.

## Token discipline

Do not paste full extracted PDFs into the conversation. Read only relevant sections when possible, using grep/search first for long papers.
