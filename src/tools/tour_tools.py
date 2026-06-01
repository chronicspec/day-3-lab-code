import re

def search_attractions(destination_and_tags: str) -> str:
    """
    Tìm kiếm các địa điểm tham quan phù hợp với điều kiện sức khỏe hoặc sở thích.
    Tham số: chuỗi chứa địa điểm và nhãn đặc biệt (ví dụ: 'danang, nguoi_gia, nhe_nhang')
    """
    text = destination_and_tags.lower()
    if "danang" in text or "đà nẵng" in text:
        if "người già" in text or "trẻ em" in text or "nhẹ nhàng" in text:
            return "Kết quả [search_attractions]: Bán đảo Sơn Trà (ngắm cảnh trên xe), Chùa Linh Ứng (đường phẳng), Phố cổ Hội An (đi bộ nhẹ nhàng buổi tối). Tiêu chí: Không leo bậc thang, lối đi bằng phẳng, ô tô tiếp cận sát cửa."
        return "Kết quả [search_attractions]: Bà Nà Hills, Bán đảo Sơn Trà, Cầu Rồng, Chợ Hàn."
    return f"Kết quả [search_attractions]: Các danh lam thắng cảnh nổi bật tại {destination_and_tags}."


def check_weather_forecast(city_and_date: str) -> str:
    """
    Kiểm tra dự báo thời tiết chi tiết của một thành phố để sắp xếp giờ khởi hành tránh nắng gắt/mưa.
    Tham số: tên thành phố và thời gian (ví dụ: 'danang, tomorrow')
    """
    text = city_and_date.lower()
    if "danang" in text or "đà nẵng" in text:
        return "Kết quả [check_weather_forecast]: Dự báo thời tiết ngày mai có Nắng gắt (nhiệt độ từ 36°C-38°C) trong khung giờ từ 10h30 đến 15h00. Đầu buổi sáng và cuối chiều trời dịu mát (28°C)."
    return f"Kết quả [check_weather_forecast]: Thời tiết tại {city_and_date} có nắng nhẹ, nhiệt độ trung bình 30°C."


def calculate_tour_budget(args_str: str) -> str:
    """
    Tính toán chi phí dự tính cho tour bao gồm giá thuê xe đưa đón riêng và vé tham quan trọn gói.
    Tham số: định dạng chuỗi (ví dụ: 'pax=6, car=7_seater')
    """
    # Trích xuất số lượng khách (pax) từ chuỗi
    pax = 6
    pax_match = re.search(r'pax=(\d+)', args_str)
    if pax_match:
        pax = int(pax_match.group(1))
        
    # Chọn loại xe phù hợp dựa trên số lượng khách hoặc yêu cầu
    car_type = "16_seater" if pax > 6 else "7_seater"
    car_cost = 2000000 if car_type == "16_seater" else 1200000
    
    # Vé tham quan giả định (ví dụ vé Hội An: 80k/người)
    ticket_cost = pax * 80000
    total = car_cost + ticket_cost
    
    return f"Kết quả [calculate_tour_budget]: Thuê xe {car_type} trọn gói 1 ngày kèm tài xế: {car_cost:,} VNĐ. Vé vào cửa ({pax} người): {ticket_cost:,} VNĐ. Tổng chi phí cố định: {total:,} VNĐ."