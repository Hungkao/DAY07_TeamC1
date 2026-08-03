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
| Q1 — Lịch đăng ký kỳ 2026.1 | Top-3 là `hust-course-registration-info`/`schedule`, chưa có bằng chứng ngày của `course-registration-03`. | `course-registration-03` chunk 2 lên top-1 và chứa đủ 4 mốc thời gian. | 2/2 | Sau khi chuẩn hóa `semester` thành chuỗi, filter loại đúng nhiễu theo học kỳ. |
| Q2 — Ba giai đoạn đăng ký | Có `course-registration-04` và `course-registration-07`; chunk 07 chứa “Đăng ký học phần”. | Không đổi thứ hạng; chỉ giữ 2 tài liệu policy. | 1/2 | Filter đúng phạm vi quy chế, nhưng các bằng chứng bị phân tán qua chunk. |
| Q3 — Giới hạn tín chỉ kỳ 2026.1 | Có bằng chứng một phần từ `hust-course-registration-info`, `course-registration-07` và 04. | `course-registration-03` chunk 4 lên top-1, chứa các mức 12, 24 và 28 TC. | 1/2 | Filter nay hoạt động, nhưng các mức cảnh báo 08, 14, 18 chưa nằm trong chunk top-3. |
| Q4 — Rút học phần và học phí | Top-1 là nhiễu `course-registration-03`; `course-registration-07` đứng thứ 3 và chứa 3 bằng chứng. | `course-registration-07` chunk 7 lên thứ 2. | 1/2 | Filter loại nhiễu lịch/kế hoạch, nhưng bằng chứng “không áp dụng kỳ hè” chưa nằm trong chunk top-3. |
| Q5 — Lớp đầy và hủy đăng ký | Top-3 đều là tài liệu lịch/kế hoạch, chưa có `course-registration-08`. | `course-registration-08` chunk 5 lên top-1. | 1/2 | Filter `registration_phase=add-drop` loại nhiễu hiệu quả; chunk top-1 chứa “Đơn xin đăng ký vào lớp đã đầy”. |

**Tổng điểm retrieval đề xuất:** **6/10**

## Nhận xét về metadata filter

Filter trước khi rank có lợi rõ ở Q1, Q3, Q4 và Q5: tài liệu không đúng học kỳ, giai đoạn hoặc đối tượng bị loại trước khi tính similarity, nên chunk đúng tăng hạng. Sau khi chuẩn hóa kiểu dữ liệu `semester`, Q1 trả đúng chunk có đầy đủ bằng chứng ở top-1 và Q3 trả đúng tài liệu ở top-1.

Kiểm tra trực tiếp bằng `parse_front_matter()` cho thấy:

```text
course-registration-03.md  semester='2026.1'  type=str
hust-course-registration-schedule.md  semester='2025.2'  type=str
```

Metadata học kỳ đã được chuẩn hóa dưới dạng chuỗi YAML:

```yaml
semester: "2026.1"
```

Các thành viên khác cần chạy lại cả 5 query với cùng corpus và local embedder để giữ phép so sánh công bằng.

## Tái lập kết quả

```powershell
$env:PYTHONIOENCODING = "utf-8"
./.venv/Scripts/python.exe bench.py --embedding-provider local
```

File [bench.py](../bench.py) in ra strategy, tham số, top-3 unfiltered/filtered, score, `doc_id`, `chunk_index`, `source_url`, preview, evidence matched và demo agent context đầy đủ cho từng query.
