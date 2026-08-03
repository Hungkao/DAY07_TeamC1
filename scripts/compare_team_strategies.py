"""Re-run the four team strategies under one fair CP6 configuration.

The individual benchmark files are preserved as submitted. This script is the
normalized group comparison: same six documents, five queries, filters,
MockEmbedder and top-k; only the chunking strategy changes.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ingest import build_knowledge_base, load_documents  # noqa: E402
from src.chunking import (  # noqa: E402
    ChunkingStrategyComparator,
    FixedSizeChunker,
    RecursiveChunker,
    SentenceChunker,
)
from src.embeddings import MockEmbedder  # noqa: E402


DATA_DIR = ROOT / "data" / "k3_university"
TOP_K = 3


@dataclass(frozen=True)
class Query:
    text: str
    metadata_filter: dict[str, str]
    gold_docs: tuple[str, ...]
    evidence: tuple[str, ...]


QUERIES = (
    Query(
        "Ba đợt đăng ký lớp học kỳ 2026.1 diễn ra trong khoảng thời gian nào?",
        {"audience": "student", "semester": "2026.1"},
        ("course-registration-03",),
        ("22/07/2026", "03/08/2026", "15/08/2026", "22/08/2026"),
    ),
    Query(
        "Quy trình đăng ký học tập chương trình đại học gồm những giai đoạn nào?",
        {"audience": "all", "registration_phase": "policy"},
        ("course-registration-04", "course-registration-07"),
        ("Đăng ký học phần", "Đăng ký lớp chính thức", "Điều chỉnh đăng ký"),
    ),
    Query(
        "Theo quy chế, sinh viên bình thường và sinh viên bị cảnh báo học tập được đăng ký bao nhiêu tín chỉ trong học kỳ chính?",
        {"audience": "all", "registration_phase": "policy"},
        ("course-registration-07",),
        ("từ 12 đến 24", "tối thiểu 8 và tối đa 14", "tối thiểu 8 và tối đa 18"),
    ),
    Query(
        "Sinh viên rút học phần trong 7 tuần đầu phải đóng bao nhiêu học phí và có ngoại lệ nào?",
        {"audience": "all", "registration_phase": "policy"},
        ("course-registration-07",),
        ("7 tuần đầu", "50%", "tuần đầu tiên của học kỳ thứ hai", "không áp dụng cho học kỳ hè"),
    ),
    Query(
        "Sinh viên SoICT cần làm gì khi muốn đăng ký vào lớp đã đầy hoặc muốn hủy đăng ký lớp?",
        {"audience": "student", "registration_phase": "add-drop"},
        ("course-registration-08",),
        ("Đơn xin đăng ký vào lớp đã đầy", "Đơn xin hủy đăng ký lớp", "đơn vị quản lý"),
    ),
)


class HeadingChunker:
    """Keep each Markdown heading with its section; recursively split long sections."""

    def __init__(self, chunk_size: int = 400) -> None:
        self.chunk_size = chunk_size
        self.fallback = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        sections = [part.strip() for part in re.split(r"(?m)(?=^#{1,6}\s+)", text) if part.strip()]
        chunks: list[str] = []
        for section in sections:
            if len(section) <= self.chunk_size:
                chunks.append(section)
                continue
            first_line, _, body = section.partition("\n")
            pieces = self.fallback.chunk(body or section)
            for piece in pieces:
                if body and not piece.startswith(first_line):
                    candidate = f"{first_line}\n{piece}"
                    if len(candidate) <= self.chunk_size:
                        chunks.append(candidate)
                    else:
                        chunks.extend(self.fallback.chunk(candidate))
                else:
                    chunks.append(piece)
        return [chunk for chunk in chunks if chunk.strip()]


STRATEGIES = (
    ("Nguyễn Hữu Khánh Tùng", "Fixed 500/overlap 50", FixedSizeChunker(500, 50)),
    ("Nguyễn Tuấn Vũ", "Recursive 400", RecursiveChunker(chunk_size=400)),
    ("Nguyễn Văn Phong", "Sentence 3", SentenceChunker(max_sentences_per_chunk=3)),
    ("Nguyễn Phúc Hưng", "Heading 400 + recursive fallback", HeadingChunker(400)),
)


def evidence_hits(results: list[dict], query: Query) -> list[str]:
    context = "\n".join(item["content"] for item in results).casefold()
    return [evidence for evidence in query.evidence if evidence.casefold() in context]


def retrieval_score(hit_count: int, evidence_count: int) -> int:
    if hit_count == evidence_count:
        return 2
    if hit_count > 0:
        return 1
    return 0


def print_baseline() -> None:
    comparator = ChunkingStrategyComparator()
    print("BASELINE (chunk_size=400; first 3 documents)")
    print("document\tstrategy\tcount\tavg_length")
    for doc in load_documents(DATA_DIR)[:3]:
        compared = comparator.compare(doc.content, chunk_size=400)
        for strategy, stats in compared.items():
            print(f"{doc.id}\t{strategy}\t{stats['count']}\t{stats['avg_length']:.1f}")
    print()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print_baseline()
    print("NORMALIZED CP6 (MockEmbedder, top_k=3)")
    print("member\tstrategy\tchunks\tQ1\tQ2\tQ3\tQ4\tQ5\ttotal")
    detail_lines: list[str] = []

    for member, strategy_name, chunker in STRATEGIES:
        store = build_knowledge_base(DATA_DIR, MockEmbedder(), chunker=chunker)
        scores: list[int] = []
        for index, query in enumerate(QUERIES, start=1):
            plain = store.search(query.text, top_k=TOP_K)
            filtered = store.search_with_filter(query.text, TOP_K, query.metadata_filter)
            plain_hits = evidence_hits(plain, query)
            filtered_hits = evidence_hits(filtered, query)
            score = retrieval_score(len(filtered_hits), len(query.evidence))
            scores.append(score)
            filtered_docs = ",".join(
                f"{item['metadata'].get('doc_id')}#{item['metadata'].get('chunk_index')}"
                for item in filtered
            )
            detail_lines.append(
                f"{member}\tQ{index}\t{len(plain_hits)}/{len(query.evidence)}\t"
                f"{len(filtered_hits)}/{len(query.evidence)}\t{score}\t{filtered_docs}"
            )
        print(
            f"{member}\t{strategy_name}\t{store.get_collection_size()}\t"
            + "\t".join(str(score) for score in scores)
            + f"\t{sum(scores)}"
        )

    print("\nDETAIL: member, query, evidence without filter, evidence with filter, score, filtered top-3")
    print("member\tquery\tunfiltered\tfiltered\tscore\tfiltered_top3")
    print("\n".join(detail_lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
