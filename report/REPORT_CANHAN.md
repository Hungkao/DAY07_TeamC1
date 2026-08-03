# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Văn Phong
**Nhóm:** C1
**Ngày:** 3/8/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai embedding có hướng gần nhau, nên mô hình đánh giá hai câu có nội dung/ngữ nghĩa tương tự. Điểm càng gần 1 thì mức tương đồng càng cao.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên cần đăng ký học phần trước khi học kỳ bắt đầu.
- Câu B: Người học phải chọn môn trên hệ thống trước khi kỳ học diễn ra.
- Tại sao tương đồng: Hai câu dùng từ khác nhau nhưng cùng nói về yêu cầu đăng ký môn trước học kỳ.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Sinh viên cần đăng ký học phần trước khi học kỳ bắt đầu.
- Câu B: Thư viện mở cửa từ 8 giờ sáng đến 5 giờ chiều.
- Tại sao khác: Một câu nói về đăng ký học phần, câu còn lại nói về giờ mở cửa thư viện.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine đo góc giữa các vector nên nhấn mạnh hướng ngữ nghĩa và ít bị ảnh hưởng bởi độ lớn vector. Khoảng cách Euclid phụ thuộc cả độ dài vector, vì vậy thường kém ổn định hơn khi so sánh embedding văn bản.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23`.
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Số chunk tăng thành `ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25`. Overlap lớn hơn giúp giữ ngữ cảnh qua ranh giới chunk, nhưng tạo nhiều chunk hơn, tốn bộ nhớ/thời gian embed và làm tăng nội dung lặp.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex `(?<=[.!?])[ \n]+` để tách tại khoảng trắng đứng sau dấu kết thúc câu, vì vậy dấu `.`, `!`, `?` vẫn nằm trong câu trước. Mỗi câu được `strip()` và bỏ phần rỗng; sau đó các câu được gộp tối đa ba câu cho strategy cá nhân `SentenceChunker(max_sentences_per_chunk=3)`. Text rỗng hoặc chỉ có khoảng trắng trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> `chunk()` gọi `_split()` với thứ tự separator đoạn → dòng → câu → từ → ký tự, sau đó gộp các phần liền nhau nhưng không vượt `chunk_size`, đồng thời bỏ chunk rỗng. `_split()` dừng khi text đã đủ ngắn; nếu hết separator hoặc gặp separator rỗng thì cắt cố định theo kích thước. Một phần còn dài sau khi tách sẽ được gọi đệ quy với separator ưu tiên thấp hơn để ưu tiên giữ ranh giới tự nhiên.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được đổi thành record gồm id duy nhất, content, bản sao metadata có `doc_id`, và embedding; in-memory store lưu các record này, còn ChromaDB được dùng khi có sẵn. Khi search, query chỉ được embed một lần, sau đó tính dot product với embedding của từng record và xếp giảm dần để lấy top-k. `ingest.py` thực hiện chunk trước khi gọi `add_documents`, vì store coi mỗi Document đầu vào là một record độc lập.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter()` lọc trước rồi mới rank: record chỉ được giữ khi mọi cặp key/value trong filter khớp metadata. Cách này tránh việc top-k ban đầu bị tài liệu sai đối tượng hoặc sai học kỳ chiếm hết chỗ. `delete_document()` dùng `metadata['doc_id']` để loại toàn bộ chunk của một tài liệu gốc và trả `True` nếu thực sự có record bị xóa.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent gọi `store.search(question, top_k)` rồi ghép các chunk thành Context được đánh số `[1]`, `[2]` và kèm `doc_id` để truy vết nguồn. Prompt yêu cầu LLM chỉ dùng Context, nói rõ khi thông tin không đủ, rồi đặt `Question` và nhãn `Answer:`. Nếu store rỗng, agent trả thông báo thiếu ngữ cảnh thay vì gọi LLM.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
================================================ test session starts ================================================
platform win32 -- Python 3.13.12, pytest-9.1.1, pluggy-1.6.0 -- E:\LabAITC\DAY07_TeamC1\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: E:\LabAITC\DAY07_TeamC1
plugins: anyio-4.14.2
collected 42 items

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                          [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                                   [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                            [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                             [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                                  [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED                  [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED                        [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                         [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED                       [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                         [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                         [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                                    [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                                [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                          [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED                 [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED                     [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED               [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED                     [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                         [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                           [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                             [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                                   [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED                        [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                          [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED              [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                           [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                                    [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                                   [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                              [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                          [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED                     [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                         [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                               [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                         [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED      [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED                    [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED                   [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED       [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED                  [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED           [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED     [100%]

================================================ 42 passed in 0.11s =================================================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên cần đăng ký học phần trước khi học kỳ bắt đầu. | Người học phải chọn môn trên hệ thống trước khi kỳ học diễn ra. | cao | 0.7463 | Có |
| 2 | Sinh viên có thể hủy lớp đã đăng ký trong thời gian điều chỉnh. | Trong đợt điều chỉnh, người học được phép bỏ lớp học phần. | cao | 0.7278 | Có |
| 3 | Lớp có dưới năm sinh viên đăng ký có thể bị hủy. | Học phần ít người đăng ký có nguy cơ không được mở lớp. | cao | 0.8064 | Có |
| 4 | Sinh viên được đăng ký tối đa bao nhiêu tín chỉ? | Thư viện mở cửa từ mấy giờ mỗi ngày? | thấp | 0.5735 | Có |
| 5 | Điều kiện tiên quyết của học phần là gì? | Thời tiết tại Hà Nội hôm nay thế nào? | thấp | 0.8825 | Không |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 5 bất ngờ nhất: hai câu ít liên quan nhưng score lại 0.8825. Embedding biểu diễn mẫu thống kê và ngữ cảnh học từ dữ liệu huấn luyện, không suy luận logic như con người; vì vậy score cao không tự động chứng minh hai câu trả lời cùng một vấn đề. Khi retrieval, cần kết hợp metadata, chất lượng corpus và kiểm tra nội dung chunk thay vì chỉ dựa vào score.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Ba đợt đăng ký lớp học kỳ 2026.1 diễn ra trong khoảng thời gian nào? | `hust-course-registration-info`, chunk 2: lịch đăng ký học phần kỳ 2026.1, không chứa các mốc đăng ký lớp trong gold answer. | 0.7343 | Không | Demo agent chỉ trả lại context của tài liệu lịch khác, không trả lời đủ ba mốc thời gian. |
| 2 | Quy trình đăng ký học tập chương trình đại học gồm những giai đoạn nào? | `course-registration-04`, chunk 0: mở đầu quy định đăng ký học tập và phần ba giai đoạn. | 0.7264 | Có, một phần | Demo agent grounded theo hai tài liệu quy chế, nhưng không tự tổng hợp trọn vẹn ba giai đoạn. |
| 3 | Trong kỳ 2026.1, sinh viên bình thường và sinh viên bị cảnh báo học tập được đăng ký bao nhiêu tín chỉ? | `hust-course-registration-info`, chunk 3: nêu 12–24 TC và tối đa 14 TC khi cảnh báo. | 0.8198 | Có, một phần | Demo agent nêu một phần giới hạn tín chỉ; thiếu các mức Elitech và một số điều kiện trong gold answer. |
| 4 | Sinh viên rút học phần trong 7 tuần đầu phải đóng bao nhiêu học phí và có ngoại lệ nào? | `course-registration-03`, chunk 6: nhắc rút trong 7 tuần đầu và học phí theo quy định, chưa có mức 50%/ngoại lệ. | 0.8224 | Không ở top-1 | Trong top-3 có `course-registration-07` chứa 50% học phí và ngoại lệ; demo agent chỉ trả context, chưa tổng hợp hoàn chỉnh. |
| 5 | Sinh viên SoICT cần làm gì khi muốn đăng ký vào lớp đã đầy hoặc muốn hủy đăng ký lớp? | `course-registration-03`, chunk 5: xử lý trạng thái hết chỗ, không có biểu mẫu SoICT. | 0.7588 | Không | Demo agent lấy nhiễu từ tài liệu kế hoạch; khi dùng filter `add-drop`, `course-registration-08` mới lên top-1. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 3 / 5 (Q2, Q3, Q4 ở truy vấn không filter). Với filter, Q4 và Q5 được cải thiện, nhưng Q1/Q3 rỗng do `semester` bị parse thành số thực thay vì chuỗi.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Qua so sánh các strategy trong nhóm, tôi nhận ra chunk theo câu giữ ngữ pháp tốt nhưng có thể làm bằng chứng dạng liệt kê hoặc ngoại lệ bị tách sang chunk khác. Các strategy recursive và heading/section đáng thử cho văn bản quy định vì chúng có thể giữ tiêu đề, điều kiện và ngoại lệ trong cùng một đơn vị ngữ nghĩa. Tôi cũng học được rằng metadata filter chỉ đáng tin khi chuẩn hóa cả giá trị lẫn kiểu dữ liệu của metadata.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 3 / 10 |
| **Tổng phần cá nhân** | **53 / 60** |
