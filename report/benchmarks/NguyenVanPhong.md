# Báo cáo CP5 — Nguyễn Văn Phong

**Corpus:** `data/k3_university/` (6 tài liệu HUST)  
**Ngày chạy:** 2026-08-03  
**Lệnh chạy:** `./.venv/Scripts/python.exe bench.py --embedding-provider local`

## Cấu hình cố định của nhóm

| Thành phần | Giá trị |
|---|---|
| Embedding backend | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` |
| Top-k | 3 |
| Số query | 5 |
| Số tài liệu | 6 |
| Số chunk đã nạp | 49 |

Model local đã tải và chạy thành công. Cảnh báo thiếu `HF_TOKEN` chỉ liên quan đến hạn mức/tốc độ tải từ Hugging Face, không làm thay đổi kết quả embedding sau khi model đã được tải.

## Strategy cá nhân: Sentence chunking

```python
SentenceChunker(max_sentences_per_chunk=3)
```

Strategy tách tại ranh giới câu và gộp tối đa ba câu trong mỗi chunk. Ưu điểm là không cắt giữa câu, nên một chunk giữ được ý nghĩa hoàn chỉnh hơn; nhược điểm là độ dài chunk không đồng đều và bằng chứng của một câu trả lời dài có thể nằm ở nhiều chunk.

## Kết quả benchmark A/B

`bench.py` chạy mỗi query hai lần: không filter và filter theo metadata chung. `Agent answer` trong output hiện là demo grounded-context, vì vậy cột điểm dưới đây là **điểm retrieval đề xuất** dựa trên bằng chứng xuất hiện trong top-3; cần có LLM thật hoặc kiểm tra thủ công trước khi chốt điểm agent cuối cùng.

| Query | Top-3 không filter | Top-3 có filter | Điểm retrieval đề xuất | Nhận xét |
|---|---|---|---:|---|
| Q1 — Lịch đăng ký kỳ 2026.1 | Top-3 là `hust-course-registration-info`/`schedule`, chưa có bằng chứng ngày của `course-registration-03`. | Không có kết quả. | 0/2 | Filter `semester="2026.1"` bị lệch kiểu dữ liệu metadata. |
| Q2 — Ba giai đoạn đăng ký | Có `course-registration-04` và `course-registration-07`; chunk 07 chứa “Đăng ký học phần”. | Không đổi thứ hạng; chỉ giữ 2 tài liệu policy. | 1/2 | Filter đúng phạm vi quy chế, nhưng các bằng chứng bị phân tán qua chunk. |
| Q3 — Giới hạn tín chỉ kỳ 2026.1 | Có bằng chứng một phần từ `hust-course-registration-info`, `course-registration-07` và 04. | Không có kết quả. | 0/2 | Cùng lỗi kiểu dữ liệu `semester` như Q1. |
| Q4 — Rút học phần và học phí | Top-1 là nhiễu `course-registration-03`; `course-registration-07` đứng thứ 3 và chứa 3 bằng chứng. | `course-registration-07` chunk 7 lên thứ 2. | 1/2 | Filter loại nhiễu lịch/kế hoạch, nhưng bằng chứng “không áp dụng kỳ hè” chưa nằm trong chunk top-3. |
| Q5 — Lớp đầy và hủy đăng ký | Top-3 đều là tài liệu lịch/kế hoạch, chưa có `course-registration-08`. | `course-registration-08` chunk 5 lên top-1. | 1/2 | Filter `registration_phase=add-drop` loại nhiễu hiệu quả; chunk top-1 chứa “Đơn xin đăng ký vào lớp đã đầy”. |

**Tổng điểm retrieval đề xuất:** **3/10** (chưa phải điểm agent chính thức).

## Nhận xét về metadata filter

Filter trước khi rank có lợi rõ ở Q4 và Q5: tài liệu không đúng giai đoạn/đối tượng bị loại trước khi tính similarity, nên chunk đúng tăng hạng. Q1 và Q3 lại cho tập rỗng vì parser front matter đọc `semester: 2026.1` thành kiểu `float`, còn benchmark filter bằng chuỗi `"2026.1"`.

Kiểm tra trực tiếp bằng `parse_front_matter()` cho thấy:

```text
course-registration-03.md  semester=2026.1  type=float
hust-course-registration-schedule.md  semester=2025.2  type=float
```

Trước CP6, nhóm nên thống nhất lưu học kỳ dưới dạng chuỗi YAML:

```yaml
semester: "2026.1"
```

Sau khi sửa schema chung, mọi thành viên phải chạy lại cả 5 query với cùng corpus và local embedder để giữ phép so sánh công bằng.

## Tái lập kết quả

```powershell
$env:PYTHONIOENCODING = "utf-8"
./.venv/Scripts/python.exe bench.py --embedding-provider local
```

File [bench.py](../bench.py) in ra strategy, tham số, top-3 unfiltered/filtered, score, `doc_id`, `chunk_index`, `source_url`, preview, evidence matched và demo agent context đầy đủ cho từng query.
