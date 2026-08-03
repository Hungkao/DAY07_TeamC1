# Kết quả benchmark CP5 — Nguyễn Tuấn Vũ

- Corpus: `data/k3_university` (6 tài liệu)
- Strategy cá nhân: `RecursiveChunker(chunk_size=400)`
- Embedding backend: `mock embeddings fallback`
- Số chunk đã nạp: **48**
- Top-k: **3**
- Agent demo: extractive, deterministic, chỉ chọn câu từ context; không dùng API và không đọc gold answer.

> Gold answer chỉ dùng để đối chiếu thủ công. Chỉ số tự động bên dưới đo evidence trong top-3 ở mức chunk, không tự nhận là điểm đúng/sai cuối cùng.

## Query 1

**Câu hỏi:** Ba đợt đăng ký lớp học kỳ 2026.1 diễn ra trong khoảng thời gian nào?

**Filter:** `{'audience': 'student', 'semester': '2026.1'}`

**Gold answer:** Đăng ký chính thức từ 22/07 đến 03/08/2026; đăng ký điều chỉnh từ 03/08 đến 15/08/2026; đăng ký thêm vào các lớp đang mở từ 15/08 đến 22/08/2026.

**Gold document:** `course-registration-03`

### A — Không filter

1. score=0.2821; doc_id=`hust-course-registration-schedule`; chunk=0; preview: # Kế hoạch mở đăng ký lớp học kỳ 2 năm học 2025-2026 Nguồn là thông báo ngày 25/12/2025 của Ban Đào tạo, Đại học Bách khoa Hà Nội, áp dụng cho sinh viên từ khóa K69 trở về trước đăng ký lớp học kỳ 2 năm học 2025-2026 (kỳ
2. score=0.2567; doc_id=`course-registration-04`; chunk=2; preview: 2. **Đăng ký lớp chính thức:** sinh viên chọn lớp cho các học phần đã đăng ký. Học phần có nhiều thành phần như lý thuyết, bài tập, thực hành hoặc thí nghiệm phải được đăng ký đủ các lớp thành phần theo yêu cầu.
3. score=0.2380; doc_id=`hust-course-registration-schedule`; chunk=3; preview: Hệ thống bảo trì hằng ngày từ 00h00 đến 02h00; sinh viên không truy cập trang đăng ký trong thời gian này. Sau khi kết thúc đăng ký chính thức và điều chỉnh, sinh viên không được thay đổi các môn đã đăng ký. ## Các mốc v

Evidence hit: **0/4**; gold doc trong top-3: **không**.

### B — Có metadata filter

1. score=0.1337; doc_id=`course-registration-03`; chunk=3; preview: - Hệ thống đóng đăng ký trực tuyến ngày 22/08/2026; toàn bộ công tác đăng ký kết thúc ngày 28/08/2026.
2. score=0.0727; doc_id=`course-registration-03`; chunk=2; preview: - Đăng ký chính thức: từ 16:00 ngày 22/07/2026 đến 14:00 ngày 03/08/2026. - Đăng ký điều chỉnh: từ 16:00 ngày 03/08/2026 đến 14:00 ngày 15/08/2026; áp dụng cho toàn bộ sinh viên, bao gồm người chưa đăng ký học phần. - Đă
3. score=0.0647; doc_id=`course-registration-03`; chunk=0; preview: # Kế hoạch đăng ký lớp học kỳ 2026.1 Thông báo áp dụng cho sinh viên các khóa K70 trở về trước. Sinh viên đăng ký lớp trực tuyến tại `https://qldt.hust.edu.vn/students` bằng địa chỉ email Office 365 do Đại học cấp và mật

Evidence hit: **4/4** (22/07/2026, 03/08/2026, 15/08/2026, 22/08/2026); gold doc trong top-3: **có**.

**Câu trả lời agent demo:** # Kế hoạch đăng ký lớp học kỳ 2026.1 [3] Đăng ký điều chỉnh: từ 16:00 ngày 03/08/2026 đến 14:00 ngày 15/08/2026; áp dụng cho toàn bộ sinh viên, bao gồm người chưa đăng ký học phần. [2] Đăng ký thêm vào các lớp đang mở: từ 16:00 ngày 15/08/2026 đến 16:00 ngày 22/08/2026 cho sinh viên K70 trở về trước. [2]

## Query 2

**Câu hỏi:** Quy trình đăng ký học tập chương trình đại học gồm những giai đoạn nào?

**Filter:** `{'audience': 'all', 'registration_phase': 'policy'}`

**Gold answer:** Quy trình gồm đăng ký học phần theo kế hoạch học tập, đăng ký lớp chính thức và điều chỉnh đăng ký trong thời hạn quy định.

**Gold document:** `course-registration-04`, `course-registration-07`

### A — Không filter

1. score=0.3480; doc_id=`hust-course-registration-info`; chunk=3; preview: Thời gian đăng ký học phần bắt đầu lúc 10h00 ngày 16/03/2026 và kết thúc lúc 16h00 ngày 27/04/2026. Khối lượng đăng ký thông thường từ 12 đến 24 tín chỉ. Sinh viên bị cảnh báo học tập mức 2 hoặc mức 3 được đăng ký tối đa
2. score=0.2887; doc_id=`course-registration-07`; chunk=8; preview: Lớp học phần có giờ lên lớp thông thường chỉ được mở khi có ít nhất 20 sinh viên đăng ký. Một số ngoại lệ được xem xét:
3. score=0.2709; doc_id=`course-registration-08`; chunk=4; preview: Trước ngày kết thúc đăng ký, sinh viên cần kiểm tra các học phần có thành phần thí nghiệm hoặc thực hành. Kết quả đăng ký phải có đủ lớp lý thuyết/bài tập và lớp thí nghiệm/thực hành theo yêu cầu của học phần. ## Xử lý v

Evidence hit: **1/3**; gold doc trong top-3: **có**.

### B — Có metadata filter

1. score=0.2887; doc_id=`course-registration-07`; chunk=8; preview: Lớp học phần có giờ lên lớp thông thường chỉ được mở khi có ít nhất 20 sinh viên đăng ký. Một số ngoại lệ được xem xét:
2. score=0.1871; doc_id=`course-registration-04`; chunk=4; preview: ## Khối lượng tín chỉ và điều kiện mở lớp Trong học kỳ chính, sinh viên không thuộc diện cảnh báo học tập đăng ký tối thiểu 12 và tối đa 24 tín chỉ; sinh viên năm cuối không áp dụng ngưỡng tối thiểu. Học kỳ hè được đăng 
3. score=0.1570; doc_id=`course-registration-07`; chunk=3; preview: 2. Đăng ký lớp chính thức: sinh viên chọn lớp cho các học phần đã đăng ký. Nếu học phần có nhiều lớp thành phần như lý thuyết, bài tập, thực hành hoặc thí nghiệm, sinh viên phải đăng ký đủ các thành phần được yêu cầu.

Evidence hit: **1/3** (Đăng ký lớp chính thức); gold doc trong top-3: **có**.

**Câu trả lời agent demo:** Sinh viên bị cảnh báo học tập bị giới hạn khối lượng đăng ký theo quy chế. [2] Trong học kỳ chính, sinh viên không thuộc diện cảnh báo học tập đăng ký tối thiểu 12 và tối đa 24 tín chỉ; sinh viên năm cuối không áp dụng ngưỡng tối thiểu. [2] Nếu học phần có nhiều lớp thành phần như lý thuyết, bài tập, thực hành hoặc thí nghiệm, sinh viên phải đăng ký đủ các thành phần được yêu cầu. [3]

## Query 3

**Câu hỏi:** Theo quy chế, sinh viên bình thường và sinh viên bị cảnh báo học tập được đăng ký bao nhiêu tín chỉ trong học kỳ chính?

**Filter:** `{'audience': 'all', 'registration_phase': 'policy'}`

**Gold answer:** Sinh viên bình thường đăng ký từ 12 đến 24 tín chỉ. Sinh viên bị cảnh báo đăng ký từ 8 đến 14 tín chỉ ở chương trình chuẩn, hoặc từ 8 đến 18 tín chỉ ở chương trình ELITECH/hợp tác quốc tế.

**Gold document:** `course-registration-07`

### A — Không filter

1. score=0.3318; doc_id=`course-registration-08`; chunk=6; preview: - Đơn xin mở lớp bổ sung dành cho cá nhân. - Đơn xin mở lớp bổ sung dành cho tập thể. - Đơn xin đăng ký vào lớp đã đầy. - Quy trình xác nhận học phần thay thế hoặc tương đương. - Mẫu đơn đăng ký học phần tương đương hoặc
2. score=0.2861; doc_id=`course-registration-04`; chunk=0; preview: # Quy định về đăng ký học tập chương trình đại học Đăng ký học tập là quy trình bắt buộc trong mỗi học kỳ, trừ sinh viên mới nhập học đã được xếp thời khóa biểu theo kế hoạch học tập chuẩn; các sinh viên này vẫn có thể t
3. score=0.2577; doc_id=`course-registration-07`; chunk=8; preview: Lớp học phần có giờ lên lớp thông thường chỉ được mở khi có ít nhất 20 sinh viên đăng ký. Một số ngoại lệ được xem xét:

Evidence hit: **0/3**; gold doc trong top-3: **có**.

### B — Có metadata filter

1. score=0.2861; doc_id=`course-registration-04`; chunk=0; preview: # Quy định về đăng ký học tập chương trình đại học Đăng ký học tập là quy trình bắt buộc trong mỗi học kỳ, trừ sinh viên mới nhập học đã được xếp thời khóa biểu theo kế hoạch học tập chuẩn; các sinh viên này vẫn có thể t
2. score=0.2577; doc_id=`course-registration-07`; chunk=8; preview: Lớp học phần có giờ lên lớp thông thường chỉ được mở khi có ít nhất 20 sinh viên đăng ký. Một số ngoại lệ được xem xét:
3. score=0.2464; doc_id=`course-registration-04`; chunk=5; preview: Với học phần có giờ lên lớp, lớp chỉ được mở khi có tối thiểu 20 sinh viên đăng ký. Có thể xem xét mở lớp có từ 5 đến 19 sinh viên theo đề nghị của sinh viên và áp dụng hệ số học phí theo quy định. Lớp dưới 5 sinh viên c

Evidence hit: **0/3** (không có); gold doc trong top-3: **có**.

**Câu trả lời agent demo:** Đăng ký học tập là quy trình bắt buộc trong mỗi học kỳ, trừ sinh viên mới nhập học đã được xếp thời khóa biểu theo kế hoạch học tập chuẩn; các sinh viên này vẫn có thể tự điều chỉnh một số lớp. [1] Lớp học phần có giờ lên lớp thông thường chỉ được mở khi có ít nhất 20 sinh viên đăng ký. [2] Lớp dưới 5 sinh viên có thể được xem xét cho người học lại học phần dưới hình thức đồ án môn học khi đáp ứng điều kiện trong quy chế. [3]

## Query 4

**Câu hỏi:** Sinh viên rút học phần trong 7 tuần đầu phải đóng bao nhiêu học phí và có ngoại lệ nào?

**Filter:** `{'audience': 'all', 'registration_phase': 'policy'}`

**Gold answer:** Trong 7 tuần đầu, sinh viên phải đóng 50% học phí; quy định có ngoại lệ ở tuần đầu tiên của học kỳ thứ hai và không áp dụng cho học kỳ hè.

**Gold document:** `course-registration-07`

### A — Không filter

1. score=0.2370; doc_id=`course-registration-07`; chunk=7; preview: Đối với chương trình cử nhân và kỹ sư, nếu đề nghị rút trong 7 tuần đầu học kỳ và được chấp thuận, sinh viên phải đóng 50% học phí của học phần đã rút. Ngoại lệ là đề nghị rút trong tuần đầu tiên của học kỳ thứ hai: nếu 
2. score=0.2353; doc_id=`course-registration-07`; chunk=1; preview: Đăng ký học tập là quy trình bắt buộc trong mỗi học kỳ đối với sinh viên đại học. Sinh viên mới nhập học được xếp thời khóa biểu theo kế hoạch học tập chuẩn nên không phải tự đăng ký, nhưng có thể điều chỉnh một số lớp. 
3. score=0.1988; doc_id=`course-registration-07`; chunk=0; preview: # Quy định đăng ký học tập chương trình đại học Nguồn là Quy chế đào tạo của Đại học Bách khoa Hà Nội, bản ghi tháng 05/2025. Nội dung dưới đây được làm sạch và giới hạn ở các quy định liên quan trực tiếp đến đăng ký học

Evidence hit: **4/4**; gold doc trong top-3: **có**.

### B — Có metadata filter

1. score=0.2370; doc_id=`course-registration-07`; chunk=7; preview: Đối với chương trình cử nhân và kỹ sư, nếu đề nghị rút trong 7 tuần đầu học kỳ và được chấp thuận, sinh viên phải đóng 50% học phí của học phần đã rút. Ngoại lệ là đề nghị rút trong tuần đầu tiên của học kỳ thứ hai: nếu 
2. score=0.2353; doc_id=`course-registration-07`; chunk=1; preview: Đăng ký học tập là quy trình bắt buộc trong mỗi học kỳ đối với sinh viên đại học. Sinh viên mới nhập học được xếp thời khóa biểu theo kế hoạch học tập chuẩn nên không phải tự đăng ký, nhưng có thể điều chỉnh một số lớp. 
3. score=0.1988; doc_id=`course-registration-07`; chunk=0; preview: # Quy định đăng ký học tập chương trình đại học Nguồn là Quy chế đào tạo của Đại học Bách khoa Hà Nội, bản ghi tháng 05/2025. Nội dung dưới đây được làm sạch và giới hạn ở các quy định liên quan trực tiếp đến đăng ký học

Evidence hit: **4/4** (7 tuần đầu, 50%, tuần đầu tiên của học kỳ thứ hai, không áp dụng cho học kỳ hè); gold doc trong top-3: **có**.

**Câu trả lời agent demo:** Đối với chương trình cử nhân và kỹ sư, nếu đề nghị rút trong 7 tuần đầu học kỳ và được chấp thuận, sinh viên phải đóng 50% học phí của học phần đã rút. [1] Ngoại lệ là đề nghị rút trong tuần đầu tiên của học kỳ thứ hai: nếu được giải quyết theo nguyện vọng thì không phải đóng học phí cho học phần đó. [1] Đăng ký học tập là quy trình bắt buộc trong mỗi học kỳ đối với sinh viên đại học. [2]

## Query 5

**Câu hỏi:** Sinh viên SoICT cần làm gì khi muốn đăng ký vào lớp đã đầy hoặc muốn hủy đăng ký lớp?

**Filter:** `{'audience': 'student', 'registration_phase': 'add-drop'}`

**Gold answer:** Sinh viên dùng đúng Đơn xin đăng ký vào lớp đã đầy hoặc Đơn xin hủy đăng ký lớp và gửi tới đơn vị quản lý học phần để được xem xét.

**Gold document:** `course-registration-08`

### A — Không filter

1. score=0.3879; doc_id=`course-registration-07`; chunk=1; preview: Đăng ký học tập là quy trình bắt buộc trong mỗi học kỳ đối với sinh viên đại học. Sinh viên mới nhập học được xếp thời khóa biểu theo kế hoạch học tập chuẩn nên không phải tự đăng ký, nhưng có thể điều chỉnh một số lớp. 
2. score=0.2376; doc_id=`hust-course-registration-schedule`; chunk=3; preview: Hệ thống bảo trì hằng ngày từ 00h00 đến 02h00; sinh viên không truy cập trang đăng ký trong thời gian này. Sau khi kết thúc đăng ký chính thức và điều chỉnh, sinh viên không được thay đổi các môn đã đăng ký. ## Các mốc v
3. score=0.2242; doc_id=`hust-course-registration-info`; chunk=0; preview: # Đăng ký kế hoạch học tập kỳ hè 2025-2026 và kỳ 1 năm học 2026-2027 Nguồn là thông báo chính thức của Ban Đào tạo, Đại học Bách khoa Hà Nội về việc đăng ký mã học phần dự định học cho kỳ hè 2025.3 và kỳ 1 năm học 2026-2

Evidence hit: **0/3**; gold doc trong top-3: **không**.

### B — Có metadata filter

1. score=0.1579; doc_id=`course-registration-08`; chunk=4; preview: Trước ngày kết thúc đăng ký, sinh viên cần kiểm tra các học phần có thành phần thí nghiệm hoặc thực hành. Kết quả đăng ký phải có đủ lớp lý thuyết/bài tập và lớp thí nghiệm/thực hành theo yêu cầu của học phần. ## Xử lý v
2. score=0.1569; doc_id=`course-registration-08`; chunk=8; preview: Trang hỗ trợ dẫn sinh viên tới Sổ tay sinh viên chung của Đại học Bách khoa Hà Nội, trang hướng dẫn thủ tục và thắc mắc về học tập, học phí, cùng Quy chế đào tạo đại học 2025. Khi thông tin giữa hướng dẫn đơn vị và quy đ
3. score=0.1530; doc_id=`course-registration-08`; chunk=0; preview: # Hướng dẫn và biểu mẫu hỗ trợ đăng ký học tập Nguồn là trang Biểu mẫu và quy định dành cho sinh viên của Trường Công nghệ Thông tin và Truyền thông, Đại học Bách khoa Hà Nội, cập nhật lần cuối ngày 30/01/2026. Các hướng

Evidence hit: **0/3** (không có); gold doc trong top-3: **có**.

**Câu trả lời agent demo:** Trước ngày kết thúc đăng ký, sinh viên cần kiểm tra các học phần có thành phần thí nghiệm hoặc thực hành. [1] Các hướng dẫn có phạm vi trực tiếp cho sinh viên SoICT; sinh viên thuộc đơn vị khác cần liên hệ trường, viện hoặc khoa quản lý học phần tương ứng. [3] Kết quả đăng ký phải có đủ lớp lý thuyết/bài tập và lớp thí nghiệm/thực hành theo yêu cầu của học phần. [1]

## Tổng kết CP5

- Query có đủ toàn bộ evidence trong top-3 sau filter: **2/5**.
- Kết quả A/B được giữ nguyên để sang CP6 phân tích precision, recall và failure case.
