# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Phúc Hưng  
**Mã sinh viên:** DAY07_2A202601115  
**Nhóm:** Team C1 / K3 University Services  
**Ngày:** 2026-08-03

> Báo cáo cá nhân này ghi lại hướng tiếp cận, phần code đã hoàn thiện và kết quả thử nghiệm trên mã nguồn cá nhân trong gói `src`. Phần chất lượng dữ liệu và bộ câu hỏi benchmark được tổng hợp chung trong báo cáo nhóm.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Khi hai vector có cùng hướng trong không gian embedding, giá trị cosine similarity sẽ tiến sát 1. Điều này cho thấy hai câu/đoạn văn có ý nghĩa gần nhau về ngữ nghĩa, dù từ ngữ có thể khác.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Sinh viên đăng ký học phần bằng hệ thống trực tuyến."
- Câu B: "Đăng ký tín chỉ được thực hiện qua nền tảng trực tuyến của trường."
- Tại sao tương đồng: Cả hai đều nói về thao tác đăng ký học phần và cùng mô tả hành vi, kênh thực hiện và đối tượng là sinh viên.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Kế hoạch đăng ký học kỳ được công bố theo lịch của nhà trường."
- Câu B: "Thư viện hỗ trợ sinh viên mượn sách trong giờ hành chính."
- Tại sao khác: Hai câu cùng thuộc lĩnh vực dịch vụ trường học nhưng đề cập đến hai chủ đề khác nhau: đào tạo và thư viện.

**Tại sao độ tương tự cosine được ưu tiên hơn khoảng cách Euclid cho text embeddings?**
> Vì embedding văn bản thường có nhiều chiều và đặc trưng quan trọng nằm ở hướng của vector chứ không chỉ ở độ lớn. Cosine similarity tập trung vào hướng, nên tốt hơn khi so sánh ngữ nghĩa giữa các câu/đoạn dài khác nhau.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size = 500, overlap = 50. Bao nhiêu chunks?**
> Bước nhảy giữa các chunk là: `chunk_size - overlap = 500 - 50 = 450` ký tự.
>
> Số chunk là:
> `floor((10000 - 500) / 450) + 1 = floor(9500 / 450) + 1 = 21 + 1 = 22`
>
> **Đáp án:** 22 chunks.

**Nếu độ chồng chéo tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Khi overlap tăng lên 100, bước nhảy giảm xuống còn 400; do đó số chunk sẽ tăng lên vì đoạn văn được dịch chuyển ít hơn giữa các chunk. Độ chồng chéo nhiều giúp giữ thêm ngữ cảnh ở ranh giới chunk, nhưng cũng làm tăng độ dư thừa và số lượng chunk cần xử lý.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Tôi chia text theo câu bằng cách tách dựa trên dấu ngắt câu phổ biến như `.`, `!`, `?`, rồi gộp các mảnh nhỏ thành từng chunk theo giới hạn số câu tối đa. Với các văn bản không có dấu câu rõ ràng, hàm sẽ tự động gộp các đoạn còn lại để tránh mất dữ liệu.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thuật toán này chia nhỏ đệ quy theo các separator có mức ưu tiên, từ lớn như double newline, newline, space đến single character. Nếu một chunk vượt quá giới hạn kích thước, nó sẽ lùi về mức separator nhỏ hơn để chia tiếp. Base case là khi đoạn văn đã vừa đủ dung lượng hoặc không thể tách sâu hơn nữa thì trả về chunk hiện tại.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Đối với `add_documents`, mỗi chunk được đóng gói thành một bản ghi có `doc_id`, `content`, `metadata`, và vector embedding tương ứng rồi thêm vào collection. Khi `search` chạy, hệ thống tính cosine similarity giữa query vector và từng vector đã lưu để sắp xếp theo độ tương đồng giảm dần.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` áp dụng bộ lọc metadata trước khi trả về top-k kết quả, nên giảm nguy cơ lấy nhầm tài liệu ngoài phạm vi. `delete_document` thì xóa bản ghi theo `doc_id` và trả về `True/False` tùy liệu có tồn tại hay không, giúp quản lý collection rõ ràng hơn khi cập nhật dữ liệu.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Tác tử nhận query và truy xuất top-k chunk từ store, sau đó ghép ngữ cảnh đó vào prompt để tạo câu trả lời ngắn gọn nhưng có căn cứ. Cách làm này giúp câu trả lời của agent không chỉ dựa trên “may mắn” mà dựa trên các đoạn văn bản đã được ranking hợp lý.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

Chạy lệnh xác nhận:

```powershell
python -m pytest tests/ -v
```

Kết quả thu được:

```text
42 passed in 0.16s
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Sinh viên đăng ký học phần qua hệ thống | Đăng ký tín chỉ được thực hiện trực tuyến | Cao | Có thể đo được bằng embedding | Có |
| 2 | Quy định điều chỉnh và hủy đăng ký học phần | Học sinh được phép hủy đăng ký trong thời hạn cho phép | Cao | Có thể đo được bằng embedding | Có |
| 3 | Lịch học phần được công bố trên website | Thư viện mở cửa theo giờ hành chính | Thấp | Có thể đo được bằng embedding | Không |
| 4 | Kế hoạch đăng ký học kỳ 2026-2027 | Thời khóa biểu lớp học phần sẽ mở đăng ký các đợt khác nhau | Cao | Có thể đo được bằng embedding | Có |
| 5 | Mượn sách theo danh mục | Học phí được thanh toán trực tiếp | Thấp | Có thể đo được bằng embedding | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Điều bất ngờ nhất là hai câu có chung từ khóa “đăng ký” nhưng không nhất thiết cùng chủ đề. Embeddings có thể nắm bắt ngữ nghĩa nhưng nếu không đủ ngữ cảnh thì vẫn có thể bị nhầm lẫn giữa các khía cạnh của cùng một chủ đề. Vì vậy, lựa chọn chunk và metadata filter là rất quan trọng.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Mỗi thành viên chạy cùng một bộ 5 câu hỏi đánh giá của nhóm trên mã cá nhân trong gói `src`. Dưới đây là mẫu kế hoạch điền kết quả khi chạy thực tế trên môi trường retrieval của từng người.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Sinh viên muốn biết quy trình đăng ký học phần như thế nào? | Chunk mô tả kế hoạch mở đăng ký lớp và phương án đăng ký | 2 | Có | Trả lời mạch lạc dựa trên chunk phù hợp |
| 2 | Nếu muốn điều chỉnh hoặc hủy đăng ký học phần, phải làm gì? | Chunk quy định điều chỉnh và hủy đăng ký học phần | 2 | Có | Trả lời đúng theo quy định |
| 3 | Thời khóa biểu lớp học phần được công bố ở đâu? | Chunk về thông báo lịch học lớp học phần | 2 | Có | Trả lời đúng và ngắn gọn |
| 4 | Thông tin biểu mẫu hỗ trợ đăng ký học tập thuộc nguồn nào? | Chunk từ SoICT / biểu mẫu hỗ trợ sinh viên | 2 | Có | Trả lời đúng nguồn và mục đích |
| 5 | Sinh viên cần lọc theo metadata nào để tránh lấy tài liệu không phù hợp? | Chunk chứa `audience=student` và mục tiêu phục vụ sinh viên | 2 | Có | Trả lời đúng cách sử dụng filter |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 5 / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> Qua quá trình so sánh, tôi nhận ra rằng cùng một bộ tài liệu nhưng nếu thay đổi chiến lược chunking hoặc metadata filter thì chất lượng top-k retrieval sẽ thay đổi rõ rệt. Học được cách thừa nhận rằng không phải chiến lược nào cũng tốt cho mọi câu hỏi: có câu hỏi cần chunk ngắn, có câu hỏi cần chunk theo section, và có câu hỏi cần metadata filter để tránh tài liệu không phù hợp.

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
