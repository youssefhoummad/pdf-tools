import tkinter as tk
from tkinter import ttk


class Showinfo(tk.Toplevel):
  def __init__(self, parent, title, message, **kw):
    tk.Toplevel.__init__(self, parent, **kw)

    self.parent = parent
    self.bell()
    self.transient(parent) # remove minimize maximize button
    self.resizable(False, False)
    self.details_expanded = False
    self.title(title)
    self.iconbitmap(r"C:\Users\youssef\AppData\Local\Programs\Python\Python37\DLLs\icon.ico")
    self.grab_set()
    self.focus()
    self.bind("<Escape>", lambda x: self.destroy())


    width = kw.get('width', 250)
    height = kw.get('height', 100)

    x = parent.winfo_x() + (parent.winfo_width() - width) // 2
    y = parent.winfo_y()

    self.geometry("{}x{}+{}+{}".format(width,height, x, y))

    self.rowconfigure(0, weight=0)
    self.rowconfigure(1, weight=1)
    self.columnconfigure(0, weight=1)
    self.columnconfigure(1, weight=1)

    tk.Label(self, image="::tk::icons::information").grid(row=0, column=0, pady=(7, 0), padx=(7, 7), sticky="e")
    tk.Label(self, text=message).grid(row=0, column=1, columnspan=2, pady=(7, 7), sticky="w")
    ttk.Button(self, text="OK", command=self.destroy).grid(row=1, column=2, padx=(7, 7), sticky="e")


  