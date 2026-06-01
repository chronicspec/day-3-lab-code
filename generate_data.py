import json
import random
import os

# Cấu hình dữ liệu giả lập
spots = [
    {"name": "Chùa Linh Ứng", "tags": ["accessible", "no_climbing"], "desc": "Địa điểm tâm linh, đường đi bằng phẳng."},
    {"name": "Phố cổ Hội An", "tags": ["accessible", "cultural"], "desc": "Khu phố đi bộ, thuận tiện cho người già."},
    {"name": "Bán đảo Sơn Trà", "tags": ["scenic", "driving"], "desc": "Ngắm cảnh từ trên xe, phù hợp gia đình."},
    {"name": "Bà Nà Hills", "tags": ["scenic", "climbing"], "desc": "Cần đi cáp treo, phù hợp nếu không ngại độ cao."},
    {"name": "Cầu Rồng", "tags": ["accessible", "nightlife"], "desc": "Ngắm cảnh đêm, đường rộng rãi."}
]

weather_conditions = ["Nắng gắt", "Dịu mát", "Có mưa nhẹ", "Nhiều mây"]

def generate_mock_data(output_dir="data"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Sinh file spots.json
    with open(f"{output_dir}/spots.json", "w", encoding="utf-8") as f:
        json.dump(spots, f, ensure_ascii=False, indent=4)
    
    # 2. Sinh file weather.json
    weather_data = {
        "DaNang": {
            "tomorrow": {"temp": random.randint(28, 38), "condition": random.choice(weather_conditions)},
            "day_after": {"temp": random.randint(28, 38), "condition": random.choice(weather_conditions)}
        }
    }
    with open(f"{output_dir}/weather.json", "w", encoding="utf-8") as f:
        json.dump(weather_data, f, ensure_ascii=False, indent=4)

    # 3. Sinh file cars.json
    cars_data = [
        {"size": "4_seater", "price": 800000, "note": "Tiết kiệm"},
        {"size": "7_seater", "price": 1200000, "note": "Phù hợp gia đình, có ghế em bé"},
        {"size": "16_seater", "price": 1800000, "note": "Cho đoàn đông người"}
    ]
    with open(f"{output_dir}/cars.json", "w", encoding="utf-8") as f:
        json.dump(cars_data, f, ensure_ascii=False, indent=4)

    print(f"✅ Đã sinh dữ liệu mẫu tại thư mục '{output_dir}/'")

if __name__ == "__main__":
    generate_mock_data()