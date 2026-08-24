import tkinter as tk
from tkinter import ttk
from winreg import *


def get_accent_color():
    """
    Return the Windows 10 accent color used by the user in a HEX format
    """
    registry = ConnectRegistry(None, HKEY_CURRENT_USER)
    key = OpenKey(registry, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Accent')
    key_value = QueryValueEx(key, 'AccentColorMenu')
    accent_int = key_value[0]
    accent = accent_int - 4278190080
    accent = str(hex(accent)).split('x')[1]
    accent = accent[4:6] + accent[2:4] + accent[0:2]
    return '#' + accent


default_colors = {"accent": get_accent_color(), "bg": '#EFF4F8', "hover": '#E8EBF0', "press": '#D6D9DE'}


class Pivot(tk.Frame):
    _id = 0

    def __init__(self, master=None, padding=[], colors=default_colors, **kw):
        self.justify = kw.pop('justify', 'left')
        super().__init__(master, **kw)

        self.colors = self.set_colors(colors)
        self.padding = padding

        self.topbar = tk.Frame(self, bg=self.colors['bg'], height=50)
        self.mainerea = tk.Frame(self, bg=master['bg'])

        self.topbar.pack(fill='x')
        self.topbar.pack_propagate(False)
        self.mainerea.pack(fill='both', expand=True)
        self.mainerea.pack_propagate(False)

        self.tabs = {}
        self.bar = tk.Frame(self.topbar, height=3, bg=self.colors['accent'])
        self.bar.place(x=0, y=42, width=0, height=3)  # Initially hidden


    def set_colors(self, colors):
        _colors = default_colors
        if colors:
            for key, value in colors.items():
                if value != 'default':
                    _colors[key] = value
        return _colors


    def add(self, widget, text, icon=None, to_end=False, **packoptions):
        tab = Tab(self.topbar, text, colors=self.colors,
                     command=lambda: self.show(widget),
                     icon=icon,
                     justify=self.justify)

        left, right = 'left', 'right'
        if self.justify == 'right':
            left, right = right, left

        if not to_end:
            tab.pack(side=left, padx=8, pady=8)
        else:
            tab.pack(side=right, padx=8, pady=8)

        self.tabs[self._id] = tab
        self._id += 1


    def show(self, widget):
        # Clean mainerea
        [w.forget() for w in self.mainerea.pack_slaves()]
        # Pack new frame
        widget.pack(in_=self.mainerea, fill='both', expand=True)

        self.animate_bar()
        

    def animate_bar(self):
        # Get the current bar position
        current_x = self.bar.winfo_x()
        current_width = self.bar.winfo_width()


        tab_id = self.current()
        tab = self.tabs[tab_id]

        # Get the target position and width
        target_x = tab.winfo_x()
        target_width = tab.winfo_width()

        if target_x == 0:
            target_x = 8
        if target_width == 1:
            target_width = tab.width

        # Animate the bar sliding
        def step():
            nonlocal current_x, current_width
            dx = (target_x - current_x) / 5
            dw = (target_width - current_width) / 5
            if abs(dx) < 1 and abs(dw) < 1:
                self.bar.place(x=target_x, y=42, width=target_width, height=3)
            else:
                current_x += dx
                current_width += dw
                self.bar.place(x=int(current_x), y=42, width=int(current_width), height=3)
                self.after(16, step)

        step()


    def select(self, _id: int) -> None:
        tab = self.tabs.get(_id)
        if tab:
            tab.on_active()
            tab.on_release()
    

    def current(self) -> int:
        for _id, tab in self.tabs.items():
            if tab.active:
                return _id
    
    def index(self, text: str) -> int:
        if text == "current":
            return self.current()
        if text in self.tabs.values():
            for _id, tab in self.tabs.items():
                if tab.text['text'] == text:
                    return _id
        return -1

    def text(self, _id: int):
        tab = self.tabs.get(_id)
        if tab:
            return tab.text['text']



class Tab(tk.Frame):
    instances = set()

    def __init__(self, master, text, icon="", colors=[], command=None, **kw):
        justify = kw.pop('justify', 'left')
        super().__init__(master, **kw)

        left, right = 'left', 'right'
        if justify == 'right':
            left, right = right, left

        self.width = len(text) * 8 + 50
        self.config(cursor='hand2', height=46, padx=10, width=self.width , bg=master['bg'])

        self.command = command
        self.colors = colors

        self.active = False

        self.text = tk.Label(self, text=text, bg=self['bg'])
        self.icon = tk.Label(self, text=icon, font=('Segoe Fluent Icons', 14, 'normal'), bg=self['bg'])

        self.icon.pack(side=left)
        self.text.pack(side=left, pady=(8, 10))

        for w in [self, self.icon, self.text]:
            w.bind("<ButtonPress-1>", self.on_press)
            w.bind("<ButtonRelease-1>", self.on_release)
            w.bind("<Enter>", self.on_hover)
            w.bind("<Leave>", self.on_leave)

        type(self).instances.add(self)
        self.pack_propagate(False)

    def on_hover(self, *args):
        if self.active:
            self.on_press()
        else:
            self.config(bg=self.colors['hover'])
            self.text.config(bg=self.colors['hover'])
            self.icon.config(bg=self.colors['hover'])
        self.text.config(fg='black')
        self.icon.config(fg='black')

    def on_press(self, *args):
        self.config(bg=self.colors['press'])
        self.text.config(bg=self.colors['press'], fg='gray')
        self.icon.config(bg=self.colors['press'], fg='gray')

        for btn in type(self).instances:
            try:
                btn.on_disactive()
            except:
                pass
        self.on_active()

    def on_leave(self, *args):
        if self.active:
            self.on_press()
        else:
            self.config(bg=self.colors['bg'])
            self.text.config(bg=self.colors['bg'])
            self.icon.config(bg=self.colors['bg'])
        self.text.config(fg='black')
        self.icon.config(fg='black')

    def on_release(self, *args):
        self.on_hover()
        self.command()

    def on_active(self):
        self.active = True
        self.config(bg=self.colors['press'])
        self.text.config(bg=self.colors['press'])
        self.icon.config(bg=self.colors['press'])

    def on_disactive(self):
        self.active = False
        self.config(bg=self.colors['bg'])
        self.text.config(bg=self.colors['bg'])
        self.icon.config(bg=self.colors['bg'])


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Pivot navigation')
    root.geometry('800x600')

    pivot = Pivot(root)
    pivot.pack(fill='both', expand=True)

    f1 = tk.Frame(pivot.mainerea, bg='red')
    f2 = tk.Frame(pivot.mainerea, bg='yellow')
    f3 = tk.Frame(pivot.mainerea, bg='green')
    f5 = tk.Frame(pivot.mainerea, bg='purple')

    pivot.add(f1, 'Tools', icon=u'\uec7a')
    pivot.add(f2, 'Merge PDFs', icon=u'\uea90')
    pivot.add(f3, 'To PDF', icon=u'\ue7aa')
    pivot.add(f5, '', icon=u'\ue713', to_end=True)

    pivot.select(0)
    # pivot.animate_bar()

    root.mainloop()
