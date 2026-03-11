"""
Phát hiện hình người và vùng đầu bằng MediaPipe Pose (Tasks API).
Trả về tọa độ mũi (điểm aim chính xác vào đầu).
"""
import os
import urllib.request

import cv2
import numpy as np

# MediaPipe Tasks API (mới) - thay thế mp.solutions
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, RunningMode
from mediapipe import ImageFormat
import mediapipe as mp

NOSE_INDEX = 0
LEFT_EYE = 2
RIGHT_EYE = 5

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"


def _get_model_path():
    base = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base, "pose_landmarker_lite.task")
    if not os.path.exists(path):
        try:
            urllib.request.urlretrieve(MODEL_URL, path)
        except Exception:
            pass
    return path if os.path.exists(path) else None


_detector = None


def _get_detector():
    global _detector
    if _detector is None:
        model_path = _get_model_path()
        if not model_path:
            raise FileNotFoundError("Không tải được pose model. Kiểm tra internet.")
        opts = PoseLandmarkerOptions(
            base_options=BaseOptions(model_asset_path=model_path),
            running_mode=RunningMode.IMAGE,
            min_pose_detection_confidence=0.5,
        )
        _detector = PoseLandmarker.create_from_options(opts)
    return _detector


def get_head_position(frame_bgr, center_x, center_y, fov_radius):
    """
    Phát hiện vị trí đầu (mũi) trong frame.
    Chỉ trả về điểm nếu nằm trong vòng FOV.
    """
    try:
        detector = _get_detector()
    except Exception:
        return None

    h, w = frame_bgr.shape[:2]
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=ImageFormat.SRGB, data=rgb)

    result = detector.detect(mp_image)

    if not result.pose_landmarks or len(result.pose_landmarks) == 0:
        return None

    landmarks = result.pose_landmarks[0]
    nose = landmarks[NOSE_INDEX]
    vis = getattr(nose, "visibility", 1.0) or 1.0
    if vis < 0.5:
        le, re = landmarks[LEFT_EYE], landmarks[RIGHT_EYE]
        lev = getattr(le, "visibility", 1.0) or 0
        rev = getattr(re, "visibility", 1.0) or 0
        if lev < 0.5 and rev < 0.5:
            return None
        x = (le.x + re.x) / 2
        y = (le.y + re.y) / 2
    else:
        x, y = nose.x, nose.y

    px = int(x * w)
    py = int(y * h)
    dist = np.sqrt((px - center_x) ** 2 + (py - center_y) ** 2)
    if dist <= fov_radius:
        return (px, py)
    return None
