import tkinter as tk
from tkinter import ttk

from webbrowser import open_new_tab

from .constant import *


class LinkLabel(ttk.Label):
  def __init__(self, parent, text, link='', **kw):
    ttk.Label.__init__(self, parent, **kw)
    
    self.config(cursor='hand2',anchor=NW, foreground=P_COLOR, justify=START_DIR, text=text, background=parent['background'], font=('Calibri',12,"normal"))
    self.bind("<Button-1>", lambda e: open_new_tab(link))



if __name__ == "__main__":
    root = tk.Tk()
    label = LinkLabel(root, text="click me", link="www.google.com")
    label.pack()
    root.mainloop()