import os
import sys
import re
from dotenv import load_dotenv

# Đẩy thư mục gốc vào path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.agent import ReActAgent
from src.core.gemini_provider import GeminiProvider

# --- MOCK LOGIC CHO TOOLS ---
def search_spots_impl(args_str: str) -> str:
    return "Gợi ý: Chùa Linh Ứng, Phố cổ Hội An, ngắm cảnh Sơn Trà từ xe. Các điểm này đều bằng phẳng, di chuyển bằng ô tô cực kỳ thuận tiện."

def get_weather_impl(args_str: str) -> str:
    return "Thời tiết Đà Nẵng ngày mai: Nắng gắt (36°C) từ 11h - 15h. Đầu sáng và cuối chiều thời tiết dịu mát (29°C)."

def book_car_impl(args_str: str) -> str:
    size_match = re.search(r'size=["\']?([^"\']+)["\']?', args_str)
    size = size_match.group(1) if size_match else "7_seater"
    return f"Xe {size} (Fortuner) kèm tài xế đã được giữ chỗ thành công. Giá trọn gói: 1.200.000 VNĐ."

def run_agent(user_input: str) -> str:
    """Hàm này được gọi từ Flask hoặc các module khác, trả về chuỗi kết quả."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("DEFAULT_MODEL", "gemini-1.5-flash")
    
    if not api_key:
        return "❌ Lỗi: Vui lòng bổ sung GEMINI_API_KEY vào file .env"

    # 1. Khởi tạo
    provider = GeminiProvider(model_name=model_name, api_key=api_key)
    tools = [
        {"name": "search_spots", "description": "Tìm kiếm điểm tham quan phù hợp.", "func": search_spots_impl},
        {"name": "get_weather", "description": "Lấy dự báo thời tiết.", "func": get_weather_impl},
        {"name": "book_car", "description": "Đặt xe du lịch.", "func": book_car_impl}
    ]
    
    # 2. Chạy Agent
    agent = ReActAgent(llm=provider, tools=tools, max_steps=5)
    
    try:
        final_answer = agent.run(user_input)
        return final_answer
    except Exception as e:
        return f"❌ Lỗi vận hành Agent: {str(e)}"

# Giữ lại khối này để vẫn có thể test chạy trực tiếp bằng lệnh: python test_local.py
if __name__ == "__main__":
    test_input = "Thiết kế tour Đà Nẵng 1 ngày cho 6 người (có người già và bé 4 tuổi), tiêu chí: nhẹ nhàng, tránh nắng."
    print(run_agent(test_input))