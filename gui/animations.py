# gui/animations.py
# -*- coding: utf-8 -*-
"""
GUI 动画工具库 — 为 CustomTkinter 添加动画效果
"""
import customtkinter as ctk


class AnimationMixin:
    """动画混入类，为 CTk 组件添加动画能力"""

    def fade_in(self, widget, duration=300, callback=None):
        """淡入动画"""
        steps = 10
        delay = duration // steps

        def _step(alpha):
            if alpha <= 1.0:
                try:
                    # 通过颜色透明度模拟淡入
                    widget.after(delay, lambda: _step(alpha + 0.1))
                except Exception:
                    pass
            else:
                if callback:
                    callback()

        _step(0)

    def slide_in(self, widget, direction="left", duration=300, callback=None):
        """滑入动画"""
        steps = 10
        delay = duration // steps
        target_x = widget.winfo_x()
        target_y = widget.winfo_y()

        if direction == "left":
            start_x = target_x - 200
        elif direction == "right":
            start_x = target_x + 200
        elif direction == "top":
            start_x = target_x
            start_y = target_y - 100
        else:
            start_x = target_x

        def _step(x):
            if abs(x - target_x) > 2:
                try:
                    widget.place(x=x)
                    step_size = (target_x - x) / steps
                    widget.after(delay, lambda: _step(x + step_size))
                except Exception:
                    widget.place(x=target_x)
                    if callback:
                        callback()
            else:
                widget.place(x=target_x)
                if callback:
                    callback()

        widget.place(x=start_x)


class AnimatedButton(ctk.CTkButton):
    """带动画效果的按钮"""

    def __init__(self, master, **kwargs):
        self._hover_scale = kwargs.pop("hover_scale", 1.05)
        self._click_scale = kwargs.pop("click_scale", 0.95)
        self._original_color = kwargs.get("fg_color", ("#3B8ED0", "#1F6AA5"))
        super().__init__(master, **kwargs)

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_enter(self, e):
        """鼠标进入"""
        self.configure(cursor="hand2")

    def _on_leave(self, e):
        """鼠标离开"""
        self.configure(cursor="")

    def _on_press(self, e):
        """按下"""
        pass

    def _on_release(self, e):
        """释放"""
        pass


class AnimatedProgressBar(ctk.CTkProgressBar):
    """带动画的进度条"""

    def __init__(self, master, **kwargs):
        self._animation_speed = kwargs.pop("animation_speed", 0.02)
        super().__init__(master, **kwargs)
        self._target_value = 0
        self._animating = False

    def set_smooth(self, value, duration=500):
        """平滑设置进度值"""
        self._target_value = value
        if not self._animating:
            self._animate_to_target(duration)

    def _animate_to_target(self, duration):
        """动画到目标值"""
        self._animating = True
        current = self.get()
        target = self._target_value

        if abs(current - target) < 0.01:
            self.set(target)
            self._animating = False
            return

        steps = 15
        delay = duration // steps
        step_size = (target - current) / steps

        def _step(val, remaining):
            if remaining <= 0:
                self.set(target)
                self._animating = False
                return

            new_val = val + step_size
            self.set(new_val)
            self.after(delay, lambda: _step(new_val, remaining - 1))

        _step(current, steps)


class LoadingSpinner(ctk.CTkFrame):
    """加载旋转动画"""

    def __init__(self, master, size=40, **kwargs):
        super().__init__(master, width=size, height=size, **kwargs)

        self._size = size
        self._angle = 0
        self._running = False
        self._canvas = ctk.CTkCanvas(self, width=size, height=size,
                                      highlightthickness=0, bg=self._apply_appearance_mode(self.cget("fg_color")))
        self._canvas.pack()

    def start(self):
        """开始旋转"""
        self._running = True
        self._rotate()

    def stop(self):
        """停止旋转"""
        self._running = False

    def _rotate(self):
        """旋转一帧"""
        if not self._running:
            return

        self._canvas.delete("all")
        self._angle = (self._angle + 30) % 360

        # 绘制弧形
        x, y = self._size // 2, self._size // 2
        r = self._size // 2 - 4
        self._canvas.create_arc(
            x - r, y - r, x + r, y + r,
            start=self._angle, extent=120,
            outline=self._apply_appearance_mode("#3B8ED0"),
            width=3, style="arc"
        )

        self.after(50, self._rotate)


class SmoothScrollableFrame(ctk.CTkScrollableFrame):
    """平滑滚动框架"""

    def __init__(self, master, **kwargs):
        self._scroll_speed = kwargs.pop("scroll_speed", 3)
        super().__init__(master, **kwargs)

        # 绑定鼠标滚轮
        self.bind("<MouseWheel>", self._on_mousewheel)
        self.bind("<Button-4>", self._on_mousewheel_linux)
        self.bind("<Button-5>", self._on_mousewheel_linux)

    def _on_mousewheel(self, event):
        """Windows/Mac 滚轮"""
        delta = -1 * (event.delta // 120) * self._scroll_speed
        self._parent_canvas.yview_scroll(delta, "units")

    def _on_mousewheel_linux(self, event):
        """Linux 滚轮"""
        if event.num == 4:
            delta = -self._scroll_speed
        else:
            delta = self._scroll_speed
        self._parent_canvas.yview_scroll(delta, "units")


class GlowEffect:
    """发光效果（用于按钮悬停）"""

    def __init__(self, widget, color="#3B8ED0", intensity=3):
        self._widget = widget
        self._color = color
        self._intensity = intensity
        self._original_border_width = widget.cget("border_width") if hasattr(widget, 'cget') else 0

    def apply(self):
        """应用发光效果"""
        try:
            self._widget.configure(border_width=self._intensity,
                                   border_color=self._color)
        except Exception:
            pass

    def remove(self):
        """移除发光效果"""
        try:
            self._widget.configure(border_width=self._original_border_width)
        except Exception:
            pass


def animate_text_typing(widget, text, delay=50, callback=None):
    """打字机效果"""
    def _type(index):
        if index <= len(text):
            widget.delete("1.0", "end")
            widget.insert("1.0", text[:index])
            widget.after(delay, lambda: _type(index + 1))
        else:
            if callback:
                callback()

    _type(0)


def animate_color_transition(widget, from_color, to_color, duration=500, attr="fg_color"):
    """颜色过渡动画"""
    steps = 15
    delay = duration // steps

    # 解析颜色
    try:
        r1, g1, b1 = int(from_color[1:3], 16), int(from_color[3:5], 16), int(from_color[5:7], 16)
        r2, g2, b2 = int(to_color[1:3], 16), int(to_color[3:5], 16), int(to_color[5:7], 16)
    except Exception:
        return

    def _step(current_step):
        if current_step > steps:
            return

        ratio = current_step / steps
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        color = f"#{r:02x}{g:02x}{b:02x}"

        try:
            widget.configure(**{attr: color})
        except Exception:
            pass

        widget.after(delay, lambda: _step(current_step + 1))

    _step(0)


def pulse_widget(widget, color1="#3B8ED0", color2="#2563EB", cycles=3, duration=1000):
    """脉冲效果"""
    def _pulse(remaining):
        if remaining <= 0:
            return
        animate_color_transition(widget, color1, color2, duration // 2)
        widget.after(duration // 2, lambda: animate_color_transition(widget, color2, color1, duration // 2))
        widget.after(duration, lambda: _pulse(remaining - 1))

    _pulse(cycles)
