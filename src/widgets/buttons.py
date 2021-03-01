import io
import base64
from tkinter import Label

from PIL import Image, ImageTk, ImageEnhance, ImageOps, ImageMath
from PIL.ImageColor import getcolor, getrgb
from PIL.ImageOps import grayscale


IMG_BASE = 'iVBORw0KGgoAAAANSUhEUgAAAJgAAAAkCAMAAABCFAMdAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAnUExURQAAABSAzxSAzRWAzhOAzhWAzhSCzxSCzhSBzhSBzhSBzhSBzhSBzrYPMWAAAAAMdFJOUwBATFSDk7O7y+vv94T4noEAAAAJcEhZcwAAFxEAABcRAcom8z8AAAB1SURBVFhH7dgxDoAgFIPhgvoE8f7nVZN6gG4d+k1l+0OYANBq3lZm9TcLO49W9ve+OM00FJeZgtn7+k1w2EmYKmGqhKkSpkqYKmGqhKkSpkqYKmGqhKkSpvINuzjMTJxcZgqdy0wHDk4rx/eluI3Fo4k1NuABG3X/RC8BNvMAAAAASUVORK5CYII='


class ButtonBase(Label):
  def __init__(self, parent, text, images=[], command=None, fg='white', bg=None):
    super().__init__(parent, text=text)

    self.command= command
    self.bg = bg

    self.disabeld = False

    self._fg = fg
    self._fgHover = fg
    self._fgPress = fg
    self._fgDis = '#F2F2F2'

    while len(images) < 4:
      images.append(images[0])


    self.images = []

    factors = [1, 1.2, 0.8, 'gray']

    for i, img in enumerate( images): 
      self.images.append(self._render_img(img, factors[i]))
    

    self.config(image=self.images[0])

    self.config(compound="center", bd=0, fg='white', bg=parent['background'], activeforeground='white', font=('Segoe UI',11,'bold'))
    self.config(fg=self._fg)

    self.bind("<Enter>", self.on_enter)
    self.bind("<Leave>", self.on_leave)
    self.bind("<ButtonPress-1>", self.on_press)
    self.bind("<ButtonRelease-1>", self.on_release)


  def _render_img(self, img, factor=1):

    imgdata = base64.b64decode(img)
    img = Image.open(io.BytesIO(imgdata)).convert("RGBA")
    if self.bg:
      img = self.image_tint(img, tint=self.bg)

    if factor=='gray':
      background = Image.new('RGBA', img.size, (255,255,255))
      img = Image.alpha_composite(background, img)
      img.putalpha(80)
    else:
      enhancer = ImageEnhance.Brightness(img)
      img = enhancer.enhance(factor)
    return ImageTk.PhotoImage(img)




    # https://stackoverflow.com/a/12310820
  def image_tint(self, src, tint='#ffffff'):
    if src.mode not in ['RGB', 'RGBA']:
        raise TypeError('Unsupported source image mode: {}'.format(src.mode))
    src.load()
    tr, tg, tb = getrgb(tint)
    tl = getcolor(tint, "L")  # tint color's overall luminosity
    if not tl: tl = 1  # avoid division by zero
    tl = float(tl)  # compute luminosity preserving tint factors
    sr, sg, sb = list(map(lambda tv: tv/tl, (tr, tg, tb)))  # per component adjustments

    # create look-up tables to list(map luminosity to adjusted tint
    # (using floating-point math only to compute table)
    luts = (list(map(lambda lr: int(lr*sr + 0.5), range(256))) +
            list(map(lambda lg: int(lg*sg + 0.5), range(256))) +
            list(map(lambda lb: int(lb*sb + 0.5), range(256))))
    l = grayscale(src)  # 8-bit luminosity version of whole image
    if Image.getmodebands(src.mode) < 4:
        merge_args = (src.mode, (l, l, l))  # for RGB verion of grayscale
    else:  # include copy of src image's alpha layer
        a = Image.new("L", src.size)
        a.putdata(src.getdata(3))
        merge_args = (src.mode, (l, l, l, a))  # for RGBA verion of grayscale
        luts += range(256)  # for 1:1 mapping of copied alpha values

    return Image.merge(*merge_args).point(luts)


  def on_enter(self, event):
    if not self.disabeld:
      self.config(image=self.images[1])
      self.config(fg=self._fgHover)
    

  def on_leave(self, event):
    if not self.disabeld:
      self.config(image=self.images[0])
      self.config(fg=self._fg)


  def on_press(self, event):
    if not self.disabeld:
      self.config(image=self.images[2])
      self.config(fg=self._fgPress)


  def on_release(self, event):
    # if self['state']!="disabled":
    if not self.disabeld:
      self.on_enter(event=None)
      if self.command: self.command()
    
  def on_disable(self, event=None):
    self.disabeld = True
    self.config(image=self.images[3], fg=self._fgDis)

  def on_unable(self, event=None):
    self.disabeld = False
    self.config(image=self.images[0], fg=self._fg)


class Button(ButtonBase):
  def __init__(self, parent, text, command=None):
    super().__init__(
        parent, text=text, images=[IMG_BASE], command=command
        )
    super().on_disable()


IMG_SM = 'iVBORw0KGgoAAAANSUhEUgAAABMAAAASCAMAAACO0hVbAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAPUExURf+AQP+gQv+fQv+gQ/+fQ+Yl0yMAAAAEdFJOUwSDh+OSQ+laAAAACXBIWXMAABcRAAAXEQHKJvM/AAAAMUlEQVQoU2NgYGRmQQbMTEAhKBsBGBlQVYEAMwOUgQyGtRi2MGCCshAAFIBoYcrEAACjSQUtaqPaYAAAAABJRU5ErkJggg=='
IMG_SM2 = 'iVBORw0KGgoAAAANSUhEUgAAABMAAAASCAMAAACO0hVbAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAPUExURf+/gP+9ef+9ef+8ef+8eaDlP8gAAAAEdFJOUwSDh+OSQ+laAAAACXBIWXMAABcRAAAXEQHKJvM/AAAAMUlEQVQoU2NgYGRmQQbMTEAhKBsBGBlQVYEAMwOUgQyGtRi2MGCCshAAFIBoYcrEAACjSQUtaqPaYAAAAABJRU5ErkJggg=='
IMG_SM3 = 'iVBORw0KGgoAAAANSUhEUgAAABMAAAASCAMAAACO0hVbAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAPUExURf+AAP+OHf+OHP+OHf+OHY6PLtQAAAAEdFJOUwSDh+OSQ+laAAAACXBIWXMAABcRAAAXEQHKJvM/AAAAMUlEQVQoU2NgYGRmQQbMTEAhKBsBGBlQVYEAMwOUgQyGtRi2MGCCshAAFIBoYcrEAACjSQUtaqPaYAAAAABJRU5ErkJggg=='
IMG_SM4 = 'iVBORw0KGgoAAAANSUhEUgAAABMAAAASCAMAAACO0hVbAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAADUExURQAAAKd6PdoAAAABdFJOUwBA5thmAAAACXBIWXMAABcRAAAXEQHKJvM/AAAADklEQVQoU2MYBXQADAwAAWgAAfzXmx8AAAAASUVORK5CYII='

class ButtonSmall(ButtonBase):
  def __init__(self, parent, text, command=None):
    super().__init__(
        parent, text=text, images=[IMG_SM, IMG_SM2, IMG_SM3, IMG_SM4], command=command
        )
    self._fgDis = 'white'
    super().on_disable()



if __name__ == "__main__":
  from tkinter import Tk
  root = Tk()
  img = r'D:\برمجة\pdf\src\button1.png'
  # b = ButtonBase(root, text='click me')
  # b = ButtonBase(root, text='click me', images=[IMG_BASE, IMG_HOVER, IMG_PRESS])
  b = ButtonBase(root, text='click me', images=[IMG_BASE], bg='#F2482E')
  b.pack(padx=20, pady=20)
  root.mainloop()