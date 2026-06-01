import time
from typing import Dict, Any

from src.telemetry.logger import logger


class PerformanceTracker:
    """Theo dõi và đo lường hiệu năng của LLM (Tokens, Latency, Cost)."""

    def __init__(self):
        self.session_metrics = []

    def track_request(self, provider: str, model: str, usage: Dict[str, int], latency_ms: int):
        metric = {
            "provider": provider,
            "model": model,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "latency_ms": latency_ms,
            # keep both key names for compatibility with UI
            "cost_estimate": self._calculate_cost(model, usage),
        }
        self.session_metrics.append(metric)
        logger.log_event("LLM_METRIC", metric)

    def _calculate_cost(self, model: str, usage: Dict[str, int]) -> float:
        """Tính toán chi phí (USD) dựa theo bảng giá mẫu của phòng lab."""
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        m = model.lower()

        # Biểu giá chuẩn cho Gemini 1.5 Flash ($0.075/1M input, $0.30/1M output)
        if "gemini-1.5-flash" in m or "gemini" in m:
            # Lab dùng giá xấp xỉ
            return ((prompt_tokens / 1_000_000) * 0.075) + ((completion_tokens / 1_000_000) * 0.30)

        # Biểu giá mẫu cho GPT-4o
        if "gpt-4o" in m:
            return ((prompt_tokens / 1_000_000) * 5.00) + ((completion_tokens / 1_000_000) * 15.00)

        return 0.0


# Global tracker instance (required by imports)
tracker = PerformanceTracker()

