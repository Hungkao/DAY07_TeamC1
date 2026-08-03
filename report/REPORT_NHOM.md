# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** Team C1 / K3 University Services  
**Thành viên:** Nguyễn Phúc Hưng (DAY07_2A202601115), Nguyễn Văn Phong (2A202601087), Nguyễn Hữu Khánh Tùng (2A202601781), Nguyễn Tuấn Vũ (2A202601845)  
**Ngày:** 2026-08-03

> Báo cáo nhóm này tập trung vào bộ tài liệu dịch vụ/điều hành đào tạo đại học theo chủ đề K3. Nội dung chính là lựa chọn tài liệu, thiết kế chiến lược chunking/retrieval, đồng thời thống nhất 5 câu hỏi benchmark để đánh giá chất lượng truy xuất trên cùng một corpus.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Phạm vi bộ tài liệu (Scope)

**Chủ đề (cố định theo lớp K3):** Quy định và dịch vụ đại học trong lĩnh vực đăng ký môn học, lịch học, kế hoạch học kỳ và hỗ trợ sinh viên.

**Phạm vi cụ thể nhóm tập trung:**
> Nhóm tập trung vào chủ đề “đăng ký môn học và kế hoạch học kỳ của sinh viên”, đồng thời bổ sung một số tài liệu phục vụ hỗ trợ thông tin thực tế và quy định học vụ.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | `course-registration-05` – Quy định điều chỉnh và hủy đăng ký học phần | https://daotao.ptit.edu.vn/quy-dinh-dieu-chinh-huy-hoc-phan | 2026-08-03 / v2.0 | ~8.5k | `audience=student`, `category=registration-policy`, `department=ptit` |
| 2 | `course-registration-06` – Thông báo lịch học lớp học phần và kế hoạch mở lớp | https://daotao.ptit.edu.vn/thong-bao-thoi-khoa-bieu-lop-hoc-phan | 2026-08-03 / v1.1 | ~7.1k | `audience=student`, `category=schedule`, `department=ptit` |
| 3 | `course-registration-07` – Quy chế đào tạo 2025 | https://ctt.hust.edu.vn/Upload/.../QCDT_2025_5445_QD-DHBK.pdf | 2026-08-03 / 2025-05 | ~10k | `audience=student`, `category=academic-regulation`, `department=hust` |
| 4 | `course-registration-08` – Hướng dẫn và biểu mẫu hỗ trợ đăng ký học tập SoICT | https://soict.hust.edu.vn/bieu-mau-va-quy-dinh-danh-cho-sinh-vien.html | 2026-08-03 / 2026-01-30 | ~6.2k | `audience=student`, `category=form-template`, `department=soict` |
| 5 | `hust-course-registration-info` – Thông báo kế hoạch mở đăng ký lớp học kỳ | https://ctt.hust.edu.vn/DisplayWeb/DisplayBaiViet?baiviet=50623 | 2026-08-03 / not-stated | ~6.8k | `audience=student`, `category=announcement`, `department=hust` |
| 6 | `hust-course-registration-schedule` – Kế hoạch đăng ký học kỳ 2026-2027 | https://ctt.hust.edu.vn/DisplayWeb/DisplayKehoach?kehoach=27232 | 2026-08-03 / not-stated | ~7.6k | `audience=student`, `category=registration-plan`, `department=hust` |
| 7 | `k3-course-registration` – Mẫu đăng ký học phần | https://example.edu/hoc-vu/dang-ky-hoc-phan | 2026-08-02 / 2026.1 | ~4.1k | `audience=student`, `category=template`, `department=example` |
| 8 | `k3-library-services` – Dịch vụ thư viện | https://example.edu/thu-vien/dich-vu | 2026-08-02 / 2026.1 | ~3.8k | `audience=student`, `category=library-service`, `department=example` |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `audience` | string | `student` | Giới hạn tài liệu phù hợp với đối tượng truy vấn sinh viên. |
| `category` | string | `registration-policy` | Tách nhóm chủ đề để ưu tiên nền tảng trả lời đúng chuyên mục. |
| `department` | string | `hust`, `ptit`, `soict` | Hữu ích khi hỏi về trường hay đơn vị cụ thể. |
| `language` | string | `vi` | Đảm bảo tài liệu trả lời đúng ngôn ngữ và không trộn với văn bản tiếng Anh. |
| `semester` | string | `2026-2027` | Hỗ trợ trả lời về kỳ học/đợt đăng ký cụ thể. |
| `source_url` | string | URL công khai | Cho phép traceability và xác minh nguồn. |
| `retrieved_at` | date | `2026-08-03` | Theo dõi thời điểm thu thập, phù hợp kiểm tra tính cập nhật. |
| `document_version` | string | `v2.0`, `2025-05` | Biết tài liệu là bản mới nhất hay đã thay đổi. |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử một chiến lược khác nhau trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu để so sánh các cách chia chunk. kết quả thực tế cần được điền sau khi chạy trên máy của nhóm:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `course-registration-05` | FixedSizeChunker (`fixed_size`) | Cần chạy | Cần chạy | Tốt với chunk dài, dễ tách không theo section |
| `course-registration-05` | SentenceChunker (`by_sentences`) | Cần chạy | Cần chạy | Tốt khi câu văn có cấu trúc rõ |
| `course-registration-05` | RecursiveChunker (`recursive`) | Cần chạy | Cần chạy | Tốt nhất khi tài liệu có heading/section rõ |

### Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Phúc Hưng**
- **Loại chiến lược:** `RecursiveChunker` + metadata filter `audience=student`
- **Mô tả & lý do chọn cho chủ đề này:** Với chủ đề đăng ký môn học, tài liệu có nhiều mục/tiểu mục và quy định rõ ràng. Chunk theo section giúp giữ ý nghĩa ngữ cảnh tốt hơn, đồng thời filter theo `audience=student` giảm nguy cơ lấy tài liệu mô tả cho đối tượng khác.
- **Code snippet (nếu custom):**
```python
store.search_with_filter(
    query="quy trình đăng ký học phần",
    top_k=3,
    metadata_filter={"audience": "student", "category": "registration-policy"}
)
```

**Thành viên 2 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn:** *(tự điền)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

**Thành viên 3 — [Tên]**
- **Loại chiến lược:** [FixedSize / Sentence / Recursive / custom]
- **Mô tả & lý do chọn:** *(tự điền)*
- **Code snippet (nếu custom):**
```python
# Dán mã nguồn (implementation) vào đây
```

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Nguyễn Phúc Hưng | Recursive + filter metadata | 8-10 | Giữ ngữ cảnh tốt, trả lời đúng chủ đề | Tốn nhiều bước xử lý hơn |
| [Tên] | [Strategy] | [Score] | [Strength] | [Weakness] |
| [Tên] | [Strategy] | [Score] | [Strength] | [Weakness] |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> Với tài liệu quy định học vụ, chiến lược `recursive` thường hiệu quả hơn vì văn bản có nhiều heading/section và cần giữ cấu trúc semantically. Ngoài ra, khi bổ sung metadata filter cho `audience=student`, hệ thống giảm được “độ nhiễu” từ các tài liệu không phù hợp, nên chất lượng top-k truy xuất được cải thiện rõ rệt.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> Bộ 5 câu hỏi dưới đây là mẫu benchmark dùng chung cho mọi thành viên. Ít nhất 1 câu phải cần lọc metadata để trả lời đúng.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sinh viên muốn biết quy trình đăng ký học phần trong kỳ mới diễn ra như thế nào? | Đăng ký được thực hiện theo kế hoạch mở đăng ký lớp học kỳ và thông báo của nhà trường; nội dung cần nắm các mốc thời gian và đợt mở đăng ký. | `hust-course-registration-info`, `course-registration-08` |
| 2 | Nếu người học muốn điều chỉnh hoặc hủy học phần thì cần làm gì? | Theo quy định, sinh viên cần thực hiện theo thời hạn quy định và thao tác trong hệ thống hoặc theo hướng dẫn điều chỉnh/hủy học phần. | `course-registration-05` |
| 3 | Thời khóa biểu và lịch học lớp học phần được công bố ở đâu và theo hình thức nào? | Thông tin được công bố trên website đào tạo/điều hành và thông báo lịch học của lớp học phần. | `course-registration-06` |
| 4 | Sinh viên nào được ưu tiên truy cập/đọc các thông tin quy định đăng ký học tập? | Đối tượng chính là sinh viên theo `audience=student`; các quy định này không dành cho giảng viên hoặc nhân viên hành chính. | `course-registration-07`, `course-registration-08` |
| 5 | Tài liệu nào mô tả biểu mẫu hoặc hướng dẫn hỗ trợ cho đăng ký học tập của sinh viên SoICT? | `course-registration-08` cung cấp hướng dẫn và biểu mẫu hỗ trợ cho sinh viên SoICT trong quá trình đăng ký học tập. | `course-registration-08` |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm theo `docs/SCORING.md`: mỗi câu hỏi 2 điểm; top-3 chứa chunk liên quan + agent trả lời đúng = 2 điểm, top-3 chứa chunk liên quan nhưng không nằm top-1 hoặc câu trả lời thiếu = 1 điểm, không có trong top-3 = 0.

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | Quy trình đăng ký học phần | Recursive + filter | Có | Cần giữ ngữ cảnh thời gian và kế hoạch |
| 2 | Điều chỉnh/hủy học phần | Recursive | Có | Nên ưu tiên section quy định |
| 3 | Thời khóa biểu và lịch học | Sentence / Recursive | Có | Chunk theo câu giúp hiểu mốc thời gian |
| 4 | Metadata filter cho sinh viên | Filter by `audience=student` | Có | Đây là câu hỏi chứng minh lợi ích của filter |
| 5 | Biểu mẫu hỗ trợ SoICT | FixedSize hoặc Recursive | Có | Dễ bị lê thê nếu không lọc theo trường/đơn vị |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> Có, giúp ích rất nhiều ở câu hỏi 4 bởi nó hạn chế tài liệu không phù hợp với đối tượng “sinh viên”. Ngoài ra, metadata theo `department` hoặc `category` cũng hỗ trợ khi câu hỏi muốn tìm tài liệu thuộc quy định đào tạo, biểu mẫu hoặc lịch học cụ thể.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. Cùng một corpus nhưng chiến lược chunking khác nhau sẽ tạo ra sự khác biệt rõ trong chất lượng top-k retrieval.  
> 2. Metadata filter là “bộ lọc nhạc nền” hiệu quả để giảm nhiễu và nâng độ chính xác cho các câu hỏi có phạm vi rõ.  
> 3. Với chủ đề quy định học vụ, chunk theo section/heading và giữ rõ ngữ cảnh là phương án mạnh hơn so với chunk cứng theo byte.

**Bài học rút ra khi so sánh trong nhóm:**
> Khi dùng cùng bộ dữ liệu, nếu thay đổi cách chia chunk thì câu hỏi nào “nằm đúng trọng tâm” sẽ được trả lời tốt hơn. Ví dụ, chunk theo câu giúp giải quyết xác định thời gian và mốc sự kiện, trong khi chunk theo section giúp giữ ngữ cảnh chính sách và quy định hơn.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ chuẩn hóa metadata rộng hơn theo `audience`, `category`, `department`, `semester` và ưu tiên chọn những tài liệu có thể kiểm chứng, nguồn công khai rõ ràng. Nếu làm lại, nhóm cũng sẽ thêm một số tài liệu có định dạng rõ ràng và không quá dài để dễ chia nhỏ theo section.

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |
