import tkinter as tk
from itertools import count

from PIL import Image, ImageTk


# https://stackoverflow.com/a/43770948

class GifLabel(tk.Label):
  """a label that displays images, and plays them if they are Labels"""
  def __init__(self, parent, gif, delay=None, **kw):
    tk.Label.__init__(self, parent, **kw)
    self.config(highlightthickness=0, bd=0, bg=parent['background'])
    self.delay = delay
    self.gif = gif

    # self.load()
  
  def load(self, gif=None):
    self.gif = gif or self.gif
    if isinstance(self.gif, str):
        im = Image.open(self.gif)
    self.loc = 0
    self.frames = []

    try:
      for i in count(1):
        self.frames.append(ImageTk.PhotoImage(im.copy()))
        im.seek(i)
    except EOFError:
      pass

    if not self.delay:
      try:
        self.delay = im.info['duration']
      except:
        self.delay = 100

    if len(self.frames) == 1:
      self.config(image=self.frames[0])
    else:
      self.next_frame()

  def unload(self):
    self.config(image="")
    self.frames = None

  def next_frame(self):
    if self.frames:
      self.loc += 1
      self.loc %= len(self.frames)
      self.config(image=self.frames[self.loc])
      self.after(self.delay, self.next_frame)


if __name__ == "__main__":
  root = tk.Tk()
  lbl = GifLabel(root, gif='wait.gif')
  lbl.pack()
  # lbl.load('wait.gif')
  root.mainloop()