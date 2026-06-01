import time
from typing import Dict, Any, List
from src.telemetry.logger import logger

class PerformanceTracker:
    """
    Theo dõi và đo lường hiệu năng của LLM (Tokens, Latency, Cost).
    """
    def __init__(self):
        self.session_metrics = []

    def track_request(self, provider: str, model: str, usage: Dict[str, int], latency_ms: int):
        """
        Ghi nhận metric của request vào hệ thống log telemetry.
        """
        metric = {
            "provider": provider,
            "model": model,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "latency_ms": latency_ms,
            "cost_estimate": self._calculate_cost(model, usage)
        }
        self.session_metrics.append(metric)
        logger.log_event("LLM_METRIC", metric)

    def _calculate_cost(self, model: str, usage: Dict[str, int]) -> float:
        """
        Tính toán chi phí dựa theo biểu giá thực tế của Gemini API.
        """
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)

        # Biểu giá Gemini 1.5 Flash: $0.075 / 1M input tokens và $0.30 / 1M output tokens
        if "gemini" in model.lower():
            input_cost = (prompt_tokens / 1_000_000) * 0.075
            output_cost = (completion_tokens / 1_000_000) * 0.30
            return input_cost + output_cost
        
        return (usage.get("total_tokens", 0) / 1000) * 0.01

# Global tracker instance
tracker = PerformanceTracker()