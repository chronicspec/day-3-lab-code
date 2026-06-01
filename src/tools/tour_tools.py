import re
import json
import os

def search_attractions(args_str: str) -> str:
    """
    Search format: search_attractions(city="DaNang", tags="accessible,no_climbing")
    """
    # Regex để trích xuất tham số từ chuỗi Action (ví dụ: city="DaNang")
    city_match = re.search(r'city=["\']([^"\']+)["\']', args_str)
    tags_match = re.search(r'tags=["\']([^"\']+)["\']', args_str)
    
    city = city_match.group(1) if city_match else "unknown"
    tags = tags_match.group(1).split(",") if tags_match else []

    # Logic: Giả lập đọc từ dữ liệu hoặc trả về kết quả cấu trúc
    if "danang" in city.lower():
        if "accessible" in tags or "no_climbing" in tags:
            return "Bán đảo Sơn Trà (ngắm cảnh từ xe), Chùa Linh Ứng (đường phẳng), Phố cổ Hội An (đi bộ)."
        return "Bà Nà Hills, Bán đảo Sơn Trà, Cầu Rồng, Chợ Hàn."
    
    return f"Không có dữ liệu địa điểm cho {city}."

def check_weather_forecast(args_str: str) -> str:
    """
    Check format: check_weather_forecast(city="DaNang", date="tomorrow")
    """
    city_match = re.search(r'city=["\']([^"\']+)["\']', args_str)
    city = city_match.group(1).lower() if city_match else ""

    if "danang" in city:
        return "Nắng gắt (36°C-38°C) từ 10h30-15h00. Đầu sáng và cuối chiều trời dịu mát (28°C)."
    return "Thời tiết ổn định, nhiệt độ trung bình 30°C."

def calculate_tour_budget(args_str: str) -> str:
    """
    Budget format: calculate_tour_budget(pax=6, car="7_seater")
    """
    pax_match = re.search(r'pax=(\d+)', args_str)
    car_match = re.search(r'car=["\']([^"\']+)["\']', args_str)
    
    pax = int(pax_match.group(1)) if pax_match else 1
    car_type = car_match.group(1) if car_match else "7_seater"
    
    # Logic tính toán
    car_cost = 1_200_000 if car_type == "7_seater" else 2_000_000
    ticket_cost = pax * 80_000
    total = car_cost + ticket_cost
    
    return f"Xe {car_type}: {car_cost:,} VNĐ. Vé tham quan ({pax} khách): {ticket_cost:,} VNĐ. Tổng: {total:,} VNĐ."