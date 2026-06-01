import os
from dotenv import load_dotenv

# Import Agent và Provider từ hệ thống lõi của bạn
from src.agent.agent import ReActAgent
from src.core.gemini_provider import GeminiProvider
from src.core.openai_provider import OpenAIProvider

# IMPORT CHÍNH XÁC CÁC TOOLS TỪ THƯ MỤC CẤU TRÚC SRC/TOOLS/
from src.tools.tour_tools import search_attractions, check_weather_forecast, calculate_tour_budget

def main():
    # 1. Tải các biến môi trường từ .env
    load_dotenv()
    
    provider_type = os.getenv("DEFAULT_PROVIDER", "google").lower()
    model_name = os.getenv("DEFAULT_MODEL", "gemini-1.5-flash")
    api_key = os.getenv("GEMINI_API_KEY") if provider_type == "google" else os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("❌ Lỗi: Vui lòng cấu hình GEMINI_API_KEY hoặc OPENAI_API_KEY trong file .env!")
        return

    print(f"--- Khởi chạy AI Travel Agent ({provider_type.upper()} - {model_name}) ---")

    # 2. Lựa chọn LLM Provider tương ứng
    if provider_type == "google":
        llm = GeminiProvider(model_name=model_name, api_key=api_key)
    elif provider_type == "openai":
        llm = OpenAIProvider(model_name=model_name, api_key=api_key)
    else:
        print("❌ Hệ thống chưa thiết lập provider này ở chế độ tự động.")
        return

    # 3. Liên kết các hàm python đã import ở trên vào danh sách cấu cụ cung cấp cho LLM
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

    # 4. Khởi tạo ReAct Agent (Giới hạn tối đa 5 vòng lặp suy nghĩ để tránh infinite loop)
    agent = ReActAgent(llm=llm, tools=tour_tools_config, max_steps=5)

    print("\n" + "="*60)
    print("🤖 AI TRAVEL AGENT ĐÃ SẴN SÀNG CHẠY TỰ ĐỘNG CHUẨN MODULES!")
    print("Mẫu thử nghiệm: 'Thiết kế tour du lịch Đà Nẵng 1 ngày vào ngày mai cho đoàn 6 người có người già cao tuổi, yêu cầu đi nhẹ nhàng tránh nắng và tính toán tổng chi phí tiền xe + vé.'")
    print("Nhập 'exit' hoặc 'quit' để tắt chương trình.")
    print("="*60 + "\n")

    # Vòng lặp nhận câu hỏi tự động liên tục từ khách hàng
    while True:
        try:
            user_query = input("👤 Khách hàng: ").strip()
            if not user_query:
                continue
            if user_query.lower() in ["exit", "quit"]:
                print("🤖 Đang đóng Agent du lịch...")
                break
                
            print("\n⚙️ [Agent bắt đầu phân tích chu trình ReAct Loop...]")
            response = agent.run(user_query)
            
            print(f"\n🤖 Kết quả thiết kế từ AI Travel Agent:\n")
            print("-" * 60)
            print(response)
            print("-" * 60 + "\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Phát sinh lỗi trong quá trình vận hành: {e}\n")

if __name__ == "__main__":
    main()