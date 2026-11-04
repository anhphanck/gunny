import pyautogui
import os
import time
from PIL import Image

def capture_template(name):
    print(f"\n--- Chuẩn bị chụp ảnh cho: {name} ---")
    print(f"HÃY MỞ GAME đến màn hình có nút '{name}'")
    print("Khi đã sẵn sàng, nhấn Enter tại đây để bắt đầu đếm ngược 5 giây...")
    input()
    
    print(f"1. Di chuyển chuột đến góc TRÊN-TRÁI của nút '{name}'")
    for i in range(5, 0, -1):
        print(f"Sẽ ghi nhận sau {i}...")
        time.sleep(1)
    x1, y1 = pyautogui.position()
    print(f"-> Đã ghi nhận Góc 1: {x1}, {y1}")
    
    print(f"\n2. Di chuyển chuột đến góc DƯỚI-PHẢI của nút '{name}'")
    for i in range(5, 0, -1):
        print(f"Sẽ ghi nhận sau {i}...")
        time.sleep(1)
    x2, y2 = pyautogui.position()
    print(f"-> Đã ghi nhận Góc 2: {x2}, {y2}")
    
    x_start = min(x1, x2)
    y_start = min(y1, y2)
    width = abs(x2 - x1)
    height = abs(y2 - y1)
    
    if width < 2 or height < 2:
        print("Lỗi: Vùng chọn quá nhỏ! Vui lòng thử lại nút này.")
        return False
    
    screenshot = pyautogui.screenshot(region=(x_start, y_start, width, height))
    path = os.path.join("templates", f"{name}.png")
    screenshot.save(path)
    print(f"--- Đã lưu Xong: {path} ---")
    return True

def main():
    if not os.path.exists("templates"):
        os.makedirs("templates")
        
    template_list = [
        "sua_thong_tin",
        "pho_ban_don",
        "dung_si_5",
        "anh_hung",
        "dong_y",
        "bat_dau",
        "luot_cua_toi",
        "ket_thuc"
    ]
    
    print("Tool hỗ trợ chụp ảnh mẫu cho Gunny Auto")
    print("Mở game lên và chuẩn bị sẵn màn hình tương ứng.")
    
    for t in template_list:
        success = False
        while not success:
            success = capture_template(t)
            if not success:
                print("Thử lại...")
    
    print("\nĐã chụp xong tất cả ảnh mẫu! Bây giờ bạn có thể chạy gunny_bot.py")

if __name__ == "__main__":
    main()
