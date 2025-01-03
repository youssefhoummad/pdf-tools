
import ctypes
from typing import Callable


class apply_dnd():
    """apply file drag and drop in a widget"""
    
    def __init__(self, widget: int, func: Callable, char_limit: int=260) -> None:

        hwnd = widget.winfo_id()

        GetWindowLong = ctypes.windll.user32.GetWindowLongPtrA
        SetWindowLong = ctypes.windll.user32.SetWindowLongPtrA
        typ = ctypes.c_uint64

        prototype = ctypes.WINFUNCTYPE(typ, typ, typ, typ, typ)
        WM_DROP_FILES = 0x233
        GWL_WND_PROC = -4
        create_buffer = ctypes.c_buffer
        func_DragQueryFile = (ctypes.windll.shell32.DragQueryFile)

        def py_drop_func(hwnd, msg, wp, lp):
            global files
            if msg == WM_DROP_FILES:
                count = func_DragQueryFile(typ(wp), -1, None, None)
                file_buffer = create_buffer(char_limit)
                files = []
                for i in range(count):
                    func_DragQueryFile(typ(wp), i, file_buffer, ctypes.sizeof(file_buffer))
                    drop_name = file_buffer.value.decode("utf-8")
                    files.append(drop_name)
                func(files)
                ctypes.windll.shell32.DragFinish(typ(wp))

            return ctypes.windll.user32.CallWindowProcW(
                *map(typ, (globals()[old], hwnd, msg, wp, lp))
            )

        """ Allow upto 10 widgets only to have dnd feature in one window, reduces system uses"""
        limit_num = 10
        for i in range(limit_num):
            if i + 1 == limit_num:
                raise OverflowError("DND limit reached for this session!")
            owp = f"old_wnd_proc_{i}"
            if owp not in globals():
                old, new = owp, f"new_wnd_proc_{i}"
                break

        globals()[old] = None
        globals()[new] = prototype(py_drop_func)

        ctypes.windll.shell32.DragAcceptFiles(hwnd, True)
        globals()[old] = GetWindowLong(hwnd, GWL_WND_PROC)
        SetWindowLong(hwnd, GWL_WND_PROC, globals()[new])

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
    root.mainloop()



