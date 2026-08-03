# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Tuấn Vũ
**Nhóm:** C1
**Ngày:** 2026-08-03

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Độ tương tự cosine cao nghĩa là hai vector embedding tạo với nhau một góc nhỏ và có hướng gần giống nhau. Với text embedding có chất lượng, điều này thường cho thấy hai đoạn văn có nội dung hoặc ý nghĩa gần nhau dù không nhất thiết dùng đúng cùng từ ngữ.

**Ví dụ có độ tương tự CAO:**
- Câu A: Sinh viên có thể điều chỉnh lớp học phần trong thời gian nào?
- Câu B: Thời hạn đổi lớp đã đăng ký dành cho sinh viên là khi nào?
- Tại sao tương đồng: Hai câu dùng từ khác nhau nhưng đều hỏi về thời gian điều chỉnh lớp học phần.

**Ví dụ có độ tương tự THẤP:**
- Câu A: Sinh viên được đăng ký tối đa bao nhiêu tín chỉ?
- Câu B: Thư viện mở cửa vào những ngày nào?
- Tại sao khác: Một câu hỏi về giới hạn học tập, câu còn lại hỏi lịch hoạt động của thư viện nên chủ đề và ý định không liên quan trực tiếp.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine tập trung vào hướng của vector thay vì độ lớn, nên ít bị ảnh hưởng bởi khác biệt về chuẩn vector hoặc độ dài văn bản. Điều này phù hợp với mục tiêu so sánh mẫu ngữ nghĩa của các embedding hơn là khoảng cách tuyệt đối giữa chúng.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Phép tính:* `ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23`.
> *Đáp án:* 23 chunks.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, bước trượt còn 400 ký tự và số chunk tăng thành `ceil((10000 - 100) / 400) = 25`. Overlap lớn hơn giúp giữ ngữ cảnh nằm gần ranh giới chunk, nhưng làm tăng dữ liệu trùng lặp, số embedding và chi phí tìm kiếm.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi dùng regex `(?<=[.!?])\s+` để tách tại khoảng trắng sau dấu kết thúc câu, nhờ lookbehind nên dấu câu vẫn nằm ở câu phía trước. Sau khi tách, từng câu được `strip()`, phần rỗng bị loại và các câu được gom theo `max_sentences_per_chunk`; text rỗng trả về danh sách rỗng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán ưu tiên ranh giới tự nhiên theo thứ tự đoạn, dòng, câu, từ rồi ký tự; các phần nhỏ liên tiếp được gom cho tới trước khi vượt `chunk_size`. Base case thứ nhất trả ngay khi text đã đủ ngắn; base case thứ hai cắt fixed-size khi hết separator hoặc gặp separator rỗng. Mỗi lần đệ quy đều giảm danh sách separator hoặc xử lý một phần text nhỏ hơn để tránh vòng lặp vô hạn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Mỗi `Document` được chuẩn hóa thành record gồm ID duy nhất, content, bản sao metadata và embedding; `metadata.doc_id` được bổ sung khi đầu vào chưa có. Khi tìm kiếm, query chỉ được embedding một lần, sau đó tính dot product với từng record, sắp xếp score giảm dần và cắt `top_k`. Các embedding được chuẩn hóa nên dot product tương đương cosine trong pipeline của lab.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc record trước khi xếp hạng và chỉ giữ record khớp mọi cặp key/value; nếu filter là `None` thì gọi lại `search` để hai đường xử lý cho cùng kết quả. `delete_document` tạo lại danh sách record sau khi loại toàn bộ chunk có `metadata.doc_id` tương ứng và trả `True` khi kích thước store thực sự giảm.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Agent gọi `store.search(question, top_k)`, đánh số từng chunk `[1]`, `[2]` và kèm `source_url`, `source` hoặc `doc_id` để truy vết. Prompt yêu cầu LLM chỉ trả lời từ Context, nói rõ khi dữ liệu không đủ và dẫn số nguồn khi có thể; nếu store không có kết quả, agent trả thông báo trực tiếp mà không gọi LLM.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
python -m pytest tests -v

platform win32 -- Python 3.11.9, pytest-9.1.1, pluggy-1.6.0
collected 42 items

tests/test_solution.py .......................................... [100%]

============================= 42 passed in 0.05s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Tôi dự đoán cao/thấp theo ý nghĩa ngôn ngữ trước khi chạy code. Điểm thực tế được tính bằng `MockEmbedder` và `compute_similarity`; trong bảng này quy ước cosine từ `0.5` trở lên là cao, dưới `0.5` là thấp.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên có thể điều chỉnh lớp học phần trong thời gian nào? | Thời hạn đổi lớp đã đăng ký dành cho sinh viên là khi nào? | Cao | 0.110591 — thấp | Không |
| 2 | Sinh viên được đăng ký tối đa bao nhiêu tín chỉ? | Thư viện mở cửa vào những ngày nào? | Thấp | -0.031167 — thấp | Có |
| 3 | Làm thế nào để hủy lớp học phần đã đăng ký? | Sinh viên cần làm gì khi muốn xóa một lớp khỏi kết quả đăng ký? | Cao | 0.094080 — thấp | Không |
| 4 | Khi nào hệ thống đăng ký học phần đóng? | Mức học phí phải đóng khi rút học phần là bao nhiêu? | Thấp | 0.065180 — thấp | Có |
| 5 | Sinh viên muốn đăng ký vào lớp đã đầy cần dùng biểu mẫu nào? | Mẫu đơn nào dành cho người học muốn vào một lớp không còn chỗ? | Cao | 0.070523 — thấp | Không |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Bất ngờ nhất là cặp 1, 3 và 5: con người nhận ra chúng là các cách diễn đạt gần như tương đương nhưng điểm mock đều thấp. Nguyên nhân là `MockEmbedder` tạo vector deterministic từ hash nội dung để kiểm thử pipeline, không được huấn luyện để biểu diễn ngữ nghĩa; vì vậy thay đổi cách dùng từ làm vector thay đổi gần như ngẫu nhiên. Kết quả này củng cố lý do benchmark chất lượng thực tế nên dùng multilingual semantic embedding khi môi trường cho phép.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân trong gói `src`; cấu hình và kết quả chính thức như sau.

- Strategy: `RecursiveChunker(chunk_size=400)`; `top_k=3`.
- Corpus chung: 6 tài liệu HUST, tạo thành 48 chunk.
- Backend: `MockEmbedder` deterministic. Việc cài `sentence-transformers`/PyTorch không hoàn tất trong giới hạn thời gian trên máy, vì vậy kết quả này dùng để kiểm chứng luồng kỹ thuật; mock không đại diện tốt cho ngữ nghĩa tiếng Việt.
- Benchmark đầy đủ, top-3 và A/B filter: `report/BENCHMARK_NGUYENTUANVU.md`.

| # | Câu hỏi (rút gọn) | Top-1 sau filter | Score | Đánh giá top-3 | Câu trả lời agent demo (tóm tắt) |
|---|---|---|---:|---|---|
| 1 | Ba đợt đăng ký lớp kỳ 2026.1 | `course-registration-03`, chunk 3 | 0.1337 | Đủ 4/4 evidence | Nêu các mốc đăng ký chính thức, điều chỉnh và đăng ký thêm lớp. |
| 2 | Các giai đoạn đăng ký học tập | `course-registration-07`, chunk 8 | 0.2887 | Chỉ 1/3 evidence, thiếu ngữ cảnh | Câu trích xuất lệch sang giới hạn tín chỉ và lớp thành phần. |
| 3 | Giới hạn tín chỉ theo quy chế | `course-registration-04`, chunk 0 | 0.2861 | 0/3 evidence | Context không chứa đủ các mức tín chỉ cần trả lời. |
| 4 | Rút học phần trong 7 tuần đầu | `course-registration-07`, chunk 7 | 0.2370 | Đủ 4/4 evidence | Trả đúng mức 50% học phí và ngoại lệ tuần đầu học kỳ hai. |
| 5 | SoICT: lớp đầy hoặc hủy lớp | `course-registration-08`, chunk 4 | 0.1579 | 0/3 evidence | Truy xuất đúng tài liệu nhưng sai section chứa biểu mẫu. |

**Tổng hợp:** 2/5 query có đủ toàn bộ evidence trong top-3; 3/5 query có ít nhất một evidence. Query 1 cho thấy metadata filter loại đúng tài liệu lịch kỳ 2025.2 và đưa lịch 2026.1 vào top-3. Failure rõ nhất là query 5: filter đưa đúng `doc_id` vào tập ứng viên nhưng mock embedding xếp sai chunk, chứng minh rằng đúng tài liệu chưa đồng nghĩa chunk chứa đáp án.

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | 5 / 5 |
| Hướng tiếp cận của tôi (My Approach) | 10 / 10 |
| Hoàn thiện code (Core Implementation — tests) | 30 / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5 / 5 |
| Kết quả truy xuất của tôi (Competition Results) | 5 / 10 |
| **Tổng phần cá nhân** | **55 / 60** |

Điểm retrieval tự đánh giá theo rubric mức chunk: Q1 = 2, Q2 = 1, Q3 = 0, Q4 = 2 và Q5 = 0. Tôi không cộng điểm chỉ vì đúng `doc_id` khi top-3 không chứa evidence trả lời được.
