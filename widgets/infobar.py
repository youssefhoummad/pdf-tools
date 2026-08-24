import tkinter as tk

class InfoBar(tk.Frame):
    def __init__(self, parent, title, text, info_type="success", duration=5000, rtl=False):
        """
        Create a styled InfoBar with horizontal sliding animation.
        :param parent: Parent widget to contain the InfoBar.
        :param title: Title to display on the InfoBar.
        :param text: The message to display in the InfoBar.
        :param info_type: The type of InfoBar ("success", "warning", or "error").
        :param duration: Time in milliseconds before the InfoBar hides automatically.
        :param rtl: If True, layout and animation are right-to-left.
        """
        super().__init__(parent)
        self.rtl = rtl

        # تحديد اتجاهات pack
        if rtl:
            LEFT, RIGHT = 'right', 'left'   # عكس الاتجاه
            justify = 'right'
            anchor = 'e'
        else:
            LEFT, RIGHT = 'left', 'right'
            justify = 'left'
            anchor = 'w'

        # تعريف الأنماط حسب النوع
        if info_type == "success":
            bg_color = "#d4edda"
            fg_color = "#155724"
            border_color = "#c3e6cb"
            icon_text = ""  # أيقونة نجاح
        elif info_type == "warning":
            bg_color = "#fff3cd"
            fg_color = "#856404"
            border_color = "#ffeeba"
            icon_text = u'\ue814'  # أيقونة تحذير
        else:  # error
            bg_color = "#f8d7da"
            fg_color = "#721c24"
            border_color = "#f5c6cb"
            icon_text = ""  # أيقونة خطأ

        self.config(
            bg=bg_color,
            padx=10,
            pady=10,
            highlightbackground=border_color,
            highlightthickness=1,
            bd=0,
            width=450,
        )

        # الأيقونة
        icon_label = tk.Label(self, text=icon_text, bg=bg_color, fg=fg_color,
                              font=("Segoe Fluent Icons", 14, "normal"))
        icon_label.pack(side=LEFT, padx=5)

        # العنوان
        title_label = tk.Label(self, text=title, bg=bg_color, fg=fg_color,
                               font=("Segoe UI", 11, "bold"))
        title_label.pack(side=LEFT, padx=5)

        # الرسالة (مع مراعاة الاتجاه)
        message_label = tk.Label(self, text=text, bg=bg_color,
                                 font=("Segoe UI", 10, "normal"),
                                 fg=fg_color, anchor=anchor,
                                 justify=justify, wraplength=300)
        message_label.pack(side=LEFT, fill="both", expand=True, padx=5)

        # زر الإغلاق
        close_button = tk.Button(
            self,
            text="",
            bg=bg_color,
            fg=fg_color,
            relief="flat",
            font=("Segoe Fluent Icons", 10, "bold"),
            command=self.destroy,
            highlightthickness=0,
            activebackground=bg_color,
            bd=0
        )
        close_button.pack(side=RIGHT)

        # حساب العرض المناسب
        width = len(text) * 8 + 140
        if width > 400:
            width = 400
        self._width = width

        self._duration = duration
        self._parent = parent
        self._current_x = 0
        self._target_x = 0

        # تعيين الموضع الأولي حسب الاتجاه
        parent_width = parent.winfo_width()
        if rtl:
            # نبدأ من اليسار (x=0) ونتحرك إلى اليمين
            self._current_x = -width          # مخفي تماماً على اليسار
            self._target_x = 10               # مكان ظهوره (بعد هامش صغير)
        else:
            # نبدأ من اليمين (x=parent_width) ونتحرك لليسار
            self._current_x = parent_width
            self._target_x = parent_width - width - 10

        self.place(x=self._current_x, y=10, width=width)

    def show(self):
        """Show the InfoBar with a sliding animation."""
        self.after(10, self._slide_in)

    def _slide_in(self):
        """Slide the InfoBar into view from the correct side."""
        step = 10
        if self.rtl:
            # التحرك من اليسار إلى اليمين (زيادة x)
            if self._current_x < self._target_x:
                self._current_x += step
                self.place_configure(x=self._current_x)
                self.after(5, self._slide_in)
            else:
                self.after(self._duration, self.hide)
        else:
            # التحرك من اليمين إلى اليسار (نقصان x)
            if self._current_x > self._target_x:
                self._current_x -= step
                self.place_configure(x=self._current_x)
                self.after(5, self._slide_in)
            else:
                self.after(self._duration, self.hide)

    def hide(self):
        """Hide the InfoBar with a sliding animation out."""
        self._slide_out()

    def _slide_out(self):
        """Slide the InfoBar out to the correct side."""
        step = 10
        parent_width = self._parent.winfo_width()
        if self.rtl:
            # التحرك إلى اليسار (نقصان x)
            if self._current_x > -self._width:
                self._current_x -= step
                self.place_configure(x=self._current_x)
                self.after(10, self._slide_out)
            else:
                self.destroy()
        else:
            # التحرك إلى اليمين (زيادة x)
            if self._current_x < parent_width:
                self._current_x += step
                self.place_configure(x=self._current_x)
                self.after(10, self._slide_out)
            else:
                self.destroy()

# === اختبار ===
if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("500x200")
    root.title("InfoBar RTL Test")

    def show_info():
        infobar = InfoBar(root, "نجاح", "تمت العملية بنجاح!", "success", 5000)
        infobar.show()

    def show_warning():
        infobar = InfoBar(root, "تحذير", "هذا تحذير مهم!", "warning", 5000, rtl=True)
        infobar.show()

    def show_error():
        infobar = InfoBar(root, "خطأ", "حدث خطأ غير متوقع!", "error", 5000, rtl=True)
        infobar.show()

    tk.Button(root, text="عرض نجاح", command=show_info).pack(pady=10)
    tk.Button(root, text="عرض تحذير", command=show_warning).pack(pady=10)
    tk.Button(root, text="عرض خطأ", command=show_error).pack(pady=10)

    root.mainloop()