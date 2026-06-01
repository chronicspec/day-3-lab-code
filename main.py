import os
import re
from dotenv import load_dotenv

# Import các module cốt lõi từ project của bạn
from src.agent.agent import ReActAgent
from src.core.gemini_provider import GeminiProvider

# --- ĐĂNG KÝ HÀM XỬ LÝ THỰC TẾ CHO CÁC TOOLS (MOCK DATA HOẶC LOGIC THỰC TẾ) ---
def search_spots_impl(args_str: str) -> str:
    """Công cụ tìm kiếm địa điểm du lịch dựa trên tham số"""
    if "danang" in args_str.lower():
        return "Gợi ý Đà Nẵng: Chùa Linh Ứng, Phố cổ Hội An, ngắm cảnh Sơn Trà từ xe. Các điểm này bằng phẳng, không leo trèo, phù hợp người già và trẻ nhỏ."
    return "Gợi ý chung: Các khu nghỉ dưỡng phức hợp hoặc trung tâm thương mại có máy lạnh."

def get_weather_impl(args_str: str) -> str:
    """Công cụ kiểm tra thời tiết"""
    return "Dự báo thời tiết ngày mai: Nắng gắt (36°C) từ 11h - 15h. Đầu sáng và cuối chiều dịu mát (29°C)."

def book_car_impl(args_str: str) -> str:
    """Công cụ đặt xe tự động"""
    size_match = re.search(r'size=["\']([^"\']*)["\']', args_str)
    size = size_match.group(1) if size_match else "7_seater"
    return f"Xe {size} kèm tài xế riêng đã được giữ chỗ thành công trên hệ thống. Giá trọn gói: 1.200.000 VNĐ."


def initialize_agent():
    """Khởi tạo cấu hình Agent từ file .env"""
    load_dotenv()
    
    # Đọc cấu hình theo đúng file .env của bạn
    api_key = os.getenv("GEMINI_API_KEY")
    model_name = os.getenv("DEFAULT_MODEL", "gemini-1.5-flash")
    
    if not api_key:
        raise ValueError("❌ Lỗi: Không tìm thấy GEMINI_API_KEY trong file .env!")

    # 1. Khởi tạo LLM Provider (Gemini)
    provider = GeminiProvider(model_name=model_name, api_key=api_key)
    
    # 2. Định nghĩa danh sách công cụ Agent được phép dùng
    tools = [
        {
            "name": "search_spots",
            "description": "Tìm kiếm các địa điểm tham quan phù hợp theo tiêu chí (ví dụ: tags=['accessible', 'no_climbing']).",
            "func": search_spots_impl
        },
        {
            "name": "get_weather",
            "description": "Lấy thông tin dự báo thời tiết chi tiết của một thành phố theo ngày.",
            "func": get_weather_impl
        },
        {
            "name": "book_car",
            "description": "Đặt thuê xe du lịch riêng kèm tài xế. Tham số truyền vào: size (số chỗ), note (ghi chú).",
            "func": book_car_impl
        }
    ]
    
    # 3. Tạo instance ReActAgent
    return ReActAgent(llm=provider, tools=tools, max_steps=5)


def main():
    try:
        agent = initialize_agent()
    except Exception as e:
        print(e)
        return

    print("\n" + "="*50)
    print("🤖 AI TRAVEL AGENT TRỰC TUYẾN ĐÃ SẴN SÀNG CHẠY TỰ ĐỘNG!")
    print("Hệ thống sử dụng mô hình: " + os.getenv("DEFAULT_MODEL", "gemini-1.5-flash"))
    print("Gõ 'exit' hoặc 'quit' để dừng chương trình.")
    print("="*50 + "\n")

    # Vòng lặp CLI vô hạn giúp Agent chạy tự động liên tục
    while True:
        try:
            # Nhận request bất kỳ từ người dùng
            user_input = input("👤 Bạn: ").strip()
            
            # Điều kiện thoát
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit"]:
                print("🤖 Tạm biệt bạn! Hy vọng gặp lại bạn trong chuyến đi tới.")
                break
            
            print("\n⚙️ [Agent đang suy nghĩ và điều phối công cụ...] Please wait...")
            
            # Kích hoạt Agent xử lý vòng lặp ReAct tự động
            final_response = agent.run(user_input)
            
            # Trả kết quả cuối cùng ra màn hình
            print("\n🤖 Assistant:")
            print(f"{final_response}")
            print("\n" + "-"*50 + "\n")
            
        except KeyboardInterrupt:
            print("\n🤖 Chương trình bị ngắt bởi người dùng. Tạm biệt!")
            break
        except Exception as e:
            print(f"\n❌ Đã xảy ra lỗi hệ thống: {e}\n")


if __name__ == "__main__":
    main()