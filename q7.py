"""
ColorAim - Unibot only. Phát hiện địch + aim theo https://github.com/vike256/Unibot
Chạy nền, cấu hình qua web http://127.0.0.1:5873
"""
try:
    import setproctitle  # type: ignore[reportMissingImports]
    setproctitle.setproctitle("RzStats")
except Exception:
    pass
import os
import subprocess
import sys
import ctypes


def _is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def _hide_console():
    try:
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        pass


def _run_as_admin():
    if not _is_admin():
        try:
            if getattr(sys, "frozen", False):
                exe = sys.executable
                params = subprocess.list2cmdline(sys.argv[1:]) if sys.argv[1:] else ""
                cwd = os.path.dirname(exe)
                target = exe
            else:
                script = os.path.abspath(sys.argv[0])
                params = subprocess.list2cmdline([script] + sys.argv[1:])
                cwd = os.path.dirname(script)
                target = sys.executable
            ret = ctypes.windll.shell32.ShellExecuteW(None, "runas", target, params, cwd, 1)
            if ret > 32:
                sys.exit(0)
        except Exception:
            pass


import m2  # noqa: F401
import threading
import time
import tkinter as tk
import winsound

from k9 import load_config, save_config
from license_key import require_license
from p4 import HotkeyManager
from t1 import detect
from w6 import move_mouse_to
from n3 import capture_scan_region
from v8 import FOVOverlay

WEB_PORT = 5873
VK_DELETE = 0x2E

# Delete toggle: bắt buộc reload config ngay
_config_invalidated = {"v": False}
_user32 = ctypes.windll.user32


def _toggle_enabled_loop():
    """Thread: phím Delete → toggle enabled, bíp 0.3s."""
    last_pressed = False
    while True:
        try:
            pressed = (_user32.GetAsyncKeyState(VK_DELETE) & 0x8000) != 0
            if pressed and not last_pressed:
                cfg = load_config()
                cfg["enabled"] = not cfg.get("enabled", False)
                save_config(cfg)
                _config_invalidated["v"] = True
                try:
                    winsound.Beep(800, 300)
                except Exception:
                    pass
            last_pressed = pressed
        except Exception:
            pass
        time.sleep(0.05)


def _set_low_priority():
    try:
        kernel32 = ctypes.windll.kernel32
        kernel32.SetPriorityClass(kernel32.GetCurrentProcess(), 0x4000)
    except Exception:
        pass


def _aim_loop(overlay, hotkey_manager):
    from m2 import get_screen_center

    last_smoothed = None
    last_target = None
    raw_history = []
    target_hold_frames = 0
    SMOOTH = 0.7
    AIM_SPD = 0.75
    cfg_cache = None
    cfg_cache_time = 0
    CONFIG_RELOAD_MS = 120

    while True:
        try:
            now_ms = time.perf_counter() * 1000
            if cfg_cache is None or (now_ms - cfg_cache_time) > CONFIG_RELOAD_MS or _config_invalidated["v"]:
                cfg_cache = load_config()
                cfg_cache_time = now_ms
                _config_invalidated["v"] = False
            cfg = cfg_cache
            if cfg.get("discreet_mode", False):
                _set_low_priority()

            enabled = cfg.get("enabled", False)
            show_fov = cfg.get("show_fov_overlay", True)

            if enabled and show_fov:
                try:
                    cx, cy = get_screen_center()
                    fov_r = max(1, int(cfg.get("fov_radius", 150)))
                    overlay.update_radius(fov_r, cx, cy)
                    overlay.show(cx, cy)
                except Exception:
                    pass
            else:
                overlay.hide()

            hotkey_manager.set_aim_key(cfg.get("aim_key", "none"))
            hotkey_manager.set_aim_key_2(cfg.get("aim_key_2", "none"))
            aim_active = enabled and hotkey_manager.is_aim_active()

            if enabled and aim_active:
                center_x, center_y = get_screen_center()
                fov_radius = max(1, int(cfg.get("fov_radius", 150)))
                frame, left, top = capture_scan_region(
                    center_x, center_y, fov_radius,
                    capture_method=cfg.get("capture_method", "auto")
                )
                h, w = frame.shape[:2]
                size = max(200, int(fov_radius * 2.5))
                fov_cx, fov_cy = w // 2, h // 2

                tc = cfg.get("target_color", {})
                tc2 = cfg.get("target_color_2") or {}
                extra = []
                if tc2.get("enabled", False):
                    extra.append((
                        tc2.get("h_min", 155), tc2.get("h_max", 179),
                        tc2.get("s_min", 80), tc2.get("s_max", 255),
                        tc2.get("v_min", 100), tc2.get("v_max", 255),
                    ))

                point = detect(
                    frame,
                    tc.get("h_min", 125), tc.get("h_max", 165),
                    tc.get("s_min", 100), tc.get("s_max", 255),
                    tc.get("v_min", 100), tc.get("v_max", 255),
                    fov_cx, fov_cy, fov_radius,
                    color_ranges_extra=extra if extra else None,
                    group_blobs=cfg.get("group_blobs", [3, 3]),
                    aim_height=cfg.get("aim_height", 0.85),
                    priority=cfg.get("target_priority", "closest"),
                )

                if point:
                    raw_x = left + point[0]
                    raw_y = top + point[1]
                    last_target = (raw_x, raw_y)
                    target_hold_frames = int(cfg.get("target_hold_frames", 12))
                elif last_target and target_hold_frames > 0:
                    raw_x, raw_y = last_target
                    target_hold_frames -= 1
                    point = (raw_x - left, raw_y - top)
                else:
                    last_target = None
                    point = None

                if point and hotkey_manager.is_aim_active():
                    raw_history.append((raw_x, raw_y))
                    if len(raw_history) > 3:
                        raw_history.pop(0)
                    xs = sorted([p[0] for p in raw_history])
                    ys = sorted([p[1] for p in raw_history])
                    avg_x, avg_y = xs[len(xs) // 2], ys[len(ys) // 2]
                    sm = float(cfg.get("aim_smoothing", SMOOTH))
                    if last_smoothed is None:
                        tx, ty = avg_x, avg_y
                    else:
                        tx = (1 - sm) * last_smoothed[0] + sm * avg_x
                        ty = (1 - sm) * last_smoothed[1] + sm * avg_y
                    last_smoothed = (tx, ty)
                    aim_spd = float(cfg.get("aim_speed", AIM_SPD))
                    dpi = max(200, int(cfg.get("mouse_dpi", 800)))
                    aim_spd = aim_spd * (800.0 / dpi)
                    move_mouse_to(
                        tx, ty,
                        cfg.get("offset_x", 0), cfg.get("offset_y", 0),
                        aim_spd,
                        cfg.get("smooth_aim", True),
                        min_move_px=2,
                        input_method=cfg.get("input_method", "rzctl"),
                        hw_serial_port=cfg.get("hw_serial_port", "").strip(),
                        human_strength=int(cfg.get("human_strength", 0)),
                        crosshair_center_x=center_x,
                        crosshair_center_y=center_y,
                        responsive_mode=True,
                    )
                else:
                    last_smoothed = None
                    if not point:
                        raw_history.clear()
            elif enabled and not aim_active:
                last_smoothed = None
                raw_history.clear()

            if aim_active and enabled:
                time.sleep(0.002)
            elif enabled:
                time.sleep(0.004)
            else:
                time.sleep(0.003)
        except Exception as e:
            try:
                print(f"[aim_loop] error: {e}", file=sys.stderr)
            except Exception:
                pass
            time.sleep(0.01)


def main():
    _hide_console()
    cfg = load_config()
    if cfg.get("discreet_mode", False):
        _set_low_priority()

    root = tk.Tk()
    root.withdraw()
    root.title("RzStats")
    try:
        _ico = os.path.join(os.path.dirname(os.path.abspath(__file__)) if not getattr(sys, "frozen", False) else os.path.dirname(sys.executable), "Razer.ico")
        if os.path.exists(_ico):
            root.iconbitmap(_ico)
    except Exception:
        pass
    overlay = FOVOverlay(radius=cfg.get("fov_radius", 150), parent=root)
    hotkey_manager = HotkeyManager()
    hotkey_manager.start_listeners()

    threading.Thread(target=_toggle_enabled_loop, daemon=True).start()
    threading.Thread(target=lambda: __import__("x0").run_server(), daemon=True).start()
    threading.Thread(target=_aim_loop, args=(overlay, hotkey_manager), daemon=True).start()

    def on_close():
        hotkey_manager.stop_listeners()
        overlay.destroy()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.after(500, lambda: print(f"\n>>> Cấu hình: http://127.0.0.1:{WEB_PORT}\n"))
    root.mainloop()


def _license_prompt():
    try:
        return input("Nhap license key: ").strip()
    except (EOFError, KeyboardInterrupt):
        return ""


def _license_gate():
    if os.environ.get("RZ_DEV") == "1":
        _hide_console()
        main()
        return
    def prompt():
        return _license_prompt()
    def on_err(msg):
        print(msg)
    if require_license(prompt, on_error=on_err, max_attempts=5):
        _hide_console()
        main()
    else:
        print("Het so lan thu. Thoat.")
        sys.exit(1)


if __name__ == "__main__":
    _run_as_admin()
    _license_gate()
