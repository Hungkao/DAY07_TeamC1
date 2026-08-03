# Báo cáo benchmark CP6 — Nguyễn Phúc Hưng

> Bản benchmark ban đầu được push nhầm tại `report/NguyenPhucHung.md`, dùng corpus/query cũ nên không thể so sánh trực tiếp. Nhóm trưởng đã chuyển file vào đúng thư mục và chạy lại strategy đã phân công bằng cấu hình chuẩn hóa chung. Lịch sử Git vẫn lưu bản ban đầu để truy vết.

## Cấu hình chuẩn hóa

- Corpus: `data/k3_university/` — 6 tài liệu HUST.
- Strategy: heading/section, ngưỡng 400 ký tự; section dài dùng `RecursiveChunker(400)` và gắn lại heading.
- Embedding: `MockEmbedder` deterministic.
- Top-k: 3.
- Số chunk: 52.
- Script tái lập: `python scripts/compare_team_strategies.py`.

## Kết quả 5 query chung

| Query | Evidence không filter | Evidence có filter | Điểm mức chunk | Top-3 sau filter |
|---|---:|---:|---:|---|
| Q1 — Ba đợt đăng ký kỳ 2026.1 | 0/4 | 4/4 | 2/2 | `course-registration-03#1`, `#2`, `#0` |
| Q2 — Ba giai đoạn đăng ký | 2/3 | 2/3 | 1/2 | `course-registration-07#2`, `#3`; `course-registration-04#6` |
| Q3 — Giới hạn tín chỉ | 0/3 | 0/3 | 0/2 | `course-registration-07#10`, `#8`; `course-registration-04#4` |
| Q4 — Rút học phần và học phí | 0/4 | 0/4 | 0/2 | `course-registration-07#6`, `#5`, `#1` |
| Q5 — SoICT: lớp đầy/hủy lớp | 0/3 | 1/3 | 1/2 | `course-registration-08#4`, `#0`, `#7` |

**Tổng điểm retrieval mức chunk: 4/10.** Điểm được chấm từ evidence trong top-3: đủ evidence = 2, có một phần = 1, không có = 0.

## Nhận xét

Heading chunking giữ tiêu đề với nội dung nên hoạt động tốt nhất ở Q1: sau filter, top-3 chứa đủ bốn mốc thời gian. Q5 cũng được cải thiện từ 0 lên 1 evidence. Tuy nhiên Q4 là failure case: top-3 đều thuộc đúng tài liệu policy nhưng sai section, cho thấy đúng `doc_id` chưa đủ để kết luận truy xuất đúng.

Đề xuất cải thiện là dùng multilingual semantic embedding, tăng nhẹ `top_k`, và bổ sung tên mục vào query/metadata section để phân biệt các phần trong cùng một quy chế.
