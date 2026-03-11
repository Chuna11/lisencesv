"""
Server kich hoat key. Key dung lan dau se tu dong gan vao may do.
Chay: python license_server.py
Host len Railway/Render/VPS, dat RZ_LICENSE_SERVER trong app tro ve URL server.
"""
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from flask import Flask, request, jsonify
except ImportError:
    print("Can: pip install flask")
    raise

# Dung cung logic voi license_key.py
import license_key as lk

app = Flask(__name__)
DB_PATH = Path(__file__).parent / "activations.json"


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
    import re
    k = key.strip().replace(" ", "").replace("-", "").upper()
    m = re.match(r"^RZ(D|W|M)(\d{8})([A-F0-9]{4})([A-F0-9]{8})([A-F0-9]{12})$", k)
    if m:
        return m.group(1), m.group(2), m.group(4), m.group(5)  # kt, date, mid, sig (bo rnd)
    m = re.match(r"^RZ(D|W|M)(\d{8})([A-F0-9]{8})([A-F0-9]{12})$", k)
    return m.groups() if m else None


def _validate_key_internals(parsed, key_norm: str):
    """Validate key (ky + ngay), tra ve (ok, kt, expires_iso)."""
    import hmac as hm
    if not parsed or len(parsed) != 4:
        return False, "", None
    kt, date_str, mid_key, sig = parsed
    if len(key_norm) == 36:
        rnd = key_norm[12:16]
        payload = kt + date_str + rnd + mid_key
    else:
        payload = kt + date_str + mid_key
    if not hm.compare_digest(lk._hash_sig(payload), sig):
        return False, "", None
    try:
        end_d = datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        return False, "", None
    now = datetime.now(timezone.utc)
    if kt == "D":
        expires = end_d.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
        if now.date() != end_d.date():
            return False, "D", expires.isoformat()
    elif kt == "W":
        start = end_d - timedelta(days=7)
        expires = end_d.replace(tzinfo=timezone.utc)
        if now < start.replace(tzinfo=timezone.utc) or now > expires:
            return False, "W", expires.isoformat()
    else:
        start = end_d - timedelta(days=30)
        expires = end_d.replace(tzinfo=timezone.utc)
        if now < start.replace(tzinfo=timezone.utc) or now > expires:
            return False, "M", expires.isoformat()
    return True, kt, expires.isoformat()


@app.route("/activate", methods=["POST"])
def activate():
    try:
        data = request.get_json() or {}
        key = (data.get("key") or "").strip()
        mid = (data.get("machine_id") or "").strip().upper()
        if not key or not mid or len(mid) != 8:
            return jsonify({"ok": False, "msg": "invalid"}), 400
        parsed = _parse_key(key)
        if not parsed:
            return jsonify({"ok": False, "msg": "invalid"}), 400
        key_norm = key.strip().replace(" ", "").replace("-", "").upper()
        ok, kt, expires = _validate_key_internals(parsed, key_norm)
        if not ok or not expires:
            return jsonify({"ok": False, "msg": "expired"}), 400
        db = _load_db()
        bound = db.get(key_norm)
        if bound is None:
            db[key_norm] = mid
            _save_db(db)
        elif bound != mid:
            return jsonify({"ok": False, "msg": "already_bound"}), 400
        return jsonify({"ok": True, "expires": expires})
    except Exception:
        return jsonify({"ok": False, "msg": "error"}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5874))
    app.run(host="0.0.0.0", port=port)
