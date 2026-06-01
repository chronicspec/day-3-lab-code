# Lab 3: Chatbot vs ReAct Agent (Industry Edition)

Chào mừng bạn đến với Giai đoạn 3 của khóa học **Agentic AI**! Bài thực hành này tập trung vào việc chuyển đổi từ một mô hình LLM Chatbot thông thường sang hệ thống cấu trúc **ReAct Agent** thông minh, đi kèm giải pháp giám sát và đo lường (Telemetry) theo tiêu chuẩn công nghiệp.

---

## 📂 Cấu trúc thư mục dự án

```text
.
├── src/
│   ├── agent/
│   │   └── agent.py          # Triển khai vòng lặp tư duy ReAct (Thought-Action-Observation)
│   ├── core/
│   │   ├── llm_provider.py   # Lớp giao tiếp cơ sở (Abstract Interface) cho các LLM Providers
│   │   └── gemini_provider.py# Bộ kết nối API Google Gemini (Cấu hình SDK tương thích hệ thống)
│   ├── tools/
│   │   └── tour_tools.py     # Nơi mở rộng và định nghĩa các công cụ tùy biến (Tools)
│   └── telemetry/
│       ├── logger.py         # Cấu hình ghi nhận nhật ký hệ thống (Structured JSON Logs)
│       └── metrics.py        # Module đo lường Token tiêu hao, Latency và Cost sinh ra
├── frontend/
│   ├── css/
│   │   └── style.css         # Tùy biến giao diện tối tối giản và thanh cuộn mượt mà
│   ├── js/
│   │   └── app.js            # Điều phối tương tác API, xử lý chuyển Tab và render giao diện
│   └── index.html            # Khung xương HTML chính tích hợp Prompt Suggestion Cards
├── .env                      # File lưu trữ biến môi trường và API Keys bảo mật
├── main_api.py               # Điểm khởi chạy FastAPI Backend Endpoint
└── requirements.txt          # Danh sách gói thư viện phụ thuộc của dự án

🚀 Hướng dẫn Cài đặt & Khởi chạy nhanh
1. Cấu hình biến môi trường
Sao chép tệp mẫu cấu hình sang file .env chính thức và bổ sung khóa API của bạn:
cp .env.example .env

Nội dung file .env cần đảm bảo:
GEMINI_API_KEY=Điền_Khóa_Gemini_API_Của_Bạn
DEFAULT_PROVIDER=google
DEFAULT_MODEL=gemini-2.5-flash

2. Cài đặt các thư viện phụ thuộc
Cài đặt toàn bộ danh sách thư viện được chỉ định trong dự án:
pip install -r requirements.txt

3. Khởi chạy FastAPI Server
Để khởi chạy ứng dụng web API đúng tiêu chuẩn ASGI của Uvicorn, thực hiện lệnh sau tại thư mục gốc để tránh lỗi định dạng cấu hình ứng dụng:
uvicorn main_api:app --reload --host 127.0.0.1 --port 8000

4. Mở giao diện tương tác (Frontend)
Truy cập vào thư mục frontend/, kích hoạt file index.html (Mở trực tiếp trên trình duyệt hoặc sử dụng Extension Live Server trên VS Code tại cổng 5500).

🎯 Mục tiêu bài Lab & Các tính năng cốt lõi
Baseline Chatbot: Kiểm tra và đánh giá các giới hạn cố hữu của mô hình LLM thuần túy khi giải quyết các bài toán nghiệp vụ phức tạp, cần tính toán logic nhiều bước.

ReAct Loop Pipeline: Hoàn thiện vòng lặp lập luận tự động Thought -> Action -> Observation bên trong cấu phần src/agent/agent.py.

DeepSeek-Style UI: Chuỗi suy nghĩ trung gian được thu gọn gọn gàng trong khối "Process Thinking" trực quan giúp tối ưu hóa không gian hiển thị và tăng tính thẩm mỹ cho giao diện.

ChatGPT Prompt Suggestions: Hệ thống thẻ mẫu gợi ý hành động nhanh ở trung tâm màn hình, hỗ trợ người dùng kích hoạt luồng tác tử tự động (Tour Planning, Weather Forecast, Budgeting) chỉ với 1-Click.

Giám sát Telemetry & Chấm điểm Lab: Tích hợp Tab giám sát trực quan để theo dõi định lượng số lượng Token, Chi phí (Cost), Độ trễ phản hồi (Latency) ngay trên UI. Dữ liệu này giúp trích xuất trực tiếp số liệu vào báo cáo cá nhân TEMPLATE_INDIVIDUAL_REPORT.md.

🛠️ Xử lý sự cố hệ thống (Troubleshooting)
Trong quá trình triển khai dự án thực tế, bạn có thể đối mặt với một số lỗi hệ thống đặc thù. Dưới đây là giải pháp xử lý triệt để căn cứ theo mã nhật ký log hệ thống:

Lỗi 1: Error loading ASGI app. Import string "main_api.py" must be in format "<module>:<attribute>"
Dấu hiệu: Xuất hiện khi cố gắng chạy server thông qua lệnh trực tiếp python main_api.py mà file chưa bọc khối thực thi của uvicorn, hoặc truyền sai tham số định dạng tệp tin cho trình điều phối ASGI.

Giải pháp: Sử dụng cú pháp lệnh tiêu chuẩn của Uvicorn, chỉ định rõ tên tệp (main_api) kết hợp với biến đại diện ứng dụng FastAPI (app):
uvicorn main_api:app --reload

Lỗi 2: GeminiProvider.generate() got an unexpected keyword argument 'current_prompt'
Dấu hiệu: Mô hình LLM báo lỗi sập luồng ReAct (AGENT_STEP_START) ngay vòng lập luận đầu tiên do việc gọi sai tên tham số tùy biến đặt tên biến tự do (current_prompt=...) không khớp với tài liệu quy định của Google SDK.

Giải pháp: Truy cập vào file src/core/gemini_provider.py tại dòng gọi hàm tạo nội dung, điều chỉnh tham số truyền vào về dạng tham số nội dung chuẩn contents theo quy định chính thức từ thư viện:
# Cấu trúc sửa đổi chính xác:
response = self.client.models.generate_content(model=self.model_name, contents=prompt)