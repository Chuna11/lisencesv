"""
Quản lý phím tắt - chỉ aim khi giữ phím (nếu có thiết lập)
Dùng GetAsyncKeyState (Windows) để kiểm tra phím - hoạt động ngay cả khi game có focus.
"""
import ctypes

user32 = ctypes.windll.user32
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12  # Alt
VK_CAPITAL = 0x14  # Caps Lock
VK_LBUTTON = 0x01  # Chuột trái
VK_RBUTTON = 0x02  # Chuột phải
VK_XBUTTON1 = 0x05  # Nút chuột 4
VK_XBUTTON2 = 0x06  # Nút chuột 5

AIM_KEY_OPTIONS = [
    ("Luôn bật (không cần giữ phím)", "none"),
    ("Shift", "shift"),
    ("Ctrl", "ctrl"),
    ("Alt", "alt"),
    ("Caps Lock", "capslock"),
    ("Chuột trái", "mouse1"),
    ("Chuột phải", "mouse2"),
    ("Nút chuột 4 (bên trái)", "mouse4"),
    ("Nút chuột 5 (bên phải)", "mouse5"),
]

VK_MAP = {
    "shift": (VK_SHIFT,),
    "ctrl": (VK_CONTROL,),
    "alt": (VK_MENU,),
    "capslock": (VK_CAPITAL,),
    "mouse1": (VK_LBUTTON,),
    "mouse2": (VK_RBUTTON,),
    "mouse4": (VK_XBUTTON1,),
    "mouse5": (VK_XBUTTON2,),
}


class HotkeyManager:
    def __init__(self):
        self._aim_key = "none"
        self._aim_key_2 = "none"

    def set_aim_key(self, key_name):
        """key_name: 'none', 'shift', 'ctrl', 'alt', 'capslock', 'mouse1', 'mouse2', 'mouse4', 'mouse5'"""
        self._aim_key = (key_name or "none").strip().lower()

    def set_aim_key_2(self, key_name):
        """Phím thứ 2 - aim khi giữ 1 TRONG 2 phím. Để 'none' nếu không dùng."""
        self._aim_key_2 = (key_name or "none").strip().lower()

    def is_aim_active(self):
        """True nếu aim nên hoạt động - dùng GetAsyncKeyState (hoạt động khi game có focus)"""
        # Nếu Phím 1 = none → luôn bật (hành vi cũ)
        if self._aim_key == "none":
            return True

        def _pressed(key_name: str) -> bool:
            if not key_name or key_name == "none":
                return False
            vk_codes = VK_MAP.get(key_name)
            if not vk_codes:
                return False
            return any(user32.GetAsyncKeyState(vk) & 0x8000 for vk in vk_codes)

        # Chỉ cần giữ 1 trong 2 phím (OR)
        return _pressed(self._aim_key) or _pressed(self._aim_key_2)

    def start_listeners(self):
        pass

    def stop_listeners(self):
        pass
