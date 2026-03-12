# ColorAim - Unibot

Cơ chế phát hiện địch và aim theo [Unibot](https://github.com/vike256/Unibot). HSV → dilation → contours → chọn mục tiêu gần tâm → nhắm chuẩn vào đầu. Chạy nền, cấu hình qua web.

## Cài đặt

```bash
pip install -r requirements.txt
```

## Chạy chương trình

```bash
python q7.py
```

Chương trình chạy **hoàn toàn nền** – không có cửa sổ, chỉ hiện process trên Task Manager.

## Cấu hình qua web

Khi chương trình đang chạy:

1. Mở trình duyệt
2. Truy cập: **http://localhost:8000**
3. Chỉnh các tham số và nhấn **Lưu cấu hình**

Có thể bật/tắt aim trực tiếp trên trang web (checkbox "Bật aim").

## Chạy không hiện cửa sổ Console (khuyến nghị)

Để không hiện cửa sổ đen:

```bash
pythonw q7.py
```

Hoặc tạo shortcut với `pythonw.exe` thay vì `python.exe`.

## Tính năng cấu hình

| Mục | Mô tả |
|-----|-------|
| Bật aim | Bật/tắt chức năng aim |
| Offset X, Y | Điều chỉnh vị trí nhắm (Y âm = lên trên / vùng đầu) |
| FOV | Bán kính vùng quét (px) |
| Hiển thị vòng FOV | Hiện/ẩn vòng tròn FOV trên màn hình |
| Aim height | 0.85 = nhắm đầu (15% từ trên) |
| Aim Speed | Tốc độ aim |
| Phím aim | Giữ phím để aim |
| Màu HSV | H, S, V cho glow địch |
| Chế độ kín đáo | Ưu tiên CPU thấp cho game |

## Tắt chương trình

- Mở **Task Manager** → tìm `Python` hoặc `pythonw` → **Kết thúc tác vụ**
- Hoặc tắt cửa sổ Console nếu chạy bằng `python q7.py`

## Lưu ý

- Chỉ dùng với game offline / single-player
- Một số anti-cheat có thể phát hiện thao tác chuột tự động
- Chỉ sử dụng trong môi trường được phép
