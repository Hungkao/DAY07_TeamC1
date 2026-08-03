"""CP5 benchmark ca nhan cua Nguyen Tuan Vu.

Giu nguyen corpus, embedding, top-k va 5 query chung cua nhom; bien chien
luoc ca nhan duy nhat la RecursiveChunker(chunk_size=400).
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ingest import build_knowledge_base, load_documents
from src.agent import KnowledgeBaseAgent
from src.chunking import RecursiveChunker
from src.embeddings import LocalEmbedder, MockEmbedder


STRATEGY = "RecursiveChunker"
CHUNK_SIZE = 400
TOP_K = 3


@dataclass(frozen=True)
class BenchmarkQuery:
    question: str
    metadata_filter: dict[str, Any]
    gold_answer: str
    gold_doc_ids: tuple[str, ...]
    evidence: tuple[str, ...]


QUERIES = (
    BenchmarkQuery(
        question="Ba đợt đăng ký lớp học kỳ 2026.1 diễn ra trong khoảng thời gian nào?",
        metadata_filter={"audience": "student", "semester": "2026.1"},
        gold_answer=(
            "Đăng ký chính thức từ 22/07 đến 03/08/2026; đăng ký điều chỉnh từ "
            "03/08 đến 15/08/2026; đăng ký thêm vào các lớp đang mở từ 15/08 đến 22/08/2026."
        ),
        gold_doc_ids=("course-registration-03",),
        evidence=("22/07/2026", "03/08/2026", "15/08/2026", "22/08/2026"),
    ),
    BenchmarkQuery(
        question="Quy trình đăng ký học tập chương trình đại học gồm những giai đoạn nào?",
        metadata_filter={"audience": "all", "registration_phase": "policy"},
        gold_answer=(
            "Quy trình gồm đăng ký học phần theo kế hoạch học tập, đăng ký lớp chính thức "
            "và điều chỉnh đăng ký trong thời hạn quy định."
        ),
        gold_doc_ids=("course-registration-04", "course-registration-07"),
        evidence=("Đăng ký học phần", "Đăng ký lớp chính thức", "Điều chỉnh đăng ký"),
    ),
    BenchmarkQuery(
        question=(
            "Theo quy chế, sinh viên bình thường và sinh viên bị cảnh báo học tập "
            "được đăng ký bao nhiêu tín chỉ trong học kỳ chính?"
        ),
        metadata_filter={"audience": "all", "registration_phase": "policy"},
        gold_answer=(
            "Sinh viên bình thường đăng ký từ 12 đến 24 tín chỉ. Sinh viên bị cảnh báo "
            "đăng ký từ 8 đến 14 tín chỉ ở chương trình chuẩn, hoặc từ 8 đến 18 tín chỉ "
            "ở chương trình ELITECH/hợp tác quốc tế."
        ),
        gold_doc_ids=("course-registration-07",),
        evidence=(
            "từ 12 đến 24", "tối thiểu 8 và tối đa 14", "tối thiểu 8 và tối đa 18",
        ),
    ),
    BenchmarkQuery(
        question="Sinh viên rút học phần trong 7 tuần đầu phải đóng bao nhiêu học phí và có ngoại lệ nào?",
        metadata_filter={"audience": "all", "registration_phase": "policy"},
        gold_answer=(
            "Trong 7 tuần đầu, sinh viên phải đóng 50% học phí; quy định có ngoại lệ ở "
            "tuần đầu tiên của học kỳ thứ hai và không áp dụng cho học kỳ hè."
        ),
        gold_doc_ids=("course-registration-07",),
        evidence=("7 tuần đầu", "50%", "tuần đầu tiên của học kỳ thứ hai", "không áp dụng cho học kỳ hè"),
    ),
    BenchmarkQuery(
        question="Sinh viên SoICT cần làm gì khi muốn đăng ký vào lớp đã đầy hoặc muốn hủy đăng ký lớp?",
        metadata_filter={"audience": "student", "registration_phase": "add-drop"},
        gold_answer=(
            "Sinh viên dùng đúng Đơn xin đăng ký vào lớp đã đầy hoặc Đơn xin hủy đăng ký "
            "lớp và gửi tới đơn vị quản lý học phần để được xem xét."
        ),
        gold_doc_ids=("course-registration-08",),
        evidence=("Đơn xin đăng ký vào lớp đã đầy", "Đơn xin hủy đăng ký lớp", "đơn vị quản lý học phần"),
    ),
)


def _tokens(text: str) -> set[str]:
    return {
        token.lower()
        for token in re.findall(r"[\wÀ-ỹ]+", text, flags=re.UNICODE)
        if len(token) > 2
    }


def _extractive_llm(prompt: str) -> str:
    """Demo LLM khong API: chon cau trong Context co lexical overlap cao.

    Ham khong doc gold answer va khong sinh them kien thuc ngoai context.
    """
    context_match = re.search(r"Context:\n(.*?)\n\nQuestion:", prompt, re.DOTALL)
    question_match = re.search(r"Question:\s*(.*?)\nAnswer:", prompt, re.DOTALL)
    if not context_match or not question_match:
        return "Chưa đủ dữ liệu trong context."

    question_tokens = _tokens(question_match.group(1))
    candidates: list[tuple[int, int, str]] = []
    source = "[?]"
    order = 0
    for line in context_match.group(1).splitlines():
        source_match = re.match(r"(\[\d+\]) Source:", line)
        if source_match:
            source = source_match.group(1)
            continue
        for sentence in re.split(r"(?<=[.!?])\s+|\n+", line):
            sentence = sentence.strip(" -")
            if len(sentence) < 20:
                continue
            overlap = len(question_tokens & _tokens(sentence))
            candidates.append((overlap, -order, f"{sentence} {source}"))
            order += 1

    candidates.sort(reverse=True)
    selected = [item[2] for item in candidates[:3] if item[0] > 0]
    return " ".join(selected) if selected else "Chưa đủ dữ liệu trong context."


class _FixedResultsStore:
    """Adapter de KnowledgeBaseAgent tao cau tra loi tu dung tap ket qua da loc."""

    def __init__(self, results: list[dict[str, Any]]) -> None:
        self.results = results

    def search(self, _question: str, top_k: int = TOP_K) -> list[dict[str, Any]]:
        return self.results[:top_k]


def _agent_answer(question: str, results: list[dict[str, Any]]) -> str:
    agent = KnowledgeBaseAgent(_FixedResultsStore(results), _extractive_llm)  # type: ignore[arg-type]
    return agent.answer(question, top_k=TOP_K)


def _result_block(results: list[dict[str, Any]]) -> str:
    if not results:
        return "_Không có kết quả._"
    lines: list[str] = []
    for rank, result in enumerate(results, start=1):
        metadata = result["metadata"]
        preview = " ".join(result["content"].split()).replace("|", "\\|")[:220]
        lines.append(
            f"{rank}. score={result['score']:.4f}; doc_id=`{metadata.get('doc_id')}`; "
            f"chunk={metadata.get('chunk_index')}; preview: {preview}"
        )
    return "\n".join(lines)


def _evaluate(results: list[dict[str, Any]], query: BenchmarkQuery) -> tuple[list[str], bool]:
    context = "\n".join(result["content"] for result in results).casefold()
    hits = [phrase for phrase in query.evidence if phrase.casefold() in context]
    gold_doc_hit = any(
        result["metadata"].get("doc_id") in query.gold_doc_ids for result in results
    )
    return hits, gold_doc_hit


def _build_report(data_dir: Path, backend: str, store: Any) -> str:
    lines = [
        "# Kết quả benchmark CP5 — Nguyễn Tuấn Vũ",
        "",
        f"- Corpus: `{data_dir.as_posix()}` ({len(load_documents(data_dir))} tài liệu)",
        f"- Strategy cá nhân: `{STRATEGY}(chunk_size={CHUNK_SIZE})`",
        f"- Embedding backend: `{backend}`",
        f"- Số chunk đã nạp: **{store.get_collection_size()}**",
        f"- Top-k: **{TOP_K}**",
        "- Agent demo: extractive, deterministic, chỉ chọn câu từ context; không dùng API và không đọc gold answer.",
        "",
        "> Gold answer chỉ dùng để đối chiếu thủ công. Chỉ số tự động bên dưới đo evidence trong top-3 ở mức chunk, không tự nhận là điểm đúng/sai cuối cùng.",
        "",
    ]

    evidence_passes = 0
    for index, query in enumerate(QUERIES, start=1):
        plain = store.search(query.question, top_k=TOP_K)
        filtered = store.search_with_filter(
            query.question, top_k=TOP_K, metadata_filter=query.metadata_filter
        )
        plain_hits, plain_doc_hit = _evaluate(plain, query)
        filtered_hits, filtered_doc_hit = _evaluate(filtered, query)
        if len(filtered_hits) == len(query.evidence):
            evidence_passes += 1

        answer = _agent_answer(query.question, filtered)
        lines.extend(
            [
                f"## Query {index}",
                "",
                f"**Câu hỏi:** {query.question}",
                "",
                f"**Filter:** `{query.metadata_filter}`",
                "",
                f"**Gold answer:** {query.gold_answer}",
                "",
                f"**Gold document:** {', '.join(f'`{doc_id}`' for doc_id in query.gold_doc_ids)}",
                "",
                "### A — Không filter",
                "",
                _result_block(plain),
                "",
                f"Evidence hit: **{len(plain_hits)}/{len(query.evidence)}**; "
                f"gold doc trong top-3: **{'có' if plain_doc_hit else 'không'}**.",
                "",
                "### B — Có metadata filter",
                "",
                _result_block(filtered),
                "",
                f"Evidence hit: **{len(filtered_hits)}/{len(query.evidence)}** "
                f"({', '.join(filtered_hits) if filtered_hits else 'không có'}); "
                f"gold doc trong top-3: **{'có' if filtered_doc_hit else 'không'}**.",
                "",
                f"**Câu trả lời agent demo:** {answer}",
                "",
            ]
        )

    lines.extend(
        [
            "## Tổng kết CP5",
            "",
            f"- Query có đủ toàn bộ evidence trong top-3 sau filter: **{evidence_passes}/5**.",
            "- Kết quả A/B được giữ nguyên để sang CP6 phân tích precision, recall và failure case.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Chạy benchmark CP5 cá nhân của Nguyễn Tuấn Vũ")
    parser.add_argument("--data-dir", type=Path, default=Path("data/k3_university"))
    parser.add_argument(
        "--embedding",
        choices=("local", "mock"),
        default="mock",
        help="Mặc định mock để CP5 chạy trên mọi máy; chọn local sau khi cài requirements-local.txt.",
    )
    parser.add_argument("--output", type=Path, default=Path("report/BENCHMARK_NGUYENTUANVU.md"))
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    if args.embedding == "local":
        embedder = LocalEmbedder()
    else:
        embedder = MockEmbedder()
    backend = getattr(embedder, "_backend_name", args.embedding)

    chunker = RecursiveChunker(chunk_size=CHUNK_SIZE)
    store = build_knowledge_base(args.data_dir, embedder, chunker=chunker)
    report = _build_report(args.data_dir, backend, store)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")

    print(f"Strategy: {STRATEGY}(chunk_size={CHUNK_SIZE})")
    print(f"Embedding backend: {backend}")
    print(f"Documents: {len(load_documents(args.data_dir))}")
    print(f"Chunks: {store.get_collection_size()}")
    print(f"Queries: {len(QUERIES)} (A/B filter, top-{TOP_K})")
    print(f"Report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
