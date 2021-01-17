import tkinter as tk
from .constant import *

class CardFrame(tk.Frame):
  def __init__(self, parent, title, content, background=None):
    tk.Frame.__init__(self, parent)
    
    self.bg = parent['background']
    self.configure(bg=self.bg)

    tk.Label(self, bg=self.bg, text=title, justify=START_DIR,  anchor=NW,font=(FONT,22,"bold")).pack(padx=START_PADDING_24,fill="both", pady=START_PADDING_24_0)
    tk.Label(self, bg=self.bg, text=content,  fg='gray', anchor=NW,justify=START_DIR, font=(FONT_1,10,"normal")).pack(fill='both', padx=START_PADDING_24)


if __name__ == "__main__":
    root = tk.Tk()
    f = CardFrame(root, "PDF tools", "PDF tools is a collections of tools \nthat will works with pdf fils")
    f.pack(fill='both', expand='True')
    root.mainloop()
