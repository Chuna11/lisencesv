"""Điều khiển di chuyển chuột - Aim Controller (Razer rzctl + Hardware)"""
import ctypes
import math
import os
import random
import sys
import time
from ctypes import wintypes

user32 = ctypes.windll.user32


def _move_via_rzctl(dx, dy):
    """Razer Synapse driver (RZCONTROL) – input qua chuột Razer → Raw Input nhận, tâm ngắm di."""
    try:
        _dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
        if _dir not in sys.path and os.path.isdir(_dir):
            sys.path.insert(0, _dir)
        from rzctl import RZCONTROL
        if not hasattr(_move_via_rzctl, "_ctrl"):
            _move_via_rzctl._ctrl = RZCONTROL()
            if not _move_via_rzctl._ctrl.init():
                return False
        _move_via_rzctl._ctrl.mouse_move(int(dx), int(dy), from_start_point=True)
        return True
    except Exception:
        return False


def _move_via_hardware(dx, dy, port=None):
    """Chuột phần cứng – Serial tới Arduino/Pico (USB HID thật)."""
    try:
        from hw_mouse import init, is_ready, move
        if port and not is_ready():
            init(port)
        if is_ready():
            return move(int(dx), int(dy))
        return False
    except Exception:
        return False


def _pro_ease(dist_ratio):
    """Ease-in-out giống pro: chậm đầu/cuối, nhanh giữa (minimum jerk)."""
    if dist_ratio <= 0:
        return 0.0
    if dist_ratio >= 1:
        return 1.0
    t = dist_ratio
    return t * t * (3 - 2 * t)


def move_mouse_to(target_x, target_y, offset_x, offset_y, aim_speed, smooth=True, min_move_px=2, input_method="rzctl", hw_serial_port="", human_strength=0, crosshair_center_x=None, crosshair_center_y=None, responsive_mode=False, pro_style=False):
    """
    Di chuyển chuột tới mục tiêu. pro_style: ease-in-out, micro-overshoot, path curve như pro.
    """
    if target_x is None or target_y is None:
        return

    final_x = target_x + offset_x
    final_y = target_y + offset_y

    try:
        if crosshair_center_x is not None and crosshair_center_y is not None:
            current_x, current_y = crosshair_center_x, crosshair_center_y
        else:
            class POINT(ctypes.Structure):
                _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
            pt = POINT()
            user32.GetCursorPos(ctypes.byref(pt))
            current_x, current_y = pt.x, pt.y

        dist = ((final_x - current_x) ** 2 + (final_y - current_y) ** 2) ** 0.5
        if dist < min_move_px:
            return

        if smooth:
            base_speed = aim_speed
            if human_strength >= 2:
                base_speed *= random.uniform(0.75, 1.25)
            elif pro_style:
                base_speed *= random.uniform(0.92, 1.08)
            if responsive_mode:
                if dist < 20:
                    base_speed = min(base_speed, 0.85)
                elif dist > 40:
                    base_speed = min(2.8, base_speed * 1.5)
                if pro_style:
                    dist_ratio = min(1.0, dist / 60)
                    ease = 0.75 + 0.25 * _pro_ease(dist_ratio)
                else:
                    ease = 0.9 + 0.1 * min(1.0, dist / 30) if dist < 40 else 1.0
                base_speed *= ease
                if dist > 40:
                    max_step = 28
                elif dist < 30:
                    max_step = 10 if pro_style else 12
                else:
                    max_step = 16 if pro_style else 18
            elif pro_style:
                if dist < 15:
                    base_speed = min(base_speed, 0.5)
                    max_step = 6
                elif dist < 40:
                    base_speed = min(base_speed * 0.9, 0.85)
                    max_step = 12
                else:
                    max_step = 18
                dist_ratio = min(1.0, dist / 80)
                ease = 0.7 + 0.3 * _pro_ease(dist_ratio)
                base_speed *= ease
            else:
                if dist < 20:
                    base_speed = min(base_speed, 0.42)
                ease = 1.0
                if dist < 40:
                    ease = 0.65 + 0.35 * (dist / 40)
                max_step = 10 if dist < 25 else 18
                base_speed *= ease
            step_x = (final_x - current_x) * base_speed
            step_y = (final_y - current_y) * base_speed
            step_len = math.sqrt(step_x * step_x + step_y * step_y)
            if step_len > max_step and step_len > 1e-6:
                f = max_step / step_len
                step_x *= f
                step_y *= f
            if (responsive_mode or pro_style) and step_len > 1e-6:
                perp_x, perp_y = -step_y, step_x
                len_perp = math.sqrt(perp_x * perp_x + perp_y * perp_y)
                if len_perp > 1e-6:
                    curve_amp = 0.002 if pro_style else 0.003
                    curve = random.uniform(-curve_amp, curve_amp) * dist
                    step_x += perp_x / len_perp * curve
                    step_y += perp_y / len_perp * curve
            if pro_style and human_strength == 0:
                jitter = random.uniform(-0.4, 0.4)
                step_x += jitter
                step_y += random.uniform(-0.4, 0.4)
                if random.random() < 0.08 and dist < 25:
                    overshoot = random.uniform(1.02, 1.06)
                    step_x *= overshoot
                    step_y *= overshoot
            elif human_strength > 0:
                curve_amp = 0.02 if human_strength < 2 else 0.04
                perp_x, perp_y = -step_y, step_x
                len_perp = math.sqrt(perp_x * perp_x + perp_y * perp_y)
                if len_perp > 1e-6:
                    curve = random.uniform(-curve_amp, curve_amp) * dist
                    step_x += perp_x / len_perp * curve
                    step_y += perp_y / len_perp * curve
                jitter = 0.6 if human_strength < 2 else 1.5
                step_x += random.uniform(-jitter, jitter)
                step_y += random.uniform(-jitter, jitter)
                if human_strength >= 2 and random.random() < 0.15:
                    step_x *= random.uniform(1.02, 1.08)
                    step_y *= random.uniform(1.02, 1.08)
            new_x = current_x + step_x
            new_y = current_y + step_y
        else:
            new_x = final_x
            new_y = final_y

        dx = int(new_x - current_x)
        dy = int(new_y - current_y)
        if dx == 0 and dy == 0:
            return

        if human_strength >= 2:
            time.sleep(random.uniform(0.0002, 0.001))
        elif pro_style:
            time.sleep(random.uniform(0.00005, 0.00025))

        ok = False
        if input_method == "hardware" and hw_serial_port:
            ok = _move_via_hardware(dx, dy, port=hw_serial_port)
        else:
            ok = _move_via_rzctl(dx, dy)
            if not ok and hw_serial_port:
                ok = _move_via_hardware(dx, dy, port=hw_serial_port)
    except Exception:
        pass
