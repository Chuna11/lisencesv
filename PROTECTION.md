# Bảo vệ source khi build exe

Hướng dẫn các kỹ thuật dev thường dùng để bảo vệ phần mềm thương mại, tránh crack / reverse engineering.

---

## 1. PyArmor – Obfuscation Python (Đã áp dụng)

**Cách dùng:**
```batch
build_protected.bat
```

Hoặc thủ công:
```batch
pip install pyarmor
pyarmor gen --pack ColorAim.spec -r q7.py m2.py k9.py p4.py t1.py w6.py n3.py v8.py x0.py license_key.py
```

**Tính năng:**
- Mã hóa bytecode → khó decompile
- Tên biến/hàm bị đổi → khó đọc
- Runtime protection → chống dump memory cơ bản

**PyArmor Pro (trả phí):** Có thêm `--private`, `--mix-str`, BCC (compile sang C) để bảo vệ mạnh hơn.

---

## 2. Cấu hình PyInstaller

Trong `ColorAim.spec`:
- `optimize=2` – bỏ docstring, assert (giảm thông tin recover được)
- `debug=False` – tắt debug
- `upx=False` – UPX làm exe dễ bị unpack, nên tắt nếu ưu tiên bảo mật

---

## 3. Bảo vệ License (Đã có)

- Kiểm tra license qua server
- Tích hợp logic check vào luồng chính, tránh bypass bằng cách patch 1 chỗ

---

## 4. VMProtect – Bảo vệ exe (Đã tích hợp)

**Cách dùng:**
```batch
build_with_vmprotect.bat
```

Script sẽ: (1) Build exe (PyArmor) nếu chưa có, (2) Chạy VMProtect_Con.exe để protect.

**Yêu cầu:**
- Cài [VMProtect](https://vmpsoft.com/) (Standard/Ultimate – bản Lite không có console)
- Đường dẫn mặc định: `C:\Program Files\VMProtect\`
- Hoặc set biến: `set VMPROTECT_PATH=C:\Duong\dan\VMProtect`

**Tùy chỉnh nâng cao:**
1. Mở VMProtect GUI
2. Add file `dist\RzStats\RzStats.exe`
3. Chọn options (virtualization, mutation, anti-debug…)
4. Lưu project thành `RzStats.vmp`
5. Chạy `build_with_vmprotect.bat` – script sẽ dùng `RzStats.vmp` nếu có

| Công cụ khác | Mô tả |
|--------------|-------|
| **Themida / WinLicense** | Packer + anti-debug |
| **Code Signing** | Ký exe (Authenticode) |

---

## 5. Best practices

1. Không hardcode key, API URL trong code – dùng env hoặc file cấu hình mã hóa
2. Tách phần license thành module riêng, obfuscate kỹ
3. Dùng `__pyarmor__` để kiểm tra code đã được obfuscate
4. Sign exe trước khi phân phối (tùy chọn nhưng nên dùng)

---

## 6. Mức độ bảo vệ (tăng dần)

| Mức | Cách làm | Độ khó crack |
|-----|----------|--------------|
| 1 | Chỉ PyInstaller | Thấp |
| 2 | PyArmor + PyInstaller | Trung bình |
| 3 | PyArmor Pro + optimize=2 | Cao hơn |
| 4 | + VMProtect / packer | Cao |
| 5 | + License server + Code signing | Cao nhất |

**Lưu ý:** Không có giải pháp nào chặn 100% crack. Mục tiêu là tăng chi phí thời gian và công sức để crack.
