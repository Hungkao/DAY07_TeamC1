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

Nhóm giữ cố định 6 tài liệu, 5 query, `top_k=3`, metadata filter và `MockEmbedder`; biến duy nhất là chunker. Các file cá nhân được giữ trong `report/benchmarks/`. Do một số lượt chạy cá nhân trước đó dùng backend hoặc phiên bản corpus khác nhau, bảng so sánh chính thức được nhóm trưởng chạy lại bằng `scripts/compare_team_strategies.py` để bảo đảm công bằng.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare(chunk_size=400)` trên ba tài liệu đầu, sau khi bỏ front matter:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `course-registration-03` | Fixed size | 6 | 355,8 | Có thể cắt giữa câu/mốc thời gian |
| `course-registration-03` | Sentence | 10 | 211,6 | Giữ nguyên câu, evidence dễ bị phân tán |
| `course-registration-03` | Recursive | 7 | 303,3 | Ưu tiên đoạn/dòng, khá mạch lạc |
| `course-registration-04` | Fixed size | 5 | 395,4 | Chunk đều nhưng ranh giới cơ học |
| `course-registration-04` | Sentence | 10 | 196,1 | Câu trọn vẹn, chunk ngắn |
| `course-registration-04` | Recursive | 5 | 393,8 | Giữ tốt các mục quy định |
| `course-registration-07` | Fixed size | 9 | 362,4 | Có nguy cơ tách điều kiện và ngoại lệ |
| `course-registration-07` | Sentence | 16 | 201,9 | Nhiều chunk, tăng cạnh tranh trong top-k |
| `course-registration-07` | Recursive | 9 | 360,7 | Cân bằng kích thước và ranh giới tự nhiên |

### Chiến lược của từng thành viên

- **Nguyễn Hữu Khánh Tùng — `FixedSizeChunker(500, overlap=50)`:** baseline dễ tái lập; overlap cho thông tin ở biên thêm một cơ hội xuất hiện nhưng tạo dữ liệu trùng lặp.
- **Nguyễn Tuấn Vũ — `RecursiveChunker(chunk_size=400)`:** ưu tiên đoạn, dòng, câu rồi từ; phù hợp văn bản quy định có đoạn ngắn nhưng không bảo đảm giữ heading ở mọi mảnh con.
- **Nguyễn Văn Phong — `SentenceChunker(max_sentences_per_chunk=3)`:** không cắt giữa câu, phù hợp câu quy định trọn ý; đổi lại kích thước không đều và số chunk tăng.
- **Nguyễn Phúc Hưng — heading 400 + recursive fallback:** tách theo heading Markdown; section dài mới recursive và gắn heading lại vào mảnh con. Đây là strategy khai thác cấu trúc domain của tài liệu quy định.

Logic chính của heading chunker:

```python
sections = re.split(r"(?m)(?=^#{1,6}\\s+)", text)
for section in sections:
    if len(section) <= 400:
        chunks.append(section)
    else:
        # recursive split phần thân và gắn lại heading cho từng mảnh
        chunks.extend(split_long_section_with_heading(section))
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Nguyễn Hữu Khánh Tùng | Fixed 500, overlap 50 — 33 chunks | 5 | Q4 và Q5 đủ evidence; ít chunk | Q1/Q3 sai section; có trùng lặp do overlap |
| Nguyễn Tuấn Vũ | Recursive 400 — 43 chunks | 2 | Q4 giữ điều kiện và ngoại lệ cùng chunk | Mock embedding xếp sai section ở Q1/Q2/Q3/Q5 |
| Nguyễn Văn Phong | Sentence 3 — 49 chunks | **6** | Tốt nhất ở Q1, Q5; câu không bị cắt | Evidence dài bị phân tán, Q3 thất bại |
| Nguyễn Phúc Hưng | Heading 400 + recursive — 52 chunks | 4 | Q1 đủ evidence, giữ tiêu đề | Nhiều chunk cùng tài liệu cạnh tranh top-k; Q4 sai section |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Trong lượt chuẩn hóa bằng mock embedding, SentenceChunker của Phong đạt cao nhất (6/10) vì các câu chứa mốc thời gian và tên biểu mẫu được giữ nguyên. Tuy nhiên không có strategy thắng mọi query: Fixed size tốt ở ngoại lệ/học phí, Heading tốt ở lịch có cấu trúc mục, còn Recursive cho chunk cân bằng. Khi triển khai thật, nhóm ưu tiên heading + recursive fallback cho văn bản quy định và dùng multilingual embedding; kết quả mock chỉ là bằng chứng kỹ thuật, không phải kết luận ngữ nghĩa cuối cùng.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Ba đợt đăng ký lớp học kỳ 2026.1 diễn ra trong khoảng thời gian nào? | Chính thức 22/07–03/08/2026; điều chỉnh 03/08–15/08/2026; đăng ký thêm lớp đang mở 15/08–22/08/2026. | `course-registration-03`, phần “Các giai đoạn và mốc thời gian” |
| 2 | Quy trình đăng ký học tập chương trình đại học gồm những giai đoạn nào? | Đăng ký học phần; đăng ký lớp chính thức; điều chỉnh đăng ký. | `course-registration-04` hoặc `07`, phần quy trình |
| 3 | Theo quy chế, sinh viên bình thường và sinh viên bị cảnh báo học tập được đăng ký bao nhiêu tín chỉ trong học kỳ chính? | Bình thường 12–24; cảnh báo: chương trình chuẩn 8–14, ELITECH/hợp tác quốc tế 8–18 tín chỉ. | `course-registration-07`, phần khối lượng tín chỉ |
| 4 | Sinh viên rút học phần trong 7 tuần đầu phải đóng bao nhiêu học phí và có ngoại lệ nào? | Đóng 50%; ngoại lệ đề nghị trong tuần đầu học kỳ hai, và quy định không áp dụng cho học kỳ hè. | `course-registration-07`, phần rút học phần |
| 5 | Sinh viên SoICT cần làm gì khi muốn đăng ký vào lớp đã đầy hoặc muốn hủy đăng ký lớp? | Dùng đúng đơn đăng ký lớp đầy/đơn hủy lớp và gửi đơn vị quản lý học phần để xét duyệt. | `course-registration-08`, phần biểu mẫu |

Gold answer được cố định trước lượt so sánh chuẩn hóa. Q1 bắt buộc filter `{"audience":"student","semester":"2026.1"}`; Q2–Q4 lọc policy; Q5 lọc `student + add-drop`.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Lịch 2026.1 | Sentence / Heading | Có, đủ 4/4 evidence | Filter loại lịch kỳ khác; hai strategy đạt 2/2 |
| 2 | Ba giai đoạn | Fixed / Sentence / Heading | Có một phần | Tối đa 2/3 evidence; các giai đoạn bị phân tán |
| 3 | Giới hạn tín chỉ | Chưa có strategy đạt | Không | Đúng tài liệu có thể xuất hiện nhưng top-3 sai section; 0/3 evidence |
| 4 | Rút học phần | Fixed / Recursive | Có, đủ 4/4 evidence | Điều kiện 7 tuần, 50% và ngoại lệ nằm cùng ngữ cảnh |
| 5 | Biểu mẫu SoICT | Fixed / Sentence | Có, đủ 3/3 evidence | Filter add-drop loại toàn bộ tài liệu policy/lịch |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có. Q1 cho thấy rõ nhất: với Heading, không filter có 0/4 evidence nhưng filter `semester="2026.1"` đưa đúng ba chunk của `course-registration-03` vào top-3 và đạt 4/4. Q5 với Sentence tăng từ 0/3 lên 3/3 nhờ `registration_phase="add-drop"`. Đánh đổi là filter phụ thuộc metadata đúng kiểu, vì vậy nhóm đã đặt `semester` trong dấu nháy để PyYAML luôn đọc là string.

### A/B filter và failure analysis

**A/B điển hình — Q1, HeadingChunker:**

- Không filter: 0/4 evidence; các lịch/chính sách khác cạnh tranh thứ hạng.
- Có filter: `course-registration-03#1`, `#2`, `#0`; đủ 4/4 mốc ngày.
- Kết luận: filter tăng precision bằng cách thu hẹp đúng học kỳ trước khi rank.

**Failure case — Q3:** cả bốn strategy đều 0/3 evidence dù một số top-3 thuộc đúng `course-registration-04/07`. Query đúng chủ đề nhưng mock embedding xếp các section chung về đăng ký/mở lớp cao hơn section chứa 12–24, 8–14 và 8–18 tín chỉ. Nguyên nhân không phải thiếu tài liệu mà là sai chunk trong cùng tài liệu. Đề xuất: multilingual embedding, heading metadata (`section_title`), hybrid keyword + vector và kiểm thử `top_k=5`.

**Failure case phụ — Q4 của Heading:** top-3 đều là policy nhưng không có evidence; heading giúp coherence nhưng không tự giải quyết ranking. Đây là minh chứng score cao hoặc đúng `doc_id` chưa phải bằng chứng câu trả lời đúng.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
1. Metadata filter phải chạy trước ranking; Q1 và Q5 cho thấy evidence tăng rõ rệt sau lọc.
2. Đánh giá phải ở mức chunk/evidence, không chỉ `doc_id`: Q3 và Q4 Heading đều lấy đúng tài liệu nhưng sai section.
3. Chunker phù hợp phụ thuộc cấu trúc câu hỏi: Sentence thắng tổng điểm mock, còn Heading giữ cấu trúc tốt cho lịch/mục quy định.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng corpus và query nhưng số chunk biến thiên từ 33 đến 52, làm thay đổi số ứng viên và khả năng evidence lọt top-3. Chunk lớn giữ được điều kiện/ngoại lệ nhưng có thể loãng chủ đề; chunk nhỏ giữ câu hoặc heading tốt hơn nhưng evidence dài dễ bị chia ra nhiều mảnh cạnh tranh nhau.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ chuẩn hóa toàn bộ metadata thành string có schema validation, thêm `section_title` lên mỗi chunk và loại nội dung trùng giữa hai bản trích cùng quy chế. Sau checkpoint code, nhóm sẽ dùng một multilingual embedding duy nhất cho cả bốn người, cache model trước giờ lab và chạy benchmark bằng một manifest query chung để tránh lệch cấu hình.

### Kịch bản demo 6–8 phút

| Thời lượng | Người trình bày | Nội dung |
|---|---|---|
| 1 phút | Nguyễn Tuấn Vũ | Phạm vi corpus, provenance và metadata schema |
| 2 phút | Tùng, Phong, Hưng, Vũ | Mỗi người giới thiệu ngắn strategy và số chunk |
| 3 phút | Nguyễn Tuấn Vũ | Bảng so sánh, A/B Q1/Q5 và failure Q3 |
| 1–2 phút | Nguyễn Văn Phong | Chạy `python scripts/compare_team_strategies.py` hoặc trình bày output đã chuẩn bị |

Khi hỏi đáp, nhóm giải thích được filter tăng precision nhưng có thể giảm recall, heading strategy dễ tái dùng cho domain có cấu trúc mục, và mock embedding chỉ kiểm tra pipeline chứ không đo đầy đủ ngữ nghĩa tiếng Việt.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 6 / 10 |
| Thuyết trình (Demo) | 4 / 5 |
| **Tổng phần nhóm** | **35 / 40** |

Điểm tự đánh giá retrieval lấy theo strategy tốt nhất trong lượt chuẩn hóa và được giữ ở mức 6/10 thay vì suy diễn từ `doc_id`. Điểm demo chỉ tự đánh giá 4/5 cho đến khi nhóm hoàn thành phần trình bày trực tiếp.
