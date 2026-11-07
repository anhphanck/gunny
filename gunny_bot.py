import pyautogui
import time
import cv2
import numpy as np
import os
import random

# Cấu hình
TEMPLATE_DIR = "templates"
CONFIDENCE = 0.8  # Giảm xuống 0.8 để bot dễ tìm thấy nút hơn
POWER_65_MIN = 2.35  # Lực bắn tối thiểu (thời gian giữ Space)
POWER_65_MAX = 2.55  # Lực bắn tối đa (thời gian giữ Space)
FAILSAFE_CORNER = (0, 0)

# Phím tắt dừng bot: Ctrl+C trong terminal hoặc di chuyển chuột về góc màn hình
pyautogui.FAILSAFE = True

templates = {
    "sua_thong_tin": os.path.join(TEMPLATE_DIR, "sua_thong_tin.png"),
    "pho_ban_don": os.path.join(TEMPLATE_DIR, "pho_ban_don.png"),
    "dung_si_5": os.path.join(TEMPLATE_DIR, "dung_si_5.png"),
    "anh_hung": os.path.join(TEMPLATE_DIR, "anh_hung.png"),
    "dong_y": os.path.join(TEMPLATE_DIR, "dong_y.png"),
    "bat_dau": os.path.join(TEMPLATE_DIR, "bat_dau.png"),
    "luot_cua_toi": os.path.join(TEMPLATE_DIR, "luot_cua_toi.png"),
    "ket_thuc": os.path.join(TEMPLATE_DIR, "ket_thuc.png")
}

def click_template(name, timeout=5, click=True, grayscale=True, confidence=None):
    path = templates.get(name)
    if not path or not os.path.exists(path):
        return False
    
    # Sử dụng confidence mặc định nếu không truyền vào
    search_confidence = confidence if confidence else CONFIDENCE
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            locations = list(pyautogui.locateAllOnScreen(path, confidence=search_confidence, grayscale=grayscale))
            for loc in locations:
                center = pyautogui.center(loc)
                if center.x < 200 and center.y < 200:
                    continue
                if click:
                    print(f"Tìm thấy {name} tại: ({center.x}, {center.y})")
                    pyautogui.moveTo(center.x, center.y, duration=0.3)
                    pyautogui.click()
                    time.sleep(1)
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False

def wait_for_my_turn(timeout=60):
    print("Đang đợi đến lượt...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        # Giảm confidence xuống 0.7 riêng cho lượt đánh để nhạy hơn
        if click_template("luot_cua_toi", timeout=1, click=False, confidence=0.7):
            return True
        if click_template("ket_thuc", timeout=1, click=False):
            return False
        time.sleep(0.5)
    return False

def extra_fire(max_turns=3):
    """Bắn bồi thêm 3 lượt (ấn b, e, 1, 4) khi boss vẫn chưa chết."""
    for i in range(1, max_turns + 1):
        print(f"Bắn thêm lượt {i}/{max_turns}: ấn 'b', 'e', '1', '4'...")
        pyautogui.press('b')
        time.sleep(0.3)
        pyautogui.press('e')
        time.sleep(0.3)
        pyautogui.press('1')
        time.sleep(0.5)
        pyautogui.press('4')
        time.sleep(0.5)
        time.sleep(0.5)

        hold_time = random.uniform(POWER_65_MIN, POWER_65_MAX)
        print(f"Bắn lực 65 (giữ Space trong {hold_time:.2f}s)...")
        pyautogui.keyDown('space')
        time.sleep(hold_time)
        pyautogui.keyUp('space')

        if i < max_turns:
            delay = 9
            print(f"Đợi {delay} giây cho lượt bắn bồi tiếp theo...")
            time.sleep(delay)
    return max_turns

def setup_room():
    print("--- Đang thiết lập phòng ---")
    found = click_template("sua_thong_tin")
    if not found:
        # Không thấy nút 'Sửa thông tin' => boss chưa chết, vẫn đang trong trận.
        print("=> Không tìm thấy nút 'Sửa thông tin' (boss chưa chết, vẫn trong trận).")
        print("=> Bắn bồi thêm 3 lượt (ấn 'b', 'e', '1', '4')...")
        extra_fire()
        print("Đã bắn thêm. Đợi 18s để nhận thưởng và quay lại phòng...")
        time.sleep(18)
        found = click_template("sua_thong_tin")
    if not found:
        print("=> Lỗi: Không tìm thấy nút 'Sửa thông tin'")
        return False
    time.sleep(1.5)
    
    if not click_template("pho_ban_don"): 
        print("=> Lỗi: Không tìm thấy tab 'Phó bản đơn'")
        return False
    time.sleep(1)
    
    if not click_template("dung_si_5"): 
        print("=> Cảnh báo: Không tìm thấy phó bản 'Dũng sĩ luyện tập 5'. Bỏ qua và ấn 'Đồng ý' luôn...")
    else:
        time.sleep(1)
        
        if not click_template("anh_hung"): 
            print("=> Lỗi: Không tìm thấy nút mức độ 'Anh Hùng'")
            return False
        time.sleep(1)
    
    if not click_template("dong_y"): 
        print("=> Lỗi: Không tìm thấy nút 'Đồng ý'")
        return False
    
    print("Thiết lập phòng xong. Đợi 2s...")
    time.sleep(2)
    return True

def fight():
    print("Bấm nút Bắt đầu...")
    if not click_template("bat_dau"): 
        if not click_template("bat_dau", timeout=10):
            return False
    
    print("Đang đợi game load vào trận (13s)...")
    time.sleep(13) 
    
    # Thực hiện bắn 5 lần với thời gian giãn cách tùy chỉnh
    for i in range(1, 6):
        print(f"Thực hiện lượt bắn thứ {i}/5...")
        
        # Nếu là lần bắn thứ 3, nhấn thêm phím 'e' trước
        if i == 3:
            print("Lần bắn thứ 3: Nhấn phím 'e' trước...")
            pyautogui.press(['e', 'c'])
            time.sleep(0.25)
            
        print("Sử dụng kỹ năng 1, 2, 4...")
        pyautogui.press('1')
        time.sleep(0.5)
        pyautogui.press('2')
        time.sleep(0.5)
        pyautogui.press('4')
        time.sleep(0.5)
        
        time.sleep(0.5)
        
        hold_time = random.uniform(POWER_65_MIN, POWER_65_MAX)
        print(f"Bắn lực 65 (giữ Space trong {hold_time:.2f}s)...")
        pyautogui.keyDown('space')
        time.sleep(hold_time)
        pyautogui.keyUp('space')
        
        if i < 5:
            # Thời gian giãn cách mặc định ngẫu nhiên 11-12s
            delay = random.uniform(11, 12)
            if i == 2:
                delay = 14 # Lượt 3 thêm 2s (11+2)
            elif i == 3:
                delay = 14 # Lượt 4 thêm 1s (13+1)
                
            print(f"Đợi {delay:.2f} giây cho lượt tiếp theo...")
            time.sleep(delay)
    
    print("Đã bắn xong 5 lần. Đợi 18s để nhận thưởng và quay lại phòng...")
    time.sleep(18) 
    return True
    
    print("Trận đấu quá lâu, tự động thoát...")
    return False

def main():
    print("Tool Gunny PC Auto Start in 5 seconds...")
    time.sleep(5)
    
    while True:
        print("--- Bắt đầu vòng lặp mới ---")
        if setup_room():
            fight()
        else:
            print("Lỗi thiết lập phòng, thử lại sau 5s...")
            time.sleep(5)

if __name__ == "__main__":
    # Tạo thư mục templates nếu chưa có
    if not os.path.exists(TEMPLATE_DIR):
        os.makedirs(TEMPLATE_DIR)
        print(f"Vui lòng bỏ các ảnh mẫu vào thư mục '{TEMPLATE_DIR}'")
    
    main()
