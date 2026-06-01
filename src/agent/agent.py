import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker  # Import tracker chuẩn cấu trúc của bạn

class ReActAgent:
    """
    Một Agent theo kiến trúc ReAct hoàn chỉnh, xử lý vòng lặp suy nghĩ và gọi công cụ.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        """
        Tạo system prompt định nghĩa các công cụ hiện có và bắt buộc mô hình tuân thủ ReAct.
        """
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        return f"""
        You are an intelligent travel assistant. You must solve the user's request step-by-step using the ReAct framework.
        
        You have access to the following tools:
        {tool_descriptions}

        CRITICAL FORMAT INSTRUCTIONS:
        At each step, you must output exactly ONE of the following formats. Do not include any extra text.

        If you want to use a tool:
        Thought: [Your reasoning about what to do next]
        Action: tool_name(arguments_string)

        If you are ready to give the final response to the user:
        Thought: [Your final reasoning concluding the task]
        Final Answer: [Your complete, detailed final response to the user in Vietnamese]

        Important: Once you output 'Action:', STOP generating and wait for the 'Observation:' from the system.
        """

    def run(self, user_input: str) -> str:
        """
        Thực thi vòng lặp ReAct phối hợp với Gemini Provider.
        """
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        
        # Lưu trữ toàn bộ mạch hội thoại (Thought/Action/Observation) để LLM đọc liên tục
        current_context = f"User Request: {user_input}\n"
        steps = 0

        while steps < self.max_steps:
            steps += 1
            logger.log_event("AGENT_STEP_START", {"step": steps})
            
            # Gọi API sinh chuỗi tiếp theo
            result = self.llm.generate(prompt=current_context, system_prompt=self.get_system_prompt())
            llm_output = result.get("content", "").strip()
            
            # Ghi nhận Telemetry Metrics (Tokens, Latency)
            tracker.track_request(
                provider=result.get("provider", "google"),
                model=self.llm.model_name,
                usage=result.get("usage", {}),
                latency_ms=result.get("latency_ms", 0)
            )

            # Nối phản hồi của LLM vào ngữ cảnh lịch sử
            current_context += f"\n{llm_output}"
            
            # Kiểm tra xem có Final Answer chưa
            final_match = re.search(r"Final Answer:\s*(.*)", llm_output, re.DOTALL | re.IGNORECASE)
            if final_match:
                logger.log_event("AGENT_END_SUCCESS", {"steps": steps})
                return final_match.group(1).strip()
            
            # Kiểm tra xem có Action gọi Tool không
            action_match = re.search(r"Action:\s*(\w+)\((.*)\)", llm_output, re.IGNORECASE)
            if action_match:
                tool_name = action_match.group(1).strip()
                tool_args = action_match.group(2).strip()
                
                # Thực thi tool
                observation = self._execute_tool(tool_name, tool_args)
                
                # Nối kết quả Observation vào ngữ cảnh để LLM đọc ở vòng lặp kế tiếp
                current_context += f"\nObservation: {observation}"
                logger.log_event("AGENT_TOOL_CALL", {"tool": tool_name, "args": tool_args, "observation": observation})
            else:
                # Ép buộc kết thúc nếu mô hình sinh lệch format
                error_msg = "Error: Invalid format. Please provide 'Action: tool_name(args)' or 'Final Answer: ...'"
                current_context += f"\nObservation: {error_msg}"
                logger.log_event("AGENT_FORMAT_ERROR", {"output": llm_output})

        logger.log_event("AGENT_END_MAX_STEPS", {"steps": steps})
        return "Hệ thống vượt quá số bước giới hạn cho phép để giải quyết bài toán."

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """
        Tìm và thực thi hàm python tương ứng được đăng ký trong cấu hình tools.
        """
        for tool in self.tools:
            if tool['name'] == tool_name:
                if "func" in tool and callable(tool["func"]):
                    try:
                        return tool["func"](args)
                    except Exception as e:
                        return f"Lỗi khi thực thi công cụ {tool_name}: {str(e)}"
                return f"Kết quả xử lý mặc định của {tool_name} với tham số ({args})"
                
        return f"Tool {tool_name} không tồn tại."