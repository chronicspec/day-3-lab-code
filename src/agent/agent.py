import re
from typing import List, Dict, Any

from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger
from src.telemetry.metrics import tracker


class ReActAgent:
    """ReAct Agent: Thought -> Action -> Observation loop."""

    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps

    def get_system_prompt(self) -> str:
        tool_descriptions = "\n".join([f"- {t['name']}: {t['description']}" for t in self.tools])
        return f"""
You are an intelligent travel assistant. Solve the user's request step-by-step using the ReAct framework.

You have access to the following tools:
{tool_descriptions}

CRITICAL FORMAT INSTRUCTIONS:
At each step, output EXACTLY ONE of the following formats (no extra text):

If you want to use a tool:
Thought: <reasoning>
Action: tool_name(arguments_string)

If you are ready to give the final response to the user:
Thought: <reasoning>
Final Answer: <your complete final response in Vietnamese>

Important:
- Once you output 'Action:', STOP generating and wait for the system to return 'Observation:'
""".strip()

    def run(self, user_input: str) -> str:
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})

        transcript = f"User Request: {user_input}\n"
        steps = 0

        while steps < self.max_steps:
            steps += 1
            logger.log_event("AGENT_STEP_START", {"step": steps})

            result = self.llm.generate(prompt=transcript, system_prompt=self.get_system_prompt())
            llm_output = (result.get("content") or "").strip()

            tracker.track_request(
                provider=result.get("provider", "google"),
                model=self.llm.model_name,
                usage=result.get("usage", {}),
                latency_ms=result.get("latency_ms", 0),
            )

            logger.log_event("AGENT_LLM_OUTPUT", {"step": steps, "output": llm_output})

            transcript += f"\n{llm_output}"

            # Final Answer
            final_match = re.search(
                r"Final Answer:\s*(.*)",
                llm_output,
                flags=re.DOTALL | re.IGNORECASE,
            )
            if final_match:
                logger.log_event("AGENT_END_SUCCESS", {"steps": steps})
                return final_match.group(1).strip()

            # Action: tool_name(args)
            action_match = re.search(
                r"Action:\s*([a-zA-Z_][\w]*)\s*\(\s*(.*)\s*\)\s*$",
                llm_output,
                flags=re.IGNORECASE | re.DOTALL,
            )
            if action_match:
                tool_name = action_match.group(1).strip()
                tool_args = action_match.group(2).strip()

                observation = self._execute_tool(tool_name, tool_args)
                transcript += f"\nObservation: {observation}"

                logger.log_event(
                    "AGENT_TOOL_CALL",
                    {"tool": tool_name, "args": tool_args, "observation": observation},
                )
                continue

            # Format error -> feed back for self-correction
            error_msg = (
                "Error: Invalid format. You must respond with either:\n"
                "- Thought + Action: tool_name(arguments_string)\n"
                "or\n"
                "- Thought + Final Answer: ..."
            )
            transcript += f"\nObservation: {error_msg}"
            logger.log_event("AGENT_FORMAT_ERROR", {"step": steps, "output": llm_output})

        logger.log_event("AGENT_END_MAX_STEPS", {"steps": steps})
        return "Hệ thống vượt quá số bước giới hạn cho phép để giải quyết bài toán."

    def _execute_tool(self, tool_name: str, args: str) -> str:
        """Execute a registered tool by name."""
        for tool in self.tools:
            if tool.get("name") == tool_name:
                func = tool.get("func")
                if callable(func):
                    try:
                        return str(func(args))
                    except Exception as e:
                        return f"Lỗi khi thực thi công cụ {tool_name}: {str(e)}"
                return f"Kết quả xử lý mặc định của {tool_name} với tham số ({args})"

        return f"Tool {tool_name} không tồn tại."
