# import tkinter as tk
from tkinter import Label

from PIL import Image, ImageTk, ImageOps

from .constant import *

class ImageLabel(Label):
  def __init__(self, parent, image_path, width=None, height=None, **kw):
    super().__init__(parent, **kw)
    self._img = Image.open(image_path)
    if width or height:
      self._img.thumbnail((width , height), Image.ANTIALIAS)
    if DIR == 'rtl':
      self._img = ImageOps.mirror(self._img)
    self._img = ImageTk.PhotoImage(self._img)
    self.config(image=self._img, bd=0)

  
# if __name__ == "__main__":

#   root = tk.Tk()
#   iL = ImageLabel(root, image_path=r'button1.png')
#   iL.pack()
#   root.mainloop()
