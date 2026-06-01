# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Nguyễn Thái Dương
- **Student ID**: 2A202600547
- **Date**: 01/06/2026

---

## I. Technical Contribution (15 Points)

*Describe your specific contribution to the codebase (e.g., implemented a specific tool, fixed the parser, etc.).*

- **Modules Implementated**: [src/agent/agent.py (Cơ chế lõi điều phối ReAct Loop) và bổ sung hoàn thiện hệ thống telemetry tính toán chi phí, token thực tế tại src/telemetry/metrics.py]
- **Code Highlights**:[Triển khai vòng lặp điều hướng suy nghĩ cốt lõi dựa trên mô hình ReAct Framework, bắt gói tin hành động gọi Tools qua biểu thức chính quy (Regex) và làm sạch định dạng Markdown nhiễu:
"""
while steps < self.max_steps:
    steps += 1
    # Gọi LLM sinh phản hồi dựa trên chuỗi ngữ cảnh tích lũy
    result = self.llm.generate(prompt=current_context, system_prompt=self.get_system_prompt())
    llm_output = result.get("content", "").strip()

    # Ghi nhận Telemetry (Tokens, Latency, Cost) tự động
    tracker.track_request(
        provider=result.get("provider", "google"),
        model=self.llm.model_name,
        usage=result.get("usage", {}),
        latency_ms=result.get("latency_ms", 0)
    )

    current_context += f"\n{llm_output}"

    # Làm sạch Markdown nhiễu (Chống lỗi cú pháp bọc ```json)
    llm_output_cleaned = re.sub(r"```[a-zA-Z]*\n?", "", llm_output).replace("```", "").strip()

    # Kịch bản 1: Nhận diện kết quả cuối cùng (Final Answer)
    final_match = re.search(r"Final Answer:\s*(.*)", llm_output_cleaned, re.DOTALL | re.IGNORECASE)
    if final_match:
        return final_match.group(1).strip()

    # Kịch bản 2: Bóc tách hành động gọi công cụ 'Action: tool_name(args)'
    action_match = re.search(r"Action:\s*(\w+)\((.*)\)", llm_output_cleaned, re.IGNORECASE)
    if action_match:
        tool_name = action_match.group(1).strip()
        tool_args = action_match.group(2).strip()
        observation = self._execute_tool(tool_name, tool_args)
        current_context += f"\nObservation: {observation}"
"""]
- **Documentation**: [Đoạn mã trên thiết lập một chu kỳ khép kín: Thought -> Action -> Observation. Hệ thống không trả lời ngay lập tức mà bắt buộc LLM suy nghĩ lý do chọn công cụ thông qua system_prompt. Khi phát hiện chuỗi ký tự hành động Action:, mã nguồn lập tức can thiệp, dừng tiến trình sinh văn bản của LLM, trích xuất tên hàm và tham số, thực thi logic Python tương ứng trong bộ công cụ tour_tools.py, và đẩy dữ liệu kết quả thực tế (Observation) trở ngược lại ngữ cảnh đầu vào để LLM đánh giá cho bước kế tiếp.]

---

## II. Debugging Case Study (10 Points)

*Analyze a specific failure event you encountered during the lab using the logging system.*

- **Problem Description**: [Khi khởi chạy Agent V2 với yêu cầu lập lịch trình du lịch từ người dùng: "Tôi muốn thiết kế 1 chuyến du lịch đến Trùng Khánh - Trung Quốc", Agent lập tức bị sập (Crash) ngay bước đầu tiên và quăng ra lỗi hệ thống: ❌ Lỗi: GeminiProvider.generate() got an unexpected keyword argument 'current_prompt'.]
- **Log Source**: [Link or snippet from `logs/2026-06-01.log`]
    """
    {"timestamp": "2026-06-01T08:43:04.023811", "event": "AGENT_START", "data": {"input": "Tôi muốn thiết kế 1 chuyến du lịch đến Trùng Khánh-Trung Quốc", "model": "gemini-2.5-flash"}}
    {"timestamp": "2026-06-01T08:43:04.023811", "event": "AGENT_STEP_START", "data": {"step": 1}}
    """
- **Diagnosis**: [Qua việc đối chiếu cấu trúc, hàm khởi tạo của GeminiProvider.generate() (cũng như OpenAIProvider và LocalProvider) được định nghĩa tham số tiếp nhận chuỗi ký tự đầu vào là prompt (def generate(self, prompt: str, ...):). Tuy nhiên, trong mã nguồn lớp điều phối ReActAgent cũ, dòng mã gọi LLM lại truyền theo kiểu tường minh từ khóa (keyword argument) sai lệch là current_prompt=current_context. Do Python kiểm soát chặt chẽ tham số truyền vào hàm, việc truyền sai tên từ khóa khiến trình thông dịch báo lỗi bất đồng bộ chữ ký hàm (signature mismatch) và ngắt kết nối hệ thống.]
- **Solution**: [Tiến hành tái cấu trúc lại lời gọi hàm trong file agent.py, đồng bộ hóa chính xác tên tham số từ khóa từ current_prompt thành prompt để tương thích hoàn toàn với tất cả các lớp Provider. Đồng thời bổ sung bọc khối try-except xung quanh tiến trình thực thi công cụ để đảm bảo hệ thống không bị đổ vỡ dây chuyền nếu LLM sinh mã lỗi định dạng hoặc sinh ra tên công cụ giả lập (Hallucination).]

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

*Reflect on the reasoning capability difference.*

1.  **Reasoning**: Khối lập luận Thought đóng vai trò như một "vùng đệm nhận thức" cực kỳ quan trọng cho mô hình ngôn ngữ lớn. Thay vì ép LLM phải đưa ra câu trả lời ngay lập tức bằng trực giác từ trọng số (dễ dẫn đến hiện tượng bịa đặt thông tin - Hallucination khi tính toán chi phí tour hoặc ngày giờ), khối Thought cho phép mô hình bẻ nhỏ bài toán phức tạp thành các bài toán con. Mô hình tự lên kế hoạch trước khi hành động: "Tôi cần biết thời tiết tại Trùng Khánh trước, sau đó mới tính tiền xe phù hợp", giúp độ chính xác của kết quả cuối cùng tăng lên vượt trội so với câu trả lời dạng Chatbot truyền thống.
2.  **Reliability**: Qua thực tế kiểm thử định lượng, hệ thống Agent hoạt động kém hiệu quả và tốn kém hơn Chatbot trong các kịch bản trả lời câu hỏi thông tin đóng hoặc hội thoại ngắn đơn giản (ví dụ: "Thủ đô của Trung Quốc là gì?"). Trong trường hợp đó, Chatbot xử lý chỉ mất đúng 1 request duy nhất với độ trễ cực thấp (dưới 500ms). Ngược lại, Agent do bị ràng buộc bởi cấu trúc ReAct vẫn phải trải qua bước suy nghĩ, phân tích, tiêu tốn lượng token hệ thống lớn cho phần system_prompt dẫn đến tăng chi phí (Cost) và thời gian phản hồi (Latency) không cần thiết.
3.  **Observation**: Các phản hồi từ môi trường thông qua các hàm Python thực thi đóng vai trò là "mỏ neo thực tế" định hướng cho LLM. Khi công cụ trả về dữ liệu nằm ngoài dự tính (ví dụ: công cụ báo lỗi hoặc trả về chuỗi rỗng do không tìm thấy chuyến bay), LLM sẽ nhìn vào Observation đó để tự sửa sai trong bước Thought tiếp theo (ví dụ: chuyển sang tìm kiếm phương tiện tàu hỏa thay thế thay vì bị kẹt lại). Đây là điều mà một Chatbot thông thường không bao giờ làm được vì nó thiếu vòng lặp phản hồi chủ động từ thế giới thực.

---

## IV. Future Improvements (5 Points)

*How would you scale this for a production-level AI agent system?*

- **Scalability**: Chuyển đổi cơ chế gọi công cụ từ tuần tự đồng bộ (Synchronous) sang mô hình hàng đợi bất đồng bộ (Asynchronous Task Queue sử dụng Celery kết hợp Redis). Điều này giúp hệ thống xử lý song song nhiều tác vụ gọi API bên ngoài (như check giá vé máy bay thời gian thực từ nhiều hãng) mà không làm nghẽn luồng suy nghĩ lõi của Agent.
- **Safety**: Thiết kế một lớp Agent giám sát (Supervisor Agent hoặc Llama Guard) độc lập để kiểm toán (Audit) toàn bộ chuỗi Action do Agent đề xuất trước khi thực thi. Rào chắn này giúp ngăn chặn triệt để các rủi ro bảo mật nguy hiểm như Prompt Injection (người dùng cố tình lừa Agent thực hiện lệnh xóa DB hoặc gọi API phá hoại tài nguyên hệ thống).
- **Performance**: Khi hệ thống mở rộng lên hàng trăm công cụ khác nhau (tìm khách sạn, đặt nhà hàng, mua vé khu vui chơi...), việc nhét toàn bộ mô tả công cụ vào system_prompt sẽ gây bùng nổ token đầu vào và làm loãng khả năng chú ý của LLM. Giải pháp là ứng dụng Cơ sở dữ liệu vectơ (Vector DB như ChromaDB hoặc Native pgvector trên Postgres) để lưu trữ các tài liệu đặc tả công cụ. Khi có yêu cầu từ người dùng, hệ thống chỉ truy vấn ngữ nghĩa để lấy ra top 3-5 công cụ phù hợp nhất rồi nạp động vào prompt, giúp tiết kiệm tối đa chi phí Token và giảm thiểu độ trễ phản hồi hệ thống.

---

