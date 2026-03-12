"""
License server - doc lap, khong import license_key.
Key format: RZ-{D|W|M}-{YYYYMMDD}-{RND4}-{MID8}-{SIG12} hoac RZ-{D|W|M}-{YYYYMMDD}-{MID8}-{SIG12} (legacy)
"""
import hashlib
import hmac
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from flask import Flask, request, jsonify
except ImportError:
    print("pip install flask")
    raise

import base64
# Cung _SECRET voi license_key.py
_SECRET = (bytes([ord(c) ^ 0x42 for c in base64.b64decode("UlpTdGF0cy1WMi1LZXktVjIwMjU=").decode("latin-1")])).decode("latin-1").encode("utf-8")

app = Flask(__name__)
DB_PATH = Path(__file__).parent / "activations.json"
TZ_VN = timezone(timedelta(hours=7))


def _hash_sig(payload: str) -> str:
    return hmac.new(_SECRET, payload.encode("utf-8"), hashlib.sha256).hexdigest()[:12].upper()


def _load_db():
    if not DB_PATH.exists():
        return {}
    try:
        return json.loads(DB_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_db(db):
    try:
        DB_PATH.write_text(json.dumps(db, indent=0), encoding="utf-8")
    except Exception:
        pass


def _parse_key(key: str):
    if not key:
        return None
    k = key.strip().replace(" ", "").replace("-", "").upper()
    m = re.match(r"^RZ(D|W|M)(\d{8})([A-F0-9]{4})([A-F0-9]{8})([A-F0-9]{12})$", k)
    if m:
        return m.group(1), m.group(2), m.group(4), m.group(5)
    m = re.match(r"^RZ(D|W|M)(\d{8})([A-F0-9]{8})([A-F0-9]{12})$", k)
    return m.groups() if m else None


def _validate(parsed, key_norm: str):
    if not parsed or len(parsed) != 4:
        return False, None, "invalid"
    kt, date_str, mid_key, sig = parsed
    if len(key_norm) == 35:
        rnd = key_norm[11:15]
        payload = kt + date_str + rnd + mid_key
    else:
        payload = kt + date_str + mid_key
    if not hmac.compare_digest(_hash_sig(payload), sig):
        return False, None, "invalid"
    try:
        end_d = datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        return False, None, "invalid"
    now = datetime.now(TZ_VN)
    expires = end_d.replace(hour=23, minute=59, second=59, tzinfo=TZ_VN)
    if kt == "D":
        if now.date() != end_d.date():
            return False, expires.isoformat(), "expired"
    elif kt == "W":
        start = (end_d - timedelta(days=7)).replace(tzinfo=TZ_VN)
        expires = end_d.replace(tzinfo=TZ_VN)
        if now < start or now > expires:
            return False, expires.isoformat(), "expired"
    else:
        start = (end_d - timedelta(days=30)).replace(tzinfo=TZ_VN)
        expires = end_d.replace(tzinfo=TZ_VN)
        if now < start or now > expires:
            return False, expires.isoformat(), "expired"
    return True, expires.isoformat(), None


@app.route("/")
def health():
    now = datetime.now(TZ_VN)
    return jsonify({"ok": True, "date": now.strftime("%Y%m%d"), "time": now.isoformat()})


@app.route("/activate", methods=["POST"])
def activate():
    try:
        data = request.get_json(silent=True) or {}
        key = (data.get("key") or "").strip()
        mid = (data.get("machine_id") or "").strip().upper()
        if not key or not mid or len(mid) != 8:
            return jsonify({"ok": False, "msg": "invalid"}), 400
        parsed = _parse_key(key)
        if not parsed:
            return jsonify({"ok": False, "msg": "invalid"}), 400
        key_norm = key.strip().replace(" ", "").replace("-", "").upper()
        ok, expires, err = _validate(parsed, key_norm)
        if not ok:
            return jsonify({"ok": False, "msg": err or "expired"}), 400
        db = _load_db()
        bound = db.get(key_norm)
        if bound is None:
            db[key_norm] = mid
            _save_db(db)
        elif bound != mid:
            return jsonify({"ok": False, "msg": "already_bound"}), 400
        return jsonify({"ok": True, "expires": expires})
    except Exception as e:
        return jsonify({"ok": False, "msg": "error", "detail": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5874))
    app.run(host="0.0.0.0", port=port)
