"""CP5 benchmark for Nguyen Van Phong's sentence-chunking strategy.

Official runs must use the shared local multilingual embedder.  ``--embedding-provider
mock`` is provided only for a no-network smoke test of this script.
"""

from __future__ import annotations

import argparse
import os
from typing import Any

from dotenv import load_dotenv

from ingest import build_knowledge_base, load_documents
from src.agent import KnowledgeBaseAgent
from src.chunking import SentenceChunker
from src.embeddings import LOCAL_EMBEDDING_MODEL, LocalEmbedder, _mock_embed


MEMBER = "Nguyễn Văn Phong"
DATA_DIR = "data/k3_university"
TOP_K = 3
STRATEGY = "SentenceChunker"
STRATEGY_PARAMETERS = {"max_sentences_per_chunk": 3}

BENCHMARKS: list[dict[str, Any]] = [
    {
        "name": "Query 1 — Lịch đăng ký kỳ 2026.1",
        "query": "Ba đợt đăng ký lớp học kỳ 2026.1 diễn ra trong khoảng thời gian nào?",
        "filter": {"audience": "student", "semester": "2026.1"},
        "gold_docs": ["course-registration-03"],
        "evidence": ["22/07/2026", "03/08/2026", "15/08/2026", "22/08/2026"],
    },
    {
        "name": "Query 2 — Ba giai đoạn đăng ký",
        "query": "Quy trình đăng ký học tập chương trình đại học gồm những giai đoạn nào?",
        "filter": {"audience": "all", "registration_phase": "policy"},
        "gold_docs": ["course-registration-04", "course-registration-07"],
        "evidence": ["Đăng ký học phần", "Đăng ký lớp chính thức", "Điều chỉnh đăng ký"],
    },
    {
        "name": "Query 3 — Giới hạn tín chỉ kỳ 2026.1",
        "query": "Trong kỳ 2026.1, sinh viên bình thường và sinh viên bị cảnh báo học tập được đăng ký bao nhiêu tín chỉ?",
        "filter": {"audience": "student", "semester": "2026.1"},
        "gold_docs": ["course-registration-03"],
        "evidence": ["12", "24", "28", "08", "14", "18"],
    },
    {
        "name": "Query 4 — Rút học phần và học phí",
        "query": "Sinh viên rút học phần trong 7 tuần đầu phải đóng bao nhiêu học phí và có ngoại lệ nào?",
        "filter": {"audience": "all", "registration_phase": "policy"},
        "gold_docs": ["course-registration-07"],
        "evidence": ["7 tuần đầu", "50%", "tuần đầu tiên của học kỳ thứ hai", "không áp dụng cho học kỳ hè"],
    },
    {
        "name": "Query 5 — Lớp đầy và hủy đăng ký",
        "query": "Sinh viên SoICT cần làm gì khi muốn đăng ký vào lớp đã đầy hoặc muốn hủy đăng ký lớp?",
        "filter": {"audience": "student", "registration_phase": "add-drop"},
        "gold_docs": ["course-registration-08"],
        "evidence": ["Đơn xin đăng ký vào lớp đã đầy", "Đơn xin hủy đăng ký lớp", "đơn vị quản lý học phần"],
    },
]


def _context_demo_llm(prompt: str) -> str:
    """Show grounded context when no real LLM is configured for the benchmark."""
    context = prompt.split("Context:\n", 1)[-1].split("\n\nQuestion:", 1)[0]
    return "[Demo LLM — cần đối chiếu với gold answer]\n" + context[:900]


def _matched_evidence(content: str, evidence: list[str]) -> list[str]:
    content_folded = content.casefold()
    return [item for item in evidence if item.casefold() in content_folded]


def _print_top_results(label: str, results: list[dict[str, Any]], evidence: list[str]) -> None:
    print(f"{label}:")
    if not results:
        print("  (không có kết quả)")
        return

    for rank, result in enumerate(results, start=1):
        metadata = result["metadata"]
        preview = " ".join(result["content"].split())[:220]
        matched = _matched_evidence(result["content"], evidence)
        print(
            f"  {rank}. score={result['score']:.4f} "
            f"doc_id={metadata.get('doc_id')} chunk_index={metadata.get('chunk_index')}"
        )
        print(f"     source_url={metadata.get('source_url', 'not-stated')}")
        print(f"     preview={preview}")
        print(f"     evidence matched={matched or 'none'}")


def _retrieval_score(results: list[dict[str, Any]], evidence: list[str]) -> int:
    """Score retrieved evidence only; final 0/1/2 also needs human agent-answer review."""
    matched = {
        item
        for result in results
        for item in _matched_evidence(result["content"], evidence)
    }
    if set(evidence).issubset(matched):
        return 2
    return 1 if matched else 0


def _select_embedder(provider: str):
    if provider == "mock":
        return _mock_embed
    return LocalEmbedder(model_name=os.getenv("LOCAL_EMBEDDING_MODEL", LOCAL_EMBEDDING_MODEL))


def run(provider: str) -> None:
    load_dotenv(override=False)
    chunker = SentenceChunker(**STRATEGY_PARAMETERS)
    embedder = _select_embedder(provider)
    backend = getattr(embedder, "_backend_name", embedder.__class__.__name__)
    documents = load_documents(DATA_DIR)
    store = build_knowledge_base(DATA_DIR, embedding_fn=embedder, chunker=chunker)
    agent = KnowledgeBaseAgent(store=store, llm_fn=_context_demo_llm)

    print("=== CP5 BENCHMARK ===")
    print(f"Thành viên: {MEMBER}")
    print(f"Embedding backend: {backend}")
    print(f"Strategy: {STRATEGY}")
    print(f"Strategy parameters: {STRATEGY_PARAMETERS}")
    print(f"Số tài liệu: {len(documents)}")
    print(f"Số chunk đã nạp: {store.get_collection_size()}")
    if provider == "mock":
        print("WARNING: mock chỉ dùng smoke test; không dùng kết quả này cho so sánh chính thức.")

    for benchmark in BENCHMARKS:
        print(f"\n=== {benchmark['name']} ===")
        print(f"Query: {benchmark['query']}")
        print(f"Gold document: {', '.join(benchmark['gold_docs'])}")
        print(f"Metadata filter: {benchmark['filter']}")

        unfiltered = store.search(benchmark["query"], top_k=TOP_K)
        filtered = store.search_with_filter(
            benchmark["query"], top_k=TOP_K, metadata_filter=benchmark["filter"]
        )
        _print_top_results("Top-3 unfiltered", unfiltered, benchmark["evidence"])
        _print_top_results("Top-3 filtered", filtered, benchmark["evidence"])
        print("Agent answer (unfiltered retrieval):")
        print(agent.answer(benchmark["query"], top_k=TOP_K))
        print(
            "Điểm retrieval đề xuất (cần kiểm agent answer trước khi chốt): "
            f"{_retrieval_score(filtered, benchmark['evidence'])}/2"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Nguyen Van Phong's CP5 sentence-chunking benchmark.")
    parser.add_argument(
        "--embedding-provider",
        choices=("local", "mock"),
        default=os.getenv("EMBEDDING_PROVIDER", "local").lower(),
        help="Use local for the official benchmark; mock is only a smoke test.",
    )
    args = parser.parse_args()
    run(args.embedding_provider)


if __name__ == "__main__":
    main()
