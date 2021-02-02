import io
import base64
from tkinter import Frame, Label

from PIL import Image, ImageTk

from .constant import *

IMG_ON = "iVBORw0KGgoAAAANSUhEUgAAACMAAAATCAMAAAAtfUTGAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAABaUExURQAAAFDfYErVaknbZEvZZUrXZUrZZkzXZkrZZkrYZUvYZUzZZUvYZUvYZUzZZUvYZEvYZUvYZUvYZUvYZV/cdonlmozmnbjww8nz0d344u778fH88/n++v///+kOdCkAAAATdFJOUwAQGBxYYGRseHyrs7/Dx8vj7/OvG9fLAAAACXBIWXMAABcRAAAXEQHKJvM/AAAAsElEQVQoU42S2xKCMAwFYwUFuQimUKrw/78pJccJtqPDPmbPtGlS2jBF03FM15Zn0YGsRznmcUHidENlx+j87N3AXJktk0bstAiT5SpEMgjFvhBZlqflfG037eVzSmDi3lABoYzQwsAFNTCKgxUcN5TOxcMKnjuC2DHDCjPzoXPuMErcT0sljBK/qzw0H8phlO85b2utoJT9vuoQIZOGdO+17H297uf/uSKx8u8fEr0BBNQxlrOx4ZEAAAAASUVORK5CYII="
IMG_OFF = "iVBORw0KGgoAAAANSUhEUgAAACMAAAATCAMAAAAtfUTGAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAABaUExURQAAAN/f39Xf39vb29nZ3Nra3NnZ29nZ3Nnb3dra3Nra3dna29ra3Nna3Nna3Nnb3Nna3Nna3Nna3Nna3N3e4Obn6Ofn6fDw8fT09fj4+Pv8/Pz8/P7+/v///7jjrQgAAAATdFJOUwAQGBxYYGRseHyrs7/Dx8vj7/OvG9fLAAAACXBIWXMAABcRAAAXEQHKJvM/AAAAqElEQVQoU42S0RKCIBBFN9ISUcPWREr//zcT9zY4OqHnkXMHlt2lBVXUlrfYRl9FB7IWx1ueNyQuJXPv/OjdC2qFUUum5G6YhKGDipgQybj7IDJN730on8tt+XdLYICJtIoK7qGFfU0F1exgBQcTqcmyhxU8TMQS8wgrjDArTt3zOKynIX34L32qP5Qf9HkZq0nOqwoRUiYx90rmPj/3d3/uSMyk9pDoC2zUMZbzZ+E3AAAAAElFTkSuQmCC"



class Switch(Frame):
  def __init__(self, master, text, variable=None, value=None, **kw):
    super().__init__(master)
    self.config(**kw)

    self.variable = variable
    self.value = value
    self.active = False


    self._imgOn = self._render_img(IMG_ON)
    self._imgOff = self._render_img(IMG_OFF)

    self._switch = Label(self, bg=self['bg'], text='')
    self._text = Label(self, text=text, bg=self['bg'])

    self._switch.pack(side=START_DIR)
    self._text.pack(side=START_DIR, padx=5, fill='x')

    self._toggle_img()

    self.bind("<ButtonRelease-1>", self.toggle)
    self._switch.bind("<ButtonRelease-1>", self.toggle)
    self._text.bind("<ButtonRelease-1>", self.toggle)


  def _render_img(self, img):
    imgdata = base64.b64decode(img)
    img = Image.open(io.BytesIO(imgdata))
    return ImageTk.PhotoImage(img)


  def get(self):
    return self.value


  def _toggle_img(self):
    if self.active:
      self._switch.config(image=self._imgOn)
      self._text.config(fg='black')
    else:
      self._switch.config(image=self._imgOff)
      self._text.config(fg='gray')
  
  def _toggel_variable(self):
    if self.variable:
      if self.active:
        self.variable.set(self.value)
      else:
        self.variable.set('')

  def toggle(self, event=None):
    self.active = not self.active
    self._toggel_variable()
    self._toggle_img()

    # print(self.variable.get())
  
if __name__=='__main__':
  import tkinter as tk

  root = tk.Tk()
  vr = tk.StringVar()
  s = Switch(root, text="test switch", value='DIR', variable=vr)
  s.pack()

  root.mainloop()

  
