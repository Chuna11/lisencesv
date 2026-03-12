"""
Phát hiện địch theo Unibot - https://github.com/vike256/Unibot
Màu mặc định: Valorant Purple (Tritanopia) – glow tím. HSV H 125–165, S/V cao.
HSV inRange → dilation → contours → chọn mục tiêu gần tâm nhất.
"""
import cv2
import numpy as np


def detect(
    frame,
    h_min,
    h_max,
    s_min,
    s_max,
    v_min,
    v_max,
    center_x,
    center_y,
    fov_radius,
    color_ranges_extra=None,
    group_blobs=None,
    aim_height=0.85,
    priority="closest",
):
    """
    Phát hiện địch theo Unibot. Trả về (aim_x, aim_y) trong frame hoặc None.
    aim_height=0.85 → nhắm đầu (15% từ trên), 0.5 → giữa.
    """
    if frame is None or frame.size == 0:
        return None
    denoised = cv2.medianBlur(frame, 3)
    hsv = cv2.cvtColor(denoised, cv2.COLOR_BGR2HSV)
    # Loại đen/xám (chân, bóng): S và V phải đủ cao – glow tím sáng có S,V cao
    s_min = max(s_min, 90)
    v_min = max(v_min, 95)
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    mask = cv2.inRange(hsv, lower, upper)
    if color_ranges_extra:
        for hmn, hmx, smn, smx, vmn, vmx in color_ranges_extra:
            smn, vmn = max(smn, 90), max(vmn, 95)
            m2 = cv2.inRange(hsv, np.array([hmn, smn, vmn]), np.array([hmx, smx, vmx]))
            mask = cv2.bitwise_or(mask, m2)
    # FOV hình tròn: chỉ detect trong vòng tròn bán kính fov_radius
    h, w = mask.shape[:2]
    yg, xg = np.ogrid[:h, :w]
    circle_mask = ((xg - center_x) ** 2 + (yg - center_y) ** 2) <= (fov_radius ** 2)
    mask = cv2.bitwise_and(mask, np.where(circle_mask, 255, 0).astype(np.uint8))
    kx, ky = (3, 3)
    if group_blobs and isinstance(group_blobs, (list, tuple)) and len(group_blobs) >= 2:
        kx, ky = max(1, int(group_blobs[0])), max(1, int(group_blobs[1]))
    kernel = np.ones((kx, ky), np.uint8)
    dilated = cv2.dilate(mask, kernel, iterations=5)
    thresh = cv2.threshold(dilated, 60, 255, cv2.THRESH_BINARY)[1]
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    aim_height = max(0.01, min(0.99, float(aim_height or 0.85)))
    best = None
    best_score = float("inf")
    priority = (priority or "closest").lower()
    for contour in contours:
        rect_x, rect_y, rect_w, rect_h = cv2.boundingRect(contour)
        if rect_w < 4 or rect_h < 4:
            continue
        area = rect_w * rect_h
        if area < 35:
            continue
        aim_x = rect_x + rect_w // 2
        frac = (1.0 - aim_height) * 0.80
        aim_y = int(rect_y + rect_h * frac)
        dist = np.sqrt((aim_x - center_x) ** 2 + (aim_y - center_y) ** 2)
        if dist > fov_radius:
            continue
        if priority == "largest":
            score = -area
        elif priority == "highest":
            score = -aim_y
        elif priority == "lowest":
            score = aim_y
        elif priority == "closest_largest":
            score = dist - 0.001 * area
        else:  # "closest"
            score = dist

        if score < best_score:
            best_score = score
            best = (aim_x, aim_y)
    return best


def profile_target_hsv(frame, center_x, center_y, fov_radius, **_kw):
    """Profile HSV của mục tiêu gần tâm (Unibot). Trả về dict h_min/h_max/... hoặc None."""
    pt = detect(frame, 110, 179, 40, 255, 60, 255, center_x, center_y, fov_radius, aim_height=0.5)
    if pt is None:
        return None
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    x, y = pt
    r = 15
    h0, h1 = max(0, y - r), min(frame.shape[0], y + r)
    w0, w1 = max(0, x - r), min(frame.shape[1], x + r)
    roi = hsv[h0:h1, w0:w1]
    if roi.size == 0:
        return None
    px = roi.reshape(-1, 3)
    return {
        "h_min": int(np.percentile(px[:, 0], 5)),
        "h_max": int(np.percentile(px[:, 0], 95)),
        "s_min": int(np.percentile(px[:, 1], 5)),
        "s_max": 255,
        "v_min": int(np.percentile(px[:, 2], 5)),
        "v_max": 255,
    }
