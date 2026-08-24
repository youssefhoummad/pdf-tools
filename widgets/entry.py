import tkinter as tk
from tkinter import ttk


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


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("250x100")

    # validator اختياري هنا لأن default_validator يطبق نفس القاعدة
    entry = Entry(root, placeholder="مثال: 1,2,-3")
    entry.pack(padx=10, pady=10, fill="x")

    root.mainloop()