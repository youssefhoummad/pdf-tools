# import tkinter as tk
from tkinter import Frame, Button, Entry
from tkinter import ttk
from tkinter.filedialog import askopenfilename, askopenfilenames



class BrowseForm(Frame):
  """
  docstring
  """
  def __init__(self, parent, textvariable, *args, **kwargs):
    justify = kwargs.get('justify', 'left')
    kwargs.pop('justify', None)
    padding = (10,0)
    if justify == 'left': padding =(0,10)

    text = kwargs.get('text', 'browse')
    kwargs.pop('text', None)
    

    super().__init__(parent, *args, **kwargs)
    self.config( bg=parent['background'])
    self.s = ttk.Style() 
    self.s.configure('TButton', background=parent['background'])

    self.textvariable = textvariable

    self.text = kwargs.get('text', 'browse')
    self.initialdir = kwargs.get('initialdir', '/')
    self.title = kwargs.get('title', 'Select file')
    self.filetypes = (("files","*.*"),("all files","*.*"))


    ttk.Entry(self, state='disabled', textvariable=textvariable,foreground='gray').pack(side=justify, padx=padding, expand=True, fill='x')
    ttk.Button(self, text=text,command=self.browse).pack(side=justify)

  
  def browse(self):
    path = askopenfilename(initialdir = self.initialdir,title =self.title, filetypes=self.filetypes)
    if path == "": return
    self.textvariable.set(path)


class BrowsePDF(BrowseForm):
  def __init__(self, parent, textvariable, *args, **kwargs):
    super().__init__(parent, textvariable, *args, **kwargs)
    self.title = "Select PDF"
    self.filetypes = (("pdf files","*.pdf"),("all files","*.*"))


class BrowseImage(BrowseForm):
  def __init__(self, parent, textvariable, *args, **kwargs):
    super().__init__(parent, textvariable, *args, **kwargs)
    self.title = "Select images"
    self.filetypes = (("image files","*.jpg *.png *.jpeg *.tif"),("all files","*.*"))

