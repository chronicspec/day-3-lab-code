import time
from typing import Dict, Any, List
from src.telemetry.logger import logger

class PerformanceTracker:
    """
    Theo dõi và cấu trúc hóa các chỉ số hiệu năng (Tokens, Latency, Cost).
    """
    def __init__(self):
        self.session_metrics: List[Dict[str, Any]] = []

    def track_request(self, provider: str, model: str, usage: Dict[str, int], latency_ms: int):
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
        logger.log_event("LLM_METRIC", metric)

    def _calculate_cost(self, provider: str, model: str, usage: Dict[str, int]) -> float:
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        model_lower = model.lower()
        provider_lower = provider.lower()

        if provider_lower == "local" or "phi" in model_lower or "llama" in model_lower:
            return 0.0

        # Áp dụng biểu giá chuẩn Google AI Studio cho Gemini 1.5 Flash
        if "gemini-1.5-flash" in model_lower:
            return ((prompt_tokens / 1_000_000) * 0.075) + ((completion_tokens / 1_000_000) * 0.30)
        elif "gemini-1.5-pro" in model_lower:
            return ((prompt_tokens / 1_000_000) * 1.25) + ((completion_tokens / 1_000_000) * 5.00)
        elif "gpt-4o-mini" in model_lower:
            return ((prompt_tokens / 1_000_000) * 0.15) + ((completion_tokens / 1_000_000) * 0.60)
        
        return (usage.get("total_tokens", 0) / 1000) * 0.002

    def get_session_summary(self) -> Dict[str, Any]:
        if not self.session_metrics:
            return {"status": "No data recorded in this session."}

        total_reqs = len(self.session_metrics)
        return {
            "total_requests": total_reqs,
            "total_prompt_tokens": sum(m["prompt_tokens"] for m in self.session_metrics),
            "total_completion_tokens": sum(m["completion_tokens"] for m in self.session_metrics),
            "total_tokens_consumed": sum(m["total_tokens"] for m in self.session_metrics),
            "total_latency_ms": sum(m["latency_ms"] for m in self.session_metrics),
            "average_latency_ms": int(sum(m["latency_ms"] for m in self.session_metrics) / total_reqs),
            "total_cost_usd": sum(m["cost_estimate"] for m in self.session_metrics)
        }

tracker = PerformanceTracker()