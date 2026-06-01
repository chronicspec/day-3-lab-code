import os
import re
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker # Đảm bảo import tracker để tính toán Token/Cost

class ReActAgent:
    """
    Hệ thống ReAct Agent du lịch điều phối vòng lặp Thought-Action-Observation.
    Đã sửa lỗi gọi sai tham số API và tối ưu hóa xử lý chuỗi phản hồi.
    """
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        return f"""You are an expert AI Travel Agent. Your goal is to design a customized itinerary using ONLY provided tools.

Available tools:
{tool_descriptions}

CRITICAL RULES - READ CAREFULLY:
1. DATA INTEGRITY: You are strictly forbidden from hallucinating information. 
   - If you need to know about attractions, prices, or weather, you MUST call the relevant tool.
   - If a tool returns information, you MUST use that exact information in your Final Answer.
   - If a tool returns no data, you must inform the user about the lack of information rather than inventing it.

2. REASONING PROCESS: You must use the ReAct framework: Thought -> Action -> Observation.
   - Thought: Analyze what information is missing.
   - Action: Call a tool to get the missing information.
   - Observation: Use the tool output to refine your plan.

3. FINAL OUTPUT: 
   - Final Answer: Your itinerary must be based ONLY on the data retrieved from tools. If you are calculating budget, use the values from the tool, not your internal knowledge.

Format:
Thought: [Reasoning]
Action: tool_name(arguments_string)

If you have collected all observations and are ready to give the final itinerary to the user:
Thought: [Your final reasoning concluding the tour planning]
Final Answer: [Your complete, beautifully formatted tour itinerary in Vietnamese]

Important: When you output 'Action:', you MUST stop generating text immediately and wait for the system's 'Observation:'.
"""

    def run(self, user_input: str) -> str:
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        
        # Biến lưu trữ toàn bộ ngữ cảnh chuỗi suy nghĩ tích lũy qua các bước
        current_context = f"User Request: {user_input}\n"
        steps = 0

        while steps < self.max_steps:
            steps += 1
            logger.log_event("AGENT_STEP_START", {"step": steps})
            
            result = self.llm.generate(prompt=current_context, system_prompt=self.get_system_prompt())
            
            llm_output = result.get("content", "").strip()
            
            # Ghi nhận Telemetry (Tokens, Latency, Cost) vào hệ thống giám sát
            tracker.track_request(
                provider=result.get("provider", "google"),
                model=self.llm.model_name,
                usage=result.get("usage", {}),
                latency_ms=result.get("latency_ms", 0)
            )

            # Nối phản hồi của LLM vào lịch sử suy nghĩ
            current_context += f"\n{llm_output}"
            
            # Xử lý làm sạch chuỗi (Chống lỗi markdown backticks ```json gây lỗi parser)
            llm_output_cleaned = re.sub(r"```[a-zA-Z]*\n?", "", llm_output).replace("```", "").strip()
            
            # Kịch bản 1: Nhận diện câu trả lời cuối cùng (Final Answer)
            final_match = re.search(r"Final Answer:\s*(.*)", llm_output_cleaned, re.DOTALL | re.IGNORECASE)
            if final_match:
                logger.log_event("AGENT_END_SUCCESS", {"steps": steps})
                return final_match.group(1).strip()
            
            # Kịch bản 2: Nhận diện hành động gọi Tools dạng tool_name(args)
            action_match = re.search(r"Action:\s*(\w+)\((.*)\)", llm_output_cleaned, re.IGNORECASE)
            if action_match:
                tool_name = action_match.group(1).strip()
                tool_args = action_match.group(2).strip()
                
                # Thực thi công cụ
                observation = self._execute_tool(tool_name, tool_args)
                
                # Nối Observation ngược lại prompt để chuẩn bị cho vòng lặp kế tiếp
                current_context += f"\nObservation: {observation}"
                logger.log_event("AGENT_TOOL_CALL", {"tool": tool_name, "args": tool_args, "observation": observation})
            else:
                # Tính năng Agent v2: Tự sửa lỗi định dạng nếu LLM không sinh đúng Action/Final Answer
                error_msg = "Error: Invalid format. You must use 'Action: tool_name(args)' or 'Final Answer: [response]'."
                current_context += f"\nObservation: {error_msg}"
                logger.log_event("AGENT_FORMAT_ERROR", {"output": llm_output})

        logger.log_event("AGENT_END_MAX_STEPS", {"steps": steps})
        return "Xin lỗi, Agent không thể hoàn thành lịch trình du lịch trong số bước quy định (Timeout)."

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """
        Tìm kiếm và thực thi hàm python tương ứng theo tên được gọi từ LLM.
        """
        for tool in self.tools:
            if tool['name'] == tool_name:
                if "func" in tool and callable(tool["func"]):
                    try:
                        return str(tool["func"](args))
                    except Exception as e:
                        return f"Lỗi thực thi công cụ {tool_name}: {str(e)}"
                return f"Đã gọi thành công công cụ {tool_name}."
        return f"Lỗi: Không tìm thấy công cụ '{tool_name}' trong hệ thống (Hallucination Error)."