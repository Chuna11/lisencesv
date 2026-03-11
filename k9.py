"""Config - Unibot style"""
import json
import os
import sys


def _get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


CONFIG_PATH = os.path.join(_get_base_dir(), "r0.json")

# Valorant Enemy Highlight: Purple (Tritanopia) – glow tím
# HSV OpenCV: H 125–165 ( tím/magenta), S/V cao để loại đen/xám
DEFAULT_CONFIG = {
    "target_color": {"h_min": 125, "h_max": 165, "s_min": 100, "s_max": 255, "v_min": 100, "v_max": 255},
    "target_color_2": {"enabled": False, "h_min": 155, "h_max": 179, "s_min": 95, "s_max": 255, "v_min": 95, "v_max": 255},
    "offset_x": 0,
    "offset_y": 0,
    "aim_height": 0.85,
    "group_blobs": [3, 3],
    "aim_smoothing": 0.7,
    "aim_speed": 0.75,
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
    "target_priority": "closest",
    "target_hold_frames": 12,
    "mouse_dpi": 800,
    "license_server": "",
}


def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
