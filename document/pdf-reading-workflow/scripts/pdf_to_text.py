#!/usr/bin/env python3
"""Convert a PDF to local txt/md cache files beside the PDF.

Default output:
    <pdf-folder>/.pdf_cache/<pdf-stem>.txt
    <pdf-folder>/.pdf_cache/<pdf-stem>.md
    <pdf-folder>/.pdf_cache/<pdf-stem>.meta.json

The script is intentionally dependency-light except for PyMuPDF.
Install once with: pip install PyMuPDF
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, cast

EXTRACTOR = "pymupdf"
EXTRACTOR_VERSION = "1"


def safe_stem(path: Path) -> str:
    stem = path.stem.strip()
    stem = re.sub(r"[<>:\"/\\|?*\x00-\x1f]", "_", stem)
    stem = re.sub(r"\s+", " ", stem).strip()
    return stem or "document"


def parse_pages(spec: str | None, page_count: int) -> list[int]:
    if not spec:
        return list(range(page_count))

    pages: set[int] = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start = int(start_s) if start_s else 1
            end = int(end_s) if end_s else page_count
            if start > end:
                raise ValueError(f"Invalid page range: {part}")
            pages.update(range(start - 1, end))
        else:
            pages.add(int(part) - 1)

    invalid = [p + 1 for p in pages if p < 0 or p >= page_count]
    if invalid:
        raise ValueError(f"Page(s) out of range: {invalid}; PDF has {page_count} pages")
    return sorted(pages)


def file_fingerprint(path: Path) -> dict[str, object]:
    stat = path.stat()
    return {
        "source_pdf": str(path.resolve()),
        "pdf_size": stat.st_size,
        "pdf_mtime_ns": stat.st_mtime_ns,
    }


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def cache_is_fresh(meta_path: Path, pdf_path: Path, pages_spec: str | None) -> bool:
    if not meta_path.exists():
        return False
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except Exception:
        return False

    expected = file_fingerprint(pdf_path)
    return (
        meta.get("source_pdf") == expected["source_pdf"]
        and meta.get("pdf_size") == expected["pdf_size"]
        and meta.get("pdf_mtime_ns") == expected["pdf_mtime_ns"]
        and meta.get("extractor") == EXTRACTOR
        and meta.get("extractor_version") == EXTRACTOR_VERSION
        and meta.get("pages_spec") == pages_spec
    )


def extract_pdf(pdf_path: Path, pages_spec: str | None) -> tuple[str, int, list[int]]:
    try:
        import fitz  # PyMuPDF
    except ImportError as exc:
        raise SystemExit(
            "PyMuPDF is not installed. Install it once with: pip install PyMuPDF"
        ) from exc

    doc = fitz.open(pdf_path)
    page_indexes = parse_pages(pages_spec, doc.page_count)
    chunks: list[str] = []
    for page_index in page_indexes:
        page = doc.load_page(page_index)
        text = cast(str, page.get_text("text"))
        chunks.append(f"=== Page {page_index + 1} / {doc.page_count} ===\n{text.rstrip()}\n")
    page_count = doc.page_count
    doc.close()
    return "\n".join(chunks).strip() + "\n", page_count, page_indexes


def to_markdown(text: str, title: str) -> str:
    return f"# {title}\n\n{text}"


def write_outputs(pdf_path: Path, text: str, page_count: int, page_indexes: Iterable[int], pages_spec: str | None) -> dict[str, object]:
    cache_dir = pdf_path.parent / ".pdf_cache"
    cache_dir.mkdir(exist_ok=True)
    stem = safe_stem(pdf_path)
    suffix = "" if not pages_spec else "__pages_" + re.sub(r"[^0-9A-Za-z,-]", "_", pages_spec)
    txt_path = cache_dir / f"{stem}{suffix}.txt"
    md_path = cache_dir / f"{stem}{suffix}.md"
    meta_path = cache_dir / f"{stem}{suffix}.meta.json"

    txt_path.write_text(text, encoding="utf-8")
    md_path.write_text(to_markdown(text, stem), encoding="utf-8")

    meta = {
        **file_fingerprint(pdf_path),
        "extractor": EXTRACTOR,
        "extractor_version": EXTRACTOR_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "pages": page_count,
        "extracted_pages": [p + 1 for p in page_indexes],
        "pages_spec": pages_spec,
        "text_sha256": hash_text(text),
        "txt_path": str(txt_path.resolve()),
        "md_path": str(md_path.resolve()),
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    meta["meta_path"] = str(meta_path.resolve())
    return meta


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Convert PDF to local txt/md cache beside the PDF.")
    parser.add_argument("pdf", help="Path to the PDF file")
    parser.add_argument("--force", action="store_true", help="Regenerate cache even if fresh")
    parser.add_argument("--pages", help="1-indexed page ranges, e.g. 1-5,8,10-")
    args = parser.parse_args(argv)

    pdf_path = Path(args.pdf).expanduser().resolve()
    if not pdf_path.exists():
        print(f"ERROR: PDF not found: {pdf_path}", file=sys.stderr)
        return 2
    if pdf_path.suffix.lower() != ".pdf":
        print(f"ERROR: Not a PDF file: {pdf_path}", file=sys.stderr)
        return 2

    cache_dir = pdf_path.parent / ".pdf_cache"
    stem = safe_stem(pdf_path)
    suffix = "" if not args.pages else "__pages_" + re.sub(r"[^0-9A-Za-z,-]", "_", args.pages)
    txt_path = cache_dir / f"{stem}{suffix}.txt"
    md_path = cache_dir / f"{stem}{suffix}.md"
    meta_path = cache_dir / f"{stem}{suffix}.meta.json"

    if not args.force and txt_path.exists() and md_path.exists() and cache_is_fresh(meta_path, pdf_path, args.pages):
        print(json.dumps({
            "status": "reused",
            "txt_path": str(txt_path.resolve()),
            "md_path": str(md_path.resolve()),
            "meta_path": str(meta_path.resolve()),
        }, ensure_ascii=False, indent=2))
        return 0

    text, page_count, page_indexes = extract_pdf(pdf_path, args.pages)
    meta = write_outputs(pdf_path, text, page_count, page_indexes, args.pages)
    print(json.dumps({"status": "generated", **meta}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
