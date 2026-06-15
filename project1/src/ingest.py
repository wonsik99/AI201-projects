from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path

from .config import RAW_DATA_DIR


@dataclass(frozen=True)
class SourceDocument:
    title: str
    source_name: str
    source_url: str
    text: str


HEADER_RE = re.compile(r"^(Title|Source URL|Source URLs|Source Type|Date Collected):\s*(.*)$", re.I)


def clean_text(text: str) -> str:
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\b(cookie policy|accept cookies|sign up|log in|share|advertisement)\b", " ", text, flags=re.I)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def parse_document(path: Path, raw_dir: Path = RAW_DATA_DIR) -> SourceDocument:
    raw = path.read_text(encoding="utf-8")
    metadata: dict[str, str] = {}
    body_lines: list[str] = []
    in_header = True

    for line in raw.splitlines():
        match = HEADER_RE.match(line.strip())
        if in_header and match:
            metadata[match.group(1).lower()] = match.group(2).strip()
            continue
        if in_header and not line.strip():
            in_header = False
            continue
        if in_header:
            in_header = False
        body_lines.append(line)

    title = metadata.get("title") or path.stem.replace("_", " ").title()
    source_url = metadata.get("source urls") or metadata.get("source url", "")
    text = clean_text("\n".join(body_lines))
    try:
        source_name = str(path.relative_to(raw_dir))
    except ValueError:
        source_name = path.name
    return SourceDocument(title=title, source_name=source_name, source_url=source_url, text=text)


def load_documents(raw_dir: Path = RAW_DATA_DIR) -> list[SourceDocument]:
    paths = sorted(p for p in raw_dir.rglob("*.txt") if p.is_file())
    documents = [parse_document(path, raw_dir) for path in paths]
    return [doc for doc in documents if doc.text]


if __name__ == "__main__":
    docs = load_documents()
    print(f"Loaded {len(docs)} documents from {RAW_DATA_DIR}")
    for doc in docs:
        print(f"- {doc.source_name}: {len(doc.text)} chars")
