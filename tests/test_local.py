import os
import sys
import re
from dotenv import load_dotenv

# Luôn đẩy thư mục gốc của dự án vào sys.path để nhận diện chính xác thư mục `src`
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.agent import ReActAgent
from src.core.gemini_provider import GeminiProvider

# --- KHAI BÁO MOCK LOGIC CHO CÁC TOOLS THEO KỊCH BẢN TOUR DU LỊCH ---

def search_spots_impl(args_str: str) -> str:
    return "Gợi ý: Chùa Linh Ứng, Phố cổ Hội An, ngắm cảnh Sơn Trà từ xe. Các điểm này đều bằng phẳng, di chuyển bằng ô tô cực kỳ thuận tiện cho người già và trẻ em."

def get_weather_impl(args_str: str) -> str:
    return "Thời tiết Đà Nẵng ngày mai: Nắng gắt (36°C) từ 11h - 15h. Đầu sáng và cuối chiều thời tiết dịu mát (29°C)."

def book_car_impl(args_str: str) -> str:
    size_match = re.search(r'size=["\']([^"\']*)["\']', args_str)
    size = size_match.group(1) if size_match else "7_seater"
    return f"Xe {size} (Fortuner) kèm tài xế đã được giữ chỗ thành công. Giá trọn gói: 1.200.000 VNĐ."


def test_react_agent_with_gemini():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("DEFAULT_MODEL", "gemini-1.5-flash")
    
    print(f"--- Đang chạy tích hợp ReAct Agent với {model_name} ---")
    
    if not api_key:
        print("❌ Lỗi: Vui lòng bổ sung GEMINI_API_KEY vào file .env")
        return

    # 1. Khởi tạo Mô hình
    provider = GeminiProvider(model_name=model_name, api_key=api_key)
    
    # 2. Tạo danh sách Tools và cấu hình function mapping
    tools = [
        {
            "name": "search_spots",
            "description": "Tìm kiếm điểm tham quan phù hợp theo tiêu chí, tránh leo trèo (tags=['accessible', 'no_climbing']).",
            "func": search_spots_impl
        },
        {
            "name": "get_weather",
            "description": "Lấy thông tin dự báo thời tiết của thành phố theo ngày (date='tomorrow').",
            "func": get_weather_impl
        },
        {
            "name": "book_car",
            "description": "Đặt xe du lịch. Tham số bao gồm size xe và yêu cầu đặc biệt (size='7_seater', note='child_seat').",
            "func": book_car_impl
        }
    ]
    
    # 3. Khởi tạo Agent
    agent = ReActAgent(llm=provider, tools=tools, max_steps=5)
    
    # Kịch bản test đầu vào
    user_input = "Thiết kế tour Đà Nẵng 1 ngày cho 6 người (có người già >70 tuổi và bé 4 tuổi), tiêu chí: đi nhẹ nhàng, tránh nắng."
    print(f"\nUser Request: {user_input}\n")
    
    # 4. Chạy Agent
    try:
        final_answer = agent.run(user_input)
        print("\n🤖 [CHATBOT AGENT RESPONSE]:")
        print("-" * 50)
        print(final_answer)
        print("-" * 50)
        print("\n✅ Thử nghiệm Agent với Gemini thành công! Xem log chi tiết tại thư mục /logs")
    except Exception as e:
        print(f"\n❌ Gặp lỗi khi Agent vận hành: {e}")

if __name__ == "__main__":
    test_react_agent_with_gemini()