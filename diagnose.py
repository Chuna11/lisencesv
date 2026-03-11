"""
Chay: python diagnose.py
Kiem tra tung buoc de xac dinh loi.
"""
import os
import sys

# Fix encoding Windows console
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE = os.path.dirname(os.path.abspath(__file__))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

def log(msg):
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode('ascii', 'replace').decode('ascii'))

def main():
    log("=== CHAN DOAN COLORAIM ===\n")

    # 1. Config
    log("1. Config (r0.json)")
    try:
        from k9 import load_config, CONFIG_PATH
        cfg = load_config()
        log(f"   enabled: {cfg.get('enabled')}")
        log(f"   aim_key: {cfg.get('aim_key')}, aim_key_2: {cfg.get('aim_key_2', 'none')} (phai GIU phim khi aim; neu co 2 phim thi giu ca 2)")
        log(f"   fov_radius: {cfg.get('fov_radius')}")
        log(f"   input_method: {cfg.get('input_method')}")
        log(f"   capture_method: {cfg.get('capture_method')}")
        log(f"   aim_speed: {cfg.get('aim_speed')}")
    except Exception as e:
        log(f"   LOI: {e}")
        return

    # 2. Screen center
    log("\n2. Tâm màn hình")
    try:
        from m2 import get_screen_center
        cx, cy = get_screen_center()
        log(f"   center: ({cx}, {cy})")
    except Exception as e:
        log(f"   LOI: {e}")
        return

    # 3. Capture
    log("\n3. Capture màn hình")
    try:
        from n3 import capture_scan_region
        frame, left, top = capture_scan_region(cx, cy, cfg.get("fov_radius", 120), capture_method=cfg.get("capture_method", "auto"))
        h, w = frame.shape[:2]
        log(f"   frame: {w}x{h}, left={left}, top={top}")
        if frame.mean() < 5:
            log("   CANH BAO: Frame gan nhu den - capture co the sai (game fullscreen chan?)")
    except Exception as e:
        log(f"   LOI: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. Detection
    log("\n4. Nhan dien mau")
    try:
        from t1 import detect
        tc = cfg.get("target_color", {})
        tc2 = cfg.get("target_color_2") or {}
        extra = []
        if tc2.get("enabled"):
            extra.append((tc2.get("h_min", 155), tc2.get("h_max", 179), tc2.get("s_min", 80), 255, tc2.get("v_min", 100), 255))
        point = detect(frame, tc.get("h_min", 120), tc.get("h_max", 165),
            tc.get("s_min", 80), 255, tc.get("v_min", 100), 255,
            w//2, h//2, cfg.get("fov_radius", 120),
            color_ranges_extra=extra if extra else None, aim_height=0.85)
        if point:
            log(f"   DA tim thay muc tieu: ({point[0]}, {point[1]}) trong frame")
        else:
            log("   KHONG tim thay muc tieu (khong co glow tim/hong trong FOV)")
    except Exception as e:
        log(f"   LOI: {e}")
        import traceback
        traceback.print_exc()
        return

    # 5. Hotkey
    log("\n5. Phim aim")
    try:
        from p4 import HotkeyManager
        hm = HotkeyManager()
        hm.set_aim_key(cfg.get("aim_key", "none"))
        hm.set_aim_key_2(cfg.get("aim_key_2", "none"))
        active = hm.is_aim_active()
        log(f"   aim_key='{cfg.get('aim_key')}', aim_key_2='{cfg.get('aim_key_2','none')}', is_aim_active={active}")
        if cfg.get("aim_key") != "none" and not active:
            log("   -> Ban PHAI GIU 1 TRONG 2 phim aim trong luc chay script nay de test!")
    except Exception as e:
        log(f"   LOI: {e}")

    # 6. rzctl
    log("\n6. rzctl (Razer chuot)")
    try:
        _dir = os.path.join(BASE, "lib")
        if _dir not in sys.path and os.path.isdir(_dir):
            sys.path.insert(0, _dir)
        from rzctl import RZCONTROL
        ctrl = RZCONTROL()
        ok = ctrl.init()
        if ok:
            log("   rzctl.init() = OK")
            ctrl.mouse_move(5, 5, from_start_point=True)
            log("   Da thu mouse_move(5,5) - chuot co di chuyen khong?")
        else:
            log("   rzctl.init() = THAT BAI")
            log("   -> Can Razer Synapse 3 + chuot Razer. RZCONTROL driver chua co.")
    except Exception as e:
        log(f"   rzctl LỖI: {e}")
        log("   -> Co the thieu Razer Synapse / chuot Razer")

    log("\n=== KET LUAN ===")
    if not point:
        log("Van de: KHONG nhan dien duoc muc tieu. Kiem tra HSV, bat highlight Purple/Yellow, tang FOV.")
    elif cfg.get("aim_key") != "none":
        k2 = cfg.get("aim_key_2", "none")
        if k2 != "none":
            log("Nho: Phai GIU 1 TRONG 2 phim aim khi aim.")
        else:
            log("Nho: Phai GIU phim aim khi aim. Thu aim_key='none' de luon bat.")
    log("Chay xong.")

if __name__ == "__main__":
    main()
