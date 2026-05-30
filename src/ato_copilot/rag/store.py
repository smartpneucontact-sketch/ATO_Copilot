from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Chunk:
    """Retrievable governance document chunk. Shape mirrors a ServiceNow
    KB article or SharePoint document — the kind of record State Street's
    Approved Technology List, control catalogs, and prior-ATO archives
    already sit in."""

    chunk_id: str
    source_type: str  # atl | control | architecture | prior_ato
    source_id: str
    section: str | None
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievedChunk:
    chunk: Chunk
    score: float
    matched_terms: list[str] = field(default_factory=list)
