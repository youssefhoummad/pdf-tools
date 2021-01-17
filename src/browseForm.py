import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename

from .constant import *

class BrowseForm(tk.Frame):
  """
  docstring
  """
  def __init__(self, parent, textvariable, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.config( bg=parent['background'])

    self.textvariable = textvariable

    ttk.Entry(self, state='disabled', textvariable=textvariable,foreground='gray').pack(side=START_DIR, padx=END_PADDING_10, expand=True, fill='x')
    ttk.Button(self, text=BROWSE,command=self.browse).pack(side=START_DIR)

  
  def browse(self):
    path = askopenfilename(initialdir = "/",title = "Select file",filetypes = (("pdf files","*.pdf"),("all files","*.*")))
    if path == "": return
    self.textvariable.set(path)


    # _f.pack(padx=24, anchor='nw', fill='x', expand=True)
