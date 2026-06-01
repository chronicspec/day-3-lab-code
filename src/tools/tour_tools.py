import re
import json
import os

# Đường dẫn đến thư mục chứa data (đảm bảo file chạy của bạn ở cấp cha của thư mục data)
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')

def search_attractions(args_str: str) -> str:
    city_match = re.search(r'city=["\']([^"\']+)["\']', args_str)
    tags_match = re.search(r'tags=["\']([^"\']+)["\']', args_str)
    
    city = city_match.group(1).capitalize() if city_match else ""
    tags = tags_match.group(1).split(",") if tags_match else []

    try:
        with open(os.path.join(DATA_DIR, 'spots.json'), 'r', encoding='utf-8') as f:
            spots_db = json.load(f)
        
        # Tìm danh sách địa điểm theo thành phố
        city_spots = spots_db.get(city, [])
        # Lọc theo tags
        results = [s['name'] for s in city_spots if any(t in s['tags'] for t in tags)]
        
        if not results:
            return f"Không tìm thấy địa điểm phù hợp với tags {tags} tại {city}."
        return f"Các điểm tham quan gợi ý tại {city}: {', '.join(results)}"
    except Exception as e:
        return f"Lỗi truy xuất dữ liệu địa điểm: {str(e)}"

def check_weather_forecast(args_str: str) -> str:
    city_match = re.search(r'city=["\']([^"\']+)["\']', args_str)
    city = city_match.group(1).capitalize() if city_match else "DaNang"

    try:
        with open(os.path.join(DATA_DIR, 'weather.json'), 'r', encoding='utf-8') as f:
            weather = json.load(f)
        
        data = weather.get(city, {}).get("tomorrow", {})
        if not data:
            return f"Không có dữ liệu thời tiết cho {city}."
        return f"Thời tiết tại {city} ngày mai: {data.get('condition', 'N/A')}, nhiệt độ {data.get('temp', 'N/A')}°C."
    except Exception as e:
        return f"Lỗi truy xuất thời tiết: {str(e)}"

def calculate_tour_budget(args_str: str) -> str:
    pax_match = re.search(r'pax=(\d+)', args_str)
    car_match = re.search(r'car=["\']?([^"\']+)["\']?', args_str)
    city_match = re.search(r'city=["\']?([^"\']+)["\']?', args_str)
    
    pax = int(pax_match.group(1)) if pax_match else 6
    car_type = car_match.group(1) if car_match else "7_seater"
    city = city_match.group(1).capitalize() if city_match else "DaNang"
    
    try:
        with open(os.path.join(DATA_DIR, 'cars.json'), 'r', encoding='utf-8') as f:
            cars_db = json.load(f)
        
        # Lấy giá xe theo thành phố
        city_cars = cars_db.get(city, [])
        car_info = next((c for c in city_cars if c['size'] == car_type), None)
        
        if not car_info:
            return f"Không tìm thấy thông tin xe {car_type} tại {city}."
            
        car_cost = car_info['price']
        ticket_cost = pax * 80000
        total = car_cost + ticket_cost
        
        return f"Tại {city}: Xe {car_type} giá {car_cost:,} VNĐ. Vé ({pax} khách): {ticket_cost:,} VNĐ. Tổng: {total:,} VNĐ."
    except Exception as e:
        return f"Lỗi tính toán ngân sách: {str(e)}"