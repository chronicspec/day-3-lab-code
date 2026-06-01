import json
import random
import os

def generate_mock_data(output_dir="data"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Dữ liệu địa điểm cho nhiều thành phố
    spots_data = {
        "DaNang": [
            {"name": "Chùa Linh Ứng", "tags": ["accessible", "no_climbing"], "desc": "Tượng Phật lớn, cảnh biển đẹp."},
            {"name": "Bà Nà Hills", "tags": ["scenic", "climbing"], "desc": "Cáp treo dài, kiến trúc Pháp."}
        ],
        "HaNoi": [
            {"name": "Hồ Hoàn Kiếm", "tags": ["accessible", "cultural"], "desc": "Trái tim thủ đô, đi bộ thư giãn."},
            {"name": "Lăng Bác", "tags": ["cultural"], "desc": "Di tích lịch sử quan trọng."}
        ],
        "Hue": [
            {"name": "Đại Nội", "tags": ["cultural", "walking"], "desc": "Cung điện cổ kính, di sản thế giới."},
            {"name": "Chùa Thiên Mụ", "tags": ["accessible", "cultural"], "desc": "Biểu tượng tâm linh ven sông Hương."}
        ]
    }
    with open(f"{output_dir}/spots.json", "w", encoding="utf-8") as f:
        json.dump(spots_data, f, ensure_ascii=False, indent=4)

    # 2. Dữ liệu thời tiết cho các thành phố
    weather_data = {
        city: {
            "tomorrow": {"temp": random.randint(20, 35), "condition": random.choice(["Nắng", "Mưa nhẹ", "Mây"])},
            "day_after": {"temp": random.randint(20, 35), "condition": random.choice(["Nắng", "Mưa", "Dịu mát"])}
        }
        for city in ["DaNang", "HaNoi", "Hue", "PhuQuoc"]
    }
    with open(f"{output_dir}/weather.json", "w", encoding="utf-8") as f:
        json.dump(weather_data, f, ensure_ascii=False, indent=4)

    # 3. Dữ liệu xe và chi phí đa dạng
    cars_data = {
        "DaNang": [{"size": "7_seater", "price": 1200000}, {"size": "16_seater", "price": 1800000}],
        "HaNoi": [{"size": "4_seater", "price": 1000000}, {"size": "7_seater", "price": 1500000}],
        "Hue": [{"size": "7_seater", "price": 1000000}],
        "PhuQuoc": [{"size": "7_seater", "price": 1500000}]
    }
    with open(f"{output_dir}/cars.json", "w", encoding="utf-8") as f:
        json.dump(cars_data, f, ensure_ascii=False, indent=4)

    print(f"✅ Đã sinh dữ liệu mẫu đa dạng tại '{output_dir}/'")

if __name__ == "__main__":
    generate_mock_data()