"""Overlay hiển thị vòng FOV trên màn hình"""
import tkinter as tk


class FOVOverlay:
    def __init__(self, radius=150, parent=None):
        self.radius = radius
        self.window = None
        self.canvas = None
        self._parent = parent

    def create(self, center_x, center_y):
        """Tạo cửa sổ overlay hiển thị vòng FOV tại tâm (center_x, center_y)"""
        if self._parent:
            self.window = tk.Toplevel(self._parent)
        else:
            self.window = tk.Tk()
        self.window.title("Overlay")
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", 0.5)
        self.window.overrideredirect(True)
        self.window.configure(bg="black")

        size = self.radius * 2 + 40
        x = center_x - size // 2
        y = center_y - size // 2

        self.window.geometry(f"{size}x{size}+{x}+{y}")

        self.canvas = tk.Canvas(
            self.window,
            width=size,
            height=size,
            bg="black",
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        # Vẽ vòng tròn FOV
        cx, cy = size // 2, size // 2
        self.canvas.create_oval(
            cx - self.radius,
            cy - self.radius,
            cx + self.radius,
            cy + self.radius,
            outline="lime",
            width=2,
        )

        # Cho phép click-through (Windows)
        try:
            self.window.attributes("-transparentcolor", "black")
        except tk.TclError:
            pass

    def update_radius(self, radius, center_x=None, center_y=None):
        """Cập nhật bán kính FOV và vẽ lại vòng tròn"""
        self.radius = radius
        if not self.canvas:
            return
        size = radius * 2 + 40
        self.canvas.configure(width=size, height=size)
        self.canvas.delete("all")
        cx, cy = size // 2, size // 2
        self.canvas.create_oval(
            cx - radius,
            cy - radius,
            cx + radius,
            cy + radius,
            outline="lime",
            width=2,
        )
        if center_x is not None and center_y is not None:
            x = center_x - size // 2
            y = center_y - size // 2
            self.window.geometry(f"{size}x{size}+{x}+{y}")

    def show(self, center_x, center_y):
        """Hiển thị overlay tại tâm màn hình (center_x, center_y)"""
        if self.window is None:
            self.create(center_x, center_y)
        self.window.deiconify()
        self.window.lift()

    def hide(self):
        """Ẩn overlay"""
        if self.window:
            self.window.withdraw()

    def destroy(self):
        """Hủy overlay"""
        if self.window:
            try:
                self.window.destroy()
            except tk.TclError:
                pass
            self.window = None
