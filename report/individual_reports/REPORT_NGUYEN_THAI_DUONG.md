# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Thái Dương
- **Student ID**: 2A202600547
- **Date**: 01/06/2026

---

1. Báo cáo Nhóm: So sánh Chatbot vs Agent 
Giảng viên muốn thấy một sự so sánh dựa trên dữ liệu thực tế (Data-driven comparison). Hãy trình bày phần này theo cấu trúc 3 bước:

Bước 1 - Đặt bối cảnh (Test Case): Đưa ra một câu hỏi phức tạp đa bước.

Ví dụ: "Tìm cho tôi tour đi Sapa rẻ nhất và tính tổng tiền nếu tôi đi 2 người kèm 10% thuế VAT."

Bước 2 - Lập bảng so sánh: Tạo một bảng trong file Markdown để làm nổi bật sự khác biệt:

Tiêu chí	Baseline Chatbot	ReAct Agent v1
Cách xử lý	Cố gắng trả lời ngay lập tức bằng dữ liệu cũ.	Phân tích yêu cầu, nhận ra cần tìm giá tour và máy tính.
Hành động	Không có (Không gọi Tool).	Gọi Search_Tour("Sapa") -> Gọi Calculator(price * 2 * 1.1).
Kết quả	Bịa ra một mức giá không có thật (Ảo giác) hoặc từ chối trả lời.	Trả về tổng chi phí chính xác dựa trên dữ liệu thực tế.
Bước 3 - Kết luận (Insight): Viết một đoạn ngắn tóm tắt rằng Chatbot chỉ giỏi "nói chuyện" dựa trên xác suất từ ngữ, trong khi Agent có khả năng "hành động" (Acting) và lập kế hoạch (Reasoning) để bù đắp các lỗ hổng kiến thức của chính nó.

2. Báo cáo Cá nhân: Case Study Phân tích lỗi (10 Điểm)
Đây là phần quan trọng nhất để chứng minh bạn thực sự hiểu hệ thống. Đừng giấu giếm lỗi, hãy trình bày một ca "thất bại" theo format sau:

Triệu chứng (The Bug): Kể lại lúc Agent bị sập hoặc kẹt. Ví dụ: "Trong quá trình chạy thử nghiệm, Agent rơi vào vòng lặp vô hạn (Infinite Loop) và liên tục gọi công cụ Check_Weather mà không bao giờ đưa ra câu trả lời cuối cùng."

Bằng chứng từ Log (The Trace): Trích xuất một đoạn JSON ngắn từ thư mục logs/ minh chứng cho lỗi này (ví dụ đoạn log cho thấy Thought bị lặp lại 5 lần).

Chẩn đoán nguyên nhân: Giải thích lý do (ví dụ: Do hàm Check_Weather trả về một chuỗi rỗng khiến LLM bị bối rối không biết làm gì tiếp theo).

Cách giải quyết (The Fix): Trình bày cách bạn sửa code hoặc system prompt. (Ví dụ: Thêm điều kiện vào hàm Python để nếu không có dữ liệu, trả về chuỗi "Không tìm thấy thông tin thời tiết", đồng thời cấu hình max_steps=5 để ép Agent dừng lại).

3. Báo cáo Cá nhân: Hướng cải tiến tương lai (5 Điểm)
Để lấy trọn vẹn điểm cho tầm nhìn kiến trúc hệ thống, bạn hãy đề xuất một giải pháp triển khai thực tế cấp độ doanh nghiệp cho tác vụ tư vấn tour này:

Kiến trúc Local RAG (Bảo mật & Tốc độ): Đề xuất nâng cấp công cụ tìm kiếm tour hiện tại thành một hệ thống Retrieval-Augmented Generation (RAG) chạy hoàn toàn nội bộ. Thay vì phụ thuộc vào API LLM bên ngoài, mô hình suy luận có thể được vận hành thông qua Ollama.

Vector Database: Dữ liệu hàng ngàn tour du lịch, chính sách giá và lịch trình sẽ được chuyển hóa thành vector và lưu trữ bằng ChromaDB để Agent có thể truy xuất ngữ nghĩa cực kỳ chính xác.

Microservices backend: Toàn bộ vòng lặp ReAct và các công cụ sẽ được đóng gói thành các API endpoint sử dụng FastAPI, giúp dễ dàng tích hợp độc lập với bất kỳ giao diện frontend nào trong tương lai.

