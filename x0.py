"""Web config - Unibot style"""
from flask import Flask, request, render_template_string
from k9 import load_config, save_config
from p4 import AIM_KEY_OPTIONS

app = Flask(__name__)
WEB_PORT = 5873

CONFIG_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Cấu hình Unibot</title>
  <style>
    * { box-sizing: border-box; }
    body { font-family: 'Segoe UI', sans-serif; max-width: 480px; margin: 20px auto; padding: 20px; background: #1a1a2e; color: #eee; }
    h1 { font-size: 1.3em; margin-bottom: 16px; }
    .group { background: #16213e; padding: 12px; margin-bottom: 12px; border-radius: 8px; }
    .group label { display: block; margin: 6px 0 4px; font-size: 0.9em; }
    input[type="number"], input[type="text"], select { padding: 6px 10px; width: 100%; max-width: 120px; background: #0f3460; border: 1px solid #533483; color: #fff; border-radius: 4px; }
    input[type="checkbox"] { margin-right: 8px; }
    .row { display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }
    button { background: #e94560; color: #fff; border: none; padding: 10px 24px; border-radius: 6px; cursor: pointer; margin-top: 8px; }
    button:hover { background: #ff6b6b; }
    .msg { padding: 10px; background: #0f3460; border-radius: 6px; margin-bottom: 12px; }
    .note { font-size: 0.8em; color: #888; margin-top: 4px; }
  </style>
</head>
<body>
  <h1>Cấu hình – Unibot</h1>
  {% if msg %}<div class="msg">{{ msg }}</div>{% endif %}
  <form method="post">
    <div class="group">
      <strong>Bật / Tắt</strong>
      <label><input type="checkbox" name="enabled" value="1" {% if cfg.enabled %}checked{% endif %}> Bật aim</label>
    </div>

    <div class="group">
      <strong>Aim – nhắm đầu</strong>
      <label>Aim height (0.85=đầu): <input type="text" name="aim_height" value="{{ cfg.aim_height }}" placeholder="0.85"></label>
      <div class="note">0.85=đầu, 0.5=giữa. Unibot: y = rect_y + rect_h*(1-aim_height)</div>
      <div class="row">
        <label>Offset X: <input type="number" name="offset_x" value="{{ cfg.offset_x }}" min="-50" max="50"></label>
        <label>Offset Y: <input type="number" name="offset_y" value="{{ cfg.offset_y }}" min="-50" max="50"></label>
      </div>
      <label>Aim smoothing: <input type="number" name="aim_smoothing" value="{{ cfg.aim_smoothing }}" min="0.01" max="0.99" step="0.01" placeholder="0.7"></label>
      <div class="note">0.01=nhanh, 0.99=dính hơn. Giới hạn: 0.01–0.99</div>
      <label>Aim speed: <input type="number" name="aim_speed" value="{{ cfg.aim_speed }}" min="0.1" max="2.5" step="0.05" placeholder="0.75"></label>
      <div class="note">Tốc độ kéo chuột. Giới hạn: 0.1–2.5</div>
      <label>Chuột DPI: <input type="number" name="mouse_dpi" value="{{ cfg.mouse_dpi }}" min="200" max="25600" step="100" placeholder="800"></label>
      <div class="note">DPI chuột – aim speed sẽ scale theo (800/DPI). VD: 1600 DPI → aim chậm hơn ~1/2.</div>
    </div>

    <div class="group">
      <strong>Tracking / Ưu tiên mục tiêu</strong>
      <label>Ưu tiên:
        <select name="target_priority">
          <option value="closest" {% if cfg.target_priority == 'closest' %}selected{% endif %}>Gần tâm nhất</option>
          <option value="largest" {% if cfg.target_priority == 'largest' %}selected{% endif %}>To nhất (gần hơn)</option>
          <option value="highest" {% if cfg.target_priority == 'highest' %}selected{% endif %}>Cao nhất trong FOV</option>
          <option value="lowest" {% if cfg.target_priority == 'lowest' %}selected{% endif %}>Thấp nhất trong FOV</option>
          <option value="closest_largest" {% if cfg.target_priority == 'closest_largest' %}selected{% endif %}>Gần + to</option>
        </select>
      </label>
      <label>Giữ mục tiêu thêm (frame): <input type="number" name="target_hold_frames" value="{{ cfg.target_hold_frames }}" min="0" max="60"></label>
      <label>Độ "người" của aim:
        <select name="human_strength">
          <option value="0" {% if cfg.human_strength == 0 %}selected{% endif %}>0 - Mượt, robot</option>
          <option value="1" {% if cfg.human_strength == 1 %}selected{% endif %}>1 - Vừa phải</option>
          <option value="2" {% if cfg.human_strength >= 2 %}selected{% endif %}>2 - Rung hơn</option>
        </select>
      </label>
      <div class="note">Giữ mục tiêu giúp aim không "tụt" khi địch bị khuất trong vài frame ngắn.</div>
    </div>

    <div class="group">
      <strong>FOV</strong>
      <label>Bán kính (px): <input type="number" name="fov_radius" value="{{ cfg.fov_radius }}" min="1" max="400"></label>
      <label><input type="checkbox" name="show_fov_overlay" value="1" {% if cfg.show_fov_overlay %}checked{% endif %}> Hiển thị FOV</label>
    </div>

    <div class="group">
      <strong>Phím aim (giữ 1 trong 2 phím)</strong>
      <div class="row">
        <label>Phím 1: <select name="aim_key">
          {% for name, val in aim_options %}
          <option value="{{ val }}" {% if cfg.aim_key == val %}selected{% endif %}>{{ name }}</option>
          {% endfor %}
        </select></label>
        <label>Phím 2 (tùy chọn): <select name="aim_key_2">
          {% for name, val in aim_options %}
          <option value="{{ val }}" {% if cfg.aim_key_2 == val %}selected{% endif %}>{{ name }}</option>
          {% endfor %}
        </select></label>
      </div>
      <div class="note">VD: Phím 1=Chuột phải, Phím 2=Shift → giữ Chuột phải HOẶC Shift để aim.</div>
    </div>

    <div class="group">
      <strong>Valorant Purple – Glow tím (Tritanopia)</strong>
      <div class="row">
        <label>H: <input type="number" name="h_min" value="{{ tc.h_min }}" min="0" max="179"></label>
        <label>– <input type="number" name="h_max" value="{{ tc.h_max }}" min="0" max="179"></label>
        <label>S min: <input type="number" name="s_min" value="{{ tc.s_min }}" min="90" max="255"></label>
        <label>V min: <input type="number" name="v_min" value="{{ tc.v_min }}" min="95" max="255"></label>
      </div>
      <div class="note">Mặc định: H 125–165 (tím). S,V ≥90 tránh đen/xám. Settings → Accessibility → Purple.</div>
    </div>

    <div class="group">
      <strong>Thêm dải hồng (tùy chọn)</strong>
      <label><input type="checkbox" name="color2_enabled" value="1" {% if tc2.enabled %}checked{% endif %}> Bật</label>
      <div class="row">
        <label>H: <input type="number" name="h2_min" value="{{ tc2.h_min }}"></label>
        <label>– <input type="number" name="h2_max" value="{{ tc2.h_max }}"></label>
      </div>
    </div>

    <div class="group">
      <strong>Khác</strong>
      <label>Chuột: <select name="input_method">
        <option value="rzctl" {% if cfg.input_method == 'rzctl' %}selected{% endif %}>Razer</option>
        <option value="hardware" {% if cfg.input_method == 'hardware' %}selected{% endif %}>Hardware</option>
      </select></label>
      <label>Chụp: <select name="capture_method">
        <option value="auto" {% if cfg.capture_method == 'auto' %}selected{% endif %}>Auto</option>
        <option value="dda" {% if cfg.capture_method == 'dda' %}selected{% endif %}>DDA</option>
        <option value="mss" {% if cfg.capture_method == 'mss' %}selected{% endif %}>mss</option>
      </select></label>
      <label>Serial: <input type="text" name="hw_serial_port" value="{{ cfg.hw_serial_port }}" placeholder="COM3"></label>
      <label><input type="checkbox" name="discreet_mode" value="1" {% if cfg.discreet_mode %}checked{% endif %}> Chế độ kín đáo</label>
    </div>

    <button type="submit">Lưu</button>
  </form>
</body>
</html>
"""


def _parse_form():
    cfg = load_config()
    tc = cfg.get("target_color", {})
    tc2 = cfg.get("target_color_2", {})
    return {"cfg": cfg, "tc": tc, "tc2": tc2, "aim_options": AIM_KEY_OPTIONS, "msg": None}


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            sm = max(90, int(request.form.get("s_min", 95)))
            vm = max(95, int(request.form.get("v_min", 100)))
            old = load_config()
            tc = {
                "h_min": int(request.form.get("h_min", 125)),
                "h_max": int(request.form.get("h_max", 165)),
                "s_min": sm, "s_max": 255,
                "v_min": vm, "v_max": 255,
            }
            tc2 = {
                "enabled": request.form.get("color2_enabled") == "1",
                "h_min": int(request.form.get("h2_min", 155)),
                "h_max": int(request.form.get("h2_max", 179)),
                "s_min": 90, "s_max": 255, "v_min": 95, "v_max": 255,
            }
            cfg = {
                "target_color": tc, "target_color_2": tc2,
                "offset_x": int(request.form.get("offset_x", 0)),
                "offset_y": int(request.form.get("offset_y", 0)),
                "aim_height": float(request.form.get("aim_height") or "0.85"),
                "aim_smoothing": max(0.01, min(0.99, float(request.form.get("aim_smoothing") or str(old.get("aim_smoothing", 0.7))))),
                "aim_speed": max(0.1, min(2.5, float(request.form.get("aim_speed") or str(old.get("aim_speed", 0.75))))),
                "fov_radius": max(1, int(request.form.get("fov_radius", 120))),
                "show_fov_overlay": request.form.get("show_fov_overlay") == "1",
                "smooth_aim": True,
                "aim_key": request.form.get("aim_key", "none"),
                "aim_key_2": request.form.get("aim_key_2", "none"),
                "input_method": request.form.get("input_method", "rzctl"),
                "capture_method": request.form.get("capture_method", "auto"),
                "hw_serial_port": request.form.get("hw_serial_port", "").strip(),
                "discreet_mode": request.form.get("discreet_mode") == "1",
                "enabled": request.form.get("enabled") == "1",
                "target_priority": request.form.get("target_priority", old.get("target_priority", "closest")),
                "target_hold_frames": max(0, int(request.form.get("target_hold_frames", old.get("target_hold_frames", 12)))),
                "human_strength": int(request.form.get("human_strength", old.get("human_strength", 0))),
                "mouse_dpi": max(200, min(25600, int(request.form.get("mouse_dpi", old.get("mouse_dpi", 800))))),
            }
            cfg["minimize_when_running"] = old.get("minimize_when_running", False)
            cfg["group_blobs"] = old.get("group_blobs", [3, 3])
            save_config(cfg)
            ctx = _parse_form()
            ctx["msg"] = "Đã lưu."
            return render_template_string(CONFIG_HTML, **ctx)
        except (ValueError, KeyError) as e:
            ctx = _parse_form()
            ctx["msg"] = f"Lỗi: {e}"
            return render_template_string(CONFIG_HTML, **ctx)
    return render_template_string(CONFIG_HTML, **_parse_form())


def run_server():
    app.run(host="127.0.0.1", port=WEB_PORT, threaded=True, use_reloader=False)
