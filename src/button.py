import io
import base64
from tkinter import Label

from PIL import Image, ImageTk

IMG_BASE = 'iVBORw0KGgoAAAANSUhEUgAAAJgAAAAkCAMAAABCFAMdAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAnUExURQAAABSAzxSAzRWAzhOAzhWAzhSCzxSCzhSBzhSBzhSBzhSBzhSBzrYPMWAAAAAMdFJOUwBATFSDk7O7y+vv94T4noEAAAAJcEhZcwAAFxEAABcRAcom8z8AAAB1SURBVFhH7dgxDoAgFIPhgvoE8f7nVZN6gG4d+k1l+0OYANBq3lZm9TcLO49W9ve+OM00FJeZgtn7+k1w2EmYKmGqhKkSpkqYKmGqhKkSpkqYKmGqhKkSpvINuzjMTJxcZgqdy0wHDk4rx/eluI3Fo4k1NuABG3X/RC8BNvMAAAAASUVORK5CYII='
IMG_HOVER = 'iVBORw0KGgoAAAANSUhEUgAAAJgAAAAkCAMAAABCFAMdAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAnUExURQAAADi37za58je28De38Ti28Ti28Te38Te38Te38Te48Te38Te38WhZQuQAAAAMdFJOUwBATFSDk7O7y+vv94T4noEAAAAJcEhZcwAAFxEAABcRAcom8z8AAAB1SURBVFhH7dgxDoAgFIPhgvoE8f7nVZN6gG4d+k1l+0OYANBq3lZm9TcLO49W9ve+OM00FJeZgtn7+k1w2EmYKmGqhKkSpkqYKmGqhKkSpkqYKmGqhKkSpvINuzjMTJxcZgqdy0wHDk4rx/eluI3Fo4k1NuABG3X/RC8BNvMAAAAASUVORK5CYII='
IMG_PRESS = 'iVBORw0KGgoAAAANSUhEUgAAAJgAAAAkCAMAAABCFAMdAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAnUExURQAAABRYmxRXmhVYmxNYnBVYmhRYmxRZmxRYmxRYmxRXmxRYmxRYm+GSz3IAAAAMdFJOUwBATFSDk7O7y+vv94T4noEAAAAJcEhZcwAAFxEAABcRAcom8z8AAAB1SURBVFhH7dgxDoAgFIPhgvoE8f7nVZN6gG4d+k1l+0OYANBq3lZm9TcLO49W9ve+OM00FJeZgtn7+k1w2EmYKmGqhKkSpkqYKmGqhKkSpkqYKmGqhKkSpvINuzjMTJxcZgqdy0wHDk4rx/eluI3Fo4k1NuABG3X/RC8BNvMAAAAASUVORK5CYII='
IMG_DISB = 'iVBORw0KGgoAAAANSUhEUgAAAJgAAAAkCAMAAABCFAMdAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAnUExURQAAAJuzx56yxp6zyJ6zx56zx52zx52zx52yxp2zx52zyJ2zx52zx5Mkjn4AAAAMdFJOUwBATFSDk7O7y+vv94T4noEAAAAJcEhZcwAAFxEAABcRAcom8z8AAAB1SURBVFhH7dgxDoAgFIPhgvoE8f7nVZN6gG4d+k1l+0OYANBq3lZm9TcLO49W9ve+OM00FJeZgtn7+k1w2EmYKmGqhKkSpkqYKmGqhKkSpkqYKmGqhKkSpvINuzjMTJxcZgqdy0wHDk4rx/eluI3Fo4k1NuABG3X/RC8BNvMAAAAASUVORK5CYII='


class ButtonBase(Label):
  def __init__(self, parent, text, images=[], command=None):
    super().__init__(parent, text=text)

    self.command= command

    self.disabeld = False

    self._fg = 'white'
    self._fgDis = '#F2F2F2'

    self.images = []

    for img in images: self.images.append(self._render_img(img))
    
    while len(self.images) < 4:
      self.images.append(self.images[0])

    self.config(image=self.images[0])

    self.config(compound="center", bd=0, fg='white', bg=parent['background'], activeforeground='white', font=('Tahoma',10,'bold'))
    self.config(fg="white")

    self.bind("<Enter>", self.on_enter)
    self.bind("<Leave>", self.on_leave)
    self.bind("<ButtonPress-1>", self.on_press)
    self.bind("<ButtonRelease-1>", self.on_release)


  def _render_img(self, img):
    imgdata = base64.b64decode(img)
    img = Image.open(io.BytesIO(imgdata))
    return ImageTk.PhotoImage(img)


  def on_enter(self, event):
    if not self.disabeld:
      self.config(image=self.images[1])
    

  def on_leave(self, event):
    if not self.disabeld:
      self.config(image=self.images[0])

  def on_press(self, event):
    if not self.disabeld:
      self.config(image=self.images[2])

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
        parent, text=text, images=[IMG_BASE, IMG_HOVER, IMG_PRESS, IMG_DISB], command=command
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
  root = tk.Tk()
  b = ButtonBase(root, text='click me', images=[IMG_BASE, IMG_HOVER, IMG_PRESS])
  b.pack(padx=20, pady=20)
  root.mainloop()