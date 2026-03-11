"""
Lấy tọa độ màn hình chính xác - tránh lệch do DPI scaling.
Dùng mss để đảm bảo capture và chuột dùng cùng hệ tọa độ.
"""
import ctypes

# Đặt DPI awareness ngay khi import (trước khi tạo window)
def _set_dpi_aware():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
    except (AttributeError, OSError):
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except (AttributeError, OSError):
            pass

_set_dpi_aware()


def _get_primary_monitor():
    """Lấy thông tin màn hình chính (monitors[1] = primary, fallback monitors[0])."""
    import mss
    with mss.mss() as sct:
        mons = sct.monitors
        return mons[1] if len(mons) > 1 else mons[0]


def get_screen_center():
    """Lấy tâm màn hình chính (tọa độ thực, phù hợp mss + chuột)."""
    mon = _get_primary_monitor()
    left, top = mon["left"], mon["top"]
    w, h = mon["width"], mon["height"]
    return left + w // 2, top + h // 2
