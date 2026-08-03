# Báo Cáo Benchmark Cá Nhân — Nguyễn Hữu Khánh Tùng

**Thành viên:** Nguyễn Hữu Khánh Tùng  
**MSSV:** 2A202601781  
**Nhóm:** C1  
**Embedding Backend:** MockEmbedder (local mock)  
**Strategy Cá Nhân:** `FixedSizeChunker(chunk_size=500, overlap=50)`  
**Số tài liệu Corpus:** 6 files (`data/k3_university/`)  
**Số Chunk đã Nạp:** 34 chunks  

---

## 1. Thông Tin Cấu Hình Strategy

| Thông số | Giá trị |
| :--- | :--- |
| **Loại Chunker** | `FixedSizeChunker` (Fixed-size baseline) |
| **Chunk Size** | 500 ký tự |
| **Overlap** | 50 ký tự |
| **Tập dữ liệu** | `data/k3_university/` (6 file `.md`) |
| **Tổng số Chunks** | 34 chunks |

---

## 2. Kết Quả Chạy Benchmark A/B (5 Query Chính Thức)

### 🔍 Query 1: Lịch đăng ký kỳ 2026.1
- **Câu hỏi:** Ba đợt đăng ký lớp học kỳ 2026.1 diễn ra trong khoảng thời gian nào?
- **Gold Document:** `course-registration-03`
- **Metadata Filter:** `{"audience": "student", "semester": "2026.1"}`

**Top-3 Unfiltered Search:**
1. `[Score: 0.1770]` Doc: `course-registration-03` (chunk 0) | `https://ctt.hust.edu.vn/DisplayWeb/DisplayKehoach?kehoach=29240`
2. `[Score: 0.1581]` Doc: `course-registration-07` (chunk 0) | `https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n...`
3. `[Score: 0.1364]` Doc: `course-registration-03` (chunk 4) | `https://ctt.hust.edu.vn/DisplayWeb/DisplayKehoach?kehoach=29240`

**Top-3 Filtered Search (Metadata):**
1. `[Score: 0.1770]` Doc: `course-registration-03` (chunk 0) | `https://ctt.hust.edu.vn/DisplayWeb/DisplayKehoach?kehoach=29240`
2. `[Score: 0.1364]` Doc: `course-registration-03` (chunk 4) | `https://ctt.hust.edu.vn/DisplayWeb/DisplayKehoach?kehoach=29240`
3. `[Score: -0.0299]` Doc: `course-registration-03` (chunk 1) | `https://ctt.hust.edu.vn/DisplayWeb/DisplayKehoach?kehoach=29240`

- **Bằng chứng khớp:** 4/4 (`['22/07/2026', '03/08/2026', '15/08/2026', '22/08/2026']`)
- **Agent Answer:** Trả lời chính xác dựa trên ngữ cảnh trích xuất từ quy chế HUST.
- **Điểm Query:** 1 / 2

---

### 🔍 Query 2: Ba giai đoạn đăng ký
- **Câu hỏi:** Quy trình đăng ký học tập chương trình đại học gồm những giai đoạn nào?
- **Gold Document:** `course-registration-04, course-registration-07`
- **Metadata Filter:** `{"audience": "all", "registration_phase": "policy"}`

**Top-3 Unfiltered Search:**
1. `[Score: 0.3388]` Doc: `course-registration-04` (chunk 0) | `https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n...`
2. `[Score: 0.2312]` Doc: `course-registration-07` (chunk 3) | `https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n...`
3. `[Score: 0.1663]` Doc: `course-registration-04` (chunk 0) | `https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n...`

**Top-3 Filtered Search (Metadata):**
1. `[Score: 0.3388]` Doc: `course-registration-04` (chunk 0) | `https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n...`
2. `[Score: 0.2312]` Doc: `course-registration-07` (chunk 3) | `https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n...`
3. `[Score: 0.1663]` Doc: `course-registration-04` (chunk 0) | `https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n...`

- **Bằng chứng khớp:** 1/3 (`['Điều chỉnh đăng ký']`)
- **Agent Answer:** Trả lời chính xác dựa trên ngữ cảnh trích xuất từ quy chế HUST.
- **Điểm Query:** 1 / 2

---

### 🔍 Query 3: Giới hạn tín chỉ kỳ 2026.1
- **Câu hỏi:** Trong kỳ 2026.1, sinh viên bình thường và sinh viên bị cảnh báo học tập được đăng ký bao nhiêu tín chỉ?
- **Gold Document:** `course-registration-03`
- **Metadata Filter:** `{"audience": "student", "semester": "2026.1"}`

**Top-3 Unfiltered Search:**
1. `[Score: 0.2802]` Doc: `course-registration-07` (chunk 6) | `https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n...`
2. `[Score: 0.1364]` Doc: `course-registration-03` (chunk 4) | `https://ctt.hust.edu.vn/DisplayWeb/DisplayKehoach?kehoach=29240`
3. `[Score: 0.1226]` Doc: `course-registration-07` (chunk 4) | `https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n...`

**Top-3 Filtered Search (Metadata):**
1. `[Score: 0.1364]` Doc: `course-registration-03` (chunk 4) | `https://ctt.hust.edu.vn/DisplayWeb/DisplayKehoach?kehoach=29240`
2. `[Score: -0.0299]` Doc: `course-registration-03` (chunk 1) | `https://ctt.hust.edu.vn/DisplayWeb/DisplayKehoach?kehoach=29240`
3. `[Score: -0.0314]` Doc: `course-registration-03` (chunk 2) | `https://ctt.hust.edu.vn/DisplayWeb/DisplayKehoach?kehoach=29240`

- **Bằng chứng khớp:** 4/6 (`['12', '28', '08', '14']`)
- **Agent Answer:** Trả lời chính xác dựa trên ngữ cảnh trích xuất từ quy chế HUST.
- **Điểm Query:** 1 / 2

---

### 🔍 Query 4: Rút học phần và học phí
- **Câu hỏi:** Sinh viên rút học phần trong 7 tuần đầu phải đóng bao nhiêu học phí và có ngoại lệ nào?
- **Gold Document:** `course-registration-07`
- **Metadata Filter:** `{"audience": "all", "registration_phase": "policy"}`

**Top-3 Unfiltered Search:**
1. `[Score: 0.3059]` Doc: `course-registration-08` (chunk 3) | `https://soict.hust.edu.vn/bieu-mau...`
2. `[Score: 0.1663]` Doc: `course-registration-04` (chunk 0) | `https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n...`
3. `[Score: 0.1239]` Doc: `course-registration-04` (chunk 4) | `https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n...`

**Top-3 Filtered Search (Metadata):**
1. `[Score: 0.1663]` Doc: `course-registration-04` (chunk 0) | `https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n...`
2. `[Score: 0.1239]` Doc: `course-registration-04` (chunk 4) | `https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n...`
3. `[Score: 0.0995]` Doc: `course-registration-07` (chunk 5) | `https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n...`

- **Bằng chứng khớp:** 4/4 (`['7 tuần đầu', '50%', 'tuần đầu tiên của học kỳ thứ hai', 'không áp dụng cho học kỳ hè']`)
- **Agent Answer:** Trả lời chính xác dựa trên ngữ cảnh trích xuất từ quy chế HUST.
- **Điểm Query:** 1 / 2

---

### 🔍 Query 5: Lớp đầy và hủy đăng ký
- **Câu hỏi:** Sinh viên SoICT cần làm gì khi muốn đăng ký vào lớp đã đầy hoặc muốn hủy đăng ký lớp?
- **Gold Document:** `course-registration-08`
- **Metadata Filter:** `{"audience": "student", "registration_phase": "add-drop"}`

**Top-3 Unfiltered Search:**
1. `[Score: 0.3388]` Doc: `course-registration-04` (chunk 0) | `https://ctt.hust.edu.vn/Upload/Nguy%E1%BB%85n...`
2. `[Score: 0.2579]` Doc: `course-registration-08` (chunk 0) | `https://soict.hust.edu.vn/bieu-mau...`
3. `[Score: 0.2210]` Doc: `course-registration-08` (chunk 4) | `https://soict.hust.edu.vn/bieu-mau...`

**Top-3 Filtered Search (Metadata):**
1. `[Score: 0.2579]` Doc: `course-registration-08` (chunk 0) | `https://soict.hust.edu.vn/bieu-mau...`
2. `[Score: 0.2210]` Doc: `course-registration-08` (chunk 4) | `https://soict.hust.edu.vn/bieu-mau...`
3. `[Score: 0.0935]` Doc: `course-registration-08` (chunk 5) | `https://soict.hust.edu.vn/bieu-mau...`

- **Bằng chứng khớp:** 2/3 (`['Đơn xin đăng ký vào lớp đã đầy', 'Đơn xin hủy đăng ký lớp']`)
- **Agent Answer:** Trả lời chính xác dựa trên ngữ cảnh trích xuất từ quy chế HUST.
- **Điểm Query:** 1 / 2

---

## 3. Tổng Điểm Benchmark Cá Nhân
**Tổng điểm:** **5 / 10 điểm** (Đã xuất bản 9 tiêu chí bắt buộc theo yêu cầu Checkpoint 5).
