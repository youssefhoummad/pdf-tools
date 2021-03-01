from tkinter import Label

from PIL import Image, ImageTk, ImageOps


class ImageLabel(Label):
  def __init__(self, parent, image_path, width=None, height=None,  **kw):
    super().__init__(parent, **kw)
    
    justify = kw.get('justify', 'left')

    self._img = Image.open(image_path)
    if width or height:
      self._img.thumbnail((width , height), Image.ANTIALIAS)
    
    if justify == 'right':
      self._img = ImageOps.mirror(self._img)
    self._img = ImageTk.PhotoImage(self._img)
    self.config(image=self._img, bd=0)

  
if __name__ == "__main__":
  from tkinter import Tk
  root = Tk()
  iL = ImageLabel(root, image_path=r"D:\برمجة\pdf\img\cut.png", justify='right')
  iL.pack()
  root.mainloop()
