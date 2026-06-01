import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker

class ReActAgent:
    """
    Hệ thống ReAct Agent điều phối vòng lặp Thought-Action-Observation.
    Đã fix lỗi đồng bộ tham số API và tối ưu hóa chuỗi Final Answer chống lặp văn bản.
    """
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.tools_description = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])

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
Final Answer: [Your complete, beautifully formatted tour itinerary in Vietnamese]

Important: When you output 'Action:', you MUST stop generating text immediately and wait for the system's 'Observation:'.
"""

    def run(self, user_input: str) -> Dict[str, Any]:
        start_time = time.time()
        trace_history = []
        current_context = f"User Request: {user_input}\n"
        steps = 0

        while steps < self.max_steps:
            steps += 1
            logger.log_event("AGENT_STEP_START", {"step": steps})
            
            # Khắc phục lỗi gán sai từ khóa 'current_prompt' -> sử dụng 'prompt'
            result = self.llm.generate(prompt=current_context, system_prompt=self.get_system_prompt())
            llm_output = result.get("content", "").strip()
            
            # Ghi nhận dữ liệu Telemetry (Token, Latency, Cost)
            tracker.track_request(
                provider=result.get("provider", "google"),
                model=self.llm.model_name,
                usage=result.get("usage", {}),
                latency_ms=result.get("latency_ms", 0)
            )

            current_context += f"\n{llm_output}"
            
            # Làm sạch định dạng markdown và ký tự nhiễu sinh ra từ LLM
            llm_output_cleaned = re.sub(r"```[a-zA-Z]*\n?", "", llm_output).replace("```", "").strip()
            
            # Kịch bản 1: Nhận diện câu trả lời cuối cùng (Final Answer)
            final_match = re.search(r"Final Answer:\s*(.*)", llm_output_cleaned, re.DOTALL | re.IGNORECASE)
            if final_match:
                logger.log_event("AGENT_END_SUCCESS", {"steps": steps})
                final_ans = final_match.group(1).strip()
                
                # Loại bỏ hiện tượng lặp lại khối văn bản hệ thống do mô hình bắt chước ngữ cảnh cũ
                if "Final Answer:" in final_ans:
                    final_ans = final_ans.split("Final Answer:")[-1].strip()
                final_ans = re.sub(r"(Thought|Action|Observation):.*", "", final_ans, flags=re.IGNORECASE | re.DOTALL).strip()
                return final_ans
            
            # Kịch bản 2: Bóc tách hành động gọi công cụ Action: tool_name(args)
            action_match = re.search(r"Action:\s*(\w+)\((.*)\)", llm_output_cleaned, re.IGNORECASE)
            if action_match:
                tool_name = action_match.group(1).strip()
                tool_args = action_match.group(2).strip()
                
                observation = self._execute_tool(tool_name, tool_args)
                step_data["observation"] = observation
                
                # Cập nhật ngữ cảnh cho bước tiếp theo
                current_context += f"\n{llm_output}\nObservation: {observation}"
            else:
                # Cơ chế tự sửa lỗi định dạng của Agent v2 khi LLM sinh sai cấu trúc ReAct
                error_msg = "Error: Invalid format. You must use 'Action: tool_name(args)' or 'Final Answer: [response]'."
                current_context += f"\nObservation: {error_msg}"
                logger.log_event("AGENT_FORMAT_ERROR", {"output": llm_output})

        logger.log_event("AGENT_END_MAX_STEPS", {"steps": steps})
        return "Xin lỗi, tác tử không thể hoàn thành lịch trình trong số bước quy định (Timeout)."

    def _execute_tool(self, tool_name: str, args: str) -> str:
        for tool in self.tools:
            if tool['name'] == tool_name:
                if "func" in tool and callable(tool["func"]):
                    try:
                        return str(tool["func"](args))
                    except Exception as e:
                        return f"Lỗi thực thi công cụ {tool_name}: {str(e)}"
                return f"Đã gọi thành công công cụ {tool_name}."
        return f"Lỗi: Không tìm thấy công cụ '{tool_name}' trong hệ thống."