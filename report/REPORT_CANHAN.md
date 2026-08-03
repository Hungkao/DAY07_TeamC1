# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Hữu Khánh Tùng
**MSSV:** 2A202601781
**Nhóm:** C1
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự Cosine đo góc giữa hai vector trong không gian đa chiều (giá trị từ -1 đến 1). Cosine similarity cao (gần 1) nghĩa là hai vector có cùng hướng, thể hiện hai đoạn văn bản có sự tương đồng cao về mặt ngữ nghĩa và nội dung.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Đăng ký học phần qua cổng thông tin sinh viên"
- Câu B: "Sinh viên thực hiện đăng ký môn học trên trang web của trường"
- Tại sao tương đồng: Cùng diễn đạt một hành động sinh viên đăng ký môn học trực tuyến, mặc dù cách dùng từ ngữ khác nhau.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Học phí được nộp qua tài khoản ngân hàng"
- Câu B: "Lịch thi học kỳ được công bố vào tuần thứ 10"
- Tại sao khác: Hai câu thuộc hai chủ đề hoàn toàn khác nhau trong môi trường đại học (tài chính học phí vs lịch thi).

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine similarity chỉ tập trung vào **hướng của vector (ngữ nghĩa)** mà không bị ảnh hưởng bởi độ dài của văn bản. Khoảng cách Euclid đo khoảng cách tuyệt đối giữa các điểm, nên hai văn bản có cùng nội dung nhưng độ dài khác nhau sẽ bị khoảng cách Euclid phạt khoảng cách rất lớn, trong khi góc Cosine vẫn giữ nguyên.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* Bước nhảy $step = chunk\_size - overlap = 500 - 50 = 450$.  
> Số lượng chunk = $\lceil \frac{length - overlap}{chunk\_size - overlap} \rceil = \lceil \frac{10000 - 50}{500 - 50} \rceil = \lceil \frac{9950}{450} \rceil = \lceil 22.11 \rceil = 23$.  
> *Đáp án:* **23 chunks**.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, bước nhảy giảm xuống $500 - 100 = 400$, số chunk sẽ tăng lên thành $\lceil \frac{9900}{400} \rceil = 25$ chunks. Việc tăng overlap giúp bảo toàn ranh giới ngữ cảnh giữa các đoạn (tránh cắt đứt câu/ý giữa chừng), nhưng đánh đổi lại là làm tăng tổng số chunk và chi phí lưu trữ/tính toán embedding.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`FixedSizeChunker.chunk` (Strategy cá nhân của tôi)** — hướng tiếp cận:
> Áp dụng thuật toán chia văn bản cố định theo ký tự với `chunk_size=500` và `overlap=50`. Sử dụng vòng lặp sliding window bước nhảy 450 ký tự để trượt trên văn bản. Đoạn overlap 50 ký tự giữa các chunk đóng vai trò bảo vệ ngữ cảnh ranh giới không bị ngắt đứt.

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Sử dụng regex `re.split(r"(?<=\. )|(?<=\! )|(?<=\? )|(?<=\.\n)", text)` để tách văn bản chính xác tại các dấu câu kết thúc. Mỗi câu được làm sạch khoảng trắng và gom nhóm tối đa `max_sentences_per_chunk` câu liên tiếp vào một chunk.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán đệ quy phân cấp theo ưu tiên các dấu phân cách `["\n\n", "\n", ". ", " ", ""]`. Base case dừng đệ quy khi độ dài đoạn văn nhỏ hơn `chunk_size` hoặc danh sách dấu phân cách rỗng. Các khối nhỏ liền nhau được ghép lại để tối ưu dung lượng chunk.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Lưu trữ in-memory dưới dạng danh sách `dict` chứa `id`, `content`, `metadata` (bản sao `dict(doc.metadata)`) và `embedding` được tạo từ `_embedding_fn`. Hàm `search()` tính điểm similarity bằng tích vô hướng (`_dot`) giữa vector query và vector từng chunk, sắp xếp giảm dần theo điểm và lấy `top_k`.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> Hàm `search_with_filter` áp dụng chiến lược **Pre-filtering** (lọc dữ liệu theo metadata trước rồi mới xếp hạng vector) để đảm bảo không bỏ sót kết quả phù hợp. Hàm `delete_document` lọc giữ lại các record có `id` và `metadata['doc_id']` khác `doc_id` cần xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Truy xuất `top_k` chunk từ store, đóng gói thành chuỗi ngữ cảnh có đánh số `[1]`, `[2]` kèm nguồn `Source: doc_id`. Xây dựng prompt chứa chỉ dẫn nghiêm ngặt ("Chỉ sử dụng ngữ cảnh được cung cấp...") rồi truyền vào `llm_fn` để tạo câu trả lời grounding có trích dẫn.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```text
============================= test session starts =============================
platform win32 -- Python 3.11.0, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\AITHUCCHIEN\LABS\Lab07(team)\DAY07_TeamC1
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED   [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED    [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED   [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================= 42 passed in 0.09s ==============================
```

**Số lượng bài test vượt qua (pass):** **42** / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Đăng ký học phần qua cổng thông tin sinh viên | Sinh viên thực hiện đăng ký môn học trên trang web của trường | cao | 0.2269 | Đúng |
| 2 | Học phí được nộp qua tài khoản ngân hàng | Lịch thi học kỳ được công bố vào tuần thứ 10 | thấp | 0.1450 | Đúng |
| 3 | Hủy đăng ký học phần trong tuần đầu | Xin rút bớt học phần đã đăng ký | cao | 0.0371 | Thấp hơn dự đoán |
| 4 | Mã môn học và số tín chỉ | Tên phòng học và thứ tiết | thấp | 0.0090 | Đúng |
| 5 | Quy định về cảnh báo học tập | Thời gian làm việc của thư viện | thấp | 0.1843 | Đúng |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp số 3 ("Hủy đăng ký học phần" vs "Xin rút bớt học phần") có điểm thực tế khá thấp khi thử nghiệm với MockEmbedder. Điều này phản ánh mô hình nhúng băm giả lập (MockEmbedder) chưa học được mối quan hệ đồng nghĩa thực tế. Đối với mô hình thật (như multilingual MiniLM), vector biểu diễn ngữ nghĩa sẽ phản ánh chính xác sự đồng nghĩa bất chấp từ ngữ khác nhau.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá chính thức của nhóm C1** trên mã nguồn cá nhân với chiến lược **`FixedSizeChunker(500, overlap=50)`**:

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Ba đợt đăng ký lớp học kỳ 2026.1 diễn ra trong khoảng thời gian nào? | `hust-course-registration-info`: Đăng ký chính thức 22/07-03/08, điều chỉnh 03/08-15/08, thêm 15/08-22/08... | 0.2777 | Có | Trả lời chính xác mốc thời gian 3 đợt đăng ký lớp kỳ 2026.1 từ thông báo HUST. |
| 2 | Quy trình đăng ký học tập chương trình đại học gồm những giai đoạn nào? | `course-registration-04`: Quy trình gồm 3 giai đoạn: đăng ký học phần, đăng ký lớp và điều chỉnh... | 0.1663 | Có | Cung cấp đầy đủ 3 giai đoạn đăng ký học tập đại học theo quy chế 2025. |
| 3 | Trong kỳ 2026.1, sinh viên bình thường và sinh viên bị cảnh báo học tập được đăng ký bao nhiêu tín chỉ? | `course-registration-03`: Sinh viên chuẩn 12-24 tín chỉ; Elitech 12-28; Cảnh báo mức 2-3 từ 8-14 tín chỉ... | 0.1364 | Có | Nêu chính xác số lượng tín chỉ tối thiểu và tối đa cho từng đối tượng sinh viên. |
| 4 | Sinh viên rút học phần trong 7 tuần đầu phải đóng bao nhiêu học phí và có ngoại lệ nào? | `course-registration-07`: Rút học phần trong 7 tuần đầu đóng 50% học phí; rút tuần đầu kỳ 2 không đóng... | 0.1663 | Có | Trích dẫn đúng quy định hoàn 50% học phí và ngoại lệ học kỳ thứ hai/học kỳ hè. |
| 5 | Sinh viên SoICT cần làm gì khi muốn đăng ký vào lớp đã đầy hoặc muốn hủy đăng ký lớp? | `course-registration-08`: Dùng đơn xin đăng ký lớp đầy hoặc đơn xin hủy đăng ký lớp gửi đơn vị quản lý... | 0.2579 | Có | Hướng dẫn đúng biểu mẫu và quy trình nộp đơn cho sinh viên SoICT ở đợt add-drop. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** **5** / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Chiến lược `FixedSizeChunker(500, 50)` có ưu điểm là phủ diện rộng thông tin, nhưng nhược điểm là dễ ngắt đứt ranh giới câu giữa 2 chunk. Việc kết hợp **Metadata Pre-filtering** (`semester` và `registration_phase`) đóng vai trò cực kỳ quan trọng giúp triệt tiêu hoàn toàn các chunk nhiễu từ các học kỳ khác.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 10 / 10 |
| **Tổng phần cá nhân** | **60 / 60** |
