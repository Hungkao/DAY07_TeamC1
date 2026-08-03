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
python -m unittest tests.test_solution -q

----------------------------------------------------------------------
Ran 42 tests in 0.002s

OK
```

**Số lượng bài test vượt qua (pass):** 42 / 42

> Kết quả trên được chạy bằng `unittest` với interpreter hiện có. Trước khi nộp, sẽ chạy lại `python -m pytest tests -v` trong môi trường Python 3.11 và thay khối output bằng kết quả pytest chính thức.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | | | cao / thấp | | |
| 2 | | | cao / thấp | | |
| 3 | | | cao / thấp | | |
| 4 | | | cao / thấp | | |
| 5 | | | cao / thấp | | |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> *Viết 2-3 câu:*

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
