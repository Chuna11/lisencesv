"""
Khach chay file nay, gui Machine ID cho nguoi ban de mua key.
"""
from license_key import get_machine_id_hash, get_machine_id

def main():
    mid = get_machine_id_hash()
    print("========================================")
    print("  RzStats - Machine ID")
    print("========================================")
    print("")
    print("  Machine ID cua ban:", mid)
    print("")
    print("  Gui day cho nguoi ban de nhan license key.")
    print("  Moi key chi dung duoc tren MAY NAY.")
    print("")
    print("========================================")

if __name__ == "__main__":
    main()
    input("Nhan Enter de dong...")
