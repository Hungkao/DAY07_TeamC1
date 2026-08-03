"""
bench.py — Script đánh giá benchmark cá nhân cho Lab 7 (Checkpoint 5).

Thành viên: Nguyễn Hữu Khánh Tùng
Strategy: FixedSizeChunker(chunk_size=500, overlap=50)
Corpus: data/k3_university/
"""
import sys
from pathlib import Path

# Đảm bảo UTF-8 output trên Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

from ingest import build_knowledge_base
from src.chunking import FixedSizeChunker
from src.embeddings import _mock_embed
from src.agent import KnowledgeBaseAgent

# ----------------------------------------------------------------------
# THÔNG TIN THÀNH VIÊN & CẤU HÌNH STRATEGY
# ----------------------------------------------------------------------
MEMBER_NAME = "Nguyễn Hữu Khánh Tùng"
STRATEGY_NAME = "Fixed-size baseline"
CHUNKER_CONFIG = FixedSizeChunker(chunk_size=500, overlap=50)
EMBEDDING_BACKEND = "MockEmbedder (local mock)"

# ----------------------------------------------------------------------
# 5 BENCHMARK QUERIES CHÍNH THỨC CỦA NHÓM C1
# ----------------------------------------------------------------------
OFFICIAL_QUERIES = [
    {
        "id": 1,
        "title": "Lịch đăng ký kỳ 2026.1",
        "query": "Ba đợt đăng ký lớp học kỳ 2026.1 diễn ra trong khoảng thời gian nào?",
        "filter": {"audience": "student", "semester": "2026.1"},
        "gold_doc": "course-registration-03",
        "evidence": ["22/07/2026", "03/08/2026", "15/08/2026", "22/08/2026"],
        "gold_answer": (
            "Đăng ký chính thức từ 16h00 ngày 22/07/2026 đến 14h00 ngày 03/08/2026. "
            "Đăng ký điều chỉnh từ 16h00 ngày 03/08/2026 đến 14h00 ngày 15/08/2026. "
            "Đăng ký thêm từ 16h00 ngày 15/08/2026 đến 16h00 ngày 22/08/2026."
        ),
    },
    {
        "id": 2,
        "title": "Ba giai đoạn đăng ký",
        "query": "Quy trình đăng ký học tập chương trình đại học gồm những giai đoạn nào?",
        "filter": {"audience": "all", "registration_phase": "policy"},
        "gold_doc": "course-registration-04, course-registration-07",
        "evidence": ["Đăng ký học phần", "Đăng ký lớp chính thức", "Điều chỉnh đăng ký"],
        "gold_answer": "Quy trình gồm ba giai đoạn: đăng ký học phần, đăng ký lớp chính thức và điều chỉnh đăng ký.",
    },
    {
        "id": 3,
        "title": "Giới hạn tín chỉ kỳ 2026.1",
        "query": "Trong kỳ 2026.1, sinh viên bình thường và sinh viên bị cảnh báo học tập được đăng ký bao nhiêu tín chỉ?",
        "filter": {"audience": "student", "semester": "2026.1"},
        "gold_doc": "course-registration-03",
        "evidence": ["12", "24", "28", "08", "14", "18"],
        "gold_answer": (
            "Sinh viên bình thường thuộc chương trình chuẩn được đăng ký từ 12 đến 24 tín chỉ; "
            "chương trình Elitech từ 12 đến 28 tín chỉ. Sinh viên bị cảnh báo học tập mức 2 hoặc 3 "
            "thuộc chương trình chuẩn được đăng ký từ 8 đến 14 tín chỉ; chương trình Elitech từ 8 đến 18 tín chỉ."
        ),
    },
    {
        "id": 4,
        "title": "Rút học phần và học phí",
        "query": "Sinh viên rút học phần trong 7 tuần đầu phải đóng bao nhiêu học phí và có ngoại lệ nào?",
        "filter": {"audience": "all", "registration_phase": "policy"},
        "gold_doc": "course-registration-07",
        "evidence": ["7 tuần đầu", "50%", "tuần đầu tiên của học kỳ thứ hai", "không áp dụng cho học kỳ hè"],
        "gold_answer": (
            "Nếu đề nghị rút học phần trong 7 tuần đầu và được chấp thuận, sinh viên thông thường phải đóng 50% học phí. "
            "Nếu rút trong tuần đầu tiên của học kỳ thứ hai và được chấp thuận thì không phải đóng học phí. Quy định này không áp dụng cho học kỳ hè."
        ),
    },
    {
        "id": 5,
        "title": "Lớp đầy và hủy đăng ký",
        "query": "Sinh viên SoICT cần làm gì khi muốn đăng ký vào lớp đã đầy hoặc muốn hủy đăng ký lớp?",
        "filter": {"audience": "student", "registration_phase": "add-drop"},
        "gold_doc": "course-registration-08",
        "evidence": ["Đơn xin đăng ký vào lớp đã đầy", "Đơn xin hủy đăng ký lớp", "đơn vị quản lý học phần"],
        "gold_answer": (
            "Sinh viên cần dùng đơn xin đăng ký lớp/lớp đầy hoặc đơn xin hủy đăng ký lớp, "
            "thực hiện theo hướng dẫn và gửi tới đúng trường, viện hoặc khoa quản lý học phần."
        ),
    },
]


def evaluate_evidence(chunks: list[dict], evidence_list: list[str]) -> list[str]:
    """Kiểm tra các từ/cụm từ bằng chứng có xuất hiện trong top-3 chunks hay không."""
    found = []
    combined_text = " ".join([c.get("content", "") for c in chunks])
    for ev in evidence_list:
        if ev.lower() in combined_text.lower():
            found.append(ev)
    return found


def calculate_score(chunks: list[dict], gold_docs: str, found_evidence: list[str], total_evidence: int) -> int:
    """
    Quy tắc chấm:
    2 điểm: Top-3 có chunk chứa đầy đủ bằng chứng và thuộc đúng gold doc.
    1 điểm: Top-3 có chunk liên quan nhưng thiếu bằng chứng hoặc không ở top-1.
    0 điểm: Top-3 không có chunk đáp án.
    """
    if not chunks:
        return 0
    top1_doc = chunks[0]["metadata"].get("doc_id", "")
    gold_list = [g.strip() for g in gold_docs.split(",")]
    
    any_gold_in_top3 = any(c["metadata"].get("doc_id") in gold_list for c in chunks)
    if not any_gold_in_top3:
        return 0

    if top1_doc in gold_list and len(found_evidence) == total_evidence:
        return 2
    return 1


def run_benchmark():
    data_dir = Path("data/k3_university")
    store = build_knowledge_base(data_dir, _mock_embed, chunker=CHUNKER_CONFIG)
    
    total_docs = len(list(data_dir.glob("*.md")))
    total_chunks = store.get_collection_size()

    print("=" * 80)
    print("                 LAB 07 BENCHMARK OUTPUT — CHECKPOINT 5")
    print("=" * 80)
    print(f" Thành viên           : {MEMBER_NAME}")
    print(f" Embedding Backend    : {EMBEDDING_BACKEND}")
    print(f" Chiến lược (Strategy): {STRATEGY_NAME}")
    print(f" Tham số Strategy     : chunk_size=500, overlap=50")
    print(f" Số tài liệu Corpus   : {total_docs} files (.md)")
    print(f" Số Chunk đã Nạp      : {total_chunks} chunks")
    print("=" * 80)

    agent = KnowledgeBaseAgent(
        store=store,
        llm_fn=lambda prompt: "Trả lời chính xác dựa trên ngữ cảnh trích xuất từ quy chế HUST."
    )

    total_score = 0

    for item in OFFICIAL_QUERIES:
        q_id = item["id"]
        q_title = item["title"]
        q_str = item["query"]
        meta_filter = item["filter"]
        gold_doc = item["gold_doc"]
        evidence_list = item["evidence"]

        print(f"\n" + "-" * 80)
        print(f"❓ QUERY {q_id} [{q_title}]: {q_str}")
        print(f"   Gold Document  : {gold_doc}")
        print(f"   Metadata Filter: {meta_filter}")
        print("-" * 80)

        # 1. Unfiltered Search
        unfiltered_results = store.search(q_str, top_k=3)
        print("\n🔹 [Top-3 UNFILTERED Search]:")
        for rank, r in enumerate(unfiltered_results, 1):
            doc_id = r["metadata"].get("doc_id", r["id"])
            chunk_idx = r["metadata"].get("chunk_index", 0)
            url = r["metadata"].get("source_url", "N/A")
            score = r["score"]
            snippet = r["content"].strip().replace("\n", " ")[:80]
            print(f"   {rank}. [Score: {score:.4f}] Doc: {doc_id} (chunk {chunk_idx}) | URL: {url}")
            print(f"      Preview: {snippet}...")

        # 2. Filtered Search
        filtered_results = store.search_with_filter(q_str, top_k=3, metadata_filter=meta_filter)
        print("\n🔸 [Top-3 FILTERED Search (Metadata)]: ")
        for rank, r in enumerate(filtered_results, 1):
            doc_id = r["metadata"].get("doc_id", r["id"])
            chunk_idx = r["metadata"].get("chunk_index", 0)
            url = r["metadata"].get("source_url", "N/A")
            score = r["score"]
            snippet = r["content"].strip().replace("\n", " ")[:80]
            print(f"   {rank}. [Score: {score:.4f}] Doc: {doc_id} (chunk {chunk_idx}) | URL: {url}")
            print(f"      Preview: {snippet}...")

        # Evaluate evidence & score
        found_ev = evaluate_evidence(filtered_results, evidence_list)
        q_score = calculate_score(filtered_results, gold_doc, found_ev, len(evidence_list))
        total_score += q_score

        agent_ans = agent.answer(q_str, top_k=3)

        print("\n📊 [ĐÁNH GIÁ KẾT QUẢ]:")
        print(f"   - Bằng chứng khớp   : {len(found_ev)}/{len(evidence_list)} ({found_ev})")
        print(f"   - Agent Answer      : {agent_ans}")
        print(f"   - Điểm số Query     : {q_score} / 2")

    print("\n" + "=" * 80)
    print(f"  TỔNG ĐIỂM BENCHMARK CÁ NHÂN: {total_score} / 10 điểm")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmark()
