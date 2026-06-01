import time
from typing import Dict, Any

from src.telemetry.logger import logger


class PerformanceTracker:
    """
    Bộ theo dõi và thu thập các chỉ số hiệu năng chuẩn công nghiệp (Token, Latency, Cost).
    Dữ liệu được lưu trữ trong session và tự động đẩy vào log hệ thống dưới dạng cấu trúc JSON.
    """
    def __init__(self):
        self.session_metrics: List[Dict[str, Any]] = []

    def track_request(self, provider: str, model: str, usage: Dict[str, int], latency_ms: int):
        """
        Ghi nhận metric của một request đơn lẻ từ LLM Provider và đẩy vào hệ thống telemetry.
        """
        metric = {
            "provider": provider,
            "model": model,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "latency_ms": latency_ms,
            "cost_estimate": self._calculate_cost(provider, model, usage)
        }
        self.session_metrics.append(metric)
        
        # Đẩy dữ liệu ra structured logger (lưu vào file .log trong thư mục logs/)
        logger.log_event("LLM_METRIC", metric)

    def _calculate_cost(self, provider: str, model: str, usage: Dict[str, int]) -> float:
        """
        Tính toán chi phí USD thực tế dựa trên bảng giá (Pricing) của từng dòng mô hình.
        Phục vụ trực tiếp cho bài toán phân tích kinh tế (Cost Analysis & ROI) trong báo cáo Lab.
        """
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        model_lower = model.lower()
        provider_lower = provider.lower()

        # 1. Trường hợp sử dụng mô hình Local (Phi-3, Llama...) chạy trên CPU/GPU cá nhân
        if provider_lower == "local" or "phi" in model_lower or "llama" in model_lower:
            return 0.0  # Chạy offline hoàn toàn miễn phí tiền Token

        # 2. Biểu giá Google Gemini API (Cập nhật chuẩn Google AI Studio)
        # Gemini 1.5 Flash: $0.075 / 1 triệu input tokens | $0.30 / 1 triệu output tokens
        if "gemini-1.5-flash" in model_lower:
            return ((prompt_tokens / 1_000_000) * 0.075) + ((completion_tokens / 1_000_000) * 0.30)
        
        # Gemini 1.5 Pro (Dự phòng nếu bạn nâng cấp): $1.25 / 1M input | $5.00 / 1M output
        elif "gemini-1.5-pro" in model_lower:
            return ((prompt_tokens / 1_000_000) * 1.25) + ((completion_tokens / 1_000_000) * 5.00)

        # 3. Biểu giá OpenAI API (Dự phòng nếu chuyển nhà cung cấp)
        # GPT-4o: $5.00 / 1 triệu input tokens | $15.00 / 1 triệu output tokens
        elif "gpt-4o" in model_lower and "mini" not in model_lower:
            return ((prompt_tokens / 1_000_000) * 5.00) + ((completion_tokens / 1_000_000) * 15.00)
        
        # GPT-4o mini: $0.150 / 1M input | $0.600 / 1M output
        elif "gpt-4o-mini" in model_lower or "gpt-4o" in model_lower:
            return ((prompt_tokens / 1_000_000) * 0.15) + ((completion_tokens / 1_000_000) * 0.60)

        # 4. Biểu giá mặc định dự phòng nếu không khớp model trên (Tính theo giá chung $0.002 / 1K tokens)
        return (usage.get("total_tokens", 0) / 1000) * 0.002

    def get_session_summary(self) -> Dict[str, Any]:
        """
        Tính toán tổng hợp các chỉ số tích lũy của toàn bộ phiên làm việc (Session) hiện tại.
        """
        if not self.session_metrics:
            return {"status": "No data recorded in this session."}

        total_reqs = len(self.session_metrics)
        total_p_tokens = sum(m["prompt_tokens"] for m in self.session_metrics)
        total_c_tokens = sum(m["completion_tokens"] for m in self.session_metrics)
        total_tokens = sum(m["total_tokens"] for m in self.session_metrics)
        total_lat = sum(m["latency_ms"] for m in self.session_metrics)
        total_cost = sum(m["cost_estimate"] for m in self.session_metrics)

        return {
            "total_requests": total_reqs,
            "total_prompt_tokens": total_p_tokens,
            "total_completion_tokens": total_c_tokens,
            "total_tokens_consumed": total_tokens,
            "total_latency_ms": total_lat,
            "average_latency_ms": int(total_lat / total_reqs),
            "total_cost_usd": total_cost
        }

# Khởi tạo instance Global duy nhất để chia sẻ tài nguyên theo dõi xuyên suốt ứng dụng
tracker = PerformanceTracker()