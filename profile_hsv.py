"""
Script một lần để auto-profile HSV cho nhân vật trong FOV.

Cách dùng:
- Mở game, đứng nhìn thẳng vào địch glow tím (nhân vật bạn muốn profile màu).
- Đặt tâm (crosshair) sao cho địch nằm TRONG vòng FOV bạn đang dùng.
- Chạy script này (nên chạy khi aimbot đang TẮT / nút aim không được giữ).

Script sẽ:
- Capture vùng quanh tâm màn hình (giống aimbot).
- Gọi t1.profile_target_hsv để tìm contour người trong FOV.
- In ra gợi ý h_min/h_max/s_min/s_max/v_min/v_max.
Bạn copy các giá trị này vào web config (mục target_color).
"""

from m2 import get_screen_center
from n3 import capture_scan_region
from k9 import load_config, save_config
from t1 import profile_target_hsv


def main():
    cfg = load_config()
    cx, cy = get_screen_center()
    fov_radius = int(cfg.get("fov_radius", 150))

    frame, left, top = capture_scan_region(cx, cy, fov_radius)
    h, w = frame.shape[:2]

    # Tâm FOV trong toạ độ frame capture_scan_region
    center_x, center_y = w // 2, h // 2

    result = profile_target_hsv(frame, center_x, center_y, fov_radius)
    if not result:
        print("Không tìm được contour nhân vật trong FOV để profile HSV. Hãy đứng gần hơn hoặc tăng FOV.")
        return

    print("Gợi ý profile HSV cho nhân vật hiện tại:")
    print(
        f"h_min={result['h_min']}, h_max={result['h_max']}, "
        f"s_min={result['s_min']}, s_max={result['s_max']}, "
        f"v_min={result['v_min']}, v_max={result['v_max']}"
    )

    # Hỏi ý kiến người dùng có muốn ghi đè luôn vào config hay không.
    try:
        ans = input("Ghi các giá trị này vào target_color trong r0.json luôn? (y/N): ").strip().lower()
    except EOFError:
        ans = "n"

    if ans == "y":
        tc = cfg.get("target_color", {}).copy()
        tc.update(result)
        cfg["target_color"] = tc
        save_config(cfg)
        print("Đã lưu profile HSV mới vào config (r0.json). Mở lại web config sẽ thấy giá trị mới.")
    else:
        print("Không ghi file. Bạn có thể copy/paste giá trị vào web config bằng tay.")


if __name__ == "__main__":
    main()

