# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** C1
**Thành viên:** Nguyễn Văn Phong, Nguyễn Hữu Khánh Tùng, Nguyễn Phúc Hưng, Nguyễn Tuấn Vũ
**Ngày:** 2026-08-03

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Dịch vụ / quy định đại học (đăng ký môn, học phí, học bổng, thư viện, ký túc xá…).

**Phạm vi cụ thể nhóm tập trung:**
> Quy định, kế hoạch và hướng dẫn đăng ký học phần dành cho sinh viên Đại học Bách khoa Hà Nội, gồm đăng ký học phần/lớp, điều chỉnh, giới hạn tín chỉ, lịch mở hệ thống và kênh hỗ trợ.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Kế hoạch mở đăng ký lớp kỳ 2026.1 | [CTT HUST — kế hoạch 29240](https://ctt.hust.edu.vn/DisplayWeb/DisplayKehoach?kehoach=29240) | 2026-08-03 / 2026.1 | 2.135 | `student`, `2026.1`, `registration` |
| 2 | Quy chế đào tạo — quy định đăng ký học tập | [CTT HUST — Quy chế đào tạo 2025](https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n%20Qu%E1%BB%91c%20%C4%90%E1%BA%A1t/files/DTDH_QDQC/Hoctap/QCDT_2025_5445_QD-DHBK.pdf) | 2026-08-03 / 5445/QĐ-ĐHBK | 1.977 | `all`, `all`, `policy` |
| 3 | Quy chế đào tạo 2025 — tín chỉ, rút học phần và mở lớp | [CTT HUST — Quy chế đào tạo 2025](https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n%20Qu%E1%BB%91c%20%C4%90%E1%BA%A1t/files/DTDH_QDQC/Hoctap/QCDT_2025_5445_QD-DHBK.pdf) | 2026-08-03 / 2025-05 | 3.262 | `all`, `all`, `policy` |
| 4 | Hướng dẫn và biểu mẫu hỗ trợ đăng ký SoICT | [SoICT HUST — biểu mẫu sinh viên](https://soict.hust.edu.vn/bieu-mau-va-quy-dinh-danh-cho-sinh-vien.html) | 2026-08-03 / 2026-01-30 | 2.731 | `student`, `all`, `add-drop` |
| 5 | Đăng ký kế hoạch học tập kỳ hè 2025.3 và kỳ 2026.1 | [CTT HUST — kế hoạch 27235](https://ctt.hust.edu.vn/DisplayWeb/DisplayKehoach?kehoach=27235) | 2026-08-03 / `not-stated` | 1.850 | `student`, `2025.3-and-2026.1`, `registration` |
| 6 | Kế hoạch mở đăng ký lớp kỳ 2025.2 | [CTT HUST — kế hoạch 27232](https://ctt.hust.edu.vn/DisplayWeb/DisplayKehoach?kehoach=27232) | 2026-08-03 / 2025-12-25 | 2.244 | `student`, `2025.2`, `registration` |

Tài liệu số 2 và 3 cùng xuất phát từ Quy chế đào tạo 2025 nhưng được làm sạch theo hai phạm vi khác nhau: tài liệu số 2 tập trung quy trình đăng ký, còn tài liệu số 3 tập trung giới hạn tín chỉ, rút học phần, học phí và điều kiện mở lớp. Khi đánh giá retrieval, nhóm không tính hai file này là hai nguồn độc lập.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu chỉ chứa trang/PDF công khai thuộc hệ thống HUST; không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` hoặc ngày hiệu lực trong metadata và có một dòng tương ứng trong `sources.csv`.
- [x] Sáu file trong `data/k3_university/` có `doc_id` duy nhất, trùng tên file; template và tài liệu ngoài phạm vi được lưu riêng dưới `data/examples/` nên không được nạp vào benchmark.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `course-registration-03` | Định danh ổn định của tài liệu gốc; hỗ trợ truy vết và xóa mọi chunk của một tài liệu. |
| `title` | string | `Kế hoạch mở đăng ký lớp kỳ 2026.1` | Hiển thị nguồn dễ hiểu trong kết quả và báo cáo. |
| `audience` | enum | `student` | Giới hạn corpus cho đối tượng sinh viên theo schema thống nhất của nhóm. |
| `department` | string | `academic-affairs` | Xác định đơn vị nghiệp vụ phụ trách quy định. |
| `category` | enum/string | `course-registration` | Thu hẹp retrieval vào chủ đề đăng ký học phần. |
| `language` | enum | `vi` | Hỗ trợ chọn corpus và embedding phù hợp với tiếng Việt. |
| `source_url` | URL | `https://ctt.hust.edu.vn/...` | Cho phép kiểm chứng thông tin từ nguồn chính thức. |
| `retrieved_at` | date | `2026-08-03` | Cho biết thời điểm thu thập để đánh giá độ mới. |
| `document_version` | string | `2026.1`, `2025-12-25` | Phân biệt phiên bản hoặc thời điểm hiệu lực của tài liệu. |
| `semester` | string | `2025.2`, `2026.1`, `all` | Tránh trộn lịch đăng ký giữa các học kỳ. |
| `registration_phase` | enum | `registration`, `add-drop`, `policy` | Lọc theo giai đoạn đăng ký hoặc loại nội dung quy định. |

Corpus gồm bốn tài liệu hướng dẫn/kế hoạch có `audience: student` và hai văn bản quy chế có `audience: all`. Bộ lọc `audience` vì vậy có thể thu hẹp tập ứng viên theo đối tượng; nhóm cũng đánh giá giá trị metadata bằng A/B filter theo `semester` hoặc `registration_phase`.

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| | FixedSizeChunker (`fixed_size`) | | | |
| | SentenceChunker (`by_sentences`) | | | |
| | RecursiveChunker (`recursive`) | | | |

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn cho chủ đề này:** *(2-3 câu)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:*

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
