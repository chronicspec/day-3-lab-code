import os
from dotenv import load_dotenv
from src.core.gemini_provider import GeminiProvider

def run_chatbot_baseline():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("DEFAULT_MODEL", "gemini-1.5-flash")
    
    print(f"--- Đang chạy Chatbot Baseline với {model_name} ---")
    
    if not api_key:
        print("❌ Lỗi: Vui lòng bổ sung GEMINI_API_KEY vào file .env")
        return

    # Khởi tạo provider
    provider = GeminiProvider(model_name=model_name, api_key=api_key)
    
    # Kịch bản test (giống kịch bản tour Đà Nẵng)
    user_input = "Thiết kế tour Đà Nẵng 1 ngày cho 6 người (có người già >70 tuổi và bé 4 tuổi), tiêu chí: đi nhẹ nhàng, tránh nắng."
    
    print(f"\nUser Request: {user_input}\n")
    
    # Chatbot baseline gửi thẳng prompt tới LLM mà không qua trung gian xử lý logic
    system_instruction = "You are a helpful travel assistant."
    result = provider.generate(prompt=user_input, system_prompt=system_instruction)
    
    print("\n🤖 [CHATBOT BASELINE RESPONSE]:")
    print("-" * 50)
    print(result.get("content"))
    print("-" * 50)

if __name__ == "__main__":
    run_chatbot_baseline()