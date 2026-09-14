import tkinter as tk
from tkinter import ttk
from typing import Callable
import ctypes


class Scale(ttk.Scale):
    def __init__(
        self,
        parent,
        from_=0, 
        to=100,
        rtl=False,
        **kwargs
    ):

        if rtl:
            to, from_ = from_, to

        super().__init__(parent, from_=from_, to=to, **kwargs)







class Entry(ttk.Entry):
    """
    Entry يسمح فقط بـ:
    - الأرقام 0-9
    - الإشارة -
    - الفاصلة ,

    ويرفض:
    - فواصل متتابعة ,,
    - شرطات متتابعة --
    """

    _ALLOWED_CHARS = set("0123456789-,")

    def __init__(self, master=None, placeholder="", validator=None, **kwargs):
        super().__init__(master, **kwargs)

        self.placeholder = placeholder
        self.validator = validator or self.default_validator

        self._placeholder_active = False
        self._programmatic = False

        self._normal_fg = super().cget("foreground")
        if not self._normal_fg:
            self._normal_fg = self.tk.call(
                "ttk::style", "lookup", "TEntry", "-foreground"
            ) or "black"

        # منع التعديل غير الصالح قبل حدوثه
        vcmd = (self.register(self._validate_key), "%P")
        super().configure(validate="key", validatecommand=vcmd)

        if self.placeholder:
            self._insert_placeholder()

        self.bind("<FocusIn>", self.remove_placeholder)
        self.bind("<FocusOut>", self.add_placeholder)
        self.bind("<KeyRelease>", self.check_empty)

    @classmethod
    def default_validator(cls, value: str) -> bool:
        return cls.is_allowed(value)

    @classmethod
    def is_allowed(cls, value: str) -> bool:
        """
        يسمح فقط بـ:
        0-9 و - و ,

        ويرفض:
        ,, و --
        """
        if not value:
            return True

        if any(ch not in cls._ALLOWED_CHARS for ch in value):
            return False

        if "--" in value or ",," in value:
            return False

        return True

    def _validate_key(self, proposed_value: str) -> bool:
        """
        يتم استدعاؤها قبل قبول التعديل داخل الـ Entry.
        proposed_value هو النص الذي سيصبح عليه الـ Entry بعد التعديل.
        """
        # أثناء إضافة/إزالة placeholder لا نرفض النص
        if self._programmatic:
            return True

        return self.is_allowed(proposed_value or "")

    def _insert_placeholder(self):
        if not self.placeholder or self._placeholder_active:
            return

        if str(super().cget("state")) == "disabled":
            return

        self._programmatic = True
        try:
            if super().get() == "":
                super().configure(foreground="gray")
                super().insert(0, self.placeholder)
                self._placeholder_active = True
        finally:
            self._programmatic = False

    def _remove_placeholder(self):
        if not self._placeholder_active:
            return

        self._programmatic = True
        try:
            if super().get() == self.placeholder:
                super().delete(0, "end")

            super().configure(foreground=self._normal_fg)
        finally:
            self._programmatic = False

        self._placeholder_active = False

    def configure(self, *args, **kwargs):
        state = kwargs.pop("state", None)

        if state in ("enable", "enabled", "normal"):
            super().configure(state="normal")

            if args or kwargs:
                super().configure(*args, **kwargs)

            self.add_placeholder(None)
            return

        if state in ("disable", "disabled"):
            self._programmatic = True
            try:
                super().delete(0, "end")
            finally:
                self._programmatic = False

            self._placeholder_active = False
            self.state(["!invalid"])
            super().configure(state="disabled")

            if args or kwargs:
                super().configure(*args, **kwargs)

            return

        if state is not None:
            kwargs["state"] = state

        if args or kwargs:
            super().configure(*args, **kwargs)

    config = configure

    def validate(self, *_):
        """
        للتحقق البصري فقط، مثل تغيير حالة invalid.
        أما المنع الفعلي للإدخال غير الصالح فيتم داخل _validate_key.
        """
        if self._placeholder_active:
            self.state(["!invalid"])
            return

        try:
            ok = bool(self.validator(self.get()))
        except Exception:
            ok = False

        if ok:
            self.state(["!invalid"])
        else:
            self.state(["invalid"])

    def remove_placeholder(self, event=None):
        self._remove_placeholder()

    def add_placeholder(self, event=None):
        if super().get() == "":
            self._insert_placeholder()
        self.validate()

    def check_empty(self, event=None):
        if self._placeholder_active:
            return
        self.validate()

    def get(self):
        if self._placeholder_active and super().get() == self.placeholder:
            return ""
        return super().get()



class Combobox(ttk.Combobox):
    """
    A custom Combobox widget with placeholder text functionality.
    Parameters:
    container : widget
        The parent widget.
    placeholder : str, optional
        The placeholder text to display when no selection is made (default is "Select an option...").
    *args : tuple
        Additional positional arguments passed to the ttk.Combobox.
    **kwargs : dict
        Additional keyword arguments passed to the ttk.Combobox.
    Methods:
    _clear_placeholder(event=None)
        Clears the placeholder text when the widget gains focus.
    _add_placeholder(event=None)
        Adds the placeholder text when the widget loses focus and no selection is made.
    _on_select(event=None)
        Handles the event when an option is selected from the combobox.
    get()
        Returns the current value of the combobox, or an empty string if the placeholder is active.
    configure(*args, **kwargs)
        Configures the combobox widget. Handles enabling and disabling of the widget and manages the placeholder text accordingly.
    """

    def __init__(self, container, placeholder="Select an option...", *args, **kwargs):
        super().__init__(container, foreground='gray', *args, **kwargs)
        
        self.placeholder = placeholder
        self.placeholder_active = True
        
        # Set initial placeholder
        self.set(self.placeholder)
        
        # Bind events
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)
        self.bind("<<ComboboxSelected>>", self._on_select)
        
    
    def _clear_placeholder(self, event=None):
        if self.placeholder_active:
            self.set('')
            self.placeholder_active = False
    
    def _add_placeholder(self, event=None):
        if not self.get():
            self.set(self.placeholder)
            self.placeholder_active = True
    
    def _on_select(self, event=None):
        self.placeholder_active = False
        color = self.tk.call("ttk::style", "lookup", "TLabel", "-foreground")

        self.config(foreground=color)
    
    def get(self):
        # Return empty string if placeholder is active
        if self.placeholder_active:
            return ''
        return super().get()

    def clear(self):
        # super().config(foreground='gray')
        # self.set(self.placeholder)
        # self.placeholder_active = True
        # if not self.get():
        self.set(self.placeholder)
        self.placeholder_active = True


    def configure(self, *args, **kwargs):
        if kwargs.get("state") == "enable":
            self._add_placeholder(None)

        if kwargs.get("state") == "disable":
            self.set('')
            super().config(foreground='gray')
        
        super().config(*args, **kwargs)
    
    config = configure



class Treeview(ttk.Treeview):
    def __init__(self, parent, on_select:Callable, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.bind("<<TreeviewSelect>>", self.on_row_select)

        self.on_select = on_select
    
    
    def move_up(self, *args, **kwargs):
        leaves = self.selection()
        for i in leaves:
            self.move(i, self.parent(i), self.index(i)-1)


    def move_down(self, *args, **kwargs):
        leaves = self.selection()
        for i in reversed(leaves):
            self.move(i, self.parent(i), self.index(i)+1)
    

    def remove_item(self, *args, **kwargs):
        leaves = self.selection()
        if leaves:
            self.delete(leaves[0])



    def on_row_select(self, *args, **kws):
        selected_item = self.selection()
        if selected_item:
            values = self.item(selected_item[0], 'values')
            self.on_select(values)



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



GWL_WND_PROC = -4
WM_DROP_FILES = 0x233
_MAX_SESSIONS = 10

_GetWindowLong = ctypes.windll.user32.GetWindowLongPtrA
_SetWindowLong = ctypes.windll.user32.SetWindowLongPtrA
_typ = ctypes.c_uint64
_prototype = ctypes.WINFUNCTYPE(_typ, _typ, _typ, _typ, _typ)

# سجلّ كل الجلسات النشطة: hwnd -> {'old_proc': ..., 'new_proc_obj': ...}
# مفتاحه hwnd (رقم نافذة ويندوز الخام) وليس عنصر tkinter نفسه، لذا يبقى صالحاً
# للاستخدام حتى لو دُمِّر عنصر tkinter لاحقاً (clear_all_dnd لا تحتاج عناصر حية).
_dnd_sessions = {}


class apply_dnd():
    """apply file drag and drop in a widget"""

    def __init__(self, widget, func: Callable, char_limit: int = 260) -> None:

        hwnd = widget.winfo_id()

        if hwnd in _dnd_sessions:
            raise ValueError("DND already applied to this widget. Call clear_dnd(widget) first.")

        if len(_dnd_sessions) >= _MAX_SESSIONS:
            raise OverflowError("DND limit reached for this session!")

        create_buffer = ctypes.create_unicode_buffer
        func_DragQueryFile = ctypes.windll.shell32.DragQueryFileW

        # حاوية قابلة للتعديل بدل متغير global كي يحمل كل عنصر مرجعه الخاص لـ proc الأصلي
        state = {}

        def py_drop_func(hwnd_, msg, wp, lp):
            if msg == WM_DROP_FILES:
                count = func_DragQueryFile(_typ(wp), -1, None, 0)
                file_buffer = create_buffer(char_limit)
                files = []
                for i in range(count):
                    func_DragQueryFile(_typ(wp), i, file_buffer, char_limit)
                    files.append(file_buffer.value)
                func(files)
                ctypes.windll.shell32.DragFinish(_typ(wp))

            return ctypes.windll.user32.CallWindowProcW(
                *map(_typ, (state['old_proc'], hwnd_, msg, wp, lp))
            )

        new_proc = _prototype(py_drop_func)

        ctypes.windll.shell32.DragAcceptFiles(hwnd, True)
        state['old_proc'] = _GetWindowLong(hwnd, GWL_WND_PROC)
        _SetWindowLong(hwnd, GWL_WND_PROC, new_proc)

        # لازم الاحتفاظ بمرجع new_proc هنا (new_proc_obj)، وإلا يجمعه garbage collector
        # ويصبح المؤشر الذي يعرفه Windows الآن غير صالح.
        _dnd_sessions[hwnd] = {'old_proc': state['old_proc'], 'new_proc_obj': new_proc}
        self.hwnd = hwnd


def clear_dnd(widget) -> bool:
    """يزيل خاصية السحب والإفلات عن عنصر واحد فقط، ويعيد window proc الأصلي.
    يرجع True إن كان مسجَّلاً وأُزيل، أو False إن لم يكن مسجَّلاً أصلاً."""
    hwnd = widget.winfo_id()
    session = _dnd_sessions.pop(hwnd, None)
    if session is None:
        return False
    _SetWindowLong(hwnd, GWL_WND_PROC, session['old_proc'])
    ctypes.windll.shell32.DragAcceptFiles(hwnd, False)
    return True


def clear_all_dnd() -> int:
    """يزيل خاصية السحب والإفلات عن كل العناصر المسجَّلة في هذه الجلسة، ويعيد
    window proc الأصلي لكل منها (بالترتيب الصحيح: استعادة أولاً ثم تحرير المرجع)،
    ويعيد فتح كل الحصص العشر للاستخدام من جديد. يرجع عدد الجلسات التي أُزيلت."""
    count = 0
    for hwnd, session in list(_dnd_sessions.items()):
        _SetWindowLong(hwnd, GWL_WND_PROC, session['old_proc'])
        ctypes.windll.shell32.DragAcceptFiles(hwnd, False)
        del _dnd_sessions[hwnd]
        count += 1
    return count


