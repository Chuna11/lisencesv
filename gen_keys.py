"""
Gen key ban cho khach. Key tu dong gan may khi khach nhap lan dau (can chay server).
Chay:  python gen_keys.py           -> 3 key D/W/M (format moi)
       python gen_keys.py --legacy  -> 3 key format cu (hop server Railway chua update)
       python gen_keys.py D         -> key ngay
"""
import sys
from datetime import datetime, timedelta
from license_key import generate_key

UNBOUND = "00000000"

def main():
    args = [a for a in sys.argv[1:] if a not in ("--legacy", "-L")]
    legacy = "--legacy" in sys.argv or "-L" in sys.argv
    today = datetime.now()
    if len(args) < 1:
        d = today.strftime("%Y%m%d")
        w = (today + timedelta(days=7)).strftime("%Y%m%d")
        m = (today + timedelta(days=30)).strftime("%Y%m%d")
        print("Key ngay: ", generate_key("D", d, UNBOUND, legacy=legacy))
        print("Key tuan: ", generate_key("W", w, UNBOUND, legacy=legacy))
        print("Key thang:", generate_key("M", m, UNBOUND, legacy=legacy))
        return
    t = args[0].upper()
    if t not in ("D", "W", "M"):
        print("D=ngay, W=tuan, M=thang")
        sys.exit(1)
    days = 0 if t == "D" else 7 if t == "W" else 30
    d = (today + timedelta(days=days)).strftime("%Y%m%d")
    print(generate_key(t, d, UNBOUND, legacy=legacy))

if __name__ == "__main__":
    main()
