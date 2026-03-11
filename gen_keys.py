"""
Gen key ban cho khach. Key tu dong gan may khi khach nhap lan dau (can chay server).
Chay:  python gen_keys.py       -> 3 key D/W/M, gui cho khach dung ngay
       python gen_keys.py D     -> key ngay
       python gen_keys.py W     -> key tuan
       python gen_keys.py M     -> key thang

Server: python license_server.py (host len Railway/Render/VPS)
        Dat RZ_LICENSE_SERVER=https://xxx trong app.
"""
import sys
from datetime import datetime, timedelta
from license_key import generate_key

UNBOUND = "00000000"

def main():
    today = datetime.now()
    if len(sys.argv) < 2:
        d = today.strftime("%Y%m%d")
        w = (today + timedelta(days=7)).strftime("%Y%m%d")
        m = (today + timedelta(days=30)).strftime("%Y%m%d")
        print("Key ngay: ", generate_key("D", d, UNBOUND))
        print("Key tuan: ", generate_key("W", w, UNBOUND))
        print("Key thang:", generate_key("M", m, UNBOUND))
        return
    t = sys.argv[1].upper()
    if t not in ("D", "W", "M"):
        print("D=ngay, W=tuan, M=thang")
        sys.exit(1)
    days = 0 if t == "D" else 7 if t == "W" else 30
    d = (today + timedelta(days=days)).strftime("%Y%m%d")
    print(generate_key(t, d, UNBOUND))

if __name__ == "__main__":
    main()
