"""Chụp màn hình vùng FOV - Screen Capture"""
import mss
import numpy as np


def _capture_mss(left, top, width, height):
    """Chụp bằng mss (mặc định)."""
    with mss.mss() as sct:
        monitor = {"left": left, "top": top, "width": width, "height": height}
        screenshot = sct.grab(monitor)
        frame = np.array(screenshot)
        return frame[:, :, :3].copy(order="C")


def _align_for_dda(x, size):
    """Căn vùng DDA theo bội 2 – ổn định hơn, giảm lệch màu."""
    return (x // 2) * 2, max(4, ((size + 1) // 2) * 2)


def _capture_dda(left, top, width, height):
    """Desktop Duplication API – chụp ở tầng GPU, hầu như không bị ứng dụng chặn."""
    try:
        import dxcam
        if not hasattr(_capture_dda, "_cam"):
            _capture_dda._cam = None
            for backend in ("dxgi", "winrt"):
                try:
                    _capture_dda._cam = dxcam.create(
                        output_color="BGR",
                        processor_backend="cv2",
                        backend=backend,
                        output_idx=0,
                    )
                    break
                except Exception:
                    continue
            if _capture_dda._cam is None:
                return None
        cam = _capture_dda._cam
        frame = cam.grab(
            region=(left, top, left + width, top + height),
            new_frame_only=False,
            copy=True,
        )
        if frame is not None and frame.size > 0 and len(frame.shape) >= 3:
            arr = np.ascontiguousarray(frame[:, :, :3].astype(np.uint8))
            if arr.size > 0 and arr.shape[0] >= 4 and arr.shape[1] >= 4:
                if np.mean(arr) > 2:
                    return arr
    except Exception:
        pass
    return None


def _capture_pil(left, top, width, height):
    """Chụp bằng PIL ImageGrab (fallback). PIL trả RGB → đổi sang BGR."""
    try:
        from PIL import ImageGrab
        bbox = (left, top, left + width, top + height)
        img = ImageGrab.grab(bbox=bbox)
        rgb = np.array(img)[:, :, :3]
        return rgb[:, :, ::-1].copy()
    except Exception:
        return None


def capture_scan_region(center_x, center_y, fov_radius, capture_method="auto"):
    """
    Chụp vùng FOV để scan glow. capture_method:
    - "dda": Desktop Duplication API (GPU, khó bị chặn)
    - "mss": mss
    - "pil": PIL
    - "auto": dda → mss → pil
    """
    size = max(200, int(fov_radius * 2.5))
    left = max(0, center_x - size // 2)
    extend_top = int(size * 0.10)
    top = max(0, center_y - size // 2 - extend_top)
    height = size + extend_top
    frame = None
    if capture_method in ("dda", "auto"):
        l2, w2 = _align_for_dda(left, size)
        t2, h2 = _align_for_dda(top, height)
        frame = _capture_dda(l2, t2, w2, h2)
        if frame is not None:
            return np.ascontiguousarray(frame), l2, t2
    if capture_method == "dda" or capture_method == "auto":
        try:
            frame = _capture_mss(left, top, size, height)
        except Exception:
            frame = None
        if frame is None:
            frame = _capture_pil(left, top, size, height)
    elif capture_method == "pil":
        frame = _capture_pil(left, top, size, height)
    elif capture_method == "mss":
        try:
            frame = _capture_mss(left, top, size, height)
        except Exception:
            frame = _capture_pil(left, top, size, height)
    if frame is None:
        return np.zeros((height, size, 3), dtype=np.uint8), left, top
    return np.ascontiguousarray(frame), left, top
