# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Mai Văn Thuyên
- **Student ID**: 2A202600926
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

*Trong Lab này, tôi đã trực tiếp tham gia xây dựng và tối ưu hóa hệ thống Agentic:*

- **Modules Implementated**: 
    - `src/agent/agent.py`: Triển khai logic vòng lặp ReAct, xử lý tách `Thought-Action-Observation` bằng Regex và cơ chế thực thi tool.
    - `src/tools/tour_tools.py`: Xây dựng các hàm xử lý dữ liệu động (`search_attractions`, `check_weather_forecast`, `calculate_tour_budget`) đọc từ file JSON.
    - `app.py` & `tests/test_local.py`: Xây dựng API trung gian kết nối Agent với Frontend.
- **Code Highlights**:
    - Sử dụng `re.search` để ép buộc định dạng đầu ra của LLM: `Action: tool_name(args)`.
    - Thiết kế cấu trúc trả về dạng `Dict` gồm `final_answer`, `trace`, và `metrics` để frontend có thể render dữ liệu theo thời gian thực.
- **Documentation**: 
    - Hệ thống được thiết kế theo tư tưởng "Agent-as-a-Service", nơi Agent nhận yêu cầu qua `POST /ask-agent` và trả về kết quả JSON đã bao gồm log chi tiết của từng bước suy nghĩ (Trace).

---

## II. Debugging Case Study (10 Points)

*Phân tích các lỗi thực tế đã gặp trong quá trình phát triển:*

- **Problem Description**: Lỗi thực thi công cụ trả về kết quả sai địa điểm (Hà Nội nhưng trả về dữ liệu Đà Nẵng) và lỗi hệ thống `AttributeError: ReActAgent object has no attribute _execute_tool`.
- **Log Source**: Trích xuất từ Console: `Error executing search_spots: name 'json' is not defined` và `DEBUG: LLM không trả về 'Final Answer'`.
- **Diagnosis**: 
    - Lỗi `AttributeError` do sai lệch cấu trúc Class trong quá trình refactor code.
    - Lỗi `json not defined` do thiếu import thư viện chuẩn.
    - Lỗi sai địa điểm do hàm `search_attractions` sử dụng dữ liệu tĩnh (hard-coded) thay vì lọc theo tham số `city` từ `spots.json`.
- **Solution**: 
    - Đưa `_execute_tool` vào trong scope của class `ReActAgent`.
    - Bổ sung `import json` vào `tour_tools.py`.
    - Viết lại hàm `search_attractions` để filter dữ liệu động dựa trên `city` lấy từ Regex.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Đánh giá sự khác biệt về năng lực suy luận:*

1.  **Reasoning**: `Thought` block cho phép Agent có "khoảng lặng" để phân tích yêu cầu trước khi hành động. Khác với Chatbot truyền thống thường đoán câu trả lời ngay lập tức (dễ gây ra ảo giác - hallucination), Agent ReAct buộc phải lấy dữ liệu từ `Observation` trước khi kết luận.
2.  **Reliability**: Trong các trường hợp truy vấn thông tin thời gian thực (ví dụ: thời tiết, giá xe), Agent vượt trội nhờ dùng tool. Tuy nhiên, nếu prompt quá phức tạp, Agent dễ bị kẹt trong vòng lặp vô tận (infinite loop) nếu không được giới hạn `max_steps`.
3.  **Observation**: Feedback từ môi trường là yếu tố thay đổi kết quả. Nếu `Observation` trả về lỗi, Agent có khả năng "tự nhận thức" và thử lại với tham số khác, điều mà một Chatbot thông thường không làm được.

---

## IV. Future Improvements (5 Points)

*Định hướng phát triển hệ thống AI Agent:*

- **Scalability**: Sử dụng hệ thống Queue (như Celery/Redis) để xử lý các yêu cầu gọi tool tốn thời gian, tránh việc block API của Flask.
- **Safety**: Triển khai một "Guardrail" hoặc "Supervisor LLM" để kiểm tra tính hợp lệ của các `Action` do Agent tạo ra trước khi thực thi lệnh lên hệ thống thật.
- **Performance**: Nâng cấp cơ chế tìm kiếm Tool lên Vector Database (như ChromaDB) thay vì dùng file JSON để hỗ trợ hàng nghìn địa điểm mà không làm giảm tốc độ phản hồi.

---