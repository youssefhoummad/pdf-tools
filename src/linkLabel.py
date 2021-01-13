import tkinter as tk
from tkinter import ttk

from webbrowser import open_new_tab


class LinkLabel(ttk.Label):
  def __init__(self, parent, text, link='', **kw):
    ttk.Label.__init__(self, parent, **kw)
    
    self.config(cursor='hand2', foreground="blue", text=text)
    self.bind("<Button-1>", lambda e: open_new_tab(link))



if __name__ == "__main__":
    root = tk.Tk()
    label = LinkLabel(root, text="click me", link="www.google.com")
    label.pack()
    root.mainloop()