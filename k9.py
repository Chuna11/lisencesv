"""Config - Unibot style. r0 duoc ma hoa XOR, khong doc duoc bang mat thuong."""
import json
import os
import sys

_CFG_KEY = b"RzStats-r0-cfg"
def _enc(b: bytes) -> bytes:
    k = _CFG_KEY
    return bytes((x ^ k[i % len(k)]) & 0xFF for i, x in enumerate(b))


def _get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _get_config_path():
    base = _get_base_dir()
    for name in ("r0", "r0.json"):
        p = os.path.join(base, name)
        if os.path.exists(p):
            return p
    if getattr(sys, "frozen", False) and getattr(sys, "_MEIPASS", None):
        p = os.path.join(sys._MEIPASS, "r0.json")
        if os.path.exists(p):
            return p
    return os.path.join(base, "r0")


CONFIG_PATH = None  # Set at runtime by load_config

# Valorant Enemy Highlight: Purple (Tritanopia) – glow tím
# HSV OpenCV: H 125–165 ( tím/magenta), S/V cao để loại đen/xám
DEFAULT_CONFIG = {
    "target_color": {"h_min": 125, "h_max": 165, "s_min": 100, "s_max": 255, "v_min": 100, "v_max": 255},
    "target_color_2": {"enabled": False, "h_min": 155, "h_max": 179, "s_min": 95, "s_max": 255, "v_min": 95, "v_max": 255},
    "offset_x": 0,
    "offset_y": 0,
    "aim_height": 0.85,
    "group_blobs": [3, 3],
    "aim_smoothing": 0.5,
    "aim_speed": 0.95,
    "fov_radius": 120,
    "show_fov_overlay": True,
    "smooth_aim": True,
    "enabled": False,
    "discreet_mode": False,
    "minimize_when_running": False,
    "aim_key": "none",
    "aim_key_2": "none",
    "input_method": "rzctl",
    "capture_method": "auto",
    "hw_serial_port": "",
    "human_strength": 0,
    "pro_style": True,
    "target_priority": "closest",
    "target_hold_frames": 25,
    "mouse_dpi": 800,
    "license_server": "",
}


def load_config():
    global CONFIG_PATH
    if CONFIG_PATH is None:
        CONFIG_PATH = _get_config_path()
    if os.path.exists(CONFIG_PATH):
        try:
            raw = open(CONFIG_PATH, "rb").read()
            if CONFIG_PATH.endswith(".json"):
                s = raw.decode("utf-8")
            else:
                s = _enc(raw).decode("utf-8")
            return {**DEFAULT_CONFIG, **json.loads(s)}
        except (json.JSONDecodeError, IOError, UnicodeDecodeError):
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config):
    global CONFIG_PATH
    if CONFIG_PATH is None:
        CONFIG_PATH = _get_config_path()
    save_path = os.path.join(_get_base_dir(), "r0")
    data = json.dumps(config, indent=2, ensure_ascii=False).encode("utf-8")
    open(save_path, "wb").write(_enc(data))
