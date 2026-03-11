"""
License key: thoi gian thuc (internet). Key RZ-*-00000000-*: kich hoat qua server, gan may lan dau.
Key: RZ-{D|W|M}-{YYYYMMDD}-{MID8}-{SIG}  (MID=00000000 = universal, bind qua server)
"""
import base64
import hashlib
import hmac
import json
import os
import random
import re
import sys
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timezone, timedelta

_SECRET = (bytes([ord(c) ^ 0x42 for c in base64.b64decode("UlpTdGF0cy1WMi1LZXktVjIwMjU=").decode("latin-1")])).decode("latin-1").encode("utf-8")
_last_activate_err: str = ""


def get_machine_id() -> str:
    """Lay ID may (Windows: UUID tu BIOS)."""
    try:
        out = subprocess.check_output("wmic csproduct get uuid", shell=True, creationflags=0x08000000).decode("utf-8", errors="ignore")
        lines = [x.strip() for x in out.split("\n") if x.strip() and x.strip().lower() != "uuid"]
        if lines:
            return lines[0].strip()
    except Exception:
        pass
    try:
        import uuid
        return str(uuid.getnode())
    except Exception:
        pass
    return os.environ.get("COMPUTERNAME", "UNKNOWN")


def get_machine_id_hash() -> str:
    """Hash 8 ky tu cho key."""
    mid = get_machine_id()
    return hashlib.sha256(mid.encode("utf-8")).hexdigest()[:8].upper()


def get_real_time_now() -> datetime | None:
    """Lay thoi gian thuc tu internet. None neu offline."""
    for url in ("https://worldtimeapi.org/api/ip", "https://timeapi.io/api/Time/current/zone?timeZone=UTC"):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "RzStats/1.0"})
            with urllib.request.urlopen(req, timeout=5) as r:
                data = json.loads(r.read().decode())
            s = data.get("datetime") or data.get("currentDateTime") or data.get("dateTime")
            if s:
                return datetime.fromisoformat(s.replace("Z", "+00:00"))
            unix = data.get("unixtime") or data.get("unixTime")
            if unix is not None:
                return datetime.fromtimestamp(int(unix), tz=timezone.utc)
        except Exception:
            continue
    return None


def _hash_sig(payload: str) -> str:
    return hmac.new(_SECRET, payload.encode("utf-8"), hashlib.sha256).hexdigest()[:12].upper()


def _get_license_server_url() -> str:
    url = os.environ.get("RZ_LICENSE_SERVER", "").strip()
    if url:
        return url.rstrip("/")
    base = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(base, "r0.json")
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                j = json.load(f)
            u = (j.get("license_server") or "").strip()
            if u:
                u = u.rstrip("/")
                if u and not u.startswith(("http://", "https://")):
                    u = "https://" + u
                return u
        except Exception:
            pass
    return ""


def _activate_server(key: str, machine_id: str) -> tuple[bool, str | None, str]:
    """Goi server kich hoat key universal. Tra ve (ok, expires_iso, error_msg)."""
    url = _get_license_server_url()
    if not url:
        return False, None, "Chua cau hinh license_server trong r0.json"
    try:
        req = urllib.request.Request(
            url + "/activate",
            data=json.dumps({"key": key.strip(), "machine_id": machine_id}).encode("utf-8"),
            headers={"Content-Type": "application/json", "User-Agent": "RzStats/1.0"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode())
        if data.get("ok") and data.get("expires"):
            return True, data["expires"], ""
        return False, None, data.get("msg", "error")
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode()
            data = json.loads(body)
            msg = data.get("msg", str(e.code))
        except Exception:
            msg = str(e.code)
        if "already_bound" in str(msg):
            return False, None, "Key da dung tren may khac, khong the dung may nay."
        if "expired" in str(msg):
            return False, None, "Key het han."
        return False, None, f"Server: {msg}"
    except Exception as e:
        return False, None, f"Khong ket noi duoc server (kiem tra mang, URL): {e!r}"


def validate_key(key: str) -> tuple[bool, str, str | None]:
    """
    Kiem tra key. Tra ve (valid, key_type, expires_iso).
    Dung thoi gian internet; bind machine ID; khong cho sua.
    """
    global _last_activate_err
    _last_activate_err = ""
    if not key or not isinstance(key, str):
        return False, "", None
    key = key.strip().replace(" ", "").replace("-", "").upper()
    m = re.match(r"^RZ(D|W|M)(\d{8})([A-F0-9]{4})([A-F0-9]{8})([A-F0-9]{12})$", key)
    if m:
        kt, date_str, rnd, mid_key, sig = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
        payload = kt + date_str + rnd + mid_key
    else:
        m = re.match(r"^RZ(D|W|M)(\d{8})([A-F0-9]{8})([A-F0-9]{12})$", key)
        if not m:
            return False, "", None
        kt, date_str, mid_key, sig = m.group(1), m.group(2), m.group(3), m.group(4)
        payload = kt + date_str + mid_key
    mid_actual = get_machine_id_hash()
    if mid_key != "00000000":
        if mid_key != mid_actual:
            return False, "", None
    else:
        ok, exp, err = _activate_server(key, mid_actual)
        if not ok or not exp:
            _last_activate_err = err or "Loi kich hoat"
            return False, "", None
        return True, kt, exp
    if not hmac.compare_digest(_hash_sig(payload), sig):
        return False, "", None
    try:
        end_d = datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        return False, "", None
    now = get_real_time_now()
    if now is None:
        now = datetime.now()
    if kt == "D":
        if now.date() != end_d.date():
            return False, "D", end_d.replace(hour=23, minute=59, second=59).isoformat()
        expires = end_d.replace(hour=23, minute=59, second=59)
    elif kt == "W":
        start = end_d - timedelta(days=7)
        if now < start or now > end_d:
            return False, "W", end_d.isoformat()
        expires = end_d
    else:
        start = end_d - timedelta(days=30)
        if now < start or now > end_d:
            return False, "M", end_d.isoformat()
        expires = end_d
    return True, kt, expires.isoformat()


def _get_license_path():
    base = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, ".rzlic")


def _enc(data: bytes, k: bytes) -> bytes:
    return bytes((b ^ k[i % len(k)]) & 0xFF for i, b in enumerate(data))


def load_cached_license() -> tuple[bool, str | None]:
    valid, _ = _check_cache()
    return valid, None


def _check_cache() -> tuple[bool, str | None]:
    path = _get_license_path()
    if not os.path.exists(path):
        return False, None
    try:
        raw = open(path, "rb").read()
        dec = _enc(raw, _SECRET[:16])
        obj = json.loads(dec.decode("utf-8"))
        exp = obj.get("e")
        if not exp:
            return False, None
        mid_cached = obj.get("m")
        if mid_cached and mid_cached != get_machine_id_hash():
            return False, None
        exp_dt = datetime.fromisoformat(exp.replace("Z", "+00:00"))
        now = get_real_time_now() or datetime.now()
        if exp_dt.tzinfo:
            now = now.replace(tzinfo=exp_dt.tzinfo) if now.tzinfo is None else now
        elif now.tzinfo:
            exp_dt = exp_dt.replace(tzinfo=now.tzinfo)
        if now > exp_dt:
            return False, None
        return True, exp
    except Exception:
        return False, None


def save_license_cache(key_type: str, expires_iso: str, machine_id: str | None = None):
    path = _get_license_path()
    mid = machine_id or get_machine_id_hash()
    data = json.dumps({"t": key_type, "e": expires_iso, "m": mid}).encode("utf-8")
    enc = _enc(data, _SECRET[:16])
    try:
        open(path, "wb").write(enc)
    except Exception:
        pass


def require_license(prompt_fn, on_error=None, max_attempts: int = 5) -> bool:
    valid, _ = _check_cache()
    if valid:
        return True
    for _ in range(max_attempts):
        key = prompt_fn()
        ok, kt, exp = validate_key(key)
        if ok and exp:
            save_license_cache(kt, exp)
            return True
        if on_error:
            msg = _last_activate_err if _last_activate_err else "Key khong hop le, het han, hoac khong dung may nay."
            on_error(msg)
    return False


def generate_key(key_type: str, date_str: str, machine_id_hash: str) -> str:
    """Tao key (chi admin). Moi lan goi tao key khac nhau (random 4 hex)."""
    mid = machine_id_hash.upper()
    rnd = "".join(random.choices("0123456789ABCDEF", k=4))
    payload = key_type + date_str + rnd + mid
    sig = _hash_sig(payload)
    return f"RZ-{key_type}-{date_str}-{rnd}-{mid}-{sig}"
