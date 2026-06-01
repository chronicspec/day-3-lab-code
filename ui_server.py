from __future__ import annotations

import os
import json
import uuid
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.agent.agent import ReActAgent
from src.core.gemini_provider import GeminiProvider
from src.core.openai_provider import OpenAIProvider
# LocalProvider requires llama-cpp-python (optional dependency)
# Import lazily inside _build_llm() so UI can run even if llama-cpp-python isn't installed.


from src.telemetry.logger import logger

import re


load_dotenv()

app = FastAPI(title="AI Travel Agent - Local UI")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# static (css/js)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")


def _build_tools():
    # dùng chính xác bộ tool tour_tools hiện có (import động để tránh lỗi đường dẫn)
    try:
        from src.tools.tour_tools import (
            search_attractions,
            check_weather_forecast,
            calculate_tour_budget,
        )

        tools = [
            {
                "name": "search_attractions",
                "description": "Tìm kiếm địa điểm tham quan du lịch phù hợp dựa trên điểm đến và nhãn yêu cầu đặc biệt. Đầu vào truyền chuỗi văn bản (Ví dụ: 'danang, nguoi_gia, nhe_nhang').",
                "func": search_attractions,
            },
            {
                "name": "check_weather_forecast",
                "description": "Lấy thông tin dự báo thời tiết chi tiết của một thành phố cụ thể theo ngày để tránh nắng mưa. Đầu vào truyền tên thành phố (Ví dụ: 'danang, tomorrow').",
                "func": check_weather_forecast,
            },
            {
                "name": "calculate_tour_budget",
                "description": "Tính toán tổng chi phí dự kiến gồm tiền thuê xe ô tô đưa đón riêng và vé vào cửa. Đầu vào truyền số lượng khách (Ví dụ: 'pax=6, destination=danang').",
                "func": calculate_tour_budget,
            },
        ]
        return tools
    except Exception:
        # fallback: bộ tool local test
        def search_spots_impl(args_str: str) -> str:
            return "Gợi ý: Chùa Linh Ứng, Phố cổ Hội An, ngắm cảnh Sơn Trà từ xe. Các điểm này đều bằng phẳng, di chuyển bằng ô tô cực kỳ thuận tiện."

        def get_weather_impl(args_str: str) -> str:
            return "Thời tiết Đà Nẵng ngày mai: Nắng gắt (36°C) từ 11h - 15h. Đầu sáng và cuối chiều dịu mát (29°C)."

        def book_car_impl(args_str: str) -> str:
            size_match = re.search(r"size=[\"']([^\"']*)[\"']", args_str)
            size = size_match.group(1) if size_match else "7_seater"
            return f"Xe {size} (Fortuner) kèm tài xế đã được giữ chỗ. Giá trọn gói: 1.200.000 VNĐ."

        return [
            {
                "name": "search_spots",
                "description": "Tìm kiếm điểm tham quan phù hợp theo tiêu chí (accessible, no_climbing...).",
                "func": search_spots_impl,
            },
            {
                "name": "get_weather",
                "description": "Lấy thông tin dự báo thời tiết của một thành phố theo ngày.",
                "func": get_weather_impl,
            },
            {
                "name": "book_car",
                "description": "Đặt thuê xe du lịch riêng kèm tài xế. Tham số: size (số chỗ), note (ghi chú).",
                "func": book_car_impl,
            },
        ]


def _build_llm() -> Any:
    provider_type = os.getenv("DEFAULT_PROVIDER", "google").lower()
    model_name = os.getenv("DEFAULT_MODEL", "gemini-1.5-flash")

    if provider_type == "google":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("Missing GEMINI_API_KEY in .env")
        return GeminiProvider(model_name=model_name, api_key=api_key)

    if provider_type == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Missing OPENAI_API_KEY in .env")
        return OpenAIProvider(model_name=model_name, api_key=api_key)

    if provider_type == "local":
        model_path = os.getenv("LOCAL_MODEL_PATH")
        if not model_path:
            raise RuntimeError("Missing LOCAL_MODEL_PATH in .env")
        n_ctx = int(os.getenv("LOCAL_N_CTX", "4096"))
        return LocalProvider(model_path=model_path, n_ctx=n_ctx)

    raise RuntimeError(f"Unsupported DEFAULT_PROVIDER={provider_type}")


def _run_agent_with_trace(agent: ReActAgent, user_input: str) -> Dict[str, Any]:
    """
    Vì ReActAgent hiện chưa trả trace trực tiếp, ta dựa vào logs +
    parsing thô để vẫn hiển thị một Trace tối thiểu.

    - final_answer: lấy từ agent.run
    - trace_steps: cố gắng suy ra từ đoạn output cuối

    Nếu bạn muốn trace chuẩn 100% theo từng tool call, ta sẽ nâng cấp ReActAgent
    để expose trace.
    """
    # Cách đơn giản: chạy agent, lấy final answer.
    final_answer = agent.run(user_input)

    # Parse token: cố gắng tách các phần theo Final Answer; còn lại để trống.
    # UI vẫn có chỗ để hiển thị.
    trace_steps: List[Dict[str, Any]] = []
    # Heuristic: tách dòng có vẻ như itinerary.
    trace_steps.append(
        {
            "type": "summary",
            "llm_output": final_answer,
            "tool": None,
            "args": None,
            "observation": None,
        }
    )

    return {
        "id": str(uuid.uuid4()),
        "final_answer": final_answer,
        "trace": trace_steps,
        "telemetry": {},
    }


# Cache agent instance để không khởi tạo lại mỗi request
AGENT_SINGLETON: Optional[ReActAgent] = None


def get_agent() -> ReActAgent:
    global AGENT_SINGLETON
    if AGENT_SINGLETON is None:
        llm = _build_llm()
        tools = _build_tools()
        AGENT_SINGLETON = ReActAgent(llm=llm, tools=tools, max_steps=5)
    return AGENT_SINGLETON


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "AI Travel Agent - UI/UX Localhost",
        },
    )


@app.post("/api/chat")
def chat(payload: Dict[str, Any]):
    user_input = (payload.get("user_input") or "").strip()
    if not user_input:
        return JSONResponse({"error": "user_input is required"}, status_code=400)

    agent = get_agent()
    logger.log_event("UI_CHAT_START", {"input": user_input})

    out = _run_agent_with_trace(agent, user_input)
    logger.log_event("UI_CHAT_END", {"id": out.get("id")})
    return out

