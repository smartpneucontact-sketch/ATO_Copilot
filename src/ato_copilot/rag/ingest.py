"""Walk the corpus and produce a list of Chunks.

Layout:
    {corpus_dir}/atl/*.md           — Approved Technology List entries
    {corpus_dir}/controls/*.md      — Security control family summaries
    {corpus_dir}/architecture/*.md  — Reference architecture patterns
    {corpus_dir}/prior_atos/*.md    — Prior ATO decisions (precedent)
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from ato_copilot.config import get_settings
from ato_copilot.rag.retriever import Retriever
from ato_copilot.rag.store import Chunk

_SECTION = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def _chunk_by_heading(path: Path, source_type: str) -> list[Chunk]:
    text = path.read_text(encoding="utf-8")
    source_id = path.stem
    matches = list(_SECTION.finditer(text))
    if not matches:
        return [Chunk(
            chunk_id=f"{source_type}:{source_id}",
            source_type=source_type,
            source_id=source_id,
            section=None,
            text=text.strip(),
        )]
    chunks: list[Chunk] = []
    for i, m in enumerate(matches):
        section = m.group(1).strip()
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunks.append(Chunk(
            chunk_id=f"{source_type}:{source_id}:{i:02d}",
            source_type=source_type,
            source_id=source_id,
            section=section,
            text=text[start:end].strip(),
        ))
    return chunks


def _chunk_whole(path: Path, source_type: str) -> Chunk:
    return Chunk(
        chunk_id=f"{source_type}:{path.stem}",
        source_type=source_type,
        source_id=path.stem,
        section=None,
        text=path.read_text(encoding="utf-8").strip(),
    )


def load_chunks(corpus_dir: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for p in sorted((corpus_dir / "controls").glob("*.md")):
        chunks.extend(_chunk_by_heading(p, "control"))
    for p in sorted((corpus_dir / "architecture").glob("*.md")):
        chunks.extend(_chunk_by_heading(p, "architecture"))
    for p in sorted((corpus_dir / "atl").glob("*.md")):
        chunks.append(_chunk_whole(p, "atl"))
    for p in sorted((corpus_dir / "prior_atos").glob("*.md")):
        chunks.append(_chunk_whole(p, "prior_ato"))
    return chunks


def build_retriever() -> Retriever:
    s = get_settings()
    retriever = Retriever()
    retriever.index(load_chunks(s.corpus_dir))
    return retriever


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", help="Test query after ingest.")
    args = parser.parse_args()
    s = get_settings()
    chunks = load_chunks(s.corpus_dir)
    print(f"Loaded {len(chunks)} chunks from {s.corpus_dir}")
    by_type: dict[str, int] = {}
    for c in chunks:
        by_type[c.source_type] = by_type.get(c.source_type, 0) + 1
    for k, v in sorted(by_type.items()):
        print(f"  {k}: {v}")
    if args.query:
        retriever = Retriever()
        retriever.index(chunks)
        for i, r in enumerate(retriever.search(args.query, k=s.top_k), 1):
            head = r.chunk.section or r.chunk.source_id
            print(f"  {i}. [{r.score:.2f}] {r.chunk.source_type}:{r.chunk.source_id} -- {head}")


if __name__ == "__main__":
    main()
