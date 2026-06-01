import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from src.agent.agent import ReActAgent
from src.core.gemini_provider import GeminiProvider
from src.tools.tour_tools import search_attractions, check_weather_forecast, calculate_tour_budget
from src.telemetry.logger import logger

load_dotenv()

app = FastAPI(title="DeepSeek-Style Travel Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

provider_type = os.getenv("DEFAULT_PROVIDER", "google").lower()
model_name = os.getenv("DEFAULT_MODEL", "gemini-1.5-flash")
api_key = os.getenv("GEMINI_API_KEY")

llm = GeminiProvider(model_name=model_name, api_key=api_key)

tour_tools_config = [
    {"name": "search_attractions", "description": "Tra cứu điểm tham quan.", "func": search_attractions},
    {"name": "check_weather_forecast", "description": "Lấy thông tin thời tiết.", "func": check_weather_forecast},
    {"name": "calculate_tour_budget", "description": "Tính toán ngân sách chuyến đi.", "func": calculate_tour_budget}
]

# Lớp kế thừa nhẹ để bóc tách lịch sử bước đi (Trace Steps) trong chu trình chạy
class TrackedReActAgent(ReActAgent):
    def run_with_trace(self, user_input: str):
        current_context = f"User Request: {user_input}\n"
        steps = 0
        trace_history = []

        while steps < self.max_steps:
            steps += 1
            result = self.llm.generate(prompt=current_context, system_prompt=self.get_system_prompt())
            llm_output = result.get("content", "").strip()
            current_context += f"\n{llm_output}"
            
            # Phân tích Thought & Action/Final Answer
            import re
            thought_match = re.search(r"Thought:\s*(.*?)(?=(Action:|Final Answer:|$))", llm_output, re.DOTALL | re.IGNORECASE)
            thought_text = thought_match.group(1).strip() if thought_match else "Đang phân tích dữ liệu..."
            
            final_match = re.search(r"Final Answer:\s*(.*)", llm_output, re.DOTALL | re.IGNORECASE)
            if final_match:
                final_ans = final_match.group(1).strip()
                if "Final Answer:" in final_ans:
                    final_ans = final_ans.split("Final Answer:")[-1].strip()
                final_ans = re.sub(r"(Thought|Action|Observation):.*", "", final_ans, flags=re.IGNORECASE | re.DOTALL).strip()
                
                trace_history.append({"step": steps, "thought": thought_text, "action": "Xác định câu trả lời cuối cùng", "observation": "Hoàn thành"})
                return {"response": final_ans, "traces": trace_history}
            
            action_match = re.search(r"Action:\s*(\w+)\((.*)\)", llm_output, re.IGNORECASE)
            if action_match:
                tool_name = action_match.group(1).strip()
                tool_args = action_match.group(2).strip()
                observation = self._execute_tool(tool_name, tool_args)
                current_context += f"\nObservation: {observation}"
                
                trace_history.append({
                    "step": steps,
                    "thought": thought_text,
                    "action": f"Gọi công cụ `{tool_name}({tool_args})`",
                    "observation": observation
                })
            else:
                error_msg = "Không rõ định dạng hành động."
                current_context += f"\nObservation: {error_msg}"
                trace_history.append({"step": steps, "thought": thought_text, "action": "Sai định dạng", "observation": error_msg})

        return {"response": "Tác tử quá hạn số bước (Timeout).", "traces": trace_history}

agent = TrackedReActAgent(llm=llm, tools=tour_tools_config, max_steps=5)

class QueryRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_endpoint(request: QueryRequest):
    try:
        user_query = request.message.strip()
        if not user_query:
            raise HTTPException(status_code=400, detail="Nội dung trống")
        
        result_data = agent.run_with_trace(user_query)
        return {"status": "success", **result_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main_api:app", host="127.0.0.1", port=8000, reload=True)