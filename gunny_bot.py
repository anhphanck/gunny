import pyautogui
import time
import os
import random

# ================== CẤU HÌNH ==================
TEMPLATE_DIR = "templates"
CONFIDENCE = 0.65

# Một phần tiêu đề cửa sổ game Gunny (không phân biệt hoa/thường).
# Bot sẽ tự đưa cửa sổ này lên trước để click/phím vào đúng game.
GAME_WINDOW_TITLE = "gunny"

# Vị trí click để nhân vật chạy 1 đoạn, tính theo TỈ LỆ trong cửa sổ game (0.0 - 1.0).
# 0.0 = mép trái/trên cửa sổ game, 1.0 = mép phải/dưới cửa sổ game.
# Nhờ vậy điểm click luôn nằm trong game dù cửa sổ ở đâu trên màn hình.
MOVE_CLICK_X_RATIO = 0.65
MOVE_CLICK_Y_RATIO = 0.40

# Góc ngắm mong muốn và góc mặc định mà game reset về đầu mỗi lượt.
# DEFAULT_ANGLE: sửa cho khớp đúng con số góc hiện ra khi bắt đầu lượt.
ANGLE_TARGET = 46
DEFAULT_ANGLE = 23

# Thời gian giữ Space tương ứng với lực 55 (bạn cân chỉnh).
POWER_HOLD_MIN = 2.25
POWER_HOLD_MAX = 2.45

SHOT_COUNT = 6          # số lần bắn mỗi lượt
SHOT_INTERVAL = 12     # giây giữa các lần bắn
SHOT2_DELAY = 15        # giây đợi sau lượt bắn thứ 2 (trước lượt 3)
SHOT3_DELAY = 15.5       # giây đợi sau lượt bắn thứ 3 (trước lượt 4)
SHOT4_DELAY = 15        # giây đợi sau lượt bắn thứ 4 (trước lượt 5)
SHOT5_DELAY = 15        # giây đợi sau lượt bắn thứ 5 (trước lượt 6)
LOAD_WAIT = 15           # giây đợi game load vào trận
DEATH_WAIT = 5         # giây đợi sau khi boss rồng giết nhân vật
KEY_PRESS_DELAY = 0.02  # delay giữa các lần bấm phím chỉnh góc

# Phím tắt dừng bot: Ctrl+C trong terminal hoặc di chuột về góc trên-trái màn hình
pyautogui.FAILSAFE = True

templates = {
    "boss_rong": os.path.join(TEMPLATE_DIR, "boss_rong.png")
}


def focus_game():
    """Đưa cửa sổ game Gunny lên trước, trả về đối tượng cửa sổ (hoặc None nếu lỗi)."""
    try:
        windows = pyautogui.getWindowsWithTitle(GAME_WINDOW_TITLE)
    except Exception as e:
        print(f"Không lấy được danh sách cửa sổ: {e}")
        return None

    if not windows:
        print(f"!! Không tìm thấy cửa sổ chứa tiêu đề '{GAME_WINDOW_TITLE}'.")
        print("!! Các cửa sổ đang mở:")
        try:
            for w in pyautogui.getAllWindows():
                if w.title.strip():
                    print(f"   - {w.title}")
        except Exception:
            pass
        print("!! Hãy sửa GAME_WINDOW_TITLE cho khớp.")
        return None

    win = windows[0]
    try:
        if win.isMinimized:
            win.restore()
            time.sleep(0.3)
        win.activate()
        time.sleep(0.5)
    except Exception as e:
        print(f"Không activate được cửa sổ game: {e}")

    if getattr(win, "isActive", True) is False:
        print("!! Cửa sổ game chưa lên trước. Hãy click tay vào game rồi chạy lại.")
        return None
    return win


def click_template(name, timeout=5, click=True, confidence=None):
    path = templates.get(name)
    if not path or not os.path.exists(path):
        return False

    search_confidence = confidence if confidence else CONFIDENCE

    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            locations = list(pyautogui.locateAllOnScreen(path, confidence=search_confidence, grayscale=True))
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


def set_angle(target):
    """Chỉnh góc ngắm từ DEFAULT_ANGLE về target bằng phím ↑ / ↓."""
    diff = target - DEFAULT_ANGLE
    key = "up" if diff > 0 else "down"
    for _ in range(abs(diff)):
        pyautogui.press(key)
        time.sleep(KEY_PRESS_DELAY)
    print(f"Đã chỉnh góc về {target}")


def move_to_boss(win):
    """Thấy boss rồng thì ấn vào boss luôn; chưa thấy mới click di chuyển để tìm."""
    x = win.left + int(win.width * MOVE_CLICK_X_RATIO)
    y = win.top + int(win.height * MOVE_CLICK_Y_RATIO)

    attempt = 0
    while True:
        # Ưu tiên ấn boss nếu đã thấy, không click di chuyển nữa
        if click_template("boss_rong", timeout=0.3, click=True):
            return True

        # Chưa thấy boss mới click di chuyển 1 đoạn để tìm
        attempt += 1
        print(f"[{attempt}] Chưa thấy boss, click di chuyển nhân vật tại ({x}, {y})...")
        pyautogui.moveTo(x, y, duration=0.2)
        pyautogui.click()
        time.sleep(0.5)  # cách 0,8 giây lại ấn di chuyển


def shoot_round():
    """Bắn SHOT_COUNT lần, mỗi lần cách nhau SHOT_INTERVAL giây."""
    for i in range(1, SHOT_COUNT + 1):
        print(f"--- Lượt bắn {i}/{SHOT_COUNT} ---")

        # Chỉ lượt đầu tiên mới quay sang phải và chỉnh góc
        if i == 1:
            print("Quay nhân vật sang phải...")
            pyautogui.press("right")
            time.sleep(0.3)

            set_angle(ANGLE_TARGET)
            time.sleep(0.3)

        # Chỉ lượt thứ 3 mới bấm 'e' trước
        if i == 3:
            print("Bấm phím 'e'...")
            pyautogui.press("e")
            time.sleep(0.3)

        # Lượt thứ 4 dùng combo b, 1, 4; các lượt khác dùng 1, 2, 4
        skills = ("b", "1", "4") if i == 4 else ("1", "2", "4")
        print(f"Dùng kỹ năng {', '.join(skills)}...")
        for skill in skills:
            pyautogui.press(skill)
            time.sleep(0.4)

        hold_time = random.uniform(POWER_HOLD_MIN, POWER_HOLD_MAX)
        print(f"Bắn lực 55 (giữ Space trong {hold_time:.2f}s)...")
        pyautogui.keyDown("space")
        time.sleep(hold_time)
        pyautogui.keyUp("space")

        if i < SHOT_COUNT:
            # Thời gian đợi riêng sau mỗi lượt bắn, còn lại dùng SHOT_INTERVAL
            delays = {
                2: SHOT2_DELAY,
                3: SHOT3_DELAY,
                4: SHOT4_DELAY,
                5: SHOT5_DELAY,
            }
            delay = delays.get(i, SHOT_INTERVAL)
            print(f"Đợi {delay}s cho lượt bắn tiếp theo...")
            time.sleep(delay)


def main():
    print("Tool Gunny Auto Boss Rồng Thế Giới - bắt đầu sau 5 giây...")
    print("Hãy mở cửa sổ game Gunny lên trước.")
    time.sleep(5)

    while True:
        print("=== Bắt đầu vòng lặp mới ===")
        win = focus_game()
        if win is None:
            print("Không thao tác được lên cửa sổ game, thử lại sau 5s...")
            time.sleep(5)
            continue
        move_to_boss(win)

        print(f"Đợi {LOAD_WAIT}s cho game load vào trận...")
        time.sleep(LOAD_WAIT)

        shoot_round()

        print(f"Đợi boss rồng giết và {DEATH_WAIT}s rồi lặp lại bước đầu...")
        time.sleep(DEATH_WAIT)


if __name__ == "__main__":
    # Tạo thư mục templates nếu chưa có
    if not os.path.exists(TEMPLATE_DIR):
        os.makedirs(TEMPLATE_DIR)
        print(f"Vui lòng bỏ các ảnh mẫu vào thư mục '{TEMPLATE_DIR}'")

    main()
