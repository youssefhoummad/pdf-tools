import ctypes
from typing import Callable


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


if __name__ == "__main__":
    import tkinter as tk

    root = tk.Tk()
    root.geometry("500x500")
    root.title("DND Test")

    def on_drop(files):
        print(files)

    # canvas drag zone
    canvas = tk.Canvas(root, bg='white', width=500, height=500)
    canvas.pack(fill='both', expand=True)
    dashed = canvas.create_rectangle(100, 100, 400, 400, dash=(10, 4), outline='black')
    dashed_text = canvas.create_text(250, 250, text="Drop files here", fill='black', font=('Arial', 12))

    apply_dnd(canvas, on_drop)

    # مثال: زر لمسح كل جلسات DND في النافذة
    tk.Button(root, text="Clear all DND", command=clear_all_dnd).pack(side='bottom', pady=8)

    root.mainloop()