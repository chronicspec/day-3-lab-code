import os
from dotenv import load_dotenv

from src.agent.agent import ReActAgent
from src.core.gemini_provider import GeminiProvider
from src.tools.tour_tools import search_attractions, check_weather_forecast, calculate_tour_budget
from src.telemetry.evaluator import AgentEvaluator # Import bộ đánh giá dữ liệu log

def main():
    load_dotenv()
    
    provider_type = os.getenv("DEFAULT_PROVIDER", "google").lower()
    model_name = os.getenv("DEFAULT_MODEL", "gemini-1.5-flash")
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("❌ Lỗi: Hãy điền đầy đủ GEMINI_API_KEY vào tệp .env")
        return

    # Khởi tạo mô hình Gemini
    llm = GeminiProvider(model_name=model_name, api_key=api_key)

    # Cấu hình danh sách Công cụ Travel Agent
    tour_tools_config = [
    {
        "name": "search_attractions",
        "description": "Tìm địa điểm. Tham số: city='TênThànhPhố', tags='tag1,tag2'. Ví dụ: search_attractions(city='HaNoi', tags='cultural,accessible')",
        "func": search_attractions
    },
    {
        "name": "check_weather_forecast",
        "description": "Xem thời tiết. Tham số: city='TênThànhPhố'. Ví dụ: check_weather_forecast(city='DaNang')",
        "func": check_weather_forecast
    },
    {
        "name": "calculate_tour_budget",
        "description": "Tính ngân sách. Tham số: city='TênThànhPhố', pax=SốNgười, car='LoạiXe'. Ví dụ: calculate_tour_budget(city='DaNang', pax=6, car='7_seater')",
        "func": calculate_tour_budget
    }
]

    agent = ReActAgent(llm=llm, tools=tour_tools_config, max_steps=5)
    evaluator = AgentEvaluator()

    print("\n" + "="*60)
    print("🤖 AI TRAVEL AGENT V2 - PRODUCTION READY")
    print("Hệ thống đã tích hợp Telemetry giám sát tự động.")
    print("👉 Gõ câu hỏi để Agent tự lên lịch trình du lịch.")
    print("👉 Gõ 'eval' để xuất báo cáo dữ liệu Token/Cost/Latency làm báo cáo Lab.")
    print("👉 Gõ 'exit' để thoát chương trình.")
    print("="*60 + "\n")

    while True:
        try:
            user_query = input("### 👤 Khách hàng: ").strip()
            if not user_query:
                continue
            if user_query.lower() == "exit":
                print("🤖 Đang đóng Agent...")
                break
            
            # Nếu người dùng gõ lệnh đánh giá, thực hiện đọc log xuất báo cáo định lượng ngay
            if user_query.lower() == "eval":
                evaluator.run_evaluation()
                continue
                
            print("\n⚙️ [Agent đang thực hiện chu trình ReAct Loop: Thought -> Action -> Observation...]")
            response = agent.run(user_query)
            
            print(f"\n🤖 Agent phản hồi:\n")
            print("-" * 60)
            print(response)
            print("-" * 60 + "\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Lỗi: {e}\n")

if __name__ == "__main__":
    main()