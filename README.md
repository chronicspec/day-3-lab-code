# 🌍 AI Travel Agent: Production-Grade ReAct System

Hệ thống **AI Travel Agent** là ứng dụng đại lý du lịch thông minh, sử dụng tư duy **ReAct (Reasoning + Acting)** để lập kế hoạch, dự báo thời tiết và tính toán ngân sách du lịch tự động.

## 🚀 Tính năng nổi bật
- **ReAct Framework**: Agent suy luận qua các bước `Thought -> Action -> Observation`.
- **Telemetry & Monitoring**: Tích hợp ghi log JSON và đo lường hiệu suất (Latency, Token usage) cho từng bước.
- **Web Interface**: Giao diện người dùng hiện đại với tính năng hiển thị tiến trình (Trace) theo thời gian thực (Accordion style).
- **Multi-Provider Support**: Dễ dàng chuyển đổi giữa Gemini, OpenAI và Local Model (thông qua `llama-cpp`).

## 🛠️ Hướng dẫn cài đặt & Vận hành

### 1. Yêu cầu hệ thống
- Python 3.10+
- `pip` (Trình quản lý gói)

### 2. Cấu hình môi trường
Tạo file cấu hình từ bản mẫu:
```bash
cp .env.example .env

Mở file .env và điền API Key của bạn:

GEMINI_API_KEY: API Key từ Google AI Studio.

DEFAULT_PROVIDER: Chọn google (cho Gemini) hoặc openai.

3. Cài đặt thư viện
Bash
pip install -r requirements.txt
4. Khởi chạy hệ thống
Để khởi động giao diện Web (Flask), chạy lệnh:

Bash
python app.py
Sau đó truy cập: http://localhost:5000

📁 Cấu trúc dự án
/src/agent/: Core logic thực thi vòng lặp ReActAgent.

/src/tools/: Các công cụ thực thi (search_attractions, check_weather, calculate_tour_budget).

/data/: Dữ liệu JSON mẫu (điểm tham quan, xe, thời tiết).

/logs/: Nhật ký hoạt động chi tiết (phục vụ đánh giá hiệu suất - Telemetry).

/templates/ & /static/: Giao diện Web (HTML/CSS).

📊 Đánh giá & Debugging
Hệ thống lưu vết mọi hành động của Agent vào thư mục /logs/. Các dữ liệu này được dùng để:

Phân tích lỗi (Failure Analysis): Truy vết các bước Agent suy luận sai.

Tối ưu hóa (Ablation Study): So sánh kết quả giữa các phiên bản Prompt.

Đánh giá hiệu năng: Tính toán Latency (độ trễ) và chi phí (Cost).