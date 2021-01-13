import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

class ImageLabel(ttk.Label):
  def __init__(self, parent, image_path, width=80, height=80, **kw):
    ttk.Label.__init__(self, parent, **kw)
    try:
      self._img = Image.open(image_path)
    except:
      self._img = image_path
    self._img.thumbnail((width , height), Image.ANTIALIAS)
    self._img = ImageTk.PhotoImage(self._img)

    self.config(image=self._img)
  

