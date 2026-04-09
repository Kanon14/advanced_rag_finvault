from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from backend.schemas.retrieve import ExcludedMatch, RetrieveMatch


@dataclass
class FilterOptions:
    min_score: float
    max_context_chars: int
    deduplicate: bool
    unique_pages: bool


def _fingerprint(text: str) -> str:
    normalized = re.sub(r"\s+", " ", text.strip().lower())
    return normalized[:500]


def filter_candidates(
    candidates: list[RetrieveMatch], options: FilterOptions
) -> tuple[list[RetrieveMatch], list[ExcludedMatch], dict[str, int]]:
    included: list[RetrieveMatch] = []
    excluded: list[ExcludedMatch] = []
    reasons = Counter()

    seen_fingerprints: set[str] = set()
    seen_doc_pages: set[tuple[str, int | None]] = set()

    current_chars = 0

    for rank, match in enumerate(candidates, start=1):
        meta = match.metadata or {}
        reason: str | None = None

        if match.score < options.min_score:
            reason = "below_score_threshold"

        if reason is None and options.deduplicate:
            fp = _fingerprint(match.text)
            if fp in seen_fingerprints:
                reason = "duplicate_text"
            else:
                seen_fingerprints.add(fp)

        if reason is None and options.unique_pages:
            key = (str(meta.get("document_id")), meta.get("page_number"))
            if key in seen_doc_pages:
                reason = "duplicate_page"
            else:
                seen_doc_pages.add(key)

        if reason is None:
            next_chars = current_chars + len(match.text)
            if next_chars > options.max_context_chars:
                reason = "context_budget_exceeded"
            else:
                current_chars = next_chars

        if reason is None:
            match.retrieval_rank = rank
            match.included_in_prompt = True
            included.append(match)
        else:
            reasons[reason] += 1
            excluded.append(
                ExcludedMatch(
                    chunk_id=match.chunk_id,
                    score=float(match.score),
                    reason=reason,
                )
            )

    return included, excluded, dict(reasons)
