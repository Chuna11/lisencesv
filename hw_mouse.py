"""
Chuột phần cứng - gửi lệnh dx,dy qua Serial tới Arduino/Pico.
Board đóng vai USB HID Mouse thật → game không block.
Cần: Arduino Leonardo / Pro Micro / Pico + firmware.
"""
import struct

_ser = None
_port = None


def init(port: str):
    """Mở cổng Serial. port ví dụ: COM3, /dev/ttyUSB0."""
    global _ser, _port
    try:
        import serial
        _ser = serial.Serial(port, 115200, timeout=0.01, write_timeout=0.02)
        _port = port
        return True
    except Exception:
        _ser = None
        _port = None
        return False


def is_ready():
    return _ser is not None and _ser.is_open


def move(dx: int, dy: int) -> bool:
    """Gửi (dx, dy) tới board. Board sẽ move chuột tương đối."""
    if not is_ready():
        return False
    try:
        # Format: 2 bytes signed dx + 2 bytes signed dy (binary nhỏ gọn)
        data = struct.pack("<hh", int(dx), int(dy))
        _ser.write(data)
        _ser.flush()
        return True
    except Exception:
        return False


def close():
    global _ser
    if _ser and _ser.is_open:
        try:
            _ser.close()
        except Exception:
            pass
    _ser = None
