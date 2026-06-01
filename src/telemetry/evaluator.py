import os
import json
from datetime import datetime

class AgentEvaluator:
    """
    Quét và phân tích các file JSON log trong thư mục logs/
    để tính toán các chỉ số Token, Latency, Cost và tỷ lệ lỗi Parser/Timeout.
    """
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir

    def run_evaluation(self):
        if not os.path.exists(self.log_dir):
            print(f"❌ Thư mục '{self.log_dir}' không tồn tại. Hãy chạy Agent trước để sinh log!")
            return

        total_requests = 0
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_latency_ms = 0
        total_cost = 0.0
        
        # Đếm các loại mã lỗi để phục vụ mục "Failure Analysis"
        parser_errors = 0
        format_errors = 0
        max_steps_reached = 0
        success_sessions = 0

        log_files = [f for f in os.listdir(self.log_dir) if f.endswith(".log")]
        
        for file_name in log_files:
            with open(os.path.join(self.log_dir, file_name), "r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        log_data = json.loads(line.strip())
                        event = log_data.get("event")
                        data = log_data.get("data", {})

                        # 1. Thống kê chỉ số LLM Metrics
                        if event == "LLM_METRIC":
                            total_requests += 1
                            total_prompt_tokens += data.get("prompt_tokens", 0)
                            total_completion_tokens += data.get("completion_tokens", 0)
                            total_latency_ms += data.get("latency_ms", 0)
                            total_cost += data.get("cost_estimate", 0.0)

                        # 2. Thống kê lỗi hệ thống
                        elif event == "AGENT_FORMAT_ERROR":
                            format_errors += 1
                        elif event == "AGENT_END_MAX_STEPS":
                            max_steps_reached += 1
                        elif event == "AGENT_END_SUCCESS":
                            success_sessions += 1

                    except json.JSONDecodeError:
                        continue

        # Xuất báo cáo ra console chuẩn báo cáo nghiệm thu
        print("\n" + "="*20 + " 📊 KIỂM TOÁN HIỆU NĂNG AGENT (TELEMETRY) " + "="*20)
        if total_requests == 0:
            print("Chưa thu thập được metric nào từ LLM. Hãy chạy thử main.py trước!")
            return

        avg_latency = total_latency_ms / total_requests
        print(f"⏱️  Tổng số request gọi tới LLM API:  {total_requests}")
        print(f"⏱️  Thời gian phản hồi trung bình:   {avg_latency:.2f} ms")
        print(f"🪙  Tổng lượng Prompt Tokens tiêu thụ: {total_prompt_tokens}")
        print(f"🪙  Tổng lượng Output Tokens tiêu thụ: {total_completion_tokens}")
        print(f"💸  Ước tính chi phí vận hành hệ thống: ${total_cost:.6f} USD")
        
        print("\n" + "-"*15 + " ĐÁNH GIÁ ĐỘ TIN CẬY (RELIABILITY) " + "-"*15)
        print(f"✅ Số lượt hoàn thành Tour thành công: {success_sessions}")
        print(f"⚠️  Số lỗi sai định dạng (Parser Error): {format_errors} (Đã được v2 tự động sửa)")
        print(f"❌ Số lần Agent bị kẹt vòng lặp (Timeout): {max_steps_reached}")
        
        reliability_rate = (success_sessions / (success_sessions + max_steps_reached)) * 100 if (success_sessions + max_steps_reached) > 0 else 0
        print(f"📈 Tỷ lệ giải quyết bài toán thành công:   {reliability_rate:.1f}%")
        print("="*60 + "\n")

if __name__ == "__main__":
    evaluator = AgentEvaluator()
    evaluator.run_evaluation()