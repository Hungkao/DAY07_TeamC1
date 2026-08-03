## Benchmark c? nh?n - Nguy?n Ph?c H?ng

Ng?y: 2026-08-03

Backend: local sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

Chunker: RecursiveChunker(chunk_size=400)

### K?t qu? benchmark

#### C?u h?i 1
- Query: Sinh vi?n mu?n bi?t quy tr?nh ??ng k? h?c ph?n nh? th? n?o?
- Top-1 doc_id: hust-course-registration-schedule::chunk_0
- Top-1 score: 0.2189
- Top-3:
  - doc_id=hust-course-registration-schedule::chunk_0 score=0.2189 source=data\k3_university\hust-course-registration-schedule.md preview=# Kế hoạch đăng ký học kỳ 2026-2027
  - doc_id=hust-course-registration-info::chunk_0 score=0.2061 source=data\k3_university\hust-course-registration-info.md preview=# Thông báo kế hoạch mở đăng ký lớp học kỳ 1 năm học 2026-2027
  - doc_id=k3-course-registration::chunk_1 score=0.16 source=data\k3_university\course-registration.md preview=# Đăng ký học phần (dữ liệu khởi động)

#### C?u h?i 2
- Query: N?u mu?n ?i?u ch?nh ho?c h?y ??ng k? h?c ph?n, ph?i l?m g??
- Top-1 doc_id: hust-course-registration-schedule::chunk_0
- Top-1 score: 0.1501
- Top-3:
  - doc_id=hust-course-registration-schedule::chunk_0 score=0.1501 source=data\k3_university\hust-course-registration-schedule.md preview=# Kế hoạch đăng ký học kỳ 2026-2027
  - doc_id=hust-course-registration-info::chunk_0 score=0.1449 source=data\k3_university\hust-course-registration-info.md preview=# Thông báo kế hoạch mở đăng ký lớp học kỳ 1 năm học 2026-2027
  - doc_id=hust-course-registration-info::chunk_3 score=0.1431 source=data\k3_university\hust-course-registration-info.md preview=Mục tiêu của tài liệu này là hỗ trợ người đọc nhanh chóng xác định thời điểm và giai đoạn đăng ký trong năm học.

#### C?u h?i 3
- Query: Th?i kh?a bi?u l?p h?c ph?n ???c c?ng b? ? ??u?
- Top-1 doc_id: hust-course-registration-info::chunk_3
- Top-1 score: 0.1764
- Top-3:
  - doc_id=hust-course-registration-info::chunk_3 score=0.1764 source=data\k3_university\hust-course-registration-info.md preview=Mục tiêu của tài liệu này là hỗ trợ người đọc nhanh chóng xác định thời điểm và giai đoạn đăng ký trong năm học.
  - doc_id=hust-course-registration-schedule::chunk_0 score=0.1717 source=data\k3_university\hust-course-registration-schedule.md preview=# Kế hoạch đăng ký học kỳ 2026-2027
  - doc_id=hust-course-registration-info::chunk_2 score=0.1695 source=data\k3_university\hust-course-registration-info.md preview=Nội dung chính của thông báo tập trung vào: - kế hoạch mở đăng ký lớp - học kỳ liên quan - thời gian liên quan đến đăng 

#### C?u h?i 4
- Query: Th?ng tin bi?u m?u h? tr? ??ng k? h?c t?p thu?c ngu?n n?o?
- Top-1 doc_id: hust-course-registration-schedule::chunk_1
- Top-1 score: 0.1102
- Top-3:
  - doc_id=hust-course-registration-schedule::chunk_1 score=0.1102 source=data\k3_university\hust-course-registration-schedule.md preview=Tài liệu này mô tả kế hoạch đăng ký học tập của CTT HUST theo học kỳ và giai đoạn cụ thể. Nội dung phù hợp với chủ đề “đ
  - doc_id=hust-course-registration-info::chunk_2 score=0.0999 source=data\k3_university\hust-course-registration-info.md preview=Nội dung chính của thông báo tập trung vào: - kế hoạch mở đăng ký lớp - học kỳ liên quan - thời gian liên quan đến đăng 
  - doc_id=hust-course-registration-info::chunk_1 score=0.0952 source=data\k3_university\hust-course-registration-info.md preview=Trang thông tin của CTT HUST cung cấp thông báo về kế hoạch mở đăng ký lớp học kỳ 1 năm học 2026-2027. Đây là nội dung c

#### C?u h?i 5
- Query: Sinh vi?n c?n l?c theo metadata n?o ?? tr?nh l?y t?i li?u kh?ng ph? h?p?
- Top-1 doc_id: k3-course-registration::chunk_1
- Top-1 score: 0.4014
- Top-3:
  - doc_id=k3-course-registration::chunk_1 score=0.4014 source=data\k3_university\course-registration.md preview=# Đăng ký học phần (dữ liệu khởi động)
  - doc_id=k3-library-services::chunk_0 score=0.3953 source=data\k3_university\library-services.md preview=> Khối metadata phía trên là **template mẫu** cho K3 — thay `source_url`/`retrieved_at`/`document_version` bằng nguồn cô
  - doc_id=k3-course-registration::chunk_0 score=0.3869 source=data\k3_university\course-registration.md preview=> Khối metadata phía trên là **template mẫu** cho K3 (bắt buộc: `audience` + `source_url` + `retrieved_at` + `document_v

