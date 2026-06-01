import os
import re
from typing import List, Dict, Any
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker

class ReActAgent:
    """
    Hệ thống ReAct Agent du lịch điều phối vòng lặp Thought-Action-Observation.
    Đã được tinh chỉnh (Phiên bản v2) chống kẹt vòng lặp và xử lý markdown backticks.
    """
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps

    def get_system_prompt(self) -> str:
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        return f"""You are an expert AI Travel Agent. Your job is to design a perfect, customized itinerary based on the user's request.
You must solve this request step-by-step using the ReAct framework: Thought -> Action -> Observation.

Available tools you can use:
{tool_descriptions}

CRITICAL FORMAT INSTRUCTIONS:
At each step, you must output exactly ONE of the following formats. Do not output anything else.

If you decide you need to call a tool:
Thought: [Your reasoning about what to do next]
Action: tool_name(arguments_string)

If you have collected all observations and are ready to give the final itinerary to the user:
Thought: [Your final reasoning concluding the tour planning]
Final Answer: [Your complete, beautifully formatted tour itinerary in Vietnamese, including a breakdown of the schedule, weather considerations, and estimated budget]

Important: When you output 'Action:', you MUST stop generating text immediately and wait for the system's 'Observation:'.
"""

    def run(self, user_input: str) -> str:
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        
        # Lưu ngữ cảnh chuỗi suy nghĩ luỹ kế của Agent
        current_context = f"User Request: {user_input}\n"
        steps = 0

        while steps < self.max_steps:
            steps += 1
            logger.log_event("AGENT_STEP_START", {"step": steps})
            
            # 1. Gọi Gemini/OpenAI API sinh bước suy nghĩ tiếp theo
            result = self.llm.generate(current_prompt=current_context, system_prompt=self.get_system_prompt())
            llm_output = result.get("content", "").strip()
            
            # Ghi nhận dữ liệu giám sát hệ thống (Tokens, Latency) phục vụ chấm điểm Lab
            tracker.track_request(
                provider=result.get("provider", "google"),
                model=self.llm.model_name,
                usage=result.get("usage", {}),
                latency_ms=result.get("latency_ms", 0)
            )

            # Nối kết quả đầu ra của mô hình vào lịch sử xử lý
            current_context += f"\n{llm_output}"
            
            # Cải tiến Agent v2: Làm sạch Markdown nhiễu nhiễu (ví dụ: ```json ... ```) khiến Parser bị lỗi
            llm_output_cleaned = re.sub(r"```[a-zA-Z]*\n?", "", llm_output).replace("```", "").strip()
            
            # Kịch bản 1: Tìm thấy Câu trả lời cuối cùng (Final Answer)
            final_match = re.search(r"Final Answer:\s*(.*)", llm_output_cleaned, re.DOTALL | re.IGNORECASE)
            if final_match:
                logger.log_event("AGENT_END_SUCCESS", {"steps": steps})
                return final_match.group(1).strip()
            
            # Kịch bản 2: Tìm thấy hành động gọi Tool dạng `tool_name(args)`
            action_match = re.search(r"Action:\s*(\w+)\((.*)\)", llm_output_cleaned, re.IGNORECASE)
            if action_match:
                tool_name = action_match.group(1).strip()
                tool_args = action_match.group(2).strip()
                
                # Thực thi tool
                observation = self._execute_tool(tool_name, tool_args)
                
                # Nối Observation ngược lại ngữ cảnh cho bước lặp sau của LLM
                current_context += f"\nObservation: {observation}"
                logger.log_event("AGENT_TOOL_CALL", {"tool": tool_name, "args": tool_args, "observation": observation})
            else:
                # Agent v2 - Tự động nhắc nhở sửa định dạng nếu LLM sinh lỗi cấu trúc (Parser Error)
                error_msg = "Error: Invalid response format. You must strictly use 'Action: tool_name(args)' or 'Final Answer: [response]'."
                current_context += f"\nObservation: {error_msg}"
                logger.log_event("AGENT_FORMAT_ERROR", {"output": llm_output})

        logger.log_event("AGENT_END_MAX_STEPS", {"steps": steps})
        return "Xin lỗi, hệ thống Agent không thể hoàn thành thiết kế lịch trình trong số bước quy định (Timeout)."

    def _execute_tool(self, tool_name: str, args: str) -> str:
        for tool in self.tools:
            if tool['name'] == tool_name:
                if "func" in tool and callable(tool["func"]):
                    try:
                        return str(tool["func"](args))
                    except Exception as e:
                        return f"Lỗi phát sinh từ công cụ {tool_name}: {str(e)}"
                return f"Đã gọi công cụ {tool_name} thành công."
        return f"Lỗi: Không tìm thấy công cụ tên '{tool_name}' trong hệ thống (Hallucination Error)."